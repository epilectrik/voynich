"""
F-F12: Compositional Convergence (DECISIVE) -- do f-compound readings match
CategoryClassifier output?

5 compounds tested:
  1. fch = f(flag) + c(adjust) + h(watch) -> "note"           -> MARKING expected
  2. ofch = o(arrange) + f(flag) + c(adjust) + h(watch) -> "arrange-note" -> MARKING expected
  3. of  = o(arrange) + f(flag) -> "arranged flag"             -> MARKING or STAGING
  4. ef  = e(cool) + f(flag) -> "cool flag"                    -> MARKING or THERMAL
  5. cf  = c(adjust) + f(flag) -> "adjust flag"                -> MARKING expected

Pass: >= 3/5 FULL or PARTIAL matches.

h-junction effect: do compounds with h (fch, ofch) show different category
from those without (of, ef, cf)?

Order sensitivity check: of vs fo, ef vs fe (if data exists).

KEY DISCRIMINANT: Non-h compounds (of, ef, cf) determine the gloss:
  - If of, ef -> MARKING: H1 "flag" confirmed
  - If of, ef -> STAGING: H2 "format" better
  - If of, ef -> OPERATION: H3 "fill" better
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
print("F-F12: Compositional Convergence (DECISIVE)")
print("=" * 72)
print()

# -- Gather all B MIDDLE category profiles -------------------------------------
middle_cat_counts = defaultdict(lambda: defaultdict(int))
middle_cat_totals = defaultdict(int)
middle_token_count = defaultdict(int)

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m is None or m.middle is None:
        continue
    middle_token_count[m.middle] += 1
    cat = cc.classify(m.middle)
    if cat and cat != 'UNK':
        middle_cat_counts[m.middle][cat] += 1
        middle_cat_totals[m.middle] += 1


def get_profile(mid):
    """Return (category_dict, total, primary_category)."""
    total = middle_cat_totals.get(mid, 0)
    if total == 0:
        return {}, 0, None
    profile = {}
    for cat in CATEGORIES:
        profile[cat] = middle_cat_counts[mid].get(cat, 0) / total
    primary = max(profile, key=profile.get)
    return profile, total, primary


# -- Define compound tests -----------------------------------------------------
compounds = [
    {
        'middle': 'fch',
        'decomposition': 'f(flag) + c(adjust) + h(watch)',
        'gloss': 'note',
        'expected': ['MARKING'],
        'h_junction': True,
    },
    {
        'middle': 'ofch',
        'decomposition': 'o(arrange) + f(flag) + c(adjust) + h(watch)',
        'gloss': 'arrange-note',
        'expected': ['MARKING'],
        'h_junction': True,
    },
    {
        'middle': 'of',
        'decomposition': 'o(arrange) + f(flag)',
        'gloss': 'arranged flag',
        'expected': ['MARKING', 'STAGING'],
        'h_junction': False,
    },
    {
        'middle': 'ef',
        'decomposition': 'e(cool) + f(flag)',
        'gloss': 'cool flag',
        'expected': ['MARKING', 'THERMAL'],
        'h_junction': False,
    },
    {
        'middle': 'cf',
        'decomposition': 'c(adjust) + f(flag)',
        'gloss': 'adjust flag',
        'expected': ['MARKING'],
        'h_junction': False,
    },
]

# -- Test each compound --------------------------------------------------------
results = []

for comp in compounds:
    mid = comp['middle']
    profile, total, primary = get_profile(mid)
    token_n = middle_token_count.get(mid, 0)

    print(f"  {mid} = {comp['decomposition']} -> \"{comp['gloss']}\"")
    print(f"    Tokens: {token_n}, Classified: {total}")

    if total == 0:
        print(f"    NO DATA -- skipping")
        print(f"    Match: SKIP")
        results.append({'mid': mid, 'match': 'SKIP', 'h_junction': comp['h_junction']})
        print()
        continue

    # Show profile
    print(f"    Expected: {' or '.join(comp['expected'])}")
    print(f"    Observed profile:")
    for cat in CATEGORIES:
        pct = profile.get(cat, 0) * 100
        marker = ""
        if cat == primary:
            marker = " <-- PRIMARY"
        elif cat in comp['expected'] and pct >= 20.0:
            marker = " <-- expected (>=20%)"
        elif cat in comp['expected']:
            marker = " (expected)"
        if pct >= 1.0 or cat in comp['expected']:
            print(f"      {cat:<14}: {pct:>5.1f}%{marker}")

    # Evaluate match
    full_match = primary in comp['expected']
    partial_match = any(profile.get(cat, 0) >= 0.20 for cat in comp['expected'])

    if full_match:
        match_type = 'FULL'
    elif partial_match:
        match_type = 'PARTIAL'
    else:
        match_type = 'NONE'

    print(f"    Match: {match_type} (primary={primary})")
    results.append({
        'mid': mid, 'match': match_type, 'primary': primary,
        'profile': profile, 'h_junction': comp['h_junction'],
        'expected': comp['expected']
    })
    print()

# -- Order sensitivity check ---------------------------------------------------
print("-" * 72)
print("Order sensitivity check")
print("-" * 72)
print()

order_pairs = [('of', 'fo'), ('ef', 'fe'), ('cf', 'fc'), ('fch', 'chf')]

for fwd, rev in order_pairs:
    fwd_profile, fwd_n, fwd_primary = get_profile(fwd)
    rev_profile, rev_n, rev_primary = get_profile(rev)

    fwd_tok = middle_token_count.get(fwd, 0)
    rev_tok = middle_token_count.get(rev, 0)

    if fwd_n > 0 and rev_n > 0:
        print(f"  {fwd} (N={fwd_tok}, primary={fwd_primary}) vs "
              f"{rev} (N={rev_tok}, primary={rev_primary})")
        # Show key differences
        for cat in CATEGORIES:
            f_pct = fwd_profile.get(cat, 0) * 100
            r_pct = rev_profile.get(cat, 0) * 100
            if abs(f_pct - r_pct) >= 5.0:
                print(f"    {cat:<14}: {fwd}={f_pct:.1f}% vs {rev}={r_pct:.1f}% "
                      f"(delta={r_pct - f_pct:+.1f}pp)")
    elif fwd_n > 0:
        print(f"  {fwd} exists (N={fwd_tok}), {rev} absent")
    elif rev_n > 0:
        print(f"  {fwd} absent, {rev} exists (N={rev_tok})")
    else:
        print(f"  Neither {fwd} nor {rev} found")
    print()

# -- h-junction vs non-h-junction comparison -----------------------------------
print("-" * 72)
print("h-junction effect: fch-family vs non-h f-compounds")
print("-" * 72)
print()

h_junction_results = [r for r in results if r.get('h_junction') and r['match'] != 'SKIP']
non_h_results = [r for r in results if not r.get('h_junction') and r['match'] != 'SKIP']

if h_junction_results:
    h_mark_rates = []
    for r in h_junction_results:
        mark = r.get('profile', {}).get('MARKING', 0) * 100
        h_mark_rates.append(mark)
        print(f"  h-junction {r['mid']}: MARKING = {mark:.1f}%")
    mean_h_mark = sum(h_mark_rates) / len(h_mark_rates) if h_mark_rates else 0
    print(f"  Mean h-junction MARKING: {mean_h_mark:.1f}%")
else:
    mean_h_mark = 0
    print("  No h-junction compounds with data")

print()

if non_h_results:
    non_h_mark_rates = []
    non_h_stg_rates = []
    for r in non_h_results:
        mark = r.get('profile', {}).get('MARKING', 0) * 100
        stg = r.get('profile', {}).get('STAGING', 0) * 100
        non_h_mark_rates.append(mark)
        non_h_stg_rates.append(stg)
        print(f"  non-h {r['mid']}: MARKING={mark:.1f}%, STAGING={stg:.1f}%")
    mean_non_h_mark = sum(non_h_mark_rates) / len(non_h_mark_rates) if non_h_mark_rates else 0
    mean_non_h_stg = sum(non_h_stg_rates) / len(non_h_stg_rates) if non_h_stg_rates else 0
    print(f"  Mean non-h MARKING:  {mean_non_h_mark:.1f}%")
    print(f"  Mean non-h STAGING:  {mean_non_h_stg:.1f}%")
else:
    mean_non_h_mark = 0
    mean_non_h_stg = 0
    print("  No non-h compounds with data")

if h_junction_results and non_h_results:
    h_shift = mean_h_mark - mean_non_h_mark
    print(f"\n  h-junction MARKING shift: {h_shift:+.1f}pp")
    if h_shift > 10:
        print("  -> h-junction pulls f-compounds toward MARKING")
    elif h_shift < -10:
        print("  -> h-junction pulls AWAY from MARKING (unexpected)")
    else:
        print("  -> h-junction effect modest")

# -- Overall evaluation --------------------------------------------------------
print()
print("=" * 72)
print("OVERALL EVALUATION")
print("=" * 72)
print()

valid_results = [r for r in results if r['match'] != 'SKIP']
full_count = sum(1 for r in valid_results if r['match'] == 'FULL')
partial_count = sum(1 for r in valid_results if r['match'] == 'PARTIAL')
none_count = sum(1 for r in valid_results if r['match'] == 'NONE')
skip_count = sum(1 for r in results if r['match'] == 'SKIP')

print(f"  Results: {full_count} FULL + {partial_count} PARTIAL + {none_count} NONE + {skip_count} SKIP")
print(f"  Pass threshold: >= 3 (FULL or PARTIAL) out of {len(valid_results)} testable")
print()

match_count = full_count + partial_count
overall_pass = match_count >= 3

for r in results:
    status = r['match']
    if status == 'SKIP':
        print(f"  {r['mid']:<5}: SKIP (no data)")
    else:
        print(f"  {r['mid']:<5}: {status} (primary={r.get('primary', '?')})")

print()
print(f"OVERALL: {'PASS' if overall_pass else 'FAIL'} ({match_count}/{len(valid_results)} match)")
print()

# -- Hypothesis discrimination from non-h compounds ---------------------------
print("KEY DISCRIMINANT: Non-h compound primary categories")
print()

non_h_primaries = defaultdict(int)
for r in non_h_results:
    if r.get('primary'):
        non_h_primaries[r['primary']] += 1

if non_h_primaries:
    dominant_cat = max(non_h_primaries, key=non_h_primaries.get)
    print(f"  Non-h compound primaries: {dict(non_h_primaries)}")
    print(f"  Dominant: {dominant_cat}")
    print()

    if dominant_cat == 'MARKING':
        print("  -> Non-h compounds are MARKING-dominant: H1 'flag' SUPPORTED")
    elif dominant_cat == 'STAGING':
        print("  -> Non-h compounds are STAGING-dominant: H2 'format' SUPPORTED")
    elif dominant_cat == 'OPERATION':
        print("  -> Non-h compounds are OPERATION-dominant: H3 'fill' SUPPORTED")
    elif dominant_cat == 'THERMAL':
        print("  -> Non-h compounds are THERMAL-dominant: f absorbed by thermal context")
        print("     (H1/H2/H3 distinction unresolved by this test)")
    else:
        print(f"  -> Non-h compounds are {dominant_cat}-dominant: unexpected")
        print("     (none of H1/H2/H3 directly supported)")
else:
    print("  No non-h compound data available for discrimination")
