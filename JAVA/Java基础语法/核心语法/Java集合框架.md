---
markmap:
  initialExpandLevel: 2
---

# Java集合框架笔记

## 1 Java中集合类框架

### 1.1 集合概述

- **集合**：一种容器，用于存储多个对象（元素），与数组类似但功能更强大
- **与数组的区别**：
  - 数组长度**固定**，集合长度**动态可变**
  - 数组可以存储**基本类型和引用类型**，集合只能存储**引用类型**（基本类型需通过包装类）
  - 集合提供了更丰富的数据结构和算法（如查找、排序、去重等）
- **主要用途**：**存储、管理、操作**一组数据对象

---

### 1.2 **Java中集合框架层次结构**

- **根接口**：`Collection` 和 `Map`
- **Collection** 子接口：`List`（有序、可重复）、`Set`（无序、不可重复）、`Queue`（队列，按特定规则操作）
- **Map** 子接口：`HashMap`、`TreeMap`、`LinkedHashMap` 等，存储键值对
- 主要实现类关系图（简化）：

```java
Iterable (接口)
  └── Collection (接口)
      ├── List (接口)
      │    ├── ArrayList
      │    └── LinkedList
      ├── Set (接口)
      │    ├── HashSet
      │    └── TreeSet
      └── Queue (接口)
Map (接口)
  ├── HashMap
  ├── LinkedHashMap
  └── TreeMap
```

---

## 2 Collection接口

### 2.1 **Collection接口通用方法**

- `Collection`是所有**单列集合**的父接口，定义了基本操作方法：

| 方法 | 说明 |
| ------ | ------ |
| `boolean add(E e)` | **添加**元素 |
| `boolean remove(Object o)` | **删除**指定元素 |
| `void clear()` | **清空所有**元素 |
| `boolean contains(Object o)` | 是否**包含**某元素 |
| `boolean isEmpty()` | 是否为**空** |
| `int size()` | 返回元素**个数** |
| `Object[] toArray()` | 转为数组 |
| `Iterator<E> iterator()` | 返回迭代器 |

---

### 2.2 List接口及其实现类

- `List`特点：**有序**（存储顺序与取出顺序一致）、**可重复**、**支持索引**

#### 2.2.1 ArrayList类

- **底层**：**动态数组**（`Object[]`）
- **特点**：查询快（根据索引直接访问）、增删慢（需移动元素）
- **初始容量**：默认10，每次扩容为原来的1.5倍
- **线程安全**：不安全，适合单线程
- **常用方法**：`add(index, element)`、`get(index)`、`set(index, element)`、`remove(index)`

#### 2.2.2 LinkedList实现类

- **底层**：**双向链表**
- **特点**：增删快（只需修改前后节点指针）、查询慢（需遍历）
- **特有方法**：`addFirst()`、`addLast()`、`removeFirst()`、`removeLast()`、`getFirst()`、`getLast()`，可作为**栈**或**队列**使用
- **线程安全**：不安全

---

### 2.3 Iterator和ListIterator接口

#### 2.3.1 Iterator接口

- 所有`Collection`集合的通用**遍历方式**
- **常用方法**：
  - `hasNext()`：是否还有下一个元素
  - `next()`：返回下一个元素并移动指针
  - `remove()`：删除当前元素（避免并发修改异常）
- **示例**：

```java
List<String> list = new ArrayList<>();
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String s = it.next();
    if (s.equals("abc")) it.remove();
}
```

#### 2.3.2 ListIterator接口

- `Iterator` 的子接口，专门用于 `List`
- 额外功能：
  - 双向遍历：`hasPrevious()`、`previous()`
  - 添加元素：`add(E e)`
  - 替换元素：`set(E e)`
  - 获取索引：`nextIndex()`、`previousIndex()`

---

### 2.4 **增强型for循环**（for-each）

- **语法**：`for (元素类型 变量名 : 集合或数组) { ... }`
- **本质**：编译器自动转换为`Iterator`遍历
- **优点**：代码简洁，不易出错
- **限制**：遍历过程中**不能直接修改集合结构**（增删），否则可能抛出 `ConcurrentModificationException`（除非使用迭代器自身的 `remove`）
- **示例**：

```java
for (String s : list) {
    System.out.println(s);
}
```

---

### 2.5 Set接口及其实现类

- `Set`特点：**无序**(部分实现有序，如`TreeSet`)、**不可重复**，**无索引**

#### 2.5.1 HashSet类

- **底层**：**哈希表**(数组 + 链表/红黑树，实际是`HashMap`的键)
- **特点**：元素无序（依赖哈希值存储），不可重复，允许一个`null`元素
- **去重原理**：先比较`hashCode()`，若相同再比较`equals()`，均相同则视为重复元素
- **性能**：增删查`O(1)`平均时间复杂度
- **要求**：存储的对象**必须正确重写**`hashCode()`和`equals()`方法

#### 2.5.2 TreeSet类

- **底层**：**红黑树**（自平衡二叉查找树）
- **特点**：元素有序（自然排序或定制排序），不可重复，不允许`null`（JDK 1.7后）
- **排序方式**：
  - 自然排序：元素实现`Comparable`接口，重写`compareTo()`
  - 定制排序：构造时传入`Comparator`比较器
- **常用方法**：`first()`、`last()`、`lower(e)`、`higher(e)`、`subSet(from, to)`等

---

## 3 Map接口及其实现类

`Map` 存储 **键值对（Key-Value）**，键唯一，值可重复

### 3.1 **Map接口下常用的方法**

| 方法 | 说明 |
| ------ | ------ |
| `V put(K key, V value)` | **添加**键值对，若键已存在则覆盖旧值并返回旧值 |
| `V get(Object key)` | 根据键**获取**值 |
| `V remove(Object key)` | **删除**指定键的键值对 |
| `boolean containsKey(Object key)` | 是否**包含**某键 |
| `boolean containsValue(Object value)` | 是否**包含**某值 |
| `Set<K> keySet()` | 返回所有键的 Set 视图 |
| `Collection<V> values()` | 返回所有值的 Collection 视图 |
| `Set<Map.Entry<K,V>> entrySet()` | 返回所有键值对实体的 Set 视图 |
| `int size()` | 键值对**个数** |
| `void clear()` | **清空** |

---

### 3.2 HashMap实现类（了解）

- **底层**：JDK 1.8 之前为数组+链表，1.8 开始为数组+链表/红黑树（当链表长度 ≥8 且数组长度 ≥64 时转为红黑树）
- **特点**：
  - 键无序（依赖键的哈希值）
  - 键不可重复（通过`hashCode` + `equals`判断）
  - 允许一个`null`键和多个`null`值
  - 线程不安全，效率高
- **初始容量**：默认16，加载因子0.75
- **扩容机制**：当元素个数 > 容量 × 加载因子，容量翻倍（重新哈希）
- **遍历方式**：
  - `keySet()` + 增强 for
  - `entrySet()` 遍历（效率更高）
  - 使用 `forEach`（JDK 8+）

> 注：`LinkedHashMap` 可保持插入顺序或访问顺序；`TreeMap` 可对键进行排序

---

### 3.3 LinkedHashMap 实现类

- **底层**：`HashMap` + 双向链表（记录插入顺序或访问顺序）
- **特点**：迭代顺序为 **插入顺序**（默认）或 **访问顺序**（构造时指定 `accessOrder=true`）
- **性能**：略低于 `HashMap`（维护链表开销），但迭代更快
- **适用场景**：需要保持元素顺序的键值对缓存（如 LRU 缓存）

---

### 3.4 TreeMap 实现类

- **底层**：红黑树
- **特点**：键**有序**（自然排序或定制排序），键不可重复
- **常用方法**：`firstKey()`、`lastKey()`、`lowerKey()`、`higherKey()`、`subMap()` 等
- **要求**：键必须实现 `Comparable` 或传入 `Comparator`

---

### 3.5 Hashtable（了解）

- **特点**：线程安全（方法用 `synchronized` 修饰），键值均不允许 `null`，性能较差
- **注意**：已过时，并发环境下推荐 `ConcurrentHashMap`

---

### 3.6 ConcurrentHashMap（扩展）

- **底层**：JDK 1.7 采用分段锁，JDK 1.8 采用 `CAS + synchronized` 锁住链表头/红黑树根节点
- **特点**：线程安全，高并发下性能优于 `Hashtable`
- **键/值**：不允许 `null`

---

## 4 集合工具类与辅助接口

### 4.1 **`Collections` 工具类**（注意结尾有 `s`）

- **常用静态方法**：
  - **排序**：`sort(List<T> list)`（需元素实现 `Comparable`）、`sort(List<T> list, Comparator<? super T> c)`
  - **反转**：`reverse(List<?> list)`
  - **打乱**：`shuffle(List<?> list)`
  - **二分查找**：`binarySearch(List<? extends Comparable<? super T>> list, T key)`
  - **线程安全包装**：`synchronizedCollection(Collection<T> c)`、`synchronizedMap(Map<K,V> m)` 等
  - **不可变集合**：`unmodifiableList(List<? extends T> list)` 等
  - **空集合**：`emptyList()`、`emptySet()`、`emptyMap()`

---

### 4.2 `Arrays` 工具类

- 数组与集合互转：`asList(T... a)` → 返回固定大小的`List`（不支持增删操作，需包装为`ArrayList`才能增删）
- 数组排序、二分查找、填充等

---

### 4.3 `Comparable` vs `Comparator`

| 接口 | 使用方式 | 侵入性 | 灵活性 |
| ------ | ---------- | -------- | -------- |
| `Comparable` | 类实现`compareTo()` | 侵入，修改类本身 | 单一排序规则 |
| `Comparator` | 单独创建比较器，传入集合 | 无侵入 | 可定义多种排序规则 |

---

## 5 **集合的选择与性能对比**

| 场景 | 推荐集合 |
| ------ | ---------- |
| 需要**快速随机访问**（索引） | `ArrayList` |
| **频繁在头/尾增删**，或需作为**队列/栈** | `LinkedList` |
| 不允许重复，且**不关心顺序** | `HashSet` |
| 不允许重复，且**需要排序** | `TreeSet` |
| 存储键值对，**不要求顺序** | `HashMap` |
| 存储键值对，**要求插入顺序** | `LinkedHashMap` |
| 存储键值对，**要求按键排序** | `TreeMap` |
| 线程安全（**并发低**） | `Hashtable` 或 `Collections.synchronizedXXX` |
| 线程安全（**并发高**） | `ConcurrentHashMap`、`CopyOnWriteArrayList` |

---

## 6 **高频面试题补充**

### 6.1 `ArrayList` 与 `LinkedList` 的区别？

- **底层**：数组 vs 双向链表
- **访问**：`ArrayList` 支持 O(1) 随机访问；`LinkedList` 需 O(n) 遍历
- **增删**：`ArrayList` 在中间增删需移动元素（O(n)）;`LinkedList` 只需修改指针（O(1)，但需先定位到位置）
- **内存**：`ArrayList` 可能有闲置容量；`LinkedList` 每个节点额外存储前后指针
- **使用场景**：查询多用`ArrayList`;增删多（尤其在头尾）用`LinkedList`

---

### 6.2 `HashSet` 如何保证元素不重复？

- 内部依赖`HashMap`，将元素作为`Map`的键
- 调用`hashCode()`定位存储位置，若该位置无元素则直接存储；若已有元素，再调用`equals()`比较，若返回`true`则认为重复，不添加
- **要求**：存储在`HashSet`中的对象**必须正确重写**`hashCode()`和`equals()`

---

### 6.3 `HashMap` 的底层实现原理（JDK 1.8）？

- 数组 + 链表/红黑树
- 计算键的`hashCode()`然后通过`(n - 1) & hash`确定桶下标
- 当链表长度 ≥8 且数组长度 ≥64 时，链表转为红黑树（提高查询效率）
- 当红黑树节点数 ≤6 时，退化为链表
- 扩容因子 0.75，扩容时重新计算 hash 分配位置

---

### 6.4 什么是 `fail-fast` 机制？如何避免？

- **定义**：在遍历集合时，如果集合结构被修改（增/删），会立即抛出 `ConcurrentModificationException`
- **实现原理**：集合内部维护一个 `modCount` 字段，迭代器每次 `next()` 前检查 `modCount` 是否变化
- **避免方法**：
  1. 使用迭代器自身的 `remove()` 方法
  2. 使用 `CopyOnWriteArrayList` 等 `fail-safe` 集合（基于副本遍历）
  3. 使用并发集合类

---

### 6.5 `HashMap` 与 `Hashtable` 的区别？

| 特性 | `HashMap` | `Hashtable` |
| ------ | ----------- | -------------- |
| 线程安全 | 否 | 是（方法加 `synchronized`） |
| 允许 `null` | 键值均可为 `null` | 不允许 `null` |
| 性能 | 高 | 低 |
| 父类 | `AbstractMap` | `Dictionary`（已废弃） |

---

### 6.6 `ConcurrentHashMap` 如何实现线程安全？

- JDK 1.7：分段锁（Segment），将数据分成多个段，每个段独立加锁
- JDK 1.8：`CAS` + `synchronized` 锁住链表头/红黑树根节点，粒度更细，并发度更高

---
