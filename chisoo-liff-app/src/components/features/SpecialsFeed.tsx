/**
 * Chi．Soo 暨宿 - 本月精選元件
 */

import React from 'react';
import Icon from '../ui/Icon';
import { SPECIALS } from '../../data';

interface SpecialsFeedProps {
    onClickCard: (locId: string) => void;
}

export const SpecialsFeed: React.FC<SpecialsFeedProps> = ({ onClickCard }) => {
    return (
        <div className="px-5 pb-safe-bottom pt-6 bg-land min-h-full">
            {/* 標題 */}
            <div className="mb-6 flex items-center justify-center relative">
                <div className="absolute left-0 top-1/2 w-full h-[1px] bg-stroke/30" />
                <span className="relative z-10 bg-land px-4 font-bold text-lg text-text tracking-widest">
                    本月精選
                </span>
            </div>

            {/* 卡片列表 */}
            <div className="space-y-6">
                {SPECIALS.map((s) => (
                    <div
                        key={s.id}
                        onClick={() => onClickCard(s.locId)}
                        className="bg-white rounded-2xl overflow-hidden shadow-md cursor-pointer hover:shadow-xl transition-shadow border border-stroke/10 group"
                    >
                        <div className="h-48 relative overflow-hidden">
                            <img
                                src={s.image}
                                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                alt={s.title}
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-text/90 via-transparent to-transparent opacity-80" />
                            <div className="absolute top-3 right-3 bg-star text-land text-xs font-bold px-3 py-1 rounded-full shadow-sm">
                                {s.date}
                            </div>
                            <div className="absolute bottom-4 left-4 right-4">
                                <h3 className="text-xl font-bold text-land mb-1">{s.title}</h3>
                            </div>
                        </div>
                        <div className="p-4">
                            <p className="text-sm text-text/80 leading-relaxed mb-3">{s.desc}</p>
                            <div className="flex items-center text-xs font-bold text-star">
                                查看地圖位置 <Icon name="mapPin" size={14} className="ml-1" />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="h-24" />
        </div>
    );
};

export default SpecialsFeed;
