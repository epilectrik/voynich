"""
T0: Authenticity Strength Assembly
Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE

Computes per-line authenticity strength for all 2,323 lines using Phase 574-
aligned signal definitions. Classifier is FROZEN from Phase 576 (no reclassification).

4 signals aligned with Phase 574's event-level n_strong_signals:
  s_cts50:  CTS > 0.5                  (= E_cts50, identical)
  s_mcb:    m_terminal_present         (= E_mcb, identical)
  s_opaque: opacity_frac > 0           (= E_opaque, FIXED from Phase 576's >= 0.5)
  s_armed:  q4_opaque > section_median (= E_armed, FIXED: no m_in_q4 OR clause)

Strength bands: STRONG (>=3), MED (1-2), WEAK (0)

Also validates per-line strength bands against Phase 574 M1 event-level
n_strong_signals (surrogate validation — expert Modification 1).
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')


def strength_band(n):
    """Map signal count to band."""
    if n >= 3:
        return 'STRONG'
    elif n >= 1:
        return 'MED'
    return 'WEAK'


def main():
    t_start = time.time()
    print("=" * 70)
    print("T0: Authenticity Strength Assembly")
    print("Phase 577 - AUTHENTICITY_STRENGTH_REGIME_GATE")
    print("=" * 70)

    # ---- Load Phase 576 T0 classification (FROZEN) ----
    print("\n--- Loading Phase 576 T0 classification (frozen) ---")
    p576_t0_path = os.path.join(PROJECT_ROOT,
        'phases/CLOSURE_REGIME_ADMISSION_GATE/results/t0_corpus_classification.json')
    with open(p576_t0_path) as f:
        p576_t0 = json.load(f)
    per_line_class = p576_t0['per_line_classification']
    print(f"  Lines from Phase 576: {len(per_line_class)}")

    # ---- Load line packets (for canonical closure_armed) ----
    print("\n--- Loading line packets ---")
    lp_path = os.path.join(PROJECT_ROOT,
        'phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t3_line_packets.json')
    with open(lp_path) as f:
        line_packets = json.load(f)['line_packets']
    print(f"  Line packets: {len(line_packets)}")

    # ---- Load domain tokens (for per-line opacity computation) ----
    print("\n--- Loading domain tokens ---")
    dd_path = os.path.join(PROJECT_ROOT,
        'phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t1_domain_decomposition.json')
    with open(dd_path) as f:
        dd = json.load(f)
    domain_tokens = dd['corpus_tokens']

    setup_path = os.path.join(PROJECT_ROOT,
        'phases/PRODUCTIVE_DISRUPTION_EXPANSION/results/t1_full_scale_setup.json')
    with open(setup_path) as f:
        setup = json.load(f)
    eligible_folios = set(setup['eligible_folios'])

    # Group domain tokens by line
    line_token_groups = defaultdict(list)
    for tok in domain_tokens:
        if tok['folio'] in eligible_folios:
            key = f"{tok['folio']}|{tok['line']}"
            line_token_groups[key].append(tok)

    # ---- Load Phase 574 T0 M1 events (for surrogate validation) ----
    print("\n--- Loading Phase 574 M1 events ---")
    p574_t0_path = os.path.join(PROJECT_ROOT,
        'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t0_event_feature_assembly.json')
    with open(p574_t0_path) as f:
        p574_t0 = json.load(f)
    m1_events = p574_t0['m1_events']
    print(f"  Phase 574 M1 events: {len(m1_events)}")

    # ---- Compute per-line authenticity strength ----
    print("\n--- Computing per-line authenticity strength ---")

    per_line_strength = {}
    band_counter = Counter()
    class_x_strength = defaultdict(lambda: Counter())
    n_opaque_changed = 0
    n_armed_changed = 0

    for line_key, p576_info in per_line_class.items():
        legit_class = p576_info['class']
        cts = p576_info.get('cts', 0.0)
        features_576 = p576_info.get('features', {})

        # Signal 1: s_cts50 (identical to E_cts50)
        s_cts50 = cts > 0.5

        # Signal 2: s_mcb (identical to E_mcb)
        s_mcb = features_576.get('m_terminal_present', False)

        # Signal 3: s_opaque = ANY opaque terminal (aligned with E_opaque)
        # Phase 576 used high_opaque = opacity_frac >= 0.5 (stricter)
        opacity_frac = p576_info.get('opacity_frac', 0.0)
        s_opaque = opacity_frac > 0  # ANY opaque terminal present

        # Track alignment changes
        old_opaque = features_576.get('high_opaque', False)
        if s_opaque != old_opaque:
            n_opaque_changed += 1

        # Signal 4: s_armed = closure_armed from line packets (strict: no OR m_in_q4)
        pkt = line_packets.get(line_key, {})
        pkt_state = pkt.get('packet_state', {})
        s_armed = pkt_state.get('closure_armed', False)

        # Track armed alignment changes
        old_armed = features_576.get('armed', False)
        if s_armed != old_armed:
            n_armed_changed += 1

        # Compute strength
        signals = {
            's_cts50': s_cts50,
            's_mcb': s_mcb,
            's_opaque': s_opaque,
            's_armed': s_armed,
        }
        n_auth = sum(signals.values())
        band = strength_band(n_auth)

        band_counter[band] += 1
        class_x_strength[legit_class][band] += 1

        per_line_strength[line_key] = {
            'class': legit_class,
            'strength_band': band,
            'n_auth_strength': n_auth,
            'signals': signals,
            'cts': round(cts, 4),
        }

    n_total = len(per_line_strength)
    print(f"  Lines with strength: {n_total}")
    print(f"  Band distribution:")
    for band in ['STRONG', 'MED', 'WEAK']:
        cnt = band_counter.get(band, 0)
        print(f"    {band}: {cnt} ({cnt/n_total*100:.1f}%)")

    print(f"\n  Signal alignment changes from Phase 576:")
    print(f"    Opaque (>=0.5 -> >0): {n_opaque_changed} lines changed")
    print(f"    Armed (proxy -> strict closure_armed): {n_armed_changed} lines changed")

    # ---- Cross-tabulate class × strength ----
    print("\n--- Class × Strength distribution ---")
    class_x_strength_output = {}
    structural_zeros = []

    all_classes = ['AUTH_RESISTANT', 'AUTH_COUNTERFEITABLE', 'AUTH_THRESHOLD',
                   'AUTH_PROTECTIVE', 'AUTH_PRONE', 'AUTH_AMBIGUOUS']

    for cls in all_classes:
        counts = class_x_strength.get(cls, Counter())
        row = {b: counts.get(b, 0) for b in ['WEAK', 'MED', 'STRONG']}
        class_x_strength_output[cls] = row
        total = sum(row.values())
        print(f"  {cls:30s}: WEAK={row['WEAK']:4d}  MED={row['MED']:4d}  STRONG={row['STRONG']:4d}  TOT={total}")

        # Identify structural zeros
        for b in ['WEAK', 'MED', 'STRONG']:
            if row[b] == 0:
                structural_zeros.append(f"{cls}+{b}")

    print(f"\n  Structural zeros: {structural_zeros}")

    # ---- Surrogate validation against Phase 574 M1 event bands ----
    print("\n--- Surrogate validation vs Phase 574 event bands ---")
    # Compare per-line strength_band against Phase 574's grammar_band (from n_strong_signals)

    confusion = defaultdict(lambda: Counter())  # confusion[line_band][event_band] = count
    n_agree = 0
    n_compared = 0
    per_class_agree = defaultdict(lambda: {'match': 0, 'total': 0})

    for ev in m1_events:
        line_key = ev.get('line_key', '')
        if line_key not in per_line_strength:
            continue

        event_band = ev.get('grammar_band', '')
        if not event_band:
            # Derive from n_strong_signals
            ns = ev.get('n_strong_signals', 0)
            event_band = strength_band(ns)

        line_band = per_line_strength[line_key]['strength_band']
        n_compared += 1

        confusion[line_band][event_band] += 1

        if line_band == event_band:
            n_agree += 1

        cls = per_line_strength[line_key]['class']
        per_class_agree[cls]['total'] += 1
        if line_band == event_band:
            per_class_agree[cls]['match'] += 1

    surrogate_agreement_pct = n_agree / n_compared * 100 if n_compared > 0 else 0
    print(f"  Events compared: {n_compared}")
    print(f"  Agreement: {n_agree}/{n_compared} ({surrogate_agreement_pct:.1f}%)")

    # Print confusion matrix
    print(f"\n  Confusion matrix (line-level vs event-level):")
    print(f"  {'':>12s}  {'STRONG':>8s}  {'MED':>8s}  {'WEAK':>8s}")
    for lb in ['STRONG', 'MED', 'WEAK']:
        row = confusion.get(lb, {})
        print(f"  line={lb:>6s}  {row.get('STRONG',0):>8d}  {row.get('MED',0):>8d}  {row.get('WEAK',0):>8d}")

    # Per-class agreement
    print(f"\n  Per-class agreement:")
    per_class_agree_output = {}
    for cls in all_classes:
        info = per_class_agree.get(cls, {'match': 0, 'total': 0})
        pct = info['match'] / info['total'] * 100 if info['total'] > 0 else 0
        print(f"    {cls}: {info['match']}/{info['total']} ({pct:.1f}%)")
        per_class_agree_output[cls] = {
            'match': info['match'],
            'total': info['total'],
            'pct': round(pct, 1),
        }

    # Build confusion matrix output
    confusion_output = {}
    for lb in ['STRONG', 'MED', 'WEAK']:
        confusion_output[lb] = {eb: confusion.get(lb, {}).get(eb, 0) for eb in ['STRONG', 'MED', 'WEAK']}

    # ---- Verification ----
    print("\n--- Verification ---")
    v_coverage = n_total >= 2300
    v_bands = len(band_counter) == 3
    # Structural zeros should include known patterns (aligned signal definitions)
    expected_zeros = {'AUTH_THRESHOLD+WEAK', 'AUTH_THRESHOLD+MED',
                      'AUTH_PROTECTIVE+WEAK', 'AUTH_PRONE+WEAK'}
    actual_zeros_set = set(structural_zeros)
    v_zeros = expected_zeros.issubset(actual_zeros_set)
    v_surrogate = surrogate_agreement_pct >= 75  # informational

    print(f"  Coverage >= 2300: {v_coverage} ({n_total})")
    print(f"  All 3 bands populated: {v_bands} ({list(band_counter.keys())})")
    print(f"  Expected structural zeros present: {v_zeros}")
    print(f"  Surrogate agreement >= 75%: {v_surrogate} ({surrogate_agreement_pct:.1f}%)")

    # ---- Save output ----
    print("\n--- Saving output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output = {
        'metadata': {
            'phase': '577',
            'script': 't0_authenticity_strength_assembly.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_lines': n_total,
            'classifier_frozen_from': 'Phase 576 T0',
        },
        'per_line_strength': per_line_strength,
        'band_distribution': {b: band_counter.get(b, 0) for b in ['STRONG', 'MED', 'WEAK']},
        'class_x_strength_distribution': class_x_strength_output,
        'structural_zeros': structural_zeros,
        'alignment_comparison': {
            'n_opaque_changed': n_opaque_changed,
            'n_armed_changed': n_armed_changed,
            'description': 'Opaque: Phase 576 high_opaque (>=0.5) vs Phase 577 any_opaque (>0). '
                           'Armed: Phase 576 proxy (q4_opaque > median OR m_in_q4) vs Phase 577 '
                           'strict closure_armed (q4_opaque > median, no OR).',
        },
        'event_band_surrogate_validation': {
            'n_compared': n_compared,
            'n_agree': n_agree,
            'agreement_pct': round(surrogate_agreement_pct, 1),
            'confusion_matrix': confusion_output,
            'per_class_agreement': per_class_agree_output,
        },
        'verification': {
            'coverage_2323': v_coverage,
            'all_bands_populated': v_bands,
            'structural_zeros_match': v_zeros,
            'surrogate_agreement_ge_75': v_surrogate,
            'all_passed': v_coverage and v_bands and v_zeros,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't0_authenticity_strength_assembly.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
