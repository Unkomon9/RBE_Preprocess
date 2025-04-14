
import sys

from debug import *
from tokens import *

import cli_parser
import lexer
import normalizer
import preprocessor
import simplifier
import converter
import operator_converter

import errors

class Compiler:

    def __init__(self):
        self.input_files = []
        self.output_file = ""
        self.include_dirs = []


    def parse_cli_args(self):
        dbg("Parsing CLI Args...")
        args = cli_parser.parse(sys.argv[1:])

        self.input_files = args.input_files
        self.output_file = args.output_file
        self.include_dirs = args.include

        dbg("ARGS:")
        dbg(args)


    def compile_all(self):
        """
        Compile all input files
        """
        for file in self.input_files:
            self.compile(file)
    

    def compile(self, file):
        dbg(f"Compiling {file}")

        dbg("++++++++++++++++++++++++++++++++++++++++++++++++++")
        dbg("Performing Lexing")
        toks:Tokens = lexer.lex(file)

        dbg("++++++++++++++++++++++++++++++++++++++++++++++++++")
        dbg("Performing Normalization")
        toks:Tokens = normalizer.normalize(toks)

        dbg("++++++++++++++++++++++++++++++++++++++++++++++++++")
        dbg("Performing Preprocessing")
        toks:Tokens = preprocessor.preprocess(toks, include_dirs=self.include_dirs)

        dbg("++++++++++++++++++++++++++++++++++++++++++++++++++")
        dbg("Performing Simplification")
        toks:Tokens = simplifier.simplify(toks)

        dbg("++++++++++++++++++++++++++++++++++++++++++++++++++")
        dbg("Performing Conversion")
        toks:Tokens = converter.convert(toks)

        dbg("++++++++++++++++++++++++++++++++++++++++++++++++++")
        dbg("Performing Operator Conversion")
        toks:Tokens = operator_converter.convert(toks)
        
        dbg("++++++++++++++++++++++++++++++++++++++++++++++++++")

        # check for errors
        errors.ERROR_HANDLER.finalize()
        return toks


    # TODO: create dictionary of variable:type
    def create_type_table(self):
        return {}



if __name__ == '__main__':
    compiler = Compiler()
    compiler.parse_cli_args()
    compiler.compile_all()

