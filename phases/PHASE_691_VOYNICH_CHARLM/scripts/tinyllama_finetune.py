#!/usr/bin/env python3
"""
Phase 691.x: Fine-tune TinyLlama on 90% of Voynich, evaluate on 10%.

Per crazy-expert: "C2015/C2018 predict large perplexity drops should be
achievable. If massive drop → real grammar; small drop → surface regularity only."

Hypothesis: Voynich has substantial learnable structure beyond what pretrained
NL priors capture. After fine-tuning, perplexity should drop dramatically on
held-out Voynich relative to base model perplexity.

Pre-registered prediction:
  Held-out perplexity drops >50% from base → significant learnable structure
  Drop 20-50% → modest structure
  Drop <20% → only surface regularity
"""
import argparse
import functools
import json
import math
import random
import sys
import time
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='TinyLlama/TinyLlama-1.1B-Chat-v1.0')
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch-size', type=int, default=4)
    parser.add_argument('--lr', type=float, default=2e-5)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--max-length', type=int, default=128)
    args = parser.parse_args()

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from torch.utils.data import Dataset, DataLoader

    device = args.device if torch.cuda.is_available() else 'cpu'
    print(f"Loading {args.model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    # bf16 for stable fine-tuning (fp16 NaNs are common with small batches)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16).to(device)
    print(f"  Params: {sum(p.numel() for p in model.parameters()):,}")

    # Load Voynich corpus (use the train/val/test splits we already built)
    train_lines, test_lines = [], []
    for split, target in [('train', train_lines), ('val', train_lines), ('test', test_lines)]:
        path = PHASE_DIR / 'data' / f'corpus_{split}.jsonl'
        with open(path, encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                if r['tokens']:
                    target.append(' '.join(r['tokens']))
    print(f"\nTrain lines: {len(train_lines)}, Test lines: {len(test_lines)}")

    # Compute base model perplexity on test set
    def eval_perplexity(model, lines, label):
        losses = []
        n_total_tokens = 0
        with torch.no_grad():
            for text in lines:
                enc = tokenizer(text, return_tensors='pt', truncation=True,
                                max_length=args.max_length)
                ids = enc['input_ids'].to(device)
                if ids.shape[1] < 2:
                    continue
                out = model(ids, labels=ids)
                losses.append(out.loss.item())
                n_total_tokens += ids.shape[1] - 1
        mean_loss = float(np.mean(losses))
        bpt = mean_loss / math.log(2)
        ppl = math.exp(min(20, mean_loss))
        print(f"  {label}: bpt={bpt:.3f}  ppl={ppl:.1f}  ({n_total_tokens} tokens)")
        return mean_loss, bpt, ppl

    print(f"\n=== Base model perplexity ===")
    base_loss, base_bpt, base_ppl = eval_perplexity(model, test_lines, 'base on test')

    # Fine-tune
    print(f"\n=== Fine-tuning ===")
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    model.train()

    rng = random.Random(691)
    rng.shuffle(train_lines)

    start = time.time()
    n_steps = 0
    for epoch in range(args.epochs):
        rng.shuffle(train_lines)
        epoch_losses = []
        for i in range(0, len(train_lines), args.batch_size):
            batch = train_lines[i:i+args.batch_size]
            enc = tokenizer(batch, return_tensors='pt', padding=True,
                            truncation=True, max_length=args.max_length)
            ids = enc['input_ids'].to(device)
            mask = enc['attention_mask'].to(device)
            # Labels: -100 for pad, else input_ids
            labels = ids.clone()
            labels[mask == 0] = -100
            out = model(ids, attention_mask=mask, labels=labels)
            loss = out.loss
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_losses.append(loss.item())
            n_steps += 1
            if n_steps % 50 == 0:
                elapsed = time.time() - start
                print(f"  step {n_steps}: loss={np.mean(epoch_losses[-50:]):.3f}  elapsed={elapsed:.0f}s")
        avg_epoch = float(np.mean(epoch_losses))
        print(f"  Epoch {epoch+1}/{args.epochs}: avg_loss={avg_epoch:.3f}")

    # Eval after fine-tuning
    model.eval()
    print(f"\n=== Post-finetune perplexity ===")
    ft_loss, ft_bpt, ft_ppl = eval_perplexity(model, test_lines, 'fine-tuned on test')

    # Comparison
    drop_pct = 100 * (base_bpt - ft_bpt) / base_bpt
    ppl_ratio = base_ppl / ft_ppl
    print(f"\n=== Results ===")
    print(f"  Base perplexity:        {base_ppl:.1f} (bpt {base_bpt:.3f})")
    print(f"  Fine-tuned perplexity:  {ft_ppl:.1f} (bpt {ft_bpt:.3f})")
    print(f"  Bits-per-token drop:    {drop_pct:.1f}%")
    print(f"  Perplexity ratio:       {ppl_ratio:.1f}x")

    if drop_pct >= 50:
        verdict = 'LARGE_DROP_REAL_GRAMMAR'
        msg = "Significant learnable structure beyond surface regularity"
    elif drop_pct >= 20:
        verdict = 'MODERATE_DROP'
        msg = "Some learnable structure, partly surface regularity"
    else:
        verdict = 'SMALL_DROP_SURFACE_ONLY'
        msg = "Mostly surface regularity, little deep structure to learn"
    print(f"  Verdict: {verdict}")
    print(f"  Interpretation: {msg}")

    out = {
        'model': args.model,
        'epochs': args.epochs,
        'lr': args.lr,
        'n_train_lines': len(train_lines),
        'n_test_lines': len(test_lines),
        'base_perplexity': base_ppl,
        'base_bpt': base_bpt,
        'finetune_perplexity': ft_ppl,
        'finetune_bpt': ft_bpt,
        'bpt_drop_pct': drop_pct,
        'perplexity_ratio': ppl_ratio,
        'verdict': verdict,
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'tinyllama_finetune.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
