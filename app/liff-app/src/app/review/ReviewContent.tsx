/**
 * 評價系統內容元件
 * 專案：Chi Soo 租屋小幫手
 */

'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import StarRating from '@/components/StarRating';
import ReviewItem from '@/components/ReviewItem';
import {
    getReviews,
    createReview,
    deleteReview,
    getHouses,
    type Review,
    type House
} from '@/lib/api';
import { initLiff, getUserId, closeLiff, isInLineApp } from '@/lib/liff';

type TabType = 'my-reviews' | 'new-review';

export default function ReviewContent() {
    const searchParams = useSearchParams();
    const preselectedHouseId = searchParams.get('house_id');

    const [activeTab, setActiveTab] = useState<TabType>(
        preselectedHouseId ? 'new-review' : 'my-reviews'
    );
    const [userId, setUserId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // 我的評價
    const [myReviews, setMyReviews] = useState<Review[]>([]);

    // 新增評價表單
    const [houses, setHouses] = useState<House[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedHouse, setSelectedHouse] = useState<House | null>(null);
    const [rating, setRating] = useState(0);
    const [comment, setComment] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [remainingToday, setRemainingToday] = useState<number | null>(null);

    // 初始化
    useEffect(() => {
        async function init() {
            try {
                await initLiff();
                const uid = getUserId();
                setUserId(uid);

                if (uid) {
                    // 載入我的評價
                    const reviewsData = await getReviews(uid);
                    setMyReviews(reviewsData.reviews);

                    // 計算今日剩餘額度
                    const today = new Date().toDateString();
                    const todayCount = reviewsData.reviews.filter(
                        (r) => new Date(r.created_at).toDateString() === today
                    ).length;
                    setRemainingToday(3 - todayCount);
                }

                // 載入房源列表
                const housesData = await getHouses({ limit: 100 });
                setHouses(housesData.houses);

                // 如果有預選房源
                if (preselectedHouseId) {
                    const house = housesData.houses.find(
                        (h) => h.house_id === Number(preselectedHouseId)
                    );
                    if (house) setSelectedHouse(house);
                }
            } catch (e) {
                console.error('初始化失敗', e);
            } finally {
                setLoading(false);
            }
        }

        init();
    }, [preselectedHouseId]);

    // 搜尋房源
    const filteredHouses = houses.filter(
        (house) =>
            house.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            house.address?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // 提交評價
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!userId || !selectedHouse || rating === 0) {
            alert('請完整填寫表單');
            return;
        }

        if (remainingToday !== null && remainingToday <= 0) {
            alert('您今日的評價次數已達上限，請明日再來。');
            return;
        }

        setSubmitting(true);
        try {
            const result = await createReview(userId, {
                house_id: selectedHouse.house_id,
                rating,
                comment,
            });

            alert(`評價已提交審核！今日剩餘額度：${result.remaining_today} 篇`);
            setRemainingToday(result.remaining_today);

            // 重置表單
            setSelectedHouse(null);
            setRating(0);
            setComment('');
            setSearchQuery('');
            setActiveTab('my-reviews');

            // 重新載入我的評價
            const reviewsData = await getReviews(userId);
            setMyReviews(reviewsData.reviews);
        } catch (e: unknown) {
            const error = e as Error;
            if (error.message.includes('limit')) {
                alert('您今日的評價次數已達上限，請明日再來。');
            } else {
                alert('提交失敗：' + error.message);
            }
        } finally {
            setSubmitting(false);
        }
    };

    // 刪除評價
    const handleDelete = async (reviewId: number) => {
        if (!userId || !confirm('確定要刪除這則評價嗎？')) return;

        try {
            await deleteReview(userId, reviewId);
            setMyReviews((prev) => prev.filter((r) => r.review_id !== reviewId));
            alert('已刪除');
        } catch (e) {
            alert('刪除失敗');
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
            </div>
        );
    }

    if (!userId) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                    <p className="text-gray-600 mb-4">請透過 LINE 開啟此頁面</p>
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
        <div className="min-h-screen bg-gray-50">
            {/* 頂部 Tab */}
            <div className="bg-white border-b sticky top-0 z-10">
                <div className="flex">
                    <button
                        onClick={() => setActiveTab('my-reviews')}
                        className={`flex-1 py-4 text-center font-medium transition ${activeTab === 'my-reviews'
                                ? 'text-indigo-600 border-b-2 border-indigo-600'
                                : 'text-gray-500'
                            }`}
                    >
                        📋 我的評價
                    </button>
                    <button
                        onClick={() => setActiveTab('new-review')}
                        className={`flex-1 py-4 text-center font-medium transition ${activeTab === 'new-review'
                                ? 'text-indigo-600 border-b-2 border-indigo-600'
                                : 'text-gray-500'
                            }`}
                    >
                        ✍️ 新增評價
                    </button>
                </div>
            </div>

            {/* 內容區 */}
            <div className="p-4">
                {activeTab === 'my-reviews' ? (
                    // 我的評價
                    <div>
                        {myReviews.length > 0 ? (
                            <div className="space-y-3">
                                {myReviews.map((review) => (
                                    <ReviewItem
                                        key={review.review_id}
                                        review={review}
                                        showStatus
                                        onDelete={handleDelete}
                                    />
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <p className="text-gray-500 mb-4">您還沒有提交過評價</p>
                                <button
                                    onClick={() => setActiveTab('new-review')}
                                    className="bg-indigo-500 text-white px-6 py-2 rounded-lg"
                                >
                                    撰寫第一則評價
                                </button>
                            </div>
                        )}
                    </div>
                ) : (
                    // 新增評價
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* 今日額度提示 */}
                        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 text-center">
                            <span className="text-indigo-700 text-sm">
                                今日剩餘額度：
                                <span className="font-bold text-lg mx-1">
                                    {remainingToday ?? '?'}
                                </span>
                                篇
                            </span>
                        </div>

                        {/* 房源搜尋 */}
                        <div className="bg-white rounded-lg p-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                選擇房源 *
                            </label>

                            {selectedHouse ? (
                                <div className="flex items-center justify-between bg-indigo-50 rounded-lg p-3">
                                    <span className="font-medium">{selectedHouse.name}</span>
                                    <button
                                        type="button"
                                        onClick={() => setSelectedHouse(null)}
                                        className="text-gray-500 hover:text-gray-700"
                                    >
                                        ✕
                                    </button>
                                </div>
                            ) : (
                                <>
                                    <input
                                        type="text"
                                        placeholder="搜尋房源名稱或地址..."
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                                    />
                                    {searchQuery && (
                                        <div className="mt-2 max-h-40 overflow-y-auto border rounded-lg">
                                            {filteredHouses.length > 0 ? (
                                                filteredHouses.slice(0, 10).map((house) => (
                                                    <button
                                                        key={house.house_id}
                                                        type="button"
                                                        onClick={() => {
                                                            setSelectedHouse(house);
                                                            setSearchQuery('');
                                                        }}
                                                        className="w-full text-left px-4 py-2 hover:bg-gray-100 border-b last:border-b-0"
                                                    >
                                                        <div className="font-medium">{house.name}</div>
                                                        <div className="text-xs text-gray-500">
                                                            ${house.rent}/月
                                                        </div>
                                                    </button>
                                                ))
                                            ) : (
                                                <p className="px-4 py-2 text-gray-500 text-sm">
                                                    找不到符合的房源
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </>
                            )}
                        </div>

                        {/* 評分 */}
                        <div className="bg-white rounded-lg p-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                評分 *
                            </label>
                            <StarRating rating={rating} onChange={setRating} size="lg" />
                        </div>

                        {/* 評論 */}
                        <div className="bg-white rounded-lg p-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                評論內容
                            </label>
                            <textarea
                                value={comment}
                                onChange={(e) => setComment(e.target.value)}
                                placeholder="分享您的租屋經驗..."
                                rows={4}
                                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                            />
                        </div>

                        {/* 學生證提醒 */}
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                            <p className="text-yellow-800 text-sm">
                                ⚠️ 評價將進入審核，審核通過後才會公開顯示。
                            </p>
                        </div>

                        {/* 提交按鈕 */}
                        <button
                            type="submit"
                            disabled={submitting || !selectedHouse || rating === 0 || remainingToday === 0}
                            className="w-full bg-indigo-500 hover:bg-indigo-600 text-white py-3 rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {submitting ? '提交中...' : '提交評價'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
}
