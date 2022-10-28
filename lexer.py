from io import TextIOWrapper
from typing import Optional, Tuple, Union
from dataclasses import dataclass
from reader import Reader
from enum import Enum


@dataclass
class ZmlVersion:
    major: int
    minor: int


class Lexer:
    class _Status(Enum):
        WAIT_NEXT_TOKEN = 0

        # Reading a start tag or an end tag.
        TAG_START = 1
        END_TAG_START = 2
        TAG_CONTENT = 3

        # Reading a number.
        NUMBER_0 = 4
        NUMBER_1_9 = 5
        NUMBER_DOT_0 = 6
        NUMBER_DOT_1 = 7

        # Reading true, false and null.
        TRUE = 8
        FALSE = 9
        NULL = 10

        # Reading a string.
        STRING_NORMAL = 11
        STRING_ESCAPING = 12

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

    def __init__(self, readable: TextIOWrapper):
        self._reader = Reader(readable)
        self._status = Lexer._Status.WAIT_NEXT_TOKEN

    # Some char sets.
    _BLANK = {' ', '\t', '\n'}
    _DIGITS = {chr(ord('0') + i) for i in range(10)}
    _ALPHABET = {chr(ord('a') + i)
                 for i in range(26)} | {chr(ord('A') + i) for i in range(26)}
    _ID_START = {'_'} | _ALPHABET
    _ID_REST = {'_'} | _ALPHABET | _DIGITS
    _DIGITS_1_9 = {chr(ord('0') + i) for i in range(1, 10)}
    _DIGITS_AND_UNDERSCORE = {'_'} | _DIGITS
    _ESCAPING_CHARACTERS = {'n', 'r', 'b', 't', '`'}

    def get_version(self) -> ZmlVersion:
        pieces = []
        while True:
            ch = self._reader.read_char()
            pieces.append(ch)
            if ch == '>':
                break
        s = ''.join(pieces)
        i = s.find('<')
        if i == -1 or not all(x in Lexer._BLANK for x in s[:i]):
            raise RuntimeError()
        t = s[i+1:-1].split(' ')
        if len(t) != 2 or t[0] != '!zml':
            raise RuntimeError()
        t = t[1].split('.')
        if len(t) != 2:
            raise RuntimeError()
        try:
            return ZmlVersion(major=int(t[0]), minor=int(t[1]))
        except ValueError as e:
            raise RuntimeError()

    def get_token(self) -> Tuple[Union[str, bool, None, int, float], Token]:
        # Skip spaces and comments.
        while True:
            ch = self._reader.read_char()
            if ch == '':
                return (None, Lexer.Token.EOF)
            elif ch == '#':
                while True:
                    ch = self._reader.read_char()
                    if ch == '\n':
                        break
                    elif ch == '':
                        return (None, Lexer.Token.EOF)
            elif ch not in Lexer._BLANK:
                self._reader.go_back()
                break

        self._reader.cut()
        ch = self._reader.read_char()

        if ch == '<':
            self._status = Lexer._Status.TAG_START
            kind = Lexer.Token.START_TAG
        elif ch == '0':
            self._status = Lexer._Status.NUMBER_0
            kind = Lexer.Token.INT
        elif ch in Lexer._DIGITS_1_9:
            self._status = Lexer._Status.NUMBER_1_9
            kind = Lexer.Token.INT
        elif ch == 't':
            self._status = Lexer._Status.TRUE
            kind = Lexer.Token.BOOL
        elif ch == 'f':
            self._status = Lexer._Status.FALSE
            kind = Lexer.Token.BOOL
        elif ch == 'n':
            self._status = Lexer._Status.NULL
            kind = Lexer.Token.NULL
        else:
            self._status = Lexer._Status.STRING_NORMAL
            kind = Lexer.Token.STRING
            str_symbol = ch

        while self._status != Lexer._Status.WAIT_NEXT_TOKEN:
            ch = self._reader.read_char()

            # Read tags.
            if self._status == Lexer._Status.TAG_START:
                if ch == '/':
                    self._status = Lexer._Status.END_TAG_START
                    kind = Lexer.Token.END_TAG
                elif ch in Lexer._ID_START:
                    self._status = Lexer._Status.TAG_CONTENT
                elif ch == '>':
                    self._status = Lexer._Status.WAIT_NEXT_TOKEN
                else:
                    return ('error', Lexer.Token.ERROR)
            elif self._status == Lexer._Status.END_TAG_START:
                if ch in Lexer._ID_START:
                    self._status = Lexer._Status.TAG_CONTENT
                elif ch == '>':
                    self._status = Lexer._Status.WAIT_NEXT_TOKEN
                else:
                    return ('error', Lexer.Token.ERROR)
            elif self._status == Lexer._Status.TAG_CONTENT:
                if ch in Lexer._ID_REST:
                    pass
                elif ch == '>':
                    self._status = Lexer._Status.WAIT_NEXT_TOKEN
                else:
                    return ('error', Lexer.Token.ERROR)

            # Read numbers.
            elif self._status == Lexer._Status.NUMBER_0:
                if ch == '.':
                    self._status = Lexer._Status.NUMBER_DOT_0
                    kind = Lexer.Token.FLOAT
                elif ch == '_':
                    pass
                else:
                    self._reader.go_back()
                    self._status = Lexer._Status.WAIT_NEXT_TOKEN
            elif self._status == Lexer._Status.NUMBER_1_9:
                if ch == '.':
                    self._status = Lexer._Status.NUMBER_DOT_0
                    kind = Lexer.Token.FLOAT
                elif ch in Lexer._DIGITS_AND_UNDERSCORE:
                    pass
                else:
                    self._reader.go_back()
                    self._status = Lexer._Status.WAIT_NEXT_TOKEN
            elif self._status == Lexer._Status.NUMBER_DOT_0:
                if ch in Lexer._DIGITS:
                    self._status = Lexer._Status.NUMBER_DOT_1
                elif ch == '_':
                    pass
                else:
                    return ('error', Lexer.Token.ERROR)
            elif self._status == Lexer._Status.NUMBER_DOT_1:
                if ch in Lexer._DIGITS_AND_UNDERSCORE:
                    pass
                else:
                    self._reader.go_back()
                    self._status = Lexer._Status.WAIT_NEXT_TOKEN

            # Read true, false and null.
            elif self._status == Lexer._Status.TRUE:
                rest = 'rue'
                if ch != rest[0]:
                    return ('error', Lexer.Token.ERROR)
                for i in rest[1:]:
                    ch = self._reader.read_char()
                    if ch != i:
                        return ('error', Lexer.Token.ERROR)
                self._status = Lexer._Status.WAIT_NEXT_TOKEN
            elif self._status == Lexer._Status.FALSE:
                rest = 'alse'
                if ch != rest[0]:
                    return ('error', Lexer.Token.ERROR)
                for i in rest[1:]:
                    ch = self._reader.read_char()
                    if ch != i:
                        return ('error', Lexer.Token.ERROR)
                self._status = Lexer._Status.WAIT_NEXT_TOKEN
            elif self._status == Lexer._Status.NULL:
                rest = 'ull'
                if ch != rest[0]:
                    return ('error', Lexer.Token.ERROR)
                for i in rest[1:]:
                    ch = self._reader.read_char()
                    if ch != i:
                        return ('error', Lexer.Token.ERROR)
                self._status = Lexer._Status.WAIT_NEXT_TOKEN

            # Read a string.
            elif self._status == Lexer._Status.STRING_NORMAL:
                if ch == str_symbol:
                    self._status = Lexer._Status.WAIT_NEXT_TOKEN
                elif ch == '`':
                    self._status = Lexer._Status.STRING_ESCAPING
                elif ch == '':
                    raise RuntimeError()
                else:
                    pass
            elif self._status == Lexer._Status.STRING_ESCAPING:
                if ch in Lexer._ESCAPING_CHARACTERS or ch == str_symbol:
                    self._status = Lexer._Status.STRING_NORMAL
                else:
                    raise RuntimeError()
            else:
                raise RuntimeError()

        content = self._reader.cut()
        if kind == Lexer.Token.START_TAG:
            return (content[1:-1], kind)
        elif kind == Lexer.Token.END_TAG:
            return (content[2:-1], kind)
        elif kind == Lexer.Token.INT:
            s = ''.join(filter(lambda x: x != '_', content))
            return (int(s), kind)
        elif kind == Lexer.Token.FLOAT:
            s = ''.join(filter(lambda x: x != '_', content))
            return (float(s), kind)
        elif kind == Lexer.Token.BOOL:
            return (True if content[0] == 't' else False, kind)
        elif kind == Lexer.Token.NULL:
            return (None, kind)
        elif kind == Lexer.Token.EOF:
            return (None, kind)
        elif kind == Lexer.Token.STRING:
            return (Lexer._process_escaping_characters(content[1:-1], str_symbol), kind)
        else:
            raise NotImplementedError()

    @staticmethod
    def _process_escaping_characters(s: str, str_symbol: str) -> str:
        pieces = []
        i = 0
        j = s.find('`', i)
        while j != -1:
            pieces.append(s[i:j])
            if j + 1 >= len(s):
                raise RuntimeError()
            ch = s[j + 1]
            if ch == 'n':
                pieces.append('\n')
            elif ch == 't':
                pieces.append('\t')
            elif ch == 'b':
                pieces.append('\b')
            elif ch == 'r':
                pieces.append('\r')
            elif ch == str_symbol:
                pieces.append(ch)
            elif ch == '`':
                pieces.append('`')
            else:
                raise RuntimeError()
            i = j + 2
            j = s.find('`', i)
        pieces.append(s[i:])
        return ''.join(pieces)
