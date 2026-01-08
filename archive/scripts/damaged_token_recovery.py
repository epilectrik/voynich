"""
Can we recover damaged tokens using structural knowledge?

Test: Given a token like "d*" or "o***", how many valid completions exist?
If completions are highly constrained, recovery is feasible.
"""

from collections import Counter, defaultdict
from pathlib import Path

filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Build vocabulary by section
vocab_by_section = defaultdict(Counter)
all_vocab = Counter()
damaged_tokens = []

with open(filepath, 'r', encoding='utf-8') as f:
    f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
            lang = parts[6].strip('"').strip()

            if not word:
                continue

            if '*' in word:
                damaged_tokens.append((word, section, folio, lang))
            else:
                vocab_by_section[section][word] += 1
                all_vocab[word] += 1

print("=" * 70)
print("DAMAGED TOKEN RECOVERY ANALYSIS")
print("=" * 70)

print(f"\nTotal damaged tokens: {len(damaged_tokens)}")
print(f"Total clean vocabulary: {len(all_vocab)} types")

# Analyze damaged tokens
print(f"\n### DAMAGED TOKEN PATTERNS")
damage_patterns = Counter()
for word, section, folio, lang in damaged_tokens:
    # Count number of * characters
    stars = word.count('*')
    length = len(word)
    clean_chars = length - stars
    pattern = f"{clean_chars}known_{stars}unknown"
    damage_patterns[pattern] += 1

for pattern, count in damage_patterns.most_common(10):
    print(f"  {pattern}: {count}")

# For each damaged token, find possible completions
print(f"\n### RECOVERY FEASIBILITY TEST")
print("For each damaged token, count how many valid tokens could match")

def matches_pattern(candidate, pattern):
    """Check if candidate matches pattern with * as wildcard."""
    if len(candidate) != len(pattern):
        return False
    for c, p in zip(candidate, pattern):
        if p != '*' and c != p:
            return False
    return True

recovery_results = []

for word, section, folio, lang in damaged_tokens[:100]:  # Test first 100
    # Find all tokens that could match this pattern
    candidates = [tok for tok in all_vocab if matches_pattern(tok, word)]

    # Also check section-specific vocabulary
    section_candidates = [tok for tok in vocab_by_section[section] if matches_pattern(tok, word)]

    recovery_results.append({
        'damaged': word,
        'section': section,
        'folio': folio,
        'all_matches': len(candidates),
        'section_matches': len(section_candidates),
        'top_candidates': sorted(candidates, key=lambda t: -all_vocab[t])[:5]
    })

# Summarize
print(f"\n{'Damaged':<15} {'Sect':<5} {'All#':>6} {'Sect#':>6} {'Top Candidates':<40}")
print("-" * 80)

unique_count = 0
low_count = 0
high_count = 0

for r in recovery_results:
    cands = ', '.join(r['top_candidates'][:3]) if r['top_candidates'] else '(none)'
    print(f"{r['damaged']:<15} {r['section']:<5} {r['all_matches']:>6} {r['section_matches']:>6} {cands:<40}")

    if r['all_matches'] == 1:
        unique_count += 1
    elif r['all_matches'] <= 5:
        low_count += 1
    else:
        high_count += 1

print(f"\n### RECOVERY SUMMARY (first 100 damaged tokens)")
print(f"Unique match (100% recoverable): {unique_count}")
print(f"Low ambiguity (2-5 candidates): {low_count}")
print(f"High ambiguity (>5 candidates): {high_count}")
print(f"No matches: {sum(1 for r in recovery_results if r['all_matches'] == 0)}")

# Test validation: can we recover known tokens?
print(f"\n### VALIDATION TEST")
print("Mask one character from known tokens, see if we can recover")

import random
random.seed(42)

# Sample 100 common tokens
test_tokens = [tok for tok, freq in all_vocab.most_common(500) if len(tok) >= 3][:100]

correct = 0
top3_correct = 0
total = 0

for tok in test_tokens:
    # Mask one random character
    pos = random.randint(0, len(tok)-1)
    masked = tok[:pos] + '*' + tok[pos+1:]

    # Find candidates
    candidates = [t for t in all_vocab if matches_pattern(t, masked)]
    candidates_ranked = sorted(candidates, key=lambda t: -all_vocab[t])

    if candidates_ranked:
        total += 1
        if candidates_ranked[0] == tok:
            correct += 1
        if tok in candidates_ranked[:3]:
            top3_correct += 1

print(f"Masked 1 character from {total} tokens:")
print(f"  Top-1 accuracy: {100*correct/total:.1f}%")
print(f"  Top-3 accuracy: {100*top3_correct/total:.1f}%")

print("\n" + "=" * 70)
