# ==用法==

| 容器                | 随机访问 | 头尾增删       | 中间增删 | 查找       | 适用场景                     |
|---------------------|----------|----------------|----------|------------|------------------------------|
| vector              | ✅ O(1)   | 尾快           | O(n)     | O(n)       | 通用、随机访问               |
| deque               | ✅ O(1)   | ✅ O(1)        | O(n)     | O(n)       | 双端操作                     |
| list                | ❌        | ✅ O(1)        | ✅ O(1)   | O(n)       | 频繁插入删除                 |
| set/map             | ❌        | ❌             | ❌        | O(log n)   | 有序、去重、区间查询         |
| unordered_set/map    | ❌        | ❌             | ❌        | O(1)       | 高频查找、去重               |
| stack/queue         | ❌        | 仅一端         | ❌        | ❌          | 栈/队列逻辑                  |
| priority_queue      | ❌        | 仅堆顶         | ❌        | ❌          | 贪心、Dijkstra               |
<br>

---

# 一、 序列式容器（按插入顺序存储，支持随机/顺序访问）

这类容器的元素顺序由插入顺序决定，==可直接按位置访问==。

## 1.vector(动态数组)

```
#include <vector>
using namespace std;
int main() 
{
    vector<int> v;          // 空 vector
    v.push_back(1);        // 尾插
    v.emplace_back(2);     // 原地构造，更高效
    v.pop_back();          // 尾删
    v.size();              // 元素个数
    v.empty();             // 是否为空
    v[0];                  // 随机访问（不检查越界）
    v.at(0);               // 带越界检查
    v.clear();             // 清空
    v.resize(5);           // 调整大小
    v.reserve(10);         // 预分配容量（不改变 size）
    // 遍历
    for (int x : v) 
    cout << x << " ";
    for (auto it = v.begin(); it != v.end(); ++it) 
    cout << *it << " ";
}
```

---

## 2.deque(双端队列)

```
#include <deque>
using namespace std;
int main() 
{
    deque<int> dq;
    dq.push_back(1);       // 尾插
    dq.push_front(2);      // 头插
    dq.pop_back();         // 尾删
    dq.pop_front();        // 头删
    dq[0];                 // 随机访问
    dq.front(); dq.back(); // 首尾元素
}
```

---

## 3.list(双向链表)

```
#include <list>
using namespace std;
int main() 
{
    list<int> lst;
    lst.push_back(1);            // 尾插
    lst.push_front(2);           // 头插
    lst.pop_back();              // 尾删
    lst.pop_front();             // 头删
    lst.insert(lst.begin(), 3);  // 在迭代器前插入
    lst.erase(lst.begin());      // 删除迭代器位置
    lst.remove(3);               // 删除所有值为3的元素
    lst.sort();                  // 排序（成员函数，比全局sort快）
    lst.reverse();               // 反转
}
```

---

# 二、 关联式容器（自动排序，基于红黑树实现）

这类容器的元素会按键自动排序，键唯一或可重复，查找效率 O(log n)。

## 1.set(有序集合，键唯一)
+ **核心：自动排序+去重，按 key 查找。**<br>

```
#include <set>
using namespace std;
int main() 
{
    set<int> s;
    s.insert(3);
    s.insert(1);
    s.insert(2); // 自动排序为 {1,2,3}
    s.erase(2);  // 按值删除
    auto it = s.find(3); // 查找，返回迭代器，没找到返回end()
    s.count(3);   // 存在返回1，否则0
    s.lower_bound(2); // >=2 的第一个元素
    s.upper_bound(2); // >2 的第一个元素
}
```

---

## 2.multiset(有序多重集合，允许重复)

```
#include <set>
using namespace std;
int main() 
{
    multiset<int> ms;
    ms.insert(3);
    ms.insert(1);
    ms.insert(2); // 自动排序为 {1,2,3}
    ms.insert(1); // 允许重复，集合变为 {1,1,2,3}
    
    ms.erase(2);  // 删除所有值为 2 的元素，集合变为 {1,1,3}
    
    auto it = ms.find(1); // 查找，返回第一个值为 1 的元素的迭代器
    ms.count(1);   // 返回 1 出现的次数（这里是 2）
    
    ms.lower_bound(2); // 返回第一个 ≥2 的元素（指向 3 的迭代器）
    ms.upper_bound(2); // 返回第一个 >2 的元素（指向 3 的迭代器）
}
```

---

## ==set vs multiset 对比==

| 特性 | set | multiset |
| :--- | :--- | :--- |
| **元素唯一性** | 每个值只能出现一次 | 允许相同值多次出现 |
| **插入重复元素** | 无效，不会增加大小 | 成功，增加大小 |
| **count(x)** | 返回 0 或 1 | 返回 x 出现的次数 |
| **erase(x)** | 删除一个元素（如果存在） | 删除所有值为 x 的元素 |
| **find(x)** | 返回迭代器（唯一） | 返回第一个匹配的迭代器 |
| **equal_range(x)** | 范围长度 ≤ 1 | 范围长度 = 出现次数 |

---

## 3.map(有序键值对，键唯一)
+ **核心： key-value，按键排序，key 唯一。**<br>

```
#include <map>
using namespace std;

int main() 
{
    map<string, int> mp;
    mp["Alice"] = 90;       // 插入/修改
    mp.insert({"Bob", 85}); // 插入
    mp.count("Alice");      // 存在返回1
    auto it = mp.find("Bob");
    if (it != mp.end()) 
    {
        cout << it->first << " " << it->second << endl;
    }
    mp.erase("Alice");
}
```

---
## 4.multimap(有序键值对，键可重复)
+ **核心：key-value 存储，按键自动排序，允许重复键。**<br>
#include <map>
using namespace std;

```
int main() 
{
    multimap<string, int> mmp;
    
    // 插入（无下标操作符 []）
    mmp.insert({"Alice", 90});
    mmp.insert({"Alice", 95});      // 允许重复键
    mmp.insert({"Bob", 85});
    mmp.insert({"Bob", 88});
    // 集合变为：{"Alice",90}, {"Alice",95}, {"Bob",85}, {"Bob",88}
    
    // 查找
    mmp.count("Alice");             // 返回键 "Alice" 出现的次数（这里是 2）
    
    auto it = mmp.find("Bob");      // 返回第一个键为 "Bob" 的迭代器
    if (it != mmp.end()) {
        cout << it->first << ": " << it->second << endl;  // 输出 Bob: 85
    }
    
    // 删除
    mmp.erase("Alice");             // 删除所有键为 "Alice" 的元素
    
    // 获取同一键的所有值
    auto range = mmp.equal_range("Bob");   // 返回 pair<iterator, iterator>
    for (auto it = range.first; it != range.second; ++it) {
        cout << it->first << ": " << it->second << endl;  // 输出两个 Bob
    }
    
    // 边界查找
    auto low = mmp.lower_bound("Bob");    // 第一个键 ≥ "Bob"
    auto up = mmp.upper_bound("Bob");     // 第一个键 > "Bob"
}
```

---
## ==map vs multimap 对比==

| 特性 | map | multimap |
| :--- | :--- | :--- |
| **键唯一性** | 每个键只能出现一次 | 允许相同键多次出现 |
| **插入重复键** | 无效（除非使用 insert 或下标覆盖） | 成功，增加元素 |
| **下标操作符 `[]`** | 支持（不存在则插入默认值） | 不支持 |
| **count(k)** | 返回 0 或 1 | 返回键 k 出现的次数 |
| **erase(k)** | 删除一个元素（如果存在） | 删除所有键为 k 的元素 |
| **find(k)** | 返回迭代器（唯一） | 返回第一个匹配的迭代器 |
| **equal_range(k)** | 范围长度 ≤ 1 | 范围长度 = 出现次数 |
| **元素类型** | `pair<const Key, T>` | `pair<const Key, T>` |
| **排序依据** | 按 key 排序 | 按 key 排序 |

---

### + 内部元素：**pair**

```
#include<utility>
#include<string>
using namespace std;
int main()
{
    pair<int,string>p1;             //默认构造（值初始化）
    pair<int,string>p2(1,"Alice");  //直接初始化
    pair<int,string>p3={2,"bob"};   //列表初始化
    auto p4=make_pair(3,"Charlie")  //make_pair(自动推导类型)
    p1.first;                       //第一个元素（键）
    p1.second;                      //第二个元素（值）
    //比较（按先first后second字典序）
    p1=p2;                          //赋值
    swap(p2,p3);                    //交换
}
```

---

# 三、无序关联式容器（哈希表，平均 O(1)）

## ==优势==
1.时间效率高
2.无排序开销
3.内存相对友好
4.接口友好，易迁移
## ==短板==
1.最坏O(n)
2.不支持有序操作
3.迭代器不稳定：扩容时迭代器失效，不能边遍历边修改

## 1.unordered_set(无序集合，键唯一)

## 2.unordered_map(无序键值对，键唯一)

# 四、容器适配器(封装底层容器，接口受限)

## 1.stack(栈，LIFO)

```
#include <stack>
using namespace std;
int main() 
{
    stack<int> st;
    st.push(1);
    st.push(2);
    st.top();  // 取栈顶（2）
    st.pop();  // 删栈顶（无返回值）
    st.size();
    st.empty();
}
```

---

## 2.queue(队列，FIFO)

```
#include <queue>
using namespace std;
int main() 
{
    queue<int> q;
    q.push(1);
    q.push(2);
    q.front(); // 队首（1）
    q.back();  // 队尾（2）
    q.pop();   // 删队首
}
```

---

## 3.priority_queue(优先队列，堆)

```
#include <queue>
#include <vector>
#include <functional> // greater
using namespace std;
int main() 
{
    // 大根堆（默认）
    priority_queue<int> pq;
    pq.push(3);
    pq.push(1);
    pq.push(2);
    pq.top(); // 3
    pq.pop();
    // 小根堆
    priority_queue<int, vector<int>, greater<int>> min_pq;    //修改类型，把所有int修改为需要的类型
    min_pq.push(3);
    min_pq.push(1);
    min_pq.top(); // 1
}
```

---

