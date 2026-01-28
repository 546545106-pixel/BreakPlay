# 推送代码到 GitHub 的步骤

## 方法一：使用 GitHub Desktop（推荐，最简单）

### 1. 打开 GitHub Desktop
- 如果还没安装，从 [GitHub Desktop 官网](https://desktop.github.com/) 下载安装

### 2. 添加本地仓库
1. 打开 GitHub Desktop
2. 点击 **"File"** → **"Add Local Repository"**
3. 选择你的项目文件夹：`d:\游戏网站1\wegogame.net-main`
4. 如果提示"这不是一个 Git 仓库"，点击 **"Create a repository"**

### 3. 连接到 GitHub 仓库
1. 在 GitHub Desktop 中，点击 **"Publish repository"** 或 **"Repository"** → **"Repository Settings"**
2. 在 "Remote" 部分，点击 **"Add Remote"**
3. 输入你的 GitHub 仓库地址（从 GitHub 网页复制）
   - 例如：`https://github.com/你的用户名/桌面教程.git`
4. 点击 **"Save"**

### 4. 提交并推送代码
1. 在 GitHub Desktop 左下角，填写提交信息：
   - 例如："优化项目结构，准备部署到 Cloudflare Pages"
2. 点击 **"Commit to main"**（或你的主分支名）
3. 点击右上角的 **"Push origin"** 推送代码到 GitHub

---

## 方法二：使用命令行（Git Bash 或 PowerShell）

### 1. 打开命令行
在项目文件夹 `d:\游戏网站1\wegogame.net-main` 中打开 PowerShell 或 Git Bash

### 2. 初始化 Git（如果还没有）
```bash
git init
```

### 3. 添加远程仓库
```bash
git remote add origin https://github.com/你的用户名/桌面教程.git
```
（将 "你的用户名" 和 "桌面教程" 替换为你的实际信息）

### 4. 添加所有文件
```bash
git add .
```

### 5. 提交代码
```bash
git commit -m "优化项目结构，准备部署到 Cloudflare Pages"
```

### 6. 推送到 GitHub
```bash
git push -u origin main
```
（如果主分支是 `master`，则使用 `git push -u origin master`）

---

## 验证推送成功

1. 刷新你的 GitHub 仓库页面
2. 应该能看到项目文件已经上传
3. 确认以下重要文件存在：
   - `package.json`
   - `vite.config.js`
   - `src/` 文件夹
   - `public/` 文件夹
   - `.gitignore`

---

## 如果遇到问题

### 问题 1：提示需要认证
- 使用 GitHub Personal Access Token 代替密码
- 或者使用 GitHub Desktop，它会自动处理认证

### 问题 2：文件太大
- 检查 `.gitignore` 是否正确配置
- 确保 `node_modules`、`dist` 等文件夹被忽略

### 问题 3：推送被拒绝
- 先执行：`git pull origin main --allow-unrelated-histories`
- 然后再推送
