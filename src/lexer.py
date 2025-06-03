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
    file_name: Optional[str] = None

    def clone(self) -> Self:
        return Position(self.line, self.column, self.file_name)

    def __str__(self):
        return f"{self.file_name + ':' if self.file_name else ''}{self.line + 1}:{self.column + 1}"


@dataclass
class Token:
    start_position: Optional[Position]
    end_position: Position
    type: TokenType = TokenType.ID
    value: str = ""

    def __str__(self):
        return f"{self.start_position}: [{self.type}] {repr(self.value)} (ends: {self.end_position})"


class Lexer:
    def __init__(self, content: str, file_name: Optional[str] = None):
        self._content = content
        self._file_name = file_name
        self._position = Position(file_name=file_name)
        self._cursor = 0
        self._tokens_generated = []
        self._current_token_index = 0

    def next_token(self) -> Optional[Token]:
        # Generate tokens if not already generated
        if not self._tokens_generated:
            self._tokens_generated = list(self._generate_tokens())
        
        # Return next token if available
        if self._current_token_index < len(self._tokens_generated):
            token = deepcopy(self._tokens_generated[self._current_token_index])
            self._current_token_index += 1
            return token
        return None

    def peek_token(self) -> Optional[Token]:
        # Generate tokens if not already generated
        if not self._tokens_generated:
            self._tokens_generated = list(self._generate_tokens())
        
        # Return current token without advancing
        if self._current_token_index < len(self._tokens_generated):
            return deepcopy(self._tokens_generated[self._current_token_index])
        return None
        
    def _generate_tokens(self) -> Generator[Token, None, None]:
        position = Position(file_name=self._file_name)
        current = Token(start_position=position.clone(), end_position=Position())
        cursor = 0
        comment_type = None

        while cursor < len(self._content):
            next_char = self._content[cursor] if cursor < len(self._content) else ""

            # Start counting position only at the last whitespace
            if not next_char.isspace() and current.start_position is None:
                current.start_position = position.clone()

            if comment_type:
                if next_char == "\n" and comment_type == self._CommentType.SINGLE_LINE:
                    comment_type = None
                elif next_char == "*" and comment_type == self._CommentType.MULTI_LINE:
                    if cursor + 1 < len(self._content) and self._content[cursor + 1] == "/":
                        comment_type = None
                        cursor += 1
                        if next_char == "\n":
                            position.line += 1
                            position.column = 0
                        else:
                            position.column += 1
            elif next_char == "/":
                if cursor + 1 < len(self._content) and self._content[cursor + 1] in ["/", "*"]:
                    for token in self._yield_token_and_reset(current, position):
                        yield token
                        current = Token(start_position=None, end_position=Position())
                    comment_type = self._CommentType.SINGLE_LINE
                    if self._content[cursor + 1] == "*":
                        comment_type = self._CommentType.MULTI_LINE
                    cursor += 1
                    position.column += 1
                else:
                    for token in self._yield_symbol(current, position, next_char):
                        yield token
                        current = Token(start_position=None, end_position=Position())
            elif next_char == '"':
                type_before_yield = current.type
                for token in self._yield_token_and_reset(current, position):
                    yield token
                    current = Token(start_position=None, end_position=Position())
                if type_before_yield != TokenType.STRING:
                    current.type = TokenType.STRING
                    current.start_position = position.clone()
            elif next_char.isspace() and current.type != TokenType.STRING:
                for token in self._yield_token_and_reset(current, position):
                    yield token
                    current = Token(start_position=None, end_position=Position())
            elif next_char.isnumeric() and not current.value and current.type != TokenType.STRING:
                if current.type != TokenType.INTEGER:
                    current.type = TokenType.INTEGER
                    current.start_position = position.clone()
                current.value += next_char
            elif next_char == "." and current.type == TokenType.INTEGER:
                current.type = TokenType.FLOAT
                current.value += next_char
            elif next_char == "=" and current.type != TokenType.STRING:
                if cursor + 1 < len(self._content) and self._content[cursor + 1] == "=":
                    for token in self._yield_symbol(current, position, "==", TokenType.SYMBOL_EQUALS):
                        yield token
                        current = Token(start_position=None, end_position=Position())
                    cursor += 1
                    position.column += 1
                else:
                    for token in self._yield_symbol(current, position, next_char):
                        yield token
                        current = Token(start_position=None, end_position=Position())
            elif next_char in KNOWN_SYMBOLS and current.type != TokenType.STRING:
                for token in self._yield_symbol(current, position, next_char):
                    yield token
                    current = Token(start_position=None, end_position=Position())
            else:
                if current.start_position is None:
                    current.start_position = position.clone()
                current.value += next_char

            cursor += 1
            if next_char == "\n":
                position.line += 1
                position.column = 0
            else:
                position.column += 1

        if current.value:
            current.end_position = position.clone()
            yield deepcopy(current)

    def _yield_symbol(self, current: Token, position: Position, symbol: str, 
                     symbol_type: TokenType = TokenType.SYMBOL) -> Generator[Token, None, None]:
        # Yield any pending token
        for token in self._yield_token_and_reset(current, position):
            yield token
        
        # Create a new token for the symbol
        symbol_token = Token(
            start_position=position.clone(),
            end_position=Position(position.line, position.column + len(symbol), position.file_name),
            type=symbol_type,
            value=symbol
        )
        yield deepcopy(symbol_token)

    def _yield_token_and_reset(self, current: Token, position: Position) -> Generator[Token, None, None]:
        if current.value or current.type == TokenType.STRING:
            current.end_position = position.clone()
            yield deepcopy(current)

    class _CommentType(Enum):
        SINGLE_LINE = 1
        MULTI_LINE = 2
