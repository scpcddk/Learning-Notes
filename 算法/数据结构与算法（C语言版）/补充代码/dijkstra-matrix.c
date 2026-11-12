#include <limits.h>
#include <stdbool.h>

#define DIJKSTRA_INF (LLONG_MAX / 4)

bool dijkstra_matrix(int n, long long edges[n][n], int src,
                     long long dist[n], int prev[n])
{
    if (src < 0 || src >= n) {
        return false;
    }

    bool settled[n];
    for (int v = 0; v < n; ++v) {
        settled[v] = false;
        dist[v] = DIJKSTRA_INF;
        prev[v] = -1;
    }
    dist[src] = 0;

    for (int step = 0; step < n; ++step) {
        int u = -1;
        for (int v = 0; v < n; ++v) {
            if (!settled[v] && (u == -1 || dist[v] < dist[u])) {
                u = v;
            }
        }
        if (u == -1 || dist[u] == DIJKSTRA_INF) {
            break;  // 剩余顶点都不可达
        }

        settled[u] = true;
        for (int v = 0; v < n; ++v) {
            long long weight = edges[u][v];
            if (settled[v] || weight == DIJKSTRA_INF) {
                continue;
            }
            if (weight >= DIJKSTRA_INF - dist[u]) {
                continue;  // 结果不在可表示的有限距离范围内
            }
            long long via_u = dist[u] + weight;
            if (via_u < dist[v]) {
                dist[v] = via_u;
                prev[v] = u;
            }
        }
    }
    return true;
}
