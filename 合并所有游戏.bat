@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 保存当前目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo 合并所有游戏脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [信息] Python已安装
python --version
echo.

REM 检查脚本文件是否存在
if not exist "%SCRIPT_DIR%合并所有游戏.py" (
    echo [错误] 找不到脚本文件: 合并所有游戏.py
    echo 当前目录: %SCRIPT_DIR%
    echo 请确保批处理文件和Python脚本在同一目录
    echo.
    pause
    exit /b 1
)

echo [信息] 找到脚本文件
echo.

REM 检查必要的目录是否存在
if not exist "%SCRIPT_DIR%src\data" (
    echo [错误] 找不到目录: src\data
    echo 请确保在项目根目录运行此脚本
    echo.
    pause
    exit /b 1
)

echo [信息] 开始执行合并脚本...
echo ========================================
echo.

REM 执行Python脚本并捕获输出
cd /d "%SCRIPT_DIR%"
python "合并所有游戏.py" 2>&1

set PYTHON_EXIT_CODE=!errorlevel!

if !PYTHON_EXIT_CODE! neq 0 (
    echo.
    echo ========================================
    echo [错误] 脚本执行失败，错误代码: !PYTHON_EXIT_CODE!
    echo ========================================
    echo.
    echo 可能的原因:
    echo 1. Python脚本语法错误
    echo 2. 文件路径不正确
    echo 3. 文件编码问题
    echo 4. 权限不足
    echo.
    echo 请检查上面的错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 批处理文件执行完成
echo ========================================
echo.
echo 提示: 如果看到上面的"合并完成"消息，说明操作已成功
echo.
pause
