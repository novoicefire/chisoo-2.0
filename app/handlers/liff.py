# ============================================================
# handlers/liff.py - LIFF 頁面路由藍圖
# 專案：Chi Soo 租屋小幫手
# 說明：將 LIFF 請求代理到 Next.js 前端應用
# ============================================================

from flask import Blueprint, redirect
from app.config import config

liff_bp = Blueprint("liff", __name__)

# Next.js 部署 URL (Vercel)
NEXT_APP_URL = "https://liff-app-beige.vercel.app"


@liff_bp.route("/detail/<int:house_id>")
def house_detail(house_id: int):
    """
    房源詳情頁 - 重定向到 Next.js
    """
    return redirect(f"{NEXT_APP_URL}/detail/{house_id}")


@liff_bp.route("/review")
def review_portal():
    """
    評價系統首頁 - 重定向到 Next.js
    """
    return redirect(f"{NEXT_APP_URL}/review")


@liff_bp.route("/map")
def map_search():
    """
    地圖式搜尋頁 - 重定向到 Next.js
    """
    return redirect(f"{NEXT_APP_URL}/map")
