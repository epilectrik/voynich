"""
F-F11: MARKING Injection -- does adding f to base atom X increase MARKING fraction?

Method:
  For each base atom X in {k, e, o, c, d}:
    - Find tokens with MIDDLE = X (standalone)
    - Find tokens with MIDDLE = fX (f prepended)
    - Find tokens with MIDDLE = Xf (f appended)
    - Use whichever direction (fX or Xf) has more tokens
    - Classify each by CategoryClassifier
    - Compute MARKING% delta

Predictions:
  - f+X MARKING rate > X in >= 3/5 testable bases
  - Mean delta >= +3pp

Pass: injection in >= 3/5 bases AND mean delta >= +3pp.

Controls: p injection +68.3pp MARKING (Phase 500), c injection +43.2pp MON+MARK (Phase 499),
          s injection +33.3pp (only 2/6).

KEY DISCRIMINANT: If f injects MARKING like p, supports H1 "flag".
                  If f injects STAGING, supports H2 "format".
                  If f injects OPERATION, supports H3 "fill".
                  If neutral (like s), inconclusive.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# -- Load data -----------------------------------------------------------------
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

print("=" * 72)
print("F-F11: MARKING Injection -- f addition to base atoms")
print("=" * 72)
print()

# -- Gather all Currier B MIDDLEs ----------------------------------------------
middle_tokens = defaultdict(int)  # middle -> count

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m is None or m.middle is None:
        continue
    middle_tokens[m.middle] += 1

# -- Test bases ----------------------------------------------------------------
bases = ['k', 'e', 'o', 'c', 'd']

print("Inventory check:")
for base in bases:
    fx = 'f' + base  # f prepended
    xf = base + 'f'  # f appended
    print(f"  {base}: {middle_tokens.get(base, 0)} tokens | "
          f"f{base}: {middle_tokens.get(fx, 0)} | "
          f"{base}f: {middle_tokens.get(xf, 0)}")
print()

# -- Classify and compute injection deltas -------------------------------------
# Rebuild per-MIDDLE category profiles from all B tokens
middle_cat_counts = defaultdict(lambda: defaultdict(int))
middle_cat_totals = defaultdict(int)

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m is None or m.middle is None:
        continue
    cat = cc.classify(m.middle)
    if cat and cat != 'UNK':
        middle_cat_counts[m.middle][cat] += 1
        middle_cat_totals[m.middle] += 1


def get_category_profile(mid):
    """Return category fraction dict for a MIDDLE."""
    total = middle_cat_totals.get(mid, 0)
    if total == 0:
        return None, 0
    profile = {}
    for cat in CATEGORIES:
        profile[cat] = middle_cat_counts[mid].get(cat, 0) / total
    return profile, total


MIN_N = 3  # Lower threshold due to sparse f-compounds

print("-" * 72)
print("Category injection analysis")
print("-" * 72)
print()

marking_deltas = []
testable_bases = 0
marking_wins = 0

results = []

for base in bases:
    base_profile, base_n = get_category_profile(base)

    # Choose whichever direction (fX or Xf) has more classified tokens
    fx = 'f' + base
    xf = base + 'f'
    fx_profile, fx_n = get_category_profile(fx)
    xf_profile, xf_n = get_category_profile(xf)

    # Pick the direction with more data
    candidates = []
    if fx_profile is not None and fx_n >= MIN_N:
        candidates.append((fx, f'f{base} (prepend)', fx_profile, fx_n))
    if xf_profile is not None and xf_n >= MIN_N:
        candidates.append((xf, f'{base}f (append)', xf_profile, xf_n))

    if base_profile is None or base_n < MIN_N:
        # Still show what we have
        print(f"  {base}: base N={base_n} < {MIN_N} -- SKIP")
        print()
        continue

    if not candidates:
        print(f"  {base} (N={base_n}): no f-compound with N >= {MIN_N}")
        # Show available counts
        print(f"    f{base}: {middle_tokens.get(fx, 0)} tokens, classified: {fx_n}")
        print(f"    {base}f: {middle_tokens.get(xf, 0)} tokens, classified: {xf_n}")
        print()
        continue

    # Use the candidate with the most tokens
    best = max(candidates, key=lambda c: c[3])
    f_form, label, f_profile, f_n = best

    testable_bases += 1

    base_mark = base_profile.get('MARKING', 0) * 100
    f_mark = f_profile.get('MARKING', 0) * 100
    delta_mark = f_mark - base_mark

    marking_deltas.append(delta_mark)
    if delta_mark > 0:
        marking_wins += 1

    # Also track STAGING and OPERATION deltas for hypothesis discrimination
    base_stg = base_profile.get('STAGING', 0) * 100
    f_stg = f_profile.get('STAGING', 0) * 100
    delta_stg = f_stg - base_stg

    base_op = base_profile.get('OPERATION', 0) * 100
    f_op = f_profile.get('OPERATION', 0) * 100
    delta_op = f_op - base_op

    results.append({
        'base': base, 'f_form': f_form, 'label': label,
        'base_n': base_n, 'f_n': f_n,
        'base_mark': base_mark, 'f_mark': f_mark, 'delta_mark': delta_mark,
        'base_stg': base_stg, 'f_stg': f_stg, 'delta_stg': delta_stg,
        'base_op': base_op, 'f_op': f_op, 'delta_op': delta_op,
        'base_profile': base_profile, 'f_profile': f_profile,
    })

# -- Display results -----------------------------------------------------------
for r in results:
    print(f"  {r['base']} (N={r['base_n']}) -> {r['label']} (N={r['f_n']}):")
    print(f"    MARKING:   {r['base_mark']:>5.1f}% -> {r['f_mark']:>5.1f}% (delta {r['delta_mark']:+.1f}pp)")
    print(f"    STAGING:   {r['base_stg']:>5.1f}% -> {r['f_stg']:>5.1f}% (delta {r['delta_stg']:+.1f}pp)")
    print(f"    OPERATION: {r['base_op']:>5.1f}% -> {r['f_op']:>5.1f}% (delta {r['delta_op']:+.1f}pp)")

    # Show full profile for the f-form
    print(f"    Full f-form profile: ", end="")
    parts = []
    for cat in CATEGORIES:
        pct = r['f_profile'].get(cat, 0) * 100
        if pct >= 5.0:
            parts.append(f"{cat[:4]}={pct:.0f}%")
    print(", ".join(parts))
    print()

# -- Summary -------------------------------------------------------------------
print("=" * 72)
print("SUMMARY")
print("=" * 72)
print()
print(f"  Testable base-f pairs: {testable_bases}")
print()

if testable_bases > 0 and marking_deltas:
    mean_mark = sum(marking_deltas) / len(marking_deltas)
else:
    mean_mark = 0.0

# Also compute mean STAGING and OPERATION deltas
stg_deltas = [r['delta_stg'] for r in results]
op_deltas = [r['delta_op'] for r in results]
stg_wins = sum(1 for d in stg_deltas if d > 0)
op_wins = sum(1 for d in op_deltas if d > 0)
mean_stg = sum(stg_deltas) / len(stg_deltas) if stg_deltas else 0.0
mean_op = sum(op_deltas) / len(op_deltas) if op_deltas else 0.0

print(f"  MARKING injection:   {marking_wins}/{testable_bases} positive, mean delta {mean_mark:+.1f}pp")
print(f"  STAGING injection:   {stg_wins}/{testable_bases} positive, mean delta {mean_stg:+.1f}pp")
print(f"  OPERATION injection: {op_wins}/{testable_bases} positive, mean delta {mean_op:+.1f}pp")
print()

# -- Predictions ---------------------------------------------------------------
print("=" * 72)
print("PREDICTION EVALUATION")
print("=" * 72)
print()

threshold_n = 3  # Need >= 3/5 positive

p1_mark = marking_wins >= threshold_n and mean_mark >= 3.0

print(f"  Need >= {threshold_n}/{testable_bases} positive AND mean delta >= +3pp")
print()
print(f"  MARKING: wins={marking_wins}/{testable_bases} mean={mean_mark:+.1f}pp -> {'PASS' if p1_mark else 'FAIL'}")
print()

overall = p1_mark
print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
print()

# Hypothesis discrimination
print("HYPOTHESIS DISCRIMINATION:")
if p1_mark:
    print("  -> MARKING injection confirmed: supports H1 'flag' (Flagge/Fahne)")
    print("     (f injects MARKING like p does)")
else:
    # Check if STAGING or OPERATION was injected instead
    p1_stg = stg_wins >= threshold_n and mean_stg >= 3.0
    p1_op = op_wins >= threshold_n and mean_op >= 3.0
    if p1_stg:
        print(f"  -> STAGING injection found: {stg_wins}/{testable_bases}, mean {mean_stg:+.1f}pp")
        print("  -> Supports H2 'format' (Fassung)")
    elif p1_op:
        print(f"  -> OPERATION injection found: {op_wins}/{testable_bases}, mean {mean_op:+.1f}pp")
        print("  -> Supports H3 'fill' (fullen)")
    else:
        print("  -> No clear injection effect detected")
        print(f"     MARKING  {marking_wins}/{testable_bases} mean={mean_mark:+.1f}pp")
        print(f"     STAGING  {stg_wins}/{testable_bases} mean={mean_stg:+.1f}pp")
        print(f"     OPERATION {op_wins}/{testable_bases} mean={mean_op:+.1f}pp")
        print("  -> f may be structurally neutral or too rare for reliable injection test")

print()
print("Controls: p injection +68.3pp MARKING (Phase 500)")
print("          c injection +43.2pp MON+MARK (Phase 499)")
print("          s injection +33.3pp STAGING (only 2/6 bases)")
