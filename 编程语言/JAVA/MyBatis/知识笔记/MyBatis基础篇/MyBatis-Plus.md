# 《MyBatis-Plus 完整学习与开发速查笔记》

> **适用环境**：Java 17+、Spring Boot 3.x、MyBatis-Plus 3.5.x、MySQL 8.x。  
> **示例版本**：MyBatis-Plus `3.5.17`（以官方文档中当前展示的稳定版本为例；项目中统一管理版本）。  
> **定位**：这是**独立的 MyBatis-Plus 补充笔记**，不重复原生 MyBatis 的 XML、事务和核心执行流程。  
> **标记说明**：  
> 【MP 增强】= MyBatis-Plus 提供；【原生 MyBatis】= MyBatis 本身具备；⚠️ 易混淆 = 开发中常见错误。

---

# 第一篇：MyBatis-Plus 基础认知

## 1. MyBatis-Plus 是什么

【**MP 增强**】

MyBatis-Plus（MP）是**基于 MyBatis 的增强工具**。它不是新数据库，也不是独立替代 MyBatis 的另一套持久层框架。

```text
Spring Boot / Service
        ↓
Mapper 接口（继承 BaseMapper）
        ↓
MyBatis-Plus（通用 CRUD / Wrapper / 插件）
        ↓
MyBatis（SqlSession / Executor / JDBC）
        ↓
MySQL
```

- **原生 MyBatis**：通常自己写 SQL，再由 Mapper 绑定执行。
- **MyBatis-Plus**：为**常规的单表 CRUD 自动提供方法和 SQL**；复杂 SQL 仍可手写。
- **它解决的问题**：减少重复的 Mapper 方法、XML 和简单条件拼接。
- **它不解决的问题**：业务逻辑设计、数据库设计、索引优化、事务设计、所有复杂 JOIN 查询。

> [!tip]
> **一句话：MyBatis-Plus = MyBatis + 通用 CRUD + 条件构造器 + 常用增强插件。**

### 1.1 MyBatis 与 MyBatis-Plus 对比

| 对比项 | 原生 MyBatis | MyBatis-Plus |
|---|---|---|
| 基础 CRUD | 写接口 + SQL/XML（或注解） | 继承 `BaseMapper<T>` 即可使用 |
| 单表条件查询 | XML 动态 SQL | `QueryWrapper` / `LambdaQueryWrapper` |
| 单表条件更新 | XML 动态 SQL | `UpdateWrapper` / `LambdaUpdateWrapper` |
| 分页 | 手写 `LIMIT` 或用分页扩展 | `Page` + `PaginationInnerInterceptor` |
| 多表复杂 SQL | 自己写 SQL | **依旧推荐自己写 SQL** |
| Spring 事务 | 支持 | 继续使用 Spring 事务 |
| MyBatis 底层 | MyBatis | **仍然是 MyBatis** |

⚠️ **易混淆**：`BaseMapper`、`IService`、`QueryWrapper`、`LambdaQueryWrapper`、`@TableName`、`@TableLogic` 都不是原生 MyBatis 的 API。

---

# 第二篇：Spring Boot 项目整合

## 2. Maven 依赖

【**MP 增强**】Spring Boot **3.x** 使用：

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
    <version>3.5.17</version>
</dependency>

<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <scope>runtime</scope>
</dependency>
```

如需使用 **MP 分页插件**（从 MP `3.5.9` 开始需单独添加）：

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-jsqlparser</artifactId>
    <version>3.5.17</version>
</dependency>
```

> [!warning]
> **不要在同一项目中再主动叠加** `mybatis-spring-boot-starter`、单独的 `mybatis`、`mybatis-spring`，以免出现依赖和自动配置冲突。已有原生 MyBatis 项目改为 MP 时，应调整原来的 Starter 依赖，而不是无条件全部保留。

## 3. application.yml

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/school?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: dev
    password: ${DB_PASSWORD}
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.example.entity
  configuration:
    map-underscore-to-camel-case: true
    # 仅开发环境排查 SQL 时使用：
    # log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
```

- `mapper-locations`：定位**自己手写的 XML**，不是 `BaseMapper` 的必需条件。
- `map-underscore-to-camel-case`：把 `class_name` 映射到 `className`。
- `type-aliases-package`：给 XML 中使用的结果类型等注册别名。
- MP 的配置前缀是 `mybatis-plus`，不是原生 Starter 的 `mybatis`。

## 4. Mapper 扫描

```java
@SpringBootApplication
@MapperScan("com.example.mapper")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

`@MapperScan` 来自 MyBatis-Spring，MP 整合后**仍可使用**。也可按接口逐个加 `@Mapper`。

---

# 第三篇：实体映射与常用注解

## 5. 表、主键、字段对应关系

沿用 `school.student` 表：

```sql
CREATE TABLE student (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT,
    gender VARCHAR(10),
    score DECIMAL(5,2),
    class_name VARCHAR(50)
);
```

```java
@TableName("student")
public class Student {
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String name;
    private Integer age;
    private String gender;
    private BigDecimal score;

    @TableField("class_name")
    private String className;

    @TableField(exist = false)
    private String displayText; // Java 临时字段，不对应数据库列

    // 省略 getter / setter；使用 LambdaWrapper 时须有相应 getter
}
```

| 注解 / 枚举 | 含义 |
|---|---|
| `@TableName("student")` | 指定实体类对应的**数据库表** |
| `@TableId("id")` | 指定实体类中的**主键字段及主键生成策略** |
| `IdType.AUTO` | 表示使用数据库自身的自增主键机制，而不是由 MP 提前生成主键 |
| `IdType.ASSIGN_ID` | MP 分配主键 ID（与数据库自增机制不同） |
| `@TableField("class_name")` | Java 属性与数据库列显式对应 |
| `@TableField(exist = false)` | 属性不参与数据库表字段映射 |
| `@TableField(fill = ...)` | 配合自动填充处理器使用 |
| `@TableLogic` | 逻辑删除字段 |
| `@Version` | 乐观锁版本字段 |

> [!tip]
> **实体类是映射配置的入口，`BaseMapper<Student>` 中的 `Student` 告诉 MP 操作哪种实体。**

> [!warning] 易混淆
> 
> - 对于已有 MySQL `AUTO_INCREMENT` 主键，应显式用 `IdType.AUTO`，不要误以为 MP 默认主键生成策略就等同于数据库自增  
> - `IdType.AUTO`：由 MySQL 生成主键：
>    - Java 应用端： INSERT 不带 id → MySQL： `AUTO_INCREMENT` 生成 → 返回 Java 应用端 → MP 回填。对应 `IdType.AUTO`。
> - `IdType.ASSIGN_ID`：由 MyBatis-Plus 在 Java 应用侧生成主键，再发送给 MySQL 补充进来
>   - Java 应用端：在插入前生成 ID → MySQL： 接收应用生成的 ID 并插入。对应 `IdType.ASSIGN_ID` 或 `IdType.INPUT`。
> - 表是 `AUTO_INCREMENT` 时必须显式写 `IdType.AUTO`；MP 默认策略通常是 `ASSIGN_ID`，是**在 Java 应用侧生成主键**，不等于数据库自增。
> - **MP 默认是在执行插入操作的过程中生成 `ID`，而不是创建 Java 对象时就生成**。 如果你需要在调用 `insert()` 之前把 `ID` 发送给其他服务，就需要提前显式生成并设置 `ID`。

---

# 第四篇：BaseMapper 与通用 CRUD

## 6. BaseMapper 是什么

【**MP 增强**】`BaseMapper<T>` 是包含常用单表 CRUD 方法的**通用 Mapper 接口**。

```java
public interface StudentMapper extends BaseMapper<Student> {
}
```

**无需为 `insert`、`selectById` 等基础方法再写 XML。**

```text
StudentMapper extends BaseMapper<Student>
        ↓
MP 读取 Student 实体和映射信息
        ↓
注入一组通用 SQL 对应的 MappedStatement
        ↓
Mapper 代理按 MyBatis 原有机制执行 SQL
```

- `extends`：让 `StudentMapper` 继承 `BaseMapper` 声明的方法。
- `<Student>`：泛型，限定这一组通用方法操作 `Student` 实体。
- 并非每次调用都“现场手写拼接完整 SQL”；MP 在框架初始化阶段提供通用方法的 SQL 映射定义，执行时由 MyBatis 处理。

## 7. 常用 CRUD 方法

```java
// INSERT
int rows1 = studentMapper.insert(student);

// SELECT
Student one = studentMapper.selectById(1L);
List<Student> all = studentMapper.selectList(null);
Long total = studentMapper.selectCount(null);

// UPDATE：根据实体主键更新（按默认策略处理字段）
int rows2 = studentMapper.updateById(student);

// DELETE：根据主键删除
int rows3 = studentMapper.deleteById(1L);
```

| BaseMapper 方法 | 作用 | 常见返回值 |
|---|---|---|
| `insert(entity)` | 新增一条 | `int` 影响行数 |
| `selectById(id)` | 根据主键查询 | `T` 或 `null` |
| `selectList(wrapper)` | 条件查询多条 | `List<T>` |
| `selectOne(wrapper)` | 查询唯一一条 | `T` 或 `null`，多条可能报错 |
| `selectCount(wrapper)` | 统计数量 | `Long` |
| `selectMaps(wrapper)` | 以 Map 返回列值 | `List<Map<String,Object>>` |
| `updateById(entity)` | 根据主键更新 | `int` 影响行数 |
| `update(entity, wrapper)` | 按条件更新 | `int` 影响行数 |
| `deleteById(id)` | 根据主键删除 | `int` 影响行数 |
| `delete(wrapper)` | 按条件删除 | `int` 影响行数 |
| `deleteByIds(ids)` | 根据多个主键删除（新版本） | `int` 影响行数 |
| `selectPage(page, wrapper)` | 分页查询 | `IPage<T>` |

### 7.1 原生 MyBatis 对照

```xml
<!-- 原生 MyBatis 写法：需要自己声明 SQL -->
<select id="selectById" resultType="Student">
    SELECT * FROM student WHERE id = #{id}
</select>
```

```java
// MP：通用语句无需为每个实体重复写
Student student = studentMapper.selectById(1L);
```

⚠️ **易混淆**：Mapper 层 CRUD 多数返回**影响行数 `int`**，而 Service 层常见方法多返回**`boolean`**。

---

# 第五篇：条件构造器 Wrapper

## 8. Wrapper 是什么

【**MP 增强**】Wrapper 是一种**用 Java API 描述 SQL 条件**的方式。

```text
Java 条件构造器
    .eq(Student::getAge, 20)
    .ge(Student::getScore, new BigDecimal("80"))
        ↓
由 MP 构造 SQL 条件与参数映射
        ↓
WHERE age = ? AND score >= ?
        ↓
MyBatis / JDBC 绑定参数并执行
```

### 8.1 四个核心 Wrapper

| 类 | 主要用途 | 列名传入方式 |
|---|---|---|
| `QueryWrapper<T>` | 查询条件、查询列、排序 | 字符串列名，如 `"age"` |
| `LambdaQueryWrapper<T>` | 查询条件、排序 | 方法引用，如 `Student::getAge` |
| `UpdateWrapper<T>` | 更新条件与 SET | 字符串列名 |
| `LambdaUpdateWrapper<T>` | 更新条件与 SET | 方法引用 |

> [!tip]
> **优先掌握 LambdaWrapper：把字段名字符串转换为 Java 方法引用，重构更方便。** 但它不能代替复杂的 SQL 表达式。

## 9. QueryWrapper 与 LambdaQueryWrapper

```java
// 字符串字段名
QueryWrapper<Student> q = new QueryWrapper<>();
q.eq("age", 20).ge("score", 80);
List<Student> list1 = studentMapper.selectList(q);

// 方法引用：更适合日常代码
LambdaQueryWrapper<Student> lq = new LambdaQueryWrapper<>();
lq.eq(Student::getAge, 20)
  .ge(Student::getScore, new BigDecimal("80"));
List<Student> list2 = studentMapper.selectList(lq);
```

对应 SQL 语义：

```sql
SELECT ... FROM student WHERE age = ? AND score >= ?
```

`Student::getAge` 指**Java 属性的 getter 方法引用**，MP 再根据实体映射找到数据库的 `age` 列。

## 10. Wrapper 常用条件方法

| 方法 | SQL 含义 | 示例 |
|---|---|---|
| `eq` | `=` | `.eq(Student::getAge, 20)` |
| `ne` | `<>` | `.ne(Student::getAge, 20)` |
| `gt` / `ge` | `>` / `>=` | `.ge(Student::getAge, 18)` |
| `lt` / `le` | `<` / `<=` | `.lt(Student::getAge, 30)` |
| `between` | `BETWEEN ... AND ...` | `.between(Student::getAge, 18, 25)` |
| `like` | `LIKE '%内容%'` | `.like(Student::getName, "张")` |
| `likeRight` | `LIKE '内容%'` | `.likeRight(Student::getName, "张")` |
| `in` | `IN (...)` | `.in(Student::getId, List.of(1L,2L))` |
| `isNull` | `IS NULL` | `.isNull(Student::getScore)` |
| `orderByDesc` | `ORDER BY ... DESC` | `.orderByDesc(Student::getScore)` |
| `orderByAsc` | `ORDER BY ... ASC` | `.orderByAsc(Student::getId)` |

## 11. 动态条件：使用 boolean condition

【**重点**】条件可能为空时，无需为每个字段写 XML `<if>`。

```java
String name = "张";         // 可能为空
Integer minAge = 18;        // 可能为 null

LambdaQueryWrapper<Student> w = new LambdaQueryWrapper<>();
w.like(name != null && !name.isBlank(), Student::getName, name)
 .ge(minAge != null, Student::getAge, minAge)
 .orderByDesc(Student::getScore)
 .orderByAsc(Student::getId);

List<Student> students = studentMapper.selectList(w);
```

相当于原生 MyBatis 的：

```xml
<where>
    <if test="name != null and name != ''">
        AND name LIKE CONCAT('%', #{name}, '%')
    </if>
    <if test="minAge != null">
        AND age >= #{minAge}
    </if>
</where>
```

> [!warning]
> 如果 `condition` 为 `false`，这一条件**不会加入 SQL**；不是生成 `字段 = NULL`。用于更新、删除时尤其要小心：可能最终没有 WHERE 条件。

## 12. AND / OR / 括号分组

```java
LambdaQueryWrapper<Student> w = new LambdaQueryWrapper<>();
w.eq(Student::getClassName, "一班")
 .and(x -> x.ge(Student::getScore, new BigDecimal("90"))
            .or().lt(Student::getScore, new BigDecimal("60")));
```

条件含义：

```sql
WHERE class_name = '一班'
  AND (score >= 90 OR score < 60)
```

- 多个普通链式条件默认用 `AND`。
- `.or()` 使后面相邻条件使用 `OR`。
- `.and(x -> ...)` / `.or(x -> ...)` 便于表达带括号的条件。

⚠️ **易混淆**：`A AND B OR C` 与 `A AND (B OR C)` 的结果**不一定相同**。复杂条件要明确分组。

## 13. select / orderBy / 安全

```java
LambdaQueryWrapper<Student> w = new LambdaQueryWrapper<Student>()
    .select(Student::getId, Student::getName, Student::getScore)
    .orderByDesc(Student::getScore)
    .orderByAsc(Student::getId);
```

- `select(...)`：只查询需要的列。未查询的实体属性通常为 `null` / 默认值。
- `orderBy...`：实现稳定排序；分页时建议追加唯一列 `id` 作为最后排序键。
- Wrapper 的普通值条件通常走**参数绑定**，但 `last`、`apply` 里的 SQL 片段、`inSql` 等依然可能存在注入风险。

```java
// 推荐：参数通过占位方式传入
w.apply("DATE(create_time) = {0}", "2026-10-21");

// 危险：绝不能把用户提交的整段 SQL 原样拼进去
// w.last(userInput);
```

> [!warning]
> **SQL 文本、表名、排序列不等于 SQL 参数值。** 前端传入排序字段时，要做字段白名单映射；不要直接拼接 `last`、`apply`、`orderBy` 的原始 SQL 字符串。

---

# 第六篇：条件更新与更新策略

## 14. UpdateWrapper / LambdaUpdateWrapper

```java
LambdaUpdateWrapper<Student> w = new LambdaUpdateWrapper<>();
w.eq(Student::getId, 1L)
 .set(Student::getName, "新名字")
 .set(Student::getAge, 21);

int rows = studentMapper.update(null, w);
```

对应 SQL 语义：

```sql
UPDATE student SET name = ?, age = ? WHERE id = ?
```

- `.set(...)`：指定 `SET` 后的赋值内容。
- `.eq(...)`：指定 `WHERE` 条件。
- `update(null, w)`：更新值完全由 Wrapper 的 `set` 指定。

### 14.1 updateById 与条件更新

```java
Student s = new Student();
s.setId(1L);
s.setName("李四");
studentMapper.updateById(s);
```

默认常见字段策略下，实体中值为 `null` 的字段通常**不会**被更新为 `NULL`。

```java
new LambdaUpdateWrapper<Student>()
    .eq(Student::getId, 1L)
    .set(Student::getClassName, null);
```

上面的显式 `set(..., null)` 则可表达“把列设置为 `NULL`”。

⚠️ **易混淆**：

1. `updateById` 依据**实体中的主键**定位记录。
2. `update(entity, wrapper)` 依据**Wrapper 的 WHERE** 更新。
3. 默认的 `null` 更新策略不等于“任何场景都不会写 NULL”；显式 `set`、字段策略等会影响结果。
4. **禁止无条件执行更新或删除**，否则可能影响全表；上线前可按需配置防全表更新删除插件。

---

# 第七篇：Service 层通用能力

## 15. IService / ServiceImpl

【**MP 增强**】MP 除 Mapper 通用 CRUD 外，还提供 Service 层通用接口和默认实现。

- `BaseMapper<T>`：提供 **Mapper 层**通用数据库操作。
- `IService<T>`：提供 **Service 层**常用的数据操作接口。
- `ServiceImpl<M, T>`：MP 提供的通用 **Service 实现基类**，方便实现 `IService<T>`。

```java
public interface StudentService extends IService<Student> {
    // 这里可以继续声明业务方法
}
```

```java
@Service
public class StudentServiceImpl
        extends ServiceImpl<StudentMapper, Student>
        implements StudentService {
}
```

> [!note]
> `ServiceImpl<M, T>` 中：`M` 为 Mapper 类型，`T` 为实体类型。`IService<T>` 定义通用 Service 操作，`ServiceImpl` 提供现成实现。新版 MP 文档也建议了解语义更明确的 `IRepository`；旧项目仍大量出现 `IService`，阅读代码必须认识。

## 16. Service 常用方法

| Service 方法 | 作用 | 典型返回值 |
|---|---|---|
| `save(entity)` | 新增 | `boolean` |
| `saveBatch(list)` | 批量新增 | `boolean` |
| `getById(id)` | 主键查询 | `T` |
| `list(wrapper)` | 查询列表 | `List<T>` |
| `count(wrapper)` | 统计数量 | `long` / `Long`（按版本签名） |
| `updateById(entity)` | 主键更新 | `boolean` |
| `removeById(id)` | 主键删除 | `boolean` |
| `page(page, wrapper)` | 分页查询 | `IPage<T>` |

```java
// 业务层调用示意
Student student = studentService.getById(1L);
boolean ok = studentService.save(newStudent);
List<Student> list = studentService.list(
    new LambdaQueryWrapper<Student>().ge(Student::getAge, 18)
);
```

### 16.1 ⚠️ 不要把“通用 Service”当成业务层设计

- 业务规则仍应放到自己写的 `Service` 方法中。
- 跨多个 Mapper 的一致性更新，仍需要 `@Transactional`。
- Controller 不应因为 `IService` 方法方便就越过业务层直接操作数据库。
- 批量方法的具体实现和 SQL 发送方式与版本、执行器、JDBC 参数有关；**不等于必然是一条 SQL**。

---

# 第八篇：分页插件

## 17. 分页组件的分工

【**MP 增强**】

| 组件 | 负责什么 |
|---|---|
| `Page<T>` | 保存页码、每页数量、记录、总数量 |
| `IPage<T>` | 分页结果接口 |
| `PaginationInnerInterceptor` | 将查询改写为对应数据库的分页 SQL，并按需统计总数 |
| `MybatisPlusInterceptor` | MP 内部插件统一入口 |

### 17.1 配置分页插件

```java
@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(
            new PaginationInnerInterceptor(DbType.MYSQL)
        );
        return interceptor;
    }
}
```

常用导入：

```java
import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
```

> [!warning]
> 仅使用 `new Page<>(...)` **并不等于分页插件已经配置好**。MP 3.5.9+ 使用 `PaginationInnerInterceptor` 前，必须确保 `mybatis-plus-jsqlparser` 依赖已加入。

## 18. 分页查询

```java
long pageNum = 2;  // 第 2 页（从 1 开始）
long pageSize = 5; // 每页 5 条

Page<Student> page = new Page<>(pageNum, pageSize);
LambdaQueryWrapper<Student> w = new LambdaQueryWrapper<Student>()
    .ge(Student::getAge, 18)
    .orderByAsc(Student::getId);

IPage<Student> result = studentMapper.selectPage(page, w);

List<Student> records = result.getRecords();
long total = result.getTotal();
long pages = result.getPages();
long current = result.getCurrent();
long size = result.getSize();
```

**SQL 语义**：

```text
pageNum = 2, pageSize = 5
          ↓
offset = (2 - 1) * 5 = 5
          ↓
LIMIT 5, 5
```

- `records`：**本页**的数据，不是全部数据。
- `total`：符合条件的记录总数（前提是执行了统计查询）。
- `pages`：总页数；受 `total` 和 `size` 影响。
- `current`：当前页码，不是数据库偏移量。

⚠️ **易混淆**：分页可能包含 **COUNT 查询 + 数据查询**，不是简单地“多加一个 LIMIT”。复杂 JOIN / `GROUP BY` 的总数统计需要检查实际生成 SQL，必要时自定义 COUNT。

---

# 第九篇：自动填充

## 19. @TableField(fill) + MetaObjectHandler

【**MP 增强**】用于新增时间、修改时间等字段。

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createTime;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updateTime;
```

```java
@Component
public class AuditMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        LocalDateTime now = LocalDateTime.now();
        this.strictInsertFill(metaObject, "createTime", LocalDateTime.class, now);
        this.strictInsertFill(metaObject, "updateTime", LocalDateTime.class, now);
    }

    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updateTime",
                LocalDateTime.class, LocalDateTime.now());
    }
}
```

相关导入：

```java
import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import org.apache.ibatis.reflection.MetaObject;
```

- `FieldFill.INSERT`：新增时填充。
- `FieldFill.UPDATE`：更新时填充。
- `FieldFill.INSERT_UPDATE`：新增、更新都尝试填充。
- `strict...Fill`：根据属性名、类型和填充策略设置实体字段，已有非空值等情况可能不覆盖。

⚠️ **易混淆**：自动填充不是数据库触发器；它依赖 MP 对**实体对象**进行处理。只有 Wrapper 而没有实体参与的更新，并不保证触发更新时间自动填充。

---

# 第十篇：逻辑删除

## 20. @TableLogic

【**MP 增强**】逻辑删除 = **数据仍在数据库中，只修改删除标记**。

需要表中有一个字段，例如：

```sql
ALTER TABLE student ADD COLUMN deleted TINYINT NOT NULL DEFAULT 0;
```

实体中：

```java
@TableLogic(value = "0", delval = "1")
private Integer deleted;
```

执行：

```java
studentMapper.deleteById(1L);
```

MP 通用删除语义类似于：

```sql
UPDATE student
SET deleted = 1
WHERE id = 1 AND deleted = 0;
```

之后 MP 的通用查询通常会增加 `deleted = 0` 过滤。

| 操作 | 逻辑删除后的行为 |
|---|---|
| MP 通用 `deleteById` | 改删除标记，不一定物理删除 |
| MP 通用 `selectList` | 排除已逻辑删除的数据 |
| MP 通用 `update...` | 通常不更新已逻辑删除的记录 |
| 自己写的 XML SQL | **须自己确认是否增加删除条件** |

> [!warning]
> **逻辑删除不等于事务回滚，也不等于数据库真正删除。** 如果业务经常需要查询归档/删除数据，应重新评估是否适合用逻辑删除。

---

# 第十一篇：乐观锁

## 21. @Version + OptimisticLockerInnerInterceptor

【**MP 增强**】乐观锁常用于减少并发覆盖更新的问题。

```sql
ALTER TABLE student ADD COLUMN version INT NOT NULL DEFAULT 0;
```

```java
@Version
private Integer version;
```

插件中添加：

```java
interceptor.addInnerInterceptor(new OptimisticLockerInnerInterceptor());
```

相关导入：

```java
import com.baomidou.mybatisplus.extension.plugins.inner.OptimisticLockerInnerInterceptor;
```

**工作过程（版本整数）**：

```text
读到 version = 3
        ↓
尝试更新某条数据
        ↓
UPDATE ...
SET ..., version = 4
WHERE id = ? AND version = 3
        ↓
影响 1 行：通常表示版本匹配，更新成功
影响 0 行：可能发生版本冲突，或记录不存在/不满足条件
```

```java
Student s = studentMapper.selectById(1L);
s.setName("新名字");
int rows = studentMapper.updateById(s);
if (rows == 0) {
    // 业务上可选择提示冲突、重新加载，或有限次数重试
}
```

⚠️ **易混淆**：

- `@Version` 需要**插件 + 实体字段 + 正确的更新方式**一起生效。
- 乐观锁不能代替 `@Transactional`。
- `update(entity, wrapper)` 使用过的 Wrapper 不建议复用。
- 自动生成的乐观锁条件不意味着所有手写 XML 都会自动获得并发保护。

---

# 第十二篇：批量操作

## 22. 批量新增、更新、删除

```java
// Service 层：批量新增
boolean inserted = studentService.saveBatch(studentList);

// Service 层：根据主键批量更新
boolean updated = studentService.updateBatchById(studentList);

// Mapper 层：按主键集合删除（新版本）
int deleted = studentMapper.deleteByIds(List.of(1L, 2L, 3L));
```

### 22.1 与原生 MyBatis <foreach> 的区别

- MP 通用方法能减少大量重复代码。
- 但具体是**逐条执行/批处理发送**还是**拼接为单条多 VALUES SQL**，不能只靠 `saveBatch` 方法名推断。
- 超大批次可能占用大量内存、连接资源、锁资源；要考虑合理分批、事务范围和驱动行为。
- **复杂批量插入 SQL** 仍可自己写 XML `<foreach>`。

---

# 第十三篇：与原生 MyBatis 混合使用

## 23. BaseMapper 与 XML 可以共存

【**重点**】MP 不是“禁止写 XML”。

```java
public interface StudentMapper extends BaseMapper<Student> {
    List<Student> selectExcellentStudents(@Param("minScore") BigDecimal minScore);
}
```

对应 `resources/mapper/StudentMapper.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.StudentMapper">
    <select id="selectExcellentStudents"
            resultType="com.example.entity.Student">
        SELECT id, name, age, gender, score, class_name
        FROM student
        WHERE score &gt;= #{minScore}
        ORDER BY score DESC, id ASC
    </select>
</mapper>
```

```java
// MP 通用方法
Student a = studentMapper.selectById(1L);

// 手写的 MyBatis XML 方法
List<Student> b = studentMapper.selectExcellentStudents(
    new BigDecimal("90")
);
```

> [!tip]
> **简单单表 CRUD → 优先 MP；多表 JOIN、窗口函数、复杂统计报表 → 优先手写 SQL/XML。** 两者共用 Spring、MyBatis 的执行与事务机制。

### 23.1 自定义 SQL 的注意事项

- 自己写的 SQL 仍要处理 `#{}` / `${}`、`resultMap`、`@Param`、索引、SQL 注入等问题。
- `@TableLogic` 的过滤条件不一定自动作用于每一条手写 SQL。
- 部分 MP 插件（例如分页）可以处理符合约定的自定义 Mapper 查询，但需正确声明分页参数并验证生成 SQL。
- 不要给 `BaseMapper` 原生通用方法写冲突的 XML statement。

---

# 第十四篇：事务、性能与常见陷阱

## 24. MP 与 Spring 事务

【**Spring Boot 整合**】事务边界仍由 Spring 管理；MP **不会**自动替业务决定跨操作的原子性。

```java
@Service
public class RegistrationService {
    private final StudentMapper studentMapper;
    private final EnrollmentMapper enrollmentMapper;

    public RegistrationService(StudentMapper studentMapper,
                               EnrollmentMapper enrollmentMapper) {
        this.studentMapper = studentMapper;
        this.enrollmentMapper = enrollmentMapper;
    }

    @Transactional(rollbackFor = Exception.class)
    public void register(Student student, Enrollment enrollment) {
        studentMapper.insert(student);
        enrollment.setStudentId(student.getId());
        enrollmentMapper.insert(enrollment);
    }
}
```

- Spring 事务机制仍涉及 `DataSourceTransactionManager`、事务绑定的 `Connection`、MyBatis-Spring 会话管理。
- `@Transactional` 代理、自调用、异常回滚规则等知识**仍然适用**。
- MP 只是在 Mapper 方法和 SQL 生成上增加了能力。

## 25. 典型问题排查表

| 现象 | 优先检查 |
|---|---|
| Mapper 无法注入 | `@MapperScan` 包路径、组件扫描、Starter 依赖 |
| 找不到表 / 字段 | `@TableName`、`@TableField`、驼峰映射、schema |
| 主键插入错误 | `@TableId` 的 `IdType` 与数据库主键设计 |
| `selectPage` 未按预期分页 | 分页依赖、分页插件 Bean、分页参数 |
| 分页 `total` 不对 | 自动 COUNT 对 JOIN / GROUP BY 的处理 |
| 更新值为 null 未生效 | 更新字段策略、是否显式 `set` |
| 更新 / 删除波及多行 | Wrapper 动态条件是否为空、是否遗漏 WHERE |
| `selectOne` 报多结果异常 | 条件是否能保证唯一 |
| 已删除数据仍查得到 | 是否手写 XML、逻辑删除配置是否生效 |
| 乐观锁返回 0 行 | version 是否正确、是否并发更新、记录是否存在 |
| 自动填充未执行 | 字段 `fill`、`MetaObjectHandler` 注册、是否有实体参与 |
| SQL 很慢 | EXPLAIN、索引、排序、分页偏移、返回列、数据量 |

### 25.1 Wrapper 的几个原则

1. **每次请求/操作创建新 Wrapper**，不要把可变 Wrapper 当成共享单例。
2. 条件更新和删除执行前必须保证 WHERE 条件符合预期。
3. 严格控制动态排序、原始 SQL 片段。
4. SQL 性能由数据库执行计划决定；用了 MP 不代表 SQL 自动更快。
5. 多表复杂查询优先保证正确、可维护，不要为了“全用 MP”强行链式拼接。

---

# 第十五篇：完整小案例（学生条件分页）

## 26. 从请求条件到分页结果

假定 `Student` 与 `StudentMapper` 已按前文定义，分页插件已配置。

```java
public IPage<Student> searchStudents(String name,
                                     Integer minAge,
                                     long pageNum,
                                     long pageSize) {
    if (pageNum < 1 || pageSize < 1 || pageSize > 100) {
        throw new IllegalArgumentException("分页参数非法");
    }

    LambdaQueryWrapper<Student> wrapper = new LambdaQueryWrapper<>();
    wrapper.like(name != null && !name.isBlank(), Student::getName, name)
           .ge(minAge != null, Student::getAge, minAge)
           .orderByDesc(Student::getScore)
           .orderByAsc(Student::getId);

    Page<Student> page = new Page<>(pageNum, pageSize);
    return studentMapper.selectPage(page, wrapper);
}
```

**执行流程：**

```text
接收 name / minAge / pageNum / pageSize
                ↓
检查分页参数（避免负数与超大请求）
                ↓
LambdaQueryWrapper 添加非空条件
                ↓
Page 指定当前页与每页大小
                ↓
BaseMapper.selectPage(page, wrapper)
                ↓
MP 插件生成分页 SQL / 按需统计数量
                ↓
MyBatis 执行 SQL，映射 Student
                ↓
IPage<Student>（records / total / pages / current）
```

### 26.1 这段代码涉及哪些知识？

| 代码 | 知识点 |
|---|---|
| `LambdaQueryWrapper` | 条件构造器 |
| `.like(boolean, ...)` | 动态 SQL / 条件开关 |
| `Student::getName` | Java 方法引用 / Lambda 字段表达 |
| `.orderByAsc(Student::getId)` | 稳定分页排序 |
| `new Page<>(...)` | 分页参数与结果承载 |
| `selectPage(...)` | `BaseMapper` 的通用分页方法 |
| `PaginationInnerInterceptor` | 改写分页 SQL |
| `IPage<Student>` | 分页数据与元信息 |

---

# 第十六篇：开发速查与最终结论

## 27. 一张表区分四类核心 API

| 需求 | 推荐 API | 原生 MyBatis 的对应思路 |
|---|---|---|
| 查 ID | `selectById(id)` | `SELECT ... WHERE id = ?` |
| 新增 | `insert(entity)` | `<insert>` |
| 按 ID 更新 | `updateById(entity)` | `<update> ... WHERE id = ?` |
| 多条件查 | `LambdaQueryWrapper` + `selectList` | `<where>` + `<if>` |
| 多条件改 | `LambdaUpdateWrapper` + `update` | `<set>` + `<where>` |
| 分页 | `Page` + `selectPage` + 分页插件 | `COUNT` + `LIMIT` |
| 批量保存 | `saveBatch`（Service） | 批处理或 `<foreach>` |
| 自动填时间 | `@TableField(fill)` + `MetaObjectHandler` | 手写填充逻辑 |
| 逻辑删除 | `@TableLogic` | 手动改删除标记并过滤 |
| 乐观锁 | `@Version` + 乐观锁插件 | 手写 `WHERE version = ?` |
| 复杂 JOIN/报表 | 自定义 Mapper XML | 自定义 Mapper XML |

## 28. 最容易记混的 8 个结论

1. **MP 基于 MyBatis**，不是绕开 MyBatis 直接操作数据库。
2. **`BaseMapper<T>` 属于 Mapper 层**；`IService<T>` 属于通用 Service 接口层。
3. **Mapper 层返回影响行数 `int`**，Service 常见保存/更新/删除方法返回 `boolean`。
4. **`QueryWrapper` 查询，`UpdateWrapper` 更新；Lambda 版本用 getter 方法引用描述列。**
5. **Wrapper 的 `eq` 等值参数一般可以安全绑定，但原始 SQL 片段仍可能产生注入。**
6. **`Page` 负责分页数据结构，`PaginationInnerInterceptor` 负责 SQL 分页处理。**
7. **`@TableLogic` 是逻辑删除；`@Version` 是乐观锁；`@TableField(fill)` 是自动填充。**
8. **复杂 SQL 依然可以写 XML**，无需也不应该把所有 SQL 都改造成 Wrapper。

> [!tip]
> **最终定位：原生 MyBatis 让你明白 SQL 如何映射和执行；MyBatis-Plus 让你在理解原理之后，更高效地写单表 CRUD。两者应该互补，而不是二选一。**

---

## 官方参考文档

- 安装与依赖：https://baomidou.com/getting-started/install/
- 条件构造器：https://baomidou.com/guides/wrapper/
- Mapper / Service 接口：https://baomidou.com/guides/data-interface/
- 注解配置：https://baomidou.com/reference/annotation/
- 分页插件：https://baomidou.com/plugins/pagination/
- 自动填充：https://baomidou.com/guides/auto-fill-field/
- 逻辑删除：https://baomidou.com/guides/logic-delete/
- 乐观锁：https://baomidou.com/plugins/optimistic-locker/

---
