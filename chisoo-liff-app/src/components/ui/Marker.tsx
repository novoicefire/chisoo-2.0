/**
 * Chi．Soo 暨宿 - 地圖標記元件
 * 顯示房源或咖啡廳位置
 */

import React from 'react';
import { motion } from 'framer-motion';
import { COLORS, type AppMode } from '../../types';
import Icon from './Icon';

interface MarkerProps {
    x: string;
    y: string;
    onClick: () => void;
    active: boolean;
    type: AppMode;
}

export const Marker: React.FC<MarkerProps> = ({ x, y, onClick, active, type }) => {
    return (
        <motion.button
            className={`absolute -translate-x-1/2 -translate-y-full cursor-pointer z-10 outline-none ${active ? 'marker-enter z-20' : ''}`}
            style={{ left: x, top: y }}
            whileTap={{ scale: 0.9 }}
            animate={{ scale: active ? 1.2 : 1, y: active ? -15 : 0 }}
            onClick={(e) => {
                e.stopPropagation();
                onClick();
            }}
        >
            {type === 'coffee' ? (
                <div className="w-10 h-10 bg-text rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                    <Icon name="coffee" size={20} className="text-white" color="white" />
                </div>
            ) : (
                <svg
                    width="40"
                    height="48"
                    viewBox="0 0 40 48"
                    fill="none"
                    className="drop-shadow-[0_4px_6px_rgba(78,60,46,0.4)]"
                >
                    <path
                        d="M20 0C8.9543 0 0 8.9543 0 20C0 31.0457 20 48 20 48C20 48 40 31.0457 40 20C40 8.9543 31.0457 0 20 0Z"
                        fill={COLORS.text}
                        stroke={active ? COLORS.stroke : 'none'}
                        strokeWidth={active ? 2 : 0}
                    />
                    <circle cx="20" cy="20" r="8" fill="white" />
                </svg>
            )}
        </motion.button>
    );
};

export default Marker;
