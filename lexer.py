import re
from grammar import TOKEN_SPECIFICATIONS, Token

class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.position = 0
        self._create_tokens()

    def _create_tokens(self):
        idx = 0
        while idx < len(self.text):
            for pattern, token_type in TOKEN_SPECIFICATIONS:
                match = re.compile(pattern).match(self.text, idx)
                if not match:
                    continue
                lexeme = match.group(0)
                if token_type and token_type != 'COMMENT':  # Ignore comments
                    self.tokens.append(Token(token_type, lexeme, idx))
                idx += len(lexeme)
                break
            else:
                raise ValueError(f"Illegal character at {idx}: '{self.text[idx]}'")
        self.tokens.append(Token('EOF', 'EOF', idx))

    def peek(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def advance(self):
        self.position += 1
        return self.peek()
