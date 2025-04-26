import unittest

from lexer import Lexer, TokenType


class TestLexer(unittest.TestCase):
    def _expect_token(self, lexer: Lexer, t_type: TokenType, value: str):
        token = lexer.next_token()
        self.assertEqual(t_type, token.type)
        self.assertEqual(value, token.value)

    def test_lexer_with_no_content_returns_no_token(self):
        lexer = Lexer("")

        self.assertIsNone(lexer.next_token())
        self.assertIsNone(lexer.next_token())
        self.assertIsNone(lexer.next_token())

    def test_lexer_loads_unquoted_word_as_id_token(self):
        lexer = Lexer("someWord")
        self._expect_token(lexer, TokenType.ID, "someWord")
        self.assertIsNone(lexer.next_token())

    def test_lexer_loads_multiple_unquoted_words_as_id_tokens(self):
        lexer = Lexer("token1 token2 token3")

        self._expect_token(lexer, TokenType.ID, "token1")
        self._expect_token(lexer, TokenType.ID, "token2")
        self._expect_token(lexer, TokenType.ID, "token3")

    def test_lexer_loads_tokens_across_multiple_lines(self):
        lexer = Lexer("token1\ntoken2\ntoken3")

        self._expect_token(lexer, TokenType.ID, "token1")
        self._expect_token(lexer, TokenType.ID, "token2")
        self._expect_token(lexer, TokenType.ID, "token3")

    def test_lexer_handles_multiple_spaces(self):
        lexer = Lexer("token1   token2")

        self._expect_token(lexer, TokenType.ID, "token1")
        self._expect_token(lexer, TokenType.ID, "token2")

    def test_lexer_can_identify_empty_string_literal(self):
        lexer = Lexer('""')

        self._expect_token(lexer, TokenType.STRING, "")

    def test_lexer_can_identify_string_literal_followed_by_id(self):
        lexer = Lexer('"some string" someWord')

        self._expect_token(lexer, TokenType.STRING, "some string")
        self._expect_token(lexer, TokenType.ID, "someWord")

    def test_lexer_can_identify_integer_followed_by_id(self):
        lexer = Lexer("123 someWord")

        self._expect_token(lexer, TokenType.INTEGER, "123")
        self._expect_token(lexer, TokenType.ID, "someWord")

    def test_lexer_can_identify_float_followed_by_id(self):
        lexer = Lexer("123.45 someWord")

        self._expect_token(lexer, TokenType.FLOAT, "123.45")
        self._expect_token(lexer, TokenType.ID, "someWord")

    def test_lexer_can_identify_special_symbol(self):
        lexer = Lexer('([ someWord "some string ()"')

        self._expect_token(lexer, TokenType.SYMBOL, "(")
        self._expect_token(lexer, TokenType.SYMBOL, "[")
        self._expect_token(lexer, TokenType.ID, "someWord")
        self._expect_token(lexer, TokenType.STRING, "some string ()")

    def test_lexer_identifies_all_listed_special_symbols(self):
        from lexer import KNOWN_SYMBOLS

        lexer = Lexer("".join(KNOWN_SYMBOLS))

        for symbol in KNOWN_SYMBOLS:
            self._expect_token(lexer, TokenType.SYMBOL, symbol)

    def test_lexer_distinguishes_between_equal_and_assignment(self):
        lexer = Lexer("== =")

        self._expect_token(lexer, TokenType.SYMBOL_EQUALS, "==")
        self._expect_token(lexer, TokenType.SYMBOL, "=")

