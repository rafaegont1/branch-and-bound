from enum import Enum
from lark import Lark, Transformer, v_args
from lark.lexer import Token
import gurobipy as gp
from gurobipy import GRB

GRAMMAR = """
    ?start: variable+ objective constraint+
    ?variable: "var" NAME VAR_DOMAIN VAR_BOUND ";" -> decl_var
    ?objective: OBJ_GOAL ":" sum ";"               -> obj
    ?constraint: cmp ";"                           -> st

    ?cmp: sum "<=" sum      -> le
        | sum ">=" sum      -> ge
        | sum "=" sum       -> eq

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"

    VAR_DOMAIN: "integer" | "real"
    VAR_BOUND: "<=0" | ">=0" | "free"
    OBJ_GOAL: "minimize" | "maximize"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS

    %ignore WS
"""


class VType(Enum):
    INTEGER = 'integer'
    REAL = 'real'


class Bound(Enum):
    GEZ = '>=0'
    LEZ = '<=0'
    FREE = 'free'


@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, neg, le, ge, eq
    number = float

    def __init__(self) -> None:
        self.vars = {}
        self.model = gp.Model()

    def decl_var(self, name: Token, domain: Token, bound: Token) -> None:
        # print("---decl_var---")
        # print(type(name), type(vtype), type(bound))
        # print(name, vtype, bound)
        lb, ub = {
            '<=0': (-GRB.INFINITY, 0),
            '>=0': (0, GRB.INFINITY),
            'free': (-GRB.INFINITY, GRB.INFINITY),
        }[bound]
        self.vars[name] = self.model.addVar(lb, ub, name=name)

    def obj(self, goal: Token, expr: gp.LinExpr) -> None:
        # print("---obj---")
        # print(type(sense), type(expr))
        # print(sense, expr)
        sense = {'minimize': GRB.MINIMIZE, 'maximize': GRB.MAXIMIZE}[goal]
        self.model.setObjective(expr, sense)

    def st(self, cmp: gp.TempConstr) -> None:
        # print("---st---")
        # print(type(lhs), type(cmp_op), type(rhs))
        # print(lhs, cmp_op, rhs)
        self.model.addConstr(cmp)

    def var(self, name: Token) -> gp.Var:
        # print("---var---")
        # print(type(name))
        # print(name)
        return self.vars[name]


def parse_text(text: str) -> gp.Model:
    transformer = CalculateTree()
    parser = Lark(GRAMMAR, parser='lalr', transformer=transformer)
    parser.parse(text)
    return transformer.model
    # for key, val in transformer.vars.items():
    #     print(f"{key}: {val}")
