#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据敏感封面/不合规内容删除指定游戏条目。

规则：
- 从 src/data/games.js 中移除 title 属于下列列表的游戏：
  ['Jianren','Ccgl','Circle','Jingzi','Gqtz','Semo','Shiyiquna','Pxfzm','Pigu','Qixi1','微信游戏首页模板']

不会动 public/games 下的实际文件，只更新 games.js 数据。
"""

from pathlib import Path
import re

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

BAD_TITLES = {
    "Jianren",
    "Ccgl",
    "Circle",
    "Jingzi",
    "Gqtz",
    "Semo",
    "Shiyiquna",
    "Pxfzm",
    "Pigu",
    "Qixi1",
    "微信游戏首页模板",
}


def extract_body(content: str) -> str:
    m = re.search(
        r"const\s+games\s*=\s*\[\s*(.*)\s*\]\s*export\s+default\s+games\s*",
        content,
        re.S,
    )
    if not m:
        raise RuntimeError("未能解析 games.js 的数组结构")
    return m.group(1)


def split_blocks(body: str):
    pattern = re.compile(r"(\s*\{\s*[\s\S]*?\s*\})\s*,?", re.S)
    blocks = []
    for match in pattern.finditer(body):
        blocks.append(match.group(1).strip())
    return blocks


def get_title(block: str) -> str:
    m = re.search(r"title:\s*'([^']*)'", block)
    return m.group(1) if m else ""


def main():
    if not GAMES_JS.exists():
        print("games.js 不存在：", GAMES_JS)
        return

    content = GAMES_JS.read_text(encoding="utf-8")
    body = extract_body(content)
    blocks = split_blocks(body)

    kept = []
    removed = []

    for b in blocks:
        title = get_title(b)
        if title in BAD_TITLES:
            removed.append(title)
        else:
            kept.append(b)

    new_body = "\n  " + ",\n  ".join(kept) + "\n"
    new_content = "const games = [" + new_body + "]\n\nexport default games\n"

    backup = GAMES_JS.with_suffix(".js.backup_remove_bad")
    backup.write_text(content, encoding="utf-8")

    GAMES_JS.write_text(new_content, encoding="utf-8")

    print(f"已删除 {len(removed)} 个不合规游戏：{removed}")
    print(f"保留 {len(kept)} 个游戏条目。")


if __name__ == "__main__":
    main()

