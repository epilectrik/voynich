"""
Phase 450 Follow-up: PARALLEL MODE TRACKS HYPOTHESIS

Tests whether Mode A and Mode B lines form parallel sequential tracks
within paragraphs — i.e., do A lines couple with the next A line, and
B lines with the next B line, more than expected by chance?

Tests:
  T1: Within-mode MIDDLE vocabulary coupling (A1->A2, B1->B2 Jaccard)
  T2: Within-mode kernel profile continuity (A1->A2, B1->B2 correlation)
  T3: Within-mode FL stage continuity
  T4: Cross-mode functional coupling (does A line predict following B line?)
  T5: Within-mode vs cross-mode coupling comparison

Exclusions:
  - Terminal lines (last body line) excluded from sequential pairs
  - Header lines excluded
  - Lines too short for mode classification (<3 tokens) excluded

References: C670, C1031, C963, C1229, C1231
"""

import sys, json
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy.stats import spearmanr, pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RNG = np.random.RandomState(42)
N_PERM = 1000

# Suffix classification (from C1231)
TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])

KERNEL_CHARS = ['k', 'h', 'e']

FL_MIDDLES = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL',
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE',
    'o': 'FINAL', 'ly': 'FINAL', 'am': 'FINAL',
    'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL',
}
FL_STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']


def classify_suffix_mode(line_toks):
    if len(line_toks) < 3:
        return None
    n = len(line_toks)
    cats = [0, 0, 0, 0]
    for tok in line_toks:
        sfx = tok['suffix']
        if sfx in TERMINAL_SUFFIXES:
            cats[0] += 1
        elif sfx in CONNECTOR_SUFFIXES:
            cats[1] += 1
        elif sfx in ITERATE_SUFFIXES:
            cats[2] += 1
        else:
            cats[3] += 1
    vec = np.array(cats, dtype=float) / n
    dist_a = np.linalg.norm(vec - MODE_A_CENTROID)
    dist_b = np.linalg.norm(vec - MODE_B_CENTROID)
    return 'A' if dist_a < dist_b else 'B'


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0


def kernel_profile(toks):
    n = len(toks)
    if n == 0:
        return np.array([0.0, 0.0, 0.0])
    counts = [0, 0, 0]
    for tok in toks:
        for i, kc in enumerate(KERNEL_CHARS):
            if kc in tok.get('kernels', []):
                counts[i] += 1
    return np.array(counts, dtype=float) / n


def fl_distribution(toks):
    vec = np.zeros(len(FL_STAGES))
    n_fl = 0
    for tok in toks:
        stage = FL_MIDDLES.get(tok['middle'])
        if stage:
            vec[FL_STAGES.index(stage)] += 1
            n_fl += 1
    if n_fl > 0:
        vec /= n_fl
    return vec


def load_data():
    tx = Transcript()
    morph = Morphology()

    tokens = []
    for t in tx.currier_b():
        if t.placement.startswith('L'):
            continue
        if '*' in t.word or not t.word.strip():
            continue
        m = morph.extract(t.word)
        tokens.append({
            'folio': t.folio,
            'line': t.line,
            'word': t.word,
            'middle': m.middle if m else '',
            'suffix': m.suffix if m else '',
            'prefix': m.prefix if m else '',
            'par_initial': t.par_initial,
            'par_final': t.par_final,
            'kernels': [c for c in 'khe' if c in (m.middle if m else '')],
        })

    folio_tokens = defaultdict(list)
    for tok in tokens:
        folio_tokens[tok['folio']].append(tok)

    folios = {}
    for folio, ftoks in folio_tokens.items():
        ftoks.sort(key=lambda t: t['line'])
        lines_dict = defaultdict(list)
        for tok in ftoks:
            lines_dict[tok['line']].append(tok)
        line_nums = sorted(lines_dict.keys())

        paragraphs = []
        current_para = []
        for ln in line_nums:
            line_toks = lines_dict[ln]
            if line_toks[0]['par_initial'] and current_para:
                paragraphs.append(current_para)
                current_para = []
            current_para.append((ln, line_toks))
        if current_para:
            paragraphs.append(current_para)

        folios[folio] = paragraphs

    return folios


def build_paragraph_line_data(folios, min_body_lines=4):
    """Build annotated body lines per paragraph, excluding header and terminal.

    Returns list of paragraphs, each containing annotated body lines with:
    - mode (A/B/None)
    - middles set
    - kernel profile
    - fl distribution
    - is_terminal (last body line)
    """
    all_paragraphs = []

    for folio, paragraphs in folios.items():
        for para in paragraphs:
            if len(para) < 2:  # need at least header + 1 body
                continue

            body_lines = para[1:]  # skip header
            if len(body_lines) < min_body_lines:
                continue

            annotated = []
            for li, (ln, toks) in enumerate(body_lines):
                is_terminal = (li == len(body_lines) - 1)
                mode = classify_suffix_mode(toks)
                middles = set(t['middle'] for t in toks if t['middle'])
                kp = kernel_profile(toks)
                fl = fl_distribution(toks)

                annotated.append({
                    'line_num': ln,
                    'toks': toks,
                    'mode': mode,
                    'middles': middles,
                    'kernel_profile': kp,
                    'fl_dist': fl,
                    'is_terminal': is_terminal,
                    'n_toks': len(toks),
                    'body_index': li,
                })

            all_paragraphs.append({
                'folio': folio,
                'lines': annotated,
                'n_body': len(annotated),
            })

    return all_paragraphs


def extract_mode_pairs(paragraphs, exclude_terminal=True):
    """Extract within-mode sequential pairs and cross-mode adjacent pairs.

    Within-mode: consecutive lines of same mode (skipping interleaved other mode)
    Cross-mode: adjacent lines of different modes (A followed by B, or B followed by A)
    """
    within_a_pairs = []   # (A_line_i, A_line_j) where j is next A after i
    within_b_pairs = []
    cross_ab_pairs = []   # (A_line, following B_line) — adjacent
    cross_ba_pairs = []   # (B_line, following A_line) — adjacent
    all_adjacent = []     # all adjacent line pairs regardless of mode

    for para in paragraphs:
        lines = para['lines']
        usable = []
        for line in lines:
            if exclude_terminal and line['is_terminal']:
                continue
            if line['mode'] is None:
                continue
            usable.append(line)

        if len(usable) < 3:
            continue

        # Within-mode pairs: find next line of same mode
        for i in range(len(usable)):
            # Find next same-mode line
            for j in range(i + 1, len(usable)):
                if usable[j]['mode'] == usable[i]['mode']:
                    pair = (usable[i], usable[j])
                    if usable[i]['mode'] == 'A':
                        within_a_pairs.append(pair)
                    else:
                        within_b_pairs.append(pair)
                    break  # only immediate next same-mode

        # Adjacent pairs (consecutive in body order)
        for i in range(len(usable) - 1):
            pair = (usable[i], usable[i + 1])
            all_adjacent.append(pair)
            if usable[i]['mode'] != usable[i + 1]['mode']:
                if usable[i]['mode'] == 'A':
                    cross_ab_pairs.append(pair)
                else:
                    cross_ba_pairs.append(pair)

    return {
        'within_a': within_a_pairs,
        'within_b': within_b_pairs,
        'cross_ab': cross_ab_pairs,
        'cross_ba': cross_ba_pairs,
        'all_adjacent': all_adjacent,
    }


def pair_jaccard(pairs):
    """Mean Jaccard across a list of (line_i, line_j) pairs."""
    if not pairs:
        return 0.0
    return np.mean([jaccard(a['middles'], b['middles']) for a, b in pairs])


def pair_kernel_correlation(pairs):
    """Mean cosine similarity of kernel profiles across pairs."""
    if len(pairs) < 5:
        return 0.0, 1.0
    sims = []
    for a, b in pairs:
        kp_a = a['kernel_profile']
        kp_b = b['kernel_profile']
        norm_a = np.linalg.norm(kp_a)
        norm_b = np.linalg.norm(kp_b)
        if norm_a > 0 and norm_b > 0:
            sims.append(np.dot(kp_a, kp_b) / (norm_a * norm_b))
    if not sims:
        return 0.0, 1.0
    return np.mean(sims), np.std(sims)


def pair_fl_similarity(pairs):
    """Mean cosine similarity of FL distributions across pairs."""
    if len(pairs) < 5:
        return 0.0
    sims = []
    for a, b in pairs:
        fl_a = a['fl_dist']
        fl_b = b['fl_dist']
        norm_a = np.linalg.norm(fl_a)
        norm_b = np.linalg.norm(fl_b)
        if norm_a > 0 and norm_b > 0:
            sims.append(np.dot(fl_a, fl_b) / (norm_a * norm_b))
    if not sims:
        return 0.0
    return np.mean(sims)


def t1_within_mode_vocabulary(pairs_data, paragraphs):
    """T1: Within-mode MIDDLE vocabulary coupling vs shuffled."""
    print("\nT1: Within-mode MIDDLE vocabulary coupling")
    print("-" * 60)

    obs_within_a = pair_jaccard(pairs_data['within_a'])
    obs_within_b = pair_jaccard(pairs_data['within_b'])
    obs_adjacent = pair_jaccard(pairs_data['all_adjacent'])

    # Permutation: shuffle mode labels within each paragraph, re-extract pairs
    perm_within_a = []
    perm_within_b = []

    for _ in range(N_PERM):
        shuffled_paras = []
        for para in paragraphs:
            lines = [l for l in para['lines']
                     if not l['is_terminal'] and l['mode'] is not None]
            if len(lines) < 3:
                continue
            modes = [l['mode'] for l in lines]
            RNG.shuffle(modes)
            shuffled_lines = []
            for l, m in zip(lines, modes):
                sl = dict(l)
                sl['mode'] = m
                shuffled_lines.append(sl)
            shuffled_paras.append({'lines': shuffled_lines})

        # Re-extract within-mode pairs from shuffled
        s_within_a, s_within_b = [], []
        for sp in shuffled_paras:
            slines = sp['lines']
            for i in range(len(slines)):
                for j in range(i + 1, len(slines)):
                    if slines[j]['mode'] == slines[i]['mode']:
                        pair = (slines[i], slines[j])
                        if slines[i]['mode'] == 'A':
                            s_within_a.append(pair)
                        else:
                            s_within_b.append(pair)
                        break

        perm_within_a.append(pair_jaccard(s_within_a))
        perm_within_b.append(pair_jaccard(s_within_b))

    null_a = np.mean(perm_within_a)
    null_b = np.mean(perm_within_b)
    p_a = np.mean([pv >= obs_within_a for pv in perm_within_a])
    p_b = np.mean([pv >= obs_within_b for pv in perm_within_b])

    ratio_a = obs_within_a / null_a if null_a > 0 else float('inf')
    ratio_b = obs_within_b / null_b if null_b > 0 else float('inf')

    print(f"  Within-A Jaccard: {obs_within_a:.4f} (null {null_a:.4f}, {ratio_a:.2f}x, p={p_a:.4f}) n={len(pairs_data['within_a'])}")
    print(f"  Within-B Jaccard: {obs_within_b:.4f} (null {null_b:.4f}, {ratio_b:.2f}x, p={p_b:.4f}) n={len(pairs_data['within_b'])}")
    print(f"  All adjacent:     {obs_adjacent:.4f} n={len(pairs_data['all_adjacent'])}")

    either_pass = p_a < 0.005 or p_b < 0.005
    print(f"  {'PASS' if either_pass else 'FAIL'}")

    return {
        'test': 'T1_within_mode_vocabulary',
        'within_a_jaccard': round(obs_within_a, 4),
        'within_a_null': round(null_a, 4),
        'within_a_ratio': round(ratio_a, 3),
        'within_a_p': round(p_a, 4),
        'within_a_n': len(pairs_data['within_a']),
        'within_b_jaccard': round(obs_within_b, 4),
        'within_b_null': round(null_b, 4),
        'within_b_ratio': round(ratio_b, 3),
        'within_b_p': round(p_b, 4),
        'within_b_n': len(pairs_data['within_b']),
        'all_adjacent_jaccard': round(obs_adjacent, 4),
        'all_adjacent_n': len(pairs_data['all_adjacent']),
        'pass': bool(either_pass),
        'verdict': 'PASS' if either_pass else 'FAIL',
    }


def t2_within_mode_kernel(pairs_data, paragraphs):
    """T2: Within-mode kernel profile continuity."""
    print("\nT2: Within-mode kernel profile continuity")
    print("-" * 60)

    obs_a, _ = pair_kernel_correlation(pairs_data['within_a'])
    obs_b, _ = pair_kernel_correlation(pairs_data['within_b'])
    obs_adj, _ = pair_kernel_correlation(pairs_data['all_adjacent'])

    # Permutation: shuffle mode labels
    perm_a_vals, perm_b_vals = [], []
    for _ in range(N_PERM):
        shuffled_paras = []
        for para in paragraphs:
            lines = [l for l in para['lines']
                     if not l['is_terminal'] and l['mode'] is not None]
            if len(lines) < 3:
                continue
            modes = [l['mode'] for l in lines]
            RNG.shuffle(modes)
            shuffled_lines = []
            for l, m in zip(lines, modes):
                sl = dict(l)
                sl['mode'] = m
                shuffled_lines.append(sl)
            shuffled_paras.append({'lines': shuffled_lines})

        s_a, s_b = [], []
        for sp in shuffled_paras:
            slines = sp['lines']
            for i in range(len(slines)):
                for j in range(i + 1, len(slines)):
                    if slines[j]['mode'] == slines[i]['mode']:
                        pair = (slines[i], slines[j])
                        if slines[i]['mode'] == 'A':
                            s_a.append(pair)
                        else:
                            s_b.append(pair)
                        break

        pa, _ = pair_kernel_correlation(s_a)
        pb, _ = pair_kernel_correlation(s_b)
        perm_a_vals.append(pa)
        perm_b_vals.append(pb)

    null_a = np.mean(perm_a_vals)
    null_b = np.mean(perm_b_vals)
    p_a = np.mean([pv >= obs_a for pv in perm_a_vals])
    p_b = np.mean([pv >= obs_b for pv in perm_b_vals])

    print(f"  Within-A kernel cosine: {obs_a:.4f} (null {null_a:.4f}, p={p_a:.4f}) n={len(pairs_data['within_a'])}")
    print(f"  Within-B kernel cosine: {obs_b:.4f} (null {null_b:.4f}, p={p_b:.4f}) n={len(pairs_data['within_b'])}")
    print(f"  All adjacent cosine:    {obs_adj:.4f} n={len(pairs_data['all_adjacent'])}")

    either_pass = p_a < 0.005 or p_b < 0.005
    print(f"  {'PASS' if either_pass else 'FAIL'}")

    return {
        'test': 'T2_within_mode_kernel',
        'within_a_cosine': round(obs_a, 4),
        'within_a_null': round(null_a, 4),
        'within_a_p': round(p_a, 4),
        'within_b_cosine': round(obs_b, 4),
        'within_b_null': round(null_b, 4),
        'within_b_p': round(p_b, 4),
        'all_adjacent_cosine': round(obs_adj, 4),
        'pass': bool(either_pass),
        'verdict': 'PASS' if either_pass else 'FAIL',
    }


def t3_within_mode_fl(pairs_data, paragraphs):
    """T3: Within-mode FL stage continuity."""
    print("\nT3: Within-mode FL stage continuity")
    print("-" * 60)

    obs_a = pair_fl_similarity(pairs_data['within_a'])
    obs_b = pair_fl_similarity(pairs_data['within_b'])
    obs_adj = pair_fl_similarity(pairs_data['all_adjacent'])

    # Permutation
    perm_a_vals, perm_b_vals = [], []
    for _ in range(N_PERM):
        shuffled_paras = []
        for para in paragraphs:
            lines = [l for l in para['lines']
                     if not l['is_terminal'] and l['mode'] is not None]
            if len(lines) < 3:
                continue
            modes = [l['mode'] for l in lines]
            RNG.shuffle(modes)
            shuffled_lines = []
            for l, m in zip(lines, modes):
                sl = dict(l)
                sl['mode'] = m
                shuffled_lines.append(sl)
            shuffled_paras.append({'lines': shuffled_lines})

        s_a, s_b = [], []
        for sp in shuffled_paras:
            slines = sp['lines']
            for i in range(len(slines)):
                for j in range(i + 1, len(slines)):
                    if slines[j]['mode'] == slines[i]['mode']:
                        pair = (slines[i], slines[j])
                        if slines[i]['mode'] == 'A':
                            s_a.append(pair)
                        else:
                            s_b.append(pair)
                        break

        perm_a_vals.append(pair_fl_similarity(s_a))
        perm_b_vals.append(pair_fl_similarity(s_b))

    null_a = np.mean(perm_a_vals)
    null_b = np.mean(perm_b_vals)
    p_a = np.mean([pv >= obs_a for pv in perm_a_vals])
    p_b = np.mean([pv >= obs_b for pv in perm_b_vals])

    print(f"  Within-A FL cosine: {obs_a:.4f} (null {null_a:.4f}, p={p_a:.4f}) n={len(pairs_data['within_a'])}")
    print(f"  Within-B FL cosine: {obs_b:.4f} (null {null_b:.4f}, p={p_b:.4f}) n={len(pairs_data['within_b'])}")
    print(f"  All adjacent FL:    {obs_adj:.4f} n={len(pairs_data['all_adjacent'])}")

    either_pass = p_a < 0.005 or p_b < 0.005
    print(f"  {'PASS' if either_pass else 'FAIL'}")

    return {
        'test': 'T3_within_mode_fl',
        'within_a_fl': round(obs_a, 4),
        'within_a_null': round(null_a, 4),
        'within_a_p': round(p_a, 4),
        'within_b_fl': round(obs_b, 4),
        'within_b_null': round(null_b, 4),
        'within_b_p': round(p_b, 4),
        'all_adjacent_fl': round(obs_adj, 4),
        'pass': bool(either_pass),
        'verdict': 'PASS' if either_pass else 'FAIL',
    }


def t4_cross_mode_functional_coupling(pairs_data, paragraphs):
    """T4: Cross-mode functional coupling.

    Does an A line's kernel profile predict the following B line's kernel profile
    (and vice versa)? This tests call-and-response: A specifies, B responds.
    """
    print("\nT4: Cross-mode functional coupling (A->B and B->A)")
    print("-" * 60)

    def kernel_correlation(pair_list):
        if len(pair_list) < 10:
            return 0.0, 1.0
        x = np.array([a['kernel_profile'] for a, b in pair_list])
        y = np.array([b['kernel_profile'] for a, b in pair_list])
        # Correlate each kernel dimension
        rhos = []
        for dim in range(3):
            if np.std(x[:, dim]) > 1e-10 and np.std(y[:, dim]) > 1e-10:
                r, _ = pearsonr(x[:, dim], y[:, dim])
                rhos.append(r)
        return np.mean(rhos) if rhos else 0.0, 0.0

    obs_ab, _ = kernel_correlation(pairs_data['cross_ab'])
    obs_ba, _ = kernel_correlation(pairs_data['cross_ba'])

    # Permutation: shuffle the B lines in A->B pairs (break the coupling)
    perm_ab_vals, perm_ba_vals = [], []
    for _ in range(N_PERM):
        # Shuffle B partners for A->B pairs
        if pairs_data['cross_ab']:
            b_lines = [b for _, b in pairs_data['cross_ab']]
            RNG.shuffle(b_lines)
            shuffled_ab = [(a, b) for (a, _), b in zip(pairs_data['cross_ab'], b_lines)]
            v, _ = kernel_correlation(shuffled_ab)
            perm_ab_vals.append(v)

        if pairs_data['cross_ba']:
            a_lines = [b for _, b in pairs_data['cross_ba']]
            RNG.shuffle(a_lines)
            shuffled_ba = [(a, b) for (a, _), b in zip(pairs_data['cross_ba'], a_lines)]
            v, _ = kernel_correlation(shuffled_ba)
            perm_ba_vals.append(v)

    p_ab = np.mean([pv >= obs_ab for pv in perm_ab_vals]) if perm_ab_vals else 1.0
    p_ba = np.mean([pv >= obs_ba for pv in perm_ba_vals]) if perm_ba_vals else 1.0

    print(f"  A->B kernel correlation: {obs_ab:.4f} (p={p_ab:.4f}) n={len(pairs_data['cross_ab'])}")
    print(f"  B->A kernel correlation: {obs_ba:.4f} (p={p_ba:.4f}) n={len(pairs_data['cross_ba'])}")

    either_pass = p_ab < 0.005 or p_ba < 0.005
    print(f"  {'PASS' if either_pass else 'FAIL'}")

    return {
        'test': 'T4_cross_mode_coupling',
        'ab_correlation': round(obs_ab, 4),
        'ab_p': round(p_ab, 4),
        'ab_n': len(pairs_data['cross_ab']),
        'ba_correlation': round(obs_ba, 4),
        'ba_p': round(p_ba, 4),
        'ba_n': len(pairs_data['cross_ba']),
        'pass': bool(either_pass),
        'verdict': 'PASS' if either_pass else 'FAIL',
    }


def t5_within_vs_cross_comparison(pairs_data):
    """T5: Is within-mode coupling stronger than cross-mode coupling?

    Direct comparison: within-mode Jaccard vs cross-mode Jaccard.
    If modes form parallel tracks, within-mode should be higher.
    """
    print("\nT5: Within-mode vs cross-mode vocabulary comparison")
    print("-" * 60)

    within_a_j = pair_jaccard(pairs_data['within_a'])
    within_b_j = pair_jaccard(pairs_data['within_b'])
    within_mean = (within_a_j * len(pairs_data['within_a']) +
                   within_b_j * len(pairs_data['within_b'])) / \
                  (len(pairs_data['within_a']) + len(pairs_data['within_b'])) \
                  if (pairs_data['within_a'] or pairs_data['within_b']) else 0.0

    cross_pairs = pairs_data['cross_ab'] + pairs_data['cross_ba']
    cross_j = pair_jaccard(cross_pairs)
    adj_j = pair_jaccard(pairs_data['all_adjacent'])

    diff = within_mean - cross_j

    # Permutation: shuffle all pairs together, split randomly
    all_pairs = (pairs_data['within_a'] + pairs_data['within_b'] +
                 pairs_data['cross_ab'] + pairs_data['cross_ba'])
    n_within = len(pairs_data['within_a']) + len(pairs_data['within_b'])

    perm_diffs = []
    all_jaccards = [jaccard(a['middles'], b['middles']) for a, b in all_pairs]
    for _ in range(N_PERM):
        perm_idx = RNG.permutation(len(all_jaccards))
        perm_within = np.mean([all_jaccards[i] for i in perm_idx[:n_within]]) if n_within > 0 else 0.0
        perm_cross = np.mean([all_jaccards[i] for i in perm_idx[n_within:]]) if len(perm_idx) > n_within else 0.0
        perm_diffs.append(perm_within - perm_cross)

    p_value = np.mean([pd >= diff for pd in perm_diffs])

    print(f"  Within-mode mean Jaccard: {within_mean:.4f} (A={within_a_j:.4f}, B={within_b_j:.4f})")
    print(f"  Cross-mode Jaccard:       {cross_j:.4f}")
    print(f"  All adjacent Jaccard:     {adj_j:.4f}")
    print(f"  Difference (within - cross): {diff:+.4f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  {'PASS' if p_value < 0.005 else 'FAIL'}: Within-mode coupling "
          f"{'IS' if p_value < 0.005 else 'is NOT'} stronger than cross-mode")

    return {
        'test': 'T5_within_vs_cross',
        'within_mean_jaccard': round(within_mean, 4),
        'within_a_jaccard': round(within_a_j, 4),
        'within_b_jaccard': round(within_b_j, 4),
        'cross_jaccard': round(cross_j, 4),
        'adjacent_jaccard': round(adj_j, 4),
        'diff': round(diff, 4),
        'p_value': round(p_value, 4),
        'n_within': n_within,
        'n_cross': len(cross_pairs),
        'pass': bool(p_value < 0.005),
        'verdict': 'PASS' if p_value < 0.005 else 'FAIL',
    }


def main():
    print("Phase 450 Follow-up: PARALLEL MODE TRACKS HYPOTHESIS")
    print("=" * 60)

    print("\nLoading data...")
    folios = load_data()
    paragraphs = build_paragraph_line_data(folios, min_body_lines=4)
    print(f"  {len(paragraphs)} paragraphs with 4+ body lines")

    # Count mode distribution in body lines
    n_a, n_b, n_none = 0, 0, 0
    for para in paragraphs:
        for line in para['lines']:
            if line['is_terminal']:
                continue
            if line['mode'] == 'A':
                n_a += 1
            elif line['mode'] == 'B':
                n_b += 1
            else:
                n_none += 1
    print(f"  Non-terminal body lines: {n_a} Mode A, {n_b} Mode B, {n_none} unclassified")

    pairs_data = extract_mode_pairs(paragraphs, exclude_terminal=True)
    print(f"  Within-A pairs: {len(pairs_data['within_a'])}")
    print(f"  Within-B pairs: {len(pairs_data['within_b'])}")
    print(f"  Cross A->B pairs: {len(pairs_data['cross_ab'])}")
    print(f"  Cross B->A pairs: {len(pairs_data['cross_ba'])}")
    print(f"  All adjacent pairs: {len(pairs_data['all_adjacent'])}")

    r1 = t1_within_mode_vocabulary(pairs_data, paragraphs)
    r2 = t2_within_mode_kernel(pairs_data, paragraphs)
    r3 = t3_within_mode_fl(pairs_data, paragraphs)
    r4 = t4_cross_mode_functional_coupling(pairs_data, paragraphs)
    r5 = t5_within_vs_cross_comparison(pairs_data)

    results = [r1, r2, r3, r4, r5]
    n_pass = sum(1 for r in results if r.get('pass'))

    print("\n" + "=" * 60)
    print(f"SUMMARY: {n_pass}/5 tests PASS")

    if n_pass >= 3:
        verdict = "SUPPORTED -- Mode A and B form parallel sequential tracks"
    elif n_pass >= 1:
        verdict = "PARTIAL -- some within-mode structure but not systematic parallel tracks"
    else:
        verdict = "NOT_SUPPORTED -- modes do not form parallel tracks; lines are independently drawn"
    print(f"  OVERALL: {verdict}")

    output = {
        'phase': 'Phase 450 Follow-up: PARALLEL_MODE_TRACKS',
        'n_pass': n_pass,
        'overall_verdict': verdict,
        'data_summary': {
            'n_paragraphs': len(paragraphs),
            'n_mode_a_lines': n_a,
            'n_mode_b_lines': n_b,
            'n_within_a_pairs': len(pairs_data['within_a']),
            'n_within_b_pairs': len(pairs_data['within_b']),
            'n_cross_ab_pairs': len(pairs_data['cross_ab']),
            'n_cross_ba_pairs': len(pairs_data['cross_ba']),
        },
        'T1': r1, 'T2': r2, 'T3': r3, 'T4': r4, 'T5': r5,
    }

    out_path = Path(__file__).resolve().parents[1] / 'results' / 'parallel_mode_tracks_test.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
