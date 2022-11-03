import zen_markup_lang as zml
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def test_zml():
    t = {'a': 114514, 'b': 1919.81, 'c': True,
         'd': False, 'e': None, 'f': ['hello\t', 'world!'], 'h': {}, 'i': []}
    t['g'] = t.copy()
    with open(HERE / 'test.zml') as f:
        assert zml.load(f) == t
    with open(HERE / 'test2.zml', 'w') as f:
        zml.dump(t, f)
    with open(HERE / 'test2.zml') as f:
        assert zml.load(f) == t
