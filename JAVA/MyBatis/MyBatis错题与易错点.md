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
