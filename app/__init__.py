# ============================================================
# __init__.py - Flask 應用程式工廠
# 專案：Chi Soo 租屋小幫手
# 說明：建立並設定 Flask 應用程式實例
# ============================================================

from flask import Flask
from flask_cors import CORS

from app.config import config


def create_app() -> Flask:
    """
    Flask 應用程式工廠函式
    
    Returns:
        Flask: 設定完成的 Flask 應用程式實例
    """
    app = Flask(__name__)
    
    # 載入設定
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["DEBUG"] = config.DEBUG
    
    # 啟用 CORS (供 LIFF 前端呼叫)
    CORS(app, origins=[
        "https://liff-app-beige.vercel.app",
        "https://liff.line.me",
        "http://localhost:3000",  # 開發環境
    ])
    
    # 驗證必要設定
    missing = config.validate()
    if missing:
        print(f"⚠️ 警告：以下設定項目尚未設定：{', '.join(missing)}")
        print("   請複製 .env.example 為 .env 並填入正確值")
    
    # 註冊藍圖 (Blueprint)
    from app.handlers import register_handlers
    register_handlers(app)
    
    # 註冊資料庫
    from app.models import init_db
    init_db(app)
    
    return app
