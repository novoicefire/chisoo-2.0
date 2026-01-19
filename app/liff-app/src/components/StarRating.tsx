/**
 * 星等評分元件
 * 專案：Chi Soo 租屋小幫手
 */

'use client';

import { useState } from 'react';

interface StarRatingProps {
    rating: number;
    maxRating?: number;
    readonly?: boolean;
    size?: 'sm' | 'md' | 'lg';
    onChange?: (rating: number) => void;
}

export default function StarRating({
    rating,
    maxRating = 5,
    readonly = false,
    size = 'md',
    onChange,
}: StarRatingProps) {
    const [hoverRating, setHoverRating] = useState(0);

    const sizeClasses = {
        sm: 'text-lg',
        md: 'text-2xl',
        lg: 'text-3xl',
    };

    const handleClick = (value: number) => {
        if (!readonly && onChange) {
            onChange(value);
        }
    };

    const displayRating = hoverRating || rating;

    return (
        <div className="flex gap-1" onMouseLeave={() => setHoverRating(0)}>
            {Array.from({ length: maxRating }, (_, index) => {
                const value = index + 1;
                const isFilled = value <= displayRating;

                return (
                    <button
                        key={index}
                        type="button"
                        disabled={readonly}
                        onClick={() => handleClick(value)}
                        onMouseEnter={() => !readonly && setHoverRating(value)}
                        className={`${sizeClasses[size]} transition ${readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'
                            } ${isFilled ? 'text-yellow-400' : 'text-gray-300'}`}
                    >
                        ★
                    </button>
                );
            })}
        </div>
    );
}
