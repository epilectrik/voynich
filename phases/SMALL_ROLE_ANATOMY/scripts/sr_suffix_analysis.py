"""
Script 3: Suffix Analysis (ALL 5 roles)

New dimension not covered in any prior anatomy phase.
Analyzes suffix usage patterns across all roles: CC, EN, FL, FQ, AX.
Tests suffix selectivity, section/REGIME interactions, cross-role overlap.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript, Morphology

# Paths
BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/SMALL_ROLE_ANATOMY/results'

# Load data
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
ALL_CLASSES = set(token_to_class.values())

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Role definitions (ICC-based)
EN_FINAL = ({8} | set(range(31, 50)) - {7, 30, 38, 40}) & ALL_CLASSES
FL_FINAL = {7, 30, 38, 40}
CC_FINAL = {10, 11, 12}
FQ_FINAL = {9, 13, 14, 23}
AX_FINAL = ALL_CLASSES - EN_FINAL - FL_FINAL - CC_FINAL - FQ_FINAL

def get_role(cls):
    if cls in CC_FINAL: return 'CC'
    if cls in FL_FINAL: return 'FL'
    if cls in FQ_FINAL: return 'FQ'
    if cls in EN_FINAL: return 'EN'
    if cls in AX_FINAL: return 'AX'
    return 'UN'

def get_section(folio):
    try:
        num = int(''.join(c for c in folio if c.isdigit())[:3])
    except Exception:
        return 'UNKNOWN'
    if num <= 56:
        return 'HERBAL'
    elif num <= 67:
        return 'PHARMA'
    elif num <= 84:
        return 'BIO'
    else:
        return 'RECIPE'

# ============================================================
print("=" * 70)
print("SUFFIX ANALYSIS (ALL 5 ROLES)")
print("=" * 70)

# ============================================================
# 1. BUILD SUFFIX DATA
# ============================================================
print("\nBuilding suffix data from corpus...")

# Per-token suffix extraction
role_suffix_counts = defaultdict(Counter)   # role -> suffix -> count
role_nosuffix = defaultdict(int)            # role -> count of suffix-less tokens
role_total = defaultdict(int)               # role -> total tokens

# Section x role x suffix
section_role_suffix = defaultdict(lambda: defaultdict(Counter))

# REGIME x role x suffix
regime_role_suffix = defaultdict(lambda: defaultdict(Counter))

# Per-class suffix
class_suffix_counts = defaultdict(Counter)
class_total = defaultdict(int)

for token in tokens:
    word = token.word.replace('*', '').strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    if cls is None:
        continue
    role = get_role(cls)
    if role == 'UN':
        continue

    m = morph.extract(word)
    suffix = m.suffix if m.suffix else 'NONE'

    role_suffix_counts[role][suffix] += 1
    role_total[role] += 1
    if suffix == 'NONE':
        role_nosuffix[role] += 1

    class_suffix_counts[cls][suffix] += 1
    class_total[cls] += 1

    section = get_section(token.folio)
    section_role_suffix[section][role][suffix] += 1

    regime = folio_regime.get(token.folio, 'UNKNOWN')
    regime_role_suffix[regime][role][suffix] += 1

# ============================================================
# 2. SUFFIX INVENTORY PER ROLE
# ============================================================
print("\n" + "-" * 70)
print("1. SUFFIX INVENTORY PER ROLE")
print("-" * 70)

ROLES = ['CC', 'EN', 'FL', 'FQ', 'AX']
role_suffix_sets = {}

for role in ROLES:
    counts = role_suffix_counts[role]
    total = role_total[role]
    suffixes = {s for s in counts if s != 'NONE'}
    role_suffix_sets[role] = suffixes
    nosuffix_pct = role_nosuffix[role] / total * 100 if total > 0 else 0

    print(f"\n{role} ({total} tokens, {len(suffixes)} suffix types, {nosuffix_pct:.1f}% suffix-less):")
    # Top suffixes
    sorted_suffixes = sorted([(s, c) for s, c in counts.items() if s != 'NONE'],
                              key=lambda x: -x[1])
    for sfx, cnt in sorted_suffixes[:10]:
        pct = cnt / total * 100
        print(f"  {sfx:>8}: {cnt:>5} ({pct:>5.1f}%)")

# ============================================================
# 3. SUFFIX SELECTIVITY (chi-square independence)
# ============================================================
print("\n" + "-" * 70)
print("2. SUFFIX SELECTIVITY TEST (role x suffix chi-square)")
print("-" * 70)

# Build contingency table: rows = roles, cols = suffix types
all_suffixes = sorted(set().union(*(role_suffix_sets[r] for r in ROLES)))
# Include NONE as a category
all_suffix_cats = ['NONE'] + all_suffixes

contingency = []
for role in ROLES:
    row = [role_suffix_counts[role].get(s, 0) for s in all_suffix_cats]
    contingency.append(row)

contingency = np.array(contingency)
# Remove columns with all zeros
nonzero_cols = contingency.sum(axis=0) > 0
contingency_filtered = contingency[:, nonzero_cols]
suffix_labels_filtered = [s for s, nz in zip(all_suffix_cats, nonzero_cols) if nz]

chi2, p_value, dof, expected = stats.chi2_contingency(contingency_filtered)

print(f"\nContingency table: {len(ROLES)} roles x {len(suffix_labels_filtered)} suffix categories")
print(f"Chi-square = {chi2:.1f}, dof = {dof}, p = {p_value:.2e}")
print(f"Suffix usage is {'ROLE-DEPENDENT' if p_value < 0.001 else 'role-independent'}")

# Compute standardized residuals for top deviations
expected_full = stats.contingency.expected_freq(contingency_filtered)
residuals = (contingency_filtered - expected_full) / np.sqrt(expected_full + 1e-10)

print(f"\nTop enrichments (standardized residual > 3):")
enrichments = []
for i, role in enumerate(ROLES):
    for j, sfx in enumerate(suffix_labels_filtered):
        if residuals[i, j] > 3:
            enrichments.append((role, sfx, residuals[i, j], contingency_filtered[i, j]))
enrichments.sort(key=lambda x: -x[2])
for role, sfx, resid, obs in enrichments[:15]:
    print(f"  {role} x {sfx}: residual={resid:.1f}, observed={int(obs)}")

print(f"\nTop depletions (standardized residual < -3):")
depletions = []
for i, role in enumerate(ROLES):
    for j, sfx in enumerate(suffix_labels_filtered):
        if residuals[i, j] < -3:
            depletions.append((role, sfx, residuals[i, j], contingency_filtered[i, j]))
depletions.sort(key=lambda x: x[2])
for role, sfx, resid, obs in depletions[:15]:
    print(f"  {role} x {sfx}: residual={resid:.1f}, observed={int(obs)}")

# ============================================================
# 4. SUFFIX-LESS RATE COMPARISON
# ============================================================
print("\n" + "-" * 70)
print("3. SUFFIX-LESS RATE BY ROLE")
print("-" * 70)

nosuffix_rates = {}
for role in ROLES:
    total = role_total[role]
    nosuffix = role_nosuffix[role]
    rate = nosuffix / total * 100 if total > 0 else 0
    nosuffix_rates[role] = rate
    print(f"  {role}: {nosuffix}/{total} = {rate:.1f}% suffix-less")

# Chi-square for suffix-less vs suffix-bearing by role
nosuffix_table = np.array([[role_nosuffix[r], role_total[r] - role_nosuffix[r]] for r in ROLES])
chi2_ns, p_ns, dof_ns, _ = stats.chi2_contingency(nosuffix_table)
print(f"\nChi-square (suffix-less rate by role): {chi2_ns:.1f}, p={p_ns:.2e}")

# ============================================================
# 5. SUFFIX x SECTION INTERACTION
# ============================================================
print("\n" + "-" * 70)
print("4. SUFFIX x SECTION INTERACTION (per role)")
print("-" * 70)

SECTIONS = ['HERBAL', 'PHARMA', 'BIO', 'RECIPE']
section_suffix_results = {}

for role in ROLES:
    # Build section x suffix contingency for this role
    section_rows = []
    for sec in SECTIONS:
        row = [section_role_suffix[sec][role].get(s, 0) for s in all_suffix_cats]
        section_rows.append(row)
    section_matrix = np.array(section_rows)
    # Remove zero columns
    nz = section_matrix.sum(axis=0) > 0
    sm_filtered = section_matrix[:, nz]

    if sm_filtered.shape[1] < 2 or sm_filtered.sum() < 10:
        print(f"\n{role}: Insufficient data for section x suffix test")
        section_suffix_results[role] = {'chi2': None, 'p_value': None, 'note': 'insufficient data'}
        continue

    try:
        chi2_s, p_s, dof_s, _ = stats.chi2_contingency(sm_filtered)
        sig = 'SIGNIFICANT' if p_s < 0.01 else 'not significant'
        print(f"\n{role}: chi2={chi2_s:.1f}, dof={dof_s}, p={p_s:.2e} [{sig}]")
        section_suffix_results[role] = {'chi2': round(chi2_s, 2), 'p_value': float(p_s)}

        # Show top suffix by section if significant
        if p_s < 0.01:
            for si, sec in enumerate(SECTIONS):
                sec_counts = section_role_suffix[sec][role]
                if sum(sec_counts.values()) == 0:
                    continue
                top = max(sec_counts, key=sec_counts.get)
                top_count = sec_counts[top]
                total_sec = sum(sec_counts.values())
                print(f"    {sec}: top suffix = '{top}' ({top_count}/{total_sec} = {top_count/total_sec*100:.1f}%)")
    except ValueError:
        print(f"\n{role}: chi-square failed (degenerate matrix)")
        section_suffix_results[role] = {'chi2': None, 'p_value': None, 'note': 'degenerate'}

# ============================================================
# 6. SUFFIX x REGIME INTERACTION
# ============================================================
print("\n" + "-" * 70)
print("5. SUFFIX x REGIME INTERACTION (per role)")
print("-" * 70)

REGIMES = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
regime_suffix_results = {}

for role in ROLES:
    regime_rows = []
    for reg in REGIMES:
        row = [regime_role_suffix[reg][role].get(s, 0) for s in all_suffix_cats]
        regime_rows.append(row)
    regime_matrix = np.array(regime_rows)
    nz = regime_matrix.sum(axis=0) > 0
    rm_filtered = regime_matrix[:, nz]

    if rm_filtered.shape[1] < 2 or rm_filtered.sum() < 10:
        print(f"\n{role}: Insufficient data for REGIME x suffix test")
        regime_suffix_results[role] = {'chi2': None, 'p_value': None, 'note': 'insufficient data'}
        continue

    try:
        chi2_r, p_r, dof_r, _ = stats.chi2_contingency(rm_filtered)
        sig = 'SIGNIFICANT' if p_r < 0.01 else 'not significant'
        print(f"\n{role}: chi2={chi2_r:.1f}, dof={dof_r}, p={p_r:.2e} [{sig}]")
        regime_suffix_results[role] = {'chi2': round(chi2_r, 2), 'p_value': float(p_r)}
    except ValueError:
        print(f"\n{role}: chi-square failed")
        regime_suffix_results[role] = {'chi2': None, 'p_value': None, 'note': 'degenerate'}

# ============================================================
# 7. CROSS-ROLE SUFFIX JACCARD
# ============================================================
print("\n" + "-" * 70)
print("6. CROSS-ROLE SUFFIX JACCARD MATRIX")
print("-" * 70)

suffix_jaccard = {}
print(f"\n{'':>4}", end='')
for r in ROLES:
    print(f"  {r:>6}", end='')
print()

for r1 in ROLES:
    print(f"{r1:>4}", end='')
    row = {}
    for r2 in ROLES:
        s1 = role_suffix_sets[r1]
        s2 = role_suffix_sets[r2]
        inter = len(s1 & s2)
        union = len(s1 | s2)
        j = inter / union if union > 0 else 0
        row[r2] = round(j, 4)
        print(f"  {j:6.3f}", end='')
    suffix_jaccard[r1] = row
    print()

# ============================================================
# 8. PER-CLASS SUFFIX SUMMARY (CC, FL, FQ)
# ============================================================
print("\n" + "-" * 70)
print("7. PER-CLASS SUFFIX PROFILES (CC, FL, FQ)")
print("-" * 70)

class_suffix_profiles = {}
for role_name, role_classes in [('CC', CC_FINAL), ('FL', FL_FINAL), ('FQ', FQ_FINAL)]:
    print(f"\n{role_name}:")
    print(f"  {'Cls':>4} {'Total':>6} {'NoSfx%':>7} {'TopSfx':>8} {'TopPct':>7} {'NSfx':>5}")
    for cls in sorted(role_classes):
        total = class_total.get(cls, 0)
        if total == 0:
            print(f"  {cls:>4}      0      --       --      --    -- EMPTY")
            continue
        counts = class_suffix_counts[cls]
        nosuffix_ct = counts.get('NONE', 0)
        nosuffix_rate = nosuffix_ct / total * 100
        suffixes = {s for s in counts if s != 'NONE'}
        n_sfx = len(suffixes)

        if suffixes:
            top_sfx = max(suffixes, key=lambda s: counts[s])
            top_pct = counts[top_sfx] / total * 100
        else:
            top_sfx = '-'
            top_pct = 0

        print(f"  {cls:>4} {total:>6} {nosuffix_rate:>6.1f} {top_sfx:>8} {top_pct:>6.1f} {n_sfx:>5}")

        class_suffix_profiles[str(cls)] = {
            'role': role_name,
            'total': total,
            'nosuffix_pct': round(nosuffix_rate, 2),
            'n_suffix_types': n_sfx,
            'top_suffix': top_sfx,
            'top_suffix_pct': round(top_pct, 2),
            'suffix_distribution': {s: c for s, c in counts.items() if s != 'NONE'}
        }

# ============================================================
# SAVE RESULTS
# ============================================================

results = {
    'role_suffix_inventory': {
        role: {
            'total_tokens': role_total[role],
            'suffix_types': len(role_suffix_sets[role]),
            'nosuffix_count': role_nosuffix[role],
            'nosuffix_pct': round(role_nosuffix[role] / role_total[role] * 100, 2) if role_total[role] > 0 else 0,
            'top_suffixes': dict(role_suffix_counts[role].most_common(10)),
            'all_suffixes': sorted(role_suffix_sets[role])
        }
        for role in ROLES
    },
    'suffix_selectivity': {
        'chi2': round(chi2, 2),
        'p_value': float(p_value),
        'dof': dof,
        'significant': p_value < 0.001,
        'top_enrichments': [
            {'role': r, 'suffix': s, 'residual': round(res, 2), 'count': int(obs)}
            for r, s, res, obs in enrichments[:10]
        ],
        'top_depletions': [
            {'role': r, 'suffix': s, 'residual': round(res, 2), 'count': int(obs)}
            for r, s, res, obs in depletions[:10]
        ]
    },
    'nosuffix_rates': nosuffix_rates,
    'nosuffix_chi2': {'chi2': round(chi2_ns, 2), 'p_value': float(p_ns)},
    'section_suffix_interaction': section_suffix_results,
    'regime_suffix_interaction': regime_suffix_results,
    'suffix_jaccard_matrix': suffix_jaccard,
    'class_suffix_profiles': class_suffix_profiles
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sr_suffix_analysis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'sr_suffix_analysis.json'}")
