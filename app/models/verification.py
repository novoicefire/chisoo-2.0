# ============================================================
# models/verification.py - 學生身份驗證模型
# 專案：Chi Soo 租屋小幫手
# 說明：儲存學生身份驗證申請與審核資料
# ============================================================

from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.models import Base


class VerificationStatus:
    """驗證狀態常數"""
    UNVERIFIED = "unverified"  # 未驗證
    PENDING = "pending"         # 審核中
    VERIFIED = "verified"       # 已通過
    REJECTED = "rejected"       # 已拒絕


class Verification(Base):
    """
    學生身份驗證主表
    
    Attributes:
        id: 主鍵
        user_id: LINE User ID (外鍵)
        name: 學生真實姓名
        student_id: 暨大學號
        dept: 系級 (如：資管三甲)
        front_image_path: 學生證正面照片路徑
        back_image_path: 學生證反面照片路徑
        status: 驗證狀態
        submitted_at: 提交時間
        reviewed_at: 審核時間
        reviewer_note: 審核備註
    """
    __tablename__ = "verifications"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(50), 
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )
    
    # 學生基本資料
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    dept: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 學生證圖片路徑
    front_image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    back_image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 審核狀態 (使用 String 匹配資料庫 VARCHAR)
    status: Mapped[str] = mapped_column(
        String(20),
        default=VerificationStatus.PENDING,
        nullable=False
    )
    
    # 時間戳記
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # 審核備註
    reviewer_note: Mapped[str] = mapped_column(Text, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Verification {self.student_id} - {self.status}>"
    
    def to_dict(self):
        """轉換為字典格式，方便 JSON 序列化"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "student_id": self.student_id,
            "dept": self.dept,
            "front_image_path": self.front_image_path,
            "back_image_path": self.back_image_path,
            "status": self.status,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewer_note": self.reviewer_note
        }
