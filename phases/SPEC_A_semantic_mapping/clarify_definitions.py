"""
Clarify the three different token categorizations:
1. Uncategorized (no known prefix)
2. Residue (doesn't fit grammar patterns)
3. Human track (low frequency, not operational)
"""

from collections import Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Definition 1: Known prefixes
KNOWN_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Definition 2: Grammar patterns (from SID)
GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']
GRAMMAR_SUFFIXES = ['aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'al', 'edy']

# Definition 3: Operational tokens (from human_track_hazard_test.py)
OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol',
    'dain', 'chain', 'shain', 'rain', 'kain', 'taiin', 'saiin',
    'chkaiin', 'otaiin', 'oraiin', 'okaiin',
}

# Load all tokens
all_tokens = []
with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 0:
            word = parts[0].strip('"').strip().lower()
            if word and not word.startswith('*'):
                all_tokens.append(word)

total = len(all_tokens)
token_counts = Counter(all_tokens)

print("=" * 70)
print("THREE DEFINITIONS COMPARED")
print("=" * 70)

# Definition 1: No known prefix
def has_prefix(tok):
    for p in KNOWN_PREFIXES:
        if tok.startswith(p):
            return True
    return False

no_prefix = [t for t in all_tokens if not has_prefix(t)]
print(f"\n1. UNCATEGORIZED (no known prefix)")
print(f"   Count: {len(no_prefix)} ({100*len(no_prefix)/total:.1f}%)")

# Definition 2: Doesn't fit grammar patterns
def fits_grammar(tok):
    for p in GRAMMAR_PREFIXES:
        if tok.startswith(p):
            return True
    for s in GRAMMAR_SUFFIXES:
        if tok.endswith(s):
            return True
    if tok.startswith('l') and len(tok) > 1 and tok[1] in 'cks':
        return True
    if tok.startswith(('yk', 'yt', 'yc', 'sa', 'so', 'ka', 'ke', 'ta', 'te', 'op')):
        return True
    return False

residue = [t for t in all_tokens if not fits_grammar(t)]
print(f"\n2. RESIDUE (doesn't fit grammar patterns)")
print(f"   Count: {len(residue)} ({100*len(residue)/total:.1f}%)")

# Definition 3: Human track (low frequency, not operational)
def is_human_track(tok):
    if tok in OPERATIONAL_TOKENS:
        return False
    freq = token_counts.get(tok, 0) / total
    if freq > 0.001:  # > 0.1%
        return False
    return True

human_track = [t for t in all_tokens if is_human_track(t)]
print(f"\n3. HUMAN TRACK (low freq <0.1%, not operational)")
print(f"   Count: {len(human_track)} ({100*len(human_track)/total:.1f}%)")

# Overlap analysis
print("\n" + "=" * 70)
print("OVERLAP ANALYSIS")
print("=" * 70)

no_prefix_set = set(no_prefix)
residue_set = set(residue)
ht_set = set(human_track)

# As unique tokens
no_prefix_vocab = set(t for t in token_counts if not has_prefix(t))
residue_vocab = set(t for t in token_counts if not fits_grammar(t))
ht_vocab = set(t for t in token_counts if is_human_track(t))

print(f"\nAs unique vocabulary types:")
print(f"  No-prefix types: {len(no_prefix_vocab)}")
print(f"  Residue types: {len(residue_vocab)}")
print(f"  Human-track types: {len(ht_vocab)}")

print(f"\nOverlaps (by type):")
print(f"  Residue ∩ Human-track: {len(residue_vocab & ht_vocab)}")
print(f"  No-prefix ∩ Human-track: {len(no_prefix_vocab & ht_vocab)}")
print(f"  No-prefix ∩ Residue: {len(no_prefix_vocab & residue_vocab)}")
print(f"  All three: {len(no_prefix_vocab & residue_vocab & ht_vocab)}")

# What's in human track but NOT residue?
ht_not_residue = ht_vocab - residue_vocab
print(f"\n  Human-track but NOT residue: {len(ht_not_residue)}")
if ht_not_residue:
    examples = list(ht_not_residue)[:20]
    print(f"    Examples: {examples}")

# What's in residue but NOT human track?
residue_not_ht = residue_vocab - ht_vocab
print(f"\n  Residue but NOT human-track: {len(residue_not_ht)}")
if residue_not_ht:
    examples = list(residue_not_ht)[:20]
    print(f"    Examples: {examples}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
