#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复games.js - 移除所有空逗号
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
MAIN_GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def quick_fix():
    print("读取文件...")
    content = MAIN_GAMES_JS.read_text(encoding='utf-8')
    
    print("移除空逗号...")
    # 移除所有单独的空逗号行
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        stripped = line.strip()
        # 跳过空逗号行
        if stripped == ',' or stripped == '':
            continue
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 移除连续的空逗号
    content = re.sub(r',\s*,+', ',', content)
    
    # 确保 } 后直接跟逗号（如果有下一个对象）
    content = re.sub(r'\}\s*\n\s*\{', '},\n  {', content)
    
    # 备份
    backup = MAIN_GAMES_JS.with_suffix('.js.backup_fix')
    MAIN_GAMES_JS.rename(backup)
    print(f"已备份到: {backup}")
    
    # 写入
    MAIN_GAMES_JS.write_text(content, encoding='utf-8')
    print("修复完成！")
    return True

if __name__ == "__main__":
    quick_fix()
