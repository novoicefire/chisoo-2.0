# **專案設計說明書：Puli Rental Consultant Bot (Chi Soo 租屋小幫手)**

**專案名稱**：Puli Rental Consultant Bot (Chi Soo 租屋小幫手)

**適用場域**：國立暨南國際大學 (埔里地區)

**平台載體**：LINE Official Account (LINE Bot)

**核心技術**：Python Flask, Local Ollama AI, LIFF, Flex Message, Cloudflare Tunnel, Google Maps API

## **1\. 專案概述 (Project Overview)**

### **1.1 核心痛點與轉型策略 (Pivot Strategy)**

* **原始痛點**：埔里地區房源分散（臉書社團、布告欄），且學生團隊無法維護「即時空房狀態」，導致資訊經常過期，使用者體驗不佳。  
* **解決方案**：從「即時空房媒合平台」轉型為 **「顧問式租屋推薦系統」**。  
* **運作邏輯**：  
  * 不保證房源「當下可租」，而是推薦「這類型的房源最適合你」。  
  * 透過 AI 分析使用者特質（人物誌），匹配最契合的居住類型與代表性房源。  
  * 提供「靜態資料庫」查詢，如過往評價、房東黑名單/紅名單、地理位置優勢等長效資訊。

### **1.2 系統目標**

1. **智慧化諮詢**：透過對話識別用戶隱性需求（如：怕吵、倒垃圾痛點）。  
2. **降低資訊焦慮**：不顯示所有房源，只推薦「高匹配度」的精選結果。  
3. **建立信任機制**：透過真實學生評價與 LINE Login 驗證，提供可信的參考依據。

## **2\. 系統架構設計 (System Architecture)**

### **2.1 技術堆疊 (Tech Stack)**

* **前端介面**：LINE Messaging API  
  * **Rich Menu**：主控制台。  
  * **Flex Message**：互動式卡片（診斷書、房源卡）。  
  * **LIFF (LINE Front-end Framework)**：處理複雜資訊（地圖、長列表）與表單交互（評價）。  
* **後端與基礎設施**：  
  * **Server**：Python (Flask 或 FastAPI)，運行於本地電腦。  
  * **Messaging Protocol**：**Strictly Reply API Only** (嚴格限制僅使用免費的 Reply Token 回覆訊息，絕不使用 Push API 以節省成本)。  
  * **AI Engine**：本地部署 Ollama，採用 **雙模型協作架構 (Model Chaining)**：  
    1. **gemma3:4b**：負責 NLU (自然語言理解)，從使用者對話中**提取標籤與參數**。  
    2. **gemma3:1b**：負責 Logic & NLG (邏輯檢查與生成)，確認資料完整性並**生成追問語句**。  
  * **Network Tunnel**：**Cloudflare Tunnel** (將本地 localhost 伺服器掛載至自有網域，供 LINE Webhook 呼叫)。  
  * **Persistence (持久化儲存)**：**SQLite / PostgreSQL** (取代 Redis，將對話狀態寫入硬碟，確保使用者可隨時中斷並續答)。  
  * **External API**：**Google Maps Platform** (使用 Distance Matrix API 計算通勤時間)。

### **2.2 系統流程圖 (System Flow)**

graph TD  
    User\[使用者\] \--\> LINE\[LINE 聊天室\]  
    LINE \--\> Cloudflare\[Cloudflare Tunnel\\n(\[https://chiran.online\](https://chiran.online))\]  
    Cloudflare \--\> LocalServer\[本地電腦 (Localhost)\]  
      
    subgraph Local\_PC \[單機部署環境\]  
        LocalServer \--\> Flask\[Python Flask Server\]  
        Flask \-- 1\. 讀取狀態 \--\> DB\[(本機資料庫)\]  
        Flask \--\> RichMenu\_Logic{狀態判斷與邏輯}  
          
        %% 測試模式 (雙模型流水線)  
        RichMenu\_Logic \-- 測試模式 \--\> AI\_Flow\[AI 對話流水線\]  
          
        AI\_Flow \-- Stage 1: 分析 \--\> Ollama4b\[Ollama: gemma3:4b\\n(提取參數 JSON)\]  
        Ollama4b \--\> AI\_Flow  
          
        AI\_Flow \-- Stage 2: 決策 \--\> Ollama1b\[Ollama: gemma3:1b\\n(檢查缺漏 & 追問)\]  
        Ollama1b \-- 資料不足: 產生問題 \--\> Flask  
        Ollama1b \-- 資料齊全: 確認完成 \--\> Confirm\[發送確認訊息\\n"資料已齊全，請輸入'開始分析'"\]  
          
        Confirm \--\> UserInput\[使用者輸入: "開始分析"\]  
        UserInput \--\> Algorithm\[進入匹配算法\]  
          
        AI\_Flow \-- 更新進度 \--\> DB  
          
        %% 資料存取  
        RichMenu\_Logic \-- 一般模式 \--\> CheckInput{檢查輸入內容}  
        CheckInput \-- 是指令/Postback \--\> Execute\[執行對應功能\]  
        CheckInput \-- 非指令文字 \--\> AutoReply\[腳本自動回覆功能列表\]  
          
        %% 動態配置  
        Flask \-- 讀取匹配邏輯 \--\> PersonaTable\[Personas 表\\n(動態人物誌庫)\]  
    end  
      
    Flask \--\> LINE\_API\[回傳 LINE API (Reply Token)\]  
    LINE\_API \--\> User

### **2.3 部署與網路架構 (Deployment Architecture)**

本專案採用 **「全本地單機部署 (All-in-One Localhost)」** 架構，以降低營運成本並確保 AI 運算效能。

1. **硬體環境**：  
   * 單一台高效能電腦（Local PC）同時運行 **Web Server (Flask)** 與 **Ollama (同時載入 4b 與 1b 模型)**。  
   * **優勢**：零延遲調用 AI，無需支付昂貴的 Cloud GPU 費用。  
2. **AI 調用方式**：  
   * Flask 透過 POST /api/generate 呼叫 Ollama，並在 model 參數中分別指定 gemma3:4b 或 gemma3:1b。  
   * 兩模型串聯運行：先呼叫 4b 取得 JSON，再將 JSON 餵給 1b 判斷下一步。  
3. **外部連接 (Cloudflare Tunnel)**：  
   * 由於 LINE Bot Webhook 需要公開的 HTTPS 網址，本專案使用 **Cloudflare Tunnel (cloudflared)**。  
   * **流程**：LINE Server \-\> 自有網域 (https://chiran.online) \-\> Cloudflare Edge \-\> 加密通道 \-\> 本地電腦 (localhost:5000)。  
   * **優勢**：無需設定路由器 Port Forwarding，無需固定 IP，安全性高。

## **3\. 核心功能邏輯：雙模式系統 (Dual Mode Logic)**

系統預設為「安靜的一般模式」，只有在明確指令下才會喚醒 AI。

### **3.1 一般模式 (Idle Mode / Tool Mode)**

* **狀態標記**：status \= "IDLE" (儲存於資料庫 user\_sessions 表)  
* **行為邏輯**：  
  * **AI 保持禁用**：此模式下完全不調用 AI 模型，確保系統效能並防止誤觸發。  
  * **腳本自動回覆 (Auto-Reply Script)**：  
    * **觸發條件**：當使用者輸入任何**非指令文字**（即不是 Rich Menu Postback，也不是「開始分析」等特定關鍵字）。  
    * **系統行為**：系統使用 Reply API 自動回覆一則固定的 **「功能導覽訊息」**。  
    * **訊息範例**：「你好！我是 Chi Soo 租屋小幫手 🦔  
      抱歉，我現在聽不懂一般的文字對話。請使用下方的選單來操作：  
      🔍 幫我找窩：AI 幫你分析適合的租屋類型  
      🏆 評價排行榜：看看大家推薦哪裡  
      📚 租屋小Tips：簽約與看房須知  
      ❤️ 我的收藏：查看已儲存的房源  
      若要開始找房測驗，請點擊選單左上角的『幫我找窩』！」  
  * 響應 **Rich Menu Postback** 或特定關鍵字（如「我的收藏」）執行對應功能。  
* **主要功能**：  
  * **評價排行榜**：顯示 Top 10 熱門房源。  
  * **租屋小 Tips**：圖文教學（合約注意事項、看房檢核表）。  
  * **我的收藏**：查看已收藏的房源清單。  
  * **外部連結 (LIFF)**：評價填寫、地圖搜尋。

### **3.2 測試模式 (Testing Mode / AI Consultant)**

* **狀態標記**：status \= "TESTING" (儲存於資料庫，永久保存直到完成)  
* **觸發條件**：點擊 Rich Menu 左上角 **「幫我找窩」**。  
* **行為邏輯**：  
  * **鎖定狀態**：使用者輸入的所有文字都會被傳送至後端進行 AI 分析。  
  * **中斷與恢復機制 (Interrupt & Resume Logic)**：  
    * **中斷觸發**：若使用者在測驗中途點擊其他 Rich Menu 功能（如「評價排行榜」），系統執行以下動作：  
      1. **Multi-Message Reply (多則訊息回覆)**：利用單一 Reply Token，一次發送兩則訊息 (Messaging API 上限為 5 則)。  
         * **Message 1 (功能回應)**：優先回傳使用者請求的內容（如：排行榜 Flex Message）。  
         * **Message 2 (中斷提示)**：緊接著發送一則文字訊息：「⚠️ 對話已暫時中斷  
           您的找房進度已自動儲存。若要繼續與 AI 對話，請隨時點擊選單左上角的 『幫我找窩』。」  
      2. **狀態更新**：將使用者狀態暫時切回 IDLE，但保留 collected\_data。  
    * **恢復**：當使用者再次點擊「幫我找窩」時，後端檢查 UserSessions 表：  
      * **若有未完成資料**：系統回覆：「嗨！Chi Soo 發現您上次的諮詢進行到一半。要繼續嗎？」  
        * **\[▶️ 繼續測驗\]** (Postback: action=resume\_test)：恢復 TESTING 狀態，AI 讀取資料庫進度，直接提出**下一個問題**。  
        * **\[🔄 重新開始\]** (Postback: action=restart\_test)：清空 collected\_data，重頭開始問第一題。  
      * **若無資料**：直接開始新的測驗。  
  * **雙階段 AI 處理 (Two-Stage Processing)**：  
    1. **提取 (Extraction)** \- **gemma3:4b**：  
       * 將使用者的自然語言（如「我要便宜一點」）轉換為結構化資料（如 {"budget\_trend": "low"}）。  
       * 只負責「翻譯」，不負責判斷是否結束對話。  
    2. **確認與追問 (Confirmation & Inquiry)** \- **gemma3:1b**：  
       * 接收 4b 提取出的資料 \+ 目前已收集的資料。  
       * 判斷核心變因（預算、地點、設施）是否齊全。  
       * **若缺漏**：生成一道自然的追問句（如「了解，那您希望靠近市區還是學校呢？」）。  
       * **若齊全**：輸出 COMPLETE 訊號。  
  * **自動結束與確認**：  
    * 當 1b 模型判定資料齊全 (COMPLETE)，AI **不直接輸出結果**，而是回覆：「好的！我已經了解您的需求了。請輸入 **『開始分析』** 來查看您的專屬租屋人格診斷。」  
    * 等待使用者輸入「開始分析」後，才觸發後端演算法，並展示**診斷書卡片**（此時不含房源，僅含診斷結果與「顯示推薦房源」按鈕）。  
    * 使用者點擊「顯示推薦房源」按鈕後，才載入房源卡片並切回 IDLE。

## **4\. 租屋類型分類與匹配邏輯 (Dynamic Persona System)**

為確保系統彈性，人物誌（Persona）**完全不寫死在程式碼中**。系統啟動時會從資料庫 Personas 表載入所有設定。這意味著管理員可以透過資料庫隨時執行以下操作，而無需修改程式碼：

1. **增減分類數量**：例如新增第 6 種「寵物友善型」。  
2. **修改類型名稱**：例如將「省錢戰士型」改名為「高 CP 值型」。  
3. **調整核心關鍵字**：隨時更新 AI 識別的觸發詞（例如新增流行語）。  
4. **微調演算法參數**：調整門檻值或加權權重，即時優化推薦邏輯。

**⚠️ 注意：演算法實作細節**

本章節僅描述「動態資料結構」。詳細的匹配分數計算公式、權重邏輯與 6 大指標 ($S\_{budget}, S\_{location}...$) 的數學定義，請參閱另一份技術文件：  
📄 Matching\_Algorithm\_Formulas.md (租屋類型匹配演算法公式說明書)

### **4.1 動態配置結構**

每個分類由以下參數動態定義：

* **基本資訊**：名稱 (Name)、描述 (Description)、代表圖片。  
* **核心關鍵字 (Keywords)**：JSON 陣列字串。AI 分析時若出現這些詞，演算法會自動增加該分類的權重。  
* **演算法參數 (Algorithm Config)**：儲存於 JSON 欄位，定義該分類的「門檻值」與「加權項目」。

### **4.2 預設分類 (Initial Seed Data)**

以下為系統初始化時預計匯入的 5 種範例分類（僅為資料庫初始值，**可完全自定義**）：

| 類型代碼 | 類型名稱 | 演算法參數範例 (Algorithm Config JSON) | 核心關鍵字 (Keywords) |
| :---- | :---- | :---- | :---- |
| **A** | **省錢戰士型** | {"rent\_max": 3500, "noise\_tolerance": "high", "room\_type": "shared"} | 便宜、雅房、睡覺就好 |
| **B** | **懶人貴族型** | {"rent\_min": 5500, "required": \["garbage", "elevator"\]} | 子母車、電梯、近市區 |
| **C** | **安全堡壘型** | {"required": \["security"\], "bonus": \["landlord\_live\_in"\]} | 門禁、監視器、限女/男 |
| **D** | **社交群居型** | {"room\_type": "apartment", "required": \["living\_room"\]} | 客廳、整層、可開伙 |
| **E** | **質感獨享型** | {"house\_age\_max": 5, "required": \["balcony", "laundry"\]} | 裝潢、新屋、獨洗獨曬 |

## **5\. 使用者介面設計細節 (UI/UX Specification)**

### **5.1 Rich Menu 設計 (6 格選單)**

* **左上：幫我找窩** (Action: Postback start\_test) \-\> **觸發 AI**  
* **中上：評價排行榜** (Action: Postback show\_ranking) \-\> **觸發「社群好評榜」與「租屋停看聽」雙排輪播**  
* **右上：租屋小Tips** (Action: Postback show\_tips) \-\> **觸發「情境式知識圖卡」(Carousel)**  
* **左下：我的收藏** (Action: Postback show\_fav) \-\> 回傳收藏列表 (Flex Message Carousel)  
* **中下：評價系統** (Action: URI https://liff.../review) \-\> **開啟 LIFF**  
* **右下：地圖式搜尋** (Action: URI https://liff.../map) \-\> **開啟 LIFF**

### **5.2 推薦結果展示 (分階段展示流程)**

當使用者輸入「開始分析」後，系統**不會一次噴出所有結果**，而是分兩階段進行：

#### **第一階段：診斷書卡片 (Diagnosis Card)**

觸發時機：使用者輸入「開始分析」。  
內容：單張 Flex Message Bubble。

1. **Header**：大大的診斷標題（如「你是：懶人貴族型」）。  
2. **Body**：雷達圖分析 (便利性/價格/安全性) 與診斷文案。  
3. **Footer**：單一顆明顯的按鈕 —— **「🏠 顯示推薦房源」** (Postback Action: show\_recommendations).

#### **第二階段：房源卡片旋轉木馬 (Housing Carousel)**

觸發時機：使用者點擊「顯示推薦房源」按鈕。  
內容：Flex Message Carousel。

1. **第 1\~5 張：精選房源卡 (Housing Card)**  
   * **Header (圖片)**：房源照片 \+ 左上角標籤 (租金 $5,500)。  
   * **Body (資訊)**：房源名稱、評分、匹配度 (92% 🔥)、推薦理由。  
   * **Footer (互動)**：  
     * $$❤️ 收藏$$  
       (Postback)：點擊後，後端將該房源加入資料庫，並自動回覆訊息：「**已加入收藏清單！透過點選 Menu 上的『我的收藏』來查看所有收藏。**」  
     * $$📄 查看詳情$$  
       (LIFF URI)  
     * $$✍️ 我要評價$$  
       (LIFF URI)  
2. **最後一張：分頁或結尾卡片 (Pagination / End Card)**  
   * **顯示邏輯**：  
     * **批次限制**：為確保手機版面閱讀舒適，嚴格限制每次僅載入 **5 間** 房源。  
     * **情境 A (還有房源)**：顯示「查看更多」卡片。  
     * **情境 B (已無房源)**：顯示「已顯示所有適合房源」卡片，並引導查看其他類型。  
   * **卡片內容設計**：  
     * **情境 A \- 查看更多**：  
       * **標題**：還有更多適合你的窩...  
       * **動作**：點擊後觸發 Postback，載入下一批 (Offset \+5)。  
     * **情境 B \- 結尾建議 (End of List)**：  
       * **標題**：已顯示所有符合「懶人貴族型」的精選房源。  
       * **文案**：沒看到心動的嗎？或許您可以參考其他類型的房源。  
       * **按鈕**：  
         1. **🔍 查看其他推薦類型** (觸發後端顯示次高分的 Persona 推薦)  
         2. **🏠 回到主選單**

### **5.3 LIFF 頁面設計**

1. **房源詳情頁 (Detail View)**  
   * 展示多張高畫質照片 (Carousel)。  
   * 詳細文字介紹、租金包含項目。  
   * **地圖與通勤資訊**：嵌入 Google Maps，並串接 **Google Maps Distance Matrix API**，自動計算該房源通往「國立暨南國際大學」的機車/公車通勤時間。  
   * **社群評價區**：顯示過往學長姐的留言（資料來源：問卷調查）。  
     * **免責聲明**：標註「本區評價來自學生匿名問卷，內容僅供參考，不代表平台立場，且不保證內容之完全真實性。」  
2. **評價系統首頁 (Review Portal)**  
   * **我的評價 (My Reviews)**：  
     * 列表顯示該使用者所有已提交的評價。  
     * **狀態標籤**：審核中 (Pending)、已發布 (Published)、已駁回 (Rejected)。  
     * **操作**：  
       * 點擊「已駁回」可查看駁回理由（如：照片模糊、內容不雅）。  
       * **刪除功能**：使用者可自行刪除已發布或審核中的評價。  
   * **新增評價 (Write Review)**：  
     * **房源搜尋**：透過地址或房源名稱搜尋系統中的房源進行評價。  
     * **填寫表單** (同原設計，含星等、評論、照片)。  
     * **學生證驗證** (必填，上傳圖片)。  
   * **⚠️ 防刷機制 (Rate Limiting)**：  
     * **規則**：後端限制每個 LINE User ID 每日（00:00 \- 23:59）最多只能提交 **3 篇** 評價。  
     * **即時顯示**：在「新增評價」頁面頂部或提交按鈕旁，**明確標示「今日剩餘額度：X 篇」**，讓使用者在開始填寫前就能知道是否還有額度。  
     * **提示**：若超過額度，前端顯示「您今日的評價次數已達上限，請明日再來。」  
3. **地圖式搜尋 (Map Search UI)**  
   此介面採用「單頁地圖應用 (Map-Based SPA)」設計，整合了瀏覽與詳細資訊展示，讓使用者在不離開地圖的情況下獲取所有資訊。  
   * **介面佈局 (Layout)**：  
     * **全螢幕地圖 (Fullscreen Map)**：作為底層，顯示埔里地區 Google Maps。  
     * **頂部導航列 (Top Bar)**：  
       * 搜尋框：搜尋路名或房源名稱。  
       * 篩選按鈕：篩選租金、類型 (雅房/套房)。  
     * **懸浮定位按鈕 (Floating Action Button \- FAB)**：位於右下角，點擊可切換視角至 **「📍 我的 GPS 位置」** 或 **「🏫 暨大校區」**。  
   * **標記與互動 (Markers & Interaction)**：  
     * **顯示邏輯**：僅針對資料庫中**有明確經緯度**的房源顯示紅色圖釘。  
     * **點擊圖釘 (On Marker Click)**：  
       * 視角移動：地圖自動平滑移動，將該房源置中。  
       * **彈出摘要卡 (Bottom Sheet)**：螢幕下方滑出一張「房源摘要卡」(高度約螢幕 25%)，顯示圖片、名稱、價格、評分。  
   * **詳情彈窗 (Detail Modal/Overlay)**：  
     * **觸發**：點擊下方的「房源摘要卡」。  
     * **行為**：摘要卡向上展開，變成**全螢幕或半版彈窗 (Modal)**，覆蓋在地圖上層。  
     * **內容**：載入與 **「1. 房源詳情頁」** 完全相同的內容 (照片輪播、評論、設施列表)。  
     * **關閉**：彈窗左上角設有 **「✕ 關閉」** 按鈕。點擊後，彈窗縮回下方的摘要卡，**使用者回到地圖介面**，可繼續瀏覽其他房源。  
   * **外部觸發 (Deep Linking)**：  
     * 若使用者是從 Flex Message 點擊「查看詳情」進入此頁面，系統會自動定位到該房源，並直接展開詳情彈窗。

### **5.4 管理者後台 (Admin Panel) \- 新增**

專為管理員設計的 Web 介面，用於審核與管理評價。**注意：此後台僅操作資料庫狀態，不發送 LINE 通知，以符合 Reply API 限制。**

* **登入機制**：簡單的管理員帳號密碼。  
* **功能模組**：  
  * **待審核列表 (Pending Reviews)**：  
    * 顯示使用者上傳的學生證圖片、評價內容、房源名稱。  
    * **操作按鈕**：  
      * ✅ **通過 (Approve)**：更新資料庫狀態為 approved，刪除學生證暫存檔。**（不發送通知，使用者需自行查看 LIFF）**  
      * ❌ **駁回 (Reject)**：更新資料庫狀態為 rejected，並填寫駁回理由。  
  * **評價管理 (Review Management)**：  
    * 搜尋/篩選已上架的評價。  
    * 提供 **下架 (Unpublish)** 功能，以應對後續爭議或房東申訴。

### **5.5 我的收藏 (My Favorites) \- 更新**

當使用者點擊 Rich Menu 的「我的收藏」時，回傳一組 **Flex Message Carousel (橫向滑動卡片)**。

* **卡片設計**：  
  * **Header (圖片)**：顯示房源封面圖 (Aspect Ratio 20:13)。  
  * **Body (資訊)**：  
    * **大標題**：房源名稱 (如「中山路精緻套房」)。  
    * **副標題**：租金與評分 (如「$5,500/月 | ⭐ 4.2」)。  
  * **Footer (按鈕)**：  
    * $$📄 查看房源卡片$$  
      (Postback)：點擊後，觸發顯示該房源的完整 Flex Message (同推薦結果中的房源卡)，方便使用者進行查看詳情、評價或移除收藏等操作。  
* **空狀態處理**：若無收藏，回傳文字訊息：「您目前沒有收藏任何房源，快去『幫我找窩』看看吧！」

### **5.6 評價排行榜 (Community Leaderboard) \- 新增**

當使用者點擊 Rich Menu 的「評價排行榜」時，系統將回傳**兩組獨立的 Flex Message Carousel (雙排輪播)**，分別展示社群評分最高與最低的房源。

* **第一組：🏆 社群好評榜 (Top 5\)**  
  * **邏輯**：取資料庫平均評分最高的 5 間。  
  * **視覺**：使用 **綠色/金色** 標題或邊框，營造正面氛圍。  
  * **標籤 (Badge)**：**「社群推薦」**。  
  * **免責文案**：卡片下方微字標註 **「評價僅供參考」**。  
* **第二組：⚠️ 租屋停看聽 (Bottom 5\)**  
  * **邏輯**：取資料庫平均評分最低的 5 間。  
  * **視覺**：使用 **橘色/黃色** 警示色 (避免使用紅色或直接寫「爛」，降低法律風險)。  
  * **標籤 (Badge)**：**「多加留意」** (取代「不推薦」等強烈負面字眼)。  
  * **內容**：除了房源資訊外，摘要顯示爭議點 (例如：「隔音反應較多」)。

### **5.7 租屋小Tips (Survival Guide) \- 新增**

當使用者點擊 Rich Menu 的「租屋小Tips」時，回傳一組 **Flex Message Carousel (情境式知識圖卡)**，包含三個核心主題：

1. **主題一：👀 看房前 (避雷針)**  
   * **封面圖**：放大鏡與房屋。  
   * **內容摘要**：如何辨識假房東、看房檢核表（採光、壁癌、手機訊號）、訂金與押金的區別。  
   * **按鈕**：\[📖 閱讀看房攻略\] (開啟 LIFF 文章或回傳長圖)。  
2. **主題二：✍️ 簽約時 (保命符)**  
   * **封面圖**：合約書與筆。  
   * **內容摘要**：  
     * **轉租陷阱**：民法第444條，轉租轉的是使用權，不是責任（損壞你要賠）。  
     * **合約審閱期**：你有權利把合約帶回去看 3 天。  
     * **修繕責任**：燈泡壞了誰修？合約沒寫就是房東修。  
   * **按鈕**：\[⚖️ 查看合約重點\] (顯示重點整理圖)。  
3. **主題三：🏠 入住後 (權益書)**  
   * **封面圖**：鑰匙與安心表情。  
   * **內容摘要**：  
     * **租金遲繳**：民法第440條，遲繳未達 2 個月，房東不能趕你走。  
     * **提前解約**：押金最多扣一個月（若有約定）。  
     * **退租點交**：拍照存證，押金 7-14 天內退還。  
   * **按鈕**：\[🛡️ 了解房客權益\] (顯示權益懶人包)。

## **6\. AI 提示詞工程 (Prompt Engineering)**

為確保回應穩定，採用「分工合作」策略。

### **6.1 分析與提取 (System Prompt \- gemma3:4b)**

此模型專注於從對話中提取資訊，**只輸出 JSON，不說話**。

你是一個資料提取員。請分析使用者的輸入，並將其轉換為 JSON 格式。  
請只輸出 JSON，不要包含任何解釋性文字。若使用者提到某個條件，請將其值設為 true/false 或具體數值。

需要提取的欄位：  
\- budget (整數)  
\- location\_pref (市區/學校/偏僻)  
\- garbage\_service (子母車: true/false)  
\- elevator (電梯: true/false)  
\- quiet (安靜: true/false)  
\- type\_pref (房型: 套房/雅房)

輸入範例："我想要找不用追垃圾車的，預算5000"  
輸出範例：{"budget": 5000, "garbage\_service": true}

### **6.2 邏輯確認與追問 (System Prompt \- gemma3:1b)**

此模型專注於對話流控制，**負責決定要「追問」還是「結束」**。

你是一個租屋顧問。  
輸入會包含：1. 目前已收集的資料 (JSON) 2\. 必要的檢查清單 (Checklist)。

任務：  
檢查 JSON 中是否所有 Checklist 的項目都已填寫（不為 null）。  
\- 若資料缺失：請用親切的繁體中文，針對缺失的項目提出\*\*一個\*\*追問問題。  
\- 若資料齊全：請只輸出字串 "COMPLETE"。

Input: {"budget": 5000, "garbage\_service": true}, Checklist: \["location\_pref"\]  
Output: "了解，那請問您希望住在靠近市區還是學校附近呢？"

Input: {"budget": 5000, "location\_pref": "市區"}, Checklist: \["location\_pref"\]  
Output: COMPLETE

## **7\. 資料庫設計概要 (Database Schema)**

### **7.1 Users (使用者主表)**

| Field | Type | Description |
| :---- | :---- | :---- |
| user\_id | String (PK) | LINE User ID |
| display\_name | String | LINE 暱稱 |
| persona\_type | String | 最近一次測驗結果 (如 "Lazy\_Noble") |
| created\_at | DateTime | 加入時間 |

### **7.2 UserSessions (對話狀態表 \- 取代 Redis)**

此表用於儲存測驗進度，確保可隨時中斷並續答。

| Field | Type | Description |
| :---- | :---- | :---- |
| user\_id | String (PK) | LINE User ID (FK) |
| status | String | "IDLE" 或 "TESTING" |
| collected\_data | JSON | 已收集的變因 (如 {"budget": 5000, "elevator": true}) |
| last\_updated | DateTime | 最後互動時間 |

### **7.3 Houses (房源)**

| Field | Type | Description |
| :---- | :---- | :---- |
| house\_id | Integer (PK) | 唯一編號 |
| name | String | 房源名稱 |
| category\_tag | String | 歸屬類型 (關聯至 Personas 表) |
| rent | Integer | 租金 |
| features | JSON | 特徵標籤 (子母車:T, 電梯:F...) |
| image\_url | String | 封面圖連結 |
| avg\_rating | Float | 平均評分 |

### **7.4 Reviews (評價)**

| Field | Type | Description |
| :---- | :---- | :---- |
| review\_id | Integer (PK) |  |
| house\_id | Integer (FK) | 關聯房源 |
| user\_id | String (FK) | 評論者 (LINE ID) |
| rating | Integer | 1-5 星 |
| comment | Text | 評論內容 |
| **status** | **String** | **審核狀態 (pending, approved, rejected)** |
| **student\_card\_img** | **String** | **學生證圖片路徑 (審核通過後建議刪除或加密)** |
| **reject\_reason** | **String** | **駁回原因 (若 status=rejected)** |
| **created\_date** | **Date** | **評價日期 (用於計算每日限額)** |

### **7.5 Personas (人物誌配置庫 \- 新增)**

此表用於動態管理所有租屋類型及其匹配邏輯。

| Field | Type | Description |
| :---- | :---- | :---- |
| persona\_id | String (PK) | 唯一代碼 (如 "type\_A") |
| name | String | 顯示名稱 (如 "省錢戰士型") \- **可編輯** |
| description | Text | 診斷書上的描述文案 \- **可編輯** |
| keywords | JSON | 觸發關鍵字列表 (如 \["便宜", "雅房"\]) \- **可增減** |
| algo\_config | JSON | **匹配演算法參數** (如 {"rent\_max": 3500, "weights": {"price": 0.8}}) |
| active | Boolean | 是否啟用此分類 |

## **8\. 開發分工建議 (Development Plan)**

基於會議記錄的分工規劃：

1. **資料組 (Data Team)**  
   * **任務**：蒐集埔里地區 20-30 間指標性房源資料。  
   * **重點**：不需要確認空房，但要確認「屬性」（是否有子母車、是否限男女、大概租金）。  
   * **產出**：建立 Excel/CSV 檔，並標註每一間房源屬於哪一種 Persona (A\~E)。  
2. **技術組 (Tech Team)**  
   * **任務 A (Infrastructure)**：設定本地開發環境。  
     * 安裝 Ollama 並下載 **gemma3:4b** (分析用) 與 **gemma3:1b** (邏輯用) 兩個模型。  
     * 設定 Cloudflare Tunnel (cloudflared) 並串接自有網域。  
   * **任務 B (Backend)**：架設 Python Flask 與 SQL 資料庫。  
     * 實作 UserSessions 表的讀寫邏輯，確保狀態能持久保存。  
     * **實作 Personas 動態載入邏輯**：系統應讀取 DB 中所有 active=True 的 Personas，並根據其 algo\_config 與 keywords 進行動態匹配，**不可使用 if type \== 'A' 等寫死邏輯**。  
   * **任務 C (AI Integration)**：撰寫 Python 程式碼，透過 API **串接雙模型流水線 (4b \-\> 1b)**。  
   * **任務 D (Frontend)**：設計 Flex Message JSON 樣板 (使用 LINE Flex Message Simulator)。  
   * **任務 E (Admin Panel)**：開發簡單的網頁後台，實作評價審核 (上架/駁回) 與學生證驗證流程。