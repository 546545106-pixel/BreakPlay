# 使用命令行初始化 Git 仓库

## 方法：使用 PowerShell 初始化

### 步骤 1：打开 PowerShell

1. **在项目文件夹中打开 PowerShell**
   - 按 `Win + R`，输入 `powershell`，回车
   - 或者：在文件资源管理器中，进入 `d:\游戏网站1\wegogame.net-main`
   - 在地址栏输入 `powershell` 并回车

2. **或者直接右键打开**
   - 在 `wegogame.net-main` 文件夹中
   - 按住 `Shift` 键，右键点击空白处
   - 选择 **"在此处打开 PowerShell 窗口"**

---

### 步骤 2：执行初始化命令

在 PowerShell 中，依次执行以下命令：

```powershell
# 1. 确认当前目录（应该显示你的项目路径）
pwd

# 2. 初始化 Git 仓库
git init

# 3. 添加所有文件到暂存区
git add .

# 4. 创建初始提交
git commit -m "初始提交：准备部署到 Cloudflare Pages"
```

---

### 步骤 3：在 GitHub Desktop 中添加仓库

初始化完成后：

1. **关闭 GitHub Desktop 的对话框**（如果有的话）

2. **重新添加本地仓库**
   - 在 GitHub Desktop 中，点击 **File** → **Add Local Repository**
   - 点击 **Choose...** 按钮
   - 选择文件夹：`d:\游戏网站1\wegogame.net-main`
   - 点击 **Add repository**

3. **现在应该能正常显示了**
   - 左侧会显示所有文件
   - 确认文件列表正确

---

## 如果 PowerShell 命令执行失败

### 检查 Git 是否已安装

在 PowerShell 中执行：
```powershell
git --version
```

如果提示找不到命令，需要先安装 Git：
- 下载：https://git-scm.com/download/win
- 或者使用 GitHub Desktop 自带的 Git

---

## 验证初始化成功

初始化后，在项目文件夹中应该能看到：
- `.git/` 文件夹（隐藏文件夹，Git 仓库信息）

如果看到这个文件夹，说明初始化成功了！

---

## 下一步

初始化完成后：
1. ✅ 在 GitHub Desktop 中添加这个仓库
2. ✅ 检查文件列表
3. ✅ 提交文件
4. ✅ 连接 GitHub 远程仓库
5. ✅ 推送代码

按照这个步骤操作即可！🚀
