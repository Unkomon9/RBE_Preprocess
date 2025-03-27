#include <cuda_runtime.h>

__global__ void multiply(int* a, int* b, int* c) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    c[i] = a[i] * b[i];
}

int main() {
    int a[] = {1, 2, 3};
    int b[] = {1, 2, 3};
    int c[3];

    multiply<<<1, 3>>>(a, b, c);

    return 0;
}
