import subprocess
import os 
import sys 
import re   

# compiles the c source file using nvcc and outputs it to b.out 
def compile_cuda_source(cuda_source_file, output_file="cuda.out"):
    try: 
        subprocess.run(["nvcc", cuda_source_file, "-o", output_file], check=True) 
        print(f"Compiled {cuda_source_file} to {output_file}.")
    except: 
        print(f"Error compiling {cuda_source_file}.")
        sys.exit(1)

# use this function if your computer don't uses a hybrid CPU architecture 
# runs the compiled program with 'perf stat' and collects metrics. 
# the metrics that's being collected is the 'Total Time' and 'Cycles'
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
            stdout=subprocess.DEVNULL,  # Ignore standard output
            text=True
        )
        perf_output = result.stderr
        print("Perf output captured")
        print(f"perf_output: {perf_output}")

        # extract GPU cycles and time elapsed
        gpu_cycles_match = re.search(r'([\d,]+)\s+cpu_core/cycles/', perf_output)
        time_match = re.search(r'([\d.]+)\s+seconds time elapsed', perf_output)

        gpu_cycles = int(gpu_cycles_match.group(1).replace(",", "")) if gpu_cycles_match else 0
        total_time = float(time_match.group(1)) if time_match else 0

        return gpu_cycles, total_time

    except Exception as e:
        print(f"Error running perf stat: {e}")
        sys.exit(1)

    
# read the IR file to extracts tokens as a rule string.     
def read_ir_file(ir_file): 
    try: 
        with open(ir_file, "r") as f: 
            cuda_tokens  = f.read().strip()
        return cuda_tokens  
    except Exception as e: 
        print(f"Error reading IR file:\n\n{e}")
        sys.exit(1)

        
def insert_rule_into_database(rule_database_file, cuda_tokens , metrics, insert_line):
    try:
        with open(rule_database_file, "r") as f:
            lines = f.readlines()

        # format the new rule with GPU metrics
        if metrics:
            metric_string = f"1:{metrics['gpu_total_cycles']:.10f}:{metrics['gpu_total_time']:.10f}"
            formatted_rule = f'".*$0 {cuda_tokens }"~{metric_string}'
        else:
            formatted_rule = f'"{cuda_tokens }"'

        # insert the new rule at the specified line number
        if insert_line - 1 < len(lines):
            lines.insert(insert_line - 1, formatted_rule + " = \n")
        else:
            lines.append(formatted_rule + ";\n")

        # write back to the database file
        with open(rule_database_file, "w") as f:
            f.writelines(lines)

        print(f"Inserted rule from IR file with metrics {metric_string} at line {insert_line}.")

    except Exception as e:
        print(f"Failed to update rule into database: {e}")
        sys.exit(1)



# the main function haha get it "main" function (not sorry) to handle the process 
def main_(cuda_source_file, cuda_tokens , rule_database_file, insert_line):
    # compile the CUDA source file
    compile_cuda_source(cuda_source_file)

    # run the compiled CUDA file with perf stat to gather GPU metrics
    gpu_total_cycles, gpu_total_time = run_perf_stat("cuda.out")

    metrics = {
        "gpu_total_cycles": gpu_total_cycles,
        "gpu_total_time": gpu_total_time
    }

    # insert the rule with GPU metrics into the rule database
    insert_rule_into_database(rule_database_file, cuda_tokens , metrics, insert_line)
    print("Process completed")


if __name__ == "__main__": 
    if len(sys.argv) != 5: 
        print("Usage: python3 rbe_insert.py <cuda_source_file> <ir_file> <rule_database_file> <insert_line>")
        sys.exit(1)
        
    cuda_source_file = sys.argv[1] # c source file 
    ir_file = sys.argv[2]  # ir file that contains the tokens 
    rule_database_file = sys.argv[3]  # rule database file 
    insert_line = int(sys.argv[4])  # line number to insert the rule 
    
    main_(cuda_source_file, ir_file, rule_database_file, insert_line)