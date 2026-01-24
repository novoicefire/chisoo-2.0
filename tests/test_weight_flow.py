
import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.weight_service import WeightService
from app.services.matching_service import MatchingService
from app.models.persona import Persona

class TestWeightFlow(unittest.TestCase):
    
    def test_weight_calculation(self):
        """測試權重計算邏輯"""
        print("\n=== Testing Weight Calculation ===")
        
        # 模擬一個超級在意「預算」且不在意「地點」的使用者
        # Q1 (Loc vs Rent): 選 B (租金便宜) -> Budget +20, Loc -10
        # Q3 (Landlord vs Budget): 選 A (省錢) -> Budget +20, Landlord -10
        # Q6 (Keyword vs General): 選 B (平衡) -> Budget +5, Loc +5
        
        answers = {
            "1": "B", # Budget++
            "2": "A", # Type++ (Random)
            "3": "A", # Budget++
            "4": "B", # Location++ (Random)
            "5": "B", # Landlord++ (Random)
            "6": "B"  # Balanced
        }
        
        weights = WeightService.calculate_weights(answers)
        print(f"Calculated Weights: {weights}")
        
        # 驗證 Budget 權重應該最高
        self.assertTrue(weights["budget"] > 50, "Budget weight should be increased")
        self.assertTrue(weights["budget"] > weights["features"], "Budget should be higher than features")
        
        # 驗證 Summary
        summary = WeightService.generate_summary_text(weights)
        print(f"Summary: {summary}")
        self.assertIn("預算", summary)

    def test_matching_with_weights(self):
        """測試帶入權重的匹配結果"""
        print("\n=== Testing Matching with Weights ===")
        
        matching_service = MatchingService()
        
        # 建立兩個 Persona Mock
        # P1: 便宜但地點差 (Budget Score High, Location Score Low)
        # P2: 貴但地點好 (Budget Score Low, Location Score High)
        
        p1 = MagicMock(spec=Persona)
        p1.name = "Budget_King"
        p1.persona_id = "p1"
        p1.get_rent_range.return_value = (3000, 5000)
        p1.get_preferred_locations.return_value = ["quiet"]
        p1.algo_config = {"management_pref": "none", "room_type": "studio"}
        p1.matches_keyword.return_value = 0
        p1.get_required_features.return_value = []
        p1.get_bonus_features.return_value = []
        
        p2 = MagicMock(spec=Persona)
        p2.name = "Location_King"
        p2.persona_id = "p2"
        p2.get_rent_range.return_value = (8000, 12000)
        p2.get_preferred_locations.return_value = ["downtown"]
        p2.algo_config = {"management_pref": "none", "room_type": "studio"}
        p2.matches_keyword.return_value = 0
        p2.get_required_features.return_value = []
        p2.get_bonus_features.return_value = []
        
        # Mock load_active_personas
        matching_service.load_active_personas = MagicMock(return_value=[p1, p2])
        matching_service.batch_prepare_features_match = MagicMock()
        
        # 使用者資料：預算 4000 (P1 完美, P2 太貴), 地點 downtown (P1 不符, P2 完美)
        user_data = {
            "budget": 4000,
            "location_pref": "downtown",
            "required_features": []
        }
        
        # --- Case A: Default Weights (Budget 1.5, Location 1.2) ---
        # Budget is slightly more important, so P1 might win or be close
        print("--- Default Weights ---")
        results_default = matching_service.match(user_data)
        score_p1_def = next(r["score"] for r in results_default if r["persona"].name == "Budget_King")
        score_p2_def = next(r["score"] for r in results_default if r["persona"].name == "Location_King")
        print(f"P1 (Budget): {score_p1_def}, P2 (Location): {score_p2_def}")
        
        # --- Case B: Custom Weights (Emphasis on Location) ---
        # 如果使用者超在意地點 (Location 100, Budget 10)
        custom_weights = {
            "budget": 10,
            "location": 100, # Normalized -> 2.0
            "features": 50,
            "landlord": 50,
            "type": 50,
            "keyword": 50
        }
        print("--- Custom Weights (Location Focused) ---")
        results_custom = matching_service.match(user_data, weights=custom_weights)
        score_p1_cus = next(r["score"] for r in results_custom if r["persona"].name == "Budget_King")
        score_p2_cus = next(r["score"] for r in results_custom if r["persona"].name == "Location_King")
        print(f"P1 (Budget): {score_p1_cus}, P2 (Location): {score_p2_cus}")
        
        # 驗證：在意地點時，P2 的分數應該大幅提升 (或 P1 大幅下降)
        # P1 地點不合，Location Score low. Weight 越高，P1 越低 (相對總分)
        # 其實是 P2 Location high * 2.0 -> Score boost
        
        self.assertTrue(score_p2_cus > score_p1_cus, "Location King should win when Location weight is high")

if __name__ == '__main__':
    unittest.main()
