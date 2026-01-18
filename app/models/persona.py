# ============================================================
# models/persona.py - 人物誌配置模型
# 專案：Chi Soo 租屋小幫手
# 說明：動態管理所有租屋類型及其匹配邏輯 (不寫死在程式碼中)
# ============================================================

from datetime import datetime
from sqlalchemy import String, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Persona(Base):
    """
    人物誌配置表
    
    系統啟動時會從此表載入所有設定，管理員可透過資料庫隨時：
    1. 增減分類數量
    2. 修改類型名稱
    3. 調整核心關鍵字與演算法參數
    
    Attributes:
        persona_id: 唯一代碼 (主鍵，如 "type_A")
        name: 顯示名稱 (如 "省錢戰士型")
        description: 診斷書上的描述文案
        keywords: 觸發關鍵字 JSON 列表 (如 ["便宜", "雅房"])
        algo_config: 匹配演算法參數 JSON
        icon_url: 類型圖示 URL
        active: 是否啟用此分類
        created_at: 建立時間
        updated_at: 更新時間
    """
    __tablename__ = "personas"
    
    persona_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    algo_config: Mapped[dict] = mapped_column(JSON, default=dict)
    icon_url: Mapped[str] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        status = "✓" if self.active else "✗"
        return f"<Persona {self.persona_id}: {self.name} [{status}]>"
    
    def get_rent_range(self) -> tuple[int, int]:
        """取得建議租金區間"""
        rent_min = self.algo_config.get("rent_min", 0)
        rent_max = self.algo_config.get("rent_max", 99999)
        return (rent_min, rent_max)
    
    def get_required_features(self) -> list[str]:
        """取得必要設施清單"""
        return self.algo_config.get("required", [])
    
    def get_bonus_features(self) -> list[str]:
        """取得加分設施清單"""
        return self.algo_config.get("bonus", [])
    
    def get_preferred_locations(self) -> list[str]:
        """取得偏好地點清單"""
        return self.algo_config.get("preferred_locations", [])
    
    def matches_keyword(self, text: str) -> int:
        """
        計算文字中命中的關鍵字數量
        
        Args:
            text: 使用者輸入的文字
            
        Returns:
            int: 命中的關鍵字數量
        """
        count = 0
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                count += 1
        return count
