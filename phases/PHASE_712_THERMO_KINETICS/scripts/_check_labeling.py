"""Sanity check: what does my excited-labeling actually pick up?

Verify that ch/sh PREFIX-h and ok/ot/qo PREFIX-k are correctly stripped.
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Sample tokens
test_tokens = ['chedy', 'shedy', 'qokeedy', 'okeey', 'cthy', 'okchy', 'chchy',
               'kchody', 'kor', 'keey', 'hor', 'cphedy', 'chckhy']
print("Sample token decompositions:")
for tok in test_tokens:
    m = morph.extract(tok)
    pfx = m.prefix or ''
    mid = m.middle or ''
    suf = m.suffix or ''
    has_k_mid = 'k' in mid
    has_h_mid = 'h' in mid
    print(f"  {tok:<12} PREFIX={pfx:<6} MIDDLE={mid:<8} SUFFIX={suf:<6} "
          f"k_in_MID={has_k_mid} h_in_MID={has_h_mid}")

# Real distribution: of tokens labeled "excited" (k or h in MIDDLE), what does
# the PREFIX look like?
prefix_counts_excited = Counter()
prefix_counts_all = Counter()
n_excited = 0
n_total = 0
examples_excited_by_prefix = {}
for t in tx.all(h_only=True):
    if not t.word.strip() or '*' in t.word:
        continue
    if t.language != 'B':
        continue
    if not (t.placement and t.placement.startswith('P')):
        continue
    n_total += 1
    w = t.word.lower()
    m = morph.extract(w)
    pfx = m.prefix or 'NONE'
    mid = m.middle or ''
    prefix_counts_all[pfx] += 1
    if 'k' in mid or 'h' in mid:
        n_excited += 1
        prefix_counts_excited[pfx] += 1
        if pfx not in examples_excited_by_prefix:
            examples_excited_by_prefix[pfx] = []
        if len(examples_excited_by_prefix[pfx]) < 5:
            examples_excited_by_prefix[pfx].append((w, mid))

print(f"\nN total Currier B P-placement tokens: {n_total}")
print(f"N excited (k or h in MIDDLE): {n_excited} ({100*n_excited/n_total:.2f}%)")
print(f"\nTop PREFIX classes among 'excited' tokens:")
for pfx, c in prefix_counts_excited.most_common(15):
    pct_within_excited = 100 * c / n_excited
    pct_within_all_pfx = 100 * c / prefix_counts_all[pfx]
    examples = examples_excited_by_prefix.get(pfx, [])[:3]
    print(f"  {pfx:<8} n_excited={c:>5} ({pct_within_excited:.1f}% of excited, "
          f"{pct_within_all_pfx:.1f}% of {pfx}-tokens) examples: {examples}")

# Breakdown: 'k' in MIDDLE vs 'h' in MIDDLE
n_k_only = sum(1 for w in (t.word.lower() for t in tx.all(h_only=True)
               if t.word.strip() and '*' not in t.word and t.language == 'B'
               and t.placement and t.placement.startswith('P'))
               if 'k' in (morph.extract(w).middle or '') and 'h' not in (morph.extract(w).middle or ''))
n_h_only = sum(1 for w in (t.word.lower() for t in tx.all(h_only=True)
               if t.word.strip() and '*' not in t.word and t.language == 'B'
               and t.placement and t.placement.startswith('P'))
               if 'h' in (morph.extract(w).middle or '') and 'k' not in (morph.extract(w).middle or ''))
n_both = sum(1 for w in (t.word.lower() for t in tx.all(h_only=True)
             if t.word.strip() and '*' not in t.word and t.language == 'B'
             and t.placement and t.placement.startswith('P'))
             if 'k' in (morph.extract(w).middle or '') and 'h' in (morph.extract(w).middle or ''))
print(f"\n  k-only in MIDDLE: {n_k_only}")
print(f"  h-only in MIDDLE: {n_h_only}")
print(f"  both k and h in MIDDLE: {n_both}")
