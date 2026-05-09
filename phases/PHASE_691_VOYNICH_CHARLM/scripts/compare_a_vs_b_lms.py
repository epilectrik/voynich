#!/usr/bin/env python3
"""
Phase 691.5b: Compare A-only vs B-only LMs.

Tests motivated by P8 finding (same MIDDLE in A vs B has divergent contextual
embeddings beyond substrate identity). If A and B are different systems sharing
orthography, expect:

  1. Cross-system perplexity swap: A-line evaluated by B-LM should be much more
     surprising than by A-LM (and vice versa). Asymmetric perplexity is the
     signature of "different systems."

  2. Procrustes alignment of shared-MIDDLE embeddings: high residual = systems
     don't map onto each other linearly.

  3. Forbidden-pair penalty per LM: do A-LM and B-LM disagree about which
     bigrams are forbidden?
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
from model import CharLM
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID)
from token_level_forbidden import line_log_prob, encode_tokens
from embeddings import encode_line_with_token_spans


def load_model(suffix, tokenizer, device, variant='without_tag', seed=691):
    ckpt_path = PHASE_DIR / 'results' / 'training' / f'{variant}_seed{seed}{suffix}' / 'checkpoints' / 'best.pt'
    print(f"  Loading {ckpt_path}")
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    m = CharLM(vocab_size=tokenizer.vocab_size).to(device)
    m.load_state_dict(ckpt['model_state_dict'])
    m.eval()
    return m, ckpt.get('val_loss', None)


def cross_system_perplexity(model_a, model_b, tokenizer, device, seed=691, n_per_section=200):
    """Take random A-lines and B-lines, evaluate each line under BOTH models.
    Compare loss distributions."""
    rng = np.random.RandomState(seed)
    out = {}
    for section in ['A', 'B']:
        path = PHASE_DIR / 'data' / f'section_{section}' / 'corpus_test.jsonl'
        if not path.exists():
            print(f"  Missing {path}")
            continue
        lines = []
        with open(path, encoding='utf-8') as f:
            for ln in f:
                lines.append(json.loads(ln))
        rng.shuffle(lines)
        sample = lines[:n_per_section]
        a_losses = []
        b_losses = []
        for rec in sample:
            la = line_log_prob(model_a, tokenizer, rec['tokens'], rec['section'], device, with_tag=False)
            lb = line_log_prob(model_b, tokenizer, rec['tokens'], rec['section'], device, with_tag=False)
            if la is None or lb is None:
                continue
            a_losses.append(la)  # higher = better
            b_losses.append(lb)
        a_losses = np.array(a_losses)
        b_losses = np.array(b_losses)
        # Native model is "better" if its log-prob is higher for these lines
        out[f'section_{section}_lines'] = {
            'n': len(a_losses),
            'mean_logprob_under_A_LM': float(a_losses.mean()),
            'mean_logprob_under_B_LM': float(b_losses.mean()),
            'A_advantage_over_B': float((a_losses - b_losses).mean()),
            'native_LM_better': bool((a_losses.mean() > b_losses.mean()) if section == 'A'
                                     else (b_losses.mean() > a_losses.mean())),
        }
    return out


def extract_token_embeddings_section(model, tokenizer, section, device, with_tag=False):
    """Extract per-occurrence embeddings restricted to a section."""
    occurrences = defaultdict(list)
    for split in ['train', 'val', 'test']:
        path = PHASE_DIR / 'data' / f'section_{section}' / f'corpus_{split}.jsonl'
        if not path.exists():
            continue
        with open(path, encoding='utf-8') as f:
            for line in f:
                rec = json.loads(line)
                ids, spans = encode_line_with_token_spans(tokenizer, rec['tokens'],
                                                           rec['section'], with_tag=with_tag)
                ids_t = torch.tensor([ids], dtype=torch.long, device=device)
                attn = torch.zeros((1, len(ids)), dtype=torch.bool, device=device)
                with torch.no_grad():
                    h = model.encode(ids_t, attn)[0].cpu().numpy()
                for ti, (s, e) in enumerate(spans):
                    if s >= e:
                        continue
                    occurrences[rec['tokens'][ti]].append(h[s:e].mean(axis=0))
    # Aggregate
    tokens = sorted(occurrences.keys())
    aggregated = np.array([np.mean(occurrences[t], axis=0) for t in tokens])
    counts = np.array([len(occurrences[t]) for t in tokens])
    return tokens, aggregated, counts


def procrustes_alignment(X, Y):
    """Find R minimizing ||X R - Y||_F. Returns aligned X, residual norm."""
    # X, Y: (N, D)
    # Standard orthogonal Procrustes
    Xc = X - X.mean(axis=0)
    Yc = Y - Y.mean(axis=0)
    M = Xc.T @ Yc
    U, S, Vt = np.linalg.svd(M)
    R = U @ Vt
    Xa = Xc @ R
    residual = np.linalg.norm(Xa - Yc, ord='fro')
    base_norm = np.linalg.norm(Yc, ord='fro')
    return Xa, float(residual / base_norm)


def shared_middle_alignment(model_a, model_b, tokenizer, device, min_freq=3):
    """For each MIDDLE that appears in both A and B contexts, get its
    A-context embedding (mean) and B-context embedding (mean). Align."""
    print("  Extracting A-context embeddings...")
    tokens_a, embs_a, counts_a = extract_token_embeddings_section(model_a, tokenizer, 'A', device)
    print(f"    A-LM: {len(tokens_a)} tokens")
    print("  Extracting B-context embeddings...")
    tokens_b, embs_b, counts_b = extract_token_embeddings_section(model_b, tokenizer, 'B', device)
    print(f"    B-LM: {len(tokens_b)} tokens")

    set_a = {t: i for i, t in enumerate(tokens_a)}
    set_b = {t: i for i, t in enumerate(tokens_b)}
    shared = sorted(set(tokens_a) & set(tokens_b))
    eligible = [t for t in shared
                if counts_a[set_a[t]] >= min_freq and counts_b[set_b[t]] >= min_freq]
    print(f"  Shared tokens with freq >= {min_freq} in both: {len(eligible)}")
    if len(eligible) < 30:
        return {'pass': False, 'reason': f'only {len(eligible)} shared tokens'}

    Xa = np.array([embs_a[set_a[t]] for t in eligible])
    Xb = np.array([embs_b[set_b[t]] for t in eligible])

    _, residual_norm = procrustes_alignment(Xa, Xb)

    # Random-pair baseline: pair shuffled
    rng = np.random.RandomState(691)
    null_residuals = []
    for _ in range(50):
        perm = rng.permutation(len(eligible))
        Xb_shuf = Xb[perm]
        _, r = procrustes_alignment(Xa, Xb_shuf)
        null_residuals.append(r)
    null_mean = float(np.mean(null_residuals))
    return {
        'n_shared_tokens': len(eligible),
        'procrustes_residual_real': float(residual_norm),
        'procrustes_residual_shuffle_mean': null_mean,
        'ratio_real_to_shuffle': float(residual_norm / max(null_mean, 1e-9)),
    }


def per_lm_forbidden_test(model, tokenizer, label, device):
    """Run token-level forbidden-pair test on a single LM."""
    forbidden = json.loads((PHASE_DIR / 'data' / 'forbidden_pairs.json').read_text())
    # Use ALL lines (not just one section) so source tokens are findable
    all_lines = []
    for split in ['train', 'val', 'test']:
        with open(PHASE_DIR / 'data' / f'corpus_{split}.jsonl', encoding='utf-8') as f:
            for line in f:
                all_lines.append(json.loads(line))

    rng = np.random.RandomState(691)
    deltas = []
    pair_results = []
    for p in forbidden:
        src, tgt = p['source'], p['target']
        candidates = []
        for rec in all_lines:
            for i, t in enumerate(rec['tokens']):
                if t == src and i + 1 < len(rec['tokens']):
                    candidates.append((rec, i))
        if not candidates:
            continue
        rng.shuffle(candidates)
        candidates = candidates[:10]  # smaller for speed
        pair_deltas = []
        for rec, i in candidates:
            orig = rec['tokens']
            sub = list(orig)
            sub[i+1] = tgt
            lp_orig = line_log_prob(model, tokenizer, orig, rec['section'], device)
            lp_sub = line_log_prob(model, tokenizer, sub, rec['section'], device)
            if lp_orig is None or lp_sub is None:
                continue
            pair_deltas.append(lp_sub - lp_orig)
        if pair_deltas:
            deltas.extend(pair_deltas)
            pair_results.append({'pair': f'{src} -> {tgt}',
                                  'mean_delta': float(np.mean(pair_deltas)),
                                  'n': len(pair_deltas)})
    return {
        'label': label,
        'mean_forbidden_delta': float(np.mean(deltas)) if deltas else None,
        'n_substitutions': len(deltas),
        'per_pair': pair_results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='cuda:0')
    args = parser.parse_args()

    tokenizer = CharTokenizer.load(PHASE_DIR / 'data' / 'tokenizer.json')
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')

    print("Loading A-LM...")
    model_a, a_loss = load_model('_sectionA', tokenizer, device)
    print(f"  val_loss={a_loss}")
    print("Loading B-LM...")
    model_b, b_loss = load_model('_sectionB', tokenizer, device)
    print(f"  val_loss={b_loss}")

    results = {'a_lm_val_loss': a_loss, 'b_lm_val_loss': b_loss}

    print("\n[1] Cross-system perplexity swap...")
    cross = cross_system_perplexity(model_a, model_b, tokenizer, device)
    results['cross_system_perplexity'] = cross
    for k, v in cross.items():
        print(f"  {k}:")
        print(f"    A-LM logprob: {v['mean_logprob_under_A_LM']:.4f}")
        print(f"    B-LM logprob: {v['mean_logprob_under_B_LM']:.4f}")
        print(f"    A advantage: {v['A_advantage_over_B']:+.4f}")
        print(f"    native better: {v['native_LM_better']}")

    print("\n[2] Procrustes alignment of shared-MIDDLE embeddings...")
    proc = shared_middle_alignment(model_a, model_b, tokenizer, device)
    results['procrustes'] = proc
    if 'reason' in proc:
        print(f"  {proc['reason']}")
    else:
        print(f"  Real residual:    {proc['procrustes_residual_real']:.4f}")
        print(f"  Shuffle residual: {proc['procrustes_residual_shuffle_mean']:.4f}")
        print(f"  Ratio:            {proc['ratio_real_to_shuffle']:.4f}")
        print(f"  (lower ratio = systems align better; near 1.0 = no better than random)")

    print("\n[3] Per-LM forbidden-pair penalty...")
    forb_a = per_lm_forbidden_test(model_a, tokenizer, 'A_LM', device)
    forb_b = per_lm_forbidden_test(model_b, tokenizer, 'B_LM', device)
    results['forbidden_pair'] = {'A_LM': forb_a, 'B_LM': forb_b}
    print(f"  A-LM: mean delta = {forb_a['mean_forbidden_delta']:+.4f}  (n={forb_a['n_substitutions']})")
    print(f"  B-LM: mean delta = {forb_b['mean_forbidden_delta']:+.4f}  (n={forb_b['n_substitutions']})")

    out_path = PHASE_DIR / 'results' / 'predictions' / 'a_vs_b_lm_comparison.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
