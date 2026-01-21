/**
 * Chi．Soo 暨宿 - 房源詳情頁元件
 */

import React, { useState } from 'react';
import Icon from '../ui/Icon';
import CommuteInfo from './CommuteInfo';
import type { Property, VerificationStatus } from '../../types';
import { COLORS } from '../../types';

interface PropertyDetailsProps {
    property: Property | null;
    onBack: () => void;
    status: VerificationStatus;
    openVerification: () => void;
    isFavorite: boolean;
    onToggleFavorite: () => void;
}

export const PropertyDetails: React.FC<PropertyDetailsProps> = ({
    property,
    onBack,
    status,
    openVerification,
    isFavorite,
    onToggleFavorite,
}) => {
    const [reviewText, setReviewText] = useState('');

    if (!property) return null;

    const isHousing = property.type === 'housing';

    const handleReviewSubmit = () => {
        if (!reviewText.trim()) return;
        console.log('提交評論:', reviewText);
        setReviewText('');
        alert('評論已提交！');
    };

    return (
        <div className="flex flex-col min-h-full">
            {/* 圖片輪播 */}
            <div className="relative w-full h-64 shrink-0 bg-gray-100">
                <div className="absolute top-4 left-4 z-20">
                    <button
                        onClick={onBack}
                        className="w-10 h-10 rounded-full bg-white/90 backdrop-blur shadow-md flex items-center justify-center text-text"
                    >
                        <Icon name="back" size={20} />
                    </button>
                </div>
                <div className="flex overflow-x-auto snap-x no-scrollbar w-full h-full">
                    {property.images.map((img, i) => (
                        <div key={i} className="w-full shrink-0 snap-center h-full relative">
                            <img src={img} className="w-full h-full object-cover sepia-[0.15] contrast-[0.95]" alt="" />
                            <div className="absolute inset-0 bg-gradient-to-t from-text/90 to-transparent opacity-60" />
                        </div>
                    ))}
                </div>
            </div>

            {/* 標題資訊 */}
            <div className="px-5 pt-5 pb-4">
                <h2 className="text-2xl font-bold mb-1 text-text">{property.title}</h2>
                <div className="flex items-center gap-1.5 text-sm mb-1">
                    <span className="font-bold flex items-center text-text">
                        {property.rating}
                        <Icon name="star" size={12} fill={COLORS.star} className="text-star ml-0.5" />
                    </span>
                    <span className="text-stroke">({property.ratingCount || 0})</span>
                </div>
                {property.tags && <p className="text-sm text-text/80 mt-1">{property.tags.join(' · ')}</p>}
            </div>

            {/* 操作按鈕 */}
            <div className="flex justify-between px-6 pb-6 border-b border-stroke/20">
                {[{ icon: 'nav', label: '導航' }, { icon: 'phone', label: '通話' }].map((btn, idx) => (
                    <button key={idx} className="flex flex-col items-center gap-1.5 active:scale-95 transition-transform">
                        <div className="w-12 h-12 rounded-full border border-stroke flex items-center justify-center text-text hover:bg-text hover:text-land transition-colors shadow-sm bg-white">
                            <Icon name={btn.icon} size={20} />
                        </div>
                        <span className="text-xs font-medium text-text">{btn.label}</span>
                    </button>
                ))}
                <button
                    onClick={onToggleFavorite}
                    className="flex flex-col items-center gap-1.5 active:scale-95 transition-transform"
                >
                    <div
                        className={`w-12 h-12 rounded-full border flex items-center justify-center transition-colors shadow-sm ${isFavorite ? 'border-star bg-star/10' : 'border-stroke bg-white hover:bg-text hover:text-land'
                            }`}
                    >
                        <Icon name="heart" size={20} fill={isFavorite ? '#e69a4d' : 'none'} className={isFavorite ? 'text-star' : ''} />
                    </div>
                    <span className={`text-xs font-medium ${isFavorite ? 'text-star' : 'text-text'}`}>
                        {isFavorite ? '已收藏' : '收藏'}
                    </span>
                </button>
                <button className="flex flex-col items-center gap-1.5 active:scale-95 transition-transform">
                    <div className="w-12 h-12 rounded-full border border-stroke flex items-center justify-center text-text hover:bg-text hover:text-land transition-colors shadow-sm bg-white">
                        <Icon name="share-2" size={20} />
                    </div>
                    <span className="text-xs font-medium text-text">分享</span>
                </button>
            </div>

            {/* 描述 */}
            <div className="px-5 py-6 space-y-4 border-b border-stroke/20">
                <p className="leading-relaxed text-text text-sm opacity-90">{property.desc || '暫無簡介'}</p>
                <div className="flex items-start gap-4 text-sm text-text">
                    <Icon name="mapPin" size={20} className="shrink-0 opacity-70 mt-0.5" />
                    <span>{property.address || '埔里鎮'}</span>
                </div>
                <div className="flex items-start gap-4 text-sm text-text">
                    <Icon name="clock" size={20} className="shrink-0 opacity-70 mt-0.5" />
                    <span>{property.price || '營業時間依店家規定'}</span>
                </div>
            </div>

            {/* 通勤資訊 */}
            {property.lng && property.lat && <CommuteInfo property={property} title={property.title} isHousing={isHousing} />}

            {/* 評價區 */}
            <div className="px-5 py-6 bg-white/30">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-lg text-text">評價</h3>
                    <span className="text-xs font-bold text-text opacity-60">查看全部 {property.ratingCount || 0} 則</span>
                </div>

                {/* 評論輸入區 */}
                {status === 'verified' ? (
                    <div className="mb-6 p-4 bg-white rounded-xl shadow-sm border border-stroke/20">
                        <div className="flex items-center gap-2 mb-3">
                            <div className="w-8 h-8 rounded-full bg-land flex items-center justify-center text-text font-bold text-xs">
                                Me
                            </div>
                            <span className="text-sm font-bold text-text">LINE User</span>
                            <span className="text-[10px] bg-star/10 text-star px-1.5 py-0.5 rounded ml-auto flex items-center gap-1">
                                <Icon name="check" size={10} /> 已驗證
                            </span>
                        </div>
                        <div className="flex gap-1 mb-3">
                            {[1, 2, 3, 4, 5].map((i) => (
                                <Icon
                                    key={i}
                                    name="star"
                                    size={16}
                                    className="text-stroke hover:text-star cursor-pointer transition-colors"
                                />
                            ))}
                        </div>
                        <div className="relative">
                            <textarea
                                value={reviewText}
                                onChange={(e) => setReviewText(e.target.value)}
                                placeholder="分享你的心得..."
                                className="w-full h-24 p-3 bg-gray-50 rounded-lg text-sm text-text outline-none border border-transparent focus:border-text/30 resize-none pr-10"
                            />
                            <button className="absolute bottom-3 left-3 text-text/50 hover:text-text">
                                <Icon name="camera" size={20} />
                            </button>
                            <button
                                onClick={handleReviewSubmit}
                                className="absolute bottom-3 right-3 w-8 h-8 bg-text rounded-full flex items-center justify-center text-white shadow-md active:scale-90 transition-transform"
                            >
                                <Icon name="send" size={14} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div
                        onClick={openVerification}
                        className="mb-6 p-5 bg-white rounded-xl shadow-sm border-2 border-dashed border-stroke/50 flex flex-col items-center text-center cursor-pointer hover:bg-land/30 transition-colors"
                    >
                        <div className="w-12 h-12 bg-stroke/10 rounded-full flex items-center justify-center text-text mb-2">
                            <Icon name={status === 'pending' ? 'time' : 'lock'} size={24} />
                        </div>
                        <h4 className="font-bold text-text text-sm mb-1">
                            {status === 'pending' ? '身份審核中' : '驗證學生身份以解鎖'}
                        </h4>
                        <p className="text-xs text-stroke mb-3">
                            {status === 'pending' ? '請耐心等候，通過後即可評價' : '僅限暨大在校生評論與分享照片'}
                        </p>
                        {status !== 'pending' && (
                            <button className="px-4 py-1.5 bg-text text-land rounded-full text-xs font-bold">前往驗證</button>
                        )}
                    </div>
                )}

                {/* 評論列表 */}
                <div className="space-y-4">
                    {property.reviews && property.reviews.length > 0 ? (
                        property.reviews.map((review, i) => (
                            <div key={i} className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-stroke flex items-center justify-center text-white text-xs font-bold shrink-0">
                                    {review.name.charAt(0)}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-0.5">
                                        <span className="text-sm font-bold text-text">{review.name}</span>
                                        <span className="text-xs text-stroke">{review.time}</span>
                                    </div>
                                    <div className="flex mb-1">
                                        {[...Array(5)].map((_, starI) => (
                                            <Icon
                                                key={starI}
                                                name="star"
                                                size={10}
                                                fill={starI < review.rating ? COLORS.star : 'none'}
                                                className={starI < review.rating ? 'text-star' : 'text-stroke'}
                                            />
                                        ))}
                                    </div>
                                    <p className="text-sm text-text leading-snug opacity-90">{review.text}</p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="text-sm text-stroke text-center py-2">尚無文字評價</p>
                    )}
                </div>
            </div>

            {/* 底部安全區域 */}
            <div className="h-safe-bottom bg-transparent" />
        </div>
    );
};

export default PropertyDetails;
