# 🛠️ 快速查漏工具包（实战操作卡片）

## 工具一：Spring 官方文档（定位 API 契约）

**目标**：查明某个注解、类或方法的确切行为，不依赖二手博客。

- **精准定位**：在 Google 搜索 `"类名.方法名 spring docs"`（例如 `"JpaRepository.save spring docs"`），点击结果进入 `docs.spring.io` 下的 `api/` 路径，这是**最权威的 JavaDoc**。
- **必看信息**：进入文档后，视线按以下顺序扫描：
  1. **类顶部注释**：看这个类是干什么的。
  2. **`@Since` 标签**：确认该功能从哪个 Spring 版本引入，判断你的项目是否支持。
  3. **方法返回值**：看返回的是 `Optional<T>`、`T` 还是 `List<T>`，决定你是否需要判空。
- **查配置项**：如果想知道 `spring.jpa.hibernate.ddl-auto` 有哪些取值，直接在 Spring Boot 文档（Reference Doc）的 **“Appendix A. Common application properties”** 里按 `Ctrl+F` 搜索。

---

## 工具二：异常堆栈与搜索引擎（定位病根）

**目标**：从满屏红色报错中，3 秒内精准捞出真正原因。

- **截断包装，直取病灶**：Spring 的异常常有 3-4 层包装（`MethodArgumentNotValidException` -> `ConstraintViolationException`）。**不要看第一行**，直接滚到堆栈最底部，找第一个 **`Caused by: `**。
- **只看自家代码行**：在堆栈中部按 `Ctrl+F` 搜索你的**项目根包名**（如 `com.yourcompany`）。如果自家代码行出现在堆栈顶部，说明是**入参/校验错**；如果出现在底部，说明是**数据库/SQL 执行错**。
- **搜索引擎套路**：只复制 **`Caused by` 那一句 + 异常类名** 去 Google。搜索结果中，**优先打开 Stack Overflow 点赞数超过 10** 的链接，通常前 3 条结果里必有解决方案。

---

## 工具三：IntelliJ IDEA（透视代码血缘）

**目标**：不迷路，迅速看清类与方法的调用网络。

- **调用层级（最强杀招）**：光标放在**方法名**上，按 **`Ctrl + Alt + H`（Win）** / **`Control + Option + H`（Mac）**。
  - 点击树形结构左侧的 **展开箭头**，查看 **Caller（谁调用了我）** 和 **Callee（我调用了谁）**，这是追踪 `Controller -> Service -> Repository` 最快的方式。
- **查找用法（分类过滤）**：光标放在**变量/方法**上，按 **`Alt + F7`（Win）** / **`Option + F7`（Mac）**。弹出窗格后，点击顶部工具栏的**分类图标**：
  - 只勾选 **Write**：看哪些地方修改了这个值。
  - 只勾选 **Read**：看哪些地方读取了这个值。
- **类图去噪**：右键类名 -> **Diagrams** -> **Show Diagram**。
  - **立刻按空格键**（展开所有父接口）。
  - 按住 `Ctrl` 多选，将 `Object`、`Serializable` 等 JDK 自带类按 **Delete** 键删除，只保留**项目自身实体类**的继承与关联关系。

---

### 💡 三连击实战演练（查错标准流程）

当你遇到一个 `500` 错误时，按这个节奏走：

1. **看堆栈（工具二）** -> 搜项目包名，找到发生错误的代码行（例如 `DeviceServiceImpl.java:45`）。
2. **查调用（工具三）** -> 在该行代码上按 `Ctrl+Alt+H`，看是谁传了错误参数进来（是 Controller 还是 Feign 调用）。
3. **对契约（工具一）** -> 怀疑是 JPA 方法写错了，立刻 Google `"JpaRepository 方法名 spring docs"`，核对方法签名是否正确。

---
