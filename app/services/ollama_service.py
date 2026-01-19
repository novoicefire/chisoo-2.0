# ============================================================
# services/ollama_service.py - AI 雙階段流水線服務
# 專案：Chi Soo 租屋小幫手
# 說明：封裝 Ollama API 調用
# ============================================================

import json
import requests
from typing import Optional

from app.config import config


class OllamaService:
    """
    Ollama AI 雙階段流水線服務
    
    實作設計文件中的雙階段處理：
    1. Stage 1 : 從使用者對話中提取標籤與參數
    2. Stage 2 : 確認資料完整性並生成追問語句
    """
    
    # 必要檢查清單 - 根據演算法文件的六大維度 (關鍵字為隱性維度，不須詢問)
    # 1. 預算 (budget)
    # 2. 地點 (location_pref)
    # 3. 房型 (type_pref)
    # 4. 管理偏好 (management_pref)
    # 5. 設施需求 (features_preference) - 確認使用者是否有一得必有的設施
    REQUIRED_FIELDS = ["budget", "location_pref", "type_pref", "management_pref", "features_preference"]
    
    # 可選欄位 - 設施需求 (自由文字陣列)
    OPTIONAL_FIELDS = ["required_features"]
    
    # 追問問題庫
    QUESTIONS = {
        "budget": (
            "💰 首先，請問您的 月租預算上限 大約是多少呢？\n\n"
            "請直接輸入數字，或選擇：\n"
            "• 輸入「3000」「5000」「8000」等數字\n"
            "• 或輸入「不限」「隨便」代表沒有預算限制"
        ),
        "location_pref": (
            "📍 請問您希望住在哪個區域呢？\n\n" 
            "1️⃣ 靠近市區 - 生活機能好、吃飯購物方便\n"
            "2️⃣ 靠近學校 - 通勤方便、上課不遲到\n"
            "3️⃣ 安靜偏僻 - 環境清幽、租金較便宜\n\n"
            "請輸入 1、2、3 或直接描述您的偏好～"
        ),
        "type_pref": (
            "🏠 請問您偏好哪種 房型 呢？\n\n"
            "1️⃣ 套房 - 獨立衛浴、隱私性高\n"
            "2️⃣ 雅房 - 共用衛浴、租金較低\n"
            "3️⃣ 整層公寓 - 跟朋友合租、空間大\n\n"
            "請輸入 1、2、3 或直接描述～"
        ),
        "management_pref": (
            "👤 關於 房東管理方式，您有什麼偏好嗎？\n\n"
            "1️⃣ 房東同住 - 有問題可以直接找人\n"
            "2️⃣ 專業管理 - 管理公司處理，較有保障\n"
            "3️⃣ 房東不住 - 自由度高，不受打擾\n"
            "4️⃣ 都可以 - 沒有特別偏好\n\n"
            "請輸入 1、2、3、4 或直接描述～"
        ),
        "features_preference": (
            "🔧 最後，有沒有什麼 必備設施 是您一定要有的？\n\n"
            "可以多選，例如：\n"
            "• 子母車（垃圾代收）\n"
            "• 電梯\n"
            "• 門禁/監視器\n"
            "• 機車停車位\n"
            "• 陽台\n\n"
            "請列出您在意的設施，若沒有特別需求請輸入「都可以」！"
        )
    }
    
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model_4b = config.OLLAMA_MODEL_4B
        # Stage 2 改由程式邏輯處理，不再需要 model_1b
    
    def _call_ollama(self, model: str, prompt: str, system: str = None) -> str:
        """
        調用 Ollama API
        
        Args:
            model: 模型名稱
            prompt: 使用者輸入
            system: 系統提示詞
            
        Returns:
            str: 模型回應
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama API 錯誤: {e}")
            return ""
    
    def _get_extraction_prompt(self, topic: str = None) -> str:
        """取得提取參數的系統提示詞 (Stage 1: 本地AI模型)"""
        base_prompt = """你是一個資料提取員，服務對象是大學生租屋族群。
請分析使用者的輸入，用語意理解將其轉換為 JSON 格式。
請只輸出 JSON，不要包含任何解釋性文字或 markdown 標記。
【重要】你必須使用繁體中文回答，禁止使用簡體中文。

需要提取的欄位（請用語意理解歸類）：

📍 budget (整數): 月租預算上限（新台幣）
   - 判斷使用者能接受的最高月租金額
   - 若說「便宜/省錢/窮學生」→ 約 3500
   - 若說「一般/普通/中等」→ 約 5500
   - 若說「不限/隨便/預算夠」→ 99999
   - 若說具體金額如「五千」「5000」→ 直接使用該數字

📍 location_pref (字串): 地點偏好，歸類到以下三種之一：
   * "downtown" = 生活機能好、購物方便、熱鬧
     （例：市區、菜市場、夜市、超商多、吃飯方便、便利）
   * "school" = 靠近學校、通勤方便
     （例：學校附近、暨大、校門口、走路上課、近一點）
   * "quiet" = 環境清幽、安靜、偏僻
     （例：安靜、偏僻、人少、便宜的地方、清幽）

📍 type_pref (字串): 房型偏好，歸類到以下三種之一：
   * "套房" = 獨立空間、有衛浴、隱私高、一個人住
     （例：套房、獨立衛浴、自己住、不想共用廁所）
   * "雅房" = 共用衛浴、價格較低、可接受室友
     （例：雅房、便宜、共用衛浴、省錢）
   * "整層" = 整層公寓、與朋友合租、空間大
     （例：整層、公寓、合租、跟朋友一起、三房）

📍 management_pref (字串): 房東管理偏好，歸類到以下四種之一：
   * "owner" = 房東同住，方便找人處理問題
     （例：房東住、有人管、方便修繕）
   * "pro" = 專業管理公司，有保障
     （例：管理公司、專業、有制度）
   * "no_owner" = 房東不住，自由度高
     （例：房東不住、自由、不被打擾、獨立）
   * "none" = 沒有偏好、都可以
     （例：都可以、沒差、隨便、無所謂）

📍 features_preference (字串): 設施需求回答狀態
   - 當使用者完成設施需求回答時（說了具體設施或說「都可以」）→ 填入 "done"

📍 required_features (字串陣列): 使用者提到的設施需求
   - 例如 ["洗衣機", "冷氣", "電梯"]
   - 常見設施：洗衣機、冷氣、冰箱、熱水器、電梯、子母車(垃圾代收)、
     門禁、監視器、車位、陽台、對外窗、網路/WiFi、傢俱、床、衣櫃、書桌

規則：
1. 只提取使用者明確提到的資訊，沒提到的欄位不要輸出
2. 用語意理解判斷使用者意圖，不要死板對照關鍵字
3. 若無法判斷屬於哪一類，寧可不輸出該欄位"""

        if topic == "management_pref":
             base_prompt += '\n5. 當前正在詢問「管理偏好」，若使用者回答「隨便/都可以/沒差」，請輸出 {"management_pref": "none"}'
        elif topic == "features_preference":
             base_prompt += '\n5. 當前正在詢問「設施需求」，若使用者回答「隨便/都可以/沒差」，請輸出 {"features_preference": "done"}'
        elif topic == "budget":
             base_prompt += '\n5. 當前正在詢問「預算」，若使用者回答「隨便/不限」，請輸出 {"budget": 99999}'
        elif topic == "type_pref":
             base_prompt += '\n5. 當前正在詢問「房型」，若使用者回答「一個人住/單人/獨居」，請傾向輸出 {"type_pref": "套房"}'

        # 根據不同主題提供對應的範例，避免 AI 混淆
        if topic == "budget":
            base_prompt += '\n\n輸出範例：\n{"budget": 5000}'
        elif topic == "location_pref":
            base_prompt += '\n\n輸出範例：\n{"location_pref": "downtown"}'
        elif topic == "type_pref":
             base_prompt += '\n\n輸出範例：\n{"type_pref": "套房"}'
        elif topic == "management_pref":
             base_prompt += '\n\n輸出範例：\n{"management_pref": "no_owner"}'
        elif topic == "features_preference":
             base_prompt += '\n\n輸出範例：\n{"required_features": ["洗衣機", "陽台"], "features_preference": "done"}'
        else:
             base_prompt += '\n\n輸出範例：\n{"budget": 5000}'
             
        return base_prompt
    
    def extract_params(self, user_input: str, topic: str = None) -> dict:
        """
        Stage 1: 從使用者輸入提取參數
        
        Args:
            user_input: 使用者的自然語言輸入
            topic: 當前正在詢問的主題 (上下文)
            
        Returns:
            dict: 提取出的參數
        """
        system_prompt = self._get_extraction_prompt(topic)
        
        response = self._call_ollama(
            model=self.model_4b,
            prompt=user_input,
            system=system_prompt
        )
        
        # 嘗試解析 JSON
        try:
            # 清理可能的 markdown 標記
            response = response.strip()
            
            # 清理 <think> 標籤 (針對思考型模型)
            import re
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            
            if response.startswith("```"):
                lines = response.split("\n")
                # 尋找 JSON 區塊
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith("```"):
                        if in_json: break
                        else: in_json = True; continue
                    if in_json:
                        json_lines.append(line)
                
                if json_lines:
                    response = "\n".join(json_lines)
                else:
                    # Fallback: 如果沒有完整包覆，嘗試去掉第一行和最後一行
                    response = "\n".join(lines[1:-1])
            
            # 有時候模型會輸出 JSON 以外的廢話，嘗試只抓取第一個 { 到最後一個 }
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ JSON 解析失敗: {response} (Error: {e})")
            return {}
    
    def check_completeness(self, collected_data: dict) -> tuple[bool, list[str]]:
        """
        用程式邏輯檢查資料完整性 (不依賴 AI)
        
        Args:
            collected_data: 目前已收集的資料
            
        Returns:
            tuple[bool, list[str]]: (是否完成, 缺少的欄位列表)
        """
        missing = []
        for field in self.REQUIRED_FIELDS:
            if field not in collected_data or collected_data[field] is None:
                missing.append(field)
        
        return len(missing) == 0, missing
    
    def generate_follow_up_question(self, missing_fields: list[str]) -> str:
        """
        根據缺少的欄位生成追問問題 (使用預設問題庫)
        
        Args:
            missing_fields: 缺少的欄位列表
            
        Returns:
            str: 追問問題
        """
        if missing_fields:
            first_missing = missing_fields[0]
            return self.QUESTIONS.get(first_missing, f"請問您對 {first_missing} 有什麼偏好嗎？")
        
        return "請告訴我更多您的需求～"
    
    def check_and_respond(self, collected_data: dict) -> tuple[bool, str]:
        """
        Stage 2: 檢查資料完整性並生成回應 (改用程式邏輯)
        
        Args:
            collected_data: 目前已收集的資料
            
        Returns:
            tuple[bool, str]: (是否完成, 追問語句或確認訊息)
        """
        is_complete, missing = self.check_completeness(collected_data)
        
        if is_complete:
            return True, "好的！我已經了解您的需求了。請輸入 『開始分析』 來查看您的專屬租屋人格診斷。"
        else:
            return False, self.generate_follow_up_question(missing)
    
    def analyze_and_respond(self, user_input: str, collected_data: dict, user_id: str = None) -> dict:
        """
        完整的分析流程 (Stage 1 用 AI 提取，Stage 2 用程式判斷)
        
        Args:
            user_input: 使用者輸入
            collected_data: 目前已收集的資料
            user_id: 使用者 ID (用於儲存 AI 紀錄)
            
        Returns:
            dict: {
                "collected_data": 更新後的資料,
                "is_complete": 是否完成資料收集,
                "response": 要回覆給使用者的訊息
            }
        """
        # 0. 判斷當前上下文 (正在問哪一題)
        # 用程式邏輯預判缺少的欄位，找出第一個缺失項作為 context
        _, missing_before = self.check_completeness(collected_data)
        current_topic = missing_before[0] if missing_before else None
        print(f"🧠 當前上下文推斷: {current_topic}")

        # Stage 1: 提取參數 (帶入上下文)
        extracted = self.extract_params(user_input, topic=current_topic)
        print(f"🔍 AI 提取結果: {extracted}")
        
        # 用於紀錄的變數
        ai_raw_response = str(extracted) if extracted else ""
        is_success = bool(extracted)
        
        # 如果 AI 沒提取到東西，嘗試用簡單規則解析
        if not extracted:
            extracted = self._simple_parse(user_input, topic=current_topic)
            print(f"📝 簡單解析結果: {extracted}")
            if extracted:
                ai_raw_response = f"[規則解析] {extracted}"
                is_success = True
        
        # 合併已收集的資料
        merged_data = {**collected_data, **extracted}
        print(f"📦 合併後資料: {merged_data}")
        
        # 判斷是否成功提取到資料
        if extracted:
            # 成功提取：走標準流程 (檢查資料完整性 -> 下一題)
            is_complete, response = self.check_and_respond(merged_data)
        else:
            # 提取失敗 (例外狀況)：請 AI 針對使用者的回答給予引導
            print(f"⚠️ 提取失敗，啟動 AI 引導模式 (Topic: {current_topic})")
            is_complete = False
            response = self.generate_guidance(user_input, current_topic)
            ai_raw_response = f"[引導] {response}"
        
        # 儲存 AI 紀錄
        if user_id:
            self._save_ai_log(
                user_id=user_id,
                topic=current_topic,
                user_input=user_input,
                ai_raw_response=ai_raw_response,
                extracted_data=extracted,
                is_success=is_success
            )
        
        return {
            "collected_data": merged_data,
            "is_complete": is_complete,
            "response": response
        }
    
    def _save_ai_log(self, user_id: str, topic: str, user_input: str, 
                     ai_raw_response: str, extracted_data: dict, is_success: bool) -> None:
        """
        儲存 AI 思考紀錄
        """
        try:
            from app.models import db_session
            from app.models.ai_log import AILog
            
            log = AILog(
                user_id=user_id,
                topic=topic,
                user_input=user_input,
                ai_raw_response=ai_raw_response,
                extracted_data=extracted_data or {},
                is_success=is_success
            )
            db_session.add(log)
            db_session.commit()
            print(f"📝 已儲存 AI 紀錄: user={user_id[:8]}... topic={topic}")
        except Exception as e:
            print(f"⚠️ 儲存 AI 紀錄失敗: {e}")
    
    def generate_guidance(self, user_input: str, topic: str) -> str:
        """
        當使用者回答無法被解析時，生成引導語句
        
        Args:
            user_input: 使用者輸入
            topic: 當前主題
            
        Returns:
            str: 引導語句
        """
        topic_name = {
            "budget": "預算範圍",
            "location_pref": "地點偏好",
            "type_pref": "房型偏好",
            "management_pref": "管理方式",
            "features_preference": "設施需求"
        }.get(topic, "租屋需求")
        
        # 取得原題目內容供 AI 對照
        original_question = self.QUESTIONS.get(topic, "")
        
        system_prompt = f"""你是 Chi Soo，一個親切的專門服務台灣南投縣埔里鎮暨南大學生的租屋顧問機器人 🦔

【背景】
- 你正在幫助「大學生」尋找學校附近的「租屋」（不是買房！）
- 使用者大多是年輕族群，語氣可以輕鬆活潑、像學長姐一樣親切
- 目標是收集租屋需求資訊，幫他們找到適合的房源

【當前情境】
正在詢問使用者的「{topic_name}」。

原本的題目是：
---
{original_question}
---

使用者回答了：「{user_input}」
但這個回答無法被正確解析（可能答非所問、或格式不對）。

【任務】
生成一句話 (15 字以內) 引導使用者重新作答：
- 告知回答偏題了，請用戶要根據題目再回答一次
- 語氣輕鬆自然，像朋友聊天

【重要】使用繁體中文，直接輸出那一句話，不要有多餘文字。"""

        response = self._call_ollama(
            model=self.model_4b,
            prompt=user_input,
            system=system_prompt
        )
        
        # 清理回應
        response = response.strip().replace('"', '')
        
        # 如果 AI 回應太短或失敗，回退到預設問題
        if len(response) < 5:
            return self.QUESTIONS.get(topic, "不好意思，可以請您再說明一次嗎？")
            
        return response
    
    def _simple_parse(self, user_input: str, topic: str = None) -> dict:
        """
        簡單規則解析 (當 AI 失敗時的備用方案)
        """
        result = {}
        text = user_input.lower()
        
        # 解析預算 (優先判斷是否為數字且數值較大)
        import re
        budget_match = re.search(r'(\d{3,5})', user_input)
        if budget_match:
            result["budget"] = int(budget_match.group(1))
        elif "便宜" in text or "省" in text:
            result["budget"] = 3500
        elif "不限" in text or "無上限" in text or "沒有上限" in text:
            result["budget"] = 99999
        elif "隨便" in text and ("預算" in text or topic == "budget"):
            result["budget"] = 99999
        
        # 解析地點
        if "市區" in text or "方便" in text or "1" in text:
            result["location_pref"] = "downtown"
        elif "學校" in text or "暨大" in text or "2" in text:
            result["location_pref"] = "school"
        elif "安靜" in text or "偏僻" in text or "3" in text:
            result["location_pref"] = "quiet"
        elif "隨便" in text and ("地點" in text or topic == "location_pref"):
            result["location_pref"] = "school" # 隨便的話預設給學校(方便)
        
        # 解析房型偏好
        if "套房" in text or user_input.strip() == "1":
            result["type_pref"] = "套房"
        elif "雅房" in text or user_input.strip() == "2":
            result["type_pref"] = "雅房"
        elif "整層" in text or "公寓" in text or "合租" in text or user_input.strip() == "3":
            result["type_pref"] = "整層"
        elif "隨便" in text and ("房型" in text or topic == "type_pref"):
            result["type_pref"] = "套房" # 預設
        
        # 解析管理偏好
        if "房東同住" in text or "同住" in text or user_input.strip() == "1":
            result["management_pref"] = "owner"
        elif "專業管理" in text or "管理公司" in text or user_input.strip() == "2":
            result["management_pref"] = "pro"
        elif "不住" in text or "不要住" in text or "自由" in text or user_input.strip() == "3":
            result["management_pref"] = "no_owner"
        elif ("都可" in text or "無所謂" in text or "沒差" in text or user_input.strip() == "4" or "隨便" in text) and \
             ("管理" in text or topic == "management_pref"):
            result["management_pref"] = "none"
        
        # 解析設施需求 (改用自由文字陣列)
        feature_keywords = {
            "洗衣機": ["洗衣", "洗衣機"],
            "冷氣": ["冷氣", "空調", "冷氣機"],
            "冰箱": ["冰箱"],
            "熱水器": ["熱水器", "熱水"],
            "電梯": ["電梯"],
            "子母車": ["子母車", "垃圾", "代收"],
            "門禁": ["門禁", "刷卡"],
            "監視器": ["監視", "監控", "攝影"],
            "車位": ["停車", "車位", "機車"],
            "陽台": ["陽台", "曬衣"],
            "對外窗": ["對外窗", "窗戶", "採光"],
            "網路": ["網路", "wifi", "wi-fi"],
            "傢俱": ["傢俱", "家具"],
            "床": ["床"],
            "衣櫃": ["衣櫃", "衣櫥"],
            "書桌": ["書桌", "桌子"],
        }
        
        found_features = []
        for feature_name, keywords in feature_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    found_features.append(feature_name)
                    break
        
        if found_features:
            result["required_features"] = found_features
            result["features_preference"] = "done"
        
        # 若正在問設施且回答隨便/都可以，也標記完成
        is_generic_reply = "都可" in text or "沒差" in text or "無所謂" in text or "沒有" in text or "隨便" in text
        
        # 已在上方處理 found_features，這裡只處理「都可以」的情況
        if is_generic_reply and topic == "features_preference" and "features_preference" not in result:
            result["features_preference"] = "done"
        
        return result
    
    def test_connection(self) -> bool:
        """
        測試 Ollama 連線
        
        Returns:
            bool: 是否連線成功
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> list[str]:
        """
        列出可用的模型
        
        Returns:
            list[str]: 模型名稱列表
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except requests.exceptions.RequestException:
            return []
    
    def match_features_semantically(self, user_features: list[str], persona_features: list[str]) -> dict:
        """
        使用 AI 進行語意特徵匹配 (單一 Persona)
        
        Args:
            user_features: 使用者想要的設施列表
            persona_features: 人物誌提供的設施列表
            
        Returns:
            dict: {"matched": int, "total": int, "match_rate": float}
        """
        if not user_features:
            return {"matched": 0, "total": 0, "match_rate": 0.5}
        
        if not persona_features:
            return {"matched": 0, "total": len(user_features), "match_rate": 0.0}
        
        # 簡單字串包含匹配 (Fallback 邏輯，快速)
        matched = 0
        persona_str = " ".join(persona_features).lower()
        for feature in user_features:
            if feature.lower() in persona_str or any(f.lower() in feature.lower() for f in persona_features):
                matched += 1
        
        return {
            "matched": matched,
            "total": len(user_features),
            "match_rate": matched / len(user_features) if user_features else 0
        }
    
    def batch_match_features(self, user_features: list[str], all_personas_features: dict[str, list[str]]) -> dict[str, dict]:
        """
        使用 AI 批次進行所有 Persona 的語意特徵匹配 (單次 API 呼叫)
        
        Args:
            user_features: 使用者想要的設施列表 (如 ["洗衣機", "陽台"])
            all_personas_features: 所有人物誌的設施字典 
                {"type_A": ["washer", "elevator"], "type_B": ["wifi", "parking"], ...}
            
        Returns:
            dict: {"type_A": {"matched": 2, "total": 2, "match_rate": 1.0}, ...}
        """
        if not user_features:
            return {pid: {"matched": 0, "total": 0, "match_rate": 0.5} for pid in all_personas_features}
        
        # 建構批次比對的提示詞
        personas_list_str = "\n".join([f"- {pid}: {features}" for pid, features in all_personas_features.items()])
        
        system_prompt = f"""你是一個設施匹配專家。請判斷使用者想要的設施在每個租屋類型中是否存在。
使用語意理解來判斷，例如「洗衣機」應該匹配「washer」或「洗衣設備」。

使用者想要的設施: {user_features}

各類型可提供的設施:
{personas_list_str}

請回傳一個 JSON，格式如下：
{{
  "類型ID": {{"matched_count": 匹配數量}},
  ...
}}

例如：
{{
  "type_A": {{"matched_count": 2}},
  "type_B": {{"matched_count": 1}}
}}

【重要】只輸出 JSON，不要有其他文字。使用繁體中文思考但輸出英文 key。"""

        response = self._call_ollama(
            model=self.model_4b,
            prompt="請進行批次設施匹配分析",
            system=system_prompt
        )
        
        try:
            import re
            response = response.strip()
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            result = json.loads(response)
            
            # 轉換成標準格式
            output = {}
            total = len(user_features)
            for pid in all_personas_features:
                matched = result.get(pid, {}).get("matched_count", 0)
                output[pid] = {
                    "matched": matched,
                    "total": total,
                    "match_rate": matched / total if total > 0 else 0
                }
            
            print(f"🔗 AI 批次設施匹配完成")
            for pid, data in output.items():
                print(f"   {pid}: {data['matched']}/{data['total']} ({data['match_rate']*100:.0f}%)")
            
            return output
            
        except Exception as e:
            print(f"⚠️ AI 批次設施匹配解析失敗: {e}")
            # Fallback: 逐一使用簡單匹配
            return {pid: self.match_features_semantically(user_features, features) 
                    for pid, features in all_personas_features.items()}
