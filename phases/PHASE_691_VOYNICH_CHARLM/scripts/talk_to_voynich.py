#!/usr/bin/env python3
"""
Phase 691.x: Interactive interface to the trained char-LMs.

Modes:
  generate N               -- sample N synthetic Voynich lines (Gibbs MLM sampling)
  complete <text>          -- complete a partial line, suggest next-token candidates
  score <text>             -- per-token plausibility scoring (mean bits/char)
  compare <text>           -- show A-LM vs B-LM perplexity for the same text
  interactive              -- REPL mode

Demonstrates what the trained Voynich char-LM "knows" about Voynichese.
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import CharLM
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID)


def load_lm(suffix='', subdir='', device='cpu', variant='without_tag', seed=691):
    if subdir:
        tok_path = PHASE_DIR / 'data' / subdir / 'tokenizer.json'
    else:
        tok_path = PHASE_DIR / 'data' / 'tokenizer.json'
    tokenizer = CharTokenizer.load(tok_path)
    ckpt_path = PHASE_DIR / 'results' / 'training' / f'{variant}_seed{seed}{suffix}' / 'checkpoints' / 'best.pt'
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model = CharLM(vocab_size=tokenizer.vocab_size).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()
    return model, tokenizer


def encode_text(tokenizer, text, max_len=256):
    """Encode whitespace-separated tokens to IDs."""
    tokens = text.strip().split()
    ids = [CLS_ID]
    for ti, tok in enumerate(tokens):
        if ti > 0:
            ids.append(SPACE_ID)
        for ch in tok:
            if ch in tokenizer.token_to_id:
                ids.append(tokenizer.token_to_id[ch])
    ids.append(SEP_ID)
    if len(ids) > max_len:
        ids = ids[:max_len - 1] + [SEP_ID]
    return ids, tokens


def decode_ids(tokenizer, ids):
    """Convert IDs back to whitespace-separated token string."""
    return tokenizer.decode(ids).strip()


def scheduled_token_generate(model, tokenizer, device, n_tokens=5,
                             token_lengths=None, n_iter=300, k_per_step=3,
                             temperature=0.7, top_k=15, seed=None):
    """Generate Voynichese by scheduling token boundaries first, then filling chars.

    Approach:
      1. Decide structure: n_tokens tokens, each with a length sampled from
         a Voynich-realistic distribution (or use provided token_lengths)
      2. Pre-place SPACE_IDs at the token boundaries
      3. Iteratively refine ONLY the content positions; SPACE positions are frozen
      4. Many iterations let the content distribution converge

    This avoids the chicken-and-egg problem where the model never predicts SPACE
    because consecutive content chars look more locally probable.
    """
    if seed is not None:
        torch.manual_seed(seed)
        random.seed(seed)

    # Default token length distribution: realistic Voynich (mostly 4-7 chars)
    if token_lengths is None:
        # Sample from a Voynich-like distribution: mean ~5.5, range 2-9
        # Roughly: 2:5%, 3:10%, 4:20%, 5:25%, 6:20%, 7:12%, 8:5%, 9:3%
        weights = [0, 0, 5, 10, 20, 25, 20, 12, 5, 3]
        choices = list(range(len(weights)))
        token_lengths = [random.choices(choices, weights=weights)[0] for _ in range(n_tokens)]

    # Build initial sequence with SPACE_IDs at token boundaries
    content_lo, content_hi = 8, tokenizer.vocab_size - 1
    ids = [CLS_ID]
    content_positions = []  # positions to fill with content
    for ti, tlen in enumerate(token_lengths):
        if ti > 0:
            ids.append(SPACE_ID)
        for _ in range(tlen):
            content_positions.append(len(ids))
            ids.append(random.randint(content_lo, content_hi))
    ids.append(SEP_ID)
    L = len(ids)

    # Iteratively refine content positions only
    for it in range(n_iter):
        temp = max(0.5, temperature * (1.0 - it / (2 * n_iter)))
        random.shuffle(content_positions)
        positions = content_positions[:k_per_step]
        for p in positions:
            ids[p] = MASK_ID
        ids_t = torch.tensor([ids], dtype=torch.long, device=device)
        attn = torch.zeros((1, L), dtype=torch.bool, device=device)
        with torch.no_grad():
            logits = model(ids_t, attn)[0]
        for p in positions:
            lp = logits[p].clone()
            valid = torch.full_like(lp, -float('inf'))
            for vi in range(content_lo, content_hi + 1):
                valid[vi] = 0.0
            lp = lp + valid
            if top_k > 0:
                top_vals, _ = lp.topk(min(top_k, lp.numel()))
                kth = top_vals[-1]
                lp = torch.where(lp >= kth, lp, torch.full_like(lp, -float('inf')))
            probs = torch.softmax(lp / temp, dim=-1)
            ids[p] = int(torch.multinomial(probs, 1).item())

    return tokenizer.decode(ids).strip()


def iterative_refinement_generate(model, tokenizer, device, length=30,
                                  n_iter=300, k_per_step=4, temperature=0.7,
                                  top_k=20, seed=None, space_bias=2.5):
    """Generate Voynichese via iterative refinement with SPACE-frequency calibration.

    Procedure:
      1. Initialize with random valid chars + corpus-rate spaces
      2. Per iteration: pick K random positions, mask, forward, sample
      3. Apply SPACE_BIAS to logits so SPACE matches corpus frequency (~13% of positions)
      4. Many iterations let the distribution converge with annealed temperature

    The model under-predicts SPACE because consecutive content chars are locally
    more probable than space. Bias compensates for this in sampling without
    affecting the model's representation of token shapes.
    """
    if seed is not None:
        torch.manual_seed(seed)
        random.seed(seed)

    L = length + 2
    target_space_rate = 0.13
    content_lo, content_hi = 8, tokenizer.vocab_size - 1
    ids = [CLS_ID]
    for i in range(length):
        if random.random() < target_space_rate and i > 0 and ids[-1] != SPACE_ID:
            ids.append(SPACE_ID)
        else:
            ids.append(random.randint(content_lo, content_hi))
    ids.append(SEP_ID)

    for it in range(n_iter):
        temp = max(0.5, temperature * (1.0 - it / (2 * n_iter)))
        all_pos = list(range(1, L - 1))
        random.shuffle(all_pos)
        positions = all_pos[:k_per_step]
        for p in positions:
            ids[p] = MASK_ID
        ids_t = torch.tensor([ids], dtype=torch.long, device=device)
        attn = torch.zeros((1, L), dtype=torch.bool, device=device)
        with torch.no_grad():
            logits = model(ids_t, attn)[0]
        for p in positions:
            lp = logits[p].clone()
            valid = torch.full_like(lp, -float('inf'))
            valid[SPACE_ID] = 0.0
            for vi in range(content_lo, content_hi + 1):
                valid[vi] = 0.0
            prev_id = ids[p - 1] if p > 1 else CLS_ID
            next_id = ids[p + 1] if p < L - 1 else SEP_ID
            if prev_id == SPACE_ID or next_id == SPACE_ID:
                valid[SPACE_ID] = -float('inf')
            if p == 1 or p == L - 2:
                valid[SPACE_ID] = -float('inf')
            lp = lp + valid
            # Apply SPACE bias if it's a valid option
            if valid[SPACE_ID] == 0.0:
                lp[SPACE_ID] = lp[SPACE_ID] + space_bias
            if top_k > 0:
                top_vals, _ = lp.topk(min(top_k, lp.numel()))
                kth = top_vals[-1]
                lp = torch.where(lp >= kth, lp, torch.full_like(lp, -float('inf')))
            probs = torch.softmax(lp / temp, dim=-1)
            ids[p] = int(torch.multinomial(probs, 1).item())

    return tokenizer.decode(ids).strip()


# Keep old name as alias
gibbs_generate = iterative_refinement_generate
autoregressive_generate = iterative_refinement_generate


def complete(model, tokenizer, device, prefix, n_predict=5, top_k=5):
    """Given a partial line, predict the most likely next-token completions."""
    # Encode prefix and add masked positions for n_predict tokens
    prefix_ids = [CLS_ID]
    tokens = prefix.strip().split()
    for ti, tok in enumerate(tokens):
        if ti > 0:
            prefix_ids.append(SPACE_ID)
        for ch in tok:
            if ch in tokenizer.token_to_id:
                prefix_ids.append(tokenizer.token_to_id[ch])

    # Add space + MASK*5 chars + SEP for next-token prediction
    ids = prefix_ids[:]
    if tokens:
        ids.append(SPACE_ID)
    next_token_start = len(ids)
    # Add MASK chars (assume avg token length 5)
    avg_token_len = 5
    ids.extend([MASK_ID] * avg_token_len)
    next_token_end = len(ids)
    ids.append(SEP_ID)

    # Predict each masked position
    ids_t = torch.tensor([ids], dtype=torch.long, device=device)
    attn = torch.zeros((1, len(ids)), dtype=torch.bool, device=device)
    with torch.no_grad():
        logits = model(ids_t, attn)[0]  # (L, V)

    # Get top-K char predictions for each masked position
    print(f"\nPrefix: {prefix!r}")
    print(f"Top-{top_k} predictions for each next character position:")
    for i, p in enumerate(range(next_token_start, next_token_end)):
        log_probs = torch.log_softmax(logits[p], dim=-1)
        # Restrict to content chars + space
        valid_mask = torch.full_like(log_probs, -float('inf'))
        valid_mask[SPACE_ID] = 0.0
        for vi in range(8, tokenizer.vocab_size):
            valid_mask[vi] = 0.0
        log_probs = log_probs + valid_mask
        top_lp, top_idx = log_probs.topk(top_k)
        items = [(tokenizer.id_to_token[int(i)], float(lp))
                 for lp, i in zip(top_lp, top_idx)]
        items_str = ', '.join(f"{t!r}({lp:.2f})" for t, lp in items)
        print(f"  pos {i}: {items_str}")


def score(model, tokenizer, device, text):
    """Per-token surprise scoring (bits/char) using masked-LM pseudo-likelihood."""
    ids, tokens = encode_text(tokenizer, text)
    L = len(ids)
    if L < 3:
        print(f"Too short to score")
        return
    positions = [p for p in range(1, L - 1) if ids[p] >= 8]
    if not positions:
        print(f"No content positions to score")
        return
    batch = torch.tensor([ids[:] for _ in positions], dtype=torch.long, device=device)
    for bi, p in enumerate(positions):
        batch[bi, p] = MASK_ID
    attn = torch.zeros(batch.shape, dtype=torch.bool, device=device)
    with torch.no_grad():
        log_probs_all = []
        for s in range(0, batch.shape[0], 32):
            logits = model(batch[s:s+32], attn[s:s+32])
            log_probs_all.append(torch.log_softmax(logits, dim=-1).cpu().numpy())
        log_probs_all = np.concatenate(log_probs_all, axis=0)
    ids_arr = np.array(ids)
    # Per-position bits
    pos_bits = {}
    for bi, p in enumerate(positions):
        lp = float(log_probs_all[bi, p, ids_arr[p]])
        pos_bits[p] = -lp / math.log(2)

    # Aggregate per token
    print(f"\n{'token':>15s}  {'bits/char':>10s}  {'surprise':>9s}")
    print('-' * 40)
    # Recompute spans
    pos = 1  # past CLS
    total_bits = 0.0
    total_chars = 0
    for ti, tok in enumerate(tokens):
        if ti > 0 and ids[pos] == SPACE_ID:
            pos += 1
        token_bits = []
        for ch in tok:
            if ch in tokenizer.token_to_id and pos < L - 1:
                if pos in pos_bits:
                    token_bits.append(pos_bits[pos])
                pos += 1
        if not token_bits:
            continue
        avg_bpc = float(np.mean(token_bits))
        flag = ' ⚠' if avg_bpc > 2.0 else ('  ★' if avg_bpc < 0.4 else '')
        print(f"  {tok:>15s}  {avg_bpc:>10.3f}  {avg_bpc * len(token_bits):>9.2f}{flag}")
        total_bits += sum(token_bits)
        total_chars += len(token_bits)

    print('-' * 40)
    print(f"  Mean bits/char: {total_bits / max(1, total_chars):.3f}")
    print(f"  Total bits: {total_bits:.2f}  ({total_chars} content chars)")
    # Compare to baseline
    print(f"  (Voynich corpus baseline: ~0.89 bits/char)")
    print(f"  (Random baseline: log2(20) = 4.32 bits/char)")


def compare(text, voynich_lm, voynich_tok, a_lm, a_tok, b_lm, b_tok, device):
    """Score same text under A-LM and B-LM."""
    print(f"\nText: {text!r}")
    print(f"\n{'Model':<12s}  {'mean bits/char':>15s}")
    print('-' * 32)
    for name, m, t in [('Voynich-full', voynich_lm, voynich_tok),
                       ('A-LM', a_lm, a_tok),
                       ('B-LM', b_lm, b_tok)]:
        ids, tokens = encode_text(t, text)
        positions = [p for p in range(1, len(ids) - 1) if ids[p] >= 8]
        if not positions:
            print(f"  {name:<12s}  (cannot score)")
            continue
        batch = torch.tensor([ids[:] for _ in positions], dtype=torch.long, device=device)
        for bi, p in enumerate(positions):
            batch[bi, p] = MASK_ID
        attn = torch.zeros(batch.shape, dtype=torch.bool, device=device)
        with torch.no_grad():
            log_probs_all = []
            for s in range(0, batch.shape[0], 32):
                logits = m(batch[s:s+32], attn[s:s+32])
                log_probs_all.append(torch.log_softmax(logits, dim=-1).cpu().numpy())
            log_probs_all = np.concatenate(log_probs_all, axis=0)
        ids_arr = np.array(ids)
        bits = []
        for bi, p in enumerate(positions):
            lp = float(log_probs_all[bi, p, ids_arr[p]])
            bits.append(-lp / math.log(2))
        print(f"  {name:<12s}  {np.mean(bits):>15.3f}")


def interactive(voynich_lm, voynich_tok, a_lm, a_tok, b_lm, b_tok, device):
    print(f"\n=== Voynichese REPL ===")
    print(f"Trained char-LM (val_loss 0.66, vocab 20). Type Voynich tokens.")
    print(f"Commands:")
    print(f"  > <text>           score the text")
    print(f"  c <text>           complete (predict next token)")
    print(f"  g [length]         generate fresh Voynichese (Gibbs MLM sampling)")
    print(f"  ab <text>          compare A-LM vs B-LM scoring")
    print(f"  q                  quit")
    print()
    while True:
        try:
            line = input("voynich> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line or line == 'q':
            break
        if line.startswith('c '):
            complete(voynich_lm, voynich_tok, device, line[2:].strip())
        elif line.startswith('g'):
            parts = line.split()
            length = int(parts[1]) if len(parts) > 1 else 30
            gen = gibbs_generate(voynich_lm, voynich_tok, device, length=length, temperature=1.0)
            print(f"  Generated: {gen!r}")
        elif line.startswith('ab '):
            compare(line[3:].strip(), voynich_lm, voynich_tok, a_lm, a_tok, b_lm, b_tok, device)
        else:
            score(voynich_lm, voynich_tok, device, line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['generate', 'complete', 'score', 'compare', 'interactive'])
    parser.add_argument('text', nargs='*', help='Input text or count')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--length', type=int, default=30, help='Generation length in chars')
    parser.add_argument('--n', type=int, default=5, help='Number of samples for generate')
    parser.add_argument('--temperature', type=float, default=1.0)
    parser.add_argument('--seed', type=int, default=None)
    args = parser.parse_args()

    device = torch.device(args.device)
    print(f"Loading Voynich LM ({args.device})...")
    voynich_lm, voynich_tok = load_lm(device=device)
    print(f"  vocab: {voynich_tok.vocab_size}")

    if args.mode in ('compare', 'interactive'):
        print(f"Loading A-LM and B-LM...")
        a_lm, a_tok = load_lm('_sectionA', device=device)
        b_lm, b_tok = load_lm('_sectionB', device=device)

    if args.mode == 'generate':
        # Approximate n_tokens from desired length (avg 5.5 chars/token + 1 space)
        n_tokens = max(2, args.length // 7)
        for i in range(args.n):
            seed = (args.seed or 691) + i
            gen = scheduled_token_generate(voynich_lm, voynich_tok, device,
                                           n_tokens=n_tokens,
                                           temperature=args.temperature, seed=seed)
            print(f"  [{i+1}] {gen}")
    elif args.mode == 'complete':
        complete(voynich_lm, voynich_tok, device, ' '.join(args.text))
    elif args.mode == 'score':
        score(voynich_lm, voynich_tok, device, ' '.join(args.text))
    elif args.mode == 'compare':
        compare(' '.join(args.text), voynich_lm, voynich_tok, a_lm, a_tok, b_lm, b_tok, device)
    elif args.mode == 'interactive':
        interactive(voynich_lm, voynich_tok, a_lm, a_tok, b_lm, b_tok, device)


if __name__ == '__main__':
    main()
