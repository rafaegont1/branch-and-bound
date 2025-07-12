from lark import Lark, Transformer, v_args
from lark.lexer import Token
import gurobipy as gp
from gurobipy import GRB

GRAMMAR = """
    ?start: variable_declaration+ objective constraint+ "end;"
    ?variable_declaration: "var" NAME VAR_DOMAIN VAR_BOUND ";" -> decl_var
    ?objective: OBJ_GOAL ":" sum ";"                           -> obj
    ?constraint: "subject to:" cmp ";"                         -> st

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
        self.vars: dict[str, gp.Var] = {}
        self.int_var_names: list[str] = []
        self.model = gp.Model()

    def decl_var(self, name: Token, domain: Token, bound: Token) -> None:
        # print("---decl_var---")
        # print(type(name), type(vtype), type(bound))
        # print(name, vtype, bound)
        match bound.value:
            case '<=0':
                lb, ub = (-GRB.INFINITY, 0)
            case '>=0':
                lb, ub = (0, GRB.INFINITY)
            case 'free':
                lb, ub = (-GRB.INFINITY, GRB.INFINITY)

        if domain.value == 'integer':
            # Adicionar à lista de nomes de variáveis inteiras
            self.int_var_names.append(name.value)

        self.vars[name.value] = self.model.addVar(lb, ub, name=name.value)

    def obj(self, goal: Token, expr: gp.LinExpr) -> None:
        # print("---obj---")
        # print(type(goal), type(expr))
        # print(goal, expr)
        match goal.value:
            case 'minimize':
                self.model.setObjective(expr, GRB.MINIMIZE)
            case 'maximize':
                self.model.setObjective(-expr, GRB.MINIMIZE)

    def st(self, cmp: gp.TempConstr) -> None:
        # print("---st---")
        # print(type(cmp))
        # print(cmp)
        self.model.addConstr(cmp)

    def var(self, name: Token) -> gp.Var:
        # print("---var---")
        # print(type(name))
        # print(name)
        return self.vars[name.value]


def parse_text(text: str) -> tuple[gp.Model, list[str]]:
    transformer = AMPLTransformer()
    parser = Lark(GRAMMAR, parser='lalr', transformer=transformer)
    parser.parse(text)

    return transformer.model, transformer.int_var_names
