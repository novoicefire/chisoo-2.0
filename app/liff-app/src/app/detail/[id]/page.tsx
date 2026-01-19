/**
 * 房源詳情頁
 * 專案：Chi Soo 租屋小幫手
 * 路由：/detail/[id]
 */

'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import PhotoCarousel from '@/components/PhotoCarousel';
import StarRating from '@/components/StarRating';
import ReviewItem from '@/components/ReviewItem';
import { getHouseDetail, addFavorite, type House, type Review } from '@/lib/api';
import { initLiff, getUserId, closeLiff, isInLineApp } from '@/lib/liff';

// 暨大座標
const NCNU_LOCATION = { lat: 23.9576, lng: 120.9277 };

export default function DetailPage() {
    const params = useParams();
    const houseId = Number(params.id);

    const [house, setHouse] = useState<House | null>(null);
    const [reviews, setReviews] = useState<Review[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [userId, setUserId] = useState<string | null>(null);
    const [favoriting, setFavoriting] = useState(false);
    const [commuteTime, setCommuteTime] = useState<string | null>(null);

    // 初始化
    useEffect(() => {
        async function init() {
            try {
                await initLiff();
                setUserId(getUserId());
            } catch (e) {
                console.error('LIFF 初始化失敗', e);
            }

            try {
                const data = await getHouseDetail(houseId);
                setHouse(data);
                setReviews(data.reviews || []);

                // 計算通勤時間 (如果有座標)
                if (data.latitude && data.longitude) {
                    calculateCommuteTime(data.latitude, data.longitude);
                }
            } catch (e) {
                setError('無法載入房源資料');
                console.error(e);
            } finally {
                setLoading(false);
            }
        }

        init();
    }, [houseId]);

    // 計算通勤時間
    const calculateCommuteTime = async (lat: number, lng: number) => {
        // 簡易估算 (直線距離 / 速度)
        const distance = Math.sqrt(
            Math.pow(lat - NCNU_LOCATION.lat, 2) + Math.pow(lng - NCNU_LOCATION.lng, 2)
        ) * 111; // 大約轉換成公里

        const bikeMinutes = Math.round(distance / 0.25); // 假設騎車 15km/h
        setCommuteTime(`騎車約 ${bikeMinutes} 分鐘`);
    };

    // 收藏
    const handleFavorite = async () => {
        if (!userId || !house) return;

        setFavoriting(true);
        try {
            await addFavorite(userId, house.house_id);
            alert('已加入收藏！');
        } catch (e: any) {
            if (e.message.includes('Already')) {
                alert('已在收藏中！');
            } else {
                alert('收藏失敗');
            }
        } finally {
            setFavoriting(false);
        }
    };

    // 設施標籤
    const featureLabels: Record<string, string> = {
        garbage_service: '🚛 子母車',
        elevator: '🛗 電梯',
        security: '🔒 門禁',
        balcony: '🌿 陽台',
        laundry: '👔 獨立洗衣',
        quiet: '🤫 安靜',
        parking: '🅿️ 停車位',
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
            </div>
        );
    }

    if (error || !house) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <p className="text-red-500 mb-4">{error || '找不到房源'}</p>
                    {isInLineApp() && (
                        <button onClick={closeLiff} className="text-indigo-500 underline">
                            關閉
                        </button>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            {/* 照片輪播 */}
            <PhotoCarousel
                images={house.images || []}
                fallbackImage={house.image_url}
            />

            {/* 房源資訊 */}
            <div className="p-4">
                {/* 標題與租金 */}
                <div className="flex items-start justify-between mb-2">
                    <h1 className="text-xl font-bold text-gray-900">{house.name}</h1>
                    <span className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                        ${house.rent.toLocaleString()}/月
                    </span>
                </div>

                {/* 評分與房型 */}
                <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                    <div className="flex items-center gap-1">
                        <StarRating rating={house.avg_rating} readonly size="sm" />
                        <span>({house.review_count} 評價)</span>
                    </div>
                    <span>|</span>
                    <span>{house.room_type || '套房'}</span>
                </div>

                {/* 設施標籤 */}
                {house.features && Object.keys(house.features).length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                        {Object.entries(house.features)
                            .filter(([_, value]) => value)
                            .map(([key]) => (
                                <span
                                    key={key}
                                    className="bg-indigo-50 text-indigo-700 px-2 py-1 rounded text-xs"
                                >
                                    {featureLabels[key] || key}
                                </span>
                            ))}
                    </div>
                )}

                {/* 描述 */}
                {house.description && (
                    <div className="bg-white rounded-lg p-4 mb-4">
                        <h2 className="font-medium text-gray-900 mb-2">房源介紹</h2>
                        <p className="text-gray-600 text-sm whitespace-pre-line">
                            {house.description}
                        </p>
                    </div>
                )}

                {/* 通勤資訊 */}
                {(house.latitude && house.longitude) && (
                    <div className="bg-white rounded-lg p-4 mb-4">
                        <h2 className="font-medium text-gray-900 mb-2">📍 交通資訊</h2>
                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                            <span>🏫 到暨大：</span>
                            <span className="font-medium text-indigo-600">
                                {commuteTime || '計算中...'}
                            </span>
                        </div>
                        {/* Google Maps 嵌入 */}
                        <iframe
                            src={`https://www.google.com/maps/embed/v1/place?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&q=${house.latitude},${house.longitude}&zoom=15`}
                            className="w-full h-48 rounded-lg border-0"
                            loading="lazy"
                            allowFullScreen
                        />
                    </div>
                )}

                {/* 評價區 */}
                <div className="bg-white rounded-lg p-4">
                    <h2 className="font-medium text-gray-900 mb-3">
                        📝 社群評價 ({reviews.length})
                    </h2>

                    {reviews.length > 0 ? (
                        <div className="space-y-3">
                            {reviews.map((review) => (
                                <ReviewItem key={review.review_id} review={review} />
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-sm text-center py-4">
                            目前沒有評價
                        </p>
                    )}

                    {/* 免責聲明 */}
                    <p className="text-gray-400 text-xs mt-4 text-center">
                        本區評價來自學生匿名問卷，內容僅供參考，不代表平台立場，且不保證內容之完全真實性。
                    </p>
                </div>
            </div>

            {/* 底部固定按鈕 */}
            <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4 flex gap-2">
                <button
                    onClick={handleFavorite}
                    disabled={favoriting || !userId}
                    className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-800 py-3 rounded-lg font-medium transition disabled:opacity-50"
                >
                    {favoriting ? '⏳' : '❤️'} 收藏
                </button>
                <a
                    href={`https://www.google.com/maps?q=${house.latitude || ''},${house.longitude || ''}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg font-medium text-center transition"
                >
                    📍 開啟地圖
                </a>
            </div>
        </div>
    );
}
