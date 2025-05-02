
from debug import *
from tokens import *

def convert(toks:Tokens):
    """
    Valid Tokens:
        ;, {, }, (, ), ~, !, %, ^,
        &, *, -, +, =, [, ], |, /,
        >, <, ,, ., ?, :, ++, --,
        return, if, else
        sizeof,  goto
        #{varnum}, @{labelnum}

    """
    # combine multi-token operators
    toks = combine_multi_token_operators(toks)
    """
    Valid Tokens:
        ;, {, }, (, ), ~, !, %, ^,
        &, *, -, +, =, [, ], |, /,
        >, <, ,, ., ?, :, ++, --,
        >>, <<, >>=, <<=, ->, !=, ==, +=, /=, *=, %=, ^=, ~=, -=, &=, |=,
        &&=, ||=, <=, >=, &&, ||
        return, if, else
        sizeof,  goto
        #{varnum}, @{labelnum}

    """

    # convert assignment operators
    toks = convert_assignment_operators(toks)
    """
    Removed:
        >>=, <<=, +=, /=, *=, %=, ^=, ~=, -=, &=, |=,
        &&=, ||=

    Valid Tokens:
        ;, {, }, (, ), ~, !, %, ^,
        &, *, -, +, =, [, ], |, /,
        >, <, ,, ., ?, :, ++, --,
        >>, <<, ->, !=, ==,
        <=, >=, &&, ||
        return, if, else
        sizeof,  goto
        #{varnum}, @{labelnum}

    """

    print("after assignments:")
    print(toks)
    print()


    # convert type casts to use cast
    toks = convert_type_casts(toks)
    """
    Added:
        cast
    Valid Tokens:
        ;, {, }, (, ), ~, !, %, ^,
        &, *, -, +, =, [, ], |, /,
        >, <, ,, ., ?, :, ++, --,
        >>, <<, ->, !=, ==,
        <=, >=, &&, ||
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    print("after casts:")
    print(toks)
    print()

    # convert unary operators
    toks = convert_unary_operators(toks)
    """
    Added:
        un+, un-, ++>, <++, -->, <--, lognot, bitnot, ref deref
    Removed:
        ++, --, !, ~
    Valid Tokens:
        ;, {, }, (, ), %, ^,
        &, *, -, +, =, [, ], |, /, lognot, bitnot, ref, deref
        >, <, ,, ., ?, :, ++>, <++, -->, <--
        >>, <<, ->, !=, ==,
        <=, >=, &&, ||,
        un+, un-
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # convert calls and accesses to use "call" and "access"
    toks = convert_calls_and_accesses(toks)
    """
    Added:
        call, access
    Removed:
        [, ]
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :, ++>, <++, -->, <--
        >>, <<, ->, !=, ==,
        <=, >=, &&, ||,
        un+, un-
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """
    print("after calls")
    print(toks)
    print()

    # break operations into 1/line
    toks = break_operations(toks)
    """
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :, ++>, <++, -->, <--
        >>, <<, ->, !=, ==,
        <=, >=, &&, ||,
        un+, un-
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    print("after breaking")
    print(toks)
    print()

    # remove un+ and un-
    toks = remove_unary_operators(toks)
    """
    Removed:
        un+, un-
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :, ++>, <++, -->, <--
        >>, <<, ->, !=, ==,
        <=, >=, &&, ||,
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # TODO: handle unsequenced modifications of variables using prefix/postfix
    # convert ++>, <++, -->, <--
    toks = convert_prefix_and_postfix(toks)
    """
    Removed:
        ++>, <++, -->, <--
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :
        >>, <<, ->, !=, ==,
        <=, >=, &&, ||,
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # convert || to &&
    toks = convert_logical_or(toks)
    """
    Removed:
        ||
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :
        >>, <<, ->, !=, ==,
        <=, >=, &&,
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # TODO: ensure && only evaluates rest of line if first part is true
    # convert && to ifs
    toks = convert_logical_and(toks)
    """
    Removed:
        ||
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :
        >>, <<, ->, !=, ==,
        <=, >=,
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # make sure all if statements have an else clause
    toks = ensure_else(toks)

    # TODO: convert returns

    # remove ->
    toks = remove_arrow(toks)
    """
    Removed:
        ->
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :
        >>, <<, !=, ==,
        <=, >=,
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # remove <=, >=, and !=
    toks = remove_or_equal(toks)
    """
    Removed:
        <=, >=, !=
    Valid Tokens:
        ;, {, }, (, ), bitnot, lognot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :
        >>, <<, ==,
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # remove lognot
    toks = remove_lognot(toks)
    """
    Removed:
        lognot
    Valid Tokens:
        ;, {, }, (, ), bitnot, ref, deref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :
        >>, <<, ==,
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    # convert derefs to accesses
    toks = convert_derefs(toks)
    """
    Removed:
        deref
    Valid Tokens:
        ;, {, }, (, ), bitnot, ref, %, ^,
        &, *, -, +, =, |, /,
        >, <, ,, ., ?, :
        >>, <<, ==,
        access, call
        return, if, else, cast
        sizeof,  goto
        #{varnum}, @{labelnum}
    """

    dbg("Finished Operator Conversion!")
    dbg(toks)
    
    return toks


def combine_multi_token_operators(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        func.combine_all([">", ">", "="])
        func.combine_all(["<", "<", "="])
        func.combine_all([">", ">"])
        func.combine_all(["<", "<"])
        func.combine_all(["-", ">"])
        func.combine_all(["&", "&", "="])
        func.combine_all(["|", "|", "="])
        func.combine_all(["&", "&"])
        func.combine_all(["|", "|"])
        func.combine_all([">", "="])
        func.combine_all(["<", "="])
        func.combine_all(["!", "="])
        func.combine_all(["=", "="])
        func.combine_all(["+", "="])
        func.combine_all(["/", "="])
        func.combine_all(["*", "="])
        func.combine_all(["%", "="])
        func.combine_all(["^", "="])
        func.combine_all(["~", "="])
        func.combine_all(["-", "="])
        func.combine_all(["&", "="])
        func.combine_all(["|", "="])
    return toks


def convert_assignment_operators(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        # find one of the assignment operators
        operators = set([">>=", "<<=", "+=", "/=", "*=", "%=", "^=", "~=", "-=", "&=", "|=", "&&=", "||="])

        i = 0
        n = len(func)
        while i < n:
            if func[i] in operators:
                base = string_to_token(func[i].token[:-1])
                func[i].token = "="

                # get the stuff before the equal sign
                start_index = func.get_line_start(i)
                stuff_before = func[start_index:i]
                # insert the stuff before and, base, and ( after the =
                # find the next semicolon and put ) before it
                end = func.find_next(i, ";")
                if end is None:
                    func[i].fatal_error("Expected ; at end of statement")
                func.insert(end, string_to_token(")"))

                insertion = strings_to_tokens(stuff_before + [base] + ["("])
                func.insert_all(i+1, insertion)

                print("Assignment Operator:")
                print(insertion)

                n = len(func)
            i += 1

        
    return toks


def convert_type_casts(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        castable = set([
            "(", "{"
            ])

        i = 0
        n = len(func)
        while i < n:
            # ( #TYPE ) x
            # =>
            # #TYPE cast x
            if func[i] == "#TYPE":
                if i > 0 and func[i-1] == "(" and i + 1 < n and func[i+1] == ")" and (i + 2 < n and (func[i+2] in castable or TOKEN_VARIABLE() == func[i+2])):
                    del func[i-1]
                    i -= 1
                    n -= 1
                    func[i+1].token = "cast"

            i += 1
    return toks


def convert_unary_operators(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        operators = set([
                ";", "{", "}", "(", "~", "!", "%", "^",
                "&", "*", "-", "+", "=", "[", "|", "/",
                ">", "<", ",", ".", "?", ":",
                ">>", "<<", "->", "!=", "==",
                "<=", ">=", "&&", "||",
                "cast", "sizeof"
            ])

        replacements = {
                "!":"lognot",
                "~":"bitnot",
                "*":"deref",
                "&":"ref"
            }

        i = 0
        n = len(func)
        while i < n:
            # look for + or - with an operator before it
            if func[i] in ["+", "-"]:
                if i == 0 or (i > 0 and func[i-1] in operators):
                    func[i].token = f"un{func[i].token}"
                    func.insert(i, string_to_token("0"))
                    i += 1
                    n += 1
            elif func[i] in ["++", "--"]:
                if i > 0 and func[i-1] in operators:
                    func[i].token = f"{func[i].token}>"
                    func.insert(i, string_to_token("0"))
                    i += 1
                else:
                    func[i].token = f"<{func[i].token}"
                    func.insert(i+1, string_to_token("0"))
                n += 1
            elif func[i] in ["!", "~", "*", "&"]:
                if i == 0 or (i > 0 and func[i-1] in operators):
                    func[i].token = replacements[func[i]]
                    func.insert(i, string_to_token("0"))
                    i += 1
                    n += 1
            elif func[i] == "sizeof":
                func.insert(i, string_to_token("0"))
                i += 1
                n += 1
            i += 1
    return toks



def convert_calls_and_accesses(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            # x[y]
            # =>
            # x access (y)
            if func[i] == "[":
                # look for closer
                closer = func.get_match_end(i, "]")
                if closer is None:
                    func[i].fatal_error("Unmatched [")
                # replace both with ()
                func[i].token = "("
                func[closer].token = ")"
                # insert access before
                func.insert(i, string_to_token("access"))
                i += 1
                n += 1
            i += 1

        # put call between function name and args
        i = 0
        n = len(func)
        while i < n:
            if TOKEN_VARIABLE() == func[i] and i + 1 < n and func[i+1] == "(":
                end_call = func.get_match_end(i+1, ")")
                func[i] = FunctionCall(func[i:end_call+1])
                func.tokens = func.tokens[:i+1] + func[end_call+1:]
                func.insert(i+1, string_to_token(";"))
                n = len(func)
            i += 1

    return toks


def break_operations(toks):
    # operator:(precedence, associativity)
    operators = {
        "<++":(1, "left"),
        "<--":(1, "left"),
        "call":(1, "left"),
        "access":(1, "left"),
        ".":(1, "left"),
        "->":(1, "left"),

        "++>":(2, "right"),
        "-->":(2, "right"),
        "un+":(2, "right"),
        "un-":(2, "right"),
        "lognot":(2, "right"),
        "bitnot":(2, "right"),
        "cast":(2, "right"),
        "deref":(2, "right"),
        "ref":(2, "right"),
        "sizeof":(2, "right"),

        "*":(3, "left"),
        "/":(3, "left"),
        "%":(3, "left"),

        "+":(4, "left"),
        "-":(4, "left"),

        "<<":(5, "left"),
        ">>":(5, "left"),

        ">":(6, "left"),
        "<":(6, "left"),
        "<=":(6, "left"),
        ">=":(6, "left"),

        "==":(7, "left"),
        "!=":(7, "left"),

        "&":(8, "left"),

        "^":(9, "left"),

        "|":(10, "left"),

        "&&":(11, "left"),

        "||":(12, "left"),

        "=":(14, "right"),

        ",":(15, "left"),
        }

    breakers = set([
            "{", "}", ";"
        ])

    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        # look for a line to break (more than 1 (not =) operation)
        operations = 0
        while i < n:
            if func[i] in breakers or i == n - 1:
                if operations >= 2:
                    line_start = func.get_line_start(i-1)
                    the_line = func[line_start:i]
                    func.tokens = func.tokens[:line_start] + func.tokens[i:]
                    i -= len(the_line)
                    n = len(func)
                    new_line = break_line(toks, the_line, operators)
                    func.insert_all(i, new_line)
                    i += len(new_line)
                    del func[i]
                    n = len(func)
                operations = 0
            elif func[i] in operators and func[i] != "=":
                operations += 1
            
            i += 1

    return toks



def break_line(toks, line, operators):
    """
    break a single line using the precedences and associativity
    """

    # convert to postfix
    expression = []
    op_stack = []

    line = Tokens(line)

    for x in line:
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


    # break postfix expression to 1 operator per line
    result = Tokens([])
    post_stack = []
    for x in expression:
        if x not in operators:
            post_stack.append(x)
        else:
            if len(post_stack) < 2:
                print("Expression:")
                print(expression)
                print("Line:")
                print(line)
                x.fatal_error("Invalid operands")
            second = post_stack.pop()
            first = post_stack.pop()

            # TODO: INFER TYPE OF INTERMEDIATE RESULT HERE
            print(x)
            new_var = VariableToken(f"#{toks.varnum}", x.filename, x.line_number, "inter", TypeToken("", "", 0, []))

            addition = [new_var, string_to_token("="), first, x, second, string_to_token(";")]

            result.tokens += addition

            post_stack.append(new_var)

            toks.varnum += 1

    return result



def ensure_else(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            # look for if
            if func[i] == "if":
                # find end of condition
                if i + 1 >= n or func[i+1] != "(":
                    func[i].fatal_error("Expected ( after if")
                condition = func.get_match_end(i+1, ")")
                if condition is None:
                    func[i+1].fatal_error("Unmatched (")
                # find end of content
                if condition + 1 >= n or func[condition+1] != "{":
                    func[condition].fatal_error("Expected { after condition")
                content = func.get_match_end(condition+1, "}")
                if content is None:
                    func[condition+1].fatal_error("Unmatched {")
                if content + 1 >= n or func[content+1] != "else":
                    insertion = strings_to_tokens(["else", "{", "}"])
                    func.insert_all(content+1, insertion)
                    n = len(func)
            i += 1
    return toks



def remove_unary_operators(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        func.replace_all_single("un+", Token("+", "", 0))
        func.replace_all_single("un-", Token("-", "", 0))

    return toks



def convert_prefix_and_postfix(toks:Tokens):
    """
    x = y <++ 0
    =>
    x = y
    y = y + 1
    -------------
    x = 0 ++> y
    =>
    y = y + 1
    x = y
    """
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] in ["<++", "<--"]:
                if i == 0:
                    func[i].fatal_error("Expected variable before postfix operator")
                the_var = func[i-1]
                func[i].token = func[i].token[-1]

                del func[i+1]
                n -= 1

                insertion = strings_to_tokens([";", the_var, "=", the_var])
                func.insert_all(i, insertion)
                i += len(insertion)
                func.insert(i+1, string_to_token("1"))

            elif func[i] in ["++>", "-->"]:
                if i + 1 >= n:
                    func[i].fatal_error("Expected variable after prefix operator")
                the_var = func[i+1]
                op = func[i]
                op.token = op.token[0]
                i -= 1
                del func[i]
                del func[i]
                n -= 2
                start = func.get_line_start(i)
                insertion = [the_var, "=", the_var, op, "1", ";"]
                insertion = strings_to_tokens(insertion)
                dbg(insertion)
                func.insert_all(start, insertion)
                n = len(func)
                i += len(insertion)
            i += 1
    return toks



def convert_logical_or(toks:Tokens):
    """
    a || b
    =>
    0 lognot (0 lognot a && 0 lognot b)
    """
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "||":
                if i == 0 or i + 1 >= n:
                    func[i].fatal_error("Expected variable before and after ||")
                insertion1 = strings_to_tokens(["0", "lognot", "(", "0", "lognot"])
                insertion2 = strings_to_tokens(["0", "lognot"])
                func[i].token = "&&"
                func.insert(i+2, string_to_token(")"))
                func.insert_all(i+1, insertion2)
                func.insert_all(i-1, insertion1)
                i += len(insertion1)
                n = len(func)

            i += 1

    toks = break_operations(toks)

    return toks



def convert_logical_and(toks:Tokens):
    """
    x = a && b
    =>
    #{newvar} = 0;
    if (a){
        if (b){
            #{newvar} = 1;
        }
    }
    x = #{newvar}
    """
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "&&":
                new_var = VariableToken(f"#{toks.varnum}", "", 0, string_to_token(""), TypeToken(Token("#TYPE", "", 0), "", 0, [string_to_token("long")]))
                before = [new_var, "=", "0", ";", "if", "("]
                middle = [")", "{", "if", "("]
                after = [")", "{", new_var, "=", "1", ";", "}", "else", "{", "}", "}", "else", "{", "}"]
                toks.varnum += 1

                start = func.get_line_start(i)
                left = func[i-1]
                right = func[i+1]
                del func[i-1]
                del func[i-1]
                del func[i-1]
                i -= 1
                func.insert(i, new_var)
                insertion = before + [left] + middle + [right] + after

                func.insert_all(start, strings_to_tokens(insertion))
                i += len(insertion)

                n = len(func)
            i += 1
    return toks


def remove_arrow(toks:Tokens):
    """
    a->b
    =>
    (*a).b
    """
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "->":
                if i == 0 or i + 1 >= n:
                    func[i].fatal_error("Expected variables on both sides of ->")
                func[i].token = "."
                func.insert_all(i-1, strings_to_tokens(["(", "0", "deref"]))
                i += 3
                func.insert(i, string_to_token(")"))
                i += 1
                n = len(func)
            i += 1

    toks = break_operations(toks)

    return toks



def remove_or_equal(toks:Tokens):
    """
    a >= b
    =>
    !(a < b)

    a <= b
    =>
    !(a > b)

    a != b
    =>
    !(a == b)
    """
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] in [">=", "<="]:
                func.insert_all(i-1, strings_to_tokens(["0", "lognot", "("]))
                i += 3
                if func[i][0] == ">":
                    func[i].token = "<"
                else:
                    func[i].token = ">"
                func.insert(i+2, string_to_token(")"))
                n += 4

            elif func[i] == "!=":
                func.insert_all(i-1, strings_to_tokens(["0", "lognot", "("]))
                i += 3
                func[i].token = "=="
                func.insert(i+2, string_to_token(")"))
                n += 4

            i += 1

    toks = break_operations(toks)

    return toks


def convert_derefs(toks):
    """
    0 deref a
    =>
    a access 0
    """
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "deref":
                func[i].token = "access"
                temp = func[i+1]
                func[i+1] = func[i-1]
                func[i-1] = temp
            i += 1

    return toks



def remove_lognot(toks:Tokens):
    """
    x = 0 lognot a
    =>
    #{newvar} = 1
    if (a){
        #{newvar} = 0
    } else {}
    x = #{newvar}
    """
    for tok in toks:
        if tok != "#FUNC":
            continue

        func:Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "lognot":
                new_var = VariableToken(f"#{toks.varnum}", "", 0, string_to_token(""), TypeToken("#TYPE", "", 0, [Token("long", "", 0)]))
                original = func[i+1]
                insertion = [new_var, "=", "1", ";", "if", "(", original, ")", "{", new_var, "=", "0", ";", "}", "else", "{", "}"]

                del func[i-1]
                del func[i-1]
                del func[i-1]
                i -= 1
                func.insert(i, new_var)
                i -= 1

                start = func.get_line_start(i)
                func.insert_all(start, strings_to_tokens(insertion))

                toks.varnum += 1
                n = len(func)
            i += 1
    return toks

