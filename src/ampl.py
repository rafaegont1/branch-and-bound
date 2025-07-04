from lark import Lark, Transformer, UnexpectedToken, v_args

GRAMMAR = """
    ?start: var

    ?var: "var" NAME TYPE BOUND ";" -> var
    TYPE: "integer" | "real"
    BOUND: "<=0" | ">=0" | "free"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE

    %ignore WS_INLINE
"""


@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    # from operator import add, sub, mul, truediv as div, neg
    # number = float

    def __init__(self) -> None:
        self.vars = {}

    def var(self, name, type, bound):
        print(name, type, bound)

    # def type(self, type_str) -> None:
    #     print("type")
    #     print(type_str)

    # def bound(self, bound_str) -> None:
    #     print("bound")
    #     print(bound_str)


def parse_text(text: str) -> None:
    transformer = CalculateTree()
    parser = Lark(GRAMMAR, parser='lalr', transformer=transformer)
    try:
        parser.parse(text)
    except UnexpectedToken as e:
        print(f"Parser error: expcted: {e.expected}, found {e.token} ({e.line}:{e.column})")
    # print(transformer.ident('a'))
