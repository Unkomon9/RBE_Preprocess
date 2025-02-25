# You are given:
#     filename of C source code
#     filename IR of that C file (given from compiler)
#     filename of rule database
#     line number to insert on

# Compile the C source with gcc
# Run the Compiled program with perf stat to get metrics
# Insert the rules like this

# Existing Database file
# ```
# "else if":1:2 eq "else { if }":3:4
# ```

# After insert of "elif" on line 1 of that file with metrics 20 and 13
# ```
# "elif":20:13 eq "else if":1:2 eq "else { if }":3:4
# ```

import subprocess
import os 
import sys 
import re   

# compiles the c source file using gcc and outputs it to a.out
def compile_c_source(c_source_file, output_file="a.out"): 
    try: 
        subprocess.run(["gcc", c_source_file, "-o", output_file], check=True)
        print(f"Compiled {c_source_file} to {output_file}.")
    except: 
        print(f"Error compiling {c_source_file}.")
        sys.exit(1)

# runs the compiled program with 'perf stat' and collects metrics. 
# The metrics that's being collected is the 'Total Time' and 'Cycles'
# return the metrics as a tuple as integers. 
# def run_perf_stat(output_file): 
#     try: 
#         result = subprocess.run( 
#             ["perf", "stat", "-r", "5", f"./{output_file}"],
#             stderr=subprocess.PIPE,
#             stdout=subprocess.DEVNULL,  # ignore the output 
#             text=True
#         )
#         perf_output = result.stderr
#         print("Perf output captured")
        
#         # extract the metrics from the perf output, Total Time and and Cycles using regex 
#         cycles_match = re.search(r'([\d,]+)\s+cycles', perf_output)
#         time_match = re.search(r'([\d.]+)\s+seconds time elapsed', perf_output)
        
#         if cycles_match and time_match: 
#             cycles = int(cycles_match.group(1).replace(",", "")) # remove commas and convert to int 
#             total_time = float(time_match.group(1)) # covert to float 
#             return cycles, total_time
#         else: 
#             print("Failed to extract metrics from perf output Raw output:")
#             print(perf_output)
#             sys.exit(1)
        
#     except Exception as e: 
#         print(f"Failed to run with perf: {e}")
#         sys.exit(1)   

# use this function if your computer uses a hybrid CPU architecture (e.g. Intel Atom and Intel Core)
def run_perf_stat(output_file): 
    try: 
        result = subprocess.run( 
            ["perf", "stat", "-r", "5", f"./{output_file}"],
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,  # ignore standard output
            text=True
        )
        perf_output = result.stderr
        print("Perf output captured")
        print (f"perf_output: {perf_output}")

        # extract cycles for both CPU types
        atom_cycles_match = re.search(r'([\d,]+)\s+cpu_atom/cycles/', perf_output)
        core_cycles_match = re.search(r'([\d,]+)\s+cpu_core/cycles/', perf_output)

        # extract total time elapsed
        time_match = re.search(r'([\d.]+)\s+seconds time elapsed', perf_output)

        # convert extracted values
        atom_cycles = int(atom_cycles_match.group(1).replace(",", "")) if atom_cycles_match else 0
        core_cycles = int(core_cycles_match.group(1).replace(",", "")) if core_cycles_match else 0
        total_cycles = atom_cycles + core_cycles  # sum cycles from both CPU types

        if time_match: 
            total_time = float(time_match.group(1))  # convert to float
            return total_cycles, total_time
        else: 
            print("Failed to extract Total Time from perf output. Raw output:")
            print(perf_output)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running perf stat: {e}")
        sys.exit(1)

    
# read the IR file to extracts tokens as a rule string.     
def read_ir_file(ir_file): 
    try: 
        with open(ir_file, "r") as f: 
            ir_tokens = f.read().strip()
        return ir_tokens 
    except Exception as e: 
        print(f"Error reading IR file: {e}")
        sys.exit(1)

# I don't what to do with this yet (救我呀 快救救我)
# insert rules the IR rule with metrics into the rule database file at the specified line number. 
def insert_rule_into_database(rule_database_file, ir_tokens, metrics, insert_line):
    try: 
        with open(rule_database_file, "r") as f: 
            lines = f.readlines()
            
        # formate the new rule with metrics 
        formatted_rule = f'"{ir_tokens}"{metrics[0]}:{metrics[1]};'
        
        # insert the new rule at the specifiied line number 
        if insert_line - 1 < len(lines): 
            lines.insert(insert_line - 1, formatted_rule + " = ") 
        else: 
            lines.append(formatted_rule + "\n")
            
        # write back to the new database file 
        with open(rule_database_file, "w") as f: 
            f.writelines(lines)
            
        print(f"Inserted rule from IR file with metrics {metrics} at line {insert_line}.")
        
    except Exception as e: 
        print(f"Failed to update rule into database: {e}")
        sys.exit(1)
        


# the main function haha get it "main" function (not sorry) to handle the process 
def main(c_source_file, ir_file, rule_database_file, insert_line): 
    
    # compile the c source file 
    compile_c_source(c_source_file)
    
    # run the compiled file with perf stat to gather metrics 
    metrics = run_perf_stat("a.out")
    
    # read the IR file to extract tokens 
    ir_tokens = read_ir_file(ir_file)
    
    # insert the rule with the metrics into the rule database
    insert_rule_into_database(rule_database_file, ir_tokens, metrics, insert_line)
    
    print("Process completed")



if __name__ == "__main__": 
    if len(sys.argv) != 5: 
        print("Usage: python3 rbe_insert.py <c_source_file> <ir_file> <rule_database_file> <insert_line>")
        sys.exit(1)
        
    c_source_file = sys.argv[1] # c source file 
    ir_file = sys.argv[2]  # ir file that contains the tokens 
    rule_database_file = sys.argv[3]  # rule database file 
    insert_line = int(sys.argv[4])  # line number to insert the rule 
    
    main(c_source_file, ir_file, rule_database_file, insert_line)