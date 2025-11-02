import json
import os
from typing import List, Dict

class TipoToken:
    FN = "FUNCTION"
    MAIN = "MAIN"
    LET = "LET"
    INT = "INT"
    FLOAT = "FLOAT"
    CHAR = "CHAR"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    PRINTLN = "PRINTLN"
    RETURN = "RETURN"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULT = "MULT"
    DIV = "DIV"
    ASSIGN = "ASSIGN"
    EQ = "EQ"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LE = "LE"
    GE = "GE"
    ARROW = "ARROW"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    COLON = "COLON"
    ID = "ID"
    INT_CONST = "INT_CONST"
    FLOAT_CONST = "FLOAT_CONST"
    CHAR_LITERAL = "CHAR_LITERAL"
    FMT_STRING = "FMT_STRING"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"


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
            return f"[ERRO] '{name}' já declarado em {self.scope_name} (linha {line})"
        self.symbols[name] = Symbol(name, type_, category, line)
        return None

    def to_dict(self):
        return {
            "escopo": self.scope_name,
            "simbolos": [s.to_dict() for s in self.symbols.values()]
        }


# =====================================================
# PARSER (DESCIDA RECURSIVA)
# =====================================================
class Parser:
    def __init__(self, tokens: List[Dict]):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.tables: List[SymbolTable] = []
        self.current_table = None

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else {"token": TipoToken.EOF, "lexema": "", "linha": 0}

    def eat(self, expected):
        tok = self.current()
        if tok["token"] == expected:
            self.pos += 1
        else:
            self.errors.append({
                "linha": tok["linha"],
                "erro": f"Esperado {expected}, encontrado {tok['token']}"
            })
            self.pos += 1

    # -----------------------------------------------------
    # GRAMÁTICA PRINCIPAL
    # -----------------------------------------------------
    def parse(self):
        while self.current()["token"] != TipoToken.EOF:
            self.function_decl()
        return self.errors, self.tables

    def function_decl(self):
        tok = self.current()
        if tok["token"] == TipoToken.FN:
            self.eat(TipoToken.FN)
            name = self.current()["lexema"]
            self.eat(self.current()["token"])  # aceita ID ou MAIN
            self.current_table = SymbolTable(name)
            self.tables.append(self.current_table)
            self.eat(TipoToken.LBRACKET)
            self.param_list()
            self.eat(TipoToken.RBRACKET)
            self.block()
        else:
            self.errors.append({
                "linha": tok["linha"],
                "erro": "Função deve começar com 'fn'"
            })
            self.pos += 1

    def param_list(self):
        if self.current()["token"] == TipoToken.ID:
            while True:
                var_name = self.current()["lexema"]
                self.eat(TipoToken.ID)
                self.eat(TipoToken.COLON)
                var_type = self.current()["lexema"]
                self.eat(self.current()["token"])
                err = self.current_table.add_symbol(var_name, var_type, "parâmetro", self.current()["linha"])
                if err:
                    self.errors.append({"linha": self.current()["linha"], "erro": err})
                if self.current()["token"] == TipoToken.COMMA:
                    self.eat(TipoToken.COMMA)
                    continue
                break

    def block(self):
        self.eat(TipoToken.LBRACE)
        while self.current()["token"] not in [TipoToken.RBRACE, TipoToken.EOF]:
            if self.current()["token"] == TipoToken.LET:
                self.var_decl()
            else:
                self.command()
        self.eat(TipoToken.RBRACE)

    def var_decl(self):
        # let a, b, c: float;
        self.eat(TipoToken.LET)
        ids = []
        while True:
            ids.append(self.current()["lexema"])
            self.eat(TipoToken.ID)
            if self.current()["token"] == TipoToken.COMMA:
                self.eat(TipoToken.COMMA)
                continue
            break
        self.eat(TipoToken.COLON)
        tipo = self.current()["lexema"]
        self.eat(self.current()["token"])
        self.eat(TipoToken.SEMICOLON)
        for name in ids:
            err = self.current_table.add_symbol(name, tipo, "variável", self.current()["linha"])
            if err:
                self.errors.append({"linha": self.current()["linha"], "erro": err})

    def command(self):
        tok = self.current()

        # ID = expressão ;
        if tok["token"] == TipoToken.ID and self.tokens[self.pos + 1]["token"] == TipoToken.ASSIGN:
            self.eat(TipoToken.ID)
            self.eat(TipoToken.ASSIGN)
            self.expression()
            self.eat(TipoToken.SEMICOLON)
            return

        # println("{}", media);
        if tok["token"] == TipoToken.PRINTLN:
            call_name = self.current()["lexema"]
            self.eat(TipoToken.PRINTLN)
            self.eat(TipoToken.LBRACKET)
            if self.current()["token"] != TipoToken.RBRACKET:
                self.expression()
                while self.current()["token"] == TipoToken.COMMA:
                    self.eat(TipoToken.COMMA)
                    self.expression()
            self.eat(TipoToken.RBRACKET)
            self.eat(TipoToken.SEMICOLON)
            # registra chamada
            if self.current_table and call_name not in self.current_table.symbols:
                self.current_table.add_symbol(call_name, "void", "chamada", tok["linha"])
            return

        # comando return
        if tok["token"] == TipoToken.RETURN:
            self.eat(TipoToken.RETURN)
            self.expression()
            self.eat(TipoToken.SEMICOLON)
            return

        # expressão isolada
        self.expression()
        if self.current()["token"] == TipoToken.SEMICOLON:
            self.eat(TipoToken.SEMICOLON)
        else:
            self.errors.append({
                "linha": tok["linha"],
                "erro": "Ponto e vírgula esperado"
            })

    def expression(self):
        tok = self.current()

        # ( expressão )
        if tok["token"] == TipoToken.LBRACKET:
            self.eat(TipoToken.LBRACKET)
            self.expression()
            self.eat(TipoToken.RBRACKET)
            if self.current()["token"] in [TipoToken.PLUS, TipoToken.MINUS, TipoToken.MULT, TipoToken.DIV]:
                op = self.current()["token"]
                self.eat(op)
                self.expression()
            return

        # átomo simples
        if tok["token"] in [TipoToken.ID, TipoToken.INT_CONST, TipoToken.FLOAT_CONST, TipoToken.CHAR_LITERAL, TipoToken.FMT_STRING]:
            self.eat(tok["token"])
            if self.current()["token"] in [TipoToken.PLUS, TipoToken.MINUS, TipoToken.MULT, TipoToken.DIV]:
                op = self.current()["token"]
                self.eat(op)
                self.expression()
            return

        self.errors.append({
            "linha": tok["linha"],
            "erro": f"Expressão inválida começando com {tok['token']}"
        })
        self.pos += 1



def executar_analise_sintatica():
    # encontra o último tokens_*.json gerado
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
    erros, tabelas = parser.parse()

    # salva os arquivos de saída
    with open("saida_sintatica.json", "w", encoding="utf-8") as f:
        json.dump({"erros_sintaticos": erros}, f, indent=2, ensure_ascii=False)
    tabelas_json = [t.to_dict() for t in tabelas]
    with open("tabelas_simbolos.json", "w", encoding="utf-8") as f:
        json.dump({"tabelas": tabelas_json}, f, indent=2, ensure_ascii=False)

    # resumo no terminal
    print("\n Análise sintática concluída!")
    print(f"Erros encontrados: {len(erros)}")
    print(f"Tabelas geradas: {len(tabelas)}")

    if erros:
        print("\nErros sintáticos:")
        for e in erros:
            print(f" - Linha {e['linha']}: {e['erro']}")
    else:
        print("\nNenhum erro sintático encontrado!")

    for t in tabelas:
        print(f"\nTabela de símbolos do escopo '{t.scope_name}':")
        for s in t.symbols.values():
            print(f" - {s.name}: {s.type} ({s.category})")



if __name__ == "__main__":
    executar_analise_sintatica()
