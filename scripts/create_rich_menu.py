# ============================================================
# scripts/create_rich_menu.py - Rich Menu 部署腳本
# 專案：Chi Soo 租屋小幫手
# 使用方式：python scripts/create_rich_menu.py
# ============================================================

import sys
import os
import json
import requests

# 將專案根目錄加入 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import config

# LINE API 設定
LINE_API_BASE = "https://api.line.me/v2/bot"
LINE_DATA_API_BASE = "https://api-data.line.me/v2/bot"  # 圖片上傳用的 Data API
HEADERS = {
    "Authorization": f"Bearer {config.LINE_CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Rich Menu 配置 (1200x810 px, 6 格)
RICH_MENU_CONFIG = {
    "size": {
        "width": 1200,
        "height": 810
    },
    "selected": True,
    "name": "Chi Soo Main Menu",
    "chatBarText": "點我開啟選單",
    "areas": [
        # 左上：幫我找窩
        {
            "bounds": {"x": 0, "y": 0, "width": 400, "height": 405},
            "action": {"type": "postback", "data": "action=start_test"}
        },
        # 中上：評價排行榜
        {
            "bounds": {"x": 400, "y": 0, "width": 400, "height": 405},
            "action": {"type": "postback", "data": "action=show_ranking"}
        },
        # 右上：租屋小Tips
        {
            "bounds": {"x": 800, "y": 0, "width": 400, "height": 405},
            "action": {"type": "postback", "data": "action=show_tips"}
        },
        # 左下：我的收藏
        {
            "bounds": {"x": 0, "y": 405, "width": 400, "height": 405},
            "action": {"type": "postback", "data": "action=show_fav"}
        },
        # 中下：評價系統 (暫時停用 - 重新設計中)
        {
            "bounds": {"x": 400, "y": 405, "width": 400, "height": 405},
            "action": {"type": "postback", "data": "action=coming_soon&feature=review"}
        },
        # 右下：地圖式搜尋 (暫時停用 - 重新設計中)
        {
            "bounds": {"x": 800, "y": 405, "width": 400, "height": 405},
            "action": {"type": "postback", "data": "action=coming_soon&feature=map"}
        }
    ]
}


def delete_all_rich_menus():
    """刪除所有現有的 Rich Menu"""
    print("🗑️  檢查現有 Rich Menu...")
    
    response = requests.get(
        f"{LINE_API_BASE}/richmenu/list",
        headers={"Authorization": f"Bearer {config.LINE_CHANNEL_ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        menus = response.json().get("richmenus", [])
        for menu in menus:
            menu_id = menu["richMenuId"]
            print(f"   刪除: {menu_id}")
            requests.delete(
                f"{LINE_API_BASE}/richmenu/{menu_id}",
                headers={"Authorization": f"Bearer {config.LINE_CHANNEL_ACCESS_TOKEN}"}
            )
        print(f"   已刪除 {len(menus)} 個舊選單")
    else:
        print(f"   ⚠️ 無法取得選單列表: {response.text}")


def create_rich_menu():
    """建立 Rich Menu"""
    print("\n📋 建立新 Rich Menu...")
    
    response = requests.post(
        f"{LINE_API_BASE}/richmenu",
        headers=HEADERS,
        json=RICH_MENU_CONFIG
    )
    
    if response.status_code == 200:
        rich_menu_id = response.json()["richMenuId"]
        print(f"   ✅ 建立成功: {rich_menu_id}")
        return rich_menu_id
    else:
        print(f"   ❌ 建立失敗: {response.text}")
        return None


def upload_image(rich_menu_id: str, image_path: str):
    """上傳 Rich Menu 圖片"""
    print(f"\n🖼️  上傳圖片: {image_path}")
    
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{LINE_DATA_API_BASE}/richmenu/{rich_menu_id}/content",
            headers={
                "Authorization": f"Bearer {config.LINE_CHANNEL_ACCESS_TOKEN}",
                "Content-Type": "image/jpeg"
            },
            data=f.read()
        )
    
    if response.status_code == 200:
        print("   ✅ 圖片上傳成功")
        return True
    else:
        print(f"   ❌ 圖片上傳失敗 (HTTP {response.status_code})")
        print(f"   回應: {response.text or '(空)'}")
        return False


def set_default_rich_menu(rich_menu_id: str):
    """設定為預設 Rich Menu"""
    print(f"\n⭐ 設定為預設選單...")
    
    response = requests.post(
        f"{LINE_API_BASE}/user/all/richmenu/{rich_menu_id}",
        headers={"Authorization": f"Bearer {config.LINE_CHANNEL_ACCESS_TOKEN}"}
    )
    
    if response.status_code == 200:
        print("   ✅ 已設定為預設選單")
        return True
    else:
        print(f"   ❌ 設定失敗: {response.text}")
        return False


def main():
    """主程式"""
    print("=" * 50)
    print("Chi Soo 租屋小幫手 - Rich Menu 部署")
    print("=" * 50)
    
    # 檢查圖片檔案
    image_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "rich_menu.jpg"
    )
    
    if not os.path.exists(image_path):
        print(f"❌ 找不到圖片: {image_path}")
        return
    
    # 執行部署流程
    delete_all_rich_menus()
    
    rich_menu_id = create_rich_menu()
    if not rich_menu_id:
        return
    
    if not upload_image(rich_menu_id, image_path):
        return
    
    set_default_rich_menu(rich_menu_id)
    
    print("\n" + "=" * 50)
    print("🎉 Rich Menu 部署完成！")
    print("   請重新開啟 LINE 聊天室查看新選單")
    print("=" * 50)


if __name__ == "__main__":
    main()
