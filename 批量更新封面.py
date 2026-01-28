#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新游戏封面 - 直接替换所有本地游戏的默认头像
"""

import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
GAMES_DIR = PROJECT_ROOT / "public" / "games"
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

COVER_IMAGE_NAMES = [
    'icon.png', 'thumb.png', 'cover.png', 'thumbnail.png',
    'photo.jpg', 'thumb.jpg', 'cover.jpg', 'icon.jpg',
    'logo.png', 'logo.jpg', 'preview.png', 'preview.jpg',
]

def find_cover_image(game_dir: Path):
    """查找封面图片"""
    for img_name in COVER_IMAGE_NAMES:
        img_path = game_dir / img_name
        if img_path.exists() and img_path.is_file():
            relative_path = img_path.relative_to(PROJECT_ROOT / "public")
            return f"/{relative_path.as_posix()}"
    
    # 查找根目录下的图片文件
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        for img_file in game_dir.glob(f'*{ext}'):
            if img_file.is_file() and img_file.parent == game_dir:
                relative_path = img_file.relative_to(PROJECT_ROOT / "public")
                return f"/{relative_path.as_posix()}"
    
    return None

def update_all_covers():
    print("=" * 70)
    print("批量更新游戏封面")
    print("=" * 70)
    
    content = GAMES_JS.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # 收集所有需要更新的游戏
    games_to_update = []
    
    print("\n步骤1: 扫描所有本地游戏...")
    for i, line in enumerate(lines):
        # 查找本地游戏URL
        url_match = re.search(r"url:\s*['\"]/games/([^/]+)/[^'\"]+['\"]", line)
        if url_match:
            game_name = url_match.group(1)
            
            # 在附近查找thumb字段（前后20行）
            for j in range(max(0, i-10), min(len(lines), i+20)):
                if 'thumb:' in lines[j] and 'default/512x512.jpg' in lines[j]:
                    games_to_update.append({
                        'name': game_name,
                        'thumb_line': j
                    })
                    break
    
    print(f"找到 {len(games_to_update)} 个需要更新的本地游戏")
    
    updated_count = 0
    not_found_count = 0
    
    print("\n步骤2: 更新游戏封面...")
    # 从后往前更新
    for game_info in reversed(games_to_update):
        game_name = game_info['name']
        thumb_line = game_info['thumb_line']
        
        game_dir = GAMES_DIR / game_name
        if not game_dir.exists():
            not_found_count += 1
            continue
        
        cover_path = find_cover_image(game_dir)
        
        if cover_path:
            # 替换thumb字段
            old_line = lines[thumb_line]
            new_line = re.sub(
                r"thumb:\s*['\"]https://img\.gamemonetize\.com/default/512x512\.jpg['\"]",
                f"thumb: '{cover_path}'",
                old_line
            )
            lines[thumb_line] = new_line
            updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"已更新 {updated_count} 个游戏...")
        else:
            not_found_count += 1
    
    # 备份
    backup = GAMES_JS.with_suffix('.js.backup_covers2')
    shutil.copy2(GAMES_JS, backup)
    print(f"\n已备份到: {backup}")
    
    # 写入
    new_content = '\n'.join(lines)
    GAMES_JS.write_text(new_content, encoding='utf-8')
    print(f"已更新: {GAMES_JS}")
    
    print("\n" + "=" * 70)
    print("更新完成！")
    print("=" * 70)
    print(f"✓ 成功更新 {updated_count} 个游戏的封面")
    print(f"✗ {not_found_count} 个游戏未找到封面")
    
    return True

if __name__ == "__main__":
    import sys
    success = update_all_covers()
    sys.exit(0 if success else 1)
