/**
 * Chi．Soo 暨宿 - Icon 元件
 * 使用 lucide-react 實作圖示系統
 */

import React from 'react';
import {
    Menu,
    User,
    Star,
    Send,
    ArrowLeft,
    Phone,
    Share2,
    Bookmark,
    MapPin,
    Clock,
    Bike,
    Bus,
    Footprints,
    X,
    Check,
    Shield,
    Camera,
    Upload,
    Lock,
    LogOut,
    Coffee,
    Info,
    AlertCircle,
    Bot,
    Wifi,
    Heart,
    Home,
    Briefcase,
    ChevronRight,
    MessageSquare,
    Edit,
    RotateCcw,
    AlertTriangle,
    type LucideProps,
} from 'lucide-react';

// Icon 名稱對應表
const iconMap: Record<string, React.FC<LucideProps>> = {
    menu: Menu,
    user: User,
    star: Star,
    nav: Send,
    send: Send,
    back: ArrowLeft,
    phone: Phone,
    share: Share2,
    'share-2': Share2,
    bookmark: Bookmark,
    mapPin: MapPin,
    'map-pin': MapPin,
    clock: Clock,
    time: Clock,
    scooter: Bike,
    bike: Bike,
    bus: Bus,
    walk: Footprints,
    footprints: Footprints,
    close: X,
    x: X,
    check: Check,
    shield: Shield,
    camera: Camera,
    upload: Upload,
    lock: Lock,
    logout: LogOut,
    'log-out': LogOut,
    coffee: Coffee,
    info: Info,
    alert: AlertCircle,
    'alert-circle': AlertCircle,
    robot: Bot,
    bot: Bot,
    wifi: Wifi,
    heart: Heart,
    home: Home,
    briefcase: Briefcase,
    'chevron-right': ChevronRight,
    'message-square': MessageSquare,
    edit: Edit,
    'rotate-ccw': RotateCcw,
    'alert-triangle': AlertTriangle,
};

interface IconProps {
    name: string;
    size?: number;
    fill?: string;
    className?: string;
    strokeWidth?: number;
    color?: string;
}

export const Icon: React.FC<IconProps> = ({
    name,
    size = 24,
    fill = 'none',
    className = '',
    strokeWidth = 2,
    color,
}) => {
    if (!name) {
        console.warn('Icon component: name prop is required');
        return (
            <span
                className={`inline-flex items-center justify-center ${className}`}
                style={{ width: size, height: size }}
            />
        );
    }

    const IconComponent = iconMap[name];

    if (!IconComponent) {
        console.warn(`Icon "${name}" not found in iconMap`);
        return (
            <span
                className={`inline-flex items-center justify-center ${className}`}
                style={{ width: size, height: size }}
            />
        );
    }

    return (
        <IconComponent
            size={size}
            fill={fill}
            strokeWidth={strokeWidth}
            color={color}
            className={className}
        />
    );
};

export default Icon;
