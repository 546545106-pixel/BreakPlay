# 初始化 Git 仓库指南

## 当前情况
GitHub Desktop 检测到 `d:\游戏网站1\wegogame.net-main` 目录还不是 Git 仓库，需要先初始化。

## 解决方案

### 方法 1：在 GitHub Desktop 中直接创建（推荐）

1. **在 GitHub Desktop 对话框中**
   - 看到提示："This directory does not appear to be a Git repository"
   - 点击 **"create a repository"** 链接（蓝色可点击的文字）

2. **配置仓库设置**
   - **Name**: `wegogame`（或你喜欢的名字）
   - **Description**: 可选，填写项目描述
   - **Local path**: 确认是 `D:\游戏网站1\wegogame.net-main`
   - **Git ignore**: 选择 "None"（我们已经有 `.gitignore` 文件了）
   - **License**: 可选，选择 "None" 即可

3. **点击 "Create repository"**
   - GitHub Desktop 会自动初始化 Git 仓库

4. **完成后**
   - 你会看到项目文件出现在 GitHub Desktop 中
   - 左下角会显示所有未提交的文件

---

### 方法 2：使用命令行初始化（备选）

如果方法 1 不工作，可以在项目文件夹中打开 PowerShell，执行：

```bash
# 进入项目目录
cd "d:\游戏网站1\wegogame.net-main"

# 初始化 Git 仓库
git init

# 添加所有文件到暂存区
git add .

# 创建初始提交
git commit -m "Initial commit: 准备部署到 Cloudflare Pages"
```

然后回到 GitHub Desktop，点击 **"Add Local Repository"**，选择该文件夹。

---

## 初始化后的下一步

### 1. 检查文件状态

在 GitHub Desktop 中，你应该看到：
- ✅ 左侧显示所有文件
- ✅ 右下角显示文件变更数量
- ⚠️ 确认 `node_modules/` 和 `dist/` **不在列表中**（如果出现，说明 `.gitignore` 需要检查）

### 2. 连接到 GitHub 远程仓库

1. 点击 **Repository** → **Repository Settings**
2. 点击 **Remote** 标签
3. 点击 **Add Remote**
4. 输入你的 GitHub 仓库地址：
   ```
   https://github.com/你的用户名/桌面教程.git
   ```
   （从 GitHub 网页复制仓库地址）
5. 点击 **Save**

### 3. 提交并推送代码

1. **填写提交信息**（左下角）：
   ```
   准备部署到 Cloudflare Pages
   ```

2. **提交代码**：
   - 点击 **Commit to main**（或你的主分支名）

3. **推送到 GitHub**：
   - 点击右上角的 **Push origin**
   - 等待上传完成

---

## 验证步骤

### 检查 .gitignore 是否生效

在 GitHub Desktop 中查看文件列表，确认：
- ❌ 没有 `node_modules/` 文件夹
- ❌ 没有 `dist/` 文件夹
- ❌ 没有 `.py` 文件
- ❌ 没有 `.bat` 文件
- ✅ 有 `src/` 文件夹
- ✅ 有 `public/` 文件夹
- ✅ 有 `package.json`

如果看到不应该提交的文件，检查 `.gitignore` 配置。

---

## 常见问题

### Q1: 点击 "create a repository" 后没有反应？

**解决方案：**
- 关闭对话框，手动初始化：
  ```bash
  cd "d:\游戏网站1\wegogame.net-main"
  git init
  ```
- 然后重新在 GitHub Desktop 中添加仓库

### Q2: 初始化后看到太多文件（包括 node_modules）？

**解决方案：**
- 检查 `.gitignore` 文件是否存在
- 如果存在但无效，可能需要重新添加：
  ```bash
  git rm -r --cached .
  git add .
  git commit -m "Update .gitignore"
  ```

### Q3: 如何确认哪些文件会被提交？

在 GitHub Desktop 中：
- 左侧文件列表显示的就是会被提交的文件
- 灰色显示的文件是被忽略的（不会提交）
- 绿色显示的文件是新文件（会被提交）

---

## 下一步

初始化完成后，按照 `快速开始.md` 中的步骤继续：
1. ✅ 初始化 Git 仓库（当前步骤）
2. ⏭️ 连接到 GitHub 远程仓库
3. ⏭️ 提交并推送代码
4. ⏭️ 在 Cloudflare Pages 中部署

祝你顺利！🚀
