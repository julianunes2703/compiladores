

class ASTNode:
    pass



# expressões


class VarNode(ASTNode):
    def __init__(self, name, line):
        self.name = name
        self.line = line
        self.type = None


class IntConstNode(ASTNode):
    def __init__(self, value, line):
        self.value = int(value)
        self.line = line
        self.type = "int"


class FloatConstNode(ASTNode):
    def __init__(self, value, line):
        self.value = float(value)
        self.line = line
        self.type = "float"


class CharConstNode(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line = line
        self.type = "char"


class StringNode(ASTNode):
    def __init__(self, value, line):
        self.value = value
        self.line = line
        self.type = "string"


class BinaryOpNode(ASTNode):
    def __init__(self, op, left, right, line):
        self.op = op
        self.left = left
        self.right = right
        self.line = line
        self.type = None




class AssignNode(ASTNode):
    def __init__(self, name, expr, line):
        self.name = name
        self.expr = expr
        self.line = line


class PrintNode(ASTNode):
    def __init__(self, args, line):
        self.args = args
        self.line = line


class ReturnNode(ASTNode):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line


class BlockNode(ASTNode):
    def __init__(self, commands):
        self.commands = commands




class FunctionNode(ASTNode):
    def __init__(self, name, params, body, table, line):
        self.name = name
        self.params = params
        self.body = body
        self.table = table
        self.line = line
