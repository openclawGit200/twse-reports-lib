#!/bin/bash
# 週六下載完成後，週一自動上傳至 GitHub
# 需確保 GitHub token 存在於 ~/.openclaw/workspace/.credentials/github_token.json
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CREDS_FILE="$HOME/.openclaw/workspace/.credentials/github_token.json"
LOG_FILE="$REPO_DIR/sync.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始同步季報至 GitHub..." >> "$LOG_FILE"

# 讀取 GitHub token
if [ ! -f "$CREDS_FILE" ]; then
    echo "[$(date)] 錯誤：找不到 $CREDS_FILE" >> "$LOG_FILE"
    exit 1
fi

GITHUB_TOKEN=$(python3 -c "import json; print(json.load(open('$CREDS_FILE'))['token'])")

cd "$REPO_DIR"

# 整理最新季報
python3 scripts/organize_reports.py >> "$LOG_FILE" 2>&1

# 設定 git
git config user.email "openclawgit200@openclaw.ai" 2>/dev/null || true
git config user.name "openclawGit200" 2>/dev/null || true

# 檢查是否有變更
if git diff --quiet && [ -z "$(git status --porcelain)" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 沒有變更，跳過上傳" >> "$LOG_FILE"
    exit 0
fi

# 提交並推送
git add -A
COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M') - $(find 2025/Q4 2025/Q3 -name '*.TXT' 2>/dev/null | wc -l) reports"
git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1

# 注入 token 推送
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/openclawGit200/twse-reports-lib.git"
git push >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 同步完成" >> "$LOG_FILE"
