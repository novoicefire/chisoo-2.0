/**
 * Chi．Soo 暨宿 - API 服務
 * 與 Flask 後端 API 通訊
 */

import type { Property } from '../types';

// API 基礎路徑 (可透過環境變數覆蓋)
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

/**
 * Flask House API 回傳格式
 */
interface HouseApiResponse {
    house_id: number;
    name: string;
    address: string;
    category_tag: string;
    rent: number;
    room_type: string;
    features: Record<string, boolean>;
    description: string;
    image_url: string | null;
    images: string[];
    latitude: number | null;
    longitude: number | null;
    avg_rating: number;
    review_count: number;
    created_at: string;
}

interface HousesListResponse {
    houses: HouseApiResponse[];
    page: number;
    limit: number;
    total: number;
    pages: number;
}

/**
 * 將 Flask API 回傳的 House 轉換為前端 Property 類型
 */
function transformHouse(house: HouseApiResponse): Property {
    // 將 features 物件轉為標籤陣列
    const tags = Object.entries(house.features || {})
        .filter(([_, value]) => value)
        .map(([key]) => {
            const tagMap: Record<string, string> = {
                wifi: 'WiFi',
                ac: '冷氣',
                garbage: '子母車',
                elevator: '電梯',
                security: '門禁',
                cctv: '監視器',
                landlord_live_in: '房東同住',
                living_room: '客廳',
                kitchen: '可開伙',
                balcony: '陽台',
                laundry: '洗衣機',
                parking: '停車位',
                new_renovation: '新裝潢',
            };
            return tagMap[key] || key;
        });

    return {
        id: house.house_id,
        type: 'housing',
        title: house.name,
        price: `NT$ ${house.rent.toLocaleString()}`,
        rating: house.avg_rating || 4.5,
        ratingCount: house.review_count || 0,
        address: house.address || '埔里鎮',
        desc: house.description || '',
        tags,
        images: house.images?.length > 0
            ? house.images
            : house.image_url
                ? [house.image_url]
                : ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80'],
        lng: house.longitude || 120.9647,
        lat: house.latitude || 23.9595,
        commute: {
            scooter: { time: '--', dist: '--' },
            bus: { stopName: '--', walkMin: '--', busNo: '--', busTime: '--', dest: '暨南大學' },
        },
        reviews: [],
    };
}

/**
 * 取得房源列表
 */
export async function fetchHouses(options?: {
    page?: number;
    limit?: number;
    category?: string;
    minRent?: number;
    maxRent?: number;
}): Promise<Property[]> {
    const params = new URLSearchParams();
    params.set('limit', String(options?.limit || 50));
    if (options?.page) params.set('page', String(options.page));
    if (options?.category) params.set('category', options.category);
    if (options?.minRent) params.set('min_rent', String(options.minRent));
    if (options?.maxRent) params.set('max_rent', String(options.maxRent));

    try {
        const response = await fetch(`${API_BASE}/houses?${params}`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        const data: HousesListResponse = await response.json();
        return data.houses.map(transformHouse);
    } catch (error) {
        console.error('Failed to fetch houses:', error);
        return [];
    }
}

/**
 * 取得單一房源詳情
 */
export async function fetchHouseDetail(houseId: number): Promise<Property | null> {
    try {
        const response = await fetch(`${API_BASE}/houses/${houseId}`);
        if (!response.ok) return null;
        const house: HouseApiResponse = await response.json();
        return transformHouse(house);
    } catch (error) {
        console.error('Failed to fetch house detail:', error);
        return null;
    }
}

/**
 * 健康檢查 - 確認 API 可用
 */
export async function checkApiHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE}/health`);
        return response.ok;
    } catch {
        return false;
    }
}
