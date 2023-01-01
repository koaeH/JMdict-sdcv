#!/bin/python3 -BOO

import os, sys

if "__main__" == __name__:
    def k_exception_hook(a, b, c):
        while c.tb_next: c = c.tb_next

        ab = os.path.dirname(__file__)

        if type(b) not in [ KeyboardInterrupt, EOFError ]:
            sys.stderr.write(chr(0xD) + "%(p)s [%(n)+d] %(q)s%(m)s\n" % {
                'p' : os.path.relpath(c.tb_frame.f_code.co_filename, ab),
                'm' : ": ↴\n%s" % b if str(b) else str(),
                'q' : str(type(b).__name__),
                'n' : c.tb_lineno,
            })

    sys.excepthook = k_exception_hook

    from k.main import main

    main(sys.argv[1:])
