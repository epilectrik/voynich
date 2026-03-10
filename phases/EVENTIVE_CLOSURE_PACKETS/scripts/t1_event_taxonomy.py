"""
t1_event_taxonomy.py -- Phase 569 T1: Event Taxonomy

Classifies all CLOSE lines into event types on TWO axes:
  Axis A: Packet identity (from morphological/structural features)
  Axis B: Closure demand (structural part only: work_preceded)

Produces thresholds and event map consumed by T2/T3.

Axis B demand qualifiers (demanded, residualized, hard_demanded) require
execution state and will be computed INLINE by T2/T3 during execution.
T1 only determines work_preceded structurally.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from phases.EVENTIVE_CLOSURE_PACKETS.scripts.shared_metrics import (
    classify_packet_identity, classify_closure_demand,
    DEFAULT_GLOBAL_THRESHOLDS, PROCESS_SVS, SV_INDEX, EQUILIBRIUM, Q1, Q2_BASE,
    classify_zone, compute_aggregate_dev
)

# ── Paths ────────────────────────────────────────────────────────────────────
REPO = os.path.join(os.path.dirname(__file__), '..', '..', '..')
PACKETS_PATH = os.path.join(REPO, 'phases', 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                            'results', 't3_line_packets.json')
CTS_PATH = os.path.join(REPO, 'phases', 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                        'results', 't7_closure_cts.json')
OUT_PATH = os.path.join(REPO, 'phases', 'EVENTIVE_CLOSURE_PACKETS',
                        'results', 't1_event_taxonomy.json')

# ── Pilot folios ─────────────────────────────────────────────────────────────
PILOT_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r', 'f40v', 'f43v', 'f34r',
    'f31r', 'f39v', 'f95r1', 'f104r', 'f111r', 'f116r', 'f105r',
    'f108v', 'f66r', 'f85r1', 'f86v5', 'f86v6',
]
PILOT_SET = set(PILOT_FOLIOS)


def load_data():
    """Load line packets and CTS data."""
    with open(PACKETS_PATH, 'r') as f:
        packets_raw = json.load(f)
    with open(CTS_PATH, 'r') as f:
        cts_raw = json.load(f)
    return packets_raw['line_packets'], cts_raw['line_cts']


def get_close_lines(line_packets):
    """Filter to lines with packet_phase == 'CLOSE'."""
    close = {}
    for key, pkt in line_packets.items():
        if pkt['packet_state']['packet_phase'] == 'CLOSE':
            close[key] = pkt
    return close


def compute_section_thresholds(close_lines, cts_data):
    """Compute per-section percentile thresholds (P50, P75, P90) for key metrics.

    Returns dict keyed by section with thresholds.
    """
    # Collect values per section
    section_vals = {}  # section -> {metric: [values]}
    metrics = ['mcb', 'cob', 'q4_opaque_rate', 'close_opacity_bias', 'cts']

    for key, pkt in close_lines.items():
        sec = pkt['section']
        if sec not in section_vals:
            section_vals[sec] = {m: [] for m in metrics}

        ps = pkt['packet_state']
        section_vals[sec]['mcb'].append(ps['m_close_bias'])
        section_vals[sec]['cob'].append(ps['close_opacity_bias'])
        section_vals[sec]['q4_opaque_rate'].append(pkt['profile'][14])
        section_vals[sec]['close_opacity_bias'].append(ps['close_opacity_bias'])

        # CTS
        if key in cts_data:
            section_vals[sec]['cts'].append(cts_data[key]['cts'])
        else:
            section_vals[sec]['cts'].append(0.0)

    # Compute percentiles
    def percentile(vals, p):
        """Compute p-th percentile (0-100) using linear interpolation."""
        if not vals:
            return 0.0
        s = sorted(vals)
        n = len(s)
        k = (p / 100.0) * (n - 1)
        lo = int(k)
        hi = min(lo + 1, n - 1)
        frac = k - lo
        return s[lo] + frac * (s[hi] - s[lo])

    thresholds = {}
    for sec, vals in section_vals.items():
        th = {}
        for m in metrics:
            v = vals[m]
            th[f'{m}_p50'] = round(percentile(v, 50), 6)
            th[f'{m}_p75'] = round(percentile(v, 75), 6)
            th[f'{m}_p90'] = round(percentile(v, 90), 6)

        # CTS compound threshold (P75 of CTS, used for section-norm E_compound)
        th['cts_compound_p75'] = th['cts_p75']

        thresholds[sec] = th

    return thresholds


def determine_work_predecessors(line_packets, close_lines):
    """For each CLOSE line, determine if the preceding line is WORK phase.

    Returns dict: close_key -> (has_work_pred: bool, work_pred_key: str|None)
    """
    # Build per-folio line ordering
    folio_lines = {}  # folio -> [(line_num, key)]
    for key, pkt in line_packets.items():
        folio = pkt['folio']
        line_num = pkt['line']
        if folio not in folio_lines:
            folio_lines[folio] = []
        folio_lines[folio].append((line_num, key))

    # Sort by line number. Some lines have suffixes like '29a', so parse
    # the numeric prefix and use the suffix as a tiebreaker.
    def line_sort_key(item):
        ln = item[0]
        # Split into numeric prefix and alphabetic suffix
        num_part = ''
        alpha_part = ''
        for ch in ln:
            if ch.isdigit():
                num_part += ch
            else:
                alpha_part += ch
        return (int(num_part) if num_part else 0, alpha_part)

    for folio in folio_lines:
        folio_lines[folio].sort(key=line_sort_key)

    # Build predecessor map
    pred_map = {}
    for folio, lines in folio_lines.items():
        for i, (line_num, key) in enumerate(lines):
            if i > 0:
                pred_map[key] = lines[i - 1][1]  # predecessor key
            else:
                pred_map[key] = None

    # Check each CLOSE line
    result = {}
    for key in close_lines:
        pred_key = pred_map.get(key)
        if pred_key is not None and pred_key in line_packets:
            pred_phase = line_packets[pred_key]['packet_state']['packet_phase']
            if pred_phase == 'WORK':
                result[key] = (True, pred_key)
            else:
                result[key] = (False, None)
        else:
            result[key] = (False, None)

    return result


def classify_all_events(close_lines, cts_data, section_thresholds, work_preds):
    """Classify all CLOSE lines into event types.

    Axis A: Full classification via classify_packet_identity.
    Axis B: Only work_preceded (structural). Demand qualifiers deferred to T2/T3.
    """
    event_map = {}
    all_event_types = set()

    for key, pkt in close_lines.items():
        sec = pkt['section']
        ps = pkt['packet_state']
        folio = pkt['folio']

        # Extract features
        mcb = ps['m_close_bias']
        cob = ps['close_opacity_bias']
        q4o = pkt['profile'][14]
        armed = ps['closure_armed']

        # CTS
        cts_entry = cts_data.get(key, {})
        cts = cts_entry.get('cts', 0.0)

        # Section thresholds for this section
        sec_th = section_thresholds.get(sec, {})

        # Handle edge case: if mcb P75 == 0, use P90; if P90 == 0, use >0 (same as global)
        effective_sec_th = dict(sec_th)
        if effective_sec_th.get('mcb_p75', 0.0) == 0.0:
            if effective_sec_th.get('mcb_p90', 0.0) > 0.0:
                effective_sec_th['mcb_p75'] = effective_sec_th['mcb_p90']
            # else: stays 0, classify_packet_identity handles mcb > 0 threshold

        # Axis A: Packet identity
        identity = classify_packet_identity(
            cts=cts, mcb=mcb, cob=cob, q4o=q4o, armed=armed,
            global_thresholds=DEFAULT_GLOBAL_THRESHOLDS,
            section_thresholds=effective_sec_th,
            section=sec
        )

        global_types = sorted(identity['global'])
        section_types = sorted(identity['section_norm'])

        all_event_types.update(global_types)
        all_event_types.update(section_types)

        # Axis B: Work predecessor (structural only)
        has_work_pred, work_pred_key = work_preds[key]

        # Build event map entry
        event_map[key] = {
            'packet_types_global': global_types,
            'packet_types_section': section_types,
            'has_work_predecessor': has_work_pred,
            'work_predecessor_key': work_pred_key,
            'section': sec,
            'cts': round(cts, 5),
            'mcb': round(mcb, 5),
            'cob': round(cob, 5),
            'q4o': round(q4o, 5),
            'armed': armed,
            'is_pilot': folio in PILOT_SET
        }

    return event_map


def compute_event_frequency(event_map, sections_found):
    """Compute frequency statistics for each event type under both regimes."""
    # Define all known event types
    all_types = ['E_any', 'E_armed', 'E_compound', 'E_cts50',
                 'E_decisive', 'E_mcb', 'E_opaque', 'E_opaque_decisive']

    total = len(event_map)

    # Global regime
    global_freq = {}
    for etype in all_types:
        count = 0
        per_sec = {s: 0 for s in sections_found}
        for key, entry in event_map.items():
            if etype in entry['packet_types_global']:
                count += 1
                per_sec[entry['section']] += 1
        if count > 0:
            global_freq[etype] = {
                'total': count,
                'fraction': round(count / total, 4) if total > 0 else 0.0,
                'per_section': per_sec
            }

    # Section-normalized regime
    section_freq = {}
    for etype in all_types:
        count = 0
        per_sec = {s: 0 for s in sections_found}
        for key, entry in event_map.items():
            if etype in entry['packet_types_section']:
                count += 1
                per_sec[entry['section']] += 1
        if count > 0:
            section_freq[etype] = {
                'total': count,
                'fraction': round(count / total, 4) if total > 0 else 0.0,
                'per_section': per_sec
            }

    return {'global': global_freq, 'section_norm': section_freq}


def compute_work_pred_stats(event_map):
    """Compute work predecessor statistics."""
    n_with = sum(1 for e in event_map.values() if e['has_work_predecessor'])
    total = len(event_map)

    per_folio = {}
    for key, entry in event_map.items():
        folio = key.split('|')[0]
        if folio not in per_folio:
            per_folio[folio] = {'n_close': 0, 'n_with_work_pred': 0}
        per_folio[folio]['n_close'] += 1
        if entry['has_work_predecessor']:
            per_folio[folio]['n_with_work_pred'] += 1

    return {
        'n_with_work_pred': n_with,
        'fraction_with_work_pred': round(n_with / total, 4) if total > 0 else 0.0,
        'per_folio': per_folio
    }


def compute_pilot_summary(event_map):
    """Compute per-pilot-folio summary."""
    pilot_data = {}

    for key, entry in event_map.items():
        if not entry['is_pilot']:
            continue
        folio = key.split('|')[0]
        if folio not in pilot_data:
            pilot_data[folio] = {
                'n_close_lines': 0,
                'event_counts_global': {},
                'event_counts_section': {},
                'n_with_work_pred': 0
            }

        pilot_data[folio]['n_close_lines'] += 1

        for etype in entry['packet_types_global']:
            pilot_data[folio]['event_counts_global'][etype] = \
                pilot_data[folio]['event_counts_global'].get(etype, 0) + 1

        for etype in entry['packet_types_section']:
            pilot_data[folio]['event_counts_section'][etype] = \
                pilot_data[folio]['event_counts_section'].get(etype, 0) + 1

        if entry['has_work_predecessor']:
            pilot_data[folio]['n_with_work_pred'] += 1

    # Sort event type dicts for consistency
    for folio in pilot_data:
        pilot_data[folio]['event_counts_global'] = dict(
            sorted(pilot_data[folio]['event_counts_global'].items()))
        pilot_data[folio]['event_counts_section'] = dict(
            sorted(pilot_data[folio]['event_counts_section'].items()))

    return pilot_data


def print_summary(event_map, section_thresholds, event_freq, work_pred_stats,
                  pilot_summary, sections_found):
    """Print summary statistics for verification."""
    total = len(event_map)
    n_pilot = sum(1 for e in event_map.values() if e['is_pilot'])

    print("=" * 72)
    print("T1 EVENT TAXONOMY SUMMARY")
    print("=" * 72)
    print(f"\nTotal CLOSE lines:       {total}")
    print(f"Pilot CLOSE lines:       {n_pilot}")
    print(f"Sections found:          {sorted(sections_found)}")

    # Per-section counts
    sec_counts = {}
    for entry in event_map.values():
        sec_counts[entry['section']] = sec_counts.get(entry['section'], 0) + 1
    print("\nPer-section CLOSE line counts:")
    for sec in sorted(sec_counts):
        print(f"  {sec}: {sec_counts[sec]}")

    # Section thresholds
    print("\n--- Section Thresholds ---")
    for sec in sorted(section_thresholds):
        th = section_thresholds[sec]
        print(f"\n  [{sec}]")
        for k in sorted(th):
            print(f"    {k:30s} = {th[k]:.6f}")

    # Event frequency (global)
    print("\n--- Event Frequency (Global Regime) ---")
    gf = event_freq['global']
    for etype in sorted(gf):
        ef = gf[etype]
        sec_str = ", ".join(f"{s}={ef['per_section'].get(s, 0)}"
                            for s in sorted(sections_found))
        print(f"  {etype:22s}  total={ef['total']:4d}  frac={ef['fraction']:.4f}  [{sec_str}]")

    # Event frequency (section-normalized)
    print("\n--- Event Frequency (Section-Normalized Regime) ---")
    sf = event_freq['section_norm']
    for etype in sorted(sf):
        ef = sf[etype]
        sec_str = ", ".join(f"{s}={ef['per_section'].get(s, 0)}"
                            for s in sorted(sections_found))
        print(f"  {etype:22s}  total={ef['total']:4d}  frac={ef['fraction']:.4f}  [{sec_str}]")

    # Work predecessor stats
    print("\n--- Work Predecessor Stats ---")
    print(f"  CLOSE lines with WORK predecessor: {work_pred_stats['n_with_work_pred']}")
    print(f"  Fraction: {work_pred_stats['fraction_with_work_pred']:.4f}")

    # Pilot summary
    print("\n--- Pilot Folio Summary ---")
    for folio in sorted(pilot_summary):
        ps = pilot_summary[folio]
        print(f"  {folio:8s}  close={ps['n_close_lines']:3d}  "
              f"work_pred={ps['n_with_work_pred']:2d}  "
              f"global_types={sorted(ps['event_counts_global'].keys())}")

    # MCB edge case documentation
    print("\n--- MCB P75 Edge Cases ---")
    for sec in sorted(section_thresholds):
        th = section_thresholds[sec]
        mcb_p75 = th.get('mcb_p75', 0.0)
        mcb_p90 = th.get('mcb_p90', 0.0)
        if mcb_p75 == 0.0:
            if mcb_p90 > 0.0:
                print(f"  [{sec}] mcb_p75=0 -> using P90={mcb_p90:.6f} for section-norm E_mcb")
            else:
                print(f"  [{sec}] mcb_p75=0, P90=0 -> using >0 threshold (same as global)")
        else:
            print(f"  [{sec}] mcb_p75={mcb_p75:.6f} (normal)")

    print()


def main():
    # 1. Load data
    line_packets, cts_data = load_data()
    print(f"Loaded {len(line_packets)} line packets, {len(cts_data)} CTS entries")

    # 2. Filter to CLOSE lines
    close_lines = get_close_lines(line_packets)
    print(f"CLOSE-phase lines: {len(close_lines)}")

    # 3. Compute section thresholds
    section_thresholds = compute_section_thresholds(close_lines, cts_data)

    # Identify sections found
    sections_found = sorted(section_thresholds.keys())

    # 4. Determine work predecessors
    work_preds = determine_work_predecessors(line_packets, close_lines)

    # 5. Classify events (Axis A full, Axis B structural only)
    event_map = classify_all_events(close_lines, cts_data,
                                    section_thresholds, work_preds)

    # 6. Compute statistics
    event_freq = compute_event_frequency(event_map, sections_found)
    work_pred_stats = compute_work_pred_stats(event_map)
    pilot_summary = compute_pilot_summary(event_map)

    # Count pilot CLOSE lines
    n_pilot_close = sum(1 for e in event_map.values() if e['is_pilot'])

    # 7. Build output
    # Clean section thresholds for output (only the relevant P75 values)
    out_section_thresholds = {}
    for sec, th in section_thresholds.items():
        out_section_thresholds[sec] = {
            'mcb_p50': th['mcb_p50'],
            'mcb_p75': th['mcb_p75'],
            'mcb_p90': th['mcb_p90'],
            'cob_p50': th['cob_p50'],
            'cob_p75': th['cob_p75'],
            'cob_p90': th['cob_p90'],
            'q4_opaque_rate_p50': th['q4_opaque_rate_p50'],
            'q4_opaque_rate_p75': th['q4_opaque_rate_p75'],
            'q4_opaque_rate_p90': th['q4_opaque_rate_p90'],
            'close_opacity_bias_p50': th['close_opacity_bias_p50'],
            'close_opacity_bias_p75': th['close_opacity_bias_p75'],
            'close_opacity_bias_p90': th['close_opacity_bias_p90'],
            'cts_p50': th['cts_p50'],
            'cts_p75': th['cts_p75'],
            'cts_p90': th['cts_p90'],
            'cts_compound_p75': th['cts_compound_p75'],
        }

    output = {
        'metadata': {
            'phase': 569,
            'script': 't1_event_taxonomy.py',
            'n_close_lines': len(close_lines),
            'n_pilot_close_lines': n_pilot_close,
            'sections_found': sections_found
        },
        'section_thresholds': out_section_thresholds,
        'global_thresholds': DEFAULT_GLOBAL_THRESHOLDS,
        'event_frequency': event_freq,
        'work_predecessor_stats': work_pred_stats,
        'event_map': event_map,
        'pilot_summary': pilot_summary
    }

    # Write output
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nWrote {OUT_PATH}")

    # Print summary
    print_summary(event_map, out_section_thresholds, event_freq,
                  work_pred_stats, pilot_summary, sections_found)


if __name__ == '__main__':
    main()
