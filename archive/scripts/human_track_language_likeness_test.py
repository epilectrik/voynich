"""
Phase HLL-2: Human-Track Language-Likeness Stress Test (Revised)
Symbolic Label Collapse Probe

Tests whether human-track tokens behave like a limited symbolic label system
for position, phase-identity, or attentional stance - NOT like measured or ranked states.

EXPLICITLY EXCLUDES (falsified in Phase HOT):
- Ordinal hierarchies
- Ranked intensity scales
- Severity or stress ladders
- Apparatus-global parameters

Outcome: WEAKLY SUPPORTED or FALSIFIED
Decision rule: >=3 tests support -> WEAKLY SUPPORTED
"""

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# DATA LOADING AND TOKEN CLASSIFICATION
# =============================================================================

# Known categorized tokens (executable grammar - from Phase 20A)
CATEGORIZED_TOKENS = {
    'daiin', 'aiin', 'chedy', 'chey', 'ol', 'ar', 'or', 'al', 'shedy',
    'qokaiin', 'qokedy', 'qokeedy', 'qokeey', 'chol', 'chor', 'shor',
    'shol', 'dar', 'dal', 'kaiin', 'taiin', 'saiin', 'raiin',
    'okaiin', 'otaiin', 'osaiin', 'oraiin', 'dain', 'ain', 'in',
    'shey', 'shy', 'chdy', 'dy', 'edy', 'eedy', 'y', 'ey',
    'qo', 'o', 'cho', 'sho', 'do', 'lo', 'ro', 'ko', 'to', 'so', 'go', 'yo',
    'ok', 'ak', 'yk', 'ek', 'ik',
    'okeedy', 'okedy', 'okeey', 'okaiin',
    'cheol', 'sheol', 'ctheol', 'pheol',
    'qol', 'sol', 'dol', 'tol', 'pol', 'fol', 'gol',
    'lkaiin', 'lkeedy', 'lkedy', 'lkeey', 'lkaiin',
    'daiiin', 'aiiin', 'oiin', 'eiin',
    's', 'e', 't', 'd', 'l', 'o', 'h', 'c', 'k', 'r',
    'ch', 'sh', 'ck', 'ct', 'cth', 'cph', 'cfh',
    'qokal', 'qokar', 'qokor', 'qokol',
    'chkal', 'chkar', 'chkor', 'chkol',
    'shal', 'shar', 'shor', 'shol',
    'dal', 'dar', 'dor', 'dol',
    'okal', 'okar', 'okor', 'okol',
    'otedy', 'oteedy', 'oteey', 'otaiin',
    'otal', 'otar', 'otor', 'otol',
    'chal', 'char', 'chor', 'chol',
    'cheedy', 'cheeedy', 'cheey',
    'sheedy', 'sheeedy', 'sheey',
    'qoeedy', 'qoeeedy', 'qoeey',
    'keedy', 'keeedy', 'keey', 'kaiin',
    'teedy', 'teeedy', 'teey', 'taiin',
    'lchedy', 'lshedy', 'lchey', 'lshey',
    'dchedy', 'dshedy', 'dchey', 'dshey',
    'ochedy', 'oshedy', 'ochey', 'oshey',
    'ychedy', 'yshedy', 'ychey', 'yshey',
    'lol', 'lor', 'lal', 'lar',
    'rol', 'ror', 'ral', 'rar',
    'eol', 'eor', 'eal', 'ear',
    'tchedy', 'tshedy', 'tchey', 'tshey',
    'pchedy', 'pshedy', 'pchey', 'pshey',
    'fchedy', 'fshedy', 'fchey', 'fshey',
    'kchedy', 'kshedy', 'kchey', 'kshey',
    'ckhedy', 'ckheedy', 'ckheey', 'ckhaiin',
    'cthedy', 'ctheedy', 'ctheey', 'cthaiin',
    'cphedy', 'cpheedy', 'cpheey', 'cphaiin',
    'lkeedy', 'lkeeedy', 'lkeey', 'lkaiin',
    'olkeedy', 'olkeeedy', 'olkeey', 'olkaiin',
    'ykeedy', 'ykeeedy', 'ykeey', 'ykaiin',
    'dkeedy', 'dkeeedy', 'dkeey', 'dkaiin',
    'okeedy', 'okeeedy', 'okeey', 'okaiin',
    'ekeedy', 'ekeeedy', 'ekeey', 'ekaiin',
    'qokain', 'okain', 'chokain', 'shokain',
    'qotedy', 'qoteedy', 'qoteey', 'qotaiin',
    'shotedy', 'shoteedy', 'shoteey', 'shotaiin',
    'chotedy', 'choteedy', 'choteey', 'chotaiin',
    'otedy', 'oteedy', 'oteey', 'otaiin',
    'lchol', 'lchor', 'lchal', 'lchar',
    'dchol', 'dchor', 'dchal', 'dchar',
    'ochol', 'ochor', 'ochal', 'ochar',
    'ychol', 'ychor', 'ychal', 'ychar',
    'tchol', 'tchor', 'tchal', 'tchar',
    'pchol', 'pchor', 'pchal', 'pchar',
    'fchol', 'fchor', 'fchal', 'fchar',
    'kchol', 'kchor', 'kchal', 'kchar',
    'lshol', 'lshor', 'lshal', 'lshar',
    'dshol', 'dshor', 'dshal', 'dshar',
    'oshol', 'oshor', 'oshal', 'oshar',
    'yshol', 'yshor', 'yshal', 'yshar',
    'ee', 'eee', 'eeee',
    'ii', 'iii', 'iiii', 'iiiii',
    'an', 'ain', 'aiin', 'aiiin',
    'on', 'oin', 'oiin', 'oiiin',
    'en', 'ein', 'eiin', 'eiiin',
}

LINK_INDICATORS = {'qo', 'ok', 'ol', 'or', 'ar', 'al', 'daiin', 'saiin', 'raiin'}
KERNEL_CHARS = {'k', 'h', 'e'}


def load_transcription(filepath: str) -> pd.DataFrame:
    """Load interlinear transcription data."""
    df = pd.read_csv(filepath, sep='\t', dtype=str)
    df = df.fillna('')

    if 'line_number' not in df.columns:
        df['line_number'] = df.groupby('folio').cumcount() + 1

    if 'section' not in df.columns:
        df['section'] = df['folio'].apply(extract_section)

    return df


def extract_section(folio: str) -> str:
    """Extract section code from folio identifier."""
    section_map = {
        'H': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
              'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19',
              'f20', 'f21', 'f22', 'f23', 'f24', 'f25'],
        'C': ['f26', 'f27', 'f28', 'f29', 'f30', 'f31', 'f32'],
        'A': ['f67', 'f68', 'f69', 'f70', 'f71', 'f72', 'f73'],
        'Z': ['f74', 'f75', 'f76', 'f77', 'f78', 'f79', 'f80', 'f81', 'f82', 'f83', 'f84'],
        'B': ['f85', 'f86', 'f87', 'f88', 'f89', 'f90', 'f91', 'f92', 'f93',
              'f94', 'f95', 'f96', 'f97', 'f98', 'f99', 'f100', 'f101', 'f102'],
        'P': ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f109', 'f110',
              'f111', 'f112', 'f113', 'f114', 'f115', 'f116'],
        'S': ['f33', 'f34', 'f35', 'f36', 'f37', 'f38', 'f39', 'f40', 'f41',
              'f42', 'f43', 'f44', 'f45', 'f46', 'f47', 'f48', 'f49', 'f50',
              'f51', 'f52', 'f53', 'f54', 'f55', 'f56', 'f57'],
        'T': ['f58', 'f59', 'f60', 'f61', 'f62', 'f63', 'f64', 'f65', 'f66'],
    }

    folio_base = folio.split('r')[0].split('v')[0]

    for section, folios in section_map.items():
        if any(folio_base.startswith(f) for f in folios):
            return section

    return 'U'


def is_human_track(token: str) -> bool:
    """Check if token is in the human-track (uncategorized)."""
    return token.lower() not in CATEGORIZED_TOKENS and len(token) > 0


def is_link_context(token: str) -> bool:
    """Check if token indicates LINK/waiting context."""
    return any(ind in token.lower() for ind in LINK_INDICATORS)


def has_kernel_char(token: str) -> bool:
    """Check if token contains kernel characters."""
    return any(k in token.lower() for k in KERNEL_CHARS)


# =============================================================================
# BEHAVIORAL ROLE CLASSIFICATION (Non-Ordinal)
# =============================================================================

def classify_behavioral_role(metrics: dict) -> str:
    """
    Classify token into behavioral role based on non-ordinal features.

    Roles are FUNCTIONAL, not ranked:
    - SECTION_BOUNDARY: marks section entry/exit
    - LINK_CONTEXT: marks waiting/attention
    - PERSISTENCE: indicates continuation
    - GRADIENT_SIGNAL: marks constraint transitions
    - NEUTRAL: no strong behavioral signal
    """
    early_rate = metrics.get('early_rate', 0)
    late_rate = metrics.get('late_rate', 0)
    near_link_rate = metrics.get('near_link_rate', 0)
    mean_run = metrics.get('mean_run_length', 1)
    gradient = metrics.get('constraint_gradient', 0)

    # Priority classification (first match wins)

    # Boundary markers: concentrated at section edges
    if early_rate > 0.35 or late_rate > 0.35:
        return 'SECTION_BOUNDARY'

    # LINK context: near waiting operations
    if near_link_rate > 0.6:
        return 'LINK_CONTEXT'

    # Persistence markers: form runs
    if mean_run > 1.5:
        return 'PERSISTENCE'

    # Gradient signals: constraint transitions
    if abs(gradient) > 0.15:
        return 'GRADIENT_SIGNAL'

    return 'NEUTRAL'


def compute_token_metrics(df: pd.DataFrame, min_freq: int = 10) -> Dict[str, dict]:
    """Compute behavioral metrics for each human-track token."""

    print("  Computing token metrics...")

    # Filter to human-track only
    ht_mask = df['word'].apply(is_human_track)

    # Token counts
    token_counts = Counter(df[ht_mask]['word'])
    frequent_tokens = {t for t, c in token_counts.items() if c >= min_freq}

    print(f"  Found {len(frequent_tokens)} tokens with freq >= {min_freq}")

    # Precompute section positions
    section_positions = {}
    for section in df['section'].unique():
        section_df = df[df['section'] == section].reset_index(drop=True)
        section_positions[section] = {
            'n_tokens': len(section_df),
            'indices': {idx: row['word'] for idx, row in section_df.iterrows()}
        }

    # Compute metrics per token
    metrics = {}

    tokens = df['word'].tolist()
    sections = df['section'].tolist()

    # LINK positions
    link_positions = np.array([i for i, t in enumerate(tokens) if is_link_context(t)])

    # Constraint density (kernel char rate in window)
    def constraint_density(start, end):
        if start >= end:
            return 0
        window = tokens[start:end]
        return sum(1 for t in window if has_kernel_char(t) or t in CATEGORIZED_TOKENS) / len(window)

    for token in frequent_tokens:
        # Find all occurrences
        occurrences = [(i, sections[i]) for i, t in enumerate(tokens) if t == token]

        if not occurrences:
            continue

        # Section positions
        positions = []
        for idx, section in occurrences:
            section_n = section_positions.get(section, {}).get('n_tokens', 1)
            # Position within section needs to be computed differently
            # Find position of this index within the section
            section_start = None
            for i in range(idx, -1, -1):
                if sections[i] != section:
                    section_start = i + 1
                    break
                section_start = i

            pos = (idx - section_start) / max(section_n - 1, 1)
            positions.append(pos)

        pos_arr = np.array(positions)

        # LINK distances
        indices = np.array([o[0] for o in occurrences])
        if len(link_positions) > 0:
            link_dists = np.array([np.min(np.abs(link_positions - i)) for i in indices])
        else:
            link_dists = np.array([999] * len(indices))

        # Run lengths
        runs = []
        current_run = 0
        for i in range(len(tokens)):
            if tokens[i] == token:
                current_run += 1
            else:
                if current_run > 0:
                    runs.append(current_run)
                current_run = 0
        if current_run > 0:
            runs.append(current_run)

        # Constraint gradient
        gradients = []
        window = 5
        for idx, _ in occurrences:
            before = constraint_density(max(0, idx - window), idx)
            after = constraint_density(idx + 1, min(len(tokens), idx + 1 + window))
            gradients.append(after - before)

        metrics[token] = {
            'count': len(occurrences),
            'sections': dict(Counter(s for _, s in occurrences)),
            'mean_position': float(np.mean(pos_arr)),
            'early_rate': float(np.mean(pos_arr < 0.2)),
            'mid_rate': float(np.mean((pos_arr >= 0.2) & (pos_arr <= 0.8))),
            'late_rate': float(np.mean(pos_arr > 0.8)),
            'mean_link_distance': float(np.mean(link_dists)),
            'near_link_rate': float(np.mean(link_dists <= 3)),
            'mean_run_length': float(np.mean(runs)) if runs else 1.0,
            'max_run_length': max(runs) if runs else 1,
            'constraint_gradient': float(np.mean(gradients)) if gradients else 0.0,
        }

    return metrics


# =============================================================================
# TEST A: VOCABULARY PRESSURE TEST
# =============================================================================

def test_vocabulary_pressure(metrics: Dict[str, dict]) -> dict:
    """
    TEST A: Does vocabulary size collapse sharply when tokens are clustered
    by behavioral role (NOT order or intensity)?

    Strong compression (<=10 core roles) -> supports symbolic labeling
    Weak compression -> attentional/navigation scatter
    """
    print("\n" + "=" * 70)
    print("TEST A: VOCABULARY PRESSURE TEST")
    print("=" * 70)

    # Classify each token into behavioral role
    role_assignments = {}
    for token, m in metrics.items():
        role = classify_behavioral_role(m)
        role_assignments[token] = role

    # Count tokens per role
    role_counts = Counter(role_assignments.values())
    n_roles = len(role_counts)
    n_tokens = len(role_assignments)

    compression_ratio = n_tokens / max(n_roles, 1)

    print(f"\nTotal human-track tokens analyzed: {n_tokens}")
    print(f"Distinct behavioral roles: {n_roles}")
    print(f"Compression ratio: {compression_ratio:.1f}:1")
    print(f"\nRole distribution:")
    for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
        print(f"  {role}: {count} tokens ({100*count/n_tokens:.1f}%)")

    # Decision
    # Strong compression means many tokens collapse to few roles
    # Threshold: <=10 roles with compression ratio > 10:1

    supports = n_roles <= 10 and compression_ratio >= 10

    result = {
        'test': 'A',
        'name': 'Vocabulary Pressure Test',
        'n_tokens': n_tokens,
        'n_roles': n_roles,
        'compression_ratio': compression_ratio,
        'role_distribution': dict(role_counts),
        'supports_symbolic_labeling': supports,
        'verdict': 'PASS - Strong compression to core roles' if supports else 'FAIL - Weak compression'
    }

    print(f"\n** RESULT: {'SUPPORTS' if supports else 'DOES NOT SUPPORT'} symbolic labeling **")

    return result


# =============================================================================
# TEST B: FUNCTIONAL EQUIVALENCE CLASS STABILITY
# =============================================================================

def test_equivalence_stability(metrics: Dict[str, dict]) -> dict:
    """
    TEST B: Do equivalence classes remain stable in FUNCTION across sections
    even when surface forms differ?

    Same function, different form -> dialectal labels (SUPPORTS)
    Same form, divergent function -> noise (FAILS)
    """
    print("\n" + "=" * 70)
    print("TEST B: FUNCTIONAL EQUIVALENCE CLASS STABILITY")
    print("=" * 70)

    # Get all sections
    all_sections = set()
    for m in metrics.values():
        all_sections.update(m['sections'].keys())

    # For each section, classify tokens into roles
    section_roles = {s: {} for s in all_sections}

    for token, m in metrics.items():
        role = classify_behavioral_role(m)
        for section, count in m['sections'].items():
            if section not in section_roles:
                section_roles[section] = {}
            if role not in section_roles[section]:
                section_roles[section][role] = []
            section_roles[section][role].append((token, count))

    # Check if all sections have all major roles
    major_roles = ['SECTION_BOUNDARY', 'LINK_CONTEXT', 'PERSISTENCE', 'GRADIENT_SIGNAL', 'NEUTRAL']

    role_coverage = {}
    for section in all_sections:
        roles_present = set(section_roles[section].keys())
        role_coverage[section] = len(roles_present.intersection(major_roles)) / len(major_roles)

    mean_coverage = np.mean(list(role_coverage.values()))

    print(f"\nSections analyzed: {len(all_sections)}")
    print(f"\nRole coverage by section:")
    for section in sorted(all_sections):
        roles = list(section_roles[section].keys())
        print(f"  {section}: {role_coverage[section]*100:.0f}% ({', '.join(roles)})")

    print(f"\nMean functional coverage across sections: {mean_coverage*100:.1f}%")

    # Check for dialectal variation (same role, different tokens)
    dialectal_evidence = []
    for role in major_roles:
        role_tokens_by_section = {}
        for section in all_sections:
            if role in section_roles[section]:
                role_tokens_by_section[section] = set(t for t, _ in section_roles[section][role])

        if len(role_tokens_by_section) >= 2:
            sections = list(role_tokens_by_section.keys())
            tokens_union = set()
            tokens_intersection = None
            for s in sections:
                tokens_union.update(role_tokens_by_section[s])
                if tokens_intersection is None:
                    tokens_intersection = role_tokens_by_section[s].copy()
                else:
                    tokens_intersection &= role_tokens_by_section[s]

            if tokens_intersection is None:
                tokens_intersection = set()

            # Dialectal: same function served by different forms
            jaccard = len(tokens_intersection) / len(tokens_union) if tokens_union else 0
            dialectal_evidence.append({
                'role': role,
                'n_sections': len(sections),
                'token_overlap': jaccard,
                'unique_per_section': 1.0 - jaccard
            })

    mean_uniqueness = np.mean([d['unique_per_section'] for d in dialectal_evidence]) if dialectal_evidence else 0

    print(f"\nDialectal variation (same function, different forms):")
    for d in dialectal_evidence:
        print(f"  {d['role']}: {d['unique_per_section']*100:.0f}% section-unique tokens")

    # Decision
    # Supports if: high coverage (>60%) AND dialectal variation (>40% unique per section)
    supports = mean_coverage > 0.6 and mean_uniqueness > 0.4

    result = {
        'test': 'B',
        'name': 'Functional Equivalence Class Stability',
        'n_sections': len(all_sections),
        'mean_coverage': mean_coverage,
        'mean_dialectal_uniqueness': mean_uniqueness,
        'dialectal_evidence': dialectal_evidence,
        'supports_symbolic_labeling': supports,
        'verdict': 'PASS - Stable functions with dialectal variation' if supports else 'FAIL - Unstable or non-dialectal'
    }

    print(f"\n** RESULT: {'SUPPORTS' if supports else 'DOES NOT SUPPORT'} symbolic labeling **")

    return result


# =============================================================================
# TEST C: REUSE ECONOMY AT ATTENTION POINTS
# =============================================================================

def test_reuse_economy(df: pd.DataFrame, metrics: Dict[str, dict]) -> dict:
    """
    TEST C: Do a small number of token families dominate LINK-adjacent,
    decision-relevant contexts?

    Concentrated reuse -> symbolic labels (SUPPORTS)
    Diffuse reuse -> navigation markup (FAILS)
    """
    print("\n" + "=" * 70)
    print("TEST C: REUSE ECONOMY AT ATTENTION POINTS")
    print("=" * 70)

    tokens = df['word'].tolist()

    # Find LINK-adjacent positions (within 3 tokens of LINK context)
    link_adjacent = set()
    for i, t in enumerate(tokens):
        if is_link_context(t):
            for j in range(max(0, i-3), min(len(tokens), i+4)):
                link_adjacent.add(j)

    # Count human-track tokens at LINK-adjacent positions
    link_adjacent_tokens = Counter()
    for i in link_adjacent:
        t = tokens[i]
        if is_human_track(t):
            link_adjacent_tokens[t] += 1

    total_link_adjacent = sum(link_adjacent_tokens.values())

    # Calculate concentration
    if total_link_adjacent == 0:
        top_10_coverage = 0
        top_20_coverage = 0
    else:
        sorted_tokens = link_adjacent_tokens.most_common()
        top_10_count = sum(c for _, c in sorted_tokens[:10])
        top_20_count = sum(c for _, c in sorted_tokens[:20])
        top_10_coverage = top_10_count / total_link_adjacent
        top_20_coverage = top_20_count / total_link_adjacent

    print(f"\nLINK-adjacent positions: {len(link_adjacent)}")
    print(f"Human-track tokens in LINK contexts: {total_link_adjacent}")
    print(f"Distinct token types: {len(link_adjacent_tokens)}")
    print(f"\nConcentration:")
    print(f"  Top 10 tokens cover: {top_10_coverage*100:.1f}% of LINK-adjacent occurrences")
    print(f"  Top 20 tokens cover: {top_20_coverage*100:.1f}% of LINK-adjacent occurrences")

    print(f"\nMost common tokens in LINK contexts:")
    for token, count in link_adjacent_tokens.most_common(15):
        pct = 100 * count / total_link_adjacent
        print(f"  {token}: {count} ({pct:.1f}%)")

    # Decision
    # Strong concentration: top 20 tokens cover >50%
    supports = top_20_coverage > 0.50

    result = {
        'test': 'C',
        'name': 'Reuse Economy at Attention Points',
        'link_adjacent_positions': len(link_adjacent),
        'total_tokens': total_link_adjacent,
        'distinct_types': len(link_adjacent_tokens),
        'top_10_coverage': top_10_coverage,
        'top_20_coverage': top_20_coverage,
        'top_tokens': dict(link_adjacent_tokens.most_common(20)),
        'supports_symbolic_labeling': supports,
        'verdict': 'PASS - Concentrated reuse at attention points' if supports else 'FAIL - Diffuse vocabulary'
    }

    print(f"\n** RESULT: {'SUPPORTS' if supports else 'DOES NOT SUPPORT'} symbolic labeling **")

    return result


# =============================================================================
# TEST D: ORDER INSENSITIVITY WITH ROLE CONSISTENCY
# =============================================================================

def test_order_insensitivity(df: pd.DataFrame, metrics: Dict[str, dict]) -> dict:
    """
    TEST D: Do tokens show no sensitivity to linear order but consistent
    role persistence?

    This supports label persistence, not syntax.
    If tokens require ordering to make sense -> FAIL (no syntax in this system)
    """
    print("\n" + "=" * 70)
    print("TEST D: ORDER INSENSITIVITY WITH ROLE CONSISTENCY")
    print("=" * 70)

    tokens = df['word'].tolist()
    sections = df['section'].tolist()

    # Test 1: Position variance within role
    # If roles are positional (syntax-like), variance should be LOW
    # If roles are order-insensitive, variance should be HIGH

    role_positions = defaultdict(list)
    for token, m in metrics.items():
        role = classify_behavioral_role(m)
        role_positions[role].append(m['mean_position'])

    role_variances = {}
    for role, positions in role_positions.items():
        if len(positions) >= 5:
            role_variances[role] = np.var(positions)

    mean_variance = np.mean(list(role_variances.values())) if role_variances else 0

    print(f"\nPosition variance by role (higher = more order-insensitive):")
    for role, var in sorted(role_variances.items(), key=lambda x: -x[1]):
        print(f"  {role}: variance = {var:.3f}")

    print(f"\nMean position variance: {mean_variance:.3f}")

    # Test 2: Bigram predictability
    # If there's syntax, certain tokens should predict next tokens
    # Low predictability = no syntax

    bigram_counts = Counter()
    unigram_counts = Counter()

    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i+1]
        if is_human_track(t1) and is_human_track(t2):
            bigram_counts[(t1, t2)] += 1
            unigram_counts[t1] += 1

    # Calculate conditional entropy (lower = more predictable)
    if unigram_counts:
        conditional_probs = []
        for (t1, t2), count in bigram_counts.items():
            p = count / unigram_counts[t1]
            conditional_probs.append(p)

        # High entropy = unpredictable = no syntax
        mean_transition_prob = np.mean(conditional_probs) if conditional_probs else 0
        max_transition_prob = max(conditional_probs) if conditional_probs else 0
    else:
        mean_transition_prob = 0
        max_transition_prob = 0

    print(f"\nBigram predictability (lower = less syntax-like):")
    print(f"  Mean transition probability: {mean_transition_prob:.3f}")
    print(f"  Max transition probability: {max_transition_prob:.3f}")

    # Test 3: Role persistence within runs
    # Same token repeated should maintain same role

    run_role_consistency = []
    current_token = None
    current_run_roles = []

    for i, t in enumerate(tokens):
        if is_human_track(t) and t in metrics:
            if t == current_token:
                current_run_roles.append(classify_behavioral_role(metrics[t]))
            else:
                if len(current_run_roles) > 1:
                    # Check consistency
                    unique_roles = len(set(current_run_roles))
                    run_role_consistency.append(1 if unique_roles == 1 else 0)
                current_token = t
                current_run_roles = [classify_behavioral_role(metrics[t])]

    role_consistency = np.mean(run_role_consistency) if run_role_consistency else 1.0

    print(f"\nRole consistency within runs: {role_consistency*100:.1f}%")

    # Decision
    # Supports if: high variance (>0.05) + low predictability (<0.3) + high consistency (>80%)
    # This means: position-free labeling with consistent role identity

    order_insensitive = mean_variance > 0.05
    syntax_free = max_transition_prob < 0.30
    role_persistent = role_consistency > 0.80

    supports = order_insensitive and syntax_free and role_persistent

    result = {
        'test': 'D',
        'name': 'Order Insensitivity with Role Consistency',
        'mean_position_variance': mean_variance,
        'role_variances': role_variances,
        'mean_transition_prob': mean_transition_prob,
        'max_transition_prob': max_transition_prob,
        'role_consistency': role_consistency,
        'order_insensitive': order_insensitive,
        'syntax_free': syntax_free,
        'role_persistent': role_persistent,
        'supports_symbolic_labeling': supports,
        'verdict': 'PASS - Order-free with role persistence' if supports else 'FAIL - Shows ordering or inconsistency'
    }

    print(f"\n** RESULT: {'SUPPORTS' if supports else 'DOES NOT SUPPORT'} symbolic labeling **")

    return result


# =============================================================================
# TEST E: EXCLUSIVE ROLE CONTEXTS
# =============================================================================

def test_exclusive_contexts(df: pd.DataFrame, metrics: Dict[str, dict]) -> dict:
    """
    TEST E: Are there contexts where only one functional label appears,
    and substitution with another breaks contextual coherence?

    This tests semantic exclusivity without rank.
    """
    print("\n" + "=" * 70)
    print("TEST E: EXCLUSIVE ROLE CONTEXTS")
    print("=" * 70)

    tokens = df['word'].tolist()

    # Define context types based on surrounding structure
    def get_context_type(idx):
        """Classify context by surrounding tokens."""
        left_kernel = False
        right_kernel = False
        left_link = False
        right_link = False

        # Check left context
        for j in range(max(0, idx-3), idx):
            if has_kernel_char(tokens[j]):
                left_kernel = True
            if is_link_context(tokens[j]):
                left_link = True

        # Check right context
        for j in range(idx+1, min(len(tokens), idx+4)):
            if has_kernel_char(tokens[j]):
                right_kernel = True
            if is_link_context(tokens[j]):
                right_link = True

        # Classify context
        if left_kernel and right_link:
            return 'KERNEL_TO_LINK'
        elif left_link and right_kernel:
            return 'LINK_TO_KERNEL'
        elif left_link and right_link:
            return 'LINK_INTERIOR'
        elif left_kernel and right_kernel:
            return 'KERNEL_INTERIOR'
        elif left_kernel:
            return 'POST_KERNEL'
        elif right_kernel:
            return 'PRE_KERNEL'
        elif left_link:
            return 'POST_LINK'
        elif right_link:
            return 'PRE_LINK'
        else:
            return 'NEUTRAL_CONTEXT'

    # Build context->role distribution
    context_roles = defaultdict(Counter)

    for i, t in enumerate(tokens):
        if is_human_track(t) and t in metrics:
            ctx = get_context_type(i)
            role = classify_behavioral_role(metrics[t])
            context_roles[ctx][role] += 1

    # Calculate exclusivity per context
    context_exclusivity = {}
    for ctx, role_counts in context_roles.items():
        total = sum(role_counts.values())
        if total >= 20:  # Minimum sample
            dominant_role = role_counts.most_common(1)[0][0]
            dominant_count = role_counts[dominant_role]
            exclusivity = dominant_count / total
            context_exclusivity[ctx] = {
                'dominant_role': dominant_role,
                'exclusivity': exclusivity,
                'total': total,
                'distribution': dict(role_counts)
            }

    print(f"\nContext types analyzed: {len(context_exclusivity)}")
    print(f"\nRole exclusivity by context:")

    exclusive_contexts = 0
    for ctx, data in sorted(context_exclusivity.items(), key=lambda x: -x[1]['exclusivity']):
        print(f"  {ctx}:")
        print(f"    Dominant: {data['dominant_role']} ({data['exclusivity']*100:.1f}%)")
        print(f"    Total: {data['total']}")
        if data['exclusivity'] > 0.6:
            exclusive_contexts += 1

    # Calculate overall exclusivity score
    if context_exclusivity:
        exclusivity_scores = [d['exclusivity'] for d in context_exclusivity.values()]
        mean_exclusivity = np.mean(exclusivity_scores)
        n_exclusive = sum(1 for e in exclusivity_scores if e > 0.6)
    else:
        mean_exclusivity = 0
        n_exclusive = 0

    print(f"\nMean exclusivity score: {mean_exclusivity*100:.1f}%")
    print(f"Contexts with >60% exclusivity: {n_exclusive}/{len(context_exclusivity)}")

    # Decision
    # Supports if: multiple contexts show >60% role exclusivity
    supports = n_exclusive >= 2 and mean_exclusivity > 0.5

    result = {
        'test': 'E',
        'name': 'Exclusive Role Contexts',
        'n_contexts': len(context_exclusivity),
        'n_exclusive_contexts': n_exclusive,
        'mean_exclusivity': mean_exclusivity,
        'context_details': context_exclusivity,
        'supports_symbolic_labeling': supports,
        'verdict': 'PASS - Role-context exclusivity found' if supports else 'FAIL - No exclusive contexts'
    }

    print(f"\n** RESULT: {'SUPPORTS' if supports else 'DOES NOT SUPPORT'} symbolic labeling **")

    return result


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_report(results: List[dict]) -> str:
    """Generate the Human-Track Language-Likeness Assessment report."""

    n_passed = sum(1 for r in results if r['supports_symbolic_labeling'])
    final_verdict = 'WEAKLY SUPPORTED' if n_passed >= 3 else 'FALSIFIED'

    lines = []

    lines.append("# Human-Track Language-Likeness Assessment (Post-HOT)")
    lines.append("")
    lines.append("**Phase:** HLL-2 - Symbolic Label Collapse Probe")
    lines.append("**Date:** 2026-01-04")
    lines.append("**Prerequisite:** Phase HOT (ordinal hierarchy falsified)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary verdict
    lines.append("## 1. Summary Verdict")
    lines.append("")
    lines.append(f"**FINAL DETERMINATION: {final_verdict}**")
    lines.append("")
    lines.append(f"Tests supporting symbolic labeling: **{n_passed}/5**")
    lines.append(f"Threshold for support: >= 3/5")
    lines.append("")

    if final_verdict == 'WEAKLY SUPPORTED':
        lines.append("> Human-track tokens behave like a limited symbolic labeling system for orientation and attentional stance.")
    else:
        lines.append("> Human-track tokens do NOT exhibit consistent symbolic labeling behavior. The linguistic hypothesis is EXHAUSTED.")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Test results matrix
    lines.append("## 2. Test Results Matrix")
    lines.append("")
    lines.append("| Test | Name | Result | Supports? |")
    lines.append("|------|------|--------|-----------|")

    for r in results:
        support = "YES" if r['supports_symbolic_labeling'] else "NO"
        lines.append(f"| {r['test']} | {r['name']} | {r['verdict'].split(' - ')[0]} | {support} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Strongest evidence FOR
    lines.append("## 3. Strongest Evidence FOR Symbolic Labeling")
    lines.append("")

    supporting = [r for r in results if r['supports_symbolic_labeling']]
    if supporting:
        for r in supporting:
            lines.append(f"### Test {r['test']}: {r['name']}")
            lines.append("")
            lines.append(f"**Verdict:** {r['verdict']}")
            lines.append("")

            if r['test'] == 'A':
                lines.append(f"- Vocabulary compressed to {r['n_roles']} core roles")
                lines.append(f"- Compression ratio: {r['compression_ratio']:.1f}:1")
            elif r['test'] == 'B':
                lines.append(f"- Functional coverage: {r['mean_coverage']*100:.1f}%")
                lines.append(f"- Dialectal variation: {r['mean_dialectal_uniqueness']*100:.1f}%")
            elif r['test'] == 'C':
                lines.append(f"- Top 20 tokens cover {r['top_20_coverage']*100:.1f}% of attention contexts")
            elif r['test'] == 'D':
                lines.append(f"- Position variance: {r['mean_position_variance']:.3f} (order-insensitive)")
                lines.append(f"- Role consistency: {r['role_consistency']*100:.1f}%")
            elif r['test'] == 'E':
                lines.append(f"- Exclusive contexts: {r['n_exclusive_contexts']}")
                lines.append(f"- Mean exclusivity: {r['mean_exclusivity']*100:.1f}%")

            lines.append("")
    else:
        lines.append("*No tests supported symbolic labeling.*")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Strongest evidence AGAINST
    lines.append("## 4. Strongest Evidence AGAINST Symbolic Labeling")
    lines.append("")

    opposing = [r for r in results if not r['supports_symbolic_labeling']]
    if opposing:
        for r in opposing:
            lines.append(f"### Test {r['test']}: {r['name']}")
            lines.append("")
            lines.append(f"**Verdict:** {r['verdict']}")
            lines.append("")

            if r['test'] == 'A':
                lines.append(f"- Compression ratio only {r['compression_ratio']:.1f}:1 (weak)")
            elif r['test'] == 'B':
                lines.append(f"- Functional coverage only {r['mean_coverage']*100:.1f}%")
            elif r['test'] == 'C':
                lines.append(f"- Top 20 tokens cover only {r['top_20_coverage']*100:.1f}%")
            elif r['test'] == 'D':
                if not r['order_insensitive']:
                    lines.append(f"- Low position variance suggests ordering matters")
                if not r['syntax_free']:
                    lines.append(f"- High transition probability suggests syntax")
                if not r['role_persistent']:
                    lines.append(f"- Role inconsistency within runs")
            elif r['test'] == 'E':
                lines.append(f"- Only {r['n_exclusive_contexts']} exclusive contexts found")

            lines.append("")
    else:
        lines.append("*All tests supported symbolic labeling.*")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Final determination
    lines.append("## 5. Final Determination")
    lines.append("")
    lines.append(f"### Verdict: **{final_verdict}**")
    lines.append("")

    if final_verdict == 'WEAKLY SUPPORTED':
        lines.append("The human-track tokens exhibit behavior consistent with a **limited symbolic labeling system**.")
        lines.append("")
        lines.append("**What this means:**")
        lines.append("- Tokens function as reusable labels for position, phase-identity, or attentional stance")
        lines.append("- The vocabulary compresses to a small set of functional roles")
        lines.append("- Labels are consistent in function but vary in form across sections (dialectal)")
        lines.append("- No syntax or ordering requirements")
        lines.append("")
        lines.append("**What this does NOT mean:**")
        lines.append("- These are NOT words in a natural language")
        lines.append("- These do NOT encode intensity scales or ranked states (falsified in HOT)")
        lines.append("- These cannot be translated to any known language")
        lines.append("")
        lines.append("**Scope of support:**")
        supporting_tests = [r['test'] for r in results if r['supports_symbolic_labeling']]
        if len(supporting_tests) == 5:
            lines.append("- GLOBAL support across all dimensions tested")
        elif all(r['supports_symbolic_labeling'] for r in results if r['test'] in ['A', 'B']):
            lines.append("- GLOBAL support for vocabulary structure")
        else:
            lines.append("- SECTION-LOCAL support (functions vary by section)")
    else:
        lines.append("The human-track tokens do **NOT** exhibit consistent symbolic labeling behavior.")
        lines.append("")
        lines.append("**Implications:**")
        lines.append("- The linguistic hypothesis space is **EXHAUSTED**")
        lines.append("- Human-track tokens are navigation/orientation markup, not symbolic labels")
        lines.append("- No further linguistic tests are warranted")
        lines.append("")
        lines.append("**What remains possible:**")
        lines.append("- Tokens serve as section/position markers")
        lines.append("- Tokens are scribal/organizational notation")
        lines.append("- Tokens have no recoverable semantic content")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Explicit Exclusions (from Phase HOT)")
    lines.append("")
    lines.append("The following interpretations were **NOT tested** because they were already falsified:")
    lines.append("")
    lines.append("- Ordinal hierarchies (low -> medium -> high)")
    lines.append("- Ranked intensity scales")
    lines.append("- Severity or stress ladders")
    lines.append("- Apparatus-global parameters")
    lines.append("")
    lines.append("These remain **FALSIFIED** regardless of HLL-2 outcome.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Phase HLL-2 complete. Linguistic hypothesis space exhausted.*")

    return '\n'.join(lines)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main analysis pipeline."""
    print("=" * 70)
    print("PHASE HLL-2: HUMAN-TRACK LANGUAGE-LIKENESS STRESS TEST (REVISED)")
    print("Symbolic Label Collapse Probe")
    print("=" * 70)

    # Load data
    transcript_path = Path("data/transcriptions/interlinear_full_words.txt")

    if not transcript_path.exists():
        print(f"ERROR: Transcription file not found: {transcript_path}")
        return

    print(f"\nLoading transcription from {transcript_path}...")
    df = load_transcription(transcript_path)
    print(f"Loaded {len(df)} tokens from {df['folio'].nunique()} folios")

    # Count human-track tokens
    ht_mask = df['word'].apply(is_human_track)
    print(f"Human-track tokens: {ht_mask.sum()} ({100*ht_mask.mean():.1f}%)")

    # Compute metrics
    print("\nComputing behavioral metrics...")
    metrics = compute_token_metrics(df, min_freq=10)
    print(f"Analyzed {len(metrics)} frequent human-track tokens")

    # Run all tests
    results = []

    results.append(test_vocabulary_pressure(metrics))
    results.append(test_equivalence_stability(metrics))
    results.append(test_reuse_economy(df, metrics))
    results.append(test_order_insensitivity(df, metrics))
    results.append(test_exclusive_contexts(df, metrics))

    # Generate report
    print("\n" + "=" * 70)
    print("GENERATING REPORT")
    print("=" * 70)

    report = generate_report(results)

    # Save report
    output_dir = Path("phases/HLL2_language_likeness")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "language_likeness_assessment_post_hot.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Save detailed results
    results_path = output_dir / "test_results.json"

    # Convert sets to lists for JSON serialization
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        else:
            return obj

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(results), f, indent=2)
    print(f"Detailed results saved to: {results_path}")

    # Final summary
    n_passed = sum(1 for r in results if r['supports_symbolic_labeling'])
    final_verdict = 'WEAKLY SUPPORTED' if n_passed >= 3 else 'FALSIFIED'

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(f"\nTests passed: {n_passed}/5")
    print(f"\n** FINAL VERDICT: {final_verdict} **")

    if final_verdict == 'WEAKLY SUPPORTED':
        print("\nHuman-track tokens behave like a limited symbolic labeling system")
        print("for orientation and attentional stance.")
    else:
        print("\nHuman-track tokens do NOT exhibit symbolic labeling behavior.")
        print("Linguistic hypothesis space is EXHAUSTED.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
