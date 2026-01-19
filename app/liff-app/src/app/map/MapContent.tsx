/**
 * 地圖搜尋內容元件
 * 專案：Chi Soo 租屋小幫手
 */

'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import StarRating from '@/components/StarRating';
import { getHouses, type House } from '@/lib/api';
import { initLiff } from '@/lib/liff';

// 暨大座標
const NCNU_LOCATION = { lat: 23.9576, lng: 120.9277 };

// 埔里中心
const PULI_CENTER = { lat: 23.9659, lng: 120.9682 };

// 動態載入 Google Maps Script
function loadGoogleMapsScript(apiKey: string): Promise<void> {
    return new Promise((resolve, reject) => {
        if (typeof google !== 'undefined' && google.maps) {
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}`;
        script.async = true;
        script.defer = true;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('Google Maps 載入失敗'));
        document.head.appendChild(script);
    });
}

export default function MapContent() {
    const searchParams = useSearchParams();
    const preselectedHouseId = searchParams.get('house_id');

    const mapRef = useRef<HTMLDivElement>(null);
    const googleMapRef = useRef<google.maps.Map | null>(null);
    const markersRef = useRef<google.maps.Marker[]>([]);

    const [houses, setHouses] = useState<House[]>([]);
    const [loading, setLoading] = useState(true);
    const [mapReady, setMapReady] = useState(false);
    const [selectedHouse, setSelectedHouse] = useState<House | null>(null);
    const [showDetail, setShowDetail] = useState(false);

    // 篩選條件
    const [searchQuery, setSearchQuery] = useState('');
    const [maxRent, setMaxRent] = useState<number | null>(null);
    const [roomType, setRoomType] = useState<string | null>(null);
    const [showFilters, setShowFilters] = useState(false);

    // 初始化 LIFF 和載入資料
    useEffect(() => {
        async function init() {
            try {
                await initLiff();
            } catch (e) {
                console.error('LIFF 初始化失敗', e);
            }

            try {
                const data = await getHouses({ limit: 100 });
                setHouses(data.houses);
            } catch (e) {
                console.error('載入房源失敗', e);
            } finally {
                setLoading(false);
            }
        }

        init();
    }, []);

    // 初始化 Google Maps
    useEffect(() => {
        if (!mapRef.current || houses.length === 0) return;

        const initMap = async () => {
            try {
                const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '';
                await loadGoogleMapsScript(apiKey);

                if (!mapRef.current) return;

                const map = new google.maps.Map(mapRef.current, {
                    center: PULI_CENTER,
                    zoom: 14,
                    styles: [
                        { featureType: 'poi', stylers: [{ visibility: 'off' }] },
                    ],
                    mapTypeControl: false,
                    streetViewControl: false,
                    fullscreenControl: false,
                });

                googleMapRef.current = map;
                setMapReady(true);

                // 暨大標記
                new google.maps.Marker({
                    position: NCNU_LOCATION,
                    map,
                    title: '國立暨南國際大學',
                    icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                    },
                });

                // 如果有預選房源
                if (preselectedHouseId) {
                    const house = houses.find(
                        (h) => h.house_id === Number(preselectedHouseId)
                    );
                    if (house && house.latitude && house.longitude) {
                        map.panTo({ lat: house.latitude, lng: house.longitude });
                        map.setZoom(16);
                        setSelectedHouse(house);
                        setShowDetail(true);
                    }
                }
            } catch (e) {
                console.error('Google Maps 初始化失敗', e);
            }
        };

        initMap();
    }, [houses, preselectedHouseId]);

    // 更新標記
    const updateMarkers = useCallback(() => {
        if (!googleMapRef.current || !mapReady) return;

        // 清除現有標記
        markersRef.current.forEach((marker) => marker.setMap(null));
        markersRef.current = [];

        // 篩選房源
        const filteredHouses = houses.filter((house) => {
            if (!house.latitude || !house.longitude) return false;
            if (searchQuery && !house.name.toLowerCase().includes(searchQuery.toLowerCase())) {
                return false;
            }
            if (maxRent && house.rent > maxRent) return false;
            if (roomType && house.room_type !== roomType) return false;
            return true;
        });

        // 建立新標記
        filteredHouses.forEach((house) => {
            const marker = new google.maps.Marker({
                position: { lat: house.latitude!, lng: house.longitude! },
                map: googleMapRef.current!,
                title: house.name,
                icon: {
                    url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
                },
            });

            marker.addListener('click', () => {
                googleMapRef.current?.panTo({ lat: house.latitude!, lng: house.longitude! });
                setSelectedHouse(house);
                setShowDetail(false);
            });

            markersRef.current.push(marker);
        });
    }, [houses, searchQuery, maxRent, roomType, mapReady]);

    // 當篩選條件改變時更新標記
    useEffect(() => {
        updateMarkers();
    }, [updateMarkers]);

    // 定位到暨大
    const goToNCNU = () => {
        googleMapRef.current?.panTo(NCNU_LOCATION);
        googleMapRef.current?.setZoom(15);
    };

    // 定位到我的位置
    const goToMyLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };
                    googleMapRef.current?.panTo(pos);
                    googleMapRef.current?.setZoom(16);
                },
                () => {
                    alert('無法取得位置');
                }
            );
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent" />
            </div>
        );
    }

    return (
        <div className="h-screen flex flex-col relative">
            {/* 頂部搜尋欄 */}
            <div className="absolute top-0 left-0 right-0 z-10 p-2 bg-white/90 backdrop-blur border-b">
                <div className="flex gap-2">
                    <input
                        type="text"
                        placeholder="搜尋房源..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="flex-1 px-3 py-2 border rounded-lg text-sm"
                    />
                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition ${showFilters ? 'bg-indigo-500 text-white' : 'bg-gray-100'
                            }`}
                    >
                        篩選
                    </button>
                </div>

                {/* 篩選選項 */}
                {showFilters && (
                    <div className="flex gap-2 mt-2 flex-wrap">
                        <select
                            value={maxRent || ''}
                            onChange={(e) => setMaxRent(e.target.value ? Number(e.target.value) : null)}
                            className="px-3 py-1 border rounded-lg text-sm"
                        >
                            <option value="">租金不限</option>
                            <option value="3000">3000 以下</option>
                            <option value="5000">5000 以下</option>
                            <option value="8000">8000 以下</option>
                        </select>
                        <select
                            value={roomType || ''}
                            onChange={(e) => setRoomType(e.target.value || null)}
                            className="px-3 py-1 border rounded-lg text-sm"
                        >
                            <option value="">房型不限</option>
                            <option value="套房">套房</option>
                            <option value="雅房">雅房</option>
                            <option value="整層">整層</option>
                        </select>
                    </div>
                )}
            </div>

            {/* 地圖 */}
            <div ref={mapRef} className="flex-1 w-full" />

            {/* FAB 按鈕 */}
            <div className="absolute right-4 bottom-40 flex flex-col gap-2">
                <button
                    onClick={goToMyLocation}
                    className="w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center text-xl hover:bg-gray-50 transition"
                    title="我的位置"
                >
                    📍
                </button>
                <button
                    onClick={goToNCNU}
                    className="w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center text-xl hover:bg-gray-50 transition"
                    title="暨大"
                >
                    🏫
                </button>
            </div>

            {/* Bottom Sheet - 摘要卡 */}
            {selectedHouse && !showDetail && (
                <div
                    className="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-2xl p-4 cursor-pointer transition-transform"
                    onClick={() => setShowDetail(true)}
                >
                    <div className="w-12 h-1 bg-gray-300 rounded-full mx-auto mb-3" />
                    <div className="flex gap-3">
                        <img
                            src={selectedHouse.image_url || 'https://via.placeholder.com/100x100'}
                            alt={selectedHouse.name}
                            className="w-20 h-20 rounded-lg object-cover"
                        />
                        <div className="flex-1">
                            <h3 className="font-bold text-gray-900">{selectedHouse.name}</h3>
                            <div className="flex items-center gap-2 text-sm text-gray-600 mt-1">
                                <StarRating rating={selectedHouse.avg_rating} readonly size="sm" />
                                <span>({selectedHouse.review_count})</span>
                            </div>
                            <p className="text-indigo-600 font-medium mt-1">
                                ${selectedHouse.rent.toLocaleString()}/月
                            </p>
                        </div>
                    </div>
                    <p className="text-center text-xs text-gray-400 mt-2">點擊查看詳情 ↑</p>
                </div>
            )}

            {/* Detail Modal */}
            {selectedHouse && showDetail && (
                <div className="absolute inset-0 bg-white z-20 overflow-y-auto">
                    {/* 關閉按鈕 */}
                    <button
                        onClick={() => {
                            setShowDetail(false);
                            setSelectedHouse(null);
                        }}
                        className="absolute top-4 left-4 z-30 w-10 h-10 bg-black/50 text-white rounded-full flex items-center justify-center"
                    >
                        ✕
                    </button>

                    {/* 圖片 */}
                    <div className="h-48 bg-gray-200">
                        <img
                            src={selectedHouse.image_url || 'https://via.placeholder.com/800x400'}
                            alt={selectedHouse.name}
                            className="w-full h-full object-cover"
                        />
                    </div>

                    {/* 內容 */}
                    <div className="p-4">
                        <div className="flex items-start justify-between mb-2">
                            <h1 className="text-xl font-bold">{selectedHouse.name}</h1>
                            <span className="bg-indigo-500 text-white px-3 py-1 rounded-full text-sm">
                                ${selectedHouse.rent.toLocaleString()}/月
                            </span>
                        </div>

                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                            <StarRating rating={selectedHouse.avg_rating} readonly size="sm" />
                            <span>({selectedHouse.review_count} 評價)</span>
                            <span>|</span>
                            <span>{selectedHouse.room_type || '套房'}</span>
                        </div>

                        {selectedHouse.description && (
                            <p className="text-gray-600 text-sm mb-4">
                                {selectedHouse.description}
                            </p>
                        )}

                        <div className="flex gap-2">
                            <a
                                href={`/detail/${selectedHouse.house_id}`}
                                className="flex-1 bg-indigo-500 text-white py-3 rounded-lg font-medium text-center"
                            >
                                查看完整詳情
                            </a>
                            <a
                                href={`https://www.google.com/maps?q=${selectedHouse.latitude},${selectedHouse.longitude}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="bg-green-500 text-white px-4 py-3 rounded-lg font-medium"
                            >
                                📍
                            </a>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
