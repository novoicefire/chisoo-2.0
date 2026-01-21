/**
 * Chi．Soo 暨宿 - 指南輪播元件
 */

import React from 'react';
import Icon from '../ui/Icon';
import { GUIDE_CARDS } from '../../data';

export const GuideCarousel: React.FC = () => {
    return (
        <div className="pt-2 pb-6 -mx-5 px-5">
            <div className="flex gap-4 overflow-x-auto snap-x no-scrollbar pb-2 px-1">
                {GUIDE_CARDS.map((card) => (
                    <div
                        key={card.id}
                        className="w-[80%] shrink-0 snap-center bg-white rounded-[24px] p-5 shadow-sm border border-stroke/20 flex flex-col justify-between h-40 relative overflow-hidden group"
                    >
                        {/* 右下角裝飾 Icon */}
                        <div className="absolute -bottom-4 -right-4 text-star/10 transform rotate-12 scale-150 pointer-events-none transition-transform group-hover:scale-[1.7] group-hover:rotate-6">
                            <Icon name={card.icon} size={80} />
                        </div>

                        <div className="relative z-10 flex flex-col h-full">
                            {/* 左上角膠囊標籤 */}
                            <div className="self-start px-2.5 py-1 rounded-full bg-star/10 mb-3 flex items-center gap-1.5 backdrop-blur-sm">
                                <Icon name={card.icon} size={10} className="text-star" />
                                <span className="text-[10px] font-bold text-star tracking-wide">{card.tag}</span>
                            </div>

                            <h4 className="font-bold text-base text-text leading-snug mb-2 line-clamp-1">
                                {card.title}
                            </h4>
                            <p className="text-xs text-text/70 leading-relaxed line-clamp-2">{card.desc}</p>

                            <div className="mt-auto flex justify-end">
                                <span className="text-[10px] font-bold text-stroke flex items-center group-hover:text-text transition-colors">
                                    閱讀更多 <Icon name="nav" size={12} className="ml-1" />
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GuideCarousel;
