#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANE_FUNCTIONAL_PROFILING - Script 2: Lane Oscillation Dynamics

Three tests of QO/CHSH oscillation dynamics:
4. REGIME-stratified oscillation rate (material vs execution stage)
5. Post-hazard return-to-QO timing
6. Hazard-class entropy by section

Data dependencies:
  - class_token_map.json (CLASS_COSURVIVAL_TEST)
  - en_census.json (EN_ANATOMY)
  - regime_folio_mapping.json (REGIME_SEMANTIC_INTERPRETATION)
"""

import json
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
from math import log2

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# SECTION 1: Load & Prepare
# ============================================================
print("=" * 60)
print("SECTION 1: Load & Prepare")
print("=" * 60)

# Load class token map
with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    ctm = json.load(f)

token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction
token_to_role = {}
for t, c in token_to_class.items():
    token_to_role[t] = class_to_role.get(c, 'UNKNOWN')

# Load EN census
with open(PROJECT_ROOT / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
qo_classes = set(en_census['prefix_families']['QO'])
chsh_classes = set(en_census['prefix_families']['CH_SH'])
all_en_classes = qo_classes | chsh_classes

# Load REGIME mapping
with open(PROJECT_ROOT / 'phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
folio_to_regime = {}
for regime, folios in regime_data.items():
    for f in folios:
        folio_to_regime[f] = regime

# Role constants
CC_CLASSES = {10, 11, 12, 17}
HAZ_CLASSES = {7, 30}

# Load transcript and morphology
tx = Transcript()
morph = Morphology()

# Build line-organized B token data
print("Building line-organized B token data...")
lines = defaultdict(list)

for token in tx.currier_b():
    cls = token_to_class.get(token.word)
    role = token_to_role.get(token.word, 'UNKNOWN')
    m = morph.extract(token.word)

    en_subfamily = None
    if cls is not None and cls in all_en_classes:
        if m.prefix == 'qo':
            en_subfamily = 'QO'
        elif m.prefix in ('ch', 'sh'):
            en_subfamily = 'CHSH'

    is_en = cls in all_en_classes if cls is not None else False
    is_haz = cls in HAZ_CLASSES if cls is not None else False

    lines[(token.folio, token.line)].append({
        'word': token.word,
        'class': cls,
        'role': role,
        'prefix': m.prefix,
        'middle': m.middle,
        'en_subfamily': en_subfamily,
        'is_en': is_en,
        'is_haz': is_haz,
        'section': token.section,
        'folio': token.folio,
    })

print(f"B lines: {len(lines)}")

# Build EN sequences per line (MIN_EN = 4)
MIN_EN = 4
en_line_data = []

for (folio, line_num), toks in lines.items():
    en_positions = []
    for i, t in enumerate(toks):
        if t['en_subfamily'] is not None:
            en_positions.append({
                'pos': i,
                'subfamily': t['en_subfamily'],
                'middle': t['middle'],
                'class': t['class'],
            })

    if len(en_positions) >= MIN_EN:
        en_line_data.append({
            'folio': folio,
            'line': line_num,
            'section': toks[0]['section'],
            'all_tokens': toks,
            'en_positions': en_positions,
            'en_seq': [e['subfamily'] for e in en_positions],
        })

print(f"Lines with >= {MIN_EN} EN tokens: {len(en_line_data)}")
total_en_pairs = sum(len(d['en_seq']) - 1 for d in en_line_data)
print(f"Total EN-to-EN transitions: {total_en_pairs}")


def partial_correlation(x, y, covariates):
    """Pearson partial correlation controlling for covariates."""
    if len(covariates) == 0:
        return stats.pearsonr(x, y)
    X_cov = np.column_stack(covariates)
    X_cov = np.column_stack([np.ones(len(x)), X_cov])
    beta_x = np.linalg.lstsq(X_cov, x, rcond=None)[0]
    resid_x = x - X_cov @ beta_x
    beta_y = np.linalg.lstsq(X_cov, y, rcond=None)[0]
    resid_y = y - X_cov @ beta_y
    r, p = stats.pearsonr(resid_x, resid_y)
    return r, p


def shannon_entropy(counts):
    """Shannon entropy in bits from a Counter or dict of counts."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in counts.values() if c > 0]
    return -sum(p * log2(p) for p in probs)


# ============================================================
# SECTION 2: Test 4 -- REGIME-Stratified Oscillation Rate
# ============================================================
print("\n" + "=" * 60)
print("SECTION 2: Test 4 -- REGIME-Stratified Oscillation Rate")
print("=" * 60)

# Per-folio oscillation rate
folio_osc = defaultdict(lambda: {'switches': 0, 'pairs': 0, 'section': None})

for d in en_line_data:
    folio = d['folio']
    seq = d['en_seq']
    if folio_osc[folio]['section'] is None:
        folio_osc[folio]['section'] = d['section']
    for i in range(len(seq) - 1):
        folio_osc[folio]['pairs'] += 1
        if seq[i] != seq[i + 1]:
            folio_osc[folio]['switches'] += 1

# Build folio records
MIN_PAIRS = 5
folio_records = []
for folio, data in folio_osc.items():
    if data['pairs'] < MIN_PAIRS:
        continue
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    if regime == 'UNKNOWN':
        continue
    rate = data['switches'] / data['pairs']
    folio_records.append({
        'folio': folio,
        'oscillation_rate': rate,
        'section': data['section'],
        'regime': regime,
        'n_pairs': data['pairs'],
    })

print(f"Folios with >= {MIN_PAIRS} EN pairs and known REGIME: {len(folio_records)}")

# By REGIME only
regimes = sorted(set(r['regime'] for r in folio_records))
regime_groups = {reg: [r['oscillation_rate'] for r in folio_records if r['regime'] == reg]
                 for reg in regimes}

print(f"\nBy REGIME:")
by_regime_stats = {}
for reg in regimes:
    vals = regime_groups[reg]
    by_regime_stats[reg] = {
        'mean': float(np.mean(vals)),
        'median': float(np.median(vals)),
        'std': float(np.std(vals)),
        'n': len(vals),
    }
    print(f"  {reg}: mean={np.mean(vals):.4f}, median={np.median(vals):.4f}, n={len(vals)}")

if len(regimes) >= 2:
    regime_kw = stats.kruskal(*[regime_groups[r] for r in regimes if len(regime_groups[r]) >= 2])
    regime_kruskal = {'H': float(regime_kw.statistic), 'p': float(regime_kw.pvalue)}
    print(f"  Kruskal-Wallis: H={regime_kw.statistic:.3f}, p={regime_kw.pvalue:.4f}")
else:
    regime_kruskal = {'H': None, 'p': None, 'note': 'insufficient groups'}

# By section only
sections = sorted(set(r['section'] for r in folio_records))
section_groups = {sec: [r['oscillation_rate'] for r in folio_records if r['section'] == sec]
                  for sec in sections}

print(f"\nBy section:")
by_section_stats = {}
for sec in sections:
    vals = section_groups[sec]
    by_section_stats[sec] = {
        'mean': float(np.mean(vals)),
        'median': float(np.median(vals)),
        'std': float(np.std(vals)),
        'n': len(vals),
    }
    print(f"  {sec}: mean={np.mean(vals):.4f}, median={np.median(vals):.4f}, n={len(vals)}")

testable_sections = [sec for sec in sections if len(section_groups[sec]) >= 2]
if len(testable_sections) >= 2:
    section_kw = stats.kruskal(*[section_groups[s] for s in testable_sections])
    section_kruskal = {'H': float(section_kw.statistic), 'p': float(section_kw.pvalue)}
    print(f"  Kruskal-Wallis: H={section_kw.statistic:.3f}, p={section_kw.pvalue:.4f}")
else:
    section_kruskal = {'H': None, 'p': None, 'note': 'insufficient groups'}

# Within-section REGIME effect
print(f"\nWithin-section REGIME effect:")
within_section_regime = {}
for sec in sections:
    sec_folios = [r for r in folio_records if r['section'] == sec]
    sec_regimes = sorted(set(r['regime'] for r in sec_folios))
    sec_regime_groups = {reg: [r['oscillation_rate'] for r in sec_folios if r['regime'] == reg]
                         for reg in sec_regimes}
    # Need >= 2 regimes with >= 5 folios each
    testable = {reg: vals for reg, vals in sec_regime_groups.items() if len(vals) >= 5}
    if len(testable) >= 2:
        kw = stats.kruskal(*testable.values())
        within_section_regime[sec] = {
            'H': float(kw.statistic), 'p': float(kw.pvalue),
            'n_regimes': len(testable),
            'group_sizes': {r: len(v) for r, v in testable.items()},
        }
        print(f"  {sec}: H={kw.statistic:.3f}, p={kw.pvalue:.4f}, regimes={len(testable)}")
    else:
        within_section_regime[sec] = {
            'insufficient_data': True,
            'n_regimes_testable': len(testable),
            'group_sizes': {r: len(v) for r, v in sec_regime_groups.items()},
        }
        print(f"  {sec}: insufficient data ({len(testable)} testable regimes)")

# Within-REGIME section effect
print(f"\nWithin-REGIME section effect:")
within_regime_section = {}
for reg in regimes:
    reg_folios = [r for r in folio_records if r['regime'] == reg]
    reg_sections = sorted(set(r['section'] for r in reg_folios))
    reg_section_groups = {sec: [r['oscillation_rate'] for r in reg_folios if r['section'] == sec]
                          for sec in reg_sections}
    testable = {sec: vals for sec, vals in reg_section_groups.items() if len(vals) >= 5}
    if len(testable) >= 2:
        kw = stats.kruskal(*testable.values())
        within_regime_section[reg] = {
            'H': float(kw.statistic), 'p': float(kw.pvalue),
            'n_sections': len(testable),
            'group_sizes': {s: len(v) for s, v in testable.items()},
        }
        print(f"  {reg}: H={kw.statistic:.3f}, p={kw.pvalue:.4f}, sections={len(testable)}")
    else:
        within_regime_section[reg] = {
            'insufficient_data': True,
            'n_sections_testable': len(testable),
            'group_sizes': {s: len(v) for s, v in reg_section_groups.items()},
        }
        print(f"  {reg}: insufficient data ({len(testable)} testable sections)")

# Two-way permutation test
print(f"\nTwo-way permutation test (10,000 shuffles)...")
osc_rates = np.array([r['oscillation_rate'] for r in folio_records])
folio_regimes = [r['regime'] for r in folio_records]
folio_sections = [r['section'] for r in folio_records]

def compute_ss(rates, groups):
    """Between-group sum of squares."""
    grand_mean = np.mean(rates)
    ss = 0.0
    for g in set(groups):
        idx = [i for i, x in enumerate(groups) if x == g]
        if len(idx) > 0:
            group_mean = np.mean(rates[idx])
            ss += len(idx) * (group_mean - grand_mean) ** 2
    return ss

def compute_eta2(rates, groups):
    """Eta-squared (proportion of variance explained)."""
    ss_between = compute_ss(rates, groups)
    ss_total = np.var(rates) * len(rates)
    return ss_between / ss_total if ss_total > 0 else 0.0

observed_regime_eta2 = compute_eta2(osc_rates, folio_regimes)
observed_section_eta2 = compute_eta2(osc_rates, folio_sections)

n_perms = 10000
regime_null = np.zeros(n_perms)
section_null = np.zeros(n_perms)
rng = np.random.default_rng(42)

for i in range(n_perms):
    # Shuffle regime labels within section (partial out section)
    shuffled_regimes = list(folio_regimes)
    for sec in set(folio_sections):
        sec_idx = [j for j, s in enumerate(folio_sections) if s == sec]
        sec_reg = [shuffled_regimes[j] for j in sec_idx]
        rng.shuffle(sec_reg)
        for j, idx in enumerate(sec_idx):
            shuffled_regimes[idx] = sec_reg[j]
    regime_null[i] = compute_eta2(osc_rates, shuffled_regimes)

    # Shuffle section labels within regime (partial out regime)
    shuffled_sections = list(folio_sections)
    for reg in set(folio_regimes):
        reg_idx = [j for j, r in enumerate(folio_regimes) if r == reg]
        reg_sec = [shuffled_sections[j] for j in reg_idx]
        rng.shuffle(reg_sec)
        for j, idx in enumerate(reg_idx):
            shuffled_sections[idx] = reg_sec[j]
    section_null[i] = compute_eta2(osc_rates, shuffled_sections)

regime_perm_p = float(np.mean(regime_null >= observed_regime_eta2))
section_perm_p = float(np.mean(section_null >= observed_section_eta2))

print(f"  REGIME partial eta2: {observed_regime_eta2:.4f}, perm p={regime_perm_p:.4f}")
print(f"  Section partial eta2: {observed_section_eta2:.4f}, perm p={section_perm_p:.4f}")

two_way = {
    'regime_partial_eta2': float(observed_regime_eta2),
    'regime_perm_p': regime_perm_p,
    'section_partial_eta2': float(observed_section_eta2),
    'section_perm_p': section_perm_p,
    'n_permutations': n_perms,
}

# Interpretation
if regime_perm_p < 0.05 and section_perm_p < 0.05:
    test4_interpretation = 'BOTH'
elif regime_perm_p < 0.05:
    test4_interpretation = 'REGIME_DRIVEN'
elif section_perm_p < 0.05:
    test4_interpretation = 'SECTION_DRIVEN'
else:
    test4_interpretation = 'NEITHER'

print(f"\nInterpretation: {test4_interpretation}")

test4_result = {
    'n_folios': len(folio_records),
    'by_regime': by_regime_stats,
    'by_section': by_section_stats,
    'regime_kruskal': regime_kruskal,
    'section_kruskal': section_kruskal,
    'within_section_regime_effect': within_section_regime,
    'within_regime_section_effect': within_regime_section,
    'two_way': two_way,
    'interpretation': test4_interpretation,
}


# ============================================================
# SECTION 3: Test 5 -- Post-Hazard Return-to-QO Timing
# ============================================================
print("\n" + "=" * 60)
print("SECTION 3: Test 5 -- Post-Hazard Return-to-QO Timing")
print("=" * 60)

recovery_sequences = []

for (folio, line_num), toks in lines.items():
    for i, t in enumerate(toks):
        if not t['is_haz']:
            continue

        # Find subsequent EN tokens in same line
        subsequent_en = []
        for j in range(i + 1, len(toks)):
            if toks[j]['en_subfamily'] is not None:
                subsequent_en.append({
                    'pos': j,
                    'lane': toks[j]['en_subfamily'],
                    'distance': j - i,
                })

        if not subsequent_en:
            continue

        first_en_lane = subsequent_en[0]['lane']
        chsh_before_qo = 0
        found_qo = False
        for en in subsequent_en:
            if en['lane'] == 'QO':
                found_qo = True
                break
            chsh_before_qo += 1

        section = toks[0]['section']
        regime = folio_to_regime.get(folio, 'UNKNOWN')

        recovery_sequences.append({
            'folio': folio,
            'haz_class': t['class'],
            'first_en': first_en_lane,
            'chsh_before_qo': chsh_before_qo if found_qo else None,
            'found_qo': found_qo,
            'n_subsequent': len(subsequent_en),
            'section': section,
            'regime': regime,
        })

print(f"Hazard events with subsequent EN: {len(recovery_sequences)}")

# First EN after hazard
first_en_qo = sum(1 for r in recovery_sequences if r['first_en'] == 'QO')
first_en_chsh = sum(1 for r in recovery_sequences if r['first_en'] == 'CHSH')
total_first = first_en_qo + first_en_chsh

# Base QO rate
base_qo_total = sum(1 for (f, l), toks in lines.items() for t in toks if t['en_subfamily'] == 'QO')
base_total = sum(1 for (f, l), toks in lines.items() for t in toks if t['en_subfamily'] is not None)
base_qo_rate = base_qo_total / base_total if base_total > 0 else 0.5

chsh_rate_post_haz = first_en_chsh / total_first if total_first > 0 else 0
binom_p = stats.binomtest(first_en_qo, total_first, base_qo_rate).pvalue if total_first > 0 else None

print(f"\nFirst EN after hazard:")
print(f"  QO: {first_en_qo} ({100*first_en_qo/total_first:.1f}%)")
print(f"  CHSH: {first_en_chsh} ({100*chsh_rate_post_haz:.1f}%)")
print(f"  Base QO rate: {base_qo_rate:.4f}")
print(f"  Binomial p: {binom_p:.6f}" if binom_p else "  No data")
c645_match = chsh_rate_post_haz > 0.70  # C645: 75.2%
print(f"  C645 match (CHSH > 70%): {c645_match}")

# CHSH-before-QO distribution
found_qo_seqs = [r for r in recovery_sequences if r['found_qo']]
censored_seqs = [r for r in recovery_sequences if not r['found_qo']]
print(f"\nRecovery sequences: {len(found_qo_seqs)} found QO, {len(censored_seqs)} censored")

chsh_counts = [r['chsh_before_qo'] for r in found_qo_seqs]
if chsh_counts:
    distribution = Counter(chsh_counts)
    print(f"  CHSH before QO: mean={np.mean(chsh_counts):.2f}, median={np.median(chsh_counts):.1f}")
    print(f"  Distribution: {dict(sorted(distribution.items()))}")
    chsh_before_qo_stats = {
        'n_with_qo_found': len(found_qo_seqs),
        'n_censored': len(censored_seqs),
        'mean': float(np.mean(chsh_counts)),
        'median': float(np.median(chsh_counts)),
        'std': float(np.std(chsh_counts)),
        'distribution': {str(k): v for k, v in sorted(distribution.items())},
    }
else:
    chsh_before_qo_stats = {'n_with_qo_found': 0, 'n_censored': len(censored_seqs)}

# By section
print(f"\nBy section:")
recovery_sections = sorted(set(r['section'] for r in found_qo_seqs))
by_section_recovery = {}
section_timing_groups = {}
for sec in recovery_sections:
    sec_seqs = [r['chsh_before_qo'] for r in found_qo_seqs if r['section'] == sec]
    if sec_seqs:
        by_section_recovery[sec] = {
            'mean_chsh_before_qo': float(np.mean(sec_seqs)),
            'median': float(np.median(sec_seqs)),
            'n': len(sec_seqs),
        }
        section_timing_groups[sec] = sec_seqs
        print(f"  {sec}: mean={np.mean(sec_seqs):.2f}, median={np.median(sec_seqs):.1f}, n={len(sec_seqs)}")

testable_sec = {s: v for s, v in section_timing_groups.items() if len(v) >= 5}
if len(testable_sec) >= 2:
    sec_kw = stats.kruskal(*testable_sec.values())
    section_recovery_kruskal = {'H': float(sec_kw.statistic), 'p': float(sec_kw.pvalue)}
    print(f"  Kruskal-Wallis: H={sec_kw.statistic:.3f}, p={sec_kw.pvalue:.4f}")
else:
    section_recovery_kruskal = {'H': None, 'p': None, 'note': 'insufficient groups'}

# By REGIME
print(f"\nBy REGIME:")
recovery_regimes = sorted(set(r['regime'] for r in found_qo_seqs if r['regime'] != 'UNKNOWN'))
by_regime_recovery = {}
regime_timing_groups = {}
for reg in recovery_regimes:
    reg_seqs = [r['chsh_before_qo'] for r in found_qo_seqs if r['regime'] == reg]
    if reg_seqs:
        by_regime_recovery[reg] = {
            'mean_chsh_before_qo': float(np.mean(reg_seqs)),
            'median': float(np.median(reg_seqs)),
            'n': len(reg_seqs),
        }
        regime_timing_groups[reg] = reg_seqs
        print(f"  {reg}: mean={np.mean(reg_seqs):.2f}, median={np.median(reg_seqs):.1f}, n={len(reg_seqs)}")

testable_reg = {r: v for r, v in regime_timing_groups.items() if len(v) >= 5}
if len(testable_reg) >= 2:
    reg_kw = stats.kruskal(*testable_reg.values())
    regime_recovery_kruskal = {'H': float(reg_kw.statistic), 'p': float(reg_kw.pvalue)}
    print(f"  Kruskal-Wallis: H={reg_kw.statistic:.3f}, p={reg_kw.pvalue:.4f}")
else:
    regime_recovery_kruskal = {'H': None, 'p': None, 'note': 'insufficient groups'}

# By hazard class
print(f"\nBy hazard class:")
by_haz_class = {}
haz_class_groups = {}
for hc in sorted(HAZ_CLASSES):
    hc_seqs = [r['chsh_before_qo'] for r in found_qo_seqs if r['haz_class'] == hc]
    if hc_seqs:
        by_haz_class[str(hc)] = {
            'mean': float(np.mean(hc_seqs)),
            'median': float(np.median(hc_seqs)),
            'n': len(hc_seqs),
        }
        haz_class_groups[hc] = hc_seqs
        print(f"  Class {hc}: mean={np.mean(hc_seqs):.2f}, n={len(hc_seqs)}")

if len(haz_class_groups) == 2 and all(len(v) >= 10 for v in haz_class_groups.values()):
    groups = list(haz_class_groups.values())
    mw = stats.mannwhitneyu(groups[0], groups[1], alternative='two-sided')
    haz_class_mw = {'U': float(mw.statistic), 'p': float(mw.pvalue)}
    print(f"  Mann-Whitney: U={mw.statistic:.1f}, p={mw.pvalue:.4f}")
else:
    haz_class_mw = {'U': None, 'p': None, 'note': 'insufficient data for comparison'}

# Interpretation
if total_first < 20:
    test5_interpretation = 'INSUFFICIENT_DATA'
elif section_recovery_kruskal.get('p') is not None and section_recovery_kruskal['p'] < 0.05:
    test5_interpretation = 'SECTION_DEPENDENT'
elif regime_recovery_kruskal.get('p') is not None and regime_recovery_kruskal['p'] < 0.05:
    test5_interpretation = 'REGIME_DEPENDENT'
else:
    mean_chsh = np.mean(chsh_counts) if chsh_counts else 0
    if mean_chsh > 2:
        test5_interpretation = 'SLOW_RECOVERY'
    else:
        test5_interpretation = 'FAST_RECOVERY'

print(f"\nInterpretation: {test5_interpretation}")

test5_result = {
    'n_hazard_events': len(recovery_sequences),
    'first_en_after_hazard': {
        'QO': first_en_qo,
        'CHSH': first_en_chsh,
        'chsh_rate': chsh_rate_post_haz,
        'base_qo_rate': base_qo_rate,
        'binom_p_vs_base': float(binom_p) if binom_p is not None else None,
        'c645_match': c645_match,
    },
    'chsh_before_qo': chsh_before_qo_stats,
    'by_section': by_section_recovery,
    'section_kruskal': section_recovery_kruskal,
    'by_regime': by_regime_recovery,
    'regime_kruskal': regime_recovery_kruskal,
    'by_hazard_class': by_haz_class,
    'hazard_class_mw': haz_class_mw,
    'interpretation': test5_interpretation,
}


# ============================================================
# SECTION 4: Test 6 -- Hazard-Class Entropy by Section
# ============================================================
print("\n" + "=" * 60)
print("SECTION 4: Test 6 -- Hazard-Class Entropy by Section")
print("=" * 60)

# Per-section hazard entropy
section_haz_counts = defaultdict(Counter)
for (folio, line_num), toks in lines.items():
    sec = toks[0]['section'] if toks else None
    if sec is None:
        continue
    for t in toks:
        if t['is_haz'] and t['class'] is not None:
            section_haz_counts[sec][t['class']] += 1

section_entropy_data = []
for sec in sorted(section_haz_counts.keys()):
    counts = section_haz_counts[sec]
    ent = shannon_entropy(counts)
    total_haz = sum(counts.values())
    section_entropy_data.append({
        'section': sec,
        'entropy': ent,
        'n_hazards': total_haz,
        'class_distribution': {str(k): v for k, v in sorted(counts.items())},
    })
    print(f"  {sec}: entropy={ent:.4f}, n_hazards={total_haz}, classes={dict(counts)}")

# Section-level oscillation rate (from en_line_data)
section_osc = defaultdict(lambda: {'switches': 0, 'pairs': 0})
for d in en_line_data:
    sec = d['section']
    seq = d['en_seq']
    for i in range(len(seq) - 1):
        section_osc[sec]['pairs'] += 1
        if seq[i] != seq[i + 1]:
            section_osc[sec]['switches'] += 1

section_osc_rate = {sec: d['switches'] / d['pairs'] if d['pairs'] > 0 else 0
                    for sec, d in section_osc.items()}

for sd in section_entropy_data:
    sd['oscillation_rate'] = section_osc_rate.get(sd['section'], 0)

# Section-level correlation (descriptive, N is small)
sec_entropies = np.array([sd['entropy'] for sd in section_entropy_data])
sec_osc_rates = np.array([sd['oscillation_rate'] for sd in section_entropy_data])

if len(section_entropy_data) >= 3:
    sec_rho, sec_p = stats.spearmanr(sec_entropies, sec_osc_rates)
    print(f"\nSection-level Spearman: rho={sec_rho:.4f}, p={sec_p:.4f}, n={len(section_entropy_data)}")
    section_level = {
        'spearman_rho': float(sec_rho),
        'p': float(sec_p),
        'n': len(section_entropy_data),
        'data': section_entropy_data,
    }
else:
    section_level = {'n': len(section_entropy_data), 'note': 'too few sections for correlation'}

# Per-folio hazard entropy and oscillation rate
folio_haz_counts = defaultdict(Counter)
for (folio, line_num), toks in lines.items():
    for t in toks:
        if t['is_haz'] and t['class'] is not None:
            folio_haz_counts[folio][t['class']] += 1

# Merge with folio oscillation data
folio_entropy_records = []
for folio, data in folio_osc.items():
    if data['pairs'] < MIN_PAIRS:
        continue
    haz_counts = folio_haz_counts.get(folio, Counter())
    if sum(haz_counts.values()) == 0:
        continue  # No hazard tokens in this folio
    ent = shannon_entropy(haz_counts)
    rate = data['switches'] / data['pairs']
    regime = folio_to_regime.get(folio, 'UNKNOWN')
    section = data['section']
    folio_entropy_records.append({
        'folio': folio,
        'entropy': ent,
        'oscillation_rate': rate,
        'n_hazards': sum(haz_counts.values()),
        'section': section,
        'regime': regime,
    })

print(f"\nFolios with hazard tokens and >= {MIN_PAIRS} EN pairs: {len(folio_entropy_records)}")

folio_ent = np.array([r['entropy'] for r in folio_entropy_records])
folio_osc_r = np.array([r['oscillation_rate'] for r in folio_entropy_records])

if len(folio_entropy_records) >= 10:
    folio_rho, folio_p = stats.spearmanr(folio_ent, folio_osc_r)
    print(f"Folio-level Spearman: rho={folio_rho:.4f}, p={folio_p:.4f}, n={len(folio_entropy_records)}")

    # Partial correlation controlling section + REGIME
    folio_sections_unique = sorted(set(r['section'] for r in folio_entropy_records))
    folio_regimes_unique = sorted(set(r['regime'] for r in folio_entropy_records
                                      if r['regime'] != 'UNKNOWN'))

    covariates = []
    for s in folio_sections_unique[1:]:
        covariates.append(np.array([1 if r['section'] == s else 0
                                    for r in folio_entropy_records], dtype=float))
    for reg in folio_regimes_unique[1:]:
        covariates.append(np.array([1 if r['regime'] == reg else 0
                                    for r in folio_entropy_records], dtype=float))

    if covariates:
        partial_r, partial_p = partial_correlation(folio_ent, folio_osc_r, covariates)
        print(f"Partial correlation: r={partial_r:.4f}, p={partial_p:.4f}")
    else:
        partial_r, partial_p = folio_rho, folio_p

    folio_level = {
        'n_folios': len(folio_entropy_records),
        'spearman_rho': float(folio_rho),
        'p': float(folio_p),
        'partial_r': float(partial_r),
        'partial_p': float(partial_p),
        'controlling': ['section', 'regime'],
    }
else:
    folio_level = {'n_folios': len(folio_entropy_records),
                   'note': 'insufficient folios for correlation'}

# Interpretation
if 'spearman_rho' in folio_level:
    if folio_level['p'] < 0.05:
        test6_interpretation = 'ENTROPY_PREDICTS_OSCILLATION'
    else:
        test6_interpretation = 'NO_ASSOCIATION'
else:
    test6_interpretation = 'INSUFFICIENT_DATA'

print(f"\nInterpretation: {test6_interpretation}")

test6_result = {
    'section_level': section_level,
    'folio_level': folio_level,
    'interpretation': test6_interpretation,
}


# ============================================================
# SECTION 5: Summary
# ============================================================
print("\n" + "=" * 60)
print("SECTION 5: Summary")
print("=" * 60)

results = {
    'test4_regime_oscillation': test4_result,
    'test5_post_hazard_recovery': test5_result,
    'test6_hazard_entropy': test6_result,
    'summary': {
        'test4': test4_interpretation,
        'test5': test5_interpretation,
        'test6': test6_interpretation,
    }
}

print(f"\nTest 4 (REGIME oscillation):    {test4_interpretation}")
print(f"Test 5 (Post-hazard recovery):  {test5_interpretation}")
print(f"Test 6 (Hazard entropy):        {test6_interpretation}")

# Save results
output_path = RESULTS_DIR / 'lane_oscillation_dynamics.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {output_path}")
