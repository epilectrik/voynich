"""Compare f66r vocabulary to A, B, and AZC."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

tx = Transcript()
all_tokens = list(tx.all(h_only=True))

# Get token sets by category
def get_vocab(tokens):
    return set(t.word for t in tokens if t.word.strip() and '*' not in t.word)

def get_words(tokens):
    return [t.word for t in tokens if t.word.strip() and '*' not in t.word]

# Currier A text (P-placement only)
a_tokens = [t for t in all_tokens if t.language == 'A' and t.placement.startswith('P')]
a_vocab = get_vocab(a_tokens)

# Currier B text (P-placement only - standard paragraphs)
b_tokens = [t for t in all_tokens if t.language == 'B' and t.placement.startswith('P')]
b_vocab = get_vocab(b_tokens)

# AZC (language=NA, which is the AZC sections)
azc_tokens = [t for t in all_tokens if t.language == 'NA']
azc_vocab = get_vocab(azc_tokens)

# f66r R-placement (the "text" part, not margin labels)
f66r_tokens = [t for t in all_tokens if t.folio == 'f66r' and t.placement.startswith('R')]
f66r_vocab = get_vocab(f66r_tokens)
f66r_words = get_words(f66r_tokens)

print("=== VOCABULARY SIZES ===\n")
print(f"Currier A (P-placement): {len(a_vocab)} types, {len(get_words(a_tokens))} tokens")
print(f"Currier B (P-placement): {len(b_vocab)} types, {len(get_words(b_tokens))} tokens")
print(f"AZC (language=NA): {len(azc_vocab)} types, {len(get_words(azc_tokens))} tokens")
print(f"f66r (R-placement): {len(f66r_vocab)} types, {len(f66r_words)} tokens")

print("\n=== VOCABULARY OVERLAP ===\n")

# How much of f66r's vocabulary appears in each corpus?
f66r_in_a = len(f66r_vocab & a_vocab)
f66r_in_b = len(f66r_vocab & b_vocab)
f66r_in_azc = len(f66r_vocab & azc_vocab)

print(f"f66r vocab in Currier A: {f66r_in_a}/{len(f66r_vocab)} = {f66r_in_a/len(f66r_vocab):.1%}")
print(f"f66r vocab in Currier B: {f66r_in_b}/{len(f66r_vocab)} = {f66r_in_b/len(f66r_vocab):.1%}")
print(f"f66r vocab in AZC: {f66r_in_azc}/{len(f66r_vocab)} = {f66r_in_azc/len(f66r_vocab):.1%}")

# Exclusive overlaps
f66r_only_in_a = f66r_vocab & a_vocab - b_vocab - azc_vocab
f66r_only_in_b = f66r_vocab & b_vocab - a_vocab - azc_vocab
f66r_only_in_azc = f66r_vocab & azc_vocab - a_vocab - b_vocab
f66r_in_none = f66r_vocab - a_vocab - b_vocab - azc_vocab

print(f"\nf66r vocab ONLY in A (not B, not AZC): {len(f66r_only_in_a)}")
print(f"f66r vocab ONLY in B (not A, not AZC): {len(f66r_only_in_b)}")
print(f"f66r vocab ONLY in AZC (not A, not B): {len(f66r_only_in_azc)}")
print(f"f66r vocab in NONE of the above: {len(f66r_in_none)}")

print("\n=== MOST COMMON f66r TOKENS ===\n")
word_counts = Counter(f66r_words)
for word, count in word_counts.most_common(20):
    in_a = "A" if word in a_vocab else "-"
    in_b = "B" if word in b_vocab else "-"
    in_azc = "Z" if word in azc_vocab else "-"
    print(f"  {word:15} x{count:>3}  [{in_a}{in_b}{in_azc}]")

print("\n=== f66r-UNIQUE VOCABULARY ===\n")
print("Tokens in f66r but NOT in A, B, or AZC:")
for word in sorted(f66r_in_none)[:30]:
    count = word_counts[word]
    print(f"  {word:15} x{count}")

print("\n=== COMPARISON: TYPICAL B FOLIO (f75r) ===\n")
f75r_tokens = [t for t in all_tokens if t.folio == 'f75r' and t.placement.startswith('P')]
f75r_vocab = get_vocab(f75r_tokens)

f75r_in_a = len(f75r_vocab & a_vocab)
f75r_in_b = len(f75r_vocab & b_vocab)
f75r_in_azc = len(f75r_vocab & azc_vocab)

print(f"f75r vocab in Currier A: {f75r_in_a}/{len(f75r_vocab)} = {f75r_in_a/len(f75r_vocab):.1%}")
print(f"f75r vocab in Currier B: {f75r_in_b}/{len(f75r_vocab)} = {f75r_in_b/len(f75r_vocab):.1%}")
print(f"f75r vocab in AZC: {f75r_in_azc}/{len(f75r_vocab)} = {f75r_in_azc/len(f75r_vocab):.1%}")
