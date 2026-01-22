/**
 * Chi．Soo 暨宿 - 驗證服務
 * 處理學生身份驗證相關的 API 呼叫
 */

// API 基礎 URL（正式環境應使用環境變數）
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * 驗證狀態類型
 */
export type VerificationStatusType = 'unverified' | 'pending' | 'verified' | 'rejected';

/**
 * 驗證資料介面
 */
export interface VerificationData {
  id?: number;
  user_id: string;
  name: string;
  student_id: string;
  dept: string;
  front_image_path?: string;
  back_image_path?: string;
  status: VerificationStatusType;
  submitted_at?: string;
  reviewed_at?: string;
  reviewer_note?: string;
}

/**
 * API 回應介面
 */
interface ApiResponse<T = unknown> {
  success?: boolean;
  error?: string;
  message?: string;
  data?: T;
}

/**
 * 上傳學生證圖片
 */
export async function uploadVerificationImage(file: File): Promise<{ success: boolean; filename?: string; error?: string }> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/verification/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('[Verification] Upload error:', error);
    return { success: false, error: '上傳失敗，請檢查網路連線' };
  }
}

/**
 * 提交驗證申請
 */
export async function submitVerification(params: {
  userId: string;
  name: string;
  studentId: string;
  dept: string;
  frontImage: string;
  backImage: string;
}): Promise<ApiResponse & { verification_id?: number }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/verification/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: params.userId,
        name: params.name,
        student_id: params.studentId,
        dept: params.dept,
        front_image: params.frontImage,
        back_image: params.backImage,
      }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('[Verification] Submit error:', error);
    return { success: false, error: '提交失敗，請檢查網路連線' };
  }
}

/**
 * 查詢驗證狀態
 */
export async function checkVerificationStatus(userId: string): Promise<{
  status: VerificationStatusType;
  verification?: VerificationData;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/verification/status/${userId}`);
    const data = await response.json();
    
    if (data.error) {
      console.error('[Verification] Status check error:', data.error);
      return { status: 'unverified' };
    }

    return {
      status: data.status as VerificationStatusType,
      verification: data.verification,
    };
  } catch (error) {
    console.error('[Verification] Status check error:', error);
    return { status: 'unverified' };
  }
}

/**
 * 同步用戶資料（LIFF 登入時呼叫）
 * 在後端建立或更新用戶記錄，並回傳驗證狀態
 */
export async function syncUser(params: {
  userId: string;
  displayName?: string;
  pictureUrl?: string;
}): Promise<{
  success: boolean;
  verificationStatus: VerificationStatusType;
  user?: {
    user_id: string;
    display_name: string;
    picture_url: string;
    verification_status: VerificationStatusType;
    persona_type: string | null;
  };
  error?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/verification/sync-user`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: params.userId,
        display_name: params.displayName,
        picture_url: params.pictureUrl,
      }),
    });

    const data = await response.json();
    
    if (!data.success) {
      console.error('[Verification] Sync user error:', data.error);
      return { success: false, verificationStatus: 'unverified', error: data.error };
    }

    return {
      success: true,
      verificationStatus: data.verification_status as VerificationStatusType,
      user: data.user,
    };
  } catch (error) {
    console.error('[Verification] Sync user error:', error);
    return { success: false, verificationStatus: 'unverified', error: '同步失敗，請檢查網路連線' };
  }
}

