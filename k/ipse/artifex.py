import k
import k.core

import k.util.maya
import k.util.text

from k.core import TaskManager, Task, Monstra
from k.util import invoke

import lxml.etree, xml.dom, xml.etree.ElementTree
import collections, itertools, json, struct, time

from unicodedata import normalize as n_of

LANG = "{%s}lang" % xml.dom.XML_NAMESPACE

class Rudimentum(Monstra):
    def __init__(self, settings):
        super(Rudimentum, self).__init__(settings, chr(0x1F516), is_input=1)

    @Monstra.cleanup
    def get(self):
        nonkanae = collections.defaultdict(list)
        readings = collections.defaultdict(list)
        origines = []

        with open(self.settings["path"], "rb") as f:
            for i, (_, n) in enumerate(lxml.etree.iterparse(f, tag = [ "entry" ])):
                for c in n:
                    if c.tag in [ "k_ele", "r_ele" ]:
                        for e in c:
                            "keb" == e.tag and nonkanae[n_of("NFKC", e.text)].append(i)
                            "reb" == e.tag and readings[n_of("NFKC", e.text)].append(i)

                origines.append((i, lxml.etree.tostring(n)))

                if i % 8192: self.display(i, 2E5)

                n.clear()

        return nonkanae, readings, origines

class Processor(Monstra):
    def __init__(self, settings, name, task):
        super(Processor, self).__init__(settings, name)

        self.task = task
        self.size = 8192

    @Monstra.cleanup
    def do(self, quid, data):
        m = TaskManager(self.settings, self.task, data)
        o = iter(quid)
        a = []

        while 1:
            b = list(itertools.islice(o, self.size))
            if not b:
                break

            self.display(len(a), len(quid))

            a += m.do(b)

        return a

    def ab(self, o, nonkanae, readings):
        data = nonkanae, readings, [ s for _, s in sorted(o) ]

        return self.do(o, data)

    def ex(self, o, nonkanae, readings):
        ko = origines = [ source for __, source in sorted(o) ]

        q  = list(nonkanae.items())
        q += list(readings.items())

        doku = []
        for head, indices in q:
            u = list(filter(lambda i: ko[i], indices))
            if u:
                doku.append((head, u))

        return self.do(doku, (nonkanae, readings, ko))

class CompositioTask(Task):
    def do(self, origo, _):
        i, entry_xml_source = origo

        entry = { s : [] for s in [ "k_eles", "r_eles", "senses" ] }

        for e in xml.etree.ElementTree.fromstring(entry_xml_source):
            if "k_ele" == e.tag:
                k_ele = {}

                for c in e:
                    if "keb" == c.tag:
                        k_ele["keb"] = n_of("NFKC", c.text)
                    else:
                        s = f"{c.tag}s"

                        if s in k_ele:
                            k_ele[s].append(c.text)
                        else:
                            k_ele[s] = [ c.text ]

                entry["k_eles"].append(k_ele)
            elif "r_ele" == e.tag:
                r_ele = {}

                for c in e:
                    if "reb" == c.tag:
                        r_ele["reb"] = n_of("NFKC", c.text)
                    elif "re_nokanji" == c.tag:
                        r_ele["re_nokanji"] = 1
                    else:
                        s = f"{c.tag}s"

                        if s in r_ele:
                            r_ele[s].append(c.text)
                        else:
                            r_ele[s] = [ c.text ]

                entry["r_eles"].append(r_ele)
            elif "sense" == e.tag:
                sense = {}

                for c in e:
                    if "gloss" == c.tag:
                        gloss = { "text" : c.text, "lang" : c.attrib[LANG] if LANG in c.attrib else "eng" }

                        if "g_type" in c.attrib: gloss["g_type"] = c.attrib["g_type"]

                        if "glossae" in sense:
                            sense["glossae"].append(gloss)
                        else:
                            sense["glossae"] = [ gloss ]
                    elif "lsource" == c.tag:
                        lsource = {
                            "lang" : c.attrib[LANG] if LANG in c.attrib else "eng",
                            "ls_wasei" : "ls_wasei" in c.attrib,
                            "text" : c.text,
                        }

                        if "ls_full" in c.attrib:
                            lsource["ls_full"] = c.attrib["ls_full"]

                        if "lsources" in sense:
                            sense["lsources"].append(lsource)
                        else:
                            sense["lsources"] = [ lsource ]
                    else:
                        s = f"{c.tag}s"

                        if s in sense:
                            sense[s].append(c.text)
                        else:
                            sense[s] = [ c.text ]

                entry["senses"].append(sense)

        entry["senses"] = [ (n, q) for n, q in enumerate(entry["senses"], start=1) ]

        return i, json.dumps(entry)

class Compositio(Processor):
    def __init__(self, settings):
        super(Compositio, self).__init__(settings, chr(0x1F33F), CompositioTask)

class ModeratrixTask(Task):
    def __init__(self, settings, data, quid):
        super(ModeratrixTask, self).__init__(settings, data, quid)

        self.passes = []
        for s, c in settings["moderatrix"]["passes"]:
            self.passes.append(invoke(s).Pass(c))

    def do(self, quid, data):
        i, entry_json_source = quid

        entry = json.loads(entry_json_source)

        for p in self.passes: p.do(entry, data)

        if entry["senses"]:
            return i, json.dumps(entry)
        else:
            return i, None

class Moderatrix(Processor):
    def __init__(self, settings):
        super(Moderatrix, self).__init__(settings, chr(0x1F342), ModeratrixTask)

class PrecantrixTask(Task):
    def __init__(self, settings, data, quid):
        super(PrecantrixTask, self).__init__(settings, data, quid)

        self.passes = []
        for s, c in self.settings["precantrix"]["passes"]:
            self.passes.append(invoke(s).Pass(c))

    def do(self, quid, data):
        i, entry_json_source = quid

        if entry_json_source:
            entry = json.loads(entry_json_source)

            for p in self.passes:
                p.do(entry, data)

            entry_json_source = json.dumps(entry)

        return i, entry_json_source

class Precantrix(Processor):
    def __init__(self, settings):
        super(Precantrix, self).__init__(settings, chr(0x02728), PrecantrixTask)

class MonstriferTask(Task):
    def __init__(self, settings, data, quid):
        super(MonstriferTask, self).__init__(settings, data, quid)

    __getattr__ = lambda self, uh: self.settings["monstrifer"][uh]

    def _(self, c, s):
        if self.ornamenta & 0b11:
            n = self.khromikon[c]
            s = f"\033[1;38;5;{n}m{s}\033[0m"
            if self.ornamenta & 1 == 0:
                s = f"\033[2m{s}"

        return s

    def render_head(self, s, n, has_multiple_entries):
        if has_multiple_entries:
            s += k.util.text.subscript(n)

        return self._(3, s)

    def render_freq(self, n):
        i = round(max(0, min(1, n)) * (len(self.frequency) - 1))

        return self._(i, chr(self.frequency[i]))

    def render_nota(self, notae, s):
        s = k.util.text.normalize(s)

        i = len(notae)
        if s in notae:
            i = notae.index(s)
        else:
            notae.append(s)

        return self._(6, self.clavicula[i])

    def render_reading(self, notae, entry):
        s = str()

        if "ko_frequency" in entry:
            s += f'{self.render_freq(entry["ko_frequency"])} {entry["reb"]}'
        else:
            s += f'\u3000{entry["reb"]}'

        if "re_nokanji" in entry:
            s += f' {self.render_nota(notae, "not a true reading of this 漢字")}'

        if "re_infs" in entry:
            s += f' {str.join(chr(32), [ self.render_nota(notae, s) for s in entry["re_infs"] ])}'

        return s

    def render_nonkana(self, notae, entry):
        s = str()

        if "ko_frequency" in entry:
            s += f'{self.render_freq(entry["ko_frequency"])} {entry["keb"]}'
        else:
            s += f'\u3000{entry["keb"]}'

        if "ke_infs" in entry:
            s += f' {str.join(chr(32), [ self.render_nota(notae, s) for s in entry["ke_infs"] ])}'

        return s

    def render_lsource(self, lsource):
        s = f'From {lsource["lang"].title()}.'

        if "text" in lsource:
            if lsource["text"]:
                s += " '%s'" % lsource["text"]

        if "ls_wasei" in lsource:
            if lsource["ls_wasei"]:
                s += ", 和製"

        return s

    def render_gloss(self, gloss):
        s = str()
        if "g_type" in gloss:
            s += self._(1, k.util.text.normalize(gloss["g_type"]))
            s += chr(0x20)

        s += gloss["text"]

        return s

    def render_sense(self, notae, sense):
        data = str()

        if "poss"     in sense: data += self._(5, ", ".join(sense["poss"]))
        if "fields"   in sense: data += f' {" ".join([ self._(6, f"[{q}]") for q in sense["fields"] ])}'
        if "miscs"    in sense: data += f' {" ".join([ self._(1, f"[{q}]") for q in sense["miscs" ] ])}'
        if "dials"    in sense: data += f' {" ".join([ self._(6, f"/{q}/") for q in sense["dials" ] ])}'
        if "s_infs"   in sense: data += f' {" ".join([ self._(4, f"({q})") for q in sense["s_infs"] ])}'
        if "lsources" in sense:
            data += chr(0x20)

            sosu = []
            for lsource in sense["lsources"]:
                sosu.append(self.render_nota(notae, self.render_lsource(lsource)))

            data += chr(0x20).join(sosu)

        if data:
            data += " → "

        data += " ¦ ".join(self.render_gloss(gloss) for gloss in sense["glossae"])

        return data

    def do(self, quid, data):
        head, entry_indices = quid

        nonkanae, readings, origines = data

        has_multiple_entries = len(entry_indices) > 1

        body, notae = [], []
        for entry_no, index in enumerate(entry_indices, start=1):
            entry = json.loads(origines[index])

            s = f"\u3000{self.render_head(head, entry_no, has_multiple_entries)}\n"

            if head in nonkanae:
                for r_ele in entry["r_eles"]:
                    s += f'{self.render_reading(notae, r_ele)}\n'
            else:
                for k_ele in entry["k_eles"]:
                    s += f'{self.render_nonkana(notae, k_ele)}\n'

            s += chr(0x0A)

            base = []
            has_multiple_senses = len(entry["senses"]) > 1
            for sense_no, (_, sense) in enumerate(entry["senses"], start=1):
                doku = str()
                if has_multiple_senses:
                    doku += f"{sense_no} ▶ "

                doku += self.render_sense(notae, sense)

                refs = sense["xrefs"] if "xrefs" in sense else []
                ants = sense["ants"]  if "ants"  in sense else []

                if refs or ants:
                    a = []
                    refs and a.append("[%s %s]" % (self._(3, "see"), " | ".join(refs)))
                    ants and a.append("[%s %s]" % (self._(0, "cf."), " | ".join(ants)))

                    doku += f' ¦ {", ".join(a)}'

                base.append(doku)

            if max([ k.util.maya.pixe_of(e) for e in base ]) > 80:
                q = " ‖ ".join(base)
                p = k.util.maya.pixe_of(q)

                a = []
                for n in self.aesthetic[p < 144]:
                    try:
                        m = k.util.maya.of(q, n)
                        if m:
                            x = k.util.maya.pixe_of(next(reversed(m)))

                            a.append((max(0, (x - n)), m))

                            if n - x < n // 3: break
                    except BufferError:
                        pass

                _, base = next(iter(sorted(a)))

            s += chr(0x0A).join(base)
            s += chr(0x0A)

            body.append(s)

        doku = chr(0x0A).join(body)

        if notae:
            doku += "\n━━━━\n"
            for nota in reversed(sorted(notae, key=len)):
                doku += f"   {self.render_nota(notae, nota)} {nota}\n"

        doku = doku.strip(chr(0x0A))

        return head, doku

class Monstrifer(Processor):
    def __init__(self, settings):
        super(Monstrifer, self).__init__(settings, chr(0x1F31F), MonstriferTask)

import sys, os

class Make:
    def __init__(self, settings):
        self.p = settings["path"]

        self.rudimentum = Rudimentum(settings)
        self.compositio = Compositio(settings)
        self.moderatrix = Moderatrix(settings)
        self.precantrix = Precantrix(settings)
        self.monstrifer = Monstrifer(settings)

    def do(self):
        nonkanae, readings, o = self.rudimentum.get()

        a = self.compositio.ab(o, nonkanae, readings)
        b = self.moderatrix.ab(a, nonkanae, readings)
        c = self.precantrix.ab(b, nonkanae, readings)
        d = self.monstrifer.ex(c, nonkanae, readings)

        u = "%s.o" % next(iter(os.path.splitext(os.path.basename(self.p))))

        with open(u, "w+") as f: f.write(json.dumps(sorted(d, key=(
            lambda e: str.upper(next(iter(e)))
        ))))

def main(a):
    Make({ ** k.SETTINGS, "path" : next(iter(a)) }).do()
