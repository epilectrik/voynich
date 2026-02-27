#!/usr/bin/env python3
"""
Phase 476: POSITION_CONDITIONED_GENERATION (M2.1)
==================================================
Tests whether adding quintile-conditioned class frequencies to the M2
generative model closes the position blind spot diagnosed in C1362.

Two models compared side-by-side:
  M2-SF:  49-class Markov + symmetric forbidden suppression (C1034 baseline)
  M2.1:   5 quintile-specific 49x49 matrices + symmetric forbidden suppression

18-metric evaluation battery:
  A1-A4:  Distributional (class KL, hapax, active classes, types)
  B1-B5:  Sequential (spectral gap, AXM self, forbidden, role rank, fwd-rev JSD)
  C1-C3:  Morphological (suffix rate, CC suffix-free, PREFIX entropy reduction)
  D1-D3:  Structural (stationary dist, AXM dwell, cross-line MI)
  P1-P3:  Positional (quintile class KL, quintile trans JSD, specialist accuracy)

Depends on: C1025, C1030, C1034, C1358, C1362, C1363
"""

import json
import sys
import math
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Constants ────────────────────────────────────────────────────────

N_CLASSES = 49
N_QUINTILES = 5
N_RUNS = 10
SEED = 42

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
CLASS_TO_STATE = {}
for _state, _classes in MACRO_STATE_PARTITION.items():
    for _c in _classes:
        CLASS_TO_STATE[_c] = _state
STATE_ORDER = ['AXM', 'AXm', 'FQ', 'CC', 'FL_HAZ', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}

ROLE_CLASSES = {
    'CC':  {10, 11, 12, 17},
    'EN':  {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49},
    'FL':  {7, 30, 38, 40},
    'FQ':  {9, 13, 14, 23},
    'AX':  {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29},
}
CLASS_TO_ROLE = {}
for _role, _classes in ROLE_CLASSES.items():
    for _c in _classes:
        CLASS_TO_ROLE[_c] = _role


# ── Utilities ────────────────────────────────────────────────────────

def assign_quintile(idx, line_len):
    """Map token position to quintile 0-4."""
    return min(N_QUINTILES - 1, int(idx / line_len * N_QUINTILES))


def normalize_rows(m):
    """Row-normalize numpy matrix. Zero rows stay zero."""
    row_sums = m.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # avoid division by zero
    return m / row_sums


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load transcript, build classified token stream and generation params."""
    print("Loading data...")

    # Token -> class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}
    class_to_tokens = defaultdict(list)
    for tok, cls in token_to_class.items():
        class_to_tokens[cls].append(tok)

    # Forbidden MIDDLE pairs (17 pairs from Phase 18A)
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    morph = Morphology()

    # Build real token stream organized by line
    lines = []
    current_line = []
    prev_key = None

    for token in Transcript().currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        cls = token_to_class.get(token.word)
        if cls is None:
            continue

        key = (token.folio, token.line)
        if key != prev_key and current_line:
            lines.append(current_line)
            current_line = []
        prev_key = key

        m = morph.extract(token.word)
        current_line.append({
            'word': token.word,
            'cls': cls,
            'state': CLASS_TO_STATE.get(cls, 'UNK'),
            'role': CLASS_TO_ROLE.get(cls, 'UNK'),
            'prefix': m.prefix if m else None,
            'middle': m.middle if m else token.word,
            'suffix': m.suffix if m else None,
        })
    if current_line:
        lines.append(current_line)

    all_tokens = [t for line in lines for t in line]
    print(f"  {len(all_tokens)} tokens in {len(lines)} lines")

    # Global class transition matrix
    class_trans = np.zeros((N_CLASSES, N_CLASSES))
    for line in lines:
        for i in range(len(line) - 1):
            class_trans[line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

    # Quintile-specific transition matrices
    quintile_trans = {q: np.zeros((N_CLASSES, N_CLASSES)) for q in range(N_QUINTILES)}
    for line in lines:
        line_len = len(line)
        for i in range(line_len - 1):
            q = assign_quintile(i, line_len)  # source token's quintile
            quintile_trans[q][line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

    # Opener class distribution
    opener_counts = Counter(line[0]['cls'] for line in lines if line)
    opener_probs = np.zeros(N_CLASSES)
    for cls, count in opener_counts.items():
        opener_probs[cls - 1] = count
    opener_probs /= max(opener_probs.sum(), 1)

    # Line lengths
    line_lengths = [len(line) for line in lines]

    # Token frequency for class->token sampling
    token_freq = Counter(t['word'] for t in all_tokens)

    # Class -> token sampling distribution
    class_token_probs = {}
    for cls in range(1, N_CLASSES + 1):
        toks = class_to_tokens.get(cls, [])
        if toks:
            counts = [token_freq.get(t, 0) for t in toks]
            total = sum(counts)
            if total > 0:
                class_token_probs[cls] = (toks, np.array(counts, dtype=float) / total)

    # MIDDLE -> classes mapping (for forbidden expansion)
    middle_to_classes = defaultdict(set)
    for t in all_tokens:
        mid = t['middle'] if t['middle'] else ''
        middle_to_classes[mid].add(t['cls'])

    params = {
        'lines': lines,
        'all_tokens': all_tokens,
        'class_trans': class_trans,
        'quintile_trans': quintile_trans,
        'opener_probs': opener_probs,
        'line_lengths': line_lengths,
        'class_token_probs': class_token_probs,
        'class_to_tokens': dict(class_to_tokens),
        'forbidden_middle_pairs': forbidden_middle_pairs,
        'middle_to_classes': dict(middle_to_classes),
        'morph': morph,
        'token_freq': token_freq,
    }
    return params


# ── Forbidden Pair Construction ──────────────────────────────────────

def build_symmetric_forbidden(params):
    """Build symmetric forbidden class pairs via C1025-MIDDLE expansion + C1034 symmetrization."""
    morph = params['morph']
    class_to_tokens = params['class_to_tokens']
    forbidden_middle_pairs = params['forbidden_middle_pairs']

    # C1025-MIDDLE expansion: for each forbidden MIDDLE pair, find all class pairs
    forbidden_cls = set()
    for src_mid, tgt_mid in forbidden_middle_pairs:
        src_classes = set()
        tgt_classes = set()
        for cls, toks in class_to_tokens.items():
            for tok in toks:
                m = morph.extract(tok)
                mid = m.middle if m else tok
                if mid == src_mid:
                    src_classes.add(cls)
                if mid == tgt_mid:
                    tgt_classes.add(cls)
        for sc in src_classes:
            for tc in tgt_classes:
                forbidden_cls.add((sc, tc))

    # C1034 symmetrization: add reverse direction
    symmetric = set()
    for a, b in forbidden_cls:
        symmetric.add((a, b))
        symmetric.add((b, a))

    print(f"  Forbidden class pairs: {len(forbidden_cls)} forward, {len(symmetric)} symmetric")
    return symmetric


# ── Model Builders ───────────────────────────────────────────────────

def build_m2sf_matrix(class_trans, forbidden_pairs):
    """Build M2-SF: global transition matrix + symmetric forbidden suppression."""
    trans = class_trans.copy()
    for src, tgt in forbidden_pairs:
        trans[src - 1, tgt - 1] = 0
    return normalize_rows(trans)


def build_m21_matrices(quintile_trans, forbidden_pairs):
    """Build M2.1: 5 quintile-specific matrices, each with symmetric forbidden suppression."""
    matrices = {}
    zero_row_counts = {}
    for q in range(N_QUINTILES):
        trans = quintile_trans[q].copy()
        for src, tgt in forbidden_pairs:
            trans[src - 1, tgt - 1] = 0
        normed = normalize_rows(trans)
        matrices[q] = normed
        # Diagnostic: count zero rows (classes with no transitions from this quintile)
        zero_rows = int((trans.sum(axis=1) == 0).sum())
        zero_row_counts[q] = zero_rows
    print(f"  Zero-row classes per quintile: {zero_row_counts}")
    return matrices


# ── Generators ───────────────────────────────────────────────────────

def generate_m2sf(params, trans_norm, rng):
    """Generate corpus from M2-SF (global stationary Markov with symmetric forbidden)."""
    corpus = []
    for _ in range(len(params['line_lengths'])):
        length = rng.choice(params['line_lengths'])
        line = []
        cls = rng.choice(N_CLASSES, p=params['opener_probs']) + 1
        for pos in range(length):
            if pos > 0:
                row = trans_norm[cls - 1]
                if row.sum() > 0:
                    cls = rng.choice(N_CLASSES, p=row) + 1
                else:
                    cls = rng.choice(N_CLASSES, p=params['opener_probs']) + 1

            if cls in params['class_token_probs']:
                toks, probs = params['class_token_probs'][cls]
                word = rng.choice(toks, p=probs)
            else:
                word = f'UNK_C{cls}'
            line.append({'word': word, 'cls': cls})
        corpus.append(line)
    return corpus


def generate_m21(params, quintile_matrices, rng):
    """Generate corpus from M2.1 (quintile-conditioned Markov with symmetric forbidden)."""
    corpus = []
    for _ in range(len(params['line_lengths'])):
        length = rng.choice(params['line_lengths'])
        line = []
        cls = rng.choice(N_CLASSES, p=params['opener_probs']) + 1
        for pos in range(length):
            if pos > 0:
                src_q = assign_quintile(pos - 1, length)
                row = quintile_matrices[src_q][cls - 1]
                if row.sum() > 0:
                    cls = rng.choice(N_CLASSES, p=row) + 1
                else:
                    cls = rng.choice(N_CLASSES, p=params['opener_probs']) + 1

            if cls in params['class_token_probs']:
                toks, probs = params['class_token_probs'][cls]
                word = rng.choice(toks, p=probs)
            else:
                word = f'UNK_C{cls}'
            line.append({'word': word, 'cls': cls})
        corpus.append(line)
    return corpus


# ── Position Data Pre-computation ────────────────────────────────────

def compute_real_pos_data(params):
    """Pre-compute real corpus positional distributions for P-metrics."""
    lines = params['lines']

    # Per-quintile class distributions
    quintile_class = {q: np.zeros(N_CLASSES) for q in range(N_QUINTILES)}
    # Per-quintile transition matrices (flattened for JSD)
    quintile_trans_flat = {q: np.zeros((N_CLASSES, N_CLASSES)) for q in range(N_QUINTILES)}
    # Class -> list of quintile assignments
    class_positions = defaultdict(list)

    for line in lines:
        line_len = len(line)
        for i, tok in enumerate(line):
            q = assign_quintile(i, line_len)
            cls = tok['cls']
            quintile_class[q][cls - 1] += 1
            class_positions[cls].append(q)
            if i < line_len - 1:
                cls2 = line[i + 1]['cls']
                quintile_trans_flat[q][cls - 1, cls2 - 1] += 1

    # Normalize quintile class distributions
    quintile_class_norm = {}
    for q in range(N_QUINTILES):
        total = quintile_class[q].sum()
        quintile_class_norm[q] = quintile_class[q] / max(total, 1)

    # Normalize and flatten quintile transition matrices
    quintile_trans_norm = {}
    for q in range(N_QUINTILES):
        flat = quintile_trans_flat[q].flatten()
        total = flat.sum()
        quintile_trans_norm[q] = flat / max(total, 1)

    # Specialist classes: those with >30% concentration in one quintile (C1358)
    specialist_info = []
    for cls in range(1, N_CLASSES + 1):
        positions = class_positions.get(cls, [])
        if len(positions) < 20:
            continue
        q_counts = Counter(positions)
        total = len(positions)
        for q in range(N_QUINTILES):
            frac = q_counts.get(q, 0) / total
            if frac > 0.30:
                specialist_info.append((cls, q, frac))
                break  # only record peak quintile

    print(f"  Specialist classes (>30% in one quintile): {len(specialist_info)}")

    return {
        'quintile_class_norm': quintile_class_norm,
        'quintile_trans_norm': quintile_trans_norm,
        'specialist_info': specialist_info,
        'class_positions': dict(class_positions),
    }


# ── Metric Computation ───────────────────────────────────────────────

def compute_metrics(corpus, params, real_pos_data):
    """Compute all 18 metrics from a generated corpus."""
    morph = params['morph']
    all_tokens = [t for line in corpus for t in line]
    n_tokens = len(all_tokens)
    if n_tokens == 0:
        return {}

    real_tokens = params['all_tokens']

    # ── A: Distributional ────────────────────────────

    # A1: Class distribution KL
    real_class_dist = np.zeros(N_CLASSES)
    for t in real_tokens:
        real_class_dist[t['cls'] - 1] += 1
    real_class_dist = real_class_dist / max(real_class_dist.sum(), 1)

    gen_class_dist = np.zeros(N_CLASSES)
    for t in all_tokens:
        if 1 <= t['cls'] <= N_CLASSES:
            gen_class_dist[t['cls'] - 1] += 1
    gen_class_dist = gen_class_dist / max(gen_class_dist.sum(), 1)

    real_s = real_class_dist + 1e-10
    gen_s = gen_class_dist + 1e-10
    real_s /= real_s.sum()
    gen_s /= gen_s.sum()
    a1_kl = float(scipy_entropy(gen_s, real_s, base=2))

    # A2: Hapax rate
    word_counts = Counter(t['word'] for t in all_tokens)
    real_word_counts = Counter(t['word'] for t in real_tokens)
    a2_hapax = sum(1 for c in word_counts.values() if c == 1) / max(len(word_counts), 1)
    real_a2 = sum(1 for c in real_word_counts.values() if c == 1) / max(len(real_word_counts), 1)

    # A3: Active class count
    a3_active = len(set(t['cls'] for t in all_tokens if 1 <= t['cls'] <= N_CLASSES))
    real_a3 = len(set(t['cls'] for t in real_tokens if 1 <= t['cls'] <= N_CLASSES))

    # A4: Token type count
    a4_types = len(word_counts)
    real_a4 = len(real_word_counts)

    # ── B: Sequential ────────────────────────────────

    # B1: Spectral gap of 6-state transition matrix
    state_trans = np.zeros((6, 6))
    for line in corpus:
        for i in range(len(line) - 1):
            s1 = STATE_IDX.get(CLASS_TO_STATE.get(line[i]['cls']))
            s2 = STATE_IDX.get(CLASS_TO_STATE.get(line[i + 1]['cls']))
            if s1 is not None and s2 is not None:
                state_trans[s1, s2] += 1
    st_norm = normalize_rows(state_trans)
    eigenvalues = np.sort(np.abs(np.linalg.eigvals(st_norm)))[::-1]
    b1_spectral = float(1.0 - eigenvalues[1]) if len(eigenvalues) > 1 else 1.0

    # Real B1
    real_state_trans = np.zeros((6, 6))
    for line in params['lines']:
        for i in range(len(line) - 1):
            s1 = STATE_IDX.get(line[i]['state'])
            s2 = STATE_IDX.get(line[i + 1]['state'])
            if s1 is not None and s2 is not None:
                real_state_trans[s1, s2] += 1
    real_st_norm = normalize_rows(real_state_trans)
    real_eig = np.sort(np.abs(np.linalg.eigvals(real_st_norm)))[::-1]
    real_b1 = float(1.0 - real_eig[1]) if len(real_eig) > 1 else 1.0

    # B2: AXM self-transition rate
    axm_idx = STATE_IDX['AXM']
    axm_row_sum = state_trans[axm_idx].sum()
    b2_axm_self = float(state_trans[axm_idx, axm_idx] / max(axm_row_sum, 1))
    real_axm_sum = real_state_trans[axm_idx].sum()
    real_b2 = float(real_state_trans[axm_idx, axm_idx] / max(real_axm_sum, 1))

    # B3: Forbidden MIDDLE pair violations
    b3_forbidden = 0
    for line in corpus:
        for i in range(len(line) - 1):
            m1 = morph.extract(line[i]['word'])
            m2 = morph.extract(line[i + 1]['word'])
            mid1 = m1.middle if m1 else line[i]['word']
            mid2 = m2.middle if m2 else line[i + 1]['word']
            if (mid1, mid2) in params['forbidden_middle_pairs']:
                b3_forbidden += 1

    # B4: Role self-transition rank order (FQ > FL > EN)
    role_self = {}
    for role_name, role_classes in ROLE_CLASSES.items():
        self_count = 0
        total_count = 0
        for line in corpus:
            for i in range(len(line) - 1):
                if line[i]['cls'] in role_classes:
                    total_count += 1
                    if line[i + 1]['cls'] in role_classes:
                        self_count += 1
        role_self[role_name] = self_count / max(total_count, 1)
    b4_rank_ok = (role_self.get('FQ', 0) > role_self.get('FL', 0) > role_self.get('EN', 0))

    # B5: Forward-backward bigram JSD
    fwd_matrix = np.zeros((N_CLASSES, N_CLASSES))
    rev_matrix = np.zeros((N_CLASSES, N_CLASSES))
    for line in corpus:
        seq = [t['cls'] for t in line]
        for i in range(len(seq) - 1):
            fwd_matrix[seq[i] - 1, seq[i + 1] - 1] += 1
        rev_seq = list(reversed(seq))
        for i in range(len(rev_seq) - 1):
            rev_matrix[rev_seq[i] - 1, rev_seq[i + 1] - 1] += 1
    fwd_flat = fwd_matrix.flatten() + 1e-12
    rev_flat = rev_matrix.flatten() + 1e-12
    fwd_flat /= fwd_flat.sum()
    rev_flat /= rev_flat.sum()
    m_flat = 0.5 * (fwd_flat + rev_flat)
    b5_jsd = float(0.5 * scipy_entropy(fwd_flat, m_flat, base=2) +
                    0.5 * scipy_entropy(rev_flat, m_flat, base=2))

    # Real B5
    real_fwd = np.zeros((N_CLASSES, N_CLASSES))
    real_rev = np.zeros((N_CLASSES, N_CLASSES))
    for line in params['lines']:
        seq = [t['cls'] for t in line]
        for i in range(len(seq) - 1):
            real_fwd[seq[i] - 1, seq[i + 1] - 1] += 1
        rev_seq = list(reversed(seq))
        for i in range(len(rev_seq) - 1):
            real_rev[rev_seq[i] - 1, rev_seq[i + 1] - 1] += 1
    rf = real_fwd.flatten() + 1e-12
    rr = real_rev.flatten() + 1e-12
    rf /= rf.sum()
    rr /= rr.sum()
    rm = 0.5 * (rf + rr)
    real_b5 = float(0.5 * scipy_entropy(rf, rm, base=2) + 0.5 * scipy_entropy(rr, rm, base=2))

    # ── C: Morphological ─────────────────────────────

    suffix_count = 0
    cc_suffix_violations = 0
    cc_total = 0
    for t in all_tokens:
        mx = morph.extract(t['word'])
        sfx = mx.suffix if mx else None
        if sfx:
            suffix_count += 1
        role = CLASS_TO_ROLE.get(t['cls'], 'UNK')
        if role == 'CC':
            cc_total += 1
            if sfx:
                cc_suffix_violations += 1
    c1_suffix_rate = suffix_count / max(n_tokens, 1)
    c2_cc_suffix_free = 1.0 - (cc_suffix_violations / max(cc_total, 1))

    # Real C1, C2
    real_sfx_count = 0
    real_cc_viol = 0
    real_cc_total = 0
    for t in real_tokens:
        sfx = t['suffix']
        if sfx:
            real_sfx_count += 1
        if t['role'] == 'CC':
            real_cc_total += 1
            if sfx:
                real_cc_viol += 1
    real_c1 = real_sfx_count / max(len(real_tokens), 1)
    real_c2 = 1.0 - (real_cc_viol / max(real_cc_total, 1))

    # C3: PREFIX entropy reduction
    by_prefix = defaultdict(Counter)
    state_counts = Counter()
    for t in all_tokens:
        mx = morph.extract(t['word'])
        pfx = mx.prefix if mx else None
        pfx = pfx if pfx else '(bare)'
        state = CLASS_TO_STATE.get(t['cls'], 'UNK')
        by_prefix[pfx][state] += 1
        state_counts[state] += 1
    total = sum(state_counts.values())
    h_marginal = scipy_entropy([state_counts.get(s, 0) / total for s in STATE_ORDER
                                 if state_counts.get(s, 0) > 0], base=2)
    h_cond = 0
    for pfx, counts in by_prefix.items():
        pfx_total = sum(counts.values())
        probs = [counts.get(s, 0) / pfx_total for s in STATE_ORDER if counts.get(s, 0) > 0]
        h_cond += (pfx_total / total) * scipy_entropy(probs, base=2)
    c3_entropy_red = (h_marginal - h_cond) / max(h_marginal, 1e-10)

    # Real C3
    real_by_prefix = defaultdict(Counter)
    real_state_counts = Counter()
    for t in real_tokens:
        pfx = t['prefix'] if t['prefix'] else '(bare)'
        real_by_prefix[pfx][t['state']] += 1
        real_state_counts[t['state']] += 1
    real_total = sum(real_state_counts.values())
    real_h_marg = scipy_entropy([real_state_counts.get(s, 0) / real_total for s in STATE_ORDER
                                  if real_state_counts.get(s, 0) > 0], base=2)
    real_h_cond = 0
    for pfx, counts in real_by_prefix.items():
        pfx_total = sum(counts.values())
        probs = [counts.get(s, 0) / pfx_total for s in STATE_ORDER if counts.get(s, 0) > 0]
        real_h_cond += (pfx_total / real_total) * scipy_entropy(probs, base=2)
    real_c3 = (real_h_marg - real_h_cond) / max(real_h_marg, 1e-10)

    # ── D: Structural ────────────────────────────────

    # D1: Macro-state stationary distribution
    stat_counts = Counter(CLASS_TO_STATE.get(t['cls'], 'UNK') for t in all_tokens)
    stat_total = sum(stat_counts.values())
    d1_stationary = {s: stat_counts.get(s, 0) / stat_total for s in STATE_ORDER}

    real_stat = Counter(t['state'] for t in real_tokens)
    real_stat_total = sum(real_stat.values())
    real_d1 = {s: real_stat.get(s, 0) / real_stat_total for s in STATE_ORDER}

    # D2: AXM mean dwell
    dwell_lengths = []
    for line in corpus:
        current_run = 0
        for t in line:
            if CLASS_TO_STATE.get(t['cls']) == 'AXM':
                current_run += 1
            else:
                if current_run > 0:
                    dwell_lengths.append(current_run)
                current_run = 0
        if current_run > 0:
            dwell_lengths.append(current_run)
    d2_dwell = float(np.mean(dwell_lengths)) if dwell_lengths else 0

    real_dwell = []
    for line in params['lines']:
        run = 0
        for t in line:
            if t['state'] == 'AXM':
                run += 1
            else:
                if run > 0:
                    real_dwell.append(run)
                run = 0
        if run > 0:
            real_dwell.append(run)
    real_d2 = float(np.mean(real_dwell)) if real_dwell else 0

    # D3: Cross-line mutual information
    cross_pairs = []
    for i in range(len(corpus) - 1):
        if corpus[i] and corpus[i + 1]:
            cross_pairs.append((corpus[i][-1]['cls'], corpus[i + 1][0]['cls']))
    if len(cross_pairs) > 10:
        xy_counts = Counter(cross_pairs)
        x_counts = Counter(p[0] for p in cross_pairs)
        y_counts = Counter(p[1] for p in cross_pairs)
        n_pairs = len(cross_pairs)
        d3_mi = 0.0
        for (x, y), count in xy_counts.items():
            p_xy = count / n_pairs
            p_x = x_counts[x] / n_pairs
            p_y = y_counts[y] / n_pairs
            if p_xy > 0 and p_x > 0 and p_y > 0:
                d3_mi += p_xy * math.log2(p_xy / (p_x * p_y))
    else:
        d3_mi = 0.0

    real_cross = []
    for i in range(len(params['lines']) - 1):
        if params['lines'][i] and params['lines'][i + 1]:
            real_cross.append((params['lines'][i][-1]['cls'], params['lines'][i + 1][0]['cls']))
    if len(real_cross) > 10:
        rxy = Counter(real_cross)
        rx = Counter(p[0] for p in real_cross)
        ry = Counter(p[1] for p in real_cross)
        rn = len(real_cross)
        real_d3 = 0.0
        for (x, y), count in rxy.items():
            p_xy = count / rn
            p_x = rx[x] / rn
            p_y = ry[y] / rn
            if p_xy > 0 and p_x > 0 and p_y > 0:
                real_d3 += p_xy * math.log2(p_xy / (p_x * p_y))
    else:
        real_d3 = 0.0

    # ── P: Positional ────────────────────────────────

    # Build generated corpus positional structures
    gen_quintile_class = {q: np.zeros(N_CLASSES) for q in range(N_QUINTILES)}
    gen_quintile_trans = {q: np.zeros((N_CLASSES, N_CLASSES)) for q in range(N_QUINTILES)}
    gen_class_positions = defaultdict(list)

    for line in corpus:
        line_len = len(line)
        for i, tok in enumerate(line):
            q = assign_quintile(i, line_len)
            cls = tok['cls']
            gen_quintile_class[q][cls - 1] += 1
            gen_class_positions[cls].append(q)
            if i < line_len - 1:
                cls2 = line[i + 1]['cls']
                gen_quintile_trans[q][cls - 1, cls2 - 1] += 1

    # P1: Mean per-quintile class KL divergence
    p1_kls = []
    for q in range(N_QUINTILES):
        gen_dist = gen_quintile_class[q] + 1e-10
        gen_dist /= gen_dist.sum()
        real_dist = real_pos_data['quintile_class_norm'][q] + 1e-10
        real_dist /= real_dist.sum()
        p1_kls.append(float(scipy_entropy(gen_dist, real_dist, base=2)))
    p1_mean_kl = float(np.mean(p1_kls))

    # P2: Mean per-quintile transition JSD
    p2_jsds = []
    for q in range(N_QUINTILES):
        gen_flat = gen_quintile_trans[q].flatten() + 1e-12
        gen_flat /= gen_flat.sum()
        real_flat = real_pos_data['quintile_trans_norm'][q] + 1e-12
        real_flat /= real_flat.sum()
        m_dist = 0.5 * (gen_flat + real_flat)
        jsd_val = float(0.5 * scipy_entropy(gen_flat, m_dist, base=2) +
                        0.5 * scipy_entropy(real_flat, m_dist, base=2))
        p2_jsds.append(jsd_val)
    p2_mean_jsd = float(np.mean(p2_jsds))

    # P3: Specialist class positional accuracy
    p3_errors = []
    for cls, peak_q, real_peak_frac in real_pos_data['specialist_info']:
        gen_positions = gen_class_positions.get(cls, [])
        if len(gen_positions) < 5:
            continue
        gen_q_counts = Counter(gen_positions)
        gen_total = len(gen_positions)
        gen_peak_frac = gen_q_counts.get(peak_q, 0) / gen_total
        p3_errors.append(abs(real_peak_frac - gen_peak_frac))
    p3_mean_error = float(np.mean(p3_errors)) if p3_errors else 1.0

    # ── Hallucination tracking ────────────────────────
    real_vocab = set(t['word'] for t in real_tokens)
    novel_count = sum(1 for t in all_tokens if t['word'] not in real_vocab and not t['word'].startswith('UNK'))
    hallucination_rate = novel_count / max(n_tokens, 1)

    metrics = {
        'A1_class_kl': a1_kl,
        'A2_hapax_rate': a2_hapax,
        'A3_active_classes': a3_active,
        'A4_type_count': a4_types,
        'B1_spectral_gap': b1_spectral,
        'B2_axm_self': b2_axm_self,
        'B3_forbidden': b3_forbidden,
        'B4_role_rank': b4_rank_ok,
        'B5_fwd_rev_jsd': b5_jsd,
        'C1_suffix_rate': c1_suffix_rate,
        'C2_cc_suffix_free': c2_cc_suffix_free,
        'C3_prefix_entropy_red': c3_entropy_red,
        'D1_stationary': d1_stationary,
        'D2_axm_dwell': d2_dwell,
        'D3_cross_line_mi': d3_mi,
        'P1_quintile_class_kl': p1_mean_kl,
        'P2_quintile_trans_jsd': p2_mean_jsd,
        'P3_specialist_accuracy': p3_mean_error,
        'hallucination_rate': hallucination_rate,
    }

    real_metrics = {
        'A2_hapax_rate': real_a2,
        'A3_active_classes': real_a3,
        'A4_type_count': real_a4,
        'B1_spectral_gap': real_b1,
        'B2_axm_self': real_b2,
        'B5_fwd_rev_jsd': real_b5,
        'C1_suffix_rate': real_c1,
        'C2_cc_suffix_free': real_c2,
        'C3_prefix_entropy_red': real_c3,
        'D1_stationary': real_d1,
        'D2_axm_dwell': real_d2,
        'D3_cross_line_mi': real_d3,
    }

    return metrics, real_metrics


# ── Evaluation ───────────────────────────────────────────────────────

def evaluate_tests(metrics, real_metrics, p_thresholds):
    """Evaluate 18 pass/fail tests."""
    results = {}

    # A1: KL < 0.05
    results['A1'] = metrics['A1_class_kl'] < 0.05

    # A2: Hapax within 5pp
    results['A2'] = abs(metrics['A2_hapax_rate'] - real_metrics['A2_hapax_rate']) < 0.05

    # A3: Active classes within +/-3
    results['A3'] = abs(metrics['A3_active_classes'] - real_metrics['A3_active_classes']) <= 3

    # A4: Types within 20%
    real_types = real_metrics['A4_type_count']
    results['A4'] = abs(metrics['A4_type_count'] - real_types) / max(real_types, 1) < 0.20

    # B1: Spectral gap within 0.05
    results['B1'] = abs(metrics['B1_spectral_gap'] - real_metrics['B1_spectral_gap']) < 0.05

    # B2: AXM self within 0.03
    results['B2'] = abs(metrics['B2_axm_self'] - real_metrics['B2_axm_self']) < 0.03

    # B3: Zero forbidden violations
    results['B3'] = metrics['B3_forbidden'] == 0

    # B4: Role rank order preserved
    results['B4'] = bool(metrics['B4_role_rank'])

    # B5: JSD within 50% of real
    real_jsd = real_metrics['B5_fwd_rev_jsd']
    results['B5'] = abs(metrics['B5_fwd_rev_jsd'] - real_jsd) / max(real_jsd, 1e-6) < 0.50

    # C1: Suffix rate within 3pp
    results['C1'] = abs(metrics['C1_suffix_rate'] - real_metrics['C1_suffix_rate']) < 0.03

    # C2: CC suffix-free >= 99%
    results['C2'] = metrics['C2_cc_suffix_free'] >= 0.99

    # C3: PREFIX entropy reduction within 10pp
    results['C3'] = abs(metrics['C3_prefix_entropy_red'] - real_metrics['C3_prefix_entropy_red']) < 0.10

    # D1: Max stationary deviation < 0.03
    max_dev = max(abs(metrics['D1_stationary'].get(s, 0) - real_metrics['D1_stationary'].get(s, 0))
                  for s in STATE_ORDER)
    results['D1'] = max_dev < 0.03

    # D2: AXM dwell within 0.5
    results['D2'] = abs(metrics['D2_axm_dwell'] - real_metrics['D2_axm_dwell']) < 0.5

    # D3: Cross-line MI within 0.15
    results['D3'] = abs(metrics['D3_cross_line_mi'] - real_metrics['D3_cross_line_mi']) < 0.15

    # P1: Quintile class KL < dynamic threshold
    results['P1'] = metrics['P1_quintile_class_kl'] < p_thresholds['P1']

    # P2: Quintile transition JSD < dynamic threshold
    results['P2'] = metrics['P2_quintile_trans_jsd'] < p_thresholds['P2']

    # P3: Specialist accuracy < dynamic threshold
    results['P3'] = metrics['P3_specialist_accuracy'] < p_thresholds['P3']

    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 60)
    print("Phase 476: M2.1 — Position-Conditioned Generation")
    print("=" * 60)

    params = load_data()

    # Build forbidden pairs (symmetric)
    print("\nBuilding symmetric forbidden class pairs...")
    forbidden_pairs = build_symmetric_forbidden(params)

    # Build M2-SF transition matrix
    print("\nBuilding M2-SF baseline...")
    m2sf_matrix = build_m2sf_matrix(params['class_trans'], forbidden_pairs)

    # Build M2.1 quintile matrices
    print("\nBuilding M2.1 quintile-conditioned matrices...")
    m21_matrices = build_m21_matrices(params['quintile_trans'], forbidden_pairs)

    # Pre-compute real positional data
    print("\nComputing real corpus positional data...")
    real_pos_data = compute_real_pos_data(params)

    # ── Run M2-SF first to establish P-metric baselines ──

    print("\n" + "-" * 60)
    print("Phase 1: M2-SF baseline (1 calibration run)")
    print("-" * 60)

    calib_rng = np.random.RandomState(SEED)
    calib_corpus = generate_m2sf(params, m2sf_matrix, calib_rng)
    calib_metrics, real_metrics = compute_metrics(calib_corpus, params, real_pos_data)

    # Dynamic P-thresholds: half of M2-SF baseline error
    p_thresholds = {
        'P1': max(calib_metrics['P1_quintile_class_kl'] * 0.5, 0.005),
        'P2': max(calib_metrics['P2_quintile_trans_jsd'] * 0.5, 0.005),
        'P3': max(calib_metrics['P3_specialist_accuracy'] * 0.5, 0.005),
    }
    print(f"\n  M2-SF calibration P-metrics:")
    print(f"    P1 (quintile class KL):   {calib_metrics['P1_quintile_class_kl']:.6f}  -> threshold: {p_thresholds['P1']:.6f}")
    print(f"    P2 (quintile trans JSD):  {calib_metrics['P2_quintile_trans_jsd']:.6f}  -> threshold: {p_thresholds['P2']:.6f}")
    print(f"    P3 (specialist accuracy): {calib_metrics['P3_specialist_accuracy']:.6f}  -> threshold: {p_thresholds['P3']:.6f}")

    # ── Multi-run evaluation ──

    model_results = {}
    for model_name, gen_fn, gen_args in [
        ('M2-SF', generate_m2sf, (params, m2sf_matrix)),
        ('M2.1',  generate_m21,  (params, m21_matrices)),
    ]:
        print(f"\n{'=' * 60}")
        print(f"Evaluating {model_name} ({N_RUNS} runs)")
        print(f"{'=' * 60}")

        run_metrics_list = []
        run_tests_list = []
        run_real_metrics = None

        for run in range(N_RUNS):
            rng = np.random.RandomState(SEED + run * 1000 + (0 if model_name == 'M2-SF' else 50000))
            corpus = gen_fn(*gen_args, rng)
            metrics, rm = compute_metrics(corpus, params, real_pos_data)
            if run_real_metrics is None:
                run_real_metrics = rm
            tests = evaluate_tests(metrics, rm, p_thresholds)
            run_metrics_list.append(metrics)
            run_tests_list.append(tests)
            pass_count = sum(1 for v in tests.values() if v)
            print(f"  Run {run+1:2d}: {pass_count}/18 pass")

        # Aggregate
        all_test_names = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B5',
                          'C1', 'C2', 'C3', 'D1', 'D2', 'D3', 'P1', 'P2', 'P3']

        per_test_pass_rate = {}
        for test in all_test_names:
            per_test_pass_rate[test] = sum(1 for r in run_tests_list if r.get(test, False)) / N_RUNS

        # Per-run total pass counts
        run_pass_counts = [sum(1 for v in r.values() if v) for r in run_tests_list]
        mean_pass = float(np.mean(run_pass_counts))
        std_pass = float(np.std(run_pass_counts))

        # Per-metric means and stds
        scalar_metrics = ['A1_class_kl', 'A2_hapax_rate', 'A3_active_classes', 'A4_type_count',
                          'B1_spectral_gap', 'B2_axm_self', 'B3_forbidden', 'B5_fwd_rev_jsd',
                          'C1_suffix_rate', 'C2_cc_suffix_free', 'C3_prefix_entropy_red',
                          'D2_axm_dwell', 'D3_cross_line_mi',
                          'P1_quintile_class_kl', 'P2_quintile_trans_jsd', 'P3_specialist_accuracy',
                          'hallucination_rate']
        metric_stats = {}
        for m_name in scalar_metrics:
            vals = [r[m_name] for r in run_metrics_list if m_name in r]
            if vals:
                metric_stats[m_name] = {
                    'mean': float(np.mean(vals)),
                    'std': float(np.std(vals)),
                }

        model_results[model_name] = {
            'mean_pass': mean_pass,
            'std_pass': std_pass,
            'per_test_pass_rate': per_test_pass_rate,
            'metric_stats': metric_stats,
        }

        print(f"\n  {model_name} Summary: {mean_pass:.1f} +/- {std_pass:.1f} / 18")
        for test in all_test_names:
            rate = per_test_pass_rate[test]
            marker = 'PASS' if rate >= 0.5 else 'FAIL'
            print(f"    {test}: {rate*100:.0f}% ({marker})")

    # ── Comparison ──

    print(f"\n{'=' * 60}")
    print("COMPARISON: M2-SF vs M2.1")
    print(f"{'=' * 60}")

    m2sf_pass = model_results['M2-SF']['per_test_pass_rate']
    m21_pass = model_results['M2.1']['per_test_pass_rate']
    all_test_names = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B5',
                      'C1', 'C2', 'C3', 'D1', 'D2', 'D3', 'P1', 'P2', 'P3']

    tests_gained = sum(1 for t in all_test_names if m21_pass.get(t, 0) >= 0.5 and m2sf_pass.get(t, 0) < 0.5)
    tests_lost = sum(1 for t in all_test_names if m21_pass.get(t, 0) < 0.5 and m2sf_pass.get(t, 0) >= 0.5)
    m2sf_total_pass = sum(1 for t in all_test_names if m2sf_pass.get(t, 0) >= 0.5)
    m21_total_pass = sum(1 for t in all_test_names if m21_pass.get(t, 0) >= 0.5)

    print(f"\n  M2-SF: {m2sf_total_pass}/18 tests pass (>=50% across runs)")
    print(f"  M2.1:  {m21_total_pass}/18 tests pass")
    print(f"  Gained: {tests_gained}, Lost: {tests_lost}, Net: +{tests_gained - tests_lost}")

    # P-metric comparison
    print("\n  Position metrics:")
    for pm in ['P1_quintile_class_kl', 'P2_quintile_trans_jsd', 'P3_specialist_accuracy']:
        m2sf_val = model_results['M2-SF']['metric_stats'].get(pm, {}).get('mean', 'N/A')
        m21_val = model_results['M2.1']['metric_stats'].get(pm, {}).get('mean', 'N/A')
        if isinstance(m2sf_val, float) and isinstance(m21_val, float) and m21_val > 0:
            ratio = m2sf_val / m21_val
            print(f"    {pm}: M2-SF={m2sf_val:.6f}, M2.1={m21_val:.6f} ({ratio:.1f}x improvement)")
        else:
            print(f"    {pm}: M2-SF={m2sf_val}, M2.1={m21_val}")

    # Verdict
    if m21_total_pass == 18 and tests_lost == 0:
        verdict = "M2.1 FULL PASS (18/18, no regressions)"
    elif tests_lost == 0 and m21_total_pass > m2sf_total_pass:
        verdict = f"M2.1 IMPROVEMENT ({m21_total_pass}/18 vs M2-SF {m2sf_total_pass}/18, no regressions)"
    elif tests_lost > 0:
        lost_tests = [t for t in all_test_names if m21_pass.get(t, 0) < 0.5 and m2sf_pass.get(t, 0) >= 0.5]
        verdict = f"M2.1 REGRESSION on {lost_tests} (gained {tests_gained}, lost {tests_lost})"
    else:
        verdict = f"M2.1 NO CHANGE ({m21_total_pass}/18 = M2-SF {m2sf_total_pass}/18)"

    print(f"\n  VERDICT: {verdict}")

    # ── Save results ──

    output = {
        'metadata': {
            'phase': 476,
            'name': 'POSITION_CONDITIONED_GENERATION',
            'n_runs': N_RUNS,
            'n_tests': 18,
            'seed': SEED,
            'forbidden_mapping': 'C1025-MIDDLE-symmetric',
            'n_forbidden_class_pairs': len(forbidden_pairs),
            'quintile_function': 'min(4, int(idx / line_len * 5))',
            'n_tokens_real': len(params['all_tokens']),
            'n_lines_real': len(params['lines']),
        },
        'real_metrics': round_floats(real_metrics),
        'p_thresholds': round_floats(p_thresholds),
        'models': round_floats(model_results),
        'comparison': {
            'm2sf_pass_count': m2sf_total_pass,
            'm21_pass_count': m21_total_pass,
            'tests_gained': tests_gained,
            'tests_lost': tests_lost,
            'net_improvement': tests_gained - tests_lost,
        },
        'verdict': verdict,
        'elapsed_seconds': round(time.time() - t0, 1),
    }

    out_path = RESULTS_DIR / 'position_conditioned_generation.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(output), f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == '__main__':
    main()
