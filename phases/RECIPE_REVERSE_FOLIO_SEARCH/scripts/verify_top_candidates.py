"""Verify top reverse-scan candidates by:
1. Pulling raw line dumps
2. Identifying structural anchors
3. Predicting recipe count + family
4. Searching SISMEL unmatched recipes
5. Reporting candidate matches for atom-decode verification
"""
from __future__ import annotations
import io, sys, json, re
from pathlib import Path
from collections import defaultdict, Counter

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

CANDIDATES = ["f104v", "f77r", "f111r", "f114r", "f75v"]


def line_key(s):
    m = re.match(r"(\d+)", str(s))
    return int(m.group()) if m else 9999


def folio_data(folio):
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
        })
        by_line[t.line].append(t.word)
    return seq, by_line, para_idx + 1 if seq else 0


HEAT = {"qokedy", "qokeedy", "qokey", "qokeey", "qoked"}


def find_anchors(seq):
    """Identify structural count-anchors in a folio sequence."""
    n = len(seq)
    # Identical-token runs ≥3
    runs = []
    i = 0
    while i < n:
        j = i
        while j + 1 < n and seq[j + 1]["word"] == seq[i]["word"]:
            j += 1
        if j - i + 1 >= 3:
            runs.append({
                "word": seq[i]["word"], "len": j - i + 1,
                "line": seq[i]["line"], "pos": i,
            })
        i = j + 1

    # Within-line clusters of qok-class ≥3
    by_line = defaultdict(list)
    for s in seq:
        by_line[s["line"]].append(s)
    line_clusters = []
    for ln, tokens in by_line.items():
        qok_count = sum(1 for t in tokens if t["word"] in HEAT)
        if qok_count >= 3:
            line_clusters.append({"line": ln, "count": qok_count})

    return {"identical_runs": runs, "line_clusters": line_clusters}


# Load SISMEL
subs = json.loads((ROOT / "phases" / "SISMEL_RECIPE_CORPUS" /
                   "results" / "sismel_subrecipes.json").read_text(encoding="utf-8"))["subrecipes"]
by_id = {s["id"]: s for s in subs}

# Already-claimed recipes (from confirmed matches + Phase 644 + matched_recipes)
CLAIMED_RECIPES = {
    "III.19.0", "III.19.1", "III.19.2", "III.19.3", "III.19.4", "III.19.5",
    "III.19.6", "III.19.7", "III.19.8",  # Ch19 sub-recipes
    "II.16.0", "III.16.0", "III.20.0", "III.12.0", "II.1.0", "III.18.0",
    "III.21.0", "II.7.0", "II.12.0", "III.11.0", "III.1.0", "III.4.0",
    "III.36.0", "II.10.0", "III.29.0", "II.8.0",
}

NUMBER_RE = re.compile(
    r"(?:per|en|de|ab|dedins|dins|amb|cum|in|ad|aprés|despres|puys|"
    r"post|infra|circa|iterum|sobre|sots)\s+"
    r"(?:\.(?P<arabic>\d+)\.?|"
    r"(?P<roman>\.[ivx]+\.?|\b[ivx]{2,5}\b(?=\s+(?:vegades?|vices|dies|"
    r"diebus|partes?|parts?|parties?|hores?|mesos?|anys?)))|"
    r"(?P<spelled>una|un|dues|dos|tres|quatre|cinch|cinc|sis|set|vuit|huit|nou|"
    r"deu|dotze|tretze|catorze|quinze|setze|disset|divuit|dinou|vint|trenta|"
    r"unum|duas|duo|tres|quatuor|quattuor|quinque|sex|septem|octo|novem|decem|"
    r"undecim|duodecim|tredecim|quindecim|viginti))"
    r"\s+(?P<unit>vegades?|vices|cops|parts?|parties?|partes?|partium|"
    r"dies(?:\s+naturalls?)?|diebus|joras?|jorns?|hores?|setmanes?|mesos?|menses?|"
    r"anys?|annos?|annis?)",
    re.IGNORECASE,
)
ROMAN = {"i":1,"ii":2,"iii":3,"iiii":4,"iv":4,"v":5,"vi":6,"vii":7,"viii":8,
         "ix":9,"x":10,"xi":11,"xii":12,"xiii":13,"xv":15,"xx":20}
SPELLED = {"una":1,"un":1,"dues":2,"dos":2,"tres":3,"quatre":4,"cinch":5,
           "cinc":5,"sis":6,"set":7,"vuit":8,"huit":8,"nou":9,"deu":10,
           "dotze":12,"unum":1,"duas":2,"duos":2,"duo":2,"tres":3,"tria":3,
           "quatuor":4,"quattuor":4,"quinque":5,"sex":6,"septem":7,"octo":8,
           "novem":9,"decem":10,"undecim":11,"duodecim":12,"tredecim":13,
           "quindecim":15,"viginti":20}

def extract_counts(text):
    if not text:
        return []
    counts = []
    for m in NUMBER_RE.finditer(text):
        if m.group("arabic"):
            v = int(m.group("arabic"))
        elif m.group("roman"):
            v = ROMAN.get(m.group("roman").strip(".").lower())
        elif m.group("spelled"):
            v = SPELLED.get(m.group("spelled").lower())
        else:
            v = None
        if v:
            counts.append({"value": v, "unit": m.group("unit"),
                           "context": text[max(0,m.start()-25):m.end()+10]
                                       .replace("\n"," ").strip()})
    return counts


# Build unmatched-recipe count index
unmatched_with_counts = []
for s in subs:
    if s["id"] in CLAIMED_RECIPES:
        continue
    if s["part"] not in ("II", "III"):
        continue
    cat = s.get("catalan") or ""
    lat = s.get("latin") or ""
    counts = extract_counts(cat) + extract_counts(lat)
    if counts:
        unmatched_with_counts.append({
            "id": s["id"], "part": s["part"],
            "title": (s.get("title_catalan") or s.get("title_latin") or "")[:75],
            "distinct_counts": sorted({c["value"] for c in counts}),
            "n_chars": len(cat) + len(lat),
            "counts": counts,
        })


for folio in CANDIDATES:
    seq, by_line, n_paras = folio_data(folio)
    n_tokens = len(seq)
    anchors = find_anchors(seq)

    print("=" * 80)
    print(f"## {folio}")
    print(f"  {n_tokens} tokens, {len(by_line)} lines, {n_paras} paragraphs")
    print(f"  Identical runs ≥3: {anchors['identical_runs']}")
    print(f"  Within-line qok clusters ≥3: {anchors['line_clusters'][:5]}")
    print()

    # Predict count from anchors
    predicted_counts = set()
    for r in anchors["identical_runs"]:
        if r["len"] >= 3:
            predicted_counts.add(r["len"])
    for c in anchors["line_clusters"]:
        if c["count"] >= 3:
            predicted_counts.add(c["count"])
    print(f"  Predicted recipe counts: {sorted(predicted_counts)}")

    # Search SISMEL unmatched recipes for matching counts
    matches = []
    for r in unmatched_with_counts:
        rc = set(r["distinct_counts"])
        overlap = predicted_counts & rc
        if overlap:
            matches.append((r, overlap))
    matches.sort(key=lambda x: (-len(x[1]), x[0]["n_chars"]))

    if matches:
        print(f"\n  Top matching unmatched recipes (overlap with predicted counts):")
        for r, ov in matches[:6]:
            print(f"    {r['id']:<10} part={r['part']}  overlap={sorted(ov)}  "
                  f"counts={r['distinct_counts']}  len={r['n_chars']}")
            print(f"      {r['title'][:70]}")
    else:
        print("  No unmatched recipes with predicted counts.")

    # Show first 3 paragraph-initial line starts
    line_first_par = {}
    cur = None
    for s in seq:
        if cur != s["line"]:
            cur = s["line"]
            line_first_par[s["line"]] = s["par_initial"]

    initial_lines = [ln for ln in sorted(by_line.keys(), key=line_key) if line_first_par.get(ln)]
    if initial_lines:
        print(f"\n  Paragraph-initial lines: {initial_lines[:8]}{'...' if len(initial_lines)>8 else ''}")
        print(f"  First paragraph-initial line content (L{initial_lines[0]}): "
              f"{' '.join(by_line[initial_lines[0]][:8])}")

    print()


print("\n" + "=" * 80)
print("Recommendation: top candidates for atom-decode verification")
print("=" * 80)
print()
print("  Use raw_data approach: pull recipe + folio raw lines, score operationally.")
