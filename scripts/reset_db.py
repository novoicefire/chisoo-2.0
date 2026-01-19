# ============================================================
# scripts/reset_db.py - 資料庫重置腳本
# 專案：Chi Soo 租屋小幫手
# 使用方式：python scripts/reset_db.py
# ============================================================

import sys
import os

# 將專案根目錄加入 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import db_session, Base, engine
from app.models.user import User
from app.models.session import UserSession


def reset_user_sessions():
    """只清空所有使用者的測驗進度 (保留使用者資料)"""
    print("🔄 清空所有測驗進度...")
    
    count = db_session.query(UserSession).delete()
    db_session.commit()
    
    print(f"   ✅ 已清空 {count} 筆 Session 資料")


def reset_all_users():
    """清空所有使用者資料 (包含 Session)"""
    print("🔄 清空所有使用者資料...")
    
    session_count = db_session.query(UserSession).delete()
    user_count = db_session.query(User).delete()
    db_session.commit()
    
    print(f"   ✅ 已清空 {session_count} 筆 Session")
    print(f"   ✅ 已清空 {user_count} 筆 User")


def reset_single_user(user_id: str):
    """重置單一使用者的測驗進度"""
    print(f"🔄 重置使用者: {user_id[:20]}...")
    
    session = db_session.query(UserSession).filter_by(user_id=user_id).first()
    if session:
        session.status = "IDLE"
        session.collected_data = {}
        db_session.commit()
        print("   ✅ 已重置")
    else:
        print("   ⚠️ 找不到該使用者")


def drop_and_recreate():
    """刪除並重建所有資料表 (危險操作!)"""
    print("⚠️ 這將刪除所有資料! 按 Enter 確認或 Ctrl+C 取消...")
    input()
    
    print("💥 刪除所有資料表...")
    Base.metadata.drop_all(bind=engine)
    
    print("🔨 重建所有資料表...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ 完成! 請執行 seed_data.py 重新初始化種子資料")


def main():
    print("=" * 50)
    print("Chi Soo 租屋小幫手 - 資料庫重置工具")
    print("=" * 50)
    print()
    print("請選擇操作：")
    print("1. 清空所有測驗進度 (保留使用者)")
    print("2. 清空所有使用者資料")
    print("3. 重置單一使用者")
    print("4. 刪除並重建所有資料表 (危險!)")
    print("0. 取消")
    print()
    
    choice = input("請輸入選項 (0-4): ").strip()
    
    if choice == "1":
        reset_user_sessions()
    elif choice == "2":
        reset_all_users()
    elif choice == "3":
        user_id = input("請輸入 User ID: ").strip()
        reset_single_user(user_id)
    elif choice == "4":
        drop_and_recreate()
    else:
        print("已取消")
    
    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
