# JSON 笔记

**阅读导航**：[写法与类型](#2-json-语法规则) · [JavaScript 解析](#6-json-常用方法javascript-环境) · [HTTP 接口](#7-json-工具与使用场景) · [Spring Boot](#9-javaspring-中的-json) · [JSON Schema](#10-json-schema) · [订单接口示例](#11-业务接口示例订单详情)

## 1. 什么是 JSON

**JSON** 全称 **JavaScript Object Notation**，是用于数据交换的文本格式。不同语言可以用同一种 JSON 表示数据，再解析为各自的本地值。常见用途有 HTTP 请求与响应、配置文件、日志和本地存储。

---

## 2. JSON 语法规则

1. 对象的成员由字符串键和对应的值组成，键和值之间使用冒号 `:`
2. 对象的成员之间、数组的元素之间使用逗号 `,` 分隔
3. **花括号 `{}` 保存对象**（无序的键值对集合）
4. **方括号 `[]` 保存数组**（有序的值的集合）
5. **键和字符串值都用英文双引号 `"` 包裹**
6. 值的类型必须是合法的 JSON 数据类型（见下节）
7. 不支持注释和尾随逗号
8. 顶层可以是任意合法 JSON 值。例如 `42`、`"hello"`、`true` 都是合法 JSON 文本。接口可以额外要求顶层为对象。
9. 跨系统交换 JSON 文本使用 UTF-8。[RFC 8259 第 8.1 节](https://www.rfc-editor.org/rfc/rfc8259.html#section-8.1)

---

## 3. JSON 数据类型

JSON 支持以下 6 种数据类型：

| 类型 | 说明 | 示例 |
| ------------ | -------------------------------------------------------------- | -------------------------- |
| **字符串** | 必须使用双引号，支持转义字符（`\"`, `\\`, `\/`, `\n` 等） | `"hello"`, `"a\"b"` |
| **数字** | 十进制数，可含小数和指数部分。解析后的类型和精度由实现决定 | `42`, `-3.14`, `1.0e10` |
| **布尔值** | `true` 或 `false` | `true`, `false` |
| **null** | 表示空值 | `null` |
| **对象** | 无序的键/值对集合，键必须为字符串，值可以是**任意合法类型** | `{"name":"Alice","age":30}` |
| **数组** | 有序的值的集合，值可以是**任意合法类型** | `[1, "text", null, true]` |

### 3.1 对象与数组

| 对比 | 对象 | 数组 |
|---|---|---|
| 用途 | 用字段名描述一条记录，如订单 | 表达一组有顺序的数据，如订单明细 |
| 示例 | `{"name":"Tom","age":20}` | `["Python","Java","MySQL"]` |
| 解码后取值 | 按键，如 `student.name` | 按下标，如 `skills[0]` |
| 空容器 | `{}` | `[]` |

对象成员名应保持唯一，避免依赖成员顺序或解析器对重复键的处理。JavaScript 会保留重复键的最后一个值。数组允许混合类型，例如 `["Python", 20, true, null]`。接口仍可约定所有元素都必须是字符串，或都遵守同一个对象结构。[RFC 8259 第 4–5 节](https://www.rfc-editor.org/rfc/rfc8259.html#section-4) · [ECMAScript JSON.parse](https://tc39.es/ecma262/multipage/structured-data.html#sec-json.parse)

### 3.2 字符串与转义

空字符串 `""` 是合法的 JSON 值。`"20"`、`"true"` 解码后仍是字符串。数值 `20` 和布尔值 `true` 各自有不同的类型。

| JSON 文本写法 | 解码后的字符 |
|---|---|
| `\"` | 双引号 |
| `\\` | 反斜杠 |
| `\n` | 换行 |
| `\t` | 制表符 |
| `\uXXXX` | 四位十六进制数表示的 Unicode 编码单元 |

> [!example] 文本字段包含引号和换行
> ```json
> {"content":"他说：\"你好\"\n接着介绍 Python。"}
> ```
>
> 解析后 `content` 是两行文本，引号留在第一行中。

### 3.3 数字写法与解码类型

| 写法 | 说明 |
|---|---|
| `20`、`-20`、`0`、`0.5` | 合法的整数、负数、零或小数 |
| `1.5e3`、`1e+3` | 合法的指数写法，值分别为 1500 和 1000 |
| `020`、`+20`、`.5` | 非法写法。整数部分禁止多余的前导零，开头不能用 `+`，小数点前需要数字 |
| `NaN`、`Infinity`、`0x10` | 不属于标准 JSON 数字 |

JavaScript 的 `JSON.parse()` 把 JSON 数字解析为 `number`。Python 的 `json.loads()` 默认按是否含小数点或指数得到 `int` 或 `float`。[RFC 8259 第 6 节](https://www.rfc-editor.org/rfc/rfc8259.html#section-6) · [ECMAScript JSON.parse](https://tc39.es/ecma262/multipage/structured-data.html#sec-json.parse) · [Python 解析与 AI 应用示例](../../AI/基础知识/AI%20原理与应用开发笔记.md#18-jsonpython-对象与嵌套提取)

数值写法合法仍可能超出目标语言的表示范围。例如 `JSON.parse("1e400")` 返回 `Infinity`。需要有限数值时用 `Number.isFinite()`，需要精确表示的 JavaScript 整数时用 `Number.isSafeInteger()` 检查解码结果，并在接口契约中约定范围。

### 3.4 布尔值与条件判断

JSON 布尔值只有小写的 `true` 和 `false`。

| JSON 值 | JavaScript 解码结果 | Python 解码结果 |
|---|---|---|
| `true` | 布尔值 `true` | `True` |
| `false` | 布尔值 `false` | `False` |
| `"false"` | 字符串 `"false"` | 字符串 `"false"` |

> [!warning] 布尔字段先检查类型
> 非空字符串 `"false"` 在 JavaScript 和 Python 的条件判断中都会被当作真。读取开关字段时，JavaScript 可用 `typeof value === "boolean"`，Python 可用 `isinstance(value, bool)` 检查类型。

### 3.5 null、缺失字段与空值

| JSON 文本 | 含义 | JavaScript 取值 |
|---|---|---|
| `{"value":null}` | 字段存在，显式为空 | `null` |
| `{}` | 字段缺失 | 访问普通缺失属性得到 `undefined` |
| `{"value":""}` | 字段存在，是空字符串 | `""` |
| `{"value":[]}` | 字段存在，是空数组 | `[]` |

`undefined` 不能写进 JSON 文本。需要区分显式 `null` 和字段缺失时，用 `Object.hasOwn(data, "value")` 判断键是否存在。需要为两者提供同一个默认值时，可用 `data.value ?? fallback`，它会保留 `0`、`false` 和 `""`。

---

## 4. JSON 示例

### 4.1 有效 JSON

```json
{
  "name": "John Doe",
  "age": 29,
  "isStudent": false,
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "zip": "12345"
  },
  "phoneNumbers": ["+1234567890", "+9876543210"],
  "spouse": null
}
```

---

### 4.2 常见语法错误

| 错误写法 | 改正 |
|---|---|
| `{name:"John"}`、`{'name':'John'}` | 键和字符串值都用双引号，写成 `{"name":"John"}` |
| `{"text":"He said "Hi""}` | 转义内部引号，写成 `{"text":"He said \"Hi\""}` |
| `["Python" "Java"]`、`["Python","Java",]` | 只在相邻元素之间加逗号，写成 `["Python","Java"]` |
| `{"score":NaN}`、`{"hobby":undefined}` | 按契约使用合法值，允许空值时可用 `null`，允许缺失时可省略字段 |
| `{"date":new Date()}` | 用约定的字符串表示时间，如 `{"date":"2026-11-24T08:30:00Z"}` |
| `{"name":"John" /* 用户名 */}` | 注释放在文档或代码里，JSON 中删除注释 |

---

## 5. JSON 与 JavaScript 对象的区别

| 特性 | JSON | JavaScript 对象 |
| -------------------- | ----------------------------------- | ------------------------------ |
| 键的引号 | 必须用双引号 | 在对象字面量中，标识符形式的键可以省略引号。也支持字符串和计算属性名 |
| 字符串界定符 | 必须用双引号 | 单引号或双引号均可 |
| 值的类型 | 对象、数组、字符串、数字、布尔值和 `null` | 属性还可以存放函数、`undefined`、`Date` 等 JavaScript 值 |
| 注释 | 不允许 | 允许 |
| 尾随逗号 | 不允许 | 允许（ES5+） |
| 原型 | JSON 文本不表达原型关系 | 普通对象有原型，也可以创建原型为 `null` 的对象 |
| 用途 | 数据交换 | 程序内数据结构 |

**相互转换：**

- `JSON.parse(jsonString)` → 将 JSON 文本解析为对应的 JavaScript 值，不一定是对象。
- `JSON.stringify(value)` → 将可序列化的 JavaScript 值转换为 JSON 文本。特殊值的处理见[第 6.2 节](#62-jsonstringify)。

---

## 6. **JSON 常用方法**（JavaScript 环境）

### 6.1 `JSON.parse()`

```js
const jsonStr = '{"name":"Alice","scores":[95,87]}';
const obj = JSON.parse(jsonStr);
console.log(obj.name);       // "Alice"
console.log(obj.scores[0]);  // 95
```

解析非法 JSON 时会抛出 `SyntaxError`。可选的 `reviver(key, value)` 用于转换解析结果，返回 `undefined` 会移除对应成员。输入是否符合接口契约，应在解析后校验。[ECMAScript JSON.parse](https://tc39.es/ecma262/multipage/structured-data.html#sec-json.parse)

---

### 6.2 `JSON.stringify()`

```js
const data = {
  name: "Bob",
  age: 25,
  active: true,
  tasks: null,
  greet: function(){}  // 函数会被忽略
};

const json = JSON.stringify(data);
// 结果: '{"name":"Bob","age":25,"active":true,"tasks":null}'
```

`JSON.stringify(value, replacer, space)` 的 `replacer` 可接收转换函数，或指定保留哪些对象属性名的数组。`space` 控制缩进，例如 `JSON.stringify(data, null, 2)` 每层缩进两个空格。

| 输入值或结构 | 默认序列化结果 |
|---|---|
| `undefined`、函数、Symbol 值 | 对象属性省略，数组位置写为 `null`，顶层返回 JavaScript 的 `undefined` |
| `NaN`、`Infinity` | 写为 JSON 的 `null` |
| `Date` | 有效日期写为 ISO 格式字符串，无效日期写为 `null` |
| 定义了 `toJSON()` 的对象 | 序列化 `toJSON()` 返回的值 |
| 参与序列化的 `BigInt` 或循环引用 | 抛出 `TypeError` |

> [!warning] 序列化往返可能改变数据
> `JSON.stringify({ note: undefined })` 得到 `{}`，而 `JSON.stringify([undefined])` 得到 `[null]`。数组位置会保留，值可能改变。发送接口请求前，应按契约明确字段是省略还是写成 `null`。[ECMAScript JSON.stringify](https://tc39.es/ecma262/multipage/structured-data.html#sec-json.stringify)

---

## 7. JSON 工具与使用场景

- **在线校验/格式化**：`JSONLint`、`JSONFormatter`等
- **配置文件**：如 `package.json`。部分编辑器配置使用允许注释的 JSONC，应按读取工具的规则处理。
- **API 数据交互**：RESTful API 常用 `Content-Type: application/json`
- **本地存储**：`localStorage.setItem('key', JSON.stringify(data))`
- **跨语言数据交换**：几乎所有语言都有 JSON 解析库

### 7.1 HTTP 请求与响应

| 环节 | 约定 |
|---|---|
| 发送 JSON 请求体 | `Content-Type: application/json` 表示正在发送的内容类型。浏览器用 `JSON.stringify(data)` 构造请求体 |
| 声明希望收到的类型 | `Accept` 表示客户端希望收到的响应格式。收到响应后仍要读取实际 `Content-Type` |
| 处理响应 | 先检查 HTTP 状态，再按接口契约判断是否应有正文。接口约定返回 `204 No Content` 时，无需读取正文 |
| 读取正文 | 预期收到 JSON 时，检查媒体类型后调用 `response.json()`。代理返回 HTML 或响应体为空时，分别按实际故障定位 |

`response.json()` 会消费响应正文，同一正文不能再用 `response.text()` 重新读取。Fetch 收到 `404` 或 `500` 时通常仍会返回 `Response`，调用方应检查状态。[Fetch 标准](https://fetch.spec.whatwg.org/#body-mixin) · [HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)

### 7.2 接口错误与可观测性

| 失败层次 | 判断与处理 |
|---|---|
| 传输失败 | 连接、超时或取消等。界面提示对应原因，保留可排查的请求信息 |
| HTTP 失败 | 按接口文档区分 `400` 请求有误、`415` 不支持的媒体类型、`422` 语法正确但请求无法处理等。使用状态码与稳定错误标识分流 |
| 正文无法解析 | 记录状态、媒体类型和请求 ID，检查 HTML 错误页、正文截断、编码和格式 |
| 字段或业务规则不通过 | 根据字段路径定位缺失、类型、范围或枚举问题。库存、订单归属等由服务端继续检查 |

HTTP 接口可使用 `application/problem+json` 返回问题详情。前端按已约定的 `type` 判别错误，正文中的描述用于辅助展示或排查。实际 HTTP 状态码用于判断请求结果。`errors` 等扩展字段的结构由接口约定。[RFC 9457 第 3.1–3.2 节](https://www.rfc-editor.org/rfc/rfc9457.html#section-3.1)

---

## 8. 常见陷阱与最佳实践

> [!warning] 解析成功还要检查字段类型
> `{"score":"85"}` 符合 JSON 语法，但 `score` 是字符串。JavaScript 的 `>=` 可能隐式转换它。先执行约定的类型和范围检查，再参与计算。
>
> ```js
> const { score } = JSON.parse('{"score":"85"}');
> console.log(score >= 80);           // true
> console.log(Number.isFinite(score)); // false
> ```

接口代码依次处理解析错误、字段校验和业务规则。`try...catch` 可以捕获 `JSON.parse()` 的语法错误。字段是否必填、范围是否允许、用户是否有权操作，需要分别判断。[ECMAScript JSON 规范](https://tc39.es/ecma262/multipage/structured-data.html#sec-json-object)

---

## 9. Java/Spring 中的 JSON

- 常见 Spring Boot 3 MVC 项目通过 `spring-boot-starter-web` 引入 Jackson，并自动配置 `ObjectMapper`。
- 不是所有 Spring Boot 项目都默认包含 JSON 库；应结合所用 Boot 版本、Starter 和依赖确认。下例按 Boot 3 / Jackson 2 编写。
- 写接口用明确的请求 DTO 绑定输入。项目引入 Bean Validation 实现后，可在 `@RequestBody` 参数上加 `@Valid` 执行声明的约束。校验通过后，业务层再检查权限、数据归属和状态转换。[Spring MVC `@RequestBody`](https://docs.spring.io/spring-framework/reference/6.2/web/webmvc/mvc-controller/ann-methods/requestbody.html)

### (1) 全局配置（application.yml）

```yaml
spring:
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: Asia/Shanghai
    default-property-inclusion: non_null
```

---

### (2) 常用注解

| 注解 | 作用 |
| ------ | ------ |
| `@JsonProperty("name")` | 字段映射 |
| `@JsonIgnore` | 忽略字段 |
| `@JsonFormat(pattern="yyyy-MM-dd")` | 格式化日期 |
| `@JsonInclude(Include.NON_NULL)` | 序列化时省略值为 `null` 的属性 |
| `@JsonIgnoreProperties(ignoreUnknown = true)` | 忽略未知字段 |
| `@JsonSerialize(using = ToStringSerializer.class)` | 将字段写成 JSON 字符串，可用于传递大整数 ID |

---

### (3) 使用方式

**Controller 绑定请求 DTO 并返回响应 DTO**。以下为控制器片段，`@Valid` 和 `@NotBlank` 来自 Jakarta Validation。

```java
record CreateUserRequest(@NotBlank String name) {}
record UserResponse(String id, String name) {}

@PostMapping("/user")
public UserResponse create(@Valid @RequestBody CreateUserRequest request) {
    User saved = userService.create(request.name());
    return new UserResponse(saved.getId().toString(), saved.getName());
}
```

**手动转换**。通过 `ObjectMapper` 读取 DTO 后，按入口约定显式调用校验器。

```java
CreateUserRequest request = objectMapper.readValue(jsonStr, CreateUserRequest.class);
String json = objectMapper.writeValueAsString(request);
```

---

### (4) 注意事项

- Spring MVC 通过 HTTP 消息转换器读写请求和响应。JSON 转换通常交给 Jackson。
- `spring.jackson.date-format` 主要作用于 `java.util.Date` 等传统日期类型。`LocalDate`、`LocalDateTime` 通常通过 Java Time 模块、`@JsonFormat` 或相应序列化器配置格式。
- `non_null` 会省略值为 `null` 的字段。接口承诺输出可空的必填字段时，应为相应 DTO 保留该字段。
- 大整数 ID 可以在对外 DTO 中声明为字符串。使用 `@JsonSerialize(using = ToStringSerializer.class)` 时，也要把接口契约的类型同步定义为字符串。
- 读取外部响应时，按兼容策略决定是否忽略新增字段。写接口应使用只含允许修改字段的 DTO，按契约处理未知字段。
- 前端用 `JSON.parse()` 解析文本。服务端将外部 JSON 绑定到明确的 DTO，限制请求体大小和嵌套深度，避免对不可信输入启用开放式多态反序列化。

---


## 10. JSON Schema

JSON Schema 用 JSON 写出数据的约束，校验器据此检查实际数据。接口中常用它约定字段是否必填、类型是否正确、取值范围是否合法。

### 10.1 描述字段和类型

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "name": { "type": "string", "minLength": 1 },
    "age": { "type": ["integer", "null"], "minimum": 0 },
    "active": { "type": "boolean" },
    "roles": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string", "enum": ["reader", "editor"] }
    }
  },
  "required": ["name", "active"],
  "additionalProperties": false
}
```

| 关键字 | 检查什么 |
|---|---|
| `$schema` | 声明采用的 Schema 版本。本例用 Draft 2020-12 |
| `type` | 限制 JSON 值的类型。允许多个类型时用数组，如 `["integer","null"]` |
| `properties` | 字段出现时，检查它的类型、范围等约束 |
| `required` | 要求指定的键出现。字段值能否为 `null` 由 `type` 决定 |
| `additionalProperties` | 控制未列出的字段，设为 `false` 可拒绝额外字段 |
| `items` / `enum` | `items` 约束数组元素。本例用 `enum` 限定角色只能是 `reader` 或 `editor` |
| `minimum` / `minLength` / `minItems` | 分别限制数值下限、字符串最短长度和数组最少项数 |

### 10.2 区分必填、可空与类型错误

以 `{"name":"Tom","active":false}` 为基准，每行独立改变一个字段。

| 变化 | 校验结果 |
|---|---|
| 省略 `age`，或设置为 `null`、`0` | 通过。`age` 可省略，存在时可空或为非负整数 |
| 删掉 `active` | 失败。`required` 要求该字段出现 |
| `active` 改成 `0` 或 `"false"` | 失败。两者分别是数字和字符串 |
| `name` 改成 `""` | 失败。长度小于 `minLength` |
| `roles` 填 `[]` 或 `["owner"]` | 失败。分别违反数组长度和枚举约束 |
| 添加 `nickname` 字段 | 失败。本例拒绝额外字段 |

### 10.3 解析后校验，再使用数据

> [!important] 解析与 Schema 校验分两步
> 先用 `JSON.parse()` 将文本解析成值，再交给支持对应版本的 Schema 校验器。通过校验后，程序才读取字段或执行业务判断。

`default` 用于描述默认值。实际填充由应用或校验器的专门配置负责。`format` 可描述日期等格式，是否强制校验取决于所用 Schema 词汇及校验器配置。[JSON Schema 2020-12 Validation](https://json-schema.org/draft/2020-12/json-schema-validation) · [订单响应的完整 Schema 示例](#112-用-schema-固定响应结构)

---

## 11. 业务接口示例：订单详情

### 11.1 先约定字段类型和单位

约定 `GET /api/orders/{orderId}` 成功返回 `200` 和 `application/json`。找不到订单时返回 `404` 和 `application/problem+json`。

```json
{
  "orderId": "9007199254740993",
  "status": "PAID",
  "amountMinor": 12990,
  "currency": "CNY",
  "createdAt": "2026-11-24T08:30:00Z",
  "remark": null
}
```

| 字段 | 契约与理由 |
|---|---|
| `orderId` | 用字符串保留原值。长整型 ID 超过 JavaScript 的安全整数上限时，按普通数字解析可能丢失精度 |
| `status` | 约定枚举 `PENDING`、`PAID`、`CANCELLED`。服务端用业务规则检查能否推进到下一个状态 |
| `amountMinor`、`currency` | 以最小货币单位传递非负安全整数，并附货币代码。本例 `12990` 分表示 ¥129.90。需要更细精度或更大范围时，可约定十进制字符串及精度规则 |
| `createdAt` | 使用带时区的 RFC 3339 时间字符串，约定大写 `T` 和 `Z`。本例中的 `Z` 表示 UTC。展示时再按用户时区格式化 |
| `remark` | 字段必填，允许字符串或 `null`。`null` 表示暂无备注，缺少该字段会违反本接口契约 |

接口中如果还要区分空字符串或空数组，应说明它们的业务含义。写入接口也应约定省略字段和显式传 `null` 分别会保留、清空还是拒绝。[RFC 8259 数值精度](https://www.rfc-editor.org/rfc/rfc8259.html#section-6) · [RFC 3339 时间格式](https://www.rfc-editor.org/rfc/rfc3339.html#section-5.6)

### 11.2 用 Schema 固定响应结构

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["orderId", "status", "amountMinor", "currency", "createdAt", "remark"],
  "properties": {
    "orderId": { "type": "string", "pattern": "^[0-9]+$" },
    "status": { "enum": ["PENDING", "PAID", "CANCELLED"] },
    "amountMinor": { "type": "integer", "minimum": 0, "maximum": 9007199254740991 },
    "currency": { "const": "CNY" },
    "createdAt": {
      "type": "string",
      "format": "date-time",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"
    },
    "remark": { "type": ["string", "null"] }
  }
}
```

响应 Schema 允许新增字段，客户端只读取已约定的字段。删除字段、改变类型或调整金额单位时，需要保留兼容路径或发布新版本。新增枚举值前，要核对页面对未知状态的处理。

时间字段的 `pattern` 检查文本结构和时区是否存在。还要启用支持 `date-time` 的校验器，或由业务层校验日期、时间和偏移值是否有效。

### 11.3 前端读取响应

下面的函数请求订单详情，处理已知的订单不存在错误，并检查页面用于展示订单号和金额的字段。完整响应契约由上一节的 Schema 描述。

```js
async function fetchOrder(orderId, signal) {
  if (typeof orderId !== "string" || !/^[0-9]+$/.test(orderId)) {
    throw new TypeError("订单号必须是数字字符串");
  }
  const response = await fetch("/api/orders/" + encodeURIComponent(orderId), {
    headers: { Accept: "application/json, application/problem+json" },
    signal
  });
  return readOrder(response);
}

async function readOrder(response) {
  const contentType = response.headers.get("content-type") ?? "";
  const mediaType = contentType.split(";", 1)[0].trim().toLowerCase();

  if (!response.ok) {
    if (response.status === 404 && mediaType === "application/problem+json") {
      const problem = await response.json().catch(() => null);
      if (problem?.type === "https://example.com/problems/order-not-found") {
        throw new Error("订单不存在");
      }
    }
    throw new Error("请求失败（HTTP " + response.status + "）");
  }

  if (response.status !== 200 || mediaType !== "application/json") {
    throw new Error("订单接口返回了非预期响应");
  }

  const order = await response.json();
  if (
    typeof order?.orderId !== "string" ||
    !/^[0-9]+$/.test(order.orderId) ||
    !Number.isSafeInteger(order.amountMinor) ||
    order.amountMinor < 0 ||
    order.currency !== "CNY"
  ) {
    throw new TypeError("订单编号或金额格式错误");
  }
  return order;
}
```

> [!example] 订单不存在时的响应正文
> HTTP 状态为 `404`，媒体类型为 `application/problem+json`。
>
> ```json
> {
>   "type": "https://example.com/problems/order-not-found",
>   "title": "订单不存在",
>   "status": 404
> }
> ```

### 11.4 上线前的验收与排错

| 场景 | 预期 |
|---|---|
| 正常响应 | 能保留完整订单 ID，按分处理金额，正确展示 `null` 备注 |
| 类型错或缺字段 | 将字符串金额、负数、超出安全整数范围的金额、缺少必填字段作为契约失败 |
| HTTP 错误或非 JSON 正文 | 区分找不到订单、代理 HTML 错误页、正文截断。错误响应使用约定的状态码和问题类型 |
| 兼容性变更 | 用脱敏的旧响应样例验证新版客户端。服务端改字段前验证已上线客户端仍可读取 |

排障时记录接口、状态码、媒体类型和请求 ID。记录校验错误时保留字段路径和错误类型，省略令牌、用户隐私字段和完整正文。将可复核的正常与异常响应做成契约测试样例。

---

核对依据：[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259#section-2)、[JSON.stringify](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify)。
