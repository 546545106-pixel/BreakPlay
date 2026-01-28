#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复并合并游戏数据
"""

import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
XIXI_GAMES_JS = PROJECT_ROOT / "xixi-games" / "src" / "data" / "games.js"
MAIN_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def extract_all_games(content):
    """提取所有游戏对象"""
    games = []
    lines = content.split('\n')
    
    current_game = []
    in_game = False
    brace_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # 检测游戏开始
        if stripped == '{' or (stripped.startswith('{') and not in_game):
            in_game = True
            brace_count = 1
            current_game = [line]
            continue
        
        if in_game:
            current_game.append(line)
            brace_count += line.count('{') - line.count('}')
            
            # 检测游戏结束
            if brace_count == 0:
                game_block = '\n'.join(current_game)
                games.append(game_block)
                current_game = []
                in_game = False
    
    return games

def get_game_id(game_block):
    """获取游戏ID"""
    match = re.search(r"id:\s*['\"]([^'\"]+)['\"]", game_block)
    return match.group(1) if match else None

def ensure_star_field(game_block):
    """确保有star字段"""
    if 'star:' not in game_block:
        # 在null字段后添加star
        game_block = re.sub(
            r"(null:\s*['\"][^'\"]*['\"])",
            r"\1,\n    star: 3",
            game_block
        )
    return game_block

print("=" * 60)
print("修复并合并游戏数据")
print("=" * 60)
print()

# 读取xixi-games中的游戏（这些是完整正确的）
print("正在读取xixi-games中的游戏...")
xixi_content = XIXI_GAMES_JS.read_text(encoding='utf-8')
xixi_games = extract_all_games(xixi_content)
print(f"✓ 找到 {len(xixi_games)} 个游戏")

# 读取主项目的游戏
print("\n正在读取主项目的游戏...")
main_content = MAIN_GAMES_JS.read_text(encoding='utf-8')
main_games = extract_all_games(main_content)
print(f"✓ 找到 {len(main_games)} 个游戏")

# 获取主项目中的游戏ID
main_ids = {get_game_id(g) for g in main_games if get_game_id(g)}

# 找出新游戏
print("\n正在检查新游戏...")
new_games = []
for game in xixi_games:
    game_id = get_game_id(game)
    if game_id and game_id not in main_ids:
        game = ensure_star_field(game)
        new_games.append(game)
        main_ids.add(game_id)

print(f"✓ 发现 {len(new_games)} 个新游戏")

if len(new_games) == 0:
    print("\n所有游戏都已存在，无需合并")
    input("按回车键退出...")
    exit()

# 备份
print("\n正在备份原文件...")
backup_path = MAIN_GAMES_JS.with_suffix('.js.backup')
shutil.copy2(MAIN_GAMES_JS, backup_path)
print(f"✓ 已备份到: {backup_path}")

# 合并：找到最后一个游戏的位置，插入新游戏
print("\n正在合并游戏...")
last_game_pos = main_content.rfind('  }')
if last_game_pos == -1:
    print("错误: 无法找到游戏数组结构")
    input("按回车键退出...")
    exit()

# 找到数组结束位置
array_end = main_content.find('\n]', last_game_pos)
if array_end == -1:
    array_end = main_content.find(']', last_game_pos)

if array_end == -1:
    print("错误: 无法找到数组结束位置")
    input("按回车键退出...")
    exit()

# 构建新内容
before = main_content[:array_end]
after = main_content[array_end:]

# 格式化新游戏
new_games_text = ',\n'.join(['  ' + g.rstrip().rstrip(',') for g in new_games])

# 合并
new_content = before + ',\n' + new_games_text + '\n' + after

# 写入
MAIN_GAMES_JS.write_text(new_content, encoding='utf-8')
print(f"✓ 已更新: {MAIN_GAMES_JS}")

print("\n" + "=" * 60)
print("合并完成！")
print("=" * 60)
print(f"主项目原有游戏: {len(main_games)}")
print(f"新增游戏: {len(new_games)}")
print(f"总计游戏: {len(main_games) + len(new_games)}")
print("\n现在可以运行 npm run dev 查看所有游戏了！")

input("\n按回车键退出...")
