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
    type: TokenType = TokenType.ID
    value: str = ""


class Lexer:
    _content: str
    _cursor: int = 0
    _tokens_iter: Generator[Optional[Token], None, None] = None

    _current: Token = Token()
    _cursor: int = 0

    def __init__(self, content: str):
        self._content = content
        self._tokens_iter = self._tokens()

    def next_token(self) -> Optional[Token]:
        try:
            return next(self._tokens_iter)
        except StopIteration:
            return None

    def peek_token(self) -> Optional[Token]:
        try:
            current_cursor = self._cursor
            token = next(self._tokens(self._cursor))
            self._cursor = current_cursor

            return token
        except StopIteration:
            return None

    def _tokens(self, cursor: int = 0) -> Generator[Optional[Token], None, None]:
        self._current = Token()
        comment_type = None
        self._cursor = cursor

        while self._cursor < len(self._content):
            next_char = "" if self._cursor == len(self._content) else str(self._content[self._cursor])

            if comment_type:
                if next_char == "\n" and comment_type == self._CommentType.SINGLE_LINE:
                    comment_type = None
                if next_char == "*" and comment_type == self._CommentType.MULTI_LINE:
                    if self._cursor + 1 < len(self._content) and self._content[self._cursor + 1] == "/":
                        comment_type = None
                        self._cursor += 1
            elif next_char == "/":
                if self._cursor + 1 < len(self._content) and self._content[self._cursor + 1] in ["/", "*"]:
                    yield from self._yield_token_and_reset()
                    comment_type = self._CommentType.SINGLE_LINE
                    if self._content[self._cursor + 1] == "*":
                        comment_type = self._CommentType.MULTI_LINE
                    self._cursor += 1
                else:
                    yield from self._yield_symbol(next_char)
            elif next_char == '"':
                type_before_yield = self._current.type
                yield from self._yield_token_and_reset()
                if type_before_yield != TokenType.STRING:
                    self._current.type = TokenType.STRING
            elif next_char.isspace() and self._current.type != TokenType.STRING:
                yield from self._yield_token_and_reset()
            elif next_char.isnumeric() and not self._current.value and self._current.type != TokenType.STRING:
                if self._current.type != TokenType.INTEGER:
                    self._current.type = TokenType.INTEGER
                self._current.value += next_char
            elif next_char == "." and self._current.type == TokenType.INTEGER:
                self._current.type = TokenType.FLOAT
                self._current.value += next_char
            elif next_char == "=" and self._current.type != TokenType.STRING:
                if self._cursor + 1 < len(self._content) and self._content[self._cursor + 1] == "=":
                    self._cursor += 1
                    yield from self._yield_symbol("==", TokenType.SYMBOL_EQUALS)
                else:
                    yield from self._yield_symbol(next_char)
            elif next_char in KNOWN_SYMBOLS and self._current.type != TokenType.STRING:
                yield from self._yield_symbol(next_char)
            else:
                self._current.value += next_char

            self._debug_step(comment_type, next_char, self._cursor)
            self._cursor += 1

        if self._current.value:
            yield self._current
        else:
            yield None

    def _yield_symbol(self, next_char: str, symbol_type: TokenType = TokenType.SYMBOL) -> Generator[Token, None, None]:
        # first provide the current token, as it just terminated
        yield from self._yield_token_and_reset()
        # next, provide the actual symbol
        yield Token(type=symbol_type, value=next_char)

    def _yield_token_and_reset(self) -> Generator[Token, None, None]:
        if self._current.value or self._current.type == TokenType.STRING:
            yield self._current
            self._current.value = ""
            self._current.type = TokenType.ID

    def _debug_step(self, comment_type, next_char, i):
        # noinspection PyUnreachableCode
        if False:
            print(f"[{i}] {repr(next_char)} -> {repr(self._current.value)} {repr(self._current.type)} {' [comment]' if comment_type else ''}")

    class _CommentType(Enum):
        SINGLE_LINE = 1
        MULTI_LINE = 2
