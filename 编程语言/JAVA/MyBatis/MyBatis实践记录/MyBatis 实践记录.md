# MyBatis 实践记录

---

## 一、Mapper 接口与 XML 映射

### 案例 001：Mapper 接口与 XML 实现数据库操作

> [!note] 实践信息
> - **技术**：原生 MyBatis、Mapper 接口、Mapper XML
> - **环境**：JDK 21、Spring Boot 3.3.13、MyBatis Starter 3.0.5、MySQL 8.0
> - **状态**：已完成基础实操，Spring Boot 集成后已验证 Mapper 能正常执行。
> - **说明**：以下代码为学习内容整理示例，并非逐字还原当时的源文件。

#### 1. 实践目标

学习在不直接编写 JDBC 操作代码的情况下，通过 Mapper 接口和 XML 映射文件完成数据库查询。

理解 Mapper 方法与 XML SQL 语句之间的对应关系。

#### 2. 关键代码

Mapper 接口：

```java
@Mapper
public interface StudentMapper {

    Student selectById(Integer id);

}
```

对应 XML：

```xml
<mapper namespace="org.example.mybatis1.mapper.StudentMapper">

    <select id="selectById"
            parameterType="java.lang.Integer"
            resultType="org.example.mybatis1.entity.Student">

        SELECT *
        FROM student
        WHERE id = #{id}

    </select>

</mapper>
```

关键映射关系：

| Java / XML | 作用 |
|---|---|
| `StudentMapper` | 定义数据库访问方法 |
| `namespace` | 对应 Mapper 接口全限定名 |
| `selectById` | 对应 XML 语句的 `id` |
| `#{id}` | 参数绑定 |
| `resultType` | 指定结果对象类型 |

#### 3. 遇到的理解问题

**问题一：接口没有实现类，为什么能够调用？**

```java
studentMapper.selectById(1);
```

MyBatis 会通过 Mapper 代理机制，为接口创建代理对象。

调用方法时，框架根据接口与方法信息定位对应 SQL 映射并执行。

**问题二：`namespace` 与 `id` 为什么重要？**

MyBatis 通常利用：

```text
namespace + "." + id
```

定位一条映射语句。

例如：

```text
org.example.mybatis1.mapper.StudentMapper.selectById
```

因此接口名称、方法名称与 XML 配置必须正确匹配。

#### 4. 实践结果

已完成：

- Mapper 接口与 XML 对应关系配置。
- XML 基础 CRUD 学习与操作。
- Mapper 代理原理理解。
- 在 Spring Boot 环境中执行真实数据库访问。

#### 5. 经验总结

> [!important] 实践结论
> 原生 MyBatis 的核心是将 Java 方法调用映射为 SQL 执行。Mapper 接口负责定义操作，XML 负责 SQL，Mapper 代理负责连接两者。

---

## 二、参数绑定与结果映射

### 案例 002：参数传递、resultType 与 resultMap

> [!note] 实践信息
> - **技术**：`#{}`、`@Param`、`resultType`、`resultMap`
> - **状态**：已完成基础学习与相关映射实践。
> - **验证范围**：未保留可逐条复现的原始 SQL 日志。

#### 1. 实践目标

掌握 Mapper 参数如何传递给 SQL，以及查询结果如何转换为 Java 对象。

#### 2. 参数绑定

示例：

```java
Student selectByNameAndAge(
        @Param("name") String name,
        @Param("age") Integer age
);
```

XML：

```xml
<select id="selectByNameAndAge"
        resultType="org.example.mybatis1.entity.Student">

    SELECT *
    FROM student
    WHERE name = #{name}
      AND age = #{age}

</select>
```

MyBatis 通常将 `#{}` 转换为 JDBC 预编译参数占位符：

```sql
SELECT *
FROM student
WHERE name = ?
  AND age = ?;
```

#### 3. 遇到的理解问题

**问题一：`#{}` 和 `${}` 有什么不同？**

```xml
WHERE id = #{id}
```

通常使用参数占位符绑定值。

```xml
ORDER BY ${columnName}
```

则是直接拼接 SQL 文本。

后者如果接受未经严格校验的用户输入，可能导致 SQL 注入风险。

因此：

- 普通查询值优先使用 `#{}`。
- 动态列名、排序方向等不能简单使用参数占位符的部分，应使用明确的白名单策略。

**问题二：Java 属性名与数据库列名不一致怎么办？**

例如：

```text
数据库：class_name
Java：className
```

可以通过 `resultMap` 明确映射：

```xml
<resultMap id="studentResultMap"
           type="org.example.mybatis1.entity.Student">

    <id property="id" column="id"/>

    <result property="name" column="name"/>

    <result property="className" column="class_name"/>

</resultMap>
```

#### 4. 实践收获

- 理解简单参数与多参数传递。
- 理解 `@Param` 的命名作用。
- 能区分 SQL 参数绑定与字符串拼接。
- 理解 `resultType` 和 `resultMap` 的用途。
- 理解 Java 属性与数据库列的映射关系。

#### 5. 经验总结

> [!important] 实践结论
> 参数绑定解决 Java 数据如何安全地传入 SQL，结果映射解决数据库查询结果如何转换为 Java 对象。两者方向不同，但都是 MyBatis 数据访问的基础。

---

## 三、动态 SQL

### 案例 003：使用动态 SQL 组合查询条件

> [!note] 实践信息
> - **技术**：`if`、`where`、`set`、`foreach`、`trim`
> - **状态**：已学习并完成动态 SQL 相关练习。
> - **代码说明**：以下为整理后的代表性写法。

#### 1. 实践目标

根据 Java 参数是否存在，动态生成 SQL 条件，避免为每一种查询组合单独编写 Mapper 方法。

#### 2. 条件查询示例

Mapper：

```java
List<Student> selectByCondition(
        @Param("name") String name,
        @Param("minScore") Integer minScore
);
```

XML：

```xml
<select id="selectByCondition"
        resultType="org.example.mybatis1.entity.Student">

    SELECT *
    FROM student

    <where>
        <if test="name != null and name != ''">
            AND name = #{name}
        </if>

        <if test="minScore != null">
            AND score >= #{minScore}
        </if>
    </where>

</select>
```

假设：

```text
name = null
minScore = 90
```

SQL 逻辑：

```sql
SELECT *
FROM student
WHERE score >= 90;
```

如果两个条件都没有传入，则不会生成多余的 `WHERE`。

#### 3. 动态更新

```xml
<update id="updateStudent">
    UPDATE student

    <set>
        <if test="name != null">
            name = #{name},
        </if>

        <if test="score != null">
            score = #{score},
        </if>
    </set>

    WHERE id = #{id}
</update>
```

`<set>` 可以处理动态字段后的多余逗号。

#### 4. 遇到的理解问题

**问题一：`<where>` 与普通 WHERE 的区别。**

`<where>` 不只是输出固定文本，还会根据内部条件决定是否生成 WHERE，并处理开头多余的 `AND` 或 `OR`。

**问题二：动态 SQL 条件全部缺失怎么办？**

查询可能变成：

```sql
SELECT * FROM student;
```

而更新或删除操作如果没有明确的业务约束，则可能产生危险的操作范围。

因此，不能把动态 SQL 能正常生成等同于业务操作一定安全。

**问题三：批量参数如何处理？**

```xml
SELECT *
FROM student
WHERE id IN

<foreach collection="ids"
         item="id"
         open="("
         separator=","
         close=")">
    #{id}
</foreach>
```

需要注意空集合，否则可能产生无效 SQL 或不符合预期的逻辑。

#### 5. 经验总结

- 动态 SQL 解决条件组合问题。
- `<where>` 和 `<set>` 能处理部分常见 SQL 拼接问题。
- `<foreach>` 适合构造 IN 条件等重复结构。
- SQL 语法正确不代表操作范围符合业务预期。
- 对 UPDATE、DELETE 必须特别重视 WHERE 条件。

> [!important] 实践结论
> 动态 SQL 提高了 SQL 的可复用性，但也引入了条件缺失、更新范围扩大和边界参数处理等问题，需要结合实际生成的 SQL 验证。

---

## 四、多表查询与结果映射

### 案例 004：使用 JOIN 与 resultMap 映射关联数据

> [!note] 实践信息
> - **技术**：`JOIN`、`association`、`collection`、`resultMap`
> - **状态**：多表关联和映射知识已学习，完成相关练习。
> - **说明**：本案例代码用于整理知识结构，不代表此前存在完全相同的实际项目表。

#### 1. 实践目标

理解数据库多表关系如何通过 MyBatis 查询并映射到 Java 对象。

#### 2. SQL 示例

假设存在：

```text
student
course
enrollment
```

查询学生选课情况：

```sql
SELECT
    s.id AS student_id,
    s.name AS student_name,
    c.id AS course_id,
    c.name AS course_name
FROM student s
JOIN enrollment e
    ON s.id = e.student_id
JOIN course c
    ON e.course_id = c.id
WHERE s.id = ?;
```

#### 3. 结果映射

如果查询结果是扁平结构，可以直接映射为 VO。

如果需要映射对象关联关系，例如：

```java
class StudentDetail {
    private Integer id;
    private String name;
    private List<Course> courses;
}
```

则可以使用 `<collection>` 组织一对多结果。

示意配置：

```xml
<resultMap id="studentDetailMap"
           type="StudentDetail">

    <id property="id" column="student_id"/>

    <result property="name"
            column="student_name"/>

    <collection property="courses"
                ofType="Course">

        <id property="id" column="course_id"/>

        <result property="name"
                column="course_name"/>

    </collection>

</resultMap>
```

#### 4. 需要注意的问题

**问题一：一对多 JOIN 为什么可能出现重复数据？**

一名学生选择三门课时，SQL 通常会返回三行。

```text
学生A - 课程1
学生A - 课程2
学生A - 课程3
```

如果想得到一个包含课程列表的学生对象，就需要正确配置结果映射。

**问题二：为什么 `<id>` 映射重要？**

在嵌套结果映射中，`<id>` 有助于 MyBatis 识别和合并对应对象，避免错误地将多行结果映射成重复或不完整的对象。

**问题三：多次查询和 JOIN 查询如何选择？**

需要综合考虑：

- SQL 可读性。
- 查询次数。
- 数据量。
- 关联复杂度。
- 是否存在 N+1 查询问题。

#### 5. 经验总结

> [!important] 实践结论
> 多表查询需要同时理解关系型数据库的 JOIN 结果和 Java 对象结构。SQL 查询正确只是第一步，还需要保证结果映射正确。

---

## 五、Spring Boot 与 MyBatis 整合

### 案例 005：配置 MyBatis Starter 与 Mapper 扫描

> [!note] 实践信息
> - **技术**：Spring Boot 3.3.13、`mybatis-spring-boot-starter` 3.0.5
> - **JDK**：21
> - **数据库**：MySQL 8.0
> - **状态**：配置成功，并已验证 Mapper 可以访问数据库。

#### 1. 实践目标

将原生 MyBatis 整合到 Spring Boot，由 Spring 管理 Mapper、SqlSession 和相关组件。

#### 2. 主要依赖

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.5</version>
</dependency>
```

#### 3. XML 文件配置

```yaml
mybatis:
  mapper-locations: classpath:mapper/*.xml
```

作用：告诉 MyBatis 从指定资源目录加载 Mapper XML 文件。

Mapper 扫描示例：

```java
@MapperScan("org.example.mybatis1.mapper")
```

也可以在对应 Mapper 接口上使用：

```java
@Mapper
```

具体使用哪种扫描方式，取决于项目结构与配置习惯。

#### 4. 实践过程中需要理解的问题

**问题一：为什么能通过 Spring 注入 Mapper？**

```java
@Autowired
private StudentMapper studentMapper;
```

Spring 集成 MyBatis 后，Mapper 代理对象作为 Spring Bean 被注册和管理。

因此无需为每个 Mapper 手动创建实现类。

**问题二：为什么 Mapper XML 路径配置错误会导致运行失败？**

如果 Spring Boot 没有成功加载 XML，可能出现找不到对应映射语句的问题。

典型错误之一：

```text
Invalid bound statement (not found)
```

排查方向：

1. `mapper-locations` 配置。
2. XML 文件实际位置。
3. XML 的 `namespace`。
4. SQL 标签的 `id`。
5. XML 是否被正确复制到构建产物。

#### 5. 验证结果

- Spring Boot 项目能够正常启动。
- Mapper 扫描配置成功。
- XML 映射成功加载。
- Mapper 能够执行数据库操作。
- JUnit 5 测试环境可以运行。

#### 6. 经验总结

> [!important] 实践结论
> Spring Boot 与 MyBatis 整合后，业务代码不需要手动创建 SqlSession。Spring 管理相关对象的生命周期，Mapper 通过 Spring 注入使用。

---

## 六、SqlSession 与 Spring 事务

### 案例 006：理解 SqlSessionTemplate 与事务连接复用

> [!note] 实践信息
> - **技术**：`SqlSessionTemplate`、`SqlSessionUtils`、`TransactionSynchronizationManager`
> - **状态**：已完成原理学习和执行流程分析。
> - **验证说明**：本案例以源码机制和场景分析为主，未将所有连接复用情形逐一进行日志级实测。

#### 1. 实践目标

理解原生 MyBatis 与 Spring 集成之后，SqlSession 和 JDBC Connection 的管理方式发生了什么变化。

#### 2. 原生 MyBatis

不依赖 Spring 的情况下，可以手动管理：

```java
try (SqlSession session =
         sqlSessionFactory.openSession(false)) {

    StudentMapper mapper =
            session.getMapper(StudentMapper.class);

    // 执行数据库操作

    session.commit();
}
```

这里：

- `openSession(false)` 表示关闭自动提交。
- `commit()` 提交事务。
- `rollback()` 可撤销尚未提交的修改。
- `close()` 释放 SqlSession 相关资源。

#### 3. Spring 集成后的变化

典型调用链：

```text
Service
   ↓
Mapper 代理对象
   ↓
SqlSessionTemplate
   ↓
SqlSessionUtils
   ↓
SqlSession
   ↓
Executor
   ↓
JDBC Connection
   ↓
MySQL
```

Spring 事务管理器负责事务开始、提交或回滚。

MyBatis-Spring 通过事务同步机制，尽可能让当前事务中的 Mapper 操作复用与事务关联的 SqlSession 及数据库连接。

#### 4. 关键理解问题

**问题一：Mapper 方法调用后，是否每次都创建一个全新的数据库连接？**

不一定。

SqlSession 对象、连接池中的连接以及物理数据库连接是不同概念。

在有效的 Spring 事务内，同一数据源上的 Mapper 操作通常使用事务绑定的连接。

**问题二：SqlSessionTemplate 是否意味着 SqlSession 可以跨线程共享？**

`SqlSessionTemplate` 本身设计为线程安全的，可以被多个请求调用。

但它不意味着所有请求共用同一个底层 SqlSession 或 JDBC Connection。

**问题三：怎样判断两个 Mapper 是否参与同一个事务？**

不能仅凭它们属于同一个 Service 或使用同一个 Mapper 判断。

需要关注：

- 是否存在有效的 Spring 事务。
- 是否在同一线程执行。
- 是否使用相同事务管理器管理的数据源。
- 是否采用兼容的事务传播行为。

#### 5. 经验总结

> [!important] 实践结论
> Spring 集成 MyBatis 后，事务边界主要由 Spring 管理，SqlSessionTemplate 与相关工具负责衔接 Mapper 执行和事务资源。线程安全不等于数据库并发安全。

---

## 七、事务回滚与传播行为

### 案例 007：@Transactional 回滚规则与异常处理

> [!note] 实践信息
> - **技术**：`@Transactional`、`Propagation.REQUIRED`
> - **状态**：已完成理论学习、执行链分析与多轮场景题练习。
> - **验证范围**：以下场景结论主要来自推演与答题纠错，不全部视为真实数据库实测结果。

#### 1. 实践目标

理解 Spring 事务如何影响 MyBatis 执行数据库更新，并掌握异常导致事务回滚的条件。

#### 2. 基础事务示例

```java
@Service
public class StudentService {

    @Transactional
    public void updateStudent() {

        studentMapper.updateScore(1, 90);

        throw new RuntimeException("模拟异常");
    }
}
```

在默认 Spring 声明式事务规则下，如果该方法经 Spring 事务代理正常调用，且异常向外传播，则事务应回滚。

#### 3. 关键场景一：SQL 已执行，但事务尚未提交

```java
connection.setAutoCommit(false);

statement.executeUpdate(
    "UPDATE student SET score = 90 WHERE id = 1"
);

connection.rollback();
```

正确理解：

```text
UPDATE 已执行
    ↓
修改尚未提交
    ↓
ROLLBACK
    ↓
撤销事务内的修改
```

不能把回滚解释为“SQL 根本没有执行”。

#### 4. 关键场景二：内部方法抛异常，外部方法捕获

假设：

```java
@Transactional
public void methodA() {

    try {
        methodB();
    } catch (RuntimeException e) {
        System.out.println("捕获异常");
    }
}
```

其中 `methodB()` 也通过事务代理参与同一个 `REQUIRED` 事务，并抛出运行时异常。

关键问题：

**外层已经捕获异常，事务就一定能提交吗？**

答案：不一定。

若内部事务拦截器已经将共享事务标记为 `rollbackOnly`，外层即使捕获异常并正常返回，最终事务也可能回滚，且可能抛出 `UnexpectedRollbackException`。

需要注意：如果 `methodB()` 只是同类中的普通内部调用，未经过事务代理，以上判断就不能直接套用。

#### 5. 关键场景三：异常被捕获但事务未标记回滚

```java
@Transactional
public void methodA() {

    try {
        studentMapper.updateScore(1, 90);

        throw new RuntimeException("失败");

    } catch (RuntimeException e) {
        System.out.println("异常已处理");
    }
}
```

如果异常在事务方法内部被捕获，没有向事务拦截器传播，也没有其他回滚标记，则事务可能正常提交。

因此：

**发生过异常，不等于事务一定回滚。**

可根据业务需要：

- 重新抛出异常。
- 主动将当前事务标记为回滚。
- 调整异常处理与事务边界。

#### 6. 关键场景四：常见事务失效

已学习以下情况：

- 同类内部调用导致事务代理未被经过。
- 异常被捕获后没有继续传播。
- 默认回滚规则不覆盖所有受检异常。
- 方法未通过 Spring 管理的代理调用。
- 方法或类的代理条件不满足，例如某些代理模式下的 `final` 方法。
- 新线程不自动继承调用线程的事务上下文。

#### 7. 经验总结

> [!important] 实践结论
> Spring 事务并不是“写了 `@Transactional` 就一定回滚”。必须分析代理调用、事务传播、异常类型、异常传播路径与 `rollbackOnly` 状态。

---

## 八、MyBatis 插件机制

### 案例 008：认识原生 MyBatis 拦截器的执行位置

> [!note] 实践信息
> - **技术**：`Interceptor`、`Executor`、`StatementHandler`、`ParameterHandler`、`ResultSetHandler`
> - **状态**：已进入原理学习。
> - **待验证**：尚无独立完成自定义拦截器并运行验证的明确记录。

#### 1. 实践目标

理解原生 MyBatis 如何在不修改 Mapper 业务接口的情况下扩展 SQL 执行过程。

#### 2. 常见拦截位置

| 接口 | 主要职责 |
|---|---|
| `Executor` | 执行查询与更新、参与缓存处理 |
| `StatementHandler` | JDBC Statement 创建、SQL 预处理和执行 |
| `ParameterHandler` | 设置 SQL 参数 |
| `ResultSetHandler` | 处理结果集并映射为对象 |

#### 3. 典型应用场景

- SQL 执行耗时统计。
- SQL 执行过程记录。
- 分页功能扩展。
- 参数处理扩展。
- 结果处理扩展。

#### 4. 理解问题

如果需要统计 SQL 执行耗时，需要明确计时范围。

例如：

- 统计一次 Mapper 查询调用的总耗时。
- 只统计 JDBC Statement 的执行耗时。
- 是否包含参数绑定和结果映射时间。

这些目标可能对应不同的拦截位置。

#### 5. 经验总结

> [!important] 实践结论
> MyBatis 插件通过拦截指定执行环节来扩展框架行为，但不同拦截点的职责与计时范围不同。目前已学习基本原理，尚未将自定义插件实操标记为完成。

---

## 九、实践中总结的 MyBatis 核心机制

| 功能 | 核心机制 | 掌握情况 |
|---|---|---|
| Mapper 接口 | 动态代理连接 Java 方法与 SQL | 已学习及实操 |
| Mapper XML | `namespace`、`id` 定位 SQL | 已实操 |
| 参数绑定 | `#{}`、`@Param`、预编译参数 | 已学习 |
| 结果映射 | `resultType`、`resultMap` | 已学习及练习 |
| 动态 SQL | `if`、`where`、`set`、`foreach` | 已学习及练习 |
| 多表映射 | JOIN、关联对象映射 | 已学习 |
| Spring Boot 整合 | Starter、Mapper 扫描与注入 | 已验证 |
| SqlSession | 会话管理与执行过程 | 已学习 |
| Spring 事务 | 连接绑定、提交与回滚 | 已深入学习 |
| 事务传播 | REQUIRED、共享事务、回滚标记 | 已完成场景练习 |
| MyBatis 插件 | 拦截执行流程 | 已学习原理 |

### 需要长期记住的区别

**1. Mapper 接口与 Mapper XML**

Mapper 接口定义 Java 访问方法，XML 保存 SQL，MyBatis 负责连接两者。

**2. `#{}` 与 `${}`**

`#{}` 通常用于绑定参数值；`${}` 是 SQL 文本替换，必须防范注入风险。

**3. SQL 执行与事务提交**

SQL 执行成功不代表事务已经提交。

**4. 捕获异常与事务回滚**

外层捕获异常不一定能阻止回滚；内部捕获异常也不一定会触发回滚。

**5. SqlSession 线程安全与数据库并发安全**

`SqlSessionTemplate` 可被多线程调用，不代表数据库操作自动具备并发安全性。

**6. 原生 MyBatis 与 MyBatis-Plus**

原生 MyBatis 更侧重 SQL 映射、执行过程和结果映射；MyBatis-Plus 在其基础上提供通用 CRUD、条件构造器和其他扩展功能。

---