"""
SID-05: Attentional Pacing vs Other Non-Encoding Models

FINAL INTERNAL DISCRIMINATIVE PHASE
Tier 4: Speculative, Eliminative

Tests whether non-executive residue is best explained as:
- Model A: Attentional pacing / occupation
- Model B: Place-keeping / orientation
- Model C: Mechanical / scribal noise

All are non-semantic. SID-05 asks only which survives best.
"""

import sys
import os
import json
import math
import random
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, r'C:\git\voynich')

# =============================================================================
# CONSTANTS
# =============================================================================

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

HAZARD_TOKENS = {'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey',
                 'l', 'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol',
                 'ol', 'shor', 'dar', 'qokaiin', 'qokedy'}

KERNEL_CHARS = {'k', 'h', 'e'}

# =============================================================================
# DATA LOADING
# =============================================================================

def load_transcription():
    """Load transcription with full metadata."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # Filter to H (PRIMARY) transcriber track only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').lower()
                folio = parts[2].strip('"')
                section = parts[3].strip('"')

                # Line position if available
                try:
                    line_num = int(parts[1].strip('"')) if len(parts) > 1 else 0
                except:
                    line_num = 0

                if word and not word.startswith('*'):
                    data.append({
                        'token': word,
                        'folio': folio,
                        'section': section,
                        'line': line_num
                    })

    return data


def load_ops2_regimes():
    """Load OPS-2 regime assignments."""
    filepath = r'C:\git\voynich\phases\OPS2_control_strategy_clustering\ops2_folio_cluster_assignments.json'

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return {folio: info['cluster_id'] for folio, info in data['assignments'].items()}


def is_grammar(token: str) -> bool:
    """Check if token is grammar (operational) vs residue."""
    for p in GRAMMAR_PREFIXES:
        if token.startswith(p): return True
    for s in GRAMMAR_SUFFIXES:
        if token.endswith(s): return True
    return False


def is_hazard_token(token: str) -> bool:
    """Check if token is involved in forbidden transitions."""
    return token in HAZARD_TOKENS


def has_kernel_char(token: str) -> bool:
    """Check if token contains kernel characters."""
    return any(c in token for c in KERNEL_CHARS)


# =============================================================================
# TEST 5.1: VARIABILITY SUPPRESSION NEAR ACUTE HAZARDS
# =============================================================================

def test_5_1_variability_suppression(data: List[Dict], n_shuffles: int = 30) -> Dict:
    """
    Test 5.1: Variability Suppression Near Acute Hazards

    Model A predicts: Lower entropy, shorter runs near hazards
    Model B predicts: Unchanged
    Model C predicts: Unchanged
    """
    print("Test 5.1: VARIABILITY SUPPRESSION NEAR ACUTE HAZARDS")

    # Find hazard positions and residue positions
    hazard_positions = []
    residue_data = []

    for i, d in enumerate(data):
        if is_hazard_token(d['token']):
            hazard_positions.append(i)
        if not is_grammar(d['token']):
            residue_data.append((i, d['token']))

    if len(hazard_positions) < 10 or len(residue_data) < 100:
        return {'status': 'INSUFFICIENT_DATA'}

    # Classify residue as near (<=3) or far (>3) from hazard
    near_tokens = []
    far_tokens = []

    for pos, token in residue_data:
        min_dist = min(abs(pos - hp) for hp in hazard_positions)
        if min_dist <= 3:
            near_tokens.append(token)
        else:
            far_tokens.append(token)

    if len(near_tokens) < 20 or len(far_tokens) < 50:
        return {'status': 'INSUFFICIENT_SPLIT'}

    # Compute entropy
    def entropy(tokens):
        counts = Counter(tokens)
        total = len(tokens)
        return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)

    near_entropy = entropy(near_tokens)
    far_entropy = entropy(far_tokens)
    entropy_diff = far_entropy - near_entropy  # Positive = near is lower (Model A)

    # Compute mean run length
    def mean_run_length(tokens):
        if len(tokens) < 2:
            return 1.0
        runs = []
        current = tokens[0]
        length = 1
        for t in tokens[1:]:
            if t == current:
                length += 1
            else:
                runs.append(length)
                current = t
                length = 1
        runs.append(length)
        return np.mean(runs)

    near_run = mean_run_length(near_tokens)
    far_run = mean_run_length(far_tokens)
    run_diff = far_run - near_run  # Positive = near is shorter (Model A)

    # Null model: shuffle assignment
    null_entropy_diffs = []
    null_run_diffs = []
    all_residue = [t for _, t in residue_data]

    for _ in range(n_shuffles):
        random.shuffle(all_residue)
        n_near = len(near_tokens)
        null_near = all_residue[:n_near]
        null_far = all_residue[n_near:]

        null_entropy_diffs.append(entropy(null_far) - entropy(null_near))
        null_run_diffs.append(mean_run_length(null_far) - mean_run_length(null_near))

    # Z-scores
    z_entropy = (entropy_diff - np.mean(null_entropy_diffs)) / np.std(null_entropy_diffs) if np.std(null_entropy_diffs) > 0 else 0
    z_run = (run_diff - np.mean(null_run_diffs)) / np.std(null_run_diffs) if np.std(null_run_diffs) > 0 else 0

    result = {
        'near_count': len(near_tokens),
        'far_count': len(far_tokens),
        'near_entropy': round(near_entropy, 3),
        'far_entropy': round(far_entropy, 3),
        'entropy_diff': round(entropy_diff, 3),
        'z_entropy': round(z_entropy, 2),
        'near_run_length': round(near_run, 3),
        'far_run_length': round(far_run, 3),
        'run_diff': round(run_diff, 3),
        'z_run': round(z_run, 2)
    }

    # Model A: lower entropy AND shorter runs near hazards
    if z_entropy > 1.5 or z_run > 1.5:
        result['verdict'] = 'MODEL_A'
        result['interpretation'] = 'Variability suppressed near hazards (supports attentional pacing)'
    elif z_entropy < -1.5 or z_run < -1.5:
        result['verdict'] = 'FALSIFIED_A'
        result['interpretation'] = 'Increased complexity near hazards (contradicts Model A)'
    else:
        result['verdict'] = 'NULL'
        result['interpretation'] = 'No significant variability difference'

    print(f"  Near entropy: {near_entropy:.3f}, Far: {far_entropy:.3f}, z={z_entropy:.2f}")
    print(f"  Near run: {near_run:.3f}, Far: {far_run:.3f}, z={z_run:.2f}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# TEST 5.2: POSITION ADVANCEMENT CORRELATION
# =============================================================================

def test_5_2_position_correlation(data: List[Dict]) -> Dict:
    """
    Test 5.2: Position Advancement Correlation

    Model A predicts: Independent of page position
    Model B predicts: Correlated with line/folio advancement
    """
    print("Test 5.2: POSITION ADVANCEMENT CORRELATION")

    # Get residue tokens with positions
    residue_positions = []

    for i, d in enumerate(data):
        if not is_grammar(d['token']):
            residue_positions.append({
                'token': d['token'],
                'global_pos': i,
                'line': d['line'],
                'folio': d['folio']
            })

    if len(residue_positions) < 100:
        return {'status': 'INSUFFICIENT_DATA'}

    # Test 1: Does token type correlate with global position?
    # Sample tokens and their positions
    sample_size = min(2000, len(residue_positions))
    sample = random.sample(residue_positions, sample_size)

    # Encode tokens as integers
    token_to_id = {}
    for r in sample:
        if r['token'] not in token_to_id:
            token_to_id[r['token']] = len(token_to_id)

    positions = [r['global_pos'] for r in sample]
    token_ids = [token_to_id[r['token']] for r in sample]

    # Correlation between position and token ID
    # (This is crude but tests if tokens systematically change with position)
    corr_global, p_global = scipy_stats.spearmanr(positions, token_ids)

    # Test 2: Does token type correlate with line number?
    lines = [r['line'] for r in sample]
    corr_line, p_line = scipy_stats.spearmanr(lines, token_ids)

    result = {
        'sample_size': sample_size,
        'unique_tokens': len(token_to_id),
        'global_position_correlation': round(corr_global, 4),
        'global_position_p': round(p_global, 4),
        'line_correlation': round(corr_line, 4),
        'line_p': round(p_line, 4)
    }

    # Strong correlation kills Model A, supports Model B
    if abs(corr_global) > 0.1 and p_global < 0.01:
        result['verdict'] = 'MODEL_B'
        result['interpretation'] = 'Token type correlates with position (supports place-keeping)'
    elif abs(corr_line) > 0.1 and p_line < 0.01:
        result['verdict'] = 'MODEL_B'
        result['interpretation'] = 'Token type correlates with line (supports place-keeping)'
    else:
        result['verdict'] = 'MODEL_A'
        result['interpretation'] = 'Token type independent of position (supports attentional pacing)'

    print(f"  Global position correlation: r={corr_global:.4f}, p={p_global:.4f}")
    print(f"  Line correlation: r={corr_line:.4f}, p={p_line:.4f}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# TEST 5.3: CHRONIC HAZARD DENSITY VS WRITING DENSITY
# =============================================================================

def test_5_3_chronic_hazard_density(data: List[Dict]) -> Dict:
    """
    Test 5.3: Chronic Hazard Density vs Writing Density

    Model A predicts: More residue in hazard-DENSE folios (sustained vigilance)
    Note: This is DISTINCT from acute hazard avoidance (Test 5.1)
    """
    print("Test 5.3: CHRONIC HAZARD DENSITY VS WRITING DENSITY")

    # Compute per-folio statistics
    folio_stats = defaultdict(lambda: {'total': 0, 'residue': 0, 'hazard': 0})

    for d in data:
        folio = d['folio']
        folio_stats[folio]['total'] += 1
        if not is_grammar(d['token']):
            folio_stats[folio]['residue'] += 1
        if is_hazard_token(d['token']):
            folio_stats[folio]['hazard'] += 1

    # Filter folios with enough tokens
    valid_folios = [(f, s) for f, s in folio_stats.items() if s['total'] >= 50]

    if len(valid_folios) < 20:
        return {'status': 'INSUFFICIENT_FOLIOS'}

    # Compute densities
    hazard_densities = []
    residue_densities = []

    for folio, stats in valid_folios:
        hazard_densities.append(stats['hazard'] / stats['total'])
        residue_densities.append(stats['residue'] / stats['total'])

    # Correlation
    corr, p_value = scipy_stats.spearmanr(hazard_densities, residue_densities)

    result = {
        'n_folios': len(valid_folios),
        'mean_hazard_density': round(np.mean(hazard_densities), 4),
        'mean_residue_density': round(np.mean(residue_densities), 4),
        'correlation': round(corr, 4),
        'p_value': round(p_value, 4)
    }

    # Model A: positive correlation (more hazards -> more residue for vigilance)
    if corr > 0.2 and p_value < 0.05:
        result['verdict'] = 'MODEL_A'
        result['interpretation'] = 'Hazard-dense folios have more residue (sustained vigilance)'
    elif corr < -0.2 and p_value < 0.05:
        result['verdict'] = 'OPPOSITE'
        result['interpretation'] = 'Hazard-dense folios have less residue (contradicts Model A)'
    else:
        result['verdict'] = 'NULL'
        result['interpretation'] = 'No folio-level relationship'

    print(f"  Folios analyzed: {len(valid_folios)}")
    print(f"  Hazard-Residue correlation: r={corr:.4f}, p={p_value:.4f}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# TEST 5.4: INTERRUPTIBILITY TEST
# =============================================================================

def test_5_4_interruptibility(data: List[Dict]) -> Dict:
    """
    Test 5.4: Interruptibility Test

    Model A predicts: Residue runs terminate sharply at grammar transitions
    Model B predicts: Gradual continuation
    Model C predicts: Random termination
    """
    print("Test 5.4: INTERRUPTIBILITY TEST")

    # Find grammar tokens (transitions) and residue runs
    grammar_positions = set()
    kernel_positions = set()

    for i, d in enumerate(data):
        if is_grammar(d['token']):
            grammar_positions.add(i)
        if has_kernel_char(d['token']):
            kernel_positions.add(i)

    # Find residue runs and where they end
    runs = []
    in_run = False
    run_start = 0

    for i, d in enumerate(data):
        is_res = not is_grammar(d['token'])

        if is_res and not in_run:
            in_run = True
            run_start = i
        elif not is_res and in_run:
            in_run = False
            run_end = i - 1
            run_length = run_end - run_start + 1
            # What terminated it?
            terminator = 'grammar' if i in grammar_positions else 'other'
            next_is_kernel = i in kernel_positions
            runs.append({
                'start': run_start,
                'end': run_end,
                'length': run_length,
                'terminator': terminator,
                'next_is_kernel': next_is_kernel
            })

    if len(runs) < 30:
        return {'status': 'INSUFFICIENT_RUNS'}

    # What fraction of runs end at grammar?
    grammar_terminated = sum(1 for r in runs if r['terminator'] == 'grammar')
    kernel_terminated = sum(1 for r in runs if r['next_is_kernel'])

    grammar_rate = grammar_terminated / len(runs)
    kernel_rate = kernel_terminated / len(runs)

    # Expected by chance (proportion of grammar in corpus)
    expected_grammar_rate = len(grammar_positions) / len(data)

    # Chi-square test
    observed = [grammar_terminated, len(runs) - grammar_terminated]
    expected = [expected_grammar_rate * len(runs), (1 - expected_grammar_rate) * len(runs)]

    if min(expected) >= 5:
        chi2, p_value = scipy_stats.chisquare(observed, expected)
    else:
        chi2, p_value = 0, 1.0

    result = {
        'n_runs': len(runs),
        'grammar_terminated_rate': round(grammar_rate, 4),
        'kernel_terminated_rate': round(kernel_rate, 4),
        'expected_rate': round(expected_grammar_rate, 4),
        'chi2': round(chi2, 2),
        'p_value': round(p_value, 4)
    }

    # Model A: runs terminate preferentially at grammar (sharp interruptibility)
    if grammar_rate > expected_grammar_rate * 1.2 and p_value < 0.05:
        result['verdict'] = 'MODEL_A'
        result['interpretation'] = 'Runs terminate sharply at grammar transitions'
    elif grammar_rate < expected_grammar_rate * 0.8 and p_value < 0.05:
        result['verdict'] = 'OPPOSITE'
        result['interpretation'] = 'Runs avoid grammar transitions'
    else:
        result['verdict'] = 'NULL'
        result['interpretation'] = 'Random termination pattern'

    print(f"  Runs analyzed: {len(runs)}")
    print(f"  Grammar termination: {grammar_rate:.4f} (expected: {expected_grammar_rate:.4f})")
    print(f"  Chi2={chi2:.2f}, p={p_value:.4f}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# TEST 5.5: CROSS-PROGRAM SIMILARITY VIA OPS-2 REGIMES
# =============================================================================

def test_5_5_regime_similarity(data: List[Dict], regimes: Dict[str, str]) -> Dict:
    """
    Test 5.5: Cross-Program Similarity via OPS-2 Regimes

    Model A predicts: Same regime -> similar STATS, different TOKENS
    Model B predicts: Same regime -> same TOKENS
    """
    print("Test 5.5: CROSS-PROGRAM SIMILARITY VIA OPS-2 REGIMES")

    # Group residue by folio
    folio_residue = defaultdict(list)

    for d in data:
        if not is_grammar(d['token']):
            folio_residue[d['folio']].append(d['token'])

    # Group folios by regime
    regime_folios = defaultdict(list)
    for folio, residue in folio_residue.items():
        if folio in regimes and len(residue) >= 20:
            regime = regimes[folio]
            regime_folios[regime].append((folio, residue))

    if len(regime_folios) < 2:
        return {'status': 'INSUFFICIENT_REGIMES'}

    # Compute stats per folio
    def folio_stats(tokens):
        if len(tokens) < 5:
            return None

        # Entropy
        counts = Counter(tokens)
        total = len(tokens)
        entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())

        # Clustering (self-transition rate)
        cluster = sum(1 for i in range(len(tokens)-1) if tokens[i] == tokens[i+1]) / (len(tokens)-1)

        # Type-token ratio
        ttr = len(counts) / total

        return {'entropy': entropy, 'clustering': cluster, 'ttr': ttr, 'vocab': set(tokens)}

    # Compute within-regime and between-regime similarities
    regime_stats = {}
    for regime, folios in regime_folios.items():
        stats_list = [folio_stats(tokens) for _, tokens in folios if folio_stats(tokens)]
        if len(stats_list) >= 2:
            regime_stats[regime] = stats_list

    if len(regime_stats) < 2:
        return {'status': 'INSUFFICIENT_REGIME_DATA'}

    # Within-regime stat variance
    within_stat_vars = []
    within_vocab_overlaps = []

    for regime, stats_list in regime_stats.items():
        entropies = [s['entropy'] for s in stats_list]
        clusters = [s['clustering'] for s in stats_list]

        if len(entropies) >= 2:
            within_stat_vars.append(np.std(entropies))
            within_stat_vars.append(np.std(clusters))

        # Vocabulary overlap within regime
        for i, s1 in enumerate(stats_list):
            for s2 in stats_list[i+1:]:
                overlap = len(s1['vocab'] & s2['vocab']) / len(s1['vocab'] | s2['vocab'])
                within_vocab_overlaps.append(overlap)

    # Between-regime comparisons
    between_stat_diffs = []
    between_vocab_overlaps = []

    regime_list = list(regime_stats.keys())
    for i, r1 in enumerate(regime_list):
        for r2 in regime_list[i+1:]:
            for s1 in regime_stats[r1]:
                for s2 in regime_stats[r2]:
                    between_stat_diffs.append(abs(s1['entropy'] - s2['entropy']))
                    overlap = len(s1['vocab'] & s2['vocab']) / len(s1['vocab'] | s2['vocab'])
                    between_vocab_overlaps.append(overlap)

    mean_within_var = np.mean(within_stat_vars) if within_stat_vars else 0
    mean_within_vocab = np.mean(within_vocab_overlaps) if within_vocab_overlaps else 0
    mean_between_diff = np.mean(between_stat_diffs) if between_stat_diffs else 0
    mean_between_vocab = np.mean(between_vocab_overlaps) if between_vocab_overlaps else 0

    result = {
        'n_regimes': len(regime_stats),
        'within_stat_variance': round(mean_within_var, 4),
        'within_vocab_overlap': round(mean_within_vocab, 4),
        'between_stat_difference': round(mean_between_diff, 4),
        'between_vocab_overlap': round(mean_between_vocab, 4)
    }

    # Model A: similar stats (low within-variance) but different tokens (low vocab overlap)
    # Model B: same tokens (high vocab overlap)

    if mean_within_vocab < 0.3 and mean_within_var < mean_between_diff:
        result['verdict'] = 'MODEL_A'
        result['interpretation'] = 'Same regime = similar stats, different tokens (embodied response)'
    elif mean_within_vocab > 0.5:
        result['verdict'] = 'MODEL_B'
        result['interpretation'] = 'Same regime = same tokens (symbolic habit)'
    else:
        result['verdict'] = 'NULL'
        result['interpretation'] = 'No clear pattern'

    print(f"  Regimes analyzed: {len(regime_stats)}")
    print(f"  Within-regime vocab overlap: {mean_within_vocab:.4f}")
    print(f"  Within-regime stat variance: {mean_within_var:.4f}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# TEST 5.6: NON-HUMAN BASELINE STRESS TEST
# =============================================================================

def test_5_6_nonhuman_baseline(data: List[Dict], n_shuffles: int = 30) -> Dict:
    """
    Test 5.6: Non-Human Baseline Stress Test

    Tests whether ANY mechanical process can reproduce all signatures jointly.
    """
    print("Test 5.6: NON-HUMAN BASELINE STRESS TEST")

    # Extract observed statistics
    residue_tokens = [d['token'] for d in data if not is_grammar(d['token'])]
    residue_sections = [d['section'] for d in data if not is_grammar(d['token'])]

    if len(residue_tokens) < 100:
        return {'status': 'INSUFFICIENT_DATA'}

    # Observed stats
    def compute_stats(tokens, sections):
        # Clustering
        cluster = sum(1 for i in range(len(tokens)-1) if tokens[i] == tokens[i+1]) / (len(tokens)-1)

        # Section exclusivity
        type_sects = defaultdict(set)
        for t, s in zip(tokens, sections):
            type_sects[t].add(s)
        excl = sum(1 for sects in type_sects.values() if len(sects) == 1) / len(type_sects)

        # Run length CV
        runs = []
        current = tokens[0]
        length = 1
        for t in tokens[1:]:
            if t == current:
                length += 1
            else:
                runs.append(length)
                current = t
                length = 1
        runs.append(length)
        cv = np.std(runs) / np.mean(runs) if np.mean(runs) > 0 else 0

        return {'clustering': cluster, 'exclusivity': excl, 'run_cv': cv}

    observed = compute_stats(residue_tokens, residue_sections)

    # Baseline 1: Shuffled tokens (random order)
    shuffled_stats = []
    for _ in range(n_shuffles):
        shuffled = residue_tokens.copy()
        random.shuffle(shuffled)
        shuffled_stats.append(compute_stats(shuffled, residue_sections))

    # Baseline 2: Shuffled sections (random section assignment)
    sect_shuffled_stats = []
    for _ in range(n_shuffles):
        shuf_sects = residue_sections.copy()
        random.shuffle(shuf_sects)
        sect_shuffled_stats.append(compute_stats(residue_tokens, shuf_sects))

    # Baseline 3: Random tokens (from vocabulary)
    vocab = list(set(residue_tokens))
    random_stats = []
    for _ in range(n_shuffles):
        random_tokens = [random.choice(vocab) for _ in range(len(residue_tokens))]
        random_stats.append(compute_stats(random_tokens, residue_sections))

    # Check which baselines match observed
    def matches(baseline_stats, observed, stat_name, tolerance=0.1):
        baseline_values = [s[stat_name] for s in baseline_stats]
        mean = np.mean(baseline_values)
        std = np.std(baseline_values)
        return abs(mean - observed[stat_name]) < 2 * std + tolerance

    shuffled_match = all([
        matches(shuffled_stats, observed, 'clustering'),
        matches(shuffled_stats, observed, 'exclusivity'),
        matches(shuffled_stats, observed, 'run_cv')
    ])

    sect_match = all([
        matches(sect_shuffled_stats, observed, 'clustering'),
        matches(sect_shuffled_stats, observed, 'exclusivity'),
        matches(sect_shuffled_stats, observed, 'run_cv')
    ])

    random_match = all([
        matches(random_stats, observed, 'clustering'),
        matches(random_stats, observed, 'exclusivity'),
        matches(random_stats, observed, 'run_cv')
    ])

    result = {
        'observed_clustering': round(observed['clustering'], 4),
        'observed_exclusivity': round(observed['exclusivity'], 4),
        'observed_run_cv': round(observed['run_cv'], 4),
        'shuffled_clustering': round(np.mean([s['clustering'] for s in shuffled_stats]), 4),
        'random_clustering': round(np.mean([s['clustering'] for s in random_stats]), 4),
        'shuffled_match_all': shuffled_match,
        'sect_shuffled_match_all': sect_match,
        'random_match_all': random_match
    }

    # Model C fails if NO baseline matches all stats jointly
    if not (shuffled_match or sect_match or random_match):
        result['verdict'] = 'MODEL_C_FAILS'
        result['interpretation'] = 'No mechanical baseline reproduces all signatures'
    else:
        result['verdict'] = 'MODEL_C_SURVIVES'
        if shuffled_match:
            result['interpretation'] = 'Shuffled baseline matches (mechanical possible)'
        elif sect_match:
            result['interpretation'] = 'Section-shuffled baseline matches'
        else:
            result['interpretation'] = 'Random baseline matches'

    print(f"  Observed: clustering={observed['clustering']:.4f}, excl={observed['exclusivity']:.4f}")
    print(f"  Shuffled match all: {shuffled_match}")
    print(f"  Random match all: {random_match}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# TEST 5.7: BOUNDARY RESET TEST
# =============================================================================

def test_5_7_boundary_reset(data: List[Dict]) -> Dict:
    """
    Test 5.7: Boundary Reset Test

    Model A predicts: Clustering RESETS at section boundaries
    Model B predicts: Gradual decay across boundaries
    """
    print("Test 5.7: BOUNDARY RESET TEST")

    # Find section boundaries
    boundaries = []
    for i in range(1, len(data)):
        if data[i]['section'] != data[i-1]['section']:
            boundaries.append(i)

    if len(boundaries) < 5:
        return {'status': 'INSUFFICIENT_BOUNDARIES'}

    # Extract residue tokens with section info
    residue = [(i, d['token'], d['section']) for i, d in enumerate(data) if not is_grammar(d['token'])]

    if len(residue) < 100:
        return {'status': 'INSUFFICIENT_RESIDUE'}

    # Compute within-section vs cross-section autocorrelation
    within_matches = 0
    within_total = 0
    cross_matches = 0
    cross_total = 0

    for i in range(len(residue) - 1):
        pos1, tok1, sect1 = residue[i]
        pos2, tok2, sect2 = residue[i + 1]

        if sect1 == sect2:
            within_total += 1
            if tok1 == tok2:
                within_matches += 1
        else:
            cross_total += 1
            if tok1 == tok2:
                cross_matches += 1

    within_rate = within_matches / within_total if within_total > 0 else 0
    cross_rate = cross_matches / cross_total if cross_total > 0 else 0

    # Fisher's exact test
    table = [[within_matches, within_total - within_matches],
             [cross_matches, cross_total - cross_matches]]

    if min(within_total, cross_total) > 0:
        odds_ratio, p_value = scipy_stats.fisher_exact(table)
    else:
        odds_ratio, p_value = 1.0, 1.0

    result = {
        'within_section_matches': within_matches,
        'within_section_total': within_total,
        'within_section_rate': round(within_rate, 4),
        'cross_section_matches': cross_matches,
        'cross_section_total': cross_total,
        'cross_section_rate': round(cross_rate, 4),
        'odds_ratio': round(odds_ratio, 3),
        'p_value': round(p_value, 4)
    }

    # Model A: within-section clustering >> cross-section (reset at boundaries)
    if within_rate > cross_rate * 1.5 and p_value < 0.05:
        result['verdict'] = 'MODEL_A'
        result['interpretation'] = 'Clustering resets at section boundaries'
    elif within_rate < cross_rate * 0.8 and p_value < 0.05:
        result['verdict'] = 'OPPOSITE'
        result['interpretation'] = 'Cross-section clustering higher (contradicts Model A)'
    else:
        result['verdict'] = 'NULL'
        result['interpretation'] = 'No boundary reset detected'

    print(f"  Within-section clustering: {within_rate:.4f}")
    print(f"  Cross-section clustering: {cross_rate:.4f}")
    print(f"  Odds ratio: {odds_ratio:.3f}, p={p_value:.4f}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# TEST 5.8: MORPHOLOGICAL COMPLEXITY GRADIENT
# =============================================================================

def test_5_8_morphological_complexity(data: List[Dict], n_shuffles: int = 30) -> Dict:
    """
    Test 5.8: Morphological Complexity Gradient

    Model A predicts: SIMPLER tokens near high-risk zones (automatic writing)
    """
    print("Test 5.8: MORPHOLOGICAL COMPLEXITY GRADIENT")

    # Find hazard positions
    hazard_positions = set()
    for i, d in enumerate(data):
        if is_hazard_token(d['token']):
            hazard_positions.add(i)

    if len(hazard_positions) < 10:
        return {'status': 'INSUFFICIENT_HAZARDS'}

    # Compute complexity metrics for residue tokens
    def token_complexity(token):
        # Length
        length = len(token)

        # Unique characters
        unique = len(set(token))

        # Complexity score
        return length + unique * 0.5

    # Classify residue by proximity to hazard
    near_complexity = []
    far_complexity = []

    for i, d in enumerate(data):
        if not is_grammar(d['token']):
            min_dist = min(abs(i - hp) for hp in hazard_positions)
            complexity = token_complexity(d['token'])

            if min_dist <= 3:
                near_complexity.append(complexity)
            else:
                far_complexity.append(complexity)

    if len(near_complexity) < 20 or len(far_complexity) < 50:
        return {'status': 'INSUFFICIENT_SPLIT'}

    near_mean = np.mean(near_complexity)
    far_mean = np.mean(far_complexity)
    diff = far_mean - near_mean  # Positive = near is simpler (Model A)

    # Statistical test
    t_stat, p_value = scipy_stats.ttest_ind(far_complexity, near_complexity)

    # Effect size (Cohen's d)
    pooled_std = np.sqrt((np.var(near_complexity) + np.var(far_complexity)) / 2)
    cohens_d = diff / pooled_std if pooled_std > 0 else 0

    result = {
        'near_count': len(near_complexity),
        'far_count': len(far_complexity),
        'near_mean_complexity': round(near_mean, 3),
        'far_mean_complexity': round(far_mean, 3),
        'difference': round(diff, 3),
        't_statistic': round(t_stat, 2),
        'p_value': round(p_value, 4),
        'cohens_d': round(cohens_d, 3)
    }

    # Model A: simpler tokens near hazards (positive diff)
    if diff > 0 and p_value < 0.05:
        result['verdict'] = 'MODEL_A'
        result['interpretation'] = 'Simpler tokens near hazards (automatic writing)'
    elif diff < 0 and p_value < 0.05:
        result['verdict'] = 'OPPOSITE'
        result['interpretation'] = 'More complex tokens near hazards (contradicts Model A)'
    else:
        result['verdict'] = 'NULL'
        result['interpretation'] = 'No complexity gradient detected'

    print(f"  Near hazard complexity: {near_mean:.3f}")
    print(f"  Far from hazard: {far_mean:.3f}")
    print(f"  Difference: {diff:.3f}, p={p_value:.4f}, d={cohens_d:.3f}")
    print(f"  Verdict: {result['verdict']}")

    return result


# =============================================================================
# MAIN
# =============================================================================

def run_sid05():
    """Execute SID-05: Attentional Pacing vs Other Non-Encoding Models."""

    print("=" * 70)
    print("SID-05: ATTENTIONAL PACING VS OTHER NON-ENCODING MODELS")
    print("=" * 70)
    print()
    print("TIER 4: Final internal discriminative phase")
    print("Models: A (attentional pacing), B (place-keeping), C (mechanical)")
    print()

    random.seed(42)
    np.random.seed(42)

    # Load data
    print("Loading data...")
    data = load_transcription()
    print(f"  Total tokens: {len(data)}")

    regimes = load_ops2_regimes()
    print(f"  OPS-2 regimes loaded: {len(regimes)} folios")
    print()

    # Run all tests
    results = {}

    print("=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    print()

    results['5.1'] = test_5_1_variability_suppression(data)
    print()

    results['5.2'] = test_5_2_position_correlation(data)
    print()

    results['5.3'] = test_5_3_chronic_hazard_density(data)
    print()

    results['5.4'] = test_5_4_interruptibility(data)
    print()

    results['5.5'] = test_5_5_regime_similarity(data, regimes)
    print()

    results['5.6'] = test_5_6_nonhuman_baseline(data)
    print()

    results['5.7'] = test_5_7_boundary_reset(data)
    print()

    results['5.8'] = test_5_8_morphological_complexity(data)
    print()

    # Score models
    print("=" * 70)
    print("MODEL SCORING")
    print("=" * 70)
    print()

    model_a_wins = 0
    model_b_wins = 0
    model_c_wins = 0
    null_results = 0

    for test_id, result in results.items():
        verdict = result.get('verdict', 'NULL')

        if verdict == 'MODEL_A':
            model_a_wins += 1
        elif verdict == 'MODEL_B':
            model_b_wins += 1
        elif verdict == 'MODEL_C_SURVIVES':
            model_c_wins += 1
        elif verdict == 'MODEL_C_FAILS':
            model_a_wins += 1  # C failing supports A
        elif verdict in ['FALSIFIED_A', 'OPPOSITE']:
            model_b_wins += 1  # Contradicting A supports B
        else:
            null_results += 1

    print(f"Model A (Attentional Pacing) wins: {model_a_wins}/8")
    print(f"Model B (Place-keeping) wins: {model_b_wins}/8")
    print(f"Model C (Mechanical) wins: {model_c_wins}/8")
    print(f"Null results: {null_results}/8")
    print()

    # Determine winner
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    if model_a_wins >= 5:
        overall = 'MODEL_A_WINS'
        print("WINNER: MODEL A (Attentional Pacing)")
        print()
        print("The non-executive residue behaves like attentional pacing residue")
        print("produced by humans co-present with a hazard-constrained process.")
    elif model_b_wins >= 5:
        overall = 'MODEL_B_WINS'
        print("WINNER: MODEL B (Place-keeping)")
        print()
        print("The non-executive residue behaves like navigation/orientation aids.")
    elif model_c_wins >= 4:
        overall = 'MODEL_C_WINS'
        print("WINNER: MODEL C (Mechanical)")
        print()
        print("The non-executive residue can be explained by mechanical processes.")
    else:
        overall = 'UNDERDETERMINED'
        print("UNDERDETERMINED: No model wins decisively")
        print()
        print(f"A={model_a_wins}, B={model_b_wins}, C={model_c_wins}")

    print()
    print("=" * 70)
    print("INTERPRETIVE LIMITS")
    print("=" * 70)
    print()
    print("  - Tokens DO NOT encode anything")
    print("  - Tokens DO NOT mean anything")
    print("  - This is Tier 4 (speculative) only")
    print("  - Winner = best explanatory fit, not truth")
    print()
    print("=" * 70)
    print("SID-05 COMPLETE")
    print("=" * 70)

    return overall, results


if __name__ == "__main__":
    overall, results = run_sid05()
