#!/usr/bin/env python3
"""
Phase 691.x: Systematic scaffolding-folio inventory.

Applies the f57v structural analysis methodology to every high-surprise
folio (rank 1-30 from Phase 691.5d) to classify each as:
  - SCAFFOLDING_LIKE: periodic/tabular structure, fixed scaffold + variable slot
  - OPERATIONAL_DIAGRAM: AZC ring or zodiac-style content (rare tokens but no
    periodic table structure)
  - ANOMALOUS_OTHER: rare/unique content, no clear category

Features computed per folio:
  - Token length distribution (1-char dominance suggests scaffolding)
  - Periodicity at lag 4-20 (high match = repetitive structure)
  - Repetition ratio (unique_tokens / total_tokens)
  - Placement code distribution (R-ring vs P-paragraph dominant)
  - Char-class enrichment vs corpus baseline (x, p, f, h)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PHASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript


def folio_features(folio, tokens):
    """Compute scaffolding-related features for a single folio."""
    if not tokens:
        return None
    words = [t.word for t in tokens]
    placements = [t.placement or '' for t in tokens]

    # Length distribution
    lens = [len(w) for w in words]
    n = len(words)
    n_single = sum(1 for L in lens if L == 1)
    n_short = sum(1 for L in lens if L <= 3)
    avg_len = sum(lens) / n
    single_pct = n_single / n
    short_pct = n_short / n

    # Repetition: unique tokens / total
    unique_pct = len(set(words)) / n

    # Placement-code distribution
    placement_prefixes = Counter(p[0] if p else '?' for p in placements)
    ring_pct = placement_prefixes.get('R', 0) / n
    para_pct = placement_prefixes.get('P', 0) / n

    # Char-class enrichment
    all_chars = ''.join(words)
    nc = len(all_chars)
    x_rate = all_chars.count('x') / max(1, nc)
    p_rate = all_chars.count('p') / max(1, nc)
    f_rate = all_chars.count('f') / max(1, nc)
    h_rate = all_chars.count('h') / max(1, nc)

    # Periodicity: for each lag from 4 to 20, count same-token at that lag
    # Compute over a single ring sequence at a time (R-prefix tokens)
    best_lag = 0
    best_match_pct = 0
    for ring_code in set(placement_prefixes.elements()):
        if ring_code != 'R':
            continue
    # Specifically test on R-prefix sequence (rings)
    by_full_placement = defaultdict(list)
    for w, p in zip(words, placements):
        if p and p.startswith('R'):
            by_full_placement[p].append(w)
    for ring_label, seq in by_full_placement.items():
        if len(seq) < 8:
            continue
        for lag in range(4, min(21, len(seq))):
            matches = sum(1 for i in range(len(seq) - lag) if seq[i] == seq[i + lag])
            possible = max(1, len(seq) - lag)
            pct = matches / possible
            if pct > best_match_pct:
                best_match_pct = pct
                best_lag = lag

    return {
        'folio': folio,
        'n_tokens': n,
        'avg_len': avg_len,
        'single_pct': single_pct,
        'short_pct': short_pct,
        'unique_pct': unique_pct,
        'ring_pct': ring_pct,
        'para_pct': para_pct,
        'x_rate': x_rate,
        'p_rate': p_rate,
        'f_rate': f_rate,
        'h_rate': h_rate,
        'best_lag': best_lag,
        'best_match_pct': best_match_pct,
    }


def classify(features, baseline):
    """Classify folio as SCAFFOLDING / OPERATIONAL / ANOMALOUS."""
    f = features
    score = 0
    reasons = []

    # Strong scaffolding signals
    if f['best_match_pct'] >= 0.5:
        score += 4
        reasons.append(f'high lag-{f["best_lag"]} periodicity ({f["best_match_pct"]:.2f})')
    elif f['best_match_pct'] >= 0.2:
        score += 2
        reasons.append(f'moderate lag-{f["best_lag"]} periodicity ({f["best_match_pct"]:.2f})')

    if f['single_pct'] >= 0.4:
        score += 3
        reasons.append(f'single-char dominant ({100*f["single_pct"]:.0f}%)')
    elif f['single_pct'] >= 0.15:
        score += 1
        reasons.append(f'single-char enriched ({100*f["single_pct"]:.0f}%)')

    if f['unique_pct'] <= 0.5:
        score += 2
        reasons.append(f'high repetition (unique pct {100*f["unique_pct"]:.0f}%)')

    # Char enrichment signals (relative to baseline ~corpus)
    x_enrich = f['x_rate'] / max(baseline['x_rate'], 1e-6)
    f_enrich = f['f_rate'] / max(baseline['f_rate'], 1e-6)
    if x_enrich >= 5:
        score += 2
        reasons.append(f'x-enriched {x_enrich:.1f}x')
    if f_enrich >= 4:
        score += 2
        reasons.append(f'f-enriched {f_enrich:.1f}x')

    # Disqualifiers (operational diagram indicators)
    if f['ring_pct'] > 0.7 and f['best_match_pct'] < 0.15:
        score -= 1
        reasons.append('ring-dominant but no periodicity (operational diagram?)')

    # Classification
    if score >= 5:
        category = 'SCAFFOLDING_LIKE'
    elif score >= 3:
        category = 'POSSIBLE_SCAFFOLDING'
    elif f['ring_pct'] >= 0.5:
        category = 'OPERATIONAL_DIAGRAM'
    else:
        category = 'ANOMALOUS_OTHER'

    return category, score, reasons


def main():
    # Load top-30 from Phase 691.5d
    scaff_path = PHASE_DIR / 'results' / 'anomaly' / 'scaffolding_folio_check.json'
    data = json.loads(scaff_path.read_text())
    top_30 = data['top_30_folios']

    # Also include known controls
    additional = ['f66r', 'f49v', 'f80r', 'f75r', 'f1r', 'f95v', 'f105v']
    folios_to_check = list(set([f['folio'] for f in top_30] + additional))
    print(f"Analyzing {len(folios_to_check)} folios...")

    # Load tokens from H-track
    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.all(h_only=True):
        if tok.word and not tok.is_uncertain:
            by_folio[tok.folio].append(tok)

    # Compute corpus baseline rates (for char enrichment)
    all_chars = ''.join(t.word for f in by_folio for t in by_folio[f])
    nc = len(all_chars)
    baseline = {
        'x_rate': all_chars.count('x') / nc,
        'p_rate': all_chars.count('p') / nc,
        'f_rate': all_chars.count('f') / nc,
        'h_rate': all_chars.count('h') / nc,
    }
    print(f"\nCorpus baseline: x={baseline['x_rate']:.4f}, p={baseline['p_rate']:.4f}, f={baseline['f_rate']:.4f}, h={baseline['h_rate']:.4f}")

    # Compute features per folio
    results = []
    for folio in folios_to_check:
        toks = by_folio.get(folio, [])
        if len(toks) < 5:
            continue
        feat = folio_features(folio, toks)
        if not feat:
            continue
        category, score, reasons = classify(feat, baseline)
        feat['category'] = category
        feat['score'] = score
        feat['reasons'] = reasons
        # Get z from existing data
        for entry in top_30:
            if entry['folio'] == folio:
                feat['z'] = entry['z']
                feat['rank'] = top_30.index(entry) + 1
                break
        else:
            feat['z'] = None
            feat['rank'] = None
        results.append(feat)

    # Sort by score (scaffolding likelihood) descending
    results.sort(key=lambda r: -r['score'])

    print(f"\n=== SCAFFOLDING-LIKELIHOOD RANKING ===")
    print(f"{'folio':>7s}  {'z':>6s}  {'rank':>4s}  {'n':>4s}  {'1ch%':>4s}  {'lag':>3s}  {'match':>5s}  {'unq%':>4s}  {'ring%':>5s}  {'x×':>4s}  {'f×':>4s}  {'score':>5s}  {'category':>22s}")
    for r in results:
        z_str = f"{r['z']:+.2f}" if r['z'] is not None else '   .  '
        rank_str = f"{r['rank']}" if r['rank'] is not None else ' . '
        x_e = r['x_rate'] / max(baseline['x_rate'], 1e-6)
        f_e = r['f_rate'] / max(baseline['f_rate'], 1e-6)
        print(f"  {r['folio']:>7s}  {z_str}  {rank_str:>4s}  {r['n_tokens']:>4d}  "
              f"{100*r['single_pct']:>4.0f}  {r['best_lag']:>3d}  {r['best_match_pct']:>5.2f}  "
              f"{100*r['unique_pct']:>4.0f}  {100*r['ring_pct']:>5.0f}  "
              f"{x_e:>4.1f}  {f_e:>4.1f}  {r['score']:>5d}  {r['category']:>22s}")

    # Detailed report on top scaffolding candidates
    print(f"\n=== Top-5 scaffolding candidates (detail) ===")
    scaff_candidates = [r for r in results if r['category'] in ('SCAFFOLDING_LIKE', 'POSSIBLE_SCAFFOLDING')]
    for r in scaff_candidates[:5]:
        print(f"\n  {r['folio']}: score={r['score']}, category={r['category']}")
        print(f"    z-score: {r.get('z')}, rank: {r.get('rank')}")
        print(f"    Reasons: {'; '.join(r['reasons'])}")

    # Save
    out_path = PHASE_DIR / 'results' / 'anomaly' / 'scaffolding_inventory.json'
    out_path.write_text(json.dumps({
        'baseline_rates': baseline,
        'folios_analyzed': len(results),
        'scaffolding_like_count': sum(1 for r in results if r['category'] == 'SCAFFOLDING_LIKE'),
        'possible_scaffolding_count': sum(1 for r in results if r['category'] == 'POSSIBLE_SCAFFOLDING'),
        'operational_count': sum(1 for r in results if r['category'] == 'OPERATIONAL_DIAGRAM'),
        'anomalous_count': sum(1 for r in results if r['category'] == 'ANOMALOUS_OTHER'),
        'results': results,
    }, indent=2))
    print(f"\nSaved: {out_path}")


if __name__ == '__main__':
    main()
