# WSL 终端文件下载与安装使用笔记（纯终端操作）

> 适用场景：在 WSL（Ubuntu）内部直接下载 Linux 安装包，无需打开 Windows 浏览器，所有操作在终端完成。

---

## 一、核心下载命令（Ubuntu 自带，无需安装）

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
curl -O https://example.com/package.zip

# curl 自定义名
curl -o mysql.deb https://example.com/mysql.deb
```

---

## 二、完整操作流程（以安装包为例）

1. **进入家目录**（保证文件存在 Linux 内部，读写速度快）
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
     sudo dpkg -i xxx.deb
     # 若提示缺依赖，执行修复
     sudo apt -f install
     ```

---

## 三、特殊情况处理

| 情形 | 解决方案 |
| ------ | ---------- |
| **网站需要登录/验证码/cookie** | `wget`/`curl` 无法直接下载，只能先用 Windows 浏览器下载，再通过方式1（复制文件到 WSL） |
| **下载中断或慢** | `wget -c 链接` 可断点续传；`curl -C - -O 链接` 类似 |
| **需要后台下载** | `wget -b 链接`（后台运行，日志写入 wget-log） |

---

## 四、系统软件一键安装（无需下载包）

对于系统仓库自带的软件，直接使用 `apt`，全程终端操作，更方便：

```bash
sudo apt update
sudo apt install git vim gcc make nodejs npm ...
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

执行后你会看到文件下载成功并列出压缩包内的前 5 个文件/目录，证明流程无误。

---

## 补充提醒

- 下载前确认链接是 **Linux 版本**，不要误下 Windows `.exe` 或 `.msi`。
- 若下载后权限不足，执行 `chmod +x 文件名` 赋予执行权限（针对二进制或脚本）。
- 推荐优先使用 `apt` 安装官方仓库软件，能自动处理依赖；第三方包再手动下载。
