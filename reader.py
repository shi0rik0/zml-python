
from io import TextIOWrapper


class Reader:
    _BUFFER_SIZE = 4096

    def __init__(self, readable: TextIOWrapper):
        self._file = readable
        self._buffer = 'x'
        self._offset = 1
        self._piece = []

    def read_char(self) -> str:
        if self._buffer == '':
            return ''
        if self._offset == len(self._buffer):
            self._buffer = self._file.read(self._BUFFER_SIZE)
            if self._buffer == '':
                return ''
            self._offset = 0
        ch = self._buffer[self._offset]
        self._piece.append(ch)
        self._offset += 1
        return ch

    def go_back(self) -> None:
        self._offset -= 1
        self._piece.pop()

    def cut(self) -> str:
        s = ''.join(self._piece)
        self._piece = []
        return s
