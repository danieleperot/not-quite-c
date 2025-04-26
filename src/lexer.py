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
    SYMBOL_EQUALS = "SYMBOL_EQUALS"


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
        comment_type = None
        i = 0

        while i < len(self._content):
            next_char = "" if i == len(self._content) else str(self._content[i])

            if comment_type:
                if next_char == "\n" and comment_type == self._CommentType.SINGLE_LINE:
                    comment_type = None
                if next_char == "*" and comment_type == self._CommentType.MULTI_LINE:
                    if i + 1 < len(self._content) and self._content[i + 1] == "/":
                        comment_type = None
                        i += 1
            elif next_char == "/":
                if i + 1 < len(self._content) and self._content[i + 1] in ["/", "*"]:
                    if self._token_value:
                        yield from self._yield_token_and_reset()

                    comment_type = self._CommentType.SINGLE_LINE
                    if self._content[i + 1] == "*":
                        comment_type = self._CommentType.MULTI_LINE
                    i += 1
                else:
                    yield from self._yield_symbol(next_char)
            elif next_char == '"':
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
            elif next_char == "=" and self._token_type != TokenType.STRING:
                if i + 1 < len(self._content) and self._content[i + 1] == "=":
                    i += 1
                    yield Token(type=TokenType.SYMBOL_EQUALS, value="==")
                else:
                    yield Token(type=TokenType.SYMBOL, value=next_char)
            elif next_char in KNOWN_SYMBOLS and self._token_type != TokenType.STRING:
                yield from self._yield_symbol(next_char)
            else:
                self._token_value += next_char
            i += 1

        if self._token_value:
            yield Token(type=self._token_type, value=self._token_value)
        else:
            yield None

    def _yield_symbol(self, next_char: str) -> Generator[Token, None, None]:
        # first provide the current token, as it just terminated
        if self._token_value:
            yield from self._yield_token_and_reset()
        # next, provide the actual symbol
        yield Token(type=TokenType.SYMBOL, value=next_char)

    def _yield_token_and_reset(self) -> Generator[Token, None, None]:
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

    class _CommentType(Enum):
        SINGLE_LINE = 1
        MULTI_LINE = 2
