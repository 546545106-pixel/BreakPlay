#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理 games.js 中的外部游戏数据，只保留本地（/games/ 开头）游戏。

规则：
- 保留所有 url 以 '/games/' 开头的条目（本地部署的游戏）
- 删除所有 url 不以 '/games/' 开头的条目（外部游戏）
"""

from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parent
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"
BACKUP_JS = PROJECT_ROOT / "src" / "data" / "games.js.backup_cleanup"

def main():
    if not GAMES_JS.exists():
        print("games.js 不存在，路径：", GAMES_JS)
        return

    content = GAMES_JS.read_text(encoding="utf-8")

    # 备份原文件（如果还没有备份）
    if not BACKUP_JS.exists():
        BACKUP_JS.write_text(content, encoding="utf-8")
        print("已备份原文件到:", BACKUP_JS)

    # 提取数组主体
    m = re.search(r"const\s+games\s*=\s*\[\s*(.*)\s*\]\s*export\s+default\s+games\s*", content, re.S)
    if not m:
        print("未能解析 games.js 的数组结构，请确认文件格式。")
        return

    body = m.group(1)

    # 匹配每个游戏对象块
    pattern = re.compile(r"(\s*\{\s*[\s\S]*?\s*\})\s*,?", re.S)
    kept_blocks = []
    removed = 0
    kept = 0

    for match in pattern.finditer(body):
        # 只取括号里的对象本身，避免把多余的逗号一起带进去
        block = match.group(1)
        if "url: '/games/" in block:
            kept_blocks.append(block.strip())
            kept += 1
        else:
            removed += 1

    print(f"外部(非 /games/)游戏条目已删除: {removed} 个，保留本地游戏: {kept} 个")

    new_body = "\n  " + ",\n  ".join(kept_blocks) + "\n"
    new_content = "const games = [" + new_body + "]\n\nexport default games\n"

    GAMES_JS.write_text(new_content, encoding="utf-8")
    print("games.js 已更新完成。")


if __name__ == "__main__":
    main()

