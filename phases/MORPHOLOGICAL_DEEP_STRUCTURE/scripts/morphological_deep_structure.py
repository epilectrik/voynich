#!/usr/bin/env python3
"""
Phase 379: Morphological Deep Structure

5-test battery combining suffix sequential microstructure and compound MIDDLE
composition rules.

T1: Suffix Sequential Signal Decomposition
T2: Suffix-Role PREFIX Mediation Test
T3: Compound Atom Position Grammar
T4: Compound Atom Co-Occurrence Rules
T5: Compound Depth-Specificity Gradient

All Tier 2 targets. Expert-advisor validated.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from scipy.stats import chi2_contingency, spearmanr, mannwhitneyu, kruskal, fisher_exact

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS = ROOT / "phases" / "MORPHOLOGICAL_DEEP_STRUCTURE" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# ============================================================
# ROLE TAXONOMY (from BCSC)
# ============================================================

ROLE_TAXONOMY = {
    'CC': {10, 11, 12, 17},
    'EN': {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL': {7, 30, 38, 40},
    'FQ': {9, 13, 14, 23},
    'AX': {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}

CLASS_TO_ROLE = {}
for role, classes in ROLE_TAXONOMY.items():
    for cls in classes:
        CLASS_TO_ROLE[cls] = role

# PREFIX families for C611 role assignment of UN tokens
PREFIX_ROLE_MAP = {
    'ch': 'EN', 'sh': 'EN',
    'qo': 'AX',
    'da': 'AX', 'sa': 'AX',
    'ok': 'AX', 'ot': 'AX', 'ol': 'AX', 'ct': 'AX',
}


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load all shared data."""
    tx = Transcript()
    morph = Morphology()

    # Load 49-class mapping
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Build PREFIX→role from classified tokens (for C611 UN assignment)
    prefix_role_counts = defaultdict(Counter)
    for word, cls in token_to_class.items():
        m = morph.extract(word)
        role = CLASS_TO_ROLE.get(cls, 'UN')
        prefix_key = m.prefix if m.prefix else '_BARE_'
        prefix_role_counts[prefix_key][role] += 1

    # For each PREFIX, find dominant role
    prefix_dominant_role = {}
    for prefix, counts in prefix_role_counts.items():
        prefix_dominant_role[prefix] = counts.most_common(1)[0][0]

    # Build token list with morphology + class + role
    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        cls = token_to_class.get(t.word)
        if cls:
            role = CLASS_TO_ROLE.get(cls, 'UN')
        else:
            # C611: assign UN tokens role via PREFIX
            prefix_key = m.prefix if m.prefix else '_BARE_'
            role = prefix_dominant_role.get(prefix_key,
                   PREFIX_ROLE_MAP.get(m.prefix, 'UN'))
        tokens.append({
            'word': t.word,
            'folio': t.folio,
            'line': t.line,
            'section': t.section,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'cls': cls,
            'role': role,
            'line_initial': t.line_initial,
            'line_final': t.line_final,
        })

    return tokens, token_to_class, morph


def cramers_v(contingency_table):
    """Compute Cramér's V from a contingency table."""
    table = np.array(contingency_table)
    if table.sum() == 0:
        return 0.0
    chi2, _, _, _ = chi2_contingency(table)
    n = table.sum()
    r, k = table.shape
    return float(np.sqrt(chi2 / (n * (min(r, k) - 1)))) if min(r, k) > 1 else 0.0


# ============================================================
# T1: SUFFIX SEQUENTIAL SIGNAL DECOMPOSITION
# ============================================================

def run_t1(tokens):
    """Decompose C1002's V=0.063 suffix bigram signal into artifact components."""
    print("\n" + "=" * 60)
    print("T1: Suffix Sequential Signal Decomposition")
    print("=" * 60)

    # Build within-line suffix bigrams
    # Group tokens by (folio, line)
    line_tokens = defaultdict(list)
    for t in tokens:
        line_tokens[(t['folio'], t['line'])].append(t)

    # Extract bigrams
    all_bigrams = []
    for key in sorted(line_tokens.keys()):
        toks = line_tokens[key]
        for i in range(len(toks) - 1):
            suf1 = toks[i]['suffix'] if toks[i]['suffix'] else 'NONE'
            suf2 = toks[i + 1]['suffix'] if toks[i + 1]['suffix'] else 'NONE'
            role1 = toks[i]['role']
            role2 = toks[i + 1]['role']
            word1 = toks[i]['word']
            word2 = toks[i + 1]['word']
            section = toks[i]['section']
            all_bigrams.append({
                'suf1': suf1, 'suf2': suf2,
                'role1': role1, 'role2': role2,
                'word1': word1, 'word2': word2,
                'section': section,
                'same_token': word1 == word2,
            })

    print(f"  Total suffix bigrams: {len(all_bigrams)}")

    # Get suffix vocabulary
    all_suffixes = sorted(set(b['suf1'] for b in all_bigrams) |
                          set(b['suf2'] for b in all_bigrams))
    suf_idx = {s: i for i, s in enumerate(all_suffixes)}
    n_suf = len(all_suffixes)

    def build_bigram_table(bigrams):
        """Build suffix bigram contingency table."""
        table = np.zeros((n_suf, n_suf), dtype=float)
        for b in bigrams:
            table[suf_idx[b['suf1']], suf_idx[b['suf2']]] += 1
        return table

    def compute_v(table):
        """Compute Cramér's V, handling zero tables."""
        if table.sum() < 10:
            return 0.0, 1.0
        # Remove all-zero rows/cols for chi2
        row_mask = table.sum(axis=1) > 0
        col_mask = table.sum(axis=0) > 0
        reduced = table[np.ix_(row_mask, col_mask)]
        if reduced.shape[0] < 2 or reduced.shape[1] < 2:
            return 0.0, 1.0
        chi2, p, _, _ = chi2_contingency(reduced)
        n = reduced.sum()
        r, k = reduced.shape
        v = float(np.sqrt(chi2 / (n * (min(r, k) - 1))))
        return v, p

    # Stage 0: Raw V
    raw_table = build_bigram_table(all_bigrams)
    v_raw, p_raw = compute_v(raw_table)
    print(f"\n  Stage 0 (raw): V={v_raw:.4f}, p={p_raw:.2e}, n={len(all_bigrams)}")

    # Stage 1: Role-conditioned expected table
    # For each role pair, compute expected suffix bigram from marginals
    role_pairs = Counter((b['role1'], b['role2']) for b in all_bigrams)
    role_bigrams = defaultdict(list)
    for b in all_bigrams:
        role_bigrams[(b['role1'], b['role2'])].append(b)

    expected_role = np.zeros((n_suf, n_suf), dtype=float)
    for (r1, r2), rp_bigrams in role_bigrams.items():
        n_rp = len(rp_bigrams)
        if n_rp < 2:
            continue
        # Suffix marginals within this role pair
        suf1_counts = Counter(b['suf1'] for b in rp_bigrams)
        suf2_counts = Counter(b['suf2'] for b in rp_bigrams)
        for s1, c1 in suf1_counts.items():
            for s2, c2 in suf2_counts.items():
                expected_role[suf_idx[s1], suf_idx[s2]] += (c1 * c2) / n_rp

    # Residual after role conditioning
    residual_role = raw_table - expected_role
    # Compute chi2 for residual (using Pearson formula directly)
    mask = expected_role > 0
    chi2_role_resid = float(np.sum((residual_role[mask]) ** 2 / expected_role[mask]))
    n_total = raw_table.sum()
    v_role_resid = float(np.sqrt(chi2_role_resid / (n_total * (min(n_suf, n_suf) - 1))))
    print(f"  Stage 1 (role-conditioned residual): V={v_role_resid:.4f}")

    # Stage 2: Exclude exact token repetitions
    no_repeat_bigrams = [b for b in all_bigrams if not b['same_token']]
    n_repeats = len(all_bigrams) - len(no_repeat_bigrams)
    table_no_repeat = build_bigram_table(no_repeat_bigrams)
    v_no_repeat, p_no_repeat = compute_v(table_no_repeat)
    print(f"  Stage 2 (no token repeats): V={v_no_repeat:.4f}, p={p_no_repeat:.2e}, "
          f"removed={n_repeats} ({100*n_repeats/len(all_bigrams):.1f}%)")

    # Stage 3: Combined (role-conditioned + no token repeats)
    role_bigrams_nr = defaultdict(list)
    for b in no_repeat_bigrams:
        role_bigrams_nr[(b['role1'], b['role2'])].append(b)

    table_nr = build_bigram_table(no_repeat_bigrams)
    expected_combined = np.zeros((n_suf, n_suf), dtype=float)
    for (r1, r2), rp_bigrams in role_bigrams_nr.items():
        n_rp = len(rp_bigrams)
        if n_rp < 2:
            continue
        suf1_counts = Counter(b['suf1'] for b in rp_bigrams)
        suf2_counts = Counter(b['suf2'] for b in rp_bigrams)
        for s1, c1 in suf1_counts.items():
            for s2, c2 in suf2_counts.items():
                expected_combined[suf_idx[s1], suf_idx[s2]] += (c1 * c2) / n_rp

    mask_c = expected_combined > 0
    chi2_combined = float(np.sum((table_nr[mask_c] - expected_combined[mask_c]) ** 2 / expected_combined[mask_c]))
    v_combined = float(np.sqrt(chi2_combined / (table_nr.sum() * (min(n_suf, n_suf) - 1))))
    print(f"  Stage 3 (combined residual): V={v_combined:.4f}")

    # Top residual suffix pairs
    residual_combined = table_nr - expected_combined
    z_scores = np.zeros_like(residual_combined)
    z_scores[mask_c] = residual_combined[mask_c] / np.sqrt(expected_combined[mask_c])

    top_pairs = []
    for i in range(n_suf):
        for j in range(n_suf):
            if abs(z_scores[i, j]) > 3.0 and expected_combined[i, j] > 1:
                top_pairs.append({
                    'suf1': all_suffixes[i],
                    'suf2': all_suffixes[j],
                    'observed': int(table_nr[i, j]),
                    'expected': round(float(expected_combined[i, j]), 1),
                    'z': round(float(z_scores[i, j]), 2),
                })
    top_pairs.sort(key=lambda x: -abs(x['z']))
    print(f"\n  Top residual suffix pairs (|z| > 3.0): {len(top_pairs)}")
    for p in top_pairs[:10]:
        print(f"    {p['suf1']:6s} -> {p['suf2']:6s}  obs={p['observed']:4d} exp={p['expected']:6.1f} z={p['z']:+.2f}")

    # Section sub-analysis
    section_results = {}
    for section in ['S', 'H', 'T', 'B', 'C']:
        sec_bigrams = [b for b in no_repeat_bigrams if b['section'] == section]
        if len(sec_bigrams) < 100:
            section_results[section] = {'n': len(sec_bigrams), 'v': None}
            continue
        sec_table = build_bigram_table(sec_bigrams)
        sec_v, sec_p = compute_v(sec_table)
        section_results[section] = {
            'n': len(sec_bigrams),
            'v': round(sec_v, 4),
            'p': float(sec_p),
        }
    print(f"\n  Section sub-analysis (no-repeat raw V):")
    for sec, r in sorted(section_results.items()):
        if r['v'] is not None:
            print(f"    {sec}: V={r['v']:.4f}, n={r['n']}")

    # Verdict
    if v_combined >= 0.02:
        verdict = "PASS"
    else:
        verdict = "FAIL"
    print(f"\n  >>> VERDICT: {verdict} (residual V={v_combined:.4f}, threshold=0.02)")

    result = {
        'test': 'T1_suffix_signal_decomposition',
        'verdict': verdict,
        'stage0_raw': {'V': round(v_raw, 4), 'p': float(p_raw), 'n': len(all_bigrams)},
        'stage1_role_conditioned': {'V_residual': round(v_role_resid, 4)},
        'stage2_no_token_repeat': {'V': round(v_no_repeat, 4), 'p': float(p_no_repeat),
                                    'n_removed': n_repeats,
                                    'pct_removed': round(100 * n_repeats / len(all_bigrams), 2)},
        'stage3_combined': {'V_residual': round(v_combined, 4)},
        'decomposition': {
            'raw_V': round(v_raw, 4),
            'role_contribution': round(v_raw - v_role_resid, 4),
            'repeat_contribution': round(v_raw - v_no_repeat, 4),
            'residual': round(v_combined, 4),
        },
        'top_residual_pairs': top_pairs[:20],
        'section_sub_analysis': section_results,
        'constraints_referenced': ['C1002', 'C1004', 'C611', 'C957', 'C1029'],
    }

    return result


# ============================================================
# T2: SUFFIX-ROLE PREFIX MEDIATION TEST
# ============================================================

def run_t2(tokens, token_to_class):
    """Test whether role-suffix association is fully PREFIX-mediated."""
    print("\n" + "=" * 60)
    print("T2: Suffix-Role PREFIX Mediation Test")
    print("=" * 60)

    # Only classified tokens
    classified = [t for t in tokens if t['cls'] is not None]
    print(f"  Classified tokens: {len(classified)}")

    # Build role × suffix contingency table (raw)
    roles = sorted(ROLE_TAXONOMY.keys())
    suffixes_raw = sorted(set(t['suffix'] if t['suffix'] else 'NONE' for t in classified))
    role_idx = {r: i for i, r in enumerate(roles)}
    suf_idx = {s: i for i, s in enumerate(suffixes_raw)}

    raw_table = np.zeros((len(roles), len(suffixes_raw)), dtype=float)
    for t in classified:
        suf = t['suffix'] if t['suffix'] else 'NONE'
        if suf in suf_idx and t['role'] in role_idx:
            raw_table[role_idx[t['role']], suf_idx[suf]] += 1

    # Remove zero rows/cols
    row_mask = raw_table.sum(axis=1) > 0
    col_mask = raw_table.sum(axis=0) > 0
    raw_reduced = raw_table[np.ix_(row_mask, col_mask)]

    if raw_reduced.shape[0] < 2 or raw_reduced.shape[1] < 2:
        print("  ERROR: Insufficient table dimensions")
        return {'test': 'T2_prefix_mediation', 'verdict': 'ERROR'}

    chi2_raw, p_raw, _, _ = chi2_contingency(raw_reduced)
    n = raw_reduced.sum()
    v_raw = float(np.sqrt(chi2_raw / (n * (min(raw_reduced.shape) - 1))))
    print(f"  Raw role×suffix: V={v_raw:.4f}, chi²={chi2_raw:.1f}, p={p_raw:.2e}")

    # PREFIX-conditioned test
    # Group tokens by PREFIX, compute per-PREFIX role×suffix V
    prefix_groups = defaultdict(list)
    for t in classified:
        pkey = t['prefix'] if t['prefix'] else '_BARE_'
        prefix_groups[pkey].append(t)

    prefix_v_results = {}
    weighted_v_sum = 0.0
    total_weight = 0

    for prefix, ptoks in sorted(prefix_groups.items()):
        if len(ptoks) < 30:
            continue
        p_table = np.zeros((len(roles), len(suffixes_raw)), dtype=float)
        for t in ptoks:
            suf = t['suffix'] if t['suffix'] else 'NONE'
            if suf in suf_idx and t['role'] in role_idx:
                p_table[role_idx[t['role']], suf_idx[suf]] += 1

        rm = p_table.sum(axis=1) > 0
        cm = p_table.sum(axis=0) > 0
        p_reduced = p_table[np.ix_(rm, cm)]

        if p_reduced.shape[0] < 2 or p_reduced.shape[1] < 2:
            prefix_v_results[prefix] = {'n': len(ptoks), 'V': 0.0, 'skip': True}
            continue

        try:
            chi2_p, _, _, _ = chi2_contingency(p_reduced)
            np_ = p_reduced.sum()
            v_p = float(np.sqrt(chi2_p / (np_ * (min(p_reduced.shape) - 1))))
        except ValueError:
            v_p = 0.0

        prefix_v_results[prefix] = {'n': len(ptoks), 'V': round(v_p, 4)}
        weighted_v_sum += v_p * len(ptoks)
        total_weight += len(ptoks)

    v_conditioned = weighted_v_sum / total_weight if total_weight > 0 else 0.0
    mediation_fraction = (v_raw - v_conditioned) / v_raw if v_raw > 0 else 0.0

    print(f"  PREFIX-conditioned weighted V: {v_conditioned:.4f}")
    print(f"  Mediation fraction: {mediation_fraction:.1%}")
    print(f"    V_raw={v_raw:.4f} → V_conditioned={v_conditioned:.4f}")

    print(f"\n  Per-PREFIX V (n>=30):")
    for prefix, r in sorted(prefix_v_results.items(), key=lambda x: -x[1].get('V', 0)):
        if not r.get('skip'):
            print(f"    {prefix:8s}: V={r['V']:.4f}, n={r['n']}")

    # Verdict
    if mediation_fraction > 0.80:
        verdict = "FULL_MEDIATION"
    elif mediation_fraction > 0.50:
        verdict = "PARTIAL_MEDIATION"
    else:
        verdict = "INDEPENDENT"
    print(f"\n  >>> VERDICT: {verdict} (mediation={mediation_fraction:.1%})")

    result = {
        'test': 'T2_prefix_mediation',
        'verdict': verdict,
        'v_raw': round(v_raw, 4),
        'chi2_raw': round(float(chi2_raw), 1),
        'p_raw': float(p_raw),
        'v_conditioned': round(v_conditioned, 4),
        'mediation_fraction': round(mediation_fraction, 4),
        'per_prefix': prefix_v_results,
        'n_classified': len(classified),
        'constraints_referenced': ['C588', 'C556', 'C378'],
    }

    return result


# ============================================================
# T3: COMPOUND ATOM POSITION GRAMMAR
# ============================================================

def run_t3():
    """Test whether atoms within compound MIDDLEs have positional preferences."""
    print("\n" + "=" * 60)
    print("T3: Compound Atom Position Grammar")
    print("=" * 60)

    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    core_middles = mid_analyzer.get_core_middles()
    print(f"  Core MIDDLEs: {len(core_middles)}")

    # Collect atom positions within compounds
    atom_positions = defaultdict(list)  # atom -> list of (normalized_pos, category)
    compound_count = 0
    compounds_with_3plus = 0

    all_middles = set()
    tx = Transcript()
    morph = Morphology()
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle:
            all_middles.add(m.middle)

    for middle in sorted(all_middles):
        if not mid_analyzer.is_compound(middle):
            continue
        atoms = mid_analyzer.get_maximal_atoms(middle)
        if not atoms or len(atoms) < 2:
            continue

        compound_count += 1
        mid_len = len(middle)
        if len(atoms) >= 3:
            compounds_with_3plus += 1

        for atom in atoms:
            # Find atom position in compound string
            idx = middle.find(atom)
            if idx < 0:
                continue
            # Normalized position [0, 1]
            norm_pos = idx / max(mid_len - 1, 1)
            # Categorical position
            is_initial = (idx == 0)
            is_final = (idx + len(atom) == mid_len)
            if is_initial:
                cat = 'INITIAL'
            elif is_final:
                cat = 'FINAL'
            else:
                cat = 'MEDIAL'

            atom_positions[atom].append({
                'norm_pos': norm_pos,
                'category': cat,
                'compound': middle,
                'compound_len': mid_len,
            })

    print(f"  Compound MIDDLEs analyzed: {compound_count}")
    print(f"  Compounds with 3+ atoms: {compounds_with_3plus}")
    print(f"  Atoms with position data: {len(atom_positions)}")

    # Filter to atoms with 10+ occurrences
    testable_atoms = {a: ps for a, ps in atom_positions.items() if len(ps) >= 10}
    print(f"  Testable atoms (10+ compounds): {len(testable_atoms)}")

    # Build atom × category contingency table
    categories = ['INITIAL', 'MEDIAL', 'FINAL']
    cat_idx = {c: i for i, c in enumerate(categories)}
    atom_list = sorted(testable_atoms.keys())

    if len(atom_list) < 2:
        print("  ERROR: Too few testable atoms")
        return {'test': 'T3_atom_position', 'verdict': 'ERROR'}

    table = np.zeros((len(atom_list), len(categories)), dtype=float)
    for i, atom in enumerate(atom_list):
        for p in testable_atoms[atom]:
            table[i, cat_idx[p['category']]] += 1

    # Remove zero cols
    col_mask = table.sum(axis=0) > 0
    table_reduced = table[:, col_mask]
    cats_reduced = [c for c, m in zip(categories, col_mask) if m]

    if table_reduced.shape[1] < 2:
        print("  ERROR: Too few position categories")
        return {'test': 'T3_atom_position', 'verdict': 'ERROR'}

    chi2, p_chi2, _, _ = chi2_contingency(table_reduced)
    n = table_reduced.sum()
    v = float(np.sqrt(chi2 / (n * (min(table_reduced.shape) - 1))))
    print(f"\n  Overall atom×position: V={v:.4f}, chi²={chi2:.1f}, p={p_chi2:.2e}")

    # Per-atom analysis
    atom_details = []
    for i, atom in enumerate(atom_list):
        counts = {c: int(table[i, cat_idx[c]]) for c in categories}
        total = sum(counts.values())
        mean_pos = float(np.mean([p['norm_pos'] for p in testable_atoms[atom]]))

        # Kernel content
        has_k = 'k' in atom
        has_e = 'e' in atom and atom != 'ee'
        has_h = 'h' in atom

        atom_details.append({
            'atom': atom,
            'n': total,
            'counts': counts,
            'mean_pos': round(mean_pos, 4),
            'has_k': has_k,
            'has_e': has_e,
            'has_h': has_h,
        })

    atom_details.sort(key=lambda x: x['mean_pos'])
    print(f"\n  {'Atom':8s} {'N':4s} {'Mean':6s} {'INIT':5s} {'MED':5s} {'FIN':5s} {'Kernel'}")
    print(f"  {'-'*8} {'-'*4} {'-'*6} {'-'*5} {'-'*5} {'-'*5} {'-'*6}")
    for a in atom_details:
        kernel = ('k' if a['has_k'] else '') + ('e' if a['has_e'] else '') + ('h' if a['has_h'] else '')
        print(f"  {a['atom']:8s} {a['n']:4d} {a['mean_pos']:.4f} "
              f"{a['counts']['INITIAL']:5d} {a['counts']['MEDIAL']:5d} {a['counts']['FINAL']:5d} "
              f"{kernel if kernel else '-'}")

    # Kernel prediction test: k-atoms earlier than e-atoms
    k_positions = [p['norm_pos'] for a, ps in testable_atoms.items()
                   for p in ps if 'k' in a]
    e_positions = [p['norm_pos'] for a, ps in testable_atoms.items()
                   for p in ps if 'e' in a and a != 'ee']

    kernel_test = None
    if len(k_positions) >= 5 and len(e_positions) >= 5:
        u_stat, u_pval = mannwhitneyu(k_positions, e_positions, alternative='less')
        kernel_test = {
            'k_mean_pos': round(float(np.mean(k_positions)), 4),
            'e_mean_pos': round(float(np.mean(e_positions)), 4),
            'n_k': len(k_positions),
            'n_e': len(e_positions),
            'MW_U': float(u_stat),
            'MW_p': round(float(u_pval), 6),
            'prediction': 'k-atoms earlier than e-atoms (extending C521)',
        }
        print(f"\n  Kernel prediction: k mean={kernel_test['k_mean_pos']:.4f} vs "
              f"e mean={kernel_test['e_mean_pos']:.4f}, MW p={kernel_test['MW_p']:.4f}")

    # Count significant atoms (Bonferroni)
    bonf_threshold = 0.05 / len(atom_list)
    n_significant = 0
    for i, atom in enumerate(atom_list):
        row = table[i, :]
        total = row.sum()
        if total < 10:
            continue
        # Test against uniform (use all 3 categories — don't filter zeros)
        expected = np.full(len(categories), total / len(categories))
        from scipy.stats import chisquare
        _, p_atom = chisquare(row, expected)
        if p_atom < bonf_threshold:
            n_significant += 1

    print(f"\n  Significant atoms (Bonferroni p < {bonf_threshold:.6f}): {n_significant}/{len(atom_list)}")

    # Verdict
    if v >= 0.10 and n_significant >= 3:
        verdict = "PASS"
    elif p_chi2 < 0.01:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"\n  >>> VERDICT: {verdict} (V={v:.4f}, n_sig={n_significant})")

    result = {
        'test': 'T3_atom_position_grammar',
        'verdict': verdict,
        'n_compounds': compound_count,
        'n_compounds_3plus': compounds_with_3plus,
        'n_testable_atoms': len(testable_atoms),
        'chi2': round(float(chi2), 1),
        'p': float(p_chi2),
        'V': round(v, 4),
        'n_significant_atoms': n_significant,
        'bonferroni_threshold': round(bonf_threshold, 6),
        'kernel_prediction': kernel_test,
        'atom_details': atom_details,
        'constraints_referenced': ['C521', 'C522', 'C935'],
    }

    return result


# ============================================================
# T4: COMPOUND ATOM CO-OCCURRENCE RULES
# ============================================================

def run_t4():
    """Test atom co-occurrence within compounds and C475 compliance."""
    print("\n" + "=" * 60)
    print("T4: Compound Atom Co-Occurrence Rules")
    print("=" * 60)

    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Load C475 compatibility graph
    c475_path = ROOT / 'phases' / 'MIDDLE_INCOMPATIBILITY' / 'results' / 'middle_incompatibility.json'
    with open(c475_path, 'r', encoding='utf-8') as f:
        c475_data = json.load(f)

    # Build MIDDLE→component_id mapping
    middle_component = {}
    for comp_id, component in enumerate(c475_data['graph_analysis']['components']):
        for mid in component:
            middle_component[mid] = comp_id

    def are_c475_compatible(mid1, mid2):
        """Check if two MIDDLEs are in the same C475 connected component."""
        c1 = middle_component.get(mid1)
        c2 = middle_component.get(mid2)
        if c1 is None or c2 is None:
            return None  # Unknown
        return c1 == c2

    # Collect atom sets per compound
    compound_atoms = {}
    all_middles = set()
    tx = Transcript()
    morph = Morphology()
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle:
            all_middles.add(m.middle)

    for middle in sorted(all_middles):
        if not mid_analyzer.is_compound(middle):
            continue
        atoms = mid_analyzer.get_maximal_atoms(middle)
        if atoms and len(atoms) >= 2:
            compound_atoms[middle] = set(atoms)

    print(f"  Compounds with 2+ atoms: {len(compound_atoms)}")

    # All atoms that appear in compounds
    all_atoms = set()
    for atoms in compound_atoms.values():
        all_atoms.update(atoms)
    all_atoms = sorted(all_atoms)
    atom_idx = {a: i for i, a in enumerate(all_atoms)}
    n_atoms = len(all_atoms)
    print(f"  Unique atoms in compounds: {n_atoms}")

    # Atom frequency (how many compounds contain each atom)
    atom_freq = Counter()
    for atoms in compound_atoms.values():
        for a in atoms:
            atom_freq[a] += 1

    n_compounds = len(compound_atoms)

    # Co-occurrence matrix
    cooccur = np.zeros((n_atoms, n_atoms), dtype=float)
    for atoms in compound_atoms.values():
        atom_list = sorted(atoms)
        for i in range(len(atom_list)):
            for j in range(i + 1, len(atom_list)):
                a1, a2 = atom_list[i], atom_list[j]
                cooccur[atom_idx[a1], atom_idx[a2]] += 1
                cooccur[atom_idx[a2], atom_idx[a1]] += 1

    # Expected under independence
    expected = np.zeros((n_atoms, n_atoms), dtype=float)
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            e = (atom_freq[all_atoms[i]] * atom_freq[all_atoms[j]]) / n_compounds
            expected[i, j] = e
            expected[j, i] = e

    # Standardized residuals
    z_scores = np.zeros((n_atoms, n_atoms), dtype=float)
    mask = expected > 0
    z_scores[mask] = (cooccur[mask] - expected[mask]) / np.sqrt(expected[mask])

    # Find enriched and depleted pairs
    enriched = []
    depleted = []
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            if expected[i, j] < 1:
                continue
            z = z_scores[i, j]
            pair_info = {
                'atom1': all_atoms[i],
                'atom2': all_atoms[j],
                'observed': int(cooccur[i, j]),
                'expected': round(float(expected[i, j]), 1),
                'z': round(float(z), 2),
            }
            if z > 3.0:
                enriched.append(pair_info)
            elif z < -3.0:
                depleted.append(pair_info)

    enriched.sort(key=lambda x: -x['z'])
    depleted.sort(key=lambda x: x['z'])
    print(f"\n  Enriched pairs (z > 3.0): {len(enriched)}")
    for p in enriched[:10]:
        print(f"    {p['atom1']:6s} + {p['atom2']:6s}  obs={p['observed']:3d} exp={p['expected']:5.1f} z={p['z']:+.2f}")
    print(f"  Depleted pairs (z < -3.0): {len(depleted)}")
    for p in depleted[:10]:
        print(f"    {p['atom1']:6s} + {p['atom2']:6s}  obs={p['observed']:3d} exp={p['expected']:5.1f} z={p['z']:+.2f}")

    # C475 compliance test
    c475_compatible_count = 0
    c475_incompatible_count = 0
    c475_unknown_count = 0

    for atoms in compound_atoms.values():
        atom_list = sorted(atoms)
        for i in range(len(atom_list)):
            for j in range(i + 1, len(atom_list)):
                compat = are_c475_compatible(atom_list[i], atom_list[j])
                if compat is True:
                    c475_compatible_count += 1
                elif compat is False:
                    c475_incompatible_count += 1
                else:
                    c475_unknown_count += 1

    total_c475_testable = c475_compatible_count + c475_incompatible_count
    compliance_rate = c475_compatible_count / max(total_c475_testable, 1)

    # Random baseline: what fraction of all atom pairs are C475-compatible?
    random_compatible = 0
    random_total = 0
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            compat = are_c475_compatible(all_atoms[i], all_atoms[j])
            if compat is not None:
                random_total += 1
                if compat:
                    random_compatible += 1
    random_rate = random_compatible / max(random_total, 1)
    enrichment = compliance_rate / max(random_rate, 0.001)

    print(f"\n  C475 compliance:")
    print(f"    Within-compound: {c475_compatible_count}/{total_c475_testable} = {compliance_rate:.1%}")
    print(f"    Random baseline: {random_compatible}/{random_total} = {random_rate:.1%}")
    print(f"    Enrichment: {enrichment:.2f}x")
    print(f"    Unknown (not in C475): {c475_unknown_count}")

    # Fisher exact for C475
    a = c475_compatible_count
    b = c475_incompatible_count
    c = random_compatible - c475_compatible_count
    d = (random_total - random_compatible) - c475_incompatible_count
    if a >= 0 and b >= 0 and c >= 0 and d >= 0:
        fisher_or, fisher_p = fisher_exact([[max(a, 0), max(b, 0)],
                                             [max(c, 0), max(d, 0)]],
                                            alternative='greater')
    else:
        fisher_or, fisher_p = float('nan'), 1.0

    # Overall chi2 on co-occurrence matrix (upper triangle only)
    obs_upper = []
    exp_upper = []
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            if expected[i, j] > 0:
                obs_upper.append(cooccur[i, j])
                exp_upper.append(expected[i, j])
    obs_upper = np.array(obs_upper)
    exp_upper = np.array(exp_upper)
    chi2_overall = float(np.sum((obs_upper - exp_upper) ** 2 / exp_upper))
    df_overall = len(obs_upper) - 1
    from scipy.stats import chi2 as chi2_dist
    p_overall = 1 - chi2_dist.cdf(chi2_overall, df_overall) if df_overall > 0 else 1.0

    print(f"\n  Overall co-occurrence: chi²={chi2_overall:.1f}, df={df_overall}, p={p_overall:.2e}")

    # Verdict
    pass_chi2 = p_overall < 0.001
    pass_pairs = len(depleted) >= 3
    pass_c475 = enrichment > 3.0
    if pass_chi2 and (pass_pairs or pass_c475):
        verdict = "PASS"
    elif pass_chi2 or pass_c475:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"\n  >>> VERDICT: {verdict}")

    result = {
        'test': 'T4_atom_cooccurrence',
        'verdict': verdict,
        'n_compounds': n_compounds,
        'n_atoms': n_atoms,
        'chi2_overall': round(chi2_overall, 1),
        'p_overall': float(p_overall),
        'n_enriched': len(enriched),
        'n_depleted': len(depleted),
        'enriched_pairs': enriched[:20],
        'depleted_pairs': depleted[:20],
        'c475_compliance': {
            'compatible': c475_compatible_count,
            'incompatible': c475_incompatible_count,
            'unknown': c475_unknown_count,
            'rate': round(compliance_rate, 4),
            'random_rate': round(random_rate, 4),
            'enrichment': round(enrichment, 2),
            'fisher_OR': round(float(fisher_or), 4) if not np.isnan(fisher_or) else None,
            'fisher_p': round(float(fisher_p), 6) if not np.isnan(fisher_p) else None,
        },
        'constraints_referenced': ['C475', 'C1053'],
    }

    return result


# ============================================================
# T5: COMPOUND DEPTH-SPECIFICITY GRADIENT
# ============================================================

def run_t5(tokens):
    """Test whether deeper compounds are more folio-specific."""
    print("\n" + "=" * 60)
    print("T5: Compound Depth-Specificity Gradient")
    print("=" * 60)

    mid_analyzer = MiddleAnalyzer()
    mid_analyzer.build_inventory('B')

    # Build MIDDLE → depth and folio spread
    middle_folios = defaultdict(set)
    middle_roles = defaultdict(Counter)

    for t in tokens:
        if t['middle']:
            middle_folios[t['middle']].add(t['folio'])
            middle_roles[t['middle']][t['role']] += 1

    middle_data = []
    for middle in sorted(middle_folios.keys()):
        is_comp = mid_analyzer.is_compound(middle)
        if is_comp:
            atoms = mid_analyzer.get_maximal_atoms(middle)
            depth = len(atoms) if atoms else 0
        else:
            depth = 0

        folio_count = len(middle_folios[middle])
        dominant_role = middle_roles[middle].most_common(1)[0][0] if middle_roles[middle] else 'UN'
        is_classified = any(t['cls'] is not None for t in tokens if t.get('middle') == middle)

        middle_data.append({
            'middle': middle,
            'depth': depth,
            'folio_count': folio_count,
            'is_compound': is_comp,
            'dominant_role': dominant_role,
            'total_tokens': sum(middle_roles[middle].values()),
        })

    # Faster: rebuild classification info from token_to_class
    morph = Morphology()
    classified_middles = set()
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    for word in ctm['token_to_class']:
        m = morph.extract(word)
        if m.middle:
            classified_middles.add(m.middle)

    for d in middle_data:
        d['is_classified'] = d['middle'] in classified_middles

    print(f"  Total MIDDLE types: {len(middle_data)}")
    print(f"  Compound: {sum(1 for d in middle_data if d['is_compound'])}")
    print(f"  Classified: {sum(1 for d in middle_data if d['is_classified'])}")

    # Primary test: Spearman(depth, folio_count)
    depths = np.array([d['depth'] for d in middle_data])
    folio_counts = np.array([d['folio_count'] for d in middle_data])

    rho, p_rho = spearmanr(depths, folio_counts)
    print(f"\n  Primary: Spearman(depth, folio_count) = {rho:.4f}, p={p_rho:.2e}")

    # Depth distribution
    depth_dist = Counter(d['depth'] for d in middle_data)
    print(f"\n  Depth distribution:")
    for depth in sorted(depth_dist.keys()):
        mean_folio = np.mean([d['folio_count'] for d in middle_data if d['depth'] == depth])
        print(f"    Depth {depth}: {depth_dist[depth]:5d} MIDDLEs, mean folio count={mean_folio:.1f}")

    # Classified vs UN depth
    classified_depths = [d['depth'] for d in middle_data if d['is_classified']]
    un_depths = [d['depth'] for d in middle_data if not d['is_classified']]

    if len(classified_depths) >= 5 and len(un_depths) >= 5:
        mw_stat, mw_p = mannwhitneyu(un_depths, classified_depths, alternative='greater')
        print(f"\n  Classified vs UN depth:")
        print(f"    Classified: mean={np.mean(classified_depths):.2f}, median={np.median(classified_depths):.1f}")
        print(f"    UN: mean={np.mean(un_depths):.2f}, median={np.median(un_depths):.1f}")
        print(f"    MW (UN > classified): U={mw_stat:.0f}, p={mw_p:.2e}")
    else:
        mw_stat, mw_p = None, None

    # Within-role depth variation
    role_depth_data = defaultdict(list)
    for d in middle_data:
        if d['is_classified'] and d['is_compound']:
            role_depth_data[d['dominant_role']].append(d['depth'])

    print(f"\n  Within-role depth (compound MIDDLEs only):")
    for role in sorted(ROLE_TAXONOMY.keys()):
        ds = role_depth_data.get(role, [])
        if ds:
            print(f"    {role}: n={len(ds)}, mean={np.mean(ds):.2f}, std={np.std(ds):.2f}")

    # KW test on role depths (if enough roles have data)
    kw_groups = [v for v in role_depth_data.values() if len(v) >= 5]
    if len(kw_groups) >= 2:
        h_stat, h_p = kruskal(*kw_groups)
        print(f"  KW test (depth ~ role): H={h_stat:.1f}, p={h_p:.4f}")
    else:
        h_stat, h_p = None, None

    # Verdict
    if abs(rho) > 0.30 and p_rho < 0.001:
        verdict = "PASS"
    elif abs(rho) > 0.15 and p_rho < 0.01:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    print(f"\n  >>> VERDICT: {verdict} (rho={rho:.4f})")

    result = {
        'test': 'T5_compound_depth_specificity',
        'verdict': verdict,
        'n_middles': len(middle_data),
        'depth_distribution': dict(depth_dist),
        'primary_test': {
            'rho': round(float(rho), 4),
            'p': float(p_rho),
        },
        'classified_vs_un': {
            'classified_mean_depth': round(float(np.mean(classified_depths)), 4) if classified_depths else None,
            'un_mean_depth': round(float(np.mean(un_depths)), 4) if un_depths else None,
            'MW_U': float(mw_stat) if mw_stat is not None else None,
            'MW_p': float(mw_p) if mw_p is not None else None,
        },
        'kruskal_wallis': {
            'H': round(float(h_stat), 1) if h_stat is not None else None,
            'p': round(float(h_p), 4) if h_p is not None else None,
        },
        'role_depth': {role: {'n': len(ds), 'mean': round(float(np.mean(ds)), 2)}
                       for role, ds in role_depth_data.items() if ds},
        'constraints_referenced': ['C766', 'C767', 'C768', 'C769'],
    }

    return result


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 379: Morphological Deep Structure")
    print("5-test battery | Tier 2 targets")
    print("=" * 60)

    print("\nLoading data...")
    tokens, token_to_class, morph = load_data()
    print(f"  Currier B tokens: {len(tokens)}")

    # Run tests
    t1 = run_t1(tokens)
    t2 = run_t2(tokens, token_to_class)
    t3 = run_t3()
    t4 = run_t4()
    t5 = run_t5(tokens)

    # Save individual results
    for name, result in [('t1_suffix_signal_decomposition', t1),
                         ('t2_role_suffix_signatures', t2),
                         ('t3_atom_position_grammar', t3),
                         ('t4_atom_cooccurrence_rules', t4),
                         ('t5_compound_depth_role', t5)]:
        path = RESULTS / f'{name}.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nSaved: {path}")

    # Summary
    tests = [t1, t2, t3, t4, t5]
    verdicts = [t['verdict'] for t in tests]

    summary = {
        'phase': 379,
        'name': 'MORPHOLOGICAL_DEEP_STRUCTURE',
        'description': '5-test battery: suffix microstructure + compound composition rules',
        'tier': 2,
        'tests': [
            {'id': 'T1', 'name': 'Suffix Signal Decomposition', 'verdict': t1['verdict']},
            {'id': 'T2', 'name': 'Suffix-Role PREFIX Mediation', 'verdict': t2['verdict']},
            {'id': 'T3', 'name': 'Atom Position Grammar', 'verdict': t3['verdict']},
            {'id': 'T4', 'name': 'Atom Co-Occurrence Rules', 'verdict': t4['verdict']},
            {'id': 'T5', 'name': 'Compound Depth-Specificity', 'verdict': t5['verdict']},
        ],
        'constraints_referenced': sorted(set(
            sum((t.get('constraints_referenced', []) for t in tests), [])
        )),
    }

    with open(RESULTS / 'morphological_deep_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {RESULTS / 'morphological_deep_summary.json'}")

    print(f"\n{'=' * 60}")
    print(f"RESULTS:")
    for t in summary['tests']:
        print(f"  {t['id']}: {t['name']} -> {t['verdict']}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
