#!/usr/bin/env python3
"""
Phase 348: GENERATIVE_SUFFICIENCY
===================================
Tests whether proven structural mechanisms can regenerate realistic
Currier B text. 5 generative models (M0-M4) of increasing complexity,
each tested against 15 structural metrics. The sufficiency frontier
is the simplest model passing >= 80% of tests.

Models:
  M0: Token frequency only (i.i.d.)
  M1: 49-class first-order Markov
  M2: M1 + forbidden MIDDLE pair suppression
  M3: 6-state macro Markov + class emission
  M4: PREFIX-routed compositional generation

Depends on: C1023, C1024, C978, C1015, C109, C267, C121, C886
"""

import json
import sys
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants ────────────────────────────────────────────────────────

MACRO_STATE_PARTITION = {
    'AXM':     {1,2,4,6,8,15,16,17,20,21,22,24,25,26,27,28,29,31,32,33,34,35,36,37,39,41,43,44,46,47,48,49},
    'AXm':     {3,5,18,19,42,45},
    'FL_HAZ':  {7,30},
    'FQ':      {9,13,14,23},
    'CC':      {10,11,12},
    'FL_SAFE': {38,40},
}
CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state
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
for role, classes in ROLE_CLASSES.items():
    for c in classes:
        CLASS_TO_ROLE[c] = role

N_INST = 20  # Instantiations per model
N_CLASSES = 49


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load all data needed for generation and testing."""
    print("Loading data...")

    # Token → class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}
    class_to_tokens = defaultdict(list)
    for tok, cls in token_to_class.items():
        class_to_tokens[cls].append(tok)

    # Forbidden MIDDLE pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    morph = Morphology()

    # Build real token stream organized by line
    lines = []  # list of lists of token dicts
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
            'folio': token.folio,
            'line': token.line,
        })
    if current_line:
        lines.append(current_line)

    # Flatten for statistics
    all_tokens = [t for line in lines for t in line]
    print(f"  {len(all_tokens)} tokens in {len(lines)} lines")

    # ── Build generation parameters ──────────────────────────

    # Token frequencies (M0)
    token_freq = Counter(t['word'] for t in all_tokens)
    tokens_list = list(token_freq.keys())
    token_probs = np.array([token_freq[t] for t in tokens_list], dtype=float)
    token_probs /= token_probs.sum()

    # Class transition matrix (M1)
    class_trans = np.zeros((N_CLASSES, N_CLASSES))
    for line in lines:
        for i in range(len(line) - 1):
            class_trans[line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

    # Opener class distribution
    opener_counts = Counter(line[0]['cls'] for line in lines if line)
    opener_probs = np.zeros(N_CLASSES)
    for cls, count in opener_counts.items():
        opener_probs[cls - 1] = count
    opener_probs /= max(opener_probs.sum(), 1)

    # Line lengths
    line_lengths = [len(line) for line in lines]

    # Class → token sampling distribution
    class_token_probs = {}
    for cls in range(1, N_CLASSES + 1):
        toks = class_to_tokens.get(cls, [])
        if toks:
            counts = [token_freq.get(t, 0) for t in toks]
            total = sum(counts)
            if total > 0:
                class_token_probs[cls] = (toks, np.array(counts, dtype=float) / total)

    # 6-state transition matrix (M3)
    state_trans = np.zeros((6, 6))
    for line in lines:
        for i in range(len(line) - 1):
            s1 = STATE_IDX.get(line[i]['state'])
            s2 = STATE_IDX.get(line[i + 1]['state'])
            if s1 is not None and s2 is not None:
                state_trans[s1, s2] += 1

    # State opener distribution
    state_opener = np.zeros(6)
    for line in lines:
        if line:
            s = STATE_IDX.get(line[0]['state'])
            if s is not None:
                state_opener[s] += 1
    state_opener /= max(state_opener.sum(), 1)

    # P(class | state) for M3
    class_given_state = np.zeros((6, N_CLASSES))
    for t in all_tokens:
        s = STATE_IDX.get(t['state'])
        if s is not None:
            class_given_state[s, t['cls'] - 1] += 1
    for s in range(6):
        row_sum = class_given_state[s].sum()
        if row_sum > 0:
            class_given_state[s] /= row_sum

    # ── M4 compositional parameters ──────────────────────────

    # P(prefix | state)
    prefix_given_state = defaultdict(Counter)
    for t in all_tokens:
        pfx = t['prefix'] if t['prefix'] else ''
        prefix_given_state[t['state']][pfx] += 1

    prefix_state_samplers = {}
    for state in STATE_ORDER:
        counts = prefix_given_state[state]
        if counts:
            prefixes = list(counts.keys())
            probs = np.array([counts[p] for p in prefixes], dtype=float)
            probs /= probs.sum()
            prefix_state_samplers[state] = (prefixes, probs)

    # P(middle | prefix)
    middle_given_prefix = defaultdict(Counter)
    for t in all_tokens:
        pfx = t['prefix'] if t['prefix'] else ''
        mid = t['middle'] if t['middle'] else ''
        middle_given_prefix[pfx][mid] += 1

    middle_prefix_samplers = {}
    for pfx, counts in middle_given_prefix.items():
        middles = list(counts.keys())
        probs = np.array([counts[m] for m in middles], dtype=float)
        probs /= probs.sum()
        middle_prefix_samplers[pfx] = (middles, probs)

    # P(suffix | middle)
    suffix_given_middle = defaultdict(Counter)
    for t in all_tokens:
        mid = t['middle'] if t['middle'] else ''
        sfx = t['suffix'] if t['suffix'] else ''
        suffix_given_middle[mid][sfx] += 1

    suffix_middle_samplers = {}
    for mid, counts in suffix_given_middle.items():
        suffixes = list(counts.keys())
        probs = np.array([counts[s] for s in suffixes], dtype=float)
        probs /= probs.sum()
        suffix_middle_samplers[mid] = (suffixes, probs)

    # Forbidden MIDDLE pairs (for M2)
    # Map to class pairs: find which classes contain each forbidden MIDDLE
    middle_to_classes = defaultdict(set)
    for t in all_tokens:
        mid = t['middle'] if t['middle'] else ''
        middle_to_classes[mid].add(t['cls'])

    # For token-level forbidden check, keep MIDDLE pairs
    # For M4 compositional: track middle → class mapping
    middle_class_probs = defaultdict(Counter)
    for t in all_tokens:
        mid = t['middle'] if t['middle'] else ''
        middle_class_probs[mid][t['cls']] += 1

    params = {
        'tokens_list': tokens_list,
        'token_probs': token_probs,
        'token_to_class': token_to_class,
        'class_to_tokens': class_to_tokens,
        'class_trans': class_trans,
        'opener_probs': opener_probs,
        'line_lengths': line_lengths,
        'class_token_probs': class_token_probs,
        'state_trans': state_trans,
        'state_opener': state_opener,
        'class_given_state': class_given_state,
        'prefix_state_samplers': prefix_state_samplers,
        'middle_prefix_samplers': middle_prefix_samplers,
        'suffix_middle_samplers': suffix_middle_samplers,
        'middle_class_probs': middle_class_probs,
        'forbidden_middle_pairs': forbidden_middle_pairs,
        'morph': morph,
    }

    return all_tokens, lines, params


# ── Generative Models ────────────────────────────────────────────────

def normalize_rows(m):
    row_sums = m.sum(axis=1, keepdims=True)
    return m / np.maximum(row_sums, 1e-12)


def sample_line_length(params, rng):
    """Sample a line length from empirical distribution."""
    return rng.choice(params['line_lengths'])


def generate_m0(params, rng):
    """M0: i.i.d. token sampling from frequency distribution."""
    corpus = []
    n_target = sum(params['line_lengths'])
    n_lines = len(params['line_lengths'])

    for _ in range(n_lines):
        length = sample_line_length(params, rng)
        line = []
        for _ in range(length):
            word = rng.choice(params['tokens_list'], p=params['token_probs'])
            cls = params['token_to_class'].get(word, 1)
            line.append({'word': word, 'cls': cls})
        corpus.append(line)
    return corpus


def generate_m1(params, rng):
    """M1: 49-class first-order Markov chain."""
    trans = normalize_rows(params['class_trans'].copy())
    corpus = []

    for _ in range(len(params['line_lengths'])):
        length = sample_line_length(params, rng)
        line = []
        # Sample opener
        cls = rng.choice(N_CLASSES, p=params['opener_probs']) + 1  # 1-indexed
        for pos in range(length):
            if pos > 0:
                row = trans[cls - 1]
                if row.sum() > 0:
                    cls = rng.choice(N_CLASSES, p=row) + 1
                else:
                    cls = rng.choice(N_CLASSES, p=params['opener_probs']) + 1

            # Sample token from class
            if cls in params['class_token_probs']:
                toks, probs = params['class_token_probs'][cls]
                word = rng.choice(toks, p=probs)
            else:
                word = f'UNK_C{cls}'
            line.append({'word': word, 'cls': cls})
        corpus.append(line)
    return corpus


def generate_m2(params, rng):
    """M2: M1 + forbidden MIDDLE pair suppression at class level."""
    # Zero out forbidden transitions and renormalize
    trans = params['class_trans'].copy()
    morph = params['morph']

    # For each forbidden MIDDLE pair, find class pairs to suppress
    for src_mid, tgt_mid in params['forbidden_middle_pairs']:
        src_classes = set()
        tgt_classes = set()
        for cls, toks_list in params['class_to_tokens'].items():
            for tok in toks_list:
                m = morph.extract(tok)
                mid = m.middle if m else tok
                if mid == src_mid:
                    src_classes.add(cls)
                if mid == tgt_mid:
                    tgt_classes.add(cls)
        for sc in src_classes:
            for tc in tgt_classes:
                trans[sc - 1, tc - 1] = 0

    trans_norm = normalize_rows(trans)
    corpus = []

    for _ in range(len(params['line_lengths'])):
        length = sample_line_length(params, rng)
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


def generate_m3(params, rng):
    """M3: 6-state macro Markov + class emission + token sampling."""
    state_trans = normalize_rows(params['state_trans'].copy())
    corpus = []

    for _ in range(len(params['line_lengths'])):
        length = sample_line_length(params, rng)
        line = []
        # Sample opener state
        state_idx = rng.choice(6, p=params['state_opener'])

        for pos in range(length):
            if pos > 0:
                row = state_trans[state_idx]
                if row.sum() > 0:
                    state_idx = rng.choice(6, p=row)

            # Sample class from state
            cls_row = params['class_given_state'][state_idx]
            if cls_row.sum() > 0:
                cls = rng.choice(N_CLASSES, p=cls_row) + 1
            else:
                cls = 1

            # Sample token from class
            if cls in params['class_token_probs']:
                toks, probs = params['class_token_probs'][cls]
                word = rng.choice(toks, p=probs)
            else:
                word = f'UNK_C{cls}'
            line.append({'word': word, 'cls': cls})
        corpus.append(line)
    return corpus


def generate_m4(params, rng):
    """M4: PREFIX-routed compositional generation."""
    state_trans = normalize_rows(params['state_trans'].copy())
    morph = params['morph']
    corpus = []

    for _ in range(len(params['line_lengths'])):
        length = sample_line_length(params, rng)
        line = []
        state_idx = rng.choice(6, p=params['state_opener'])

        for pos in range(length):
            if pos > 0:
                row = state_trans[state_idx]
                if row.sum() > 0:
                    state_idx = rng.choice(6, p=row)

            state_name = STATE_ORDER[state_idx]

            # 1. Sample PREFIX from P(prefix | state)
            if state_name in params['prefix_state_samplers']:
                prefixes, probs = params['prefix_state_samplers'][state_name]
                prefix = rng.choice(prefixes, p=probs)
            else:
                prefix = ''

            # 2. Sample MIDDLE from P(middle | prefix)
            if prefix in params['middle_prefix_samplers']:
                middles, probs = params['middle_prefix_samplers'][prefix]
                middle = rng.choice(middles, p=probs)
            else:
                # Fallback: sample from marginal MIDDLE distribution
                all_mid = params['middle_prefix_samplers'].get('', None)
                if all_mid:
                    middles, probs = all_mid
                    middle = rng.choice(middles, p=probs)
                else:
                    middle = 'od'  # most common MIDDLE

            # 3. Sample SUFFIX from P(suffix | middle)
            if middle in params['suffix_middle_samplers']:
                suffixes, probs = params['suffix_middle_samplers'][middle]
                suffix = rng.choice(suffixes, p=probs)
            else:
                suffix = ''

            # 4. Compose word
            word = (prefix or '') + (middle or '') + (suffix or '')
            if not word:
                word = 'daiin'  # fallback

            # 5. Look up class
            cls = params['token_to_class'].get(word)
            if cls is None:
                # Novel token — assign class from most common class for this MIDDLE
                mid_cls = params['middle_class_probs'].get(middle, {})
                if mid_cls:
                    cls = mid_cls.most_common(1)[0][0]
                else:
                    cls = 1  # fallback

            line.append({
                'word': word, 'cls': cls,
                'prefix': prefix, 'middle': middle, 'suffix': suffix,
                '_novel': word not in params['token_to_class'],
            })
        corpus.append(line)
    return corpus


# ── Test Battery ─────────────────────────────────────────────────────

def compute_metrics(corpus, params, morph):
    """Compute all 15 test metrics from a generated corpus."""
    all_tokens = [t for line in corpus for t in line]
    n_tokens = len(all_tokens)
    if n_tokens == 0:
        return {}

    # ── A: Distributional ────────────────────────────────
    # A1: Class distribution KL divergence
    real_class_dist = np.zeros(N_CLASSES)
    for cls in range(1, N_CLASSES + 1):
        real_class_dist[cls - 1] = sum(1 for t in params.get('_real_tokens', []) if t['cls'] == cls)
    real_class_dist = real_class_dist / max(real_class_dist.sum(), 1)

    gen_class_dist = np.zeros(N_CLASSES)
    for t in all_tokens:
        if 1 <= t['cls'] <= N_CLASSES:
            gen_class_dist[t['cls'] - 1] += 1
    gen_class_dist = gen_class_dist / max(gen_class_dist.sum(), 1)

    # KL(gen || real) with smoothing
    real_s = real_class_dist + 1e-10
    gen_s = gen_class_dist + 1e-10
    real_s /= real_s.sum()
    gen_s /= gen_s.sum()
    a1_kl = float(scipy_entropy(gen_s, real_s, base=2))

    # A2: Hapax rate
    word_counts = Counter(t['word'] for t in all_tokens)
    a2_hapax = sum(1 for c in word_counts.values() if c == 1) / max(len(word_counts), 1)

    # A3: Active class count
    a3_active = len(set(t['cls'] for t in all_tokens if 1 <= t['cls'] <= N_CLASSES))

    # A4: Token type count
    a4_types = len(word_counts)

    # ── B: Sequential ────────────────────────────────────
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

    # B2: AXM self-transition rate
    axm_idx = STATE_IDX['AXM']
    axm_row_sum = state_trans[axm_idx].sum()
    b2_axm_self = float(state_trans[axm_idx, axm_idx] / max(axm_row_sum, 1))

    # B3: Forbidden MIDDLE pair violations
    b3_forbidden = 0
    for line in corpus:
        for i in range(len(line) - 1):
            mid1 = line[i].get('middle')
            mid2 = line[i + 1].get('middle')
            if mid1 is None:
                m1 = morph.extract(line[i]['word'])
                mid1 = m1.middle if m1 else line[i]['word']
            if mid2 is None:
                m2 = morph.extract(line[i + 1]['word'])
                mid2 = m2.middle if m2 else line[i + 1]['word']
            if (mid1, mid2) in params['forbidden_middle_pairs']:
                b3_forbidden += 1

    # B4: Self-transition rank order by role (FQ > FL > EN)
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

    # ── C: Morphological ─────────────────────────────────
    # Extract morphology for all tokens
    suffix_count = 0
    cc_suffix_violations = 0
    cc_total = 0

    for t in all_tokens:
        m = t.get('suffix') if 'suffix' in t else None
        if m is None:
            mx = morph.extract(t['word'])
            sfx = mx.suffix if mx else None
        else:
            sfx = t.get('suffix')
        if sfx:
            suffix_count += 1

        role = CLASS_TO_ROLE.get(t['cls'], 'UNK')
        if role == 'CC':
            cc_total += 1
            if sfx:
                cc_suffix_violations += 1

    c1_suffix_rate = suffix_count / max(n_tokens, 1)
    c2_cc_suffix_free = 1.0 - (cc_suffix_violations / max(cc_total, 1))

    # C3: PREFIX entropy reduction for macro-state
    by_prefix = defaultdict(Counter)
    state_counts = Counter()
    for t in all_tokens:
        pfx = t.get('prefix')
        if pfx is None:
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

    # ── D: Structural ────────────────────────────────────
    # D1: Macro-state stationary distribution
    stat_counts = Counter(CLASS_TO_STATE.get(t['cls'], 'UNK') for t in all_tokens)
    stat_total = sum(stat_counts.values())
    d1_stationary = {s: stat_counts.get(s, 0) / stat_total for s in STATE_ORDER}

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

    # D3: Cross-line mutual information
    # MI between last class of line i and first class of line i+1
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
                d3_mi += p_xy * np.log2(p_xy / (p_x * p_y))
        d3_mi = float(d3_mi)
    else:
        d3_mi = 0.0

    # ── Novelty tracking ─────────────────────────────────
    novel_count = sum(1 for t in all_tokens if t.get('_novel', False))
    hallucination_rate = novel_count / max(n_tokens, 1)

    return {
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
        'hallucination_rate': hallucination_rate,
    }


def evaluate_tests(metrics, real_metrics):
    """Evaluate 15 pass/fail tests from computed metrics."""
    results = {}

    # A1: KL < 0.05
    results['A1'] = metrics['A1_class_kl'] < 0.05

    # A2: Hapax within 5pp
    results['A2'] = abs(metrics['A2_hapax_rate'] - real_metrics['A2_hapax_rate']) < 0.05

    # A3: Active classes within ±3
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

    # C2: CC suffix-free = 100%
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

    return results


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 348: GENERATIVE_SUFFICIENCY")
    print("=" * 60)

    all_tokens, lines, params = load_data()
    morph = params['morph']

    # Store real tokens for KL computation
    params['_real_tokens'] = all_tokens

    # Compute real metrics
    print("\n--- Computing real corpus metrics ---")
    real_corpus = lines  # Each line is a list of token dicts
    real_metrics = compute_metrics(real_corpus, params, morph)

    print(f"  A1 class KL (self): {real_metrics['A1_class_kl']:.6f}")
    print(f"  A2 hapax rate: {real_metrics['A2_hapax_rate']:.3f}")
    print(f"  A3 active classes: {real_metrics['A3_active_classes']}")
    print(f"  A4 type count: {real_metrics['A4_type_count']}")
    print(f"  B1 spectral gap: {real_metrics['B1_spectral_gap']:.4f}")
    print(f"  B2 AXM self: {real_metrics['B2_axm_self']:.4f}")
    print(f"  B3 forbidden: {real_metrics['B3_forbidden']}")
    print(f"  B5 fwd-rev JSD: {real_metrics['B5_fwd_rev_jsd']:.6f}")
    print(f"  C1 suffix rate: {real_metrics['C1_suffix_rate']:.3f}")
    print(f"  C3 PREFIX entropy red: {real_metrics['C3_prefix_entropy_red']:.3f}")
    print(f"  D1 stationary: { {s: f'{v:.3f}' for s,v in real_metrics['D1_stationary'].items()} }")
    print(f"  D2 AXM dwell: {real_metrics['D2_axm_dwell']:.2f}")
    print(f"  D3 cross-line MI: {real_metrics['D3_cross_line_mi']:.4f}")

    # ── Run models ───────────────────────────────────────
    generators = {
        'M0': generate_m0,
        'M1': generate_m1,
        'M2': generate_m2,
        'M3': generate_m3,
        'M4': generate_m4,
    }

    all_results = {}
    test_names = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B5',
                  'C1', 'C2', 'C3', 'D1', 'D2', 'D3']

    for model_name, gen_fn in generators.items():
        print(f"\n{'=' * 60}")
        print(f"Model {model_name}: Generating {N_INST} corpora...")
        print("=" * 60)

        inst_metrics = []
        inst_tests = []
        halluc_rates = []

        for inst in range(N_INST):
            rng = np.random.RandomState(42 + inst * 1000 + hash(model_name) % 10000)
            corpus = gen_fn(params, rng)
            metrics = compute_metrics(corpus, params, morph)
            tests = evaluate_tests(metrics, real_metrics)
            inst_metrics.append(metrics)
            inst_tests.append(tests)
            halluc_rates.append(metrics.get('hallucination_rate', 0))

        # Aggregate
        per_test = {}
        for test in test_names:
            pass_rate = sum(1 for t in inst_tests if t.get(test, False)) / N_INST
            per_test[test] = pass_rate

        pass_counts = [sum(t.values()) for t in inst_tests]
        mean_pass = float(np.mean(pass_counts))
        std_pass = float(np.std(pass_counts))
        mean_halluc = float(np.mean(halluc_rates))

        print(f"  Mean tests passed: {mean_pass:.1f} / {len(test_names)} (std={std_pass:.1f})")
        print(f"  Hallucination rate: {mean_halluc:.3f}")
        print(f"  Per-test pass rates:")
        for test in test_names:
            rate = per_test[test]
            mark = 'v' if rate >= 0.5 else 'x'
            print(f"    {test}: {rate:.0%} [{mark}]")

        # Collect key metric means for reporting
        metric_means = {}
        for key in ['A1_class_kl', 'A2_hapax_rate', 'A3_active_classes', 'A4_type_count',
                     'B1_spectral_gap', 'B2_axm_self', 'B3_forbidden', 'B5_fwd_rev_jsd',
                     'C1_suffix_rate', 'C3_prefix_entropy_red', 'D2_axm_dwell', 'D3_cross_line_mi']:
            vals = [m[key] for m in inst_metrics if key in m]
            if vals:
                metric_means[key] = {'mean': float(np.mean(vals)), 'std': float(np.std(vals))}

        all_results[model_name] = {
            'mean_pass': mean_pass,
            'std_pass': std_pass,
            'mean_pass_rate': mean_pass / len(test_names),
            'per_test_pass_rate': per_test,
            'hallucination_rate': mean_halluc,
            'metric_means': metric_means,
        }

    # ── Synthesis ────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("SYNTHESIS")
    print("=" * 60)

    print(f"\n  {'Model':>5} {'Pass':>6} {'Rate':>6} {'Halluc':>7}")
    print(f"  {'-'*30}")
    for model_name in generators:
        r = all_results[model_name]
        print(f"  {model_name:>5} {r['mean_pass']:>5.1f} {r['mean_pass_rate']:>5.0%} {r['hallucination_rate']:>6.1%}")

    # Find sufficiency frontier (first model >= 80% pass rate)
    frontier = None
    for model_name in ['M0', 'M1', 'M2', 'M3', 'M4']:
        if all_results[model_name]['mean_pass_rate'] >= 0.80:
            frontier = model_name
            break

    if frontier:
        print(f"\n  Sufficiency frontier: {frontier} (>= 80% pass rate)")
    else:
        print(f"\n  No model reached 80% pass rate")
        # Find the best
        best = max(all_results, key=lambda m: all_results[m]['mean_pass_rate'])
        print(f"  Best model: {best} ({all_results[best]['mean_pass_rate']:.0%})")

    # Check predictions
    predictions = {}
    p1 = all_results['M0']['mean_pass'] <= 3
    predictions['P1_m0_le3'] = p1
    p2 = 5 <= all_results['M1']['mean_pass'] <= 8
    predictions['P2_m1_5to8'] = p2
    m2_delta = all_results['M2']['mean_pass'] - all_results['M1']['mean_pass']
    p3 = m2_delta <= 1.5
    predictions['P3_m2_delta_le1'] = p3
    p4 = all_results['M4']['mean_pass'] >= 12
    predictions['P4_m4_ge12'] = p4
    p5 = all_results['M4']['mean_pass'] < 15
    predictions['P5_none_perfect'] = p5

    print(f"\n  Pre-registered predictions:")
    for name, result in predictions.items():
        mark = 'PASS' if result else 'FAIL'
        print(f"    {name}: {mark}")

    pred_correct = sum(predictions.values())
    print(f"  Predictions correct: {pred_correct}/5")

    # Determine overall verdict
    if frontier:
        verdict = f"GENERATIVE_SUFFICIENCY_AT_{frontier}"
    else:
        best = max(all_results, key=lambda m: all_results[m]['mean_pass_rate'])
        verdict = f"INSUFFICIENCY_BEST_{best}_{all_results[best]['mean_pass_rate']:.0%}"

    print(f"\n  Overall verdict: {verdict}")

    # ── Save ─────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 348,
            'name': 'GENERATIVE_SUFFICIENCY',
            'n_instantiations': N_INST,
            'n_tests': len(test_names),
            'test_names': test_names,
        },
        'real_metrics': {k: v for k, v in real_metrics.items()
                         if not isinstance(v, np.ndarray)},
        'models': all_results,
        'sufficiency_frontier': frontier,
        'predictions': predictions,
        'predictions_correct': pred_correct,
        'verdict': verdict,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'generative_sufficiency.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == '__main__':
    main()
