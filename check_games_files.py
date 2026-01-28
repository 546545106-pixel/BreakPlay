import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GAMES_JS = BASE_DIR / "src" / "data" / "games.js"
PUBLIC_DIR = BASE_DIR / "public"


def load_games_js() -> str:
    if not GAMES_JS.exists():
        raise FileNotFoundError(f"games.js 不存在: {GAMES_JS}")
    return GAMES_JS.read_text(encoding="utf-8", errors="ignore")


def iter_game_blocks(content: str):
    """
    非严格解析，只是按顶层花括号粗略拆分每个游戏对象。
    依赖现有格式：
        const games = [
          {
            id: '1',
            ...
          },
          {
            ...
          },
        ]
    """
    body_match = re.search(r"const\s+games\s*=\s*\[(.*)]\s*;", content, re.S)
    if not body_match:
        return
    body = body_match.group(1)

    depth = 0
    start = None
    for i, ch in enumerate(body):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                yield body[start : i + 1]
                start = None


def get_field(block: str, name: str) -> str:
    m = re.search(rf"{re.escape(name)}\s*:\s*'([^']*)'", block)
    return m.group(1).strip() if m else ""


def main():
    content = load_games_js()

    missing = []
    ok = 0

    for block in iter_game_blocks(content):
        gid = get_field(block, "id")
        title = get_field(block, "title")
        url = get_field(block, "url")

        if not url:
            missing.append(
                {"id": gid, "title": title, "url": url, "reason": "games.js 中缺少 url 字段"}
            )
            continue

        # 只检查站内游戏：以 /games 开头的
        if not url.startswith("/games/"):
            ok += 1
            continue

        # 去掉开头的 /
        rel = url.lstrip("/")
        fs_path = PUBLIC_DIR / rel

        if fs_path.exists():
            ok += 1
        else:
            missing.append(
                {
                    "id": gid,
                    "title": title,
                    "url": url,
                    "reason": f"文件不存在: {fs_path}",
                }
            )

    report_path = BASE_DIR / "games_missing_report.txt"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("=== 游戏 URL 文件检查报告 ===\n")
        f.write(f"站内游戏(以 /games/ 开头) 实际存在数量: {ok}\n")
        f.write(f"疑似存在问题的条目数量: {len(missing)}\n\n")

        for item in missing:
            f.write(
                f"ID: {item['id']}\n"
                f"标题: {item['title']}\n"
                f"URL: {item['url']}\n"
                f"问题: {item['reason']}\n"
                "------------------------\n"
            )

    print("检查完成。")
    print(f"可用站内游戏数量: {ok}")
    print(f"疑似有问题的游戏数量: {len(missing)}")
    print(f"详细报告已写入: {report_path}")


if __name__ == "__main__":
    main()

