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
