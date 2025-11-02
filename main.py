#Alunos : Julia Nunes e Lucas Alemida

from afd import returnNextState
from read_file import save_string
from TipoToken import TipoToken
import json
import os

# Listas para armazenar os elementos
id_list = []
num_int_list = []
num_dec_list = []
text_list = []
tokens = []
erros = []
arquivo_analisado = ""  # Variável global para armazenar o nome do arquivo

def analisar_com_afd():
    """Função principal que usa o AFD para análise léxica"""
    global tokens, erros, arquivo_analisado
    
    # Obtém o código do arquivo .p e o nome do arquivo
    codigo, nome_arquivo = save_string()
    arquivo_analisado = nome_arquivo  # Salva o nome do arquivo globalmente
    
    if not codigo:
        print("Erro: Nenhum código encontrado para analisar.")
        return
    
    print("\n=== INICIANDO ANÁLISE LÉXICA COM AFD ===")
    print(f"Analisando arquivo: {nome_arquivo}\n")
    
    # Limpa listas para nova análise
    tokens.clear()
    erros.clear()
    id_list.clear()
    num_int_list.clear()
    num_dec_list.clear()
    text_list.clear()
    
    # Usa o AFD para analisar token por token
    posicao = 0
    linha = 1
    
    while posicao < len(codigo):
        # Pula espaços em branco
        while posicao < len(codigo) and codigo[posicao].isspace():
            if codigo[posicao] == '\n':
                linha += 1
            posicao += 1
        
        if posicao >= len(codigo):
            break
                
                        
        # Encontra o próximo token
        token_str = extrair_proximo_token(codigo, posicao)
        
        if token_str:
            # Usa o AFD para classificar o token
            tipo_token = returnNextState(token_str)
            
            if tipo_token and tipo_token != TipoToken.UNKNOWN:
                processar_token(tipo_token, token_str, linha)
            else:
                # Token não reconhecido
                erros.append(f"Erro léxico: Token não reconhecido '{token_str}' na linha {linha}")
                tokens.append(("ERRO", token_str, linha))
            
            # Atualiza posição
            posicao += len(token_str)
            
            # Atualiza contador de linhas se houver quebras no token
            for char in token_str:
                if char == '\n':
                    linha += 1
        else:
            # Caractere não processável
            if posicao < len(codigo):
                erros.append(f"Erro léxico: Caractere não reconhecido '{codigo[posicao]}' na linha {linha}")
                tokens.append(("ERRO", codigo[posicao], linha))
                posicao += 1
    
    # Adiciona token EOF
    tokens.append((TipoToken.EOF, "", linha))

def extrair_proximo_token(codigo, posicao_inicial):
    """Extrai o próximo token do código"""
    if posicao_inicial >= len(codigo):
        return ""
        
    posicao = posicao_inicial
    char_atual = codigo[posicao]
    
    # Se for string, captura até a próxima aspas
    if char_atual == '"':
        token = '"'
        posicao += 1
        while posicao < len(codigo) and codigo[posicao] != '"':
            token += codigo[posicao]
            posicao += 1
        if posicao < len(codigo) and codigo[posicao] == '"':
            token += '"'
            posicao += 1
        return token
    
    # Se for char, captura até o próximo apóstrofo
    elif codigo[posicao] == "'":       
        token = "'"
        posicao += 1
        
        # Caso char vazio
        if posicao < len(codigo) and codigo[posicao] == "'":
            token += "'"
            posicao += 1
            return token
        
        # Caso char com um caractere
        elif posicao < len(codigo):
            token += codigo[posicao]  # Adiciona o caractere
            posicao += 1
            
            # Procura aspas de fechamento
            if posicao < len(codigo) and codigo[posicao] == "'":
                token += "'"
                posicao += 1
                return token
            else:
                # Char não fechado - erro
                return token  # Token incompleto: "'a" em vez de "'a'"
    

    
    # Para identificadores e números
    elif char_atual.isalpha() or char_atual == '_':
        token = ""
        while posicao < len(codigo) and (codigo[posicao].isalnum() or codigo[posicao] == '_'):
            token += codigo[posicao]
            posicao += 1
        return token
    
    # Para números
    elif char_atual.isdigit():
        token = ""
        tem_ponto = False
        while posicao < len(codigo):
            char = codigo[posicao]
            if char.isdigit():
                token += char
                posicao += 1
            elif char == '.' and not tem_ponto:
                token += char
                posicao += 1
                tem_ponto = True
            else:
                break
        return token
    
    # Para operadores e delimitadores
    else:
        # Operadores de dois caracteres
        if posicao + 1 < len(codigo):
            dois_chars = codigo[posicao:posicao + 2]
            if dois_chars in ['->', '==', '!=', '<=', '>=']:
                return dois_chars
        
        # Operadores de um caractere
        delimitadores = '(){}[];:,=!<>+-*/"'
        if char_atual in delimitadores:
            return char_atual
        
        # Caractere desconhecido
        return char_atual
    
    token_str = extrair_proximo_token(codigo, posicao)
    print(f"[DEBUG] Token extraído: {repr(token_str)}")

def processar_token(tipo_token, lexema, linha):
    """Processa o token classificando nas listas apropriadas"""
    global tokens, id_list, num_int_list, num_dec_list, text_list
    
    # Verifica se é palavra reservada
    from reserved_words import reserved_words
    if lexema in reserved_words:
        tokens.append((reserved_words[lexema], lexema, linha))
    
    # Classifica baseado no tipo do AFD
    elif tipo_token == TipoToken.ID:
        if lexema not in id_list:
            id_list.append(lexema)
        index = id_list.index(lexema)
        tokens.append((f"ID", lexema, linha))
    
    elif tipo_token == TipoToken.INT_CONST:
        if lexema not in num_int_list:
            num_int_list.append(lexema)
        index = num_int_list.index(lexema)
        tokens.append((f"INT_CONST", lexema, linha))
    
    elif tipo_token == TipoToken.FLOAT_CONST:
        if lexema not in num_dec_list:
            num_dec_list.append(lexema)
        index = num_dec_list.index(lexema)
        tokens.append((f"FLOAT_CONST", lexema, linha))

    elif tipo_token == TipoToken.FMT_STRING:
        if lexema not in text_list:
            print('{}', lexema)
            text_list.append(lexema)
        index = text_list.index(lexema)
        tokens.append((f"FMT_STRING", lexema, linha))
    
    elif tipo_token == TipoToken.CHAR_LITERAL:
        tokens.append((TipoToken.CHAR_LITERAL, lexema, linha))
    
    else:
        # Outros tokens (operadores, delimitadores)        
        tokens.append((tipo_token, lexema, linha))

def salvar_resultados_json():
    """Salva os resultados em arquivo JSON com o mesmo nome do arquivo .p"""
    global tokens, id_list, num_int_list, num_dec_list, text_list, erros, arquivo_analisado
    
    # Se não temos o nome do arquivo analisado, usa um padrão
    if not arquivo_analisado:
        arquivos_p = [f for f in os.listdir('.') if f.endswith('.p')]
        if arquivos_p:
            arquivo_analisado = arquivos_p[0]
        else:
            arquivo_analisado = "programa"
    
    # Remove a extensão .p e cria nome do JSON
    nome_base = os.path.splitext(arquivo_analisado)[0]
    arquivo_json = f"tokens_{nome_base}.json"
    
    print(f" Salvando resultados como: {arquivo_json}")
    
    dados = {
        "tokens": [
            {
                "token": token[0],
                "lexema": token[1],
                "linha": token[2]
            } for token in tokens
        ],
        "tabelas": {
            "identificadores": id_list,
            "numeros_inteiros": num_int_list,
            "numeros_decimais": num_dec_list,
            "textos": text_list
        },
        "estatisticas": {
            "total_tokens": len(tokens),
            "identificadores": len(id_list),
            "numeros_inteiros": len(num_int_list),
            "numeros_decimais": len(num_dec_list),
            "textos": len(text_list),
            "erros": len(erros)
        },
        "erros": erros,
        "arquivo_origem": arquivo_analisado,
        "timestamp": os.path.getctime(arquivo_analisado) if os.path.exists(arquivo_analisado) else None
    }
    
    try:
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return arquivo_json
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")
        return None

def mostrar_resultados():
    """Exibe os resultados na tela"""
    print("\n" + "="*50)
    print("RESULTADOS DA ANÁLISE LÉXICA")
    print("="*50)
    
    print(f"\nTotal de tokens: {len(tokens)}")
    print(f" Erros encontrados: {len(erros)}")
    
    if erros:
        print(f"\n--- ERROS ENCONTRADOS ---")
        for erro in erros:
            print(f"{erro}")
    
    print(f"\n--- AMOSTRA DE TOKENS (primeiros 10) ---")
    for token in tokens[:10]:
        print(f"Linha {token[2]}: {token[0]} -> '{token[1]}'")
    
    if len(tokens) > 10:
        print(f"... e mais {len(tokens) - 10} tokens")
    
    print(f"\n--- TABELAS ---")
    print(f"Identificadores: {len(id_list)} -> {id_list}")
    print(f"Números inteiros: {len(num_int_list)} -> {num_int_list}")
    print(f"Números decimais: {len(num_dec_list)} -> {num_dec_list}")
    print(f"Textos: {len(text_list)} -> {text_list}")

def main():
    """Função principal"""
    print("=== ANALISADOR LÉXICO COM AFD ===")
    print("Buscando arquivos com extensão .p...")
    
    # Executa a análise
    analisar_com_afd()
    
    if not tokens:
        print(" Nenhum token foi reconhecido. Verifique o arquivo de entrada.")
        return
    
    # Mostra resultados
    mostrar_resultados()
    
    # Salva em JSON
    arquivo_json = salvar_resultados_json()
    if arquivo_json:
        print(f"\nResultados salvos em: {arquivo_json}")
        print(f"Arquivo origem: {arquivo_analisado}")
    else:
        print("Falha ao salvar resultados em JSON")

if __name__ == "__main__":
    main()