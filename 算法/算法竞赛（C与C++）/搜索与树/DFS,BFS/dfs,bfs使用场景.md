## DFS 和 BFS 的核心区别

| 特性 | DFS (深度优先搜索) | BFS (广度优先搜索) |
|------|-------------------|-------------------|
| **数据结构** | 栈（递归或显式栈） | 队列 |
| **辅助空间** | 树上递归栈 O(h)；一般图另需 O(V) 访问标记 | 树上队列 O(w)；一般图的队列和访问标记均可达 O(V) |
| **特点** | 一条路走到黑，然后回溯 | 层层推进，按层遍历 |
| **是否保证最短路径** | 普通遍历不保证；枚举所有候选路径并取最小值另计复杂度 | 是（无权或统一正边权时，最短路等价于最少边数） |
| **适用场景** | 连通性、路径存在性、拓扑排序 | 最短路径、层序遍历 |

---

## 具体使用场景

代码片段中的邻接表、访问标记、结果数组等全局变量须先初始化；下标范围须与题目约定一致。

### DFS 适用场景

1. **连通性问题**
```cpp
// 判断图中两点是否连通
bool dfs_connected(int u, int target) {
    if (u == target) return true;
    visited[u] = true;
    for (int v : graph[u]) {
        if (!visited[v] && dfs_connected(v, target))
            return true;
    }
    return false;
}
```

1. **回溯/排列组合**
```cpp
// 全排列：假设 nums 中元素互不相同；含重复值时还需对分支去重
void dfs_permutation(vector<int>& nums, vector<bool>& used, vector<int>& path) {
    if (path.size() == nums.size()) {
        result.push_back(path);
        return;
    }
    for (int i = 0; i < nums.size(); i++) {
        if (!used[i]) {
            used[i] = true;
            path.push_back(nums[i]);
            dfs_permutation(nums, used, path);
            path.pop_back();
            used[i] = false;
        }
    }
}
```

2. **拓扑排序**
```cpp
// graph 为有向图邻接表；0=未访问，1=当前递归路径，2=已完成。
vector<vector<int>> graph;
vector<int> state, result;

bool dfs_topological(int u) {
    state[u] = 1;
    for (int v : graph[u]) {
        if (state[v] == 1) return false; // 回到当前路径：发现有向环
        if (state[v] == 0 && !dfs_topological(v)) return false;
    }
    state[u] = 2;
    result.push_back(u);
    return true;
}

bool topological_dfs(int n) {
    state.assign(n, 0);
    result.clear();
    for (int u = 0; u < n; ++u) {
        if (state[u] == 0 && !dfs_topological(u)) {
            result.clear();
            return false;
        }
    }
    reverse(result.begin(), result.end()); // 逆后序才是拓扑序
    return true;
}
```

3. **迷宫/棋盘问题**（找到一条路径即可）
```cpp
bool dfs_maze(int x, int y, int target_x, int target_y) {
    if (x < 0 || x >= n || y < 0 || y >= m || maze[x][y] == 1) return false;
    if (x == target_x && y == target_y) return true;
    
    maze[x][y] = 1;  // 标记访问
    // 四个方向探索
    if (dfs_maze(x+1, y, target_x, target_y)) return true;
    if (dfs_maze(x-1, y, target_x, target_y)) return true;
    if (dfs_maze(x, y+1, target_x, target_y)) return true;
    if (dfs_maze(x, y-1, target_x, target_y)) return true;
    return false;
}
```

---

### BFS 适用场景

1. **最短路径问题**（边权相等）
```cpp
// 奇怪的电梯问题
int bfs_elevator(int start, int target) {
    if (start < 1 || start > N || target < 1 || target > N) return -1;
    if (start == target) return 0;
    queue<int> q;
    vector<int> dist(N+1, -1);
    
    dist[start] = 0;
    q.push(start);
    
    while (!q.empty()) {
        int curr = q.front(); q.pop();
        
        // 检查上下两个方向
        int up = curr + K[curr];
        if (up <= N && dist[up] == -1) {
            dist[up] = dist[curr] + 1;
            if (up == target) return dist[up];
            q.push(up);
        }
        
        int down = curr - K[curr];
        if (down >= 1 && dist[down] == -1) {
            dist[down] = dist[curr] + 1;
            if (down == target) return dist[down];
            q.push(down);
        }
    }
    return -1;
}
```

2. **层序遍历**
```cpp
// 二叉树的层序遍历
vector<vector<int>> levelOrder(TreeNode* root) {
    if (!root) return {};
    
    vector<vector<int>> result;
    queue<TreeNode*> q;
    q.push(root);
    
    while (!q.empty()) {
        int levelSize = q.size();
        vector<int> currentLevel;
        
        for (int i = 0; i < levelSize; i++) {
            TreeNode* node = q.front(); q.pop();
            currentLevel.push_back(node->val);
            
            if (node->left) q.push(node->left);
            if (node->right) q.push(node->right);
        }
        result.push_back(currentLevel);
    }
    return result;
}
```

3. **多源最短路径**
```cpp
// 多个起点同时搜索
void multi_source_bfs(vector<pair<int,int>>& sources) {
    queue<pair<int,int>> q;
    vector<vector<int>> dist(n, vector<int>(m, -1));
    
    for (auto [x, y] : sources) {
        dist[x][y] = 0;
        q.push({x, y});
    }
    
    int dx[] = {1, -1, 0, 0};
    int dy[] = {0, 0, 1, -1};
    
    while (!q.empty()) {
        auto [x, y] = q.front(); q.pop();
        
        for (int i = 0; i < 4; i++) {
            int nx = x + dx[i], ny = y + dy[i];
            if (nx >= 0 && nx < n && ny >= 0 && ny < m && dist[nx][ny] == -1) {
                dist[nx][ny] = dist[x][y] + 1;
                q.push({nx, ny});
            }
        }
    }
}
```

4. **拓扑排序的BFS版本（Kahn算法）**
```cpp
vector<int> topological_sort(int n, vector<vector<int>>& graph) {
    vector<int> in_degree(n, 0);
    for (int u = 0; u < n; u++) {
        for (int v : graph[u]) {
            in_degree[v]++;
        }
    }
    
    queue<int> q;
    for (int i = 0; i < n; i++) {
        if (in_degree[i] == 0) q.push(i);
    }
    
    vector<int> result;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        result.push_back(u);
        
        for (int v : graph[u]) {
            if (--in_degree[v] == 0) q.push(v);
        }
    }
    
    return result.size() == n ? result : vector<int>();  // 检查是否有环
}
```

---

## 选择指南

| 问题特征 | 推荐算法 | 原因 |
|---------|---------|------|
| 找最短路径（等权） | BFS | BFS第一次到达即最短 |
| 路径是否存在 | DFS 或 BFS | 普通图中均为 O(V+E)，按图结构和其他需求选择 |
| 需要所有简单路径 | DFS 回溯 | 维护当前路径并恢复访问标记；普通图遍历只访问各点一次，不能枚举所有路径 |
| 搜索深度浅、需要按层或最短路 | BFS | 按层扩展；仍需评估队列宽度 |
| 状态空间很大但宽度广 | DFS | 避免队列过大 |
| 需要回溯状态 | DFS | 递归自然支持回溯 |
| 层序遍历 | BFS | 天然按层处理 |

**总结**：
- **BFS**：求最短路径、层序遍历、等权图
- **DFS**：求是否存在路径、排列组合、回溯问题、拓扑排序