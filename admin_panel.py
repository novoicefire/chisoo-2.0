# ============================================================
# admin_panel.py - 簡易管理後台
# 專案：Chi Soo 租屋小幫手
# 使用方式：python admin_panel.py (開啟 http://localhost:8000)
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from app.models import db_session, Base, engine
from app.models.user import User
from app.models.session import UserSession
from app.models.house import House
from app.models.persona import Persona
from app.models.review import Review
from app.models.ai_log import AILog
from app.models.verification import Verification, VerificationStatus
from datetime import datetime, timedelta
from sqlalchemy import func

# 設定 template 資料夾
app = Flask(__name__, template_folder="templates")
app.secret_key = "admin-secret-key"

# 自動建立所有資料表
Base.metadata.create_all(bind=engine)

@app.context_processor
def inject_notifications():
    """全域注入通知資料"""
    pending_verifications_count = db_session.query(Verification).filter_by(status=VerificationStatus.PENDING).count()
    pending_reviews_count = db_session.query(Review).filter_by(status="pending").count()
    
    total_notifications = pending_verifications_count + pending_reviews_count
    
    notifications = []
    if pending_verifications_count > 0:
        notifications.append({
            "msg": f"{pending_verifications_count} 筆待審核驗證",
            "link": "/", # 暫時指向首頁待辦區
            "icon": "fa-user-check"
        })
    if pending_reviews_count > 0:
        notifications.append({
            "msg": f"{pending_reviews_count} 筆待審核評價",
            "link": "/reviews?status=pending",
            "icon": "fa-comment-dots"
        })
        
    return dict(
        notification_count=total_notifications,
        notifications_list=notifications
    )

@app.route("/")
def index():
    """首頁 (Dashboard)"""
    users = db_session.query(User).all()
    users_with_sessions = []
    # 僅顯示最近 10 筆使用者
    for user in users[-10:]:
        session = db_session.query(UserSession).filter_by(user_id=user.user_id).first()
        users_with_sessions.append((user, session))
    
    # 查詢待審核的驗證申請
    pending_verifications = db_session.query(Verification).filter_by(
        status=VerificationStatus.PENDING
    ).order_by(Verification.submitted_at.desc()).limit(10).all()
    
    # 統計數據 for Charts
    # Persona Distribution
    persona_counts = {}
    for p in db_session.query(Persona).all():
        count = db_session.query(User).filter_by(persona_type=p.name).count()
        if count > 0:
            persona_counts[p.name] = count
    
    # 未分類
    unknown_count = db_session.query(User).filter((User.persona_type == None) | (User.persona_type == "")).count()
    if unknown_count > 0:
        persona_counts["未分類"] = unknown_count

    # User Growth (Last 7 days)
    today = datetime.utcnow().date()
    growth_data = {}
    # Initialize last 7 days with 0
    for i in range(6, -1, -1):
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        growth_data[date_str] = 0
        
    # Query data
    try:
        last_week = datetime.utcnow() - timedelta(days=7)
        # Check DB Dialect for date function
        if 'sqlite' in engine.url.drivername:
            date_func = func.date(User.created_at)
        else:
            # PostgreSQL usually treats date() on timestamp as cast
            date_func = func.date(User.created_at)

        registrations = db_session.query(
            date_func, func.count(User.user_id)
        ).filter(User.created_at >= last_week).group_by(date_func).all()
        
        for date_obj, count in registrations:
            date_str = str(date_obj)
            if date_str in growth_data:
                growth_data[date_str] = count
    except Exception as e:
        print(f"Error calculating growth: {e}")

    return render_template(
        "admin/dashboard.html",
        active_page="dashboard",
        user_count=db_session.query(User).count(),
        session_count=db_session.query(UserSession).count(),
        testing_count=db_session.query(UserSession).filter_by(status="TESTING").count(),
        house_count=db_session.query(House).count(),
        persona_count=db_session.query(Persona).count(),
        pending_count=db_session.query(Verification).filter_by(status=VerificationStatus.PENDING).count(),
        users=sorted(users_with_sessions, key=lambda x: x[0].created_at or datetime.min, reverse=True),
        personas=db_session.query(Persona).all(),
        pending_verifications=pending_verifications,
        persona_labels=list(persona_counts.keys()),
        persona_data=list(persona_counts.values()),
        growth_labels=list(growth_data.keys()),
        growth_data=list(growth_data.values())
    )

@app.route("/user/<user_id>")
def user_detail(user_id):
    """使用者詳情頁"""
    user = db_session.query(User).filter_by(user_id=user_id).first()
    if not user:
        flash("使用者不存在") # Removed Emoji
        return redirect(url_for("index"))
    
    session = db_session.query(UserSession).filter_by(user_id=user_id).first()
    logs = db_session.query(AILog).filter_by(user_id=user_id).order_by(AILog.created_at.desc()).all()
    
    return render_template("admin/user_detail.html", user=user, session=session, logs=logs)

# --- House Management Routes ---

@app.route("/houses")
def houses_list():
    """房源管理列表"""
    houses = db_session.query(House).order_by(House.house_id.desc()).all()
    return render_template("admin/houses.html", houses=houses, active_page="houses")

@app.route("/house/new", methods=["GET", "POST"])
def house_new():
    """新增房源"""
    if request.method == "POST":
        # 收集 features
        features = {}
        for key in request.form:
            if key.startswith("feature_"):
                feat_name = key.replace("feature_", "")
                features[feat_name] = True

        house = House(
            name=request.form.get("name", "").strip(),
            address=request.form.get("address", "").strip(),
            rent=int(request.form.get("rent", 0)),
            room_type=request.form.get("room_type", "套房"),
            category_tag=request.form.get("category_tag", "") or None,
            description=request.form.get("description", "").strip(),
            image_url=request.form.get("image_url", "").strip(),
            features=features,
            is_active="is_active" in request.form
        )
        db_session.add(house)
        db_session.commit()
        
        flash(f"已新增房源：{house.name}")
        return redirect(url_for("houses_list"))
    
    # Empty house object for template
    class EmptyHouse:
        name = ""; address = ""; rent = ""; room_type = "套房"; category_tag = ""
        description = ""; image_url = ""; features = {}; is_active = True
    
    personas = db_session.query(Persona).all()
    return render_template("admin/house_edit.html", house=EmptyHouse(), is_new=True, personas=personas)

@app.route("/house/<int:house_id>", methods=["GET", "POST"])
def house_edit(house_id):
    """編輯房源"""
    house = db_session.query(House).filter_by(house_id=house_id).first()
    if not house:
        flash("房源不存在")
        return redirect(url_for("houses_list"))
    
    if request.method == "POST":
        house.name = request.form.get("name", "").strip()
        house.address = request.form.get("address", "").strip()
        house.rent = int(request.form.get("rent", 0))
        house.room_type = request.form.get("room_type", "套房")
        house.category_tag = request.form.get("category_tag", "") or None
        house.description = request.form.get("description", "").strip()
        house.image_url = request.form.get("image_url", "").strip()
        house.is_active = "is_active" in request.form
        
        # Features update
        features = {}
        for key in request.form:
            if key.startswith("feature_"):
                feat_name = key.replace("feature_", "")
                features[feat_name] = True
        house.features = features
        
        db_session.commit()
        flash(f"已更新房源：{house.name}")
        return redirect(url_for("houses_list"))
    
    personas = db_session.query(Persona).all()
    return render_template("admin/house_edit.html", house=house, is_new=False, personas=personas)

@app.route("/house/<int:house_id>/toggle", methods=["POST"])
def house_toggle(house_id):
    """切換房源上架狀態"""
    house = db_session.query(House).filter_by(house_id=house_id).first()
    if house:
        house.is_active = not house.is_active
        db_session.commit()
        status = "上架" if house.is_active else "下架"
        flash(f"已{status}：{house.name}")
    return redirect(url_for("houses_list"))

@app.route("/house/<int:house_id>/delete", methods=["POST"])
def house_delete(house_id):
    """刪除房源"""
    house = db_session.query(House).filter_by(house_id=house_id).first()
    if house:
        # 先刪除關聯的 Review
        db_session.query(Review).filter_by(house_id=house_id).delete()
        
        name = house.name
        db_session.delete(house)
        db_session.commit()
        flash(f"已刪除房源：{name}")
    return redirect(url_for("houses_list"))

# --- Persona Routes ---

@app.route("/persona/new", methods=["GET", "POST"])
def persona_new():
    """新增人物誌"""
    if request.method == "POST":
        persona_id = request.form.get("persona_id", "").strip()
        
        # 檢查是否已存在
        existing = db_session.query(Persona).filter_by(persona_id=persona_id).first()
        if existing:
            flash(f"類型代碼 {persona_id} 已存在") # Removed Emoji
            return redirect(url_for("persona_new"))
        
        # 解析關鍵字
        keywords = [k.strip() for k in request.form.get("keywords", "").split(",") if k.strip()]
        
        # 建立 algo_config
        algo_config = {
            "rent_min": int(request.form.get("rent_min", 0) or 0),
            "rent_max": int(request.form.get("rent_max", 99999) or 99999),
            "preferred_locations": [loc.strip() for loc in request.form.get("preferred_locations", "").split(",") if loc.strip()],
            "required": [f.strip() for f in request.form.get("required_features", "").split(",") if f.strip()],
            "bonus": [f.strip() for f in request.form.get("bonus_features", "").split(",") if f.strip()],
            "management_pref": request.form.get("management_pref", "").strip() or None,
            "room_type": request.form.get("room_type", "").strip() or None,
        }
        
        persona = Persona(
            persona_id=persona_id,
            name=request.form.get("name", "").strip(),
            description=request.form.get("description", "").strip(),
            keywords=keywords,
            algo_config=algo_config,
            active="active" in request.form
        )
        db_session.add(persona)
        db_session.commit()
        
        flash(f"已新增類型：{persona.name}") # Removed Emoji
        return redirect(url_for("index"))
    
    # 空白的 Persona 物件 (用於模板)
    class EmptyPersona:
        persona_id = ""
        name = ""
        description = ""
        keywords = []
        algo_config = {}
        active = True
    
    return render_template("admin/persona_edit.html", persona=EmptyPersona(), is_new=True, active_page="personas")

@app.route("/persona/<persona_id>", methods=["GET", "POST"])
def persona_edit(persona_id):
    """編輯人物誌"""
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    if not persona:
        flash("類型不存在") # Removed Emoji
        return redirect(url_for("index"))
    
    if request.method == "POST":
        # 更新欄位
        persona.name = request.form.get("name", "").strip()
        persona.description = request.form.get("description", "").strip()
        persona.keywords = [k.strip() for k in request.form.get("keywords", "").split(",") if k.strip()]
        persona.active = "active" in request.form
        
        # 更新 algo_config
        persona.algo_config = {
            "rent_min": int(request.form.get("rent_min", 0) or 0),
            "rent_max": int(request.form.get("rent_max", 99999) or 99999),
            "preferred_locations": [loc.strip() for loc in request.form.get("preferred_locations", "").split(",") if loc.strip()],
            "required": [f.strip() for f in request.form.get("required_features", "").split(",") if f.strip()],
            "bonus": [f.strip() for f in request.form.get("bonus_features", "").split(",") if f.strip()],
            "management_pref": request.form.get("management_pref", "").strip() or None,
            "room_type": request.form.get("room_type", "").strip() or None,
        }
        
        db_session.commit()
        flash(f"已更新：{persona.name}") # Removed Emoji
        return redirect(url_for("index"))
    
    return render_template("admin/persona_edit.html", persona=persona, is_new=False, active_page="personas")

@app.route("/persona/<persona_id>/toggle", methods=["POST"])
def persona_toggle(persona_id):
    """切換人物誌啟用狀態"""
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    if persona:
        persona.active = not persona.active
        db_session.commit()
        status = "啟用" if persona.active else "停用"
        flash(f"已{status}：{persona.name}") # Removed Emoji
    return redirect(url_for("index"))

@app.route("/persona/<persona_id>/delete", methods=["POST"])
def persona_delete(persona_id):
    """刪除人物誌"""
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    if persona:
        name = persona.name
        db_session.delete(persona)
        db_session.commit()
        flash(f"已刪除：{name}") # Removed Emoji
    return redirect(url_for("index"))

# --- Review Management ---

@app.route("/reviews")
def reviews_list():
    """評價管理列表"""
    status_filter = request.args.get("status")
    query = db_session.query(Review)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    reviews = query.order_by(Review.created_at.desc()).all()
    
    return render_template("admin/reviews.html", reviews=reviews, status_filter=status_filter, active_page="reviews")

@app.route("/reviews/<int:review_id>/approve", methods=["POST"])
def review_approve(review_id):
    """通過評價"""
    review = db_session.query(Review).filter_by(id=review_id).first()
    if review:
        review.status = "approved"
        db_session.commit()
        flash(f"已發布評價 #{review.id}") # Removed Emoji
    return redirect(request.referrer or url_for("reviews_list"))

@app.route("/reviews/<int:review_id>/reject", methods=["POST"])
def review_reject(review_id):
    """駁回評價"""
    review = db_session.query(Review).filter_by(id=review_id).first()
    if review:
        review.status = "rejected"
        review.reject_reason = "管理員駁回" # 簡化，未來可加 UI 輸入理由
        db_session.commit()
        flash(f"已駁回評價 #{review.id}") # Removed Emoji
    return redirect(request.referrer or url_for("reviews_list"))

@app.route("/reviews/<int:review_id>/delete", methods=["POST"])
def review_delete(review_id):
    """刪除評價"""
    review = db_session.query(Review).filter_by(id=review_id).first()
    if review:
        db_session.delete(review)
        db_session.commit()
        flash(f"已刪除評價 #{review_id}") # Removed Emoji
    return redirect(request.referrer or url_for("reviews_list"))

# --- Verification Routes ---

@app.route("/verifications")
def verifications_list():
    """驗證列表 (導向 Dashboard 或未來實作完整列表頁)"""
    return redirect(url_for("index")) # 暫時導回首頁

@app.route("/verification/<int:verification_id>")
def verification_detail(verification_id):
    """審核詳情頁"""
    v = db_session.query(Verification).filter_by(id=verification_id).first()
    if not v:
        flash("驗證申請不存在") # Removed Emoji
        return redirect(url_for("index"))
    
    return render_template("admin/verification_detail.html", v=v)

@app.route("/verification/<int:verification_id>/approve", methods=["POST"])
def verification_approve(verification_id):
    """通過驗證"""
    v = db_session.query(Verification).filter_by(id=verification_id).first()
    if not v:
        flash("驗證申請不存在")
        return redirect(url_for("index"))
    
    v.status = VerificationStatus.VERIFIED
    v.reviewed_at = datetime.utcnow()
    
    user = db_session.query(User).filter_by(user_id=v.user_id).first()
    if user:
        user.verification_status = VerificationStatus.VERIFIED
    
    db_session.commit()
    flash(f"已通過 {v.name} 的驗證申請") # Removed Emoji
    return redirect(url_for("index"))

@app.route("/verification/<int:verification_id>/reject", methods=["POST"])
def verification_reject(verification_id):
    """拒絕驗證"""
    v = db_session.query(Verification).filter_by(id=verification_id).first()
    if not v:
        flash("驗證申請不存在")
        return redirect(url_for("index"))
    
    v.status = VerificationStatus.REJECTED
    v.reviewed_at = datetime.utcnow()
    v.reviewer_note = request.form.get("note", "").strip()
    
    user = db_session.query(User).filter_by(user_id=v.user_id).first()
    if user:
        user.verification_status = VerificationStatus.REJECTED
    
    db_session.commit()
    flash(f"已拒絕 {v.name} 的驗證申請") # Removed Emoji
    return redirect(url_for("index"))

@app.route("/uploads/verifications/<filename>")
def serve_verification_image(filename):
    """提供驗證圖片檔案"""
    upload_folder = os.path.join(os.getcwd(), "uploads", "verifications")
    return send_from_directory(upload_folder, filename)

@app.route("/reset-verification/<user_id>", methods=["POST"])
def reset_verification(user_id):
    """重置使用者驗證狀態"""
    user = db_session.query(User).filter_by(user_id=user_id).first()
    if not user:
        flash(f"使用者 {user_id} 不存在") # Removed Emoji
        return redirect(url_for("index"))
        
    verifications = db_session.query(Verification).filter_by(user_id=user_id).all()
    upload_folder = os.path.join(os.getcwd(), "uploads", "verifications")
    
    count = 0
    for v in verifications:
        # 嘗試刪除圖片
        if v.front_image_path:
            try:
                os.remove(os.path.join(upload_folder, v.front_image_path))
            except OSError:
                pass
        if v.back_image_path:
            try:
                os.remove(os.path.join(upload_folder, v.back_image_path))
            except OSError:
                pass
        db_session.delete(v)
        count += 1
    
    user.verification_status = 'unverified'
    db_session.commit()
    flash(f"已重置 {user.display_name or user_id} 的驗證狀態") # Removed Emoji
    return redirect(url_for("index"))

# --- System Routes ---

@app.route("/reset-sessions", methods=["POST"])
def reset_sessions():
    """清空所有 Session"""
    count = db_session.query(UserSession).delete()
    db_session.commit()
    flash(f"已清空 {count} 筆測驗進度") # Removed Emoji
    return redirect(url_for("index"))

@app.route("/reset-users", methods=["POST"])
def reset_users():
    """清空所有使用者"""
    # 刪除關聯資料 (因 Foreign Key 限制)
    db_session.query(Verification).delete()
    db_session.query(Review).delete()
    db_session.query(AILog).delete()
    db_session.query(UserSession).delete()
    
    # 最後刪除使用者
    user_count = db_session.query(User).delete()
    db_session.commit()
    flash(f"已清空 {user_count} 筆使用者資料 (含關聯紀錄)") # Removed Emoji
    return redirect(url_for("index"))

@app.route("/reset-user/<user_id>", methods=["POST"])
def reset_user(user_id):
    """重置單一使用者"""
    session = db_session.query(UserSession).filter_by(user_id=user_id).first()
    if session:
        session.status = "IDLE"
        session.collected_data = {}
        db_session.commit()
        flash(f"已重置使用者 {user_id[:20]}...") # Removed Emoji
    return redirect(url_for("index"))

@app.route("/clear-user-logs/<user_id>", methods=["POST"])
def clear_user_logs(user_id):
    """清除使用者的 AI 紀錄"""
    log_count = db_session.query(AILog).filter_by(user_id=user_id).delete()
    session = db_session.query(UserSession).filter_by(user_id=user_id).first()
    if session:
        session.collected_data = {}
        session.status = "IDLE"
    db_session.commit()
    flash(f"已清除 {log_count} 筆紀錄") # Removed Emoji
    return redirect(url_for("user_detail", user_id=user_id))

@app.route("/seed")
def seed_data():
    """重新初始化種子資料"""
    from scripts.seed_data import seed_personas, seed_sample_houses
    seed_personas()
    seed_sample_houses()
    flash("種子資料已重新初始化") # Removed Emoji
    return redirect(url_for("index"))

if __name__ == "__main__":
    print("=" * 50)
    print(" Chi Soo 管理後台 (Refactored)")
    print("=" * 50)
    print()
    print(" 開啟瀏覽器前往: http://localhost:8000")
    print("   按 Ctrl+C 停止")
    print()
    app.run(host="0.0.0.0", port=8000, debug=True)
