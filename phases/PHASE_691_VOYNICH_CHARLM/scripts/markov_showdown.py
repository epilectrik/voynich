#!/usr/bin/env python3
"""
Phase 691.x: Markov chain vs transformer showdown.

Train char-level n-gram Markov chains on Voynich H-track training set.
Compare their bits-per-char to our 4.8M-param transformer's bpc on the test set.

Question: How much of Voynich's predictability comes from local statistics
vs deeper structure?

If n-gram nearly matches transformer (within ~5%): shallow structure
If transformer crushes n-gram (>30%): deep structure exists

This tests crazy-expert's C1025 generative-sufficiency speculation directly.
"""
import argparse
import functools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from talk_to_voynich import load_lm
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID)


def line_to_chars(tokens):
    """Convert a list of tokens to a single char stream with spaces."""
    return ' '.join(tokens)


def train_ngram(lines, order, smooth=0.5):
    """Train an order-N Markov model on character sequences.
    Returns (context_to_char_counts, context_totals, vocab_size)."""
    counts = defaultdict(Counter)
    totals = Counter()
    vocab = set()
    for tokens in lines:
        s = line_to_chars(tokens)
        # Pad with start markers
        padded = '\x01' * (order - 1) + s + '\x02'
        for c in padded:
            vocab.add(c)
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            ch = padded[i]
            counts[ctx][ch] += 1
            totals[ctx] += 1
    return counts, totals, len(vocab)


def ngram_bits_per_char(lines, counts, totals, vocab_size, order, smooth=0.5):
    """Compute mean bits-per-char for the given n-gram model on test lines."""
    total_bits = 0.0
    total_chars = 0
    for tokens in lines:
        s = line_to_chars(tokens)
        if not s:
            continue
        padded = '\x01' * (order - 1) + s + '\x02'
        for i in range(order - 1, len(padded)):
            ctx = padded[i - (order - 1):i]
            ch = padded[i]
            ch_count = counts.get(ctx, Counter()).get(ch, 0)
            ctx_total = totals.get(ctx, 0)
            # Laplace smoothing
            prob = (ch_count + smooth) / (ctx_total + smooth * vocab_size)
            # Only count content chars + spaces (not start/end markers) for fair compare
            if ch in ('\x01', '\x02'):
                continue
            total_bits += -math.log2(max(prob, 1e-12))
            total_chars += 1
    return total_bits / max(1, total_chars), total_chars


def transformer_bits_per_char(model, tokenizer, test_lines, device, max_lines=200):
    """Compute mean bits-per-char on test lines using the transformer.
    Uses pseudo-likelihood: mask each char, predict, take its log-prob."""
    total_bits = 0.0
    total_chars = 0
    for rec in test_lines[:max_lines]:
        tokens = rec['tokens']
        if not tokens:
            continue
        ids = [CLS_ID]
        for ti, tok in enumerate(tokens):
            if ti > 0:
                ids.append(SPACE_ID)
            for ch in tok:
                if ch in tokenizer.token_to_id:
                    ids.append(tokenizer.token_to_id[ch])
        ids.append(SEP_ID)
        L = len(ids)
        if L < 3 or L > 256:
            continue
        # All non-special positions (>= 8) are content, plus SPACE_ID positions
        positions = [p for p in range(1, L - 1) if ids[p] >= 4]  # space + content
        if not positions:
            continue
        batch = torch.tensor([ids[:] for _ in positions], dtype=torch.long, device=device)
        for bi, p in enumerate(positions):
            batch[bi, p] = MASK_ID
        attn = torch.zeros(batch.shape, dtype=torch.bool, device=device)
        with torch.no_grad():
            all_lp = []
            for s in range(0, batch.shape[0], 32):
                logits = model(batch[s:s + 32], attn[s:s + 32])
                all_lp.append(torch.log_softmax(logits, dim=-1).cpu().numpy())
            all_lp = np.concatenate(all_lp, axis=0)
        ids_arr = np.array(ids)
        for bi, p in enumerate(positions):
            lp = float(all_lp[bi, p, ids_arr[p]])
            total_bits += -lp / math.log(2)
            total_chars += 1
    return total_bits / max(1, total_chars), total_chars


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--orders', default='2,3,4,5,6,7')
    parser.add_argument('--n-test-lines', type=int, default=200)
    args = parser.parse_args()

    # Load corpora (matched to LM training splits)
    train_path = PHASE_DIR / 'data' / 'corpus_train.jsonl'
    test_path = PHASE_DIR / 'data' / 'corpus_test.jsonl'
    train_lines = []
    with open(train_path, encoding='utf-8') as f:
        for line in f:
            train_lines.append(json.loads(line)['tokens'])
    test_lines_full = []
    with open(test_path, encoding='utf-8') as f:
        for line in f:
            test_lines_full.append(json.loads(line))
    test_token_lists = [r['tokens'] for r in test_lines_full]
    print(f"Train: {len(train_lines)} lines, Test: {len(test_token_lists)} lines")

    # Train and evaluate Markov chains
    orders = [int(x) for x in args.orders.split(',')]
    print(f"\n{'order':>5s}  {'bpc':>6s}  {'n_chars':>8s}  {'note':>20s}")
    print('-' * 50)
    ngram_results = {}
    for order in orders:
        counts, totals, vocab_size = train_ngram(train_lines, order)
        bpc, n = ngram_bits_per_char(test_token_lists, counts, totals, vocab_size, order)
        ngram_results[order] = bpc
        n_unique_contexts = len(counts)
        print(f"  {order:>3d}   {bpc:>6.3f}  {n:>8d}  {n_unique_contexts:>5d} contexts")

    # Run transformer on same test lines
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print(f"\nLoading transformer...")
    model, tokenizer = load_lm(device=device)
    print(f"Computing transformer bpc on {min(args.n_test_lines, len(test_lines_full))} lines...")
    tf_bpc, tf_chars = transformer_bits_per_char(model, tokenizer, test_lines_full, device,
                                                  max_lines=args.n_test_lines)
    print(f"\nTransformer (4.8M params, BERT-style MLM): bpc={tf_bpc:.3f}  ({tf_chars} chars)")

    # Comparison
    print(f"\n=== COMPARISON ===")
    print(f"  Random baseline (log2(28)):    {math.log2(28):.3f} bpc")
    print(f"  Transformer:                    {tf_bpc:.3f} bpc")
    print()
    print(f"  {'order':>5s}  {'ngram bpc':>9s}  {'vs transformer':>14s}  {'savings':>9s}")
    for order, bpc in ngram_results.items():
        diff_pct = ((bpc - tf_bpc) / tf_bpc) * 100
        savings = bpc - tf_bpc
        print(f"  {order:>3d}    {bpc:>9.3f}     {diff_pct:>+10.1f}%   {savings:>+8.3f} bpc")

    # Verdict
    best_ngram = min(ngram_results.values())
    ratio = best_ngram / tf_bpc
    print(f"\n=== VERDICT ===")
    print(f"  Best n-gram bpc: {best_ngram:.3f}")
    print(f"  Transformer bpc: {tf_bpc:.3f}")
    print(f"  N-gram / Transformer ratio: {ratio:.3f}")
    if ratio < 1.05:
        print(f"  → SHALLOW STRUCTURE: n-gram nearly matches transformer.")
        print(f"    Voynich's compressibility is largely local. C1025 generative sufficiency supported.")
    elif ratio < 1.30:
        print(f"  → MIXED: transformer captures {(ratio - 1) * 100:.0f}% additional structure beyond n-gram.")
        print(f"    Some long-range dependencies, but most structure is local.")
    else:
        print(f"  → DEEP STRUCTURE: transformer captures {(ratio - 1) * 100:.0f}% structure beyond best n-gram.")
        print(f"    Long-range dependencies present. Voynich is not a simple Markov chain.")

    # Save
    out = {
        'transformer_bpc': float(tf_bpc),
        'ngram_results': {str(k): float(v) for k, v in ngram_results.items()},
        'best_ngram_bpc': float(best_ngram),
        'ratio_best_ngram_to_transformer': float(ratio),
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'markov_showdown.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
