#include <stddef.h>

typedef struct RadixNode {
    unsigned key;
    struct RadixNode *next;
} RadixNode;

static RadixNode *radix_pass(RadixNode *head, unsigned place)
{
    RadixNode *first[10] = {NULL}, *last[10] = {NULL};
    while (head) {
        RadixNode *node = head;
        head = head->next;
        node->next = NULL;
        unsigned digit = node->key / place % 10;
        if (last[digit]) {
            last[digit]->next = node;  // 尾插保留桶内次序
        } else {
            first[digit] = node;
        }
        last[digit] = node;
    }
    RadixNode dummy = {0, NULL};
    RadixNode *tail = &dummy;
    for (int digit = 0; digit < 10; ++digit) {
        if (first[digit]) {
            tail->next = first[digit];
            tail = last[digit];
        }
    }
    return dummy.next;
}

RadixNode *radix_sort(RadixNode *head)
{
    unsigned max_key = 0;
    for (RadixNode *p = head; p; p = p->next) {
        if (p->key > max_key) {
            max_key = p->key;
        }
    }
    for (unsigned place = 1; max_key / place > 0; place *= 10) {
        head = radix_pass(head, place);
        if (max_key / place < 10) {
            break;  // 最高位处理完毕，避免 place 再乘 10
        }
    }
    return head;
}
