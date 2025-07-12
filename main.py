from src.branch_and_bound import BranchAndBound
from src.ampl import parse_text


def main() -> None:
    text = """var x1 real >=0;
    var x2 integer >=0;
    minimize: -3*x1 - 5*x2;
    1*x1 <= 4;
    1*x2 <= 6;
    3*x1 + 2*x2 >= 18;"""

    model, int_var_names = parse_text(text)
    # x['x1'].setAttr('UB', 2.0)
    # x['x1'].UB = 2.0
    # model.optimize()
    # print(f"id: {id(x['x1'])}")

    # for v in model.getVars():
    #     print(f"{v.VarName}: {v.X:g} | id:{id(v)}")
    #     # print(f"is integer: {v.X.is_integer()}")
    # print(f"Obj: {model.ObjVal:g}")

    # print("Integer variables:")
    # for name in int_var_names:
    #     print(f"\t{name}: {model.getVarByName(name)}")

    b_and_b = BranchAndBound()
    b_and_b.optimize(model, int_var_names)
    print(f"best solution: {b_and_b.best_solution}")


if __name__ == "__main__":
    main()
