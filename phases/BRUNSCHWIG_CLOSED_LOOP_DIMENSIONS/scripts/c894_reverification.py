#!/usr/bin/env python3
"""
C894 Reverification: Does REGIME_4 recovery specialization survive
the new authoritative regime mapping?

C894 claimed: Recovery-specialized folios (HIGH_K paragraph signature)
cluster in REGIME_4 (33% vs 0-3% other REGIMEs). Chi-square = 28.41, p = 0.0001.

The old regime mapping was broken (two sources agreed on only 39% of folios).
This script re-tests C894 against the new GMM-based regime mapping.

Approach:
1. Recompute paragraph classifications from transcript (regime-independent)
2. Cross-tabulate folio specialization with NEW regime mapping
3. Run chi-square and Fisher exact tests
4. Report whether C894 survives, weakens, or dies
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'

# ---- Load new authoritative regime mapping ----
with open(PROJECT_ROOT / 'data' / 'regime_folio_mapping.json') as f:
    regime_data = json.load(f)

folio_to_regime = {
    folio: data['regime']
    for folio, data in regime_data['regime_assignments'].items()
}

folio_to_prob = {
    folio: data['probability']
    for folio, data in regime_data['regime_assignments'].items()
}

# ---- Reconstruct paragraph classifications (regime-independent) ----
tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

folio_line_tokens = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section


def get_paragraphs(folio):
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []
    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))
    if current_para:
        paragraphs.append(current_para)
    return paragraphs


def classify_paragraph(words):
    if len(words) < 10:
        return None
    k = sum(w.count('k') for w in words)
    h = sum(w.count('h') for w in words)
    e = sum(w.count('e') for w in words)
    total_kernel = k + h + e
    if total_kernel < 10:
        return None
    k_pct = 100 * k / total_kernel
    h_pct = 100 * h / total_kernel
    if k_pct > 35:
        return 'HIGH_K'
    elif h_pct > 35:
        return 'HIGH_H'
    else:
        return 'BALANCED'


# Collect paragraphs
all_paragraphs = []
for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    for i, p in enumerate(paras):
        words = [t.word for line_num, tokens in p for t in tokens]
        ptype = classify_paragraph(words)
        if ptype is None:
            continue
        all_paragraphs.append({
            'folio': folio,
            'section': folio_section.get(folio, 'UNKNOWN'),
            'ptype': ptype,
            'n_tokens': len(words),
        })

# Folio-level specialization
folio_types = defaultdict(Counter)
for p in all_paragraphs:
    folio_types[p['folio']][p['ptype']] += 1

# Classify folios
folio_spec = {}
for folio, counts in folio_types.items():
    total = sum(counts.values())
    if total < 3:
        folio_spec[folio] = 'TOO_FEW'
        continue
    k_pct = 100 * counts.get('HIGH_K', 0) / total
    h_pct = 100 * counts.get('HIGH_H', 0) / total
    if k_pct >= 50:
        folio_spec[folio] = 'RECOVERY'
    elif h_pct >= 70:
        folio_spec[folio] = 'DISTILL'
    else:
        folio_spec[folio] = 'MIXED'

# ---- Cross-tabulate with NEW regime mapping ----
print("=" * 70)
print("C894 REVERIFICATION")
print("Using NEW authoritative regime mapping (data/regime_folio_mapping.json)")
print("=" * 70)

print(f"\nTotal paragraphs: {len(all_paragraphs)}")
print(f"Folios with paragraph data: {len(folio_types)}")
print(f"Folios with >=3 paragraphs: {sum(1 for v in folio_spec.values() if v != 'TOO_FEW')}")

# Build regime x specialization table
regime_spec = defaultdict(Counter)
for folio, spec in folio_spec.items():
    if spec == 'TOO_FEW':
        continue
    regime = folio_to_regime.get(folio)
    if regime is None:
        continue
    regime_spec[regime][spec] += 1

print(f"\n{'REGIME':<12} {'RECOVERY':<12} {'DISTILL':<12} {'MIXED':<12} {'Total':<8} {'%Recovery':<12}")
print("-" * 68)

regimes = sorted(regime_spec.keys())
contingency_rows = []

for regime in regimes:
    counts = regime_spec[regime]
    rec = counts.get('RECOVERY', 0)
    dist = counts.get('DISTILL', 0)
    mixed = counts.get('MIXED', 0)
    total = rec + dist + mixed
    pct_rec = 100 * rec / total if total > 0 else 0
    print(f"{regime:<12} {rec:<12} {dist:<12} {mixed:<12} {total:<8} {pct_rec:.1f}%")
    contingency_rows.append([rec, dist, mixed])

# Chi-square on full contingency table
contingency = np.array(contingency_rows)
print(f"\nContingency table shape: {contingency.shape}")

# Only run chi-square if we have enough data
if contingency.shape[0] >= 2 and contingency.shape[1] >= 2:
    chi2, p_val, dof, expected = scipy_stats.chi2_contingency(contingency)
    print(f"\nChi-square test (REGIME x SPECIALIZATION):")
    print(f"  chi2 = {chi2:.2f}")
    print(f"  df = {dof}")
    print(f"  p = {p_val:.6f}")

    if p_val < 0.001:
        print(f"  -> HIGHLY SIGNIFICANT")
    elif p_val < 0.05:
        print(f"  -> SIGNIFICANT")
    else:
        print(f"  -> NOT SIGNIFICANT")

# Fisher exact for RECOVERY vs NOT, by regime (pairwise)
print(f"\n{'='*70}")
print("PAIRWISE FISHER EXACT TESTS: RECOVERY vs NOT by REGIME")
print("="*70)

for regime in regimes:
    rec = regime_spec[regime].get('RECOVERY', 0)
    not_rec = sum(regime_spec[regime].values()) - rec
    other_rec = sum(regime_spec[r].get('RECOVERY', 0) for r in regimes if r != regime)
    other_not = sum(sum(regime_spec[r].values()) for r in regimes if r != regime) - other_rec

    table = np.array([[rec, not_rec], [other_rec, other_not]])
    odds, p_fisher = scipy_stats.fisher_exact(table, alternative='two-sided')
    total_in_regime = rec + not_rec
    pct = 100 * rec / total_in_regime if total_in_regime > 0 else 0
    sig = "***" if p_fisher < 0.001 else "**" if p_fisher < 0.01 else "*" if p_fisher < 0.05 else ""
    print(f"  {regime}: {rec}/{total_in_regime} recovery ({pct:.0f}%)  OR={odds:.2f}  p={p_fisher:.4f} {sig}")

# ---- K/(K+H) ratio by regime (continuous measure, not threshold) ----
print(f"\n{'='*70}")
print("CONTINUOUS MEASURE: K/(K+H) RATIO BY REGIME")
print("="*70)

folio_kh_ratio = {}
for folio, counts in folio_types.items():
    k = counts.get('HIGH_K', 0)
    h = counts.get('HIGH_H', 0)
    if k + h > 0:
        folio_kh_ratio[folio] = k / (k + h)

regime_ratios = defaultdict(list)
for folio, ratio in folio_kh_ratio.items():
    regime = folio_to_regime.get(folio)
    if regime:
        regime_ratios[regime].append(ratio)

print(f"\n{'REGIME':<12} {'Mean K/(K+H)':<15} {'Std':<10} {'N':<6}")
print("-" * 43)
for regime in sorted(regime_ratios.keys()):
    vals = regime_ratios[regime]
    print(f"{regime:<12} {np.mean(vals):<15.3f} {np.std(vals):<10.3f} {len(vals):<6}")

# Kruskal-Wallis test
groups = [regime_ratios[r] for r in sorted(regime_ratios.keys()) if len(regime_ratios[r]) > 1]
if len(groups) >= 2:
    h_stat, p_kw = scipy_stats.kruskal(*groups)
    print(f"\nKruskal-Wallis H={h_stat:.3f}, p={p_kw:.4f}")
    if p_kw < 0.05:
        print("  -> Significant difference in K/(K+H) across REGIMEs")
    else:
        print("  -> No significant difference in K/(K+H) across REGIMEs")

# ---- Section confound control ----
print(f"\n{'='*70}")
print("SECTION CONFOUND CONTROL")
print("Within same section, does REGIME still predict K/(K+H)?")
print("="*70)

for section in sorted(set(folio_section.values())):
    section_folios = [f for f, s in folio_section.items() if s == section]
    section_regime_ratios = defaultdict(list)
    for folio in section_folios:
        if folio in folio_kh_ratio and folio in folio_to_regime:
            section_regime_ratios[folio_to_regime[folio]].append(folio_kh_ratio[folio])

    if sum(len(v) for v in section_regime_ratios.values()) < 5:
        continue

    print(f"\nSection {section}:")
    for regime in sorted(section_regime_ratios.keys()):
        vals = section_regime_ratios[regime]
        if vals:
            print(f"  {regime}: K/(K+H) = {np.mean(vals):.3f} (n={len(vals)})")

    groups_s = [v for v in section_regime_ratios.values() if len(v) > 1]
    if len(groups_s) >= 2:
        h_stat, p_kw = scipy_stats.kruskal(*groups_s)
        print(f"  Kruskal-Wallis H={h_stat:.3f}, p={p_kw:.4f}")

# ---- Recovery folio details ----
print(f"\n{'='*70}")
print("RECOVERY-SPECIALIZED FOLIOS (>=50% HIGH_K, >=3 paragraphs)")
print("="*70)

recovery_folios = [f for f, s in folio_spec.items() if s == 'RECOVERY']
print(f"\n{'Folio':<12} {'Section':<10} {'REGIME':<12} {'Prob':<8} {'HIGH_K':<8} {'HIGH_H':<8} {'BAL':<8}")
print("-" * 66)
for folio in sorted(recovery_folios):
    sec = folio_section.get(folio, '?')
    reg = folio_to_regime.get(folio, '?')
    prob = folio_to_prob.get(folio, 0)
    counts = folio_types[folio]
    print(f"{folio:<12} {sec:<10} {reg:<12} {prob:<8.3f} {counts.get('HIGH_K',0):<8} {counts.get('HIGH_H',0):<8} {counts.get('BALANCED',0):<8}")

# ---- Compare with OLD C894 claim ----
print(f"\n{'='*70}")
print("COMPARISON WITH OLD C894 CLAIM")
print("="*70)

print("""
OLD C894 (broken regime mapping):
  REGIME_4: 33% recovery-specialized (8/24), K/(K+H) = 0.32
  REGIME_1: 3% (1/31), K/(K+H) = 0.21
  REGIME_2: 0% (0/10), K/(K+H) = 0.27
  REGIME_3: 0% (0/16), K/(K+H) = 0.10
  Chi-square = 28.41, p = 0.0001
""")

print("NEW (authoritative regime mapping):")
for regime in regimes:
    counts = regime_spec[regime]
    rec = counts.get('RECOVERY', 0)
    total = sum(counts.values())
    pct = 100 * rec / total if total > 0 else 0
    mean_kh = np.mean(regime_ratios.get(regime, [0]))
    print(f"  {regime}: {pct:.0f}% recovery ({rec}/{total}), K/(K+H) = {mean_kh:.3f}")

# ---- Verdict ----
print(f"\n{'='*70}")
print("VERDICT")
print("="*70)

# Determine if recovery concentration is still regime-dependent
any_sig = False
for regime in regimes:
    rec = regime_spec[regime].get('RECOVERY', 0)
    total = sum(regime_spec[regime].values())
    not_rec = total - rec
    other_rec = sum(regime_spec[r].get('RECOVERY', 0) for r in regimes if r != regime)
    other_total = sum(sum(regime_spec[r].values()) for r in regimes if r != regime)
    other_not = other_total - other_rec

    table = np.array([[rec, not_rec], [other_rec, other_not]])
    _, p_fisher = scipy_stats.fisher_exact(table, alternative='two-sided')
    if p_fisher < 0.05 and rec / max(total, 1) > other_rec / max(other_total, 1):
        any_sig = True
        print(f"  {regime} shows SIGNIFICANT recovery concentration (p={p_fisher:.4f})")

if not any_sig:
    print("  NO regime shows significant recovery concentration.")
    print("  C894 does NOT survive with the new regime mapping.")
    verdict = "RETRACT"
else:
    verdict = "SURVIVES_MODIFIED"

# Save results
output = {
    'test': 'C894_reverification',
    'regime_mapping': 'data/regime_folio_mapping.json (v2, GMM k=4)',
    'n_paragraphs': len(all_paragraphs),
    'n_folios_analyzed': sum(1 for v in folio_spec.values() if v != 'TOO_FEW'),
    'regime_specialization': {
        regime: {
            'recovery': regime_spec[regime].get('RECOVERY', 0),
            'distill': regime_spec[regime].get('DISTILL', 0),
            'mixed': regime_spec[regime].get('MIXED', 0),
            'total': sum(regime_spec[regime].values()),
            'pct_recovery': round(100 * regime_spec[regime].get('RECOVERY', 0) / max(sum(regime_spec[regime].values()), 1), 1),
            'mean_kh_ratio': round(float(np.mean(regime_ratios.get(regime, [0]))), 3),
        }
        for regime in regimes
    },
    'recovery_folios': {
        folio: {
            'section': folio_section.get(folio, '?'),
            'regime': folio_to_regime.get(folio, '?'),
            'regime_probability': folio_to_prob.get(folio, 0),
        }
        for folio in recovery_folios
    },
    'chi_square': {
        'chi2': round(float(chi2), 2),
        'df': int(dof),
        'p': round(float(p_val), 6),
    } if contingency.shape[0] >= 2 else None,
    'old_c894': {
        'regime4_recovery_pct': 33,
        'chi2': 28.41,
        'p': 0.0001,
    },
    'verdict': verdict,
}

out_path = RESULTS_DIR / 'c894_reverification.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {out_path}")
