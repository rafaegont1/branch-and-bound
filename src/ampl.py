from lark import Lark, Transformer, v_args
from lark.lexer import Token

GRAMMAR = """
    ?start: variable+ objective constraint+
    ?variable: "var" NAME VAR_TYPE VAR_BOUND ";" -> decl_var
    ?objective: OBJ_SENSE ":" sum ";"            -> obj
    ?constraint: sum CMP_OP sum ";"              -> st

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: atom
        | product "*" atom  -> mul

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"

    VAR_TYPE: "integer" | "real"
    VAR_BOUND: "<=0" | ">=0" | "free"
    OBJ_SENSE: "minimize" | "maximize"
    CMP_OP: "<=" | "=" | ">="

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS

    %ignore WS
"""


@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, neg
    number = float

    def __init__(self) -> None:
        self.vars = {}

    def decl_var(self, name: Token, vtype: Token, bound: Token) -> None:
        print("---decl_var---")
        print(type(name), type(vtype), type(bound))
        print(name, vtype, bound)
        self.vars[name] = (vtype, bound)

    def obj(self, sense: Token, expr) -> None:
        print("---obj---")
        print(type(sense), type(expr))
        print(sense, expr)

    def st(self, left_expr, cmp_op: Token, right_expr) -> None:
        print("---st---")
        print(type(left_expr), type(cmp_op), type(right_expr))
        print(left_expr, cmp_op, right_expr)

    def var(self, name):
        print("---var---")
        print(type(name))
        print(name)
        return 1


def parse_text(text: str) -> None:
    transformer = CalculateTree()
    parser = Lark(GRAMMAR, parser='lalr', transformer=transformer)
    parser.parse(text)
