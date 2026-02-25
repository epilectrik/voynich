#!/usr/bin/env python3
"""Phase 460c: Parallel Track Coupling Probe

Exploratory analysis of how Mode A and Mode B lines relate at the token
level. Instead of testing a specific interleaving hypothesis, we look at
the data from multiple angles to discover the coupling pattern.

If A and B are parallel tracks in a control system, they MUST be coordinated.
The question is: what does that coordination look like?

Probes:
  P1: Positional alignment - do categories at the same relative position couple?
  P2: Cross-sequence category flow - how does A's sequence relate to B's?
  P3: Interleaved coherence scan - try multiple interleaving ratios
  P4: Category handoff patterns - what transitions happen at the A/B boundary?
  P5: Temporal alignment by dynamic warping - best alignment between sequences
  P6: Complementarity structure - do A and B fill each other's gaps?
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from math import log2
from itertools import product

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# Constants
# ============================================================

N_PERM = 1000
SEED = 42

CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
              'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}

GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'fire': 'THERMAL', 'cool': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'gather': 'FLOW', 'discharge': 'FLOW',
    'release': 'FLOW', 'vent': 'FLOW', 'route': 'FLOW',
    'portion': 'FLOW', 'input': 'FLOW', 'intake': 'FLOW',
    'watch': 'MONITORING', 'check': 'MONITORING', 'verify': 'MONITORING',
    'confirm': 'MONITORING', 'scan': 'MONITORING', 'measure': 'MONITORING',
    'control': 'MONITORING', 'regulate': 'MONITORING',
    'work': 'OPERATION', 'operate': 'OPERATION', 'batch': 'OPERATION',
    'pound': 'OPERATION', 'strip': 'OPERATION', 'exact': 'OPERATION',
    'precise': 'OPERATION', 'hard': 'OPERATION', 'wide': 'OPERATION',
    'start': 'TRANSITION', 'open': 'TRANSITION', 'close': 'TRANSITION',
    'end': 'TRANSITION', 'finish': 'TRANSITION', 'complete': 'TRANSITION',
    'finalize': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'stand': 'TRANSITION', 'settle': 'TRANSITION', 'set': 'TRANSITION',
    'halt': 'TRANSITION',
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}

ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {a: GLOSS_TO_CATEGORY[g] for a, g in ATOM_GLOSSES.items()}

MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])

TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def auto_assign_category(atoms_str):
    if not atoms_str:
        return None
    votes = Counter()
    for atom in atoms_str:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]
    return sorted(winners)[0]


def build_category_map():
    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']
    mid_to_cat = {}
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]
    for mid, minfo in mid_dict.items():
        if mid in mid_to_cat:
            continue
        atoms_str = minfo.get('autogloss_atoms', '')
        if atoms_str:
            cat = auto_assign_category(atoms_str)
            if cat:
                mid_to_cat[mid] = cat
    return mid_to_cat


def classify_suffix_mode(line_tokens, morph):
    if len(line_tokens) < 3:
        return None
    n = len(line_tokens)
    cats = [0, 0, 0, 0]
    for tok in line_tokens:
        sfx = morph.extract(tok['word']).suffix or ''
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


def transition_entropy(cat_sequence):
    if len(cat_sequence) < 2:
        return None
    trans = Counter()
    source_counts = Counter()
    for i in range(len(cat_sequence) - 1):
        trans[(cat_sequence[i], cat_sequence[i+1])] += 1
        source_counts[cat_sequence[i]] += 1
    total = sum(source_counts.values())
    if total == 0:
        return None
    h = 0.0
    for s, ns in source_counts.items():
        targets = {t: c for (src, t), c in trans.items() if src == s}
        hs = 0.0
        for t, c in targets.items():
            p = c / ns
            if p > 0:
                hs -= p * log2(p)
        h += (ns / total) * hs
    return h


# ============================================================
# Data Loading & Structure
# ============================================================

def load_and_build(morph):
    mid_to_cat = build_category_map()
    tx = Transcript()

    b_tokens = []
    for tok in tx.currier_b():
        w = tok.word
        if not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle or ''
        cat = mid_to_cat.get(mid)
        if not cat and mid:
            cat = auto_assign_category(mid)
        b_tokens.append({
            'word': w, 'folio': tok.folio, 'line': tok.line,
            'middle': mid, 'suffix': m.suffix or '',
            'prefix': m.prefix or '', 'category': cat,
            'par_initial': tok.par_initial, 'par_final': tok.par_final,
        })

    # Group by line
    line_groups = defaultdict(list)
    for tok in b_tokens:
        line_groups[(tok['folio'], tok['line'])].append(tok)

    # Build paragraphs
    folio_lines = defaultdict(list)
    for (folio, line), toks in sorted(line_groups.items()):
        folio_lines[folio].append({
            'folio': folio, 'line': line, 'tokens': toks,
            'has_par_initial': any(t['par_initial'] for t in toks),
        })

    paragraphs = []
    for folio in sorted(folio_lines.keys()):
        current = []
        for li in folio_lines[folio]:
            if li['has_par_initial'] and current:
                paragraphs.append(current)
                current = []
            current.append(li)
        if current:
            paragraphs.append(current)

    # Classify lines, extract AB pairs
    ab_pairs = []  # (a_line_tokens, b_line_tokens, folio)
    ba_pairs = []

    for para in paragraphs:
        if len(para) < 3:
            continue
        body = para[1:]  # skip header
        classified = []
        for li in body:
            mode = classify_suffix_mode(li['tokens'], morph)
            cat_seq = [t['category'] for t in li['tokens'] if t['category']]
            if mode and len(cat_seq) >= 3:
                classified.append({
                    'mode': mode, 'tokens': li['tokens'],
                    'cat_seq': cat_seq, 'folio': li['folio'],
                })

        for i in range(len(classified) - 1):
            l1 = classified[i]
            l2 = classified[i + 1]
            if l1['mode'] == 'A' and l2['mode'] == 'B':
                ab_pairs.append((l1, l2))
            elif l1['mode'] == 'B' and l2['mode'] == 'A':
                ba_pairs.append((l1, l2))

    return ab_pairs, ba_pairs, paragraphs


# ============================================================
# P1: Positional Alignment
# ============================================================

def probe_positional_alignment(ab_pairs):
    """At the same relative position, do A and B categories couple?"""
    print("\n=== P1: Positional Alignment ===")
    print("  Do categories at the same relative position in A and B lines correlate?")

    # Normalize positions to bins: EARLY (0-0.33), MID (0.33-0.67), LATE (0.67-1.0)
    # For each AB pair, bin tokens by relative position and compare categories
    N_BINS = 5
    joint_by_bin = [Counter() for _ in range(N_BINS)]

    for a_line, b_line in ab_pairs:
        a_cats = a_line['cat_seq']
        b_cats = b_line['cat_seq']

        # Bin each token by relative position
        def bin_cats(cats):
            binned = defaultdict(list)
            n = len(cats)
            for i, c in enumerate(cats):
                b_idx = min(int(i / n * N_BINS), N_BINS - 1)
                binned[b_idx].append(c)
            return binned

        a_binned = bin_cats(a_cats)
        b_binned = bin_cats(b_cats)

        for b_idx in range(N_BINS):
            if b_idx in a_binned and b_idx in b_binned:
                # Dominant category in each bin
                a_dom = Counter(a_binned[b_idx]).most_common(1)[0][0]
                b_dom = Counter(b_binned[b_idx]).most_common(1)[0][0]
                joint_by_bin[b_idx][(a_dom, b_dom)] += 1

    # Build contingency per bin and overall
    match_rates = []
    complement_counts = Counter()
    for b_idx in range(N_BINS):
        total = sum(joint_by_bin[b_idx].values())
        if total < 10:
            continue
        matches = sum(c for (a, b), c in joint_by_bin[b_idx].items() if a == b)
        match_rate = matches / total
        match_rates.append(match_rate)

        bin_label = ['EARLY', 'EARLY-MID', 'MID', 'MID-LATE', 'LATE'][b_idx]
        print(f"  Bin {bin_label}: {total} pairs, same-category rate = {match_rate:.3f}")

        # Track most common A->B category combinations
        for (a, b), c in joint_by_bin[b_idx].items():
            complement_counts[(a, b)] += c

    # Overall same-category rate vs expected by chance
    total_pairs = sum(complement_counts.values())
    total_matches = sum(c for (a, b), c in complement_counts.items() if a == b)
    obs_match = total_matches / total_pairs if total_pairs > 0 else 0

    # Expected match rate: sum of (p_a * p_b) for each category
    all_a = Counter()
    all_b = Counter()
    for (a, b), c in complement_counts.items():
        all_a[a] += c
        all_b[b] += c
    expected_match = sum((all_a[cat]/total_pairs) * (all_b[cat]/total_pairs)
                         for cat in CATEGORIES) if total_pairs > 0 else 0

    print(f"\n  Overall same-category rate: {obs_match:.3f}")
    print(f"  Expected by chance: {expected_match:.3f}")
    print(f"  Ratio: {obs_match/expected_match:.2f}x" if expected_match > 0 else "")

    # Top A->B category combinations
    print(f"\n  Top positional A->B category pairings:")
    top = sorted(complement_counts.items(), key=lambda x: -x[1])[:10]
    for (a, b), c in top:
        label = "SAME" if a == b else "COMP"
        print(f"    {a:15s} -> {b:15s}: {c:4d} ({100*c/total_pairs:.1f}%) [{label}]")

    # Permutation: shuffle B lines among AB pairs
    rng = np.random.default_rng(SEED)
    null_match_rates = []
    b_lines = [b for _, b in ab_pairs]
    for _ in range(N_PERM):
        perm_b = list(b_lines)
        rng.shuffle(perm_b)
        perm_matches = 0
        perm_total = 0
        for (a_line, _), pb in zip(ab_pairs, perm_b):
            a_cats = a_line['cat_seq']
            b_cats = pb['cat_seq']

            def bin_cats_quick(cats):
                binned = {}
                n = len(cats)
                for i, c in enumerate(cats):
                    b_idx = min(int(i / n * N_BINS), N_BINS - 1)
                    if b_idx not in binned:
                        binned[b_idx] = Counter()
                    binned[b_idx][c] += 1
                return binned

            ab = bin_cats_quick(a_cats)
            bb = bin_cats_quick(b_cats)
            for bi in range(N_BINS):
                if bi in ab and bi in bb:
                    a_dom = ab[bi].most_common(1)[0][0]
                    b_dom = bb[bi].most_common(1)[0][0]
                    perm_total += 1
                    if a_dom == b_dom:
                        perm_matches += 1
        if perm_total > 0:
            null_match_rates.append(perm_matches / perm_total)

    perm_p = (sum(1 for nr in null_match_rates if nr >= obs_match) + 1) / (len(null_match_rates) + 1)
    null_mean = np.mean(null_match_rates) if null_match_rates else 0
    print(f"\n  Permutation: null mean={null_mean:.3f}, observed={obs_match:.3f}, p={perm_p:.4f}")

    return {
        'probe': 'P1_positional_alignment',
        'observed_match_rate': float(obs_match),
        'expected_match_rate': float(expected_match),
        'enrichment': float(obs_match / expected_match) if expected_match > 0 else None,
        'perm_p': float(perm_p),
        'null_mean': float(null_mean),
        'n_pairs': len(ab_pairs),
    }


# ============================================================
# P2: Cross-Sequence Category Flow
# ============================================================

def probe_category_flow(ab_pairs, ba_pairs):
    """How does the category sequence in A relate to what follows in B?"""
    print("\n=== P2: Cross-Sequence Category Flow ===")
    print("  What categories does A end with, and what does B start with?")

    # A's last N tokens -> B's first N tokens
    for window in [1, 2, 3]:
        a_end_cats = Counter()
        b_start_cats = Counter()
        cross = Counter()

        for a_line, b_line in ab_pairs:
            a_cats = a_line['cat_seq']
            b_cats = b_line['cat_seq']
            if len(a_cats) >= window and len(b_cats) >= window:
                a_tail = tuple(a_cats[-window:])
                b_head = tuple(b_cats[:window])
                a_end_cats[a_tail[-1]] += 1
                b_start_cats[b_head[0]] += 1
                cross[(a_tail[-1], b_head[0])] += 1

        # Build contingency
        table = np.zeros((8, 8), dtype=float)
        for (a_cat, b_cat), cnt in cross.items():
            if a_cat in CAT_IDX and b_cat in CAT_IDX:
                table[CAT_IDX[a_cat], CAT_IDX[b_cat]] = cnt

        rm = table.sum(axis=1) > 0
        cm = table.sum(axis=0) > 0
        reduced = table[np.ix_(rm, cm)]
        if reduced.shape[0] >= 2 and reduced.shape[1] >= 2:
            chi2, p, _, _ = stats.chi2_contingency(reduced)
            n = reduced.sum()
            k = min(reduced.shape) - 1
            v = np.sqrt(chi2 / (n * k)) if k > 0 else 0.0
            print(f"  Window={window}: A_last -> B_first: N={int(n)} V={v:.3f} p={p:.2e}")
        else:
            print(f"  Window={window}: degenerate")

    # Same for BA pairs: B's last -> A's first
    print()
    for window in [1, 2, 3]:
        cross_ba = Counter()
        for b_line, a_line in ba_pairs:
            b_cats = b_line['cat_seq']
            a_cats = a_line['cat_seq']
            if len(b_cats) >= window and len(a_cats) >= window:
                cross_ba[(b_cats[-1], a_cats[0])] += 1

        table = np.zeros((8, 8), dtype=float)
        for (b_cat, a_cat), cnt in cross_ba.items():
            if b_cat in CAT_IDX and a_cat in CAT_IDX:
                table[CAT_IDX[b_cat], CAT_IDX[a_cat]] = cnt

        rm = table.sum(axis=1) > 0
        cm = table.sum(axis=0) > 0
        reduced = table[np.ix_(rm, cm)]
        if reduced.shape[0] >= 2 and reduced.shape[1] >= 2:
            chi2, p, _, _ = stats.chi2_contingency(reduced)
            n = reduced.sum()
            k = min(reduced.shape) - 1
            v = np.sqrt(chi2 / (n * k)) if k > 0 else 0.0
            print(f"  Window={window}: B_last -> A_first: N={int(n)} V={v:.3f} p={p:.2e}")

    return {'probe': 'P2_category_flow'}


# ============================================================
# P3: Interleaved Coherence Scan
# ============================================================

def probe_interleaved_coherence(ab_pairs):
    """Try multiple interleaving ratios and measure category coherence."""
    print("\n=== P3: Interleaved Coherence Scan ===")
    print("  Trying multiple A:B interleaving ratios")

    def interleave(a_seq, b_seq, a_chunk, b_chunk):
        """Interleave a_seq and b_seq with given chunk sizes."""
        result = []
        ai, bi = 0, 0
        while ai < len(a_seq) or bi < len(b_seq):
            for _ in range(a_chunk):
                if ai < len(a_seq):
                    result.append(a_seq[ai])
                    ai += 1
            for _ in range(b_chunk):
                if bi < len(b_seq):
                    result.append(b_seq[bi])
                    bi += 1
        return result

    ratios = [(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2)]

    # Baseline: individual line entropies
    a_entropies = []
    b_entropies = []
    for a_line, b_line in ab_pairs:
        ha = transition_entropy(a_line['cat_seq'])
        hb = transition_entropy(b_line['cat_seq'])
        if ha is not None:
            a_entropies.append(ha)
        if hb is not None:
            b_entropies.append(hb)

    mean_a_h = np.mean(a_entropies) if a_entropies else 0
    mean_b_h = np.mean(b_entropies) if b_entropies else 0
    baseline_h = (mean_a_h + mean_b_h) / 2
    print(f"  Baseline: A mean H={mean_a_h:.4f}, B mean H={mean_b_h:.4f}, avg={baseline_h:.4f}")

    # Concatenated (A then B, no interleaving)
    concat_entropies = []
    for a_line, b_line in ab_pairs:
        seq = a_line['cat_seq'] + b_line['cat_seq']
        h = transition_entropy(seq)
        if h is not None:
            concat_entropies.append(h)
    mean_concat_h = np.mean(concat_entropies) if concat_entropies else 0
    print(f"  Concatenated (A+B): mean H={mean_concat_h:.4f}")

    results = {}
    for a_chunk, b_chunk in ratios:
        label = f"{a_chunk}:{b_chunk}"
        entropies = []
        for a_line, b_line in ab_pairs:
            seq = interleave(a_line['cat_seq'], b_line['cat_seq'], a_chunk, b_chunk)
            h = transition_entropy(seq)
            if h is not None:
                entropies.append(h)
        if entropies:
            mean_h = np.mean(entropies)
            diff = mean_h - baseline_h
            print(f"  Ratio {label}: mean H={mean_h:.4f} (delta from baseline: {diff:+.4f})")
            results[label] = {'mean_H': float(mean_h), 'delta': float(diff), 'n': len(entropies)}

    # Permutation control: shuffle B lines, compute 1:1 interleaved entropy
    rng = np.random.default_rng(SEED)
    b_lines = [b for _, b in ab_pairs]
    obs_11_h = results.get('1:1', {}).get('mean_H', 0)

    null_11 = []
    for _ in range(N_PERM):
        perm_b = list(b_lines)
        rng.shuffle(perm_b)
        hs = []
        for (a_line, _), pb in zip(ab_pairs, perm_b):
            seq = interleave(a_line['cat_seq'], pb['cat_seq'], 1, 1)
            h = transition_entropy(seq)
            if h is not None:
                hs.append(h)
        if hs:
            null_11.append(np.mean(hs))

    null_mean = np.mean(null_11)
    null_std = np.std(null_11)
    # Lower entropy = more structured
    perm_p = (sum(1 for nh in null_11 if nh <= obs_11_h) + 1) / (len(null_11) + 1)
    z = (obs_11_h - null_mean) / null_std if null_std > 0 else 0

    print(f"\n  1:1 permutation control:")
    print(f"    Observed H={obs_11_h:.4f}, Null mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"    Z={z:+.2f}, p(obs <= null)={perm_p:.4f}")

    return {
        'probe': 'P3_interleaved_coherence',
        'baseline_avg_H': float(baseline_h),
        'concat_H': float(mean_concat_h),
        'ratios': results,
        'perm_1_1': {
            'observed_H': float(obs_11_h),
            'null_mean': float(null_mean),
            'null_std': float(null_std),
            'z_score': float(z),
            'perm_p': float(perm_p),
        },
    }


# ============================================================
# P4: Category Handoff Patterns
# ============================================================

def probe_handoff_patterns(ab_pairs, ba_pairs):
    """What specific category transitions happen at the A-B junction?"""
    print("\n=== P4: Category Handoff Patterns ===")

    # A-line last token -> B-line first token
    ab_handoff = Counter()
    for a_line, b_line in ab_pairs:
        a_last = a_line['cat_seq'][-1]
        b_first = b_line['cat_seq'][0]
        ab_handoff[(a_last, b_first)] += 1

    # B-line last token -> A-line first token
    ba_handoff = Counter()
    for b_line, a_line in ba_pairs:
        b_last = b_line['cat_seq'][-1]
        a_first = a_line['cat_seq'][0]
        ba_handoff[(b_last, a_first)] += 1

    print(f"  AB handoffs (A_last -> B_first): {sum(ab_handoff.values())}")
    top_ab = sorted(ab_handoff.items(), key=lambda x: -x[1])[:8]
    for (a, b), c in top_ab:
        pct = 100 * c / sum(ab_handoff.values())
        print(f"    {a:15s} -> {b:15s}: {c:4d} ({pct:.1f}%)")

    print(f"\n  BA handoffs (B_last -> A_first): {sum(ba_handoff.values())}")
    top_ba = sorted(ba_handoff.items(), key=lambda x: -x[1])[:8]
    for (b, a), c in top_ba:
        pct = 100 * c / sum(ba_handoff.values())
        print(f"    {b:15s} -> {a:15s}: {c:4d} ({pct:.1f}%)")

    # Compare: do AB and BA handoffs differ?
    # Build tables
    ab_table = np.zeros((8, 8), dtype=float)
    for (a, b), c in ab_handoff.items():
        if a in CAT_IDX and b in CAT_IDX:
            ab_table[CAT_IDX[a], CAT_IDX[b]] = c

    ba_table = np.zeros((8, 8), dtype=float)
    for (b, a), c in ba_handoff.items():
        if b in CAT_IDX and a in CAT_IDX:
            ba_table[CAT_IDX[b], CAT_IDX[a]] = c

    # Flatten and compare
    ab_flat = ab_table.flatten()
    ba_flat = ba_table.flatten()
    if ab_flat.sum() > 0 and ba_flat.sum() > 0:
        ab_norm = ab_flat / ab_flat.sum()
        ba_norm = ba_flat / ba_flat.sum()
        # Cosine similarity
        cos = np.dot(ab_norm, ba_norm) / (np.linalg.norm(ab_norm) * np.linalg.norm(ba_norm))
        # Correlation
        rho, p = stats.spearmanr(ab_norm, ba_norm)
        print(f"\n  AB vs BA handoff similarity: cosine={cos:.3f}, rho={rho:.3f} (p={p:.2e})")
        print(f"  {'SYMMETRIC' if cos > 0.8 else 'ASYMMETRIC'}: handoff patterns are {'similar' if cos > 0.8 else 'different'} in each direction")

    return {
        'probe': 'P4_handoff_patterns',
        'n_ab': sum(ab_handoff.values()),
        'n_ba': sum(ba_handoff.values()),
    }


# ============================================================
# P5: Complementarity Structure
# ============================================================

def probe_complementarity(ab_pairs):
    """Do A and B lines fill each other's category gaps?"""
    print("\n=== P5: Complementarity Structure ===")
    print("  Do categories missing from A appear in B (and vice versa)?")

    complement_scores = []
    overlap_scores = []

    for a_line, b_line in ab_pairs:
        a_cats = set(a_line['cat_seq'])
        b_cats = set(b_line['cat_seq'])

        # Categories in B but not A
        b_only = b_cats - a_cats
        a_only = a_cats - b_cats
        overlap = a_cats & b_cats
        union = a_cats | b_cats

        if len(union) > 0:
            complement = len(b_only | a_only) / len(union)  # Fraction that are complementary
            overlap_frac = len(overlap) / len(union)  # Jaccard
            complement_scores.append(complement)
            overlap_scores.append(overlap_frac)

    if not complement_scores:
        print("  No data")
        return {'probe': 'P5_complementarity'}

    mean_comp = np.mean(complement_scores)
    mean_overlap = np.mean(overlap_scores)
    print(f"  Mean complementarity (exclusive fraction): {mean_comp:.3f}")
    print(f"  Mean overlap (Jaccard): {mean_overlap:.3f}")

    # Combined coverage: how many of the 8 categories does A+B cover together?
    coverage = []
    a_coverage = []
    b_coverage = []
    for a_line, b_line in ab_pairs:
        a_cats = set(a_line['cat_seq'])
        b_cats = set(b_line['cat_seq'])
        coverage.append(len(a_cats | b_cats))
        a_coverage.append(len(a_cats))
        b_coverage.append(len(b_cats))

    print(f"  Category coverage: A alone={np.mean(a_coverage):.1f}, B alone={np.mean(b_coverage):.1f}, A+B={np.mean(coverage):.1f} of 8")
    print(f"  Coverage gain from combining: {np.mean(coverage) - max(np.mean(a_coverage), np.mean(b_coverage)):.1f} categories")

    # Permutation: shuffle B lines, measure coverage
    rng = np.random.default_rng(SEED)
    b_lines = [b for _, b in ab_pairs]
    obs_coverage = np.mean(coverage)

    null_coverages = []
    for _ in range(N_PERM):
        perm_b = list(b_lines)
        rng.shuffle(perm_b)
        perm_cov = []
        for (a_line, _), pb in zip(ab_pairs, perm_b):
            perm_cov.append(len(set(a_line['cat_seq']) | set(pb['cat_seq'])))
        null_coverages.append(np.mean(perm_cov))

    null_mean = np.mean(null_coverages)
    # Higher coverage = more complementary
    perm_p = (sum(1 for nc in null_coverages if nc >= obs_coverage) + 1) / (len(null_coverages) + 1)
    print(f"  Coverage permutation: observed={obs_coverage:.2f}, null={null_mean:.2f}, p={perm_p:.4f}")

    # Which categories are A-dominant vs B-dominant in paired context?
    a_cat_freq = Counter()
    b_cat_freq = Counter()
    for a_line, b_line in ab_pairs:
        for c in a_line['cat_seq']:
            a_cat_freq[c] += 1
        for c in b_line['cat_seq']:
            b_cat_freq[c] += 1

    a_total = sum(a_cat_freq.values())
    b_total = sum(b_cat_freq.values())
    print(f"\n  Category specialization in AB pairs:")
    print(f"  {'Category':15s} {'A_frac':>8s} {'B_frac':>8s} {'A/B ratio':>10s} {'Dominant':>10s}")
    for cat in CATEGORIES:
        a_f = a_cat_freq.get(cat, 0) / a_total if a_total > 0 else 0
        b_f = b_cat_freq.get(cat, 0) / b_total if b_total > 0 else 0
        ratio = a_f / b_f if b_f > 0 else float('inf')
        dom = 'A' if ratio > 1.2 else ('B' if ratio < 0.8 else 'SHARED')
        print(f"  {cat:15s} {a_f:8.3f} {b_f:8.3f} {ratio:10.2f} {dom:>10s}")

    return {
        'probe': 'P5_complementarity',
        'mean_complement': float(mean_comp),
        'mean_overlap': float(mean_overlap),
        'mean_combined_coverage': float(obs_coverage),
        'coverage_perm_p': float(perm_p),
    }


# ============================================================
# P6: Position-Resolved Cross-Line MI
# ============================================================

def probe_positional_mi(ab_pairs):
    """At each position, how much does A's category tell us about B's?"""
    print("\n=== P6: Position-Resolved Cross-Line Mutual Information ===")
    print("  Does knowing A's category at position X predict B's category at position X?")

    N_BINS = 5
    bin_labels = ['EARLY', 'EARLY-MID', 'MID', 'MID-LATE', 'LATE']

    for b_idx in range(N_BINS):
        joint = Counter()
        a_marginal = Counter()
        b_marginal = Counter()

        for a_line, b_line in ab_pairs:
            a_cats = a_line['cat_seq']
            b_cats = b_line['cat_seq']

            def get_bin_cat(cats, bi):
                n = len(cats)
                start = int(bi / N_BINS * n)
                end = int((bi + 1) / N_BINS * n)
                if start >= end:
                    return None
                segment = cats[start:end]
                return Counter(segment).most_common(1)[0][0] if segment else None

            a_cat = get_bin_cat(a_cats, b_idx)
            b_cat = get_bin_cat(b_cats, b_idx)
            if a_cat and b_cat:
                joint[(a_cat, b_cat)] += 1
                a_marginal[a_cat] += 1
                b_marginal[b_cat] += 1

        # Compute MI
        total = sum(joint.values())
        if total < 20:
            print(f"  {bin_labels[b_idx]}: insufficient data")
            continue

        mi = 0.0
        for (a, b), c in joint.items():
            pab = c / total
            pa = a_marginal[a] / total
            pb = b_marginal[b] / total
            if pab > 0 and pa > 0 and pb > 0:
                mi += pab * log2(pab / (pa * pb))

        # H(B) for normalization
        hb = 0.0
        for cat, c in b_marginal.items():
            p = c / total
            if p > 0:
                hb -= p * log2(p)

        nmi = mi / hb if hb > 0 else 0  # normalized MI
        print(f"  {bin_labels[b_idx]}: MI={mi:.4f} bits, H(B)={hb:.4f}, NMI={nmi:.3f} (N={total})")

    return {'probe': 'P6_positional_mi'}


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 460c: Parallel Track Coupling Probe")
    print("=" * 60)

    morph = Morphology()

    print("\nLoading and building structures...")
    t0 = time.time()
    ab_pairs, ba_pairs, paragraphs = load_and_build(morph)
    print(f"  AB pairs: {len(ab_pairs)}")
    print(f"  BA pairs: {len(ba_pairs)}")
    print(f"  Loaded in {time.time()-t0:.1f}s")

    results = {}

    results['P1'] = probe_positional_alignment(ab_pairs)
    results['P2'] = probe_category_flow(ab_pairs, ba_pairs)
    results['P3'] = probe_interleaved_coherence(ab_pairs)
    results['P4'] = probe_handoff_patterns(ab_pairs, ba_pairs)
    results['P5'] = probe_complementarity(ab_pairs)
    results['P6'] = probe_positional_mi(ab_pairs)

    # Summary
    print(f"\n{'=' * 60}")
    print("KEY FINDINGS")
    print(f"{'=' * 60}")

    p1 = results['P1']
    print(f"  Positional alignment: match={p1['observed_match_rate']:.3f} vs chance={p1['expected_match_rate']:.3f} "
          f"({p1.get('enrichment', 0):.2f}x), perm p={p1['perm_p']:.4f}")

    p3 = results['P3']
    print(f"  Best interleaving: baseline H={p3['baseline_avg_H']:.4f}")
    for ratio, data in p3['ratios'].items():
        print(f"    {ratio}: H={data['mean_H']:.4f} (delta={data['delta']:+.4f})")
    perm = p3['perm_1_1']
    print(f"  1:1 perm control: Z={perm['z_score']:+.2f} p={perm['perm_p']:.4f}")

    p5 = results['P5']
    print(f"  Complementarity: overlap={p5['mean_overlap']:.3f}, coverage={p5['mean_combined_coverage']:.1f}/8")

    # Save
    out_path = ROOT / 'phases' / 'CROSS_MODE_CATEGORY_COUPLING' / 'results' / 'parallel_track_probe.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
