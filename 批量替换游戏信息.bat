@echo off
chcp 65001 >nul
echo ========================================
echo 批量替换游戏信息
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    pause
    exit /b 1
)

python "批量替换游戏信息.py"

if errorlevel 1 (
    echo.
    echo [错误] 替换失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 处理完成！
echo ========================================
pause
