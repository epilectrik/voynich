"""
Test 3: Extended Form Context Discrimination

Question: Do extended forms (ke, kch) appear in different grammatical contexts than base forms (k, ch)?

Hypothesis: Extended forms represent "modified" or "sustained" operations appearing
later in procedures. They should have different PREFIX/SUFFIX distributions.

Method:
1. Compare PREFIX distribution: k-tokens vs ke-tokens
2. Compare SUFFIX distribution: k-tokens vs ke-tokens
3. Test if distributions differ significantly
"""
import sys
sys.path.insert(0, 'scripts')
from voynich import Transcript, Morphology
from collections import Counter
import json

tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'pc', 'do', 'ta'}

# Collect tokens by MIDDLE type
base_k_tokens = []
extended_ke_tokens = []
base_ch_tokens = []
extended_kch_tokens = []

for t in b_tokens:
    m = morph.extract(t.word)
    if m.prefix and m.prefix in HT_PREFIXES:
        continue
    if not m.middle:
        continue

    if m.middle == 'k':
        base_k_tokens.append((t, m))
    elif m.middle == 'ke':
        extended_ke_tokens.append((t, m))
    elif m.middle == 'ch':
        base_ch_tokens.append((t, m))
    elif m.middle == 'kch':
        extended_kch_tokens.append((t, m))

print("=" * 70)
print("TEST 3: EXTENDED FORM CONTEXT DISCRIMINATION")
print("=" * 70)
print()
print("Question: Do extended forms (ke, kch) have different PREFIX/SUFFIX")
print("distributions than base forms (k, ch)?")
print()

def analyze_pair(base_name, base_tokens, ext_name, ext_tokens):
    print(f"\n{'-'*60}")
    print(f"COMPARISON: {base_name} (n={len(base_tokens)}) vs {ext_name} (n={len(ext_tokens)})")
    print(f"{'-'*60}")

    # PREFIX distribution
    base_prefix = Counter(m.prefix for t, m in base_tokens if m.prefix)
    ext_prefix = Counter(m.prefix for t, m in ext_tokens if m.prefix)

    print("\nPREFIX DISTRIBUTION:")
    print(f"  {'PREFIX':<10} {base_name:>10} {ext_name:>10} {'Diff':>10}")
    print("  " + "-" * 45)

    all_prefixes = set(base_prefix.keys()) | set(ext_prefix.keys())
    prefix_data = []
    for p in sorted(all_prefixes, key=lambda x: -(base_prefix.get(x, 0) + ext_prefix.get(x, 0))):
        base_pct = base_prefix.get(p, 0) / len(base_tokens) * 100 if base_tokens else 0
        ext_pct = ext_prefix.get(p, 0) / len(ext_tokens) * 100 if ext_tokens else 0
        diff = ext_pct - base_pct
        print(f"  {p:<10} {base_pct:>9.1f}% {ext_pct:>9.1f}% {diff:>+9.1f}%")
        prefix_data.append({'prefix': p, 'base_pct': base_pct, 'ext_pct': ext_pct, 'diff': diff})

    # SUFFIX distribution
    base_suffix = Counter(m.suffix for t, m in base_tokens if m.suffix)
    ext_suffix = Counter(m.suffix for t, m in ext_tokens if m.suffix)

    print("\nSUFFIX DISTRIBUTION:")
    print(f"  {'SUFFIX':<10} {base_name:>10} {ext_name:>10} {'Diff':>10}")
    print("  " + "-" * 45)

    all_suffixes = set(base_suffix.keys()) | set(ext_suffix.keys())
    suffix_data = []
    for s in sorted(all_suffixes, key=lambda x: -(base_suffix.get(x, 0) + ext_suffix.get(x, 0)))[:10]:
        base_pct = base_suffix.get(s, 0) / len(base_tokens) * 100 if base_tokens else 0
        ext_pct = ext_suffix.get(s, 0) / len(ext_tokens) * 100 if ext_tokens else 0
        diff = ext_pct - base_pct
        print(f"  {s:<10} {base_pct:>9.1f}% {ext_pct:>9.1f}% {diff:>+9.1f}%")
        suffix_data.append({'suffix': s, 'base_pct': base_pct, 'ext_pct': ext_pct, 'diff': diff})

    # Chi-square test on PREFIX
    from scipy import stats
    import numpy as np

    top_prefixes = sorted(all_prefixes, key=lambda x: -(base_prefix.get(x, 0) + ext_prefix.get(x, 0)))[:5]
    observed = np.array([
        [base_prefix.get(p, 0) for p in top_prefixes],
        [ext_prefix.get(p, 0) for p in top_prefixes]
    ])

    # Only test if we have enough data
    if observed.sum() >= 20 and np.all(observed.sum(axis=0) > 0):
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        print(f"\nChi-square (PREFIX top 5): chi2={chi2:.2f}, p={p_value:.4f}")
    else:
        chi2, p_value = None, None
        print("\nInsufficient data for chi-square test")

    return {
        'base': base_name,
        'extended': ext_name,
        'base_n': len(base_tokens),
        'ext_n': len(ext_tokens),
        'prefix_comparison': prefix_data[:5],
        'suffix_comparison': suffix_data[:5],
        'chi_square': chi2,
        'p_value': p_value
    }

# Analyze k vs ke
result_k = analyze_pair('k', base_k_tokens, 'ke', extended_ke_tokens)

# Analyze ch vs kch
result_ch = analyze_pair('ch', base_ch_tokens, 'kch', extended_kch_tokens)

print()
print("=" * 70)
print("KEY FINDINGS:")
print("=" * 70)

# Check for major differences
k_qo_base = next((p['base_pct'] for p in result_k['prefix_comparison'] if p['prefix'] == 'qo'), 0)
k_qo_ext = next((p['ext_pct'] for p in result_k['prefix_comparison'] if p['prefix'] == 'qo'), 0)

print(f"\n1. k vs ke PREFIX 'qo': {k_qo_base:.1f}% vs {k_qo_ext:.1f}% (diff: {k_qo_ext - k_qo_base:+.1f}%)")

# Verdict
significant_diff = False
if result_k['p_value'] and result_k['p_value'] < 0.05:
    significant_diff = True
if result_ch['p_value'] and result_ch['p_value'] < 0.05:
    significant_diff = True

if significant_diff:
    verdict = "CONFIRMED"
else:
    # Check for large effect sizes even without significance
    max_diff = max(abs(p['diff']) for p in result_k['prefix_comparison'][:3])
    if max_diff > 10:
        verdict = "SUPPORT"
    else:
        verdict = "NOT SUPPORTED"

print()
print("=" * 70)
print(f"VERDICT: {verdict}")
print("=" * 70)

if verdict in ["CONFIRMED", "SUPPORT"]:
    print("\nInterpretation: Extended forms (ke, kch) have different grammatical")
    print("contexts than base forms (k, ch), supporting the 'modified operation'")
    print("interpretation of extended MIDDLEs.")

# Output JSON
output = {
    "test": "Extended Form Context Discrimination",
    "question": "Do extended forms (ke, kch) differ grammatically from base forms (k, ch)?",
    "k_vs_ke": result_k,
    "ch_vs_kch": result_ch,
    "verdict": verdict
}

with open('phases/REVERSE_BRUNSCHWIG_V2/results/extended_form_context.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput saved to phases/REVERSE_BRUNSCHWIG_V2/results/extended_form_context.json")
