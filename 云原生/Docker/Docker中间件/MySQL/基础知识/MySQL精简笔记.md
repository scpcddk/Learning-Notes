# MySQL精简笔记

## 快速打开（连接MySQL）

**语法**：
```bash
mysql -h IP地址 -P 端口 -u 用户名 -p
```
**事例**：
```bash
mysql -u root -p
# 输入密码后进入 mysql> 交互终端
```

---

## SQL语言基础

### 分类

**语法**：
| 分类 | 对应命令 | 作用 |
|------|----------|------|
| **DDL** | `CREATE`, `DROP`, `ALTER`, `TRUNCATE` | 操作**表结构/库结构** |
| **DML** | `INSERT`, `UPDATE`, `DELETE` | 操作**表里的数据行** |
| **DQL** | `SELECT` | 查询数据 |
| **DCL** | `GRANT`, `REVOKE` | 管理**权限/用户** |

**事例**：
- DDL：`CREATE TABLE t_order (...)` —— 建表
- DML：`INSERT INTO t_order VALUES (...)` —— 插数据
- DQL：`SELECT * FROM t_order` —— 查数据
- DCL：`GRANT SELECT ON *.* TO 'user'@'%'` —— 授权

### 库操作

**语法**：
```sql
-- 创建数据库（指定字符集）
CREATE DATABASE IF NOT EXISTS 库名 CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;

-- 切换数据库
USE 库名;

-- 查看所有数据库 / 查看当前库所有表
SHOW DATABASES;
SHOW TABLES;

-- 删除数据库（危险）
DROP DATABASE IF EXISTS 库名;
```
**事例**：
```sql
CREATE DATABASE IF NOT EXISTS `order_db` CHARACTER SET utf8mb4;
USE order_db;
SHOW TABLES;
```

### 表操作

**语法**：
```sql
-- 创建表（标准模板）
CREATE TABLE IF NOT EXISTS 表名 (
    列名 数据类型 约束 COMMENT '注释',
    PRIMARY KEY (列名),
    KEY 索引名 (列名)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='表注释';

-- 查看表结构
DESC 表名;
SHOW CREATE TABLE 表名\G;

-- 修改表结构（ALTER）
ALTER TABLE 表名 ADD COLUMN 列名 数据类型 COMMENT '注释';
ALTER TABLE 表名 MODIFY COLUMN 列名 新数据类型;
ALTER TABLE 表名 CHANGE COLUMN 旧列名 新列名 数据类型;

-- 重命名表 / 删除表
RENAME TABLE 旧表名 TO 新表名;
DROP TABLE IF EXISTS 表名;
```
**事例**：
```sql
CREATE TABLE IF NOT EXISTS `t_order` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `t_order` ADD COLUMN `amount` DECIMAL(10,2);
DESC t_order;
```

---

## 数据操作（DML）

### 增（INSERT）

**语法**：
```sql
-- 标准插入（必须指定列名）
INSERT INTO 表名 (列名1, 列名2) VALUES (值1, 值2);

-- 批量插入（高性能，建议500~1000行/批）
INSERT INTO 表名 (列名1, 列名2) VALUES (值1, 值2), (值3, 值4);

-- 插入或更新（存在则改）
INSERT INTO 表名 (列名1, 列名2) VALUES (值1, 值2)
ON DUPLICATE KEY UPDATE 列名1 = VALUES(列名1);
```
**事例**：
```sql
INSERT INTO `t_order` (`user_id`, `amount`) VALUES (1001, 99.50);
INSERT INTO `t_order` (`user_id`, `amount`) VALUES (1002, 50), (1003, 30);
```

### 删（DELETE）

**语法**：
```sql
-- 标准删除（必须带条件）
DELETE FROM 表名 WHERE 条件;

-- 生产标准写法（WHERE + LIMIT 双保险，防锁表）
DELETE FROM 表名 WHERE 条件 LIMIT 100;
```
**事例**：
```sql
DELETE FROM `t_order` WHERE `id` = 1;
DELETE FROM `t_order` WHERE `status` = 0 LIMIT 100;   -- 分批删除
```

### 改（UPDATE）

**语法**：
```sql
-- 标准更新（带WHERE条件）
UPDATE 表名 SET 列名 = 新值 WHERE 条件;

-- 生产写法（LIMIT 1 防手滑）
UPDATE 表名 SET 列名 = 新值 WHERE 条件 LIMIT 1;

-- 原子计算（无需先查后算，避免并发覆盖）
UPDATE 表名 SET 列名 = 列名 + 数值 WHERE 条件;

-- 重置为默认值
UPDATE 表名 SET 列名 = DEFAULT WHERE 条件;
```
**事例**：
```sql
UPDATE `t_order` SET `status` = 1 WHERE `id` = 2 LIMIT 1;
UPDATE `t_order` SET `amount` = `amount` + 10 WHERE `id` = 2;   -- 原子累加
```

### 查（SELECT）

**语法**：
```sql
-- 基础查询（严禁使用 SELECT *）
SELECT 列名1, 列名2 FROM 表名 WHERE 条件;

-- 查询 + 排序 + 分页（必须加 LIMIT）
SELECT 列名1, 列名2 FROM 表名 WHERE 条件 ORDER BY 排序列 LIMIT 行数;

-- 统计查询（COUNT）
SELECT COUNT(*) FROM 表名 WHERE 条件;
```
**事例**：
```sql
SELECT `id`, `user_id`, `amount` FROM `t_order` WHERE `user_id` = 1001;
SELECT `id`, `amount` FROM `t_order` WHERE `status` = 0 ORDER BY `id` DESC LIMIT 20;
SELECT COUNT(*) FROM `t_order` WHERE `status` = 1;
```

### 导入（LOAD DATA）

**语法**：
```sql
-- 从CSV文件批量导入（比INSERT快20倍以上）
LOAD DATA INFILE '/绝对路径/文件名.csv' 
INTO TABLE 表名 
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
(列名1, 列名2, ...);

-- 导入前调优（千万级数据提速5~10倍）
SET autocommit = 0;
SET unique_checks = 0;
SET foreign_key_checks = 0;
LOAD DATA INFILE ...;
COMMIT;
```
**事例**：
```sql
LOAD DATA INFILE '/tmp/order_export.csv'
INTO TABLE `t_order`
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
(`id`, `user_id`, `amount`);
```

### 导出（SELECT INTO OUTFILE）

**语法**：
```sql
-- 导出为CSV文件（比mysqldump快10倍以上）
SELECT 列名1, 列名2
INTO OUTFILE '/绝对路径/文件名.csv'
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
FROM 表名 WHERE 条件;
```
**事例**：
```sql
SELECT `id`, `user_id`, `amount`, `create_time`
INTO OUTFILE '/tmp/order_export.csv'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
FROM `t_order` WHERE `create_time` >= '2024-01-01';
```

---

## 常用语句（条件筛选）

### IN

**语法**：
```sql
-- 判断列值是否在列表/子查询中
WHERE 列名 IN (值A, 值B, 值C);
WHERE 列名 IN (子查询);
```
**事例**：
```sql
SELECT * FROM `t_order` WHERE `status` IN (0, 1, 2);
-- ⚠️ 注意：NOT IN 遇到 NULL 会返回空集，优先用 NOT EXISTS
```

### BETWEEN

**语法**：
```sql
-- 判断列值是否在闭区间内（等价于 >= 和 <=）
WHERE 列名 BETWEEN 下限 AND 上限;
```
**事例**：
```sql
SELECT * FROM `t_order` WHERE `amount` BETWEEN 100 AND 500;
-- ⚠️ 日期范围建议改用 >= 和 < 避免漏秒：WHERE create_time >= '2024-01-01' AND create_time < '2024-01-03'
```

### LIKE

**语法**：
```sql
-- 模糊匹配：%代表任意多个字符，_代表单个字符
WHERE 列名 LIKE '模式';
```
**事例**：
```sql
SELECT * FROM `t_user` WHERE `name` LIKE '张%';   -- 匹配"张三"、"张三丰"
-- ⚠️ %放在开头（如 '%张'）会导致索引失效，必须查后缀时改用ES或反转字段
```

### REGEXP

**语法**：
```sql
-- 基于正则表达式进行复杂匹配（无法使用索引，仅限离线场景）
WHERE 列名 REGEXP '正则模式';
```
**事例**：
```sql
SELECT * FROM `t_user` WHERE `mobile` REGEXP '^13[89][0-9]{8}$';   -- 匹配138/139开头的手机号
-- ⚠️ 线上接口禁止使用，只能用于离线统计或临时排查
```

---

## 分组与聚合

### ORDERED BY

**语法**：
`ORDER BY 排序列名 DESC(降序)/ASC(升序) `

**事例**：

```sql
SELECT `id`, `amount` FROM `t_order` 
WHERE `status` = 0 
ORDER BY `id` DESC 
LIMIT 20;
```

### 聚合函数

**语法**：
| 函数 | 作用 |
|------|------|
| `COUNT(*)` | 统计总行数（含NULL） |
| `COUNT(列名)` | 统计该列非NULL的行数 |
| `SUM(列名)` | 求和（忽略NULL） |
| `AVG(列名)` | 平均值（忽略NULL） |
| `MAX(列名)` / `MIN(列名)` | 最大/最小值 |
| `GROUP_CONCAT(列名)` | 将分组内值拼接成字符串 |

**事例**：
```sql
SELECT COUNT(*), SUM(amount), AVG(amount), MAX(amount)
FROM `t_order` WHERE `status` = 1;
```

### GROUP BY

**语法**：
```sql
SELECT 分组列, 聚合函数(列名) FROM 表名 WHERE 条件 GROUP BY 分组列;
```
**事例**：
```sql
SELECT user_id, COUNT(*) AS order_count
FROM `t_order` WHERE `status` = 1
GROUP BY user_id;
```

### HAVING

**语法**：
```sql
-- 分组后过滤（WHERE在分组前，HAVING在分组后）
SELECT 分组列, 聚合函数(列名) 
FROM 表名 
GROUP BY 分组列 
HAVING 聚合函数(列名) > 值;
```
**事例**：
```sql
SELECT user_id, SUM(amount) AS total
FROM `t_order` WHERE `status` = 1
GROUP BY user_id
HAVING SUM(amount) > 1000;   -- 只保留总额大于1000的用户
```

---

## 查询进阶

### DISTINCT

**语法**：
```sql
-- 去除所有选定列组合完全重复的行
SELECT DISTINCT 列名1, 列名2 FROM 表名 WHERE 条件;
```
**事例**：
```sql
SELECT DISTINCT user_id FROM t_order;   -- 查询有哪些不同的用户ID
```

### UNION / UNION ALL

**语法**：
```sql
-- 纵向拼接两个查询结果（字段数必须一致）
SELECT 列名1, 列名2 FROM 表1
UNION [ALL]
SELECT 列名1, 列名2 FROM 表2;

-- UNION：去重 + 排序（代价高）
-- UNION ALL：保留全部行，不去重（性能好，推荐）
```
**事例**：
```sql
SELECT user_id FROM t_order
UNION ALL
SELECT user_id FROM t_member;   -- 所有用户ID，重复保留
```

### INTERSECT（交集，MySQL 8.0.31+）

**语法**：
```sql
-- 返回两个查询结果中共同存在的行
SELECT 列名 FROM 表1
INTERSECT [ALL]
SELECT 列名 FROM 表2;
```
**事例**：
```sql
SELECT user_id FROM t_vip
INTERSECT
SELECT user_id FROM t_order;   -- 既是VIP又有过下单的用户

-- MySQL 5.7替代写法：
SELECT DISTINCT v.user_id FROM t_vip v
INNER JOIN t_order o ON v.user_id = o.user_id;
```

---

## 子查询

**语法**：

```sql
-- 子查询：嵌套在另一个SQL中的SELECT（用在WHERE / FROM / SELECT 子句中）
WHERE 列名 = (SELECT ...);
WHERE 列名 IN (SELECT ...);
WHERE EXISTS (SELECT 1 FROM ... WHERE 关联条件);
```
**事例**：
```sql
-- 查询下单金额最大的订单所属用户
SELECT user_id FROM t_order 
WHERE amount = (SELECT MAX(amount) FROM t_order);
```

## 表关联（JOIN）

**语法**：

```sql
-- 标准JOIN语法
SELECT 表A.列名, 表B.列名
FROM 表A
[INNER | LEFT] JOIN 表B ON 表A.关联列 = 表B.关联列
WHERE 过滤条件;

-- INNER JOIN：只返回匹配成功的行
-- LEFT JOIN：返回左表全部 + 右表匹配字段（无匹配补NULL）
```

**事例**：

```sql
-- 查询订单及用户昵称
SELECT o.id, u.nickname
FROM `order` o
LEFT JOIN `user` u ON o.user_id = u.id
WHERE o.status = 'PAID';

-- ⚠️ 被驱动表（LEFT JOIN的右表）关联列必须有索引，否则全表扫描
```

---

## 索引

### 索引的创建

**语法**：

```sql
-- 普通索引
CREATE INDEX 索引名 ON 表名 (列名);
ALTER TABLE 表名 ADD INDEX 索引名 (列名);

-- 唯一索引
CREATE UNIQUE INDEX 索引名 ON 表名 (列名);

-- 联合索引
CREATE INDEX 索引名 ON 表名 (列名1, 列名2);

-- 查看索引
SHOW INDEX FROM 表名;

-- 删除索引
DROP INDEX 索引名 ON 表名;
```
**事例**：
```sql
CREATE INDEX idx_user_id ON t_order (user_id);
CREATE UNIQUE INDEX uk_mobile ON t_user (mobile);
SHOW INDEX FROM t_order;
```

### 索引的使用

**语法规则**：
- **最左前缀原则**：联合索引 `(a, b, c)` 能命中 `a`、`a,b`、`a,b,c`，但查 `b` 或 `c` 走不了索引。
- **索引失效场景**：
  - 对索引列使用函数（如 `DATE(create_time)`）
  - 隐式类型转换（如 `varchar` 列和数字比较）
  - `LIKE '%xxx'`（通配符在开头）

**事例**：
```sql
-- ✅ 能走索引：name LIKE '张%'
-- ❌ 不走索引：name LIKE '%张'  或  WHERE DATE(create_time) = '2024-01-01'
-- ✅ 联合索引 idx_user_status (user_id, status) 命中：
WHERE user_id = 1001 AND status = 1;
-- ❌ 联合索引不命中：
WHERE status = 1;   -- 跳过了最左列 user_id
```

### 索引的作用

**核心作用**：
- **加速查询**：B+树结构将查询时间复杂度从 O(n) 降到 O(log n)，避免全表扫描。
- **排序加速**：索引本身有序，`ORDER BY` 可直接利用索引避免 `filesort`。
- **唯一约束**：唯一索引保证数据唯一性。
- **覆盖索引**：查询列全部在索引中时，无需回表（`Using index`）。

**代价**：
- 占用磁盘空间（额外存储B+树）。
- 写入变慢（`INSERT`/`UPDATE`/`DELETE` 需同步维护所有索引）。

**事例**：
```sql
-- 以下查询走 idx_user_id 索引，且因为只查 id 和 user_id，是覆盖索引（无须回表）
SELECT id, user_id FROM t_order WHERE user_id = 1001;
```

---

## 视图

**语法**：
```sql
-- 创建视图（虚拟表，封装SELECT语句）
CREATE VIEW 视图名 AS
SELECT 列名1, 列名2 FROM 表名 WHERE 条件;

-- 使用视图（当成表查）
SELECT * FROM 视图名 WHERE 条件;

-- 查看视图定义 / 删除视图
SHOW CREATE VIEW 视图名;
DROP VIEW 视图名;
```
**事例**：
```sql
-- 创建一个安全视图：只暴露脱敏后的用户信息
CREATE VIEW v_user_safe AS
SELECT id, nickname, LEFT(mobile, 3) AS mobile_prefix
FROM user WHERE status = 1;

-- 查询视图
SELECT * FROM v_user_safe;
```

---
