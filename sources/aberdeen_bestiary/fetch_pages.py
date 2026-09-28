"""Fetch Aberdeen Bestiary (Aberdeen UL MS 24) folio pages with caching.

Usage:
    python fetch_pages.py                 # fetch all f1r..f103v
    python fetch_pages.py f7r f1r ...     # fetch only listed folios
    python fetch_pages.py --url URL NAME  # fetch an arbitrary URL into html/NAME.html

Raw HTML is cached under html/; a page already cached is never refetched.
A >=1.5 s delay separates live requests.
"""
import os
import sys
import time

import requests

BASE = "https://www.abdn.ac.uk/bestiary/ms24/"
HERE = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(HERE, "html")
UA = ("VoynichResearch-AberdeenBestiaryCorpus/1.0 "
      "(academic text-corpus build; +https://github.com/epilectrik/voynich; "
      "polite crawler, 1 req per 1.5 s, cached)")
DELAY = 1.5

os.makedirs(HTML_DIR, exist_ok=True)
_session = requests.Session()
_session.headers.update({"User-Agent": UA})
_last = [0.0]


def fetch(url, name):
    path = os.path.join(HTML_DIR, name + ".html")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path, "cached"
    wait = DELAY - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    r = _session.get(url, timeout=60)
    _last[0] = time.time()
    if r.status_code != 200:
        return None, "HTTP %d" % r.status_code
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path, "fetched"


def all_folios():
    out = []
    for n in range(1, 104):
        for s in ("r", "v"):
            out.append("f%d%s" % (n, s))
    return out


def main(argv):
    if len(argv) >= 3 and argv[0] == "--url":
        p, st = fetch(argv[1], argv[2])
        print(argv[2], st, p, flush=True)
        return
    folios = argv if argv else all_folios()
    for f in folios:
        p, st = fetch(BASE + f, f)
        print(f, st, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
