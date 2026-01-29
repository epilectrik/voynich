"""
T3: Material Class Alignment

H0: PP vocabulary shows random distribution across B sections
H1: Specific PP subsets preferentially appear in specific B sections

Method: Test whether A-section-specific vocabulary preferentially matches B-section vocabulary
Threshold: Cramer's V > 0.2 and p < 0.01 to support H1

Note: This uses manuscript sections (H=Herbal, P=Pharma, B=Biological, etc.) as proxy
for material class, since explicit material class markers are not well-established.
"""

import sys, json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=== T3: MATERIAL CLASS ALIGNMENT ===\n")

# Build A folio data by section
print("Building A folio data by section...")
a_section_middles = defaultdict(set)  # section -> set of MIDDLEs
a_folio_section = {}
a_folio_middles = defaultdict(set)

for t in tx.currier_a():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        a_section_middles[t.section].add(m.middle)
        a_folio_middles[t.folio].add(m.middle)
    if t.folio not in a_folio_section:
        a_folio_section[t.folio] = t.section

# Build B folio data by section
b_section_middles = defaultdict(set)
b_folio_section = {}
b_folio_middles = defaultdict(set)

for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_section_middles[t.section].add(m.middle)
        b_folio_middles[t.folio].add(m.middle)
    if t.folio not in b_folio_section:
        b_folio_section[t.folio] = t.section

a_sections = sorted(a_section_middles.keys())
b_sections = sorted(b_section_middles.keys())

print(f"A sections: {[(s, len(a_section_middles[s])) for s in a_sections]}")
print(f"B sections: {[(s, len(b_section_middles[s])) for s in b_sections]}")

# Find section-exclusive MIDDLEs in A
# These are MIDDLEs that appear in only one A section
middle_to_a_sections = defaultdict(set)
for sec in a_sections:
    for mid in a_section_middles[sec]:
        middle_to_a_sections[mid].add(sec)

a_exclusive_middles = defaultdict(set)  # section -> MIDDLEs exclusive to that section
for mid, secs in middle_to_a_sections.items():
    if len(secs) == 1:
        a_exclusive_middles[list(secs)[0]].add(mid)

print(f"\nA-section exclusive MIDDLEs:")
for sec in a_sections:
    print(f"  {sec}: {len(a_exclusive_middles[sec])} exclusive MIDDLEs")

# For each A-section-exclusive MIDDLE, check which B sections contain it
print("\n=== A-EXCLUSIVE MIDDLES IN B SECTIONS ===\n")

# Build contingency table: A-exclusive-from-section X present-in-B-section
# Rows = A section of origin, Cols = B section where it appears

contingency_data = []
for a_sec in a_sections:
    for mid in a_exclusive_middles[a_sec]:
        # Which B sections contain this MIDDLE?
        for b_sec in b_sections:
            if mid in b_section_middles[b_sec]:
                contingency_data.append({'a_sec': a_sec, 'b_sec': b_sec, 'middle': mid})

# Count A-section x B-section co-occurrences
contingency_counts = Counter((d['a_sec'], d['b_sec']) for d in contingency_data)

# Build matrix
contingency_matrix = np.zeros((len(a_sections), len(b_sections)))
for i, a_sec in enumerate(a_sections):
    for j, b_sec in enumerate(b_sections):
        contingency_matrix[i, j] = contingency_counts.get((a_sec, b_sec), 0)

print("Contingency table (A-exclusive MIDDLEs appearing in B sections):")
print(f"\n{'':>8s}", end='')
for b_sec in b_sections:
    print(f"  B-{b_sec:>2s}", end='')
print("    Total")
print("-" * (12 + 7 * len(b_sections)))

for i, a_sec in enumerate(a_sections):
    print(f"A-{a_sec:>2s}   ", end='')
    for j in range(len(b_sections)):
        print(f"  {int(contingency_matrix[i, j]):>4d}", end='')
    print(f"    {int(contingency_matrix[i, :].sum()):>4d}")

print(f"{'Total':>8s}", end='')
for j in range(len(b_sections)):
    print(f"  {int(contingency_matrix[:, j].sum()):>4d}", end='')
print(f"    {int(contingency_matrix.sum()):>4d}")

# Chi-square test
if contingency_matrix.sum() > 0:
    # Remove rows/cols with zero marginal totals
    row_mask = contingency_matrix.sum(axis=1) > 0
    col_mask = contingency_matrix.sum(axis=0) > 0
    filtered_matrix = contingency_matrix[row_mask][:, col_mask]

    if filtered_matrix.shape[0] > 1 and filtered_matrix.shape[1] > 1:
        chi2, p_chi, dof, expected = stats.chi2_contingency(filtered_matrix)
        n = filtered_matrix.sum()
        k = min(filtered_matrix.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * k)) if n * k > 0 else 0

        print(f"\nChi-square test:")
        print(f"  chi2 = {chi2:.2f}, dof = {dof}, p = {p_chi:.2e}")
        print(f"  Cramer's V = {cramers_v:.4f}")
    else:
        chi2, p_chi, cramers_v = 0, 1, 0
        print("\nInsufficient data for chi-square test")
else:
    chi2, p_chi, cramers_v = 0, 1, 0
    print("\nNo A-exclusive MIDDLEs found in B")

# Also test: do A-H exclusive MIDDLEs preferentially appear in B-H?
print("\n=== SECTION-SPECIFIC ALIGNMENT TEST ===\n")

# Focus on the largest A section (H = Herbal) and test if its exclusive vocabulary
# preferentially appears in herbal-related B sections (H, S)

if 'H' in a_exclusive_middles and len(a_exclusive_middles['H']) > 0:
    h_exclusive = a_exclusive_middles['H']

    h_in_b_h = len(h_exclusive & b_section_middles.get('H', set()))
    h_in_b_s = len(h_exclusive & b_section_middles.get('S', set()))
    h_in_b_other = len(h_exclusive) - h_in_b_h - h_in_b_s

    # What fraction of H-exclusive MIDDLEs appear in B-H vs other B sections?
    total_h_in_b = sum(1 for mid in h_exclusive if any(mid in b_section_middles[s] for s in b_sections))

    print(f"A-Herbal exclusive MIDDLEs: {len(h_exclusive)}")
    print(f"  Appearing in B-H: {h_in_b_h} ({h_in_b_h/len(h_exclusive)*100:.1f}%)")
    print(f"  Appearing in B-S: {h_in_b_s} ({h_in_b_s/len(h_exclusive)*100:.1f}%)")
    print(f"  Appearing anywhere in B: {total_h_in_b} ({total_h_in_b/len(h_exclusive)*100:.1f}%)")

    # Expected under null: B sections have different sizes, so expected proportion
    # is based on B section vocabulary sizes
    total_b_vocab = sum(len(b_section_middles[s]) for s in b_sections)
    expected_h = len(b_section_middles.get('H', set())) / total_b_vocab if total_b_vocab > 0 else 0
    expected_s = len(b_section_middles.get('S', set())) / total_b_vocab if total_b_vocab > 0 else 0

    print(f"\n  Expected under null (proportional to B section size):")
    print(f"    B-H: {expected_h*100:.1f}%")
    print(f"    B-S: {expected_s*100:.1f}%")

    # Binomial test: is A-H exclusive presence in B-H higher than expected?
    if total_h_in_b > 0:
        observed_h_rate = h_in_b_h / total_h_in_b
        from scipy.stats import binomtest
        binom_result = binomtest(h_in_b_h, total_h_in_b, expected_h, alternative='greater')
        print(f"\n  Binomial test (A-H exclusive in B-H vs expected):")
        print(f"    Observed: {observed_h_rate*100:.1f}%, Expected: {expected_h*100:.1f}%")
        print(f"    p-value (one-sided): {binom_result.pvalue:.4f}")
        binom_p = binom_result.pvalue
    else:
        binom_p = 1.0
else:
    binom_p = 1.0
    print("Insufficient A-Herbal exclusive MIDDLEs for analysis")

# Verdict
threshold_v = 0.2
threshold_p = 0.01

if cramers_v > threshold_v and p_chi < threshold_p:
    verdict = "SECTION_ALIGNMENT"
    explanation = f"Cramer's V={cramers_v:.3f} > 0.2 with p < 0.01: A-section vocabulary aligns with B-sections"
elif cramers_v > 0.1:
    verdict = "WEAK_ALIGNMENT"
    explanation = f"Cramer's V={cramers_v:.3f} shows weak section alignment"
else:
    verdict = "NO_ALIGNMENT"
    explanation = f"Cramer's V={cramers_v:.3f} shows no section-specific vocabulary alignment"

print(f"\n=== VERDICT: {verdict} ===")
print(f"  {explanation}")

# Save results
results = {
    'test': 'T3_material_class_alignment',
    'a_sections': a_sections,
    'b_sections': b_sections,
    'a_exclusive_counts': {sec: len(mids) for sec, mids in a_exclusive_middles.items()},
    'contingency_matrix': contingency_matrix.tolist(),
    'chi_square': {
        'chi2': float(chi2),
        'p': float(p_chi),
        'cramers_v': float(cramers_v),
    },
    'h_exclusive_test': {
        'binom_p': float(binom_p) if 'H' in a_exclusive_middles else None,
    },
    'threshold': {
        'cramers_v': threshold_v,
        'p': threshold_p,
    },
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / 't3_material_class_alignment.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
