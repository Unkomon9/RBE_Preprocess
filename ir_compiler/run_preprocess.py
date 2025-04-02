import subprocess

def run_script(input, args):
    if input == "0":
        script = "c_preprocess.py"  
        command = ["python3", script, "testcase1.c", args, "c.rbe", "1"]
        cwd = None 
        
    elif input == "1":
        script = "cuda_preprocess.py"
        command = ["python3", script, "cuda2.cu", "cuda.rbe", "1"]
        cwd = "cuda" 
        
    else:
        print("Invalid input. Please enter 0 or 1.")
        return

    try:
        subprocess.run(command, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}")

if __name__ == "__main__":
    user_input = input("Enter 0 to run c_preprocess.py or 1 to run cuda_preprocess.py: ").strip()
    args = '{"#1": "$1"}' 
    run_script(user_input, args)
