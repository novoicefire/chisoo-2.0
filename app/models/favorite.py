# ============================================================
# models/favorite.py - 收藏模型
# 專案：Chi Soo 租屋小幫手
# 說明：儲存使用者收藏的房源
# ============================================================

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Favorite(Base):
    """
    收藏表
    
    Attributes:
        id: 收藏 ID (主鍵)
        user_id: 使用者 LINE ID (外鍵)
        house_id: 房源 ID (外鍵)
        created_at: 收藏時間
    """
    __tablename__ = "favorites"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("houses.house_id", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User", backref="favorites")
    house = relationship("House", backref="favorited_by")
    
    def __repr__(self) -> str:
        return f"<Favorite User {self.user_id[:8]}... -> House {self.house_id}>"
