#!/usr/bin/env python3
"""
AX BEHAVIORAL UNPACKING - Script 3: Context Conditioning

Tests whether section, REGIME, or LINK context affects AX behavior.

Sections:
1. Section-Stratified AX Transitions
2. Section-Specific AX MIDDLE Selection
3. AX-REGIME Interaction
4. AX-LINK Interaction
"""

import os
import sys
import json
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, kruskal, spearmanr

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("=" * 70)
print("AX BEHAVIORAL UNPACKING - Script 3: Context Conditioning")
print("=" * 70)

tx = Transcript()
morph = Morphology()

with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

with open('phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json', 'r') as f:
    regime_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']

ROLE_ABBREV = {
    'CORE_CONTROL': 'CC',
    'ENERGY_OPERATOR': 'EN',
    'FLOW_OPERATOR': 'FL',
    'FREQUENT_OPERATOR': 'FQ',
    'AUXILIARY': 'AX',
}

AX_INIT_CLASSES = {4, 5, 6, 24, 26}
AX_MED_CLASSES = {1, 2, 3, 16, 18, 27, 28, 29}
AX_FINAL_CLASSES = {15, 19, 20, 21, 22, 25}

def get_subgroup(cls_num):
    if cls_num in AX_INIT_CLASSES:
        return 'AX_INIT'
    elif cls_num in AX_MED_CLASSES:
        return 'AX_MED'
    elif cls_num in AX_FINAL_CLASSES:
        return 'AX_FINAL'
    return None

def get_role(word):
    if word in token_to_class:
        cls = str(token_to_class[word])
        role = class_to_role.get(cls, 'UNKNOWN')
        return ROLE_ABBREV.get(role, role)
    return 'UN'

def is_link(word):
    return 'ol' in word

# Build folio -> REGIME lookup
folio_to_regime = {}
for regime, folios in regime_map.items():
    for f in folios:
        folio_to_regime[f] = regime

# Build line sequences
b_tokens = list(tx.currier_b())
total_b = len(b_tokens)
print(f"Total Currier B tokens: {total_b}")

line_seqs = defaultdict(list)
for t in b_tokens:
    line_seqs[(t.folio, t.line)].append(t)

# Classify all AX tokens with full context
ax_data = []  # (token, subgroup, morph, line_key, pos, section, regime)
for key, seq in line_seqs.items():
    for i, t in enumerate(seq):
        if t.word in token_to_class:
            cls = token_to_class[t.word]
            cls_str = str(cls)
            role_full = class_to_role.get(cls_str, 'UNKNOWN')
            if ROLE_ABBREV.get(role_full) == 'AX':
                sg = get_subgroup(cls)
                if sg:
                    m = morph.extract(t.word)
                    section = t.section if t.section else 'UNK'
                    regime = folio_to_regime.get(t.folio, 'NONE')
                    ax_data.append((t, sg, m, key, i, section, regime))

print(f"AX tokens: {len(ax_data)}")

sections = sorted(set(s for _, _, _, _, _, s, _ in ax_data))
regimes = sorted(set(r for _, _, _, _, _, _, r in ax_data if r != 'NONE'))
print(f"Sections present: {sections}")
print(f"Regimes present: {regimes}")

section_counts = Counter(s for _, _, _, _, _, s, _ in ax_data)
print(f"AX by section: {dict(section_counts)}")

roles_order = ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']

# ==============================================================================
# SECTION 1: SECTION-STRATIFIED AX TRANSITIONS
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 1: SECTION-STRATIFIED AX TRANSITIONS")
print("=" * 70)

# Per section: AX -> next-role distribution
section_transitions = defaultdict(Counter)

for t, sg, m, key, pos, section, regime in ax_data:
    seq = line_seqs[key]
    if pos + 1 < len(seq):
        next_role = get_role(seq[pos + 1].word)
        section_transitions[section][next_role] += 1

print(f"\nAX -> next-role by section:")
print(f"  {'Section':<8} {'N':>6} {'CC':>6} {'EN':>6} {'FL':>6} {'FQ':>6} {'AX':>6} {'UN':>6}")
print(f"  {'-' * 55}")

for section in sections:
    dist = section_transitions[section]
    n = sum(dist.values())
    vals = [f"{dist.get(r, 0) / n * 100:5.1f}%" for r in roles_order]
    print(f"  {section:<8} {n:>6} {' '.join(vals)}")

# Chi-squared: section x next-role contingency table
table_rows = []
valid_sections = []
for section in sections:
    dist = section_transitions[section]
    n = sum(dist.values())
    if n >= 20:
        table_rows.append([dist.get(r, 0) for r in roles_order])
        valid_sections.append(section)

if len(table_rows) >= 2:
    table = np.array(table_rows)
    nonzero_cols = table.sum(axis=0) > 0
    table_f = table[:, nonzero_cols]

    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2, p, dof, exp = chi2_contingency(table_f)
        n_total = table_f.sum()
        k = min(table_f.shape)
        V = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 and k > 1 else 0

        print(f"\nChi-squared (section x next-role):")
        print(f"  chi2={chi2:.2f}, p={p:.6f}, dof={dof}, V={V:.3f}")
        print(f"  {'SECTION AFFECTS AX TRANSITIONS' if p < 0.05 else 'Section does NOT affect AX transitions'}")

# Pairwise: Section B vs Section S (lowest vs highest UN proportion per C551)
for s1, s2 in [('B', 'S'), ('B', 'T'), ('H', 'S')]:
    if s1 in section_transitions and s2 in section_transitions:
        d1 = section_transitions[s1]
        d2 = section_transitions[s2]
        n1 = sum(d1.values())
        n2 = sum(d2.values())
        if n1 >= 20 and n2 >= 20:
            pair_table = np.array([[d1.get(r, 0) for r in roles_order],
                                   [d2.get(r, 0) for r in roles_order]])
            nz = pair_table.sum(axis=0) > 0
            pair_f = pair_table[:, nz]
            if pair_f.shape[1] >= 2:
                chi2_p, p_p, dof_p, _ = chi2_contingency(pair_f)
                print(f"  {s1} vs {s2}: chi2={chi2_p:.2f}, p={p_p:.4f}")

# ==============================================================================
# SECTION 2: SECTION-SPECIFIC AX MIDDLE SELECTION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 2: SECTION-SPECIFIC AX MIDDLE SELECTION")
print("=" * 70)

# Per section: AX MIDDLE frequency distribution
section_middles = defaultdict(Counter)
for t, sg, m, key, pos, section, regime in ax_data:
    mid = m.middle if m.middle else '_NONE_'
    section_middles[section][mid] += 1

# Find MIDDLEs with sufficient representation
all_middles = set()
for dist in section_middles.values():
    all_middles.update(dist.keys())

# Filter to MIDDLEs appearing >= 20 times total
middle_totals = Counter()
for dist in section_middles.values():
    for mid, count in dist.items():
        middle_totals[mid] += count

frequent_middles = sorted([m for m, c in middle_totals.items() if c >= 20],
                          key=lambda m: middle_totals[m], reverse=True)

print(f"\nTotal unique AX MIDDLEs: {len(all_middles)}")
print(f"MIDDLEs with >= 20 occurrences: {len(frequent_middles)}")

# Chi-squared: section x MIDDLE contingency table (frequent MIDDLEs only)
if len(frequent_middles) >= 2:
    table_rows = []
    for section in valid_sections:
        row = [section_middles[section].get(mid, 0) for mid in frequent_middles]
        table_rows.append(row)

    table = np.array(table_rows)
    nonzero_cols = table.sum(axis=0) > 0
    table_f = table[:, nonzero_cols]
    middles_f = [m for m, nz in zip(frequent_middles, nonzero_cols) if nz]

    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2, p, dof, exp = chi2_contingency(table_f)
        n_total = table_f.sum()
        k = min(table_f.shape)
        V = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 and k > 1 else 0

        print(f"\nChi-squared (section x MIDDLE):")
        print(f"  chi2={chi2:.2f}, p={p:.6f}, dof={dof}, V={V:.3f}")
        print(f"  {'SECTION AFFECTS AX MIDDLE SELECTION' if p < 0.05 else 'Section does NOT affect AX MIDDLE selection'}")

# Find section-enriched MIDDLEs
print(f"\nSection-enriched MIDDLEs (>= 2x expected proportion):")
for mid in frequent_middles[:20]:
    total = middle_totals[mid]
    enriched = []
    for section in valid_sections:
        sec_count = section_middles[section].get(mid, 0)
        sec_total = sum(section_middles[section].values())
        if sec_total == 0:
            continue
        observed = sec_count / sec_total
        expected = total / sum(middle_totals.values())
        if expected > 0 and observed / expected >= 2.0:
            enriched.append(f"{section}({observed / expected:.1f}x)")
    if enriched:
        print(f"  {mid}: {', '.join(enriched)}")

# ==============================================================================
# SECTION 3: AX-REGIME INTERACTION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 3: AX-REGIME INTERACTION")
print("=" * 70)

# Per REGIME: AX -> next-role distribution
regime_transitions = defaultdict(Counter)
for t, sg, m, key, pos, section, regime in ax_data:
    if regime == 'NONE':
        continue
    seq = line_seqs[key]
    if pos + 1 < len(seq):
        next_role = get_role(seq[pos + 1].word)
        regime_transitions[regime][next_role] += 1

print(f"\nAX -> next-role by REGIME:")
print(f"  {'REGIME':<12} {'N':>6} {'CC':>6} {'EN':>6} {'FL':>6} {'FQ':>6} {'AX':>6} {'UN':>6}")
print(f"  {'-' * 58}")

for regime in sorted(regimes):
    dist = regime_transitions[regime]
    n = sum(dist.values())
    if n == 0:
        continue
    vals = [f"{dist.get(r, 0) / n * 100:5.1f}%" for r in roles_order]
    print(f"  {regime:<12} {n:>6} {' '.join(vals)}")

# Chi-squared: REGIME x next-role
regime_table_rows = []
valid_regimes = []
for regime in sorted(regimes):
    dist = regime_transitions[regime]
    n = sum(dist.values())
    if n >= 20:
        regime_table_rows.append([dist.get(r, 0) for r in roles_order])
        valid_regimes.append(regime)

regime_chi2_result = {}
if len(regime_table_rows) >= 2:
    table = np.array(regime_table_rows)
    nonzero_cols = table.sum(axis=0) > 0
    table_f = table[:, nonzero_cols]

    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2, p, dof, exp = chi2_contingency(table_f)
        n_total = table_f.sum()
        k = min(table_f.shape)
        V = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 and k > 1 else 0

        print(f"\nChi-squared (REGIME x next-role):")
        print(f"  chi2={chi2:.2f}, p={p:.6f}, dof={dof}, V={V:.3f}")
        sig = p < 0.05
        print(f"  {'REGIME AFFECTS AX TRANSITIONS' if sig else 'REGIME does NOT affect AX transitions'}")

        regime_chi2_result = {
            'chi2': round(float(chi2), 2),
            'p': round(float(p), 6),
            'V': round(float(V), 3),
            'significant': bool(sig),
        }

# Kruskal-Wallis on AX->EN proportion per folio by REGIME
print(f"\nKruskal-Wallis: AX->EN proportion by REGIME:")
folio_ax_en = defaultdict(lambda: [0, 0])  # folio -> [AX->EN count, AX total]
for t, sg, m, key, pos, section, regime in ax_data:
    seq = line_seqs[key]
    if pos + 1 < len(seq):
        next_role = get_role(seq[pos + 1].word)
        folio_ax_en[t.folio][1] += 1
        if next_role == 'EN':
            folio_ax_en[t.folio][0] += 1

regime_en_proportions = defaultdict(list)
for folio, (en_count, total) in folio_ax_en.items():
    regime = folio_to_regime.get(folio, 'NONE')
    if regime != 'NONE' and total >= 5:
        regime_en_proportions[regime].append(en_count / total)

if len(regime_en_proportions) >= 2:
    groups = [regime_en_proportions[r] for r in sorted(regime_en_proportions.keys())
              if len(regime_en_proportions[r]) >= 3]
    if len(groups) >= 2:
        H_stat, p_kw = kruskal(*groups)
        print(f"  H={H_stat:.2f}, p={p_kw:.4f}")
        print(f"  {'REGIME AFFECTS AX->EN proportion' if p_kw < 0.05 else 'REGIME does NOT affect AX->EN proportion'}")

        for regime in sorted(regime_en_proportions.keys()):
            props = regime_en_proportions[regime]
            if len(props) >= 3:
                print(f"    {regime}: mean={np.mean(props):.3f}, median={np.median(props):.3f}, n={len(props)}")

# Focus on AX->FQ by REGIME (C602 says this is REGIME-independent)
print(f"\nAX->FQ proportion by REGIME (C602 reference):")
regime_fq_proportions = defaultdict(list)
for folio, (en_count, total) in folio_ax_en.items():
    # Recompute for FQ
    pass

# Recompute for FQ specifically
folio_ax_fq = defaultdict(lambda: [0, 0])
for t, sg, m, key, pos, section, regime in ax_data:
    seq = line_seqs[key]
    if pos + 1 < len(seq):
        next_role = get_role(seq[pos + 1].word)
        folio_ax_fq[t.folio][1] += 1
        if next_role == 'FQ':
            folio_ax_fq[t.folio][0] += 1

regime_fq_props = defaultdict(list)
for folio, (fq_count, total) in folio_ax_fq.items():
    regime = folio_to_regime.get(folio, 'NONE')
    if regime != 'NONE' and total >= 5:
        regime_fq_props[regime].append(fq_count / total)

if len(regime_fq_props) >= 2:
    groups_fq = [regime_fq_props[r] for r in sorted(regime_fq_props.keys())
                 if len(regime_fq_props[r]) >= 3]
    if len(groups_fq) >= 2:
        H_fq, p_fq = kruskal(*groups_fq)
        print(f"  H={H_fq:.2f}, p={p_fq:.4f}")
        print(f"  {'REGIME AFFECTS AX->FQ' if p_fq < 0.05 else 'REGIME-INDEPENDENT (consistent with C602)'}")

# ==============================================================================
# SECTION 4: AX-LINK INTERACTION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 4: AX-LINK INTERACTION")
print("=" * 70)

# LINK detection: 'ol' in word (C609: 13.2% of B tokens)
link_count = sum(1 for t in b_tokens if is_link(t.word))
print(f"\nLINK tokens in B: {link_count} ({link_count / total_b * 100:.1f}%)")

# Per-line: AX presence and LINK presence
line_ax_present = {}
line_link_present = {}
line_ax_count = Counter()
line_link_count = Counter()

for key, seq in line_seqs.items():
    has_ax = False
    has_link = False
    ax_c = 0
    link_c = 0
    for t in seq:
        role = get_role(t.word)
        if role == 'AX':
            has_ax = True
            ax_c += 1
        if is_link(t.word):
            has_link = True
            link_c += 1
    line_ax_present[key] = has_ax
    line_link_present[key] = has_link
    line_ax_count[key] = ax_c
    line_link_count[key] = link_c

# Co-occurrence: how often do AX and LINK appear in the same line?
both = sum(1 for k in line_seqs if line_ax_present.get(k) and line_link_present.get(k))
ax_only = sum(1 for k in line_seqs if line_ax_present.get(k) and not line_link_present.get(k))
link_only = sum(1 for k in line_seqs if not line_ax_present.get(k) and line_link_present.get(k))
neither = sum(1 for k in line_seqs if not line_ax_present.get(k) and not line_link_present.get(k))
total_lines = len(line_seqs)

print(f"\nLine-level co-occurrence (n={total_lines} lines):")
print(f"  AX + LINK:   {both:>5} ({both / total_lines * 100:.1f}%)")
print(f"  AX only:     {ax_only:>5} ({ax_only / total_lines * 100:.1f}%)")
print(f"  LINK only:   {link_only:>5} ({link_only / total_lines * 100:.1f}%)")
print(f"  Neither:     {neither:>5} ({neither / total_lines * 100:.1f}%)")

# Chi-squared: AX presence x LINK presence
cooc_table = np.array([[both, ax_only], [link_only, neither]])
if cooc_table.min() >= 0:
    chi2_cooc, p_cooc, dof_cooc, _ = chi2_contingency(cooc_table)
    print(f"\n  Chi-squared (AX x LINK line co-occurrence):")
    print(f"  chi2={chi2_cooc:.2f}, p={p_cooc:.6f}")
    print(f"  {'AX and LINK co-occur NON-RANDOMLY' if p_cooc < 0.05 else 'AX and LINK co-occur at random rates'}")

# Does AX subgroup predict LINK proximity?
# For each AX token, find distance to nearest LINK in same line
print(f"\nAX subgroup -> LINK proximity:")
sg_link_distances = defaultdict(list)

for t, sg, m, key, pos, section, regime in ax_data:
    seq = line_seqs[key]
    link_positions = [i for i, s in enumerate(seq) if is_link(s.word)]
    if link_positions:
        min_dist = min(abs(pos - lp) for lp in link_positions)
        sg_link_distances[sg].append(min_dist)
    # Tokens with no LINK in line get no entry (distance = infinity)

for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    dists = sg_link_distances[sg]
    if dists:
        ax_sg_total = sum(1 for _, s, _, _, _, _, _ in ax_data if s == sg)
        print(f"  {sg}: mean dist={np.mean(dists):.2f}, median={np.median(dists):.1f}, "
              f"with LINK={len(dists)}/{ax_sg_total} ({len(dists)/ax_sg_total*100:.1f}%)")

# Are AX tokens themselves LINK tokens?
ax_link_count = sum(1 for t, sg, m, key, pos, s, r in ax_data if is_link(t.word))
print(f"\nAX tokens that ARE LINK: {ax_link_count}/{len(ax_data)} ({ax_link_count/len(ax_data)*100:.1f}%)")

# By subgroup
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    sg_total = sum(1 for _, s, _, _, _, _, _ in ax_data if s == sg)
    sg_link = sum(1 for t, s, _, _, _, _, _ in ax_data if s == sg and is_link(t.word))
    print(f"  {sg}: {sg_link}/{sg_total} ({sg_link/sg_total*100:.1f}%)")

# Folio-level: AX proportion vs LINK density
folio_ax_prop = Counter()
folio_link_prop = Counter()
folio_total = Counter()

for t in b_tokens:
    folio_total[t.folio] += 1
    if get_role(t.word) == 'AX':
        folio_ax_prop[t.folio] += 1
    if is_link(t.word):
        folio_link_prop[t.folio] += 1

folios = sorted(set(t.folio for t in b_tokens))
ax_props = np.array([folio_ax_prop[f] / folio_total[f] if folio_total[f] > 0 else 0 for f in folios])
link_props = np.array([folio_link_prop[f] / folio_total[f] if folio_total[f] > 0 else 0 for f in folios])

rho, p_rho = spearmanr(ax_props, link_props)
sig_str = '***' if p_rho < 0.001 else ('**' if p_rho < 0.01 else ('*' if p_rho < 0.05 else ''))
print(f"\nFolio-level: AX proportion vs LINK density:")
print(f"  Spearman rho={rho:+.3f}, p={p_rho:.4f} {sig_str}")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

# Section transition chi2
section_chi2 = {}
if len(table_rows) >= 2:
    table = np.array(table_rows)
    nonzero_cols = table.sum(axis=0) > 0
    table_f = table[:, nonzero_cols]
    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2, p, dof, exp = chi2_contingency(table_f)
        n_total = table_f.sum()
        k = min(table_f.shape)
        V = np.sqrt(chi2 / (n_total * (k - 1))) if n_total > 0 and k > 1 else 0
        section_chi2 = {
            'chi2': round(float(chi2), 2),
            'p': round(float(p), 6),
            'V': round(float(V), 3),
            'significant': bool(p < 0.05),
        }

results = {
    'ax_count': len(ax_data),
    'section_transitions': {
        'chi2_test': section_chi2,
        'sections': {s: dict(section_transitions[s]) for s in sections},
    },
    'section_middle_selection': {
        'unique_middles': len(all_middles),
        'frequent_middles': len(frequent_middles),
    },
    'regime_interaction': {
        'chi2_test': regime_chi2_result,
        'regimes': {r: dict(regime_transitions[r]) for r in sorted(regimes)},
    },
    'link_interaction': {
        'ax_link_rate': round(ax_link_count / len(ax_data) * 100, 1),
        'by_subgroup': {},
        'folio_correlation': {
            'rho': round(float(rho), 3),
            'p': round(float(p_rho), 4),
        },
        'line_cooccurrence': {
            'both': both,
            'ax_only': ax_only,
            'link_only': link_only,
            'neither': neither,
        },
    },
}

# Add subgroup LINK rates
for sg in ['AX_INIT', 'AX_MED', 'AX_FINAL']:
    sg_total = sum(1 for _, s, _, _, _, _, _ in ax_data if s == sg)
    sg_link = sum(1 for t, s, _, _, _, _, _ in ax_data if s == sg and is_link(t.word))
    results['link_interaction']['by_subgroup'][sg] = {
        'link_rate_pct': round(sg_link / sg_total * 100, 1) if sg_total > 0 else 0,
        'total': sg_total,
        'link_count': sg_link,
    }

output_path = 'phases/AX_BEHAVIORAL_UNPACKING/results/ax_context_conditioning.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\n{'=' * 70}")
print("AX CONTEXT CONDITIONING COMPLETE")
print(f"{'=' * 70}")
