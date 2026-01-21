/**
 * Chi．Soo 暨宿 - 房源資料
 * 埔里地區租屋房源 (含真實座標)
 */

import type { Property } from '../types';

export const PROPERTIES: Property[] = [
    {
        id: 1,
        type: 'housing',
        title: '靜巷・老宅寓所',
        price: 'NT$ 12,800',
        rating: 4.9,
        ratingCount: 86,
        address: '埔里鎮青田街 12 巷',
        desc: '位於埔里市區靜謐巷弄中。適合喜歡閱讀與獨處的暨大生。',
        tags: ['老宅', '機車好停'],
        images: [
            'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&q=80',
            'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=600&q=80',
        ],
        commute: {
            scooter: { time: '15', dist: '6.2' },
            bus: {
                stopName: '崎下站',
                walkMin: '5',
                busNo: '1 號公車',
                busTime: '20',
                dest: '學人會館',
            },
        },
        reviews: [{ name: 'Emily C.', time: '2天前', rating: 5, text: '太喜歡這裡的氛圍了！' }],
        lng: 120.9680,
        lat: 23.9610,
        x: '50%',
        y: '40%',
    },
    {
        id: 2,
        type: 'housing',
        title: '日光・莫蘭迪',
        price: 'NT$ 9,500',
        rating: 4.7,
        ratingCount: 42,
        address: '埔里鎮中山路三段',
        desc: '全新裝潢，全聯旁邊。',
        tags: ['採光佳', '生活機能'],
        images: ['https://images.unsplash.com/photo-1502005229762-cf1afd38088d?w=600&q=80'],
        commute: {
            scooter: { time: '10', dist: '4.5' },
            bus: {
                stopName: '埔里總站',
                walkMin: '3',
                busNo: '台灣好行',
                busTime: '15',
                dest: '圖書館前',
            },
        },
        reviews: [],
        lng: 120.9650,
        lat: 23.9580,
        x: '20%',
        y: '30%',
    },
    {
        id: 3,
        type: 'housing',
        title: '城南・讀書室',
        price: 'NT$ 8,200',
        rating: 4.8,
        ratingCount: 120,
        address: '埔里鎮南安路',
        desc: '河堤旁視野開闊。',
        tags: ['河堤', '書香'],
        images: ['https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=600&q=80'],
        commute: {
            scooter: { time: '18', dist: '7.0' },
            bus: {
                stopName: '地母廟',
                walkMin: '10',
                busNo: '南投客運',
                busTime: '25',
                dest: '學人會館',
            },
        },
        reviews: [],
        lng: 120.9720,
        lat: 23.9550,
        x: '80%',
        y: '55%',
    },
];
