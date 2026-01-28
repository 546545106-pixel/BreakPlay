#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复games.js文件格式
移除空逗号，确保所有游戏对象格式正确
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
MAIN_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def fix_games_js():
    """修复games.js文件格式"""
    print("=" * 70)
    print("修复games.js文件格式")
    print("=" * 70)
    
    if not MAIN_GAMES_JS.exists():
        print(f"错误: 找不到文件: {MAIN_GAMES_JS}")
        return False
    
    print(f"\n读取文件: {MAIN_GAMES_JS}")
    content = MAIN_GAMES_JS.read_text(encoding='utf-8')
    
    print("修复格式问题...")
    
    # 1. 移除所有单独的空逗号行（, 或 , , ,）
    # 匹配：行首空白 + 逗号 + 可选空白 + 换行
    content = re.sub(r'^\s*,+\s*$', '', content, flags=re.MULTILINE)
    
    # 2. 移除连续的空逗号（, , ,）
    content = re.sub(r',\s*,+', ',', content)
    
    # 3. 移除 } 后跟换行再跟逗号的情况，改为 } 后直接跟逗号
    content = re.sub(r'\}\s*\n\s*,+', '},\n', content)
    
    # 4. 确保每个游戏对象后只有一个逗号（最后一个除外）
    # 先找到所有游戏对象，然后重新格式化
    lines = content.split('\n')
    fixed_lines = []
    in_array = False
    brace_level = 0
    last_was_closing_brace = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 检测数组开始
        if 'const games = [' in line:
            in_array = True
            fixed_lines.append(line)
            continue
        
        if stripped == '[' and not in_array:
            in_array = True
            fixed_lines.append(line)
            continue
        
        # 检测数组结束
        if stripped == ']' and in_array:
            in_array = False
            fixed_lines.append(line)
            continue
        
        if in_array:
            # 跳过空行和空逗号
            if not stripped or stripped == ',':
                continue
            
            # 处理游戏对象
            if stripped == '{':
                brace_level += 1
                fixed_lines.append('  {')
                last_was_closing_brace = False
            elif stripped == '}':
                brace_level -= 1
                # 检查下一个对象是否存在
                has_next = False
                for j in range(i + 1, len(lines)):
                    next_stripped = lines[j].strip()
                    if next_stripped and next_stripped != ',':
                        if next_stripped == '{':
                            has_next = True
                        break
                    elif next_stripped == ',':
                        continue
                
                if has_next:
                    fixed_lines.append('  },')
                else:
                    fixed_lines.append('  }')
                last_was_closing_brace = True
            elif stripped.startswith('}'):
                # 处理 } 后跟逗号的情况
                brace_level -= 1
                fixed_lines.append('  },')
                last_was_closing_brace = True
            elif stripped:
                # 其他内容，确保有正确的缩进
                if brace_level > 0:
                    fixed_lines.append('    ' + stripped)
                else:
                    fixed_lines.append('  ' + stripped)
                last_was_closing_brace = False
        else:
            # 数组外的内容保持原样
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 最后清理：确保没有连续的空逗号
    content = re.sub(r',\s*,+', ',', content)
    content = re.sub(r',\s*\n\s*,', ',\n', content)
    # 移除数组开始后的空逗号
    content = re.sub(r'\[\s*,+', '[\n', content)
    # 移除数组结束前的空逗号
    content = re.sub(r',+\s*\]', '\n]', content)
    
    # 备份原文件
    backup_path = MAIN_GAMES_JS.with_suffix('.js.backup3')
    MAIN_GAMES_JS.rename(backup_path)
    print(f"已备份原文件到: {backup_path}")
    
    # 写入修复后的内容
    MAIN_GAMES_JS.write_text(content, encoding='utf-8')
    print(f"已修复并更新: {MAIN_GAMES_JS}")
    
    print("\n" + "=" * 70)
    print("修复完成！")
    print("=" * 70)
    print("✓ 已移除所有空逗号")
    print("✓ 已修复游戏对象格式")
    print("✓ 文件格式已规范化")
    
    return True

if __name__ == "__main__":
    import sys
    success = fix_games_js()
    sys.exit(0 if success else 1)
