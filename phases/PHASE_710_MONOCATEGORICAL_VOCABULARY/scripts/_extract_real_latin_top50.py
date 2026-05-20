"""Extract actual top-50 word-forms from Codicillus to verify our hand-curated list.
If significant divergence, flag and re-run main test with real data.
"""
from __future__ import annotations
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
COD_PATH = ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt'
MES_PATH = ROOT / 'sources' / 'mesue_grabadin' / 'mesue_grabadin_latin_full.txt'


def top_n_words(path, n=50):
    text = Path(path).read_text(encoding='utf-8', errors='replace').lower()
    words = re.findall(r'[a-zA-Z]+', text)
    return Counter(words).most_common(n), len(words)


for label, path in [("Codicillus", COD_PATH), ("Mesue", MES_PATH)]:
    if not path.exists():
        print(f"{label}: missing {path}")
        continue
    top, total = top_n_words(path, 50)
    print(f"\n=== {label} top-50 (out of {total} total words) ===")
    for i, (w, c) in enumerate(top, 1):
        print(f"  {i:2d}. {w:<15} {c}")
