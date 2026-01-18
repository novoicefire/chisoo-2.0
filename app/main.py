# ============================================================
# main.py - Flask 應用程式入口點
# 專案：Chi Soo 租屋小幫手
# 說明：LINE Bot Webhook 接收端點與應用程式啟動
# ============================================================

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
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

# 建立 Flask 應用程式
app = Flask(__name__)

# 設定 LINE Bot SDK
configuration = Configuration(access_token=config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)


@app.route("/")
def index():
    """健康檢查端點"""
    return {"status": "ok", "service": "Chi Soo 租屋小幫手", "version": "1.0.0"}


@app.route("/callback", methods=["POST"])
def callback():
    """
    LINE Webhook 接收端點
    接收來自 LINE Platform 的事件並分發處理
    """
    # 取得請求標頭中的簽章
    signature = request.headers.get("X-Line-Signature", "")
    
    # 取得請求 body
    body = request.get_data(as_text=True)
    app.logger.info(f"收到 Webhook 請求: {body}")
    
    # 驗證簽章並處理事件
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("無效的簽章，請檢查 Channel Secret 設定")
        abort(400)
    
    return "OK"


# === 事件處理器 ===

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """
    處理文字訊息事件
    根據使用者狀態決定回應方式 (IDLE 模式 / TESTING 模式)
    """
    user_id = event.source.user_id
    user_message = event.message.text
    reply_token = event.reply_token
    
    # TODO: Phase 3 實作 - 根據使用者狀態分流處理
    # 目前先回傳固定訊息作為測試
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 預設回覆 (一般模式自動回覆)
        welcome_message = (
            "你好！我是 Chi Soo 租屋小幫手 🦔\n\n"
            "抱歉，我現在聽不懂一般的文字對話。請使用下方的選單來操作：\n\n"
            "🔍 幫我找窩：AI 幫你分析適合的租屋類型\n"
            "🏆 評價排行榜：看看大家推薦哪裡\n"
            "📚 租屋小Tips：簽約與看房須知\n"
            "❤️ 我的收藏：查看已儲存的房源\n\n"
            "若要開始找房測驗，請點擊選單左上角的『幫我找窩』！"
        )
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=welcome_message)]
            )
        )


@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    """
    處理 Postback 事件 (Rich Menu 點擊)
    根據 action 參數執行對應功能
    """
    user_id = event.source.user_id
    postback_data = event.postback.data
    reply_token = event.reply_token
    
    # TODO: Phase 3 實作 - Postback 事件分流處理
    app.logger.info(f"收到 Postback: user={user_id}, data={postback_data}")
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 暫時回覆收到
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=f"收到指令：{postback_data}")]
            )
        )


@handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    """處理加入好友事件"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    app.logger.info(f"新使用者加入: {user_id}")
    
    # TODO: Phase 2 實作 - 建立使用者資料
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        welcome_message = (
            "🎉 歡迎使用 Chi Soo 租屋小幫手！\n\n"
            "我是專為埔里地區設計的 AI 租屋顧問。\n"
            "我會根據你的需求，推薦最適合你的租屋類型！\n\n"
            "👉 點擊下方選單的『幫我找窩』開始吧！"
        )
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=welcome_message)]
            )
        )


@handler.add(UnfollowEvent)
def handle_unfollow(event: UnfollowEvent):
    """處理封鎖/取消追蹤事件"""
    user_id = event.source.user_id
    app.logger.info(f"使用者取消追蹤: {user_id}")
    
    # TODO: Phase 2 實作 - 更新使用者 is_blocked 狀態


# === 啟動應用程式 ===

if __name__ == "__main__":
    # 印出設定狀態
    config.print_status()
    
    # 啟動開發伺服器
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)
