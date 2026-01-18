# ============================================================
# models/house.py - 房源模型
# 專案：Chi Soo 租屋小幫手
# 說明：儲存埔里地區房源資訊與特徵標籤
# ============================================================

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class House(Base):
    """
    房源表
    
    Attributes:
        house_id: 唯一編號 (主鍵)
        name: 房源名稱
        address: 地址
        category_tag: 歸屬類型 (關聯至 Personas 表)
        rent: 租金
        room_type: 房型 (套房/雅房/家庭式)
        features: 特徵標籤 JSON (子母車:T, 電梯:F...)
        description: 詳細描述
        image_url: 封面圖連結
        images: 多張圖片 JSON 陣列
        latitude: 緯度 (Google Maps)
        longitude: 經度 (Google Maps)
        avg_rating: 平均評分 (從 Reviews 計算)
        review_count: 評價數量
        is_active: 是否上架
        created_at: 建立時間
        updated_at: 更新時間
    """
    __tablename__ = "houses"
    
    house_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=True)
    category_tag: Mapped[str] = mapped_column(String(20), nullable=True)
    rent: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[str] = mapped_column(String(20), default="套房")  # 套房/雅房/整層
    features: Mapped[dict] = mapped_column(JSON, default=dict)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    images: Mapped[list] = mapped_column(JSON, default=list)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<House {self.house_id}: {self.name} (${self.rent})>"
    
    def has_feature(self, feature_key: str) -> bool:
        """檢查是否具備某特徵"""
        return self.features.get(feature_key, False)
    
    def update_rating(self, new_avg: float, new_count: int) -> None:
        """更新評分統計"""
        self.avg_rating = new_avg
        self.review_count = new_count
        self.updated_at = datetime.utcnow()
