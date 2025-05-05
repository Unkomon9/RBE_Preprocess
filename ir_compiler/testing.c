int gcd(int a, int b) {
    if (a == 0){
        return b;
    }
    if (b == 0){
        return a;
    }

    // Count common factors of 2
    int shift = 0;
    while (((a | b) & 1) == 0) {
        a >>= 1;
        b >>= 1;
        shift++;
    }

    // Remove factors of 2 from a
    while ((a & 1) == 0){
        a >>= 1;
    }

    while (b != 0) {
        // Remove factors of 2 from b
        while ((b & 1) == 0){
            b >>= 1;
        }

        // Ensure a <= b
        if (a > b) {
            int temp = a;
            a = b;
            b = temp;
        }

        b = b - a;
    }

    // Restore common factors of 2
    return a << shift;
}

#include <stdio.h>
#include <stdlib.h>
int a = 100;
int b = 85;

int main() {
    int result = gcd(a, b);

    printf("%d\n", result);

    return 0;
}
