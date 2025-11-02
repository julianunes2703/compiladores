import re
from TipoToken import TipoToken
from reserved_words import reserved_words

class AFD:
    def __init__(self):
        # Estados do AFD baseados no seu código
        self.ESTADO_INICIAL = "q0"
        self.estado_atual = "q0"

        # Tabela de transições baseada no seu padrão
        self.transitions = {
            # Delimitadores - reconhece imediatamente
            ('q0', re.compile(r'^\($')): 'q0',
            ('q0', re.compile(r'^\)$')): 'q0',
            ('q0', re.compile(r'^\{$')): 'q0',
            ('q0', re.compile(r'^\}$')): 'q0',
            ('q0', re.compile(r'^;$')): 'q0',
            ('q0', re.compile(r'^:$')): 'q0',
            ('q0', re.compile(r'^,$')): 'q0',            
            ('q0', re.compile(r'^\*$')): 'q0',
            ('q0', re.compile(r'^\/$')): 'q0',
            ('q0', re.compile(r'^\+$')): 'q0',

            # Operador - (seta ->)
            ('q0', re.compile(r'^-$')): 'q1',
            ('q1', re.compile(r'^>$')): 'q0',
            ('q1', re.compile(r'^.$')): 'q0',

            # Operador ! e !=
            ('q0', re.compile(r'^!$')): 'q2',
            ('q2', re.compile(r'^=$')): 'q0',
            ('q2', re.compile(r'^.$')): 'q0',

            # Operador = e ==
            ('q0', re.compile(r'^=$')): 'q3',
            ('q3', re.compile(r'^=$')): 'q0',
            ('q3', re.compile(r'^.$')): 'q0',

            # Operador < e <=
            ('q0', re.compile(r'^<$')): 'q4',
            ('q4', re.compile(r'^=$')): 'q0',
            ('q4', re.compile(r'^.$')): 'q0',

            # Operador > e >=
            ('q0', re.compile(r'^>$')): 'q5',
            ('q5', re.compile(r'^=$')): 'q0',
            ('q5', re.compile(r'^.$')): 'q0',

            # Identificadores
            ('q0', re.compile(r'^[A-Za-z_]$')): 'q6',
            ('q6', re.compile(r'^[A-Za-z0-9_]$')): 'q6',
            ('q6', re.compile(r'^.$')): 'q0',

            # Números inteiros
            ('q0', re.compile(r'^[0-9]$')): 'q7',
            ('q7', re.compile(r'^[0-9]$')): 'q7',
            ('q7', re.compile(r'[^.]$')): 'q0',

            # Números decimais
            ('q7', re.compile(r'^.$')): 'q8',
            ('q8', re.compile(r'^[0-9]$')): 'q9',
            ('q9', re.compile(r'^[0-9]$')): 'q9',
            ('q9', re.compile(r'^.$')): 'q0',

            # Char literal
            ('q0', re.compile(r"^'$")): 'q10',
            ('q10', re.compile(r'^.$', re.DOTALL)): 'q11',
            ('q11', re.compile(r"^'$")): 'q0',

            # String
            ('q0', re.compile(r'^\"')): 'q12',
            ('q12', re.compile(r'^[^"]*')): 'q12',
            ('q12', re.compile(r'^\"')): 'q0' 
        }

        # Mapeamento de estados finais para tipos de token
        self.finish_states = {
            'q0': {
                '(': TipoToken.LBRACKET,
                ')': TipoToken.RBRACKET,
                '{': TipoToken.LBRACE,
                '}': TipoToken.RBRACE,
                ';': TipoToken.SEMICOLON,
                ':': TipoToken.COLON,
                ',': TipoToken.COMMA,
                '+': TipoToken.PLUS,
                '*': TipoToken.MULT,
                '/': TipoToken.DIV,
                '"': TipoToken.FMT_STRING,
                "'": TipoToken.CHAR_LITERAL
            },
            'q1': TipoToken.MINUS,
            'q3': TipoToken.ASSIGN,
            'q4': TipoToken.LT,
            'q5': TipoToken.GT,
            'q6': TipoToken.ID,
            'q7': TipoToken.INT_CONST,
            'q8': TipoToken.UNKNOWN,
            'q9': TipoToken.FLOAT_CONST,
            'q11': TipoToken.CHAR_LITERAL,
            'q12': TipoToken.FMT_STRING
        }

        # Tokens de dois caracteres
        self.two_char_tokens = {
            '->': TipoToken.ARROW,
            '!=': TipoToken.NE,
            '==': TipoToken.EQ,
            '<=': TipoToken.LE,
            '>=': TipoToken.GE
        }

    def reset(self):
        """Reseta o AFD para o estado inicial"""
        self.estado_atual = self.ESTADO_INICIAL

    def processar_caractere(self, char):
        """Processa um caractere e retorna o próximo estado"""
        for (current_state, regex_pattern), next_state in self.transitions.items():
            if self.estado_atual == current_state and regex_pattern.match(str(char)):
                self.estado_atual = next_state
                return self.estado_atual
        return self.estado_atual


    def obter_tipo_token(self, lexema):
        """Determina o tipo do token baseado no estado atual e no lexema"""
        # Primeiro verifica tokens de dois caracteres
        if lexema in self.two_char_tokens:
            return self.two_char_tokens[lexema]

        # Verifica tokens de um caractere no estado q0
        if self.estado_atual == 'q0' and len(lexema) == 1:
            if lexema in self.finish_states['q0']:
                return self.finish_states['q0'][lexema]
        
        if re.fullmatch(r"'(.)'", lexema):
            return TipoToken.CHAR_LITERAL
        
        # Verifica outros estados
        if self.estado_atual in self.finish_states:
            tipo_base = self.finish_states[self.estado_atual]

            if isinstance(tipo_base, dict):
                if lexema in tipo_base:
                    return tipo_base[lexema]
            elif tipo_base == TipoToken.FMT_STRING and self.estado_atual == 'q0' and lexema.startswith('"') and lexema.endswith('"'):
                 return TipoToken.FMT_STRING
            elif isinstance(tipo_base, str):
                # Para identificadores, verifica se é palavra-chave
                if tipo_base == TipoToken.ID:
                    return reserved_words.get(lexema, TipoToken.ID)
                return tipo_base


        return TipoToken.UNKNOWN


    def eh_estado_final(self, estado=None):
        """Verifica se um estado é final (pode retornar um token)"""
        if estado is None:
            estado = self.estado_atual

        estados_finais = ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q9', 'q10', 'q11']
        return estado in estados_finais

# Função de compatibilidade com seu código existente
def returnNextState(token):
    """Função compatível com seu código existente"""
    afd = AFD()
    afd.reset()

    # Simula o processamento do token
    
    for char in token:
        afd.processar_caractere(char)
    
        
        #char
        

    # Obtém o tipo do token
    tipo = afd.obter_tipo_token(token)
    print(f"[DEBUG AFD] Analisando: {repr(token)} -> {tipo}")
    return tipo    