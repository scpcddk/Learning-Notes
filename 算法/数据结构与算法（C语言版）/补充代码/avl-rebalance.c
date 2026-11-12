typedef struct AvlNode {
    int key, height;
    struct AvlNode *left, *right;
} AvlNode;

static int height(const AvlNode *p)
{
    return p ? p->height : 0;
}

static void update_height(AvlNode *p)
{
    int left = height(p->left), right = height(p->right);
    p->height = 1 + (left > right ? left : right);
}

static int balance(const AvlNode *p)
{
    return height(p->left) - height(p->right);
}

static AvlNode *rotate_right(AvlNode *a)
{
    AvlNode *b = a->left;
    a->left = b->right;  // 中间子树仍在 a 与 b 之间
    b->right = a;
    update_height(a);
    update_height(b);
    return b;
}

static AvlNode *rotate_left(AvlNode *a)
{
    AvlNode *b = a->right;
    a->right = b->left;
    b->left = a;
    update_height(a);
    update_height(b);
    return b;
}

AvlNode *rebalance(AvlNode *a)
{
    update_height(a);
    if (balance(a) > 1) {
        if (balance(a->left) < 0) {  // LR 先旋转左孩子
            a->left = rotate_left(a->left);
        }
        return rotate_right(a);     // LL 直接右旋
    }
    if (balance(a) < -1) {
        if (balance(a->right) > 0) {  // RL 先旋转右孩子
            a->right = rotate_right(a->right);
        }
        return rotate_left(a);       // RR 直接左旋
    }
    return a;
}
