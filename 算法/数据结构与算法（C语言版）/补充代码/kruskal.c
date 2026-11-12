typedef struct {
    int u, v, weight;
} Edge;

static int component_root(int parent[], int v)
{
    while (parent[v] != v) {
        parent[v] = parent[parent[v]];
        v = parent[v];
    }
    return v;
}

int kruskal(int n, const Edge edges[], int m, Edge picked[])
{
    if (n <= 1) {
        return 0;
    }
    int parent[n], size[n];
    for (int v = 0; v < n; ++v) {
        parent[v] = v;
        size[v] = 1;
    }
    int count = 0;
    for (int i = 0; i < m && count < n - 1; ++i) {
        int a = component_root(parent, edges[i].u);
        int b = component_root(parent, edges[i].v);
        if (a == b) {
            continue;  // 两端已经连通，加入该边会成环
        }
        if (size[a] < size[b]) {
            int temp = a;
            a = b;
            b = temp;
        }
        parent[b] = a;
        size[a] += size[b];
        picked[count++] = edges[i];
    }
    return count;
}
