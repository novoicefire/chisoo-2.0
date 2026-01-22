/**
 * Chi．Soo 暨宿 - Mapbox 地圖元件
 * 使用 react-map-gl 渲染真實地圖
 */

import React, { useCallback } from 'react';
import Map, { Marker, NavigationControl, GeolocateControl } from 'react-map-gl';
import type { MapRef } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import type { Property } from '../../types';
import { MAP_CENTER, COLORS } from '../../types';

interface MapViewProps {
    properties: Property[];
    selectedId: string | number | null;
    onSelect: (property: Property) => void;
    disabled?: boolean;
}

export const MapView: React.FC<MapViewProps> = ({
    properties,
    selectedId,
    onSelect,
    disabled = false,
}) => {
    const mapRef = React.useRef<MapRef>(null);

    const handleMarkerClick = useCallback(
        (property: Property) => {
            if (disabled) return;
            onSelect(property);

            // 平滑移動到選中的標記
            mapRef.current?.flyTo({
                center: [property.lng, property.lat],
                zoom: 15,
                duration: 800,
            });
        },
        [disabled, onSelect]
    );

    return (
        <div className={`absolute inset-0 z-0 ${disabled ? 'pointer-events-none opacity-50' : ''}`}>
            <Map
                ref={mapRef}
                mapboxAccessToken={import.meta.env.VITE_MAPBOX_TOKEN}
                initialViewState={{
                    longitude: MAP_CENTER.lng,
                    latitude: MAP_CENTER.lat,
                    zoom: MAP_CENTER.zoom,
                }}
                style={{ width: '100%', height: '100%' }}
                mapStyle="mapbox://styles/ofireo1023/cmknnkpjn007301srbr9b9gn9"
                attributionControl={false}
                logoPosition="bottom-left"
            >
                {/* 導航控制項 */}
                <NavigationControl position="bottom-right" showCompass={false} />
                <GeolocateControl position="bottom-right" trackUserLocation />

                {/* 房源/咖啡廳標記 */}
                {properties.map((property) => (
                    <Marker
                        key={String(property.id)}
                        longitude={property.lng}
                        latitude={property.lat}
                        anchor="bottom"
                        onClick={(e) => {
                            e.originalEvent.stopPropagation();
                            handleMarkerClick(property);
                        }}
                    >
                        <div
                            className={`cursor-pointer transition-transform duration-200 ${selectedId === property.id ? 'scale-125 z-20' : 'hover:scale-110'
                                }`}
                        >
                            <svg
                                width="40"
                                height="48"
                                viewBox="0 0 40 48"
                                fill="none"
                                className="drop-shadow-[0_4px_6px_rgba(78,60,46,0.4)]"
                            >
                                <path
                                    d="M20 0C8.9543 0 0 8.9543 0 20C0 31.0457 20 48 20 48C20 48 40 31.0457 40 20C40 8.9543 31.0457 0 20 0Z"
                                    fill={selectedId === property.id ? COLORS.star : COLORS.text}
                                    stroke={selectedId === property.id ? COLORS.stroke : 'none'}
                                    strokeWidth={selectedId === property.id ? 2 : 0}
                                />
                                <circle cx="20" cy="20" r="8" fill="white" />
                            </svg>
                        </div>
                    </Marker>
                ))}
            </Map>
        </div>
    );
};

export default MapView;
