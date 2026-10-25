#include <algorithm>
#include <iostream>
#include <limits>
#include <vector>
using namespace std;

// 演示：无向、非负权图。有限最短距离须小于 INF。
// 无向图的负权边会产生可反复经过的负权闭合游走，本实现拒绝负权。
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    if (!(cin >> n >> m) || n < 1 || m < 0) return 1;
    using ll = long long;
    const ll INF = numeric_limits<ll>::max() / 4;
    vector<vector<ll>> dist(n + 1, vector<ll>(n + 1, INF));
    for (int i = 1; i <= n; ++i) dist[i][i] = 0;
    for (int i = 0; i < m; ++i) {
        int u, v;
        ll w;
        if (!(cin >> u >> v >> w) || u < 1 || u > n || v < 1 || v > n || w < 0 || w >= INF)
            return 1;
        dist[u][v] = min(dist[u][v], w);
        dist[v][u] = min(dist[v][u], w);
    }
    for (int k = 1; k <= n; ++k) {
        for (int i = 1; i <= n; ++i) {
            if (dist[i][k] == INF) continue;
            for (int j = 1; j <= n; ++j) {
                if (dist[k][j] == INF) continue;
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
    }
    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= n; ++j) {
            if (j > 1) cout << ' ';
            if (dist[i][j] == INF) cout << "INF";
            else cout << dist[i][j];
        }
        cout << '\n';
    }
    return 0;
}
