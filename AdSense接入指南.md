# Google AdSense 广告接入指南

## 接入概述

根据 [Google AdSense 官方文档](https://support.google.com/adsense/answer/9274019?hl=zh-Hans)，已完成以下接入工作：

1. ✅ AdSense 基础代码已添加到 `<head>` 标签中
2. ✅ 创建了 AdSense 广告组件
3. ✅ 在所有广告位集成了 AdSense 代码
4. ✅ 广告位位置清晰可见，带有占位符标识

---

## 已完成的修改

### 1. AdSense 基础代码 ✅

**文件：** `index.html`

**位置：** `<head>` 标签内

**代码：**
```html
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5319587106206709"
     crossorigin="anonymous"></script>
```

**说明：**
- 已按照 Google 要求放置在 `<head>` 标签中
- 包含您的 AdSense 发布商ID：`ca-pub-5319587106206709`
- 使用 `async` 和 `crossorigin="anonymous"` 属性

---

### 2. AdSense 广告组件 ✅

**文件：** `src/components/AdSenseAd.vue`（新建）

**功能：**
- 可复用的 AdSense 广告单元组件
- 自动初始化 AdSense 广告
- 支持自定义尺寸和样式
- 自动处理脚本加载延迟

**使用方法：**
```vue
<AdSenseAd 
  ad-slot="your-ad-slot-id" 
  :width="300" 
  :height="250" 
/>
```

**Props：**
- `adSlot` (必需) - 广告位ID，需要在 AdSense 后台获取
- `adClient` (可选) - 发布商ID，默认：`ca-pub-5319587106206709`
- `width` (可选) - 广告宽度，默认：`auto`
- `height` (可选) - 广告高度，默认：`auto`

---

### 3. 广告位集成 ✅

#### 首页广告位

**文件：** `src/views/HomePage/index.vue`

**广告位 #0：**
- 位置：页面顶部
- 尺寸：300×250px
- 代码：`<AdSenseAd ad-slot="your-ad-slot-id-0" :width="300" :height="250" />`

**广告位 #1：**
- 位置：Hot Games 和 Try Now 之间
- 尺寸：300×250px
- 代码：`<AdSenseAd ad-slot="your-ad-slot-id-1" :width="300" :height="250" />`

#### 详情页广告位

**文件：** `src/views/DetailPage/index.vue`

**广告位 #2：**
- 位置：游戏详情和相似游戏之间
- 尺寸：300×250px
- 代码：`<AdSenseAd ad-slot="your-ad-slot-id-2" :width="300" :height="250" />`

**广告位 #3：**
- 位置：页面底部
- 尺寸：300×250px
- 代码：`<AdSenseAd ad-slot="your-ad-slot-id-3" :width="300" :height="250" />`

---

## 下一步操作

### 1. 获取广告位ID

根据 Google AdSense 文档，您需要：

1. 登录您的 AdSense 账号
2. 点击 **广告** → **按广告单元**
3. 创建新的广告单元（或使用现有单元）
4. 获取每个广告单元的 **广告位ID**

### 2. 替换占位符ID

在以下文件中，将 `your-ad-slot-id-X` 替换为实际的广告位ID：

**首页：** `src/views/HomePage/index.vue`
- `your-ad-slot-id-0` → 您的第一个广告位ID
- `your-ad-slot-id-1` → 您的第二个广告位ID

**详情页：** `src/views/DetailPage/index.vue`
- `your-ad-slot-id-2` → 您的第三个广告位ID
- `your-ad-slot-id-3` → 您的第四个广告位ID

### 3. 示例代码

假设您的广告位ID是 `1234567890`，则代码应该是：

```vue
<AdSenseAd ad-slot="1234567890" :width="300" :height="250" />
```

---

## 广告位位置说明

### 首页（HomePage）

1. **Advertisement Slot #0**
   - 位置：页面最顶部
   - 尺寸：300×250px
   - 用途：首屏展示

2. **Advertisement Slot #1**
   - 位置：Hot Games 区块之后，Try Now 区块之前
   - 尺寸：300×250px
   - 用途：内容中间插入

### 详情页（DetailPage）

3. **Advertisement Slot #2**
   - 位置：游戏详情描述之后，相似游戏之前
   - 尺寸：300×250px
   - 用途：内容相关广告

4. **Advertisement Slot #3**
   - 位置：页面底部
   - 尺寸：300×250px
   - 用途：页面底部展示

---

## 广告位样式

所有广告位都带有：
- **蓝色虚线边框** - 方便识别位置
- **浅蓝色背景** - 视觉区分
- **占位符文字** - 显示广告位编号和提示信息
- **自动隐藏** - 当广告加载后，占位符自动隐藏

---

## 技术实现

### AdSense 初始化

组件会在以下时机初始化广告：
1. 组件挂载后立即尝试初始化
2. 如果脚本未加载，等待1秒后重试
3. 使用 `window.adsbygoogle.push({})` 初始化

### 响应式支持

- 使用 `data-full-width-responsive="true"` 属性
- 广告会自动适配不同屏幕尺寸
- 移动端自动调整大小

---

## 注意事项

1. **广告位ID必须唯一**：每个广告位需要使用不同的ID
2. **等待审核**：新创建的广告单元需要等待 Google 审核
3. **测试模式**：审核期间可能显示测试广告或空白
4. **占位符**：占位符会在广告实际加载后自动隐藏
5. **保留其他广告服务**：代码中保留了 GPT 和 ExMarketplace 脚本，可以同时使用

---

## 修改的文件清单

1. ✅ `index.html` - 添加 AdSense 基础代码
2. ✅ `src/components/AdSenseAd.vue` - 新建 AdSense 组件
3. ✅ `src/views/HomePage/index.vue` - 集成广告位 #0 和 #1
4. ✅ `src/views/DetailPage/index.vue` - 集成广告位 #2 和 #3
5. ✅ `src/assets/ui-optimized.css` - 更新广告位样式

---

## 测试检查清单

- [ ] AdSense 基础代码已添加到 `<head>` 标签
- [ ] 所有广告位都显示占位符
- [ ] 占位符显示正确的广告位编号
- [ ] 替换广告位ID后，广告能正常显示
- [ ] 广告加载后，占位符自动隐藏
- [ ] 移动端广告正常显示

---

所有 AdSense 代码已正确接入！请按照上述步骤获取广告位ID并替换占位符即可。
