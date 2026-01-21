/**
 * Chi．Soo 暨宿 - 身份驗證中心元件
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Icon from '../ui/Icon';
import type { VerificationStatus, UserData } from '../../types';

interface VerificationCenterProps {
    onClose: () => void;
    status: VerificationStatus;
    setStatus: (status: VerificationStatus) => void;
    setUserData: (data: UserData | null) => void;
}

export const VerificationCenter: React.FC<VerificationCenterProps> = ({
    onClose,
    status,
    setStatus,
    setUserData,
}) => {
    const [formData, setFormData] = useState({ name: '', studentId: '', dept: '' });
    const [frontImg, setFrontImg] = useState<string | null>(null);
    const [backImg, setBackImg] = useState<string | null>(null);

    const handleFileChange = (
        e: React.ChangeEvent<HTMLInputElement>,
        setter: (url: string | null) => void
    ) => {
        if (e.target.files && e.target.files[0]) {
            setter(URL.createObjectURL(e.target.files[0]));
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.name.trim() || !formData.studentId.trim() || !formData.dept.trim()) {
            alert('請填寫完整資料');
            return;
        }
        if (!frontImg || !backImg) {
            alert('請上傳學生證正反面');
            return;
        }
        setUserData({ ...formData });
        setStatus('pending');
        setFormData({ name: '', studentId: '', dept: '' });
        setFrontImg(null);
        setBackImg(null);
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
                            <div className="mt-8 p-4 border border-dashed border-stroke rounded-xl bg-white/30">
                                <p className="text-xs text-stroke mb-2">[測試模式] 模擬管理員操作</p>
                                <button
                                    onClick={() => setStatus('verified')}
                                    className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-bold shadow-md"
                                >
                                    一鍵通過審核
                                </button>
                            </div>
                        </div>
                    )}

                    {status === 'unverified' && (
                        <form onSubmit={handleSubmit} className="space-y-6">
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
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* 學生證上傳 */}
                            <div className="bg-white p-4 rounded-2xl shadow-sm border border-stroke/10 space-y-4">
                                <h4 className="font-bold text-text mb-2 border-l-4 border-star pl-3">學生證上傳</h4>
                                <p className="text-xs text-text/60 mb-2">請上傳清晰的學生證正反面照片以供查驗。</p>
                                <div className="grid grid-cols-2 gap-4">
                                    <label className="aspect-[4/3] rounded-xl border-2 border-dashed border-stroke flex flex-col items-center justify-center cursor-pointer hover:bg-land/50 transition-colors relative overflow-hidden bg-gray-50">
                                        {frontImg ? (
                                            <img src={frontImg} className="w-full h-full object-cover" alt="正面" />
                                        ) : (
                                            <>
                                                <Icon name="camera" size={24} className="text-stroke mb-1" />
                                                <span className="text-xs font-bold text-stroke">正面 (有照片)</span>
                                            </>
                                        )}
                                        <input
                                            type="file"
                                            hidden
                                            accept="image/*"
                                            onChange={(e) => handleFileChange(e, setFrontImg)}
                                        />
                                    </label>
                                    <label className="aspect-[4/3] rounded-xl border-2 border-dashed border-stroke flex flex-col items-center justify-center cursor-pointer hover:bg-land/50 transition-colors relative overflow-hidden bg-gray-50">
                                        {backImg ? (
                                            <img src={backImg} className="w-full h-full object-cover" alt="反面" />
                                        ) : (
                                            <>
                                                <Icon name="upload" size={24} className="text-stroke mb-1" />
                                                <span className="text-xs font-bold text-stroke">反面 (註冊章)</span>
                                            </>
                                        )}
                                        <input
                                            type="file"
                                            hidden
                                            accept="image/*"
                                            onChange={(e) => handleFileChange(e, setBackImg)}
                                        />
                                    </label>
                                </div>
                            </div>

                            {/* Submit */}
                            <div className="pt-2 pb-safe-bottom">
                                <button
                                    type="submit"
                                    className="w-full h-14 bg-text text-land rounded-2xl font-bold text-lg shadow-xl active:scale-95 transition-transform flex items-center justify-center gap-2"
                                >
                                    提交審核 <Icon name="check" size={20} />
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
