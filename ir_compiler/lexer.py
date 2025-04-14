
from debug import *
from tokens import *
import errors


def lex(file:str):
    """
    Convert a file into a Tokens object
    """
    dbg(f"Reading file: {file}")
    data = open_file(file)
    dbg("Tokenizing...")
    toks = tokenize(data, file)
    dbg("Combining Prefix and Postfix...")
    toks = combine_prefix_and_postfix(toks)
    dbg("Done lexing.")
    dbg(toks)
    return toks


def open_file(filename):
    try:
        with open(filename, 'r') as f:
            data = f.read()
    except:
        errors.ERROR_HANDLER.add_error(errors.Error(f"Unable to open file: {filename}", "", 0), fatal=True)

    return data


def tokenize(data:str, filename:str):
    break_chars = {"~", "!", "#", "%", "^", "&", "*", "(", ")", "-", "+", "=", "{", "}", "[", "]", "|", '\\', "'", '"', ';', ":", "/", "?", ".", ",", "<", ">", '\n', '\t', ' '}

    tokens = []
    line_number = 0
    current_token = ""

    i = 0
    n = len(data)
    while i < n:
        if data[i] in break_chars:
            # increase line number if needed
            if data[i] == "\n":
                line_number += 1

            # create broken token
            if len(current_token) > 0:
                new_token = Token(current_token, filename, line_number)
                tokens.append(new_token)

            # add the break char
            new_token = Token(data[i], filename, line_number)
            tokens.append(new_token)

            # reset the current token
            current_token = ""
        else:
            # add the current char since not broken
            current_token += data[i]

        i += 1

    # handle possible last token at end of file
    if len(current_token) > 0:
        new_token = Token(current_token, filename, line_number)
        tokens.append(new_token)

    # return the Tokens object
    result = Tokens(tokens)
    return result


def combine_prefix_and_postfix(toks:Tokens):
    toks.combine_all(["+", "+"])
    toks.combine_all(["-", "-"])
    return toks


