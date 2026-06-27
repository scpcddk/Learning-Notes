# Shell 脚本学习笔记（精简实用版）

> 本笔记面向**后端开发者**，聚焦最常用的 Shell 语法和场景，无需深入所有细节

---

## 1.认识shell

### 1.1什么是shell

- Shell 是一个用 C 语言编写的程序，是用户使用 Linux 的桥梁。Shell 既是一种命令语言，又是一种程序设计语言
- Shell 是指一种应用程序，这个应用程序提供了一个界面，用户通过这个界面访问操作系统内核的服务

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
#!/bin/bash          # 告诉系统用 Bash 解释器
```

---

### 2.2 **变量**

```bash
name="ClashRoyale"   # 等号两边不能有空格
echo $name           # 使用变量加 $
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
| `$@` | **所有参数** |
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
echo ${#str}          # 输出长度：5
echo ${str:1:2}       # 从下标1截取2个：el
```

- **单引号**:字符会**原样输出**，里面的**变量**是**无效**的,不能出现单独一个的单引号（对单引号使用转义符后也不行）
- **双引号**:里面**可以有变量**,可以出现转义字符
- **拼接字符串**:

  ```bash
  your_name="runoob"
  # 使用双引号拼接
  greeting="hello, "$your_name" !"
  greeting_1="hello, ${your_name} !"
  echo $greeting  $greeting_1
  
  # 使用单引号拼接
  greeting_2='hello, '$your_name' !'
  greeting_3='hello, ${your_name} !'
  echo $greeting_2  $greeting_3
  
  输出结果为：
  hello, runoob ! hello, runoob !
  hello, runoob ! hello, ${your_name} !
  ```

---

### 2.5 数组

```bash
arr=("apple" "banana" "orange")
echo ${arr[0]}        # 第一个元素
echo ${arr[@]}        # 所有元素
echo ${#arr[@]}       # 数组长度
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
  | `[ -z str ]` | 字符串长度为0 |
  | `[ -n str ]` | 字符串长度非0 |
  | `[ str1 = str2 ]` | 字符串相等 |
  | `[ a -eq b ]` | 整数相等（-ne, -gt, -lt, -ge, -le） |
  | `[ condition1 -a condition2 ]` | 与运算（-o 或） |

- 示例：

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
    echo $i
done

# 遍历文件
for file in *.txt; do
    echo $file
done
```

---

### 3.3 while 循环

```bash
count=1
while [ $count -le 5 ]; do
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
  ls -l | grep ".jar"
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

### 6.2 查找并杀死进程

```bash
PID=$(ps -ef | grep "my-app.jar" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
    kill -9 $PID
fi
```

---

### 6.3 实时查看日志并过滤

```bash
tail -f app.log | grep ERROR
```

---

### 6.4 批量替换文件内容

```bash
sed -i 's/old/new/g' *.java
```

---

## 7. 调试与安全

- **调试模式**：`bash -x script.sh` 逐行执行并显示变量值
- **严格模式**：在脚本开头加 `set -e`（遇到错误退出）和 `set -u`（使用未定义变量时报错）
- **避免注入**：使用 `"$var"` 双引号包裹变量

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
| 2 | 误用 Shell 命令 |
| 126 | 命令不可执行 |
| 127 | 命令未找到 |
| 130 | 通过 Ctrl+C 终止 |

---

**参考链接**：[https://www.runoob.com/linux/linux-shell.html]
