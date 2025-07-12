from math import floor, ceil
from dataclasses import dataclass, dataclass
from time import time
import gurobipy as gp
from gurobipy import GRB


@dataclass
class Solution:
    x: dict[str, float]
    z: float


class BranchAndBound:
    def __init__(self) -> None:
        self.best_solution = Solution({}, float('inf'))
        self.iteration = 0

    def optimize(self, model: gp.Model, int_var_names: list[str]):
        start_time = time()
        self.best_solution = Solution({}, float('inf'))
        self.iteration = 0

        # print("núm iter\t\t núm aval\t\tnúm ñ aval\t\tz iter\t\tação\t\tz ótim\t\ttempo (s)")

        self.__iterate(model, int_var_names)

        end_time = time()
        elapsed_time = end_time - start_time
        print(f"elapsed time: {elapsed_time}")

    def __iterate(self, model: gp.Model, int_var_names: list[str]):
        self.iteration += 1

        # Relaxação linear do subproblema
        model.optimize()
        # Variáveis que devem ser inteiras
        y = [model.getVarByName(yi_name) for yi_name in int_var_names]

        # Poda por invibialidade
        if model.Status == GRB.INFEASIBLE:
            print(f"iteração {self.iteration}: poda por invibialidade")
        # Poda pelo limite
        elif model.ObjVal >= self.best_solution.z:
            print(f"iteração {self.iteration}: poda pelo limite")
        # Poda por otimalidade
        elif all(yi.X.is_integer() for yi in y):
            print(f"iteração {self.iteration}: poda por otimalidade")
            if model.ObjVal < self.best_solution.z:
                self.best_solution.x = {v.VarName: v.X for v in model.getVars()}
                self.best_solution.z = model.ObjVal
        # Nenhuma poda possível
        else:
            print(f"iteração {self.iteration}: nenhuma poda possível")
            # Variável com maior resíduo: a variável inteira que assume valor
            # fracionário e que a parte fracionária é mais próxima de 0.5 é
            # escolhida para realizar a ramificação
            branch_var = min(y, key=lambda yi: abs((yi.X % 1) - 0.5))

            left_branch = model.copy()
            left_branch.getVarByName(branch_var.VarName).UB = floor(branch_var.X)
            self.__iterate(left_branch, int_var_names)

            right_branch = model.copy()
            right_branch.getVarByName(branch_var.VarName).LB = ceil(branch_var.X)
            self.__iterate(right_branch, int_var_names)
