
from debug import *
from tokens import *

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

DEFINITIONS = {}
CONDITIONS = []
DELETING = False

def preprocess(toks:Tokens):
    """
    iterate through the file and handle a directive at a time
    """
    dbg("Handling Directives...")
    toks = handle_directives(toks)

    dbg("Finshed Preprocessing!")
    dbg(toks)
    return toks


def handle_directives(toks:Tokens):
    i = 0
    n = len(toks)

    while i < n:
        if toks[i] == "#":
            directive = toks.splice_until(i, "#END_DIRECTIVE")
            directive = Tokens(directive)
            dbg(f"Found directive:")
            dbg(directive)
            handle_directive(directive)
            n = len(toks)
            i -= 1
        elif DELETING:
            del toks[i]
            i -= 1
            n -= 1
        i += 1

    return toks


def get_directive_type(directive):
    if len(directive) <= 1:
        directive[0].fatal_error("Expected content in directive")
    valid_types = set(["define", "undef", "include", "ifdef", "ifndef", "if", "else", "elif", "endif"])

    i = 1
    while i < len(directive):
        if directive[i] not in valid_types:
            if directive[i] != "#DEFINE_SPACE":
                directive[i].fatal_error("Invalid directive")
        else:
            return directive[i]
        i += 1


def handle_directive(directive):
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
                handle_include(directive)
        case "ifdef":
            handle_ifdef(directive)
        case "ifndef":
            handle_ifndef(directive)
        case "if":
            handle_if(directive)
        case "else":
            handle_else(directive)
        case "elif":
            handle_elif(directive)
        case "endif":
            handle_endif(directive)

def handle_define(directive):
    dbg("Handling define...")
    # TODO
    # figure out if a normal or function-like macro


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


def handle_include(directive):
    dbg("Handling include...")
    # TODO
    # figure out if it is a local or library include


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
    dbg(f"Checking condition:")
    dbg(condition)
    # TODO
    return True


def should_delete():
    global DELETING
    DELETING = False
    for x in CONDITIONS:
        if x == False:
            DELETING = True
    return DELETING

