class ParserError(Exception):
    """
    Exception raised when the parser encounters a syntax error.
    Carries a message including the position in the token stream.
    """
    pass

class Parser:
    """
    Recursive‐descent parser for a tiny imperative language.

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
        self.current_token = lexer.peek()

    def error(self, message):
        pos = self.current_token.position if self.current_token else -1
        raise ParserError(f"Parser error at position {pos}: {message}")

    def consume(self, token_type):
        if not self.current_token:
            self.error(f"Unexpected end of input, expected {token_type}.")
        if self.current_token.type == token_type:
            self.current_token = self.lexer.advance()
        else:
            self.error(f"Expected '{token_type}' but got '{self.current_token.type}'")

    def parse(self):
        self.parseProgram()
        if self.current_token.type != 'EOF':
            self.error("Extra token(s) after 'end_program'.")
        return True

    def parseProgram(self):
        if self.current_token.type != 'PROGRAM':
            self.error("Program must start with 'program' token.")
        self.consume('PROGRAM')
        self.parseStatements()
        self.consume('END_PROGRAM')

    def parseStatements(self):
        stop = {'END_PROGRAM', 'END_IF', 'END_LOOP', 'EOF'}
        while self.current_token.type not in stop:
            self.parseStatement()

    def parseStatement(self):
        t = self.current_token.type
        if t == 'IDENTIFIER':
            self.parseAssignment()
            self.consume('SEMICOLON')
        elif t == 'IF':
            self.parseIfStatement()
        elif t == 'LOOP':
            self.parseLoopStatement()
        else:
            self.error(f"Unexpected token in statement: {self.current_token.value}")

    def parseAssignment(self):
        self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        self.parseExpression()

    def parseExpression(self):
        self.parseTerm()
        while self.current_token.type in ('PLUS', 'MINUS'):
            self.consume(self.current_token.type)
            self.parseTerm()

    def parseTerm(self):
        self.parseFactor()
        while self.current_token.type in ('MUL', 'DIV', 'MOD'):
            self.consume(self.current_token.type)
            self.parseFactor()

    def parseFactor(self):
        if self.current_token.type == 'LPAREN':
            self.consume('LPAREN')
            self.parseExpression()
            self.consume('RPAREN')
        elif self.current_token.type in ('IDENTIFIER', 'NUMBER'):
            self.consume(self.current_token.type)
        else:
            self.error(f"Unexpected token in factor: {self.current_token.value}")
            
    def parseIfStatement(self):
        self.consume('IF')
        self.consume('LPAREN')
        self.parseLogicExpr()
        self.consume('RPAREN')
        self.parseStatements()
        self.consume('END_IF')

    def parseLoopStatement(self):
        self.consume('LOOP')
        self.consume('LPAREN')
        self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        if self.current_token.type in ('IDENTIFIER', 'NUMBER'):
            self.consume(self.current_token.type)
        else:
            self.error("Expected IDENTIFIER or NUMBER in loop range.")
        self.consume('COLON')
        if self.current_token.type in ('IDENTIFIER', 'NUMBER'):
            self.consume(self.current_token.type)
        else:
            self.error("Expected IDENTIFIER or NUMBER in loop range.")
        self.consume('RPAREN')
        self.parseStatements()
        self.consume('END_LOOP')
        
    def parseLogicExpr(self):
        self.parseComparison()
        while self.current_token.type in ('AND', 'OR'):
            self.consume(self.current_token.type)
            self.parseComparison()
            
    def parseComparison(self):
        if self.current_token.type in ('IDENTIFIER', 'NUMBER'):
            self.consume(self.current_token.type)
            if self.current_token.type in ('EQ', 'NEQ', 'GT', 'LT', 'GE', 'LE'):
                self.consume(self.current_token.type)
                if self.current_token.type in ('IDENTIFIER', 'NUMBER'):
                    self.consume(self.current_token.type)
                else:
                    self.error("Expected IDENTIFIER or NUMBER after comparison operator.")
            else:
                self.error("Expected comparison operator (==, !=, >, <, >=, <=).")
        else:
            self.error("Expected IDENTIFIER or NUMBER at the start of comparison.")