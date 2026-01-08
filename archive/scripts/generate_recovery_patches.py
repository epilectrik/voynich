"""
Generate recovery_patches.tsv for damaged tokens in the Voynich transcription.

Uses structural knowledge (vocabulary frequency) to propose recoveries for
tokens containing * characters (EVA notation for uncertain/damaged glyphs).
"""

from collections import Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
input_filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
output_filepath = project_root / 'data' / 'transcriptions' / 'recovery_patches.tsv'

# Build clean vocabulary with frequencies
print("Building vocabulary from clean tokens...")
all_vocab = Counter()
damaged_tokens = []

with open(input_filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
            line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

            if not word:
                continue

            if '*' in word:
                damaged_tokens.append({
                    'word': word,
                    'folio': folio,
                    'line': line_num
                })
            else:
                all_vocab[word] += 1

print(f"Clean vocabulary: {len(all_vocab)} types, {sum(all_vocab.values())} tokens")
print(f"Damaged tokens: {len(damaged_tokens)}")

def matches_pattern(candidate, pattern):
    """Check if candidate matches pattern with * as wildcard."""
    if len(candidate) != len(pattern):
        return False
    for c, p in zip(candidate, pattern):
        if p != '*' and c != p:
            return False
    return True

def analyze_damaged_token(word, vocab):
    """Find candidates and determine confidence level."""
    candidates = [tok for tok in vocab if matches_pattern(tok, word)]
    candidates_ranked = sorted(candidates, key=lambda t: -vocab[t])

    if len(candidates_ranked) == 0:
        return None, 'NO_MATCH', []
    elif len(candidates_ranked) == 1:
        return candidates_ranked[0], 'CERTAIN', candidates_ranked
    elif len(candidates_ranked) <= 5:
        # Check if top candidate dominates
        top_freq = vocab[candidates_ranked[0]]
        total_freq = sum(vocab[c] for c in candidates_ranked)
        if top_freq / total_freq >= 0.8:
            return candidates_ranked[0], 'HIGH', candidates_ranked
        else:
            return candidates_ranked[0], 'HIGH', candidates_ranked
    else:
        # High ambiguity
        top_freq = vocab[candidates_ranked[0]]
        total_freq = sum(vocab[c] for c in candidates_ranked)
        if top_freq / total_freq >= 0.5:
            return candidates_ranked[0], 'AMBIGUOUS', candidates_ranked[:10]
        else:
            return candidates_ranked[0], 'AMBIGUOUS', candidates_ranked[:10]

# Generate patches
print("\nAnalyzing damaged tokens...")
patches = []
stats = Counter()

for entry in damaged_tokens:
    word = entry['word']
    folio = entry['folio']
    line = entry['line']

    recovered, confidence, candidates = analyze_damaged_token(word, all_vocab)
    stats[confidence] += 1

    if recovered:
        # Format candidates as semicolon-separated list
        cand_str = ';'.join(candidates[:5])
        patches.append({
            'folio': folio,
            'line': line,
            'original': word,
            'recovered': recovered,
            'confidence': confidence,
            'candidates': cand_str
        })

# Write patch file
print(f"\nWriting {len(patches)} patches to {output_filepath}...")

with open(output_filepath, 'w', encoding='utf-8') as f:
    f.write("folio\tline\toriginal\trecovered\tconfidence\tcandidates\n")
    for p in patches:
        f.write(f"{p['folio']}\t{p['line']}\t{p['original']}\t{p['recovered']}\t{p['confidence']}\t{p['candidates']}\n")

print("\n" + "=" * 60)
print("RECOVERY PATCH GENERATION COMPLETE")
print("=" * 60)
print(f"\nStatistics:")
print(f"  CERTAIN (unique match):     {stats['CERTAIN']:>5} ({100*stats['CERTAIN']/len(damaged_tokens):.1f}%)")
print(f"  HIGH (2-5 candidates):      {stats['HIGH']:>5} ({100*stats['HIGH']/len(damaged_tokens):.1f}%)")
print(f"  AMBIGUOUS (>5 candidates):  {stats['AMBIGUOUS']:>5} ({100*stats['AMBIGUOUS']/len(damaged_tokens):.1f}%)")
print(f"  NO_MATCH (no candidates):   {stats['NO_MATCH']:>5} ({100*stats['NO_MATCH']/len(damaged_tokens):.1f}%)")
print(f"\nTotal damaged: {len(damaged_tokens)}")
print(f"Total recoverable: {len(patches)}")
print(f"\nOutput: {output_filepath}")

# Show sample patches
print("\n" + "-" * 60)
print("SAMPLE PATCHES (first 20)")
print("-" * 60)
print(f"{'Folio':<10} {'Original':<15} {'Recovered':<15} {'Confidence':<12}")
for p in patches[:20]:
    print(f"{p['folio']:<10} {p['original']:<15} {p['recovered']:<15} {p['confidence']:<12}")
