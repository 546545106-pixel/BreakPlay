#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 public/games 里的本地图片，自动为每个游戏选择一张封面图，写回 src/data/games.js。

规则：
- 解析 games.js 中每个游戏对象的 url，形如 '/games/<folder>/index.html'
- 在 public/games/<folder>/ 下查找图片文件（png/jpg/jpeg/gif/webp）
- 优先使用文件名包含 icon/logo/cover/thumb/thumbnail 的图片；否则取第一个图片
- 把该路径写入 thumb 字段，例如：thumb: '/games/<folder>/<image>'
- 如果某个游戏没找到本地图片，则保留原来的 thumb 不变
"""

from pathlib import Path
import re

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"
PUBLIC_GAMES_DIR = PROJECT_ROOT / "public" / "games"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
PREFERRED_KEYWORDS = ["icon", "logo", "cover", "thumb", "thumbnail"]


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


def choose_image_for_folder(folder: Path):
    """在游戏目录及子目录中选择一张最合适的封面图。"""
    if not folder.exists() or not folder.is_dir():
        return None

    images = []

    # 1）优先扫描当前目录下的图片
    for p in folder.iterdir():
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            images.append(p)

    # 2）如果当前目录没有，再递归子目录（img/images等）
    if not images:
        for p in folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                images.append(p)

    if not images:
        return None

    # 优先包含关键字的文件，其次路径越浅越好
    def score(p: Path):
        name = p.name.lower()
        base_score = len(PREFERRED_KEYWORDS) + 1
        for idx, kw in enumerate(PREFERRED_KEYWORDS):
            if kw in name:
                base_score = idx
                break
        # 子目录越少，优先级越高
        depth = len(p.relative_to(folder).parts)
        return (base_score, depth, p.name.lower())

    images.sort(key=score)
    # 返回相对 folder 的路径，兼容子目录
    rel_path = images[0].relative_to(folder).as_posix()
    return rel_path


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
        m = re.search(r"url:\s*'([^']*)'", b)
        if not m:
            new_blocks.append(b)
            continue

        url = m.group(1)
        # 只处理 /games/ 开头的本地游戏
        m2 = re.match(r"/games/([^/]+)/", url)
        if not m2:
            new_blocks.append(b)
            continue

        folder_name = m2.group(1)
        folder_path = PUBLIC_GAMES_DIR / folder_name
        image_rel_path = choose_image_for_folder(folder_path)

        if not image_rel_path:
            new_blocks.append(b)
            continue

        new_thumb = f"/games/{folder_name}/{image_rel_path}"
        # 替换 thumb 字段
        if "thumb:" in b:
            b2 = re.sub(r"thumb:\s*'[^']*'", f"thumb: '{new_thumb}'", b, count=1)
        else:
            # 没有 thumb 字段时，插入一行（理论上不会出现）
            b2 = b.replace("url:", f"thumb: '{new_thumb}',\n    url:", 1)

        if b2 != b:
            updated_count += 1
        new_blocks.append(b2)

    new_body = "\n  " + ",\n  ".join(new_blocks) + "\n"
    new_content = "const games = [" + new_body + "]\n\nexport default games\n"

    # 先备份
    backup = GAMES_JS.with_suffix(".js.backup_thumbs")
    backup.write_text(content, encoding="utf-8")

    GAMES_JS.write_text(new_content, encoding="utf-8")

    print(f"封面更新完成，已更新 {updated_count} 条游戏的 thumb 字段。")


if __name__ == "__main__":
    main()

