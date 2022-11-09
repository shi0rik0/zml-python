from copy import deepcopy
from enum import Enum
from typing import Tuple, Union
from .ply import lex

# List of token names.   This is always required
tokens = (
    'START_TAG',
    'END_TAG',
    'INT',
    'FLOAT',
    'STR',
    'BOOL',
    'NULL',
    'EMPTY_ARR',
    'EMPTY_OBJ',
    'COMMENT',
)

# Regular expression rules for simple tokens
t_START_TAG = r'<([_a-zA-Z][_a-zA-Z0-9]*)?>'
t_END_TAG = r'</([_a-zA-Z][_a-zA-Z0-9]*)?>'
t_INT = r'0_*|[1-9][_0-9]*'
t_FLOAT = r'(0_*|[1-9][_0-9]*)\._*[0-9][_0-9]*'
t_STR = r'"([^\\\n"]|\\\\|\\"|\\n|\\b|\\t)*"|`[^\n`]*`'
t_BOOL = 'true|false'
t_NULL = 'null'
t_EMPTY_ARR = 'empty_arr'
t_EMPTY_OBJ = 'empty_obj'


def t_COMMENT(t):
    r'\#[^\n]*\n'
    t.lexer.lineno += 1

# A regular expression rule with some action code


# def t_NUMBER(t):
#     r'\d+'
#     t.value = int(t.value)
#     return t

# Define a rule so we can track line numbers


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t\r'

# Error handling rule


def t_error(t):
    raise RuntimeError(f'illegal character {t.value[0]} in line {t.lineno}')


# Build the lexer
lexer = lex.lex()


escaping = {
    't': '\t',
    'n': '\n',
    'b': '\b',
    '"': '"',
    '\\': '\\',
}


def string_literal(s: str) -> str:
    if s[0] == '"':
        builder = []
        i = 1
        while True:
            j = s.find('\\', i)
            if j == -1:
                builder.append(s[i:-1])
                break
            builder.append(s[i:j])
            builder.append(escaping[s[j+1]])
            i = j + 2
        return ''.join(builder)
    elif s[0] == '`':
        return s[1:-1]
    else:
        raise RuntimeError()


class Lexer:
    class Token(Enum):
        START_TAG = 0
        END_TAG = 1
        BOOL = 2
        NULL = 3
        INT = 20
        FLOAT = 21
        STRING = 5
        ERROR = 6
        EOF = 7
        EMPTY_OBJ = 8
        EMPTY_ARR = 9

    _str_to_token = {'START_TAG': Token.START_TAG, 'END_TAG': Token.END_TAG, 'INT': Token.INT, 'FLOAT': Token.FLOAT, 'STR': Token.STRING,
                     'BOOL': Token.BOOL, 'NULL': Token.NULL, 'EMPTY_ARR': Token.EMPTY_ARR, 'EMPTY_OBJ': Token.EMPTY_OBJ}

    def __init__(self) -> None:
        self._lexer = deepcopy(lexer)

    def input(self, s: str) -> None:
        self._lexer.input(s)

    def get_token(self) -> Tuple[Union[str, bool, None, int, float], Token]:
        tok = self._lexer.token()
        if not tok:
            return [None, Lexer.Token.EOF]
        kind = Lexer._str_to_token[tok.type]
        content: str = tok.value

        T = Lexer.Token
        if kind == T.START_TAG:
            content = content[1:-1]
        elif kind == T.END_TAG:
            content = content[2:-1]
        elif kind == T.INT:
            content = int(content.replace('_', ''))
        elif kind == T.FLOAT:
            content = float(content.replace('_', ''))
        elif kind == T.STRING:
            content = string_literal(content)
        elif kind == T.BOOL:
            content = True if content[0] == 't' else False
        elif kind == T.NULL:
            content = None
        elif kind == T.EMPTY_ARR:
            content = []
        elif kind == T.EMPTY_OBJ:
            content = {}
        else:
            raise RuntimeError()
        return (content, kind)
