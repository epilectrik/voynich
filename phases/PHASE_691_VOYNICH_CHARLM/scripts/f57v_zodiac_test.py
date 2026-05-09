#!/usr/bin/env python3
"""
Test crazy-expert prediction: f57v R2 coordinate-system primitives appear at
predicted positions in zodiac folios.

f57v R2 cycle: o l d r x k _ _ t r y c (10 fixed + 2 variable positions)
Zodiac folios: 12 (one per month). If f57v R2 specifies a 12-position
coordinate axis, each zodiac folio should "land" at one cycle position.

Tests:
  1. Inventory tokens of each zodiac folio
  2. Check if any zodiac folio prominently features one specific f57v R2
     primitive (e.g., zodiac month-1 has 'o' as a key marker, month-2 'l', etc.)
  3. Look at folio-mean tokens / labels for f57v-cycle correspondence
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript


# 12-position coordinate cycle from f57v R2
F57V_R2_CYCLE_FIXED = ['o', 'l', 'd', 'r', 'x', 'k', None, None, 't', 'r', 'y', 'c']
# Variable slot (positions 6-7): observed combinations
F57V_R2_VAR_SLOT = ['kf', 'mf', 'kp']  # observed unique values

# Zodiac folios in order (per project: each represents one zodiac sign / month)
# Pisces, Aries, Taurus etc. - actual order may vary
ZODIAC_FOLIOS = [
    'f70v2', 'f70v1', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v',
]


def main():
    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.all(h_only=True):
        if tok.folio in ZODIAC_FOLIOS and tok.word and not tok.is_uncertain:
            by_folio[tok.folio].append(tok)

    print(f"Zodiac folios with H-track tokens:")
    for f in ZODIAC_FOLIOS:
        n = len(by_folio.get(f, []))
        print(f"  {f}: {n} tokens")

    # For each zodiac folio, look at:
    # - Most common single-char tokens (might match f57v R2 cycle positions)
    # - Most common starting characters (might match cycle position)
    # - Distribution of f57v R2 fixed-position chars: o, l, d, r, x, k, t, y, c

    f57v_chars = set('oldrxktryc')

    print(f"\n=== f57v R2 primitive presence across zodiac folios ===")
    print(f"  Looking for concentration of f57v cycle primitives: o, l, d, r, x, k, t, y, c")
    print(f"  AND the variable-slot indicators: f, p, m\n")
    print(f"{'folio':>7s}  {'n_tok':>5s}  {'1char':>5s}  {'len2':>4s}  {'len3':>4s}  {'l_avg':>5s}  {'p_chars':>7s}  {'f_chars':>7s}  {'x_chars':>7s}")
    for f in ZODIAC_FOLIOS:
        toks = by_folio.get(f, [])
        if not toks:
            continue
        word_lens = [len(t.word) for t in toks]
        len_dist = Counter(word_lens)
        all_chars = ''.join(t.word for t in toks)
        n_p = all_chars.count('p')
        n_f = all_chars.count('f')
        n_x = all_chars.count('x')
        avg_len = sum(word_lens) / len(toks)
        print(f"  {f:>7s}  {len(toks):>5d}  {len_dist.get(1, 0):>5d}  {len_dist.get(2, 0):>4d}  {len_dist.get(3, 0):>4d}  {avg_len:>5.2f}  {n_p:>7d}  {n_f:>7d}  {n_x:>7d}")

    # For folios with single-char tokens, what are they?
    print(f"\n=== Single-char tokens in zodiac folios (should match f57v R2 cycle if hypothesis holds) ===")
    for f in ZODIAC_FOLIOS:
        toks = by_folio.get(f, [])
        single_chars = [t.word for t in toks if len(t.word) == 1]
        if single_chars:
            counts = Counter(single_chars)
            in_cycle = sum(1 for c in single_chars if c in f57v_chars)
            print(f"  {f}: {len(single_chars)} single-char tokens. Distribution: {dict(counts.most_common())}. In-f57v-cycle: {in_cycle}/{len(single_chars)}")

    # CONTROL: same analysis on randomly-chosen non-zodiac folios
    print(f"\n=== Control: same analysis on random Currier-B folios ===")
    control_folios = ['f75r', 'f80r', 'f95v', 'f105v', 'f111r', 'f113r']
    for f in control_folios:
        ctrl_toks = []
        for tok in tx.all(h_only=True):
            if tok.folio == f and tok.word and not tok.is_uncertain:
                ctrl_toks.append(tok)
        if not ctrl_toks:
            continue
        single_chars = [t.word for t in ctrl_toks if len(t.word) == 1]
        word_lens = [len(t.word) for t in ctrl_toks]
        avg_len = sum(word_lens) / len(ctrl_toks)
        n_x = sum(t.word.count('x') for t in ctrl_toks)
        n_f = sum(t.word.count('f') for t in ctrl_toks)
        n_p = sum(t.word.count('p') for t in ctrl_toks)
        print(f"  {f}: n={len(ctrl_toks)} avg_len={avg_len:.2f} 1char={len(single_chars)} x={n_x} f={n_f} p={n_p}")
        if single_chars:
            counts = Counter(single_chars)
            print(f"     single-char distribution: {dict(counts.most_common())}")


if __name__ == '__main__':
    main()
