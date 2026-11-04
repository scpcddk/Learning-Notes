# MySQL 实践记录

> **数据库环境**：MySQL 8.0.46 / InnoDB  
> **主要实践数据库**：`school`  
> **主要实践表**：`student`  
> **记录范围**：SQL 基础、复杂查询、数据库设计、索引、执行计划、事务、MVCC 与锁  
> **说明**：本记录根据此前的学习、SQL 编码练习、错误纠正和复习结果整理。明确区分实际操作、题目验证和原理学习。

---

## 一、数据库基础操作与表结构管理

### 案例 001：数据库连接与基础命令

> [!note] 实践信息
> - **技术**：MySQL CLI、`SHOW`、`USE`、`DESC`
> - **环境**：MySQL 8.0.46
> - **状态**：基础操作已学习，近期完成命令复习
> - **实践重点**：正确区分数据库操作与表结构查看命令

#### 1. 实践目标

能够连接 MySQL，选择数据库，查看数据库中的表及其结构。

#### 2. 核心 SQL

```sql
SHOW DATABASES;

USE school;

SHOW TABLES;

DESC student;

SHOW CREATE TABLE student;
```

#### 3. 遇到的错误

**问题：DESC 命令的语法。**

复习时曾写出：

```sql
DESC TABLE student;
```

正确写法：

```sql
DESC student;
```

也可以使用：

```sql
DESCRIBE student;
```

`DESC` 后面直接指定表名，不需要 `TABLE` 关键字。

#### 4. 验证结果

- 已学习数据库连接与基础管理命令。
- 近期复习中发现并纠正了 `DESC` 语法错误。
- 强化练习中能够正确使用 `DESC student;`。

#### 5. 经验总结

> [!important] 实践结论
> `DESC` 用于查看表结构；`SHOW CREATE TABLE` 用于查看建表定义。两者用途不同，不能混淆。

---

### 案例 002：ALTER TABLE 修改表结构

> [!note] 实践信息
> - **技术**：`ALTER TABLE`、`ADD COLUMN`、`MODIFY COLUMN`、`DROP COLUMN`
> - **状态**：已学习，近期完成纠错与强化
> - **实践重点**：区分表结构修改与数据插入

#### 1. 实践目标

掌握对现有表增加、修改和删除字段的方法。

#### 2. 核心 SQL

增加字段：

```sql
ALTER TABLE student
ADD COLUMN email VARCHAR(100);
```

修改字段：

```sql
ALTER TABLE student
MODIFY COLUMN email VARCHAR(150);
```

删除字段：

```sql
ALTER TABLE student
DROP COLUMN email;
```

#### 3. 遇到的错误

**问题：将增加字段与 INSERT 混淆。**

复习时，面对“给 student 表增加 email 字段”的题目，最初没有想起 `ALTER TABLE`，而是联想到 `INSERT`。

两者的区别：

```sql
-- 修改表结构
ALTER TABLE student
ADD COLUMN email VARCHAR(100);

-- 插入一条数据
INSERT INTO student(name, age)
VALUES ('张三', 20);
```

`ALTER TABLE` 修改表结构。

`INSERT INTO` 向表中插入数据。

#### 4. 验证结果

后续强化题中，已正确写出：

```sql
ALTER TABLE student
ADD COLUMN phone VARCHAR(20);
```

并能够判断 `ALTER TABLE ... DROP COLUMN` 属于 DDL。

#### 5. 经验总结

> [!important] 实践结论
> 判断 SQL 命令时，先区分操作对象：修改表的定义使用 DDL；修改表中的记录使用 DML。

---

### 案例 003：DELETE、TRUNCATE 与 DROP 的区别

> [!note] 实践信息
> - **技术**：`DELETE`、`TRUNCATE TABLE`、`DROP TABLE`
> - **状态**：已学习并完成多轮复习
> - **实践重点**：理解三种删除操作的对象、事务行为和风险

#### 1. 实践目标

掌握删除数据、清空表和删除表结构的区别。

#### 2. 核心 SQL

删除指定记录：

```sql
DELETE FROM student
WHERE id = 5;
```

清空表数据：

```sql
TRUNCATE TABLE student;
```

删除整张表：

```sql
DROP TABLE student;
```

#### 3. 遇到的错误

**问题一：TRUNCATE 的 SQL 分类。**

复习时能够正确写出：

```sql
TRUNCATE TABLE student;
```

但最初将其归类为 DML。

正确分类：

| 操作 | SQL 分类 |
|---|---|
| DELETE | DML |
| TRUNCATE TABLE | DDL |
| DROP TABLE | DDL |

**问题二：事务回滚与 TRUNCATE。**

在 MySQL 中，普通 `DELETE` 可以在有效事务中回滚。

但 `TRUNCATE TABLE` 属于 DDL，会触发隐式提交，不能依靠普通事务的 `ROLLBACK` 撤销。

#### 4. 验证结果

- 已完成三种操作的语法练习。
- 已纠正 TRUNCATE 的分类错误。
- 已理解 DELETE 与事务回滚的关系。
- 已理解 TRUNCATE 与 DROP 的高风险性质。

#### 5. 经验总结

> [!important] 实践结论
> DELETE 删除记录；TRUNCATE 清空表；DROP 删除表对象。生产环境执行前必须确认操作范围，并准备相应的备份与恢复措施。

---

## 二、基础 SQL 与数据查询

### 案例 004：student 表 CRUD 综合实践

> [!note] 实践信息
> - **技术**：`INSERT`、`SELECT`、`UPDATE`、`DELETE`
> - **数据库**：`school`
> - **实践表**：`student`
> - **状态**：已完成基础 CRUD 学习与 SQL 编码练习

#### 1. 实践目标

通过学生表完成数据新增、查询、修改和删除。

#### 2. 实践表结构

此前使用的核心字段：

```text
student
├── id
├── name
├── age
├── gender
├── score
└── class_name
```

其中 `id` 为主键，并使用自增机制。

#### 3. 核心 SQL

新增学生：

```sql
INSERT INTO student
(name, age, gender, score, class_name)
VALUES
('张三', 20, '男', 90, '一班');
```

查询学生：

```sql
SELECT *
FROM student
WHERE score >= 90;
```

更新成绩：

```sql
UPDATE student
SET score = 95
WHERE id = 1;
```

删除指定学生：

```sql
DELETE FROM student
WHERE id = 1;
```

以上 SQL 为所学操作的代表性示例，不表示这些具体数据均有保留的运行日志。

#### 4. 重点问题

执行 UPDATE 和 DELETE 时必须明确 WHERE 条件。

例如：

```sql
UPDATE student
SET score = 100;
```

没有 WHERE 条件时，将尝试更新表中的所有记录。

#### 5. 验证结果

- 已完成基础 CRUD 学习。
- 已完成 WHERE 条件查询练习。
- 已完成数据修改与删除的语法练习。
- 能够理解缺少 WHERE 的风险。

#### 6. 经验总结

> [!important] 实践结论
> CRUD 是 MySQL 开发的基础。真正重要的不只是记住 SQL 语法，还要明确操作范围以及事务是否已经提交。

---

### 案例 005：条件查询、排序、分页与聚合

> [!note] 实践信息
> - **技术**：`WHERE`、`ORDER BY`、`LIMIT`、`GROUP BY`、`HAVING`
> - **状态**：已完成系统学习及练习
> - **实践重点**：根据业务条件筛选、排序与统计数据

#### 1. 实践目标

掌握多条件查询、排序、分页和统计。

#### 2. 核心 SQL

查询成绩在 80 到 100 分之间的学生：

```sql
SELECT *
FROM student
WHERE score BETWEEN 80 AND 100;
```

查询姓张的学生：

```sql
SELECT *
FROM student
WHERE name LIKE '张%';
```

查询成绩最高的前五名：

```sql
SELECT *
FROM student
ORDER BY score DESC, id ASC
LIMIT 5;
```

统计每个班级的平均成绩：

```sql
SELECT
    class_name,
    AVG(score) AS avg_score
FROM student
GROUP BY class_name;
```

筛选平均成绩不低于 85 分的班级：

```sql
SELECT
    class_name,
    AVG(score) AS avg_score
FROM student
GROUP BY class_name
HAVING AVG(score) >= 85;
```

#### 3. 重点理解

`WHERE` 在分组前筛选记录。

`HAVING` 在分组后筛选聚合结果。

```sql
SELECT class_name, AVG(score)
FROM student
WHERE score IS NOT NULL
GROUP BY class_name
HAVING AVG(score) >= 85;
```

#### 4. 验证结果

- 已学习 IN、BETWEEN、LIKE、NULL 等条件。
- 已学习排序与 LIMIT。
- 已学习 COUNT、SUM、AVG、MAX、MIN。
- 已完成 GROUP BY 与 HAVING 相关练习。

#### 5. 经验总结

> [!important] 实践结论
> SQL 查询需要明确筛选、分组、聚合和排序的不同职责。不要把 WHERE 与 HAVING 混为一谈。

---

## 三、多表 JOIN 与子查询

### 案例 006：LEFT JOIN 一对多结果行数验证

> [!note] 实践信息
> - **技术**：`LEFT JOIN`、`INNER JOIN`
> - **状态**：已完成题目验证及纠错
> - **实践重点**：理解 JOIN 结果行数与匹配关系

#### 1. 实践目标

判断一对多关联查询的结果行数。

#### 2. 测试数据

学生表：

| id | name |
|---|---|
| 1 | 张三 |
| 2 | 李四 |
| 3 | 王五 |

成绩表：

| student_id | score |
|---|---|
| 1 | 90 |
| 2 | 80 |
| 2 | 85 |

#### 3. 核心 SQL

```sql
SELECT s.name, r.score
FROM student s
LEFT JOIN score_record r
ON s.id = r.student_id;
```

预期结果：

| name | score |
|---|---|
| 张三 | 90 |
| 李四 | 80 |
| 李四 | 85 |
| 王五 | NULL |

共 4 行。

#### 4. 遇到的错误

最初认为 LEFT JOIN 的结果只有 3 行。

错误原因：

将“保留左表所有记录”理解为“结果行数等于左表行数”。

实际上：

- 张三匹配 1 条。
- 李四匹配 2 条。
- 王五没有匹配，但 LEFT JOIN 保留 1 条 NULL 结果。

因此：

```text
1 + 2 + 1 = 4 行
```

#### 5. 强化验证

INNER JOIN：

```sql
SELECT s.name, r.score
FROM student s
INNER JOIN score_record r
ON s.id = r.student_id;
```

结果为 3 行。

后续强化题中已正确判断。

#### 6. 经验总结

> [!important] 实践结论
> JOIN 结果行数由实际匹配关系决定。一对多关联可能增加结果行数；LEFT JOIN 还会保留未匹配的左表记录。

---

### 案例 007：LEFT JOIN 与 IS NULL 查找未匹配记录

> [!note] 实践信息
> - **技术**：`LEFT JOIN`、`IS NULL`
> - **状态**：已完成强化练习
> - **实践重点**：查找没有关联记录的数据

#### 1. 实践目标

查询没有成绩记录的学生。

#### 2. 核心 SQL

```sql
SELECT s.*
FROM student s
LEFT JOIN score_record r
ON s.id = r.student_id
WHERE r.student_id IS NULL;
```

#### 3. 重点问题

不能使用：

```sql
WHERE r.student_id = NULL;
```

应使用：

```sql
WHERE r.student_id IS NULL;
```

因为 SQL 中的 NULL 表示未知值，普通等号比较不能用于判断是否为 NULL。

#### 4. 验证结果

- 已正确判断 IS NULL 的用法。
- 已完成查找未匹配记录的强化练习。
- 能够解释 LEFT JOIN 保留左表记录的机制。

#### 5. 经验总结

> [!important] 实践结论
> LEFT JOIN 配合右表非空关联键的 IS NULL 判断，可以查找左表中没有匹配记录的数据。

---

### 案例 008：复杂子查询与 EXISTS

> [!note] 实践信息
> - **技术**：子查询、`IN`、`EXISTS`
> - **状态**：已完成相关知识学习与练习
> - **实践重点**：理解子查询与外层查询的关系

#### 1. 实践目标

掌握利用子查询实现条件筛选。

#### 2. 代表性 SQL

查询成绩高于全校平均分的学生：

```sql
SELECT *
FROM student
WHERE score > (
    SELECT AVG(score)
    FROM student
);
```

使用 EXISTS 判断关联记录是否存在：

```sql
SELECT s.*
FROM student s
WHERE EXISTS (
    SELECT 1
    FROM score_record r
    WHERE r.student_id = s.id
);
```

#### 3. 重点理解

- 标量子查询返回单个值。
- IN 可以用于判断值是否属于子查询结果集合。
- EXISTS 判断子查询是否至少返回一条记录。
- 相关子查询可以引用外层查询的字段。

#### 4. 验证结果

已学习复杂子查询及 EXISTS 的相关知识，能够分析典型子查询逻辑。

#### 5. 经验总结

> [!important] 实践结论
> 子查询的核心不是嵌套层数，而是明确内层查询返回什么、外层查询如何使用结果。

---

## 四、窗口函数

### 案例 009：PARTITION BY 班级排名

> [!note] 实践信息
> - **技术**：`ROW_NUMBER()`、`RANK()`、`DENSE_RANK()`
> - **状态**：已完成学习与错题纠正
> - **实践重点**：理解分区、排序与排名的关系

#### 1. 实践目标

根据班级对学生成绩进行排名。

#### 2. 核心 SQL

```sql
SELECT
    id,
    name,
    class_name,
    score,
    RANK() OVER (
        PARTITION BY class_name
        ORDER BY score DESC
    ) AS ranking
FROM student;
```

#### 3. 遇到的理解问题

此前曾混淆：

```sql
PARTITION BY class_name
```

与：

```sql
ORDER BY score DESC
```

正确理解：

- `PARTITION BY class_name`：按照班级划分排名范围。
- `ORDER BY score DESC`：在每个班级内部按照学生自己的成绩降序排名。

这里的 score 不是班级平均分。

#### 4. 三种排名函数

假设成绩为：

```text
95
90
90
85
```

对应结果：

| 成绩 | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|
| 95 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 85 | 4 | 4 | 3 |

#### 5. 验证结果

- 已完成三种排名函数学习。
- 已理解 PARTITION BY 的分组作用。
- 已完成相关错题纠正。

#### 6. 经验总结

> [!important] 实践结论
> PARTITION BY 决定在哪个范围内计算，窗口 ORDER BY 决定范围内的顺序。两者共同决定窗口函数的结果。

---

### 案例 010：GROUP BY 与窗口聚合的行数区别

> [!note] 实践信息
> - **技术**：`GROUP BY`、`AVG() OVER`
> - **状态**：近期复习全部答对
> - **实践重点**：理解聚合查询与窗口计算的不同

#### 1. 实践目标

比较 GROUP BY 与窗口聚合的结果。

#### 2. GROUP BY 查询

```sql
SELECT
    class_name,
    AVG(score) AS avg_score
FROM student
GROUP BY class_name;
```

假设原表有五名学生，分属两个班级。

结果通常为：

```text
2 行
```

#### 3. 窗口函数查询

```sql
SELECT
    name,
    class_name,
    score,
    AVG(score) OVER (
        PARTITION BY class_name
    ) AS class_avg
FROM student;
```

结果为：

```text
5 行
```

#### 4. 验证结果

近期复习中已正确回答：

- GROUP BY：2 行。
- 窗口函数：5 行。

#### 5. 经验总结

> [!important] 实践结论
> GROUP BY 按分组聚合记录；窗口函数通常保留原始记录，同时为每行附加窗口计算结果。

---

## 五、索引与执行计划

### 案例 011：联合索引与最左前缀原则

> [!note] 实践信息
> - **技术**：联合索引、最左前缀原则
> - **状态**：已学习并通过近期强化题
> - **实践重点**：判断查询条件能否利用联合索引

#### 1. 实践目标

理解联合索引中字段顺序对查询的影响。

#### 2. 示例索引

```sql
CREATE INDEX idx_name_age
ON student(name, age);
```

#### 3. 查询分析

查询一：

```sql
SELECT *
FROM student
WHERE name = '张三';
```

符合联合索引的最左前缀。

查询二：

```sql
SELECT *
FROM student
WHERE name = '张三'
  AND age = 20;
```

同样符合最左前缀。

查询三：

```sql
SELECT *
FROM student
WHERE age = 20;
```

缺少最左侧的 name 条件，通常不能像前两种查询那样直接进行高效的联合索引前缀定位。

实际是否使用该索引，需要结合执行计划和优化器判断。

#### 4. 验证结果

近期复习题中，正确选择前两种查询。

#### 5. 经验总结

> [!important] 实践结论
> 联合索引中的字段顺序很重要。设计索引时应结合实际 WHERE、ORDER BY 和查询频率，而不是机械地把所有字段放进索引。

---

### 案例 012：聚簇索引、二级索引与覆盖索引

> [!note] 实践信息
> - **技术**：B+Tree、聚簇索引、二级索引、覆盖索引
> - **状态**：已学习核心原理
> - **实践重点**：理解回表的原因

#### 1. 实践目标

理解 InnoDB 不同索引的存储内容。

#### 2. 核心机制

聚簇索引：

```text
主键索引
    ↓
B+Tree
    ↓
叶子节点存储完整行记录
```

二级索引：

```text
二级索引
    ↓
B+Tree
    ↓
叶子节点保存索引字段与主键值
```

需要其他字段时：

```text
二级索引
    ↓
取得主键
    ↓
查询聚簇索引
    ↓
取得完整记录
```

这个过程称为回表。

#### 3. 覆盖索引示例

```sql
CREATE INDEX idx_name_age
ON student(name, age);
```

```sql
SELECT name, age
FROM student
WHERE name = '张三';
```

查询所需字段都包含在索引中，具备覆盖索引条件。

#### 4. 验证结果

- 已学习聚簇索引和二级索引。
- 已理解回表机制。
- 已学习覆盖索引。
- 近期复习中能够正确判断二级索引叶子节点保存的主要信息。

#### 5. 经验总结

> [!important] 实践结论
> 索引不仅影响 WHERE 查询速度，还可能影响是否回表、排序、分组和读取的数据量。

---

### 案例 013：EXPLAIN 与 Using filesort

> [!note] 实践信息
> - **技术**：`EXPLAIN`、`type`、`key`、`rows`、`Extra`
> - **状态**：已学习核心字段，近期完成概念复习
> - **实践重点**：避免对执行计划字段产生错误理解

#### 1. 实践目标

掌握 MySQL 查询执行计划的基础分析方法。

#### 2. 核心 SQL

```sql
EXPLAIN
SELECT *
FROM student
WHERE score >= 90
ORDER BY score DESC;
```

#### 3. 重点字段

| 字段 | 作用 |
|---|---|
| type | 表访问方式 |
| possible_keys | 可能使用的索引 |
| key | 实际选择的索引 |
| key_len | 使用的索引键长度 |
| rows | 估计扫描行数 |
| Extra | 附加执行信息 |

#### 4. 重点问题

`Using filesort` 是否表示一定使用磁盘文件排序？

**不是。**

`Using filesort` 表示 MySQL 使用了额外排序操作，而不是直接依靠可用索引顺序获得结果。

排序可能在内存中完成，也可能涉及磁盘临时文件。

#### 5. 验证结果

近期复习中已正确理解：

```text
Using filesort ≠ 一定发生磁盘排序
```

#### 6. 经验总结

> [!important] 实践结论
> EXPLAIN 是性能分析的起点，但不能仅凭某个 Extra 标记就断言 SQL 一定慢。还需要结合数据量、实际执行时间和执行计划整体判断。

---

## 六、事务与回滚

### 案例 014：START TRANSACTION、UPDATE 与 ROLLBACK

> [!note] 实践信息
> - **技术**：事务、`COMMIT`、`ROLLBACK`
> - **状态**：已完成原理学习与多轮场景题纠错
> - **实践重点**：理解 SQL 执行、事务提交与回滚的区别

#### 1. 实践目标

理解事务中的数据修改何时真正提交，以及 ROLLBACK 的作用。

#### 2. 核心 SQL

```sql
START TRANSACTION;

UPDATE student
SET score = 90
WHERE id = 1;

ROLLBACK;
```

#### 3. 遇到的理解问题

此前曾将 ROLLBACK 理解为：

```text
SQL 没有执行
```

正确理解：

```text
UPDATE 已经执行
    ↓
事务尚未提交
    ↓
执行 ROLLBACK
    ↓
撤销当前事务中的修改
```

ROLLBACK 不等于 SQL 没有执行过。

#### 4. 对比 COMMIT

```sql
START TRANSACTION;

UPDATE student
SET score = 90
WHERE id = 1;

COMMIT;
```

COMMIT 表示提交事务。

提交后，普通 ROLLBACK 不能再撤销该次已经提交的修改。

#### 5. 验证结果

- 已完成事务提交与回滚的学习。
- 已纠正“回滚等于未执行”的错误理解。
- 已掌握 UPDATE 执行与事务提交的区别。

#### 6. 经验总结

> [!important] 实践结论
> 事务中的 SQL 可以已经执行，但修改尚未提交。ROLLBACK 撤销的是事务中的修改，而不是让已经执行过的 SQL 从未发生。

---

### 案例 015：AUTO_INCREMENT 与事务回滚

> [!note] 实践信息
> - **技术**：`AUTO_INCREMENT`、事务回滚
> - **状态**：已学习相关原理
> - **实践重点**：理解自增主键不保证连续

#### 1. 实践目标

理解事务回滚与自增 ID 的关系。

#### 2. 示例 SQL

```sql
START TRANSACTION;

INSERT INTO student
(name, age, gender, score, class_name)
VALUES
('测试学生', 20, '男', 80, '测试班');

ROLLBACK;
```

#### 3. 重点问题

虽然插入操作被回滚，但已经分配的自增值通常不会因为回滚而重新使用。

因此：

```text
AUTO_INCREMENT 保证自动生成值
不保证主键连续
```

#### 4. 验证情况

已学习并讨论自增主键与事务回滚的关系；此处没有保留可引用的具体数据库输出。

#### 5. 经验总结

> [!important] 实践结论
> 不应依赖 AUTO_INCREMENT 的连续性实现业务编号。主键可能因为回滚、删除或其他数据库行为出现间隔。

---

## 七、MVCC 与事务可见性

### 案例 016：REPEATABLE READ 下的快照读

> [!note] 实践信息
> - **技术**：`REPEATABLE READ`、Read View、Undo Log
> - **状态**：已完成并发场景分析题
> - **实践重点**：理解普通 SELECT 的快照可见性

#### 1. 实践目标

分析两个事务交替执行时，普通 SELECT 的读取结果。

#### 2. 并发场景

初始数据：

```text
id = 1
score = 80
```

事务 A：

```sql
START TRANSACTION;

SELECT score
FROM student
WHERE id = 1;
```

读取：

```text
80
```

事务 B：

```sql
START TRANSACTION;

UPDATE student
SET score = 90
WHERE id = 1;

COMMIT;
```

事务 A 再次执行普通查询：

```sql
SELECT score
FROM student
WHERE id = 1;
```

在所讨论的 InnoDB REPEATABLE READ 快照读场景中，预期仍读取：

```text
80
```

#### 3. 原理分析

事务 A 已建立一致性读快照。

事务 B 虽然提交了新版本，但事务 A 的后续普通快照读仍根据既有 Read View 判断版本可见性。

核心机制：

```text
Read View
    ↓
判断版本是否可见
    ↓
Undo Log 版本链
    ↓
取得可见的历史版本
```

#### 4. 验证结果

此前强化题中正确回答：

- 第二次普通 SELECT 读取 80。
- Read View 决定版本可见性。
- Undo Log 提供历史版本。

#### 5. 经验总结

> [!important] 实践结论
> Read View 负责判断哪些版本可见，Undo Log 支持读取历史版本。两者共同支撑 InnoDB 的 MVCC 一致性读。

---

### 案例 017：SELECT FOR UPDATE 当前读

> [!note] 实践信息
> - **技术**：`SELECT ... FOR UPDATE`
> - **状态**：近期强化题回答正确
> - **实践重点**：理解快照读与当前读的区别

#### 1. 实践目标

理解为什么同一事务中的普通 SELECT 与 SELECT FOR UPDATE 可能读到不同结果。

#### 2. 并发场景

事务 A 已通过普通快照读读取：

```text
score = 80
```

事务 B 将成绩更新为：

```text
score = 90
```

并提交。

事务 A 执行：

```sql
SELECT score
FROM student
WHERE id = 1
FOR UPDATE;
```

在没有其他冲突锁、记录未发生其他修改的前提下，预期读取：

```text
90
```

#### 3. 原理分析

普通 SELECT：

```text
快照读
    ↓
按照 Read View 判断版本
```

SELECT FOR UPDATE：

```text
当前读
    ↓
读取当前可用的记录版本
    ↓
对相关记录加锁
```

#### 4. 实际答题记录

此前回答：

> 选择：90  
> 理由：SELECT ... FOR UPDATE 是当前读，会读取当前可用的最新版本，并对相关记录加锁。

该回答正确。

#### 5. 注意事项

当前读并不意味着永远立即返回。

如果存在冲突锁，可能需要等待。

此外，实际加锁范围受到索引、查询条件和隔离级别等因素影响。

#### 6. 经验总结

> [!important] 实践结论
> 快照读强调一致性视图，当前读强调读取当前记录状态并参与加锁。二者属于不同的读取机制。

---

## 八、数据库设计与表关系

### 案例 018：主外键与一对多、多对多建模

> [!note] 实践信息
> - **技术**：主键、外键、中间表、数据库范式
> - **状态**：已学习数据库设计核心内容
> - **实践重点**：根据业务关系确定表结构

#### 1. 实践目标

理解不同实体关系在关系型数据库中的表达方式。

#### 2. 一对多关系

例如：

```text
班级
  ↓
学生
```

一个班级可以对应多个学生。

#### 3. 多对多关系

例如：

```text
学生
  ↓
选课记录
  ↑
课程
```

通常需要通过中间表表达。

示例：

```sql
CREATE TABLE enrollment (
    student_id BIGINT NOT NULL,
    course_id BIGINT NOT NULL,
    PRIMARY KEY (student_id, course_id)
);
```

#### 4. 重点理解

- 主键用于标识记录。
- 外键用于建立并约束表之间的引用关系。
- 一对多通常在多的一方保存关联字段。
- 多对多通常需要中间表。
- 范式用于减少不必要的数据冗余与更新异常。

#### 5. 验证结果

此前已学习：

- 一对一关系。
- 一对多关系。
- 多对多关系。
- 中间表设计。
- 三范式。
- 基础业务表设计。

#### 6. 经验总结

> [!important] 实践结论
> 数据库设计应先明确业务实体和实体关系，再决定表结构、主外键和索引，而不是先写 CREATE TABLE 再考虑业务关系。

---

## 九、已学习但尚需独立实操验证的内容

以下内容不标记为已完成实践。

### 案例 019：双会话锁等待与死锁实验

> [!note] 实践信息
> - **技术**：行锁、Gap Lock、Next-Key Lock、死锁
> - **状态**：待实践
> - **实践重点**：验证锁等待、加锁范围与死锁机制

#### 1. 计划目标

使用两个 MySQL 会话，分别模拟：

- 行锁等待。
- 共享锁与排他锁冲突。
- 不同索引条件下的加锁范围。
- 两个事务互相等待形成死锁。

#### 2. 计划验证

- [ ] 创建专用测试表。
- [ ] 使用两个会话开启事务。
- [ ] 验证 UPDATE 的锁等待。
- [ ] 验证 SELECT FOR UPDATE 的行为。
- [ ] 复现死锁。
- [ ] 查看 InnoDB 死锁诊断信息。

#### 3. 当前状态

尚无可确认的完整实操结果。

---

### 案例 020：索引优化与执行计划对比

> [!note] 实践信息
> - **技术**：`CREATE INDEX`、`EXPLAIN ANALYZE`
> - **状态**：待综合实践
> - **实践重点**：通过真实数据验证索引效果

#### 1. 计划目标

比较相同 SQL 在建立索引前后的执行计划和性能表现。

#### 2. 计划步骤

1. 准备具有一定数据量的测试表。
2. 执行原始 SQL。
3. 记录执行计划。
4. 建立适当索引。
5. 再次执行相同 SQL。
6. 比较实际执行时间、扫描行数及访问方式。

#### 3. 验收要求

- [ ] 保存优化前 EXPLAIN。
- [ ] 保存优化后 EXPLAIN。
- [ ] 记录索引定义。
- [ ] 分析优化器是否选择索引。
- [ ] 解释优化效果与可能的代价。

#### 4. 当前状态

索引理论和 EXPLAIN 核心字段已学习，但尚缺少可确认的完整性能对比记录。

---

### 案例 021：InnoDB 日志与持久化机制

> [!note] 实践信息
> - **技术**：Redo Log、Undo Log、Binlog、Buffer Pool
> - **状态**：待系统实践与深化
> - **实践重点**：理解事务提交、数据落盘和恢复

#### 1. 计划目标

建立一次 UPDATE 操作的完整执行链路。

```text
执行 UPDATE
    ↓
生成 Undo 信息
    ↓
修改 Buffer Pool 中的数据页
    ↓
记录 Redo Log
    ↓
提交事务
    ↓
后台刷脏页
```

上述为简化的概念流程，不代表所有内部操作严格按此单线顺序发生。

#### 2. 计划内容

- [ ] 理解 Buffer Pool。
- [ ] 理解 Redo Log。
- [ ] 深化 Undo Log。
- [ ] 理解 Binlog。
- [ ] 理解两阶段提交。
- [ ] 理解崩溃恢复。

#### 3. 当前状态

Undo Log 与 MVCC 的关系已学习；完整日志协作和恢复机制尚待深入。

---
