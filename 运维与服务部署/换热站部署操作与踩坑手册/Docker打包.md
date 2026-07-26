# 📒 部署笔记：Vue3 项目 Docker 打包与 GitHub Pages 上线全流程

## 1. 环境准备与项目启动（依赖安装）

### 🤔 遇到问题

在 `CloudPlatform` 目录下执行 `npm install`，报错 `ENOENT: no such file or directory, open '...package.json'`。

### 🧠 原因分析

项目结构是多层嵌套的，`package.json` 并不在根目录，而是在子文件夹 `cloud-platform-frontend` 中。直接对没有配置文件的目录安装依赖，NPM 无法识别。

### ✅ 解决方案

使用 `dir`（Windows）或 `ls`（Mac/Linux）查看目录结构，找到包含 `package.json` 的实际项目根目录，进入该目录后再执行 `npm install`。

---

## 2. 本地运行与打包构建

### 💻 运行命令

```bash
npm run serve   # 启动开发服务器（默认 localhost:8080）
npm run build   # 生成生产环境静态文件（默认输出到 dist 目录）
```

### ⚠️ 遇到警告

打包时出现警告：`entrypoint size limit: The following entrypoint(s) combined asset size exceeds the recommended limit (244 KiB)`。
**原因**：`chunk-vendors.js` 等第三方库（如 Element Plus、ECharts）体积较大，超过了 Webpack 默认的建议大小。

---

## 3. Docker 容器化部署

### 🐳 核心步骤

编写 `Dockerfile`，基于 `nginx:alpine` 镜像，将 `dist` 目录内容复制到 Nginx 的 `/usr/share/nginx/html` 目录。

### ❌ 踩坑 1：Docker build 参数缺失

执行 `docker build -t cloud-fronted` 报错 `requires 1 argument`。
**原因**：命令末尾漏掉了代表构建上下文的 `.`。
**修复**：`docker build -t cloud-frontend .`

### ❌ 踩坑 2：运行容器时镜像名拼写错误

执行 `docker run -d -p 8080:80 --name my-fronted cloud-fronted` 报错 `Unable to find image 'cloud-fronted:latest' locally`。
**原因**：构建时的标签是 `cloud-frontend`（有 `n`），运行时的名称写成了 `cloud-fronted`（少了 `n`）。
**修复**：保持镜像名称完全一致：`docker run -d -p 8080:80 --name my-frontend cloud-frontend`

---

## 4. GitHub Pages 部署（最核心、坑最多的地方）

### 🎯 目标

将打包好的静态网页部署到 `https://<用户名>.github.io/<仓库名>`，让任何人都能通过网址访问。

### 🔧 关键配置

**① 配置 `vue.config.js`（设置资源公共路径）**

```javascript
const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  publicPath: process.env.NODE_ENV === 'production' 
    ? '/仓库名/'   // 如 /CloudPlatform/，注意前后斜杠不能少
    : '/'
})
```
<details>
<summary>解析</summary>

> [!NOTE]
>
>1. `const { defineConfig } = require('@vue/cli-service')`
>
>- 从 `@vue/cli-service` 包中解构出 `defineConfig` 函数。
>- **作用**：`defineConfig` 是 Vue CLI 3+ 提供的辅助函数，主要用来提供**智能提示**（TypeScript 类型支持）和**配置校验**，避免手写对象时出现拼写>错误或格式问题。虽然直接用普通对象也行，但官方推荐使用它。
>
>2. `module.exports = defineConfig({ ... })`
>
>- 将配置对象导出，Vue CLI 会读取这个导出对象作为最终的配置。
>- `defineConfig` 接收一个配置对象，内部包含了所有可用的构建选项。
>
>3. `publicPath` 字段
>
>- **含义**：`publicPath` 是部署应用时的**基础 URL**，决定了所有静态资源（JS、CSS、图片、字体等）在浏览器中引用的路径前缀。
>- 例如，如果 `publicPath` 设为 `/my-app/`，那么构建后生成的 `index.html` 中加载的脚本路径会是 `/my-app/js/app.js`，而不是 `/js/app.js`。
>
>4. 条件判断：`process.env.NODE_ENV === 'production' ? '/仓库名/' : '/'`
>
>- `process.env.NODE_ENV` 是 Node.js 环境变量，Vue CLI 在运行时自动设置：
>  - 执行 `npm run serve`（开发模式）时，值为 `'development'`。
>  - 执行 `npm run build`（生产构建）时，值为 `'production'`。
>    - **开发模式(development)保留详细报错和未压缩代码方便你调试排查问题，生产模式(production)则通过压缩混淆、剔除无用代码并关闭所有警告来大幅减小体积，让用户加载飞快。**
>- **开发环境**（`development`）：`publicPath` 设为 `'/'`，表示资源从站点根目录加载，适合本地开发（`localhost:8080`）。
>- **生产环境**（`production`）：`publicPath` 设为 `'/仓库名/'`（例如 `'/CloudPlatform/'`），这里“仓库名”通常指 **GitHub 仓库的名称**，因为很>多项目会部署到 GitHub Pages，而 GitHub Pages 的访问地址是 `https://<用户名>.github.io/<仓库名>/`，所以资源必须加上仓库名前缀才能正确加载。
>
>5. 为什么注释强调“前后斜杠不能少”？
>
>- `publicPath` 的值必须**以斜杠开头和结尾**。
>  - **前导斜杠**：表示绝对路径（从域名根开始），例如 `/CloudPlatform/` 表示从 `https://xxx.github.io/CloudPlatform/` 开始。
>  - **末尾斜杠**：表示这是一个目录，确保路径拼接时正确，比如 `/CloudPlatform/js/app.js` 而不是 `/CloudPlatformjs/app.js`（缺少斜杠会导致路径错>误）。
>- 如果部署在子路径下，末尾斜杠尤为重要，否则可能会出现资源 404 或路由匹配异常。
>
>6. 对其他配置的影响
>
>- **Vue Router 的 `base` 选项**：如果你使用了 Vue Router 的 **history 模式**，还需要同步设置路由的 `base` 选项为同样的值（如 `/仓库名/`），否>则刷新页面时路由会 404。
>- **开发代理**：开发环境下 `publicPath` 为 `/`，所以不需要额外配置，但若后端接口代理了，要注意路径冲突。
>
>7. 更灵活的配置方式
>
>有些项目会根据环境变量（如 `VUE_APP_PUBLIC_PATH`）动态设置，例如：
>
>```js
>publicPath: process.env.VUE_APP_PUBLIC_PATH || '/'
>```
>
>这样可以在构建时通过 `.env` 文件或命令行参数覆盖，而不用硬编码仓库名。
>
>8. 总结
>
>- 这段配置的核心目的是**适配不同环境的部署路径**。
>- 开发时用根路径，方便调试；生产时加上仓库名，适配 GitHub Pages 等子路径部署。
>- 正确配置 `publicPath` 是确保打包后应用能正常运行的关键一步，尤其对于单页应用，所有资源请求都必须基于这个基础路径。
</details>


**② 配置 `package.json`（添加 homepage 和 deploy 命令）**

```json
{
  "homepage": "https://用户名.github.io/仓库名",
  "scripts": {
    "deploy": "gh-pages -d dist"
  }
}
```

<details>
<summary>解析</summary>

> [!NOTE]
> 1. `"homepage": "https://用户名.github.io/仓库名"`
> - **作用**：给项目贴上一个“线上地址”的标签。它主要被 `gh-pages` 插件读取，用来确认最终要部署到的具体网址。
> - **关键关联**：这个网址中的 **`/仓库名`** 部分，**必须**和你在 `vue.config.js` 里配置的 `publicPath: '/仓库名/'` **保持完全一致**。否则部署上去后，页面会白屏或资源 404。
> 2. `"deploy": "gh-pages -d dist"`
> - **作用**：这是你敲 `npm run deploy` 时实际执行的命令。
> - **拆解**：`gh-pages` 是一个 Node 插件，`-d dist` 的意思是“把 `dist` 文件夹（你执行 `npm run build` 后生成的打包文件）里的所有内容，推送到你 GitHub 仓库的 `gh-pages` 分支上”。
>3. 一键部署流程（串起来）
当你在终端依次执行：
>  1. `npm run build` → 根据 `production` 模式，生成带有 `/仓库名/` 路径的静态文件到 `dist` 文件夹。
>  2. `npm run deploy` → 执行这段脚本，把 `dist` 里的文件推送到 GitHub 的 `gh-pages` 分支。
>  3. GitHub Pages 会自动读取该分支并托管，最终用户通过 `homepage` 里的地址访问。
>
>**简单一句话**：`homepage` 是告诉插件“要发到哪”，`deploy` 脚本是“实际动手发送”的指令。两者配合 `publicPath`，保证发上去的文件路径都能找得到。
</details>

### ❌ 踩坑 3：package.json 格式错误（对象重复）

直接将 `homepage` 和 `scripts` 写在第二个 `{}` 里，导致 JSON 解析失败。
**修复**：必须合并到最外层的唯一大括号 `{}` 中。

### ❌ 踩坑 4：`npm run deploy` 显示 "Published" 但远程无分支

执行后终端显示成功，但 `git branch -r` 看不到 `origin/gh-pages`。
**原因**：`gh-pages` 包可能存在网络或内部解析问题，导致实际未推送。
**修复（Windows 环境）**：放弃 `gh-pages` 包，改为**手动推送**：

```bash
# 1. 复制 dist 到临时目录
Copy-Item -Recurse cloud-platform-frontend/dist temp-deploy
cd temp-deploy

# 2. 初始化为 Git 仓库并强制推送到远程的 gh-pages 分支
git init
git add .
git commit -m "Deploy to GitHub Pages"
git remote add origin https://github.com/用户名/仓库名.git
git push origin HEAD:gh-pages --force   # 关键：强制覆盖

# 3. 删除临时目录
cd ..
Remove-Item -Recurse -Force temp-deploy
```

### ❌ 踩坑 5：GitHub Pages 设置 404 且无权限

打开设置页面提示 404 或 `You don't have access to repository options`。
**原因**：该仓库属于组织或其他协作者，我不是仓库所有者，没有 Settings 管理权限。
**修复**：联系仓库所有者，在仓库 `Settings -> Pages` 中，将 **Branch** 改为 `gh-pages`，文件夹选 `/ (root)`，点击 **Save**。等待 1-3 分钟生效。

---

## 5. 后续更新与协作方式

部署成功后，访问地址为：`https://用户名.github.io/仓库名`

### 🔄 如何更新代码？

- **方式一（推荐）**：让仓库所有者给我的 GitHub 账号添加 **Write** 权限。以后我修改代码后，只需在本地执行 `npm run build && npm run deploy`，线上网站自动更新。
- **方式二**：我只负责提交源码到 `main` 分支，由仓库所有者手动拉取并执行打包部署。

---

## 🎤 面试官可能会追问的技术问题（补充）

### 1. 为什么要设置 `publicPath: '/仓库名/'`？

**答**：GitHub Pages 不是部署在域名根目录下，而是子目录（即仓库名）。如果不设置，打包后的 JS、CSS 会从根目录 `/js/...` 加载，导致 404。设置后，资源路径会带上 `/仓库名/` 前缀，确保资源加载正确。

### 2. SPA（单页面应用）刷新页面为什么 404？怎么解决？

**答**：SPA 只有 `index.html` 一个入口，`history` 模式下，刷新 `/about` 时，服务器去查找 `/about` 文件，找不到就会 404。
**解决方案**：

- **简单方案**：Vue Router 改用 `hash` 模式（URL 带 `#`）。
- **正规方案**：若保持 `history` 模式，需配置 Nginx 将所有 404 请求指向 `index.html`（`try_files $uri $uri/ /index.html;`）。但由于 GitHub Pages 不支持自定义服务端配置，通常建议使用 Hash 模式。

### 3. 打包文件太大（1.68 MiB）怎么优化？

**答**：

- **路由懒加载**：使用 `() => import('@/views/xxx.vue')` 按需加载页面。
- **CDN 引入**：将 Vue、Element Plus 等大库通过 CDN 引入，不打包进 `vendor`。
- **Gzip 压缩**：在 Nginx 服务器开启 `gzip on;`，传输体积可减少 70% 以上（构建时已有 Gzip 报告，原始 1.3MB -> Gzip 后约 400KB）。

### 4. `docker build` 命令中的 `.` 代表什么？

**答**：代表 **构建上下文（Build Context）**。Docker 会将当前目录下的所有文件（根据 `.dockerignore` 过滤）发送给 Docker 守护进程进行构建。如果不加 `.`，Docker 不知道去哪里找 `Dockerfile` 和需要复制的 `dist` 目录。

### 5. 为什么选择 `nginx:alpine` 作为基础镜像？

**答**：`alpine` 版本基于 Alpine Linux，体积非常小（仅 5MB 左右），安全性高，且包含了 Nginx 核心功能，非常适合前端静态资源的部署，能显著减小最终镜像的体积，提升拉取和启动速度。

---
