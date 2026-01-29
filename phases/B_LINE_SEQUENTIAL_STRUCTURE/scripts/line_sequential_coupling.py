#!/usr/bin/env python3
"""
B_LINE_SEQUENTIAL_STRUCTURE - Script 1: Line Sequential Coupling

Measures whether adjacent lines within a folio are sequentially coupled
or independent draws from a stationary distribution.

Tests:
  1. Adjacent-Line MIDDLE Overlap (Jaccard similarity, permutation baseline)
  2. MIDDLE Novelty Curve (cumulative unique MIDDLEs, front-loaded vs uniform)
  3. Cross-Line Boundary Bigrams (class transitions at line boundaries)
  4. CC Trigger Autocorrelation (daiin/ol/ol_d sequence memory)
  5. EN Subfamily Autocorrelation (QO fraction lag memory, position-controlled)

Constraint references:
  C171: 94.2% class change line-to-line; closed-loop
  C357: Lines are formal control blocks; 0 cross-line grammar violations
  C389: Bigram determinism H=0.41 bits (within-line)
  C390: 99.6% trigrams hapax; no formulas
  C391: Time-reversal symmetry
  C506.b: 73% of within-class MIDDLE pairs JSD > 0.4
  C606: CC trigger predicts EN subfamily (V=0.246)
  C608: No lane coherence (p=0.963)

Dependencies:
  - phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json
  - phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json
  - scripts/voynich.py (Transcript, Morphology)

Output: results/line_sequential_coupling.json
"""

import json
import sys
import warnings
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================

CLASS_TO_ROLE = {
    10: 'CC', 11: 'CC', 12: 'CC', 17: 'CC',
    8: 'EN', 31: 'EN', 32: 'EN', 33: 'EN', 34: 'EN', 35: 'EN',
    36: 'EN', 37: 'EN', 39: 'EN', 41: 'EN', 42: 'EN', 43: 'EN',
    44: 'EN', 45: 'EN', 46: 'EN', 47: 'EN', 48: 'EN', 49: 'EN',
    7: 'FL', 30: 'FL', 38: 'FL', 40: 'FL',
    9: 'FQ', 13: 'FQ', 14: 'FQ', 23: 'FQ',
}
for c in list(range(1, 7)) + list(range(15, 17)) + list(range(18, 23)) + list(range(24, 30)):
    if c not in CLASS_TO_ROLE:
        CLASS_TO_ROLE[c] = 'AX'

EN_QO_CLASSES = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH_CLASSES = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}
EN_MINOR_CLASSES = {41}

CC_DAIIN = {10}
CC_OL = {11}
CC_OL_D = {17}

MIN_LINES_PER_FOLIO = 8
N_PERMUTATIONS = 1000

np.random.seed(42)


def line_sort_key(line_str):
    digits = ''
    for ch in line_str:
        if ch.isdigit():
            digits += ch
        else:
            break
    rest = line_str[len(digits):]
    return (int(digits) if digits else 0, rest)


def get_en_subfamily(cls):
    if cls in EN_QO_CLASSES:
        return 'QO'
    if cls in EN_CHSH_CLASSES:
        return 'CHSH'
    if cls in EN_MINOR_CLASSES:
        return 'MINOR'
    return None


def get_cc_subgroup(cls):
    if cls in CC_DAIIN:
        return 'CC_DAIIN'
    if cls in CC_OL:
        return 'CC_OL'
    if cls in CC_OL_D:
        return 'CC_OL_D'
    return None


def safe_spearmanr(x, y):
    from scipy.stats import spearmanr
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        if len(set(y)) <= 1 or len(x) < 3:
            return 0.0, 1.0
        return spearmanr(x, y)


# ============================================================
# SECTION 1: LOAD & PREPARE
# ============================================================
print("=" * 70)
print("B_LINE_SEQUENTIAL_STRUCTURE - Script 1: Line Sequential Coupling")
print("=" * 70)
print("\n--- Section 1: Load & Prepare ---")

# Load class token map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm_raw = json.load(f)
if 'token_to_class' in ctm_raw:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw['token_to_class'].items()}
else:
    token_to_class = {tok: int(cls) for tok, cls in ctm_raw.items()}
print(f"  Loaded class_token_map: {len(token_to_class)} tokens mapped")

# Load regime mapping
regime_path = PROJECT_ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_to_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_to_regime[folio] = regime
print(f"  Loaded regime mapping: {len(folio_to_regime)} folios")

# Build morphology cache
morph = Morphology()
morph_cache = {}


def get_middle(word):
    if word not in morph_cache:
        m = morph.extract(word)
        morph_cache[word] = m.middle if m else None
    return morph_cache[word]


# Build per-folio, per-line data
tx = Transcript()

folio_lines = defaultdict(lambda: defaultdict(list))
total_b_tokens = 0

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    total_b_tokens += 1

    cls = token_to_class.get(token.word)
    role = CLASS_TO_ROLE.get(cls, 'UNC') if cls is not None else 'UNC'
    middle = get_middle(token.word)

    folio_lines[token.folio][token.line].append({
        'word': token.word,
        'class': cls,
        'role': role,
        'middle': middle,
        'en_subfamily': get_en_subfamily(cls) if role == 'EN' else None,
        'cc_subgroup': get_cc_subgroup(cls) if role == 'CC' else None,
    })

# Filter to folios with >= MIN_LINES
valid_folios = {f for f, lines in folio_lines.items() if len(lines) >= MIN_LINES_PER_FOLIO}
n_folios = len(valid_folios)
n_lines_total = sum(len(folio_lines[f]) for f in valid_folios)
print(f"  Total B tokens: {total_b_tokens}")
print(f"  Folios with >={MIN_LINES_PER_FOLIO} lines: {n_folios}")
print(f"  Lines in valid folios: {n_lines_total}")
print(f"  Morphology cache: {len(morph_cache)} unique words")

regimes = sorted(set(folio_to_regime.get(f, 'UNKNOWN') for f in valid_folios))
print(f"  Regimes: {regimes}")


# ============================================================
# Pre-compute per-folio sorted line lists + per-line MIDDLE sets
# ============================================================
folio_sorted_lines = {}  # folio -> [line_id, ...]
folio_line_middles = {}  # folio -> {line_id: set(middles)}
folio_line_classes = {}  # folio -> {line_id: [class, ...]}
folio_line_tokens = {}   # folio -> {line_id: [{token_data}, ...]}

for folio in valid_folios:
    sorted_lines = sorted(folio_lines[folio].keys(), key=line_sort_key)
    folio_sorted_lines[folio] = sorted_lines

    line_mid = {}
    line_cls = {}
    line_tok = {}
    for line_id in sorted_lines:
        tokens = folio_lines[folio][line_id]
        line_mid[line_id] = set(t['middle'] for t in tokens if t['middle'] is not None)
        line_cls[line_id] = [t['class'] for t in tokens if t['class'] is not None]
        line_tok[line_id] = tokens
    folio_line_middles[folio] = line_mid
    folio_line_classes[folio] = line_cls
    folio_line_tokens[folio] = line_tok


# ============================================================
# TEST 1: ADJACENT-LINE MIDDLE OVERLAP
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: Adjacent-Line MIDDLE Overlap")
print("=" * 70)


def compute_adjacent_jaccard(folio, line_order):
    """Compute mean Jaccard of adjacent line MIDDLE sets."""
    middles = folio_line_middles[folio]
    jaccards = []
    for i in range(len(line_order) - 1):
        s1 = middles[line_order[i]]
        s2 = middles[line_order[i + 1]]
        if len(s1) == 0 and len(s2) == 0:
            continue
        union = s1 | s2
        inter = s1 & s2
        jaccards.append(len(inter) / len(union) if len(union) > 0 else 0)
    return np.mean(jaccards) if jaccards else 0.0


# Observed adjacent Jaccard per folio
observed_jaccards = {}
for folio in valid_folios:
    observed_jaccards[folio] = compute_adjacent_jaccard(folio, folio_sorted_lines[folio])

# Permutation baseline: shuffle line order within each folio
perm_means = {f: [] for f in valid_folios}
for perm_i in range(N_PERMUTATIONS):
    for folio in valid_folios:
        shuffled = list(folio_sorted_lines[folio])
        np.random.shuffle(shuffled)
        perm_means[folio].append(compute_adjacent_jaccard(folio, shuffled))

# Per-folio p-values and effect sizes
test1_folio_results = {}
obs_values = []
perm_baseline_means = []
p_values = []

for folio in sorted(valid_folios):
    obs = observed_jaccards[folio]
    perm_dist = perm_means[folio]
    perm_mean = np.mean(perm_dist)
    perm_std = np.std(perm_dist) if np.std(perm_dist) > 0 else 1e-9
    p_val = np.mean([1 for p in perm_dist if p >= obs])
    effect_size = (obs - perm_mean) / perm_std

    obs_values.append(obs)
    perm_baseline_means.append(perm_mean)
    p_values.append(p_val)

    test1_folio_results[folio] = {
        'observed_jaccard': round(obs, 4),
        'permuted_mean': round(perm_mean, 4),
        'effect_size': round(effect_size, 4),
        'p_value': round(p_val, 4),
        'regime': folio_to_regime.get(folio, 'UNKNOWN'),
    }

grand_obs = np.mean(obs_values)
grand_perm = np.mean(perm_baseline_means)
sig_folios = sum(1 for p in p_values if p < 0.05)

print(f"\n  Grand mean observed Jaccard: {grand_obs:.4f}")
print(f"  Grand mean permuted Jaccard: {grand_perm:.4f}")
print(f"  Difference: {grand_obs - grand_perm:+.4f}")
print(f"  Folios with p<0.05: {sig_folios}/{n_folios} ({100*sig_folios/n_folios:.1f}%)")

# Regime stratification
print(f"\n  Regime stratification:")
for regime in regimes:
    r_folios = [f for f in valid_folios if folio_to_regime.get(f) == regime]
    if not r_folios:
        continue
    r_obs = np.mean([observed_jaccards[f] for f in r_folios])
    r_perm = np.mean([np.mean(perm_means[f]) for f in r_folios])
    r_sig = sum(1 for f in r_folios if test1_folio_results[f]['p_value'] < 0.05)
    print(f"    {regime} (n={len(r_folios)}): obs={r_obs:.4f} perm={r_perm:.4f} diff={r_obs-r_perm:+.4f} sig={r_sig}/{len(r_folios)}")

test1_results = {
    'grand_observed_jaccard': round(grand_obs, 4),
    'grand_permuted_jaccard': round(grand_perm, 4),
    'difference': round(grand_obs - grand_perm, 4),
    'significant_folios': sig_folios,
    'total_folios': n_folios,
    'pct_significant': round(100 * sig_folios / n_folios, 1),
    'folio_detail': test1_folio_results,
}


# ============================================================
# TEST 2: MIDDLE NOVELTY CURVE
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: MIDDLE Novelty Curve")
print("=" * 70)


def compute_novelty_curve(folio, line_order):
    """Track cumulative unique MIDDLEs across lines. Return first-half fraction."""
    middles = folio_line_middles[folio]
    seen = set()
    cumulative = []
    for line_id in line_order:
        seen |= middles[line_id]
        cumulative.append(len(seen))

    total_unique = cumulative[-1] if cumulative else 0
    if total_unique == 0:
        return 0.5, cumulative

    half = len(line_order) // 2
    first_half_unique = cumulative[half - 1] if half > 0 else 0
    return first_half_unique / total_unique, cumulative


# Observed novelty curves
test2_folio_results = {}
observed_first_half = []
perm_first_half_means = {f: [] for f in valid_folios}

for folio in valid_folios:
    fh_frac, curve = compute_novelty_curve(folio, folio_sorted_lines[folio])
    observed_first_half.append(fh_frac)
    test2_folio_results[folio] = {
        'first_half_fraction': round(fh_frac, 4),
        'total_unique_middles': curve[-1] if curve else 0,
        'n_lines': len(folio_sorted_lines[folio]),
        'regime': folio_to_regime.get(folio, 'UNKNOWN'),
    }

# Permutation baseline
for perm_i in range(N_PERMUTATIONS):
    for folio in valid_folios:
        shuffled = list(folio_sorted_lines[folio])
        np.random.shuffle(shuffled)
        fh_frac, _ = compute_novelty_curve(folio, shuffled)
        perm_first_half_means[folio].append(fh_frac)

# Classify each folio
classifications = {'FRONT_LOADED': 0, 'BACK_LOADED': 0, 'UNIFORM': 0}
for folio in valid_folios:
    fh = test2_folio_results[folio]['first_half_fraction']
    perm_mean = np.mean(perm_first_half_means[folio])
    perm_std = np.std(perm_first_half_means[folio])
    p_front = np.mean([1 for p in perm_first_half_means[folio] if p >= fh])
    p_back = np.mean([1 for p in perm_first_half_means[folio] if p <= fh])

    if fh > 0.6:
        cat = 'FRONT_LOADED'
    elif fh < 0.4:
        cat = 'BACK_LOADED'
    else:
        cat = 'UNIFORM'
    classifications[cat] += 1
    test2_folio_results[folio]['category'] = cat
    test2_folio_results[folio]['perm_mean'] = round(perm_mean, 4)
    test2_folio_results[folio]['p_front'] = round(p_front, 4)
    test2_folio_results[folio]['p_back'] = round(p_back, 4)

grand_fh = np.mean(observed_first_half)
grand_perm_fh = np.mean([np.mean(perm_first_half_means[f]) for f in valid_folios])

print(f"\n  Grand mean first-half fraction: {grand_fh:.4f}")
print(f"  Grand permuted first-half fraction: {grand_perm_fh:.4f}")
print(f"  Difference: {grand_fh - grand_perm_fh:+.4f}")
print(f"\n  Classification:")
for cat, count in classifications.items():
    print(f"    {cat}: {count}/{n_folios} ({100*count/n_folios:.1f}%)")

# Regime stratification
print(f"\n  Regime stratification:")
for regime in regimes:
    r_folios = [f for f in valid_folios if folio_to_regime.get(f) == regime]
    if not r_folios:
        continue
    r_fh = np.mean([test2_folio_results[f]['first_half_fraction'] for f in r_folios])
    r_cats = Counter(test2_folio_results[f]['category'] for f in r_folios)
    print(f"    {regime} (n={len(r_folios)}): mean_fh={r_fh:.4f} FL={r_cats.get('FRONT_LOADED',0)} BL={r_cats.get('BACK_LOADED',0)} UN={r_cats.get('UNIFORM',0)}")

test2_results = {
    'grand_first_half_fraction': round(grand_fh, 4),
    'grand_permuted_first_half': round(grand_perm_fh, 4),
    'difference': round(grand_fh - grand_perm_fh, 4),
    'classifications': classifications,
    'folio_detail': test2_folio_results,
}


# ============================================================
# TEST 3: CROSS-LINE BOUNDARY BIGRAMS
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: Cross-Line Boundary Bigrams")
print("=" * 70)

from scipy.stats import chi2_contingency

# Collect boundary pairs (last class of line N -> first class of line N+1)
boundary_pairs = []
within_pairs = []

for folio in valid_folios:
    sorted_lines = folio_sorted_lines[folio]
    for i in range(len(sorted_lines)):
        line_id = sorted_lines[i]
        classes = folio_line_classes[folio][line_id]

        # Within-line bigrams (for comparison)
        for j in range(len(classes) - 1):
            within_pairs.append((classes[j], classes[j + 1]))

        # Boundary bigram: last of this line -> first of next line
        if i < len(sorted_lines) - 1:
            next_line_id = sorted_lines[i + 1]
            next_classes = folio_line_classes[folio][next_line_id]
            if classes and next_classes:
                boundary_pairs.append((classes[-1], next_classes[0]))

print(f"\n  Boundary pairs collected: {len(boundary_pairs)}")
print(f"  Within-line pairs collected: {len(within_pairs)}")

# Build transition matrices
all_classes = sorted(set(c for pair in boundary_pairs + within_pairs for c in pair))
cls_idx = {c: i for i, c in enumerate(all_classes)}
n_cls = len(all_classes)

boundary_matrix = np.zeros((n_cls, n_cls), dtype=int)
for src, tgt in boundary_pairs:
    boundary_matrix[cls_idx[src], cls_idx[tgt]] += 1

within_matrix = np.zeros((n_cls, n_cls), dtype=int)
for src, tgt in within_pairs:
    within_matrix[cls_idx[src], cls_idx[tgt]] += 1

# Conditional entropy H(next | prev) for boundary vs within
def conditional_entropy(matrix):
    """H(col | row) from count matrix."""
    row_sums = matrix.sum(axis=1)
    h = 0.0
    total = matrix.sum()
    if total == 0:
        return 0.0
    for i in range(matrix.shape[0]):
        if row_sums[i] == 0:
            continue
        p_row = row_sums[i] / total
        row_probs = matrix[i] / row_sums[i]
        row_h = -np.sum(row_probs[row_probs > 0] * np.log2(row_probs[row_probs > 0]))
        h += p_row * row_h
    return h

h_boundary = conditional_entropy(boundary_matrix)
h_within = conditional_entropy(within_matrix)

# Unconditional entropy of class distribution
all_class_counts = Counter(c for pair in boundary_pairs for c in pair)
total_c = sum(all_class_counts.values())
h_unconditional = -sum((count/total_c) * np.log2(count/total_c)
                       for count in all_class_counts.values() if count > 0)

print(f"\n  Conditional entropy H(next|prev):")
print(f"    Within-line:   {h_within:.4f} bits")
print(f"    Boundary:      {h_boundary:.4f} bits")
print(f"    Unconditional: {h_unconditional:.4f} bits")
print(f"    Boundary/Within ratio: {h_boundary/h_within:.4f}" if h_within > 0 else "    Within = 0")

# Chi-square independence test on boundary matrix
# Remove zero-sum rows/cols for valid chi-square
bm_trimmed = boundary_matrix.copy()
nonzero_rows = bm_trimmed.sum(axis=1) > 0
nonzero_cols = bm_trimmed.sum(axis=0) > 0
bm_test = bm_trimmed[np.ix_(nonzero_rows, nonzero_cols)]

try:
    chi2, p_chi2, dof, expected = chi2_contingency(bm_test)
    print(f"\n  Chi-square independence test on boundary matrix:")
    print(f"    chi2 = {chi2:.2f}, dof = {dof}, p = {p_chi2:.2e}")
    chi2_result = {'chi2': round(chi2, 2), 'dof': dof, 'p': float(p_chi2)}
except Exception as e:
    print(f"\n  Chi-square test failed: {e}")
    chi2_result = {'error': str(e)}

# Top 10 boundary bigrams
boundary_counts = Counter(boundary_pairs)
top_boundary = boundary_counts.most_common(10)
print(f"\n  Top 10 boundary bigrams (class_N_last -> class_N+1_first):")
for pair, count in top_boundary:
    pct = 100 * count / len(boundary_pairs)
    print(f"    {pair[0]:>3} -> {pair[1]:>3}: {count:>5} ({pct:.1f}%)")

# Role-level boundary transitions
boundary_role_pairs = []
for src, tgt in boundary_pairs:
    src_role = CLASS_TO_ROLE.get(src, 'UNC')
    tgt_role = CLASS_TO_ROLE.get(tgt, 'UNC')
    boundary_role_pairs.append((src_role, tgt_role))

role_counts = Counter(boundary_role_pairs)
roles = ['CC', 'EN', 'FL', 'FQ', 'AX']
print(f"\n  Boundary role transitions:")
print(f"    {'':>6}", end='')
for r in roles:
    print(f" {r:>6}", end='')
print()
for src_role in roles:
    print(f"    {src_role:>6}", end='')
    row_total = sum(role_counts.get((src_role, tgt_role), 0) for tgt_role in roles)
    for tgt_role in roles:
        ct = role_counts.get((src_role, tgt_role), 0)
        pct = 100 * ct / row_total if row_total > 0 else 0
        print(f" {pct:>5.1f}%", end='')
    print()

test3_results = {
    'n_boundary_pairs': len(boundary_pairs),
    'n_within_pairs': len(within_pairs),
    'h_boundary': round(h_boundary, 4),
    'h_within': round(h_within, 4),
    'h_unconditional': round(h_unconditional, 4),
    'h_ratio_boundary_to_within': round(h_boundary / h_within, 4) if h_within > 0 else None,
    'chi_square': chi2_result,
    'top_10_boundary_bigrams': [{'src': p[0], 'tgt': p[1], 'count': c} for p, c in top_boundary],
}


# ============================================================
# TEST 4: CC TRIGGER AUTOCORRELATION
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: CC Trigger Autocorrelation")
print("=" * 70)

# Extract first CC token per line -> classify subgroup
folio_cc_sequences = {}  # folio -> [(line_id, cc_subgroup), ...]
total_lines_with_cc = 0
total_lines_checked = 0

for folio in valid_folios:
    cc_seq = []
    for line_id in folio_sorted_lines[folio]:
        total_lines_checked += 1
        tokens = folio_line_tokens[folio][line_id]
        # Find first CC token
        first_cc = None
        for t in tokens:
            if t['cc_subgroup'] is not None:
                first_cc = t['cc_subgroup']
                break
        if first_cc is not None:
            cc_seq.append((line_id, first_cc))
            total_lines_with_cc += 1
    folio_cc_sequences[folio] = cc_seq

print(f"\n  Lines with CC trigger: {total_lines_with_cc}/{total_lines_checked} ({100*total_lines_with_cc/total_lines_checked:.1f}%)")

# CC subgroup distribution
cc_dist = Counter()
for folio in valid_folios:
    for _, sg in folio_cc_sequences[folio]:
        cc_dist[sg] += 1
print(f"  CC subgroup distribution: {dict(cc_dist)}")

# Lag-1 autocorrelation: encode CC type as categorical and compute transition matrix
cc_types = ['CC_DAIIN', 'CC_OL', 'CC_OL_D']
cc_type_idx = {t: i for i, t in enumerate(cc_types)}

observed_cc_transitions = np.zeros((3, 3), dtype=int)
for folio in valid_folios:
    seq = folio_cc_sequences[folio]
    for i in range(len(seq) - 1):
        src = cc_type_idx.get(seq[i][1])
        tgt = cc_type_idx.get(seq[i + 1][1])
        if src is not None and tgt is not None:
            observed_cc_transitions[src, tgt] += 1

total_cc_pairs = observed_cc_transitions.sum()
print(f"\n  CC transition pairs: {total_cc_pairs}")
print(f"  Observed CC transition matrix:")
print(f"    {'':>12}", end='')
for t in cc_types:
    print(f" {t:>10}", end='')
print()
for i, src_type in enumerate(cc_types):
    row_sum = observed_cc_transitions[i].sum()
    print(f"    {src_type:>12}", end='')
    for j in range(3):
        pct = 100 * observed_cc_transitions[i, j] / row_sum if row_sum > 0 else 0
        print(f" {pct:>9.1f}%", end='')
    print(f"  (n={row_sum})")

# Permutation test: shuffle CC sequence within folio, recompute transition matrix
perm_cc_diag_fracs = []  # fraction of self-transitions (diagonal)
obs_diag_frac = np.trace(observed_cc_transitions) / total_cc_pairs if total_cc_pairs > 0 else 0

for perm_i in range(N_PERMUTATIONS):
    perm_transitions = np.zeros((3, 3), dtype=int)
    for folio in valid_folios:
        seq = [s[1] for s in folio_cc_sequences[folio]]
        np.random.shuffle(seq)
        for i in range(len(seq) - 1):
            src = cc_type_idx.get(seq[i])
            tgt = cc_type_idx.get(seq[i + 1])
            if src is not None and tgt is not None:
                perm_transitions[src, tgt] += 1
    perm_total = perm_transitions.sum()
    perm_diag = np.trace(perm_transitions) / perm_total if perm_total > 0 else 0
    perm_cc_diag_fracs.append(perm_diag)

p_cc_auto = np.mean([1 for p in perm_cc_diag_fracs if p >= obs_diag_frac])
print(f"\n  Self-transition (diagonal) fraction:")
print(f"    Observed: {obs_diag_frac:.4f}")
print(f"    Permuted mean: {np.mean(perm_cc_diag_fracs):.4f}")
print(f"    p-value: {p_cc_auto:.4f}")

# Chi-square on CC transition matrix
try:
    # Remove zero rows/cols
    cc_nz_rows = observed_cc_transitions.sum(axis=1) > 0
    cc_nz_cols = observed_cc_transitions.sum(axis=0) > 0
    cc_test = observed_cc_transitions[np.ix_(cc_nz_rows, cc_nz_cols)]
    chi2_cc, p_chi2_cc, dof_cc, _ = chi2_contingency(cc_test)
    print(f"  Chi-square: chi2={chi2_cc:.2f}, dof={dof_cc}, p={p_chi2_cc:.2e}")
    cc_chi2_result = {'chi2': round(chi2_cc, 2), 'dof': dof_cc, 'p': float(p_chi2_cc)}
except Exception as e:
    print(f"  Chi-square failed: {e}")
    cc_chi2_result = {'error': str(e)}

test4_results = {
    'lines_with_cc': total_lines_with_cc,
    'cc_distribution': dict(cc_dist),
    'transition_matrix': observed_cc_transitions.tolist(),
    'transition_types': cc_types,
    'self_transition_fraction': round(obs_diag_frac, 4),
    'perm_self_transition_mean': round(float(np.mean(perm_cc_diag_fracs)), 4),
    'p_value_self_transition': round(float(p_cc_auto), 4),
    'chi_square': cc_chi2_result,
}


# ============================================================
# TEST 5: EN SUBFAMILY AUTOCORRELATION
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: EN Subfamily Autocorrelation (QO fraction)")
print("=" * 70)

# Per-line QO fraction (require >= 3 EN tokens per line for stability)
MIN_EN_PER_LINE = 3
folio_qo_sequences = {}  # folio -> [(line_idx_within_folio, norm_pos, qo_fraction), ...]

for folio in valid_folios:
    sorted_lines = folio_sorted_lines[folio]
    n_lines = len(sorted_lines)
    qo_seq = []
    for idx, line_id in enumerate(sorted_lines):
        tokens = folio_line_tokens[folio][line_id]
        en_tokens = [t for t in tokens if t['role'] == 'EN']
        qo = sum(1 for t in en_tokens if t['en_subfamily'] == 'QO')
        chsh = sum(1 for t in en_tokens if t['en_subfamily'] == 'CHSH')
        total_en = qo + chsh
        if total_en >= MIN_EN_PER_LINE:
            norm_pos = idx / max(n_lines - 1, 1)
            qo_frac = qo / total_en
            qo_seq.append((idx, norm_pos, qo_frac))
    folio_qo_sequences[folio] = qo_seq

total_qo_lines = sum(len(s) for s in folio_qo_sequences.values())
print(f"\n  Lines with >={MIN_EN_PER_LINE} EN tokens: {total_qo_lines}")

# Raw lag-1 autocorrelation (pooled across folios)
lag1_pairs_raw = []  # (qo_N, qo_N+1) for consecutive eligible lines
for folio in valid_folios:
    seq = folio_qo_sequences[folio]
    for i in range(len(seq) - 1):
        idx_a, _, qo_a = seq[i]
        idx_b, _, qo_b = seq[i + 1]
        # Only consecutive lines (adjacent in folio, not just adjacent in eligible set)
        if idx_b - idx_a == 1:
            lag1_pairs_raw.append((qo_a, qo_b))

if len(lag1_pairs_raw) >= 3:
    x_raw = np.array([p[0] for p in lag1_pairs_raw])
    y_raw = np.array([p[1] for p in lag1_pairs_raw])
    rho_raw, p_raw = safe_spearmanr(x_raw, y_raw)
else:
    rho_raw, p_raw = 0.0, 1.0

print(f"\n  Raw lag-1 autocorrelation (strictly consecutive lines):")
print(f"    Pairs: {len(lag1_pairs_raw)}")
print(f"    Spearman rho = {rho_raw:.4f}, p = {p_raw:.2e}")

# Position-controlled lag-1: partial correlation
# QO_N+1 ~ QO_N after regressing out norm_pos_N+1
lag1_pairs_controlled = []  # (qo_N, qo_N+1, norm_pos_N+1)
for folio in valid_folios:
    seq = folio_qo_sequences[folio]
    for i in range(len(seq) - 1):
        idx_a, pos_a, qo_a = seq[i]
        idx_b, pos_b, qo_b = seq[i + 1]
        if idx_b - idx_a == 1:
            lag1_pairs_controlled.append((qo_a, qo_b, pos_b))

if len(lag1_pairs_controlled) >= 10:
    from scipy.stats import pearsonr
    arr = np.array(lag1_pairs_controlled)
    qo_prev = arr[:, 0]
    qo_next = arr[:, 1]
    pos_next = arr[:, 2]

    # Residualize: regress out position from both qo_prev and qo_next
    from numpy.polynomial.polynomial import polyfit, polyval
    # Simple linear regression residuals
    coef_next = np.polyfit(pos_next, qo_next, 1)
    resid_next = qo_next - np.polyval(coef_next, pos_next)

    coef_prev = np.polyfit(pos_next, qo_prev, 1)  # control prev by next's position too
    resid_prev = qo_prev - np.polyval(coef_prev, pos_next)

    rho_partial, p_partial = safe_spearmanr(resid_prev, resid_next)
    print(f"\n  Position-controlled lag-1 (partial autocorrelation):")
    print(f"    Pairs: {len(lag1_pairs_controlled)}")
    print(f"    Spearman rho (partial) = {rho_partial:.4f}, p = {p_partial:.2e}")
else:
    rho_partial, p_partial = 0.0, 1.0
    print(f"\n  Position-controlled: insufficient pairs ({len(lag1_pairs_controlled)})")

# Lag-2 and lag-3 raw autocorrelation
lag2_pairs = []
lag3_pairs = []
for folio in valid_folios:
    seq = folio_qo_sequences[folio]
    indices = [s[0] for s in seq]
    qo_vals = [s[2] for s in seq]
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            gap = indices[j] - indices[i]
            if gap == 2:
                lag2_pairs.append((qo_vals[i], qo_vals[j]))
            elif gap == 3:
                lag3_pairs.append((qo_vals[i], qo_vals[j]))

rho_lag2, p_lag2 = 0.0, 1.0
if len(lag2_pairs) >= 3:
    x2 = np.array([p[0] for p in lag2_pairs])
    y2 = np.array([p[1] for p in lag2_pairs])
    rho_lag2, p_lag2 = safe_spearmanr(x2, y2)

rho_lag3, p_lag3 = 0.0, 1.0
if len(lag3_pairs) >= 3:
    x3 = np.array([p[0] for p in lag3_pairs])
    y3 = np.array([p[1] for p in lag3_pairs])
    rho_lag3, p_lag3 = safe_spearmanr(x3, y3)

print(f"\n  Lag-2 autocorrelation: rho={rho_lag2:.4f}, p={p_lag2:.2e} (n={len(lag2_pairs)})")
print(f"  Lag-3 autocorrelation: rho={rho_lag3:.4f}, p={p_lag3:.2e} (n={len(lag3_pairs)})")

# Permutation test for lag-1
perm_lag1_rhos = []
for perm_i in range(N_PERMUTATIONS):
    perm_pairs = []
    for folio in valid_folios:
        seq = list(folio_qo_sequences[folio])
        # Shuffle QO fractions within folio, keep positions fixed
        qo_vals_shuffled = [s[2] for s in seq]
        np.random.shuffle(qo_vals_shuffled)
        shuffled_seq = [(seq[k][0], seq[k][1], qo_vals_shuffled[k]) for k in range(len(seq))]
        for i in range(len(shuffled_seq) - 1):
            idx_a = shuffled_seq[i][0]
            idx_b = shuffled_seq[i + 1][0]
            if idx_b - idx_a == 1:
                perm_pairs.append((shuffled_seq[i][2], shuffled_seq[i + 1][2]))
    if len(perm_pairs) >= 3:
        px = np.array([p[0] for p in perm_pairs])
        py = np.array([p[1] for p in perm_pairs])
        r, _ = safe_spearmanr(px, py)
        perm_lag1_rhos.append(r)
    else:
        perm_lag1_rhos.append(0.0)

p_perm_lag1 = np.mean([1 for r in perm_lag1_rhos if abs(r) >= abs(rho_raw)])
print(f"\n  Permutation test for lag-1:")
print(f"    Observed rho: {rho_raw:.4f}")
print(f"    Permuted mean rho: {np.mean(perm_lag1_rhos):.4f}")
print(f"    Two-sided p: {p_perm_lag1:.4f}")

test5_results = {
    'n_eligible_lines': total_qo_lines,
    'min_en_per_line': MIN_EN_PER_LINE,
    'lag1_raw': {
        'n_pairs': len(lag1_pairs_raw),
        'spearman_rho': round(rho_raw, 4),
        'p_value': float(p_raw),
    },
    'lag1_partial': {
        'n_pairs': len(lag1_pairs_controlled),
        'spearman_rho': round(rho_partial, 4),
        'p_value': float(p_partial),
    },
    'lag2': {
        'n_pairs': len(lag2_pairs),
        'spearman_rho': round(rho_lag2, 4),
        'p_value': float(p_lag2),
    },
    'lag3': {
        'n_pairs': len(lag3_pairs),
        'spearman_rho': round(rho_lag3, 4),
        'p_value': float(p_lag3),
    },
    'permutation_lag1': {
        'observed_rho': round(rho_raw, 4),
        'perm_mean_rho': round(float(np.mean(perm_lag1_rhos)), 4),
        'two_sided_p': round(float(p_perm_lag1), 4),
    },
}


# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\n  T1 Adjacent MIDDLE Overlap:")
print(f"    obs={test1_results['grand_observed_jaccard']:.4f} vs perm={test1_results['grand_permuted_jaccard']:.4f}")
print(f"    diff={test1_results['difference']:+.4f}, sig folios: {test1_results['pct_significant']:.1f}%")

print(f"\n  T2 Novelty Curve:")
print(f"    first_half_frac={test2_results['grand_first_half_fraction']:.4f} vs perm={test2_results['grand_permuted_first_half']:.4f}")
print(f"    FL={classifications['FRONT_LOADED']} BL={classifications['BACK_LOADED']} UN={classifications['UNIFORM']}")

print(f"\n  T3 Boundary Bigrams:")
print(f"    H_boundary={test3_results['h_boundary']:.4f} vs H_within={test3_results['h_within']:.4f}")
print(f"    ratio={test3_results['h_ratio_boundary_to_within']}")
if 'chi2' in test3_results['chi_square']:
    print(f"    chi2={test3_results['chi_square']['chi2']}, p={test3_results['chi_square']['p']:.2e}")

print(f"\n  T4 CC Trigger Autocorrelation:")
print(f"    self_transition={test4_results['self_transition_fraction']:.4f} vs perm={test4_results['perm_self_transition_mean']:.4f}")
print(f"    p={test4_results['p_value_self_transition']:.4f}")

print(f"\n  T5 EN Lane Autocorrelation:")
print(f"    lag1_raw rho={test5_results['lag1_raw']['spearman_rho']:.4f}, p={test5_results['lag1_raw']['p_value']:.2e}")
print(f"    lag1_partial rho={test5_results['lag1_partial']['spearman_rho']:.4f}, p={test5_results['lag1_partial']['p_value']:.2e}")
print(f"    perm p={test5_results['permutation_lag1']['two_sided_p']:.4f}")


# ============================================================
# SAVE
# ============================================================
results = {
    'metadata': {
        'phase': 'B_LINE_SEQUENTIAL_STRUCTURE',
        'script': 'line_sequential_coupling',
        'timestamp': datetime.now().isoformat(),
        'total_b_tokens': total_b_tokens,
        'valid_folios': n_folios,
        'total_lines': n_lines_total,
        'n_permutations': N_PERMUTATIONS,
        'min_lines_per_folio': MIN_LINES_PER_FOLIO,
    },
    'test1_adjacent_middle_overlap': test1_results,
    'test2_novelty_curve': test2_results,
    'test3_boundary_bigrams': test3_results,
    'test4_cc_trigger_autocorrelation': test4_results,
    'test5_en_lane_autocorrelation': test5_results,
}

output_path = RESULTS_DIR / 'line_sequential_coupling.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {output_path}")
print("\nDone.")
