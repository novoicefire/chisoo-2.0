/**
 * 評價系統頁面
 * 專案：Chi Soo 租屋小幫手
 * 路由：/review
 */

'use client';

import { Suspense } from 'react';
import dynamic from 'next/dynamic';

// 動態載入評價內容元件 (避免 SSR 問題)
const ReviewContent = dynamic(() => import('./ReviewContent'), {
    ssr: false,
    loading: () => (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
        </div>
    ),
});

export default function ReviewPage() {
    return (
        <Suspense
            fallback={
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
                </div>
            }
        >
            <ReviewContent />
        </Suspense>
    );
}
