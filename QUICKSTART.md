# 快速啟動指南

## 🚀 3 分鐘快速啟動

### 步驟 1：安裝依賴 (1 分鐘)

```bash
pip install -r requirements.txt
```

### 步驟 2：配置 API 金鑰 (1 分鐘)

```bash
# 複製環境變數範例檔案
cp .env.example .env
```

編輯 `.env` 檔案，填入您的 Gemini API 金鑰：

```env
GEMINI_API_KEY=your_actual_api_key_here
```

**如何獲取 API 金鑰？**
1. 訪問：https://makersuite.google.com/app/apikey
2. 使用 Google 帳號登入
3. 點擊 "Create API Key"
4. 複製金鑰並貼到 `.env` 檔案

### 步驟 3：啟動應用 (1 分鐘)

```bash
python app.py
```

看到以下訊息表示啟動成功：

```
Starting Flask application on 127.0.0.1:5000
 * Running on http://127.0.0.1:5000
```

### 步驟 4：開始使用

在瀏覽器中訪問：**http://127.0.0.1:5000**

---

## 📝 背景圖片準備（可選）

系統預設會使用 CSS 漸層色作為背景。如果您想使用自訂背景圖片：

1. 查看 `static/images/background/README.md` 中的 AI 生成 Prompt
2. 使用 AI 圖片生成工具（Midjourney、DALL-E、Stable Diffusion）生成4張圖片
3. 將圖片命名為：
   - `computer_room.jpg` - 電腦房
   - `bedroom.jpg` - 臥室
   - `mcp_studio.jpg` - MCP 工作室
   - `planning_room.jpg` - 繪圖室
4. 放到 `static/images/background/` 目錄下
5. 重新整理瀏覽器即可看到背景圖片

---

## 💡 使用技巧

### 場景切換
- 點擊下方場景按鈕手動切換
- 或在對話中提到相關活動，AI 會自動建議切換

### MCP 工具使用
1. 切換到「MCP 工作室」場景
2. 在對話中提到「使用工具」、「執行指令」等
3. AI 會自動執行相關的 MCP 模擬指令

### 對話歷史
- 系統自動儲存對話記錄
- 刷新頁面後仍會保留
- 點擊右上角「清除歷史」可刪除所有記錄

---

## ⚠️ 常見問題

**Q: 啟動時提示 "GEMINI_API_KEY is not set"**

A: 請確認：
1. 已建立 `.env` 檔案（複製 `.env.example`）
2. 已在 `.env` 中正確填入 API 金鑰
3. API 金鑰沒有多餘的空格或引號

**Q: 訊息發送後沒有回應**

A: 檢查：
1. 瀏覽器開發者工具的 Console（F12）是否有錯誤
2. API 金鑰是否有效
3. 網路連接是否正常
4. 檢查後端 terminal 的錯誤訊息

**Q: 表情符號不顯示**

A: 確認 `static/images/emoji/` 目錄下有圖片檔案（應該有29個）

---

## 📚 更多資訊

詳細的設置和開發指南請參考：**SETUP.md**

---

祝您使用愉快！如有問題歡迎查閱文檔或提出 Issue。
