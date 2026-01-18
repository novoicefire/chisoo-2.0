# ============================================================
# handlers/api.py - API 端點藍圖
# 專案：Chi Soo 租屋小幫手
# 說明：提供 LIFF 前端與管理後台呼叫的 REST API
# ============================================================

from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """API 健康檢查"""
    return jsonify({"status": "ok", "service": "Chi Soo API"})


@api_bp.route("/houses", methods=["GET"])
def get_houses():
    """
    取得房源列表
    
    Query Parameters:
        - page: 頁碼 (預設 1)
        - limit: 每頁數量 (預設 10)
        - category: 類型篩選
    """
    # TODO: Phase 5 實作
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    
    return jsonify({
        "houses": [],
        "page": page,
        "limit": limit,
        "total": 0
    })


@api_bp.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id: int):
    """取得單一房源詳情"""
    # TODO: Phase 5 實作
    return jsonify({"error": "Not implemented"}), 501


@api_bp.route("/reviews", methods=["GET"])
def get_reviews():
    """取得評價列表"""
    # TODO: Phase 7 實作
    return jsonify({"reviews": [], "total": 0})


@api_bp.route("/reviews", methods=["POST"])
def create_review():
    """新增評價"""
    # TODO: Phase 7 實作
    return jsonify({"error": "Not implemented"}), 501


@api_bp.route("/favorites", methods=["GET"])
def get_favorites():
    """取得收藏列表"""
    # TODO: Phase 3 實作
    return jsonify({"favorites": [], "total": 0})


@api_bp.route("/favorites", methods=["POST"])
def add_favorite():
    """加入收藏"""
    # TODO: Phase 3 實作
    return jsonify({"error": "Not implemented"}), 501
