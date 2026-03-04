"""
S-S11: Staging Injection — does adding s to base atom X increase STAGING
(or MONITORING) fraction?

Method:
  For each base atom X in {k, e, o, c, t, d}:
    - Find tokens with MIDDLE = X (standalone)
    - Find tokens with MIDDLE = sX (s prepended)
    - Find tokens with MIDDLE = Xs (s appended)
    - Classify each by CategoryClassifier
    - Compute STAGING% delta

Predictions:
  - s+X STAGING rate > X in >= 2/3 testable bases (or MONITORING > X)
  - Mean delta >= +3pp

Pass: injection in >= 2/3 bases AND mean delta >= +3pp.

Controls: p injection +68.3pp MARKING (Phase 500), c injection +43.2pp MON+MARK (Phase 499).
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

# ── Load data ──────────────────────────────────────────────────────────────
tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

CATEGORIES = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
              'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

print("=" * 72)
print("S-S11: Staging Injection -- s addition to base atoms")
print("=" * 72)
print()

# ── Gather all Currier B MIDDLEs ───────────────────────────────────────────
middle_tokens = defaultdict(int)  # middle -> count

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m is None or m.middle is None:
        continue
    middle_tokens[m.middle] += 1

# ── Test bases ─────────────────────────────────────────────────────────────
bases = ['k', 'e', 'o', 'c', 't', 'd']

print("Inventory check:")
for base in bases:
    sx = 's' + base  # s prepended
    xs = base + 's'  # s appended
    print(f"  {base}: {middle_tokens.get(base, 0)} tokens | "
          f"s{base}: {middle_tokens.get(sx, 0)} | "
          f"{base}s: {middle_tokens.get(xs, 0)}")
print()

# ── Classify and compute injection deltas ─────────────────────────────────
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


MIN_N = 3  # Lower threshold due to sparse s-compounds

print("-" * 72)
print("Category injection analysis")
print("-" * 72)
print()

staging_deltas = []
monitoring_deltas = []
combined_deltas = []  # STAGING + MONITORING
testable_bases = 0
staging_wins = 0
monitoring_wins = 0
combined_wins = 0

results = []

for base in bases:
    base_profile, base_n = get_category_profile(base)

    for s_form, label in [('s' + base, f's{base} (prepend)'), (base + 's', f'{base}s (append)')]:
        s_profile, s_n = get_category_profile(s_form)

        if base_profile is None or base_n < MIN_N:
            continue
        if s_profile is None or s_n < MIN_N:
            continue

        testable_bases += 1

        base_stg = base_profile.get('STAGING', 0) * 100
        s_stg = s_profile.get('STAGING', 0) * 100
        delta_stg = s_stg - base_stg

        base_mon = base_profile.get('MONITORING', 0) * 100
        s_mon = s_profile.get('MONITORING', 0) * 100
        delta_mon = s_mon - base_mon

        base_comb = base_stg + base_mon
        s_comb = s_stg + s_mon
        delta_comb = s_comb - base_comb

        staging_deltas.append(delta_stg)
        monitoring_deltas.append(delta_mon)
        combined_deltas.append(delta_comb)

        if delta_stg > 0:
            staging_wins += 1
        if delta_mon > 0:
            monitoring_wins += 1
        if delta_comb > 0:
            combined_wins += 1

        results.append({
            'base': base, 's_form': s_form, 'label': label,
            'base_n': base_n, 's_n': s_n,
            'base_stg': base_stg, 's_stg': s_stg, 'delta_stg': delta_stg,
            'base_mon': base_mon, 's_mon': s_mon, 'delta_mon': delta_mon,
            'base_comb': base_comb, 's_comb': s_comb, 'delta_comb': delta_comb,
            'base_profile': base_profile, 's_profile': s_profile
        })

# ── Display results ────────────────────────────────────────────────────────
for r in results:
    print(f"  {r['base']} (N={r['base_n']}) -> {r['label']} (N={r['s_n']}):")
    print(f"    STAGING:    {r['base_stg']:>5.1f}% -> {r['s_stg']:>5.1f}% (delta {r['delta_stg']:+.1f}pp)")
    print(f"    MONITORING: {r['base_mon']:>5.1f}% -> {r['s_mon']:>5.1f}% (delta {r['delta_mon']:+.1f}pp)")
    print(f"    Combined:   {r['base_comb']:>5.1f}% -> {r['s_comb']:>5.1f}% (delta {r['delta_comb']:+.1f}pp)")

    # Show full profile for the s-form
    print(f"    Full s-form profile: ", end="")
    parts = []
    for cat in CATEGORIES:
        pct = r['s_profile'].get(cat, 0) * 100
        if pct >= 5.0:
            parts.append(f"{cat[:4]}={pct:.0f}%")
    print(", ".join(parts))
    print()

# ── Summary ────────────────────────────────────────────────────────────────
print("=" * 72)
print("SUMMARY")
print("=" * 72)
print()
print(f"  Testable base-s pairs: {testable_bases}")
print()

if testable_bases > 0:
    mean_stg = sum(staging_deltas) / len(staging_deltas)
    mean_mon = sum(monitoring_deltas) / len(monitoring_deltas)
    mean_comb = sum(combined_deltas) / len(combined_deltas)
else:
    mean_stg = mean_mon = mean_comb = 0.0

print(f"  STAGING injection:    {staging_wins}/{testable_bases} positive, mean delta {mean_stg:+.1f}pp")
print(f"  MONITORING injection: {monitoring_wins}/{testable_bases} positive, mean delta {mean_mon:+.1f}pp")
print(f"  Combined (STG+MON):   {combined_wins}/{testable_bases} positive, mean delta {mean_comb:+.1f}pp")
print()

# ── Predictions ────────────────────────────────────────────────────────────
print("=" * 72)
print("PREDICTION EVALUATION")
print("=" * 72)
print()

threshold_n = max(1, int(testable_bases * 2 / 3))  # 2/3 of testable

p1_stg = staging_wins >= threshold_n and mean_stg >= 3.0
p1_mon = monitoring_wins >= threshold_n and mean_mon >= 3.0
p1_comb = combined_wins >= threshold_n and mean_comb >= 3.0

print(f"  Need >= {threshold_n}/{testable_bases} positive AND mean delta >= +3pp")
print()
print(f"  STAGING alone:    wins={staging_wins}/{testable_bases} mean={mean_stg:+.1f}pp -> {'PASS' if p1_stg else 'FAIL'}")
print(f"  MONITORING alone: wins={monitoring_wins}/{testable_bases} mean={mean_mon:+.1f}pp -> {'PASS' if p1_mon else 'FAIL'}")
print(f"  Combined STG+MON: wins={combined_wins}/{testable_bases} mean={mean_comb:+.1f}pp -> {'PASS' if p1_comb else 'FAIL'}")
print()

overall = p1_stg or p1_mon or p1_comb
print(f"OVERALL: {'PASS' if overall else 'FAIL'}")
print()

# Hypothesis discrimination
print("HYPOTHESIS DISCRIMINATION:")
if p1_stg and not p1_mon:
    print("  -> STAGING injection dominant: supports H1 'sequence'")
elif p1_mon and not p1_stg:
    print("  -> MONITORING injection dominant: supports H2 'sift/inspect'")
elif p1_stg and p1_mon:
    print("  -> Both STAGING and MONITORING injected: mixed signal (H1/H2)")
elif p1_comb:
    print("  -> Combined injection only: s adds STAGING+MONITORING mix")
else:
    print("  -> No clear injection effect: s may be structurally neutral")
    # Check if OPERATION was injected instead
    op_deltas = []
    op_wins = 0
    for r in results:
        base_op = r['base_profile'].get('OPERATION', 0) * 100
        s_op = r['s_profile'].get('OPERATION', 0) * 100
        delta_op = s_op - base_op
        op_deltas.append(delta_op)
        if delta_op > 0:
            op_wins += 1
    if op_deltas:
        mean_op = sum(op_deltas) / len(op_deltas)
        if op_wins >= threshold_n and mean_op >= 3.0:
            print(f"  -> But OPERATION injection found: {op_wins}/{testable_bases}, mean {mean_op:+.1f}pp")
            print("  -> Supports H3 'step' (OPERATION carrier)")

print()
print("Controls: p injection +68.3pp MARKING (Phase 500)")
print("          c injection +43.2pp MON+MARK (Phase 499)")
