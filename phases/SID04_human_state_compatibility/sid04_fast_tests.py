"""
SID-04: Human-State Compatibility Analysis (FAST VERSION)

EPISTEMIC TIER: 4 (SPECULATIVE COMPATIBILITY ONLY)
"""

import sys
import os
import math
import random
from collections import defaultdict, Counter
from typing import List, Dict, Tuple
import numpy as np
from scipy import stats

sys.path.insert(0, r'C:\git\voynich')

# =============================================================================
# DATA LOADING
# =============================================================================

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'), ('chol', 'r'),
    ('chedy', 'ee'), ('chey', 'chedy'), ('l', 'chol'), ('dy', 'aiin'),
    ('dy', 'chey'), ('or', 'dal'), ('ar', 'chol'), ('qo', 'shey'),
    ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'), ('dar', 'qokaiin'),
    ('qokaiin', 'qokedy')
]

HAZARD_TOKENS = set()
for a, b in FORBIDDEN_PAIRS:
    HAZARD_TOKENS.add(a)
    HAZARD_TOKENS.add(b)


def load_transcription():
    """Load transcription data."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    sections = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # Filter to H (PRIMARY) transcriber track only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"')
                section = parts[3].strip('"')
                if word and not word.startswith('*'):
                    tokens.append(word.lower())
                    sections.append(section)

    return tokens, sections


def is_grammar_token(token: str) -> bool:
    """Classify as grammar (operational) or residue (human-track)."""
    for pf in GRAMMAR_PREFIXES:
        if token.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if token.endswith(sf):
            return True
    return False


def classify_tokens(tokens):
    """Split into grammar and residue."""
    grammar = []
    residue = []
    residue_positions = []

    for i, t in enumerate(tokens):
        if is_grammar_token(t):
            grammar.append(t)
        else:
            residue.append(t)
            residue_positions.append(i)

    return grammar, residue, residue_positions


# =============================================================================
# FAST TESTS
# =============================================================================

def test_autocorrelation(residue_tokens, n_shuffles=50):
    """Test 1: Do residue tokens show temporal clustering?"""
    print("Test 1: Temporal Autocorrelation")

    if len(residue_tokens) < 50:
        return {'status': 'INSUFFICIENT_DATA'}

    # Compute self-transition rate (same token type repeated)
    def compute_self_rate(seq):
        matches = sum(1 for i in range(len(seq)-1) if seq[i] == seq[i+1])
        return matches / (len(seq) - 1)

    observed = compute_self_rate(residue_tokens)

    # Null: shuffle and recompute
    null_rates = []
    for _ in range(n_shuffles):
        shuffled = residue_tokens.copy()
        random.shuffle(shuffled)
        null_rates.append(compute_self_rate(shuffled))

    null_mean = np.mean(null_rates)
    null_std = np.std(null_rates)
    z_score = (observed - null_mean) / null_std if null_std > 0 else 0
    p_value = np.mean([1 if r >= observed else 0 for r in null_rates])

    result = {
        'observed_self_rate': round(observed, 4),
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'z_score': round(z_score, 2),
        'p_value': round(p_value, 4)
    }

    if z_score > 2:
        result['verdict'] = 'CONSISTENT'
        result['interpretation'] = 'Elevated clustering, consistent with state inertia'
    elif z_score > 1:
        result['verdict'] = 'WEAKLY_CONSISTENT'
        result['interpretation'] = 'Mild clustering effect'
    else:
        result['verdict'] = 'INCONSISTENT'
        result['interpretation'] = 'No clustering detected'

    print(f"  Self-rate: {observed:.4f} (null: {null_mean:.4f} ± {null_std:.4f})")
    print(f"  z-score: {z_score:.2f}, Verdict: {result['verdict']}")

    return result


def test_hazard_proximity(tokens, residue_positions, n_shuffles=50):
    """Test 2: Does residue distribution change near hazard tokens?"""
    print("Test 2: Hazard Proximity Deformation")

    # Find hazard positions
    hazard_pos = [i for i, t in enumerate(tokens) if t in HAZARD_TOKENS]

    if len(hazard_pos) < 10:
        return {'status': 'INSUFFICIENT_HAZARD_DATA'}

    # Compute mean distance from residue to nearest hazard
    def compute_mean_dist(res_pos, haz_pos):
        if not haz_pos:
            return float('inf')
        dists = []
        for rp in res_pos:
            dists.append(min(abs(rp - hp) for hp in haz_pos))
        return np.mean(dists)

    observed_dist = compute_mean_dist(residue_positions, hazard_pos)

    # Null: shuffle residue positions
    n_residue = len(residue_positions)
    all_positions = list(range(len(tokens)))

    null_dists = []
    for _ in range(n_shuffles):
        null_pos = random.sample(all_positions, n_residue)
        null_dists.append(compute_mean_dist(null_pos, hazard_pos))

    null_mean = np.mean(null_dists)
    null_std = np.std(null_dists)
    z_score = (observed_dist - null_mean) / null_std if null_std > 0 else 0

    result = {
        'observed_mean_dist': round(observed_dist, 2),
        'null_mean': round(null_mean, 2),
        'z_score': round(z_score, 2)
    }

    if z_score > 1.5:  # Further from hazard than expected
        result['verdict'] = 'CONSISTENT'
        result['interpretation'] = 'Residue avoids hazard zones (consistent with heightened state there)'
    elif z_score < -1.5:  # Closer to hazard
        result['verdict'] = 'OPPOSITE_SIGNAL'
        result['interpretation'] = 'Residue clusters near hazard zones'
    else:
        result['verdict'] = 'INCONSISTENT'
        result['interpretation'] = 'No hazard-proximity effect'

    print(f"  Mean distance: {observed_dist:.2f} (null: {null_mean:.2f})")
    print(f"  z-score: {z_score:.2f}, Verdict: {result['verdict']}")

    return result


def test_section_exclusivity(residue_tokens, residue_sections, n_shuffles=50):
    """Test 3: Are residue types section-exclusive?"""
    print("Test 3: Section Exclusivity")

    def compute_exclusivity(tokens, sections):
        type_sections = defaultdict(set)
        for t, s in zip(tokens, sections):
            type_sections[t].add(s)
        exclusive = sum(1 for sects in type_sections.values() if len(sects) == 1)
        return exclusive / len(type_sections) if type_sections else 0

    observed = compute_exclusivity(residue_tokens, residue_sections)

    # Null: shuffle section assignments
    null_excl = []
    for _ in range(n_shuffles):
        shuffled_sections = residue_sections.copy()
        random.shuffle(shuffled_sections)
        null_excl.append(compute_exclusivity(residue_tokens, shuffled_sections))

    null_mean = np.mean(null_excl)
    null_std = np.std(null_excl)
    z_score = (observed - null_mean) / null_std if null_std > 0 else 0

    result = {
        'observed_exclusivity': round(observed, 3),
        'null_mean': round(null_mean, 3),
        'z_score': round(z_score, 2)
    }

    if z_score > 3:
        result['verdict'] = 'STRONGLY_CONSISTENT'
        result['interpretation'] = 'High section exclusivity, consistent with section-conditioned state'
    elif z_score > 2:
        result['verdict'] = 'CONSISTENT'
        result['interpretation'] = 'Elevated section exclusivity'
    else:
        result['verdict'] = 'INCONSISTENT'
        result['interpretation'] = 'No section conditioning detected'

    print(f"  Exclusivity: {observed:.3f} (null: {null_mean:.3f})")
    print(f"  z-score: {z_score:.2f}, Verdict: {result['verdict']}")

    return result


def test_run_lengths(residue_tokens):
    """Test 4: Do run lengths fit geometric (memoryless)?"""
    print("Test 4: Run-Length Distribution")

    # Compute runs of same type
    runs = []
    current_type = None
    current_len = 0

    for t in residue_tokens:
        if t == current_type:
            current_len += 1
        else:
            if current_len > 0:
                runs.append(current_len)
            current_type = t
            current_len = 1
    if current_len > 0:
        runs.append(current_len)

    if len(runs) < 20:
        return {'status': 'INSUFFICIENT_DATA'}

    mean_run = np.mean(runs)
    cv = np.std(runs) / mean_run if mean_run > 0 else 0

    # Geometric CV = sqrt(1-p)/p where p = 1/mean
    p_geom = 1 / mean_run
    expected_cv = math.sqrt(1 - p_geom) / p_geom if p_geom < 1 else 1

    cv_ratio = cv / expected_cv if expected_cv > 0 else 0

    result = {
        'mean_run_length': round(mean_run, 2),
        'coefficient_of_variation': round(cv, 3),
        'expected_geometric_cv': round(expected_cv, 3),
        'cv_ratio': round(cv_ratio, 3)
    }

    if 0.8 < cv_ratio < 1.2:
        result['verdict'] = 'CONSISTENT'
        result['interpretation'] = 'Run lengths match geometric (memoryless), consistent with independent state transitions'
    elif cv_ratio > 1.2:
        result['verdict'] = 'OVERDISPERSED'
        result['interpretation'] = 'More variable than geometric, suggests clustered/sticky states'
    else:
        result['verdict'] = 'UNDERDISPERSED'
        result['interpretation'] = 'Less variable than geometric, suggests regularized structure'

    print(f"  Mean run: {mean_run:.2f}, CV: {cv:.3f} (geometric expect: {expected_cv:.3f})")
    print(f"  CV ratio: {cv_ratio:.3f}, Verdict: {result['verdict']}")

    return result


def test_boundary_asymmetry(tokens, residue_positions, sections, n_shuffles=50):
    """Test 5: Do residue patterns differ at section entry vs exit?"""
    print("Test 5: Boundary Asymmetry")

    # Find section boundaries
    boundaries = []
    for i in range(1, len(sections)):
        if sections[i] != sections[i-1]:
            boundaries.append(i)

    if len(boundaries) < 5:
        return {'status': 'INSUFFICIENT_BOUNDARIES'}

    residue_set = set(residue_positions)

    # Count residue in entry vs exit windows
    window = 5
    entry_count = 0
    exit_count = 0

    for b in boundaries:
        for i in range(max(0, b - window), b):
            if i in residue_set:
                exit_count += 1
        for i in range(b, min(len(tokens), b + window)):
            if i in residue_set:
                entry_count += 1

    # Asymmetry ratio
    total = entry_count + exit_count
    if total == 0:
        return {'status': 'NO_BOUNDARY_RESIDUE'}

    asymmetry = (entry_count - exit_count) / total

    # Null: shuffle positions
    null_asymm = []
    n_res = len(residue_positions)
    all_pos = list(range(len(tokens)))

    for _ in range(n_shuffles):
        null_pos = set(random.sample(all_pos, n_res))
        null_entry = sum(1 for b in boundaries for i in range(b, min(len(tokens), b + window)) if i in null_pos)
        null_exit = sum(1 for b in boundaries for i in range(max(0, b - window), b) if i in null_pos)
        null_total = null_entry + null_exit
        if null_total > 0:
            null_asymm.append((null_entry - null_exit) / null_total)

    if len(null_asymm) > 0:
        null_mean = np.mean(null_asymm)
        null_std = np.std(null_asymm)
        z_score = (asymmetry - null_mean) / null_std if null_std > 0 else 0
    else:
        null_mean = 0
        z_score = 0

    result = {
        'entry_count': entry_count,
        'exit_count': exit_count,
        'asymmetry': round(asymmetry, 3),
        'z_score': round(z_score, 2)
    }

    if abs(z_score) > 2:
        result['verdict'] = 'CONSISTENT'
        result['interpretation'] = f'Significant asymmetry ({"entry" if asymmetry > 0 else "exit"} biased)'
    else:
        result['verdict'] = 'INCONSISTENT'
        result['interpretation'] = 'No boundary asymmetry detected'

    print(f"  Entry: {entry_count}, Exit: {exit_count}, Asymmetry: {asymmetry:.3f}")
    print(f"  z-score: {z_score:.2f}, Verdict: {result['verdict']}")

    return result


def test_synthetic_model(residue_tokens, residue_sections, n_iter=50):
    """Test 6: Can a simple AR(1) model reproduce key stats?"""
    print("Test 6: Synthetic Operator Model")

    # Target statistics
    obs_vocab = len(set(residue_tokens))
    obs_ttr = obs_vocab / len(residue_tokens)
    obs_autocorr = sum(1 for i in range(len(residue_tokens)-1)
                       if residue_tokens[i] == residue_tokens[i+1]) / (len(residue_tokens)-1)

    # Build section emission model
    section_vocabs = defaultdict(Counter)
    for t, s in zip(residue_tokens, residue_sections):
        section_vocabs[s][t] += 1

    section_probs = {}
    for s, counts in section_vocabs.items():
        total = sum(counts.values())
        section_probs[s] = {t: c/total for t, c in counts.items()}

    # Generate with AR(1) state
    matches = {'vocab_ratio': [], 'ttr_ratio': [], 'autocorr_ratio': []}

    for _ in range(n_iter):
        synth_tokens = []
        state = random.random()  # Continuous state [0,1]
        ar_coef = 0.7

        for s in residue_sections:
            # Evolve state (AR(1) with noise)
            state = ar_coef * state + (1 - ar_coef) * random.random()

            # Emit token based on state + section
            if s in section_probs:
                tokens_list = list(section_probs[s].keys())
                probs = list(section_probs[s].values())
                # State biases selection (weakly)
                weights = [p * (1 + 0.1 * (state - 0.5)) for p in probs]
                total = sum(weights)
                weights = [w/total for w in weights]
                tok = random.choices(tokens_list, weights=weights)[0]
            else:
                tok = random.choice(residue_tokens)
            synth_tokens.append(tok)

        syn_vocab = len(set(synth_tokens))
        syn_ttr = syn_vocab / len(synth_tokens)
        syn_autocorr = sum(1 for i in range(len(synth_tokens)-1)
                          if synth_tokens[i] == synth_tokens[i+1]) / (len(synth_tokens)-1)

        matches['vocab_ratio'].append(syn_vocab / obs_vocab)
        matches['ttr_ratio'].append(syn_ttr / obs_ttr)
        matches['autocorr_ratio'].append(syn_autocorr / obs_autocorr if obs_autocorr > 0 else 1)

    # Average match quality (1.0 = perfect)
    def match_quality(ratios):
        return 1 - np.mean([abs(r - 1) for r in ratios])

    vocab_match = match_quality(matches['vocab_ratio'])
    ttr_match = match_quality(matches['ttr_ratio'])
    auto_match = match_quality(matches['autocorr_ratio'])
    overall = (vocab_match + ttr_match + auto_match) / 3

    result = {
        'vocab_match': round(vocab_match, 3),
        'ttr_match': round(ttr_match, 3),
        'autocorr_match': round(auto_match, 3),
        'overall_match': round(overall, 3)
    }

    if overall > 0.8:
        result['verdict'] = 'STRONGLY_CONSISTENT'
        result['interpretation'] = 'Simple AR(1) model reproduces key statistics well'
    elif overall > 0.6:
        result['verdict'] = 'CONSISTENT'
        result['interpretation'] = 'AR(1) model partially reproduces statistics'
    else:
        result['verdict'] = 'INCONSISTENT'
        result['interpretation'] = 'Simple model fails to reproduce statistics'

    print(f"  Vocab match: {vocab_match:.3f}, TTR match: {ttr_match:.3f}, Autocorr match: {auto_match:.3f}")
    print(f"  Overall: {overall:.3f}, Verdict: {result['verdict']}")

    return result


# =============================================================================
# MAIN
# =============================================================================

def run_sid04():
    """Execute SID-04 tests."""
    print("=" * 70)
    print("SID-04: HUMAN-STATE COMPATIBILITY ANALYSIS")
    print("=" * 70)
    print()
    print("TIER 4: Speculative compatibility only")
    print()

    random.seed(42)
    np.random.seed(42)

    # Load data
    print("Loading data...")
    tokens, sections = load_transcription()
    grammar, residue, res_positions = classify_tokens(tokens)
    res_sections = [sections[i] for i in res_positions]

    print(f"  Total: {len(tokens)}, Grammar: {len(grammar)}, Residue: {len(residue)}")
    print(f"  Residue types: {len(set(residue))}")
    print()

    # Run tests
    print("=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    print()

    results = []

    r1 = test_autocorrelation(residue)
    results.append(('AUTOCORRELATION', r1))
    print()

    r2 = test_hazard_proximity(tokens, res_positions)
    results.append(('HAZARD_PROXIMITY', r2))
    print()

    r3 = test_section_exclusivity(residue, res_sections)
    results.append(('SECTION_EXCLUSIVITY', r3))
    print()

    r4 = test_run_lengths(residue)
    results.append(('RUN_LENGTHS', r4))
    print()

    r5 = test_boundary_asymmetry(tokens, res_positions, sections)
    results.append(('BOUNDARY_ASYMMETRY', r5))
    print()

    r6 = test_synthetic_model(residue, res_sections)
    results.append(('SYNTHETIC_MODEL', r6))
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    consistent = 0
    for name, r in results:
        v = r.get('verdict', 'N/A')
        if 'CONSISTENT' in v:
            consistent += 1
        print(f"  {name}: {v}")

    print()
    print(f"Tests consistent with human-state model: {consistent}/6")
    print()

    if consistent >= 4:
        overall = "COMPATIBLE"
        print("OVERALL: Residue is STATISTICALLY COMPATIBLE with")
        print("         non-encoding human-state generative model.")
    elif consistent >= 2:
        overall = "PARTIALLY_COMPATIBLE"
        print("OVERALL: PARTIALLY COMPATIBLE with human-state model.")
    else:
        overall = "INCOMPATIBLE"
        print("OVERALL: INCOMPATIBLE with simple human-state model.")

    print()
    print("=" * 70)
    print("INTERPRETIVE LIMITS (REQUIRED)")
    print("=" * 70)
    print()
    print("  - Tokens DO NOT 'encode' states")
    print("  - Tokens DO NOT 'mean' anything")
    print("  - Tokens DO NOT causally affect execution")
    print("  - Compatibility ≠ explanation")
    print("  - Fit ≠ proof")
    print()
    print("=" * 70)
    print("SID-04 COMPLETE")
    print("=" * 70)

    return overall, results


if __name__ == "__main__":
    run_sid04()
