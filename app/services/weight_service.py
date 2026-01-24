# ============================================================
# services/weight_service.py - 權重強制選擇服務
# 專案：Chi Soo 租屋小幫手
# 說明：處理 6 組二選一情境，計算使用者權重並產生雷達圖
# ============================================================

import urllib.parse

class WeightService:
    """
    權重強制選擇服務
    
    負責管理 6 個二選一情境，並根據使用者的選擇計算
    Budget, Location, Features, Landlord, Type, Keyword 六個維度的權重。
    """
    
    # 權重維度
    DIMENSIONS = ["budget", "location", "features", "landlord", "type", "keyword"]
    
    # 預設權重 (總和 300%)
    DEFAULT_WEIGHTS = {
        "budget": 50,
        "location": 50,
        "features": 50,
        "landlord": 50,
        "type": 50,
        "keyword": 50
    }
    
    # 題目定義（價值觀權重測驗）
    # 設計原則：
    # 1. 只問「你更在乎什麼」，不涉及具體選項（如套房/雅房）
    # 2. 每個維度至少出現 2 次
    # 3. impact 數值控制在 ±20 以內保持平衡
    SCENARIOS = [
        {
            "id": 1,
            "title": "📍 距離 vs 💰 租金",
            "question": "如果要二選一，你會選？",
            "options": [
                {
                    "label": "A. 走路就能到學校，但每月多付 $2000",
                    "value": "A",
                    "impact": {"location": 20, "budget": -10}
                },
                {
                    "label": "B. 通勤要花 20 分鐘，但租金省超多",
                    "value": "B",
                    "impact": {"budget": 20, "location": -10}
                }
            ]
        },
        {
            "id": 2,
            "title": "🔒 隱私 vs 🛁 硬體設施",
            "question": "同樣的租金，你比較想要？",
            "options": [
                {
                    "label": "A. 自己一個人的獨立空間，但什麼設備都沒有",
                    "value": "A",
                    "impact": {"type": 20, "features": -10}
                },
                {
                    "label": "B. 要跟別人共用空間，但設備超級豪華",
                    "value": "B",
                    "impact": {"features": 20, "type": -10}
                }
            ]
        },
        {
            "id": 3,
            "title": "👴 自由度 vs 💰 省錢",
            "question": "為了每月省 $1000，你願意...？",
            "options": [
                {
                    "label": "A. 願意！跟房東住一起也沒關係，省錢最重要",
                    "value": "A",
                    "impact": {"budget": 20, "landlord": -10}
                },
                {
                    "label": "B. 不願意！我寧願多花錢也要有自己的自由",
                    "value": "B",
                    "impact": {"landlord": 20, "budget": -10}
                }
            ]
        },
        {
            "id": 4,
            "title": "📍 生活機能 vs 🔒 居住品質",
            "question": "這兩種生活，你更嚮往哪一種？",
            "options": [
                {
                    "label": "A. 住得遠一點，但房間大又舒適",
                    "value": "A",
                    "impact": {"type": 20, "location": -10}
                },
                {
                    "label": "B. 住得近、生活方便，房間小一點沒關係",
                    "value": "B",
                    "impact": {"location": 20, "type": -10}
                }
            ]
        },
        {
            "id": 5,
            "title": "🛁 硬體設施 vs 👴 房東好壞",
            "question": "這兩個房東，你會選誰的房子？",
            "options": [
                {
                    "label": "A. 房東超難相處，但房間設備全新又齊全",
                    "value": "A",
                    "impact": {"features": 20, "landlord": -10}
                },
                {
                    "label": "B. 房東人超好超照顧，但設備比較舊",
                    "value": "B",
                    "impact": {"landlord": 20, "features": -10}
                }
            ]
        },
        {
            "id": 6,
            "title": "🔑 特殊需求 vs ⚖️ 整體條件",
            "question": "最後一題！這是你的靈魂拷問...",
            "options": [
                {
                    "label": "A. 這間能滿足我的特殊需求 (如：養寵物、開伙)，但其他條件普普",
                    "value": "A",
                    "impact": {"keyword": 25, "budget": -5, "features": -5}
                },
                {
                    "label": "B. 沒有特殊功能，但整體條件平均都很好",
                    "value": "B",
                    "impact": {"budget": 10, "location": 10, "features": 10, "keyword": -15}
                }
            ]
        }
    ]


    @staticmethod
    def get_question(index: int) -> dict:
        """取得第 index 題的內容 (index 從 1 開始)"""
        if 1 <= index <= len(WeightService.SCENARIOS):
            return WeightService.SCENARIOS[index - 1]
        return None

    @staticmethod
    def calculate_weights(answers: dict) -> dict:
        """
        根據使用者答案計算最終權重
        answers: { "1": "A", "2": "B", ... }
        """
        final_weights = WeightService.DEFAULT_WEIGHTS.copy()
        
        for q_index_str, choice in answers.items():
            try:
                q_index = int(q_index_str)
                scenario = WeightService.get_question(q_index)
                if not scenario:
                    continue
                
                # 找出選中的選項
                selected_option = next((opt for opt in scenario["options"] if opt["value"] == choice), None)
                if selected_option:
                    impact = selected_option["impact"]
                    for dim, score in impact.items():
                        if dim in final_weights:
                            final_weights[dim] += score
                            
            except ValueError:
                continue
                
        # 確保權重不為負數，且進行簡單的正規化 (讓總分維持在 300 左右，方便顯示)
        # 這裡不強求精確 300，只要相對比例對即可
        for k, v in final_weights.items():
            final_weights[k] = max(10, v) # 最低 10 分
            
        return final_weights

    @staticmethod
    def generate_radar_chart_url(weights: dict) -> str:
        """產生 QuickChart 雷達圖 URL"""
        
        # 準備數據 (順序：Budget, Location, Features, Landlord, Type, Keyword)
        labels = ["預算", "地段", "設施", "房東", "房型", "關鍵字"]
        data = [
            weights.get("budget", 50),
            weights.get("location", 50),
            weights.get("features", 50),
            weights.get("landlord", 50),
            weights.get("type", 50),
            weights.get("keyword", 50)
        ]
        
        # QuickChart Config
        chart_config = {
            "type": "radar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "你的租屋價值觀",
                    "data": data,
                    "backgroundColor": "rgba(99, 102, 241, 0.5)", # Indigo-500
                    "borderColor": "rgb(99, 102, 241)",
                    "pointBackgroundColor": "rgb(99, 102, 241)",
                    "borderWidth": 2
                }]
            },
            "options": {
                "scale": {
                    "ticks": {
                        "beginAtZero": True,
                        "max": 100,
                        "min": 0,
                        "stepSize": 20,
                        "display": False # 隱藏刻度數字，保持簡潔
                    },
                    "pointLabels": {
                        "fontSize": 14,
                        "fontStyle": "bold",
                        "fontColor": "#333"
                    }
                },
                "legend": {
                    "display": False
                }
            }
        }
        
        # URL Encoding
        # QuickChart API: https://quickchart.io/chart?c={config}
        import json
        config_str = json.dumps(chart_config)
        encoded_config = urllib.parse.quote(config_str)
        
        return f"https://quickchart.io/chart?c={encoded_config}&w=500&h=500"

    @staticmethod
    def generate_summary_text(weights: dict) -> str:
        """根據權重產生總結文案（不含分類標籤，僅描述偏好分佈）"""
        # 找出最高分的 2 個維度
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top1 = sorted_weights[0]
        top2 = sorted_weights[1]
        
        dim_names = {
            "budget": "預算考量",
            "location": "地段便利性",
            "features": "硬體設施",
            "landlord": "房東相處",
            "type": "房型隱私",
            "keyword": "特殊需求"
        }
        
        t1_name = dim_names.get(top1[0], top1[0])
        t2_name = dim_names.get(top2[0], top2[0])
        
        return (
            f"了解了！從你的選擇來看，「{t1_name}」與「{t2_name}」是你最看重的兩個面向 ✨\n\n"
            f"接下來進入 Step 2，我會問幾個具體的條件問題，完成後就能為你診斷專屬的租屋人格囉！"
        )
