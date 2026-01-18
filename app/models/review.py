# ============================================================
# models/review.py - 評價模型
# 專案：Chi Soo 租屋小幫手
# 說明：儲存使用者對房源的評價，含審核狀態與學生證驗證
# ============================================================

from datetime import datetime, date
from sqlalchemy import String, Integer, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Review(Base):
    """
    評價表
    
    Attributes:
        review_id: 評價 ID (主鍵)
        house_id: 關聯房源 (外鍵)
        user_id: 評論者 LINE ID (外鍵)
        rating: 1-5 星評分
        comment: 評論內容
        status: 審核狀態 (pending/approved/rejected)
        student_card_img: 學生證圖片路徑
        reject_reason: 駁回原因
        created_date: 評價日期 (用於計算每日限額)
        created_at: 建立時間
        updated_at: 更新時間
    """
    __tablename__ = "reviews"
    
    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("houses.house_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 星
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/approved/rejected
    student_card_img: Mapped[str] = mapped_column(String(500), nullable=True)
    reject_reason: Mapped[str] = mapped_column(String(200), nullable=True)
    created_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # 關聯
    house = relationship("House", backref="reviews")
    user = relationship("User", backref="reviews")
    
    def __repr__(self) -> str:
        return f"<Review {self.review_id}: House {self.house_id} - {self.rating}★>"
    
    def is_pending(self) -> bool:
        """是否待審核"""
        return self.status == "pending"
    
    def is_approved(self) -> bool:
        """是否已通過"""
        return self.status == "approved"
    
    def is_rejected(self) -> bool:
        """是否已駁回"""
        return self.status == "rejected"
    
    def approve(self) -> None:
        """通過審核"""
        self.status = "approved"
        self.updated_at = datetime.utcnow()
    
    def reject(self, reason: str) -> None:
        """駁回評價"""
        self.status = "rejected"
        self.reject_reason = reason
        self.updated_at = datetime.utcnow()
