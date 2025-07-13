from src.branch_and_bound import BranchAndBound
from src.ampl import parse_text
import sys
import gurobipy as gp


def config_gurobi(model: gp.Model) -> None:
    model.Params.Threads = 1         # Limita o número de threads
    model.Params.Method = 0          # Força o uso do Simplex
    model.Params.DualReductions = 0  # Para saber se a solução foi ilimitada
    model.Params.Presolve = 0        # Desativa pré-processamento
    model.Params.CutPasses = 0       # Desativa geração de cortes
    model.Params.Cuts = 0            # Desativa geração de cortes
    model.Params.Heuristics = 0      # Desativa heurísticas


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError(f"usage: {sys.argv[0]} <ampl_file>")
    # text = """var x1 integer >=0;
    # var x2 integer >=0;
    # maximize: 5*x1 + 8*x2;
    # subject to: 1*x1 + 1*x2 <= 6;
    # subject to: 5*x1 + 9*x2 <= 45;
    # end;"""

    filename = sys.argv[1]
    model, int_var_names, is_maximize = parse_text(filename)
    config_gurobi(model)

    # model.presolve()
    # print(f"vars1: {model.getVars()}")
    # model.addConstr(model.getVarByName('x1') <= 1)
    # # model.getVarByName('x1').setAttr('UB', 2.0)
    # # model.getVarByName('x1').UB = 2.0
    # # print(f"UB: {model.getVarByName('x1').UB}")
    # model.optimize()
    # print(f"vars2: {model.getVars()}")
    # print(f"Obj: {model.getObjective()}")
    # for v in model.getVars():
    #     print(f"{v.VarName}: {v.X:g}")
    #     # print(f"is integer: {v.X.is_integer()}")
    # print(f"z: {model.ObjVal:g}")

    b_and_b = BranchAndBound(is_maximize)
    b_and_b.optimize(model, int_var_names)


if __name__ == "__main__":
    main()
