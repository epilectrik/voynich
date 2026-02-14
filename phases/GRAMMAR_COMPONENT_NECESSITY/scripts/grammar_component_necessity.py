#!/usr/bin/env python3
"""
Phase 349: GRAMMAR_COMPONENT_NECESSITY
========================================
Phase 348 proved SUFFICIENCY — M2 (49-class Markov + forbidden suppression)
regenerates 80% of measurable structure. This phase proves NECESSITY:
which grammar components are load-bearing for which structural properties?

5 ablation conditions on the real Currier B corpus:
  (a) forbidden_injection:      Inject forbidden class pairs at random positions
  (b) forbidden_subset:         Inject only top-frequency forbidden pairs (7/17)
  (c) class_shuffle_in_state:   Shuffle class assignments within macro-state per line
  (d) class_shuffle_in_role:    Shuffle class assignments within role per line
  (e) token_shuffle_in_class:   Randomize token choice within class, keep class sequence

10 topology-sensitive metrics (replacing Phase 348's weak marginal battery).
100 shuffle instantiations per ablation.
100 bootstrap resamples for real corpus sigma.
Break threshold: ablated metric deviates > 2 sigma from real.

Depends on: C1025 (generative sufficiency), C109 (forbidden transitions),
            C121 (49 classes), C1010 (6-state macro), C789 (forbidden permeability),
            C971 (depletion asymmetry), C967 (hazard gate), C786 (FL forward bias)
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

np.random.seed(349)

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

N_CLASSES = 49
N_SHUFFLES = 100
N_BOOTSTRAP = 100


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load real B corpus and forbidden pair information."""
    print("Loading data...")

    # Token -> class map
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
    forbidden_middle_pairs = []
    for t in forbidden_inv['transitions']:
        forbidden_middle_pairs.append((t['source'], t['target']))

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
            'folio': token.folio,
            'line': token.line,
        })
    if current_line:
        lines.append(current_line)

    all_tokens = [t for line in lines for t in line]
    print(f"  {len(all_tokens)} tokens in {len(lines)} lines")

    # Map forbidden MIDDLE pairs to forbidden CLASS pairs
    middle_to_classes = defaultdict(set)
    for t in all_tokens:
        mid = t['middle'] if t['middle'] else ''
        middle_to_classes[mid].add(t['cls'])

    forbidden_class_pairs = set()
    for src_mid, tgt_mid in forbidden_middle_pairs:
        for sc in middle_to_classes.get(src_mid, set()):
            for tc in middle_to_classes.get(tgt_mid, set()):
                forbidden_class_pairs.add((sc, tc))

    print(f"  {len(forbidden_middle_pairs)} forbidden MIDDLE pairs -> {len(forbidden_class_pairs)} forbidden class pairs")

    # Count how often each forbidden class pair is "approached" in real data
    # (i.e., source class appears and could transition to target)
    forbidden_pair_freq = Counter()
    for line in lines:
        for i in range(len(line) - 1):
            pair = (line[i]['cls'], line[i+1]['cls'])
            if pair in forbidden_class_pairs:
                forbidden_pair_freq[pair] += 1
            # Count approaches: source class has at least one forbidden successor
            for fp in forbidden_class_pairs:
                if fp[0] == line[i]['cls']:
                    forbidden_pair_freq[('approach', fp)] += 1

    # Sort forbidden pairs by approach frequency for subset ablation
    approach_counts = {}
    for fp in forbidden_class_pairs:
        approach_counts[fp] = sum(1 for line in lines for i in range(len(line)-1)
                                  if line[i]['cls'] == fp[0])
    sorted_forbidden = sorted(forbidden_class_pairs, key=lambda x: approach_counts.get(x, 0), reverse=True)
    top_forbidden = set(sorted_forbidden[:len(sorted_forbidden)//2])  # top half by approach frequency

    print(f"  Top-frequency forbidden subset: {len(top_forbidden)} pairs")

    # Build class-level token frequency for within-class sampling
    class_token_freq = {}
    for cls in range(1, N_CLASSES + 1):
        toks = class_to_tokens.get(cls, [])
        if toks:
            freq = Counter()
            for t in all_tokens:
                if t['cls'] == cls:
                    freq[t['word']] += 1
            if freq:
                words = list(freq.keys())
                probs = np.array([freq[w] for w in words], dtype=float)
                probs /= probs.sum()
                class_token_freq[cls] = (words, probs)

    # Build state-to-class distribution for within-state shuffling
    state_class_freq = {}
    for state in STATE_ORDER:
        state_classes = MACRO_STATE_PARTITION[state]
        freq = Counter(t['cls'] for t in all_tokens if t['cls'] in state_classes)
        if freq:
            classes = list(freq.keys())
            probs = np.array([freq[c] for c in classes], dtype=float)
            probs /= probs.sum()
            state_class_freq[state] = (classes, probs)

    # Build role-to-class distribution for within-role shuffling
    role_class_freq = {}
    for role in ['AX', 'CC', 'EN', 'FL', 'FQ']:
        role_cls = ROLE_CLASSES[role]
        freq = Counter(t['cls'] for t in all_tokens if t['cls'] in role_cls)
        if freq:
            classes = list(freq.keys())
            probs = np.array([freq[c] for c in classes], dtype=float)
            probs /= probs.sum()
            role_class_freq[role] = (classes, probs)

    data = {
        'lines': lines,
        'all_tokens': all_tokens,
        'morph': morph,
        'token_to_class': token_to_class,
        'class_to_tokens': class_to_tokens,
        'forbidden_middle_pairs': set(forbidden_middle_pairs),
        'forbidden_class_pairs': forbidden_class_pairs,
        'top_forbidden': top_forbidden,
        'class_token_freq': class_token_freq,
        'state_class_freq': state_class_freq,
        'role_class_freq': role_class_freq,
    }
    return data


# ── Topology-Sensitive Metrics ───────────────────────────────────────

def compute_metrics(lines, data):
    """Compute 10 topology-sensitive metrics from a line-structured corpus."""
    all_tokens = [t for line in lines for t in line]
    n_tokens = len(all_tokens)
    if n_tokens < 100:
        return None

    morph = data['morph']
    forbidden_mp = data['forbidden_middle_pairs']
    forbidden_cp = data['forbidden_class_pairs']

    # ── M1: Spectral gap of 49-class transition matrix ──
    class_trans = np.zeros((N_CLASSES, N_CLASSES))
    for line in lines:
        for i in range(len(line) - 1):
            class_trans[line[i]['cls'] - 1, line[i+1]['cls'] - 1] += 1
    row_sums = class_trans.sum(axis=1, keepdims=True)
    ct_norm = class_trans / np.maximum(row_sums, 1e-12)
    eigenvalues = np.sort(np.abs(np.linalg.eigvals(ct_norm)))[::-1]
    m1_spectral_gap_49 = float(1.0 - eigenvalues[1]) if len(eigenvalues) > 1 else 1.0

    # ── M2: Forbidden MIDDLE pair violation count ──
    m2_forbidden_count = 0
    for line in lines:
        for i in range(len(line) - 1):
            mid1 = line[i].get('middle', '')
            mid2 = line[i+1].get('middle', '')
            if (mid1, mid2) in forbidden_mp:
                m2_forbidden_count += 1

    # ── M3: Forbidden class pair violation count ──
    m3_forbidden_class = 0
    for line in lines:
        for i in range(len(line) - 1):
            if (line[i]['cls'], line[i+1]['cls']) in forbidden_cp:
                m3_forbidden_class += 1

    # ── M4: Bigram diversity (unique class bigrams / total bigrams) ──
    bigrams = set()
    total_bigrams = 0
    for line in lines:
        for i in range(len(line) - 1):
            bigrams.add((line[i]['cls'], line[i+1]['cls']))
            total_bigrams += 1
    m4_bigram_diversity = len(bigrams) / max(total_bigrams, 1)

    # ── M5: Depletion asymmetry count ──
    # Count pairs where |P(A->B) - P(B->A)| > 0.01 (normalized)
    m5_depletion_count = 0
    for i in range(N_CLASSES):
        for j in range(i+1, N_CLASSES):
            p_ij = ct_norm[i, j] if row_sums[i] > 0 else 0
            p_ji = ct_norm[j, i] if row_sums[j] > 0 else 0
            if abs(p_ij - p_ji) > 0.01:
                m5_depletion_count += 1

    # ── M6: Forward-backward bigram JSD ──
    fwd_matrix = np.zeros((N_CLASSES, N_CLASSES))
    rev_matrix = np.zeros((N_CLASSES, N_CLASSES))
    for line in lines:
        seq = [t['cls'] for t in line]
        for i in range(len(seq) - 1):
            fwd_matrix[seq[i]-1, seq[i+1]-1] += 1
        rev_seq = list(reversed(seq))
        for i in range(len(rev_seq) - 1):
            rev_matrix[rev_seq[i]-1, rev_seq[i+1]-1] += 1
    fwd_flat = fwd_matrix.flatten() + 1e-12
    rev_flat = rev_matrix.flatten() + 1e-12
    fwd_flat /= fwd_flat.sum()
    rev_flat /= rev_flat.sum()
    m_flat = 0.5 * (fwd_flat + rev_flat)
    m6_fwd_rev_jsd = float(0.5 * scipy_entropy(fwd_flat, m_flat, base=2) +
                           0.5 * scipy_entropy(rev_flat, m_flat, base=2))

    # ── M7: FL forward bias ratio ──
    # P(FL -> non-FL) / P(non-FL -> FL)
    fl_classes = ROLE_CLASSES['FL']
    fl_to_nonfl = 0
    nonfl_to_fl = 0
    for line in lines:
        for i in range(len(line) - 1):
            c1 = line[i]['cls']
            c2 = line[i+1]['cls']
            if c1 in fl_classes and c2 not in fl_classes:
                fl_to_nonfl += 1
            if c1 not in fl_classes and c2 in fl_classes:
                nonfl_to_fl += 1
    m7_fl_forward_bias = fl_to_nonfl / max(nonfl_to_fl, 1)

    # ── M8: Cross-line first-class MI ──
    cross_pairs = []
    for i in range(len(lines) - 1):
        if lines[i] and lines[i+1]:
            cross_pairs.append((lines[i][-1]['cls'], lines[i+1][0]['cls']))
    if len(cross_pairs) > 10:
        xy_counts = Counter(cross_pairs)
        x_counts = Counter(p[0] for p in cross_pairs)
        y_counts = Counter(p[1] for p in cross_pairs)
        n_pairs = len(cross_pairs)
        m8_cross_mi = 0.0
        for (x, y), count in xy_counts.items():
            p_xy = count / n_pairs
            p_x = x_counts[x] / n_pairs
            p_y = y_counts[y] / n_pairs
            if p_xy > 0 and p_x > 0 and p_y > 0:
                m8_cross_mi += p_xy * np.log2(p_xy / (p_x * p_y))
    else:
        m8_cross_mi = 0.0

    # ── M9: Role self-transition enrichment ──
    # Observed/expected self-transition ratio per role
    role_self_enrichment = {}
    total_transitions = 0
    role_source_count = Counter()
    role_target_count = Counter()
    role_self_count = Counter()
    for line in lines:
        for i in range(len(line) - 1):
            r1 = CLASS_TO_ROLE.get(line[i]['cls'], 'UNK')
            r2 = CLASS_TO_ROLE.get(line[i+1]['cls'], 'UNK')
            total_transitions += 1
            role_source_count[r1] += 1
            role_target_count[r2] += 1
            if r1 == r2:
                role_self_count[r1] += 1
    for role in ['AX', 'CC', 'EN', 'FL', 'FQ']:
        observed = role_self_count[role] / max(role_source_count[role], 1)
        expected = role_target_count[role] / max(total_transitions, 1)
        role_self_enrichment[role] = observed / max(expected, 1e-10)
    m9_mean_enrichment = np.mean(list(role_self_enrichment.values()))

    # ── M10: Within-class token entropy (mean) ──
    class_token_counts = defaultdict(Counter)
    for t in all_tokens:
        class_token_counts[t['cls']][t['word']] += 1
    entropies = []
    for cls in range(1, N_CLASSES + 1):
        counts = class_token_counts[cls]
        if len(counts) > 1:
            total = sum(counts.values())
            probs = [c / total for c in counts.values()]
            entropies.append(scipy_entropy(probs, base=2))
    m10_within_class_entropy = float(np.mean(entropies)) if entropies else 0.0

    return {
        'M1_spectral_gap_49': m1_spectral_gap_49,
        'M2_forbidden_middle': m2_forbidden_count,
        'M3_forbidden_class': m3_forbidden_class,
        'M4_bigram_diversity': m4_bigram_diversity,
        'M5_depletion_asymmetry': m5_depletion_count,
        'M6_fwd_rev_jsd': m6_fwd_rev_jsd,
        'M7_fl_forward_bias': m7_fl_forward_bias,
        'M8_cross_line_mi': float(m8_cross_mi),
        'M9_role_self_enrichment': m9_mean_enrichment,
        'M10_within_class_entropy': m10_within_class_entropy,
        '_role_enrichment_detail': role_self_enrichment,
    }


# ── Ablation Conditions ─────────────────────────────────────────────

def deep_copy_lines(lines):
    """Deep copy line structure."""
    return [[dict(t) for t in line] for line in lines]


def ablation_a_forbidden_injection(lines, data, rng):
    """(a) Inject forbidden class pairs at random transition positions.

    At each transition where the source class has forbidden successors,
    with probability 0.3, replace the next token's class with a random
    forbidden successor and assign a matching token.
    """
    new_lines = deep_copy_lines(lines)
    morph = data['morph']

    # Build source -> forbidden targets lookup
    src_to_forbidden = defaultdict(list)
    for (sc, tc) in data['forbidden_class_pairs']:
        src_to_forbidden[sc].append(tc)

    injected = 0
    for line in new_lines:
        for i in range(len(line) - 1):
            src_cls = line[i]['cls']
            if src_cls in src_to_forbidden and rng.random() < 0.3:
                # Inject: replace next token with forbidden successor
                tgt_cls = rng.choice(src_to_forbidden[src_cls])
                if tgt_cls in data['class_token_freq']:
                    words, probs = data['class_token_freq'][tgt_cls]
                    new_word = rng.choice(words, p=probs)
                    m = morph.extract(new_word)
                    line[i+1] = {
                        'word': new_word,
                        'cls': tgt_cls,
                        'state': CLASS_TO_STATE.get(tgt_cls, 'UNK'),
                        'role': CLASS_TO_ROLE.get(tgt_cls, 'UNK'),
                        'prefix': m.prefix if m else None,
                        'middle': m.middle if m else new_word,
                        'suffix': m.suffix if m else None,
                        'folio': line[i+1].get('folio', ''),
                        'line': line[i+1].get('line', ''),
                    }
                    injected += 1
    return new_lines, injected


def ablation_b_forbidden_subset(lines, data, rng):
    """(b) Inject only top-frequency forbidden pairs.

    Same as (a) but restricted to the most frequently approached
    forbidden pairs (top half by source class frequency).
    """
    new_lines = deep_copy_lines(lines)
    morph = data['morph']

    src_to_forbidden = defaultdict(list)
    for (sc, tc) in data['top_forbidden']:
        src_to_forbidden[sc].append(tc)

    injected = 0
    for line in new_lines:
        for i in range(len(line) - 1):
            src_cls = line[i]['cls']
            if src_cls in src_to_forbidden and rng.random() < 0.3:
                tgt_cls = rng.choice(src_to_forbidden[src_cls])
                if tgt_cls in data['class_token_freq']:
                    words, probs = data['class_token_freq'][tgt_cls]
                    new_word = rng.choice(words, p=probs)
                    m = morph.extract(new_word)
                    line[i+1] = {
                        'word': new_word,
                        'cls': tgt_cls,
                        'state': CLASS_TO_STATE.get(tgt_cls, 'UNK'),
                        'role': CLASS_TO_ROLE.get(tgt_cls, 'UNK'),
                        'prefix': m.prefix if m else None,
                        'middle': m.middle if m else new_word,
                        'suffix': m.suffix if m else None,
                        'folio': line[i+1].get('folio', ''),
                        'line': line[i+1].get('line', ''),
                    }
                    injected += 1
    return new_lines, injected


def ablation_c_class_shuffle_in_state(lines, data, rng):
    """(c) Shuffle class within macro-state per line.

    For each position, the macro-state is preserved but the specific
    class is resampled from P(class|state). Tokens are then resampled
    from the new class.
    """
    new_lines = deep_copy_lines(lines)
    morph = data['morph']

    for line in new_lines:
        for t in line:
            state = t['state']
            if state in data['state_class_freq']:
                classes, probs = data['state_class_freq'][state]
                new_cls = rng.choice(classes, p=probs)
                if new_cls != t['cls'] and new_cls in data['class_token_freq']:
                    words, wprobs = data['class_token_freq'][new_cls]
                    new_word = rng.choice(words, p=wprobs)
                    m = morph.extract(new_word)
                    t['word'] = new_word
                    t['cls'] = new_cls
                    t['role'] = CLASS_TO_ROLE.get(new_cls, 'UNK')
                    t['prefix'] = m.prefix if m else None
                    t['middle'] = m.middle if m else new_word
                    t['suffix'] = m.suffix if m else None
    return new_lines, 0


def ablation_d_class_shuffle_in_role(lines, data, rng):
    """(d) Shuffle class within role per line.

    For each position, the role is preserved but the specific class
    is resampled from P(class|role). Tokens are then resampled.
    """
    new_lines = deep_copy_lines(lines)
    morph = data['morph']

    for line in new_lines:
        for t in line:
            role = t['role']
            if role in data['role_class_freq']:
                classes, probs = data['role_class_freq'][role]
                new_cls = rng.choice(classes, p=probs)
                if new_cls != t['cls'] and new_cls in data['class_token_freq']:
                    words, wprobs = data['class_token_freq'][new_cls]
                    new_word = rng.choice(words, p=wprobs)
                    m = morph.extract(new_word)
                    t['word'] = new_word
                    t['cls'] = new_cls
                    t['state'] = CLASS_TO_STATE.get(new_cls, 'UNK')
                    t['prefix'] = m.prefix if m else None
                    t['middle'] = m.middle if m else new_word
                    t['suffix'] = m.suffix if m else None
    return new_lines, 0


def ablation_e_token_shuffle_in_class(lines, data, rng):
    """(e) Randomize token within class, keeping class sequence exact.

    Class sequence is preserved. Each token is replaced with a random
    token from the same class. Tests whether token identity carries
    structural signal beyond class assignment.
    """
    new_lines = deep_copy_lines(lines)
    morph = data['morph']

    for line in new_lines:
        for t in line:
            cls = t['cls']
            if cls in data['class_token_freq']:
                words, probs = data['class_token_freq'][cls]
                new_word = rng.choice(words, p=probs)
                m = morph.extract(new_word)
                t['word'] = new_word
                t['prefix'] = m.prefix if m else None
                t['middle'] = m.middle if m else new_word
                t['suffix'] = m.suffix if m else None
    return new_lines, 0


# ── Bootstrap ────────────────────────────────────────────────────────

def bootstrap_metrics(lines, data, n_bootstrap, rng):
    """Compute metric variance via bootstrap resampling of lines."""
    print(f"  Bootstrap ({n_bootstrap} resamples)...")
    metric_samples = defaultdict(list)

    for b in range(n_bootstrap):
        # Resample lines with replacement
        idx = rng.choice(len(lines), size=len(lines), replace=True)
        resampled = [lines[i] for i in idx]
        metrics = compute_metrics(resampled, data)
        if metrics is None:
            continue
        for key, val in metrics.items():
            if key.startswith('_'):
                continue
            metric_samples[key].append(val)

    # Compute mean and std
    stats = {}
    for key, vals in metric_samples.items():
        stats[key] = {
            'mean': float(np.mean(vals)),
            'std': float(np.std(vals)),
        }
    return stats


# ── Main ─────────────────────────────────────────────────────────────

def main():
    data = load_data()
    lines = data['lines']
    rng = np.random.default_rng(349)

    # ── Step 1: Real corpus metrics ──
    print("\nComputing real corpus metrics...")
    real_metrics = compute_metrics(lines, data)
    print("  Real metrics:")
    for key, val in sorted(real_metrics.items()):
        if key.startswith('_'):
            continue
        print(f"    {key}: {val}")

    # ── Step 2: Bootstrap for sigma ──
    print("\nBootstrapping real corpus variance...")
    boot_stats = bootstrap_metrics(lines, data, N_BOOTSTRAP, rng)
    print("  Bootstrap sigmas:")
    for key in sorted(boot_stats.keys()):
        print(f"    {key}: mean={boot_stats[key]['mean']:.6f}, std={boot_stats[key]['std']:.6f}")

    # ── Step 3: Run ablations ──
    ablations = {
        'a_forbidden_injection': ablation_a_forbidden_injection,
        'b_forbidden_subset': ablation_b_forbidden_subset,
        'c_class_shuffle_in_state': ablation_c_class_shuffle_in_state,
        'd_class_shuffle_in_role': ablation_d_class_shuffle_in_role,
        'e_token_shuffle_in_class': ablation_e_token_shuffle_in_class,
    }

    ablation_results = {}
    for abl_name, abl_func in ablations.items():
        print(f"\nRunning ablation: {abl_name} ({N_SHUFFLES} instantiations)...")
        metric_samples = defaultdict(list)
        total_injected = 0

        for s in range(N_SHUFFLES):
            if (s + 1) % 25 == 0:
                print(f"  ... {s + 1}/{N_SHUFFLES}")
            abl_lines, injected = abl_func(lines, data, rng)
            total_injected += injected
            metrics = compute_metrics(abl_lines, data)
            if metrics is None:
                continue
            for key, val in metrics.items():
                if key.startswith('_'):
                    continue
                metric_samples[key].append(val)

        # Compute ablation statistics
        abl_stats = {}
        for key in sorted(metric_samples.keys()):
            vals = metric_samples[key]
            abl_mean = float(np.mean(vals))
            abl_std = float(np.std(vals))

            # Break detection: deviation from real > 2 * bootstrap sigma
            real_val = real_metrics.get(key, 0)
            boot_sigma = boot_stats.get(key, {}).get('std', 1e-10)
            if boot_sigma < 1e-10:
                boot_sigma = 1e-10

            deviation = abs(abl_mean - real_val)
            z_score = deviation / boot_sigma
            breaks = z_score > 2.0

            abl_stats[key] = {
                'mean': abl_mean,
                'std': abl_std,
                'real_value': real_val,
                'deviation': deviation,
                'boot_sigma': boot_sigma,
                'z_score': float(z_score),
                'breaks': breaks,
                'direction': 'higher' if abl_mean > real_val else 'lower',
            }

        ablation_results[abl_name] = {
            'stats': abl_stats,
            'mean_injected': total_injected / N_SHUFFLES if abl_name.startswith(('a_', 'b_')) else 0,
        }

        # Print summary
        print(f"  Results for {abl_name}:")
        if abl_name.startswith(('a_', 'b_')):
            print(f"    Mean injected: {total_injected / N_SHUFFLES:.1f}")
        for key in sorted(abl_stats.keys()):
            s = abl_stats[key]
            flag = "**BREAKS**" if s['breaks'] else "survives"
            print(f"    {key}: real={s['real_value']:.4f} abl={s['mean']:.4f} z={s['z_score']:.2f} {flag}")

    # ── Step 4: Classification matrix ──
    print("\n" + "="*70)
    print("METRIC SENSITIVITY CLASSIFICATION")
    print("="*70)

    metric_keys = [k for k in sorted(real_metrics.keys()) if not k.startswith('_')]
    abl_names = list(ablations.keys())

    # Build break matrix
    break_matrix = {}
    for mk in metric_keys:
        break_matrix[mk] = {}
        for abl_name in abl_names:
            breaks = ablation_results[abl_name]['stats'].get(mk, {}).get('breaks', False)
            break_matrix[mk][abl_name] = breaks

    # Classify each metric
    classifications = {}
    for mk in metric_keys:
        broken_by = [a for a in abl_names if break_matrix[mk].get(a, False)]
        if not broken_by:
            category = 'DISTRIBUTIONAL'  # survives all ablations = marginal
        elif any('forbidden' in a for a in broken_by) and not any('shuffle' in a for a in broken_by):
            category = 'TOPOLOGICAL'  # breaks only under forbidden injection
        elif any('shuffle' in a for a in broken_by) and not any('forbidden' in a for a in broken_by):
            category = 'SEQUENTIAL'  # breaks only under class/token shuffle
        else:
            category = 'COMPOUND'  # breaks under both

        classifications[mk] = {
            'category': category,
            'broken_by': broken_by,
            'n_breaks': len(broken_by),
        }

        print(f"  {mk}: {category} (breaks: {len(broken_by)}/5 = {broken_by})")

    # Summary
    cat_counts = Counter(c['category'] for c in classifications.values())
    print(f"\n  DISTRIBUTIONAL: {cat_counts.get('DISTRIBUTIONAL', 0)}")
    print(f"  SEQUENTIAL:     {cat_counts.get('SEQUENTIAL', 0)}")
    print(f"  TOPOLOGICAL:    {cat_counts.get('TOPOLOGICAL', 0)}")
    print(f"  COMPOUND:       {cat_counts.get('COMPOUND', 0)}")

    # ── Step 5: Necessity verdicts per ablation ──
    print("\n" + "="*70)
    print("NECESSITY VERDICTS")
    print("="*70)

    necessity_verdicts = {}
    for abl_name in abl_names:
        broken = [mk for mk in metric_keys if break_matrix[mk].get(abl_name, False)]
        total = len(metric_keys)
        verdict = 'LOAD_BEARING' if len(broken) >= 3 else 'PARTIAL' if len(broken) >= 1 else 'DECORATIVE'
        necessity_verdicts[abl_name] = {
            'broken_metrics': broken,
            'n_broken': len(broken),
            'n_total': total,
            'verdict': verdict,
        }
        print(f"  {abl_name}: {verdict} ({len(broken)}/{total} metrics break)")
        for mk in broken:
            z = ablation_results[abl_name]['stats'][mk]['z_score']
            d = ablation_results[abl_name]['stats'][mk]['direction']
            print(f"    - {mk}: z={z:.2f} ({d})")

    # ── Output ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        'metadata': {
            'phase': 349,
            'name': 'GRAMMAR_COMPONENT_NECESSITY',
            'n_shuffles': N_SHUFFLES,
            'n_bootstrap': N_BOOTSTRAP,
            'break_threshold': '2 sigma',
            'n_forbidden_middle_pairs': len(data['forbidden_middle_pairs']),
            'n_forbidden_class_pairs': len(data['forbidden_class_pairs']),
            'n_top_forbidden': len(data['top_forbidden']),
        },
        'real_metrics': {k: v for k, v in real_metrics.items() if not k.startswith('_')},
        'bootstrap_sigmas': boot_stats,
        'ablation_results': {},
        'classifications': classifications,
        'necessity_verdicts': necessity_verdicts,
    }

    # Serialize ablation results (strip non-serializable)
    for abl_name, abl_data in ablation_results.items():
        output['ablation_results'][abl_name] = {
            'stats': abl_data['stats'],
            'mean_injected': abl_data['mean_injected'],
        }

    out_path = RESULTS_DIR / 'grammar_component_necessity.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")

    # ── Final summary ──
    print("\n" + "="*70)
    print("PHASE 349 SUMMARY")
    print("="*70)
    print(f"  Metrics computed: {len(metric_keys)}")
    print(f"  Ablation conditions: {len(abl_names)}")
    print(f"  Break matrix: {sum(1 for mk in metric_keys for a in abl_names if break_matrix[mk].get(a, False))} breaks / {len(metric_keys) * len(abl_names)} cells")
    print(f"  Classification: {dict(cat_counts)}")
    for abl_name, v in necessity_verdicts.items():
        print(f"  {abl_name}: {v['verdict']}")


if __name__ == '__main__':
    main()
