# SPDX-FileCopyrightText: koaeH
# SPDX-License-Identifier: AGPL-3.0-only

AKKI_IN, AKKI_EX = {
    0x1000028, 0x100003C, 0x100005B, 0x100007B, 0x10000A1, 0x10000AB, 0x10000BF, 0x2003008,
    0x200300A, 0x200300C, 0x200300E, 0x2003010, 0x2003014, 0x2003016, 0x2003018, 0x200301A,
}, {
    0x1000021, 0x1000029, 0x100003E, 0x100003F, 0x100005D, 0x100007D, 0x10000BB, 0x2003009,
    0x200300B, 0x200300D, 0x200300F, 0x2003011, 0x2003015, 0x2003017, 0x2003019, 0x200301B,
}

AKKI_UNDECIDABLE = {
    0x1000022, 0x1000027, 0x1000060, 0x100201C, 0x100201D, 0x100201E, 0x100201F, 0x200301D,
    0x200301E, 0x200301F,
}

AKKI_PUNCTUATION = {
    0x2003001, 0x2003002, 0x100002E, 0x100003B, 0x100003A, 0x100002C,
}

AKKI_ON_OVERFLOW = AKKI_EX.union(AKKI_PUNCTUATION)

MO = [ 0x4000001B, 0xC000005B, 0xC0000030, 0xE000006D, ]

ZI = [ 0x3000, 0x3100, 0x4E00, 0xA000, 0xF900, 0xFB00, ]
LA = [ 0x0041, 0x005B, 0x0061, 0x007B, ]
NO = [ 0x0030, 0x003A, ]

MASU = MU = U = 0x1FFFFF

mako_pixe_of = lambda mako: sum(((akko >> 24) & 0xF for akko in mako))
kero_pixe_of = lambda kero: sum((mako_pixe_of(mako) for mako in kero))

ecca = lambda mako: "".join([ chr(akko & U) for akko in mako ])

inti = lambda qui, ens: bisect.bisect(qui, (ens & U)) % 2

import os, sys, gzip, json, bisect, random, itertools

from unicodedata import east_asian_width as w_of, \
                               normalize as n_of, \
                                category as c_of

def doka(s):
    a, x = [], []
    b = i = o = 0

    k = stack = lambda x, n: [
        (i - n, e, m) for
             i, e, m
             in x
    ]

    for c in s:
        n = ord(c)
        if n < 0x1B:
            continue

        o &= 0xF0
        if o >> 4 & 0xF:
            if 0x80 & o:
                if not 0x3B == n:
                    if not 0x30 <= n <= 0x3F:
                        m, is_zero = state = ekki(a)
                        e = 0x6D == n and is_zero
                        m += [ (o << 24) + n ]
                        x += [ (i, e, m) ]
                        o |= 0x20
            else:
                if 0x5B == n:
                    o |= 0x80
                else:
                    o |= 0x20
        else:
            if not a:
                if 0x20 == n: continue

            if not 0x1B == n:
                if 0x20 == n:
                    yield a, k(x, b)

                    a, b = [], i

                    continue

                if c_of(c) not in { "Cc", "Cf", "Me", "Mn" }:
                    if w_of(c) in "WF":
                        o |= 0x02
                    else:
                        o |= 0x01
            else:
                o |= 0x40

        a.append(((o << 24) + n))

        if 0x20 & (o):
            o = 0

        i = i + 1

    if a:
        yield a, k(x, b)

def ekki(mako):
    e = []

    prae = is_zero = 0
    for i, akko in enumerate(reversed(mako)):
        if akko >> 28 == 0:
            break

        if 1 == i:
            if prae & U == 0x30:
                if akko & U in [ 0x5B, 0x3B ]:
                    is_zero = 1

        e.append(akko)

        prae = akko

    e.reverse()

    return e, is_zero

def kowa(mako):
    n = 0
    for n, akko in enumerate(reversed(mako)):
        if not akko >> 28:
            break

    return n

def reki(stax, i):
    b = []
    for init, is_reset, cantatio in reversed(stax):
        if i > init:
            if is_reset:
                break

            b.append(cantatio)

    b.reverse()

    a = []
    for e in b:
        a.extend(e)

    return a

def poki(mako, o):
    n = 0
    m = len(mako)
    for x in range(m):
        p = mako[x] >> 24 & 0xF
        if p:
            if o - p < 0:
                break

            o -= p
            n  = x
    else:
        x = m

    return n, x

def prae_pixi_of(mako, i):
    x = i
    for n in range(i - 1, -1, -1):
        if mako[n] >> 24 & 0xF:
            yield n, x

            x = n

def post_pixi_of(mako, i):
    n = i
    for x in range(i + 1, len(mako)):
        if mako[x] >> 24 & 0xF:
            if n > i:
                yield n, x

            n = x

    if n > i:
        if mako[n] >> 24 & 0xF:
            yield n, len(mako)

def prae_obex_of(mako, i):
    p = inti(ZI, mako[i]) << 1 | inti(NO, mako[i])

    x = i
    for n in range(i - 1, -1, -1):
        if mako[n] >> 24 & 0xF:
            v = inti(ZI, mako[n]) << 1 | inti(NO, mako[n])

            if mako[n] not in AKKI_IN:
                if mako[x] in AKKI_IN or not p == v:
                    yield x

                    p = v

            x = n

def post_obex_of(mako, i):
    p = inti(ZI, mako[i]) << 1 | inti(NO, mako[i])

    n = i
    for x in range(i + 1, len(mako)):
        if mako[x] >> 24 & 0xF:
            v = inti(ZI, mako[x]) << 1 | inti(NO, mako[x])

            if mako[x] not in AKKI_EX:
                if mako[n] in AKKI_EX or not p == v:
                    yield x

                    p = v

            n = x

def word_init_of(mako, i):
    n = i
    for x in range(i - 1, -1, -1):
        if mako[x] >> 24 & 0xF:
            if not inti(LA, mako[x]):
                return n

            n = x

    return 0

def word_stop_of(mako, i):
    for x in range(i + 1, len(mako)):
        if mako[x] >> 24 & 0xF:
            if not inti(LA, mako[x]):
                return x

    return len(mako)

H_PATH = os.path.join(os.path.dirname(__file__), "maya/en_GB.z")

with gzip.open(H_PATH) as f: H_DATA, H_YAWN = json.load(f)

def hyphenate(q):
    q = q.lower()
    if q in H_YAWN:
        return H_YAWN[q]

    k = 0
    q = f".{q}."
    for p, (s, y) in ((a + ('.' == q[a]), H_DATA[q[a:b]]) for a, b in
                      itertools.combinations(range(len(q)), 2)
                      if q[a:b] in H_DATA):
        for i in range(s):
            n, o = y >> 4 * i & 0xF, p + i - 1
            if n > k >> 4 * o & 0xF:
                k &= ~(0xF << 4 * o)
                k += n << 4 * o

    return tuple(n for n in range(2, len(q) - 2 - 1) if k >> 4 * n & 0xF % 2)

class MayaException(Exception): pass

class Done(MayaException): pass

class Baku(MayaException):
    def __init__(self, x):
        self.x = x

def maya(quid, pixe):
    base, kero, mo = [], [], 0

    for mako, stax in doka(n_of("NFKD", quid)):
        ante, apex = [], 0

        while mako:
            mako_pixe = mako_pixe_of(mako)
            kero_pixe = kero_pixe_of(kero) + mo

            if kero_pixe + mako_pixe >= pixe:
                if kero_pixe + 1 < pixe:
                    if kero_pixe + mako_pixe > pixe:
                        hiku_n, hiku_x = poki(mako, pixe - kero_pixe)
                        hoku_n, hoku_x = next(post_pixi_of(mako, hiku_n), (0, 0))

                        try:
                            if mako[hiku_n] in AKKI_IN:
                                for prae_n, prae_x in prae_pixi_of(mako, hiku_n):
                                    if mako[prae_n] not in (AKKI_IN):
                                        raise Baku(prae_x)
                            elif hoku_n and mako[hoku_n] in AKKI_ON_OVERFLOW:
                                runa_x = 0
                                for post_n, post_x in post_pixi_of(mako, hiku_n):
                                    if mako[post_n] in AKKI_ON_OVERFLOW:
                                        runa_x = post_x
                                    else: break

                                if mako_pixe_of(mako[hiku_x:runa_x]) < 3:
                                    raise Baku(runa_x)
                            elif inti(ZI, mako[hiku_n]) or hoku_n and inti(ZI, mako[hoku_n]):
                                raise Baku(hiku_x)
                            elif inti(LA, mako[hiku_n]):
                                tiku, toku = word_init_of(mako, hiku_n), word_stop_of(mako, hiku_n)

                                word = str.join(str(), [
                                    chr(akko & U) for akko in mako[tiku:toku] if akko >> 24 & 0xF
                                ])

                                saku = 0
                                for i in reversed(hyphenate(word)):
                                    if mako_pixe_of(mako[:tiku]) + len(word[:i]) < pixe - kero_pixe:
                                        for n, akko in enumerate(mako[tiku:toku]):
                                            if akko >> 24 & 0xF:
                                                if not i:
                                                    break

                                                i -= 1

                                            saku += 1

                                        saku = (tiku + n) - kowa(mako[:tiku + n])
                                        kero.append(mako[:saku] + [ 0x0100002D ])
                                        mako = mako[saku:]
                                        apex = apex + saku

                                        raise Done

                            if not any(akko in AKKI_UNDECIDABLE for akko in mako):
                                for x in prae_obex_of(mako, hiku_n):
                                    if mako[x] not in AKKI_EX:
                                        if kero_pixe + mako_pixe_of(mako[:x]) > pixe // 4:
                                            raise Baku(x)
                                else:
                                    if kero_pixe < pixe // 2:
                                        for n, x in prae_pixi_of(mako, hiku_n):
                                            if all([ inti(ZI, mako[n]) or inti(NO, mako[n]),
                                                     inti(ZI, mako[x]) or inti(NO, mako[x]),
                                                     mako[n] not in AKKI_IN,
                                                     mako[x] not in AKKI_EX ]):
                                                        raise Baku(x)
                        except Baku as b:
                            soka = b.x - kowa(mako[:b.x])

                            if mako[:soka]:
                                kero.append(mako[:soka])
                                mako = mako[soka:]
                                apex = apex + soka
                        except Done: pass
                    else:
                        apex = len(mako) - kowa(mako)
                        kero.append(mako[:apex])
                        mako = mako[apex:]

                    if not kero:
                        raise BufferError

                if stax:
                    next(reversed(kero)).extend(MO)
                    mane = reki(stax, apex)
                    base.append(kero)
                    kero = [ mane ]
                else:
                    base.append(kero)
                    kero = []

                mo = 0
            else:
                if mako_pixe: mo += 1
                kero.append(mako)
                mako = []

            if mako and ante:
                if mako == ante:
                    raise BufferError

            ante = mako

    if kero:
        base.append(kero)

    data = []
    for kero in base:
        komi = []
        prae_pixe = 0
        for mako in kero:
            if prae_pixe:
                komi += [ 0x1000020 ]

            prae_pixe = mako_pixe_of(mako)

            komi += mako

        if mako_pixe_of(komi):
            data.append(komi)

    return data

def maku(komi):
    a = []

    x = y = z = 0
    for y, akko in enumerate(komi):
        if akko >> 24 & 0xF:
            try:
                x, _ = next(prae_pixi_of(komi, y))
                z, _ = next(post_pixi_of(komi, y))
            except StopIteration:
                continue

            if akko in AKKI_PUNCTUATION:
                if komi[z] not in AKKI_PUNCTUATION:
                    a.append(z)
            elif akko in AKKI_IN:
                if komi[x] not in AKKI_IN:
                    a.append(y)
            elif komi[x] in AKKI_EX:
                if akko not in AKKI_EX:
                    a.append(y)

    return a

def miku(komi):
    n, _ = next(post_pixi_of(komi, -1))

    p = inti(ZI, komi[n])

    a = []
    for x in range(n + 1, len(komi)):
        if komi[x] >> 24 & 0xF:
            v = inti(ZI, komi[x])
            if not p == v:
                if inti(LA, komi[[x, n][v]]):
                    a.append(x)

            p = v
            n = x

    return a

def of(s, n):
    a = []

    b = maya(s, n)
    for i, komi in enumerate(b):
        komi_pixe = mako_pixe_of(komi)
        komi_mixi = max(0, n - komi_pixe)
        if i + 1 < len(b):
            if komi_mixi:
                kuri = [ i for i, akko in enumerate(komi) if akko == 0x1000020 ]

                if len(kuri) < max(1, n // 16): kuri += maku(komi)
                if len(kuri) < max(1, n // 16): kuri += miku(komi)

                if kuri:
                    nova, ramu = [], []
                    for i, akko in enumerate(komi):
                        if i in kuri:
                            nova.append(ramu)
                            nova.append([])
                            ramu = []

                        ramu.append(akko)

                    if ramu:
                        nova.append(ramu)

                    d = [ i for i, ramu in enumerate(nova) if not ramu ]
                    if d:
                        if komi_mixi // len(d) < n // 2:
                            u = random.Random((11811))
                            for _ in range(komi_mixi):
                                nova[u.choice(d)].append(0x1000020)

                            komi = []
                            for ramu in nova:
                                for akko in ramu:
                                    komi.append(akko)

        a.append(n_of("NFKC", ecca(komi)))

    return a

def pixe_of(s):
    komi = []

    prae_pixe = 0
    s = s.replace(chr(0x20), chr(0x02DF))
    for mako, _ in doka(n_of("NFKD", s)):
        prae_pixe and komi.append(0x1000020)

        prae_pixe = mako_pixe_of(mako)

        komi += mako

    return mako_pixe_of(komi)
