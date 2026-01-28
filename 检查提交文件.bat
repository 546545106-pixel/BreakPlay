@echo off
chcp 65001 >nul
echo ========================================
echo 检查哪些文件会被提交到 Git
echo ========================================
echo.

if not exist ".git" (
    echo ❌ 错误: 这不是一个 Git 仓库
    echo 请先初始化 Git 仓库
    pause
    exit /b 1
)

echo [检查 1] 查看 .gitignore 配置...
if exist ".gitignore" (
    echo ✅ .gitignore 文件存在
    echo.
    echo .gitignore 中配置的忽略规则：
    findstr /i "node_modules dist .py .bat" .gitignore
    echo.
) else (
    echo ❌ .gitignore 文件不存在！
    pause
    exit /b 1
)

echo [检查 2] 检查不应该提交的文件是否存在...
if exist "node_modules" (
    echo ⚠️  警告: node_modules 文件夹存在
    echo    这个文件夹应该被 .gitignore 忽略，不应该提交
) else (
    echo ✅ node_modules 不存在（正常）
)

if exist "dist" (
    echo ⚠️  警告: dist 文件夹存在
    echo    这个文件夹应该被 .gitignore 忽略，不应该提交
) else (
    echo ✅ dist 不存在（正常）
)

echo.
echo [检查 3] 检查开发工具文件...
set /a py_count=0
set /a bat_count=0
for %%f in (*.py) do set /a py_count+=1
for %%f in (*.bat) do set /a bat_count+=1

if %py_count% GTR 0 (
    echo ⚠️  警告: 发现 %py_count% 个 .py 文件
    echo    这些文件应该被 .gitignore 忽略
) else (
    echo ✅ 没有 .py 文件在根目录（正常）
)

if %bat_count% GTR 0 (
    echo ⚠️  警告: 发现 %bat_count% 个 .bat 文件
    echo    这些文件应该被 .gitignore 忽略
) else (
    echo ✅ 没有 .bat 文件在根目录（正常）
)

echo.
echo [检查 4] 检查必需文件...
if exist "package.json" (
    echo ✅ package.json 存在
) else (
    echo ❌ package.json 不存在！
)

if exist "vite.config.js" (
    echo ✅ vite.config.js 存在
) else (
    echo ❌ vite.config.js 不存在！
)

if exist "src\main.js" (
    echo ✅ src\main.js 存在
) else (
    echo ❌ src\main.js 不存在！
)

if exist "public\_redirects" (
    echo ✅ public\_redirects 存在
) else (
    echo ⚠️  警告: public\_redirects 不存在（建议添加）
)

echo.
echo ========================================
echo 检查完成！
echo ========================================
echo.
echo 重要提示：
echo 1. 如果 node_modules 或 dist 文件夹存在，这是正常的
echo    它们会被 .gitignore 自动忽略，不会提交
echo 2. 在 GitHub Desktop 中，被忽略的文件不会显示在文件列表中
echo 3. 如果 GitHub Desktop 中看到 node_modules，说明 .gitignore 可能有问题
echo.
echo 下一步：在 GitHub Desktop 中查看文件列表
echo 确认没有看到 node_modules、dist、.py、.bat 文件
echo.
pause
