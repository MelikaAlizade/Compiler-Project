# Elina Hozhabri - 401170661
# Melika Alizadeh - 401106255
input_text = ''
pos = 0
lineno = 1
tokens = []
errors = []
symbol_table = []
keywords = ['break', 'else', 'for', 'if', 'int', 'return', 'void']
symbols = [';', ':', ',', '[', ']',
           '(', ')', '{', '}', '+', '-', '*', '/', '=', '<', '==']


def initialize():
    global input_text, pos, lineno, tokens, errors, symbol_table
    pos = 0
    lineno = 1
    tokens = []
    errors = []
    symbol_table = []

    for keyword in keywords:
        symbol_table.append(keyword)

    try:
        with open('input.txt', 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        input_text = ''


def get_next_token():
    global lineno, errors

    skip_whitespace()

    if current_char() is None:
        return None

    if current_char() == '/' and lookahead_char() in ['/', '*']:
        read_comment()
        return get_next_token()

    token_line = lineno
    ch = current_char()

    if ch == '*' and lookahead_char() == '/':
        errors.append((token_line, '*/', 'Stray closing comment'))
        advance()
        advance()
        return get_next_token()

    if is_digit(ch):
        return read_number(token_line)

    if is_letter(ch):
        return read_identifier(token_line)

    if ch in ['(', ')', '[', ']', '{', '}', ';', ':', ',', '+', '-', '*', '/']:
        advance()
        return (token_line, 'SYMBOL', ch)

    if ch == '=':
        advance()
        if current_char() == '=':
            advance()
            return (token_line, 'SYMBOL', '==')
        return (token_line, 'SYMBOL', '=')

    if ch == '<':
        advance()
        return (token_line, 'SYMBOL', '<')

    errors.append((token_line, ch, 'Illegal character'))
    advance()
    return get_next_token()


def skip_whitespace():
    while current_char() and is_whitespace(current_char()):
        advance()


def is_whitespace(ch):
    return ch in [' ', '\n', '\r', '\t', '\v', '\f']


def current_char():
    global pos, input_text

    if pos < len(input_text):
        return input_text[pos]

    return None


def lookahead_char(offset=1):
    global pos, input_text

    if pos + offset < len(input_text):
        return input_text[pos + offset]
    return None


def advance():
    global pos, lineno, input_text

    if pos < len(input_text):
        if input_text[pos] == '\n':
            lineno += 1

        pos += 1


def read_comment():
    global lineno, pos, input_text, errors

    start_line = lineno

    if current_char() == '/' and lookahead_char() == '/':
        advance()  # skip first /
        advance()  # skip second /

        while current_char() and current_char() not in ['\n', '\f']:
            advance()

        if current_char() == '\f':
            advance()

        return True

    elif current_char() == '/' and lookahead_char() == '*':
        advance()  # skip /
        advance()  # skip *

        comment_start = pos - 2

        while True:
            if current_char() is None:
                unclosed_text = input_text[comment_start:min(
                    comment_start + 7, len(input_text))]
                if len(input_text) - comment_start > 7:
                    unclosed_text += '…'
                errors.append(
                    (start_line, unclosed_text, 'Open comment at EOF'))
                return True

            if current_char() == '*' and lookahead_char() == '/':
                advance()  # skip *
                advance()  # skip /
                return True

            advance()

    return False


def is_digit(ch):
    return ch and ch.isdigit()


def read_number(token_line):
    global pos, errors

    start_pos = pos
    num_str = ''

    while is_digit(current_char()):
        num_str += current_char()
        advance()

    if is_letter(current_char()):
        error_str = num_str
        while is_id_char(current_char()):
            error_str += current_char()
            advance()
        errors.append((token_line, error_str, 'Malformed number'))
        return get_next_token()

    if len(num_str) > 1 and num_str[0] == '0':
        errors.append((token_line, num_str, 'Malformed number'))
        return get_next_token()

    return (token_line, 'NUM', num_str)


def is_letter(ch):
    return ch and (ch.isalpha() or ch == '_')


def is_id_char(ch):
    return ch and (ch.isalnum() or ch == '_')


def read_identifier(token_line):
    global symbol_table, errors
    id_str = ''

    while is_id_char(current_char()):
        id_str += current_char()
        advance()

    if current_char() and not is_whitespace(current_char()) and \
       current_char() not in ['(', ')', '[', ']', '{', '}', ';', ':', ',', '+', '-', '*', '/', '=', '<'] and \
       not is_digit(current_char()) and not is_letter(current_char()):
        error_str = id_str + current_char()
        errors.append((token_line, error_str, 'Illegal character'))
        advance()
        return get_next_token()

    if id_str in keywords:
        return (token_line, 'KEYWORD', id_str)

    if id_str not in symbol_table:
        symbol_table.append(id_str)

    return (token_line, 'ID', id_str)


def scan():
    global tokens

    while True:
        token = get_next_token()
        if token is None:
            break
        tokens.append(token)

    write_tokens()
    write_symbol_table()
    write_errors()


def write_tokens():
    global tokens

    with open('tokens.txt', 'w', encoding='utf-8') as f:
        if not tokens:
            return

        current_line = 1
        line_tokens = []

        for token in tokens:
            token_line, token_type, token_value = token
            while current_line < token_line:
                if line_tokens:
                    f.write(f"{current_line}. {' '.join(line_tokens)}\n")
                    line_tokens = []
                current_line += 1

            line_tokens.append(f"({token_type}, {token_value})")

        if line_tokens:
            f.write(f"{current_line}. {' '.join(line_tokens)}\n")


def write_symbol_table():
    global symbol_table

    with open('symbol_table.txt', 'w', encoding='utf-8') as f:
        for i, symbol in enumerate(symbol_table, 1):
            f.write(f"{i}.\t{symbol}\n")


def write_errors():
    global errors

    with open('lexical_errors.txt', 'w', encoding='utf-8') as f:
        if not errors:
            f.write('No lexical errors found.\n')
        else:
            errors_by_line = {}
            for error_line, error_str, error_msg in errors:
                if error_line not in errors_by_line:
                    errors_by_line[error_line] = []
                errors_by_line[error_line].append((error_str, error_msg))

            for line in sorted(errors_by_line.keys()):
                error_list = errors_by_line[line]
                error_strings = [
                    f"({err_str}, {err_msg})" for err_str, err_msg in error_list]
                f.write(f"{line}.\t{' '.join(error_strings)}\n")


def main():
    initialize()
    scan()


if __name__ == '__main__':
    main()
