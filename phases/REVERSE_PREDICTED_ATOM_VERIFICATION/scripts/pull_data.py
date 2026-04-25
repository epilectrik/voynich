"""Pull raw line dumps + recipe Catalan/Latin text for f108v↔III.29.0 and
f79v↔II.8.0. Output to results/raw_data.md for direct reading."""
from __future__ import annotations
import io, sys, json, re
from pathlib import Path
from collections import defaultdict

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

CANDIDATES = [
    ("f108v", "III.29.0", "mercury sublimation × 3 vegades"),
    ("f79v",  "II.8.0",   "first liquefaction / 3-day balneum"),
]

OUT = ROOT / "phases" / "REVERSE_PREDICTED_ATOM_VERIFICATION" / "results" / "raw_data.md"


def line_key(s):
    m = re.match(r"(\d+)", str(s))
    return int(m.group()) if m else 9999


def folio_seq(folio):
    tx = Transcript()
    morph = Morphology()
    para_idx = 0
    seq = []
    by_line = defaultdict(list)
    for t in tx.currier_b():
        if t.folio != folio:
            continue
        if t.placement and t.placement.startswith("L"):
            continue
        if t.par_initial and seq:
            para_idx += 1
        seq.append({
            "para": para_idx, "line": t.line, "word": t.word,
            "par_initial": t.par_initial,
            "atom": morph.atomize(t.word),
            "morph": morph.extract(t.word),
        })
        by_line[t.line].append(t.word)
    return seq, by_line, para_idx + 1 if seq else 0


# Load recipes
subs = json.loads((ROOT / "phases" / "SISMEL_RECIPE_CORPUS" /
                   "results" / "sismel_subrecipes.json").read_text(encoding="utf-8"))["subrecipes"]
by_id = {s["id"]: s for s in subs}

md = ["# Reverse-Predicted Atom Verification — Raw Data",
      "",
      "Two reverse-predicted candidates from the Phase 641 blind test.",
      "Both flagged STRONG/MODERATE in initial blind verification.",
      "Now applying full atom-decode methodology (C1899-style) for confirmation.",
      ""]

for folio, recipe_id, label in CANDIDATES:
    seq, by_line, n_paras = folio_seq(folio)
    n_tokens = len(seq)
    recipe = by_id.get(recipe_id, {})

    md.append("=" * 80)
    md.append(f"## {folio} ↔ {recipe_id} ({label})")
    md.append("=" * 80)
    md.append("")
    md.append(f"**Folio stats:** {n_tokens} tokens, "
              f"{len(by_line)} lines, {n_paras} paragraphs")
    md.append("")
    md.append(f"**Recipe (Catalan):**")
    md.append("")
    md.append(f"> {recipe.get('catalan') or '(no Catalan)'}")
    md.append("")
    md.append(f"**Recipe (Latin):**")
    md.append("")
    md.append(f"> {recipe.get('latin') or '(no Latin)'}")
    md.append("")
    md.append("**Folio raw lines** (★ = paragraph-initial)")
    md.append("")

    # Get line-initial-paragraph markers
    line_first_par = {}
    cur_line = None
    for s in seq:
        if cur_line != s["line"]:
            cur_line = s["line"]
            line_first_par[s["line"]] = s["par_initial"]

    md.append("```")
    for ln in sorted(by_line.keys(), key=line_key):
        flag = "★" if line_first_par.get(ln) else " "
        md.append(f"  {flag} L{str(ln):>3} ({len(by_line[ln]):>2}): {' '.join(by_line[ln])}")
    md.append("```")
    md.append("")

    # Quick-stat summary
    HEAT = {"qokedy", "qokeedy", "qokey", "qokeey", "qoked"}
    MATERIAL = {"dar", "dal"}
    ITER_TOK = {"daiin", "dain", "dair"}
    dar_count = sum(1 for s in seq if s["word"] == "dar")
    dal_count = sum(1 for s in seq if s["word"] == "dal")
    daiin_count = sum(1 for s in seq if s["word"] in {"daiin", "dain", "dair"})
    chekar_count = sum(1 for s in seq if s["word"] == "chekar")
    qokedy_count = sum(1 for s in seq if s["word"] == "qokedy")
    qokeedy_count = sum(1 for s in seq if s["word"] == "qokeedy")
    qok_class = sum(1 for s in seq if s["word"] in HEAT)
    qokaiin_count = sum(1 for s in seq if s["word"] == "qokaiin")
    qokain_count = sum(1 for s in seq if s["word"] == "qokain")

    md.append(f"**Atom stat summary:**")
    md.append(f"- dar={dar_count}, dal={dal_count}, daiin/dain/dair={daiin_count}, chekar={chekar_count}")
    md.append(f"- qokedy={qokedy_count}, qokeedy={qokeedy_count}, qok-class total={qok_class}")
    md.append(f"- qokaiin={qokaiin_count}, qokain={qokain_count} (iteration verbs)")
    md.append("")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(md), encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)}")
print(f"  Read this file directly to score the matches.")
