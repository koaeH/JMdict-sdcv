import os, sys

import tarfile, tempfile, json, struct, time

INFO, HEAD, DATA = [ f"main.{s}" for s in [ "ifo", "idx", "dict" ] ]

def main(a):
    doku = next(iter(a))
    data = json.load(open(doku))
    base = next(iter(os.path.splitext(os.path.basename(doku))))

    path = tempfile.mkdtemp()

    with open(os.path.join(path, INFO), "w+", encoding="UTF-8") as a, \
         open(os.path.join(path, HEAD), "wb")                   as b, \
         open(os.path.join(path, DATA), "wb")                   as c:

         m = 0
         u = 0
         for head, body in data:
            n  = c.write(body.encode("UTF-8"))
            u += b.write(head.encode("UTF-8"))
            u += b.write(struct.pack('>B', 0))
            u += b.write(struct.pack(">I", m))
            u += b.write(struct.pack(">I", n))

            m += n

         a.write("StarDict's dict ifo file\n")

         for k, v in (("version", "2.4.2"), ("bookname", base),
                      ("description", "github.com/koaeH/JMdict-sdcv"),
                      ("date", time.strftime("%Y-%m-%d")),
                      ("sametypesequence", 'm'),
                      ("wordcount", len(data)),
                      ("idxfilesize", u)):
            a.write(f"{k}={v}\n")

    with tarfile.open(f"{base}.tar.gz", "w:gz") as ark:
        ark.add(path, base)
