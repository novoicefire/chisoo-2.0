# ============================================================
# config.py - 統一設定管理模組
# 專案：Chi Soo 租屋小幫手
# 說明：從環境變數載入所有設定，提供類型安全的存取方式
# ============================================================

import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()


class Config:
    """應用程式設定類別"""
    
    # === LINE Bot 設定 ===
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")
    
    # === Ollama AI 設定 ===
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL_4B: str = os.getenv("OLLAMA_MODEL_4B", "qwen3:8b")
    
    # === 資料庫設定 ===
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/puli_rental"
    )
    
    # === 外部服務設定 ===
    BASE_URL: str = os.getenv("BASE_URL", "https://chiran.online")
    LIFF_URL: str = os.getenv("LIFF_URL", "https://liff.line.me/2008803154-R8zX1GgB")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # === Flask 設定 ===
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> list[str]:
        """
        驗證必要設定是否已填寫
        
        Returns:
            list[str]: 缺少的設定項目清單
        """
        missing = []
        
        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            missing.append("LINE_CHANNEL_ACCESS_TOKEN")
        if not cls.LINE_CHANNEL_SECRET:
            missing.append("LINE_CHANNEL_SECRET")
            
        return missing
    
    @classmethod
    def print_status(cls) -> None:
        """印出設定狀態 (用於除錯)"""
        print("=" * 50)
        print("Chi Soo 租屋小幫手 - 設定狀態")
        print("=" * 50)
        print(f"LINE Token: {'✓ 已設定' if cls.LINE_CHANNEL_ACCESS_TOKEN else '✗ 未設定'}")
        print(f"LINE Secret: {'✓ 已設定' if cls.LINE_CHANNEL_SECRET else '✗ 未設定'}")
        print(f"Ollama URL: {cls.OLLAMA_BASE_URL}")
        print(f"Ollama Model: {cls.OLLAMA_MODEL_4B}")
        print(f"Database: {'✓ 已設定' if 'localhost' not in cls.DATABASE_URL else cls.DATABASE_URL}")
        print(f"Base URL: {cls.BASE_URL}")
        print(f"Google Maps: {'✓ 已設定' if cls.GOOGLE_MAPS_API_KEY else '✗ 未設定'}")
        print("=" * 50)


# 建立全域設定實例
config = Config()
