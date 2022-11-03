from __future__ import annotations
from io import TextIOWrapper
from typing import Any, Dict, List, Tuple, NoReturn, Union
from .lexer import Lexer
from .string_stream import InStringStream, OutStringStream

AllTypes = Union['Object', 'Array', str, int, float, bool, None]
Object = Dict[str, AllTypes]
Array = List[AllTypes]


class IReadable:
    def __init__(self) -> NoReturn:
        raise NotImplementedError()

    def read(self, size: int) -> str:
        raise NotImplementedError()


class IWriteable:
    def __init__(self) -> NoReturn:
        raise NotImplementedError()

    def write(self, s: str) -> int:
        raise NotImplementedError()


class ZmlReader:
    _TERMINATORS = {Lexer.Token.BOOL, Lexer.Token.INT,
                    Lexer.Token.FLOAT, Lexer.Token.NULL, Lexer.Token.STRING,
                    Lexer.Token.EMPTY_ARR, Lexer.Token.EMPTY_OBJ}

    def __init__(self, readable: IReadable):
        self._lexer = Lexer(readable)

    def _read_next(self, key: str) -> Any:
        content, kind = self._lexer.get_token()
        if kind in ZmlReader._TERMINATORS:
            content2, kind2 = self._lexer.get_token()
            if content2 != key or kind2 != Lexer.Token.END_TAG:
                raise RuntimeError()
            ret = content
        elif kind == Lexer.Token.START_TAG:
            if content != '':
                ret, end_tag = self._read_object(content)
            else:
                ret, end_tag = self._read_array()
            if end_tag != key:
                raise RuntimeError()
        else:
            raise RuntimeError()
        return ret

    def _read_object(self, first_key: str) -> Tuple[Dict, str]:
        ret = {first_key: self._read_next(first_key)}
        while True:
            content, kind = self._lexer.get_token()
            if kind == Lexer.Token.START_TAG:
                ret[content] = self._read_next(content)
            elif kind == Lexer.Token.END_TAG:
                return (ret, content)
            elif kind == Lexer.Token.EOF:
                return (ret, '')
            else:
                raise RuntimeError()

    def _read_array(self) -> Tuple[List, str]:
        ret = [self._read_next('')]
        while True:
            content, kind = self._lexer.get_token()
            if kind == Lexer.Token.START_TAG:
                if content != '':
                    raise RuntimeError()
                ret.append(self._read_next(''))
            elif kind == Lexer.Token.END_TAG:
                return (ret, content)
            elif kind == Lexer.Token.EOF:
                return (ret, '')
            else:
                raise RuntimeError()

    def read(self) -> Dict:
        version = self._lexer.get_version()
        if version.major != 0 or version.minor != 1:
            raise RuntimeError()
        content, kind = self._lexer.get_token()
        if kind != Lexer.Token.START_TAG:
            raise RuntimeError()
        return self._read_object(content)[0]


_DIGITS = {chr(ord('0') + i) for i in range(10)}
_ALPHABET = {chr(ord('a') + i)
             for i in range(26)} | {chr(ord('A') + i) for i in range(26)}
_ID_START = {'_'} | _ALPHABET
_ID_REST = {'_'} | _ALPHABET | _DIGITS


def is_identifier(s: str) -> bool:
    return s and s[0] in _ID_START and all(map(lambda x: x in _ID_REST, s[1:]))


def dump(d: Object, fp: IWriteable) -> None:
    fp.write('<!zml 0.1>\n')
    _dump(d, fp, 0)


def dumps(d: Object) -> str:
    ss = OutStringStream()
    dump(d, ss)
    return ss.get_str()


def to_zml_str(s: str) -> str:
    a = ['"']
    for i in s:
        if i == '`':
            a.append('``')
        elif i == '\n':
            a.append('`n')
        elif i == '\t':
            a.append('`t')
        elif i == '\b':
            a.append('`b')
        elif i == '\r':
            a.append('`r')
        elif i == '"':
            a.append('`"')
        else:
            a.append(i)
    a.append('"')
    return ''.join(a)


indent = ' ' * 4


def _dump(elem: Any, fp: IWriteable, level: int) -> None:
    if isinstance(elem, dict):
        if not elem:
            fp.write(indent * level + 'empty_obj\n')
            return
        for k, v in elem.items():
            if not is_identifier(k):
                raise RuntimeError()
            fp.write(indent * level + f'<{k}>')
            if not (isinstance(v, (int, float, bool, str)) or v is None):
                fp.write('\n')
            _dump(v, fp, level + 1)
            if not (isinstance(v, (int, float, bool, str)) or v is None):
                fp.write(indent * level)
            fp.write(f'</{k}>\n')
    elif isinstance(elem, list):
        if not elem:
            fp.write(indent * level + 'empty_arr\n')
            return
        for i in elem:
            fp.write(indent * level + f'<>')
            if not (isinstance(i, (int, float, bool, str)) or i is None):
                fp.write('\n')
            _dump(i, fp, level + 1)
            if not (isinstance(i, (int, float, bool, str)) or i is None):
                fp.write(indent * level)
            fp.write(f'</>\n')
    elif isinstance(elem, bool):
        fp.write(' true ' if elem else ' false ')
    elif isinstance(elem, (int, float)):
        fp.write(' ' + str(elem) + ' ')
    elif elem is None:
        fp.write(' null ')
    elif isinstance(elem, str):
        fp.write(' ' + to_zml_str(elem) + ' ')
    else:
        raise RuntimeError()


def load(fp: IReadable) -> Object:
    """Summary line.

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
    arg2 : str
        Description of arg2

    Returns
    -------
    bool
        Description of return value

    """
    return ZmlReader(fp).read()


def loads(s: str) -> Object:
    ss = InStringStream(s)
    return load(ss)
