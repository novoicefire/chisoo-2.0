/**
 * Chi．Soo 暨宿 - 真實路線地圖元件
 * 使用 Mapbox 繪製實際路線
 */

import React from 'react';
import Map, { Source, Layer, Marker } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import Icon from '../ui/Icon';
import type { Property } from '../../types';
import { NCNU_LOCATION, COLORS } from '../../types';

interface RouteMapRealProps {
    routeGeometry: GeoJSON.LineString;
    property: Property;
    isHousing: boolean;
}

export const RouteMapReal: React.FC<RouteMapRealProps> = ({
    routeGeometry,
    property,
    isHousing,
}) => {
    // 計算地圖中心點
    const centerLng = (property.lng + NCNU_LOCATION.lng) / 2;
    const centerLat = (property.lat + NCNU_LOCATION.lat) / 2;

    const routeGeoJSON: GeoJSON.Feature<GeoJSON.LineString> = {
        type: 'Feature',
        properties: {},
        geometry: routeGeometry,
    };

    return (
        <div className="w-full h-48 rounded-xl overflow-hidden relative border border-stroke/30 mt-4">
            <Map
                mapboxAccessToken={import.meta.env.VITE_MAPBOX_TOKEN}
                initialViewState={{
                    longitude: centerLng,
                    latitude: centerLat,
                    zoom: 12,
                }}
                style={{ width: '100%', height: '100%' }}
                mapStyle="mapbox://styles/ofireo1023/cmknnkpjn007301srbr9b9gn9"
                attributionControl={false}
                interactive={false}
            >
                {/* 路線 */}
                <Source id="route" type="geojson" data={routeGeoJSON}>
                    <Layer
                        id="route-line"
                        type="line"
                        paint={{
                            'line-color': COLORS.text,
                            'line-width': 4,
                            'line-opacity': 0.8,
                        }}
                    />
                </Source>

                {/* 起點標記 */}
                <Marker
                    longitude={isHousing ? property.lng : NCNU_LOCATION.lng}
                    latitude={isHousing ? property.lat : NCNU_LOCATION.lat}
                    anchor="bottom"
                >
                    <div className="w-8 h-8 bg-star rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                        <Icon name="home" size={14} className="text-white" color="white" />
                    </div>
                </Marker>

                {/* 終點標記 */}
                <Marker
                    longitude={isHousing ? NCNU_LOCATION.lng : property.lng}
                    latitude={isHousing ? NCNU_LOCATION.lat : property.lat}
                    anchor="bottom"
                >
                    <div className="w-8 h-8 bg-text rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                        <Icon name="mapPin" size={14} className="text-white" color="white" />
                    </div>
                </Marker>
            </Map>

            {/* 終點標籤 */}
            <div className="absolute bottom-2 right-2 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg text-xs font-bold text-text shadow-sm">
                {isHousing ? '暨南大學' : property.title}
            </div>
        </div>
    );
};

export default RouteMapReal;
