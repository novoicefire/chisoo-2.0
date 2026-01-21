/**
 * Chi．Soo 暨宿 - 關於頁面元件
 */

import React from 'react';
import Icon from '../ui/Icon';

interface AboutContentProps {
    onClose: () => void;
}

export const AboutContent: React.FC<AboutContentProps> = ({ onClose }) => {
    return (
        <div className="h-full bg-land relative overflow-y-auto">
            <button
                onClick={onClose}
                className="absolute top-4 left-4 z-20 w-10 h-10 rounded-full bg-white/90 backdrop-blur shadow-md flex items-center justify-center text-text"
            >
                <Icon name="back" size={20} />
            </button>

            <div className="pt-20 px-6 pb-12 flex flex-col items-center text-center">
                {/* Logo */}
                <div className="w-24 h-24 bg-text rounded-[28px] flex items-center justify-center text-land shadow-xl mb-6 transform -rotate-3 overflow-hidden">
                    <img src="/logo.jpg" className="w-full h-full object-cover" alt="Chi.Soo Logo" />
                </div>

                <h1 className="text-3xl font-bold text-text mb-2 tracking-tight">Chi．Soo 暨宿</h1>
                <p className="text-sm font-bold text-stroke uppercase tracking-[0.2em] mb-8">NCNU Living Guide</p>

                <div className="space-y-8 w-full max-w-sm">
                    {/* 團隊介紹 */}
                    <div className="bg-white/60 p-6 rounded-2xl border border-white/50 shadow-sm">
                        <h3 className="font-bold text-text mb-2 flex items-center justify-center gap-2">
                            <Icon name="heart" size={18} /> 關於好home米
                        </h3>
                        <p className="text-sm text-text/80 leading-relaxed text-justify">
                            「Chi．Soo」取自暨南(Chi Nan) 與住宿 (Soo)
                            諧音。我們是「好home米團隊」，由五位暨大國企系 112
                            級學生組成。團隊技術核心來自「暨大生超級助理」開發者，我們結合商業思維與技術實力，致力於透過這份溫柔的地圖，讓山城租屋生活更加從容。
                        </p>
                    </div>

                    {/* 版本資訊 */}
                    <div className="bg-white/60 p-6 rounded-2xl border border-white/50 shadow-sm">
                        <h3 className="font-bold text-text mb-2 flex items-center justify-center gap-2">
                            <Icon name="info" size={18} /> 版本資訊
                        </h3>
                        <div className="text-sm text-text/80 space-y-1">
                            <p>目前版本：v1.2.0 (Beta)</p>
                            <p>最後更新：2026.01.22</p>
                            <p>開發團隊：好home米團隊 (NCNU IBS)</p>
                        </div>
                    </div>

                    {/* 連結 */}
                    <div className="pt-4">
                        <button className="text-xs text-stroke hover:text-text transition-colors border-b border-transparent hover:border-text">
                            隱私權政策
                        </button>
                        <span className="mx-2 text-stroke">•</span>
                        <button className="text-xs text-stroke hover:text-text transition-colors border-b border-transparent hover:border-text">
                            聯絡我們
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AboutContent;
