#!/usr/bin/env python3
"""
Extract token embeddings from a trained char-LM checkpoint.

For each unique token in the H-track corpus, encode each occurrence in its
natural line context, pool the character-level hidden states for that
token's position-range, and aggregate (mean) across all occurrences.

Outputs:
  embeddings/token_embeddings_{variant}_seed{seed}.npz containing:
    tokens:       (V,) array of token strings
    embeddings:   (V, D) float32 array
    occurrences:  (V,) int array — # of occurrences pooled per token
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import CharLM
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID,
                       SECTION_TAG_IDS)


def encode_line_with_token_spans(tokenizer, tokens, section, with_tag=False, max_len=256):
    """Return (ids, token_spans) where token_spans[i] = (start, end) in ids
    indicating the character positions for token i."""
    ids = [CLS_ID]
    if with_tag:
        ids.append(SECTION_TAG_IDS[section])
    spans = []
    for ti, tok in enumerate(tokens):
        if ti > 0:
            ids.append(SPACE_ID)
        start = len(ids)
        for ch in tok:
            if ch in tokenizer.token_to_id:
                ids.append(tokenizer.token_to_id[ch])
        end = len(ids)
        spans.append((start, end))
    ids.append(SEP_ID)
    if len(ids) > max_len:
        # Truncate; spans beyond max_len are dropped
        ids = ids[:max_len - 1] + [SEP_ID]
        spans = [(s, e) for s, e in spans if e < max_len]
    return ids, spans


def extract_embeddings(model, tokenizer, lines, with_tag, device, max_len=256):
    """For each token in each line, get its mean-pooled embedding.
    Returns dict: token -> list of (embedding, folio, line, section)."""
    model.eval()
    token_occurrences = defaultdict(list)

    with torch.no_grad():
        for rec in lines:
            tokens = rec['tokens']
            section = rec['section']
            folio = rec['folio']
            line = rec['line']
            if not tokens:
                continue
            ids, spans = encode_line_with_token_spans(
                tokenizer, tokens, section, with_tag=with_tag, max_len=max_len,
            )
            ids_tensor = torch.tensor([ids], dtype=torch.long, device=device)
            attn_mask = torch.zeros((1, len(ids)), dtype=torch.bool, device=device)
            hidden = model.encode(ids_tensor, attn_mask)  # [1, L, D]
            hidden = hidden[0].cpu().numpy()  # [L, D]
            for ti, (start, end) in enumerate(spans):
                if start >= end:
                    continue
                tok_str = tokens[ti]
                emb = hidden[start:end].mean(axis=0)
                token_occurrences[tok_str].append({
                    'embedding': emb,
                    'folio': folio,
                    'line': line,
                    'section': section,
                })
    return token_occurrences


def aggregate_token_embeddings(token_occurrences):
    """Return tokens, embeddings (V, D), occurrence_counts."""
    tokens = sorted(token_occurrences.keys())
    embeddings = np.zeros((len(tokens), 256), dtype=np.float32)
    occurrence_counts = np.zeros(len(tokens), dtype=np.int32)
    section_majority = []
    for i, tok in enumerate(tokens):
        occs = token_occurrences[tok]
        embs = np.stack([o['embedding'] for o in occs])
        embeddings[i] = embs.mean(axis=0)
        occurrence_counts[i] = len(occs)
        secs = [o['section'] for o in occs]
        section_majority.append(max(set(secs), key=secs.count))
    return tokens, embeddings, occurrence_counts, section_majority


def load_corpus_lines(jsonl_path):
    with open(jsonl_path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=['without_tag', 'with_tag'], default='without_tag')
    parser.add_argument('--seed', type=int, default=691)
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()

    ckpt_path = PHASE_DIR / 'results' / 'training' / f'{args.variant}_seed{args.seed}' / 'checkpoints' / 'best.pt'
    print(f"Loading checkpoint: {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)

    tokenizer = CharTokenizer.load(PHASE_DIR / 'data' / 'tokenizer.json')
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    model = CharLM(vocab_size=tokenizer.vocab_size).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()
    print(f"  val_loss: {ckpt.get('val_loss', '?')}")
    print(f"  variant:  {ckpt.get('variant', '?')}")

    # Use ALL splits for embedding extraction (train + val + test)
    # This is OK because we're not measuring generalization — we want every token's
    # representation. The held-out folios still serve their purpose (model never
    # trained on them), they're just included for completeness of the embedding map.
    all_lines = []
    for split in ['train', 'val', 'test']:
        all_lines.extend(load_corpus_lines(PHASE_DIR / 'data' / f'corpus_{split}.jsonl'))
    print(f"Total lines: {len(all_lines)}")

    with_tag = (args.variant == 'with_tag')
    print(f"Extracting embeddings (with_tag={with_tag})...")
    occurrences = extract_embeddings(model, tokenizer, all_lines, with_tag, device)
    print(f"Unique tokens: {len(occurrences)}")

    tokens, embeddings, counts, sec_maj = aggregate_token_embeddings(occurrences)
    print(f"Embeddings: {embeddings.shape}")

    out_dir = PHASE_DIR / 'results' / 'embeddings'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'token_embeddings_{args.variant}_seed{args.seed}.npz'
    np.savez(
        out_path,
        tokens=np.array(tokens),
        embeddings=embeddings,
        occurrences=counts,
        section=np.array(sec_maj),
    )
    print(f"Saved: {out_path}")

    # Quick stats
    print(f"\nTop 10 most frequent tokens:")
    order = np.argsort(-counts)
    for i in order[:10]:
        print(f"  {tokens[i]:>10s} (n={counts[i]}, sec={sec_maj[i]})")


if __name__ == '__main__':
    main()
