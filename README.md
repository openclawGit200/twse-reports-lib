# TWSE Reports Lib — 台股季度財報開放資料庫

> 將台灣證券交易所公開的上市櫃公司季度財報轉換為可機讀的文字檔與摘要，供研究、分析與 AI 應用使用。

## 📋 資料概覽

| 季度 | 股票數 | TXT 文字檔 | MD 摘要檔 |
|------|--------|-----------|----------|
| 2025 Q4 | ~1,643 檔 | ✅ | ✅ |
| 2025 Q3 | ~434 檔 | ✅ | ✅ |

## 📁 資料結構

```
twse-reports-lib/
├── 2025/
│   ├── Q4/
│   │   ├── {stock_id}/
│   │   │   ├── 台股季報2025Q4_{stock_id}.TXT       # 原始文字檔
│   │   │   └── 台股季報20254_{stock_id}.md          # AI 摘要
│   │   └── ...
│   └── Q3/
│       ├── {stock_id}/
│       │   ├── 台股季報2025Q3_{stock_id}.TXT
│       │   └── 台股季報20253_{stock_id}.md
│       └── ...
└── scripts/
    └── summarize_stock.py   # 用 AI 總結 TXT 產生新 MD 的腳本
```

## 🔧 使用方式

### 1. 克隆資料

```bash
git clone https://github.com/openclawGit200/twse-reports-lib.git
cd twse-reports-lib
```

### 2. 產生個股摘要（需要 Ollama 或 OpenAI API）

```bash
# 安裝依賴
pip install -r requirements.txt

# 對單一股票產生摘要
python3 scripts/summarize_stock.py --stock-id 2330 --quarter Q4

# 批次產生（使用本地 Ollama）
python3 scripts/summarize_stock.py --all --quarter Q4
```

### 3. 資料來源

- **TXT 文字檔**：来自臺灣證券交易所（TWSE）公開的季度財務報告 PDF，經文字提取後儲存
- **MD 摘要檔**：由 AI 模型（Ollama / OpenAI）對 TXT 進行語意摘要產生

## ⚠️ 已知限制

- 部分股票在某些季度無公開財報（TWSE 未提供），該季度資料夾為空
- TXT 為 PDF 直接轉換，精確度約 95%，少數圖表數字可能略有偏差
- Q4 = 年度季報（4月公告），涵蓋全年度資訊

## 📄 授權

本專案資料來自臺灣證券交易所公開資訊，版權歸原單位所有。
衍生資料（MD 摘要）開放自由使用，建議註明來源。

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request，例如：
- 修正文字錯誤
- 新增更多季度資料
- 改善摘要品質
- 建立搜尋引擎或視覺化工具
