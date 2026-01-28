@echo off
chcp 65001 >nul
echo ========================================
echo 合并游戏数据脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.6+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 正在合并游戏数据...
echo.

python "修复并合并游戏.py"

if errorlevel 1 (
    echo.
    echo 合并过程中出现错误，请查看上方错误信息
) else (
    echo.
    echo 合并完成！
)

echo.
pause
