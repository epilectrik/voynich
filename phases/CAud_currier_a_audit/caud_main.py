"""
Phase CAud: Currier A Executability Boundary Audit

Determines whether Currier A text is executable under the frozen B-derived grammar.

Three Admissible Conclusions:
1. EXECUTABLE - A operates under frozen grammar (same system)
2. RELATED_NON_EXECUTING - A is structurally related but non-executable layer
3. DISJOINT - A is a separate non-system layer

8 Tracks with pre-registered PASS/FAIL criteria.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Any
import numpy as np
from scipy import stats as sp_stats

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# =============================================================================
# DATA LOADING
# =============================================================================

def load_transcription_data() -> List[Dict]:
    """Load transcription with Currier designation."""
    filepath = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    data = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 13:
                word = parts[0].strip('"')
                folio = parts[2].strip('"')
                language = parts[6].strip('"')  # Currier A/B/NA
                transcriber = parts[12].strip('"')

                # Filter to canonical transcriber only
                if transcriber == 'H' and word:
                    data.append({
                        'word': word.lower(),
                        'folio': folio,
                        'currier': language,
                    })
    return data


def load_grammar_symbols() -> Set[str]:
    """Load symbols from canonical grammar."""
    grammar_path = PROJECT_ROOT / 'results' / 'canonical_grammar.json'

    with open(grammar_path, 'r', encoding='utf-8') as f:
        grammar = json.load(f)

    symbols = set()
    for item in grammar.get('terminals', {}).get('list', []):
        symbols.add(item['symbol'].lower())

    return symbols


def load_forbidden_pairs() -> Set[Tuple[str, str]]:
    """Load the 17 forbidden transition pairs."""
    # Hardcoded from hazards.py
    pairs = [
        ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'), ('chol', 'r'),
        ('chedy', 'ee'), ('chey', 'chedy'), ('l', 'chol'),
        ('dy', 'aiin'), ('dy', 'chey'), ('or', 'dal'), ('ar', 'chol'),
        ('qo', 'shey'), ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'),
        ('dar', 'qokaiin'), ('qokaiin', 'qokedy'),
    ]

    forbidden = set()
    for a, b in pairs:
        forbidden.add((a, b))
        forbidden.add((b, a))  # Bidirectional

    return forbidden


def load_hazard_tokens() -> Set[str]:
    """Load tokens that participate in forbidden transitions."""
    pairs = load_forbidden_pairs()
    tokens = set()
    for a, b in pairs:
        tokens.add(a)
        tokens.add(b)
    return tokens


def load_operational_tokens() -> Set[str]:
    """Load known operational tokens (from prior analysis)."""
    # Core operational vocabulary from CLAUDE.md
    return {
        'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
        'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
        'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
        'al', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
        'chor', 'char', 'shor', 'shal', 'shol', 's', 'o', 'd', 'y',
        'a', 'e', 'l', 'r', 'k', 'h', 'c', 't', 'n', 'p', 'm', 'g', 'f',
        'dain', 'chain', 'shain', 'ain', 'in', 'an', 'dan',
    }


def load_grammar_prefixes() -> Set[str]:
    """Load grammar-significant prefixes."""
    return {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}


def load_grammar_suffixes() -> Set[str]:
    """Load grammar-significant suffixes."""
    return {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}


# =============================================================================
# TRACK 0: FOLIO ATOMICITY
# =============================================================================

def track_0_atomicity(currier_a_data: List[Dict], currier_b_data: List[Dict]) -> Dict:
    """
    Test: Does Currier A respect 1-folio = 1 autonomous unit?

    PASS: Mean cross-folio MI <= B baseline, orphaned transitions <= 5%
    FAIL: Cross-folio MI > 2x B, orphaned > 20%
    """
    print("\n" + "=" * 70)
    print("TRACK 0: FOLIO ATOMICITY TEST")
    print("=" * 70)

    # Group by folio
    a_by_folio = defaultdict(list)
    b_by_folio = defaultdict(list)

    for d in currier_a_data:
        a_by_folio[d['folio']].append(d['word'])
    for d in currier_b_data:
        b_by_folio[d['folio']].append(d['word'])

    # Calculate vocabulary overlap between adjacent folios
    def calc_adjacent_overlap(folios_dict):
        folios = sorted(folios_dict.keys())
        overlaps = []
        for i in range(len(folios) - 1):
            vocab_1 = set(folios_dict[folios[i]])
            vocab_2 = set(folios_dict[folios[i + 1]])
            if vocab_1 and vocab_2:
                intersection = len(vocab_1 & vocab_2)
                union = len(vocab_1 | vocab_2)
                overlaps.append(intersection / union if union > 0 else 0)
        return np.mean(overlaps) if overlaps else 0

    a_overlap = calc_adjacent_overlap(a_by_folio)
    b_overlap = calc_adjacent_overlap(b_by_folio)

    # Check folio sizes (atomicity indicator)
    a_sizes = [len(tokens) for tokens in a_by_folio.values()]
    b_sizes = [len(tokens) for tokens in b_by_folio.values()]

    a_mean_size = np.mean(a_sizes) if a_sizes else 0
    b_mean_size = np.mean(b_sizes) if b_sizes else 0

    # Orphaned transitions: tokens that only appear once and at folio boundary
    # (simplified: check if single-occurrence tokens are boundary-adjacent)
    all_a_tokens = [d['word'] for d in currier_a_data]
    a_token_counts = Counter(all_a_tokens)
    hapax = {t for t, c in a_token_counts.items() if c == 1}
    hapax_rate = len(hapax) / len(a_token_counts) if a_token_counts else 0

    print(f"\nCurrier A folios: {len(a_by_folio)}")
    print(f"Currier B folios: {len(b_by_folio)}")
    print(f"\nA mean tokens/folio: {a_mean_size:.1f}")
    print(f"B mean tokens/folio: {b_mean_size:.1f}")
    print(f"\nA adjacent folio overlap (Jaccard): {a_overlap:.4f}")
    print(f"B adjacent folio overlap (Jaccard): {b_overlap:.4f}")
    print(f"Overlap ratio (A/B): {a_overlap/b_overlap:.2f}x" if b_overlap > 0 else "N/A")
    print(f"\nA hapax legomena rate: {hapax_rate:.1%}")

    # Verdict
    overlap_ratio = a_overlap / b_overlap if b_overlap > 0 else float('inf')

    if overlap_ratio <= 1.0 and hapax_rate <= 0.5:
        verdict = "PASS"
        reasoning = "A shows similar or lower cross-folio dependency than B"
    elif overlap_ratio > 2.0 or hapax_rate > 0.8:
        verdict = "FAIL"
        reasoning = "A shows excessive cross-folio dependency or fragmentation"
    else:
        verdict = "AMBIGUOUS"
        reasoning = "Metrics in intermediate range"

    print(f"\n** TRACK 0 VERDICT: {verdict} **")
    print(f"   {reasoning}")

    return {
        'track': 0,
        'name': 'Folio Atomicity',
        'verdict': verdict,
        'a_folios': len(a_by_folio),
        'b_folios': len(b_by_folio),
        'a_mean_size': a_mean_size,
        'b_mean_size': b_mean_size,
        'a_overlap': a_overlap,
        'b_overlap': b_overlap,
        'overlap_ratio': overlap_ratio,
        'hapax_rate': hapax_rate,
        'reasoning': reasoning,
    }


# =============================================================================
# TRACK 1-2: GRAMMAR COVERAGE AND TRANSITION VALIDITY
# =============================================================================

def track_1_2_grammar(currier_a_data: List[Dict], grammar_symbols: Set[str],
                       currier_b_data: List[Dict]) -> Dict:
    """
    Track 1: Grammar coverage (% of A tokens in 49-class grammar)
    Track 2: Transition validity (do class-to-class transitions respect grammar?)

    PASS (EXECUTABLE): Coverage >= 90%, validity >= 85%
    FAIL: Coverage < 70% or validity < 60%
    """
    print("\n" + "=" * 70)
    print("TRACK 1-2: GRAMMAR COVERAGE & TRANSITION VALIDITY")
    print("=" * 70)

    # Track 1: Coverage
    a_tokens = [d['word'] for d in currier_a_data]
    b_tokens = [d['word'] for d in currier_b_data]

    a_unique = set(a_tokens)
    b_unique = set(b_tokens)

    a_in_grammar = sum(1 for t in a_tokens if t in grammar_symbols)
    b_in_grammar = sum(1 for t in b_tokens if t in grammar_symbols)

    a_coverage = a_in_grammar / len(a_tokens) if a_tokens else 0
    b_coverage = b_in_grammar / len(b_tokens) if b_tokens else 0

    # Novel tokens (in A but not in B vocab)
    a_only = a_unique - b_unique
    novel_rate = len(a_only) / len(a_unique) if a_unique else 0

    # Missing tokens (high-freq B tokens not in A)
    b_counts = Counter(b_tokens)
    b_top_100 = {t for t, _ in b_counts.most_common(100)}
    missing_high_freq = b_top_100 - a_unique
    missing_rate = len(missing_high_freq) / len(b_top_100) if b_top_100 else 0

    print(f"\nTrack 1: Grammar Coverage")
    print(f"-" * 40)
    print(f"Currier A tokens: {len(a_tokens)}")
    print(f"Currier A unique types: {len(a_unique)}")
    print(f"A tokens in grammar: {a_in_grammar} ({a_coverage:.1%})")
    print(f"B tokens in grammar (baseline): {b_coverage:.1%}")
    print(f"\nA-only tokens (novel): {len(a_only)} ({novel_rate:.1%})")
    print(f"Missing B high-freq tokens: {len(missing_high_freq)} ({missing_rate:.1%})")

    # Track 2: Transition validity
    # Check if consecutive tokens form valid transitions
    # (simplified: check if both tokens are in grammar)
    valid_transitions = 0
    total_transitions = 0

    # Group by folio and check transitions within each
    a_by_folio = defaultdict(list)
    for d in currier_a_data:
        a_by_folio[d['folio']].append(d['word'])

    folio_validities = []
    for folio, tokens in a_by_folio.items():
        folio_valid = 0
        folio_total = 0
        for i in range(len(tokens) - 1):
            t1, t2 = tokens[i], tokens[i + 1]
            folio_total += 1
            total_transitions += 1
            # Both tokens must be in grammar for valid transition
            if t1 in grammar_symbols and t2 in grammar_symbols:
                folio_valid += 1
                valid_transitions += 1
        if folio_total > 0:
            folio_validities.append(folio_valid / folio_total)

    overall_validity = valid_transitions / total_transitions if total_transitions > 0 else 0
    low_validity_folios = sum(1 for v in folio_validities if v < 0.5)
    low_validity_rate = low_validity_folios / len(folio_validities) if folio_validities else 0

    print(f"\nTrack 2: Transition Validity")
    print(f"-" * 40)
    print(f"Total transitions: {total_transitions}")
    print(f"Valid transitions: {valid_transitions} ({overall_validity:.1%})")
    print(f"Folios with <50% validity: {low_validity_folios} ({low_validity_rate:.1%})")

    # Verdicts
    t1_verdict = "PASS" if a_coverage >= 0.90 else ("FAIL" if a_coverage < 0.70 else "AMBIGUOUS")
    t2_verdict = "PASS" if overall_validity >= 0.85 else ("FAIL" if overall_validity < 0.60 else "AMBIGUOUS")

    if t1_verdict == "PASS" and t2_verdict == "PASS":
        combined = "PASS"
        reasoning = "High coverage AND valid transitions -> likely EXECUTABLE"
    elif t1_verdict == "PASS" and t2_verdict == "FAIL":
        combined = "RELATED_NON_EXECUTING"
        reasoning = "Vocabulary overlap but invalid sequences -> non-executable usage"
    elif t1_verdict == "FAIL":
        combined = "DISJOINT"
        reasoning = "Low grammar coverage -> different vocabulary system"
    else:
        combined = "AMBIGUOUS"
        reasoning = "Metrics in intermediate range"

    print(f"\n** TRACK 1 VERDICT: {t1_verdict} ** (coverage {a_coverage:.1%})")
    print(f"** TRACK 2 VERDICT: {t2_verdict} ** (validity {overall_validity:.1%})")
    print(f"** COMBINED: {combined} **")
    print(f"   {reasoning}")

    return {
        'track': '1-2',
        'name': 'Grammar Coverage & Transition Validity',
        'verdict': combined,
        't1_coverage': a_coverage,
        't1_verdict': t1_verdict,
        't2_validity': overall_validity,
        't2_verdict': t2_verdict,
        'a_tokens': len(a_tokens),
        'a_unique': len(a_unique),
        'novel_rate': novel_rate,
        'missing_rate': missing_rate,
        'low_validity_rate': low_validity_rate,
        'reasoning': reasoning,
    }


# =============================================================================
# TRACK 3: HAZARD TOPOLOGY
# =============================================================================

def track_3_hazards(currier_a_data: List[Dict], forbidden_pairs: Set[Tuple[str, str]],
                    hazard_tokens: Set[str]) -> Dict:
    """
    Test: Do the 17 forbidden transitions apply to Currier A?

    PASS (EXECUTABLE): 0 violations, approach rate similar to B
    PASS (RELATED_NON_EXECUTING): 0 violations, high avoidance
    FAIL: Frequent violations -> DISJOINT
    """
    print("\n" + "=" * 70)
    print("TRACK 3: HAZARD TOPOLOGY TEST")
    print("=" * 70)

    # Group by folio
    a_by_folio = defaultdict(list)
    for d in currier_a_data:
        a_by_folio[d['folio']].append(d['word'])

    violations = 0
    approaches = 0  # One token of pair present but not violation
    total_transitions = 0
    hazard_token_count = 0

    for folio, tokens in a_by_folio.items():
        for i, t in enumerate(tokens):
            if t in hazard_tokens:
                hazard_token_count += 1

            if i < len(tokens) - 1:
                t1, t2 = tokens[i], tokens[i + 1]
                total_transitions += 1

                if (t1, t2) in forbidden_pairs:
                    violations += 1
                elif t1 in hazard_tokens or t2 in hazard_tokens:
                    approaches += 1

    violation_rate = violations / total_transitions if total_transitions > 0 else 0
    approach_rate = approaches / total_transitions if total_transitions > 0 else 0
    hazard_presence = hazard_token_count / len([d['word'] for d in currier_a_data]) if currier_a_data else 0

    print(f"\nForbidden pairs checked: {len(forbidden_pairs) // 2}")
    print(f"Total transitions in A: {total_transitions}")
    print(f"\nViolations: {violations} ({violation_rate:.4%})")
    print(f"Approaches (near-miss): {approaches} ({approach_rate:.1%})")
    print(f"Hazard token presence: {hazard_token_count} ({hazard_presence:.1%})")

    # Verdict
    if violations > 0:
        verdict = "FAIL"
        hazard_verdict = "DISJOINT"
        reasoning = f"{violations} forbidden transitions occur -> A operates under different rules"
    elif approach_rate < 0.05:
        verdict = "PASS"
        hazard_verdict = "AVOIDANCE"
        reasoning = "Zero violations AND low approach rate -> active avoidance (HT-like)"
    else:
        verdict = "PASS"
        hazard_verdict = "NORMAL"
        reasoning = "Zero violations with normal approach rate -> respects hazard topology"

    print(f"\n** TRACK 3 VERDICT: {verdict} ({hazard_verdict}) **")
    print(f"   {reasoning}")

    return {
        'track': 3,
        'name': 'Hazard Topology',
        'verdict': verdict,
        'hazard_verdict': hazard_verdict,
        'violations': violations,
        'violation_rate': violation_rate,
        'approaches': approaches,
        'approach_rate': approach_rate,
        'hazard_presence': hazard_presence,
        'reasoning': reasoning,
    }


# =============================================================================
# TRACK 4: HT vs SYSTEM-TRACK CLASSIFICATION
# =============================================================================

def track_4_classification(currier_a_data: List[Dict],
                           operational_tokens: Set[str],
                           hazard_tokens: Set[str],
                           grammar_prefixes: Set[str],
                           grammar_suffixes: Set[str],
                           forbidden_pairs: Set[Tuple[str, str]]) -> Dict:
    """
    Test: Does Currier A behave like human-track or system-track?

    Necessary conditions for system-track:
    1. Appears near hazards
    2. Participates in forbidden seams
    3. Removing tokens breaks transitions
    """
    print("\n" + "=" * 70)
    print("TRACK 4: HT vs SYSTEM-TRACK CLASSIFICATION")
    print("=" * 70)

    a_tokens = [d['word'] for d in currier_a_data]
    a_unique = set(a_tokens)

    # % in operational token set
    in_operational = sum(1 for t in a_tokens if t in operational_tokens)
    operational_rate = in_operational / len(a_tokens) if a_tokens else 0

    # % in hazard tokens
    in_hazard = sum(1 for t in a_tokens if t in hazard_tokens)
    hazard_rate = in_hazard / len(a_tokens) if a_tokens else 0

    # % matching grammar prefixes/suffixes
    def has_grammar_morphology(token):
        for pf in grammar_prefixes:
            if token.startswith(pf):
                return True
        for sf in grammar_suffixes:
            if token.endswith(sf):
                return True
        return False

    with_morphology = sum(1 for t in a_tokens if has_grammar_morphology(t))
    morphology_rate = with_morphology / len(a_tokens) if a_tokens else 0

    # Presence at forbidden seams
    a_by_folio = defaultdict(list)
    for d in currier_a_data:
        a_by_folio[d['folio']].append(d['word'])

    seam_presence = 0
    near_hazard = 0
    for folio, tokens in a_by_folio.items():
        for i in range(len(tokens) - 1):
            t1, t2 = tokens[i], tokens[i + 1]
            if (t1, t2) in forbidden_pairs or (t2, t1) in forbidden_pairs:
                seam_presence += 1
            if t1 in hazard_tokens or t2 in hazard_tokens:
                near_hazard += 1

    total_trans = sum(len(tokens) - 1 for tokens in a_by_folio.values() if len(tokens) > 1)
    near_hazard_rate = near_hazard / total_trans if total_trans > 0 else 0

    print(f"\nCurrier A Classification Metrics:")
    print(f"-" * 40)
    print(f"In operational tokens: {operational_rate:.1%}")
    print(f"In hazard tokens: {hazard_rate:.1%}")
    print(f"Has grammar morphology: {morphology_rate:.1%}")
    print(f"At forbidden seams: {seam_presence}")
    print(f"Near hazard tokens: {near_hazard_rate:.1%}")

    # System-track necessary conditions
    appears_near_hazards = hazard_rate > 0.01 or near_hazard_rate > 0.05
    participates_seams = seam_presence > 0
    has_operational_vocab = operational_rate > 0.3

    system_conditions_met = sum([appears_near_hazards, participates_seams, has_operational_vocab])

    print(f"\nSystem-Track Conditions:")
    print(f"  1. Appears near hazards: {'YES' if appears_near_hazards else 'NO'}")
    print(f"  2. Participates in seams: {'YES' if participates_seams else 'NO'}")
    print(f"  3. Has operational vocabulary: {'YES' if has_operational_vocab else 'NO'}")
    print(f"  Conditions met: {system_conditions_met}/3")

    if system_conditions_met >= 2:
        verdict = "SYSTEM_TRACK"
        reasoning = "Meets multiple system-track conditions -> likely executable"
    elif system_conditions_met == 0:
        verdict = "HT_LIKE"
        reasoning = "Fails all system-track conditions -> HT-like non-executable"
    else:
        verdict = "MIXED"
        reasoning = "Partial system-track indicators -> may be transitional"

    print(f"\n** TRACK 4 VERDICT: {verdict} **")
    print(f"   {reasoning}")

    return {
        'track': 4,
        'name': 'HT vs System-Track Classification',
        'verdict': verdict,
        'operational_rate': operational_rate,
        'hazard_rate': hazard_rate,
        'morphology_rate': morphology_rate,
        'seam_presence': seam_presence,
        'near_hazard_rate': near_hazard_rate,
        'conditions_met': system_conditions_met,
        'reasoning': reasoning,
    }


# =============================================================================
# TRACK 5: MORPHOLOGICAL INDEPENDENCE
# =============================================================================

def track_5_morphology(currier_a_data: List[Dict], currier_b_data: List[Dict]) -> Dict:
    """
    Test: Does A use different prefix/suffix patterns than B?

    Known: Prefix-suffix archetypes 1, 3, 4 never appear in B-text
    """
    print("\n" + "=" * 70)
    print("TRACK 5: MORPHOLOGICAL INDEPENDENCE TEST")
    print("=" * 70)

    a_tokens = set(d['word'] for d in currier_a_data)
    b_tokens = set(d['word'] for d in currier_b_data)

    # Extract prefixes and suffixes
    def get_prefixes(tokens, length=2):
        return Counter(t[:length] for t in tokens if len(t) >= length)

    def get_suffixes(tokens, length=2):
        return Counter(t[-length:] for t in tokens if len(t) >= length)

    a_prefixes = get_prefixes(a_tokens)
    b_prefixes = get_prefixes(b_tokens)
    a_suffixes = get_suffixes(a_tokens)
    b_suffixes = get_suffixes(b_tokens)

    # A-exclusive morphemes
    a_only_prefixes = set(a_prefixes.keys()) - set(b_prefixes.keys())
    a_only_suffixes = set(a_suffixes.keys()) - set(b_suffixes.keys())
    b_only_prefixes = set(b_prefixes.keys()) - set(a_prefixes.keys())
    b_only_suffixes = set(b_suffixes.keys()) - set(a_suffixes.keys())

    shared_prefixes = set(a_prefixes.keys()) & set(b_prefixes.keys())
    shared_suffixes = set(a_suffixes.keys()) & set(b_suffixes.keys())

    prefix_overlap = len(shared_prefixes) / len(set(a_prefixes.keys()) | set(b_prefixes.keys()))
    suffix_overlap = len(shared_suffixes) / len(set(a_suffixes.keys()) | set(b_suffixes.keys()))

    print(f"\nPrefix Analysis:")
    print(f"  A prefixes: {len(a_prefixes)}")
    print(f"  B prefixes: {len(b_prefixes)}")
    print(f"  A-only prefixes: {len(a_only_prefixes)}")
    print(f"  B-only prefixes: {len(b_only_prefixes)}")
    print(f"  Shared: {len(shared_prefixes)} ({prefix_overlap:.1%})")

    print(f"\nSuffix Analysis:")
    print(f"  A suffixes: {len(a_suffixes)}")
    print(f"  B suffixes: {len(b_suffixes)}")
    print(f"  A-only suffixes: {len(a_only_suffixes)}")
    print(f"  B-only suffixes: {len(b_only_suffixes)}")
    print(f"  Shared: {len(shared_suffixes)} ({suffix_overlap:.1%})")

    if a_only_prefixes:
        print(f"\nTop A-only prefixes: {sorted(a_only_prefixes)[:10]}")
    if a_only_suffixes:
        print(f"Top A-only suffixes: {sorted(a_only_suffixes)[:10]}")

    # Verdict
    morphological_divergence = (1 - prefix_overlap + 1 - suffix_overlap) / 2

    if morphological_divergence > 0.3:
        verdict = "DIVERGENT"
        reasoning = f"Significant morphological independence ({morphological_divergence:.1%} divergence)"
    elif morphological_divergence < 0.1:
        verdict = "CONVERGENT"
        reasoning = f"Morphology highly similar ({morphological_divergence:.1%} divergence)"
    else:
        verdict = "MODERATE"
        reasoning = f"Partial morphological overlap ({morphological_divergence:.1%} divergence)"

    print(f"\n** TRACK 5 VERDICT: {verdict} **")
    print(f"   {reasoning}")

    return {
        'track': 5,
        'name': 'Morphological Independence',
        'verdict': verdict,
        'a_only_prefixes': len(a_only_prefixes),
        'a_only_suffixes': len(a_only_suffixes),
        'b_only_prefixes': len(b_only_prefixes),
        'b_only_suffixes': len(b_only_suffixes),
        'prefix_overlap': prefix_overlap,
        'suffix_overlap': suffix_overlap,
        'divergence': morphological_divergence,
        'reasoning': reasoning,
    }


# =============================================================================
# TRACK 6: LINK/KERNEL CONTACT
# =============================================================================

def track_6_control(currier_a_data: List[Dict], currier_b_data: List[Dict]) -> Dict:
    """
    Test: Does A show same control structure signatures?

    B values: LINK density ~38%, Kernel contact ~62%
    """
    print("\n" + "=" * 70)
    print("TRACK 6: LINK/KERNEL CONTACT TEST")
    print("=" * 70)

    # LINK tokens
    link_tokens = {'ol', 'or', 'ar', 'al', 'ain', 'aiin'}

    # Kernel tokens
    kernel_tokens = {'k', 'h', 'e', 's', 't', 'd', 'l', 'o', 'c', 'r'}

    a_tokens = [d['word'] for d in currier_a_data]
    b_tokens = [d['word'] for d in currier_b_data]

    # LINK density
    a_link = sum(1 for t in a_tokens if t in link_tokens)
    b_link = sum(1 for t in b_tokens if t in link_tokens)
    a_link_density = a_link / len(a_tokens) if a_tokens else 0
    b_link_density = b_link / len(b_tokens) if b_tokens else 0

    # Kernel contact (single-char kernel tokens)
    a_kernel = sum(1 for t in a_tokens if t in kernel_tokens)
    b_kernel = sum(1 for t in b_tokens if t in kernel_tokens)
    a_kernel_density = a_kernel / len(a_tokens) if a_tokens else 0
    b_kernel_density = b_kernel / len(b_tokens) if b_tokens else 0

    # Check for kernel-adjacent patterns (tokens containing kernel chars)
    def kernel_contact_rate(tokens):
        contact = 0
        for t in tokens:
            for k in kernel_tokens:
                if k in t:
                    contact += 1
                    break
        return contact / len(tokens) if tokens else 0

    a_contact = kernel_contact_rate(a_tokens)
    b_contact = kernel_contact_rate(b_tokens)

    print(f"\nLINK Density:")
    print(f"  Currier A: {a_link_density:.1%}")
    print(f"  Currier B: {b_link_density:.1%}")
    print(f"  Ratio (A/B): {a_link_density/b_link_density:.2f}x" if b_link_density > 0 else "N/A")

    print(f"\nKernel Token Density:")
    print(f"  Currier A: {a_kernel_density:.1%}")
    print(f"  Currier B: {b_kernel_density:.1%}")

    print(f"\nKernel Contact Rate:")
    print(f"  Currier A: {a_contact:.1%}")
    print(f"  Currier B: {b_contact:.1%}")

    # Verdict
    link_ratio = a_link_density / b_link_density if b_link_density > 0 else 0
    contact_ratio = a_contact / b_contact if b_contact > 0 else 0

    if 0.7 <= link_ratio <= 1.3 and 0.7 <= contact_ratio <= 1.3:
        verdict = "SAME_SYSTEM"
        reasoning = "LINK and kernel patterns within expected range for same system"
    elif link_ratio < 0.5 or link_ratio > 2.0:
        verdict = "DIFFERENT"
        reasoning = f"LINK density diverges significantly (ratio {link_ratio:.2f}x)"
    else:
        verdict = "MODERATE"
        reasoning = "Partial overlap in control signatures"

    print(f"\n** TRACK 6 VERDICT: {verdict} **")
    print(f"   {reasoning}")

    return {
        'track': 6,
        'name': 'LINK/Kernel Contact',
        'verdict': verdict,
        'a_link_density': a_link_density,
        'b_link_density': b_link_density,
        'link_ratio': link_ratio,
        'a_kernel_density': a_kernel_density,
        'b_kernel_density': b_kernel_density,
        'a_contact': a_contact,
        'b_contact': b_contact,
        'contact_ratio': contact_ratio,
        'reasoning': reasoning,
    }


# =============================================================================
# TRACK 7: STRUCTURAL DENSITY
# =============================================================================

def track_7_density(currier_a_data: List[Dict], currier_b_data: List[Dict]) -> Dict:
    """
    Test: Is A "sparse/definitional" or "dense/procedural"?

    Reference:
    - Z, A sections = ~2-3 tokens/folio (label-like)
    - B, H sections = ~8-12 tokens/folio (procedural)
    """
    print("\n" + "=" * 70)
    print("TRACK 7: STRUCTURAL DENSITY TEST")
    print("=" * 70)

    # Group by folio
    a_by_folio = defaultdict(list)
    b_by_folio = defaultdict(list)

    for d in currier_a_data:
        a_by_folio[d['folio']].append(d['word'])
    for d in currier_b_data:
        b_by_folio[d['folio']].append(d['word'])

    # Tokens per folio
    a_sizes = [len(tokens) for tokens in a_by_folio.values()]
    b_sizes = [len(tokens) for tokens in b_by_folio.values()]

    a_mean = np.mean(a_sizes) if a_sizes else 0
    b_mean = np.mean(b_sizes) if b_sizes else 0
    a_median = np.median(a_sizes) if a_sizes else 0
    b_median = np.median(b_sizes) if b_sizes else 0

    # Diversity (unique/total)
    a_all = [d['word'] for d in currier_a_data]
    b_all = [d['word'] for d in currier_b_data]

    a_diversity = len(set(a_all)) / len(a_all) if a_all else 0
    b_diversity = len(set(b_all)) / len(b_all) if b_all else 0

    # Token length distribution
    a_lengths = [len(t) for t in a_all]
    b_lengths = [len(t) for t in b_all]

    a_mean_len = np.mean(a_lengths) if a_lengths else 0
    b_mean_len = np.mean(b_lengths) if b_lengths else 0

    print(f"\nTokens per Folio:")
    print(f"  Currier A mean: {a_mean:.1f}")
    print(f"  Currier A median: {a_median:.1f}")
    print(f"  Currier B mean: {b_mean:.1f}")
    print(f"  Currier B median: {b_median:.1f}")

    print(f"\nVocabulary Diversity (unique/total):")
    print(f"  Currier A: {a_diversity:.3f}")
    print(f"  Currier B: {b_diversity:.3f}")

    print(f"\nMean Token Length:")
    print(f"  Currier A: {a_mean_len:.2f}")
    print(f"  Currier B: {b_mean_len:.2f}")

    # Verdict (supportive only)
    density_ratio = a_mean / b_mean if b_mean > 0 else 0

    if density_ratio < 0.5:
        verdict = "SPARSE"
        reasoning = f"A is much sparser than B (ratio {density_ratio:.2f}x) - label-like"
    elif density_ratio > 1.5:
        verdict = "DENSE"
        reasoning = f"A is denser than B (ratio {density_ratio:.2f}x) - procedural"
    else:
        verdict = "SIMILAR"
        reasoning = f"A has similar density to B (ratio {density_ratio:.2f}x)"

    print(f"\n** TRACK 7 VERDICT: {verdict} ** (supportive evidence only)")
    print(f"   {reasoning}")

    return {
        'track': 7,
        'name': 'Structural Density',
        'verdict': verdict,
        'a_mean_size': a_mean,
        'b_mean_size': b_mean,
        'density_ratio': density_ratio,
        'a_diversity': a_diversity,
        'b_diversity': b_diversity,
        'a_mean_length': a_mean_len,
        'b_mean_length': b_mean_len,
        'reasoning': reasoning,
    }


# =============================================================================
# TRACK 8: EXECUTION SIMULATION
# =============================================================================

def track_8_simulation(currier_a_data: List[Dict], grammar_symbols: Set[str]) -> Dict:
    """
    Test: Can A be executed at all?

    Not testing success - testing attemptability.
    PASS: <10% immediate stalls, <20% dead ends
    FAIL: >50% immediate stalls OR >50% dead ends
    """
    print("\n" + "=" * 70)
    print("TRACK 8: EXECUTION SIMULATION ATTEMPT")
    print("=" * 70)

    # Group by folio
    a_by_folio = defaultdict(list)
    for d in currier_a_data:
        a_by_folio[d['folio']].append(d['word'])

    folio_results = []
    total_stalls = 0
    total_tokens = 0

    for folio, tokens in a_by_folio.items():
        stalls = 0
        for t in tokens:
            total_tokens += 1
            if t not in grammar_symbols:
                stalls += 1
                total_stalls += 1

        stall_rate = stalls / len(tokens) if tokens else 0
        folio_results.append({
            'folio': folio,
            'tokens': len(tokens),
            'stalls': stalls,
            'stall_rate': stall_rate,
        })

    overall_stall_rate = total_stalls / total_tokens if total_tokens > 0 else 0

    # Dead ends: consecutive unrecognized tokens
    dead_ends = 0
    for folio, tokens in a_by_folio.items():
        consecutive_unknown = 0
        for t in tokens:
            if t not in grammar_symbols:
                consecutive_unknown += 1
                if consecutive_unknown >= 3:  # 3+ consecutive unknown = dead end
                    dead_ends += 1
            else:
                consecutive_unknown = 0

    dead_end_rate = dead_ends / len(a_by_folio) if a_by_folio else 0

    high_stall_folios = sum(1 for r in folio_results if r['stall_rate'] > 0.5)
    high_stall_rate = high_stall_folios / len(folio_results) if folio_results else 0

    print(f"\nExecution Attemptability:")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Immediate stalls (unrecognized): {total_stalls} ({overall_stall_rate:.1%})")
    print(f"  Dead ends (3+ consecutive unknown): {dead_ends}")
    print(f"  Folios with >50% stall rate: {high_stall_folios} ({high_stall_rate:.1%})")

    # Verdict
    if overall_stall_rate < 0.10 and high_stall_rate < 0.20:
        verdict = "PASS"
        reasoning = "Low stall rate - execution is attemptable"
    elif overall_stall_rate > 0.50 or high_stall_rate > 0.50:
        verdict = "FAIL"
        reasoning = f"High stall rate ({overall_stall_rate:.1%}) - execution would fail"
    else:
        verdict = "MARGINAL"
        reasoning = f"Intermediate stall rate ({overall_stall_rate:.1%}) - partial attemptability"

    print(f"\n** TRACK 8 VERDICT: {verdict} **")
    print(f"   {reasoning}")

    return {
        'track': 8,
        'name': 'Execution Simulation',
        'verdict': verdict,
        'total_tokens': total_tokens,
        'stalls': total_stalls,
        'stall_rate': overall_stall_rate,
        'dead_ends': dead_ends,
        'dead_end_rate': dead_end_rate,
        'high_stall_folios': high_stall_folios,
        'high_stall_rate': high_stall_rate,
        'reasoning': reasoning,
    }


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

def determine_final_verdict(results: Dict) -> str:
    """
    Apply decision tree to determine final verdict.

    Three Admissible Conclusions:
    1. EXECUTABLE - A operates under frozen grammar
    2. RELATED_NON_EXECUTING - A is structurally related but non-executable
    3. DISJOINT - A is a separate non-system layer
    """
    # Track 0: Atomicity gate
    if results['track_0']['verdict'] == 'FAIL':
        return 'DISJOINT', 'A fails folio atomicity - not program-structured'

    # Track 1-2: Grammar gate
    t12_verdict = results['track_1_2']['verdict']
    if t12_verdict == 'DISJOINT':
        return 'DISJOINT', 'Low grammar coverage - different vocabulary system'
    if t12_verdict == 'RELATED_NON_EXECUTING':
        return 'RELATED_NON_EXECUTING', 'Vocabulary overlap but invalid sequences'

    # Track 3: Hazard gate
    if results['track_3']['verdict'] == 'FAIL':
        return 'DISJOINT', 'Forbidden transitions occur - different rules'
    if results['track_3']['hazard_verdict'] == 'AVOIDANCE':
        # Strong HT-like signal
        pass

    # Track 4: Classification
    t4_verdict = results['track_4']['verdict']

    # Count system-track vs HT-like signals
    system_signals = 0
    ht_signals = 0

    if t4_verdict == 'SYSTEM_TRACK':
        system_signals += 2
    elif t4_verdict == 'HT_LIKE':
        ht_signals += 2
    else:
        system_signals += 1
        ht_signals += 1

    if results['track_3']['hazard_verdict'] == 'AVOIDANCE':
        ht_signals += 1
    elif results['track_3']['hazard_verdict'] == 'NORMAL':
        system_signals += 1

    if results['track_6']['verdict'] == 'SAME_SYSTEM':
        system_signals += 1
    elif results['track_6']['verdict'] == 'DIFFERENT':
        ht_signals += 1

    if results['track_8']['verdict'] == 'PASS':
        system_signals += 1
    elif results['track_8']['verdict'] == 'FAIL':
        ht_signals += 1

    # Final decision
    if system_signals > ht_signals + 1:
        return 'EXECUTABLE', f'System-track signals dominate ({system_signals} vs {ht_signals})'
    elif ht_signals > system_signals + 1:
        return 'RELATED_NON_EXECUTING', f'HT-like signals dominate ({ht_signals} vs {system_signals})'
    else:
        return 'RELATED_NON_EXECUTING', f'Mixed signals (system={system_signals}, HT={ht_signals}) - default to non-executing'


def main():
    print("=" * 70)
    print("PHASE CAud: CURRIER A EXECUTABILITY BOUNDARY AUDIT")
    print("=" * 70)
    print("\nLoading data...")

    # Load data
    all_data = load_transcription_data()
    currier_a = [d for d in all_data if d['currier'] == 'A']
    currier_b = [d for d in all_data if d['currier'] == 'B']

    print(f"Total tokens loaded: {len(all_data)}")
    print(f"Currier A tokens: {len(currier_a)}")
    print(f"Currier B tokens: {len(currier_b)}")

    # Load infrastructure
    grammar_symbols = load_grammar_symbols()
    forbidden_pairs = load_forbidden_pairs()
    hazard_tokens = load_hazard_tokens()
    operational_tokens = load_operational_tokens()
    grammar_prefixes = load_grammar_prefixes()
    grammar_suffixes = load_grammar_suffixes()

    print(f"Grammar symbols: {len(grammar_symbols)}")
    print(f"Forbidden pairs: {len(forbidden_pairs) // 2}")

    # Run all tracks
    results = {}

    results['track_0'] = track_0_atomicity(currier_a, currier_b)
    results['track_1_2'] = track_1_2_grammar(currier_a, grammar_symbols, currier_b)
    results['track_3'] = track_3_hazards(currier_a, forbidden_pairs, hazard_tokens)
    results['track_4'] = track_4_classification(currier_a, operational_tokens,
                                                  hazard_tokens, grammar_prefixes,
                                                  grammar_suffixes, forbidden_pairs)
    results['track_5'] = track_5_morphology(currier_a, currier_b)
    results['track_6'] = track_6_control(currier_a, currier_b)
    results['track_7'] = track_7_density(currier_a, currier_b)
    results['track_8'] = track_8_simulation(currier_a, grammar_symbols)

    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)

    final_verdict, reasoning = determine_final_verdict(results)

    print(f"\n{'*' * 50}")
    print(f"  CURRIER A CLASSIFICATION: {final_verdict}")
    print(f"{'*' * 50}")
    print(f"\nReasoning: {reasoning}")

    # Summary table
    print("\n" + "-" * 70)
    print("TRACK SUMMARY")
    print("-" * 70)
    print(f"{'Track':<30} {'Verdict':<20} {'Key Metric':<20}")
    print("-" * 70)

    track_order = ['track_0', 'track_1_2', 'track_3', 'track_4',
                   'track_5', 'track_6', 'track_7', 'track_8']

    for track_key in track_order:
        r = results[track_key]
        name = r['name']
        verdict = r['verdict']

        # Key metric varies by track
        if track_key == 'track_0':
            metric = f"overlap_ratio={r['overlap_ratio']:.2f}"
        elif track_key == 'track_1_2':
            metric = f"cov={r['t1_coverage']:.1%}, val={r['t2_validity']:.1%}"
        elif track_key == 'track_3':
            metric = f"violations={r['violations']}"
        elif track_key == 'track_4':
            metric = f"conditions={r['conditions_met']}/3"
        elif track_key == 'track_5':
            metric = f"divergence={r['divergence']:.1%}"
        elif track_key == 'track_6':
            metric = f"link_ratio={r['link_ratio']:.2f}"
        elif track_key == 'track_7':
            metric = f"density_ratio={r['density_ratio']:.2f}"
        elif track_key == 'track_8':
            metric = f"stall_rate={r['stall_rate']:.1%}"

        print(f"{name:<30} {verdict:<20} {metric:<20}")

    print("-" * 70)
    print(f"{'FINAL':<30} {final_verdict:<20}")
    print("=" * 70)

    # Save results
    output_path = Path(__file__).parent / 'caud_results.json'
    results['final_verdict'] = final_verdict
    results['final_reasoning'] = reasoning

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
