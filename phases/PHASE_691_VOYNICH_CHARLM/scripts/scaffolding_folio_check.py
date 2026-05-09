#!/usr/bin/env python3
"""
Phase 691.5d: Anomaly check on candidate "scaffolding" folios (per crazy-expert).

If f66r is a Rosetta-Stone-style decoding key (Phase 684), other folios
suspected of containing instructional/scaffolding structure should also flag
as anomaly-rich. Test:
  - f57v (numerology, AZC ring, C763/C764)
  - f49v (L-label / example alternation, C497)
  - f116v (last folio, mixed-script, structurally isolated)
  - The rosettes foldout folios (f86v3-f86v6)

Method: for each candidate folio, compute mean surprise rank of its tokens
relative to all other folios. Compare to non-candidate baseline.
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

PHASE_DIR = Path(__file__).resolve().parents[1]

SCAFFOLDING_CANDIDATES = {
    'f66r': 'character-key page (Phase 684)',
    'f57v': 'numerology / AZC ring (C763/C764)',
    'f49v': 'L-label / example alternation (C497)',
    'f116v': 'last folio, mixed-script, isolated',
    'f86v3': 'rosettes foldout',
    'f86v4': 'rosettes foldout',
    'f86v5': 'rosettes foldout',
    'f86v6': 'rosettes foldout',
}


def main():
    surprise_path = PHASE_DIR / 'results' / 'anomaly' / 'lm_surprise_per_token_without_tag.jsonl'
    print(f"Loading {surprise_path}...")
    records = []
    with open(surprise_path, encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line))
    print(f"  {len(records)} records")

    # Compute folio-mean surprise (length-stratified within folio is unfair due to small N;
    # use raw mean and z-score across all folios)
    by_folio = defaultdict(list)
    for r in records:
        by_folio[r['folio']].append(r['surprise'])

    folio_means = {f: float(np.mean(s)) for f, s in by_folio.items() if len(s) >= 5}
    folio_n = {f: len(s) for f, s in by_folio.items()}

    all_means = list(folio_means.values())
    overall_mean = np.mean(all_means)
    overall_std = np.std(all_means)
    folio_z = {f: (m - overall_mean) / overall_std for f, m in folio_means.items()}
    rank = sorted(folio_means.keys(), key=lambda f: -folio_means[f])
    rank_pos = {f: i for i, f in enumerate(rank)}

    print(f"\nTotal folios with >=5 tokens: {len(folio_means)}")
    print(f"Overall mean surprise: {overall_mean:.3f} (sd {overall_std:.3f})")

    # Top-30 most surprising folios
    print(f"\nTop-30 highest-mean-surprise folios:")
    print(f"  {'rank':>4s}  {'folio':>7s}  {'n':>4s}  {'mean':>6s}  {'z':>6s}")
    for i, f in enumerate(rank[:30]):
        marker = ' ← scaffold candidate' if f in SCAFFOLDING_CANDIDATES else ''
        print(f"  {i+1:>4d}  {f:>7s}  {folio_n[f]:>4d}  {folio_means[f]:>6.3f}  {folio_z[f]:>+6.2f}{marker}")

    # Scaffolding candidate report
    print(f"\nScaffolding candidate folios:")
    print(f"  {'folio':>7s}  {'n':>4s}  {'mean':>6s}  {'z':>6s}  {'rank':>5s}/{len(rank):<5d}  description")
    rows = []
    for f, desc in SCAFFOLDING_CANDIDATES.items():
        if f not in folio_means:
            print(f"  {f:>7s}  --   (no data, may not be in corpus)  {desc}")
            continue
        rows.append({
            'folio': f, 'n_tokens': folio_n[f],
            'mean_surprise': folio_means[f], 'z': float(folio_z[f]),
            'rank': rank_pos[f] + 1, 'total_folios': len(rank), 'description': desc,
        })
        marker = ' ← FLAGGED' if folio_z[f] >= 1.0 else ''
        print(f"  {f:>7s}  {folio_n[f]:>4d}  {folio_means[f]:>6.3f}  {folio_z[f]:>+6.2f}  {rank_pos[f]+1:>5d}/{len(rank):<5d}  {desc}{marker}")

    n_flagged = sum(1 for r in rows if r['z'] >= 1.0)
    print(f"\nSummary: {n_flagged}/{len(rows)} candidates flagged at z >= 1.0")

    out_path = PHASE_DIR / 'results' / 'anomaly' / 'scaffolding_folio_check.json'
    out_path.write_text(json.dumps({
        'overall_mean': float(overall_mean),
        'overall_std': float(overall_std),
        'top_30_folios': [
            {'folio': f, 'n': folio_n[f], 'mean': folio_means[f], 'z': float(folio_z[f])}
            for f in rank[:30]
        ],
        'scaffolding_candidates': rows,
        'n_flagged_at_z_ge_1': n_flagged,
    }, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
