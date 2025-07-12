from lark import Lark, Transformer, v_args
from lark.lexer import Token
import gurobipy as gp
from gurobipy import GRB

GRAMMAR = """
    ?start: variable_declaration+ objective constraint+
    ?variable_declaration: "var" NAME VAR_DOMAIN VAR_BOUND ";" -> decl_var
    ?objective: OBJ_GOAL ":" sum ";"                           -> obj
    ?constraint: cmp ";"                                       -> st

    ?cmp: sum "<=" number          -> le
        | sum ">=" number          -> ge
        | sum "=" number           -> eq

    ?sum: product
        | sum "+" product          -> add
        | sum "-" product          -> sub

    ?product: number "*" variable  -> mul

    ?number: NUMBER                -> num
           | "-" number            -> neg

    ?variable: NAME                -> var

    VAR_DOMAIN: "integer" | "real"
    VAR_BOUND: "<=0" | ">=0" | "free"
    OBJ_GOAL: "minimize" | "maximize"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS

    %ignore WS
"""


@v_args(inline=True)    # Affects the signatures of the methods
class AMPLTransformer(Transformer):
    from operator import add, sub, mul, neg, le, ge, eq
    num = float

    def __init__(self) -> None:
        self.x: dict[str, gp.Var] = {}  # real variables
        self.y: dict[str, gp.Var] = {}  # integer variables
        self.model = gp.Model()

    def decl_var(self, name: Token, domain: Token, bound: Token) -> None:
        # print("---decl_var---")
        # print(type(name), type(vtype), type(bound))
        # print(name, vtype, bound)
        lb, ub = {
            '<=0': (-GRB.INFINITY, 0),
            '>=0': (0, GRB.INFINITY),
            'free': (-GRB.INFINITY, GRB.INFINITY),
        }[bound.value]
        if domain == "real":
            self.x[name.value] = self.model.addVar(lb, ub, name=name.value)
        elif domain == "integer":
            self.y[name.value] = self.model.addVar(lb, ub, name=name.value)

    def obj(self, goal: Token, expr: gp.LinExpr) -> None:
        # print("---obj---")
        # print(type(sense), type(expr))
        # print(sense, expr)
        sense = {'minimize': GRB.MINIMIZE, 'maximize': GRB.MAXIMIZE}[goal.value]
        self.model.setObjective(expr, sense)

    def st(self, cmp: gp.TempConstr) -> None:
        # print("---st---")
        # print(type(cmp))
        # print(cmp)
        self.model.addConstr(cmp)

    def var(self, name: Token) -> gp.Var:
        # print("---var---")
        # print(type(name))
        # print(name)
        return self.x[name.value] or self.y[name.value]


def parse_text(
    text: str
) -> tuple[gp.Model, dict[str, gp.Var], dict[str, gp.Var]]:
    transformer = AMPLTransformer()
    parser = Lark(GRAMMAR, parser='lalr', transformer=transformer)
    parser.parse(text)
    return transformer.model, transformer.x, transformer.y
    # for key, val in transformer.vars.items():
    #     print(f"{key}: {val}")
