# 📘 npm 实用笔记

---

## 1. **核心文件解读**

| 文件 | 作用 | 是否提交 Git |
| :--- | :--- | :--- |
| **`package.json`** | 项目配置入口，记录**依赖范围**和**脚本命令** | ✅ 必须提交 |
| **`package-lock.json`** | 记录已解析的**精确版本号**和**依赖树**，提高安装可复现性；仍需匹配 Node/npm 版本、平台与安装配置 | ✅ 必须提交 |
| **`.npmrc`** | **npm 配置**文件（源地址、缓存路径等） | ⚠️ 可提交非敏感配置；令牌等凭证通过环境或本机配置注入 |
| **`node_modules`** | 实际**存放代码**的文件夹，体积巨大 | ❌ **绝不提交**（.gitignore 忽略） |

---

## 2. 高频命令大全（按场景分类）

### 📦 安装与卸载

| 命令 | 说明 |
| :--- | :--- |
| `npm init -y` | 快速生成默认`package.json` |
| `npm i` / `npm install` | ==根据 package.json 与可用的 lock 文件解析和安装依赖==；生产模式或 --omit=dev 等配置会省略开发依赖 |
| `npm i <包名>` | 安装生产依赖（默认写入`dependencies`） |
| `npm i <包名> -D` | 安装开发依赖（写入 `devDependencies`，如测试/打包工具） |
| `npm i <包名> -g` | 全局安装（命令行工具，如 `pm2`、`yarn`） |
| `npm uninstall <包名>` | 卸载依赖（自动移除 `package.json` 记录） |
| `npm ci` | 要求已有 lock 文件且与 package.json 一致；清理现有 node_modules 后安装，不改写 lock；常用于 CI/CD |

### 🚀 版本与更新

| 命令 | 说明 |
| :--- | :--- |
| `npm outdated` | 查看哪些依赖有可用更新 |
| `npm update` | 在版本范围和依赖约束允许的范围内更新；不等于无条件升级到所有最新版本 |
| `npm i <包名>@latest` | 无视版本限制，直接安装最新版 |
| `npm view <包名> versions` | 查看某个包的所有历史版本号 |
| `npm audit` | 检查依赖的安全漏洞 |
| `npm audit fix` | 尝试在允许的依赖范围内修复；仍需检查差异和运行测试，--force 可能越过版本范围并引入破坏性更新 |
| `npm ls <包名>` | 查看依赖树中某包的版本（厘清为什么安装它） |

### 🛠 脚本运行

| 命令 | 说明 |
| :--- | :--- |
| `npm run <脚本名>` | ==**执行** `package.json` 中 `scripts` 定义的命令== |
| `npm start` | 特殊脚本，可简写（无需 `run`） |
| `npm test` | 特殊脚本，可简写（无需 `run`） |
| `npx <包名>` | 执行本地包提供的命令；缺少对应包时可能提示下载并安装到 npm 缓存，不等于完全不安装 |

<details><summary>深入理解npm run</summary>

### 🧩 补充：深入理解 `npm run`

`npm run <脚本名>` 不只是执行一段字符串，它会做三件关键的事：

1.  **临时把 `node_modules/.bin` 加入系统 PATH**  
    这样就能直接调用项目本地安装的各种命令行工具（如 `webpack`、`eslint`、`vite`），而不需要全局安装
2.  **提供当前 npm 版本支持的脚本环境变量**<br>
    脚本内可直接使用 `$npm_package_name`、`$npm_package_version` 等变量
3.  **支持前置/后置钩子**  
    自动执行 `pre<script>` 和 `post<script>` 脚本

#### 🔧 常用技巧

**1. 传递参数**

给 `npm run` 传参需要用 `--` 隔开：

```bash
# 启动时指定端口
npm run dev -- --port 3000

# 只运行某个测试文件
npm run test -- --grep="login"
```

**2. pre / post 钩子**

在 `package.json` 中定义：

```json
"scripts": {
  "prebuild": "npm run lint",
  "build": "webpack --mode production",
  "postbuild": "echo Build success!"
}
```

运行 `npm run build` 时，会**自动先执行 `prebuild`，再执行 `build`，最后执行 `postbuild`**。

**3. 串行与并行运行多个脚本**

```bash
# 串行：先 lint 再测试
npm run lint && npm run test

# 并行（需要安装 npm-run-all）
npm i -D npm-run-all
# 然后
npm-run-all --parallel dev server
```

**4. 跨平台设置环境变量**

直接在脚本里写 `NODE_ENV=production` 在 Windows 上会报错。可用 `cross-env`：

```bash
npm i -D cross-env
```

```json
"scripts": {
  "build": "cross-env NODE_ENV=production webpack"
}
```

**5. 列出所有可用脚本**

```bash
npm run
```

会直接打印 `scripts` 里所有命令，比翻文件快。

**为什么你会觉得“好多命令都是 npm run”？**  
因为现代前端工程化的工具链（编译、打包、检查、测试、部署）全都通过 `scripts` 集中管理，最终入口就是 `npm run <任务名>`。这其实是一种**统一接口**，让团队不需要记忆工具的具体 CLI 参数。
</details>

---

## 3. 版本符号速查（语义化版本 Semver）
在 `package.json` 中，版本号格式为 `主版本号.次版本号.补丁号`（如 `2.5.1`）：

| 符号 | 含义 | 示例匹配规则 |
| :--- | :--- | :--- |
| `^2.5.1` | **兼容主版本**（最常用） | 通常允许 `>=2.5.1 <3.0.0` 的稳定版本 |
| `~2.5.1` | **兼容补丁版本** | 通常允许 `>=2.5.1 <2.6.0` 的稳定版本 |
| `>=2.5.1` | 大于等于该版本 | 任意高于 `2.5.1` 的版本 |
| `*` / `x` | 通配版本范围 | 单独 * 或 x 通常匹配任意稳定版本；已有 lock 时不会因此每次都安装最新版本 |

> `^` 保留最左侧非零版本位：`^0.2.1` 通常允许 `>=0.2.1 <0.3.0`，而 `^0.0.3` 只允许 0.0.3 的稳定版本；不能把所有 0.x.x 都理解成与 ~ 相同。预发布版本还有单独的匹配规则。

---

## 4. 国内环境优化（换源与代理）

### 查看当前源
```bash
npm config get registry
```

### 可选：切换 npmmirror 镜像
```bash
npm config set registry https://registry.npmmirror.com
```

### 恢复官方源
```bash
npm config set registry https://registry.npmjs.org
```

### 可选：使用 nrm 管理源
```bash
npm i -g nrm          # 安装
nrm ls                # 列出所有源
nrm use taobao        # 切换淘宝
nrm use npm           # 切回官方
```

---

## 5. 日常开发标准工作流（别搞乱顺序）

1. **拉取项目**：`git clone xxx`
2. **安装依赖**：`npm ci`（如果没 lock 文件则用 `npm i`）
3. **启动开发**：`npm run dev` 或 `npm start`
4. **新增依赖**：
   - 生产包（如 `axios`）：`npm i axios`
   - 开发包（如 `webpack`）：`npm i webpack -D`
5. **提交代码前**：确保 `package-lock.json` 的变更一起提交
6. **项目构建**：`npm run build`

---

## 6. 常见报错 & 快速自救

| 报错信息 | 大概率原因 | 解决方案 |
| :--- | :--- | :--- |
| `ERESOLVE unable to resolve dependency tree` | 依赖版本冲突（常见于 React/Vue 生态） | 先根据冲突报告核对 peerDependencies 和版本组合；--legacy-peer-deps 会忽略 peer 依赖约束，仅在明确原因时临时使用，不默认加 --force |
| `npm ERR! code EACCES` | 权限不足（Mac/Linux） | 按下方方法使用 Node 版本管理器或用户级全局目录；不要把递归修改系统目录所有权当作通用修复 |
| `npm install` 卡死/极慢 | 源被墙或缓存问题 | 先检查网络、registry 和代理，再运行 npm cache verify；缓存清理不是常规第一步 |
| `command not found: xxx`（本地包命令） | 环境变量未加载本地 bin | 使用 `npx <包名>` 执行（如 `npx webpack`），或 `./node_modules/.bin/xxx` |

### 🛠 权限问题进阶修复（一劳永逸）

- **方法一（推荐）**：使用 **nvm** 管理 Node 版本，彻底避免权限问题。
- **方法二**：重设 npm 全局安装目录到用户目录下：
  
  ```bash
  mkdir ~/.npm-global
  npm config set prefix ~/.npm-global
  # 然后将 ~/.npm-global/bin 加入 PATH（写入 .bashrc 或 .zshrc）
  ```

### 根据报错重新安装

```bash
npm cache verify
npm ci
```

上例要求已有且一致的 package-lock.json。若提示 lock 与 package.json 不一致，先确认依赖修改，再运行 npm install 并审查锁文件差异。不要把删除锁文件作为通用修复，否则可能改变整棵依赖树，掩盖原问题。

---

## 7. 极简发布自己的包（流程备忘）

1. 登录：`npm login`
2. 修改版本号：`npm version patch`（自动升补丁号）
3. 发布：`npm publish`
4. 撤包前先检查官方策略：新包发布未满 72 小时且没有其他 npm 公共包依赖它时通常可撤；超过 72 小时还需同时满足无包依赖、最近一周下载少于 300 次、只有一位所有者/维护者等条件。`npm unpublish <包名>@<版本>` 删除指定版本，删除整包另需 --force；该参数不能绕过撤包政策。
> 📌 注意：新包名需可用，发布现有包需具备权限；项目必须有 package.json，已发布的同一版本号不能复用。

---

> [!TIP]
> 💡 **终极建议**：尽量使用 `npm ci` 替代 `npm i` 用于部署环境；写脚本时多用 `||` 和 `&&` 组合命令（如 `npm run build && npm run test`）。将此笔记收藏，遇到问题时先对照第 6 条

核对依据：[npm install](https://docs.npmjs.com/cli/v11/commands/npm-install/)、[npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)、[node-semver](https://github.com/npm/node-semver#caret-ranges-123-025-004)、[npm 撤包策略](https://docs.npmjs.com/policies/unpublish/)。
