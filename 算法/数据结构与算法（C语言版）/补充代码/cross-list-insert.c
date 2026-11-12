#include <stdlib.h>

typedef struct OLNode {
    int i, j, e;
    struct OLNode *right, *down;
} OLNode, *OLink;

typedef struct {
    OLink *rhead, *chead;
    int mu, nu, tu;
} CrossList;

int cross_insert(CrossList *matrix, int i, int j, int e)
{
    if (i < 1 || i > matrix->mu || j < 1 || j > matrix->nu || e == 0) {
        return 0;
    }
    OLink *row = &matrix->rhead[i];
    while (*row && (*row)->j < j) {
        row = &(*row)->right;
    }
    if (*row && (*row)->j == j) {
        return 0;
    }
    OLink *col = &matrix->chead[j];
    while (*col && (*col)->i < i) {
        col = &(*col)->down;
    }
    OLink node = malloc(sizeof *node);
    if (!node) {
        return 0;
    }
    *node = (OLNode){i, j, e, *row, *col};
    *row = node;
    *col = node;  // 行链和列链指向同一结点
    ++matrix->tu;
    return 1;
}
