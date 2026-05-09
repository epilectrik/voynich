#!/usr/bin/env python3
"""
Phase 691.3 supplement:
  - P7: forbidden-bigram perplexity cliff
  - P8: cross-system MIDDLE invariance (uses per-section embeddings)
  - P3 binary: MODIFIER vs BASE only (no OTHER) — class-imbalance-free
  - P9 binary: HEAD vs TERM only (drop singleton MOD) — class-imbalance-free
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
import torch.nn.functional as F

PHASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PHASE_DIR.parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Morphology
from model import CharLM
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID,
                       SECTION_TAG_IDS)
from embeddings import encode_line_with_token_spans, load_corpus_lines
from test_predictions import (train_linear, MODIFIER_CHARS, BASE_CHARS,
                              HEAD_CHARS, MOD_CHARS, TERM_CHARS)


# ---------- P7: Forbidden-bigram perplexity cliff ----------

def test_p7(model, tokenizer, device, with_tag, n_legal_samples=200, seed=691):
    """Compute LM-assigned probability of forbidden bigrams vs frequency-matched legal bigrams.

    Method: for each (src, tgt) bigram, build a synthetic line "<src> <tgt>" and
    compute the avg log-prob of the target token's chars given the source-and-space context.
    Compare distribution of forbidden vs legal bigrams.
    """
    rng = np.random.RandomState(seed)
    forbidden = json.loads((PHASE_DIR / 'data' / 'forbidden_pairs.json').read_text())

    # Find legal bigrams: pairs (src, tgt) that DO occur in the corpus
    train_path = PHASE_DIR / 'data' / 'corpus_train.jsonl'
    legal_counts = defaultdict(int)
    with open(train_path, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            tokens = r['tokens']
            for i in range(len(tokens) - 1):
                legal_counts[(tokens[i], tokens[i + 1])] += 1
    # Sample legal pairs roughly matched on source-token frequency
    forbidden_sources = set(p['source'] for p in forbidden)
    same_source_legal = [(s, t) for (s, t), c in legal_counts.items()
                         if s in forbidden_sources]
    if len(same_source_legal) < n_legal_samples:
        general_legal = [(s, t) for (s, t), c in legal_counts.items() if c >= 2]
        rng.shuffle(general_legal)
        legal_pairs = same_source_legal + general_legal[:n_legal_samples - len(same_source_legal)]
    else:
        rng.shuffle(same_source_legal)
        legal_pairs = same_source_legal[:n_legal_samples]

    print(f"  Forbidden pairs: {len(forbidden)}")
    print(f"  Legal sample pairs: {len(legal_pairs)}")

    def bigram_avg_logprob(src, tgt, section='B'):
        ids = [CLS_ID]
        if with_tag:
            ids.append(SECTION_TAG_IDS[section])
        # Encode src
        for ch in src:
            if ch in tokenizer.token_to_id:
                ids.append(tokenizer.token_to_id[ch])
        # Space
        ids.append(SPACE_ID)
        target_start = len(ids)
        for ch in tgt:
            if ch in tokenizer.token_to_id:
                ids.append(tokenizer.token_to_id[ch])
        target_end = len(ids)
        ids.append(SEP_ID)
        if target_start >= target_end:
            return None
        ids_t = torch.tensor([ids], dtype=torch.long, device=device)
        attn = torch.zeros((1, len(ids)), dtype=torch.bool, device=device)
        with torch.no_grad():
            logits = model(ids_t, attn)
        log_probs = torch.log_softmax(logits[0], dim=-1).cpu().numpy()
        # Predict each char in [target_start, target_end) at the SAME position
        # (BERT-style: model directly outputs at each position given full context)
        ids_arr = np.array(ids)
        target_lp = log_probs[target_start:target_end, ids_arr[target_start:target_end]]
        return float(target_lp.mean())

    forbidden_logprobs = []
    for p in forbidden:
        lp = bigram_avg_logprob(p['source'], p['target'])
        if lp is not None:
            forbidden_logprobs.append(lp)
    legal_logprobs = []
    for src, tgt in legal_pairs:
        lp = bigram_avg_logprob(src, tgt)
        if lp is not None:
            legal_logprobs.append(lp)

    forbidden_logprobs = np.array(forbidden_logprobs)
    legal_logprobs = np.array(legal_logprobs)

    # Convert to perplexity-like metric: -mean(log p) (higher = more surprised)
    forbidden_surprise = -forbidden_logprobs
    legal_surprise = -legal_logprobs
    ratio = forbidden_surprise.mean() / max(legal_surprise.mean(), 1e-6)

    # Mann-Whitney
    from scipy import stats
    u_stat, p_value = stats.mannwhitneyu(forbidden_surprise, legal_surprise, alternative='greater')

    return {
        'forbidden_mean_surprise': float(forbidden_surprise.mean()),
        'legal_mean_surprise': float(legal_surprise.mean()),
        'ratio': float(ratio),
        'mannwhitney_p': float(p_value),
        'n_forbidden': len(forbidden_logprobs),
        'n_legal': len(legal_logprobs),
        'pass': bool(ratio >= 5.0 and p_value < 0.001),
        'criterion': 'ratio >= 5.0 AND Mann-Whitney p < 0.001',
    }


# ---------- P8: Cross-system MIDDLE invariance ----------

def test_p8(model, tokenizer, device, with_tag, min_freq_per_section=5, seed=691):
    """For each MIDDLE in BOTH A and B with freq >=5 each, compute distance between
    section-specific embeddings. Compare to distance between random sections."""
    rng = np.random.RandomState(seed)
    morph = Morphology()

    # Walk all corpus, encode each line, pool char embeddings per token, group by (MIDDLE, section)
    all_lines = []
    for split in ['train', 'val', 'test']:
        all_lines.extend(load_corpus_lines(PHASE_DIR / 'data' / f'corpus_{split}.jsonl'))

    middle_section_embs = defaultdict(list)
    middle_section_count = defaultdict(int)

    model.eval()
    with torch.no_grad():
        for rec in all_lines:
            tokens = rec['tokens']
            section = rec['section']
            ids, spans = encode_line_with_token_spans(
                tokenizer, tokens, section, with_tag=with_tag,
            )
            ids_t = torch.tensor([ids], dtype=torch.long, device=device)
            attn = torch.zeros((1, len(ids)), dtype=torch.bool, device=device)
            hidden = model.encode(ids_t, attn)[0].cpu().numpy()
            for ti, (s, e) in enumerate(spans):
                if s >= e:
                    continue
                tok = tokens[ti]
                m = morph.extract(tok)
                if not m or not m.middle:
                    continue
                emb = hidden[s:e].mean(axis=0)
                middle_section_embs[(m.middle, section)].append(emb)
                middle_section_count[(m.middle, section)] += 1

    # Find MIDDLEs that appear in BOTH A and B with sufficient count
    qualifying = []
    for middle in set(m for (m, s) in middle_section_embs.keys()):
        a_count = middle_section_count.get((middle, 'A'), 0)
        b_count = middle_section_count.get((middle, 'B'), 0)
        if a_count >= min_freq_per_section and b_count >= min_freq_per_section:
            qualifying.append(middle)
    print(f"  MIDDLEs with >={min_freq_per_section} occ in both A and B: {len(qualifying)}")
    if len(qualifying) < 5:
        return {'pass': False, 'reason': f'only {len(qualifying)} qualifying MIDDLEs'}

    # Compute d_AB for each qualifying MIDDLE
    d_ab_list = []
    for middle in qualifying:
        a_centroid = np.mean(middle_section_embs[(middle, 'A')], axis=0)
        b_centroid = np.mean(middle_section_embs[(middle, 'B')], axis=0)
        d_ab_list.append(np.linalg.norm(a_centroid - b_centroid))
    d_ab = np.mean(d_ab_list)

    # Random pair distance (across DIFFERENT MIDDLEs)
    n_perm = 1000
    d_random_list = []
    for _ in range(n_perm):
        m1, m2 = rng.choice(qualifying, size=2, replace=False)
        # Random sections to compare
        c1 = np.mean(middle_section_embs[(m1, 'A')], axis=0)
        c2 = np.mean(middle_section_embs[(m2, 'B')], axis=0)
        d_random_list.append(np.linalg.norm(c1 - c2))
    d_random = np.mean(d_random_list)
    ratio = d_ab / d_random

    # P value: how often does folio-shuffle give a d_ab as small as observed?
    null_d_abs = []
    for _ in range(n_perm):
        # Shuffle which observations are A vs B for each middle
        shuffled_d = []
        for middle in qualifying:
            all_obs = (middle_section_embs[(middle, 'A')]
                       + middle_section_embs[(middle, 'B')])
            n_a = len(middle_section_embs[(middle, 'A')])
            rng.shuffle(all_obs)
            a_part = all_obs[:n_a]
            b_part = all_obs[n_a:]
            if not a_part or not b_part:
                continue
            shuffled_d.append(np.linalg.norm(
                np.mean(a_part, axis=0) - np.mean(b_part, axis=0)
            ))
        if shuffled_d:
            null_d_abs.append(np.mean(shuffled_d))
    p_value = float(np.mean(np.array(null_d_abs) <= d_ab))

    return {
        'd_within_AB_mean': float(d_ab),
        'd_random_pair_mean': float(d_random),
        'ratio': float(ratio),
        'n_qualifying_middles': len(qualifying),
        'p_value_shuffle': p_value,
        'pass': bool(ratio < 0.7 and p_value < 0.01),
        'criterion': 'ratio < 0.7 AND folio-shuffle p < 0.01',
    }


# ---------- P3 binary re-test: MODIFIER vs BASE only ----------

def test_p3_binary(model, tokenizer, n_iter=2000, seed=691):
    """Drop OTHER class to remove imbalance bias."""
    char_to_id = tokenizer.token_to_id
    with torch.no_grad():
        char_emb = model.tok_embed.weight.detach().cpu().numpy()
    X = []
    y = []
    for ch in tokenizer.chars:
        if ch in MODIFIER_CHARS:
            X.append(char_emb[char_to_id[ch]]); y.append(0)
        elif ch in BASE_CHARS:
            X.append(char_emb[char_to_id[ch]]); y.append(1)
    X = np.array(X); y = np.array(y)
    if len(set(y)) < 2:
        return {'pass': False, 'reason': '<2 classes'}
    correct = 0
    for i in range(len(X)):
        Xtr = np.delete(X, i, 0); ytr = np.delete(y, i)
        W_b = train_linear(Xtr, ytr, 2, n_iter=n_iter, seed=seed)
        pred = (X[i:i+1] @ W_b['W'] + W_b['b']).argmax(1)
        correct += int(pred[0] == y[i])
    acc = correct / len(X)
    rng = np.random.RandomState(seed + 6)
    Xr = rng.randn(*X.shape).astype(np.float32) * 0.02
    correct_r = 0
    for i in range(len(Xr)):
        Xtr = np.delete(Xr, i, 0); ytr = np.delete(y, i)
        W_b = train_linear(Xtr, ytr, 2, n_iter=n_iter, seed=seed)
        pred = (Xr[i:i+1] @ W_b['W'] + W_b['b']).argmax(1)
        correct_r += int(pred[0] == y[i])
    rand_acc = correct_r / len(Xr)
    return {
        'binary_loo_acc': acc,
        'random_init_baseline_acc': rand_acc,
        'lift_pp': (acc - rand_acc) * 100,
        'n_chars': len(X),
        'pass': bool(acc >= 0.85 and (acc - rand_acc) * 100 >= 25),
        'criterion': 'binary LOO acc >= 0.85 AND >= 25pp lift',
    }


# ---------- P9 binary re-test: HEAD vs TERM only ----------

def test_p9_binary(model, tokenizer, n_iter=2000, seed=691):
    """Drop singleton MOD class."""
    char_to_id = tokenizer.token_to_id
    with torch.no_grad():
        char_emb = model.tok_embed.weight.detach().cpu().numpy()
    X = []
    y = []
    for ch in tokenizer.chars:
        if ch in HEAD_CHARS:
            X.append(char_emb[char_to_id[ch]]); y.append(0)
        elif ch in TERM_CHARS:
            X.append(char_emb[char_to_id[ch]]); y.append(1)
    X = np.array(X); y = np.array(y)
    if len(set(y)) < 2:
        return {'pass': False, 'reason': '<2 classes'}
    correct = 0
    for i in range(len(X)):
        Xtr = np.delete(X, i, 0); ytr = np.delete(y, i)
        W_b = train_linear(Xtr, ytr, 2, n_iter=n_iter, seed=seed)
        pred = (X[i:i+1] @ W_b['W'] + W_b['b']).argmax(1)
        correct += int(pred[0] == y[i])
    acc = correct / len(X)
    rng = np.random.RandomState(seed + 7)
    Xr = rng.randn(*X.shape).astype(np.float32) * 0.02
    correct_r = 0
    for i in range(len(Xr)):
        Xtr = np.delete(Xr, i, 0); ytr = np.delete(y, i)
        W_b = train_linear(Xtr, ytr, 2, n_iter=n_iter, seed=seed)
        pred = (Xr[i:i+1] @ W_b['W'] + W_b['b']).argmax(1)
        correct_r += int(pred[0] == y[i])
    rand_acc = correct_r / len(Xr)
    return {
        'binary_loo_acc': acc,
        'random_init_baseline_acc': rand_acc,
        'lift_pp': (acc - rand_acc) * 100,
        'n_chars': len(X),
        'pass': bool(acc >= 0.85 and (acc - rand_acc) * 100 >= 25),
        'criterion': 'binary LOO acc >= 0.85 AND >= 25pp lift',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=['without_tag', 'with_tag'], default='without_tag')
    parser.add_argument('--seed', type=int, default=691)
    parser.add_argument('--device', default='cuda:0')
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

    results = {}

    print("\n[P3-binary] MODIFIER vs BASE (no OTHER)...")
    results['P3_binary'] = test_p3_binary(model, tokenizer)
    p = results['P3_binary']
    print(f"  acc={p.get('binary_loo_acc'):.3f} lift={p.get('lift_pp'):.1f}pp {'PASS' if p['pass'] else 'FAIL'}")

    print("\n[P9-binary] HEAD vs TERM (no MOD)...")
    results['P9_binary'] = test_p9_binary(model, tokenizer)
    p = results['P9_binary']
    print(f"  acc={p.get('binary_loo_acc'):.3f} lift={p.get('lift_pp'):.1f}pp {'PASS' if p['pass'] else 'FAIL'}")

    print("\n[P7] Forbidden-bigram perplexity cliff...")
    with_tag = (args.variant == 'with_tag')
    results['P7'] = test_p7(model, tokenizer, device, with_tag)
    p = results['P7']
    print(f"  ratio={p.get('ratio'):.3f} mw_p={p.get('mannwhitney_p'):.4f} {'PASS' if p['pass'] else 'FAIL'}")

    print("\n[P8] Cross-system MIDDLE invariance...")
    results['P8'] = test_p8(model, tokenizer, device, with_tag)
    p = results['P8']
    if 'reason' in p:
        print(f"  {p['reason']} FAIL")
    else:
        print(f"  ratio={p.get('ratio'):.3f} p={p.get('p_value_shuffle'):.4f} {'PASS' if p['pass'] else 'FAIL'}")

    out_path = PHASE_DIR / 'results' / 'predictions' / f'test_results_supplement_{args.variant}_seed{args.seed}.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
