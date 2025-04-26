from lexer import Lexer


def print_all_tokens(l: Lexer):
    while token := l.next_token():
        print(f"[{token.type}] {token.value}")


if __name__ == "__main__":
    # Example usage
    lexer = Lexer("""
    int main() {
        printf("Hello, World!");
        double a = 0.1 + 0.2;
        return 0;
    }
    """)

    print_all_tokens(lexer)
