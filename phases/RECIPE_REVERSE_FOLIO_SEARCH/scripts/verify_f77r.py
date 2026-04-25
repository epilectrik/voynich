"""Pull f77r raw lines + III.28.0 recipe text for direct atom-decode verification."""
from __future__ import annotations
import io, sys, json, re
from pathlib import Path
from collections import defaultdict

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

subs = json.loads((ROOT / "phases" / "SISMEL_RECIPE_CORPUS" /
                   "results" / "sismel_subrecipes.json").read_text(encoding="utf-8"))["subrecipes"]
recipe = next(s for s in subs if s["id"] == "III.28.0")

print("=" * 80)
print(f"f77r ↔ III.28.0")
print(f"Title: {recipe.get('title_catalan') or recipe.get('title_latin')}")
print("=" * 80)
print()
print("CATALAN:")
print(recipe.get("catalan", "(none)")[:3500])
print()
print("LATIN (excerpt):")
print(recipe.get("latin", "(none)")[:1500])
print()
print("=" * 80)

tx = Transcript()
morph = Morphology()
para_idx = 0
seq = []
by_line = defaultdict(list)
for t in tx.currier_b():
    if t.folio != "f77r":
        continue
    if t.placement and t.placement.startswith("L"):
        continue
    if t.par_initial and seq:
        para_idx += 1
    seq.append({"para": para_idx, "line": t.line, "word": t.word, "par_initial": t.par_initial})
    by_line[t.line].append(t.word)

line_first_par = {}
cur = None
for s in seq:
    if cur != s["line"]:
        cur = s["line"]
        line_first_par[s["line"]] = s["par_initial"]


def line_key(s):
    m = re.match(r"(\d+)", str(s))
    return int(m.group()) if m else 9999


print("f77r RAW LINES (★ = paragraph-initial)")
print()
for ln in sorted(by_line.keys(), key=line_key):
    flag = "★" if line_first_par.get(ln) else " "
    print(f"  {flag} L{str(ln):>3} ({len(by_line[ln]):>2}): {' '.join(by_line[ln])}")

print()
print(f"Stats: {len(seq)} tokens, {len(by_line)} lines, {para_idx + 1} paragraphs")

# Heat anchors
HEAT = {"qokedy", "qokeedy", "qokey", "qokeey", "qoked"}
qok_lines = {}
for ln, words in by_line.items():
    qc = sum(1 for w in words if w in HEAT)
    if qc >= 3:
        qok_lines[ln] = qc

print(f"\n4-clusters in lines: {qok_lines}")
print(f"Paragraph-initial lines: {[ln for ln in sorted(by_line, key=line_key) if line_first_par.get(ln)]}")
