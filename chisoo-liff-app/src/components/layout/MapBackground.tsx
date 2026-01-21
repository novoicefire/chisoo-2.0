/**
 * Chi．Soo 暨宿 - 地圖背景元件
 * SVG 風格化地圖底圖
 */

import React from 'react';
import { COLORS } from '../../types';

export const MapBackground: React.FC = () => {
    return (
        <div
            className="absolute inset-0 z-0 overflow-hidden pointer-events-none"
            style={{ backgroundColor: COLORS.land }}
        >
            {/* 裝飾區塊 */}
            <div
                className="absolute top-0 right-0 w-64 h-64 rounded-bl-full opacity-50"
                style={{ backgroundColor: COLORS.water }}
            />

            {/* 道路 SVG */}
            <svg className="w-full h-full absolute inset-0">
                <defs>
                    <filter id="road-border" x="-20%" y="-20%" width="140%" height="140%">
                        <feMorphology operator="dilate" radius="1.5" in="SourceAlpha" result="thicken" />
                        <feFlood floodColor={COLORS.stroke} result="color" />
                        <feComposite in="color" in2="thicken" operator="in" result="outline" />
                        <feMerge>
                            <feMergeNode in="outline" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                <g filter="url(#road-border)" stroke={COLORS.road} strokeLinecap="round" fill="none">
                    <path d="M-10 100 Q 150 150 400 50 T 900 200" strokeWidth="16" />
                    <path d="M200 -10 L 250 900" strokeWidth="14" />
                    <path d="M50 300 L 400 350 L 800 300" strokeWidth="10" />
                    <path d="M100 500 Q 200 600 300 500 T 500 600" strokeWidth="10" />
                </g>
            </svg>
        </div>
    );
};

export default MapBackground;
