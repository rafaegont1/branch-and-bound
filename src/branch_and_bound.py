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

        self.__iterate(model, int_var_names)

        end_time = time()
        elapsed_time = end_time - start_time
        print(f"elapsed time: {elapsed_time}")

    def __iterate(self, model: gp.Model, int_var_names: list[str]) -> None:
        self.iteration += 1
        print(f"-----> iteração nº: {self.iteration} <-----")

        # Relaxação linear do subproblema
        model.optimize()
        print(f"status: {model.Status}")
        print(f"variáveis: {model.getVars()}")
        if model.Status == GRB.OPTIMAL:
            print(f"z: {model.ObjVal}")
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
            branch_var = min(y, key=lambda yi: abs((yi.X % 1) - 0.5))
            print(f"branching with: {branch_var}")

            left_branch = self.__new_branch(model, branch_var, 'left')
            self.__iterate(left_branch, int_var_names)

            right_branch = self.__new_branch(model, branch_var, 'right')
            self.__iterate(right_branch, int_var_names)

            # left_branch = model.copy()
            # left_branch.presolve()
            # left_branch_var = left_branch.getVarByName(branch_var.VarName)
            # print(f"left_branch_var: {left_branch_var}")
            # # left_branch.addConstr(left_branch_var <= branch_var.X)
            # left_branch_var.setAttr('UB', floor(branch_var.X))
            # print(f"var: {left_branch.getVarByName(branch_var.VarName)}")
            # print(f"floor: {floor(branch_var.X)}")
            # # left_branch_var.UB = floor(branch_var.X)
            # print(f"left UB: {left_branch_var.UB}")
            # # self.__iterate(left_branch, int_var_names)

            # right_branch = model.copy()
            # right_branch_var = right_branch.getVarByName(branch_var.VarName)
            # right_branch.addConstr(right_branch_var >= branch_var.X)
            # self.__iterate(right_branch, int_var_names)

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
                print(f"criando novo branch a partir da variável `{parent_var.VarName}` com valor `{floor(parent_var.X)}`")
            case 'right':
                child_var.LB = ceil(parent_var.X)
                print(f"criando novo branch a partir da variável `{parent_var.VarName}` com valor `{ceil(parent_var.X)}`")
            case _:
                raise ValueError(f"undefined `{side}` child")

        return child

    # def __new_branch_bounds(self, y: list[gp.Var]) -> tuple[str, float, float]:
    #     # Variável com maior resíduo: a variável inteira que assume valor
    #     # fracionário e que a parte fracionária é mais próxima de 0.5 é
    #     # escolhida para realizar a ramificação
    #     branch_var = min(y, key=lambda yi: abs((yi.X % 1) - 0.5))
    #     return branch_var.VarName, floor(branch_var.X), ceil(branch_var.X)
