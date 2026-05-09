#!/usr/bin/env python3
"""
Phase 691.4: Anomaly detection — top-surprise LM tokens vs 18-transcriber disagreement.

Pipeline:
1. Compute per-token pseudo-likelihood for every token in the H-track corpus
   (mask each char, predict, average log-prob across token chars)
2. Build 18-transcriber disagreement set: at each (folio, line, position-idx),
   count distinct readings and # of transcribers that disagree with the modal reading
3. Cross-reference: of top 1% LM-surprise tokens, how many fall in disagreement
   positions? Significance via permutation null.

Per pre-reg P1.4 auxiliary criterion: ≥ 30% overlap = success.

Outputs:
  results/anomaly/lm_surprise_per_token.jsonl
  results/anomaly/transcriber_disagreement.jsonl
  results/anomaly/overlap_report.md
"""
import argparse
import functools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PHASE_DIR.parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript
from model import CharLM
from tokenizer import (CharTokenizer, PAD_ID, MASK_ID, CLS_ID, SEP_ID, SPACE_ID,
                       SECTION_TAG_IDS)
from embeddings import encode_line_with_token_spans, load_corpus_lines


# ---------- Per-token pseudo-likelihood ----------

def compute_token_surprise(model, tokenizer, all_lines, with_tag, device, batch_size=8):
    """For each token in each line, compute pseudo-likelihood per char (mean).
    Returns list of dicts with folio/line/idx/token/avg_logprob/surprise."""
    model.eval()
    results = []
    n_lines = len(all_lines)

    for li_idx, rec in enumerate(all_lines):
        if li_idx % 200 == 0:
            print(f"  {li_idx}/{n_lines}")
        tokens = rec['tokens']
        if not tokens:
            continue
        section = rec['section']
        ids, spans = encode_line_with_token_spans(tokenizer, tokens, section, with_tag=with_tag)
        L = len(ids)
        if L < 3:
            continue

        # Build batch: L copies of `ids`, each with one position masked
        # Skip CLS (0) and SEP (L-1)
        positions_to_mask = [p for p in range(1, L - 1) if ids[p] != PAD_ID]
        if not positions_to_mask:
            continue

        batch = torch.tensor([ids[:] for _ in positions_to_mask], dtype=torch.long, device=device)
        for bi, p in enumerate(positions_to_mask):
            batch[bi, p] = MASK_ID
        attn = torch.zeros(batch.shape, dtype=torch.bool, device=device)

        with torch.no_grad():
            # Sub-batch for memory
            all_log_probs = []
            for s in range(0, batch.shape[0], batch_size):
                sub = batch[s:s + batch_size]
                sub_attn = attn[s:s + batch_size]
                logits = model(sub, sub_attn)  # [b, L, V]
                lp = torch.log_softmax(logits, dim=-1).cpu().numpy()
                all_log_probs.append(lp)
            all_log_probs = np.concatenate(all_log_probs, axis=0)  # [|positions|, L, V]

        # For each masked position, get log-prob of the true char at that position
        ids_arr = np.array(ids)
        pos_log_prob = {}  # position -> log prob of true char
        for bi, p in enumerate(positions_to_mask):
            pos_log_prob[p] = float(all_log_probs[bi, p, ids_arr[p]])

        # Aggregate per token (mean over its char positions)
        for ti, (s, e) in enumerate(spans):
            char_lps = [pos_log_prob[p] for p in range(s, e) if p in pos_log_prob]
            if not char_lps:
                continue
            avg_lp = float(np.mean(char_lps))
            results.append({
                'folio': rec['folio'],
                'line': rec['line'],
                'token_idx': ti,
                'token': tokens[ti],
                'section': section,
                'n_chars': len(char_lps),
                'avg_log_prob': avg_lp,
                'surprise': -avg_lp,
            })
    return results


# ---------- 18-transcriber disagreement ----------

def build_transcriber_disagreement():
    """For each (folio, line, position-within-line), gather all transcriber readings
    and count distinct/disagree counts. Position is 0-indexed by token order in
    each transcriber's reading of that line.

    Note: alignment by positional index is approximate when transcribers disagree
    on segmentation. Acknowledged limitation.
    """
    tx = Transcript()
    # Per (folio, line, transcriber): ordered list of tokens
    per_track = defaultdict(list)
    for tok in tx.all(h_only=False):
        if not tok.word or '*' in tok.word:
            continue
        per_track[(tok.folio, tok.line, tok.transcriber)].append(tok.word)

    # Pivot: per (folio, line, idx) -> {transcriber: token}
    by_position = defaultdict(dict)
    folio_lines = set((f, l) for (f, l, t) in per_track.keys())
    for (folio, line) in folio_lines:
        # Find max length across transcribers (positional alignment)
        track_tokens = {t: per_track.get((folio, line, t), []) for (f, l, t) in per_track if f == folio and l == line}
        for transcriber, tokens in track_tokens.items():
            for idx, tok in enumerate(tokens):
                by_position[(folio, line, idx)][transcriber] = tok

    # Compute disagreement per position
    disagreement_records = []
    for (folio, line, idx), readings in by_position.items():
        n_trans = len(readings)
        if n_trans < 2:
            continue
        readings_h = readings.get('H')
        if not readings_h:
            continue
        modal = Counter(readings.values()).most_common(1)[0][0]
        n_disagree = sum(1 for v in readings.values() if v != modal)
        n_distinct = len(set(readings.values()))
        disagree_with_h = sum(1 for k, v in readings.items() if k != 'H' and v != readings_h)
        disagreement_records.append({
            'folio': folio,
            'line': line,
            'token_idx': idx,
            'h_token': readings_h,
            'modal': modal,
            'n_transcribers': n_trans,
            'n_distinct_readings': n_distinct,
            'n_disagree_with_modal': n_disagree,
            'n_disagree_with_h': disagree_with_h,
            'distinct_readings': sorted(set(readings.values())),
        })
    return disagreement_records


# ---------- Cross-reference + significance ----------

def overlap_analysis(surprise_records, disagreement_records, top_pct=1.0,
                     min_disagree=3, n_perm=1000, seed=691):
    rng = np.random.RandomState(seed)
    # Index disagreement by (folio, line, idx)
    disagree_set = {}
    for r in disagreement_records:
        key = (r['folio'], r['line'], r['token_idx'])
        disagree_set[key] = r['n_disagree_with_h']

    # Add disagreement to each surprise record
    for r in surprise_records:
        key = (r['folio'], r['line'], r['token_idx'])
        r['transcriber_n_disagree'] = disagree_set.get(key, 0)

    # Filter out hapax-only (tokens that appear ≤ 1 time)
    token_freq = Counter(r['token'] for r in surprise_records)
    eligible = [r for r in surprise_records if token_freq[r['token']] >= 2]
    print(f"  Eligible (non-hapax) tokens: {len(eligible)} / {len(surprise_records)}")

    # Sort by surprise (descending)
    eligible.sort(key=lambda x: -x['surprise'])
    n_top = max(1, int(len(eligible) * top_pct / 100))
    top = eligible[:n_top]

    # Disagreement set (positions with ≥3 transcriber-disagreement)
    flagged_top = [r for r in top if r['transcriber_n_disagree'] >= min_disagree]
    overlap_rate = len(flagged_top) / len(top)

    # Baseline: rate of disagreement in random sample of same size from eligible
    eligible_disagree_rate = sum(1 for r in eligible if r['transcriber_n_disagree'] >= min_disagree) / len(eligible)

    # Permutation null: random samples
    null_overlaps = []
    for _ in range(n_perm):
        sample = [eligible[i] for i in rng.choice(len(eligible), size=n_top, replace=False)]
        n = sum(1 for r in sample if r['transcriber_n_disagree'] >= min_disagree)
        null_overlaps.append(n / n_top)
    null_overlaps = np.array(null_overlaps)
    p_value = float(np.mean(null_overlaps >= overlap_rate))

    return {
        'n_top': n_top,
        'top_pct': top_pct,
        'min_disagree_threshold': min_disagree,
        'top_disagreement_rate': overlap_rate,
        'eligible_baseline_rate': float(eligible_disagree_rate),
        'enrichment': float(overlap_rate / max(eligible_disagree_rate, 1e-6)),
        'permutation_p_value': p_value,
        'success_per_prereg': bool(overlap_rate >= 0.30),
        'top_token_examples': [
            {
                'token': r['token'], 'folio': r['folio'], 'line': r['line'],
                'idx': r['token_idx'], 'surprise': r['surprise'],
                'n_disagree': r['transcriber_n_disagree'],
            } for r in top[:30]
        ],
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

    out_dir = PHASE_DIR / 'results' / 'anomaly'
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Per-token surprise
    print("\n[1] Computing per-token pseudo-likelihood...")
    all_lines = []
    for split in ['train', 'val', 'test']:
        all_lines.extend(load_corpus_lines(PHASE_DIR / 'data' / f'corpus_{split}.jsonl'))
    print(f"  Total lines: {len(all_lines)}")
    with_tag = (args.variant == 'with_tag')
    surprise_records = compute_token_surprise(model, tokenizer, all_lines, with_tag, device)
    print(f"  Computed surprise for {len(surprise_records)} token instances")

    # Save
    surprise_path = out_dir / f'lm_surprise_per_token_{args.variant}.jsonl'
    with open(surprise_path, 'w', encoding='utf-8') as f:
        for r in surprise_records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"  Saved: {surprise_path}")

    # 2. Transcriber disagreement
    print("\n[2] Building transcriber disagreement table...")
    disagreement_records = build_transcriber_disagreement()
    print(f"  Positions with ≥2 transcribers: {len(disagreement_records)}")
    n_disagree_3 = sum(1 for r in disagreement_records if r['n_disagree_with_h'] >= 3)
    print(f"  Positions with ≥3 disagree-with-H: {n_disagree_3}")

    disagree_path = out_dir / 'transcriber_disagreement.jsonl'
    with open(disagree_path, 'w', encoding='utf-8') as f:
        for r in disagreement_records:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"  Saved: {disagree_path}")

    # 3. Overlap analysis at multiple top-pct levels
    print("\n[3] Cross-reference top-surprise vs disagreement...")
    reports = {}
    for top_pct in [0.5, 1.0, 2.0, 5.0]:
        print(f"\n  -- top {top_pct}% --")
        report = overlap_analysis(surprise_records, disagreement_records, top_pct=top_pct)
        reports[f'top_{top_pct}pct'] = report
        print(f"    n_top: {report['n_top']}")
        print(f"    overlap (>=3 disagree): {report['top_disagreement_rate']:.3f}")
        print(f"    baseline rate: {report['eligible_baseline_rate']:.3f}")
        print(f"    enrichment: {report['enrichment']:.2f}x")
        print(f"    perm p: {report['permutation_p_value']:.4f}")
        print(f"    pre-reg success (>=0.30): {report['success_per_prereg']}")

    # Save report
    report_path = out_dir / f'overlap_report_{args.variant}.json'
    report_path.write_text(json.dumps(reports, indent=2, ensure_ascii=False))
    print(f"\nSaved: {report_path}")


if __name__ == '__main__':
    main()
