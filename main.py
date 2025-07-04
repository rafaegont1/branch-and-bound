from src.ampl import parse_text


def main() -> None:
    text = "var x1 integer free;"
    parse_text(text)


if __name__ == "__main__":
    main()
