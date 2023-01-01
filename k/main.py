import k

import sys, argparse

def main(a):
    p = argparse.ArgumentParser(exit_on_error=0, add_help=0)
    o = p.add_subparsers(dest="ars")

    for ko in k.COMMANDS:
        o.add_parser(ko, add_help=0)

    try:
        q, a = p.parse_known_args(a)
        name = s = k.COMMANDS[q.ars]
        if not a:
            raise Exception
    except:
        print('😶', file=sys.stderr)

        quit((181))

    from k.util import invoke

    m = invoke(s)

    m.main(a)
