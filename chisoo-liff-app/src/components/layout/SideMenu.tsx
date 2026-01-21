/**
 * Chi．Soo 暨宿 - 側邊選單元件
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Icon from '../ui/Icon';
import type { AppMode, SheetState } from '../../types';

interface SideMenuProps {
    isOpen: boolean;
    onClose: () => void;
    setAppMode: (mode: AppMode) => void;
    setSheetState: (state: SheetState) => void;
    setShowSpecials: (show: boolean) => void;
    setShowAbout: (show: boolean) => void;
}

export const SideMenu: React.FC<SideMenuProps> = ({
    isOpen,
    onClose,
    setAppMode,
    setSheetState,
    setShowSpecials,
    setShowAbout,
}) => {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-text/60 z-50 backdrop-blur-sm"
                        onClick={onClose}
                    />

                    {/* Menu Panel */}
                    <motion.div
                        initial={{ x: '-100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '-100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        className="fixed top-0 left-0 bottom-0 w-[80%] max-w-[300px] bg-land z-50 shadow-2xl flex flex-col"
                    >
                        {/* Header */}
                        <div className="px-6 pb-6 pt-24 bg-white/50 border-b border-stroke/20">
                            <div className="flex items-center gap-3 mb-1">
                                <div className="w-10 h-10 bg-text rounded-full flex items-center justify-center text-land">
                                    <Icon name="mapPin" size={20} />
                                </div>
                                <span className="font-bold text-xl text-text">Chi．Soo 暨宿</span>
                            </div>
                            <p className="text-xs text-stroke pl-1">埔里生活指南 x 暨大租屋</p>
                        </div>

                        {/* Menu Items */}
                        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
                            {/* 探索生活 */}
                            <div>
                                <h4 className="px-3 text-xs font-bold text-stroke mb-2 uppercase tracking-wider">
                                    探索生活
                                </h4>
                                <div className="space-y-1">
                                    <button
                                        onClick={() => {
                                            setShowSpecials(true);
                                            setSheetState('half');
                                            onClose();
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left"
                                    >
                                        <Icon name="star" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">本月精選特輯</span>
                                    </button>
                                    <button
                                        onClick={() => {
                                            setAppMode('coffee');
                                            onClose();
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left"
                                    >
                                        <Icon name="coffee" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">讀書咖啡地圖</span>
                                    </button>
                                    <button
                                        onClick={() => {
                                            setAppMode('housing');
                                            onClose();
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left"
                                    >
                                        <Icon name="mapPin" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">找房模式 (預設)</span>
                                    </button>
                                </div>
                            </div>

                            {/* 暨大學生工具 */}
                            <div>
                                <h4 className="px-3 text-xs font-bold text-stroke mb-2 uppercase tracking-wider">
                                    暨大學生工具
                                </h4>
                                <div className="space-y-1">
                                    <a
                                        href="https://ncnu-super-assistant.vercel.app/"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left block"
                                    >
                                        <Icon name="robot" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">暨大生超級助理</span>
                                    </a>
                                    <a
                                        href="https://www.taiwanbus.tw/eBUSPage/Query/QueryResult.aspx?rno=0706B&rn=1624261592512&lan=C"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left block"
                                    >
                                        <Icon name="bus" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">校車/公車動態</span>
                                    </a>
                                </div>
                            </div>

                            {/* 平台資訊 */}
                            <div>
                                <h4 className="px-3 text-xs font-bold text-stroke mb-2 uppercase tracking-wider">
                                    平台資訊
                                </h4>
                                <div className="space-y-1">
                                    <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left">
                                        <Icon name="user" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">房東合作刊登</span>
                                    </button>
                                    <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left">
                                        <Icon name="alert" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">許願池 / 回報問題</span>
                                    </button>
                                    <button
                                        onClick={() => {
                                            setShowAbout(true);
                                            setSheetState('half');
                                            onClose();
                                        }}
                                        className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/60 text-text transition-colors text-left"
                                    >
                                        <Icon name="info" size={20} className="opacity-70" />
                                        <span className="font-medium text-sm">關於我們</span>
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-4 text-center border-t border-stroke/20">
                            <p className="text-[10px] text-stroke">v1.2.0 • Made for NCNU</p>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default SideMenu;
