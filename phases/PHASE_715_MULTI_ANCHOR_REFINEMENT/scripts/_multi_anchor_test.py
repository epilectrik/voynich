"""PHASE_715: Multi-anchor directional refinement comparison.

Apply PHASE_714 methodology to 4 directional anchors:
  A0 (baseline): C645 — post-hazard CHSH dominance
  A1: C1212 — TERMINAL→INITIAL cross-token chaining (h→p, r→a)
  A2: C1314 — qo-k → ok-e thermal cycling
  A3: C2041 — ar → al closure asymmetry

Cross-anchor comparison reveals whether substrate is uniformly single-step bigram
or has multi-step structure for some patterns.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

OUT_PATH = ROOT / 'phases' / 'PHASE_715_MULTI_ANCHOR_REFINEMENT' / 'results' / 'multi_anchor_results.json'

HAZ_CLASSES = {7, 30}
N_NULL = 500
N_SHUFFLE = 500
MAX_LAG = 4
MAX_BACK = 3


# ---- Token feature extraction (unified) ----

def extract_features(token, morph_obj, class_map, en_classes_set):
    """Return dict of features for one token."""
    cls = class_map.get(token.word)
    m = morph_obj.extract(token.word)
    middle = m.middle or ''
    prefix = m.prefix or ''
    en_subfamily = None
    if cls is not None and cls in en_classes_set:
        if prefix == 'qo':
            en_subfamily = 'QO'
        elif prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'
    is_haz = cls in HAZ_CLASSES if cls is not None else False
    head_atom = middle[0] if middle and middle[0] in 'aeokt' else None
    term_atom = middle[-1] if middle and middle[-1] in 'ynmhlrkt' else None
    is_qo_k = prefix == 'qo' and head_atom == 'k'
    is_ok_e = prefix == 'ok' and head_atom == 'e'
    middle_is_ar = middle == 'ar' or (middle.startswith('ar') and len(middle) <= 3)
    middle_is_al = middle == 'al' or (middle.startswith('al') and len(middle) <= 3)
    return {
        'word': token.word,
        'class': cls,
        'prefix': prefix,
        'middle': middle,
        'en_subfamily': en_subfamily,
        'is_haz': is_haz,
        'head_atom': head_atom,
        'term_atom': term_atom,
        'is_qo_k': is_qo_k,
        'is_ok_e': is_ok_e,
        'middle_is_ar': middle_is_ar,
        'middle_is_al': middle_is_al,
    }


def load_data():
    """Load Currier B tokens with all features needed for anchor tests."""
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
        feats = extract_features(token, morph, token_to_class, all_en_classes)
        lines[(token.folio, token.line)].append(feats)
    return lines


# ---- Anchor definitions ----

class Anchor:
    """Represents one directional anchor with event/target predicates."""
    def __init__(self, name, event_pred, target_pred, description):
        self.name = name
        self.event_pred = event_pred
        self.target_pred = target_pred
        self.description = description


def middle_starts_with(t, char):
    """Return True if token's MIDDLE first character is `char` (any role)."""
    return bool(t.get('middle')) and t['middle'][0] == char


ANCHORS = [
    Anchor(
        name='A0_hazard_to_CHSH',
        event_pred=lambda t: t['is_haz'],
        target_pred=lambda t: t['en_subfamily'] == 'CHSH',
        description='C645 baseline: hazard-class → CHSH lane',
    ),
    Anchor(
        name='A1a_h_term_to_p_mid0',
        event_pred=lambda t: t['term_atom'] == 'h',
        target_pred=lambda t: middle_starts_with(t, 'p'),
        description='C1212 cross-token: h-TERM → MIDDLE[0]=p (FIXED predicate)',
    ),
    Anchor(
        name='A1b_r_term_to_a_mid0',
        event_pred=lambda t: t['term_atom'] == 'r',
        target_pred=lambda t: middle_starts_with(t, 'a'),
        description='C1212 cross-token: r-TERM → MIDDLE[0]=a',
    ),
    Anchor(
        name='A2_qok_to_oke',
        event_pred=lambda t: t['is_qo_k'],
        target_pred=lambda t: t['is_ok_e'],
        description='C1314 cycling: qo-k → ok-e',
    ),
    Anchor(
        name='A3_ar_to_al',
        event_pred=lambda t: t['middle_is_ar'],
        target_pred=lambda t: t['middle_is_al'],
        description='C2041 closure: ar → al',
    ),
]


# ---- Per-anchor test framework ----

def multi_lag_trajectory(lines, anchor):
    """Measure target-rate at lag +1, +2, +3, +4 after event tokens."""
    counts = {lag: 0 for lag in range(1, MAX_LAG + 1)}
    totals = {lag: 0 for lag in range(1, MAX_LAG + 1)}
    n_events = 0
    for key, toks in lines.items():
        for i, t in enumerate(toks):
            if not anchor.event_pred(t):
                continue
            n_events += 1
            for lag in range(1, MAX_LAG + 1):
                if i + lag >= len(toks):
                    break
                totals[lag] += 1
                if anchor.target_pred(toks[i + lag]):
                    counts[lag] += 1
    results = {}
    for lag in range(1, MAX_LAG + 1):
        if totals[lag] > 0:
            results[lag] = {
                'count': counts[lag],
                'total': totals[lag],
                'rate': counts[lag] / totals[lag],
            }
    return results, n_events


def pre_event_signature(lines, anchor):
    """Measure target-rate at lag -1, -2, -3 BEFORE event tokens."""
    counts = {lag: 0 for lag in range(1, MAX_BACK + 1)}
    totals = {lag: 0 for lag in range(1, MAX_BACK + 1)}
    for key, toks in lines.items():
        for i, t in enumerate(toks):
            if not anchor.event_pred(t):
                continue
            for lag in range(1, MAX_BACK + 1):
                if i - lag < 0:
                    break
                totals[lag] += 1
                if anchor.target_pred(toks[i - lag]):
                    counts[lag] += 1
    results = {}
    for lag in range(1, MAX_BACK + 1):
        if totals[lag] > 0:
            results[lag] = {
                'count': counts[lag],
                'total': totals[lag],
                'rate': counts[lag] / totals[lag],
            }
    return results


def baseline_target_rate(lines, anchor):
    """Overall target-rate across all tokens (not just post-event)."""
    total_target = 0
    total = 0
    for key, toks in lines.items():
        for t in toks:
            total += 1
            if anchor.target_pred(t):
                total_target += 1
    return total_target / max(total, 1)


def null_distribution(lines, anchor, n_size, n_null=N_NULL, lag=1, seed=42):
    """Random subsets: target-rate at lag after random non-event tokens."""
    rng = np.random.default_rng(seed)
    all_positions = []
    for key, toks in lines.items():
        for i, t in enumerate(toks):
            if not anchor.event_pred(t):
                all_positions.append((key, i))
    if len(all_positions) < n_size:
        return np.array([])
    null_rates = []
    for _ in range(n_null):
        sampled = rng.choice(len(all_positions), size=n_size, replace=False)
        count, total = 0, 0
        for idx in sampled:
            key, pos = all_positions[idx]
            toks = lines[key]
            if pos + lag < len(toks):
                total += 1
                if anchor.target_pred(toks[pos + lag]):
                    count += 1
        if total > 0:
            null_rates.append(count / total)
    return np.array(null_rates)


def folio_consistency(lines, anchor, min_events=3):
    """Per-folio post-event target-rate (lag +1)."""
    per_folio = defaultdict(lambda: {'target': 0, 'total': 0})
    for key, toks in lines.items():
        folio = key[0]
        for i, t in enumerate(toks):
            if not anchor.event_pred(t):
                continue
            if i + 1 < len(toks):
                per_folio[folio]['total'] += 1
                if anchor.target_pred(toks[i + 1]):
                    per_folio[folio]['target'] += 1
    rates = []
    for folio, d in per_folio.items():
        if d['total'] >= min_events:
            rates.append(d['target'] / d['total'])
    return rates


def within_folio_shuffle_null(lines, anchor, n_perm=N_SHUFFLE, seed=42):
    """Shuffle event/target labels within each folio; recompute post-event target-rate."""
    rng = np.random.default_rng(seed)
    # Identify which folios have data
    folio_to_lines = defaultdict(list)
    for key in lines:
        folio_to_lines[key[0]].append(key)

    # Cache target labels per folio (preserve order across lines but we'll permute together)
    null_rates = []
    for trial in range(n_perm):
        target_count, total = 0, 0
        for folio, line_keys in folio_to_lines.items():
            # Build per-token (event_flag, target_flag, position) per line
            positions = []  # list of (line_key, token_idx)
            event_flags = []  # bool
            target_flags = []  # bool
            for lk in line_keys:
                for ti, t in enumerate(lines[lk]):
                    positions.append((lk, ti))
                    event_flags.append(anchor.event_pred(t))
                    target_flags.append(anchor.target_pred(t))
            # Permute the event_flags array within folio
            perm_event = list(event_flags)
            rng.shuffle(perm_event)
            # Also permute target_flags? Actually for the null we want to break the
            # event-target ordering relationship. Permute event flags only — keeps
            # target positions fixed.
            # Recount post-event target rate
            for idx, (lk, ti) in enumerate(positions):
                if not perm_event[idx]:
                    continue
                # Find next token in same line
                same_line_positions = [(j, p) for j, p in enumerate(positions)
                                       if p[0] == lk and p[1] == ti + 1]
                if not same_line_positions:
                    continue
                next_idx, _ = same_line_positions[0]
                total += 1
                if target_flags[next_idx]:
                    target_count += 1
        if total > 0:
            null_rates.append(target_count / total)
    return np.array(null_rates)


# ---- Faster within-folio shuffle ----

def within_folio_shuffle_null_fast(lines, anchor, n_perm=N_SHUFFLE, seed=42):
    """Optimized: build per-folio arrays once, do bulk shuffles."""
    rng = np.random.default_rng(seed)
    folio_to_data = {}
    for key in lines:
        folio = key[0]
        if folio not in folio_to_data:
            folio_to_data[folio] = []
    # Build per-folio per-line arrays
    for key, toks in lines.items():
        folio = key[0]
        line_events = np.array([anchor.event_pred(t) for t in toks], dtype=bool)
        line_targets = np.array([anchor.target_pred(t) for t in toks], dtype=bool)
        if len(line_events) >= 2:
            folio_to_data[folio].append((line_events, line_targets))

    null_rates = []
    for trial in range(n_perm):
        target_count, total = 0, 0
        for folio, lines_data in folio_to_data.items():
            # Pool events and targets across folio
            all_events = []
            for events, targets in lines_data:
                all_events.append(events)
            if not all_events:
                continue
            # Concatenate
            concat_events = np.concatenate(all_events)
            # Shuffle the event positions across the folio
            perm = rng.permutation(len(concat_events))
            # Map back per-line
            offset = 0
            for events, targets in lines_data:
                n_line = len(events)
                shuffled_events = concat_events[perm[offset:offset + n_line]]
                offset += n_line
                # Recompute post-event target rate within this line
                for i in range(n_line - 1):
                    if shuffled_events[i]:
                        total += 1
                        if targets[i + 1]:
                            target_count += 1
        if total > 0:
            null_rates.append(target_count / total)
    return np.array(null_rates)


# ---- Per-anchor runner ----

def run_anchor(lines, anchor):
    """Run all 4 tests for one anchor. Return dict of results."""
    print(f"\n{'='*70}\n  ANCHOR: {anchor.name} ({anchor.description})\n{'='*70}")

    base_rate = baseline_target_rate(lines, anchor)
    print(f"  Baseline target-rate (across all tokens): {base_rate:.4f}")

    # Multi-lag trajectory
    multi_lag, n_events = multi_lag_trajectory(lines, anchor)
    print(f"  N events: {n_events}")
    if not multi_lag:
        print("  [insufficient data]")
        return {'anchor': anchor.name, 'description': anchor.description, 'error': 'insufficient'}

    print(f"  Multi-lag trajectory (target-rate):")
    for lag, d in multi_lag.items():
        diff = d['rate'] - base_rate
        print(f"    Lag +{lag}: {d['rate']:.4f} (n={d['total']}) — above baseline by {diff:+.4f}")

    # Pre-event signature
    pre = pre_event_signature(lines, anchor)
    print(f"  Pre-event signature:")
    for lag, d in pre.items():
        diff = d['rate'] - base_rate
        print(f"    Lag -{lag}: {d['rate']:.4f} (n={d['total']}) — above baseline by {diff:+.4f}")

    # Per-lag null distribution
    print(f"  Per-lag null distribution (random non-event tokens of matched count):")
    per_lag_null = {}
    for lag in [1, 2, 3, 4]:
        if lag in multi_lag:
            n_size = multi_lag[lag]['total']
            nulls = null_distribution(lines, anchor, n_size, n_null=N_NULL, lag=lag, seed=42 + lag)
            if len(nulls) > 0:
                p99 = float(np.percentile(nulls, 99))
                p_emp = float(np.mean(nulls >= multi_lag[lag]['rate']))
                passes = multi_lag[lag]['rate'] > p99
                print(f"    Lag +{lag}: observed={multi_lag[lag]['rate']:.4f}, "
                      f"null_mean={nulls.mean():.4f}, p99={p99:.4f}, p_emp={p_emp:.4f}, "
                      f"passes={passes}")
                per_lag_null[lag] = {
                    'observed': multi_lag[lag]['rate'],
                    'null_mean': float(nulls.mean()),
                    'null_p99': p99,
                    'p_emp': p_emp,
                    'passes': passes,
                }

    # Folio consistency
    folio_rates = folio_consistency(lines, anchor)
    if folio_rates:
        mean_folio = float(np.mean(folio_rates))
        frac_above = sum(1 for r in folio_rates if r > base_rate) / len(folio_rates)
        print(f"  Folio consistency: {len(folio_rates)} folios with ≥3 events")
        print(f"    Mean folio rate: {mean_folio:.4f}")
        print(f"    Fraction above baseline: {frac_above:.2%}")
    else:
        mean_folio = frac_above = 0
        print(f"  Folio consistency: no folios with ≥3 events")

    # Within-folio shuffle null
    print(f"  Within-folio shuffle null ({N_SHUFFLE} perms)...")
    shuffle_nulls = within_folio_shuffle_null_fast(lines, anchor, n_perm=N_SHUFFLE, seed=42)
    if len(shuffle_nulls) > 0:
        observed_lag1 = multi_lag[1]['rate']
        shuf_mean = float(shuffle_nulls.mean())
        shuf_p99 = float(np.percentile(shuffle_nulls, 99))
        shuf_p_emp = float(np.mean(shuffle_nulls >= observed_lag1))
        shuf_passes = observed_lag1 > shuf_p99
        print(f"    Observed lag+1: {observed_lag1:.4f}")
        print(f"    Within-folio shuffle null mean: {shuf_mean:.4f}, p99: {shuf_p99:.4f}")
        print(f"    p_empirical: {shuf_p_emp:.4f}, passes p99: {shuf_passes}")
    else:
        shuf_mean = shuf_p99 = shuf_p_emp = 0
        shuf_passes = False

    # ---- Pattern classification (pre-registered) ----
    lag1_pass = per_lag_null.get(1, {}).get('passes', False)
    lag2_pass = per_lag_null.get(2, {}).get('passes', False)
    lag3_pass = per_lag_null.get(3, {}).get('passes', False)

    if lag1_pass and shuf_passes:
        if lag2_pass or lag3_pass:
            pattern = "MULTI-STEP SUBSTRATE-LEVEL"
        else:
            pattern = "SINGLE-STEP SUBSTRATE-LEVEL"
    elif lag1_pass and not shuf_passes:
        pattern = "FOLIO-LOCAL"
    else:
        pattern = "NO REAL EFFECT"

    print(f"\n  PATTERN: {pattern}")

    return {
        'anchor': anchor.name,
        'description': anchor.description,
        'baseline_target_rate': base_rate,
        'n_events': n_events,
        'multi_lag': {str(k): v for k, v in multi_lag.items()},
        'pre_event': {str(k): v for k, v in pre.items()},
        'per_lag_null': per_lag_null,
        'folio_consistency': {
            'n_folios': len(folio_rates),
            'mean_rate': mean_folio,
            'frac_above_baseline': frac_above,
        },
        'within_folio_shuffle_null': {
            'observed_lag1': multi_lag[1]['rate'],
            'mean': shuf_mean,
            'p99': shuf_p99,
            'p_empirical': shuf_p_emp,
            'passes_p99': shuf_passes,
        },
        'pattern': pattern,
        'lag1_pass': lag1_pass,
        'lag2_pass': lag2_pass,
        'lag3_pass': lag3_pass,
    }


def main():
    print("=" * 70)
    print("PHASE_715 MULTI-ANCHOR DIRECTIONAL REFINEMENT")
    print("=" * 70)

    print("\nLoading data...")
    lines = load_data()
    print(f"  N Currier B lines: {len(lines)}")

    # Run each anchor
    results = {}
    for anchor in ANCHORS:
        r = run_anchor(lines, anchor)
        results[anchor.name] = r

    # Cross-anchor summary
    print("\n" + "=" * 70)
    print("CROSS-ANCHOR SUMMARY")
    print("=" * 70)
    print(f"\n{'Anchor':<32}{'N_events':>10}{'lag1_obs':>10}{'lag1_p99':>10}{'lag2_pass':>10}{'shuf_p99':>10}{'Pattern':>30}")
    print("-" * 112)
    for name, r in results.items():
        if 'error' in r:
            print(f"{name:<32}  ERROR")
            continue
        ml1 = float(r['multi_lag'].get('1', {}).get('rate', 0)) if '1' in r['multi_lag'] else 0
        p99_lag1 = r['per_lag_null'].get(1, {}).get('null_p99', 0)
        lag2_pass_str = 'Y' if r.get('lag2_pass') else 'N'
        shuf_p99 = r['within_folio_shuffle_null'].get('p99', 0)
        pattern = r.get('pattern', '?')[:28]
        print(f"{name:<32}{r['n_events']:>10}{ml1:>10.4f}{p99_lag1:>10.4f}{lag2_pass_str:>10}{shuf_p99:>10.4f}{pattern:>30}")

    # ---- Cross-anchor verdict ----
    print("\n" + "=" * 70)
    print("CROSS-ANCHOR VERDICT")
    print("=" * 70)

    patterns = [r.get('pattern', '?') for r in results.values() if 'error' not in r]
    n_single = sum(1 for p in patterns if p == "SINGLE-STEP SUBSTRATE-LEVEL")
    n_multi = sum(1 for p in patterns if p == "MULTI-STEP SUBSTRATE-LEVEL")
    n_folio = sum(1 for p in patterns if p == "FOLIO-LOCAL")
    n_none = sum(1 for p in patterns if p == "NO REAL EFFECT")
    n_total = len(patterns)

    print(f"\n  Total anchors tested: {n_total}")
    print(f"    SINGLE-STEP SUBSTRATE-LEVEL: {n_single}")
    print(f"    MULTI-STEP SUBSTRATE-LEVEL:  {n_multi}")
    print(f"    FOLIO-LOCAL:                 {n_folio}")
    print(f"    NO REAL EFFECT:              {n_none}")

    if n_multi > 0 and n_single >= 1:
        verdict = "SUBSTRATE HAS HETEROGENEOUS DEPTH (some anchors single-step, some multi-step)"
    elif n_multi == n_total:
        verdict = "MULTI-STEP SUBSTRATE THROUGHOUT (PHASE_714 finding was atypical)"
    elif n_single == n_total:
        verdict = "SINGLE-STEP BIGRAM-RULE SUBSTRATE CONFIRMED (PHASE_714 generalizes)"
    elif n_folio > 0:
        verdict = "MIXED — some anchors folio-local; substrate-level vs local distinction matters"
    elif n_none > 0:
        verdict = "SOME ANCHORS NO REAL EFFECT (revisit anchor selection)"
    else:
        verdict = "MIXED — see per-anchor patterns"

    print(f"\n  CROSS-ANCHOR VERDICT: {verdict}")

    # Save
    out = {
        'method': 'PHASE_715 multi-anchor directional refinement',
        'n_anchors': len(results),
        'n_perms': N_SHUFFLE,
        'n_null': N_NULL,
        'results_by_anchor': results,
        'cross_anchor_pattern_counts': {
            'SINGLE-STEP SUBSTRATE-LEVEL': n_single,
            'MULTI-STEP SUBSTRATE-LEVEL': n_multi,
            'FOLIO-LOCAL': n_folio,
            'NO REAL EFFECT': n_none,
        },
        'cross_anchor_verdict': verdict,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nWritten: {OUT_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
