import sys

def invoke(s):
    try: __import__(s, globals())
    except (ModuleNotFoundError):
        raise

    return sys.modules[s]

def assign(a, n):
    m = len(a)

    if n < m:
        i = m // n
        for p in range(n):
            o = a[p * i : p * i + i]

            if p + 1 == n and i * n < m:
                yield o + a[i * n:]
            else:
                yield o
    else:
        for e in a:
            yield [ e ]
