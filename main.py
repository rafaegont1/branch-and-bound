from src.ampl import parse_text


def main() -> None:
    text = """var x1 integer free;
    var x2 integer free;
    minimize: 2*x1 + 1*x2;
    5*x1 + 10*x2 <= 10;"""

    parse_text(text)


if __name__ == "__main__":
    main()
