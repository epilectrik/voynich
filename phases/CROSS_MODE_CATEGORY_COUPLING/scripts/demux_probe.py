#!/usr/bin/env python3
"""Phase 460b: Intra-Line Demultiplexing Probe

Tests whether within-line token sequences contain two interleaved coherent
threads (A-like = terminal-suffixed, B-like = bare-suffixed) that individually
show stronger category sequencing than the mixed stream.

Hypothesis: Lines look like "loose bags" because two multiplexed signals
are being analyzed as one. Demultiplexing by suffix type may reveal
coherent category sequences in each thread.

Tests:
  T1: Interleaving pattern - do A-like and B-like tokens alternate or cluster?
  T2: Demux coherence - does each thread show stronger category transitions?
  T3: Cross-thread coupling - do adjacent A/B tokens show category relationships?
  T4: Thread-internal category runs - longer same-category runs in threads?
  T5: Demux vs mixed entropy comparison (permutation controlled)
  T6: Category sequence predictability by thread
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from math import log2

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
BONFERRONI_P = 0.05 / 6  # 0.00833

CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
              'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}

# Category assignment
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


def suffix_type(sfx):
    """Classify suffix into A-like, B-like, or other."""
    if sfx in TERMINAL_SUFFIXES:
        return 'TERM'  # A-like
    elif sfx in CONNECTOR_SUFFIXES:
        return 'CONN'
    elif sfx in ITERATE_SUFFIXES:
        return 'ITER'
    else:
        return 'BARE'  # B-like


def transition_entropy(cat_sequence):
    """Compute category transition entropy for a sequence of categories."""
    if len(cat_sequence) < 2:
        return None
    trans = Counter()
    source_counts = Counter()
    for i in range(len(cat_sequence) - 1):
        s = cat_sequence[i]
        t = cat_sequence[i + 1]
        trans[(s, t)] += 1
        source_counts[s] += 1
    # H(next | current) = weighted average entropy
    total = sum(source_counts.values())
    if total == 0:
        return None
    h = 0.0
    for s, ns in source_counts.items():
        # Entropy of transitions from s
        targets = {t: c for (src, t), c in trans.items() if src == s}
        hs = 0.0
        for t, c in targets.items():
            p = c / ns
            if p > 0:
                hs -= p * log2(p)
        h += (ns / total) * hs
    return h


def max_transition_entropy(n_categories):
    """Maximum possible transition entropy."""
    return log2(n_categories)


def category_run_length(cat_sequence):
    """Compute mean run length of same-category tokens."""
    if not cat_sequence:
        return 0.0
    runs = []
    current = cat_sequence[0]
    length = 1
    for i in range(1, len(cat_sequence)):
        if cat_sequence[i] == current:
            length += 1
        else:
            runs.append(length)
            current = cat_sequence[i]
            length = 1
    runs.append(length)
    return np.mean(runs)


# ============================================================
# Data Loading
# ============================================================

def load_data():
    t0 = time.time()
    mid_to_cat = build_category_map()
    print(f"  Category map: {len(mid_to_cat)} MIDDLEs")

    tx = Transcript()
    morph = Morphology()

    b_tokens = []
    for tok in tx.currier_b():
        w = tok.word
        if not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle or ''
        sfx = m.suffix or ''
        cat = mid_to_cat.get(mid)
        if not cat and mid:
            cat = auto_assign_category(mid)
        stype = suffix_type(sfx)
        b_tokens.append({
            'word': w,
            'folio': tok.folio,
            'line': tok.line,
            'middle': mid,
            'suffix': sfx,
            'suffix_type': stype,
            'category': cat,
        })
    print(f"  B tokens: {len(b_tokens)}")

    # Group by line
    line_groups = defaultdict(list)
    for tok in b_tokens:
        line_groups[(tok['folio'], tok['line'])].append(tok)

    # Filter to lines with 6+ tokens (enough for meaningful demux)
    lines = {}
    for key, toks in line_groups.items():
        if len(toks) >= 6:
            lines[key] = toks

    print(f"  Lines with 6+ tokens: {len(lines)}")

    # Suffix type distribution
    stype_counts = Counter()
    for tok in b_tokens:
        stype_counts[tok['suffix_type']] += 1
    total = sum(stype_counts.values())
    for st in ['TERM', 'BARE', 'CONN', 'ITER']:
        print(f"    {st}: {stype_counts[st]} ({100*stype_counts[st]/total:.1f}%)")

    print(f"  Data loaded in {time.time()-t0:.1f}s")
    return lines, morph


# ============================================================
# T1: Interleaving Pattern
# ============================================================

def test_t1_interleaving(lines):
    """Do A-like (TERM) and B-like (BARE) tokens interleave or cluster within lines?"""
    print("\n=== T1: Interleaving Pattern ===")

    # For each line, compute alternation rate between TERM and BARE tokens
    # (ignoring CONN and ITER positions)
    alternation_rates = []
    cluster_sizes_term = []
    cluster_sizes_bare = []
    n_mixed_lines = 0

    for key, toks in lines.items():
        # Extract binary sequence: only TERM and BARE tokens, in order
        binary = []
        for tok in toks:
            if tok['suffix_type'] == 'TERM':
                binary.append('T')
            elif tok['suffix_type'] == 'BARE':
                binary.append('B')
            # Skip CONN and ITER

        if len(binary) < 4:
            continue

        n_term = sum(1 for b in binary if b == 'T')
        n_bare = sum(1 for b in binary if b == 'B')
        if n_term < 1 or n_bare < 1:
            continue  # Need both types

        n_mixed_lines += 1

        # Count alternations (T->B or B->T transitions)
        alternations = sum(1 for i in range(len(binary) - 1) if binary[i] != binary[i+1])
        alt_rate = alternations / (len(binary) - 1)
        alternation_rates.append(alt_rate)

        # Cluster sizes
        current = binary[0]
        run = 1
        for i in range(1, len(binary)):
            if binary[i] == current:
                run += 1
            else:
                if current == 'T':
                    cluster_sizes_term.append(run)
                else:
                    cluster_sizes_bare.append(run)
                current = binary[i]
                run = 1
        if current == 'T':
            cluster_sizes_term.append(run)
        else:
            cluster_sizes_bare.append(run)

    print(f"  Mixed lines (both TERM+BARE, 4+ binary tokens): {n_mixed_lines}")

    if not alternation_rates:
        print("  -> FAIL (no mixed lines)")
        return {'test': 'T1_interleaving', 'verdict': 'FAIL', 'reason': 'no_mixed_lines'}

    mean_alt = np.mean(alternation_rates)
    # Expected alternation rate for random arrangement:
    # For a binary sequence with p(T) and p(B), expected alt rate = 2*p*q
    # But varies per line. Compute expected per line and compare.

    # Permutation: shuffle TERM/BARE labels within each line
    rng = np.random.default_rng(SEED)
    null_alt_rates = []
    for _ in range(N_PERM):
        perm_rates = []
        for key, toks in lines.items():
            binary = []
            for tok in toks:
                if tok['suffix_type'] in ('TERM', 'BARE'):
                    binary.append(tok['suffix_type'])
            if len(binary) < 4:
                continue
            n_t = sum(1 for b in binary if b == 'TERM')
            if n_t < 1 or n_t >= len(binary):
                continue
            shuffled = list(binary)
            rng.shuffle(shuffled)
            alt = sum(1 for i in range(len(shuffled) - 1) if shuffled[i] != shuffled[i+1])
            perm_rates.append(alt / (len(shuffled) - 1))
        null_alt_rates.append(np.mean(perm_rates))

    null_mean = np.mean(null_alt_rates)
    null_std = np.std(null_alt_rates)

    # If observed > null: interleaving (more alternation than random)
    # If observed < null: clustering (less alternation than random)
    perm_p_interleave = (sum(1 for nr in null_alt_rates if nr >= mean_alt) + 1) / (len(null_alt_rates) + 1)
    perm_p_cluster = (sum(1 for nr in null_alt_rates if nr <= mean_alt) + 1) / (len(null_alt_rates) + 1)

    direction = 'INTERLEAVED' if mean_alt > null_mean else 'CLUSTERED'
    z = (mean_alt - null_mean) / null_std if null_std > 0 else 0

    print(f"  Mean alternation rate: {mean_alt:.4f}")
    print(f"  Null mean: {null_mean:.4f} std: {null_std:.4f}")
    print(f"  Z-score: {z:+.2f} -> {direction}")
    print(f"  p(interleave): {perm_p_interleave:.4f}, p(cluster): {perm_p_cluster:.4f}")
    print(f"  TERM cluster size: mean={np.mean(cluster_sizes_term):.2f}")
    print(f"  BARE cluster size: mean={np.mean(cluster_sizes_bare):.2f}")

    best_p = min(perm_p_interleave, perm_p_cluster)
    verd = 'PASS' if best_p < BONFERRONI_P else ('WEAK' if best_p < 0.05 else 'FAIL')
    print(f"  -> {verd} ({direction})")

    return {
        'test': 'T1_interleaving',
        'verdict': verd,
        'direction': direction,
        'mean_alternation_rate': float(mean_alt),
        'null_mean': float(null_mean),
        'null_std': float(null_std),
        'z_score': float(z),
        'perm_p_interleave': float(perm_p_interleave),
        'perm_p_cluster': float(perm_p_cluster),
        'n_mixed_lines': n_mixed_lines,
        'term_cluster_mean': float(np.mean(cluster_sizes_term)),
        'bare_cluster_mean': float(np.mean(cluster_sizes_bare)),
    }


# ============================================================
# T2: Demux Coherence - Thread-Separated Transition Entropy
# ============================================================

def test_t2_demux_coherence(lines):
    """Does each suffix-type thread show lower category transition entropy than the mixed stream?"""
    print("\n=== T2: Demux Coherence ===")

    mixed_entropies = []
    term_entropies = []
    bare_entropies = []

    for key, toks in lines.items():
        cats_all = [tok['category'] for tok in toks if tok['category']]
        cats_term = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'TERM']
        cats_bare = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'BARE']

        h_all = transition_entropy(cats_all)
        h_term = transition_entropy(cats_term)
        h_bare = transition_entropy(cats_bare)

        if h_all is not None:
            mixed_entropies.append(h_all)
        if h_term is not None:
            term_entropies.append(h_term)
        if h_bare is not None:
            bare_entropies.append(h_bare)

    print(f"  Lines with mixed entropy: {len(mixed_entropies)}")
    print(f"  Lines with TERM thread entropy: {len(term_entropies)}")
    print(f"  Lines with BARE thread entropy: {len(bare_entropies)}")

    mean_mixed = np.mean(mixed_entropies) if mixed_entropies else 0
    mean_term = np.mean(term_entropies) if term_entropies else 0
    mean_bare = np.mean(bare_entropies) if bare_entropies else 0

    print(f"  Mixed stream mean H: {mean_mixed:.4f}")
    print(f"  TERM thread mean H: {mean_term:.4f}")
    print(f"  BARE thread mean H: {mean_bare:.4f}")

    # Statistical tests: is each thread's entropy lower than mixed?
    # Need paired comparison - only use lines that have all three
    paired_data = []
    for key, toks in lines.items():
        cats_all = [tok['category'] for tok in toks if tok['category']]
        cats_term = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'TERM']
        cats_bare = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'BARE']

        h_all = transition_entropy(cats_all)
        h_term = transition_entropy(cats_term)
        h_bare = transition_entropy(cats_bare)

        if h_all is not None and h_term is not None and h_bare is not None:
            paired_data.append((h_all, h_term, h_bare))

    print(f"  Lines with all three measures: {len(paired_data)}")

    if len(paired_data) < 20:
        print("  -> FAIL (insufficient paired lines)")
        return {'test': 'T2_demux_coherence', 'verdict': 'FAIL', 'reason': 'insufficient_paired'}

    mixed_arr = np.array([p[0] for p in paired_data])
    term_arr = np.array([p[1] for p in paired_data])
    bare_arr = np.array([p[2] for p in paired_data])

    # Wilcoxon signed-rank: is TERM entropy < mixed?
    stat_term, p_term = stats.wilcoxon(term_arr, mixed_arr, alternative='less')
    # Wilcoxon signed-rank: is BARE entropy < mixed?
    stat_bare, p_bare = stats.wilcoxon(bare_arr, mixed_arr, alternative='less')

    # Effect sizes
    mean_reduction_term = np.mean(mixed_arr - term_arr)
    mean_reduction_bare = np.mean(mixed_arr - bare_arr)

    print(f"  TERM vs Mixed: reduction={mean_reduction_term:+.4f} p={p_term:.6f}")
    print(f"  BARE vs Mixed: reduction={mean_reduction_bare:+.4f} p={p_bare:.6f}")

    # Average demux entropy (mean of TERM and BARE thread entropies)
    avg_demux = np.mean([term_arr, bare_arr], axis=0)
    stat_avg, p_avg = stats.wilcoxon(avg_demux, mixed_arr, alternative='less')
    mean_reduction_avg = np.mean(mixed_arr - avg_demux)
    print(f"  Avg demux vs Mixed: reduction={mean_reduction_avg:+.4f} p={p_avg:.6f}")

    any_pass = p_term < BONFERRONI_P or p_bare < BONFERRONI_P
    verd = 'PASS' if any_pass else ('WEAK' if min(p_term, p_bare) < 0.05 else 'FAIL')
    print(f"  -> {verd}")

    return {
        'test': 'T2_demux_coherence',
        'verdict': verd,
        'n_paired_lines': len(paired_data),
        'mean_mixed_H': float(mean_mixed),
        'mean_term_H': float(mean_term),
        'mean_bare_H': float(mean_bare),
        'term_vs_mixed_p': float(p_term),
        'bare_vs_mixed_p': float(p_bare),
        'avg_demux_vs_mixed_p': float(p_avg),
        'mean_reduction_term': float(mean_reduction_term),
        'mean_reduction_bare': float(mean_reduction_bare),
        'mean_reduction_avg': float(mean_reduction_avg),
    }


# ============================================================
# T3: Cross-Thread Coupling
# ============================================================

def test_t3_cross_thread(lines):
    """Do adjacent TERM/BARE tokens show structured category relationships?"""
    print("\n=== T3: Cross-Thread Coupling ===")

    # Build cross-thread transition table:
    # When a TERM token is followed by a BARE token (or vice versa),
    # what category transition occurs?
    term_to_bare = Counter()  # (term_cat, bare_cat)
    bare_to_term = Counter()  # (bare_cat, term_cat)
    same_term = Counter()     # (term_cat, term_cat)
    same_bare = Counter()     # (bare_cat, bare_cat)

    for key, toks in lines.items():
        cat_toks = [(tok['suffix_type'], tok['category']) for tok in toks if tok['category']]
        for i in range(len(cat_toks) - 1):
            st1, c1 = cat_toks[i]
            st2, c2 = cat_toks[i + 1]
            if st1 == 'TERM' and st2 == 'BARE':
                term_to_bare[(c1, c2)] += 1
            elif st1 == 'BARE' and st2 == 'TERM':
                bare_to_term[(c1, c2)] += 1
            elif st1 == 'TERM' and st2 == 'TERM':
                same_term[(c1, c2)] += 1
            elif st1 == 'BARE' and st2 == 'BARE':
                same_bare[(c1, c2)] += 1

    def build_table(counter):
        table = np.zeros((8, 8), dtype=float)
        for (c1, c2), cnt in counter.items():
            if c1 in CAT_IDX and c2 in CAT_IDX:
                table[CAT_IDX[c1], CAT_IDX[c2]] = cnt
        return table

    def test_table(table, label):
        n = table.sum()
        if n < 20:
            print(f"  {label}: N={int(n)} (insufficient)")
            return {'n': int(n), 'verdict': 'INSUFFICIENT'}
        rm = table.sum(axis=1) > 0
        cm = table.sum(axis=0) > 0
        reduced = table[np.ix_(rm, cm)]
        if reduced.shape[0] < 2 or reduced.shape[1] < 2:
            print(f"  {label}: degenerate")
            return {'n': int(n), 'verdict': 'DEGENERATE'}
        chi2, p, _, _ = stats.chi2_contingency(reduced)
        k = min(reduced.shape) - 1
        v = np.sqrt(chi2 / (reduced.sum() * k)) if k > 0 else 0.0
        verd = 'PASS' if p < BONFERRONI_P else ('WEAK' if p < 0.05 else 'FAIL')
        print(f"  {label}: N={int(n)} Chi2={chi2:.1f} V={v:.3f} p={p:.2e} -> {verd}")
        return {'n': int(n), 'chi_squared': float(chi2), 'cramers_v': float(v),
                'p_value': float(p), 'verdict': verd}

    r_tb = test_table(build_table(term_to_bare), "TERM->BARE (cross-thread)")
    r_bt = test_table(build_table(bare_to_term), "BARE->TERM (cross-thread)")
    r_tt = test_table(build_table(same_term), "TERM->TERM (within-thread)")
    r_bb = test_table(build_table(same_bare), "BARE->BARE (within-thread)")

    # Key comparison: is cross-thread V higher than within-thread V?
    cross_v = np.mean([r_tb.get('cramers_v', 0) or 0, r_bt.get('cramers_v', 0) or 0])
    within_v = np.mean([r_tt.get('cramers_v', 0) or 0, r_bb.get('cramers_v', 0) or 0])
    print(f"  Cross-thread mean V: {cross_v:.3f}")
    print(f"  Within-thread mean V: {within_v:.3f}")

    any_cross_pass = r_tb.get('verdict') == 'PASS' or r_bt.get('verdict') == 'PASS'
    verd = 'PASS' if any_cross_pass else 'FAIL'
    if not any_cross_pass:
        if r_tb.get('verdict') == 'WEAK' or r_bt.get('verdict') == 'WEAK':
            verd = 'WEAK'
    print(f"  -> {verd}")

    return {
        'test': 'T3_cross_thread',
        'verdict': verd,
        'term_to_bare': r_tb,
        'bare_to_term': r_bt,
        'term_to_term': r_tt,
        'bare_to_bare': r_bb,
        'cross_thread_mean_v': float(cross_v),
        'within_thread_mean_v': float(within_v),
    }


# ============================================================
# T4: Thread-Internal Category Runs
# ============================================================

def test_t4_category_runs(lines):
    """Do demultiplexed threads have longer same-category runs than the mixed stream?"""
    print("\n=== T4: Thread-Internal Category Runs ===")

    mixed_runs = []
    term_runs = []
    bare_runs = []

    for key, toks in lines.items():
        cats_all = [tok['category'] for tok in toks if tok['category']]
        cats_term = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'TERM']
        cats_bare = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'BARE']

        if len(cats_all) >= 4:
            mixed_runs.append(category_run_length(cats_all))
        if len(cats_term) >= 3:
            term_runs.append(category_run_length(cats_term))
        if len(cats_bare) >= 3:
            bare_runs.append(category_run_length(cats_bare))

    print(f"  Mixed lines: {len(mixed_runs)} (mean run: {np.mean(mixed_runs):.3f})")
    print(f"  TERM threads: {len(term_runs)} (mean run: {np.mean(term_runs):.3f})")
    print(f"  BARE threads: {len(bare_runs)} (mean run: {np.mean(bare_runs):.3f})")

    # Paired comparison on lines that have all three
    paired = []
    for key, toks in lines.items():
        cats_all = [tok['category'] for tok in toks if tok['category']]
        cats_term = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'TERM']
        cats_bare = [tok['category'] for tok in toks if tok['category'] and tok['suffix_type'] == 'BARE']

        if len(cats_all) >= 4 and len(cats_term) >= 3 and len(cats_bare) >= 3:
            paired.append((
                category_run_length(cats_all),
                category_run_length(cats_term),
                category_run_length(cats_bare),
            ))

    print(f"  Paired lines: {len(paired)}")

    if len(paired) < 20:
        print("  -> FAIL (insufficient)")
        return {'test': 'T4_category_runs', 'verdict': 'FAIL', 'reason': 'insufficient'}

    mixed_arr = np.array([p[0] for p in paired])
    term_arr = np.array([p[1] for p in paired])
    bare_arr = np.array([p[2] for p in paired])

    # Are thread runs longer than mixed runs?
    stat_term, p_term = stats.wilcoxon(term_arr, mixed_arr, alternative='greater')
    stat_bare, p_bare = stats.wilcoxon(bare_arr, mixed_arr, alternative='greater')

    print(f"  TERM runs > Mixed: mean diff={np.mean(term_arr - mixed_arr):+.3f} p={p_term:.6f}")
    print(f"  BARE runs > Mixed: mean diff={np.mean(bare_arr - mixed_arr):+.3f} p={p_bare:.6f}")

    any_pass = p_term < BONFERRONI_P or p_bare < BONFERRONI_P
    verd = 'PASS' if any_pass else ('WEAK' if min(p_term, p_bare) < 0.05 else 'FAIL')
    print(f"  -> {verd}")

    return {
        'test': 'T4_category_runs',
        'verdict': verd,
        'n_paired': len(paired),
        'mean_mixed_run': float(np.mean(mixed_runs)),
        'mean_term_run': float(np.mean(term_runs)) if term_runs else None,
        'mean_bare_run': float(np.mean(bare_runs)) if bare_runs else None,
        'term_vs_mixed_p': float(p_term),
        'bare_vs_mixed_p': float(p_bare),
        'mean_diff_term': float(np.mean(term_arr - mixed_arr)),
        'mean_diff_bare': float(np.mean(bare_arr - mixed_arr)),
    }


# ============================================================
# T5: Demux vs Mixed Entropy (Permutation Control)
# ============================================================

def test_t5_permutation_control(lines):
    """Is the entropy reduction from demuxing real, or an artifact of shorter subsequences?"""
    print("\n=== T5: Permutation Control (Entropy Reduction) ===")

    # Shorter sequences naturally have lower transition entropy due to
    # fewer observed transitions. Control: shuffle suffix types within
    # each line and re-compute the demux entropy reduction.

    rng = np.random.default_rng(SEED)

    # Observed reduction
    def compute_entropy_reduction(line_dict):
        reductions = []
        for key, toks in line_dict.items():
            cat_toks = [(tok['suffix_type'], tok['category']) for tok in toks if tok['category']]
            if len(cat_toks) < 6:
                continue

            cats_all = [c for _, c in cat_toks]
            cats_term = [c for st, c in cat_toks if st == 'TERM']
            cats_bare = [c for st, c in cat_toks if st == 'BARE']

            h_all = transition_entropy(cats_all)
            h_term = transition_entropy(cats_term)
            h_bare = transition_entropy(cats_bare)

            if h_all is not None and h_term is not None and h_bare is not None:
                avg_demux = (h_term + h_bare) / 2
                reductions.append(h_all - avg_demux)
        return np.mean(reductions) if reductions else 0.0

    observed_reduction = compute_entropy_reduction(lines)
    print(f"  Observed mean entropy reduction: {observed_reduction:.4f}")

    # Permutation: shuffle suffix_type labels within each line
    null_reductions = []
    for _ in range(N_PERM):
        shuffled_lines = {}
        for key, toks in lines.items():
            stypes = [tok['suffix_type'] for tok in toks]
            rng.shuffle(stypes)
            shuffled_toks = []
            for tok, st in zip(toks, stypes):
                new_tok = dict(tok)
                new_tok['suffix_type'] = st
                shuffled_toks.append(new_tok)
            shuffled_lines[key] = shuffled_toks
        null_reductions.append(compute_entropy_reduction(shuffled_lines))

    null_mean = np.mean(null_reductions)
    null_std = np.std(null_reductions)
    perm_p = (sum(1 for nr in null_reductions if nr >= observed_reduction) + 1) / (len(null_reductions) + 1)
    z = (observed_reduction - null_mean) / null_std if null_std > 0 else 0

    print(f"  Null mean: {null_mean:.4f} std: {null_std:.4f}")
    print(f"  Z-score: {z:+.2f}")
    print(f"  Permutation p: {perm_p:.4f}")

    verd = 'PASS' if perm_p < BONFERRONI_P else ('WEAK' if perm_p < 0.05 else 'FAIL')
    print(f"  -> {verd}")

    return {
        'test': 'T5_permutation_control',
        'verdict': verd,
        'observed_reduction': float(observed_reduction),
        'null_mean': float(null_mean),
        'null_std': float(null_std),
        'z_score': float(z),
        'perm_p': float(perm_p),
    }


# ============================================================
# T6: Category Sequence Predictability by Thread
# ============================================================

def test_t6_predictability(lines):
    """Can we predict the next token's category better within a thread than in the mixed stream?"""
    print("\n=== T6: Category Sequence Predictability by Thread ===")

    # Build transition matrices for mixed, TERM-thread, and BARE-thread
    mixed_trans = defaultdict(Counter)
    term_trans = defaultdict(Counter)
    bare_trans = defaultdict(Counter)

    for key, toks in lines.items():
        cat_toks = [(tok['suffix_type'], tok['category']) for tok in toks if tok['category']]

        # Mixed stream transitions
        for i in range(len(cat_toks) - 1):
            mixed_trans[cat_toks[i][1]][cat_toks[i+1][1]] += 1

        # Thread-separated transitions
        term_cats = [c for st, c in cat_toks if st == 'TERM']
        bare_cats = [c for st, c in cat_toks if st == 'BARE']

        for i in range(len(term_cats) - 1):
            term_trans[term_cats[i]][term_cats[i+1]] += 1
        for i in range(len(bare_cats) - 1):
            bare_trans[bare_cats[i]][bare_cats[i+1]] += 1

    def matrix_entropy(trans_dict):
        """Weighted conditional entropy H(next|current) from transition counts."""
        total = sum(sum(v.values()) for v in trans_dict.values())
        if total == 0:
            return None
        h = 0.0
        for src, targets in trans_dict.items():
            ns = sum(targets.values())
            if ns == 0:
                continue
            ps = ns / total
            hs = 0.0
            for t, c in targets.items():
                p = c / ns
                if p > 0:
                    hs -= p * log2(p)
            h += ps * hs
        return h

    h_mixed = matrix_entropy(mixed_trans)
    h_term = matrix_entropy(term_trans)
    h_bare = matrix_entropy(bare_trans)

    print(f"  Mixed stream H(next|current): {h_mixed:.4f}" if h_mixed else "  Mixed: N/A")
    print(f"  TERM thread H(next|current): {h_term:.4f}" if h_term else "  TERM: N/A")
    print(f"  BARE thread H(next|current): {h_bare:.4f}" if h_bare else "  BARE: N/A")

    if h_mixed and h_term and h_bare:
        # Entropy reduction
        term_reduction = h_mixed - h_term
        bare_reduction = h_mixed - h_bare
        avg_reduction = (term_reduction + bare_reduction) / 2
        print(f"  TERM reduction: {term_reduction:+.4f} ({100*term_reduction/h_mixed:.1f}%)")
        print(f"  BARE reduction: {bare_reduction:+.4f} ({100*bare_reduction/h_mixed:.1f}%)")
        print(f"  Avg reduction: {avg_reduction:+.4f} ({100*avg_reduction/h_mixed:.1f}%)")

        # Also: what are the dominant transitions in each thread?
        print(f"\n  Top TERM transitions:")
        term_total = sum(sum(v.values()) for v in term_trans.values())
        top_term = sorted(
            [(s, t, c) for s, targets in term_trans.items() for t, c in targets.items()],
            key=lambda x: -x[2]
        )[:5]
        for s, t, c in top_term:
            print(f"    {s:15s} -> {t:15s}: {c} ({100*c/term_total:.1f}%)")

        print(f"\n  Top BARE transitions:")
        bare_total = sum(sum(v.values()) for v in bare_trans.values())
        top_bare = sorted(
            [(s, t, c) for s, targets in bare_trans.items() for t, c in targets.items()],
            key=lambda x: -x[2]
        )[:5]
        for s, t, c in top_bare:
            print(f"    {s:15s} -> {t:15s}: {c} ({100*c/bare_total:.1f}%)")
    else:
        term_reduction = 0
        bare_reduction = 0
        avg_reduction = 0

    # Verdict based on whether threads are more predictable
    verd = 'PASS' if avg_reduction > 0.05 else ('WEAK' if avg_reduction > 0.02 else 'FAIL')
    print(f"  -> {verd}")

    return {
        'test': 'T6_predictability',
        'verdict': verd,
        'h_mixed': float(h_mixed) if h_mixed else None,
        'h_term': float(h_term) if h_term else None,
        'h_bare': float(h_bare) if h_bare else None,
        'term_reduction': float(term_reduction),
        'bare_reduction': float(bare_reduction),
        'avg_reduction': float(avg_reduction),
    }


# ============================================================
# Bonus: Category Distribution by Suffix Type
# ============================================================

def describe_thread_categories(lines):
    """Show category distributions for each suffix type."""
    print("\n=== Category Distribution by Suffix Type ===")

    cat_by_stype = defaultdict(Counter)
    for key, toks in lines.items():
        for tok in toks:
            if tok['category']:
                cat_by_stype[tok['suffix_type']][tok['category']] += 1

    print(f"  {'Category':15s}", end='')
    for st in ['TERM', 'BARE', 'CONN', 'ITER']:
        print(f" {st:>8s}", end='')
    print()

    for cat in CATEGORIES:
        print(f"  {cat:15s}", end='')
        for st in ['TERM', 'BARE', 'CONN', 'ITER']:
            total = sum(cat_by_stype[st].values())
            frac = cat_by_stype[st].get(cat, 0) / total if total > 0 else 0
            print(f" {frac:8.3f}", end='')
        print()

    # Chi-squared: suffix_type x category
    table = np.zeros((4, 8), dtype=float)
    for i, st in enumerate(['TERM', 'BARE', 'CONN', 'ITER']):
        for j, cat in enumerate(CATEGORIES):
            table[i, j] = cat_by_stype[st].get(cat, 0)

    rm = table.sum(axis=1) > 0
    cm = table.sum(axis=0) > 0
    reduced = table[np.ix_(rm, cm)]
    if reduced.shape[0] >= 2 and reduced.shape[1] >= 2:
        chi2, p, _, _ = stats.chi2_contingency(reduced)
        k = min(reduced.shape) - 1
        v = np.sqrt(chi2 / (reduced.sum() * k)) if k > 0 else 0.0
        print(f"\n  Suffix type x Category: Chi2={chi2:.1f} V={v:.3f} p={p:.2e}")
    else:
        v = 0.0
        p = 1.0

    return {
        'suffix_type_x_category_v': float(v),
        'suffix_type_x_category_p': float(p),
    }


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 460b: Intra-Line Demultiplexing Probe")
    print("=" * 60)

    print("\nLoading data...")
    lines, morph = load_data()

    results = {}
    t0 = time.time()

    results['T1'] = test_t1_interleaving(lines)
    results['T2'] = test_t2_demux_coherence(lines)
    results['T3'] = test_t3_cross_thread(lines)
    results['T4'] = test_t4_category_runs(lines)
    results['T5'] = test_t5_permutation_control(lines)
    results['T6'] = test_t6_predictability(lines)

    # Bonus descriptive
    results['thread_categories'] = describe_thread_categories(lines)

    elapsed = time.time() - t0

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    pass_count = 0
    weak_count = 0
    for tname in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']:
        r = results[tname]
        v = r['verdict']
        label = r['test']
        if v == 'PASS':
            pass_count += 1
        elif v == 'WEAK':
            weak_count += 1
        print(f"  {label:<43s} {v:<10s}")

    print(f"\nPASS: {pass_count}/6, WEAK: {weak_count}/6, FAIL: {6-pass_count-weak_count}/6")

    if pass_count >= 4:
        overall = 'DEMUX_CONFIRMED'
    elif pass_count >= 2:
        overall = 'PARTIAL_DEMUX'
    elif pass_count >= 1:
        overall = 'WEAK_DEMUX'
    else:
        overall = 'NO_DEMUX'

    # Critical check: T5 must pass for demux to be real
    if results['T5']['verdict'] == 'FAIL' and pass_count > 0:
        overall += '_ARTIFACT_SUSPECT'

    print(f"Overall verdict: {overall}")
    print(f"Runtime: {elapsed:.1f}s")

    # Save
    output = {
        'phase': 'CROSS_MODE_CATEGORY_COUPLING_DEMUX',
        'phase_number': '460b',
        'overall_verdict': overall,
        'pass_count': pass_count,
        'weak_count': weak_count,
        'fail_count': 6 - pass_count - weak_count,
        'n_lines': len(lines),
        'runtime_seconds': float(elapsed),
        'tests': results,
    }

    out_path = ROOT / 'phases' / 'CROSS_MODE_CATEGORY_COUPLING' / 'results' / 'demux_probe.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
