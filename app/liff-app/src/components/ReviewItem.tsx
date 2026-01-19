/**
 * 評價項目元件
 * 專案：Chi Soo 租屋小幫手
 */

'use client';

import StarRating from './StarRating';
import type { Review } from '@/lib/api';

interface ReviewItemProps {
    review: Review;
    showStatus?: boolean;
    onDelete?: (reviewId: number) => void;
}

export default function ReviewItem({ review, showStatus = false, onDelete }: ReviewItemProps) {
    const statusColors = {
        pending: 'bg-yellow-100 text-yellow-800',
        approved: 'bg-green-100 text-green-800',
        rejected: 'bg-red-100 text-red-800',
    };

    const statusLabels = {
        pending: '審核中',
        approved: '已發布',
        rejected: '已駁回',
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('zh-TW');
    };

    return (
        <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
            {/* 頭部：評分與狀態 */}
            <div className="flex items-center justify-between mb-2">
                <StarRating rating={review.rating} readonly size="sm" />
                {showStatus && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[review.status]}`}>
                        {statusLabels[review.status]}
                    </span>
                )}
            </div>

            {/* 評論內容 */}
            {review.comment && (
                <p className="text-gray-700 text-sm mb-2">{review.comment}</p>
            )}

            {/* 駁回原因 */}
            {review.status === 'rejected' && review.reject_reason && (
                <div className="bg-red-50 border border-red-200 rounded p-2 mb-2">
                    <p className="text-red-700 text-xs">
                        <span className="font-medium">駁回原因：</span>
                        {review.reject_reason}
                    </p>
                </div>
            )}

            {/* 底部：日期與操作 */}
            <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{formatDate(review.created_at)}</span>
                {onDelete && (
                    <button
                        onClick={() => onDelete(review.review_id)}
                        className="text-red-500 hover:text-red-700 transition"
                    >
                        刪除
                    </button>
                )}
            </div>
        </div>
    );
}
