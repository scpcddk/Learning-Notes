# 《MyBatis-Plus 完整学习与开发速查笔记》

> **示例环境**：基础示例使用 Java 17+、Spring Boot 3.x、MyBatis-Plus 3.5.x、MySQL 8.x。第 17 节另给出 Spring Boot 4.1.1 项目的分页配置。
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

MP 主要减少常规单表 CRUD 的 Mapper 方法、XML 和简单条件拼接；业务逻辑、数据库设计、索引优化与事务设计仍由开发者负责。

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
    <scope>runtime</scope> <!-- 运行时加载 JDBC 驱动，业务代码通常无需直接引用驱动类 -->
</dependency>
```

Spring Boot 4.x 项目使用 `mybatis-plus-spring-boot4-starter`。分页所需的解析模块及 Maven 配置见第 17.1 节。[官方安装说明](https://baomidou.com/getting-started/install/)

> [!warning]
> **不要在同一项目中再主动叠加** `mybatis-spring-boot-starter`、单独的 `mybatis`、`mybatis-spring`，以免出现依赖和自动配置冲突。已有原生 MyBatis 项目改为 MP 时，应调整原来的 Starter 依赖，而不是无条件全部保留。

---

## 3. application.yml

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/school?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
    username: dev
    password: ${DB_PASSWORD} # 从环境变量等配置源读取，避免在文件里写明文密码
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

---

## 4. Mapper 扫描

```java
@SpringBootApplication
// 扫描 Mapper 接口并注册代理 Bean，之后可通过构造器注入 Mapper
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
    private Integer age; // 包装类型可表示数据库 NULL；int 无法表示 null
    private String gender;
    private BigDecimal score; // 对应 DECIMAL，避免用浮点数表示需要精确的小数

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
> - **数据库自增 `IdType.AUTO`**：Java 不提供 ID → MySQL 用 `AUTO_INCREMENT` 生成 → MP 回填实体。使用数据库自增机制时，应显式配置该策略。
> - **MP 分配 `IdType.ASSIGN_ID`**：MP 在 Java 应用侧生成 ID → 随 INSERT 发送给 MySQL。MP 默认策略通常是 `ASSIGN_ID`，不等于数据库自增。
> - **MP 分配 ID 发生在执行插入的过程中，不是创建 Java 对象时**。若调用 `insert()` 前就需要把 ID 发给其他服务，应提前显式生成并设置 ID。

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

---

## 7. 常用 CRUD 方法

```java
// INSERT
int rows1 = studentMapper.insert(student);

// SELECT
Student one = studentMapper.selectById(1L); // 1L 是 long 字面量，与 Long 主键类型对应
List<Student> all = studentMapper.selectList(null); // null 表示不额外传入 Wrapper 条件
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

**为什么需要条件构造器？**

假设要查询年龄大于 18 岁的学生，对应 SQL 是：

```sql
SELECT * FROM student WHERE age > 18;
```

但 `studentMapper.selectList(null)` 没有传入额外筛选条件，无法表达“年龄大于 18 岁”。要让 MP 按条件查询，可以把条件放进 `QueryWrapper`，再传给 `selectList`：

```java
// <> 根据左侧类型推断为 Student；泛型指定实体，不是表名字符串
QueryWrapper<Student> query = new QueryWrapper<>();
query.gt("age", 18); // 添加 age > 18 条件，此时还没有访问数据库
List<Student> students = studentMapper.selectList(query); // 把条件交给 Mapper，此处才执行查询
```

**条件构造器的作用，就是把“按什么条件操作数据”告诉 MP，由 MP 生成对应的 SQL。** 上例实际使用参数绑定，条件为 `WHERE age > ?`，参数值为 `18`。

### 8.1 四个核心 Wrapper

先看用途（**查询 / 更新**），再看指定列的方式（**字符串 / getter 方法引用**）：

| 构造器 | 主要用途 | 指定列的方式 | 简单示例 |
|---|---|---|---|
| `QueryWrapper<T>` | **查询**：筛选、选列、排序 | 数据库列名字符串 | `.eq("age", 20)` |
| `LambdaQueryWrapper<T>` | **查询**：筛选、选列、排序 | 实体 getter 方法引用 | `.eq(Student::getAge, 20)` |
| `UpdateWrapper<T>` | **更新**：筛选、设置新值 | 数据库列名字符串 | `.set("age", 21)` |
| `LambdaUpdateWrapper<T>` | **更新**：筛选、设置新值 | 实体 getter 方法引用 | `.set(Student::getAge, 21)` |

表中的 `eq` 筛选年龄为 20 的记录，`set` 把年龄改为 21；更新时还应添加条件限定记录范围。四种 Wrapper 的完整示例见第 9 节。

> [!tip]
> **Query 管查询，Update 管更新；普通版写列名，Lambda 版引用 getter。**

### 8.2 条件构造器的实际用途

**① 列表搜索：把页面筛选项转换成数据库查询条件**

学生管理页可按姓名、班级、最低成绩组合筛选，只添加用户已填写的条件。动态条件写法见第 11 节，完整分页案例见第 26 节。

**② 条件更新：一次修改所有符合条件的记录**

例如，把“一班中成绩达到 90 分的学生”统一调整到“提高班”，无需先查询再逐个更新。`eq`、`ge` 限定范围，`set` 指定新班级；更新示例见第 9.3、22.1 节。

**③ 条件删除：组合勾选结果与业务范围**

例如，页面勾选了一批学生，但本次操作只允许删除其中属于“一班”的记录：

```java
List<Long> selectedIds = List.of(1L, 2L, 3L); // List.of 创建不可修改的列表，这里模拟页面勾选结果
if (selectedIds == null || selectedIds.isEmpty()) {
    throw new IllegalArgumentException("请先选择要删除的学生");
}

LambdaQueryWrapper<Student> toDelete = new LambdaQueryWrapper<>();
toDelete.in(Student::getId, selectedIds) // 集合中的每个 ID 对应 IN 中的一个参数值
        .eq(Student::getClassName, "一班"); // 默认用 AND：既要被勾选，也要属于一班

int deletedRows = studentMapper.delete(toDelete);
```

条件相当于 `WHERE id IN (?, ?, ?) AND class_name = ?`，业务允许操作的班级应由服务端确定。空集合的处理见第 10.1 节，逻辑删除见第 20 节。

**④ 条件统计与分页：同样的筛选需求，选择不同执行入口**

- **统计人数**：构造“一班且成绩达到 60 分”的条件，传给 `studentMapper.selectCount(wrapper)`，获得符合条件的人数，无需把所有学生查回 Java 再计数。
- **分页展示**：构造列表筛选条件，传给 `studentMapper.selectPage(page, wrapper)`；Wrapper 描述筛选和排序，`Page` 提供页码与每页数量，分页插件处理分页 SQL。

---

## 9. 四种 Wrapper 的用法与区别

以下示例均沿用前文的 `Student` 实体和 `studentMapper`。

### 9.1 QueryWrapper：用列名字符串描述查询

适合通过数据库列名直接组织查询条件，也可以指定查询列和排序。

```java
QueryWrapper<Student> q = new QueryWrapper<>();
// 下列方法返回当前构造器，因此可以用 . 连续调用，逐步补充同一条查询
q.select("id", "name", "score") // SELECT 只返回这三列，不是按这三列筛选
 .eq("class_name", "一班")
 .ge("score", new BigDecimal("80"))
 .orderByDesc("score") // 先按成绩降序，高分排在前面
 .orderByAsc("id"); // 成绩相同时再按主键排序，使结果顺序确定

List<Student> students = studentMapper.selectList(q);
```

对应 SQL 语义：

```sql
SELECT id, name, score
FROM student
WHERE class_name = ? AND score >= ?
ORDER BY score DESC, id ASC;
```

`"class_name"` 是**数据库列名**，不能因为 Java 属性叫 `className` 就直接写成 `"className"`。

### 9.2 LambdaQueryWrapper：用 getter 方法引用描述查询

`QueryWrapper` 与 `LambdaQueryWrapper` 的主要区别是**指定列的方式**，两者仍通过 MyBatis / JDBC 访问数据库。下面实现与上一例相同的查询：

```java
LambdaQueryWrapper<Student> lq = new LambdaQueryWrapper<>();
lq.select(Student::getId, Student::getName, Student::getScore)
  .eq(Student::getClassName, "一班") // getter 对应 Java 属性，最终条件使用数据库列 class_name
  .ge(Student::getScore, new BigDecimal("80"))
  .orderByDesc(Student::getScore)
  .orderByAsc(Student::getId);

List<Student> students = studentMapper.selectList(lq);
```

`Student::getClassName` 是**getter 方法引用**，MP 根据实体映射找到 `class_name` 列；这里不是先读取某个学生对象的班级值。

**方法引用指定操作哪一列，`eq()`、`lt()`、`set()` 等方法指定操作类型，后续值参数提供比较值或新值。** 例如，`eq` 表示等值筛选，`lt` 表示小于筛选，更新构造器的 `set` 表示赋值。

**方法调用、Lambda 与方法引用的区别：**

| 写法 | 含义 |
|---|---|
| `student.getName()` | 立即调用该对象的方法，获得返回值 |
| `s -> s.getName()` | Lambda 表达式，接收学生对象，调用时读取姓名 |
| `Student::getName` | 对 `Student` 实例方法 `getName` 的方法引用 |

后两种写法在 `Function<Student, String>` 等合适的函数式接口目标类型下，可以表达等价行为；声明时都不会立即读取某个学生的姓名。

**但在 MP 中，列参数仍应使用 `Student::getName` 这样的 getter 方法引用。** MP 通过方法引用的元信息确定属性和列，并非执行函数取值，不能据此把列参数直接改成任意 `s -> ...` 表达式。

**为什么用 `Student::getAge`，不能直接写 `"age"`？**

`"age"` 可以用，但要看构造器类型：**普通版的列参数接收字符串，Lambda 版的列参数要求 getter 方法引用，两者不能直接混用。**

```java
new QueryWrapper<Student>().eq("age", 20); // 普通版：数据库列名
new LambdaQueryWrapper<Student>().eq(Student::getAge, 20); // Lambda 版：由 getter 找到列
// new LambdaQueryWrapper<Student>().eq("age", 20); // 参数类型不匹配，无法编译
```

前两种写法都表达 `age = 20`。

**方法引用的优势与边界：**

- 字符串列名不受 Java 编译器检查；重命名实体属性并同步修改 getter 时，IDE 通常可更新方法引用，引用的方法不存在则会编译报错。
- 方法引用不检查数据库中的列是否存在，映射错误仍可能在运行时暴露；`apply / last` 等 SQL 片段也仍需后端控制。
- Lambda 的优势是 Java 层的检查与重构支持，不会额外提升 SQL 性能或通过 Spring 获得数据库访问安全保障。

### 9.3 UpdateWrapper：分别指定更新值和更新条件

更新时需要分清：**`set` 决定改什么，`eq` 等条件决定改哪些记录**。

```java
UpdateWrapper<Student> u = new UpdateWrapper<>();
// 两次 set 为同一批记录设置两列；eq 限定记录范围，不是给 id 赋值
u.set("class_name", "二班")
 .set("age", 21)
 .eq("id", 1L);

int rows = studentMapper.update(null, u); // 无实体参数，SET 的更新值全部取自 u
```

对应 SQL 语义：

```sql
UPDATE student
SET class_name = ?, age = ?
WHERE id = ?;
```

- `set("age", 21)` 表示把年龄改为 21；`eq("age", 21)` 表示筛选年龄为 21 的记录，**不会给年龄赋值**。
- 这里的 `rows` 是影响行数；若条件匹配多条记录，就可能更新多条。

### 9.4 LambdaUpdateWrapper：用方法引用描述更新

与 `UpdateWrapper` 的分工相同，使用 getter 方法引用指定 `SET` 和 `WHERE` 中的列。下面与上一例的更新语义相同：

```java
LambdaUpdateWrapper<Student> lu = new LambdaUpdateWrapper<>();
// set、eq 的书写先后不决定 SQL 子句顺序，MP 会分别组织 SET 与 WHERE
lu.set(Student::getClassName, "二班")
  .set(Student::getAge, 21) // getter 用来定位列，新值由第二个参数提供
  .eq(Student::getId, 1L);

int rows = studentMapper.update(null, lu);
```

虽然是**更新**，这里仍写 `Student::getAge`，不是 `Student::setAge`：方法引用用于**标识列**，新值由 `set` 的第二个参数提供。

实体与 Wrapper 的配合、NULL 更新规则见第 14 节。

### 9.5 Wrapper 与 Mapper 的分工

> [!warning] Wrapper 构造条件，Mapper 执行操作
>
> - 上面四种 Wrapper 的 `eq`、`set` 等调用只构造 SQL 片段，**不会立即访问数据库**；调用 Mapper 方法后才执行。
> - `QueryWrapper` / `LambdaQueryWrapper` 的条件也可传给 `delete(wrapper)`，并非只能用于查询；是否执行删除由 Mapper 方法决定。

以上 API 用法可对照 [MyBatis-Plus 官方条件构造器文档](https://baomidou.com/guides/wrapper/)。

---

## 10. Wrapper 常用条件方法

| 方法 | SQL 含义 | 示例 |
|---|---|---|
| `eq` | `=` | `.eq(Student::getAge, 20)` |
| `ne` | `<>`(不等于) | `.ne(Student::getAge, 20)` |
| `gt` / `ge` | `>` / `>=` | `.ge(Student::getAge, 18)` |
| `lt` / `le` | `<` / `<=` | `.lt(Student::getAge, 30)` |
| `between` | `BETWEEN ... AND ...` | `.between(Student::getAge, 18, 25)` |
| `notBetween` | `NOT BETWEEN ... AND ...` | `.notBetween(Student::getAge, 18, 25)` |
| `like` | `LIKE '%内容%'` | `.like(Student::getName, "张")` |
| `likeLeft` | `LIKE '%内容'`，以指定内容结尾 | `.likeLeft(Student::getName, "三")` |
| `likeRight` | `LIKE '内容%'` | `.likeRight(Student::getName, "张")` |
| `in` | `IN (...)` | `.in(Student::getId, List.of(1L,2L))` |
| `notIn` | `NOT IN (...)` | `.notIn(Student::getId, List.of(1L,2L))` |
| `isNull` | `IS NULL` | `.isNull(Student::getScore)` |
| `isNotNull` | `IS NOT NULL` | `.isNotNull(Student::getScore)` |
| `or` | 用 `OR` 连接下一个条件 | `.eq(Student::getAge, 18).or().eq(Student::getAge, 20)` |
| `nested` | 将内部条件组成括号分组 | `.nested(x -> x.eq(Student::getAge, 18).or().eq(Student::getAge, 20))` |
| `orderByDesc` | `ORDER BY ... DESC` | `.orderByDesc(Student::getScore)` |
| `orderByAsc` | `ORDER BY ... ASC` | `.orderByAsc(Student::getId)` |

> [!tip]
> SQL 判断 NULL 应使用 `IS NULL` / `IS NOT NULL`，不能用 `eq(..., null)` 或 `ne(..., null)` 代替。空字符串 `""` 与 NULL 不同，`isNotNull` 不会排除空字符串。

`between()` 的参数应按**下界、上界**传入，不会自动排序。逻辑分组见第 12 节。

### 10.1 空集合：先明确业务含义

`wrapper.in("class_name", classes)` 中 `classes` 为空，**不能直接理解为“查询不到学生”**。应结合 MP 版本检查实际 SQL，并在业务层明确处理：

- **空集合表示“不按班级筛选”**：主动跳过该条件。
- **空集合表示“没有任何允许的班级”**：查询前直接返回空列表（如 `return List.of()`），不要仅靠空集合限制范围，以免条件被跳过后扩大查询范围，甚至退化为全表查询。

---

## 11. 动态条件：使用 boolean condition

【**重点**】条件可能为空时，无需为每个字段写 XML `<if>`。

**eq 的三参数重载**

`QueryWrapper` 支持 `eq(boolean condition, String column, Object value)`：三个参数依次为**是否加入条件、数据库列名、比较值**。

```java
String className = "一班"; // 假设来自请求，也可能未填写
QueryWrapper<Student> q = new QueryWrapper<>();
q.eq(className != null && !className.isBlank(),
     "class_name", className);
```

`isBlank()` 是 Java 11+ 的字符串方法：空字符串 `""` 或只含空格、制表符、换行等空白字符时返回 `true`；如 `"一班"` 则返回 `false`。`isEmpty()` 只判断长度是否为 0，因此 `"   ".isEmpty()` 为 `false`，但 `"   ".isBlank()` 为 `true`。

先判断 `className != null`，再利用 `&&` 短路调用 `isBlank()`，避免空指针异常。

有班级值时添加 `class_name = ?`；未填写时跳过该条件。两参数 `eq(column, value)` 相当于 `condition=true`，不会自动判断值是否为空。

Lambda 版同样支持三参数形式，可组合多个可选筛选项：

```java
String name = "张";         // 可能为空
Integer minAge = 18;        // 可能为 null

LambdaQueryWrapper<Student> w = new LambdaQueryWrapper<>();
w.like(name != null && !name.isBlank(), Student::getName, name)
 .ge(minAge != null, Student::getAge, minAge)
 .orderByDesc(Student::getScore)
 .orderByAsc(Student::getId);

// name="张"、minAge=18 时：WHERE name LIKE '%张%' AND age >= 18（实际走参数绑定）
List<Student> students = studentMapper.selectList(w);
```

> [!warning] 关键细节：不添加条件，不等于返回空结果
> `condition = false` 表示**不添加该条件**，并不等于“查询不到任何记录”，也不是生成 `字段 = NULL`。其余条件仍正常生效；如果所有筛选条件都被跳过，可能退化为全表查询。用于更新、删除时，同样要检查最终的 WHERE 范围。

---

## 12. AND / OR / 括号分组

```java
LambdaQueryWrapper<Student> w = new LambdaQueryWrapper<>();
w.eq(Student::getClassName, "一班")
 // x 是括号内部的条件构造器；这里组合为 AND (score >= 90 OR score < 60)
 .and(x -> x.ge(Student::getScore, new BigDecimal("90"))
            // 此处 or 连接括号内两个成绩条件，班级条件仍位于括号外
            .or().lt(Student::getScore, new BigDecimal("60")));
```

**条件含义**：

```sql
WHERE class_name = '一班'
  AND (score >= 90 OR score < 60)
```

- 多个普通链式条件默认用 `AND`。
- `.or()` 使后面相邻条件使用 `OR`。
- `.and(x -> ...)` / `.or(x -> ...)` 便于表达带括号的条件。

**AND 与 OR 的优先级**

在这些条件组合中，**括号分组优先，`AND` 的优先级高于 `OR`**。Wrapper 最终生成 SQL，逻辑分组遵循 SQL 规则，不能把 Java 链式调用顺序理解为从左到右依次加括号。[MySQL 官方说明](https://dev.mysql.com/doc/refman/8.0/en/operator-precedence.html)

```text
A AND B OR C   等价于 (A AND B) OR C
A OR B AND C   等价于 A OR (B AND C)
A AND (B OR C) 必须显式添加括号分组
```

例如，`class_name = '一班' AND score >= 90 OR score < 60` 会把**其他班级中成绩低于 60 分的学生也查出来**。本节示例通过 `.and(x -> ...)` 生成括号，使两个成绩条件都受到“一班”的限制。

### 12.1 nested：独立的括号分组

`nested(x -> ...)` 把内部条件放进一对括号，**自身不强制指定与前面条件使用 AND 还是 OR 连接**。它适合先组织一组条件，再与其他条件组合。

```java
LambdaQueryWrapper<Student> query = new LambdaQueryWrapper<>();
query.nested(x -> x.eq(Student::getAge, 18)
                   .or().eq(Student::getAge, 20)) // 先组成 (age = 18 OR age = 20)
     .eq(Student::getClassName, "一班"); // 后续普通条件默认通过 AND 连接

List<Student> students = studentMapper.selectList(query);
```

对应 SQL 条件：

```sql
WHERE (age = 18 OR age = 20) AND class_name = '一班'
```

**与 and / or 嵌套的区别：**

| 写法 | 与前面已有条件 A 的组合方式 |
|---|---|
| `.and(x -> ...)` | 明确组成 `A AND (...)` |
| `.or(x -> ...)` | 明确组成 `A OR (...)` |
| `.nested(x -> ...)` | 只构造 `(...)`，连接方式取决于外部上下文 |

`nested(...)` 放在开头时直接形成首个括号分组；前面已有普通条件时默认用 `AND` 连接，若写成 `.or().nested(...)` 则用 `OR` 连接。也可用 `nested(boolean condition, x -> ...)` 控制是否加入整组条件。[官方说明](https://baomidou.com/guides/wrapper/#nested)

> [!note]
> `x` 是 MP 传入的内部构造器形参，可改名为 `w` 或 `nested`。例如 `.and(nested -> nested.eq(...))` 中的 `nested` 只是变量名，调用的方法仍是 `and`，不是 `nested(...)`。

---

## 13. 查询指定列与进阶方法

例如，只读取学生的主键、姓名和成绩：

```java
LambdaQueryWrapper<Student> w = new LambdaQueryWrapper<Student>()
    .select(Student::getId, Student::getName, Student::getScore);

List<Student> students = studentMapper.selectList(w); // 返回类型仍是 List<Student>
```

上例未读取 `age`、`gender`、`class_name`，结果对象中的对应属性通常为 `null` / 默认值。**这不代表数据库中的值是 NULL，而是本次查询没有读取这些列。** 排序写法见第 9.1 节。

以下进阶方法的示例相互独立。

### 13.1 allEq：用 Map 组合多个等值条件

适合把一组明确的“列 → 值”条件一起加入 SQL，多个条件默认用 `AND` 连接。

```java
Map<String, Object> filters = new LinkedHashMap<>();
filters.put("class_name", "一班"); // 普通 QueryWrapper 的 key 是数据库列名
filters.put("age", 20);
filters.put("score", null);

QueryWrapper<Student> query = new QueryWrapper<>();
query.allEq(filters, false); // false 是 null2IsNull：忽略值为 null 的项
```

上例条件相当于 `class_name = ? AND age = ?`。使用时注意：

1. **列名要正确**：对于本例的普通 `QueryWrapper`，Map 的键必须是数据库列名，如 `class_name`。
2. **默认保留 NULL 判断**：`allEq(params)` 等同于 `allEq(params, true)`，值为 `null` 的项会生成 `IS NULL`，如 `score IS NULL`。
3. **可跳过 NULL 项**：`allEq(params, false)` 忽略值为 `null` 的条目；这里的 `false` 是 `null2IsNull`，不是整个方法的条件开关。
4. **HashMap 不保证条件顺序**：等值条件通过 `AND` 连接时，顺序变化通常不影响查询逻辑。示例使用 `LinkedHashMap` 保持插入顺序，方便对照生成的 SQL。

如需控制是否添加整组条件，使用 `allEq(boolean condition, map, null2IsNull)`。另外，`Map.of(...)` 不允许 null 键或值，不能用来构造上面包含 null 的示例。

### 13.2 apply：添加带参数的 SQL 条件片段

适合表达普通 `eq / ge` 等方法不便描述的数据库函数条件。假设表中已增加 `create_time` 列：

```java
LambdaQueryWrapper<Student> query = new LambdaQueryWrapper<>();
query.apply("DATE(create_time) = {0}", "2026-10-21");
// DATE(...) 提取日期；{0} 对应后面的第一个参数，通过参数绑定传值
```

生成的条件类似 `WHERE DATE(create_time) = ?`。后续参数可用 `{1}`、`{2}` 引用；SQL 片段中写的是数据库列名，即使用 LambdaWrapper 也不会自动把字符串转成实体属性。

**不要直接拼接用户输入：**

```java
// 不安全：userInput 被直接拼入 SQL 文本，可能引入 SQL 注入
query.apply("score > " + userInput);
```

上面的成绩比较可直接写为 `query.gt(Student::getScore, minScore)`，其中 `minScore` 是经过校验的数值参数。

使用 `apply()` 时，**值用 `{0}` 等占位符绑定，SQL 片段由后端编写**，不要在片段中自行添加 `WHERE`。

### 13.3 last：在 SQL 末尾直接追加片段

例如按主键排序后只取第一条：

```java
LambdaQueryWrapper<Student> query = new LambdaQueryWrapper<>();
query.orderByAsc(Student::getId)
     .last("LIMIT 1"); // 后端固定片段，直接追加到 SQL 末尾

List<Student> students = studentMapper.selectList(query); // 仍返回 List，最多一条
```

SQL 类似 `SELECT ... FROM student ORDER BY id ASC LIMIT 1`。

**同一 Wrapper 多次调用 `last()`，通常以后一次设置为准，不会逐次累加。** 其中的文本直接拼接，不是参数绑定。常规分页优先使用 `Page` 与分页插件，避免再手工追加 `LIMIT`。

### 13.4 exists：筛选存在关联记录的数据

例如查询“已有报名记录的学生”。假设存在 `enrollment` 表，其中 `student_id` 关联学生主键：

```java
LambdaQueryWrapper<Student> query = new LambdaQueryWrapper<>();
query.exists("SELECT 1 FROM enrollment e WHERE e.student_id = student.id");
// student.id 引用外层学生记录，e.student_id 来自报名表
```

条件相当于：

```sql
WHERE EXISTS (
    SELECT 1 FROM enrollment e WHERE e.student_id = student.id
)
```

`EXISTS` 判断子查询是否返回记录，`SELECT 1` 不会把常量 1 加到学生查询的返回字段中。相反，`notExists(...)` 用于筛选不存在关联记录的学生。

更多重载与参数说明见 [官方条件构造器文档](https://baomidou.com/guides/wrapper/)。

---

# 第六篇：条件更新与更新策略

## 14. updateById 与条件更新

`updateById(entity)` 根据实体主键定位，`update(entity, wrapper)` 根据 Wrapper 条件定位。基础写法见第 7、9.3、9.4 节，本节重点说明更新值来源和字段策略。

### 14.1 update(null, wrapper) 与 update(student, wrapper)

`update(null, wrapper)` 的第一个参数为 `null`，表示**没有提供更新实体**，更新内容由 Wrapper 的 SET 设置提供；并不是把某个数据库字段更新为 NULL。

| 对比 | `update(null, wrapper)` | `update(student, wrapper)` |
|---|---|---|
| 更新字段来源 | Wrapper 的 `set(...)`、`setSql(...)` 等 | 实体属性，也可结合 Wrapper 的 SET 设置 |
| 筛选条件来源 | Wrapper | Wrapper |
| 是否需要提供实体 | 否 | 是，可以使用已有实体对象 |
| Mapper 返回值 | `int`，影响行数 | `int`，影响行数 |

例如，实体提供待更新的值，Wrapper 只负责筛选二班学生：

```java
Student student = new Student();
student.setScore(new BigDecimal("95"));
student.setGender("男");

LambdaUpdateWrapper<Student> wrapper = new LambdaUpdateWrapper<>();
wrapper.eq(Student::getClassName, "二班"); // WHERE 条件，不是要把班级改成二班

int rows = studentMapper.update(student, wrapper);
```

SQL 语义类似（实际使用参数绑定）：

```sql
UPDATE student SET score = 95, gender = '男'
WHERE class_name = '二班';
```

默认字段更新策略通常为 `NOT_NULL`，实体中未赋值、为 `null` 的普通属性不会进入 SET。**避免实体和 `wrapper.set(...)` 同时指定同一列，否则可能生成重复赋值。**

### 14.2 显式更新为 NULL

```java
// 这里只构造更新片段；还需传给 studentMapper.update(null, wrapper) 才会执行
new LambdaUpdateWrapper<Student>()
    .eq(Student::getId, 1L)
    .set(Student::getClassName, null);
```

上面的显式 `set(..., null)` 则可表达“把列设置为 `NULL`”。

### 14.3 setSql：使用 SQL 更新表达式

`UpdateWrapper`、`LambdaUpdateWrapper` 都支持 `setSql()`，可以直接编写 SET 部分的赋值表达式，传入时不带 `SET` 关键字。例如，把某个学生的成绩在原值基础上增加 5 分：

```java
LambdaUpdateWrapper<Student> wrapper = new LambdaUpdateWrapper<>();
wrapper.eq(Student::getId, 1L)
       .setSql("score = score + {0}", new BigDecimal("5"));
// 表达式使用数据库列名；{0} 绑定增量值，不是把用户输入拼进 SQL

int rows = studentMapper.update(null, wrapper);
```

SQL 类似 `UPDATE student SET score = score + ? WHERE id = ?`。

- `set(Student::getScore, new BigDecimal("5"))`：直接把成绩设为 5。
- `setSql("score = score + {0}", new BigDecimal("5"))`：由数据库根据当前成绩计算新值。

**普通赋值优先使用 `set()`，数据库表达式再考虑 `setSql()`。** SQL 片段由后端编写，值用 `{0}` 等占位符绑定，不要直接拼接用户输入。

⚠️ **更新、删除前检查 WHERE 范围**，否则可能影响全表；可按需配置防全表更新删除插件。

---

# 第七篇：Service 层通用能力

## 15. IService / ServiceImpl

【**MP 增强**】MP 除 Mapper 通用 CRUD 外，还提供 Service 层通用接口和默认实现。

```java
public interface StudentService extends IService<Student> {
    // 这里可以继续声明业务方法
}
```

```java
@Service // 将实现类注册为 Spring Bean，供其他组件注入
public class StudentServiceImpl
        extends ServiceImpl<StudentMapper, Student>
        implements StudentService {
}
```

> [!note]
> `ServiceImpl<M, T>` 中，`M` 是 Mapper 类型，`T` 是实体类型。新版 MP 文档也建议了解 `IRepository`；旧项目仍大量使用 `IService`。

| 对比 | Mapper | Service |
| ---------- | ------------------------ | -------------------------- |
| 对象创建机制 | MyBatis 创建 Mapper 代理 | Spring 创建 Service Bean |
| 通用方法来源 | `BaseMapper` + MP SQL 映射 | `IService` + `ServiceImpl` |
| 是否需要自己写实现类 | 通常不需要 | 通常需要 |
| 主要职责 | 数据库访问 | 业务逻辑及事务协调 |

---

## 16. Service 常用方法

| Service 方法 | 作用 | 典型返回值 |
|---|---|---|
| `save(entity)` | 新增 | `boolean` |
| `saveBatch(list,batchSize)` | **批量**新增,`batchSize`：指定每批处理多少条记录 | `boolean` |
| `getById(id)` | 主键查询 | `T` |
| `list(wrapper)` | 查询列表 | `List<T>` |
| `count(wrapper)` | 统计数量 | `long` / `Long`（按版本签名） |
| `updateById(entity)` | 主键更新 | `boolean` |
| `removeById(id)` | 主键删除 | `boolean` |
| `removeByIds(ids)` | 按主键集合批量删除 | `boolean` |
| `page(page, wrapper)` | 分页查询 | `IPage<T>` |

```java
// 业务层调用示意
Student student = studentService.getById(1L);
boolean ok = studentService.save(newStudent); // newStudent 为已准备好的实体；返回操作结果，不是主键
List<Student> list = studentService.list(
    new LambdaQueryWrapper<Student>().ge(Student::getAge, 18)
);
```

### 16.1 ⚠️ 不要把“通用 Service”当成业务层设计

- 业务规则仍应放到自己写的 `Service` 方法中。
- 跨多个 Mapper 的一致性更新，仍需要 `@Transactional`。
- Controller 不应因为 `IService` 方法方便就越过业务层直接操作数据库。

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

> [!example] 为什么创建了 Page 还需要插件？
>
> `new Page<Student>(3, 4)` 只保存“第 3 页、每页 4 条”。调用 `studentMapper.selectPage(page, wrapper)` 时，`PaginationInnerInterceptor` 才读取 `current` 和 `size`，按 MySQL 方言改写查询。
>
> 例如，按 `id` 稳定排序时，偏移量为 `(3 - 1) * 4 = 8`。开启总数统计时，插件按需先执行 `COUNT` 查询，再由 MyBatis 通过 JDBC 执行带 `ORDER BY id ASC LIMIT 8, 4` 的数据查询，取排序后的第 9 至 12 条记录（若存在）。

### 17.1 添加分页解析依赖

`mybatis2` 示例使用 Spring Boot `4.1.1`、MP `3.5.17`、JDK 21、MySQL 8.0 和 Maven。项目已有 `com.baomidou:mybatis-plus-spring-boot4-starter:3.5.17`，保留现有 Starter。

从 MP `3.5.9` 起，分页解析模块需单独引入。该项目使用 JDK 21，在 `pom.xml` 的 `<dependencies>` 中加入标准版 `mybatis-plus-jsqlparser`，版本与 Starter 一致。[官方分页文档](https://baomidou.com/plugins/pagination/)

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-jsqlparser</artifactId>
    <version>3.5.17</version>
</dependency>
```

在 IDEA 的 Maven 面板重新加载项目，确认该依赖已解析，再配置拦截器。

### 17.2 注册分页拦截器

配置文件位于 `src/main/java/org/example/mybatis2/config/MybatisPlusConfig.java`。

```java
package org.example.mybatis2.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MybatisPlusConfig {

    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        PaginationInnerInterceptor pagination = new PaginationInnerInterceptor(DbType.MYSQL);
        pagination.setOverflow(false); // 超出总页数时返回空页，采用默认行为
        pagination.setMaxLimit(100L); // 本例设置单页上限为 100 条
        interceptor.addInnerInterceptor(pagination);
        return interceptor;
    }
}
```

- `@Configuration` 标记配置类。若启动类在 `org.example.mybatis2` 包下，默认组件扫描会覆盖 `config` 子包。
- `@Bean` 将返回的 `MybatisPlusInterceptor` 注册为 Spring Bean，供 MP 接入 MyBatis 插件体系。
- `addInnerInterceptor(...)` 将分页处理器加入插件容器。`DbType.MYSQL` 指定分页方言。使用多个内部拦截器时，分页拦截器最后添加。

---

## 18. 分页查询

### 18.1 从 LIMIT 理解分页

假设 `student` 表共有 17 条记录，每页展示 5 条，并按 `id` 升序查询：

| 页码 | SQL 分页范围 | 本页记录数 |
|---|---|---|
| 第 1 页 | `LIMIT 0, 5` | 5 |
| 第 2 页 | `LIMIT 5, 5` | 5 |
| 第 3 页 | `LIMIT 10, 5` | 5 |
| 第 4 页 | `LIMIT 15, 5` | 2 |

页码从 1 开始时，**`offset = (current - 1) * size`**：`current` 是当前页码，`size` 是每页条数，`offset` 是跳过的结果行数。实际查询应有明确的 `ORDER BY`，不要依赖数据库的自然返回顺序。

### 18.2 Page：既保存请求参数，也承载查询结果

假设前文的分页插件已经配置：

```java
Page<Student> page = new Page<>(2, 5); // 第 2 页，每页 5 条；Student 是记录的实体类型
LambdaQueryWrapper<Student> wrapper = new LambdaQueryWrapper<>();
wrapper.orderByAsc(Student::getId); // 本例不筛选记录，只指定稳定排序

IPage<Student> result = studentMapper.selectPage(page, wrapper);
// 通常包含 COUNT 查询与本页数据查询；数据 SQL 类似 ORDER BY id ASC LIMIT 5, 5
```

`Page` 的构造参数是**页码与每页条数，不是 offset**。`selectPage` 的第二个参数是 Wrapper，传 `null` 表示不额外设置条件，本例使用它指定排序。

**selectList 与 selectPage 的区别**

**分页针对符合 Wrapper 条件的记录。** 筛选条件进入 SQL 的 `WHERE`，数据库对满足条件的结果进行排序和分页，而不是先从全表取出一页，再在 Java 中筛选。

| 方法 | 功能 | 返回内容 |
|---|---|---|
| `selectList(wrapper)` | 按 Wrapper 查询符合条件的记录列表 | `List<Student>` |
| `selectPage(page, wrapper)` | 根据页码与每页条数查询指定页 | 分页对象，包含本页记录和分页信息，可用 `IPage<Student>` 接收 |

在本例使用的 MP `3.5.17` 中，传入 `Page<Student>` 时，也可写为 `Page<Student> result = studentMapper.selectPage(page, wrapper)`。如果只需要本页的学生列表，调用 `result.getRecords()`。

### 18.3 读取分页结果

继续以上例为例，若总数统计得到 17 条：

| 方法 | 含义 | 本例结果 |
|---|---|---|
| `result.getRecords()` | 当前页的 `Student` 列表 | 第 2 页的 5 条记录 |
| `result.getTotal()` | 符合条件的总记录数，需执行统计查询 | 17 |
| `result.getCurrent()` | 当前页码，不是偏移量 | 2 |
| `result.getSize()` | 设置的每页条数 | 5 |
| `result.getPages()` | 根据总记录数与每页条数计算的总页数 | 4 |

**`size` 不等于实际返回条数。** 例如第 4 页的 `getSize()` 仍为 5，但 `getRecords().size()` 为 2；`getRecords()` 返回的也不是全部 17 条记录。

复杂 JOIN / `GROUP BY` 的总数统计需要检查实际生成 SQL，必要时自定义 COUNT。

### 18.4 searchCount：是否自动查询总数

`searchCount` 属于单个 `Page`，默认为 `true`。例如第 2 页、每页 3 条时，通常会先统计符合条件的总数，再执行带 `LIMIT 3, 3` 的数据查询。

```java
Page<Student> page = new Page<>(2, 3);
page.setSearchCount(false); // 只关心本页记录时，可跳过自动 COUNT
```

分页数据查询负责“取这一页”，COUNT 查询负责“统计一共有多少条”。关闭 COUNT 后，当前页仍能正常查询，但总记录数不会自动统计。

例如，数据库中实际有 8 条符合条件的记录，每页 3 条，查询第 2 页。使用上面新建的 `Page`，且没有手动设置总数时：

| 读取内容 | 开启 COUNT | 关闭 COUNT |
|---|---|---|
| `getRecords().size()` | 3，拿到第 2 页的记录 | 3，仍能拿到第 2 页的记录 |
| `getTotal()` | 8，来自总数统计 | 0，保留新对象的默认值 |
| `getPages()` | 3，根据总数 8 和每页 3 条计算 | 0，根据尚未更新的总数 0 计算 |

**右侧的 0 表示总数没有统计。** 数据库里仍有 8 条记录，第 3 页仍有 2 条，所以不能据此判断“没有记录”或“没有下一页”。需要准确显示总条数、总页数时，应开启 COUNT 或另行提供准确的总数。

### 18.5 overflow：页码超出总页数

`overflow` 属于分页拦截器，会影响使用该拦截器的分页查询。假设符合条件的记录共 8 条，每页 3 条，共 3 页，却请求 `new Page<Student>(100, 3)`：

- 默认 `overflow=false`，保留请求页码，当前页记录通常为空。
- 在第 17.2 节的配置中改为 `pagination.setOverflow(true)`，当总数统计能确认页码越界且结果集非空时，将请求调整回第 1 页。

**超页回退依赖总数统计。** 使用 `page.setSearchCount(false)` 时，插件会跳过这段越界判断，不能期待 `overflow=true` 自动将请求改回第一页。

### 18.6 maxLimit：限制单页条数

分页拦截器的 `maxLimit` 默认未设置。第 17.2 节示例通过 `pagination.setMaxLimit(100L)` 配置单页上限，限制过大的每页条数，例如 `new Page<Student>(1, 1_000_000)`。

Service 层仍应校验 `pageNum >= 1`、`pageSize >= 1` 以及业务允许的最大条数，示例见第 26 节。插件上限用于限制分页 SQL 的数据量，参数是否合法由业务层明确处理。

在 MP `3.5.17` 中，若单个 `Page` 另设 `maxLimit`，会优先使用该值，因此这些上限应由服务端统一控制。[MP 3.5.17 分页实现](https://github.com/baomidou/mybatis-plus/blob/v3.5.17/mybatis-plus-jsqlparser-support/mybatis-plus-jsqlparser/src/main/java/com/baomidou/mybatisplus/extension/plugins/inner/PaginationInnerInterceptor.java#L153)

---

# 第九篇：自动填充

## 19. @TableField(fill) + MetaObjectHandler

【**MP 增强**】用于新增时间、修改时间等字段。

**只添加 `@TableField(fill = ...)`，不会自动填入当前时间。** 注解声明字段何时参与填充，`MetaObjectHandler` 负责填什么值、如何填充。

### 19.1 声明字段的填充时机

```java
// 以下字段需加入 Student，同时在数据库中增加对应的 create_time、update_time 列
@TableField(value = "create_time", fill = FieldFill.INSERT)
private LocalDateTime createTime;

@TableField(value = "update_time", fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updateTime;
```

- `value`：指定数据库列名，例如 Java 属性 `createTime` 对应 `create_time`。MP 默认开启驼峰与下划线映射，符合命名规则时可以省略 `value`，这里显式写出便于理解。
- `fill`：指定自动填充时机，具体策略见下表。
- `LocalDateTime`：Java 8 引入的日期时间类型，不包含时区信息，常用于映射 MySQL 的 `DATETIME`。

| 策略 | 插入时 | 更新时 |
|---|---|---|
| `FieldFill.DEFAULT` | 不自动填充 | 不自动填充 |
| `FieldFill.INSERT` | 允许填充 | 不填充 |
| `FieldFill.UPDATE` | 不填充 | 允许填充 |
| `FieldFill.INSERT_UPDATE` | 允许填充 | 允许填充 |

### 19.2 实现填充处理器

`MetaObjectHandler` 是 MP 提供的自动填充接口，主要有两个回调方法：

| 方法 | 触发场景 | 典型用途 |
|---|---|---|
| `insertFill()` | 适用的实体插入操作 | 设置创建时间、初始修改时间 |
| `updateFill()` | 适用的实体更新操作 | 设置修改时间 |

实现示例：

```java
@Component // 注册填充处理器，MP 才能在处理实体时使用它
public class AuditMetaObjectHandler implements MetaObjectHandler {

    @Override
    public void insertFill(MetaObject metaObject) {
        // 同一次插入共用 now，保持两个时间一致
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

**相关导入**：

```java
import com.baomidou.mybatisplus.core.handlers.MetaObjectHandler;
import org.apache.ibatis.reflection.MetaObject;
```

以 `strictInsertFill(metaObject, "createTime", LocalDateTime.class, now)` 为例，四个参数分别为：

| 参数 | 含义 |
|---|---|
| `metaObject` | 当前操作实体的元对象包装，用于读写属性 |
| `"createTime"` | Java 属性名，使用 `createTime`，而非数据库列名 `create_time` |
| `LocalDateTime.class` | 属性类型 |
| `now` | 希望填入的值，这里来自 `LocalDateTime.now()` |

`strictInsertFill()`、`strictUpdateFill()` 要求属性名、类型和填充策略匹配，默认不覆盖非空属性，填充值为 `null` 时不填充。旧更新时间的问题见第 19.4 节。

### 19.3 执行流程与更新限制

以 `studentMapper.insert(student)` 为例：

```text
MP 处理实体及其填充标记 → 调用 insertFill() → 给实体属性赋值 → 执行 INSERT SQL
```

自动填充是在 SQL 执行前修改实体属性，不会给 MySQL 表创建默认值或触发器。

**更新自动填充需要提供实体。** `MetaObjectHandler` 主要给实体属性赋值，不会直接向 Wrapper 的 `SET` 条件中追加更新时间。

| 更新方式 | `score` 更新来源 | `updateTime` 自动填充 |
|---|---|---|
| `update(null, wrapper)` | `wrapper.set()` | 不触发 |
| `update(entity, wrapper)` | 实体属性，也可结合 `wrapper.set()` | 满足填充条件时可以 |
| `updateById(entity)` | 实体属性，按实体主键更新 | 满足填充条件时可以 |

**方案一：提供实体，由处理器填充时间。**

```java
Student student = new Student();
student.setScore(new BigDecimal("90"));
// 新实体的 updateTime 为 null，可由上面的处理器填充

LambdaUpdateWrapper<Student> wrapper = new LambdaUpdateWrapper<>();
wrapper.eq(Student::getClassName, "一班");

studentMapper.update(student, wrapper);
```

**方案二：通过 Wrapper 显式设置时间。**

```java
LambdaUpdateWrapper<Student> wrapper = new LambdaUpdateWrapper<>();
wrapper.eq(Student::getClassName, "一班")
       .set(Student::getScore, new BigDecimal("90"))
       .set(Student::getUpdateTime, LocalDateTime.now());

studentMapper.update(null, wrapper);
```

方案二不依赖处理器。项目中应统一更新时间管理方式，同一字段避免同时由实体和 Wrapper 赋值（见第 14.1 节）。

### 19.4 不自动刷新，不代表不参与 UPDATE

如果先查询学生，再修改成绩并调用 `updateById(student)`，实体通常带有旧的 `updateTime`。按上述严格填充规则，旧时间不会刷新，SQL 仍可能把它写回：

```sql
UPDATE student
SET score = 100,
    update_time = '2026-11-02 21:02:45'
WHERE id = 1;
```

**填充逻辑决定是否改写实体属性，更新 SQL 决定哪些属性写入数据库，两者需要区分。**

希望每次更新都刷新时间，可以选择：

- 更新时让实体的 `updateTime` 为 `null`，由已配置的严格填充逻辑补入当前时间。这里的 `null` 是填充前的属性值，并不表示最终写入数据库的是 `NULL`。
- 在处理器的 `updateFill()` 中，针对修改时间设计强制覆盖逻辑，不依赖 `strictUpdateFill()` 默认的非空不覆盖规则。

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

### 20.1 value 与 delval

| 参数 | 含义 | 本例配置 |
|---|---|---|
| `value` | 未删除标记 | `"0"` |
| `delval` | 已删除标记 | `"1"` |

注解参数使用字符串表示配置，不会改变字段类型。本例 `deleted` 仍是数据库中的 `TINYINT` 列，生成 SQL 时使用数值 `0`、`1`。

### 20.2 对删除、查询和更新的影响

以本例的 `@TableLogic(value = "0", delval = "1")` 为例：

```text
初始化阶段：
Student 实体中的 @TableLogic
    ↓
MP 解析实体的表映射信息
    ↓
为 BaseMapper 内置方法生成 SQL 映射
    ├── deleteById → UPDATE，设置 deleted = 1，并限定 deleted = 0
    ├── selectById → 查询条件附加 deleted = 0
    └── updateById → 更新条件附加 deleted = 0

运行阶段：
调用 Service / Mapper → MyBatis 执行对应 SQL → MySQL
```

**`@TableLogic` 参与内置 SQL 的生成。** 删除模板在初始化时选定，不是运行时根据记录的 `deleted` 值决定使用 UPDATE 还是 DELETE。[MP 3.5.17 实现](https://github.com/baomidou/mybatis-plus/blob/v3.5.17/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/injector/methods/DeleteById.java)

Service 的 `removeById()` 调用 Mapper 的 `deleteById()`，执行已生成的删除 SQL：

```java
studentService.removeById(1L);
```

配置生效前后的 SQL 语义如下：

```sql
-- 未启用逻辑删除：物理删除记录
DELETE FROM student WHERE id = ?;

-- 启用逻辑删除：修改标记，只处理未删除记录
UPDATE student
SET deleted = 1
WHERE id = ? AND deleted = 0;
```

`studentService.getById(id)`、`studentService.list()` 等通用查询会添加 `deleted = 0` 条件，排除已删除记录。

**对同一条已删除记录，两种删除方式的区别：**

| 操作 | 物理删除后 | 逻辑删除后 |
|---|---|---|
| MP 普通查询 | 查不到 | 被 `deleted = 0` 条件排除 |
| MP 内置 `updateById()` | 无记录可更新 | 被 `deleted = 0` 条件排除，默认无法更新 |
| MySQL 原生 SELECT | 查不到 | 不加未删除条件时可以查到 |
| MySQL 原生 UPDATE | 无记录可更新 | 可以修改保留的记录 |
| 恢复数据 | 通常需要备份等恢复手段 | 可通过受控操作将删除标记改回 `0` |

**MySQL 本身不知道 Java 中的 `@TableLogic`。** 例如终端执行 `SELECT * FROM student`，仍能查到 `deleted = 1` 的记录；要排除它们，需自行添加 `WHERE deleted = 0`。手写 SQL 也应自行确认逻辑删除条件。

**逻辑删除也不会在数据库层面禁止更新。** 例如，直接执行以下原生 SQL，仍可修改已逻辑删除记录的成绩：

```sql
UPDATE student SET score = 100
WHERE id = 1 AND deleted = 1;
```

原生 SQL 修改或恢复逻辑删除数据，应有明确的权限和业务规则，不能因记录仍在表中就随意操作。

### 20.3 需要物理删除时怎么办？

已启用逻辑删除时，普通 `removeById()` 仍按逻辑删除规则执行。确需彻底删除，可在已有 `StudentMapper` 中增加专门的方法：

```java
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Param;

public interface StudentMapper extends BaseMapper<Student> {
    @Delete("DELETE FROM student WHERE id = #{id}")
    int physicalDeleteById(@Param("id") Long id);
}
```

```java
int rows = studentMapper.physicalDeleteById(1L); // 执行 DELETE，可删除已逻辑删除的记录
```

这个手写 DELETE 与 MySQL 终端执行的 DELETE 都可物理删除记录，不会仅因 `@TableLogic` 改成 UPDATE。应通过独立入口和权限区分日常逻辑删除与彻底清理。

> [!warning]
> **逻辑删除不等于事务回滚，也不等于数据库真正删除。** 如果业务经常需要查询归档/删除数据，应重新评估是否适合用逻辑删除。

### 20.4 逻辑删除与唯一索引冲突

以下用独立的 `user` 表说明，不需要修改前文的 `student` 表设计。

**① 只有用户名唯一：逻辑删除后仍占用用户名。**

```sql
UNIQUE KEY uk_username (username)
```

注册 `zhangsan` 后再逻辑删除，原记录仍在表中。即使 MP 普通查询已查不到它，再插入同名用户仍会违反唯一约束，出现 `Duplicate entry`。

**② 改成联合唯一索引：固定的 0 / 1 标记仍有限制。**

```sql
UNIQUE KEY uk_username_deleted (username, deleted)
```

此时 `(zhangsan, 0)` 与 `(zhangsan, 1)` 可以共存，因此删除后能重新注册。但再次删除新用户时，也要改成 `(zhangsan, 1)`，会与旧记录冲突。**它只能保留一条同名的已删除记录。**

**③ 一种方案：让历史记录使用不同的删除标记。**

将 `deleted` 设计为 `BIGINT NOT NULL DEFAULT 0`，配合上述联合唯一索引：正常记录固定为 `0`，已删除记录使用自身非零主键 ID。例如：

| id | username | deleted | 状态 |
|---|---|---|---|
| 101 | zhangsan | 101 | 历史删除记录 |
| 102 | zhangsan | 102 | 历史删除记录 |
| 103 | zhangsan | 0 | 当前正常记录 |

这样既能保留多条同名历史记录，又能保证正常记录的用户名唯一。对应的 `User` 属性可以配置为：

```java
@TableLogic(value = "0", delval = "id")
private Long deleted;
```

这里 `delval = "id"` 引用数据库主键列，删除时生成类似 `UPDATE user SET deleted = id WHERE id = ? AND deleted = 0` 的 SQL；字段使用数值类型 `Long`，而非字符串类型。[官方说明](https://baomidou.com/guides/logic-delete/)

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
// 添加到前文配置类的同一个 MybatisPlusInterceptor 中，不是单独创建一个无关联对象
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
Student s = studentMapper.selectById(1L); // 同时读取 version；实际业务应先检查查询结果是否为 null
s.setName("新名字");
int rows = studentMapper.updateById(s); // 插件携带旧版本作为条件，并生成新版本值
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
// Service 层：studentList 是待新增实体的集合
boolean inserted = studentService.saveBatch(studentList);

// Service 层：根据主键批量更新，集合中每个实体都应设置自己的 id
boolean updated = studentService.updateBatchById(studentList);
```

### 22.1 三种更新方式如何选择

以下以 **Service 层方法**为例，返回值均为 `boolean`：

| 方法 | 更新方式 | 典型场景 |
|---|---|---|
| `updateById(student)` | 一个实体按自身主键更新一条记录 | 修改一名学生的成绩 |
| `updateBatchById(studentList)` | 多个实体分别按各自主键更新，可以设置不同值 | 多名学生分别设置不同成绩 |
| `update(wrapper)` | 用统一条件筛选记录，更新内容由 Wrapper 的 SET 设置提供 | 将某班成绩低于 60 分的学生统一调整为 60 分 |

例如，第三种写法不需要先查出每名学生，再逐个按 ID 更新：

```java
LambdaUpdateWrapper<Student> wrapper = new LambdaUpdateWrapper<>();
wrapper.eq(Student::getClassName, "二班")
       .lt(Student::getScore, new BigDecimal("60"))
       .set(Student::getScore, new BigDecimal("60"));

boolean updated = studentService.update(wrapper); // WHERE 与 SET 都由 Wrapper 提供
```

### 22.2 removeByIds：按主键集合批量删除

适合页面勾选多条记录后删除，传入的是**主键集合，不是 Wrapper**：

```java
List<Long> ids = List.of(1L, 2L, 3L);
boolean removed = studentService.removeByIds(ids); // 返回操作结果，不是删除条数
```

- 未启用逻辑删除时，SQL 语义类似 `DELETE FROM student WHERE id IN (1, 2, 3)`；配置了 `@TableLogic` 时，按逻辑删除规则修改删除标记。
- Mapper 层对应 `studentMapper.deleteByIds(ids)`，返回 `int` 影响行数；按业务条件删除则使用 `studentService.remove(wrapper)`。
- 实际请求中先校验主键集合非空，并确认允许操作的记录范围。

### 22.3 与原生 MyBatis <foreach> 的区别

- 具体是**逐条执行/批处理发送**还是**拼接为单条多 VALUES SQL**，不能只靠 `saveBatch` 方法名推断。
- 超大批次可能占用大量内存、连接资源、锁资源；要考虑合理分批、事务范围和驱动行为。
- **复杂批量插入 SQL** 仍可自己写 XML `<foreach>`。

---

# 第十三篇：与原生 MyBatis 混合使用

## 23. BaseMapper 与 XML 可以共存

【**重点**】MP 不是“禁止写 XML”。

```java
public interface StudentMapper extends BaseMapper<Student> {
    // 为 XML 参数命名，使 #{minScore} 可以引用这个方法参数
    List<Student> selectExcellentStudents(@Param("minScore") BigDecimal minScore);
}
```

对应 `resources/mapper/StudentMapper.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<!-- namespace 是 Mapper 接口全限定名，select 的 id 对应接口方法名 -->
<mapper namespace="com.example.mapper.StudentMapper">
    <select id="selectExcellentStudents"
            resultType="com.example.entity.Student">
        SELECT id, name, age, gender, score, class_name
        FROM student
        <!-- XML 中 &gt; 表示 >；#{minScore} 通过参数绑定传值 -->
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
    // Enrollment / EnrollmentMapper 表示报名记录及其 Mapper，本例省略它们的定义
    private final EnrollmentMapper enrollmentMapper;

    // 单构造器由 Spring 注入两个 Mapper，无需再手动 new
    public RegistrationService(StudentMapper studentMapper,
                               EnrollmentMapper enrollmentMapper) {
        this.studentMapper = studentMapper;
        this.enrollmentMapper = enrollmentMapper;
    }

    @Transactional(rollbackFor = Exception.class) // 通过 Spring 代理调用时，抛出 Exception 也回滚
    public void register(Student student, Enrollment enrollment) {
        studentMapper.insert(student);
        // 前一次插入已回填学生主键，作为报名记录关联的 studentId
        enrollment.setStudentId(student.getId());
        enrollmentMapper.insert(enrollment);
    }
}
```

- Spring 事务机制仍涉及 `DataSourceTransactionManager`、事务绑定的 `Connection`、MyBatis-Spring 会话管理。
- `@Transactional` 代理、自调用、异常回滚规则等知识**仍然适用**。

---

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

### 25.1 Wrapper 工程原则速查

| 场景 | 推荐方式 |
|---|---|
| 普通比较、范围、集合、模糊查询 | 优先使用 `eq / gt / between / in / like` 等内置条件方法 |
| 可选查询参数 | 使用 `condition` 参数控制是否添加条件 |
| 多条件逻辑分组 | 使用 `and(...)`、`or(...)`、`nested(...)` 明确括号范围 |
| 特殊数据库表达式 | 条件表达式用 `apply()`，更新表达式用 `setSql()`；值通过 `{0}` 等占位符绑定 |
| SQL 尾部追加 | 谨慎使用 `last()`；常规分页优先使用 `Page` 与分页插件 |
| 复杂关联、聚合业务 | 考虑 XML 或自定义查询，不强求全部用 Wrapper 表达 |
| 动态字段名、SQL 片段 | 字段名通过服务端白名单映射，SQL 片段由后端控制；不能直接信任用户输入 |
| Wrapper 的创建与共享 | 每次操作新建，不把可变 Wrapper 作为共享单例 |
| 条件更新、删除 | 执行前检查最终 WHERE 的实际范围，尤其注意动态条件被跳过的情况 |
| SQL 性能 | 结合 EXPLAIN、索引和数据量评估；使用 MP 不代表 SQL 自动更快 |

---

# 第十五篇：完整小案例（学生条件分页）

## 26. 从请求条件到分页结果

假定 `Student` 与 `StudentMapper` 已按前文定义，分页插件已配置。

```java
public IPage<Student> searchStudents(String name,
                                     Integer minAge,
                                     long pageNum,
                                     long pageSize) {
    // 在访问数据库前检查页码与单页上限，避免非法或过大的分页请求
    if (pageNum < 1 || pageSize < 1 || pageSize > 100) {
        throw new IllegalArgumentException("分页参数非法");
    }

    LambdaQueryWrapper<Student> wrapper = new LambdaQueryWrapper<>();
    // 未填写的筛选项不加入 WHERE；like 默认在关键词两侧补 %
    wrapper.like(name != null && !name.isBlank(), Student::getName, name)
           .ge(minAge != null, Student::getAge, minAge)
           .orderByDesc(Student::getScore)
           .orderByAsc(Student::getId); // 同分时按唯一主键排序，保证排序规则确定

    Page<Student> page = new Page<>(pageNum, pageSize);
    // 返回分页对象：既包含本页 records，也包含 total、current、size 等元信息
    return studentMapper.selectPage(page, wrapper);
}
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

# 第十六篇：开发速查

## 27. 常用功能与 API 速查

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
