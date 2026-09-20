# 《MyBatis 完整学习与开发速查笔记》

> **适用环境**：Java 17+、Spring Boot 3.x、MyBatis 3.x、mybatis-spring-boot-starter 3.x、MySQL 8.x。  
> **标记说明**：  
> 【MyBatis 核心】= MyBatis 原生功能  
> 【Spring Boot 整合】= MyBatis-Spring / Starter 提供  
> 【第三方扩展】= PageHelper、MyBatis-Plus 等，不属于 MyBatis 核心  
> ⚠️ 易混淆 = 实际开发高频混淆点

---

# 第一篇：MyBatis 基础认知

## 1. MyBatis 是什么

【**MyBatis 核心**】

MyBatis 是一个**半自动 ORM 持久层框架**。它把 JDBC 中重复的：

- 获取连接
- 创建 `PreparedStatement`
- 设置参数
- 执行 SQL
- 处理 `ResultSet`
- 映射 Java 对象
- 关闭资源

封装起来，但 **SQL 仍然由开发者自己写**。

> [!tip]
> 
> - JDBC 是手动挡，Hibernate/JPA 是自动挡，MyBatis 是“SQL 自己写，映射框架帮你做”。
> - **MyBatis = Java ↔ SQL ↔ 数据库之间的桥梁**

### MyBatis 与 JDBC 的关系

| 对比项 | JDBC | MyBatis |
|---|---|---|
| SQL 控制 | 完全手写 | 完全手写 |
| 参数设置 | `ps.setXxx()` | `#{}` |
| 结果映射 | 手动 `ResultSet` | `resultType/resultMap` |
| 资源管理 | 手动关闭 | 框架管理 |
| 重复代码 | 多 | 少 |
| 灵活性 | 最高 | 很高 |

MyBatis 底层仍然使用 JDBC，只是封装了流程。

```
JDBC
= Java 直接操作数据库的底层 API
= 自己处理很多细节

MyBatis
= 建立在 JDBC 之上的持久层框架
= SQL 仍然可以自己写
= MyBatis 帮你处理 JDBC 的大量重复工作
= 特别是参数绑定 + 结果映射
```

### MyBatis 与 Hibernate / JPA 的区别

| 特性 | MyBatis | Hibernate / JPA |
|---|---|---|
| SQL 控制 | 开发者写 SQL | 框架生成 SQL |
| ORM 程度 | 半自动 | 全自动 |
| 学习成本 | 较低 | 较高 |
| 复杂 SQL | 非常友好 | 较麻烦 |
| 数据库移植 | 依赖 SQL | 较好 |
| 典型场景 | 互联网、复杂查询 | 业务模型稳定、CRUD 多 |

### MyBatis 优缺点

**优点：**

- SQL 可控，性能调优方便
- 动态 SQL 强大
- 学习成本相对低
- 与 Spring Boot 整合简单
- 适合复杂查询、报表、多表关联

**缺点：**

- 需要手写 SQL
- XML 较多时维护成本高
- 数据库移植性弱
- 简单 CRUD 也要写 Mapper

**适合**：需要精细控制 SQL、复杂查询多的项目。  
**不适合**：完全不想写 SQL、追求全自动 ORM 的项目。

---

## 2. MyBatis 整体工作流程

【MyBatis 核心】

```text
Java 调用 Mapper 接口
        ↓
MapperProxy 代理
        ↓
SqlSession
        ↓
Executor
        ↓
MappedStatement（namespace + id）
        ↓
ParameterHandler 设置参数
        ↓
StatementHandler + JDBC PreparedStatement
        ↓
MySQL 执行
        ↓
ResultSetHandler
        ↓
resultType / resultMap 映射
        ↓
Java 对象
```

核心组件关系：

| 组件 | 职责 |
|---|---|
| `SqlSessionFactory` | 工厂，单例，创建 `SqlSession` |
| `SqlSession` | 一次会话，执行 SQL、获取 Mapper、管理事务 |
| `Executor` | 真正执行 SQL，有 SIMPLE、REUSE、BATCH |
| `MappedStatement` | 一个 SQL 映射，由 `namespace + id` 唯一确定 |
| `ParameterHandler` | 把 Java 参数设置到 PreparedStatement |
| `StatementHandler` | 创建、执行 JDBC Statement |
| `ResultSetHandler` | 把 ResultSet 映射为 Java 对象 |
| `Configuration` | 全局配置，保存所有映射、TypeHandler、缓存等 |

---

# 第二篇：MyBatis 项目搭建

## 3. 最小 MyBatis 项目

### Maven 依赖

```xml
<dependencies>
    <dependency>
        <groupId>org.mybatis</groupId>
        <artifactId>mybatis</artifactId>
        <version>3.5.16</version>
    </dependency>
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <version>8.4.0</version>
    </dependency>
</dependencies>
```

### 数据库表

```sql
CREATE TABLE student (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50),
    age INT,
    score DECIMAL(5,2)
);
```

### Java Bean

```java
package com.example.entity;

public class Student {
    private Long id;
    private String name;
    private Integer age;
    private Double score;

    // getter / setter / toString
}
```

### Mapper 接口

```java
package com.example.mapper;

import com.example.entity.Student;

public interface StudentMapper {
    Student selectById(Long id);
}
```

### Mapper XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.StudentMapper">

    <select id="selectById" resultType="com.example.entity.Student">
        SELECT id, name, age, score
        FROM student
        WHERE id = #{id}
    </select>

</mapper>
```

> [!tip]
> `Mapper.xml` 是 MyBatis 的 SQL 映射文件，**核心作用**：
> **把 Mapper 接口的方法和具体 SQL 绑定起来，并定义参数怎么传、结果怎么映射成 Java 对象**。

### mybatis-config.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>      // 这是 XML 1.0，使用 UTF-8 编码
<!DOCTYPE configuration
        PUBLIC "-//mybatis.org//DTD Config 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-config.dtd">    //这个文件遵循 MyBatis Mapper XML 的格式规范
<configuration>
    <environments default="development">
        <environment id="development">
            <transactionManager type="JDBC"/>
            <dataSource type="POOLED">
                <property name="driver" value="com.mysql.cj.jdbc.Driver"/>
                <property name="url" value="jdbc:mysql://localhost:3306/test?serverTimezone=Asia/Shanghai"/>
                <property name="username" value="root"/>
                <property name="password" value="123456"/>
            </dataSource>
        </environment>
    </environments>

    <mappers>
        <mapper resource="mapper/StudentMapper.xml"/>
    </mappers>
</configuration>
```

### 测试

```java
InputStream in = Resources.getResourceAsStream("mybatis-config.xml");
SqlSessionFactory factory = new SqlSessionFactoryBuilder().build(in);

try (SqlSession session = factory.openSession()) {
    StudentMapper mapper = session.getMapper(StudentMapper.class);
    Student student = mapper.selectById(1L);
    System.out.println(student);
}
```

---

# 第三篇：Mapper

## 4. Mapper 接口

【MyBatis 核心】

Mapper 接口不需要写实现类，MyBatis 通过 JDK 动态代理生成 `MapperProxy`。

**对应关系：**

```text
Mapper 接口全限定名 = XML namespace
方法名 = XML 标签 id
参数 = #{}
返回值 = resultType / resultMap
```

> [!tip]
> **`resultType`：决定“结果封装成什么 Java 类型”，而 MyBatis 再根据这个类型的属性和 SQL 返回的列进行结果映射**
> **`resultMap`：手动告诉 MyBatis “这一列对应哪个属性”**

**示例：**

```java
Student selectById(Integer id);
```

```xml
<select id="selectById" resultType="Student">
    SELECT * FROM student WHERE id = #{id}
</select>
```

**对应关系：**

```text
StudentMapper.selectById()
        ↕
namespace="com.example.mapper.StudentMapper"
id="selectById"
```

### @Mapper 与 @MapperScan

> [!tip]
> **`@Mapper`告诉 MyBatis：这个接口是 Mapper，请为它创建代理对象**
> **`@MapperScan`告诉 MyBatis：去这个包下面，把 Mapper 接口全部扫描出来**

【Spring Boot 整合】

```java
@Mapper
public interface StudentMapper {
    Student selectById(Long id);
}
```

或在启动类：

```java
@SpringBootApplication
@MapperScan("com.example.demo.mapper")
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

> [!warning]
> **易混淆：**`@Mapper` 加在单个接口上，`@MapperScan` 加在配置类或启动类上扫描包

**整体链路：**

```
Spring Boot
    │
    │ @MapperScan
    ↓
发现 StudentMapper
    │
    ↓
MyBatis 为 StudentMapper 创建代理
    │
    ↓
namespace 找到 StudentMapper.xml
    │
    ↓
id="selectAll"
    │
    ↓
找到 SQL
    │
    ↓
执行
```

---

# 第四篇：XML 映射文件

## 5. Mapper XML

【MyBatis 核心】

```xml
<mapper namespace="com.example.mapper.StudentMapper">
    <select id="selectById" resultType="Student">
        SELECT * FROM student WHERE id = #{id}
    </select>

    <insert id="insert" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO student(name, age, score)
        VALUES(#{name}, #{age}, #{score})
    </insert>

    <update id="update">
        UPDATE student SET name = #{name} WHERE id = #{id}
    </update>

    <delete id="deleteById">
        DELETE FROM student WHERE id = #{id}
    </delete>
</mapper>
```

**常用属性**：

| 属性 | 作用 |
|---|---|
| `namespace` | 对应 Mapper 名 |
| `id` | 对应 Mapper 方法名 |
| `parameterType` | 参数类型，通常可省略 |
| `resultType` | 自动映射结果类型 |
| `resultMap` | 手动映射结果 |
| `useGeneratedKeys` | 使用自增主键 |
| `keyProperty` | 主键回填到哪个属性 |

> [!note]
> `Mapper` 与 `Mapper.xml` 文件名相同，只是我们开发时的约定和习惯。
> **`namespace + id` 才是 MyBatis 用来定位 SQL 的关键。**

---

# 第五篇：参数传递

## 6. 单参数

```java
Student selectById(Integer id);
```

```xml
<select id="selectById" resultType="Student">
    SELECT * FROM student WHERE id = #{id}
</select>
```

单参数时，`#{}` 内名称可以任意，但推荐与方法参数名一致。

## 7. 多参数

```java
Student selectByCondition(String name, Integer age);
```

不写 `@Param` 时，MyBatis 使用：

- `arg0`、`arg1`
- `param1`、`param2`

```xml
WHERE name = #{param1} AND age = #{param2}
```

推荐：

```java
Student select(@Param("name") String name, @Param("age") Integer age);
```

```xml
<select id="select" resultType="Student">
    SELECT * FROM student
    WHERE name = #{name}
      AND age = #{age}
</select>
```

⚠️ 易混淆：多参数没有 `@Param`，XML 中写 `#{name}` 会报 `Parameter 'name' not found`。

---

# 第六篇：`#{}` 与 `${}`

## 8. `#{}`

【**MyBatis 核心**】

`#{}` 是预编译**参数占位符**(把 `{}` 内的值作为 SQL 参数传进去)，底层变成 JDBC `?`。

```xml
WHERE id = #{id}
```

**等价于**：

```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM student WHERE id = ?");
ps.setLong(1, id);
```

**优点**：

- 防止 SQL 注入
- 参数类型自动处理
- 推荐所有参数值都用 `#{}`

## 9. `${}`

`${}` 是字符串直接拼接，直接替换 SQL 文本。

```xml
ORDER BY ${orderBy}
```

如果 `orderBy = "id; DROP TABLE student"`，就会产生 SQL 注入风险。

### ⚠️ `#{}` 与 `${}` 对比

| 对比项 | `#{}` | `${}` |
|---|---|---|
| 处理方式 | 预编译 `?` | 字符串拼接 |
| SQL 注入 | 安全 | 危险 |
| 适用 | 参数值 | 动态表名、列名、ORDER BY |
| 示例 | `#{id}` | `${orderBy}` |
| 推荐 | 默认使用 | 必须白名单校验 |

安全示例：

```java
String orderBy = "id";
if (!Set.of("id", "name", "score").contains(orderBy)) {
    throw new IllegalArgumentException("非法排序字段");
}
```

```xml
ORDER BY ${orderBy}
```

---

# 第七篇：结果映射

## 10. resultType

【**MyBatis 核心**】

**自动映射**：

```xml
<select id="selectById" resultType="com.example.entity.Student">
    SELECT id, name, age, score FROM student WHERE id = #{id}
</select>
```

字段名与属性名不一致时：

- **开启驼峰映射**：

```yaml
mybatis:
  configuration:
    map-underscore-to-camel-case: true
```

例如 `class_name` -> `className`。

- **或使用别名**：

```sql
SELECT class_name AS className FROM student
```

## 11. resultMap

**复杂映射使用**：

```xml
<resultMap id="StudentResultMap" type="com.example.entity.Student">
    <id column="id" property="id"/>
    <result column="name" property="name"/>
    <result column="age" property="age"/>
    <result column="score" property="score"/>
</resultMap>

<select id="selectById" resultMap="StudentResultMap">
    SELECT id, name, age, score FROM student WHERE id = #{id}
</select>
```

> [!tip]
> `resultType` 适合简单自动映射；`resultMap` 适合字段不一致、一对一、一对多、多对多。

> [!note]
> `property `代表：Java 对象的属性
> `column` 代表：SQL 查询结果中的列名
>
> `<id>`：用于主键映射。
> `<result>`：用于普通字段映射。

```
resultType
    ↓
指定结果对象类型
    ↓
主要依靠自动映射

resultMap
    ↓
指定结果对象类型
+
明确指定字段 → 属性的映射关系
```

---

# 第八篇：CRUD

> [!tip]
> **Mapper 接口**：声明“我要做什么”
> **Mapper.xml**：告诉 MyBatis “具体怎么做”

**CRUD 全流程**：

```
Mapper 接口（如 UserMapper）
    ↓
声明 Java 方法，如 User selectById(Long id)
    ↓
Mapper.xml
    ↓
namespace = Mapper 接口全限定名
id = 接口方法名
    ↓
两者共同组成 statement id：namespace + id
    ↓
编写具体 SQL
    ↓
#{参数} 进行参数绑定，生成预编译 SQL 占位符 ?
    ↓
MyBatis 通过 JDK 动态代理调用接口方法
    ↓
Executor / StatementHandler 执行 SQL
    ↓
ResultSetHandler 把结果映射成 Java 对象
    ↓
查询返回对象/List/Map；增删改返回 int 影响行数
```

## 12. SELECT

```xml
<select id="selectAll" resultType="Student">
    SELECT * FROM student
</select>

<select id="selectByName" resultType="Student">
    SELECT * FROM student
    WHERE name LIKE CONCAT('%', #{name}, '%')
</select>
```

## 13. INSERT

```xml
<insert id="insert" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO student(name, age, score)
    VALUES(#{name}, #{age}, #{score})
</insert>
```

**主键回填**：

```java
Student student = new Student();
student.setName("Tom");
studentMapper.insert(student);
System.out.println(student.getId()); // 自增 id 已回填
```

- **`useGeneratedKeys` + `keyProperty` 的作用与价值**：
  - **`AUTO_INCREMENT`**：MySQL 自动生成新的主键 ID。
  - **`useGeneratedKeys="true"`**：让 MyBatis 获取这个自动生成的 ID。
  - **`keyProperty="id"`**：把获取到的 ID 回填到 Java 对象的 `id` 属性。
  - **核心价值**：
    - **一次 INSERT 后，同时知道“插入是否成功/影响几行”和“刚插入的数据 ID 是多少”，方便后续代码继续使用这个 ID。**
  - **注意**：
    - **它不是用来自动查询或输出新数据的。**

**批量插入**：

```xml
<insert id="insertBatch">
    INSERT INTO student(name, age, score) VALUES
    <foreach collection="list" item="s" separator=",">
        (#{s.name}, #{s.age}, #{s.score})
    </foreach>
</insert>
```

## 14. UPDATE

```xml
<update id="update">
    UPDATE student
    SET name = #{name},
        age = #{age}
    WHERE id = #{id}
</update>
```

动态更新见 `<set>`。

## 15. DELETE

```xml
<delete id="deleteById">
    DELETE FROM student WHERE id = #{id}
</delete>

<delete id="deleteBatch">
    DELETE FROM student WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</delete>
```

---

# 第九篇：动态 SQL

## 16. if

```xml
<if test="name != null and name != ''">
    AND name = #{name}
</if>
```

## 17. where

```xml
<select id="selectByCondition" resultType="Student">
    SELECT * FROM student
    <where>
        <if test="name != null and name != ''">
            AND name LIKE CONCAT('%', #{name}, '%')
        </if>
        <if test="age != null">
            AND age = #{age}
        </if>
    </where>
</select>
```

`<where>` 会自动去掉开头多余的 `AND` 或 `OR`。

## 18. trim

```xml
<trim prefix="WHERE" prefixOverrides="AND |OR ">
    <if test="name != null">
        AND name = #{name}
    </if>
</trim>
```

## 19. choose / when / otherwise

```xml
<choose>
    <when test="name != null">
        AND name = #{name}
    </when>
    <when test="age != null">
        AND age = #{age}
    </when>
    <otherwise>
        AND id > 0
    </otherwise>
</choose>
```

类似 Java `switch`，只命中一个分支。

## 20. set

```xml
<update id="updateSelective">
    UPDATE student
    <set>
        <if test="name != null">name = #{name},</if>
        <if test="age != null">age = #{age},</if>
        <if test="score != null">score = #{score},</if>
    </set>
    WHERE id = #{id}
</update>
```

`<set>` 会自动去掉最后多余的逗号。

## 21. foreach

```xml
<delete id="deleteBatch">
    DELETE FROM student
    WHERE id IN
    <foreach collection="ids"
             item="id"
             open="("
             separator=","
             close=")">
        #{id}
    </foreach>
</delete>
```

| 属性 | 作用 |
|---|---|
| `collection` | 要遍历的集合 |
| `item` | 每次迭代元素 |
| `index` | 下标 |
| `open` | 开始符号 |
| `separator` | 分隔符 |
| `close` | 结束符号 |

---

# 第十篇：复杂查询

## 22. 多表查询

SQL 负责 JOIN，MyBatis 负责映射。

```sql
SELECT s.id, s.name, c.class_name
FROM student s
LEFT JOIN class c ON s.class_id = c.id
WHERE s.id = #{id}
```

## 23. association 一对一

```xml
<resultMap id="StudentWithClass" type="Student">
    <id column="id" property="id"/>
    <result column="name" property="name"/>
    <association property="clazz" javaType="Class">
        <id column="class_id" property="id"/>
        <result column="class_name" property="name"/>
    </association>
</resultMap>
```

## 24. collection 一对多

```xml
<resultMap id="ClassWithStudents" type="Class">
    <id column="class_id" property="id"/>
    <result column="class_name" property="name"/>
    <collection property="students" ofType="Student">
        <id column="student_id" property="id"/>
        <result column="student_name" property="name"/>
    </collection>
</resultMap>
```

## 25. 多对多

```text
Student
Course
Student_Course
```

```xml
<resultMap id="StudentWithCourses" type="Student">
    <id column="student_id" property="id"/>
    <result column="student_name" property="name"/>
    <collection property="courses" ofType="Course">
        <id column="course_id" property="id"/>
        <result column="course_name" property="name"/>
    </collection>
</resultMap>

<select id="selectStudentWithCourses" resultMap="StudentWithCourses">
    SELECT s.id AS student_id,
           s.name AS student_name,
           c.id AS course_id,
           c.name AS course_name
    FROM student s
    JOIN student_course sc ON s.id = sc.student_id
    JOIN course c ON c.id = sc.course_id
    WHERE s.id = #{id}
</select>
```

---

# 第十一篇：注解方式

【MyBatis 核心】

```java
@Mapper
public interface StudentMapper {

    @Select("SELECT * FROM student WHERE id = #{id}")
    Student selectById(Long id);

    @Insert("INSERT INTO student(name, age) VALUES(#{name}, #{age})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(Student student);

    @Update("UPDATE student SET name = #{name} WHERE id = #{id}")
    int update(Student student);

    @Delete("DELETE FROM student WHERE id = #{id}")
    int deleteById(Long id);
}
```

`@Results`：

```java
@Results(id = "studentMap", value = {
    @Result(column = "id", property = "id", id = true),
    @Result(column = "name", property = "name"),
    @Result(column = "class_id", property = "clazz",
            one = @One(select = "com.example.mapper.ClassMapper.selectById"))
})
@Select("SELECT * FROM student WHERE id = #{id}")
Student selectWithClass(Long id);
```

一对多：

```java
@Many(select = "com.example.mapper.StudentMapper.selectByClassId")
```

XML vs 注解：

| 场景 | 推荐 |
|---|---|
| 简单 CRUD | 注解 |
| 动态 SQL | XML |
| 复杂 resultMap | XML |
| 快速小项目 | 注解 |

---

# 第十二篇：MyBatis 与 Spring Boot

## 26. Spring Boot 整合

【Spring Boot 整合】

依赖：

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <scope>runtime</scope>
</dependency>
```

**三者关系**：

```text
MyBatis：核心 SQL 映射框架
MyBatis-Spring：让 MyBatis 接入 Spring 事务、Bean 管理
MyBatis-Spring-Boot-Starter：Spring Boot 自动配置
```

## 27. Spring Boot 项目结构

```text
src/main/java/com/example/demo
├── controller
├── service
├── service/impl
├── mapper
└── entity

src/main/resources
├── mapper
│   └── StudentMapper.xml
└── application.yml
```

## 28. Mapper 注入

```java
@Service
public class StudentService {

    private final StudentMapper studentMapper;

    public StudentService(StudentMapper studentMapper) {
        this.studentMapper = studentMapper;
    }

    public Student getById(Long id) {
        return studentMapper.selectById(id);
    }
}
```

为什么能注入？  
因为 `@MapperScan` 或 `@Mapper` 让 MyBatis 为接口生成代理对象，并注册到 Spring 容器。

---

# 第十三篇：MyBatis 核心组件

## 29. SqlSessionFactory

- 是什么：创建 `SqlSession` 的工厂
- 负责什么：加载配置、保存 `Configuration`
- 什么时候接触：框架初始化
- 实际项目：一般不直接操作
- 源码关系：`SqlSessionFactoryBuilder` -> `SqlSessionFactory`

## 30. SqlSession

- 是什么：一次数据库会话
- 负责什么：执行 SQL、获取 Mapper、提交/回滚
- 什么时候接触：非 Spring 项目手动使用
- Spring 项目：由 `SqlSessionTemplate` 管理

## 31. Executor

- 是什么：SQL 执行器
- 类型：`SIMPLE`、`REUSE`、`BATCH`
- 负责什么：调用 JDBC、处理缓存
- 实际项目：一般不直接操作

## 32. MappedStatement

- 是什么：一个 SQL 映射对象
- 唯一标识：`namespace + id`
- 保存：SQL、参数映射、结果映射、缓存配置

## 33. Configuration

- 是什么：MyBatis 全局配置
- 保存：`MappedStatement`、`TypeHandler`、缓存、插件
- 实际项目：一般不直接操作

## 34. TypeHandler

见第十四篇。

---

# 第十四篇：TypeHandler

【MyBatis 核心】

TypeHandler 负责 Java 类型 ↔ JDBC 类型转换。

常见：

- `StringTypeHandler`
- `IntegerTypeHandler`
- `LongTypeHandler`
- `BooleanTypeHandler`
- `DateTypeHandler`

自定义示例：List<String> 转 JSON 字符串。

```java
@MappedTypes(List.class)
@MappedJdbcTypes(JdbcType.VARCHAR)
public class StringListTypeHandler extends BaseTypeHandler<List<String>> {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    @Override
    public void setNonNullParameter(PreparedStatement ps, int i,
                                    List<String> parameter, JdbcType jdbcType)
            throws SQLException {
        try {
            ps.setString(i, MAPPER.writeValueAsString(parameter));
        } catch (JsonProcessingException e) {
            throw new SQLException(e);
        }
    }

    @Override
    public List<String> getNullableResult(ResultSet rs, String columnName)
            throws SQLException {
        return parse(rs.getString(columnName));
    }

    @Override
    public List<String> getNullableResult(ResultSet rs, int columnIndex)
            throws SQLException {
        return parse(rs.getString(columnIndex));
    }

    @Override
    public List<String> getNullableResult(CallableStatement cs, int columnIndex)
            throws SQLException {
        return parse(cs.getString(columnIndex));
    }

    private List<String> parse(String json) throws SQLException {
        if (json == null) return null;
        try {
            return MAPPER.readValue(json, new TypeReference<List<String>>() {});
        } catch (JsonProcessingException e) {
            throw new SQLException(e);
        }
    }
}
```

注册：

```yaml
mybatis:
  type-handlers-package: com.example.demo.handler
```

---

# 第十五篇：MyBatis 缓存

## 35. 一级缓存

【MyBatis 核心】

- 级别：`SqlSession`
- 默认：开启
- 命中：同一个 SqlSession 执行相同 SQL、相同参数
- 失效：
  - 不同 SqlSession
  - 执行 insert/update/delete
  - commit/rollback
  - `flushCache=true`
  - 手动清空

Spring 中无事务时，每次 Mapper 调用可能新 SqlSession，一级缓存不一定命中。

## 36. 二级缓存

【MyBatis 核心】

- 级别：`namespace`
- 默认：关闭
- 开启：

```xml
<cache/>
```

或：

```xml
<cache eviction="LRU"
       flushInterval="60000"
       size="512"
       readOnly="true"/>
```

实体需实现 `Serializable`。

注意：

- 跨 SqlSession
- 不同 namespace 隔离
- 更新会清空当前 namespace 缓存
- 分布式环境需 Redis 等集中缓存

⚠️ 易混淆：MyBatis 缓存是应用层缓存，MySQL Buffer Pool 是数据库层缓存，不是一回事。

---

# 第十六篇：事务

【Spring Boot 整合】

MyBatis 自身通过 `SqlSession.commit()` / `rollback()` 管理事务。

Spring 整合后，通常由 Spring 管理：

```java
@Service
public class StudentService {

    private final StudentMapper studentMapper;

    public StudentService(StudentMapper studentMapper) {
        this.studentMapper = studentMapper;
    }

    @Transactional(rollbackFor = Exception.class)
    public void create(Student student) {
        studentMapper.insert(student);
        // 抛异常则回滚
    }
}
```

关键点：

- `@Transactional` 默认回滚 `RuntimeException` 和 `Error`
- 检查异常需 `rollbackFor = Exception.class`
- 同一事务内通常复用同一个 SqlSession
- try-catch 吞掉异常会导致不回滚
- 自调用会导致代理失效

---

# 第十七篇：分页

【MyBatis 核心】手动分页：

```xml
<select id="selectPage" resultType="Student">
    SELECT * FROM student
    ORDER BY id
    LIMIT #{offset}, #{size}
</select>
```

【第三方扩展】PageHelper：

```java
PageHelper.startPage(pageNum, pageSize);
List<Student> list = studentMapper.selectAll();
PageInfo<Student> pageInfo = new PageInfo<>(list);
```

【第三方扩展】MyBatis-Plus 分页：

```java
Page<Student> page = new Page<>(pageNum, pageSize);
studentMapper.selectPage(page, null);
```

---

# 第十八篇：动态 SQL 实战

### 场景 1：学生条件查询

```xml
<select id="selectByCondition" resultType="Student">
    SELECT * FROM student
    <where>
        <if test="name != null and name != ''">
            AND name LIKE CONCAT('%', #{name}, '%')
        </if>
        <if test="age != null">
            AND age = #{age}
        </if>
        <if test="gender != null and gender != ''">
            AND gender = #{gender}
        </if>
        <if test="className != null and className != ''">
            AND class_name = #{className}
        </if>
        <if test="minScore != null">
            AND score >= #{minScore}
        </if>
    </where>
</select>
```

### 场景 2：学生动态修改

```xml
<update id="updateSelective">
    UPDATE student
    <set>
        <if test="name != null">name = #{name},</if>
        <if test="age != null">age = #{age},</if>
        <if test="gender != null">gender = #{gender},</if>
        <if test="score != null">score = #{score},</if>
    </set>
    WHERE id = #{id}
</update>
```

### 场景 3：批量删除

```xml
<delete id="deleteBatch">
    DELETE FROM student
    WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</delete>
```

### 场景 4：批量插入

```xml
<insert id="insertBatch">
    INSERT INTO student(name, age, gender, score) VALUES
    <foreach collection="list" item="s" separator=",">
        (#{s.name}, #{s.age}, #{s.gender}, #{s.score})
    </foreach>
</insert>
```

---

# 第十九篇：常见问题与坑

| 现象 | 原因 | 检查 | 解决 |
|---|---|---|---|
| `Invalid bound statement (not found)` | Mapper 接口与 XML 不对应 | namespace、id、方法名 | 改成全限定名一致 |
| `Parameter 'xxx' not found` | 多参数未加 `@Param` | 方法参数 | 加 `@Param` |
| `TooManyResultsException` | 查询返回多条但方法返回单条 | SQL 条件 | 用 `List` 或加条件 |
| `BindingException` | Mapper 未注册 | `@Mapper`、`@MapperScan` | 加注解或扫描 |
| XML 未加载 | `mapper-locations` 错 | resources 路径 | 配 `classpath:mapper/*.xml` |
| 字段映射不上 | 下划线/驼峰 | `map-underscore-to-camel-case` | 开启驼峰或 `resultMap` |
| SQL 注入 | 用了 `${}` | 参数值 | 改 `#{}` |
| 动态 SQL 多 AND | `<where>` 没用 | SQL 拼接 | 用 `<where>` |
| 主键拿不到 | 未配置回填 | insert 标签 | `useGeneratedKeys=true`、`keyProperty` |
| 事务不回滚 | 异常被吞/检查异常 | `@Transactional` | `rollbackFor=Exception.class` |
| 查询执行两次 | 一级缓存/嵌套查询 | 日志 | 用 join 或二级缓存 |

---

# 第二十篇：MyBatis 常用配置速查

```yaml
mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.demo.entity
  type-handlers-package: com.example.demo.handler
  configuration:
    map-underscore-to-camel-case: true
    cache-enabled: true
    lazy-loading-enabled: true
    aggressive-lazy-loading: false
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

| 配置 | 作用 | 频率 |
|---|---|---|
| `mapper-locations` | XML 位置 | 必须 |
| `type-aliases-package` | 实体别名 | 常用 |
| `map-underscore-to-camel-case` | 下划线转驼峰 | 必须 |
| `log-impl` | 打印 SQL | 常用 |
| `cache-enabled` | 二级缓存开关 | 偶尔 |
| `lazy-loading-enabled` | 延迟加载 | 偶尔 |
| `type-handlers-package` | 自定义 TypeHandler | 高级 |

---

# 第二十一篇：MyBatis 常用标签速查

| 标签 | 作用 | 频率 | 示例 |
|---|---|---|---|
| `select` | 查询 | 高 | `<select id="selectById">` |
| `insert` | 插入 | 高 | `<insert id="insert">` |
| `update` | 更新 | 高 | `<update id="update">` |
| `delete` | 删除 | 高 | `<delete id="deleteById">` |
| `if` | 条件 | 高 | `<if test="name != null">` |
| `where` | 动态 WHERE | 高 | `<where>` |
| `set` | 动态 UPDATE | 高 | `<set>` |
| `foreach` | 批量 | 高 | `<foreach collection="ids">` |
| `choose` | 分支 | 中 | `<choose><when>...` |
| `trim` | SQL 修饰 | 中 | `<trim prefix="WHERE">` |
| `resultMap` | 复杂映射 | 高 | `<resultMap id="...">` |
| `association` | 一对一 | 中 | `<association property="clazz">` |
| `collection` | 一对多 | 中 | `<collection property="students">` |

---

# 第二十二篇：MyBatis 与 JDBC / JPA 对比

| 特性 | JDBC | MyBatis | JPA |
|---|---|---|---|
| SQL 控制 | 完全手写 | 完全手写 | 框架生成 |
| 学习成本 | 低 | 中 | 高 |
| 灵活性 | 最高 | 高 | 中 |
| ORM 程度 | 无 | 半自动 | 全自动 |
| 映射 | 手动 | XML/注解 | 注解 |
| 复杂 SQL | 麻烦 | 友好 | 较麻烦 |
| 典型场景 | 教学/底层 | 互联网复杂查询 | 业务模型稳定 |

---

# 第二十三篇：实际项目代码阅读方法

```text
Controller
  ↓
Service
  ↓
Mapper 接口
  ↓
Mapper XML
  ↓
SQL
  ↓
Database
```

看到：

```java
studentMapper.selectByCondition(...)
```

按顺序找：

1. `StudentMapper` 接口方法
2. `namespace` 对应的 XML
3. `id` 对应的 `<select>`
4. `#{}` 参数来源
5. `resultType` / `resultMap`
6. SQL 涉及的表
7. 返回对象结构

---

# 第二十四篇：MyBatis 学习重点分级

### Level 1：必须掌握

- Mapper、XML、CRUD
- 参数传递、`@Param`
- `#{}`、`${}`
- `resultType`、`resultMap`
- 动态 SQL：`if`、`where`、`set`、`foreach`
- Spring Boot 整合
- 主键回填

### Level 2：应该掌握

- `association`、`collection`
- 事务、`@Transactional`
- 缓存
- 分页
- TypeHandler

### Level 3：理解原理

- `SqlSessionFactory`
- `SqlSession`
- `Executor`
- `MappedStatement`
- `Plugin`、`Interceptor`

### Level 4：暂时了解

- 源码级解析
- 自定义插件深度开发
- 多级缓存整合 Redis
- MyBatis-Plus 高级功能

---

# MyBatis 与 MyBatis-Plus 的关系

【第三方扩展】

- MyBatis：原生持久层框架，SQL 自己写。
- MyBatis-Plus：在 MyBatis 上增强，提供通用 CRUD、条件构造器、分页、代码生成等。
- 关系：MyBatis-Plus 不是 MyBatis 核心，它依赖 MyBatis。
- 很多 Spring Boot 项目用 MP 是为了少写简单 CRUD。

不要混淆：`BaseMapper`、`IService`、`LambdaQueryWrapper` 都是 MyBatis-Plus 的，不是 MyBatis 原生。

---

# 第二十五篇：最终速查手册 Cheat Sheet

### Mapper

```java
@Mapper
public interface StudentMapper {
    Student selectById(Long id);
    List<Student> selectByCondition(@Param("name") String name,
                                    @Param("age") Integer age);
    int insert(Student student);
    int update(Student student);
    int deleteBatch(@Param("ids") List<Long> ids);
}
```

### XML

```xml
<mapper namespace="com.example.mapper.StudentMapper">
    <select id="selectById" resultType="Student">
        SELECT * FROM student WHERE id = #{id}
    </select>
</mapper>
```

### 参数

```java
Student select(@Param("name") String name, @Param("age") Integer age);
```

```xml
WHERE name = #{name} AND age = #{age}
```

### `#{}`

```xml
WHERE id = #{id}
```

### `${}`

```xml
ORDER BY ${orderBy}
```

### resultType

```xml
<select id="selectAll" resultType="Student">
    SELECT * FROM student
</select>
```

### resultMap

```xml
<resultMap id="StudentMap" type="Student">
    <id column="id" property="id"/>
    <result column="name" property="name"/>
</resultMap>
```

### 动态 SQL

```xml
<where>
    <if test="name != null and name != ''">
        AND name LIKE CONCAT('%', #{name}, '%')
    </if>
</where>
```

### foreach

```xml
<foreach collection="ids" item="id" open="(" separator="," close=")">
    #{id}
</foreach>
```

### 一对一

```xml
<association property="clazz" javaType="Class">
    <id column="class_id" property="id"/>
    <result column="class_name" property="name"/>
</association>
```

### 一对多

```xml
<collection property="students" ofType="Student">
    <id column="student_id" property="id"/>
    <result column="student_name" property="name"/>
</collection>
```

### Spring Boot 配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/test?serverTimezone=Asia/Shanghai
    username: root
    password: 123456
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.example.demo.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

---

# MyBatis 问题 → 知识点索引

| 我遇到的问题 | 优先查询 |
|---|---|
| Mapper 找不到 | `@Mapper` / `@MapperScan` |
| XML 找不到 | `mapper-locations` |
| `Invalid bound statement` | namespace / id / 方法名 |
| 参数找不到 | `@Param` / 参数绑定 |
| SQL 注入 | `#{}` / `${}` |
| 查询结果为空 | `resultType` / `resultMap` |
| 字段映射不上 | 驼峰映射 / `resultMap` |
| 一对多查询 | `collection` |
| 一对一查询 | `association` |
| 多对多查询 | 中间表 + `collection` |
| 批量查询/删除 | `foreach` |
| 动态 WHERE | `if` / `where` |
| 动态 UPDATE | `if` / `set` |
| 主键拿不到 | `useGeneratedKeys` / `keyProperty` |
| 事务不回滚 | Spring Transaction / `@Transactional` |
| 查询执行两次 | 一级缓存 / 嵌套查询 |
| 分页 | LIMIT / PageHelper / MyBatis-Plus |
| 类型转换 | TypeHandler |
| 缓存 | 一级缓存 / 二级缓存 |
| MyBatis-Plus 功能 | 第三方扩展，不是 MyBatis 核心 |

---

## 基础篇总结

- 默认用 `#{}`，只有动态表名、列名、排序字段才考虑 `${}`，并且必须白名单校验。
- 多参数一定加 `@Param`。
- 复杂映射用 `resultMap`，简单映射用 `resultType`。
- Spring Boot 项目优先使用构造器注入 Mapper。
- 事务交给 Spring `@Transactional`，不要手动 `commit/rollback`。
- MyBatis 缓存是应用层缓存，不要和 MySQL Buffer Pool 混淆。
- MyBatis-Plus 是第三方增强，不是 MyBatis 原生功能。

---
---

# 进阶篇

> 以下内容针对评价中提到的“原理深度偏浅”“批量与性能建议不足”“进阶主题未覆盖”等方向进行补充。所有内容仍以 **Java 17+、Spring Boot 3.x、MyBatis 3.5.x、mybatis-spring-boot-starter 3.x、MySQL 8.x** 为基准。

---

# 补充篇一：版本兼容性与依赖管理

## 1.1 mybatis-spring-boot-starter 版本矩阵

根据官方仓库的说明，各版本要求如下：

| Starter 版本 | MyBatis | MyBatis-Spring | Spring Boot | Java |
|---|---|---|---|---|
| 4.0.x | 3.5 | 4.0 | 4.0 | 17+ |
| 3.0.x | 3.5 | 3.0 | 3.2 – 3.5 | 17+ |
| 2.3.x | 3.5 | 2.1 | 2.5 – 2.7 | 8+ |

> ⚠️ 版本兼容性以官方兼容矩阵为准，生产项目建议通过父工程或 BOM 统一管理版本，避免在子模块中写死过旧版本。Spring Boot 3.x 必须使用 starter 3.x，底层要求 Java 17 和 Jakarta EE 9+。

## 1.2 MyBatis-Plus 与 Spring Boot 3.x 的版本匹配

从 Spring Boot 3.x 开始，推荐使用 MyBatis 3.5.x 系列。MyBatis-Plus 3.5.x 是与 Spring Boot 3.x 系列兼容的最佳选择。在实际项目中，需确保 MyBatis-Plus 依赖的 MyBatis 版本与 mybatis-spring-boot-starter 引入的 MyBatis 版本一致，否则可能报 `NoSuchMethodError`。

## 1.3 各进阶功能所需额外依赖

| 功能 | 需额外引入的依赖 | 说明 |
|---|---|---|
| Redis 二级缓存 | `org.mybatis.caches:mybatis-redis` | 兼容 MyBatis 3.4+ |
| `@MybatisTest` 切片测试 | `org.mybatis.spring.boot:mybatis-spring-boot-starter-test` | 提供 `mybatis-spring-boot-test-autoconfigure` |
| ShardingSphere 分库分表 | `org.apache.shardingsphere:shardingsphere-jdbc-core-spring-boot-starter` | 5.x 版本，支持 JDK17 |
| dynamic-datasource | `com.baomidou:dynamic-datasource-spring-boot-starter` | 提供 `@DS` 注解切换数据源 |

---

# 补充篇二：参数传递的精确边界

上一轮评价指出“单参数时 `#{}` 内名称可以任意”需要限定前提。精确结论如下：

| 参数类型 | `#{}` 内如何写 | 示例 |
|---|---|---|
| 单个简单类型（String、Integer、Long 等） | 任意名称，MyBatis 忽略 | `selectById(Long id)` → `#{anything}` |
| 单个对象（POJO / Map） | 必须写属性名或 Map key | `selectByStudent(Student s)` → `#{name}`、`#{age}` |
| 多参数（无 `@Param`） | `arg0/arg1`、`param1/param2`，或开启 `-parameters` 后用真实参数名 | `#{param1}`、`#{param2}` |
| 多参数（有 `@Param`） | 使用 `@Param` 指定的名称 | `@Param("name")` → `#{name}` |

核心原则：**多参数一律加 `@Param`**，不依赖编译器行为和隐式命名规则。

---

# 补充篇三：Executor 三种类型源码级区别

## 3.1 三种 Executor 对比

| 类型 | 触发方式 | Statement 策略 | 适用场景 |
|---|---|---|---|
| `SIMPLE`（默认） | `openSession()` | 每次执行新建 PreparedStatement，用完关闭 | 常规查询 |
| `REUSE` | `openSession(ExecutorType.REUSE)` | 以 SQL 为 key 缓存 Statement，复用同一 SQL 的 Statement | 同一 SQL 反复执行 |
| `BATCH` | `openSession(ExecutorType.BATCH)` | 攒批，调用 JDBC `addBatch`，直到 commit 或触发查询才批量执行 | 大批量写操作 |

## 3.2 执行器在调用链中的位置

```text
MapperProxy.invoke()
  → SqlSession.selectOne/insert/update
    → CachingExecutor.query/update   （二级缓存包装层）
      → SimpleExecutor / ReuseExecutor / BatchExecutor
        → StatementHandler
          → ParameterHandler + JDBC PreparedStatement
```

`CachingExecutor` 是所有 Executor 的外层包装，负责二级缓存查询和写入，内部委托给真正的 Executor。

---

# 补充篇四：MyBatis 插件（Interceptor）机制

## 4.1 可拦截的四大组件

| 拦截目标 | 接口 | 典型用途 |
|---|---|---|
| Executor | `org.apache.ibatis.executor.Executor` | 分页、读写分离、SQL 重写、执行时间统计 |
| StatementHandler | `org.apache.ibatis.executor.statement.StatementHandler` | SQL 改写、参数加工 |
| ParameterHandler | `org.apache.ibatis.executor.parameter.ParameterHandler` | 参数加密、参数校验 |
| ResultSetHandler | `org.apache.ibatis.executor.resultset.ResultSetHandler` | 结果集脱敏、字段填充 |

## 4.2 自定义 SQL 执行时间统计拦截器

```java
@Intercepts({
    @Signature(type = Executor.class, method = "update",
               args = {MappedStatement.class, Object.class}),
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class,
                       org.apache.ibatis.session.RowBounds.class,
                       org.apache.ibatis.session.ResultHandler.class})
})
public class SqlExecuteTimeInterceptor implements Interceptor {

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long elapsed = System.currentTimeMillis() - start;
            MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
            if (elapsed > 500) { // 慢 SQL 阈值
                System.err.println("慢 SQL [" + ms.getId() + "] 耗时 " + elapsed + "ms");
            }
        }
    }

    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }

    @Override
    public void setProperties(Properties properties) {
        // 可从配置读取阈值
    }
}
```

注册方式（Spring Boot）：

```java
@Configuration
public class MyBatisPluginConfig {

    @Bean
    public SqlExecuteTimeInterceptor sqlExecuteTimeInterceptor() {
        return new SqlExecuteTimeInterceptor();
    }
}
```

MyBatis 的插件基于 JDK 动态代理实现：`Plugin.wrap(target, interceptor)` 为目标对象生成代理，调用链经过 `InterceptorChain` 时依次执行 `intercept()`。`@Intercepts` 中的 `@Signature` 精确指定拦截哪个类的哪个方法。

---

# 补充篇五：批量操作性能优化

## 5.1 两种批量插入方式对比

| 方式 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| `<foreach>` 拼多值 INSERT | 一条 SQL 插入多行 | 简单，无额外配置 | 数据量大时 SQL 极长，受 `max_allowed_packet` 限制 |
| `ExecutorType.BATCH` | 攒批，JDBC `addBatch` | 分批可控，内存友好 | 需手动管理 SqlSession 和分批提交 |

```java
// ExecutorType.BATCH 方式
try (SqlSession session = sqlSessionFactory.openSession(ExecutorType.BATCH)) {
    StudentMapper mapper = session.getMapper(StudentMapper.class);
    int batchSize = 500;
    for (int i = 0; i < list.size(); i++) {
        mapper.insert(list.get(i));
        if ((i + 1) % batchSize == 0) {
            session.flushStatements();
        }
    }
    session.commit();
}
```

## 5.2 关键性能参数

在 JDBC URL 中添加：

```text
jdbc:mysql://localhost:3306/db?rewriteBatchedStatements=true
```

`rewriteBatchedStatements=true` 让 MySQL 驱动将多条 INSERT 合并为一条高效的多值 INSERT。不配这个参数时，`ExecutorType.BATCH` 的性能通常远低于理论值，可能差一个数量级。配合 `ExecutorType.BATCH` 使用效果最明显。

## 5.3 大批量写入的推荐策略

```text
数据量 < 1000 条：  <foreach> 多值 INSERT 即可
数据量 1000 – 1万： ExecutorType.BATCH + rewriteBatchedStatements=true，分批 flush
数据量 > 1万：      生成 CSV 后 LOAD DATA INFILE，或分片写入
```

同时注意：增大 MySQL `max_allowed_packet`；批量插入期间可临时关闭非必要索引，插入后重建；设置 `flushCache=true` 避免一级缓存干扰。

---

# 补充篇六：缓存生产实践深化

## 6.1 二级缓存一致性挑战

MyBatis 二级缓存以 **Mapper namespace** 为单位。当多表关联查询时，跨 namespace 更新会导致脏读：

```text
OrderMapper 缓存了包含用户信息的订单
UserMapper 更新了用户信息
→ OrderMapper 缓存不会自动失效 → 脏读
```

解决方案：使用 `<cache-ref>` 让关联 Mapper 共享缓存刷新：

```xml
<!-- OrderMapper.xml -->
<cache/>
<cache-ref namespace="com.example.mapper.UserMapper"/>
```

这样 UserMapper 的任何写操作都会同时刷新 OrderMapper 的缓存。但需注意：`cache-ref` 共享缓存虽然能解决跨 namespace 脏读，也会让缓存依赖更复杂，需谨慎使用。

## 6.2 分布式场景：Redis 二级缓存

MyBatis 原生二级缓存基于 JVM 本地内存，集群环境下各节点缓存不共享。集成 Redis 需要额外引入依赖：

```xml
<dependency>
    <groupId>org.mybatis.caches</groupId>
    <artifactId>mybatis-redis</artifactId>
    <version>1.0.0-beta2</version>
</dependency>
```

然后在 Mapper 上配置：

```java
@CacheNamespace(implementation = RedisCache.class)
public interface IUserMapper { ... }
```

同时需要在 `resources` 根目录添加 `redis.properties` 配置文件：

```properties
host=localhost
port=6379
password=
database=0
```

实体类必须实现 `Serializable`。Redis 缓存使所有节点共享同一缓存区域，解决分布式一致性问题。

## 6.3 缓存副作用防控

| 风险 | 场景 | 对策 |
|---|---|---|
| 长会话脏读 | 一级缓存中 SqlSession 生命周期过长 | 设置 `local-cache-scope: statement` |
| 批量处理读到过期数据 | 循环中重复查询相同数据 | `@Options(flushCache = TRUE)` |
| 缓存击穿 | 热点 key 失效瞬间大量请求打到数据库 | 互斥锁重建缓存 |
| 缓存雪崩 | 大量 key 同时过期 | 过期时间加随机偏移 |

```yaml
mybatis:
  configuration:
    local-cache-scope: statement   # 每次查询后清空一级缓存
```

## 6.4 生产环境建议

**不要盲目开启二级缓存。** 数据更新频繁、多表关联复杂、分布式环境下，二级缓存带来的不一致风险往往大于收益。如果确实需要缓存，优先考虑在 Service 层使用 Spring Cache + Redis，控制粒度更精细，与业务逻辑耦合更清晰。

---

# 补充篇七：事务生产细节

## 7.1 传播行为速查

| 传播行为 | 含义 | 典型场景 |
|---|---|---|
| `REQUIRED`（默认） | 有事务加入，无则新建 | 绝大多数业务方法 |
| `REQUIRES_NEW` | 总是新建事务，挂起当前 | 日志记录、审计 |
| `NESTED` | 嵌套事务，可独立回滚 | 批量操作中单条失败不影响其他 |
| `SUPPORTS` | 有则加入，无则非事务执行 | 只读查询 |
| `NOT_SUPPORTED` | 非事务执行，挂起当前 | 耗时操作不占用事务 |

> ⚠️ `NESTED` 传播行为依赖 JDBC savepoint，不是所有数据库/驱动都支持，使用前需确认数据库兼容性。

## 7.2 隔离级别与只读事务

```java
@Transactional(
    isolation = Isolation.READ_COMMITTED,
    readOnly = true,
    timeout = 30
)
public Student getById(Long id) {
    return studentMapper.selectById(id);
}
```

`readOnly = true` 对 MySQL InnoDB 本身不改变读行为，但可作为语义提示，且某些连接池会据此优化。生产环境一般使用数据库默认隔离级别（MySQL 为 `REPEATABLE READ`）。

## 7.3 自调用失效与解决方案

```java
@Service
public class OrderService {

    public void createOrder() {
        this.deductStock();  // ❌ 自调用，@Transactional 失效
    }

    @Transactional
    public void deductStock() { ... }
}
```

原因：Spring AOP 代理只拦截外部调用。解决方案：注入自身代理、拆分为独立 Service、或使用 `AopContext.currentProxy()`。

---

# 补充篇八：延迟加载与 N+1 问题

## 8.1 延迟加载配置

```yaml
mybatis:
  configuration:
    lazy-loading-enabled: true
    aggressive-lazy-loading: false   # 必须关闭，否则延迟加载形同虚设
```

`aggressiveLazyLoading=true`（旧版默认）会在调用任意方法时加载所有延迟属性；设为 `false` 后，只有真正调用关联属性的 getter 时才触发加载。

## 8.2 N+1 问题

```text
1 次查询班级列表
+ N 次查询每个班级的学生列表
= N+1 次查询
```

解决方案：

| 方案 | 做法 | 效果 |
|---|---|---|
| JOIN + resultMap | 用 `<collection>` 嵌套结果映射，一次 JOIN 查出所有数据 | 彻底消除 N+1 |
| 批量查询 | 先查主表，再用 `IN` 批量查关联表 | 从 N+1 降到 2 次 |
| `fetchType="eager"` | 关联数据确定常用时立即加载 | 减少触发次数，但可能浪费 |

推荐：**关联数据确定需要时用 JOIN 嵌套结果映射**；关联数据可能不需要时用延迟加载 + 批量查询兜底。

---

# 补充篇九：多数据源与动态数据源

## 9.1 非 MyBatis-Plus 方案

Spring Boot 原生多数据源需要：

```text
1. 禁用 DataSourceAutoConfiguration
2. 手动配置多个 DataSource Bean
3. 为每个数据源配置独立的 SqlSessionFactory 和 MapperScan
4. 通过 @Qualifier 注入对应数据源
```

```java
@Configuration
@MapperScan(basePackages = "com.example.mapper.primary",
            sqlSessionFactoryRef = "primarySqlSessionFactory")
public class PrimaryDataSourceConfig { ... }

@Configuration
@MapperScan(basePackages = "com.example.mapper.secondary",
            sqlSessionFactoryRef = "secondarySqlSessionFactory")
public class SecondaryDataSourceConfig { ... }
```

## 9.2 dynamic-datasource（第三方扩展）

Baomidou 的 `dynamic-datasource-spring-boot-starter` 提供注解切换：

```java
@Service
public class UserService {

    @DS("master")
    public void write(User user) { ... }

    @DS("slave")
    public User read(Long id) { ... }
}
```

```yaml
spring:
  datasource:
    dynamic:
      primary: master
      datasource:
        master:
          url: jdbc:mysql://master-host:3306/db
        slave:
          url: jdbc:mysql://slave-host:3306/db
```

支持数据源分组、读写分离、`@DS` 方法级/类级切换、方法级优先级高于类级。

## 9.3 读写分离实现

基于 `dynamic-datasource` 的读写分离方案：

```text
1. 配置 master 和 slave 数据源
2. 写操作使用 @DS("master")，读操作使用 @DS("slave")
3. 或使用 AOP 切面根据方法前缀（select/query/get vs insert/update/delete）自动路由
4. 在事务中强制走主库，确保“写后立即读”能读到最新数据
```

> ⚠️ 读写分离下，“写后立即读”可能因主从复制延迟而读不到最新数据。解决方案：在事务中强制走主库，或使用 `@DS("master")` 显式指定。

---

# 补充篇十：SQL 审计与监控

## 10.1 基于 Interceptor 的 SQL 审计

```java
@Intercepts({
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class,
                       RowBounds.class, ResultHandler.class}),
    @Signature(type = Executor.class, method = "update",
               args = {MappedStatement.class, Object.class})
})
public class SqlAuditInterceptor implements Interceptor {

    private static final Logger log = LoggerFactory.getLogger(SqlAuditInterceptor.class);

    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
        Object parameter = invocation.getArgs().length > 1 ? invocation.getArgs()[1] : null;
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            log.info("SQL_AUDIT | id={} | cost={}ms | param={}",
                     ms.getId(), cost, parameter);
        }
    }
}
```

拦截器可在 `intercept` 中获取 SQL 语句、参数信息、执行时间等关键数据，实现日志审计。

## 10.2 生产配置提醒

开发阶段可临时使用：

```yaml
mybatis:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

**生产环境不要使用 `StdOutImpl`**，应使用 SLF4J 桥接，通过日志框架控制级别和输出目标：

```yaml
logging:
  level:
    com.example.mapper: DEBUG   # 只对指定 Mapper 包开 SQL 日志
```

生产环境建议：禁止在配置中硬编码数据库账号密码，应通过环境变量或配置中心动态注入，防止敏感信息泄露到代码仓库。

## 10.3 MyBatis 语句超时控制

MyBatis 提供了 `defaultStatementTimeout` 全局配置和 Mapper 级别的 `timeout` 属性，精准控制单条 SQL 的最大执行时长：

```yaml
mybatis:
  configuration:
    default-statement-timeout: 30   # 单位：秒
```

```xml
<select id="selectLargeData" timeout="10">
    ...
</select>
```

> ⚠️ `socketTimeout` 必须大于 MyBatis 语句超时、事务超时，避免上层提前终止而网络层还未触发。

---

# 补充篇十一：测试方案

## 11.1 分层测试策略

| 层次 | 测试内容 | 工具 |
|---|---|---|
| Mapper 接口测试 | 接口与 XML 映射是否正确 | `@MybatisTest`（切片测试） |
| SQL 映射测试 | 动态 SQL 分支是否覆盖 | `@MybatisTest` + H2 |
| 数据库集成测试 | SQL 在真实 MySQL 上的行为 | `@SpringBootTest` + Testcontainers |

## 11.2 @MybatisTest 切片测试

需要引入依赖：

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter-test</artifactId>
    <version>3.0.3</version>
    <scope>test</scope>
</dependency>
```

```java
@MybatisTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class StudentMapperTest {

    @Autowired
    private StudentMapper studentMapper;

    @Test
    void selectById_shouldReturnStudent() {
        Student student = studentMapper.selectById(1L);
        assertThat(student).isNotNull();
        assertThat(student.getName()).isEqualTo("Tom");
    }
}
```

`@MybatisTest` 只加载 MyBatis 相关配置，不启动整个 Spring 上下文，速度远快于 `@SpringBootTest`。默认情况下，它配置 MyBatis 组件、Mapper 接口和内存数据库，且测试基于事务并在结尾回滚。

---

# 补充篇十二：ExecutorType.BATCH 与 `<foreach>` 的选型决策

| 维度 | `<foreach>` 多值 INSERT | `ExecutorType.BATCH` |
|---|---|---|
| SQL 长度 | 随数据量线性增长 | 恒定 |
| 内存占用 | 需一次性构建完整 SQL | 流式，内存友好 |
| 网络交互 | 1 次 | 分批 N 次（可控） |
| 主键回填 | 支持 | 支持（需 `useGeneratedKeys`） |
| 配置复杂度 | 零 | 需管理 SqlSession |
| MySQL 优化 | 依赖 `max_allowed_packet` | 依赖 `rewriteBatchedStatements` |
| 推荐数据量 | < 1000 | 1000 – 1万 |

---

# 补充篇十三：常见生产问题速查

| 问题 | 优先检查 |
|---|---|
| 批量插入慢 | `rewriteBatchedStatements=true` 是否配置；是否用了 `ExecutorType.BATCH`；是否分批 flush |
| 内存暴增 | `aggressiveLazyLoading` 是否误开；是否在循环中触发延迟加载 |
| 缓存脏读 | 二级缓存是否跨 namespace；是否用 `<cache-ref>`；是否需要改用 Redis |
| 多数据源切换失败 | `@DS` 是否生效；方法级注解是否被类级覆盖；是否在自调用中 |
| 插件不生效 | `@Intercepts` 签名是否匹配；是否注册为 Spring Bean |
| Spring Boot 3 升级报错 | starter 是否升级到 3.x；是否使用 Jakarta 命名空间 |
| N+1 查询 | 是否在循环中调用 Mapper；是否该用 JOIN + `collection` 嵌套结果映射 |
| 慢 SQL 无法定位 | 是否配置了 SQL 审计拦截器；是否只对特定 Mapper 包开了 DEBUG 日志 |

---
---

# 深度篇：源码级原理补充

> 以下内容针对评价中“源码深度仍有限”的反馈，补充 MyBatis 核心组件的源码级调用流程。目标是理解“为什么能工作”，而非逐行分析源码。

---

# 深度篇一：MapperProxy 源码调用流程

## 1.1 getMapper 的调用链

调用 `sqlSession.getMapper(StudentMapper.class)` 时，源码流程如下：

```text
SqlSession.getMapper(Class<T> type)
  → Configuration.getMapper(type, this)
    → MapperRegistry.getMapper(type, sqlSession)
      → knownMappers.get(type)        // 获取 MapperProxyFactory
        → mapperProxyFactory.newInstance(sqlSession)
          → MapperProxy 实例（JDK 动态代理）
```

`MapperRegistry` 内部维护了一个 `Map<Class<?>, MapperProxyFactory<?>> knownMappers`，在 MyBatis 初始化时，通过 `XMLConfigBuilder.parseConfiguration()` 解析 `<mappers>` 节点，将 Mapper 接口和对应的 `MapperProxyFactory` 注册进去。

## 1.2 MapperProxy.invoke() 的执行逻辑

`MapperProxy` 实现了 `InvocationHandler` 接口，核心方法 `invoke()` 的关键逻辑：

```java
public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
    // 1. 如果方法是 Object 的默认方法（如 toString、equals），直接执行
    if (Object.class.equals(method.getDeclaringClass())) {
        return method.invoke(this, args);
    }
    // 2. 获取或创建 MapperMethod 缓存
    MapperMethod mapperMethod = cachedMapperMethod(method);
    // 3. 执行 MapperMethod
    return mapperMethod.execute(sqlSession, args);
}
```

`MapperMethod` 是核心执行类，内部持有 `SqlCommand`（封装了 `namespace + id`）和 `MethodSignature`（封装了方法参数、返回值等信息）。`MapperMethod.execute()` 根据方法返回类型和 SQL 命令类型，最终调用 `sqlSession.selectOne()`、`sqlSession.insert()` 等方法。

## 1.3 Mapper 接口与 XML 的绑定时机

Mapper 接口与 XML 的绑定发生在 MyBatis 初始化阶段：

```text
SqlSessionFactoryBuilder.build(InputStream)
  → XMLConfigBuilder.parse()
    → XMLConfigBuilder.parseConfiguration()
      → mapperElement(XNode)           // 解析 <mappers> 节点
        → XMLMapperBuilder.parse()
          → XMLMapperBuilder.configurationElement()
            → XMLMapperBuilder.bindMapperForNamespace()
              → MapperRegistry.addMapper(type)
                → knownMappers.put(type, new MapperProxyFactory<>(type))
```

`XMLMapperBuilder.bindMapperForNamespace()` 的关键逻辑是：如果 `namespace` 对应的接口存在且尚未注册，则将其注册到 `MapperRegistry` 中。同时，`XMLStatementBuilder` 解析每个 `<select>`、`<insert>` 等标签，生成 `MappedStatement` 对象，存入 `Configuration.mappedStatements`。

---

# 深度篇二：Configuration 解析 XML 的过程

## 2.1 解析入口

MyBatis 通过 `XMLConfigBuilder` 解析全局配置文件，通过 `XMLMapperBuilder` 解析 Mapper XML 文件：

```text
XMLConfigBuilder.parse()
  → Configuration 实例创建
  → parseConfiguration(XNode root)
    → propertiesElement()          // <properties>
    → settingsAsProperties()       // <settings>
    → typeAliasesElement()         // <typeAliases>
    → pluginsElement()             // <plugins>
    → objectFactoryElement()       // <objectFactory>
    → environmentsElement()        // <environments>
    → typeHandlerElement()         // <typeHandlers>
    → mapperElement()              // <mappers>
```

## 2.2 Mapper XML 的解析过程

`XMLMapperBuilder.configurationElement()` 解析 `<mapper>` 节点的核心流程：

```text
<mapper namespace="...">
  → cacheElement()                 // <cache> 二级缓存
  → cacheRefElement()              // <cache-ref>
  → resultMapElements()            // <resultMap>
  → sqlElement()                   // <sql> 可复用片段
  → buildStatementFromContext()    // <select>/<insert>/<update>/<delete>
    → XMLStatementBuilder.parseStatementNode()
      → MappedStatement 构建
        → Configuration.addMappedStatement()
```

每个 `<select>` 标签最终被解析为一个 `MappedStatement` 对象，存入 `Configuration.mappedStatements`（一个 `StrictMap<String, MappedStatement>`，key 为 `namespace + "." + id`）。

## 2.3 Configuration 的核心数据结构

| 字段 | 类型 | 说明 |
|---|---|---|
| `mappedStatements` | `Map<String, MappedStatement>` | 所有 SQL 映射，key = namespace + id |
| `resultMaps` | `Map<String, ResultMap>` | 所有结果映射 |
| `parameterMaps` | `Map<String, ParameterMap>` | 所有参数映射 |
| `caches` | `Map<String, Cache>` | 所有二级缓存 |
| `interceptorChain` | `InterceptorChain` | 插件链 |
| `typeHandlerRegistry` | `TypeHandlerRegistry` | 类型处理器注册表 |
| `languageRegistry` | `LanguageDriverRegistry` | 语言驱动注册表 |

---

# 深度篇三：一级缓存与二级缓存源码

## 3.1 一级缓存：PerpetualCache

一级缓存实现在 `BaseExecutor` 中，使用 `PerpetualCache` 作为底层存储。`PerpetualCache` 的默认实现极其简单，内部就是一个 `HashMap`：

```java
public class PerpetualCache implements Cache {
    private final String id;
    private final Map<Object, Object> cache = new HashMap<>();
    // putObject / getObject / removeObject 直接委托给 HashMap
}
```

`BaseExecutor.query()` 中一级缓存的查询逻辑：

```java
public <E> List<E> query(MappedStatement ms, Object parameter, ...) {
    if (queryStack == 0 && ms.isFlushCacheRequired()) {
        clearLocalCache();  // flushCache = true 时清空
    }
    List<E> list;
    try {
        queryStack++;
        list = resultHandler == null ? (List<E>) localCache.getObject(key) : null;
        if (list != null) {
            handleLocallyCachedOutputParameters(ms, key, parameter, boundSql);
        } else {
            list = queryFromDatabase(ms, parameter, rowBounds, resultHandler, key, boundSql);
        }
    } finally {
        queryStack--;
    }
    return list;
}
```

## 3.2 二级缓存：CachingExecutor 与 TransactionalCacheManager

二级缓存通过 `CachingExecutor` 装饰 `BaseExecutor` 实现。`CachingExecutor` 内部持有 `TransactionalCacheManager`，管理事务提交/回滚时的缓存写入：

```java
public class CachingExecutor implements Executor {
    private final Executor delegate;
    private final TransactionalCacheManager tcm = new TransactionalCacheManager();

    public <E> List<E> query(MappedStatement ms, Object parameter, ...) {
        Cache cache = ms.getCache();
        if (cache != null) {
            flushCacheIfRequired(ms);
            if (ms.isUseCache() && resultHandler == null) {
                List<E> list = (List<E>) tcm.getObject(cache, key);
                if (list == null) {
                    list = delegate.query(ms, parameter, rowBounds, resultHandler, key, boundSql);
                    tcm.putObject(cache, key, list);
                }
                return list;
            }
        }
        return delegate.query(ms, parameter, rowBounds, resultHandler, key, boundSql);
    }
}
```

`TransactionalCacheManager` 内部维护 `Map<Cache, TransactionalCache>`，`TransactionalCache` 的核心机制是：查询结果先暂存在 `entriesToAddOnCommit` 中，只有事务提交时才批量写入真正的二级缓存；如果事务回滚，则清空暂存区。

## 3.3 二级缓存的装饰器链

二级缓存默认使用 `PerpetualCache`，但可以通过装饰器叠加功能：

```text
PerpetualCache（基础 HashMap）
  → LruCache（LRU 淘汰策略）
    → SerializedCache（序列化/反序列化）
      → LoggingCache（日志统计）
        → SynchronizedCache（线程安全）
```

装饰顺序由 `<cache>` 标签的 `eviction` 属性决定，默认是 `LRU`。

---

# 深度篇四：Plugin 代理链与 InterceptorChain 源码

## 4.1 Plugin.wrap 的代理逻辑

`Plugin` 类实现了 `InvocationHandler`，`wrap()` 方法的核心逻辑：

```java
public static Object wrap(Object target, Interceptor interceptor) {
    Map<Class<?>, Set<Method>> signatureMap = getSignatureMap(interceptor);
    Class<?> type = target.getClass();
    Class<?>[] interfaces = getAllInterfaces(type, signatureMap);
    if (interfaces.length > 0) {
        return Proxy.newProxyInstance(
            type.getClassLoader(),
            interfaces,
            new Plugin(target, interceptor, signatureMap));
    }
    return target;
}
```

`getSignatureMap()` 解析 `@Intercepts` 和 `@Signature` 注解，得到“需要拦截的类 -> 需要拦截的方法集合”的映射。`getAllInterfaces()` 过滤出目标对象实现的、且在签名映射中存在的接口。

## 4.2 InterceptorChain.pluginAll()

`InterceptorChain` 维护一个 `List<Interceptor>`，在创建 Executor、StatementHandler 等核心组件时，依次应用所有拦截器：

```java
public Object pluginAll(Object target) {
    for (Interceptor interceptor : interceptors) {
        target = interceptor.plugin(target);
    }
    return target;
}
```

因此，如果有三个拦截器，最终的代理链是：

```text
Interceptor3(Interceptor2(Interceptor1(目标对象)))
```

调用时先经过 Interceptor3，再经过 Interceptor2，再经过 Interceptor1，最后到达目标对象。这就是 MyBatis 插件的“洋葱式”责任链。

## 4.3 插件在 Configuration 中的注册

插件在 `Configuration` 初始化时通过 `interceptorChain.addInterceptor()` 注册。在 Spring Boot 中，任何实现了 `Interceptor` 接口的 Spring Bean 会被 `MybatisAutoConfiguration` 自动注册到 `Configuration` 中。

---

# 深度篇五：SqlSessionTemplate 线程安全原理

## 5.1 DefaultSqlSession 为什么线程不安全

`DefaultSqlSession` 线程不安全的原因有两个：

1. **Connection 不是线程安全的**：`DefaultSqlSession` 持有 `Executor`，`Executor` 持有 `Transaction`（通常是 `JdbcTransaction`），`JdbcTransaction` 持有 `Connection`。如果多个线程共享同一个 `SqlSession`，它们将使用同一个 `Connection`，导致事务混乱。
2. **一级缓存使用 HashMap**：`BaseExecutor` 中的 `localCache` 是 `PerpetualCache`，底层是 `HashMap`，不是线程安全的。

## 5.2 SqlSessionTemplate 的 ThreadLocal 机制

`SqlSessionTemplate` 通过 JDK 动态代理和 `ThreadLocal` 实现线程安全：

```java
public class SqlSessionTemplate implements SqlSession {
    private final SqlSessionFactory sqlSessionFactory;
    private final ExecutorType executorType;
    private final SqlSession sqlSessionProxy;

    public SqlSessionTemplate(SqlSessionFactory sqlSessionFactory, ...) {
        this.sqlSessionProxy = (SqlSession) newProxyInstance(
            SqlSessionFactory.class.getClassLoader(),
            new Class[] { SqlSession.class },
            new SqlSessionInterceptor());
    }

    private class SqlSessionInterceptor implements InvocationHandler {
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            SqlSession sqlSession = getSqlSession(sqlSessionFactory, executorType, exceptionTranslator);
            try {
                Object result = method.invoke(sqlSession, args);
                if (!isSqlSessionTransactional(sqlSession, sqlSessionFactory)) {
                    sqlSession.commit(true);
                }
                return result;
            } catch (Throwable t) {
                // 异常时回滚
                throw t;
            } finally {
                if (sqlSession != null) {
                    closeSqlSession(sqlSession, sqlSessionFactory);
                }
            }
        }
    }
}
```

关键点：

- `SqlSessionTemplate` 本身是单例，但每次方法调用都通过 `SqlSessionInterceptor` 获取一个 `SqlSession`。
- `getSqlSession()` 内部使用 `TransactionSynchronizationManager` 的 `ThreadLocal<Map<Object, Object>>` 保存每个线程对应的 `SqlSession`，确保同一线程内复用同一个 `SqlSession`，不同线程之间互不干扰。
- 如果当前线程已在 Spring 事务中，`isSqlSessionTransactional()` 返回 `true`，不会自动提交，由 Spring 事务管理器统一提交/回滚。

---

# 深度篇六：MyBatis-Plus 高级用法

【第三方扩展】

## 6.1 LambdaQueryWrapper 类型安全查询

`LambdaQueryWrapper` 是 MyBatis-Plus 提供的类型安全条件构造器，通过方法引用指定字段，编译期即可校验字段是否存在：

```java
@Service
public class StudentService {

    private final StudentMapper studentMapper;

    public StudentService(StudentMapper studentMapper) {
        this.studentMapper = studentMapper;
    }

    public List<Student> query(StudentQuery query) {
        LambdaQueryWrapper<Student> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.hasText(query.getName()), Student::getName, query.getName())
               .eq(query.getAge() != null, Student::getAge, query.getAge())
               .ge(query.getMinScore() != null, Student::getScore, query.getMinScore())
               .orderByDesc(Student::getScore);
        return studentMapper.selectList(wrapper);
    }
}
```

相比 `QueryWrapper` 的字符串字段名，`LambdaQueryWrapper` 避免了硬编码字段名，重构时更安全。

## 6.2 代码生成器 FastAutoGenerator

MyBatis-Plus 3.5.1+ 推荐使用 `FastAutoGenerator` 替代旧的 `AutoGenerator`：

```java
public class CodeGenerator {
    public static void main(String[] args) {
        FastAutoGenerator.create(
                "jdbc:mysql://localhost:3306/order_db",
                "root", "123456")
            .globalConfig(builder -> builder
                .author("dev")
                .outputDir(System.getProperty("user.dir") + "/src/main/java")
                .disableOpenDir())
            .packageConfig(builder -> builder
                .parent("com.example")
                .moduleName("order")
                .entity("entity")
                .mapper("mapper")
                .service("service")
                .controller("controller"))
            .strategyConfig(builder -> builder
                .addInclude("order", "order_item")
                .addTablePrefix("t_", "order_")
                .entityBuilder()
                    .enableLombok()
                    .logicDeleteColumnName("deleted")
                .controllerBuilder()
                    .enableRestStyle())
            .execute();
    }
}
```

## 6.3 公共字段自动填充

通过 `MetaObjectHandler` 实现创建时间、更新时间的自动填充：

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, LocalDateTime.now());
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime", LocalDateTime.class, LocalDateTime.now());
    }
}
```

实体类字段标注：

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createTime;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updateTime;
```

---

# 深度篇七：分库分表实践（ShardingSphere）

【第三方扩展】

## 7.1 ShardingSphere-JDBC 与 MyBatis 的协同

ShardingSphere-JDBC 是一个 JDBC 驱动层解决方案，嵌入应用内部，无需额外部署。它拦截 SQL 并进行分库分表的路由、改写和结果归并，对业务代码几乎无侵入。MyBatis-Plus 负责 ORM 和单表操作增强，ShardingSphere-JDBC 负责 SQL 路由，两者是协同工作的关系。

## 7.2 核心依赖

```xml
<!-- ShardingSphere-JDBC -->
<dependency>
    <groupId>org.apache.shardingsphere</groupId>
    <artifactId>shardingsphere-jdbc-core-spring-boot-starter</artifactId>
    <version>5.3.2</version>
</dependency>
<!-- MyBatis-Plus -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.3.1</version>
</dependency>
```

## 7.3 分片配置示例

以电商订单系统为例：日均订单 100 万，按 `order_id` 哈希取模分 2 个库，每个库分 16 张表：

```yaml
spring:
  shardingsphere:
    datasource:
      names: order_db_0, order_db_1
      order_db_0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/order_db_0
        username: root
        password: 123456
      order_db_1:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/order_db_1
        username: root
        password: 123456
    rules:
      sharding:
        tables:
          order:
            actual-data-nodes: order_db_${0..1}.order_${0..15}
            database-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: db-hash-mod
            table-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: table-hash-mod
        sharding-algorithms:
          db-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 2
          table-hash-mod:
            type: HASH_MOD
            props:
              sharding-count: 16
```

## 7.4 常见坑

- **绑定表**：订单表和订单项表使用相同的分片规则时，需配置为绑定表，避免笛卡尔积关联。
- **广播表**：字典表等小表可配置为广播表，在所有库中冗余存储。
- **分布式主键**：ShardingSphere 集成雪花算法，配置机器标识确保不同节点生成的 ID 不重复。

---
