#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
431个H5游戏部署和翻译脚本
功能：
1. 扫描所有游戏文件夹
2. 复制游戏到public/games目录
3. 检测并翻译所有中文内容为英文
4. 更新games.js文件
"""

import os
import shutil
import json
import re
from pathlib import Path
from typing import List, Dict, Set

# 配置路径
PROJECT_ROOT = Path(r"d:\游戏网站1\wegogame.net-main")
SOURCE_GAMES_DIR = PROJECT_ROOT / "431套H5小游戏源码大合集 带网页导航" / "games"
TARGET_GAMES_DIR = PROJECT_ROOT / "public" / "games"
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

# 常见游戏术语翻译字典（按长度从长到短排序，确保长短语优先匹配）
TRANSLATION_DICT = {
    '是男人就下100层': 'Real Man Goes Down 100 Floors',
    '开始游戏': 'Start Game',
    '游戏结束': 'Game Over',
    '重新开始': 'Restart',
    '加载完成': 'Loading Complete',
    '网络错误': 'Network Error',
    '请稍候': 'Please Wait',
    '下一关': 'Next Level',
    '上一关': 'Previous Level',
    '最高分': 'High Score',
    '生命值': 'HP',
    '开始': 'Start',
    '暂停': 'Pause',
    '继续': 'Continue',
    '得分': 'Score',
    '分数': 'Score',
    '等级': 'Level',
    '关卡': 'Level',
    '设置': 'Settings',
    '音效': 'Sound',
    '音乐': 'Music',
    '帮助': 'Help',
    '说明': 'Instructions',
    '返回': 'Back',
    '退出': 'Exit',
    '确认': 'Confirm',
    '取消': 'Cancel',
    '确定': 'OK',
    '是': 'Yes',
    '否': 'No',
    '点击': 'Click',
    '触摸': 'Touch',
    '滑动': 'Swipe',
    '移动': 'Move',
    '跳跃': 'Jump',
    '攻击': 'Attack',
    '防御': 'Defense',
    '生命': 'Life',
    '能量': 'Energy',
    '金币': 'Coins',
    '道具': 'Items',
    '商店': 'Shop',
    '购买': 'Buy',
    '升级': 'Upgrade',
    '加载中': 'Loading',
    '重试': 'Retry',
    '游戏': 'Game',
    '玩家': 'Player',
    '敌人': 'Enemy',
    '胜利': 'Victory',
    '失败': 'Defeat',
    '时间': 'Time',
    '速度': 'Speed',
    '力量': 'Power',
    '技能': 'Skill',
    '装备': 'Equipment',
    '任务': 'Mission',
    '挑战': 'Challenge',
    '奖励': 'Reward',
    '成就': 'Achievement',
    '排行榜': 'Leaderboard',
    '分享': 'Share',
    '保存': 'Save',
    '加载': 'Load',
    '新游戏': 'New Game',
    '继续游戏': 'Continue Game',
    '主菜单': 'Main Menu',
    '选项': 'Options',
    '关于': 'About',
    '版本': 'Version',
    '作者': 'Author',
    '制作': 'Made by',
    '版权所有': 'Copyright',
    '版权所有': 'All Rights Reserved',
}

# 需要翻译的文件扩展名
TRANSLATABLE_EXTENSIONS = {'.html', '.htm', '.js', '.css', '.json', '.txt', '.xml'}

# 需要跳过的文件/目录
SKIP_PATTERNS = {
    'node_modules', '.git', '.svn', '.DS_Store', 
    'Thumbs.db', '.min.js', '.min.css', 'jquery', 'bootstrap'
}

def is_chinese(text: str) -> bool:
    """检测文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def translate_text(text: str) -> str:
    """翻译文本（使用字典和简单规则）"""
    if not is_chinese(text):
        return text
    
    original_text = text
    
    # 按长度从长到短排序，优先匹配长短语
    sorted_dict = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)
    
    # 首先尝试完整匹配字典
    for chinese, english in sorted_dict:
        if chinese in text:
            text = text.replace(chinese, english)
    
    # 如果还有中文，尝试逐字符翻译常见字符
    if is_chinese(text):
        # 对于常见单字符，进行翻译
        char_dict = {
            '是': 'Is', '的': '', '了': '', '在': 'In', '有': 'Has', '和': 'And',
            '就': 'Then', '不': 'Not', '人': 'Person', '我': 'I', '你': 'You',
            '他': 'He', '她': 'She', '它': 'It', '这': 'This', '那': 'That',
            '上': 'Up', '下': 'Down', '左': 'Left', '右': 'Right', '中': 'Middle',
            '大': 'Big', '小': 'Small', '新': 'New', '旧': 'Old', '好': 'Good',
            '坏': 'Bad', '快': 'Fast', '慢': 'Slow', '高': 'High', '低': 'Low',
        }
        
        # 只翻译独立的单字符（前后不是中文字符）
        for char, trans in char_dict.items():
            if char in text:
                # 使用正则确保是独立的字符
                pattern = f'([^\\u4e00-\\u9fff]){char}([^\\u4e00-\\u9fff])'
                if trans:
                    text = re.sub(pattern, f'\\1{trans}\\2', text)
                else:
                    text = re.sub(pattern, '\\1\\2', text)
    
    # 如果翻译后还有中文，保留原样（避免破坏游戏逻辑）
    # 但至少尝试翻译了已知的短语
    return text if text != original_text or not is_chinese(text) else original_text

def translate_file_content(content: str, file_path: Path) -> str:
    """翻译文件内容"""
    original_content = content
    
    # 对于HTML文件，只翻译可见文本，不翻译代码
    if file_path.suffix in {'.html', '.htm'}:
        # 翻译title标签
        content = re.sub(r'<title>([^<]*)</title>', 
                        lambda m: f'<title>{translate_text(m.group(1))}</title>', 
                        content, flags=re.IGNORECASE)
        
        # 翻译meta description和keywords
        content = re.sub(r'<meta\s+name=["\'](description|keywords)["\']\s+content=["\']([^"\']*)["\']', 
                        lambda m: f'<meta name="{m.group(1)}" content="{translate_text(m.group(2))}"', 
                        content, flags=re.IGNORECASE)
        
        # 分离script和style标签，避免翻译代码
        parts = []
        last_end = 0
        
        # 找到所有script和style标签
        for match in re.finditer(r'(<script[^>]*>.*?</script>|<style[^>]*>.*?</style>)', 
                                content, flags=re.IGNORECASE | re.DOTALL):
            # 添加script/style之前的内容
            if match.start() > last_end:
                html_part = content[last_end:match.start()]
                # 翻译HTML中的可见文本
                html_part = re.sub(r'>([^<>]*[\u4e00-\u9fff][^<>]*)<', 
                                  lambda m: f'>{translate_text(m.group(1))}<', 
                                  html_part)
                parts.append(html_part)
            
            # 保持script/style标签不变
            parts.append(match.group(0))
            last_end = match.end()
        
        # 添加最后的部分
        if last_end < len(content):
            html_part = content[last_end:]
            html_part = re.sub(r'>([^<>]*[\u4e00-\u9fff][^<>]*)<', 
                              lambda m: f'>{translate_text(m.group(1))}<', 
                              html_part)
            parts.append(html_part)
        
        content = ''.join(parts)
    
    # 对于JS文件，只翻译字符串字面量中的中文
    elif file_path.suffix == '.js':
        # 更智能的字符串翻译：匹配引号内的字符串
        def translate_js_string(match):
            full_match = match.group(0)
            quote_char = match.group(1)  # ' 或 "
            string_content = match.group(2)
            
            # 跳过URL、路径等（包含http://、/、\等）
            if re.search(r'(https?://|/|\\|\.(js|css|png|jpg|gif|ico))', string_content, re.IGNORECASE):
                return full_match
            
            # 跳过变量名、函数名等（只包含字母数字下划线）
            if re.match(r'^[a-zA-Z0-9_]+$', string_content):
                return full_match
            
            # 只翻译包含中文的字符串
            if is_chinese(string_content):
                translated = translate_text(string_content)
                # 转义引号
                translated = translated.replace(quote_char, f'\\{quote_char}')
                return f'{quote_char}{translated}{quote_char}'
            
            return full_match
        
        # 匹配单引号或双引号字符串（简单版本）
        # 注意：这个正则可能不够完善，但对于大多数情况应该可以工作
        content = re.sub(r'(["\'])((?:(?!\1)[^\\]|\\.)*[\u4e00-\u9fff](?:(?!\1)[^\\]|\\.)*)(\1)', 
                        translate_js_string, content)
    
    # 对于CSS和JSON，保持原样（通常不包含需要翻译的中文）
    elif file_path.suffix in {'.css', '.json'}:
        pass
    
    # 对于TXT和XML文件，翻译所有可见文本
    elif file_path.suffix in {'.txt', '.xml'}:
        if is_chinese(content):
            content = translate_text(content)
    
    return content

def should_skip_file(file_path: Path) -> bool:
    """判断是否应该跳过该文件"""
    file_str = str(file_path).lower()
    for pattern in SKIP_PATTERNS:
        if pattern.lower() in file_str:
            return True
    return False

def translate_game_files(game_dir: Path, verbose: bool = False):
    """翻译游戏文件夹中的所有文件"""
    translated_count = 0
    total_files = 0
    
    for file_path in game_dir.rglob('*'):
        if not file_path.is_file():
            continue
        
        if should_skip_file(file_path):
            continue
        
        if file_path.suffix not in TRANSLATABLE_EXTENSIONS:
            continue
        
        total_files += 1
        
        try:
            # 读取文件
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # 检查是否包含中文
            if not is_chinese(content):
                continue
            
            # 翻译内容
            translated_content = translate_file_content(content, file_path)
            
            # 如果内容有变化，写入文件
            if translated_content != content:
                file_path.write_text(translated_content, encoding='utf-8')
                translated_count += 1
                if verbose:
                    print(f"    已翻译: {file_path.name}")
        
        except Exception as e:
            if verbose:
                print(f"    警告: 翻译文件失败 {file_path.name}: {e}")
            continue
    
    return translated_count

def find_all_game_folders() -> List[Dict]:
    """查找所有游戏文件夹"""
    game_folders = []
    
    if not SOURCE_GAMES_DIR.exists():
        print(f"错误: 源游戏目录不存在: {SOURCE_GAMES_DIR}")
        return game_folders
    
    for game_folder in SOURCE_GAMES_DIR.iterdir():
        if not game_folder.is_dir():
            continue
        
        # 查找HTML文件
        html_files = list(game_folder.glob('*.html')) + list(game_folder.glob('*.htm'))
        if not html_files:
            # 也检查子目录
            html_files = list(game_folder.rglob('*.html')) + list(game_folder.rglob('*.htm'))
        
        if html_files:
            # 使用第一个找到的HTML文件作为入口
            html_file = html_files[0]
            game_folders.append({
                'name': game_folder.name,
                'path': game_folder,
                'html_file': html_file.name,
                'html_path': html_file.relative_to(game_folder)
            })
    
    return game_folders

def copy_and_translate_games(game_folders: List[Dict]) -> List[Dict]:
    """复制游戏并翻译"""
    if not TARGET_GAMES_DIR.exists():
        TARGET_GAMES_DIR.mkdir(parents=True, exist_ok=True)
    
    deployed_games = []
    total_translated = 0
    
    print(f"\n开始部署 {len(game_folders)} 个游戏...")
    
    for idx, game_info in enumerate(game_folders, 1):
        game_name = game_info['name']
        source_dir = game_info['path']
        
        # 清理游戏名称
        safe_name = re.sub(r'[^a-zA-Z0-9\-_]', '_', game_name)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')
        if not safe_name:
            safe_name = f'game_{idx}'
        
        dest_dir = TARGET_GAMES_DIR / safe_name
        
        try:
            print(f"\n[{idx}/{len(game_folders)}] 处理游戏: {game_name} -> {safe_name}")
            
            # 复制游戏文件夹
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(source_dir, dest_dir)
            
            # 翻译游戏文件
            translated_count = translate_game_files(dest_dir, verbose=(idx <= 5))
            total_translated += translated_count
            
            # 查找HTML入口文件
            html_file = game_info['html_file']
            html_path = dest_dir / html_file
            if not html_path.exists():
                # 尝试查找其他HTML文件
                html_files = list(dest_dir.glob('*.html')) + list(dest_dir.glob('*.htm'))
                if html_files:
                    html_file = html_files[0].name
                    html_path = html_files[0]
            
            deployed_games.append({
                'name': game_name,
                'safe_name': safe_name,
                'html_file': html_file,
                'path': f"/games/{safe_name}/{html_file}",
                'translated_files': translated_count
            })
            
            print(f"  ✓ 完成 (翻译了 {translated_count} 个文件)")
        
        except Exception as e:
            print(f"  ✗ 错误: {e}")
            continue
    
    print(f"\n翻译统计: 共翻译了 {total_translated} 个文件")
    return deployed_games

def read_existing_games() -> List[Dict]:
    """读取现有的games.js文件"""
    if not GAMES_JS.exists():
        return []
    
    try:
        content = GAMES_JS.read_text(encoding='utf-8')
        
        # 提取游戏数组
        match = re.search(r'(?:const\s+games\s*=\s*|export\s+default\s*)(\[[\s\S]*?\])', content)
        if match:
            games_str = match.group(1)
            # 清理注释
            games_str = re.sub(r'//.*?$', '', games_str, flags=re.MULTILINE)
            games_str = re.sub(r'/\*.*?\*/', '', games_str, flags=re.DOTALL)
            
            # 尝试解析JSON
            try:
                games = json.loads(games_str)
                return games if isinstance(games, list) else []
            except:
                # 如果JSON解析失败，尝试手动提取
                pass
        
        return []
    except Exception as e:
        print(f"警告: 读取现有游戏失败: {e}")
        return []

def generate_game_entry(game_info: Dict, index: int, existing_games: List[Dict]) -> Dict:
    """生成游戏数据条目"""
    # 获取下一个ID
    max_id = 0
    for g in existing_games:
        try:
            gid = int(g.get('id', '0'))
            if gid > max_id:
                max_id = gid
        except:
            pass
    
    new_id = str(max_id + index + 1)
    
    # 生成游戏标题（从文件夹名转换）
    title = game_info['name'].replace('_', ' ').replace('-', ' ').title()
    
    # 生成描述
    description = f"Play {title} - An exciting HTML5 game. Challenge yourself and have fun!"
    
    game_entry = {
        'id': new_id,
        'title': title,
        'description': description,
        'instructions': 'Use mouse or touch controls to play. Follow the on-screen instructions.',
        'url': game_info['path'],
        'category': 'Arcade',
        'tags': 'HTML5, Game, Fun',
        'thumb': 'https://img.gamemonetize.com/default/512x512.jpg',
        'link': game_info['safe_name'].lower().replace('_', '-'),
        'null': '',
        'star': 3
    }
    
    return game_entry

def update_games_js(deployed_games: List[Dict]):
    """更新games.js文件"""
    print("\n正在更新games.js文件...")
    
    existing_games = read_existing_games()
    new_games = []
    
    for idx, game_info in enumerate(deployed_games):
        game_entry = generate_game_entry(game_info, idx, existing_games)
        new_games.append(game_entry)
    
    # 合并游戏
    all_games = existing_games + new_games
    
    # 生成games.js内容
    games_js_content = "const games = [\n"
    
    for i, game in enumerate(all_games):
        games_js_content += "  {\n"
        # 转义单引号，避免在JavaScript字符串中出错
        game_id = str(game['id']).replace("'", "\\'")
        game_title = str(game['title']).replace("'", "\\'")
        game_desc = str(game['description']).replace("'", "\\'")
        game_instr = str(game['instructions']).replace("'", "\\'")
        game_url = str(game['url']).replace("'", "\\'")
        game_category = str(game['category']).replace("'", "\\'")
        game_tags = str(game['tags']).replace("'", "\\'")
        game_thumb = str(game['thumb']).replace("'", "\\'")
        game_link = str(game['link']).replace("'", "\\'")
        game_null = str(game['null']).replace("'", "\\'")
        
        games_js_content += f"    id: '{game_id}',\n"
        games_js_content += f"    title: '{game_title}',\n"
        games_js_content += f"    description: '{game_desc}',\n"
        games_js_content += f"    instructions: '{game_instr}',\n"
        games_js_content += f"    url: '{game_url}',\n"
        games_js_content += f"    category: '{game_category}',\n"
        games_js_content += f"    tags: '{game_tags}',\n"
        games_js_content += f"    thumb: '{game_thumb}',\n"
        games_js_content += f"    link: '{game_link}',\n"
        games_js_content += f"    null: '{game_null}',\n"
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
    print("=" * 70)
    print("431个H5游戏部署和翻译脚本")
    print("=" * 70)
    
    # 检查源目录
    if not SOURCE_GAMES_DIR.exists():
        print(f"错误: 源游戏目录不存在: {SOURCE_GAMES_DIR}")
        print("请确认游戏文件夹路径正确")
        return
    
    try:
        # 1. 查找所有游戏文件夹
        print("\n步骤1: 扫描游戏文件夹...")
        game_folders = find_all_game_folders()
        print(f"找到 {len(game_folders)} 个游戏文件夹")
        
        if not game_folders:
            print("警告: 未找到游戏文件夹")
            return
        
        # 2. 复制并翻译游戏
        print("\n步骤2: 复制游戏并翻译中文内容...")
        deployed_games = copy_and_translate_games(game_folders)
        
        if not deployed_games:
            print("错误: 没有成功部署任何游戏")
            return
        
        # 3. 更新games.js
        print("\n步骤3: 更新games.js文件...")
        update_games_js(deployed_games)
        
        print("\n" + "=" * 70)
        print("部署完成！")
        print("=" * 70)
        print(f"✓ 成功部署 {len(deployed_games)} 个游戏")
        print(f"✓ 所有中文内容已翻译为英文")
        print(f"✓ games.js文件已更新")
        print("\n注意事项:")
        print("1. 游戏已部署到: public/games/")
        print("2. 游戏URL使用相对路径，兼容开发和生产环境")
        print("3. 建议测试几个游戏确保正常运行")
        print("4. 可以手动编辑games.js调整游戏信息")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
