# ============================================================
# admin_panel.py - 簡易管理後台
# 專案：Chi Soo 租屋小幫手
# 使用方式：python admin_panel.py (開啟 http://localhost:8000)
# ============================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string, request, redirect, url_for, flash, send_from_directory
from app.models import db_session, Base, engine
from app.models.user import User
from app.models.session import UserSession
from app.models.house import House
from app.models.persona import Persona
from app.models.review import Review
from app.models.ai_log import AILog
from app.models.verification import Verification, VerificationStatus

app = Flask(__name__)
app.secret_key = "admin-secret-key"

# 自動建立所有資料表 (包括新的 ai_logs)
Base.metadata.create_all(bind=engine)

# HTML 模板
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chi Soo 管理後台</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { 
            color: white; 
            text-align: center; 
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-box .number { font-size: 2em; font-weight: bold; }
        .stat-box .label { opacity: 0.9; margin-top: 5px; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th { background: #f8f9fa; font-weight: 600; }
        tr:hover { background: #f8f9fa; }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn-danger { background: #ef4444; color: white; }
        .btn-warning { background: #f59e0b; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-primary { background: #6366f1; color: white; }
        .actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }
        .flash {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            background: #10b981;
            color: white;
        }
        .status-idle { color: #10b981; }
        .status-testing { color: #f59e0b; }
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-testing { background: #fef3c7; color: #d97706; }
        .badge-pending { background: #fef3c7; color: #d97706; }
        .badge-verified { background: #d1fae5; color: #059669; }
        .badge-rejected { background: #fee2e2; color: #dc2626; }
        .badge-unverified { background: #e5e7eb; color: #6b7280; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🦔 Chi Soo 管理後台</h1>
        
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        {% for message in messages %}
        <div class="flash">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}
        
        <!-- 統計卡片 -->
        <div class="card">
            <h2>📊 系統統計</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="number">{{ user_count }}</div>
                    <div class="label">使用者</div>
                </div>
                <div class="stat-box">
                    <div class="number">{{ session_count }}</div>
                    <div class="label">Session</div>
                </div>
                <div class="stat-box">
                    <div class="number">{{ testing_count }}</div>
                    <div class="label">測試中</div>
                </div>
                <div class="stat-box">
                    <div class="number">{{ house_count }}</div>
                    <div class="label">房源</div>
                </div>
                <div class="stat-box">
                    <div class="number">{{ persona_count }}</div>
                    <div class="label">人物誌</div>
                </div>
                <div class="stat-box" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                    <div class="number">{{ pending_count }}</div>
                    <div class="label">待審核</div>
                </div>
            </div>
        </div>
        
        <!-- 快速操作 -->
        <div class="card">
            <h2>⚡ 快速操作</h2>
            <div class="actions">
                <form action="/reset-sessions" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-warning" onclick="return confirm('確定要清空所有測驗進度嗎？')">
                        🔄 清空所有測驗進度
                    </button>
                </form>
                <form action="/reset-users" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-danger" onclick="return confirm('⚠️ 這將刪除所有使用者資料！確定嗎？')">
                        🗑️ 清空所有使用者
                    </button>
                </form>
                <a href="/seed" class="btn btn-success">🌱 重新初始化種子資料</a>
            </div>
        </div>
        
        <!-- 使用者列表 -->
        <div class="card">
            <h2>👥 使用者列表</h2>
            {% if users %}
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>頭像</th>
                        <th>暱稱</th>
                        <th>人格類型</th>
                        <th>測驗狀態</th>
                        <th>驗證狀態</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user, session in users %}
                    <tr>
                        <td><code>{{ user.user_id[:8] }}...</code></td>
                        <td>
                            {% if user.picture_url %}
                            <img src="{{ user.picture_url }}" alt="avatar" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #ddd;">
                            {% else %}
                            <div style="width: 40px; height: 40px; border-radius: 50%; background: #eee; display: flex; align-items: center; justify-content: center; color: #999;">?</div>
                            {% endif %}
                        </td>
                        <td>{{ user.display_name or '-' }}</td>
                        <td>{{ user.persona_type or '-' }}</td>
                        <td>
                            {% if session %}
                            <span class="badge badge-{{ session.status.lower() }}">{{ session.status }}</span>
                            {% else %}
                            <span class="badge badge-idle">無 Session</span>
                            {% endif %}
                        </td>
                        <td>
                            <span class="badge badge-{{ user.verification_status or 'unverified' }}">{{ user.verification_status or 'Unverified' }}</span>
                        </td>
                        <td>
                            <a href="/user/{{ user.user_id }}" class="btn btn-primary" style="padding: 5px 10px; margin-right: 5px;">詳情</a>
                            <form action="/reset-user/{{ user.user_id }}" method="POST" style="display:inline;" title="重置測驗狀態">
                                <button type="submit" class="btn btn-warning" style="padding: 5px 10px;">
                                    重置測驗
                                </button>
                            </form>
                            {% if user.verification_status != 'unverified' %}
                            <form action="/reset-verification/{{ user.user_id }}" method="POST" style="display:inline; margin-left: 5px;" title="重置驗證狀態">
                                <button type="submit" class="btn btn-danger" style="padding: 5px 10px; background-color: #6366f1;">
                                    重置驗證
                                </button>
                            </form>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #666;">目前沒有使用者</p>
            {% endif %}
        </div>
        
        <!-- 身份驗證審核 -->
        <div class="card">
            <h2>🎓 身份驗證審核 <a href="/verifications" class="btn btn-primary" style="float: right; padding: 5px 15px;">查看全部</a></h2>
            {% if pending_verifications %}
            <table>
                <thead>
                    <tr>
                        <th>提交時間</th>
                        <th>姓名</th>
                        <th>學號</th>
                        <th>系級</th>
                        <th>狀態</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for v in pending_verifications %}
                    <tr>
                        <td>{{ v.submitted_at.strftime('%m/%d %H:%M') if v.submitted_at else '-' }}</td>
                        <td>{{ v.name }}</td>
                        <td><code>{{ v.student_id }}</code></td>
                        <td>{{ v.dept }}</td>
                        <td><span class="badge badge-{{ v.status }}">{{ v.status }}</span></td>
                        <td>
                            <a href="/verification/{{ v.id }}" class="btn btn-primary" style="padding: 5px 10px;">審核</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #666;">目前沒有待審核的驗證申請 ✅</p>
            {% endif %}
        </div>
        
        <!-- 人物誌列表 -->
        <div class="card">
            <h2>🎭 人物誌類型 <a href="/persona/new" class="btn btn-success" style="float: right; padding: 5px 15px;">+ 新增類型</a></h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>名稱</th>
                        <th>租金範圍</th>
                        <th>關鍵字</th>
                        <th>狀態</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for persona in personas %}
                    <tr>
                        <td><code>{{ persona.persona_id }}</code></td>
                        <td>{{ persona.name }}</td>
                        <td>{{ persona.algo_config.get('rent_min', 0) }} ~ {{ persona.algo_config.get('rent_max', 99999) }}</td>
                        <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;">{{ ', '.join(persona.keywords[:3]) }}{% if persona.keywords|length > 3 %}...{% endif %}</td>
                        <td>{{ '✅' if persona.active else '❌' }}</td>
                        <td>
                            <a href="/persona/{{ persona.persona_id }}" class="btn btn-primary" style="padding: 5px 10px;">編輯</a>
                            <form action="/persona/{{ persona.persona_id }}/toggle" method="POST" style="display:inline;">
                                <button type="submit" class="btn btn-warning" style="padding: 5px 10px;">
                                    {{ '停用' if persona.active else '啟用' }}
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    """首頁"""
    users = db_session.query(User).all()
    users_with_sessions = []
    for user in users:
        session = db_session.query(UserSession).filter_by(user_id=user.user_id).first()
        users_with_sessions.append((user, session))
    
    # 查詢待審核的驗證申請
    pending_verifications = db_session.query(Verification).filter_by(
        status=VerificationStatus.PENDING
    ).order_by(Verification.submitted_at.desc()).limit(10).all()
    
    return render_template_string(
        ADMIN_TEMPLATE,
        user_count=db_session.query(User).count(),
        session_count=db_session.query(UserSession).count(),
        testing_count=db_session.query(UserSession).filter_by(status="TESTING").count(),
        house_count=db_session.query(House).count(),
        persona_count=db_session.query(Persona).count(),
        pending_count=db_session.query(Verification).filter_by(status=VerificationStatus.PENDING).count(),
        users=users_with_sessions,
        personas=db_session.query(Persona).all(),
        pending_verifications=pending_verifications
    )

@app.route("/reset-sessions", methods=["POST"])
def reset_sessions():
    """清空所有 Session"""
    count = db_session.query(UserSession).delete()
    db_session.commit()
    flash(f"✅ 已清空 {count} 筆測驗進度")
    return redirect(url_for("index"))

@app.route("/reset-users", methods=["POST"])
def reset_users():
    """清空所有使用者"""
    session_count = db_session.query(UserSession).delete()
    user_count = db_session.query(User).delete()
    db_session.commit()
    flash(f"✅ 已清空 {user_count} 筆使用者資料")
    return redirect(url_for("index"))

@app.route("/reset-user/<user_id>", methods=["POST"])
def reset_user(user_id):
    """重置單一使用者"""
    session = db_session.query(UserSession).filter_by(user_id=user_id).first()
    if session:
        session.status = "IDLE"
        session.collected_data = {}
        db_session.commit()
        flash(f"✅ 已重置使用者 {user_id[:20]}...")
    return redirect(url_for("index"))

@app.route("/seed")
def seed_data():
    """重新初始化種子資料"""
    from scripts.seed_data import seed_personas, seed_sample_houses
    seed_personas()
    seed_sample_houses()
    flash("✅ 種子資料已重新初始化")
    return redirect(url_for("index"))


# 使用者詳情頁模板
USER_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>使用者詳情 - Chi Soo 管理後台</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 30px; }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 { color: #333; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-danger { background: #ef4444; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .user-info { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
        .avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #ddd; }
        .collected-data { background: #f8f9fa; padding: 15px; border-radius: 10px; font-family: monospace; white-space: pre-wrap; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
        th { background: #f8f9fa; }
        .success { color: #10b981; }
        .failure { color: #ef4444; }
        .flash { padding: 15px; border-radius: 8px; margin-bottom: 20px; background: #10b981; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🦔 使用者詳情</h1>
        
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        {% for message in messages %}
        <div class="flash">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}
        
        <div class="card">
            <div class="user-info">
                {% if user.picture_url %}
                <img src="{{ user.picture_url }}" alt="avatar" class="avatar">
                {% else %}
                <div class="avatar" style="background: #eee; display: flex; align-items: center; justify-content: center; color: #999; font-size: 2em;">?</div>
                {% endif %}
                <div>
                    <h2 style="border: none; padding: 0; margin: 0;">{{ user.display_name or '未知' }}</h2>
                    <p style="color: #666; margin-top: 5px;"><code>{{ user.user_id }}</code></p>
                    <p style="color: #666;">人格類型: {{ user.persona_type or '-' }}</p>
                </div>
            </div>
            <div style="display: flex; gap: 10px;">
                <a href="/" class="btn btn-secondary">← 返回列表</a>
                <form action="/clear-user-logs/{{ user.user_id }}" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-danger" onclick="return confirm('確定要清除此使用者的所有 AI 紀錄與標記嗎？')">
                        🗑️ 清除所有紀錄與標記
                    </button>
                </form>
            </div>
        </div>
        
        <div class="card">
            <h2>📦 已收集的標記 (collected_data)</h2>
            {% if session and session.collected_data %}
            <div class="collected-data">{{ session.collected_data | tojson(indent=2) }}</div>
            {% else %}
            <p style="color: #666;">尚無資料</p>
            {% endif %}
        </div>
        
        <div class="card">
            <h2>🧠 AI 思考紀錄 (共 {{ logs | length }} 筆)</h2>
            {% if logs %}
            <table>
                <thead>
                    <tr>
                        <th>時間</th>
                        <th>主題</th>
                        <th>使用者輸入</th>
                        <th>AI 回應</th>
                        <th>提取結果</th>
                        <th>狀態</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td>{{ log.created_at.strftime('%m/%d %H:%M') }}</td>
                        <td>{{ log.topic or '-' }}</td>
                        <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;">{{ log.user_input[:30] }}{% if log.user_input|length > 30 %}...{% endif %}</td>
                        <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;">{{ log.ai_raw_response[:30] if log.ai_raw_response else '-' }}{% if log.ai_raw_response and log.ai_raw_response|length > 30 %}...{% endif %}</td>
                        <td><code>{{ log.extracted_data }}</code></td>
                        <td class="{{ 'success' if log.is_success else 'failure' }}">{{ '✅' if log.is_success else '❌' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #666;">尚無 AI 紀錄</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


@app.route("/user/<user_id>")
def user_detail(user_id):
    """使用者詳情頁"""
    user = db_session.query(User).filter_by(user_id=user_id).first()
    if not user:
        flash("❌ 使用者不存在")
        return redirect(url_for("index"))
    
    session = db_session.query(UserSession).filter_by(user_id=user_id).first()
    logs = db_session.query(AILog).filter_by(user_id=user_id).order_by(AILog.created_at.desc()).all()
    
    return render_template_string(USER_DETAIL_TEMPLATE, user=user, session=session, logs=logs)


@app.route("/clear-user-logs/<user_id>", methods=["POST"])
def clear_user_logs(user_id):
    """清除使用者的 AI 紀錄與標記"""
    # 清除 AI 紀錄
    log_count = db_session.query(AILog).filter_by(user_id=user_id).delete()
    
    # 清除 collected_data
    session = db_session.query(UserSession).filter_by(user_id=user_id).first()
    if session:
        session.collected_data = {}
        session.status = "IDLE"
    
    db_session.commit()
    flash(f"✅ 已清除 {log_count} 筆 AI 紀錄與標記資料")
    return redirect(url_for("user_detail", user_id=user_id))


# 人物誌編輯頁模板
PERSONA_EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ '新增' if is_new else '編輯' }}人物誌 - Chi Soo 管理後台</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 30px; }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 { color: #333; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; font-weight: 600; margin-bottom: 8px; color: #333; }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #6366f1;
        }
        .form-group textarea { min-height: 100px; font-family: monospace; }
        .form-group .hint { font-size: 12px; color: #666; margin-top: 5px; }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-primary { background: #6366f1; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .actions { display: flex; gap: 10px; margin-top: 20px; }
        .flash { padding: 15px; border-radius: 8px; margin-bottom: 20px; background: #10b981; color: white; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; }
        .checkbox-group input[type="checkbox"] { width: 20px; height: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 {{ '新增' if is_new else '編輯' }}人物誌</h1>
        
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        {% for message in messages %}
        <div class="flash">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}
        
        <form method="POST" class="card">
            <h2>基本資訊</h2>
            
            <div class="form-group">
                <label>類型代碼 (persona_id)</label>
                <input type="text" name="persona_id" value="{{ persona.persona_id or '' }}" 
                       {{ 'readonly' if not is_new else '' }} required
                       pattern="[a-z_]+" placeholder="例: type_F">
                <div class="hint">小寫英文加底線，例如 type_F（建立後不可修改）</div>
            </div>
            
            <div class="form-group">
                <label>顯示名稱</label>
                <input type="text" name="name" value="{{ persona.name or '' }}" required placeholder="例: 寵物友善型">
            </div>
            
            <div class="form-group">
                <label>診斷書描述</label>
                <textarea name="description" placeholder="這段文字會顯示在診斷書上...">{{ persona.description or '' }}</textarea>
            </div>
            
            <div class="form-group">
                <label>關鍵字（逗號分隔）</label>
                <input type="text" name="keywords" 
                       value="{{ ', '.join(persona.keywords) if persona.keywords else '' }}"
                       placeholder="例: 便宜, 省錢, 經濟, CP值">
                <div class="hint">AI 用來識別使用者意圖的觸發詞</div>
            </div>
            
            <h2 style="margin-top: 30px;">演算法參數（六大維度）</h2>
            
            <!-- 1. 預算契合度 (S_budget) -->
            <div class="form-group">
                <label>📊 預算契合度 (S_budget) - 權重 1.5</label>
                <div style="display: flex; gap: 10px; align-items: center;">
                    <input type="number" name="rent_min" style="width: 120px;"
                           value="{{ persona.algo_config.get('rent_min', 0) if persona.algo_config else 0 }}"
                           placeholder="最低">
                    <span>~</span>
                    <input type="number" name="rent_max" style="width: 120px;"
                           value="{{ persona.algo_config.get('rent_max', 99999) if persona.algo_config else 99999 }}"
                           placeholder="最高">
                    <span>元/月</span>
                </div>
                <div class="hint">建議租金區間，使用者預算落在此區間內得滿分</div>
            </div>
            
            <!-- 2. 地段便利性 (S_location) -->
            <div class="form-group">
                <label>📍 地段便利性 (S_location) - 權重 1.2</label>
                <input type="text" name="preferred_locations" 
                       value="{{ ', '.join(persona.algo_config.get('preferred_locations', [])) if persona.algo_config else '' }}"
                       placeholder="例: downtown, school, quiet">
                <div class="hint">偏好地點（逗號分隔）：downtown=市區 / school=學校 / quiet=安靜</div>
            </div>
            
            <!-- 3. 硬體設施 (S_features) -->
            <div class="form-group">
                <label>🔧 必備設施 (L_req) - 設施分 +30</label>
                <input type="text" name="required_features" 
                       value="{{ ', '.join(persona.algo_config.get('required', [])) if persona.algo_config else '' }}"
                       placeholder="例: garbage, elevator, security">
                <div class="hint">此類型必須有的設施，使用者需求命中得滿分</div>
            </div>
            
            <div class="form-group">
                <label>✨ 加分設施 (L_bonus) - 設施分 +15</label>
                <input type="text" name="bonus_features" 
                       value="{{ ', '.join(persona.algo_config.get('bonus', [])) if persona.algo_config else '' }}"
                       placeholder="例: parking, laundry, wifi">
                <div class="hint">此類型可能有的設施，命中給額外加分</div>
            </div>
            
            <!-- 4. 房東與管理 (S_landlord) -->
            <div class="form-group">
                <label>🏠 管理模式 (S_landlord) - 權重 1.0</label>
                <select name="management_pref" style="padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; width: 100%;">
                    <option value="" {{ 'selected' if not persona.algo_config or not persona.algo_config.get('management_pref') else '' }}>不限</option>
                    <option value="owner" {{ 'selected' if persona.algo_config and persona.algo_config.get('management_pref') == 'owner' else '' }}>房東同住 (owner)</option>
                    <option value="pro" {{ 'selected' if persona.algo_config and persona.algo_config.get('management_pref') == 'pro' else '' }}>專業管理 (pro)</option>
                    <option value="no_owner" {{ 'selected' if persona.algo_config and persona.algo_config.get('management_pref') == 'no_owner' else '' }}>房東不住 (no_owner)</option>
                </select>
                <div class="hint">此類型適合的管理模式</div>
            </div>
            
            <!-- 5. 房型偏好 (S_type) -->
            <div class="form-group">
                <label>🛏️ 房型偏好 (S_type) - 權重 0.8</label>
                <select name="room_type" style="padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; width: 100%;">
                    <option value="" {{ 'selected' if not persona.algo_config or not persona.algo_config.get('room_type') else '' }}>不限</option>
                    <option value="shared" {{ 'selected' if persona.algo_config and persona.algo_config.get('room_type') == 'shared' else '' }}>雅房 (shared)</option>
                    <option value="studio" {{ 'selected' if persona.algo_config and persona.algo_config.get('room_type') == 'studio' else '' }}>套房 (studio)</option>
                    <option value="apartment" {{ 'selected' if persona.algo_config and persona.algo_config.get('room_type') == 'apartment' else '' }}>整層/家庭式 (apartment)</option>
                </select>
                <div class="hint">此類型偏好的房型</div>
            </div>
            
            <!-- 6. 關鍵字已在上方設定 -->
            <div class="hint" style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin-top: 10px;">
                💡 <strong>關鍵字加權 (S_keyword)</strong> - 權重 0.5：已於「基本資訊」區塊設定，AI 會比對對話內容給予額外加分（上限 20 分）。
            </div>
            
            <div class="form-group checkbox-group" style="margin-top: 20px;">
                <input type="checkbox" name="active" id="active" {{ 'checked' if persona.active else '' }}>
                <label for="active" style="margin: 0;">啟用此類型</label>
            </div>
            
            <div class="actions">
                <button type="submit" class="btn btn-primary">💾 儲存</button>
                <a href="/" class="btn btn-secondary">← 返回</a>
                {% if not is_new %}
                <form action="/persona/{{ persona.persona_id }}/delete" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-danger" 
                            onclick="return confirm('⚠️ 確定要刪除此類型嗎？這將無法復原！')">
                        🗑️ 刪除
                    </button>
                </form>
                {% endif %}
            </div>
        </form>
    </div>
</body>
</html>
"""


@app.route("/persona/new", methods=["GET", "POST"])
def persona_new():
    """新增人物誌"""
    import json
    
    if request.method == "POST":
        persona_id = request.form.get("persona_id", "").strip()
        
        # 檢查是否已存在
        existing = db_session.query(Persona).filter_by(persona_id=persona_id).first()
        if existing:
            flash(f"❌ 類型代碼 {persona_id} 已存在")
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
        
        flash(f"✅ 已新增類型：{persona.name}")
        return redirect(url_for("index"))
    
    # 空白的 Persona 物件
    class EmptyPersona:
        persona_id = ""
        name = ""
        description = ""
        keywords = []
        algo_config = {}
        active = True
    
    return render_template_string(PERSONA_EDIT_TEMPLATE, persona=EmptyPersona(), is_new=True)


@app.route("/persona/<persona_id>", methods=["GET", "POST"])
def persona_edit(persona_id):
    """編輯人物誌"""
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    if not persona:
        flash("❌ 類型不存在")
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
        flash(f"✅ 已更新：{persona.name}")
        return redirect(url_for("index"))
    
    return render_template_string(PERSONA_EDIT_TEMPLATE, persona=persona, is_new=False)


@app.route("/persona/<persona_id>/toggle", methods=["POST"])
def persona_toggle(persona_id):
    """切換人物誌啟用狀態"""
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    if persona:
        persona.active = not persona.active
        db_session.commit()
        status = "啟用" if persona.active else "停用"
        flash(f"✅ 已{status}：{persona.name}")
    return redirect(url_for("index"))


@app.route("/persona/<persona_id>/delete", methods=["POST"])
def persona_delete(persona_id):
    """刪除人物誌"""
    persona = db_session.query(Persona).filter_by(persona_id=persona_id).first()
    if persona:
        name = persona.name
        db_session.delete(persona)
        db_session.commit()
        flash(f"✅ 已刪除：{name}")
    return redirect(url_for("index"))


# 審核詳情頁模板
VERIFICATION_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>審核詳情 - Chi Soo 管理後台</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 30px; }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .card h2 { color: #333; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px; }
        .info-item { padding: 15px; background: #f8f9fa; border-radius: 8px; }
        .info-item label { font-weight: 600; color: #666; font-size: 12px; display: block; margin-bottom: 5px; }
        .info-item span { font-size: 16px; color: #333; }
        .image-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .image-card { text-align: center; }
        .image-card img { max-width: 100%; border-radius: 10px; border: 2px solid #ddd; }
        .image-card p { margin-top: 10px; font-weight: 600; color: #666; }
        .actions { display: flex; gap: 15px; margin-top: 20px; justify-content: center; }
        .flash { padding: 15px; border-radius: 8px; margin-bottom: 20px; background: #10b981; color: white; }
        .badge { padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: bold; }
        .badge-pending { background: #fef3c7; color: #d97706; }
        .badge-verified { background: #d1fae5; color: #059669; }
        .badge-rejected { background: #fee2e2; color: #dc2626; }
        textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; min-height: 80px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 審核詳情</h1>
        
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        {% for message in messages %}
        <div class="flash">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}
        
        <div class="card">
            <h2>👤 學生資訊 <span class="badge badge-{{ v.status }}" style="float: right;">{{ v.status }}</span></h2>
            <div class="info-grid">
                <div class="info-item">
                    <label>姓名</label>
                    <span>{{ v.name }}</span>
                </div>
                <div class="info-item">
                    <label>學號</label>
                    <span><code>{{ v.student_id }}</code></span>
                </div>
                <div class="info-item">
                    <label>系級</label>
                    <span>{{ v.dept }}</span>
                </div>
                <div class="info-item">
                    <label>提交時間</label>
                    <span>{{ v.submitted_at.strftime('%Y-%m-%d %H:%M') if v.submitted_at else '-' }}</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📷 學生證照片</h2>
            <div class="image-grid">
                <div class="image-card">
                    <img src="/uploads/verifications/{{ v.front_image_path }}" alt="正面" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22><rect fill=%22%23eee%22 width=%22400%22 height=%22300%22/><text x=%22200%22 y=%22150%22 text-anchor=%22middle%22 fill=%22%23999%22>圖片載入失敗</text></svg>'">
                    <p>正面（有照片）</p>
                </div>
                <div class="image-card">
                    <img src="/uploads/verifications/{{ v.back_image_path }}" alt="反面" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 400 300%22><rect fill=%22%23eee%22 width=%22400%22 height=%22300%22/><text x=%22200%22 y=%22150%22 text-anchor=%22middle%22 fill=%22%23999%22>圖片載入失敗</text></svg>'">
                    <p>反面（註冊章）</p>
                </div>
            </div>
        </div>
        
        {% if v.status == 'pending' %}
        <div class="card">
            <h2>⚙️ 審核操作</h2>
            <form action="/verification/{{ v.id }}/approve" method="POST" style="margin-bottom: 15px;">
                <button type="submit" class="btn btn-success" onclick="return confirm('確定通過此驗證申請？')">
                    ✅ 通過審核
                </button>
            </form>
            <form action="/verification/{{ v.id }}/reject" method="POST">
                <label style="font-weight: 600; margin-bottom: 8px; display: block;">拒絕原因（選填）</label>
                <textarea name="note" placeholder="例：照片模糊、資料不符等..."></textarea>
                <button type="submit" class="btn btn-danger" style="margin-top: 10px;" onclick="return confirm('確定拒絕此驗證申請？')">
                    ❌ 拒絕審核
                </button>
            </form>
        </div>
        {% elif v.reviewer_note %}
        <div class="card">
            <h2>📝 審核備註</h2>
            <p>{{ v.reviewer_note }}</p>
            <p style="color: #666; margin-top: 10px;">審核時間：{{ v.reviewed_at.strftime('%Y-%m-%d %H:%M') if v.reviewed_at else '-' }}</p>
        </div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="/" class="btn btn-secondary">← 返回首頁</a>
        </div>
    </div>
</body>
</html>
"""


@app.route("/verification/<int:verification_id>")
def verification_detail(verification_id):
    """審核詳情頁"""
    v = db_session.query(Verification).filter_by(id=verification_id).first()
    if not v:
        flash("❌ 驗證申請不存在")
        return redirect(url_for("index"))
    
    return render_template_string(VERIFICATION_DETAIL_TEMPLATE, v=v)


@app.route("/verification/<int:verification_id>/approve", methods=["POST"])
def verification_approve(verification_id):
    """通過驗證"""
    from datetime import datetime
    
    v = db_session.query(Verification).filter_by(id=verification_id).first()
    if not v:
        flash("❌ 驗證申請不存在")
        return redirect(url_for("index"))
    
    # 更新驗證狀態
    v.status = VerificationStatus.VERIFIED
    v.reviewed_at = datetime.utcnow()
    
    # 更新使用者驗證狀態
    user = db_session.query(User).filter_by(user_id=v.user_id).first()
    if user:
        user.verification_status = VerificationStatus.VERIFIED
    
    db_session.commit()
    flash(f"✅ 已通過 {v.name} 的驗證申請")
    return redirect(url_for("index"))


@app.route("/verification/<int:verification_id>/reject", methods=["POST"])
def verification_reject(verification_id):
    """拒絕驗證"""
    from datetime import datetime
    
    v = db_session.query(Verification).filter_by(id=verification_id).first()
    if not v:
        flash("❌ 驗證申請不存在")
        return redirect(url_for("index"))
    
    # 更新驗證狀態
    v.status = VerificationStatus.REJECTED
    v.reviewed_at = datetime.utcnow()
    v.reviewer_note = request.form.get("note", "").strip()
    
    # 更新使用者驗證狀態
    user = db_session.query(User).filter_by(user_id=v.user_id).first()
    if user:
        user.verification_status = VerificationStatus.REJECTED
    
    db_session.commit()
    flash(f"❌ 已拒絕 {v.name} 的驗證申請")
    return redirect(url_for("index"))


@app.route("/uploads/verifications/<filename>")
def serve_verification_image(filename):
    """提供驗證圖片檔案"""
    import os
    upload_folder = os.path.join(os.getcwd(), "uploads", "verifications")
    return send_from_directory(upload_folder, filename)


@app.route("/reset-verification/<user_id>", methods=["POST"])
def reset_verification(user_id):
    """重置使用者驗證狀態"""
    import os
    
    # 1. 查找使用者
    user = db_session.query(User).filter_by(user_id=user_id).first()
    if not user:
        flash(f"❌ 使用者 {user_id} 不存在")
        return redirect(url_for("index"))
        
    # 2. 刪除驗證紀錄
    verifications = db_session.query(Verification).filter_by(user_id=user_id).all()
    upload_folder = os.path.join(os.getcwd(), "uploads", "verifications")
    
    count = 0
    for v in verifications:
        # 嘗試刪除圖片檔案
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
    
    # 3. 重置使用者狀態
    user.verification_status = 'unverified'
    db_session.commit()
    
    flash(f"✅ 已重置 {user.display_name or user_id} 的驗證狀態 (刪除 {count} 筆申請紀錄)")
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("=" * 50)
    print("🦔 Chi Soo 管理後台")
    print("=" * 50)
    print()
    print("📌 開啟瀏覽器前往: http://localhost:8000")
    print("   按 Ctrl+C 停止")
    print()
    app.run(host="0.0.0.0", port=8000, debug=True)
