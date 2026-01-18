# Chi Soo 租屋小幫手 🦔

> 專為埔里地區（國立暨南國際大學）設計的 AI 顧問式租屋推薦系統

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![LINE](https://img.shields.io/badge/LINE-Bot-00C300.svg)](https://developers.line.biz/)

## 📋 專案概述

Chi Soo 是一個基於 LINE Bot 的「顧問式租屋推薦系統」，透過 AI 分析使用者的需求與特質，推薦最適合的租屋類型與房源。

### 核心特色

- 🤖 **雙模型 AI 引擎**：使用本地 Ollama (gemma3:4b + gemma3:1b) 進行對話分析
- 🎯 **六維度匹配演算法**：預算、地段、設施、房東、房型、關鍵字全方位評估
- 📱 **LINE 原生體驗**：Rich Menu、Flex Message、LIFF 完整整合
- 💾 **持久化對話狀態**：可隨時中斷並續答測驗

## 🏗️ 技術架構

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  LINE App   │────▶│  Cloudflare  │────▶│  Flask Server   │
│  (使用者)    │     │   Tunnel     │     │  (localhost)    │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             ▼                             │
                    │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
                    │  │   Ollama     │    │  PostgreSQL  │    │   LIFF       │ │
                    │  │  (AI 引擎)   │    │   (資料庫)    │    │  (前端頁面)   │ │
                    │  │ gemma3:4b/1b │    │              │    │  Next.js     │ │
                    │  └──────────────┘    └──────────────┘    └──────────────┘ │
                    │                     本地開發環境                           │
                    └───────────────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 前置需求

- Python 3.10+
- PostgreSQL 14+
- Ollama (已安裝 gemma3:4b 與 gemma3:1b)
- LINE Developers 帳號
- Cloudflare 帳號 (用於 Tunnel)

### 安裝步驟

```bash
# 1. 複製專案
git clone https://github.com/your-username/puli-rental-bot.git
cd puli-rental-bot

# 2. 建立虛擬環境
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定環境變數
copy .env.example .env
# 編輯 .env 填入實際值

# 5. 初始化資料庫
python scripts/seed_data.py

# 6. 啟動伺服器
python app/main.py
```

### 設定 Cloudflare Tunnel

```bash
# 安裝 cloudflared
# 下載: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# 登入 Cloudflare
cloudflared login

# 建立 Tunnel
cloudflared tunnel create chisoo

# 啟動 Tunnel
cloudflared tunnel run --url http://localhost:5000 chisoo
```

## 📁 專案結構

```
puli-rental-bot/
├── app/
│   ├── __init__.py          # Flask 應用程式工廠
│   ├── main.py              # Webhook 入口點
│   ├── config.py            # 設定管理
│   ├── models/              # SQLAlchemy ORM Models
│   ├── services/            # 業務邏輯層
│   │   ├── ollama_service.py    # AI 雙模型流水線
│   │   ├── matching_service.py  # 匹配演算法
│   │   └── session_service.py   # 對話狀態管理
│   ├── handlers/            # 事件處理器
│   └── templates/           # Flex Message 模板
├── scripts/                 # 工具腳本
│   └── seed_data.py         # 種子資料初始化
├── .env.example             # 環境變數範例
├── requirements.txt         # Python 依賴
└── README.md
```

## 🎮 功能說明

### 雙模式系統

| 模式 | 狀態 | 行為 |
|------|------|------|
| 一般模式 | IDLE | AI 禁用，回覆功能導覽 |
| 測試模式 | TESTING | AI 啟用，進行對話分析 |

### 五種租屋人物誌

| 代碼 | 名稱 | 特色 |
|------|------|------|
| type_A | 省錢戰士型 | 預算導向，雅房首選 |
| type_B | 懶人貴族型 | 便利優先，子母車必備 |
| type_C | 安全堡壘型 | 安全至上，門禁監視器 |
| type_D | 社交群居型 | 喜歡室友，整層公寓 |
| type_E | 質感獨享型 | 追求品味，新裝潢 |

## 📝 環境變數

| 變數 | 說明 |
|------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Bot Access Token |
| `LINE_CHANNEL_SECRET` | LINE Bot Channel Secret |
| `OLLAMA_BASE_URL` | Ollama API URL |
| `OLLAMA_MODEL_4B` | 分析用模型名稱 |
| `OLLAMA_MODEL_1B` | 邏輯用模型名稱 |
| `DATABASE_URL` | PostgreSQL 連線字串 |
| `BASE_URL` | 對外服務網址 |

## 🧪 測試

```bash
# 執行單元測試
pytest tests/ -v

# 測試匹配演算法
pytest tests/test_matching.py -v

# 測試 Ollama 連線
python -c "from app.services import OllamaService; print(OllamaService().test_connection())"
```

## 📚 相關文件

- [設計規格書](./Puli_Rental_Bot_Design_Spec.md)
- [匹配演算法公式](./Matching_Algorithm_Formulas.md)

## 🤝 貢獻

歡迎提交 Issue 與 Pull Request！

## 📄 授權

MIT License
