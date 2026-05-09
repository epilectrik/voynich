#!/usr/bin/env python3
"""
Phase 691.x: Voynichese Turing Test.

Generate N synthetic Voynich lines using our trained LM. Mix with N real
H-track test lines. Score all under the LM. Can the LM distinguish its own
samples from real Voynich?

If real and synthetic score similarly: model has captured the distribution
If real scores notably better: model misses something
If synthetic scores BETTER: model is over-fit to its own preferences

Also use simple statistical tests:
  - Mann-Whitney U on bpc distributions
  - Linear classifier on bpc + token-length features
"""
import argparse
import functools
import json
import math
import random
import sys
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from talk_to_voynich import load_lm, scheduled_token_generate
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID)


def score_line(model, tokenizer, tokens, device, max_len=256):
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
    L = len(ids)
    positions = [p for p in range(1, L - 1) if ids[p] >= 8]
    if not positions:
        return None
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
    bits = []
    for bi, p in enumerate(positions):
        lp = float(all_lp[bi, p, ids_arr[p]])
        bits.append(-lp / math.log(2))
    return float(np.mean(bits))


def generate_synthetic_lines(model, tokenizer, device, n=200, seed=691):
    """Generate N synthetic Voynich lines via scheduled-token generation."""
    rng = random.Random(seed)
    samples = []
    for i in range(n):
        n_tokens = rng.randint(4, 12)
        gen_text = scheduled_token_generate(
            model, tokenizer, device, n_tokens=n_tokens,
            temperature=0.7, seed=seed + i,
        )
        samples.append(gen_text.split())
    return samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--n-real', type=int, default=200)
    parser.add_argument('--n-synthetic', type=int, default=200)
    args = parser.parse_args()

    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    print("Loading Voynich LM...")
    model, tokenizer = load_lm(device=device)

    # Real test lines
    real_lines = []
    with open(PHASE_DIR / 'data' / 'corpus_test.jsonl', encoding='utf-8') as f:
        for line in f:
            real_lines.append(json.loads(line))
    rng = random.Random(691)
    rng.shuffle(real_lines)
    real_lines = real_lines[:args.n_real]
    real_token_lists = [r['tokens'] for r in real_lines if r['tokens']]
    print(f"Real lines: {len(real_token_lists)}")

    # Synthetic lines
    print("Generating synthetic lines...")
    synth_token_lists = generate_synthetic_lines(model, tokenizer, device, args.n_synthetic)
    synth_token_lists = [t for t in synth_token_lists if t]
    print(f"Synthetic lines: {len(synth_token_lists)}")

    # Score both
    print("\nScoring all lines under Voynich LM...")
    real_bpc = []
    for tokens in real_token_lists:
        b = score_line(model, tokenizer, tokens, device)
        if b is not None:
            real_bpc.append(b)
    synth_bpc = []
    for tokens in synth_token_lists:
        b = score_line(model, tokenizer, tokens, device)
        if b is not None:
            synth_bpc.append(b)
    real_bpc = np.array(real_bpc)
    synth_bpc = np.array(synth_bpc)

    print(f"\n=== Bits-per-char distributions ===")
    print(f"  {'set':<10s}  {'n':>5s}  {'mean':>6s}  {'std':>6s}  {'median':>6s}  {'min':>6s}  {'max':>6s}")
    print(f"  {'real':<10s}  {len(real_bpc):>5d}  {real_bpc.mean():>6.3f}  {real_bpc.std():>6.3f}  {np.median(real_bpc):>6.3f}  {real_bpc.min():>6.3f}  {real_bpc.max():>6.3f}")
    print(f"  {'synthetic':<10s}  {len(synth_bpc):>5d}  {synth_bpc.mean():>6.3f}  {synth_bpc.std():>6.3f}  {np.median(synth_bpc):>6.3f}  {synth_bpc.min():>6.3f}  {synth_bpc.max():>6.3f}")

    # Statistical tests
    from scipy import stats
    u_stat, p_value = stats.mannwhitneyu(real_bpc, synth_bpc, alternative='two-sided')
    print(f"\n  Mann-Whitney U: U={u_stat:.0f}  p={p_value:.4f}")
    if p_value < 0.001:
        print(f"    DISTINGUISHABLE at p<0.001 — model output differs from real distribution")
    elif p_value < 0.05:
        print(f"    weakly distinguishable (p<0.05)")
    else:
        print(f"    NOT statistically distinguishable — synthetic and real same distribution")

    # Effect size: which scores lower?
    diff = synth_bpc.mean() - real_bpc.mean()
    pct = diff / real_bpc.mean() * 100
    if abs(pct) < 5:
        print(f"  Effect size: |Δ|={abs(diff):.3f} bpc ({abs(pct):.1f}%) — negligible")
    elif diff < 0:
        print(f"  Synthetic is {-pct:.1f}% LOWER bpc than real — model over-fit to its own preferences")
    else:
        print(f"  Real is {pct:.1f}% LOWER bpc than synthetic — model misses some real-data structure")

    # Try a simple classifier: can we distinguish using just bpc?
    all_bpc = np.concatenate([real_bpc, synth_bpc])
    labels = np.array([0] * len(real_bpc) + [1] * len(synth_bpc))
    # Find optimal threshold
    sorted_bpc = np.sort(all_bpc)
    best_acc = 0.5
    best_threshold = None
    for t in sorted_bpc:
        preds = (all_bpc >= t).astype(int)
        acc = max((preds == labels).mean(), (preds == 1 - labels).mean())
        if acc > best_acc:
            best_acc = acc
            best_threshold = t
    print(f"\n  Best single-feature classifier accuracy: {best_acc:.3f}")
    print(f"    (chance = 0.5 = unable to distinguish)")
    if best_acc < 0.55:
        print(f"    INDISTINGUISHABLE — model output passes the Turing test")
    elif best_acc < 0.70:
        print(f"    weakly distinguishable (~{int(best_acc*100)}% accuracy)")
    else:
        print(f"    distinguishable")

    # Show example real and synthetic at various surprise levels
    print(f"\n=== Sample comparison ===")
    real_pairs = sorted(zip(real_bpc, real_token_lists), key=lambda x: x[0])
    synth_pairs = sorted(zip(synth_bpc, synth_token_lists), key=lambda x: x[0])
    print(f"Lowest-bpc REAL (most stereotypical): {' '.join(real_pairs[0][1])} [bpc={real_pairs[0][0]:.3f}]")
    print(f"Lowest-bpc SYNTH (best generation):   {' '.join(synth_pairs[0][1])} [bpc={synth_pairs[0][0]:.3f}]")
    print(f"Median-bpc REAL:                      {' '.join(real_pairs[len(real_pairs)//2][1])} [bpc={real_pairs[len(real_pairs)//2][0]:.3f}]")
    print(f"Median-bpc SYNTH:                     {' '.join(synth_pairs[len(synth_pairs)//2][1])} [bpc={synth_pairs[len(synth_pairs)//2][0]:.3f}]")
    print(f"Highest-bpc REAL (most anomalous):    {' '.join(real_pairs[-1][1])} [bpc={real_pairs[-1][0]:.3f}]")
    print(f"Highest-bpc SYNTH (worst gen):        {' '.join(synth_pairs[-1][1])} [bpc={synth_pairs[-1][0]:.3f}]")

    out = {
        'real_bpc_mean': float(real_bpc.mean()),
        'synthetic_bpc_mean': float(synth_bpc.mean()),
        'real_bpc_std': float(real_bpc.std()),
        'synthetic_bpc_std': float(synth_bpc.std()),
        'mannwhitney_p': float(p_value),
        'best_classifier_accuracy': float(best_acc),
        'best_threshold': float(best_threshold) if best_threshold is not None else None,
        'distinguishable': bool(p_value < 0.001 and best_acc > 0.7),
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'turing_test.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
