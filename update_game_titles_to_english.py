#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将站内展示的所有游戏名称统一改成英文（无中文字符）。

规则：
- 读取 src/data/games.js
- 对每个游戏对象：
  - 如果 title 中包含中文字符，则用 url 中的 /games/<folder>/ 生成英文标题：
    - folder 名中的下划线/中划线替换为空格
    - 再做 .title()，例如：'zhandou_feiji' -> 'Zhandou Feiji'
  - 如果 title 已经是纯英文/拼音（没有中文），则保持不动
- 只修改 title 字段，其他字段（url、thumb、description 等）保持不变

会自动备份原始文件到 games.js.backup_titles。
"""

from pathlib import Path
import re

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"


def has_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


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


def build_english_title_from_url(block: str) -> str | None:
    m = re.search(r"url:\s*'([^']+)'", block)
    if not m:
        return None
    url = m.group(1)
    m2 = re.match(r"/games/([^/]+)/", url)
    if not m2:
        return None
    folder = m2.group(1)
    # 去掉明显的前后空白和下划线
    folder = folder.strip().replace("_", " ").replace("-", " ")
    if not folder:
        return None
    # 转成类似 Title Case
    english_title = folder.title()
    return english_title


def main():
    if not GAMES_JS.exists():
        print("games.js 不存在：", GAMES_JS)
        return

    content = GAMES_JS.read_text(encoding="utf-8")
    body = extract_body(content)
    blocks = split_blocks(body)

    new_blocks = []
    updated_count = 0

    for b in blocks:
        # 取原 title
        m_title = re.search(r"title:\s*'([^']*)'", b)
        if not m_title:
            new_blocks.append(b)
            continue

        title = m_title.group(1)
        # 只改含中文的标题
        if not has_chinese(title):
            new_blocks.append(b)
            continue

        english_title = build_english_title_from_url(b)
        if not english_title:
            new_blocks.append(b)
            continue

        # 替换 title 字段
        b2 = re.sub(
            r"title:\s*'[^']*'",
            f"title: '{english_title}'",
            b,
            count=1,
        )
        if b2 != b:
            updated_count += 1
        new_blocks.append(b2)

    new_body = "\n  " + ",\n  ".join(new_blocks) + "\n"
    new_content = "const games = [" + new_body + "]\n\nexport default games\n"

    # 备份原文件
    backup = GAMES_JS.with_suffix(".js.backup_titles")
    backup.write_text(content, encoding="utf-8")

    GAMES_JS.write_text(new_content, encoding="utf-8")

    print(f"标题更新完成，已将 {updated_count} 条含中文的 title 改为英文。")


if __name__ == "__main__":
    main()

