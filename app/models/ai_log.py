# ============================================================
# models/ai_log.py - AI 思考紀錄模型
# 專案：Chi Soo 租屋小幫手
# 說明：儲存每次 AI 提取與引導的歷史紀錄
# ============================================================

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class AILog(Base):
    """
    AI 思考紀錄表
    
    Attributes:
        id: 主鍵 (自增)
        user_id: LINE User ID (外鍵)
        topic: 當時詢問的主題 (budget/location_pref/...)
        user_input: 使用者輸入
        ai_raw_response: AI 原始回應
        extracted_data: 提取出的結構化資料 (JSON)
        is_success: 是否成功解析
        created_at: 建立時間
    """
    __tablename__ = "ai_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True
    )
    topic: Mapped[str] = mapped_column(String(50), nullable=True)
    user_input: Mapped[str] = mapped_column(Text, nullable=True)
    ai_raw_response: Mapped[str] = mapped_column(Text, nullable=True)
    extracted_data: Mapped[dict] = mapped_column(JSON, default=dict)
    is_success: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", backref="ai_logs")
    
    def __repr__(self) -> str:
        return f"<AILog {self.id} user={self.user_id[:8]}... topic={self.topic}>"
