#!/usr/bin/env python3
"""
Phase 370: SECTION_SPECIFIC_M2
================================
Capstone validation: does M2 generative sufficiency (C1025) hold per
section independently, or does it only emerge from pooling?

Tests 5 hypotheses:
  H1: Per-section M2 sufficiency (LOCAL train, LOCAL test)
  H2: Global M2 per-section (GLOBAL train, LOCAL test)
  H3: Cross-section transfer (X-train, Y-test) vs C1029 JSD
  H4: Test sensitivity classification (invariant vs section-sensitive)
  H5: No pooling advantage (global - weighted-local <= 1 test)

Depends on: C1025, C1029, C1030, C1047
"""

import json
import sys
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy, spearmanr

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

np.random.seed(42)

# ── Constants (from Phase 348) ──────────────────────────────────────

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

N_INST = 20
N_CLASSES = 49

# C1029 pairwise JSD values
SECTION_JSD = {
    ('B', 'C'): 0.378,
    ('B', 'H'): 0.307,
    ('B', 'S'): 0.238,
    ('C', 'H'): 0.399,
    ('C', 'S'): 0.352,
    ('H', 'S'): 0.273,
}

SECTION_NAMES = {'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS_RECIPE', 'C': 'COSMO'}


# ── Utility ─────────────────────────────────────────────────────────

def normalize_rows(m):
    row_sums = m.sum(axis=1, keepdims=True)
    return m / np.maximum(row_sums, 1e-12)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# ── Data Loading ────────────────────────────────────────────────────

def load_data():
    """Load all data, partition by section, build per-section params."""
    print("Loading data...")

    # Token → class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}
    class_to_tokens_global = defaultdict(list)
    for tok, cls in token_to_class.items():
        class_to_tokens_global[cls].append(tok)

    # Forbidden MIDDLE pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    morph = Morphology()

    # Build real token stream with section tracking
    section_lines = defaultdict(list)  # section -> list of lines
    global_lines = []
    current_line = []
    current_section = None
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
        sec = token.section

        if key != prev_key and current_line:
            global_lines.append(current_line)
            if current_section:
                section_lines[current_section].append(current_line)
            current_line = []
        prev_key = key
        current_section = sec

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
            'section': sec,
        })
    if current_line:
        global_lines.append(current_line)
        if current_section:
            section_lines[current_section].append(current_line)

    def build_params(lines, token_to_class, class_to_tokens, forbidden_middle_pairs, morph):
        """Build generation parameters from a set of lines."""
        all_tokens = [t for line in lines for t in line]
        if not all_tokens:
            return None, [], None

        token_freq = Counter(t['word'] for t in all_tokens)
        tokens_list = list(token_freq.keys())
        token_probs = np.array([token_freq[t] for t in tokens_list], dtype=float)
        token_probs /= token_probs.sum()

        # Class transition matrix
        class_trans = np.zeros((N_CLASSES, N_CLASSES))
        for line in lines:
            for i in range(len(line) - 1):
                class_trans[line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

        # Opener distribution
        opener_counts = Counter(line[0]['cls'] for line in lines if line)
        opener_probs = np.zeros(N_CLASSES)
        for cls, count in opener_counts.items():
            opener_probs[cls - 1] = count
        opener_probs /= max(opener_probs.sum(), 1)

        # Line lengths
        line_lengths = [len(line) for line in lines]

        # Class → token probs (section-specific)
        class_token_probs = {}
        section_class_to_tokens = defaultdict(list)
        for t in all_tokens:
            section_class_to_tokens[t['cls']].append(t['word'])
        for cls in range(1, N_CLASSES + 1):
            toks_list = section_class_to_tokens.get(cls, [])
            if toks_list:
                freq = Counter(toks_list)
                toks = list(freq.keys())
                counts = [freq[t] for t in toks]
                total = sum(counts)
                if total > 0:
                    class_token_probs[cls] = (toks, np.array(counts, dtype=float) / total)

        # Topology coverage
        n_nonzero = np.count_nonzero(class_trans)

        params = {
            'tokens_list': tokens_list,
            'token_probs': token_probs,
            'token_to_class': token_to_class,
            'class_to_tokens': class_to_tokens,
            'class_trans': class_trans,
            'opener_probs': opener_probs,
            'line_lengths': line_lengths,
            'class_token_probs': class_token_probs,
            'forbidden_middle_pairs': forbidden_middle_pairs,
            'morph': morph,
            'n_nonzero_transitions': n_nonzero,
            '_real_tokens': all_tokens,
        }

        return params, all_tokens, lines

    # Build global params
    global_params, global_tokens, _ = build_params(
        global_lines, token_to_class, class_to_tokens_global,
        forbidden_middle_pairs, morph)

    # Build per-section params
    section_params = {}
    section_tokens = {}
    for sec in sorted(section_lines.keys()):
        params, tokens, _ = build_params(
            section_lines[sec], token_to_class, class_to_tokens_global,
            forbidden_middle_pairs, morph)
        if params:
            section_params[sec] = params
            section_tokens[sec] = tokens

    return global_params, global_tokens, global_lines, section_params, section_tokens, section_lines, morph


# ── M2 Generation (from Phase 348) ─────────────────────────────────

def generate_m2(params, rng, override_n_lines=None, override_line_lengths=None):
    """M2: 49-class Markov + forbidden MIDDLE pair suppression."""
    trans = params['class_trans'].copy()
    morph = params['morph']

    # Apply forbidden suppression
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
    n_lines = override_n_lines if override_n_lines else len(params['line_lengths'])
    line_lengths = override_line_lengths if override_line_lengths else params['line_lengths']

    for _ in range(n_lines):
        length = rng.choice(line_lengths)
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


# ── Test Battery (from Phase 348) ──────────────────────────────────

def compute_metrics(corpus, params, morph):
    """Compute all 15 test metrics."""
    all_tokens = [t for line in corpus for t in line]
    n_tokens = len(all_tokens)
    if n_tokens == 0:
        return {}

    # A1: Class KL
    real_class_dist = np.zeros(N_CLASSES)
    for t in params.get('_real_tokens', []):
        if 1 <= t['cls'] <= N_CLASSES:
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
    a2_hapax = sum(1 for c in word_counts.values() if c == 1) / max(len(word_counts), 1)

    # A3: Active classes
    a3_active = len(set(t['cls'] for t in all_tokens if 1 <= t['cls'] <= N_CLASSES))

    # A4: Type count
    a4_types = len(word_counts)

    # B1: Spectral gap
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

    # B2: AXM self-transition
    axm_idx = STATE_IDX['AXM']
    axm_row_sum = state_trans[axm_idx].sum()
    b2_axm_self = float(state_trans[axm_idx, axm_idx] / max(axm_row_sum, 1))

    # B3: Forbidden violations
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

    # B4: Role rank order
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

    # B5: Fwd-rev JSD
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

    # C1: Suffix rate
    suffix_count = 0
    cc_suffix_violations = 0
    cc_total = 0
    for t in all_tokens:
        sfx = t.get('suffix')
        if sfx is None:
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

    # C3: PREFIX entropy reduction
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

    # D1: Stationary distribution
    stat_counts = Counter(CLASS_TO_STATE.get(t['cls'], 'UNK') for t in all_tokens)
    stat_total = sum(stat_counts.values())
    d1_stationary = {s: stat_counts.get(s, 0) / stat_total for s in STATE_ORDER}

    # D2: AXM dwell
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

    # D3: Cross-line MI
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
    }


def evaluate_tests(metrics, real_metrics):
    """Evaluate 15 pass/fail tests."""
    results = {}
    results['A1'] = metrics['A1_class_kl'] < 0.05
    results['A2'] = abs(metrics['A2_hapax_rate'] - real_metrics['A2_hapax_rate']) < 0.05
    results['A3'] = abs(metrics['A3_active_classes'] - real_metrics['A3_active_classes']) <= 3
    real_types = real_metrics['A4_type_count']
    results['A4'] = abs(metrics['A4_type_count'] - real_types) / max(real_types, 1) < 0.20
    results['B1'] = abs(metrics['B1_spectral_gap'] - real_metrics['B1_spectral_gap']) < 0.05
    results['B2'] = abs(metrics['B2_axm_self'] - real_metrics['B2_axm_self']) < 0.03
    results['B3'] = metrics['B3_forbidden'] == 0
    results['B4'] = bool(metrics['B4_role_rank'])
    real_jsd = real_metrics['B5_fwd_rev_jsd']
    results['B5'] = abs(metrics['B5_fwd_rev_jsd'] - real_jsd) / max(real_jsd, 1e-6) < 0.50
    results['C1'] = abs(metrics['C1_suffix_rate'] - real_metrics['C1_suffix_rate']) < 0.03
    results['C2'] = metrics['C2_cc_suffix_free'] >= 0.99
    results['C3'] = abs(metrics['C3_prefix_entropy_red'] - real_metrics['C3_prefix_entropy_red']) < 0.10
    max_dev = max(abs(metrics['D1_stationary'].get(s, 0) - real_metrics['D1_stationary'].get(s, 0))
                  for s in STATE_ORDER)
    results['D1'] = max_dev < 0.03
    results['D2'] = abs(metrics['D2_axm_dwell'] - real_metrics['D2_axm_dwell']) < 0.5
    results['D3'] = abs(metrics['D3_cross_line_mi'] - real_metrics['D3_cross_line_mi']) < 0.15
    return results


TEST_NAMES = ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B5',
              'C1', 'C2', 'C3', 'D1', 'D2', 'D3']


def run_m2_battery(params, real_metrics, morph, n_inst=N_INST,
                   override_n_lines=None, override_line_lengths=None):
    """Generate n_inst M2 corpora and evaluate the 15-test battery.
    Returns per-test pass rates and mean pass count."""
    inst_tests = []
    for inst in range(n_inst):
        rng = np.random.RandomState(42 + inst * 1000)
        corpus = generate_m2(params, rng, override_n_lines, override_line_lengths)
        metrics = compute_metrics(corpus, params, morph)
        tests = evaluate_tests(metrics, real_metrics)
        inst_tests.append(tests)

    per_test = {}
    for test in TEST_NAMES:
        per_test[test] = sum(1 for t in inst_tests if t.get(test, False)) / n_inst

    pass_counts = [sum(t.values()) for t in inst_tests]
    mean_pass = float(np.mean(pass_counts))

    return {
        'mean_pass': mean_pass,
        'pass_rate': mean_pass / len(TEST_NAMES),
        'per_test_pass_rate': per_test,
    }


# ── Main ────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Phase 370: SECTION_SPECIFIC_M2")
    print("=" * 70)

    # ── S1: Load Data ──────────────────────────────────────────
    print("\n--- S1: Data Loading + Section Partitioning ---")
    (global_params, global_tokens, global_lines,
     section_params, section_tokens, section_lines, morph) = load_data()

    print(f"  Global: {len(global_tokens)} tokens, {len(global_lines)} lines")
    section_inventory = {}
    for sec in sorted(section_params.keys()):
        n_tok = len(section_tokens[sec])
        n_lines = len(section_lines[sec])
        n_nonzero = section_params[sec]['n_nonzero_transitions']
        viable = n_tok >= 500
        section_inventory[sec] = {
            'name': SECTION_NAMES.get(sec, sec),
            'tokens': n_tok,
            'lines': n_lines,
            'n_nonzero_transitions': n_nonzero,
            'viable': viable,
        }
        flag = '' if viable else ' [TOO SMALL — excluded from thresholds]'
        print(f"  Section {sec} ({SECTION_NAMES.get(sec, sec)}): "
              f"{n_tok} tokens, {n_lines} lines, {n_nonzero} transitions{flag}")

    viable_sections = [s for s in section_inventory if section_inventory[s]['viable']]
    # Exclude COSMO from threshold testing
    threshold_sections = [s for s in viable_sections if s != 'C']

    # ── S2: Real Metrics Per Section ───────────────────────────
    print("\n--- S2: Real Metrics Per Section ---")
    real_metrics = {}
    real_metrics['global'] = compute_metrics(global_lines, global_params, morph)
    print(f"  Global real: A1_kl={real_metrics['global']['A1_class_kl']:.6f}, "
          f"B1={real_metrics['global']['B1_spectral_gap']:.4f}, "
          f"B3={real_metrics['global']['B3_forbidden']}")

    for sec in viable_sections:
        real_metrics[sec] = compute_metrics(section_lines[sec], section_params[sec], morph)
        print(f"  Section {sec}: A1_kl={real_metrics[sec]['A1_class_kl']:.6f}, "
              f"B1={real_metrics[sec]['B1_spectral_gap']:.4f}, "
              f"B3={real_metrics[sec]['B3_forbidden']}, "
              f"types={real_metrics[sec]['A4_type_count']}")

    # ── S3: H1 — Per-Section M2 (LOCAL-LOCAL) ─────────────────
    print("\n--- S3: H1 — Per-Section M2 Sufficiency (LOCAL-LOCAL) ---")
    h1_results = {}
    for sec in viable_sections:
        print(f"  Generating M2 for section {sec} ({SECTION_NAMES[sec]})...")
        result = run_m2_battery(section_params[sec], real_metrics[sec], morph)
        h1_results[sec] = result
        print(f"    Mean pass: {result['mean_pass']:.1f}/15 ({result['pass_rate']:.0%})")
        # Show per-test
        for test in TEST_NAMES:
            rate = result['per_test_pass_rate'][test]
            mark = 'v' if rate >= 0.5 else 'x'
            print(f"      {test}: {rate:.0%} [{mark}]")

    # Evaluate H1
    h1_pass = True
    h1_detail = []
    for sec in threshold_sections:
        threshold = 12 if sec in ('B', 'S') else 10
        if h1_results[sec]['mean_pass'] < threshold:
            h1_pass = False
            h1_detail.append(f"{sec}: {h1_results[sec]['mean_pass']:.1f} < {threshold}")
        else:
            h1_detail.append(f"{sec}: {h1_results[sec]['mean_pass']:.1f} >= {threshold} PASS")
    print(f"\n  H1 PASS: {h1_pass}")
    for d in h1_detail:
        print(f"    {d}")

    # ── S4: H2 — Global M2 Per-Section (GLOBAL-LOCAL) ─────────
    print("\n--- S4: H2 — Global M2 Per-Section (GLOBAL-LOCAL) ---")

    # Generate 20 global M2 instantiations and evaluate per section
    print("  Generating 20 global M2 corpora...")
    global_inst_results = {sec: [] for sec in viable_sections}
    global_self_tests = []

    for inst in range(N_INST):
        rng = np.random.RandomState(42 + inst * 1000)
        corpus = generate_m2(global_params, rng)
        # Evaluate against global metrics
        g_metrics = compute_metrics(corpus, global_params, morph)
        g_tests = evaluate_tests(g_metrics, real_metrics['global'])
        global_self_tests.append(g_tests)
        # Evaluate against each section's real metrics
        for sec in viable_sections:
            s_tests = evaluate_tests(g_metrics, real_metrics[sec])
            global_inst_results[sec].append(s_tests)

    # Global self-evaluation (should match C1025)
    global_per_test = {}
    for test in TEST_NAMES:
        global_per_test[test] = sum(1 for t in global_self_tests if t.get(test, False)) / N_INST
    global_mean_pass = float(np.mean([sum(t.values()) for t in global_self_tests]))
    print(f"  Global M2 self-evaluation: {global_mean_pass:.1f}/15")

    h2_per_section = {}
    for sec in viable_sections:
        per_test = {}
        for test in TEST_NAMES:
            per_test[test] = sum(1 for t in global_inst_results[sec]
                                 if t.get(test, False)) / N_INST
        mean_pass = float(np.mean([sum(t.values()) for t in global_inst_results[sec]]))
        h2_per_section[sec] = {
            'mean_pass': mean_pass,
            'pass_rate': mean_pass / len(TEST_NAMES),
            'per_test_pass_rate': per_test,
        }
        print(f"  Global M2 → Section {sec}: {mean_pass:.1f}/15")
        for test in TEST_NAMES:
            rate = per_test[test]
            mark = 'v' if rate >= 0.5 else 'x'
            print(f"      {test}: {rate:.0%} [{mark}]")

    # H2 evaluation: A1/D1 degradation, B1/B3 preservation
    a1_degraded = sum(1 for sec in viable_sections
                      if h2_per_section[sec]['per_test_pass_rate']['A1'] < 0.5)
    d1_degraded = sum(1 for sec in viable_sections
                      if h2_per_section[sec]['per_test_pass_rate']['D1'] < 0.5)
    distrib_degraded = a1_degraded + d1_degraded
    b1_preserved = all(h2_per_section[sec]['per_test_pass_rate']['B1'] >= 0.8
                       for sec in viable_sections)
    b3_preserved = all(h2_per_section[sec]['per_test_pass_rate']['B3'] >= 0.8
                       for sec in viable_sections)

    h2_pass = (distrib_degraded >= 2) and b1_preserved and b3_preserved
    print(f"\n  H2 evaluation:")
    print(f"    A1 degraded sections: {a1_degraded}")
    print(f"    D1 degraded sections: {d1_degraded}")
    print(f"    Distributional degraded (A1+D1): {distrib_degraded} (need >= 2)")
    print(f"    B1 preserved: {b1_preserved}")
    print(f"    B3 preserved: {b3_preserved}")
    print(f"  H2 PASS: {h2_pass}")

    # ── S5: H3 — Cross-Section Transfer ───────────────────────
    print("\n--- S5: H3 — Cross-Section Transfer ---")
    transfer_results = {}
    for src in viable_sections:
        for tgt in viable_sections:
            if src == tgt:
                continue
            # Train on src, generate with src params but tgt line structure
            tgt_n_lines = len(section_lines[tgt])
            tgt_line_lengths = section_params[tgt]['line_lengths']
            result = run_m2_battery(
                section_params[src], real_metrics[tgt], morph,
                override_n_lines=tgt_n_lines,
                override_line_lengths=tgt_line_lengths)
            key = f"{src}_to_{tgt}"
            transfer_results[key] = result
            print(f"  {src}→{tgt}: {result['mean_pass']:.1f}/15")

    # Compute correlation with C1029 JSD
    jsd_values = []
    pass_values = []
    for (s1, s2), jsd in SECTION_JSD.items():
        fwd_key = f"{s1}_to_{s2}"
        rev_key = f"{s2}_to_{s1}"
        if fwd_key in transfer_results:
            jsd_values.append(jsd)
            pass_values.append(transfer_results[fwd_key]['mean_pass'])
        if rev_key in transfer_results:
            jsd_values.append(jsd)
            pass_values.append(transfer_results[rev_key]['mean_pass'])

    if len(jsd_values) >= 4:
        rho, p_val = spearmanr(jsd_values, pass_values)
    else:
        rho, p_val = 0.0, 1.0

    # Check specific transfer predictions
    bs_key = 'B_to_S'
    bs_pass = transfer_results.get(bs_key, {}).get('mean_pass', 0)
    cosmo_max = max(
        (transfer_results.get(f'C_to_{tgt}', {}).get('mean_pass', 0)
         for tgt in viable_sections if tgt != 'C'),
        default=0)

    h3_rho_pass = rho < -0.5
    h3_bs_pass = bs_pass >= 10
    h3_cosmo_pass = cosmo_max <= 8 if 'C' in viable_sections else True
    h3_pass = h3_rho_pass and h3_bs_pass

    print(f"\n  JSD-transfer correlation: rho={rho:.3f}, p={p_val:.4f}")
    print(f"  BIO→STARS_RECIPE: {bs_pass:.1f}/15 (need >= 10): {'PASS' if h3_bs_pass else 'FAIL'}")
    if 'C' in viable_sections:
        print(f"  COSMO→best: {cosmo_max:.1f}/15 (need <= 8): {'PASS' if h3_cosmo_pass else 'FAIL'}")
    print(f"  rho < -0.5: {'PASS' if h3_rho_pass else 'FAIL'}")
    print(f"  H3 PASS: {h3_pass}")

    # ── S6: H4 — Test Sensitivity Classification ──────────────
    print("\n--- S6: H4 — Test Sensitivity Classification ---")
    # Use only threshold sections (BIO, HERBAL, STARS_RECIPE) for classification
    test_classification = {}
    for test in TEST_NAMES:
        rates = [h1_results[sec]['per_test_pass_rate'][test]
                 for sec in threshold_sections if sec in h1_results]
        rate_range = max(rates) - min(rates) if rates else 0
        classification = 'invariant' if rate_range <= 0.20 else 'sensitive'
        test_classification[test] = {
            'pass_rates': {sec: h1_results[sec]['per_test_pass_rate'][test]
                          for sec in threshold_sections},
            'range': rate_range,
            'classification': classification,
        }
        print(f"  {test}: range={rate_range:.2f} → {classification}")
        for sec in threshold_sections:
            print(f"    {sec}: {h1_results[sec]['per_test_pass_rate'][test]:.0%}")

    n_invariant = sum(1 for t in test_classification.values() if t['classification'] == 'invariant')
    n_sensitive = sum(1 for t in test_classification.values() if t['classification'] == 'sensitive')
    b3_invariant = test_classification.get('B3', {}).get('classification') == 'invariant'
    c1_invariant = test_classification.get('C1', {}).get('classification') == 'invariant'

    h4_pass = (n_invariant >= 3 and n_sensitive >= 3
               and b3_invariant and c1_invariant)
    print(f"\n  Invariant: {n_invariant} (need >= 3)")
    print(f"  Sensitive: {n_sensitive} (need >= 3)")
    print(f"  B3 invariant: {b3_invariant}")
    print(f"  C1 invariant: {c1_invariant}")
    print(f"  H4 PASS: {h4_pass}")

    # ── S7: H5 — Pooling Advantage ────────────────────────────
    print("\n--- S7: H5 — No Pooling Advantage ---")

    # Weighted average of local M2 pass rates (COSMO excluded)
    total_weight = sum(section_inventory[sec]['tokens'] for sec in threshold_sections)
    weighted_local = sum(
        h1_results[sec]['mean_pass'] * section_inventory[sec]['tokens'] / total_weight
        for sec in threshold_sections)
    advantage = global_mean_pass - weighted_local

    print(f"  Global M2 mean pass: {global_mean_pass:.1f}")
    print(f"  Weighted local M2 mean pass: {weighted_local:.1f}")
    print(f"  Pooling advantage: {advantage:+.1f} tests")

    h5_pass = advantage <= 1.0
    print(f"  Advantage <= 1.0: {h5_pass}")
    print(f"  H5 PASS: {h5_pass}")

    # ── S8: Verdict Synthesis ─────────────────────────────────
    print("\n--- S8: Verdict Synthesis ---")
    n_pass = sum([h1_pass, h2_pass, h3_pass, h4_pass, h5_pass])
    hypotheses = {
        'H1': {'name': 'Per-section M2 sufficiency', 'pass': h1_pass},
        'H2': {'name': 'Global M2 distributional degradation', 'pass': h2_pass},
        'H3': {'name': 'Cross-section transfer vs JSD', 'pass': h3_pass},
        'H4': {'name': 'Test sensitivity classification', 'pass': h4_pass},
        'H5': {'name': 'No pooling advantage', 'pass': h5_pass},
    }

    print(f"\nResults: {n_pass}/5 hypotheses pass")
    for h, info in hypotheses.items():
        mark = 'PASS' if info['pass'] else 'FAIL'
        print(f"  {h} ({info['name']}): {mark:>8}")

    # Determine verdict
    if h1_pass and h5_pass:
        if h3_pass:
            verdict = "SECTION_DECOMPOSABLE"
        else:
            verdict = "SECTION_SUFFICIENT"
    elif h1_pass:
        verdict = "LOCAL_SUFFICIENT_POOLING_HELPS"
    else:
        verdict = "POOLING_REQUIRED"

    print(f"\nVerdict: {verdict}")

    # ── Save ──────────────────────────────────────────────────
    output = {
        'phase': 'SECTION_SPECIFIC_M2',
        'phase_number': 370,
        'depends_on': ['C1025', 'C1029', 'C1030', 'C1047'],
        'section_inventory': section_inventory,
        'real_metrics': {k: {mk: mv for mk, mv in v.items()
                             if not isinstance(mv, np.ndarray)}
                         for k, v in real_metrics.items()},
        'h1_local_local': {
            'per_section': h1_results,
            'pass': h1_pass,
            'detail': h1_detail,
        },
        'h2_global_local': {
            'global_self': {'mean_pass': global_mean_pass, 'per_test': global_per_test},
            'per_section': h2_per_section,
            'a1_degraded': a1_degraded,
            'd1_degraded': d1_degraded,
            'b1_preserved': b1_preserved,
            'b3_preserved': b3_preserved,
            'pass': h2_pass,
        },
        'h3_cross_transfer': {
            'transfer_results': transfer_results,
            'jsd_correlation': {'rho': rho, 'p': p_val},
            'bio_to_stars': bs_pass,
            'cosmo_max_transfer': cosmo_max,
            'pass': h3_pass,
        },
        'h4_test_sensitivity': {
            'per_test': test_classification,
            'n_invariant': n_invariant,
            'n_sensitive': n_sensitive,
            'b3_invariant': b3_invariant,
            'c1_invariant': c1_invariant,
            'pass': h4_pass,
        },
        'h5_pooling_advantage': {
            'global_pass': global_mean_pass,
            'weighted_local_pass': weighted_local,
            'advantage': advantage,
            'pass': h5_pass,
        },
        'verdict': verdict,
        'verdict_score': f'{n_pass}/5',
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'section_specific_m2.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults written to {out_path}")
    print("\nDone.")


if __name__ == '__main__':
    main()
