@echo off
chcp 65001 >nul
echo ========================================
echo 批量更新游戏封面
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    pause
    exit /b 1
)

python "批量更新封面.py"

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
