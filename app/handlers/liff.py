# ============================================================
# handlers/liff.py - LIFF 頁面路由藍圖
# 專案：Chi Soo 租屋小幫手
# 說明：提供 LIFF 網頁應用的 HTML 頁面路由
# ============================================================

from flask import Blueprint, render_template, send_from_directory
import os

liff_bp = Blueprint(
    "liff", 
    __name__,
    static_folder="../liff/static",
    template_folder="../liff/templates"
)


@liff_bp.route("/detail/<int:house_id>")
def house_detail(house_id: int):
    """
    房源詳情頁
    
    此路由將在 Phase 7 實作，目前回傳佔位頁面
    實際 LIFF 頁面將使用 Next.js 開發
    """
    # TODO: Phase 7 - 整合 Next.js LIFF 應用
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>房源詳情 - Chi Soo</title>
    </head>
    <body>
        <h1>房源詳情頁</h1>
        <p>House ID: {house_id}</p>
        <p>此頁面將在 Phase 7 實作 (Next.js)</p>
    </body>
    </html>
    """


@liff_bp.route("/review")
def review_portal():
    """
    評價系統首頁
    """
    # TODO: Phase 7 - 整合 Next.js LIFF 應用
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>評價系統 - Chi Soo</title>
    </head>
    <body>
        <h1>評價系統</h1>
        <p>此頁面將在 Phase 7 實作 (Next.js)</p>
    </body>
    </html>
    """


@liff_bp.route("/map")
def map_search():
    """
    地圖式搜尋頁
    """
    # TODO: Phase 7 - 整合 Next.js LIFF 應用
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>地圖搜尋 - Chi Soo</title>
    </head>
    <body>
        <h1>地圖式搜尋</h1>
        <p>此頁面將在 Phase 7 實作 (Next.js)</p>
    </body>
    </html>
    """
