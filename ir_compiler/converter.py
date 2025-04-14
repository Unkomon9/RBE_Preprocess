
from debug import *
from tokens import *

def convert(toks:Tokens):
    # break operations from return
    toks = break_operations_from_returns(toks)

    # break operations from function calls
    toks = break_operations_from_function_calls(toks)

    # TODO: handle switch/case
    toks = handle_switch_case(toks)

    # convert else if(){} into else { if(){} }
    toks = handle_else_if(toks)

    # break operations from if
    toks = break_operations_from_ifs(toks)

    # convert labels
    toks = convert_labels(toks)
    
    # convert breaks, continues, and loops
    toks = convert_breaks_continues_and_loops(toks)

    # TODO: handle array literals
    # TODO: handle compound literals

    dbg("Finished Conversion!")
    dbg(toks)

    return toks


def break_operations_from_returns(toks:Tokens):
    """
    return x+y;
    =>
    z = x+y;
    return z;
    """

    for tok in toks:
        if tok != "#FUNC":
            continue

        func = tok.value
        if func is None:
            continue

        return_type = tok.return_type

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "return":
                if i + 1 >= n:
                    func[i].fatal_error("Expected ; after return")

                # get stuff from after return to ;
                return_content = func.splice_until(i+1, ";")
                n = len(func)

                # create new variable and insert 
                # #newvar = content; 
                # before return
                new_variable = VariableToken(f"#{toks.varnum}", func[i].filename, func[i].line_number, "ret_brk", return_type)
                insertion = [new_variable, "="] + return_content
                insertion = strings_to_tokens(insertion)
                func.insert_all(i, insertion)
                i += len(insertion)
                n = len(func)

                # insert
                # #newvar;
                # after return
                after_insertion = [new_variable, ";"]
                after_insertion = strings_to_tokens(after_insertion)
                func.insert_all(i+1, after_insertion)
                n = len(func)

                toks.varnum += 1
            i += 1

    return toks


def break_operations_from_function_calls(toks:Tokens):
    # store the variables of functions as we go
    # pull the values out of the function call

    functions = {}

    for tok in toks:
        if tok != "#FUNC":
            continue

        functions[tok.name_value] = tok
        func = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            # look for a function call
            # variable followed by (
            if TOKEN_VARIABLE() == func[i]:
                if i + 1 < n and func[i+1] == "(":
                    dbg(func[i])
                    content = func.get_match_content(i+1, ")")
                    if content is None:
                        func[i+1].fatal_error("Unmatched (")

                    func[i].token = f"{func[i].token}H"

                    content = Tokens(content[1:-1])
                    n = len(func)
                    # split the content at ,
                    splitted = content.split_at(",")

                    final_args = []
                    j = func.get_line_start(i)
                    k = i + 1
                    for x in splitted:
                        if len(x) == 0:
                            func[i].fatal_error("Empty argument found")
                        new_var = f"#{toks.varnum}"
                        prepare = strings_to_tokens([new_var, "="]) + x.tokens + strings_to_tokens([";"])
                        func.insert_all(j, prepare)
                        n = len(func)
                        j += len(prepare)
                        k += len(prepare)

                        # TODO: give new_var the correct type

                        final_args.append(string_to_token(new_var))
                        toks.varnum += 1

                    dbg("final args")
                    dbg(final_args)
                    l = 1
                    while l < len(final_args):
                        final_args.insert(l, ",")
                        l += 2
                    replacement_args = strings_to_tokens(["("] + final_args + [")"])
                    func.insert_all(k, replacement_args)
                    n = len(func)
            elif func[i][-1:] == "H" and TOKEN_VARIABLE() == func[i][:-1]:
                func[i].token = func[i][:-1]

            i += 1

    return toks



def handle_else_if(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func: Tokens = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "else" and i + 1 < n and func[i+1] == "if":
                func.insert(i+1, string_to_token("{"))
                n = len(func)

                j = i + 3
                if j >= n or func[j] != "(":
                    func[i+2].fatal_error("Expected ( after if")

                end = func.get_match_end(j, ")")
                if end is None:
                    func[j].fatal_error("Unmatched (")

                if end + 1 >= n or func[end+1] != "{":
                    func[end].fatal_error("Expected { after condition")

                end2 = func.get_match_end(end+1, "}")
                if end2 is None:
                    func[end+1].fatal_error("Unmatched {")


                while end2 + 1 < n and func[end2+1] == "else":
                    if end2 + 3 < n and func[end2 + 2] == "if":
                        if func[end2 + 3] != "(":
                            func[end2+3].fatal_error("Expected ( after if")
                        end3 = func.get_match_end(end2+3, ")")
                        if end3 is None:
                            func[end2+3].fatal_error("Unmatched (")
                        if end3 + 1 >= n or func[end3+1] != "{":
                            func[end2+3].fatal_error("Expected { after condition")
                        end4 = func.get_match_end(end3+1, "}")
                        if end4 is None:
                            func[end3+1].fatal_error("Unmatched {")
                        end2 = end4
                    elif end2 + 2 < n and func[end2 + 2] == "{":
                        end3 = func.get_match_end(end2+2, "}")
                        if end3 is None:
                            func[end2+2].fatal_error("Unmatched {")
                        end2 = end3
                    else:
                        func[end2+1].fatal_error("Expected { after else")

                func.insert(end2, string_to_token("}"))

                n = len(func)

            i += 1

    return toks



def break_operations_from_ifs(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            if func[i] == "if":
                if i + 1 >= n or func[i+1] != "(":
                    func[i].fatal_error("Expected ( after if")
                content = func.get_match_content(i+1, ")")
                if content is None:
                    func[i+1].fatal_error("Unmatched (")

                the_variable = VariableToken(f"#{toks.varnum}", func[i].filename, func[i].line_number, "inner_if", TypeToken("#TYPE", func[i].filename, func[i].line_number, [Token("int", "", 0)]))
                insertion = strings_to_tokens([the_variable, "="] + content[1:-1] + [";"])
                insertion2 = strings_to_tokens(["(", the_variable, ")"])
                func.insert_all(i+1, insertion2)
                func.insert_all(i, insertion)

                i += len(insertion)

                n = len(func)
                
                toks.varnum += 1


            i += 1

    return toks



def handle_switch_case(toks:Tokens):
    """
    """
    return toks



def convert_labels(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func = tok.value

        if func is None:
            continue

        labels = {}

        i = 0
        n = len(func)
        while i < n:
            if func[i] == ":":
                if i <= 0:
                    func[i].fatal_error("Expected identifier before :")
                new_var = VariableToken(f"@{toks.label_num}", func[i].filename, func[i].line_number, func[i-1].token, None)
                labels[new_var.original] = new_var

                func[i-1] = new_var

                toks.label_num += 1
            i += 1

        i = 0
        while i < n:
            if func[i] == "goto":
                if i + 1 >= n or func[i+1] not in labels:
                    func[i].fatal_error("Expected label after goto")
                func[i+1] = labels[func[i+1]]
            i += 1

    return toks



def convert_breaks_continues_and_loops(toks:Tokens):
    for tok in toks:
        if tok != "#FUNC":
            continue

        func = tok.value

        if func is None:
            continue

        i = 0
        n = len(func)
        while i < n:
            # find for or while loop
            if func[i] in ["for", "while"]:
                if i + 1 >= n or func[i+1] != "(":
                    func[i].fatal_error(f"Expected ( after {func[i]}")
                condition = func.get_match_content(i+1, ")")
                n = len(func)
                if i + 1 >= n or func[i+1] != "{":
                    func[i].fatal_error("Expected { after condition")
                end = func.get_match_end(i+1, "}")

                # create label before and after
                before_label = VariableToken(f"@{toks.label_num}", func[i].filename, func[i].line_number, func[i-1].token, None)
                toks.label_num += 1
                after_label = VariableToken(f"@{toks.label_num}", func[i].filename, func[i].line_number, func[i-1].token, None)
                toks.label_num += 1

                func.insert(i, before_label)
                i += 1
                func.insert(i, string_to_token(":"))
                i += 1
                n += 2
                end += 2
                func.insert(end+1, string_to_token(":"))
                func.insert(end+1, after_label)
                n += 2

                # get the initializer, condition, and increment
                initializer = None
                increment = None
                if func[i] == "for":
                    splitted = Tokens(condition[1:-1]).split_at(";")
                    if len(splitted) != 3:
                        func[i].fatal_error("Expected 3 sections in for loop")
                    initializer = Tokens(splitted[0])
                    condition = Tokens(strings_to_tokens(["("] + splitted[1].tokens + [")"]))
                    increment = Tokens(splitted[2])

                    initializer.append(Token(";", "", 0))
                    increment.append(Token(";", "", 0))
                else:
                    condition = Tokens(condition)


                j = i+1
                while j < end:
                    if func[j] in ["while", "for"]:
                        # skip j to end of loop
                        if j + 1 >= end or func[j+1] != "(":
                            func[j].fatal_error(f"Expected ( after {func[j]}")
                        inner_condition = func.get_match_end(j+1, ")")
                        if inner_condition is None:
                            func[j].fatal_error("Unmatched (")

                        if inner_condition + 1 >= end or func[inner_condition+1] != "{":
                            func[inner_condition].fatal_error("Expected { after condition")
                        loop_end = func.get_match_end(inner_condition+1, "}")
                        if loop_end is None:
                            func[inner_condition].fatal_error("Unmatched {")
                        j = loop_end
                    elif func[j] == "continue":
                        # convert continues to go back to start (and increment in for loops)
                        if func[i] == "for":
                            # add the increment first
                            func.insert_all(j, increment)
                            j += len(increment)
                            end += len(increment)
                        func[j].token = "goto"
                        func.insert(j+1, before_label)
                        end += 1
                    elif func[j] == "break":
                        # convert breaks to go to end
                        func[j].token = "goto"
                        func.insert(j+1, after_label)
                        end += 1
                    
                    j += 1
                n = len(func)

                if func[i] == "for":
                    # place the incrementer at the end
                    func.insert_all(end, increment)
                    end += len(increment)
                    n = len(func)
                    # place the initializer before the label
                    func.insert_all(i-2, initializer)
                    end += len(initializer)
                    i += len(initializer)
                    n = len(func)
                # place the jump back to the start at the end
                func.insert_all(end, strings_to_tokens(["goto", before_label, ";"]))
                # place the condition inside the if statement
                func[i] = "if"
                func.insert_all(i+1, condition)
                n = len(func)

            i += 1

    return toks




