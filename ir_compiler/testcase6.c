struct TestStruct {
    int a;
    int b;
};

struct TestStruct test;
struct TestStruct *ptest;

test.a = 10;
test.b = test.a;
ptest->a = 20;

union TestUnion {
    int x;
    int y;
};

union TestUnion myUnion;
myUnion.x = 5;

union TestUnion *pUnion;
pUnion->y = 30;

