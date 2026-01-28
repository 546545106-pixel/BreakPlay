import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GAMES_JS = BASE_DIR / "src" / "data" / "games.js"
PUBLIC_DIR = BASE_DIR / "public"
BACKUP_FILE = BASE_DIR / "src" / "data" / "games.js.backup_before_fix"

# 常见的游戏入口文件名
ENTRY_FILES = [
    "index.html",
    "index.htm",
    "game.html",
    "game.htm",
    "main.html",
    "main.htm",
    "play.html",
    "play.htm",
]


def find_entry_file(game_dir: Path) -> str | None:
    """在游戏目录中查找入口文件"""
    if not game_dir.exists() or not game_dir.is_dir():
        return None
    
    # 先检查当前 URL 指定的文件是否存在
    for entry in ENTRY_FILES:
        candidate = game_dir / entry
        if candidate.exists():
            return entry
    
    # 递归查找所有 HTML 文件
    html_files = list(game_dir.rglob("*.html")) + list(game_dir.rglob("*.htm"))
    
    if html_files:
        # 优先选择根目录下的文件
        root_files = [f for f in html_files if f.parent == game_dir]
        if root_files:
            return root_files[0].name
        # 否则选择第一个找到的
        return html_files[0].relative_to(game_dir).as_posix()
    
    return None


def main():
    print("正在读取 games.js...")
    content = GAMES_JS.read_text(encoding="utf-8", errors="ignore")
    
    # 备份原文件
    print(f"备份原文件到: {BACKUP_FILE}")
    BACKUP_FILE.write_text(content, encoding="utf-8")
    
    # 解析所有游戏块
    # 匹配 const games = [...] 后面可能有 ; 或换行+export
    # 使用贪婪匹配到最后一个 ]，因为文件很大
    match_pattern = r"const\s+games\s*=\s*\[(.*)\]\s*(?:;|\n\s*\n\s*export)"
    body_match = re.search(match_pattern, content, re.S)
    if not body_match:
        print("错误: 无法找到 games 数组")
        print("尝试调试: 检查文件格式...")
        # 检查是否有 const games
        if "const games" not in content:
            print("文件中没有找到 'const games'")
        else:
            print("找到了 'const games'，但正则匹配失败")
            # 尝试找到数组的开始和结束位置
            start_idx = content.find("const games = [")
            if start_idx >= 0:
                print(f"数组开始位置: {start_idx}")
                # 找到最后一个 ]
                last_bracket = content.rfind("]")
                if last_bracket > start_idx:
                    print(f"数组结束位置: {last_bracket}")
                    print(f"数组内容长度: {last_bracket - start_idx - 14}")
        return
    
    body = body_match.group(1)
    
    # 分割游戏块
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
                blocks.append((start, i + 1))
                start = None
    
    print(f"找到 {len(blocks)} 个游戏条目")
    
    fixes = []
    ok_count = 0
    missing_count = 0
    fixed_count = 0
    
    for idx, (start_pos, end_pos) in enumerate(blocks):
        block = body[start_pos:end_pos]
        
        # 提取字段
        id_match = re.search(r"id\s*:\s*['\"]([^'\"]+)['\"]", block)
        title_match = re.search(r"title\s*:\s*['\"]([^'\"]+)['\"]", block)
        url_match = re.search(r"url\s*:\s*['\"]([^'\"]+)['\"]", block)
        
        if not id_match or not url_match:
            continue
        
        gid = id_match.group(1)
        title = title_match.group(1) if title_match else "Unknown"
        url = url_match.group(1)
        
        # 只处理本地游戏
        if not url.startswith("/games/"):
            ok_count += 1
            continue
        
        # 检查文件是否存在
        rel_path = url.lstrip("/")
        fs_path = PUBLIC_DIR / rel_path
        
        if fs_path.exists():
            ok_count += 1
            continue
        
        # 文件不存在，尝试修复
        missing_count += 1
        game_folder = fs_path.parent
        
        entry_file = find_entry_file(game_folder)
        
        if entry_file:
            # 找到入口文件，修复 URL
            new_url = f"/games/{game_folder.name}/{entry_file}"
            # 确保路径格式正确（处理子目录情况）
            if "/" in entry_file:
                new_url = f"/games/{game_folder.name}/{entry_file}"
            else:
                new_url = f"/games/{game_folder.name}/{entry_file}"
            
            # 替换 URL
            old_url_pattern = rf"url\s*:\s*['\"]({re.escape(url)})['\"]"
            new_block = re.sub(old_url_pattern, f"url: '{new_url}'", block)
            
            fixes.append({
                "index": idx,
                "start": start_pos,
                "end": end_pos,
                "id": gid,
                "title": title,
                "old_url": url,
                "new_url": new_url,
                "old_block": block,
                "new_block": new_block
            })
            fixed_count += 1
            print(f"✓ [{gid}] {title}: {url} -> {new_url}")
        else:
            print(f"✗ [{gid}] {title}: {url} - 未找到入口文件")
    
    # 应用修复
    if fixes:
        print(f"\n正在应用 {len(fixes)} 个修复...")
        new_body = body
        # 从后往前替换，避免位置偏移
        for fix in reversed(fixes):
            new_body = new_body[:fix["start"]] + fix["new_block"] + new_body[fix["end"]:]
        
        # 重建完整内容，保持原有的格式
        # 找到数组开始位置
        array_start = body_match.start()
        # 找到数组结束位置（] 之后）
        array_end = content.find("]", body_match.end(1)) + 1
        if array_end <= array_start:
            array_end = len(content)
        
        # 检查后面是否有 export default games
        rest_content = content[array_end:].strip()
        if rest_content.startswith("export"):
            new_content = content[:array_start] + f"const games = [{new_body}]\n\nexport default games"
        else:
            # 保持原有格式
            new_content = content[:body_match.start(1)] + new_body + content[body_match.end(1):]
        
        GAMES_JS.write_text(new_content, encoding="utf-8")
        print(f"✓ 已保存修复后的 games.js")
    else:
        print("\n没有需要修复的 URL")
    
    print(f"\n=== 统计 ===")
    print(f"正常游戏: {ok_count}")
    print(f"缺失文件: {missing_count}")
    print(f"已修复: {fixed_count}")
    print(f"仍缺失: {missing_count - fixed_count}")


if __name__ == "__main__":
    main()
