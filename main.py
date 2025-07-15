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

    filename = sys.argv[1]
    model, int_var_names, is_maximize = parse_text(filename)
    config_gurobi(model)

    b_and_b = BranchAndBound(is_maximize)
    b_and_b.optimize(model, int_var_names)


if __name__ == "__main__":
    main()
