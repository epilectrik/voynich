"""
07_compound_atom_sharing.py - Compound MIDDLE Atom Sharing

Phase: MIDDLE_MATERIAL_SEMANTICS
Test 7

Question: Do folio-unique middles on structurally similar folios share more atoms?

Method:
1. Extract core atoms from all folio-unique compound middles using MiddleAnalyzer
2. Compute atom Jaccard between folio pairs
3. Correlate with structural similarity (section, regime, kernel profile)

Expected: r > 0.2, p < 0.05
"""
import sys
sys.path.insert(0, 'C:/git/voynich/scripts')

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
from voynich import Transcript, Morphology, MiddleAnalyzer

from scipy.stats import pearsonr, spearmanr
import numpy as np
import math

RESULTS_DIR = Path('C:/git/voynich/phases/MIDDLE_MATERIAL_SEMANTICS/results')
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# STEP 1: Build MiddleAnalyzer inventory for Currier B
# ============================================================
print("=" * 70)
print("COMPOUND MIDDLE ATOM SHARING")
print("=" * 70)

tx = Transcript()
morph = Morphology()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

summary = mid_analyzer.summary()
print(f"\nMiddleAnalyzer inventory summary:")
print(f"  Total MIDDLEs: {summary['total_middles']}")
print(f"  Core MIDDLEs (20+ folios): {summary['core_count']}")
print(f"  Folio-unique MIDDLEs (1 folio): {summary['folio_unique_count']}")

core_middles = mid_analyzer.get_core_middles()
folio_unique_middles = mid_analyzer.get_folio_unique_middles()

print(f"\nCore MIDDLEs: {sorted(core_middles)[:20]}...")
print(f"Folio-unique MIDDLEs: {len(folio_unique_middles)} total")

# ============================================================
# STEP 2: Collect per-folio data (section, words, middles)
# ============================================================
print("\n" + "=" * 70)
print("COLLECTING PER-FOLIO DATA")
print("=" * 70)

# Pre-compute: per-folio section, words, middles
folio_section = {}  # folio -> section
folio_words = defaultdict(list)  # folio -> [words]
folio_middles = defaultdict(set)  # folio -> set of all middles

for token in tx.currier_b():
    folio = token.folio
    folio_section[folio] = token.section
    folio_words[folio].append(token.word)
    m = morph.extract(token.word)
    if m.middle and m.middle != '_EMPTY_':
        folio_middles[folio].add(m.middle)

all_folios = sorted(folio_section.keys())
n_folios = len(all_folios)
print(f"Total Currier B folios: {n_folios}")

# Section distribution
section_counts = Counter(folio_section.values())
print(f"Section distribution: {dict(section_counts)}")

# ============================================================
# STEP 3: Identify folio-unique COMPOUND middles per folio
#         and extract their constituent atoms
# ============================================================
print("\n" + "=" * 70)
print("FOLIO-UNIQUE COMPOUND MIDDLES -> ATOM SETS")
print("=" * 70)

# For each folio, find its folio-unique middles that are compound,
# and collect the set of atoms (core middles) they contain
folio_atom_sets = {}  # folio -> set of atoms from its folio-unique compound middles
folio_compound_count = {}  # folio -> how many folio-unique compound middles it has

for folio in all_folios:
    # Get folio-unique middles present in this folio
    fu_in_folio = folio_middles[folio] & folio_unique_middles

    atoms = set()
    n_compound = 0
    for mid in fu_in_folio:
        if mid_analyzer.is_compound(mid):
            n_compound += 1
            contained = mid_analyzer.get_contained_atoms(mid)
            atoms.update(contained)

    folio_atom_sets[folio] = atoms
    folio_compound_count[folio] = n_compound

# Filter to folios that have at least 1 compound folio-unique middle
active_folios = [f for f in all_folios if len(folio_atom_sets[f]) > 0]
n_active = len(active_folios)

total_compound_fu = sum(folio_compound_count.values())
print(f"Folios with compound folio-unique MIDDLEs: {n_active} / {n_folios}")
print(f"Total compound folio-unique MIDDLEs across corpus: {total_compound_fu}")

# Show some examples
for folio in active_folios[:5]:
    fu_in_folio = folio_middles[folio] & folio_unique_middles
    compounds = [m for m in fu_in_folio if mid_analyzer.is_compound(m)]
    print(f"  {folio} (section={folio_section[folio]}): "
          f"{folio_compound_count[folio]} compound FU middles, "
          f"atoms={sorted(folio_atom_sets[folio])[:8]}")
    if compounds:
        for c in sorted(compounds)[:3]:
            print(f"    {c} -> atoms: {mid_analyzer.get_contained_atoms(c)}")

# ============================================================
# STEP 4: Compute atom Jaccard similarity between folio pairs
# ============================================================
print("\n" + "=" * 70)
print("ATOM JACCARD SIMILARITY")
print("=" * 70)

folio_idx = {f: i for i, f in enumerate(active_folios)}
n = n_active

atom_jaccard = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        si = folio_atom_sets[active_folios[i]]
        sj = folio_atom_sets[active_folios[j]]
        union = si | sj
        if len(union) == 0:
            atom_jaccard[i, j] = 0.0
        else:
            atom_jaccard[i, j] = len(si & sj) / len(union)

upper_tri_idx = np.triu_indices(n, k=1)
jaccard_upper = atom_jaccard[upper_tri_idx]
n_pairs = len(jaccard_upper)

print(f"Active folios: {n}")
print(f"Folio pairs: {n_pairs}")
print(f"Atom Jaccard statistics:")
print(f"  Mean: {np.mean(jaccard_upper):.4f}")
print(f"  Median: {np.median(jaccard_upper):.4f}")
print(f"  Std: {np.std(jaccard_upper):.4f}")
print(f"  Min: {np.min(jaccard_upper):.4f}, Max: {np.max(jaccard_upper):.4f}")

# ============================================================
# STEP 5: Compute structural similarity between folio pairs
# ============================================================
print("\n" + "=" * 70)
print("STRUCTURAL SIMILARITY")
print("=" * 70)

# Component 1: Same section (binary)
section_sim = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if folio_section[active_folios[i]] == folio_section[active_folios[j]]:
            section_sim[i, j] = 1.0

section_upper = section_sim[upper_tri_idx]
same_section_pct = 100.0 * np.mean(section_upper)
print(f"Same-section pair fraction: {same_section_pct:.1f}%")

# Component 2: Kernel profile similarity (cosine)
# Build kernel profile per folio: fraction of k, h, e characters in all words
KERNEL_CHARS = {'k', 'h', 'e'}
folio_kernel_profiles = {}

for folio in active_folios:
    k_count = 0
    h_count = 0
    e_count = 0
    total_chars = 0
    for word in folio_words[folio]:
        for c in word:
            if c == 'k':
                k_count += 1
            elif c == 'h':
                h_count += 1
            elif c == 'e':
                e_count += 1
            total_chars += 1

    if total_chars > 0:
        folio_kernel_profiles[folio] = np.array([
            k_count / total_chars,
            h_count / total_chars,
            e_count / total_chars
        ])
    else:
        folio_kernel_profiles[folio] = np.array([0.0, 0.0, 0.0])


def cosine_sim(a, b):
    """Compute cosine similarity between two vectors."""
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


kernel_sim = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        kernel_sim[i, j] = cosine_sim(
            folio_kernel_profiles[active_folios[i]],
            folio_kernel_profiles[active_folios[j]]
        )

kernel_upper = kernel_sim[upper_tri_idx]
print(f"Kernel profile cosine similarity:")
print(f"  Mean: {np.mean(kernel_upper):.4f}")
print(f"  Std: {np.std(kernel_upper):.4f}")

# Component 3: Regime similarity
# Classify each folio into a regime based on kernel profile dominance
# (k-dominant, h-dominant, e-dominant, mixed)
folio_regime = {}
for folio in active_folios:
    profile = folio_kernel_profiles[folio]
    k_frac, h_frac, e_frac = profile
    total_kernel = k_frac + h_frac + e_frac
    if total_kernel == 0:
        folio_regime[folio] = 'none'
    else:
        # Dominant if > 50% of kernel fraction
        k_rel = k_frac / total_kernel
        h_rel = h_frac / total_kernel
        e_rel = e_frac / total_kernel
        if k_rel > 0.5:
            folio_regime[folio] = 'k_dominant'
        elif h_rel > 0.5:
            folio_regime[folio] = 'h_dominant'
        elif e_rel > 0.5:
            folio_regime[folio] = 'e_dominant'
        else:
            folio_regime[folio] = 'mixed'

regime_dist = Counter(folio_regime.values())
print(f"\nRegime distribution: {dict(regime_dist)}")

regime_sim = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if folio_regime[active_folios[i]] == folio_regime[active_folios[j]]:
            regime_sim[i, j] = 1.0

regime_upper = regime_sim[upper_tri_idx]
same_regime_pct = 100.0 * np.mean(regime_upper)
print(f"Same-regime pair fraction: {same_regime_pct:.1f}%")

# Composite structural similarity: mean of section, regime, kernel cosine
# Each component is [0,1] so composite is [0,1]
structural_sim = (section_sim + regime_sim + kernel_sim) / 3.0
structural_upper = structural_sim[upper_tri_idx]

print(f"\nComposite structural similarity:")
print(f"  Mean: {np.mean(structural_upper):.4f}")
print(f"  Std: {np.std(structural_upper):.4f}")

# ============================================================
# STEP 6: Correlation analysis
# ============================================================
print("\n" + "=" * 70)
print("CORRELATION ANALYSIS")
print("=" * 70)

# Primary test: Spearman correlation between atom Jaccard and composite structural similarity
if (n_pairs > 2 and np.std(jaccard_upper) > 0 and np.std(structural_upper) > 0):
    r_spearman, p_spearman = spearmanr(jaccard_upper, structural_upper)
    r_pearson, p_pearson = pearsonr(jaccard_upper, structural_upper)
else:
    r_spearman, p_spearman = 0.0, 1.0
    r_pearson, p_pearson = 0.0, 1.0

print(f"\nAtom Jaccard vs Composite Structural Similarity:")
print(f"  Spearman r = {r_spearman:.4f}, p = {p_spearman:.6f}")
print(f"  Pearson  r = {r_pearson:.4f}, p = {p_pearson:.6f}")
print(f"  N pairs = {n_pairs}")

# Component-level correlations
component_correlations = {}

# Section similarity
if np.std(section_upper) > 0 and np.std(jaccard_upper) > 0:
    r_sec, p_sec = spearmanr(jaccard_upper, section_upper)
else:
    r_sec, p_sec = 0.0, 1.0
component_correlations['section'] = {'r': round(float(r_sec), 4), 'p': round(float(p_sec), 6)}
print(f"\n  vs Section similarity:  r={r_sec:.4f}, p={p_sec:.6f}")

# Regime similarity
if np.std(regime_upper) > 0 and np.std(jaccard_upper) > 0:
    r_reg, p_reg = spearmanr(jaccard_upper, regime_upper)
else:
    r_reg, p_reg = 0.0, 1.0
component_correlations['regime'] = {'r': round(float(r_reg), 4), 'p': round(float(p_reg), 6)}
print(f"  vs Regime similarity:   r={r_reg:.4f}, p={p_reg:.6f}")

# Kernel profile similarity
if np.std(kernel_upper) > 0 and np.std(jaccard_upper) > 0:
    r_ker, p_ker = spearmanr(jaccard_upper, kernel_upper)
else:
    r_ker, p_ker = 0.0, 1.0
component_correlations['kernel_profile'] = {'r': round(float(r_ker), 4), 'p': round(float(p_ker), 6)}
print(f"  vs Kernel profile sim:  r={r_ker:.4f}, p={p_ker:.6f}")

# ============================================================
# STEP 7: Breakdown by section (same vs different)
# ============================================================
print("\n" + "=" * 70)
print("SAME-SECTION vs CROSS-SECTION ATOM SHARING")
print("=" * 70)

same_section_jaccards = []
diff_section_jaccards = []

for idx in range(n_pairs):
    i = upper_tri_idx[0][idx]
    j = upper_tri_idx[1][idx]
    jac = jaccard_upper[idx]
    if section_upper[idx] == 1.0:
        same_section_jaccards.append(jac)
    else:
        diff_section_jaccards.append(jac)

if same_section_jaccards:
    mean_same = np.mean(same_section_jaccards)
    print(f"Same-section pairs: {len(same_section_jaccards)}, mean Jaccard: {mean_same:.4f}")
else:
    mean_same = 0.0
    print(f"Same-section pairs: 0")

if diff_section_jaccards:
    mean_diff = np.mean(diff_section_jaccards)
    print(f"Diff-section pairs: {len(diff_section_jaccards)}, mean Jaccard: {mean_diff:.4f}")
else:
    mean_diff = 0.0
    print(f"Diff-section pairs: 0")

if same_section_jaccards and diff_section_jaccards:
    enrichment_ratio = mean_same / mean_diff if mean_diff > 0 else float('inf')
    print(f"Enrichment ratio (same/diff): {enrichment_ratio:.4f}")
else:
    enrichment_ratio = None

# ============================================================
# STEP 8: Top atom-sharing folio pairs
# ============================================================
print("\n" + "=" * 70)
print("TOP ATOM-SHARING FOLIO PAIRS")
print("=" * 70)

pair_data = []
for idx in range(n_pairs):
    i = upper_tri_idx[0][idx]
    j = upper_tri_idx[1][idx]
    jac = float(jaccard_upper[idx])
    fi = active_folios[i]
    fj = active_folios[j]
    pair_data.append({
        'folio_i': fi,
        'folio_j': fj,
        'atom_jaccard': round(jac, 4),
        'same_section': folio_section[fi] == folio_section[fj],
        'same_regime': folio_regime[fi] == folio_regime[fj],
        'section_i': folio_section[fi],
        'section_j': folio_section[fj],
        'shared_atoms': sorted(folio_atom_sets[fi] & folio_atom_sets[fj]),
    })

pair_data.sort(key=lambda x: x['atom_jaccard'], reverse=True)

print(f"\nTop 10 folio pairs by atom Jaccard:")
for p in pair_data[:10]:
    sec_match = "SAME" if p['same_section'] else "DIFF"
    reg_match = "SAME" if p['same_regime'] else "DIFF"
    print(f"  {p['folio_i']} - {p['folio_j']}: J={p['atom_jaccard']:.4f} "
          f"[sec:{sec_match}, reg:{reg_match}] "
          f"atoms={p['shared_atoms'][:5]}{'...' if len(p['shared_atoms']) > 5 else ''}")

# ============================================================
# STEP 9: Verdict
# ============================================================
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

# SUPPORTED if Spearman r > 0.2 AND p < 0.05
supported = (r_spearman > 0.2 and p_spearman < 0.05)
verdict = "SUPPORTED" if supported else "NOT_SUPPORTED"

verdict_reasons = []
if r_spearman > 0.2:
    verdict_reasons.append(f"Spearman r={r_spearman:.4f} > 0.2 threshold")
else:
    verdict_reasons.append(f"Spearman r={r_spearman:.4f} <= 0.2 threshold")

if p_spearman < 0.05:
    verdict_reasons.append(f"p={p_spearman:.6f} < 0.05 significance")
else:
    verdict_reasons.append(f"p={p_spearman:.6f} >= 0.05 significance")

notes = (
    f"Compound folio-unique MIDDLEs from {n_active} Currier B folios "
    f"decomposed into core atoms. "
    f"Atom Jaccard vs composite structural similarity: "
    f"Spearman r={r_spearman:.4f} (p={p_spearman:.6f}). "
    f"Component correlations: section r={r_sec:.4f}, "
    f"regime r={r_reg:.4f}, kernel r={r_ker:.4f}. "
    f"Same-section mean Jaccard={mean_same:.4f} vs "
    f"cross-section={mean_diff:.4f}"
    + (f" (enrichment={enrichment_ratio:.2f}x)." if enrichment_ratio and enrichment_ratio != float('inf') else ".")
)

print(f"\nVerdict: {verdict}")
for reason in verdict_reasons:
    print(f"  - {reason}")
print(f"\n{notes}")

# ============================================================
# STEP 10: Save results
# ============================================================
# Serialize top pairs for JSON (limit to top 20)
top_pairs_json = []
for p in pair_data[:20]:
    top_pairs_json.append({
        'folio_i': p['folio_i'],
        'folio_j': p['folio_j'],
        'atom_jaccard': p['atom_jaccard'],
        'same_section': p['same_section'],
        'same_regime': p['same_regime'],
        'shared_atoms': p['shared_atoms'],
    })

output = {
    "test": "Compound MIDDLE Atom Sharing",
    "n_currier_b_folios": n_folios,
    "n_active_folios": n_active,
    "n_folio_pairs": n_pairs,
    "total_compound_folio_unique_middles": total_compound_fu,
    "n_core_middles": len(core_middles),
    "n_folio_unique_middles": len(folio_unique_middles),
    "atom_jaccard_stats": {
        "mean": round(float(np.mean(jaccard_upper)), 4),
        "median": round(float(np.median(jaccard_upper)), 4),
        "std": round(float(np.std(jaccard_upper)), 4),
        "min": round(float(np.min(jaccard_upper)), 4),
        "max": round(float(np.max(jaccard_upper)), 4),
    },
    "structural_similarity_stats": {
        "mean": round(float(np.mean(structural_upper)), 4),
        "std": round(float(np.std(structural_upper)), 4),
    },
    "spearman_r": round(float(r_spearman), 4),
    "spearman_p": round(float(p_spearman), 6),
    "pearson_r": round(float(r_pearson), 4),
    "pearson_p": round(float(p_pearson), 6),
    "component_correlations": component_correlations,
    "same_section_mean_jaccard": round(float(mean_same), 4),
    "diff_section_mean_jaccard": round(float(mean_diff), 4),
    "section_enrichment_ratio": round(float(enrichment_ratio), 4) if enrichment_ratio and enrichment_ratio != float('inf') else None,
    "regime_distribution": dict(regime_dist),
    "top_pairs": top_pairs_json,
    "verdict": verdict,
    "notes": notes,
}

output_path = RESULTS_DIR / 'compound_atom_sharing.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
