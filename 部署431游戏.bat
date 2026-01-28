@echo off
chcp 65001 >nul
echo ========================================
echo 431个H5游戏部署和翻译脚本
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

echo 正在运行部署脚本...
echo.

python "部署431游戏并翻译.py"

echo.
echo ========================================
echo 脚本执行完成
echo ========================================
pause
