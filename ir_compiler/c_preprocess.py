import compiler
import rbe_insert
import sys
import os 
import subprocess
import re 
import json # for parsing args from command line

        
# ensure the rule database file has at least rule_num lines. 
# if not, appends empty lines until the file has rule_num lines. 
def create_new_rule(rbe_file, rule_num: int) -> None: 
    # rbe_file = "test.rbe"
    #print(f"Checking if rule {rule_num} exists in {rbe_file}...")
    
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
    
    #print(f"Rule {rule_num} ensured in {rbe_file}.")    
    #print(f"Rule {rule_num} created successfully in {rbe_file}")


# insert the rule into the rule database using rbe_insert.py 
def insert_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num:list) -> None: 
    # check if the rule exists in the rule database
    if not os.path.exists(rbe_file): 
        #print(f"Rule database file '{rbe_file}' does not exist. Please check your current directory")
        create_new_rule(rbe_file, rule_num)
        
    # insert the rule into the rule database using rbe_insert.py  
    #print(f"\nCalling rbe_insert.py with arguments: {c_source}, {ir_tokens}, {rbe_file}, {rule_num}")
    #print(f"Inserting rule into {rbe_file} at line {rule_num}...")
    
    create_new_rule(rbe_file, rule_num)
    
    
    rbe_insert.main_(c_source, ir_tokens, rbe_file, rule_num)

def compile(c_source: str, func_name) -> list[str]:
    
    if not os.path.exists(c_source): 
        #print(f"Error: {c_source} does not exist.")
        return []
    
    #print(f"Compiling {c_source} using main.py to generate IR tokens...")
    
    try: 
        ir_tokens = compiler.Compiler().compile(c_source)
    
    except: 
        #print(f"Error compiling {c_source}.")
        return [] 

    for tok in ir_tokens:
        if tok == "#FUNC":
            if tok.name == func_name:
                return tok.value

    return []

def preprocess(ir_tokens, args): 
    special_chars = set(['.', '+', '*', '|', '{', '$', '\\', '"']) # set of special characters that need to be escaped

    for i in range(len(ir_tokens)):
        if ir_tokens[i][0] == "#":
            ir_tokens[i].token = ir_tokens[i].token + "(" + "".join([x.token for x in ir_tokens[i].type])
    
    
    # # prints it out in one line 
    # ir_tokens = result.stdout.splitlines() 
    
    #print(f"Compiled {c_source} into IR tokens.\n")
    #print(f"Compilation successful.\nIR tokens:\n{ir_tokens}")
    #print("\n\n\n")
    #print(f"\nPreprocessing IR tokens:\n{ir_tokens}")

    #for i in range(len(ir_tokens)):
    #    old = ir_tokens[i]
        
    #    # escape special characters 
    #    new_token = ""
    #    for char in ir_tokens[i]:
    #        if char in special_chars:
    #            new_token += "\\"
    #        new_token += char
    #    ir_tokens[i] = new_token

    #    if ir_tokens[i] in args: 
    #        ir_tokens[i] += args[ir_tokens[i]] # replace the IR token with the corresponding argument value 
            
    #        #print(f"Replaced token {old} -> {ir_tokens}")
    
    #print("\n\n\n")
    #print(f"\nPreprocess completed successfully.\nProcessed IR tokens:\n{ir_tokens}")
    return " ".join(ir_tokens)

# main function to compile the c source file, preprocess the IR tokens, and insert the rule into the rule database.
def main_(c_source:str, args:dict, rbe_file:str, rule_num:int, func_name):
    #print(f"Preparing to insert rule into {rbe_file} at line {rule_num}...")
    
    ir_tokens = compile(c_source, func_name)
    
    # TODO: fix this stuff 
    ir_tokens = preprocess(ir_tokens, args)
    
    insert_rule(c_source, ir_tokens, rbe_file, rule_num)
    #print("Process completed.")     


if __name__ == "__main__":
    if len(sys.argv) != 7:
        #print("Usage: python3 c_preprocess.py <c_source_file> <args> <rule_database_file> <rule_num>")
        sys.exit(1)
        
    c_source = sys.argv[1] # c source file 
    sys.stdout = open(os.devnull, "w")

    num_args = sys.argv[2]
    func_name = sys.argv[3]
    
    try: 
        args = json.loads(sys.argv[4]) # arguments to replace in the IR tokens (args = '{"#1": "$1"}')
        if not isinstance(args, dict): 
            raise ValueError("Parsed args is not a dictionary.")
    
    except json.JSONDecodeErrors as e: 
        #print(f"Failed to parse args: {e}")
        sys.exit(1)
    
    
    rbe_file = sys.argv[5]  # rule database file 
    rule_num = int(sys.argv[6])  # rule number to insert the rule 
    
    main_(c_source, args, rbe_file, rule_num, func_name)
    sys.stdout = sys.__stdout__
