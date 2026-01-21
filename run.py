# ============================================================
# run.py - Flask Server Startup Script
# Usage: python run.py
# ============================================================

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_cors import CORS
from app.main import app
from app.config import config
from app.handlers import register_handlers
from app.models import init_db

# 啟用 CORS (供 LIFF 前端呼叫)
CORS(app, origins=[
    "https://liff-app-beige.vercel.app",
    "https://liff.line.me",
    "http://localhost:3000",
    "http://localhost:5173",  # Vite Dev
    "http://localhost:5174",  # Vite Dev
])

# 註冊 API 和 LIFF Blueprint
register_handlers(app)

# 初始化資料庫
init_db(app)

if __name__ == "__main__":
    config.print_status()
    
    # 顯示已註冊的路由
    print("\n📋 已註冊的路由:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.methods} {rule.rule}")
    print()
    
    app.run(host="0.0.0.0", port=5000, debug=True)
