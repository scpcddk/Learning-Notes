#include <stdlib.h>

typedef struct TermNode {
    double coef;
    int expn;
    struct TermNode *next;
} TermNode;

TermNode *add_polynomials(TermNode *a, TermNode *b)
{
    TermNode dummy = {0, 0, NULL};
    TermNode *tail = &dummy;
    while (a && b) {
        TermNode *term;
        if (a->expn < b->expn) {
            term = a;
            a = a->next;
        } else if (b->expn < a->expn) {
            term = b;
            b = b->next;  // 接入 B 的较低次项后，推进 B
        } else {
            term = a;
            a = a->next;
            term->coef += b->coef;
            TermNode *merged = b;
            b = b->next;
            free(merged);
            if (term->coef == 0.0) {
                free(term);  // 同次项相消，结果不保留零项
                continue;
            }
        }
        tail->next = term;
        tail = term;
    }
    tail->next = a ? a : b;  // 剩余项已经按指数有序
    return dummy.next;
}
