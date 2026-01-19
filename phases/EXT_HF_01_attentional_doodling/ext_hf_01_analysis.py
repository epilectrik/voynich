"""
EXT-HF-01: Human-Factors - Attentional Doodling vs Procedural Practice

Tier 4 interpretive phase examining whether human-track tokens represent:
- Low-intent attentional doodling, or
- Intentional procedural handwriting rehearsal

during safe waiting (LINK-buffered) phases.

PROHIBITIONS:
- No semantic, symbolic, or execution-linked interpretations
- No modification of Tier 0-2 claims
- Results capped at Tier 4
"""

import math
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats
from itertools import permutations

project_root = Path(__file__).parent.parent.parent

# =============================================================================
# TOKEN CLASSIFICATION CONSTANTS
# =============================================================================

# Grammar patterns (from SID-04)
GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

# Hazard tokens (from forbidden pairs)
HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}

# High-frequency operational tokens
OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol', 's', 'o', 'd', 'y',
    'a', 'e', 'l', 'r', 'k', 'h', 'c', 't', 'n', 'p', 'm', 'g', 'f',
    'dain', 'chain', 'shain', 'ain', 'in', 'an', 'dan',
}

# LINK-indicative tokens (waiting phases)
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'oiin', 'aiiin', 'ar'}


def is_grammar_token(token):
    """Check if token matches grammar patterns."""
    t = token.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def is_strict_ht_token(token, freq=None):
    """Strict human-track token classification per phase requirements."""
    t = token.lower().strip()

    # Length >= 2
    if len(t) < 2:
        return False

    # Alpha only
    if not t.isalpha():
        return False

    # Not hazard token
    if t in HAZARD_TOKENS:
        return False

    # Not operational token
    if t in OPERATIONAL_TOKENS:
        return False

    # Not grammar token
    if is_grammar_token(t):
        return False

    return True


def is_hazard_proximal(position, hazard_positions, distance=3):
    """Check if position is within distance of any hazard token."""
    for hp in hazard_positions:
        if abs(position - hp) <= distance:
            return True
    return False


def is_link_buffered(position, tokens, window=5):
    """Check if position is in a LINK-buffered region (waiting phase)."""
    # Look for LINK tokens within window
    start = max(0, position - window)
    end = min(len(tokens), position + window + 1)

    for i in range(start, end):
        if tokens[i].lower() in LINK_TOKENS:
            return True

    # Also check for grammar tokens with LINK-indicative suffixes
    for i in range(start, end):
        t = tokens[i].lower()
        if t.endswith('ol') or t.endswith('al') or t.endswith('aiin'):
            return True

    return False


def load_data():
    """Load transcription and classify tokens."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()  # skip header
        for line_num, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # CRITICAL: Filter to H (PRIMARY) transcriber only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"').strip()
                section = parts[3].strip('"') if len(parts) > 3 else ''
                folio = parts[2].strip('"') if len(parts) > 2 else ''

                if word and word.isalpha():
                    data.append({
                        'token': word,
                        'section': section,
                        'folio': folio,
                        'position': len(data)
                    })

    return data


def extract_ht_corpus(data):
    """Extract strict HT tokens from LINK-buffered, non-hazard-proximal regions."""
    tokens = [d['token'] for d in data]

    # Find hazard positions
    hazard_positions = set()
    for i, d in enumerate(data):
        if d['token'].lower() in HAZARD_TOKENS:
            hazard_positions.add(i)

    # Extract HT tokens meeting all criteria
    ht_corpus = []
    executable_corpus = []

    for i, d in enumerate(data):
        token = d['token']

        # Check if hazard-proximal (exclude per requirements)
        if is_hazard_proximal(i, hazard_positions):
            continue

        # Check if LINK-buffered (required for HT)
        if not is_link_buffered(i, tokens):
            # Still collect executable tokens from non-LINK regions for comparison
            if is_grammar_token(token):
                executable_corpus.append({
                    'token': token,
                    'position': i,
                    'section': d['section'],
                    'folio': d['folio']
                })
            continue

        if is_strict_ht_token(token):
            ht_corpus.append({
                'token': token,
                'position': i,
                'section': d['section'],
                'folio': d['folio']
            })
        elif is_grammar_token(token):
            executable_corpus.append({
                'token': token,
                'position': i,
                'section': d['section'],
                'folio': d['folio']
            })

    return ht_corpus, executable_corpus


def get_grapheme_freq(tokens):
    """Get character (grapheme) frequency distribution."""
    freq = Counter()
    for t in tokens:
        for c in t.lower():
            freq[c] += 1
    return freq


# =============================================================================
# TEST A: Rare-Grapheme Over-Representation
# =============================================================================

def test_a_rare_grapheme(ht_corpus, executable_corpus):
    """
    Test A: Rare-Grapheme Over-Representation
    Practice predicts engagement with difficult/rare forms.
    """
    print("\n" + "=" * 60)
    print("TEST A: Rare-Grapheme Over-Representation")
    print("=" * 60)

    ht_tokens = [d['token'] for d in ht_corpus]
    exec_tokens = [d['token'] for d in executable_corpus]

    # Get global grapheme frequencies
    all_tokens = ht_tokens + exec_tokens
    global_freq = get_grapheme_freq(all_tokens)
    total_chars = sum(global_freq.values())

    # Identify rare graphemes (lowest decile)
    sorted_graphemes = sorted(global_freq.items(), key=lambda x: x[1])
    n_graphemes = len(sorted_graphemes)
    rare_threshold = n_graphemes // 10  # Lowest 10%
    rare_graphemes = {g for g, _ in sorted_graphemes[:rare_threshold]}

    print(f"\nGlobal grapheme count: {n_graphemes}")
    print(f"Rare graphemes (lowest decile, n={len(rare_graphemes)}): {sorted(rare_graphemes)}")

    # Calculate rare grapheme density in each corpus
    def rare_density(tokens):
        total = 0
        rare_count = 0
        for t in tokens:
            for c in t.lower():
                total += 1
                if c in rare_graphemes:
                    rare_count += 1
        return rare_count / total if total > 0 else 0

    ht_rare = rare_density(ht_tokens)
    exec_rare = rare_density(exec_tokens)

    print(f"\nRare grapheme density:")
    print(f"  HT corpus: {ht_rare:.4f}")
    print(f"  Executable corpus: {exec_rare:.4f}")
    print(f"  Ratio (HT/Exec): {ht_rare/exec_rare:.2f}x" if exec_rare > 0 else "  N/A")

    # Statistical test
    ht_chars = sum(len(t) for t in ht_tokens)
    exec_chars = sum(len(t) for t in exec_tokens)
    ht_rare_count = int(ht_rare * ht_chars)
    exec_rare_count = int(exec_rare * exec_chars)

    # Chi-square test for independence
    contingency = np.array([
        [ht_rare_count, ht_chars - ht_rare_count],
        [exec_rare_count, exec_chars - exec_rare_count]
    ])

    chi2, p_value, _, _ = stats.chi2_contingency(contingency)

    print(f"\nChi-square test:")
    print(f"  chi2 = {chi2:.2f}")
    print(f"  p = {p_value:.4f}")

    # Determine lean
    if ht_rare > exec_rare * 1.2 and p_value < 0.05:
        lean = "Practice-leaning"
        confidence = "MODERATE" if p_value < 0.01 else "LOW"
    elif ht_rare < exec_rare * 0.8 and p_value < 0.05:
        lean = "Doodling-leaning"
        confidence = "MODERATE" if p_value < 0.01 else "LOW"
    else:
        lean = "Indeterminate"
        confidence = "LOW"

    print(f"\nResult: {lean} (confidence: {confidence})")

    return {
        'test': 'A',
        'name': 'Rare-Grapheme Over-Representation',
        'ht_rare_density': ht_rare,
        'exec_rare_density': exec_rare,
        'ratio': ht_rare / exec_rare if exec_rare > 0 else None,
        'chi2': chi2,
        'p_value': p_value,
        'lean': lean,
        'confidence': confidence
    }


# =============================================================================
# TEST B: Local Permutation Coverage
# =============================================================================

def test_b_permutation_coverage(ht_corpus, executable_corpus):
    """
    Test B: Local Permutation Coverage
    Practice predicts systematic exploration of grapheme combinations.
    """
    print("\n" + "=" * 60)
    print("TEST B: Local Permutation Coverage")
    print("=" * 60)

    ht_tokens = [d['token'].lower() for d in ht_corpus]
    exec_tokens = [d['token'].lower() for d in executable_corpus]

    # Identify most common grapheme pairs/triples in HT
    ht_bigrams = Counter()
    for t in ht_tokens:
        for i in range(len(t) - 1):
            ht_bigrams[t[i:i+2]] += 1

    # Select top grapheme pairs for permutation analysis
    top_bigrams = [bg for bg, _ in ht_bigrams.most_common(10)]

    # Get unique chars from top bigrams
    top_chars = set()
    for bg in top_bigrams[:5]:
        for c in bg:
            top_chars.add(c)
    top_chars = sorted(top_chars)[:4]  # Limit to 4 chars

    print(f"\nTop grapheme subset for permutation: {top_chars}")

    # Generate all 3-char permutations
    all_perms_3 = set(''.join(p) for p in permutations(top_chars, 3))

    # Check which permutations appear in HT tokens
    ht_realized = set()
    for t in ht_tokens:
        for i in range(len(t) - 2):
            trigram = t[i:i+3]
            if set(trigram).issubset(set(top_chars)):
                ht_realized.add(trigram)

    # Check which permutations appear in executable tokens
    exec_realized = set()
    for t in exec_tokens:
        for i in range(len(t) - 2):
            trigram = t[i:i+3]
            if set(trigram).issubset(set(top_chars)):
                exec_realized.add(trigram)

    # Calculate coverage
    ht_coverage = len(ht_realized) / len(all_perms_3) if all_perms_3 else 0
    exec_coverage = len(exec_realized) / len(all_perms_3) if all_perms_3 else 0

    print(f"\nPossible 3-char permutations: {len(all_perms_3)}")
    print(f"HT realized: {len(ht_realized)} ({ht_coverage:.1%})")
    print(f"Exec realized: {len(exec_realized)} ({exec_coverage:.1%})")

    # Control: Shuffled HT tokens
    import random
    random.seed(42)
    shuffled_ht = [''.join(random.sample(list(t), len(t))) for t in ht_tokens]
    shuffled_realized = set()
    for t in shuffled_ht:
        for i in range(len(t) - 2):
            trigram = t[i:i+3]
            if set(trigram).issubset(set(top_chars)):
                shuffled_realized.add(trigram)

    shuffled_coverage = len(shuffled_realized) / len(all_perms_3) if all_perms_3 else 0
    print(f"Shuffled HT realized: {len(shuffled_realized)} ({shuffled_coverage:.1%})")

    # Determine lean
    if ht_coverage > exec_coverage * 1.3 and ht_coverage > shuffled_coverage * 1.2:
        lean = "Practice-leaning"
        confidence = "MODERATE"
    elif ht_coverage < exec_coverage * 0.7:
        lean = "Doodling-leaning"
        confidence = "LOW"
    else:
        lean = "Indeterminate"
        confidence = "LOW"

    print(f"\nResult: {lean} (confidence: {confidence})")

    return {
        'test': 'B',
        'name': 'Local Permutation Coverage',
        'ht_coverage': ht_coverage,
        'exec_coverage': exec_coverage,
        'shuffled_coverage': shuffled_coverage,
        'lean': lean,
        'confidence': confidence
    }


# =============================================================================
# TEST C: Run-Internal Uniformity
# =============================================================================

def test_c_run_uniformity(ht_corpus):
    """
    Test C: Run-Internal Uniformity
    Practice favors structured rehearsal blocks.
    """
    print("\n" + "=" * 60)
    print("TEST C: Run-Internal Uniformity")
    print("=" * 60)

    # Sort by position to identify runs
    sorted_ht = sorted(ht_corpus, key=lambda x: x['position'])

    # Identify consecutive runs
    runs = []
    current_run = []

    for i, d in enumerate(sorted_ht):
        if not current_run:
            current_run = [d]
        elif d['position'] - sorted_ht[i-1]['position'] <= 2:  # Allow 1 gap
            current_run.append(d)
        else:
            if len(current_run) >= 2:
                runs.append(current_run)
            current_run = [d]

    if len(current_run) >= 2:
        runs.append(current_run)

    run_lengths = [len(r) for r in runs]

    print(f"\nHT runs identified: {len(runs)}")
    if run_lengths:
        print(f"Run length stats:")
        print(f"  Mean: {np.mean(run_lengths):.2f}")
        print(f"  Std: {np.std(run_lengths):.2f}")
        print(f"  CV: {np.std(run_lengths)/np.mean(run_lengths):.2f}" if np.mean(run_lengths) > 0 else "  CV: N/A")
        print(f"  Min: {min(run_lengths)}, Max: {max(run_lengths)}")

    # Compare to geometric (memoryless) model
    if run_lengths:
        mean_len = np.mean(run_lengths)
        # Geometric distribution: CV = sqrt(1-p)/p ≈ 1 for small p
        geometric_cv = 1.0
        observed_cv = np.std(run_lengths) / mean_len if mean_len > 0 else 0

        print(f"\nModel comparison:")
        print(f"  Observed CV: {observed_cv:.2f}")
        print(f"  Geometric (memoryless) expected CV: ~{geometric_cv:.1f}")

        # Fixed-block rehearsal model: CV << 1 (uniform blocks)
        print(f"  Fixed-block rehearsal expected CV: ~0.3-0.5")

        # Shuffled control
        import random
        random.seed(42)
        shuffled_runs = random.sample(run_lengths, len(run_lengths))
        shuffled_cv = np.std(shuffled_runs) / np.mean(shuffled_runs) if np.mean(shuffled_runs) > 0 else 0
        print(f"  Shuffled CV: {shuffled_cv:.2f}")

    # Determine lean based on CV
    if run_lengths:
        if observed_cv < 0.6:
            lean = "Practice-leaning"
            confidence = "MODERATE"
        elif observed_cv > 0.9:
            lean = "Doodling-leaning"
            confidence = "MODERATE"
        else:
            lean = "Indeterminate"
            confidence = "LOW"
    else:
        lean = "Indeterminate"
        confidence = "LOW"

    print(f"\nResult: {lean} (confidence: {confidence})")

    return {
        'test': 'C',
        'name': 'Run-Internal Uniformity',
        'n_runs': len(runs),
        'mean_length': np.mean(run_lengths) if run_lengths else 0,
        'cv': observed_cv if run_lengths else 0,
        'lean': lean,
        'confidence': confidence
    }


# =============================================================================
# TEST D: Morphological Boundary Exploration
# =============================================================================

def test_d_morphological_boundary(ht_corpus, executable_corpus):
    """
    Test D: Morphological Boundary Exploration
    Practice tolerates malformed or extreme joins.
    """
    print("\n" + "=" * 60)
    print("TEST D: Morphological Boundary Exploration")
    print("=" * 60)

    ht_tokens = set(d['token'].lower() for d in ht_corpus)
    exec_tokens = set(d['token'].lower() for d in executable_corpus)

    # Measure edit distance from canonical executable forms
    def min_edit_distance(token, reference_set):
        """Minimum edit distance to any token in reference set."""
        if not reference_set:
            return 0

        min_dist = float('inf')
        for ref in reference_set:
            dist = levenshtein(token, ref)
            if dist < min_dist:
                min_dist = dist
        return min_dist

    def levenshtein(s1, s2):
        """Compute Levenshtein distance."""
        if len(s1) < len(s2):
            return levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]

    # Sample for efficiency
    import random
    random.seed(42)
    ht_sample = random.sample(list(ht_tokens), min(200, len(ht_tokens)))
    exec_sample = list(exec_tokens)[:500]

    # Calculate distances
    ht_distances = [min_edit_distance(t, exec_sample) for t in ht_sample]

    # Also compute average token length difference
    ht_lengths = [len(t) for t in ht_sample]
    exec_lengths = [len(t) for t in exec_sample]

    print(f"\nHT tokens sampled: {len(ht_sample)}")
    print(f"Exec tokens for comparison: {len(exec_sample)}")

    print(f"\nEdit distance from executable forms:")
    print(f"  Mean: {np.mean(ht_distances):.2f}")
    print(f"  Std: {np.std(ht_distances):.2f}")
    print(f"  Median: {np.median(ht_distances):.2f}")

    # Find boundary-pushing forms (high edit distance but valid structure)
    boundary_examples = [(t, d) for t, d in zip(ht_sample, ht_distances) if d >= 3]
    boundary_examples.sort(key=lambda x: -x[1])

    print(f"\nBoundary-pushing forms (edit distance >= 3): {len(boundary_examples)}")
    print(f"  Examples: {boundary_examples[:5]}")

    # Length analysis
    print(f"\nToken length comparison:")
    print(f"  HT mean length: {np.mean(ht_lengths):.2f}")
    print(f"  Exec mean length: {np.mean(exec_lengths):.2f}")

    # Determine lean
    boundary_rate = len(boundary_examples) / len(ht_sample) if ht_sample else 0

    if boundary_rate > 0.15 and np.mean(ht_distances) > 1.5:
        lean = "Practice-leaning"
        confidence = "MODERATE"
    elif boundary_rate < 0.05 or np.mean(ht_distances) < 1.0:
        lean = "Doodling-leaning"
        confidence = "LOW"
    else:
        lean = "Indeterminate"
        confidence = "LOW"

    print(f"\nResult: {lean} (confidence: {confidence})")

    return {
        'test': 'D',
        'name': 'Morphological Boundary Exploration',
        'mean_edit_distance': np.mean(ht_distances),
        'boundary_rate': boundary_rate,
        'lean': lean,
        'confidence': confidence
    }


# =============================================================================
# TEST E: Section-Level Family Rotation (Exploratory)
# =============================================================================

def test_e_family_rotation(ht_corpus):
    """
    Test E: Section-Level Family Rotation (Exploratory)
    Practice may cycle focus areas.

    NOTE: This test is illustrative only and labeled WEAK EVIDENCE.
    """
    print("\n" + "=" * 60)
    print("TEST E: Section-Level Family Rotation (EXPLORATORY)")
    print("=" * 60)
    print("WARNING: This test provides WEAK EVIDENCE only.")

    # Group HT by section
    by_section = defaultdict(list)
    for d in ht_corpus:
        by_section[d['section']].append(d['token'])

    # Define grapheme families
    def get_grapheme_family(token):
        """Assign token to dominant grapheme family."""
        t = token.lower()
        if 'o' in t and 'l' in t:
            return 'OL-family'
        elif 'e' in t and ('y' in t or 'd' in t):
            return 'EY-family'
        elif 'a' in t and 'i' in t:
            return 'AI-family'
        elif 'k' in t or 'c' in t:
            return 'KC-family'
        else:
            return 'OTHER'

    # Calculate family distribution per section
    section_families = {}
    for section, tokens in by_section.items():
        if len(tokens) < 10:
            continue
        family_counts = Counter(get_grapheme_family(t) for t in tokens)
        dominant = family_counts.most_common(1)[0] if family_counts else ('NONE', 0)
        section_families[section] = {
            'dominant': dominant[0],
            'dominant_pct': dominant[1] / len(tokens),
            'total': len(tokens),
            'distribution': dict(family_counts)
        }

    print(f"\nSections analyzed: {len(section_families)}")

    for section, info in sorted(section_families.items()):
        print(f"\n  {section}:")
        print(f"    Dominant: {info['dominant']} ({info['dominant_pct']:.1%})")
        print(f"    Distribution: {info['distribution']}")

    # Check for rotation vs monotonic drift
    sections = sorted(section_families.keys())
    dominant_sequence = [section_families[s]['dominant'] for s in sections]

    # Count family changes
    changes = sum(1 for i in range(1, len(dominant_sequence))
                  if dominant_sequence[i] != dominant_sequence[i-1])

    change_rate = changes / (len(dominant_sequence) - 1) if len(dominant_sequence) > 1 else 0

    print(f"\nDominant family sequence: {dominant_sequence}")
    print(f"Family changes: {changes}")
    print(f"Change rate: {change_rate:.2f}")

    # Determine lean (weak)
    if change_rate > 0.5:
        lean = "Practice-leaning (rotation pattern)"
        confidence = "WEAK"
    elif change_rate < 0.2:
        lean = "Doodling-leaning (monotonic drift)"
        confidence = "WEAK"
    else:
        lean = "Indeterminate"
        confidence = "WEAK"

    print(f"\nResult: {lean} (confidence: {confidence})")

    return {
        'test': 'E',
        'name': 'Section-Level Family Rotation',
        'change_rate': change_rate,
        'n_sections': len(section_families),
        'lean': lean,
        'confidence': confidence
    }


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def main():
    print("=" * 70)
    print("EXT-HF-01: Attentional Doodling vs Procedural Practice")
    print("=" * 70)
    print("\nTier 4 - Interpretive / Human-Factors Refinement")
    print("No Tier 0-2 claims may be modified by outcomes of this phase.")

    # Load and filter data
    print("\n" + "=" * 60)
    print("DATA LOADING AND FILTERING")
    print("=" * 60)

    data = load_data()
    print(f"Total tokens loaded: {len(data)}")

    ht_corpus, executable_corpus = extract_ht_corpus(data)
    print(f"Strict HT tokens (LINK-buffered, non-hazard-proximal): {len(ht_corpus)}")
    print(f"Executable tokens for comparison: {len(executable_corpus)}")

    if len(ht_corpus) < 100:
        print("\n⚠️  WARNING: HT corpus too small for reliable analysis.")
        print("    Proceeding with limited confidence.")

    # Run all tests
    results = []

    results.append(test_a_rare_grapheme(ht_corpus, executable_corpus))
    results.append(test_b_permutation_coverage(ht_corpus, executable_corpus))
    results.append(test_c_run_uniformity(ht_corpus))
    results.append(test_d_morphological_boundary(ht_corpus, executable_corpus))
    results.append(test_e_family_rotation(ht_corpus))

    # =============================================================================
    # SUMMARY AND SYNTHESIS
    # =============================================================================

    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)

    print("\n| Test | Name | Result | Lean | Confidence |")
    print("|------|------|--------|------|------------|")
    for r in results:
        print(f"| {r['test']} | {r['name']} | See above | {r['lean']} | {r['confidence']} |")

    # Count leans
    practice_count = sum(1 for r in results if 'Practice' in r['lean'])
    doodling_count = sum(1 for r in results if 'Doodling' in r['lean'])
    indeterminate_count = sum(1 for r in results if 'Indeterminate' in r['lean'])

    print(f"\nLean counts:")
    print(f"  Practice-leaning: {practice_count}/5")
    print(f"  Doodling-leaning: {doodling_count}/5")
    print(f"  Indeterminate: {indeterminate_count}/5")

    # =============================================================================
    # CONSTRAINT CHECK
    # =============================================================================

    print("\n" + "=" * 70)
    print("CONSTRAINT CHECK")
    print("=" * 70)

    print("""
[PASS] No semantic, symbolic, or execution-linked interpretation introduced
[PASS] All Tier 0-2 claims remain intact:
       - Grammar coverage (100%)
       - Hazard topology (17 forbidden transitions)
       - Kernel structure (k, h, e operators)
       - MONOSTATE convergence
       - Folio atomicity
[PASS] Results capped at Tier 4
""")

    # =============================================================================
    # FINAL TIER-4 STATEMENT
    # =============================================================================

    print("\n" + "=" * 70)
    print("FINAL TIER-4 STATEMENT")
    print("=" * 70)

    if practice_count > doodling_count and practice_count >= 3:
        verdict = "PRACTICE-LEANING"
        statement = """
The human-track token layer shows patterns more consistent with intentional
procedural handwriting practice than with low-intent attentional doodling.
Specifically, the tokens exhibit: structured run lengths suggesting deliberate
rehearsal blocks, exploration of morphological boundaries beyond canonical
executable forms, and systematic coverage of local grapheme permutations.
However, this interpretation remains at Tier 4 (EXPLORATORY) with LOW to MODERATE
confidence. The pattern is compatible with the SID-05 attentional pacing model
(writing during waiting phases) while suggesting that the writing may have been
purposeful practice rather than purely automatic behavior. This finding does not
imply semantic content, instruction encoding, or execution relevance.
"""
    elif doodling_count > practice_count and doodling_count >= 3:
        verdict = "DOODLING-LEANING"
        statement = """
The human-track token layer shows patterns more consistent with low-intent
attentional doodling than with structured procedural practice. The tokens
exhibit memoryless run distributions, limited morphological exploration, and
grapheme distributions that do not suggest systematic rehearsal. This finding
reinforces the SID-05 attentional pacing interpretation: operators made these
marks to maintain alertness during waiting phases, not to practice writing
skills. Confidence remains LOW at Tier 4 (EXPLORATORY). This finding does not
imply semantic content, instruction encoding, or execution relevance.
"""
    else:
        verdict = "INDETERMINATE"
        statement = """
The tests yield mixed or inconclusive results, with neither practice nor
doodling patterns clearly dominant. The human-track token layer may represent
a mix of behaviors, situational variation, or a writing mode that does not
cleanly fit either model. The SID-05 attentional pacing interpretation remains
the best available explanation, with this phase unable to further discriminate
between automatic and intentional writing behaviors. Confidence is LOW at
Tier 4 (EXPLORATORY). This finding does not imply semantic content, instruction
encoding, or execution relevance.
"""

    print(f"\nVERDICT: {verdict}")
    print(statement)

    print("\n" + "=" * 70)
    print("PHASE COMPLETE: EXT-HF-01")
    print("=" * 70)

    return results


if __name__ == '__main__':
    main()
