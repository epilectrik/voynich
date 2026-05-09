#!/usr/bin/env python3
"""
Phase 691.5: Token-level reformulation of P7 (forbidden-bigram cliff).

P7 in Phase 691.3 used char-level surprise on synthetic "<src> <tgt>" sequences
and FAILED. The methodology issue: char-level model evaluates char sequences,
not MIDDLE-class transitions. The forbidden-pair claim is at the token-bigram
level, so the test must be at that level.

Method here:
  For each forbidden pair (src, tgt):
    Find real lines where `src` actually appears (any position).
    Construct two variants of each line:
      - LEGAL: original line
      - FORBIDDEN: replace next token with `tgt`
    Compute LM log-prob of the entire line for each.
    The forbidden variant should have substantially lower log-prob.

  Compare the LEGAL→FORBIDDEN log-prob delta on forbidden pairs vs:
    Random legal-pair substitution (control)

If the LM has internalized the forbidden-pair constraint, forbidden substitutions
should produce larger log-prob drops than legal substitutions.
"""
import argparse
import functools
import json
import sys
from collections import defaultdict
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import CharLM
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID,
                       SECTION_TAG_IDS)


def encode_tokens(tokenizer, tokens, section, with_tag=False, max_len=256):
    ids = [CLS_ID]
    if with_tag:
        ids.append(SECTION_TAG_IDS[section])
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


def line_log_prob(model, tokenizer, tokens, section, device, with_tag=False):
    """Compute mean per-content-char log-prob via masked-LM.
    Mask each content position and predict; aggregate."""
    ids = encode_tokens(tokenizer, tokens, section, with_tag=with_tag)
    L = len(ids)
    if L < 3:
        return None
    # Identify content positions (chars, not specials/space)
    positions = [p for p in range(1, L - 1) if ids[p] >= 8]
    if not positions:
        return None
    # Build batch with each position masked
    batch = torch.tensor([ids[:] for _ in positions], dtype=torch.long, device=device)
    for bi, p in enumerate(positions):
        batch[bi, p] = MASK_ID
    attn = torch.zeros(batch.shape, dtype=torch.bool, device=device)
    with torch.no_grad():
        log_probs = []
        for s in range(0, batch.shape[0], 32):
            sub = batch[s:s+32]
            sub_attn = attn[s:s+32]
            logits = model(sub, sub_attn)
            log_probs.append(torch.log_softmax(logits, dim=-1).cpu().numpy())
        log_probs = np.concatenate(log_probs, axis=0)
    ids_arr = np.array(ids)
    char_lps = []
    for bi, p in enumerate(positions):
        char_lps.append(float(log_probs[bi, p, ids_arr[p]]))
    return float(np.mean(char_lps))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', default='without_tag')
    parser.add_argument('--seed', type=int, default=691)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--max-occurrences-per-pair', type=int, default=20,
                        help='Sample up to N occurrences of each forbidden source')
    parser.add_argument('--n-legal-controls', type=int, default=100,
                        help='Number of legal-bigram substitutions to compare against')
    args = parser.parse_args()

    tokenizer = CharTokenizer.load(PHASE_DIR / 'data' / 'tokenizer.json')
    ckpt = torch.load(
        PHASE_DIR / 'results' / 'training' / f'{args.variant}_seed{args.seed}' / 'checkpoints' / 'best.pt',
        map_location='cpu', weights_only=False,
    )
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')
    model = CharLM(vocab_size=tokenizer.vocab_size).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()

    forbidden = json.loads((PHASE_DIR / 'data' / 'forbidden_pairs.json').read_text())
    print(f"Loaded {len(forbidden)} forbidden pairs")

    # Load all corpus lines
    all_lines = []
    for split in ['train', 'val', 'test']:
        with open(PHASE_DIR / 'data' / f'corpus_{split}.jsonl', encoding='utf-8') as f:
            for line in f:
                all_lines.append(json.loads(line))
    print(f"Total lines: {len(all_lines)}")
    with_tag = (args.variant == 'with_tag')

    # Build legal-pair frequency table for control
    legal_pair_counts = defaultdict(int)
    for rec in all_lines:
        for i in range(len(rec['tokens']) - 1):
            legal_pair_counts[(rec['tokens'][i], rec['tokens'][i+1])] += 1

    # Per forbidden pair, find lines where src appears
    rng = np.random.RandomState(args.seed)
    forbidden_results = []

    print("\n=== Forbidden-pair substitution test ===")
    for pair_idx, p in enumerate(forbidden):
        src = p['source']
        tgt = p['target']
        # Find lines where src appears
        candidates = []
        for rec in all_lines:
            tokens = rec['tokens']
            for i, t in enumerate(tokens):
                if t == src and i + 1 < len(tokens):
                    candidates.append((rec, i))
        if not candidates:
            continue
        rng.shuffle(candidates)
        candidates = candidates[:args.max_occurrences_per_pair]

        deltas = []
        for rec, i in candidates:
            original_tokens = list(rec['tokens'])
            original_lp = line_log_prob(model, tokenizer, original_tokens, rec['section'], device, with_tag)

            # Substitute next token with forbidden target
            substituted = list(original_tokens)
            substituted[i + 1] = tgt
            forbidden_lp = line_log_prob(model, tokenizer, substituted, rec['section'], device, with_tag)

            if original_lp is None or forbidden_lp is None:
                continue
            deltas.append(forbidden_lp - original_lp)  # if model dislikes forbidden, this is NEGATIVE

        if not deltas:
            continue
        forbidden_results.append({
            'pair': f'{src} -> {tgt}',
            'n_substitutions': len(deltas),
            'mean_delta': float(np.mean(deltas)),
            'median_delta': float(np.median(deltas)),
            'all_negative': bool(all(d < 0 for d in deltas)),
        })
        print(f"  [{pair_idx+1}/{len(forbidden)}] {src} -> {tgt}: n={len(deltas)} mean_delta={np.mean(deltas):+.4f}")

    print("\n=== Legal-pair substitution control ===")
    # Sample N legal pairs, run same test
    legal_results = []
    legal_pairs = sorted(legal_pair_counts.items(), key=lambda x: -x[1])
    legal_pairs = [p for p, c in legal_pairs if c >= 3 and len(p[0]) >= 2 and len(p[1]) >= 2]
    rng.shuffle(legal_pairs)
    legal_pairs = legal_pairs[:args.n_legal_controls]

    for pair_idx, (src, tgt) in enumerate(legal_pairs):
        candidates = []
        for rec in all_lines:
            tokens = rec['tokens']
            for i, t in enumerate(tokens):
                if t == src and i + 1 < len(tokens) and tokens[i+1] != tgt:
                    candidates.append((rec, i))
        if not candidates:
            continue
        rng.shuffle(candidates)
        candidates = candidates[:5]  # smaller per-pair sample for legal

        deltas = []
        for rec, i in candidates:
            original_tokens = list(rec['tokens'])
            original_lp = line_log_prob(model, tokenizer, original_tokens, rec['section'], device, with_tag)
            substituted = list(original_tokens)
            substituted[i + 1] = tgt
            sub_lp = line_log_prob(model, tokenizer, substituted, rec['section'], device, with_tag)
            if original_lp is None or sub_lp is None:
                continue
            deltas.append(sub_lp - original_lp)

        if deltas:
            legal_results.append({
                'pair': f'{src} -> {tgt}',
                'n_substitutions': len(deltas),
                'mean_delta': float(np.mean(deltas)),
            })

    print(f"  {len(legal_results)} legal pairs tested")

    # Compare distributions
    forb_deltas = [r['mean_delta'] for r in forbidden_results]
    legal_deltas = [r['mean_delta'] for r in legal_results]

    forb_mean = float(np.mean(forb_deltas)) if forb_deltas else None
    legal_mean = float(np.mean(legal_deltas)) if legal_deltas else None

    from scipy import stats
    if forb_deltas and legal_deltas:
        u_stat, p_value = stats.mannwhitneyu(forb_deltas, legal_deltas, alternative='less')
    else:
        p_value = None

    print(f"\n=== Summary ===")
    print(f"  Forbidden mean delta: {forb_mean:+.4f}  (negative = model dislikes forbidden)")
    print(f"  Legal mean delta:     {legal_mean:+.4f}")
    print(f"  Mann-Whitney p (forb < legal): {p_value:.4f}" if p_value is not None else "  no p")
    print(f"  N forbidden tested: {len(forb_deltas)}")
    print(f"  N legal controls:   {len(legal_deltas)}")

    out = {
        'method': 'token-level substitution: original_lp - substituted_lp',
        'n_forbidden_pairs_tested': len(forb_deltas),
        'n_legal_pairs_tested': len(legal_deltas),
        'forbidden_mean_delta': forb_mean,
        'legal_mean_delta': legal_mean,
        'mannwhitney_p_forb_less_than_legal': float(p_value) if p_value is not None else None,
        'forbidden_results': forbidden_results,
        'legal_results': legal_results[:30],  # truncate
        'pass': bool(p_value is not None and p_value < 0.01 and forb_mean < legal_mean),
        'criterion': 'forbidden mean_delta < legal mean_delta with p < 0.01',
    }
    out_path = PHASE_DIR / 'results' / 'predictions' / f'p7_token_level_{args.variant}.json'
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
