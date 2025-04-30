import unittest

from lexer import Lexer, TokenType


class TestLexer(unittest.TestCase):
    def _expect_token(self, lexer: Lexer, t_type: TokenType, value: str):
        token = lexer.next_token()
        # print(f"   ==> {repr(token.value)} [{token.type}]")

        self.assertEqual(value, token.value)
        self.assertEqual(t_type, token.type)

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
        lexer = Lexer('firstWord"some string" someWord')

        self._expect_token(lexer, TokenType.ID, "firstWord")
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

    def test_lexer_can_parse_numbers_in_special_situations(self):
        lexer = Lexer('first123.45.12.34 "123 45.67" second')

        self._expect_token(lexer, TokenType.ID, "first123")
        self._expect_token(lexer, TokenType.SYMBOL, ".")
        self._expect_token(lexer, TokenType.FLOAT, "45.12")
        self._expect_token(lexer, TokenType.SYMBOL, ".")
        self._expect_token(lexer, TokenType.INTEGER, "34")
        self._expect_token(lexer, TokenType.STRING, "123 45.67")
        self._expect_token(lexer, TokenType.ID, "second")

    def test_lexer_can_identify_special_symbol(self):
        lexer = Lexer('([ someWord "some string ()" another.word')

        self._expect_token(lexer, TokenType.SYMBOL, "(")
        self._expect_token(lexer, TokenType.SYMBOL, "[")
        self._expect_token(lexer, TokenType.ID, "someWord")
        self._expect_token(lexer, TokenType.STRING, "some string ()")
        self._expect_token(lexer, TokenType.ID, "another")
        self._expect_token(lexer, TokenType.SYMBOL, ".")
        self._expect_token(lexer, TokenType.ID, "word")

    def test_lexer_identifies_all_listed_special_symbols(self):
        from lexer import KNOWN_SYMBOLS

        lexer = Lexer("".join(KNOWN_SYMBOLS))

        for symbol in KNOWN_SYMBOLS:
            self._expect_token(lexer, TokenType.SYMBOL, symbol)

    def test_lexer_distinguishes_between_equal_and_assignment(self):
        lexer = Lexer("== =")

        self._expect_token(lexer, TokenType.SYMBOL_EQUALS, "==")
        self._expect_token(lexer, TokenType.SYMBOL, "=")

    def test_lexer_distinguishes_equal_and_assignment_without_spaces(self):
        lexer = Lexer("===")

        self._expect_token(lexer, TokenType.SYMBOL_EQUALS, "==")
        self._expect_token(lexer, TokenType.SYMBOL, "=")
        self.assertIsNone(lexer.next_token())

    def test_lexer_distinguishes_equal_and_assignment_separated_by_words(self):
        lexer = Lexer("first==second=third")

        self._expect_token(lexer, TokenType.ID, "first")
        self._expect_token(lexer, TokenType.SYMBOL_EQUALS, "==")
        self._expect_token(lexer, TokenType.ID, "second")
        self._expect_token(lexer, TokenType.SYMBOL, "=")
        self._expect_token(lexer, TokenType.ID, "third")

    def test_lexer_ignores_single_line_comments(self):
        lexer = Lexer("someWord // this is a comment\n anotherWord")

        self._expect_token(lexer, TokenType.ID, "someWord")
        self._expect_token(lexer, TokenType.ID, "anotherWord")
        self.assertIsNone(lexer.next_token())

    def test_lexer_ignores_multi_line_comments(self):
        lexer = Lexer("someWord/* this // (inline?) is \n\n a comment */anotherWord")

        self._expect_token(lexer, TokenType.ID, "someWord")
        self._expect_token(lexer, TokenType.ID, "anotherWord")
        self.assertIsNone(lexer.next_token())

        lexer = Lexer("someWord // this /* (inline?) is \n\n comment */")
        self._expect_token(lexer, TokenType.ID, "someWord")
        self._expect_token(lexer, TokenType.ID, "comment")
        self._expect_token(lexer, TokenType.SYMBOL, "*")
        self._expect_token(lexer, TokenType.SYMBOL, "/")
        self.assertIsNone(lexer.next_token())

    def test_token_is_deep_copied(self):
        lexer = Lexer("first second")

        first_token = lexer.next_token()
        second_token = lexer.next_token()

        self.assertEqual("first", first_token.value)
        self.assertEqual("second", second_token.value)



class TestLexerPeek(unittest.TestCase):
    def _expect_token(self, lexer: Lexer, t_type: TokenType, value: str):
        token = lexer.next_token()

        self.assertEqual(value, token.value)
        self.assertEqual(t_type, token.type)

    def _expect_token_peek(self, lexer: Lexer, t_type: TokenType, value: str):
        token = lexer.peek_token()

        self.assertEqual(value, token.value)
        self.assertEqual(t_type, token.type)

    def test_lexer_peek_does_not_consume_token(self):
        lexer = Lexer("firstWord secondWord thirdWord")
        self._expect_token_peek(lexer, TokenType.ID, "firstWord")
        self._expect_token(lexer, TokenType.ID, "firstWord")
        self._expect_token_peek(lexer, TokenType.ID, "secondWord")
        self._expect_token(lexer, TokenType.ID, "secondWord")
        self._expect_token_peek(lexer, TokenType.ID, "thirdWord")
        self._expect_token(lexer, TokenType.ID, "thirdWord")

        self.assertIsNone(lexer.peek_token())
        self.assertIsNone(lexer.next_token())

    def test_token_is_deep_copied(self):
        lexer = Lexer("first second")

        first_token = lexer.peek_token()
        lexer.next_token()
        second_token = lexer.peek_token()

        self.assertEqual("first", first_token.value)
        self.assertEqual("second", second_token.value)
