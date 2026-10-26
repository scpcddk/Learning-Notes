# 📘 笔记一：创建项目与基础语法

## 📇 知识卡片

| 项目 | 内容 |
|------|------|
| 概念 | 用 Vite 快速搭建 Vue3 工程，通过模板语法和指令将数据渲染到页面 |
| 一句话定义 | Vite 是极速开发服务器，模板语法是“带逻辑的 HTML” |
| 难度 | ⭐ |
| 使用频率 | 🔴 极高 |
| 关联知识 | 响应式系统、组件、SFC |

## 📌 核心要点

### 1️⃣ 创建项目
`npm create vue@latest` 调用官方 create-vue 脚手架，生成基于 Vite 的 Vue 3 项目；不要把脚手架创建速度与开发服务器启动速度混为一谈。

**✅ 正确**
```bash
npm create vue@latest heat-station-screen
cd heat-station-screen
npm install
npm run dev
```

**❌ 错误**  
把 Vue CLI 的旧项目流程与当前 create-vue 流程混用，或创建后忘记安装依赖。已有 Vue CLI 项目仍可维护，并非命令本身无效。

**🔧 修正**  
新项目使用 `npm create vue@latest`，并按所用 create-vue / Vite 版本检查 Node.js 要求。2026-10-26 核对的 Vue 官方快速开始要求 `^22.18.0 || >=24.12.0`；后续以官方页面与依赖 engines 字段为准，不能继续按“Node ≥16”安装最新工具链。

### 2️⃣ 插值 `{{ }}`
只能放表达式，不能写语句。

**✅ 正确**
```vue
<p>供水温度：{{ supplyTemp }}℃</p>
```

**❌ 错误**
```vue
<p>{{ let x = 1 }}</p>
```

**🔧 修正**  
把逻辑移到 `<script setup>`，插值只展示结果。

### 3️⃣ 指令 `v-bind` 和 `v-on`
- `v-bind:` 简写 `:` 动态绑定属性  
- `v-on:` 简写 `@` 监听事件

**✅ 正确**
```vue
<img :src="logoUrl" @click="handleClick">
```

**❌ 错误**  
`<img src="{{ logoUrl }}">` 插值不能用于属性。

**🔧 修正**  
用 `:src="logoUrl"`。

### 4️⃣ 单文件组件结构
`.vue` 文件包含 `<template>`、`<script setup>`、`<style scoped>` 三个顶层标签，如一份标准简历。

## 🔬 代码实验室：换热站卡片
```vue
<script setup>
import { ref } from 'vue'
const station = '2号站'
const temp = 68.3
const online = ref(true)
</script>
<template>
  <div class="card">
    <h2>{{ station }}</h2>
    <p :class="{ green: online, red: !online }">
      {{ online ? '在线' : '离线' }} ｜ 供水 {{ temp }}℃
    </p>
    <button @click="online = !online">切换状态</button>
  </div>
</template>
<style scoped>
.card { border:1px solid #ccc; padding:16px; width:200px; }
.green { color:green; } .red { color:red; }
</style>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| `{{ var a=1 }}` | 表达式放 script，模板只渲染 | 插值 |
| `src="imgUrl"` 动态路径 | `:src="imgUrl"` | 图片 |
| `@click="fn"` 未定义 | 先在 script 里定义函数 | 事件 |
| 本想限制组件样式，却写了全局选择器 | 按需求使用 scoped、CSS Modules 或明确的全局样式；scoped 不是必需语法 | 组件 |

## 🏭 项目应用场景
- 站点卡片动态显示温度、压力
- 报警灯颜色绑定
- 操作按钮绑定远程指令

## 📝 自测问题
**Q1: 为什么 `{{ }}` 里不能写 if？**  
<details><summary>答案</summary>插值只接受表达式，逻辑控制请用 v-if 或三元表达式。</details>

**Q2: Vite 项目 index.html 的作用？**  
<details><summary>答案</summary>提供 `#app` 挂载点，main.js 通过 createApp 挂载根组件。</details>

**Q3: scoped 样式的原理？**  
<details><summary>答案</summary>给元素添加 `data-v-xxx` 唯一属性，并改写选择器实现隔离。</details>

---

# 📘 笔记二：响应式系统 (ref / reactive / computed / watch)

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | 数据变化时视图自动更新，核心 API 为 ref、reactive、computed、watch |
| 一句话定义 | 数据即视图，改数据就是改界面 |
| 难度 | ⭐⭐ |
| 使用频率 | 🔴 极高 |
| 关联知识 | 模板语法、生命周期 |

## 📌 核心要点

### 1️⃣ `ref` —— 响应式值容器
ref 可以保存基本类型或对象；在 JavaScript 中通过 .value 访问，模板中作为顶层绑定通常会自动解包。

**✅ 正确**
```js
import { ref } from 'vue'
const temperature = ref(75.2)
temperature.value += 1   // 触发更新
```

**❌ 错误**  
```js
let temperature = 75.2   // 非响应式
// 或 temperature = ref(75); temperature = 80 // 丢失响应式
```

**🔧 修正**  
使用 `const` 声明，修改 `.value`。

### 2️⃣ `reactive` —— 对象响应式外衣
reactive 返回对象的代理。应保持需要追踪的代理引用；不能把“重新赋值变量”和“更新代理属性”混为一谈。解构基本类型属性会丢失与原属性的响应式联系，嵌套对象的代理则另当别论。

**✅ 正确**
```js
import { reactive, toRefs } from 'vue'
const station = reactive({ name: '1号站', temp: 70 })
station.temp = 72
```

**❌ 错误**
```js
// station 用 const 声明，直接重新赋值会先抛出 TypeError。
// 即使用 let 声明，换成普通对象也会脱离原代理：
let replacement = reactive({ temp: 70 })
replacement = { temp: 80 }
let { name } = station // 解构后不是响应式
```

**🔧 修正**  
需要保持与原对象属性的联系时使用 `const { name, temp } = toRefs(station)` 或 toRef。`ref(station.temp)` 只取得当时的值，不能代替 toRef；若需要整体替换对象，可以一开始使用 ref 包裹整个对象。

### 3️⃣ `computed` —— 智能计算属性
依赖变化才重新求值，有缓存。

**✅ 正确**
```js
const supplyTemp = ref(80)
const returnTemp = ref(60)
const avgTemp = computed(() => (supplyTemp.value + returnTemp.value) / 2)
```

**❌ 错误**  
```js
const avgTemp = (supplyTemp.value + returnTemp.value) / 2 // 只算一次
```

### 4️⃣ `watch` —— 数据变更哨兵
监听一个或多个源，执行副作用（如请求数据、存储）。

**✅ 正确**
```js
watch(supplyTemp, (newVal, oldVal) => {
  if (newVal > 85) sendAlarm('温度过高')
})
```

**❌ 错误**  
把普通属性值直接交给 watch，例如 `watch(station.temp, ...)`，不是有效的响应式监听源；deep:true 不能修复这一点。

**🔧 修正**  
```js
watch(() => station.temp, (val) => { ... })
```

## 🔬 代码实验室：实时温度仪表盘
```vue
<script setup>
import { ref, reactive, computed, watch } from 'vue'
const temp = ref(72.0)
const unit = ref('℃')
const history = reactive([])

const status = computed(() => temp.value > 80 ? '高温' : temp.value < 10 ? '低温' : '正常')

watch(temp, (newVal) => {
  history.push({ time: new Date().toLocaleTimeString(), value: newVal })
  if (history.length > 5) history.shift()
})
</script>
<template>
  <div>
    <h3>供水温度</h3>
    <input type="range" v-model.number="temp" min="0" max="100" />
    <p>{{ temp }}{{ unit }} - <strong :style="{color: status==='高温'?'red':'green'}">{{ status }}</strong></p>
    <ul><li v-for="h in history" :key="h.time">{{ h.time }}: {{ h.value }}{{ unit }}</li></ul>
  </div>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| ref 忘记 .value | 在 JS 里加 .value | 数据读取 |
| 直接整体替换 reactive 对象 | 修改属性或使用 ref | 对象更新 |
| computed 里执行副作用 | 副作用放 watch | 预警触发 |
| 混淆对象监听与 getter 监听 | watch(reactiveObject, ...) 默认深层监听；watch(() => obj.child, ...) 通常只监听 child 被替换，深层变更按需加 deep:true | 复杂对象 |

## 🏭 项目应用场景
- 实时温度、压力数据绑定
- 计算供回水温差、能效比
- 监听温度超限自动报警

## 📝 自测问题
**Q1: ref 和 reactive 什么时候选哪个？**  
<details><summary>答案</summary>基本类型用 ref，对象推荐用 reactive 或 ref 均可，但解构时 reactive 需配合 toRefs。</details>

**Q2: computed 和 method 有什么区别？**  
<details><summary>答案</summary>computed 有缓存，依赖不变不重新执行；method 每次访问都执行。</details>

**Q3: watchEffect 和 watch 的区别？**  
<details><summary>答案</summary>watchEffect 自动跟踪内部响应式依赖，立即执行；watch 需显式指定源，可获新旧值。</details>

---

# 📘 笔记三：生命周期与副作用

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | 组件从创建到销毁的各个阶段，可在特定时刻执行代码 |
| 一句话定义 | 在合适的时间做合适的事，如获取数据、清理定时器 |
| 难度 | ⭐⭐ |
| 使用频率 | 🟡 中高 |
| 关联知识 | 响应式、组件、路由 |

## 📌 核心要点

### 1️⃣ `onMounted` —— 挂载后执行
DOM 渲染完毕，此时可获取元素、发起请求、启动定时器。

**✅ 正确**
```js
import { onMounted, ref } from 'vue'
const data = ref(null)
onMounted(async () => {
  try {
    const response = await fetch('/api/station')
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    data.value = await response.json()
  } catch (error) {
    console.error('站点加载失败', error)
  }
})
```

**❌ 错误**  
在 setup 顶层直接读取尚未创建的 DOM。与 DOM 无关的数据请求可以在 setup 中发起；SSR 项目应按框架的数据获取机制处理，而不是一律放进 onMounted。

### 2️⃣ `onUnmounted` —— 清理资源
组件卸载后执行，适合清理手动创建的副作用；卸载前的钩子是 onBeforeUnmount。

**✅ 正确**
```js
let timer
onMounted(() => { timer = setInterval(updateData, 5000) })
onUnmounted(() => { clearInterval(timer) })
```

**❌ 错误**  
忘记清除定时器，路由切换后定时器仍在运行。

### 3️⃣ 副作用处理
数据订阅、WebSocket 连接、事件监听必须在销毁时移除。

**✅ 正确**
```js
onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))
```

## 🔬 代码实验室：换热站实时时钟与状态轮询
```vue
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const now = ref(new Date())
const status = ref('正常')
let timer, pollTimer

onMounted(() => {
  timer = setInterval(() => { now.value = new Date() }, 1000)
  pollTimer = setInterval(() => {
    status.value = Math.random() > 0.9 ? '报警' : '正常'
  }, 3000)
})
onUnmounted(() => {
  clearInterval(timer)
  clearInterval(pollTimer)
})
</script>
<template>
  <div>
    <p>当前时间：{{ now.toLocaleTimeString() }}</p>
    <p :class="{ alarm: status==='报警' }">设备状态：{{ status }}</p>
  </div>
</template>
<style scoped>
.alarm { color: red; font-weight: bold; }
</style>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 | 场景 |
|--------|--------|------|
| setup 内直接操作 DOM | 在 onMounted 中操作 DOM | 需要获取元素 |
| 定时器不清理 | onUnmounted 中 clearInterval | 定时更新数据 |
| 在异步回调里创建 watcher，却忘了停止 | setup 中同步创建的 watch/watchEffect 会随组件卸载自动停止；异步创建或需要提前停止时使用返回的 stop | 手动控制 |

## 🏭 项目应用场景
- 页面加载时获取所有换热站列表
- 每 5 秒轮询实时数据
- 清除定时器和 WebSocket 连接，防止后台消耗

## 📝 自测问题
**Q1: onMounted 和 setup 执行顺序？**  
<details><summary>答案</summary>setup 同步执行，onMounted 在 DOM 挂载后执行。数据请求放在 onMounted 可保证已有容器。</details>

**Q2: 为什么要在 onUnmounted 里清理？**  
<details><summary>答案</summary>手动创建的定时器、连接和全局监听若继续运行，可能保留不再需要的数据或发起无意义请求。清理这些副作用；同步创建于 setup 的响应式 watcher 通常会自动停止。</details>

---

# 📘 笔记四：组件通信 (props / emit / v-model / 插槽)

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | 父子组件间传递数据和方法，实现组件解耦与复用 |
| 一句话定义 | props 向下传数据，emit 向上抛事件 |
| 难度 | ⭐⭐ |
| 使用频率 | 🔴 极高 |
| 关联知识 | 响应式、列表渲染 |

## 📌 核心要点

### 1️⃣ `props` —— 父传子只读礼物
定义接口，父组件绑定，子组件不能修改。

**✅ 正确**
```vue
<!-- 父 -->
<StationCard :name="station.name" :temp="70" />

<!-- 子 -->
<script setup>
const props = defineProps({
  name: String,
  temp: Number
})
</script>
```

**❌ 错误**  
子组件尝试 `props.temp = 80` 会警告。

**🔧 修正**  
如需修改父组件数据，通常发送事件让父组件更新；仅需本地草稿时再复制。props 是浅只读，嵌套对象仍可能被修改，不能因此绕过单向数据流。

### 2️⃣ `emit` —— 子传父电话
子组件触发事件，父组件监听。

**✅ 正确**
```js
const emit = defineEmits(['update'])
emit('update', newValue)
```

**❌ 错误**  
直接修改 prop 并期望父组件同步，或忘记声明 emits。

### 3️⃣ `v-model` —— 双向对话糖
本质是 `:modelValue` + `@update:modelValue`。

**✅ 正确**
```vue
<!-- 父组件模板片段，text 应在父组件中声明 -->
<MyInput v-model="text" />
```

```vue
<!-- 子组件内：此写法同时适用于 Vue 3.4 之前的版本 -->
<script setup>
defineProps({ modelValue: String })
const emit = defineEmits(['update:modelValue'])
</script>
<template>
  <input :value="modelValue" @input="emit('update:modelValue', $event.target.value)" />
</template>
```

### 4️⃣ 插槽 —— 预留占位盒
匿名插槽、具名插槽、作用域插槽。

**✅ 正确**
```vue
<StationCard>
  <template #header>报警信息</template>
</StationCard>
```

## 🔬 代码实验室：换热站面板父子协作
```vue
<!-- 父组件 ParentPanel.vue -->
<script setup>
import { ref } from 'vue'
import StationItem from './StationItem.vue'
const stations = ref([
  { id:1, name:'1号站', temp:70 },
  { id:2, name:'2号站', temp:65 }
])
function handleDelete(id) {
  stations.value = stations.value.filter(s => s.id !== id)
}
</script>
<template>
  <StationItem v-for="s in stations" :key="s.id" :station="s" @delete="handleDelete">
    <template #footer>🔧 操作</template>
  </StationItem>
</template>
```

子组件 `StationItem.vue`（与父组件分别保存）：

```vue
<script setup>
const props = defineProps({ station: Object })
const emit = defineEmits(['delete'])
</script>
<template>
  <div class="item">
    <h4>{{ station.name }} - {{ station.temp }}℃</h4>
    <button @click="emit('delete', station.id)">删除</button>
    <slot name="footer" />
  </div>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 修改 prop | 用局部变量或 v-model |
| emit 未声明 | `defineEmits(['event'])` |
| 插槽名拼错 | 子 `<slot name="x">` 父 `#x` |

## 🏭 项目应用场景
- 换热站列表将每个站点封装成卡片组件
- 顶部导航用插槽插入动态内容
- 监控参数面板双向绑定到图表组件

## 📝 自测问题
**Q1: 如何将父组件的所有属性批量传给子组件？**  
<details><summary>答案</summary>在父组件中批量绑定一个属性对象可用 `v-bind="propsObject"`。`$attrs` 只包含当前组件未声明为 props/emits 的透传属性和监听器，并不是“全部 props”；`inheritAttrs: false` 配合 `v-bind="$attrs"` 用于自行控制透传位置。</details>

**Q2: v-model 如何绑定多个值？**  
<details><summary>答案</summary>使用具名 v-model:title="title" 等。</details>

---

# 📘 笔记五：列表渲染与条件渲染

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | v-for 循环渲染列表，v-if/v-show 控制显示隐藏 |
| 一句话定义 | 让页面结构随数据动态变化 |
| 难度 | ⭐ |
| 使用频率 | 🔴 极高 |
| 关联知识 | 响应式、key、组件 |

## 📌 核心要点

### 1️⃣ `v-for` 必须绑定唯一 `key`
key 是 Vue 的身份证，帮助 diff 算法高效更新。

**✅ 正确**
```vue
<li v-for="item in list" :key="item.id">{{ item.name }}</li>
```

**❌ 错误**  
用 index 作为 key 且列表会变动顺序或增删。

**🔧 修正**  
用与数据关联的唯一 id。

### 2️⃣ `v-if` vs `v-show`
`v-if` 是真的销毁和重建，`v-show` 只是 display 切换。

**✅ 正确**
```vue
<div v-if="alarm">报警！</div>   <!-- 频繁切换用 v-show -->
<div v-show="showTooltip">提示</div>
```

**❌ 错误**  
Vue 3 中同一元素的 v-if 优先于 v-for，v-if 因而无法使用该 v-for 才声明的循环变量；不是“每次循环都判断”。

**🔧 修正**  
用 `<template>` 包裹 v-for，内部使用 v-if。

## 🔬 代码实验室：换热站报警列表
```vue
<script setup>
import { ref } from 'vue'
const alarms = ref([
  { id:1, level:'严重', msg:'1号站压力过高' },
  { id:2, level:'警告', msg:'3号站通讯中断' }
])
</script>
<template>
  <ul>
    <template v-for="a in alarms" :key="a.id">
      <li v-if="a.level==='严重'" style="color:red">{{ a.msg }}</li>
      <li v-else style="color:orange">{{ a.msg }}</li>
    </template>
  </ul>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| key 用 index | 用唯一业务 id |
| v-if 和 v-for 同元素 | template 分层 |
| 忘记 key 导致状态错乱 | 始终加 key |

## 🏭 项目应用场景
- 多个换热站动态卡片
- 根据报警等级显示不同颜色
- 动态表格行

## 📝 自测问题
**Q1: 为什么更新数组后视图没变？**  
<details><summary>答案</summary>先确认操作的是响应式数组。Vue 3 对响应式数组的索引赋值和 length 修改都能追踪；“索引赋值不响应”是常见的 Vue 2 旧限制。filter 返回新数组，需要接收结果，例如 `list.value = list.value.filter(...)`；操作原始普通数组或丢失响应式引用也可能导致视图不更新。</details>

---

# 📘 笔记六：表单与双向绑定

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | v-model 实现表单元素和数据的双向同步 |
| 一句话定义 | 输入框改，数据变；数据变，输入框改 |
| 难度 | ⭐ |
| 使用频率 | 🔴 极高 |
| 关联知识 | 组件通信、响应式 |

## 📌 核心要点

### 1️⃣ 基本用法与修饰符
`.number`、`.trim`、`.lazy` 优化输入。

**✅ 正确**
```vue
<input v-model.number="temp" type="number" />
```

**❌ 错误**  
认为 type="number" 还必须再加 .number 才会转换。Vue 会为这种输入框自动应用数字转换；文本框可显式使用 .number。无法解析时仍保留原字符串，清空后通常是空字符串，因此仍需验证输入。

### 2️⃣ 表单元素全覆盖
文本框、多行文本、复选框、单选框、下拉框。

**✅ 正确**
```vue
<select v-model="selectedStation">
  <option v-for="s in stations" :key="s.id" :value="s.id">{{ s.name }}</option>
</select>
```

## 🔬 代码实验室：换热站参数设置表单
```vue
<script setup>
import { ref } from 'vue'
const setting = ref({
  tempLimit: 80,
  autoMode: true,
  stationId: null
})
const stations = [{id:1,name:'1号站'},{id:2,name:'2号站'}]
</script>
<template>
  <form>
    <label>温度阈值：<input v-model.number="setting.tempLimit" /></label><br/>
    <label>自动模式：<input type="checkbox" v-model="setting.autoMode" /></label><br/>
    <select v-model="setting.stationId">
      <option :value="null">--选择站点--</option>
      <option v-for="s in stations" :key="s.id" :value="s.id">{{ s.name }}</option>
    </select>
    <p>当前设置：{{ setting }}</p>
  </form>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 把输入法组合输入期间暂不更新当成故障 | 如需逐次读取组合输入，显式处理 input/composition 事件；.lazy 改为 change 时同步，不是实时输入修复方案 |
| 复选框 true-value 未定义 | 可用 :true-value="1" :false-value="0" |

## 🏭 项目应用场景
- 运维人员设定报警阈值
- 远程下发参数指令

---

# 📘 笔记七：Pinia 状态管理

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | Vue 的官方状态管理库，替代 Vuex |
| 一句话定义 | 全站共享的数据仓库，组件直接取用 |
| 难度 | ⭐⭐ |
| 使用频率 | 🟡 中高 |
| 关联知识 | 组件通信、响应式、路由 |

## 📌 核心要点

### 1️⃣ 定义 Store —— 组合式写法
像 setup 函数一样组织 state、getters、actions。

**✅ 正确**
```js
// stores/station.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
export const useStationStore = defineStore('station', () => {
  const list = ref([])
  const activeId = ref(null)
  const activeStation = computed(() => list.value.find(s => s.id === activeId.value))
  async function fetchAll() {
    const response = await fetch('/api/stations')
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    list.value = await response.json()
  }
  return { list, activeId, activeStation, fetchAll }
})
```

**❌ 错误**  
直接在组件里维护全局共享数据，导致不同页面数据不一致。

使用前先在应用入口安装 Pinia：`app.use(createPinia())`，其中 createPinia 从 pinia 导入；再挂载应用、调用 useStationStore。

### 2️⃣ 在组件中使用
```js
import { useStationStore } from '@/stores/station'
const store = useStationStore()
store.fetchAll()  // 调用 action
```

## 🔬 代码实验室：全局站点切换
```vue
<script setup>
import { onMounted } from 'vue'
import { useStationStore } from '@/stores/station'
const store = useStationStore()
onMounted(async () => {
  try { await store.fetchAll() }
  catch (error) { console.error('站点加载失败', error) }
})
</script>
<template>
  <select v-model="store.activeId">
    <option v-for="s in store.list" :key="s.id" :value="s.id">{{ s.name }}</option>
  </select>
  <div v-if="store.activeStation">当前选中：{{ store.activeStation.name }}</div>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 直接解构 store 的 state/getter，丢失响应式联系 | state/getter 用 storeToRefs；action 可以直接解构 |
| action 异步不等待 | 适当使用 await 并处理 loading |

## 🏭 项目应用场景
- 全局当前选中换热站
- 用户登录信息
- 报警未读数、通知

---

# 📘 笔记八：Vue Router

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | 前端路由，根据 URL 切换不同页面组件 |
| 一句话定义 | 点击导航不刷新，界面平滑切换 |
| 难度 | ⭐⭐ |
| 使用频率 | 🟡 中高 |
| 关联知识 | 组件、Pinia、生命周期 |

## 📌 核心要点

### 1️⃣ 配置路由
定义路径与组件映射。

**✅ 正确**
```js
const routes = [
  { path: '/', component: () => import('@/views/Dashboard.vue') },
  { path: '/detail/:id', name: 'detail', component: () => import('@/views/Detail.vue') }
]
```

### 2️⃣ 导航与传参
`router-link` 或编程式 `router.push`，通过 params 或 query 传参。

**✅ 正确**
```vue
<router-link :to="{ name:'detail', params:{ id: station.id }}">详情</router-link>
```

编程式导航（在 setup 中获取 router）：

```js
import { useRouter } from 'vue-router'
const router = useRouter()
function openDetail(id) {
  router.push({ name:'detail', params:{ id } })
}
```

## 🔬 代码实验室：大屏路由切换
```vue
<template>
  <nav>
    <router-link to="/">总览</router-link>
    <router-link to="/alarm">报警</router-link>
  </nav>
  <router-view v-slot="{ Component }">
    <keep-alive>
      <component :is="Component" />
    </keep-alive>
  </router-view>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 把未声明在路径中的对象塞进 params | 动态路径参数会编码进 URL，正常配置服务器回退后刷新仍可恢复；额外状态用 store/持久化，查询条件用 query |
| 旧式 next 分支重复调用或漏调用 | 优先使用守卫返回值；使用 next 时每条逻辑路径只调用一次 |

## 🏭 项目应用场景
- 大屏总览、站点详情、报警页面切换
- 历史数据查询页面

---

# 📘 笔记九：组件库使用 (Element Plus)

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | 集成 Element Plus UI 库，快速搭建专业界面 |
| 一句话定义 | 现成的轮子，拿来即用 |
| 难度 | ⭐ |
| 使用频率 | 🔴 极高 |
| 关联知识 | 组件、v-model、插槽 |

## 📌 核心要点

### 1️⃣ 安装与按需引入
推荐自动导入。

**✅ 正确**
```bash
npm install element-plus
npm install -D unplugin-vue-components unplugin-auto-import
```
配置 vite 插件后，组件可直接使用无需手动 import。

### 2️⃣ 常用组件
`el-table`、`el-button`、`el-input`、`el-dialog`、`el-icon`。

## 🔬 代码实验室：换热站表格
```vue
<script setup>
import { ref } from 'vue'
const tableData = [
  { name:'1号站', temp:70, status:'正常' },
  { name:'2号站', temp:85, status:'报警' }
]
</script>
<template>
  <el-table :data="tableData" style="width:100%">
    <el-table-column prop="name" label="名称" />
    <el-table-column prop="temp" label="温度(℃)" />
    <el-table-column label="状态">
      <template #default="{ row }">
        <el-tag :type="row.status==='报警'?'danger':'success'">{{ row.status }}</el-tag>
      </template>
    </el-table-column>
  </el-table>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 全局引入导致包体积大 | 按需自动导入 |
| 图标不显示 | 安装 @element-plus/icons-vue 并引入 |

## 🏭 项目应用场景
- 数据表格、弹窗设置
- 报警确认对话框

---

# 📘 笔记十：性能优化

## 📇 知识卡片
| 项目 | 内容 |
|------|------|
| 概念 | 使用 keep-alive、异步组件、懒加载等技术提升应用速度和体验 |
| 一句话定义 | 让大屏不卡顿，加载更快 |
| 难度 | ⭐⭐ |
| 使用频率 | 🟢 中等 |
| 关联知识 | 路由、组件、动态导入 |

## 📌 核心要点

### 1️⃣ `keep-alive` —— 缓存组件状态
缓存切换出去的组件实例和局部状态，例如表单数据；窗口滚动位置不由 KeepAlive 自动保证，需要配合路由 scrollBehavior 或激活钩子处理。

**✅ 正确**
```vue
<router-view v-slot="{ Component }">
  <keep-alive include="Dashboard">
    <component :is="Component" />
  </keep-alive>
</router-view>
```

### 2️⃣ 异步组件 + 路由懒加载
```js
import { defineAsyncComponent } from 'vue'
const Detail = defineAsyncComponent(() => import('./Detail.vue'))
// 路由中直接 () => import(...)
```

### 3️⃣ 避免不必要的响应式
大量静态数据用 `shallowRef` 或 `markRaw`。

## 🔬 代码实验室：大屏优化示例
```vue
<template>
  <el-container>
    <el-aside width="200px">菜单</el-aside>
    <el-main>
      <router-view v-slot="{ Component }">
        <keep-alive :max="10">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </el-main>
  </el-container>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 全部组件同步加载 | 路由懒加载 |
| 把 include/exclude 当成路由路径匹配 | 它们按组件名匹配；不配置表示缓存符合条件的组件，可结合 max 限制数量 |
| 超大列表一次渲染全部行 | 按需求分页或使用虚拟列表；computed 缓存派生数据，不会自动减少 DOM 行数 |

## 🏭 项目应用场景
- 切换换热站详情保留之前查询条件
- 图表组件懒加载避免首屏过重
- 实时数据使用节流避免频繁渲染

---

核对依据：[Vue 快速开始](https://vuejs.org/guide/quick-start.html)、[响应式基础](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)、[表单绑定](https://vuejs.org/guide/essentials/forms.html)、[生命周期](https://vuejs.org/api/composition-api-lifecycle.html)、[Vue Router 命名路由](https://router.vuejs.org/guide/essentials/named-routes.html)。
