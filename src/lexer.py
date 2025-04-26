from dataclasses import dataclass
from enum import Enum
from typing import Generator, Optional

KNOWN_SYMBOLS = ["(", ")", "{", "}", "[", "]", ",", ";", ":", ".", "=", "+", "-", "*", "/", "%",
                 ">", "<", "!", "&", "|", "^", "~"]


class TokenType(Enum):
    ID = "ID"
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    SYMBOL = "SYMBOL"


@dataclass
class Token:
    type: TokenType
    value: str = ""


class Lexer:
    _content: str
    _cursor: int = 0
    _tokens_iter: Generator[Optional[Token], None, None] = None

    def __init__(self, content: str):
        self._content = content

    def _tokens(self) -> Generator[Optional[Token], None, None]:
        t_value = ""
        t_type = TokenType.ID
        i = 0

        while i < len(self._content):
            next_char = "" if i == len(self._content) else str(self._content[i])

            if next_char == '"':
                if t_type != TokenType.STRING:
                    t_type = TokenType.STRING
                else:
                    yield Token(type=t_type, value=t_value)
                    t_value = ""
                    t_type = TokenType.ID
            elif next_char.isspace() and t_type != TokenType.STRING:
                if t_value:
                    yield Token(type=t_type, value=t_value)
                    t_value = ""
                    t_type = TokenType.ID
            elif next_char.isnumeric() and not t_value:
                if t_type != TokenType.INTEGER:
                    t_type = TokenType.INTEGER
                t_value += next_char
            elif next_char == "." and t_type == TokenType.INTEGER:
                t_type = TokenType.FLOAT
                t_value += next_char
            elif next_char in KNOWN_SYMBOLS and t_type != TokenType.STRING:
                # first provide the current token, as it just terminated
                if t_value:
                    yield Token(type=t_type, value=t_value)
                    t_value = ""
                    t_type = TokenType.ID

                # next, provide the actual symbol
                yield Token(type=TokenType.SYMBOL, value=next_char)
            else:
                t_value += next_char
            i += 1

        if t_value:
            yield Token(type=t_type, value=t_value)
        else:
            yield None

    def next_token(self) -> Optional[Token]:
        if self._tokens_iter is None:
            self._tokens_iter = self._tokens()

        try:
            return next(self._tokens_iter)
        except StopIteration:
            return None
