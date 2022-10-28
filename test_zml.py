from zml import ZmlReader


def test_zml():
    t = {'a': 114514, 'b': 1919.81, 'c': True,
         'd': False, 'e': None, 'f': ['hello\t', 'world!']}
    t['g'] = t.copy()
    with open('test.zml') as f:
        reader = ZmlReader(f)
        assert reader.read() == t
