/**
 * Chi．Soo 暨宿 - 通勤資訊元件
 * 顯示機車/公車通勤時間 (整合真實 API)
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Icon from '../ui/Icon';
import { RouteMapReal } from './RouteMapReal';
import {
    getScooterRoute,
    formatDistance,
    formatDuration,
    getGoogleMapsTransitUrl,
    getGoogleMapsScooterUrl,
    type RouteResult,
} from '../../services/routeService';
import type { Property } from '../../types';
import { NCNU_LOCATION } from '../../types';

interface CommuteInfoProps {
    property: Property;
    title: string;
    isHousing: boolean;
}

export const CommuteInfo: React.FC<CommuteInfoProps> = ({ property, title, isHousing }) => {
    const [mode, setMode] = useState<'scooter' | 'bus'>('scooter');
    const [routeData, setRouteData] = useState<RouteResult | null>(null);
    const [loading, setLoading] = useState(false);

    // 取得真實路線資料
    useEffect(() => {
        if (mode === 'scooter' && property.lng && property.lat) {
            setLoading(true);
            const destLng = isHousing ? NCNU_LOCATION.lng : property.lng;
            const destLat = isHousing ? NCNU_LOCATION.lat : property.lat;
            const fromLng = isHousing ? property.lng : NCNU_LOCATION.lng;
            const fromLat = isHousing ? property.lat : NCNU_LOCATION.lat;

            getScooterRoute(fromLng, fromLat, destLng, destLat)
                .then((data) => {
                    setRouteData(data);
                    setLoading(false);
                })
                .catch(() => setLoading(false));
        }
    }, [mode, property.lng, property.lat, isHousing]);

    const googleMapsTransitUrl = getGoogleMapsTransitUrl(
        property.lng,
        property.lat,
        isHousing ? NCNU_LOCATION.lng : property.lng,
        isHousing ? NCNU_LOCATION.lat : property.lat
    );

    const googleMapsScooterUrl = getGoogleMapsScooterUrl(
        property.lng,
        property.lat,
        isHousing ? NCNU_LOCATION.lng : property.lng,
        isHousing ? NCNU_LOCATION.lat : property.lat
    );

    return (
        <div className="px-5 py-6 border-b border-stroke/20">
            {/* 標題與模式切換 */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-lg text-text">
                    {isHousing ? '前往暨南大學' : `前往 ${title}`}
                </h3>

                {/* 切換器 */}
                <div className="flex bg-stroke/20 p-0.5 rounded-full relative overflow-hidden">
                    <motion.div
                        className="absolute top-0 bottom-0 w-[calc(50%+2px)] bg-white rounded-full shadow-sm z-0"
                        animate={{ x: mode === 'scooter' ? 2 : 'calc(100% - 2px)' }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                    <button
                        onClick={() => setMode('scooter')}
                        className={`relative z-10 px-4 py-1.5 rounded-full flex items-center gap-1.5 text-xs font-bold transition-colors ${mode === 'scooter' ? 'text-text' : 'text-text/60'
                            }`}
                    >
                        <Icon name="scooter" size={14} /> 騎車
                    </button>
                    <button
                        onClick={() => setMode('bus')}
                        className={`relative z-10 px-4 py-1.5 rounded-full flex items-center gap-1.5 text-xs font-bold transition-colors ${mode === 'bus' ? 'text-text' : 'text-text/60'
                            }`}
                    >
                        <Icon name="bus" size={14} /> 公車
                    </button>
                </div>
            </div>

            {/* 通勤資訊卡片 */}
            <div className="bg-white/60 rounded-2xl p-4 border border-white">
                {mode === 'scooter' ? (
                    <motion.div
                        key="scooter"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center justify-between"
                    >
                        <div>
                            {loading ? (
                                <div className="flex items-center gap-2">
                                    <div className="w-6 h-6 border-2 border-text/30 border-t-text rounded-full animate-spin" />
                                    <span className="text-sm text-text/70">計算中...</span>
                                </div>
                            ) : routeData ? (
                                <>
                                    <div className="flex items-end gap-2 mb-1">
                                        <span className="text-3xl font-bold text-text">
                                            {formatDuration(routeData.duration)}
                                        </span>
                                        <span className="text-sm font-bold text-stroke mb-1.5">分鐘</span>
                                    </div>
                                    <p className="text-xs text-text/70">
                                        距離約 {formatDistance(routeData.distance)} 公里
                                    </p>
                                </>
                            ) : (
                                <>
                                    <div className="flex items-end gap-2 mb-1">
                                        <span className="text-3xl font-bold text-text">
                                            {property.commute?.scooter?.time || '--'}
                                        </span>
                                        <span className="text-sm font-bold text-stroke mb-1.5">分鐘</span>
                                    </div>
                                    <p className="text-xs text-text/70">
                                        距離約 {property.commute?.scooter?.dist || '--'} 公里
                                    </p>
                                </>
                            )}
                        </div>
                        <a
                            href={googleMapsScooterUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-12 h-12 bg-land rounded-full flex items-center justify-center text-text hover:bg-text hover:text-land transition-colors"
                        >
                            <Icon name="nav" size={24} strokeWidth={1.5} />
                        </a>
                    </motion.div>
                ) : (
                    <motion.div key="bus" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <div className="text-center py-4">
                            <div className="w-16 h-16 bg-land rounded-full flex items-center justify-center text-text mx-auto mb-3">
                                <Icon name="bus" size={32} />
                            </div>
                            <p className="text-sm text-text/80 mb-4">
                                點擊下方按鈕在 Google Maps 中查看完整公車路線與時刻表
                            </p>
                            <a
                                href={googleMapsTransitUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 px-6 py-3 bg-text text-land rounded-full font-bold text-sm shadow-lg hover:bg-text/90 transition-colors"
                            >
                                <Icon name="nav" size={18} />
                                在 Google Maps 中查看
                            </a>
                        </div>
                    </motion.div>
                )}
            </div>

            {/* 路線地圖 (僅機車模式) */}
            {mode === 'scooter' && routeData && (
                <RouteMapReal routeGeometry={routeData.geometry} property={property} isHousing={isHousing} />
            )}
        </div>
    );
};

export default CommuteInfo;
