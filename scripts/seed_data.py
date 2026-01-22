# ============================================================
# scripts/seed_data.py - 種子資料初始化腳本
# 專案：Chi Soo 租屋小幫手
# 說明：初始化 5 種 Persona 類型與範例房源資料
# 使用方式：python scripts/seed_data.py
# ============================================================

import sys
import os

# 將專案根目錄加入 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import db_session, Base, engine
from app.models.persona import Persona
from app.models.house import House


def seed_personas():
    """初始化 5 種租屋人物誌類型"""
    
    personas_data = [
        {
            "persona_id": "type_A",
            "name": "省錢戰士型",
            "description": (
                "你是精打細算的省錢高手！對你來說，租金是最重要的考量。"
                "你能接受較簡樸的居住環境，只要乾淨、安全就好。"
                "雅房或分租套房是你的首選，能省則省才是王道！"
            ),
            "keywords": ["便宜", "省錢", "雅房", "睡覺就好", "最低", "預算有限", "經濟", "CP值"],
            "algo_config": {
                "rent_min": 2000,
                "rent_max": 3500,
                "preferred_locations": ["quiet", "school"],
                "required": [],
                "bonus": ["wifi"],
                "noise_tolerance": "high",
                "room_type": "shared",
                "weights": {"price": 0.8, "location": 0.1, "features": 0.1}
            },
            "active": True
        },
        {
            "persona_id": "type_B",
            "name": "懶人貴族型",
            "description": (
                "生活品質是你最在意的事！你願意多花一點錢，換取更便利的生活。"
                "子母車收垃圾、電梯大樓、近市區...這些對你來說都是必備條件。"
                "畢竟時間就是金錢，你值得更好的生活！"
            ),
            "keywords": ["子母車", "電梯", "近市區", "方便", "不用追垃圾車", "便利", "不想麻煩"],
            "algo_config": {
                "rent_min": 5500,
                "rent_max": 8000,
                "preferred_locations": ["downtown"],
                "required": ["garbage", "elevator"],
                "bonus": ["parking", "laundry"],
                "noise_tolerance": "medium",
                "room_type": "studio",
                "weights": {"price": 0.3, "location": 0.3, "features": 0.4}
            },
            "active": True
        },
        {
            "persona_id": "type_C",
            "name": "安全堡壘型",
            "description": (
                "安全感是你選擇住所的第一考量！門禁系統、監視器、房東同住..."
                "這些讓你感到安心的設施缺一不可。你可能偏好限男/限女的房源，"
                "畢竟住得安心才能專心念書！"
            ),
            "keywords": ["門禁", "監視器", "限女", "限男", "安全", "房東同住", "管理員"],
            "algo_config": {
                "rent_min": 4000,
                "rent_max": 6500,
                "preferred_locations": ["downtown", "school"],
                "required": ["security"],
                "bonus": ["landlord_live_in", "cctv"],
                "noise_tolerance": "low",
                "room_type": "studio",
                "management_pref": "owner",
                "weights": {"price": 0.2, "location": 0.2, "features": 0.3, "security": 0.3}
            },
            "active": True
        },
        {
            "persona_id": "type_D",
            "name": "社交群居型",
            "description": (
                "你喜歡有室友的生活！一起看電影、一起煮飯、偶爾開個小派對..."
                "對你來說，租房不只是找個地方住，更是找一群志同道合的夥伴。"
                "整層公寓或有客廳的分租房是你的最愛！"
            ),
            "keywords": ["客廳", "整層", "可開伙", "室友", "分租", "一起住", "廚房"],
            "algo_config": {
                "rent_min": 4000,
                "rent_max": 7000,
                "preferred_locations": ["downtown", "school"],
                "required": ["living_room"],
                "bonus": ["kitchen", "balcony"],
                "noise_tolerance": "high",
                "room_type": "apartment",
                "weights": {"price": 0.3, "location": 0.2, "features": 0.5}
            },
            "active": True
        },
        {
            "persona_id": "type_E",
            "name": "質感獨享型",
            "description": (
                "你追求的是生活品味！新裝潢、採光好、有陽台可以曬衣服..."
                "這些細節對你來說都很重要。你喜歡獨立的空間，"
                "一個人靜靜享受獨處的時光，是你充電的方式。"
            ),
            "keywords": ["裝潢", "新屋", "獨洗獨曬", "陽台", "採光", "質感", "乾淨"],
            "algo_config": {
                "rent_min": 6000,
                "rent_max": 10000,
                "preferred_locations": ["downtown", "quiet"],
                "required": ["balcony", "laundry"],
                "bonus": ["parking", "new_renovation"],
                "house_age_max": 5,
                "noise_tolerance": "low",
                "room_type": "studio",
                "weights": {"price": 0.2, "location": 0.2, "features": 0.6}
            },
            "active": True
        }
    ]
    
    print("🌱 開始初始化 Personas...")
    
    for data in personas_data:
        existing = db_session.query(Persona).filter_by(persona_id=data["persona_id"]).first()
        if existing:
            print(f"  ⏭️  {data['name']} 已存在，跳過")
            continue
        
        persona = Persona(**data)
        db_session.add(persona)
        print(f"  ✅ 新增 {data['name']}")
    
    db_session.commit()
    print("✨ Personas 初始化完成！\n")


def seed_sample_houses():
    """初始化範例房源資料"""
    
    houses_data = [
        {
            "name": "【山水桃米】",
            "address": "南投縣埔里鎮桃米里種瓜路1-1號",
            "category_tag": "type_E",
            "rent": 5000,
            "room_type": "獨立套房",
            "features": {"wifi": True, "ac": False, "laundry": False, "fridge": True}, # 根據描述: 網路免費, 沒寫冷氣但通常有? 圖片有冷氣
            "description": "與大自然共舞，環境清幽。透天、獨立電表、水泥隔間。(第四臺+網路費+水費)全免，無菸租屋。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2338x1.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2338x1.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2338x2.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2338x3.jpg"
            ],
            "latitude": 23.941075941054237,
            "longitude": 120.92406204456546,
        },
        {
            "name": "近市區水裡巷雅房",
            "address": "南投縣埔里鎮大城里水裡巷2號",
            "category_tag": "type_A",
            "rent": 2300,
            "room_type": "雅房",
            "features": {"wifi": False, "ac": False},
            "description": "近市區、全聯、星巴克、85度C、拉麵店...生活機能強。透天、獨立電表。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2380x1_20210407-150629.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2380x1_20210407-150629.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2380x2_20210407-150538.jpg"
            ],
            "latitude": 23.968686670756966,
            "longitude": 120.95654652641345
        },
        {
            "name": "桃米社區近派出所套房",
            "address": "南投縣埔里鎮桃米里桃米巷36號及36-1號",
            "category_tag": "type_A",
            "rent": 3500,
            "room_type": "獨立套房",
            "features": {"wifi": True},
            "description": "離校近，環境單純。透天、獨立電表、水泥隔間。電費一度4元。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2307x1.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2307x1.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2307x2.jpg"
            ],
            "latitude": 23.942951843267412,
            "longitude": 120.93095348131277
        },
        {
            "name": "南安路清新套房",
            "address": "南投縣埔里鎮清新里南安路231號",
            "category_tag": "type_C",
            "rent": 5000,
            "room_type": "獨立套房",
            "features": {"wifi": True, "security": True, "cctv": True, "parking": True, "ac": True},
            "description": "門禁系統、監視錄影設備、滅火器。無菸租屋。5500元房型附獨立洗衣機。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/14740x1.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/14740x1.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/14740x2.jpg"
            ],
            "latitude": 23.963843419758476,
            "longitude": 120.95908471467365
        },
        {
            "name": "桃米巷35-1號套房",
            "address": "南投縣埔里鎮桃米里桃米巷35-1號",
            "category_tag": "type_A",
            "rent": 3600,
            "room_type": "獨立套房",
            "features": {"wifi": True},
            "description": "環境清幽，皆有對外窗戶，有停車場，鄰近暨南大學機車道。水費及公共用電免費。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2354x1.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2354x1.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2354x2.jpg"
            ],
            "latitude": 23.941813397481255,
            "longitude": 120.93074053456257
        },
        {
            "name": "中新居#50號",
            "address": "南投縣埔里鎮西門里中正二路50號",
            "category_tag": "type_C",
            "rent": 5500,
            "room_type": "獨立套房",
            "features": {"wifi": True, "ac": True, "fridge": True, "laundry": True, "security": True, "cctv": True, "parking": True},
            "description": "設備齊全：電視、冰箱、冷氣、洗衣機、飲水機。有中庭、停車場、門禁系統。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/15055x1.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/15055x1.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/15055x2.jpg"
            ],
            "latitude": 23.96879731526369,
            "longitude": 120.96351076400963
        },
        {
            "name": "中山路女生套房",
            "address": "南投縣埔里鎮大城里中山路三段290號",
            "category_tag": "type_C",
            "rent": 6000,
            "room_type": "獨立套房",
            "features": {"wifi": True, "ac": True, "fridge": True, "laundry": True, "dispenser": True},
            "description": "限女生。生活機能強，採光佳，校車經過。剩3間。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2381x1.jpeg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2381x1.jpeg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2381x2.jpeg"
            ],
            "latitude": 23.968877059902056,
            "longitude": 120.95745839582938
        },
        {
            "name": "中新居_48號",
            "address": "南投縣埔里鎮西門里中正二路48號",
            "category_tag": "type_B",
            "rent": 5000,
            "room_type": "獨立套房",
            "features": {"wifi": True, "ac": True, "fridge": True, "laundry": True, "dispenser": True},
            "description": "近市區，生活便利。設備包含冷氣、冰箱、洗衣機、飲水機。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2369x1_20210218-164549.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2369x1_20210218-164549.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/2369x2.jpeg"
            ],
            "latitude": 23.96876016397592,
            "longitude": 120.96355457952117
        },
        {
            "name": "中正二路便利套房",
            "address": "南投縣埔里鎮西門里中正二路67號",
            "category_tag": "type_B",
            "rent": 4500,
            "room_type": "分租套房",
            "features": {"wifi": True, "ac": True, "fridge": True, "security": True, "living_room": True},
            "description": "鄰近嬌豐、埔里西站、郵局。暨大校車必經之路。有交誼廳、門禁感應。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/7589x1_20241023-171836.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/7589x1_20241023-171836.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/7589x2_20241023-171836.jpg"
            ],
            "latitude": 23.969166638375473,
            "longitude": 120.96374294882801
        },
        {
            "name": "南興街清幽套房",
            "address": "南投縣埔里鎮南興街383號",
            "category_tag": "type_A",
            "rent": 3250,
            "room_type": "獨立套房",
            "features": {"wifi": True, "ac": True, "fridge": True, "laundry": True},
            "description": "暨大接駁車有經過，生活機能佳，環境清幽。",
            "image_url": "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/7583x1.jpg",
            "images": [
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/7583x1.jpg",
                "https://house.nfu.edu.tw/uploads/data/NCNU/images_house/7583x2.jpg"
            ],
            "latitude": 23.965607971017704,
            "longitude": 120.96219107775867
        }
    ]
    
    print("🏠 開始初始化範例房源...")
    
    # 清空現有房源，確保只有真實資料
    try:
        num_deleted = db_session.query(House).delete()
        db_session.commit()
        print(f"  🗑️ 已刪除 {num_deleted} 筆舊房源資料")
    except Exception as e:
        db_session.rollback()
        print(f"  ⚠️ 清除舊資料失敗: {e}")
    
    for data in houses_data:
        existing = db_session.query(House).filter_by(name=data["name"]).first()
        if existing:
            print(f"  ⏭️  {data['name']} 已存在，跳過")
            continue
        
        house = House(**data)
        db_session.add(house)
        print(f"  ✅ 新增 {data['name']}")
    
    db_session.commit()
    print("✨ 範例房源初始化完成！\n")


def main():
    """執行所有種子資料初始化"""
    print("=" * 50)
    print("Chi Soo 租屋小幫手 - 種子資料初始化")
    print("=" * 50)
    print()
    
    # 建立所有表格
    print("📦 建立資料庫表格...")
    Base.metadata.create_all(bind=engine)
    print("✅ 資料庫表格建立完成\n")
    
    # 初始化種子資料
    seed_personas()
    seed_sample_houses()
    
    print("=" * 50)
    print("🎉 所有種子資料初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
