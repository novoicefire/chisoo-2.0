# ============================================================
# services/matching_service.py - 租屋類型匹配演算法服務
# 專案：Chi Soo 租屋小幫手
# 說明：實作六維度評分計算器，動態載入 Persona 並進行匹配
# ============================================================

import math
from typing import Optional

from app.models import db_session
from app.models.persona import Persona
from app.models.house import House


class MatchingService:
    """
    租屋類型匹配演算法服務
    
    實作設計文件中的六維度評分計算：
    1. 預算契合度 (S_budget) - 權重 1.5
    2. 地段便利性 (S_location) - 權重 1.2
    3. 硬體設施 (S_features) - 權重 1.0
    4. 管理模式 (S_landlord) - 權重 1.0
    5. 房型偏好 (S_type) - 權重 0.8
    6. 語意關鍵字 (S_keyword) - 權重 0.5
    """
    
    # 維度權重
    WEIGHTS = {
        "budget": 1.5,
        "location": 1.2,
        "features": 1.0,
        "landlord": 1.0,
        "type": 0.8,
        "keyword": 0.5
    }
    
    def __init__(self):
        self._personas_cache: list[Persona] = []
    
    def load_active_personas(self) -> list[Persona]:
        """
        載入所有啟用的人物誌
        
        Returns:
            list[Persona]: 啟用的人物誌列表
        """
        self._personas_cache = db_session.query(Persona).filter_by(active=True).all()
        return self._personas_cache
    
    def calculate_budget_score(self, user_budget: Optional[int], persona: Persona) -> float:
        """
        計算預算契合度 (使用高斯衰減函數)
        
        Args:
            user_budget: 使用者預算上限
            persona: 人物誌實例
            
        Returns:
            float: 0-100 分
        """
        if user_budget is None:
            return 0
        
        rent_min, rent_max = persona.get_rent_range()
        
        if rent_min <= user_budget <= rent_max:
            # 完美落在區間內
            return 100
        elif user_budget < rent_min:
            # 預算不足 - 指數衰減
            # 每少 1000 元，分數下降約 13.5%
            diff = rent_min - user_budget
            return 100 * math.exp(-0.002 * diff)
        else:
            # 預算充裕 - 輕微扣分
            return 90
    
    def calculate_location_score(self, user_location: Optional[str], persona: Persona) -> float:
        """
        計算地段便利性 (矩陣匹配)
        
        Args:
            user_location: 使用者地點偏好 (downtown/school/quiet)
            persona: 人物誌實例
            
        Returns:
            float: 0-100 分
        """
        if user_location is None:
            return 50  # 沒有偏好給一半分
        
        preferred_locations = persona.get_preferred_locations()
        
        if user_location in preferred_locations:
            # 完全命中
            return 100
        elif user_location == "downtown" and "school" in preferred_locations:
            # 市區跟學校相容 (埔里市區離暨大不遠)
            return 50
        elif user_location == "school" and "downtown" in preferred_locations:
            return 50
        else:
            return 0
    
    def calculate_features_score(self, user_features: dict, persona: Persona) -> float:
        """
        計算設施需求匹配度 (Jaccard 相似度變體)
        
        Args:
            user_features: 使用者需求的設施 {feature_name: True/False}
            persona: 人物誌實例
            
        Returns:
            float: 0-100 分
        """
        # 取得使用者想要的設施
        wanted_features = [k for k, v in user_features.items() if v is True]
        
        if not wanted_features:
            return 50  # 沒有特別需求給一半分
        
        required = persona.get_required_features()
        bonus = persona.get_bonus_features()
        
        score_sum = 0
        for feature in wanted_features:
            if feature in required:
                score_sum += 30  # 必備設施 +30
            elif feature in bonus:
                score_sum += 15  # 常見設施 +15
            else:
                score_sum -= 10  # 通常沒有 -10
        
        # 正規化到 0-100
        max_possible = len(wanted_features) * 30
        normalized = (score_sum / max_possible) * 100 if max_possible > 0 else 0
        
        # 限制在 0-100 範圍
        return max(0, min(100, normalized))
    
    def calculate_landlord_score(self, user_management_pref: Optional[str], persona: Persona) -> float:
        """
        計算房東與管理模式匹配度 (互斥邏輯)
        
        Args:
            user_management_pref: 使用者管理偏好 (owner/pro/none/no_owner)
            persona: 人物誌實例
            
        Returns:
            float: -100 到 100 分 (可能有致命衝突)
        """
        if user_management_pref is None or user_management_pref == "none":
            return 50  # 沒有偏好
        
        persona_management = persona.algo_config.get("management_pref", "none")
        
        # 致命衝突：使用者排斥房東同住，但人物誌是房東同住型
        if user_management_pref == "no_owner" and persona_management == "owner":
            return -100
        
        # 完全匹配
        if user_management_pref == persona_management:
            return 100
        
        return 0
    
    def calculate_type_score(self, user_type_pref: Optional[str], persona: Persona) -> float:
        """
        計算房型偏好匹配度
        
        Args:
            user_type_pref: 使用者房型偏好 (套房/雅房/整層)
            persona: 人物誌實例
            
        Returns:
            float: 0-100 分
        """
        if user_type_pref is None:
            return 50
        
        persona_type = persona.algo_config.get("room_type", "")
        
        # 映射對照
        type_mapping = {
            "套房": "studio",
            "雅房": "shared",
            "整層": "apartment"
        }
        
        normalized_user = type_mapping.get(user_type_pref, user_type_pref)
        
        if normalized_user == persona_type:
            return 100
        
        return 0
    
    def calculate_keyword_score(self, raw_text: str, persona: Persona) -> float:
        """
        計算關鍵字加權分數
        
        Args:
            raw_text: 使用者對話原文
            persona: 人物誌實例
            
        Returns:
            float: 0-20 分 (上限 20)
        """
        if not raw_text:
            return 0
        
        matches = persona.matches_keyword(raw_text)
        
        # 每個關鍵字 +5 分，上限 20 分
        return min(20, matches * 5)
    
    def calculate_persona_score(self, user_data: dict, persona: Persona, raw_text: str = "") -> float:
        """
        計算單一人物誌的總分
        
        Args:
            user_data: 使用者收集的資料
            persona: 人物誌實例
            raw_text: 使用者對話原文 (用於關鍵字匹配)
            
        Returns:
            float: 加權總分
        """
        # 取得各維度分數
        s_budget = self.calculate_budget_score(
            user_data.get("budget"), persona
        )
        s_location = self.calculate_location_score(
            user_data.get("location_pref"), persona
        )
        s_features = self.calculate_features_score(
            {k: v for k, v in user_data.items() if isinstance(v, bool)}, persona
        )
        s_landlord = self.calculate_landlord_score(
            user_data.get("management_pref"), persona
        )
        s_type = self.calculate_type_score(
            user_data.get("type_pref"), persona
        )
        s_keyword = self.calculate_keyword_score(raw_text, persona)
        
        # 加權計算
        total = (
            s_budget * self.WEIGHTS["budget"] +
            s_location * self.WEIGHTS["location"] +
            s_features * self.WEIGHTS["features"] +
            s_landlord * self.WEIGHTS["landlord"] +
            s_type * self.WEIGHTS["type"] +
            s_keyword * self.WEIGHTS["keyword"]
        )
        
        return total
    
    def match(self, user_data: dict, raw_text: str = "") -> list[dict]:
        """
        計算所有人物誌分數並排序
        
        Args:
            user_data: 使用者收集的資料
            raw_text: 使用者對話原文
            
        Returns:
            list[dict]: 排序後的結果列表
                [{"persona": Persona, "score": float, "rank": int}, ...]
        """
        personas = self.load_active_personas()
        
        results = []
        for persona in personas:
            score = self.calculate_persona_score(user_data, persona, raw_text)
            results.append({
                "persona": persona,
                "score": round(score, 2)
            })
        
        # 排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # 加入排名
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        return results
    
    def get_best_match(self, user_data: dict, raw_text: str = "") -> Optional[dict]:
        """
        取得最佳匹配結果
        
        Args:
            user_data: 使用者收集的資料
            raw_text: 使用者對話原文
            
        Returns:
            dict: 最佳匹配 {"persona": Persona, "score": float} 或 None
        """
        results = self.match(user_data, raw_text)
        return results[0] if results else None
    
    def get_recommended_houses(self, persona_id: str, limit: int = 5, offset: int = 0) -> list[House]:
        """
        取得該人物誌的推薦房源
        
        Args:
            persona_id: 人物誌 ID
            limit: 數量限制
            offset: 偏移量 (用於分頁)
            
        Returns:
            list[House]: 房源列表
        """
        return db_session.query(House).filter(
            House.category_tag == persona_id,
            House.is_active == True
        ).order_by(
            House.avg_rating.desc()
        ).offset(offset).limit(limit).all()
