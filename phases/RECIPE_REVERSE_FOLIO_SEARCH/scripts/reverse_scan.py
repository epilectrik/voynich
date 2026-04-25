"""Reverse-direction match search: for each confirmed recipe, find unmatched
B folios whose structural signature most closely matches the confirmed match's
signature. Goal: identify top-3 candidate matches per recipe for atom-decode
verification.

Approach:
1. Compute signatures for the 8 confirmed-match folios (treated as templates)
2. Compute signatures for all unmatched B folios (≥200 tokens, ≥4 paragraphs)
3. For each unmatched folio, find the best-matching template via Euclidean
   distance on standardized signature features
4. Report top candidates per recipe
"""
from __future__ import annotations
import io, sys, json, re
from pathlib import Path
from collections import defaultdict, Counter
from math import sqrt

if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(r"C:\git\voynich")
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

# Already-matched folios (DO NOT scan these)
MATCHED = {
    "f75r", "f76r", "f76v", "f77v", "f79r", "f80r", "f81v",
    "f82r", "f82v", "f83r", "f84r", "f103r", "f107r",
    "f112r", "f112v", "f116r", "f78r", "f86v3",
    "f108v", "f79v",  # Phase 644 confirmed
}

# Confirmed-match folios (treated as templates) with their recipes
TEMPLATES = [
    ("f75r",  "III.19.0", "aqua vitae × 4-9 reflux"),
    ("f84r",  "II.12.0",  "gold dissolution / putrefaction"),
    ("f78r",  "III.36.0", "mercury congelation"),
    ("f86v3", "II.10.0",  "3-day coniuncció"),
    ("f82r",  "III.19.3", "lunaria 3-day sealed"),
    ("f108v", "III.29.0", "mercury sublimation"),
    ("f79v",  "II.8.0",   "first liquefaction"),
]

HEAT = {"qokedy", "qokeedy", "qokey", "qokeey", "qoked"}


def folio_signature(folio):
    tx = Transcript()
    morph = Morphology()
    para_idx = 0
    seq = []
    for t in tx.currier_b():
        if t.folio != folio:
            continue
        if t.placement and t.placement.startswith("L"):
            continue
        if t.par_initial and seq:
            para_idx += 1
        seq.append({
            "word": t.word,
            "atom": morph.atomize(t.word),
            "morph": morph.extract(t.word),
        })
    n = len(seq)
    if n == 0:
        return None
    n_paras = para_idx + 1

    cnt = Counter(s["word"] for s in seq)
    qokedy_n = cnt["qokedy"]
    qokeedy_n = cnt["qokeedy"]
    dar_n = cnt["dar"]
    dal_n = cnt["dal"]
    chekar_n = cnt["chekar"]
    qokain_n = cnt["qokain"]
    qokaiin_n = cnt["qokaiin"]
    qok_class = sum(1 for s in seq if s["word"] in HEAT)

    # Longest identical-token run
    longest_run = 1
    cur_run = 1
    for i in range(1, n):
        if seq[i]["word"] == seq[i-1]["word"]:
            cur_run += 1
            if cur_run > longest_run:
                longest_run = cur_run
        else:
            cur_run = 1

    # mean e_depth
    mean_e = sum(s["atom"].e_depth for s in seq) / n if n else 0

    return {
        "folio": folio,
        "n_tokens": n,
        "n_paras": n_paras,
        "qokedy_frac": qokedy_n / n,
        "qokeedy_frac": qokeedy_n / n,
        "qok_class_frac": qok_class / n,
        "dar_frac": dar_n / n,
        "dal_frac": dal_n / n,
        "chekar": chekar_n,
        "qokain_frac": qokain_n / n,
        "qokaiin_frac": qokaiin_n / n,
        "longest_run": longest_run,
        "mean_e": mean_e,
        "balneum_score": (qokeedy_n - qokedy_n) / n,
    }


# Compute template signatures
templates = []
for folio, recipe_id, label in TEMPLATES:
    sig = folio_signature(folio)
    if sig:
        sig["recipe_id"] = recipe_id
        sig["label"] = label
        templates.append(sig)

# Compute unmatched signatures
tx = Transcript()
all_b_folios = set()
for t in tx.currier_b():
    all_b_folios.add(t.folio)

unmatched = sorted(all_b_folios - MATCHED)
unmatched_sigs = []
for f in unmatched:
    sig = folio_signature(f)
    if sig and sig["n_tokens"] >= 200 and sig["n_paras"] >= 4:
        unmatched_sigs.append(sig)

print(f"Templates: {len(templates)}")
print(f"Unmatched B folios with >=200 tokens, >=4 paragraphs: {len(unmatched_sigs)}")
print()

# Feature set for similarity
FEATURES = [
    "qokedy_frac", "qokeedy_frac", "qok_class_frac",
    "dar_frac", "dal_frac", "qokain_frac", "qokaiin_frac",
    "longest_run", "mean_e", "balneum_score",
]

# Standardize features (z-score on combined templates+unmatched pool)
all_sigs = templates + unmatched_sigs
means = {}
stds = {}
for feat in FEATURES:
    vals = [s[feat] for s in all_sigs]
    m = sum(vals) / len(vals)
    var = sum((v - m)**2 for v in vals) / len(vals)
    s = sqrt(var) if var > 0 else 1.0
    means[feat] = m
    stds[feat] = s


def vec(sig):
    return [(sig[f] - means[f]) / stds[f] for f in FEATURES]


def euclid(v1, v2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


# For each unmatched folio, find nearest template
print("=" * 100)
print("UNMATCHED FOLIOS — best-matching template")
print("=" * 100)
print(f"\n{'folio':<8} {'tokens':>6} {'paras':>5} {'best_template':<8} {'recipe':<10} {'distance':>8}  {'longest_run':>10}")
print("-" * 100)

candidate_pairs = []
for u in unmatched_sigs:
    uv = vec(u)
    distances = [(euclid(uv, vec(t)), t) for t in templates]
    distances.sort()
    best = distances[0]
    candidate_pairs.append((u, best[1], best[0]))

# Sort by distance — closest matches first
candidate_pairs.sort(key=lambda x: x[2])

for u, best_t, dist in candidate_pairs[:25]:
    print(f"{u['folio']:<8} {u['n_tokens']:>6} {u['n_paras']:>5} "
          f"{best_t['folio']:<8} {best_t['recipe_id']:<10} {dist:>8.2f}  {u['longest_run']:>10}")

# Per-recipe top candidates
print("\n" + "=" * 100)
print("PER-RECIPE TOP CANDIDATES")
print("=" * 100)

per_recipe = defaultdict(list)
for u, best_t, dist in candidate_pairs:
    per_recipe[best_t["recipe_id"]].append((u, dist))

for recipe_id in sorted(per_recipe.keys()):
    top = per_recipe[recipe_id][:5]
    print(f"\n{recipe_id}:")
    for u, dist in top:
        run_anchor = f" (run-{u['longest_run']})" if u["longest_run"] >= 3 else ""
        print(f"  {u['folio']:<8}  d={dist:.2f}  "
              f"n={u['n_tokens']} para={u['n_paras']} "
              f"qokeedy={u['qokeedy_frac']*100:.1f}% qokedy={u['qokedy_frac']*100:.1f}% "
              f"dar={u['dar_frac']*100:.2f}%{run_anchor}")

# Write results JSON
out = ROOT / "phases" / "RECIPE_REVERSE_FOLIO_SEARCH" / "results" / "scan_results.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({
    "templates": templates,
    "unmatched_sigs": unmatched_sigs,
    "candidate_pairs": [
        {"folio": u["folio"], "best_template": t["folio"],
         "recipe_id": t["recipe_id"], "distance": d}
        for u, t, d in candidate_pairs
    ],
    "per_recipe_top5": {
        rid: [{"folio": u["folio"], "distance": d, "n_tokens": u["n_tokens"],
               "n_paras": u["n_paras"], "longest_run": u["longest_run"]}
              for u, d in cands[:5]]
        for rid, cands in per_recipe.items()
    },
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nWrote {out.relative_to(ROOT)}")
