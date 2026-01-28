import re
from pathlib import Path

import requests

# ===== 配置区域 =====
# 这里写你本地或线上访问网站的基础地址
# 本地开发时一般是这个：
BASE_URL = "http://localhost:5173"
# 如果你要在上线后的域名上检测，可以改成：
# BASE_URL = "https://your-domain.com"

TIMEOUT = 5  # 每个游戏检测的超时时间（秒）

BASE_DIR = Path(__file__).resolve().parent
GAMES_JS = BASE_DIR / "src" / "data" / "games.js"
BACKUP_FILE = BASE_DIR / "src" / "data" / "games.js.backup_before_filter"


def load_games_js() -> str:
  if not GAMES_JS.exists():
    raise FileNotFoundError(f"games.js 不存在: {GAMES_JS}")
  return GAMES_JS.read_text(encoding="utf-8", errors="ignore")


def extract_body(content: str) -> str:
  """
  提取 const games = [...] 中间的内容（不含首尾中括号）
  兼容：
    const games = [ ... ]

    export default games
  或
    const games = [ ... ];
  """
  pattern = r"const\s+games\s*=\s*\[(.*)\]\s*(?:;|\n\s*\n\s*export)"
  m = re.search(pattern, content, re.S)
  if not m:
    raise ValueError("无法在 games.js 中找到 games 数组，请检查文件格式。")
  return m.group(1), m.start(1), m.end(1)


def split_blocks(body: str):
  """按顶层花括号拆分每个游戏对象文本块，返回 (start, end, block) 列表"""
  blocks = []
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
        blocks.append((start, i + 1, body[start : i + 1]))
        start = None
  return blocks


def get_field(block: str, name: str) -> str:
  m = re.search(rf"{re.escape(name)}\s*:\s*'([^']*)'", block)
  return m.group(1).strip() if m else ""


def is_game_working(url: str) -> bool:
  """通过 HTTP 请求判断游戏是否能正常打开（至少返回 200/304）"""
  full_url = f"{BASE_URL}{url}"
  try:
    resp = requests.get(full_url, timeout=TIMEOUT)
    # 认为 200 / 304 是“能正常打开页面”
    if resp.status_code in (200, 304):
      return True
    return False
  except Exception as e:
    print(f"  请求失败: {full_url} -> {e}")
    return False


def main():
  print("读取 games.js...")
  content = load_games_js()

  print(f"先备份到: {BACKUP_FILE}")
  BACKUP_FILE.write_text(content, encoding="utf-8")

  body, body_start, body_end = extract_body(content)
  blocks = split_blocks(body)
  print(f"共检测到 {len(blocks)} 个游戏条目，开始逐个请求 {BASE_URL} ...")

  working_blocks = []
  broken_blocks = []

  for idx, (start, end, block) in enumerate(blocks, start=1):
    gid = get_field(block, "id")
    title = get_field(block, "title")
    url = get_field(block, "url")

    # 没有 url 的，直接当作坏的（一般不会出现）
    if not url:
      print(f"[{idx:03}] id={gid} title={title} 缺少 url，标记为【删除】")
      broken_blocks.append((gid, title, url))
      continue

    # 只关心站内游戏；其他直接保留
    if not url.startswith("/games/"):
      print(f"[{idx:03}] id={gid} 外部 / 非本地游戏，保留")
      working_blocks.append(block)
      continue

    print(f"[{idx:03}] 检测游戏 id={gid} title={title} url={url} ...", end=" ")
    if is_game_working(url):
      print("OK，保留")
      working_blocks.append(block)
    else:
      print("失败，标记为【删除】")
      broken_blocks.append((gid, title, url))

  print("\n=== 检测结果 ===")
  print(f"可正常打开的游戏数量: {len(working_blocks)}")
  print(f"将要删除的异常游戏数量: {len(broken_blocks)}")

  # 重新生成 games.js 内容，只保留 working_blocks
  new_body = ""
  for i, block in enumerate(working_blocks):
    # 保持原来的缩进和逗号风格
    # 原文件是每个对象之间用逗号分隔
    if i == 0:
      new_body += f"\n  {block}"
    else:
      new_body += f",\n  {block}"
  new_body += "\n"

  new_content = (
    content[: body_start]
    + new_body
    + content[body_end:]
  )

  GAMES_JS.write_text(new_content, encoding="utf-8")
  print(f"\n已写回过滤后的 games.js，只保留可正常访问的游戏。")

  if broken_blocks:
    # 额外输出一个简单文本报告
    report_path = BASE_DIR / "filtered_broken_games.txt"
    with report_path.open("w", encoding="utf-8") as f:
      for gid, title, url in broken_blocks:
        f.write(f"id={gid}\ttitle={title}\turl={url}\n")
    print(f"已将被删除的异常游戏列表写入: {report_path}")


if __name__ == "__main__":
  main()

