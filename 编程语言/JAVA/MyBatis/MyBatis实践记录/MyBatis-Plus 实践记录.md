# MyBatis-Plus 实践记录

---

## 一、条件查询与条件更新

### 案例 001：Wrapper 条件构造

> [!note] 实践信息
> - **技术**：QueryWrapper、LambdaQueryWrapper、UpdateWrapper、LambdaUpdateWrapper
> - **状态**：已完成实操验证。

**1. 实践内容**

完成条件查询、排序、嵌套 AND/OR、动态条件及条件更新。

代表性代码：

```java
LambdaQueryWrapper<Student> wrapper = new LambdaQueryWrapper<>();

wrapper.eq(Student::getClassName, "一班")
       .ge(Student::getScore, 90)
       .orderByDesc(Student::getScore)
       .orderByAsc(Student::getId);

studentMapper.selectList(wrapper);
```

对应 SQL 逻辑：

```sql
SELECT *
FROM student
WHERE class_name = '一班'
  AND score >= 90
ORDER BY score DESC, id ASC;
```

**2. 遇到的问题**

- `Student::getClassName` 用于解析实体属性，并非执行 Getter 取值。
- 嵌套 `and(w -> ...)` 中的 `w` 是内部条件构造器。
- 动态条件为 `false` 时会跳过该条件，可能导致更新范围意外扩大。

**3. 实践结论**

四种 Wrapper 的核心功能已完成实操。**条件更新必须检查 WHERE 范围，避免误更新。**

---

## 二、批量操作

### 案例 002：saveBatch 批量插入

> [!note] 实践信息
> - **技术**：`saveBatch()`
> - **测试记录**：ID 25、26、27
> - **状态**：批量插入成功，数据已清理。

**1. 关键代码**

```java
boolean success = studentService.saveBatch(students, 2);
```

插入三条测试记录，`batchSize = 2`。

**2. 验证结果**

```text
保存结果：true
回填 ID：25、26、27

第一批：2 条
第二批：1 条
```

测试后确认三条临时记录已物理删除。

**3. 实践结论**

- `batchSize` 控制批次处理规模，不代表事务边界。
- 批量处理不一定生成一条多行 INSERT SQL。
- 应验证返回值、主键回填和数据库实际结果。

> `updateBatchById()` 已学习原理，未单独完成数据库实操。

---

## 三、分页查询

### 案例 003：分页插件与条件分页

> [!note] 实践信息
> - **技术**：`Page<T>`、`PaginationInnerInterceptor`
> - **状态**：普通分页与条件分页均已验证。

**1. 关键配置**

```java
interceptor.addInnerInterceptor(
    new PaginationInnerInterceptor(DbType.MYSQL)
);
```

**2. 普通分页**

```java
Page<Student> page = new Page<>(3, 4);

studentMapper.selectPage(page,
    new LambdaQueryWrapper<Student>()
        .orderByAsc(Student::getId));
```

实际 SQL 参数：

```text
LIMIT 8, 4
总记录数：17
返回 ID：11、12、13、14
```

**3. 条件分页**

条件：一班、成绩 ≥ 90，按成绩降序、ID 升序。

```text
current = 2
size = 3
total = 8
pages = 3

返回 ID：14、12、16
```

**4. 实践结论**

- 分页插件负责生成分页 SQL。
- COUNT 统计符合条件的总记录数。
- 分页应设置稳定排序，必要时增加 ID 作为排序条件。

---

## 四、自动填充

### 案例 004：MetaObjectHandler 自动维护时间

> [!note] 实践信息
> - **技术**：`@TableField`、`MetaObjectHandler`
> - **测试记录**：ID 28
> - **状态**：新增、修改和物理清理验证成功。

**1. 关键配置**

```java
@TableField(value = "create_time", fill = FieldFill.INSERT)
private LocalDateTime createTime;

@TableField(value = "update_time", fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updateTime;
```

处理器：

```java
@Override
public void insertFill(MetaObject metaObject) {
    LocalDateTime now = LocalDateTime.now();

    strictInsertFill(metaObject, "createTime", LocalDateTime.class, now);
    strictInsertFill(metaObject, "updateTime", LocalDateTime.class, now);
}

@Override
public void updateFill(MetaObject metaObject) {
    strictUpdateFill(metaObject, "updateTime",
                     LocalDateTime.class, LocalDateTime.now());
}
```

**2. 遇到的问题**

- 最初将 Java 属性名误写为数据库列名 `create_time`、`update_time`。
- 最初插入时漏填 `updateTime`。
- 使用完整查询实体更新时，`updateTime` 已非空，严格填充默认不会覆盖旧值。

**3. 验证结果**

```text
INSERT：createTime、updateTime 均成功填充
UPDATE：score 80 → 90，updateTime 更新
createTime：保持不变
DELETE：Updates = 1
```

**4. 实践结论**

`MetaObjectHandler` 使用 **Java 属性名**，`strictUpdateFill()` 默认只填充符合条件的空属性。

---

## 五、逻辑删除

### 案例 005：@TableLogic 删除与过滤

> [!note] 实践信息
> - **技术**：`@TableLogic`
> - **测试记录**：ID 29
> - **状态**：逻辑删除成功，物理清理待确认。

**1. 关键配置**

```java
@TableLogic(value = "0", delval = "1")
private Integer deleted;
```

**2. 实际操作**

```java
studentService.removeById(29);
```

实际 SQL：

```sql
UPDATE student
SET update_time = ?, deleted = 1
WHERE id = ? AND deleted = 0;
```

运行结果：

```text
Updates: 1
removeById() = true
getById(29) = null

MySQL 直接查询：
id = 29, deleted = 1
```

**3. 遇到的问题**

- `student.setDeleted(1)` 只修改 Java 对象，不会执行数据库更新。
- 逻辑删除后的数据仍然存在于数据库。
- 逻辑删除字段与唯一索引组合不合理时，可能影响重新创建和再次删除。

**4. 实践结论**

MP 内置删除操作通过 UPDATE 修改删除标记，普通查询自动过滤已逻辑删除记录。

---

## 六、乐观锁

### 案例 006：@Version 防止旧版本覆盖

> [!note] 实践信息
> - **技术**：`@Version`、`OptimisticLockerInnerInterceptor`
> - **测试记录**：ID 30
> - **状态**：乐观锁冲突验证成功，已逻辑清理。

**1. 关键配置**

```java
@Version
private Integer version;
```

```java
interceptor.addInnerInterceptor(
    new OptimisticLockerInnerInterceptor()
);
```

**2. 实践过程**

```java
Student studentA = studentService.getById(id);
Student studentB = studentService.getById(id);

studentA.setScore(90);
boolean resultA = studentService.updateById(studentA);

studentB.setScore(100);
boolean resultB = studentService.updateById(studentB);
```

A、B 均先读取版本 1，再依次更新。

**3. 实际运行结果**

| 检查项目 | 结果 |
|---|---|
| A 初始版本 | 1 |
| B 初始版本 | 1 |
| A 更新成绩 90 | `true`，Updates = 1 |
| B 更新成绩 100 | `false`，Updates = 0 |
| 最终成绩 | 90 |
| 最终版本 | 2 |
| 测试数据逻辑清理 | 成功，ID 30 |

关键 SQL 条件：

```sql
WHERE id = ?
  AND version = ?
  AND deleted = 0
```

**4. 发现的问题**

直接更新完整查询实体：

```java
studentA.setScore(90);
studentService.updateById(studentA);
```

可能将姓名、年龄、创建时间等非空字段一起写入 SQL。

更适合部分字段更新的方式：

```java
Student updateStudent = new Student();

updateStudent.setId(studentA.getId());
updateStudent.setScore(90);
updateStudent.setVersion(studentA.getVersion());

studentService.updateById(updateStudent);
```

这样只提交必要业务字段和旧版本号，`updateTime` 为 `null` 时还可以触发严格自动填充。

**5. 实践结论**

- 乐观锁通过旧版本号检测冲突。
- 更新成功后，整数版本号递增。
- 版本冲突可能返回 `false`，不一定抛出异常。
- 乐观锁不能替代事务。
- ID 30 已逻辑删除，物理清理待确认。

---

## 七、核心机制总结

| 功能 | 核心机制 | 状态 |
|---|---|---|
| Wrapper | 构造 SQL 条件与更新字段 | 已实操 |
| `saveBatch()` | 批次处理，批次不等于事务 | 已实操 |
| 分页 | 拦截器处理 COUNT、LIMIT | 已实操 |
| 自动填充 | `MetaObjectHandler` 填充实体属性 | 已实操 |
| 逻辑删除 | 删除转 UPDATE，查询自动过滤 | 已实操 |
| 乐观锁 | 版本号匹配与递增 | 已实操 |
| `updateBatchById()` | 按主键批量更新 | 已学习原理 |

> [!important] 阶段结论
> 已完成 MyBatis-Plus 常用功能的核心实操，能够结合 Java 代码、SQL 日志和数据库查询验证结果。下一步通过完整 Spring Boot 项目巩固业务层应用。

---