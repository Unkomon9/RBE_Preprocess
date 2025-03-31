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
        print(f"\nCompilation successful.")
        print(f"Generated cuda tokens: {cuda_tokens}")
    
    except: 
        print(f"Error compiling {cuda_source}.")
        return []
    
    print(f"Compiled {cuda_source} into cuda tokens strings.\n")
    print(f"Compile successful.\nCUDA tokens: {cuda_tokens}")
    return " ".join(map(str,cuda_tokens)) # formatted string of cuda tokens 


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
    insert_rule(cuda_source, cuda_tokens, rbe_file, rule_num)
    print("\nPreprocess completed.")



if __name__ == "__main__": 
    if len(sys.argv) != 4: 
        print("Usage: python3 cuda_preprocess.py <cuda_source_file> <rule_database_file> <rule_num>")
        sys.exit(1) 
        
    cuda_source = sys.argv[1] # cuda source file 
    rbe_file = sys.argv[2] # rule database file for cuda 
    rule_num = int(sys.argv[3]) # rule number to insert into the rule database file 
    
    main_(cuda_source, rbe_file, rule_num)

