/**
 * Chi．Soo 暨宿 - 路線地圖元件
 * 顯示通勤路線示意圖
 */

import React from 'react';

interface RouteMapProps {
    mode: 'scooter' | 'bus';
    isHousing: boolean;
}

export const RouteMap: React.FC<RouteMapProps> = ({ mode, isHousing }) => {
    return (
        <div className="w-full h-40 bg-water/30 rounded-xl overflow-hidden relative border border-stroke/30 mt-4">
            {/* 道路背景 */}
            <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                <path
                    d="M-10 120 C 50 120, 100 80, 150 100 S 250 150, 350 120"
                    stroke="white"
                    strokeWidth="8"
                    fill="none"
                    opacity="0.8"
                />
            </svg>

            {/* 校園裝飾 (房源模式) */}
            {isHousing && (
                <>
                    <div className="absolute top-[-20px] right-[-20px] w-32 h-32 bg-text/5 rounded-full blur-xl" />
                    <div className="absolute top-2 right-2 text-[10px] font-bold text-text/40">NCNU Campus</div>
                </>
            )}

            {/* 路線 SVG */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {mode === 'scooter' ? (
                    isHousing ? (
                        <>
                            <path
                                d="M 40 100 C 80 100, 120 40, 200 60 S 260 40, 280 40"
                                stroke="#4e3c2e"
                                strokeWidth="4"
                                fill="none"
                                strokeLinecap="round"
                                className="drop-shadow-sm"
                            />
                            <path
                                d="M 40 100 C 80 100, 120 40, 200 60 S 260 40, 280 40"
                                stroke="#faeee1"
                                strokeWidth="2"
                                fill="none"
                                className="animate-flow"
                            />
                            <g transform="translate(160, 45)">
                                <rect x="-30" y="-10" width="60" height="20" rx="4" fill="white" fillOpacity="0.9" />
                                <text x="0" y="4" textAnchor="middle" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                                    經桃米巷
                                </text>
                            </g>
                            <circle cx="280" cy="40" r="4" fill="#4e3c2e" />
                            <text x="270" y="30" textAnchor="end" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                                機車入口
                            </text>
                        </>
                    ) : (
                        <>
                            <path
                                d="M 40 100 L 100 100 L 120 50 L 280 50"
                                stroke="#4e3c2e"
                                strokeWidth="4"
                                fill="none"
                                strokeLinecap="round"
                                className="drop-shadow-sm"
                            />
                            <path
                                d="M 40 100 L 100 100 L 120 50 L 280 50"
                                stroke="#faeee1"
                                strokeWidth="2"
                                fill="none"
                                className="animate-flow"
                            />
                            <g transform="translate(160, 30)">
                                <rect x="-35" y="-10" width="70" height="20" rx="4" fill="white" fillOpacity="0.9" />
                                <text x="0" y="4" textAnchor="middle" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                                    經市區道路
                                </text>
                            </g>
                            <circle cx="280" cy="50" r="4" fill="#4e3c2e" />
                            <text x="270" y="40" textAnchor="end" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                                目的地
                            </text>
                        </>
                    )
                ) : isHousing ? (
                    <>
                        <path d="M 40 100 L 80 100" stroke="#b9b0a6" strokeWidth="3" strokeDasharray="4 2" fill="none" />
                        <path
                            d="M 80 100 Q 150 100 220 80 T 280 20"
                            stroke="#4e3c2e"
                            strokeWidth="4"
                            fill="none"
                            strokeLinecap="round"
                            className="drop-shadow-sm"
                        />
                        <path
                            d="M 80 100 Q 150 100 220 80 T 280 20"
                            stroke="#faeee1"
                            strokeWidth="2"
                            fill="none"
                            className="animate-flow"
                        />
                        <g transform="translate(180, 85)">
                            <rect x="-30" y="-10" width="60" height="20" rx="4" fill="white" fillOpacity="0.9" />
                            <text x="0" y="4" textAnchor="middle" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                                台14線
                            </text>
                        </g>
                        <circle cx="280" cy="20" r="4" fill="#4e3c2e" />
                        <text x="270" y="30" textAnchor="end" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                            學人會館
                        </text>
                    </>
                ) : (
                    <>
                        <path d="M 40 100 L 60 100" stroke="#b9b0a6" strokeWidth="3" strokeDasharray="4 2" fill="none" />
                        <path
                            d="M 60 100 Q 120 100 180 80 T 240 60"
                            stroke="#4e3c2e"
                            strokeWidth="4"
                            fill="none"
                            strokeLinecap="round"
                            className="drop-shadow-sm"
                        />
                        <path
                            d="M 60 100 Q 120 100 180 80 T 240 60"
                            stroke="#faeee1"
                            strokeWidth="2"
                            fill="none"
                            className="animate-flow"
                        />
                        <path d="M 240 60 L 280 60" stroke="#b9b0a6" strokeWidth="3" strokeDasharray="4 2" fill="none" />
                        <g transform="translate(150, 70)">
                            <rect x="-30" y="-10" width="60" height="20" rx="4" fill="white" fillOpacity="0.9" />
                            <text x="0" y="4" textAnchor="middle" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                                公車行駛
                            </text>
                        </g>
                        <circle cx="280" cy="60" r="4" fill="#4e3c2e" />
                        <text x="270" y="50" textAnchor="end" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                            目的地
                        </text>
                    </>
                )}
                {/* 起點 */}
                <circle cx="40" cy="100" r="6" fill="#4e3c2e" stroke="white" strokeWidth="2" />
                <text x="40" y="125" textAnchor="middle" fontSize="10" fill="#4e3c2e" fontWeight="bold">
                    {isHousing ? '房源位置' : '我的位置'}
                </text>
            </svg>
        </div>
    );
};

export default RouteMap;
