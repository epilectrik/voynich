"""PHASE_714: Refine C645 post-hazard directional anchor.

Five refinement tests of C645's 75.2% post-hazard CHSH dominance:
  R1: per-hazard-class specificity (split class 7 vs 30)
  R2: multi-lag trajectory (next-EN at lag +1, +2, +3, +4)
  R3: triplet patterns (hazard → CHSH → ?)
  R4: pre-hazard signature (lag -1, -2, -3 before hazard)
  R5: folio-level consistency

Each with random-subset null distribution comparison.
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_714_POSTHAZARD_REFINEMENT' / 'results' / 'posthazard_refinement_results.json'

# Reuse C645 framework
HAZ_CLASSES = {7, 30}
N_NULL = 1000


# ---- Data loading (same as LANE_CHANGE_HOLD_ANALYSIS) ----

def load_data():
    """Load token-class map and EN census, build line-organized tokens."""
    with open(ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    with open(ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
        en_census = json.load(f)
    qo_classes = set(en_census['prefix_families']['QO'])
    chsh_classes = set(en_census['prefix_families']['CH_SH'])
    all_en_classes = qo_classes | chsh_classes

    tx = Transcript()
    morph = Morphology()
    lines = defaultdict(list)
    for token in tx.currier_b():
        cls = token_to_class.get(token.word)
        m = morph.extract(token.word)
        en_subfamily = None
        if cls is not None and cls in all_en_classes:
            if m.prefix == 'qo':
                en_subfamily = 'QO'
            elif m.prefix in ('ch', 'sh'):
                en_subfamily = 'CHSH'
        is_haz = cls in HAZ_CLASSES if cls is not None else False
        lines[(token.folio, token.line)].append({
            'word': token.word,
            'class': cls,
            'prefix': m.prefix,
            'en_subfamily': en_subfamily,
            'is_haz': is_haz,
        })
    return lines, all_en_classes


# ---- R1: Per-hazard-class specificity ----

def test_per_class_specificity(lines):
    """For each hazard class (7, 30), measure next-EN CHSH rate."""
    per_class = {cls: {'QO': 0, 'CHSH': 0, 'total': 0} for cls in HAZ_CLASSES}
    for (folio, line_num), toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                continue
            cls = t['class']
            for j in range(i + 1, len(toks)):
                if toks[j]['en_subfamily'] is not None:
                    per_class[cls][toks[j]['en_subfamily']] += 1
                    per_class[cls]['total'] += 1
                    break
    results = {}
    for cls in HAZ_CLASSES:
        d = per_class[cls]
        if d['total'] > 0:
            results[cls] = {
                'qo': d['QO'], 'chsh': d['CHSH'], 'total': d['total'],
                'chsh_rate': d['CHSH'] / d['total'],
                'qo_rate': d['QO'] / d['total'],
            }
    return results


# ---- R2: Multi-lag trajectory ----

def test_multi_lag_trajectory(lines, max_lag=4):
    """For each hazard, record next-EN at lag +1, +2, +3, +4 EN-positions."""
    lag_distributions = {lag: {'QO': 0, 'CHSH': 0, 'total': 0} for lag in range(1, max_lag + 1)}
    for (folio, line_num), toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                continue
            en_count = 0
            for j in range(i + 1, len(toks)):
                if toks[j]['en_subfamily'] is not None:
                    en_count += 1
                    if en_count > max_lag:
                        break
                    lag_distributions[en_count][toks[j]['en_subfamily']] += 1
                    lag_distributions[en_count]['total'] += 1
    results = {}
    for lag, d in lag_distributions.items():
        if d['total'] > 0:
            results[lag] = {
                'qo': d['QO'], 'chsh': d['CHSH'], 'total': d['total'],
                'chsh_rate': d['CHSH'] / d['total'],
                'qo_rate': d['QO'] / d['total'],
            }
    return results


# ---- R3: Triplet patterns (hazard → CHSH → ?) ----

def test_triplet_patterns(lines):
    """For each (hazard, CHSH) pair, what's the next EN?"""
    triplet_counts = {'QO': 0, 'CHSH': 0, 'total': 0}
    # Also condition on (hazard → QO) for comparison
    qo_triplet_counts = {'QO': 0, 'CHSH': 0, 'total': 0}
    for (folio, line_num), toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                continue
            # Find first EN after hazard
            first_en_idx = None
            first_en_subfam = None
            for j in range(i + 1, len(toks)):
                if toks[j]['en_subfamily'] is not None:
                    first_en_idx = j
                    first_en_subfam = toks[j]['en_subfamily']
                    break
            if first_en_idx is None:
                continue
            # Find second EN
            for k in range(first_en_idx + 1, len(toks)):
                if toks[k]['en_subfamily'] is not None:
                    if first_en_subfam == 'CHSH':
                        triplet_counts[toks[k]['en_subfamily']] += 1
                        triplet_counts['total'] += 1
                    elif first_en_subfam == 'QO':
                        qo_triplet_counts[toks[k]['en_subfamily']] += 1
                        qo_triplet_counts['total'] += 1
                    break
    return {
        'hazard_chsh_then': triplet_counts,
        'hazard_qo_then': qo_triplet_counts,
        'chsh_then_chsh_rate': triplet_counts['CHSH'] / max(triplet_counts['total'], 1),
        'qo_then_chsh_rate': qo_triplet_counts['CHSH'] / max(qo_triplet_counts['total'], 1),
    }


# ---- R4: Pre-hazard signature ----

def test_pre_hazard_signature(lines, max_back=3):
    """What characterizes EN positions immediately BEFORE a hazard?"""
    pre_distributions = {lag: {'QO': 0, 'CHSH': 0, 'total': 0} for lag in range(1, max_back + 1)}
    for (folio, line_num), toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                continue
            # Find previous EN tokens (going backward)
            en_count = 0
            for j in range(i - 1, -1, -1):
                if toks[j]['en_subfamily'] is not None:
                    en_count += 1
                    if en_count > max_back:
                        break
                    pre_distributions[en_count][toks[j]['en_subfamily']] += 1
                    pre_distributions[en_count]['total'] += 1
    results = {}
    for lag, d in pre_distributions.items():
        if d['total'] > 0:
            results[lag] = {
                'qo': d['QO'], 'chsh': d['CHSH'], 'total': d['total'],
                'qo_rate': d['QO'] / d['total'],
                'chsh_rate': d['CHSH'] / d['total'],
            }
    return results


# ---- R5: Folio-level consistency ----

def test_folio_consistency(lines):
    """Per-folio post-hazard CHSH rate."""
    per_folio = defaultdict(lambda: {'QO': 0, 'CHSH': 0, 'total': 0})
    for (folio, line_num), toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                continue
            for j in range(i + 1, len(toks)):
                if toks[j]['en_subfamily'] is not None:
                    per_folio[folio][toks[j]['en_subfamily']] += 1
                    per_folio[folio]['total'] += 1
                    break
    folio_rates = []
    folios_with_data = 0
    for folio, d in per_folio.items():
        if d['total'] >= 3:  # Require min 3 events
            folio_rates.append({
                'folio': folio,
                'total': d['total'],
                'chsh_rate': d['CHSH'] / d['total'],
                'qo_rate': d['QO'] / d['total'],
            })
            folios_with_data += 1
    return {
        'per_folio': folio_rates,
        'n_folios_with_data': folios_with_data,
        'mean_chsh_rate_across_folios': float(np.mean([f['chsh_rate'] for f in folio_rates])) if folio_rates else 0,
        'std_chsh_rate_across_folios': float(np.std([f['chsh_rate'] for f in folio_rates])) if folio_rates else 0,
        'fraction_folios_above_baseline_chsh': sum(1 for f in folio_rates if f['chsh_rate'] > 0.447) / max(len(folio_rates), 1),
    }


# ---- Null distribution: random non-hazard "events" ----

def null_distribution_post_event_chsh_rate(lines, n_events, n_null=N_NULL, seed=42):
    """Null: pick random non-hazard tokens of matched count, measure next-EN CHSH rate."""
    rng = np.random.default_rng(seed)
    # Build list of (line_key, position) for non-hazard tokens
    all_positions = []
    for (folio, line_num), toks in lines.items():
        for i, t in enumerate(toks):
            if not t['is_haz']:
                all_positions.append(((folio, line_num), i))
    if len(all_positions) < n_events:
        return np.array([])

    null_rates = []
    for _ in range(n_null):
        sampled = rng.choice(len(all_positions), size=n_events, replace=False)
        qo, chsh, total = 0, 0, 0
        for idx in sampled:
            key, pos = all_positions[idx]
            toks = lines[key]
            for j in range(pos + 1, len(toks)):
                if toks[j]['en_subfamily'] is not None:
                    if toks[j]['en_subfamily'] == 'CHSH':
                        chsh += 1
                    else:
                        qo += 1
                    total += 1
                    break
        if total > 0:
            null_rates.append(chsh / total)
    return np.array(null_rates)


# ---- Main ----

def main():
    print("=" * 80)
    print("PHASE_714 C645 POST-HAZARD DIRECTIONAL ANCHOR REFINEMENT")
    print("=" * 80)

    print("\nLoading data...")
    lines, all_en_classes = load_data()
    print(f"  Loaded {len(lines)} Currier B lines")
    n_haz = sum(1 for toks in lines.values() for t in toks if t['is_haz'])
    print(f"  Total hazard tokens: {n_haz}")
    n_en = sum(1 for toks in lines.values() for t in toks if t['en_subfamily'] is not None)
    print(f"  Total EN tokens: {n_en}")

    # Compute base CHSH rate
    qo_total = sum(1 for toks in lines.values() for t in toks if t['en_subfamily'] == 'QO')
    chsh_total = sum(1 for toks in lines.values() for t in toks if t['en_subfamily'] == 'CHSH')
    base_chsh_rate = chsh_total / (qo_total + chsh_total)
    print(f"  Base CHSH rate: {base_chsh_rate:.4f}")

    # ---- R1: Per-hazard-class specificity ----
    print("\n" + "=" * 80)
    print("REFINEMENT 1: Per-hazard-class specificity")
    print("=" * 80)
    r1 = test_per_class_specificity(lines)
    for cls, d in r1.items():
        print(f"  Hazard class {cls}: total={d['total']}, CHSH={d['chsh']} ({d['chsh_rate']:.3f}), "
              f"QO={d['qo']} ({d['qo_rate']:.3f})")
    if len(r1) >= 2:
        classes = sorted(r1.keys())
        rates = [r1[c]['chsh_rate'] for c in classes]
        spread = max(rates) - min(rates)
        print(f"  Spread between classes: {spread:.3f}")
        r1_specificity = "YES" if spread > 0.05 else "NO"
        print(f"  Class-specific recovery pattern: {r1_specificity}")

    # ---- R2: Multi-lag trajectory ----
    print("\n" + "=" * 80)
    print("REFINEMENT 2: Multi-lag trajectory")
    print("=" * 80)
    r2 = test_multi_lag_trajectory(lines, max_lag=4)
    for lag in sorted(r2.keys()):
        d = r2[lag]
        print(f"  Lag +{lag} EN-position: total={d['total']}, CHSH={d['chsh']} ({d['chsh_rate']:.3f}), "
              f"QO={d['qo']} ({d['qo_rate']:.3f}) — above baseline by {d['chsh_rate'] - base_chsh_rate:+.3f}")

    # Detect trajectory shape
    rates = [r2[lag]['chsh_rate'] for lag in sorted(r2.keys()) if r2[lag]['total'] >= 20]
    if len(rates) >= 3:
        if all(rates[i] >= rates[i+1] for i in range(len(rates) - 1)):
            r2_shape = "MONOTONIC DECAY (thermal-like)"
        elif rates[0] > base_chsh_rate and rates[-1] <= base_chsh_rate + 0.02:
            r2_shape = "RETURN TO BASELINE"
        elif rates[0] > base_chsh_rate and all(r > base_chsh_rate for r in rates):
            r2_shape = "SUSTAINED ELEVATION (structural lane-lock)"
        elif rates[0] > base_chsh_rate and rates[1] < base_chsh_rate:
            r2_shape = "OSCILLATORY"
        else:
            r2_shape = "OTHER"
        print(f"  Trajectory shape: {r2_shape}")

    # ---- R3: Triplet patterns ----
    print("\n" + "=" * 80)
    print("REFINEMENT 3: Triplet patterns (hazard → CHSH → ? vs hazard → QO → ?)")
    print("=" * 80)
    r3 = test_triplet_patterns(lines)
    t1 = r3['hazard_chsh_then']
    t2 = r3['hazard_qo_then']
    print(f"  After (hazard → CHSH), next EN: CHSH={t1['CHSH']} ({r3['chsh_then_chsh_rate']:.3f}), "
          f"QO={t1['QO']} (n={t1['total']})")
    print(f"  After (hazard → QO), next EN: CHSH={t2['CHSH']} ({r3['qo_then_chsh_rate']:.3f}), "
          f"QO={t2['QO']} (n={t2['total']})")
    triplet_asymmetry = r3['chsh_then_chsh_rate'] - r3['qo_then_chsh_rate']
    print(f"  Asymmetry (chsh_then_chsh - qo_then_chsh): {triplet_asymmetry:+.3f}")

    # ---- R4: Pre-hazard signature ----
    print("\n" + "=" * 80)
    print("REFINEMENT 4: Pre-hazard signature")
    print("=" * 80)
    r4 = test_pre_hazard_signature(lines, max_back=3)
    for lag in sorted(r4.keys()):
        d = r4[lag]
        print(f"  Lag -{lag} EN-position: total={d['total']}, QO={d['qo']} ({d['qo_rate']:.3f}), "
              f"CHSH={d['chsh']} ({d['chsh_rate']:.3f}) — QO above baseline by {d['qo_rate'] - (1 - base_chsh_rate):+.3f}")

    # ---- R5: Folio-level consistency ----
    print("\n" + "=" * 80)
    print("REFINEMENT 5: Folio-level consistency")
    print("=" * 80)
    r5 = test_folio_consistency(lines)
    print(f"  N folios with ≥3 post-hazard EN events: {r5['n_folios_with_data']}")
    print(f"  Mean across-folio CHSH rate: {r5['mean_chsh_rate_across_folios']:.3f}")
    print(f"  Std across folios: {r5['std_chsh_rate_across_folios']:.3f}")
    print(f"  Fraction of folios above baseline CHSH (0.447): {r5['fraction_folios_above_baseline_chsh']:.2%}")

    # ---- Null distribution comparison for primary CHSH-rate (lag +1) ----
    print("\n" + "=" * 80)
    print("NULL DISTRIBUTION FOR LAG +1 CHSH RATE")
    print("=" * 80)
    n_haz_events = r2[1]['total']
    print(f"  Computing null distribution (n_events={n_haz_events}, n_null={N_NULL})...")
    nulls = null_distribution_post_event_chsh_rate(lines, n_haz_events, n_null=N_NULL)
    observed = r2[1]['chsh_rate']
    null_mean = float(nulls.mean())
    null_p95 = float(np.percentile(nulls, 95))
    null_p99 = float(np.percentile(nulls, 99))
    p_emp = float(np.mean(nulls >= observed))
    print(f"  Null mean CHSH rate: {null_mean:.4f}")
    print(f"  Null 95th percentile: {null_p95:.4f}")
    print(f"  Null 99th percentile: {null_p99:.4f}")
    print(f"  Observed (hazard) CHSH rate: {observed:.4f}")
    print(f"  p_empirical: {p_emp:.4f}")
    print(f"  Passes p99: {observed > null_p99}")

    # ---- Per-lag null comparison ----
    print("\n  Per-lag null comparison:")
    per_lag_null = {}
    for lag in sorted(r2.keys()):
        if r2[lag]['total'] >= 20:
            n_evt = r2[lag]['total']
            nulls_lag = null_distribution_post_event_chsh_rate(lines, n_evt, n_null=300, seed=42 + lag)
            observed_lag = r2[lag]['chsh_rate']
            p_emp_lag = float(np.mean(nulls_lag >= observed_lag))
            p99_lag = float(np.percentile(nulls_lag, 99))
            passes = observed_lag > p99_lag
            print(f"    Lag +{lag}: observed={observed_lag:.4f}, null_mean={nulls_lag.mean():.4f}, "
                  f"null_p99={p99_lag:.4f}, p_emp={p_emp_lag:.4f}, passes={passes}")
            per_lag_null[lag] = {
                'observed': observed_lag,
                'null_mean': float(nulls_lag.mean()),
                'null_p99': p99_lag,
                'p_emp': p_emp_lag,
                'passes': passes,
            }

    # ---- Verdict ----
    print("\n" + "=" * 80)
    print("VERDICT EVALUATION")
    print("=" * 80)

    pass_count = 0
    pass_details = []

    # R1: spread between classes > 0.05
    if len(r1) >= 2:
        classes = sorted(r1.keys())
        rates = [r1[c]['chsh_rate'] for c in classes]
        spread = max(rates) - min(rates)
        if spread > 0.05:
            pass_count += 1
            pass_details.append(f"R1: class spread {spread:.3f} > 0.05 (class-specific)")
        else:
            pass_details.append(f"R1: class spread {spread:.3f} ≤ 0.05 (no class-specificity)")

    # R2: trajectory decays from above baseline toward baseline
    if r2[1]['chsh_rate'] > base_chsh_rate + 0.10:
        if 4 in r2 and r2[4]['chsh_rate'] < r2[1]['chsh_rate'] - 0.05:
            pass_count += 1
            pass_details.append(f"R2: trajectory decays from +{r2[1]['chsh_rate'] - base_chsh_rate:.3f} at lag+1 to +{r2[4]['chsh_rate'] - base_chsh_rate:.3f} at lag+4")
        else:
            pass_details.append(f"R2: trajectory does NOT decay sufficiently")
    else:
        pass_details.append(f"R2: lag+1 effect insufficient")

    # R3: triplet asymmetry (chsh_then_chsh > qo_then_chsh) by ≥ 0.10
    if triplet_asymmetry >= 0.10:
        pass_count += 1
        pass_details.append(f"R3: chsh-extended pattern (asymmetry={triplet_asymmetry:+.3f})")
    else:
        pass_details.append(f"R3: weak triplet asymmetry ({triplet_asymmetry:+.3f})")

    # R4: pre-hazard QO elevation at lag -1 by ≥ 0.05 above (1 - base_chsh_rate)
    if 1 in r4 and r4[1]['qo_rate'] > (1 - base_chsh_rate) + 0.05:
        pass_count += 1
        pass_details.append(f"R4: pre-hazard QO elevation +{r4[1]['qo_rate'] - (1 - base_chsh_rate):+.3f}")
    else:
        pass_details.append(f"R4: no pre-hazard QO buildup detected")

    # R5: ≥ 70% of folios above baseline CHSH
    if r5['fraction_folios_above_baseline_chsh'] >= 0.70:
        pass_count += 1
        pass_details.append(f"R5: {r5['fraction_folios_above_baseline_chsh']:.2%} of folios above baseline (consistent)")
    else:
        pass_details.append(f"R5: only {r5['fraction_folios_above_baseline_chsh']:.2%} of folios above baseline (not consistent)")

    print(f"\n  Refinement axis pass count: {pass_count}/5")
    for d in pass_details:
        print(f"    {d}")

    if pass_count >= 4:
        verdict = "STRONG THERMAL RECOVERY ARCHITECTURE"
    elif pass_count >= 2:
        verdict = "MODERATE THERMAL RECOVERY"
    elif pass_count == 1:
        verdict = "C645 ISOLATED (only 1 axis confirms)"
    else:
        verdict = "C645 ANOMALY (no refinement confirms)"

    print(f"\n  VERDICT: {verdict}")

    # ---- Save ----
    out = {
        'method': 'PHASE_714 C645 post-hazard directional anchor refinement',
        'n_lines': len(lines),
        'n_hazard_tokens': n_haz,
        'n_en_tokens': n_en,
        'base_chsh_rate': base_chsh_rate,
        'refinement_1_per_class': {str(k): v for k, v in r1.items()},
        'refinement_2_multi_lag': {str(k): v for k, v in r2.items()},
        'refinement_3_triplet': r3,
        'refinement_4_pre_hazard': {str(k): v for k, v in r4.items()},
        'refinement_5_folio_consistency': {
            'n_folios_with_data': r5['n_folios_with_data'],
            'mean_chsh_rate': r5['mean_chsh_rate_across_folios'],
            'std_chsh_rate': r5['std_chsh_rate_across_folios'],
            'fraction_above_baseline': r5['fraction_folios_above_baseline_chsh'],
            'per_folio_sample': r5['per_folio'][:20],
        },
        'null_lag1': {
            'observed': observed,
            'null_mean': null_mean,
            'null_p95': null_p95,
            'null_p99': null_p99,
            'p_empirical': p_emp,
            'passes_p99': observed > null_p99,
        },
        'null_per_lag': per_lag_null,
        'pass_count': pass_count,
        'pass_details': pass_details,
        'verdict': verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
