#!/usr/bin/env python3
"""
Phase 9: Constraint Collision Analysis
=====================================

Purpose: Discriminate between two top-scoring domains from Phase 8:
- D1: Pharmacology / Materia Medica (6.0/6)
- D2: Alchemical Transformation Grammar (6.0/6)

The goal is to find tests where they CANNOT BOTH BE RIGHT.

Test Batteries:
- 9A: Symmetry vs Asymmetry (directional entropy, reversibility, commutativity)
- 9B: Combination Explosion (core reuse, vocab/operation ratio, combination depth)
- 9C: Outcome Encoding (terminal constraints, terminal clustering, ending emphasis)
"""

import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set
import random

# ============================================================================
# FROZEN MODEL (from Phase 7 - NO CHANGES)
# ============================================================================

MODEL = {
    "clusters": {
        "FLEXIBLE_CORE": {"size": 35, "mean_a_ratio": 0.40},
        "DEFINITION_CORE": {"size": 25, "mean_a_ratio": 0.755},
        "EXPOSITION_CORE": {"size": 33, "mean_a_ratio": 0.122},
        "RESTRICTED_CORE": {"size": 187, "mean_a_ratio": 0.26}
    },
    "operators": {"POSITION": 6, "SCOPE": 16, "SEMANTIC": 8},
    "grammar": {"slots": 10, "rules": 11, "coverage": 0.951},
    "slot_roles": {
        0: "TOPIC_POSITION",
        1: "PRIMARY_CONTENT",
        2: "PRIMARY_CONTENT",
        3: "SECONDARY_CONTENT",
        4: "SECONDARY_CONTENT",
        5: "SECONDARY_CONTENT",
        6: "MODIFIER_POSITION",
        7: "MODIFIER_POSITION",
        8: "TERMINAL_POSITION",
        9: "TERMINAL_POSITION"
    }
}

# Known prefixes and suffixes from Phase 7
KNOWN_PREFIXES = {'qo', 'da', 'ch', 'sh', 'ok', 'ot', 'sa', 'ct', 'yk', 'yp',
                  'ar', 'ko', 'so', 'ra', 'ta', 'op', 'cf', 'fc', 'pc', 'ts',
                  'al', 'ol', 'or', 'dy', 'od', 'ke', 'am', 'lk', 'ka'}
KNOWN_SUFFIXES = {'aiin', 'ol', 'hy', 'or', 'ar', 'ey', 'edy', 'dy', 'y',
                  'al', 'eey', 'eedy', 'ain', 'in', 'an', 'am', 'o'}

# ============================================================================
# CORPUS LOADING
# ============================================================================

def load_corpus():
    """Load the interlinear transcription corpus (PRIMARY transcriber H only)."""
    corpus_path = Path("data/transcriptions/interlinear_full_words.txt")
    records = []

    with open(corpus_path, 'r', encoding='utf-8') as f:
        header = None
        for line in f:
            if line.strip():
                parts = line.strip().split('\t')

                # Handle header
                if header is None:
                    header = parts
                    continue

                if len(parts) >= 13:
                    # Filter to PRIMARY transcriber (H) only - column 12
                    transcriber = parts[12].strip('"')
                    if transcriber != 'H':
                        continue

                    # Remove quotes from fields
                    word = parts[0].strip('"')
                    folio = parts[2].strip('"')
                    language = parts[6].strip('"')  # This is Currier A or B

                    # Skip words with special characters
                    if '*' in word or '?' in word:
                        continue

                    records.append({
                        'folio': folio,
                        'word': word,
                        'population': language  # 'A' or 'B' directly from data
                    })
    return records

def get_prefix(word: str) -> str:
    """Extract prefix from word."""
    for length in [2, 1]:
        if len(word) >= length:
            prefix = word[:length]
            if prefix in KNOWN_PREFIXES:
                return prefix
    return word[:2] if len(word) >= 2 else word

def get_suffix(word: str) -> str:
    """Extract suffix from word."""
    for length in [4, 3, 2, 1]:
        if len(word) >= length:
            suffix = word[-length:]
            if suffix in KNOWN_SUFFIXES:
                return suffix
    return word[-2:] if len(word) >= 2 else word

def get_middle(word: str) -> str:
    """Extract middle from word."""
    prefix = get_prefix(word)
    suffix = get_suffix(word)

    # Handle edge cases
    if len(word) <= len(prefix) + len(suffix):
        return word

    middle = word[len(prefix):-len(suffix)] if suffix else word[len(prefix):]
    return middle if middle else word

def group_by_entry(records: List[Dict]) -> Dict[str, List[str]]:
    """Group tokens by folio (entry)."""
    entries = defaultdict(list)
    for rec in records:
        entries[rec['folio']].append(rec['word'])
    return dict(entries)

def assign_slot_positions(tokens: List[str]) -> List[Tuple[str, int]]:
    """Assign normalized slot positions (0-9) to tokens in an entry."""
    n = len(tokens)
    if n == 0:
        return []

    result = []
    for i, token in enumerate(tokens):
        # Map to 0-9 slot range
        slot = min(9, int((i / n) * 10))
        result.append((token, slot))
    return result

# ============================================================================
# TEST 9A: SYMMETRY VS ASYMMETRY
# ============================================================================

def test_9a_symmetry(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Test whether the slot structure implies irreversible progression (pharmacology)
    or allows symmetric/cyclical patterns (alchemy).
    """
    print("Running Test 9A: Symmetry vs Asymmetry...")

    # A1: Directional Entropy
    a1_result = test_a1_directional_entropy(entries)

    # A2: Entry Reversibility
    a2_result = test_a2_reversibility(entries)

    # A3: Operator Commutativity
    a3_result = test_a3_commutativity(entries)

    # Calculate compatibility
    pharm_compatible = True
    alchemy_compatible = True

    # Pharmacology expects: ratio > 1 (forward more constrained), low reversal legality, low commutativity
    # Alchemy expects: ratio ≈ 1, higher reversal legality, higher commutativity

    discriminators = []

    if a1_result['ratio'] > 1.05:  # Forward significantly more constrained
        alchemy_compatible = False
        discriminators.append(f"A1: Forward entropy ratio {a1_result['ratio']:.3f} > 1.05 rules out alchemy")
    elif a1_result['ratio'] < 0.95:
        pharm_compatible = False
        discriminators.append(f"A1: Forward entropy ratio {a1_result['ratio']:.3f} < 0.95 rules out pharmacology")

    if a2_result['reversal_legality_rate'] < 0.15:
        alchemy_compatible = False
        discriminators.append(f"A2: Reversal legality {a2_result['reversal_legality_rate']:.1%} < 15% rules out alchemy")
    elif a2_result['reversal_legality_rate'] > 0.35:
        pharm_compatible = False
        discriminators.append(f"A2: Reversal legality {a2_result['reversal_legality_rate']:.1%} > 35% rules out pharmacology")

    if a3_result['commutativity_rate'] < 0.25:
        alchemy_compatible = False
        discriminators.append(f"A3: Commutativity {a3_result['commutativity_rate']:.1%} < 25% rules out alchemy")
    elif a3_result['commutativity_rate'] > 0.45:
        pharm_compatible = False
        discriminators.append(f"A3: Commutativity {a3_result['commutativity_rate']:.1%} > 45% rules out pharmacology")

    return {
        "metadata": {
            "phase": "9A",
            "title": "Symmetry vs Asymmetry Test",
            "timestamp": datetime.now().isoformat()
        },
        "tests": {
            "A1_directional_entropy": a1_result,
            "A2_reversibility": a2_result,
            "A3_commutativity": a3_result
        },
        "verdict": {
            "pharmacology_compatible": pharm_compatible,
            "alchemy_compatible": alchemy_compatible,
            "discriminators": discriminators,
            "discriminator_strength": "STRONG" if len(discriminators) >= 2 else ("WEAK" if discriminators else "NONE")
        }
    }

def test_a1_directional_entropy(entries: Dict[str, List[str]]) -> Dict:
    """Measure forward vs backward entropy ratio."""

    # Build transition matrices
    forward_transitions = defaultdict(Counter)  # slot N -> N+1
    backward_transitions = defaultdict(Counter)  # slot N -> N-1

    for folio, tokens in entries.items():
        slot_tokens = assign_slot_positions(tokens)
        for i in range(len(slot_tokens) - 1):
            t1, s1 = slot_tokens[i]
            t2, s2 = slot_tokens[i + 1]
            m1, m2 = get_middle(t1), get_middle(t2)

            # Forward: given position i, what comes at i+1
            forward_transitions[s1][m2] += 1
            # Backward: given position i+1, what was at i
            backward_transitions[s2][m1] += 1

    # Calculate entropy for each direction
    def calc_entropy(counter: Counter) -> float:
        total = sum(counter.values())
        if total == 0:
            return 0
        probs = [c/total for c in counter.values()]
        return -sum(p * math.log2(p) for p in probs if p > 0)

    forward_entropies = []
    backward_entropies = []

    for slot in range(9):  # 0-8, since we look at transitions
        if forward_transitions[slot]:
            forward_entropies.append(calc_entropy(forward_transitions[slot]))
        if backward_transitions[slot + 1]:
            backward_entropies.append(calc_entropy(backward_transitions[slot + 1]))

    mean_forward = sum(forward_entropies) / len(forward_entropies) if forward_entropies else 0
    mean_backward = sum(backward_entropies) / len(backward_entropies) if backward_entropies else 0

    ratio = mean_forward / mean_backward if mean_backward > 0 else 1.0

    return {
        "mean_forward_entropy": round(mean_forward, 4),
        "mean_backward_entropy": round(mean_backward, 4),
        "ratio": round(ratio, 4),
        "interpretation": "forward_more_constrained" if ratio > 1.05 else
                         ("backward_more_constrained" if ratio < 0.95 else "symmetric"),
        "pharmacology_prediction": "ratio > 1.0 (forward constrained)",
        "alchemy_prediction": "ratio ≈ 1.0 (bidirectional)"
    }

def test_a2_reversibility(entries: Dict[str, List[str]]) -> Dict:
    """Test if reversed slot sequences maintain legality."""

    # Get observed transitions (considered "legal")
    observed_transitions = set()

    for folio, tokens in entries.items():
        slot_tokens = assign_slot_positions(tokens)
        for i in range(len(slot_tokens) - 1):
            m1 = get_middle(slot_tokens[i][0])
            m2 = get_middle(slot_tokens[i + 1][0])
            observed_transitions.add((m1, m2))

    # Test reversal legality
    total_reversals = 0
    legal_reversals = 0

    for folio, tokens in list(entries.items())[:200]:  # Sample 200 entries
        slot_tokens = assign_slot_positions(tokens)
        if len(slot_tokens) < 5:
            continue

        # Take middle portion (slots 3-7) and reverse
        middle_tokens = [t for t, s in slot_tokens if 3 <= s <= 7]
        if len(middle_tokens) < 3:
            continue

        reversed_tokens = middle_tokens[::-1]

        # Check if reversed transitions are observed
        for i in range(len(reversed_tokens) - 1):
            total_reversals += 1
            m1, m2 = get_middle(reversed_tokens[i]), get_middle(reversed_tokens[i + 1])
            if (m1, m2) in observed_transitions:
                legal_reversals += 1

    legality_rate = legal_reversals / total_reversals if total_reversals > 0 else 0

    return {
        "total_reversals_tested": total_reversals,
        "legal_reversals": legal_reversals,
        "reversal_legality_rate": round(legality_rate, 4),
        "interpretation": "low_reversibility" if legality_rate < 0.2 else
                         ("moderate_reversibility" if legality_rate < 0.4 else "high_reversibility"),
        "pharmacology_prediction": "<10% reversals legal",
        "alchemy_prediction": ">30% reversals legal"
    }

def test_a3_commutativity(entries: Dict[str, List[str]]) -> Dict:
    """Test if operator pairs commute (order doesn't matter)."""

    # Extract operator (prefix) pairs from entries
    prefix_pair_orders = defaultdict(Counter)  # (p1, p2) sorted -> order counts

    for folio, tokens in entries.items():
        for i in range(len(tokens) - 1):
            p1 = get_prefix(tokens[i])
            p2 = get_prefix(tokens[i + 1])

            if p1 != p2 and p1 in KNOWN_PREFIXES and p2 in KNOWN_PREFIXES:
                # Track both orders for this pair
                pair = tuple(sorted([p1, p2]))
                order = f"{p1}->{p2}"
                prefix_pair_orders[pair][order] += 1

    # Calculate commutativity: pairs where both orders appear with similar frequency
    commutative_pairs = 0
    total_pairs = 0

    for pair, orders in prefix_pair_orders.items():
        if len(orders) < 2:
            continue

        total_pairs += 1
        counts = list(orders.values())
        if len(counts) >= 2:
            ratio = min(counts) / max(counts) if max(counts) > 0 else 0
            if ratio > 0.3:  # Both orders appear at least 30% as often as the other
                commutative_pairs += 1

    commutativity_rate = commutative_pairs / total_pairs if total_pairs > 0 else 0

    return {
        "total_operator_pairs": total_pairs,
        "commutative_pairs": commutative_pairs,
        "commutativity_rate": round(commutativity_rate, 4),
        "interpretation": "low_commutativity" if commutativity_rate < 0.3 else
                         ("moderate_commutativity" if commutativity_rate < 0.5 else "high_commutativity"),
        "pharmacology_prediction": "<20% commutativity",
        "alchemy_prediction": ">40% commutativity"
    }

# ============================================================================
# TEST 9B: COMBINATION EXPLOSION
# ============================================================================

def test_9b_combination(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Test whether the system combines few cores in many ways (alchemy)
    or many cores in few ways (pharmacology).
    """
    print("Running Test 9B: Combination Explosion...")

    # B1: Core Reuse Frequency
    b1_result = test_b1_core_reuse(entries)

    # B2: Vocabulary vs Operation Ratio
    b2_result = test_b2_vocab_operation_ratio(entries)

    # B3: Combination Depth
    b3_result = test_b3_combination_depth(entries, records)

    # Calculate compatibility
    pharm_compatible = True
    alchemy_compatible = True
    discriminators = []

    # Alchemy: high core reuse (>5 paths per core), low ratio (<0.5), low middle count
    # Pharmacology: low core reuse (<3 paths), high ratio (>1.0), higher middle count

    if b1_result['mean_operator_paths_per_core'] > 4.5:
        pharm_compatible = False
        discriminators.append(f"B1: Operator paths/core {b1_result['mean_operator_paths_per_core']:.1f} > 4.5 rules out pharmacology")
    elif b1_result['mean_operator_paths_per_core'] < 2.5:
        alchemy_compatible = False
        discriminators.append(f"B1: Operator paths/core {b1_result['mean_operator_paths_per_core']:.1f} < 2.5 rules out alchemy")

    if b2_result['middle_to_operation_ratio'] < 0.6:
        pharm_compatible = False
        discriminators.append(f"B2: Middle/operation ratio {b2_result['middle_to_operation_ratio']:.2f} < 0.6 rules out pharmacology")
    elif b2_result['middle_to_operation_ratio'] > 1.2:
        alchemy_compatible = False
        discriminators.append(f"B2: Middle/operation ratio {b2_result['middle_to_operation_ratio']:.2f} > 1.2 rules out alchemy")

    if b3_result['b_entry_middle_to_operator_ratio'] < 0.8:
        pharm_compatible = False
        discriminators.append(f"B3: B-entry middle/operator ratio {b3_result['b_entry_middle_to_operator_ratio']:.2f} < 0.8 rules out pharmacology")
    elif b3_result['b_entry_middle_to_operator_ratio'] > 1.5:
        alchemy_compatible = False
        discriminators.append(f"B3: B-entry middle/operator ratio {b3_result['b_entry_middle_to_operator_ratio']:.2f} > 1.5 rules out alchemy")

    return {
        "metadata": {
            "phase": "9B",
            "title": "Combination Explosion Test",
            "timestamp": datetime.now().isoformat()
        },
        "tests": {
            "B1_core_reuse": b1_result,
            "B2_vocab_operation_ratio": b2_result,
            "B3_combination_depth": b3_result
        },
        "verdict": {
            "pharmacology_compatible": pharm_compatible,
            "alchemy_compatible": alchemy_compatible,
            "discriminators": discriminators,
            "discriminator_strength": "STRONG" if len(discriminators) >= 2 else ("WEAK" if discriminators else "NONE")
        }
    }

def test_b1_core_reuse(entries: Dict[str, List[str]]) -> Dict:
    """Count unique operator combinations per core middle."""

    # For each middle, track unique prefix+suffix combinations
    middle_operator_combos = defaultdict(set)

    for folio, tokens in entries.items():
        for token in tokens:
            middle = get_middle(token)
            prefix = get_prefix(token)
            suffix = get_suffix(token)
            combo = f"{prefix}+{suffix}"
            middle_operator_combos[middle].add(combo)

    # Focus on "flexible" cores (middles appearing in 10+ tokens)
    flexible_middles = {m: combos for m, combos in middle_operator_combos.items()
                       if len(combos) >= 5}

    if not flexible_middles:
        return {
            "flexible_cores_analyzed": 0,
            "mean_operator_paths_per_core": 0,
            "max_operator_paths": 0,
            "interpretation": "insufficient_data"
        }

    paths_per_core = [len(combos) for combos in flexible_middles.values()]
    mean_paths = sum(paths_per_core) / len(paths_per_core)

    return {
        "flexible_cores_analyzed": len(flexible_middles),
        "mean_operator_paths_per_core": round(mean_paths, 2),
        "max_operator_paths": max(paths_per_core),
        "top_5_flexible_cores": sorted(
            [(m, len(c)) for m, c in flexible_middles.items()],
            key=lambda x: -x[1]
        )[:5],
        "interpretation": "high_reuse" if mean_paths > 4 else
                         ("moderate_reuse" if mean_paths > 2.5 else "low_reuse"),
        "alchemy_prediction": ">5 operator combinations per core",
        "pharmacology_prediction": "<3 operator combinations per core"
    }

def test_b2_vocab_operation_ratio(entries: Dict[str, List[str]]) -> Dict:
    """Compare number of unique middles to number of unique operator combinations."""

    unique_middles = set()
    unique_operator_combos = set()

    for folio, tokens in entries.items():
        for token in tokens:
            middle = get_middle(token)
            prefix = get_prefix(token)
            suffix = get_suffix(token)

            unique_middles.add(middle)
            unique_operator_combos.add(f"{prefix}+{suffix}")

    ratio = len(unique_middles) / len(unique_operator_combos) if unique_operator_combos else 0

    return {
        "unique_middles": len(unique_middles),
        "unique_operator_combinations": len(unique_operator_combos),
        "middle_to_operation_ratio": round(ratio, 3),
        "interpretation": "vocabulary_dominant" if ratio > 1.0 else
                         ("operation_dominant" if ratio < 0.6 else "balanced"),
        "alchemy_prediction": "ratio < 0.5 (few cores, many operations)",
        "pharmacology_prediction": "ratio > 1.0 (many cores, fewer operations)"
    }

def test_b3_combination_depth(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """Analyze middle count vs operator count in B-text entries."""

    # Separate by population
    a_entries = defaultdict(list)
    b_entries = defaultdict(list)

    for rec in records:
        if rec['population'] == 'A':
            a_entries[rec['folio']].append(rec['word'])
        else:
            b_entries[rec['folio']].append(rec['word'])

    def analyze_entries(entry_dict):
        middle_counts = []
        operator_counts = []

        for folio, tokens in entry_dict.items():
            if len(tokens) < 10:
                continue

            middles = set()
            operators = set()

            for token in tokens:
                middles.add(get_middle(token))
                operators.add(get_prefix(token))
                operators.add(get_suffix(token))

            middle_counts.append(len(middles))
            operator_counts.append(len(operators))

        return middle_counts, operator_counts

    a_middles, a_operators = analyze_entries(a_entries)
    b_middles, b_operators = analyze_entries(b_entries)

    a_ratio = (sum(a_middles) / sum(a_operators)) if a_operators and sum(a_operators) > 0 else 0
    b_ratio = (sum(b_middles) / sum(b_operators)) if b_operators and sum(b_operators) > 0 else 0

    return {
        "a_entries_analyzed": len(a_middles),
        "b_entries_analyzed": len(b_middles),
        "a_mean_unique_middles": round(sum(a_middles)/len(a_middles), 2) if a_middles else 0,
        "b_mean_unique_middles": round(sum(b_middles)/len(b_middles), 2) if b_middles else 0,
        "a_mean_unique_operators": round(sum(a_operators)/len(a_operators), 2) if a_operators else 0,
        "b_mean_unique_operators": round(sum(b_operators)/len(b_operators), 2) if b_operators else 0,
        "a_entry_middle_to_operator_ratio": round(a_ratio, 3),
        "b_entry_middle_to_operator_ratio": round(b_ratio, 3),
        "interpretation": "operator_heavy" if b_ratio < 0.8 else
                         ("middle_heavy" if b_ratio > 1.5 else "balanced"),
        "alchemy_prediction": "Low middle count, high operator count in B",
        "pharmacology_prediction": "Higher middle count, moderate operator count in B"
    }

# ============================================================================
# TEST 9C: OUTCOME ENCODING
# ============================================================================

def test_9c_outcome(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """
    Test whether terminals are privileged (pharmacology - outcome focused)
    or if process is uniformly distributed (alchemy).
    """
    print("Running Test 9C: Outcome Encoding...")

    # C1: Terminal Slot Constraint
    c1_result = test_c1_terminal_constraint(entries)

    # C2: Terminal Middle Clustering
    c2_result = test_c2_terminal_clustering(entries)

    # C3: B-Text Ending Emphasis
    c3_result = test_c3_ending_emphasis(entries, records)

    # Calculate compatibility
    pharm_compatible = True
    alchemy_compatible = True
    discriminators = []

    # Pharmacology: lower terminal entropy ratio (<0.85), high terminal concentration (>55%)
    # Alchemy: similar entropy (ratio > 0.92), distributed terminal vocabulary

    if c1_result['terminal_to_middle_entropy_ratio'] < 0.88:
        alchemy_compatible = False
        discriminators.append(f"C1: Terminal/middle entropy ratio {c1_result['terminal_to_middle_entropy_ratio']:.3f} < 0.88 rules out alchemy")
    elif c1_result['terminal_to_middle_entropy_ratio'] > 0.98:
        pharm_compatible = False
        discriminators.append(f"C1: Terminal/middle entropy ratio {c1_result['terminal_to_middle_entropy_ratio']:.3f} > 0.98 rules out pharmacology")

    if c2_result['top_2_role_concentration'] > 0.55:
        alchemy_compatible = False
        discriminators.append(f"C2: Terminal role concentration {c2_result['top_2_role_concentration']:.1%} > 55% rules out alchemy")
    elif c2_result['top_2_role_concentration'] < 0.35:
        pharm_compatible = False
        discriminators.append(f"C2: Terminal role concentration {c2_result['top_2_role_concentration']:.1%} < 35% rules out pharmacology")

    if c3_result['terminal_operator_density_ratio'] > 1.3:
        alchemy_compatible = False
        discriminators.append(f"C3: Terminal operator density ratio {c3_result['terminal_operator_density_ratio']:.2f} > 1.3 rules out alchemy")
    elif c3_result['terminal_operator_density_ratio'] < 0.8:
        pharm_compatible = False
        discriminators.append(f"C3: Terminal operator density ratio {c3_result['terminal_operator_density_ratio']:.2f} < 0.8 rules out pharmacology")

    return {
        "metadata": {
            "phase": "9C",
            "title": "Outcome Encoding Test",
            "timestamp": datetime.now().isoformat()
        },
        "tests": {
            "C1_terminal_constraint": c1_result,
            "C2_terminal_clustering": c2_result,
            "C3_ending_emphasis": c3_result
        },
        "verdict": {
            "pharmacology_compatible": pharm_compatible,
            "alchemy_compatible": alchemy_compatible,
            "discriminators": discriminators,
            "discriminator_strength": "STRONG" if len(discriminators) >= 2 else ("WEAK" if discriminators else "NONE")
        }
    }

def test_c1_terminal_constraint(entries: Dict[str, List[str]]) -> Dict:
    """Compare entropy of terminal slots (8-9) vs middle slots (3-5)."""

    terminal_middles = Counter()
    middle_middles = Counter()

    for folio, tokens in entries.items():
        slot_tokens = assign_slot_positions(tokens)
        for token, slot in slot_tokens:
            middle = get_middle(token)
            if slot in [8, 9]:
                terminal_middles[middle] += 1
            elif slot in [3, 4, 5]:
                middle_middles[middle] += 1

    def calc_entropy(counter: Counter) -> float:
        total = sum(counter.values())
        if total == 0:
            return 0
        probs = [c/total for c in counter.values()]
        return -sum(p * math.log2(p) for p in probs if p > 0)

    terminal_entropy = calc_entropy(terminal_middles)
    middle_entropy = calc_entropy(middle_middles)

    ratio = terminal_entropy / middle_entropy if middle_entropy > 0 else 1.0

    return {
        "terminal_slot_entropy": round(terminal_entropy, 4),
        "middle_slot_entropy": round(middle_entropy, 4),
        "terminal_to_middle_entropy_ratio": round(ratio, 4),
        "terminal_vocabulary_size": len(terminal_middles),
        "middle_vocabulary_size": len(middle_middles),
        "interpretation": "terminals_constrained" if ratio < 0.9 else
                         ("uniform_distribution" if ratio > 0.95 else "slight_terminal_constraint"),
        "pharmacology_prediction": "ratio < 0.8 (terminals more constrained)",
        "alchemy_prediction": "ratio > 0.9 (similar throughout)"
    }

def test_c2_terminal_clustering(entries: Dict[str, List[str]]) -> Dict:
    """Check if terminal middles cluster tightly or are distributed."""

    terminal_middles = []

    for folio, tokens in entries.items():
        slot_tokens = assign_slot_positions(tokens)
        for token, slot in slot_tokens:
            if slot in [8, 9]:
                terminal_middles.append(get_middle(token))

    # Count frequency of each middle
    counter = Counter(terminal_middles)
    total = sum(counter.values())

    if total == 0:
        return {"interpretation": "no_data"}

    # Calculate concentration in top N middles
    sorted_counts = sorted(counter.values(), reverse=True)
    top_2_concentration = sum(sorted_counts[:2]) / total if len(sorted_counts) >= 2 else 1.0
    top_5_concentration = sum(sorted_counts[:5]) / total if len(sorted_counts) >= 5 else 1.0

    # Estimate role distribution (using prefix as proxy for role)
    terminal_prefixes = Counter(get_prefix(t) for t in terminal_middles if t in counter)
    prefix_concentration = max(terminal_prefixes.values()) / sum(terminal_prefixes.values()) if terminal_prefixes else 0

    return {
        "unique_terminal_middles": len(counter),
        "total_terminal_positions": total,
        "top_2_concentration": round(top_2_concentration, 4),
        "top_5_concentration": round(top_5_concentration, 4),
        "top_2_role_concentration": round(top_2_concentration, 4),  # Using same metric
        "most_common_terminal_middles": counter.most_common(10),
        "interpretation": "tightly_clustered" if top_2_concentration > 0.4 else
                         ("distributed" if top_2_concentration < 0.2 else "moderately_clustered"),
        "pharmacology_prediction": ">60% in 1-2 role clusters",
        "alchemy_prediction": "Distributed across 4+ clusters"
    }

def test_c3_ending_emphasis(entries: Dict[str, List[str]], records: List[Dict]) -> Dict:
    """Compare operator density in initial vs terminal portions of B-entries."""

    # Get B-entries only
    b_entries = defaultdict(list)
    for rec in records:
        if rec['population'] == 'B':
            b_entries[rec['folio']].append(rec['word'])

    initial_operators = []
    terminal_operators = []

    for folio, tokens in b_entries.items():
        if len(tokens) < 15:
            continue

        n = len(tokens)
        third = n // 3

        initial_third = tokens[:third]
        terminal_third = tokens[-third:]

        # Count unique operators in each third
        initial_ops = set()
        terminal_ops = set()

        for t in initial_third:
            initial_ops.add(get_prefix(t))
            initial_ops.add(get_suffix(t))

        for t in terminal_third:
            terminal_ops.add(get_prefix(t))
            terminal_ops.add(get_suffix(t))

        initial_operators.append(len(initial_ops) / len(initial_third))
        terminal_operators.append(len(terminal_ops) / len(terminal_third))

    mean_initial = sum(initial_operators) / len(initial_operators) if initial_operators else 0
    mean_terminal = sum(terminal_operators) / len(terminal_operators) if terminal_operators else 0

    ratio = mean_terminal / mean_initial if mean_initial > 0 else 1.0

    return {
        "b_entries_analyzed": len(initial_operators),
        "mean_initial_operator_density": round(mean_initial, 4),
        "mean_terminal_operator_density": round(mean_terminal, 4),
        "terminal_operator_density_ratio": round(ratio, 4),
        "interpretation": "terminal_emphasis" if ratio > 1.2 else
                         ("initial_emphasis" if ratio < 0.8 else "even_distribution"),
        "pharmacology_prediction": "Terminal density > Initial (building to outcome)",
        "alchemy_prediction": "Even or Initial > Terminal (setup matters)"
    }

# ============================================================================
# SYNTHESIS
# ============================================================================

def synthesize_results(result_9a: Dict, result_9b: Dict, result_9c: Dict) -> Dict:
    """Synthesize results from all three test batteries."""

    print("Synthesizing Phase 9 results...")

    # Collect all compatibility verdicts
    tests = [
        ("9A_Symmetry", result_9a["verdict"]),
        ("9B_Combination", result_9b["verdict"]),
        ("9C_Outcome", result_9c["verdict"])
    ]

    # Count compatibility
    pharm_compatible_count = sum(1 for _, v in tests if v["pharmacology_compatible"])
    alchemy_compatible_count = sum(1 for _, v in tests if v["alchemy_compatible"])

    # Collect all discriminators
    all_discriminators = []
    for name, v in tests:
        for d in v["discriminators"]:
            all_discriminators.append(f"{name}: {d}")

    # Determine final verdict
    if pharm_compatible_count == 3 and alchemy_compatible_count < 3:
        final_verdict = "PHARMACOLOGY_ONLY"
        reason = f"Alchemy eliminated by {3 - alchemy_compatible_count} test battery"
    elif alchemy_compatible_count == 3 and pharm_compatible_count < 3:
        final_verdict = "ALCHEMY_ONLY"
        reason = f"Pharmacology eliminated by {3 - pharm_compatible_count} test battery"
    elif pharm_compatible_count == 3 and alchemy_compatible_count == 3:
        final_verdict = "HYBRID_SYSTEM"
        reason = "Both domains survive all tests - historically plausible fusion"
    elif pharm_compatible_count < 3 and alchemy_compatible_count < 3:
        # Both fail some tests - check which fails more
        if pharm_compatible_count > alchemy_compatible_count:
            final_verdict = "PHARMACOLOGY_FAVORED"
            reason = f"Pharmacology compatible with {pharm_compatible_count}/3, Alchemy {alchemy_compatible_count}/3"
        elif alchemy_compatible_count > pharm_compatible_count:
            final_verdict = "ALCHEMY_FAVORED"
            reason = f"Alchemy compatible with {alchemy_compatible_count}/3, Pharmacology {pharm_compatible_count}/3"
        else:
            final_verdict = "INCONCLUSIVE"
            reason = "Both domains fail equally - tests lack discriminating power"
    else:
        final_verdict = "INCONCLUSIVE"
        reason = "Results do not clearly favor one domain"

    return {
        "metadata": {
            "phase": "9_SYNTHESIS",
            "title": "Constraint Collision Analysis Synthesis",
            "timestamp": datetime.now().isoformat()
        },
        "test_summary": {
            "9A_Symmetry": {
                "pharmacology_compatible": result_9a["verdict"]["pharmacology_compatible"],
                "alchemy_compatible": result_9a["verdict"]["alchemy_compatible"],
                "strength": result_9a["verdict"]["discriminator_strength"]
            },
            "9B_Combination": {
                "pharmacology_compatible": result_9b["verdict"]["pharmacology_compatible"],
                "alchemy_compatible": result_9b["verdict"]["alchemy_compatible"],
                "strength": result_9b["verdict"]["discriminator_strength"]
            },
            "9C_Outcome": {
                "pharmacology_compatible": result_9c["verdict"]["pharmacology_compatible"],
                "alchemy_compatible": result_9c["verdict"]["alchemy_compatible"],
                "strength": result_9c["verdict"]["discriminator_strength"]
            }
        },
        "compatibility_scores": {
            "pharmacology": f"{pharm_compatible_count}/3",
            "alchemy": f"{alchemy_compatible_count}/3"
        },
        "discriminators": all_discriminators,
        "final_verdict": final_verdict,
        "verdict_reason": reason,
        "interpretation": get_interpretation(final_verdict),
        "implications": get_implications(final_verdict, all_discriminators)
    }

def get_interpretation(verdict: str) -> str:
    """Get interpretation for final verdict."""
    interpretations = {
        "PHARMACOLOGY_ONLY": "The system encodes therapeutic materia medica with goal-directed, irreversible application sequences.",
        "ALCHEMY_ONLY": "The system encodes transformation processes with recursive/cyclical structure and bidirectional operations.",
        "HYBRID_SYSTEM": "The system predates the pharmacology/alchemy split OR encodes a hybrid tradition where both patterns coexist.",
        "PHARMACOLOGY_FAVORED": "Evidence leans toward pharmacological encoding but some alchemical patterns remain compatible.",
        "ALCHEMY_FAVORED": "Evidence leans toward alchemical encoding but some pharmacological patterns remain compatible.",
        "INCONCLUSIVE": "Tests lack sufficient discriminating power to determine domain. Need different discriminators OR accept ambiguity."
    }
    return interpretations.get(verdict, "Unknown verdict")

def get_implications(verdict: str, discriminators: List[str]) -> List[str]:
    """Get implications based on verdict."""
    implications = []

    if verdict in ["PHARMACOLOGY_ONLY", "PHARMACOLOGY_FAVORED"]:
        implications.extend([
            "Proceed with pharmacological grounding attempts",
            "Entry structure should map to: substance -> properties -> preparations -> applications",
            "Hub categories likely represent drug classes (purgatives, tonics, etc.)",
            "B-text represents application/recipe elaboration"
        ])
    elif verdict in ["ALCHEMY_ONLY", "ALCHEMY_FAVORED"]:
        implications.extend([
            "Proceed with alchemical grounding attempts",
            "Entry structure should map to: material -> operation -> conditions -> result",
            "Hub categories likely represent stages or metals",
            "Operator sequences may be cyclical/recursive"
        ])
    elif verdict == "HYBRID_SYSTEM":
        implications.extend([
            "Consider iatrochemistry (alchemical medicine) tradition",
            "Both pharmacological AND alchemical templates may be useful",
            "15th century overlap between traditions is historically documented",
            "May need dual-domain grounding approach"
        ])
    else:
        implications.extend([
            "Current tests insufficient for discrimination",
            "Consider external evidence (plant IDs, recipe matches)",
            "May need to develop new discriminating tests"
        ])

    return implications

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_phase9():
    """Execute all Phase 9 tests."""
    print("=" * 60)
    print("PHASE 9: CONSTRAINT COLLISION ANALYSIS")
    print("=" * 60)
    print()
    print("Discriminating between:")
    print("  D1: Pharmacology / Materia Medica")
    print("  D2: Alchemical Transformation Grammar")
    print()

    # Load corpus
    print("Loading corpus...")
    records = load_corpus()
    entries = group_by_entry(records)
    print(f"  Loaded {len(records)} records in {len(entries)} entries")
    print()

    # Run test batteries
    result_9a = test_9a_symmetry(entries, records)
    print()
    result_9b = test_9b_combination(entries, records)
    print()
    result_9c = test_9c_outcome(entries, records)
    print()

    # Synthesize
    synthesis = synthesize_results(result_9a, result_9b, result_9c)

    # Save results
    with open("phase9a_symmetry_test.json", 'w') as f:
        json.dump(result_9a, f, indent=2)
    print("Saved: phase9a_symmetry_test.json")

    with open("phase9b_combination_test.json", 'w') as f:
        json.dump(result_9b, f, indent=2)
    print("Saved: phase9b_combination_test.json")

    with open("phase9c_outcome_test.json", 'w') as f:
        json.dump(result_9c, f, indent=2)
    print("Saved: phase9c_outcome_test.json")

    with open("phase9_synthesis.json", 'w') as f:
        json.dump(synthesis, f, indent=2)
    print("Saved: phase9_synthesis.json")

    # Print summary
    print()
    print("=" * 60)
    print("PHASE 9 RESULTS SUMMARY")
    print("=" * 60)
    print()
    print("Test Battery Results:")
    for name, data in synthesis["test_summary"].items():
        print(f"  {name}:")
        print(f"    Pharmacology compatible: {data['pharmacology_compatible']}")
        print(f"    Alchemy compatible: {data['alchemy_compatible']}")
        print(f"    Discriminator strength: {data['strength']}")
        print()

    print("Compatibility Scores:")
    print(f"  Pharmacology: {synthesis['compatibility_scores']['pharmacology']}")
    print(f"  Alchemy: {synthesis['compatibility_scores']['alchemy']}")
    print()

    if synthesis["discriminators"]:
        print("Key Discriminators:")
        for d in synthesis["discriminators"]:
            print(f"  - {d}")
        print()

    print(f"FINAL VERDICT: {synthesis['final_verdict']}")
    print(f"Reason: {synthesis['verdict_reason']}")
    print()
    print("Interpretation:")
    print(f"  {synthesis['interpretation']}")
    print()
    print("Implications:")
    for imp in synthesis["implications"]:
        print(f"  - {imp}")

if __name__ == "__main__":
    run_phase9()
