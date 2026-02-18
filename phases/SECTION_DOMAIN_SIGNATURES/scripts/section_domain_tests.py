#!/usr/bin/env python3
"""
Phase 386: Section Domain Signatures — Temporal Structure & LINK Distribution

Tests whether manuscript sections show operationally distinct temporal
signatures consistent with different craft domains (distillation,
compounding, treatment) or whether section variation is fully explained
by REGIME composition.

Tests:
  T1: Temporal Structure (AXM state-run length distributions by section)
      - Distillation = long runs (continuous process)
      - Compounding = short cyclic runs (repetitive discrete operations)
      - Treatment = episodic bursts (observe → decide → intervene)

  T2: LINK Distribution (inter-LINK intervals and positioning by section)
      - Distillation: periodic checkpoints
      - Compounding: step boundaries
      - Treatment: observation pauses

  T3: Recovery Architecture by Section
      - Post-hazard kernel profiles: what operations follow hazard sources?
      - Different domains should show different recovery strategies

  T4: REGIME Sufficiency Test (critical null model)
      - Does REGIME composition alone explain section differences?
      - If yes, three-domain hypothesis is redundant

Grounding constraints:
  C1006 (AXM dwell), C1029 (section-parameterized weights),
  C1047 (section-dynamics additive only), C1055 (near-section-decomposable),
  C552 (section role profiles), C609 (LINK density), C634 (recovery profiling),
  C805 (LINK positional bias), C1085-C1087 (Bio distinctiveness)
"""

import sys
import json
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats as sp_stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import (Transcript, Morphology, BFolioDecoder,
                              BTokenAnalysis)

RESULTS = ROOT / "phases" / "SECTION_DOMAIN_SIGNATURES" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# C109 hazard sources
FORBIDDEN_TRANSITIONS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]
HAZARD_SOURCES = set(a for a, b in FORBIDDEN_TRANSITIONS)

SECTION_NAMES = {'B': 'Bio', 'S': 'Stars', 'H': 'Herbal', 'C': 'Cosmo', 'T': 'Recipe'}
STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}

# ===================================================================
print("=" * 80)
print("PHASE 386: SECTION DOMAIN SIGNATURES")
print("=" * 80)
print()

tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()

# Load regime assignments
regime_path = ROOT / 'data' / 'regime_folio_mapping.json'
with open(regime_path, 'r', encoding='utf-8') as f:
    regime_data = json.load(f)
folio_regime = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

# Build per-folio token data with full analysis
print("Building token database...")
folio_tokens = defaultdict(list)
folio_section = {}

for tok in tx.currier_b():
    if not tok.word.strip() or '*' in tok.word:
        continue

    m = morph.extract(tok.word)
    analysis = decoder.analyze_token(tok.word)

    entry = {
        'word': tok.word,
        'folio': tok.folio,
        'line': tok.line,
        'section': tok.section,
        'middle': m.middle if m.middle else '',
        'prefix': m.prefix if m.prefix else '',
        'macro_state': analysis.macro_state if analysis.macro_state else None,
        'is_link': m.prefix in {'lk', 'lo'} if m.prefix else False,
        'kernel': None,
    }

    # Kernel character
    if m.middle:
        for c in m.middle:
            if c in ('k', 'h', 'e'):
                entry['kernel'] = c
                break

    folio_tokens[tok.folio].append(entry)
    if tok.folio not in folio_section:
        folio_section[tok.folio] = tok.section

# Group folios by section
section_folios = defaultdict(list)
for f, s in folio_section.items():
    section_folios[s].append(f)

# Overview
for s in sorted(section_folios.keys()):
    folios = section_folios[s]
    n_tok = sum(len(folio_tokens[f]) for f in folios)
    regimes = Counter(folio_regime.get(f, '?') for f in folios)
    r_str = ', '.join(f"{r}:{n}" for r, n in sorted(regimes.items()))
    print(f"  {s} ({SECTION_NAMES.get(s, '?')}): {len(folios)} folios, {n_tok} tokens | {r_str}")
print()


# ===================================================================
# TEST 1: TEMPORAL STRUCTURE — STATE RUN LENGTHS BY SECTION
# ===================================================================
print("-" * 80)
print("TEST 1: TEMPORAL STRUCTURE (State Run Lengths by Section)")
print("  Continuous process = long runs")
print("  Repetitive discrete = short cyclic runs")
print("  Episodic intervention = variable burst pattern")
print("-" * 80)
print()

def compute_runs(token_list):
    """Compute state runs from a token sequence."""
    runs = []
    current_state = None
    current_length = 0

    for tok in token_list:
        state = tok['macro_state']
        if state is None:
            continue
        if state == current_state:
            current_length += 1
        else:
            if current_state is not None:
                runs.append({'state': current_state, 'length': current_length})
            current_state = state
            current_length = 1

    if current_state is not None:
        runs.append({'state': current_state, 'length': current_length})

    return runs

# Compute per-folio run statistics
folio_run_stats = {}
for folio, tokens in folio_tokens.items():
    runs = compute_runs(tokens)
    if len(runs) < 5:
        continue

    lengths = [r['length'] for r in runs]
    state_runs = defaultdict(list)
    for r in runs:
        state_runs[r['state']].append(r['length'])

    # State transition count (how often state changes)
    n_transitions = len(runs) - 1
    n_tokens_with_state = sum(r['length'] for r in runs)
    cycling_rate = n_transitions / n_tokens_with_state if n_tokens_with_state > 0 else 0

    # Run length distribution statistics
    folio_run_stats[folio] = {
        'mean_run': np.mean(lengths),
        'median_run': np.median(lengths),
        'max_run': max(lengths),
        'std_run': np.std(lengths),
        'cv_run': np.std(lengths) / np.mean(lengths) if np.mean(lengths) > 0 else 0,
        'cycling_rate': cycling_rate,
        'n_runs': len(runs),
        'n_tokens': n_tokens_with_state,
        'axm_mean_run': np.mean(state_runs.get('AXM', [0])),
        'state_runs': {s: len(v) for s, v in state_runs.items()},
    }

# Aggregate by section
print(f"  {'Section':<10} {'MeanRun':>8} {'MedRun':>8} {'MaxRun':>8} {'CV':>8} {'CycleRate':>10} {'AXM_Run':>8} {'Folios':>7}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*8} {'-'*7}")

section_run_data = {}
for s in sorted(section_folios.keys()):
    folios = [f for f in section_folios[s] if f in folio_run_stats]
    if not folios:
        continue

    means = [folio_run_stats[f]['mean_run'] for f in folios]
    medians = [folio_run_stats[f]['median_run'] for f in folios]
    maxes = [folio_run_stats[f]['max_run'] for f in folios]
    cvs = [folio_run_stats[f]['cv_run'] for f in folios]
    cycling = [folio_run_stats[f]['cycling_rate'] for f in folios]
    axm_runs = [folio_run_stats[f]['axm_mean_run'] for f in folios]

    section_run_data[s] = {
        'mean_run': means,
        'median_run': medians,
        'max_run': maxes,
        'cv_run': cvs,
        'cycling_rate': cycling,
        'axm_mean_run': axm_runs,
        'n_folios': len(folios),
    }

    print(f"  {s:<10} {np.median(means):>8.2f} {np.median(medians):>8.2f} "
          f"{np.median(maxes):>8.1f} {np.median(cvs):>8.2f} "
          f"{np.median(cycling):>10.4f} {np.median(axm_runs):>8.2f} {len(folios):>7}")

print()

# Pairwise tests (mean run length, Mann-Whitney)
sections_with_data = sorted(s for s in section_run_data if section_run_data[s]['n_folios'] >= 3)
print("  Pairwise mean-run comparisons (Mann-Whitney):")
print(f"  {'Pair':<10} {'Med1':>8} {'Med2':>8} {'U':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*5}")

t1_pairwise = {}
for i, s1 in enumerate(sections_with_data):
    for s2 in sections_with_data[i+1:]:
        v1 = section_run_data[s1]['mean_run']
        v2 = section_run_data[s2]['mean_run']
        u, p = sp_stats.mannwhitneyu(v1, v2, alternative='two-sided')
        med1, med2 = np.median(v1), np.median(v2)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
        print(f"  {s1+'-'+s2:<10} {med1:>8.2f} {med2:>8.2f} {u:>8.0f} {p:>10.4f} {sig:>5}")
        t1_pairwise[f"{s1}-{s2}"] = {'U': float(u), 'p': float(p), 'med1': float(med1), 'med2': float(med2)}

# Cycling rate comparison
print()
print("  Pairwise cycling-rate comparisons (Mann-Whitney):")
print(f"  {'Pair':<10} {'Med1':>8} {'Med2':>8} {'U':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*5}")

t1_cycling = {}
for i, s1 in enumerate(sections_with_data):
    for s2 in sections_with_data[i+1:]:
        v1 = section_run_data[s1]['cycling_rate']
        v2 = section_run_data[s2]['cycling_rate']
        u, p = sp_stats.mannwhitneyu(v1, v2, alternative='two-sided')
        med1, med2 = np.median(v1), np.median(v2)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
        print(f"  {s1+'-'+s2:<10} {med1:>8.4f} {med2:>8.4f} {u:>8.0f} {p:>10.4f} {sig:>5}")
        t1_cycling[f"{s1}-{s2}"] = {'U': float(u), 'p': float(p)}

# Kruskal-Wallis across all sections (excl T)
kw_sections = [s for s in sections_with_data if s != 'T']
kw_groups_mean = [section_run_data[s]['mean_run'] for s in kw_sections]
kw_groups_cycle = [section_run_data[s]['cycling_rate'] for s in kw_sections]

if len(kw_groups_mean) >= 3:
    h_mean, p_mean = sp_stats.kruskal(*kw_groups_mean)
    h_cycle, p_cycle = sp_stats.kruskal(*kw_groups_cycle)
    print(f"\n  Kruskal-Wallis (excl T): mean_run H={h_mean:.2f}, p={p_mean:.4f}")
    print(f"  Kruskal-Wallis (excl T): cycling_rate H={h_cycle:.2f}, p={p_cycle:.4f}")

# Run length distribution shape (continuous vs cyclic vs episodic)
print()
print("  Run length distribution shape by section:")
print(f"  {'Section':<10} {'Pct_1':>8} {'Pct_2':>8} {'Pct_3+':>8} {'Pct_5+':>8} {'Pct_10+':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

for s in sorted(section_folios.keys()):
    all_runs = []
    for f in section_folios[s]:
        runs = compute_runs(folio_tokens[f])
        all_runs.extend([r['length'] for r in runs])

    if not all_runs:
        continue

    n = len(all_runs)
    pct1 = 100 * sum(1 for r in all_runs if r == 1) / n
    pct2 = 100 * sum(1 for r in all_runs if r == 2) / n
    pct3 = 100 * sum(1 for r in all_runs if r >= 3) / n
    pct5 = 100 * sum(1 for r in all_runs if r >= 5) / n
    pct10 = 100 * sum(1 for r in all_runs if r >= 10) / n
    print(f"  {s:<10} {pct1:>7.1f}% {pct2:>7.1f}% {pct3:>7.1f}% {pct5:>7.1f}% {pct10:>7.1f}%")

# T1 Verdict
print()
# Check if sections differ significantly on temporal structure
sig_pairs_run = sum(1 for k, v in t1_pairwise.items() if v['p'] < 0.05 and 'T' not in k)
total_pairs_run = sum(1 for k in t1_pairwise if 'T' not in k)
if p_mean < 0.01:
    t1_verdict = "PASS_TEMPORAL_DISTINCT"
    print(f"T1 VERDICT: {t1_verdict} (KW p={p_mean:.4f}, {sig_pairs_run}/{total_pairs_run} pairs significant)")
elif p_mean < 0.05:
    t1_verdict = "MARGINAL_TEMPORAL"
    print(f"T1 VERDICT: {t1_verdict} (KW p={p_mean:.4f})")
else:
    t1_verdict = "FAIL_TEMPORAL_SAME"
    print(f"T1 VERDICT: {t1_verdict} (KW p={p_mean:.4f})")

print()


# ===================================================================
# TEST 2: LINK DISTRIBUTION BY SECTION
# ===================================================================
print("-" * 80)
print("TEST 2: LINK DISTRIBUTION BY SECTION")
print("  Metric: LINK density, inter-LINK intervals, LINK paragraph position")
print("-" * 80)
print()

# Compute per-folio LINK statistics
folio_link_stats = {}
for folio, tokens in folio_tokens.items():
    n_total = len(tokens)
    if n_total < 20:
        continue

    link_positions = [i for i, t in enumerate(tokens) if t['is_link']]
    n_link = len(link_positions)
    density = n_link / n_total

    # Inter-LINK intervals
    intervals = []
    for i in range(len(link_positions) - 1):
        intervals.append(link_positions[i+1] - link_positions[i])

    folio_link_stats[folio] = {
        'density': density,
        'n_link': n_link,
        'n_total': n_total,
        'mean_interval': np.mean(intervals) if intervals else float('nan'),
        'median_interval': np.median(intervals) if intervals else float('nan'),
        'cv_interval': np.std(intervals) / np.mean(intervals) if intervals and np.mean(intervals) > 0 else float('nan'),
    }

# Aggregate by section
print(f"  {'Section':<10} {'Density':>8} {'N_LINK':>8} {'MeanInt':>8} {'MedInt':>8} {'CV_Int':>8} {'Folios':>7}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*7}")

section_link_data = {}
for s in sorted(section_folios.keys()):
    folios = [f for f in section_folios[s] if f in folio_link_stats]
    if not folios:
        continue

    densities = [folio_link_stats[f]['density'] for f in folios]
    n_links = [folio_link_stats[f]['n_link'] for f in folios]
    mean_ints = [folio_link_stats[f]['mean_interval'] for f in folios if not np.isnan(folio_link_stats[f]['mean_interval'])]
    med_ints = [folio_link_stats[f]['median_interval'] for f in folios if not np.isnan(folio_link_stats[f]['median_interval'])]
    cv_ints = [folio_link_stats[f]['cv_interval'] for f in folios if not np.isnan(folio_link_stats[f]['cv_interval'])]

    section_link_data[s] = {
        'density': densities,
        'mean_interval': mean_ints,
        'n_folios': len(folios),
        'n_with_link': len(mean_ints),
    }

    d_med = np.median(densities)
    nl_med = np.median(n_links)
    mi_med = np.median(mean_ints) if mean_ints else float('nan')
    mdi_med = np.median(med_ints) if med_ints else float('nan')
    cv_med = np.median(cv_ints) if cv_ints else float('nan')

    print(f"  {s:<10} {d_med:>7.4f} {nl_med:>8.0f} {mi_med:>8.1f} {mdi_med:>8.1f} {cv_med:>8.2f} {len(folios):>7}")

print()

# Pairwise LINK density comparisons
print("  Pairwise LINK density comparisons (Mann-Whitney):")
print(f"  {'Pair':<10} {'Med1':>8} {'Med2':>8} {'U':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*5}")

sections_link = sorted(s for s in section_link_data if section_link_data[s]['n_folios'] >= 3)
t2_pairwise = {}
for i, s1 in enumerate(sections_link):
    for s2 in sections_link[i+1:]:
        v1 = section_link_data[s1]['density']
        v2 = section_link_data[s2]['density']
        u, p = sp_stats.mannwhitneyu(v1, v2, alternative='two-sided')
        med1, med2 = np.median(v1), np.median(v2)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'NS'
        print(f"  {s1+'-'+s2:<10} {med1:>8.4f} {med2:>8.4f} {u:>8.0f} {p:>10.4f} {sig:>5}")
        t2_pairwise[f"{s1}-{s2}"] = {'U': float(u), 'p': float(p)}

# Kruskal-Wallis
kw_link_sections = [s for s in sections_link if s != 'T']
kw_link_groups = [section_link_data[s]['density'] for s in kw_link_sections]
if len(kw_link_groups) >= 3:
    h_link, p_link = sp_stats.kruskal(*kw_link_groups)
    print(f"\n  Kruskal-Wallis LINK density (excl T): H={h_link:.2f}, p={p_link:.4f}")

# LINK density by REGIME (to check if section effect is just REGIME)
print()
print("  LINK density by REGIME (is section effect just REGIME composition?):")
regime_link = defaultdict(list)
for folio, stats in folio_link_stats.items():
    r = folio_regime.get(folio, '?')
    regime_link[r].append(stats['density'])

print(f"  {'REGIME':<12} {'Median':>8} {'Mean':>8} {'N':>5}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*5}")
for r in sorted(regime_link.keys()):
    vals = regime_link[r]
    print(f"  {r:<12} {np.median(vals):>8.4f} {np.mean(vals):>8.4f} {len(vals):>5}")

# T2 Verdict
print()
if p_link < 0.01:
    t2_verdict = "PASS_LINK_DISTINCT"
    print(f"T2 VERDICT: {t2_verdict} (KW p={p_link:.4f})")
elif p_link < 0.05:
    t2_verdict = "MARGINAL_LINK"
    print(f"T2 VERDICT: {t2_verdict} (KW p={p_link:.4f})")
else:
    t2_verdict = "FAIL_LINK_SAME"
    print(f"T2 VERDICT: {t2_verdict} (KW p={p_link:.4f})")

print()


# ===================================================================
# TEST 3: RECOVERY ARCHITECTURE BY SECTION
# ===================================================================
print("-" * 80)
print("TEST 3: RECOVERY ARCHITECTURE BY SECTION")
print("  Post-hazard kernel profile: what operations follow hazard sources?")
print("-" * 80)
print()

# For each section, look at tokens following hazard-source MIDDLEs
# and profile the kernel (k/h/e) of the next 1-3 tokens
def compute_post_hazard_profile(folio_set, window=3):
    """Compute kernel profile of tokens following hazard sources."""
    post_kernels = Counter()
    post_states = Counter()
    n_events = 0

    for folio in folio_set:
        tokens = folio_tokens[folio]
        for i, tok in enumerate(tokens):
            if tok['middle'] in HAZARD_SOURCES:
                n_events += 1
                # Look at next 1-window tokens
                for j in range(1, min(window + 1, len(tokens) - i)):
                    next_tok = tokens[i + j]
                    if next_tok['kernel']:
                        post_kernels[next_tok['kernel']] += 1
                    if next_tok['macro_state']:
                        post_states[next_tok['macro_state']] += 1

    return post_kernels, post_states, n_events

print(f"  {'Section':<10} {'Events':>8} {'Post-k%':>8} {'Post-h%':>8} {'Post-e%':>8} {'k/e':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

t3_data = {}
for s in sorted(section_folios.keys()):
    pk, ps, n_ev = compute_post_hazard_profile(section_folios[s])
    total_k = sum(pk.values())
    if total_k == 0 or n_ev == 0:
        continue

    k_pct = 100 * pk['k'] / total_k
    h_pct = 100 * pk['h'] / total_k
    e_pct = 100 * pk['e'] / total_k
    ke = pk['k'] / pk['e'] if pk['e'] > 0 else float('inf')

    t3_data[s] = {
        'n_events': n_ev,
        'post_k': float(k_pct),
        'post_h': float(h_pct),
        'post_e': float(e_pct),
        'post_ke': float(ke),
        'post_states': dict(ps),
    }

    print(f"  {s:<10} {n_ev:>8} {k_pct:>7.1f}% {h_pct:>7.1f}% {e_pct:>7.1f}% {ke:>8.3f}")

# Compare post-hazard profiles: chi-square
print()
recovery_sections = [s for s in sorted(t3_data.keys()) if s != 'T']
if len(recovery_sections) >= 2:
    contingency = []
    for s in recovery_sections:
        pk, _, _ = compute_post_hazard_profile(section_folios[s])
        contingency.append([pk['k'], pk['h'], pk['e']])
    contingency = np.array(contingency)
    chi2, p_rec, dof, _ = sp_stats.chi2_contingency(contingency)
    v = np.sqrt(chi2 / (contingency.sum() * (min(contingency.shape) - 1)))
    print(f"  Chi-square (post-hazard kernel x section): chi2={chi2:.1f}, p={p_rec:.2e}, V={v:.4f}")

# Compare with BASELINE kernel profiles (from Phase 385 supplement)
print()
print("  Comparison: Post-hazard vs baseline kernel profiles")
print(f"  {'Section':<10} {'Base-k%':>8} {'Post-k%':>8} {'Shift':>8} {'Base-h%':>8} {'Post-h%':>8} {'Shift':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

# Compute baseline kernel profiles
def compute_baseline_kernels(folio_set):
    counts = Counter()
    for folio in folio_set:
        for tok in folio_tokens[folio]:
            if tok['kernel']:
                counts[tok['kernel']] += 1
    return counts

for s in recovery_sections:
    bk = compute_baseline_kernels(section_folios[s])
    bt = sum(bk.values())
    if bt == 0:
        continue
    base_k = 100 * bk['k'] / bt
    base_h = 100 * bk['h'] / bt
    post_k = t3_data[s]['post_k']
    post_h = t3_data[s]['post_h']
    k_shift = post_k - base_k
    h_shift = post_h - base_h
    print(f"  {s:<10} {base_k:>7.1f}% {post_k:>7.1f}% {k_shift:>+7.1f} {base_h:>7.1f}% {post_h:>7.1f}% {h_shift:>+7.1f}")

# T3 Verdict
print()
if p_rec < 0.01:
    t3_verdict = "PASS_RECOVERY_DISTINCT"
    print(f"T3 VERDICT: {t3_verdict} (chi2={chi2:.1f}, p={p_rec:.2e})")
elif p_rec < 0.05:
    t3_verdict = "MARGINAL_RECOVERY"
    print(f"T3 VERDICT: {t3_verdict} (chi2={chi2:.1f}, p={p_rec:.2e})")
else:
    t3_verdict = "FAIL_RECOVERY_SAME"
    print(f"T3 VERDICT: {t3_verdict} (chi2={chi2:.1f}, p={p_rec:.2e})")

print()


# ===================================================================
# TEST 4: REGIME SUFFICIENCY — Critical Null Model
# ===================================================================
print("-" * 80)
print("TEST 4: REGIME SUFFICIENCY (Does REGIME explain section differences?)")
print("  If REGIME alone predicts section profiles, 3-domain is redundant")
print("-" * 80)
print()

# Strategy: for each dimension, compute REGIME-predicted value per folio
# (using the REGIME mean across all folios in that REGIME), then compare
# residuals by section. If section effects vanish after REGIME conditioning,
# REGIME is sufficient.

# Build per-folio profiles
folio_profiles = {}
for folio in folio_tokens:
    tokens = folio_tokens[folio]
    if len(tokens) < 20:
        continue

    kernels = Counter()
    n_with_kernel = 0
    n_link = 0
    n_total = len(tokens)

    for tok in tokens:
        if tok['kernel']:
            kernels[tok['kernel']] += 1
            n_with_kernel += 1
        if tok['is_link']:
            n_link += 1

    k_total = sum(kernels.values())
    if k_total == 0:
        continue

    # Run stats
    runs = compute_runs(tokens)
    lengths = [r['length'] for r in runs] if runs else [1]
    n_transitions = len(runs) - 1 if len(runs) > 1 else 0
    n_run_tokens = sum(r['length'] for r in runs)

    folio_profiles[folio] = {
        'k_pct': kernels['k'] / k_total,
        'h_pct': kernels['h'] / k_total,
        'e_pct': kernels['e'] / k_total,
        'link_density': n_link / n_total,
        'mean_run': np.mean(lengths),
        'cycling_rate': n_transitions / n_run_tokens if n_run_tokens > 0 else 0,
        'section': folio_section[folio],
        'regime': folio_regime.get(folio, '?'),
    }

# Compute REGIME means
regime_means = defaultdict(lambda: defaultdict(list))
for folio, prof in folio_profiles.items():
    for dim in ['k_pct', 'h_pct', 'e_pct', 'link_density', 'mean_run', 'cycling_rate']:
        regime_means[prof['regime']][dim].append(prof[dim])

regime_avg = {}
for r, dims in regime_means.items():
    regime_avg[r] = {dim: np.mean(vals) for dim, vals in dims.items()}

# Compute residuals (folio value - REGIME mean)
folio_residuals = {}
for folio, prof in folio_profiles.items():
    r = prof['regime']
    if r not in regime_avg:
        continue
    folio_residuals[folio] = {
        dim: prof[dim] - regime_avg[r][dim]
        for dim in ['k_pct', 'h_pct', 'e_pct', 'link_density', 'mean_run', 'cycling_rate']
    }
    folio_residuals[folio]['section'] = prof['section']

# Test: do REGIME-residuals still differ by section?
DIMS_TEST = ['k_pct', 'h_pct', 'e_pct', 'link_density', 'mean_run', 'cycling_rate']
DIM_NAMES = {
    'k_pct': 'k kernel%', 'h_pct': 'h kernel%', 'e_pct': 'e kernel%',
    'link_density': 'LINK density', 'mean_run': 'Mean run len', 'cycling_rate': 'Cycling rate',
}

print("  REGIME-residual Kruskal-Wallis by section (excl T):")
print(f"  {'Dimension':<16} {'H':>8} {'p':>10} {'Sig':>5} {'Interpretation':>30}")
print(f"  {'-'*16} {'-'*8} {'-'*10} {'-'*5} {'-'*30}")

t4_results = {}
section_residual_groups = defaultdict(lambda: defaultdict(list))
for folio, resid in folio_residuals.items():
    s = resid['section']
    if s == 'T':
        continue
    for dim in DIMS_TEST:
        section_residual_groups[dim][s].append(resid[dim])

n_surviving = 0
for dim in DIMS_TEST:
    groups = section_residual_groups[dim]
    sections_present = sorted(s for s in groups if len(groups[s]) >= 3)
    if len(sections_present) < 3:
        continue

    data = [groups[s] for s in sections_present]
    h_val, p_val = sp_stats.kruskal(*data)
    sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'NS'

    if p_val < 0.05:
        n_surviving += 1
        interp = "SECTION EFFECT SURVIVES REGIME"
    else:
        interp = "regime explains this dimension"

    t4_results[dim] = {'H': float(h_val), 'p': float(p_val), 'survives': p_val < 0.05}
    print(f"  {DIM_NAMES[dim]:<16} {h_val:>8.2f} {p_val:>10.4f} {sig:>5} {interp:>30}")

print()
total_dims = len(t4_results)
print(f"  Summary: {n_surviving}/{total_dims} dimensions have section effects BEYOND REGIME")

# T4 Verdict
if n_surviving == 0:
    t4_verdict = "REGIME_SUFFICIENT"
    print(f"\nT4 VERDICT: {t4_verdict} — REGIME alone explains all section differences")
    print("  -> Three-domain hypothesis is REDUNDANT (parsimony violation)")
elif n_surviving <= 2:
    t4_verdict = "PARTIAL_RESIDUAL"
    print(f"\nT4 VERDICT: {t4_verdict} — {n_surviving} dimensions show section effects beyond REGIME")
elif n_surviving >= 3:
    t4_verdict = "SECTION_INDEPENDENT"
    print(f"\nT4 VERDICT: {t4_verdict} — {n_surviving} dimensions show section effects beyond REGIME")
    print("  -> Section carries information NOT reducible to REGIME composition")

print()

# ===================================================================
# COSMO BOOTSTRAP (sample size concern)
# ===================================================================
print("-" * 80)
print("COSMO BOOTSTRAP (N=5 reliability check)")
print("-" * 80)
print()

# Bootstrap Cosmo's key metrics by resampling its 5 folios
cosmo_folios = [f for f in section_folios.get('C', []) if f in folio_profiles]
if len(cosmo_folios) >= 3:
    n_boot = 10000
    np.random.seed(42)

    boot_k = []
    boot_h = []
    boot_link = []
    boot_run = []

    for _ in range(n_boot):
        sample = np.random.choice(cosmo_folios, size=len(cosmo_folios), replace=True)
        boot_k.append(np.mean([folio_profiles[f]['k_pct'] for f in sample]))
        boot_h.append(np.mean([folio_profiles[f]['h_pct'] for f in sample]))
        boot_link.append(np.mean([folio_profiles[f]['link_density'] for f in sample]))
        boot_run.append(np.mean([folio_profiles[f]['mean_run'] for f in sample]))

    print(f"  {'Metric':<16} {'Observed':>10} {'Boot 2.5%':>10} {'Boot 97.5%':>10} {'Width':>10}")
    print(f"  {'-'*16} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    for name, obs, boot in [
        ('k kernel%', np.mean([folio_profiles[f]['k_pct'] for f in cosmo_folios]), boot_k),
        ('h kernel%', np.mean([folio_profiles[f]['h_pct'] for f in cosmo_folios]), boot_h),
        ('LINK density', np.mean([folio_profiles[f]['link_density'] for f in cosmo_folios]), boot_link),
        ('Mean run', np.mean([folio_profiles[f]['mean_run'] for f in cosmo_folios]), boot_run),
    ]:
        lo = np.percentile(boot, 2.5)
        hi = np.percentile(boot, 97.5)
        width = hi - lo
        print(f"  {name:<16} {obs:>10.4f} {lo:>10.4f} {hi:>10.4f} {width:>10.4f}")

    # Does Cosmo's h% CI overlap with corpus mean?
    corpus_h = np.mean([p['h_pct'] for p in folio_profiles.values()])
    h_lo = np.percentile(boot_h, 2.5)
    h_hi = np.percentile(boot_h, 97.5)
    if corpus_h < h_lo:
        print(f"\n  Cosmo h% CI [{h_lo:.4f}, {h_hi:.4f}] EXCLUDES corpus mean ({corpus_h:.4f})")
        print(f"  -> Cosmo h-enrichment is RELIABLE despite N=5")
    else:
        print(f"\n  Cosmo h% CI [{h_lo:.4f}, {h_hi:.4f}] INCLUDES corpus mean ({corpus_h:.4f})")
        print(f"  -> Cosmo h-enrichment may be a sample-size artifact")

print()

# ===================================================================
# SUMMARY
# ===================================================================
print("=" * 80)
print("PHASE 386 SUMMARY: SECTION DOMAIN SIGNATURES")
print("=" * 80)
print()
print(f"  T1 Temporal Structure:  {t1_verdict}")
print(f"  T2 LINK Distribution:   {t2_verdict}")
print(f"  T3 Recovery Architecture: {t3_verdict}")
print(f"  T4 REGIME Sufficiency:  {t4_verdict}")
print()

# Overall assessment
t_pass = sum(1 for v in [t1_verdict, t2_verdict, t3_verdict] if 'PASS' in v)
t_marginal = sum(1 for v in [t1_verdict, t2_verdict, t3_verdict] if 'MARGINAL' in v)

if 'SUFFICIENT' in t4_verdict:
    overall = "REGIME_EXPLAINS_ALL"
    conclusion = ("Section differences are fully explained by REGIME composition. "
                   "Three-domain hypothesis is not supported — parsimony favors "
                   "single-domain with REGIME parameterization.")
elif t_pass >= 2 and 'INDEPENDENT' in t4_verdict:
    overall = "MULTI_DOMAIN_SUPPORTED"
    conclusion = ("Sections show distinct temporal signatures beyond REGIME composition. "
                   "Consistent with operationally distinct domains sharing one grammar.")
elif t_pass >= 2:
    overall = "DISTINCT_BUT_REGIME_MEDIATED"
    conclusion = ("Sections have distinct operational profiles, but some differences "
                   "are mediated by REGIME composition. Domain interpretation is "
                   "possible but not strongly supported over REGIME-only model.")
elif t_pass >= 1 or t_marginal >= 2:
    overall = "WEAK_SIGNAL"
    conclusion = "Some section differences detected but insufficient for domain claims."
else:
    overall = "NO_DOMAIN_SIGNAL"
    conclusion = "No meaningful section-level temporal or structural differences detected."

print(f"  OVERALL: {overall}")
print(f"  {conclusion}")
print()

# Save results
results = {
    'phase': 386,
    'name': 'SECTION_DOMAIN_SIGNATURES',
    'verdicts': {
        'T1_temporal': t1_verdict,
        'T2_link': t2_verdict,
        'T3_recovery': t3_verdict,
        'T4_regime_sufficiency': t4_verdict,
    },
    'overall': overall,
    'conclusion': conclusion,
    'T1_data': {
        'section_medians': {
            s: {
                'mean_run': float(np.median(d['mean_run'])),
                'cycling_rate': float(np.median(d['cycling_rate'])),
            }
            for s, d in section_run_data.items()
        },
        'kruskal_wallis_mean_run': {'H': float(h_mean), 'p': float(p_mean)},
        'kruskal_wallis_cycling': {'H': float(h_cycle), 'p': float(p_cycle)},
    },
    'T2_data': {
        'section_medians': {
            s: float(np.median(d['density']))
            for s, d in section_link_data.items()
        },
        'kruskal_wallis': {'H': float(h_link), 'p': float(p_link)},
    },
    'T3_data': t3_data,
    'T4_data': {
        'dimensions_tested': total_dims,
        'surviving_regime': n_surviving,
        'results': {dim: {'H': v['H'], 'p': v['p'], 'survives': v['survives']}
                    for dim, v in t4_results.items()},
    },
}

out_path = RESULTS / 'section_domain_results.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to: {out_path}")
