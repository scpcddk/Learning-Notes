#include <limits.h>

#define FLOYD_INF (LLONG_MAX / 4)

void floyd(int n, long long d[n][n])
{
    for (int k = 0; k < n; ++k) {  // 本轮允许使用中间顶点 k
        for (int i = 0; i < n; ++i) {
            if (d[i][k] == FLOYD_INF) {
                continue;
            }
            for (int j = 0; j < n; ++j) {
                if (d[k][j] == FLOYD_INF) {
                    continue;  // 两段都可达时才尝试拼接
                }
                long long via_k = d[i][k] + d[k][j];
                if (via_k < d[i][j]) {
                    d[i][j] = via_k;
                }
            }
        }
    }
}
