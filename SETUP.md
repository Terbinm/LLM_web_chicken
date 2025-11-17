# AI 虛擬場景互動系統 - 設置說明

這是一個基於 Flask + Vue.js 3 + Google Gemini API 的虛擬場景互動系統，提供4個不同場景的 AI 對話體驗。

## 專案架構

```
flask_llm_web/
├── app.py                          # Flask 主應用程式
├── config.py                       # 配置檔案
├── requirements.txt                # Python 依賴
├── .env.example                    # 環境變數範例
├── .env                            # 環境變數（需自行建立）
├── utils/                          # 工具模組
│   ├── __init__.py
│   ├── llm_client.py              # Gemini API 客戶端
│   ├── scene_manager.py           # 場景管理器
│   └── mcp_handler.py             # MCP 模擬處理器
├── static/                         # 靜態資源
│   ├── index.html                 # 主頁面
│   ├── css/
│   │   └── style.css              # 樣式表
│   ├── js/
│   │   └── app.js                 # Vue.js 應用
│   └── images/
│       ├── emoji/                 # 表情符號（29個）
│       └── background/            # 場景背景（需準備）
├── image/
│   └── mcp_pipe.py                # MCP WebSocket 代理
└── readme.md                      # 專案需求說明
```

## 快速開始

### 1. 安裝 Python 依賴

```bash
# 確保您使用 Python 3.8 或更高版本
python --version

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置環境變數

複製 `.env.example` 為 `.env` 並填入您的 API 金鑰：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```env
# Google Gemini API Configuration
GEMINI_API_KEY=your_actual_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here

# Server Configuration
HOST=127.0.0.1
PORT=5000
```

### 3. 獲取 Gemini API 金鑰

1. 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用 Google 帳號登入
3. 點擊 "Create API Key" 建立 API 金鑰
4. 複製金鑰並貼到 `.env` 檔案中

### 4. 準備背景圖片（可選）

參考 `static/images/background/README.md` 中的 Prompt，準備4張場景背景圖片：

- `computer_room.jpg` - 電腦房
- `bedroom.jpg` - 臥室
- `mcp_studio.jpg` - MCP 工作室
- `planning_room.jpg` - 繪圖室

如果暫時沒有圖片，系統會使用 CSS 漸層色作為背景。

### 5. 啟動應用程式

```bash
python app.py
```

應用程式將在 `http://127.0.0.1:5000` 啟動。

### 6. 開啟瀏覽器

訪問 `http://127.0.0.1:5000` 開始使用！

## 功能特色

### ✨ 核心功能

1. **4個虛擬場景**
   - 電腦房：網路檢索、資訊查詢
   - 臥室：休息、放鬆
   - MCP 工作室：使用 MCP 工具開發
   - 繪圖室：創意規劃

2. **AI 對話互動**
   - 使用 Google Gemini 2.0 Flash 模型
   - 結構化輸出（訊息 + 表情 + 場景建議）
   - 支援對話歷史記錄

3. **動態表情系統**
   - 29個中文命名的表情符號
   - AI 根據情境自動選擇表情

4. **場景自動切換**
   - AI 根據對話內容智慧推薦場景
   - 支援手動切換場景

5. **MCP 工具模擬**
   - 在 MCP 工作室場景模擬工具執行
   - 支援 search、file-read、file-write、execute 等指令
   - 顯示工具執行結果

6. **對話歷史記錄**
   - 使用 LocalStorage 儲存
   - 刷新頁面後保留對話
   - 支援清除歷史

## API 端點

### 場景相關

- `GET /api/scenes` - 獲取所有場景
- `GET /api/scene/<scene_id>` - 獲取特定場景資訊

### 對話相關

- `POST /api/chat` - 發送訊息給 AI
  ```json
  {
    "message": "用戶訊息",
    "current_scene": "場景ID",
    "conversation_history": []
  }
  ```

### MCP 相關

- `POST /api/mcp/execute` - 執行 MCP 指令
  ```json
  {
    "command": "mcp list-tools"
  }
  ```
- `GET /api/mcp/tools` - 獲取可用 MCP 工具列表

### 其他

- `GET /api/health` - 健康檢查
- `GET /api/emojis` - 獲取可用表情符號列表

## 開發指南

### 修改場景

編輯 `utils/scene_manager.py` 中的 `SCENES` 字典：

```python
'new_scene': {
    'id': 'new_scene',
    'name': '新場景',
    'description': '場景描述',
    'background': '/static/images/background/new_scene.jpg',
    'icon': '🏠',
    'activities': ['活動1', '活動2']
}
```

### 添加新的 MCP 工具

編輯 `utils/mcp_handler.py`，在 `AVAILABLE_TOOLS` 中添加工具定義，並實作對應的處理方法。

### 自訂 AI Prompt

編輯 `utils/llm_client.py` 中的 `_build_prompt` 方法來調整 AI 的行為和回應風格。

### 修改 UI 樣式

編輯 `static/css/style.css` 來自訂視覺風格。

## 故障排除

### 問題：無法啟動應用程式

**解決方案**：
- 確認已安裝所有依賴：`pip install -r requirements.txt`
- 檢查 Python 版本：`python --version`（需要 3.8+）
- 檢查埠號 5000 是否被佔用

### 問題：API 請求失敗

**解決方案**：
- 確認 `.env` 檔案中的 `GEMINI_API_KEY` 已正確設置
- 檢查網路連接
- 確認 API 金鑰有效且有足夠配額

### 問題：表情符號不顯示

**解決方案**：
- 確認 `static/images/emoji/` 目錄下有圖片檔案
- 檢查瀏覽器開發者工具中的網路請求
- 確認檔案路徑正確

### 問題：背景圖片不顯示

**解決方案**：
- 確認 `static/images/background/` 目錄下有對應的圖片檔案
- 檔案名稱必須完全符合：
  - `computer_room.jpg`
  - `bedroom.jpg`
  - `mcp_studio.jpg`
  - `planning_room.jpg`
- 如果沒有圖片，系統會使用 CSS 漸層色

## 效能優化建議

1. **圖片優化**
   - 背景圖片建議 < 500KB
   - 使用 WebP 格式可減少檔案大小
   - 表情符號建議 < 100KB

2. **API 快取**
   - 考慮在後端實作快取機制
   - 減少重複的 API 請求

3. **前端優化**
   - 考慮使用 Vue.js 的生產版本
   - 實作虛擬滾動處理大量對話記錄

## 安全性注意事項

1. **API 金鑰保護**
   - 永遠不要將 `.env` 檔案提交到版本控制
   - 在生產環境使用環境變數而非檔案

2. **輸入驗證**
   - 後端已實作基本的輸入驗證
   - 考慮添加更嚴格的內容過濾

3. **CORS 設定**
   - 生產環境記得調整 `config.py` 中的 `CORS_ORIGINS`

## 未來擴展方向

- [ ] 整合真實的 MCP WebSocket 連接（使用 `image/mcp_pipe.py`）
- [ ] 添加語音輸入功能（Web Speech API）
- [ ] 實作多用戶支援
- [ ] 添加對話匯出功能
- [ ] 支援圖片上傳和分析
- [ ] 3D 場景渲染（Three.js）
- [ ] 實作用戶帳號系統

## 授權

本專案僅供學習和個人使用。

## 支援

如有問題，請參考：
- Google Gemini API 文檔：https://ai.google.dev/docs
- Flask 文檔：https://flask.palletsprojects.com/
- Vue.js 文檔：https://vuejs.org/

---

祝您使用愉快！ 🚀
