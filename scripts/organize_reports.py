#!/usr/bin/env python3
"""
Organize Q3/Q4 quarterly reports into the twse-reports-lib repo structure.
Handles multiple naming conventions for both TXT and MD files.
"""
import shutil
from pathlib import Path

BASE_DIR = Path("/Users/downtoearth/.openclaw/workspace/台股季報/2025")
REPO_DIR = Path("/Users/downtoearth/.openclaw/workspace/twse-reports-lib")

QUARTERS = {
    "Q4": {
        "txt_globs": ["*2025Q4*.TXT", "*2025Q04*.TXT"],
        "md_globs": ["*20254*.md", "*202504*.md"],  # new and old naming
        "dest": "2025/Q4",
    },
    "Q3": {
        "txt_globs": ["*2025Q3*.TXT"],
        "md_globs": ["*20253*.md"],
        "dest": "2025/Q3",
    },
}

def main():
    for quarter, cfg in QUARTERS.items():
        src_dir = BASE_DIR / quarter
        dest_dir = REPO_DIR / cfg["dest"]
        dest_dir.mkdir(parents=True, exist_ok=True)

        txt_count = 0
        md_count = 0
        empty_skip = 0

        for folder in sorted(src_dir.iterdir()):
            if not folder.is_dir():
                continue

            # Extract stock ID: "1101" or "1101台泥" → "1101"
            stock_id = folder.name
            import re
            clean_id = re.sub(r'[^\d]', '', stock_id)
            if not clean_id:
                continue

            files_in_folder = list(folder.iterdir())
            if not files_in_folder:
                empty_skip += 1
                continue

            # Copy TXT
            txt_files = []
            for g in cfg.get("txt_globs", []):
                txt_files.extend(folder.glob(g))
            txt_files = list(set(txt_files))
            if txt_files:
                txt_src = txt_files[0]
                txt_dst = dest_dir / clean_id / txt_src.name
                txt_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(txt_src, txt_dst)
                txt_count += 1

            # Copy MD (both naming conventions)
            md_files = []
            for g in cfg.get("md_globs", []):
                md_files.extend(folder.glob(g))
            md_files = list(set(md_files))
            if md_files:
                md_src = md_files[0]
                md_dst = dest_dir / clean_id / md_src.name
                md_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_src, md_dst)
                md_count += 1

        print(f"{quarter}: {txt_count} TXT, {md_count} MD copied, {empty_skip} empty skipped")

if __name__ == "__main__":
    main()
