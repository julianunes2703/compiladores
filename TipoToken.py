# TipoToken.py

class TipoToken:
    # Palavras-chave da linguagem P
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
    
    # Operadores
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
    
    # Delimitadores
    LBRACKET = "LBRACKET"       #(
    RBRACKET = "RBRACKET"       #)
    LBRACE = "LBRACE"           #{
    RBRACE = "RBRACE"           #}
    SEMICOLON = "SEMICOLON"     #;
    COMMA = "COMMA"             #,
    COLON = "COLON"             #: 
    
    # Literais e identificadores
    ID = "ID"
    INT_CONST = "INT_CONST"
    FLOAT_CONST = "FLOAT_CONST"
    CHAR_LITERAL = "CHAR_LITERAL"
    FMT_STRING = "FMT_STRING"
    
    # Outros
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

# Nota: PALAVRAS_CHAVE foi movido para reserved_words.py para centralização