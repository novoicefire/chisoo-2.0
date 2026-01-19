# ============================================================
# services/session_service.py - 對話狀態管理服務
# 專案：Chi Soo 租屋小幫手
# 說明：管理使用者對話狀態 (IDLE/TESTING)，實作中斷與恢復機制
# ============================================================

from datetime import datetime
from typing import Optional

from app.models import db_session
from app.models.user import User
from app.models.session import UserSession


class SessionService:
    """
    對話狀態管理服務
    
    負責管理使用者在 IDLE 與 TESTING 模式之間的切換，
    並處理測驗進度的儲存與恢復。
    """
    
    @staticmethod
    def get_or_create_user(user_id: str, display_name: str = None, picture_url: str = None) -> User:
        """
        取得或建立使用者
        
        Args:
            user_id: LINE User ID
            display_name: LINE 暱稱
            picture_url: LINE 頭像網址
            
        Returns:
            User: 使用者實例
        """
        user = db_session.query(User).filter_by(user_id=user_id).first()
        
        if not user:
            user = User(
                user_id=user_id,
                display_name=display_name,
                picture_url=picture_url,
                is_blocked=False
            )
            db_session.add(user)
            db_session.commit()
        else:
            changed = False
            if display_name and user.display_name != display_name:
                user.display_name = display_name
                changed = True
            
            if picture_url and user.picture_url != picture_url:
                user.picture_url = picture_url
                changed = True
            
            # 確保解除封鎖狀態
            if user.is_blocked:
                user.is_blocked = False
                changed = True
            
            if changed:
                db_session.commit()
        
        return user
    
    @staticmethod
    def get_or_create_session(user_id: str) -> UserSession:
        """
        取得或建立對話狀態
        
        Args:
            user_id: LINE User ID
            
        Returns:
            UserSession: 對話狀態實例
        """
        session = db_session.query(UserSession).filter_by(user_id=user_id).first()
        
        if not session:
            # 先確保 user 存在 (外鍵約束)
            SessionService.get_or_create_user(user_id)
            
            session = UserSession(
                user_id=user_id,
                status="IDLE",
                collected_data={}
            )
            db_session.add(session)
            db_session.commit()
        
        return session
    
    @staticmethod
    def get_status(user_id: str) -> str:
        """
        取得使用者目前狀態
        
        Args:
            user_id: LINE User ID
            
        Returns:
            str: "IDLE" 或 "TESTING"
        """
        session = SessionService.get_or_create_session(user_id)
        return session.status
    
    @staticmethod
    def is_testing(user_id: str) -> bool:
        """檢查使用者是否處於測試模式"""
        return SessionService.get_status(user_id) == "TESTING"
    
    @staticmethod
    def start_test(user_id: str, keep_progress: bool = False) -> UserSession:
        """
        開始測驗模式
        
        Args:
            user_id: LINE User ID
            keep_progress: 是否保留既有進度
            
        Returns:
            UserSession: 更新後的對話狀態
        """
        session = SessionService.get_or_create_session(user_id)
        session.status = "TESTING"
        
        if not keep_progress:
            session.collected_data = {}
        
        session.last_updated = datetime.utcnow()
        db_session.commit()
        
        return session
    
    @staticmethod
    def pause_test(user_id: str) -> UserSession:
        """
        暫停測驗 (切回 IDLE 但保留進度)
        
        Args:
            user_id: LINE User ID
            
        Returns:
            UserSession: 更新後的對話狀態
        """
        session = SessionService.get_or_create_session(user_id)
        session.status = "IDLE"
        session.last_updated = datetime.utcnow()
        db_session.commit()
        
        return session
    
    @staticmethod
    def reset_test(user_id: str) -> UserSession:
        """
        重設測驗 (清空所有進度)
        
        Args:
            user_id: LINE User ID
            
        Returns:
            UserSession: 更新後的對話狀態
        """
        session = SessionService.get_or_create_session(user_id)
        session.status = "IDLE"
        session.collected_data = {}
        session.last_updated = datetime.utcnow()
        db_session.commit()
        
        return session
    
    @staticmethod
    def update_collected_data(user_id: str, new_data: dict) -> UserSession:
        """
        更新已收集的資料
        
        Args:
            user_id: LINE User ID
            new_data: 新收集的資料 (會合併至現有資料)
            
        Returns:
            UserSession: 更新後的對話狀態
        """
        session = SessionService.get_or_create_session(user_id)
        
        # 合併資料
        merged = {**session.collected_data, **new_data}
        session.collected_data = merged
        session.last_updated = datetime.utcnow()
        db_session.commit()
        
        return session
    
    @staticmethod
    def get_collected_data(user_id: str) -> dict:
        """
        取得已收集的資料
        
        Args:
            user_id: LINE User ID
            
        Returns:
            dict: 已收集的資料
        """
        session = SessionService.get_or_create_session(user_id)
        return session.collected_data or {}
    
    @staticmethod
    def has_progress(user_id: str) -> bool:
        """
        檢查是否有未完成的測驗進度
        
        Args:
            user_id: LINE User ID
            
        Returns:
            bool: 是否有進度
        """
        session = SessionService.get_or_create_session(user_id)
        return bool(session.collected_data)
    
    @staticmethod
    def set_persona_result(user_id: str, persona_id: str) -> None:
        """
        設定使用者的測驗結果
        
        Args:
            user_id: LINE User ID
            persona_id: 診斷出的人物誌 ID
        """
        user = db_session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.persona_type = persona_id
            user.updated_at = datetime.utcnow()
            db_session.commit()
    
    @staticmethod
    def mark_blocked(user_id: str, is_blocked: bool = True) -> None:
        """
        標記使用者封鎖狀態
        
        Args:
            user_id: LINE User ID
            is_blocked: 是否封鎖
        """
        user = db_session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.is_blocked = is_blocked
            user.updated_at = datetime.utcnow()
            db_session.commit()
