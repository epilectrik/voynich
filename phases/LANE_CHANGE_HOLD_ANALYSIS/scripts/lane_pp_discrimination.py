#!/usr/bin/env python3
"""
LANE_CHANGE_HOLD_ANALYSIS - Script 1: PP MIDDLE Lane Discrimination

Which Currier A PP MIDDLEs predict QO vs CHSH lane preference?

Sections:
1. Load & Reconstruct A Records
2. PP-Level Lane Discrimination (Main Test)
3. Obligatory Slot Analysis
4. Permutation Significance
5. Material Class & Pathway Profile
6. Summary & Save
"""

import json
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Reconstruct A Records
# ============================================================
print("=" * 60)
print("SECTION 1: Load & Reconstruct A Records")
print("=" * 60)

# Load data dependencies
with open(PROJECT_ROOT / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json') as f:
    mid_classes = json.load(f)
pp_set = set(mid_classes['a_shared_middles'])
print(f"PP MIDDLEs loaded: {len(pp_set)}")

with open(PROJECT_ROOT / 'phases/PP_CLASSIFICATION/results/pp_classification.json') as f:
    pp_class_data = json.load(f)
pp_material = {m: d['material_class'] for m, d in pp_class_data['pp_classification'].items()}

with open(PROJECT_ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/pp_role_foundation.json') as f:
    role_data = json.load(f)
pp_role_map = role_data['pp_role_map']
azc_med_set = set(role_data['azc_split']['azc_mediated'])
b_native_set = set(role_data['azc_split']['b_native'])

with open(PROJECT_ROOT / 'phases/A_TO_B_ROLE_PROJECTION/results/population_profiles.json') as f:
    pop_data = json.load(f)
pp_en_details = pop_data.get('en_subfamily_classification', {}).get('pp_en_details', {})

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Reconstruct A records: group by (folio, line)
records = []
record_groups = defaultdict(list)
for token in tx.currier_a():
    key = (token.folio, token.line)
    m = morph.extract(token.word)
    record_groups[key].append({
        'word': token.word,
        'prefix': m.prefix,
        'middle': m.middle,
        'suffix': m.suffix,
        'section': token.section,
    })

# Build record-level features
LANE_PREFIXES = {'qo', 'ch', 'sh'}

for (folio, line), tokens in record_groups.items():
    pp_middles_present = set()
    qo_count = 0
    chsh_count = 0
    section = tokens[0]['section'] if tokens else ''

    for t in tokens:
        mid = t['middle']
        pfx = t['prefix']

        # Identify PP MIDDLEs
        if mid and mid in pp_set:
            pp_middles_present.add(mid)

        # Count lane-bearing prefixes
        if pfx == 'qo':
            qo_count += 1
        elif pfx in ('ch', 'sh'):
            chsh_count += 1

    total_lane = qo_count + chsh_count
    if total_lane == 0:
        continue  # No lane signal — exclude

    qo_prefix_frac = qo_count / total_lane

    records.append({
        'folio': folio,
        'line': line,
        'section': section,
        'n_tokens': len(tokens),
        'n_pp': len(pp_middles_present),
        'pp_middles': pp_middles_present,
        'qo_prefix_frac': qo_prefix_frac,
        'qo_count': qo_count,
        'chsh_count': chsh_count,
    })

qo_fracs = np.array([r['qo_prefix_frac'] for r in records])
print(f"\nTotal A records: {len(record_groups)}")
print(f"Records with lane prefixes: {len(records)}")
print(f"qo_prefix_frac: mean={qo_fracs.mean():.4f}, std={qo_fracs.std():.4f}, "
      f"median={np.median(qo_fracs):.4f}")
print(f"Quartiles: Q1={np.percentile(qo_fracs, 25):.4f}, "
      f"Q3={np.percentile(qo_fracs, 75):.4f}")

# Section stats for report
section_counts = defaultdict(int)
for r in records:
    section_counts[r['section']] += 1
print(f"Records by section: {dict(section_counts)}")

# ============================================================
# SECTION 2: PP-Level Lane Discrimination (Main Test)
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: PP-Level Lane Discrimination")
print("=" * 60)

MIN_RECORDS = 10  # Minimum records containing MIDDLE to test

# Build per-MIDDLE presence vectors
middle_presence = defaultdict(list)  # middle -> list of (record_idx, present_bool)
for i, r in enumerate(records):
    for mid in pp_set:
        middle_presence[mid].append(1 if mid in r['pp_middles'] else 0)

# Test each MIDDLE
disc_results = {}
n_tested = 0
n_skipped = 0

for mid in sorted(pp_set):
    presence = np.array(middle_presence[mid])
    n_present = int(presence.sum())

    if n_present < MIN_RECORDS:
        n_skipped += 1
        continue

    n_tested += 1

    # Point-biserial correlation
    r_val, p_val = stats.pointbiserialr(presence, qo_fracs)

    # Mann-Whitney U: qo_prefix_frac WITH vs WITHOUT
    with_vals = qo_fracs[presence == 1]
    without_vals = qo_fracs[presence == 0]
    u_stat, u_p = stats.mannwhitneyu(with_vals, without_vals, alternative='two-sided')

    # Rank-biserial effect size: r_rb = 1 - 2U/(n1*n2)
    n1, n2 = len(with_vals), len(without_vals)
    r_rb = 1 - (2 * u_stat) / (n1 * n2) if n1 > 0 and n2 > 0 else 0.0

    # Direction
    direction = 'QO' if r_val > 0 else 'CHSH'

    # Metadata
    en_info = pp_en_details.get(mid, {})
    en_subfamily = en_info.get('subfamily', 'none') if en_info else 'none'
    has_en = en_subfamily != 'none'

    role_info = pp_role_map.get(mid, {})
    b_role = role_info.get('dominant_role', 'unmatched') or 'unmatched'

    mat_class = pp_material.get(mid, 'UNKNOWN')
    azc_type = 'AZC-Med' if mid in azc_med_set else ('B-Native' if mid in b_native_set else 'unknown')

    disc_results[mid] = {
        'r': float(r_val),
        'p': float(p_val),
        'u_p': float(u_p),
        'r_rb': float(r_rb),
        'direction': direction,
        'n_records_present': n_present,
        'mean_qo_with': float(with_vals.mean()),
        'mean_qo_without': float(without_vals.mean()),
        'has_en_association': has_en,
        'en_subfamily': en_subfamily,
        'material_class': mat_class,
        'b_role': b_role,
        'azc_type': azc_type,
    }

print(f"PP MIDDLEs tested: {n_tested}")
print(f"PP MIDDLEs skipped (< {MIN_RECORDS} records): {n_skipped}")

# Benjamini-Hochberg FDR
p_vals = [(mid, d['p']) for mid, d in disc_results.items()]
p_vals.sort(key=lambda x: x[1])
n_tests = len(p_vals)

for rank, (mid, p) in enumerate(p_vals, 1):
    fdr = p * n_tests / rank
    disc_results[mid]['fdr'] = min(float(fdr), 1.0)
    disc_results[mid]['rank'] = rank

# Propagate FDR monotonicity (step-up)
sorted_mids = [mid for mid, _ in p_vals]
for i in range(len(sorted_mids) - 2, -1, -1):
    disc_results[sorted_mids[i]]['fdr'] = min(
        disc_results[sorted_mids[i]]['fdr'],
        disc_results[sorted_mids[i + 1]]['fdr']
    )

# Count significant
sig_mids = [m for m, d in disc_results.items() if d['fdr'] < 0.05]
sig_qo = [m for m in sig_mids if disc_results[m]['direction'] == 'QO']
sig_chsh = [m for m in sig_mids if disc_results[m]['direction'] == 'CHSH']

# EN vs non-EN breakdown
sig_en = [m for m in sig_mids if disc_results[m]['has_en_association']]
sig_non_en = [m for m in sig_mids if not disc_results[m]['has_en_association']]

print(f"\nSignificant at FDR < 0.05: {len(sig_mids)}")
print(f"  QO-enriched: {len(sig_qo)}")
print(f"  CHSH-enriched: {len(sig_chsh)}")
print(f"  EN-associated: {len(sig_en)}")
print(f"  Non-EN (novel): {len(sig_non_en)}")

# Top discriminators
top_by_abs_r = sorted(disc_results.items(), key=lambda x: abs(x[1]['r']), reverse=True)[:20]
print(f"\nTop 20 discriminators by |r|:")
print(f"{'MIDDLE':>10} {'r':>8} {'FDR':>8} {'Dir':>6} {'EN':>6} {'MatClass':>10} {'Role':>18} {'N':>5}")
for mid, d in top_by_abs_r:
    sig_mark = '*' if d['fdr'] < 0.05 else ' '
    print(f"{mid:>10} {d['r']:>8.4f} {d['fdr']:>8.4f} {d['direction']:>6} "
          f"{d['en_subfamily']:>6} {d['material_class']:>10} {d['b_role']:>18} {d['n_records_present']:>5}{sig_mark}")

# ============================================================
# SECTION 3: Obligatory Slot Analysis
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Obligatory Slot Analysis")
print("=" * 60)

# Split records into quartiles by qo_prefix_frac
q25, q75 = np.percentile(qo_fracs, 25), np.percentile(qo_fracs, 75)
q1_records = [i for i, r in enumerate(records) if r['qo_prefix_frac'] <= q25]
q4_records = [i for i, r in enumerate(records) if r['qo_prefix_frac'] >= q75]

print(f"Q1 (most CHSH): {len(q1_records)} records (qo_frac <= {q25:.4f})")
print(f"Q4 (most QO): {len(q4_records)} records (qo_frac >= {q75:.4f})")

obligatory_slots = []
strong_differentials = []
weak_differentials = []

for mid in sig_mids:
    # Presence rate in Q1 vs Q4
    q1_present = sum(1 for i in q1_records if mid in records[i]['pp_middles'])
    q4_present = sum(1 for i in q4_records if mid in records[i]['pp_middles'])
    q1_rate = q1_present / len(q1_records) if q1_records else 0
    q4_rate = q4_present / len(q4_records) if q4_records else 0

    slot_info = {
        'middle': mid,
        'q1_rate': float(q1_rate),
        'q4_rate': float(q4_rate),
        'diff': float(q4_rate - q1_rate),
        'direction': disc_results[mid]['direction'],
        'material_class': disc_results[mid]['material_class'],
        'en_subfamily': disc_results[mid]['en_subfamily'],
        'r': disc_results[mid]['r'],
    }

    if (q1_rate > 0.8 and q4_rate < 0.2) or (q4_rate > 0.8 and q1_rate < 0.2):
        obligatory_slots.append(slot_info)
    elif abs(q1_rate - q4_rate) > 0.30:
        strong_differentials.append(slot_info)
    else:
        weak_differentials.append(slot_info)

print(f"\nObligatory slots (>80% / <20%): {len(obligatory_slots)}")
for s in obligatory_slots:
    print(f"  {s['middle']:>10}: Q1={s['q1_rate']:.3f} Q4={s['q4_rate']:.3f} "
          f"dir={s['direction']} mat={s['material_class']} en={s['en_subfamily']}")

print(f"Strong differentials (|diff|>0.30): {len(strong_differentials)}")
for s in strong_differentials:
    print(f"  {s['middle']:>10}: Q1={s['q1_rate']:.3f} Q4={s['q4_rate']:.3f} "
          f"dir={s['direction']} mat={s['material_class']} en={s['en_subfamily']}")

print(f"Weak differentials: {len(weak_differentials)}")

# ============================================================
# SECTION 4: Permutation Significance
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Permutation Significance")
print("=" * 60)

N_PERMS = 10000
observed_n_sig = len(sig_mids)

# Find the minimum |r| among significant results (threshold)
if sig_mids:
    min_sig_r = min(abs(disc_results[m]['r']) for m in sig_mids)
else:
    min_sig_r = float('inf')

print(f"Observed significant: {observed_n_sig}, min |r| threshold: {min_sig_r:.4f}")
print(f"Running {N_PERMS} permutations...")

perm_sig_counts = []
rng = np.random.default_rng(42)

for perm_i in range(N_PERMS):
    # Shuffle qo_prefix_frac across records
    shuffled_fracs = rng.permutation(qo_fracs)

    perm_count = 0
    for mid in disc_results:
        presence = np.array(middle_presence[mid])
        r_val, _ = stats.pointbiserialr(presence, shuffled_fracs)
        if abs(r_val) >= min_sig_r:
            perm_count += 1

    perm_sig_counts.append(perm_count)

    if (perm_i + 1) % 1000 == 0:
        print(f"  Permutation {perm_i + 1}/{N_PERMS}...")

perm_array = np.array(perm_sig_counts)
perm_p = float(np.mean(perm_array >= observed_n_sig))

print(f"\nPermutation results:")
print(f"  Observed significant: {observed_n_sig}")
print(f"  Null mean: {perm_array.mean():.2f} (std: {perm_array.std():.2f})")
print(f"  Null max: {perm_array.max()}")
print(f"  Empirical p-value: {perm_p:.4f}")
print(f"  Z-score: {(observed_n_sig - perm_array.mean()) / (perm_array.std() + 1e-10):.2f}")

# ============================================================
# SECTION 5: Material Class & Pathway Profile
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Material Class & Pathway Profile")
print("=" * 60)

if sig_mids:
    # Material class by direction
    mat_by_dir = {'QO': defaultdict(int), 'CHSH': defaultdict(int)}
    role_by_dir = {'QO': defaultdict(int), 'CHSH': defaultdict(int)}
    azc_by_dir = {'QO': defaultdict(int), 'CHSH': defaultdict(int)}

    for mid in sig_mids:
        d = disc_results[mid]
        mat_by_dir[d['direction']][d['material_class']] += 1
        role_by_dir[d['direction']][d['b_role']] += 1
        azc_by_dir[d['direction']][d['azc_type']] += 1

    print("\nMaterial class by direction:")
    for direction in ['QO', 'CHSH']:
        print(f"  {direction}: {dict(mat_by_dir[direction])}")

    print("\nB role by direction:")
    for direction in ['QO', 'CHSH']:
        print(f"  {direction}: {dict(role_by_dir[direction])}")

    print("\nAZC type by direction:")
    for direction in ['QO', 'CHSH']:
        print(f"  {direction}: {dict(azc_by_dir[direction])}")

    # Chi-squared on material class × direction (if enough data)
    mat_classes = ['ANIMAL', 'HERB', 'MIXED', 'NEUTRAL']
    contingency = []
    for direction in ['QO', 'CHSH']:
        row = [mat_by_dir[direction].get(mc, 0) for mc in mat_classes]
        contingency.append(row)

    contingency = np.array(contingency)
    total = contingency.sum()
    if total >= 10 and contingency.min(axis=None) >= 0:
        try:
            chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
            cramers_v = float(np.sqrt(chi2 / (total * min(contingency.shape) - 1))) if total > 0 else 0
            print(f"\nMaterial × Direction chi2={chi2:.3f}, p={chi_p:.4f}, V={cramers_v:.3f}")
        except ValueError:
            chi2, chi_p, cramers_v = float('nan'), float('nan'), float('nan')
            print("\nMaterial × Direction: insufficient data for chi2")
    else:
        chi2, chi_p, cramers_v = float('nan'), float('nan'), float('nan')
        print("\nMaterial × Direction: insufficient data for chi2")

    # Fuel-specific check: NEUTRAL or HERB in CHSH
    chsh_fuel_candidates = [m for m in sig_chsh
                            if disc_results[m]['material_class'] in ('NEUTRAL', 'HERB')]
    print(f"\nFuel candidates (NEUTRAL/HERB CHSH-enriched): {len(chsh_fuel_candidates)}")
    for m in chsh_fuel_candidates:
        d = disc_results[m]
        print(f"  {m:>10}: r={d['r']:.4f}, mat={d['material_class']}, "
              f"en={d['en_subfamily']}, role={d['b_role']}")
else:
    mat_by_dir = {}
    role_by_dir = {}
    azc_by_dir = {}
    chi2, chi_p, cramers_v = float('nan'), float('nan'), float('nan')
    chsh_fuel_candidates = []
    print("No significant discriminators — skipping profile analysis.")

# ============================================================
# SECTION 6: Summary & Save
# ============================================================
print("\n" + "=" * 60)
print("SECTION 6: Summary & Save")
print("=" * 60)

# Top 10 by direction
top_qo = sorted([(m, d) for m, d in disc_results.items() if d['direction'] == 'QO' and d['fdr'] < 0.05],
                 key=lambda x: x[1]['r'], reverse=True)[:10]
top_chsh = sorted([(m, d) for m, d in disc_results.items() if d['direction'] == 'CHSH' and d['fdr'] < 0.05],
                   key=lambda x: x[1]['r'])[:10]

print(f"\nTop 10 QO-enriched discriminators:")
for mid, d in top_qo:
    print(f"  {mid:>10}: r={d['r']:.4f} fdr={d['fdr']:.4f} mat={d['material_class']} "
          f"en={d['en_subfamily']} role={d['b_role']}")

print(f"\nTop 10 CHSH-enriched discriminators:")
for mid, d in top_chsh:
    print(f"  {mid:>10}: r={d['r']:.4f} fdr={d['fdr']:.4f} mat={d['material_class']} "
          f"en={d['en_subfamily']} role={d['b_role']}")

# Verdict
if observed_n_sig >= 20 and perm_p < 0.01:
    verdict = "DISCRETE_SIGNATURE"
elif observed_n_sig >= 5:
    verdict = "MODERATE_SIGNAL"
else:
    verdict = "DISTRIBUTED_SIGNAL"

print(f"\nVERDICT: {verdict}")
print(f"  Significant discriminators: {observed_n_sig}")
print(f"  Permutation p: {perm_p:.4f}")
print(f"  Non-EN discriminators: {len(sig_non_en)}")

# Save
results = {
    'record_reconstruction': {
        'n_total_records': len(record_groups),
        'n_with_lane_prefixes': len(records),
        'qo_prefix_frac_stats': {
            'mean': float(qo_fracs.mean()),
            'std': float(qo_fracs.std()),
            'median': float(np.median(qo_fracs)),
            'q25': float(np.percentile(qo_fracs, 25)),
            'q75': float(np.percentile(qo_fracs, 75)),
        },
        'section_counts': dict(section_counts),
    },
    'discrimination_test': {
        'n_tested': n_tested,
        'n_skipped': n_skipped,
        'n_significant_fdr05': len(sig_mids),
        'n_qo_enriched': len(sig_qo),
        'n_chsh_enriched': len(sig_chsh),
        'by_en_status': {
            'en_associated': {
                'n_tested': sum(1 for d in disc_results.values() if d['has_en_association']),
                'n_sig': len(sig_en),
            },
            'non_en': {
                'n_tested': sum(1 for d in disc_results.values() if not d['has_en_association']),
                'n_sig': len(sig_non_en),
            },
        },
        'all_results': {m: d for m, d in disc_results.items()},
    },
    'obligatory_slots': {
        'q1_threshold': float(q25),
        'q4_threshold': float(q75),
        'n_q1_records': len(q1_records),
        'n_q4_records': len(q4_records),
        'n_obligatory': len(obligatory_slots),
        'n_strong_differential': len(strong_differentials),
        'n_weak_differential': len(weak_differentials),
        'obligatory': obligatory_slots,
        'strong_differentials': strong_differentials,
    },
    'permutation_test': {
        'n_perms': N_PERMS,
        'observed_significant': observed_n_sig,
        'min_sig_r_threshold': float(min_sig_r) if min_sig_r != float('inf') else None,
        'null_mean': float(perm_array.mean()),
        'null_std': float(perm_array.std()),
        'null_max': int(perm_array.max()),
        'empirical_p': perm_p,
    },
    'material_profile': {
        'qo_enriched': dict(mat_by_dir.get('QO', {})) if mat_by_dir else {},
        'chsh_enriched': dict(mat_by_dir.get('CHSH', {})) if mat_by_dir else {},
        'chi2': float(chi2) if not np.isnan(chi2) else None,
        'p': float(chi_p) if not np.isnan(chi_p) else None,
        'cramers_v': float(cramers_v) if not np.isnan(cramers_v) else None,
        'fuel_candidates': [m for m in chsh_fuel_candidates],
    },
    'top_discriminators': {
        'top_qo': [{'middle': m, **d} for m, d in top_qo],
        'top_chsh': [{'middle': m, **d} for m, d in top_chsh],
    },
    'verdict': verdict,
}

output_path = RESULTS_DIR / 'lane_pp_discrimination.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {output_path}")
print("DONE.")
