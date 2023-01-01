from k.core import Cantatio

import json, queue

INTERPUNCTUS = chr(0x30FB)

def reach_x(xref, data):
    nonkanae, readings, _ = data

    a  = xref in nonkanae
    a |= xref in readings

    return a, xref

def reach_x_y(xref, data):
    nonkanae, readings, origines = data

    x, y = xref.split(INTERPUNCTUS)

    if y.isdigit():
        y = int(y)

        m = []
        if x in nonkanae: m += nonkanae[x]
        if x in readings: m += readings[x]

        try:
            b, t = [], []

            for q in set(m):
                if origines[q]:
                    entry = json.loads(origines[q])

                    i, s = 0, 0
                    for p, (c, _) in enumerate(entry["senses"], start=1):
                        if c == y:
                            i = p

                        if c != p:
                            s = 1

                    if not i and s:
                        raise KeyError

                    b += [ i ]
                    t += [ s ]

            if b:
                if any(t):
                    if all(map(lambda e: e == b[0], b)):
                        return 1, INTERPUNCTUS.join([
                            x, str(next(iter(b)))
                        ])

                if any(b):
                    return 1, xref
        except KeyError:
            pass
    else:
        if x in nonkanae and y in readings:
            return 1, xref

    return 0, xref

def reach_x_y_z(xref, data):
    nonkanae, readings, origines = data

    x, y, z = xref.split(INTERPUNCTUS)

    try:
        z = int(z)

        if x in nonkanae and y in readings:
            b, t = [], []

            m = [ e for e in readings[y] if e in nonkanae[x] ]

            for q in m:
                if origines[q]:
                    entry = json.loads(origines[q])

                    i, s = 0, 0
                    for p, (c, _) in enumerate(entry["senses"], start=1):
                        if c == z:
                            i = p

                        if c != p:
                            s = 1

                    if not i and s:
                        raise KeyError

                    b += [ i ]
                    t += [ s ]

            if b:
                if any(t):
                    if all(map(lambda e: e == b[0], b)):
                        return 1, INTERPUNCTUS.join([
                            x, y, str(next(iter(b)))
                        ])

                if any(b):
                    return 1, xref
    except (ValueError, KeyError):
        pass

    return 0, xref

PATH_FINDERS = [
    reach_x,
    reach_x_y,
    reach_x_y_z,
]

class Pass(Cantatio):
    def do(self, entry, data):
        for _, sense in entry["senses"]:
            for o in [ "xrefs", "ants" ]:
                if o in sense:
                    a = []
                    for xref in sense[o]:
                        m = xref.count(INTERPUNCTUS)

                        if m <= 2:
                            p = PATH_FINDERS[m]

                            is_reachable, v = p(xref, data)
                            if is_reachable:
                                a.append(v)

                    sense[o] = a
