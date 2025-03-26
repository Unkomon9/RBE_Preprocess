# please end me 

# going compile using nvcc instead of our custom compiler (there is a function for this inside RBE insert)
# most likely going to be done in the same way as the preprocess script for the C source file. 
# there will be separate rule database from the one in the preprocess script which stores the IR tokens followed by the perf stat metrics 
# believe we are going to use RBE insert to perform the insertion of the rule into separate rule database file for cuda. 
# rule database for cuda will be called cuda.rbe 

# new rule format for cuda.rbe: ".*$0 \{ #3 = 0 ; @2 : #5 = #3 < 10 ; if #5 \{ #7 = \"Hello, World!\\n\" ; #4 call #7 ; #3 ; #3 = #3 \+ 1 ; goto @2 ; } else \{ } @0 : } #6 = 0 ; #8 access 0 = #6 ; return ;"~0:569928.0000000000:0.0001630000: = "int .*$0 int"~1:0.0000000000:0.0002150000 = 
# .*$0 contents ~0:metrics = devicefunction .*$0 mainfunction ~1:metrics 
# ~0 is for the IR tokens and ~1 is to indicate CUDA metrics. 
# devicefunction and mainfunction are the functions that are being called in the C source file (device function is the kernel function and main function is the main function of the C source file).
# at least that's what i think it happening. 
# anyway devicefunction and main function will get turned into a string and inserted just like the C source file (or IR tokens) into the rule database file. 

# devicefunction = ["__global__", "void", "(", ")", ";"]
# mainfunction = ["int", "main", "(", ")", "{", "}"]

# resulting in the following clause in the rule database file: "__global__ void ( ) ; .*$0 int main ( ) { }"~1:<time from perf stat>:<cpu cycles from perf stat>;

# which afterward it would set that clause to the C clause in the rule database file: .*$0 contents ~0:metrics = devicefunction .*$0 mainfunction ~1:metrics


# 1. create_new_rule(rbe_file, rule_num: int) -> None
# 2. insert_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num:list) -> None
# 3. compile(c_source: str) -> list[str] 
# 4. preprocess (don't know what this does yet)
# 5. main_ (c_source_file, ir_tokens, rule_database_file, insert_line)


import rbe_insert 
import sys
import os 
import subprocess 

# ensure the rule database file has at least rule_num lines. 
# if not, appends empty lines until the file has rule_num lines. 
def create_new_rule(rbe_file, rule_num: int) -> None: 
    print(f"Checking if rule {rule_num} exists in {rbe_file}...")
    
    # read existing lines from the file (if the file exists) 
    try: 
        with open(rbe_file, "r") as f: 
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
        
        # append empty lines until it reached the required rule_num 
        while len(lines) < rule_num: 
            lines.append("\n")
            
        # write the updated content back to the file
        with open(rbe_file, "w") as f: 
            f.writelines(lines)
            
        print(f"Rule {rule_num} ensured in {rbe_file}.")
        print(f"Rule {rule_num} created successfully in {rbe_file}.")
        
def compile_cuda(cuda_source : str) -> tuple[list[str], list[str]]: 
    if not os.path.exists(cuda_source): 
        print(f"CUDA source file '{cuda_source}' does not exist. Please check your current directory.")
        sys.exit(1)
        
    print(f"Compiling CUDA source file {cuda_source} using nvcc...")
    
    try: 
        # compile the CUDA source file using nvcc from the RBE insert script
        rbe_insert.nvcc_compile_c_source(cuda_source, "cuda_out")
        
        # placeholder for the extracting device function and main function from CUDA source file 
        device_function, main_function = [], []
        
        with open(cuda_source, "r") as f: 
            lines = f.readlines() 
            for line in lines: 
                tokens = line.strip().split()
                if "__global__" in tokens: 
                    device_function = tokens 
                elif "int" in tokens and "main" in tokens: 
                    main_function = tokens
                    
    except Exception as e:
        print(f"Error compiling {cuda_source}: {e}")
        return [], []
    
    return device_function, main_function 
        
# insert the rule into the rule database using rbe_insert.py 
def insert_cuda_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num): 
    x = bruh 