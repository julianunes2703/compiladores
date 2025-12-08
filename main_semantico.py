# main_semantico.py

import json
import os
from main2 import Parser   # usa seu parser modificado
from semantic import SemanticAnalyzer

def achar_json_tokens():
    arquivos = [f for f in os.listdir(".") if f.startswith("tokens_") and f.endswith(".json")]
    if not arquivos:
        print("Nenhum arquivo tokens_*.json encontrado. Rode a análise léxica antes!")
        exit(1)
    return max(arquivos, key=os.path.getctime)

def ast_to_dict(node):
    # valores nulos
    if node is None:
        return None

    # se for um tipo primitivo (int, float, string, etc.)
    if isinstance(node, (int, float, str)):
        return node

    # se for uma TUPLA (como a lista de parâmetros)
    if isinstance(node, tuple):
        return list(node)   # converte tuple → lista para aparecer no JSON

    # se for uma LISTA de nós
    if isinstance(node, list):
        return [ast_to_dict(n) for n in node]

    # se não tiver __dict__, retorna como valor bruto
    if not hasattr(node, "__dict__"):
        return node

    # caso geral: nó da AST
    d = {"tipo": node.__class__.__name__}

    for attr, value in node.__dict__.items():

        if attr == "table":  # não incluir tabela de símbolos dentro da AST
            continue

        d[attr] = ast_to_dict(value)

    return d


def main():
    json_tokens_file = achar_json_tokens()
    print(f"Carregando tokens de {json_tokens_file}")

    with open(json_tokens_file, "r", encoding="utf-8") as f:
        dados = json.load(f)

    tokens = dados["tokens"]

    parser = Parser(tokens)
    erros_sintaticos, tabelas_simbolos, funcoes_ast = parser.parse()

    sem = SemanticAnalyzer(funcoes_ast)
    erros_semanticos = sem.analyze()

    # montar estrutura final
    saida = {
        "funcoes": {}
    }

    for func in funcoes_ast:
        saida["funcoes"][func.name] = {
            "tabela_simbolos": func.table.to_dict(),
            "ast": ast_to_dict(func),
            "erros_semanticos": erros_semanticos
        }

    with open("saida_semantica.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=2, ensure_ascii=False)

    print("\nAnálise semântica concluída!")
    print(f"Erros semânticos encontrados: {len(erros_semanticos)}")

    for e in erros_semanticos:
        print(" -", e)

if __name__ == "__main__":
    main()
