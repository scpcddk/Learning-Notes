# WSL 终端文件下载与安装使用笔记（纯终端操作）

> 适用场景：在 WSL（Ubuntu）内部直接下载 Linux 安装包，无需打开 Windows 浏览器，所有操作在终端完成。

---

## 一、核心下载命令

是否预装取决于 Ubuntu/WSL 镜像。先用 `command -v wget`、`command -v curl` 检查；缺少时执行 `sudo apt update` 后再执行 `sudo apt install wget curl`。

下面的 `example.com` 链接和中文文件名是语法示意，需要替换为实际下载地址。

| 命令 | 特点 | 常用语法 |
| ------ | ------ | ---------- |
| **wget** | 简单直观，新手优先 | `wget 链接`（自动保留原名）<br>`wget 链接 -O 自定义名`（重命名） |
| **curl** | 功能更强大，支持更多协议 | `curl -O 链接`（大写 O，保留原名）<br>`curl -o 文件名 链接`（小写 o，自定义名） |

**示例：**
```bash
# wget 直接下载
wget https://example.com/jdk17-linux-x64.tar.gz

# wget 重命名
wget https://example.com/jdk17-linux-x64.tar.gz -O jdk.tar

# curl 保留原名
curl -fLO https://example.com/package.zip

# curl 自定义名
curl -fL -o mysql.deb https://example.com/mysql.deb
```

---

## 二、完整操作流程（以安装包为例）

1. **进入家目录**（默认通常位于 Linux 文件系统中；具体路径与性能取决于配置）
   ```bash
   cd ~
   ```

2. **复制官网提供的 Linux 版下载链接**，在终端执行 `wget` 下载
   ```bash
   wget https://xxx.com/package.tar.gz
   ```

3. **查看下载文件**
   ```bash
   ls
   ```

4. **解压或安装**
   - 解压 `.tar.gz`：
     ```bash
     tar -zxvf 文件名.tar.gz
     ```
   - 安装 `.deb` 包：
     ```bash
     sudo apt install ./xxx.deb
     # ./ 表示本地包；apt 会尝试从已配置的软件源获取所需依赖
     ```

---

## 三、特殊情况处理

| 情形 | 解决方案 |
| ------ | ---------- |
| **网站需要登录/验证码/cookie** | wget/curl 可通过认证参数或 Cookie 访问部分受保护资源；若流程依赖交互式登录、验证码或 JavaScript，可先用浏览器下载，再从 `/mnt/c/Users/你的用户名/Downloads/` 等位置复制到 WSL |
| **下载中断** | 服务器支持续传且远端内容未变时，可用 `wget -c 链接` 或 `curl -fL -C - -O 链接`；续传不保证提速 |
| **需要后台下载** | `wget -b 链接`（后台运行，日志写入 wget-log） |

---

## 四、从系统软件源安装（无需手动下载包）

对于系统仓库自带的软件，直接使用 `apt`，全程终端操作，更方便：

```bash
sudo apt update
sudo apt install git vim gcc make nodejs npm
```

---

## 五、小练习模板（直接套用）

```bash
# 1. 进入家目录
cd ~

# 2. 替换成你真实的 Linux 安装包链接
wget https://你的链接.tar.gz

# 3. 查看文件
ls

# 4. 解压或安装（按需）
tar -zxvf 下载的文件名.tar.gz
```

---

## 六、真实可测试的命令（复制即可运行）

> 下载一个公开的 Linux 小工具（`htop` 源码包）作为测试：
> 
```bash
cd ~
wget https://github.com/htop-dev/htop/archive/refs/tags/3.3.0.tar.gz -O htop.tar.gz
ls -lh htop.tar.gz
tar -tzf htop.tar.gz | head -5   # 仅查看内容，不实际解压
```

网络和远端资源可用时，执行后可看到下载文件及压缩包内的前 5 个条目。这里只测试下载与读取归档；源码包解压后仍需编译安装，不能视为已安装 htop。

---

## 补充提醒

- 下载前确认链接是 **Linux 版本**，不要误下 Windows `.exe` 或 `.msi`。
- 若二进制或脚本缺少执行权限，可用 `chmod u+x 文件名`；这不会解决架构不匹配、缺少解释器、依赖缺失或挂载点禁止执行等问题。
- 推荐优先使用 `apt` 安装官方仓库软件，能自动处理依赖；第三方包再手动下载。
