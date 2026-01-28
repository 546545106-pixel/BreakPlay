#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并本地旧游戏（清理前备份中的 /games/ 本地条目）和当前 95 个新游戏。

目标：
- 从 games.js.backup_cleanup 中提取所有 url 以 '/games/' 开头的本地游戏
- 从当前 games.js 中提取所有游戏（即刚导入的 95 个）
- 以“当前 games.js（新 95 个）优先”的顺序，按 url 去重合并
- 重新从 1 开始顺编号 id，生成新的 src/data/games.js

注意：不会动任何 public/games 里的实际游戏文件，只是重建 games.js 数据。
"""

from pathlib import Path
import re

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
CURRENT_JS = PROJECT_ROOT / "src" / "data" / "games.js"
BACKUP_CLEANUP_JS = PROJECT_ROOT / "src" / "data" / "games.js.backup_cleanup"


def extract_body(content: str) -> str:
    """提取 const games = [ ... ] 中间的主体部分。"""
    m = re.search(
        r"const\s+games\s*=\s*\[\s*(.*)\s*\]\s*export\s+default\s+games\s*",
        content,
        re.S,
    )
    if not m:
        raise RuntimeError("未能解析 games.js 的数组结构")
    return m.group(1)


def split_blocks(body: str):
    """把主体拆成一个个 { ... } 游戏对象块（保留原始格式）。"""
    pattern = re.compile(r"(\s*\{\s*[\s\S]*?\s*\})\s*,?", re.S)
    blocks = []
    for match in pattern.finditer(body):
        block = match.group(1)
        blocks.append(block.strip())
    return blocks


def get_url(block: str) -> str:
    """从对象块中提取 url 字段。"""
    m = re.search(r"url:\s*'([^']*)'", block)
    return m.group(1) if m else ""


def rebuild_games_js():
    if not BACKUP_CLEANUP_JS.exists():
        raise FileNotFoundError(f"找不到备份文件: {BACKUP_CLEANUP_JS}")
    if not CURRENT_JS.exists():
        raise FileNotFoundError(f"找不到当前 games.js: {CURRENT_JS}")

    # 1. 读取当前 games.js（新导入的 95 个）
    current_content = CURRENT_JS.read_text(encoding="utf-8")
    current_body = extract_body(current_content)
    current_blocks = split_blocks(current_body)

    # 2. 从备份中读取所有本地 /games/ 游戏
    backup_content = BACKUP_CLEANUP_JS.read_text(encoding="utf-8")
    backup_body = extract_body(backup_content)
    backup_blocks_all = split_blocks(backup_body)
    backup_local_blocks = [
        b for b in backup_blocks_all if "url: '/games/" in b
    ]

    # 3. 以 url 作为去重键，先加入当前（新 95 个），再补充旧本地游戏
    merged_blocks = []
    seen_urls = set()

    # 先 current（新）
    for b in current_blocks:
        url = get_url(b)
        if not url or url in seen_urls:
            continue
        merged_blocks.append(b)
        seen_urls.add(url)

    # 再 backup 本地旧游戏
    for b in backup_local_blocks:
        url = get_url(b)
        if not url or url in seen_urls:
            continue
        merged_blocks.append(b)
        seen_urls.add(url)

    # 4. 重新编号 id，从 1 开始
    renumbered_blocks = []
    for idx, b in enumerate(merged_blocks, start=1):
        new_id = str(idx)
        b2 = re.sub(r"id:\s*'[^']*'", f"id: '{new_id}'", b, count=1)
        renumbered_blocks.append(b2)

    # 5. 生成新的 games.js 内容
    body_str = "\n  " + ",\n  ".join(renumbered_blocks) + "\n"
    new_content = "const games = [" + body_str + "]\n\nexport default games\n"

    # 6. 备份当前 games.js 再覆盖
    backup_path = CURRENT_JS.with_suffix(".js.backup_merge_local_95")
    backup_path.write_text(current_content, encoding="utf-8")

    CURRENT_JS.write_text(new_content, encoding="utf-8")

    print(f"合并完成，写入 {CURRENT_JS}")
    print(f"当前 95 个游戏条目: {len(current_blocks)}")
    print(f"备份中的本地游戏条目: {len(backup_local_blocks)}")
    print(f"去重后合并总数: {len(renumbered_blocks)}")


def main():
    try:
        rebuild_games_js()
    except Exception as e:
        print("合并过程中出错：", e)


if __name__ == "__main__":
    main()

