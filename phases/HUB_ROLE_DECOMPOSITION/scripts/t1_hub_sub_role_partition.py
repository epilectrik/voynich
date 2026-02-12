"""
T1: HUB Sub-Role Partition
==========================
Phase: HUB_ROLE_DECOMPOSITION

Classifies the 23 HUB_UNIVERSAL (Bin 6) MIDDLEs into functional sub-roles
based on forbidden transition participation and safety buffer duty.

Sub-roles (overlapping):
  HAZARD_SOURCE  - MIDDLE appears as source in a forbidden transition
  HAZARD_TARGET  - MIDDLE appears as target in a forbidden transition
  SAFETY_BUFFER  - MIDDLE appears in a safety buffer token
  PURE_CONNECTOR - MIDDLE in none of the above

Compares behavioral signatures (17 dimensions from affordance table) across
sub-roles. Reports Kruskal-Wallis tests with eta-squared.

Output: t1_hub_sub_role_partition.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

HUB_BIN = 6
SIGNATURE_DIMS = [
    'length', 'k_ratio', 'e_ratio', 'h_ratio', 'is_compound',
    'qo_affinity', 'regime_1_enrichment', 'regime_2_enrichment',
    'regime_3_enrichment', 'regime_4_enrichment', 'regime_entropy',
    'initial_rate', 'final_rate', 'folio_spread',
]


def lane_prediction(middle):
    """C649 rule: initial character determines lane."""
    if not middle:
        return 'NEUTRAL'
    first = middle[0]
    if first in ('k', 't', 'p'):
        return 'QO'
    elif first in ('e', 'o'):
        return 'CHSH'
    return 'NEUTRAL'


def main():
    morph = Morphology()

    # ── Load affordance table ──────────────────────────────
    with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
        aff = json.load(f)

    # Extract HUB MIDDLEs and their signatures
    hub_middles = {}
    middle_to_bin = {}
    for mid, data in aff['middles'].items():
        middle_to_bin[mid] = data['affordance_bin']
        if data['affordance_bin'] == HUB_BIN:
            hub_middles[mid] = data

    print(f"HUB_UNIVERSAL MIDDLEs: {len(hub_middles)}")
    print(f"  {sorted(hub_middles.keys())}")

    # ── Load forbidden inventory ───────────────────────────
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' /
              'phase18a_forbidden_inventory.json') as f:
        inv = json.load(f)

    # Decompose forbidden tokens to MIDDLEs
    source_middles = set()
    target_middles = set()
    forbidden_pairs_set = set()
    for tr in inv['transitions']:
        src_m = morph.extract(tr['source']).middle or ''
        tgt_m = morph.extract(tr['target']).middle or ''
        source_middles.add(src_m)
        target_middles.add(tgt_m)
        forbidden_pairs_set.add((tr['source'], tr['target']))

    # ── Load safety buffer scan ────────────────────────────
    with open(PROJECT / 'phases' / 'BIN_HAZARD_NECESSITY' / 'results' /
              'safety_buffer_scan.json') as f:
        buf_data = json.load(f)

    buffer_middles = set()
    for buf in buf_data['safety_buffers']:
        buffer_middles.add(buf['middle'])

    # ── Classify HUB MIDDLEs into sub-roles ────────────────
    hub_roles = {}
    for mid in hub_middles:
        roles = set()
        if mid in source_middles:
            roles.add('HAZARD_SOURCE')
        if mid in target_middles:
            roles.add('HAZARD_TARGET')
        if mid in buffer_middles:
            roles.add('SAFETY_BUFFER')
        if not roles:
            roles.add('PURE_CONNECTOR')
        hub_roles[mid] = sorted(roles)

    # Build role groups (for statistical comparison, assign primary role)
    # Priority: HAZARD_SOURCE > HAZARD_TARGET > SAFETY_BUFFER > PURE_CONNECTOR
    primary_role = {}
    for mid, roles in hub_roles.items():
        if 'HAZARD_SOURCE' in roles:
            primary_role[mid] = 'HAZARD_SOURCE'
        elif 'HAZARD_TARGET' in roles:
            primary_role[mid] = 'HAZARD_TARGET'
        elif 'SAFETY_BUFFER' in roles:
            primary_role[mid] = 'SAFETY_BUFFER'
        else:
            primary_role[mid] = 'PURE_CONNECTOR'

    role_groups = defaultdict(list)
    for mid, role in primary_role.items():
        role_groups[role].append(mid)

    # ── Print sub-role assignments ─────────────────────────
    print(f"\nSUB-ROLE ASSIGNMENTS:")
    for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER',
                 'PURE_CONNECTOR']:
        members = role_groups.get(role, [])
        print(f"  {role:<16s}: {len(members):2d}  {sorted(members)}")

    # Overlap report
    print(f"\nOVERLAP ANALYSIS:")
    src_and_tgt = source_middles & target_middles & set(hub_middles)
    src_and_buf = source_middles & buffer_middles & set(hub_middles)
    tgt_and_buf = target_middles & buffer_middles & set(hub_middles)
    all_three = source_middles & target_middles & buffer_middles & set(hub_middles)
    print(f"  Source AND Target (HUB): {sorted(src_and_tgt)}")
    print(f"  Source AND Buffer (HUB): {sorted(src_and_buf)}")
    print(f"  Target AND Buffer (HUB): {sorted(tgt_and_buf)}")
    print(f"  All three (HUB):         {sorted(all_three)}")

    # ── Behavioral signature comparison ────────────────────
    # Build signature arrays per primary role
    role_signatures = {}
    for role, members in role_groups.items():
        sigs = []
        for mid in members:
            bs = hub_middles[mid]['behavioral_signature']
            sigs.append([bs.get(dim, 0.0) for dim in SIGNATURE_DIMS])
        role_signatures[role] = np.array(sigs) if sigs else np.empty((0, len(SIGNATURE_DIMS)))

    # Kruskal-Wallis across primary roles per dimension
    print(f"\n{'='*70}")
    print(f"BEHAVIORAL SIGNATURE COMPARISON (primary role)")
    print(f"{'='*70}")
    print(f"{'Dimension':<24s} {'H':>8s} {'p':>10s} {'eta_sq':>8s} "
          f"{'SRC':>8s} {'TGT':>8s} {'BUF':>8s} {'CON':>8s}")
    print(f"{'-'*24} {'-'*8} {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    behavioral_results = {}
    role_order = ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER',
                  'PURE_CONNECTOR']
    for i, dim in enumerate(SIGNATURE_DIMS):
        groups = []
        means = {}
        for role in role_order:
            arr = role_signatures.get(role, np.empty(0))
            if arr.size > 0:
                vals = arr[:, i]
                groups.append(vals)
                means[role] = float(np.mean(vals))
            else:
                means[role] = float('nan')

        # Kruskal-Wallis (need at least 2 groups with data)
        valid_groups = [g for g in groups if len(g) >= 1]
        all_vals = np.concatenate(valid_groups) if valid_groups else np.array([])
        if len(valid_groups) >= 2 and np.ptp(all_vals) > 0:
            H_stat, p_val = stats.kruskal(*valid_groups)
            # Eta-squared approximation: (H - k + 1) / (N - k)
            N = sum(len(g) for g in valid_groups)
            k = len(valid_groups)
            eta_sq = (H_stat - k + 1) / (N - k) if N > k else 0.0
            eta_sq = max(0.0, eta_sq)
        else:
            H_stat, p_val, eta_sq = 0.0, 1.0, 0.0

        behavioral_results[dim] = {
            'KW_H': float(H_stat),
            'p': float(p_val),
            'eta_sq': float(eta_sq),
            'per_role_means': means,
        }

        src_m = means.get('HAZARD_SOURCE', float('nan'))
        tgt_m = means.get('HAZARD_TARGET', float('nan'))
        buf_m = means.get('SAFETY_BUFFER', float('nan'))
        con_m = means.get('PURE_CONNECTOR', float('nan'))
        sig = '*' if p_val < 0.05 else ''
        print(f"  {dim:<22s} {H_stat:>8.2f} {p_val:>10.4f} {eta_sq:>8.3f} "
              f"{src_m:>8.3f} {tgt_m:>8.3f} {buf_m:>8.3f} {con_m:>8.3f} {sig}")

    # ── Lane distribution per sub-role ─────────────────────
    # Pre-compute lane for each HUB MIDDLE
    middle_to_lane = {mid: lane_prediction(mid) for mid in hub_middles}

    print(f"\nLANE DISTRIBUTION BY PRIMARY ROLE:")
    lane_by_role = {}
    for role in role_order:
        members = role_groups.get(role, [])
        lane_counts = defaultdict(int)
        for mid in members:
            lane_counts[middle_to_lane[mid]] += 1
        lane_by_role[role] = dict(lane_counts)
        total = len(members)
        print(f"  {role:<16s}: QO={lane_counts.get('QO', 0)} "
              f"CHSH={lane_counts.get('CHSH', 0)} "
              f"NEUTRAL={lane_counts.get('NEUTRAL', 0)} "
              f"(n={total})")

    # ── Corpus-based lane token counts per sub-role ────────
    # Pre-compute word -> middle lookup (O(1) per token in corpus)
    tx = Transcript()
    unique_words = set()
    for token in tx.currier_b():
        w = token.word.strip()
        if w and '*' not in w:
            unique_words.add(w)

    word_to_middle = {}
    for w in unique_words:
        m = morph.extract(w)
        word_to_middle[w] = m.middle or ''

    # Single corpus pass: count tokens per HUB sub-role
    role_token_counts = defaultdict(int)
    role_lane_token_counts = defaultdict(lambda: defaultdict(int))
    hub_set = set(hub_middles.keys())

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        mid = word_to_middle.get(w, '')
        if mid not in hub_set:
            continue
        role = primary_role.get(mid, 'UNKNOWN')
        role_token_counts[role] += 1
        lane = middle_to_lane.get(mid, 'NEUTRAL')
        role_lane_token_counts[role][lane] += 1

    print(f"\nTOKEN-LEVEL LANE DISTRIBUTION BY PRIMARY ROLE:")
    token_lane_by_role = {}
    for role in role_order:
        counts = dict(role_lane_token_counts[role])
        total = role_token_counts[role]
        token_lane_by_role[role] = {
            'total_tokens': total,
            'QO': counts.get('QO', 0),
            'CHSH': counts.get('CHSH', 0),
            'NEUTRAL': counts.get('NEUTRAL', 0),
        }
        qo_pct = counts.get('QO', 0) / total * 100 if total > 0 else 0
        chsh_pct = counts.get('CHSH', 0) / total * 100 if total > 0 else 0
        neut_pct = counts.get('NEUTRAL', 0) / total * 100 if total > 0 else 0
        print(f"  {role:<16s}: {total:>6d} tokens  "
              f"QO={qo_pct:5.1f}%  CHSH={chsh_pct:5.1f}%  "
              f"NEUTRAL={neut_pct:5.1f}%")

    # ── Verdict ────────────────────────────────────────────
    sig_dims = sum(1 for d in behavioral_results.values()
                   if d['p'] < 0.05 and d['eta_sq'] > 0.10)
    total_dims = len(SIGNATURE_DIMS)

    if sig_dims >= 3:
        verdict = 'DECOMPOSABLE'
        detail = (f'{sig_dims}/{total_dims} dimensions show significant '
                  f'sub-role differentiation (p<0.05, eta_sq>0.10).')
    elif sig_dims >= 1:
        verdict = 'PARTIAL_DECOMPOSITION'
        detail = (f'{sig_dims}/{total_dims} dimensions show differentiation. '
                  f'Sub-roles exist but are weakly separated.')
    else:
        verdict = 'HOMOGENEOUS'
        detail = ('No dimension significantly differentiates sub-roles. '
                  'HUB is behaviorally homogeneous despite functional diversity.')

    print(f"\nVERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ─────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'HUB_ROLE_DECOMPOSITION',
            'test': 'T1_HUB_SUB_ROLE_PARTITION',
        },
        'hub_middles': len(hub_middles),
        'hub_middle_list': sorted(hub_middles.keys()),
        'sub_roles': {
            mid: hub_roles[mid] for mid in sorted(hub_middles.keys())
        },
        'primary_roles': {
            mid: primary_role[mid] for mid in sorted(hub_middles.keys())
        },
        'role_groups': {
            role: sorted(role_groups[role])
            for role in role_order if role in role_groups
        },
        'overlap': {
            'source_and_target': sorted(src_and_tgt),
            'source_and_buffer': sorted(src_and_buf),
            'target_and_buffer': sorted(tgt_and_buf),
            'all_three': sorted(all_three),
        },
        'behavioral_comparison': behavioral_results,
        'lane_distribution_by_role': lane_by_role,
        'token_lane_by_role': token_lane_by_role,
        'verdict': verdict,
        'verdict_detail': detail,
        'significant_dimensions': sig_dims,
    }

    out_path = RESULTS_DIR / 't1_hub_sub_role_partition.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
