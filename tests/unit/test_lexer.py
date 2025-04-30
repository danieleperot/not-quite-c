import unittest

from lexer import Lexer, TokenType, Position


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


class TestTokenPosition(unittest.TestCase):
    def test_position_has_file_name_if_lexer_accepted_it(self):
        lexer = Lexer("firstWord")
        self.assertEqual(None, lexer.next_token().start_position.file_name)

        lexer = Lexer("firstWord", file_name="test_file")
        token = lexer.next_token()
        self.assertEqual("test_file", token.start_position.file_name)

    def test_position_can_be_represented_as_string(self):
        position_without_file = Position(1, 2)
        # we sum 1 to both row and column. This way we can store the values indexing from zero, but
        # print them in a way that is more user-friendly.
        self.assertEqual("2:3", str(position_without_file))

        position_with_file = Position(1, 2, "/home/test/test_file.txt")
        self.assertEqual("/home/test/test_file.txt:2:3", str(position_with_file))

    def test_all_tokens_have_position(self):
        lexer = Lexer("firstWord  secondWord\n\n\n thirdWord;>fourth==fifth", __file__)
        #  0|firstWord  secondWord
        #   |^        ^
        #   |0        9
        #===============================
        #  0|firstWord  secondWord
        #   |           ^         ^
        #   |           11        21
        #===============================
        #  0|firstWord  secondWord
        #  1|
        #  2|
        #  3| thirdWord;>fourth==fifth
        #   |          ^^
        #   |          10
        #   |           11

        tokens = [
            { "value": "firstWord", "start": (0, 0), "end": (0, 9) },
            { "value": "secondWord", "start": (0, 11), "end": (0, 21) },
            { "value": "thirdWord", "start": (3, 1), "end": (3, 10) },
            { "value": ";", "start": (3, 10), "end": (3, 11) },
            { "value": ">", "start": (3, 11), "end": (3, 12) },
            { "value": "fourth", "start": (3, 12), "end": (3, 18) },
            { "value": "==", "start": (3, 18), "end": (3, 20) },
            { "value": "fifth", "start": (3, 20), "end": (3, 25) },
        ]

        for expected in tokens:
            token = lexer.next_token()
            self.assertEqual(expected["value"], token.value)
            self.assertEqual(token.end_position.column - token.start_position.column, len(token.value))
            self.assertEqual(expected["end"][1] - expected["start"][1], len(token.value))
            self.assertEqual(expected["start"][0], token.start_position.line)
            self.assertEqual(expected["start"][1], token.start_position.column)
            self.assertEqual(expected["end"][0], token.end_position.line)
            self.assertEqual(expected["end"][1], token.end_position.column)

    def test_peek_does_not_interfere_with_position(self):
        assert False, f"TODO!"
