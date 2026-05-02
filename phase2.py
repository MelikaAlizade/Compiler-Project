# Elina Hozhabri - 401170661
# Melika Alizadeh - 401106255
from anytree import Node, RenderTree, ContStyle

# ==================== SCANNER CODE ====================

input_text = ''
pos = 0
target_pos = 1
lineno = 1
tokens = []
errors = []
symbol_table = []
keywords = ['break', 'else', 'for', 'if', 'int', 'return', 'void', 'while']
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
        return ('$', '$')

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
        return ('SYMBOL', ch)

    if ch == '=':
        advance()
        if current_char() == '=':
            advance()
            return ('SYMBOL', '==')
        return ('SYMBOL', '=')

    if ch == '<':
        advance()
        return ('SYMBOL', '<')

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
    global lineno, pos, input_text, errors, target_pos

    start_line = lineno
    target_pos += 1
    start_pos = pos

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
                    unclosed_text += 'â€¦'
                errors.append(
                    (start_line, unclosed_text, 'Open comment at EOF'))
                return True

            if current_char() == '*' and lookahead_char() == '/':
                advance()  # skip *
                advance()  # skip /
                return True

            advance()


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

    return ('NUM', num_str)


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

    ch = current_char()
    is_symbol_or_whitespace = ch is None or is_whitespace(ch) or ch in symbols

    if ch and not is_id_char(ch) and not is_symbol_or_whitespace:

        if not id_str:
            error_str = ''

        else:
            error_str = id_str

        while current_char() and not is_whitespace(current_char()) and current_char() not in symbols:
            error_str += current_char()
            advance()

        errors.append((token_line, error_str, 'Illegal character'))
        return get_next_token()

    if id_str in keywords:
        return ('KEYWORD', id_str)

    if id_str not in symbol_table:
        symbol_table.append(id_str)

    return ('ID', id_str)


def line_number():
    global lineno
    return lineno


def scan():
    global tokens
    while True:
        token = get_next_token()
        if token == ('$', '$'):
            break
        tokens.append((lineno, token[0], token[1]))


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
                    f.write(f"{current_line}.\t{' '.join(line_tokens)} \n")
                    line_tokens = []
                current_line += 1

            line_tokens.append(f"({token_type}, {token_value})")

        if line_tokens:
            f.write(f"{current_line}.\t{' '.join(line_tokens)} \n")


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


# ==================== PARSER CODE ====================
grammar_rules = {
    "Program": [["Declaration-list"]],
    "Declaration-list": [["Declaration", "Declaration-list"], ["EPSILON"]],
    "Declaration": [["Declaration-initial", "Declaration-prime"]],
    "Declaration-initial": [["Type-specifier", "ID"]],
    "Declaration-prime": [["Fun-declaration-prime"], ["Var-declaration-prime"]],
    "Var-declaration-prime": [[";"], ["[", "NUM", "]", ";"]],
    "Fun-declaration-prime": [["(", "Params", ")", "Compound-stmt"]],
    "Type-specifier": [["int"], ["void"]],
    "Params": [["int", "ID", "Param-prime", "Param-list"], ["void"]],
    "Param-list": [[",", "Param", "Param-list"], ["EPSILON"]],
    "Param": [["Declaration-initial", "Param-prime"]],
    "Param-prime": [["[", "]"], ["EPSILON"]],
    "Compound-stmt": [["{", "Declaration-list", "Statement-list", "}"]],
    "Statement-list": [["Statement", "Statement-list"], ["EPSILON"]],
    "Statement": [["Expression-stmt"], ["Compound-stmt"], ["Selection-stmt"], ["Iteration-stmt"], ["Return-stmt"]],
    "Expression-stmt": [["Expression", ";"], ["break", ";"], [";"]],
    "Selection-stmt": [["if", "(", "Expression", ")", "Statement", "Else-stmt"]],
    "Else-stmt": [["else", "Statement"], ["EPSILON"]],
    "Iteration-stmt": [["for", "(", "Expression", ";", "Expression", ";", "Expression", ")", "Compound-stmt"]],
    "Return-stmt": [["return", "Return-stmt-prime"]],
    "Return-stmt-prime": [[";"], ["Expression", ";"]],
    "Expression": [["Simple-expression-zegond"], ["ID", "B"]],
    "B": [["=", "Expression"], ["[", "Expression", "]", "H"], ["Simple-expression-prime"]],
    "H": [["=", "Expression"], ["G", "D", "C"]],
    "Simple-expression-zegond": [["Additive-expression-zegond", "C"]],
    "Simple-expression-prime": [["Additive-expression-prime", "C"]],
    "C": [["Relop", "Additive-expression"], ["EPSILON"]],
    "Relop": [["<"], ["=="]],
    "Additive-expression": [["Term", "D"]],
    "Additive-expression-prime": [["Term-prime", "D"]],
    "Additive-expression-zegond": [["Term-zegond", "D"]],
    "D": [["Addop", "Term", "D"], ["EPSILON"]],
    "Addop": [["+"], ["-"]],
    "Term": [["Signed-factor", "G"]],
    "Term-prime": [["Factor-prime", "G"]],
    "Term-zegond": [["Signed-factor-zegond", "G"]],
    "G": [["*", "Signed-factor", "G"], ["/", "Signed-factor", "G"], ["EPSILON"]],
    "Signed-factor": [["+", "Factor"], ["-", "Factor"], ["Factor"]],
    "Signed-factor-zegond": [["+", "Factor"], ["-", "Factor"], ["Factor-zegond"]],
    "Factor": [["(", "Expression", ")"], ["ID", "Var-call-prime"], ["NUM"]],
    "Var-call-prime": [["(", "Args", ")"], ["Var-prime"]],
    "Var-prime": [["[", "Expression", "]"], ["EPSILON"]],
    "Factor-prime": [["(", "Args", ")"], ["EPSILON"]],
    "Factor-zegond": [["(", "Expression", ")"], ["NUM"]],
    "Args": [["Arg-list"], ["EPSILON"]],
    "Arg-list": [["Expression", "Arg-list-prime"]],
    "Arg-list-prime": [[",", "Expression", "Arg-list-prime"], ["EPSILON"]]
}


class Parser:
    SYNC_ADD_EPSILON = "ADD_EPSILON"
    SYNC_NON_TERMINAL = "NON_TERMINAL"
    SYNC_LAST_TOKEN = "TOKEN"
    SYNC_REMAIN = "REMAIN"

    def __init__(self):
        self.current_token = None
        self.production_functions = {}
        self.syntax_errors = []
        self.parse_tree = []
        self.tree_depth = 0
        self.FIRST, self.FOLLOW = self.find_first_follow()
        for non_terminal in grammar_rules:
            self.production_functions[non_terminal] = self.create_transition_diagram(
                non_terminal)
            setattr(self, non_terminal,
                    self.production_functions[non_terminal])

    def find_first_follow(self):
        FIRST = {nt: set() for nt in grammar_rules}
        FOLLOW = {nt: set() for nt in grammar_rules}
        terminals = set()

        def is_non_terminal(symbol):
            return symbol in grammar_rules

        def get_first_of_sequence(sequence):
            first_set = set()

            for symbol in sequence:
                if symbol == "EPSILON":
                    first_set.add("EPSILON")
                    break
                elif not is_non_terminal(symbol):
                    first_set.add(symbol)
                    break
                else:
                    first_set.update(FIRST[symbol] - {"EPSILON"})
                    if "EPSILON" not in FIRST[symbol]:
                        break
            else:
                first_set.add("EPSILON")

            return first_set

        def get_first_sets():
            changed = True

            while changed:
                changed = False

                for non_terminal, productions in grammar_rules.items():
                    for production in productions:
                        current_first = FIRST[non_terminal]
                        production_first = get_first_of_sequence(production)

                        new_items = production_first - current_first
                        if new_items:
                            FIRST[non_terminal].update(new_items)
                            changed = True

                        for symbol in production:
                            if symbol not in grammar_rules and symbol != "EPSILON":
                                terminals.add(symbol)

        def get_follow_sets(start_symbol="Program"):
            FOLLOW[start_symbol].add('$')
            changed = True

            while changed:
                changed = False

                for non_terminal, productions in grammar_rules.items():
                    for production in productions:
                        follow_accumulator = set(FOLLOW[non_terminal])

                        for i in range(len(production) - 1, -1, -1):
                            symbol = production[i]

                            if not is_non_terminal(symbol):
                                follow_accumulator = {symbol}
                                continue

                            before_size = len(FOLLOW[symbol])
                            FOLLOW[symbol].update(follow_accumulator)

                            if len(FOLLOW[symbol]) > before_size:
                                changed = True

                            if "EPSILON" in FIRST[symbol]:
                                follow_accumulator.update(
                                    FIRST[symbol] - {"EPSILON"})
                            else:
                                follow_accumulator = set(FIRST[symbol])

        get_first_sets()
        get_follow_sets()
        return FIRST, FOLLOW

    def parse(self):
        initialize()
        self.current_token = get_next_token()
        self.Program()

        _, token_value = self.current_token
        if token_value != "$":
            self.add_syntax_error(
                line_number(),
                "illegal",
                token_value
            )

            while token_value != "$":
                self.current_token = get_next_token()
                _, token_value = self.current_token

        self.write_tree()
        self.write_errors()

    def create_transition_diagram(self, non_terminal):
        def transition_diagram():
            self.add_node(non_terminal)
            self.tree_depth += 1

            sync_status = self.synchronize(non_terminal)

            if sync_status == self.SYNC_NON_TERMINAL:
                self.tree_depth -= 1
                return

            while sync_status == self.SYNC_LAST_TOKEN:
                self.current_token = get_next_token()
                sync_status = self.synchronize(non_terminal)

            production = self.select_production(non_terminal, force_epsilon=(
                sync_status == self.SYNC_ADD_EPSILON))
            if not production:
                self.tree_depth -= 1
                return

            if production == ["EPSILON"]:
                self.parse_tree.append("\t" * self.tree_depth + "epsilon")
            else:
                for symbol in production:
                    if symbol in grammar_rules:
                        self.production_functions[symbol]()
                    else:
                        self.match_terminal(symbol)

            self.tree_depth -= 1
            if non_terminal == "Program":
                self.parse_tree.append("\t" * (self.tree_depth + 1) + "$")

        return transition_diagram

    def synchronize(self, non_terminal):
        token_type, token_value = self.current_token

        if token_type == "$" and "$" not in self.FOLLOW[non_terminal]:
            self.handle_eof()

        in_first = (token_type in self.FIRST[non_terminal]
                    or token_value in self.FIRST[non_terminal])
        can_epsilon = ("EPSILON" in self.FIRST[non_terminal] and (
            token_type in self.FOLLOW[non_terminal] or token_value in self.FOLLOW[non_terminal]))
        in_follow = (
            token_type in self.FOLLOW[non_terminal] or token_value in self.FOLLOW[non_terminal])

        if in_first:
            return self.SYNC_REMAIN
        if can_epsilon:
            return self.SYNC_ADD_EPSILON
        if not in_follow:
            self.report_illegal(token_type, token_value)
            return self.SYNC_LAST_TOKEN
        self.report_missing(non_terminal)
        return self.SYNC_NON_TERMINAL

    def select_production(self, non_terminal, force_epsilon=False):
        token_type, token_value = self.current_token
        for production in grammar_rules[non_terminal]:
            first_set = self.get_first_of_production(production)
            if (token_type in first_set) or (token_value in first_set):
                return production
            if "EPSILON" in first_set and force_epsilon:
                return production
        return None

    def get_first_of_production(self, production):
        result = set()
        for symbol in production:
            if symbol == "EPSILON":
                result.add("EPSILON")
                break
            if symbol in grammar_rules:
                result.update(self.FIRST[symbol])
                if "EPSILON" not in self.FIRST[symbol]:
                    break
            else:
                result.add(symbol)
                break
        return result

    def match_terminal(self, symbol):
        if symbol in symbols:
            self.match_token("SYMBOL", symbol)
        elif symbol in keywords:
            self.match_token("KEYWORD", symbol)
        elif symbol == "ID":
            self.match_token("ID")
        elif symbol == "NUM":
            self.match_token("NUM")

    def match_token(self, expected_type, expected_value=None):
        token_type, token_value = self.current_token
        if token_type == expected_type and (expected_value is None or token_value == expected_value):
            self.add_node(f"({token_type}, {token_value})")
            self.current_token = get_next_token()
        else:
            missing = expected_value if expected_value else expected_type
            self.add_syntax_error(
                line_number(),
                "missing",
                missing
            )

    def add_node(self, node):
        self.parse_tree.append("\t" * self.tree_depth + node)

    def add_syntax_error(self, line_number, error_message, symbol):
        self.syntax_errors.append(
            f"#{line_number} : syntax error, {error_message} {symbol}")

    def report_illegal(self, token_type, token_value):
        illegal = token_type if token_type in {"NUM", "ID"} else token_value
        self.add_syntax_error(
            line_number(),
            "illegal",
            illegal
        )

    def report_missing(self, non_terminal):
        self.add_syntax_error(
            line_number(),
            "missing",
            non_terminal
        )
        self.parse_tree.pop()

    def handle_eof(self):
        self.add_syntax_error(
            line_number(),
            "Unexpected",
            "EOF"
        )
        self.parse_tree.pop()
        self.write_tree()
        self.write_errors()
        exit()

    def write_tree(self):
        with open("parse_tree.txt", "w", encoding="utf-8") as f:
            for line in self.parse_tree:
                f.write(line + "\n")
        self.build_and_print_tree("parse_tree.txt")

    def write_errors(self):
        with open("syntax_errors.txt", "w", encoding="utf-8") as f:
            if not self.syntax_errors:
                f.write("No syntax errors found.\n")
            else:
                for error in self.syntax_errors:
                    f.write(error + "\n")

    def build_tree(self, file_path):
        nodes_stack = []
        root_node = None

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                stripped_line = line.rstrip('\n')
                if not stripped_line.strip():
                    continue

                indentation = len(stripped_line) - \
                    len(stripped_line.lstrip('\t'))
                node_label = stripped_line.lstrip('\t')
                new_node = Node(node_label)

                if indentation == 0:
                    root_node = new_node
                    nodes_stack = [new_node]
                else:
                    if indentation <= len(nodes_stack):
                        nodes_stack = nodes_stack[:indentation]

                    if nodes_stack:
                        new_node.parent = nodes_stack[-1]

                    nodes_stack.append(new_node)

        return root_node

    def print_tree(self, root, output_file="parse_tree.txt"):
        rendered_lines = []
        for prefix, _, node in RenderTree(root, style=ContStyle()):
            line = f"{prefix}{node.name}"
            if line.endswith(')'):
                line += ' '
            rendered_lines.append(line)

        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(rendered_lines) + '\n')

    def build_and_print_tree(self, input_file, output_file="parse_tree.txt"):
        root = self.build_tree(input_file)
        if root:
            self.print_tree(root, output_file)
        return root


def main():
    initialize()
    parser = Parser()
    parser.parse()


if __name__ == '__main__':
    main()
