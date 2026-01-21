/**
 * Chi．Soo 暨宿 - 主應用程式
 * LINE LIFF 暨大租屋與生活探索平台
 */

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Icon,
  MapView,
  SideMenu,
  BottomSheet,
  VerificationCenter,
  UserMenu,
} from './components';
import { COFFEE_SHOPS, OTHER_LOCATIONS } from './data';
import { fetchHouses, checkApiHealth } from './services/apiService';
import { initLiff, liffLogout } from './services/liffService';
import { useLocalStorage } from './hooks';
import type {
  Property,
  FavoriteItem,
  VerificationStatus,
  UserData,
  AppMode,
  SheetState,
} from './types';
import { COLORS } from './types';
import './index.css';

function App() {
  // 狀態管理
  const [selectedProp, setSelectedProp] = useState<Property | null>(null);
  const [sheetState, setSheetState] = useState<SheetState>('peek');
  const [verificationStatus, setVerificationStatus] = useLocalStorage<VerificationStatus>(
    'verificationStatus',
    'unverified'
  );
  const [showVerification, setShowVerification] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showSideMenu, setShowSideMenu] = useState(false);
  const deepLinkProcessed = useRef(false);
  const [userData, setUserData] = useLocalStorage<UserData | null>('userData', null);
  const [appMode, setAppMode] = useState<AppMode>('housing');
  const [showSpecials, setShowSpecials] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);
  const [favoritesTab, setFavoritesTab] = useState<'homes' | 'life'>('homes');
  const [toast, setToast] = useState<string | null>(null);
  const [favorites, setFavorites] = useLocalStorage<FavoriteItem[]>('favorites', []);
  const [houses, setHouses] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiAvailable, setApiAvailable] = useState(false);


  // 從 API 載入房源
  useEffect(() => {
    const loadHouses = async () => {
      setLoading(true);
      const isHealthy = await checkApiHealth();
      setApiAvailable(isHealthy);

      if (isHealthy) {
        const data = await fetchHouses();
        setHouses(data);
      } else {
        console.warn('[API] Flask API unavailable, housing list will be empty');
      }
      setLoading(false);
    };
    loadHouses();
  }, []);

  // Debug: log API availability status
  useEffect(() => {
    if (!loading && !apiAvailable && houses.length === 0) {
      console.info('[API] Tip: Start Flask backend with `python run.py` to load properties');
    }
  }, [loading, apiAvailable, houses.length]);

  // 初始化 LIFF
  useEffect(() => {
    initLiff().then((state) => {

      console.info('[LIFF] Initialized:', state.isLoggedIn ? 'logged in' : 'not logged in', state.isInClient ? '(in LINE)' : '(browser)');
      // 如果已登入且有 Profile，更新使用者資料
      if (state.isLoggedIn && state.profile) {
        setUserData((prev) => ({
          ...prev,
          name: prev?.name || state.profile!.displayName,
          studentId: prev?.studentId || '',
          dept: prev?.dept || '',
          lineUserId: state.profile!.userId,
          displayName: state.profile!.displayName,
          pictureUrl: state.profile!.pictureUrl,
        }));
      }
    });
  }, []);

  // Deep Linking 處理
  useEffect(() => {
    if (deepLinkProcessed.current) return;
    if (loading) return; // 等待 API 載入完成

    const urlParams = new URLSearchParams(window.location.search);
    const propertyId = urlParams.get('propertyId');

    if (!propertyId) return;

    deepLinkProcessed.current = true;

    const findPropertyById = (id: string) => {
      const fromHouses = houses.find((p: Property) => String(p.id) === id);
      if (fromHouses) return { ...fromHouses, type: 'housing' as const };

      const fromCoffee = COFFEE_SHOPS.find((c) => String(c.id) === id);
      if (fromCoffee) return fromCoffee;

      const fromOther = OTHER_LOCATIONS.find((o) => String(o.id) === id);
      if (fromOther) return fromOther;

      return null;
    };

    const targetProperty = findPropertyById(propertyId);

    if (targetProperty) {
      setSelectedProp(targetProperty);
      setSheetState('half');
      setShowSpecials(false);
      setShowAbout(false);

      if (targetProperty.type === 'housing') {
        setAppMode('housing');
      } else if (String(targetProperty.id).startsWith('c')) {
        setAppMode('coffee');
      }
    } else {
      console.warn(`[Deep Linking] 找不到 ID 為 ${propertyId} 的房源`);
    }
  }, [loading, houses]);

  // 收藏功能
  const toggleFavorite = (property: Property) => {
    if (!property) return;

    const propertyId = String(property.id);
    const isHousing = property.type === 'housing';
    const newTab = isHousing ? 'homes' : 'life';
    const exists = favorites.find((f) => String(f.id) === propertyId);

    if (exists) {
      setFavorites(favorites.filter((f) => String(f.id) !== propertyId));
      setFavoritesTab(newTab);
      setToast('已從收藏移除');
    } else {
      setFavorites([
        ...favorites,
        {
          ...property,
          status: 'saved',
          addedAt: new Date().toISOString(),
        } as FavoriteItem,
      ]);
      setFavoritesTab(newTab);
      const listName = isHousing ? '找房清單' : '生活口袋';
      setToast(`已存入「${listName}」`);
    }
    setTimeout(() => setToast(null), 2500);
  };

  const isFavorite = (propertyId: string | number) => {
    if (propertyId === undefined || propertyId === null) return false;
    return favorites.some((f) => String(f.id) === String(propertyId));
  };

  // 瀏覽器返回鍵處理
  useEffect(() => {
    const handlePopState = () => {
      if (sheetState === 'full') {
        setSheetState('half');
      } else if (selectedProp || showSpecials || showAbout || showFavorites) {
        setSelectedProp(null);
        setShowSpecials(false);
        setShowAbout(false);
        setShowFavorites(false);
        setSheetState('peek');
      }
    };

    if (sheetState === 'full' || selectedProp || showSpecials || showAbout || showFavorites) {
      window.history.pushState({ panel: 'open' }, '');
    }

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [sheetState, selectedProp, showSpecials, showAbout, showFavorites]);

  const displayProperties = appMode === 'coffee' ? COFFEE_SHOPS : houses;

  // 處理地圖標記點擊
  const handleMapSelect = (property: Property) => {
    setSelectedProp(property);
    setSheetState('half');
    setShowSpecials(false);
    setShowAbout(false);
  };

  return (
    <div
      className="relative w-full h-[100dvh] overflow-hidden font-sans"
      style={{ backgroundColor: COLORS.land }}
    >
      {/* Mapbox 真實地圖 */}
      <MapView
        properties={displayProperties}
        selectedId={selectedProp?.id ?? null}
        onSelect={handleMapSelect}
        appMode={appMode}
        disabled={sheetState === 'full'}
      />

      {/* 頂部搜尋列 */}
      <motion.div
        animate={{ y: sheetState === 'full' ? -100 : 0, opacity: sheetState === 'full' ? 0 : 1 }}
        className="absolute top-0 left-0 right-0 z-20 px-4 pt-safe-top pb-2 flex flex-col items-center pointer-events-none"
      >
        <div className="w-full max-w-md pointer-events-auto mt-4 space-y-3">
          <div className="bg-white rounded-full h-12 flex items-center px-4 shadow-[0_4px_16px_rgba(78,60,46,0.1)] border border-stroke/30">
            <button
              className="mr-3 text-text opacity-60 pointer-events-auto"
              onClick={() => setShowSideMenu(true)}
            >
              <Icon name="menu" size={20} />
            </button>
            <input
              type="text"
              placeholder={appMode === 'coffee' ? '搜尋咖啡廳、插座...' : '搜尋地標或路名...'}
              className="flex-1 bg-transparent outline-none text-base placeholder-stroke text-text"
              onFocus={() => setSheetState('peek')}
            />
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-8 h-8 bg-land rounded-full flex items-center justify-center border border-stroke/50 overflow-hidden relative pointer-events-auto"
            >
              <div className="text-xs font-bold text-text">
                {userData?.pictureUrl ? (
                  <img src={userData.pictureUrl} alt="" className="w-full h-full object-cover" />
                ) : userData?.displayName ? (
                  userData.displayName.charAt(0)
                ) : userData?.name ? (
                  userData.name.charAt(0)
                ) : (
                  'L'
                )}
              </div>
            </button>
          </div>
        </div>
      </motion.div>

      {/* 側邊選單與彈窗 */}
      <AnimatePresence>
        {showSideMenu && (
          <SideMenu
            isOpen={showSideMenu}
            onClose={() => setShowSideMenu(false)}
            setAppMode={setAppMode}
            setSheetState={setSheetState}
            setShowSpecials={setShowSpecials}
            setShowAbout={setShowAbout}
          />
        )}
        {showVerification && (
          <VerificationCenter
            onClose={() => setShowVerification(false)}
            status={verificationStatus}
            setStatus={setVerificationStatus}
            setUserData={setUserData}
          />
        )}
        {showUserMenu && (
          <UserMenu
            user={userData}
            onClose={() => setShowUserMenu(false)}
            onOpenVerification={() => setShowVerification(true)}
            onLogout={() => {
              liffLogout();
              setUserData(null);
            }}
            onOpenFavorites={() => {
              setShowUserMenu(false);
              setShowFavorites(true);
              setSheetState('full');
            }}
          />
        )}
      </AnimatePresence>

      {/* 導航按鈕 */}
      <motion.button
        whileTap={{ scale: 0.9 }}
        className="absolute right-5 z-20 w-14 h-14 bg-white rounded-full shadow-[0_4px_16px_rgba(78,60,46,0.2)] flex items-center justify-center text-text border border-stroke/20"
        style={{ bottom: sheetState === 'full' ? '-100px' : 'calc(15vh + 30px)', transition: 'bottom 0.4s' }}
      >
        <Icon name="nav" size={24} fill={COLORS.text} />
      </motion.button>

      {/* 底部面板 */}
      <BottomSheet
        snapState={sheetState}
        setSnapState={setSheetState}
        selectedProperty={selectedProp}
        setSelectedProp={setSelectedProp}
        onClearSelection={() => {
          setSelectedProp(null);
          setSheetState('peek');
        }}
        status={verificationStatus}
        openVerification={() => setShowVerification(true)}
        appMode={appMode}
        setAppMode={setAppMode}
        showSpecials={showSpecials}
        setShowSpecials={setShowSpecials}
        showAbout={showAbout}
        setShowAbout={setShowAbout}
        showFavorites={showFavorites}
        setShowFavorites={setShowFavorites}
        favorites={favorites}
        setFavorites={setFavorites}
        isFavorite={isFavorite}
        toggleFavorite={toggleFavorite}
        favoritesTab={favoritesTab}
        currentList={displayProperties}
        setToast={setToast}
      />

      {/* Toast 提示 */}
      {toast && (
        <div className="fixed inset-0 z-50 flex items-end justify-center pb-32 pointer-events-none">
          <button
            className="bg-text text-land px-6 py-3 rounded-full text-sm font-bold shadow-lg flex items-center gap-2 whitespace-nowrap animate-bounce pointer-events-auto hover:bg-text/90 transition-colors cursor-pointer"
            onClick={() => {
              setToast(null);
              setShowFavorites(true);
              setSheetState('full');
            }}
          >
            <Icon name="check" size={18} />
            {toast}
            <Icon name="chevron-right" size={14} className="ml-1 opacity-70" />
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
