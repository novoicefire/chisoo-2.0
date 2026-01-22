/**
 * Chi．Soo 暨宿 - 身份驗證中心元件
 * 整合後端 API 進行真實驗證流程
 */

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import Icon from '../ui/Icon';
import type { VerificationStatus, UserData } from '../../types';
import { uploadVerificationImage, submitVerification } from '../../services/verificationService';

interface VerificationCenterProps {
    onClose: () => void;
    status: VerificationStatus;
    setStatus: (status: VerificationStatus) => void;
    setUserData: (data: UserData | null) => void;
    userId?: string;  // LINE User ID
}

export const VerificationCenter: React.FC<VerificationCenterProps> = ({
    onClose,
    status,
    setStatus,
    setUserData,
    userId,
}) => {
    const [formData, setFormData] = useState({ name: '', studentId: '', dept: '' });
    const [frontImg, setFrontImg] = useState<string | null>(null);
    const [backImg, setBackImg] = useState<string | null>(null);
    const [frontFile, setFrontFile] = useState<File | null>(null);
    const [backFile, setBackFile] = useState<File | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    
    const frontInputRef = useRef<HTMLInputElement>(null);
    const backInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (
        e: React.ChangeEvent<HTMLInputElement>,
        setPreview: (url: string | null) => void,
        setFile: (file: File | null) => void
    ) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setFile(file);
            setPreview(URL.createObjectURL(file));
            setError(null);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        // 驗證表單
        if (!formData.name.trim() || !formData.studentId.trim() || !formData.dept.trim()) {
            setError('請填寫完整資料');
            return;
        }
        if (!frontFile || !backFile) {
            setError('請上傳學生證正反面');
            return;
        }
        if (!userId) {
            setError('請先登入 LINE');
            return;
        }

        setIsSubmitting(true);

        try {
            // 1. 上傳正面圖片
            const frontResult = await uploadVerificationImage(frontFile);
            if (!frontResult.success || !frontResult.filename) {
                throw new Error(frontResult.error || '正面圖片上傳失敗');
            }

            // 2. 上傳反面圖片
            const backResult = await uploadVerificationImage(backFile);
            if (!backResult.success || !backResult.filename) {
                throw new Error(backResult.error || '反面圖片上傳失敗');
            }

            // 3. 提交驗證申請
            const submitResult = await submitVerification({
                userId,
                name: formData.name.trim(),
                studentId: formData.studentId.trim(),
                dept: formData.dept.trim(),
                frontImage: frontResult.filename,
                backImage: backResult.filename,
            });

            if (!submitResult.success) {
                throw new Error(submitResult.error || '提交失敗');
            }

            // 成功：更新狀態
            setUserData({ ...formData });
            setStatus('pending');
            setFormData({ name: '', studentId: '', dept: '' });
            setFrontImg(null);
            setBackImg(null);
            setFrontFile(null);
            setBackFile(null);

        } catch (err) {
            setError(err instanceof Error ? err.message : '提交失敗，請稍後再試');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center sm:p-6">
            {/* Backdrop */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-text/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <motion.div
                initial={{ y: '100%' }}
                animate={{ y: 0 }}
                exit={{ y: '100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                className="bg-land w-full max-w-lg h-[90dvh] sm:h-auto sm:rounded-[32px] rounded-t-[32px] relative z-10 flex flex-col overflow-hidden shadow-2xl"
            >
                {/* Header */}
                <div className="px-6 py-5 border-b border-stroke/20 flex items-center justify-between bg-white/50 backdrop-blur-md">
                    <h3 className="text-xl font-bold text-text flex items-center gap-2">
                        <Icon name="shield" size={24} /> 身份驗證中心
                    </h3>
                    <button
                        onClick={onClose}
                        className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-text hover:bg-text hover:text-land transition-colors"
                    >
                        <Icon name="close" size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {status === 'verified' && (
                        <div className="flex flex-col items-center justify-center py-10 text-center space-y-4">
                            <div className="w-24 h-24 bg-star/20 rounded-full flex items-center justify-center text-star">
                                <Icon name="check" size={48} strokeWidth={3} />
                            </div>
                            <h2 className="text-2xl font-bold text-text">恭喜！身份已驗證</h2>
                            <p className="text-text/70">您現在可以盡情評論、評分與分享照片。</p>
                            <button
                                onClick={onClose}
                                className="px-8 py-3 bg-text text-land rounded-full font-bold shadow-lg"
                            >
                                開始探索
                            </button>
                        </div>
                    )}

                    {status === 'pending' && (
                        <div className="flex flex-col items-center justify-center py-10 text-center space-y-4">
                            <div className="w-24 h-24 bg-stroke/20 rounded-full flex items-center justify-center text-text animate-pulse">
                                <Icon name="time" size={48} />
                            </div>
                            <h2 className="text-2xl font-bold text-text">資料審核中</h2>
                            <p className="text-text/70 px-4">
                                我們的團隊正在人工核對您的學生證資料。
                                <br />
                                通常需要 1-2 個工作天。
                            </p>
                            <button
                                onClick={onClose}
                                className="px-6 py-2 bg-stroke/30 text-text rounded-full font-medium"
                            >
                                知道了
                            </button>
                        </div>
                    )}

                    {status === 'rejected' && (
                        <div className="flex flex-col items-center justify-center py-10 text-center space-y-4">
                            <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center text-red-500">
                                <Icon name="close" size={48} strokeWidth={3} />
                            </div>
                            <h2 className="text-2xl font-bold text-text">驗證未通過</h2>
                            <p className="text-text/70 px-4">
                                您的驗證申請未通過審核。
                                <br />
                                請確認資料正確後重新提交。
                            </p>
                            <button
                                onClick={() => setStatus('unverified')}
                                className="px-6 py-2 bg-text text-land rounded-full font-bold"
                            >
                                重新申請
                            </button>
                        </div>
                    )}

                    {status === 'unverified' && (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {/* 錯誤訊息 */}
                            {error && (
                                <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                                    ❌ {error}
                                </div>
                            )}

                            {/* 基本資料 */}
                            <div className="bg-white p-4 rounded-2xl shadow-sm border border-stroke/10 space-y-4">
                                <h4 className="font-bold text-text mb-2 border-l-4 border-star pl-3">基本資料</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="col-span-2">
                                        <label className="block text-xs font-bold text-text/70 mb-1 ml-1">真實姓名</label>
                                        <input
                                            required
                                            type="text"
                                            className="w-full h-12 px-4 rounded-xl bg-gray-50 text-text border border-transparent focus:border-text outline-none"
                                            placeholder="王小明"
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                            disabled={isSubmitting}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-text/70 mb-1 ml-1">學號</label>
                                        <input
                                            required
                                            type="text"
                                            className="w-full h-12 px-4 rounded-xl bg-gray-50 text-text outline-none"
                                            placeholder="s112..."
                                            value={formData.studentId}
                                            onChange={(e) => setFormData({ ...formData, studentId: e.target.value })}
                                            disabled={isSubmitting}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold text-text/70 mb-1 ml-1">系級</label>
                                        <input
                                            required
                                            type="text"
                                            className="w-full h-12 px-4 rounded-xl bg-gray-50 text-text outline-none"
                                            placeholder="資管三甲"
                                            value={formData.dept}
                                            onChange={(e) => setFormData({ ...formData, dept: e.target.value })}
                                            disabled={isSubmitting}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* 學生證上傳 */}
                            <div className="bg-white p-4 rounded-2xl shadow-sm border border-stroke/10 space-y-4">
                                <h4 className="font-bold text-text mb-2 border-l-4 border-star pl-3">學生證上傳</h4>
                                <p className="text-xs text-text/60 mb-2">請上傳清晰的學生證正反面照片以供查驗。</p>
                                <div className="grid grid-cols-2 gap-4">
                                    <label 
                                        className="aspect-4/3 rounded-xl border-2 border-dashed border-stroke flex flex-col items-center justify-center cursor-pointer hover:bg-land/50 transition-colors relative overflow-hidden bg-gray-50"
                                        onClick={() => !isSubmitting && frontInputRef.current?.click()}
                                    >
                                        {frontImg ? (
                                            <img src={frontImg} className="w-full h-full object-cover" alt="正面" />
                                        ) : (
                                            <>
                                                <Icon name="camera" size={24} className="text-stroke mb-1" />
                                                <span className="text-xs font-bold text-stroke">正面 (有照片)</span>
                                            </>
                                        )}
                                        <input
                                            ref={frontInputRef}
                                            type="file"
                                            hidden
                                            accept="image/*"
                                            onChange={(e) => handleFileChange(e, setFrontImg, setFrontFile)}
                                            disabled={isSubmitting}
                                        />
                                    </label>
                                    <label 
                                        className="aspect-4/3 rounded-xl border-2 border-dashed border-stroke flex flex-col items-center justify-center cursor-pointer hover:bg-land/50 transition-colors relative overflow-hidden bg-gray-50"
                                        onClick={() => !isSubmitting && backInputRef.current?.click()}
                                    >
                                        {backImg ? (
                                            <img src={backImg} className="w-full h-full object-cover" alt="反面" />
                                        ) : (
                                            <>
                                                <Icon name="upload" size={24} className="text-stroke mb-1" />
                                                <span className="text-xs font-bold text-stroke">反面 (註冊章)</span>
                                            </>
                                        )}
                                        <input
                                            ref={backInputRef}
                                            type="file"
                                            hidden
                                            accept="image/*"
                                            onChange={(e) => handleFileChange(e, setBackImg, setBackFile)}
                                            disabled={isSubmitting}
                                        />
                                    </label>
                                </div>
                            </div>

                            {/* Submit */}
                            <div className="pt-2 pb-safe-bottom">
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="w-full h-14 bg-text text-land rounded-2xl font-bold text-lg shadow-xl active:scale-95 transition-transform flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isSubmitting ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-land border-t-transparent rounded-full animate-spin" />
                                            提交中...
                                        </>
                                    ) : (
                                        <>
                                            提交審核 <Icon name="check" size={20} />
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </motion.div>
        </div>
    );
};

export default VerificationCenter;
