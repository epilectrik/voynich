#!/usr/bin/env python3
"""
Train Voynich char-LM with masked character modeling.

Usage:
  python train.py --variant without_tag --epochs 100
  python train.py --variant with_tag --epochs 100

Locked per Phase 691.1:
  - 15% mask rate (80% [MASK], 10% random, 10% identity)
  - AdamW, lr 5e-4, weight decay 0.01
  - Linear warmup 1000 steps, cosine decay
  - Batch size 64
  - Max seq len 256

N=10 seeds for aggregate metrics required by pre-registration.
"""
import argparse
import functools
import json
import math
import sys
import time
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import CharLM, count_params
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID,
                       SECTION_TAG_IDS)


class MLMDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, with_tag=False, max_len=256):
        self.records = []
        with open(jsonl_path, encoding='utf-8') as f:
            for line in f:
                self.records.append(json.loads(line))
        self.tokenizer = tokenizer
        self.with_tag = with_tag
        self.max_len = max_len

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        r = self.records[idx]
        ids = self.tokenizer.encode_line(r['tokens'], r['section'],
                                         with_tag=self.with_tag, max_len=self.max_len)
        return torch.tensor(ids, dtype=torch.long)


def collate_pad(batch, pad_id=PAD_ID):
    lens = [len(x) for x in batch]
    L = max(lens)
    out = torch.full((len(batch), L), pad_id, dtype=torch.long)
    for i, x in enumerate(batch):
        out[i, :len(x)] = x
    attn_mask = (out == pad_id)
    return out, attn_mask


def apply_mlm_mask(ids, vocab_size, mask_rate=0.15, mask_id=MASK_ID,
                   pad_id=PAD_ID, special_max_id=7, rng=None):
    """
    BERT-style MLM masking on a batch [B, L].
    Per pre-reg: 15% rate, 80% mask, 10% random char, 10% identity.

    Only masks content positions (id >= 8). Special tokens never masked.
    """
    if rng is None:
        rng = torch.Generator()
    B, L = ids.shape
    can_mask = (ids > special_max_id) & (ids != pad_id)

    rand = torch.rand(B, L, generator=rng)
    selected = (rand < mask_rate) & can_mask

    sub_rand = torch.rand(B, L, generator=rng)
    do_mask = selected & (sub_rand < 0.8)
    do_random = selected & (sub_rand >= 0.8) & (sub_rand < 0.9)
    do_identity = selected & (sub_rand >= 0.9)

    masked_ids = ids.clone()
    masked_ids[do_mask] = mask_id
    if do_random.any():
        # Random replacement in content range only [special_max_id+1, vocab_size-1]
        n_random = do_random.sum().item()
        rand_chars = torch.randint(
            special_max_id + 1, vocab_size, (n_random,), generator=rng,
        )
        masked_ids[do_random] = rand_chars
    # do_identity: leave token unchanged but include in loss

    # Loss target: -100 where NOT a masked position; else original ID
    target = ids.clone()
    target[~selected] = -100  # cross_entropy ignore_index

    return masked_ids, target, selected


def get_lr(step, warmup, total_steps, base_lr):
    if step < warmup:
        return base_lr * (step + 1) / warmup
    progress = (step - warmup) / max(1, total_steps - warmup)
    return base_lr * 0.5 * (1.0 + math.cos(math.pi * progress))


def evaluate(model, loader, vocab_size, device, mlm_rng):
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for ids, attn_mask in loader:
            ids = ids.to(device)
            attn_mask = attn_mask.to(device)
            masked, target, selected = apply_mlm_mask(
                ids.cpu(), vocab_size, rng=mlm_rng
            )
            masked = masked.to(device)
            target = target.to(device)
            logits = model(masked, attn_mask)
            loss = F.cross_entropy(logits.view(-1, vocab_size), target.view(-1),
                                   ignore_index=-100, reduction='sum')
            n_target = (target != -100).sum().item()
            total_loss += loss.item()
            total_tokens += max(1, n_target)
    avg = total_loss / total_tokens
    ppl = math.exp(min(20, avg))
    model.train()
    return avg, ppl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=['without_tag', 'with_tag'], default='without_tag')
    parser.add_argument('--seed', type=int, default=691)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--lr', type=float, default=5e-4)
    parser.add_argument('--weight-decay', type=float, default=0.01)
    parser.add_argument('--warmup-steps', type=int, default=1000)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--output-dir', type=Path,
                        default=PHASE_DIR / 'results' / 'training')
    args = parser.parse_args()

    out_dir = args.output_dir / f'{args.variant}_seed{args.seed}'
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = out_dir / 'checkpoints'
    ckpt_dir.mkdir(exist_ok=True)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    # Load tokenizer
    tokenizer = CharTokenizer.load(PHASE_DIR / 'data' / 'tokenizer.json')
    print(f"Vocab size: {tokenizer.vocab_size}")

    # Datasets
    with_tag = (args.variant == 'with_tag')
    train_ds = MLMDataset(PHASE_DIR / 'data' / 'corpus_train.jsonl', tokenizer, with_tag=with_tag)
    val_ds = MLMDataset(PHASE_DIR / 'data' / 'corpus_val.jsonl', tokenizer, with_tag=with_tag)
    print(f"Train: {len(train_ds)}, Val: {len(val_ds)}")

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              collate_fn=collate_pad, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            collate_fn=collate_pad, num_workers=0)

    # Model
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    model = CharLM(vocab_size=tokenizer.vocab_size).to(device)
    n_params = count_params(model)
    print(f"Params: {n_params:,}")
    print(f"Device: {device}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr,
                                  weight_decay=args.weight_decay,
                                  betas=(0.9, 0.95))

    total_steps = args.epochs * len(train_loader)
    print(f"Total steps: {total_steps:,}")

    mlm_rng = torch.Generator().manual_seed(args.seed)
    best_val_loss = float('inf')
    history = []
    step = 0
    start = time.time()

    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        total_tok = 0
        for ids, attn_mask in train_loader:
            lr = get_lr(step, args.warmup_steps, total_steps, args.lr)
            for g in optimizer.param_groups:
                g['lr'] = lr

            ids = ids.to(device)
            attn_mask = attn_mask.to(device)
            masked_cpu, target_cpu, sel = apply_mlm_mask(ids.cpu(), tokenizer.vocab_size, rng=mlm_rng)
            masked = masked_cpu.to(device)
            target = target_cpu.to(device)

            logits = model(masked, attn_mask)
            loss = F.cross_entropy(logits.view(-1, tokenizer.vocab_size),
                                   target.view(-1), ignore_index=-100,
                                   reduction='sum')
            n_t = (target != -100).sum().item()
            optimizer.zero_grad()
            (loss / max(1, n_t)).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item()
            total_tok += max(1, n_t)
            step += 1

        train_avg = total_loss / total_tok
        val_avg, val_ppl = evaluate(model, val_loader, tokenizer.vocab_size, device, mlm_rng)
        elapsed = time.time() - start
        print(f"Epoch {epoch+1:>3}/{args.epochs}  "
              f"train_loss={train_avg:.4f}  val_loss={val_avg:.4f}  "
              f"val_ppl={val_ppl:.2f}  lr={lr:.2e}  ({elapsed:.0f}s)")

        history.append({
            'epoch': epoch + 1, 'train_loss': train_avg,
            'val_loss': val_avg, 'val_ppl': val_ppl, 'lr': lr,
        })

        if val_avg < best_val_loss:
            best_val_loss = val_avg
            torch.save({
                'model_state_dict': model.state_dict(),
                'epoch': epoch + 1,
                'val_loss': val_avg, 'val_ppl': val_ppl,
                'vocab_size': tokenizer.vocab_size,
                'variant': args.variant, 'seed': args.seed,
                'args': vars(args),
            }, ckpt_dir / 'best.pt')
            print(f"  ** New best val_loss {val_avg:.4f} **")

    # Save history
    with open(out_dir / 'history.json', 'w') as f:
        json.dump({'history': history, 'best_val_loss': best_val_loss}, f, indent=2)
    print(f"\n=== DONE === best val_loss={best_val_loss:.4f}")


if __name__ == '__main__':
    main()
