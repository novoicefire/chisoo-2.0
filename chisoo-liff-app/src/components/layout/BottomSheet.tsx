/**
 * Chi．Soo 暨宿 - BottomSheet 元件
 * 可拖曳的底部面板
 */

import React, { useEffect } from 'react';
import { motion, useAnimation, useDragControls } from 'framer-motion';
import Icon from '../ui/Icon';
import PropertyDetails from '../features/PropertyDetails';
import FavoritesPage from '../features/FavoritesPage';
import ReviewsPage from '../features/ReviewsPage';
import GuideCarousel from '../features/GuideCarousel';
import AboutContent from '../features/AboutContent';
import type { Property, FavoriteItem, VerificationStatus, SheetState, UserReview } from '../../types';
import { COLORS } from '../../types';

interface BottomSheetProps {
    snapState: SheetState;
    setSnapState: (state: SheetState) => void;
    selectedProperty: Property | null;
    setSelectedProp: (prop: Property | null) => void;
    onClearSelection: () => void;
    status: VerificationStatus;
    openVerification: () => void;
    showAbout: boolean;
    setShowAbout: (show: boolean) => void;
    showFavorites: boolean;
    setShowFavorites: (show: boolean) => void;
    favorites: FavoriteItem[];
    setFavorites: (favorites: FavoriteItem[]) => void;
    isFavorite: (id: string | number) => boolean;
    toggleFavorite: (property: Property) => void;
    favoritesTab: 'homes' | 'life';
    currentList: Property[];
    setToast: (msg: string | null) => void;
    // 評價管理
    showReviews: boolean;
    setShowReviews: (show: boolean) => void;
    userReviews: UserReview[];
    onUpdateReview: (reviewId: number, data: { rating: number; comment: string }) => Promise<boolean>;
    onWithdrawReview: (reviewId: number) => Promise<boolean>;
    onRefreshReviews: () => void;
}

export const BottomSheet: React.FC<BottomSheetProps> = ({
    snapState,
    setSnapState,
    selectedProperty,
    setSelectedProp,
    onClearSelection,
    status,
    openVerification,
    showAbout,
    setShowAbout,
    showFavorites,
    setShowFavorites,
    favorites,
    setFavorites,
    isFavorite,
    toggleFavorite,
    favoritesTab,
    currentList,
    setToast,
    showReviews,
    setShowReviews,
    userReviews,
    onUpdateReview,
    onWithdrawReview,
    onRefreshReviews,
}) => {
    const controls = useAnimation();
    const dragControls = useDragControls();

    const variants = {
        peek: { y: '85vh' },
        half: { y: '55vh' },
        full: { y: '0vh' },
    };

    useEffect(() => {
        controls.start(snapState);
    }, [snapState, controls]);

    const handleDragEnd = (_event: MouseEvent | TouchEvent | PointerEvent, info: { point: { y: number }; velocity: { y: number } }) => {
        const velocity = info.velocity.y;
        const currentY = info.point.y;
        const windowHeight = window.innerHeight;
        
        // 將目前 Y 座標轉換為視窗高度百分比 (0-100)
        const currentVh = (currentY / windowHeight) * 100;

        // 定義錨點 (對應 styles 中的 vh 值)
        const anchors = {
            full: 0,
            half: 55,
            peek: 85
        };

        // 快速滑動判定 (Velocity-based)
        if (Math.abs(velocity) > 500) {
            if (velocity < 0) {
                // 向上滑
                if (snapState === 'peek') setSnapState('half');
                else if (snapState === 'half') setSnapState('full');
                else controls.start('full');
            } else {
                // 向下滑
                if (snapState === 'full') setSnapState('half');
                else if (snapState === 'half') setSnapState('peek');
                else controls.start('peek');
            }
        } else {
            // 慢速拖曳位置判定 (Position-based)
            // 找出距離目前位置最近的錨點
            const distFull = Math.abs(currentVh - anchors.full);
            const distHalf = Math.abs(currentVh - anchors.half);
            const distPeek = Math.abs(currentVh - anchors.peek);

            if (distFull < distHalf && distFull < distPeek) {
                setSnapState('full');
            } else if (distHalf < distPeek) {
                setSnapState('half');
            } else {
                setSnapState('peek');
            }
        }
    };

    return (
        <motion.div
            drag="y"
            dragControls={dragControls}
            dragListener={false}
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.05}
            onDragEnd={handleDragEnd}
            animate={controls}
            variants={variants}
            initial="peek"
            transition={{ type: 'spring', damping: 32, stiffness: 300 }}
            className={`fixed bottom-0 left-0 right-0 z-30 w-full h-dvh rounded-t-[24px] shadow-[0_-8px_30px_rgba(78,60,46,0.15)] overflow-hidden flex flex-col bg-land ${snapState === 'full' ? 'rounded-t-none' : ''
                }`}
        >
            {/* 拖曳手柄 */}
            <div
                onPointerDown={(e) => dragControls.start(e)}
                className={`w-full flex justify-center shrink-0 cursor-grab active:cursor-grabbing touch-none z-40 bg-land transition-all ${snapState === 'full' && (selectedProperty || showAbout || showFavorites || showReviews)
                        ? 'absolute top-0 opacity-0 pointer-events-none'
                        : 'pt-3 pb-2'
                    }`}
            >
                <div className="w-10 h-[5px] rounded-full bg-stroke" />
            </div>

            {/* 內容區 */}
            <div className="flex-1 overflow-y-auto overscroll-contain bg-land">
                {showAbout ? (
                    <AboutContent onClose={() => setShowAbout(false)} />
                ) : showFavorites ? (
                    <FavoritesPage
                        onClose={() => setShowFavorites(false)}
                        favorites={favorites}
                        onRemove={(id) => setFavorites(favorites.filter((f) => String(f.id) !== String(id)))}
                        onUpdateStatus={(id, newStatus) =>
                            setFavorites(
                                favorites.map((f) => (String(f.id) === String(id) ? { ...f, status: newStatus } : f))
                            )
                        }
                        onSelect={(item) => {
                            setSelectedProp(item);
                            setShowFavorites(false);
                            setSnapState('half');
                        }}
                        onToast={(msg) => {
                            setToast(msg);
                            setTimeout(() => setToast(null), 2500);
                        }}
                        initialTab={favoritesTab}
                    />
                ) : showReviews ? (
                    <ReviewsPage
                        onClose={() => setShowReviews(false)}
                        reviews={userReviews}
                        onUpdate={onUpdateReview}
                        onWithdraw={onWithdrawReview}
                        onRefresh={onRefreshReviews}
                        onToast={(msg) => {
                            setToast(msg);
                            setTimeout(() => setToast(null), 2500);
                        }}
                    />
                ) : selectedProperty ? (
                    <PropertyDetails
                        property={selectedProperty}
                        onBack={onClearSelection}
                        status={status}
                        openVerification={openVerification}
                        isFavorite={isFavorite(selectedProperty.id)}
                        onToggleFavorite={() => toggleFavorite(selectedProperty)}
                    />
                ) : (
                    <div className="px-5 pb-safe-bottom pt-2">
                        {/* 標題 */}
                        <div className="text-center py-2 mb-4">
                            <p className="font-bold text-lg tracking-wide text-text">
                                探索周邊 {currentList.length} 間房源
                            </p>
                        </div>

                        <h4 className="text-sm font-bold opacity-60 mb-3 text-text">
                            精選推薦
                        </h4>

                        {/* 卡片輪播 */}
                        <div className="flex gap-4 overflow-x-auto pb-4 -mx-5 px-5 snap-x no-scrollbar">
                            {currentList.map((p) => {
                                const fav = favorites.find((f) => String(f.id) === String(p.id));
                                return (
                                    <div
                                        key={String(p.id)}
                                        onClick={() => {
                                            setSelectedProp(p);
                                            setSnapState('half');
                                        }}
                                        className="shrink-0 w-[260px] rounded-[20px] overflow-hidden bg-white shadow-sm snap-center border border-stroke/20 relative group"
                                    >
                                        <div className="h-36 relative overflow-hidden">
                                            <img
                                                src={p.images[0]}
                                                className="w-full h-full object-cover sepia-[0.1] contrast-[0.95]"
                                                alt={p.title}
                                            />
                                            <div className="absolute inset-0 bg-linear-to-t from-text/90 to-transparent opacity-80" />
                                            <div className="absolute top-3 left-3 w-8 h-8 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-sm">
                                                <Icon
                                                    name="heart"
                                                    size={16}
                                                    fill={fav ? '#e69a4d' : 'none'}
                                                    className={fav ? 'text-star' : 'text-stroke'}
                                                />
                                            </div>
                                            <div className="absolute bottom-3 left-3 text-land">
                                                <h5 className="font-bold text-lg leading-tight">{p.title}</h5>
                                                <p className="text-xs opacity-90 font-medium mt-0.5">{p.price}</p>
                                            </div>
                                            <div className="absolute top-3 right-3 bg-land/90 backdrop-blur-sm px-2 py-1 rounded-lg text-[10px] font-bold text-text flex items-center shadow-sm">
                                                <Icon name="star" size={10} fill={COLORS.text} className="mr-0.5" />
                                                {p.rating}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* 指南輪播 */}
                        <div className="pt-4 space-y-4">
                            <div className="h-px w-full bg-stroke/30" />
                            <p className="text-sm opacity-60 text-center text-text mb-2">繼續探索更多...</p>
                            <GuideCarousel />
                            <div className="h-20" />
                        </div>
                    </div>
                )}
            </div>
        </motion.div>
    );
};

export default BottomSheet;
