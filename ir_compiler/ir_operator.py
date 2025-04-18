
from debug import *
from token import *

from ir_types import *
import standard


class Operator:
    def __init__(self, tokens:list[Token], varnum:int, variable_names):
        self.tokens = tokens
        self.varnum = varnum
        self.variable_names = variable_names

        # combine multi-token operations
        self.tokens = self.combine_multi_token_operations(self.tokens)

        # break operations
        self.tokens = self.break_operations(self.tokens)

        # convert assignment operators
        # x += 3
        # =>
        # x = x + (3)
        self.tokens = self.convert_assignment_operators(self.tokens)

        # convert type casts to use "cast"
        self.tokens = self.convert_casts(self.tokens)


        # convert unary operators
        self.tokens = self.convert_unary_operators(self.tokens)

        # convert calls and accesses to use "call" and "access"
        self.tokens = self.convert_calls_and_accesses(self.tokens)

        # Remove $TYPE, $STRUCT, $UNION, $ENUM, and $INFER variables
        self.token_types = ["NA"] * self.varnum
        self.tokens = self.remove_types(self.tokens)

        # break up lines that have more than one operation on them
        self.tokens = self.break_multiple_operations(self.tokens)

        # remove any remaining inferences
        self.tokens = self.remove_remaining_inferences(self.tokens)

        # convert unary + and -
        self.tokens = self.convert_unary_plus_and_minus(self.tokens)

        # parse structures, unions, enums, and typedefs into objects
        self.functions = []
        self.structures = []
        self.unions = []
        self.enums = []
        self.typedefs = []
        self.tokens = self.parse_structs_unions_enums_and_typedefs(self.tokens)

        # remove un+ and un-
        self.tokens = self.remove_unary_operators(self.tokens)

        # convert returns
        self.convert_returns()

        # remove ->
        self.remove_arrows()

        # remove <=, >=, and !=
        self.remove_or_equal()

        # make sure all if statements have an else clause
        self.create_else_clauses()

        # remove || 
        self.remove_logical_or()

        # remove &&
        self.remove_logical_and()

        # remove lognot
        self.remove_logical_not()

        # convert derefs to accesses
        self.convert_derefs_to_accesses()

        # remove remaining parenthesis
        self.remove_remaining_parenthesis()

        # remove any remaining inferences
        self.tokens = self.remove_remaining_inferences(self.tokens)
        """
        remaining tokens:
        $INFER, $TYPE, $ENUM, $STRUCTURE_DEFINITION, $UNION_DEFINITION, $TYPEDEF_DEFINITION
        bitnot, ref, %, ^, &, |, -, +, <, >, *, /, ==, ., call, access, >>, <<, =, ,, cast
        {, }, ;
        if, else
        goto, @x, #x, :
        <char, int, float, and string literals>
        """

        
    def combine_multi_token_operations(self, tokens:list[Token]) -> list[Token]:

        first_tokens = set(["+", "/", "*", "!", "=", "%", "^", "~", "-"])
        second_tokens = set(["<", ">", "&", "|"])

        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i].token in first_tokens:
                if i + 1 < n and tokens[i+1] == "=":
                    tokens[i].token += tokens[i+1].token
                    del tokens[i+1]
                    n -= 1
                    i += 1
                    continue
                if tokens[i] == "-":
                    if i + 1 < n and tokens[i+1] == ">":
                        tokens[i].token += tokens[i+1].token
                        del tokens[i+1]
                        n -= 1
                        i += 1
                        continue
            elif tokens[i].token in second_tokens:
                if i + 1 < n:
                    if tokens[i+1] == "=":
                        tokens[i].token += tokens[i+1].token
                        del tokens[i+1]
                        n -= 1
                        i += 1
                        continue
                    if tokens[i+1].token == tokens[i].token:
                        if i + 2 < n and tokens[i+2] == "=":
                            tokens[i].token += tokens[i+1].token + tokens[i+2].token
                            del tokens[i+1]
                            del tokens[i+1]
                            n -= 2
                            i += 1
                            continue
                        else:
                            tokens[i].token += tokens[i+1].token
                            del tokens[i+1]
                            n -= 1
                            i += 1
                            continue
            i += 1


        return tokens


    def break_operations(self, tokens:list[Token]):
        dbg("Breaking operations from if statements")

        tokens = self.break_operations_from_ifs(tokens)

        tokens = self.break_operations_from_returns(tokens)

        tokens = self.convert_prefix_and_postfix(tokens)

        tokens = self.break_operations_from_function_calls(tokens)
        
        return tokens


    def break_operations_from_ifs(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i] == "if":
                between = []
                parens = []
                starting_index = i
                while i < n:
                    if tokens[i] == "(":
                        break
                    i += 1
                while i < n:
                    if tokens[i] == "(":
                        parens.append("(")
                        i += 1
                        continue
                    elif tokens[i] == ")":
                        if len(parens) == 0:
                            fatal_error(tokens[i], "Mismatched )...")
                        parens.pop()
                        if len(parens) == 0:
                            break
                    between.append(tokens[i])
                    del tokens[i]
                    n -= 1
                tokens.insert(i, Token("#" + str(self.varnum), tokens[i].line_number, tokens[i].filename))
                i += 1
                n += 1
                tokens.insert(starting_index, Token("$INFER", tokens[i].line_number, tokens[i].filename))
                starting_index += 1
                i += 1
                n += 1
                tokens.insert(starting_index, Token("#" + str(self.varnum), tokens[starting_index].line_number, tokens[starting_index].filename))



                starting_index += 1
                i += 1
                n += 1
                tokens.insert(starting_index, Token("=", tokens[starting_index].line_number, tokens[starting_index].filename))
                starting_index += 1
                i += 1
                n += 1

                for x in between:
                    tokens.insert(starting_index, x)
                    starting_index += 1
                    i += 1
                    n += 1
                tokens.insert(starting_index, Token(";", tokens[starting_index].line_number, tokens[starting_index].filename))
                starting_index += 1
                i += 1
                n += 1

                self.varnum += 1
                
            i += 1

        return tokens


    def break_operations_from_returns(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i] == "return":
                starting_index = i;
                after = []
                i += 1
                while i < n:
                    if tokens[i] == ";":
                        break
                    after.append(tokens[i])
                    del tokens[i]
                    n -= 1
                tokens.insert(i, Token("#" + str(self.varnum), tokens[i].line_number, tokens[i].filename))
                i += 1
                n += 1
                tokens.insert(starting_index, Token("$INFER", tokens[starting_index].line_number, tokens[starting_index].filename))
                i += 1
                n += 1
                starting_index += 1

                tokens.insert(starting_index, Token("#" + str(self.varnum), tokens[starting_index].line_number, tokens[starting_index].filename))
                i += 1
                n += 1
                starting_index += 1

                tokens.insert(starting_index, Token("=", tokens[starting_index].line_number, tokens[starting_index].filename))
                i += 1
                n += 1
                starting_index += 1

                for x in after:
                    tokens.insert(starting_index, x)
                    i += 1
                    n += 1
                    starting_index += 1
                tokens.insert(starting_index, Token(";", tokens[starting_index].line_number, tokens[starting_index].filename))
                i += 1
                n += 1
                starting_index += 1

                self.varnum += 1

            i += 1

        return tokens

    
    def convert_prefix_and_postfix(self, tokens:list[Token]) -> list[Token]:
        dbg("Converting prefix and postfix operators...")
        i = 0
        n = len(tokens)

        operators = set(["~", "!", "%", "^", "&", "|", "-", "+", "<", ">", "/", "*", "+=", "/=", "*=", "<=", ">=", "!=", "==", "%=", "^=", "&=", "|=", "~=", "-=", "->", "&&", "||", "&&=", "||=", ".", "(", "[", ">>", "<<", "<<=", ">>=", "=", ";", "++", "--"])
        
        while i < n:
            if tokens[i].token in ["++", "--"]:
                if tokens[i] == "++":
                    new_operator = "+="
                else:
                    new_operator = "-="
                # figure out if this is prefix or postfix
                is_prefix = 0
                if i > 0 and (tokens[i-1].token in ["}", "{", ";", "("] or tokens[i-1].token in operators):
                    is_prefix = 1

                inside = []

                del tokens[i]
                n -= 1

                if is_prefix:
                    parens = []
                    j = i
                    # higher:
                    # function call ()
                    # array subscript []
                    # .
                    # ->
                    # TODO: finish this
                    while j < n:
                        if tokens[j].token in ["(", "["]:
                            parens.append(tokens[j].token)
                        elif tokens[j] == ")":
                            if len(parens) == 0:
                                fatal_error(tokens[j], "Mismatched )...")

                            if len(parens) == 0:
                                break
                        elif tokens[j] == "]":
                            if len(parens) == 0:
                                fatal_error(tokens[j], "Mismatched ]...")

                            if len(parens) == 0:
                                break
                        elif tokens[j].token in ["(", "[", ".", "->"]:
                            inside.append(tokens[j])
                            j += 1
                            continue

                        inside.append(tokens[j])
                        if len(parens) == 0:
                            if not (j+1 < n and tokens[j+1].token in ["(", "[", ".", "->"]):
                                break

                        j += 1
                    # move to the line before
                    j = i
                    while j >= 0:
                        if tokens[j].token in ["{", ";", "}"]:
                            break
                        j -= 1
                    j += 1


                    for x in inside:
                        tokens.insert(j, x)
                        j += 1; n += 1
                    tokens.insert(j, Token(new_operator, tokens[j].line_number, tokens[j].filename))
                    j += 1; n += 1
                    tokens.insert(j, Token("1", tokens[j].line_number, tokens[j].filename))
                    j += 1; n += 1
                    tokens.insert(j, Token(";", tokens[j].line_number, tokens[j].filename))
                    j += 1; n += 1

                else:
                    j = i - 1
                    parens = []
                    while j >= 0:
                        if tokens[j] == ")":
                            parens.append(")")
                        elif tokens[j] == "(":
                            if len(parens) == 0:
                                fatal_error(tokens[j], "Mismatched (...")
                            parens.pop()
                            if len(parens) == 0:
                                break
                        inside.append(tokens[j])

                        if len(parens) == 0:
                            break

                        j -= 1

                    # move to the line after
                    j = i
                    while j < n:
                        if tokens[j] == ";":
                            j += 1
                            break
                        j += 1

                    for x in inside:
                        tokens.insert(j, x)
                        j += 1; n += 1
                    tokens.insert(j, Token(new_operator, tokens[j].line_number, tokens[j].filename))
                    j += 1; n += 1
                    tokens.insert(j, Token("1", tokens[j].line_number, tokens[j].filename))
                    j += 1; n += 1
                    tokens.insert(j, Token(";", tokens[j].line_number, tokens[j].filename))
                    j += 1; n += 1
                        

            

            i += 1

        dbg("Finished converting prefix and postfix operators...")
        return tokens

    def break_operations_from_function_calls(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)
        changes = 1
        while changes:
            changes = 0
            while i < n:
                if len(tokens[i].token) > 0 and tokens[i].token[0] == '#':
                    # this is a variable
                    starting_index = i
                    if i + 1 < n and tokens[i+1] == "(":
                        # this is a function call or definition
                        # make sure the thing before the var is not $TYPE or $STRUCT x, $ENUM x, $UNION x
                        if not (i > 0 and tokens[i-1] == "$TYPE" or i > 1 and tokens[i-2] in ["$STRUCT", "$ENUM", "$UNION", "struct", "union", "enum"]):
                            # this is a function call
                            while starting_index >= 0:
                                if tokens[starting_index].token in ["{", ";", "}"]:
                                    starting_index += 1
                                    break
                                starting_index -= 1
                            i += 1
                            braces = []
                            current = []
                            while i < n:
                                if tokens[i].token in ["(", "{"]:
                                    braces.append(tokens[i].token)
                                    if len(braces) == 1:
                                        i += 1
                                        continue
                                elif tokens[i] == "}":
                                    if len(braces) == 0:
                                        fatal_error(tokens[i], "Mismatched }...")
                                    braces.pop()
                                elif tokens[i] == ")":
                                    if len(braces) == 0:
                                        fatal_error(tokens[i], "Mismatched )...")
                                    braces.pop()
                                    if len(braces) == 0:
                                        # handle what was left
                                        if len(current) > 0:
                                            if len(current) == 1 and len(current[0].token) > 0 and current[0].token[0] == "#":
                                                # this should just be put back
                                                tokens.insert(i, current[0])
                                                current = []
                                                i += 2
                                                n += 1
                                                break

                                            changes += 1

                                            tokens.insert(i, Token("#" + str(self.varnum), tokens[i].line_number, tokens[i].filename))
                                            i += 2
                                            n += 1
                                            tokens.insert(starting_index, Token("$INFER", tokens[starting_index].line_number, tokens[starting_index].filename))
                                            starting_index += 1
                                            i += 1
                                            n += 1

                                            tokens.insert(starting_index, Token("#" + str(self.varnum), tokens[starting_index].line_number, tokens[starting_index].filename))
                                            starting_index += 1
                                            i += 1
                                            n += 1
                                            tokens.insert(starting_index, Token("=", tokens[starting_index].line_number, tokens[starting_index].filename))
                                            starting_index += 1
                                            i += 1
                                            n += 1

                                            for x in current:
                                                tokens.insert(starting_index, x)
                                                starting_index += 1
                                                i += 1
                                                n += 1
                                            tokens.insert(starting_index, Token(";", tokens[starting_index].line_number, tokens[starting_index].filename))
                                            starting_index += 1
                                            i += 1
                                            n += 1
                                            current = []

                                            self.varnum += 1

                                        break
                                elif tokens[i] == ",":
                                    if len(current) == 1 and len(current[0].token) > 0 and current[0].token[0] == "#":
                                        # this should just be put back
                                        tokens.insert(i, current[0])
                                        i += 2
                                        n += 1
                                        current = []
                                        continue

                                    changes += 1

                                    tokens.insert(i, Token("#" + str(self.varnum), tokens[i].line_number, tokens[i].filename))
                                    i += 2
                                    n += 1
                                    self.varnum += 1

                                    tokens.insert(starting_index, Token("#" + str(self.varnum), tokens[starting_index].line_number, tokens[starting_index].filename))
                                    starting_index += 1
                                    i += 1
                                    n += 1
                                    tokens.insert(starting_index, Token("=", tokens[starting_index].line_number, tokens[starting_index].filename))
                                    starting_index += 1
                                    i += 1
                                    n += 1

                                    for x in current:
                                        tokens.insert(starting_index, x)
                                        starting_index += 1
                                        i += 1
                                        n += 1
                                    tokens.insert(starting_index, Token(";", tokens[starting_index].line_number, tokens[starting_index].filename))
                                    starting_index += 1
                                    i += 1
                                    n += 1
                                    current = []
                                    continue
                                    
                                current.append(tokens[i])
                                del tokens[i] 
                                n -= 1


                i += 1;

        return tokens

    
    def convert_assignment_operators(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)

        assignment_operators = set(["+=", "/=", "*=", "%=", "^=", "&=", "|=", "~=", "-=", "&&=", "||=", "<<=", ">>="])

        while i < n:
            if tokens[i].token in assignment_operators:
                the_operator = tokens[i].token.strip("=")
                tokens[i].token = "="

                before = []
                j = i-1
                while j >= 0:
                    if tokens[j].token in [";", "{", "}"]:
                        break
                    before.append(tokens[j])
                    j -= 1
                j += 1

                i += 1
                for x in before:
                    tokens.insert(i, x)
                    i += 1
                    n += 1
                tokens.insert(i, Token(the_operator, tokens[i].line_number, tokens[i].filename))
                i += 1
                n += 1
                tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                i += 1
                n += 1

                j = i
                while j < n:
                    if tokens[j] == ";":
                        j += 1
                        break
                    j += 1
                j -= 1
                tokens.insert(j, Token(")", tokens[j].line_number, tokens[j].filename))
                n += 1
            
            i += 1


        return tokens

    def convert_unary_operators(self, tokens:list[Token]) -> list[Token]:
        print(f"CONVERTING UNARY OPERATORS: {tokens}")
        unary_operators = {"~":"bitnot", "!":"lognot", "&":"ref", "*":"deref", "-":"un-", "+":"un+"}

        operators = set(["~", "!", "%", "^", "&", "|", "-", "+", "/", "<", ">", "*", "==", "->", "&&", "||", ".", "(", "[", ">>", "<<", "=", ";", "{", "}", "<=", ">=", "!=", "cast"])

        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i].token in unary_operators:
                if i == 0 or (i > 0 and tokens[i-1].token in operators):
                    # this is a unary operator
                    tokens.insert(i, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens[i].token = unary_operators[tokens[i].token]
            
            i += 1

        return tokens


    def convert_calls_and_accesses(self, tokens:list[Token]) -> list[Token]:
        operators = set(["bitnot", "lognot", "deref", "ref", "un-", "un+", "%", "^", "&", "|", "-", "/", "+", "<", ">", "*", "==", "->", "&&", "||", ".", "(", "[", ">>", "<<", "=", "!=", "<=", ">="])
        # x[y] => x access (y)
        # x(y) => x call (y)
        # x() => x call(#NOTHING)
        i = 0
        n = len(tokens)
        while i < n:
            if len(tokens[i].token) > 0 and tokens[i].token[0] == '#':
                # this is a variable
                starting_index = i
                if i + 1 < n and tokens[i+1] == "(":
                    # this is a function call or definition
                    # make sure the thing before the var is not $TYPE or $STRUCT x, $ENUM x, $UNION x
                    if not (i > 0 and tokens[i-1] == "$TYPE" or i > 1 and tokens[i-2] in ["$STRUCT", "$ENUM", "$UNION"]):
                        # this is a function call
                        i += 1
                        tokens.insert(i, Token("call", tokens[i].line_number, tokens[i].filename))
                        i += 1
                        n += 1
                        i += 1
                        if i < n and tokens[i] == ")":
                            tokens.insert(i, Token("#NOTHING", tokens[i].line_number, tokens[i].filename))
                            i += 1
                            n += 1
            i += 1
        

        return tokens


    def convert_casts(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i] == "$TYPE":
                if i > 0 and i + 1 < n and tokens[i-1] == "(" and tokens[i+1] == ")":
                    if i + 2 < n and tokens[i+2].token in ["{", ";"]:
                        i += 1
                        continue
                    del tokens[i-1]
                    del tokens[i]
                    tokens.insert(i, Token("cast", tokens[i].line_number, tokens[i].filename))
                    n -= 1

            i += 1

        return tokens


    def convert_unary_plus_and_minus(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i] == "un-":
                tokens[i].token = "-"
            elif tokens[i] == "un+":
                tokens[i].token = "+"
            i += 1
        

        return tokens


    def remove_types(self, tokens:list[Token], structures=[], unions=[]) -> list[Token]:
        i = 0
        n = len(tokens)

        print("Removing TYPES:")
        print(tokens)

        while i < n:
            if tokens[i] == "$TYPE":
                if i + 1 < n and len(tokens[i+1].token) > 0 and tokens[i+1].token[0] == "#":
                    varnum = tokens[i+1].token[1:]
                    try:
                        varnum = int(varnum)
                    except:
                        i += 1
                        continue
                    if varnum >= len(self.token_types):
                        fatal_error(tokens[i+1], "There is a serious problem with the compiler. Report this...")

                    new_type = self.parse_type_string(tokens[i].types, structures, unions)
                    print(f"type val: {tokens[i].types} {new_type}")

                    self.token_types[varnum] = new_type
                    del tokens[i]
                    n -= 1
                    continue
            elif tokens[i] == "$STRUCT":
                structures.append(tokens[i])
            elif tokens[i] == "$UNION":
                unions.append(tokens[i])
            elif tokens[i] == "$INFER":
                pass

            i += 1

        print(f"Token types: {self.token_types}")

        self.type_structures = structures
        self.type_unions = unions

        return tokens


    def remove_struct_types(self, tokens:list[Token], structures=[], unions=[]) -> list[Token]:
        i = 0
        n = len(tokens)

        print("Removing TYPES FROM STRUCT:")
        print(tokens)

        result = []

        while i < n:
            if tokens[i] == "$TYPE":
                print("found a type")
                if i + 1 < n and len(tokens[i+1].token) > 0:
                    new_type = self.parse_type_string(tokens[i].types, structures, unions)
                    print(f"type val: {tokens[i].types} {new_type}")

                    result.append(new_type)
                    del tokens[i]
                    n -= 1
                    continue
            elif tokens[i] == "$STRUCT":
                structures.append(tokens[i])
            elif tokens[i] == "$UNION":
                unions.append(tokens[i])
            elif tokens[i] == "$INFER":
                pass

            i += 1

        print(f"FINISHED REMOVING TYPES FROM STRUCT")

        return result

    
    def parse_type_string(self, type_tokens, structures, unions):
        print(f"Parsing... {type_tokens}")

        pointers = ""
        sign = ""
        size = ""

        i = 0
        n = len(type_tokens)

        result = ""

        while i < n:
            match(type_tokens[i]):
                case "int":
                    size = "32"
                    sign = "i"
                case "long":
                    size = "64"
                    sign = "i"
                case "short":
                    size = "16"
                    sign = "i"
                case "float":
                    sign = "f"
                case "double":
                    sign = "f"
                case "unsigned":
                    sign = "u"
                case "signed":
                    sign = "i"
                case "char":
                    sign = "u"
                    size = "8"
                case "void":
                    sign = "void"
                    size = ""
                case "*":
                    pointers += "*"
                case "struct": # TODO: convert to structure
                    print("found struct")
                    struct_types = ""
                    if i + 1 < n:
                        struct_name = type_tokens[i+1].token
                        for struct in structures:
                            print(struct_name, struct.name)
                            if struct.name == struct_name:
                                print(struct.types)
                                print("Found THE struct")
                                struct_types = struct.types[1:-1]
                    result = "s{" + f"{','.join(self.remove_struct_types(struct_types, structures, unions))}" + "}"
                    i += 1
                case "union": # TODO: convert to union type
                    print("found union")
                    union_types = ""
                    if i + 1 < n:
                        union_name = type_tokens[i+1].token
                        for union in unions:
                            print(union_name, union.name)
                            if union.name == union_name:
                                print(union.types)
                                print("Found THE union")
                                union_types = union.types[1:-1]
                    result = "u{" + f"{','.join(self.remove_struct_types(union_types, structures, unions))}" + "}"
                    i += 1
            i += 1

        return f"{pointers}{result}{sign}{size}"

    
    def remove_remaining_inferences(self, tokens:list[Token]) -> list[Token]:

        print("Removing remaining inferences...")

        i = 0
        n = len(tokens)

        while i < n:
            if tokens[i] == "$INFER":
                if i + 1 < n:
                    the_var = tokens[i+1].token
                    print(f"FOUND INFERENCE {the_var}")
                    if len(the_var) < 2:
                        i += 1
                        continue

                    the_varnum = the_var[1:]
                    try:
                        the_varnum = int(the_varnum)
                    except:
                        i += 1
                        continue

                    if len(self.token_types) > the_varnum:
                        if self.token_types[the_varnum] != "N/A":
                            del tokens[i]
                            n -= 1
                            continue

                    while len(self.token_types) <= the_varnum:
                        the_varnum.append("NA")

                    inferred_type = "NA"
                    if i + 2 < n:
                        next_token = tokens[i+2]
                        if next_token != "=":
                            inferred_type = "NA"
                        else:
                            operator = None
                            first = None
                            second = None
                            if i + 3 < n:
                                first = tokens[i+3]
                            if i + 4 < n:
                                operator = tokens[i+4]
                                if operator.token in [";", "}", "{"]:
                                    operator = None
                            if i + 5 < n:
                                second = tokens[i+5]

                            if operator is not None:
                                inferred_type = self.infer_type(first, operator, second)
                                print("INFERRING TYPE")
                            elif first is not None:
                                inferred_type = self.infer_type(first)

                    self.token_types[the_varnum] = inferred_type

                    del tokens[i]
                    i -= 1
                    n -= 1

            i += 1


        print("Finished removing remaining inferences!")
        print(tokens)

        return tokens

    
    def get_literal_type(self, token):
        if len(token.token) > 0 and token.token[0] == "#":
            the_varnum = token.token[1:]
            try:
                the_varnum = int(the_varnum)
            except:
                return "NA"

            while len(self.token_types) <= the_varnum:
                the_varnum.append("NA")

            return self.token_types[the_varnum]

        # we know it is a literal
        if len(token.token) > 0 and token.token[0] == '"':
            return "*u8"

        if len(token.token) > 0 and token.token[0] == "'":
            return "u8"

        try:
            value = float(token.token)
        except:
            return "NA"

        if "." in token.token:
            # this is a float
            return "f64"

        # this is an int
        sign = "i"
        # if value > 0:
        #     sign = "u"

        if sign == "u":
            # if value < 256:
            #     size = "8"
            # elif value < 65536:
            #     size = "16"
            if value < 4294967296:
                size = "32"
            else:
                size = "64"
        else:
            # if -129 < value < 128:
            #     size = "8"
            # elif -32769 < value < 32768:
            #     size = "16"
            if -2147483649 < value < 2147483648:
                size = "32"
            else:
                size = "64"

        return f"{sign}{size}"


    def infer_type(self, first, operator=None, second=None):
        first_literal_type = self.get_literal_type(first)

        if operator is None or second is None:
            # use the type of the first
            return first_literal_type

        second_literal_type = self.get_literal_type(second)

        first_sign = None
        first_size = None
        second_sign = None
        second_size = None
        first_is_pointer = False
        second_is_pointer = False
        if first_literal_type is not None:
            if len(first_literal_type) > 0 and first_literal_type != "NA":
                first_sign = first_literal_type[0]
                if first_sign in ["u", "f", "i"]:
                    try:
                        first_size = int(first_literal_type[1:])
                    except:
                        first_sign = None
                        first_size = None
                else:
                    first__sign = None
                    if first_literal_type[0] == "*":
                        first_is_pointer = True
        if second_literal_type is not None:
            if len(second_literal_type) > 0 and second_literal_type != "NA":
                second_sign = second_literal_type[0]
                if second_sign in ["u", "f", "i"]:
                    try:
                        second_size = int(second_literal_type[1:])
                    except:
                        second_sign = None
                        second_size = None
                else:
                    second_sign = None
                    if second_literal_type[0] == "*":
                        second_is_pointer = True


        match(operator):
            case "bitnot":
                if second_sign not in ["i", "u"] or second_is_pointer:
                    fatal_error(operator, "Can only perform bitwise not on integer types.")
                return second_literal_type
            case "lognot":
                if second_sign is None or second_is_pointer:
                    fatal_error(operator, "Can only perform logical not on scalar types.")
                return "u8"
            case "deref":
                if not second_is_pointer:
                    fatal_error(operator, "Can only dereference pointers.")
                return second_literal_type[1:]
            case "ref":
                if second_literal_type is None:
                    return "NA"
                return f"*{second_literal_type}"
            case "%":
                if first_sign not in ["i", "u"] or first_is_pointer or second_sign not in ["i", "u"] or second_is_pointer:
                    fatal_error(operator, "Can only perform % between two integers.")

                if first_literal_type == second_literal_type:
                    return first_literal_type

                result = first_literal_type
                if first_size != second_size:
                    if int(second_size) > int(first_size):
                        result = second_literal_type

                return result
            case "^":
                if first_sign not in ["i", "u"] or first_is_pointer or second_sign not in ["i", "u"] or second_is_pointer:
                    fatal_error(operator, "Can only perform ^ between two integers.")

                if first_literal_type == second_literal_type:
                    return first_literal_type

                result = first_literal_type
                if first_size != second_size:
                    if int(second_size) > int(first_size):
                        result = second_literal_type

                return result
            case "&":
                if first_sign not in ["i", "u"] or first_is_pointer or second_sign not in ["i", "u"] or second_is_pointer:
                    fatal_error(operator, "Can only perform & between two integers.")

                if first_literal_type == second_literal_type:
                    return first_literal_type

                result = first_literal_type
                if first_size != second_size:
                    if int(second_size) > int(first_size):
                        result = second_literal_type

                return result
            case "|":
                if first_sign not in ["i", "u"] or first_is_pointer or second_sign not in ["i", "u"] or second_is_pointer:
                    fatal_error(operator, "Can only perform | between two integers.")

                if first_literal_type == second_literal_type:
                    return first_literal_type

                result = first_literal_type
                if first_size != second_size:
                    if int(second_size) > int(first_size):
                        result = second_literal_type

                return result
            case "-": # TODO
                pass
            case "+":
                if first_is_pointer:
                    if second_is_pointer:
                        fatal_error(operator, "Cannot add two pointers together.")
                    return first_literal_type
                if second_is_pointer: 
                    if first_is_pointer:
                        fatal_error(operator, "Cannot add two pointers together.")
                    return second_literal_type
                
                if first_sign == "f":
                    if int(first_size) > int(second_size):
                        return first_literal_type
                    return f"{first_sign}{second_size}"
                if second_size == "f":
                    if int(second_size) > int(first_size):
                        return second_literal_type
                    return f"{second_sign}{first_size}"

                if int(second_size) > int(first_size):
                    return f"i{second_size}"
                return f"i{first_size}"
            case "<":
                return f"i32"
            case ">":
                return f"i32"
            case "*":
                if first_is_pointer or second_is_pointer:
                    fatal_error(operator, "Cannot multiply by a pointer.")
                    
                if first_sign == "f":
                    if int(first_size) > int(second_size):
                        return first_literal_type
                    return f"{first_sign}{second_size}"
                if second_size == "f":
                    if int(second_size) > int(first_size):
                        return second_literal_type
                    return f"{second_sign}{first_size}"

                if int(second_size) > int(first_size):
                    return f"i{second_size}"
                return f"i{first_size}"
            case "==":
                return f"i32"
            case "->": # TODO
                pass
            case "&&":
                return f"i32"
            case "||":
                return f"i32"
            case ".":
                pass
            case "access":
                if not first_is_pointer:
                    fatal_error(operator, "Can only access pointers.")
                return first_literal_type[1:]
            case ">>": # TODO
                pass
            case "<<": # TODO
                pass
            case ",":
                return f"{first_literal_type},{second_literal_type}"
            case "!=":
                return f"i32"
            case "<=":
                return f"i32"
            case ">=":
                return f"i32"
            case "un+":
                return second_literal_type
            case "un-":
                return second_literal_type


        return "NA"


    def break_multiple_operations(self, tokens:list[Token]) -> list[Token]:
        dbg("Breaking lines that have multiple operations...")
        operators = set(["bitnot", "lognot", "deref", "ref", "cast", "%", "^", "&", "|", "-", "+", "/", "<", ">", "*", "==", "->", "&&", "||", ".", "call", "access", ">>", "<<", "=", "&&", "||", ",", "!=", "<=", ">=", "un+", "un-"])
        
        i = 0
        n = len(tokens)
        this_line = 0
        line_start = 0
        equals = 0
        while i < n:
            if tokens[i].token in [";", "{", "}"]:
                if this_line > 1 or equals > 1:
                    print(f"breaking ({this_line} ops): {tokens[line_start:i]}")
                    tokens = self.break_line(tokens, line_start, i)
                    i += len(tokens) - n
                    n = len(tokens)
                this_line = 0
                equals = 0
                line_start = i + 1
            elif tokens[i].token in operators:
                if tokens[i].token == "=":
                    equals += 1
                else:
                    this_line += 1
            
            i += 1
        
        dbg("Finished breaking lines that have multiple operations!")

        return tokens


    def break_line(self, tokens:list[Token], line_start:int, line_end:int) -> int:
        # break the given tokens using infix to postfix and convert them to include only 1 operation per line (not including =)

        precedences = {
                "call":1, 
                "access":2, 
                ".":3, 
                "->":4, 
                "un+":5,
                "un-":6,
                "lognot":7,
                "bitnot":8,
                "cast":9,
                "deref":10,
                "ref":11,
                "*":12, 
                "/":13, 
                "%":14, 
                "+":15, 
                "-":16, 
                "<<":17, 
                ">>":18, 
                "<":19, 
                "<=":20, 
                ">":21, 
                ">=":22,
                "==":23, 
                "!=":24, 
                "&":25, 
                "^":26, 
                "|":27, 
                "&&":28, 
                "||":29, 
                "=":30,
                ",":31, 
                }

        associativity = {
                "un++":1,
                "un--":1,
                "lognot":1,
                "bitnot":1,
                "cast":1,
                "deref":1,
                "ref":1,
                }

        the_line = tokens[line_start:line_end]
        prefix = []
        # convert from infix to postfix
        if len(the_line) > 0 and the_line[0].token == "$TYPE":
            prefix.append(the_line[0])
            del the_line[0]

        postfix = []
        op_stack = []
        for x in the_line:
            # if curr token is operand, put it in the postfix
            if x.token not in precedences and x.token not in ["(", ")"]:
                postfix.append(x)

            # if a (, push it to the stack
            elif x == "(":
                op_stack.append(x)
            # if a ), pop from the stack until (
            elif x == ")":
                while True:
                    if len(op_stack) == 0:
                        fatal_error(x, "Mismatched (...")
                    curr = op_stack.pop()
                    if curr == "(":
                        break
                    postfix.append(curr)
            else:
                if x.token not in precedences:
                    fatal_error(x, "Unrecognized operator...")
                if len(op_stack) == 0 or op_stack[-1] == "(" or precedences[x.token] < precedences[op_stack[-1].token]:
                    op_stack.append(x)
                else:
                    while len(op_stack) > 0 and op_stack[-1].token != "(":
                        if x.token in associativity and op_stack[-1].token in associativity:
                            break
                        if precedences[x.token] <= precedences[op_stack[-1].token]:
                            break
                        postfix.append(op_stack.pop())
                    op_stack.append(x)

        while len(op_stack) > 0:
            postfix.append(op_stack.pop())

        print(f"POSTFIX: {postfix}")

        # break the postfix expression into multiple lines
        result = []
        val_stack = []
        for x in postfix:
            # if a variable/number, push it onto the stack
            if x.token not in precedences:
                val_stack.append(x)
            else:
                if len(val_stack) < 2:
                    fatal_error(x, "Operator does not have enough inputs...")
                second = val_stack.pop()
                first = val_stack.pop()
                # op = x
                if x.token == "=":
                    for y in prefix:
                        result.append(y)
                else:
                    result.append(Token("$INFER", x.line_number, x.filename))
                    result.append(Token("#" + str(self.varnum), x.line_number, x.filename))
                    result.append(Token("=", x.line_number, x.filename))
                    val_stack.append(Token("#" + str(self.varnum), x.line_number, x.filename))

                    # TODO: infer the type of <first> <op> <second>
                    while len(self.token_types) <= self.varnum:
                        self.token_types.append("NA")

                    """
                    "call"
                    "access"
                    "."
                    "->"
                    "un+"
                    "un-"
                    "lognot"
                    "bitnot"
                    "cast"
                    "deref"
                    "ref"
                    "*"
                    "/"
                    "%"
                    "+"
                    "-"
                    "<<"
                    ">>"
                    "<"
                    "<="
                    ">"
                    ">="
                    "=="
                    "!="
                    "&"
                    "^"
                    "|"
                    "&&"
                    "||"
                    "="
                    ","
                    "un++"
                    "un--"
                    "lognot"
                    "bitnot"
                    "cast"
                    "deref"
                    "ref"
                    """
                    match(x.token):
                        case "cast":
                            self.token_types[self.varnum] = self.parse_type_string(first.types, self.type_structures, self.type_unions)
                            result.append(second)
                            self.varnum += 1
                            result.append(Token(";", x.line_number, x.filename))
                            continue
                        case "+":
                            pass
                        case "-":
                            pass
                        case "+":
                            pass
                        case "+":
                            pass
                        case "+":
                            pass
                        case "+":
                            pass
                        case "+":
                            pass
                        case "+":
                            pass
                        case "+":
                            pass
                        case "+":
                            pass

                    self.varnum += 1

                result.append(first)
                result.append(x)
                result.append(second)
                result.append(Token(";", x.line_number, x.filename))


        print(f"RESULT: {result}")

        tokens = tokens[:line_start] + result + tokens[line_end+1:]

        return tokens


    def parse_structs_unions_enums_and_typedefs(self, tokens:list[Token]):
        i = 0
        n = len(tokens)

        # handle structs and unions
        while i < n:
            if tokens[i] == "$STRUCT" or tokens[i] == "$UNION":
                # get the name
                the_name = None
                if i + 1 < n and len(tokens[i+1].token) > 0 and tokens[i+1].token[0] == "#":
                    the_name = self.variable_names[tokens[i+1].token]
                    del tokens[i+1]
                    n -= 1

                # TODO: finish structs/unions
                member_names = []
                member_types = []

                if tokens[i] == "$STRUCT":
                    the_struct = standard.Structure(the_name, member_names, member_types)
                    self.structures.append(the_struct)
                else:
                    the_struct = standard.Union(the_name, member_names, member_types)
                    self.unions.append(the_struct)
                tokens[i] = the_struct
            elif tokens[i] == "$ENUM":
                the_name = None
                if i + 1 < n and len(tokens[i+1].token) > 0 and tokens[i+1].token[0] == "#":
                    the_name = self.variable_names[tokens[i+1].token]
                    del tokens[i+1]
                    n -= 1
                # TODO: finish enums
                member_names = []
                member_values = []

                the_enum = standard.Enum(the_name, member_names, member_values)
                self.enums.append(the_enum)
                tokens[i] = the_enum
            i += 1

        # get function definitions now
        i = 0
        n = len(tokens)
        while i < n:
            # variable followed by ( is a function
            if i + 1 < n and len(tokens[i].token) > 0:
                if tokens[i].token[0] == "#" and tokens[i+1] == "(":
                    starting_index = i
                    # this is a function def
                    the_name = self.variable_names[tokens[i].token]
                    return_type = standard.Type(self.token_types[int(tokens[i].token[1:])])

                    # TODO: set the type of the function's variable in self.token_types

                    arg_types = []
                    arg_constraints = []
                    i += 1
                    parens = []

                    args = [[]]
                    while i < n:
                        if tokens[i] == "(":
                            parens.append("(")
                        elif tokens[i] == ")":
                            parens.pop()
                            if len(parens) == 0:
                                break
                        elif tokens[i] == ",":
                            args.append([])
                            pass
                        else:
                            args[-1].append(tokens[i])
                        i += 1

                    # if it ends in );, ignore this function
                    declaration = False

                    print(f"ARGS: {args}")
                    arg_names = [x[0] for x in args]
                    print(f"ARGNAMES: {arg_names}")
                    if len(args) == 1 and len(args[0]) == 1 and args[0][0] == "$TYPE" and len(args[0][0].types) == 1 and args[0][0].types[0] == "void":
                        arg_types = [self.variable_types[x] for x in args]
                        # TODO: create function constraints
                        arg_constraints = []
                    else:
                        pass

                    
                    func_tokens = []
                    if i + 1 >= n or tokens[i+1] == ";":
                        declaration = True
                    elif tokens[i+1] == "{":
                        i += 2
                        braces = 1
                        while i < n:
                            if tokens[i] == "{":
                                braces += 1
                            elif tokens[i] == "}":
                                braces -= 1
                                if braces == 0:
                                    break
                            func_tokens.append(tokens[i])
                            del tokens[i]
                            n -= 1

                    while i > starting_index:
                        del tokens[starting_index]
                        i -= 1
                        n -= 1
                    the_function = standard.Function(the_name, return_type, arg_names, arg_types, arg_constraints, func_tokens, declaration)
                    if i < len(tokens):
                        tokens[i] = the_function
                    else:
                        tokens.append(the_function)
                    self.functions.append(the_function)
            
            i += 1

        return tokens



    def convert_returns(self):
        # int foo(int x){return 3;}
        # y = foo(3);
        # =>
        # void foo(int* z, int x){*z = 3;}
        # foo(&y, 3);

        for func in self.functions:
            i = 0
            n = len(func.tokens)
            print(f"Converting returns:")
            print(f"{func.arg_types}")
            print(f"{func.return_type}")
            print(func.tokens)

            if func.return_type.type == "void":
                return_var = None
                return_type = None
                return_varnum = None
            else:
                return_var = f"#{self.varnum}"
                return_varnum = self.varnum
                return_type = standard.Type(f"*{func.return_type.type}")

                func.args.insert(0, Token(f"{return_var}", func.tokens[i-1].filename, func.tokens[i-1].line_number))
                func.arg_types.insert(0, standard.Type(f"*{func.return_type.type}"))

                func.arg_constraints.insert(0, standard.Constraint([]))
                func.return_type = standard.Type("void")

                while len(self.token_types) <= self.varnum:
                    self.token_types.append("NA")

                self.token_types[self.varnum] = standard.Type(return_type)

                self.varnum += 1


            while i < n:
                if func.tokens[i] == "return":
                    if i + 1 < len(func.tokens):
                        if func.tokens[i+1].token != ";":
                            # this is an actual return
                            if return_type is None:
                                fatal_error(func.tokens[i], "Cannot return value in void function.")
                            func.tokens[i] = Token(f"{return_var}", func.tokens[i].filename, func.tokens[i].line_number)
                            i += 1
                            func.tokens.insert(i, Token("access", func.tokens[i].filename, func.tokens[i].line_number))
                            i += 1
                            n += 1
                            func.tokens.insert(i, Token("0", func.tokens[i].filename, func.tokens[i].line_number))
                            i += 1
                            n += 1
                            func.tokens.insert(i, Token("=", func.tokens[i].filename, func.tokens[i].line_number))
                            i += 3
                            n += 1

                            func.tokens.insert(i, Token("return", func.tokens[i-1].filename, func.tokens[i-1].line_number))
                            i += 1
                            n += 1
                            func.tokens.insert(i, Token(";", func.tokens[i-1].filename, func.tokens[i-1].line_number))
                            i += 1
                            n += 1
                            
                i += 1




    def remove_unary_operators(self, tokens:list[Token]) -> list[Token]:
        i = 0
        n = len(tokens)
        while i < n:
            if tokens[i] == "un+":
                tokens[i].token = "+"
            elif tokens[i] == "un-":
                tokens[i].token = "-"
            i += 1
        return tokens


    def remove_arrows(self):
        for func in self.functions:
            tokens = func.tokens
            i = 0
            n = len(tokens)
            while i < n:
                if tokens[i] == "->":
                    tokens[i].token = ")"
                    i += 1
                    tokens.insert(i, Token(".", tokens[i].line_number, tokens[i].filename))
                    n += 1
                    parens = 0
                    return_index = i
                    while i > 0:
                        if tokens[i].token in ["=", "{", "}", ";"]:
                            i += 1
                            break
                        i -= 1
                    tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("deref", tokens[i].line_number, tokens[i].filename))
                    n += 1
                    i = return_index + 3
                    continue
                i += 1
            func.tokens = self.break_multiple_operations(func.tokens)


    def remove_or_equal(self):
        for func in self.functions:
            tokens = func.tokens
            # remove <=, >=, and !=
            # x <= y 
            # 0 lognot (x > y)
            i = 0
            n = len(tokens)
            while i < n:
                replace = False
                if tokens[i] == "<=":
                    replace = True
                    operator = ">"
                elif tokens[i] == ">=":
                    replace = True
                    operator = "<"
                elif tokens[i] == "!=":
                    replace = True
                    operator = "=="

                if replace:
                    tokens[i].token = operator
                    starting_index = i
                    while i < n:
                        if tokens[i] == ";":
                            break
                        i += 1
                    tokens.insert(i, Token(")", tokens[i].line_number, tokens[i].filename))
                    n += 1
                    i = starting_index
                    while i > 0:
                        if tokens[i].token in ["=", "{", "}", ";"]:
                            i += 1
                            break
                        i -= 1
                    tokens.insert(i, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("lognot", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1

                i += 1
            func.tokens = self.break_multiple_operations(func.tokens)


    def create_else_clauses(self):
        for func in self.functions:
            tokens = func.tokens
            i = 0
            n = len(tokens)
            while i < n:
                if tokens[i] == "if":
                    braces = 0
                    while i < n:
                        if tokens[i] == "{":
                            braces += 1
                        elif tokens[i] == "}":
                            braces -= 1
                            if braces == 0:
                                i += 1
                                break
                        i += 1
                    if i >= n or tokens[i].token != "else":
                        tokens.insert(i, Token("else", tokens[i].line_number, tokens[i].filename))
                        i += 1
                        n += 1
                        tokens.insert(i, Token("{", tokens[i].line_number, tokens[i].filename))
                        i += 1
                        n += 1
                        tokens.insert(i, Token("}", tokens[i].line_number, tokens[i].filename))
                        i += 1
                        n += 1
                
                i += 1
            func.tokens = self.break_multiple_operations(func.tokens)


    def remove_logical_or(self):

        # x || y
        # !(!(x)&&!(y))

        for func in self.functions:
            tokens = func.tokens
            i = 0
            n = len(tokens)
            while i < n:
                if tokens[i] == "||":
                    starting_index = i
                    tokens[i].token = "&&"
                    i += 1
                    tokens.insert(i, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("lognot", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    while i < n:
                        if tokens[i] == ";":
                            break
                        i += 1
                    pass
                    tokens.insert(i, Token(")", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token(")", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1

                    i = starting_index
                    tokens.insert(i, Token(")", tokens[i].line_number, tokens[i].filename))
                    n += 1
                    while i > 0:
                        if tokens[i].token in ["=", "{", "}", ";"]:
                            i += 1
                            break
                        i -= 1
                    tokens.insert(i, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("lognot", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("lognot", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1
                    tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    n += 1


                i += 1


            func.tokens = self.break_multiple_operations(func.tokens)


    def remove_logical_and(self):
        # a && b
        # =>
        # result = 0
        # if (a){
        #     if(b){
        #         result = 1
        #     }
        # }

        for func in self.functions:
            tokens = func.tokens
            
            i = 0
            n = len(tokens)
            while i < n:
                if tokens[i] == "&&":
                    before = []
                    j = i-2
                    while j >= 0:
                        if tokens[j].token in [";", "{", "}", "("]:
                            break
                        j -= 1
                    before = tokens[j+1:i-1]
                    tokens.insert(i-1, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i-1, Token(";", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i-1, Token("if", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i-1, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens[i] = Token(")", tokens[i].line_number, tokens[i].filename)
                    i += 1
                    tokens.insert(i, Token("{", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("if", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 2
                    tokens.insert(i, Token(")", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("{", tokens[i].line_number, tokens[i].filename))
                    i += 1

                    for the_token in before:
                        tokens.insert(i, Token(the_token.token, the_token.line_number, the_token.filename))
                        i += 1

                    tokens.insert(i, Token("1", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token(";", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("}", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("else", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("{", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("}", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("}", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("else", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("{", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("}", tokens[i].line_number, tokens[i].filename))
                    if i + 1 < len(tokens):
                        if tokens[i+1] == ";":
                            del tokens[i+1]

                    n = len(tokens)

                i += 1

            func.tokens = tokens

    def remove_logical_not(self):
        for func in self.functions:
            tokens = func.tokens
            
            i = 0
            n = len(tokens)
            while i < n:
                if tokens[i] == "lognot":
                    j = i - 2
                    while j >= 0:
                        if tokens[j].token in [";", "{", "}", "("]:
                            break
                        j -= 1
                    before = tokens[j+1:i-1]

                    tokens[i-1] = Token("1", tokens[i].line_number, tokens[i].filename)

                    tokens[i] = Token(";", tokens[i].line_number, tokens[i].filename)
                    i += 1
                    tokens.insert(i, Token("if", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("(", tokens[i].line_number, tokens[i].filename))
                    i += 2
                    tokens.insert(i, Token(")", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("{", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    for the_token in before:
                        tokens.insert(i, Token(the_token.token, the_token.line_number, the_token.filename))
                        i += 1
                    tokens.insert(i, Token("0", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token(";", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("}", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("else", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("{", tokens[i].line_number, tokens[i].filename))
                    i += 1
                    tokens.insert(i, Token("}", tokens[i].line_number, tokens[i].filename))
                    if i + 1 < len(tokens) and tokens[i+1] == ";":
                        del tokens[i+1]

                    n = len(tokens)

                i += 1

            func.tokens = tokens


    def remove_remaining_parenthesis(self):
        for func in self.functions:
            i = 0
            n = len(func.tokens)
            while i < n:
                if func.tokens[i] == "(" or func.tokens[i] == ")":
                    del func.tokens[i]
                    i -= 1
                    n -= 1
                i += 1


    def convert_derefs_to_accesses(self):
        for func in self.functions:
            i = 0
            n = len(func.tokens)
            while i < n:
                if func.tokens[i] == "deref":
                    if i == 0 or i + 1 >= n:
                        fatal_error(func.tokens[i], "Expected pointer after deref.")
                        continue
                    temp = func.tokens[i-1]
                    func.tokens[i-1] = func.tokens[i+1]
                    func.tokens[i+1] = temp

                    func.tokens[i].token = "access"
                i += 1

        




