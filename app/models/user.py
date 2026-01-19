# ============================================================
# models/user.py - 使用者模型
# 專案：Chi Soo 租屋小幫手
# 說明：儲存 LINE 使用者基本資訊與最近測驗結果
# ============================================================

from datetime import datetime
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class User(Base):
    """
    使用者主表
    
    Attributes:
        user_id: LINE User ID (主鍵)
        display_name: LINE 暱稱
        persona_type: 最近一次測驗結果 (如 "type_B")
        is_blocked: 是否已封鎖 Bot
        created_at: 加入時間
        updated_at: 最後更新時間
    """
    __tablename__ = "users"
    
    user_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    picture_url: Mapped[str] = mapped_column(String(255), nullable=True)
    persona_type: Mapped[str] = mapped_column(String(20), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<User {self.user_id[:8]}... ({self.display_name})>"
