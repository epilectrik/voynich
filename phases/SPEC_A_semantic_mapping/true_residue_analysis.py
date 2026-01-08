"""
Find the TRUE residue tokens - ones that don't fit ANY grammar pattern.
These are the "human track" candidates.
"""

from collections import Counter, defaultdict
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

# Grammar patterns (from SID-01 definition)
GRAMMAR_PREFIXES = ['qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'da', 'ct']
GRAMMAR_SUFFIXES = ['aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'al', 'edy']

# Known grammar tokens
GRAMMAR_TOKENS = {
    'qokaiin', 'chey', 'cheey', 'chedy', 'okaiin', 'dar', 'okal', 'saiin',
    'qokal', 'daiin', 'dol', 'ckhey', 'chol', 'dy', 'cheky', 'tedy', 'ol',
    'aiin', 'checkhy', 'otain', 'shey', 'shol', 'shedy', 'shy', 'shor',
    'qo', 'qok', 'ok', 'al', 'or', 'ar', 'dal', 'qokedy', 'okey', 'okeey',
    'okedy', 'chee', 'cheol', 'ched', 'chor', 'char', 'sho', 'she',
    'qokeey', 'qokain', 'okain', 'sheey', 'sheo', 'otar',
    'oteey', 'otedy', 'okeedy', 'taiin', 'cthaiin', 'cthol', 'cthor', 'cthy',
    'kcheol', 'kchey', 'kcheedy', 'pchedy', 'pchey', 'fchedy', 'fchey',
    's', 'y', 'r', 'l', 'o', 'd', 'k', 'e', 'h', 't', 'c'  # Single-char primitives
}

def is_grammar_token(tok):
    """Check if token fits grammar pattern."""
    t = tok.lower()

    # Direct match
    if t in GRAMMAR_TOKENS:
        return True

    # Has grammar prefix
    for p in GRAMMAR_PREFIXES:
        if t.startswith(p):
            return True

    # Has grammar suffix
    for s in GRAMMAR_SUFFIXES:
        if t.endswith(s):
            return True

    # L-compounds (B grammar operators)
    if t.startswith('l') and len(t) > 1 and t[1] in 'cks':
        return True

    # Articulator patterns (yk-, yt-, sa-, etc.)
    if t.startswith(('yk', 'yt', 'yc', 'yd', 'sa', 'so', 'ka', 'ke', 'ta', 'te', 'op', 'pc', 'dc', 'tc', 'kc')):
        return True

    return False

# Load tokens
all_tokens = []
by_language = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 6:
            word = parts[0].strip('"').strip().lower()
            lang = parts[6].strip('"').strip()
            section = parts[3].strip('"').strip() if len(parts) > 3 else ''

            if word and not word.startswith('*'):
                all_tokens.append({'word': word, 'lang': lang, 'section': section})
                by_language[lang].append(word)

print("=" * 70)
print("TRUE RESIDUE TOKEN ANALYSIS")
print("=" * 70)

# Classify all tokens
grammar_tokens = []
residue_tokens = []

for entry in all_tokens:
    word = entry['word']
    if is_grammar_token(word):
        grammar_tokens.append(entry)
    else:
        residue_tokens.append(entry)

print(f"\n### CLASSIFICATION")
print(f"Total tokens: {len(all_tokens)}")
print(f"Grammar tokens: {len(grammar_tokens)} ({100*len(grammar_tokens)/len(all_tokens):.1f}%)")
print(f"RESIDUE tokens: {len(residue_tokens)} ({100*len(residue_tokens)/len(all_tokens):.1f}%)")

# Residue by language
a_residue = [e for e in residue_tokens if e['lang'] == 'A']
b_residue = [e for e in residue_tokens if e['lang'] == 'B']

print(f"\n### RESIDUE BY LANGUAGE")
print(f"A residue: {len(a_residue)} ({100*len(a_residue)/len(by_language['A']):.1f}% of A)")
print(f"B residue: {len(b_residue)} ({100*len(b_residue)/len(by_language['B']):.1f}% of B)")

# What ARE the residue tokens?
residue_words = [e['word'] for e in residue_tokens]
residue_freq = Counter(residue_words)

print(f"\n### TOP 50 RESIDUE TOKENS")
print(f"{'Token':<15} {'Count':>8} {'A':>8} {'B':>8}")
print("-" * 45)

a_residue_words = Counter([e['word'] for e in a_residue])
b_residue_words = Counter([e['word'] for e in b_residue])

for tok, count in residue_freq.most_common(50):
    a_c = a_residue_words.get(tok, 0)
    b_c = b_residue_words.get(tok, 0)
    print(f"{tok:<15} {count:>8} {a_c:>8} {b_c:>8}")

# What do residue tokens look like?
print(f"\n### RESIDUE TOKEN CHARACTERISTICS")
print("-" * 70)

# Length distribution
lens = [len(w) for w in residue_words]
print(f"\nAverage length: {sum(lens)/len(lens):.1f} chars")
print(f"Length distribution:")
len_dist = Counter(lens)
for l in sorted(len_dist.keys())[:8]:
    print(f"  {l} chars: {len_dist[l]} ({100*len_dist[l]/len(residue_words):.1f}%)")

# Starting patterns
starts = Counter()
for w in residue_words:
    if len(w) >= 2:
        starts[w[:2]] += 1

print(f"\nTop starting digraphs:")
for digraph, count in starts.most_common(15):
    print(f"  {digraph}: {count}")

# Ending patterns
ends = Counter()
for w in residue_words:
    if len(w) >= 2:
        ends[w[-2:]] += 1

print(f"\nTop ending digraphs:")
for digraph, count in ends.most_common(15):
    print(f"  {digraph}: {count}")

# Section distribution
print(f"\n### RESIDUE BY SECTION")
section_dist = Counter(e['section'] for e in residue_tokens)
total_by_section = Counter(e['section'] for e in all_tokens)

for section in ['H', 'P', 'T', 'A', 'B', 'C', 'S', 'Z']:
    res = section_dist.get(section, 0)
    total = total_by_section.get(section, 0)
    if total > 0:
        print(f"  {section}: {res}/{total} ({100*res/total:.1f}%)")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
