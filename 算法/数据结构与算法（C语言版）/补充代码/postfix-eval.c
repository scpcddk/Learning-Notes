#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

int eval_postfix(const char *const tokens[], size_t count, double *result)
{
    if (count == 0) {
        return 0;
    }
    double stack[count];
    size_t top = 0;
    for (size_t i = 0; i < count; ++i) {
        const char *token = tokens[i];
        char op = token[0];
        if (op && token[1] == '\0' && strchr("+-*/", op)) {
            if (top < 2) {
                return 0;
            }
            double right = stack[--top];  // 减法和除法先弹右操作数
            double left = stack[--top];
            double value;
            switch (op) {
            case '+': value = left + right; break;
            case '-': value = left - right; break;
            case '*': value = left * right; break;
            default:
                if (right == 0.0) {
                    return 0;
                }
                value = left / right;
                break;
            }
            if (!isfinite(value)) {
                return 0;
            }
            stack[top++] = value;
        } else {
            char *end;
            double value = strtod(token, &end);
            if (end == token || *end != '\0' || !isfinite(value)) {
                return 0;
            }
            stack[top++] = value;
        }
    }
    if (top != 1) {
        return 0;
    }
    *result = stack[0];
    return 1;
}
