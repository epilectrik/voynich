"""
16_b_convergence_full_tokens.py

B-Convergence Validation using FULL PP TOKENS (not just MIDDLEs).

Per C733: 38% of PP structure is in PREFIX+SUFFIX selection, not just MIDDLE.
Per C662: PREFIX significantly constrains instruction class in B.

This test properly traces full token forms through the pipeline.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

results_dir = Path(__file__).parent.parent / "results"
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"

print("="*70)
print("B-CONVERGENCE VALIDATION - FULL TOKENS")
print("="*70)
print("Per C733: Using full tokens, not just MIDDLEs")

# Load PRECISION candidates
with open(results_dir / "precision_analysis.json") as f:
    precision_data = json.load(f)

with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

# Get validated candidates (k+e > 2h)
candidates = precision_data['precision_candidates']
validated = [c for c in candidates if c['kernels']['k'] + c['kernels']['e'] > 2 * c['kernels']['h']]
print(f"\nPRECISION candidates (kernel-validated): {len(validated)}")

for v in validated:
    print(f"  {v['para_id']}: {v['initial_ri']}")

# Extract FULL PP TOKENS from each PRECISION paragraph
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

precision_tokens = set()  # Full token forms
precision_token_details = []  # For analysis

for v in validated:
    para_id = v['para_id']
    tokens = para_tokens.get(para_id, [])

    for t in tokens:
        word = t.get('word', '')
        if not word or '*' in word:
            continue
        try:
            m = morph.extract(word)
            # Check if this is a PP token (MIDDLE is in pp_middles)
            if m.middle and m.middle in pp_middles:
                precision_tokens.add(word)
                precision_token_details.append({
                    'word': word,
                    'prefix': m.prefix,
                    'middle': m.middle,
                    'suffix': m.suffix,
                    'para_id': para_id
                })
        except:
            pass

print(f"\nPRECISION PP tokens (full forms): {len(precision_tokens)}")

# Analyze PREFIX distribution in PRECISION PP
prefix_counts = Counter(t['prefix'] for t in precision_token_details if t['prefix'])
print(f"\nPREFIX distribution in PRECISION PP tokens:")
for prefix, count in prefix_counts.most_common(10):
    print(f"  {prefix}: {count} ({100*count/len(precision_token_details):.1f}%)")

# Load B tokens
print("\n" + "="*70)
print("TRACING FULL TOKENS THROUGH B")
print("="*70)

tx = Transcript()
b_tokens = list(tx.currier_b())

# Build word -> B locations mapping
word_to_b = defaultdict(list)
for t in b_tokens:
    word_to_b[t.word].append(t)

# Find which PRECISION tokens appear in B
precision_in_b = {}
for word in precision_tokens:
    if word in word_to_b:
        precision_in_b[word] = word_to_b[word]

print(f"PRECISION PP tokens found in B: {len(precision_in_b)} / {len(precision_tokens)}")
print(f"Coverage: {100*len(precision_in_b)/len(precision_tokens):.1f}%")

# Total B tokens matching PRECISION PP
total_b_matches = sum(len(locs) for locs in precision_in_b.values())
print(f"Total B token instances: {total_b_matches}")

# Get folios where PRECISION tokens appear
precision_b_folios = set()
for word, locs in precision_in_b.items():
    for t in locs:
        precision_b_folios.add(t.folio)

print(f"B folios with PRECISION PP: {len(precision_b_folios)}")

# Load REGIME mapping
regime_map_file = Path(__file__).parent.parent.parent.parent / "results" / "regime_folio_mapping.json"
with open(regime_map_file) as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

# REGIME distribution
print("\n" + "="*70)
print("REGIME DISTRIBUTION")
print("="*70)

regime_counts = Counter()
for folio in precision_b_folios:
    regime = folio_to_regime.get(folio, 'unknown')
    regime_counts[regime] += 1

print(f"\nREGIME distribution of B folios with PRECISION PP:")
total = sum(regime_counts.values())
for regime, count in sorted(regime_counts.items()):
    pct = 100 * count / total if total > 0 else 0
    print(f"  {regime}: {count} folios ({pct:.1f}%)")

# Baseline
all_b_folios = set(t.folio for t in b_tokens)
baseline_regimes = Counter(folio_to_regime.get(f, 'unknown') for f in all_b_folios)
print(f"\nBaseline (all B folios):")
total_base = sum(baseline_regimes.values())
for regime, count in sorted(baseline_regimes.items()):
    pct = 100 * count / total_base if total_base > 0 else 0
    print(f"  {regime}: {count} folios ({pct:.1f}%)")

# Kernel analysis on MATCHED B tokens
print("\n" + "="*70)
print("KERNEL PROFILE IN B (matched tokens)")
print("="*70)

precision_b_kernel = {'k': 0, 'h': 0, 'e': 0, 'total': 0}
precision_b_prefix = Counter()

for word, locs in precision_in_b.items():
    for t in locs:
        try:
            m = morph.extract(t.word)
            precision_b_kernel['total'] += 1
            if m.middle:
                if 'k' in m.middle:
                    precision_b_kernel['k'] += 1
                if 'h' in m.middle:
                    precision_b_kernel['h'] += 1
                if 'e' in m.middle:
                    precision_b_kernel['e'] += 1
            if m.prefix:
                precision_b_prefix[m.prefix] += 1
        except:
            pass

if precision_b_kernel['total'] > 0:
    k_rate = precision_b_kernel['k'] / precision_b_kernel['total']
    h_rate = precision_b_kernel['h'] / precision_b_kernel['total']
    e_rate = precision_b_kernel['e'] / precision_b_kernel['total']

    print(f"\nPRECISION PP in B ({precision_b_kernel['total']} tokens):")
    print(f"  k rate: {k_rate:.4f}")
    print(f"  h rate: {h_rate:.4f}")
    print(f"  e rate: {e_rate:.4f}")
    print(f"  k+e: {k_rate + e_rate:.4f}")

    # Compare to A profile
    prec_k = precision_data['precision_kernels']['k']
    prec_h = precision_data['precision_kernels']['h']
    prec_e = precision_data['precision_kernels']['e']

    print(f"\nComparison:")
    print(f"  A (PRECISION): k={prec_k:.3f}, h={prec_h:.3f}, e={prec_e:.3f}, k+e={prec_k+prec_e:.3f}")
    print(f"  B (matched):   k={k_rate:.3f}, h={h_rate:.3f}, e={e_rate:.3f}, k+e={k_rate+e_rate:.3f}")

    kernel_test = (k_rate + e_rate) > 2 * h_rate
    print(f"\n  k+e > 2h test: {'PASS' if kernel_test else 'FAIL'}")

# PREFIX analysis in B
print("\n" + "="*70)
print("PREFIX DISTRIBUTION IN B (matched tokens)")
print("="*70)

print(f"\nPREFIX distribution of PRECISION PP in B:")
total_prefix = sum(precision_b_prefix.values())
for prefix, count in precision_b_prefix.most_common(10):
    pct = 100 * count / total_prefix if total_prefix > 0 else 0
    print(f"  {prefix}: {count} ({pct:.1f}%)")

# Baseline PREFIX in B
baseline_prefix = Counter()
for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m.prefix:
            baseline_prefix[m.prefix] += 1
    except:
        pass

print(f"\nBaseline PREFIX in B:")
total_base_prefix = sum(baseline_prefix.values())
for prefix, count in baseline_prefix.most_common(10):
    pct = 100 * count / total_base_prefix if total_base_prefix > 0 else 0
    print(f"  {prefix}: {count} ({pct:.1f}%)")

# Compare key prefixes
print("\n" + "="*70)
print("PREFIX ENRICHMENT ANALYSIS")
print("="*70)

key_prefixes = ['qo', 'ok', 'ot', 'ch', 'sh', 'ol', 'or']
print("\nKey PREFIX enrichment (PRECISION vs baseline):")
for prefix in key_prefixes:
    prec_rate = precision_b_prefix.get(prefix, 0) / total_prefix if total_prefix > 0 else 0
    base_rate = baseline_prefix.get(prefix, 0) / total_base_prefix if total_base_prefix > 0 else 0
    ratio = prec_rate / base_rate if base_rate > 0 else 0
    print(f"  {prefix}: {prec_rate:.3f} vs {base_rate:.3f} = {ratio:.2f}x")

# Baseline B kernel for comparison
print("\n" + "="*70)
print("BASELINE COMPARISON")
print("="*70)

baseline_kernel = {'k': 0, 'h': 0, 'e': 0, 'total': 0}
for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle:
            baseline_kernel['total'] += 1
            if 'k' in m.middle:
                baseline_kernel['k'] += 1
            if 'h' in m.middle:
                baseline_kernel['h'] += 1
            if 'e' in m.middle:
                baseline_kernel['e'] += 1
    except:
        pass

if baseline_kernel['total'] > 0:
    base_k = baseline_kernel['k'] / baseline_kernel['total']
    base_h = baseline_kernel['h'] / baseline_kernel['total']
    base_e = baseline_kernel['e'] / baseline_kernel['total']

    print(f"\nBaseline B kernel:")
    print(f"  k: {base_k:.4f}")
    print(f"  h: {base_h:.4f}")
    print(f"  e: {base_e:.4f}")
    print(f"  k+e: {base_k + base_e:.4f}")

    print(f"\nEnrichment (PRECISION vs baseline):")
    print(f"  k: {k_rate/base_k:.2f}x")
    print(f"  h: {h_rate/base_h:.2f}x")
    print(f"  e: {e_rate/base_e:.2f}x")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
FULL TOKEN ANALYSIS:
  PRECISION PP tokens: {len(precision_tokens)}
  Found in B: {len(precision_in_b)} ({100*len(precision_in_b)/len(precision_tokens):.1f}%)
  B instances: {total_b_matches}
  B folios: {len(precision_b_folios)}

KERNEL SIGNATURE:
  A (PRECISION): k+e = {prec_k+prec_e:.3f}, h = {prec_h:.3f}
  B (matched):   k+e = {k_rate+e_rate:.3f}, h = {h_rate:.3f}
  Baseline B:    k+e = {base_k+base_e:.3f}, h = {base_h:.3f}

  h-suppression: {h_rate/base_h:.2f}x baseline
  k+e > 2h test: {'PASS' if kernel_test else 'FAIL'}

REGIME: {'Universal' if len(precision_b_folios) == len(all_b_folios) else 'Partial'} coverage
""")

# Save results
results = {
    'precision_tokens': len(precision_tokens),
    'found_in_b': len(precision_in_b),
    'coverage_pct': 100*len(precision_in_b)/len(precision_tokens),
    'b_instances': total_b_matches,
    'b_folios': len(precision_b_folios),
    'precision_b_kernel': {
        'k': k_rate,
        'h': h_rate,
        'e': e_rate,
        'k_plus_e': k_rate + e_rate
    },
    'baseline_b_kernel': {
        'k': base_k,
        'h': base_h,
        'e': base_e,
        'k_plus_e': base_k + base_e
    },
    'h_suppression': h_rate / base_h if base_h > 0 else 0,
    'kernel_test_pass': kernel_test,
    'regime_distribution': dict(regime_counts),
    'prefix_enrichment': {
        p: (precision_b_prefix.get(p, 0) / total_prefix) / (baseline_prefix.get(p, 0) / total_base_prefix)
        if baseline_prefix.get(p, 0) > 0 else 0
        for p in key_prefixes
    }
}

with open(results_dir / "b_convergence_full_tokens.json", 'w') as f:
    json.dump(results, f, indent=2)
print(f"Saved to b_convergence_full_tokens.json")
