"""
SISTER_PAIR_DECOMPOSITION Script 1: EN Subfamily Selection

What determines whether an EN token is QO or CHSH?
Tests REGIME, section, line position, and CC trigger composition
as predictors of EN subfamily balance at the folio level.

Data dependencies:
  - class_token_map.json (CLASS_COSURVIVAL_TEST)
  - regime_folio_mapping.json (REGIME_SEMANTIC_INTERPRETATION)
  - voynich.py (scripts/)
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
REGIME_FILE = BASE / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json'
RESULTS = BASE / 'phases/SISTER_PAIR_DECOMPOSITION/results'

# Sub-group definitions (from SUB_ROLE_INTERACTION)
EN_QO = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}
EN_MINOR = {41}
EN_CLASSES = EN_QO | EN_CHSH | EN_MINOR

CC_DAIIN = {10}
CC_OL = {11}
CC_OL_D = {17}
CC_CLASSES = CC_DAIIN | CC_OL | CC_OL_D

FL_HAZ = {7, 30}
FL_SAFE = {38, 40}
FL_CLASSES = FL_HAZ | FL_SAFE

def get_en_subfamily(cls):
    if cls in EN_QO: return 'QO'
    if cls in EN_CHSH: return 'CHSH'
    if cls in EN_MINOR: return 'MINOR'
    return None

def get_cc_subgroup(cls):
    if cls in CC_DAIIN: return 'CC_DAIIN'
    if cls in CC_OL: return 'CC_OL'
    if cls in CC_OL_D: return 'CC_OL_D'
    return None

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("SISTER_PAIR_DECOMPOSITION: EN SUBFAMILY SELECTION")
print("=" * 70)

tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

with open(REGIME_FILE) as f:
    regime_data = json.load(f)
folio_regime = {}
for regime, folios in regime_data.items():
    for folio in folios:
        folio_regime[folio] = regime

# Build per-line token structures
lines = defaultdict(list)
for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    lines[(token.folio, token.line)].append({
        'word': word,
        'class': cls,
        'folio': token.folio,
        'section': token.section,
    })

# Compute normalized positions
for (folio, line_id), line_tokens in lines.items():
    n = len(line_tokens)
    for i, tok in enumerate(line_tokens):
        tok['position'] = i / (n - 1) if n > 1 else 0.5

# Verification counts
en_total = sum(1 for t in tokens if token_to_class.get(t.word.strip()) in EN_CLASSES and t.word.strip())
qo_total = sum(1 for t in tokens if token_to_class.get(t.word.strip()) in EN_QO and t.word.strip())
chsh_total = sum(1 for t in tokens if token_to_class.get(t.word.strip()) in EN_CHSH and t.word.strip())
minor_total = sum(1 for t in tokens if token_to_class.get(t.word.strip()) in EN_MINOR and t.word.strip())

print(f"\nVerification: EN total = {en_total} (expected ~7211)")
print(f"  QO: {qo_total}, CHSH: {chsh_total}, MINOR: {minor_total}")
print(f"  Sum: {qo_total + chsh_total + minor_total}")
print(f"  QO%: {qo_total/en_total*100:.1f}%, CHSH%: {chsh_total/en_total*100:.1f}%")

results = {}

# ============================================================
# SECTION 1: EN SUBFAMILY BALANCE BY REGIME
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: EN SUBFAMILY BALANCE BY REGIME")
print("=" * 70)

REGIMES = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
subfamilies = ['QO', 'CHSH', 'MINOR']

regime_counts = {r: Counter() for r in REGIMES}
for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    sf = get_en_subfamily(cls)
    if sf is None:
        continue
    regime = folio_regime.get(token.folio, 'UNKNOWN')
    if regime in REGIMES:
        regime_counts[regime][sf] += 1

# Build contingency table
contingency_regime = np.zeros((len(REGIMES), len(subfamilies)), dtype=int)
print(f"\n{'Regime':>12} {'QO':>6} {'CHSH':>6} {'MINOR':>6} {'Total':>6} {'QO%':>6} {'CHSH%':>7}")
for i, reg in enumerate(REGIMES):
    for j, sf in enumerate(subfamilies):
        contingency_regime[i, j] = regime_counts[reg][sf]
    total = contingency_regime[i].sum()
    qo_pct = contingency_regime[i, 0] / total * 100 if total > 0 else 0
    chsh_pct = contingency_regime[i, 1] / total * 100 if total > 0 else 0
    print(f"{reg:>12} {contingency_regime[i,0]:>6} {contingency_regime[i,1]:>6} {contingency_regime[i,2]:>6} {total:>6} {qo_pct:>5.1f}% {chsh_pct:>6.1f}%")

chi2_r, p_r, dof_r, expected_r = stats.chi2_contingency(contingency_regime)
n_total_r = contingency_regime.sum()
min_dim_r = min(len(REGIMES), len(subfamilies)) - 1
cramers_v_r = np.sqrt(chi2_r / (n_total_r * min_dim_r))

print(f"\nChi-squared: chi2={chi2_r:.2f}, df={dof_r}, p={p_r:.6f}")
print(f"Cramer's V: {cramers_v_r:.3f}")
print(f"REGIME x EN Subfamily: {'DEPENDENT (p<0.05)' if p_r < 0.05 else 'INDEPENDENT'}")

# Enrichment per REGIME
regime_enrichment = {}
for i, reg in enumerate(REGIMES):
    total_reg = contingency_regime[i].sum()
    if total_reg == 0:
        continue
    enr = {}
    for j, sf in enumerate(subfamilies):
        observed = contingency_regime[i, j] / total_reg
        expected_rate = contingency_regime[:, j].sum() / n_total_r
        enr[sf] = round(observed / expected_rate, 3) if expected_rate > 0 else 0
    regime_enrichment[reg] = enr
    print(f"  {reg}: QO enrich={enr['QO']:.3f}, CHSH enrich={enr['CHSH']:.3f}")

results['regime_balance'] = {
    'contingency': {REGIMES[i]: {subfamilies[j]: int(contingency_regime[i, j])
                     for j in range(len(subfamilies))}
                     for i in range(len(REGIMES))},
    'chi2': round(float(chi2_r), 4),
    'p_value': float(p_r),
    'dof': int(dof_r),
    'cramers_v': round(float(cramers_v_r), 4),
    'enrichment': regime_enrichment,
    'significant': bool(p_r < 0.05),
}

# ============================================================
# SECTION 2: EN SUBFAMILY BALANCE BY SECTION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: EN SUBFAMILY BALANCE BY SECTION")
print("=" * 70)

section_counts = defaultdict(Counter)
for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    sf = get_en_subfamily(cls)
    if sf is None:
        continue
    section_counts[token.section][sf] += 1

# Use B-relevant sections with enough data
b_sections = sorted([s for s, c in section_counts.items() if sum(c.values()) >= 50])
contingency_sec = np.zeros((len(b_sections), len(subfamilies)), dtype=int)

print(f"\n{'Section':>12} {'QO':>6} {'CHSH':>6} {'MINOR':>6} {'Total':>6} {'QO%':>6} {'CHSH%':>7}")
for i, sec in enumerate(b_sections):
    for j, sf in enumerate(subfamilies):
        contingency_sec[i, j] = section_counts[sec][sf]
    total = contingency_sec[i].sum()
    qo_pct = contingency_sec[i, 0] / total * 100 if total > 0 else 0
    chsh_pct = contingency_sec[i, 1] / total * 100 if total > 0 else 0
    print(f"{sec:>12} {contingency_sec[i,0]:>6} {contingency_sec[i,1]:>6} {contingency_sec[i,2]:>6} {total:>6} {qo_pct:>5.1f}% {chsh_pct:>6.1f}%")

if len(b_sections) >= 2:
    chi2_s, p_s, dof_s, _ = stats.chi2_contingency(contingency_sec)
    n_total_s = contingency_sec.sum()
    min_dim_s = min(len(b_sections), len(subfamilies)) - 1
    cramers_v_s = np.sqrt(chi2_s / (n_total_s * min_dim_s))
    print(f"\nChi-squared: chi2={chi2_s:.2f}, df={dof_s}, p={p_s:.6f}")
    print(f"Cramer's V: {cramers_v_s:.3f}")
    print(f"Section x EN Subfamily: {'DEPENDENT (p<0.05)' if p_s < 0.05 else 'INDEPENDENT'}")

    # Section enrichment
    sec_enrichment = {}
    for i, sec in enumerate(b_sections):
        total_sec = contingency_sec[i].sum()
        if total_sec == 0:
            continue
        enr = {}
        for j, sf in enumerate(subfamilies):
            observed = contingency_sec[i, j] / total_sec
            expected_rate = contingency_sec[:, j].sum() / n_total_s
            enr[sf] = round(observed / expected_rate, 3) if expected_rate > 0 else 0
        sec_enrichment[sec] = enr
        print(f"  {sec}: QO enrich={enr['QO']:.3f}, CHSH enrich={enr['CHSH']:.3f}")

    results['section_balance'] = {
        'sections': b_sections,
        'contingency': {b_sections[i]: {subfamilies[j]: int(contingency_sec[i, j])
                         for j in range(len(subfamilies))}
                         for i in range(len(b_sections))},
        'chi2': round(float(chi2_s), 4),
        'p_value': float(p_s),
        'dof': int(dof_s),
        'cramers_v': round(float(cramers_v_s), 4),
        'enrichment': sec_enrichment,
        'significant': bool(p_s < 0.05),
    }
else:
    print("Insufficient sections for chi-squared test")
    results['section_balance'] = {'verdict': 'insufficient_sections'}

# ============================================================
# SECTION 3: EN SUBFAMILY BALANCE BY LINE POSITION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: EN SUBFAMILY BALANCE BY LINE POSITION")
print("=" * 70)

ZONES = {
    'INITIAL': (0.0, 0.2),
    'EARLY': (0.2, 0.4),
    'MEDIAL': (0.4, 0.6),
    'LATE': (0.6, 0.8),
    'FINAL': (0.8, 1.01),
}
zone_names = list(ZONES.keys())

zone_counts = {z: Counter() for z in zone_names}
for (folio, line_id), line_tokens in lines.items():
    for tok in line_tokens:
        cls = tok['class']
        sf = get_en_subfamily(cls)
        if sf is None:
            continue
        pos = tok['position']
        for zone_name, (lo, hi) in ZONES.items():
            if lo <= pos < hi:
                zone_counts[zone_name][sf] += 1
                break

contingency_pos = np.zeros((len(zone_names), len(subfamilies)), dtype=int)
print(f"\n{'Zone':>12} {'QO':>6} {'CHSH':>6} {'MINOR':>6} {'Total':>6} {'QO%':>6} {'CHSH%':>7}")
for i, zone in enumerate(zone_names):
    for j, sf in enumerate(subfamilies):
        contingency_pos[i, j] = zone_counts[zone][sf]
    total = contingency_pos[i].sum()
    qo_pct = contingency_pos[i, 0] / total * 100 if total > 0 else 0
    chsh_pct = contingency_pos[i, 1] / total * 100 if total > 0 else 0
    print(f"{zone:>12} {contingency_pos[i,0]:>6} {contingency_pos[i,1]:>6} {contingency_pos[i,2]:>6} {total:>6} {qo_pct:>5.1f}% {chsh_pct:>6.1f}%")

chi2_p, p_p, dof_p, _ = stats.chi2_contingency(contingency_pos)
n_total_p = contingency_pos.sum()
min_dim_p = min(len(zone_names), len(subfamilies)) - 1
cramers_v_p = np.sqrt(chi2_p / (n_total_p * min_dim_p))

print(f"\nChi-squared: chi2={chi2_p:.2f}, df={dof_p}, p={p_p:.6f}")
print(f"Cramer's V: {cramers_v_p:.3f}")
print(f"Position x EN Subfamily: {'DEPENDENT (p<0.05)' if p_p < 0.05 else 'INDEPENDENT'}")

# Position enrichment
pos_enrichment = {}
for i, zone in enumerate(zone_names):
    total_zone = contingency_pos[i].sum()
    if total_zone == 0:
        continue
    enr = {}
    for j, sf in enumerate(subfamilies):
        observed = contingency_pos[i, j] / total_zone
        expected_rate = contingency_pos[:, j].sum() / n_total_p
        enr[sf] = round(observed / expected_rate, 3) if expected_rate > 0 else 0
    pos_enrichment[zone] = enr

results['position_balance'] = {
    'contingency': {zone_names[i]: {subfamilies[j]: int(contingency_pos[i, j])
                     for j in range(len(subfamilies))}
                     for i in range(len(zone_names))},
    'chi2': round(float(chi2_p), 4),
    'p_value': float(p_p),
    'dof': int(dof_p),
    'cramers_v': round(float(cramers_v_p), 4),
    'enrichment': pos_enrichment,
    'significant': bool(p_p < 0.05),
}

# ============================================================
# SECTION 4: FOLIO-LEVEL QO PROPORTION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: FOLIO-LEVEL QO PROPORTION")
print("=" * 70)

folio_en_counts = defaultdict(Counter)
folio_total_b = Counter()
for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    folio_total_b[token.folio] += 1
    cls = token_to_class.get(word)
    sf = get_en_subfamily(cls)
    if sf is not None:
        folio_en_counts[token.folio][sf] += 1

# Require at least 10 EN tokens per folio
MIN_EN = 10
valid_folios = sorted([f for f, c in folio_en_counts.items()
                        if sum(c.values()) >= MIN_EN])
print(f"\nValid folios (>={MIN_EN} EN tokens): {len(valid_folios)}")

folio_data = {}
for folio in valid_folios:
    qo_count = folio_en_counts[folio]['QO']
    chsh_count = folio_en_counts[folio]['CHSH']
    minor_count = folio_en_counts[folio]['MINOR']
    en_total_f = qo_count + chsh_count + minor_count
    qo_prop = qo_count / en_total_f if en_total_f > 0 else 0
    chsh_prop = chsh_count / en_total_f if en_total_f > 0 else 0
    folio_data[folio] = {
        'qo_count': qo_count,
        'chsh_count': chsh_count,
        'minor_count': minor_count,
        'en_total': en_total_f,
        'b_total': folio_total_b[folio],
        'qo_proportion': round(qo_prop, 4),
        'chsh_proportion': round(chsh_prop, 4),
        'regime': folio_regime.get(folio, 'UNKNOWN'),
        'section': None,  # filled below
    }

# Get section for each folio (from first token)
folio_sections = {}
for token in tokens:
    if token.folio not in folio_sections:
        folio_sections[token.folio] = token.section
for folio in folio_data:
    folio_data[folio]['section'] = folio_sections.get(folio, 'UNKNOWN')

# Distribution of QO proportion
qo_props = [folio_data[f]['qo_proportion'] for f in valid_folios]
print(f"\nQO proportion distribution:")
print(f"  Mean: {np.mean(qo_props):.3f}")
print(f"  Std:  {np.std(qo_props):.3f}")
print(f"  Min:  {np.min(qo_props):.3f}")
print(f"  Max:  {np.max(qo_props):.3f}")
print(f"  Median: {np.median(qo_props):.3f}")

# Kruskal-Wallis: does REGIME predict folio-level QO proportion?
regime_qo_groups = defaultdict(list)
for folio in valid_folios:
    regime = folio_data[folio]['regime']
    if regime in REGIMES:
        regime_qo_groups[regime].append(folio_data[folio]['qo_proportion'])

groups = [regime_qo_groups[r] for r in REGIMES if len(regime_qo_groups[r]) >= 3]
if len(groups) >= 2:
    h_stat, kw_p = stats.kruskal(*groups)
    print(f"\nKruskal-Wallis (REGIME -> QO proportion):")
    print(f"  H={h_stat:.3f}, p={kw_p:.6f}")
    for r in REGIMES:
        vals = regime_qo_groups[r]
        if vals:
            print(f"  {r}: mean={np.mean(vals):.3f}, std={np.std(vals):.3f}, n={len(vals)}")
    results['folio_qo_regime_kw'] = {
        'H': round(float(h_stat), 4),
        'p_value': float(kw_p),
        'per_regime': {r: {'mean': round(float(np.mean(regime_qo_groups[r])), 4),
                           'std': round(float(np.std(regime_qo_groups[r])), 4),
                           'n': len(regime_qo_groups[r])}
                       for r in REGIMES if regime_qo_groups[r]},
        'significant': bool(kw_p < 0.05),
    }

results['folio_qo_distribution'] = {
    'n_folios': len(valid_folios),
    'mean': round(float(np.mean(qo_props)), 4),
    'std': round(float(np.std(qo_props)), 4),
    'min': round(float(np.min(qo_props)), 4),
    'max': round(float(np.max(qo_props)), 4),
    'median': round(float(np.median(qo_props)), 4),
}

# ============================================================
# SECTION 5: CC TRIGGER COMPOSITION BY FOLIO
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: CC TRIGGER COMPOSITION BY FOLIO")
print("=" * 70)

folio_cc_counts = defaultdict(Counter)
for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    cc_sg = get_cc_subgroup(cls)
    if cc_sg is not None:
        folio_cc_counts[token.folio][cc_sg] += 1

# Also count FL sub-groups per folio
folio_fl_counts = defaultdict(Counter)
for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    if cls in FL_HAZ:
        folio_fl_counts[token.folio]['FL_HAZ'] += 1
    elif cls in FL_SAFE:
        folio_fl_counts[token.folio]['FL_SAFE'] += 1

# Extend folio_data with CC and FL fractions
for folio in valid_folios:
    cc = folio_cc_counts[folio]
    daiin = cc.get('CC_DAIIN', 0)
    ol = cc.get('CC_OL', 0)
    old = cc.get('CC_OL_D', 0)
    cc_total = daiin + ol + old

    folio_data[folio]['cc_daiin'] = daiin
    folio_data[folio]['cc_ol'] = ol
    folio_data[folio]['cc_old'] = old
    folio_data[folio]['cc_total'] = cc_total
    folio_data[folio]['cc_daiin_fraction'] = round(daiin / cc_total, 4) if cc_total > 0 else None
    folio_data[folio]['cc_old_fraction'] = round(old / cc_total, 4) if cc_total > 0 else None

    fl = folio_fl_counts[folio]
    fl_haz = fl.get('FL_HAZ', 0)
    fl_safe = fl.get('FL_SAFE', 0)
    fl_total = fl_haz + fl_safe
    folio_data[folio]['fl_haz'] = fl_haz
    folio_data[folio]['fl_safe'] = fl_safe
    folio_data[folio]['fl_haz_fraction'] = round(fl_haz / fl_total, 4) if fl_total > 0 else None

# Spearman: CC_OL_D fraction vs EN QO proportion
# C600 showed OL_D triggers QO; so higher CC_OL_D -> higher QO proportion
cc_valid = [(folio_data[f]['cc_old_fraction'], folio_data[f]['qo_proportion'])
            for f in valid_folios
            if folio_data[f]['cc_old_fraction'] is not None]
if len(cc_valid) >= 10:
    cc_old_vals, qo_vals2 = zip(*cc_valid)
    rho_cc_qo, p_cc_qo = stats.spearmanr(cc_old_vals, qo_vals2)
    print(f"\nCC_OL_D fraction vs QO proportion:")
    print(f"  Spearman rho={rho_cc_qo:.3f}, p={p_cc_qo:.4f}, n={len(cc_valid)}")
    print(f"  Direction: {'Positive (OL_D predicts QO)' if rho_cc_qo > 0 else 'Negative (unexpected)'}")
else:
    rho_cc_qo, p_cc_qo = None, None
    print(f"\nInsufficient data for CC_OL_D vs QO test (n={len(cc_valid)})")

# Also test: CC_DAIIN fraction vs CHSH proportion
# C600 showed DAIIN triggers CHSH; so higher CC_DAIIN -> higher CHSH proportion
cc_daiin_valid = [(folio_data[f]['cc_daiin_fraction'], folio_data[f]['chsh_proportion'])
                  for f in valid_folios
                  if folio_data[f]['cc_daiin_fraction'] is not None]
if len(cc_daiin_valid) >= 10:
    cc_daiin_vals, chsh_vals = zip(*cc_daiin_valid)
    rho_cc_chsh, p_cc_chsh = stats.spearmanr(cc_daiin_vals, chsh_vals)
    print(f"\nCC_DAIIN fraction vs CHSH proportion:")
    print(f"  Spearman rho={rho_cc_chsh:.3f}, p={p_cc_chsh:.4f}, n={len(cc_daiin_valid)}")
    print(f"  Direction: {'Positive (DAIIN predicts CHSH)' if rho_cc_chsh > 0 else 'Negative (unexpected)'}")
else:
    rho_cc_chsh, p_cc_chsh = None, None
    print(f"\nInsufficient data for CC_DAIIN vs CHSH test (n={len(cc_daiin_valid)})")

# FL_HAZ fraction vs CHSH proportion (C601: CHSH participates in hazards)
fl_valid = [(folio_data[f]['fl_haz_fraction'], folio_data[f]['chsh_proportion'])
            for f in valid_folios
            if folio_data[f]['fl_haz_fraction'] is not None]
if len(fl_valid) >= 10:
    fl_haz_vals, chsh_vals_fl = zip(*fl_valid)
    rho_fl_chsh, p_fl_chsh = stats.spearmanr(fl_haz_vals, chsh_vals_fl)
    print(f"\nFL_HAZ fraction vs CHSH proportion:")
    print(f"  Spearman rho={rho_fl_chsh:.3f}, p={p_fl_chsh:.4f}, n={len(fl_valid)}")
else:
    rho_fl_chsh, p_fl_chsh = None, None
    print(f"\nInsufficient data for FL_HAZ vs CHSH test (n={len(fl_valid)})")

results['cc_qo_correlation'] = {
    'rho': round(float(rho_cc_qo), 4) if rho_cc_qo is not None else None,
    'p_value': float(p_cc_qo) if p_cc_qo is not None else None,
    'n': len(cc_valid),
    'test': 'CC_OL_D_fraction vs QO_proportion',
}
results['cc_chsh_correlation'] = {
    'rho': round(float(rho_cc_chsh), 4) if rho_cc_chsh is not None else None,
    'p_value': float(p_cc_chsh) if p_cc_chsh is not None else None,
    'n': len(cc_daiin_valid),
    'test': 'CC_DAIIN_fraction vs CHSH_proportion',
}
results['fl_chsh_correlation'] = {
    'rho': round(float(rho_fl_chsh), 4) if rho_fl_chsh is not None else None,
    'p_value': float(p_fl_chsh) if p_fl_chsh is not None else None,
    'n': len(fl_valid),
    'test': 'FL_HAZ_fraction vs CHSH_proportion',
}

# ============================================================
# SECTION 6: SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: SUMMARY")
print("=" * 70)

predictors = []

# REGIME
if results['regime_balance']['significant']:
    predictors.append(('REGIME', results['regime_balance']['cramers_v'], results['regime_balance']['p_value']))
    print(f"\n  REGIME: SIGNIFICANT (V={results['regime_balance']['cramers_v']:.3f}, p={results['regime_balance']['p_value']:.2e})")
else:
    print(f"\n  REGIME: not significant (p={results['regime_balance']['p_value']:.4f})")

# Section
if 'section_balance' in results and results['section_balance'].get('significant'):
    predictors.append(('Section', results['section_balance']['cramers_v'], results['section_balance']['p_value']))
    print(f"  Section: SIGNIFICANT (V={results['section_balance']['cramers_v']:.3f}, p={results['section_balance']['p_value']:.2e})")
elif 'section_balance' in results and 'p_value' in results['section_balance']:
    print(f"  Section: not significant (p={results['section_balance']['p_value']:.4f})")

# Position
if results['position_balance']['significant']:
    predictors.append(('Position', results['position_balance']['cramers_v'], results['position_balance']['p_value']))
    print(f"  Position: SIGNIFICANT (V={results['position_balance']['cramers_v']:.3f}, p={results['position_balance']['p_value']:.2e})")
else:
    print(f"  Position: not significant (p={results['position_balance']['p_value']:.4f})")

# CC composition
if rho_cc_qo is not None and p_cc_qo < 0.05:
    predictors.append(('CC_OL_D->QO', abs(rho_cc_qo), p_cc_qo))
    print(f"  CC_OL_D->QO: SIGNIFICANT (rho={rho_cc_qo:.3f}, p={p_cc_qo:.4f})")
elif rho_cc_qo is not None:
    print(f"  CC_OL_D->QO: not significant (rho={rho_cc_qo:.3f}, p={p_cc_qo:.4f})")

if rho_cc_chsh is not None and p_cc_chsh < 0.05:
    predictors.append(('CC_DAIIN->CHSH', abs(rho_cc_chsh), p_cc_chsh))
    print(f"  CC_DAIIN->CHSH: SIGNIFICANT (rho={rho_cc_chsh:.3f}, p={p_cc_chsh:.4f})")
elif rho_cc_chsh is not None:
    print(f"  CC_DAIIN->CHSH: not significant (rho={rho_cc_chsh:.3f}, p={p_cc_chsh:.4f})")

if rho_fl_chsh is not None and p_fl_chsh < 0.05:
    predictors.append(('FL_HAZ->CHSH', abs(rho_fl_chsh), p_fl_chsh))
    print(f"  FL_HAZ->CHSH: SIGNIFICANT (rho={rho_fl_chsh:.3f}, p={p_fl_chsh:.4f})")
elif rho_fl_chsh is not None:
    print(f"  FL_HAZ->CHSH: not significant (rho={rho_fl_chsh:.3f}, p={p_fl_chsh:.4f})")

# Rank by effect size
predictors.sort(key=lambda x: x[1], reverse=True)
print(f"\nPredictor ranking by effect size:")
for rank, (name, effect, pval) in enumerate(predictors, 1):
    print(f"  {rank}. {name}: effect={effect:.3f}, p={pval:.2e}")

if not predictors:
    print("  No significant predictors found.")

results['predictor_ranking'] = [
    {'name': name, 'effect_size': round(float(effect), 4), 'p_value': float(pval)}
    for name, effect, pval in predictors
]

# Save folio-level data for Script 2
results['folio_data'] = folio_data
results['valid_folios'] = valid_folios

# ============================================================
# SAVE
# ============================================================
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'en_subfamily_selection.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'en_subfamily_selection.json'}")
