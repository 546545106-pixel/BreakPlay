@echo off
chcp 65001 >nul
echo ========================================
echo 修复games.js文件格式
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b 1
)

python "修复games.js格式.py"

if errorlevel 1 (
    echo.
    echo [错误] 修复失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 修复完成！
echo ========================================
pause
