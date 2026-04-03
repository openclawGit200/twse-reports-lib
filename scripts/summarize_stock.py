#!/usr/bin/env python3
"""
Given a stock ID and quarter, read the TXT report and generate a new MD summary.
Can use local Ollama (default) or OpenAI API.

Usage:
  python3 summarize_stock.py --stock-id 2330 --quarter Q4
  python3 summarize_stock.py --stock-id 2330 --quarter Q4 --model openai --openai-model gpt-4o
  python3 summarize_stock.py --all --quarter Q4
"""
import argparse
import json
import os
import subprocess
import sys
import re
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
MODEL_DIR = REPO_DIR / "model"  # optional: cache prompts

OLLAMA_MODEL = "gemma3:12b"  # default for Ollama

PROMPT_TEMPLATE = """你是一位專業的台灣股票基本面分析師。請根據以下季度財務報告內容，產生一份結構化的分析摘要。

要求：
1. 先總結該季度營收與獲利表現（營收、毛利、營業利益、稅後淨利，與去年同期比較）
2. 列出三項最重要的變化或亮點
3. 列出三項需要關注的風險或疑慮
4. 給出簡短的總結與未來展望

---

{text_content}

---

請用正體中文輸出，以 Markdown 格式撰寫。"""


def get_txt_content(stock_id: str, quarter: str) -> Path:
    """Find the TXT file for a given stock and quarter."""
    q_dir = REPO_DIR / "2025" / quarter / stock_id
    txt_files = list(q_dir.glob("*.TXT")) + list(q_dir.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No TXT file found for {stock_id} {quarter}")
    return txt_files[0]


def generate_summary_via_ollama(text: str, model: str = OLLAMA_MODEL) -> str:
    """Generate summary using local Ollama."""
    prompt = PROMPT_TEMPLATE.format(text_content=text[:8000])  # token limit guard
    result = subprocess.run(
        ["ollama", "chat", model],
        input=json.dumps({"messages": [{"role": "user", "content": prompt}]}),
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ollama error: {result.stderr}")
    return json.loads(result.stdout)["message"]["content"]


def generate_summary_via_openai(text: str, model: str = "gpt-4o") -> str:
    """Generate summary using OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not installed: pip install openai")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(text_content=text[:8000])
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content


def save_summary(stock_id: str, quarter: str, content: str):
    """Save the generated summary as a MD file."""
    q_num = quarter  # Q3 -> 20253, Q4 -> 20254
    q_map = {"Q3": "20253", "Q4": "20254"}
    q_code = q_map.get(quarter, quarter)

    out_dir = REPO_DIR / "2025" / quarter / stock_id
    out_file = out_dir / f"台股季報{q_code}_{stock_id}_AI摘要.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# {stock_id} {quarter} 季度財報 AI 摘要\n\n")
        f.write(content)
        f.write(f"\n\n---\n*本摘要由 AI 自動生成 | 原始資料：{REPO_DIR.name}/2025/{quarter}/{stock_id}*\n")
    print(f"✅ 摘要已儲存：{out_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate MD summary from TWSE TXT report")
    parser.add_argument("--stock-id", help="Stock ID (e.g. 2330)")
    parser.add_argument("--quarter", choices=["Q3", "Q4"], help="Quarter (Q3 or Q4)")
    parser.add_argument("--all", action="store_true", help="Process all stocks in the quarter")
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--model", default=OLLAMA_MODEL)
    parser.add_argument("--openai-model", default="gpt-4o")
    args = parser.parse_args()

    if args.all:
        if not args.quarter:
            print("Error: --quarter required with --all")
            sys.exit(1)
        q_dir = REPO_DIR / "2025" / args.quarter
        stock_ids = [d.name for d in q_dir.iterdir() if d.is_dir()]
        print(f"Found {len(stock_ids)} stocks in {args.quarter}")
        for sid in stock_ids:
            try:
                txt = get_txt_content(sid, args.quarter)
                text = txt.read_text(encoding="utf-8", errors="replace")
                if args.provider == "ollama":
                    summary = generate_summary_via_ollama(text, args.model)
                else:
                    summary = generate_summary_via_openai(text, args.openai_model)
                save_summary(sid, args.quarter, summary)
            except Exception as e:
                print(f"⚠️ {sid}: {e}")
    else:
        if not args.stock_id or not args.quarter:
            parser.print_help()
            sys.exit(1)
        txt = get_txt_content(args.stock_id, args.quarter)
        text = txt.read_text(encoding="utf-8", errors="replace")
        if args.provider == "ollama":
            summary = generate_summary_via_ollama(text, args.model)
        else:
            summary = generate_summary_via_openai(text, args.openai_model)
        save_summary(args.stock_id, args.quarter, summary)


if __name__ == "__main__":
    main()
