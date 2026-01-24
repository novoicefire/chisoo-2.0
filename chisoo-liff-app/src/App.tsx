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
import { OTHER_LOCATIONS } from './data';
import { fetchHouses, checkApiHealth, fetchFavorites, addFavorite, removeFavorite, transformFavoriteToProperty, fetchUserReviews, updateReview, withdrawReview } from './services/apiService';
import { initLiff, liffLogout, liffLogin } from './services/liffService';
import { syncUser } from './services/verificationService';
import { useLocalStorage } from './hooks';
import type {
  Property,
  FavoriteItem,
  VerificationStatus,
  UserData,
  SheetState,
  UserReview,
} from './types';
import { COLORS } from './types';
import './index.css';

function App() {
  // 狀態管理
  const [selectedProp, setSelectedProp] = useState<Property | null>(null);
  const [sheetState, setSheetState] = useState<SheetState>('peek');
  // 安全性修正：驗證狀態不應持久化，每次開啟 App 預設未驗證，等待伺服器確認
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus>('unverified');
  const [showVerification, setShowVerification] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showSideMenu, setShowSideMenu] = useState(false);
  const deepLinkProcessed = useRef(false);
  const [userData, setUserData] = useLocalStorage<UserData | null>('userData', null);
  const [showAbout, setShowAbout] = useState(false);
  const [showFavorites, setShowFavorites] = useState(false);
  const [showReviews, setShowReviews] = useState(false);
  const [favoritesTab, setFavoritesTab] = useState<'homes' | 'life'>('homes');
  const [toast, setToast] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [userReviews, setUserReviews] = useState<UserReview[]>([]);
  const [_favoritesLoading, setFavoritesLoading] = useState(false);
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
    initLiff().then(async (state) => {
      console.info('[LIFF] Initialized:', state.isLoggedIn ? 'logged in' : 'not logged in', state.isInClient ? '(in LINE)' : '(browser)');

      // 如果已登入且有 Profile，更新使用者資料並同步驗證狀態
      if (state.isLoggedIn && state.profile) {
        
        // 1. 同步後端用戶資料與驗證狀態
        try {
          const { verificationStatus, user } = await syncUser({
            userId: state.profile.userId,
            displayName: state.profile.displayName,
            pictureUrl: state.profile.pictureUrl
          });
          
          setVerificationStatus(verificationStatus);
          
          setUserData((prev) => ({
            ...prev,
            name: user?.display_name || prev?.name || state.profile!.displayName,
            studentId: prev?.studentId || '', // syncUser 目前不回傳 studentId，保留本地或等待驗證資料
            dept: prev?.dept || '',
            lineUserId: state.profile!.userId,
            displayName: state.profile!.displayName,
            pictureUrl: state.profile!.pictureUrl,
          }));
          
          // 載入收藏列表
          setFavoritesLoading(true);
          try {
            const { favorites: favList } = await fetchFavorites(state.profile.userId);
            const transformedFavs = favList.map((fav) => ({
              ...transformFavoriteToProperty(fav),
              status: 'saved' as const,
              addedAt: fav.created_at,
            }));
            setFavorites(transformedFavs);
          } catch (favError) {
            console.error('[App] Failed to load favorites:', favError);
          } finally {
            setFavoritesLoading(false);
          }
        } catch (error) {
          console.error('[App] Failed to sync user status:', error);
          setVerificationStatus('unverified');
        }
      } else {
        // 如果未登入，確保狀態重置
        if (!state.isLoggedIn) {
          setVerificationStatus('unverified');
        }

        // 如果未登入，且沒有本地使用者資料，則執行登入
        if (!state.isLoggedIn && !userData) {
          liffLogin();
        }
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

      const fromOther = OTHER_LOCATIONS.find((o) => String(o.id) === id);
      if (fromOther) return fromOther;

      return null;
    };

    const targetProperty = findPropertyById(propertyId);

    if (targetProperty) {
      setSelectedProp(targetProperty);
      setSheetState('half');
      setShowAbout(false);
    } else {
      console.warn(`[Deep Linking] 找不到 ID 為 ${propertyId} 的房源`);
    }
  }, [loading, houses]);

  // 收藏功能 (同步到後端 API)
  const toggleFavorite = async (property: Property) => {
    if (!property) return;
    if (!userData?.lineUserId) {
      setToast('請先登入 LINE');
      setTimeout(() => setToast(null), 2500);
      return;
    }

    const propertyId = String(property.id);
    const isHousing = property.type === 'housing';
    const newTab = isHousing ? 'homes' : 'life';
    const existingFav = favorites.find((f) => String(f.id) === propertyId) as (FavoriteItem & { favoriteId?: number }) | undefined;

    if (existingFav && existingFav.favoriteId) {
      // 移除收藏
      const result = await removeFavorite(userData.lineUserId, existingFav.favoriteId);
      if (result.success) {
        setFavorites(favorites.filter((f) => String(f.id) !== propertyId));
        setFavoritesTab(newTab);
        setToast('已從收藏移除');
      } else {
        setToast('移除失敗: ' + (result.error || '未知錯誤'));
      }
    } else {
      // 新增收藏
      const result = await addFavorite(userData.lineUserId, Number(property.id));
      if (result.success) {
        setFavorites([
          ...favorites,
          {
            ...property,
            favoriteId: result.favoriteId,
            status: 'saved',
            addedAt: new Date().toISOString(),
          } as FavoriteItem,
        ]);
        setFavoritesTab(newTab);
        const listName = isHousing ? '找房清單' : '生活口袋';
        setToast(`已存入「${listName}」`);
      } else {
        setToast('收藏失敗: ' + (result.error || '未知錯誤'));
      }
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
      } else if (selectedProp || showAbout || showFavorites || showReviews) {
        setSelectedProp(null);
        setShowAbout(false);
        setShowFavorites(false);
        setShowReviews(false);
        setSheetState('peek');
      }
    };

    if (sheetState === 'full' || selectedProp || showAbout || showFavorites || showReviews) {
      window.history.pushState({ panel: 'open' }, '');
    }

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [sheetState, selectedProp, showAbout, showFavorites, showReviews]);

  // 載入使用者評價
  const loadUserReviews = async () => {
    if (!userData?.lineUserId) return;
    const { reviews } = await fetchUserReviews(userData.lineUserId);
    setUserReviews(reviews);
  };

  // 編輯評價
  const handleUpdateReview = async (reviewId: number, data: { rating: number; comment: string }) => {
    if (!userData?.lineUserId) return false;
    const result = await updateReview(userData.lineUserId, reviewId, data);
    return result.success;
  };

  // 收回評價
  const handleWithdrawReview = async (reviewId: number) => {
    if (!userData?.lineUserId) return false;
    const result = await withdrawReview(userData.lineUserId, reviewId);
    return result.success;
  };

  // 處理地圖標記點擊
  const handleMapSelect = (property: Property) => {
    setSelectedProp(property);
    setSheetState('half');
    setShowAbout(false);
  };

  return (
    <div
      className="relative w-full h-dvh overflow-hidden font-sans"
      style={{ backgroundColor: COLORS.land }}
    >
      {/* Mapbox 真實地圖 */}
      <MapView
        properties={houses}
        selectedId={selectedProp?.id ?? null}
        onSelect={handleMapSelect}
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
              placeholder="搜尋地標或路名..."
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
            setSheetState={setSheetState}
            setShowAbout={setShowAbout}
          />
        )}
        {showVerification && (
          <VerificationCenter
            onClose={() => setShowVerification(false)}
            status={verificationStatus}
            setStatus={setVerificationStatus}
            userId={userData?.lineUserId}
          />
        )}
        {showUserMenu && (
          <UserMenu
            user={userData}
            verificationStatus={verificationStatus}
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
            onOpenReviews={() => {
              setShowUserMenu(false);
              setShowReviews(true);
              setSheetState('full');
              loadUserReviews();
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
        showAbout={showAbout}
        setShowAbout={setShowAbout}
        showFavorites={showFavorites}
        setShowFavorites={setShowFavorites}
        favorites={favorites}
        setFavorites={setFavorites}
        isFavorite={isFavorite}
        toggleFavorite={toggleFavorite}
        favoritesTab={favoritesTab}
        currentList={houses}
        setToast={setToast}
        showReviews={showReviews}
        setShowReviews={setShowReviews}
        userReviews={userReviews}
        onUpdateReview={handleUpdateReview}
        onWithdrawReview={handleWithdrawReview}
        onRefreshReviews={loadUserReviews}
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
