## DFS 和 BFS 的核心区别

| 特性 | DFS (深度优先搜索) | BFS (广度优先搜索) |
|------|-------------------|-------------------|
| **数据结构** | 栈（递归或显式栈） | 队列 |
| **空间复杂度** | O(h)，h为树的高度 | O(w)，w为树的宽度 |
| **特点** | 一条路走到黑，然后回溯 | 层层推进，按层遍历 |
| **是否保证最短路径** | 否（除非全遍历） | 是（边权相等时） |
| **适用场景** | 连通性、路径存在性、拓扑排序 | 最短路径、层序遍历 |

---

## 具体使用场景

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
// 全排列
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
void dfs_topological(int u) {
    visited[u] = true;
    for (int v : graph[u]) {
        if (!visited[v]) dfs_topological(v);
    }
    result.push_back(u);  // 后序加入结果
}
```

3. **迷宫/棋盘问题**（找到一条路径即可）
```cpp
bool dfs_maze(int x, int y, int target_x, int target_y) {
    if (x == target_x && y == target_y) return true;
    if (x < 0 || x >= n || y < 0 || y >= m || maze[x][y] == 1) return false;
    
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
| 路径是否存在 | DFS | 找到即返回，空间小 |
| 需要所有路径 | DFS/BFS都可 | 需要完整遍历 |
| 状态空间很大但深度浅 | BFS | 避免递归过深 |
| 状态空间很大但宽度广 | DFS | 避免队列过大 |
| 需要回溯状态 | DFS | 递归自然支持回溯 |
| 层序遍历 | BFS | 天然按层处理 |

**总结**：
- **BFS**：求最短路径、层序遍历、等权图
- **DFS**：求是否存在路径、排列组合、回溯问题、拓扑排序