# 1.算法描述
这是一个双机流水车间调度（Flow Shop）的经典问题，通常被称为 Johnson 法则（Johnson’s rule）问题。
Johnson 法则适用于两台机器（A 和 B）的情况，目标是最小化总完工时间（makespan）。

---

# 2.算法思路
+ 将所有产品分成两类：
+ 在 A 车间加工时间 ≤ B 车间加工时间 的产品。
+ 在 A 车间加工时间 > B 车间加工时间 的产品。
+ 对第一类产品，按 A 车间时间升序 排序。
+ 对第二类产品，按 B 车间时间降序 排序。
+ 最终的加工顺序是：第一类产品（按 A 升序）在前，第二类产品（按 B 降序）在后。
+ 按照这个顺序模拟加工过程，计算总时间。

---

# 3.代码实现
```
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

struct Product {
    int id;
    int timeA;
    int timeB;
};

bool compare(const Product &a, const Product &b) {
    if (a.timeA <= a.timeB && b.timeA <= b.timeB) {
        // 都在第一组，按 timeA 升序
        return a.timeA < b.timeA;
    } else if (a.timeA <= a.timeB) {
        // a在第一组，b在第二组，a在前
        return true;
    } else if (b.timeA <= b.timeB) {
        // a在第二组，b在第一组，b在前
        return false;
    } else {
        // 都在第二组，按 timeB 降序
        return a.timeB > b.timeB;
    }
}

int main() {
    int n;
    cin >> n;
    
    vector<Product> products(n);
    for (int i = 0; i < n; i++) {
        products[i].id = i + 1;
        cin >> products[i].timeA;
    }
    for (int i = 0; i < n; i++) {
        cin >> products[i].timeB;
    }
    
    // Johnson 规则排序
    sort(products.begin(), products.end(), compare);
    
    // 模拟加工时间
    int timeA = 0, timeB = 0;
    for (int i = 0; i < n; i++) {
        timeA += products[i].timeA;
        // B机器开始时间为 max(A结束时间, B上一件结束时间)
        timeB = max(timeA, timeB) + products[i].timeB;
    }
    
    // 输出总时间
    cout << timeB << endl;
    
    // 输出顺序
    for (int i = 0; i < n; i++) {
        if (i > 0) cout << " ";
        cout << products[i].id;
    }
    cout << endl;
    
    return 0;
}
```
---
