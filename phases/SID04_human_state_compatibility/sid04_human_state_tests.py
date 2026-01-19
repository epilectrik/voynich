"""
SID-04: Human-State Compatibility Analysis

Tests whether the non-executive token residue is STATISTICALLY COMPATIBLE
with generic human state dynamics WITHOUT implying encoding, control,
semantics, or information transfer.

EPISTEMIC TIER: 4 (SPECULATIVE COMPATIBILITY ONLY)

Hard Constraints:
- No claims about what tokens encode/mean
- No causal attribution to execution outcomes
- All results framed as "consistent/inconsistent with"
- Compatibility ≠ explanation

Input: Final EVA transcription, grammar-filtered stream, pre-identified
       non-executive token set, section/LINK/hazard markers
"""

import sys
import os
import math
import random
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional
import numpy as np
from scipy import stats

# Add project root to path
sys.path.insert(0, r'C:\git\voynich')

# =============================================================================
# DATA LOADING
# =============================================================================

def load_transcription():
    """Load and parse the interlinear transcription."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    sections = []
    folios = []
    line_positions = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()  # Skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # Filter to H (PRIMARY) transcriber track only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"')
                folio = parts[2].strip('"')
                section = parts[3].strip('"')

                # Skip empty or placeholder tokens
                if word and not word.startswith('*'):
                    tokens.append(word)
                    folios.append(folio)
                    sections.append(section)

                    # Track line position
                    try:
                        line_pos = int(parts[11].strip('"')) if len(parts) > 11 else 0
                        is_line_initial = (parts[13].strip('"') == '1') if len(parts) > 13 else False
                        line_positions.append((line_pos, is_line_initial))
                    except:
                        line_positions.append((0, False))

    return tokens, sections, folios, line_positions


# Grammar tokens (high-frequency operational patterns)
GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

# Forbidden transitions from hazards.py (17 total)
FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'), ('chol', 'r'),
    ('chedy', 'ee'), ('chey', 'chedy'), ('l', 'chol'), ('dy', 'aiin'),
    ('dy', 'chey'), ('or', 'dal'), ('ar', 'chol'), ('qo', 'shey'),
    ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'), ('dar', 'qokaiin'),
    ('qokaiin', 'qokedy')
]

# Hazard-involved tokens
HAZARD_TOKENS = set()
for a, b in FORBIDDEN_PAIRS:
    HAZARD_TOKENS.add(a)
    HAZARD_TOKENS.add(b)


def is_grammar_token(token: str) -> bool:
    """Classify token as grammar (executable) or residue (human-track)."""
    t = token.lower()
    # Check prefix
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    # Check suffix
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def classify_tokens(tokens: List[str]) -> Tuple[List[int], List[str], List[str]]:
    """Classify tokens as grammar (0) or residue (1)."""
    classifications = []
    grammar_list = []
    residue_list = []

    for t in tokens:
        if is_grammar_token(t):
            classifications.append(0)
            grammar_list.append(t)
        else:
            classifications.append(1)
            residue_list.append(t)

    return classifications, grammar_list, residue_list


def identify_link_regions(tokens: List[str], classifications: List[int]) -> List[Tuple[int, int]]:
    """
    Identify LINK regions (consecutive non-grammar tokens).
    LINK = waiting phase = high residue token density.
    """
    regions = []
    in_region = False
    start = 0
    consecutive_residue = 0

    for i, (t, c) in enumerate(zip(tokens, classifications)):
        if c == 1:  # Residue
            if not in_region:
                start = i
                in_region = True
            consecutive_residue += 1
        else:
            if in_region and consecutive_residue >= 2:
                regions.append((start, i - 1))
            in_region = False
            consecutive_residue = 0

    if in_region and consecutive_residue >= 2:
        regions.append((start, len(tokens) - 1))

    return regions


def identify_section_boundaries(sections: List[str]) -> List[int]:
    """Find positions where section changes."""
    boundaries = []
    for i in range(1, len(sections)):
        if sections[i] != sections[i-1]:
            boundaries.append(i)
    return boundaries


def compute_hazard_adjacency(tokens: List[str]) -> List[int]:
    """Compute positions adjacent to hazard tokens."""
    positions = []
    for i, t in enumerate(tokens):
        if t.lower() in HAZARD_TOKENS:
            positions.append(i)
    return positions


# =============================================================================
# TEST 1: TEMPORAL AUTOCORRELATION
# =============================================================================

def test_temporal_autocorrelation(residue_tokens: List[str],
                                   residue_positions: List[int],
                                   section_boundaries: List[int],
                                   n_shuffles: int = 200) -> Dict:
    """
    Test 1: Temporal Autocorrelation

    Question: Do residue tokens show short-range temporal structure
    consistent with human state inertia (clustered, not random)?

    Human-state model predicts:
    - High autocorrelation at lag 1-2
    - Decay with increasing lag
    - Reset at section boundaries

    Null model: Shuffled token positions (destroys temporal structure)
    """
    result = {
        'test_name': 'TEMPORAL_AUTOCORRELATION',
        'question': 'Do residue tokens show inertial (clustered) temporal structure?',
        'null_models': ['position-shuffled', 'random-baseline']
    }

    if len(residue_tokens) < 50:
        result['status'] = 'INSUFFICIENT_DATA'
        return result

    # Build position-to-index mapping
    residue_positions_set = set(residue_positions)

    # Compute observed autocorrelation: P(residue at i+k | residue at i)
    max_lag = 10
    observed_ac = []

    for lag in range(1, max_lag + 1):
        same_type_count = 0
        total = 0
        for i, pos in enumerate(residue_positions):
            if i + lag < len(residue_positions):
                next_pos = residue_positions[i + lag]
                # Check if next position is within same section
                # (crude: just check if gap is small)
                if next_pos - pos < 20:  # Within local window
                    total += 1
                    if residue_positions[i] in residue_positions_set and \
                       residue_positions[i + lag] in residue_positions_set:
                        same_type_count += 1

        if total > 0:
            observed_ac.append(same_type_count / total)
        else:
            observed_ac.append(0.0)

    # Build token-type transition matrix for observed
    type_transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(residue_tokens) - 1):
        type_transitions[residue_tokens[i].lower()][residue_tokens[i+1].lower()] += 1

    # Compute self-transition rate (same token type repeated)
    self_transitions = sum(type_transitions[t].get(t, 0) for t in type_transitions)
    total_transitions = sum(sum(d.values()) for d in type_transitions.values())
    observed_self_rate = self_transitions / total_transitions if total_transitions > 0 else 0

    # Null model: shuffle residue tokens, recompute
    null_self_rates = []
    for _ in range(n_shuffles):
        shuffled = residue_tokens.copy()
        random.shuffle(shuffled)

        null_type_trans = defaultdict(lambda: defaultdict(int))
        for i in range(len(shuffled) - 1):
            null_type_trans[shuffled[i].lower()][shuffled[i+1].lower()] += 1

        null_self = sum(null_type_trans[t].get(t, 0) for t in null_type_trans)
        null_total = sum(sum(d.values()) for d in null_type_trans.values())
        null_self_rates.append(null_self / null_total if null_total > 0 else 0)

    # Compute p-value: proportion of null >= observed
    p_value = np.mean([1 if ns >= observed_self_rate else 0 for ns in null_self_rates])

    # Effect size: Cohen's d
    null_mean = np.mean(null_self_rates)
    null_std = np.std(null_self_rates)
    effect_size = (observed_self_rate - null_mean) / null_std if null_std > 0 else 0

    result['observed'] = {
        'self_transition_rate': round(observed_self_rate, 4),
        'autocorrelation_lag1': round(observed_ac[0], 4) if observed_ac else 0,
        'autocorrelation_decay': observed_ac[:5]
    }
    result['null_comparison'] = {
        'null_mean': round(null_mean, 4),
        'null_std': round(null_std, 4),
        'p_value': round(p_value, 4),
        'effect_size_d': round(effect_size, 2)
    }

    # Interpretive limit
    if p_value < 0.05 and effect_size > 0.5:
        result['verdict'] = 'STATISTICALLY_CONSISTENT'
        result['interpretation'] = (
            'Residue tokens show significantly elevated self-transition rate compared to shuffled null. '
            'This is CONSISTENT WITH human state inertia (clustered, not random). '
            'LIMIT: Does not prove tokens encode states; only shows clustering pattern.'
        )
    elif p_value < 0.05:
        result['verdict'] = 'WEAKLY_CONSISTENT'
        result['interpretation'] = (
            'Residue tokens show statistically significant but small clustering effect. '
            'LIMIT: Effect size insufficient to distinguish from weak structure.'
        )
    else:
        result['verdict'] = 'STATISTICALLY_INCONSISTENT'
        result['interpretation'] = (
            'Residue tokens do NOT show significantly elevated clustering. '
            'This is INCONSISTENT WITH simple human state inertia model.'
        )

    return result


# =============================================================================
# TEST 2: HAZARD PROXIMITY DEFORMATION
# =============================================================================

def test_hazard_proximity_deformation(tokens: List[str],
                                       classifications: List[int],
                                       n_shuffles: int = 200) -> Dict:
    """
    Test 2: Hazard Proximity Deformation

    Question: Does residue token distribution change near hazard-adjacent positions?

    Human-state model predicts:
    - Different residue types near hazard positions (heightened attention)
    - Entropy change (possibly higher or lower diversity)

    Null model: Shuffled residue types (preserves positional structure)
    """
    result = {
        'test_name': 'HAZARD_PROXIMITY_DEFORMATION',
        'question': 'Does residue distribution deform near hazard positions?',
        'null_models': ['type-shuffled residue']
    }

    # Find hazard-adjacent positions
    hazard_positions = []
    for i, t in enumerate(tokens):
        if t.lower() in HAZARD_TOKENS:
            hazard_positions.append(i)

    if len(hazard_positions) < 10:
        result['status'] = 'INSUFFICIENT_HAZARD_DATA'
        return result

    # Extract residue tokens near vs far from hazards
    near_threshold = 3  # Within 3 positions

    near_residue = []
    far_residue = []

    for i, (t, c) in enumerate(zip(tokens, classifications)):
        if c == 1:  # Residue
            min_dist = min(abs(i - hp) for hp in hazard_positions)
            if min_dist <= near_threshold:
                near_residue.append(t.lower())
            else:
                far_residue.append(t.lower())

    if len(near_residue) < 20 or len(far_residue) < 20:
        result['status'] = 'INSUFFICIENT_RESIDUE_DATA'
        return result

    # Compute entropy of each group
    def compute_entropy(tokens_list):
        counts = Counter(tokens_list)
        total = len(tokens_list)
        entropy = 0.0
        for c in counts.values():
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
        return entropy

    near_entropy = compute_entropy(near_residue)
    far_entropy = compute_entropy(far_residue)

    # Compute type overlap (Jaccard)
    near_types = set(near_residue)
    far_types = set(far_residue)
    jaccard = len(near_types & far_types) / len(near_types | far_types)

    # Null model: shuffle residue types across all positions, recompute
    all_residue = [t.lower() for t, c in zip(tokens, classifications) if c == 1]
    residue_positions = [i for i, c in enumerate(classifications) if c == 1]

    null_entropy_diffs = []
    null_jaccards = []

    for _ in range(n_shuffles):
        shuffled = all_residue.copy()
        random.shuffle(shuffled)

        # Reassign to positions
        pos_to_token = dict(zip(residue_positions, shuffled))

        null_near = []
        null_far = []
        for pos, tok in pos_to_token.items():
            min_dist = min(abs(pos - hp) for hp in hazard_positions)
            if min_dist <= near_threshold:
                null_near.append(tok)
            else:
                null_far.append(tok)

        if len(null_near) > 0 and len(null_far) > 0:
            null_near_ent = compute_entropy(null_near)
            null_far_ent = compute_entropy(null_far)
            null_entropy_diffs.append(abs(null_near_ent - null_far_ent))

            null_near_types = set(null_near)
            null_far_types = set(null_far)
            null_jaccards.append(len(null_near_types & null_far_types) / len(null_near_types | null_far_types))

    observed_entropy_diff = abs(near_entropy - far_entropy)

    # P-values
    p_entropy = np.mean([1 if nd >= observed_entropy_diff else 0 for nd in null_entropy_diffs])
    p_jaccard = np.mean([1 if nj <= jaccard else 0 for nj in null_jaccards])

    # Effect sizes
    entropy_effect = (observed_entropy_diff - np.mean(null_entropy_diffs)) / np.std(null_entropy_diffs) if np.std(null_entropy_diffs) > 0 else 0
    jaccard_effect = (jaccard - np.mean(null_jaccards)) / np.std(null_jaccards) if np.std(null_jaccards) > 0 else 0

    result['observed'] = {
        'near_hazard_count': len(near_residue),
        'far_hazard_count': len(far_residue),
        'near_entropy': round(near_entropy, 3),
        'far_entropy': round(far_entropy, 3),
        'entropy_difference': round(observed_entropy_diff, 3),
        'type_overlap_jaccard': round(jaccard, 3)
    }
    result['null_comparison'] = {
        'null_entropy_diff_mean': round(np.mean(null_entropy_diffs), 3),
        'p_value_entropy': round(p_entropy, 4),
        'effect_size_entropy': round(entropy_effect, 2),
        'null_jaccard_mean': round(np.mean(null_jaccards), 3),
        'p_value_jaccard': round(p_jaccard, 4),
        'effect_size_jaccard': round(jaccard_effect, 2)
    }

    if p_entropy < 0.05 or p_jaccard < 0.05:
        result['verdict'] = 'STATISTICALLY_CONSISTENT'
        result['interpretation'] = (
            'Residue distribution shows significant deformation near hazard positions. '
            'This is CONSISTENT WITH heightened/altered state near hazard zones. '
            'LIMIT: Does not prove tokens encode hazard awareness; only shows distributional change.'
        )
    else:
        result['verdict'] = 'STATISTICALLY_INCONSISTENT'
        result['interpretation'] = (
            'Residue distribution does NOT significantly change near hazard positions. '
            'This is INCONSISTENT WITH hazard-proximity-driven state change model.'
        )

    return result


# =============================================================================
# TEST 3: LINK-CONDITIONED DISTRIBUTION
# =============================================================================

def test_link_conditioned_distribution(tokens: List[str],
                                        classifications: List[int],
                                        n_shuffles: int = 200) -> Dict:
    """
    Test 3: LINK-Conditioned Distribution

    Question: Do residue tokens differ between high-LINK and low-LINK regions?

    Human-state model predicts:
    - Different residue types during prolonged waiting (LINK-dense) vs active phases
    - Reflects different operator states (patience vs alertness)

    Null model: Shuffled residue (preserves LINK structure)
    """
    result = {
        'test_name': 'LINK_CONDITIONED_DISTRIBUTION',
        'question': 'Do residue tokens differ between LINK-dense and LINK-sparse regions?',
        'null_models': ['type-shuffled residue']
    }

    # Identify LINK regions
    link_regions = identify_link_regions(tokens, classifications)

    if len(link_regions) < 5:
        result['status'] = 'INSUFFICIENT_LINK_REGIONS'
        return result

    # Compute LINK density per position (running average)
    window = 10
    link_density = []
    for i in range(len(tokens)):
        start = max(0, i - window // 2)
        end = min(len(tokens), i + window // 2)
        residue_count = sum(1 for j in range(start, end) if classifications[j] == 1)
        link_density.append(residue_count / (end - start))

    # Classify positions as high-LINK or low-LINK
    median_density = np.median(link_density)

    high_link_residue = []
    low_link_residue = []

    for i, (t, c) in enumerate(zip(tokens, classifications)):
        if c == 1:  # Residue
            if link_density[i] > median_density:
                high_link_residue.append(t.lower())
            else:
                low_link_residue.append(t.lower())

    if len(high_link_residue) < 20 or len(low_link_residue) < 20:
        result['status'] = 'INSUFFICIENT_SPLIT_DATA'
        return result

    # Compute KL divergence between distributions
    def kl_divergence(p_counts, q_counts):
        all_keys = set(p_counts.keys()) | set(q_counts.keys())
        p_total = sum(p_counts.values())
        q_total = sum(q_counts.values())
        eps = 1e-10

        kl = 0.0
        for k in all_keys:
            p_prob = (p_counts.get(k, 0) + eps) / (p_total + eps * len(all_keys))
            q_prob = (q_counts.get(k, 0) + eps) / (q_total + eps * len(all_keys))
            kl += p_prob * math.log2(p_prob / q_prob)
        return kl

    high_counts = Counter(high_link_residue)
    low_counts = Counter(low_link_residue)
    observed_kl = kl_divergence(high_counts, low_counts)

    # Null model: shuffle all residue types
    all_residue = [t.lower() for t, c in zip(tokens, classifications) if c == 1]
    residue_indices = [i for i, c in enumerate(classifications) if c == 1]

    null_kls = []
    for _ in range(n_shuffles):
        shuffled = all_residue.copy()
        random.shuffle(shuffled)

        null_high = []
        null_low = []
        for j, idx in enumerate(residue_indices):
            if link_density[idx] > median_density:
                null_high.append(shuffled[j])
            else:
                null_low.append(shuffled[j])

        if len(null_high) > 0 and len(null_low) > 0:
            null_kls.append(kl_divergence(Counter(null_high), Counter(null_low)))

    # P-value
    p_value = np.mean([1 if nk >= observed_kl else 0 for nk in null_kls])
    effect_size = (observed_kl - np.mean(null_kls)) / np.std(null_kls) if np.std(null_kls) > 0 else 0

    result['observed'] = {
        'high_link_count': len(high_link_residue),
        'low_link_count': len(low_link_residue),
        'kl_divergence': round(observed_kl, 4)
    }
    result['null_comparison'] = {
        'null_kl_mean': round(np.mean(null_kls), 4),
        'null_kl_std': round(np.std(null_kls), 4),
        'p_value': round(p_value, 4),
        'effect_size_d': round(effect_size, 2)
    }

    if p_value < 0.05 and effect_size > 0.5:
        result['verdict'] = 'STATISTICALLY_CONSISTENT'
        result['interpretation'] = (
            'Residue distribution differs significantly between high-LINK and low-LINK regions. '
            'This is CONSISTENT WITH different operator states during waiting vs active phases. '
            'LIMIT: Does not prove tokens encode waiting states; only shows distributional divergence.'
        )
    elif p_value < 0.05:
        result['verdict'] = 'WEAKLY_CONSISTENT'
        result['interpretation'] = (
            'Residue distribution shows statistically significant but small divergence by LINK density. '
            'LIMIT: Effect size insufficient for confident interpretation.'
        )
    else:
        result['verdict'] = 'STATISTICALLY_INCONSISTENT'
        result['interpretation'] = (
            'Residue distribution does NOT significantly differ by LINK density. '
            'This is INCONSISTENT WITH LINK-correlated state variation model.'
        )

    return result


# =============================================================================
# TEST 4: BOUNDARY ASYMMETRY (CF-1 vs CF-2)
# =============================================================================

def test_boundary_asymmetry(tokens: List[str],
                             classifications: List[int],
                             section_boundaries: List[int],
                             n_shuffles: int = 200) -> Dict:
    """
    Test 4: Boundary Asymmetry

    Question: Do residue tokens differ between section-entry (CF-1) and
    section-exit (CF-2) positions?

    Human-state model predicts:
    - Different states at boundaries (starting vs finishing)
    - Asymmetric distribution reflecting transition states

    This test is DESCRIPTIVE only - does not infer causation.
    """
    result = {
        'test_name': 'BOUNDARY_ASYMMETRY',
        'question': 'Do residue tokens show asymmetry at section boundaries?',
        'null_models': ['type-shuffled residue']
    }

    if len(section_boundaries) < 5:
        result['status'] = 'INSUFFICIENT_BOUNDARIES'
        return result

    # Define entry and exit windows
    entry_window = 5  # Tokens after boundary
    exit_window = 5   # Tokens before boundary

    entry_residue = []
    exit_residue = []

    for boundary in section_boundaries:
        # Exit window: before boundary
        for i in range(max(0, boundary - exit_window), boundary):
            if i < len(classifications) and classifications[i] == 1:
                exit_residue.append(tokens[i].lower())

        # Entry window: after boundary
        for i in range(boundary, min(len(tokens), boundary + entry_window)):
            if classifications[i] == 1:
                entry_residue.append(tokens[i].lower())

    if len(entry_residue) < 15 or len(exit_residue) < 15:
        result['status'] = 'INSUFFICIENT_BOUNDARY_DATA'
        return result

    # Compute asymmetry metrics
    entry_counts = Counter(entry_residue)
    exit_counts = Counter(exit_residue)

    # Entropy asymmetry
    def compute_entropy(counts):
        total = sum(counts.values())
        entropy = 0.0
        for c in counts.values():
            if c > 0:
                p = c / total
                entropy -= p * math.log2(p)
        return entropy

    entry_entropy = compute_entropy(entry_counts)
    exit_entropy = compute_entropy(exit_counts)

    # Type overlap
    entry_types = set(entry_residue)
    exit_types = set(exit_residue)
    overlap = len(entry_types & exit_types) / len(entry_types | exit_types)

    # Chi-square test for distribution difference
    all_types = entry_types | exit_types
    observed_entry = [entry_counts.get(t, 0) for t in all_types]
    observed_exit = [exit_counts.get(t, 0) for t in all_types]

    # Expected under null (equal distribution)
    total_entry = sum(observed_entry)
    total_exit = sum(observed_exit)

    # Null model: shuffle residue types, recompute asymmetry
    all_residue = [t.lower() for t, c in zip(tokens, classifications) if c == 1]
    residue_positions = [i for i, c in enumerate(classifications) if c == 1]

    null_entropy_diffs = []
    null_overlaps = []

    for _ in range(n_shuffles):
        shuffled = all_residue.copy()
        random.shuffle(shuffled)
        pos_to_token = dict(zip(residue_positions, shuffled))

        null_entry = []
        null_exit = []

        for boundary in section_boundaries:
            for i in range(max(0, boundary - exit_window), boundary):
                if i in pos_to_token:
                    null_exit.append(pos_to_token[i])

            for i in range(boundary, min(len(tokens), boundary + entry_window)):
                if i in pos_to_token:
                    null_entry.append(pos_to_token[i])

        if len(null_entry) > 0 and len(null_exit) > 0:
            null_entry_ent = compute_entropy(Counter(null_entry))
            null_exit_ent = compute_entropy(Counter(null_exit))
            null_entropy_diffs.append(abs(null_entry_ent - null_exit_ent))

            null_entry_types = set(null_entry)
            null_exit_types = set(null_exit)
            if len(null_entry_types | null_exit_types) > 0:
                null_overlaps.append(len(null_entry_types & null_exit_types) / len(null_entry_types | null_exit_types))

    observed_entropy_diff = abs(entry_entropy - exit_entropy)

    # P-values
    p_entropy = np.mean([1 if nd >= observed_entropy_diff else 0 for nd in null_entropy_diffs])
    p_overlap = np.mean([1 if no <= overlap else 0 for no in null_overlaps])

    result['observed'] = {
        'entry_count': len(entry_residue),
        'exit_count': len(exit_residue),
        'entry_entropy': round(entry_entropy, 3),
        'exit_entropy': round(exit_entropy, 3),
        'entropy_difference': round(observed_entropy_diff, 3),
        'type_overlap': round(overlap, 3)
    }
    result['null_comparison'] = {
        'null_entropy_diff_mean': round(np.mean(null_entropy_diffs), 3) if null_entropy_diffs else 0,
        'p_value_entropy': round(p_entropy, 4),
        'null_overlap_mean': round(np.mean(null_overlaps), 3) if null_overlaps else 0,
        'p_value_overlap': round(p_overlap, 4)
    }

    if p_entropy < 0.05 or p_overlap < 0.05:
        result['verdict'] = 'STATISTICALLY_CONSISTENT'
        result['interpretation'] = (
            'Residue tokens show significant asymmetry between entry and exit boundaries. '
            'This is CONSISTENT WITH different operator states at transitions. '
            'LIMIT: Does not prove tokens encode boundary awareness; only shows positional asymmetry.'
        )
    else:
        result['verdict'] = 'STATISTICALLY_INCONSISTENT'
        result['interpretation'] = (
            'Residue tokens do NOT show significant entry/exit asymmetry. '
            'This is INCONSISTENT WITH boundary-driven state differentiation model.'
        )

    return result


# =============================================================================
# TEST 5: RUN-LENGTH DISTRIBUTION
# =============================================================================

def test_run_length_distribution(tokens: List[str],
                                  classifications: List[int],
                                  n_shuffles: int = 200) -> Dict:
    """
    Test 5: Run-Length Distribution

    Question: Does the distribution of consecutive same-type residue tokens
    fit a human-state model (geometric/exponential) better than random?

    Human-state model predicts:
    - State persistence -> geometric/exponential run lengths
    - Occasional long runs (state gets "stuck")

    Random model: Bernoulli process -> geometric runs
    The test is whether parameters match human-state vs pure random.
    """
    result = {
        'test_name': 'RUN_LENGTH_DISTRIBUTION',
        'question': 'Do residue run lengths follow human-state dynamics?',
        'null_models': ['Bernoulli random', 'shuffled positions']
    }

    # Extract runs of consecutive same-type residue tokens
    runs = []
    current_type = None
    current_length = 0

    for t, c in zip(tokens, classifications):
        if c == 1:  # Residue
            tok_type = t.lower()
            if tok_type == current_type:
                current_length += 1
            else:
                if current_length > 0:
                    runs.append(current_length)
                current_type = tok_type
                current_length = 1
        else:
            if current_length > 0:
                runs.append(current_length)
            current_type = None
            current_length = 0

    if current_length > 0:
        runs.append(current_length)

    if len(runs) < 30:
        result['status'] = 'INSUFFICIENT_RUN_DATA'
        return result

    # Fit geometric distribution
    mean_run = np.mean(runs)
    p_geometric = 1 / mean_run  # MLE for geometric

    # Generate expected geometric distribution
    max_run = max(runs)
    expected_geometric = []
    for k in range(1, max_run + 1):
        expected_geometric.append((1 - p_geometric) ** (k - 1) * p_geometric)

    # Normalize to counts
    n = len(runs)
    expected_counts = [e * n for e in expected_geometric[:max_run]]
    observed_counts = [runs.count(k) for k in range(1, max_run + 1)]

    # Chi-square goodness of fit
    # Combine bins with expected < 5
    combined_obs = []
    combined_exp = []
    current_obs = 0
    current_exp = 0

    for obs, exp in zip(observed_counts, expected_counts):
        current_obs += obs
        current_exp += exp
        if current_exp >= 5:
            combined_obs.append(current_obs)
            combined_exp.append(current_exp)
            current_obs = 0
            current_exp = 0

    if current_exp > 0:
        combined_obs.append(current_obs)
        combined_exp.append(current_exp)

    if len(combined_obs) >= 2:
        chi2, p_value = stats.chisquare(combined_obs, combined_exp)
    else:
        chi2, p_value = 0, 1.0

    # Coefficient of variation (CV) - higher than geometric suggests clustering
    cv = np.std(runs) / np.mean(runs) if np.mean(runs) > 0 else 0
    geometric_cv = math.sqrt(1 - p_geometric) / p_geometric  # Expected CV for geometric

    # Null model: shuffle residue types, recompute run stats
    all_residue = [t.lower() for t, c in zip(tokens, classifications) if c == 1]
    residue_positions = [i for i, c in enumerate(classifications) if c == 1]

    null_cvs = []
    null_means = []

    for _ in range(n_shuffles):
        shuffled = all_residue.copy()
        random.shuffle(shuffled)

        null_runs = []
        current_type = None
        current_length = 0

        for tok in shuffled:
            if tok == current_type:
                current_length += 1
            else:
                if current_length > 0:
                    null_runs.append(current_length)
                current_type = tok
                current_length = 1

        if current_length > 0:
            null_runs.append(current_length)

        if len(null_runs) > 0:
            null_means.append(np.mean(null_runs))
            null_cvs.append(np.std(null_runs) / np.mean(null_runs) if np.mean(null_runs) > 0 else 0)

    # P-values
    p_mean = np.mean([1 if nm >= mean_run else 0 for nm in null_means])
    p_cv = np.mean([1 if nc >= cv else 0 for nc in null_cvs])

    result['observed'] = {
        'total_runs': len(runs),
        'mean_run_length': round(mean_run, 3),
        'max_run_length': max(runs),
        'coefficient_of_variation': round(cv, 3),
        'geometric_fit_p': round(p_value, 4),
        'run_length_distribution': dict(Counter(runs).most_common(10))
    }
    result['null_comparison'] = {
        'null_mean_run': round(np.mean(null_means), 3) if null_means else 0,
        'null_cv_mean': round(np.mean(null_cvs), 3) if null_cvs else 0,
        'p_value_mean': round(p_mean, 4),
        'p_value_cv': round(p_cv, 4)
    }
    result['model_fit'] = {
        'geometric_p_parameter': round(p_geometric, 4),
        'expected_geometric_cv': round(geometric_cv, 3),
        'chi_square': round(chi2, 2),
        'geometric_fit_acceptable': p_value > 0.05
    }

    if p_value > 0.05:
        result['verdict'] = 'STATISTICALLY_CONSISTENT'
        result['interpretation'] = (
            'Residue run lengths are consistent with geometric (memoryless) distribution. '
            'This is CONSISTENT WITH independent state transitions. '
            'LIMIT: Does not prove tokens represent states; geometric is also consistent with random.'
        )
    else:
        result['verdict'] = 'STATISTICALLY_INCONSISTENT'
        result['interpretation'] = (
            'Residue run lengths deviate significantly from geometric distribution. '
            'This suggests non-memoryless (clustered or long-memory) state dynamics. '
            'LIMIT: Does not prove encoding; may reflect scribe behavior or manuscript structure.'
        )

    return result


# =============================================================================
# TEST 6: SYNTHETIC OPERATOR MODEL
# =============================================================================

def test_synthetic_operator_model(tokens: List[str],
                                   classifications: List[int],
                                   sections: List[str],
                                   n_iterations: int = 100) -> Dict:
    """
    Test 6: Synthetic Operator Model

    Question: Can a simple non-encoding generative model reproduce
    observed residue statistics?

    Model: Latent continuous state -> noisy many-to-many mapping -> tokens
    - Continuous state follows AR(1) with section-reset
    - State maps to token distribution (many states -> same token, one state -> many tokens)
    - Zero recoverable information

    Success: Synthetic matches observed on key statistics
    """
    result = {
        'test_name': 'SYNTHETIC_OPERATOR_MODEL',
        'question': 'Can a non-encoding state model reproduce observed statistics?',
        'null_models': ['latent AR(1) with noisy emission']
    }

    # Extract observed statistics to match
    residue_tokens = [t.lower() for t, c in zip(tokens, classifications) if c == 1]
    residue_sections = [s for s, c in zip(sections, classifications) if c == 1]

    if len(residue_tokens) < 100:
        result['status'] = 'INSUFFICIENT_DATA'
        return result

    # Observed statistics
    obs_vocab_size = len(set(residue_tokens))
    obs_mean_freq = len(residue_tokens) / obs_vocab_size
    obs_entropy = compute_entropy_from_list(residue_tokens)
    obs_section_exclusivity = compute_section_exclusivity(residue_tokens, residue_sections)

    def compute_autocorr(seq):
        """Compute lag-1 autocorrelation of types."""
        matches = sum(1 for i in range(len(seq)-1) if seq[i] == seq[i+1])
        return matches / (len(seq) - 1) if len(seq) > 1 else 0

    obs_autocorr = compute_autocorr(residue_tokens)

    # Build emission model: section -> token distribution
    section_vocabs = defaultdict(Counter)
    for t, s in zip(residue_tokens, residue_sections):
        section_vocabs[s][t] += 1

    # Normalize to probabilities
    section_probs = {}
    for s, counts in section_vocabs.items():
        total = sum(counts.values())
        section_probs[s] = {t: c/total for t, c in counts.items()}

    # Synthetic model parameters
    n_states = 50  # Latent state space
    ar_coef = 0.8  # Autocorrelation of state
    noise_level = 0.3  # Noise in state->token mapping

    # Generate synthetic sequences
    synth_matches = {
        'vocab_ratio': [],
        'entropy_ratio': [],
        'exclusivity_ratio': [],
        'autocorr_ratio': []
    }

    for _ in range(n_iterations):
        synth_tokens = []
        synth_sections = []
        state = random.randint(0, n_states - 1)

        for s in residue_sections:
            # State evolves (AR process with section reset)
            if synth_sections and synth_sections[-1] != s:
                # Section change -> partial state reset
                state = random.randint(0, n_states - 1) if random.random() < 0.5 else state

            # AR(1) evolution
            innovation = random.gauss(0, 1 - ar_coef**2)
            state = int((ar_coef * state + innovation * n_states / 3) % n_states)

            # Noisy emission: state influences token choice
            if s in section_probs:
                probs = section_probs[s]
                tokens_list = list(probs.keys())
                base_probs = list(probs.values())

                # Add state-dependent perturbation
                state_bias = [(state / n_states - 0.5) * noise_level * random.random() for _ in tokens_list]
                adjusted = [max(0.001, p + b) for p, b in zip(base_probs, state_bias)]
                total_adj = sum(adjusted)
                adjusted = [p / total_adj for p in adjusted]

                tok = random.choices(tokens_list, weights=adjusted)[0]
            else:
                tok = random.choice(residue_tokens)

            synth_tokens.append(tok)
            synth_sections.append(s)

        # Compute synthetic statistics
        syn_vocab = len(set(synth_tokens))
        syn_entropy = compute_entropy_from_list(synth_tokens)
        syn_excl = compute_section_exclusivity(synth_tokens, synth_sections)
        syn_autocorr = compute_autocorr(synth_tokens)

        synth_matches['vocab_ratio'].append(syn_vocab / obs_vocab_size)
        synth_matches['entropy_ratio'].append(syn_entropy / obs_entropy if obs_entropy > 0 else 0)
        synth_matches['exclusivity_ratio'].append(syn_excl / obs_section_exclusivity if obs_section_exclusivity > 0 else 0)
        synth_matches['autocorr_ratio'].append(syn_autocorr / obs_autocorr if obs_autocorr > 0 else 0)

    # Evaluate match quality (ratio close to 1.0 = good match)
    def match_quality(ratios):
        deviations = [abs(r - 1.0) for r in ratios]
        return 1.0 - np.mean(deviations)  # 1.0 = perfect match

    result['observed'] = {
        'vocab_size': obs_vocab_size,
        'entropy': round(obs_entropy, 3),
        'section_exclusivity': round(obs_section_exclusivity, 3),
        'autocorrelation': round(obs_autocorr, 4)
    }
    result['synthetic_match'] = {
        'vocab_ratio_mean': round(np.mean(synth_matches['vocab_ratio']), 3),
        'vocab_ratio_std': round(np.std(synth_matches['vocab_ratio']), 3),
        'entropy_ratio_mean': round(np.mean(synth_matches['entropy_ratio']), 3),
        'exclusivity_ratio_mean': round(np.mean(synth_matches['exclusivity_ratio']), 3),
        'autocorr_ratio_mean': round(np.mean(synth_matches['autocorr_ratio']), 3)
    }
    result['model_parameters'] = {
        'n_latent_states': n_states,
        'ar_coefficient': ar_coef,
        'noise_level': noise_level,
        'degrees_of_freedom': 3
    }

    # Overall match quality
    overall_match = np.mean([
        match_quality(synth_matches['vocab_ratio']),
        match_quality(synth_matches['entropy_ratio']),
        match_quality(synth_matches['exclusivity_ratio']),
        match_quality(synth_matches['autocorr_ratio'])
    ])

    result['overall_match_quality'] = round(overall_match, 3)

    if overall_match > 0.7:
        result['verdict'] = 'STATISTICALLY_CONSISTENT'
        result['interpretation'] = (
            f'Synthetic non-encoding model achieves {overall_match*100:.0f}% match on key statistics. '
            'Residue tokens are CONSISTENT WITH a latent-state model that encodes zero information. '
            'LIMIT: Model fit does not prove mechanism; multiple generative processes may achieve similar fit.'
        )
    elif overall_match > 0.5:
        result['verdict'] = 'WEAKLY_CONSISTENT'
        result['interpretation'] = (
            f'Synthetic model achieves {overall_match*100:.0f}% match (moderate). '
            'Residue tokens are PARTIALLY CONSISTENT with non-encoding state model. '
            'LIMIT: Requires additional model tuning or different architecture.'
        )
    else:
        result['verdict'] = 'STATISTICALLY_INCONSISTENT'
        result['interpretation'] = (
            f'Synthetic model achieves only {overall_match*100:.0f}% match. '
            'Residue tokens show statistics that simple non-encoding models struggle to reproduce. '
            'LIMIT: Does not prove encoding; may require more complex generative process.'
        )

    return result


def compute_entropy_from_list(tokens: List[str]) -> float:
    """Compute entropy from token list."""
    counts = Counter(tokens)
    total = len(tokens)
    entropy = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            entropy -= p * math.log2(p)
    return entropy


def compute_section_exclusivity(tokens: List[str], sections: List[str]) -> float:
    """Compute fraction of types exclusive to one section."""
    type_sections = defaultdict(set)
    for t, s in zip(tokens, sections):
        type_sections[t].add(s)

    exclusive = sum(1 for sects in type_sections.values() if len(sects) == 1)
    return exclusive / len(type_sections) if type_sections else 0


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def run_sid04():
    """Execute SID-04 Human-State Compatibility Analysis."""

    print("=" * 70)
    print("SID-04: HUMAN-STATE COMPATIBILITY ANALYSIS")
    print("=" * 70)
    print()
    print("EPISTEMIC TIER: 4 (SPECULATIVE COMPATIBILITY ONLY)")
    print()
    print("This phase tests whether residue tokens are STATISTICALLY COMPATIBLE")
    print("with generic human-state dynamics WITHOUT implying encoding.")
    print()

    # Set seed for reproducibility
    random.seed(42)
    np.random.seed(42)

    # Load data
    print("Loading transcription data...")
    tokens, sections, folios, line_positions = load_transcription()
    print(f"  Total tokens: {len(tokens)}")

    # Classify
    classifications, grammar_tokens, residue_tokens = classify_tokens(tokens)
    residue_sections = [s for s, c in zip(sections, classifications) if c == 1]
    residue_positions = [i for i, c in enumerate(classifications) if c == 1]

    print(f"  Grammar tokens: {len(grammar_tokens)} ({len(grammar_tokens)/len(tokens)*100:.1f}%)")
    print(f"  Residue tokens: {len(residue_tokens)} ({len(residue_tokens)/len(tokens)*100:.1f}%)")
    print(f"  Residue types: {len(set(residue_tokens))}")
    print()

    # Identify structural features
    section_boundaries = identify_section_boundaries(sections)
    hazard_positions = compute_hazard_adjacency(tokens)
    link_regions = identify_link_regions(tokens, classifications)

    print(f"  Section boundaries: {len(section_boundaries)}")
    print(f"  Hazard-adjacent positions: {len(hazard_positions)}")
    print(f"  LINK regions: {len(link_regions)}")
    print()

    # Run tests
    results = []

    print("=" * 70)
    print("RUNNING COMPATIBILITY TESTS")
    print("=" * 70)
    print()

    # Test 1: Temporal Autocorrelation
    print("Test 1: Temporal Autocorrelation...")
    test1 = test_temporal_autocorrelation(residue_tokens, residue_positions, section_boundaries)
    results.append(test1)
    print(f"  Verdict: {test1.get('verdict', 'N/A')}")
    print()

    # Test 2: Hazard Proximity Deformation
    print("Test 2: Hazard Proximity Deformation...")
    test2 = test_hazard_proximity_deformation(tokens, classifications)
    results.append(test2)
    print(f"  Verdict: {test2.get('verdict', 'N/A')}")
    print()

    # Test 3: LINK-Conditioned Distribution
    print("Test 3: LINK-Conditioned Distribution...")
    test3 = test_link_conditioned_distribution(tokens, classifications)
    results.append(test3)
    print(f"  Verdict: {test3.get('verdict', 'N/A')}")
    print()

    # Test 4: Boundary Asymmetry
    print("Test 4: Boundary Asymmetry (CF-1 vs CF-2)...")
    test4 = test_boundary_asymmetry(tokens, classifications, section_boundaries)
    results.append(test4)
    print(f"  Verdict: {test4.get('verdict', 'N/A')}")
    print()

    # Test 5: Run-Length Distribution
    print("Test 5: Run-Length Distribution...")
    test5 = test_run_length_distribution(tokens, classifications)
    results.append(test5)
    print(f"  Verdict: {test5.get('verdict', 'N/A')}")
    print()

    # Test 6: Synthetic Operator Model
    print("Test 6: Synthetic Operator Model...")
    test6 = test_synthetic_operator_model(tokens, classifications, sections)
    results.append(test6)
    print(f"  Verdict: {test6.get('verdict', 'N/A')}")
    print()

    # ==========================================================================
    # RESULTS SUMMARY
    # ==========================================================================

    print("=" * 70)
    print("SID-04 RESULTS SUMMARY")
    print("=" * 70)
    print()

    for r in results:
        print(f"### {r.get('test_name', 'UNKNOWN')}")
        print(f"Question: {r.get('question', 'N/A')}")
        print(f"Null models: {r.get('null_models', [])}")
        print()

        if 'observed' in r:
            print("Observed:")
            for k, v in r['observed'].items():
                print(f"  {k}: {v}")
            print()

        if 'null_comparison' in r:
            print("Null comparison:")
            for k, v in r['null_comparison'].items():
                print(f"  {k}: {v}")
            print()

        print(f"VERDICT: {r.get('verdict', 'N/A')}")
        print()
        print(f"Interpretation: {r.get('interpretation', 'N/A')}")
        print()
        print("-" * 70)
        print()

    # ==========================================================================
    # SYNTHESIS
    # ==========================================================================

    print("=" * 70)
    print("SID-04 SYNTHESIS")
    print("=" * 70)
    print()

    # Count verdicts
    consistent_count = sum(1 for r in results if 'CONSISTENT' in r.get('verdict', ''))
    inconsistent_count = sum(1 for r in results if r.get('verdict') == 'STATISTICALLY_INCONSISTENT')
    weak_count = sum(1 for r in results if r.get('verdict') == 'WEAKLY_CONSISTENT')

    print(f"Tests CONSISTENT with human-state model: {consistent_count}/6")
    print(f"Tests WEAKLY CONSISTENT: {weak_count}/6")
    print(f"Tests INCONSISTENT: {inconsistent_count}/6")
    print()

    # Determine overall verdict
    if consistent_count >= 4:
        overall = "COMPATIBLE"
        overall_msg = (
            "Residue tokens are STATISTICALLY COMPATIBLE with a non-encoding "
            "human-state generative model. The observed patterns (clustering, "
            "distributional variation, run structure) can be reproduced by a "
            "model that encodes zero recoverable information."
        )
    elif consistent_count >= 2:
        overall = "PARTIALLY_COMPATIBLE"
        overall_msg = (
            "Residue tokens are PARTIALLY COMPATIBLE with human-state dynamics. "
            "Some observed patterns match the model; others require alternative explanation."
        )
    else:
        overall = "INCOMPATIBLE"
        overall_msg = (
            "Residue tokens are INCOMPATIBLE with simple human-state dynamics. "
            "The observed patterns cannot be reproduced by tested non-encoding models."
        )

    print(f"OVERALL VERDICT: {overall}")
    print()
    print(overall_msg)
    print()

    # Non-conclusion
    print("=" * 70)
    print("NON-CONCLUSION (REQUIRED)")
    print("=" * 70)
    print()
    print("What CANNOT be inferred from SID-04:")
    print("  - Tokens DO NOT 'encode' operator states")
    print("  - Tokens DO NOT 'mean' anything")
    print("  - Tokens DO NOT causally affect execution")
    print("  - No specific operator states can be identified")
    print("  - No information can be recovered from tokens")
    print()
    print("Compatibility ≠ explanation.")
    print("Fit ≠ proof.")
    print("Statistical pattern ≠ semantic content.")
    print()

    # Closure assessment
    print("=" * 70)
    print("CLOSURE ASSESSMENT")
    print("=" * 70)
    print()

    if overall == "COMPATIBLE":
        print("CLOSURE: JUSTIFIED")
        print()
        print("The null hypothesis (tokens are non-semantic traces of human state)")
        print("cannot be rejected. No encoding is REQUIRED to explain the data.")
        print()
        print("Further investigation of token 'meaning' is NOT warranted.")
        print("Residue tokens are interpretively closed at Tier 4.")
    elif overall == "PARTIALLY_COMPATIBLE":
        print("CLOSURE: PARTIAL")
        print()
        print("Multiple models remain equally compatible with the data.")
        print("The human-state model is not uniquely favored.")
        print()
        print("Further investigation may refine but will not identify 'meaning'.")
    else:
        print("CLOSURE: NOT JUSTIFIED")
        print()
        print("The human-state model fails to reproduce key statistics.")
        print("Alternative generative models should be tested.")
        print()
        print("This does NOT imply tokens encode information.")

    print()
    print("=" * 70)
    print("SID-04 COMPLETE")
    print("=" * 70)

    return overall, results


if __name__ == "__main__":
    overall, results = run_sid04()
