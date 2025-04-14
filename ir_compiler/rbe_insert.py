import subprocess
import os 
import sys 
import re   
import main

# compiles the c source file using gcc and outputs it to a.out
def compile_c_source(c_source_file, output_file="a.out"): 
    try: 
        subprocess.run(["gcc", c_source_file, "-o", output_file], check=True)
        #print(f"Compiled {c_source_file} to {output_file}.")
    except: 
        #print(f"Error compiling {c_source_file}.")
        sys.exit(1) 

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
        #print("Perf output captured")
        #print (f"perf_output: {perf_output}")

        if output_file == "a.out": # CPU metrics 
            # extract cycles for both CPU types
            atom_cycles_match = re.search(r'([\d,]+)\s+cpu_atom/cycles/', perf_output)
            core_cycles_match = re.search(r'([\d,]+)\s+cpu_core/cycles/', perf_output)

            # extract total time elapsed
            time_match = re.search(r'([\d.]+)\s+seconds time elapsed', perf_output)

            # convert extracted values
            atom_cycles = int(atom_cycles_match.group(1).replace(",", "")) if atom_cycles_match else 0
            core_cycles = int(core_cycles_match.group(1).replace(",", "")) if core_cycles_match else 0
            total_cycles = atom_cycles + core_cycles  # sum cycles from both CPU types

            total_time = float(time_match.group(1)) if time_match else 0  # convert to float
            return total_cycles, total_time
        
        elif output_file == "b.out": # GPU metrics
            gpu_cycles_match = re.search(r'([\d,]+)\s+cpu_core/cycles/', perf_output)
            time_match = re.search(r'([\d.]+)\s+seconds time elapsed', perf_output)
            
            gpu_cycles = int(gpu_cycles_match.group(1).replace(",", "")) if gpu_cycles_match else 0
            total_time = float(time_match.group(1)) if time_match else 0
            return gpu_cycles, total_time
            
        # if time_match: 
        #     total_time = float(time_match.group(1))  # convert to float
        #     return total_cycles, total_time
        else: 
            #print("Failed to extract Total Time from perf output. Raw output:")
            #print(perf_output)
            sys.exit(1)
    
    except Exception as e:
        #print(f"Error running perf stat: {e}")
        sys.exit(1)

    
# read the IR file to extracts tokens as a rule string.     
def read_ir_file(ir_file): 
    try: 
        with open(ir_file, "r") as f: 
            ir_tokens = f.read().strip()
        return ir_tokens 
    except Exception as e: 
        #print(f"Error reading IR file:\n\n{e}")
        sys.exit(1)

# insert rules the IR rule with metrics into the rule database file at the specified line number. 
# def insert_rule_into_database(rule_database_file, ir_tokens, metrics, insert_line):
#     try: 
#         with open(rule_database_file, "r") as f: 
#             lines = f.readlines()
            
#         # formate the new rule with metrics
#         if len(metrics) > 0:
#             metric_string = ":".join([f"{x:.10f}" for x in metrics])
#             formatted_rule = f'"{ir_tokens}"~{metric_string}'
#         else: 
#             formatted_rule = f'"{ir_tokens}"'
        
#         # insert the new rule at the specified line number 
#         if insert_line - 1 < len(lines): 
#             lines.insert(insert_line - 1, formatted_rule + " = ") 
#         else: 
#             lines.append(formatted_rule + ";\n")
            
#         # write back to the new database file 
#         with open(rule_database_file, "w") as f: 
#             f.writelines(lines)
            
#         print(f"Inserted rule from IR file with metrics {metrics} at line {insert_line}.")
        
#     except Exception as e: 
#         print(f"Failed to update rule into database: {e}")
#         sys.exit(1)
        
def insert_rule_into_database(rule_database_file, ir_tokens, metrics, insert_line):
    try: 
        with open(rule_database_file, "r") as f: 
            lines = f.readlines()
            
        # format the new rule with GPU metrics
        if metrics:
            metric_string = f"0:{metrics['cpu_total_cycles']:.10f}:{metrics['cpu_total_time']:.10f}"
            formatted_rule = f'".*$0 {ir_tokens }"~{metric_string}'
        else:
            formatted_rule = f'"{ir_tokens }"'
        
        # insert the new rule at the specified line number 
        if insert_line - 1 < len(lines): 
            lines.insert(insert_line - 1, formatted_rule + " = \n") 
        else: 
            lines.append(formatted_rule + ";\n")
            
        # write back to the database file 
        with open(rule_database_file, "w") as f: 
            f.writelines(lines)
            
        #print(f"Inserted rule from IR file with metrics {metric_string} at line {insert_line}.")
        sys.stdout = sys.__stdout__
        print(metrics['cpu_total_cycles']/10000)
        sys.stdout = open(os.devnull, "w")
        
    except Exception as e: 
        #print(f"Failed to update rule into database: {e}")
        sys.exit(1)


# the main function haha get it "main" function (not sorry) to handle the process 
def main_(c_source_file, ir_tokens, rule_database_file, insert_line): 
    
    # compile the c source file 
    compile_c_source(c_source_file)
    
    # run the compiled file with perf stat to gather metrics 
    cpu_total_cycles, cpu_total_time = run_perf_stat("a.out")
    
    metrics = {
        "cpu_total_cycles": cpu_total_cycles,
        "cpu_total_time": cpu_total_time,
    }
    
    # insert the rule with the metrics into the rule database
    insert_rule_into_database(rule_database_file, ir_tokens, metrics, insert_line)
    #print("Process completed")



if __name__ == "__main__": 
    if len(sys.argv) != 5: 
        #print("Usage: python3 rbe_insert.py <c_source_file> <ir_file> <rule_database_file> <insert_line>")
        sys.exit(1)
        
    c_source_file = sys.argv[1] # c source file 
    ir_file = sys.argv[2]  # ir file that contains the tokens 
    rule_database_file = sys.argv[3]  # rule database file 
    insert_line = int(sys.argv[4])  # line number to insert the rule 
    
    main_(c_source_file, ir_file, rule_database_file, insert_line)
