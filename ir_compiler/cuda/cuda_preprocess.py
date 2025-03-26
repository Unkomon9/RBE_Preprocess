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

# resulting in the following clause in the rule database file: 
# "__global__ void ( ) ; .*$0 int main ( ) { }"~1:<time from perf stat>:<cpu cycles from perf stat>;

# which afterward it would set that clause to the C clause in the rule database file: .*$0 contents ~0:metrics = devicefunction .*$0 mainfunction ~1:metrics


# 1. create_new_rule(rbe_file, rule_num: int) -> None
# 2. insert_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num:list) -> None
# 3. compile(c_source: str) -> list[str] 
# 4. preprocess (don't know what this does yet)
# 5. main_ (c_source_file, ir_tokens, rule_database_file, insert_line)


import rbe_insert
import compiler 
import sys
import os 
import subprocess 

# ensure the rule database file has at least rule_num lines. 
# if not, appends empty lines until the file has rule_num lines. 
def create_new_rule(cuda_rbe_file, rule_num: int) -> None: 
    print(f"Checking if rule {rule_num} exists in {cuda_rbe_file}...")
    
    # read existing lines from the file (if the file exists) 
    try: 
        with open(cuda_rbe_file, "r") as f: 
            lines = f.readlines()
    except FileNotFoundError:
        lines = []
        
        # append empty lines until it reached the required rule_num 
        while len(lines) < rule_num: 
            lines.append("\n")
            
        # write the updated content back to the file
        with open(cuda_rbe_file, "w") as f: 
            f.writelines(lines)
            
        print(f"Rule {rule_num} ensured in {cuda_rbe_file}.")
        print(f"Rule {rule_num} created successfully in {cuda_rbe_file}.")
        

def compile(cuda_source: str) -> list[str]: 
    # compile the cuda source file using the compiler 
    if not os.path.exists(cuda_source): 
        print(f"CUDA source file '{cuda_source}' does not exist. Please check your current directory.")
        return [] 
        
    print(f"Compiling {cuda_source} using compile function from compiler.py...)") 
    
    try: 
        # compile the cuda source file using compiler.py 
        cuda_tokens = compiler.Compiler().compile(cuda_source)
        print(f"\nCompilation successful. Generated cuda tokens: {cuda_tokens}")
    
    except: 
        print(f"Error compiling {cuda_source}.")
        return []
    
    print(f"Compiled {cuda_source} into cuda tokens strings.\n")
    print(f"Compile successful.\nCUDA tokens: {cuda_tokens}")
    return cuda_tokens 


def insert_rule(cuda_source, cuda_tokens:list[str], cuda_rbe_file, rule_num:int) -> None: 
    # check if the rule exists in the rule database 
    if not os.path.exists(cuda_rbe_file): 
        print(f"Rule database file '{cuda_rbe_file}' does not exist. Please check your current directory.")
        create_new_rule(cuda_rbe_file, rule_num)
        
    # insert the rule into the rule database using rbe_insert.py 
    print(f"\nCalling rbe_insert.py with arguments: {cuda_source}, {cuda_tokens}, {cuda_rbe_file}, {rule_num}")
    print(f"Inserting rule into {cuda_rbe_file} at line {rule_num}...")
    
    create_new_rule(cuda_rbe_file, rule_num) 
    
    rbe_insert.main_(cuda_source, cuda_tokens, cuda_rbe_file, rule_num) 

def main_(cuda_source:str, rbe_file:str, rule_num:int) -> None:
    print(f"Preprocessing {cuda_source}...")
    cuda_tokens = compile(cuda_source)  
    print(cuda_tokens)
    insert_rule(cuda_source, cuda_tokens, rbe_file, rule_num)
    print("\nPreprocess completed.")



if __name__ == "__main__": 
    if len(sys.argv) != 2: 
        print("Usage: python3 cuda_preprocess.py <cuda_source_file>")
        sys.exit(1) 
        
    cuda_source = sys.argv[1] # cuda source file 
    rbe_file = sys.argv[2] # rule database file for cuda 
    rule_num = int(sys.argv[3]) # rule number to insert into the rule database file 
    
    main_(cuda_source, rbe_file, rule_num)

