#include <limits.h>

typedef struct {
    long long weight;
    int lchild, rchild, parent;
} HuffNode;

static int smallest_root(const HuffNode tree[], int end, int skip)
{
    int best = -1;
    for (int i = 0; i < end; ++i) {
        if (i != skip && tree[i].parent == -1 &&
            (best == -1 || tree[i].weight < tree[best].weight)) {
            best = i;
        }
    }
    return best;
}

int build_huffman(const long long weights[], int n, HuffNode tree[])
{
    if (n <= 0 || n > INT_MAX / 2 + 1) {
        return -1;
    }
    int node_count = n + (n - 1);
    for (int i = 0; i < n; ++i) {
        tree[i] = (HuffNode){weights[i], -1, -1, -1};
    }
    for (int k = n; k < node_count; ++k) {
        int a = smallest_root(tree, k, -1);
        int b = smallest_root(tree, k, a);
        tree[k] = (HuffNode){tree[a].weight + tree[b].weight, a, b, -1};
        tree[a].parent = tree[b].parent = k;  // 两棵子树并入新根
    }
    return node_count - 1;
}
