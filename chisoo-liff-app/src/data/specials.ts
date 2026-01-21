/**
 * Chi．Soo 暨宿 - 精選活動資料
 */

import type { Special, GuideCard } from '../types';

export const SPECIALS: Special[] = [
    {
        id: 's1',
        title: '期末考週・咖啡買一送一',
        date: '限時 6/20 - 6/25',
        desc: '憑暨大學生證，全品項手沖咖啡買一送一，陪你戰鬥到天亮！',
        image: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&q=80',
        locId: 'c1',
    },
    {
        id: 's2',
        title: '吉他社成發：夏日晚風',
        date: '6/28 19:00 @ 學活',
        desc: '免費入場！前 50 名入場贈送精美社團貼紙。',
        image: 'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=800&q=80',
        locId: 'event1',
    },
    {
        id: 's3',
        title: '早八救星！三明治 9 折',
        date: '每日 07:00 - 09:00',
        desc: '只要出示此畫面，豬排蛋吐司現折 5 元。',
        image: 'https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80',
        locId: 'shop1',
    },
];

export const GUIDE_CARDS: GuideCard[] = [
    {
        id: 'g1',
        title: '那些地圖沒告訴你的事',
        desc: '信義路套房冬天山風大，記得加裝厚窗簾...',
        icon: 'heart',
        tag: '#學長姐真心話',
    },
    {
        id: 'g2',
        title: '三分鐘看房防雷清單',
        desc: '檢查牆角發霉與電費計價，別讓合約變惡夢',
        icon: 'bookmark',
        tag: '#新手必看',
    },
    {
        id: 'g3',
        title: '埔里今晚的節奏',
        desc: '週三夜市開張！必吃地瓜球。明晨校園可能有雲海',
        icon: 'clock',
        tag: '#山城生活',
    },
    {
        id: 'g4',
        title: '憑學生證，生活甜一點',
        desc: '某某早午餐內用紅茶續杯，好home米會員送明信片',
        icon: 'star',
        tag: '#特約優惠',
    },
];
