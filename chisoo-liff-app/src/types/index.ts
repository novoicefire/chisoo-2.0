/**
 * Chi．Soo 暨宿 - 類型定義
 * 定義房源、咖啡廳、收藏等資料結構
 */

/** 通勤資訊 - 機車 */
export interface ScooterCommute {
    time: string;
    dist: string;
}

/** 通勤資訊 - 公車 */
export interface BusCommute {
    stopName: string;
    walkMin: string;
    busNo: string;
    busTime: string;
    dest: string;
}

/** 通勤資訊 */
export interface CommuteInfo {
    scooter: ScooterCommute;
    bus: BusCommute;
}

/** 評論 */
export interface Review {
    name: string;
    time: string;
    rating: number;
    text: string;
}

/** 地點類型 */
export type LocationType = 'housing' | 'place' | 'event';

/** 房源/地點基礎資料 */
export interface Property {
    id: string | number;
    type: LocationType;
    title: string;
    price: string;
    rating: number;
    ratingCount: number;
    address: string;
    desc: string;
    tags: string[];
    images: string[];
    commute: CommuteInfo;
    reviews: Review[];
    // 地圖座標
    lng: number;  // 經度
    lat: number;  // 緯度
    // 舊版百分比座標 (向後相容)
    x?: string;
    y?: string;
}

/** 精選活動 */
export interface Special {
    id: string;
    title: string;
    date: string;
    desc: string;
    image: string;
    locId: string;
}

/** 指南卡片 */
export interface GuideCard {
    id: string;
    title: string;
    desc: string;
    icon: string;
    tag: string;
}

/** 收藏狀態 */
export type FavoriteStatus = 'saved' | 'visited' | 'contacting';

/** 收藏項目 */
export interface FavoriteItem extends Property {
    status: FavoriteStatus;
    addedAt: string;
}

/** 身份驗證狀態 */
export type VerificationStatus = 'unverified' | 'pending' | 'verified' | 'rejected';

/** 使用者資料 (結合 LINE Profile 與學生驗證) */
export interface UserData {
    // LINE Profile
    lineUserId?: string;
    displayName?: string;
    pictureUrl?: string;
    // 學生驗證資料
    name: string;
    studentId: string;
    dept: string;
}

/** App 模式 */
export type AppMode = 'housing' | 'coffee';

/** BottomSheet 狀態 */
export type SheetState = 'peek' | 'half' | 'full';

/** 設計系統色彩 */
export const COLORS = {
    land: '#faeee1',
    text: '#4e3c2e',
    stroke: '#b9b0a6',
    road: '#ffffff',
    water: '#e8dfd6',
    star: '#e69a4d',
} as const;

/** 地圖預設中心 (埔里) */
export const MAP_CENTER = {
    lng: 120.9647,
    lat: 23.9595,
    zoom: 13,
} as const;

/** 暨南大學座標 (桃米警衛室入口) */
export const NCNU_LOCATION = {
    lng: 120.93193042901837,
    lat: 23.948202841048932,
} as const;
