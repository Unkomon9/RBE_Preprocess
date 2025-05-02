int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

#include <stdio.h>
#include <stdlib.h>
int a = 17;
int b = 13;

int main() {
    int result = gcd(a, b);

    printf("%d\n", result);

    return 0;
}
