# ============================================================
# handlers/verification.py - 學生身份驗證 API Handler
# 專案：Chi Soo 租屋小幫手
# 說明：處理學生驗證申請、圖片上傳、狀態查詢等 API
# ============================================================

import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

from app.models import db_session, User, Verification
from app.models.verification import VerificationStatus


# 建立 Blueprint
verification_bp = Blueprint('verification', __name__, url_prefix="/api/verification")

# 設定上傳目錄
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "verifications")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 確保上傳目錄存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """檢查檔案類型是否允許"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@verification_bp.route("/upload", methods=["POST"])
def upload_image():
    """
    上傳學生證圖片
    
    Request:
        - file: 圖片檔案 (multipart/form-data)
    
    Response:
        - 200: { "success": true, "filename": "xxx.jpg" }
        - 400: { "success": false, "error": "錯誤訊息" }
    """
    try:
        # 檢查是否有檔案
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "沒有上傳檔案"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "檔案名稱為空"}), 400
        
        # 檢查檔案類型
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "不支援的檔案類型，請上傳 PNG 或 JPG"}), 400
        
        # 檢查檔案大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"success": False, "error": "檔案過大，最大 5MB"}), 400
        
        # 生成唯一檔名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # 儲存檔案
        file.save(filepath)
        
        return jsonify({
            "success": True,
            "filename": filename
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@verification_bp.route("/submit", methods=["POST"])
def submit_verification():
    """
    提交學生身份驗證申請
    
    Request JSON:
        {
            "user_id": "LINE User ID",
            "name": "真實姓名",
            "student_id": "學號",
            "dept": "系級",
            "front_image": "正面照檔名",
            "back_image": "反面照檔名"
        }
    
    Response:
        - 200: { "success": true, "verification_id": 123 }
        - 400: { "success": false, "error": "錯誤訊息" }
    """
    try:
        data = request.get_json()
        
        # 驗證必要欄位
        required_fields = ['user_id', 'name', 'student_id', 'dept', 'front_image', 'back_image']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"缺少必要欄位: {field}"}), 400
        
        # 檢查使用者是否存在，不存在則建立<
        user = db_session.query(User).filter_by(user_id=data['user_id']).first()
        if not user:
            user = User(user_id=data['user_id'])
            db_session.add(user)
            db_session.commit()
        
        # 檢查是否已有待審核或已通過的申請
        existing = db_session.query(Verification).filter_by(
            user_id=data['user_id']
        ).filter(
            Verification.status.in_([VerificationStatus.PENDING, VerificationStatus.VERIFIED])
        ).first()
        
        if existing:
            if existing.status == VerificationStatus.VERIFIED:
                return jsonify({"success": False, "error": "您已通過驗證"}), 400
            else:
                return jsonify({"success": False, "error": "您已有待審核的申請"}), 400
        
        # 建立新的驗證記錄
        verification = Verification(
            user_id=data['user_id'],
            name=data['name'],
            student_id=data['student_id'],
            dept=data['dept'],
            front_image_path=data['front_image'],
            back_image_path=data['back_image'],
            status=VerificationStatus.PENDING
        )
        
        db_session.add(verification)
        
        # 更新使用者驗證狀態
        user.verification_status = VerificationStatus.PENDING
        
        db_session.commit()
        
        return jsonify({
            "success": True,
            "verification_id": verification.id,
            "message": "申請已提交，請等待審核"
        }), 200
        
    except IntegrityError as e:
        db_session.rollback()
        if 'student_id' in str(e):
            return jsonify({"success": False, "error": "此學號已被使用"}), 400
        return jsonify({"success": False, "error": "資料重複"}), 400
    except Exception as e:
        db_session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@verification_bp.route("/status/<user_id>", methods=["GET"])
def get_verification_status(user_id):
    """
    查詢使用者的驗證狀態
    
    Response:
        - 200: { "status": "pending", "verification": {...} }
        - 404: { "status": "unverified" }
    """
    try:
        # 查詢最新的驗證記錄
        verification = db_session.query(Verification).filter_by(
            user_id=user_id
        ).order_by(Verification.submitted_at.desc()).first()
        
        if not verification:
            return jsonify({"status": "unverified"}), 200
        
        return jsonify({
            "status": verification.status,
            "verification": verification.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@verification_bp.route("/image/<filename>", methods=["GET"])
def get_image(filename):
    """
    取得上傳的圖片（用於顯示）
    """
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({"error": "圖片不存在"}), 404
