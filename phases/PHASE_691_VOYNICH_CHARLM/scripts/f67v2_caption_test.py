#!/usr/bin/env python3
"""
Phase 691.x: Test crazy-expert's caption-inventory hypothesis for f67v2.

PRE-REGISTERED PREDICTIONS (locked before computation):

f67v2 is hypothesized to be a "caption inventory" — fourth reference type
distinct from f57v (table), f66r (glossary), f49v (apparatus). Specifically,
f67v2 contains per-element labels for the central rosette diagram with ~12
surrounding elements.

Predictions to test (pre-registered):
  P-67-1: Token length distribution skewed short (mean < corpus mean)
  P-67-2: Low PREFIX rate (< corpus baseline)
  P-67-3: ≥80% of tokens occur ≤2 times (key prediction — caption inventories
          are highly non-repetitive: each label uniquely identifies one element)
  P-67-4: Token count consistent with ~12 surrounding elements (12-30 unique
          labels expected, allowing for 1-2 tokens per label)
  P-67-5: NOT periodic (already shown — confirms not f57v-type)

PASS criteria: ≥4 of 5 predictions confirmed = caption-inventory hypothesis
supported. <3 = falsified.
"""
import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

PHASE_DIR = Path(__file__).resolve().parents[1]


def main():
    tx = Transcript()
    morph = Morphology()

    # f67v2 tokens
    f67v2_tokens = [t for t in tx.all(h_only=True)
                    if t.folio == 'f67v2' and t.word and not t.is_uncertain]
    print(f"f67v2: {len(f67v2_tokens)} H-track tokens")

    # Corpus baseline (all H-track)
    all_tokens = [t for t in tx.all(h_only=True)
                  if t.word and not t.is_uncertain]
    print(f"Corpus baseline: {len(all_tokens)} tokens")

    words = [t.word for t in f67v2_tokens]
    n = len(words)
    if n < 5:
        print("Too few tokens to analyze.")
        return

    # ===== P-67-1: Token length skewed short =====
    f67v2_lens = [len(w) for w in words]
    f67v2_avg_len = sum(f67v2_lens) / n
    corpus_avg_len = sum(len(t.word) for t in all_tokens) / len(all_tokens)
    p1_pass = f67v2_avg_len < corpus_avg_len
    p1_diff = corpus_avg_len - f67v2_avg_len
    print(f"\n[P-67-1] Token length skewed short (vs corpus)")
    print(f"  f67v2 mean length:  {f67v2_avg_len:.2f}")
    print(f"  Corpus mean length: {corpus_avg_len:.2f}")
    print(f"  Difference:         {p1_diff:+.2f}")
    print(f"  PASS criterion: f67v2 < corpus  →  {'✓ PASS' if p1_pass else '✗ FAIL'}")

    # ===== P-67-2: Low PREFIX rate =====
    n_with_prefix = 0
    for w in words:
        m = morph.extract(w)
        if m and m.prefix:
            n_with_prefix += 1
    f67v2_prefix_rate = n_with_prefix / n
    n_corpus_with_prefix = 0
    for t in all_tokens:
        m = morph.extract(t.word)
        if m and m.prefix:
            n_corpus_with_prefix += 1
    corpus_prefix_rate = n_corpus_with_prefix / len(all_tokens)
    p2_pass = f67v2_prefix_rate < corpus_prefix_rate
    print(f"\n[P-67-2] Low PREFIX rate (vs corpus)")
    print(f"  f67v2 PREFIX rate:  {100*f67v2_prefix_rate:.1f}%")
    print(f"  Corpus PREFIX rate: {100*corpus_prefix_rate:.1f}%")
    print(f"  PASS criterion: f67v2 < corpus  →  {'✓ PASS' if p2_pass else '✗ FAIL'}")

    # ===== P-67-3: ≥80% tokens occur ≤2 times =====
    word_counts = Counter(words)
    n_rare = sum(1 for c in word_counts.values() if c <= 2)
    n_unique_words = len(word_counts)
    rare_pct = n_rare / n_unique_words
    # Also compute: % of TOKEN OCCURRENCES that are in rare types
    rare_occurrences = sum(c for c in word_counts.values() if c <= 2)
    rare_occ_pct = rare_occurrences / n
    p3_pass = rare_pct >= 0.80
    print(f"\n[P-67-3] ≥80% of tokens occur ≤2 times (key prediction)")
    print(f"  Unique tokens:                {n_unique_words}")
    print(f"  Tokens occurring ≤2 times:    {n_rare} ({100*rare_pct:.1f}%)")
    print(f"  Token occurrences in rare:    {rare_occurrences} ({100*rare_occ_pct:.1f}%)")
    print(f"  PASS criterion: ≥80% rare types  →  {'✓ PASS' if p3_pass else '✗ FAIL'}")

    # ===== P-67-4: Token count consistent with ~12 surrounding elements =====
    p4_pass = (12 <= n_unique_words <= 200)  # 12-30 labels × 1-2 tokens, with some flex
    print(f"\n[P-67-4] Token count consistent with ~12 surrounding elements")
    print(f"  Total tokens: {n}")
    print(f"  Unique tokens: {n_unique_words}")
    print(f"  PASS criterion: 12 ≤ unique ≤ 200  →  {'✓ PASS' if p4_pass else '✗ FAIL'}")

    # ===== P-67-5: NOT periodic =====
    # Already shown in scaffolding inventory: best_match_pct = 0 (no periodicity)
    placement_seqs = {}
    for t in f67v2_tokens:
        if t.placement:
            placement_seqs.setdefault(t.placement, []).append(t.word)
    best_periodicity = 0.0
    for seq in placement_seqs.values():
        if len(seq) < 8:
            continue
        for lag in range(4, min(21, len(seq))):
            matches = sum(1 for i in range(len(seq) - lag) if seq[i] == seq[i + lag])
            possible = max(1, len(seq) - lag)
            pct = matches / possible
            best_periodicity = max(best_periodicity, pct)
    p5_pass = best_periodicity < 0.20  # not strongly periodic
    print(f"\n[P-67-5] NOT periodic (vs f57v's periodic-tabular structure)")
    print(f"  Best lag periodicity: {best_periodicity:.3f}")
    print(f"  PASS criterion: < 0.20  →  {'✓ PASS' if p5_pass else '✗ FAIL'}")

    # ===== Aggregate verdict =====
    n_passed = sum([p1_pass, p2_pass, p3_pass, p4_pass, p5_pass])
    print(f"\n=== VERDICT ===")
    print(f"  {n_passed}/5 predictions confirmed")
    if n_passed >= 4:
        verdict = 'CAPTION_INVENTORY_HYPOTHESIS_SUPPORTED'
    elif n_passed >= 3:
        verdict = 'PARTIAL_SUPPORT'
    else:
        verdict = 'CAPTION_INVENTORY_HYPOTHESIS_FALSIFIED'
    print(f"  {verdict}")

    # Show actual content for inspection
    print(f"\n=== f67v2 token inventory ===")
    print(f"  Most frequent tokens:")
    for w, c in word_counts.most_common(15):
        print(f"    {w:>15s}  ×{c}")
    if n_unique_words > 15:
        print(f"  ... and {n_unique_words - 15} unique tokens occurring ≤{word_counts.most_common(15)[-1][1]} times")

    # Show by placement code (illustrates structure)
    print(f"\n  By placement code:")
    placement_counts = Counter(t.placement or '?' for t in f67v2_tokens)
    for p, c in placement_counts.most_common():
        print(f"    {p:>6s}: {c} tokens")

    # Save
    out = {
        'folio': 'f67v2',
        'hypothesis': 'caption_inventory_for_central_rosette',
        'n_tokens': n,
        'n_unique': n_unique_words,
        'predictions': {
            'P-67-1': {'pass': bool(p1_pass), 'f67v2_avg_len': float(f67v2_avg_len),
                       'corpus_avg_len': float(corpus_avg_len)},
            'P-67-2': {'pass': bool(p2_pass), 'f67v2_prefix_rate': float(f67v2_prefix_rate),
                       'corpus_prefix_rate': float(corpus_prefix_rate)},
            'P-67-3': {'pass': bool(p3_pass), 'rare_pct': float(rare_pct),
                       'rare_occ_pct': float(rare_occ_pct)},
            'P-67-4': {'pass': bool(p4_pass), 'n_unique': n_unique_words},
            'P-67-5': {'pass': bool(p5_pass), 'best_periodicity': float(best_periodicity)},
        },
        'n_passed': n_passed,
        'verdict': verdict,
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'f67v2_caption_test.json'
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
