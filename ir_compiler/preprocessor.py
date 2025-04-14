
from debug import *
from tokens import *

import lexer
import normalizer

import os

INCLUDED_ALREADY = set()

USER_LIBS = set()
LIBRARY_LIBS = set()

"""
OPERATORS:
    # - Stringize
    ## - Token Pasting
DIRECTIVES:
    define
    undef
    include
    ifdef
    ifndef
    if
    else
    elif
    endif
CONDITIONALS:
    defined()
    +, -, *, /, %,
    ==, !=, <, >, <=, >=,
    &&, ||, !,
    &, |, ^, ~, <<, >>
PREDEFINED:
    __DATE__
    __TIME__
    __FILE__
    __LINE__
    __STDC__
"""

class FunctionMacro:
    def __init__(self, args:Tokens, definition, is_variadic=False):
        self.args = args
        self.is_variadic = is_variadic
        self.definition = definition

    def get_replacement(self, args:Tokens):
        dbg(f"Getting replacement for {args}")
        result = Tokens([])

        # throw error if not enough args supplied
        if self.is_variadic:
            if len(args) < len(self.args)-1:
                self.definition[0].fatal_error("Too few args supplied to Macro")
        else:
            if len(args) > len(self.args):
                self.definition[0].fatal_error("Too many args supplied to Macro")
            elif len(args) < len(self.args):
                self.definition[0].fatal_error("Too few args supplied to Macro")

        for x in self.definition:
            result.append(x)

        # put the passed values into the definition
        i = 0
        n = len(result)
        while i < n:
            if result[i] == "__VA_ARGS__":
                if not self.is_variadic:
                    result[i].fatal_error("Cannot use __VA_ARGS__ in non-variadic function")
                insertion = []
                for j in range(len(self.args)-1, len(args)):
                    insertion += args[j]
                    if j < len(args)-1:
                        new_tok = string_to_token(",")
                        insertion.append(new_tok)
                print(result[i])
                del result[i]
                result.insert_all(i, insertion)
                i += len(insertion)
                n = len(result)
                continue
            elif result[i] in self.args:
                ind = self.args.index(result[i])
                del result[i]
                result.insert_all(i, args[ind])
                i += len(args[ind])
                n = len(result)
                continue
            i += 1

        result.remove_all("#DEFINE_SPACE")
        result.remove_all("#END_DIRECTIVE")

        # perform stringizing
        i = 0
        n = len(result)
        while i < n:
            if result[i] == "#":
                # next toke becomes string literal
                if i + 1 >= n:
                    result[i].fatal_error("Expected token to stringize after this")
                del result[i]
                n -= 1
                result[i].token = f'"{result[i].token}"'
            i += 1

        # perform token pasting
        i = 0
        n = len(result)
        while i < n:
            if result[i] == "##":
                del result[i]
                i -= 1
                n -= 1
                if i + 1 >= n:
                    result[i].fatal_error("Expected token to paste with after")
                result[i].token += result[i+1].token
                del result[i+1]
                n -= 1
            i += 1

        return result


DEFINITIONS = {}

# add builtin definitions
DEFINITIONS["__STDC__"] = strings_to_tokens(["1"])
DEFINITIONS["__STDC_VERSION__"] = strings_to_tokens(["199901"])
DEFINITIONS["__STDC_HOSTED__"] = strings_to_tokens(["0"])
DEFINITIONS["__STDC_NO_ATOMICS__"] = strings_to_tokens(["1"])
DEFINITIONS["__STDC_NO_THREADS__"] = strings_to_tokens(["1"])
DEFINITIONS["__STDC_NO_VLA__"] = strings_to_tokens(["1"])
DEFINITIONS["__linux__"] = strings_to_tokens(["1"])
DEFINITIONS["__unix__"] = strings_to_tokens(["1"])
DEFINITIONS["__x86_64__"] = strings_to_tokens(["1"])
DEFINITIONS["__GNUC__"] = strings_to_tokens(["1"])
DEFINITIONS["__clang__"] = strings_to_tokens(["1"])
DEFINITIONS["__BYTE_ORDER__"] = strings_to_tokens(["__ORDER_LITTLE_ENDIAN__"])
DEFINITIONS["__SIZEOF_INT__"] = strings_to_tokens(["4"])
DEFINITIONS["__SIZEOF_LONG__"] = strings_to_tokens(["8"])
DEFINITIONS["__SIZEOF_POINTER__"] = strings_to_tokens(["8"])
DEFINITIONS["__CHAR_BIT__"] = strings_to_tokens(["8"])
DEFINITIONS["__INT_MAX__"] = strings_to_tokens(["2147483647"])
DEFINITIONS["__LONG_MAX__"] = strings_to_tokens(["9223372036854775807"])
DEFINITIONS["__SIZE_MAX__"] = strings_to_tokens(["18446744073709551615"])
DEFINITIONS["_FILE_OFFSET_BITS"] = strings_to_tokens(["18446744073709551615"])
DEFINITIONS["__cplusplus"] = strings_to_tokens(["199711"])
DEFINITIONS["_XOPEN_SOURCE"] = strings_to_tokens(["500"])


CONDITIONS = []
DELETING = False

def preprocess(toks:Tokens, include_dirs=[]):
    """
    iterate through the file and handle a directive at a time
    """
    dbg("Handling Directives...")
    toks = handle_directives(toks, include_dirs=include_dirs)

    dbg("Finshed Preprocessing!")
    dbg(toks)
    return toks


def handle_directives(toks:Tokens, include_dirs=[]):
    i = 0
    n = len(toks)

    while i < n:
        if toks[i] == "#":
            directive = toks.splice_until(i, "#END_DIRECTIVE")
            directive = Tokens(directive)
            dbg(f"Found directive:")
            dbg(directive)
            handle_directive(directive, toks, i, include_dirs=include_dirs)
            n = len(toks)
            i -= 1
        elif DELETING:
            del toks[i]
            i -= 1
            n -= 1
        elif toks[i] in DEFINITIONS:
            # replace with the definition
            toks = replace_index_with_defined(toks, i)
            new_n = len(toks)
            i -= 1
            n = new_n
        i += 1

    return toks


def replace_index_with_defined(toks:Tokens, index:int):
    """
    Use the definitions to replace tokens at specific index
    """
    # see if this should be function-like or normal
    if toks[index] not in DEFINITIONS:
        return toks

    the_definition = DEFINITIONS[toks[index]]
    print(f"{toks[index]} -> {the_definition}")

    if issubclass(type(the_definition), FunctionMacro):
        dbg("Should be replaced with function macro")
        if index + 1 >= len(toks) or toks[index+1] != "(":
            return toks
        arg_values = toks.get_match_content(index+1, ")")
        if arg_values is None:
            toks[index+1].fatal_error("Unmatched (")
        arg_values = arg_values[1:-1]
        arg_values = Tokens(arg_values).split_at(",")
        dbg(f"Function args values: {arg_values}")
        replacement = the_definition.get_replacement(arg_values)
        dbg(f"Replacement = {replacement}")

        del toks[index]
        toks.insert_all(index, replacement)

    else:
        dbg("Should be replaced normally")
        del toks[index]
        toks.insert_all(index, the_definition)
    
    dbg(toks)

    return toks


def replace_with_defined(toks:Tokens):
    """
    Use the definitions to replace tokens
    """
    i = 0
    n = len(toks)
    print(f"Replacing {toks} with defined")
    print(DEFINITIONS)
    while i < len(toks):
        if toks[i] in DEFINITIONS:
            toks = replace_index_with_defined(toks, i)
            new_n = len(toks)
            i += new_n - n
            n = new_n
        i += 1
    return toks


def get_directive_type(directive):
    if len(directive) <= 1:
        directive[0].fatal_error("Expected content in directive")
    valid_types = set(["define", "undef", "include", "ifdef", "ifndef", "if", "else", "elif", "endif", "error", "warning"])

    i = 1
    while i < len(directive):
        if directive[i] not in valid_types:
            if directive[i] != "#DEFINE_SPACE":
                directive[i].fatal_error("Invalid directive")
        else:
            return directive[i]
        i += 1


def handle_directive(directive, toks, index, include_dirs=[]):
    directive_type = get_directive_type(directive)
    match (directive_type):
        case "define":
            if not DELETING:
                handle_define(directive)
        case "undef":
            if not DELETING:
                handle_undef(directive)
        case "include":
            if not DELETING:
                handle_include(directive, toks, index, include_dirs=include_dirs)
        case "ifdef":
            handle_ifdef(directive)
        case "ifndef":
            handle_ifndef(directive)
        case "if":
            directive = handle_define_check(directive)
            directive = replace_with_defined(directive)
            handle_if(directive)
        case "else":
            handle_else(directive)
        case "elif":
            directive = handle_define_check(directive)
            directive = replace_with_defined(directive)
            handle_elif(directive)
        case "endif":
            handle_endif(directive)
        case "error":
            if not DELETING:
                handle_error(directive)
        case "warning":
            if not DELETING:
                handle_warning(directive)


def handle_define_check(directive):
    """
    """
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")

    dbg("Handling define checks")
    dbg(directive)
    i = 0
    n = len(directive)
    while i < n:
        if directive[i] == "defined":
            if i + 3 >= n or directive[i+1] != "(" or directive[i+3] != ")":
                if i + 1 >= n:
                    directive[i].fatal_error("Expected token after defined")
                if directive[i+1] in DEFINITIONS:
                    directive[i].token = "1"
                    dbg(f"defined({directive[i+1]}) = 1")
                else:
                    directive[i].token = "0"
                    dbg(f"defined({directive[i+1]}) = 0")
                del directive[i+1]
                n -= 1
            else:
                if directive[i+2] in DEFINITIONS:
                    directive[i].token = "1"
                    dbg(f"defined({directive[i+2]}) = 1")
                else:
                    directive[i].token = "0"
                    dbg(f"defined({directive[i+2]}) = 0")
                del directive[i+1]
                del directive[i+1]
                del directive[i+1]
                n -= 3
        i += 1
    dbg("After checking")
    dbg(directive)
    return directive


def handle_define(directive):
    dbg("Handling define...")
    if len(directive) > 0 and directive[-1] == "#END_DIRECTIVE":
        del directive[-1]

    # figure out if a normal or function-like macro
    # first, get first thing after the define and DEFINE_SPACE
    while len(directive) > 0:
        if directive[0] != "define":
            del directive[0]
        else:
            define_token = directive[0]
            del directive[0]
            if directive[0] == "#DEFINE_SPACE":
                del directive[0]
            break
    # we should now be at the definition name
    if len(directive) == 0:
        define_token.fatal_error("Expected definition after define")

    the_definition = directive[0]
    if len(directive) < 2:
        handle_normal_define(the_definition, [])
        return
    dbg(f"DefName = {the_definition}")

    if directive[1] == "(":
        definition_type = "function"
    else:
        definition_type = "normal"

    dbg(f"Definition type is {definition_type}")
    if definition_type == "normal":
        # if normal, add to definitions
        del directive[0]
        print(directive)

        dbg("Replacing with defined")
        dbg(directive)
        directive = replace_with_defined(directive)

        directive.remove_all("#DEFINE_SPACE")

        handle_normal_define(the_definition, directive)
    else:
        # if function-like, handle separately
        del directive[0]
        directive = Tokens(directive)
        directive = replace_with_defined(directive)
        args = directive.get_match_content(0, ")")
        if args is None:
            directive[0].fatal_error("Unmatched (")
        args = args[1:-1]

        directive.remove_all("#DEFINE_SPACE")

        dbg(f"{args = }")
        dbg(f"{directive = }")
        

        handle_function_define(the_definition, args, directive)


def handle_normal_define(the_definition, directive):
    dbg("Handling normal define:")
    dbg(f"\tdefinition: {the_definition}")
    dbg(f"\tdirective: {directive}")
    if the_definition in DEFINITIONS:
        the_definition.fatal_error(f"Redefinition of {the_definition}")
    directive = [x for x in directive if x != "#DEFINE_SPACE"]
    DEFINITIONS[the_definition] = Tokens(directive)


def handle_function_define(the_definition, args, directive):
    dbg("Handling function define:")
    dbg(f"\tdefinition: {the_definition}")
    dbg(f"\targs: {args}")
    dbg(f"\tdirective: {directive}")
    if the_definition in DEFINITIONS:
        the_definition.fatal_error(f"Redefinition of {the_definition}")
    directive = Tokens([x for x in directive if x != "#DEFINE_SPACE"])

    args = Tokens(args)
    args.combine_all([".", ".", "."])
    args.remove_all("#DEFINE_SPACE")
    args = args.split_at(",")
    # combine ...
    # combine ##
    directive.combine_all(["#", "#"])

    # throw error if ... exists and is not last arg
    is_variadic = False
    for i in range(len(args)):
        if len(args[i]) == 0:
            #the_definition.fatal_error("Cannot define function-like macro with empty argument")
            break
        args[i] = args[i][0]
        if args[i] == "...":
            if i != len(args)-1:
                args[i].fatal_error("... must be last argument")
            is_variadic = True

    # create FunctionMacro object
    result = FunctionMacro(args, directive, is_variadic=is_variadic)

    DEFINITIONS[the_definition] = result


def handle_undef(directive):
    dbg("Handling undef...")
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")
    if len(directive) < 3:
        directive[1].fatal_error("Expected a definition after undef")
    definition = directive[2]
    if definition in DEFINITIONS:
        DEFINITIONS.pop(definition)
        dbg(f"Removed definition of {definition}")


def handle_include(directive:Tokens, toks, index, include_dirs=[]):
    dbg("Handling include...")
    dbg(directive)
    # figure out if it is a user or library include
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")
    while len(directive) > 0:
        if directive[0] == "include":
            include_word = directive[0]
            del directive[0]
            break
        del directive[0]

    if len(directive) == 0:
        include_word.fatal_error("Expected filename after include")

    if len(directive[0]) > 0 and directive[0][0] == '"':
        lib_type = "local"
    elif directive[0] == "<":
        lib_type = "lib"
    else:
        directive[0].fatal_error("Excpected \" or < after include")

    if lib_type == "lib" and directive[-1] != '>': 
        directive[-1].fatal_error("Excpected > at end of library include")


    if lib_type == "lib":
        filepath = "".join([x.token for x in directive[1:-1]])
        dbg(f"{filepath = }")
        dbg("Library include...")
        LIBRARY_LIBS.add(filepath)
        """
        result = handle_library_include(filepath, include_dirs=include_dirs)
        toks.insert_all(index, result)
        """
    else:
        filepath = directive[0].token.strip('"')
        dbg(f"{filepath = }")
        dbg("User include...")
        USER_LIBS.add(filepath)
        """
        result = handle_user_include(filepath, include_dirs=include_dirs)
        toks.insert_all(index, result)
        """
    


def handle_ifdef(directive:Tokens):
    dbg("Handling ifdef...")
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")
    if len(directive) < 3:
        directive[1].fatal_error("Invalid ifdef syntax")
    definition = directive[2]
    if definition in DEFINITIONS:
        CONDITIONS.append(True)
        dbg("ifdef = True")
    else:
        CONDITIONS.append(False)
        dbg("ifdef = False")
    should_delete()

def handle_ifndef(directive):
    dbg("Handling ifndef...")
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")
    if len(directive) < 3:
        directive[1].fatal_error("Invalid ifndef syntax")
    definition = directive[2]
    if definition in DEFINITIONS:
        CONDITIONS.append(False)
        dbg("ifndef = False")
    else:
        CONDITIONS.append(True)
        dbg("ifndef = True")
    should_delete()

def handle_if(directive):
    dbg("Handling if...")
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")
    condition = directive[2:]
    result = check_condition(condition)
    CONDITIONS.append(result)
    dbg(f"if = {result}")
    should_delete()


def handle_else(directive):
    dbg("Handling else...")
    # if condition was true, change to None
    if len(CONDITIONS) == 0:
        directive[1].fatal_error("No conditional opened")
    if CONDITIONS[-1] == True:
        CONDITIONS[-1] = None
        dbg("Closed previous conditional")
    elif CONDITIONS[-1] == False:
        CONDITIONS[-1] = True
        dbg("else = True")
    should_delete()


def handle_elif(directive):
    dbg("Handling elif...")
    if len(CONDITIONS) == 0:
        directive[1].fatal_error("No conditional opened")
    if CONDITIONS[-1] == True:
        CONDITIONS[-1] = None
        dbg("Closed previous conditional")
    elif CONDITIONS[-1] == False:
        # check the condition
        directive.remove_all("#DEFINE_SPACE")
        directive.remove_all("#END_DIRECTIVE")
        condition = directive[2:]
        result = check_condition(condition)
        CONDITIONS[-1] = result
        dbg(f"elif = {result}")
    should_delete()


def handle_endif(directive):
    dbg("Handling endif...")
    if len(CONDITIONS) == 0:
        directive[1].fatal_error("Unmatched endif")
    CONDITIONS.pop()
    dbg("Closed conditional")
    should_delete()


def check_condition(condition):
    """
    +, -, /, *, %, 
    ==, !=, <, >, <=, >=
    &&, ||, !, 
    &, |, ^, ~, <<, >>
    """
    dbg(f"Checking condition:")
    dbg(condition)
    # Evaluate expression
    condition = Tokens(condition)

    # combine multi-token operators
    condition.combine_all(["=", "="])
    condition.combine_all(["!", "="])
    condition.combine_all(["<", "="])
    condition.combine_all([">", "="])
    condition.combine_all(["&", "&"])
    condition.combine_all(["|", "|"])
    condition.combine_all(["<", "<"])
    condition.combine_all([">", ">"])

    # convert unary operators
    i = 0
    n = len(condition)
    while i < n:
        if condition[i] in ["!", "~"]:
            condition.insert(i, string_to_token("0"))
            i += 1
            n += 1
        i += 1

    # convert to postfix
    postfix_expression = convert_to_postfix(condition)
    dbg(f"postfix expression: {postfix_expression}")

    # evaluate
    dbg("Evaluating")

    operators = set(["+", "-", "/", "*", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", "?", ":"])

    stack = []

    for x in postfix_expression:
        if x in operators:
            if len(stack) < 2:
                x.fatal_error("Expected 2 operands for operator")
            second = stack.pop()
            first = stack.pop()
            # perform operation and push result to stack
            intermediate = perform_operation(first, x, second)
            stack.append(intermediate)
        else:
            try:
                new_val = int(x.token)
                if str(new_val) != x.token:
                    x.fatal_error("Can only use ints and operators in condition")
            except:
                new_val = 0

            # push to stack
            stack.append(new_val)

    print(stack)
    # final result should be an integer still on stack
    if len(stack) != 1:
        # hopefully impossible state
        condition[0].fatal_error("Bad parse of conditional")

    # pop result and return true/false
    result = stack.pop()
    dbg(f"result = {result}")
    return result != 0


def perform_operation(first:int, operator:str, second:int):
    """
    Perform a single operation given the operands and operator
    """
    match (operator):
        case "+":
            return first + second
        case "-":
            return first - second
        case "/":
            return int(first // second)
        case "*":
            return first * second
        case "%":
            return first % second
        case "==":
            return 1 if first == second else 0
        case "!=":
            return 1 if first != second else 0
        case "<":
            return 1 if first < second else 0
        case ">":
            return 1 if first > second else 0
        case "<=":
            return 1 if first <= second else 0
        case ">=":
            return 1 if first >= second else 0
        case "&&":
            return 1 if first != 0 and second != 0 else 0
        case "||":
            return 1 if first != 0 or second != 0 else 0
        case "!":
            return 1 if second == 0 else 0
        case "&":
            return first & second
        case "|":
            return first | second
        case "^":
            return first ^ second
        case "~":
            return ~second
        case "<<":
            return first << second
        case ">>":
            return first >> second
        case "?":
            return False if first == 0 else second
        case ":":
            return second if first == False else first



def convert_to_postfix(infix):
    dbg(f"Converting {infix} to postfix")
    result = []

    operators = {
        "!":(2, "right"),
        "~":(2, "right"),

        "*":(3, "left"),
        "/":(3, "left"),
        "%":(3, "left"),

        "+":(4, "left"),
        "-":(4, "left"),

        "<<":(5, "left"),
        ">>":(5, "left"),

        "<":(6, "left"),
        ">":(6, "left"),
        "<=":(6, "left"),
        ">=":(6, "left"),

        "==":(7, "left"),
        "!=":(7, "left"),

        "&":(8, "left"),

        "^":(9, "left"),

        "|":(10, "left"),

        "&&":(11, "left"),

        "||":(12, "left"),

        "?":(13, "left"),
        ":":(13, "left"),
    }

    expression = []
    op_stack = []

    for x in infix:
        # if x is an operand, put it in the expression
        if x not in operators and x not in ["(", ")"]:
            expression.append(x)
        else:
            # if (, push to stack
            # if ), pop until (
            if x == "(":
                op_stack.append(x)
            elif x == ")":
                while 1:
                    if len(op_stack) == 0:
                        x.fatal_error("Unmatched )")
                    if op_stack[-1] == "(":
                        op_stack.pop()
                        break
                    else:
                        expression.append(op_stack.pop())
            else:
                # if precedence of current operator is higher than on top of stack, stack is empty, or contains (, push to stack
                if len(op_stack) == 0 or op_stack[-1] == "(" or operators[x][0] < operators[op_stack[-1]][0]:
                    op_stack.append(x)
                else:
                    # else pop from stack while top of stack >= then push current to stack
                    while len(op_stack) > 0 and op_stack[-1] != "(" and operators[op_stack[-1]][0] <= operators[x][0]:
                        expression.append(op_stack.pop())
                    op_stack.append(x)

    while len(op_stack) > 0:
        expression.append(op_stack.pop())

    return expression


def should_delete():
    global DELETING
    DELETING = False
    for x in CONDITIONS:
        if x is None or x == False:
            DELETING = True
    return DELETING


def handle_error(directive):
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")
    if len(directive) < 2:
        directive[0].fatal_error("Expected error message in error directive")

    print("PREPROCESSOR ERROR:")
    print("\t" + directive[2].token.strip('"'))
    panic("Enountered Preprocessor error")

def handle_warning(directive):
    directive.remove_all("#DEFINE_SPACE")
    directive.remove_all("#END_DIRECTIVE")
    if len(directive) < 2:
        directive[0].fatal_error("Expected warning message in warning directive")

    print("PREPROCESSOR WARNING:")
    print("\t" + directive[2].token.strip('"'))


