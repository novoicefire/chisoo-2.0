/**
 * Chi．Soo 暨宿 - 收藏頁面元件
 */

import React, { useState } from 'react';
import Icon from '../ui/Icon';
import type { FavoriteItem, FavoriteStatus, Property } from '../../types';

interface FavoritesPageProps {
    onClose: () => void;
    favorites: FavoriteItem[];
    onRemove: (id: string | number) => void;
    onUpdateStatus: (id: string | number, status: FavoriteStatus) => void;
    onSelect: (item: Property) => void;
    onToast: (msg: string) => void;
    initialTab?: 'homes' | 'life';
}

const statusLabels: Record<FavoriteStatus, string> = {
    saved: '待預約',
    visited: '已看完房',
    contacting: '聯繫中',
};

const statusColors: Record<FavoriteStatus, string> = {
    saved: 'bg-stroke/20 text-stroke',
    visited: 'bg-star/20 text-star',
    contacting: 'bg-text/10 text-text',
};

export const FavoritesPage: React.FC<FavoritesPageProps> = ({
    onClose,
    favorites,
    onRemove,
    onUpdateStatus,
    onSelect,
    onToast,
    initialTab = 'homes',
}) => {
    const [activeTab, setActiveTab] = useState<'homes' | 'life'>(initialTab);
    const [statusFilter, setStatusFilter] = useState<FavoriteStatus | 'all'>('all');

    const housingFavorites = favorites.filter((f) => f.type === 'housing');
    const placeFavorites = favorites.filter((f) => f.type === 'place' || f.type === 'event');

    const HousingCard: React.FC<{ item: FavoriteItem }> = ({ item }) => (
        <div
            onClick={() => onSelect(item)}
            className="bg-white rounded-2xl p-4 shadow-sm border border-stroke/20 cursor-pointer active:scale-[0.98] transition-transform"
        >
            <div className="flex gap-3 items-stretch relative">
                <img src={item.images[0]} className="w-24 h-24 rounded-xl object-cover shrink-0" alt="" />
                <div className="flex-1 min-w-0 flex flex-col justify-center">
                    <h3 className="font-bold text-text truncate pr-2">{item.title}</h3>
                    <p className="text-lg text-star font-bold mt-0.5">{item.price}</p>
                    <p className="text-xs text-stroke truncate mt-1">{item.address}</p>
                    <div className="flex items-center gap-2 mt-1.5">
                        <span className="flex items-center gap-1 text-xs text-text/70">
                            <Icon name="star" size={12} fill="#e69a4d" className="text-star" />
                            {item.rating}
                        </span>
                        {item.tags?.slice(0, 2).map((t) => (
                            <span key={t} className="text-[10px] bg-text/10 text-text px-1.5 py-0.5 rounded-full">
                                {t}
                            </span>
                        ))}
                    </div>
                </div>
                <div className="flex flex-col justify-center items-end shrink-0">
                    <select
                        value={item.status}
                        onChange={(e) => {
                            e.stopPropagation();
                            onUpdateStatus(item.id, e.target.value as FavoriteStatus);
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className={`px-3 py-1.5 rounded-full text-xs font-bold border-0 cursor-pointer min-w-[80px] text-center ${statusColors[item.status]}`}
                    >
                        <option value="saved">{statusLabels.saved}</option>
                        <option value="contacting">{statusLabels.contacting}</option>
                        <option value="visited">{statusLabels.visited}</option>
                    </select>
                </div>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemove(item.id);
                        onToast('已從收藏移除');
                    }}
                    className="absolute -top-2 -right-2 w-7 h-7 bg-stroke/40 rounded-full shadow-md flex items-center justify-center text-text hover:text-red-500 hover:bg-stroke/60 transition-colors"
                >
                    <Icon name="x" size={14} />
                </button>
            </div>
        </div>
    );

    const PlaceCard: React.FC<{ item: FavoriteItem }> = ({ item }) => (
        <div
            onClick={() => onSelect(item)}
            className="bg-gradient-to-br from-white to-land/50 rounded-2xl p-4 shadow-sm border border-star/30 cursor-pointer active:scale-[0.98] transition-transform"
        >
            <div className="flex gap-3 items-stretch relative">
                <div className="w-24 h-24 rounded-xl overflow-hidden relative shrink-0">
                    <img src={item.images[0]} className="w-full h-full object-cover" alt="" />
                    <div className="absolute inset-0 bg-gradient-to-t from-text/60 to-transparent" />
                    <div className="absolute bottom-2 left-2">
                        <Icon name="coffee" size={16} className="text-white" />
                    </div>
                </div>
                <div className="flex-1 min-w-0 flex flex-col justify-center">
                    <h3 className="font-bold text-text truncate pr-2">{item.title}</h3>
                    <span className="inline-flex items-center gap-1 text-[10px] bg-star/20 text-star px-2 py-0.5 rounded-full mt-1 w-max">
                        <Icon name="coffee" size={10} /> 讀書聖地
                    </span>
                    <p className="text-sm text-text/80 mt-1 line-clamp-2">{item.desc?.slice(0, 40)}...</p>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="flex items-center gap-1 text-xs text-text/70">
                            <Icon name="star" size={12} fill="#e69a4d" className="text-star" />
                            {item.rating}
                        </span>
                        {item.price && <span className="text-xs text-text/70">{item.price}</span>}
                    </div>
                </div>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onRemove(item.id);
                        onToast('已從收藏移除');
                    }}
                    className="absolute -top-2 -right-2 w-7 h-7 bg-star/30 rounded-full shadow-md flex items-center justify-center text-star hover:text-red-500 hover:bg-star/50 transition-colors"
                >
                    <Icon name="x" size={14} />
                </button>
            </div>
        </div>
    );

    return (
        <div className="h-full bg-land relative overflow-y-auto">
            <button
                onClick={onClose}
                className="absolute top-4 left-4 z-20 w-10 h-10 rounded-full bg-white/90 backdrop-blur shadow-md flex items-center justify-center text-text"
            >
                <Icon name="x" size={20} />
            </button>

            <div className="pt-16 px-5 pb-6">
                <h2 className="text-xl font-bold text-text text-center mb-4">我的收藏</h2>

                {/* Tab 切換 */}
                <div className="flex gap-2 mb-4 bg-white/50 p-1 rounded-2xl">
                    <button
                        onClick={() => setActiveTab('homes')}
                        className={`flex-1 py-2.5 rounded-xl text-sm font-bold transition-colors ${activeTab === 'homes' ? 'bg-text text-land shadow-md' : 'text-text/60 hover:text-text'
                            }`}
                    >
                        <Icon name="home" size={16} className="inline mr-1.5" />
                        找房清單
                        <span className="ml-1.5 text-xs opacity-70">({housingFavorites.length})</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('life')}
                        className={`flex-1 py-2.5 rounded-xl text-sm font-bold transition-colors ${activeTab === 'life' ? 'bg-star text-white shadow-md' : 'text-text/60 hover:text-text'
                            }`}
                    >
                        <Icon name="briefcase" size={16} className="inline mr-1.5" />
                        生活口袋
                        <span className="ml-1.5 text-xs opacity-70">({placeFavorites.length})</span>
                    </button>
                </div>

                {activeTab === 'homes' ? (
                    housingFavorites.length === 0 ? (
                        <div className="text-center py-12 text-stroke">
                            <Icon name="home" size={48} className="mx-auto mb-3 opacity-50" />
                            <p className="text-sm">找房清單是空的</p>
                            <p className="text-xs mt-1">收藏房源來比較租金與坪數</p>
                        </div>
                    ) : (
                        <>
                            {/* 狀態篩選 */}
                            <div className="flex gap-2 mb-3 overflow-x-auto no-scrollbar pb-1">
                                {(['all', 'saved', 'contacting', 'visited'] as const).map((f) => (
                                    <button
                                        key={f}
                                        onClick={() => setStatusFilter(f)}
                                        className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-colors ${statusFilter === f
                                            ? 'bg-text text-land'
                                            : 'bg-white text-text border border-stroke/30'
                                            }`}
                                    >
                                        {f === 'all' ? '全部' : statusLabels[f]}
                                    </button>
                                ))}
                            </div>
                            <div className="space-y-3">
                                {housingFavorites
                                    .filter((f) => statusFilter === 'all' || f.status === statusFilter)
                                    .map((item) => (
                                        <HousingCard key={String(item.id)} item={item} />
                                    ))}
                            </div>
                        </>
                    )
                ) : placeFavorites.length === 0 ? (
                    <div className="text-center py-12 text-stroke">
                        <Icon name="coffee" size={48} className="mx-auto mb-3 opacity-50" />
                        <p className="text-sm">生活口袋是空的</p>
                        <p className="text-xs mt-1">收藏咖啡廳、活動來探索山城生活</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {placeFavorites.map((item) => (
                            <PlaceCard key={String(item.id)} item={item} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default FavoritesPage;
