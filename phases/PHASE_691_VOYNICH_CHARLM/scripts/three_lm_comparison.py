#!/usr/bin/env python3
"""
Phase 691.6: Three-LM comparison (Voynich vs Latin vs English).

Compares LMs trained on equally-sized corpora (~4435 lines, ~38K tokens each):
  - Voynich H-track   (val_loss 0.66, vocab 20)
  - Latin (SISMEL)    (val_loss ~1.37, vocab 26)
  - English (Brunschwig translation)

Tests:
  1. Per-char bits-per-character (compression metric)
  2. Position-conditional entropy (does Voynich show U-shape per C1430?)
  3. Effective context — how much does context lower per-char surprise vs unigram?
"""
import argparse
import functools
import json
import math
import sys
from collections import Counter
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import CharLM
from tokenizer import CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID


def load_lm(suffix, data_subdir, device, variant='without_tag', seed=691):
    """Load model + tokenizer for a given LM."""
    if data_subdir:
        tok_path = PHASE_DIR / 'data' / data_subdir / 'tokenizer.json'
    else:
        tok_path = PHASE_DIR / 'data' / 'tokenizer.json'
    tokenizer = CharTokenizer.load(tok_path)
    ckpt_path = PHASE_DIR / 'results' / 'training' / f'{variant}_seed{seed}{suffix}' / 'checkpoints' / 'best.pt'
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    m = CharLM(vocab_size=tokenizer.vocab_size).to(device)
    m.load_state_dict(ckpt['model_state_dict'])
    m.eval()
    return m, tokenizer, ckpt.get('val_loss', None)


def encode_for_eval(tokenizer, tokens, max_len=256):
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
    return ids


def per_position_logprobs(model, tokenizer, lines, device, max_lines=300):
    """For each line, mask each char position and compute log-prob of true char.
    Returns array of (line_idx, position_in_line, char_id, log_prob, tokens_in_line)."""
    records = []
    for li, rec in enumerate(lines[:max_lines]):
        ids = encode_for_eval(tokenizer, rec['tokens'])
        L = len(ids)
        if L < 4:
            continue
        positions = [p for p in range(1, L - 1) if ids[p] >= 8]  # content chars only
        if not positions:
            continue
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
        L_content = len(positions)
        for bi, p in enumerate(positions):
            char_lp = float(log_probs_all[bi, p, ids_arr[p]])
            records.append({
                'line_idx': li,
                'pos_in_content': bi,
                'pos_frac': bi / max(1, L_content - 1),
                'L': L_content,
                'char_id': int(ids_arr[p]),
                'log_prob': char_lp,
                'bits': -char_lp / math.log(2),
            })
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')

    # Load all three LMs
    print("Loading Voynich LM...")
    m_v, t_v, vl_v = load_lm('', '', device)
    print(f"  vocab={t_v.vocab_size}  val_loss={vl_v:.4f}")
    print("Loading Latin LM...")
    m_l, t_l, vl_l = load_lm('_latin', 'lang_latin', device)
    print(f"  vocab={t_l.vocab_size}  val_loss={vl_l:.4f}")
    print("Loading English LM...")
    m_e, t_e, vl_e = load_lm('_english', 'lang_english', device)
    print(f"  vocab={t_e.vocab_size}  val_loss={vl_e:.4f}")

    # Load test sets
    voy_lines = []
    with open(PHASE_DIR / 'data' / 'corpus_test.jsonl', encoding='utf-8') as f:
        for line in f:
            voy_lines.append(json.loads(line))
    lat_lines = []
    with open(PHASE_DIR / 'data' / 'lang_latin' / 'corpus_test.jsonl', encoding='utf-8') as f:
        for line in f:
            lat_lines.append(json.loads(line))
    eng_lines = []
    with open(PHASE_DIR / 'data' / 'lang_english' / 'corpus_test.jsonl', encoding='utf-8') as f:
        for line in f:
            eng_lines.append(json.loads(line))

    print("\n[1] Computing per-position log-probs (each LM on its own test set)...")
    print("  Voynich..."); voy_recs = per_position_logprobs(m_v, t_v, voy_lines, device)
    print("  Latin...");   lat_recs = per_position_logprobs(m_l, t_l, lat_lines, device)
    print("  English..."); eng_recs = per_position_logprobs(m_e, t_e, eng_lines, device)

    def summary(name, recs, vocab_size):
        bits = np.array([r['bits'] for r in recs])
        mean_bits = float(bits.mean())
        # Random baseline: log2(vocab_size)
        random_bits = math.log2(vocab_size)
        # Effective compression
        return {
            'name': name, 'vocab_size': vocab_size,
            'n_chars': len(recs),
            'mean_bits_per_char': mean_bits,
            'random_baseline_bpc': random_bits,
            'compression_ratio': mean_bits / random_bits,
            'std_bits': float(bits.std()),
            'median_bits': float(np.median(bits)),
        }

    print("\n[2] Compression statistics:")
    s_v = summary('Voynich', voy_recs, 20)  # excludes specials
    s_l = summary('Latin', lat_recs, 26)
    s_e = summary('English', eng_recs, 26)
    print(f"  {'Lang':<10s}  {'V':>3s}  {'BPC':>6s}  {'Random':>7s}  {'Ratio':>6s}  {'Std':>5s}")
    for s in [s_v, s_l, s_e]:
        print(f"  {s['name']:<10s}  {s['vocab_size']:>3d}  {s['mean_bits_per_char']:>6.3f}  "
              f"{s['random_baseline_bpc']:>7.3f}  {s['compression_ratio']:>6.3f}  {s['std_bits']:>5.3f}")

    # Position-conditional entropy
    print("\n[3] Position-conditional entropy (10 buckets):")
    def buckets(recs, n_bins=10):
        b = [[] for _ in range(n_bins)]
        for r in recs:
            idx = min(n_bins - 1, int(r['pos_frac'] * n_bins))
            b[idx].append(r['bits'])
        return [float(np.mean(x)) if x else 0.0 for x in b]

    voy_buckets = buckets(voy_recs)
    lat_buckets = buckets(lat_recs)
    eng_buckets = buckets(eng_recs)

    print(f"  pos_frac:  {' '.join(f'{i*0.1:>5.2f}' for i in range(10))}")
    print(f"  Voynich :  {' '.join(f'{x:>5.3f}' for x in voy_buckets)}")
    print(f"  Latin   :  {' '.join(f'{x:>5.3f}' for x in lat_buckets)}")
    print(f"  English :  {' '.join(f'{x:>5.3f}' for x in eng_buckets)}")

    # Detect U-shape: bits at edges (positions 0, 9) vs middle (positions 4-5)
    def u_shape_signal(buckets):
        edges = (buckets[0] + buckets[-1]) / 2
        middle = (buckets[4] + buckets[5]) / 2
        return edges - middle  # positive = U-shape (high at edges, low at middle)

    print(f"\n  U-shape signal (edge bits - middle bits, positive = U-shape):")
    print(f"    Voynich: {u_shape_signal(voy_buckets):+.3f}")
    print(f"    Latin:   {u_shape_signal(lat_buckets):+.3f}")
    print(f"    English: {u_shape_signal(eng_buckets):+.3f}")

    # Save
    out = {
        'compression': {'Voynich': s_v, 'Latin': s_l, 'English': s_e},
        'val_loss': {'Voynich': vl_v, 'Latin': vl_l, 'English': vl_e},
        'position_buckets': {
            'Voynich': voy_buckets,
            'Latin': lat_buckets,
            'English': eng_buckets,
        },
        'u_shape_signal': {
            'Voynich': u_shape_signal(voy_buckets),
            'Latin': u_shape_signal(lat_buckets),
            'English': u_shape_signal(eng_buckets),
        },
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / 'three_lm_comparison.json'
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
