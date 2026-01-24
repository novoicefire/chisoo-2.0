# ============================================================
# handlers/api.py - API 端點藍圖
# 專案：Chi Soo 租屋小幫手
# 說明：提供 LIFF 前端與管理後台呼叫的 REST API
# ============================================================

from datetime import date
from flask import Blueprint, jsonify, request

from app.models import db_session
from app.models.house import House
from app.models.favorite import Favorite
from app.models.review import Review
from app.models.user import User

api_bp = Blueprint("api", __name__)


# ============================================================
# 健康檢查
# ============================================================

@api_bp.route("/health", methods=["GET"])
def health_check():
    """API 健康檢查"""
    return jsonify({"status": "ok", "service": "Chi Soo API", "version": "1.0.0"})


# ============================================================
# 房源 API
# ============================================================

@api_bp.route("/houses", methods=["GET"])
def get_houses():
    """
    取得房源列表
    
    Query Parameters:
        - page: 頁碼 (預設 1)
        - limit: 每頁數量 (預設 10)
        - category: 類型篩選
        - min_rent: 最低租金
        - max_rent: 最高租金
        - room_type: 房型篩選
    """
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    category = request.args.get("category")
    min_rent = request.args.get("min_rent", type=int)
    max_rent = request.args.get("max_rent", type=int)
    room_type = request.args.get("room_type")
    
    # 建立查詢
    query = db_session.query(House).filter(House.is_active == True)
    
    # 套用篩選條件
    if category:
        query = query.filter(House.category_tag == category)
    if min_rent:
        query = query.filter(House.rent >= min_rent)
    if max_rent:
        query = query.filter(House.rent <= max_rent)
    if room_type:
        query = query.filter(House.room_type == room_type)
    
    # 計算總數
    total = query.count()
    
    # 分頁
    offset = (page - 1) * limit
    houses = query.order_by(House.avg_rating.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        "houses": [house_to_dict(h) for h in houses],
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit
    })


@api_bp.route("/houses/<int:house_id>", methods=["GET"])
def get_house_detail(house_id: int):
    """取得單一房源詳情"""
    house = db_session.query(House).filter_by(house_id=house_id).first()
    
    if not house:
        return jsonify({"error": "House not found"}), 404
    
    # 取得該房源的評價
    reviews = db_session.query(Review).filter(
        Review.house_id == house_id,
        Review.status == "approved"
    ).order_by(Review.created_at.desc()).limit(10).all()
    
    result = house_to_dict(house)
    result["reviews"] = [review_to_dict(r) for r in reviews]
    
    return jsonify(result)


# ============================================================
# 收藏 API
# ============================================================

@api_bp.route("/favorites", methods=["GET"])
def get_favorites():
    """取得收藏列表 (需要 X-User-Id header)"""
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        return jsonify({"error": "X-User-Id header is required"}), 401
    
    favorites = db_session.query(Favorite).filter(
        Favorite.user_id == user_id
    ).order_by(Favorite.created_at.desc()).all()
    
    # 取得房源資料
    house_ids = [f.house_id for f in favorites]
    houses = db_session.query(House).filter(House.house_id.in_(house_ids)).all()
    house_map = {h.house_id: h for h in houses}
    
    result = []
    for fav in favorites:
        house = house_map.get(fav.house_id)
        if house:
            result.append({
                "favorite_id": fav.id,
                "house": house_to_dict(house),
                "created_at": fav.created_at.isoformat()
            })
    
    return jsonify({"favorites": result, "total": len(result)})


@api_bp.route("/favorites", methods=["POST"])
def add_favorite():
    """新增收藏"""
    from app.services.session_service import SessionService
    
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        return jsonify({"error": "X-User-Id header is required"}), 401
    
    data = request.get_json()
    house_id = data.get("house_id")
    
    if not house_id:
        return jsonify({"error": "house_id is required"}), 400
    
    # 確保使用者存在（解決外鍵約束問題）
    SessionService.get_or_create_user(user_id)
    
    # 檢查房源是否存在
    house = db_session.query(House).filter_by(house_id=house_id).first()
    if not house:
        return jsonify({"error": "House not found"}), 404
    
    # 檢查是否已收藏
    existing = db_session.query(Favorite).filter_by(
        user_id=user_id, house_id=house_id
    ).first()
    
    if existing:
        return jsonify({"error": "Already in favorites", "favorite_id": existing.id}), 409
    
    # 新增收藏
    new_favorite = Favorite(user_id=user_id, house_id=house_id)
    db_session.add(new_favorite)
    db_session.commit()
    
    return jsonify({
        "message": "Added to favorites",
        "favorite_id": new_favorite.id
    }), 201


@api_bp.route("/favorites/<int:favorite_id>", methods=["DELETE"])
def delete_favorite(favorite_id: int):
    """刪除收藏"""
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        return jsonify({"error": "X-User-Id header is required"}), 401
    
    favorite = db_session.query(Favorite).filter_by(
        id=favorite_id, user_id=user_id
    ).first()
    
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    
    db_session.delete(favorite)
    db_session.commit()
    
    return jsonify({"message": "Removed from favorites"})


# ============================================================
# 評價 API
# ============================================================

@api_bp.route("/reviews", methods=["GET"])
def get_reviews():
    """取得評價列表"""
    house_id = request.args.get("house_id", type=int)
    user_id = request.headers.get("X-User-Id")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    
    query = db_session.query(Review)
    
    if house_id:
        # 取得特定房源的已審核評價
        query = query.filter(Review.house_id == house_id, Review.status == "approved")
    elif user_id:
        # 取得使用者自己的評價 (含所有狀態)
        query = query.filter(Review.user_id == user_id)
    else:
        # 只取已審核的公開評價
        query = query.filter(Review.status == "approved")
    
    total = query.count()
    offset = (page - 1) * limit
    reviews = query.order_by(Review.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        "reviews": [review_to_dict(r) for r in reviews],
        "page": page,
        "limit": limit,
        "total": total
    })


@api_bp.route("/reviews", methods=["POST"])
def create_review():
    """新增評價 (每日限 3 篇)"""
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        return jsonify({"error": "X-User-Id header is required"}), 401
    
    data = request.get_json()
    house_id = data.get("house_id")
    rating = data.get("rating")
    comment = data.get("comment", "")
    
    # 驗證必填欄位
    if not house_id:
        return jsonify({"error": "house_id is required"}), 400
    if not rating or not (1 <= rating <= 5):
        return jsonify({"error": "rating must be between 1 and 5"}), 400
    
    # 檢查房源是否存在
    house = db_session.query(House).filter_by(house_id=house_id).first()
    if not house:
        return jsonify({"error": "House not found"}), 404
    
    # 檢查每日限額
    today = date.today()
    today_count = db_session.query(Review).filter(
        Review.user_id == user_id,
        Review.created_date == today
    ).count()
    
    if today_count >= 3:
        return jsonify({
            "error": "Daily review limit reached",
            "message": "您今日的評價次數已達上限 (3 篇)，請明日再來。",
            "remaining": 0
        }), 429
    
    # 新增評價
    new_review = Review(
        house_id=house_id,
        user_id=user_id,
        rating=rating,
        comment=comment,
        status="pending",  # 預設待審核
        created_date=today
    )
    db_session.add(new_review)
    db_session.commit()
    
    return jsonify({
        "message": "Review submitted for approval",
        "review_id": new_review.review_id,
        "remaining_today": 3 - today_count - 1
    }), 201


@api_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id: int):
    """刪除評價 (僅限本人)"""
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        return jsonify({"error": "X-User-Id header is required"}), 401
    
    review = db_session.query(Review).filter_by(
        review_id=review_id, user_id=user_id
    ).first()
    
    if not review:
        return jsonify({"error": "Review not found or not owned by you"}), 404
    
    db_session.delete(review)
    db_session.commit()
    
    return jsonify({"message": "Review deleted"})


# ============================================================
# 輔助函數
# ============================================================

def house_to_dict(house: House) -> dict:
    """將 House 物件轉為字典"""
    return {
        "house_id": house.house_id,
        "name": house.name,
        "address": house.address,
        "category_tag": house.category_tag,
        "rent": house.rent,
        "room_type": house.room_type,
        "features": house.features,
        "description": house.description,
        "image_url": house.image_url,
        "images": house.images,
        "latitude": house.latitude,
        "longitude": house.longitude,
        "avg_rating": house.avg_rating,
        "review_count": house.review_count,
        "created_at": house.created_at.isoformat() if house.created_at else None
    }


def review_to_dict(review: Review) -> dict:
    """將 Review 物件轉為字典"""
    return {
        "review_id": review.review_id,
        "house_id": review.house_id,
        "rating": review.rating,
        "comment": review.comment,
        "status": review.status,
        "reject_reason": review.reject_reason,
        "created_at": review.created_at.isoformat() if review.created_at else None
    }
