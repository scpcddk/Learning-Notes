# Shell 脚本学习笔记（精简实用版）

> 本笔记面向**后端开发者**，聚焦最常用的 Shell 语法和场景，无需深入所有细节

---

## 1.认识shell

### 1.1什么是shell

- Shell 是一类命令解释器，常见实现有 Bash、dash、Zsh；“Shell”并不限定实现语言。本文主要讲 **Bash** 语法，数组、`[[ ]]`、`&>` 等不能假定适用于所有 `sh`
- Shell 是指一种**应用程序**，这个应用程序提供了一个界面，用户通过这个界面**访问操作系统内核**的服务

---

### 1.2 为什么后端要学 Shell？

- **自动化部署**：写脚本一键打包、上传、重启服务
- **日志分析**：用`grep`、`awk`快速排查线上问题
- **批量测试**：循环调用接口、压测脚本
- **环境配置**：初始化服务器、安装依赖

> **不需要成为专家，掌握 20% 的核心语法就能解决 80% 的日常需求**

---

## 2. **基本语法**

### 2.1 Shebang

写在脚本第一行，行首无空格

```bash
#!/bin/bash
# 告诉系统用 Bash 解释器；说明文字另起一行
```

不要在 Shebang 行尾追加注释：Linux 可能将后面的文字当作解释器参数，导致 `./script.sh` 执行失败。

---

### 2.2 **变量**

```bash
name="ClashRoyale"   # 等号两边不能有空格
echo "$name"         # 使用变量加 $，加双引号避免分词与通配符展开
readonly VERSION=1.0 # 只读变量
unset name           # 删除变量
```

---

### 2.3 特殊变量

| 变量 | 含义 |
| ------ | ------ |
| `$0` | 脚本文件名 |
| `$1`~`$9` | 第1~9个参数 |
| `$#` | **参数个数** |
| `"$@"` | **所有参数**，每个原参数保持为独立参数 |
| `$?` | 上一条命令的退出状态（0成功，非0失败） |

示例：

```bash
#!/bin/bash
echo "脚本名: $0"
echo "第一个参数: $1"
echo "参数个数: $#"
```

---

### 2.4 字符串

```bash
str="Hello"
echo "${#str}"        # 输出长度：5
echo "${str:1:2}"     # 从下标1截取2个：el
```

- **单引号**:字符会**原样输出**，里面的**变量**是**无效**的,不能出现单独一个的单引号（对单引号使用转义符后也不行）
- **双引号**：仍会进行变量展开和命令替换；反斜杠只对部分字符有特殊作用，`\n` 不会自动变成换行，可用 `printf` 输出
- **拼接字符串**:

  ```bash
  your_name="runoob"
  # 使用双引号拼接
  greeting="hello, ""$your_name"" !"
  greeting_1="hello, ${your_name} !"
  printf '%s %s\n' "$greeting" "$greeting_1"
  
  # 使用单引号拼接
  greeting_2='hello, '"$your_name"' !'
  greeting_3='hello, ${your_name} !'
  printf '%s %s\n' "$greeting_2" "$greeting_3"
  
  # 输出结果为：
  # hello, runoob ! hello, runoob !
  # hello, runoob ! hello, ${your_name} !
  ```

---

### 2.5 数组

```bash
arr=("apple" "banana" "orange")
echo "${arr[0]}"      # 第一个元素
printf '%s\n' "${arr[@]}" # 所有元素，每个元素一行
echo "${#arr[@]}"     # 数组长度
```

---

## 3. 流程控制

### 3.1 if 条件判断

```bash
if [ condition ]; then
    commands
elif [ condition2 ]; then
    commands
else
    commands
fi
```

- **常用条件测试**（`test` 命令或 `[ ]`）：

  | 表达式 | 含义 |
  | -------- | ------ |
  | `[ -f file ]` | 文件存在且为普通文件 |
  | `[ -d dir ]` | 目录存在 |
  | `[ -z "$str" ]` | 字符串长度为0 |
  | `[ -n "$str" ]` | 字符串长度非0 |
  | `[ "$str1" = "$str2" ]` | 字符串相等 |
  | `[ a -eq b ]` | 整数相等（-ne, -gt, -lt, -ge, -le） |
  | `[ 条件1 ] && [ 条件2 ]` | 两个条件都成立；或运算用 `[ 条件1 ] \|\| [ 条件2 ]` |

- **示例**：

  ```bash
  if [ $# -eq 0 ]; then
      echo "请提供参数"
      exit 1
  fi
  
  if [ -f "/var/log/nginx/error.log" ]; then
      echo "日志文件存在"
  fi
  ```

---

### 3.2 for 循环

```bash
# 遍历列表
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# 使用 {start..end}
for i in {1..10}; do
    echo "$i"
done

# 遍历文件
for file in *.txt; do
    [ -f "$file" ] || continue  # 没有匹配时跳过字面量 *.txt
    echo "$file"
done
```

---

### 3.3 while 循环

```bash
count=1
while [ "$count" -le 5 ]; do
    echo "Count: $count"
    count=$((count + 1))
done
```

---

### 3.4 case 多分支

```bash
case $1 in
    start)
        echo "Starting..."
        ;;
    stop)
        echo "Stopping..."
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        ;;
esac
```

---

### 3.5 until 循环

until 循环执行一系列命令直至条件为 true 时停止

```bash
until condition
do
    command
done
```

---

## 4. 函数

```bash
# 定义函数
function greet() {
    echo "Hello, $1"
    return 0
}

# 调用函数
greet "World"
```

---

## 5. 输入/输出重定向

| 符号 | 含义 |
| ------ | ------ |
| `>` | **覆盖输出**到文件 |
| `>>` | **追加输出**到文件 |
| `2>` | **重定向错误**输出 |
| `&>` | **重定向所有**输出 |
| `<` | 从文件**读入** |
| `\|` | **管道**，前一个命令的输出作为后一个的输入 |

- 示例：

  ```bash
  echo "hello" > output.txt
  ./my.sh 2> error.log
  find . -maxdepth 1 -type f -name '*.jar'
  ```

---

## 6. **实用组合命令**

### 6.1 循环调用接口

```bash
for i in {1..10}; do
    curl http://localhost:8080/api/battles/1
    sleep 1
done
```

---

### 6.2 查找并请求终止进程

```bash
# 先查看匹配的 PID 和完整命令行，核对目标
pgrep -af 'my-app[.]jar'

# 将 1234 替换为确认后的目标 PID，优先请求正常退出
kill -TERM -- 1234
```

不要将模糊匹配得到的多个 PID 直接交给 `kill -9`；受服务管理器管理的程序优先用对应的停止服务命令。

---

### 6.3 实时查看日志并过滤

```bash
tail -f app.log | grep --line-buffered ERROR
```

---

### 6.4 批量替换文件内容

```bash
sed -i 's/old/new/g' *.java
```

---

## 7. 调试与安全

- **调试模式**：`bash -x script.sh` 逐行执行并显示变量值
- **错误处理**：`set -e` 会在部分失败场景退出，但 `if` 条件、`&&`/`||` 等场景有例外；管道默认只取最后一条命令的状态，Bash 可用 `set -o pipefail` 检查前面命令的失败。关键步骤仍应显式检查结果
- **未定义变量**：`set -u` 会使多数未定义变量展开报错；可选参数使用 `${1:-}` 等默认值
- **变量传参**：使用 `"$var"` 避免分词和通配符展开，必要时使用 `--` 分隔选项与文件名；这不等于能防止所有注入，避免将不可信输入传给 `eval` 或拼入 `sh -c`

---

## 8. 学习建议

- **先掌握 20 条常用命令**：`echo`, `cat`, `grep`, `awk`, `sed`, `ps`, `kill`, `curl`, `wget`, `tar`, `chmod`, `ls`, `cd`, `pwd`, `cp`, `mv`, `rm`, `mkdir`, `find`, `tail`
- **动手写**：把重复的手工操作写成脚本（例如启动 Spring Boot + 健康检查）
- **善用搜索引擎**：忘记语法时查 `bash for loop`、`bash if file exists` 即可

> **记住**：Shell 是工具，不是目的。当你在项目中遇到重复性工作时，自然就会想写脚本。那时再查笔记也不迟

---

## 附录：**常见错误码**

| 退出码 | 含义 |
| -------- | ------ |
| 0 | 成功 |
| 1 | 通用错误 |
| 2 | Bash 内置命令通常用它表示用法错误；其他程序可自行定义 |
| 126 | 命令不可执行 |
| 127 | 命令未找到 |
| 130 | 通过 Ctrl+C 终止 |

---

**参考链接**：[https://www.runoob.com/linux/linux-shell.html]

语义核对：[Bash 官方手册](https://www.gnu.org/software/bash/manual/bash.html)、[Linux execve(2)：解释器脚本](https://man7.org/linux/man-pages/man2/execve.2.html)。
