
import re

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
