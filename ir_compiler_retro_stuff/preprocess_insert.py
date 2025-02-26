# Functions:
#     create_new_rule(rule_num:int) -> None
#         - while number of lines of file < rule_num, add new empty line

#     insert_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num:int) -> None
#         - if rule_num doesn't exist, create_new_rule(rule_num)
#         - use rbe_insert.py to do this stuff

#     compile(c_source:str) -> ir_tokens
#         - run compiler on c_source

#     preprocess(ir_tokens:list[str], func_details) -> ir_tokens
#         - do some stuff that needs to be further looked at

#     main(c_source:str, func_details, rbe_file, rule_num)
#         - ir_tokens = compile(c_source)
#         - ir_tokens = preprocess(ir_tokens, func_details)
#         - insert_rule(c_source, ir_tokens, rbe_file, rule_num)


# So main will be what you call the program with. You will give it a C source file, the function's details (which we don't know yet), the rbe filename (the rule database), and the rule_num (which is just the problem number on the website [and the line number to insert on]).

# Main will call the compile function which will just import the compiler and run it    on the C source file (outputting the IR tokens).

# It will then call preprocess on the IR tokens to do something that we don't know yet. (it will replace the IR variables with something else)

# It will then call insert_rule which will use your rbe_insert.py script. You should have all of the arguments at that point.

import main
import rbe_insert
import sys
import os 
sys.path = [p for p in sys.path if p != os.getcwd()] # ensures that the local `types.py` file won't be picked up first
import subprocess
import re 
import json # for parsing args from command line

        
# ensure the rule database file has at least rule_num lines. 
# if not, appends empty lines until the file has rule_num lines. 
def create_new_rule(rbe_file, rule_num: int) -> None: 
    # rbe_file = "test.rbe"
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
    print(f"Rule {rule_num} created successfully in {rbe_file}")


# insert the rule into the rule database using rbe_insert.py 
def insert_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num:list) -> None: 
    # check if the rule exists in the rule database
    if not os.path.exists(rbe_file): 
        print(f"Rule database file '{rbe_file}' does not exist. Please check your current directory")
        create_new_rule(rbe_file, rule_num)
        
    # insert the rule into the rule database using rbe_insert.py  
    #print(f"\nCalling rbe_insert.py with arguments: {c_source}, {ir_tokens}, {rbe_file}, {rule_num}")
    print(f"\nCalling rbe_insert.py with arguments: {c_source}, {rbe_file}, {rule_num}")
    print(f"Inserting rule into {rbe_file} at line {rule_num}...")
    
    create_new_rule(rbe_file, rule_num)
    
    
    rbe_insert.main_(c_source, ir_tokens, rbe_file, rule_num)
    
    # try: 
    #     #subprocess.run(["python3", "rbe_insert.py", c_source, ir_tokens, rbe_file, rule_num], check=True)
    #     subprocess.run(["python3", "rbe_insert.py", c_source, " ".join(ir_tokens), rbe_file, str(rule_num)], check=True)
    #     print(f"Inserted rule into {rbe_file} at line {rule_num}.")
        
    # except subprocess.CalledProcessError as e:
    #     print(f"\n\nFailed to insert rule into {rbe_file}:\n\n{e}")
    #     sys.exit(1)

def compile(c_source: str) -> list[str]:
    print(f"Compiling {c_source} using main.py to generate IR tokens...")
    
    ir_tokens, ir_types = main.Main().start(["./main.py", c_source])
    # result = subprocess.run(
    #     ['python3', 'main.py', c_source],  # Call main.py from the compiler to compile the C source into IR tokens 
    #     capture_output=True,  # capture standard output and error
    #     text=True  # return output as a string, not bytes
    # )
    
    # # check for errors during the subprocess execution
    # if result.returncode != 0:
    #     print(f"Error while running main.py: {result.stderr}")
    #     print(f"Compilation of {c_source} failed. Exiting...")
    #     return []
    
    # # prints it out in one line 
    # ir_tokens = result.stdout.splitlines()  # adjust this based on the actual format
    
    print(f"Compiled {c_source} into IR tokens.\n")
    print(f"Compilation successful.\nIR tokens:\n{ir_tokens}")
    return ir_tokens


#args = {'#1': '$1'}
def preprocess(ir_tokens, args): 
    special_chars = set(['.', '+', '*', '|', '{', '$', '\\', '"']) # set of special characters that need to be escaped
    
    
    # # prints it out in one line 
    # ir_tokens = result.stdout.splitlines()  # adjust this based on the actual format
    
    print(f"Compiled {c_source} into IR tokens.\n")
    print(f"Compilation successful.\nIR tokens:\n{ir_tokens}")
    print("\n\n\n")
    print(f"\nPreprocessing IR tokens:\n{ir_tokens}")

    for i in range(len(ir_tokens)):
        old = ir_tokens[i]
        
        # escape special characters 
        new_token = ""
        for char in ir_tokens[i]:
            if char in special_chars:
                new_token += "\\"
            new_token += char
        ir_tokens[i] = new_token

        if ir_tokens[i] in args: 
            ir_tokens[i] += args[ir_tokens[i]] # replace the IR token with the corresponding argument value 
            
            print(f"Replaced token {old} -> {ir_tokens}")
    
    print("\n\n\n")
    print(f"\nPreprocess completed successfully.\nProcessed IR tokens:\n{ir_tokens}")
    return " ".join(ir_tokens)

# main function to compile the c source file, preprocess the IR tokens, and insert the rule into the rule database.
def main_(c_source:str, args:dict, rbe_file:str, rule_num:int):
    print(f"Preparing to insert rule into {rbe_file} at line {rule_num}...")
    
    ir_tokens = compile(c_source)
    
    # TODO: FIX THIS PLEASE!!!
    ir_tokens = [x.token for x in ir_tokens[0].tokens]
    
    ir_tokens = preprocess(ir_tokens, args)
    
    insert_rule(c_source, ir_tokens, rbe_file, rule_num)
    
    print("Process completed.")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 prepare_rbe_insert.py <c_source_file> <args> <rule_database_file> <rule_num>")
        sys.exit(1)
        
    c_source = sys.argv[1] # c source file 
    
    try: 
        args = json.loads(sys.argv[2]) # arguments to replace in the IR tokens (args = {'#1': '$1'})
        if not isinstance(args, dict): 
            raise ValueError("Parsed args is not a dictionary.")
    
    except json.JSONDecodeErrors as e: 
        print(f"Failed to parse args: {e}")
        sys.exit(1)
    
    
    rbe_file = sys.argv[3]  # rule database file 
    rule_num = int(sys.argv[4])  # rule number to insert the rule 
    
    main_(c_source, args, rbe_file, rule_num)
