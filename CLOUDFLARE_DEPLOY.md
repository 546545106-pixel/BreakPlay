# Cloudflare Pages 部署指南

## 部署前准备

### 1. 确保项目可以正常构建

在本地测试构建：
```bash
npm install
npm run build
```

构建成功后，会在 `dist` 文件夹生成静态文件。

### 2. 将代码推送到 Git 仓库

确保你的代码已经推送到 GitHub 或 GitLab 仓库。

## Cloudflare Pages 部署步骤

### 步骤 1：登录 Cloudflare

1. 访问 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 登录你的 Cloudflare 账号（如果没有，先注册）

### 步骤 2：创建 Pages 项目

1. 在 Cloudflare 控制台左侧菜单，找到并点击 **"Workers 和 Pages"**
2. 选择 **"Pages"** 标签页
3. 点击 **"创建项目"** 或 **"Create a project"**

### 步骤 3：连接 Git 仓库

1. 选择 **"连接到 Git"** (Connect to Git)
2. 授权 Cloudflare 访问你的 GitHub/GitLab 账号
3. 选择你要部署的仓库
4. 点击 **"开始设置"** (Begin setup)

### 步骤 4：配置构建设置

**项目名称：** 自定义（如 `wegogame`，会生成 `wegogame.pages.dev` 域名）

**生产分支：** `main` 或 `master`（根据你的仓库主分支）

**构建设置：**

- **框架预设：** `Vite`
- **构建命令：** `npm run build`
- **构建输出目录：** `dist`
- **根目录：** `/`（默认）

**环境变量（如果需要）：**
- `NODE_VERSION`: `18`（可选，Cloudflare 会自动检测）

### 步骤 5：保存并部署

1. 检查所有设置
2. 点击 **"保存并部署"** (Save and Deploy)
3. 等待构建完成（通常需要 1-3 分钟）

### 步骤 6：获取部署网址

部署完成后，Cloudflare 会生成一个默认网址：
- 格式：`https://你的项目名.pages.dev`
- 例如：`https://wegogame.pages.dev`

点击这个网址，确认网站能正常打开。

## 绑定自定义域名（可选）

如果你有自己的域名：

1. 在 Cloudflare Pages 项目页面，点击 **"自定义域"** (Custom domains)
2. 点击 **"设置自定义域"** (Set up a custom domain)
3. 输入你的域名（如 `wegogame.net`）
4. 按照提示完成 DNS 配置
5. 等待 DNS 生效（通常几分钟到几小时）

## 自动部署

配置完成后，每次你向主分支推送代码，Cloudflare Pages 会自动：
1. 检测代码变更
2. 运行构建命令
3. 部署新版本

你可以在 Cloudflare Pages 控制台查看部署历史和状态。

## 常见问题

### Q1: 构建失败怎么办？

**检查清单：**
- ✅ 确保 `package.json` 中有 `build` 脚本
- ✅ 检查构建日志中的错误信息
- ✅ 确保所有依赖都已正确安装
- ✅ 检查 Node.js 版本兼容性

### Q2: 网站显示 404 错误？

**可能原因：**
- 构建输出目录配置错误（应该是 `dist`）
- 路由配置问题（Vue Router 需要配置 history 模式）

**解决方案：**
在 `vite.config.js` 中确保路由配置正确，或添加 `_redirects` 文件到 `public` 文件夹。

### Q3: 如何回滚到之前的版本？

在 Cloudflare Pages 控制台：
1. 进入项目页面
2. 点击 **"部署"** (Deployments) 标签
3. 找到之前的成功部署
4. 点击 **"重新部署"** (Retry deployment)

## 提交 Google AdSense 审核

部署完成后，你可以：
1. 使用 Cloudflare Pages 提供的网址（`xxx.pages.dev`）或你的自定义域名
2. 确保网站可以正常访问
3. 提交给 Google AdSense 进行审核

## 性能优化建议

Cloudflare Pages 自动提供：
- ✅ CDN 加速（全球节点）
- ✅ HTTPS 证书（自动配置）
- ✅ DDoS 防护
- ✅ 缓存优化

你的网站已经配置了代码分割和优化，可以充分利用 Cloudflare 的 CDN 优势。
