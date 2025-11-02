# reserved_words.py

from TipoToken import TipoToken

# Mapeamento completo de todos os tokens reservados e especiais
reserved_words = {
    # Palavras-chave
    'fn': TipoToken.FN,
    'main': TipoToken.MAIN,
    'let': TipoToken.LET,
    'int': TipoToken.INT,
    'float': TipoToken.FLOAT,
    'char': TipoToken.CHAR,
    'char_lit': TipoToken.CHAR_LITERAL,
    'string': TipoToken.FMT_STRING,
    'if': TipoToken.IF,
    'else': TipoToken.ELSE,
    'while': TipoToken.WHILE,
    'println': TipoToken.PRINTLN,
    'return': TipoToken.RETURN,
    
    # Operadores (para verificação, embora sejam single char)
    '->': TipoToken.ARROW,
    '==': TipoToken.EQ,
    '!=': TipoToken.NE,
    '<=': TipoToken.LE,
    '>=': TipoToken.GE,
    
    # Delimitadores (para verificação)
    '(': TipoToken.LBRACKET,
    ')': TipoToken.RBRACKET,
    '{': TipoToken.LBRACE,
    '}': TipoToken.RBRACE,
    ';': TipoToken.SEMICOLON,
    ',': TipoToken.COMMA,
    ':': TipoToken.COLON,
    '+': TipoToken.PLUS,
    '-': TipoToken.MINUS,
    '*': TipoToken.MULT,
    '/': TipoToken.DIV,
    '=': TipoToken.ASSIGN,
    '<': TipoToken.LT,
    '>': TipoToken.GT
}

# Função auxiliar para verificar se é palavra reservada
def is_reserved_word(lexema):
    return lexema in reserved_words

# Função para obter o tipo do token reservado
def get_reserved_token_type(lexema):
    return reserved_words.get(lexema, None)