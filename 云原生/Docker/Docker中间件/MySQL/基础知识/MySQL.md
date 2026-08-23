# MySQL 架构师进阶手册

## 第一篇 MySQL 基础认知

### 1. MySQL 整体架构

#### 1.1 Server 层与存储引擎层

MySQL 分为 **Server 层** 和 **存储引擎层**：

- **Server 层**：连接器、分析器、优化器、执行器，以及内置函数（日期、数学、加密等），所有跨存储引擎的功能都在这一层实现。
- **存储引擎层**：负责数据的存储和提取，采用插件式架构，常见的有 InnoDB、MyISAM、Memory 等。InnoDB 从 MySQL 5.5.5 开始成为默认存储引擎。

#### 1.2 InnoDB 架构全景

```
+---------------------+
|   MySQL Server 层   |
| 连接器/分析器/优化器/执行器 |
+----------+----------+
           |
+----------v----------+
|   InnoDB 存储引擎层  |
| Buffer Pool / Change Buffer / AHI |
| Redo Log / Undo Log / Binlog |
| 表空间 / 页 / 区 / 段 |
+---------------------+
```

**核心组件**：

- **Buffer Pool**：缓存数据页和索引页，减少磁盘 IO。
- **Change Buffer**：针对非唯一二级索引的写缓冲。
- **Adaptive Hash Index (AHI)**：自动建立的热点哈希索引。
- **Redo Log**：物理日志，保证持久性。
- **Undo Log**：逻辑日志，用于回滚和 MVCC。
- **Binlog**：Server 层逻辑日志，用于主从复制和数据恢复。

#### 1.3 SQL 执行流程

执行一条更新语句的完整流程：

1. 连接器建立连接，校验权限。
2. 分析器进行词法、语法分析。
3. 优化器选择索引、生成执行计划。
4. 执行器调用 InnoDB 接口：
   - 写 Undo Log（记录旧值）
   - 修改内存页（Buffer Pool）
   - 写 Redo Log（prepare 阶段）
   - 写 Binlog
   - 提交事务，Redo Log 标记 commit（两阶段提交）

### 2. SQL 基础

#### 2.1 常用数据类型选择原则

##### INT vs BIGINT

| 类型 | 字节数 | 有符号范围 | 适用场景 |
|------|--------|------------|----------|
| `INT` | 4 | -2,147,483,648 ~ 2,147,483,647 | 用户量、普通状态、数量 |
| `BIGINT` | 8 | -9,223,372,036,854,775,808 ~ 9,223,372,036,854,775,807 | 流水号、大额订单、雪花 ID |

**核心结论**  
- 能用 `INT` 不用 `BIGINT`：主键变大会放大二级索引空间、Buffer Pool 占用和磁盘 IO。  
- 业务增长不确定时，主键、订单号、金额累计等建议直接 `BIGINT`。

##### VARCHAR vs CHAR

| 类型 | 存储 | 特点 | 适用 |
|------|------|------|------|
| `VARCHAR(n)` | 变长，长度前缀 1~2 字节 | 省空间，更新可能引起页分裂 | 姓名、地址、可变长文本 |
| `CHAR(n)` | 定长，补空格存储 | 查询效率略高，空间固定 | 手机号、MD5、枚举码等固定长度 |

**避坑**  
- `VARCHAR(255)` 别随便用：不代表省空间，只是最大长度，实际按使用长度存储。  
- 索引前缀长度受限制，长字段建立索引需配合前缀索引。

##### DATETIME vs TIMESTAMP

| 类型 | 字节 | 范围 | 时区 | 特点 |
|------|------|------|------|------|
| `DATETIME` | 8 | 1000-01-01 ~ 9999-12-31 | 不受时区影响 | 存储字面时间 |
| `TIMESTAMP` | 4 | 1970-01-01 00:00:01 UTC ~ 2038-01-19 | 受 `time_zone` 影响 | 自动初始化和更新 |

**生产建议**  
- 业务时间跨时区时，推荐 `DATETIME` 存 UTC 或 `BIGINT` 存毫秒时间戳，由应用层转换。  
- 避免依赖 `TIMESTAMP` 的自动更新，隐式行为容易在 ORM 中产生脏数据。

##### DECIMAL 精确计算

```sql
-- 创建订单表，金额字段使用 DECIMAL 类型
CREATE TABLE `order` (
  id BIGINT PRIMARY KEY,
  amount DECIMAL(10,2) NOT NULL COMMENT '金额，最多8位整数，2位小数'
);

-- 浮点数运算存在精度误差，禁止用 FLOAT/DOUBLE 存金额
SELECT 0.1 + 0.2; -- 0.30000000000000004
```

`DECIMAL(M,D)` 内部使用**二进制编码的十进制定点数（Binary-Coded Decimal）**存储，本质是十进制存储，避免 `FLOAT/DOUBLE` 的二进制浮点误差。每 9 位十进制数约占用 4 字节。

#### 2.2 建表规范：三范式 vs 反范式

##### 三范式（3NF）

- **1NF**：列不可再分，保证原子性。  
- **2NF**：消除非主属性对主键的部分依赖。  
- **3NF**：消除非主属性对主键的传递依赖。

**示例**  
```
用户表（用户ID，姓名）  
订单表（订单ID，用户ID，金额）  
地址表（地址ID，用户ID，省市区）
```

##### 反范式设计（空间换时间）

互联网高并发场景经常**故意冗余**，减少 JOIN：

```sql
-- 订单表冗余用户昵称，避免查询订单列表时 JOIN 用户表
CREATE TABLE `order` (
  id BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  user_nickname VARCHAR(64) DEFAULT '' COMMENT '冗余用户昵称',
  amount DECIMAL(10,2)
);
```

**权衡**  
- 三范式：数据一致性高，写入简单，但多表关联查询性能差。  
- 反范式：查询快，但数据冗余，更新需维护一致性。

**怎么选择？**  
核心查询频繁且 JOIN 过多的字段（如订单列表展示用户昵称、商品标题），适合冗余；非核心或变化频繁的字段建议保留关联。

##### 主键选择原则：自增 ID vs 雪花算法 Snowflake

| 方案 | 优点 | 缺点 | 适用 |
|------|------|------|------|
| 自增 ID | 有序、紧凑、插入性能高 | 单机局限，分布式冲突 | 单库或通过号段分配 |
| 雪花算法 | 全局唯一，趋势递增 | 长整型，依赖机器时钟 | 分布式、分库分表 |

**B+ 树视角**  
自增主键顺序插入，叶子页单向追加，页分裂最少；随机主键（如 UUID）会导致大量页分裂、空间碎片、Buffer Pool 污染。

**Java 实现雪花 ID 注意事项**  
- 时钟回拨需处理，可使用 `Leaf`、`UidGenerator` 或数据库号段方案。  
- 若分库分表，主键必须是全局唯一，单纯自增不够。

#### 2.3 核心 SQL 与高效查询

##### DML / DDL 基础

```sql
-- 创建用户表，使用 utf8mb4 字符集
CREATE TABLE user (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  mobile CHAR(11) NOT NULL DEFAULT '' COMMENT '手机号',
  nickname VARCHAR(64) NOT NULL DEFAULT '' COMMENT '昵称',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_mobile (mobile)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- 插入或更新（存在则更新昵称）
INSERT INTO user(mobile, nickname) VALUES ('13800000000', 'Tom')
  ON DUPLICATE KEY UPDATE nickname = VALUES(nickname);

-- 更新操作必须加 LIMIT 防止误更新全表
UPDATE user SET nickname = 'Jerry' WHERE id = 1 LIMIT 1;

-- 删除操作同样加 LIMIT
DELETE FROM user WHERE id = 1 LIMIT 1;
```

**避坑**  
- 生产环境删除/更新必须带 `LIMIT`，防止误更新全表。  
- 字符集建议 `utf8mb4`，排序规则用 `utf8mb4_bin` 或 `utf8mb4_general_ci`，避免表情乱码。

##### 聚合函数与 GROUP BY 深度理解

**SQL 逻辑执行顺序**  
```
FROM → ON → JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

```sql
-- 统计每个用户的订单总额，过滤总额大于1000的
SELECT user_id, SUM(amount) AS total_amount
FROM `order`
WHERE status = 'PAID'
GROUP BY user_id
HAVING SUM(amount) > 1000
ORDER BY total_amount DESC
LIMIT 10;
```

**底层机制**  
- `GROUP BY` 没有合适索引时，MySQL 会创建临时表（`Using temporary`）并排序（`Using filesort`）。  
- 如果 `GROUP BY` 字段命中索引，且顺序与索引一致，可能避免临时表。  
- `ONLY_FULL_GROUP_BY` 模式下，`SELECT` 中的非聚合列必须出现在 `GROUP BY` 中。

**优化 GROUP BY**：建立 `(user_id, status, amount)` 联合索引，让分组和聚合走索引覆盖。

##### 多表 JOIN 执行机制与驱动表选择

**连接类型**  
- `INNER JOIN`：优化器可选择驱动表，通常选过滤后行数少的作为驱动表。  
- `LEFT JOIN`：左表强制为驱动表，右表为被驱动表。  
- `RIGHT JOIN`：右表为驱动表（建议改写为 LEFT JOIN）。

**Nested-Loop Join（NLJ）**  
```
for each row in 驱动表:
    for each row in 被驱动表 where 驱动表.关联键 = 被驱动表.索引键:
        输出
```
被驱动表的关联键必须有索引，否则全表扫描。

```sql
-- 查询订单及用户昵称，LEFT JOIN 左表为驱动表
SELECT o.id, u.nickname
FROM `order` o
LEFT JOIN `user` u ON o.user_id = u.id
WHERE o.status = 'PAID';
-- 驱动表：o（左表），被驱动表：u，需在 u.id 有索引（主键索引即可）
```

`EXPLAIN` 中 `rows` 小的通常是驱动表；`Using join buffer` 表示被驱动表无可用索引（需要优化）。MySQL 8.0 对连接算法进行过重构，目前仍以 Nested-Loop Join 为主，Hash Join 在特定场景下使用，不必深入展开。

#### 2.4 SQL 避坑指南与高频问题

**避坑指南**  
1. 不用 `SELECT *`，只取需要的列，利用覆盖索引。  
2. `VARCHAR` 长度不是越大越好，索引长度受 `max_index_key_length` 限制。  
3. 金额计算用 `DECIMAL`，禁止浮点。  
4. 分布式环境不要依赖自增主键，分库分表优先雪花或号段。  
5. JOIN 前先过滤，尽量用小结果集做驱动表。

**高频问题**  

**Q1：为什么建议自增 ID 而不是 UUID 作为主键？**  
自增 ID 有序，B+ 树叶子页顺序写入，页分裂少，索引紧凑，Buffer Pool 效率高；UUID 随机导致大量页分裂、空间碎片和缓存命中率下降。

**Q2：GROUP BY 产生临时表怎么排查？**  
`EXPLAIN` 中 `Extra` 出现 `Using temporary`；优化方向：为 `GROUP BY` + `ORDER BY` 字段建立联合索引，或改写为物化视图/汇总表。

**Q3：LEFT JOIN 时右表过滤条件写在哪？**  
如果过滤右表且希望不丢失左表行，条件写在 `ON` 后；如果过滤结果集，写在 `WHERE` 后。写错会导致语义变化。

#### 2.5 MySQL 8.0 新特性（SQL 相关）

##### 窗口函数

常用窗口函数：`ROW_NUMBER()`、`RANK()`、`DENSE_RANK()`、`SUM() OVER()`、`LAG()`、`LEAD()`。

```sql
-- 按部门分组，按工资降序排名，同时计算部门总工资
SELECT emp_name, dept_id, salary,
       ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn,
       RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rk,
       SUM(salary) OVER (PARTITION BY dept_id) AS dept_total
FROM employee;
```

窗口函数不减少行数，而是在每行上计算聚合值，`PARTITION BY` 分组，`ORDER BY` 排序，常用于排名、累计、移动平均。

##### CTE（公用表表达式）

```sql
-- 递归 CTE：生成 1~10 序列
WITH RECURSIVE seq(n) AS (
  SELECT 1
  UNION ALL
  SELECT n+1 FROM seq WHERE n < 10
)
SELECT * FROM seq;
```

**作用**：简化复杂 SQL，递归处理树形结构（如组织架构、评论回复）。

##### 原子 DDL 与即时加列

- **原子 DDL**：DDL 操作要么全部成功，要么全部回滚，避免中途失败导致表损坏。
- **即时加列**：`ALTER TABLE t ADD COLUMN c INT, ALGORITHM=INSTANT;` 只修改元数据，秒级完成。

##### Clone 插件

```sql
-- 安装 clone 插件
INSTALL PLUGIN clone SONAME 'mysql_clone.so';
-- 克隆本地实例
CLONE LOCAL DATA DIRECTORY = '/backup/clone';
-- 远程克隆（从库搭建）
CLONE INSTANCE FROM 'user'@'host':3306 IDENTIFIED BY 'password';
```

**定位**：Clone 插件适合快速实例克隆和搭建从库，物理备份方面 xtrabackup 仍是生产环境主流工具，两者定位不同。

### 3. 存储引擎

#### 3.1 MyISAM vs InnoDB

| 特性 | MyISAM | InnoDB |
|------|--------|--------|
| 事务支持 | 不支持 | 支持 ACID |
| 锁粒度 | 表锁 | 行锁 + 间隙锁 |
| 外键 | 不支持 | 支持（但互联网常用应用层保证） |
| 崩溃恢复 | 较差（易损坏） | 通过 Redo Log 快速恢复 |
| 索引结构 | B+树，索引文件与数据文件分离 | 聚簇索引，数据即索引 |
| 全文索引 | 支持（较早） | MySQL 5.6+ 支持 |
| 适用场景 | 读多写少、日志表、临时表 | 绝大多数业务表，尤其高并发写 |

#### 3.2 InnoDB 成为默认引擎的原因

- **事务支持**：符合现代应用高一致性要求。  
- **行级锁**：并发写性能远高于 MyISAM 的表锁。  
- **崩溃恢复**：WAL + Redo Log 保证数据不丢。  
- **MVCC**：读写不阻塞，高并发读性能好。  
- **热备份**：支持在线备份（xtrabackup）。  
- **数据缓存**：Buffer Pool 缓存数据页和索引页，IO 效率高。

#### 3.3 其他存储引擎简介

- **Memory**：数据存内存，速度快，重启丢失，适合临时表。  
- **CSV**：CSV 文件存储，便于数据交换。  
- **Archive**：压缩存储，适合归档，只支持 INSERT/SELECT。  
- **NDB**：分布式，适合数据仓库。

---

## 第二篇 SQL 与索引体系

### 4. 索引基础

#### 4.1 索引作用与数据结构选择

索引的作用：加速数据检索，类似于书的目录。

选择 B+ 树而非其他数据结构的原因：

| 数据结构 | 缺点 |
|----------|------|
| Hash | 不支持范围查询、排序、最左前缀匹配；哈希碰撞处理复杂 |
| 红黑树 | 二叉，树高过高，IO 次数多 |
| B 树 | 非叶子节点存储数据，导致每页存储索引条目减少，树高变高 |
| B+ 树 | 数据只存叶子节点，非叶子节点只存键+指针，扇出大，树高低；叶子节点双向链表，适合范围查询 |

**B+ 树优点**  
- 磁盘 IO 次数少  
- 范围查询效率高（叶子节点有序链表）  
- 查询稳定性好（任何查询最终到叶子节点）

#### 4.2 B+ 树索引结构

**假设**  
- 页大小 16KB  
- 主键 BIGINT 8 字节 + 指针 6 字节 ≈ 14 字节  
- 每页可存非叶子索引条目：`16 * 1024 / 14 ≈ 1170`  
- 每行数据 1KB，叶子页约存 16 行

**高度与容量估算**  
- 高度 1：16 行  
- 高度 2：1170 * 16 ≈ 1.8 万行  
- 高度 3：1170² * 16 ≈ 2190 万行  
- 高度 4：1170³ * 16 ≈ 256 亿行

**注意**：以上计算是理想化估算，实际 InnoDB 页内还有页头、记录头、Infimum/Supremum、空闲空间和 MVCC 隐藏列等开销，实际行数会减少。**架构师面试建议表述**：  
> InnoDB 中百万级、千万级数据通常 B+ 树高度为 3~4 层，具体高度受行大小、索引键长度影响。高度每增加一层，查询多一次磁盘 IO，因此保持索引紧凑至关重要。

#### 4.3 聚簇索引与非聚簇索引

**聚簇索引（Clustered Index）**  
- 表数据按主键顺序存储，主键索引的叶子节点就是完整行记录。  
- 一张表只能有一个聚簇索引。

**二级索引 / 非聚簇索引**  
- 二级索引叶子节点存储索引列 + 主键值。  
- 查询时如果索引不包含所需字段，需要回表：  
  ```
  二级索引 → 拿到主键 ID → 回表到聚簇索引 → 取完整行
  ```

```sql
-- 创建手机号索引
CREATE INDEX idx_mobile ON user(mobile);
-- 查询所有列，需要回表
SELECT * FROM user WHERE mobile = '13800000000';
```

**避免回表**：使用覆盖索引（Covering Index），让查询列都包含在索引中。

#### 4.4 联合索引

联合索引 `(a, b, c)` 会建立 `a` → `a,b` → `a,b,c` 三层索引。  
以下查询能命中索引：
```sql
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3
```
以下不能完全命中：
```sql
WHERE b = 2            -- 缺少 a
WHERE a = 1 AND c = 3  -- 中间断 b
```
**原理**：B+ 树按 (a,b,c) 排序，只有最左前缀有序。

### 5. 索引高级原理

#### 5.1 最左前缀匹配原则

（见 4.4，不再重复）

#### 5.2 覆盖索引

```sql
-- 建立联合索引，查询列都在索引中，无需回表
CREATE INDEX idx_user_status ON `order`(user_id, status, amount);
SELECT user_id, status, amount FROM `order` WHERE user_id = 100;
-- Extra: Using index，无需回表
```

#### 5.3 索引下推 ICP（Index Condition Pushdown）

MySQL 5.6+ 支持，在存储引擎层对索引中的字段先做过滤，减少回表次数。

```sql
-- 联合索引 (a, b)
SELECT * FROM t WHERE a > 10 AND b = 5;
-- 没有 ICP：按 a>10 返回所有行再回表过滤 b=5
-- 有 ICP：在索引层先判断 b=5，满足的才回表
```

`EXPLAIN` 中 `Extra` 显示 `Using index condition`。

#### 5.4 回表机制

（见 4.3）

#### 5.5 前缀索引与索引选择

长字符串列建立索引时可只取前 N 个字符：
```sql
-- 为文章标题建立前缀索引，减少索引大小
CREATE INDEX idx_title ON article(title(20));
```
**缺点**：不支持范围查询和排序，精度会下降。

**索引选择原则**：
- 不要在区分度低的字段建索引（如性别、状态）。  
- 联合索引注意顺序：区分度高、等值查询、范围查询字段依次靠前。  
- 避免在小表上建索引，优化器可能不会使用。  
- 索引不是越多越好，写操作会维护所有索引。

#### 5.6 MySQL 8.0 索引新特性

##### 降序索引

```sql
-- 创建降序索引（8.0 支持）
CREATE INDEX idx_a_desc_b ON t (a DESC, b ASC);
```

可用于优化 `ORDER BY a DESC, b ASC` 的查询。

##### 不可见索引

```sql
-- 创建不可见索引，优化器默认不使用
CREATE INDEX idx_name ON user(name) INVISIBLE;
-- 测试时可临时启用
SET SESSION optimizer_switch = 'use_invisible_indexes=on';
```

**作用**：安全地测试删除索引的影响，避免直接 DROP。

##### 函数索引

```sql
-- 对表达式建立索引，例如对日期函数结果建索引
CREATE INDEX idx_day ON orders ((DATE(create_time)));
-- 查询时使用相同表达式才能命中
SELECT * FROM orders WHERE DATE(create_time) = '2024-01-01';
```

#### 5.7 SQL 高级技巧

##### 索引合并（Index Merge）

MySQL 优化器可能同时使用多个索引，然后对结果取交集或并集。

```sql
-- 假设 name 和 age 都有索引，但无联合索引
SELECT * FROM t WHERE name = 'Tom' OR age = 30;
-- 优化器可能使用 index_merge（union）
```

`EXPLAIN` 中 type 为 `index_merge`，Extra 显示 `Using union(idx_name,idx_age)`。

##### MRR 与 Batched Key Access

- **MRR（Multi-Range Read）**：将二级索引回表的随机 IO 转换为顺序 IO。
- **BKA（Batched Key Access）**：结合 MRR 和 join buffer，优化 JOIN 回表。

启用参数：
```sql
SET optimizer_switch = 'mrr=on,mrr_cost_based=off,batched_key_access=on';
```

##### 索引跳跃扫描（Index Skip Scan）

MySQL 8.0 引入，当联合索引 `(a,b)` 查询只涉及 `b` 时，若 `a` 区分度低，优化器可跳过 `a` 扫描。

```sql
-- 假设 (gender, age) 联合索引，gender 只有 M/F，查询 age=20
-- 优化器可能使用 index skip scan
EXPLAIN SELECT * FROM user WHERE age = 20;
-- type: range, Extra: Using index for skip scan
```

##### 子查询优化

- 半连接优化：`IN` 子查询可能转为 semi-join，提升性能。
- 物化：将子查询结果存入临时表，加速重复访问。
- `EXISTS` vs `IN`：MySQL 8.0 优化器能自动转换，一般无需手动改写。

### 6. 索引失效场景

#### 6.1 函数操作、运算、隐式转换

| 场景 | 示例 | 对策 |
|------|------|------|
| 1. LIKE 前置百分号 | `LIKE '%abc'` | 反转字段或使用全文索引/ES |
| 2. 隐式类型转换 | `WHERE phone = 13800000000`（phone 为 varchar） | 改 `phone = '13800000000'` |
| 3. 对索引列使用函数 | `WHERE DATE(created_at) = '2024-01-01'` | 改用范围查询 |
| 4. 对索引列做运算 | `WHERE id + 1 = 100` | 改为 `WHERE id = 99` |
| 5. 违反最左前缀 | 联合索引 `(a,b)` 只查 `b` | 调整索引顺序或补全条件 |
| 6. OR 连接非索引列 | `WHERE a = 1 OR b = 2`（b 无索引） | 联合索引或 UNION |
| 7. NOT IN / <> | `WHERE status <> 1` | 范围拆分或覆盖索引 |
| 8. 索引列使用 IS NULL / IS NOT NULL | 视优化器而定 | 覆盖索引或默认值 |
| 9. 字符集不一致 JOIN | 关联列 utf8mb4 vs utf8 | 统一字符集 |
| 10. 优化器选择错误 | 数据分布不均，走全表扫描更快 | 强制索引/修改统计信息 |

#### 6.2 LIKE 前置百分号、OR 查询

- `LIKE '%abc'` 无法使用索引，因为 B+ 树从左到右匹配。  
- `OR` 连接不同列，如果任一列没有索引，则整句无法使用索引；可改写为 UNION 或建立联合索引。

#### 6.3 数据分布问题与优化器选择

**为什么明明有索引，MySQL 还是走全表扫描？**  
1. **统计信息错误**：表数据变化后未及时更新，优化器低估/高估行数。  
2. **回表成本过高**：二级索引过滤性差，需要回表大量行，优化器认为全表扫描更优。  
3. **选择性不足**：索引列区分度低（如 status 只有两个值），过滤后仍很多行。  
4. **成本模型判断全表更优**：全表扫描是顺序 IO，回表是随机 IO，当回表行数超过一定比例（通常 20%~30%），优化器倾向全表扫描。  
5. **参数影响**：如 `eq_range_index_dive_limit` 影响范围估算，可能导致选择偏差。

#### 6.4 索引失效避坑与优化策略

- 定期使用 `ANALYZE TABLE` 更新统计信息，或对倾斜列创建直方图。  
- 对索引列不做任何函数/运算，保持“裸列”比较。  
- 优化器选择错误时，可用 `FORCE INDEX` 临时干预，但需评估。  
- 通过 `EXPLAIN` 验证索引是否生效，`type` 至少达到 `range` 级别。

---

## 第三篇 InnoDB 底层原理

### 7. InnoDB 存储结构

#### 7.1 表空间、段、区、页、行

- **页 Page**：InnoDB 默认页大小 `16KB`，是磁盘和内存的最小交互单元。页类型：数据页、索引页、Undo 页、LOB 页等。  
- **区 Extent**：每个区 `1MB`，包含 64 个连续页，用于保证顺序 IO。  
- **段 Segment**：逻辑概念，包含叶子节点段、非叶子节点段等，由多个区组成。索引由两个段组成：一个管理叶子节点数据，一个管理非叶子节点。  
- **表空间**：逻辑存储的最高层，包含多个段。

#### 7.2 行格式 Compact/Dynamic

| 行格式 | 特点 |
|--------|------|
| `Compact` | 长字段溢出时，页内保存前缀 + 溢出页指针 |
| `Dynamic` | 与 Compact 类似，但完全溢出，页内只存指针 |
| `Compressed` | 支持压缩，CPU 开销较高 |
| `Redundant` | 老格式，已淘汰 |

**MySQL 8.0 默认行格式为 `Dynamic`**，适合包含大字段（TEXT/BLOB）的表。

#### 7.3 源码阅读路线

**核心源码路径**：
```
storage/innobase/
├── buf/
│   ├── buf0buf.cc        # Buffer Pool 主体，页分配、LRU、flush 协调
│   ├── buf0flu.cc        # 脏页刷盘逻辑
│   └── buf0lru.cc        # LRU 链表操作
├── trx/
│   ├── trx0trx.cc        # 事务对象、ReadView 生成
│   ├── trx0undo.cc       # Undo Log 管理
│   └── trx0purge.cc      # Purge 线程
├── log/
│   ├── log0log.cc        # Redo Log 写入、checkpoint
│   └── log0recv.cc       # 崩溃恢复
├── lock/
│   ├── lock0lock.cc      # 锁管理、死锁检测
│   └── lock0wait.cc      # 锁等待
└── row/
    ├── row0mysql.cc      # 行操作入口
    └── row0sel.cc        # 查询、MVCC 读取
```

架构师读源码不必逐行，先掌握核心数据结构与调用关系，重点看 Buffer Pool、Redo、Undo、Lock 四个模块。

#### 7.4 InnoDB 页结构（16KB）

一个 InnoDB 数据页内部布局：

```
+---------------------+
| FIL Header (38B)    |  页头，记录页类型、空间ID、LSN
+---------------------+
| Page Header (56B)   |  页内记录数、槽数量、free指针
+---------------------+
| Infimum + Supremum  |  最小记录和最大记录，用于链表
+---------------------+
| User Records        |  实际存储的行记录，通过单向链表组织
+---------------------+
| Free Space          |  空闲空间
+---------------------+
| Page Directory      |  槽数组，每个槽指向一组记录，用于二分查找
+---------------------+
| FIL Trailer (8B)    |  校验和、LSN
+---------------------+
```

**为什么页内能快速二分查找？**  
Page Directory 槽将记录分组，每个槽指向组内最后一条记录。查找时先通过槽二分定位组，再在组内顺序扫描，从而在页内实现高效查找。

#### 7.5 一次 SELECT 的源码调用链

```
客户端 SQL
  ↓
SQL Parser（词法/语法分析）
  ↓
LEX 结构
  ↓
JOIN::optimize()
  ↓
make_join_plan()（生成执行计划，选择索引）
  ↓
handler 接口（存储引擎抽象层）
  ↓
ha_innobase::index_read()（InnoDB 读取入口）
  ↓
B+Tree 搜索（btr_cur_search_to_nth_level）
  ↓
Buffer Pool 页访问（buf_page_get）
  ↓
返回行数据
```

架构师理解这条链路后，能快速定位 SQL 慢在哪个环节。

#### 7.6 Undo 日志两类

- **Insert Undo**：仅在事务回滚时需要，事务提交后可直接删除，不参与 MVCC。
- **Update Undo**：用于回滚和 MVCC 版本链，事务提交后不能立即删除，需等 Purge 线程清理。

Purge 删除 delete-mark 记录的条件：当 delete-mark 记录的 Undo 版本不再被任何 ReadView 需要时，Purge 线程才会物理删除。

#### 7.7 Redo Log Buffer 与 mini-transaction（mtr）

事务修改数据时，InnoDB 内部通过 **mini-transaction（mtr）** 生成 Redo 记录：

```
事务修改 → mtr → 生成 redo record → 写入 log buffer → 提交时 flush
```

mtr 保证 Redo 记录的原子性写入，多个 mtr 组成一个事务的 Redo 日志。

#### 7.8 主从复制深化

- **GTID 自动定位**：从库记录已执行的 GTID 集合，重新连接时自动协商从哪个 GTID 继续，无需手动指定 binlog 文件+偏移量。
- **Relay Log Recovery**：从库崩溃后，根据 SQL 线程执行进度和 relay log 信息恢复，避免重复执行。
- **Crash Safe Replication**：通过 `relay_log_recovery=ON` 和 `sync_relay_log` 保证从库崩溃恢复后数据一致。
- **并行复制 WRITESET**：MySQL 8.0 基于写集合判断事务之间是否有冲突，无冲突的事务可在从库并行回放，极大提升复制速度。

#### 7.9 分库分表真实坑

**跨分片唯一约束**：例如手机号唯一，但数据按 user_id 分片后，无法在单个分片内保证全局唯一。解决方案：
- 使用全局唯一服务（Redis setnx / 数据库唯一表）
- 维护一张“手机号 → user_id”映射表，映射表不分片或按手机号分片
- 使用分布式锁

**跨库分页**：订单按 user_id 分 64 库，查询全部订单第 1 页。需要：64 个库分别 `limit 0,20`，应用层合并 1280 条后排序取前 20，复杂度 O(N*M)。更优方案：使用 ES 等搜索引擎维护排序结果。

### 8. Buffer Pool

#### 8.1 作用与组成

**作用**：缓存表数据和索引页，减少磁盘 IO，是 InnoDB 最重要的内存结构。

**关键参数**：
```sql
-- 查看 Buffer Pool 大小，通常设为物理内存的 50%~80%
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
```

**内部组成**：数据页、索引页、插入缓冲页、自适应哈希索引、锁信息，以及三种链表：`free list`、`flush list`、`LRU list`。

#### 8.2 Free List / LRU List / Flush List

- **Free List**：空闲页链表，新页分配时从头部取。  
- **LRU List**：所有已加载页，按访问时间排序，分 young/old 区。  
- **Flush List**：脏页链表，按 oldest_modification（LSN）排序，用于刷脏。

#### 8.3 LRU 冷热分离与 midpoint 插入策略

**背景问题**：大查询（全表扫描）会读入大量页，若直接放入 LRU 头部会淘汰热点数据。

**MySQL 解决**：LRU 链表分 **young 区（热端）** 和 **old 区（冷端）**。新读入的页默认放在 old 区头部（midpoint，约 5/8 处），只有该页在 `innodb_old_blocks_time`（默认 1000ms）之后再次被访问，才会移到 young 区头部。

**关键参数**：
```sql
-- old 区占比，默认 37
SHOW VARIABLES LIKE 'innodb_old_blocks_pct';
-- 晋升 young 区时间阈值，默认 1000ms
SHOW VARIABLES LIKE 'innodb_old_blocks_time';
```

**调优建议**：如果热点数据频繁被大扫描挤出，可增大 `innodb_old_blocks_pct` 或 `innodb_old_blocks_time`。

#### 8.4 Change Buffer

**作用**：当对**非唯一二级索引**做插入/更新/删除时，如果目标索引页不在 Buffer Pool 中，先写入 Change Buffer，后续通过 merge 写入磁盘。

**为什么只支持非唯一索引？** 唯一索引必须读取磁盘判断是否冲突，无法缓冲。

**参数**：`innodb_change_buffer_max_size` 默认 25% of Buffer Pool。

**面试题：唯一索引和普通索引选哪个？** 查询性能接近；写入性能普通索引更好（可利用 Change Buffer），唯一索引保证约束。核心还是业务约束优先。

#### 8.5 Adaptive Hash Index（AHI）

InnoDB 监控热点页的等值查询，自动在 Buffer Pool 上建立哈希索引，加速 `WHERE id = ?` 类查询。无需人工干预，但仅对热点数据有效。

#### 8.6 脏页刷新与调优

- **脏页**：Buffer Pool 中已被修改但尚未写入磁盘的页。  
- **刷脏策略**：由 Page Cleaner 线程根据脏页比例、LSN 年龄等决定刷盘顺序。

**关键参数**：
```sql
SHOW VARIABLES LIKE 'innodb_max_dirty_pages_pct';     -- 脏页比例阈值，默认 75%
SHOW VARIABLES LIKE 'innodb_max_dirty_pages_pct_lwm'; -- 低水位线
SHOW VARIABLES LIKE 'innodb_flush_neighbors';         -- 是否刷相邻脏页
SHOW VARIABLES LIKE 'innodb_adaptive_flushing';       -- 自适应刷脏
SHOW VARIABLES LIKE 'innodb_io_capacity';             -- IO 能力，影响刷脏速度
```

**机制**：脏页达到阈值后，后台线程开始刷盘。刷盘顺序基于 LSN 年龄，优先刷最旧的脏页。自适应刷脏根据 redo log 产生速度动态调整刷脏速率，避免 checkpoint 滞后。

**避坑**：
- 设置过高的 `innodb_max_dirty_pages_pct` 可能导致刷盘不及时，IO 尖刺。  
- 传统 HDD 可开启 `innodb_flush_neighbors`，SSD 建议关闭减少随机 IO。  
- 监控 `Innodb_buffer_pool_pages_dirty` 和 `Innodb_buffer_pool_wait_free`。

**如何避免全表扫描污染 Buffer Pool？**  
调整 `innodb_old_blocks_pct` 和 `innodb_old_blocks_time`，让扫描页在 old 区快速淘汰；同时尽量避免高峰期执行大查询。

### 9. Redo Log

#### 9.1 WAL 机制

**核心思想**：先写日志，后写磁盘。修改数据时先记录 Redo Log，再修改内存页，随后由后台线程刷脏页。崩溃后通过 Redo Log 重做。

#### 9.2 Redo Log 写入链路与 Checkpoint

- **文件**：`ib_logfile0` / `ib_logfile1`，循环写入。  
- **记录内容**：物理页的修改，保证持久性。  
- **落盘时机**：由 `innodb_flush_log_at_trx_commit` 控制：
  - `1`：每次事务提交 fsync（最安全）  
  - `0`：每秒刷（可能丢失 1s 数据）  
  - `2`：写入 OS 缓存，每秒刷（可能丢失 1s 数据）

**写入链路图**：
```
事务提交 → 写 Redo Log Buffer → 写入 OS Cache → fsync 到 ib_logfile
```

**Checkpoint**：记录 LSN，表示该点之前的 Redo 日志对应的脏页已全部刷盘，可被覆盖。Redo Log 文件循环使用，写满后触发 checkpoint。若 checkpoint 跟不上日志产生速度，会强制刷脏，导致性能下降。

**监控**：`Innodb_log_waits` 大于 0 说明日志缓冲不足。

#### 9.3 两阶段提交（2PC）

**为什么需要 2PC？** 保证 Redo Log 与 Binlog 的一致性，避免主从数据不一致。

**流程**：
```
事务开始
执行 SQL → 写 Undo Log → 修改内存页 → 写 Redo Log（prepare 阶段）
写 Binlog
提交事务 → Redo Log 标记 commit
```

**崩溃恢复判断**：
- Redo Log 中 prepare 且 Binlog 已完整写入 → 提交。  
- Redo Log 中 prepare 但 Binlog 未写入 → 回滚。

#### 9.4 崩溃恢复机制

崩溃后，InnoDB 读取 Redo Log，从 checkpoint 开始重放已提交但未刷盘的事务，保证持久性。对于 prepare 状态的事务，根据 Binlog 是否存在决定提交或回滚。

### 10. Undo Log

#### 10.1 回滚与 MVCC

- 记录逻辑修改前的旧值，用于事务回滚和 MVCC。  
- 存储在系统表空间或独立 undo 表空间。  
- 长事务会保留大量 Undo Log，导致版本链过长、空间膨胀。

#### 10.2 Undo Log 生命周期与 Purge 机制

**Undo 为什么不能立即删除？**  
MVCC 要求事务能够读取到事务开始时的数据快照。如果事务 A 开启后尚未结束，其他事务修改数据产生的旧版本必须保留，否则 A 无法获得一致性读。

**示例**：
```
事务 A（trx_id=100）SELECT * FROM user WHERE id=1;  -- 创建 ReadView
事务 B（trx_id=101）UPDATE user SET name='new' WHERE id=1; -- 产生 Undo 版本（旧 name）
事务 A 再次 SELECT 时，需要读取旧版本。
如果 Undo 立即删除，事务 A 将读到不一致数据。
```

**purge thread 与 history list length**  
- **purge thread**：后台线程，负责清理不再需要的 Undo 日志和删除标记的记录。  
- **history list**：由未清理的 Undo 日志组成的链表，可通过 `SHOW ENGINE INNODB STATUS\G` 查看 `History list length`。  
- `history list length` 越大，说明积压的 Undo 越多，可能导致 undo 表空间膨胀。

**清理条件**：一个 Undo 日志只有在以下条件都满足时才可被 purge：
- 生成该 Undo 的事务已提交或回滚  
- 所有在它之前开启的读视图（ReadView）已关闭

#### 10.3 长事务与 History List 排查

**排查 SQL**：
```sql
-- 查看当前运行的事务，关注 trx_started 时间
SELECT * FROM information_schema.innodb_trx\G
```

**线上问题：磁盘空间一直增长**  
很多时候并非数据增长，而是长事务导致 Undo 无法 purge。处理：
- 找到长事务，尽快提交或回滚。  
- 应用层避免在事务中进行外部调用（RPC、MQ、文件 IO）。  
- 设置 `max_execution_time` 或超时监控。

监控 `History list length`，超过阈值（如 10000）立即告警并排查长事务。

### 11. Binlog

#### 11.1 三种日志格式

- **STATEMENT**：记录 SQL 语句，体积小，但某些函数可能导致主从不一致。  
- **ROW**：记录行级变更，体积大，但精确，推荐使用。  
- **MIXED**：混合模式，默认使用 STATEMENT，必要时切换 ROW。

**生产建议**：使用 ROW 格式，配合 `binlog_row_image=full` 保证数据一致性。

#### 11.2 主从复制与数据同步

Binlog 用于主从复制：主库 Binlog Dump 线程发送日志，从库 I/O 线程写入 Relay Log，SQL 线程回放。通过 `sync_binlog = 1` 保证每次事务写入并刷盘。

#### 11.3 Binlog 实战：Canal 同步

**架构**：
```
MySQL Master → Binlog dump → Canal Server（伪装从库）→ 解析 Binlog → Kafka/RocketMQ → 消费者 → ES/Redis/数仓
```

**应用场景**：
- 搜索同步：MySQL → ES  
- 缓存更新：异步刷新 Redis  
- 数据订阅：订单变更触发后续流程  
- 数据湖/数仓：增量同步到 Hive/ClickHouse  
- 跨系统解耦：微服务异步通信

**注意点**：
- MySQL 必须开启 Binlog，格式为 ROW。  
- 消费者要幂等，防止重复消费。  
- 监控 Canal 延迟。

---

## 第四篇 事务、MVCC 与锁机制

### 12. 事务模型

#### 12.1 ACID 特性及底层保障

| 特性 | 定义 | 底层保障 |
|------|------|----------|
| 原子性 | 事务全部成功或全部失败 | Undo Log 回滚 |
| 一致性 | 数据库状态从一个一致状态到另一个 | 原子性+隔离性+持久性共同保障 |
| 隔离性 | 并发事务互不干扰 | MVCC + 锁 |
| 持久性 | 提交后数据不会丢失 | Redo Log + Binlog |

#### 12.2 事务隔离级别与并发异常

| 级别 | 脏读 | 不可重复读 | 幻读 |
|------|------|-----------|------|
| READ UNCOMMITTED | 可能 | 可能 | 可能 |
| READ COMMITTED | 不可能 | 可能 | 可能 |
| REPEATABLE READ（默认） | 不可能 | 不可能 | 可能（InnoDB 通过锁解决当前读幻读） |
| SERIALIZABLE | 不可能 | 不可能 | 不可能 |

**RR 级别下如何解决幻读？**
- **快照读（普通 SELECT）**：通过 MVCC 的 ReadView 解决，事务内读取一致。  
- **当前读（`SELECT ... FOR UPDATE` / `UPDATE` / `DELETE`）**：通过 Next-Key Lock 解决，锁住记录及间隙，阻止插入。

#### 12.3 隔离级别的选择

- 生产环境默认使用 REPEATABLE READ（MySQL 默认），兼顾一致性和并发。  
- 对幻读要求极高的场景可考虑 SERIALIZABLE，但性能差。  
- 某些业务（如报表）可接受 RC，提高并发。

### 13. MVCC

#### 13.1 隐藏字段与 Undo 版本链

每行记录有隐藏列：
- `DB_TRX_ID`：最近修改的事务 ID  
- `DB_ROLL_PTR`：指向 Undo Log 的回滚指针  
- `DB_ROW_ID`：无主键时的隐藏主键

**版本链**：不同事务修改同一行会形成 Undo Log 链：
```
行记录 → Undo1 (trx=100) → Undo2 (trx=90) → ...
```

#### 13.2 ReadView 结构

```
ReadView {
  m_ids: 创建时活跃事务 ID 列表
  min_trx_id: 最小活跃事务 ID
  max_trx_id: 下一个可分配的事务 ID（不是最大活跃）
  creator_trx_id: 创建 ReadView 的事务 ID
}
```

**可见性判断**：
- 行版本 `trx_id < min_trx_id` → 可见  
- `trx_id >= max_trx_id` → 不可见  
- `trx_id` 在 `m_ids` 中 → 不可见（活跃事务未提交）  
- 否则可见

**隔离级别差异**：
- RC：每次快照读生成新 ReadView。  
- RR：第一次快照读生成 ReadView，事务内复用。

#### 13.3 一致性读与当前读

- **一致性读（快照读）**：普通 `SELECT`，使用 MVCC 读取快照，不加锁。  
- **当前读**：`SELECT ... FOR UPDATE`、`UPDATE`、`DELETE`，读取最新版本并加锁。  
- 两者不能混用，否则可能逻辑不一致。

#### 13.4 RC vs RR 的 MVCC 差异

RC 每次快照读生成新 ReadView，能看到已提交的修改；RR 事务内 ReadView 固定，保证可重复读。

### 14. 锁机制

#### 14.1 行锁/表锁/意向锁

- **行锁**：共享锁 `S`、排他锁 `X`  
- **表锁**：`LOCK TABLES`，DDL 使用  
- **意向锁**：`IS` / `IX`，表级，用于协调行锁与表锁，事务申请行锁前先加意向锁

#### 14.2 Record Lock / Gap Lock / Next-Key Lock

| 锁 | 作用对象 | 阻止 |
|----|----------|------|
| Record Lock | 单条索引记录 | 锁住该记录 |
| Gap Lock | 索引记录之间的间隙 | 阻止在间隙插入 |
| Next-Key Lock | 记录 + 前置间隙（左开右闭） | 阻止插入和修改 |

**RR 级别默认开启 Next-Key Lock**，可防止幻读。  
示例：
```sql
-- 表 t(id)，索引 id，数据：1,5,10
-- 事务 A
SELECT * FROM t WHERE id = 5 FOR UPDATE;
-- 锁住 (1,5] 和 (5,10] 的 Next-Key Lock
```

**陷阱**：
- Gap Lock 会导致并发插入阻塞，即使插入的记录和锁定记录无关。  
- RR 级别下普通 SELECT 不加锁，但 `FOR UPDATE` / `UPDATE` / `DELETE` 会加 Next-Key Lock。  
- 如果 `UPDATE/DELETE` 的 `WHERE` 条件未命中任何索引，InnoDB 会扫描聚簇索引，并对扫描到的每一条记录加 Next-Key Lock，产生大量行锁和间隙锁，效果上类似表锁，阻塞大量并发。准确说法是：**未走索引的锁操作可能扫描大量记录并产生大量锁，造成类似表锁的阻塞效果**，但并非直接加表锁。

#### 14.3 死锁排查与解决

**死锁日志**：
```sql
-- 查看死锁日志
SHOW ENGINE INNODB STATUS;
-- 查看 LATEST DETECTED DEADLOCK 部分
```

**系统表**：
```sql
SELECT * FROM information_schema.innodb_trx;
SELECT * FROM information_schema.innodb_locks; -- 8.0 用 performance_schema.data_locks
SELECT * FROM information_schema.innodb_lock_waits;
```

**案例：交叉更新**：
```sql
-- 事务 A
BEGIN;
UPDATE account SET balance = balance - 100 WHERE id = 1;
UPDATE account SET balance = balance + 100 WHERE id = 2;

-- 事务 B
BEGIN;
UPDATE account SET balance = balance - 200 WHERE id = 2;
UPDATE account SET balance = balance + 200 WHERE id = 1;
```
产生循环等待，InnoDB 检测到后回滚其中一个事务。

**解决策略**：
- 事务中按相同顺序加锁  
- 减小事务粒度，缩短持有锁时间  
- 使用乐观锁替代悲观锁  
- 设置 `innodb_lock_wait_timeout`，避免无限等待  
- 应用层捕获死锁异常并自动重试

#### 14.4 锁等待诊断体系

**查看当前所有锁**：
```sql
SELECT * FROM performance_schema.data_locks\G
```

**查看锁等待关系**：
```sql
SELECT * FROM performance_schema.data_lock_waits\G
```

**完整排查流程**：
```
接口慢 → 慢查询日志 → 发现 SQL 等待 → data_lock_waits 查看 WAITING 事务
→ innodb_trx 找到阻塞源事务 → 定位应用代码 → 优化事务范围/加锁顺序
```

**关键字段**：`ENGINE_TRANSACTION_ID`、`OBJECT_SCHEMA`、`INDEX_NAME`、`LOCK_TYPE`、`LOCK_MODE`、`LOCK_STATUS`。

#### 14.5 生产案例：锁等待、死锁、长事务

- 监控 `data_lock_waits` 持续增长，告警通知。  
- 长事务通过 `innodb_trx` 的 `trx_started` 判断，超过阈值自动 kill 或通知。  
- 死锁不可避免，应用层必须处理重试逻辑，并记录日志方便分析。

#### 14.6 锁与事务深度

##### 锁兼容矩阵

|  | IS | IX | S | X |
|--|----|----|---|---|
| IS | ✅ | ✅ | ✅ | ❌ |
| IX | ✅ | ✅ | ❌ | ❌ |
| S  | ✅ | ❌ | ✅ | ❌ |
| X  | ❌ | ❌ | ❌ | ❌ |

Gap Lock 与 Gap Lock 之间兼容（都是纯间隙锁），Next-Key Lock = Record + Gap，兼容性取决于组合。

##### 使用 sys.innodb_lock_waits 视图

```sql
-- 查看当前锁等待关系
SELECT * FROM sys.innodb_lock_waits;
```

比直接查 `performance_schema` 更直观，包含阻塞事务、等待事务、SQL 等。

##### 事务隐式提交场景

以下语句会隐式提交当前事务（即使未执行 COMMIT）：
- DDL（CREATE、ALTER、DROP 等）
- `LOCK TABLES` / `UNLOCK TABLES`
- `BEGIN` / `START TRANSACTION`
- 加载数据 `LOAD DATA`（部分情况）

##### Group Commit 原理

Binlog 组提交将多个事务的 Binlog 写入合并为一次 fsync，提升写入性能。Redo Log 也有组提交机制。两个组提交协作保证 2PC 效率。

---

## 第五篇 SQL 性能优化体系

### 15. MySQL 优化器

#### 15.1 Cost Model 成本计算

MySQL 优化器基于成本选择执行计划，成本包括 IO 成本和 CPU 成本。

```sql
-- 查看 JSON 格式执行计划成本
EXPLAIN FORMAT=JSON
SELECT * FROM `order` WHERE user_id = 100 AND status = 'PAID';
```

**关键字段**：
```json
"cost_info": {
  "read_cost": "12.35",   // 磁盘 IO 成本
  "eval_cost": "3.50",    // CPU 成本
  "prefix_cost": "15.85", // 累计总成本
  "data_read_per_join": "5K"
}
```

优化器选择 `prefix_cost` 最小的方案。

#### 15.2 统计信息与直方图

**普通统计信息**：索引的 Cardinality，通过 `SHOW INDEX FROM t;` 查看。

**数据倾斜问题**：列数据分布不均时，仅靠普通统计信息无法精确评估过滤效果。

**Histogram 直方图（MySQL 8.0+）**：
```sql
-- 为 status 列创建直方图，100 个桶
ANALYZE TABLE `order` UPDATE HISTOGRAM ON status WITH 100 BUCKETS;

-- 查看直方图
SELECT * FROM information_schema.column_statistics
WHERE table_name = 'order' AND column_name = 'status';

-- 删除直方图
ANALYZE TABLE `order` DROP HISTOGRAM ON status;
```

**使用建议**：对区分度低、数据倾斜严重的列创建直方图；占用额外存储，不宜对所有列创建；数据频繁变更后需定期更新。

#### 15.3 执行计划稳定性管理

MySQL 没有 Oracle 那种完整的 SQL Plan Baseline，但可以通过以下方式管理执行计划稳定性：

- **直方图**：优化倾斜列的行数估算。
- **不可见索引**：测试删除索引的影响，避免直接 DROP 导致执行计划退化。
- **优化器 Hint**：使用 `FORCE INDEX`、`USE INDEX`、`STRAIGHT_JOIN` 等临时固定计划。
- **持久化统计信息**：`innodb_stats_persistent=ON`，避免统计信息频繁变化。
- **`OPTIMIZER_TRACE`**：分析优化器决策，发现不稳定原因。
- **SQL 改写**：有时改写 SQL 比强制计划更稳定。

#### 15.4 Optimizer Trace 分析

```sql
-- 开启 optimizer trace
SET optimizer_trace = 'enabled=on';
SELECT * FROM `order` WHERE user_id = 100;
SELECT * FROM information_schema.optimizer_trace\G
SET optimizer_trace = 'enabled=off';
```

输出包含 `considered_execution_plans`，展示每个候选路径的成本和行数，解释优化器为何选择某个索引。

#### 15.5 优化器深度：为什么选全表扫描？

**基础原因**：统计信息错误、回表成本高、选择性不足、成本模型判断。

**深度分析**：
- 优化器通过 `mysql.innodb_index_stats` 中的 Cardinality 估算行数，如果该值因数据变更未更新，会误判。
- 对于二级索引，访问路径成本 = 索引范围扫描成本 + 回表成本（随机 IO）。若回表行数超过约 20%~30%，全表顺序扫描可能更优。
- 直方图缺失时，对倾斜列过滤率估算偏差大。
- `eq_range_index_dive_limit` 影响范围扫描的采样精度，超出后使用平均值估算。
- 可查看 `OPTIMIZER_TRACE` 确认具体成本对比，必要时用 `FORCE INDEX` 或调整统计信息。

### 16. EXPLAIN 深度分析

#### 16.1 type 级别详解

| type | 含义 | 优化建议 |
|------|------|----------|
| `system` | 表仅一行，系统表 | 无需优化 |
| `const` | 主键或唯一索引等值查询 | 极好 |
| `eq_ref` | 关联查询用主键/唯一索引，每行只匹配一行 | 好 |
| `ref` | 非唯一索引等值查询 | 较好 |
| `range` | 范围扫描（BETWEEN/IN/>,<） | 可接受 |
| `index` | 全索引扫描 | 需优化 |
| `ALL` | 全表扫描 | 必须优化 |

#### 16.2 key / rows / filtered

- `key`：实际使用的索引  
- `rows`：预估扫描行数  
- `filtered`：过滤后行数百分比  
- `Extra` 常见：
  - `Using index`：覆盖索引，不回表  
  - `Using where`：存储引擎层返回后，Server 层过滤  
  - `Using temporary`：使用了临时表（GROUP BY/ORDER BY）  
  - `Using filesort`：文件排序，需优化  
  - `Using index condition`：索引下推  
  - `Using join buffer`：被驱动表无可用索引，连接缓冲

#### 16.3 Extra 关键信息

（见 16.2）

#### 16.4 EXPLAIN FORMAT=JSON 成本分析

`EXPLAIN FORMAT=JSON` 提供详细的成本信息，帮助理解优化器决策。重点关注 `cost_info` 和 `rows_examined_per_scan`。

### 17. 慢 SQL 优化流程

#### 17.1 发现问题 → 定位 SQL → EXPLAIN → 优化 → 验证

**流程**：
```
开启慢查询日志（long_query_time=1, log_queries_not_using_indexes=1）
→ 使用 pt-query-digest 分析
→ 定位高频慢 SQL
→ EXPLAIN / OPTIMIZER_TRACE 分析
→ 优化索引或改写 SQL
→ 回归测试验证
```

#### 17.2 深分页优化

```sql
-- 慢：OFFSET 1000000 导致扫描大量行后丢弃
SELECT id, title FROM article ORDER BY id LIMIT 1000000, 20;

-- 优化1：记录上次位置，使用游标
SELECT id, title FROM article WHERE id > 1000000 ORDER BY id LIMIT 20;

-- 优化2：延迟关联，先取主键再回表
SELECT a.id, a.title
FROM article a
JOIN (SELECT id FROM article ORDER BY id LIMIT 1000000, 20) tmp ON tmp.id = a.id;
```

#### 17.3 索引失效的 10 种场景

（见第二篇 6.1 完整表格）

**生产实践**：
- 定期分析慢查询日志，持续优化索引。  
- 上线前 SQL 审核，`type` 不得低于 `range`，`rows` 不超过阈值。  
- 使用 `pt-index-usage` 或 `sys.schema_unused_indexes` 发现冗余索引。

---

## 第六篇 MySQL 高并发架构设计

### 18. 热点数据问题

#### 18.1 秒杀库存与热点行更新

```sql
-- 热点行更新：10000 个请求同时更新同一行，产生严重锁竞争
UPDATE stock SET count = count - 1 WHERE id = 1;
```

#### 18.2 拆库存方案

将库存拆分为多个记录：
```
stock_0, stock_1, stock_2 ... stock_9
```
请求随机选择一个分片扣减，降低单行锁竞争。

```sql
-- 扣减某个库存分片，同时判断库存充足
UPDATE stock_0 SET count = count - 1 WHERE id = 1 AND count > 0;
```
**优点**：实现简单，数据库内解决。  
**缺点**：库存碎片，需要定期合并；库存总量判断复杂。

#### 18.3 Redis 扣减 + 异步落库（含失败补偿）

使用 Redis 原子操作扣减库存（`DECR` / `Lua`），异步同步到数据库。
```
请求 → Redis 扣减 → 成功 → 发送 MQ（库存扣减流水）
                        ↓
                  消费者更新数据库库存
                        ↓ 失败重试
                  多次失败进入死信队列
                        ↓
                  补偿任务：回滚 Redis 库存 或 人工介入
```

**必须处理 Redis 成功但 DB 失败**的场景：
1. Redis 扣减成功后，发送 MQ 消息（库存扣减流水）。
2. 消费者更新数据库库存，若失败重试。
3. 若多次重试仍失败，进入死信队列，触发**补偿任务**：回滚 Redis 库存（加回）或人工介入。
4. 每日对账：对比 Redis 库存与 DB 库存，修复差异。
5. 数据库兜底：订单表唯一约束 + 库存表 `count > 0` 条件更新防超卖。

**优点**：Redis 单线程原子性，性能极高。  
**缺点**：数据一致性复杂，需处理 Redis 与 DB 最终一致，需设计补偿机制。

#### 18.4 乐观锁方案

```sql
-- 使用 version 字段做乐观锁，更新时判断版本号
UPDATE stock
SET count = count - 1, version = version + 1
WHERE id = 1 AND version = 10;
```
**优点**：无锁等待，失败重试即可。  
**缺点**：冲突高时重试多，不适合超热点场景。

**Java 代码示例**：
```java
// 乐观锁扣减库存，带重试
public boolean deductStock(long productId, int quantity) {
    int retry = 3;
    while (retry-- > 0) {
        Stock stock = stockMapper.selectById(productId);
        if (stock.getCount() < quantity) return false;
        int affected = stockMapper.deductWithVersion(productId, quantity, stock.getVersion());
        if (affected == 1) return true;
    }
    return false;
}
```

**面试回答**：秒杀场景如何保证不超卖？数据库层面可用乐观锁、悲观锁、拆库存；高并发场景建议 Redis 原子扣减 + 数据库最终一致，配合限流和防重，并设计失败补偿和对账机制。

### 19. MySQL + Redis

#### 19.1 Cache Aside Pattern

**读流程**：
```
查询缓存 → 未命中 → 查询DB → 写缓存
```

**写流程**：
```
更新DB → 删除缓存
```

**为什么不是先删除缓存再更新 DB？**  
并发场景下，线程A删除缓存后，线程B查询旧数据写回缓存，线程A再更新DB，结果缓存中仍然是旧数据，产生脏缓存。

#### 19.2 缓存一致性（先更新 DB 再删除缓存）

先更新 DB 再删除缓存可能短暂不一致，但通过设置缓存过期时间兜底。

#### 19.3 延迟双删

```java
// 延迟双删，降低缓存不一致窗口
public void updateOrder(Order order) {
    orderMapper.update(order);                    // 1. 更新数据库
    redisTemplate.delete("order:" + order.getId()); // 2. 删除缓存
    CompletableFuture.runAsync(() -> {
        try { Thread.sleep(1000); } catch (InterruptedException e) {}
        redisTemplate.delete("order:" + order.getId()); // 3. 延迟再次删除
    });
}
```

#### 19.4 高并发架构设计

**万级 QPS 数据库架构**：
```
用户请求 → 负载均衡 → Redis 缓存集群 → 命中直接返回
                                    ↘ 未命中 → MySQL 集群（读写分离）
                                                  ↘ Binlog → MQ → ES/缓存/数仓
```

**关键组件**：缓存层、读写分离、Binlog 订阅、限流降级、数据隔离。

**热点 Key 缓存**：Redis + 本地缓存（Caffeine），防止缓存击穿（互斥锁/提前预热）。

**限流与降级**：接口限流（令牌桶/漏桶），降级非核心功能，熔断快速失败。

不要过度依赖缓存，数据一致性是难点。写后立即读需要路由到主库。

### 20. MySQL + MQ

#### 20.1 异步化与最终一致性

设计模式：
- **事务消息**：本地事务 + MQ 事务消息，保证 DB 和 MQ 的一致性。  
- **本地消息表**：业务表 + 消息表在同一事务，后台定时扫描发送。  
- **Binlog 订阅**：通过 Canal 解耦。

**示例：本地消息表**：
```sql
-- 本地消息表，与业务表同库
CREATE TABLE order_msg (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT,
  msg_body TEXT,
  status TINYINT DEFAULT 0, -- 0 未发送 1 已发送
  created_at DATETIME
);
```

```java
// 创建订单和消息记录在同一事务中
@Transactional
public void createOrder(Order order) {
    orderMapper.insert(order);
    orderMsgMapper.insert(new OrderMsg(order.getId(), order.toJson(), 0));
    // 事务提交后，后台任务扫描 status=0 发送 MQ
}
```

#### 20.2 Binlog Canal 同步

（见第三篇 11.3）

#### 20.3 本地消息表与分布式事务

| 方案 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 2PC/XA | 两阶段提交 | 强一致 | 性能差，单点 |
| TCC | Try-Confirm-Cancel | 灵活，业务控制 | 侵入大，实现复杂 |
| 本地消息表 | 消息 + 本地事务 | 简单，可靠 | 需后台任务 |
| Seata AT | 自动生成回滚 SQL | 无侵入 | 性能有损耗 |

**选型建议**：优先避免跨库事务，通过消息驱动最终一致。核心业务可选用 TCC 或 Seata。

#### 20.4 项目实战：订单/库存/评论系统

**订单系统**：
- 按 `user_id` 水平拆分 64 片，订单号雪花 ID。  
- 状态机：待支付 → 已支付 → 已发货 → 已完成/已取消。  
- 创建订单和扣库存通过本地消息表保证最终一致。  
- 查询优化：覆盖索引，商家订单可冗余或 ES。

**库存系统**：
- Redis 预扣减 + 异步落库 + 数据库兜底。  
- 防超卖：Lua 原子扣减，数据库 `count > 0` 条件更新。  
- 热点库存拆分多个 key。  
- 失败补偿和对账机制。

**评论系统**：
- 按内容 ID 水平分表，游标分页避免深分页。  
- 热门内容评论缓存或同步 ES。  
- 点赞数冗余原子更新。

#### 20.5 分布式事务与一致性模式

##### Saga 模式

Saga 将一个长事务拆分为多个本地事务，每个事务都有对应的补偿操作。如果某个步骤失败，则按逆序执行补偿。

适用场景：订单流程（下单、扣库存、支付、发货），隔离性要求不高。

##### TCC 三大坑

1. **空回滚**：Try 未执行，Cancel 却执行了。需记录 Try 状态，允许空回滚。
2. **幂等**：Try、Confirm、Cancel 均需幂等，防止网络重试导致重复执行。
3. **悬挂**：Cancel 先于 Try 到达，导致 Try 后执行无法回滚。需要拒绝迟到的 Try。

##### Seata AT 原理

AT 模式自动生成反向 SQL 作为 undo log，通过全局锁保证隔离。性能比 XA 好，但仍有性能损耗。

##### XA 事务缺陷

- 同步阻塞，性能差。
- 单点故障，协调者宕机导致事务悬挂。
- 部分数据库不支持。

##### 可靠消息最终一致性完整实现

1. 生产者本地事务：业务操作 + 写入消息表。
2. 后台任务扫描消息表，发送 MQ，更新消息状态。
3. 消费者幂等消费，处理业务，返回 ACK。
4. 消息发送失败自动重试，超过次数进入死信，人工处理。

---

## 第七篇 MySQL 高可用与扩展

### 21. 主从复制

#### 21.1 三个线程与复制流程

| 线程 | 位置 | 职责 |
|------|------|------|
| Binlog Dump 线程 | 主库 | 读取 Binlog 并发送给从库 |
| I/O 线程 | 从库 | 接收 Binlog 写入 Relay Log |
| SQL 线程 | 从库 | 回放 Relay Log 中的事件 |

#### 21.2 半同步复制与并行复制

**半同步复制**：主库提交事务时，等待至少一个从库确认收到 Binlog 后才返回客户端。优点：数据强一致；缺点：增加提交延迟。

**并行复制**：
- MySQL 5.6：按库级并行  
- MySQL 5.7：基于组提交的 `LOGICAL_CLOCK` 并行  
- MySQL 8.0：基于写集合的 `WRITESET` 并行

```sql
-- 设置并行复制类型和 worker 数量
SET GLOBAL slave_parallel_type = 'LOGICAL_CLOCK';
SET GLOBAL slave_parallel_workers = 4;
```

#### 21.3 GTID 复制

GTID（Global Transaction Identifier）是全局事务标识，简化主从切换和故障恢复。每个事务有一个唯一 GTID，从库通过 GTID 自动定位复制位置，避免手动指定 binlog 文件和偏移量。

#### 21.4 主从延迟原因与排查

**常见原因**：
- 主库大事务批量操作  
- 从库 SQL 线程单线程（未开并行复制）  
- 热点行更新导致从库锁等待  
- 网络带宽不足

**解决措施**：
- 拆分大事务，小批量提交  
- 开启并行复制，增加 workers  
- 延迟敏感业务走主库  
- 半同步复制降低延迟

监控 `Seconds_Behind_Master`，设置告警阈值。

### 22. 高可用方案

#### 22.1 MHA

MHA（Master High Availability）由管理节点和数据节点组成，可在主库故障时自动完成故障切换，通常 10~30 秒内完成。依赖 GTID 或 binlog 位置，需配合 VIP 或代理。

#### 22.2 MGR 组复制

MySQL Group Replication 是原生高可用方案，基于 Paxos 协议的多主/单主模式，数据强一致，自动选主，但性能有一定开销。

#### 22.3 ProxySQL / ShardingSphere

- **ProxySQL**：高性能代理，支持读写分离、查询路由、连接池。  
- **ShardingSphere**：Apache 顶级项目，支持 JDBC 和 Proxy 模式，可做分库分表和读写分离。  
- **MyCat**：老牌 Proxy 架构，功能全面。  
- **Vitess**：YouTube 开源，云原生大规模场景。

#### 22.4 读写分离架构与容灾

**读写分离**：写请求走主库，读请求走从库，中间件路由。

**主从延迟解决方案**：
| 方案 | 说明 |
|------|------|
| 半同步复制 | 主库等待从库确认，降低延迟 |
| 并行复制 | 从库多线程回放，提升消费速度 |
| 业务容忍 | 延迟敏感查询强制走主库 |
| 缓存 | 读请求走缓存，降低从库压力 |
| 监控 | `Seconds_Behind_Master` 告警 |
| 拆分 | 延迟大的业务单独从库 |

Java 中使用路由注解或动态数据源，对实时性要求高的接口指定主库。

#### 22.5 分布式中间件与高可用细节

##### ShardingSphere-JDBC vs Proxy

|  | JDBC | Proxy |
|--|------|-------|
| 架构 | 客户端直连，无代理 | 独立代理层 |
| 性能 | 无额外网络跳转，性能高 | 多一跳，性能略低 |
| 运维 | 需在应用内配置 | 集中配置，运维方便 |
| 适用 | 同构语言，应用规模不大 | 多语言，集中治理 |

##### MyCat / ProxySQL 高可用

- ProxySQL 通过管理平面配置读写分离，支持故障检测和自动切换。
- MyCat 通常配合 keepalived 实现 VIP 漂移。

##### MHA 故障切换流程

1. Manager 检测到主库宕机。
2. 从所有从库中选出数据最新的作为新主库。
3. 应用差异日志（relay log）到新主库。
4. 其他从库重新指向新主库。
5. 切换 VIP 或通知应用。

##### MGR 脑裂处理

MGR 使用 Paxos 协议，当网络分区时，只有多数派（quorum）能继续写入，少数派自动进入只读状态，防止脑裂。

##### Orchestrator

用于拓扑管理和自动故障切换，比 MHA 更灵活，支持多主、级联复制，提供 Web UI 和 API。

#### 22.6 云原生与新技术趋势

##### Aurora / PolarDB 存算分离

- 计算层和存储层分离，存储层采用共享分布式存储。
- 主从切换快速（秒级），数据可靠性高（多副本）。
- 兼容 MySQL 协议，无需修改应用。

##### TiDB / OceanBase 分布式数据库对比

| 特性 | TiDB | OceanBase |
|------|------|-----------|
| 兼容性 | MySQL 协议 | MySQL 协议 |
| 分布式事务 | Percolator 模型 | 原生分布式事务 |
| 适用场景 | HTAP，大规模 OLTP | 金融级高可用 |
| 扩展性 | 自动分片，弹性扩展 | 水平扩展，多租户 |

##### Serverless MySQL

自动伸缩计算资源，按使用量计费，适合低频、弹性负载。

##### MySQL HeatWave

Oracle 推出的 MySQL 分析加速引擎，内存列式存储，加速复杂查询。

### 23. 分库分表

#### 23.1 垂直拆分 vs 水平拆分

| 维度 | 垂直拆分 | 水平拆分 |
|------|----------|----------|
| 拆分方式 | 按业务域拆库拆表 | 按主键/分片键拆分行 |
| 解决问题 | 单库表过多、资源竞争 | 单表数据量过大 |
| 示例 | 用户库、订单库、商品库 | 订单表 `order_0` ~ `order_9` |

#### 23.2 分片策略

- **Hash 分片**：`user_id % 32`，分布均匀，扩容难。  
- **Range 分片**：按时间分表，归档方便，热点集中。  
- **一致性哈希**：减少扩容迁移量，需虚拟节点。  
- **自定义路由**：按业务规则（地区、用户类型）分片。

**Sharding Key 选择**：查询频繁、分布均匀、稳定。

#### 23.3 Sharding Key 选择与全局 ID 设计

- 雪花算法（时间戳 + 机器码 + 序列号）  
- 数据库号段（如美团 Leaf）  
- Redis INCR  
- UUID（不适合作为主键）

#### 23.4 跨库 JOIN 与分页处理

| 方案 | 实现 |
|------|------|
| 字段冗余 | 避免 JOIN，直接查询单表 |
| 全局表 | 小表全量同步到每个库 |
| 应用层组装 | 分别查询多个库，Java 代码合并 |
| 数据同步 | 通过 Canal / DTS 将数据聚合到 ES、数仓 |

**分页查询**：单分片正常；跨分片需查询多个分片后合并排序，可用中间件支持或维护搜索索引（如 ES）。

#### 23.5 数据迁移与平滑扩容

**双写切换**：
```
老库/老表 ← 应用双写 → 新库/新表
        ↓ 数据同步（Canal / DTS）
   校验数据一致性 → 切换读流量 → 下线老库
```

**扩容 4库→8库**：双写+历史数据迁移，或一致性哈希减少迁移量，或预分片（如一开始分 128 片）。

#### 23.6 容量规划

| 指标 | 阈值参考 | 方案 |
|------|----------|------|
| 单表数据量 | > 1000 万行 | 分表 |
| 单库 QPS | > 2000~5000 | 分库 |
| 单库连接数 | > 1000 | 分库 / 读写分离 |
| IO 压力 | 磁盘 IO 利用率 > 70% | 读写分离 / 缓存 |
| 热点数据 | 单行更新 > 1000 TPS | 拆分 / Redis |

提前规划容量，先做读写分离和缓存缓解，再逐步拆分。分库分表后避免跨库事务，尽量本地事务+最终一致。

#### 23.7 数据一致性校验

##### pt-table-checksum

```bash
# 校验主从数据一致性
pt-table-checksum --host=127.0.0.1 --user=root --password=xxx --databases=test
```

生成校验结果，发现不一致时用 `pt-table-sync` 修复。

##### pt-table-sync

```bash
# 打印修复 SQL（不执行）
pt-table-sync --print --host=127.0.0.1 --user=root --password=xxx D=test,t=user

# 执行修复
pt-table-sync --execute --host=127.0.0.1 --user=root --password=xxx D=test,t=user
```

##### 分库分表数据一致性校验

在双写切换中，可定期对比源库和目标库的摘要值（如 `CRC32` 或 `MD5` 分组聚合），或使用数据同步工具自带校验（如 Canal 的校验功能）。

---

## 第八篇 MySQL 生产运维与故障排查

### 24. 监控与告警体系

#### 24.1 关键指标

- CPU、内存、磁盘 IO  
- 连接数（`Threads_connected`、`Threads_running`）  
- 慢查询数、锁等待数  
- 主从延迟（`Seconds_Behind_Master`）  
- Buffer Pool 命中率（`Innodb_buffer_pool_read_requests` / `Innodb_buffer_pool_reads`）

#### 24.2 SQL 审核与线上治理

**流程**：
```
慢日志 / 性能监控 → pt-query-digest / 自研采集 → SQL 排名与趋势
→ EXPLAIN 分析 → 优化方案 → 回归测试 → 上线验证
```

**SQL Review 与发布前检查**：
- 使用 Yearning、Archery 集成 CI/CD。  
- 规则：禁止 `SELECT *`、必须有索引、禁止深分页、DDL 需走 Online 流程等。  
- 强制 `EXPLAIN` 输出，`type` 不得低于 `range`，`rows` 不超过阈值。  
- 自动索引检测：`pt-index-usage`、`sys.schema_unused_indexes`。

#### 24.3 参数调优与内存管理

##### 多实例 Buffer Pool

```sql
-- 设置 Buffer Pool 实例数，通常为 CPU 核数，减少锁竞争
SET GLOBAL innodb_buffer_pool_instances = 8;
```

要求 `innodb_buffer_pool_size` >= 1GB 才能生效。

##### 会话级内存参数

| 参数 | 作用 | 建议值 |
|------|------|--------|
| `sort_buffer_size` | 排序缓冲区 | 256KB~2MB，按需调整 |
| `join_buffer_size` | JOIN 缓冲区 | 256KB~4MB |
| `read_rnd_buffer_size` | 随机读缓冲区 | 256KB~1MB |
| `tmp_table_size` | 内存临时表大小 | 16MB~64MB |
| `max_heap_table_size` | MEMORY 表最大大小 | 与 tmp_table_size 一致 |

##### IO 相关

- `innodb_io_capacity`：后台刷新脏页的 IOPS 基准，普通 SSD 设 200~2000。
- `innodb_io_capacity_max`：最大 IOPS，通常为 capacity 的 2 倍。
- `innodb_flush_method`：推荐 `O_DIRECT`，避免双缓存。

##### 日志与一致性组合

| 场景 | `innodb_flush_log_at_trx_commit` | `sync_binlog` |
|------|----------------------------------|---------------|
| 金融核心（安全第一） | 1 | 1 |
| 互联网业务（性能优先） | 2 | 1 或 2 |
| 允许少量丢失（日志） | 0 | 0 |

##### binlog_row_image

- `FULL`：记录所有列，最安全。
- `MINIMAL`：只记录主键和变更列，减少日志量，适合 Canal 同步。

##### max_connections 与连接池配比

```
应用连接池总大小 = (数据库 max_connections - 预留) / 应用实例数
```

预留约 10% 给管理连接，避免连接耗尽。

#### 24.4 数据库压测与容量评估

##### sysbench 使用

```bash
# 准备数据
sysbench oltp_read_write --mysql-host=127.0.0.1 --mysql-user=root --mysql-password=xxx \
 --mysql-db=test --tables=10 --table_size=100000 prepare

# 运行压测
sysbench oltp_read_write --mysql-host=127.0.0.1 --mysql-user=root --mysql-password=xxx \
 --mysql-db=test --tables=10 --table_size=100000 --threads=100 --time=60 run

# 清理
sysbench oltp_read_write --mysql-host=127.0.0.1 --mysql-user=root --mysql-password=xxx \
 --mysql-db=test --tables=10 --table_size=100000 cleanup
```

关注指标：TPS（事务/秒）、QPS（查询/秒）、95% 延迟。

##### 容量估算模型

假设单条 SQL 平均耗时 1ms，CPU 核数 16，数据库可支撑约 `16 / 0.001 = 16000 QPS`（理想值）。实际需考虑锁等待、IO 等，通常打 5~7 折。

磁盘 IOPS 估算：每事务 2 次 IO，TPS=1000 则需要 2000 IOPS，SSD 通常提供 10000+ IOPS。

#### 24.5 团队规范与治理

##### 数据库设计规范

- 表名、字段名统一小写+下划线，如 `user_id`。
- 主键统一 `BIGINT UNSIGNED AUTO_INCREMENT` 或雪花 ID。
- 必备字段：`id`、`create_time`、`update_time`。
- 索引命名：`idx_表名_字段`、`uk_表名_字段`。

##### SQL 上线流程

1. 开发提交 SQL 工单（含 EXPLAIN 截图）。
2. DBA 或审核工具自动检查（Yearning/Archery）。
3. 审批通过后，定时执行或灰度执行。
4. 执行后监控慢查询、锁等待。

##### 元数据管理

使用工具（如 Flyway、Liquibase）管理表结构变更，版本化脚本，可回溯。

##### 慢查询治理平台

Yearning、Archery 开源平台可集成 SQL 审核、工单、执行、审计，实现全流程管控。

### 25. 故障排查方法论

#### 25.1 CPU 100% 排查

**排查流程**：
```
监控发现 CPU 100% → SHOW FULL PROCESSLIST 查看活跃连接
→ 找到执行时间长的 SQL → EXPLAIN 分析
→ 定位全表扫描 / 索引失效 / 大事务
```

**常见原因**：SQL 未走索引全表扫描；大量并发复杂 SQL；大事务导致锁等待、Buffer Pool 污染。

**解决**：紧急限流、KILL 慢查询；长期优化 SQL、添加索引、拆分大事务。

#### 25.2 磁盘增长排查

**排查流程**：
```
磁盘使用率告警 → df -h → 查看数据目录 → 检查 undo 表空间 / binlog / 大表
```

**常见原因**：
- 数据增长：大表无归档  
- Undo 膨胀：长事务导致 undo 无法 purge  
- Binlog 堆积：从库延迟或未及时清理  
- 临时表空间膨胀

**解决**：
- 归档历史数据  
- 找出长事务并回滚，监控 `History list length`  
- 设置 `binlog_expire_logs_seconds`  
- 限制临时表空间

#### 25.3 主从延迟排查

（见 21.4）

#### 25.4 数据库连接耗尽

**排查流程**：
```
应用报错无法获取连接 → 查看数据库连接数 → SHOW STATUS LIKE 'Threads_connected'
→ 查看慢 SQL / 锁等待 → 查看连接池配置
```

**常见原因**：
- 慢 SQL 导致连接占用时间过长  
- 锁等待导致连接堆积  
- 连接池配置过小  
- 数据库 `max_connections` 过小

**解决**：
- 优化慢 SQL  
- 合理配置连接池（不超过 `max_connections` 的 80%）  
- 设置 `max_execution_time`

#### 25.5 大表 DDL 与 Online DDL

**风险**：传统 `ALTER TABLE` 会锁表；大表（千万级）可能耗时数小时。

**Online DDL**：
```sql
-- 在线添加索引，不阻塞读写
ALTER TABLE `order` ADD INDEX idx_user_id (user_id), ALGORITHM=INPLACE, LOCK=NONE;
```

**生产最佳实践**：使用 `pt-online-schema-change` 或 `gh-ost` 无阻塞变更。

### 26. 备份恢复体系

#### 26.1 备份类型与工具

| 类型 | 工具 | 特点 | 适用 |
|------|------|------|------|
| 逻辑全量 | `mysqldump` | 导出 SQL 文本，可读，速度慢 | 小库、跨版本迁移 |
| 物理全量 | `xtrabackup` / `mysqlbackup` | 物理文件拷贝，速度快，在线 | 大库生产备份 |
| 增量 | Binlog / xtrabackup | 只备份变更 | 减少备份时间和空间 |
| 快照 | 云盘快照 / LVM 快照 | 快速，依赖存储 | 云环境快速恢复 |

#### 26.2 PITR 时间点恢复

**恢复流程**：
```
恢复最近全量备份 → 应用增量备份 → 回放 Binlog 直到故障前时间点
```

**Binlog 回放**：
```bash
# 回放指定时间段的 binlog
mysqlbinlog --start-datetime="2025-01-01 00:00:00" \
            --stop-datetime="2025-01-02 12:00:00" \
            mysql-bin.000010 | mysql -u root -p
```

#### 26.3 备份策略与恢复演练

- 全量备份频率：每天或每周一次。  
- 增量备份：实时 Binlog 归档。  
- 备份保留：全量保留 2 周，Binlog 保留 7 天以上。  
- 定期恢复演练，确保备份可用。

#### 26.4 备份与恢复强化

##### Clone 插件备份

```sql
-- 克隆到本地目录
CLONE LOCAL DATA DIRECTORY = '/backup/clone_20240101';
```

##### 备份加密

xtrabackup 支持 `--encrypt=AES256 --encrypt-key-file`，保护备份文件安全。

##### PITR 自动化脚本

编写 shell 脚本：
1. 每周全量备份（xtrabackup）
2. 每日增量备份（xtrabackup --incremental）
3. 实时备份 binlog
4. 恢复时自动组合全量+增量+binlog

##### 误删除恢复工具

- **binlog2sql**：解析 binlog 生成回滚 SQL。
- **MyFlash**：美团开源的 binlog 回滚工具，速度快。

```bash
# 使用 binlog2sql 生成回滚语句
python binlog2sql.py -h127.0.0.1 -uroot -pxxx -dtest -tuser --start-file='mysql-bin.000010' --start-position=123 --stop-position=456 --flashback
```

### 27. 安全与运维

#### 27.1 权限管理

最小权限原则：
```sql
-- 创建应用专用账号，只授予必要权限
CREATE USER 'app_user'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON app_db.* TO 'app_user'@'%';
```

- 应用账号不要有 DDL 权限。  
- 生产环境禁止使用 root 直连。  
- 定期审计账号权限。

#### 27.2 数据脱敏与加密

- 敏感字段加密存储，查询时脱敏显示。  
- 使用 `AES_ENCRYPT` / 应用层加密。  
- 加密字段无法直接范围查询，需额外索引或哈希。  
- 启用 SSL/TLS 加密传输。

```sql
-- 脱敏示例：手机号中间四位用星号替代
SELECT CONCAT(LEFT(mobile,3), '****', RIGHT(mobile,4)) FROM user;
```

#### 27.3 SQL 审计

- 使用 MySQL Enterprise Audit 或 ProxySQL 记录 SQL。  
- 记录所有 DDL/DCL 和敏感 DML。  
- 定期分析审计日志，发现异常访问。

---

## 第九篇 架构师面试体系

### 28. 原理问题

#### 28.1 索引原理

**Q1：为什么用 B+ 树而不选 Hash、B 树、红黑树？**  
- Hash 不支持范围、排序、最左前缀。  
- B 树非叶子存储数据，扇出小，树高。  
- 红黑树二叉，树高过高。  
- B+ 树数据只存叶子，扇出大，树高低，范围查询高效。

**Q2：聚簇索引和二级索引存储有什么区别？**  
聚簇索引叶子节点存完整行，二级索引叶子节点存主键值。通过二级索引查询非索引列需要回表。

**Q3：为什么优化器选全表扫描？**  
**基础原因**：统计信息错误、回表成本高、选择性不足、成本模型。  
**深度分析**：
- 优化器通过 `mysql.innodb_index_stats` 中的 Cardinality 估算行数，如果该值因数据变更未更新，会误判。
- 对于二级索引，访问路径成本 = 索引范围扫描成本 + 回表成本（随机 IO）。若回表行数超过约 20%~30%，全表顺序扫描可能更优。
- 直方图缺失时，对倾斜列过滤率估算偏差大。
- `eq_range_index_dive_limit` 影响范围扫描的采样精度，超出后使用平均值估算。
- 可查看 `OPTIMIZER_TRACE` 确认具体成本对比，必要时用 `FORCE INDEX` 或调整统计信息。

#### 28.2 事务与 MVCC

**Q4：RR 级别下幻读如何解决？**  
MVCC 解决快照读，Next-Key Lock 解决当前读。

**Q5：MVCC 能彻底解决幻读吗？**  
不能，当前读需锁。

**Q6：长事务有什么危害？**  
Undo 膨胀、锁持有、主从延迟。

#### 28.3 日志系统

**Q7：Redo Log 和 Binlog 区别？**  
引擎层物理日志 vs Server 层逻辑日志；循环写 vs 追加写；崩溃恢复 vs 主从复制。

**Q8：为什么需要两阶段提交？**  
保证 Redo 和 Binlog 一致，避免主从数据不一致。

**Q9：Purge 线程的作用？**  
清理 Undo 和删除标记记录，释放空间。

#### 28.4 锁机制

**Q10：死锁如何排查和避免？**  
`SHOW ENGINE INNODB STATUS`，统一加锁顺序，缩短事务。

**Q11：锁兼容矩阵是怎样的？**  
|  | IS | IX | S | X |
|--|----|----|---|---|
| IS | ✅ | ✅ | ✅ | ❌ |
| IX | ✅ | ✅ | ❌ | ❌ |
| S  | ✅ | ❌ | ✅ | ❌ |
| X  | ❌ | ❌ | ❌ | ❌ |

Gap Lock 与 Gap Lock 之间兼容，Next-Key Lock = Record + Gap，兼容性取决于组合。

### 29. SQL 优化问题

#### 29.1 索引失效场景

**Q12：什么情况下索引失效？**  
列出 10 种场景（LIKE 前置、隐式转换、函数、运算、违反最左前缀、OR、NOT IN、IS NULL、字符集不一致、优化器选择）。

#### 29.2 慢 SQL 定位与优化

**Q13：如何定位慢 SQL？**  
慢日志、pt-query-digest、EXPLAIN、OPTIMIZER_TRACE。

**Q14：如何优化深分页？**  
游标分页、延迟关联。

#### 29.3 优化器选择错误分析

**Q15：如何判断优化器选择错误？**  
对比 `EXPLAIN` 中预估行数与实际行数，若差异大说明统计信息不准；可通过 `FORCE INDEX` 测试实际性能，必要时使用 `OPTIMIZER_TRACE` 查看优化过程。

### 30. 架构设计问题

#### 30.1 千万级订单表设计

- 按 `user_id` 水平拆分 64 片，订单号雪花 ID。  
- 状态机，事件驱动。  
- 创建订单和扣库存通过本地消息表保证最终一致。  
- 查询走分片键，覆盖索引。

#### 30.2 秒杀库存设计

- Redis 预扣减 + 异步落库 + 数据库兜底。  
- Lua 原子扣减，`count > 0` 条件更新。  
- 热点库存拆分。  
- 失败补偿和对账机制。

**全链路深度回答**：
1. **前端**：按钮防重复点击，验证码，限流。
2. **网关**：令牌桶限流，阻止大部分无效请求。
3. **Redis 预扣减**：将库存预热到 Redis，使用 Lua 脚本原子判断并扣减，返回结果。
4. **异步下单**：扣减成功后，发送 MQ 创建订单，异步更新数据库库存。
5. **数据库兜底**：订单表唯一约束（用户+商品）防止重复下单，库存表 `count > 0` 条件更新防止超卖。
6. **失败补偿**：Redis 成功但 DB 失败时，通过 MQ 重试、死信队列、补偿任务回滚 Redis 库存。
7. **对账**：定时对账 Redis 和数据库库存，修复差异。
8. **热点隔离**：库存分片或热点 key 单独缓存。

#### 30.3 缓存一致性方案

Cache Aside，先更新 DB 再删缓存，延迟双删或 Binlog 订阅。

#### 30.4 分布式事务选型

根据业务一致性要求：强一致选 XA，最终一致选本地消息表或 TCC。尽量通过架构设计避免分布式事务。

**补充**：
- Saga 模式适用于长事务补偿。
- TCC 需处理空回滚、幂等、悬挂。
- Seata AT 自动生成回滚 SQL，但性能有损耗。

#### 30.5 真实项目设计题

**订单系统**：按 `user_id` 分片，雪花 ID，本地消息表保证最终一致。  
**库存系统**：Redis 预扣减 + 异步落库，防超卖，失败补偿。  
**评论系统**：按内容 ID 分表，游标分页，冷热分离。

---
