#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
95 个 H5 游戏部署和翻译脚本

功能：
1. 扫描 95 套 H5 小游戏源码大合集目录下的所有游戏文件夹
2. 复制到 public/games/ 对应的子目录（不会删除已有的 431 个游戏）
3. 对游戏中的中文文本做英文翻译（使用与 431 脚本相同的词典和规则）
4. 清理常见第三方广告脚本，并在游戏页面中注入站点自有的 GameAdAPI 接口
5. 将新游戏信息追加到 src/data/games.js，保证在网站上可以正常显示和打开
"""

import os
import shutil
import json
import re
from pathlib import Path
from typing import List, Dict

# 基本路径配置
PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
SOURCE_GAMES_DIR = PROJECT_ROOT / "95套H5小游戏源码大合集"
TARGET_GAMES_DIR = PROJECT_ROOT / "public" / "games"
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

# 引用 431 脚本中相同的翻译配置（拷贝简化版）
TRANSLATION_DICT = {
    '是男人就下100层': 'Real Man Goes Down 100 Floors',
    '开始游戏': 'Start Game',
    '游戏结束': 'Game Over',
    '重新开始': 'Restart',
    '加载完成': 'Loading Complete',
    '网络错误': 'Network Error',
    '请稍候': 'Please Wait',
    '下一关': 'Next Level',
    '上一关': 'Previous Level',
    '最高分': 'High Score',
    '生命值': 'HP',
    '开始': 'Start',
    '暂停': 'Pause',
    '继续': 'Continue',
    '得分': 'Score',
    '分数': 'Score',
    '等级': 'Level',
    '关卡': 'Level',
    '设置': 'Settings',
    '音效': 'Sound',
    '音乐': 'Music',
    '帮助': 'Help',
    '说明': 'Instructions',
    '返回': 'Back',
    '退出': 'Exit',
    '确认': 'Confirm',
    '取消': 'Cancel',
    '确定': 'OK',
    '开始按钮': 'Start',
    '继续游戏': 'Continue Game',
    '主菜单': 'Main Menu',
    '新游戏': 'New Game',
    '更多游戏': 'More Games',
}

TRANSLATABLE_EXTENSIONS = {'.html', '.htm', '.js', '.css', '.json', '.txt', '.xml'}

SKIP_PATTERNS = {
    'node_modules', '.git', '.svn', '.DS_Store',
    'Thumbs.db', '.min.js', '.min.css', 'jquery', 'bootstrap'
}

AD_KEYWORDS = [
    'adsbygoogle',
    'pagead2.googlesyndication.com',
    'doubleclick.net',
    'cpro.baidu.com',
    'hm.baidu.com',
    'cnzz.com',
]


def is_chinese(text: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def translate_text(text: str) -> str:
    if not is_chinese(text):
        return text

    original = text
    # 长词优先
    for cn, en in sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True):
        if cn in text:
            text = text.replace(cn, en)

    return text if text != original else original


def remove_ad_scripts_and_inject_api(html: str, slot_id: str) -> str:
    # 移除常见广告 script 标签
    pattern = re.compile(
        r'<script[^>]*(?:' +
        r'adsbygoogle|pagead2\.googlesyndication\.com|doubleclick\.net|cpro\.baidu\.com|hm\.baidu\.com|cnzz\.com' +
        r')[\s\S]*?</script>',
        flags=re.IGNORECASE
    )
    html = re.sub(pattern, '<!-- removed third-party ad script -->', html)

    # 在 body 结束前注入 GameAdAPI 调用
    snippet = f"""
<script src="/game-ad-api.js"></script>
<script>
  window.GameAdAPI && GameAdAPI.requestGameAd('game_{slot_id}');
</script>
""".strip()

    if '</body>' in html:
        html = html.replace('</body>', snippet + '\n</body>', 1)
    else:
        html = html + '\n' + snippet

    return html


def translate_file_content(content: str, file_path: Path) -> str:
    # 先做广告清理和翻译
    if file_path.suffix in {'.html', '.htm'}:
        # 翻译 <title> 和 meta 文本
        content = re.sub(
            r'<title>([^<]*)</title>',
            lambda m: f'<title>{translate_text(m.group(1))}</title>',
            content,
            flags=re.IGNORECASE
        )
        content = re.sub(
            r'<meta\s+name=["\'](description|keywords)["\']\s+content=["\']([^"\']*)["\']',
            lambda m: f'<meta name="{m.group(1)}" content="{translate_text(m.group(2))}"',
            content,
            flags=re.IGNORECASE
        )
    elif file_path.suffix == '.js':
        # 注释掉包含广告关键字的行
        lines = []
        for line in content.splitlines():
            if any(k in line for k in AD_KEYWORDS):
                lines.append('// [removed-ad] ' + line)
            else:
                lines.append(line)
        content = '\n'.join(lines)

    return content


def should_skip_file(file_path: Path) -> bool:
    file_str = str(file_path).lower()
    for pat in SKIP_PATTERNS:
        if pat.lower() in file_str:
            return True
    return False


def translate_and_clean_game(game_dir: Path, slot_id: str):
    """翻译一个游戏目录，并清理广告、注入 GameAdAPI。"""
    for file_path in game_dir.rglob('*'):
        if not file_path.is_file():
            continue
        if should_skip_file(file_path):
            continue
        if file_path.suffix not in TRANSLATABLE_EXTENSIONS:
            continue

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        original = content
        content = translate_file_content(content, file_path)

        # 对入口 HTML 再额外注入 GameAdAPI
        if file_path.suffix in {'.html', '.htm'} and 'game_' + slot_id not in content:
            content = remove_ad_scripts_and_inject_api(content, slot_id)

        if content != original:
            try:
                file_path.write_text(content, encoding='utf-8')
            except Exception:
                pass


def find_all_game_folders() -> List[Dict]:
    game_folders: List[Dict] = []
    if not SOURCE_GAMES_DIR.exists():
        print(f"错误: 源游戏目录不存在: {SOURCE_GAMES_DIR}")
        return game_folders

    for game_folder in SOURCE_GAMES_DIR.iterdir():
        if not game_folder.is_dir():
            continue
        html_files = list(game_folder.glob('*.html')) + list(game_folder.glob('*.htm'))
        if not html_files:
            html_files = list(game_folder.rglob('*.html')) + list(game_folder.rglob('*.htm'))
        if not html_files:
            continue
        html_file = html_files[0]
        game_folders.append({
            'name': game_folder.name,
            'path': game_folder,
            'html_file': html_file.name,
        })
    return game_folders


def copy_and_process_games(game_folders: List[Dict]) -> List[Dict]:
    if not TARGET_GAMES_DIR.exists():
        TARGET_GAMES_DIR.mkdir(parents=True, exist_ok=True)

    deployed_games: List[Dict] = []

    print(f"\n开始部署 {len(game_folders)} 个游戏...")

    for idx, info in enumerate(game_folders, 1):
        game_name = info['name']
        source_dir = info['path']

        safe_name = re.sub(r'[^a-zA-Z0-9\-_]', '_', game_name)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_') or f'game_{idx}'

        dest_dir = TARGET_GAMES_DIR / safe_name

        try:
            print(f"\n[{idx}/{len(game_folders)}] 处理游戏: {game_name} -> {safe_name}")

            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(source_dir, dest_dir)

            # 翻译 + 清广告 + 注入 GameAdAPI
            translate_and_clean_game(dest_dir, safe_name)

            # 确定入口 html
            html_file = info['html_file']
            if not (dest_dir / html_file).exists():
                html_files = list(dest_dir.glob('*.html')) + list(dest_dir.glob('*.htm'))
                if html_files:
                    html_file = html_files[0].name

            deployed_games.append({
                'name': game_name,
                'safe_name': safe_name,
                'html_file': html_file,
                'path': f"/games/{safe_name}/{html_file}",
            })
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            continue

    return deployed_games


def read_existing_games() -> List[Dict]:
    if not GAMES_JS.exists():
        return []
    try:
        content = GAMES_JS.read_text(encoding='utf-8')
        match = re.search(r'(?:const\s+games\s*=\s*|export\s+default\s*)(\[[\s\S]*?\])', content)
        if not match:
            return []
        games_str = match.group(1)
        games_str = re.sub(r'//.*?$', '', games_str, flags=re.MULTILINE)
        games_str = re.sub(r'/\*.*?\*/', '', games_str, flags=re.DOTALL)
        return json.loads(games_str)
    except Exception as e:
        print(f"警告: 读取现有 games.js 失败: {e}")
        return []


def generate_game_entry(game_info: Dict, index: int, existing_games: List[Dict]) -> Dict:
    max_id = 0
    for g in existing_games:
        try:
            gid = int(g.get('id', '0'))
            if gid > max_id:
                max_id = gid
        except Exception:
            continue

    new_id = str(max_id + index + 1)
    title = game_info['name'].replace('_', ' ').replace('-', ' ').title()
    description = f"Play {title} - An exciting HTML5 game. Challenge yourself and have fun!"

    return {
        'id': new_id,
        'title': title,
        'description': description,
        'instructions': 'Use mouse or touch controls to play. Follow the on-screen instructions.',
        'url': game_info['path'],
        'category': 'Arcade',
        'tags': 'HTML5, Game, Fun',
        'thumb': 'https://img.gamemonetize.com/default/512x512.jpg',
        'link': game_info['safe_name'].lower().replace('_', '-'),
        'null': '',
        'star': 3,
    }


def update_games_js(deployed_games: List[Dict]):
    print("\n正在更新 games.js ...")
    existing = read_existing_games()
    new_entries = [generate_game_entry(info, i, existing) for i, info in enumerate(deployed_games)]
    all_games = existing + new_entries

    out = ["const games = ["]
    for i, g in enumerate(all_games):
        out.append("  {")
        game_id = str(g['id']).replace("'", "\\'")
        game_title = str(g['title']).replace("'", "\\'")
        game_desc = str(g['description']).replace("'", "\\'")
        game_instr = str(g['instructions']).replace("'", "\\'")
        game_url = str(g['url']).replace("'", "\\'")
        game_cat = str(g['category']).replace("'", "\\'")
        game_tags = str(g['tags']).replace("'", "\\'")
        game_thumb = str(g['thumb']).replace("'", "\\'")
        game_link = str(g['link']).replace("'", "\\'")
        game_null = str(g['null']).replace("'", "\\'")

        out.append(f"    id: '{game_id}',")
        out.append(f"    title: '{game_title}',")
        out.append(f"    description: '{game_desc}',")
        out.append(f"    instructions: '{game_instr}',")
        out.append(f"    url: '{game_url}',")
        out.append(f"    category: '{game_cat}',")
        out.append(f"    tags: '{game_tags}',")
        out.append(f"    thumb: '{game_thumb}',")
        out.append(f"    link: '{game_link}',")
        out.append(f"    null: '{game_null}',")
        out.append(f"    star: {g['star']}")
        out.append("  }" + ("," if i < len(all_games) - 1 else ""))
    out.append("]\n")
    out.append("export default games\n")

    if GAMES_JS.exists():
        backup = GAMES_JS.with_suffix('.js.backup_95')
        shutil.copy2(GAMES_JS, backup)
        print(f"已备份原 games.js 到: {backup}")

    GAMES_JS.write_text('\n'.join(out), encoding='utf-8')
    print(f"已写入 {GAMES_JS}，总游戏数: {len(all_games)}")


def main():
    print("=" * 70)
    print("95 个 H5 游戏部署与翻译脚本")
    print("=" * 70)

    if not SOURCE_GAMES_DIR.exists():
        print(f"错误: 源游戏目录不存在: {SOURCE_GAMES_DIR}")
        return

    game_folders = find_all_game_folders()
    print(f"找到 {len(game_folders)} 个游戏文件夹")
    if not game_folders:
        print("未找到任何游戏文件夹，退出。")
        return

    deployed = copy_and_process_games(game_folders)
    if not deployed:
        print("没有成功部署任何游戏。")
        return

    update_games_js(deployed)

    print("\n部署完成，请在浏览器中测试若干游戏以确保运行正常。")


if __name__ == "__main__":
    main()

