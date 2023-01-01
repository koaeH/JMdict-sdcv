def subscript(n):
    return str.join(str(), [ chr(0x2080 + (ord(c) & 0xF)) for c in str(n) ])

def laconical(s, n):
    return f"{s[:n - 3].strip()}..." if len(s) > n else s

def normalize(s):
    if s:
        n = ord(next(reversed(s)))

        if n in [ 0x2C, 0x2E, 0x3001, 0x3002, ]:
            return f"{s[:-1]}."

        return f"{s}."

    return s
