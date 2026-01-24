/**
 * Chi．Soo 暨宿 - 評價管理頁面元件
 * 顯示用戶所有評價，支援編輯、收回等管理功能
 */

import React, { useState } from 'react';
import Icon from '../ui/Icon';
import type { UserReview, ReviewStatus } from '../../types';
import { COLORS } from '../../types';

interface ReviewsPageProps {
    onClose: () => void;
    reviews: UserReview[];
    onUpdate: (reviewId: number, data: { rating: number; comment: string }) => Promise<boolean>;
    onWithdraw: (reviewId: number) => Promise<boolean>;
    onRefresh: () => void;
    onToast: (msg: string) => void;
}

// 狀態標籤配置
const statusConfig: Record<ReviewStatus, { label: string; bgColor: string; textColor: string }> = {
    approved: { label: '已公開', bgColor: 'bg-green-100', textColor: 'text-green-700' },
    pending: { label: '審核中', bgColor: 'bg-gray-100', textColor: 'text-gray-600' },
    rejected: { label: '被駁回', bgColor: 'bg-red-100', textColor: 'text-red-600' },
};

export const ReviewsPage: React.FC<ReviewsPageProps> = ({
    onClose,
    reviews,
    onUpdate,
    onWithdraw,
    onRefresh,
    onToast,
}) => {
    const [statusFilter, setStatusFilter] = useState<ReviewStatus | 'all'>('all');
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editRating, setEditRating] = useState(5);
    const [editComment, setEditComment] = useState('');
    const [loading, setLoading] = useState(false);

    // 篩選評價
    const filteredReviews = statusFilter === 'all'
        ? reviews
        : reviews.filter(r => r.status === statusFilter);

    // 開始編輯
    const startEdit = (review: UserReview) => {
        setEditingId(review.review_id);
        setEditRating(review.rating);
        setEditComment(review.comment || '');
    };

    // 取消編輯
    const cancelEdit = () => {
        setEditingId(null);
        setEditRating(5);
        setEditComment('');
    };

    // 儲存編輯
    const saveEdit = async (reviewId: number) => {
        setLoading(true);
        const success = await onUpdate(reviewId, { rating: editRating, comment: editComment });
        setLoading(false);
        if (success) {
            onToast('評價已更新，等待審核');
            cancelEdit();
            onRefresh();
        } else {
            onToast('更新失敗，請稍後再試');
        }
    };

    // 收回評價
    const handleWithdraw = async (reviewId: number) => {
        setLoading(true);
        const success = await onWithdraw(reviewId);
        setLoading(false);
        if (success) {
            onToast('評價已收回，可進行編輯');
            onRefresh();
        } else {
            onToast('收回失敗，請稍後再試');
        }
    };

    // 評價卡片
    const ReviewCard: React.FC<{ review: UserReview }> = ({ review }) => {
        const isEditing = editingId === review.review_id;
        const config = statusConfig[review.status];
        const canEdit = review.status === 'pending' || review.status === 'rejected';
        const canWithdraw = review.status === 'approved';

        return (
            <div className="bg-white rounded-2xl p-4 shadow-sm border border-stroke/20">
                {/* 房源資訊 */}
                <div className="flex gap-3 mb-3">
                    <img
                        src={review.house_image || 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=100&q=60'}
                        className="w-16 h-16 rounded-xl object-cover shrink-0"
                        alt=""
                    />
                    <div className="flex-1 min-w-0">
                        <h4 className="font-bold text-text truncate">{review.house_name || `房源 #${review.house_id}`}</h4>
                        <div className="flex items-center gap-2 mt-1">
                            <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${config.bgColor} ${config.textColor}`}>
                                {config.label}
                            </span>
                            <span className="text-xs text-stroke">
                                {new Date(review.created_at).toLocaleDateString('zh-TW')}
                            </span>
                        </div>
                    </div>
                </div>

                {/* 駁回原因 */}
                {review.status === 'rejected' && review.reject_reason && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-3">
                        <div className="flex items-start gap-2">
                            <Icon name="alert-triangle" size={16} className="text-red-500 mt-0.5 shrink-0" />
                            <div>
                                <p className="text-xs font-bold text-red-600 mb-1">駁回原因</p>
                                <p className="text-sm text-red-700">{review.reject_reason}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* 編輯模式 */}
                {isEditing ? (
                    <div className="space-y-3">
                        {/* 星級評分 */}
                        <div>
                            <p className="text-xs font-bold text-text mb-2">評分</p>
                            <div className="flex gap-1">
                                {[1, 2, 3, 4, 5].map((star) => (
                                    <button
                                        key={star}
                                        onClick={() => setEditRating(star)}
                                        className="p-1"
                                    >
                                        <Icon
                                            name="star"
                                            size={24}
                                            fill={star <= editRating ? COLORS.star : 'none'}
                                            className={star <= editRating ? 'text-star' : 'text-stroke'}
                                        />
                                    </button>
                                ))}
                            </div>
                        </div>
                        {/* 評論內容 */}
                        <div>
                            <p className="text-xs font-bold text-text mb-2">評論內容</p>
                            <textarea
                                value={editComment}
                                onChange={(e) => setEditComment(e.target.value)}
                                placeholder="分享您的租屋體驗..."
                                className="w-full h-24 p-3 border border-stroke/30 rounded-xl text-sm resize-none focus:outline-none focus:border-star"
                            />
                        </div>
                        {/* 操作按鈕 */}
                        <div className="flex gap-2">
                            <button
                                onClick={cancelEdit}
                                className="flex-1 py-2.5 rounded-xl text-sm font-bold text-text border border-stroke/30 hover:bg-land transition-colors"
                            >
                                取消
                            </button>
                            <button
                                onClick={() => saveEdit(review.review_id)}
                                disabled={loading}
                                className="flex-1 py-2.5 rounded-xl text-sm font-bold bg-star text-white hover:bg-star/90 transition-colors disabled:opacity-50"
                            >
                                {loading ? '儲存中...' : '送審'}
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        {/* 顯示模式 - 評分與內容 */}
                        <div className="mb-3">
                            <div className="flex items-center gap-1 mb-2">
                                {[1, 2, 3, 4, 5].map((star) => (
                                    <Icon
                                        key={star}
                                        name="star"
                                        size={16}
                                        fill={star <= review.rating ? COLORS.star : 'none'}
                                        className={star <= review.rating ? 'text-star' : 'text-stroke'}
                                    />
                                ))}
                            </div>
                            {review.comment && (
                                <p className="text-sm text-text/80 line-clamp-3">{review.comment}</p>
                            )}
                        </div>

                        {/* 操作按鈕 */}
                        <div className="flex gap-2">
                            {canEdit && (
                                <button
                                    onClick={() => startEdit(review)}
                                    className="flex-1 py-2 rounded-xl text-sm font-bold text-text border border-stroke/30 hover:bg-land transition-colors flex items-center justify-center gap-1.5"
                                >
                                    <Icon name="edit" size={14} />
                                    編輯
                                </button>
                            )}
                            {canWithdraw && (
                                <button
                                    onClick={() => handleWithdraw(review.review_id)}
                                    disabled={loading}
                                    className="flex-1 py-2 rounded-xl text-sm font-bold text-star border border-star/30 hover:bg-star/10 transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
                                >
                                    <Icon name="rotate-ccw" size={14} />
                                    收回編輯
                                </button>
                            )}
                        </div>
                    </>
                )}
            </div>
        );
    };

    return (
        <div className="h-full bg-land relative overflow-y-auto">
            {/* 返回按鈕 */}
            <button
                onClick={onClose}
                className="absolute top-4 left-4 z-20 w-10 h-10 rounded-full bg-white/90 backdrop-blur shadow-md flex items-center justify-center text-text"
            >
                <Icon name="x" size={20} />
            </button>

            <div className="pt-16 px-5 pb-6">
                <h2 className="text-xl font-bold text-text text-center mb-4">評價管理</h2>

                {/* 狀態篩選 */}
                <div className="flex gap-2 mb-4 overflow-x-auto no-scrollbar pb-1">
                    {(['all', 'approved', 'pending', 'rejected'] as const).map((f) => (
                        <button
                            key={f}
                            onClick={() => setStatusFilter(f)}
                            className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-colors ${
                                statusFilter === f
                                    ? 'bg-text text-land'
                                    : 'bg-white text-text border border-stroke/30'
                            }`}
                        >
                            {f === 'all' ? '全部' : statusConfig[f].label}
                            {f !== 'all' && (
                                <span className="ml-1 opacity-70">
                                    ({reviews.filter(r => r.status === f).length})
                                </span>
                            )}
                        </button>
                    ))}
                </div>

                {/* 評價列表 */}
                {filteredReviews.length === 0 ? (
                    <div className="text-center py-12 text-stroke">
                        <Icon name="message-square" size={48} className="mx-auto mb-3 opacity-50" />
                        <p className="text-sm">
                            {statusFilter === 'all' ? '尚無評價' : `沒有${statusConfig[statusFilter as ReviewStatus].label}的評價`}
                        </p>
                        <p className="text-xs mt-1">在房源詳情頁留下您的評價吧</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filteredReviews.map((review) => (
                            <ReviewCard key={review.review_id} review={review} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReviewsPage;
