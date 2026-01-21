/**
 * Chi．Soo 暨宿 - Mapbox 路線規劃服務
 * 使用 Mapbox Directions API 取得真實路線
 */

import { NCNU_LOCATION } from '../types';

export interface RouteResult {
    distance: number; // 公尺
    duration: number; // 秒
    geometry: GeoJSON.LineString;
}

/**
 * 計算兩點之間的駕駛/騎車路線
 */
export async function getScooterRoute(
    fromLng: number,
    fromLat: number,
    toLng: number = NCNU_LOCATION.lng,
    toLat: number = NCNU_LOCATION.lat
): Promise<RouteResult | null> {
    const token = import.meta.env.VITE_MAPBOX_TOKEN;

    if (!token) {
        console.error('Mapbox token not found');
        return null;
    }

    try {
        const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${fromLng},${fromLat};${toLng},${toLat}?geometries=geojson&overview=full&access_token=${token}`;

        const response = await fetch(url);
        const data = await response.json();

        if (data.routes && data.routes.length > 0) {
            const route = data.routes[0];
            return {
                distance: route.distance,
                duration: route.duration,
                geometry: route.geometry,
            };
        }
        return null;
    } catch (error) {
        console.error('Failed to fetch route:', error);
        return null;
    }
}

/**
 * 格式化距離 (公尺 -> 公里)
 */
export function formatDistance(meters: number): string {
    return (meters / 1000).toFixed(1);
}

/**
 * 格式化時間 (秒 -> 分鐘)
 */
export function formatDuration(seconds: number): string {
    return Math.round(seconds / 60).toString();
}

/**
 * 產生 Google Maps 導航連結 (公車模式)
 */
export function getGoogleMapsTransitUrl(
    fromLng: number,
    fromLat: number,
    toLng: number = NCNU_LOCATION.lng,
    toLat: number = NCNU_LOCATION.lat
): string {
    return `https://www.google.com/maps/dir/?api=1&origin=${fromLat},${fromLng}&destination=${toLat},${toLng}&travelmode=transit`;
}

/**
 * 產生 Google Maps 導航連結 (機車模式)
 */
export function getGoogleMapsScooterUrl(
    fromLng: number,
    fromLat: number,
    toLng: number = NCNU_LOCATION.lng,
    toLat: number = NCNU_LOCATION.lat
): string {
    return `https://www.google.com/maps/dir/?api=1&origin=${fromLat},${fromLng}&destination=${toLat},${toLng}&travelmode=driving`;
}
