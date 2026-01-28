#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
60 款 H5 小游戏部署脚本（Html5小游戏JavaScript源码/60套H5小游戏源码大合集）

功能：
1. 解压 60 个 .rar 到临时目录（需 7-Zip，或使用已解压目录）
2. 清空 public/games/，只保留这 60 款游戏，部署为 game_01 ~ game_60
3. 移除游戏内第三方广告，注入本站 GameAdAPI（对接你的 AdSense）
4. 使用 1-60套预览图 作为缩略图
5. 重写 src/data/games.js，仅包含这 60 款游戏
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 路径（请按你本机修改项目根目录）
PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_RAR_DIR = PROJECT_ROOT / "Html5小游戏JavaScript源码" / "60套H5小游戏源码大合集"
PREVIEW_DIR = PROJECT_ROOT / "Html5小游戏JavaScript源码" / "1-60套预览图"
EXTRACT_DIR = PROJECT_ROOT / "_60games_extracted"
TARGET_GAMES_DIR = PROJECT_ROOT / "public" / "games"
GAMES_JS = PROJECT_ROOT / "src" / "data" / "games.js"

# 60 款游戏中文名 -> 英文标题（用于列表）
GAME_NAMES = [
    ("僵尸鸭猎手", "Zombie Duck Hunter"),
    ("斯瓦特大战僵尸", "Swat vs Zombies"),
    ("坦克大战", "Tank Battle"),
    ("木乃伊糖果", "Mummy Candy"),
    ("万圣节记忆", "Halloween Memory"),
    ("毁灭僵尸", "Destroy Zombies"),
    ("粘猴手机游戏", "Sticky Monkey"),
    ("水暖工", "Plumber"),
    ("黄金矿工", "Gold Miner"),
    ("逃亡", "Escape"),
    ("水果馅饼", "Fruit Pie"),
    ("砌砖", "Brick Stack"),
    ("流浪者大战僵尸", "Wanderer vs Zombies"),
    ("万圣节泡泡枪手", "Halloween Bubble Shooter"),
    ("忍者冒险小游戏", "Ninja Adventure"),
    ("赌场卡记忆", "Casino Card Memory"),
    ("吃水果的蛇", "Fruit Snake"),
    ("坦克防御兵", "Tank Defense"),
    ("捕鱼狂", "Fish Frenzy"),
    ("疯狂跑步者", "Crazy Runner"),
    ("航天飞机", "Space Shuttle"),
    ("超级牛仔跑", "Super Cowboy Run"),
    ("猎鸭者", "Duck Hunter"),
    ("交通赛车", "Traffic Racing"),
    ("女孩打扮", "Girl Dress Up"),
    ("烛光超线", "Candle Overline"),
    ("果冻3", "Jelly 3"),
    ("射击强盗", "Shoot Robbers"),
    ("僵尸枪手", "Zombie Shooter"),
    ("圣诞熊猫跑步", "Christmas Panda Run"),
    ("速度赛车", "Speed Racing"),
    ("圣诞比赛", "Christmas Race"),
    ("圣诞气球", "Christmas Balloon"),
    ("儿童真彩色", "Kids True Color"),
    ("空战", "Air Combat"),
    ("狂鲨任务", "Shark Mission"),
    ("棍兵", "Stick Soldier"),
    ("泡泡教授", "Bubble Professor"),
    ("忍者游戏", "Ninja Game"),
    ("糖果比赛3", "Candy Match 3"),
    ("超彩色线", "Ultra Color Line"),
    ("触球", "Touch Ball"),
    ("快骰子", "Fast Dice"),
    ("气球天堂", "Balloon Paradise"),
    ("热珠宝", "Hot Jewel"),
    ("笑脸微笑小游戏", "Smiley Face"),
    ("儿童数学游戏", "Kids Math"),
    ("僵尸起义", "Zombie Uprising"),
    ("超级目标", "Super Target"),
    ("超级跑车拼图", "Super Car Puzzle"),
    ("儿童纵横填字游戏", "Kids Crossword"),
    ("希塔洛契卡", "Hit the Card"),
    ("汽车物理学", "Car Physics"),
    ("机器人X", "Robot X"),
    ("记忆游戏", "Memory Game"),
    ("卡通糖果-MatCH3", "Cartoon Candy Match3"),
    ("弹力球", "Bouncy Ball"),
    ("跳动弹跳", "Bounce Jump"),
    ("鱼类世界-MatCH3", "Fish World Match3"),
    ("复活节记忆", "Easter Memory"),
]

AD_KEYWORDS = [
    "adsbygoogle", "pagead2.googlesyndication.com", "doubleclick.net",
    "cpro.baidu.com", "hm.baidu.com", "cnzz.com",
]


def find_7z() -> Optional[Path]:
    for p in [
        Path(r"C:\Program Files\7-Zip\7z.exe"),
        Path(r"C:\Program Files (x86)\7-Zip\7z.exe"),
    ]:
        if p.exists():
            return p
    return None


def extract_rar(rar_path: Path, out_dir: Path, seven_z: Path) -> bool:
    try:
        subprocess.run(
            [str(seven_z), "x", str(rar_path), f"-o{out_dir}", "-y"],
            check=True,
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return True
    except Exception:
        return False


def remove_ad_scripts_and_inject_api(html: str, slot_id: str) -> str:
    pattern = re.compile(
        r"<script[^>]*(?:"
        r"adsbygoogle|pagead2\.googlesyndication\.com|doubleclick\.net|"
        r"cpro\.baidu\.com|hm\.baidu\.com|cnzz\.com"
        r")[\s\S]*?</script>",
        flags=re.IGNORECASE,
    )
    html = re.sub(pattern, "<!-- removed third-party ad -->", html)
    snippet = f'''<script src="/game-ad-api.js"></script>
<script>window.GameAdAPI&&GameAdAPI.requestGameAd("game_{slot_id}");</script>'''
    if "</body>" in html:
        html = html.replace("</body>", snippet + "\n</body>", 1)
    else:
        html = html + "\n" + snippet
    return html


def inject_ads_into_game(game_dir: Path, slot_id: str):
    for ext in ("*.html", "*.htm"):
        for f in game_dir.rglob(ext):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                if f"game_{slot_id}" in content and "game-ad-api.js" in content:
                    continue
                new_content = remove_ad_scripts_and_inject_api(content, slot_id)
                if new_content != content:
                    f.write_text(new_content, encoding="utf-8")
            except Exception:
                pass


def get_first_html_path(game_dir: Path) -> Optional[Path]:
    for name in ("index.html", "index.htm", "Index.html", "Index.htm"):
        p = game_dir / name
        if p.exists():
            return p
    for f in sorted(game_dir.glob("*.html")) + sorted(game_dir.glob("*.htm")):
        return f
    for sub in game_dir.iterdir():
        if sub.is_dir():
            r = get_first_html_path(sub)
            if r:
                return r
    return None


def get_extracted_game_folder(extract_base: Path, num: int) -> Optional[Path]:
    """从解压目录找到第 num 个游戏的实际内容目录（可能有一层子目录）。"""
    folder = extract_base / f"{num:02d}"
    if not folder.exists():
        return None
    # 可能解压得到 01/01-僵尸鸭猎手/ 或 01/<一堆文件>
    html = get_first_html_path(folder)
    if html:
        return folder
    for sub in folder.iterdir():
        if sub.is_dir():
            if get_first_html_path(sub):
                return sub
    return None


def clear_public_games():
    if not TARGET_GAMES_DIR.exists():
        TARGET_GAMES_DIR.mkdir(parents=True, exist_ok=True)
        return
    for item in TARGET_GAMES_DIR.iterdir():
        if item.is_dir() or item.is_file():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except Exception as e:
                print(f"  删除失败 {item}: {e}")


def main():
    print("=" * 60)
    print("60 款 H5 小游戏部署（仅保留此 60 款，并接入你的广告）")
    print("=" * 60)

    if not SOURCE_RAR_DIR.exists():
        print(f"错误: 源目录不存在: {SOURCE_RAR_DIR}")
        return

    # 1) 解压或使用已解压目录
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    rar_files = sorted(SOURCE_RAR_DIR.glob("*.rar"))
    if not rar_files:
        print("未找到 .rar 文件。若你已手动解压，请把 60 个子文件夹放到：")
        print(f"  {EXTRACT_DIR}")
        print("并命名为 01, 02, ... 60，然后重新运行本脚本。")
        return

    seven_z = find_7z()
    if seven_z:
        print("使用 7-Zip 解压 60 个 RAR ...")
        for i, rar in enumerate(rar_files, 1):
            num = i  # 01-xxx.rar -> 01
            out = EXTRACT_DIR / f"{num:02d}"
            out.mkdir(parents=True, exist_ok=True)
            if extract_rar(rar, out, seven_z):
                print(f"  [{i}/60] {rar.name} OK")
            else:
                print(f"  [{i}/60] {rar.name} 解压失败")
    else:
        print("未检测到 7-Zip。请手动将 60 个 RAR 解压到：")
        print(f"  {EXTRACT_DIR}/01, {EXTRACT_DIR}/02, ... {EXTRACT_DIR}/60")
        print("然后重新运行本脚本。")
        return

    # 2) 清空并部署到 public/games/game_01..game_60
    print("\n清空 public/games 并部署 60 款游戏...")
    clear_public_games()

    deployed: List[Dict] = []
    for i in range(1, 61):
        slot_id = f"{i:02d}"
        src = get_extracted_game_folder(EXTRACT_DIR, i)
        if not src:
            print(f"  [{i}/60] 未找到解压内容，跳过")
            continue
        dest = TARGET_GAMES_DIR / f"game_{slot_id}"
        try:
            shutil.copytree(src, dest)
            inject_ads_into_game(dest, slot_id)
            html_path = get_first_html_path(dest)
            rel_html = html_path.relative_to(dest) if html_path else "index.html"
            # 缩略图：从预览图复制
            thumb_src = PREVIEW_DIR / f"{i:02d}.jpg"
            if not thumb_src.exists():
                thumb_src = PREVIEW_DIR / f"{i:02d}.png"
            thumb_name = thumb_src.suffix.lstrip(".") or "jpg"
            thumb_dest = dest / f"thumb.{thumb_name}"
            if thumb_src.exists():
                shutil.copy2(thumb_src, thumb_dest)
                thumb_url = f"/games/game_{slot_id}/thumb.{thumb_name}"
            else:
                thumb_url = f"/games/game_{slot_id}/thumb.jpg"
            cn_name, en_name = GAME_NAMES[i - 1] if i <= len(GAME_NAMES) else ("", f"Game {i}")
            deployed.append({
                "id": i,
                "slot_id": slot_id,
                "title_en": en_name,
                "title_cn": cn_name,
                "url": f"/games/game_{slot_id}/{rel_html.as_posix()}".replace("\\", "/"),
                "thumb": thumb_url,
            })
            print(f"  [{i}/60] game_{slot_id} {en_name or cn_name}")
        except Exception as e:
            print(f"  [{i}/60] game_{slot_id} 失败: {e}")

    if not deployed:
        print("没有成功部署任何游戏。")
        return

    # 3) 重写 games.js，仅包含这 60 款
    print("\n写入 src/data/games.js（仅此 60 款）...")
    if GAMES_JS.exists():
        backup = GAMES_JS.with_suffix(".js.backup_60")
        shutil.copy2(GAMES_JS, backup)
        print(f"  已备份原文件到: {backup}")

    lines = ["const games = ["]
    for i, g in enumerate(deployed):
        title = g["title_en"] or g["title_cn"] or f"Game {g['id']}"
        lines.append("  {")
        lines.append(f"    id: '{g['id']}',")
        lines.append(f"    title: '{title.replace(chr(39), chr(92) + chr(39))}',")
        lines.append(f"    description: 'Play {title} - HTML5 game. Have fun!',")
        lines.append("    instructions: 'Use mouse or touch to play.',")
        lines.append(f"    url: '{g['url']}',")
        lines.append("    category: 'Arcade',")
        lines.append("    tags: 'HTML5, Game, Fun',")
        lines.append(f"    thumb: '{g['thumb']}',")
        lines.append(f"    link: 'game-{g['slot_id']}',")
        lines.append("    null: '',")
        lines.append("    star: 3")
        lines.append("  }" + ("," if i < len(deployed) - 1 else ""))
    lines.append("]")
    lines.append("export default games")
    GAMES_JS.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已写入，共 {len(deployed)} 条。")

    # 4) 提醒广告配置
    print("\n" + "=" * 60)
    print("下一步：请确认广告已接你的 AdSense")
    print("  - 站内已用 ca-pub-5319587106206709（见 index.html / AdSense接入指南.md）")
    print("  - 游戏内通过 /game-ad-api.js 请求 game_01..game_60 广告位")
    print("  - 在 src/utils/adManager.js 中把 SLOT_CONFIG 的 game_01..game_60 的 adSlot 改成你的广告位 ID")
    print("=" * 60)


if __name__ == "__main__":
    main()
