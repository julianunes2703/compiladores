

from ast import (
    FunctionNode, BlockNode,
    VarNode, IntConstNode, FloatConstNode, CharConstNode, StringNode,
    BinaryOpNode, AssignNode, PrintNode, ReturnNode
)

class SemanticAnalyzer:
    def __init__(self, functions_ast):
        self.functions = functions_ast
        self.errors = []

   
    def analyze(self):
        for func in self.functions:
            self.check_function(func)
        return self.errors

 
    def check_function(self, func: FunctionNode):
        self.current_table = func.table
        self.check_block(func.body)


    def check_block(self, block: BlockNode):
        for cmd in block.commands:
            self.check_command(cmd)

    def check_command(self, cmd):

       
        if isinstance(cmd, AssignNode):
            symbol = self.current_table.symbols.get(cmd.name)

            if not symbol:
                self.errors.append(
                    f"[ERRO SEMÂNTICO] Variável '{cmd.name}' não declarada (linha {cmd.line})"
                )
                return

            expr_type = self.check_expression(cmd.expr)

            if expr_type and expr_type != symbol.type:
                self.errors.append(
                    f"[ERRO SEMÂNTICO] Tipo incompatível em '{cmd.name}' = expr "
                    f"(linha {cmd.line}) → esperado {symbol.type}, encontrado {expr_type}"
                )
            return

      
        if isinstance(cmd, PrintNode):
            for expr in cmd.args:
                self.check_expression(expr)
            return

    
        if isinstance(cmd, ReturnNode):
            self.check_expression(cmd.expr)
            return

      
        if isinstance(cmd, BinaryOpNode):
            self.check_expression(cmd)
            return

    def check_expression(self, expr):

        
        if isinstance(expr, VarNode):
            symbol = self.current_table.symbols.get(expr.name)
            if not symbol:
                self.errors.append(
                    f"[ERRO SEMÂNTICO] Variável '{expr.name}' não declarada "
                    f"(linha {expr.line})"
                )
                return None
            return symbol.type

        # INT
        if isinstance(expr, IntConstNode):
            return "int"

        # FLOAT
        if isinstance(expr, FloatConstNode):
            return "float"

        # CHAR
        if isinstance(expr, CharConstNode):
            return "char"

        # STRING
        if isinstance(expr, StringNode):
            return "string"

        # BINÁRIO
        if isinstance(expr, BinaryOpNode):
            left = self.check_expression(expr.left)
            right = self.check_expression(expr.right)

            # qualquer operação exige tipos compatíveis
            if left != right:
                self.errors.append(
                    f"[ERRO SEMÂNTICO] Tipos incompatíveis em operação binária "
                    f"'{expr.op}' (linha {expr.line})"
                )
                return None

            # Apenas int/float aceitos em + - * /
            if expr.op in ["PLUS", "MINUS", "MULT", "DIV"]:
                if left not in ["int", "float"]:
                    self.errors.append(
                        f"[ERRO SEMÂNTICO] Operação '{expr.op}' só aceita int/float "
                        f"(linha {expr.line})"
                    )
                    return None
                return left  # preserva tipo

            return None

        return None
