# ============================================================
# handlers/__init__.py - 事件處理器註冊
# 專案：Chi Soo 租屋小幫手
# 說明：統一註冊所有 Flask Blueprint 與事件處理器
# ============================================================

from flask import Flask


def register_handlers(app: Flask) -> None:
    """
    註冊所有事件處理器藍圖
    
    Args:
        app: Flask 應用程式實例
    """
    # 註冊 API 藍圖
    from app.handlers.api import api_bp
    from app.handlers.verification import verification_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(verification_bp)  # 已包含 /api/verification prefix
    
    # [停用] LIFF 頁面藍圖 - 功能重新設計中
    # from app.handlers.liff import liff_bp
    # app.register_blueprint(liff_bp, url_prefix="/liff")
