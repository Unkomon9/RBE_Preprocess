
from debug import *
from tokens import *

def normalize(toks:Tokens):
    # remove comments and multi-line comments not in strings
    dbg("Removing Comments from tokens...")
    toks = remove_comments(toks)

    # manage compiler directive syntax
    dbg("Managing the preprocessor directive syntax...")
    toks = manage_directive_syntax(toks)

    # combine strings into single tokens
    dbg("Combining Strings into single tokens...")
    toks = combine_strings(toks)

    # combine floats into single tokens
    dbg("Combining Floats into single tokens...")
    toks = combine_floats(toks)

    # remove whitespace
    dbg("Removing all whitespace...")
    toks = remove_whitespace(toks)

    # remove auto and register keywords
    dbg("Removing auto and register keywords...")
    toks = remove_auto_and_register(toks)

    dbg("Finished Normalization!")
    dbg(toks)

    return toks


def remove_comments(toks:Tokens):

    comment = False
    multi_line = False
    quotes = False
    char_quote = False

    backslashes = 0

    i = 0
    n = len(toks)
    while i < n:
            # handle if this is the end of a multi-line comment
        if comment and multi_line:
            if toks[i] == "*" and i + 1 < n and toks[i+1] == "/":
                comment = False
                multi_line = False
                del toks[i]
                del toks[i]
                n -= 2
                continue

        if toks[i] == "/":
            # handle if this is the start of either type of comment
            if i + 1 < n:
                if not comment and not quotes:
                    if toks[i+1] == "/":
                        comment = True
                        multi_line = False
                    elif toks[i+1] == '*':
                        comment = True
                        multi_line = True

        elif toks[i] == '"':
            if not quotes and not char_quote:
                quotes = True
            elif quotes and not char_quote:
                if backslashes % 2 == 0:
                    quotes = False
        elif toks[i] == "'":
            if not quotes and not char_quote:
                char_quote = True
            elif not quotes and char_quote:
                if backslashes % 2 == 0:
                    char_quote = False
        elif toks[i] == '\n':
            # end a single-line comment if needed
            if comment and not multi_line and backslashes % 2 == 0:
                comment = False
            elif (quotes or char_quote) and i:
                # throw error if reaching end of string
                if backslashes % 2 == 0:
                    toks[i].fatal_error("Unmatched '\"'.")
                else:
                    # act as if newline wasn't there if escaped
                    del toks[i]
                    i -= 1
                    del toks[i]
                    n -= 2
                    continue

        # keep count of backslashes
        if toks[i] == "\\":
            backslashes += 1
        else:
            backslashes = 0

        # remove this token if in a comment
        if comment:
            del toks[i]
            n -= 1
            continue

        i += 1
    
    return toks


def manage_directive_syntax(toks:Tokens):
    # throw errors for reserved tokens
    toks.error_all("#END_DIRECTIVE", "Token is not valid", fatal=True)
    toks.error_all("#DEFINE_SPACE", "Token is not valid", fatal=True)


    i = 0
    n = len(toks)
    while i < n:
        if toks[i] == "#":
            backslashes = 0
            while i < n:
                if toks[i] == " ":
                    toks[i].token = "#DEFINE_SPACE"
                elif toks[i] == "\n":
                    if backslashes % 2 == 0:
                        toks[i].token = "#END_DIRECTIVE"
                        break
                    else:
                        del toks[i]
                        i -= 1
                        del toks[i]
                        n -= 2
                        backslashes = 0
                        continue

                if toks[i] == "\\":
                    backslashes += 1
                else:
                    backslashes = 0

                i += 1

        i += 1

    # Consolidate adjacent define spaces
    toks.replace_all(["#DEFINE_SPACE", "#DEFINE_SPACE"], ["#DEFINE_SPACE"])
    

    return toks



def combine_strings(toks:Tokens):
    i = 0
    n = len(toks)

    quotes = False
    char_quote = False
    backslashes = 0

    while i < n:
        if toks[i] == "'":
            if i + 2 >= n:
                toks[i].fatal_error("Expected character after '''")
            if toks[i+1] == "\\":
                if i + 3 >= n:
                    toks[i].fatal_error("Expected character after '''")
                toks.combine(i)
                n -= 1

            toks.combine(i)
            n -= 1
            if toks[i+1] != "'":
                toks[i+1].fatal_error("Expected closing '''")

            toks.combine(i)
            n -= 1
        elif toks[i] == '"':
            while i + 1 < n:
                if toks[i+1] == '"':
                    if backslashes % 2 == 0:
                        toks.combine(i)
                        n -= 1
                        break
                elif toks[i+1] == "\\":
                    backslashes += 1
                else:
                    backslashes = 0

                toks.combine(i)
                n -= 1
        i += 1

    return toks


def combine_floats(toks:Tokens):
    # floats should be in the form INT.INT
    toks.combine_all([TOKEN_INTEGER(), ".", TOKEN_INTEGER()])
    return toks


def remove_whitespace(toks:Tokens):
    toks.remove_all(" ")
    toks.remove_all("\t")
    toks.remove_all("\n")
    return toks


def remove_auto_and_register(toks:Tokens):
    toks.remove_all("auto")
    toks.remove_all("register")
    return toks

