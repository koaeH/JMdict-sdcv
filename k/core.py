import k
import k.util

from multiprocessing import Process, Queue
from signal import signal, SIGINT, SIG_DFL

class Task(Process):
    def __init__(self, settings, data, quid):
        super(Task, self).__init__()

        self.settings, self.data, self.quid = settings, data, quid

        signal(SIGINT, SIG_DFL)
        self.queue = Queue()
        self.daemon = 1

    def run(self):
        while self.quid:
            self.queue.put(self.do(self.quid.pop(), self.data))

class TaskManager:
    def __init__(self, settings, task, data):
        self.p, self.data = task, data

        self.settings = settings

    def do(self, ab):
        u = [ self.p(self.settings, self.data, q) for q in k.util.assign(ab, 8) ]

        for p in u:
            p.start()

        m = [ * u ]

        a = []
        while m:
            for p in u:
                while not p.queue.empty():
                    a.append(p.queue.get())

                if not p.is_alive():
                    if p in m:
                        m.remove(p)

        return a

class Cantatio:
    def __init__(self, config): self.settings = config

    def do(self, entry, data):
        raise NotImplementedError

class Monstra:
    def __init__(self, settings, ko, is_input = 0):
        self.ko, self.is_input = ko, is_input

        self.settings = settings

    def display(self, n, m, w = 24):
        i = int(min(w, n / m * w) if not self.is_input else max(0, (m - n) / m * w))

        s = "\r[%s]" % str.join(str(), [ chr(0xB7) * i, chr(32) * (w - i) ])

        sys.stderr.write((f"{s} {self.ko}" if self.ko else str(s)))

    @classmethod
    def cleanup(self, p):
        def w(self, * a, ** kwa):
            wp = p(self, * a, ** kwa)

            if not self.is_input:
                self.display(1, 1)

                sys.stderr.write(chr(0x0A))

            return wp

        return w

import sys
