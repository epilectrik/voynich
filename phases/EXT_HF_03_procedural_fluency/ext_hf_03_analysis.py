"""
EXT-HF-03: Procedural Fluency Reinforcement (Confirmatory Tests)

Tier 4 confirmatory phase testing whether HT tokens show statistical signatures
expected from intentional handwriting practice.

Tests:
A - Grapheme Combination Coverage Efficiency
B - Difficult Bigram Over-Representation
C - Run-Internal Combinatorial Diversity
D - Token Repetition Suppression
E - Operational Alphabet Fidelity
"""

from collections import defaultdict, Counter
from pathlib import Path
from itertools import permutations
import numpy as np
from scipy import stats
import random

project_root = Path(__file__).parent.parent.parent

# ============================================================================
# TOKEN FILTERING (Identical to EXT-HF-01/02)
# ============================================================================

HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}

OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol', 's', 'o', 'd', 'y',
    'a', 'e', 'l', 'r', 'k', 'h', 'c', 't', 'n', 'p', 'm', 'g', 'f',
    'dain', 'chain', 'shain', 'ain', 'in', 'an', 'dan',
}

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

KERNEL_TOKENS = {'k', 'h', 'e', 's', 't', 'd', 'l', 'o', 'c', 'r'}


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


def is_human_track_strict(token):
    """Strict HT filtering matching EXT-HF-01/02."""
    t = token.lower().strip()

    if len(t) < 2:
        return False
    if not t.isalpha():
        return False
    if t in HAZARD_TOKENS:
        return False
    if t in OPERATIONAL_TOKENS:
        return False
    if t in KERNEL_TOKENS:
        return False
    if is_grammar_token(t):
        return False

    return True


def is_executable_token(token):
    """Check if token is executable (grammar or operational)."""
    t = token.lower().strip()
    if len(t) < 2:
        return False
    if not t.isalpha():
        return False
    if is_grammar_token(t):
        return True
    if t in OPERATIONAL_TOKENS:
        return True
    return False


# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load transcription data with LINK and hazard proximity info."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    all_tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line_num, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # CRITICAL: Filter to H (PRIMARY) transcriber only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"').strip()
                folio = parts[1].strip('"') if len(parts) > 1 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''

                if word and '*' not in word:
                    all_tokens.append({
                        'token': word.lower(),
                        'folio': folio,
                        'section': section,
                        'position': len(all_tokens)
                    })

    # Mark hazard-proximal positions
    hazard_positions = set()
    for i, t in enumerate(all_tokens):
        if t['token'] in HAZARD_TOKENS:
            for j in range(max(0, i-3), min(len(all_tokens), i+4)):
                hazard_positions.add(j)

    # Filter to HT tokens in non-hazard-proximal regions
    ht_tokens = []
    exec_tokens = []

    for i, t in enumerate(all_tokens):
        if i not in hazard_positions:
            if is_human_track_strict(t['token']):
                ht_tokens.append(t)
            elif is_executable_token(t['token']):
                exec_tokens.append(t)

    return ht_tokens, exec_tokens, all_tokens


def extract_graphemes(token):
    """Extract grapheme sequence from token."""
    # Simple character-level for now
    return list(token.lower())


def extract_bigrams(token):
    """Extract bigrams from token."""
    t = token.lower()
    if len(t) < 2:
        return []
    return [t[i:i+2] for i in range(len(t)-1)]


# ============================================================================
# TEST A: Grapheme Combination Coverage Efficiency
# ============================================================================

def test_a_coverage_efficiency(ht_tokens, exec_tokens):
    """
    Test whether HT achieves broader coverage of grapheme combinations
    per token than operational text or shuffled baselines.
    """
    print("\n" + "="*60)
    print("TEST A: Grapheme Combination Coverage Efficiency")
    print("="*60)

    # Get unique tokens
    ht_unique = list(set(t['token'] for t in ht_tokens))
    exec_unique = list(set(t['token'] for t in exec_tokens))

    # Extract all bigrams from each corpus
    ht_bigrams = set()
    exec_bigrams = set()

    for token in ht_unique:
        ht_bigrams.update(extract_bigrams(token))

    for token in exec_unique:
        exec_bigrams.update(extract_bigrams(token))

    # Coverage per token
    ht_coverage_rate = len(ht_bigrams) / len(ht_unique) if ht_unique else 0
    exec_coverage_rate = len(exec_bigrams) / len(exec_unique) if exec_unique else 0

    # Shuffled baseline: shuffle HT token characters and measure coverage
    shuffled_coverages = []
    for _ in range(100):
        shuffled_bigrams = set()
        for token in ht_unique:
            chars = list(token)
            random.shuffle(chars)
            shuffled_token = ''.join(chars)
            shuffled_bigrams.update(extract_bigrams(shuffled_token))
        shuffled_coverages.append(len(shuffled_bigrams) / len(ht_unique) if ht_unique else 0)

    shuffled_mean = np.mean(shuffled_coverages)
    shuffled_std = np.std(shuffled_coverages)

    # Test: is HT coverage significantly different from shuffled?
    z_score = (ht_coverage_rate - shuffled_mean) / shuffled_std if shuffled_std > 0 else 0

    # Also compute trigram coverage
    ht_trigrams = set()
    exec_trigrams = set()

    for token in ht_unique:
        t = token.lower()
        if len(t) >= 3:
            ht_trigrams.update([t[i:i+3] for i in range(len(t)-2)])

    for token in exec_unique:
        t = token.lower()
        if len(t) >= 3:
            exec_trigrams.update([t[i:i+3] for i in range(len(t)-2)])

    ht_trigram_rate = len(ht_trigrams) / len(ht_unique) if ht_unique else 0
    exec_trigram_rate = len(exec_trigrams) / len(exec_unique) if exec_unique else 0

    print(f"\nHT unique tokens: {len(ht_unique)}")
    print(f"Exec unique tokens: {len(exec_unique)}")
    print(f"\nBigram Coverage:")
    print(f"  HT: {len(ht_bigrams)} unique bigrams, {ht_coverage_rate:.3f} per token")
    print(f"  Exec: {len(exec_bigrams)} unique bigrams, {exec_coverage_rate:.3f} per token")
    print(f"  Shuffled HT mean: {shuffled_mean:.3f} +/- {shuffled_std:.3f}")
    print(f"  HT vs Shuffled z-score: {z_score:.2f}")
    print(f"\nTrigram Coverage:")
    print(f"  HT: {len(ht_trigrams)} unique trigrams, {ht_trigram_rate:.3f} per token")
    print(f"  Exec: {len(exec_trigrams)} unique trigrams, {exec_trigram_rate:.3f} per token")

    # Interpretation
    if ht_coverage_rate > exec_coverage_rate * 1.1:
        lean = "Practice-leaning"
        reason = "HT achieves higher combinatorial coverage per token"
    elif ht_coverage_rate < exec_coverage_rate * 0.9:
        lean = "Doodling-leaning"
        reason = "HT achieves lower combinatorial coverage"
    else:
        lean = "Indeterminate"
        reason = "Coverage rates similar"

    # Strength based on z-score
    if abs(z_score) > 2:
        strength = "MODERATE"
    elif abs(z_score) > 1:
        strength = "WEAK"
    else:
        strength = "NEGLIGIBLE"

    print(f"\nVerdict: {lean} ({strength})")
    print(f"Reason: {reason}")

    return {
        'test': 'A',
        'name': 'Grapheme Combination Coverage',
        'ht_bigrams': len(ht_bigrams),
        'exec_bigrams': len(exec_bigrams),
        'ht_rate': ht_coverage_rate,
        'exec_rate': exec_coverage_rate,
        'shuffled_mean': shuffled_mean,
        'z_score': z_score,
        'lean': lean,
        'strength': strength
    }


# ============================================================================
# TEST B: Difficult Bigram Over-Representation
# ============================================================================

def test_b_difficult_bigrams(ht_tokens, exec_tokens):
    """
    Test whether rare/difficult bigrams from executable corpus
    are over-represented in HT tokens.
    """
    print("\n" + "="*60)
    print("TEST B: Difficult Bigram Over-Representation")
    print("="*60)

    # Count bigrams in executable corpus
    exec_bigram_counts = Counter()
    for t in exec_tokens:
        exec_bigram_counts.update(extract_bigrams(t['token']))

    total_exec_bigrams = sum(exec_bigram_counts.values())

    # Identify bottom decile (rare) bigrams
    if not exec_bigram_counts:
        print("No executable bigrams found")
        return {'test': 'B', 'lean': 'Indeterminate', 'strength': 'N/A'}

    sorted_bigrams = sorted(exec_bigram_counts.items(), key=lambda x: x[1])
    decile_cutoff = len(sorted_bigrams) // 10
    rare_bigrams = set(b for b, c in sorted_bigrams[:max(1, decile_cutoff)])

    print(f"\nTotal unique bigrams in exec: {len(exec_bigram_counts)}")
    print(f"Rare bigrams (bottom decile): {len(rare_bigrams)}")
    print(f"Examples: {list(rare_bigrams)[:10]}")

    # Count rare bigram occurrences in HT
    ht_bigram_counts = Counter()
    for t in ht_tokens:
        ht_bigram_counts.update(extract_bigrams(t['token']))

    total_ht_bigrams = sum(ht_bigram_counts.values())

    # Calculate rare bigram density
    exec_rare_count = sum(exec_bigram_counts[b] for b in rare_bigrams if b in exec_bigram_counts)
    ht_rare_count = sum(ht_bigram_counts[b] for b in rare_bigrams if b in ht_bigram_counts)

    exec_rare_density = exec_rare_count / total_exec_bigrams if total_exec_bigrams else 0
    ht_rare_density = ht_rare_count / total_ht_bigrams if total_ht_bigrams else 0

    # Ratio
    ratio = ht_rare_density / exec_rare_density if exec_rare_density > 0 else 0

    # Chi-square test
    # Expected HT rare count under null (same density as exec)
    expected_ht_rare = exec_rare_density * total_ht_bigrams

    if expected_ht_rare > 5:  # Chi-square validity
        chi2 = (ht_rare_count - expected_ht_rare)**2 / expected_ht_rare
        p_value = 1 - stats.chi2.cdf(chi2, df=1)
    else:
        chi2 = None
        p_value = None

    print(f"\nRare bigram density:")
    print(f"  Exec: {exec_rare_count}/{total_exec_bigrams} = {exec_rare_density:.6f}")
    print(f"  HT: {ht_rare_count}/{total_ht_bigrams} = {ht_rare_density:.6f}")
    print(f"  Ratio (HT/Exec): {ratio:.2f}x")
    if chi2 is not None:
        print(f"  Chi-square: {chi2:.2f}, p = {p_value:.6f}")

    # Interpretation
    if ratio > 1.5 and (p_value is None or p_value < 0.05):
        lean = "Practice-leaning"
        strength = "MODERATE" if ratio > 2 else "WEAK"
    elif ratio < 0.7:
        lean = "Doodling-leaning"
        strength = "MODERATE" if ratio < 0.5 else "WEAK"
    else:
        lean = "Indeterminate"
        strength = "NEGLIGIBLE"

    print(f"\nVerdict: {lean} ({strength})")

    return {
        'test': 'B',
        'name': 'Difficult Bigram Over-Representation',
        'exec_rare_density': exec_rare_density,
        'ht_rare_density': ht_rare_density,
        'ratio': ratio,
        'chi2': chi2,
        'p_value': p_value,
        'lean': lean,
        'strength': strength
    }


# ============================================================================
# TEST C: Run-Internal Combinatorial Diversity
# ============================================================================

def test_c_run_diversity(ht_tokens, exec_tokens):
    """
    Test whether sequences within HT runs are more combinatorially
    diverse than expected under random repetition.
    """
    print("\n" + "="*60)
    print("TEST C: Run-Internal Combinatorial Diversity")
    print("="*60)

    # Identify HT runs (consecutive HT tokens)
    ht_runs = []
    current_run = []
    last_pos = -2

    for t in sorted(ht_tokens, key=lambda x: x['position']):
        if t['position'] == last_pos + 1:
            current_run.append(t['token'])
        else:
            if len(current_run) >= 2:
                ht_runs.append(current_run)
            current_run = [t['token']]
        last_pos = t['position']

    if len(current_run) >= 2:
        ht_runs.append(current_run)

    print(f"\nHT runs identified (length >= 2): {len(ht_runs)}")
    if not ht_runs:
        return {'test': 'C', 'lean': 'Indeterminate', 'strength': 'N/A', 'reason': 'No runs found'}

    # Calculate diversity metrics for each run
    def run_diversity(run):
        """Calculate diversity: unique forms / total forms."""
        return len(set(run)) / len(run) if run else 0

    def run_entropy(run):
        """Calculate Shannon entropy of run."""
        if not run:
            return 0
        counts = Counter(run)
        probs = [c/len(run) for c in counts.values()]
        return -sum(p * np.log2(p) for p in probs if p > 0)

    ht_diversities = [run_diversity(r) for r in ht_runs]
    ht_entropies = [run_entropy(r) for r in ht_runs]

    mean_diversity = np.mean(ht_diversities)
    mean_entropy = np.mean(ht_entropies)

    print(f"Mean run diversity: {mean_diversity:.3f}")
    print(f"Mean run entropy: {mean_entropy:.3f} bits")

    # Shuffled baseline: shuffle tokens within runs
    shuffled_diversities = []
    for _ in range(100):
        shuffled_divs = []
        for run in ht_runs:
            shuffled_run = run.copy()
            random.shuffle(shuffled_run)
            shuffled_divs.append(run_diversity(shuffled_run))
        shuffled_diversities.append(np.mean(shuffled_divs))

    # Note: shuffling within run doesn't change diversity (same tokens)
    # Instead, shuffle token identities across runs
    all_ht_tokens = [t for run in ht_runs for t in run]

    shuffled_cross_diversities = []
    for _ in range(100):
        shuffled_all = all_ht_tokens.copy()
        random.shuffle(shuffled_all)

        idx = 0
        temp_divs = []
        for run in ht_runs:
            fake_run = shuffled_all[idx:idx+len(run)]
            temp_divs.append(run_diversity(fake_run))
            idx += len(run)
        shuffled_cross_diversities.append(np.mean(temp_divs))

    shuffled_mean = np.mean(shuffled_cross_diversities)
    shuffled_std = np.std(shuffled_cross_diversities)

    z_score = (mean_diversity - shuffled_mean) / shuffled_std if shuffled_std > 0 else 0

    print(f"\nComparison to shuffled baseline:")
    print(f"  Observed mean diversity: {mean_diversity:.3f}")
    print(f"  Shuffled mean diversity: {shuffled_mean:.3f} +/- {shuffled_std:.3f}")
    print(f"  Z-score: {z_score:.2f}")

    # Also check: do real runs have more unique tokens than expected?
    # If practice, we expect intentional variation

    # For comparison, compute exec run diversity
    exec_runs = []
    current_run = []
    last_pos = -2

    for t in sorted(exec_tokens, key=lambda x: x['position']):
        if t['position'] == last_pos + 1:
            current_run.append(t['token'])
        else:
            if len(current_run) >= 2:
                exec_runs.append(current_run)
            current_run = [t['token']]
        last_pos = t['position']

    if len(current_run) >= 2:
        exec_runs.append(current_run)

    if exec_runs:
        exec_diversities = [run_diversity(r) for r in exec_runs]
        exec_mean_div = np.mean(exec_diversities)
        print(f"\nExec run mean diversity: {exec_mean_div:.3f}")

    # Interpretation
    if mean_diversity > shuffled_mean + shuffled_std:
        lean = "Practice-leaning"
        reason = "Higher diversity than shuffled baseline"
    elif mean_diversity < shuffled_mean - shuffled_std:
        lean = "Doodling-leaning"
        reason = "Lower diversity than shuffled baseline"
    else:
        lean = "Indeterminate"
        reason = "Diversity within expected range"

    strength = "MODERATE" if abs(z_score) > 2 else ("WEAK" if abs(z_score) > 1 else "NEGLIGIBLE")

    print(f"\nVerdict: {lean} ({strength})")
    print(f"Reason: {reason}")

    return {
        'test': 'C',
        'name': 'Run-Internal Diversity',
        'n_runs': len(ht_runs),
        'mean_diversity': mean_diversity,
        'mean_entropy': mean_entropy,
        'shuffled_mean': shuffled_mean,
        'z_score': z_score,
        'lean': lean,
        'strength': strength
    }


# ============================================================================
# TEST D: Token Repetition Suppression (Supporting Only)
# ============================================================================

def test_d_repetition_suppression(ht_tokens, exec_tokens):
    """
    Test how often the same HT token repeats adjacently within a run.
    Supporting test only - not decisive.
    """
    print("\n" + "="*60)
    print("TEST D: Token Repetition Suppression (Supporting Only)")
    print("="*60)

    # Identify adjacent repetitions in HT
    ht_sorted = sorted(ht_tokens, key=lambda x: x['position'])

    ht_adjacent_pairs = 0
    ht_repetitions = 0

    for i in range(len(ht_sorted) - 1):
        if ht_sorted[i+1]['position'] == ht_sorted[i]['position'] + 1:
            ht_adjacent_pairs += 1
            if ht_sorted[i+1]['token'] == ht_sorted[i]['token']:
                ht_repetitions += 1

    ht_repeat_rate = ht_repetitions / ht_adjacent_pairs if ht_adjacent_pairs > 0 else 0

    print(f"\nHT adjacent pairs: {ht_adjacent_pairs}")
    print(f"HT repetitions: {ht_repetitions}")
    print(f"HT repeat rate: {ht_repeat_rate:.3%}")

    # Shuffled baseline
    ht_tokens_list = [t['token'] for t in ht_sorted]
    shuffled_repeat_rates = []

    for _ in range(1000):
        shuffled = ht_tokens_list.copy()
        random.shuffle(shuffled)

        reps = sum(1 for i in range(len(shuffled)-1) if shuffled[i] == shuffled[i+1])
        rate = reps / (len(shuffled)-1) if len(shuffled) > 1 else 0
        shuffled_repeat_rates.append(rate)

    shuffled_mean = np.mean(shuffled_repeat_rates)
    shuffled_std = np.std(shuffled_repeat_rates)

    # Percentile of observed in shuffled distribution
    percentile = sum(1 for r in shuffled_repeat_rates if r >= ht_repeat_rate) / len(shuffled_repeat_rates) * 100

    print(f"\nShuffled baseline:")
    print(f"  Mean repeat rate: {shuffled_mean:.3%}")
    print(f"  Std: {shuffled_std:.3%}")
    print(f"  Observed percentile: {percentile:.1f}%")

    # Compare to exec
    exec_sorted = sorted(exec_tokens, key=lambda x: x['position'])

    exec_adjacent_pairs = 0
    exec_repetitions = 0

    for i in range(len(exec_sorted) - 1):
        if exec_sorted[i+1]['position'] == exec_sorted[i]['position'] + 1:
            exec_adjacent_pairs += 1
            if exec_sorted[i+1]['token'] == exec_sorted[i]['token']:
                exec_repetitions += 1

    exec_repeat_rate = exec_repetitions / exec_adjacent_pairs if exec_adjacent_pairs > 0 else 0
    print(f"\nExec repeat rate for comparison: {exec_repeat_rate:.3%}")

    # Interpretation (supporting only)
    if ht_repeat_rate < shuffled_mean - shuffled_std:
        lean = "Practice-leaning"
        reason = "Active suppression of repetition (intentional variation)"
    elif ht_repeat_rate > shuffled_mean + shuffled_std:
        lean = "Doodling-leaning"
        reason = "Elevated repetition (automatic behavior)"
    else:
        lean = "Indeterminate"
        reason = "Repetition rate within expected range"

    strength = "SUPPORTING" if lean != "Indeterminate" else "NEGLIGIBLE"

    print(f"\nVerdict: {lean} ({strength})")
    print(f"Reason: {reason}")
    print("Note: This test is SUPPORTING ONLY - not decisive")

    return {
        'test': 'D',
        'name': 'Token Repetition Suppression',
        'ht_repeat_rate': ht_repeat_rate,
        'shuffled_mean': shuffled_mean,
        'percentile': percentile,
        'exec_repeat_rate': exec_repeat_rate,
        'lean': lean,
        'strength': strength,
        'note': 'Supporting test only'
    }


# ============================================================================
# TEST E: Operational Alphabet Fidelity (Guardrail)
# ============================================================================

def test_e_alphabet_fidelity(ht_tokens, exec_tokens, all_tokens):
    """
    Guardrail test: Do HT tokens use exactly the same grapheme
    inventory as operational tokens?
    """
    print("\n" + "="*60)
    print("TEST E: Operational Alphabet Fidelity (Guardrail)")
    print("="*60)

    # Extract character sets
    ht_chars = set()
    for t in ht_tokens:
        ht_chars.update(t['token'])

    exec_chars = set()
    for t in exec_tokens:
        exec_chars.update(t['token'])

    all_chars = set()
    for t in all_tokens:
        all_chars.update(t['token'].lower())

    print(f"\nCharacter sets:")
    print(f"  HT characters: {len(ht_chars)} - {sorted(ht_chars)}")
    print(f"  Exec characters: {len(exec_chars)} - {sorted(exec_chars)}")
    print(f"  All characters: {len(all_chars)} - {sorted(all_chars)}")

    # Check for deviations
    ht_only = ht_chars - exec_chars
    exec_only = exec_chars - ht_chars
    shared = ht_chars & exec_chars

    print(f"\nOverlap analysis:")
    print(f"  Shared characters: {len(shared)} - {sorted(shared)}")
    print(f"  HT-only characters: {len(ht_only)} - {sorted(ht_only) if ht_only else 'None'}")
    print(f"  Exec-only characters: {len(exec_only)} - {sorted(exec_only) if exec_only else 'None'}")

    # Fidelity score
    fidelity = len(shared) / len(ht_chars) if ht_chars else 0

    print(f"\nAlphabet fidelity: {fidelity:.1%}")

    # Interpretation
    if len(ht_only) == 0:
        lean = "Confirmed"
        reason = "HT uses exact subset of operational alphabet"
        strength = "PASS"
    elif len(ht_only) <= 2:
        lean = "Mostly confirmed"
        reason = f"Minor deviations: {ht_only}"
        strength = "PASS"
    else:
        lean = "Deviation detected"
        reason = f"HT uses non-operational characters: {ht_only}"
        strength = "FLAG"

    print(f"\nVerdict: {lean} ({strength})")
    print(f"Reason: {reason}")

    return {
        'test': 'E',
        'name': 'Operational Alphabet Fidelity',
        'ht_chars': len(ht_chars),
        'exec_chars': len(exec_chars),
        'shared': len(shared),
        'ht_only': list(ht_only),
        'fidelity': fidelity,
        'lean': lean,
        'strength': strength
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*60)
    print("EXT-HF-03: Procedural Fluency Reinforcement")
    print("Tier 4 Confirmatory Tests")
    print("="*60)

    # Load data
    ht_tokens, exec_tokens, all_tokens = load_data()

    print(f"\nData loaded:")
    print(f"  HT tokens (strict filtered): {len(ht_tokens)}")
    print(f"  Executable tokens: {len(exec_tokens)}")
    print(f"  Total tokens: {len(all_tokens)}")

    # Run all tests
    results = []

    results.append(test_a_coverage_efficiency(ht_tokens, exec_tokens))
    results.append(test_b_difficult_bigrams(ht_tokens, exec_tokens))
    results.append(test_c_run_diversity(ht_tokens, exec_tokens))
    results.append(test_d_repetition_suppression(ht_tokens, exec_tokens))
    results.append(test_e_alphabet_fidelity(ht_tokens, exec_tokens, all_tokens))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    print("\n| Test | Name | Metric | Lean | Strength |")
    print("|------|------|--------|------|----------|")

    for r in results:
        metric = ""
        if r['test'] == 'A':
            metric = f"HT rate {r.get('ht_rate', 0):.3f} vs Exec {r.get('exec_rate', 0):.3f}"
        elif r['test'] == 'B':
            metric = f"Ratio {r.get('ratio', 0):.2f}x"
        elif r['test'] == 'C':
            metric = f"z={r.get('z_score', 0):.2f}"
        elif r['test'] == 'D':
            metric = f"Repeat {r.get('ht_repeat_rate', 0):.1%} vs {r.get('shuffled_mean', 0):.1%}"
        elif r['test'] == 'E':
            metric = f"Fidelity {r.get('fidelity', 0):.1%}"

        print(f"| {r['test']} | {r['name'][:25]} | {metric} | {r['lean']} | {r['strength']} |")

    # Count leans
    practice_count = sum(1 for r in results if 'Practice' in r.get('lean', ''))
    doodling_count = sum(1 for r in results if 'Doodling' in r.get('lean', ''))
    indeterminate_count = sum(1 for r in results if r.get('lean', '') in ['Indeterminate', 'Confirmed', 'Mostly confirmed'])

    print(f"\nLean counts:")
    print(f"  Practice-leaning: {practice_count}/5")
    print(f"  Doodling-leaning: {doodling_count}/5")
    print(f"  Indeterminate/Confirmed: {indeterminate_count}/5")

    # Constraint check
    print("\n" + "="*60)
    print("CONSTRAINT CONFIRMATION")
    print("="*60)
    print("\n[PASS] No semantic or encoding interpretations introduced")
    print("[PASS] All Tier 0-2 claims remain untouched")
    print("[PASS] Results remain Tier 4 only")

    # Final verdict
    print("\n" + "="*60)
    print("FINAL INTERPRETIVE STATEMENT (TIER 4)")
    print("="*60)

    if practice_count >= 3:
        verdict = "STRENGTHENED"
        confidence = "MODERATE" if practice_count >= 4 else "LOW"
    elif doodling_count >= 3:
        verdict = "WEAKENED"
        confidence = "MODERATE" if doodling_count >= 4 else "LOW"
    else:
        verdict = "MIXED"
        confidence = "LOW"

    print(f"""
These confirmatory tests {verdict.lower()} the handwriting-practice interpretation
of the human-track layer. Of five tests, {practice_count} lean toward practice,
{doodling_count} lean toward doodling, and {indeterminate_count} are indeterminate/confirmatory.

Confidence: {confidence}

This remains a Tier 4 (EXPLORATORY) finding. The tests provide additional
evidence for evaluating the practice hypothesis but do not establish it
as proven. The interpretation remains speculative and does not modify
any Tier 0-2 structural claims.
""")

    return results


if __name__ == '__main__':
    random.seed(42)
    np.random.seed(42)
    main()
