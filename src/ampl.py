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
        self.is_maximize = False

    def decl_var(self, name: Token, domain: Token, bound: Token) -> None:
        match bound.value:
            case '<=0':
                lb, ub = (-GRB.INFINITY, 0)
            case '>=0':
                lb, ub = (0, GRB.INFINITY)
            case 'free':
                lb, ub = (-GRB.INFINITY, GRB.INFINITY)

        if domain.value == 'integer':
            # Adiciona à lista de nomes de variáveis inteiras (eu uso esta lista
            # para verificar se as variáveis com estes nomes são inteiras dentro
            # do branch and bound)
            self.int_var_names.append(name.value)

        self.vars[name.value] = self.model.addVar(lb, ub, name=name.value)

    def obj(self, goal: Token, expr: gp.LinExpr) -> None:
        # Se o problema for `maximize z`, eu passo para `minimize -z` (pois
        # assim fica mais simples de implementar o branch and bound, igual ao
        # pseudo-código que esta nos slides)
        match goal.value:
            case 'minimize':
                self.model.setObjective(expr, GRB.MINIMIZE)
                self.is_maximize = False
            case 'maximize':
                self.model.setObjective(-expr, GRB.MINIMIZE)
                self.is_maximize = True

    def st(self, cmp: gp.TempConstr) -> None:
        self.model.addConstr(cmp)

    def var(self, name: Token) -> gp.Var:
        return self.vars[name.value]


def parse_text(filename: str) -> tuple[gp.Model, list[str], bool]:
    with open(filename, encoding='utf-8') as file:
        text = file.read()
    transformer = AMPLTransformer()
    parser = Lark(GRAMMAR, parser='lalr', transformer=transformer)
    parser.parse(text)

    return transformer.model, transformer.int_var_names, transformer.is_maximize
