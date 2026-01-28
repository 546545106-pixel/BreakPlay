#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量替换游戏信息脚本
根据图片说明，替换431个游戏中的以下内容：
1. 游戏网站名称："空中传媒" -> 用户自定义
2. 游戏访问地址："game.ikongzhong.cn" -> 用户自定义（不带http://）
3. 微信关注链接：原始链接 -> 用户自定义
4. 微信号："mkongzhong" -> 用户自定义
5. 微信头像图片：替换 index/img/weixin.jpg（如果存在）
"""

import re
import shutil
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
GAMES_DIR = PROJECT_ROOT / "public" / "games"

# 需要替换的内容配置
REPLACEMENTS = {
    # 1. 游戏网站名称
    'site_name_old': '空中传媒',
    'site_name_new': '',  # 用户需要填写
    
    # 2. 游戏访问地址（不带http://）
    'domain_old': 'game.ikongzhong.cn',
    'domain_new': '',  # 用户需要填写
    
    # 3. 微信关注链接（可能有多种变体）
    'wechat_link_patterns': [
        'http://mp.weixin.qq.com/s?__biz=MzI4MjA2MjE0MQ==&mid=246005295&idx=1&sn=490f8141976d607ba079d48f52a3fcd7#rd',
        'http://mp.weixin.qq.com/s?_biz=MzI4MjA2MjE0MQ==&mid=246005295&idx=1&sn=490f8141976d607ba079d48f52a3fcd7#rd',
    ],
    'wechat_link_new': '',  # 用户需要填写
    
    # 4. 微信号
    'wechat_id_old': 'mkongzhong',
    'wechat_id_new': '',  # 用户需要填写
    
    # 5. 微信头像图片路径（如果用户提供）
    'weixin_image_path': None,  # 用户自己的微信头像图片路径
}

# 需要处理的文件类型
TEXT_FILE_EXTENSIONS = ['.html', '.htm', '.js', '.css', '.json', '.txt', '.xml']

def get_user_input():
    """获取用户输入"""
    print("=" * 70)
    print("批量替换游戏信息")
    print("=" * 70)
    print("\n请按照图片说明填写以下信息：\n")
    
    # 1. 游戏网站名称
    site_name = input("1. 游戏网站名称（替换'空中传媒'）: ").strip()
    if site_name:
        REPLACEMENTS['site_name_new'] = site_name
    
    # 2. 游戏访问地址
    domain = input("2. 游戏访问地址（替换'game.ikongzhong.cn'，不要带http://）: ").strip()
    if domain:
        # 移除可能的http://或https://前缀
        domain = re.sub(r'^https?://', '', domain)
        REPLACEMENTS['domain_new'] = domain
    
    # 3. 微信关注链接
    wechat_link = input("3. 微信关注链接（替换原始微信链接）: ").strip()
    if wechat_link:
        REPLACEMENTS['wechat_link_new'] = wechat_link
    
    # 4. 微信号
    wechat_id = input("4. 微信号（替换'mkongzhong'）: ").strip()
    if wechat_id:
        REPLACEMENTS['wechat_id_new'] = wechat_id
    
    # 5. 微信头像图片
    weixin_image = input("5. 微信头像图片路径（可选，留空跳过）: ").strip()
    if weixin_image:
        weixin_path = Path(weixin_image)
        if weixin_path.exists() and weixin_path.is_file():
            REPLACEMENTS['weixin_image_path'] = weixin_path
        else:
            print(f"警告: 图片文件不存在: {weixin_image}")
    
    print("\n" + "=" * 70)
    print("替换配置：")
    print("=" * 70)
    if REPLACEMENTS['site_name_new']:
        print(f"网站名称: '{REPLACEMENTS['site_name_old']}' -> '{REPLACEMENTS['site_name_new']}'")
    if REPLACEMENTS['domain_new']:
        print(f"访问地址: '{REPLACEMENTS['domain_old']}' -> '{REPLACEMENTS['domain_new']}'")
    if REPLACEMENTS['wechat_link_new']:
        print(f"微信链接: [原始链接（多种变体）] -> '{REPLACEMENTS['wechat_link_new']}'")
    if REPLACEMENTS['wechat_id_new']:
        print(f"微信号: '{REPLACEMENTS['wechat_id_old']}' -> '{REPLACEMENTS['wechat_id_new']}'")
    if REPLACEMENTS['weixin_image_path']:
        print(f"微信头像: 将替换所有 index/img/weixin.jpg")
    print("=" * 70)
    
    confirm = input("\n确认开始替换？(y/n): ").strip().lower()
    return confirm == 'y'

def replace_in_file(file_path: Path) -> Tuple[int, int]:
    """在文件中执行所有替换，返回(替换次数, 匹配的文件数)"""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        original_content = content
        replacements_count = 0
        
        # 1. 替换网站名称
        if REPLACEMENTS['site_name_new']:
            count = content.count(REPLACEMENTS['site_name_old'])
            if count > 0:
                content = content.replace(REPLACEMENTS['site_name_old'], REPLACEMENTS['site_name_new'])
                replacements_count += count
        
        # 2. 替换域名（多种形式）
        if REPLACEMENTS['domain_new']:
            # 替换 http://game.ikongzhong.cn
            pattern1 = r'http://' + re.escape(REPLACEMENTS['domain_old'])
            count1 = len(re.findall(pattern1, content))
            if count1 > 0:
                content = re.sub(pattern1, f"http://{REPLACEMENTS['domain_new']}", content)
                replacements_count += count1
            
            # 替换 https://game.ikongzhong.cn
            pattern2 = r'https://' + re.escape(REPLACEMENTS['domain_old'])
            count2 = len(re.findall(pattern2, content))
            if count2 > 0:
                content = re.sub(pattern2, f"https://{REPLACEMENTS['domain_new']}", content)
                replacements_count += count2
            
            # 替换不带协议的域名（在变量、字符串等中）
            pattern3 = r'\b' + re.escape(REPLACEMENTS['domain_old']) + r'\b'
            count3 = len(re.findall(pattern3, content))
            if count3 > 0:
                content = re.sub(pattern3, REPLACEMENTS['domain_new'], content)
                replacements_count += count3
        
        # 3. 替换微信关注链接（处理多种变体）
        if REPLACEMENTS['wechat_link_new']:
            for old_link in REPLACEMENTS['wechat_link_patterns']:
                if old_link in content:
                    count = content.count(old_link)
                    content = content.replace(old_link, REPLACEMENTS['wechat_link_new'])
                    replacements_count += count
        
        # 4. 替换微信号
        if REPLACEMENTS['wechat_id_new']:
            # 使用单词边界，避免误替换
            pattern = r'\b' + re.escape(REPLACEMENTS['wechat_id_old']) + r'\b'
            count = len(re.findall(pattern, content))
            if count > 0:
                content = re.sub(pattern, REPLACEMENTS['wechat_id_new'], content)
                replacements_count += count
        
        # 如果有替换，写入文件
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return replacements_count, 1
        
        return 0, 0
    
    except Exception as e:
        print(f"错误处理文件 {file_path}: {e}")
        return 0, 0

def replace_weixin_image(game_dir: Path) -> bool:
    """替换微信头像图片"""
    if not REPLACEMENTS['weixin_image_path']:
        return False
    
    # 查找可能的weixin.jpg位置
    possible_paths = [
        game_dir / 'index' / 'img' / 'weixin.jpg',
        game_dir / 'img' / 'weixin.jpg',
        game_dir / 'images' / 'weixin.jpg',
        game_dir / 'res' / 'weixin.jpg',
        game_dir / 'resources' / 'weixin.jpg',
    ]
    
    for target_path in possible_paths:
        if target_path.exists():
            try:
                # 备份原文件
                backup_path = target_path.with_suffix('.jpg.backup')
                shutil.copy2(target_path, backup_path)
                
                # 复制新文件
                shutil.copy2(REPLACEMENTS['weixin_image_path'], target_path)
                return True
            except Exception as e:
                print(f"警告: 无法替换 {target_path}: {e}")
    
    return False

def process_all_games():
    """处理所有游戏"""
    if not GAMES_DIR.exists():
        print(f"错误: 游戏目录不存在: {GAMES_DIR}")
        return False
    
    print("\n开始处理所有游戏...")
    print("=" * 70)
    
    total_replacements = 0
    total_files_modified = 0
    total_images_replaced = 0
    games_processed = 0
    
    # 遍历所有游戏文件夹
    for game_dir in sorted(GAMES_DIR.iterdir()):
        if not game_dir.is_dir():
            continue
        
        games_processed += 1
        game_replacements = 0
        game_files_modified = 0
        
        # 处理文本文件
        for ext in TEXT_FILE_EXTENSIONS:
            for file_path in game_dir.rglob(f'*{ext}'):
                if file_path.is_file():
                    replacements, files_modified = replace_in_file(file_path)
                    game_replacements += replacements
                    game_files_modified += files_modified
        
        # 替换微信头像图片
        if replace_weixin_image(game_dir):
            total_images_replaced += 1
        
        if game_replacements > 0:
            total_replacements += game_replacements
            total_files_modified += game_files_modified
            if games_processed % 50 == 0:
                print(f"已处理 {games_processed} 个游戏...")
    
    print("\n" + "=" * 70)
    print("处理完成！")
    print("=" * 70)
    print(f"✓ 处理了 {games_processed} 个游戏")
    print(f"✓ 修改了 {total_files_modified} 个文件")
    print(f"✓ 执行了 {total_replacements} 次文本替换")
    print(f"✓ 替换了 {total_images_replaced} 个微信头像图片")
    print("=" * 70)
    
    return True

def main():
    """主函数"""
    if not get_user_input():
        print("已取消操作")
        return
    
    process_all_games()

if __name__ == "__main__":
    main()
