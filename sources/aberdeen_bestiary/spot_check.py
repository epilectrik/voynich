"""Spot-check extraction: compare stored latin_raw / latin_norm against the page's
transcription panel read by an independent path (plain regex over the cached HTML, no
BeautifulSoup), and show the start of the English translation panel to confirm it is
not what was extracted. Output: spot_check.txt
"""
import html as htmlmod
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = ["f1r", "f7r", "f18v", "f55v", "f94r", "f103v", "f6r", "f45r"]
ALL = "--all" in sys.argv   # audit every page; prints only the summary line
if ALL:
    PAGES = ["f%d%s" % (n, s) for n in range(1, 104) for s in "rv"]
rows = {r["folio"]: r for r in json.load(open(os.path.join(HERE, "aberdeen_pages.json"), encoding="utf-8"))}


def panel(src, cls):
    m = re.search(r'<div class="%s">\s*<h2>[^<]*</h2>(.*?)</div>' % cls, src, re.S)
    if not m:
        return None
    t = re.sub(r"<[^>]+>", "", m.group(1))
    return re.sub(r"\s+", " ", htmlmod.unescape(t)).strip()


out = []
bad = []
for f in PAGES:
    src = open(os.path.join(HERE, "html", f + ".html"), encoding="utf-8", errors="replace").read()
    shown = panel(src, "transcription")
    trans = panel(src, "translation")
    r = rows[f]
    stored = re.sub(r"\s+", " ", r["latin_raw"]).strip()
    same = (shown or "") == stored
    if not same:
        bad.append(f)
    out.append("=" * 100)
    out.append("%s  (%s)  n_words=%d  identical_to_page_panel=%s" % (f, r["title"], r["n_words"], same))
    out.append("  PAGE transcription panel : %r" % ((shown or "<no transcription panel>")[:200]))
    out.append("  STORED latin_raw         : %r" % (stored[:200]))
    out.append("  STORED latin_norm        : %r" % (r["latin_norm"][:200]))
    out.append("  PAGE translation panel   : %r" % ((trans or "<no translation panel>")[:120]))
out.append("=" * 100)
out.append("pages where stored raw != page panel: %s" % (bad or "none"))
txt = "\n".join(out)
if ALL:
    print("audited %d pages; %s" % (len(PAGES), out[-1]))
else:
    open(os.path.join(HERE, "spot_check.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)
