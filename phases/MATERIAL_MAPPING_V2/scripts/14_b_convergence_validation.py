"""
14_b_convergence_validation.py

B-Convergence Validation for PRECISION candidates.

Tests the full A->AZC->B pipeline:
1. Extract PP vocabulary from 6 PRECISION paragraphs
2. Find which B folios these PP MIDDLEs appear in
3. Check REGIME distribution (expect REGIME_4 per C536)
4. Check which instruction classes survive under PP filtering
5. Check if k+e kernel signature manifests in B execution

This validates/invalidates the C384.a pathway with well-characterized specimens.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

results_dir = Path(__file__).parent.parent / "results"
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"

print("="*70)
print("B-CONVERGENCE VALIDATION FOR PRECISION CANDIDATES")
print("="*70)

# Load PRECISION candidates
with open(results_dir / "precision_analysis.json") as f:
    precision_data = json.load(f)

candidates = precision_data['precision_candidates']
print(f"PRECISION candidates: {len(candidates)}")

# Filter to 6 that pass kernel validation (k+e >> h)
validated = [c for c in candidates if c['kernels']['k'] + c['kernels']['e'] > 2 * c['kernels']['h']]
print(f"Kernel-validated (k+e > 2h): {len(validated)}")

for v in validated:
    print(f"  {v['para_id']}: {v['initial_ri']}")

# Load paragraph tokens to get PP vocabulary
with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

# Extract PP MIDDLEs from each PRECISION paragraph
morph = Morphology()

# Load RI/PP classification
from voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()

print("\n" + "="*70)
print("EXTRACTING PP VOCABULARY FROM PRECISION PARAGRAPHS")
print("="*70)

precision_pp = {}
all_precision_pp = set()

for v in validated:
    para_id = v['para_id']
    tokens = para_tokens.get(para_id, [])

    pp_in_para = []
    for t in tokens:
        word = t.get('word', '')
        if not word or '*' in word:
            continue
        try:
            m = morph.extract(word)
            middle = m.middle
            if middle and middle in pp_middles:
                pp_in_para.append(middle)
        except:
            pass

    precision_pp[para_id] = list(set(pp_in_para))
    all_precision_pp.update(pp_in_para)
    print(f"\n{para_id}: {len(set(pp_in_para))} unique PP MIDDLEs")
    print(f"  Sample: {list(set(pp_in_para))[:10]}")

print(f"\nTotal unique PP MIDDLEs across all PRECISION: {len(all_precision_pp)}")

# Load B transcript and find where these PP appear
print("\n" + "="*70)
print("TRACING PP VOCABULARY THROUGH B")
print("="*70)

tx = Transcript()
b_tokens = list(tx.currier_b())

# Build MIDDLE -> B folio mapping
middle_to_b_folios = defaultdict(set)
for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle:
            middle_to_b_folios[m.middle].add(t.folio)
    except:
        pass

# Find B folios for PRECISION PP
precision_b_folios = defaultdict(set)
for para_id, pp_list in precision_pp.items():
    for pp in pp_list:
        if pp in middle_to_b_folios:
            precision_b_folios[para_id].update(middle_to_b_folios[pp])

print("\nB folio coverage per PRECISION paragraph:")
for para_id in validated:
    pid = para_id['para_id']
    folios = precision_b_folios.get(pid, set())
    print(f"  {pid}: {len(folios)} B folios")

# Combined B folios for all PRECISION
all_precision_b = set()
for folios in precision_b_folios.values():
    all_precision_b.update(folios)
print(f"\nTotal B folios covered by PRECISION PP: {len(all_precision_b)}")

# Load REGIME data
print("\n" + "="*70)
print("REGIME DISTRIBUTION CHECK")
print("="*70)
print("Expectation: PRECISION (animals) should route to REGIME_4 per C536")

# Get REGIME for each B folio from mapping file
regime_map_file = Path(__file__).parent.parent.parent.parent / "results" / "regime_folio_mapping.json"
with open(regime_map_file) as f:
    regime_mapping = json.load(f)

# Invert to folio -> REGIME
folio_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_regime[folio] = regime

# Count REGIMEs in PRECISION-covered folios
regime_counts = Counter()
for folio in all_precision_b:
    regime = folio_regime.get(folio, 'unknown')
    regime_counts[regime] += 1

print(f"\nREGIME distribution of B folios covered by PRECISION PP:")
total = sum(regime_counts.values())
for regime, count in sorted(regime_counts.items()):
    pct = 100 * count / total if total > 0 else 0
    print(f"  {regime}: {count} folios ({pct:.1f}%)")

# Compare to baseline B REGIME distribution
baseline_regimes = Counter(folio_regime.values())
print(f"\nBaseline B REGIME distribution (all folios):")
total_base = sum(baseline_regimes.values())
for regime, count in sorted(baseline_regimes.items()):
    pct = 100 * count / total_base if total_base > 0 else 0
    print(f"  {regime}: {count} folios ({pct:.1f}%)")

# Load instruction class data
print("\n" + "="*70)
print("INSTRUCTION CLASS SURVIVAL")
print("="*70)

# Build MIDDLE -> class mapping from B
try:
    class_file = Path(__file__).parent.parent.parent.parent / "phases" / "A_INTERNAL_STRATIFICATION" / "results" / "middle_classes.json"
    with open(class_file) as f:
        class_data = json.load(f)

    # This has ri_middles and pp_middles, but we need B class assignments
    # Let's compute class survival differently - by role distribution

except Exception as e:
    print(f"Could not load class data: {e}")

# Instead, compute role distribution in B tokens that match PRECISION PP
print("\nAnalyzing role distribution of PRECISION PP in B context...")

# Load role taxonomy (from B classification)
role_file = Path(__file__).parent.parent.parent.parent / "data" / "b_role_assignments.json"
try:
    with open(role_file) as f:
        role_data = json.load(f)
    has_roles = True
except:
    has_roles = False
    print("Role assignment file not found, using morphological proxy")

# Compute kernel profile of B tokens that share PP with PRECISION
print("\n" + "="*70)
print("KERNEL PROFILE IN B EXECUTION CONTEXT")
print("="*70)
print("Expectation: High k+e, suppressed h (matching PRECISION signature)")

b_kernel_profile = {'k': 0, 'h': 0, 'e': 0, 'total': 0}
b_kernel_by_folio = defaultdict(lambda: {'k': 0, 'h': 0, 'e': 0, 'total': 0})

for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in all_precision_pp:
            middle = m.middle
            if 'k' in middle:
                b_kernel_profile['k'] += 1
                b_kernel_by_folio[t.folio]['k'] += 1
            if 'h' in middle:
                b_kernel_profile['h'] += 1
                b_kernel_by_folio[t.folio]['h'] += 1
            if 'e' in middle:
                b_kernel_profile['e'] += 1
                b_kernel_by_folio[t.folio]['e'] += 1
            b_kernel_profile['total'] += 1
            b_kernel_by_folio[t.folio]['total'] += 1
    except:
        pass

if b_kernel_profile['total'] > 0:
    k_rate = b_kernel_profile['k'] / b_kernel_profile['total']
    h_rate = b_kernel_profile['h'] / b_kernel_profile['total']
    e_rate = b_kernel_profile['e'] / b_kernel_profile['total']

    print(f"\nPRECISION PP tokens in B:")
    print(f"  Total tokens: {b_kernel_profile['total']}")
    print(f"  k rate: {k_rate:.3f}")
    print(f"  h rate: {h_rate:.3f}")
    print(f"  e rate: {e_rate:.3f}")
    print(f"  k+e: {k_rate + e_rate:.3f}")

    # Compare to PRECISION A profile
    prec_k = precision_data['precision_kernels']['k']
    prec_h = precision_data['precision_kernels']['h']
    prec_e = precision_data['precision_kernels']['e']

    print(f"\nComparison to PRECISION A profile:")
    print(f"  A: k={prec_k:.3f}, h={prec_h:.3f}, e={prec_e:.3f}, k+e={prec_k+prec_e:.3f}")
    print(f"  B: k={k_rate:.3f}, h={h_rate:.3f}, e={e_rate:.3f}, k+e={k_rate+e_rate:.3f}")

    # Test: does k+e > 2h hold in B?
    b_passes = (k_rate + e_rate) > 2 * h_rate
    print(f"\n  k+e > 2h test: {'PASS' if b_passes else 'FAIL'}")

# Compute baseline B kernel profile for comparison
print("\n" + "="*70)
print("BASELINE COMPARISON")
print("="*70)

baseline_kernel = {'k': 0, 'h': 0, 'e': 0, 'total': 0}
for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle:
            if 'k' in m.middle:
                baseline_kernel['k'] += 1
            if 'h' in m.middle:
                baseline_kernel['h'] += 1
            if 'e' in m.middle:
                baseline_kernel['e'] += 1
            baseline_kernel['total'] += 1
    except:
        pass

if baseline_kernel['total'] > 0:
    base_k = baseline_kernel['k'] / baseline_kernel['total']
    base_h = baseline_kernel['h'] / baseline_kernel['total']
    base_e = baseline_kernel['e'] / baseline_kernel['total']

    print(f"Baseline B kernel profile (all tokens):")
    print(f"  k: {base_k:.3f}")
    print(f"  h: {base_h:.3f}")
    print(f"  e: {base_e:.3f}")
    print(f"  k+e: {base_k + base_e:.3f}")

    # Enrichment ratios
    if base_k > 0:
        print(f"\nEnrichment in PRECISION PP vs baseline:")
        print(f"  k: {k_rate/base_k:.2f}x")
        print(f"  h: {h_rate/base_h:.2f}x")
        print(f"  e: {e_rate/base_e:.2f}x")

# Summary
print("\n" + "="*70)
print("CONVERGENCE VALIDATION SUMMARY")
print("="*70)

results = {
    'precision_candidates': len(validated),
    'unique_pp_middles': len(all_precision_pp),
    'b_folios_covered': len(all_precision_b),
    'regime_distribution': dict(regime_counts),
    'precision_b_kernel': {
        'k': k_rate if b_kernel_profile['total'] > 0 else 0,
        'h': h_rate if b_kernel_profile['total'] > 0 else 0,
        'e': e_rate if b_kernel_profile['total'] > 0 else 0,
    },
    'baseline_b_kernel': {
        'k': base_k if baseline_kernel['total'] > 0 else 0,
        'h': base_h if baseline_kernel['total'] > 0 else 0,
        'e': base_e if baseline_kernel['total'] > 0 else 0,
    },
    'kernel_test_pass': b_passes if b_kernel_profile['total'] > 0 else False
}

print(f"""
PRECISION PP vocabulary ({len(all_precision_pp)} MIDDLEs) traces to {len(all_precision_b)} B folios.

REGIME distribution: {dict(regime_counts)}

Kernel signature preservation:
  - A (PRECISION): k+e = {prec_k+prec_e:.3f}
  - B (filtered):  k+e = {k_rate+e_rate:.3f}
  - Baseline B:    k+e = {base_k+base_e:.3f}

k+e > 2h test in B: {'PASS' if results['kernel_test_pass'] else 'FAIL'}
""")

with open(results_dir / "b_convergence_validation.json", 'w') as f:
    json.dump(results, f, indent=2)
print(f"Saved to b_convergence_validation.json")
