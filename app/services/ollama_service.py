# ============================================================
# services/ollama_service.py - AI 雙模型流水線服務
# 專案：Chi Soo 租屋小幫手
# 說明：封裝 Ollama API 調用，實作 gemma3:4b → gemma3:1b 雙階段處理
# ============================================================

import json
import requests
from typing import Optional

from app.config import config


class OllamaService:
    """
    Ollama AI 雙模型流水線服務
    
    實作設計文件中的雙階段處理：
    1. Stage 1 (gemma3:4b): 從使用者對話中提取標籤與參數
    2. Stage 2 (gemma3:1b): 確認資料完整性並生成追問語句
    """
    
    # 必要檢查清單 (使用者需提供的核心資訊)
    REQUIRED_FIELDS = ["budget", "location_pref"]
    
    # 可選欄位 (有則加分，無則不影響)
    OPTIONAL_FIELDS = ["garbage_service", "elevator", "quiet", "type_pref", "security"]
    
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model_4b = config.OLLAMA_MODEL_4B
        self.model_1b = config.OLLAMA_MODEL_1B
    
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
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama API 錯誤: {e}")
            return ""
    
    def _get_extraction_prompt(self) -> str:
        """取得提取參數的系統提示詞 (Stage 1: gemma3:4b)"""
        return """你是一個資料提取員。請分析使用者的輸入，並將其轉換為 JSON 格式。
請只輸出 JSON，不要包含任何解釋性文字或 markdown 標記。

需要提取的欄位：
- budget (整數): 預算上限，單位為新台幣
- location_pref (字串): 地點偏好，可能值為 "downtown"(市區)、"school"(學校附近)、"quiet"(安靜偏僻)
- garbage_service (布林): 是否需要子母車收垃圾
- elevator (布林): 是否需要電梯
- quiet (布林): 是否需要安靜環境
- type_pref (字串): 房型偏好，可能值為 "套房"、"雅房"、"整層"
- security (布林): 是否需要門禁/監視器等安全設施

規則：
1. 只提取使用者明確提到的資訊
2. 如果某個欄位沒有提到，不要包含在輸出中
3. 預算相關詞彙對照：「便宜」→ 3500、「中等」→ 5500、「不限」→ 10000
4. 地點相關詞彙對照：「市區」「方便」→ downtown、「學校」「暨大」→ school、「安靜」「偏僻」→ quiet

輸出範例：
{"budget": 5000, "garbage_service": true}"""
    
    def _get_confirmation_prompt(self) -> str:
        """取得確認與追問的系統提示詞 (Stage 2: gemma3:1b)"""
        return """你是一個親切的租屋顧問。
你會收到兩個資訊：
1. 目前已收集的使用者資料 (JSON)
2. 必要的檢查清單

任務：
檢查 JSON 中是否所有檢查清單的項目都已填寫。

- 若資料缺失：請用親切的繁體中文，針對缺失的項目提出「一個」追問問題。
  問題要自然、口語化，像朋友聊天一樣。
  
- 若資料齊全：請只輸出字串 "COMPLETE"（不要輸出其他任何文字）。

範例：
輸入: {"budget": 5000, "garbage_service": true}, 檢查清單: ["location_pref"]
輸出: 了解，那請問您希望住在靠近市區還是學校附近呢？

輸入: {"budget": 5000, "location_pref": "downtown"}, 檢查清單: ["budget", "location_pref"]
輸出: COMPLETE"""
    
    def extract_params(self, user_input: str) -> dict:
        """
        Stage 1: 從使用者輸入提取參數
        
        Args:
            user_input: 使用者的自然語言輸入
            
        Returns:
            dict: 提取出的參數
        """
        system_prompt = self._get_extraction_prompt()
        
        response = self._call_ollama(
            model=self.model_4b,
            prompt=user_input,
            system=system_prompt
        )
        
        # 嘗試解析 JSON
        try:
            # 清理可能的 markdown 標記
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            
            return json.loads(response)
        except json.JSONDecodeError:
            print(f"⚠️ JSON 解析失敗: {response}")
            return {}
    
    def check_and_respond(self, collected_data: dict) -> tuple[bool, str]:
        """
        Stage 2: 檢查資料完整性並生成回應
        
        Args:
            collected_data: 目前已收集的資料
            
        Returns:
            tuple[bool, str]: (是否完成, 追問語句或確認訊息)
        """
        system_prompt = self._get_confirmation_prompt()
        
        # 建立輸入格式
        prompt = f"""已收集資料: {json.dumps(collected_data, ensure_ascii=False)}
檢查清單: {json.dumps(self.REQUIRED_FIELDS)}"""
        
        response = self._call_ollama(
            model=self.model_1b,
            prompt=prompt,
            system=system_prompt
        )
        
        response = response.strip()
        
        if response == "COMPLETE" or "COMPLETE" in response:
            return True, "好的！我已經了解您的需求了。請輸入 **『開始分析』** 來查看您的專屬租屋人格診斷。"
        else:
            return False, response
    
    def analyze_and_respond(self, user_input: str, collected_data: dict) -> dict:
        """
        完整的雙階段分析流程
        
        Args:
            user_input: 使用者輸入
            collected_data: 目前已收集的資料
            
        Returns:
            dict: {
                "collected_data": 更新後的資料,
                "is_complete": 是否完成資料收集,
                "response": 要回覆給使用者的訊息
            }
        """
        # Stage 1: 提取參數
        extracted = self.extract_params(user_input)
        
        # 合併已收集的資料
        merged_data = {**collected_data, **extracted}
        
        # Stage 2: 檢查完整性並生成回應
        is_complete, response = self.check_and_respond(merged_data)
        
        return {
            "collected_data": merged_data,
            "is_complete": is_complete,
            "response": response
        }
    
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
