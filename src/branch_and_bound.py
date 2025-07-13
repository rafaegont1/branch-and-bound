from queue import Queue
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
        self.nodes = Queue()
        self.__reset()

    def __reset(self) -> None:
        self.best_solution = Solution({}, float('inf'))
        self.iteration = 0
        self.there_is_unbounded_solution = False

    def optimize(self, root: gp.Model, int_var_names: list[str]) -> None:
        self.__reset()
        start_time = time()

        print("iter\t\taval\t\tñ aval\t\tz iter\t\tação\t\tz ótim\t\ttempo (s)")
        self.nodes.put(root)

        while not self.nodes.empty():
            node = self.nodes.get()
            self.__iterate(node, int_var_names)

        end_time = time()
        elapsed_time = end_time - start_time
        print(f"elapsed time: {elapsed_time:.3f} s")

    def __iterate(self, node: gp.Model, int_var_names: list[str]) -> None:
        self.iteration += 1
        print(self.iteration, end='\t\t')
        print("TODO", end='\t\t')  # TODO: nodes avaliados
        print("TODO", end='\t\t')  # TODO: nodes não avaliados

        # Relaxação linear do subproblema
        node.optimize()

        if node.Status == GRB.OPTIMAL:
            print(f"{node.ObjVal:.2f}", end='\t\t')
        else:
            print("None", end='\t\t')

        # Variáveis que devem ser inteiras
        y = [node.getVarByName(yi_name) for yi_name in int_var_names]

        # Poda por invibialidade
        if node.Status != GRB.OPTIMAL:
            print("I")
            if node.Status == GRB.UNBOUNDED:
                self.there_is_unbounded_solution = True
        # Poda pelo limite
        elif node.ObjVal >= self.best_solution.z:
            print("L")
        # Poda por otimalidade
        elif all(yi.X.is_integer() for yi in y):
            print("O")
            if node.ObjVal < self.best_solution.z:
                self.best_solution.x = {v.VarName: v.X for v in node.getVars()}
                self.best_solution.z = node.ObjVal
        # Nenhuma poda possível
        else:
            print("D")

            # Variável com maior resíduo
            branch_var = min(y, key=lambda yi: abs((yi.X % 1) - 0.5))

            left_child = self.__new_branch(node, branch_var, 'left')
            self.nodes.put(left_child)

            right_child = self.__new_branch(node, branch_var, 'right')
            self.nodes.put(right_child)

    def __new_branch(
        self,
        parent: gp.Model,
        parent_var: gp.Var,
        side: str
    ) -> gp.Model:
        child = parent.copy()
        child_var = child.getVarByName(parent_var.VarName)

        match side:
            case 'left':
                child_var.UB = floor(parent_var.X)
            case 'right':
                child_var.LB = ceil(parent_var.X)
            case _:
                raise ValueError(f"undefined `{side}` child")

        return child
