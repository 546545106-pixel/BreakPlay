#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并游戏数据脚本
将xixi-games文件夹中的游戏数据合并到主项目的games.js中
"""

import os
import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
XIXI_GAMES_JS = PROJECT_ROOT / "xixi-games" / "src" / "data" / "games.js"
MAIN_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def escape_js_string(s):
    """转义JavaScript字符串中的特殊字符"""
    if not isinstance(s, str):
        s = str(s)
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('\t', '\\t')
    return s

def parse_games_js(file_path):
    """解析games.js文件，提取游戏数据"""
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8')
    games = []
    
    # 使用正则表达式匹配游戏对象
    # 匹配 { id: '...', title: '...', ... }
    pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    
    # 更精确的匹配：查找所有游戏对象
    game_blocks = re.findall(r'\{\s*id:\s*[\'"]([^\'"]+)[\'"],\s*title:\s*[\'"]([^\'"]+)[\'"],.*?\}', content, re.DOTALL)
    
    # 更简单的方法：逐行解析
    lines = content.split('\n')
    current_game = None
    in_game = False
    brace_count = 0
    
    for line in lines:
        line = line.strip()
        
        # 检测游戏对象开始
        if line.startswith('{'):
            if current_game is None:
                current_game = {}
                in_game = True
                brace_count = 1
            else:
                brace_count += 1
            continue
        
        # 检测游戏对象结束
        if line.startswith('}') and in_game:
            brace_count -= 1
            if brace_count == 0:
                if current_game and 'id' in current_game:
                    games.append(current_game)
                current_game = None
                in_game = False
            continue
        
        # 解析游戏属性
        if in_game and current_game is not None:
            # 匹配 id: 'value' 或 id: "value"
            for attr in ['id', 'title', 'description', 'instructions', 'url', 'category', 'tags', 'thumb', 'link', 'null', 'star']:
                pattern = rf'{attr}:\s*[\'"]([^\'"]*)[\'"]'
                match = re.search(pattern, line)
                if match:
                    value = match.group(1)
                    if attr == 'star':
                        try:
                            current_game[attr] = int(value) if value else 3
                        except:
                            current_game[attr] = 3
                    else:
                        current_game[attr] = value
                    break
    
    return games

def parse_games_js_simple(file_path):
    """简单解析games.js文件"""
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8')
    games = []
    
    # 使用更简单的方法：查找所有游戏对象
    # 匹配整个游戏对象块
    game_pattern = r'\{\s*id:\s*[\'"]([^\'"]+)[\'"],\s*title:\s*[\'"]([^\'"]+)[\'"],\s*description:\s*[\'"]([^\'"]*)[\'"],\s*instructions:\s*[\'"]([^\'"]*)[\'"],\s*url:\s*[\'"]([^\'"]+)[\'"],\s*category:\s*[\'"]([^\'"]+)[\'"],\s*tags:\s*[\'"]([^\'"]+)[\'"],\s*thumb:\s*[\'"]([^\'"]+)[\'"],\s*link:\s*[\'"]([^\'"]+)[\'"],\s*null:\s*[\'"]([^\'"]*)[\'"],\s*star:\s*(\d+)'
    
    # 更灵活的方法：逐块解析
    # 先找到所有游戏对象的开始和结束位置
    game_blocks = []
    start_pos = 0
    while True:
        start_pos = content.find("  {", start_pos)
        if start_pos == -1:
            break
        # 找到对应的结束位置
        brace_count = 0
        pos = start_pos
        while pos < len(content):
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    game_blocks.append((start_pos, pos + 1))
                    start_pos = pos + 1
                    break
            pos += 1
    
    # 解析每个游戏块
    for start, end in game_blocks:
        game_block = content[start:end]
        game = {}
        
        # 提取各个字段
        for field in ['id', 'title', 'description', 'instructions', 'url', 'category', 'tags', 'thumb', 'link', 'null']:
            pattern = rf'{field}:\s*[\'"]([^\'"]*)[\'"]'
            match = re.search(pattern, game_block, re.DOTALL)
            if match:
                game[field] = match.group(1)
        
        # 提取star（数字）
        star_match = re.search(r'star:\s*(\d+)', game_block)
        if star_match:
            game['star'] = int(star_match.group(1))
        else:
            game['star'] = 3
        
        if 'id' in game:
            games.append(game)
    
    return games

def read_games_from_js(file_path):
    """从games.js文件读取游戏数据（使用AST-like解析）"""
    if not file_path.exists():
        return []
    
    content = file_path.read_text(encoding='utf-8')
    games = []
    
    # 移除注释
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # 使用正则表达式提取所有游戏对象
    # 匹配模式：{ id: '...', title: '...', ... }
    game_pattern = r'\{\s*id:\s*[\'"]([^\'"]+)[\'"],\s*title:\s*[\'"]([^\'"]+)[\'"],\s*description:\s*[\'"]([^\'"]*?)[\'"],\s*instructions:\s*[\'"]([^\'"]*?)[\'"],\s*url:\s*[\'"]([^\'"]+)[\'"],\s*category:\s*[\'"]([^\'"]+)[\'"],\s*tags:\s*[\'"]([^\'"]+)[\'"],\s*thumb:\s*[\'"]([^\'"]+)[\'"],\s*link:\s*[\'"]([^\'"]+)[\'"],\s*null:\s*[\'"]([^\'"]*?)[\'"],\s*star:\s*(\d+)'
    
    # 由于description可能是多行的，我们需要更复杂的解析
    # 分步骤解析：先找到所有游戏对象的边界
    game_objects = []
    pos = 0
    while pos < len(content):
        # 查找游戏对象开始
        obj_start = content.find("  {", pos)
        if obj_start == -1:
            break
        
        # 查找对应的结束位置
        brace_count = 0
        obj_pos = obj_start
        obj_end = -1
        
        while obj_pos < len(content):
            if content[obj_pos] == '{':
                brace_count += 1
            elif content[obj_pos] == '}':
                brace_count -= 1
                if brace_count == 0:
                    obj_end = obj_pos + 1
                    break
            obj_pos += 1
        
        if obj_end > 0:
            game_objects.append(content[obj_start:obj_end])
            pos = obj_end
        else:
            break
    
    # 解析每个游戏对象
    for obj_str in game_objects:
        game = {}
        
        # 提取各个字段（处理多行description）
        patterns = {
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
        
        for field, pattern in patterns.items():
            match = re.search(pattern, obj_str, re.DOTALL)
            if match:
                if field == 'star':
                    game[field] = int(match.group(1))
                else:
                    game[field] = match.group(1)
        
        # 如果没有star，设置默认值
        if 'star' not in game:
            game['star'] = 3
        
        if 'id' in game:
            games.append(game)
    
    return games

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
    
    # 检查文件是否存在
    if not XIXI_GAMES_JS.exists():
        print(f"错误: 找不到文件: {XIXI_GAMES_JS}")
        return
    
    if not MAIN_GAMES_JS.exists():
        print(f"错误: 找不到文件: {MAIN_GAMES_JS}")
        return
    
    try:
        # 1. 读取现有游戏
        print("正在读取主项目的游戏数据...")
        existing_games = read_games_from_js(MAIN_GAMES_JS)
        print(f"主项目现有游戏: {len(existing_games)} 个")
        
        # 2. 读取xixi-games中的游戏
        print("\n正在读取xixi-games中的游戏数据...")
        new_games = read_games_from_js(XIXI_GAMES_JS)
        print(f"xixi-games中的游戏: {len(new_games)} 个")
        
        if not new_games:
            print("警告: 未找到新游戏数据")
            return
        
        # 3. 合并游戏
        print("\n正在合并游戏数据...")
        merged_games, added_count = merge_games(existing_games, new_games)
        print(f"合并后总计: {len(merged_games)} 个游戏")
        print(f"新增游戏: {added_count} 个")
        
        # 4. 备份原文件
        if MAIN_GAMES_JS.exists():
            backup_path = MAIN_GAMES_JS.with_suffix('.js.backup')
            shutil.copy2(MAIN_GAMES_JS, backup_path)
            print(f"\n已备份原文件到: {backup_path}")
        
        # 5. 写入新文件
        print("\n正在写入新的games.js文件...")
        write_games_js(merged_games, MAIN_GAMES_JS)
        print(f"已更新: {MAIN_GAMES_JS}")
        
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
