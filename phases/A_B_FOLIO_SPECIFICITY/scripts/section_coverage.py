"""
Test whether A folio section identity predicts which B folios it serves,
after controlling for pool size.

T8: Section-to-section coverage (raw)
T9: Residual specificity (pool-size removed)
T10: Folio length -> pool size correlation

Questions:
1. Do Herbal A folios preferentially cover Herbal B folios?
2. Does normalizing for pool size reveal hidden specificity?
3. Does folio line count drive pool size?

Extends: C734-C739 (A_B_FOLIO_SPECIFICITY)
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

rng = np.random.RandomState(42)

# Build B MIDDLE set for PP classification
b_middles = set()
for token in tx.currier_b():
    m = morph.extract(token.word)
    if m.middle:
        b_middles.add(m.middle)

# Build A folio PP pools
print("Building A folio PP pools...")
a_folio_pools = {}
a_folio_section = {}
a_folio_nlines = {}

a_data = defaultdict(lambda: defaultdict(list))
for t in tx.currier_a():
    a_data[t.folio][t.line].append(t)
    if t.folio not in a_folio_section:
        a_folio_section[t.folio] = t.section

for fol in sorted(a_data.keys()):
    mids, prefs, sufs = set(), set(), set()
    for ln in a_data[fol]:
        for t in a_data[fol][ln]:
            m = morph.extract(t.word)
            if m.middle and m.middle in b_middles:
                mids.add(m.middle)
                if m.prefix:
                    prefs.add(m.prefix)
                if m.suffix:
                    sufs.add(m.suffix)
    a_folio_pools[fol] = (mids, prefs, sufs)
    a_folio_nlines[fol] = len(a_data[fol])

# Collect B folio tokens
b_folio_tokens = defaultdict(list)
b_folio_section = {}
b_folio_morphs = {}
for t in tx.currier_b():
    w = t.word.strip()
    if not w or '*' in w:
        continue
    b_folio_tokens[t.folio].append(w)
    if t.folio not in b_folio_section:
        b_folio_section[t.folio] = t.section

b_folios = sorted(b_folio_tokens.keys())
a_folios = sorted(a_folio_pools.keys())

# Pre-compute B morphologies
for b_fol in b_folios:
    b_folio_morphs[b_fol] = [morph.extract(w) for w in b_folio_tokens[b_fol]]

print(f"  {len(a_folios)} A folios, {len(b_folios)} B folios")

# ============================================================
# Compute full coverage matrix
# ============================================================
print("\nComputing coverage matrix...")

coverage = np.zeros((len(a_folios), len(b_folios)))
for i, a_fol in enumerate(a_folios):
    a_m, a_p, a_s = a_folio_pools[a_fol]
    for j, b_fol in enumerate(b_folios):
        tokens = b_folio_tokens[b_fol]
        morphs_list = b_folio_morphs[b_fol]
        legal = 0
        for w, mo in zip(tokens, morphs_list):
            if not mo.middle or mo.middle not in a_m:
                continue
            if mo.prefix and mo.prefix not in a_p:
                continue
            if mo.suffix and mo.suffix not in a_s:
                continue
            legal += 1
        coverage[i, j] = legal / len(tokens) if tokens else 0

# ============================================================
# Build section indices
# ============================================================
a_sections = sorted(set(a_folio_section.values()))
b_sections = sorted(set(b_folio_section.values()))

a_sec_idx = defaultdict(list)
b_sec_idx = defaultdict(list)
for i, fol in enumerate(a_folios):
    a_sec_idx[a_folio_section[fol]].append(i)
for j, fol in enumerate(b_folios):
    b_sec_idx[b_folio_section[fol]].append(j)

results = {}

# ============================================================
# T8: Section-to-section raw coverage
# ============================================================
print("\n=== T8: SECTION-TO-SECTION RAW COVERAGE ===\n")

sec_matrix_raw = {}
for a_sec in a_sections:
    a_idx = a_sec_idx[a_sec]
    sec_matrix_raw[a_sec] = {}
    for b_sec in b_sections:
        b_idx = b_sec_idx[b_sec]
        sub = coverage[np.ix_(a_idx, b_idx)]
        sec_matrix_raw[a_sec][b_sec] = float(sub.mean())

print(f"A sections: {[(s, len(a_sec_idx[s])) for s in a_sections]}")
print(f"B sections: {[(s, len(b_sec_idx[s])) for s in b_sections]}")
print(f"\n{'':>12s}", end='')
for bs in b_sections:
    print(f"  B-{bs:>3s}", end='')
print(f"  {'Pool':>6s}  {'Lines':>5s}")
print("-" * 70)

sec_pool_means = {}
sec_line_means = {}
for a_sec in a_sections:
    a_idx = a_sec_idx[a_sec]
    pools = [len(a_folio_pools[a_folios[i]][0]) for i in a_idx]
    lines = [a_folio_nlines[a_folios[i]] for i in a_idx]
    sec_pool_means[a_sec] = float(np.mean(pools))
    sec_line_means[a_sec] = float(np.mean(lines))
    print(f"A-{a_sec:>3s} (n={len(a_idx):>3d})", end='')
    for b_sec in b_sections:
        print(f"  {sec_matrix_raw[a_sec][b_sec]*100:5.1f}%", end='')
    print(f"  {np.mean(pools):5.1f}  {np.mean(lines):5.1f}")

results['T8_section_raw'] = {
    'section_matrix': sec_matrix_raw,
    'a_section_counts': {s: len(a_sec_idx[s]) for s in a_sections},
    'b_section_counts': {s: len(b_sec_idx[s]) for s in b_sections},
    'a_section_pool_means': sec_pool_means,
    'a_section_line_means': sec_line_means,
}

# ============================================================
# T9: Pool-size normalized residual specificity
# ============================================================
print("\n=== T9: POOL-SIZE NORMALIZED RESIDUAL SPECIFICITY ===\n")

pool_sizes_arr = np.array([len(a_folio_pools[a_folios[i]][0]) for i in range(len(a_folios))])
mean_cov_per_a = coverage.mean(axis=1)

slope, intercept, r_val, p_val, std_err = stats.linregress(pool_sizes_arr, mean_cov_per_a)
print(f"Coverage ~ pool_size: slope={slope:.4f}, intercept={intercept:.4f}, r={r_val:.3f}")

expected_cov = slope * pool_sizes_arr + intercept
residual = coverage - expected_cov[:, np.newaxis]

# Section-to-section residual matrix
sec_matrix_resid = {}
for a_sec in a_sections:
    a_idx = a_sec_idx[a_sec]
    sec_matrix_resid[a_sec] = {}
    for b_sec in b_sections:
        b_idx = b_sec_idx[b_sec]
        sub = residual[np.ix_(a_idx, b_idx)]
        sec_matrix_resid[a_sec][b_sec] = float(sub.mean())

print(f"\n{'':>12s}", end='')
for bs in b_sections:
    print(f"  B-{bs:>3s}", end='')
print()
print("-" * 55)
for a_sec in a_sections:
    a_idx = a_sec_idx[a_sec]
    print(f"A-{a_sec:>3s} (n={len(a_idx):>3d})", end='')
    for b_sec in b_sections:
        print(f"  {sec_matrix_resid[a_sec][b_sec]*100:+5.1f}%", end='')
    print()

# Residual best-match assignment
b_assignments_resid = []
for j, b_fol in enumerate(b_folios):
    col = residual[:, j]
    best_i = np.argmax(col)
    best_a = a_folios[best_i]
    second_i = np.argsort(-col)[1]
    second_a = a_folios[second_i]
    b_assignments_resid.append({
        'b_folio': b_fol,
        'b_section': b_folio_section[b_fol],
        'best_a': best_a,
        'best_a_section': a_folio_section[best_a],
        'best_resid': float(col[best_i]),
        'gap': float(col[best_i] - col[second_i]),
    })

unique_a_resid = len(set(ba['best_a'] for ba in b_assignments_resid))
same_sec_resid = sum(1 for ba in b_assignments_resid if ba['best_a_section'] == ba['b_section'])
gaps_resid = [ba['gap'] for ba in b_assignments_resid]

print(f"\nResidual best-match: {unique_a_resid} unique A folios used / {len(a_folios)}")
print(f"Same-section matches: {same_sec_resid}/{len(b_assignments_resid)} ({same_sec_resid/len(b_assignments_resid)*100:.0f}%)")
print(f"Mean residual gap: {np.mean(gaps_resid)*100:.2f}pp")

# Permutation test: is 33% same-section match rate above chance?
# Under null: shuffle A folio section labels, recount same-section matches
n_perm = 10000
null_same_sec = np.zeros(n_perm)
a_section_labels = [a_folio_section[a_folios[i]] for i in range(len(a_folios))]

for p in range(n_perm):
    shuffled = list(a_section_labels)
    rng.shuffle(shuffled)
    count = 0
    for ba in b_assignments_resid:
        best_i = [k for k, f in enumerate(a_folios) if f == ba['best_a']][0]
        if shuffled[best_i] == ba['b_section']:
            count += 1
    null_same_sec[p] = count

null_mean = null_same_sec.mean()
null_std = null_same_sec.std()
z_sec = (same_sec_resid - null_mean) / null_std if null_std > 0 else 0
p_sec = np.mean(null_same_sec >= same_sec_resid)

print(f"\nPermutation test (section alignment):")
print(f"  Observed same-section: {same_sec_resid}")
print(f"  Null mean: {null_mean:.1f}, null std: {null_std:.2f}")
print(f"  z-score: {z_sec:.2f}, p-value: {p_sec:.4f}")

verdict_sec = 'SECTION_ROUTING' if p_sec < 0.01 else ('MARGINAL' if p_sec < 0.05 else 'NO_ROUTING')
print(f"  Verdict: {verdict_sec}")

# A-H specificity for B-H vs rest
a_h_idx = a_sec_idx.get('H', [])
b_h_idx = b_sec_idx.get('H', [])
b_not_h_idx = [j for j in range(len(b_folios)) if j not in set(b_h_idx)]
if a_h_idx and b_h_idx and b_not_h_idx:
    resid_ah_bh = residual[np.ix_(a_h_idx, b_h_idx)].mean()
    resid_ah_brest = residual[np.ix_(a_h_idx, b_not_h_idx)].mean()
    t_stat, t_p = stats.ttest_ind(
        residual[np.ix_(a_h_idx, b_h_idx)].flatten(),
        residual[np.ix_(a_h_idx, b_not_h_idx)].flatten()
    )
    print(f"\nA-H specificity:")
    print(f"  A-H -> B-H residual: {resid_ah_bh*100:+.2f}%")
    print(f"  A-H -> B-rest residual: {resid_ah_brest*100:+.2f}%")
    print(f"  t-test: t={t_stat:.2f}, p={t_p:.2e}")
    ah_specificity = {
        'ah_to_bh': float(resid_ah_bh),
        'ah_to_brest': float(resid_ah_brest),
        't_stat': float(t_stat),
        'p_value': float(t_p),
    }
else:
    ah_specificity = None

results['T9_residual_specificity'] = {
    'regression': {
        'slope': float(slope),
        'intercept': float(intercept),
        'r': float(r_val),
        'p': float(p_val),
    },
    'section_residual_matrix': sec_matrix_resid,
    'unique_a_folios_used': unique_a_resid,
    'same_section_matches': same_sec_resid,
    'same_section_rate': same_sec_resid / len(b_assignments_resid),
    'permutation_test': {
        'n_permutations': n_perm,
        'null_mean': float(null_mean),
        'null_std': float(null_std),
        'z_score': float(z_sec),
        'p_value': float(p_sec),
        'verdict': verdict_sec,
    },
    'ah_specificity': ah_specificity,
    'mean_residual_gap_pp': float(np.mean(gaps_resid) * 100),
}

# ============================================================
# T10: Folio length -> pool size correlation
# ============================================================
print("\n=== T10: FOLIO LENGTH -> POOL SIZE ===\n")

lengths = np.array([a_folio_nlines[a_folios[i]] for i in range(len(a_folios))])
r_len, p_len = stats.spearmanr(pool_sizes_arr, lengths)
print(f"Pool size vs folio length: Spearman r={r_len:.3f}, p={p_len:.2e}")

# By section
sec_stats = {}
for sec in a_sections:
    idx = a_sec_idx[sec]
    if len(idx) < 5:
        continue
    sec_pools = [len(a_folio_pools[a_folios[i]][0]) for i in idx]
    sec_lines = [a_folio_nlines[a_folios[i]] for i in idx]
    r_s, p_s = stats.spearmanr(sec_pools, sec_lines) if len(idx) >= 5 else (0, 1)
    sec_stats[sec] = {
        'n': len(idx),
        'pool_mean': float(np.mean(sec_pools)),
        'pool_std': float(np.std(sec_pools)),
        'lines_mean': float(np.mean(sec_lines)),
        'lines_std': float(np.std(sec_lines)),
        'within_section_r': float(r_s),
        'within_section_p': float(p_s),
    }
    print(f"  {sec} (n={len(idx)}): pool={np.mean(sec_pools):.1f}+/-{np.std(sec_pools):.1f}, "
          f"lines={np.mean(sec_lines):.1f}+/-{np.std(sec_lines):.1f}, r={r_s:.3f}")

results['T10_length_pool'] = {
    'overall_spearman_r': float(r_len),
    'overall_spearman_p': float(p_len),
    'by_section': sec_stats,
}

# ============================================================
# Save results
# ============================================================
out_path = Path(__file__).resolve().parent.parent / 'results' / 'section_coverage.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"\nResults saved to {out_path}")

# Summary
print("\n=== SUMMARY ===\n")
print(f"T8: Section-to-section raw coverage shows A-T (3 folios) dominates at 60-68%,")
print(f"    but this is pool-size driven (mean 78 MIDs vs 35.6 for A-H).")
print(f"T9: After pool-size regression (r={r_val:.3f}), residual specificity emerges:")
print(f"    {unique_a_resid} distinct A folios used, {same_sec_resid}/{len(b_assignments_resid)} same-section")
print(f"    Permutation z={z_sec:.2f}, p={p_sec:.4f} -> {verdict_sec}")
if ah_specificity:
    print(f"    A-H -> B-H: {ah_specificity['ah_to_bh']*100:+.2f}% vs B-rest: {ah_specificity['ah_to_brest']*100:+.2f}%")
    print(f"    t={ah_specificity['t_stat']:.2f}, p={ah_specificity['p_value']:.2e}")
print(f"T10: Folio length -> pool size: r={r_len:.3f}, p={p_len:.2e}")
