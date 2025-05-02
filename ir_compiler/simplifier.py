
from debug import *
from tokens import *

def simplify(toks:Tokens):
    # handle typing (converting types into single #TYPE tokens)
    toks = convert_type_tokens(toks)

    # get possible names after #ENUM, #STRUCT, and #UNION
    toks = get_possible_names(toks)

    # handle enums (converting enums into single #ENUM tokens)
    # TODO:
    toks = convert_enums(toks)

    # handle structs, unions (converting into single #STRUCT and #UNION tokens)
    # TODO:
    toks = convert_structs_and_unions(toks)

    # handle typedefs 
    toks = handle_typedefs(toks)

    # combine structs and pointers now
    toks = combine_structs_and_pointers(toks)

    #  combine types and [int]
    toks = combine_array_types(toks)

    # handle do-while loops (converting to a while loop)
    toks = handle_do_whiles(toks)

    # TODO: handle compound literals
    dbg(toks)

    # TODO: handle static and const

    # add extra scopes around for loops to protect variable names
    toks = add_extra_scopes(toks)

    dbg(toks)
    # generalize variables, assigning each a type
    toks = handle_generalization(toks)

    dbg(toks)

    # handle functions (converting functions into single #FUNC tokens)
    toks = handle_functions(toks)

    dbg("Finished Simplification!")
    dbg(toks)

    return toks


"""
char
signed char
unsigned char
short
short int
signed short
signed short int
unsigned short
unsigned short int
int
signed
signed int
unsigned
unsigned int
long
long int
signed long
signed long int
unsigned long
unsigned long int
long long
long long int
signed long long
signed long long int
unsigned long long
unsigned long long int
float
double
long double

TYPE* var;
TYPE** var;
TYPE var[INT];
TYPE* var[INT];
TYPE (*var)[INT];
TYPE (*var)(TYPE);
"""


def convert_type_tokens(toks:Tokens):
    """
    Convert all type descriptors of a single token
    into a single #TYPE token
    """
    # handle primitive types
    toks = handle_primitive_types(toks)

    # handle pointer types
    toks = handle_pointer_types(toks)

    # handle array types

    # handle compound pointer, array types

    # handle function pointer types

    return toks


def handle_primitive_types(toks:Tokens):
    """
    combine primitive types into single type tokens
    """
    i = 0
    n = len(toks)
    starters = set([
            "void",
            "char",
            "short",
            "int",
            "long",
            "float",
            "double",
            "signed",
            "unsigned",
            "size_t",
            "ssize_t",
            "clock_t"

            "__builtin_va_list",
        ])

    while i < n:
        if toks[i] in starters or toks[i] in ["enum", "struct", "union"]:
            match(toks[i]):
                case "enum":
                    toks[i] = EnumToken("#ENUM", toks[i].filename, toks[i].line_number, [toks[i]])
                case "struct":
                    toks[i] = StructToken("#STRUCT", toks[i].filename, toks[i].line_number, [toks[i]])
                case "union":
                    toks[i] = UnionToken("#UNION", toks[i].filename, toks[i].line_number, [toks[i]])
                case default:
                    toks[i] = TypeToken("#TYPE", toks[i].filename, toks[i].line_number, [toks[i]])

            j = i + 1
            while j < n:
                if toks[j] in starters:
                    toks[i].value.append(toks[j])
                    del toks[j]
                    n -= 1
                else:
                    break
        i += 1
    
    return toks


def handle_pointer_types(toks:Tokens):
    """
    type tokens now consume * directly after it
    """
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] in ["#TYPE", "#ENUM", "#STRUCT", "#UNION"]:
            j = i + 1
            while j < n and toks[j] in ["*", "restrict"]:
                toks[i].value.append(toks[j])
                del toks[j]
                n -= 1
        i += 1
    return toks


def handle_array_types(toks:Tokens):
    # TODO
    """
    type tokens now consume array declarations
    after the identifier

    #TYPE (x) [10]
    =>
    #TYPE (*x)

    can only contain (, *, one identifier, and ) in the middle
    
    if xyz contains parenthesis, match
    """
    i = 0
    n = len(toks)

    pass


def get_possible_names(toks:Tokens):
    # There may be a name after #ENUM, #STRUCT, or #UNION
    # get it and set the name in the type token

    builtins = set([
            "#TYPE",
            "#ENUM",
            "#STRUCT",
            "#UNION",
            ";", "{", "}", "(", ")", "~", "!", "%", "^",
            "&", "*", "-", "+", "=", "[", "]", "|", "/",
            ">", "<", ",", ".", "?", ":", "++", "--",
            "return", "break", "if", "else", "for",
            "while", "switch", "case", "default", "sizeof",
            "continue", "static", "const", "goto", "do", "extern", "restrict"
        ])

    i = 0
    n = len(toks)
    while i < n:
        if toks[i] in ["#ENUM", "#STRUCT", "#UNION"]:
            if i + 1 < n and toks[i+1] not in builtins:
                toks[i].name = toks[i+1]
                del toks[i+1]
                n -= 1
        i += 1

    return toks


def convert_enums(toks:Tokens):
    """
    enum <optional name> {CONSTANT <optional = CONSTANT>, ..., CONSTANT <optional = CONSTANT>}
    """
    # get possible definition after
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] == "#ENUM":
            if i + 1 < n and toks[i+1] == "{":
                # this is a definition
                contents = toks.get_match_content(i+1, "}")
                if contents is None:
                    toks[i].fatal_error("Unmatched {")
                n = len(toks)

                toks[i].original_value = contents[:]

                # TODO: parse the contents
        i += 1

    return toks


def convert_structs_and_unions(toks:Tokens):
    # get possible definition after
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] in ["#STRUCT", "#UNION"]:
            if i + 1 < n and toks[i+1] == "{":
                # this is a definition
                contents = toks.get_match_content(i+1, "}")
                if contents is None:
                    toks[i].fatal_error("Unmatched {")
                n = len(toks)
                toks[i].original_value = contents[:]
        i += 1
    return toks


def get_definition(scopes, tok):
    for scope in reversed(scopes):
        if tok in scope:
            return scope[tok]
    return None

def handle_typedefs(toks:Tokens):
    i = 0
    n = len(toks)

    type_tokens = set([
        "#TYPE",
        "#ENUM",
        "#STRUCT",
        "#UNION",
        "#TYPEDEF",
        ])

    scopes = [{}]

    def is_defined(tok):
        for scope in scopes:
            if tok in scope:
                return True
        return False

    while i < n:
        if toks[i] == "{":
            scopes.append({})
        elif toks[i] == "}":
            if len(scopes) == 0:
                toks[i].fatal_error("Unmatched }")
            scopes.pop()
        elif toks[i] == "typedef":
            if i + 2 >= n:
                toks[i].fatal_error("Expected type definition")
            if toks[i+1] not in type_tokens and not is_defined(toks[i+1]):
                toks[i+1].fatal_error("Invalid type")
            
            if is_defined(toks[i+1]):
                toks[i] = TypedefToken("#TYPEDEF", toks[i].filename, toks[i].line_number, get_definition(scopes, toks[i+1]).original_value , toks[i+2])
            else:
                toks[i] = TypedefToken("#TYPEDEF", toks[i].filename, toks[i].line_number, toks[i+1], toks[i+2])

            if is_defined(toks[i+2]):
                toks[i+2].fatal_error("Multiple definitions of type")
            scopes[-1][toks[i+2]] = toks[i]

            del toks[i+1]
            del toks[i+1]
            n -= 2
        elif is_defined(toks[i]):
            # if it is a typedefed token, replace with the original definition
            for scope in scopes:
                if toks[i] in scope:
                    definition = scope[toks[i]]
                    break
            toks[i] = definition.original_value
        i += 1

    return toks


def handle_functions(toks:Tokens):
    type_tokens = set([
        "#TYPE",
        "#ENUM",
        "#STRUCT",
        "#UNION",
        ])
    builtins = set([
            "#TYPE",
            "#ENUM",
            "#STRUCT",
            "#UNION",
            "#TYPEDEF",
            ";", "{", "}", "(", ")", "~", "!", "%", "^",
            "&", "*", "-", "+", "=", "[", "]", "|", "/",
            "<", ",", ".", "?", ":", "++", "--",
            "return", "break", "if", "else", "for",
            "while", "switch", "case", "default", "sizeof",
            "continue", "static", "const", "goto", "do", "extern"
        ])

    i = 0
    n = len(toks)
    any_var = TOKEN_VARIABLE()
    while i < n:
        if any_var == toks[i]:
            if i + 1 < n and toks[i+1] == "(":
                # this is a function
                # get the args from ()
                # if { is after, this is a definition
                # get the content from {}
                args = toks.get_match_content(i+1, ")")
                n = len(toks)
                if args is None:
                    toks[i+1].fatal_error("Unmatched (")
                if i + 1 < n and toks[i+1] == "{":
                    # this is a definition
                    content = toks.get_match_content(i+1, "}")
                    content = Tokens(content)
                    n = len(toks)
                    if content is None:
                        toks[i+1].fatal_error("Unmatched {")
                    toks[i] = FuncToken("#FUNC", toks[i].token, toks[i].filename, toks[i].line_number, toks[i].original, toks[i].type, args, content)
                else:
                    # this is just a declaration
                    toks[i] = FuncToken("#FUNC", toks[i].token, toks[i].filename, toks[i].line_number, toks[i].original, toks[i].type, args, None)

        i += 1
    return toks


def handle_do_whiles(toks:Tokens):
    """
    Do-while loops:
        do { stuff } while (condition);
        =>
        {
            {
                stuff;
            }
            while (condition){
                stuff;
            }
        }
    """

    i = 0
    n = len(toks)
    while i < n:
        if toks[i] == "do":
            if i + 1 >= n or toks[i+1] != "{":
                toks[i].fatal_error("Expected { after do")

            content = toks.get_match_content(i + 1, "}")
            n = len(toks)
            if content is None:
                toks[i+1].fatal_error("Unclosed {")
            if i + 1 >= n or toks[i+1] != "while":
                toks[i].fatal_error("Expected while after do block")
            if i + 2 >= n or toks[i+2] != "(":
                toks[i+1].fatal_error("Expected ( after while")

            condition = toks.get_match_content(i+2, ")")
            if condition is None:
                toks[i+1].fatal_error("Unclosed (")
            n = len(toks)
            if i + 2 >= n or toks[i+2] != ";":
                toks[i+1].fatal_error("Expected ; after do-while loop")

            del toks[i]
            del toks[i]
            del toks[i]
            n -= 3

            result = ["{"] + content + ["while"] + condition + ["{"] + content[1:-1] + ["}", "}"]
            result = strings_to_tokens(result)
            toks.insert_all(i, result)
        i += 1

    return toks


def add_extra_scopes(toks:Tokens):
    """
    around every for loop, add an extra {}
    """
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] == "for":
            toks.insert(i, string_to_token("{"))
            n += 1 
            i += 2
            if i >= n:
                toks[i-1].fatal_error("Expected ( after for")
            end_condition = toks.get_match_end(i, ")")
            if end_condition is None or end_condition + 1 >= n:
                toks[i].fatal_error("Expected { after loop condition")
            end_loop = toks.get_match_end(end_condition+1, "}")
            toks.insert(end_loop, string_to_token("}"))
            n += 1


        i += 1
    return toks



def handle_generalization(toks:Tokens):

    type_tokens = set([
            "#TYPE",
            "#ENUM",
            "#STRUCT",
            "#UNION",
        ])

    builtins = set([
            "#TYPE",
            "#ENUM",
            "#STRUCT",
            "#UNION",
            "#TYPEDEF",
            ";", "{", "}", "(", ")", "~", "!", "%", "^",
            "&", "*", "-", "+", "=", "[", "]", "|", "/",
            ">", "<", ",", ".", "?", ":", "++", "--",
            "return", "break", "if", "else", "for",
            "while", "switch", "case", "default", "sizeof",
            "continue", "static", "const", "goto", "do", "extern", "restrict"
        ])

    scopes = [{}]
    functions = {}

    def is_defined(tok:Token):
        for scope in scopes:
            if tok in scope:
                return True
        return False
    
    i = 0
    n = len(toks)

    while i < n:
        if toks[i] == "{":
            scopes.append({})
        elif toks[i] == "}":
            if len(scopes) == 0:
                toks[i].fatal_error("Unmatched }")
            scopes.pop()
        elif toks[i] not in builtins and TOKEN_LITERAL() != toks[i] and TOKEN_VARIABLE() != toks[i]:
            """
            if this is a function, do not throw a redefinition error.
            pretend there is a new scope 
            """
            if (i + 1 < n and toks[i+1] == ":") or (i-1 > 0 and toks[i-1] == "goto"):
                i += 1
                continue

            if i > 0 and toks[i-1] in type_tokens and i + 1 < n and toks[i+1] == "(":
                # this is a function
                # handle the name
                toks[i] = VariableToken(f"#{toks.varnum}", toks[i].filename, toks[i].line_number, toks[i].token, the_type=toks[i-1])
                del toks[i-1]
                i -= 1
                n = len(toks)
                toks.varnum += 1

                # handle the args
                args = toks.get_match_content(i+1, ")")
                if args is None:
                    toks[i+1].fatal_error("Unmatched (")
                n = len(toks)
                j = 0
                m = len(args)
                this_scope = {}
                while j < m:
                    if args[j] not in builtins:
                        if args[j] in this_scope:
                            toks[i].fatal_error(f"Redefinition of {args[j]} in function header")
                        original = args[j].token
                        args[j] = VariableToken(f"#{toks.varnum}", toks[i].filename, toks[i].line_number, toks[i].token, the_type=toks[i-1])
                        this_scope[original] = args[j]
                        toks.varnum += 1
                    j += 1

                # replace occurances of these variables in the function
                if i + 1 < n and toks[i+1] == "{":
                    # there are contents of the function to replace
                    functions[toks[i].original] = toks[i]
                    func_end = toks.get_match_end(i+1, "}")
                    if func_end is None:
                        toks[i+1].fatal_error("Unmatched {")
                    j = i + 1
                    while j < func_end:
                        if toks[j] in this_scope:
                            toks[j] = this_scope[toks[j]]
                        j += 1
                toks.insert_all(i+1, args)
                n = len(toks)
                i += 1
                continue
            
            if is_defined(toks[i]) or toks[i] in functions:
                # if there is a type before, throw error
                if i > 0 and toks[i-1] == "#TYPE":
                    toks[i].fatal_error(f"Redefinition of {toks[i]}")
                # find the scope it was used in
                if toks[i] in functions:
                    toks[i] = functions[toks[i]]
                else:
                    for scope in scopes:
                        if toks[i] in scope:
                            toks[i] = scope[toks[i]]
                            break
            else:
                # if there is not a type before, throw error
                if i - 2 >= 0 and toks[i-1] == ">" and toks[i-2] == "-":
                    new_tok = VariableToken(f"#{toks.varnum}", toks[i].filename, toks[i].line_number, toks[i].token, the_type=toks[i-1])
                    toks[i] = new_tok

                    scopes[-1][toks[i].original] = toks[i]
                    toks.varnum += 1
                    i += 1
                    continue

                if i == 0 or (toks[i-1] not in type_tokens and toks[i-1] != "."):
                    #toks[i].fatal_error(f"Undefined identifier {toks[i]}")
                    toks[i].undefined = True
                # add it to the current scope
                the_type = None
                if toks[i-1] in ["#TYPE", "#STRUCT", "#UNION", "#ENUM"]:
                    the_type = toks[i-1]
                    del toks[i-1]
                    i -= 1
                    n -= 1

                new_tok = VariableToken(f"#{toks.varnum}", toks[i].filename, toks[i].line_number, toks[i].token, the_type=the_type)
                toks[i] = new_tok

                scopes[-1][toks[i].original] = toks[i]
                toks.varnum += 1


        i += 1


    return toks



def combine_structs_and_pointers(toks):
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] == "#STRUCT" or toks[i] == "#UNION":
            while i + 1 < n and toks[i+1] in ["*", "restrict"]:
                toks[i].value.append(toks[i+1])
                del toks[i+1]
                n -= 1
        i += 1

    return toks


def combine_array_types(toks):
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] in ["#STRUCT", "#ENUM", "#TYPE", "#UNION"]:
            if i + 3 < n and toks[i+1] == "[" and toks[i+3] == "]" and TOKEN_INTEGER() == toks[i+2]:
                toks[i].value.append(toks[i+1:i+4])
                del toks[i+1]
                del toks[i+1]
                del toks[i+1]
                n -= 3
                i -= 1
        i += 1

    return toks

