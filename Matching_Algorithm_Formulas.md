# **租屋類型匹配演算法公式說明書 (Advanced Version)**

文件版本：v2.0 (Enhanced Logic)  
適用模組：後端邏輯核心 (Backend Core Logic)  
目標：計算使用者 ($User$) 與每一種租屋人物誌 ($Persona\_i$) 之間的 契合度分數 (Compatibility Score)，並排序選出最佳推薦。

## **1\. 核心數學模型 (Core Model)**

總分 $S\_{total}(P\_i)$ 是由六個維度的子分數，經過權重加權後總和而成。

$$S\_{total}(P\_i) \= \\sum\_{k \\in Dimensions} (S\_k \\times W\_k)$$

### **六大維度 ($k$) 與建議權重 ($W\_k$)**

| 維度代號 | 維度名稱 | 權重 (Wk​) | 說明 |
| :---- | :---- | :---- | :---- |
| $S\_{budget}$ | **預算契合度** | **1.5** | 經濟基礎，權重最高，預算不符很難成交。 |
| $S\_{location}$ | **地段便利性** | **1.2** | 交通與生活機能是大學生第二考量。 |
| $S\_{features}$ | **硬體設施** | **1.0** | 子母車、電梯、冷氣等具體設備。 |
| $S\_{landlord}$ | **管理模式** | **1.0** | 房東同住或專業管理，影響居住自由度。 |
| $S\_{type}$ | **房型偏好** | **0.8** | 雅房/套房/家庭式，可視情況妥協。 |
| $S\_{keyword}$ | **語意關鍵字** | **0.5** | AI 從對話中捕捉到的額外加分項。 |

## **2\. 各維度詳細計算公式**

### **2.1 預算契合度 ($S\_{budget}$) \- 使用高斯衰減函數**

不再使用簡單的「符合/不符合」，而是允許「預算稍微爆一點點」。

* $U\_{budget}$：使用者預算上限。  
* $P\_{min}, P\_{max}$：該人物誌 ($P\_i$) 的建議價格區間。  
* $P\_{avg}$：該人物誌的平均價格 $\\frac{P\_{min} \+ P\_{max}}{2}$。

**邏輯**：

1. 若 $U\_{budget}$ 落在 $\[P\_{min}, P\_{max}\]$ 區間內 $\\rightarrow$ **滿分 (100分)**。  
2. 若 $U\_{budget} \< P\_{min}$ (預算不足)：使用指數衰減，每少 1000 元分數大幅下降。  
3. 若 $U\_{budget} \> P\_{max}$ (預算過高)：輕微扣分 (因為有錢人住便宜房是 OK 的，但可能不符身分)。

$$S\_{budget} \= \\begin{cases} 100 & \\text{if } P\_{min} \\le U\_{budget} \\le P\_{max} \\\\ 100 \\times e^{-0.002 \\times (P\_{min} \- U\_{budget})} & \\text{if } U\_{budget} \< P\_{min} \\text{ (預算不足)} \\\\ 90 & \\text{if } U\_{budget} \> P\_{max} \\text{ (預算充裕)} \\\\ 0 & \\text{if } U\_{budget} \\text{ is NULL} \\end{cases}$$  
範例：若 $P\_{min}=5000$，使用者 $U\_{budget}=4500$ (差500元)。  
分數 $\\approx 100 \\times e^{-1} \\approx 36.7$ 分 (預算不足是大硬傷)。

### **2.2 地段與便利性 ($S\_{location}$) \- 矩陣匹配**

使用「偏好矩陣」來定義地點之間的相容性。

* $U\_{loc}$：使用者偏好 (Enum: downtown, school, quiet)。  
* $P\_{loc\\\_list}$：該人物誌包含的地點屬性列表。

$$S\_{location} \= \\begin{cases} 100 & \\text{if } U\_{loc} \\in P\_{loc\\\_list} \\text{ (完全命中)} \\\\ 50 & \\text{if } U\_{loc} \= \\text{'downtown'} \\text{ AND } \\text{'school'} \\in P\_{loc\\\_list} \\text{ (市區跟學校其實不遠，給一半分)} \\\\ 0 & \\text{if } U\_{loc} \\text{ 不在列表內} \\end{cases}$$

### **2.3 設施需求匹配 ($S\_{features}$) \- Jaccard 相似度變體**

計算「使用者想要的功能」在「該人物誌提供的功能」中的覆蓋率。

* $F\_{user}$：使用者許願的功能集合 (如 {子母車, 電梯, 陽台})。  
* $F\_{persona}$：該人物誌的 **必要配備 (**$L\_{req}$**)** 與 **常見配備 (**$L\_{bonus}$**)**。

$$S\_{features} \= \\frac{\\sum\_{f \\in F\_{user}} Score(f)}{|F\_{user}| \\times 30} \\times 100$$

單項得分 $Score(f)$：

* **\+30**：若 $f \\in L\_{req}$ (人物誌必備，如懶人型的子母車)。  
* **\+15**：若 $f \\in L\_{bonus}$ (人物誌可能有)。  
* **\-10**：若 $f \\notin (L\_{req} \\cup L\_{bonus})$ (人物誌通常沒有，如省錢型通常沒電梯)。

### **2.4 房東與管理 ($S\_{landlord}$) \- 互斥邏輯**

* $U\_{mgt}$：使用者偏好 (Enum: owner (房東同住), pro (專業管理), none (無所謂))。  
* $P\_{mgt}$：該人物誌的管理屬性。

衝突懲罰 (Penalty)：  
若使用者極度排斥房東同住 ($U\_{hate\\\_owner} \= True$)，但該人物誌是「房東同住型」，則直接給 \-100 分 (否決權)。  
$$S\_{landlord} \= \\begin{cases} 100 & \\text{if } U\_{mgt} \= P\_{mgt} \\\\ \-100 & \\text{if } P\_{mgt} \= \\text{'owner'} \\text{ AND } U\_{mgt} \= \\text{'no\_owner'} \\text{ (致命衝突)} \\\\ 50 & \\text{if } U\_{mgt} \= \\text{'none'} \\text{ (使用者沒意見)} \\\\ 0 & \\text{otherwise} \\end{cases}$$

### **2.5 房型偏好 ($S\_{type}$)**

$$S\_{type} \= \\begin{cases} 100 & \\text{if } U\_{type} \= P\_{type} \\\\ 0 & \\text{if } U\_{type} \\neq P\_{type} \\end{cases}$$

### **2.6 關鍵字加權 ($S\_{keyword}$)**

利用 AI 提取的對話原始文本 ($Text\_{raw}$)，比對資料庫中的 keywords 列表。

$$S\_{keyword} \= \\min(20, \\text{Count}(Matches) \\times 5)$$  
*(上限 20 分，作為微調用，避免關鍵字過度影響核心需求)*

## **3\. 演算法實作範例 (Python Pseudocode)**

這段代碼展示了如何將上述公式轉化為程式邏輯。

import math

def calculate\_persona\_score(user\_data, persona):  
    total\_score \= 0  
      
    \# 1\. 預算 (Budget) \- Weight: 1.5  
    u\_budget \= user\_data.get('budget')  
    p\_min \= persona\['algo\_config'\]\['rent\_min'\]  
    p\_max \= persona\['algo\_config'\]\['rent\_max'\]  
      
    s\_budget \= 0  
    if u\_budget:  
        if p\_min \<= u\_budget \<= p\_max:  
            s\_budget \= 100  
        elif u\_budget \< p\_min:  
            \# 指數衰減公式  
            s\_budget \= 100 \* math.exp(-0.002 \* (p\_min \- u\_budget))  
        else:  
            s\_budget \= 90  
    total\_score \+= s\_budget \* 1.5

    \# 2\. 地點 (Location) \- Weight: 1.2  
    u\_loc \= user\_data.get('location\_pref')  
    p\_locs \= persona\['algo\_config'\].get('preferred\_locations', \[\])  
      
    s\_loc \= 0  
    if u\_loc in p\_locs:  
        s\_loc \= 100  
    elif u\_loc:  
        s\_loc \= 0 \# 完全不符  
    total\_score \+= s\_loc \* 1.2

    \# 3\. 設施 (Features) \- Weight: 1.0  
    u\_features \= \[k for k, v in user\_data.items() if v is True and k in \['garbage', 'elevator', 'cctv'\]\]  
    p\_req \= persona\['algo\_config'\].get('required', \[\])  
    p\_bonus \= persona\['algo\_config'\].get('bonus', \[\])  
      
    feature\_score\_sum \= 0  
    if u\_features:  
        for f in u\_features:  
            if f in p\_req:  
                feature\_score\_sum \+= 30  
            elif f in p\_bonus:  
                feature\_score\_sum \+= 15  
            else:  
                feature\_score\_sum \-= 10  
          
        \# 正規化到 0\~100  
        max\_possible \= len(u\_features) \* 30  
        s\_features \= (feature\_score\_sum / max\_possible) \* 100  
        s\_features \= max(0, min(100, s\_features)) \# Clamp  
        total\_score \+= s\_features \* 1.0

    \# ... 其他維度 (Landlord, Type, Keywords) 依此類推 ...

    return total\_score

## **4\. 最終排序與輸出**

系統計算完所有 Active Personas 的分數後：

1. **排序**：由高到低排列。  
2. **閾值過濾 (Threshold)**：若最高分仍低於 **60 分**，顯示「無強力推薦，但這些可能適合...」。  
3. **Top 1**：作為主要推薦 (Diagnosis Card)。  
4. **Top 2**：若分數接近 Top 1 (差距 \< 10分)，可列為「次要推薦」。

// 輸出範例  
{  
  "best\_match": "type\_B",  
  "score": 85.5,  
  "match\_details": {  
    "budget\_match": "perfect",  
    "feature\_match": "high"  
  }  
}  
