#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int n, m;  // n: 点数, m: 边数
const int INF = 1e9;  // 定义无穷大，表示不可达

int main() {
    // 输入输出优化，提高读写速度
    ios::sync_with_stdio(false);
    cin.tie(nullptr); 
    
    // 读入点数和边数
    cin >> n >> m;
    
    // 距离矩阵，dist[i][j] 表示从 i 到 j 的最短距离
    int dist[101][101];
    
    // 初始化距离矩阵
    for(int i = 1; i <= n; i++) {
        for(int j = 1; j <= n; j++) {
            if(i == j) 
                dist[i][j] = 0;      // 自己到自己的距离为0
            else 
                dist[i][j] = INF;    // 初始化为无穷大，表示不可达
        }
    }
    
    // 读入所有边
    for(int i = 0; i < m; i++) {
        int u, v, w;  // 边的起点u，终点v，权值w
        cin >> u >> v >> w;
        
        // 由于可能有重边（多条u到v的边），取权值最小的那条
        dist[u][v] = min(dist[u][v], w);
        dist[v][u] = min(dist[v][u], w);  // 无向图，双向赋值
    }
    
    // Floyd-Warshall 算法核心部分
    // 三重循环：枚举中间点k，起点i，终点j
    for(int k = 1; k <= n; k++) {           // 枚举中间点
        for(int i = 1; i <= n; i++) {       // 枚举起点
            for(int j = 1; j <= n; j++) {   // 枚举终点
                // 只有当中转点k到起点i和终点j都可达时才更新
                // 防止INF相加导致溢出
                if(dist[i][k] < INF && dist[k][j] < INF) {
                    // 状态转移：考虑通过k中转是否更短
                    // dist[i][j] = min(直接走i->j, 先走i->k再走k->j)
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
                }
            }
        }
    }
    
    // 输出结果：所有点对之间的最短距离
    for(int i = 1; i <= n; i++) {
        for(int j = 1; j <= n; j++) {
            cout << dist[i][j] << " ";  // 输出i到j的最短距离
        }
        cout << endl;  // 每行输出后换行
    }
    
    return 0;
}