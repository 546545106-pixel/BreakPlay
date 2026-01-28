@echo off
chcp 65001 >nul
echo ========================================
echo 更新游戏封面脚本
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b 1
)

python "更新游戏封面.py"

if errorlevel 1 (
    echo.
    echo [错误] 更新失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 更新完成！
echo ========================================
pause
