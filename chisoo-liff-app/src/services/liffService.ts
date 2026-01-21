/**
 * Chi．Soo 暨宿 - LIFF 服務
 * LINE Login 整合與使用者資訊取得
 */

import liff from '@line/liff';

// LIFF App ID (從環境變數讀取)
const LIFF_ID = import.meta.env.VITE_LIFF_ID || '';

/** LINE 使用者資料 */
export interface LiffUserProfile {
    userId: string;
    displayName: string;
    pictureUrl?: string;
    statusMessage?: string;
}

/** LIFF 初始化狀態 */
export interface LiffState {
    isLoggedIn: boolean;
    isInClient: boolean;
    profile: LiffUserProfile | null;
    error: string | null;
}

/**
 * 初始化 LIFF SDK
 */
export async function initLiff(): Promise<LiffState> {
    const state: LiffState = {
        isLoggedIn: false,
        isInClient: false,
        profile: null,
        error: null,
    };

    if (!LIFF_ID) {
        console.warn('[LIFF] VITE_LIFF_ID not set, skipping LIFF init');
        return state;
    }

    try {
        await liff.init({ liffId: LIFF_ID });
        state.isInClient = liff.isInClient();
        state.isLoggedIn = liff.isLoggedIn();

        if (state.isLoggedIn) {
            const profile = await liff.getProfile();
            state.profile = {
                userId: profile.userId,
                displayName: profile.displayName,
                pictureUrl: profile.pictureUrl,
                statusMessage: profile.statusMessage,
            };
        }
    } catch (error) {
        console.error('[LIFF] Init failed:', error);
        state.error = error instanceof Error ? error.message : 'Unknown error';
    }

    return state;
}

/**
 * 執行 LINE Login
 */
export function liffLogin(): void {
    if (!liff.isLoggedIn()) {
        liff.login();
    }
}

/**
 * 登出
 */
export function liffLogout(): void {
    if (liff.isLoggedIn()) {
        liff.logout();
        window.location.reload();
    }
}

/**
 * 取得 LIFF 存取權杖
 */
export function getLiffAccessToken(): string | null {
    try {
        return liff.getAccessToken();
    } catch {
        return null;
    }
}

/**
 * 檢查是否在 LINE App 內
 */
export function isInLineApp(): boolean {
    try {
        return liff.isInClient();
    } catch {
        return false;
    }
}

/**
 * 關閉 LIFF 視窗 (僅在 LINE App 內有效)
 */
export function closeLiff(): void {
    if (liff.isInClient()) {
        liff.closeWindow();
    }
}
