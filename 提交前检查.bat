@echo off
chcp 65001 >nul
echo ========================================
echo 提交前检查工具
echo ========================================
echo.

echo [1] 检查必需文件是否存在...
if not exist "package.json" (
    echo ❌ 错误: package.json 不存在！
    pause
    exit /b 1
)
if not exist "vite.config.js" (
    echo ❌ 错误: vite.config.js 不存在！
    pause
    exit /b 1
)
if not exist "index.html" (
    echo ❌ 错误: index.html 不存在！
    pause
    exit /b 1
)
if not exist "src\main.js" (
    echo ❌ 错误: src\main.js 不存在！
    pause
    exit /b 1
)
if not exist "public\_redirects" (
    echo ⚠️  警告: public\_redirects 不存在（建议添加）
)
echo ✅ 必需文件检查通过
echo.

echo [2] 检查不需要提交的文件...
if exist "node_modules" (
    echo ⚠️  警告: node_modules 文件夹存在（应该被 .gitignore 忽略）
)
if exist "dist" (
    echo ⚠️  警告: dist 文件夹存在（应该被 .gitignore 忽略）
)
echo ✅ 检查完成
echo.

echo [3] 检查 .gitignore 配置...
if not exist ".gitignore" (
    echo ❌ 错误: .gitignore 不存在！
    pause
    exit /b 1
)
echo ✅ .gitignore 存在
echo.

echo ========================================
echo 检查完成！
echo ========================================
echo.
echo 如果所有检查都通过，可以安全地提交代码。
echo.
pause
