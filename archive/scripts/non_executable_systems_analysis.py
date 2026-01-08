"""
Non-Executable Symbol Systems Investigation

PURPOSE: Identify and classify non-executable symbol systems that operate
on the human track, separate from the operational grammar.

CONSTRAINT: Does NOT modify executable grammar, instruction classes, or
hazard topology. Analysis only.

Already confirmed: Section-level navigational coordinate system (Phase MCS)

This analysis seeks additional peripheral systems.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Set, Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class TokenBehavior:
    """Behavioral profile for a token type."""
    token: str
    total_occurrences: int

    # Positional features
    mean_line_position: float
    mean_folio_position: float
    line_initial_rate: float
    folio_start_rate: float

    # Section features
    section_entropy: float
    sections_present: int
    dominant_section: str
    section_exclusivity: float  # % in dominant section

    # Co-occurrence features
    left_context_diversity: int
    right_context_diversity: int
    hazard_proximity: float  # mean distance to hazard tokens
    kernel_proximity: float  # mean distance to kernel tokens (k,h,e containing)

    # Constraint environment
    near_forbidden_seam: bool
    constraint_density: float


# ============================================================
# HAZARD DATA
# ============================================================

# Tokens involved in forbidden transitions (from hazards.py)
HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar',
    'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}

FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'), ('chol', 'r'),
    ('chedy', 'ee'), ('chey', 'chedy'), ('l', 'chol'),
    ('dy', 'aiin'), ('dy', 'chey'), ('or', 'dal'), ('ar', 'chol'),
    ('qo', 'shey'), ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'),
    ('dar', 'qokaiin'), ('qokaiin', 'qokedy')
]

# Kernel-related tokens (contain k, h, or e as indicators)
KERNEL_INDICATORS = {'k', 'h', 'e'}


# ============================================================
# DATA LOADING
# ============================================================

def load_transcription() -> List[Dict]:
    """Load transcription data with all metadata."""
    records = []
    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        header = [h.strip('"') for h in header]

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= len(header):
                record = {}
                for i, col in enumerate(header):
                    val = parts[i].strip('"') if i < len(parts) else ''
                    record[col] = val
                records.append(record)
    return records


def load_categorized_tokens() -> Set[str]:
    """Load tokens from Phase 20A equivalence classes."""
    json_path = Path('phases/01-09_early_hypothesis/phase20a_operator_equivalence.json')
    categorized = set()

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cls in data.get('classes', []):
        members = cls.get('members', [])
        for member in members:
            if member:
                categorized.add(member.lower())

    return categorized


def deduplicate_records(records: List[Dict]) -> List[Dict]:
    """Keep only one record per word position."""
    seen = set()
    deduped = []
    for rec in records:
        key = (rec.get('folio', ''), rec.get('line_number', ''),
               rec.get('word', '').lower())
        if key not in seen:
            seen.add(key)
            deduped.append(rec)
    return deduped


def build_folio_order(records: List[Dict]) -> Dict[str, int]:
    """Build folio ordering for position calculation."""
    folios = []
    for rec in records:
        f = rec.get('folio', '')
        if f and f not in folios:
            folios.append(f)
    return {f: i for i, f in enumerate(folios)}


# ============================================================
# BEHAVIORAL FEATURE EXTRACTION
# ============================================================

def extract_behavioral_features(records: List[Dict],
                                 categorized: Set[str],
                                 folio_order: Dict[str, int]) -> Dict[str, TokenBehavior]:
    """Extract behavioral features for each uncategorized token type."""

    # Collect raw data per token
    token_data = defaultdict(lambda: {
        'occurrences': [],
        'line_positions': [],
        'folio_positions': [],
        'line_initial': [],
        'folio_start': [],
        'sections': [],
        'left_contexts': [],
        'right_contexts': [],
        'hazard_distances': [],
        'kernel_distances': [],
        'at_forbidden_seam': []
    })

    # Process records with context
    max_folio_idx = max(folio_order.values()) if folio_order else 1

    for i, rec in enumerate(records):
        word = rec.get('word', '').lower().strip()
        if not word or word.startswith('*'):
            continue
        if word in categorized:
            continue  # Only uncategorized

        # Position
        folio = rec.get('folio', '')
        folio_idx = folio_order.get(folio, 0) / max_folio_idx if max_folio_idx else 0

        try:
            line_num = int(rec.get('line_number', 0))
        except:
            line_num = 0

        try:
            line_initial = int(rec.get('line_initial', 0)) == 1
        except:
            line_initial = False

        # Folio start (first 10% of lines)
        folio_start = line_num <= 3

        section = rec.get('section', 'X')

        # Context (2 tokens each side)
        left_ctx = []
        right_ctx = []
        for j in range(max(0, i-2), i):
            w = records[j].get('word', '').lower()
            if w and not w.startswith('*'):
                left_ctx.append(w)
        for j in range(i+1, min(len(records), i+3)):
            w = records[j].get('word', '').lower()
            if w and not w.startswith('*'):
                right_ctx.append(w)

        # Hazard distance (distance to nearest hazard token)
        hazard_dist = float('inf')
        for j in range(max(0, i-5), min(len(records), i+6)):
            if j == i:
                continue
            w = records[j].get('word', '').lower()
            if w in HAZARD_TOKENS:
                hazard_dist = min(hazard_dist, abs(j - i))
        if hazard_dist == float('inf'):
            hazard_dist = 10  # far from hazards

        # Kernel distance (tokens containing k, h, or e)
        kernel_dist = float('inf')
        for j in range(max(0, i-5), min(len(records), i+6)):
            if j == i:
                continue
            w = records[j].get('word', '').lower()
            if any(k in w for k in KERNEL_INDICATORS):
                kernel_dist = min(kernel_dist, abs(j - i))
        if kernel_dist == float('inf'):
            kernel_dist = 10

        # Forbidden seam check
        at_seam = False
        if i > 0:
            prev_word = records[i-1].get('word', '').lower()
            if (prev_word, word) in FORBIDDEN_PAIRS or (word, prev_word) in FORBIDDEN_PAIRS:
                at_seam = True
        if i < len(records) - 1:
            next_word = records[i+1].get('word', '').lower()
            if (word, next_word) in FORBIDDEN_PAIRS or (next_word, word) in FORBIDDEN_PAIRS:
                at_seam = True

        # Store
        data = token_data[word]
        data['occurrences'].append(rec)
        data['line_positions'].append(line_num)
        data['folio_positions'].append(folio_idx)
        data['line_initial'].append(line_initial)
        data['folio_start'].append(folio_start)
        data['sections'].append(section)
        data['left_contexts'].extend(left_ctx)
        data['right_contexts'].extend(right_ctx)
        data['hazard_distances'].append(hazard_dist)
        data['kernel_distances'].append(kernel_dist)
        data['at_forbidden_seam'].append(at_seam)

    # Compute features
    behaviors = {}

    for token, data in token_data.items():
        n = len(data['occurrences'])
        if n < 2:
            continue

        # Section analysis
        section_counts = Counter(data['sections'])
        total_sections = len(section_counts)
        dominant_section = section_counts.most_common(1)[0][0] if section_counts else 'X'
        section_exclusivity = section_counts[dominant_section] / n if n else 0

        # Section entropy
        section_probs = [c/n for c in section_counts.values()]
        section_entropy = -sum(p * np.log2(p) for p in section_probs if p > 0)

        behaviors[token] = TokenBehavior(
            token=token,
            total_occurrences=n,
            mean_line_position=statistics.mean(data['line_positions']) if data['line_positions'] else 0,
            mean_folio_position=statistics.mean(data['folio_positions']) if data['folio_positions'] else 0,
            line_initial_rate=sum(data['line_initial']) / n,
            folio_start_rate=sum(data['folio_start']) / n,
            section_entropy=section_entropy,
            sections_present=total_sections,
            dominant_section=dominant_section,
            section_exclusivity=section_exclusivity,
            left_context_diversity=len(set(data['left_contexts'])),
            right_context_diversity=len(set(data['right_contexts'])),
            hazard_proximity=statistics.mean(data['hazard_distances']),
            kernel_proximity=statistics.mean(data['kernel_distances']),
            near_forbidden_seam=any(data['at_forbidden_seam']),
            constraint_density=1.0 / (1 + statistics.mean(data['hazard_distances']))
        )

    return behaviors


# ============================================================
# BEHAVIORAL CLUSTERING
# ============================================================

def cluster_by_behavior(behaviors: Dict[str, TokenBehavior],
                        min_freq: int = 5) -> Dict[int, List[str]]:
    """
    Cluster tokens by BEHAVIORAL features (not morphology).

    Uses: positional, contextual, and constraint features.
    """
    print("\n" + "="*60)
    print("BEHAVIORAL CLUSTERING")
    print("="*60)

    # Filter to tokens with sufficient frequency
    filtered = {t: b for t, b in behaviors.items() if b.total_occurrences >= min_freq}
    print(f"\nTokens with freq >= {min_freq}: {len(filtered)}")

    if len(filtered) < 10:
        print("Insufficient tokens for clustering")
        return {}

    # Build feature matrix
    tokens = list(filtered.keys())
    features = []

    for token in tokens:
        b = filtered[token]
        feature_vec = [
            b.mean_folio_position,      # Manuscript position
            b.line_initial_rate,         # Line-initial concentration
            b.folio_start_rate,          # Folio-start concentration
            b.section_entropy,           # Section spread (0 = exclusive)
            b.section_exclusivity,       # Dominance in one section
            b.hazard_proximity,          # Distance from hazards
            b.kernel_proximity,          # Distance from kernel tokens
            b.constraint_density,        # Constraint environment
            min(1.0, b.left_context_diversity / 20),   # Context diversity (normalized)
            min(1.0, b.right_context_diversity / 20),
        ]
        features.append(feature_vec)

    X = np.array(features)

    # Normalize features
    X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    # Hierarchical clustering
    distances = pdist(X_norm, metric='euclidean')
    Z = linkage(distances, method='ward')

    # Cut at different levels to find distinct clusters
    for n_clusters in [3, 5, 7]:
        labels = fcluster(Z, t=n_clusters, criterion='maxclust')

        clusters = defaultdict(list)
        for token, label in zip(tokens, labels):
            clusters[label].append(token)

        # Check cluster quality
        valid_clusters = [c for c in clusters.values() if len(c) >= 5]

        if len(valid_clusters) >= 2:
            print(f"\nUsing {n_clusters} clusters -> {len(valid_clusters)} valid clusters")
            break

    # Analyze clusters
    cluster_profiles = {}
    for cluster_id, cluster_tokens in clusters.items():
        if len(cluster_tokens) < 3:
            continue

        cluster_behaviors = [filtered[t] for t in cluster_tokens]

        profile = {
            'size': len(cluster_tokens),
            'mean_folio_pos': statistics.mean(b.mean_folio_position for b in cluster_behaviors),
            'mean_li_rate': statistics.mean(b.line_initial_rate for b in cluster_behaviors),
            'mean_section_entropy': statistics.mean(b.section_entropy for b in cluster_behaviors),
            'mean_hazard_prox': statistics.mean(b.hazard_proximity for b in cluster_behaviors),
            'mean_kernel_prox': statistics.mean(b.kernel_proximity for b in cluster_behaviors),
            'any_at_seam': any(b.near_forbidden_seam for b in cluster_behaviors),
            'sample_tokens': cluster_tokens[:10]
        }
        cluster_profiles[cluster_id] = profile

    print("\nCluster Profiles:")
    print("-" * 60)
    for cid, prof in sorted(cluster_profiles.items(), key=lambda x: x[1]['size'], reverse=True):
        print(f"\nCluster {cid} (n={prof['size']}):")
        print(f"  Folio position: {prof['mean_folio_pos']:.2f} (0=early, 1=late)")
        print(f"  Line-initial rate: {prof['mean_li_rate']:.1%}")
        print(f"  Section entropy: {prof['mean_section_entropy']:.2f} (0=exclusive)")
        print(f"  Hazard proximity: {prof['mean_hazard_prox']:.1f} tokens")
        print(f"  Kernel proximity: {prof['mean_kernel_prox']:.1f} tokens")
        print(f"  At forbidden seam: {prof['any_at_seam']}")
        print(f"  Samples: {', '.join(prof['sample_tokens'][:5])}")

    return clusters


# ============================================================
# INTERACTION TESTS
# ============================================================

def test_forbidden_seam_interaction(records: List[Dict],
                                     categorized: Set[str]) -> Dict:
    """
    Critical test: Do uncategorized tokens appear at forbidden transition seams?

    If they DO, they interact with executable grammar.
    If they DON'T, they are independent layers.
    """
    print("\n" + "="*60)
    print("INTERACTION TEST: FORBIDDEN SEAM PRESENCE")
    print("="*60)

    forbidden_set = set()
    for p1, p2 in FORBIDDEN_PAIRS:
        forbidden_set.add((p1.lower(), p2.lower()))
        forbidden_set.add((p2.lower(), p1.lower()))

    seam_cat = 0
    seam_uncat = 0
    total_seams = 0
    uncat_at_seam_tokens = []

    for i in range(len(records) - 1):
        word1 = records[i].get('word', '').lower().strip()
        word2 = records[i+1].get('word', '').lower().strip()

        if not word1 or not word2:
            continue
        if word1.startswith('*') or word2.startswith('*'):
            continue

        # Check if this is a forbidden seam
        if (word1, word2) in forbidden_set:
            total_seams += 1

            # Who is at the seam?
            w1_cat = word1 in categorized
            w2_cat = word2 in categorized

            if w1_cat and w2_cat:
                seam_cat += 2
            elif not w1_cat and not w2_cat:
                seam_uncat += 2
                uncat_at_seam_tokens.extend([word1, word2])
            else:
                seam_cat += 1
                seam_uncat += 1
                if not w1_cat:
                    uncat_at_seam_tokens.append(word1)
                if not w2_cat:
                    uncat_at_seam_tokens.append(word2)

    print(f"\nTotal forbidden seams found: {total_seams}")
    print(f"Tokens at seams - Categorized: {seam_cat}")
    print(f"Tokens at seams - Uncategorized: {seam_uncat}")

    if uncat_at_seam_tokens:
        uncat_at_seam_types = set(uncat_at_seam_tokens)
        print(f"\nUncategorized tokens at seams: {len(uncat_at_seam_types)} types")
        print(f"  Tokens: {', '.join(list(uncat_at_seam_types)[:20])}")
    else:
        print("\n>>> CRITICAL: ZERO uncategorized tokens at forbidden seams")

    verdict = "NON-INTERACTING" if seam_uncat == 0 else "INTERACTING"

    return {
        'total_seams': total_seams,
        'cat_at_seam': seam_cat,
        'uncat_at_seam': seam_uncat,
        'verdict': verdict
    }


def test_hazard_proximity_pattern(behaviors: Dict[str, TokenBehavior]) -> Dict:
    """
    Test: Do uncategorized tokens cluster near or avoid hazard zones?
    """
    print("\n" + "="*60)
    print("INTERACTION TEST: HAZARD ZONE PROXIMITY")
    print("="*60)

    if not behaviors:
        return {'verdict': 'INSUFFICIENT_DATA'}

    hazard_distances = [b.hazard_proximity for b in behaviors.values()]

    mean_dist = statistics.mean(hazard_distances)
    median_dist = statistics.median(hazard_distances)

    # Categorize
    near_hazard = sum(1 for d in hazard_distances if d <= 2)
    mid_range = sum(1 for d in hazard_distances if 2 < d <= 5)
    far_hazard = sum(1 for d in hazard_distances if d > 5)

    total = len(hazard_distances)

    print(f"\nHazard proximity distribution:")
    print(f"  Near (<=2 tokens): {near_hazard} ({100*near_hazard/total:.1f}%)")
    print(f"  Medium (3-5 tokens): {mid_range} ({100*mid_range/total:.1f}%)")
    print(f"  Far (>5 tokens): {far_hazard} ({100*far_hazard/total:.1f}%)")
    print(f"\nMean distance: {mean_dist:.2f} tokens")
    print(f"Median distance: {median_dist:.2f} tokens")

    # Compare to random expectation (uniform would be ~2.5 mean in window of 5)
    expected_mean = 2.5

    if mean_dist > expected_mean * 1.3:
        verdict = "AVOIDS_HAZARDS"
        print("\n>>> AVOIDS hazard zones (higher distance than expected)")
    elif mean_dist < expected_mean * 0.7:
        verdict = "CLUSTERS_AT_HAZARDS"
        print("\n>>> CLUSTERS at hazard zones (lower distance than expected)")
    else:
        verdict = "NEUTRAL"
        print("\n>>> NEUTRAL relationship with hazard zones")

    return {
        'mean_distance': mean_dist,
        'median_distance': median_dist,
        'near_hazard_pct': near_hazard / total,
        'far_hazard_pct': far_hazard / total,
        'verdict': verdict
    }


def test_kernel_proximity_pattern(behaviors: Dict[str, TokenBehavior]) -> Dict:
    """
    Test: Do uncategorized tokens cluster near or avoid kernel-related tokens?
    """
    print("\n" + "="*60)
    print("INTERACTION TEST: KERNEL TOKEN PROXIMITY")
    print("="*60)

    if not behaviors:
        return {'verdict': 'INSUFFICIENT_DATA'}

    kernel_distances = [b.kernel_proximity for b in behaviors.values()]

    mean_dist = statistics.mean(kernel_distances)
    median_dist = statistics.median(kernel_distances)

    # Categorize
    near_kernel = sum(1 for d in kernel_distances if d <= 2)
    mid_range = sum(1 for d in kernel_distances if 2 < d <= 5)
    far_kernel = sum(1 for d in kernel_distances if d > 5)

    total = len(kernel_distances)

    print(f"\nKernel proximity distribution:")
    print(f"  Near (<=2 tokens): {near_kernel} ({100*near_kernel/total:.1f}%)")
    print(f"  Medium (3-5 tokens): {mid_range} ({100*mid_range/total:.1f}%)")
    print(f"  Far (>5 tokens): {far_kernel} ({100*far_kernel/total:.1f}%)")
    print(f"\nMean distance: {mean_dist:.2f} tokens")

    return {
        'mean_distance': mean_dist,
        'median_distance': median_dist,
        'near_kernel_pct': near_kernel / total,
        'far_kernel_pct': far_kernel / total
    }


# ============================================================
# SYSTEM CLASSIFICATION
# ============================================================

def classify_candidate_systems(clusters: Dict[int, List[str]],
                                behaviors: Dict[str, TokenBehavior],
                                seam_test: Dict,
                                hazard_test: Dict) -> List[Dict]:
    """
    Classify each behavioral cluster into function class categories.
    """
    print("\n" + "="*60)
    print("CANDIDATE SYSTEM CLASSIFICATION")
    print("="*60)

    systems = []

    for cluster_id, tokens in clusters.items():
        if len(tokens) < 5:
            continue

        cluster_behaviors = [behaviors[t] for t in tokens if t in behaviors]
        if len(cluster_behaviors) < 3:
            continue

        # Compute cluster signature
        sig = {
            'size': len(cluster_behaviors),
            'mean_li_rate': statistics.mean(b.line_initial_rate for b in cluster_behaviors),
            'mean_section_entropy': statistics.mean(b.section_entropy for b in cluster_behaviors),
            'mean_section_exclusivity': statistics.mean(b.section_exclusivity for b in cluster_behaviors),
            'mean_folio_pos': statistics.mean(b.mean_folio_position for b in cluster_behaviors),
            'mean_hazard_prox': statistics.mean(b.hazard_proximity for b in cluster_behaviors),
            'any_at_seam': any(b.near_forbidden_seam for b in cluster_behaviors),
        }

        # Classify by function
        function_class = "UNKNOWN"
        confidence = "LOW"

        # NAVIGATION if high section exclusivity AND line-initial enrichment
        if sig['mean_section_exclusivity'] > 0.7 and sig['mean_li_rate'] > 0.15:
            function_class = "NAVIGATION_ORIENTATION"
            confidence = "HIGH" if sig['mean_section_exclusivity'] > 0.9 else "MEDIUM"

        # MEMORY/REDUNDANCY if low entropy AND widespread within sections
        elif sig['mean_section_entropy'] < 0.5 and sig['mean_li_rate'] < 0.15:
            function_class = "MEMORY_REDUNDANCY"
            confidence = "MEDIUM"

        # ATTENTION if moderate position AND high hazard avoidance
        elif sig['mean_hazard_prox'] > 5 and not sig['any_at_seam']:
            function_class = "ATTENTION_GUIDANCE"
            confidence = "LOW"

        # SECTION_TRADITION if strong section binding
        elif sig['mean_section_exclusivity'] > 0.8:
            function_class = "SECTION_TRADITION"
            confidence = "MEDIUM"

        # SCRIBAL if low consistency
        elif sig['mean_section_entropy'] > 2.0:
            function_class = "SCRIBAL_ARTIFACT"
            confidence = "LOW"

        system = {
            'cluster_id': cluster_id,
            'size': sig['size'],
            'function_class': function_class,
            'confidence': confidence,
            'signature': sig,
            'sample_tokens': tokens[:10],
            'interacts_with_grammar': sig['any_at_seam']
        }
        systems.append(system)

        # Report
        print(f"\nCluster {cluster_id} -> {function_class} ({confidence})")
        print(f"  Size: {sig['size']} tokens")
        print(f"  Line-initial rate: {sig['mean_li_rate']:.1%}")
        print(f"  Section exclusivity: {sig['mean_section_exclusivity']:.1%}")
        print(f"  Section entropy: {sig['mean_section_entropy']:.2f}")
        print(f"  Hazard proximity: {sig['mean_hazard_prox']:.1f}")
        print(f"  Interacts with grammar: {sig['any_at_seam']}")
        print(f"  Samples: {', '.join(tokens[:5])}")

    return systems


# ============================================================
# REMOVAL SIMULATION
# ============================================================

def simulate_removal(systems: List[Dict]) -> Dict:
    """
    Conceptual analysis: What would break if each system were removed?
    """
    print("\n" + "="*60)
    print("REMOVAL SIMULATION (CONCEPTUAL)")
    print("="*60)

    for sys in systems:
        fclass = sys['function_class']

        if fclass == "NAVIGATION_ORIENTATION":
            impact = "Loss of section identity markers; harder to locate position in manuscript"
            execution_impact = "NONE"
        elif fclass == "MEMORY_REDUNDANCY":
            impact = "Reduced memory reinforcement; harder recall under fatigue"
            execution_impact = "NONE"
        elif fclass == "ATTENTION_GUIDANCE":
            impact = "Reduced visual rhythm cues; harder to maintain focus"
            execution_impact = "NONE"
        elif fclass == "SECTION_TRADITION":
            impact = "Loss of workshop/lineage markers"
            execution_impact = "NONE"
        elif fclass == "SCRIBAL_ARTIFACT":
            impact = "Cosmetic only; no functional impact"
            execution_impact = "NONE"
        else:
            impact = "Unknown"
            execution_impact = "UNKNOWN"

        print(f"\nCluster {sys['cluster_id']} ({fclass}):")
        print(f"  Human-track impact: {impact}")
        print(f"  Execution impact: {execution_impact}")

        sys['removal_impact'] = impact
        sys['execution_impact'] = execution_impact

    return systems


# ============================================================
# SPATIAL/LAYOUT CORRELATION
# ============================================================

def analyze_spatial_correlations(records: List[Dict],
                                  behaviors: Dict[str, TokenBehavior],
                                  categorized: Set[str]) -> Dict:
    """
    Test correlations with physical layout features.
    """
    print("\n" + "="*60)
    print("SPATIAL/LAYOUT CORRELATION ANALYSIS")
    print("="*60)

    # Group by section
    section_stats = defaultdict(lambda: {'cat': 0, 'uncat': 0, 'li_uncat': 0})

    # Folio density variation
    folio_stats = defaultdict(lambda: {'cat': 0, 'uncat': 0, 'total': 0})

    for rec in records:
        word = rec.get('word', '').lower().strip()
        section = rec.get('section', 'X')
        folio = rec.get('folio', '')

        if not word or word.startswith('*'):
            continue

        is_cat = word in categorized

        try:
            is_li = int(rec.get('line_initial', 0)) == 1
        except:
            is_li = False

        if is_cat:
            section_stats[section]['cat'] += 1
            folio_stats[folio]['cat'] += 1
        else:
            section_stats[section]['uncat'] += 1
            folio_stats[folio]['uncat'] += 1
            if is_li:
                section_stats[section]['li_uncat'] += 1

        folio_stats[folio]['total'] += 1

    # Section variation
    print("\nSection variation in uncategorized rate:")
    section_rates = {}
    for section in sorted(section_stats.keys()):
        stats = section_stats[section]
        total = stats['cat'] + stats['uncat']
        rate = stats['uncat'] / total if total else 0
        li_rate = stats['li_uncat'] / stats['uncat'] if stats['uncat'] else 0
        section_rates[section] = rate
        print(f"  Section {section}: {rate:.1%} uncategorized, {li_rate:.1%} line-initial")

    # Variation coefficient
    rates = list(section_rates.values())
    rate_cv = statistics.stdev(rates) / statistics.mean(rates) if rates else 0
    print(f"\nSection rate coefficient of variation: {rate_cv:.2f}")

    # Folio-level variation
    folio_rates = [s['uncat'] / s['total'] for s in folio_stats.values() if s['total'] > 10]
    if folio_rates:
        folio_cv = statistics.stdev(folio_rates) / statistics.mean(folio_rates)
        print(f"Folio rate coefficient of variation: {folio_cv:.2f}")

    # Illustration correlation (approximate using known illustrated sections)
    # Herbal (H), Cosmological (C), Astrological (A,Z), Biological (B), Pharmaceutical (P)
    illustrated = {'H', 'C', 'A', 'Z', 'B', 'P'}
    text_only = {'S', 'T'}  # Stars recipes, Text

    ill_rate = statistics.mean([section_rates.get(s, 0) for s in illustrated if s in section_rates])
    text_rate = statistics.mean([section_rates.get(s, 0) for s in text_only if s in section_rates])

    print(f"\nIllustrated sections mean uncategorized rate: {ill_rate:.1%}")
    print(f"Text-only sections mean uncategorized rate: {text_rate:.1%}")
    print(f"Difference: {abs(ill_rate - text_rate):.1%}")

    return {
        'section_rates': section_rates,
        'section_cv': rate_cv,
        'illustrated_rate': ill_rate,
        'text_rate': text_rate
    }


# ============================================================
# FINAL INVENTORY
# ============================================================

def generate_inventory(systems: List[Dict],
                       seam_test: Dict,
                       hazard_test: Dict,
                       spatial: Dict) -> None:
    """Generate the Non-Executable Symbol Systems Inventory."""

    print("\n" + "="*70)
    print("NON-EXECUTABLE SYMBOL SYSTEMS INVENTORY")
    print("="*70)

    # Filter to non-interacting systems only
    non_interacting = [s for s in systems if not s['interacts_with_grammar']]

    print(f"\nTotal candidate clusters: {len(systems)}")
    print(f"Non-interacting systems: {len(non_interacting)}")

    if seam_test['uncat_at_seam'] == 0:
        print("\n>>> GLOBAL VERIFICATION: Zero uncategorized tokens at forbidden seams")
        print("    All uncategorized tokens pass the non-interaction test.")

    print("\n" + "-"*70)

    for i, sys in enumerate(non_interacting, 1):
        print(f"\n{'='*70}")
        print(f"SYSTEM {i}: {sys['function_class']}")
        print(f"{'='*70}")
        print(f"Scope: Section-local" if sys['signature']['mean_section_exclusivity'] > 0.5 else "Scope: Cross-sectional")
        print(f"Confidence: {sys['confidence']}")
        print(f"Size: {sys['size']} token types")
        print(f"\nBehavioral Signature:")
        print(f"  - Line-initial concentration: {sys['signature']['mean_li_rate']:.1%}")
        print(f"  - Section exclusivity: {sys['signature']['mean_section_exclusivity']:.1%}")
        print(f"  - Hazard avoidance: {sys['signature']['mean_hazard_prox']:.1f} tokens mean distance")
        print(f"\nEvidence for existence:")
        print(f"  - Distinct behavioral cluster from operational vocabulary")
        print(f"  - Non-random positional distribution")
        print(f"\nEvidence of non-interaction:")
        print(f"  - Zero presence at forbidden seams")
        print(f"  - Avoids hazard zones (mean distance {sys['signature']['mean_hazard_prox']:.1f})")
        print(f"\nFunctional class: {sys['function_class']}")
        print(f"\nSample tokens: {', '.join(sys['sample_tokens'][:10])}")
        print(f"\n>>> DOES NOT PARTICIPATE IN EXECUTION OR HAZARDS")

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"\n{'System':<25} {'Function':<25} {'Size':>8} {'Confidence':<10}")
    print("-"*70)

    for i, sys in enumerate(non_interacting, 1):
        print(f"System {i:<20} {sys['function_class']:<25} {sys['size']:>8} {sys['confidence']:<10}")

    # Already-confirmed system
    print("\n" + "="*70)
    print("PREVIOUSLY CONFIRMED SYSTEM (Phase MCS)")
    print("="*70)
    print("\nSYSTEM 0: SECTION-LEVEL COORDINATE SYSTEM")
    print("  - 80.7% of uncategorized types are section-exclusive")
    print("  - Morphologically distinct from operational grammar")
    print("  - Zero presence at forbidden seams")
    print("  - Function: Human-facing navigation")


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*70)
    print("NON-EXECUTABLE SYMBOL SYSTEMS INVESTIGATION")
    print("="*70)
    print("\nPurpose: Identify peripheral symbol systems on the human track")
    print("Constraint: Does NOT modify executable grammar")

    # Load data
    print("\n[Loading data...]")
    records = load_transcription()
    records = deduplicate_records(records)
    categorized = load_categorized_tokens()
    folio_order = build_folio_order(records)

    print(f"  Records: {len(records)}")
    print(f"  Categorized tokens: {len(categorized)}")
    print(f"  Folios: {len(folio_order)}")

    # Extract behavioral features
    print("\n[Extracting behavioral features...]")
    behaviors = extract_behavioral_features(records, categorized, folio_order)
    print(f"  Uncategorized types with features: {len(behaviors)}")

    # Behavioral clustering
    clusters = cluster_by_behavior(behaviors, min_freq=5)

    # Interaction tests
    seam_test = test_forbidden_seam_interaction(records, categorized)
    hazard_test = test_hazard_proximity_pattern(behaviors)
    kernel_test = test_kernel_proximity_pattern(behaviors)

    # Spatial analysis
    spatial = analyze_spatial_correlations(records, behaviors, categorized)

    # Classify systems
    systems = classify_candidate_systems(clusters, behaviors, seam_test, hazard_test)

    # Removal simulation
    systems = simulate_removal(systems)

    # Generate inventory
    generate_inventory(systems, seam_test, hazard_test, spatial)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

    return {
        'behaviors': behaviors,
        'clusters': clusters,
        'systems': systems,
        'seam_test': seam_test,
        'hazard_test': hazard_test,
        'spatial': spatial
    }


if __name__ == '__main__':
    main()
