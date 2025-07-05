from src.ampl import parse_text


def main() -> None:
    text = """var x1 real >=0;
    var x2 real >=0;
    minimize: -3*x1 - 5*x2;
    1*x1 <= 4;
    1*x2 <= 6;
    3*x1 + 2*x2 >= 18;"""

    model = parse_text(text)
    model.optimize()

    for v in model.getVars():
        print(f"{v.VarName} {v.X:g}")
    print(f"Obj: {model.ObjVal:g}")


if __name__ == "__main__":
    main()
