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

遇到 `Parameter 'studentName' not found` 时，先核对 `@Param("studentName")` 与 XML 中的 `#{studentName}` 是否一致，并查看异常给出的可用参数名。

参数命名规则与错误示例见第 5—7 题。

---

## 26. `Unknown column` 优先检查真实数据库结构

遇到 `Unknown column 'c.name'` 时，先用 `DESC class;` 核对实际表结构和 SQL 中的表别名、列名；不要先怀疑 Java 结果映射。

本例的实际字段是 `class_name`，完整踩坑场景见第 23 题。

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

❌ **错误理解：** 查询结果依次经过“数据库 → Mapper XML → TypeHandler → Java 对象”。

✅ **正确区分：**

| 组件 | 职责 |
|---|---|
| Mapper XML | 定义 SQL 与映射配置，不是结果数据流经的转换器 |
| TypeHandler | 处理参数写入、结果读取时的 Java ↔ JDBC 类型转换 |

例如，查询由 XML 定义，JDBC 执行后返回 `ResultSet`；读取 `gender` 列时，TypeHandler 可以把 `"M"` 转成 `Gender.MALE`，再用于映射 `Student.gender`。

### 补充：`#{}` 是参数绑定，不是字符串替换

```text
XML 中的 WHERE age = #{age}
        ↓
SQL 使用 WHERE age = ?
        ↓
TypeHandler 将 Java 参数交给 PreparedStatement.setInt(..., 18)
        ↓
JDBC 执行
```

TypeHandler 不负责把 XML 中的 `#{age}` 替换成文本 `18`，而是按 JDBC 类型绑定参数值。

---

## 33. `rollback()` ≠ SQL 没有执行

❌ **错误理解：** 最后调用 `rollback()`，前面的 SQL 就没有执行。

```java
setAutoCommit(false); // SQL 仍执行，只是不在每条语句后自动提交
updateA();
updateB();
rollback(); // 撤销当前事务中已执行、尚未提交的修改
```

**SQL 执行 ≠ 事务提交。** 回滚不代表 SQL 从未执行；判断最终结果时，要区分执行、提交和回滚。

---

## 34. 事务异常传播与 `@Transactional` 回滚判断

**判断前提：** 事务方法通过 Spring 代理调用。以下讨论运行时异常；SQL 是否执行与是否提交的区别见第 33 题。

### ① 异常在事务方法内部被捕获

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

上例中，异常由普通代码产生并在方法内被捕获，方法正常返回；若事务没有被其他因素标记为回滚，A、B 通常会提交。**共用 Connection 不代表出错后一定回滚。**

### ② 异常离开事务方法后，才被外层捕获

```java
@Transactional
public void transfer() {
    studentMapper.updateScoreA();
    studentMapper.updateScoreB(); // 假设此处抛出运行时异常
}
```

```java
try {
    service.transfer(); // 通过 Spring 事务代理调用
} catch (Exception e) {
    System.out.println("捕获异常");
}
```

异常已经经过事务代理，Spring 按回滚规则处理后才继续向外抛出。调用方随后 `catch`，不会撤销已经发生的回滚。

**特别注意：** 内层事务代理也可能先把共享事务标记为 `rollback-only`；这时即使外层方法内部捕获异常，仍不能正常提交，见第 35 题。

**事务边界：** `@Transactional` 的核心是划定事务边界，让参与该事务的操作统一提交或回滚。共用 Connection 是典型实现机制，不能替代对异常传播与回滚规则的判断。

---

## 35：REQUIRED + 内层异常 + 外层 catch 的回滚判断

### 题目与前提

`methodA()` 通过 Spring Bean 调用；`methodB()` 位于另一个 Bean 中，确实经过事务代理，使用默认传播行为 `REQUIRED`。

```java
@Transactional
public void methodA() {
    updateA();
    try {
        innerService.methodB(); // 跨 Bean 调用，经过内层事务代理
    } catch (Exception e) {
        System.out.println("B失败");
    }
}
```

```java
// 另一个 Spring Bean 中的方法
@Transactional
public void methodB() {
    updateB();
    throw new RuntimeException();
}
```

**问题：** 外层捕获异常后，A、B 提交还是回滚？

### 正确答案与原因

**A、B 都回滚。**

```text
methodA 开启事务 T1
        ↓
methodB 的 REQUIRED 加入 T1
        ↓
运行时异常经过内层事务代理
        ↓
共享事务 T1 被标记为 rollback-only
        ↓
methodA 捕获异常并正常结束
        ↓
T1 仍不能提交，最终回滚
```

`catch` 能阻止异常继续传播，**不能自动清除已有的 `rollback-only` 标记**。

### 与第 34 题的区别

- **普通代码抛出异常后直接被方法内部捕获**：事务代理可能看不到异常，通常可以提交。
- **异常先经过内层事务代理，再被外层捕获**：共享事务已被标记回滚，外层吞掉异常也无法恢复提交。

判断时先看内层调用是否经过事务代理、是否加入外层事务，以及事务是否已被标记回滚；不能只看“最后有没有 `catch`”。

---

## 36. `keyProperty` 对应 Java 属性名，不是数据库列名

❌ **错误理解：** 数据库主键列叫 `id`，`keyProperty` 就必须写 `id`。

✅ **正确理解：** `keyProperty` 填写接收主键的 **Java 属性名**。例如：

```java
public class Student {
    private Integer studentId;
    private String name;
}
```

```xml
<insert id="insertStudent"
        useGeneratedKeys="true"
        keyProperty="studentId">
    INSERT INTO student (name)
    VALUES (#{name})
</insert>
```

即使数据库主键列叫 `id`，也应回填到 `Student.studentId`，所以使用 `keyProperty="studentId"`。主键获取与回填机制见第 37 题。

---

## 37. `useGeneratedKeys` 与 `keyProperty` 的职责不同

**易错点：** 把“获取数据库生成的主键”与“指定 Java 接收属性”混为一谈。

| 配置 | 职责 |
|---|---|
| `useGeneratedKeys="true"` | 启用 JDBC 获取数据库生成的主键 |
| `keyProperty="studentId"` | 指定将主键回填到 Java 对象的哪个属性 |

```text
Java Student 对象 → JDBC 执行 INSERT → MySQL 生成主键
        → JDBC 获取生成值 → MyBatis 回填 Student.studentId
```

数据库负责生成主键，MyBatis/JDBC 负责获取并回填，数据库不会直接修改 Java 对象。`MAX(id) + 1` 的误解见第 10 题，属性名与列名的区别见第 36 题。

---

## 38：Spring Boot 与 JUnit 测试环境变量不一致，导致 MyBatis-Plus 数据库连接失败

**问题场景：** `JdbcTemplate` 已能连接 MySQL，但 JUnit 中的 `@SpringBootTest` 调用 `BaseMapper.selectById()` 失败：

```text
CannotGetJdbcConnectionException: Failed to obtain JDBC Connection
Caused by: java.sql.SQLException:
Access denied for user 'dev'@'localhost' (using password: YES)
```

`application.yml` 使用：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/school
    username: dev
    password: ${DB_PASSWORD}
```

**实际原因：** 只在 IDEA 的 Spring Boot Application 运行配置中设置了 `DB_PASSWORD`，JUnit 使用独立配置，没有自动继承该变量，因而未获得正确密码。

**解决与验证：**

1. 打开 `Run → Edit Configurations`，选中 `StudentMapperTest` 的 JUnit 配置。
2. 在 `Environment variables` 中添加 `DB_PASSWORD=实际数据库密码`，保存并重跑。
3. 使用查询验证连接：

   ```java
   @Test
   public void testSelectById() {
       Student student = studentMapper.selectById(1);
       System.out.println(student);
   }
   ```

修正后查询成功，输出了对应学生记录。

**保留的排错要点：**

- 查看最底层 `Caused by`；`Access denied` 优先检查账号、密码、实际运行配置和 MySQL 账号匹配。
- `using password: YES` 只表示提供了密码，不代表密码正确。
- `${DB_PASSWORD}` 通过 Spring 配置解析取值，可以来自环境变量；不要把真实密码提交到 Git。
- 数据库工具或另一运行配置连接成功，不代表当前 JUnit 配置也正确。

---

## 39：区分 Java 中的 null 对象引用与对象属性为 null

**错误理解：** 查询不到学生时，打印对象和调用对象的 getter 都只会输出 `null`。

```java
Student student = studentMapper.selectById(99999); // 假设该主键不存在，返回 null
System.out.println(student);           // 输出 null
System.out.println(student.getName()); // 抛出 NullPointerException
```

`student == null` 表示没有指向实际对象，不能调用实例方法。它与“对象存在，但属性值为 `null`”不同：

```java
Student student = new Student();
student.setName(null);
System.out.println(student.getName()); // 输出 null：对象存在，可以正常调用 getter
```

**正确处理：** 先检查查询结果，再访问属性。

```java
Student student = studentMapper.selectById(99999);
if (student != null) {
    System.out.println(student.getName());
} else {
    System.out.println("学生不存在");
}
```

实际业务也可按需求返回空结果、抛出业务异常，或通过 HTTP 404 表示资源不存在。

---

## 40：理解 MyBatis-Plus 中 Lambda 参数 `w` 的来源及其与外部 `wrapper` 的关系

**错误理解：** 没有提前定义 `w` 就不能写 `w ->`，或者 `w` 是外部 `wrapper` 的别名、自动缩写。

### ① 参数在 Lambda 中声明，由 MP 传入对象

`and()` 的方法签名可以简化理解为：

```java
and(Consumer<Children> consumer)
```

`Consumer<T>` 接收一个 `T` 类型的参数，执行操作，不要求返回结果。**`w ->` 本身就声明了形参**；类似普通方法的 `Student s`，不需要在外部提前定义。

调用 `and(w -> ...)` 时，MP 创建嵌套条件构造器，传给 Lambda 的 `w`，执行内部条件构造，再将结果作为括号分组接到外层。**`w` 接收的嵌套构造器与外部 `wrapper` 不是同一个对象。**

### ② 用一个完整例子区分外部与内部条件

需求：查询二班学生，并满足“年龄大于 19 岁”或“成绩达到 95 分”中的任一条件。

```java
QueryWrapper<Student> wrapper = new QueryWrapper<>();

wrapper.eq("class_name", "二班") // 外部条件
       .and(w -> w.gt("age", 19) // w 负责括号内的条件
                  .or()
                  .ge("score", 95));

List<Student> students = studentMapper.selectList(wrapper);
```

```sql
WHERE class_name = '二班'
  AND (age > 19 OR score >= 95)
```

`wrapper` 负责整体条件，`w` 负责内部条件；`and(w -> ...)` 把内部条件用括号分组，通过 `AND` 连接到外部。

### ③ 参数名可改，但不能与外围局部变量重名

下面是同一段 Lambda 的两种替代写法：

```java
wrapper.and(w -> w.gt("age", 19));
wrapper.and(nested -> nested.gt("age", 19));
```

如果外部已经定义局部变量 `wrapper`，下面会编译失败：

```java
wrapper.and(wrapper -> wrapper.gt("age", 19)); // 与外围局部变量重名
```

遇到 `.and(w -> ...)`、`.or(w -> ...)`、`.nested(w -> ...)` 时，都应从 Lambda 形参声明、调用方传参和嵌套条件构造来理解，不能把 `w` 当作外部变量的别名。

---
