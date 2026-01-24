# ============================================================
# main.py - Flask 應用程式入口點
# 專案：Chi Soo 租屋小幫手
# 說明：LINE Bot Webhook 接收端點與 Postback 處理
# ============================================================

import json
import threading
from urllib.parse import parse_qs
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
    ShowLoadingAnimationRequest,
    PushMessageRequest,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
    FollowEvent,
    UnfollowEvent,
)
from linebot.v3.exceptions import InvalidSignatureError

from app.config import config
from app.services.session_service import SessionService
from app.services.ollama_service import OllamaService
from app.services.matching_service import MatchingService
from app.services.weight_service import WeightService

# 建立 Flask 應用程式
app = Flask(__name__)

# 設定 LINE Bot SDK
configuration = Configuration(access_token=config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)

# 初始化服務
ollama_service = OllamaService()
matching_service = MatchingService()


@app.route("/")
def index():
    """健康檢查端點"""
    return {"status": "ok", "service": "Chi Soo 租屋小幫手", "version": "1.0.0"}


@app.route("/callback", methods=["POST"])
def callback():
    """LINE Webhook 接收端點"""
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    app.logger.info(f"收到 Webhook 請求: {body}")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("無效的簽章")
        abort(400)
    
    return "OK"


# ============================================================
# 文字訊息處理
# ============================================================

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """處理文字訊息事件"""
    user_id = event.source.user_id
    user_message = event.message.text.strip()
    reply_token = event.reply_token
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 全域：收到訊息立即顯示 Loading 動畫
        try:
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id, loading_seconds=50)
            )
        except Exception as e:
            app.logger.warning(f"無法顯示 Loading 動畫: {e}")
        
        # 檢查使用者狀態
        is_testing = SessionService.is_testing(user_id)
        is_weight_selection = SessionService.is_weight_selection(user_id)
        
        if is_weight_selection:
            # 權重選擇模式：不處理文字訊息，提示使用按鈕
            reply_text(line_bot_api, reply_token, "請點擊上方的按鈕進行選擇喔！")
        elif is_testing:
            # 測試模式：處理 AI 對話
            handle_testing_message(line_bot_api, reply_token, user_id, user_message)
        else:
            # 一般模式
            if user_message == "開始分析":
                # 檢查是否有收集到的資料
                collected_data = SessionService.get_collected_data(user_id)
                if collected_data:
                    handle_start_analysis(line_bot_api, reply_token, user_id, collected_data)
                else:
                    reply_text(line_bot_api, reply_token, "請先點擊選單的『幫我找窩』開始測驗喔！")
            else:
                # 回覆功能導覽
                reply_idle_message(line_bot_api, reply_token)


def handle_testing_message(line_bot_api, reply_token, user_id, user_message):
    """處理測試模式中的訊息"""
    collected_data = SessionService.get_collected_data(user_id)
    
    # 呼叫 AI 分析 (傳入 user_id 以儲存紀錄)
    result = ollama_service.analyze_and_respond(user_message, collected_data, user_id=user_id)
    
    # 更新收集到的資料
    SessionService.update_collected_data(user_id, result["collected_data"])
    
    if result["is_complete"]:
        # 資料已齊全，切回 IDLE 並提示輸入「開始分析」
        SessionService.pause_test(user_id)
        reply_text(line_bot_api, reply_token, result["response"])
    else:
        # 繼續追問
        reply_text(line_bot_api, reply_token, result["response"])


def handle_start_analysis(line_bot_api, reply_token, user_id, collected_data):
    """處理開始分析指令 (非同步模式)"""
    import os
    
    # 1. 立即回覆「分析中」卡片
    template_path = os.path.join(os.path.dirname(__file__), "templates", "processing_card.json")
    with open(template_path, "r", encoding="utf-8") as f:
        processing_card = json.load(f)
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="⏳ 分析中...", contents=FlexContainer.from_dict(processing_card))]
        )
    )
    
    # 3. 背景執行匹配演算法
    def run_matching_async():
        try:
            # 取得該 User 的自訂權重
            session = SessionService.get_or_create_session(user_id)
            user_weights = session.weights
            
            results = matching_service.match(collected_data, weights=user_weights)
            
            if results:
                best_match = results[0]
                persona = best_match["persona"]
                score = best_match["score"]
                
                # 儲存結果到 Session (供稍後查詢)
                SessionService.set_persona_result(user_id, persona.persona_id)
                SessionService.reset_test(user_id)
                
                app.logger.info(f"背景分析完成: {user_id} -> {persona.persona_id}")
            else:
                app.logger.error(f"背景分析失敗: 無結果")
        except Exception as e:
            app.logger.error(f"背景分析發生錯誤: {e}")
    
    thread = threading.Thread(target=run_matching_async)
    thread.daemon = True
    thread.start()


def reply_idle_message(line_bot_api, reply_token):
    """回覆一般模式的功能導覽"""
    message = (
        "你好！我是 Chi Soo 租屋小幫手 🦔\n\n"
        "抱歉，我現在聽不懂一般的文字對話。請使用下方的選單來操作：\n\n"
        "🔍 幫我找窩：AI 幫你分析適合的租屋類型\n"
        "🏆 評價排行榜：看看大家推薦哪裡\n"
        "📚 租屋小Tips：簽約與看房須知\n"
        "❤️ 我的收藏：查看已儲存的房源\n\n"
        "若要開始找房測驗，請點擊選單左上角的『幫我找窩』！"
    )
    reply_text(line_bot_api, reply_token, message)


def reply_text(line_bot_api, reply_token, text):
    """回覆純文字訊息"""
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=text)]
        )
    )


# ============================================================
# Postback 事件處理
# ============================================================

@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    """處理 Postback 事件 (Rich Menu 點擊)"""
    user_id = event.source.user_id
    postback_data = event.postback.data
    reply_token = event.reply_token
    
    # 解析 postback data
    params = parse_qs(postback_data)
    action = params.get("action", [""])[0]
    
    app.logger.info(f"Postback: user={user_id}, action={action}")
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 全域：收到 Postback 立即顯示 Loading 動畫
        try:
            line_bot_api.show_loading_animation(
                ShowLoadingAnimationRequest(chat_id=user_id, loading_seconds=30)
            )
        except Exception as e:
            app.logger.warning(f"無法顯示 Loading 動畫: {e}")
        
        # 根據 action 執行對應功能
        if action == "answer_weight":
            q_idx = int(params.get("q", ["0"])[0])
            choice = params.get("choice", [""])[0]
            handle_weight_answer(line_bot_api, reply_token, user_id, q_idx, choice)
        elif action == "start_test":
            handle_start_test(line_bot_api, reply_token, user_id)
        elif action == "show_ranking":
            handle_show_ranking(line_bot_api, reply_token)
        elif action == "show_tips":
            handle_show_tips(line_bot_api, reply_token)
        elif action == "show_fav":
            handle_show_favorites(line_bot_api, reply_token, user_id)
        elif action == "show_review":
            handle_show_review(line_bot_api, reply_token)
        elif action == "show_map":
            handle_show_map(line_bot_api, reply_token)
        elif action == "show_recommendations":
            persona_id = params.get("persona", [""])[0]
            handle_show_recommendations(line_bot_api, reply_token, user_id, persona_id)
        elif action == "resume_test":
            handle_resume_test(line_bot_api, reply_token, user_id)
        elif action == "restart_test":
            handle_restart_test(line_bot_api, reply_token, user_id)
        elif action == "get_result":
            handle_get_result(line_bot_api, reply_token, user_id)
        elif action == "add_favorite":
            house_id = params.get("house_id", [""])[0]
            handle_add_favorite(line_bot_api, reply_token, user_id, house_id)
        elif action == "remove_favorite":
            house_id = params.get("house_id", [""])[0]
            handle_remove_favorite(line_bot_api, reply_token, user_id, house_id)
        elif action == "show_house_detail":
            house_id = params.get("house_id", [""])[0]
            handle_show_house_detail(line_bot_api, reply_token, house_id)
        elif action == "show_more_houses":
            persona_id = params.get("persona", [""])[0]
            offset = int(params.get("offset", ["0"])[0])
            handle_show_more_houses(line_bot_api, reply_token, user_id, persona_id, offset)
        elif action == "coming_soon":
            # 功能建置中提示
            feature = params.get("feature", [""])[0]
            feature_names = {
                "review": "評價系統",
                "map": "地圖式搜尋"
            }
            feature_name = feature_names.get(feature, "此功能")
            reply_text(line_bot_api, reply_token, 
                f"🚧 {feature_name}正在重新設計中！\n\n"
                "我們正在打造更好的體驗，敬請期待 🦔✨"
            )
        else:
            reply_text(line_bot_api, reply_token, f"收到指令：{action}")


def handle_start_test(line_bot_api, reply_token, user_id):
    """開始找房測驗"""
    # 檢查是否有未完成的進度
    has_progress = SessionService.has_progress(user_id)
    
    if has_progress:
        # 詢問是否繼續
        message = (
            "嗨！Chi Soo 發現您上次的諾詢進行到一半。\n\n"
            "要繼續嗎？還是重新開始？"
        )
        # TODO: 之後改成 Flex Message 帶按鈕
        SessionService.start_test(user_id, keep_progress=True)
        reply_text(line_bot_api, reply_token, 
            "歡迎回來！讓我們繼續吧 😊\n\n" + 
            "請告訴我您的租屋需求，例如：\n" +
            "「我預算大概 5000，希望靠近市區」"
        )
    else:
        # 開始新測驗 - 進入權重選擇關卡 (新增流程說明)
        SessionService.start_weight_selection(user_id)
        
        # 發送流程說明 + 第一題
        intro_text = TextMessage(text=(
            "🧒 開始剖析你的租屋人格！\n\n"
            "接下來分兩步驟進行：\n\n"
            "👉 Step 1: 租屋價值觀快問快答（6 題）\n"
            "　→ 了解你在乎哪些面向\n\n"
            "👉 Step 2: 具體條件問答（AI 對話）\n"
            "　→ 收集預算、地點、房型等細節\n\n"
            "全部完成後，我會為你診斷專屬的「租屋人格」🎯\n"
            "準備好了就開始吧！"
        ))
        
        question = WeightService.get_question(1)
        flex_msg = create_weight_question_flex(question, 1, 6)
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    intro_text,
                    FlexMessage(alt_text="Step 1: 租屋價值觀 (1/6)", contents=flex_msg)
                ]
            )
        )


def handle_weight_answer(line_bot_api, reply_token, user_id, q_idx, choice):
    """處理權重選擇答案"""
    # 紀錄答案並取得下一關
    next_stage = SessionService.submit_weight_answer(user_id, q_idx, choice)
    
    if next_stage <= 6:
        # 還有下一題
        question = WeightService.get_question(next_stage)
        flex_msg = create_weight_question_flex(question, next_stage, 6)
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[FlexMessage(alt_text=f"租屋價值觀大哉問 ({next_stage}/6)", contents=flex_msg)]
            )
        )
    else:
        # 完成所有題目 -> 結算並進入 AI 聊天
        session = SessionService.get_or_create_session(user_id)
        weights = WeightService.calculate_weights(session.weight_answers)
        chart_url = WeightService.generate_radar_chart_url(weights)
        summary = WeightService.generate_summary_text(weights)
        
        # 儲存並轉移狀態
        SessionService.finish_weight_selection(user_id, weights)
        SessionService.start_test(user_id, keep_progress=True) # 確保狀態是 TESTING 且保留 weights
        
        # 1. 發送雷達圖與總結 (調整價值觀標題)
        chart_flex = create_chart_summary_flex(chart_url, summary)
        
        # 2. 發送 AI 聊天的開場白 (Step 2 開始)
        intro_msg = TextMessage(text=(
            "🚀 進入 Step 2：具體條件問答\n\n"
            "首先，請問你的 💰 預算上限 是多少呢？\n"
            "（例如：5000、8000、不限）"
        ))
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    FlexMessage(alt_text="Step 1 完成！你的租屋價值觀", contents=chart_flex),
                    intro_msg
                ]
            )
        )


def create_weight_question_flex(question, current, total):
    """建立權重二選一 Flex Message (Carousel 版本)"""
    progress = f"{current}/{total}"
    
    # Bubble 1: 題目
    question_bubble = {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"租屋價值觀 ({progress})", "size": "xs", "color": "#6366F1", "weight": "bold"},
                {"type": "text", "text": question["title"], "size": "lg", "weight": "bold", "color": "#1f2937", "margin": "sm"}
            ],
            "backgroundColor": "#EEF2FF",
            "paddingAll": "15px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": question["question"], "size": "md", "color": "#374151", "wrap": True, "margin": "md"},
            ],
             "paddingAll": "20px"
        }
    }

    # Bubble 2 & 3: 選項
    bubbles = [question_bubble]
    
    colors = ["#10B981", "#F59E0B"] # Green, Amber
    
    for i, opt in enumerate(question["options"]):
        color = colors[i % 2]
        option_label = "選項 A" if i == 0 else "選項 B"
        
        opt_bubble = {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": option_label, "weight": "bold", "color": "#FFFFFF", "size": "md"}
                ],
                "backgroundColor": color,
                "paddingAll": "10px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": opt["label"], "wrap": True, "size": "md", "color": "#333333", "weight": "bold"}
                ],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "選擇此方案",
                            "data": f"action=answer_weight&q={current}&choice={opt['value']}",
                            "displayText": f"我選 {opt['label']}"
                        },
                        "style": "primary",
                        "color": color
                    }
                ],
                "paddingAll": "10px"
            }
        }
        bubbles.append(opt_bubble)
        
    carousel_json = {
        "type": "carousel",
        "contents": bubbles
    }
        
    return FlexContainer.from_dict(carousel_json)


def create_chart_summary_flex(chart_url, summary):
    """建立雷達圖結果 Flex Message (價值觀分佈)"""
    flex_json = {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "✅ Step 1 完成", "weight": "bold", "size": "xl", "color": "#ffffff"}
            ],
            "backgroundColor": "#10B981",
            "paddingAll": "15px"
        },
        "hero": {
            "type": "image",
            "url": chart_url,
            "size": "full",
            "aspectRatio": "1:1",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "📊 你的租屋價值觀分佈", "weight": "bold", "size": "md", "color": "#1f2937"},
                {"type": "text", "text": summary, "wrap": True, "size": "sm", "color": "#4b5563", "margin": "md", "lineSpacing": "5px"}
            ],
            "paddingAll": "15px"
        }
    }
    return FlexContainer.from_dict(flex_json)


def handle_get_result(line_bot_api, reply_token, user_id):
    """取得分析結果（從 Session 讀取）"""
    from app.models.persona import Persona
    from app.models import db_session
    
    # 取得使用者的 persona_type
    user = SessionService.get_or_create_user(user_id)
    persona_id = user.persona_type
    
    if not persona_id:
        # 結果尚未準備好
        reply_text(
            line_bot_api, 
            reply_token, 
            "⏳ 分析還在進行中喔！\n請再等幾秒後再按一次按鈕～"
        )
        return
    
    # 取得 Persona 資料
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    
    if not persona:
        reply_text(line_bot_api, reply_token, "❌ 找不到分析結果，請重新開始測驗。")
        return
    
    # 建立診斷書 Flex Message
    diagnosis_flex = create_diagnosis_flex(persona, 85)  # 預設 85%
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text=f"你是：{persona.name}", contents=diagnosis_flex)]
        )
    )


def handle_show_ranking(line_bot_api, reply_token):
    """顯示評價排行榜 - Flex Message Carousel 版本"""
    from app.models.house import House
    from app.models import db_session
    
    # 查詢評分最高的 5 間房源 (好評榜)
    top_houses = db_session.query(House).filter(
        House.is_active == True,
        House.review_count > 0
    ).order_by(House.avg_rating.desc()).limit(5).all()
    
    # 查詢評分最低的 5 間房源 (停看聽)
    bottom_houses = db_session.query(House).filter(
        House.is_active == True,
        House.review_count > 0
    ).order_by(House.avg_rating.asc()).limit(5).all()
    
    messages = []
    
    # 建立好評榜 Carousel
    if top_houses:
        top_carousel = create_ranking_carousel(
            houses=top_houses,
            title="🏆 社群好評榜",
            badge="社群推薦",
            header_color="#10B981",
            button_color="#10B981"
        )
        messages.append(FlexMessage(
            alt_text="🏆 社群好評榜",
            contents=top_carousel
        ))
    
    # 建立停看聽 Carousel
    if bottom_houses:
        bottom_carousel = create_ranking_carousel(
            houses=bottom_houses,
            title="⚠️ 租屋停看聽",
            badge="多加留意",
            header_color="#F59E0B",
            button_color="#F59E0B"
        )
        messages.append(FlexMessage(
            alt_text="⚠️ 租屋停看聽",
            contents=bottom_carousel
        ))
    
    # 若無資料，回傳文字訊息
    if not messages:
        reply_text(line_bot_api, reply_token, 
            "📊 目前還沒有足夠的評價資料～\n\n"
            "快去『評價系統』幫房源評分吧！\n"
            "📝 評價僅供參考"
        )
        return
    
    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=reply_token, messages=messages)
    )


def handle_show_tips(line_bot_api, reply_token):
    """顯示租屋小 Tips - Flex Message Carousel 版本"""
    tips_carousel = create_tips_carousel()
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="📚 租屋小 Tips", contents=tips_carousel)]
        )
    )


def handle_show_favorites(line_bot_api, reply_token, user_id):
    """顯示我的收藏 - Flex Message Carousel 版本"""
    from app.models.favorite import Favorite
    from app.models.house import House
    from app.models import db_session
    
    # 查詢使用者收藏的房源
    favorites = db_session.query(Favorite).filter(
        Favorite.user_id == user_id
    ).order_by(Favorite.created_at.desc()).all()
    
    if not favorites:
        reply_text(line_bot_api, reply_token,
            "❤️ 我的收藏\n\n"
            "您目前沒有收藏任何房源。\n\n"
            "快去『幫我找窩』看看適合你的房源吧！"
        )
        return
    
    # 取得房源資訊
    house_ids = [f.house_id for f in favorites]
    houses = db_session.query(House).filter(House.house_id.in_(house_ids)).all()
    house_map = {h.house_id: h for h in houses}
    
    # 建立收藏 Carousel
    favorites_carousel = create_favorites_carousel(favorites, house_map)
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="❤️ 我的收藏", contents=favorites_carousel)]
        )
    )


def handle_show_review(line_bot_api, reply_token):
    """顯示評價系統"""
    review_url = f"{config.BASE_URL}/liff/review"
    message = (
        "✍️ 評價系統\n\n"
        "此功能開發中，敬請期待！\n\n"
        f"未來將可在此連結填寫評價：\n{review_url}"
    )
    reply_text(line_bot_api, reply_token, message)


def handle_show_map(line_bot_api, reply_token):
    """顯示地圖式搜尋"""
    map_url = f"{config.BASE_URL}/liff/map"
    message = (
        "🗺️ 地圖式搜尋\n\n"
        "此功能開發中，敬請期待！\n\n"
        f"未來將可在此連結查看地圖：\n{map_url}"
    )
    reply_text(line_bot_api, reply_token, message)


def handle_show_recommendations(line_bot_api, reply_token, user_id, persona_id):
    """顯示推薦房源 - Flex Message Carousel 版本"""
    from app.models.persona import Persona
    from app.models import db_session
    
    # 取得推薦房源（含匹配分數）
    houses_with_scores = matching_service.get_recommended_houses_with_scores(persona_id, limit=5)
    
    if not houses_with_scores:
        reply_text(line_bot_api, reply_token, 
            "📭 目前沒有找到適合的房源～\n\n"
            "請稍後再試，或調整您的租屋需求！"
        )
        return
    
    # 取得 Persona 資訊用於生成推薦理由
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    
    # 建立精美的房源 Carousel
    recommendation_carousel = create_recommendation_carousel(
        houses_with_scores, 
        persona, 
        persona_id, 
        offset=0
    )
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="🏠 為您推薦的房源", contents=recommendation_carousel)]
        )
    )


def handle_resume_test(line_bot_api, reply_token, user_id):
    """繼續測驗"""
    SessionService.start_test(user_id, keep_progress=True)
    reply_text(line_bot_api, reply_token, 
        "好的，讓我們繼續！\n\n請告訴我更多您的需求～"
    )


def handle_restart_test(line_bot_api, reply_token, user_id):
    """重新開始測驗"""
    SessionService.reset_test(user_id)
    SessionService.start_test(user_id)
    reply_text(line_bot_api, reply_token, 
        "好的，重新開始！\n\n請問您的預算上限是多少呢？"
    )


# ============================================================
# Flex Message 建立
# ============================================================

def create_diagnosis_flex(persona, match_percent):
    """建立診斷書 Flex Message"""
    flex_json = {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "🎯 租屋人格診斷書", "weight": "bold", "size": "lg", "color": "#FFFFFF"}
            ],
            "backgroundColor": "#6366F1",
            "paddingAll": "15px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "你是：", "size": "md", "color": "#666666"},
                {"type": "text", "text": persona.name, "weight": "bold", "size": "xxl", "margin": "md", "color": "#1a1a1a"},
                {"type": "separator", "margin": "lg"},
                {"type": "text", "text": persona.description or "適合你的租屋類型！", "wrap": True, "color": "#666666", "size": "sm", "margin": "lg"},
                {"type": "separator", "margin": "lg"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "lg",
                    "contents": [
                        {"type": "text", "text": "匹配度", "size": "sm", "color": "#666666", "flex": 1},
                        {"type": "text", "text": f"{match_percent}% 🔥", "size": "sm", "color": "#6366F1", "weight": "bold", "flex": 1, "align": "end"}
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "🏠 顯示推薦房源",
                        "data": f"action=show_recommendations&persona={persona.persona_id}"
                    },
                    "style": "primary",
                    "color": "#6366F1"
                }
            ]
        }
    }
    
    return FlexContainer.from_dict(flex_json)


# ============================================================
# Follow/Unfollow 事件
# ============================================================

@handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    """處理加入好友事件"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    app.logger.info(f"新使用者加入: {user_id}")
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 嘗試取得使用者 Profile
        display_name = None
        picture_url = None
        try:
            profile = line_bot_api.get_profile(user_id)
            display_name = profile.display_name
            picture_url = profile.picture_url
            app.logger.info(f"取得使用者資料: {display_name}")
        except Exception as e:
            app.logger.error(f"無法取得使用者資料: {e}")
        
        # 建立或更新使用者 (帶入暱稱與頭像)
        SessionService.get_or_create_user(user_id, display_name, picture_url)
        
        message = (
            "🎉 歡迎使用 Chi Soo 租屋小幫手！\n\n"
            "我是專為埔里地區設計的 AI 租屋顧問 🦔\n"
            "您可以隨時使用下方的選單來操作：\n\n"
            "🔍 幫我找窩：AI 幫你分析適合的租屋類型\n"
            "🏆 評價排行榜：看看大家推薦哪裡\n"
            "📚 租屋小Tips：簽約與看房須知\n"
            "❤️ 我的收藏：查看已儲存的房源\n\n"
            "👉 現在就點擊左上角的『幫我找窩』開始吧！"
        )
        reply_text(line_bot_api, reply_token, message)


@handler.add(UnfollowEvent)
def handle_unfollow(event: UnfollowEvent):
    """處理封鎖事件"""
    user_id = event.source.user_id
    app.logger.info(f"使用者取消追蹤: {user_id}")
    SessionService.mark_blocked(user_id, True)


# ============================================================
# 收藏功能 Handlers
# ============================================================

def handle_add_favorite(line_bot_api, reply_token, user_id, house_id):
    """加入收藏"""
    from app.models.favorite import Favorite
    from app.models.house import House
    from app.models import db_session
    from app.services.session_service import SessionService
    
    app.logger.info(f"[收藏] user={user_id}, house_id={house_id}")
    
    if not house_id:
        reply_text(line_bot_api, reply_token, "❌ 無效的房源 ID")
        return
    
    try:
        house_id = int(house_id)
    except ValueError:
        reply_text(line_bot_api, reply_token, "❌ 無效的房源 ID")
        return
    
    try:
        # 確保使用者存在（解決外鍵約束問題）
        SessionService.get_or_create_user(user_id)
        
        # 檢查房源是否存在
        house = db_session.query(House).filter_by(house_id=house_id).first()
        if not house:
            app.logger.warning(f"[收藏] 找不到房源 house_id={house_id}")
            reply_text(line_bot_api, reply_token, "❌ 找不到此房源")
            return
        
        # 檢查是否已收藏
        existing = db_session.query(Favorite).filter_by(
            user_id=user_id, house_id=house_id
        ).first()
        
        if existing:
            reply_text(line_bot_api, reply_token, 
                f"📌 「{house.name}」已在您的收藏中！\n\n"
                "點擊選單的『我的收藏』查看所有收藏。"
            )
            return
        
        # 新增收藏
        new_favorite = Favorite(user_id=user_id, house_id=house_id)
        db_session.add(new_favorite)
        db_session.commit()
        
        app.logger.info(f"[收藏] 成功加入收藏 user={user_id}, house={house.name}")
        reply_text(line_bot_api, reply_token, 
            f"❤️ 已將「{house.name}」加入收藏！\n\n"
            "點擊選單的『我的收藏』查看所有收藏。"
        )
    except Exception as e:
        app.logger.error(f"[收藏] 發生錯誤: {e}")
        db_session.rollback()
        reply_text(line_bot_api, reply_token, 
            f"❌ 收藏失敗，請稍後再試\n\n錯誤：{str(e)[:50]}"
        )


def handle_remove_favorite(line_bot_api, reply_token, user_id, house_id):
    """移除收藏"""
    from app.models.favorite import Favorite
    from app.models.house import House
    from app.models import db_session
    
    if not house_id:
        reply_text(line_bot_api, reply_token, "❌ 無效的房源 ID")
        return
    
    try:
        house_id = int(house_id)
    except ValueError:
        reply_text(line_bot_api, reply_token, "❌ 無效的房源 ID")
        return
    
    # 查找並刪除收藏
    favorite = db_session.query(Favorite).filter_by(
        user_id=user_id, house_id=house_id
    ).first()
    
    if not favorite:
        reply_text(line_bot_api, reply_token, "📭 此房源不在您的收藏中")
        return
    
    # 取得房源名稱
    house = db_session.query(House).filter_by(house_id=house_id).first()
    house_name = house.name if house else "未知房源"
    
    db_session.delete(favorite)
    db_session.commit()
    
    reply_text(line_bot_api, reply_token, 
        f"🗑️ 已將「{house_name}」從收藏中移除"
    )


def handle_show_house_detail(line_bot_api, reply_token, house_id):
    """顯示房源詳情卡片"""
    from app.models.house import House
    from app.models import db_session
    
    if not house_id:
        reply_text(line_bot_api, reply_token, "❌ 無效的房源 ID")
        return
    
    try:
        house_id = int(house_id)
    except ValueError:
        reply_text(line_bot_api, reply_token, "❌ 無效的房源 ID")
        return
    
    house = db_session.query(House).filter_by(house_id=house_id).first()
    if not house:
        reply_text(line_bot_api, reply_token, "❌ 找不到此房源")
        return
    
    # 建立房源詳情卡片
    house_card = create_house_detail_card(house)
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text=f"🏠 {house.name}", contents=house_card)]
        )
    )


def handle_show_more_houses(line_bot_api, reply_token, user_id, persona_id, offset):
    """顯示更多推薦房源（分頁）"""
    houses = matching_service.get_recommended_houses(persona_id, limit=5, offset=offset)
    
    if not houses:
        reply_text(line_bot_api, reply_token, 
            "📭 已顯示所有適合的房源～\n\n"
            "沒看到心動的嗎？可以試試調整您的需求！"
        )
        return
    
    # 建立房源 Carousel
    houses_carousel = create_houses_carousel(houses, persona_id, offset)
    
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[FlexMessage(alt_text="🏠 更多推薦房源", contents=houses_carousel)]
        )
    )


# ============================================================
# Flex Carousel 建立輔助函數
# ============================================================

def create_ranking_carousel(houses, title, badge, header_color, button_color):
    """建立排行榜 Carousel"""
    bubbles = []
    
    # 預設圖片 URL
    default_image = "https://via.placeholder.com/400x260/6366F1/FFFFFF?text=No+Image"
    
    for house in houses:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": badge, "size": "xs", "color": "#FFFFFF", "weight": "bold"}
                ],
                "backgroundColor": header_color,
                "paddingAll": "10px"
            },
            "hero": {
                "type": "image",
                "url": house.image_url or default_image,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": house.name, "weight": "bold", "size": "md", "wrap": True},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": f"⭐ {house.avg_rating:.1f}", "size": "sm", "color": "#F59E0B", "flex": 1},
                            {"type": "text", "text": f"${house.rent:,}/月", "size": "sm", "color": "#6366F1", "weight": "bold", "flex": 1, "align": "end"}
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "查看詳情",
                            "uri": f"{config.LIFF_URL}?propertyId={house.house_id}"
                        },
                        "style": "primary",
                        "color": button_color,
                        "height": "sm"
                    }
                ]
            }
        }
        bubbles.append(bubble)
    
    return FlexContainer.from_dict({"type": "carousel", "contents": bubbles})


def create_tips_carousel():
    """建立租屋小 Tips Carousel"""
    tips_data = [
        {
            "emoji": "👀",
            "title": "看房前",
            "subtitle": "避雷針",
            "theme_color": "#3B82F6",
            "tips": [
                "確認房東身分（要求看權狀）",
                "檢查採光、壁癌、手機訊號",
                "訂金≠押金，別搞混！"
            ],
            "button_label": "📖 閱讀看房攻略"
        },
        {
            "emoji": "✍️",
            "title": "簽約時",
            "subtitle": "保命符",
            "theme_color": "#10B981",
            "tips": [
                "合約可以帶回去看 3 天",
                "確認修繕責任歸屬",
                "轉租要小心！責任還是你的"
            ],
            "button_label": "⚖️ 查看合約重點"
        },
        {
            "emoji": "🏠",
            "title": "入住後",
            "subtitle": "權益書",
            "theme_color": "#8B5CF6",
            "tips": [
                "遲繳未達 2 個月，房東不能趕你",
                "押金應在 7-14 天內退還",
                "退租前記得拍照存證！"
            ],
            "button_label": "🛡️ 了解房客權益"
        }
    ]
    
    bubbles = []
    for tip in tips_data:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": f"{tip['emoji']} {tip['title']}", "weight": "bold", "size": "md", "color": "#FFFFFF"}
                ],
                "backgroundColor": tip["theme_color"],
                "paddingAll": "15px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": tip["subtitle"], "weight": "bold", "size": "sm", "color": "#1a1a1a"},
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": f"• {t}", "size": "sm", "color": "#666666", "wrap": True, "margin": "sm"}
                            for t in tip["tips"]
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": tip["button_label"],
                            "data": f"action=show_tip_detail&topic={tip['title']}"
                        },
                        "style": "primary",
                        "color": tip["theme_color"],
                        "height": "sm"
                    }
                ]
            }
        }
        bubbles.append(bubble)
    
    return FlexContainer.from_dict({"type": "carousel", "contents": bubbles})


def create_favorites_carousel(favorites, house_map):
    """建立我的收藏 Carousel"""
    bubbles = []
    default_image = "https://via.placeholder.com/400x260/6366F1/FFFFFF?text=No+Image"
    
    for fav in favorites:
        house = house_map.get(fav.house_id)
        if not house:
            continue
        
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": house.image_url or default_image,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": house.name, "weight": "bold", "size": "md", "wrap": True},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": f"${house.rent:,}/月", "size": "sm", "color": "#6366F1", "weight": "bold"},
                            {"type": "text", "text": f"⭐ {house.avg_rating:.1f}", "size": "sm", "color": "#F59E0B", "align": "end"}
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "📄 查看詳情",
                            "data": f"action=show_house_detail&house_id={house.house_id}"
                        },
                        "style": "primary",
                        "color": "#6366F1",
                        "height": "sm",
                        "flex": 2
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "🗑️",
                            "data": f"action=remove_favorite&house_id={house.house_id}"
                        },
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1,
                        "margin": "sm"
                    }
                ]
            }
        }
        bubbles.append(bubble)
    
    return FlexContainer.from_dict({"type": "carousel", "contents": bubbles})


def create_house_detail_card(house):
    """建立房源詳情卡片"""
    default_image = "https://via.placeholder.com/400x260/6366F1/FFFFFF?text=No+Image"
    
    # 解析特徵標籤
    features = house.features or {}
    feature_tags = []
    feature_map = {
        "garbage_service": "🚛 子母車",
        "elevator": "🛗 電梯",
        "security": "🔒 門禁",
        "balcony": "🌿 陽台",
        "laundry": "👔 獨立洗衣",
        "quiet": "🤫 安靜",
        "parking": "🅿️ 停車位"
    }
    for key, label in feature_map.items():
        if features.get(key):
            feature_tags.append(label)
    
    feature_text = " | ".join(feature_tags[:3]) if feature_tags else "暫無特徵資訊"
    
    flex_json = {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "image",
            "url": house.image_url or default_image,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": house.name, "weight": "bold", "size": "lg", "flex": 4, "wrap": True},
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": f"${house.rent:,}/月", "size": "sm", "color": "#FFFFFF", "align": "center"}
                            ],
                            "backgroundColor": "#6366F1",
                            "cornerRadius": "md",
                            "paddingAll": "5px",
                            "flex": 2
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": [
                        {"type": "text", "text": f"⭐ {house.avg_rating:.1f} ({house.review_count} 評價)", "size": "sm", "color": "#F59E0B"},
                        {"type": "text", "text": house.room_type or "套房", "size": "sm", "color": "#666666", "align": "end"}
                    ]
                },
                {"type": "separator", "margin": "lg"},
                {"type": "text", "text": house.description or "暫無詳細描述", "wrap": True, "color": "#666666", "size": "sm", "margin": "lg"},
                {"type": "separator", "margin": "lg"},
                {"type": "text", "text": feature_text, "size": "xs", "color": "#888888", "margin": "lg"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "❤️ 收藏",
                        "data": f"action=add_favorite&house_id={house.house_id}"
                    },
                    "style": "secondary",
                    "height": "sm",
                    "flex": 1
                },
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "📍 地圖",
                        "uri": f"https://www.google.com/maps?q={house.latitude or 23.9576},{house.longitude or 120.9277}"
                    },
                    "style": "primary",
                    "color": "#10B981",
                    "height": "sm",
                    "flex": 1,
                    "margin": "sm"
                },
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "✍️ 評價",
                        "uri": f"{config.BASE_URL}/liff/review?house_id={house.house_id}"
                    },
                    "style": "secondary",
                    "height": "sm",
                    "flex": 1,
                    "margin": "sm"
                }
            ]
        }
    }
    
    return FlexContainer.from_dict(flex_json)


def create_houses_carousel(houses, persona_id, current_offset):
    """建立房源推薦 Carousel（含分頁）"""
    bubbles = []
    default_image = "https://via.placeholder.com/400x260/6366F1/FFFFFF?text=No+Image"
    
    for house in houses:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": house.image_url or default_image,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": house.name, "weight": "bold", "size": "md", "wrap": True},
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": f"⭐ {house.avg_rating:.1f}", "size": "sm", "color": "#F59E0B"},
                            {"type": "text", "text": f"${house.rent:,}/月", "size": "sm", "color": "#6366F1", "weight": "bold", "align": "end"}
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "❤️",
                            "data": f"action=add_favorite&house_id={house.house_id}"
                        },
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "詳情",
                            "uri": f"{config.LIFF_URL}?propertyId={house.house_id}"
                        },
                        "style": "primary",
                        "color": "#6366F1",
                        "height": "sm",
                        "flex": 2,
                        "margin": "sm"
                    }
                ]
            }
        }
        bubbles.append(bubble)
    
    # 添加「查看更多」卡片
    next_offset = current_offset + 5
    more_bubble = {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "justifyContent": "center",
            "contents": [
                {"type": "text", "text": "還有更多...", "weight": "bold", "size": "lg", "align": "center"},
                {"type": "text", "text": "點擊查看更多適合你的房源", "size": "sm", "color": "#888888", "align": "center", "margin": "md"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "📄 查看更多",
                        "data": f"action=show_more_houses&persona={persona_id}&offset={next_offset}"
                    },
                    "style": "primary",
                    "color": "#6366F1"
                }
            ]
        }
    }
    bubbles.append(more_bubble)
    
    return FlexContainer.from_dict({"type": "carousel", "contents": bubbles})


def create_recommendation_carousel(houses_with_scores, persona, persona_id, offset=0):
    """
    建立推薦房源 Carousel (含匹配分數與推薦理由)
    
    Args:
        houses_with_scores: 房源列表，包含匹配分數與推薦理由
        persona: 人物誌實例
        persona_id: 人物誌 ID
        offset: 偏移量 (用於分頁)
        
    Returns:
        FlexContainer: Carousel 容器
    """
    bubbles = []
    default_image = "https://via.placeholder.com/400x260/6366F1/FFFFFF?text=Chi+Soo"
    
    for item in houses_with_scores:
        house = item["house"]
        match_score = item["match_score"]
        reason = item["recommendation_reason"]
        
        # 解析特徵標籤
        features = house.features or {}
        feature_tags = []
        feature_map = {
            "garbage_service": "🚛 子母車",
            "elevator": "🛗 電梯",
            "security": "🔒 門禁",
            "balcony": "🌿 陽台",
            "laundry": "👔 洗衣",
            "quiet": "🤫 安靜",
            "parking": "🅿️ 停車"
        }
        for key, label in feature_map.items():
            if features.get(key):
                feature_tags.append(label)
        
        # 匹配度顏色
        if match_score >= 90:
            match_color = "#EF4444"  # 紅色
            match_emoji = "🔥"
        elif match_score >= 80:
            match_color = "#F59E0B"  # 橙色
            match_emoji = "⭐"
        elif match_score >= 70:
            match_color = "#10B981"  # 綠色
            match_emoji = "✨"
        else:
            match_color = "#6366F1"  # 紫色
            match_emoji = "💡"
        
        # 特徵標籤 (最多顯示 3 個)
        feature_boxes = []
        for tag in feature_tags[:3]:
            feature_boxes.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": tag, "size": "xxs", "color": "#6366F1", "align": "center"}
                ],
                "backgroundColor": "#EEF2FF",
                "cornerRadius": "sm",
                "paddingAll": "3px",
                "margin": "xs"
            })
        
        # 如果沒有特徵標籤，顯示房型
        if not feature_boxes:
            feature_boxes.append({
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": house.room_type or "套房", "size": "xxs", "color": "#6366F1", "align": "center"}
                ],
                "backgroundColor": "#EEF2FF",
                "cornerRadius": "sm",
                "paddingAll": "3px"
            })
        
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": house.image_url or default_image,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": f"{config.LIFF_URL}?propertyId={house.house_id}"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    # 房名與匹配分數
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": house.name, "weight": "bold", "size": "md", "flex": 4, "wrap": True},
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {"type": "text", "text": f"{match_emoji} {match_score}%", "size": "xs", "color": "#FFFFFF", "align": "center", "weight": "bold"}
                                ],
                                "backgroundColor": match_color,
                                "cornerRadius": "md",
                                "paddingAll": "3px",
                                "flex": 2
                            }
                        ]
                    },
                    # 評分與租金
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": f"⭐ {house.avg_rating:.1f}", "size": "sm", "color": "#F59E0B"},
                            {"type": "text", "text": f"${house.rent:,}/月", "size": "sm", "color": "#6366F1", "weight": "bold", "align": "end"}
                        ]
                    },
                    # 推薦理由
                    {
                        "type": "text",
                        "text": reason,
                        "size": "xs",
                        "color": "#666666",
                        "wrap": True,
                        "margin": "md"
                    },
                    # 特徵標籤
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": feature_boxes
                    }
                ],
                "paddingAll": "12px"
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "postback",
                            "label": "❤️",
                            "data": f"action=add_favorite&house_id={house.house_id}"
                        },
                        "style": "secondary",
                        "height": "sm",
                        "flex": 1
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "📍 詳情",
                            "uri": f"{config.LIFF_URL}?propertyId={house.house_id}"
                        },
                        "style": "primary",
                        "color": "#6366F1",
                        "height": "sm",
                        "flex": 2,
                        "margin": "sm"
                    }
                ],
                "paddingAll": "10px"
            }
        }
        bubbles.append(bubble)
    
    # 添加「查看更多」卡片
    next_offset = offset + 5
    persona_name = persona.name if persona else "你"
    
    more_bubble = {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "justifyContent": "center",
            "alignItems": "center",
            "contents": [
                {"type": "text", "text": "🏠", "size": "3xl", "align": "center"},
                {"type": "text", "text": "探索更多房源", "weight": "bold", "size": "lg", "align": "center", "margin": "md"},
                {"type": "text", "text": f"還有更多適合{persona_name}的選擇", "size": "sm", "color": "#888888", "align": "center", "margin": "sm", "wrap": True}
            ],
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": "📄 查看更多",
                        "data": f"action=show_more_houses&persona={persona_id}&offset={next_offset}"
                    },
                    "style": "primary",
                    "color": "#6366F1"
                }
            ],
            "paddingAll": "10px"
        }
    }
    bubbles.append(more_bubble)
    
    return FlexContainer.from_dict({"type": "carousel", "contents": bubbles})

