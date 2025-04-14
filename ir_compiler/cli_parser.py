
import argparse


"""
input_filenames
output_filename
include_dirs
"""

def parse(args):
    parser = argparse.ArgumentParser(
                prog="IR Compiler",
                description="Converts C code to IR"
            )

    # input filenames
    parser.add_argument(
            "input_files",
            type=str,
            help="C source files to be compiled",
            nargs="+"
            )

    # output filename
    parser.add_argument(
            "-o",
            "--output_file",
            type=str,
            help="File to save output to",
            default="a.out"
            )

    # include directories
    parser.add_argument(
            "-I",
            "--include",
            action="append",
            type=str,
            help="Directories to search for headers",
            default=[]
            )



    result = parser.parse_args(args)
    return result



