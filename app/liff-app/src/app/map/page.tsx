/**
 * 地圖搜尋頁面
 * 專案：Chi Soo 租屋小幫手
 * 路由：/map
 */

'use client';

import { Suspense } from 'react';
import dynamic from 'next/dynamic';

// 動態載入地圖元件 (避免 SSR 問題)
const MapContent = dynamic(() => import('./MapContent'), {
    ssr: false,
    loading: () => (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
        </div>
    ),
});

export default function MapPage() {
    return (
        <Suspense
            fallback={
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
                </div>
            }
        >
            <MapContent />
        </Suspense>
    );
}
