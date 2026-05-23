# JSON 笔记

## 1. 什么是 JSON

- **JSON** 全称 **JavaScript Object Notation**（JavaScript 对象表示法）。
- 是一种轻量级的**数据交换格式**，易于人阅读和编写，也易于机器解析和生成。
- 完全独立于编程语言，但采用了类似 C 语言家族的习惯（包括 C、C++、C#、Java、JavaScript、Python 等）。
- 常用于客户端与服务器之间的数据传输、配置文件、日志记录等。

## 2. JSON 语法规则

1. 数据以 **键/值对** 形式存在。
2. 数据由逗号 `,` 分隔。
3. **花括号 `{}` 保存对象**（无序的键值对集合）。
4. **方括号 `[]` 保存数组**（有序的值的集合）。
5. **键必须用双引号 `"` 包裹**（单引号不允许）。
6. 值的类型必须是合法的 JSON 数据类型（见下节）。
7. 不支持注释。
8. 整体必须是一个对象 `{}` 或数组 `[]`（不能是原始值直接裸露，但早期有些实现允许，标准要求最外层为对象或数组）。

## 3. JSON 数据类型

JSON 支持以下 6 种数据类型：

| 类型       | 说明                                                         | 示例                     |
|------------|--------------------------------------------------------------|--------------------------|
| **字符串** | 必须使用双引号，支持转义字符（`\"`, `\\`, `\/`, `\n` 等）   | `"hello"`, `"a\"b"`      |
| **数字**   | 整数或浮点数，不支持 NaN、Infinity、八进制/十六进制          | `42`, `-3.14`, `1.0e10`  |
| **布尔值** | `true` 或 `false`                                            | `true`, `false`          |
| **null**   | 表示空值                                                     | `null`                   |
| **对象**   | 无序的键/值对集合，键必须为字符串，值可以是**任意合法类型** | `{"name":"Alice","age":30}` |
| **数组**   | 有序的值的集合，值可以是**任意合法类型** | `[1, "text", null, true]` |

*注意：JSON 没有日期类型，通常用 ISO 8601 字符串表示；也没有函数、undefined、Symbol 等。*

## 4. JSON 示例

### (1)有效 JSON

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

### (2)无效 JSON 及原因

```json
{
  name: "John",          // 错误：键没有双引号
  'age': 30,             // 错误：键用了单引号
  "desc": "He said "Hi"",// 错误：字符串内部双引号未转义
  "score": NaN,          // 错误：NaN 不是合法数字
  "hobby": undefined,    // 错误：undefined 不是合法类型
  "date": new Date(),    // 错误：不能使用构造函数
  /* comment */          // 错误：不支持注释
}
```

## 5. JSON 与 JavaScript 对象的区别

| 特性               | JSON                              | JavaScript 对象              |
| -------------------- | ----------------------------------- |------------------------------ |
| 键的引号           | 必须用双引号                      | 通常不加引号，或可使用单/双引号 |
| 字符串界定符       | 必须用双引号                      | 单引号或双引号均可            |
| 值的类型           | 仅支持6种类型                     | 支持所有 JS 类型（函数、日期等）|
| 注释               | 不允许                            | 允许                         |
| 尾随逗号           | 不允许                            | 允许（ES5+）                 |
| 原型继承           | 无，纯粹数据容器                  | 有原型链                     |
| 用途               | 数据交换                          | 程序内数据结构               |

**相互转换：**

- `JSON.parse(jsonString)` → 将 JSON 字符串解析为 JavaScript 对象。
- `JSON.stringify(jsObject)` → 将 JavaScript 对象序列化为 JSON 字符串。

## 6. JSON 常用方法（JavaScript 环境）

### (1)`JSON.parse()`

```js
const jsonStr = '{"name":"Alice","scores":[95,87]}';
const obj = JSON.parse(jsonStr);
console.log(obj.name);       // "Alice"
console.log(obj.scores[0]);  // 95
```

*错误处理：如果字符串格式不合法，会抛出 `SyntaxError`，可用 `try...catch` 捕获。*

### (2)`JSON.stringify()`

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

**常用参数：**

- `JSON.stringify(value, replacer, space)`
  - `replacer`：可选，过滤或转换函数/数组。
  - `space`：可选，缩进空格数或字符串，美化输出。

```js
JSON.stringify(data, null, 2);
// 输出带缩进的格式化 JSON 字符串
```

**特殊行为：**

- `undefined`、函数、Symbol 作为对象属性值会被忽略；作为数组元素会转为 `null`。
- `NaN`、`Infinity` 转为 `null`。
- Date 对象会调用 `toJSON()` 转为 ISO 字符串。
- 对象定义了 `toJSON()` 方法时，会序列化其返回值。

## 7. JSON 工具与使用场景

- **在线校验/格式化**：JSONLint、JSONFormatter 等。
- **配置文件**：如 `package.json`、`tsconfig.json`、VSCode 设置。
- **API 数据交互**：RESTful API 常用 `Content-Type: application/json`。
- **本地存储**：`localStorage.setItem('key', JSON.stringify(data))`。
- **跨语言数据交换**：几乎所有语言都有 JSON 解析库。

## 8. 常见陷阱与最佳实践

- **尾随逗号**：对象或数组最后一个元素后不能有逗号。

```json
{ "a": 1, "b": 2, }  // 错误
[1, 2, ]              // 错误
```

- **数字前导零**：JSON 不允许数字有前导零（如 `01`），八进制不支持。
- **字符串转义**：注意路径中的反斜杠 `\\`，换行 `\n`，引号 `\"` 等。
- **日期序列化**：使用 ISO 字符串 `"2026-05-23T10:00:00Z"`，前后端统一解析。
- **大数字精度**：JavaScript 的 `JSON.parse` 对大整数（超过 `Number.MAX_SAFE_INTEGER`）可能丢失精度，考虑使用自定义解析或字符串传输。
- **确保安全解析**：对不信任的 JSON 使用 `try...catch`；避免直接用 `eval()` 解析（`eval('('+json+')')` 有代码注入风险）。

## 9. JSON Schema（扩展了解）

- 用于描述和验证 JSON 数据结构的规范（用 JSON 书写）。
- 定义属性类型、必填字段、数值范围等。
- 常用关键字：`$schema`, `type`, `properties`, `required`, `additionalProperties` 等。
- 广泛应用于 API 参数校验、自动生成文档、IDE 智能提示。

示例 Schema：

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "age": { "type": "integer", "minimum": 0 }
  },
  "required": ["name"]
}
```

---
