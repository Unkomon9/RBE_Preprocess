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


import subprocess
import sys

# need to change, doesn't look right 
def create_new_rule(rule_num:int) -> None: 
    with open("rbe_file.txt", "r") as f:
        lines = f.readlines()
        while len(lines) < rule_num:
            lines.append("\n")
    with open("rbe_file.txt", "w") as f:
        f.writelines(lines)

def insert_rule(c_source:str, ir_tokens:list[str], rbe_file, rule_num:list) -> None: 
    if rule_num not in range(1, 100): 
        print("Rule number does not exist")
        return 
    create_new_rule(rule_num)
    

def compile(c_source:str) -> list[str]: 
    try: 
        subprocess.run(["gcc", c_source])
        return ["ir", "tokens"]
    
    except Exception as e: 
        print(f"Failed to compile C source: {e}")
        sys.exit(1)
    
    
def preprocess(ir_tokens:list[str], function_details) -> ir_tokens:
    # do some stuff that needs to be further looked at
    return ir_tokens

def main(c_source:str, function_details, rbe_file, rule_num):
    ir_tokens = compile(c_source)
    ir_tokens = preprocess(ir_tokens, function_details)
    insert_rule(c_source, ir_tokens, rbe_file, rule_num)

