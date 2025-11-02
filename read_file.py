# read_file.py
import os

def save_string():
    """Lê um arquivo .p do diretório atual e retorna (conteúdo, nome_arquivo)"""
    arquivos_p = [f for f in os.listdir('.') if f.endswith('.p')]
    
    if not arquivos_p:
        print("Nenhum arquivo .p encontrado no diretório atual.")
        print("Certifique-se de que existem arquivos com extensão .p na pasta.")
        return "", ""
    
    print("Arquivos .p encontrados:")
    for i, arquivo in enumerate(arquivos_p, 1):
        print(f"{i}. {arquivo}")
    
    try:
        escolha = int(input("\nEscolha o número do arquivo: ")) - 1
        if 0 <= escolha < len(arquivos_p):
            arquivo_selecionado = arquivos_p[escolha]
            print(f"Lendo arquivo: {arquivo_selecionado}")
            with open(arquivo_selecionado, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            print(f"✓ Arquivo lido com sucesso! ({len(conteudo)} caracteres)")
            return conteudo, arquivo_selecionado
        else:
            print("Escolha inválida!")
            return "", ""
    except (ValueError, IndexError):
        print("Entrada inválida!")
        return "", ""
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return "", ""