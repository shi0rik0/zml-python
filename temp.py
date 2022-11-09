
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
