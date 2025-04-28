import re
import tkinter as tk
from tkinter import scrolledtext, messagebox

# #############################################################################
# 1) TOKEN DEFINITIONS
# ##############################################################################
TOKEN_SPECIFICATIONS = [
    (r'//.*',             'COMMENT'),       # Single-line comment
    (r'\bprogram\b',      'PROGRAM'),       # 'program'
    (r'\bend_program\b',  'END_PROGRAM'),   # 'end_program'
    (r'\bif\b',           'IF'),            # 'if'
    (r'\bend_if\b',       'END_IF'),        # 'end_if'
    (r'\bloop\b',         'LOOP'),          # 'loop'
    (r'\bend_loop\b',     'END_LOOP'),      # 'end_loop'
    (r'\b[0-9]+\b',       'NUMBER'),        # Number
    (r'\b[a-zA-Z]\w*\b',  'IDENTIFIER'),    # Alphanumeric identifier
    (r'==',               'EQ'),            # ==
    (r'!=',               'NEQ'),           # !=
    (r'>=',               'GE'),            # >=
    (r'<=',               'LE'),            # <=
    (r'>',                'GT'),            # >
    (r'<',                'LT'),            # <
    (r'\+',               'PLUS'),          # +
    (r'-',                'MINUS'),         # -
    (r'\*',               'MUL'),           # *
    (r'/',                'DIV'),           # /
    (r'%',                'MOD'),           # %
    (r'&&',               'AND'),           # &&
    (r'\|\|',             'OR'),            # ||
    (r'=',                'ASSIGN'),        # =
    (r'\(',               'LPAREN'),        # (
    (r'\)',               'RPAREN'),        # )
    (r':',                'COLON'),         # :
    (r';',                'SEMICOLON'),     # ;
    (r'\s+',              None),            # Whitespace (ignore)
]

class Token:
    """Simple token with type, value, and position."""
    def __init__(self, ttype, value, position):
        self.type = ttype
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type}, {self.value}, pos={self.position})"

# #############################################################################
# 2) LEXER
# #############################################################################
class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.position = 0
        self.create_tokens()

    def create_tokens(self):
        idx = 0
        while idx < len(self.text):
            match_found = False
            for pattern, token_type in TOKEN_SPECIFICATIONS:
                regex = re.compile(pattern)
                match = regex.match(self.text, idx)
                if match:
                    match_text = match.group(0)
                    if token_type and token_type != 'COMMENT':
                        self.tokens.append(Token(token_type, match_text, idx))
                    idx += len(match_text)
                    match_found = True
                    break

            if not match_found:
                raise ValueError(f"Illegal character at index {idx}: '{self.text[idx]}'")

        self.tokens.append(Token('EOF', 'EOF', idx))

    def peek(self):
        """Return the current token without consuming it."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def advance(self):
        """
        Move to the next token and return it.
        This fix ensures we actually consume the current token
        and advance to the subsequent token.
        """
        self.position += 1
        return self.peek()

# #############################################################################
# 3) RECURSIVE DESCENT PARSER
# #############################################################################

class ParserError(Exception):
    pass

class Parser:
    """
    Grammar:
    
    program       -> 'program' statements 'end_program'
    statements    -> { statement }
    statement     -> assignment ';' | if_statement | loop_statement
    assignment    -> IDENTIFIER '=' expression
    if_statement  -> 'if' '(' logic_expr ')' statements 'end_if'
    loop_statement-> 'loop' '(' IDENTIFIER '=' (IDENTIFIER|NUMBER) ':' (IDENTIFIER|NUMBER) ')' statements 'end_loop'
    
    logic_expr    -> comparison { ('&&' | '||') comparison }
    comparison    -> (IDENTIFIER|NUMBER) (==|!=|>|<|>=|<=) (IDENTIFIER|NUMBER)
    
    expression    -> term { ('+' | '-') term }
    term          -> factor { ('*' | '/' | '%') factor }
    factor        -> '(' expression ')' | IDENTIFIER | NUMBER
    """
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.peek()

    def error(self, message):
        pos = self.current_token.position if self.current_token else -1
        raise ParserError(f"Parser error at position {pos}: {message}")

    def consume(self, token_type):
        if self.current_token.type == token_type:
            # Consume the current token and move to the next
            self.current_token = self.lexer.advance()
        else:
            self.error(f"Expected token type '{token_type}' but got '{self.current_token.type}'")

    def parse(self):
        """
        Parse the entire source code as a single 'program'.
        """
        self.parseProgram()
        if self.current_token.type != 'EOF':
            self.error("Extra tokens after 'end_program'.")
        return True

    # program -> 'program' statements 'end_program'
    def parseProgram(self):
        if self.current_token.type == 'PROGRAM':
            self.consume('PROGRAM')
            self.parseStatements()
            if self.current_token.type == 'END_PROGRAM':
                self.consume('END_PROGRAM')
            else:
                self.error("Missing 'end_program' at the end.")
        else:
            self.error("Program must start with 'program'.")

    # statements -> { statement }
    def parseStatements(self):
        stop_tokens = {'END_PROGRAM', 'END_IF', 'END_LOOP', 'EOF'}
        while self.current_token.type not in stop_tokens:
            self.parseStatement()

    # statement -> assignment ';' | if_statement | loop_statement
    def parseStatement(self):
        ttype = self.current_token.type
        if ttype == 'IDENTIFIER':
            self.parseAssignment()
            self.consume('SEMICOLON')
        elif ttype == 'IF':
            self.parseIfStatement()
        elif ttype == 'LOOP':
            self.parseLoopStatement()
        else:
            self.error(f"Unexpected token in statement '{self.current_token.value}'")

    # assignment -> IDENTIFIER '=' expression
    def parseAssignment(self):
        self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        self.parseExpression()

    # if_statement -> 'if' '(' logic_expr ')' statements 'end_if'
    def parseIfStatement(self):
        self.consume('IF')
        self.consume('LPAREN')
        self.parseLogicExpr()
        self.consume('RPAREN')
        self.parseStatements()
        self.consume('END_IF')

    # loop_statement -> 'loop' '(' IDENTIFIER '=' (IDENTIFIER|NUMBER) ':' (IDENTIFIER|NUMBER) ')' statements 'end_loop'
    def parseLoopStatement(self):
        self.consume('LOOP')
        self.consume('LPAREN')
        self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        if self.current_token.type in ('IDENTIFIER', 'NUMBER'):
            self.consume(self.current_token.type)
        else:
            self.error("Expected IDENTIFIER or NUMBER in loop start value.")
        self.consume('COLON')
        if self.current_token.type in ('IDENTIFIER', 'NUMBER'):
            self.consume(self.current_token.type)
        else:
            self.error("Expected IDENTIFIER or NUMBER in loop end value.")
        self.consume('RPAREN')
        self.parseStatements()
        self.consume('END_LOOP')

    # logic_expr -> comparison { ('&&' | '||') comparison }
    def parseLogicExpr(self):
        self.parseComparison()
        while self.current_token.type in ('AND', 'OR'):
            self.consume(self.current_token.type)
            self.parseComparison()

    # comparison -> (IDENTIFIER|NUMBER) (==|!=|>|<|>=|<=) (IDENTIFIER|NUMBER)
    def parseComparison(self):
        if self.current_token.type not in ('IDENTIFIER','NUMBER'):
            self.error("Expected IDENTIFIER or NUMBER in comparison.")
        self.consume(self.current_token.type)

        if self.current_token.type not in ('EQ','NEQ','GT','LT','GE','LE'):
            self.error("Expected a comparison operator (==, !=, >, <, >=, <=).")
        self.consume(self.current_token.type)

        if self.current_token.type not in ('IDENTIFIER','NUMBER'):
            self.error("Expected IDENTIFIER or NUMBER in comparison.")
        self.consume(self.current_token.type)

    # expression -> term { ('+' | '-') term }
    def parseExpression(self):
        self.parseTerm()
        while self.current_token.type in ('PLUS','MINUS'):
            self.consume(self.current_token.type)
            self.parseTerm()

    # term -> factor { ('*'|'/'|'%') factor }
    def parseTerm(self):
        self.parseFactor()
        while self.current_token.type in ('MUL','DIV','MOD'):
            self.consume(self.current_token.type)
            self.parseFactor()

    # factor -> '(' expression ')' | IDENTIFIER | NUMBER
    def parseFactor(self):
        ttype = self.current_token.type
        if ttype == 'LPAREN':
            self.consume('LPAREN')
            self.parseExpression()
            self.consume('RPAREN')
        elif ttype in ('IDENTIFIER', 'NUMBER'):
            self.consume(ttype)
        else:
            self.error("Expected '(', IDENTIFIER, or NUMBER in factor.")

# #############################################################################
# 4) TKINTER GUI
# #############################################################################
class ParserGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Recursive Descent Parser")

        # Text area
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=60, height=15)
        self.text_area.pack(padx=10, pady=10)

        # Buttons
        button_frame = tk.Frame(master)
        button_frame.pack()

        parse_button = tk.Button(button_frame, text="Parse", command=self.on_parse)
        parse_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(button_frame, text="Clear", command=self.on_clear)
        clear_button.pack(side=tk.LEFT, padx=5)

    def on_parse(self):
        source_code = self.text_area.get("1.0", tk.END)
        try:
            lexer = Lexer(source_code)
            parser = Parser(lexer)
            parser.parse()
            messagebox.showinfo("Result", "Parsing succeeded! No errors.")
        except (ParserError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def on_clear(self):
        self.text_area.delete("1.0", tk.END)

# #############################################################################
# 5) MAIN
# #############################################################################
if __name__ == "__main__":
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()
