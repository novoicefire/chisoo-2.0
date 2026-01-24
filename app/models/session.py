# ============================================================
# models/session.py - 使用者對話狀態模型
# 專案：Chi Soo 租屋小幫手
# 說明：儲存測驗進度，確保可隨時中斷並續答 (取代 Redis)
# ============================================================

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class UserSession(Base):
    """
    對話狀態表 (取代 Redis)
    
    Attributes:
        user_id: LINE User ID (主鍵, 外鍵)
        status: 狀態 ("IDLE" 或 "TESTING")
        collected_data: 已收集的變因 JSON (如 {"budget": 5000, "elevator": true})
        last_updated: 最後互動時間
    """
    __tablename__ = "user_sessions"
    
    user_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    status: Mapped[str] = mapped_column(String(20), default="IDLE")
    collected_data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Weight Selection Stage
    weight_stage: Mapped[int] = mapped_column(default=0)  # 0: Not started, 1-6: In progress
    weight_answers: Mapped[dict] = mapped_column(JSON, default=dict)  # Stores answers for Q1-Q6
    weights: Mapped[dict] = mapped_column(JSON, default=dict)  # Final calculated weights
    
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # 關聯
    user = relationship("User", backref="session")
    
    def __repr__(self) -> str:
        return f"<UserSession {self.user_id[:8]}... status={self.status}>"
    
    def is_testing(self) -> bool:
        """檢查是否處於測試模式"""
        return self.status == "TESTING"
    
    def is_idle(self) -> bool:
        """檢查是否處於一般模式"""
        return self.status == "IDLE"
    
    def has_progress(self) -> bool:
        """檢查是否有未完成的測驗進度"""
        return bool(self.collected_data)
    
    def start_testing(self) -> None:
        """開始測試模式"""
        self.status = "TESTING"
        self.last_updated = datetime.utcnow()
    
    def pause_testing(self) -> None:
        """暫停測試 (切回 IDLE 但保留進度)"""
        self.status = "IDLE"
        self.last_updated = datetime.utcnow()
    
    def reset(self) -> None:
        """重設測驗進度"""
        self.status = "IDLE"
        self.collected_data = {}
        self.last_updated = datetime.utcnow()
