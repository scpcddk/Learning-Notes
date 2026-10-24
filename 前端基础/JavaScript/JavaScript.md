# 完整笔记：JavaScript 核心知识点 —— 换热站无人值守前端项目

## 1. 变量与数据类型

> [!TIP]
> 把数据当成“水”，变量就是“储水罐”，类型决定这罐水是热水、冷水还是压力值

---

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | 变量是存储数据的**容器**，数据类型决定了数据能做什么操作 |
| **难度** | ⭐⭐ (入门但易踩坑) |
| **使用频率** | 🔴🔴🔴 极高（每行代码都在用） |
| **关联知识** | 作用域、内存、运算符、函数传参、API 数据解析 |

---

### 📌 核心要点

#### 1. 变量声明三兄弟：`let`、`const`、`var`

```js
// ✅ 正常写法 — 现代项目推荐
let supplyTemp = 75.2;      // 可变的供水温度
const STATION_ID = 12;      // 换热站ID，永不改变
var oldWay = '不推荐';      // 老式写法，有坑

// ❌ 错误写法 — 未声明直接赋值（会成为全局变量，污染命名空间）
pressure = 0.8;             // 严格模式报错，松散模式埋雷

// ✅ 修正写法
let pressure = 0.8;
```

> [!TIP]
> **生活比喻**：`let` 是可擦写的白板，`const` 是刻字的石碑，`var` 是容易弄丢的便签纸

---

#### 2. 基本类型 vs 引用类型 —— “复印”与“共享链接”

```js
// ✅ 基本类型：赋值就是“复印”一份
let tempA = 50;
let tempB = tempA;        // tempB 得到 50
tempA = 55;
console.log(tempB);       // 还是 50 ✅

// ✅ 引用类型：赋值是“共享同一个遥控器”
let sensorA = { id: 1, value: 22.5 };
let sensorB = sensorA;    // 指向同一个对象
sensorB.value = 23.0;
console.log(sensorA.value); // 23.0 ✅

// ❌ 错误：以为对象赋值会独立
let alarmList1 = ['断电', '超压'];
let alarmList2 = alarmList1;
alarmList2.push('过温');
console.log(alarmList1); // ['断电','超压','过温']，被意外修改了

// ✅ 修正：浅拷贝基本满足简单场景
let alarmList2 = [...alarmList1];
```

> [!TIP]
> **关键结论**：**基本类型（数字、字符串、布尔）像一张照片的复印，引用类型（对象、数组、函数）像一张照片的共享相册链接**

---

#### 3. 类型转换 —— 避免“20℃” + 5 = “20℃5”的惨案

```js
// ✅ 显式转换 — 自己动手，丰衣足食
let rawTemp = "55.3";               // 从输入框拿到的是字符串
let realTemp = Number(rawTemp);     // 转成数字 55.3
let isHot = Boolean(realTemp > 50); // 转布尔

// ❌ 错误 — 隐式转换拼接字符串
let heatLoad = "20" + 5;            // "205" 而不是 25

// ✅ 修正 — 先转换再运算
let heatLoad = Number("20") + 5;    // 25

// ❌ 易错：比较时类型不同
console.log(0 == false);   // true （松散相等，会发生类型转换）
console.log(0 === false);  // false ✅ 严格相等，先检查类型

// ✅ 推荐始终使用 ===
if (sensorValue === 0) { /* 确信是数字0 */ }
```

---

### 🔬 代码实验室：换热站供水温度监视器

```js
// 场景：从后端API获取数据，检查供水温度是否异常
// 原始数据（模拟API返回，全是字符串！）
const rawData = {
  station_id: "3",
  supply_temp: "82.5",    // 供水温度
  return_temp: "60.2",    // 回水温度
  pressure: "0.95",
  alarms: ["sensor_fault"] // 已存在报警
};

// 1. 常量保存安全阈值
const HIGH_TEMP_LIMIT = 80;     // 超过80℃报警
const LOW_TEMP_LIMIT = 45;

// 2. 显式转换并存储可变状态
let currentSupplyTemp = Number(rawData.supply_temp);
let currentReturnTemp = Number(rawData.return_temp);

// 3. 检查报警（注意：数组是引用类型，先浅拷贝再修改）
let activeAlarms = [...rawData.alarms];  // 拷贝一份，不影响原始数据

if (currentSupplyTemp > HIGH_TEMP_LIMIT) {
  activeAlarms.push('high_supply_temp');  // 添加过温报警
} else if (currentSupplyTemp < LOW_TEMP_LIMIT) {
  activeAlarms.push('low_supply_temp');
}

// 4. 计算温差（确保都是数字才能做减法）
let tempDiff = currentSupplyTemp - currentReturnTemp;

console.log('当前供水温度:', currentSupplyTemp, '℃');
console.log('供回温差:', tempDiff, '℃');
console.log('活跃报警:', activeAlarms);
// 输出：当前供水温度: 82.5 ℃  供回温差: 22.3 ℃  活跃报警: ['sensor_fault', 'high_supply_temp']
```

**解释**：从后端接口拿到的一定是字符串或原始对象，必须进行类型转换和拷贝再操作，否则数据展示错误或原始数据被污染

---

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| 用 `var` 导致变量提升或重复声明 | 用 `let`/`const`，优先 `const` | 现代JavaScript开发 |
| 认为 `const` 对象属性不可变 | `const` 对象属性可变，要冻结用 `Object.freeze` | 保存不变配置 |
| 用 `==` 比较数字和字符串 | 始终用 `===` 和 `!==` | 数值判断、报警条件 |
| 直接修改函数参数中的对象 | 先拷贝再修改或使用不可变数据 | 修改报警列表 |
| 忘记 `Number()` 转换，用 `+` 拼接字符串 | 算术运算前先转换 | 计算供回水平均温度 |
| 对 `null` 或 `undefined` 做属性访问 | 使用可选链或先判空 | 读取可能缺失的传感器数据 |

---

### 🏭 项目应用场景

在换热站无人值守前端项目中，变量与数据类型的运用无处不在：

- **传感器实时数据存储**：用 `let` 存储经常变化的温度、压力、流量值，用 `const` 保存报警阈值（`MAX_PRESSURE = 1.6`）
- **API 数据解析**：后端返回的 JSON 中数字可能是字符串类型，需要统一 `Number()` 转换后再用于图表绑定。
- **报警列表管理**：报警数组是引用类型，展示时需浅拷贝后排序，避免混淆原始数据顺序，也防止无意修改缓存的数据源。
- **站状态位运算**：一个站可能有多个状态标识（如运行、故障、离线），可通过**基本类型**布尔或数字位掩码来表示，保证状态判断准确。
- **表单输入处理**：用户输入的值永远是字符串，设置参数前必须转换成数字并校验，防止提交“abc”到PLC导致异常。

---

### 📝 自测问题

#### Q1: 以下代码输出什么？为什么？

```js
let a = 10;
const b = a;
a = 20;
console.log(b);
```

<details>
<summary>答案与解析</summary>

**答案**：`10`  
**常见错误**：以为 `b` 跟着变成 20。  
**解析**：基本类型赋值是值的复制，`b` 保存的是 `a` 的旧值 10，之后 `a` 改变不影响 `b`。**`const` 只是不能重新赋值，值本身可以改变**.这里存的数字是基本类型，无法改变，所以 `b` 还是 10。
</details>

#### Q2: 如何正确判断一个变量是不是数字 0（排除假值）？

```js
let val = "0";
if (val == false) { console.log("假值"); }  // 会输出吗？
```

<details>
<summary>答案与解析</summary>

**答案**：会输出，但这是错误的判断。应使用 `Number(val) === 0` 或 `val === 0` 如果已知类型。  
**常见错误**：用 `==` 导致 `"0" == false` 为 `true`（隐式转换规则诡异）。正确做法：先确保类型一致，再用严格相等。
</details>

#### Q3: 为什么修改从 API 取到的原始数据对象可能会导致 bug？

```js
let station = { id: 1, alarms: [] };
function addAlarm(s) {
  s.alarms.push('error');  // 直接修改了外部对象
}
addAlarm(station);
```

<details>
<summary>答案与解析</summary>

**答案**：`station.alarms` 被修改了，因为对象是引用类型。如果其他地方还依赖原数据（比如缓存、比较是否变化），就会发生意外改变。  
**修正**：在函数内拷贝 `let newAlarms = [...s.alarms, 'error']` 并返回新对象，保持数据不可变。
</details>

---

## 2. 运算符与流程控制

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | 运算符进行数据运算和比较，流程控制决定代码执行的分支和循环。 |
| **难度** | ⭐⭐ |
| **使用频率** | 🔴🔴🔴 极高 |
| **关联知识** | 数据类型、函数、算法、异步处理 |

### 📌 核心要点

#### 1. 算术与比较运算符 —— “温度求和与阈值判断”

```js
// ✅ 正常写法
let supply = 65.5;
let returnTemp = 50.2;
let diff = supply - returnTemp;          // 15.3
let isNormal = diff >= 10 && diff <= 40; // 正常温差范围

// ❌ 错误 — 字符串拼接误用
let total = "温度：" + supply + returnTemp; // "温度：65.550.2"
// ✅ 修正 — 分组或转换
let total = "温度：" + (supply + returnTemp); // 先计算数字和
let total2 = `供水${supply}℃, 回水${returnTemp}℃`;
```

#### 2. 逻辑运算符 —— “报警条件组合”

```js
// ✅ 短路求值常用于设置默认值
let pressure = getPressure() || 0.0;  // 看的是 “真假”（只要左边是假值，就用右边）
let name = stationName ?? "未命名";   // 看的是 “有没有值”（只有左边是 null 或 undefined，才用右边）

// ❌ 错误 — 误判0为假
let flow = 0;
let flowRate = flow || 1.0;   // flowRate是1，但流量可能就是0
// ✅ 修正
let flowRate = flow ?? 1.0;   // flowRate是0
```

#### 3. 条件语句 —— “运行模式切换”

```js
let mode = "auto"; // 'manual', 'auto', 'off'

// ✅ if/else if 链
if (mode === "off") {
  console.log("系统已停机");
} else if (mode === "manual") {
  console.log("手动控制模式");
} else {
  console.log("自动恒温调节");
}

// ❌ 错误 — 忘记break导致穿透
let valveState;
switch (mode) {
  case "off": valveState = 0;
  case "manual": valveState = 1; // 忘记break，off也会变成1
}
// ✅ 修正
switch (mode) {
  case "off": valveState = 0; break;
  case "manual": valveState = 1; break;
  default: valveState = 2;
}
```

#### 4. 循环 —— “巡检所有换热站”

```js
const stations = [101, 102, 103];
// ✅ for...of 遍历值
for (let id of stations) {
  console.log(`正在查询站${id}数据`);
}
// ❌ 错误 — 用for...in遍历数组（拿到的是索引字符串，且会遍历原型属性）
for (let i in stations) { ... } // 不推荐
// ✅ 修正：普通for或forEach
stations.forEach(id => { ... });
```

### 🔬 代码实验室：自动温差报警巡检

```js
// 模拟多个换热站实时数据
const stationsData = [
  { name: "1#站", supply: 78.2, returnTemp: 55.1 },
  { name: "2#站", supply: 92.5, returnTemp: 85.0 },
  { name: "3#站", supply: 60.0, returnTemp: 59.8 }
];

const HIGH_DIFF = 35; // 温差过大阈值
const LOW_DIFF = 3;   // 温差过小阈值

for (let station of stationsData) {
  let diff = station.supply - station.returnTemp;
  let status = "正常";

  if (diff > HIGH_DIFF) {
    status = "⚠️ 温差过大，可能热损";
  } else if (diff < LOW_DIFF && station.supply > 50) {
    status = "⚠️ 温差过小，可能循环不畅";
  } else if (station.supply > 90) {
    status = "🔥 供水超温";
  }

  console.log(`${station.name}: 温差${diff.toFixed(1)}℃ ${status}`);
}
```

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| `=`, `==` 混淆赋值与比较 | 比较用 `===`，赋值用 `=` | if 条件中 |
| `&&` 或 `||` 两端类型不明确 | 显式转为布尔再逻辑 | 权限判断、报警等级 |
| switch 漏掉 break | 每个 case 后加 break 或 return | 状态机处理 |
| 循环内修改被遍历数组 | 创建副本或使用 for 索引反向 | 动态增删报警项 |
| 用 `==` 判断 `null` 同时捕获 `undefined` | 使用 `=== null` 或 `== null`(仅判空) | 数据字段缺失 |

### 🏭 项目应用场景

- **阈值报警**：比较运算符判断温度、压力是否越限。
- **模式切换**：根据用户选择执行不同的控制逻辑。
- **批量数据轮询**：循环请求多个站点的实时数据。
- **状态机**：用 switch 处理换热站通讯状态（连接中、在线、离线、故障）。
- **默认参数**：用 `??` 为缺失的传感器值提供安全默认值。

### 📝 自测问题

**Q1** `"10" > 5` 的结果是什么？  
<details><summary>答案</summary>`true`，字符串"10"被隐式转换为数字10比较。</details>

**Q2** 下面代码如何避免死循环？  
```js
let temp = 30;
while (temp < 80) {
  console.log(temp);
}
```
<details><summary>答案</summary>循环内必须改变 temp，如 `temp += 5;` 否则无限循环。</details>

**Q3** 为什么建议在项目中使用 `===` 而非 `==`？  
<details><summary>答案</summary>`==` 进行类型转换，`0==''` 为 true，可能隐藏 bug；`===` 严格比较类型和值，更安全可预测。</details>

---

## 3. 函数

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | 函数是一段可重复使用的代码块，接收输入返回输出。 |
| **难度** | ⭐⭐⭐ |
| **使用频率** | 🔴🔴🔴 |
| **关联知识** | 作用域、闭包、异步、模块化 |

### 📌 核心要点

#### 1. 函数声明与箭头函数

```js
// ✅ 函数声明
function calcHeatLoad(flow, tempDiff) {
  return flow * 4.2 * tempDiff;
}

// ✅ 箭头函数（简短，不绑定this）
const calcHeatLoad = (flow, tempDiff) => flow * 4.2 * tempDiff;

// ❌ 错误 — 箭头函数不能用作构造函数
const LoadCalc = () => {};
// new LoadCalc(); // TypeError
```

#### 2. 参数默认值与解构参数

```js
// ✅ 默认参数
function setThreshold(temp = 75) { ... }

// ❌ 错误 — 函数默认参数只在参数为 undefined 时生效。null 在 JS 里被当作“一个主动传进来的有效值”，所以它不会触发默认，直接原样赋值为 null
setThreshold(null); // temp = null

// ✅ 对象解构参数，直观
function updateSensor({ id, value = 0 }) {
  console.log(id, value);
}
updateSensor({ id: 'T1', value: 22 });

// 原写法（拆解后）
function updateSensor(obj) {
  let id = obj.id;          // 从对象里取 id
  let value = obj.value;    // 从对象里取 value
  if (value === undefined) {
    value = 0;              // 只有取不到（undefined）时才赋默认0
  }
  console.log(id, value);
}
```

#### 3. 作用域 —— “每个房间的私有物品”

```js
let outside = "全局"; //var 没有块级作用域，整个函数内部都能访问，结果立刻不同
function room() {
  let inside = "函数内";
  console.log(outside); // 可访问外部
  if (true) {
    let block = "块级"; // let/const 块级
  }
  console.log(block); // ❌ ReferenceError: block is not defined
}//花括号 {} 是 let/const 的“防弹玻璃”，里面看得见外面，外面绝对看不见里面。
```

#### 4. 闭包 —— “背包记忆”

```js
// ✅ 闭包：函数记住外部变量
function createCounter(init) {
  let count = init;        // 私有变量
  return function() {
    count++;
    return count;
  };
}
const stationCounter = createCounter(0);
console.log(stationCounter()); // 1
console.log(stationCounter()); // 2
```

### 🔬 代码实验室：可配置报警生成器

```js
// 创建一个报警检测函数，记住设定的阈值
function createAlarmChecker(highLimit, lowLimit) {
  // 闭包保存阈值
  return function(temperature) {
    if (temperature > highLimit) return "过热报警";
    if (temperature < lowLimit) return "低温报警";
    return "正常";
  };
}

const supplyCheck = createAlarmChecker(85, 45);
console.log(supplyCheck(90)); // "过热报警"
console.log(supplyCheck(50)); // "正常"

// 不同站可配置不同阈值
const returnCheck = createAlarmChecker(60, 30);
console.log(returnCheck(65)); // "过热报警"
```

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| 箭头函数内使用 `arguments` 对象 | 使用剩余参数 `...args` | 可变参数处理 |
| 在循环里用 var 定义函数，索引错误 | 用 let 或者闭包 | 动态绑定事件 |
| 忘记 return，得到 undefined | 明确需要返回值的函数加 return | 数据转换函数 |
| 函数名与变量名冲突 | 使用动词或明确功能命名 | 事件处理函数 |
| 滥用全局变量 | 用参数传递，函数返回结果 | 数据流管理 |

### 🏭 项目应用场景

- **数据格式化**：把API数据转成图表需要的数据结构。
- **报警判断**：封装阈值比较逻辑，不同测点复用。
- **事件处理**：按钮点击切换模式、提交参数设置。
- **防抖/节流**：实时数据推送避免频繁更新界面。
- **权限校验**：高阶函数包装需要登录才能执行的操作。

### 📝 自测问题

**Q1** 下面代码输出什么？  
```js
for (var i = 1; i <= 3; i++) {
  setTimeout(() => console.log(i), 0);
}
```
<details><summary>答案</summary>`4,4,4`，因为 var 没有块作用域，循环完后 i 变为 4，回调执行时访问同一个 i。用 let 可解决。</details>

**Q2** 闭包可能引起什么问题？  
<details><summary>答案</summary>内存泄漏，因为闭包保持着对外部变量的引用，这些变量不会被垃圾回收。需及时释放不必要的闭包引用。</details>

**Q3** 如何设计一个函数，既能被 `new` 调用又能普通调用？  
<details><summary>答案</summary>内部用 `if (!new.target)` 判断，若普通调用则返回 new 实例。但通常避免混合使用，保持单一职责。</details>

---

## 4. 对象与数组

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | 对象存储键值对，数组存储有序列表 |
| **难度** | ⭐⭐ |
| **使用频率** | 🔴🔴🔴 |
| **关联知识** | JSON、API、遍历、解构 |

### 📌 核心要点

#### 1. 创建与访问

```js
// ✅ 对象字面量
let sensor = {
  id: "TEMP-01",
  value: 22.5,
  unit: "℃",
  "last-update": "2026-07-21" // 特殊属性名需引号
};
console.log(sensor.value);
console.log(sensor["last-update"]); // 动态访问

// ❌ 错误 — 访问不存在的属性得到 undefined
console.log(sensor.location); // undefined
// ✅ 使用可选链
console.log(sensor?.location?.x); // 安全
```

#### 2. 数组常用方法（map, filter, reduce）

```js
let temps = [23.1, 24.5, 22.0, 26.3];

// ✅ filter(挑出符合条件的) 获取异常温度
let anomalies = temps.filter(t => t > 25);
// ✅ map(加工每个元素) 转换为华氏度显示
let fahrenheit = temps.map(t => t * 9/5 + 32);
// ✅ reduce(汇总成单一结果) 求平均
// 数组.reduce( (acc, curr) => { 返回新值 }, 存钱罐初始值 );
let avg = temps.reduce((sum, t) => sum + t, 0) / temps.length;

// ❌ 错误 — 忘记提供reduce初始值，空数组报错
[].reduce((a, b) => a + b); // TypeError
// ✅ 始终提供初始值
```

#### 3. 解构赋值 —— “抽出盒子里的东西”

```js
// ✅ 对象解构
const { id, value, unit = "℃" } = sensor; // 默认值
// ✅ 数组解构
const [first, second, ...rest] = [101, 102, 103, 104];
// rest = [103, 104]

// ❌ 错误 — 解构null或undefined
const { name } = null; // TypeError
```

#### 4. 不可变操作 —— “不破坏原件”

```js
let alarms = ["断电", "过温"];
// ✅ 添加：返回新数组
let newAlarms = [...alarms, "过压"];
// ✅ 删除：filter 保留
let filtered = alarms.filter(a => a !== "过温");
// ❌ 错误 — 直接sort()修改原数组
alarms.sort(); 
// ✅ 先复制再排序
[...alarms].sort();
```

### 🔬 代码实验室：换热站数据看板汇总

```js
const rawStations = [
  { id: 1, name: "1#站", temp: 78.2, pressure: 0.95, online: true },
  { id: 2, name: "2#站", temp: 91.0, pressure: 1.2, online: true },
  { id: 3, name: "3#站", temp: 45.5, pressure: 0.65, online: false }
];

// 1. 只取在线站，并提取所需字段
const onlineData = rawStations
  .filter(s => s.online)
  .map(({ name, temp, pressure }) => ({ name, temp, pressure }));

// 2. 计算平均温度
const avgTemp = onlineData.reduce((sum, s) => sum + s.temp, 0) / onlineData.length;

// 3. 找出压力最高的站
const maxPressureStation = onlineData.reduce((prev, curr) =>
  prev.pressure > curr.pressure ? prev : curr
);

console.log("在线站:", onlineData);
console.log("平均温度:", avgTemp.toFixed(1));
console.log("压力最高站:", maxPressureStation.name);
```

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| 修改了作为props传入的对象 | 使用解构创建新对象或浅拷贝 | 组件间数据传递 |
| `arr.length = 0` 清空数组但多处引用 | 确认无其他引用，或重新赋值 | 重置数据列表 |
| `for...in` 遍历数组 | 用 `for...of` 或 `forEach` | 遍历测点列表 |
| 对象键隐式转换为字符串 | 如果需非字符串键用Map | 用对象做缓存 |
| 解构时变量名冲突 | 使用重命名 `{ name: stationName }` | 提取数据 |

### 🏭 项目应用场景

- **站点列表存储**：数组管理多个换热站对象。
- **报警列表操作**：新增、筛选、排序报警记录。
- **表单数据收集**：用对象保存用户输入的参数设置。
- **图表数据转换**：把后端数据 map 成 ECharts 所需格式。
- **本地缓存**：用对象存储用户偏好设置。

### 📝 自测问题

**Q1** 怎样深拷贝一个含有嵌套对象的数组？  
<details><summary>答案</summary>`JSON.parse(JSON.stringify(obj))` 适用于无函数/日期等类型，或使用 `structuredClone`，或 lodash 的 `cloneDeep`。</details>

**Q2** `const arr = [1,2,3]; arr.push(4);` 为什么可行？  
<details><summary>答案</summary>`const` 限制的是变量引用不可变，但数组内容（堆内存）可以修改。</details>

**Q3** 解构时如何避免未定义属性报错？  
<details><summary>答案</summary>提供默认值 `{ key = 'default' }` 或结合可选链先判断对象存在。</details>

---

## 5. DOM操作

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | 通过 JavaScript **操纵 HTML 元素**，实现动态交互 |
| **难度** | ⭐⭐ |
| **使用频率** | 🔴🔴🔴 |
| **关联知识** | 浏览器对象、事件、异步渲染 |

### 📌 核心要点

#### 1. 选择元素 —— “找到操作的对象”

```js
// ✅ 现代方法
//  document.querySelector：JS 用来在网页里“抓取”HTML标签的工具
const tempSpan = document.querySelector('#temp-value');
const allAlarms = document.querySelectorAll('.alarm-item');

// document	整个网页文档
// querySelector	懒汉模式：查询并返回第一个
// querySelectorAll()	勤劳模式：返回 NodeList（集合），哪怕只有 1 个
// ('.temp')	查询条件（CSS选择器）
// ❌ 错误 — 没注意选择器匹配多个，直接用innerHTML
document.querySelector('.temp').innerHTML = 90; // 只改了第一个
// ✅ 如果有多个则循环或精确选择
```

#### 2. 修改内容、样式、属性

```js
// ✅ 内容
tempSpan.textContent = '75.2℃'; // 纯文本，安全
// tempSpan.innerHTML = '<b>75.2℃</b>'; // 需防XSS

// ✅ 样式
tempSpan.style.color = 'red';
tempSpan.classList.add('warning');

// ✅ 自定义属性
tempSpan.setAttribute('data-sensor-id', 'T1');

// ❌ 错误 — 直接修改类名字符串覆盖其他类
tempSpan.className = 'warning'; // 丢了原有类
// ✅ 使用 classList
tempSpan.classList.add('warning');
```

#### 3. 事件监听 —— “响应用户操作”

```js
const btn = document.getElementById('confirm-btn');

// ✅ 添加监听
// JS 引擎做了一件事：在 btn 上贴一个纸条，上面写着“如果有人点击，就喊这句话”
btn.addEventListener('click', function(event) {
  console.log('参数已保存');
  event.stopPropagation(); // 阻止冒泡（按需）
});

// ❌ 错误 — 在循环中直接使用var索引
// for 循环跑得飞快，点击发生在循环结束之后。
// var 只给一块公共黑板，点击时，JS 只能拿到这个最终值
// let 每人发一张私人便利贴,每次点击都有自己的值
for (var i=0; i<buttons.length; i++) {
  buttons[i].addEventListener('click', () => console.log(i));
} // 所有都打印同一个值
// ✅ 用let或闭包
```

> [!TIP]
> 但凡在 `for` 循环里绑定点击事件，索引变量永远只用 `let` 

#### 4. 创建与删除元素

```js
// ✅ 动态添加报警卡片
const list = document.querySelector('.alarm-list');
const newAlarm = document.createElement('div');
newAlarm.className = 'alarm-item';
newAlarm.textContent = '超温报警';
list.appendChild(newAlarm);

// ❌ 错误 — 频繁操作DOM导致回流
for (let i=0; i<100; i++) { list.appendChild(...); }
// ✅ 使用DocumentFragment或先拼接字符串再一次性插入
```

### 🔬 代码实验室：实时温度仪表盘更新

```js
// HTML 结构: <span id="temp-display">--</span> <span id="status-light"></span>
const tempEl = document.getElementById('temp-display');
const statusLight = document.getElementById('status-light');

function updateTemperature(value) {
  // 更新文本
  tempEl.textContent = value.toFixed(1) + '℃';
  
  // 根据阈值改变样式
  if (value > 85) {
    tempEl.style.color = 'red';
    statusLight.className = 'light high';
  } else if (value < 45) {
    tempEl.style.color = 'blue';
    statusLight.className = 'light low';
  } else {
    tempEl.style.color = 'green';
    statusLight.className = 'light normal';
  }
}

// 模拟实时数据推送
setInterval(() => {
  let simulatedTemp = 50 + Math.random() * 40;
  updateTemperature(simulatedTemp);
}, 2000);
```

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| 在DOM加载前访问元素 | 把脚本放底部或 `DOMContentLoaded` | 初始化页面 |
| 用 `innerHTML` 拼接用户输入 | 使用 `textContent` 或转义 | 显示备注信息 |
| 事件处理器内误用 `this` | 箭头函数不绑定this，需要用e.target | 动态列表项事件 |
| 未移除不必要的事件监听 | `removeEventListener` 或在元素销毁时 | 单页应用组件卸载 |
| 直接修改 `style` 太多 | 改为添加/移除 class | 状态样式切换 |

### 🏭 项目应用场景

- **数据看板**：动态更新温度、压力数值，状态指示灯。
- **报警弹窗**：新建dom展示报警详情，点击关闭移除。
- **参数设置面板**：监听输入框变化，启用/禁用应用按钮。
- **图表容器**：管理 ECharts 实例的挂载与销毁。
- **响应式布局**：根据窗口尺寸调整仪表盘布局。

### 📝 自测问题

**Q1** `document.querySelector('.item')` 和 `getElementById('item')` 性能差异？  
<details><summary>答案</summary>getElementById 更快，但 querySelector 更灵活。除非性能关键且大量调用，差异可忽略。</details>

**Q2** 如何给动态添加的元素绑定事件？  
<details><summary>答案</summary>事件委托，在父元素上监听，通过 `e.target` 判断实际元素。</details>

**Q3** 为什么避免使用 `innerHTML` 插入用户提供的内容？  
<details><summary>答案</summary>可能导致 XSS 攻击，用户恶意脚本被执行。应使用 `textContent` 或经过消毒处理。</details>

---

## 6. 异步编程

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | 处理需要等待的操作（网络请求、定时），不阻塞主线程 |
| **难度** | ⭐⭐⭐⭐ |
| **使用频率** | 🔴🔴🔴 |
| **关联知识** | Promise, fetch, 事件循环, 错误处理 |

### 📌 核心要点

#### 1. 回调函数 —— “留下电话号码，好了叫我”

```js
// ❌ 回调地狱
// 回调地狱本质就是异步任务的‘单向阻塞流水线’——上一道工序不交付，下一道工序只能干瞪眼，整个业务流被时序依赖彻底焊死，毫无弹性
getStationData(1, function(data) {      // 步骤1：去服务器拿1号站的数据
  updateUI(data, function() {           // 步骤2：拿到数据后，更新页面UI（可能带动画）
    checkAlarms(function(alarms) {      // 步骤3：UI更新完后，再去检查有没有警报
      // ... 最终拿到警报结果
    });
  });
});
```

<details><summary>补充</summary>

- 为什么叫“地狱”？（四个致命伤）

| 痛点 | 大白话解释 | 你的代码里怎么体现 |
| :--- | :--- | :--- |
| **1. 金字塔缩进（Pyramid of Doom）** | 每多一层异步，缩进就往右推一格，业务复杂时能推到屏幕外面去。 | 现在才3层，看着还行。要是加个“保存日志”“发送通知”，直接变成向右的三角形。 |
| **2. 错误处理无处安放（Try-Catch失效）** | `try-catch` 只能抓同步错误，抓不住异步回调里的报错。如果 `updateUI` 崩了，外面根本不知道。 | 你没法在外面用 `try` 包住整个链条，只能每个回调里单独写 `if(err)`，代码瞬间翻倍。 |
| **3. 流程无法“中断”或“跳过”** | 如果步骤2（`updateUI`）发现数据非法，想直接结束不往下走，你没法 `return` 或 `break`。 | 你必须在 `updateUI` 的回调里判断，如果错了，就别调用 `checkAlarms`，但代码结构极其拧巴。 |
| **4. 变量作用域污染** | 内层函数能拿到外层变量，但外层拿不到内层。如果你想在最后把 `data` 和 `alarms` 合并，只能把它们挂在全局对象上，极其危险。 | 最终 `// ...` 里想同时用 `data` 和 `alarms`？抱歉，`data` 在外层，`alarms` 在内层，你得写闭包传参，超级麻烦。 |
</details>

#### 2. Promise —— “承诺未来给结果”

```js
// ✅ 创建Promise
function fetchStationData(id) {
   // 异步操作写在这里
   // new Promise = 下个快递单（异步任务）。
   // resolve = 签收成功，货给 .then；reject = 丢件理赔，货给 .catch
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (id > 0) resolve({ id, temp: 75 });
      else reject('无效ID');
    }, 1000);
  });
}

// 使用
fetchStationData(1)
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

#### 3. async/await —— “同步写法，异步灵魂”

```js
// ✅ 现代写法
async function loadDashboard() {
  try {
    const data = await fetchStationData(1);  // 等待 Promise 完成，拿到实际数据
    console.log(data.temp);                  // 此时 data 是 { temp: ... } 这样的对象
  } catch (error) {
    console.error('加载失败:', error);       // 如果请求出错，统一捕获
  }
}
// ❌ 错误 — 忘记await
const data = fetchStationData(1); // data是Promise对象，不是结果
```

#### 4. fetch API —— “网络请求利器”

```js
// ✅ 带错误处理
async function getAlarms(stationId) {
  const response = await fetch(`/api/stations/${stationId}/alarms`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const alarms = await response.json(); // 解析JSON也是异步
  return alarms;
}

// ❌ 错误 — 未检查 response.ok
const data = await fetch(url).then(res => res.json()); // 可能4xx解析出错
```

### 🔬 代码实验室：自动轮询换热站数据

```js
const stationIds = [1, 2, 3];
const REFRESH_INTERVAL = 5000; // 5秒

async function fetchStationData(id) {
  // 模拟API请求
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({ id, temp: 60 + Math.random() * 30, pressure: 0.8 + Math.random() * 0.4 });
    }, 200);
  });
}

async function updateAllStations() {
  const promises = stationIds.map(id => fetchStationData(id));
  try {
    const results = await Promise.all(promises); // 并行请求
    results.forEach(station => {
      console.log(`站${station.id}: ${station.temp.toFixed(1)}℃`);
    });
  } catch (err) {
    console.error('部分数据获取失败', err);
  }
}

// 首次加载后定时轮询
updateAllStations();
setInterval(updateAllStations, REFRESH_INTERVAL);
```

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| 忘记 `await` 导致得到 Promise 对象 | 异步函数调用前加 `await` | 数据请求 |
| 并行请求用顺序 await | 用 `Promise.all` 提高效率 | 多站数据 |
| 未捕获异步错误 | 使用 `try/catch` 或 `.catch` | 网络异常 |
| 在 `forEach` 中使用 `async` | 使用 `for...of` 或 `Promise.all` | 需要按序处理 |
| 混淆宏任务与微任务执行顺序 | 理解事件循环，合理使用 `setTimeout` 与 `Promise` | 状态更新时机 |

### 🏭 项目应用场景

- **实时数据轮询**：定时从后端获取换热站运行参数。
- **历史曲线查询**：请求历史数据并等待渲染。
- **用户登录**：异步验证账号，等待 token。
- **批量报警确认**：并行发送多个确认请求。
- **WebSocket连接**：异步处理连接建立和消息接收。

### 📝 自测问题

**Q1** `Promise.all` 中一个失败会怎样？  
<details><summary>答案</summary>整体 reject，立即返回第一个失败原因。若想忽略失败用 `Promise.allSettled`。</details>

**Q2** `setTimeout(fn, 0)` 一定立即执行吗？  
<details><summary>答案</summary>不会，它只是将回调放入宏任务队列，需等待当前执行栈和微任务清空。</details>

**Q3** 如何在循环中顺序执行异步操作？  
<details><summary>答案</summary>用 `for...of` 循环加上 `await`，因为 `forEach` 不支持 async 回调的等待。</details>

---

## 7. ES6+常用特性

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | ECMAScript 2015 及之后版本带来的新语法和API，提高开发效率。 |
| **难度** | ⭐⭐ |
| **使用频率** | 🔴🔴🔴 |
| **关联知识** | 变量、函数、对象、异步、模块化 |

### 📌 核心要点

#### 1. 模板字符串 —— “优雅拼接”

```js
const station = { name: "1#站", temp: 78.2 };
// ✅ 模板字符串
const msg = `${station.name} 当前温度：${station.temp}℃`;
// 可嵌入表达式
const warn = `状态：${station.temp > 80 ? '超温' : '正常'}`;

// ❌ 错误 — 传统拼接难以阅读
const oldMsg = station.name + ' 当前温度：' + station.temp + '℃';
```

#### 2. 展开运算符 —— “拆包与打包”

```js
// 数组展开
const temps1 = [20, 25];
const temps2 = [18, 22];
const allTemps = [...temps1, ...temps2]; // [20,25,18,22]

// 对象展开合并
const baseConfig = { high: 85, low: 45 };
const stationConfig = { ...baseConfig, low: 50 }; // 覆盖low
```

#### 3. 模块化 (import/export)

```js
// 导出 (utils.js)
export const API_URL = '/api';
export function formatTemp(val) { return val.toFixed(1) + '℃'; }
// 或默认导出
export default function request() {...}

// 导入
import request, { API_URL, formatTemp } from './utils.js';
```

#### 4. 可选链 `?.` 与空值合并 `??`

```js
const data = { station: { temp: null } };
// ✅ 可选链：安全访问
const temp = data?.station?.temp;  // null，不会报错
// ✅ 空值合并：只针对 null/undefined
const displayTemp = temp ?? '--';  // '--'

// ❌ 错误 — 使用 ||，会把0当作假
const flow = 0 || '无数据'; // '无数据'，但流量就是0
// ✅ 用 ??
const flow2 = 0 ?? '无数据'; // 0
```

### 🔬 代码实验室：配置化报警规则生成

```js
// 使用模块和展开运算符组织报警规则
const defaultRules = {
  tempHigh: 85,
  tempLow: 45,
  pressureHigh: 1.6,
  pressureLow: 0.2
};

// 站点自定义配置（只需覆盖部分）
const station1Rules = { ...defaultRules, tempHigh: 80 }; // 更严格
const station2Rules = { ...defaultRules, pressureHigh: 1.8 };

function checkRules(data, rules) {
  return {
    tempStatus: data.temp > rules.tempHigh ? '超温' : 
                data.temp < rules.tempLow ? '低温' : '正常',
    pressureStatus: data.pressure > rules.pressureHigh ? '超压' : '正常'
  };
}

// 使用时
const data1 = { temp: 82, pressure: 1.0 };
console.log(checkRules(data1, station1Rules)); // temp超温
```

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| 模板字符串中不小心嵌套复杂表达式 | 提取变量或函数，保持可读性 | 报警提示生成 |
| 展开对象时后面同名属性覆盖顺序错误 | 明确放置顺序，`{...base, ...override}` | 默认配置合并 |
| 动态导入模块路径错误 | 确保路径正确，或使用 `import()` 函数 | 按需加载组件 |
| 可选链滥用导致未定义不报错隐藏bug | 关键属性仍要做判断，逻辑用if明确 | 核心数据检查 |
| 忘记在支持环境外使用ES6 | 使用Babel转译或确保目标浏览器支持 | 部署到老旧工控机 |

### 🏭 项目应用场景

- **多语言报警信息**：用模板字符串拼接参数。
- **站点配置继承**：默认配置与站点专用配置合并。
- **代码结构**：工具函数、API模块分文件管理。
- **空数据安全**：接口返回缺失字段时用可选链和空值合并避免白屏。
- **动态图表类型**：按需导入 ECharts 组件，减少包体积。

### 📝 自测问题

**Q1** `{...obj}` 是深拷贝吗？  
<details><summary>答案</summary>不是，只有一层属性浅拷贝，嵌套对象仍共享引用。深拷贝需用其他方法。</details>

**Q2** 如何动态导入模块？  
<details><summary>答案</summary>`import('./module.js').then(module => ...)` 返回 Promise，常用于代码分割。</details>

**Q3** `??` 和 `||` 区别举例。  
<details><summary>答案</summary>`0 || 5` 得5，`0 ?? 5` 得0；`'' || 'def'` 得'def'，`'' ?? 'def'` 得''。?? 只视 null/undefined 为无效。</details>

---

## 8. 错误处理

### 📇 知识卡片

| 项目 | 内容 |
|------|------|
| **一句话定义** | 预见并捕获代码运行中的异常，防止程序崩溃。 |
| **难度** | ⭐⭐⭐ |
| **使用频率** | 🔴🔴🟡 |
| **关联知识** | 异步、Promise、调试、用户体验 |

### 📌 核心要点

#### 1. try/catch/finally

```js
try {
  const data = JSON.parse(responseText); // 可能解析失败
  updateDashboard(data);
} catch (error) {
  console.error('数据格式错误:', error.message);
  showErrorToast('数据加载失败');
} finally {
  hideLoading(); // 无论成败都执行
}
```

#### 2. 抛出与自定义错误

```js
// ✅ 抛出明确错误
function validateTemp(value) {
  if (typeof value !== 'number' || isNaN(value)) {
    throw new Error(`无效的温度值: ${value}`);
  }
  if (value < -50 || value > 200) {
    throw new RangeError(`温度${value}超出合理范围`);
  }
}
```

#### 3. 异步错误处理

```js
// ✅ async/await 搭配 try/catch
async function loadData() {
  try {
    const res = await fetch('/api/data');
    if (!res.ok) throw new Error(`请求失败 ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('网络或解析错误', err);
    return null; // 返回安全默认值
  }
}
// ❌ 错误 — Promise链忘记catch
fetchData().then(updateUI); // 未捕获的拒绝会导致控制台错误
```

#### 4. 全局异常捕获（最后防线）

```js
// 未处理的Promise拒绝
window.addEventListener('unhandledrejection', event => {
  console.error('未处理的异步错误:', event.reason);
  // 上报到监控系统
});
```

### 🔬 代码实验室：健壮的数据刷新器

```js
// 模拟不稳定的数据获取和解析
async function fetchStationData(id) {
  const response = await fetch(`/api/stations/${id}`);
  if (!response.ok) {
    throw new Error(`服务器错误: ${response.status}`);
  }
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch (parseErr) {
    throw new Error('数据格式无效');
  }
}

async function safeRefresh() {
  for (let id of [1, 2, 3]) {
    try {
      const data = await fetchStationData(id);
      if (data) {
        updateStationCard(id, data);
      }
    } catch (error) {
      console.warn(`站${id}刷新失败:`, error.message);
      showStationError(id, '数据获取失败'); // 显示离线状态
    }
  }
}

function updateStationCard(id, data) {
  // 防御性检查
  if (!data || data.temp === undefined) {
    console.warn(`站${id}数据不完整`);
    return;
  }
  // 正常更新...
}
```

### ⚠️ 易错点清单

| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| 捕获错误后什么都不做，吞掉异常 | 记录日志并给用户反馈 | 网络请求失败 |
| 在 `catch` 中抛出错误但不处理 | 重新抛出或转换为统一格式 | 上层需要知道 |
| 信任外部数据直接使用 | 对API数据进行类型检查和默认值 | 防止渲染错误 |
| 忘记JSON.parse可能抛错 | 放在try块内 | 处理历史数据导入 |
| 同步代码中抛错未捕获导致程序中止 | 关键流程加 try/catch | 初始化逻辑 |

### 🏭 项目应用场景

- **仪表盘数据加载**：网络异常时显示重试按钮，不白屏。
- **参数设置提交**：校验前端输入，范围错误提示。
- **实时消息解析**：WebSocket 消息格式错误不影响连接。
- **历史数据导出**：大数据量时捕获内存错误。
- **第三方库集成**：地图、图表组件初始化失败时降级方案。

### 📝 自测问题

**Q1** `try` 块中 `return` 语句后，`finally` 还会执行吗？  
<details><summary>答案</summary>会，finally 始终执行，甚至在 return 之前。如果 finally 中 return，会覆盖 try 中的返回值。</details>

**Q2** 如何处理 `setTimeout` 中的错误？  
<details><summary>答案</summary>在回调内部使用 try/catch，因为定时器回调是独立调用堆栈，外部 try 无法捕获。</details>

**Q3** 为什么不推荐捕获所有错误并忽略？  
<details><summary>答案</summary>隐藏了真实问题，导致数据不一致或难以排查，至少应记录日志。只捕获预期内的特定错误。</details>

---
