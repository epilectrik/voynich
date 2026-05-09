#!/usr/bin/env python3
"""
Train a Voynich-to-Gloss translator transformer.

Small autoregressive char-level transformer learns to map Voynich tokens to
their atomize() decomposition (per C1394). Training format:

  <BOS> q o k e d y <SEP> q o : h e a t . c o o l . d o . e n d <EOS>

The model learns deterministic atom-cipher decoding from the data.
At inference, prompt with token chars + SEP, sample autoregressively.

Useful as:
- Interactive Voynich-to-gloss translator
- Test bed for "given a synthetic token, what gloss does it produce?"
- Foundation for richer models (line-level, recipe-level)
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
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

PHASE_DIR = Path(__file__).resolve().parent.parent

# Vocabulary: all chars used in either input (Voynich tokens) or output (glosses)
SPECIALS = ['<PAD>', '<BOS>', '<SEP>', '<EOS>', '<UNK>']
PAD_ID = 0
BOS_ID = 1
SEP_ID = 2
EOS_ID = 3
UNK_ID = 4


def build_vocab(pairs):
    chars = set()
    for p in pairs:
        chars.update(p['token'])
        chars.update(p['gloss'])
    return list(SPECIALS) + sorted(chars)


def encode_pair(token, gloss, char_to_id):
    ids = [BOS_ID]
    for c in token:
        ids.append(char_to_id.get(c, UNK_ID))
    ids.append(SEP_ID)
    for c in gloss:
        ids.append(char_to_id.get(c, UNK_ID))
    ids.append(EOS_ID)
    return ids


def encode_input(token, char_to_id):
    """Encoder-only: token + SEP, ready for autoregressive completion."""
    ids = [BOS_ID]
    for c in token:
        ids.append(char_to_id.get(c, UNK_ID))
    ids.append(SEP_ID)
    return ids


class GlossDataset(Dataset):
    def __init__(self, pairs, char_to_id, max_len=80):
        self.records = []
        for p in pairs:
            ids = encode_pair(p['token'], p['gloss'], char_to_id)
            if len(ids) <= max_len:
                self.records.append({'ids': ids, 'token': p['token'], 'gloss': p['gloss']})
        self.max_len = max_len

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        return torch.tensor(self.records[idx]['ids'], dtype=torch.long)


def collate(batch, pad_id=PAD_ID):
    L = max(len(x) for x in batch)
    out = torch.full((len(batch), L), pad_id, dtype=torch.long)
    for i, x in enumerate(batch):
        out[i, :len(x)] = x
    return out


class GlosserGPT(nn.Module):
    """Small decoder-only autoregressive transformer."""
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=4,
                 dim_feedforward=512, max_seq_len=80, dropout=0.1):
        super().__init__()
        self.tok_embed = nn.Embedding(vocab_size, d_model)
        self.pos_embed = nn.Embedding(max_seq_len, d_model)
        self.embed_dropout = nn.Dropout(dropout)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            dropout=dropout, activation='gelu', batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=num_layers)
        self.layer_norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)
        self.head.weight = self.tok_embed.weight  # tied

        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.02)

    def forward(self, ids):
        B, L = ids.shape
        positions = torch.arange(L, device=ids.device).unsqueeze(0).expand(B, L)
        h = self.tok_embed(ids) + self.pos_embed(positions)
        h = self.embed_dropout(h)
        # Causal mask
        mask = torch.triu(torch.ones(L, L, dtype=torch.bool, device=ids.device), diagonal=1)
        # PAD mask
        pad_mask = (ids == PAD_ID)
        h = self.encoder(h, mask=mask, src_key_padding_mask=pad_mask)
        h = self.layer_norm(h)
        return self.head(h)


def train(model, loader, val_loader, epochs, lr, device):
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = epochs * len(loader)
    best_val = float('inf')
    history = []
    start = time.time()
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        n_t = 0
        for batch in loader:
            batch = batch.to(device)
            inp = batch[:, :-1]
            target = batch[:, 1:]
            logits = model(inp)
            loss = F.cross_entropy(logits.reshape(-1, logits.shape[-1]),
                                    target.reshape(-1), ignore_index=PAD_ID)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
            n_t += 1
        train_loss = total_loss / n_t

        # Eval
        model.eval()
        val_loss_sum = 0.0
        nv = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(device)
                inp = batch[:, :-1]
                target = batch[:, 1:]
                logits = model(inp)
                vl = F.cross_entropy(logits.reshape(-1, logits.shape[-1]),
                                      target.reshape(-1), ignore_index=PAD_ID)
                val_loss_sum += vl.item()
                nv += 1
        val_loss = val_loss_sum / nv
        elapsed = time.time() - start
        print(f"  Epoch {epoch+1:>3d}/{epochs}  train={train_loss:.4f}  val={val_loss:.4f}  ({elapsed:.0f}s)")
        history.append({'epoch': epoch + 1, 'train_loss': train_loss, 'val_loss': val_loss})
        if val_loss < best_val:
            best_val = val_loss
    return best_val, history


@torch.no_grad()
def gloss_token(model, token_str, char_to_id, id_to_char, device, max_gen=60):
    """Generate gloss for a Voynich token via greedy autoregressive sampling."""
    ids = encode_input(token_str, char_to_id)
    out_ids = list(ids)
    for _ in range(max_gen):
        x = torch.tensor([out_ids], dtype=torch.long, device=device)
        logits = model(x)[0, -1]
        # Disallow special tokens except EOS
        for t in [PAD_ID, BOS_ID, SEP_ID, UNK_ID]:
            logits[t] = -float('inf')
        next_id = int(logits.argmax().item())
        if next_id == EOS_ID:
            break
        out_ids.append(next_id)
    # Decode the gloss part only (after first SEP)
    sep_pos = out_ids.index(SEP_ID)
    gloss_chars = ''.join(id_to_char[i] for i in out_ids[sep_pos + 1:] if i not in (PAD_ID, BOS_ID, SEP_ID, EOS_ID, UNK_ID))
    return gloss_chars


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--lr', type=float, default=5e-4)
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()

    # Load pairs
    pairs = []
    with open(PHASE_DIR / 'data' / 'gloss_pairs.jsonl', encoding='utf-8') as f:
        for line in f:
            pairs.append(json.loads(line))
    print(f"Loaded {len(pairs)} (token, gloss) pairs")

    # Build vocab
    vocab = build_vocab(pairs)
    char_to_id = {c: i for i, c in enumerate(vocab)}
    id_to_char = {i: c for c, i in char_to_id.items()}
    print(f"Vocab size: {len(vocab)}")

    # Train/val split (90/10) by frequency-weighted sampling
    rng = random.Random(691)
    rng.shuffle(pairs)
    n_val = max(50, len(pairs) // 10)
    val_pairs = pairs[:n_val]
    train_pairs = pairs[n_val:]
    print(f"Train: {len(train_pairs)}  Val: {len(val_pairs)}")

    # Datasets
    train_ds = GlossDataset(train_pairs, char_to_id)
    val_ds = GlossDataset(val_pairs, char_to_id)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                            collate_fn=collate)

    # Model
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    model = GlosserGPT(vocab_size=len(vocab)).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Params: {n_params:,}")

    # Train
    best_val, history = train(model, train_loader, val_loader, args.epochs, args.lr, device)

    # Test on sample tokens
    print(f"\n=== Test predictions (greedy) ===")
    test_tokens = ['qokeedy', 'chedy', 'daiin', 'shedy', 'qokar', 'okal', 'qokedy', 'oror', 'sho', 'aiin']
    for tok in test_tokens:
        pred = gloss_token(model, tok, char_to_id, id_to_char, device)
        # Ground truth
        for p in pairs:
            if p['token'] == tok:
                gt = p['gloss']
                break
        else:
            gt = '(not in corpus)'
        match = '✓' if pred == gt else '✗'
        print(f"  {tok:>10s} -> {pred:<30s} {match}  truth: {gt}")

    # Save
    out_dir = PHASE_DIR / 'results' / 'training_glosser'
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({
        'model_state_dict': model.state_dict(),
        'vocab': vocab,
        'best_val': best_val,
        'history': history,
        'args': vars(args),
    }, out_dir / 'glosser.pt')
    print(f"\nSaved: {out_dir / 'glosser.pt'}")


if __name__ == '__main__':
    main()
