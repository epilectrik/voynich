#!/usr/bin/env python3
"""
Phase 384: Galenic Parallel Tests -- 5-test battery

Tests whether the Galenic intellectual framework (4-element theory,
humoral dynamics, degree system) left structural fingerprints in the
Voynich control architecture. These are derived from the expert-validated
observation that the manuscript was authored by a humorally-trained
practitioner encoding distillation procedures.

Tests:
  T1: Class-Specific vs Generic Recovery (revised from oppositional correction)
  T2: Degree-4 Universality (rare MIDDLEs hazard-adjacent across PREFIX channels)
  T3: Illustration Residual (external metadata predicting AXM residual)
  T4: Kernel Triad as Elemental Grammar (k/h/e directional asymmetry)
  T5: Concoction Duration (paragraph length vs PP complexity scaling)

Grounding constraints:
  C109 (5 hazard classes), C521 (kernel directional asymmetry),
  C541 (6/49 hazard-involved classes), C601 (QO hazard exclusion),
  C645 (CHSH post-hazard dominance), C858 (paragraph-complexity correlation),
  C883/C884 (illustration-handling correlation), C997 (safety buffers),
  C1035 (AXM residual irreducible to internal predictors)
"""

import sys
import json
import csv
import math
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, BFolioDecoder, MiddleAnalyzer,
                              BTokenAnalysis)

RESULTS = ROOT / "phases" / "GALENIC_PARALLEL_TESTS" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# C109: 17 forbidden transitions (Tier 0, FROZEN)
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]

# Build lookup structures
FORBIDDEN_SET = set()
for a, b in FORBIDDEN_TRANSITIONS:
    FORBIDDEN_SET.add((a, b))

HAZARD_SOURCES = set(a for a, b in FORBIDDEN_TRANSITIONS)
HAZARD_TARGETS = set(b for a, b in FORBIDDEN_TRANSITIONS)
HAZARD_WORDS = HAZARD_SOURCES | HAZARD_TARGETS

# C109: Hazard class assignments for each forbidden pair
HAZARD_CLASSES = {
    ('shey', 'aiin'): 'PHASE_ORDERING',
    ('shey', 'al'): 'PHASE_ORDERING',
    ('shey', 'c'): 'PHASE_ORDERING',
    ('chol', 'r'): 'PHASE_ORDERING',
    ('dy', 'chey'): 'PHASE_ORDERING',
    ('chey', 'chedy'): 'PHASE_ORDERING',
    ('chey', 'shedy'): 'PHASE_ORDERING',
    ('chedy', 'ee'): 'COMPOSITION_JUMP',
    ('dy', 'aiin'): 'COMPOSITION_JUMP',
    ('c', 'ee'): 'COMPOSITION_JUMP',
    ('shedy', 'aiin'): 'COMPOSITION_JUMP',
    ('l', 'chol'): 'CONTAINMENT_TIMING',
    ('ar', 'dal'): 'CONTAINMENT_TIMING',
    ('he', 't'): 'CONTAINMENT_TIMING',
    ('shedy', 'o'): 'CONTAINMENT_TIMING',
    ('or', 'dal'): 'RATE_MISMATCH',
    ('he', 'or'): 'ENERGY_OVERSHOOT',
}

# ===================================================================
# Initialize analysis infrastructure
# ===================================================================
print("=" * 70)
print("PHASE 384: GALENIC PARALLEL TESTS")
print("=" * 70)
print()

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Build token sequence per folio (Currier B only, body tokens)
folio_tokens = defaultdict(list)  # folio -> [(word, token_obj, analysis)]
all_b_tokens = []

for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue
    folio_tokens[tok.folio].append(tok)
    all_b_tokens.append(tok)

print(f"Loaded {len(all_b_tokens)} Currier B tokens across {len(folio_tokens)} folios")
print()

# Load regime assignments
regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# ===================================================================
# TEST 1: CLASS-SPECIFIC VS GENERIC RECOVERY
# ===================================================================
# After a hazard-adjacent transition, does recovery depend on the
# hazard CLASS (Galenic prediction: specific correction for each
# imbalance type) or is it generic (CHSH always dominates)?
#
# Expert revision: Use broader hazard-adjacent population.
# Frame as: class-specific vs generic post-hazard lane profile.
# ===================================================================
print("-" * 70)
print("TEST 1: Class-Specific vs Generic Recovery")
print("  Galenic prediction: recovery is hazard-class-specific")
print("  Null: all hazard classes produce identical CHSH-dominant recovery")
print("-" * 70)
print()

# Build token sequences per folio and find hazard-source contexts
# Hazard SOURCES are tokens that participate as the first element
# of a forbidden transition. When we see a source token, we record
# the hazard class(es) it participates in and the lane of the next
# 1-3 tokens (the "recovery" context).
#
# This uses the broader hazard-adjacent population per expert revision.

# Map each hazard source word to its hazard class(es)
source_to_classes = defaultdict(set)
for (a, b), hclass in HAZARD_CLASSES.items():
    source_to_classes[a].add(hclass)

t1_results = defaultdict(lambda: Counter())  # hazard_class -> Counter(lane)
t1_baseline = Counter()  # overall lane distribution
t1_source_events = defaultdict(int)  # count events per class

for folio, tokens in folio_tokens.items():
    words = [t.word for t in tokens]

    # Record baseline lane distribution
    for w in words:
        m = morph.extract(w)
        if m.prefix:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            t1_baseline[lane] += 1

    # Find hazard-source tokens and record recovery context
    for i, w in enumerate(words):
        if w in source_to_classes:
            for hclass in source_to_classes[w]:
                t1_source_events[hclass] += 1
                # Record lanes of next 1-3 tokens
                for j in range(i + 1, min(i + 4, len(words))):
                    m_rec = morph.extract(words[j])
                    if m_rec.prefix:
                        lane_rec = BTokenAnalysis._get_prefix_lane(m_rec.prefix)
                        t1_results[hclass][lane_rec] += 1

# Aggregate into QO vs CHSH for comparison
t1_data = {}
print("Post-hazard lane profiles by hazard class:")
print(f"  {'Class':<22} {'QO':>5} {'CHSH':>5} {'Other':>6} {'CHSH%':>7} {'N':>4}")
print(f"  {'-'*22} {'-'*5} {'-'*5} {'-'*6} {'-'*7} {'-'*4}")

for hclass in ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING',
               'RATE_MISMATCH', 'ENERGY_OVERSHOOT']:
    counts = t1_results[hclass]
    qo = counts.get('QO', 0)
    chsh = counts.get('CHSH', 0)
    other = sum(v for k, v in counts.items() if k not in ('QO', 'CHSH'))
    total = qo + chsh + other
    chsh_pct = 100 * chsh / total if total > 0 else 0
    print(f"  {hclass:<22} {qo:>5} {chsh:>5} {other:>6} {chsh_pct:>6.1f}% {total:>4}")
    t1_data[hclass] = {'QO': qo, 'CHSH': chsh, 'other': other, 'total': total,
                       'chsh_pct': chsh_pct}

# Baseline
base_qo = t1_baseline.get('QO', 0)
base_chsh = t1_baseline.get('CHSH', 0)
base_other = sum(v for k, v in t1_baseline.items() if k not in ('QO', 'CHSH'))
base_total = base_qo + base_chsh + base_other
base_chsh_pct = 100 * base_chsh / base_total if base_total > 0 else 0
print(f"  {'BASELINE':<22} {base_qo:>5} {base_chsh:>5} {base_other:>6} {base_chsh_pct:>6.1f}% {base_total:>4}")
print()

# Chi-square test: do hazard classes differ in recovery lane profile?
# Build contingency table: rows = hazard classes, cols = QO/CHSH/other
contingency = []
class_labels = []
for hclass in ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'CONTAINMENT_TIMING',
               'RATE_MISMATCH', 'ENERGY_OVERSHOOT']:
    counts = t1_results[hclass]
    qo = counts.get('QO', 0)
    chsh = counts.get('CHSH', 0)
    other = sum(v for k, v in counts.items() if k not in ('QO', 'CHSH'))
    if qo + chsh + other > 0:
        contingency.append([qo, chsh, other])
        class_labels.append(hclass)

if len(contingency) >= 2:
    ct = np.array(contingency)
    # Remove zero-sum columns
    col_sums = ct.sum(axis=0)
    valid_cols = col_sums > 0
    ct_valid = ct[:, valid_cols]

    if ct_valid.shape[1] >= 2:
        chi2, p_val, dof, expected = sp_stats.chi2_contingency(ct_valid)
        print(f"Chi-square test (hazard class x recovery lane):")
        print(f"  chi2 = {chi2:.3f}, dof = {dof}, p = {p_val:.4f}")
        if p_val < 0.05:
            print(f"  -> SIGNIFICANT: Recovery IS class-specific (GALENIC prediction SUPPORTED)")
            t1_verdict = "PASS"
        else:
            print(f"  -> NOT SIGNIFICANT: Recovery is GENERIC (Galenic prediction NOT supported)")
            t1_verdict = "FAIL"
    else:
        print("  Insufficient column variation for chi-square")
        t1_verdict = "UNDERPOWERED"
else:
    print("  Insufficient hazard classes with data for comparison")
    t1_verdict = "UNDERPOWERED"

# Also: overall CHSH enrichment vs baseline (replicating C645)
all_post = sum(d['total'] for d in t1_data.values())
all_chsh = sum(d['CHSH'] for d in t1_data.values())
if all_post > 0:
    overall_chsh_pct = 100 * all_chsh / all_post
    enrichment = overall_chsh_pct / base_chsh_pct if base_chsh_pct > 0 else 0
    print(f"\nOverall post-hazard CHSH: {overall_chsh_pct:.1f}% (baseline: {base_chsh_pct:.1f}%)")
    print(f"  CHSH enrichment: {enrichment:.2f}x (C645 reports: 1.36x)")
    # Fisher exact on QO vs CHSH aggregate
    table_2x2 = np.array([
        [all_chsh, sum(d['QO'] for d in t1_data.values())],
        [base_chsh, base_qo]
    ])
    odds, pval_fisher = sp_stats.fisher_exact(table_2x2)
    print(f"  Fisher exact (CHSH enrichment): p = {pval_fisher:.4f}")

print(f"\nT1 VERDICT: {t1_verdict}")
print()

# ===================================================================
# TEST 2: DEGREE-4 UNIVERSALITY
# ===================================================================
# Galenic Degree 4: universally dangerous regardless of quality.
# Prediction: rarest MIDDLEs in ALL PREFIX channels are hazard-adjacent.
# Counter-prediction (C601): hazard is channel-specific, not universal.
# ===================================================================
print("-" * 70)
print("TEST 2: Degree-4 Universality")
print("  Galenic prediction: rare MIDDLEs are hazard-adjacent in ALL channels")
print("  Null (C601): hazard adjacency is channel-specific (QO=zero)")
print("-" * 70)
print()

# Build per-PREFIX-channel MIDDLE frequency and hazard adjacency
prefix_middle_freq = defaultdict(Counter)  # lane -> Counter(middle)
middle_hazard_adjacency = defaultdict(float)  # middle -> hazard adjacency score

for folio, tokens in folio_tokens.items():
    words = [t.word for t in tokens]

    # Per-token: record prefix lane and MIDDLE
    for w in words:
        m = morph.extract(w)
        if m.prefix and m.middle:
            lane = BTokenAnalysis._get_prefix_lane(m.prefix)
            prefix_middle_freq[lane][m.middle] += 1

    # Hazard adjacency: for each token within 2 positions of a hazard word,
    # increment its hazard adjacency score
    for i, w in enumerate(words):
        if w in HAZARD_WORDS:
            # Mark neighbors
            for j in range(max(0, i - 2), min(len(words), i + 3)):
                if j != i:
                    m_adj = morph.extract(words[j])
                    if m_adj.middle:
                        middle_hazard_adjacency[m_adj.middle] += 1

# Normalize adjacency by total MIDDLE occurrences
middle_total_count = Counter()
for lane_counts in prefix_middle_freq.values():
    for mid, cnt in lane_counts.items():
        middle_total_count[mid] += cnt

middle_hazard_rate = {}
for mid, adj_count in middle_hazard_adjacency.items():
    if middle_total_count[mid] > 0:
        middle_hazard_rate[mid] = adj_count / middle_total_count[mid]

# For each major lane (QO, CHSH), compute rank-hazard correlation
t2_data = {}
print(f"Per-channel rarity vs hazard adjacency:")
print(f"  {'Channel':<10} {'N_MIDDLEs':>10} {'Spearman_rho':>13} {'p-value':>10} {'Direction':>12}")
print(f"  {'-'*10} {'-'*10} {'-'*13} {'-'*10} {'-'*12}")

for lane in ['QO', 'CHSH', 'PREP', 'SETUP', 'CLOSE', 'LINK']:
    middles = prefix_middle_freq[lane]
    if len(middles) < 5:
        continue

    # Build paired vectors: frequency rank (1=most common) and hazard rate
    mid_list = list(middles.keys())
    frequencies = [middles[m] for m in mid_list]
    haz_rates = [middle_hazard_rate.get(m, 0) for m in mid_list]

    # Only include MIDDLEs that have any hazard adjacency somewhere in the corpus
    if sum(1 for h in haz_rates if h > 0) < 3:
        print(f"  {lane:<10} {len(mid_list):>10} {'--':>13} {'--':>10} {'NO_HAZ_DATA':>12}")
        t2_data[lane] = {'n': len(mid_list), 'rho': None, 'p': None, 'direction': 'NO_HAZ_DATA'}
        continue

    # Spearman: is frequency rank correlated with hazard rate?
    # Negative rho = rarer MIDDLEs have HIGHER hazard rate (supports Galenic)
    rho, p = sp_stats.spearmanr(frequencies, haz_rates)
    direction = "RARE=DANGER" if rho < 0 else "COMMON=DANGER"
    print(f"  {lane:<10} {len(mid_list):>10} {rho:>13.3f} {p:>10.4f} {direction:>12}")
    t2_data[lane] = {'n': len(mid_list), 'rho': float(rho), 'p': float(p), 'direction': direction}

# Test the Galenic prediction: rho < 0 in ALL channels
print()
channels_with_data = {k: v for k, v in t2_data.items() if v.get('rho') is not None}
rare_danger_count = sum(1 for v in channels_with_data.values() if v['rho'] < 0)
total_channels = len(channels_with_data)

if total_channels > 0:
    print(f"Channels where rare = more hazard-adjacent: {rare_danger_count}/{total_channels}")
    qo_result = t2_data.get('QO', {})
    chsh_result = t2_data.get('CHSH', {})

    # Key test: does QO show the pattern? (C601 predicts NO)
    if qo_result.get('rho') is not None:
        if qo_result['rho'] < 0 and qo_result['p'] < 0.05:
            print(f"  QO channel: RARE=DANGER (rho={qo_result['rho']:.3f}, p={qo_result['p']:.4f})")
            print(f"  -> GALENIC: universality SUPPORTED in QO")
        else:
            print(f"  QO channel: rho={qo_result['rho']:.3f}, p={qo_result['p']:.4f}")
            print(f"  -> C601: QO does NOT show universal degree-4 pattern")

    if rare_danger_count == total_channels:
        t2_verdict = "PASS_UNIVERSAL"
        print(f"\n  -> PASS: All channels show rare=danger (Galenic Degree-4 universality)")
    elif rare_danger_count > total_channels / 2:
        t2_verdict = "PARTIAL"
        print(f"\n  -> PARTIAL: Majority of channels show rare=danger but not universal")
    else:
        t2_verdict = "FAIL"
        print(f"\n  -> FAIL: Rare=danger is NOT universal. Hazard is channel-specific.")
else:
    t2_verdict = "UNDERPOWERED"
    print("  Insufficient data across channels")

print(f"\nT2 VERDICT: {t2_verdict}")
print()


# ===================================================================
# TEST 3: ILLUSTRATION RESIDUAL (AXM external metadata)
# ===================================================================
# C1035 tested 6 internal structural predictors for the 57% AXM
# residual -- all failed. This tests EXTERNAL metadata: does the
# section (herbal/bio/stars) or illustration type predict AXM
# self-transition rate?
#
# Framing: C138 says illustrations don't constrain grammar.
# But section is external metadata about subject matter, not an
# illustration feature. C883 opens this door.
# ===================================================================
print("-" * 70)
print("TEST 3: Illustration Residual (Section as External Predictor)")
print("  Hypothesis: section (H/B/S/C/T) predicts AXM self-transition rate")
print("  Null (C1035): residual is genuinely program-specific free variation")
print("-" * 70)
print()

# Compute AXM self-transition rate per folio
folio_axm_self = {}
for folio, tokens in folio_tokens.items():
    words = [t.word for t in tokens]
    # Get macro states
    states = []
    for w in words:
        tc = decoder._token_to_class.get(w)
        if tc is not None:
            ms = decoder.MACRO_STATE.get(str(tc))
            if ms:
                states.append(ms)

    # Count AXM self-transitions
    axm_transitions = 0
    axm_self = 0
    for i in range(len(states) - 1):
        if states[i] == 'AXM':
            axm_transitions += 1
            if states[i + 1] == 'AXM':
                axm_self += 1

    if axm_transitions >= 5:  # minimum for reliable rate
        folio_axm_self[folio] = axm_self / axm_transitions

# Get section per folio
folio_section = {}
for tok in all_b_tokens:
    if tok.folio not in folio_section:
        folio_section[tok.folio] = tok.section

# Group AXM rates by section
section_axm = defaultdict(list)
for folio, rate in folio_axm_self.items():
    sec = folio_section.get(folio, 'X')
    section_axm[sec].append(rate)

print("AXM self-transition rate by section:")
print(f"  {'Section':<10} {'N':>4} {'Mean':>8} {'SD':>8} {'Min':>8} {'Max':>8}")
print(f"  {'-'*10} {'-'*4} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

t3_data = {}
for sec in sorted(section_axm.keys()):
    rates = section_axm[sec]
    n = len(rates)
    mean = np.mean(rates)
    sd = np.std(rates, ddof=1) if n > 1 else 0
    print(f"  {sec:<10} {n:>4} {mean:>8.4f} {sd:>8.4f} {min(rates):>8.4f} {max(rates):>8.4f}")
    t3_data[sec] = {'n': n, 'mean': float(mean), 'sd': float(sd),
                    'rates': [float(r) for r in rates]}

# Kruskal-Wallis test: does section predict AXM rate?
groups = [section_axm[s] for s in sorted(section_axm.keys()) if len(section_axm[s]) >= 3]
if len(groups) >= 2:
    kw_stat, kw_p = sp_stats.kruskal(*groups)
    print(f"\nKruskal-Wallis test (section -> AXM rate):")
    print(f"  H = {kw_stat:.3f}, p = {kw_p:.4f}")

    if kw_p < 0.05:
        print(f"  -> SIGNIFICANT: Section DOES predict AXM self-transition rate")
        t3_verdict = "PASS"

        # Effect size: eta-squared
        all_rates = [r for rates in groups for r in rates]
        ss_total = sum((r - np.mean(all_rates))**2 for r in all_rates)
        ss_between = sum(len(g) * (np.mean(g) - np.mean(all_rates))**2 for g in groups)
        eta2 = ss_between / ss_total if ss_total > 0 else 0
        print(f"  eta-squared = {eta2:.4f} (proportion of variance explained)")

        # Pairwise comparisons
        secs = sorted([s for s in section_axm.keys() if len(section_axm[s]) >= 3])
        print(f"\n  Pairwise Mann-Whitney tests:")
        for i in range(len(secs)):
            for j in range(i + 1, len(secs)):
                u_stat, u_p = sp_stats.mannwhitneyu(
                    section_axm[secs[i]], section_axm[secs[j]], alternative='two-sided')
                sig = "*" if u_p < 0.05 else ""
                print(f"    {secs[i]} vs {secs[j]}: U={u_stat:.0f}, p={u_p:.4f} {sig}")
    else:
        print(f"  -> NOT SIGNIFICANT: Section does NOT predict AXM rate")
        print(f"  -> Extends C1035: external metadata also fails to explain residual")
        t3_verdict = "FAIL"
else:
    print("  Insufficient sections with data for comparison")
    t3_verdict = "UNDERPOWERED"

# Also: REGIME-controlled analysis (is section significant AFTER controlling for REGIME?)
print(f"\nREGIME-controlled analysis:")
regime_section_axm = defaultdict(lambda: defaultdict(list))
for folio, rate in folio_axm_self.items():
    sec = folio_section.get(folio, 'X')
    reg = folio_regime.get(folio, 'X')
    regime_section_axm[reg][sec].append(rate)

for reg in sorted(regime_section_axm.keys()):
    by_sec = regime_section_axm[reg]
    secs_with_data = {s: r for s, r in by_sec.items() if len(r) >= 2}
    if len(secs_with_data) >= 2:
        print(f"  {reg}: ", end="")
        for s in sorted(secs_with_data.keys()):
            print(f"{s}(n={len(secs_with_data[s])}, mean={np.mean(secs_with_data[s]):.3f}) ", end="")
        print()

print(f"\nT3 VERDICT: {t3_verdict}")
print()


# ===================================================================
# TEST 4: KERNEL TRIAD AS ELEMENTAL GRAMMAR
# ===================================================================
# C521: k->h->e directional asymmetry with e as absorbing boundary.
# Galenic prediction: the quantitative ratios match elemental ordering
# (fire > air/water > earth in activity). If k=fire, h=air/water,
# e=earth, then:
#   - Transitions toward e should be IRREVERSIBLE (absorbing)
#   - k->h should be easier than h->k (fire dominates)
#   - The ratios should show a MONOTONIC potency gradient
#
# C521 reports: e->h=0.00, h->k=0.22, e->k=0.27, h->e=7.00, k->e=4.32, k->h=1.10
# ===================================================================
print("-" * 70)
print("TEST 4: Kernel Triad as Elemental Grammar")
print("  Galenic prediction: k(fire) > h(water/air) > e(earth) ordering")
print("  Test: quantitative ratios match monotonic potency gradient")
print("-" * 70)
print()

# C521 documents character-level kernel primitive directional asymmetry.
# The constraint text says "at the character level" but the ratios (7.00x)
# suggest between-token measurement. We compute BOTH:
#   (a) Within-MIDDLE character transitions (rare, most MIDDLEs have 1 kernel)
#   (b) Between-token: last kernel char of token N -> first kernel char of token N+1
# Method (b) matches C521's published ratios.

kernel_transitions = defaultdict(lambda: defaultdict(int))
kernel_counts = Counter()

for folio, tokens in folio_tokens.items():
    words = [t.word for t in tokens]
    # Build per-token kernel sequence: use first kernel char per token
    token_kernels = []
    for w in words:
        m = morph.extract(w)
        if not m.middle:
            continue
        kchars = [c for c in m.middle if c in ('k', 'h', 'e')]
        if kchars:
            token_kernels.append(kchars[0])  # First kernel char

    for c in token_kernels:
        kernel_counts[c] += 1
    for i in range(len(token_kernels) - 1):
        kernel_transitions[token_kernels[i]][token_kernels[i + 1]] += 1

# Compute transition ratios (observed / expected by frequency)
total_kernels = sum(kernel_counts.values())
kernel_freq = {k: kernel_counts[k] / total_kernels for k in ['k', 'h', 'e']}

print("Kernel character frequencies (within MIDDLEs):")
for kc in ['k', 'h', 'e']:
    print(f"  {kc}: {kernel_counts[kc]} ({100*kernel_freq[kc]:.1f}%)")
print()

print("Kernel char transition matrix (observed / expected):")
print(f"  {'':>5} {'->k':>8} {'->h':>8} {'->e':>8}")
for src in ['k', 'h', 'e']:
    parts = []
    for tgt in ['k', 'h', 'e']:
        obs = kernel_transitions[src][tgt]
        exp = kernel_counts[src] * kernel_freq[tgt]
        ratio = obs / exp if exp > 0 else 0
        parts.append(f"{ratio:>8.2f}")
    print(f"  {src:>5} {''.join(parts)}")

print()
print("Galenic elemental ordering test:")
print("  C521 reference: e->h=0.00, h->k=0.22, e->k=0.27, h->e=7.00, k->e=4.32, k->h=1.10")
print("  Prediction 1: e->h and e->k suppressed (earth cannot generate fire/water)")

eh_ratio = kernel_transitions['e']['h'] / (kernel_counts['e'] * kernel_freq['h']) if kernel_counts['e'] * kernel_freq['h'] > 0 else 0
ek_ratio = kernel_transitions['e']['k'] / (kernel_counts['e'] * kernel_freq['k']) if kernel_counts['e'] * kernel_freq['k'] > 0 else 0
he_ratio = kernel_transitions['h']['e'] / (kernel_counts['h'] * kernel_freq['e']) if kernel_counts['h'] * kernel_freq['e'] > 0 else 0
ke_ratio = kernel_transitions['k']['e'] / (kernel_counts['k'] * kernel_freq['e']) if kernel_counts['k'] * kernel_freq['e'] > 0 else 0
kh_ratio = kernel_transitions['k']['h'] / (kernel_counts['k'] * kernel_freq['h']) if kernel_counts['k'] * kernel_freq['h'] > 0 else 0
hk_ratio = kernel_transitions['h']['k'] / (kernel_counts['h'] * kernel_freq['k']) if kernel_counts['h'] * kernel_freq['k'] > 0 else 0

print(f"    e->h = {eh_ratio:.3f}, e->k = {ek_ratio:.3f}")
pred1_pass = eh_ratio < 0.5 and ek_ratio < 0.5
print(f"    {'PASS' if pred1_pass else 'FAIL'}: both < 0.5 (strongly suppressed)")

print(f"  Prediction 2: h->e and k->e elevated (natural fall toward earth)")
print(f"    h->e = {he_ratio:.3f}, k->e = {ke_ratio:.3f}")
pred2_pass = he_ratio > 2.0 and ke_ratio > 2.0
print(f"    {'PASS' if pred2_pass else 'FAIL'}: both > 2.0 (strongly elevated)")

print(f"  Prediction 3: k->h > h->k (fire dominates air/water)")
print(f"    k->h = {kh_ratio:.3f}, h->k = {hk_ratio:.3f}")
pred3_pass = kh_ratio > hk_ratio
print(f"    {'PASS' if pred3_pass else 'FAIL'}: k->h > h->k")

print(f"  Prediction 4: Monotonic potency: k->e > k->h > 1 > h->k > e->k")
pred4_pass = ke_ratio > kh_ratio > 1.0 > hk_ratio > ek_ratio
print(f"    {ke_ratio:.3f} > {kh_ratio:.3f} > 1.0 > {hk_ratio:.3f} > {ek_ratio:.3f}")
print(f"    {'PASS' if pred4_pass else 'FAIL'}: strict monotonic gradient")

preds_pass = sum([pred1_pass, pred2_pass, pred3_pass, pred4_pass])
if preds_pass == 4:
    t4_verdict = "PASS"
elif preds_pass >= 3:
    t4_verdict = "STRONG_PARTIAL"
elif preds_pass >= 2:
    t4_verdict = "PARTIAL"
else:
    t4_verdict = "FAIL"

# Additional: test whether ratios follow geometric (Galenic degree theory)
# vs linear decay
ratios_descending = sorted([ke_ratio, kh_ratio, he_ratio], reverse=True)
if len(ratios_descending) == 3 and all(r > 0 for r in ratios_descending):
    # Geometric: ratio[i+1]/ratio[i] should be constant
    geo_ratios = [ratios_descending[i+1] / ratios_descending[i]
                  for i in range(len(ratios_descending) - 1)]
    geo_cv = np.std(geo_ratios) / np.mean(geo_ratios) if np.mean(geo_ratios) > 0 else float('inf')
    print(f"\n  Geometric ratio test (Galenic degree theory):")
    print(f"    Descending ratios: {[f'{r:.3f}' for r in ratios_descending]}")
    print(f"    Step ratios: {[f'{r:.3f}' for r in geo_ratios]}")
    print(f"    CV of step ratios: {geo_cv:.3f} (< 0.3 = geometric)")
    if geo_cv < 0.3:
        print(f"    -> Ratios follow GEOMETRIC decay (matches degree theory)")
    else:
        print(f"    -> Ratios do NOT follow geometric decay")

t4_data = {
    'transitions': {f'{s}->{t}': kernel_transitions[s][t]
                    for s in ['k', 'h', 'e'] for t in ['k', 'h', 'e']},
    'ratios': {
        'e->h': eh_ratio, 'e->k': ek_ratio,
        'h->e': he_ratio, 'k->e': ke_ratio,
        'k->h': kh_ratio, 'h->k': hk_ratio
    },
    'predictions': {
        'P1_suppression': pred1_pass,
        'P2_elevation': pred2_pass,
        'P3_fire_dominance': pred3_pass,
        'P4_monotonic': pred4_pass
    }
}

print(f"\nT4 VERDICT: {t4_verdict} ({preds_pass}/4 predictions)")
print()


# ===================================================================
# TEST 5: CONCOCTION DURATION (PARAGRAPH LENGTH VS PP COMPLEXITY)
# ===================================================================
# Galenic concoction: processing time scales NON-LINEARLY with
# material complexity. Convex shape (diminishing returns) matches
# Galenic kinetics.
#
# Test: paragraph_length ~ f(PP_count). If non-linear convex, PASS.
# If linear, adds nothing beyond C858.
# ===================================================================
print("-" * 70)
print("TEST 5: Concoction Duration Scaling")
print("  Galenic prediction: paragraph length scales non-linearly with PP count")
print("  Null (C858): linear relationship only")
print("-" * 70)
print()

# Compute PP count and paragraph length for each Currier A paragraph
# PP MIDDLEs: those that propagate to B (C504)
from scripts.voynich import RecordAnalyzer

rec_analyzer = RecordAnalyzer()

# Build A paragraph structure: group records by folio
# For Currier A, a "paragraph" = all records in a folio (simplified)
# Actually, we need to match A folios to B program length

# Alternative approach: for each B folio, count:
# - Total token count (paragraph length / operational complexity)
# - Corresponding A folio PP count (material complexity)
# This tests whether richer material specs (more PP) predict longer programs.

# Get all Currier A records
a_folio_pp = defaultdict(int)
a_folio_ri = defaultdict(int)
a_folio_records = defaultdict(int)

for tok in tx.currier_a():
    if not tok.word.strip() or '*' in tok.word:
        continue
    m = morph.extract(tok.word)
    a_folio_records[tok.folio] += 1

# Use RecordAnalyzer for PP/RI classification
# Get unique Currier A folios
a_folios = set()
for tok in tx.currier_a():
    a_folios.add(tok.folio)

# For A folios, count PP vs RI MIDDLEs per folio
from scripts.voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()

for tok in tx.currier_a():
    if not tok.word.strip() or '*' in tok.word:
        continue
    m = morph.extract(tok.word)
    if m.middle:
        if m.middle in pp_middles:
            a_folio_pp[tok.folio] += 1
        elif m.middle in ri_middles:
            a_folio_ri[tok.folio] += 1

# B folio token counts (program length)
b_folio_length = Counter()
for folio, tokens in folio_tokens.items():
    b_folio_length[folio] = len(tokens)

# Now we need A-B folio correspondence
# Herbal folios have both A and B content: check overlap
# Actually, A and B are different folios (different Currier language assignments)
# The cross-system connection is through the A->AZC->B pipeline (C473)
# For this test, use WITHIN-B complexity: PP MIDDLEs in B tokens as material spec proxy

# Revised: compute per-B-paragraph PP MIDDLE count and total length
print("Computing per-paragraph PP complexity and length...")
print()

para_pp_counts = []
para_lengths = []
para_labels = []

for folio in sorted(folio_tokens.keys()):
    try:
        paragraphs = decoder.analyze_folio_paragraphs(folio)
    except Exception:
        continue

    for para in paragraphs:
        if para.token_count < 3:
            continue

        # Count PP MIDDLEs in this paragraph
        pp_count = 0
        for line in para.lines:
            for tok_analysis in line.tokens:
                if tok_analysis.morph and tok_analysis.morph.middle:
                    if tok_analysis.morph.middle in pp_middles:
                        pp_count += 1

        para_pp_counts.append(pp_count)
        para_lengths.append(para.token_count)
        para_labels.append(f"{folio}_{para.paragraph_id}")

if len(para_pp_counts) >= 10:
    pp_arr = np.array(para_pp_counts)
    len_arr = np.array(para_lengths)

    # Linear fit
    slope_lin, intercept_lin, r_lin, p_lin, se_lin = sp_stats.linregress(pp_arr, len_arr)
    r2_lin = r_lin ** 2

    # Log-linear fit (concoction kinetics: length ~ a * log(pp + 1) + b)
    log_pp = np.log(pp_arr + 1)
    slope_log, intercept_log, r_log, p_log, se_log = sp_stats.linregress(log_pp, len_arr)
    r2_log = r_log ** 2

    # Quadratic fit
    coeffs_quad = np.polyfit(pp_arr, len_arr, 2)
    pred_quad = np.polyval(coeffs_quad, pp_arr)
    ss_res_quad = np.sum((len_arr - pred_quad) ** 2)
    ss_tot = np.sum((len_arr - np.mean(len_arr)) ** 2)
    r2_quad = 1 - ss_res_quad / ss_tot if ss_tot > 0 else 0

    print(f"Paragraphs analyzed: {len(para_pp_counts)}")
    print(f"PP count range: {min(para_pp_counts)} - {max(para_pp_counts)}")
    print(f"Token count range: {min(para_lengths)} - {max(para_lengths)}")
    print()
    print(f"Model comparison:")
    print(f"  Linear:    R2 = {r2_lin:.4f}, p = {p_lin:.2e}")
    print(f"  Log-linear: R2 = {r2_log:.4f}, p = {p_log:.2e}")
    print(f"  Quadratic: R2 = {r2_quad:.4f}")
    print()

    # Test for non-linearity: compare linear vs quadratic
    # F-test for added quadratic term
    n = len(para_pp_counts)
    ss_res_lin = np.sum((len_arr - (slope_lin * pp_arr + intercept_lin)) ** 2)
    df_lin = n - 2
    df_quad = n - 3

    if df_quad > 0 and ss_res_quad > 0:
        f_stat = ((ss_res_lin - ss_res_quad) / 1) / (ss_res_quad / df_quad)
        p_f = 1 - sp_stats.f.cdf(f_stat, 1, df_quad)
        print(f"  F-test (linear vs quadratic): F = {f_stat:.3f}, p = {p_f:.4f}")

        if p_f < 0.05:
            print(f"  -> SIGNIFICANT non-linearity detected")
            # Check convexity (Galenic prediction: diminishing returns)
            if coeffs_quad[0] < 0:
                print(f"  -> Quadratic term NEGATIVE (concave = diminishing returns)")
                print(f"  -> GALENIC concoction kinetics SUPPORTED")
                t5_verdict = "PASS"
            else:
                print(f"  -> Quadratic term POSITIVE (convex = accelerating returns)")
                print(f"  -> Galenic prediction CONTRADICTED")
                t5_verdict = "FAIL_WRONG_SHAPE"
        else:
            print(f"  -> NOT SIGNIFICANT: relationship is LINEAR")
            print(f"  -> Galenic concoction kinetics NOT supported (no non-linearity)")
            t5_verdict = "FAIL_LINEAR"
    else:
        t5_verdict = "UNDERPOWERED"

    # Correlation coefficient for main relationship
    rho_main, p_main = sp_stats.spearmanr(pp_arr, len_arr)
    print(f"\n  Spearman (PP count vs para length): rho = {rho_main:.3f}, p = {p_main:.2e}")

    t5_data = {
        'n_paragraphs': len(para_pp_counts),
        'r2_linear': float(r2_lin),
        'r2_log': float(r2_log),
        'r2_quadratic': float(r2_quad),
        'spearman_rho': float(rho_main),
        'spearman_p': float(p_main),
        'quad_coefficient': float(coeffs_quad[0])
    }
else:
    print(f"  Insufficient paragraphs: {len(para_pp_counts)}")
    t5_verdict = "UNDERPOWERED"
    t5_data = {}

print(f"\nT5 VERDICT: {t5_verdict}")
print()


# ===================================================================
# SUMMARY
# ===================================================================
print("=" * 70)
print("PHASE 384 SUMMARY: GALENIC PARALLEL TESTS")
print("=" * 70)
print()
print(f"  T1 Class-Specific Recovery:     {t1_verdict}")
print(f"  T2 Degree-4 Universality:       {t2_verdict}")
print(f"  T3 Illustration Residual:       {t3_verdict}")
print(f"  T4 Kernel Elemental Grammar:    {t4_verdict}")
print(f"  T5 Concoction Duration:         {t5_verdict}")
print()

verdicts = [t1_verdict, t2_verdict, t3_verdict, t4_verdict, t5_verdict]
passes = sum(1 for v in verdicts if v.startswith('PASS'))
partials = sum(1 for v in verdicts if 'PARTIAL' in v)
fails = sum(1 for v in verdicts if v.startswith('FAIL'))
underpowered = sum(1 for v in verdicts if v == 'UNDERPOWERED')

print(f"  PASS: {passes}  PARTIAL: {partials}  FAIL: {fails}  UNDERPOWERED: {underpowered}")
print()

if passes >= 3:
    overall = "GALENIC_FINGERPRINT_CONFIRMED"
    print("OVERALL: Galenic intellectual framework leaves measurable structural")
    print("fingerprint in the Voynich control architecture.")
elif passes + partials >= 3:
    overall = "GALENIC_FINGERPRINT_PARTIAL"
    print("OVERALL: Partial evidence of Galenic structural fingerprint.")
    print("Some but not all quantitative predictions confirmed.")
elif fails >= 3:
    overall = "GALENIC_FINGERPRINT_NOT_SUPPORTED"
    print("OVERALL: Galenic framework does NOT leave measurable structural")
    print("fingerprint beyond already-known constraints.")
else:
    overall = "INCONCLUSIVE"
    print("OVERALL: Results inconclusive. Mixed evidence.")

print()

# Save results
results = {
    'phase': 384,
    'name': 'GALENIC_PARALLEL_TESTS',
    'test_count': 5,
    'verdicts': {
        'T1_class_specific_recovery': t1_verdict,
        'T2_degree4_universality': t2_verdict,
        'T3_illustration_residual': t3_verdict,
        'T4_kernel_elemental_grammar': t4_verdict,
        'T5_concoction_duration': t5_verdict
    },
    'overall': overall,
    'T1_data': {k: {kk: int(vv) if isinstance(vv, (int, np.integer)) else vv
                    for kk, vv in v.items()} if isinstance(v, dict) else v
                for k, v in t1_data.items()},
    'T2_data': t2_data,
    'T3_data': t3_data,
    'T4_data': t4_data,
    'T5_data': t5_data
}

output_path = RESULTS / 'galenic_test_results.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to: {output_path}")
