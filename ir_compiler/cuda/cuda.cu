
__global__ void add(int* a, int* b, int* c){
    int i = threadIdx.x + blockDim.x * blockIdx.x;
    c[i] = a[i] + b[i];
}

int main(int argc, char** argv){
    int* a = {1, 2, 3};
    int* b = {1, 2, 3};
    int* c;
    add<<<1, 3>>>(a, b, c);
    return 0;
}


