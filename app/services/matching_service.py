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
        計算預算契合度 (改良版本)
        
        邏輯：
        - 預算在 persona 的理想範圍內 → 100 分
        - 預算低於 persona 範圍 → 扣分 (這個人可能負擔不起)
        - 預算高於 persona 範圍 → 也扣分 (這個人可能想要更好的)
        
        Args:
            user_budget: 使用者預算上限
            persona: 人物誌實例
            
        Returns:
            float: 0-100 分
        """
        if user_budget is None:
            return 50  # 沒有提供預算給中等分數
        
        rent_min, rent_max = persona.get_rent_range()
        
        # 預算無上限(99999)的情況 - 傾向推薦高端選項
        if user_budget >= 99999:
            # 越高端的 persona (rent_max 越高) 分數越高
            return min(100, rent_max / 100)  # 例如 rent_max=8000 → 80分
        
        if rent_min <= user_budget <= rent_max:
            # 完美落在區間內
            return 100
        elif user_budget < rent_min:
            # 預算不足 - 這個 persona 可能太貴
            diff = rent_min - user_budget
            return max(0, 100 - diff * 0.05)  # 每少 1000 元扣 50 分
        else:
            # 預算充裕 - 這個 persona 可能太便宜給使用者
            diff = user_budget - rent_max
            return max(20, 100 - diff * 0.02)  # 每多 1000 元扣 20 分，最低 20 分
    
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
    
    def calculate_features_score(self, user_data: dict, persona: Persona) -> float:
        """
        計算設施需求匹配度 (使用快取的批次 AI 結果)
        
        Args:
            user_data: 使用者收集的資料 (包含 required_features 陣列)
            persona: 人物誌實例
            
        Returns:
            float: 0-100 分
        """
        wanted_features = user_data.get("required_features", [])
        
        if not wanted_features:
            return 50  # 沒有特別需求給一半分
        
        # 檢查是否有快取的批次匹配結果
        if hasattr(self, '_feature_match_cache') and persona.persona_id in self._feature_match_cache:
            match_result = self._feature_match_cache[persona.persona_id]
            return match_result["match_rate"] * 100
        
        # Fallback: 使用簡單匹配
        from app.services.ollama_service import OllamaService
        ollama = OllamaService()
        required = persona.get_required_features()
        bonus = persona.get_bonus_features()
        match_result = ollama.match_features_semantically(wanted_features, required + bonus)
        
        return max(0, min(100, match_result["match_rate"] * 100))
    
    def batch_prepare_features_match(self, user_data: dict, personas: list[Persona]) -> None:
        """
        批次進行所有 Persona 的設施匹配 (預先計算並快取結果)
        
        Args:
            user_data: 使用者收集的資料
            personas: 所有人物誌列表
        """
        wanted_features = user_data.get("required_features", [])
        
        if not wanted_features:
            self._feature_match_cache = {}
            return
        
        # 收集所有 Persona 的設施
        all_personas_features = {}
        for persona in personas:
            required = persona.get_required_features()
            bonus = persona.get_bonus_features()
            all_personas_features[persona.persona_id] = required + bonus
        
        # 一次性 AI 批次匹配
        from app.services.ollama_service import OllamaService
        ollama = OllamaService()
        
        self._feature_match_cache = ollama.batch_match_features(wanted_features, all_personas_features)
    
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
    
    def calculate_persona_score(self, user_data: dict, persona: Persona, raw_text: str = "", weights: dict = None) -> float:
        """
        計算單一人物誌的總分
        
        Args:
            user_data: 使用者收集的資料
            persona: 人物誌實例
            raw_text: 使用者對話原文 (用於關鍵字匹配)
            weights: 使用者自訂權重 (若無則使用預設)
            
        Returns:
            float: 加權總分
        """
        # 決定使用的權重
        if weights:
            # 正規化權重 (除以 50 讓數值接近預設的 1.0~1.5)
            # 例如 70 分 -> 1.4
            use_weights = {k: v / 50.0 for k, v in weights.items()}
        else:
            use_weights = self.WEIGHTS

        # 取得各維度分數
        s_budget = self.calculate_budget_score(
            user_data.get("budget"), persona
        )
        s_location = self.calculate_location_score(
            user_data.get("location_pref"), persona
        )
        s_features = self.calculate_features_score(
            user_data, persona
        )
        s_landlord = self.calculate_landlord_score(
            user_data.get("management_pref"), persona
        )
        s_type = self.calculate_type_score(
            user_data.get("type_pref"), persona
        )
        s_keyword = self.calculate_keyword_score(raw_text, persona)
        
        # 加權計算 (防呆：若 key 不存在則用 1.0)
        total = (
            s_budget * use_weights.get("budget", 1.0) +
            s_location * use_weights.get("location", 1.0) +
            s_features * use_weights.get("features", 1.0) +
            s_landlord * use_weights.get("landlord", 1.0) +
            s_type * use_weights.get("type", 1.0) +
            s_keyword * use_weights.get("keyword", 0.5)
        )
        
        return total
    
    def match(self, user_data: dict, raw_text: str = "", weights: dict = None) -> list[dict]:
        """
        計算所有人物誌分數並排序
        
        Args:
            user_data: 使用者收集的資料
            raw_text: 使用者對話原文
            weights: 使用者自訂權重
            
        Returns:
            list[dict]: 排序後的結果列表
                [{"persona": Persona, "score": float, "rank": int}, ...]
        """
        personas = self.load_active_personas()
        
        print(f"🎯 開始匹配，使用者資料: {user_data}")
        if weights:
            print(f"⚖️ 使用自訂權重: {weights}")
        
        # 批次預先計算設施匹配 (單次 AI 呼叫)
        self.batch_prepare_features_match(user_data, personas)
        
        results = []
        for persona in personas:
            score = self.calculate_persona_score(user_data, persona, raw_text, weights)
            results.append({
                "persona": persona,
                "score": round(score, 2)
            })
            print(f"   📊 {persona.name}: {round(score, 2)} 分")
        
        # 排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # 加入排名
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        print(f"🏆 最佳匹配: {results[0]['persona'].name} ({results[0]['score']} 分)")
        
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
    
    def get_recommended_houses_with_scores(
        self, 
        persona_id: str, 
        limit: int = 5, 
        offset: int = 0
    ) -> list[dict]:
        """
        取得該人物誌的推薦房源（含匹配分數）
        
        Args:
            persona_id: 人物誌 ID
            limit: 數量限制
            offset: 偏移量 (用於分頁)
            
        Returns:
            list[dict]: 房源列表，包含 house 物件與 match_score
                [{"house": House, "match_score": 85, "recommendation_reason": "..."}, ...]
        """
        # 取得 Persona 資訊
        persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
        
        # 查詢適合的房源
        houses = db_session.query(House).filter(
            House.is_active == True
        ).order_by(
            House.avg_rating.desc()
        ).offset(offset).limit(limit + 10).all()  # 多取一些用於篩選
        
        if not houses:
            return []
        
        results = []
        for house in houses:
            # 計算匹配分數
            score = self._calculate_house_match_score(house, persona)
            
            # 生成推薦理由
            reason = self._generate_recommendation_reason(house, persona, score)
            
            results.append({
                "house": house,
                "match_score": score,
                "recommendation_reason": reason
            })
        
        # 依匹配分數排序
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        # 取前 limit 個
        return results[:limit]
    
    def _calculate_house_match_score(self, house: House, persona: Optional[Persona]) -> int:
        """
        計算單一房源與 Persona 的匹配分數
        
        Args:
            house: 房源實例
            persona: 人物誌實例
            
        Returns:
            int: 匹配分數 (0-100)
        """
        if not persona:
            # 沒有 Persona，基於房源品質評分
            base_score = 70
            if house.avg_rating >= 4.5:
                base_score += 15
            elif house.avg_rating >= 4.0:
                base_score += 10
            elif house.avg_rating >= 3.5:
                base_score += 5
            return min(100, base_score)
        
        score = 50  # 基礎分
        
        # 1. 類型匹配 (category_tag)
        if house.category_tag == persona.persona_id:
            score += 25
        
        # 2. 租金區間匹配
        rent_min, rent_max = persona.get_rent_range()
        if rent_min <= house.rent <= rent_max:
            score += 15
        elif house.rent < rent_min:
            score += 5  # 比預期便宜也不錯
        
        # 3. 設施匹配
        required_features = persona.get_required_features()
        house_features = house.features or {}
        
        matched_features = 0
        for feature in required_features:
            # 簡單的關鍵字匹配
            feature_lower = feature.lower()
            for house_feat_key, house_feat_val in house_features.items():
                if house_feat_val and feature_lower in house_feat_key.lower():
                    matched_features += 1
                    break
        
        if required_features:
            feature_ratio = matched_features / len(required_features)
            score += int(feature_ratio * 10)
        
        # 4. 評分加成
        if house.avg_rating >= 4.5:
            score += 10
        elif house.avg_rating >= 4.0:
            score += 5
        
        return min(100, max(0, score))
    
    def _generate_recommendation_reason(
        self, 
        house: House, 
        persona: Optional[Persona], 
        score: int
    ) -> str:
        """
        生成推薦理由
        
        Args:
            house: 房源實例
            persona: 人物誌實例
            score: 匹配分數
            
        Returns:
            str: 推薦理由文字
        """
        reasons = []
        
        # 評分相關
        if house.avg_rating >= 4.5:
            reasons.append("⭐ 社群高評價")
        elif house.avg_rating >= 4.0:
            reasons.append("👍 好評推薦")
        
        # 設施相關
        features = house.features or {}
        feature_highlights = []
        
        if features.get("garbage_service"):
            feature_highlights.append("子母車")
        if features.get("elevator"):
            feature_highlights.append("電梯")
        if features.get("security"):
            feature_highlights.append("門禁")
        if features.get("balcony"):
            feature_highlights.append("陽台")
        if features.get("parking"):
            feature_highlights.append("停車位")
        
        if feature_highlights:
            reasons.append(f"🏠 {', '.join(feature_highlights[:3])}")
        
        # Persona 相關
        if persona:
            if house.category_tag == persona.persona_id:
                reasons.append(f"🎯 適合 {persona.name}")
            
            rent_min, rent_max = persona.get_rent_range()
            if rent_min <= house.rent <= rent_max:
                reasons.append("💰 符合預算")
        
        # 匹配度
        if score >= 90:
            reasons.insert(0, "🔥 極度推薦")
        elif score >= 80:
            reasons.insert(0, "✨ 強力推薦")
        
        if not reasons:
            reasons.append("📍 埔里優質房源")
        
        return " | ".join(reasons[:3])
