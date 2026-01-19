/**
 * 照片輪播元件
 * 專案：Chi Soo 租屋小幫手
 */

'use client';

import { useState } from 'react';

interface PhotoCarouselProps {
    images: string[];
    fallbackImage?: string;
}

export default function PhotoCarousel({ images, fallbackImage }: PhotoCarouselProps) {
    const [currentIndex, setCurrentIndex] = useState(0);

    const displayImages = images.length > 0
        ? images
        : [fallbackImage || 'https://via.placeholder.com/800x400/6366F1/FFFFFF?text=No+Image'];

    const goToPrevious = () => {
        setCurrentIndex((prev) => (prev === 0 ? displayImages.length - 1 : prev - 1));
    };

    const goToNext = () => {
        setCurrentIndex((prev) => (prev === displayImages.length - 1 ? 0 : prev + 1));
    };

    return (
        <div className="relative w-full aspect-video bg-gray-100 rounded-lg overflow-hidden">
            {/* 圖片 */}
            <img
                src={displayImages[currentIndex]}
                alt={`照片 ${currentIndex + 1}`}
                className="w-full h-full object-cover"
            />

            {/* 左右箭頭 */}
            {displayImages.length > 1 && (
                <>
                    <button
                        onClick={goToPrevious}
                        className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition"
                    >
                        ◀
                    </button>
                    <button
                        onClick={goToNext}
                        className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition"
                    >
                        ▶
                    </button>
                </>
            )}

            {/* 頁碼指示器 */}
            {displayImages.length > 1 && (
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                    {displayImages.map((_, index) => (
                        <button
                            key={index}
                            onClick={() => setCurrentIndex(index)}
                            className={`w-2 h-2 rounded-full transition ${index === currentIndex ? 'bg-white' : 'bg-white/50'
                                }`}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
