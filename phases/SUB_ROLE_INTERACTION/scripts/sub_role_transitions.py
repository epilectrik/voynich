"""
SUB_ROLE_INTERACTION Script 1: Cross-Boundary Sub-Group Transitions

Build sub-group->sub-group transition matrices for all cross-role pairs.
Test whether internal sub-group structure is visible across role boundaries.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/SUB_ROLE_INTERACTION/results'

# ============================================================
# SECTION 1: SUB-GROUP DEFINITIONS
# ============================================================

# ICC role sets
ICC_CC = {10, 11, 12, 17}
ICC_EN = {8} | set(range(31, 50)) - {38, 40}
ICC_FL = {7, 30, 38, 40}
ICC_FQ = {9, 13, 14, 23}

# Sub-group class assignments (from prior anatomy phases)
SUBGROUP_MAP = {}

# EN sub-groups (C573, C576)
EN_QO = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}
EN_MINOR = {41}
for c in EN_QO: SUBGROUP_MAP[c] = ('EN', 'QO')
for c in EN_CHSH: SUBGROUP_MAP[c] = ('EN', 'CHSH')
for c in EN_MINOR: SUBGROUP_MAP[c] = ('EN', 'MINOR')

# FQ sub-groups (C593)
FQ_CONN = {9}
FQ_PAIR = {13, 14}
FQ_CLOSER = {23}
for c in FQ_CONN: SUBGROUP_MAP[c] = ('FQ', 'CONN')
for c in FQ_PAIR: SUBGROUP_MAP[c] = ('FQ', 'PAIR')
for c in FQ_CLOSER: SUBGROUP_MAP[c] = ('FQ', 'CLOSER')

# FL sub-groups (C586)
FL_HAZ = {7, 30}
FL_SAFE = {38, 40}
for c in FL_HAZ: SUBGROUP_MAP[c] = ('FL', 'HAZ')
for c in FL_SAFE: SUBGROUP_MAP[c] = ('FL', 'SAFE')

# AX sub-groups (C563)
AX_INIT = {4, 5, 6, 24, 26}
AX_MED = {1, 2, 3, 16, 18, 27, 28, 29}
AX_FINAL = {15, 19, 20, 21, 22, 25}
for c in AX_INIT: SUBGROUP_MAP[c] = ('AX', 'INIT')
for c in AX_MED: SUBGROUP_MAP[c] = ('AX', 'MED')
for c in AX_FINAL: SUBGROUP_MAP[c] = ('AX', 'FINAL')

# CC sub-groups (C581, C590)
CC_DAIIN = {10}
CC_OL = {11}
CC_OLD = {17}
CC_GHOST = {12}  # 0 tokens
for c in CC_DAIIN: SUBGROUP_MAP[c] = ('CC', 'DAIIN')
for c in CC_OL: SUBGROUP_MAP[c] = ('CC', 'OL')
for c in CC_OLD: SUBGROUP_MAP[c] = ('CC', 'OL_D')
for c in CC_GHOST: SUBGROUP_MAP[c] = ('CC', 'GHOST')

# All sub-group labels (ordered)
ALL_SUBGROUPS = [
    'EN_QO', 'EN_CHSH', 'EN_MINOR',
    'FQ_CONN', 'FQ_PAIR', 'FQ_CLOSER',
    'FL_HAZ', 'FL_SAFE',
    'AX_INIT', 'AX_MED', 'AX_FINAL',
    'CC_DAIIN', 'CC_OL', 'CC_OL_D',
    'UN'
]

ROLE_SUBGROUPS = {
    'EN': ['EN_QO', 'EN_CHSH', 'EN_MINOR'],
    'FQ': ['FQ_CONN', 'FQ_PAIR', 'FQ_CLOSER'],
    'FL': ['FL_HAZ', 'FL_SAFE'],
    'AX': ['AX_INIT', 'AX_MED', 'AX_FINAL'],
    'CC': ['CC_DAIIN', 'CC_OL', 'CC_OL_D'],
}

def get_subgroup_label(cls):
    """Return sub-group label string like 'EN_QO' or 'UN'."""
    if cls is None:
        return 'UN'
    sg = SUBGROUP_MAP.get(cls)
    if sg is None:
        return 'UN'
    return f"{sg[0]}_{sg[1]}"

def get_role(cls):
    if cls is None:
        return 'UN'
    if cls in ICC_CC: return 'CC'
    if cls in ICC_EN: return 'EN'
    if cls in ICC_FL: return 'FL'
    if cls in ICC_FQ: return 'FQ'
    for c in AX_INIT | AX_MED | AX_FINAL:
        if cls == c: return 'AX'
    return 'UN'

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("SUB-ROLE INTERACTION: CROSS-BOUNDARY TRANSITIONS")
print("=" * 70)

tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Build line structures
lines = defaultdict(list)
for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    sg = get_subgroup_label(cls)
    role = sg.split('_')[0] if sg != 'UN' else 'UN'
    lines[(token.folio, token.line)].append({
        'word': word, 'class': cls, 'subgroup': sg, 'role': role,
        'folio': token.folio
    })

results = {}

# ============================================================
# SECTION 2: MASTER TRANSITION MATRIX
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: MASTER TRANSITION MATRIX")
print("=" * 70)

master_matrix = defaultdict(lambda: defaultdict(int))
total_pairs = 0

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        src = line_tokens[i]['subgroup']
        dst = line_tokens[i + 1]['subgroup']
        master_matrix[src][dst] += 1
        total_pairs += 1

print(f"\nTotal adjacent pairs: {total_pairs}")
print(f"Sub-group categories: {len(ALL_SUBGROUPS)}")

# Compute marginals
row_totals = {sg: sum(master_matrix[sg].values()) for sg in ALL_SUBGROUPS}
col_totals = {sg: sum(master_matrix[src][sg] for src in ALL_SUBGROUPS) for sg in ALL_SUBGROUPS}

print(f"\nSub-group token counts (as source):")
for sg in ALL_SUBGROUPS:
    if row_totals[sg] > 0:
        print(f"  {sg:>12}: {row_totals[sg]:>5}")

# Store master matrix
results['master_matrix'] = {
    'total_pairs': total_pairs,
    'matrix': {src: dict(master_matrix[src]) for src in ALL_SUBGROUPS if row_totals[src] > 0},
    'row_totals': {sg: row_totals[sg] for sg in ALL_SUBGROUPS if row_totals[sg] > 0},
    'col_totals': {sg: col_totals[sg] for sg in ALL_SUBGROUPS if col_totals[sg] > 0}
}

# ============================================================
# SECTION 3: CROSS-ROLE PAIR ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: CROSS-ROLE PAIR ANALYSIS")
print("=" * 70)

# Define the 10 interesting cross-role pairs
CROSS_PAIRS = [
    ('AX', 'EN', "AX scaffolding -> EN families"),
    ('EN', 'AX', "EN families -> AX positions"),
    ('AX', 'FQ', "AX scaffolding -> FQ sub-groups"),
    ('FQ', 'AX', "FQ sub-groups -> AX positions"),
    ('EN', 'FQ', "EN families -> FQ sub-groups"),
    ('FQ', 'EN', "FQ sub-groups -> EN families"),
    ('FQ', 'FL', "FQ sub-groups -> FL hazard/safe"),
    ('FL', 'FQ', "FL hazard/safe -> FQ sub-groups"),
    ('CC', 'EN', "CC triggers -> EN families"),
    ('CC', 'FQ', "CC triggers -> FQ sub-groups"),
]

pair_results = {}

for src_role, dst_role, question in CROSS_PAIRS:
    pair_key = f"{src_role}->{dst_role}"
    src_sgs = ROLE_SUBGROUPS[src_role]
    dst_sgs = ROLE_SUBGROUPS[dst_role]

    print(f"\n--- {pair_key}: {question} ---")

    # Build sub-matrix
    obs = np.zeros((len(src_sgs), len(dst_sgs)), dtype=int)
    for i, s in enumerate(src_sgs):
        for j, d in enumerate(dst_sgs):
            obs[i, j] = master_matrix[s][d]

    total = obs.sum()
    print(f"  Total pairs: {total}")

    if total < 10:
        print(f"  INSUFFICIENT DATA (n={total})")
        pair_results[pair_key] = {
            'question': question,
            'total': int(total),
            'verdict': 'INSUFFICIENT_DATA'
        }
        continue

    # Print observed matrix
    print(f"\n  Observed:")
    print(f"  {'':>12}", end='')
    for d in dst_sgs:
        print(f" {d:>10}", end='')
    print(f" {'Total':>8}")
    for i, s in enumerate(src_sgs):
        print(f"  {s:>12}", end='')
        for j in range(len(dst_sgs)):
            print(f" {obs[i, j]:>10}", end='')
        print(f" {obs[i].sum():>8}")

    # Expected under independence
    row_sums = obs.sum(axis=1)
    col_sums = obs.sum(axis=0)
    expected = np.outer(row_sums, col_sums) / total

    # Enrichment
    enrichment = np.zeros_like(obs, dtype=float)
    for i in range(len(src_sgs)):
        for j in range(len(dst_sgs)):
            if expected[i, j] > 0:
                enrichment[i, j] = obs[i, j] / expected[i, j]

    print(f"\n  Enrichment:")
    print(f"  {'':>12}", end='')
    for d in dst_sgs:
        print(f" {d:>10}", end='')
    print()
    for i, s in enumerate(src_sgs):
        print(f"  {s:>12}", end='')
        for j in range(len(dst_sgs)):
            e = enrichment[i, j]
            marker = '+' if e > 1.3 else ('-' if e < 0.7 else ' ')
            print(f" {e:>8.2f}{marker}", end='')
        print()

    # Chi-squared or Fisher's exact
    min_expected = expected.min() if expected.size > 0 else 0
    if obs.shape[0] >= 2 and obs.shape[1] >= 2:
        if min_expected >= 5:
            chi2, p, dof, _ = stats.chi2_contingency(obs)
            test_type = 'chi2'
        else:
            # Use chi2 anyway but flag sparsity
            chi2, p, dof, _ = stats.chi2_contingency(obs)
            test_type = 'chi2_sparse'
    elif obs.shape == (2, 2):
        _, p = stats.fisher_exact(obs)
        chi2 = None
        dof = None
        test_type = 'fisher'
    else:
        chi2 = None
        p = None
        test_type = 'none'

    sig = p < 0.05 if p is not None else False
    bonf_sig = p < (0.05 / 20) if p is not None else False  # Bonferroni for 20 tests

    if chi2 is not None:
        print(f"\n  Chi2={chi2:.2f}, df={dof}, p={p:.2e}, test={test_type}")
    elif p is not None:
        print(f"\n  Fisher p={p:.2e}")
    print(f"  Significant (raw): {sig}")
    print(f"  Significant (Bonferroni): {bonf_sig}")

    # Store
    pair_results[pair_key] = {
        'question': question,
        'total': int(total),
        'src_subgroups': src_sgs,
        'dst_subgroups': dst_sgs,
        'observed': obs.tolist(),
        'expected': expected.tolist(),
        'enrichment': enrichment.tolist(),
        'chi2': float(chi2) if chi2 is not None else None,
        'p': float(p) if p is not None else None,
        'dof': int(dof) if dof is not None else None,
        'test_type': test_type,
        'significant_raw': bool(sig),
        'significant_bonferroni': bool(bonf_sig),
        'min_expected': float(min_expected)
    }

results['cross_role_pairs'] = pair_results

# ============================================================
# SECTION 4: SYMMETRY ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: SYMMETRY ANALYSIS")
print("=" * 70)

symmetry_results = {}
symmetry_pairs = [
    ('AX', 'EN'), ('AX', 'FQ'), ('EN', 'FQ'), ('FQ', 'FL'), ('CC', 'EN')
]

for role_a, role_b in symmetry_pairs:
    fwd_key = f"{role_a}->{role_b}"
    rev_key = f"{role_b}->{role_a}"

    fwd = pair_results.get(fwd_key, {})
    rev = pair_results.get(rev_key, {})

    if fwd.get('verdict') == 'INSUFFICIENT_DATA' or rev.get('verdict') == 'INSUFFICIENT_DATA':
        print(f"\n{role_a}<->{role_b}: Insufficient data in one direction")
        symmetry_results[f"{role_a}<->{role_b}"] = {'verdict': 'INSUFFICIENT_DATA'}
        continue

    fwd_enr = np.array(fwd.get('enrichment', [[]]))
    rev_enr = np.array(rev.get('enrichment', [[]]))

    # Compare: for each (a_sub, b_sub), compare A->B enrichment vs B->A enrichment
    fwd_sgs = fwd.get('src_subgroups', [])
    fwd_dgs = fwd.get('dst_subgroups', [])
    rev_sgs = rev.get('src_subgroups', [])
    rev_dgs = rev.get('dst_subgroups', [])

    asymmetric_pairs = []
    for i, a_sg in enumerate(fwd_sgs):
        for j, b_sg in enumerate(fwd_dgs):
            fwd_e = fwd_enr[i, j] if i < fwd_enr.shape[0] and j < fwd_enr.shape[1] else 0
            # Find reverse: b_sg->a_sg
            if b_sg in rev_sgs and a_sg in rev_dgs:
                ri = rev_sgs.index(b_sg)
                rj = rev_dgs.index(a_sg)
                rev_e = rev_enr[ri, rj] if ri < rev_enr.shape[0] and rj < rev_enr.shape[1] else 0
            else:
                rev_e = 0

            if fwd_e > 0 and rev_e > 0:
                ratio = max(fwd_e, rev_e) / min(fwd_e, rev_e)
                if ratio > 1.5:
                    asymmetric_pairs.append({
                        'pair': f"{a_sg}<->{b_sg}",
                        'fwd': round(fwd_e, 3),
                        'rev': round(rev_e, 3),
                        'ratio': round(ratio, 3)
                    })

    print(f"\n{role_a}<->{role_b}: {len(asymmetric_pairs)} asymmetric pairs (ratio > 1.5)")
    for ap in asymmetric_pairs:
        direction = '->' if ap['fwd'] > ap['rev'] else '<-'
        print(f"  {ap['pair']}: fwd={ap['fwd']:.2f} rev={ap['rev']:.2f} ratio={ap['ratio']:.2f} {direction}")

    symmetry_results[f"{role_a}<->{role_b}"] = {
        'asymmetric_count': len(asymmetric_pairs),
        'asymmetric_pairs': asymmetric_pairs
    }

results['symmetry'] = symmetry_results

# ============================================================
# SECTION 5: UN DECOMPOSITION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: UN DECOMPOSITION")
print("=" * 70)

# UN -> sub-group preferences
un_follows = Counter()
un_precedes = Counter()

for (folio, line_id), line_tokens in lines.items():
    for i in range(len(line_tokens) - 1):
        src = line_tokens[i]['subgroup']
        dst = line_tokens[i + 1]['subgroup']
        if src == 'UN' and dst != 'UN':
            un_follows[dst] += 1
        if dst == 'UN' and src != 'UN':
            un_precedes[src] += 1

# Compute enrichment vs baseline sub-group frequencies
total_classified = sum(row_totals[sg] for sg in ALL_SUBGROUPS if sg != 'UN')
sg_baseline = {sg: row_totals[sg] / total_classified for sg in ALL_SUBGROUPS if sg != 'UN' and row_totals[sg] > 0}

un_total_follows = sum(un_follows.values())
un_total_precedes = sum(un_precedes.values())

print(f"\nUN -> classified tokens: {un_total_follows}")
print(f"Classified -> UN tokens: {un_total_precedes}")

un_follow_enrichment = {}
un_precede_enrichment = {}

print(f"\nUN -> sub-group (what follows UN):")
for sg in ALL_SUBGROUPS:
    if sg == 'UN' or un_follows[sg] == 0:
        continue
    rate = un_follows[sg] / un_total_follows
    base = sg_baseline.get(sg, 0)
    enr = rate / base if base > 0 else 0
    un_follow_enrichment[sg] = round(enr, 3)
    marker = '+' if enr > 1.3 else ('-' if enr < 0.7 else ' ')
    print(f"  {sg:>12}: {un_follows[sg]:>5} ({rate:.3f}) enrich={enr:.2f}{marker}")

print(f"\nSub-group -> UN (what precedes UN):")
for sg in ALL_SUBGROUPS:
    if sg == 'UN' or un_precedes[sg] == 0:
        continue
    rate = un_precedes[sg] / un_total_precedes
    base = sg_baseline.get(sg, 0)
    enr = rate / base if base > 0 else 0
    un_precede_enrichment[sg] = round(enr, 3)
    marker = '+' if enr > 1.3 else ('-' if enr < 0.7 else ' ')
    print(f"  {sg:>12}: {un_precedes[sg]:>5} ({rate:.3f}) enrich={enr:.2f}{marker}")

results['un_decomposition'] = {
    'un_follows': dict(un_follows),
    'un_precedes': dict(un_precedes),
    'un_follow_enrichment': un_follow_enrichment,
    'un_precede_enrichment': un_precede_enrichment
}

# ============================================================
# SECTION 6: SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: SUMMARY")
print("=" * 70)

# Count significant pairs
sig_raw = sum(1 for v in pair_results.values() if v.get('significant_raw'))
sig_bonf = sum(1 for v in pair_results.values() if v.get('significant_bonferroni'))
total_tested = sum(1 for v in pair_results.values() if v.get('p') is not None)

print(f"\nCross-role pairs tested: {total_tested}")
print(f"Significant (raw p<0.05): {sig_raw}/{total_tested}")
print(f"Significant (Bonferroni p<{0.05/20:.4f}): {sig_bonf}/{total_tested}")

# Top enrichments across all pairs
all_enrichments = []
for pair_key, pr in pair_results.items():
    if 'enrichment' not in pr:
        continue
    enr = np.array(pr['enrichment'])
    src_sgs = pr['src_subgroups']
    dst_sgs = pr['dst_subgroups']
    obs = np.array(pr['observed'])
    for i in range(enr.shape[0]):
        for j in range(enr.shape[1]):
            if obs[i, j] >= 5:  # Only report cells with enough data
                all_enrichments.append({
                    'pair': pair_key,
                    'src': src_sgs[i],
                    'dst': dst_sgs[j],
                    'enrichment': enr[i, j],
                    'count': int(obs[i, j])
                })

all_enrichments.sort(key=lambda x: x['enrichment'], reverse=True)

print(f"\nTop 10 enrichments (n>=5):")
for e in all_enrichments[:10]:
    print(f"  {e['src']:>12} -> {e['dst']:<12}: {e['enrichment']:.2f}x (n={e['count']})")

print(f"\nTop 10 depletions (n>=5):")
all_enrichments.sort(key=lambda x: x['enrichment'])
for e in all_enrichments[:10]:
    print(f"  {e['src']:>12} -> {e['dst']:<12}: {e['enrichment']:.2f}x (n={e['count']})")

results['summary'] = {
    'total_tested': total_tested,
    'significant_raw': sig_raw,
    'significant_bonferroni': sig_bonf,
    'top_enrichments': all_enrichments[-10:][::-1] if len(all_enrichments) >= 10 else sorted(all_enrichments, key=lambda x: -x['enrichment']),
    'top_depletions': all_enrichments[:10] if len(all_enrichments) >= 10 else sorted(all_enrichments, key=lambda x: x['enrichment'])
}

# Overall verdict
if sig_bonf >= 5:
    verdict = "STRONG_CROSS_BOUNDARY_STRUCTURE"
elif sig_bonf >= 2:
    verdict = "MODERATE_CROSS_BOUNDARY_STRUCTURE"
elif sig_raw >= 5:
    verdict = "WEAK_CROSS_BOUNDARY_STRUCTURE"
else:
    verdict = "NO_CROSS_BOUNDARY_STRUCTURE"

print(f"\nVerdict: {verdict}")
results['summary']['verdict'] = verdict

# Save results
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sub_role_transitions.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'sub_role_transitions.json'}")
