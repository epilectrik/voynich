#!/usr/bin/env python3
"""
Phase 691.x: Explore f57v structure to test coordinate-system hypothesis.

Per crazy-expert prediction:
  - R2 ring has 12-char period (reference positions)
  - p/f markers at offset 27 partition hemispheres
  - 'x' character (corpus-rare) marks coordinate origin
  - f57v decodes positional/coordinate primitives (vs f66r operational atoms)

Tests:
  1. Inventory f57v tokens by placement code (P=text, R=ring, S=star, etc.)
  2. Character composition of R2 ring specifically
  3. Period analysis: is there a 12-char repeating structure?
  4. p/f distribution: hemispheric pattern?
  5. 'x' usage: where does it appear (only on f57v?)
  6. Check zodiac folios for the same primitives
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript


def main():
    tx = Transcript()
    f57v_tokens = []
    for tok in tx.all(h_only=True):
        if tok.folio == 'f57v' and tok.word and not tok.is_uncertain:
            f57v_tokens.append(tok)
    print(f"f57v: {len(f57v_tokens)} H-track tokens")

    # Group by placement code prefix (P / R / S / C / L)
    by_placement = defaultdict(list)
    for tok in f57v_tokens:
        prefix = tok.placement[0] if tok.placement else '?'
        by_placement[prefix].append(tok)
    print("\nPlacement code distribution:")
    for k in sorted(by_placement.keys()):
        print(f"  {k}: {len(by_placement[k])} tokens")

    # Look at R-prefix (ring) tokens by full placement code
    print("\nRing-token placement codes:")
    by_full_placement = defaultdict(list)
    for tok in f57v_tokens:
        if tok.placement and tok.placement.startswith('R'):
            by_full_placement[tok.placement].append(tok)
    for k in sorted(by_full_placement.keys()):
        toks = by_full_placement[k]
        print(f"  {k}: {len(toks)} tokens — {' '.join(t.word for t in toks[:30])}")

    # Token length distribution
    lens = Counter(len(t.word) for t in f57v_tokens)
    print(f"\nToken length distribution:")
    for L in sorted(lens.keys()):
        print(f"  L={L}: {lens[L]}")

    # Character composition
    chars = Counter()
    for t in f57v_tokens:
        chars.update(t.word)
    print(f"\nCharacter frequency (f57v):")
    for c, n in chars.most_common():
        print(f"  {c}: {n}")

    # 'x' usage check across whole corpus
    print("\n'x' character usage across corpus:")
    x_folios = defaultdict(int)
    for tok in tx.all(h_only=True):
        if 'x' in tok.word and not tok.is_uncertain:
            x_folios[tok.folio] += 1
    for f in sorted(x_folios.keys(), key=lambda x: -x_folios[x]):
        print(f"  {f}: {x_folios[f]} tokens with 'x'")

    # 'p' and 'f' usage in f57v specifically
    print(f"\n'p' and 'f' character usage in f57v vs corpus:")
    f57v_p = sum(t.word.count('p') for t in f57v_tokens)
    f57v_f = sum(t.word.count('f') for t in f57v_tokens)
    f57v_total_chars = sum(len(t.word) for t in f57v_tokens)

    all_p, all_f, all_total = 0, 0, 0
    for tok in tx.all(h_only=True):
        if tok.is_uncertain or not tok.word:
            continue
        all_p += tok.word.count('p')
        all_f += tok.word.count('f')
        all_total += len(tok.word)

    print(f"  f57v: p={f57v_p} ({100*f57v_p/max(1,f57v_total_chars):.2f}%) f={f57v_f} ({100*f57v_f/max(1,f57v_total_chars):.2f}%) total chars={f57v_total_chars}")
    print(f"  all : p={all_p} ({100*all_p/max(1,all_total):.2f}%) f={all_f} ({100*all_f/max(1,all_total):.2f}%) total chars={all_total}")
    print(f"  f57v p enrichment: {(f57v_p/max(1,f57v_total_chars)) / (all_p/max(1,all_total)):.2f}x")
    print(f"  f57v f enrichment: {(f57v_f/max(1,f57v_total_chars)) / (all_f/max(1,all_total)):.2f}x")

    # Test 12-period hypothesis on R-ring tokens
    if 'R' in by_placement:
        print(f"\n12-period hypothesis test on R-prefix tokens:")
        # All R-ring tokens in order they appear
        r_tokens = [t.word for t in by_placement['R']]
        print(f"  Total R-ring tokens: {len(r_tokens)}")
        # Look at R2 specifically (most-cited)
        for ring_code in sorted(by_full_placement.keys()):
            r_seq = [t.word for t in by_full_placement[ring_code]]
            if len(r_seq) < 6:
                continue
            print(f"\n  {ring_code} sequence ({len(r_seq)} tokens):")
            # Print as 12-wide grid
            for i in range(0, len(r_seq), 12):
                row = r_seq[i:i+12]
                print(f"    pos {i:>2}-{i+len(row)-1:>2}: {' '.join(f'{w:>4s}' for w in row)}")
            # Length pattern within period
            if len(r_seq) >= 12:
                period_lens = [len(r_seq[i % len(r_seq)]) for i in range(12)]
                print(f"    First-12 lengths: {period_lens}")
                # Check periodicity: do lengths repeat?
                # Compute autocorrelation at lag 12
                if len(r_seq) >= 24:
                    matches = sum(1 for i in range(12) if i+12 < len(r_seq) and r_seq[i] == r_seq[i+12])
                    print(f"    Same-token at lag 12: {matches}/12")

    # Compare to other AZC folios with R-rings
    print(f"\nOther AZC folios with R-rings (for comparison):")
    azc_folios_with_rings = defaultdict(list)
    for tok in tx.all(h_only=True):
        if tok.is_uncertain or not tok.word:
            continue
        if tok.placement and tok.placement.startswith('R'):
            azc_folios_with_rings[tok.folio].append(tok)
    for f in sorted(azc_folios_with_rings.keys()):
        if f == 'f57v':
            continue
        toks = azc_folios_with_rings[f]
        if len(toks) < 5:
            continue
        # Show length distribution and char composition for comparison
        lens = Counter(len(t.word) for t in toks)
        print(f"  {f}: n={len(toks)}, lengths={dict(lens)}")


if __name__ == '__main__':
    main()
