# import subprocess
# import sys
# import os

import sys
import os
# This ensures that the local `types.py` file won't be picked up first
sys.path = [p for p in sys.path if p != os.getcwd()]

import subprocess


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
    
    # Here, we're assuming that main.py outputs IR tokens in the stdout.
    # We need to parse that output. For now, we'll assume it's a simple text output.
    # You can adjust the parsing logic based on the actual format from `main.py`.
    ir_tokens = result.stdout.splitlines()  # Adjust this based on the actual format
    
    print(f"Compiled {c_source} into IR tokens.")
    return ir_tokens


if __name__ == "__main__":
    test_c_source = "testcase1.c"  # Adjust this to your actual C file
    ir_tokens = compile(test_c_source)
    print("Generated IR tokens: ", ir_tokens)
