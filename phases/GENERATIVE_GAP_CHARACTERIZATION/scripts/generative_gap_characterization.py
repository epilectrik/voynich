#!/usr/bin/env python3
"""
Phase 479: M2.1 GENERATIVE GAP CHARACTERIZATION
=================================================
Characterizes the gap between M2.1 (corpus-wide generative model, 21/21
at corpus level) and real per-folio structure. Instead of predicting the
~27% folio-level design freedom (C1169 — proven irreducible by C1035,
C1155, C1189, C1294, C1047), this phase CHARACTERIZES it: generating 100
synthetic counterparts per real folio, computing 32-feature vectors,
z-scoring each real folio against its synthetic distribution, and
analyzing the anomaly landscape.

Core question: What specific statistical properties do real folios exhibit
that M2.1 synthetic folios do not, and how does this gap vary?

Depends on: C1365, C1364, C1034, C1169, C1035, C1048, C458
"""

import json
import sys
import math
import time
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import entropy as scipy_entropy, spearmanr, mannwhitneyu

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ── Constants ────────────────────────────────────────────────────────

N_CLASSES = 49
N_QUINTILES = 5
N_SYNTHETIC = 100
SEED = 479

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

KERNEL_K = {1, 2, 3, 4, 5, 6}
KERNEL_H = {7, 30, 38, 40}
KERNEL_E = {9, 13, 14, 23, 10, 11, 12}

FEATURE_NAMES = [
    # A: Class distribution (7)
    'class_entropy', 'class_concentration', 'axm_fraction', 'fq_fraction',
    'cc_fraction', 'fl_haz_fraction', 'active_classes',
    # B: Sequential (6)
    'axm_self_transition', 'spectral_gap', 'mean_run_length',
    'forbidden_violations', 'bigram_entropy', 'fwd_rev_jsd',
    # C: Morphological (6)
    'suffix_rate', 'prefix_entropy', 'prefix_count', 'bare_token_rate',
    'articulator_rate', 'mean_word_length',
    # D: Positional (4)
    'q0_axm_frac', 'q4_axm_frac', 'axm_gradient', 'opener_entropy',
    # E: Dark/Bridge (3)
    'dark_middle_fraction', 'bridge_middle_fraction', 'exclusive_b_fraction',
    # F: Kernel (3)
    'k_fraction', 'h_fraction', 'e_fraction',
    # G: Category (2)
    'category_entropy', 'dominant_category_fraction',
    # H: Boundary (1)
    'closer_rate',
]

# Features related to hazard (C458: should be clamped / low z)
HAZARD_FEATURES = {'fl_haz_fraction', 'cc_fraction'}
# Features related to recovery/freedom (C458: should be free / high z)
RECOVERY_FEATURES = {'suffix_rate', 'prefix_entropy', 'articulator_rate',
                     'mean_word_length', 'dark_middle_fraction', 'category_entropy'}
# Excluded from analysis (sanity check only — class-level vs MIDDLE-level mismatch)
EXCLUDED_FROM_ANALYSIS = {'forbidden_violations'}


# ── Utilities ────────────────────────────────────────────────────────

def assign_quintile(idx, line_len):
    return min(N_QUINTILES - 1, int(idx / line_len * N_QUINTILES))


def normalize_rows(m):
    row_sums = m.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
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
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def safe_entropy(counts):
    """Shannon entropy from a counts array."""
    total = sum(counts) if isinstance(counts, (list, tuple)) else counts.sum()
    if total == 0:
        return 0.0
    probs = np.array(counts, dtype=float) / total
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load all data needed for gap characterization."""
    print("Loading data...")

    # 49-class map
    with open(PROJECT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json',
              encoding='utf-8') as f:
        cmap = json.load(f)
    token_to_class = {tok: int(cls) for tok, cls in cmap['token_to_class'].items()}
    class_to_tokens = defaultdict(list)
    for tok, cls in token_to_class.items():
        class_to_tokens[cls].append(tok)

    # Forbidden pairs
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json',
              encoding='utf-8') as f:
        forbidden_inv = json.load(f)
    forbidden_middle_pairs = set()
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.add((t['source'], t['target']))

    # Dark pipeline MIDDLEs
    with open(PROJECT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
        dark_data = json.load(f)
    dark_middles = set(dark_data['middles'])

    # Bridge MIDDLEs
    with open(PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json',
              encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])

    # Folio metadata (72 valid folios)
    with open(PROJECT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json',
              encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_metadata = axm_data['folio_data']

    # REGIME mapping
    with open(PROJECT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_raw = json.load(f)
    folio_regime = {}
    for f_id, v in regime_raw.get('regime_assignments', regime_raw).items():
        if isinstance(v, dict):
            folio_regime[f_id] = v.get('regime', v.get('REGIME', 'UNK'))
        else:
            folio_regime[f_id] = str(v)

    morph = Morphology()
    cc = CategoryClassifier()

    # Build token-to-morph cache for all known B vocabulary
    token_morph_cache = {}
    for tok in token_to_class:
        m = morph.extract(tok)
        token_morph_cache[tok] = {
            'prefix': m.prefix if m else None,
            'middle': m.middle if m else tok,
            'suffix': m.suffix if m else None,
            'articulator': m.articulator if m else None,
        }

    # Build MIDDLE-to-category cache
    middle_category_cache = {}
    all_middles = set()
    for tok_morph in token_morph_cache.values():
        all_middles.add(tok_morph['middle'])
    for mid in all_middles:
        cat = cc.classify(mid)
        if cat:
            middle_category_cache[mid] = cat

    # Load transcript organized by folio and line
    valid_folios = set(folio_metadata.keys())
    folio_lines = defaultdict(list)  # folio -> list of lines (each line = list of token dicts)
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
        if token.folio not in valid_folios:
            continue

        key = (token.folio, token.line)
        if key != prev_key and current_line:
            folio_lines[prev_key[0]].append(current_line)
            current_line = []
        prev_key = key

        mc = token_morph_cache.get(token.word, {})
        current_line.append({
            'word': token.word,
            'cls': cls,
            'state': CLASS_TO_STATE.get(cls, 'UNK'),
            'prefix': mc.get('prefix'),
            'middle': mc.get('middle', token.word),
            'suffix': mc.get('suffix'),
            'articulator': mc.get('articulator'),
        })
    if current_line and prev_key and prev_key[0] in valid_folios:
        folio_lines[prev_key[0]].append(current_line)

    # Also build corpus-wide lines for M2.1 parameters
    all_lines = []
    for folio in sorted(folio_lines.keys()):
        all_lines.extend(folio_lines[folio])

    all_tokens = [t for line in all_lines for t in line]

    n_folios = len(folio_lines)
    n_tokens = len(all_tokens)
    n_lines = len(all_lines)
    print(f"  {n_tokens} tokens in {n_lines} lines across {n_folios} folios")

    # Corpus-wide quintile transition matrices
    quintile_trans = {q: np.zeros((N_CLASSES, N_CLASSES)) for q in range(N_QUINTILES)}
    for line in all_lines:
        line_len = len(line)
        for i in range(line_len - 1):
            q = assign_quintile(i, line_len)
            quintile_trans[q][line[i]['cls'] - 1, line[i + 1]['cls'] - 1] += 1

    # Opener distribution
    opener_counts = Counter(line[0]['cls'] for line in all_lines if line)
    opener_probs = np.zeros(N_CLASSES)
    for cls, count in opener_counts.items():
        opener_probs[cls - 1] = count
    opener_probs /= max(opener_probs.sum(), 1)

    # Class-to-token frequency-weighted probabilities
    token_freq = Counter(t['word'] for t in all_tokens)
    class_token_probs = {}
    for cls in range(1, N_CLASSES + 1):
        toks = class_to_tokens.get(cls, [])
        if toks:
            counts = [token_freq.get(t, 0) for t in toks]
            total = sum(counts)
            if total > 0:
                class_token_probs[cls] = (toks, np.array(counts, dtype=float) / total)

    # Compute closer classes (top-5 by line-final position fraction)
    closer_counts = Counter()
    for line in all_lines:
        if line:
            closer_counts[line[-1]['cls']] += 1
    total_lines = sum(closer_counts.values())
    closer_classes = set(cls for cls, _ in closer_counts.most_common(5))

    params = {
        'folio_lines': dict(folio_lines),
        'all_lines': all_lines,
        'all_tokens': all_tokens,
        'quintile_trans': quintile_trans,
        'opener_probs': opener_probs,
        'class_token_probs': class_token_probs,
        'class_to_tokens': dict(class_to_tokens),
        'forbidden_middle_pairs': forbidden_middle_pairs,
        'token_morph_cache': token_morph_cache,
        'middle_category_cache': middle_category_cache,
        'dark_middles': dark_middles,
        'bridge_middles': bridge_middles,
        'folio_metadata': folio_metadata,
        'folio_regime': folio_regime,
        'closer_classes': closer_classes,
        'morph': morph,
    }
    return params


# ── Forbidden Pair Construction ──────────────────────────────────────

def build_symmetric_forbidden(params):
    """Build symmetric forbidden class pairs from MIDDLE-level forbidden pairs."""
    morph = params['morph']
    class_to_tokens = params['class_to_tokens']
    forbidden_middle_pairs = params['forbidden_middle_pairs']

    # Pre-compute MIDDLE for each token in each class
    class_middles = {}
    for cls, toks in class_to_tokens.items():
        mids = set()
        for tok in toks:
            m = morph.extract(tok)
            mids.add(m.middle if m else tok)
        class_middles[cls] = mids

    forbidden_cls = set()
    for src_mid, tgt_mid in forbidden_middle_pairs:
        src_classes = {cls for cls, mids in class_middles.items() if src_mid in mids}
        tgt_classes = {cls for cls, mids in class_middles.items() if tgt_mid in mids}
        for sc in src_classes:
            for tc in tgt_classes:
                forbidden_cls.add((sc, tc))

    symmetric = set()
    for a, b in forbidden_cls:
        symmetric.add((a, b))
        symmetric.add((b, a))

    print(f"  Forbidden class pairs: {len(forbidden_cls)} forward, {len(symmetric)} symmetric")
    return symmetric


def build_m21_matrices(quintile_trans, forbidden_pairs):
    """Build 5 quintile-conditioned transition matrices with forbidden suppression."""
    matrices = {}
    for q in range(N_QUINTILES):
        trans = quintile_trans[q].copy()
        for src, tgt in forbidden_pairs:
            trans[src - 1, tgt - 1] = 0
        matrices[q] = normalize_rows(trans)
    return matrices


# ── Synthetic Folio Generation ───────────────────────────────────────

def generate_synthetic_folio(line_lengths, quintile_matrices, opener_probs,
                             class_token_probs, token_morph_cache, rng):
    """Generate one synthetic folio matching the given line lengths.

    Returns list of lines, each line = list of token dicts with
    word, cls, state, prefix, middle, suffix, articulator.
    """
    folio_lines = []
    for length in line_lengths:
        line = []
        cls = rng.choice(N_CLASSES, p=opener_probs) + 1
        for pos in range(length):
            if pos > 0:
                src_q = assign_quintile(pos - 1, length)
                row = quintile_matrices[src_q][cls - 1]
                if row.sum() > 0:
                    cls = rng.choice(N_CLASSES, p=row) + 1
                else:
                    cls = rng.choice(N_CLASSES, p=opener_probs) + 1
            if cls in class_token_probs:
                toks, probs = class_token_probs[cls]
                word = rng.choice(toks, p=probs)
            else:
                word = f'UNK_C{cls}'

            mc = token_morph_cache.get(word, {})
            line.append({
                'word': word,
                'cls': cls,
                'state': CLASS_TO_STATE.get(cls, 'UNK'),
                'prefix': mc.get('prefix'),
                'middle': mc.get('middle', word),
                'suffix': mc.get('suffix'),
                'articulator': mc.get('articulator'),
            })
        folio_lines.append(line)
    return folio_lines


# ── Feature Computation ──────────────────────────────────────────────

def compute_folio_features(folio_lines, params):
    """Compute 32-feature vector from a folio's lines.

    Args:
        folio_lines: list of lines, each line = list of token dicts
        params: dict with dark_middles, bridge_middles, middle_category_cache,
                closer_classes
    Returns:
        dict {feature_name: float_value}
    """
    all_tokens = [t for line in folio_lines for t in line]
    n = len(all_tokens)
    if n == 0:
        return {f: 0.0 for f in FEATURE_NAMES}

    dark_middles = params['dark_middles']
    bridge_middles = params['bridge_middles']
    mid_cat_cache = params['middle_category_cache']
    closer_classes = params['closer_classes']

    # ── A: Class distribution ────────────────────────────────────
    cls_counts = np.zeros(N_CLASSES)
    for t in all_tokens:
        cls_counts[t['cls'] - 1] += 1
    cls_probs = cls_counts / n

    class_entropy = safe_entropy(cls_counts)
    class_concentration = float(np.sum(cls_probs ** 2))  # HHI

    state_counts = Counter(t['state'] for t in all_tokens)
    axm_fraction = state_counts.get('AXM', 0) / n
    fq_fraction = state_counts.get('FQ', 0) / n
    cc_fraction = state_counts.get('CC', 0) / n
    fl_haz_fraction = state_counts.get('FL_HAZ', 0) / n

    active_classes = int(np.sum(cls_counts > 0))

    # ── B: Sequential ────────────────────────────────────────────
    # 6-state transition matrix
    state_trans = np.zeros((6, 6))
    for line in folio_lines:
        for i in range(len(line) - 1):
            s1 = STATE_IDX.get(line[i]['state'])
            s2 = STATE_IDX.get(line[i + 1]['state'])
            if s1 is not None and s2 is not None:
                state_trans[s1, s2] += 1

    state_trans_norm = normalize_rows(state_trans.copy())
    axm_idx = STATE_IDX['AXM']
    axm_row_sum = state_trans[axm_idx].sum()
    axm_self_transition = float(state_trans[axm_idx, axm_idx] / max(axm_row_sum, 1))

    # Spectral gap
    try:
        eigvals = np.abs(np.linalg.eigvals(state_trans_norm))
        eigvals_sorted = sorted(eigvals, reverse=True)
        spectral_gap = float(1.0 - eigvals_sorted[1]) if len(eigvals_sorted) > 1 else 0.0
    except Exception:
        spectral_gap = 0.0

    # Mean AXM run length
    runs = []
    current_run = 0
    for line in folio_lines:
        for t in line:
            if t['state'] == 'AXM':
                current_run += 1
            else:
                if current_run > 0:
                    runs.append(current_run)
                current_run = 0
        if current_run > 0:
            runs.append(current_run)
        current_run = 0
    mean_run_length = float(np.mean(runs)) if runs else 0.0

    # Forbidden violations (49-class bigrams)
    forbidden_middle_pairs = params['forbidden_middle_pairs']
    violations = 0
    for line in folio_lines:
        for i in range(len(line) - 1):
            pair = (line[i]['middle'], line[i + 1]['middle'])
            if pair in forbidden_middle_pairs:
                violations += 1

    # Bigram entropy (49-class)
    bigram_counts = Counter()
    for line in folio_lines:
        for i in range(len(line) - 1):
            bigram_counts[(line[i]['cls'], line[i + 1]['cls'])] += 1
    bigram_entropy = safe_entropy(list(bigram_counts.values())) if bigram_counts else 0.0

    # Forward-backward JSD (class-level)
    fwd_counts = Counter()
    rev_counts = Counter()
    for line in folio_lines:
        classes = [t['cls'] for t in line]
        for i in range(len(classes) - 1):
            fwd_counts[(classes[i], classes[i + 1])] += 1
        for i in range(len(classes) - 1, 0, -1):
            rev_counts[(classes[i], classes[i - 1])] += 1
    all_keys = sorted(set(fwd_counts.keys()) | set(rev_counts.keys()))
    if all_keys:
        fwd_total = sum(fwd_counts.values())
        rev_total = sum(rev_counts.values())
        fwd_arr = np.array([fwd_counts.get(k, 0) / max(fwd_total, 1) for k in all_keys]) + 1e-12
        rev_arr = np.array([rev_counts.get(k, 0) / max(rev_total, 1) for k in all_keys]) + 1e-12
        fwd_arr /= fwd_arr.sum()
        rev_arr /= rev_arr.sum()
        m_arr = 0.5 * (fwd_arr + rev_arr)
        fwd_rev_jsd = float(0.5 * scipy_entropy(fwd_arr, m_arr, base=2) +
                            0.5 * scipy_entropy(rev_arr, m_arr, base=2))
    else:
        fwd_rev_jsd = 0.0

    # ── C: Morphological ─────────────────────────────────────────
    suffix_count = sum(1 for t in all_tokens if t['suffix'])
    suffix_rate = suffix_count / n

    prefix_counts = Counter(t['prefix'] for t in all_tokens if t['prefix'])
    prefix_entropy = safe_entropy(list(prefix_counts.values())) if prefix_counts else 0.0
    prefix_count = len(prefix_counts)

    bare_count = sum(1 for t in all_tokens if not t['prefix'] and not t['suffix'])
    bare_token_rate = bare_count / n

    art_count = sum(1 for t in all_tokens if t['articulator'])
    articulator_rate = art_count / n

    mean_word_length = float(np.mean([len(t['word']) for t in all_tokens]))

    # ── D: Positional ────────────────────────────────────────────
    quintile_axm = {q: [0, 0] for q in range(N_QUINTILES)}  # [axm_count, total]
    for line in folio_lines:
        line_len = len(line)
        for i, t in enumerate(line):
            q = assign_quintile(i, line_len)
            quintile_axm[q][1] += 1
            if t['state'] == 'AXM':
                quintile_axm[q][0] += 1

    q_fracs = []
    for q in range(N_QUINTILES):
        total = quintile_axm[q][1]
        q_fracs.append(quintile_axm[q][0] / max(total, 1))

    q0_axm_frac = q_fracs[0]
    q4_axm_frac = q_fracs[4]

    # AXM gradient: slope of linear fit across quintiles
    if any(quintile_axm[q][1] > 0 for q in range(N_QUINTILES)):
        x = np.arange(N_QUINTILES)
        y = np.array(q_fracs)
        if np.std(y) > 0:
            axm_gradient = float(np.polyfit(x, y, 1)[0])
        else:
            axm_gradient = 0.0
    else:
        axm_gradient = 0.0

    opener_cls_counts = Counter(line[0]['cls'] for line in folio_lines if line)
    opener_entropy = safe_entropy(list(opener_cls_counts.values())) if opener_cls_counts else 0.0

    # ── E: Dark/Bridge ───────────────────────────────────────────
    dark_count = sum(1 for t in all_tokens if t['middle'] in dark_middles)
    bridge_count = sum(1 for t in all_tokens if t['middle'] in bridge_middles)
    exclusive_count = n - dark_count - bridge_count

    dark_middle_fraction = dark_count / n
    bridge_middle_fraction = bridge_count / n
    exclusive_b_fraction = max(0, exclusive_count) / n

    # ── F: Kernel ────────────────────────────────────────────────
    k_count = sum(1 for t in all_tokens if t['cls'] in KERNEL_K)
    h_count = sum(1 for t in all_tokens if t['cls'] in KERNEL_H)
    e_count = sum(1 for t in all_tokens if t['cls'] in KERNEL_E)

    k_fraction = k_count / n
    h_fraction = h_count / n
    e_fraction = e_count / n

    # ── G: Category ──────────────────────────────────────────────
    cat_counts = Counter()
    n_classifiable = 0
    for t in all_tokens:
        cat = mid_cat_cache.get(t['middle'])
        if cat:
            cat_counts[cat] += 1
            n_classifiable += 1

    category_entropy = safe_entropy(list(cat_counts.values())) if cat_counts else 0.0
    dominant_category_fraction = (max(cat_counts.values()) / max(n_classifiable, 1)
                                  if cat_counts else 0.0)

    # ── H: Boundary ──────────────────────────────────────────────
    closer_count = sum(1 for line in folio_lines if line and line[-1]['cls'] in closer_classes)
    closer_rate = closer_count / max(len(folio_lines), 1)

    return {
        'class_entropy': class_entropy,
        'class_concentration': class_concentration,
        'axm_fraction': axm_fraction,
        'fq_fraction': fq_fraction,
        'cc_fraction': cc_fraction,
        'fl_haz_fraction': fl_haz_fraction,
        'active_classes': float(active_classes),
        'axm_self_transition': axm_self_transition,
        'spectral_gap': spectral_gap,
        'mean_run_length': mean_run_length,
        'forbidden_violations': float(violations),
        'bigram_entropy': bigram_entropy,
        'fwd_rev_jsd': fwd_rev_jsd,
        'suffix_rate': suffix_rate,
        'prefix_entropy': prefix_entropy,
        'prefix_count': float(prefix_count),
        'bare_token_rate': bare_token_rate,
        'articulator_rate': articulator_rate,
        'mean_word_length': mean_word_length,
        'q0_axm_frac': q0_axm_frac,
        'q4_axm_frac': q4_axm_frac,
        'axm_gradient': axm_gradient,
        'opener_entropy': opener_entropy,
        'dark_middle_fraction': dark_middle_fraction,
        'bridge_middle_fraction': bridge_middle_fraction,
        'exclusive_b_fraction': exclusive_b_fraction,
        'k_fraction': k_fraction,
        'h_fraction': h_fraction,
        'e_fraction': e_fraction,
        'category_entropy': category_entropy,
        'dominant_category_fraction': dominant_category_fraction,
        'closer_rate': closer_rate,
    }


# ── Z-Score Computation ──────────────────────────────────────────────

def compute_z_scores(real_features, synthetic_features_list):
    """Compute per-feature z-scores for a real folio vs its synthetic distribution.

    Returns dict {feature_name: z_score} and composite anomaly (mean |z|).
    """
    z_scores = {}
    for feat in FEATURE_NAMES:
        real_val = real_features[feat]
        syn_vals = [sf[feat] for sf in synthetic_features_list]
        syn_mean = np.mean(syn_vals)
        syn_std = np.std(syn_vals)
        z = (real_val - syn_mean) / (syn_std + 1e-10)
        z_scores[feat] = float(z)

    # Exclude sanity-check features from composite
    z_for_composite = [abs(z_scores[f]) for f in FEATURE_NAMES if f not in EXCLUDED_FROM_ANALYSIS]
    composite = float(np.mean(z_for_composite))

    return z_scores, composite


# ── Landscape Analysis ───────────────────────────────────────────────

def analyze_landscape(all_z_scores, all_composites, folio_metadata, folio_regime):
    """Analyze the anomaly landscape across all folios."""
    print("\n=== Landscape Analysis ===")

    folios = sorted(all_z_scores.keys())
    n_folios = len(folios)

    # ── Per-feature statistics ───────────────────────────────────
    analysis_features = [f for f in FEATURE_NAMES if f not in EXCLUDED_FROM_ANALYSIS]
    feature_stats = {}
    for feat in analysis_features:
        z_vals = [all_z_scores[f][feat] for f in folios]
        abs_z = [abs(z) for z in z_vals]
        mean_abs_z = float(np.mean(abs_z))
        frac_gt_2 = sum(1 for z in abs_z if z > 2) / n_folios
        mean_z = float(np.mean(z_vals))
        direction = 'positive' if mean_z > 0 else 'negative'
        feature_stats[feat] = {
            'mean_abs_z': mean_abs_z,
            'fraction_z_gt_2': frac_gt_2,
            'mean_z': mean_z,
            'systematic_direction': direction,
        }

    # Rank features by mean |z|
    features_ranked = sorted(feature_stats.items(), key=lambda x: x[1]['mean_abs_z'], reverse=True)
    print("\nFeatures ranked by mean |z|:")
    for feat, stats in features_ranked[:10]:
        print(f"  {feat:30s}  mean|z|={stats['mean_abs_z']:.3f}  "
              f"frac>2={stats['fraction_z_gt_2']:.2f}  dir={stats['systematic_direction']}")

    # ── Composite anomaly statistics ─────────────────────────────
    composites = [all_composites[f] for f in folios]
    comp_stats = {
        'mean': float(np.mean(composites)),
        'std': float(np.std(composites)),
        'min': float(np.min(composites)),
        'max': float(np.max(composites)),
        'median': float(np.median(composites)),
    }
    print(f"\nComposite anomaly: mean={comp_stats['mean']:.3f}, "
          f"std={comp_stats['std']:.3f}, range=[{comp_stats['min']:.3f}, {comp_stats['max']:.3f}]")

    # ── Section breakdown ────────────────────────────────────────
    section_composites = defaultdict(list)
    for f in folios:
        section = folio_metadata.get(f, {}).get('section', 'UNK')
        section_composites[section].append(all_composites[f])

    anomaly_by_section = {}
    for section, vals in sorted(section_composites.items()):
        anomaly_by_section[section] = {
            'mean': float(np.mean(vals)),
            'n': len(vals),
        }
    print("\nAnomaly by section:")
    for section, stats in sorted(anomaly_by_section.items(), key=lambda x: x[1]['mean']):
        print(f"  {section:15s}  mean={stats['mean']:.3f}  n={stats['n']}")

    # ── REGIME breakdown ─────────────────────────────────────────
    regime_composites = defaultdict(list)
    for f in folios:
        regime = folio_metadata.get(f, {}).get('regime', folio_regime.get(f, 'UNK'))
        regime_composites[regime].append(all_composites[f])

    anomaly_by_regime = {}
    for regime, vals in sorted(regime_composites.items()):
        anomaly_by_regime[regime] = {
            'mean': float(np.mean(vals)),
            'n': len(vals),
        }
    print("\nAnomaly by REGIME:")
    for regime, stats in sorted(anomaly_by_regime.items()):
        print(f"  {regime:15s}  mean={stats['mean']:.3f}  n={stats['n']}")

    # ── Correlation with AXM self-transition ─────────────────────
    axm_vals = []
    comp_vals = []
    for f in folios:
        axm_self = folio_metadata.get(f, {}).get('axm_self')
        if axm_self is not None:
            axm_vals.append(axm_self)
            comp_vals.append(all_composites[f])

    if len(axm_vals) >= 5:
        rho, p = spearmanr(axm_vals, comp_vals)
        anomaly_vs_axm = {'rho': float(rho), 'p': float(p)}
        print(f"\nAnomaly vs AXM self-transition: rho={rho:.3f}, p={p:.4f}")
    else:
        anomaly_vs_axm = {'rho': None, 'p': None}

    # ── T3: C1048 BIO test ───────────────────────────────────────
    bio_composites = []
    non_bio_composites = []
    for f in folios:
        section = folio_metadata.get(f, {}).get('section', 'UNK')
        if section == 'B':  # BIO section
            bio_composites.append(all_composites[f])
        else:
            non_bio_composites.append(all_composites[f])

    if bio_composites and non_bio_composites:
        u_stat, mw_p = mannwhitneyu(bio_composites, non_bio_composites, alternative='less')
        c1048_test = {
            'bio_mean_anomaly': float(np.mean(bio_composites)),
            'non_bio_mean_anomaly': float(np.mean(non_bio_composites)),
            'bio_n': len(bio_composites),
            'non_bio_n': len(non_bio_composites),
            'mw_U': float(u_stat),
            'mw_p': float(mw_p),
            'bio_lower': float(np.mean(bio_composites)) < float(np.mean(non_bio_composites)),
        }
        print(f"\nC1048 BIO test: bio_mean={c1048_test['bio_mean_anomaly']:.3f}, "
              f"non_bio_mean={c1048_test['non_bio_mean_anomaly']:.3f}, "
              f"MW p={mw_p:.4f}, bio_lower={c1048_test['bio_lower']}")
    else:
        c1048_test = {'bio_mean_anomaly': None, 'non_bio_mean_anomaly': None,
                      'mw_p': None, 'bio_lower': None}

    # ── T4: C458 hazard-recovery asymmetry ───────────────────────
    hazard_z = []
    recovery_z = []
    for f in folios:
        for feat in HAZARD_FEATURES:
            hazard_z.append(abs(all_z_scores[f][feat]))
        for feat in RECOVERY_FEATURES:
            recovery_z.append(abs(all_z_scores[f][feat]))

    hazard_mean = float(np.mean(hazard_z))
    recovery_mean = float(np.mean(recovery_z))
    c458_test = {
        'hazard_feature_mean_abs_z': hazard_mean,
        'recovery_feature_mean_abs_z': recovery_mean,
        'ratio': recovery_mean / max(hazard_mean, 1e-10),
        'hazard_clamped_recovery_free': hazard_mean < recovery_mean,
    }
    print(f"\nC458 asymmetry: hazard_mean|z|={hazard_mean:.3f}, "
          f"recovery_mean|z|={recovery_mean:.3f}, "
          f"ratio={c458_test['ratio']:.2f}, "
          f"clamped/free={c458_test['hazard_clamped_recovery_free']}")

    # ── T5: Archetype correlation ────────────────────────────────
    arch_vals = []
    arch_comp = []
    for f in folios:
        arch = folio_metadata.get(f, {}).get('archetype')
        if arch is not None:
            arch_vals.append(arch)
            arch_comp.append(all_composites[f])

    archetype_composites = defaultdict(list)
    for a, c in zip(arch_vals, arch_comp):
        archetype_composites[a].append(c)

    anomaly_by_archetype = {}
    for arch, vals in sorted(archetype_composites.items()):
        anomaly_by_archetype[str(arch)] = {
            'mean': float(np.mean(vals)),
            'n': len(vals),
        }
    print("\nAnomaly by archetype:")
    for arch, stats in sorted(anomaly_by_archetype.items()):
        print(f"  Archetype {arch}  mean={stats['mean']:.3f}  n={stats['n']}")

    # ── Most/least anomalous folios ──────────────────────────────
    sorted_folios = sorted(folios, key=lambda f: all_composites[f], reverse=True)
    most_anomalous = [[f, all_composites[f]] for f in sorted_folios[:10]]
    least_anomalous = [[f, all_composites[f]] for f in sorted_folios[-10:]]

    print("\nMost anomalous folios:")
    for f, c in most_anomalous[:5]:
        section = folio_metadata.get(f, {}).get('section', '?')
        regime = folio_metadata.get(f, {}).get('regime', '?')
        print(f"  {f}  anomaly={c:.3f}  section={section}  regime={regime}")

    print("\nLeast anomalous folios:")
    for f, c in least_anomalous[-5:]:
        section = folio_metadata.get(f, {}).get('section', '?')
        regime = folio_metadata.get(f, {}).get('regime', '?')
        print(f"  {f}  anomaly={c:.3f}  section={section}  regime={regime}")

    # ── Systematic gap features (mean|z| > 1.5) ─────────────────
    systematic_gaps = [feat for feat, stats in feature_stats.items()
                       if stats['mean_abs_z'] > 1.5]
    print(f"\nSystematic gap features (mean|z| > 1.5): {len(systematic_gaps)}")
    for feat in systematic_gaps:
        print(f"  {feat}: mean|z|={feature_stats[feat]['mean_abs_z']:.3f}")

    # ── T1: Feature normality (fraction with z < 2) ─────────────
    total_feature_slots = n_folios * len(analysis_features)
    within_2 = sum(1 for f in folios for feat in analysis_features
                   if abs(all_z_scores[f][feat]) < 2)
    normality_fraction = within_2 / total_feature_slots
    print(f"\nT1 Feature normality: {normality_fraction:.1%} of folio-feature pairs have |z| < 2")

    return {
        'feature_analysis': feature_stats,
        'features_ranked_by_gap': [[f, s['mean_abs_z']] for f, s in features_ranked],
        'composite_anomaly_stats': comp_stats,
        'anomaly_by_section': anomaly_by_section,
        'anomaly_by_regime': anomaly_by_regime,
        'anomaly_by_archetype': anomaly_by_archetype,
        'anomaly_vs_axm_self': anomaly_vs_axm,
        'c1048_bio_test': c1048_test,
        'c458_asymmetry_test': c458_test,
        'most_anomalous_folios': most_anomalous,
        'least_anomalous_folios': least_anomalous,
        'systematic_gap_features': systematic_gaps,
        'normality_fraction': normality_fraction,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()

    # Step 1: Load data
    params = load_data()

    # Step 2: Build M2.1 parameters
    print("\nBuilding M2.1 parameters...")
    forbidden_pairs = build_symmetric_forbidden(params)
    quintile_matrices = build_m21_matrices(params['quintile_trans'], forbidden_pairs)

    # Step 3: Compute real folio features
    print("\nComputing real folio features...")
    folio_lines = params['folio_lines']
    valid_folios = sorted(folio_lines.keys())
    print(f"  {len(valid_folios)} folios")

    real_features = {}
    for folio in valid_folios:
        real_features[folio] = compute_folio_features(folio_lines[folio], params)

    # Step 4: Generate synthetic folios and compute z-scores
    print(f"\nGenerating {N_SYNTHETIC} synthetic folios per real folio...")
    all_z_scores = {}
    all_composites = {}
    per_folio_data = {}

    for fi, folio in enumerate(valid_folios):
        lines = folio_lines[folio]
        line_lengths = [len(line) for line in lines]
        n_tokens = sum(line_lengths)

        # Generate N_SYNTHETIC synthetic counterparts
        syn_features_list = []
        for si in range(N_SYNTHETIC):
            rng = np.random.RandomState(SEED + fi * 10000 + si)
            syn_lines = generate_synthetic_folio(
                line_lengths, quintile_matrices, params['opener_probs'],
                params['class_token_probs'], params['token_morph_cache'], rng
            )
            syn_feat = compute_folio_features(syn_lines, params)
            syn_features_list.append(syn_feat)

        # Compute z-scores
        z_scores, composite = compute_z_scores(real_features[folio], syn_features_list)
        all_z_scores[folio] = z_scores
        all_composites[folio] = composite

        # Top anomalous features for this folio
        sorted_z = sorted(z_scores.items(), key=lambda x: abs(x[1]), reverse=True)
        top_anomalous = [[feat, z] for feat, z in sorted_z[:5]]

        meta = params['folio_metadata'].get(folio, {})
        per_folio_data[folio] = {
            'n_tokens': n_tokens,
            'n_lines': len(lines),
            'regime': meta.get('regime', params['folio_regime'].get(folio, 'UNK')),
            'section': meta.get('section', 'UNK'),
            'archetype': meta.get('archetype'),
            'real_features': real_features[folio],
            'z_scores': z_scores,
            'composite_anomaly': composite,
            'top_anomalous_features': top_anomalous,
        }

        if (fi + 1) % 10 == 0 or fi == 0:
            print(f"  [{fi+1}/{len(valid_folios)}] {folio}: anomaly={composite:.3f} "
                  f"(n={n_tokens}, top={top_anomalous[0][0]}={top_anomalous[0][1]:.2f})")

    # Step 5: Landscape analysis
    landscape = analyze_landscape(all_z_scores, all_composites,
                                  params['folio_metadata'], params['folio_regime'])

    # Step 6: Build verdict
    systematic_gaps = landscape['systematic_gap_features']
    c1048_pass = landscape['c1048_bio_test'].get('bio_lower', False)
    c458_pass = landscape['c458_asymmetry_test'].get('hazard_clamped_recovery_free', False)
    normality = landscape['normality_fraction']

    verdict_parts = []
    if systematic_gaps:
        verdict_parts.append(f"M2.1 gap concentrates in {len(systematic_gaps)} features: "
                             f"{', '.join(systematic_gaps[:5])}")
    else:
        verdict_parts.append("No systematic gaps (mean|z| > 1.5) found")

    if c1048_pass:
        verdict_parts.append("C1048 confirmed: BIO lower anomaly")
    else:
        verdict_parts.append("C1048 not confirmed: BIO not lower anomaly")

    if c458_pass:
        verdict_parts.append("C458 confirmed: hazard clamped, recovery free")
    else:
        verdict_parts.append("C458 not confirmed in generative gap")

    verdict_parts.append(f"{normality:.1%} of feature-folio pairs within |z|<2")

    verdict = "; ".join(verdict_parts)
    print(f"\n{'='*60}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Step 7: Save results
    results = {
        'metadata': {
            'phase': 479,
            'name': 'GENERATIVE_GAP_CHARACTERIZATION',
            'n_folios': len(valid_folios),
            'n_synthetic_per_folio': N_SYNTHETIC,
            'n_features': len(FEATURE_NAMES),
            'feature_names': FEATURE_NAMES,
            'seed': SEED,
            'model': 'M2.1 (49-class quintile-conditioned Markov + symmetric forbidden)',
            'elapsed_seconds': elapsed,
        },
        'per_folio': per_folio_data,
        'landscape': landscape,
        'verdict': verdict,
    }

    out_path = RESULTS_DIR / 'generative_gap_characterization.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
