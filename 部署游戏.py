#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏部署脚本
用于解压zip文件并将游戏部署到网站中
"""

import os
import zipfile
import json
import shutil
from pathlib import Path
import re

# 配置路径
ZIP_FILE = r"d:\Backup\xwechat_files\wxid_jicv7dwfa17f22_36ee\msg\file\2026-01\xixi-games.zip"
PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
GAMES_DIR = PROJECT_ROOT / "public" / "games"
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

def extract_zip():
    """解压zip文件"""
    print(f"正在解压: {ZIP_FILE}")
    temp_dir = PROJECT_ROOT / "temp_xixi_games"
    
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    print(f"解压完成，文件位于: {temp_dir}")
    return temp_dir

def find_game_folders(temp_dir):
    """查找所有游戏文件夹"""
    game_folders = []
    
    for root, dirs, files in os.walk(temp_dir):
        # 查找包含index.html或game.html的文件夹
        if 'index.html' in files or 'game.html' in files or any(f.endswith('.html') for f in files):
            # 检查是否是游戏文件夹（包含html文件）
            html_files = [f for f in files if f.endswith('.html')]
            if html_files:
                game_folders.append({
                    'path': Path(root),
                    'html_file': html_files[0],
                    'name': Path(root).name
                })
    
    # 如果没有找到，尝试查找所有包含html文件的目录
    if not game_folders:
        for root, dirs, files in os.walk(temp_dir):
            html_files = [f for f in files if f.endswith('.html')]
            if html_files:
                game_folders.append({
                    'path': Path(root),
                    'html_file': html_files[0],
                    'name': Path(root).name
                })
    
    return game_folders

def copy_games_to_public(game_folders):
    """将游戏复制到public/games目录"""
    if GAMES_DIR.exists():
        shutil.rmtree(GAMES_DIR)
    GAMES_DIR.mkdir(parents=True, exist_ok=True)
    
    deployed_games = []
    
    for game in game_folders:
        game_name = game['name']
        # 清理游戏名称，只保留字母数字和连字符
        safe_name = re.sub(r'[^a-zA-Z0-9\-_]', '_', game_name)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')
        
        dest_dir = GAMES_DIR / safe_name
        
        # 复制整个游戏文件夹
        if game['path'].is_dir():
            shutil.copytree(game['path'], dest_dir, dirs_exist_ok=True)
            print(f"已复制游戏: {game_name} -> {safe_name}")
            
            # 查找主HTML文件
            html_file = game['html_file']
            if not (dest_dir / html_file).exists():
                # 尝试查找其他html文件
                html_files = list(dest_dir.glob('*.html'))
                if html_files:
                    html_file = html_files[0].name
            
            deployed_games.append({
                'name': game_name,
                'safe_name': safe_name,
                'html_file': html_file,
                'path': f"/games/{safe_name}/{html_file}"
            })
    
    return deployed_games

def read_existing_games():
    """读取现有的games.js文件"""
    if not GAMES_JS.exists():
        return []
    
    content = GAMES_JS.read_text(encoding='utf-8')
    
    # 提取游戏数组
    # 查找 const games = [...] 或 export default [...]
    match = re.search(r'(?:const\s+games\s*=\s*|export\s+default\s*)(\[[\s\S]*?\])', content)
    if match:
        games_str = match.group(1)
        # 简单的JSON解析（可能需要处理注释）
        games_str = re.sub(r'//.*?$', '', games_str, flags=re.MULTILINE)
        games_str = re.sub(r'/\*.*?\*/', '', games_str, flags=re.DOTALL)
        try:
            games = json.loads(games_str)
            return games
        except:
            pass
    
    return []

def generate_game_entry(game_info, index):
    """生成游戏数据条目"""
    # 获取下一个ID（基于现有游戏的最大ID）
    existing_games = read_existing_games()
    max_id = 0
    for g in existing_games:
        try:
            gid = int(g.get('id', '0'))
            if gid > max_id:
                max_id = gid
        except:
            pass
    
    new_id = str(max_id + index + 1)
    
    # 使用相对路径，兼容开发和生产环境
    game_url = game_info['path']
    
    # 生成游戏数据
    game_entry = {
        'id': new_id,
        'title': game_info['name'].replace('_', ' ').replace('-', ' ').title(),
        'description': f"Play {game_info['name']} - A fun HTML5 game. Enjoy this exciting game and challenge yourself!",
        'instructions': 'Use mouse or touch to play. Follow the on-screen instructions.',
        'url': game_url,  # 使用相对路径
        'category': 'Arcade',
        'tags': 'HTML5, Game, Fun',
        'thumb': 'https://img.gamemonetize.com/default/512x512.jpg',  # 默认缩略图，后续可替换
        'link': game_info['safe_name'].lower().replace('_', '-'),
        'null': '',
        'star': 3
    }
    
    return game_entry

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

def update_games_js(deployed_games):
    """更新games.js文件"""
    existing_games = read_existing_games()
    new_games = []
    
    for idx, game_info in enumerate(deployed_games):
        game_entry = generate_game_entry(game_info, idx)
        new_games.append(game_entry)
    
    # 合并现有游戏和新游戏
    all_games = existing_games + new_games
    
    # 生成新的games.js内容
    games_js_content = "const games = [\n"
    
    for i, game in enumerate(all_games):
        games_js_content += "  {\n"
        games_js_content += f"    id: '{escape_js_string(game['id'])}',\n"
        games_js_content += f"    title: '{escape_js_string(game['title'])}',\n"
        
        # 处理多行description
        desc = escape_js_string(game['description'])
        if len(desc) > 100:
            games_js_content += f"    description: '{desc}',\n"
        else:
            games_js_content += f"    description: '{desc}',\n"
        
        games_js_content += f"    instructions: '{escape_js_string(game['instructions'])}',\n"
        games_js_content += f"    url: '{escape_js_string(game['url'])}',\n"
        games_js_content += f"    category: '{escape_js_string(game['category'])}',\n"
        games_js_content += f"    tags: '{escape_js_string(game['tags'])}',\n"
        games_js_content += f"    thumb: '{escape_js_string(game['thumb'])}',\n"
        games_js_content += f"    link: '{escape_js_string(game['link'])}',\n"
        games_js_content += f"    null: '{escape_js_string(game['null'])}',\n"
        games_js_content += f"    star: {game['star']}\n"
        games_js_content += "  }"
        if i < len(all_games) - 1:
            games_js_content += ","
        games_js_content += "\n"
    
    games_js_content += "]\n\n"
    games_js_content += "export default games\n"
    
    # 备份原文件
    if GAMES_JS.exists():
        backup_path = GAMES_JS.with_suffix('.js.backup')
        shutil.copy2(GAMES_JS, backup_path)
        print(f"已备份原文件到: {backup_path}")
    
    # 写入新文件
    GAMES_JS.write_text(games_js_content, encoding='utf-8')
    print(f"已更新: {GAMES_JS}")
    print(f"新增 {len(new_games)} 个游戏")
    print(f"总计 {len(all_games)} 个游戏")

def main():
    print("=" * 60)
    print("游戏部署脚本")
    print("=" * 60)
    
    # 检查zip文件是否存在
    if not os.path.exists(ZIP_FILE):
        print(f"错误: 找不到zip文件: {ZIP_FILE}")
        return
    
    try:
        # 1. 解压zip文件
        temp_dir = extract_zip()
        
        # 2. 查找游戏文件夹
        print("\n正在查找游戏...")
        game_folders = find_game_folders(temp_dir)
        print(f"找到 {len(game_folders)} 个游戏")
        
        if not game_folders:
            print("警告: 未找到游戏文件，请检查zip文件内容")
            return
        
        # 3. 复制游戏到public/games
        print("\n正在复制游戏到public/games...")
        deployed_games = copy_games_to_public(game_folders)
        
        # 4. 更新games.js
        print("\n正在更新games.js...")
        update_games_js(deployed_games)
        
        # 5. 清理临时文件
        print("\n正在清理临时文件...")
        shutil.rmtree(temp_dir)
        
        print("\n" + "=" * 60)
        print("部署完成！")
        print("=" * 60)
        print(f"已部署 {len(deployed_games)} 个游戏")
        print("\n注意事项:")
        print("1. 游戏URL使用localhost:5173（开发环境）")
        print("2. 生产环境需要修改URL为实际域名")
        print("3. 建议为每个游戏添加合适的缩略图")
        print("4. 可以手动编辑games.js调整游戏信息")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
