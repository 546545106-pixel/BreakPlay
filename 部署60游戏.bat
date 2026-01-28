@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ========================================
echo   60 款 H5 游戏部署（仅保留此 60 款）
echo ========================================
echo.
python 部署60游戏.py
echo.
pause
