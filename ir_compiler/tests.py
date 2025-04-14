import debug
debug.TESTING = 1
debug.DEBUG = 0

import os

import compiler

class Test:
    def __init__(self, filename):
        self.filename = filename
        self.comp = compiler.Compiler()

    def run_test(self):
        print("++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f"TESTCASE: {self.filename}")
        try:
            with open(self.filename, 'r') as f:
                print(f.read())
        except:
            pass
        self.result = self.comp.compile(self.filename)
        print("----------------------------------------")
        print(f"TESTCASE: {self.filename}")
        print(self.result)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++")


class TestSuite:
    def __init__(self, dirname):
        self.dirname = dirname
        self.run_tests()

    def run_tests(self):
        test_files = os.listdir(self.dirname)
        test_files.sort()
        test_files = [os.path.join(self.dirname, x) for x in test_files]
        test_files = [x for x in test_files if os.path.isfile(x)]
        for test_file in test_files:
            t = Test(test_file)
            t.run_test()

if __name__ == '__main__':
    # test preprocessor
    TestSuite("testing/preprocessor")

