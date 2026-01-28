#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新游戏封面脚本
为所有本地游戏查找并设置封面图片
"""

import re
import shutil
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
GAMES_DIR = PROJECT_ROOT / "public" / "games"
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

# 可能的封面图片文件名（按优先级排序）
COVER_IMAGE_NAMES = [
    'icon.png',
    'thumb.png',
    'cover.png',
    'thumbnail.png',
    'photo.jpg',
    'thumb.jpg',
    'cover.jpg',
    'icon.jpg',
    'logo.png',
    'logo.jpg',
    'preview.png',
    'preview.jpg',
]

def find_cover_image(game_dir: Path) -> Optional[str]:
    """在游戏文件夹中查找封面图片"""
    # 按优先级查找
    for img_name in COVER_IMAGE_NAMES:
        img_path = game_dir / img_name
        if img_path.exists() and img_path.is_file():
            # 返回相对于public的路径
            relative_path = img_path.relative_to(PROJECT_ROOT / "public")
            return f"/{relative_path.as_posix()}"
    
    # 如果没有找到标准名称，查找所有图片文件（排除子文件夹）
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    for ext in image_extensions:
        # 只在游戏根目录查找，不在子文件夹中查找
        for img_file in game_dir.glob(f'*{ext}'):
            if img_file.is_file() and img_file.parent == game_dir:
                # 确保不在子文件夹中
                relative_path = img_file.relative_to(PROJECT_ROOT / "public")
                return f"/{relative_path.as_posix()}"
    
    return None

def update_game_covers():
    """更新所有本地游戏的封面"""
    print("=" * 70)
    print("更新游戏封面脚本")
    print("=" * 70)
    
    if not GAMES_JS.exists():
        print(f"错误: 找不到文件: {GAMES_JS}")
        return False
    
    print(f"\n读取文件: {GAMES_JS}")
    content = GAMES_JS.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # 查找所有本地游戏对象
    # 方法：找到所有包含 /games/ URL的游戏，然后在其对象内查找thumb字段
    
    updated_count = 0
    not_found_count = 0
    processed_games = set()
    games_to_update = []
    
    # 第一步：收集所有需要更新的游戏信息
    print("\n步骤1: 扫描所有本地游戏...")
    for i, line in enumerate(lines):
        # 查找包含 /games/ 的URL行
        url_match = re.search(r"url:\s*['\"]/games/([^/]+)/[^'\"]+['\"]", line)
        if url_match:
            game_name = url_match.group(1)
            
            # 避免重复处理
            if game_name in processed_games:
                continue
            processed_games.add(game_name)
            
            # 在URL行附近查找thumb字段（前后30行内）
            thumb_line_num = None
            search_start = max(0, i - 15)
            search_end = min(len(lines), i + 30)
            
            for j in range(search_start, search_end):
                if 'thumb:' in lines[j]:
                    thumb_line_num = j
                    break
            
            if thumb_line_num is not None:
                games_to_update.append({
                    'name': game_name,
                    'thumb_line': thumb_line_num,
                    'url_line': i
                })
    
    print(f"找到 {len(games_to_update)} 个需要更新的本地游戏")
    
    # 第二步：更新所有游戏的封面
    print("\n步骤2: 更新游戏封面...")
    for game_info in games_to_update:
        game_name = game_info['name']
        thumb_line_num = game_info['thumb_line']
        
        # 检查游戏文件夹
        game_dir = GAMES_DIR / game_name
        if not game_dir.exists():
            not_found_count += 1
            if not_found_count <= 5:
                print(f"警告: 游戏文件夹不存在: {game_name}")
            continue
        
        # 查找封面图片
        cover_path = find_cover_image(game_dir)
        
        if cover_path:
            # 更新thumb字段所在的行
            old_line = lines[thumb_line_num]
            # 替换thumb字段的值
            new_line = re.sub(
                r"thumb:\s*['\"]([^'\"]+)['\"]",
                f"thumb: '{cover_path}'",
                old_line
            )
            lines[thumb_line_num] = new_line
            updated_count += 1
            
            # 每50个显示一次进度
            if updated_count % 50 == 0:
                print(f"已更新 {updated_count} 个游戏...")
        else:
            not_found_count += 1
            # 只显示前10个未找到的
            if not_found_count <= 10:
                print(f"✗ {game_name}: 未找到封面图片")
    
    if not_found_count > 10:
        print(f"... 还有 {not_found_count - 10} 个游戏未找到封面")
    
    # 备份原文件
    backup_path = GAMES_JS.with_suffix('.js.backup_covers')
    shutil.copy2(GAMES_JS, backup_path)
    print(f"\n已备份原文件到: {backup_path}")
    
    # 写入更新后的内容
    new_content = '\n'.join(lines)
    GAMES_JS.write_text(new_content, encoding='utf-8')
    print(f"已更新: {GAMES_JS}")
    
    print("\n" + "=" * 70)
    print("更新完成！")
    print("=" * 70)
    print(f"✓ 成功更新 {updated_count} 个游戏的封面")
    print(f"✗ {not_found_count} 个游戏未找到封面（使用默认头像）")
    
    return True

if __name__ == "__main__":
    import sys
    success = update_game_covers()
    sys.exit(0 if success else 1)
