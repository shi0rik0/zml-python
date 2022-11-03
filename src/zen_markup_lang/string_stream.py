from typing import List


class OutStringStream:
    _contents: List[str]

    def __init__(self) -> None:
        self._contents = []

    def write(self, s: str) -> int:
        self._contents.append(s)
        return len(s)

    def get_str(self) -> str:
        return ''.join(self._contents)


class InStringStream:
    _str: str
    _i: int

    def __init__(self, s: str) -> None:
        self._str = s
        self._i = 0

    def read(self, size: int) -> str:
        ret = self._str[self._i:self._i+size]
        self._i += size
        return ret
