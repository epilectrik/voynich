#!/usr/bin/env python3
"""
Phase 691.4b: Stratified within-length anomaly detection.

Phase 691.4's top-1% surprise list was dominated by single-char tokens (length
anomaly). To surface STRUCTURAL/SEMANTIC anomalies, rank tokens by surprise
WITHIN each length bucket. A 5-char token in the top 1% of 5-char-token
surprise is a more interesting anomaly than a 1-char token.

Cross-reference stratified top-1% against transcriber disagreement.
"""
import argparse
import functools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

print = functools.partial(print, flush=True)

import numpy as np

PHASE_DIR = Path(__file__).resolve().parents[1]


def load_jsonl(path):
    out = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            out.append(json.loads(line))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', default='without_tag')
    parser.add_argument('--seed', type=int, default=691)
    args = parser.parse_args()

    surprise_path = PHASE_DIR / 'results' / 'anomaly' / f'lm_surprise_per_token_{args.variant}.jsonl'
    disagree_path = PHASE_DIR / 'results' / 'anomaly' / 'transcriber_disagreement.jsonl'
    print(f"Loading {surprise_path}...")
    surprise = load_jsonl(surprise_path)
    print(f"  {len(surprise):,} surprise records")
    print(f"Loading {disagree_path}...")
    disagree = load_jsonl(disagree_path)
    print(f"  {len(disagree):,} disagreement records")

    # Index disagreement
    disagree_idx = {(r['folio'], r['line'], r['token_idx']): r['n_disagree_with_h'] for r in disagree}
    for r in surprise:
        key = (r['folio'], r['line'], r['token_idx'])
        r['n_disagree'] = disagree_idx.get(key, 0)

    # Bucket by token character length
    by_len = defaultdict(list)
    for r in surprise:
        L = len(r['token'])
        by_len[L].append(r)

    print(f"\nLength distribution:")
    print(f"  {'L':>3s}  {'n':>7s}  {'mean_surprise':>13s}  {'sd_surprise':>11s}")
    for L in sorted(by_len.keys()):
        recs = by_len[L]
        s = np.array([r['surprise'] for r in recs])
        print(f"  {L:>3d}  {len(recs):>7d}  {s.mean():>13.3f}  {s.std():>11.3f}")

    # Within each length, take top-1% by surprise
    rng = np.random.RandomState(args.seed)
    top_by_length = {}
    overall_top = []
    overall_eligible_disagree = 0
    overall_eligible_total = 0
    print(f"\nWithin-length top 1% surprise (where N >= 100):")
    print(f"  {'L':>3s}  {'n':>5s}  {'top':>4s}  {'overlap':>9s}  {'baseline':>9s}  {'enrich':>7s}")
    for L in sorted(by_len.keys()):
        recs = by_len[L]
        if len(recs) < 100:
            continue
        recs_sorted = sorted(recs, key=lambda r: -r['surprise'])
        n_top = max(1, len(recs) // 100)
        top = recs_sorted[:n_top]
        overlap = sum(1 for r in top if r['n_disagree'] >= 3) / n_top
        baseline = sum(1 for r in recs if r['n_disagree'] >= 3) / len(recs)
        enrichment = overlap / max(baseline, 1e-6)
        top_by_length[L] = {
            'n': len(recs), 'n_top': n_top,
            'overlap_rate': float(overlap), 'baseline_rate': float(baseline),
            'enrichment': float(enrichment),
            'top_examples': [
                {'token': r['token'], 'folio': r['folio'], 'line': r['line'],
                 'surprise': r['surprise'], 'n_disagree': r['n_disagree']}
                for r in top[:5]
            ],
        }
        overall_top.extend(top)
        overall_eligible_disagree += sum(1 for r in recs if r['n_disagree'] >= 3)
        overall_eligible_total += len(recs)
        print(f"  {L:>3d}  {len(recs):>5d}  {n_top:>4d}  {overlap:>9.3f}  {baseline:>9.3f}  {enrichment:>7.2f}")

    # Aggregate stratified-top stats
    overall_overlap = sum(1 for r in overall_top if r['n_disagree'] >= 3) / len(overall_top)
    overall_baseline = overall_eligible_disagree / overall_eligible_total
    print(f"\nStratified aggregate:")
    print(f"  Total stratified-top tokens: {len(overall_top)}")
    print(f"  Overlap with >=3 disagree: {overall_overlap:.3f}")
    print(f"  Eligible baseline (across lengths >=100): {overall_baseline:.3f}")
    print(f"  Aggregate enrichment: {overall_overlap / overall_baseline:.2f}x")

    # Top-30 of stratified-top by surprise
    overall_top_sorted = sorted(overall_top, key=lambda r: -r['surprise'])
    print(f"\nTop-30 stratified-top tokens (excluding length-1 dominance):")
    print(f"  {'token':>12s}  {'L':>2s}  {'folio':>7s}  {'line':>4s}  {'surprise':>9s}  {'dis':>4s}")
    n_shown = 0
    for r in overall_top_sorted:
        if len(r['token']) <= 1:
            continue
        print(f"  {r['token']:>12s}  {len(r['token']):>2d}  {r['folio']:>7s}  L{r['line']:>3s}  {r['surprise']:>9.3f}  {r['n_disagree']:>4d}")
        n_shown += 1
        if n_shown >= 30:
            break

    # Save
    out = {
        'method': 'within-length top-1% surprise + transcriber disagreement overlap',
        'by_length': {str(k): v for k, v in top_by_length.items()},
        'aggregate': {
            'total_top_tokens': len(overall_top),
            'overall_overlap_rate': float(overall_overlap),
            'overall_baseline_rate': float(overall_baseline),
            'enrichment': float(overall_overlap / overall_baseline),
        },
        'top_30_excluding_length_1': [
            {'token': r['token'], 'L': len(r['token']), 'folio': r['folio'],
             'line': r['line'], 'surprise': r['surprise'], 'n_disagree': r['n_disagree']}
            for r in [rec for rec in overall_top_sorted if len(rec['token']) > 1][:30]
        ],
    }
    out_path = PHASE_DIR / 'results' / 'anomaly' / f'stratified_anomaly_{args.variant}.json'
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
