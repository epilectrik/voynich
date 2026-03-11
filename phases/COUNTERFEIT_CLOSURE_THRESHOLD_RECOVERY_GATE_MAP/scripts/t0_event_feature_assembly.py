"""
T0: Per-Event Feature Assembly
Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP

Builds the analysis-ready dataset: every M1 CLOSE event enriched with
token-level morphology from the domain decomposition, plus stored
DYE/CCS1/ablation metrics from Phase 572/573.

Enrichments per event:
  - Token-level morphology (terminal, HEAD, opacity, headless, suffix)
  - Closure packet morphology signatures (m_terminal, opaque band, hazard, etc.)
  - Grammar strength band and n_strong_signals
  - CRR, NRI from state vectors
  - Event confidence / reliability weight
  - Folio-level apparatus parameters (F1-F5) and ablation sensitivities
"""

import json
import sys
import os
import math
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')
P573_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES', 'results')

# Reuse grammar strength logic from Phase 573 T2
STRONG_SIGNALS = ['E_cts50', 'E_mcb', 'E_opaque', 'E_armed']

SV_INDEX = {'T': 0, 'RC': 1, 'S': 2, 'C': 3, 'TR': 4, 'X': 5, 'Y': 6}
EQUILIBRIUM = 0.5
CONTAINMENT_SVS = ['C', 'X', 'TR']
PROCESS_SVS = ['T', 'RC', 'S', 'C', 'TR', 'X']


def grammar_strength_band(ptg):
    n = sum(1 for s in STRONG_SIGNALS if s in ptg)
    if n >= 3:
        return 'STRONG', n
    elif n >= 1:
        return 'MEDIUM', n
    else:
        return 'WEAK', n


def compute_crr(close_pre_state, line_end_state):
    entry_disp = sum(abs(close_pre_state[SV_INDEX[sv]] - EQUILIBRIUM)
                     for sv in CONTAINMENT_SVS)
    exit_disp = sum(abs(line_end_state[SV_INDEX[sv]] - EQUILIBRIUM)
                    for sv in CONTAINMENT_SVS)
    if entry_disp < 0.001:
        return 1.0
    return exit_disp / entry_disp


def compute_nri(y_gain_event, close_pre_state):
    process_disp = sum(abs(close_pre_state[SV_INDEX[sv]] - EQUILIBRIUM)
                       for sv in PROCESS_SVS)
    if process_disp < 0.001:
        return 0.0
    return y_gain_event / process_disp


def build_line_morphology_index(domain_tokens):
    """Group domain decomposition tokens by (folio, line) and pre-compute
    per-line morphology features."""
    line_index = {}
    for tok in domain_tokens:
        key = (tok['folio'], str(tok['line']))
        if key not in line_index:
            line_index[key] = []
        line_index[key].append(tok)

    morphology = {}
    for key, tokens in line_index.items():
        n = len(tokens)
        terminal_counts = Counter(t.get('term', 'unknown') for t in tokens)
        head_counts = Counter()
        for t in tokens:
            h = t.get('head')
            if t.get('headless_subtype') is not None:
                head_counts['headless'] += 1
            elif h is not None:
                head_counts[h] += 1
            else:
                head_counts['unknown'] += 1

        opacity_counts = Counter()
        for t in tokens:
            op = t.get('terminal_opacity')
            if op is None:
                opacity_counts['null'] += 1
            else:
                opacity_counts[op] += 1

        headless_count = sum(1 for t in tokens if t.get('headless_subtype') is not None)
        m_terminal_count = terminal_counts.get('m', 0)
        suffix_present_count = sum(1 for t in tokens
                                   if t.get('suffix') is not None and t.get('suffix') != '')

        # Frame hazard distribution
        hazard_counts = Counter(t.get('frame_hazard', 'unknown') for t in tokens)

        # Compound depth
        depths = [t.get('compound_depth', 1) for t in tokens]
        mean_depth = sum(depths) / len(depths) if depths else 1.0

        # Dominant terminal and head
        dom_term = terminal_counts.most_common(1)[0][0] if terminal_counts else 'unknown'
        dom_head = head_counts.most_common(1)[0][0] if head_counts else 'unknown'

        morphology[key] = {
            'n_tokens': n,
            'terminal_counts': dict(terminal_counts),
            'head_counts': dict(head_counts),
            'opacity_counts': dict(opacity_counts),
            'headless_count': headless_count,
            'm_terminal_count': m_terminal_count,
            'suffix_present_count': suffix_present_count,
            'hazard_counts': dict(hazard_counts),
            'mean_compound_depth': mean_depth,
            'dominant_terminal': dom_term,
            'dominant_head': dom_head,
        }

    return morphology


def compute_event_confidence(folio_n_events, dv_magnitude):
    """Event confidence weight: penalizes low-event folios and near-zero dV."""
    count_weight = min(1.0, math.sqrt(folio_n_events / 5.0))
    dv_weight = min(1.0, dv_magnitude / 0.01)
    return count_weight * dv_weight


def main():
    t_start = time.time()
    print("=" * 70)
    print("T0: Per-Event Feature Assembly")
    print("Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")

    print("  Loading domain decomposition...")
    dd_path = os.path.join(PROJECT_ROOT, 'phases',
                           'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL', 'results',
                           't1_domain_decomposition.json')
    with open(dd_path, 'r', encoding='utf-8') as f:
        dd = json.load(f)
    domain_tokens = dd['corpus_tokens']
    print(f"  Domain tokens: {len(domain_tokens)}")

    print("  Loading Phase 572 T1 setup...")
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json'), 'r', encoding='utf-8') as f:
        t1_setup = json.load(f)
    eligible_folios = t1_setup['eligible_folios']
    folio_configs = t1_setup['folio_configs']

    print("  Loading Phase 572 T2 model runs...")
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json'), 'r', encoding='utf-8') as f:
        t2_runs = json.load(f)
    primary_runs = t2_runs['primary_runs']

    print("  Loading Phase 573 T1 ablation effects...")
    with open(os.path.join(P573_RESULTS, 't1_mechanism_ablation.json'), 'r', encoding='utf-8') as f:
        t1_ablation = json.load(f)
    per_folio_ablation = t1_ablation['per_folio']

    print("  Loading CTS data...")
    cts_path = os.path.join(PROJECT_ROOT, 'phases', 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                            'results', 't7_closure_cts.json')
    with open(cts_path, 'r', encoding='utf-8') as f:
        cts_raw = json.load(f)
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            cts_data[key] = val.get('cts', 0.0) if isinstance(val, dict) else float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            cts_data[key] = (val.get('cts', val.get('score', 0.0))
                             if isinstance(val, dict) else float(val))

    # ---- Build morphology index ----
    print("\n--- Building line morphology index ---")
    morph_index = build_line_morphology_index(domain_tokens)
    print(f"  Lines in morphology index: {len(morph_index)}")

    # ---- Count events per folio first (needed for confidence weights) ----
    print("\n--- Counting events per folio ---")
    folio_event_counts = {}
    eligible_set = set(eligible_folios)
    for folio in eligible_folios:
        if folio not in primary_runs:
            folio_event_counts[folio] = 0
            continue
        events = primary_runs[folio].get('M1', {}).get('per_event_detail', [])
        folio_event_counts[folio] = len(events)

    # ---- Assemble per-event features ----
    print("\n--- Assembling per-event features ---")
    m1_events = []
    join_hits = 0
    join_misses = 0
    total_events = 0

    for folio in eligible_folios:
        fc = folio_configs[folio]
        profile = fc['profile']
        section = fc['section']
        f1, f2, f3, f4, f5 = fc['F1'], fc['F2'], fc['F3'], fc['F4_raw'], fc['F5']

        # Folio-level CCS1 and ablation sensitivity
        abl_data = per_folio_ablation.get(folio, {})
        folio_ccs1 = abl_data.get('baseline_m4f_dye', 0.0)
        abl_no_cr = abl_data.get('ablations', {}).get('NO_CLOSE_RECOVERY', {}).get('delta_m4f_dye', 0.0)

        n_events = folio_event_counts.get(folio, 0)

        events = primary_runs.get(folio, {}).get('M1', {}).get('per_event_detail', [])
        for ev in events:
            total_events += 1
            line_key = ev.get('line_key', '')
            parts = line_key.split('|')
            if len(parts) != 2:
                join_misses += 1
                continue

            ev_folio, ev_line = parts[0], parts[1]

            # Compute per-event DYE
            dv = ev.get('dv_magnitude_sum', 0.0)
            yg = ev.get('y_gain_event', 0.0)
            dye = yg / dv if dv > 0.001 else 0.0

            # Grammar strength
            ptg = ev.get('packet_types_global', [])
            band, n_strong = grammar_strength_band(ptg)

            # CRR and NRI
            cps = ev.get('close_pre_state', [0.5] * 7)
            les = ev.get('line_end_state', [0.5] * 7)
            crr = compute_crr(cps, les)
            nri = compute_nri(yg, cps)

            # CTS
            cts = cts_data.get(line_key, 0.0)

            # Demand qualifiers
            dq = ev.get('demand_qualifiers', [])

            # Event confidence
            confidence = compute_event_confidence(n_events, dv)

            # Morphology join
            morph_key = (ev_folio, ev_line)
            morph = morph_index.get(morph_key)

            if morph is not None:
                join_hits += 1
                n_tok = morph['n_tokens']
                tc = morph['terminal_counts']
                hc = morph['head_counts']
                oc = morph['opacity_counts']
                haz = morph['hazard_counts']

                terminal_m_frac = tc.get('m', 0) / n_tok if n_tok > 0 else 0.0
                head_k_frac = hc.get('k', 0) / n_tok if n_tok > 0 else 0.0
                headless_frac = morph['headless_count'] / n_tok if n_tok > 0 else 0.0
                opaque_count = oc.get('OPAQUE', 0)
                opacity_opaque_frac = opaque_count / n_tok if n_tok > 0 else 0.0
                suffix_present_frac = morph['suffix_present_count'] / n_tok if n_tok > 0 else 0.0

                # Packet morphology signatures
                m_terminal_present = morph['m_terminal_count'] > 0
                # Opaque frac band (terciles)
                if opacity_opaque_frac < 0.33:
                    opaque_frac_band = 'LOW'
                elif opacity_opaque_frac < 0.66:
                    opaque_frac_band = 'MED'
                else:
                    opaque_frac_band = 'HIGH'
                # Q4 hazard band
                hazard_high_frac = haz.get('HIGH', 0) / n_tok if n_tok > 0 else 0.0
                q4_hazard_band = 'HIGH' if hazard_high_frac > 0.3 else 'LOW'
                headless_involved = morph['headless_count'] > 0
                has_e_head = hc.get('e', 0) > 0
                has_k_head = hc.get('k', 0) > 0
                has_a_head_closure = morph['dominant_head'] == 'a'

                # Closure packet density: approximate from n_close_tokens / n_tokens
                n_close_tokens = ev.get('n_close_tokens', n_tok)
                closure_packet_density = n_close_tokens / n_tok if n_tok > 0 else 0.0
            else:
                join_misses += 1
                n_tok = 0
                terminal_m_frac = 0.0
                head_k_frac = 0.0
                headless_frac = 0.0
                opacity_opaque_frac = 0.0
                suffix_present_frac = 0.0
                m_terminal_present = False
                opaque_frac_band = 'LOW'
                q4_hazard_band = 'LOW'
                headless_involved = False
                has_e_head = False
                has_k_head = False
                has_a_head_closure = False
                closure_packet_density = 0.0
                morph = {'dominant_terminal': 'unknown', 'dominant_head': 'unknown',
                         'mean_compound_depth': 1.0}

            record = {
                'folio': folio,
                'line_key': line_key,
                'profile': profile,
                'section': section,
                'DYE': round(dye, 6),
                'CCS1_folio': round(folio_ccs1, 6),
                'DYE_adv_event': round(dye - folio_ccs1, 6),
                'CRR': round(crr, 6),
                'NRI': round(nri, 6),
                'CTS': round(cts, 4),
                'n_strong_signals': n_strong,
                'grammar_band': band,
                'dv_magnitude': round(dv, 6),
                'y_gain': round(yg, 6),
                # Token-level morphology
                'n_tokens_on_line': n_tok,
                'terminal_m_frac': round(terminal_m_frac, 4),
                'dominant_terminal': morph['dominant_terminal'],
                'dominant_head': morph['dominant_head'],
                'head_k_frac': round(head_k_frac, 4),
                'headless_frac': round(headless_frac, 4),
                'opacity_opaque_frac': round(opacity_opaque_frac, 4),
                'suffix_present_frac': round(suffix_present_frac, 4),
                'mean_compound_depth': round(morph['mean_compound_depth'], 3),
                # Closure packet morphology signatures
                'm_terminal_present': m_terminal_present,
                'opaque_frac_band': opaque_frac_band,
                'q4_hazard_band': q4_hazard_band,
                'headless_involved': headless_involved,
                'has_e_head_support': has_e_head,
                'has_k_head_support': has_k_head,
                'has_a_head_closure': has_a_head_closure,
                'closure_packet_density': round(closure_packet_density, 4),
                # Event taxonomy flags
                'E_cts50': 'E_cts50' in ptg,
                'E_mcb': 'E_mcb' in ptg,
                'E_opaque': 'E_opaque' in ptg,
                'E_armed': 'E_armed' in ptg,
                'E_compound': 'E_compound' in ptg,
                'demanded': 'demanded' in dq,
                'work_preceded': 'work_preceded' in dq,
                # Apparatus parameters
                'F1': fc['F1'],
                'F2': fc['F2'],
                'F3': fc['F3'],
                'F4_raw': fc['F4_raw'],
                'F5': fc['F5'],
                # Folio-level ablation sensitivity
                'abl_NO_CLOSE_RECOVERY': round(abl_no_cr, 6),
                # Reliability weight
                'event_confidence': round(confidence, 4),
            }
            m1_events.append(record)

    print(f"  Total M1 events: {total_events}")
    print(f"  Morphology join hits: {join_hits}")
    print(f"  Morphology join misses: {join_misses}")
    coverage = join_hits / total_events if total_events > 0 else 0.0
    print(f"  Morphology coverage: {coverage:.1%}")

    # ---- Per-folio summary ----
    print("\n--- Computing per-folio summary ---")
    per_folio_summary = {}
    folio_events = {}
    for ev in m1_events:
        folio_events.setdefault(ev['folio'], []).append(ev)

    for folio in eligible_folios:
        fc = folio_configs[folio]
        evts = folio_events.get(folio, [])
        n = len(evts)

        if n == 0:
            per_folio_summary[folio] = {
                'n_events': 0,
                'event_count_band': '0',
                'profile': fc['profile'],
                'section': fc['section'],
                'mean_CTS': 0.0,
                'mean_DYE': 0.0,
                'mean_event_confidence': 0.0,
                'grammar_band_distribution': {},
                'dominant_terminal': 'none',
                'dominant_head': 'none',
            }
            continue

        if n <= 2:
            band_label = '1-2'
        elif n <= 5:
            band_label = '3-5'
        else:
            band_label = '6+'

        band_dist = Counter(e['grammar_band'] for e in evts)
        term_dist = Counter(e['dominant_terminal'] for e in evts)
        head_dist = Counter(e['dominant_head'] for e in evts)

        per_folio_summary[folio] = {
            'n_events': n,
            'event_count_band': band_label,
            'profile': fc['profile'],
            'section': fc['section'],
            'mean_CTS': round(sum(e['CTS'] for e in evts) / n, 4),
            'mean_DYE': round(sum(e['DYE'] for e in evts) / n, 6),
            'mean_event_confidence': round(sum(e['event_confidence'] for e in evts) / n, 4),
            'grammar_band_distribution': dict(band_dist),
            'dominant_terminal': term_dist.most_common(1)[0][0] if term_dist else 'none',
            'dominant_head': head_dist.most_common(1)[0][0] if head_dist else 'none',
            'strong_frac': round(band_dist.get('STRONG', 0) / n, 4),
            'opacity_frac': round(sum(e['opacity_opaque_frac'] for e in evts) / n, 4),
            'm_terminal_frac': round(sum(1 for e in evts if e['m_terminal_present']) / n, 4),
            'headless_frac': round(sum(e['headless_frac'] for e in evts) / n, 4),
            'k_head_frac': round(sum(e['head_k_frac'] for e in evts) / n, 4),
        }

    # ---- Profile summary verification ----
    print("\n--- Profile summary ---")
    for profile in sorted(set(fc['profile'] for fc in folio_configs.values())):
        prof_events = [e for e in m1_events if e['profile'] == profile]
        n = len(prof_events)
        if n == 0:
            continue
        mean_dye = sum(e['DYE'] for e in prof_events) / n
        mean_ccs1 = sum(e['CCS1_folio'] for e in prof_events) / n
        mean_cts = sum(e['CTS'] for e in prof_events) / n
        band_dist = Counter(e['grammar_band'] for e in prof_events)
        print(f"  {profile}: n={n}, mean_DYE={mean_dye:.4f}, "
              f"mean_CCS1={mean_ccs1:.4f}, mean_CTS={mean_cts:.4f}")
        print(f"    Bands: {dict(band_dist)}")

    # ---- Save output ----
    print("\n--- Saving output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'metadata': {
            'phase': '574',
            'script': 't0_event_feature_assembly.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': time.time() - t_start,
            'n_eligible_folios': len(eligible_folios),
            'n_m1_events': len(m1_events),
            'morphology_coverage': round(coverage, 4),
            'join_hits': join_hits,
            'join_misses': join_misses,
        },
        'm1_events': m1_events,
        'per_folio_summary': per_folio_summary,
    }

    out_path = os.path.join(RESULTS_DIR, 't0_event_feature_assembly.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
