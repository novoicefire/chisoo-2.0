# ============================================================
# models/__init__.py - 資料庫模型初始化
# 專案：Chi Soo 租屋小幫手
# 說明：SQLAlchemy ORM 設定與資料庫初始化
# ============================================================

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase

from app.config import config


class Base(DeclarativeBase):
    """SQLAlchemy 基礎類別"""
    pass


# 建立資料庫引擎
engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)

# 建立 Session 工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立 Scoped Session (線程安全)
db_session = scoped_session(SessionLocal)


def init_db(app: Flask) -> None:
    """
    初始化資料庫連線
    
    Args:
        app: Flask 應用程式實例
    """
    # 匯入所有 Model 以確保它們被註冊
    from app.models.user import User
    from app.models.session import UserSession
    from app.models.house import House
    from app.models.review import Review
    from app.models.persona import Persona
    from app.models.favorite import Favorite
    from app.models.ai_log import AILog
    from app.models.verification import Verification
    
    # 建立所有表格
    Base.metadata.create_all(bind=engine)
    
    # 註冊清理函式
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()


def get_db():
    """
    取得資料庫 Session
    
    Yields:
        Session: SQLAlchemy Session 實例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 匯出模型
from app.models.user import User
from app.models.session import UserSession
from app.models.house import House
from app.models.review import Review
from app.models.persona import Persona
from app.models.favorite import Favorite
from app.models.ai_log import AILog
from app.models.verification import Verification

__all__ = [
    "Base",
    "engine",
    "db_session",
    "get_db",
    "init_db",
    "User",
    "UserSession",
    "House",
    "Review",
    "Persona",
    "Favorite",
    "AILog",
    "Verification",
]
