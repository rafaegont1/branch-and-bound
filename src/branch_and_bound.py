from queue import Queue
from math import floor, ceil
from dataclasses import dataclass
from time import time
import gurobipy as gp
from gurobipy import GRB
from tabulate import tabulate


class Table:
    def __init__(self) -> None:
        self.headers = ['Iter', 'Nós aval', 'Nós ñ aval', 'z da iter', 'Ação',
            'z ótimo', 'tempo (s)']
        self.reset()

    def reset(self) -> None:
        self.__lines = []
        self.fmt = ""
        self.__reset_line()

    def __reset_line(self) -> None:
        self.iter: int | None = None
        self.eval: int | None = None
        self.not_eval: int | None = None
        self.z_iter: float | None = None
        self.action: str | None = None
        self.z_optm: str | None = None  # deve ser string para colocar o `*`
        self.elapsed_time: float | None = None

    def add_line(self) -> None:
        self.__lines.append([self.iter, self.eval, self.not_eval, self.z_iter,
            self.action, self.z_optm, self.elapsed_time])
        self.__reset_line()

    def print(self) -> None:
        table = tabulate(self.__lines, headers=self.headers,
            tablefmt=self.fmt, floatfmt='.4f')
        print(table)


@dataclass
class Solution:
    x: dict[str, float]
    z: float


class BranchAndBound:
    def __init__(self) -> None:
        self.nodes = Queue()
        self.table = Table()
        self.__reset()

    def __reset(self) -> None:
        self.best_solution = Solution({}, float('inf'))
        self.iteration = 0
        self.there_is_unbounded_solution = False
        self.start_time = time()

    def optimize(self, root: gp.Model, int_var_names: list[str]) -> None:
        self.__reset()

        self.nodes.put(root)

        while not self.nodes.empty():
            node = self.nodes.get()
            self.__iterate(node, int_var_names)

        elapsed_time = time() - self.start_time

        self.table.fmt = "grid"
        self.table.print()
        self.table.reset()

        print(f"elapsed time: {elapsed_time:.4f} s")

    def __iterate(self, node: gp.Model, int_var_names: list[str]) -> None:
        best_solution_improved = False
        self.iteration += 1

        self.table.iter = self.iteration
        self.table.eval = self.iteration
        self.table.not_eval = self.nodes.qsize()

        # Relaxação linear do subproblema
        node.optimize()

        if node.Status == GRB.OPTIMAL:
            self.table.z_iter = node.ObjVal

        # Variáveis que devem ser inteiras
        y = [v for name in int_var_names if (v := node.getVarByName(name)) is not None]

        # Poda por invibialidade
        if node.Status != GRB.OPTIMAL:
            self.table.action = 'I'
            if node.Status == GRB.UNBOUNDED:
                self.there_is_unbounded_solution = True
        # Poda pelo limite
        elif node.ObjVal >= self.best_solution.z:
            self.table.action = 'L'
        # Poda por otimalidade
        elif all(yi.X.is_integer() for yi in y):
            self.table.action = 'O'
            if node.ObjVal < self.best_solution.z:
                best_solution_improved = True
                self.best_solution.x = {v.VarName: v.X for v in node.getVars()}
                self.best_solution.z = node.ObjVal
        # Nenhuma poda possível
        else:
            self.table.action = 'D'

            # Variável com maior resíduo
            branch_var = min(y, key=lambda yi: abs((yi.X % 1) - 0.5))

            left_child = self.__new_branch(node, branch_var, 'left')
            self.nodes.put(left_child)

            right_child = self.__new_branch(node, branch_var, 'right')
            self.nodes.put(right_child)

        if best_solution_improved:
            self.table.z_optm = f'*{self.best_solution.z:.4f}'
        elif self.best_solution.z != float('inf'):
            self.table.z_optm = f'{self.best_solution.z:.4f}'
        self.table.elapsed_time = time() - self.start_time
        self.table.add_line()

    def __new_branch(
        self,
        parent: gp.Model,
        parent_var: gp.Var,
        side: str
    ) -> gp.Model:
        child = parent.copy()
        var_name = parent_var.VarName
        child_var = child.getVarByName(var_name)

        # O retorno de `getVarByName` é opcional
        if child_var is None:
            raise ValueError(f"child variable `{var_name}` wasn't found")

        match side:
            case 'left':
                child_var.UB = floor(parent_var.X)
            case 'right':
                child_var.LB = ceil(parent_var.X)
            case _:
                raise ValueError(f"undefined `{side}` child")

        return child
