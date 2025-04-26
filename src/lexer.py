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

    _token_value: str = ""
    _token_type: TokenType = TokenType.ID

    def __init__(self, content: str):
        self._content = content

    def _tokens(self) -> Generator[Optional[Token], None, None]:
        self._token_value = ""
        self._token_type = TokenType.ID
        i = 0

        while i < len(self._content):
            next_char = "" if i == len(self._content) else str(self._content[i])

            if next_char == '"':
                if self._token_type != TokenType.STRING:
                    self._token_type = TokenType.STRING
                else:
                    yield from self._yield_token_and_reset()
            elif next_char.isspace() and self._token_type != TokenType.STRING:
                if self._token_value:
                    yield from self._yield_token_and_reset()
            elif next_char.isnumeric() and not self._token_value:
                if self._token_type != TokenType.INTEGER:
                    self._token_type = TokenType.INTEGER
                self._token_value += next_char
            elif next_char == "." and self._token_type == TokenType.INTEGER:
                self._token_type = TokenType.FLOAT
                self._token_value += next_char
            elif next_char in KNOWN_SYMBOLS and self._token_type != TokenType.STRING:
                # first provide the current token, as it just terminated
                if self._token_value:
                    yield from self._yield_token_and_reset()

                # next, provide the actual symbol
                yield Token(type=TokenType.SYMBOL, value=next_char)
            else:
                self._token_value += next_char
            i += 1

        if self._token_value:
            yield Token(type=self._token_type, value=self._token_value)
        else:
            yield None

    def _yield_token_and_reset(self):
        yield Token(type=self._token_type, value=self._token_value)
        self._token_value = ""
        self._token_type = TokenType.ID

    def next_token(self) -> Optional[Token]:
        if self._tokens_iter is None:
            self._tokens_iter = self._tokens()

        try:
            return next(self._tokens_iter)
        except StopIteration:
            return None
