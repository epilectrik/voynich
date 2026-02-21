#!/usr/bin/env python3
"""
Phase 411: SECTION_CONDITIONED_GENERATIVE_FIDELITY
====================================================
Tests whether section-conditioned M2 captures folio-level structural
variation, or whether inter-folio heterogeneity within a section is
program-specific design freedom that no section model can reproduce.

5-test battery:
  T1: INTER_FOLIO_VARIANCE_RATIO (real vs synthetic JSD spread)
  T2: AXM_RESIDUAL_REDUCTION (per-folio AXM SD comparison)
  T3: KERNEL_PROFILE_CAPTURE (k/h/e variance reproduction)
  T4: FOLIO_FIDELITY_IMPROVEMENT (global-M2 vs section-M2 per folio)
  T5: DESIGN_FREEDOM_QUANTIFICATION (aggregated residual)

Depends on: C1016, C1029, C1035, C1047, C1055, C1150
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

# ── Constants (from Phase 348/370) ──────────────────────────────────

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
MIN_FOLIO_TOKENS = 30  # Minimum tokens for folio-level analysis

KERNEL_CHARS = {'k', 'h', 'e'}

SECTION_NAMES = {
    'B': 'BIO', 'H': 'HERBAL_B', 'S': 'STARS_RECIPE', 'C': 'COSMO',
    'P': 'PHARMA', 'R': 'RECIPE_B',
}


# ── Utilities ───────────────────────────────────────────────────────

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


def jsd(p, q):
    """Jensen-Shannon divergence between two distributions."""
    p = np.asarray(p, dtype=float) + 1e-12
    q = np.asarray(q, dtype=float) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * scipy_entropy(p, m, base=2) +
                 0.5 * scipy_entropy(q, m, base=2))


def kl_divergence(p, q):
    """KL(p || q) with smoothing."""
    p = np.asarray(p, dtype=float) + 1e-12
    q = np.asarray(q, dtype=float) + 1e-12
    p = p / p.sum()
    q = q / q.sum()
    return float(scipy_entropy(p, q, base=2))


def class_distribution(tokens, n_classes=N_CLASSES):
    """Compute normalized 49-class distribution from token dicts."""
    dist = np.zeros(n_classes)
    for t in tokens:
        cls = t['cls'] if isinstance(t, dict) else t
        if 1 <= cls <= n_classes:
            dist[cls - 1] += 1
    total = dist.sum()
    if total > 0:
        dist /= total
    return dist


def mean_pairwise_jsd(distributions):
    """Mean pairwise JSD between a list of distributions."""
    n = len(distributions)
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += jsd(distributions[i], distributions[j])
            count += 1
    return total / count


def round_floats(obj, digits=6):
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    return obj


# ── Data Loading ────────────────────────────────────────────────────

def load_data():
    """Load all data, partition by section and folio, build params."""
    print("Loading data...")

    # Token -> class map
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

    # Build real token stream with section + folio tracking
    section_lines = defaultdict(list)        # section -> [lines]
    section_folio_lines = defaultdict(lambda: defaultdict(list))  # section -> folio -> [lines]
    global_lines = []
    current_line = []
    current_section = None
    current_folio = None
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
        folio = token.folio

        if key != prev_key and current_line:
            global_lines.append(current_line)
            if current_section:
                section_lines[current_section].append(current_line)
                section_folio_lines[current_section][current_folio].append(current_line)
            current_line = []
        prev_key = key
        current_section = sec
        current_folio = folio

        m = morph.extract(token.word)
        current_line.append({
            'word': token.word,
            'cls': cls,
            'state': CLASS_TO_STATE.get(cls, 'UNK'),
            'role': CLASS_TO_ROLE.get(cls, 'UNK'),
            'prefix': m.prefix if m else None,
            'middle': m.middle if m else token.word,
            'suffix': m.suffix if m else None,
            'folio': folio,
            'line': token.line,
            'section': sec,
        })
    if current_line:
        global_lines.append(current_line)
        if current_section:
            section_lines[current_section].append(current_line)
            section_folio_lines[current_section][current_folio].append(current_line)

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

        # Class -> token probs (section-specific)
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

    # Report
    print(f"  Global: {len(global_tokens)} tokens in {len(global_lines)} lines")
    for sec in sorted(section_params.keys()):
        n_folios = len(section_folio_lines[sec])
        n_tok = len(section_tokens[sec])
        print(f"  Section {sec} ({SECTION_NAMES.get(sec, sec)}): {n_tok} tokens, {n_folios} folios")

    return (global_params, global_tokens, global_lines,
            section_params, section_tokens, section_lines,
            dict(section_folio_lines), morph)


# ── M2 Generation (from Phase 348/370) ─────────────────────────────

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


def generate_synthetic_folios(params, real_folio_lines, rng, morph):
    """Generate one M2 corpus partitioned into folio-sized chunks.

    real_folio_lines: {folio: [lines]} for this section.
    Returns: {folio: [token_dicts]} flat token list per folio.
    """
    # Collect all line lengths in folio order
    folio_order = sorted(real_folio_lines.keys())
    folio_n_lines = {}
    all_line_lengths = []
    for folio in folio_order:
        lines = real_folio_lines[folio]
        folio_n_lines[folio] = len(lines)
        for line in lines:
            all_line_lengths.append(len(line))

    # Generate all lines at once
    corpus = generate_m2(params, rng,
                         override_n_lines=len(all_line_lengths),
                         override_line_lengths=all_line_lengths)

    # Add morphology to generated tokens
    for line in corpus:
        for t in line:
            m = morph.extract(t['word'])
            t['middle'] = m.middle if m else t['word']
            t['state'] = CLASS_TO_STATE.get(t['cls'], 'UNK')

    # Partition into folio-sized chunks
    synthetic_folios = {}
    idx = 0
    for folio in folio_order:
        n = folio_n_lines[folio]
        folio_tokens = []
        for line in corpus[idx:idx + n]:
            folio_tokens.extend(line)
        synthetic_folios[folio] = folio_tokens
        idx += n

    return synthetic_folios


# ── Folio-Level Metrics ─────────────────────────────────────────────

def folio_axm_self_transition(tokens):
    """Compute AXM self-transition rate from a flat token list.
    Uses sequential pairs (approximation — no line breaks tracked)."""
    axm_total = 0
    axm_self = 0
    for i in range(len(tokens) - 1):
        s1 = CLASS_TO_STATE.get(tokens[i]['cls'] if isinstance(tokens[i], dict) else tokens[i])
        s2 = CLASS_TO_STATE.get(tokens[i+1]['cls'] if isinstance(tokens[i+1], dict) else tokens[i+1])
        if s1 == 'AXM':
            axm_total += 1
            if s2 == 'AXM':
                axm_self += 1
    return axm_self / max(axm_total, 1)


def folio_kernel_fracs(tokens, morph):
    """Compute k/h/e kernel fractions for a flat token list."""
    counts = {'k': 0, 'h': 0, 'e': 0}
    for t in tokens:
        mid = t.get('middle') if isinstance(t, dict) else None
        if mid is None:
            m = morph.extract(t['word'] if isinstance(t, dict) else t)
            mid = m.middle if m else ''
        for ch in mid:
            if ch in KERNEL_CHARS:
                counts[ch] += 1
    total = counts['k'] + counts['h'] + counts['e']
    if total == 0:
        return {'k_frac': 0, 'h_frac': 0, 'e_frac': 0}
    return {
        'k_frac': counts['k'] / total,
        'h_frac': counts['h'] / total,
        'e_frac': counts['e'] / total,
    }


# ── Test 1: Inter-Folio Variance Ratio ─────────────────────────────

def test1_inter_folio_variance_ratio(section_params, section_folio_lines, morph):
    """T1: Compare real vs synthetic inter-folio class distribution variance."""
    print("\n── Test 1: INTER_FOLIO_VARIANCE_RATIO ──")

    viable_sections = {}
    for sec, folio_lines in section_folio_lines.items():
        # Filter to folios with enough tokens
        viable = {}
        for folio, lines in folio_lines.items():
            n_tok = sum(len(line) for line in lines)
            if n_tok >= MIN_FOLIO_TOKENS:
                viable[folio] = lines
        if len(viable) >= 3 and sec in section_params:
            viable_sections[sec] = viable

    results = {}
    for sec in sorted(viable_sections.keys()):
        folio_lines = viable_sections[sec]
        n_folios = len(folio_lines)

        # Real per-folio class distributions
        real_dists = []
        for folio in sorted(folio_lines.keys()):
            tokens = [t for line in folio_lines[folio] for t in line]
            real_dists.append(class_distribution(tokens))
        real_mpjsd = mean_pairwise_jsd(real_dists)

        # Synthetic: N_INST instantiations
        synth_mpjsds = []
        for inst in range(N_INST):
            rng = np.random.RandomState(42 + inst)
            synth_folios = generate_synthetic_folios(
                section_params[sec], folio_lines, rng, morph)

            synth_dists = []
            for folio in sorted(synth_folios.keys()):
                tokens = synth_folios[folio]
                if len(tokens) >= MIN_FOLIO_TOKENS:
                    synth_dists.append(class_distribution(tokens))
            if len(synth_dists) >= 3:
                synth_mpjsds.append(mean_pairwise_jsd(synth_dists))

        synth_mean = float(np.mean(synth_mpjsds)) if synth_mpjsds else 0
        synth_std = float(np.std(synth_mpjsds)) if synth_mpjsds else 0
        ratio = real_mpjsd / max(synth_mean, 1e-10)

        results[sec] = {
            'section_name': SECTION_NAMES.get(sec, sec),
            'n_folios': n_folios,
            'real_mpjsd': round(real_mpjsd, 6),
            'synth_mpjsd_mean': round(synth_mean, 6),
            'synth_mpjsd_std': round(synth_std, 6),
            'ratio': round(ratio, 3),
        }
        print(f"  {sec} ({SECTION_NAMES.get(sec, sec)}): "
              f"real={real_mpjsd:.4f}, synth={synth_mean:.4f}, ratio={ratio:.2f}x "
              f"({n_folios} folios)")

    # Aggregate
    ratios = [r['ratio'] for r in results.values()]
    mean_ratio = float(np.mean(ratios)) if ratios else 0

    if mean_ratio > 2.0:
        verdict = 'SECTION_INSUFFICIENT'
    elif mean_ratio < 1.5:
        verdict = 'SECTION_CAPTURES'
    else:
        verdict = 'SECTION_PARTIAL'

    print(f"  Mean ratio: {mean_ratio:.2f}x -> {verdict}")

    return {
        'per_section': results,
        'mean_ratio': round(mean_ratio, 3),
        'verdict': verdict,
    }


# ── Test 2: AXM Residual Reduction ─────────────────────────────────

def test2_axm_residual_reduction(section_params, section_folio_lines, morph):
    """T2: Does section-M2 reproduce folio-level AXM self-transition spread?"""
    print("\n── Test 2: AXM_RESIDUAL_REDUCTION ──")

    viable_sections = {}
    for sec, folio_lines in section_folio_lines.items():
        viable = {}
        for folio, lines in folio_lines.items():
            n_tok = sum(len(line) for line in lines)
            if n_tok >= MIN_FOLIO_TOKENS:
                viable[folio] = lines
        if len(viable) >= 3 and sec in section_params:
            viable_sections[sec] = viable

    results = {}
    for sec in sorted(viable_sections.keys()):
        folio_lines = viable_sections[sec]

        # Real per-folio AXM self-transition rates
        real_axm = []
        for folio in sorted(folio_lines.keys()):
            tokens = [t for line in folio_lines[folio] for t in line]
            real_axm.append(folio_axm_self_transition(tokens))
        real_sd = float(np.std(real_axm))
        real_mean = float(np.mean(real_axm))

        # Synthetic
        synth_sds = []
        for inst in range(N_INST):
            rng = np.random.RandomState(42 + inst)
            synth_folios = generate_synthetic_folios(
                section_params[sec], folio_lines, rng, morph)

            synth_axm = []
            for folio in sorted(synth_folios.keys()):
                tokens = synth_folios[folio]
                if len(tokens) >= MIN_FOLIO_TOKENS:
                    synth_axm.append(folio_axm_self_transition(tokens))
            if len(synth_axm) >= 3:
                synth_sds.append(float(np.std(synth_axm)))

        synth_sd_mean = float(np.mean(synth_sds)) if synth_sds else 0
        ratio = real_sd / max(synth_sd_mean, 1e-10)

        results[sec] = {
            'section_name': SECTION_NAMES.get(sec, sec),
            'n_folios': len(folio_lines),
            'real_axm_mean': round(real_mean, 4),
            'real_axm_sd': round(real_sd, 4),
            'synth_axm_sd_mean': round(synth_sd_mean, 4),
            'ratio': round(ratio, 3),
        }
        print(f"  {sec}: real AXM SD={real_sd:.4f}, synth SD={synth_sd_mean:.4f}, "
              f"ratio={ratio:.2f}x")

    ratios = [r['ratio'] for r in results.values()]
    mean_ratio = float(np.mean(ratios)) if ratios else 0

    if mean_ratio > 1.5:
        verdict = 'AXM_UNCAPTURED'
    elif mean_ratio > 1.2:
        verdict = 'AXM_PARTIAL'
    else:
        verdict = 'AXM_CAPTURED'

    print(f"  Mean ratio: {mean_ratio:.2f}x -> {verdict}")

    return {
        'per_section': results,
        'mean_ratio': round(mean_ratio, 3),
        'verdict': verdict,
    }


# ── Test 3: Kernel Profile Capture ─────────────────────────────────

def test3_kernel_profile_capture(section_params, section_folio_lines, morph):
    """T3: Does section-M2 reproduce folio-level kernel fraction variance?"""
    print("\n── Test 3: KERNEL_PROFILE_CAPTURE ──")

    viable_sections = {}
    for sec, folio_lines in section_folio_lines.items():
        viable = {}
        for folio, lines in folio_lines.items():
            n_tok = sum(len(line) for line in lines)
            if n_tok >= MIN_FOLIO_TOKENS:
                viable[folio] = lines
        if len(viable) >= 3 and sec in section_params:
            viable_sections[sec] = viable

    results = {}
    for sec in sorted(viable_sections.keys()):
        folio_lines = viable_sections[sec]

        # Real per-folio kernel fractions
        real_k, real_h, real_e = [], [], []
        for folio in sorted(folio_lines.keys()):
            tokens = [t for line in folio_lines[folio] for t in line]
            kf = folio_kernel_fracs(tokens, morph)
            real_k.append(kf['k_frac'])
            real_h.append(kf['h_frac'])
            real_e.append(kf['e_frac'])

        real_sd_k = float(np.std(real_k))
        real_sd_h = float(np.std(real_h))
        real_sd_e = float(np.std(real_e))

        # Synthetic
        synth_sd_ks, synth_sd_hs, synth_sd_es = [], [], []
        for inst in range(N_INST):
            rng = np.random.RandomState(42 + inst)
            synth_folios = generate_synthetic_folios(
                section_params[sec], folio_lines, rng, morph)

            sk, sh, se = [], [], []
            for folio in sorted(synth_folios.keys()):
                tokens = synth_folios[folio]
                if len(tokens) >= MIN_FOLIO_TOKENS:
                    kf = folio_kernel_fracs(tokens, morph)
                    sk.append(kf['k_frac'])
                    sh.append(kf['h_frac'])
                    se.append(kf['e_frac'])
            if len(sk) >= 3:
                synth_sd_ks.append(float(np.std(sk)))
                synth_sd_hs.append(float(np.std(sh)))
                synth_sd_es.append(float(np.std(se)))

        synth_k_mean = float(np.mean(synth_sd_ks)) if synth_sd_ks else 0
        synth_h_mean = float(np.mean(synth_sd_hs)) if synth_sd_hs else 0
        synth_e_mean = float(np.mean(synth_sd_es)) if synth_sd_es else 0

        ratio_k = real_sd_k / max(synth_k_mean, 1e-10)
        ratio_h = real_sd_h / max(synth_h_mean, 1e-10)
        ratio_e = real_sd_e / max(synth_e_mean, 1e-10)

        results[sec] = {
            'section_name': SECTION_NAMES.get(sec, sec),
            'n_folios': len(folio_lines),
            'real_sd': {'k': round(real_sd_k, 4), 'h': round(real_sd_h, 4), 'e': round(real_sd_e, 4)},
            'synth_sd_mean': {'k': round(synth_k_mean, 4), 'h': round(synth_h_mean, 4), 'e': round(synth_e_mean, 4)},
            'ratio': {'k': round(ratio_k, 3), 'h': round(ratio_h, 3), 'e': round(ratio_e, 3)},
        }
        print(f"  {sec}: k ratio={ratio_k:.2f}x, h ratio={ratio_h:.2f}x, e ratio={ratio_e:.2f}x")

    # Aggregate: mean ratio across sections and kernels
    all_ratios = []
    for sec_r in results.values():
        for k_type in ['k', 'h', 'e']:
            all_ratios.append(sec_r['ratio'][k_type])
    mean_ratio = float(np.mean(all_ratios)) if all_ratios else 0

    if mean_ratio > 1.5:
        verdict = 'KERNEL_UNCAPTURED'
    elif mean_ratio > 1.2:
        verdict = 'KERNEL_PARTIAL'
    else:
        verdict = 'KERNEL_CAPTURED'

    print(f"  Mean ratio: {mean_ratio:.2f}x -> {verdict}")

    return {
        'per_section': results,
        'mean_ratio': round(mean_ratio, 3),
        'verdict': verdict,
    }


# ── Test 4: Folio Fidelity Improvement ─────────────────────────────

def test4_folio_fidelity_improvement(global_params, section_params,
                                     section_folio_lines, morph):
    """T4: Per-folio KL from global-M2 vs section-M2 class distribution."""
    print("\n── Test 4: FOLIO_FIDELITY_IMPROVEMENT ──")

    # Compute global-M2 average class distribution (over N_INST)
    global_dists = []
    for inst in range(N_INST):
        rng = np.random.RandomState(1000 + inst)
        corpus = generate_m2(global_params, rng)
        all_tokens = [t for line in corpus for t in line]
        global_dists.append(class_distribution(all_tokens))
    global_mean_dist = np.mean(global_dists, axis=0)

    # Compute per-section M2 average class distribution
    section_mean_dists = {}
    for sec in sorted(section_params.keys()):
        sec_dists = []
        for inst in range(N_INST):
            rng = np.random.RandomState(2000 + inst)
            corpus = generate_m2(section_params[sec], rng)
            all_tokens = [t for line in corpus for t in line]
            sec_dists.append(class_distribution(all_tokens))
        section_mean_dists[sec] = np.mean(sec_dists, axis=0)

    # Per-folio comparison
    improvements = []
    per_section_improvements = defaultdict(list)
    folio_details = {}

    for sec, folio_lines in section_folio_lines.items():
        if sec not in section_mean_dists:
            continue
        for folio, lines in folio_lines.items():
            tokens = [t for line in lines for t in line]
            if len(tokens) < MIN_FOLIO_TOKENS:
                continue

            folio_dist = class_distribution(tokens)
            kl_global = kl_divergence(folio_dist, global_mean_dist)
            kl_section = kl_divergence(folio_dist, section_mean_dists[sec])
            improvement = kl_global - kl_section  # positive = section better

            improvements.append(improvement)
            per_section_improvements[sec].append(improvement)
            folio_details[folio] = {
                'section': sec,
                'kl_global': round(kl_global, 6),
                'kl_section': round(kl_section, 6),
                'improvement': round(improvement, 6),
                'section_better': improvement > 0,
            }

    n_improved = sum(1 for x in improvements if x > 0)
    frac_improved = n_improved / max(len(improvements), 1)
    mean_improvement = float(np.mean(improvements)) if improvements else 0

    # Per-section summary
    per_section = {}
    for sec in sorted(per_section_improvements.keys()):
        imps = per_section_improvements[sec]
        n_imp = sum(1 for x in imps if x > 0)
        per_section[sec] = {
            'section_name': SECTION_NAMES.get(sec, sec),
            'n_folios': len(imps),
            'n_improved': n_imp,
            'frac_improved': round(n_imp / max(len(imps), 1), 3),
            'mean_improvement': round(float(np.mean(imps)), 6),
        }
        print(f"  {sec}: {n_imp}/{len(imps)} improved "
              f"({n_imp/max(len(imps),1)*100:.0f}%), "
              f"mean KL improvement={float(np.mean(imps)):.4f}")

    if frac_improved > 0.7:
        verdict = 'SECTION_HELPS'
    elif frac_improved > 0.5:
        verdict = 'SECTION_MARGINAL'
    else:
        verdict = 'SECTION_NO_HELP'

    print(f"  Overall: {n_improved}/{len(improvements)} improved "
          f"({frac_improved*100:.0f}%) -> {verdict}")

    return {
        'per_section': per_section,
        'total_folios': len(improvements),
        'n_improved': n_improved,
        'frac_improved': round(frac_improved, 3),
        'mean_improvement': round(mean_improvement, 6),
        'verdict': verdict,
    }


# ── Test 5: Design Freedom Quantification ──────────────────────────

def test5_design_freedom_quantification(t1, t2, t3):
    """T5: Aggregate design freedom lower bound from T1-T3."""
    print("\n── Test 5: DESIGN_FREEDOM_QUANTIFICATION ──")

    # Uncaptured fraction = 1 - 1/ratio (ratio > 1 means uncaptured)
    # Clamp to [0, 1]
    def uncaptured(ratio):
        if ratio <= 1.0:
            return 0.0
        return 1.0 - 1.0 / ratio

    # T1: class distribution variance
    t1_uncaptured = uncaptured(t1['mean_ratio'])

    # T2: AXM spread
    t2_uncaptured = uncaptured(t2['mean_ratio'])

    # T3: kernel profile variance (mean across k/h/e)
    t3_uncaptured = uncaptured(t3['mean_ratio'])

    # Aggregate
    design_freedom = float(np.mean([t1_uncaptured, t2_uncaptured, t3_uncaptured]))

    print(f"  T1 uncaptured (class dist): {t1_uncaptured:.3f}")
    print(f"  T2 uncaptured (AXM spread): {t2_uncaptured:.3f}")
    print(f"  T3 uncaptured (kernel):     {t3_uncaptured:.3f}")
    print(f"  Design freedom estimate:    {design_freedom:.3f}")
    print(f"  C1016 residual:             0.663")
    print(f"  C1035 AXM residual:         0.570")

    if design_freedom > 0.5:
        verdict = 'PROGRAM_SPECIFIC_CONFIRMED'
    elif design_freedom > 0.3:
        verdict = 'PARTIALLY_PROGRAM_SPECIFIC'
    else:
        verdict = 'SECTION_DOMINANT'

    # Consistency check
    c1016_consistent = abs(design_freedom - 0.663) < 0.25
    c1035_consistent = abs(design_freedom - 0.570) < 0.25

    print(f"  Verdict: {verdict}")
    print(f"  C1016 consistent: {c1016_consistent}")
    print(f"  C1035 consistent: {c1035_consistent}")

    return {
        't1_uncaptured': round(t1_uncaptured, 4),
        't2_uncaptured': round(t2_uncaptured, 4),
        't3_uncaptured': round(t3_uncaptured, 4),
        'design_freedom': round(design_freedom, 4),
        'c1016_residual': 0.663,
        'c1035_residual': 0.570,
        'c1016_consistent': c1016_consistent,
        'c1035_consistent': c1035_consistent,
        'verdict': verdict,
    }


# ── Synthesis ───────────────────────────────────────────────────────

def synthesize(t1, t2, t3, t4, t5):
    """Combine all test results into overall verdict."""
    print("\n── SYNTHESIS ──")

    # Scoring
    score = 0.0

    # T1: ratio < 1.5 = captures (1pt), 1.5-2.0 = partial (0.5pt), > 2.0 = insufficient (0pt)
    if t1['mean_ratio'] < 1.5:
        t1_score = 1.0
    elif t1['mean_ratio'] < 2.0:
        t1_score = 0.5
    else:
        t1_score = 0.0

    # T2: ratio < 1.2 = captured (1pt), 1.2-1.5 = partial (0.5pt), > 1.5 = uncaptured (0pt)
    if t2['mean_ratio'] < 1.2:
        t2_score = 1.0
    elif t2['mean_ratio'] < 1.5:
        t2_score = 0.5
    else:
        t2_score = 0.0

    # T3: same as T2
    if t3['mean_ratio'] < 1.2:
        t3_score = 1.0
    elif t3['mean_ratio'] < 1.5:
        t3_score = 0.5
    else:
        t3_score = 0.0

    # T4: frac > 0.7 = helps (1pt), 0.5-0.7 = marginal (0.5pt), < 0.5 = no help (0pt)
    if t4['frac_improved'] > 0.7:
        t4_score = 1.0
    elif t4['frac_improved'] > 0.5:
        t4_score = 0.5
    else:
        t4_score = 0.0

    # T5: freedom < 0.3 = section dominant (1pt), 0.3-0.5 = partial (0.5pt), > 0.5 = program (0pt)
    if t5['design_freedom'] < 0.3:
        t5_score = 1.0
    elif t5['design_freedom'] < 0.5:
        t5_score = 0.5
    else:
        t5_score = 0.0

    score = t1_score + t2_score + t3_score + t4_score + t5_score

    if score <= 1.0:
        overall = 'PROGRAM_SPECIFIC_DOMINATES'
    elif score <= 3.0:
        overall = 'SECTION_PARTIALLY_CAPTURES'
    else:
        overall = 'SECTION_SUFFICIENT'

    scores = {
        't1_inter_folio_variance': t1_score,
        't2_axm_residual': t2_score,
        't3_kernel_profile': t3_score,
        't4_folio_fidelity': t4_score,
        't5_design_freedom': t5_score,
        'total': score,
        'max': 5.0,
    }

    print(f"  T1={t1_score} T2={t2_score} T3={t3_score} T4={t4_score} T5={t5_score}")
    print(f"  Total: {score}/5.0")
    print(f"  Overall: {overall}")

    return {
        'scores': scores,
        'overall': overall,
        'test_verdicts': {
            't1': t1['verdict'],
            't2': t2['verdict'],
            't3': t3['verdict'],
            't4': t4['verdict'],
            't5': t5['verdict'],
        },
    }


# ── Main ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 411: SECTION_CONDITIONED_GENERATIVE_FIDELITY")
    print("=" * 60)

    (global_params, global_tokens, global_lines,
     section_params, section_tokens, section_lines,
     section_folio_lines, morph) = load_data()

    # Run 5-test battery
    t1 = test1_inter_folio_variance_ratio(section_params, section_folio_lines, morph)
    t2 = test2_axm_residual_reduction(section_params, section_folio_lines, morph)
    t3 = test3_kernel_profile_capture(section_params, section_folio_lines, morph)
    t4 = test4_folio_fidelity_improvement(global_params, section_params,
                                          section_folio_lines, morph)
    t5 = test5_design_freedom_quantification(t1, t2, t3)

    verdicts = synthesize(t1, t2, t3, t4, t5)

    # Save
    output = round_floats({
        'phase': 'SECTION_CONDITIONED_GENERATIVE_FIDELITY',
        'phase_number': 411,
        'depends_on': ['C1016', 'C1029', 'C1035', 'C1047', 'C1055', 'C1150'],
        'test1_inter_folio_variance_ratio': t1,
        'test2_axm_residual_reduction': t2,
        'test3_kernel_profile_capture': t3,
        'test4_folio_fidelity_improvement': t4,
        'test5_design_freedom_quantification': t5,
        'synthesis': verdicts,
    })

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'section_conditioned_fidelity.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
