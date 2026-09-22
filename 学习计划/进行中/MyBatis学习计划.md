# MyBatis 学习计划

**路线**：
**“MyBatis → MyBatis-Plus → Spring Boot → 项目 → 深入原理”**

每天约 **1.5 小时**，目标是 **2027 年前 MyBatis 达到 B（能写、能读、能排查）**，未来再进入 C（原理/源码）。

---

# 一、现在：MyBatis 原生

**目标：5～6 周，约 38～45 小时**

### 第 1 阶段：认识 MyBatis

* [x] MyBatis 是什么
* [x] MyBatis 解决什么问题
* [x] JDBC 与 MyBatis
* [x] MyBatis 整体执行流程
* [x] Mapper 是什么
* [x] Mapper XML 是什么
* [x] Mapper 接口与 XML 如何对应
* [x] 第一个 MyBatis 项目

### 第 2 阶段：CRUD

* [x] `select`
* [x] `insert`
* [x] `update`
* [x] `delete`
* [x] 单条查询
* [x] 多条查询
* [x] 主键回填
* [x] 自增主键

### 第 3 阶段：参数

* [x] 单参数
* [x] 多参数
* [x] `@Param`
* [ ] JavaBean 参数
* [x] `#{}`
* [x] `${}`
* [x] `#{}` 与 `${}` 的区别
* [ ] SQL 注入风险

### 第 4 阶段：结果映射

* [x] `resultType`
* [x] `resultMap`
* [x] 字段 → Java 属性
* [x] 驼峰映射
* [ ] 多种结果映射方式
* [ ] 常见映射错误

### 第 5 阶段：动态 SQL

这是 **MyBatis 最重要的部分之一**。

* [x] `<if>`
* [x] `<where>`
* [x] `<set>`
* [x] `<trim>`
* [x] `<choose>`
* [x] `<when>`
* [x] `<otherwise>`
* [x] `<foreach>`
* [x] 动态查询
* [x] 动态更新
* [x] `IN`
* [x] 批量删除
* [x] 批量插入

### 第 6 阶段：多表映射

* [x] JOIN 与 MyBatis
* [x] `association`
* [x] 一对一
* [x] `collection`
* [x] 一对多
* [x] 多对多
* [x] 嵌套查询
* [x] 嵌套结果

### 第 7 阶段：Spring Boot 整合

* [ ] MyBatis-Spring
* [ ] MyBatis-Spring-Boot-Starter
* [ ] `@Mapper`
* [ ] `@MapperScan`
* [ ] `application.yml`
* [ ] Mapper 扫描
* [ ] XML 加载
* [ ] Service 调用 Mapper
* [ ] Controller → Service → Mapper

### 第 8 阶段：常见问题

自己能够排查：

* [ ] Mapper 找不到
* [ ] XML 找不到
* [ ] namespace 错误
* [ ] statement 找不到
* [ ] 参数找不到
* [ ] `@Param` 问题
* [ ] resultType / resultMap 问题
* [ ] 字段映射问题
* [ ] 动态 SQL 问题
* [ ] 数据库连接问题

---

# 二、MyBatis 第一轮实战

**目标：约 1～2 周**

学完上面不要马上去看源码。

自己做一个小项目。

例如：

```text
学生管理系统
```

实现：

```text
学生
 ├── 新增
 ├── 删除
 ├── 修改
 ├── 根据 ID 查询
 ├── 条件查询
 ├── 分页查询
 ├── 批量删除
 └── 多表查询
```

要求：

> **尽量自己写，而不是复制教程。**

做到这里，你的 MyBatis 就应该从：

```text
“看过一个 1 小时教程”
```

变成：

```text
“我可以独立使用 MyBatis”
```

---

# 三、MyBatis 进阶

**目标：约 1～2 周**

这部分是为了达到你的 **B 水平**。

* [ ] `SqlSessionFactory`
* [ ] `SqlSession`
* [ ] MyBatis 生命周期
* [ ] 一级缓存
* [ ] 二级缓存
* [ ] TypeHandler
* [ ] 自定义 TypeHandler
* [ ] MyBatis 事务
* [ ] Spring `@Transactional`
* [ ] 分页
* [ ] MyBatis 插件基本概念
* [ ] 常见性能问题
* [ ] 常见设计问题

这里不要求源码级理解。

---

# 四、MyBatis-Plus

**目标：约 3～7 天**

这时候再学 MP 会非常舒服。

### 基础

* [ ] MyBatis-Plus 是什么
* [ ] MyBatis 与 MP 的关系
* [ ] MP 项目配置
* [ ] `BaseMapper`
* [ ] 通用 CRUD
* [ ] `IService`
* [ ] Service 层常用方法

### 条件构造器

* [ ] `QueryWrapper`
* [ ] `LambdaQueryWrapper`
* [ ] `UpdateWrapper`
* [ ] `LambdaUpdateWrapper`

### 常用功能

* [ ] 条件查询
* [ ] 条件更新
* [ ] 批量操作
* [ ] 分页
* [ ] 自动填充
* [ ] 逻辑删除
* [ ] 乐观锁基本概念

### 最重要

学完以后要能够看懂：

```text
原生 MyBatis 项目
+
MyBatis-Plus 项目
```

而不是只会 MP。

---

# 五、Spring Boot 系统复习

这个实际上是未来比较重要的一块。

因为你现在：

```text
Spring MVC     2/3
Spring IOC     1/3
Spring AOP     1/3
Spring Boot    1/3
```

所以 MyBatis 学完后，建议系统补。

### Spring 核心

* [x] IOC
* [ ] DI
* [x] Bean
* [x] Bean 生命周期
* [ ] Bean 作用域
* [ ] 自动装配
* [x] `@Component`
* [x] `@Service`
* [x] `@Repository`
* [x] `@Autowired`
* [x] 构造器注入

### Spring AOP

* [x] AOP 是什么
* [x] 切面
* [x] JoinPoint
* [x] Pointcut
* [ ] Advice
* [ ] Proxy
* [x] 实际应用场景

重点理解：

```text
为什么 Spring 能“在不修改业务代码的情况下”
给方法增加事务、日志等功能？
```

### Spring Boot

* [ ] 自动配置
* [ ] Starter
* [x] 配置文件
* [ ] 配置绑定
* [ ] Bean 管理
* [ ] Controller
* [ ] Service
* [ ] Repository / Mapper
* [ ] 异常处理
* [ ] 日志
* [ ] 参数校验

---

# 六、Spring Boot + MyBatis 综合项目

**这是一个非常重要的节点。**

不要继续无止境看教程。

做一个真正属于自己的项目。

例如：

```text
用户
订单
商品
分类
```

形成：

```text
Controller
      ↓
Service
      ↓
Mapper
      ↓
MyBatis
      ↓
MySQL
```

至少实现：

* [ ] 用户 CRUD
* [ ] 商品 CRUD
* [ ] 条件查询
* [ ] 分页
* [ ] 多表查询
* [ ] 动态 SQL
* [ ] 事务
* [ ] 异常处理
* [ ] 参数校验
* [ ] 统一返回
* [ ] 日志
* [ ] 数据库设计

做到这里，你的目标就从：

> “学习 MyBatis”

变成：

> **“能够用 Spring Boot + MyBatis 做后端功能。”**

---

# 七、2027 年：结合学校数据库课程重新巩固

你 2027 年春季有数据库课程，这反而是一个优势。

不要把它当成重复学习。

可以形成：

```text
现在
MySQL 已掌握
      ↓
MyBatis
      ↓
Spring Boot
      ↓
项目实践
      ↓
2027 春季数据库课程
      ↓
重新巩固数据库原理
      ↓
把理论 ↔ 实际项目联系起来
```

重点重新建立：

* [ ] SQL 与执行计划
* [ ] 索引
* [ ] 事务
* [ ] 隔离级别
* [ ] MVCC
* [ ] 锁
* [ ] 数据库设计
* [ ] 范式
* [ ] 性能优化

你现在已经学过这些，所以届时重点应该变成：

> **“这些数据库理论，在 MyBatis / Spring Boot 项目里到底什么时候体现出来？”**

---

# 八、之后：MyBatis C 级别

这个阶段**不要现在学**。

等你已经实际使用 MyBatis 一段时间以后再进入。

### 核心源码结构

```text
SqlSessionFactory
        ↓
    SqlSession
        ↓
    Executor
        ↓
StatementHandler
        ↓
ParameterHandler
        ↓
JDBC
        ↓
MySQL
        ↓
ResultSetHandler
        ↓
Java对象
```

学习：

* [ ] Configuration
* [ ] SqlSessionFactory
* [ ] SqlSession
* [ ] MappedStatement
* [ ] Executor
* [ ] StatementHandler
* [ ] ParameterHandler
* [ ] ResultSetHandler
* [ ] TypeHandler
* [ ] Plugin / Interceptor
* [ ] 一级缓存源码
* [ ] 二级缓存机制
* [ ] MyBatis 动态 SQL 内部实现

然后再：

* [ ] 阅读 MyBatis 源码
* [ ] Debug MyBatis 执行过程
* [ ] 理解代理 Mapper 的实现
* [ ] 理解 SQL 执行链
* [ ] 理解插件机制

---

# 九、最终路线

把整个未来压缩成一张图，就是：

```text
                    现在
                     │
                     ▼
              ┌─────────────┐
              │   MyBatis   │
              │   5～6周     │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ MyBatis实战 │
              │   1～2周     │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ MyBatis-Plus│
              │    3～7天    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ Spring Boot │
              │    系统复习   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ 后端项目实战 │
              └──────┬──────┘
                     │
                     ▼
               2027 春季
                     │
                     ▼
              ┌─────────────┐
              │  数据库课程  │
              │ 理论再次巩固 │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ MyBatis C级  │
              │ 原理 + 源码  │
              └─────────────┘
```

### 按优先级来看

**现在最重要：**

> **MyBatis → Spring Boot → 项目**

**辅助补齐：**

> Java 集合 → Lambda / Stream → IOC / AOP

**以后再深入：**

> MyBatis 源码 → Spring 源码 → 数据库底层

这样安排比较符合你现在的实际情况：**MySQL 已经不是瓶颈，真正需要把“会看”转化成“会写”的，是 Java + Spring Boot + MyBatis 这一整条链。**

---
