#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并所有游戏脚本
将之前的106个外部游戏和新的423个本地游戏合并
"""

import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
BACKUP_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js.backup"
XIXI_GAMES_JS = PROJECT_ROOT / "xixi-games" / "src" / "data" / "games.js"
MAIN_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def extract_array_content(content):
    """提取数组内容"""
    # 找到数组开始
    start_match = re.search(r'const\s+games\s*=\s*\[|export\s+default\s*\[', content)
    if not start_match:
        return None
    
    start_pos = content.find('[', start_match.end() - 1)
    if start_pos == -1:
        return None
    
    # 找到匹配的结束括号
    bracket_count = 0
    in_string = False
    string_char = None
    escape_next = False
    
    for i in range(start_pos, len(content)):
        char = content[i]
        
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char in ('"', "'") and not escape_next:
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
            continue
        
        if in_string:
            continue
        
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                return content[start_pos + 1:i]
    
    return None

def split_games(array_content):
    """分割游戏对象"""
    games = []
    current = []
    brace_level = 0
    in_string = False
    string_char = None
    escape_next = False
    
    for i, char in enumerate(array_content):
        if escape_next:
            escape_next = False
            current.append(char)
            continue
        
        if char == '\\':
            escape_next = True
            current.append(char)
            continue
        
        if char in ('"', "'") and not escape_next:
            current.append(char)
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
            continue
        
        current.append(char)
        
        if in_string:
            continue
        
        if char == '{':
            brace_level += 1
        elif char == '}':
            brace_level -= 1
            if brace_level == 0:
                game_str = ''.join(current).strip()
                if game_str and 'id:' in game_str:
                    games.append(game_str)
                current = []
                # 跳过后续的逗号和空白
                j = i + 1
                while j < len(array_content) and array_content[j] in (',', ' ', '\n', '\r', '\t'):
                    j += 1
    
    return games

def get_game_id(game_str):
    """提取游戏ID"""
    match = re.search(r"id:\s*['\"]([^'\"]+)['\"]", game_str)
    return match.group(1) if match else None

def merge_all_games():
    """合并所有游戏"""
    try:
        print("=" * 70)
        print("合并所有游戏脚本")
        print("=" * 70)
        
        # 检查项目根目录
        if not PROJECT_ROOT.exists():
            print(f"\n[错误] 项目根目录不存在: {PROJECT_ROOT}")
            print("请确保在正确的目录运行脚本")
            return False
        
        # 1. 读取之前的106个游戏
        print("\n步骤1: 读取之前的106个外部游戏...")
        old_games = []
        
        source_file = None
        if BACKUP_GAMES_JS.exists():
            source_file = BACKUP_GAMES_JS
            print(f"找到备份文件: {BACKUP_GAMES_JS}")
        elif XIXI_GAMES_JS.exists():
            source_file = XIXI_GAMES_JS
            print(f"找到xixi-games文件: {XIXI_GAMES_JS}")
        else:
            print("警告: 找不到之前的游戏文件")
            print(f"  查找路径1: {BACKUP_GAMES_JS}")
            print(f"  查找路径2: {XIXI_GAMES_JS}")
        
        if source_file:
            try:
                content = source_file.read_text(encoding='utf-8')
                array_content = extract_array_content(content)
                if array_content:
                    old_games = split_games(array_content)
                    print(f"从 {source_file.name} 读取到 {len(old_games)} 个游戏")
                else:
                    print(f"警告: 无法从 {source_file.name} 提取游戏数据")
            except Exception as e:
                print(f"错误: 读取 {source_file.name} 时出错: {e}")
        
        # 2. 读取新的423个本地游戏
        print("\n步骤2: 读取新的423个本地游戏...")
        new_games = []
        if MAIN_GAMES_JS.exists():
            try:
                content = MAIN_GAMES_JS.read_text(encoding='utf-8')
                array_content = extract_array_content(content)
                if array_content:
                    new_games = split_games(array_content)
                    print(f"从主文件读取到 {len(new_games)} 个游戏")
                else:
                    print("错误: 无法从主文件提取游戏数据")
                    return False
            except Exception as e:
                print(f"错误: 读取主文件时出错: {e}")
                return False
        else:
            print(f"错误: 找不到主游戏文件: {MAIN_GAMES_JS}")
            return False
    
        # 3. 合并游戏（去重）
        print("\n步骤3: 合并游戏（去重）...")
        all_games_dict = {}
        
        for game_str in old_games:
            game_id = get_game_id(game_str)
            if game_id:
                all_games_dict[game_id] = game_str
        
        for game_str in new_games:
            game_id = get_game_id(game_str)
            if game_id:
                all_games_dict[game_id] = game_str
        
        all_games = list(all_games_dict.values())
        
        print(f"合并后共有 {len(all_games)} 个游戏")
        print(f"  - 外部游戏: {len(old_games)} 个")
        print(f"  - 本地游戏: {len(new_games)} 个")
        
        if len(all_games) == 0:
            print("错误: 没有找到任何游戏，无法合并")
            return False
        
        # 4. 生成新的games.js文件
        print("\n步骤4: 生成新的games.js文件...")
        
        try:
            games_js_content = "const games = [\n"
            
            for i, game_str in enumerate(all_games):
                # 清理游戏字符串，移除多余的空白和空行
                game_str = game_str.strip()
                
                # 移除开头和结尾的大括号周围的空白
                game_str = re.sub(r'^\s*\{', '{', game_str)
                game_str = re.sub(r'\}\s*$', '}', game_str)
                
                # 格式化游戏对象（添加正确的缩进）
                lines = game_str.split('\n')
                formatted_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped:
                        # 确保正确的缩进（2个空格）
                        formatted_lines.append('  ' + stripped)
                    # 跳过空行，避免产生空逗号
                
                if formatted_lines:
                    games_js_content += '\n'.join(formatted_lines)
                    if i < len(all_games) - 1:
                        games_js_content += ","
                    games_js_content += "\n"
            
            games_js_content += "]\n\n"
            games_js_content += "export default games\n"
            
            # 清理生成的内容：移除所有空逗号（, , , 这样的模式）
            games_js_content = re.sub(r',\s*,+', ',', games_js_content)  # 移除连续的空逗号
            games_js_content = re.sub(r',\s*\n\s*,', ',\n', games_js_content)  # 移除换行间的空逗号
            
            # 备份当前文件
            if MAIN_GAMES_JS.exists():
                backup_path = MAIN_GAMES_JS.with_suffix('.js.backup2')
                try:
                    shutil.copy2(MAIN_GAMES_JS, backup_path)
                    print(f"已备份当前文件到: {backup_path}")
                except Exception as e:
                    print(f"警告: 备份文件失败: {e}")
            
            # 写入新文件
            MAIN_GAMES_JS.write_text(games_js_content, encoding='utf-8')
            print(f"已更新: {MAIN_GAMES_JS}")
            
            print("\n" + "=" * 70)
            print("合并完成！")
            print("=" * 70)
            print(f"✓ 成功合并 {len(all_games)} 个游戏")
            print(f"  - 外部游戏（gamemonetize.com）: {len(old_games)} 个")
            print(f"  - 本地游戏（/games/目录）: {len(new_games)} 个")
            print("\n所有游戏现在都可以正常访问了！")
            return True
            
        except Exception as e:
            print(f"错误: 生成或写入文件时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"\n[严重错误] 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = merge_all_games()
    sys.exit(0 if success else 1)
