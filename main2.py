import json
import os
from typing import List, Dict

from TipoToken import TipoToken
from ast import (
    FunctionNode, BlockNode,
    VarNode, IntConstNode, FloatConstNode, CharConstNode, StringNode,
    BinaryOpNode, AssignNode, PrintNode, ReturnNode
)



# tabela de simbolos

class Symbol:
    def __init__(self, name, type_, category, line):
        self.name = name
        self.type = type_
        self.category = category
        self.line = line

    def to_dict(self):
        return {
            "nome": self.name,
            "tipo": self.type,
            "categoria": self.category,
            "linha": self.line
        }


class SymbolTable:
    def __init__(self, scope_name):
        self.scope_name = scope_name
        self.symbols: Dict[str, Symbol] = {}

    def add_symbol(self, name, type_, category, line):
        if name in self.symbols:
            return f"[ERRO] '{name}' já declarado no escopo '{self.scope_name}' (linha {line})"
        self.symbols[name] = Symbol(name, type_, category, line)
        return None

    def to_dict(self):
        return {
            "escopo": self.scope_name,
            "simbolos": [s.to_dict() for s in self.symbols.values()]
        }



class Parser:
    def __init__(self, tokens: List[Dict]):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.tables: List[SymbolTable] = []
        self.current_table = None

        
        self.functions_ast = []

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else {
            "token": TipoToken.EOF, "lexema": "", "linha": 0
        }

    def eat(self, expected):
        tok = self.current()
        if tok["token"] == expected:
            self.pos += 1
        else:
            self.errors.append({
                "linha": tok["linha"],
                "erro": f"Erro sintático: esperado {expected}, encontrado {tok['token']}"
            })
            self.pos += 1

  
    def parse(self):
        while self.current()["token"] != TipoToken.EOF:
            func = self.function_decl()
            if func:
                self.functions_ast.append(func)

        return self.errors, self.tables, self.functions_ast

  
    def function_decl(self):
        tok = self.current()

        if tok["token"] != TipoToken.FN:
            self.errors.append({
                "linha": tok["linha"],
                "erro": "Função deve começar com 'fn'"
            })
            self.pos += 1
            return None

        self.eat(TipoToken.FN)

        name = self.current()["lexema"]
        line = self.current()["linha"]
        self.eat(self.current()["token"])  

        # inicia tabela de símbolos desse escopo
        self.current_table = SymbolTable(name)
        self.tables.append(self.current_table)

        # parâmetros
        self.eat(TipoToken.LBRACKET)
        params = self.param_list()
        self.eat(TipoToken.RBRACKET)

        # corpo
        body = self.block()

        # retorna AST
        return FunctionNode(name, params, body, self.current_table, line)

   
    def param_list(self):
        params = []

        if self.current()["token"] == TipoToken.ID:
            while True:
                pname = self.current()["lexema"]
                pline = self.current()["linha"]
                self.eat(TipoToken.ID)

                self.eat(TipoToken.COLON)
                ptype = self.current()["lexema"]
                self.eat(self.current()["token"])

                err = self.current_table.add_symbol(pname, ptype, "parâmetro", pline)
                if err:
                    self.errors.append({"linha": pline, "erro": err})

                params.append((pname, ptype, pline))

                if self.current()["token"] == TipoToken.COMMA:
                    self.eat(TipoToken.COMMA)
                    continue
                break

        return params

 
    def block(self):
        self.eat(TipoToken.LBRACE)

        commands = []

        while self.current()["token"] not in [TipoToken.RBRACE, TipoToken.EOF]:

            if self.current()["token"] == TipoToken.LET:
                self.var_decl()
                continue

            cmd = self.command()
            if cmd:
                commands.append(cmd)

        self.eat(TipoToken.RBRACE)

        return BlockNode(commands)

    
    def var_decl(self):
        self.eat(TipoToken.LET)

        ids = []
        while True:
            name = self.current()["lexema"]
            line = self.current()["linha"]
            ids.append((name, line))
            self.eat(TipoToken.ID)

            if self.current()["token"] == TipoToken.COMMA:
                self.eat(TipoToken.COMMA)
                continue
            break

        self.eat(TipoToken.COLON)

        tipo = self.current()["lexema"]
        self.eat(self.current()["token"])

        self.eat(TipoToken.SEMICOLON)

        # registro na tabela
        for name, line in ids:
            err = self.current_table.add_symbol(name, tipo, "variável", line)
            if err:
                self.errors.append({"linha": line, "erro": err})

 
    def command(self):
        tok = self.current()

       
        if tok["token"] == TipoToken.ID and self.tokens[self.pos + 1]["token"] == TipoToken.ASSIGN:
            name = tok["lexema"]
            line = tok["linha"]

            self.eat(TipoToken.ID)
            self.eat(TipoToken.ASSIGN)

            expr = self.expression()

            self.eat(TipoToken.SEMICOLON)
            return AssignNode(name, expr, line)

      
        if tok["token"] == TipoToken.PRINTLN:
            line = tok["linha"]
            self.eat(TipoToken.PRINTLN)
            self.eat(TipoToken.LBRACKET)

            args = []
            if self.current()["token"] != TipoToken.RBRACKET:
                args.append(self.expression())
                while self.current()["token"] == TipoToken.COMMA:
                    self.eat(TipoToken.COMMA)
                    args.append(self.expression())

            self.eat(TipoToken.RBRACKET)
            self.eat(TipoToken.SEMICOLON)

            return PrintNode(args, line)

        
        if tok["token"] == TipoToken.RETURN:
            line = tok["linha"]
            self.eat(TipoToken.RETURN)
            expr = self.expression()
            self.eat(TipoToken.SEMICOLON)
            return ReturnNode(expr, line)

      
        expr = self.expression()
        self.eat(TipoToken.SEMICOLON)
        return expr

  
    def expression(self):
        node = self.atom()

        while self.current()["token"] in [
            TipoToken.PLUS, TipoToken.MINUS, TipoToken.MULT, TipoToken.DIV
        ]:
            op = self.current()["token"]
            line = self.current()["linha"]
            self.eat(op)
            right = self.atom()
            node = BinaryOpNode(op, node, right, line)

        return node

    def atom(self):
        tok = self.current()
        line = tok["linha"]

        if tok["token"] == TipoToken.ID:
            name = tok["lexema"]
            self.eat(TipoToken.ID)
            return VarNode(name, line)

        if tok["token"] == TipoToken.INT_CONST:
            v = tok["lexema"]
            self.eat(TipoToken.INT_CONST)
            return IntConstNode(v, line)

        if tok["token"] == TipoToken.FLOAT_CONST:
            v = tok["lexema"]
            self.eat(TipoToken.FLOAT_CONST)
            return FloatConstNode(v, line)

        if tok["token"] == TipoToken.CHAR_LITERAL:
            v = tok["lexema"]
            self.eat(TipoToken.CHAR_LITERAL)
            return CharConstNode(v, line)

        if tok["token"] == TipoToken.FMT_STRING:
            v = tok["lexema"]
            self.eat(TipoToken.FMT_STRING)
            return StringNode(v, line)

        if tok["token"] == TipoToken.LBRACKET:
            self.eat(TipoToken.LBRACKET)
            n = self.expression()
            self.eat(TipoToken.RBRACKET)
            return n

        self.errors.append({
            "linha": line,
            "erro": f"Expressão inválida começando com {tok['token']}"
        })
        self.pos += 1
        return None



def executar_analise_sintatica():
    arquivos = [f for f in os.listdir(".") if f.startswith("tokens_") and f.endswith(".json")]
    if not arquivos:
        print(" Nenhum arquivo tokens_*.json encontrado. Rode a análise léxica antes!")
        return

    json_tokens = max(arquivos, key=os.path.getctime)
    print(f" Usando arquivo de tokens: {json_tokens}")

    with open(json_tokens, "r", encoding="utf-8") as f:
        dados = json.load(f)

    tokens = dados["tokens"]
    parser = Parser(tokens)

    erros, tabelas, funcoes_ast = parser.parse()

    with open("saida_sintatica.json", "w", encoding="utf-8") as f:
        json.dump({"erros_sintaticos": erros}, f, indent=2, ensure_ascii=False)

    tabelas_json = [t.to_dict() for t in tabelas]
    with open("tabelas_simbolos.json", "w", encoding="utf-8") as f:
        json.dump({"tabelas": tabelas_json}, f, indent=2, ensure_ascii=False)

    print("\n Análise sintática concluída!")
    print(f"Erros encontrados: {len(erros)}")
    print(f"Tabelas geradas: {len(tabelas)}")

    for t in tabelas:
        print(f"\nTabela de símbolos de '{t.scope_name}':")
        for s in t.symbols.values():
            print(f" - {s.name}: {s.type} ({s.category})")


if __name__ == "__main__":
    executar_analise_sintatica()
