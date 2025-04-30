from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Generator, Optional, Self

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
class Position:
    line: int = 0
    column: int = 0

    def clone(self) -> Self:
        return Position(self.line, self.column)

    def __str__(self):
        return f"{self.line}:{self.column}"


@dataclass
class Token:
    start_position: Optional[Position]
    end_position: Position
    type: TokenType = TokenType.ID
    value: str = ""

    def __str__(self):
        return f"{self.start_position}-{self.end_position}: [{self.type}] {repr(self.value)}"


class Lexer:
    _content: str
    _cursor: int = 0
    _tokens_iter: Generator[Optional[Token], None, None] = None

    _current: Token
    _position: Position

    def __init__(self, content: str):
        self._content = content
        self._tokens_iter = self._tokens()
        self._position = Position()

    def next_token(self) -> Optional[Token]:
        try:
            return deepcopy(next(self._tokens_iter))
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
        self._current = Token(start_position=self._position.clone(), end_position=Position())
        comment_type = None
        self._cursor = cursor

        while self._cursor < len(self._content):
            next_char = "" if self._cursor == len(self._content) else str(self._content[self._cursor])

            # Start counting position only at the last whitespace
            if not next_char.isspace() and self._current.start_position is None:
                self._current.start_position = self._position.clone()

            if comment_type:
                if next_char == "\n" and comment_type == self._CommentType.SINGLE_LINE:
                    comment_type = None
                if next_char == "*" and comment_type == self._CommentType.MULTI_LINE:
                    if self._cursor + 1 < len(self._content) and self._content[self._cursor + 1] == "/":
                        comment_type = None
                        self._advance(next_char)
            elif next_char == "/":
                if self._cursor + 1 < len(self._content) and self._content[self._cursor + 1] in ["/", "*"]:
                    yield from self._yield_token_and_reset()
                    comment_type = self._CommentType.SINGLE_LINE
                    if self._content[self._cursor + 1] == "*":
                        comment_type = self._CommentType.MULTI_LINE
                    self._advance(next_char)
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
                    yield from self._yield_symbol("==", TokenType.SYMBOL_EQUALS)
                    self._advance(next_char)
                else:
                    yield from self._yield_symbol(next_char)
            elif next_char in KNOWN_SYMBOLS and self._current.type != TokenType.STRING:
                yield from self._yield_symbol(next_char)
            else:
                self._current.value += next_char

            self._debug_step(comment_type, next_char, self._cursor)
            self._advance(next_char)

        if self._current.value:
            self._current.end_position = self._position.clone()
            yield self._current
        else:
            yield None

    def _advance(self, next_char: str):
        self._cursor += 1
        if next_char == "\n":
            self._position.line += 1
            self._position.column = 0
        else:
            self._position.column += 1


    def _yield_symbol(self, next_char: str, symbol_type: TokenType = TokenType.SYMBOL) -> Generator[Token, None, None]:
        # first provide the current token, as it just terminated
        yield from self._yield_token_and_reset()

        # next, provide the actual symbol
        self._current.type = symbol_type
        self._current.value = next_char
        self._current.start_position = self._position.clone()
        self._current.end_position = self._position.clone()
        self._current.end_position.column += len(next_char)

        yield from self._yield_token_and_reset(skip_end=True)

    def _yield_token_and_reset(self, skip_end: bool = False) -> Generator[Token, None, None]:
        if self._current.value or self._current.type == TokenType.STRING:
            if not skip_end:
                self._current.end_position = self._position.clone()

            yield self._current
            self._current.start_position = None
            self._current.value = ""
            self._current.type = TokenType.ID

    def _debug_step(self, comment_type, next_char, i):
        # noinspection PyUnreachableCode
        if False:
            print(f"[{i} - {self._position}] {repr(next_char)} -> {self._current} {' [comment]' if comment_type else ''}")

    class _CommentType(Enum):
        SINGLE_LINE = 1
        MULTI_LINE = 2
