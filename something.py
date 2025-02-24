# [Website]
# -> submit C source code, problem





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

import re 
import sys
import os 
sys.path = [p for p in sys.path if p != os.getcwd()] # ensures that the local `types.py` file won't be picked up first
import subprocess

        
# ensure the rule database file has at least rule_num lines. 
# if not, appends empty lines until the file has rule_num lines. 
# def create_new_rule(rule_num: int) -> None: 
#     rbe_file = "rule_database.txt"
    
#     # read existing lines from the file (if the file exists)
#     try: ef
#         with open(rbe_file, "r") as f: 
#             lines = f.readlines() 
#     except FileNotFoundError: 
#         lines = [] 
        
#     # append empty lines until it reached the required rule_num 
#     while len(lines) < rule_num: 
#         lines.append("\n")
        
#     # write the updated content back to the file 
#     with open(rbe_file, "w") as f: 
#         f.writelines(lines)
    
#     print(f"Rule {rule_num} created successfully in {rbe_file}")


# insert the rule into the rule database using rbe_insert.py 
# def insert_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num:list) -> None: 
#     # check if the rule exists in the rule database
#     if not os.path.exists(rbe_file): 
#         create_new_rule(rule_num)
        
#     # insert the rule into the rule database using rbe_insert.py  
#     create_new_rule(rule_num)
#     subprocess.run(["python3", "rbe_insert.py", c_source, ir_tokens, rbe_file, rule_num], check=True)
#     print(f"Inserted rule into {rbe_file} at line {rule_num}.")

def compile(c_source: str) -> list[str]:
    # Simulate calling main.py using subprocess
    result = subprocess.run(
        ['python3', 'main.py', c_source],  # Call main.py with the test source file
        capture_output=True,  # Capture standard output and error
        text=True  # Return output as a string, not bytes
    )
    
    # Check for errors during the subprocess execution
    if result.returncode != 0:
        print(f"Error while running main.py: {result.stderr}")
        return []
    
    # prints it out in one line 
    ir_tokens = result.stdout.splitlines()  # Adjust this based on the actual format
    
    print(f"Compiled {c_source} into IR tokens.")
    return ir_tokens


args = {'#1': '$1'}
def preprocess(ir_tokens, args): 
    special_chars = {'.', '+', '*', '|', '{', '$', '\\', '"'} # set of special characters that need to be escaped

    for i in range(len(ir_tokens)): 
        if ir_tokens[i] in args: 
            # escape special characters in the token by prepending a backslash 
            escape_tokens = ''.join(f'\\{char}' if char in special_chars else char for char in args[ir_tokens[i]])
            ir_tokens[i] = escape_tokens # replace the original token with the escaped token 
            
            print("Processed IR tokens: ", ir_tokens)
    
    return ir_tokens

# main function to compile the c source file, preprocess the IR tokens, and insert the rule into the rule database.
# def main(c_source:str, function_details, rbe_file, rule_num):
#     ir_tokens = compile(c_source)
#     ir_tokens = preprocess(ir_tokens, function_details)
#     insert_rule(c_source, ir_tokens, rbe_file, rule_num)
#     print("Process completed.")


# if __name__ == "__main__":
#     if len(sys.argv) != 5:
#         print("Usage: python3 rbe_main.py <c_source_file> <function_details> <rule_database_file> <rule_num>")
#         sys.exit(1)
        
#     c_source = sys.argv[1] # c source file 
#     function_details = sys.argv[2]  # placeholder, modify when further information given 
#     rbe_file = sys.argv[3]  # rule database file 
#     rule_num = int(sys.argv[4])  # rule number to insert the rule 
    
#     main(c_source, function_details, rbe_file, rule_num)



# test for the compile function
# if __name__ == "__main__":
#     test_c_source = "testcase1.c"
#     ir_tokens = compile(test_c_source)
#     print("Generated IR tokens: ", ir_tokens)
