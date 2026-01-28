#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并游戏数据脚本（简单版）
直接读取JavaScript文件并合并游戏数据
"""

import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
XIXI_GAMES_JS = PROJECT_ROOT / "xixi-games" / "src" / "data" / "games.js"
MAIN_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def extract_games_from_content(content):
    """从JavaScript内容中提取游戏对象"""
    games = []
    
    # 移除注释
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # 找到所有游戏对象（从 "  {" 到对应的 "  }," 或 "  }"）
    pattern = r'  \{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        game_block = match.group(0)
        game = {}
        
        # 提取各个字段
        fields = {
            'id': r"id:\s*['\"]([^'\"]+)['\"]",
            'title': r"title:\s*['\"]([^'\"]+)['\"]",
            'description': r"description:\s*['\"]([^'\"]*?)['\"]",
            'instructions': r"instructions:\s*['\"]([^'\"]*?)['\"]",
            'url': r"url:\s*['\"]([^'\"]+)['\"]",
            'category': r"category:\s*['\"]([^'\"]+)['\"]",
            'tags': r"tags:\s*['\"]([^'\"]+)['\"]",
            'thumb': r"thumb:\s*['\"]([^'\"]+)['\"]",
            'link': r"link:\s*['\"]([^'\"]+)['\"]",
            'null': r"null:\s*['\"]([^'\"]*?)['\"]",
            'star': r"star:\s*(\d+)"
        }
        
        for field, pattern in fields.items():
            field_match = re.search(pattern, game_block, re.DOTALL)
            if field_match:
                if field == 'star':
                    try:
                        game[field] = int(field_match.group(1))
                    except:
                        game[field] = 3
                else:
                    game[field] = field_match.group(1)
        
        # 处理多行description（如果description跨多行）
        if 'description' not in game:
            # 尝试匹配多行description
            desc_pattern = r"description:\s*['\"](.*?)['\"]"
            desc_match = re.search(desc_pattern, game_block, re.DOTALL)
            if desc_match:
                game['description'] = desc_match.group(1).strip()
        
        # 确保必要字段存在
        if 'id' in game:
            if 'star' not in game:
                game['star'] = 3
            if 'null' not in game:
                game['null'] = ''
            games.append(game)
    
    return games

def read_games(file_path):
    """读取games.js文件并提取游戏数据"""
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8')
    return extract_games_from_content(content)

def merge_games(existing_games, new_games):
    """合并游戏列表，避免重复（基于ID）"""
    existing_ids = {game['id'] for game in existing_games if 'id' in game}
    
    merged = existing_games.copy()
    added_count = 0
    
    for new_game in new_games:
        if 'id' not in new_game:
            continue
        
        if new_game['id'] not in existing_ids:
            merged.append(new_game)
            existing_ids.add(new_game['id'])
            added_count += 1
    
    return merged, added_count

def escape_js_string(s):
    """转义JavaScript字符串"""
    if not isinstance(s, str):
        s = str(s)
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    return s

def write_games_js(games, output_path):
    """写入games.js文件"""
    games_js_content = "const games = [\n"
    
    for i, game in enumerate(games):
        games_js_content += "  {\n"
        games_js_content += f"    id: '{escape_js_string(game.get('id', ''))}',\n"
        games_js_content += f"    title: '{escape_js_string(game.get('title', ''))}',\n"
        games_js_content += f"    description: '{escape_js_string(game.get('description', ''))}',\n"
        games_js_content += f"    instructions: '{escape_js_string(game.get('instructions', ''))}',\n"
        games_js_content += f"    url: '{escape_js_string(game.get('url', ''))}',\n"
        games_js_content += f"    category: '{escape_js_string(game.get('category', 'Arcade'))}',\n"
        games_js_content += f"    tags: '{escape_js_string(game.get('tags', ''))}',\n"
        games_js_content += f"    thumb: '{escape_js_string(game.get('thumb', ''))}',\n"
        games_js_content += f"    link: '{escape_js_string(game.get('link', ''))}',\n"
        games_js_content += f"    null: '{escape_js_string(game.get('null', ''))}',\n"
        games_js_content += f"    star: {game.get('star', 3)}\n"
        games_js_content += "  }"
        if i < len(games) - 1:
            games_js_content += ","
        games_js_content += "\n"
    
    games_js_content += "]\n\n"
    games_js_content += "export default games\n"
    
    output_path.write_text(games_js_content, encoding='utf-8')

def main():
    print("=" * 60)
    print("合并游戏数据脚本")
    print("=" * 60)
    print()
    
    # 检查文件
    if not XIXI_GAMES_JS.exists():
        print(f"错误: 找不到文件: {XIXI_GAMES_JS}")
        return
    
    if not MAIN_GAMES_JS.exists():
        print(f"错误: 找不到文件: {MAIN_GAMES_JS}")
        return
    
    try:
        # 读取现有游戏
        print("正在读取主项目的游戏数据...")
        existing_games = read_games(MAIN_GAMES_JS)
        print(f"✓ 主项目现有游戏: {len(existing_games)} 个")
        
        # 读取xixi-games中的游戏
        print("\n正在读取xixi-games中的游戏数据...")
        new_games = read_games(XIXI_GAMES_JS)
        print(f"✓ xixi-games中的游戏: {len(new_games)} 个")
        
        if not new_games:
            print("警告: 未找到新游戏数据")
            return
        
        # 合并游戏
        print("\n正在合并游戏数据（去重）...")
        merged_games, added_count = merge_games(existing_games, new_games)
        print(f"✓ 合并后总计: {len(merged_games)} 个游戏")
        print(f"✓ 新增游戏: {added_count} 个")
        
        # 备份
        if MAIN_GAMES_JS.exists():
            backup_path = MAIN_GAMES_JS.with_suffix('.js.backup')
            shutil.copy2(MAIN_GAMES_JS, backup_path)
            print(f"\n✓ 已备份原文件到: {backup_path}")
        
        # 写入新文件
        print("\n正在写入新的games.js文件...")
        write_games_js(merged_games, MAIN_GAMES_JS)
        print(f"✓ 已更新: {MAIN_GAMES_JS}")
        
        print("\n" + "=" * 60)
        print("合并完成！")
        print("=" * 60)
        print(f"总计游戏数量: {len(merged_games)}")
        print(f"新增游戏数量: {added_count}")
        print("\n现在可以运行 npm run dev 查看所有游戏了！")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
