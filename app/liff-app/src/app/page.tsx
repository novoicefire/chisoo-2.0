/**
 * LIFF 首頁
 * 專案：Chi Soo 租屋小幫手
 * 路由：/
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { initLiff, getProfile, isInLineApp } from '@/lib/liff';

export default function Home() {
  const [profile, setProfile] = useState<{ displayName: string; pictureUrl?: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function init() {
      try {
        await initLiff();
        const userProfile = await getProfile();
        setProfile(userProfile);
      } catch (e) {
        console.error('初始化失敗', e);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
      {/* Header */}
      <div className="p-6 text-center">
        <h1 className="text-3xl font-bold mb-2">🏠 Chi Soo</h1>
        <p className="text-indigo-100">暨大租屋小幫手</p>

        {profile && (
          <div className="mt-4 flex items-center justify-center gap-3">
            {profile.pictureUrl && (
              <img
                src={profile.pictureUrl}
                alt={profile.displayName}
                className="w-10 h-10 rounded-full border-2 border-white"
              />
            )}
            <span className="text-lg">歡迎，{profile.displayName}！</span>
          </div>
        )}
      </div>

      {/* Menu Cards */}
      <div className="px-4 pb-8 space-y-4">
        <Link
          href="/map"
          className="block bg-white/20 backdrop-blur rounded-xl p-6 hover:bg-white/30 transition"
        >
          <div className="flex items-center gap-4">
            <span className="text-4xl">🗺️</span>
            <div>
              <h2 className="text-xl font-bold">地圖搜尋</h2>
              <p className="text-indigo-100 text-sm">在地圖上探索埔里租屋</p>
            </div>
          </div>
        </Link>

        <Link
          href="/review"
          className="block bg-white/20 backdrop-blur rounded-xl p-6 hover:bg-white/30 transition"
        >
          <div className="flex items-center gap-4">
            <span className="text-4xl">⭐</span>
            <div>
              <h2 className="text-xl font-bold">評價系統</h2>
              <p className="text-indigo-100 text-sm">查看與撰寫租屋評價</p>
            </div>
          </div>
        </Link>

        {!isInLineApp() && (
          <div className="bg-yellow-500/20 backdrop-blur rounded-xl p-4 text-center">
            <p className="text-yellow-100 text-sm">
              💡 建議透過 LINE App 開啟以獲得完整功能
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="text-center py-4 text-indigo-200 text-sm">
        <p>Powered by Chi Soo Bot</p>
      </div>
    </div>
  );
}
