"""
Phase 654 Step 1: Run the locked typology test.

This script READS the pre-registered classifications from
locked_classifications.json and applies the locked statistical protocol.
Per pre-registration, no retroactive modification of categories,
classifications, atoms tested, or pass criteria is permitted.

Test:
- Compute folio-presence rate of each of 9 atoms per substrate category
- Fisher exact test for each (atom, category) pair
- Bonferroni correction: alpha = 0.05 / 9 = 0.00556 per atom
- Pass criteria per locked PRE_REGISTRATION.md
"""
import sys
import json
import math
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript
from collections import defaultdict, Counter

tx = Transcript()

# Load locked pre-registration
with open('phases/PHASE_654_DARK_PIPELINE_FOLIO_TYPOLOGY/locked_classifications.json') as f:
    pre_reg = json.load(f)

CATEGORIES = pre_reg['categories']
ATOMS = pre_reg['atoms_tested']
FOLIO_CLS = {f: d['category'] for f, d in pre_reg['folio_classifications'].items()}
ALPHA_BONF = 0.05 / len(ATOMS)
ENRICH_THRESHOLD = 4.0

print("="*78)
print("PHASE 654: DARK PIPELINE FOLIO-RESOLUTION TYPOLOGY TEST")
print("="*78)
print()
print(f"Pre-registered categories: {len(CATEGORIES)}")
print(f"Pre-registered atoms: {len(ATOMS)} ({', '.join(ATOMS)})")
print(f"Pre-registered folios: {len(FOLIO_CLS)}")
print(f"Bonferroni alpha: {ALPHA_BONF:.5f}")
print(f"Enrichment threshold: {ENRICH_THRESHOLD}x")

# Per-folio atom presence
folio_atom_present = defaultdict(set)
for t in tx.currier_b():
    f = t.folio
    if f not in FOLIO_CLS: continue
    w = t.word
    for atom in ATOMS:
        if atom in w:
            folio_atom_present[f].add(atom)

# Verify all classified folios were observed
print()
print("Folios in locked classification:")
for f, cat in sorted(FOLIO_CLS.items()):
    n_atoms = len(folio_atom_present.get(f, set()))
    print(f"  {f:>6s} → {cat:<22s}  ({n_atoms} of 9 atoms present)")

# Manual Fisher exact (one-sided, greater)
def log_factorial(n):
    if n <= 1: return 0.0
    return math.lgamma(n + 1)

def hypergeom_p(a, b, c, d):
    """P(X = a) where X ~ Hypergeometric(N=a+b+c+d, K=a+b, n=a+c)."""
    n = a + b + c + d
    return math.exp(
        log_factorial(a + b) + log_factorial(c + d) +
        log_factorial(a + c) + log_factorial(b + d) -
        log_factorial(n) - log_factorial(a) - log_factorial(b) -
        log_factorial(c) - log_factorial(d)
    )

def fisher_exact_one_sided_greater(a, b, c, d):
    """One-sided Fisher exact test, alternative = greater (a is enriched)."""
    p = 0.0
    a_max = min(a + b, a + c)
    for a_i in range(a, a_max + 1):
        b_i = (a + b) - a_i
        c_i = (a + c) - a_i
        d_i = (a + b + c + d) - a_i - b_i - c_i
        if b_i >= 0 and c_i >= 0 and d_i >= 0:
            p += hypergeom_p(a_i, b_i, c_i, d_i)
    return min(p, 1.0)

# Build contingency tables and run Fisher exact for each (atom, category) pair
print()
print("="*78)
print("CONTINGENCY ANALYSIS")
print("="*78)
print()
print(f"{'Atom':>5s}  {'Category':<22s}  {'in_cat':>6s}  {'not_cat':>7s}  "
      f"{'enrich':>7s}  {'p (Fisher)':>10s}  {'sig?':>4s}")
print("-"*85)

results = []
significant_pairs = []

for atom in ATOMS:
    for cat in CATEGORIES:
        # 2x2: rows = atom_present (yes/no), cols = in_category (yes/no)
        # a = in_cat AND has atom
        # b = not_cat AND has atom
        # c = in_cat AND no atom
        # d = not_cat AND no atom
        a = sum(1 for f, c in FOLIO_CLS.items()
                if c == cat and atom in folio_atom_present.get(f, set()))
        b = sum(1 for f, c in FOLIO_CLS.items()
                if c != cat and atom in folio_atom_present.get(f, set()))
        c = sum(1 for f, ct in FOLIO_CLS.items()
                if ct == cat and atom not in folio_atom_present.get(f, set()))
        d = sum(1 for f, ct in FOLIO_CLS.items()
                if ct != cat and atom not in folio_atom_present.get(f, set()))

        in_cat_n = a + c
        not_cat_n = b + d
        if in_cat_n == 0:
            continue  # category has no folios
        in_cat_rate = a / in_cat_n
        not_cat_rate = b / not_cat_n if not_cat_n > 0 else 0
        enrich = (in_cat_rate / not_cat_rate) if not_cat_rate > 0 else (float('inf') if a > 0 else 0)
        p_val = fisher_exact_one_sided_greater(a, b, c, d)

        passes_enrich = enrich >= ENRICH_THRESHOLD
        passes_p = p_val < ALPHA_BONF
        passes = passes_enrich and passes_p
        sig_str = '***' if passes else (' . ' if (enrich >= 2 and p_val < 0.10) else '   ')

        results.append({
            'atom': atom, 'category': cat,
            'a': a, 'b': b, 'c': c, 'd': d,
            'in_cat_rate': in_cat_rate, 'not_cat_rate': not_cat_rate,
            'enrich': enrich, 'p': p_val, 'passes': passes,
        })
        if passes:
            significant_pairs.append((atom, cat, enrich, p_val, a, in_cat_n))

        # Only print top results per atom
        enrich_str = f"{enrich:.2f}x" if enrich != float('inf') else "inf"
        print(f"  {atom:>4s}  {cat:<22s}  {a:>3d}/{in_cat_n:<2d}  "
              f"{b:>3d}/{not_cat_n:<2d}    {enrich_str:>6s}  {p_val:>10.5f}  {sig_str}")

# Summary
print()
print("="*78)
print("VERDICT")
print("="*78)
print()
print(f"Atoms passing strict criteria (enrich ≥{ENRICH_THRESHOLD}x AND Bonferroni p<{ALPHA_BONF:.4f}):")
if significant_pairs:
    for atom, cat, enr, p, a, n in significant_pairs:
        enr_str = f"{enr:.2f}x" if enr != float('inf') else "inf"
        print(f"  {atom} → {cat}  (rate {a}/{n}, enrich {enr_str}, p={p:.5f})")
else:
    print("  (none)")

n_passing = len(significant_pairs)
print(f"\nTotal passing: {n_passing}")

if n_passing >= 3:
    verdict = "PASS"
    print()
    print(f"VERDICT: PASS — typology framework supported.")
    print(f"Register C1968 per locked outcome plan.")
elif n_passing == 2:
    verdict = "INCONCLUSIVE"
    print()
    print(f"VERDICT: INCONCLUSIVE — 2 atoms pass, register Tier 3 with underpowered note.")
elif n_passing <= 1:
    verdict = "NULL"
    print()
    print(f"VERDICT: NULL — typology framework refuted.")
    print(f"C1939 and C1940 stand as isolated material-identification findings.")
    print(f"Update INTERPRETATION_SUMMARY.md to reflect refuted framework.")

# Save results
with open('phases/PHASE_654_DARK_PIPELINE_FOLIO_TYPOLOGY/results/test_results.json', 'w') as f:
    json.dump({
        'verdict': verdict,
        'n_passing': n_passing,
        'significant_pairs': [{'atom': a, 'category': c, 'enrichment': e if e != float('inf') else None,
                                'p_value': p, 'positive': pos, 'total': tot}
                              for a, c, e, p, pos, tot in significant_pairs],
        'all_results': [{'atom': r['atom'], 'category': r['category'],
                         'a': r['a'], 'b': r['b'], 'c': r['c'], 'd': r['d'],
                         'in_cat_rate': r['in_cat_rate'],
                         'enrich': r['enrich'] if r['enrich'] != float('inf') else None,
                         'p': r['p'], 'passes': r['passes']}
                        for r in results],
    }, f, indent=2, default=str)
print()
print("Saved: phases/PHASE_654_DARK_PIPELINE_FOLIO_TYPOLOGY/results/test_results.json")
