#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接合并游戏数据 - 简单可靠版本
"""

import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
XIXI_GAMES_JS = PROJECT_ROOT / "xixi-games" / "src" / "data" / "games.js"
MAIN_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def read_games_simple(file_path):
    """简单读取游戏 - 直接提取游戏对象块"""
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return []
    
    content = file_path.read_text(encoding='utf-8')
    games = []
    
    # 找到所有游戏对象块（从 "  {" 开始到对应的 "  }," 或 "  }" 结束）
    # 使用更简单的方法：逐行解析
    lines = content.split('\n')
    current_game_lines = []
    in_game = False
    brace_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # 检测游戏对象开始
        if stripped.startswith('{') and not in_game:
            in_game = True
            brace_count = 1
            current_game_lines = [line]
            continue
        
        if in_game:
            current_game_lines.append(line)
            
            # 计算大括号
            brace_count += line.count('{') - line.count('}')
            
            # 检测游戏对象结束
            if brace_count == 0:
                game_block = '\n'.join(current_game_lines)
                games.append(game_block)
                current_game_lines = []
                in_game = False
    
    return games

def extract_game_id(game_block):
    """从游戏块中提取ID"""
    match = re.search(r"id:\s*['\"]([^'\"]+)['\"]", game_block)
    if match:
        return match.group(1)
    return None

def add_star_field(game_block):
    """为游戏块添加star字段（如果缺失）"""
    if 'star:' not in game_block:
        # 在 null 字段后添加 star
        game_block = re.sub(
            r"(null:\s*['\"][^'\"]*['\"])",
            r"\1,\n    star: 3",
            game_block
        )
    return game_block

def main():
    print("=" * 60)
    print("合并游戏数据（直接版）")
    print("=" * 60)
    print()
    
    # 检查文件
    if not XIXI_GAMES_JS.exists():
        print(f"错误: 找不到文件: {XIXI_GAMES_JS}")
        input("按回车键退出...")
        return
    
    if not MAIN_GAMES_JS.exists():
        print(f"错误: 找不到文件: {MAIN_GAMES_JS}")
        input("按回车键退出...")
        return
    
    try:
        # 读取主项目的游戏
        print("正在读取主项目的游戏...")
        main_content = MAIN_GAMES_JS.read_text(encoding='utf-8')
        main_games = read_games_simple(MAIN_GAMES_JS)
        print(f"✓ 主项目游戏数量: {len(main_games)}")
        
        # 提取主项目中的游戏ID
        main_ids = set()
        for game in main_games:
            game_id = extract_game_id(game)
            if game_id:
                main_ids.add(game_id)
        
        # 读取xixi-games中的游戏
        print("\n正在读取xixi-games中的游戏...")
        xixi_games = read_games_simple(XIXI_GAMES_JS)
        print(f"✓ xixi-games游戏数量: {len(xixi_games)}")
        
        # 合并游戏（去重）
        print("\n正在合并游戏（去重）...")
        new_games = []
        added_count = 0
        
        for game in xixi_games:
            game_id = extract_game_id(game)
            if game_id and game_id not in main_ids:
                # 添加star字段（如果缺失）
                game = add_star_field(game)
                new_games.append(game)
                main_ids.add(game_id)
                added_count += 1
        
        print(f"✓ 新增游戏数量: {added_count}")
        
        if added_count == 0:
            print("\n没有新游戏需要添加（所有游戏已存在）")
            input("按回车键退出...")
            return
        
        # 备份原文件
        print("\n正在备份原文件...")
        backup_path = MAIN_GAMES_JS.with_suffix('.js.backup')
        shutil.copy2(MAIN_GAMES_JS, backup_path)
        print(f"✓ 已备份到: {backup_path}")
        
        # 生成新的games.js内容
        print("\n正在生成新的games.js文件...")
        
        # 读取主文件，找到games数组的开始和结束位置
        main_content = MAIN_GAMES_JS.read_text(encoding='utf-8')
        
        # 找到最后一个游戏对象的结束位置
        last_game_end = main_content.rfind('  }')
        if last_game_end == -1:
            print("错误: 无法找到游戏数组结构")
            input("按回车键退出...")
            return
        
        # 找到最后一个游戏对象后的位置
        insert_pos = main_content.find('\n]', last_game_end)
        if insert_pos == -1:
            insert_pos = main_content.find(']', last_game_end)
        
        if insert_pos == -1:
            print("错误: 无法找到数组结束位置")
            input("按回车键退出...")
            return
        
        # 构建新内容
        before = main_content[:insert_pos]
        after = main_content[insert_pos:]
        
        # 插入新游戏
        new_games_text = ',\n'.join(['  ' + game.rstrip().rstrip(',') for game in new_games])
        new_content = before + ',\n' + new_games_text + '\n' + after
        
        # 写入文件
        MAIN_GAMES_JS.write_text(new_content, encoding='utf-8')
        print(f"✓ 已更新: {MAIN_GAMES_JS}")
        
        print("\n" + "=" * 60)
        print("合并完成！")
        print("=" * 60)
        print(f"总计游戏数量: {len(main_games) + added_count}")
        print(f"新增游戏数量: {added_count}")
        print("\n现在可以运行 npm run dev 查看所有游戏了！")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
