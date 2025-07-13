from queue import Queue
from math import floor, ceil
from dataclasses import dataclass
from time import time
import gurobipy as gp
from gurobipy import GRB
from tabulate import tabulate


class Table:
    def __init__(self) -> None:
        self.headers = ['Iter nº', 'Nós aval', 'Nós ñ aval', 'z da iter',
            'Ação', 'z ótimo', 'tempo (s)']
        self.reset()

    def reset(self) -> None:
        self.__rows = []
        self.fmt = ""
        self.__reset_row()

    def __reset_row(self) -> None:
        self.iter: int | None = None
        self.eval: int | None = None
        self.not_eval: int | None = None
        self.z_iter: float | None = None
        self.action: str | None = None
        self.z_optm: str | None = None  # deve ser string para colocar o `*`
        self.elapsed_time: float | None = None

    def add_row(self) -> None:
        self.__rows.append([self.iter, self.eval, self.not_eval, self.z_iter,
            self.action, self.z_optm, self.elapsed_time])
        self.__reset_row()

    def print(self) -> None:
        table = tabulate(self.__rows, headers=self.headers,
            tablefmt=self.fmt, floatfmt='.4f')
        print(table)


@dataclass
class Solution:
    x: dict[str, float]
    z: float


class BranchAndBound:
    def __init__(self, is_maximize: bool) -> None:
        self.is_maximize = is_maximize
        self.nodes = Queue()
        self.table = Table()
        self.__reset()

    def __reset(self) -> None:
        self.best_solution = Solution({}, float('inf'))
        self.iterations = 0
        self.there_is_unbounded_solution = False
        self.start_time = time()
        self.total_time = 0.0

    def optimize(self, root: gp.Model, int_var_names: list[str]) -> None:
        self.__reset()

        self.nodes.put(root)

        while not self.nodes.empty():
            node = self.nodes.get()
            self.__iterate(node, int_var_names)

        self.total_time = time() - self.start_time
        self.__print()

    def __iterate(self, node: gp.Model, int_var_names: list[str]) -> None:
        best_solution_improved = False
        self.iterations += 1
        self.table.iter = self.iterations

        # Relaxação linear do subproblema
        node.optimize()

        # Adiciona o valor da funça o objetivo da relaxaça o linear à tabela
        if node.Status == GRB.OPTIMAL:
            self.table.z_iter = self.__fix_signal(node.ObjVal)

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

        # Adiciona informações da iteração à tabela
        self.table.eval = self.iterations
        self.table.not_eval = self.nodes.qsize()
        if best_solution_improved:
            self.table.z_optm = f'*{self.__fix_signal(self.best_solution.z):.4f}'
        elif self.best_solution.z != float('inf'):
            self.table.z_optm = f'{self.__fix_signal(self.best_solution.z):.4f}'
        self.table.elapsed_time = time() - self.start_time
        self.table.add_row()

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

    def __fix_signal(self, num: int | float) -> int | float:
        # Inverte o sinal se o problema for de maximização (eu fiz isso porque
        # estou considerando todos os problemas como de minimização)
        return -num if self.is_maximize else num

    def __print(self) -> None:
        self.table.fmt = "grid"
        self.table.print()
        self.table.reset()

        # Imprime o valor da função objetivo
        if self.best_solution.z == float('inf'):
            if self.there_is_unbounded_solution:
                print("Solução ótima ilimitada")
            else:
                print("Problema inviável")
        else:
            print(f"Solução ótima (z): {self.__fix_signal(self.best_solution.z):.4f}")
            print("Valor das variáveis de decisão:")
            for var_name, var_value in self.best_solution.x.items():
                print(f"-> {var_name}: {var_value:.4f}")

        print(f"Número de iterações realizadas: {self.iterations}")
        print(f"Tempo total de execução: {self.total_time:.4f} s")
