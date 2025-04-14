

// This is a test comment \
How do you do?
#define \
    testing 2

# ifdef testing
#undef testing

#define test(a, b) \
    printf("%s%s", a, b)
#else
#undef testing
#define test(b, c) \
    echo("hello, world")

#endif

#ifndef TESTING

/*
 * Multiple lines /*
 *
 */
int main(int argc, char** argv){

testLabel:

    if (argc < 2){
        printf("HELLO, WORLD!\n");
    }

    goto testLabel;

    int d = '\n';
    d++;
    d--;

    auto float a = 2.3;
    register double b = 0.3;
    int c = a / b;
    return c;
}
#endif
