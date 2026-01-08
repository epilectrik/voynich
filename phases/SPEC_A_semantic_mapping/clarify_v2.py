"""
Clarify definitions - fixed encoding
"""

from collections import Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

KNOWN_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']
GRAMMAR_SUFFIXES = ['aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'al', 'edy']
OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol',
    'dain', 'chain', 'shain', 'rain', 'kain', 'taiin', 'saiin',
    'chkaiin', 'otaiin', 'oraiin', 'okaiin',
}

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

def has_prefix(tok):
    for p in KNOWN_PREFIXES:
        if tok.startswith(p):
            return True
    return False

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

def is_human_track(tok):
    if tok in OPERATIONAL_TOKENS:
        return False
    freq = token_counts.get(tok, 0) / total
    if freq > 0.001:
        return False
    return True

no_prefix_vocab = set(t for t in token_counts if not has_prefix(t))
residue_vocab = set(t for t in token_counts if not fits_grammar(t))
ht_vocab = set(t for t in token_counts if is_human_track(t))

print("OVERLAP ANALYSIS (by unique token types)")
print("=" * 50)
print(f"No-prefix types: {len(no_prefix_vocab)}")
print(f"Residue types: {len(residue_vocab)}")
print(f"Human-track types: {len(ht_vocab)}")

print(f"\nResdiue AND Human-track: {len(residue_vocab & ht_vocab)}")
print(f"No-prefix AND Human-track: {len(no_prefix_vocab & ht_vocab)}")
print(f"No-prefix AND Residue: {len(no_prefix_vocab & residue_vocab)}")
print(f"All three: {len(no_prefix_vocab & residue_vocab & ht_vocab)}")

# The key question: what IS human track that ISN'T residue?
ht_not_residue = ht_vocab - residue_vocab
print(f"\nHuman-track but NOT residue: {len(ht_not_residue)} types")
print("Examples:", sorted(ht_not_residue, key=lambda x: -token_counts[x])[:30])

# And what IS residue that isn't low frequency?
high_freq_residue = [t for t in residue_vocab if token_counts[t]/total > 0.001]
print(f"\nResidue but HIGH frequency (>0.1%): {len(high_freq_residue)} types")
print("Examples:", high_freq_residue[:20])
