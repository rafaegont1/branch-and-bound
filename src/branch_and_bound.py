from math import floor, ceil
from dataclasses import dataclass
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

    def optimize(self, model: gp.Model, int_var_names: list[str]) -> None:
        start_time = time()
        self.best_solution = Solution({}, float('inf'))
        self.iteration = 0

        # print("núm iter\t\t núm aval\t\tnúm ñ aval\t\tz iter\t\tação\t\tz ótim\t\ttempo (s)")

        self.__iterate(model, int_var_names, 1)

        end_time = time()
        elapsed_time = end_time - start_time
        print(f"elapsed time: {elapsed_time:.3f} s")

    def __iterate(self,
        model: gp.Model,
        int_var_names: list[str],
        node_id: int
    ) -> None:
        self.iteration += 1
        print(f"-----> iteração nº: {self.iteration} <-----")
        print(f"-----> node nº: {node_id} <-----")

        # Relaxação linear do subproblema
        model.optimize()
        print(f"status: {model.Status}")
        print(f"variáveis: {model.getVars()}")
        if model.Status == GRB.OPTIMAL:
            print(f"z: {model.ObjVal}")
        # Variáveis que devem ser inteiras
        y = [model.getVarByName(yi_name) for yi_name in int_var_names]

        # Poda por invibialidade
        if model.Status != GRB.OPTIMAL:
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

            print(f"branching with: {branch_var}")

            left_branch = self.__new_branch(model, branch_var, 'left')
            self.__iterate(left_branch, int_var_names, node_id + 1)

            right_branch = self.__new_branch(model, branch_var, 'right')
            self.__iterate(right_branch, int_var_names, node_id + 2)

    def __new_branch(self,
        parent: gp.Model,
        parent_var: gp.Var,
        side: str
    ) -> gp.Model:
        child = parent.copy()
        child_var = child.getVarByName(parent_var.VarName)

        match side:
            case 'left':
                child_var.UB = floor(parent_var.X)
                print(f"criando novo branch a partir da variável com `{parent_var.VarName} <= {floor(parent_var.X)}`")
            case 'right':
                child_var.LB = ceil(parent_var.X)
                print(f"criando novo branch a partir da variável `{parent_var.VarName} >= {ceil(parent_var.X)}`")
            case _:
                raise ValueError(f"undefined `{side}` child")

        return child
