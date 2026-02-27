#!/usr/bin/env python3
"""
Phase 474: LINE_MICRO_GRAMMAR
=================================
Tests line-internal execution structure at 49-class resolution.

5-test battery:
  T1: CLASS_POSITIONAL_SPECIALIZATION (49 classes x 5 quintiles)
  T2: TRANSITION_GRADIENT_RESOLUTION (quintile-conditioned 49x49 matrices)
  T3: FORBIDDEN_TRANSITION_LOCALIZATION (where in lines do violations occur?)
  T4: POSITIONAL_MOTIF_DETECTION (position-locked class bigrams)
  T5: POSITION_CONDITIONED_GENERATIVE_IMPROVEMENT (M2p vs M2)

Extends: C1156 (3-zone), C556 (role-level), C964 (boundary-constrained)
Depends on: C121 (49 classes), C1025 (M2 generative), C681 (line independence)
"""

import json, sys, math, time, random, functools
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology

sys.path.insert(0, str(ROOT / 'phases' / 'TEXT_BLOCK_PARALLEL_OPERATORS' / 'scripts'))
from text_block_parallel_operators import jsd, normalize_profile, mann_whitney_u, normal_cdf, chi2_sf

sys.path.insert(0, str(ROOT / 'phases' / 'SUFFIX_MODE_ASSIGNMENT' / 'scripts'))
from suffix_mode_assignment import entropy_from_counts, chi2_independence

sys.path.insert(0, str(ROOT / 'phases' / 'BLOCK_GALLOWS_ORDERING' / 'scripts'))
from block_gallows_ordering import spearman_rho

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = ROOT / "phases" / "LINE_MICRO_GRAMMAR" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_CLASSES = 49
N_QUINTILES = 5
N_PERM = 1000
N_SYNTH = 1000
SEED = 42

# 6-state macro partition
MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
STATE_ORDER = ['AXM', 'AXm', 'FQ', 'CC', 'FL_HAZ', 'FL_SAFE']
CLASS_TO_STATE = {}
for _state, _classes in MACRO_STATE_PARTITION.items():
    for _c in _classes:
        CLASS_TO_STATE[_c] = _state

# 17 forbidden MIDDLE pairs
FORBIDDEN_MIDDLE_PAIRS = {
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o'),
}


def round_floats(obj, digits=6):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


def kl_divergence(p, q, epsilon=1e-10):
    """KL(p || q) where p and q are dicts or lists of probabilities."""
    if isinstance(p, dict):
        keys = set(p.keys()) | set(q.keys())
        total = 0.0
        for k in keys:
            pk = p.get(k, 0.0)
            qk = q.get(k, 0.0)
            if pk > epsilon:
                total += pk * math.log2(pk / max(qk, epsilon))
        return total
    else:
        total = 0.0
        for pk, qk in zip(p, q):
            if pk > epsilon:
                total += pk * math.log2(pk / max(qk, epsilon))
        return total


def assign_quintile(idx, line_len):
    """Assign quintile Q0-Q4 for token at position idx in line of length line_len."""
    return min(N_QUINTILES - 1, int(idx / line_len * N_QUINTILES))


# ── Data Loading ──────────────────────────────────────────────────

def load_data():
    """Load B tokens grouped by line with 49-class assignments."""
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    morph = Morphology()

    folio_lines = defaultdict(lambda: defaultdict(list))
    skipped = 0
    total = 0

    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue
        total += 1
        cls = token_to_class.get(w)
        m = morph.extract(w)
        folio_lines[t.folio][t.line].append({
            'word': w,
            'cls': cls,  # None if unclassified
            'middle': m.middle if m else '',
            'section': t.section,
            'folio': t.folio,
        })
        if cls is None:
            skipped += 1

    # Build ordered line list (ALL tokens, including unclassified for T3)
    all_lines = []  # (folio, section, tokens_list)
    for folio in sorted(folio_lines.keys()):
        for line_key in sorted(folio_lines[folio].keys()):
            tokens = folio_lines[folio][line_key]
            if len(tokens) >= 2:
                section = tokens[0]['section']
                all_lines.append((folio, section, tokens))

    classified = total - skipped
    print(f"  Total B tokens: {total}, classified: {classified}, skipped: {skipped}")
    print(f"  Lines (>=2 tokens): {len(all_lines)}")

    return all_lines, token_to_class, morph


# ── T1: Class Positional Specialization ───────────────────────────

def test_class_positional_specialization(all_lines):
    """For each of 49 classes, compute distribution over 5 quintiles."""
    print("\n=== T1: CLASS POSITIONAL SPECIALIZATION ===")

    # Count class occurrences per quintile (only lines with >=5 classified tokens)
    class_quintile = defaultdict(lambda: Counter())  # class_id -> Counter(quintile)
    total_per_quintile = Counter()
    n_lines_used = 0
    n_tokens_used = 0

    for folio, section, tokens in all_lines:
        # Get classified tokens with their original positions
        classified = [(i, t) for i, t in enumerate(tokens) if t['cls'] is not None]
        if len(classified) < 5:
            continue
        n_lines_used += 1
        line_len = len(tokens)
        for idx, tok in classified:
            q = assign_quintile(idx, line_len)
            cls = tok['cls']
            class_quintile[cls][q] += 1
            total_per_quintile[q] += 1
            n_tokens_used += 1

    print(f"  Lines used (>=5 classified tokens): {n_lines_used}")
    print(f"  Tokens used: {n_tokens_used}")
    print(f"  Quintile totals: {dict(sorted(total_per_quintile.items()))}")

    # Chi2 test for each class vs uniform
    specialist_classes = []
    generalist_classes = []
    class_profiles = {}
    class_entropies = {}

    for cls_id in range(1, N_CLASSES + 1):
        counts = class_quintile[cls_id]
        total_cls = sum(counts.values())
        if total_cls < 10:
            continue

        # Expected under uniform: proportional to quintile totals
        grand_total = sum(total_per_quintile.values())
        expected = {q: total_cls * total_per_quintile[q] / grand_total for q in range(N_QUINTILES)}

        # Chi2
        chi2 = 0.0
        for q in range(N_QUINTILES):
            obs = counts.get(q, 0)
            exp = expected[q]
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp
        df = N_QUINTILES - 1
        p_val = chi2_sf(chi2, df)

        # Positional entropy
        profile = {q: counts.get(q, 0) / total_cls for q in range(N_QUINTILES)}
        ent = 0.0
        for q in range(N_QUINTILES):
            if profile[q] > 0:
                ent -= profile[q] * math.log2(profile[q])
        max_ent = math.log2(N_QUINTILES)  # 2.322

        class_profiles[cls_id] = profile
        class_entropies[cls_id] = ent

        if p_val < 0.001:
            specialist_classes.append({
                'class': cls_id,
                'state': CLASS_TO_STATE[cls_id],
                'chi2': chi2,
                'p': p_val,
                'entropy': ent,
                'max_entropy': max_ent,
                'profile': profile,
                'peak_quintile': max(profile, key=profile.get),
                'total': total_cls,
            })
        else:
            generalist_classes.append({
                'class': cls_id,
                'state': CLASS_TO_STATE[cls_id],
                'chi2': chi2,
                'p': p_val,
                'entropy': ent,
                'total': total_cls,
            })

    n_spec = len(specialist_classes)
    n_gen = len(generalist_classes)
    n_tested = n_spec + n_gen

    if n_spec > 30:
        verdict = 'STRONG'
    elif n_spec > 15:
        verdict = 'MODERATE'
    else:
        verdict = 'WEAK'

    # Top 10 most specialized (lowest entropy)
    specialist_classes.sort(key=lambda x: x['entropy'])
    top10 = specialist_classes[:10]

    print(f"  Specialist classes (p<0.001): {n_spec}/{n_tested}")
    print(f"  Generalist classes: {n_gen}/{n_tested}")
    print(f"  Verdict: {verdict}")
    print(f"\n  Top 10 specialists (lowest entropy):")
    for s in top10:
        peak = s['peak_quintile']
        print(f"    Class {s['class']:2d} ({s['state']:7s}): entropy={s['entropy']:.3f}, "
              f"peak=Q{peak}, chi2={s['chi2']:.1f}, n={s['total']}")

    return {
        'test': 'T1_CLASS_POSITIONAL_SPECIALIZATION',
        'verdict': verdict,
        'n_specialist': n_spec,
        'n_generalist': n_gen,
        'n_tested': n_tested,
        'n_lines': n_lines_used,
        'n_tokens': n_tokens_used,
        'top10_specialists': [{
            'class': s['class'],
            'state': s['state'],
            'entropy': s['entropy'],
            'chi2': s['chi2'],
            'p': s['p'],
            'peak_quintile': s['peak_quintile'],
            'profile': s['profile'],
            'total': s['total'],
        } for s in top10],
        'mean_specialist_entropy': (sum(s['entropy'] for s in specialist_classes) / n_spec
                                    if n_spec > 0 else None),
        'mean_generalist_entropy': (sum(s['entropy'] for s in generalist_classes) / n_gen
                                    if n_gen > 0 else None),
        'max_entropy': math.log2(N_QUINTILES),
    }


# ── T2: Transition Gradient Resolution ────────────────────────────

def test_transition_gradient(all_lines):
    """Compute 49x49 transition matrix per quintile, test for monotonic gradient."""
    print("\n=== T2: TRANSITION GRADIENT RESOLUTION ===")

    # Build per-quintile transition matrices
    quintile_matrices = {q: [[0] * N_CLASSES for _ in range(N_CLASSES)] for q in range(N_QUINTILES)}
    quintile_trans_counts = Counter()

    for folio, section, tokens in all_lines:
        classified = [(i, t) for i, t in enumerate(tokens) if t['cls'] is not None]
        if len(classified) < 5:
            continue
        line_len = len(tokens)

        for j in range(len(classified) - 1):
            idx1, tok1 = classified[j]
            idx2, tok2 = classified[j + 1]
            cls1 = tok1['cls']
            cls2 = tok2['cls']
            # Quintile of source token
            q = assign_quintile(idx1, line_len)
            quintile_matrices[q][cls1 - 1][cls2 - 1] += 1
            quintile_trans_counts[q] += 1

    print(f"  Transitions per quintile: {dict(sorted(quintile_trans_counts.items()))}")

    # Normalize to probability matrices
    def normalize_matrix(m):
        normed = []
        for row in m:
            total = sum(row)
            if total > 0:
                normed.append([x / total for x in row])
            else:
                normed.append([0.0] * N_CLASSES)
        return normed

    normed_matrices = {q: normalize_matrix(quintile_matrices[q]) for q in range(N_QUINTILES)}

    # Compute pairwise JSD between quintile matrices
    # Flatten each matrix to a single distribution over (src, tgt) pairs
    def matrix_to_dist(m):
        flat = {}
        for i in range(N_CLASSES):
            row_total = sum(m[i])
            for j in range(N_CLASSES):
                if m[i][j] > 0:
                    flat[(i, j)] = m[i][j]
        total = sum(flat.values())
        if total > 0:
            return {k: v / total for k, v in flat.items()}
        return flat

    raw_dists = {q: matrix_to_dist(quintile_matrices[q]) for q in range(N_QUINTILES)}

    def dict_jsd(d1, d2):
        """JSD between two dict distributions, converting to aligned lists."""
        keys = sorted(set(d1.keys()) | set(d2.keys()))
        p = [d1.get(k, 0.0) for k in keys]
        q = [d2.get(k, 0.0) for k in keys]
        return jsd(p, q)

    pair_jsd = {}
    for q1 in range(N_QUINTILES):
        for q2 in range(q1 + 1, N_QUINTILES):
            j = dict_jsd(raw_dists[q1], raw_dists[q2])
            pair_jsd[(q1, q2)] = j

    print(f"\n  Pairwise JSD (quintile pairs):")
    for (q1, q2), j in sorted(pair_jsd.items()):
        print(f"    Q{q1}-Q{q2}: {j:.4f}")

    # Test monotonic gradient: |q1-q2| vs JSD
    distances = []
    jsds = []
    for (q1, q2), j in pair_jsd.items():
        distances.append(abs(q1 - q2))
        jsds.append(j)

    rho, p_rho = spearman_rho(distances, jsds)

    # Permutation test for significance of JSD differences
    # Null: shuffle quintile labels across all transitions
    all_transitions = []
    for folio, section, tokens in all_lines:
        classified = [(i, t) for i, t in enumerate(tokens) if t['cls'] is not None]
        if len(classified) < 5:
            continue
        line_len = len(tokens)
        for j in range(len(classified) - 1):
            idx1, tok1 = classified[j]
            cls1 = tok1['cls']
            cls2 = classified[j + 1][1]['cls']
            q = assign_quintile(idx1, line_len)
            all_transitions.append((q, cls1, cls2))

    # Compute observed mean JSD
    obs_mean_jsd = sum(pair_jsd.values()) / len(pair_jsd)

    # Permutation: shuffle quintile assignments
    rng = random.Random(SEED)
    perm_mean_jsds = []
    quintiles_list = [t[0] for t in all_transitions]
    for _ in range(N_PERM):
        shuffled = quintiles_list[:]
        rng.shuffle(shuffled)
        perm_matrices = {q: [[0] * N_CLASSES for _ in range(N_CLASSES)] for q in range(N_QUINTILES)}
        for k, (_, cls1, cls2) in enumerate(all_transitions):
            sq = shuffled[k]
            perm_matrices[sq][cls1 - 1][cls2 - 1] += 1
        perm_dists = {q: matrix_to_dist(perm_matrices[q]) for q in range(N_QUINTILES)}
        perm_jsds = []
        for q1 in range(N_QUINTILES):
            for q2 in range(q1 + 1, N_QUINTILES):
                perm_jsds.append(dict_jsd(perm_dists[q1], perm_dists[q2]))
        perm_mean_jsds.append(sum(perm_jsds) / len(perm_jsds))

    perm_p = sum(1 for x in perm_mean_jsds if x >= obs_mean_jsd) / N_PERM

    # AXM self-transition by quintile
    axm_self = {}
    for q in range(N_QUINTILES):
        axm_src = 0
        axm_self_count = 0
        for cls1 in MACRO_STATE_PARTITION['AXM']:
            for cls2 in range(1, N_CLASSES + 1):
                axm_src += quintile_matrices[q][cls1 - 1][cls2 - 1]
            for cls2 in MACRO_STATE_PARTITION['AXM']:
                axm_self_count += quintile_matrices[q][cls1 - 1][cls2 - 1]
        axm_self[q] = axm_self_count / axm_src if axm_src > 0 else 0.0

    # Verdict
    if rho > 0.5 and p_rho < 0.05:
        verdict = 'GRADIENT'
    elif perm_p < 0.01:
        verdict = 'STRUCTURED'
    else:
        verdict = 'FLAT'

    print(f"\n  Mean JSD: {obs_mean_jsd:.4f}, perm p: {perm_p:.4f}")
    print(f"  Spearman rho (|distance| vs JSD): {rho:.4f}, p={p_rho:.4f}")
    print(f"  AXM self-transition by quintile: {' '.join(f'Q{q}={v:.3f}' for q, v in sorted(axm_self.items()))}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T2_TRANSITION_GRADIENT_RESOLUTION',
        'verdict': verdict,
        'pairwise_jsd': {f'Q{q1}_Q{q2}': j for (q1, q2), j in sorted(pair_jsd.items())},
        'mean_jsd': obs_mean_jsd,
        'perm_p': perm_p,
        'spearman_rho': rho,
        'spearman_p': p_rho,
        'axm_self_by_quintile': {f'Q{q}': v for q, v in sorted(axm_self.items())},
        'n_transitions': sum(quintile_trans_counts.values()),
        'transitions_per_quintile': {f'Q{q}': c for q, c in sorted(quintile_trans_counts.items())},
    }


# ── T3: Forbidden Transition Localization ─────────────────────────

def test_forbidden_localization(all_lines, morph):
    """Test where in lines forbidden MIDDLE transitions are observed."""
    print("\n=== T3: FORBIDDEN TRANSITION LOCALIZATION ===")

    forbidden_positions = []   # normalized positions of forbidden violations
    all_positions = []         # normalized positions of ALL transitions
    n_forbidden_found = 0
    n_total_transitions = 0
    forbidden_type_counts = Counter()

    for folio, section, tokens in all_lines:
        line_len = len(tokens)
        if line_len < 2:
            continue
        for i in range(line_len - 1):
            mid1 = tokens[i]['middle']
            mid2 = tokens[i + 1]['middle']
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            n_total_transitions += 1
            all_positions.append(norm_pos)

            if (mid1, mid2) in FORBIDDEN_MIDDLE_PAIRS:
                forbidden_positions.append(norm_pos)
                n_forbidden_found += 1
                forbidden_type_counts[(mid1, mid2)] += 1

    print(f"  Total MIDDLE transitions: {n_total_transitions}")
    print(f"  Forbidden violations found: {n_forbidden_found}")
    print(f"  Violation rate: {n_forbidden_found / n_total_transitions:.4f}" if n_total_transitions > 0 else "  N/A")

    if n_forbidden_found < 10:
        print(f"  Too few forbidden violations ({n_forbidden_found}) for statistical test")
        return {
            'test': 'T3_FORBIDDEN_TRANSITION_LOCALIZATION',
            'verdict': 'INSUFFICIENT_DATA',
            'n_forbidden': n_forbidden_found,
            'n_total': n_total_transitions,
        }

    # KS test vs uniform [0,1]
    forbidden_sorted = sorted(forbidden_positions)
    n = len(forbidden_sorted)
    ks_stat = 0.0
    for i, val in enumerate(forbidden_sorted):
        d_plus = (i + 1) / n - val
        d_minus = val - i / n
        ks_stat = max(ks_stat, d_plus, d_minus)

    # KS critical values (approximate, using Kolmogorov distribution)
    # For large n, critical value at alpha=0.01 is ~1.63/sqrt(n)
    ks_crit_01 = 1.63 / math.sqrt(n)
    ks_crit_05 = 1.36 / math.sqrt(n)
    ks_p_approx = 'p<0.01' if ks_stat > ks_crit_01 else ('p<0.05' if ks_stat > ks_crit_05 else 'p>=0.05')

    # Quintile distribution of forbidden vs all
    forb_quintile = Counter()
    all_quintile = Counter()
    for pos in forbidden_positions:
        forb_quintile[min(4, int(pos * 5))] += 1
    for pos in all_positions:
        all_quintile[min(4, int(pos * 5))] += 1

    # Entropy of forbidden quintile distribution
    forb_ent = entropy_from_counts(forb_quintile)
    all_ent = entropy_from_counts(all_quintile)

    verdict = 'LOCALIZED' if ks_stat > ks_crit_01 else 'DISPERSED'

    print(f"  KS statistic: {ks_stat:.4f}, critical(0.01)={ks_crit_01:.4f}, {ks_p_approx}")
    print(f"  Forbidden quintile distribution: {dict(sorted(forb_quintile.items()))}")
    print(f"  All transitions quintile: {dict(sorted(all_quintile.items()))}")
    print(f"  Forbidden entropy: {forb_ent:.3f}, all: {all_ent:.3f}")
    print(f"  Top forbidden types:")
    for (m1, m2), cnt in forbidden_type_counts.most_common(5):
        print(f"    {m1}->{m2}: {cnt}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T3_FORBIDDEN_TRANSITION_LOCALIZATION',
        'verdict': verdict,
        'n_forbidden': n_forbidden_found,
        'n_total': n_total_transitions,
        'violation_rate': n_forbidden_found / n_total_transitions if n_total_transitions > 0 else 0,
        'ks_stat': ks_stat,
        'ks_crit_01': ks_crit_01,
        'ks_p_approx': ks_p_approx,
        'forbidden_quintile_dist': {f'Q{q}': forb_quintile.get(q, 0) for q in range(N_QUINTILES)},
        'all_quintile_dist': {f'Q{q}': all_quintile.get(q, 0) for q in range(N_QUINTILES)},
        'forbidden_entropy': forb_ent,
        'all_entropy': all_ent,
        'top_types': {f'{m1}->{m2}': cnt for (m1, m2), cnt in forbidden_type_counts.most_common(10)},
    }


# ── T4: Positional Motif Detection ───────────────────────────────

def test_positional_motifs(all_lines):
    """Test for class bigrams with significant positional preference."""
    print("\n=== T4: POSITIONAL MOTIF DETECTION ===")

    # Count bigrams per quintile
    bigram_quintile = defaultdict(lambda: Counter())  # (cls1, cls2) -> Counter(quintile)
    quintile_totals = Counter()
    bigram_totals = Counter()

    for folio, section, tokens in all_lines:
        classified = [(i, t) for i, t in enumerate(tokens) if t['cls'] is not None]
        if len(classified) < 5:
            continue
        line_len = len(tokens)

        for j in range(len(classified) - 1):
            idx1, tok1 = classified[j]
            cls1 = tok1['cls']
            cls2 = classified[j + 1][1]['cls']
            q = assign_quintile(idx1, line_len)
            bigram = (cls1, cls2)
            bigram_quintile[bigram][q] += 1
            quintile_totals[q] += 1
            bigram_totals[bigram] += 1

    grand_total = sum(quintile_totals.values())
    n_bigram_types = len(bigram_totals)
    print(f"  Unique bigram types: {n_bigram_types}")
    print(f"  Total bigrams: {grand_total}")

    # Chi2 test for each bigram: observed vs expected (bigram_marginal * quintile_marginal)
    bonferroni_threshold = 0.001 / n_bigram_types  # very conservative
    significant_bigrams = []

    for bigram, total_b in bigram_totals.items():
        if total_b < 10:  # need sufficient counts
            continue
        chi2 = 0.0
        for q in range(N_QUINTILES):
            obs = bigram_quintile[bigram].get(q, 0)
            exp = total_b * quintile_totals[q] / grand_total
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp
        df = N_QUINTILES - 1
        p_val = chi2_sf(chi2, df)

        if p_val < bonferroni_threshold:
            # Find peak quintile
            profile = {q: bigram_quintile[bigram].get(q, 0) / total_b for q in range(N_QUINTILES)}
            peak_q = max(profile, key=profile.get)
            enrichment = profile[peak_q] / (quintile_totals[peak_q] / grand_total)

            significant_bigrams.append({
                'bigram': bigram,
                'chi2': chi2,
                'p': p_val,
                'total': total_b,
                'peak_quintile': peak_q,
                'enrichment': enrichment,
                'profile': profile,
            })

    n_sig = len(significant_bigrams)
    if n_sig > 100:
        verdict = 'STEREOTYPED'
    elif n_sig > 30:
        verdict = 'MODERATE'
    else:
        verdict = 'FREE'

    # Sort by chi2 descending for top motifs
    significant_bigrams.sort(key=lambda x: x['chi2'], reverse=True)
    top15 = significant_bigrams[:15]

    # Count by peak quintile
    peak_dist = Counter(s['peak_quintile'] for s in significant_bigrams)

    print(f"  Significant position-locked bigrams (Bonferroni p<{bonferroni_threshold:.2e}): {n_sig}")
    print(f"  Peak quintile distribution: {dict(sorted(peak_dist.items()))}")
    print(f"  Top 15 motifs:")
    for m in top15:
        cls1, cls2 = m['bigram']
        s1, s2 = CLASS_TO_STATE[cls1], CLASS_TO_STATE[cls2]
        print(f"    {cls1:2d}({s1:4s})->{cls2:2d}({s2:4s}): peak=Q{m['peak_quintile']}, "
              f"enrich={m['enrichment']:.2f}x, chi2={m['chi2']:.1f}, n={m['total']}")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T4_POSITIONAL_MOTIF_DETECTION',
        'verdict': verdict,
        'n_significant': n_sig,
        'n_tested': n_bigram_types,
        'bonferroni_threshold': bonferroni_threshold,
        'peak_quintile_distribution': {f'Q{q}': peak_dist.get(q, 0) for q in range(N_QUINTILES)},
        'top15_motifs': [{
            'bigram': f'{m["bigram"][0]}->{m["bigram"][1]}',
            'states': f'{CLASS_TO_STATE[m["bigram"][0]]}->{CLASS_TO_STATE[m["bigram"][1]]}',
            'chi2': m['chi2'],
            'p': m['p'],
            'total': m['total'],
            'peak_quintile': m['peak_quintile'],
            'enrichment': m['enrichment'],
            'profile': m['profile'],
        } for m in top15],
    }


# ── T5: Position-Conditioned Generative Improvement ──────────────

def test_generative_improvement(all_lines):
    """Compare M2 (stationary) vs M2p (quintile-conditioned) generation."""
    print("\n=== T5: POSITION-CONDITIONED GENERATIVE IMPROVEMENT ===")

    rng = random.Random(SEED)

    # Build real data structures
    # Per-quintile class distributions and transition matrices
    real_quintile_class = {q: Counter() for q in range(N_QUINTILES)}
    real_quintile_trans = {q: [[0] * N_CLASSES for _ in range(N_CLASSES)] for q in range(N_QUINTILES)}
    real_class_positions = defaultdict(list)  # class -> [quintiles]
    real_line_lengths = []  # lengths of classified token sequences
    real_initial_class = Counter()  # first classified token class
    real_initial_by_q = {q: Counter() for q in range(N_QUINTILES)}  # not used but available

    # Global (stationary) transition matrix
    global_trans = [[0] * N_CLASSES for _ in range(N_CLASSES)]

    for folio, section, tokens in all_lines:
        classified = [(i, t) for i, t in enumerate(tokens) if t['cls'] is not None]
        if len(classified) < 5:
            continue
        line_len = len(tokens)
        real_line_lengths.append(len(classified))

        if classified:
            real_initial_class[classified[0][1]['cls']] += 1

        for k, (idx, tok) in enumerate(classified):
            q = assign_quintile(idx, line_len)
            cls = tok['cls']
            real_quintile_class[q][cls] += 1
            real_class_positions[cls].append(q)

            if k < len(classified) - 1:
                cls2 = classified[k + 1][1]['cls']
                real_quintile_trans[q][cls - 1][cls2 - 1] += 1
                global_trans[cls - 1][cls2 - 1] += 1

    # Normalize transition matrices
    def normalize_row(row):
        total = sum(row)
        if total > 0:
            return [x / total for x in row]
        # Uniform fallback
        return [1.0 / N_CLASSES] * N_CLASSES

    global_normed = [normalize_row(row) for row in global_trans]
    quintile_normed = {q: [normalize_row(row) for row in real_quintile_trans[q]]
                       for q in range(N_QUINTILES)}

    # Initial class distribution (normalized)
    init_total = sum(real_initial_class.values())
    init_probs = [real_initial_class.get(c, 0) / init_total for c in range(1, N_CLASSES + 1)]

    # Generate synthetic lines
    def sample_class(probs, rng):
        r = rng.random()
        cumsum = 0.0
        for i, p in enumerate(probs):
            cumsum += p
            if r <= cumsum:
                return i + 1  # classes are 1-indexed
        return N_CLASSES

    def generate_m2_line(length, rng):
        """Stationary Markov chain."""
        line = [sample_class(init_probs, rng)]
        for _ in range(length - 1):
            cur = line[-1]
            line.append(sample_class(global_normed[cur - 1], rng))
        return line

    def generate_m2p_line(length, rng):
        """Quintile-conditioned Markov chain."""
        line = [sample_class(init_probs, rng)]
        for pos in range(1, length):
            q = assign_quintile(pos, length)
            cur = line[-1]
            prev_q = assign_quintile(pos - 1, length)
            line.append(sample_class(quintile_normed[prev_q][cur - 1], rng))
        return line

    # Sample line lengths from real distribution
    print(f"  Generating {N_SYNTH} synthetic lines for M2 and M2p...")
    m2_lines = []
    m2p_lines = []
    for _ in range(N_SYNTH):
        length = rng.choice(real_line_lengths)
        m2_lines.append(generate_m2_line(length, rng))
        m2p_lines.append(generate_m2p_line(length, rng))

    # Compute metrics for synthetic data
    def compute_metrics(synth_lines):
        s_quintile_class = {q: Counter() for q in range(N_QUINTILES)}
        s_quintile_trans = {q: [[0] * N_CLASSES for _ in range(N_CLASSES)] for q in range(N_QUINTILES)}
        s_class_positions = defaultdict(list)

        for line in synth_lines:
            length = len(line)
            for pos, cls in enumerate(line):
                q = assign_quintile(pos, length)
                s_quintile_class[q][cls] += 1
                s_class_positions[cls].append(q)
                if pos < length - 1:
                    cls2 = line[pos + 1]
                    s_quintile_trans[q][cls - 1][cls2 - 1] += 1

        return s_quintile_class, s_quintile_trans, s_class_positions

    m2_qc, m2_qt, m2_cp = compute_metrics(m2_lines)
    m2p_qc, m2p_qt, m2p_cp = compute_metrics(m2p_lines)

    # Metric (a): Per-quintile class distribution KL
    def quintile_class_kl(synth_qc, real_qc):
        kls = []
        for q in range(N_QUINTILES):
            real_total = sum(real_qc[q].values())
            synth_total = sum(synth_qc[q].values())
            if real_total == 0 or synth_total == 0:
                continue
            p = {c: real_qc[q].get(c, 0) / real_total for c in range(1, N_CLASSES + 1)}
            q_dist = {c: synth_qc[q].get(c, 0) / synth_total for c in range(1, N_CLASSES + 1)}
            kls.append(kl_divergence(p, q_dist))
        return sum(kls) / len(kls) if kls else 0.0

    m2_metric_a = quintile_class_kl(m2_qc, real_quintile_class)
    m2p_metric_a = quintile_class_kl(m2p_qc, real_quintile_class)

    # Metric (b): Per-quintile transition KL
    def quintile_trans_kl(synth_qt, real_qt):
        kls = []
        for q in range(N_QUINTILES):
            real_flat = {}
            synth_flat = {}
            r_total = 0
            s_total = 0
            for i in range(N_CLASSES):
                for j in range(N_CLASSES):
                    rv = real_qt[q][i][j]
                    sv = synth_qt[q][i][j]
                    if rv > 0 or sv > 0:
                        real_flat[(i, j)] = rv
                        synth_flat[(i, j)] = sv
                        r_total += rv
                        s_total += sv
            if r_total == 0 or s_total == 0:
                continue
            p = {k: v / r_total for k, v in real_flat.items()}
            q_dist = {k: v / s_total for k, v in synth_flat.items()}
            # Use JSD instead of KL (more symmetric, handles zeros better)
            keys = set(p.keys()) | set(q_dist.keys())
            keys_sorted = sorted(keys)
            p_list = [p.get(k, 0.0) for k in keys_sorted]
            q_list = [q_dist.get(k, 0.0) for k in keys_sorted]
            kls.append(jsd(p_list, q_list))
        return sum(kls) / len(kls) if kls else 0.0

    m2_metric_b = quintile_trans_kl(m2_qt, real_quintile_trans)
    m2p_metric_b = quintile_trans_kl(m2p_qt, real_quintile_trans)

    # Metric (c): Per-class positional entropy match
    def class_pos_entropy_match(synth_cp, real_cp):
        diffs = []
        for cls in range(1, N_CLASSES + 1):
            real_qs = real_cp.get(cls, [])
            synth_qs = synth_cp.get(cls, [])
            if len(real_qs) < 10:
                continue
            real_ent = entropy_from_counts(Counter(real_qs))
            synth_ent = entropy_from_counts(Counter(synth_qs)) if synth_qs else math.log2(N_QUINTILES)
            diffs.append(abs(real_ent - synth_ent))
        return sum(diffs) / len(diffs) if diffs else 0.0

    m2_metric_c = class_pos_entropy_match(m2_cp, real_class_positions)
    m2p_metric_c = class_pos_entropy_match(m2p_cp, real_class_positions)

    # Metric (d): AXM self-transition by quintile match
    def axm_self_match(synth_qt, real_qt):
        diffs = []
        for q in range(N_QUINTILES):
            for mat, label in [(real_qt, 'real'), (synth_qt, 'synth')]:
                axm_src = 0
                axm_self = 0
                for cls1 in MACRO_STATE_PARTITION['AXM']:
                    for cls2 in range(1, N_CLASSES + 1):
                        axm_src += mat[q][cls1 - 1][cls2 - 1]
                    for cls2 in MACRO_STATE_PARTITION['AXM']:
                        axm_self += mat[q][cls1 - 1][cls2 - 1]
                if label == 'real':
                    real_rate = axm_self / axm_src if axm_src > 0 else 0
                else:
                    synth_rate = axm_self / axm_src if axm_src > 0 else 0
            diffs.append(abs(real_rate - synth_rate))
        return sum(diffs) / len(diffs)

    m2_metric_d = axm_self_match(m2_qt, real_quintile_trans)
    m2p_metric_d = axm_self_match(m2p_qt, real_quintile_trans)

    # Metric (e): Specialist-class positional accuracy
    # For classes with strong positional preference (from T1-like analysis), check accuracy
    def specialist_accuracy(synth_cp, real_cp):
        # Find specialist classes: those where >40% of occurrences are in one quintile
        specialist_hits = []
        for cls in range(1, N_CLASSES + 1):
            real_qs = real_cp.get(cls, [])
            if len(real_qs) < 20:
                continue
            real_dist = Counter(real_qs)
            total = sum(real_dist.values())
            peak_q = max(real_dist, key=real_dist.get)
            peak_frac = real_dist[peak_q] / total
            if peak_frac < 0.30:
                continue  # not specialist enough

            # Check how well synthetic matches the peak quintile fraction
            synth_qs = synth_cp.get(cls, [])
            if not synth_qs:
                specialist_hits.append(abs(peak_frac - 0.2))  # worst case
                continue
            synth_dist = Counter(synth_qs)
            synth_total = sum(synth_dist.values())
            synth_peak_frac = synth_dist.get(peak_q, 0) / synth_total
            specialist_hits.append(abs(peak_frac - synth_peak_frac))

        return sum(specialist_hits) / len(specialist_hits) if specialist_hits else 0.0

    m2_metric_e = specialist_accuracy(m2_cp, real_class_positions)
    m2p_metric_e = specialist_accuracy(m2p_cp, real_class_positions)

    # Score: M2p wins on each metric (lower = better for all)
    metrics = {
        'a_quintile_class_kl': (m2_metric_a, m2p_metric_a),
        'b_quintile_trans_jsd': (m2_metric_b, m2p_metric_b),
        'c_class_pos_entropy': (m2_metric_c, m2p_metric_c),
        'd_axm_self_match': (m2_metric_d, m2p_metric_d),
        'e_specialist_accuracy': (m2_metric_e, m2p_metric_e),
    }

    m2p_wins = 0
    for name, (m2_val, m2p_val) in metrics.items():
        if m2p_val < m2_val:
            m2p_wins += 1
        print(f"  {name}: M2={m2_val:.6f}, M2p={m2p_val:.6f}, "
              f"winner={'M2p' if m2p_val < m2_val else 'M2'}")

    if m2p_wins >= 3:
        verdict = 'IMPROVEMENT'
    elif m2p_wins >= 1:
        verdict = 'MARGINAL'
    else:
        verdict = 'NONE'

    print(f"\n  M2p wins: {m2p_wins}/5")
    print(f"  Verdict: {verdict}")

    return {
        'test': 'T5_POSITION_CONDITIONED_GENERATIVE_IMPROVEMENT',
        'verdict': verdict,
        'm2p_wins': m2p_wins,
        'metrics': {name: {'m2': m2_val, 'm2p': m2p_val, 'winner': 'M2p' if m2p_val < m2_val else 'M2'}
                    for name, (m2_val, m2p_val) in metrics.items()},
        'n_synth_lines': N_SYNTH,
        'n_real_lines': len(real_line_lengths),
        'mean_line_length': sum(real_line_lengths) / len(real_line_lengths) if real_line_lengths else 0,
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("Phase 474: LINE_MICRO_GRAMMAR")
    print("=" * 60)

    all_lines, token_to_class, morph = load_data()

    t1_result = test_class_positional_specialization(all_lines)
    t2_result = test_transition_gradient(all_lines)
    t3_result = test_forbidden_localization(all_lines, morph)
    t4_result = test_positional_motifs(all_lines)
    t5_result = test_generative_improvement(all_lines)

    # Overall verdict
    verdicts = [t1_result['verdict'], t2_result['verdict'], t3_result['verdict'],
                t4_result['verdict'], t5_result['verdict']]
    print(f"\n{'=' * 60}")
    print(f"VERDICTS: T1={verdicts[0]}, T2={verdicts[1]}, T3={verdicts[2]}, "
          f"T4={verdicts[3]}, T5={verdicts[4]}")

    results = {
        'phase': 'LINE_MICRO_GRAMMAR',
        'phase_number': 474,
        'tests': [t1_result, t2_result, t3_result, t4_result, t5_result],
        'verdicts': {f'T{i+1}': v for i, v in enumerate(verdicts)},
        'elapsed_seconds': round(time.time() - t0, 1),
    }

    out_path = RESULTS_DIR / 'line_micro_grammar.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults written to {out_path}")
    print(f"Elapsed: {results['elapsed_seconds']}s")


if __name__ == '__main__':
    main()
