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
        # 真實埔里租屋資料 (座標來自 Google Maps)
        {
            "name": "桃米生態村雅房",
            "address": "南投縣埔里鎮桃米巷68號",
            "category_tag": "type_A",
            "rent": 3500,
            "room_type": "雅房",
            "features": {"wifi": True, "ac": True},
            "description": "鄰近暨大桃米校門，騎車5分鐘到校。環境清幽，適合喜歡安靜的同學。",
            "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80"
            ],
            "latitude": 23.9512,
            "longitude": 120.9358
        },
        {
            "name": "大成街電梯套房",
            "address": "南投縣埔里鎮大成街15號",
            "category_tag": "type_B",
            "rent": 6000,
            "room_type": "套房",
            "features": {"garbage": True, "elevator": True, "ac": True, "wifi": True, "laundry": True},
            "description": "子母車收垃圾免追垃圾車！電梯大樓，近全聯、寶雅，生活機能超讚。",
            "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80",
                "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80"
            ],
            "latitude": 23.9652,
            "longitude": 120.9634
        },
        {
            "name": "中山路三段學生套房",
            "address": "南投縣埔里鎮中山路三段118號",
            "category_tag": "type_C",
            "rent": 5500,
            "room_type": "套房",
            "features": {"security": True, "cctv": True, "ac": True, "wifi": True},
            "description": "門禁管理、24小時監視器，房東阿姨人很好。近埔里酒廠、7-11。",
            "image_url": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=600&q=80"
            ],
            "latitude": 23.9680,
            "longitude": 120.9610
        },
        {
            "name": "信義路整層三房",
            "address": "南投縣埔里鎮信義路201號",
            "category_tag": "type_D",
            "rent": 15000,
            "room_type": "整層",
            "features": {"living_room": True, "kitchen": True, "balcony": True, "parking": True},
            "description": "適合3-4人分租！有大客廳、廚房可開伙，還有專屬車位。",
            "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80",
                "https://images.unsplash.com/photo-1560185007-c5ca9d2c014d?w=600&q=80"
            ],
            "latitude": 23.9589,
            "longitude": 120.9701
        },
        {
            "name": "北環路質感新套房",
            "address": "南投縣埔里鎮北環路58號",
            "category_tag": "type_E",
            "rent": 7500,
            "room_type": "套房",
            "features": {"balcony": True, "laundry": True, "new_renovation": True, "ac": True, "wifi": True},
            "description": "2024年新裝潢，獨立陽台可曬衣，採光超好！近愛蘭橋。",
            "image_url": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80"
            ],
            "latitude": 23.9720,
            "longitude": 120.9550
        },
        {
            "name": "西安路女生宿舍",
            "address": "南投縣埔里鎮西安路一段88號",
            "category_tag": "type_C",
            "rent": 4800,
            "room_type": "套房",
            "features": {"security": True, "cctv": True, "landlord_live_in": True, "ac": True},
            "description": "限女！房東阿姨同住超安心，門禁晚上11點。適合注重安全的女同學。",
            "image_url": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=600&q=80"
            ],
            "latitude": 23.9612,
            "longitude": 120.9645
        },
        {
            "name": "隆生路平價雅房",
            "address": "南投縣埔里鎮隆生路55號",
            "category_tag": "type_A",
            "rent": 2800,
            "room_type": "雅房",
            "features": {"wifi": True},
            "description": "超省錢選擇！共用衛浴，但空間乾淨。騎車到暨大約15分鐘。",
            "image_url": "https://images.unsplash.com/photo-1502672023488-70e25813eb80?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1502672023488-70e25813eb80?w=600&q=80"
            ],
            "latitude": 23.9610,
            "longitude": 120.9680
        },
        {
            "name": "中正路商圈套房",
            "address": "南投縣埔里鎮中正路320號",
            "category_tag": "type_B",
            "rent": 6800,
            "room_type": "套房",
            "features": {"garbage": True, "elevator": True, "ac": True, "wifi": True, "parking": True},
            "description": "位於埔里最熱鬧的中正路！樓下就是小吃街，機車有停車位。",
            "image_url": "https://images.unsplash.com/photo-1560185007-c5ca9d2c014d?w=600&q=80",
            "images": [
                "https://images.unsplash.com/photo-1560185007-c5ca9d2c014d?w=600&q=80",
                "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80"
            ],
            "latitude": 23.9634,
            "longitude": 120.9623
        }
    ]
    
    print("🏠 開始初始化範例房源...")
    
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
