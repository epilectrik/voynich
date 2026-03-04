"""P-L1 & P-L2: Testing crazy expert's l="let flow" hypothesis.

P-L1: l-initial MIDDLEs enriched in REGIME_2 (collection) vs REGIME_1 (heating)
P-L2: Tokens with l-atom MIDDLEs have elevated FL_SAFE rates
"""

import json
import math
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

PROJECT = Path(__file__).resolve().parent


def normal_cdf(z):
    if z < -8: return 0.0
    if z > 8: return 1.0
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if z >= 0 else -1
    t = 1.0 / (1.0 + p * abs(z))
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z / 2.0)
    return 0.5 * (1.0 + sign * y)


tx = Transcript()
morph = Morphology()

# Load regime mapping
with open(PROJECT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# Load 49-class and macro_state mapping
# We need the BAnalyzer for macro_state. Let's load it if available,
# otherwise we'll use the class->macro_state mapping directly.
try:
    from scripts.voynich import BFolioDecoder
    decoder = BFolioDecoder()
    has_decoder = True
    print("BFolioDecoder loaded successfully")
except Exception as e:
    has_decoder = False
    print(f"BFolioDecoder not available: {e}")
    print("Will use manual class mapping")

# ============================================================
# P-L1: l-initial MIDDLE fraction by REGIME
# ============================================================
print(f"\n{'='*70}")
print("P-L1: l-INITIAL MIDDLE FRACTION BY REGIME")
print(f"{'='*70}")
print("Prediction: l-initial enriched in REGIME_2 relative to REGIME_1")

# Count l-initial vs total MIDDLEs per regime
regime_counts = defaultdict(lambda: {'l_initial': 0, 'total': 0})
folio_counts = defaultdict(lambda: {'l_initial': 0, 'total': 0})

atoms = set('a d e h k o n i m y c p f s t r l q'.split())

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid:
        continue
    f = token.folio
    regime = folio_regime.get(f)
    if not regime:
        continue

    first_atom = mid[0]
    regime_counts[regime]['total'] += 1
    folio_counts[f]['total'] += 1
    if first_atom == 'l':
        regime_counts[regime]['l_initial'] += 1
        folio_counts[f]['l_initial'] += 1

print(f"\n  {'Regime':<12s} {'l-init':>8s} {'total':>8s} {'fraction':>10s} {'enrichment':>12s}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*10} {'-'*12}")

global_l = sum(r['l_initial'] for r in regime_counts.values())
global_total = sum(r['total'] for r in regime_counts.values())
global_frac = global_l / global_total

for regime in sorted(regime_counts.keys()):
    d = regime_counts[regime]
    frac = d['l_initial'] / d['total']
    enrich = frac / global_frac
    print(f"  {regime:<12s} {d['l_initial']:>8d} {d['total']:>8d} {frac:>10.4f} {enrich:>11.3f}x")

print(f"  {'GLOBAL':<12s} {global_l:>8d} {global_total:>8d} {global_frac:>10.4f} {'1.000x':>12s}")

# Chi-square: REGIME_2 vs REGIME_1 for l-initial
r1 = regime_counts['REGIME_1']
r2 = regime_counts['REGIME_2']
r1_frac = r1['l_initial'] / r1['total']
r2_frac = r2['l_initial'] / r2['total']
# 2x2 chi-square
a_val = r2['l_initial']
b_val = r2['total'] - r2['l_initial']
c_val = r1['l_initial']
d_val = r1['total'] - r1['l_initial']
n = a_val + b_val + c_val + d_val
chi2 = (n * (a_val * d_val - b_val * c_val) ** 2) / ((a_val + b_val) * (c_val + d_val) * (a_val + c_val) * (b_val + d_val))
z_chi = math.sqrt(chi2)
p_chi = 2 * (1 - normal_cdf(z_chi))

print(f"\n  REGIME_2 vs REGIME_1: {r2_frac:.4f} vs {r1_frac:.4f}")
print(f"  R2/R1 ratio: {r2_frac/r1_frac:.3f}x")
print(f"  Chi-square: {chi2:.2f}, p={p_chi:.6f}")

# Also do comprehensive atom-initial by regime (like P16 did for AXM)
print(f"\n{'='*70}")
print("ALL ATOM-INITIAL FRACTIONS BY REGIME (comprehensive)")
print(f"{'='*70}")

all_atoms = 'a d e h k o n i m y c p f s t r l q'.split()
print(f"\n  {'Atom':<5s}", end="")
for regime in sorted(regime_counts.keys()):
    print(f" {regime:>10s}", end="")
print(f" {'R2/R1':>8s} {'R2/R3':>8s}")
print(f"  {'-'*5}", end="")
for _ in sorted(regime_counts.keys()):
    print(f" {'-'*10}", end="")
print(f" {'-'*8} {'-'*8}")

# Per-regime atom counts
regime_atom_counts = defaultdict(lambda: defaultdict(int))
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid:
        continue
    f = token.folio
    regime = folio_regime.get(f)
    if not regime:
        continue
    regime_atom_counts[regime][mid[0]] += 1

for atom in all_atoms:
    print(f"  {atom:<5s}", end="")
    fracs = {}
    for regime in sorted(regime_counts.keys()):
        total = regime_counts[regime]['total']
        count = regime_atom_counts[regime].get(atom, 0)
        frac = count / total
        fracs[regime] = frac
        print(f" {frac:>10.4f}", end="")
    r1v = fracs.get('REGIME_1', 0) or 0.0001
    r3v = fracs.get('REGIME_3', 0) or 0.0001
    r2r1 = fracs.get('REGIME_2', 0) / r1v
    r2r3 = fracs.get('REGIME_2', 0) / r3v
    print(f" {r2r1:>7.3f}x {r2r3:>7.3f}x")

# ============================================================
# P-L2: l-atom presence vs FL_SAFE macro state
# ============================================================
print(f"\n{'='*70}")
print("P-L2: l-ATOM PRESENCE vs FL_SAFE/FL_HAZ MACRO STATE")
print(f"{'='*70}")
print("Prediction: tokens with l in MIDDLE have elevated FL_SAFE rate")

if has_decoder:
    # Use BAnalyzer for macro_state classification
    l_macro = Counter()
    nol_macro = Counter()
    total_classified = 0

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        mid = morph.extract(w).middle
        if not mid:
            continue

        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if not ms:
            continue

        total_classified += 1
        has_l = 'l' in mid
        if has_l:
            l_macro[ms] += 1
        else:
            nol_macro[ms] += 1

    print(f"\n  Total classified: {total_classified}")
    l_total = sum(l_macro.values())
    nol_total = sum(nol_macro.values())

    print(f"\n  {'State':<12s} {'l-atom':>8s} {'l-%':>8s} {'no-l':>8s} {'no-l-%':>8s} {'l/no-l':>8s}")
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    for state in ['FL_SAFE', 'FL_HAZ', 'AXM', 'AXm', 'FQ', 'CC']:
        lc = l_macro.get(state, 0)
        nc = nol_macro.get(state, 0)
        l_pct = lc / l_total * 100 if l_total > 0 else 0
        n_pct = nc / nol_total * 100 if nol_total > 0 else 0
        ratio = (lc / l_total) / (nc / nol_total) if nc > 0 and nol_total > 0 else 0
        print(f"  {state:<12s} {lc:>8d} {l_pct:>7.1f}% {nc:>8d} {n_pct:>7.1f}% {ratio:>7.3f}x")

    # Chi-square for FL_SAFE specifically
    l_safe = l_macro.get('FL_SAFE', 0)
    l_other = l_total - l_safe
    nol_safe = nol_macro.get('FL_SAFE', 0)
    nol_other = nol_total - nol_safe
    n = l_safe + l_other + nol_safe + nol_other
    chi2_safe = (n * (l_safe * nol_other - l_other * nol_safe) ** 2) / \
                ((l_safe + l_other) * (nol_safe + nol_other) * (l_safe + nol_safe) * (l_other + nol_other))
    z_s = math.sqrt(chi2_safe)
    p_s = 2 * (1 - normal_cdf(z_s))

    l_safe_rate = l_safe / l_total if l_total > 0 else 0
    nol_safe_rate = nol_safe / nol_total if nol_total > 0 else 0
    print(f"\n  FL_SAFE rate: l-atom={l_safe_rate:.4f} vs no-l={nol_safe_rate:.4f}")
    print(f"  Enrichment: {l_safe_rate/nol_safe_rate:.3f}x" if nol_safe_rate > 0 else "")
    print(f"  Chi-square: {chi2_safe:.2f}, p={p_s:.6f}")

    # Also check FL_HAZ
    l_haz = l_macro.get('FL_HAZ', 0)
    nol_haz = nol_macro.get('FL_HAZ', 0)
    l_haz_rate = l_haz / l_total if l_total > 0 else 0
    nol_haz_rate = nol_haz / nol_total if nol_total > 0 else 0
    print(f"\n  FL_HAZ rate: l-atom={l_haz_rate:.4f} vs no-l={nol_haz_rate:.4f}")
    if nol_haz_rate > 0:
        print(f"  Enrichment: {l_haz_rate/nol_haz_rate:.3f}x")

    # ============================================================
    # BONUS: l-atom by atom position (initial vs terminal vs middle)
    # ============================================================
    print(f"\n{'='*70}")
    print("BONUS: l-POSITION WITHIN MIDDLE vs MACRO STATE")
    print(f"{'='*70}")

    l_init_macro = Counter()
    l_term_macro = Counter()
    l_mid_macro = Counter()

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        mid = morph.extract(w).middle
        if not mid or 'l' not in mid:
            continue

        analysis = decoder.analyze_token(w)
        ms = analysis.macro_state
        if not ms:
            continue

        if mid[0] == 'l':
            l_init_macro[ms] += 1
        if mid[-1] == 'l':
            l_term_macro[ms] += 1
        if 'l' in mid[1:-1]:
            l_mid_macro[ms] += 1

    for label, counter in [('l-initial', l_init_macro), ('l-terminal', l_term_macro), ('l-medial', l_mid_macro)]:
        total = sum(counter.values())
        if total == 0:
            continue
        safe_rate = counter.get('FL_SAFE', 0) / total
        haz_rate = counter.get('FL_HAZ', 0) / total
        print(f"  {label:<12s} (n={total:>5d}): FL_SAFE={safe_rate:.4f}  FL_HAZ={haz_rate:.4f}  safe/haz={safe_rate/haz_rate:.2f}x" if haz_rate > 0 else f"  {label:<12s} (n={total:>5d}): FL_SAFE={safe_rate:.4f}  FL_HAZ={haz_rate:.4f}")

else:
    # Fallback: use the 49-class mapping file directly
    print("  [Using manual approach - loading class maps]")

    # Load the middle dictionary for class assignments
    with open(PROJECT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)

    # Count MIDDLEs containing 'l' by their kernel assignment
    l_kernels = Counter()
    nol_kernels = Counter()
    for mid_key, mid_data in mid_dict.items():
        kernel = mid_data.get('kernel', 'UNKNOWN')
        if 'l' in mid_key:
            l_kernels[kernel] += mid_data.get('count', 0)
        else:
            nol_kernels[kernel] += mid_data.get('count', 0)

    print("\n  Kernel distribution (l-atom vs no-l MIDDLEs):")
    for k in ['K', 'H', 'E']:
        l_pct = l_kernels.get(k, 0) / sum(l_kernels.values()) * 100
        n_pct = nol_kernels.get(k, 0) / sum(nol_kernels.values()) * 100
        print(f"    {k}: l-atom={l_pct:.1f}% no-l={n_pct:.1f}%")

# ============================================================
# P-L1 EXTENDED: l-initial by section too
# ============================================================
print(f"\n{'='*70}")
print("P-L1 EXTENDED: l-INITIAL BY SECTION")
print(f"{'='*70}")

# Load section data from AXM file
with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
          'axm_residual_decomposition.json', encoding='utf-8') as f:
    axm_data = json.load(f)
folio_section = {f: d['section'] for f, d in axm_data['folio_data'].items()}

section_counts = defaultdict(lambda: {'l_initial': 0, 'total': 0})
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    mid = morph.extract(w).middle
    if not mid:
        continue
    f = token.folio
    sec = folio_section.get(f)
    if not sec:
        continue
    section_counts[sec]['total'] += 1
    if mid[0] == 'l':
        section_counts[sec]['l_initial'] += 1

print(f"\n  {'Section':<10s} {'l-init':>8s} {'total':>8s} {'fraction':>10s} {'enrichment':>12s}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*10} {'-'*12}")
for sec in sorted(section_counts.keys()):
    d = section_counts[sec]
    frac = d['l_initial'] / d['total']
    enrich = frac / global_frac
    print(f"  {sec:<10s} {d['l_initial']:>8d} {d['total']:>8d} {frac:>10.4f} {enrich:>11.3f}x")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"\n  P-L1: l-initial in REGIME_2 vs REGIME_1")
print(f"    R2 fraction: {r2_frac:.4f}")
print(f"    R1 fraction: {r1_frac:.4f}")
print(f"    Ratio: {r2_frac/r1_frac:.3f}x")
if r2_frac > r1_frac and p_chi < 0.05:
    print(f"    RESULT: CONFIRMED (p={p_chi:.6f})")
elif r2_frac > r1_frac:
    print(f"    RESULT: DIRECTIONALLY CORRECT but not significant (p={p_chi:.6f})")
else:
    print(f"    RESULT: FAILED (R2 not enriched over R1)")
