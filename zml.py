from io import TextIOWrapper
from typing import Any, Dict, List, Tuple
from lexer import Lexer


class ZmlReader:
    _TERMINATORS = {Lexer.Token.BOOL, Lexer.Token.INT,
                    Lexer.Token.FLOAT, Lexer.Token.NULL, Lexer.Token.STRING}

    def __init__(self, readable: TextIOWrapper):
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
