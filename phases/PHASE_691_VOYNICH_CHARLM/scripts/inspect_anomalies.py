#!/usr/bin/env python3
"""Inspect top-surprise tokens from anomaly detection."""
import json
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parents[1]
report = json.loads((PHASE_DIR / 'results' / 'anomaly' / 'overlap_report_without_tag.json').read_text())

print('Top-30 LM-surprise tokens (top 1%):')
hdr = f"{'token':>12s}  {'folio':>7s}  {'line':>4s}  {'surprise':>9s}  {'n_dis':>5s}"
print(hdr)
print('-' * len(hdr))
for e in report['top_1.0pct']['top_token_examples'][:30]:
    print(f"  {e['token']:>12s}  {e['folio']:>7s}  L{e['line']:>3s}  {e['surprise']:9.3f}  {e['n_disagree']:>5d}")

print()
print('Summary across thresholds:')
print(f"{'top%':>6s}  {'n':>6s}  {'overlap_rate':>12s}  {'baseline':>9s}  {'enrich':>7s}  {'p':>6s}")
for k in ['top_0.5pct', 'top_1.0pct', 'top_2.0pct', 'top_5.0pct']:
    r = report[k]
    print(f"  {r['top_pct']:>4.1f}  {r['n_top']:>6d}  {r['top_disagreement_rate']:>12.3f}  {r['eligible_baseline_rate']:>9.3f}  {r['enrichment']:>7.2f}  {r['permutation_p_value']:>6.4f}")
