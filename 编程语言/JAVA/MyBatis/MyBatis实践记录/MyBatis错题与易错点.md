# MyBatis 错题与易错点

> 只记录容易混淆、曾经理解错误、实际踩过坑、以后需要重点避免的知识点。
>
> 不重复记录完整知识讲解。
>
> 本错题本基于 MyBatis 第一轮学习、实战、排错与综合复盘整理。

---

## 1. MyBatis 不是“自动把 SQL 写出来”

❌ 容易产生的误解：

> MyBatis 会根据 Mapper 方法自动生成 SQL。

✅ 正确理解：

> MyBatis 主要负责 Java 与 SQL 之间的映射和执行；原生 MyBatis 中，SQL 通常由开发者在 XML 或注解中定义。

**易错点：**

Mapper 接口只是声明：

```java
selectById()
```

真正执行什么 SQL，需要找到对应的 SQL 映射。

---

## 2. Mapper 接口 ≠ Mapper XML

❌ 错误理解：

> Mapper 接口本身就包含 SQL。

✅ 正确理解：

```text
Mapper 接口
→ 定义 Java 方法

Mapper XML
→ 定义 SQL

MyBatis
→ 把二者关联起来
```

**易错点：**

Mapper 接口没有方法体并不代表没有实现。

MyBatis 会在运行时生成 Mapper 的代理实现。

---

## 3. `namespace` 是 Mapper 的全限定名

❌ 容易混淆：

> namespace 写 Mapper 的简单类名即可。

例如错误：

```xml
<mapper namespace="StudentMapper">
```

✅ 正确：

```xml
<mapper namespace="org.example.mybatis1.mapper.StudentMapper">
```

**易错点：**

必须与 Mapper 接口的**全限定类名**一致。

---

## 4. `@MapperScan` 与 `mapper-locations` 负责不同事情

例如：

```yaml
mybatis:
  mapper-locations: classpath:mapper/*.xml
```

负责：

> 找到 XML Mapper 文件。

而：

```java
@MapperScan("org.example.mybatis1.mapper")
```

负责：

> 扫描 Mapper 接口。

可以记成：

```text
@MapperScan
→ 找 Java Mapper

mapper-locations
→ 找 XML Mapper
```

---

## 5. `@Param` 的核心作用是“给参数命名”

❌ 错误理解：

> `@Param` 只是让参数匹配得更加精确。

✅ 正确：

> `@Param` 给 Mapper 方法参数指定 MyBatis 可以使用的明确名称。

例如：

```java
@Param("name") String name
```

对应：

```xml
#{name}
```

---

## 6. 多参数没有 `@Param` 时，不要随便写参数名

曾经遇到：

```java
List<Student> selectStudent(String name, Integer age);
```

XML：

```xml
#{name}
#{age}
```

结果：

```text
Parameter 'name' not found.
Available parameters are [arg1, arg0, param1, param2]
```

**易错点：**

多参数没有 `@Param` 时，MyBatis 可能使用：

```text
arg0
arg1
param1
param2
```

所以实际项目中，多参数 Mapper 方法使用 `@Param` 更清晰。

---

## 7. `#{xxx}` 中的名字必须能对应参数

例如：

```java
@Param("name") String name
```

不能写：

```xml
#{studentName}
```

否则可能出现：

```text
Parameter 'studentName' not found
```

正确：

```xml
#{name}
```

**核心记忆：**

```text
@Param("name")
        ↓
#{name}
```

---

## 8. INSERT 中 Java 属性和数据库字段不要混淆

例如数据库字段：

```text
class_name
```

Java 属性：

```text
className
```

如果没有对应配置，不能随便写：

```xml
#{class_name}
```

而 Java 对象属性是：

```xml
#{className}
```

**核心：**

```text
SQL column
→ class_name

Java property
→ className
```

---

## 9. `int` 并不专属于 UPDATE / DELETE

虽然常见：

```text
INSERT → int
UPDATE → int
DELETE → int
```

但：

```sql
SELECT COUNT(*)
```

也可以返回：

```java
int
```

因此：

> `int` 的具体含义取决于 SQL 和业务。

---

## 10. `useGeneratedKeys` ≠ `MAX(id) + 1`

❌ 错误理解：

> MyBatis 插入数据时通过最大 ID + 1 得到新 ID。

✅ 正确理解：

数据库负责生成自增主键。

```xml
useGeneratedKeys="true"
```

让 MyBatis/JDBC 获取数据库生成的 Key。

```xml
keyProperty="id"
```

指定：

> 把这个 Key 写回 Java 对象的 `id` 属性。

---

## 11. `resultType` ≠ “整体映射”

❌ 错误理解：

> resultType 是整体映射，resultMap 是一对一映射。

✅ 正确：

```text
resultType
→ 指定结果 Java 类型，通常进行自动映射

resultMap
→ 显式定义列 → 属性的映射关系
```

---

## 12. `property` 与 `column` 方向不要弄反

例如：

```xml
<result property="className" column="class_name"/>
```

其中：

```text
property
→ Java 属性

column
→ SQL 查询结果中的列
```

记忆：

```text
property → Java
column   → SQL
```

---

## 13. SQL 别名可以帮助自动映射

例如：

```sql
SELECT
    student_id AS id,
    student_name AS name,
    class_name AS className
```

可以让 SQL 查询结果的列名直接接近 Java 属性。

因此：

```text
SQL 别名
+
resultType
```

有时可以减少显式 `resultMap` 配置。

**易错点：**

不是所有字段名不同都必须使用 `resultMap`。

---

## 14. `<id>` 不只是“声明数据库主键”

例如：

```xml
<id property="id" column="student_id"/>
```

它标识的是 Java 对象的 ID 字段。

在复杂 JOIN / 嵌套结果映射中，它还帮助 MyBatis 判断对象身份。

**易错点：**

不要只记：

```text
<id> = 主键
```

还要记：

```text
<id> = 对象身份识别的重要依据
```

---

## 15. 所有 `<if>` 都不成立时可能变成全表查询

例如：

```xml
<where>
    <if test="name != null">
        AND name = #{name}
    </if>
</where>
```

如果：

```text
name == null
```

可能生成：

```sql
SELECT * FROM student
```

**易错点：**

动态 SQL 没有语法错误，不代表业务上就是安全的。

---

## 16. `<set>` 也存在“什么都没有”的问题

例如：

```xml
<set>
    <if test="name != null">
        name = #{name},
    </if>

    <if test="score != null">
        score = #{score},
    </if>
</set>
```

如果所有参数都是 `null`，就可能形成没有实际更新字段的 SQL。

**易错点：**

动态 UPDATE 必须考虑：

> 所有更新字段都没有提供怎么办？

---

## 17. 分页不依赖 ID 连续

例如数据库 ID：

```text
1
2
3
4
5
8
```

执行：

```sql
LIMIT 3, 3
```

仍然是：

> 跳过查询结果前 3 行，取后 3 行。

可能得到：

```text
4
5
8
```

**易错点：**

分页是针对**查询结果集的位置**，不是根据 ID 数值计算。

---

## 18. 分页查询最好明确 `ORDER BY`

例如：

```sql
SELECT *
FROM student
ORDER BY id
LIMIT #{offset}, #{pageSize}
```

**易错点：**

没有明确排序时，不应该依赖数据库返回的自然顺序来保证分页结果稳定。

---

## 19. Service 接口 ≠ Service 实现类

结构：

```text
StudentService
        ↓
StudentServiceImpl
        ↓
StudentMapper
```

接口：

```java
List<Student> selectPage(...);
```

实现：

```java
@Override
public List<Student> selectPage(...) {
    ...
}
```

**易错点：**

普通 `class` 中不能只声明没有方法体的方法：

```java
List<Student> xxx(...);
```

这种形式通常应该出现在：

```java
interface
```

中。

---

## 20. Service 可以做业务参数校验

例如：

```java
if (pageNum < 1 || pageSize < 1) {
    throw new RuntimeException(...);
}
```

这属于业务层逻辑。

同样：

```text
className == null
&& minScore == null
```

如果业务不允许无条件查询，也可以在 Service 层拦截。

---

## 21. `@PathVariable` 与 `@RequestParam` 不要混淆

路径参数：

```text
/students/2/3
```

使用：

```java
@PathVariable
```

查询参数：

```text
/students/search?pageNum=2&pageSize=3
```

使用：

```java
@RequestParam
```

---

## 22. `@RequestParam` 默认是必填参数

例如：

```java
@RequestParam("name") String name
```

如果 URL 不传：

```text
name
```

Spring 可能直接返回：

```text
400 Bad Request
```

如果业务上允许缺失：

```java
@RequestParam(
    value = "name",
    required = false
)
String name
```

---

## 23. 多表 JOIN 不要根据表名猜字段

曾经实际遇到：

```sql
c.name
```

但数据库实际是：

```text
class_name
teacher
room
```

导致：

```text
Unknown column 'c.name'
```

正确做法：

```sql
DESC class;
```

先确认真实结构。

**易错点：**

数据库设计和你脑中的“应该有这个字段”不是一回事。

---

## 24. SQL 别名可以解决字段名称冲突

例如：

```sql
s.id AS student_id,
s.name AS student_name,
c.class_name AS class_name
```

这样查询结果列名明确：

```text
student_id
student_name
class_name
```

然后：

```xml
<result property="id" column="student_id"/>
<result property="name" column="student_name"/>
<result property="className" column="class_name"/>
```

**易错点：**

多表 JOIN 中尽量避免直接依赖重复的：

```text
id
name
```

等模糊列名。

---

## 25. `Parameter 'xxx' not found` 优先检查参数名称

例如：

```text
Parameter 'studentName' not found
```

优先检查：

```text
@Param("studentName")
```

以及：

```text
#{studentName}
```

是否一致。

---

## 26. `Unknown column` 优先检查真实数据库结构

例如：

```text
Unknown column 'c.name'
```

优先：

```sql
DESC class;
```

检查字段。

**易错点：**

不要先怀疑 MyBatis 映射。

如果 MySQL 明确告诉你：

```text
Unknown column
```

首先就是 SQL 引用了不存在的列。

---

## 27. Mapper 代理可以共享 ≠ SqlSession 可以共享

❌ 容易混淆：

> `studentMapper` 可以被多个请求使用，所以它内部的 `SqlSession` 也可以被多个请求共享。

✅ 正确理解：

Spring 通常管理的是 **Mapper 代理对象**。多个请求可以调用同一个 Mapper 代理，但这不意味着它们共享同一个 SqlSession。

```text
请求 A ──→ Mapper代理 ──→ 当前调用对应的 SqlSession
请求 B ──→ Mapper代理 ──→ 当前调用对应的 SqlSession
```

**核心：**

```text
Mapper代理
→ 通常可以被多个请求使用

SqlSession
→ 不能简单地跨线程共享
```

---

## 28. `SqlSession` 不是线程安全的，不要用 MySQL 锁解决

❌ 容易产生的误解：

> 多个线程同时使用一个 SqlSession，是数据库并发问题，所以应该使用 MySQL 锁解决。

✅ 正确理解：

这是两个不同层次的问题：

```text
Java / MyBatis 对象层
        ↓
多个线程是否共享同一个 SqlSession
        ↓
线程安全问题
```

而：

```text
数据库层
        ↓
多个事务并发访问数据库数据
        ↓
行锁 / 表锁 / MVCC / 隔离级别
```

因此：

> **SqlSession 的线程安全问题首先通过正确的对象生命周期和线程隔离来解决，而不是依靠 MySQL 锁。**

---

## 29. Spring 管理 Mapper ≠ “Spring 管理所以天然线程安全”

❌ 容易产生的误解：

> Mapper 是 Spring Bean，所以 Mapper 的所有底层对象都天然线程安全。

✅ 正确理解：

关键不只是“Spring 管理”，而是 **Mapper 代理不会简单地永久持有一个供所有线程共享的 SqlSession**。

MyBatis-Spring 会协调 SqlSession 与当前调用、事务上下文。

```text
Spring管理 Mapper代理
        ↓
Mapper代理执行数据库操作
        ↓
MyBatis-Spring协调 SqlSession
        ↓
执行 SQL
```

**易错点：**

不要把：

> Spring 管理

直接等同于：

> 内部所有对象都是线程安全的。

---

## 30. SqlSession 线程安全 ≠ SQL/数据库并发安全

**题目：**
多个线程使用不同的 `SqlSession`，是否就能保证它们同时修改同一条数据库记录时不会产生并发问题？

**你的错误点：**
一开始忘记了这里还存在数据库层面的并发问题。

**正确理解：**

* **同一个 SqlSession 被多个线程使用** → Java/MyBatis **对象层面**的线程安全问题。
* **不同 SqlSession 同时操作同一条数据** → SQL/数据库**并发控制**问题。
* 不同 `SqlSession` 只能解决“不要共享同一个会话对象”，**不能解决数据库中的并发修改冲突**。
* 数据库并发问题需要结合 **事务、锁、隔离级别、MVCC** 等机制处理。

**一句话记忆：**

> **Session 隔离 ≠ 数据隔离；对象线程安全 ≠ 数据库并发安全。**

---

## 31. MyBatis 二级缓存无法自动感知外部数据库修改

* 易错理解： 只要数据库记录发生变化，MyBatis 就会自动清理对应缓存。

* 正确理解： 其他程序、服务或 SQL 脚本直接修改数据库时，MyBatis 无法自动感知，二级缓存可能继续保留旧数据，导致缓存与数据库不一致。

* 记忆关键： MyBatis 自身的缓存失效机制，不等于数据库级别的缓存一致性保障。

---

## 32. TypeHandler 与 Mapper XML 在执行链路中的职责不要混淆

❌ **易错理解：**

在查询结果转换过程中，把：

```text
数据库
→ Mapper XML
→ TypeHandler
→ Java 对象
```

看成一条直接转换链路。

✅ **正确理解：**

Mapper XML 与 TypeHandler 处于不同职责阶段。

**Mapper XML：**

```text
定义 SQL
↓
MyBatis 得到 SQL
↓
JDBC 执行
```

**TypeHandler：**

```text
SQL 参数写入：
Java 类型 → JDBC 类型

查询结果读取：
JDBC 类型 → Java 类型
```

例如查询：

```text
Mapper XML
    ↓
SELECT id, name, gender FROM student
    ↓
JDBC 执行
    ↓
MySQL 返回 ResultSet
    ↓
TypeHandler
    ↓
"M" → Gender.MALE
    ↓
Student.gender
```

**核心记忆：**

```text
Mapper XML
→ 定义 SQL

TypeHandler
→ 处理 Java ↔ JDBC 类型转换
```

不要把 Mapper XML 放进 TypeHandler 的“数据类型转换链”中。

### 补充：`#{}` 也不要理解成字符串替换

今天已经重新确认：

❌

```text
#{age}
→ 替换成 18
→ WHERE age = 18
```

✅

```text
#{age}
→ WHERE age = ?
→ TypeHandler 处理 Java 参数
→ PreparedStatement.setInt(..., 18)
→ JDBC 执行
```

因此：

```text
#{}
→ 参数占位 / 参数绑定

TypeHandler
→ Java ↔ JDBC 类型转换

Mapper XML
→ 定义 SQL
```

**`TypeHandler` 不负责把 `#{age}` 替换成 `18`，而是负责把 Java 参数按照对应的 JDBC 类型设置到 `PreparedStatement` 的 `?` 参数中**

---

## 33. `rollback()` ≠ SQL 没有执行

❌ **易错理解：**

```java
setAutoCommit(false);

updateA();
updateB();

rollback();
```

认为：

> `updateA()` 和 `updateB()` 都不会执行。

✅ **正确理解：**

```text
updateA()
    ↓
SQL 已经执行

updateB()
    ↓
SQL 已经执行

rollback()
    ↓
回滚当前事务中尚未提交的修改
```

### 核心记忆

```text
SQL 执行 ≠ 事务提交
```

`autoCommit=false` 的含义不是“不执行 SQL”，而是：

> SQL 仍然执行，但不会在每条 SQL 执行后自动提交。

因此：

```text
执行 SQL
    ↓
产生数据库修改
    ↓
尚未提交
    ↓
rollback()
    ↓
撤销修改
```

**一句话记忆：**

> `rollback()` 回滚的是**已执行但尚未提交的事务修改**，不是让 SQL 从未执行过。

---

## 34. 事务异常传播与 `@Transactional` 回滚判断

### ① SQL 执行 ≠ 事务提交

场景：

```java
@Transactional
public void transfer() {
    studentMapper.updateScoreA();
    studentMapper.updateScoreB();
}
```

如果 `updateScoreB()` 执行过程中抛出运行时异常：

❌ 错误理解：

> B 没有执行，所以回滚。

✅ 正确理解：

如果 B 已经执行到数据库并抛出异常，那么：

```text
A、B 都可能已经执行
        ↓
异常向外传播
        ↓
Spring 感知异常
        ↓
事务回滚
        ↓
A、B 尚未提交的修改都回滚
```

**核心：**

```text
SQL 执行 ≠ 事务提交 ≠ 最终数据库状态
```

### ② `try-catch` 的位置会影响事务回滚

场景：

```java
@Transactional
public void transfer() {
    studentMapper.updateScoreA();

    try {
        studentMapper.updateScoreB();
        throw new RuntimeException();
    } catch (Exception e) {
        System.out.println("出错了");
    }
}
```

❌ 错误理解：

> A、B 在同一个 Connection 中，所以一定回滚。

✅ 正确理解：

异常在 `@Transactional` 方法内部被捕获，并且没有继续向外抛出：

```text
异常被 catch
    ↓
@Transactional 方法正常返回
    ↓
Spring 默认认为事务正常结束
    ↓
commit
```

因此 A、B 通常都会提交。

### ③ 外层 `catch` 不等于事务不会回滚

场景：

```java
@Transactional
public void transfer() {
    studentMapper.updateScoreA();
    studentMapper.updateScoreB();
}
```

外层：

```java
try {
    service.transfer();
} catch (Exception e) {
    System.out.println("捕获异常");
}
```

❌ 错误理解：

> 最后异常被 catch，所以 A、B 都提交。

✅ 正确理解：

异常已经从 `transfer()` 向外传播，Spring 在事务方法返回前就已经感知到异常并执行回滚。

之后外层再 `catch`：

```text
@Transactional 方法
    ↓
RuntimeException
    ↓
Spring 感知
    ↓
rollback
    ↓
异常继续向外传播
    ↓
外层 catch
```

==**核心区别：**==

```text
事务方法内部 catch
→ Spring 可能看不到异常
→ 默认可能提交

事务方法外部 catch
→ Spring 已经看到异常
→ 已经执行回滚
```

### ④ `@Transactional` 的核心不是“共享 Connection”

❌ 不准确：

> `@Transactional` 的作用是让多个 Mapper 使用同一个 Connection。

✅ 更准确：

> **`@Transactional` 的核心作用是划定事务边界。**

在这个事务边界内：

```text
多个数据库操作
        ↓
参与同一个事务上下文
        ↓
最终统一 commit / rollback
```

同一个 Connection 是典型实现机制中的重要表现，但不是 `@Transactional` 最核心的定义。

**核心记忆：**

```text
@Transactional
→ 划定事务边界

事务边界内
→ 多个数据库操作参与同一事务

异常传播 + 回滚规则
→ 决定最终 commit 还是 rollback
```

---

## 35：REQUIRED + 内层异常 + 外层 catch 的回滚判断

### 题目

```java
@Transactional
public void methodA() {
    updateA();

    try {
        methodB();
    } catch (Exception e) {
        System.out.println("B失败");
    }
}
```

```java
@Transactional
public void methodB() {
    updateB();
    throw new RuntimeException();
}
```

假设：

* `methodA()` 通过 Spring Bean 正常调用
* `methodB()` **确实经过 Spring Proxy**
* `methodB()` 使用默认传播行为 `REQUIRED`

问题：

> `methodA()` 最终 catch 住 `methodB()` 的异常后，A、B 是提交还是回滚？

### 正确答案

> **A、B 都回滚。**

### 为什么？

#### ① `methodA()` 开启事务 T1

```text
methodA()
 ↓
事务 T1
 ↓
updateA()
```

#### ② `methodB()` 使用 `REQUIRED`

当前已经存在事务 T1：

```text
methodB()
 ↓
REQUIRED
 ↓
加入 T1
```

所以不是两个事务：

```text
❌ T1 → methodA
   T2 → methodB
```

而是：

```text
✅ T1
├── updateA()
└── updateB()
```

#### ③ `methodB()` 抛出 RuntimeException

```text
updateB()
 ↓
RuntimeException
 ↓
Spring 事务拦截器处理
 ↓
T1 被标记为 rollback-only
```

这是本题最关键的地方。

#### ④ `methodA()` 虽然 catch 住了异常

```java
catch (Exception e) {
    System.out.println("B失败");
}
```

但：

> [!warning]
> **catch 只能阻止异常继续向外传播，不能自动把已经被标记为 rollback-only 的事务恢复成可提交状态。**

因此：

```text
methodA()
 ↓
catch
 ↓
正常结束
 ↓
Spring 尝试 commit T1
 ↓
发现 T1 = rollback-only
 ↓
最终 rollback
```

所以：

```text
updateA() → 回滚
updateB() → 回滚
```

### 最容易混淆的地方

之前有一道题：

```java
@Transactional
public void transfer() {

    updateA();

    try {
        updateB();
        throw new RuntimeException();
    } catch (Exception e) {
    }
}
```

当异常只是**普通代码中产生并被直接 catch**，Spring 没有观察到向外传播的异常，因此通常可以正常提交。

而本题不同：

```text
methodA
 ↓
methodB
 ↓
Spring Proxy
 ↓
事务拦截器已经处理 RuntimeException
 ↓
共享事务被标记 rollback-only
 ↓
外层 catch
```

所以不能简单记成：

> **“异常被 catch → 一定提交”**

正确判断应该是：

```text
① methodB 是否经过 Spring 事务代理？
        ↓
② 是否加入了外层事务？
        ↓
③ 异常是否已经导致共享事务 rollback-only？
        ↓
④ 外层 catch 是否只是把异常吞掉？
        ↓
⑤ 最终提交时是否发现 rollback-only？
```

### 核心记忆

> **REQUIRED 共享同一个事务；内层事务异常可能把共享事务标记为 rollback-only，即使外层 catch 住异常，最终仍可能回滚。**

#### 一句话版

```text
REQUIRED + 同一事务 + 内层异常 → rollback-only → 外层 catch 也救不回来
```

---

## 36. `keyProperty` 对应 Java 属性名，不是数据库列名

❌ **错误理解：**

> `keyProperty` 应该填写数据库自增主键的列名。

例如，数据库主键列为 `id`，Java 对象属性为 `studentId`，就写 `keyProperty="id"`。

✅ **正确理解：**

`keyProperty` 指定的是接收生成主键的 **Java 对象属性名**。

```java
public class Student {
    private Integer studentId;
    private String name;
}
```

对应 XML：

```xml
<insert id="insertStudent"
        useGeneratedKeys="true"
        keyProperty="studentId">
    INSERT INTO student (name)
    VALUES (#{name})
</insert>
```

其中：

```text
数据库列名 → id
Java 属性名 → studentId
```

**易错点：**

不要混淆数据库字段与 Java 对象属性。即使数据库列名是 `id`，只要 Java 对象中接收主键的属性是 `studentId`，就应使用 `keyProperty="studentId"`。

---

## 37. `useGeneratedKeys` 与 `keyProperty` 的职责不同

❌ **错误理解：**

> `useGeneratedKeys` 负责使用自增主键，`keyProperty` 具体回填字段，但不清楚中间机制。

✅ **正确理解：**

```text
useGeneratedKeys="true"
→ 启用 JDBC 获取数据库生成的主键

keyProperty="studentId"
→ 指定主键回填到 Java 对象的哪个属性
```

完整过程：

```text
Java Student 对象
        ↓
MyBatis / JDBC 执行 INSERT
        ↓
MySQL 生成自增主键
        ↓
JDBC 获取生成的主键值
        ↓
MyBatis 将主键回填到 Student.studentId
```

**易错点：**

- 主键由数据库生成，不是 MyBatis 使用 `MAX(id) + 1` 生成。
- 数据库不会直接修改 Java 对象。
- MyBatis/JDBC 负责获取生成的主键，并将其回填到指定属性。

**核心记忆：**

```text
数据库生成
→ JDBC 获取
→ MyBatis 回填
→ Java 对象获得主键值
```

---

## 38：Spring Boot 与 JUnit 测试环境变量不一致，导致 MyBatis-Plus 数据库连接失败

**1. 问题场景**

在 Spring Boot + MyBatis-Plus 项目中，已经通过 `JdbcTemplate` 成功连接 MySQL：

```text
数据库连接测试：1
```

但使用 `@SpringBootTest` 测试 `BaseMapper.selectById()` 时，出现：

```text
CannotGetJdbcConnectionException:
Failed to obtain JDBC Connection

Caused by: java.sql.SQLException:
Access denied for user 'dev'@'localhost'
(using password: YES)
```

**2. 错误原因**

`application.yml` 使用环境变量配置数据库密码：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/school
    username: dev
    password: ${DB_PASSWORD}
```

此前只在 IntelliJ IDEA 的 **Spring Boot Application 运行配置**中设置了 `DB_PASSWORD`。

但是，`StudentMapperTest` 使用的是独立的 **JUnit 运行配置**，不会自动继承另一个运行配置中的环境变量。

因此，JUnit 测试没有获得正确的数据库密码，导致 MySQL 身份认证失败。

注意：`using password: YES` 只说明客户端提供了密码，不代表密码正确。

**3. 正确解决方法**

在 IntelliJ IDEA 中：

1. 打开 `Run → Edit Configurations`。
2. 选择 `StudentMapperTest` 对应的 JUnit 配置。
3. 找到 `Environment variables`（环境变量）。
4. 添加：

   ```text
   DB_PASSWORD=实际数据库密码
   ```

5. 保存配置，重新运行测试。

不要将真实数据库密码提交到 Git 仓库。

**4. 验证结果**

重新运行：

```java
@Test
public void testSelectById() {
    Student student = studentMapper.selectById(1);
    System.out.println(student);
}
```

成功输出：

```text
Student(id=1, name=张三, age=18, gender=男, score=95, className=一班)
```

说明 JUnit 测试已经可以通过 MyBatis-Plus 正常访问 MySQL。

**5. 核心知识点**

- Spring Boot Application 与 JUnit Test **可以使用不同的运行配置**。
- IDEA 中某个运行配置的环境变量，不会自动共享给其他运行配置。
- `${DB_PASSWORD}` 表示通过 Spring 属性解析机制获取对应配置值，可以来自环境变量等配置源。
- IDEA Database 工具连接成功，不代表 Spring Boot 或 JUnit 的数据源配置一定正确。
- `CannotGetJdbcConnectionException` 是上层异常，需要继续查看最底层的 `Caused by`。
- `Access denied` 应优先检查用户名、密码、运行环境变量和 MySQL 账号匹配情况。

**6. 排查流程**

```text
MyBatis 查询失败
      ↓
查看异常堆栈
      ↓
CannotGetJdbcConnectionException
      ↓
继续查找最底层 Caused by
      ↓
Access denied
      ↓
检查 application.yml
      ↓
检查实际运行配置中的 DB_PASSWORD
      ↓
修正 JUnit 环境变量
      ↓
重新运行，查询成功
```

**7. 本题教训**

**程序能正常启动、数据库工具能连接，不代表所有运行环境都能正确访问数据库。**

今后遇到数据库连接错误，应先检查底层异常，并确认**当前实际执行的运行配置**，不要直接认定是 MyBatis Mapper、SQL 或数据库服务的问题。

---

## 39：区分 Java 中的 null 对象引用与对象属性为 null

**1. 错误场景**

在 MyBatis-Plus 查询中执行：

```java
Student student = studentMapper.selectById(99999);

System.out.println(student);
System.out.println(student.getName());
```

假设数据库中不存在 `id = 99999` 的学生，`selectById()` 返回 `null`。

**错误理解：**

认为两条 `System.out.println()` 都会输出 `null`。

**2. 正确理解**

第一条：

```java
System.out.println(student);
```

输出：

```text
null
```

原因：`student` 是一个空引用，`System.out.println()` 可以直接打印空引用。

第二条：

```java
System.out.println(student.getName());
```

抛出：

```text
java.lang.NullPointerException
```

原因：`student == null`，没有指向实际对象，无法通过空引用调用 `getName()` 实例方法。

**3. 关键区别：对象为 null 与属性为 null**

情况一：对象本身为 `null`

```java
Student student = null;

System.out.println(student);          // 输出 null
System.out.println(student.getName()); // NullPointerException
```

情况二：对象存在，但属性为 `null`

```java
Student student = new Student();
student.setName(null);

System.out.println(student);           // 输出 Student(id=null, name=null, ...)
System.out.println(student.getName()); // 输出 null
```

第二种情况不会因为 `getName()` 返回 `null` 而抛出空指针异常，因为 **`student` 对象确实存在**。

**4. 对比总结**

| 代码 | 执行结果 |
|---|---|
| `System.out.println(student)`，对象为 null | 输出 `null` |
| `student.getName()`，对象为 null | 抛出 `NullPointerException` |
| `student.getName()`，对象存在但 name 为 null | 返回 `null` |
| `student != null`，对象为 null | `false` |
| `new Student()` | 创建真实对象，属性可以为 null |

**5. 正确处理方式**

对于可能返回 `null` 的查询：

```java
Student student = studentMapper.selectById(99999);

if (student != null) {
    System.out.println(student.getName());
} else {
    System.out.println("学生不存在");
}
```

实际业务中，可以根据需求选择返回空结果、抛出业务异常或通过 HTTP 404 表示资源不存在。

**6. 核心知识点**

- `null` 表示引用没有指向对象。
- `new Student()` 表示创建了真实对象，即使所有属性都是 `null`。
- `System.out.println(null)` 可以正常输出。
- 通过空引用调用实例方法会抛出 `NullPointerException`。
- MyBatis-Plus 的 `selectById()` 查询不到记录时，通常返回 `null`。
- 调用查询结果的方法之前，应考虑对象是否存在。

**7. 本题教训**

**对象本身为 `null`，与对象存在但内部属性为 `null`，是两种完全不同的情况。**

以后遇到可能返回空对象的数据库查询，先判断对象是否为 `null`，再访问其属性或调用实例方法。

---
