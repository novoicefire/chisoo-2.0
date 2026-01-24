/**
 * Chi．Soo 暨宿 - 使用者選單元件
 */

import React from 'react';
import { motion } from 'framer-motion';
import Icon from '../ui/Icon';
import type { UserData, VerificationStatus } from '../../types';

interface UserMenuProps {
    user: UserData | null;
    verificationStatus: VerificationStatus;  // 新增：正確的驗證狀態
    onClose: () => void;
    onOpenVerification: () => void;
    onLogout: () => void;
    onOpenFavorites: () => void;
    onOpenReviews: () => void;
}

export const UserMenu: React.FC<UserMenuProps> = ({
    user,
    verificationStatus,
    onClose,
    onOpenVerification,
    onLogout,
    onOpenFavorites,
    onOpenReviews,
}) => {
    // 判斷是否已驗證：必須明確檢查 verificationStatus
    const isVerified = verificationStatus === 'verified';

    return (
        <>
            {/* Backdrop */}
            <div className="fixed inset-0 z-40" onClick={onClose} />

            {/* Menu */}
            <motion.div
                initial={{ opacity: 0, scale: 0.9, y: -10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="absolute top-16 right-4 z-50 w-[320px] bg-land rounded-[28px] shadow-[0_4px_20px_rgba(78,60,46,0.2)] p-4 flex flex-col border border-white/50"
            >
                {/* 使用者資訊卡 */}
                <div className="bg-white rounded-[20px] p-4 flex flex-col items-center shadow-sm mb-2">
                    <div className="w-20 h-20 rounded-full bg-land flex items-center justify-center text-text text-3xl font-bold mb-3 border-4 border-white shadow-inner overflow-hidden">
                        {user?.pictureUrl ? (
                            <img src={user.pictureUrl} alt={user.displayName || user.name} className="w-full h-full object-cover" />
                        ) : (
                            user?.displayName?.charAt(0) || user?.name?.charAt(0) || 'L'
                        )}
                    </div>
                    <h3 className="text-lg font-bold text-text">{user?.displayName || user?.name || 'LINE 用戶'}</h3>
                    
                    {/* 顯示驗證狀態說明 */}
                    <p className="text-sm text-stroke mb-4">
                        {isVerified ? (user?.dept || '暨大學生') : '未驗證學生身份'}
                    </p>
                    
                    {/* 根據 verificationStatus 顯示對應 UI */}
                    {isVerified ? (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-star/10 text-star text-xs font-bold">
                            <Icon name="check" size={12} /> 已驗證學生
                        </div>
                    ) : verificationStatus === 'pending' ? (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gray-100 text-gray-500 text-xs font-bold">
                            <Icon name="time" size={12} /> 審核中
                        </div>
                    ) : (
                        <button
                            onClick={() => {
                                onClose();
                                onOpenVerification();
                            }}
                            className="w-full py-2.5 rounded-full border border-stroke text-text text-sm font-bold hover:bg-land transition-colors"
                        >
                            驗證暨大學生身份
                        </button>
                    )}
                </div>

                {/* 選單項目 */}
                <div className="bg-white rounded-[20px] overflow-hidden shadow-sm">
                    <button
                        onClick={() => {
                            onClose();
                            onOpenFavorites();
                        }}
                        className="w-full px-4 py-3.5 flex items-center gap-4 text-sm text-text hover:bg-land/50 text-left"
                    >
                        <Icon name="bookmark" size={20} className="opacity-60" /> 我的收藏
                    </button>
                    <button
                        onClick={() => {
                            onClose();
                            onOpenReviews();
                        }}
                        className="w-full px-4 py-3.5 flex items-center gap-4 text-sm text-text hover:bg-land/50 text-left border-t border-gray-100"
                    >
                        <Icon name="message-square" size={20} className="opacity-60" /> 評價管理
                    </button>
                    <button
                        onClick={() => {
                            onLogout();
                            onClose();
                        }}
                        className="w-full px-4 py-3.5 flex items-center gap-4 text-sm text-text hover:bg-land/50 text-left border-t border-gray-100"
                    >
                        <Icon name="logout" size={20} className="opacity-60" /> 登出
                    </button>
                </div>
            </motion.div>
        </>
    );
};

export default UserMenu;

