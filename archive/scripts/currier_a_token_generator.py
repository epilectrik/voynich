"""
Currier A Token Generator Model (Target 1)

Tests hypothesis: P(token) = P(PREFIX) * P(MIDDLE|PREFIX) * P(SUFFIX|PREFIX,MIDDLE)

Success criteria:
- Type coverage >90% of observed
- Token coverage >85%
- Perplexity < 30% of uniform baseline
"""

import json
import math
import random
from collections import defaultdict, Counter
from pathlib import Path

# Known prefixes and suffixes
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in',
            'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy',
            'r', 'l', 's', 'd', 'n', 'm']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)


def load_modeling_data():
    """Load prepared modeling data."""
    filepath = Path(__file__).parent.parent.parent / 'results' / 'currier_a_modeling_data.json'
    with open(filepath, 'r') as f:
        return json.load(f)


def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix


def load_currier_a_tokens():
    """Load all Currier A tokens."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()
                    if token:
                        tokens.append(token)
    return tokens


def build_probability_tables(tokens):
    """Build factored probability tables from observed tokens."""
    # Decompose all tokens
    decomposed = []
    for t in tokens:
        prefix, middle, suffix = decompose_token(t)
        if prefix:
            decomposed.append({
                'token': t,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix
            })

    total = len(decomposed)
    print(f"Building probability tables from {total} decomposed tokens")

    # P(PREFIX)
    prefix_counts = Counter(d['prefix'] for d in decomposed)
    p_prefix = {p: c/total for p, c in prefix_counts.items()}

    # P(MIDDLE|PREFIX)
    middle_given_prefix = defaultdict(Counter)
    for d in decomposed:
        middle_given_prefix[d['prefix']][d['middle']] += 1

    p_middle_given_prefix = {}
    for prefix, middles in middle_given_prefix.items():
        total_p = sum(middles.values())
        p_middle_given_prefix[prefix] = {m: c/total_p for m, c in middles.items()}

    # P(SUFFIX|PREFIX,MIDDLE)
    suffix_given_pm = defaultdict(Counter)
    for d in decomposed:
        key = (d['prefix'], d['middle'])
        suffix_given_pm[key][d['suffix']] += 1

    p_suffix_given_pm = {}
    for (prefix, middle), suffixes in suffix_given_pm.items():
        total_pm = sum(suffixes.values())
        key = f"{prefix}|{middle}"
        p_suffix_given_pm[key] = {s: c/total_pm for s, c in suffixes.items()}

    return p_prefix, p_middle_given_prefix, p_suffix_given_pm, decomposed


def sample_from_dist(prob_dict):
    """Sample from a probability distribution."""
    items = list(prob_dict.keys())
    probs = list(prob_dict.values())
    return random.choices(items, weights=probs, k=1)[0]


def generate_token(p_prefix, p_middle_given_prefix, p_suffix_given_pm):
    """Generate a single token from the factored model."""
    # Sample prefix
    prefix = sample_from_dist(p_prefix)

    # Sample middle given prefix
    if prefix in p_middle_given_prefix:
        middle = sample_from_dist(p_middle_given_prefix[prefix])
    else:
        middle = ''

    # Sample suffix given prefix and middle
    key = f"{prefix}|{middle}"
    if key in p_suffix_given_pm:
        suffix = sample_from_dist(p_suffix_given_pm[key])
    else:
        # Fallback: uniform over observed suffixes for this prefix
        all_suffixes = set()
        for k, v in p_suffix_given_pm.items():
            if k.startswith(f"{prefix}|"):
                all_suffixes.update(v.keys())
        if all_suffixes:
            suffix = random.choice(list(all_suffixes))
        else:
            suffix = 'y'  # Most common suffix as fallback

    return prefix + middle + suffix


def calculate_log_probability(token, p_prefix, p_middle_given_prefix, p_suffix_given_pm):
    """Calculate log probability of a token under the model."""
    prefix, middle, suffix = decompose_token(token)
    if not prefix:
        return float('-inf')

    # P(PREFIX)
    if prefix not in p_prefix:
        return float('-inf')
    log_p = math.log(p_prefix[prefix])

    # P(MIDDLE|PREFIX)
    if prefix in p_middle_given_prefix and middle in p_middle_given_prefix[prefix]:
        log_p += math.log(p_middle_given_prefix[prefix][middle])
    else:
        # Smoothing: assign small probability to unseen middles
        log_p += math.log(0.001)

    # P(SUFFIX|PREFIX,MIDDLE)
    key = f"{prefix}|{middle}"
    if key in p_suffix_given_pm and suffix in p_suffix_given_pm[key]:
        log_p += math.log(p_suffix_given_pm[key][suffix])
    else:
        # Smoothing
        log_p += math.log(0.001)

    return log_p


def evaluate_generator(tokens, decomposed, p_prefix, p_middle_given_prefix, p_suffix_given_pm):
    """Evaluate the generator against success criteria."""
    print("\n" + "=" * 60)
    print("EVALUATION")
    print("=" * 60)

    # Get observed types and token counts
    observed_types = set(d['token'] for d in decomposed)
    observed_tokens = [d['token'] for d in decomposed]
    token_counts = Counter(observed_tokens)

    # Generate samples
    n_samples = len(observed_tokens)
    generated = [generate_token(p_prefix, p_middle_given_prefix, p_suffix_given_pm)
                 for _ in range(n_samples)]
    generated_types = set(generated)

    # Metric 1: Type coverage
    type_overlap = observed_types & generated_types
    type_coverage = len(type_overlap) / len(observed_types)
    print(f"\n1. TYPE COVERAGE")
    print(f"   Observed types: {len(observed_types)}")
    print(f"   Generated types: {len(generated_types)}")
    print(f"   Overlap: {len(type_overlap)}")
    print(f"   Coverage: {100*type_coverage:.1f}%")
    print(f"   Target: >90% | {'PASS' if type_coverage > 0.9 else 'FAIL'}")

    # Novel types (generated but not observed)
    novel_types = generated_types - observed_types
    print(f"   Novel types: {len(novel_types)} ({100*len(novel_types)/len(generated_types):.1f}%)")

    # Metric 2: Token coverage (by frequency)
    covered_tokens = sum(token_counts[t] for t in type_overlap)
    total_tokens = sum(token_counts.values())
    token_coverage = covered_tokens / total_tokens
    print(f"\n2. TOKEN COVERAGE (weighted by frequency)")
    print(f"   Total tokens: {total_tokens}")
    print(f"   Covered: {covered_tokens}")
    print(f"   Coverage: {100*token_coverage:.1f}%")
    print(f"   Target: >85% | {'PASS' if token_coverage > 0.85 else 'FAIL'}")

    # Metric 3: Perplexity
    # Calculate perplexity of observed tokens under the model
    log_probs = []
    for token in observed_tokens[:5000]:  # Sample for efficiency
        lp = calculate_log_probability(token, p_prefix, p_middle_given_prefix, p_suffix_given_pm)
        if lp > float('-inf'):
            log_probs.append(lp)

    if log_probs:
        avg_log_prob = sum(log_probs) / len(log_probs)
        perplexity = math.exp(-avg_log_prob)

        # Uniform baseline
        uniform_perplexity = len(observed_types)

        perplexity_ratio = perplexity / uniform_perplexity
        print(f"\n3. PERPLEXITY")
        print(f"   Model perplexity: {perplexity:.1f}")
        print(f"   Uniform perplexity: {uniform_perplexity}")
        print(f"   Ratio: {100*perplexity_ratio:.1f}%")
        print(f"   Target: <30% | {'PASS' if perplexity_ratio < 0.3 else 'FAIL'}")
    else:
        perplexity = float('inf')
        perplexity_ratio = 1.0
        print(f"\n3. PERPLEXITY: Could not calculate")

    # Overall assessment
    print("\n" + "=" * 60)
    print("OVERALL ASSESSMENT")
    print("=" * 60)

    all_pass = type_coverage > 0.9 and token_coverage > 0.85 and perplexity_ratio < 0.3
    print(f"\nType coverage: {100*type_coverage:.1f}% {'PASS' if type_coverage > 0.9 else 'FAIL'}")
    print(f"Token coverage: {100*token_coverage:.1f}% {'PASS' if token_coverage > 0.85 else 'FAIL'}")
    print(f"Perplexity ratio: {100*perplexity_ratio:.1f}% {'PASS' if perplexity_ratio < 0.3 else 'FAIL'}")
    print(f"\nModel status: {'SUCCESS - factored model explains structure' if all_pass else 'PARTIAL - some criteria not met'}")

    # Save results
    results = {
        'type_coverage': type_coverage,
        'token_coverage': token_coverage,
        'perplexity': perplexity,
        'perplexity_ratio': perplexity_ratio,
        'observed_types': len(observed_types),
        'generated_types': len(generated_types),
        'novel_types': len(novel_types),
        'novel_rate': len(novel_types) / len(generated_types),
        'all_pass': all_pass,
        'sample_novel_types': list(novel_types)[:20],
        'sample_covered_types': list(type_overlap)[:20]
    }

    return results


def analyze_component_contribution():
    """Analyze how much each component contributes to the model."""
    print("\n" + "=" * 60)
    print("COMPONENT CONTRIBUTION ANALYSIS")
    print("=" * 60)

    tokens = load_currier_a_tokens()
    p_prefix, p_middle_given_prefix, p_suffix_given_pm, decomposed = build_probability_tables(tokens)

    # How many unique middles per prefix?
    print("\nMIDDLE diversity per PREFIX:")
    for prefix in sorted(p_prefix.keys(), key=lambda x: p_prefix[x], reverse=True):
        n_middles = len(p_middle_given_prefix.get(prefix, {}))
        print(f"  {prefix}: {n_middles} unique middles, P(prefix)={p_prefix[prefix]:.3f}")

    # How concentrated are the suffix distributions?
    print("\nSUFFIX concentration per (PREFIX, MIDDLE):")
    entropy_samples = []
    for key, suffixes in list(p_suffix_given_pm.items())[:20]:
        # Calculate entropy
        entropy = -sum(p * math.log2(p) for p in suffixes.values() if p > 0)
        max_entropy = math.log2(len(suffixes)) if len(suffixes) > 1 else 0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        entropy_samples.append(normalized_entropy)
        print(f"  {key}: {len(suffixes)} suffixes, entropy={entropy:.2f} bits")

    if entropy_samples:
        print(f"\nMean normalized suffix entropy: {sum(entropy_samples)/len(entropy_samples):.3f}")


def main():
    print("=" * 60)
    print("CURRIER A TOKEN GENERATOR MODEL (Target 1)")
    print("=" * 60)

    # Load tokens
    tokens = load_currier_a_tokens()
    print(f"\nLoaded {len(tokens)} Currier A tokens")

    # Build probability tables
    p_prefix, p_middle_given_prefix, p_suffix_given_pm, decomposed = build_probability_tables(tokens)

    # Show model statistics
    print(f"\nModel statistics:")
    print(f"  Prefixes: {len(p_prefix)}")
    print(f"  Unique (prefix, middle) pairs: {sum(len(v) for v in p_middle_given_prefix.values())}")
    print(f"  Unique (prefix, middle, suffix) contexts: {len(p_suffix_given_pm)}")

    # Evaluate
    results = evaluate_generator(tokens, decomposed, p_prefix, p_middle_given_prefix, p_suffix_given_pm)

    # Component analysis
    analyze_component_contribution()

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'currier_a_token_generator_eval.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    main()
