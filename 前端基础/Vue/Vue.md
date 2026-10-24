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
`npm create vue@latest` 是官方推荐方式，比老 `vue create` 快几十倍。

**✅ 正确**
```bash
npm create vue@latest heat-station-screen
cd heat-station-screen
npm install
npm run dev
```

**❌ 错误**  
仍使用 `vue create` 或忘记安装依赖。

**🔧 修正**  
改用 `npm create vue@latest`，并确保 Node.js ≥ 16。

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
const station = '2号站'
const temp = 68.3
let online = true
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
| `<style>` 没加 scoped | 添加 scoped 隔离样式 | 组件 |

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

### 1️⃣ `ref` —— 基本类型响应式盒子
访问或修改都需要 `.value`，模板中自动解包。

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
不能整体替换，不能解构。

**✅ 正确**
```js
const station = reactive({ name: '1号站', temp: 70 })
station.temp = 72
```

**❌ 错误**
```js
station = { name: '2号站', temp: 80 } // 失去响应
let { name } = station // 解构后不是响应式
```

**🔧 修正**  
用 `toRefs()` 解构，或直接用 `ref` 包裹对象属性。

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
监听对象属性时没写 getter 函数或没有 `deep:true`。

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
| watch 深度监听忘写 {deep:true} | 监听对象内部属性时加 deep:true | 复杂对象 |

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
  data.value = await fetch('/api/station')
})
```

**❌ 错误**  
在 setup 顶层直接发请求，此时组件未挂载，可能引起 SSR 问题。

### 2️⃣ `onUnmounted` —— 清理资源
组件销毁前执行，避免内存泄漏。

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
| watch 监听后未停止 | 使用返回的 stop 函数或 watchEffect | 手动控制 |

## 🏭 项目应用场景
- 页面加载时获取所有换热站列表
- 每 5 秒轮询实时数据
- 清除定时器和 WebSocket 连接，防止后台消耗

## 📝 自测问题
**Q1: onMounted 和 setup 执行顺序？**  
<details><summary>答案</summary>setup 同步执行，onMounted 在 DOM 挂载后执行。数据请求放在 onMounted 可保证已有容器。</details>

**Q2: 为什么要在 onUnmounted 里清理？**  
<details><summary>答案</summary>组件卸载后仍持有引用会造成内存泄漏，且可能对已销毁组件更新数据报错。</details>

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
如需修改，应在子组件内拷贝一份到本地响应式变量。

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
<MyInput v-model="text" />
<!-- 子组件内 -->
<template>
  <input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" />
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

<!-- 子组件 StationItem.vue -->
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
<details><summary>答案</summary>使用 v-bind="$attrs" 并设置 inheritAttrs: false。</details>

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
v-if 和 v-for 在同一元素上使用（v-if 优先级更高，会导致每次循环都判断）。

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
<details><summary>答案</summary>可能使用了非变异方法(如 filter 返回新数组需要重新赋值)，或直接通过索引修改数组没触发响应式(需用 reactive 包裹或 ref 整体替换)。</details>

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
忘记加 `.number` 导致获取字符串。

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
| 中文输入法下 v-model 延迟 | 使用 @input 直接处理或 lazy |
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
export const useStationStore = defineStore('station', () => {
  const list = ref([])
  const activeId = ref(null)
  const activeStation = computed(() => list.value.find(s => s.id === activeId.value))
  async function fetchAll() {
    list.value = await api.getStations()
  }
  return { list, activeId, activeStation, fetchAll }
})
```

**❌ 错误**  
直接在组件里维护全局共享数据，导致不同页面数据不一致。

### 2️⃣ 在组件中使用
```js
import { useStationStore } from '@/stores/station'
const store = useStationStore()
store.fetchAll()  // 调用 action
```

## 🔬 代码实验室：全局站点切换
```vue
<script setup>
import { useStationStore } from '@/stores/station'
const store = useStationStore()
onMounted(() => store.fetchAll())
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
| 直接解构 store 失去响应 | 使用 storeToRefs(store) 解构 |
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
  { path: '/detail/:id', component: () => import('@/views/Detail.vue') }
]
```

### 2️⃣ 导航与传参
`router-link` 或编程式 `router.push`，通过 params 或 query 传参。

**✅ 正确**
```vue
<router-link :to="{ name:'detail', params:{ id: station.id }}">详情</router-link>
<!-- 编程式 -->
router.push({ name:'detail', params:{ id:1 } })
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
| params 刷新后丢失 | 使用 query 或持久化 store |
| 路由钩子未正确放行 | next() 调用或 return true |

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
切换路由时保留表单和滚动位置。

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
      <keep-alive :max="10">
        <router-view />
      </keep-alive>
    </el-main>
  </el-container>
</template>
```

## ⚠️ 易错点清单
| ❌ 错误 | ✅ 正确 |
|--------|--------|
| 全部组件同步加载 | 路由懒加载 |
| keep-alive 不写 include/exclude | 精细控制缓存 |
| 大列表不解构 props | 使用 computed 减少渲染 |

## 🏭 项目应用场景
- 切换换热站详情保留之前查询条件
- 图表组件懒加载避免首屏过重
- 实时数据使用节流避免频繁渲染

---
