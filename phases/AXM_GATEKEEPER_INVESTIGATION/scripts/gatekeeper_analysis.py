"""
AXM Gatekeeper Investigation (Phase 327)

Probes the exit-boundary gatekeeper subset discovered in C1007:
  T1: Entry vs exit boundary asymmetry
  T2: Exit routing (gatekeeper -> target state conditioning)
  T3: Positional confound control (mid-line vs line-end exits)
  T4: Run-length prediction (does gatekeeper identity predict duration?)
  T5: REGIME invariance of gatekeeper enrichment
  T6: HUB sub-role composition (C1000 mapping)
  T7: Transition entropy (successor predictability)
  T8: Approach-to-boundary geometry (radial depth + hazard-target gradient)
  T9: AXM internal subgraph profiling (betweenness centrality)

Builds on Phase 326 finding: classes 22, 21, 15, 20, 25 are 3-10x enriched
at AXM run exit boundaries (chi2=178.21, p<0.0001).
"""

import json
import sys
import os
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology

# -- Constants ----------------------------------------------------------------

REGIME_ORDER = ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']
REGIME_RANK = {r: i for i, r in enumerate(REGIME_ORDER)}

MACRO_NAMES = ['FL_HAZ', 'FQ', 'CC', 'AXm', 'AXM', 'FL_SAFE']
MACRO_PARTITION = {
    'FL_HAZ':  {7, 30},
    'FQ':      {9, 13, 14, 23},
    'CC':      {10, 11, 12},
    'AXm':     {3, 5, 18, 19, 42, 45},
    'AXM':     {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28, 29,
                31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49},
    'FL_SAFE': {38, 40},
}
CLASS_TO_MACRO = {}
for macro, classes in MACRO_PARTITION.items():
    for c in classes:
        CLASS_TO_MACRO[c] = macro

AXM_CLASSES = sorted(MACRO_PARTITION['AXM'])
GATEKEEPER_CLASSES = {15, 20, 21, 22, 25}  # Top 5 enriched from T8

# HUB sub-role mapping from C1000
HUB_SUB_ROLES = {
    'HAZARD_SOURCE':  {'ar', 'dy', 'ey', 'l', 'ol', 'or'},
    'HAZARD_TARGET':  {'aiin', 'al', 'ee', 'o', 'r', 't'},
    'SAFETY_BUFFER':  {'eol', 'k', 'od'},
    'PURE_CONNECTOR': {'d', 'e', 'eey', 'ek', 'eo', 'iin', 's', 'y'},
}
MIDDLE_TO_SUBROLE = {}
for role, middles in HUB_SUB_ROLES.items():
    for m in middles:
        MIDDLE_TO_SUBROLE[m] = role

# -- Load data ----------------------------------------------------------------

with open('data/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
regime_map = {f: d['regime'] for f, d in regime_data['regime_assignments'].items()}

with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']

tx = Transcript()
morph = Morphology()

# -- Build per-line token sequences with class and position info --------------

folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = token.line
    folio_section[folio] = token.section

    cls = token_to_class.get(w)
    macro = CLASS_TO_MACRO.get(cls) if cls else None
    if not macro:
        continue

    m = morph.extract(w)
    folio_lines[folio][line].append({
        'word': w,
        'macro': macro,
        'class': cls,
        'middle': m.middle if m else None,
    })

# Add normalized line position (token_index / line_length)
for folio, lines_dict in folio_lines.items():
    for line_key, tokens in lines_dict.items():
        n = len(tokens)
        for i, tok in enumerate(tokens):
            tok['line_pos'] = i / max(n - 1, 1)  # 0.0 = first, 1.0 = last

print(f"Folios with data: {len(folio_lines)}")
total_tokens = sum(len(t) for lines in folio_lines.values() for t in lines.values())
print(f"Total classified tokens: {total_tokens}")

# -- Extract detailed AXM runs -----------------------------------------------

all_runs = []  # All runs (all states)
axm_runs = []  # AXM runs only

for folio, lines_dict in folio_lines.items():
    for line_key, tokens in sorted(lines_dict.items()):
        if len(tokens) < 2:
            continue

        current_state = tokens[0]['macro']
        current_classes = [tokens[0]['class']]
        current_words = [tokens[0]['word']]
        current_middles = [tokens[0]['middle']]
        current_positions = [tokens[0]['line_pos']]
        prev_state = None

        for i in range(1, len(tokens)):
            if tokens[i]['macro'] == current_state:
                current_classes.append(tokens[i]['class'])
                current_words.append(tokens[i]['word'])
                current_middles.append(tokens[i]['middle'])
                current_positions.append(tokens[i]['line_pos'])
            else:
                run = {
                    'state': current_state,
                    'length': len(current_classes),
                    'folio': folio,
                    'classes': current_classes[:],
                    'middles': current_middles[:],
                    'positions': current_positions[:],
                    'next_state': tokens[i]['macro'],
                    'next_class': tokens[i]['class'],
                    'prev_state': prev_state,
                    'is_line_end': False,
                }
                all_runs.append(run)
                if current_state == 'AXM':
                    axm_runs.append(run)

                prev_state = current_state
                current_state = tokens[i]['macro']
                current_classes = [tokens[i]['class']]
                current_words = [tokens[i]['word']]
                current_middles = [tokens[i]['middle']]
                current_positions = [tokens[i]['line_pos']]

        # Last run in line
        run = {
            'state': current_state,
            'length': len(current_classes),
            'folio': folio,
            'classes': current_classes[:],
            'middles': current_middles[:],
            'positions': current_positions[:],
            'next_state': None,
            'next_class': None,
            'prev_state': prev_state,
            'is_line_end': True,
        }
        all_runs.append(run)
        if current_state == 'AXM':
            axm_runs.append(run)

print(f"Total runs: {len(all_runs)}")
print(f"AXM runs: {len(axm_runs)}")
axm_exits = [r for r in axm_runs if r['next_state'] is not None]
print(f"AXM runs with exits: {len(axm_exits)}")


# =============================================================================
# T1: ENTRY vs EXIT BOUNDARY ASYMMETRY
# =============================================================================

print("\n" + "=" * 70)
print("T1: ENTRY vs EXIT BOUNDARY ASYMMETRY")
print("=" * 70)

# For AXM runs length >= 3: first class = entry, last class = exit, middle = mid-run
entry_counts = defaultdict(int)
exit_counts = defaultdict(int)
midrun_counts = defaultdict(int)
entry_total = 0
exit_total = 0
midrun_total = 0

for r in axm_runs:
    if r['length'] >= 3:
        entry_counts[r['classes'][0]] += 1
        entry_total += 1
        exit_counts[r['classes'][-1]] += 1
        exit_total += 1
        for c in r['classes'][1:-1]:
            midrun_counts[c] += 1
            midrun_total += 1

# Compute enrichment for gatekeeper classes at entry vs exit
print(f"\n  AXM runs (length >= 3): {sum(1 for r in axm_runs if r['length'] >= 3)}")
print(f"  Entry tokens: {entry_total}, Exit tokens: {exit_total}, Mid-run tokens: {midrun_total}")

print(f"\n  Enrichment at entry vs exit boundaries (gatekeeper classes):")
print(f"  {'Class':<8} {'Entry_enrich':<14} {'Exit_enrich':<14} {'Mid-run_frac':<14}")
t1_class_data = {}
for cls in sorted(GATEKEEPER_CLASSES):
    e_frac = entry_counts[cls] / entry_total if entry_total > 0 else 0
    x_frac = exit_counts[cls] / exit_total if exit_total > 0 else 0
    m_frac = midrun_counts[cls] / midrun_total if midrun_total > 0 else 0
    e_enrich = e_frac / m_frac if m_frac > 0 else 0
    x_enrich = x_frac / m_frac if m_frac > 0 else 0
    print(f"  {cls:<8} {e_enrich:<14.2f} {x_enrich:<14.2f} {m_frac:<14.4f}")
    t1_class_data[str(cls)] = {
        'entry_frac': float(e_frac), 'exit_frac': float(x_frac), 'midrun_frac': float(m_frac),
        'entry_enrichment': float(e_enrich), 'exit_enrichment': float(x_enrich),
    }

# Chi-squared: entry-boundary distribution vs exit-boundary distribution
all_cls_both = sorted(set(entry_counts.keys()) | set(exit_counts.keys()))
entry_vec = np.array([entry_counts.get(c, 0) for c in all_cls_both])
exit_vec = np.array([exit_counts.get(c, 0) for c in all_cls_both])
nonzero_t1 = (entry_vec + exit_vec) > 0
if nonzero_t1.sum() >= 5:
    cont_t1 = np.array([entry_vec[nonzero_t1], exit_vec[nonzero_t1]])
    chi2_t1, p_t1, dof_t1, _ = stats.chi2_contingency(cont_t1)
    asymmetric = bool(p_t1 < 0.05)
    print(f"\n  Chi2 (entry vs exit distribution): chi2={chi2_t1:.2f}, p={p_t1:.4f}, dof={dof_t1}")
    print(f"  Entry/exit asymmetry: {'DETECTED' if asymmetric else 'NOT DETECTED'}")
else:
    chi2_t1, p_t1, dof_t1 = None, None, None
    asymmetric = False

t1_result = {
    'per_class': t1_class_data,
    'chi2_entry_vs_exit': float(chi2_t1) if chi2_t1 is not None else None,
    'p_entry_vs_exit': float(p_t1) if p_t1 is not None else None,
    'asymmetric': asymmetric,
}


# =============================================================================
# T2: EXIT ROUTING (Gatekeeper -> Target State)
# =============================================================================

print("\n" + "=" * 70)
print("T2: EXIT ROUTING (Gatekeeper -> Target State)")
print("=" * 70)

# For AXM exits: contingency table of last_class x next_state
# Focus on gatekeeper classes
target_states = [s for s in MACRO_NAMES if s != 'AXM']
gk_routing = {cls: defaultdict(int) for cls in sorted(GATEKEEPER_CLASSES)}
non_gk_routing = defaultdict(int)
non_gk_total = 0

for r in axm_exits:
    last_cls = r['classes'][-1]
    target = r['next_state']
    if last_cls in GATEKEEPER_CLASSES:
        gk_routing[last_cls][target] += 1
    else:
        non_gk_routing[target] += 1
        non_gk_total += 1

print(f"\n  Exit routing by gatekeeper class:")
print(f"  {'Class':<8}" + "".join(f"{s:<10}" for s in target_states) + "  Total")
for cls in sorted(GATEKEEPER_CLASSES):
    total_cls = sum(gk_routing[cls].values())
    row = f"  {cls:<8}"
    for s in target_states:
        n = gk_routing[cls].get(s, 0)
        pct = f"{n / total_cls:.0%}" if total_cls > 0 else "N/A"
        row += f"{n} ({pct})"[:10].ljust(10)
    row += f"  {total_cls}"
    print(row)

# Non-gatekeeper baseline
print(f"  {'Other':<8}", end="")
for s in target_states:
    n = non_gk_routing.get(s, 0)
    pct = f"{n / non_gk_total:.0%}" if non_gk_total > 0 else "N/A"
    print(f"{n} ({pct})"[:10].ljust(10), end="")
print(f"  {non_gk_total}")

# Chi-squared: is routing dependent on gatekeeper identity?
# Build contingency: rows = gatekeeper classes, cols = target states
gk_cls_list = sorted(GATEKEEPER_CLASSES)
routing_matrix = np.array([[gk_routing[cls].get(s, 0) for s in target_states]
                           for cls in gk_cls_list])

# Remove columns with all zeros
col_nonzero = routing_matrix.sum(axis=0) > 0
row_nonzero = routing_matrix.sum(axis=1) > 0
routing_clean = routing_matrix[np.ix_(row_nonzero, col_nonzero)]

if routing_clean.shape[0] >= 2 and routing_clean.shape[1] >= 2:
    chi2_t2, p_t2, dof_t2, _ = stats.chi2_contingency(routing_clean)
    routing_dependent = bool(p_t2 < 0.05)
    print(f"\n  Chi2 (gatekeeper x target): chi2={chi2_t2:.2f}, p={p_t2:.4f}, dof={dof_t2}")
    print(f"  Routing dependency: {'DETECTED' if routing_dependent else 'NOT DETECTED'}")
else:
    chi2_t2, p_t2, dof_t2 = None, None, None
    routing_dependent = False

t2_result = {
    'gatekeeper_routing': {str(cls): {s: int(gk_routing[cls].get(s, 0)) for s in target_states}
                           for cls in gk_cls_list},
    'non_gatekeeper_routing': {s: int(non_gk_routing.get(s, 0)) for s in target_states},
    'chi2': float(chi2_t2) if chi2_t2 is not None else None,
    'p': float(p_t2) if p_t2 is not None else None,
    'routing_dependent': routing_dependent,
}


# =============================================================================
# T3: POSITIONAL CONFOUND CONTROL
# =============================================================================

print("\n" + "=" * 70)
print("T3: POSITIONAL CONFOUND CONTROL")
print("=" * 70)

# Separate mid-line exits vs line-end exits
midline_exit_last = defaultdict(int)
midline_midrun = defaultdict(int)
midline_exit_total = 0
midline_midrun_total = 0

lineend_exit_last = defaultdict(int)
lineend_exit_total = 0

for r in axm_runs:
    if r['length'] < 3:
        continue
    if r['is_line_end']:
        lineend_exit_last[r['classes'][-1]] += 1
        lineend_exit_total += 1
    else:
        midline_exit_last[r['classes'][-1]] += 1
        midline_exit_total += 1
        for c in r['classes'][1:-1]:
            midline_midrun[c] += 1
            midline_midrun_total += 1

print(f"\n  Mid-line AXM exits (length >= 3): {midline_exit_total}")
print(f"  Line-end AXM exits (length >= 3): {lineend_exit_total}")

print(f"\n  Gatekeeper enrichment at MID-LINE exits only:")
print(f"  {'Class':<8} {'Midline_exit_enrich':<22} {'Line_end_exit_enrich':<22}")
t3_class_data = {}
for cls in sorted(GATEKEEPER_CLASSES):
    ml_frac = midline_exit_last[cls] / midline_exit_total if midline_exit_total > 0 else 0
    le_frac = lineend_exit_last[cls] / lineend_exit_total if lineend_exit_total > 0 else 0
    m_frac = midline_midrun.get(cls, 0) / midline_midrun_total if midline_midrun_total > 0 else 0
    ml_enrich = ml_frac / m_frac if m_frac > 0 else 0
    le_enrich = le_frac / m_frac if m_frac > 0 else 0
    print(f"  {cls:<8} {ml_enrich:<22.2f} {le_enrich:<22.2f}")
    t3_class_data[str(cls)] = {
        'midline_exit_enrichment': float(ml_enrich),
        'lineend_exit_enrichment': float(le_enrich),
        'midrun_frac': float(m_frac),
    }

# Chi-squared: mid-line exit boundary vs mid-run (controlling for line-end)
all_cls_ml = sorted(set(midline_exit_last.keys()) | set(midline_midrun.keys()))
ml_exit_v = np.array([midline_exit_last.get(c, 0) for c in all_cls_ml])
ml_mid_v = np.array([midline_midrun.get(c, 0) for c in all_cls_ml])
nz_ml = (ml_exit_v + ml_mid_v) > 0
if nz_ml.sum() >= 5:
    cont_ml = np.array([ml_exit_v[nz_ml], ml_mid_v[nz_ml]])
    chi2_t3, p_t3, dof_t3, _ = stats.chi2_contingency(cont_ml)
    midline_gating = bool(p_t3 < 0.05)
    print(f"\n  Chi2 (mid-line exit boundary vs mid-run): chi2={chi2_t3:.2f}, p={p_t3:.4f}")
    print(f"  Mid-line gating: {'CONFIRMED' if midline_gating else 'NOT CONFIRMED'}")
    if midline_gating:
        print("  -> Gatekeeper enrichment survives positional control (genuine gating)")
    else:
        print("  -> Gatekeeper enrichment may be positional artifact")
else:
    chi2_t3, p_t3, dof_t3 = None, None, None
    midline_gating = False

# Mean line position of gatekeeper vs non-gatekeeper AXM tokens
gk_positions = []
non_gk_positions = []
for r in axm_runs:
    for i, cls in enumerate(r['classes']):
        if cls in GATEKEEPER_CLASSES:
            gk_positions.append(r['positions'][i])
        else:
            non_gk_positions.append(r['positions'][i])

gk_mean_pos = float(np.mean(gk_positions)) if gk_positions else None
non_gk_mean_pos = float(np.mean(non_gk_positions)) if non_gk_positions else None
if gk_positions and non_gk_positions:
    u_stat, u_p = stats.mannwhitneyu(gk_positions, non_gk_positions, alternative='two-sided')
    print(f"\n  Mean line position: gatekeeper={gk_mean_pos:.3f}, non-gatekeeper={non_gk_mean_pos:.3f}")
    print(f"  Mann-Whitney: U={u_stat:.0f}, p={u_p:.4f}")
else:
    u_stat, u_p = None, None

t3_result = {
    'per_class': t3_class_data,
    'midline_chi2': float(chi2_t3) if chi2_t3 is not None else None,
    'midline_p': float(p_t3) if p_t3 is not None else None,
    'midline_gating': midline_gating,
    'gk_mean_position': gk_mean_pos,
    'non_gk_mean_position': non_gk_mean_pos,
    'position_mannwhitney_p': float(u_p) if u_p is not None else None,
}


# =============================================================================
# T4: RUN-LENGTH PREDICTION
# =============================================================================

print("\n" + "=" * 70)
print("T4: RUN-LENGTH PREDICTION")
print("=" * 70)

# For AXM runs (length >= 2): does last class predict run length?
gk_run_lengths = {cls: [] for cls in sorted(GATEKEEPER_CLASSES)}
non_gk_run_lengths = []

for r in axm_runs:
    if r['length'] < 2:
        continue
    last_cls = r['classes'][-1]
    if last_cls in GATEKEEPER_CLASSES:
        gk_run_lengths[last_cls].append(r['length'])
    else:
        non_gk_run_lengths.append(r['length'])

print(f"\n  AXM run length by exit class (length >= 2):")
print(f"  {'Class':<8} {'n':<8} {'Mean':<10} {'Median':<10} {'Std':<10}")
t4_per_class = {}
for cls in sorted(GATEKEEPER_CLASSES):
    runs = gk_run_lengths[cls]
    if runs:
        print(f"  {cls:<8} {len(runs):<8} {np.mean(runs):<10.2f} {np.median(runs):<10.1f} "
              f"{np.std(runs, ddof=1):<10.2f}" if len(runs) > 1 else
              f"  {cls:<8} {len(runs):<8} {np.mean(runs):<10.2f}")
        t4_per_class[str(cls)] = {
            'n': len(runs), 'mean': float(np.mean(runs)),
            'median': float(np.median(runs)),
        }
    else:
        print(f"  {cls:<8} 0")
        t4_per_class[str(cls)] = {'n': 0}

print(f"  {'Other':<8} {len(non_gk_run_lengths):<8} {np.mean(non_gk_run_lengths):<10.2f} "
      f"{np.median(non_gk_run_lengths):<10.1f}")

# Kruskal-Wallis: run length ~ gatekeeper class
gk_groups = [gk_run_lengths[cls] for cls in sorted(GATEKEEPER_CLASSES) if len(gk_run_lengths[cls]) >= 5]
if len(gk_groups) >= 2:
    kw_stat, kw_p = stats.kruskal(*gk_groups)
    print(f"\n  Kruskal-Wallis (run length ~ gatekeeper class): H={kw_stat:.2f}, p={kw_p:.4f}")
    kw_significant = bool(kw_p < 0.05)
    if kw_significant:
        print("  -> Gatekeeper identity PREDICTS run duration")
    else:
        print("  -> Gatekeeper identity does not predict run duration")
else:
    kw_stat, kw_p = None, None
    kw_significant = False

# Gatekeeper-terminated vs non-gatekeeper-terminated
all_gk_runs = [l for runs in gk_run_lengths.values() for l in runs]
if all_gk_runs and non_gk_run_lengths:
    mw_stat, mw_p = stats.mannwhitneyu(all_gk_runs, non_gk_run_lengths, alternative='two-sided')
    print(f"\n  Gatekeeper-terminated mean={np.mean(all_gk_runs):.2f} vs "
          f"Non-gatekeeper mean={np.mean(non_gk_run_lengths):.2f}")
    print(f"  Mann-Whitney: U={mw_stat:.0f}, p={mw_p:.4f}")
    gk_shorter = bool(mw_p < 0.05 and np.mean(all_gk_runs) < np.mean(non_gk_run_lengths))
else:
    mw_stat, mw_p = None, None
    gk_shorter = False

t4_result = {
    'per_class': t4_per_class,
    'non_gatekeeper_mean': float(np.mean(non_gk_run_lengths)) if non_gk_run_lengths else None,
    'kruskal_wallis_H': float(kw_stat) if kw_stat is not None else None,
    'kruskal_wallis_p': float(kw_p) if kw_p is not None else None,
    'gatekeeper_predicts_duration': kw_significant,
    'gk_vs_nongk_mannwhitney_p': float(mw_p) if mw_p is not None else None,
    'gk_shorter_runs': gk_shorter,
}


# =============================================================================
# T5: REGIME INVARIANCE
# =============================================================================

print("\n" + "=" * 70)
print("T5: REGIME INVARIANCE")
print("=" * 70)

t5_per_regime = {}
regime_enrichment_profiles = {}

for regime in REGIME_ORDER:
    regime_folios = {f for f, r in regime_map.items() if r == regime}
    regime_exit_last = defaultdict(int)
    regime_midrun = defaultdict(int)
    r_exit_total = 0
    r_mid_total = 0

    for r in axm_runs:
        if r['folio'] not in regime_folios or r['length'] < 3:
            continue
        regime_exit_last[r['classes'][-1]] += 1
        r_exit_total += 1
        for c in r['classes'][1:-1]:
            regime_midrun[c] += 1
            r_mid_total += 1

    print(f"\n  {regime}: {r_exit_total} exits, {r_mid_total} mid-run tokens")
    enrichment_profile = {}
    for cls in sorted(GATEKEEPER_CLASSES):
        x_frac = regime_exit_last.get(cls, 0) / r_exit_total if r_exit_total > 0 else 0
        m_frac = regime_midrun.get(cls, 0) / r_mid_total if r_mid_total > 0 else 0
        enrich = x_frac / m_frac if m_frac > 0 else 0
        enrichment_profile[cls] = enrich
        print(f"    Class {cls}: {enrich:.2f}x enriched")

    regime_enrichment_profiles[regime] = enrichment_profile

    # Per-regime chi-squared
    all_cls_r = sorted(set(regime_exit_last.keys()) | set(regime_midrun.keys()))
    ev = np.array([regime_exit_last.get(c, 0) for c in all_cls_r])
    mv = np.array([regime_midrun.get(c, 0) for c in all_cls_r])
    nz = (ev + mv) > 0
    if nz.sum() >= 5:
        cont_r = np.array([ev[nz], mv[nz]])
        chi2_r, p_r, _, _ = stats.chi2_contingency(cont_r)
        print(f"    Chi2 (exit vs mid-run): chi2={chi2_r:.2f}, p={p_r:.4f}")
        t5_per_regime[regime] = {'chi2': float(chi2_r), 'p': float(p_r),
                                 'significant': bool(p_r < 0.05)}
    else:
        t5_per_regime[regime] = {'status': 'insufficient_data'}

# Cross-regime consistency: Spearman correlation of enrichment profiles
# Compare each pair of REGIMEs
profile_vectors = []
for regime in REGIME_ORDER:
    vec = [regime_enrichment_profiles[regime].get(cls, 0) for cls in sorted(GATEKEEPER_CLASSES)]
    profile_vectors.append(vec)

cross_regime_rhos = []
for i in range(len(REGIME_ORDER)):
    for j in range(i + 1, len(REGIME_ORDER)):
        rho_ij, _ = stats.spearmanr(profile_vectors[i], profile_vectors[j])
        cross_regime_rhos.append(float(rho_ij))

mean_cross_rho = float(np.mean(cross_regime_rhos)) if cross_regime_rhos else None
print(f"\n  Cross-regime enrichment profile correlations: {[f'{r:.2f}' for r in cross_regime_rhos]}")
print(f"  Mean cross-REGIME rho: {mean_cross_rho:.3f}" if mean_cross_rho else "  Insufficient data")
if mean_cross_rho and mean_cross_rho > 0.8:
    print("  -> Gatekeeper pattern is REGIME-INVARIANT (structural)")
elif mean_cross_rho and mean_cross_rho > 0.5:
    print("  -> Gatekeeper pattern is partially REGIME-stable")
else:
    print("  -> Gatekeeper pattern varies by REGIME (contextual)")

t5_result = {
    'per_regime': t5_per_regime,
    'enrichment_profiles': {regime: {str(k): float(v) for k, v in prof.items()}
                            for regime, prof in regime_enrichment_profiles.items()},
    'cross_regime_rhos': cross_regime_rhos,
    'mean_cross_regime_rho': mean_cross_rho,
}


# =============================================================================
# T6: HUB SUB-ROLE COMPOSITION
# =============================================================================

print("\n" + "=" * 70)
print("T6: HUB SUB-ROLE COMPOSITION (C1000 mapping)")
print("=" * 70)

# Map exit-boundary vs mid-run tokens to HUB sub-roles
gk_subroles = defaultdict(int)
nongk_subroles = defaultdict(int)
gk_total_mapped = 0
nongk_total_mapped = 0

for r in axm_runs:
    if r['length'] < 3:
        continue
    # Exit boundary (last token)
    mid_last = r['middles'][-1]
    sr = MIDDLE_TO_SUBROLE.get(mid_last)
    if sr:
        gk_subroles[sr] += 1
        gk_total_mapped += 1
    # Mid-run tokens
    for mid in r['middles'][1:-1]:
        sr = MIDDLE_TO_SUBROLE.get(mid)
        if sr:
            nongk_subroles[sr] += 1
            nongk_total_mapped += 1

print(f"\n  Exit-boundary tokens mapped to sub-role: {gk_total_mapped}")
print(f"  Mid-run tokens mapped to sub-role: {nongk_total_mapped}")

all_subroles = ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']
print(f"\n  {'Sub-role':<20} {'Exit-boundary':<16} {'Mid-run':<16}")
for sr in all_subroles:
    gk_f = gk_subroles[sr] / gk_total_mapped if gk_total_mapped > 0 else 0
    ng_f = nongk_subroles[sr] / nongk_total_mapped if nongk_total_mapped > 0 else 0
    print(f"  {sr:<20} {gk_f:<16.3f} {ng_f:<16.3f}")

# Chi-squared: sub-role distribution at exit boundary vs mid-run
sr_exit_v = np.array([gk_subroles.get(sr, 0) for sr in all_subroles])
sr_mid_v = np.array([nongk_subroles.get(sr, 0) for sr in all_subroles])
nz_sr = (sr_exit_v + sr_mid_v) > 0
if nz_sr.sum() >= 3:
    cont_sr = np.array([sr_exit_v[nz_sr], sr_mid_v[nz_sr]])
    chi2_t6, p_t6, dof_t6, _ = stats.chi2_contingency(cont_sr)
    subrole_enriched = bool(p_t6 < 0.05)
    print(f"\n  Chi2 (exit-boundary vs mid-run sub-role dist): chi2={chi2_t6:.2f}, p={p_t6:.4f}")
    if subrole_enriched:
        print("  -> Exit-boundary tokens have DIFFERENT sub-role composition")
    else:
        print("  -> Sub-role composition is same at boundaries and mid-run")
else:
    chi2_t6, p_t6 = None, None
    subrole_enriched = False

t6_result = {
    'exit_boundary_subroles': {sr: int(gk_subroles.get(sr, 0)) for sr in all_subroles},
    'midrun_subroles': {sr: int(nongk_subroles.get(sr, 0)) for sr in all_subroles},
    'exit_boundary_total': gk_total_mapped,
    'midrun_total': nongk_total_mapped,
    'chi2': float(chi2_t6) if chi2_t6 is not None else None,
    'p': float(p_t6) if p_t6 is not None else None,
    'subrole_enriched': subrole_enriched,
}


# =============================================================================
# T7: TRANSITION ENTROPY (Successor Predictability)
# =============================================================================

print("\n" + "=" * 70)
print("T7: TRANSITION ENTROPY (Successor Predictability)")
print("=" * 70)

# For each AXM class, compute Shannon entropy of successor class distribution
# (across ALL transitions, not just within runs)
successor_counts = defaultdict(lambda: defaultdict(int))

for folio, lines_dict in folio_lines.items():
    for line_key, tokens in sorted(lines_dict.items()):
        for i in range(len(tokens) - 1):
            if tokens[i]['macro'] == 'AXM':
                successor_counts[tokens[i]['class']][tokens[i + 1]['class']] += 1

def shannon_entropy(count_dict):
    total = sum(count_dict.values())
    if total == 0:
        return 0.0
    probs = np.array([v / total for v in count_dict.values()])
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))

class_entropy = {}
gk_entropies = []
nongk_entropies = []

for cls in AXM_CLASSES:
    h = shannon_entropy(successor_counts[cls])
    n = sum(successor_counts[cls].values())
    class_entropy[cls] = {'entropy': h, 'n_transitions': n}
    if cls in GATEKEEPER_CLASSES:
        gk_entropies.append(h)
    else:
        nongk_entropies.append(h)

print(f"\n  Gatekeeper class transition entropy:")
for cls in sorted(GATEKEEPER_CLASSES):
    info = class_entropy[cls]
    print(f"    Class {cls}: H={info['entropy']:.3f} bits (n={info['n_transitions']})")

print(f"\n  Gatekeeper mean entropy: {np.mean(gk_entropies):.3f}")
print(f"  Non-gatekeeper mean entropy: {np.mean(nongk_entropies):.3f}")

# Mann-Whitney: gatekeeper entropy vs non-gatekeeper entropy
if gk_entropies and nongk_entropies:
    mw_ent, mw_ent_p = stats.mannwhitneyu(gk_entropies, nongk_entropies, alternative='two-sided')
    lower_entropy = bool(mw_ent_p < 0.05 and np.mean(gk_entropies) < np.mean(nongk_entropies))
    print(f"  Mann-Whitney: U={mw_ent:.0f}, p={mw_ent_p:.4f}")
    if lower_entropy:
        print("  -> Gatekeepers have LOWER entropy (more predictable successors = routing switches)")
    elif mw_ent_p < 0.05:
        print("  -> Gatekeepers have HIGHER entropy (less predictable)")
    else:
        print("  -> No entropy difference between gatekeepers and non-gatekeepers")
else:
    mw_ent, mw_ent_p = None, None
    lower_entropy = False

t7_result = {
    'gatekeeper_entropies': {str(cls): class_entropy[cls] for cls in sorted(GATEKEEPER_CLASSES)},
    'gatekeeper_mean_entropy': float(np.mean(gk_entropies)),
    'non_gatekeeper_mean_entropy': float(np.mean(nongk_entropies)),
    'mannwhitney_U': float(mw_ent) if mw_ent is not None else None,
    'mannwhitney_p': float(mw_ent_p) if mw_ent_p is not None else None,
    'gatekeepers_lower_entropy': lower_entropy,
}


# =============================================================================
# T8: APPROACH-TO-BOUNDARY GEOMETRY
# =============================================================================

print("\n" + "=" * 70)
print("T8: APPROACH-TO-BOUNDARY GEOMETRY (radial depth + hazard-target gradient)")
print("=" * 70)

# Compute radial depth per MIDDLE (same method as Phase 326 T3)
# Reconstruct MIDDLE list from Currier A (same ordering as t1_definitive_matrix.py)
all_middles_set = set()
for token in tx.currier_a():
    word = token.word.strip()
    if not word or '*' in word:
        continue
    m = morph.extract(word)
    if m.middle:
        all_middles_set.add(m.middle)
all_middles = sorted(all_middles_set)
mid_to_idx = {m: i for i, m in enumerate(all_middles)}

compat_path = 'phases/DISCRIMINATION_SPACE_DERIVATION/results/t1_compat_matrix.npy'
compat = np.load(compat_path)
eigenvalues, eigenvectors = np.linalg.eigh(compat.astype(float))
idx_sort = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx_sort]
eigenvectors = eigenvectors[:, idx_sort]
n_dims = min(100, len(eigenvalues) - 1)
residual_embedding = eigenvectors[:, 1:n_dims + 1] * np.sqrt(np.abs(eigenvalues[1:n_dims + 1]))
radial_depth = np.linalg.norm(residual_embedding, axis=1)
middle_depth = {all_middles[i]: float(radial_depth[i]) for i in range(len(all_middles))}

print(f"  Radial depth computed for {len(middle_depth)} MIDDLEs")

# For AXM runs length >= 4: compute per-position metrics from end
# Positions: t-4, t-3, t-2, t-1 (where t-1 = last token = exit boundary)
MAX_LOOKBACK = 6
pos_depth = {pos: [] for pos in range(MAX_LOOKBACK)}  # 0 = last, 1 = second-to-last, etc.
pos_haztar = {pos: [] for pos in range(MAX_LOOKBACK)}
pos_gk = {pos: [] for pos in range(MAX_LOOKBACK)}

for r in axm_runs:
    if r['length'] < 4:
        continue
    n = r['length']
    for offset in range(min(MAX_LOOKBACK, n)):
        idx = n - 1 - offset  # from end
        mid = r['middles'][idx]
        cls = r['classes'][idx]

        # Radial depth
        if mid and mid in middle_depth:
            pos_depth[offset].append(middle_depth[mid])

        # Hazard-target flag
        is_ht = 1.0 if (mid and mid in HUB_SUB_ROLES['HAZARD_TARGET']) else 0.0
        pos_haztar[offset].append(is_ht)

        # Gatekeeper flag
        is_gk = 1.0 if cls in GATEKEEPER_CLASSES else 0.0
        pos_gk[offset].append(is_gk)

n_long_runs = sum(1 for r in axm_runs if r['length'] >= 4)
print(f"  AXM runs (length >= 4): {n_long_runs}")

print(f"\n  Position-from-end profiles (0 = exit token):")
print(f"  {'Pos':<6} {'Depth_mean':<12} {'Depth_std':<12} {'HazTar_%':<12} {'GK_%':<12} {'n':<8}")
t8_positions = {}
for pos in range(MAX_LOOKBACK):
    d_arr = pos_depth[pos]
    ht_arr = pos_haztar[pos]
    gk_arr = pos_gk[pos]
    if not d_arr:
        continue
    d_mean = float(np.mean(d_arr))
    d_std = float(np.std(d_arr))
    ht_pct = float(np.mean(ht_arr)) * 100
    gk_pct = float(np.mean(gk_arr)) * 100
    print(f"  t-{pos:<4} {d_mean:<12.4f} {d_std:<12.4f} {ht_pct:<12.1f} {gk_pct:<12.1f} {len(d_arr):<8}")
    t8_positions[f"t-{pos}"] = {
        'depth_mean': d_mean, 'depth_std': d_std,
        'hazard_target_pct': float(np.mean(ht_arr)),
        'gatekeeper_pct': float(np.mean(gk_arr)),
        'n': len(d_arr),
    }

# Spearman: position-from-end vs depth (does depth decrease toward exit?)
positions_flat = []
depths_flat = []
for pos in range(MAX_LOOKBACK):
    for d in pos_depth[pos]:
        positions_flat.append(pos)
        depths_flat.append(d)

if len(positions_flat) > 50:
    rho_depth, p_depth = stats.spearmanr(positions_flat, depths_flat)
    # Positive rho = depth increases with distance from exit = depth DECREASES toward exit
    print(f"\n  Spearman (position-from-end vs depth): rho={rho_depth:+.4f}, p={p_depth:.4f}")
    if rho_depth > 0 and p_depth < 0.05:
        print("  -> Radial depth DECREASES toward exit (approach to hub)")
    elif rho_depth < 0 and p_depth < 0.05:
        print("  -> Radial depth INCREASES toward exit (departure from hub)")
    else:
        print("  -> No significant depth gradient toward exit")
else:
    rho_depth, p_depth = None, None

# Spearman: position-from-end vs hazard-target density
positions_ht = []
ht_flat = []
for pos in range(MAX_LOOKBACK):
    for h in pos_haztar[pos]:
        positions_ht.append(pos)
        ht_flat.append(h)

if len(positions_ht) > 50:
    rho_ht, p_ht = stats.spearmanr(positions_ht, ht_flat)
    # Negative rho = hazard-target decreases with distance = INCREASES toward exit
    print(f"  Spearman (position-from-end vs hazard-target): rho={rho_ht:+.4f}, p={p_ht:.4f}")
    if rho_ht < 0 and p_ht < 0.05:
        print("  -> Hazard-target density INCREASES toward exit (boundary curvature)")
    elif rho_ht > 0 and p_ht < 0.05:
        print("  -> Hazard-target density DECREASES toward exit")
    else:
        print("  -> No significant hazard-target gradient toward exit")
else:
    rho_ht, p_ht = None, None

# Compare exit token (t-0) vs deep interior (t-3 to t-5)
if pos_depth[0] and any(pos_depth[p] for p in range(3, MAX_LOOKBACK)):
    exit_depths = pos_depth[0]
    interior_depths = []
    for p in range(3, MAX_LOOKBACK):
        interior_depths.extend(pos_depth[p])
    if interior_depths:
        mw_depth, mw_depth_p = stats.mannwhitneyu(exit_depths, interior_depths, alternative='two-sided')
        print(f"\n  Exit token depth ({np.mean(exit_depths):.4f}) vs interior depth ({np.mean(interior_depths):.4f})")
        print(f"  Mann-Whitney: U={mw_depth:.0f}, p={mw_depth_p:.4f}")
        depth_curvature = bool(mw_depth_p < 0.05 and np.mean(exit_depths) < np.mean(interior_depths))
        if depth_curvature:
            print("  -> EXIT TOKENS ARE SHALLOWER (closer to hub) -- geometric boundary curvature")
        else:
            print("  -> No depth difference between exit and interior tokens")
    else:
        mw_depth, mw_depth_p = None, None
        depth_curvature = False
else:
    mw_depth, mw_depth_p = None, None
    depth_curvature = False

t8_result = {
    'n_long_runs': n_long_runs,
    'positions': t8_positions,
    'depth_gradient_rho': float(rho_depth) if rho_depth is not None else None,
    'depth_gradient_p': float(p_depth) if p_depth is not None else None,
    'haztarget_gradient_rho': float(rho_ht) if rho_ht is not None else None,
    'haztarget_gradient_p': float(p_ht) if p_ht is not None else None,
    'exit_vs_interior_depth_p': float(mw_depth_p) if mw_depth_p is not None else None,
    'depth_curvature': depth_curvature,
}


# =============================================================================
# T9: AXM INTERNAL SUBGRAPH PROFILING
# =============================================================================

print("\n" + "=" * 70)
print("T9: AXM INTERNAL SUBGRAPH PROFILING (betweenness centrality)")
print("=" * 70)

# Build 32x32 transition matrix within AXM
axm_trans = defaultdict(lambda: defaultdict(int))
axm_total_trans = defaultdict(int)

for folio, lines_dict in folio_lines.items():
    for line_key, tokens in sorted(lines_dict.items()):
        for i in range(len(tokens) - 1):
            if tokens[i]['macro'] == 'AXM' and tokens[i + 1]['macro'] == 'AXM':
                c_from = tokens[i]['class']
                c_to = tokens[i + 1]['class']
                axm_trans[c_from][c_to] += 1
                axm_total_trans[c_from] += 1

# Compute betweenness centrality via shortest paths on transition graph
# Use -log(prob) as edge weight (information-theoretic distance)
active_classes = sorted(set(c for c in AXM_CLASSES if axm_total_trans[c] > 0))
n_active = len(active_classes)
cls_idx = {c: i for i, c in enumerate(active_classes)}

# Build weighted adjacency matrix
adj = np.full((n_active, n_active), np.inf)
for c_from in active_classes:
    total = axm_total_trans[c_from]
    if total == 0:
        continue
    for c_to in active_classes:
        count = axm_trans[c_from].get(c_to, 0)
        if count > 0:
            prob = count / total
            adj[cls_idx[c_from]][cls_idx[c_to]] = -np.log(prob)

print(f"  Active AXM classes: {n_active}")
print(f"  Total internal transitions: {sum(axm_total_trans.values())}")

# Floyd-Warshall for all-pairs shortest paths
dist = adj.copy()
for k in range(n_active):
    for i in range(n_active):
        for j in range(n_active):
            if dist[i][k] + dist[k][j] < dist[i][j]:
                dist[i][j] = dist[i][k] + dist[k][j]

# Betweenness centrality (approximate via shortest paths)
# For each node v, count how many shortest paths pass through v
betweenness = np.zeros(n_active)
for s in range(n_active):
    for t in range(n_active):
        if s == t:
            continue
        if np.isinf(dist[s][t]):
            continue
        # Check each intermediate node
        for v in range(n_active):
            if v == s or v == t:
                continue
            if np.isinf(dist[s][v]) or np.isinf(dist[v][t]):
                continue
            # Does shortest path go through v?
            if abs(dist[s][v] + dist[v][t] - dist[s][t]) < 1e-10:
                betweenness[v] += 1

# Normalize
max_pairs = (n_active - 1) * (n_active - 2)
if max_pairs > 0:
    betweenness /= max_pairs

# Also: PageRank (simple power iteration on transition probability matrix)
pr_matrix = np.zeros((n_active, n_active))
for c_from in active_classes:
    total = axm_total_trans[c_from]
    if total == 0:
        continue
    for c_to in active_classes:
        count = axm_trans[c_from].get(c_to, 0)
        if count > 0:
            pr_matrix[cls_idx[c_from]][cls_idx[c_to]] = count / total

# Power iteration with damping
damping = 0.85
n_iter = 100
pr = np.ones(n_active) / n_active
for _ in range(n_iter):
    pr = (1 - damping) / n_active + damping * pr_matrix.T @ pr

# Results for gatekeeper vs non-gatekeeper classes
gk_betweenness = []
nongk_betweenness = []
gk_pagerank = []
nongk_pagerank = []

print(f"\n  Gatekeeper class centrality:")
print(f"  {'Class':<8} {'Betweenness':<14} {'PageRank':<12} {'InDegree':<12}")
for cls in active_classes:
    i = cls_idx[cls]
    b = float(betweenness[i])
    p = float(pr[i])
    in_degree = sum(1 for c in active_classes if axm_trans[c].get(cls, 0) > 0)

    if cls in GATEKEEPER_CLASSES:
        gk_betweenness.append(b)
        gk_pagerank.append(p)
        print(f"  {cls:<8} {b:<14.4f} {p:<12.4f} {in_degree:<12}")
    else:
        nongk_betweenness.append(b)
        nongk_pagerank.append(p)

# Mann-Whitney: gatekeeper betweenness vs non-gatekeeper
if gk_betweenness and nongk_betweenness:
    mw_bw, mw_bw_p = stats.mannwhitneyu(gk_betweenness, nongk_betweenness, alternative='two-sided')
    gk_higher_bw = bool(mw_bw_p < 0.05 and np.mean(gk_betweenness) > np.mean(nongk_betweenness))
    print(f"\n  Gatekeeper mean betweenness: {np.mean(gk_betweenness):.4f}")
    print(f"  Non-gatekeeper mean betweenness: {np.mean(nongk_betweenness):.4f}")
    print(f"  Mann-Whitney: U={mw_bw:.0f}, p={mw_bw_p:.4f}")
    if gk_higher_bw:
        print("  -> Gatekeepers have HIGHER betweenness (structural bridges/choke points)")
    else:
        print("  -> Gatekeepers do not have higher betweenness")
else:
    mw_bw, mw_bw_p = None, None
    gk_higher_bw = False

# PageRank comparison
if gk_pagerank and nongk_pagerank:
    mw_pr, mw_pr_p = stats.mannwhitneyu(gk_pagerank, nongk_pagerank, alternative='two-sided')
    print(f"\n  Gatekeeper mean PageRank: {np.mean(gk_pagerank):.4f}")
    print(f"  Non-gatekeeper mean PageRank: {np.mean(nongk_pagerank):.4f}")
    print(f"  Mann-Whitney: U={mw_pr:.0f}, p={mw_pr_p:.4f}")
else:
    mw_pr, mw_pr_p = None, None

t9_result = {
    'n_active_classes': n_active,
    'gatekeeper_betweenness': {str(active_classes[i]): float(betweenness[i])
                               for i in range(n_active) if active_classes[i] in GATEKEEPER_CLASSES},
    'gk_mean_betweenness': float(np.mean(gk_betweenness)) if gk_betweenness else None,
    'nongk_mean_betweenness': float(np.mean(nongk_betweenness)) if nongk_betweenness else None,
    'betweenness_mannwhitney_p': float(mw_bw_p) if mw_bw_p is not None else None,
    'gk_higher_betweenness': gk_higher_bw,
    'gatekeeper_pagerank': {str(active_classes[i]): float(pr[i])
                            for i in range(n_active) if active_classes[i] in GATEKEEPER_CLASSES},
    'gk_mean_pagerank': float(np.mean(gk_pagerank)) if gk_pagerank else None,
    'nongk_mean_pagerank': float(np.mean(nongk_pagerank)) if nongk_pagerank else None,
    'pagerank_mannwhitney_p': float(mw_pr_p) if mw_pr_p is not None else None,
}


# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

findings = []

# T1
print(f"\nT1: Entry/exit asymmetry: {'YES' if asymmetric else 'NO'} (p={p_t1:.4f})" if p_t1 else "T1: Insufficient data")
if asymmetric:
    findings.append("Entry and exit boundaries have DIFFERENT class composition (directional gating)")
else:
    findings.append("Entry and exit boundaries have similar class composition (symmetric)")

# T2
print(f"T2: Exit routing dependency: {'YES' if routing_dependent else 'NO'} (p={p_t2:.4f})" if p_t2 else "T2: Insufficient data")
if routing_dependent:
    findings.append("Different gatekeeper classes route to different target states (functional specialization)")
else:
    findings.append("Gatekeeper classes route similarly (no target-state specialization)")

# T3
print(f"T3: Mid-line gating: {'CONFIRMED' if midline_gating else 'NOT CONFIRMED'} (p={p_t3:.4f})" if p_t3 else "T3: Insufficient data")
if midline_gating:
    findings.append("Gatekeeper enrichment survives positional control (genuine gating)")
else:
    findings.append("Gatekeeper enrichment may be positional artifact")

# T4
print(f"T4: Duration prediction: {'YES' if kw_significant else 'NO'} (KW p={kw_p:.4f})" if kw_p else "T4: Insufficient data")
if kw_significant:
    findings.append("Gatekeeper identity predicts AXM run duration")
else:
    findings.append("Gatekeeper identity does not predict run duration")

# T5
regime_sig_count = sum(1 for v in t5_per_regime.values() if v.get('significant', False))
print(f"T5: REGIME invariance: {regime_sig_count}/4 REGIMEs significant, "
      f"mean cross-rho={mean_cross_rho:.3f}" if mean_cross_rho else "T5: Insufficient data")
if mean_cross_rho and mean_cross_rho > 0.8:
    findings.append(f"Gatekeeper pattern is REGIME-invariant (structural, mean rho={mean_cross_rho:.3f})")
elif mean_cross_rho and mean_cross_rho > 0.5:
    findings.append(f"Gatekeeper pattern is partially REGIME-stable (mean rho={mean_cross_rho:.3f})")
else:
    findings.append("Gatekeeper pattern varies by REGIME")

# T6
print(f"T6: Sub-role enrichment: {'YES' if subrole_enriched else 'NO'} (p={p_t6:.4f})" if p_t6 else "T6: Insufficient data")
if subrole_enriched:
    findings.append("Exit-boundary tokens have different HUB sub-role composition (C1000 connection)")
else:
    findings.append("Sub-role composition is same at boundaries and mid-run")

# T7
print(f"T7: Lower gatekeeper entropy: {'YES' if lower_entropy else 'NO'} (p={mw_ent_p:.4f})" if mw_ent_p else "T7: Insufficient data")
if lower_entropy:
    findings.append("Gatekeepers have lower transition entropy (routing switches)")
else:
    findings.append("Gatekeepers do not have lower transition entropy")

# T8
print(f"T8: Depth curvature: {'YES' if depth_curvature else 'NO'} "
      f"(depth rho={rho_depth:+.4f} p={p_depth:.4f})" if rho_depth is not None else "T8: Insufficient data")
if depth_curvature:
    findings.append("AXM runs drift toward SHALLOWER depth before exit (geometric boundary curvature)")
elif rho_depth is not None and p_depth < 0.05:
    findings.append(f"Depth gradient toward exit (rho={rho_depth:+.3f}, p={p_depth:.4f})")
else:
    findings.append("No significant depth gradient toward AXM exit")

ht_gradient = rho_ht is not None and rho_ht < 0 and p_ht < 0.05
if ht_gradient:
    findings.append(f"Hazard-target density INCREASES toward exit (rho={rho_ht:+.3f}, p={p_ht:.4f})")
else:
    findings.append("No significant hazard-target gradient toward exit")

# T9
print(f"T9: Gatekeeper betweenness: {'HIGHER' if gk_higher_bw else 'NOT HIGHER'} "
      f"(p={mw_bw_p:.4f})" if mw_bw_p is not None else "T9: Insufficient data")
if gk_higher_bw:
    findings.append("Gatekeepers have higher betweenness centrality (structural bridges)")
else:
    findings.append("Gatekeepers do not have higher betweenness centrality")

print(f"\nTotal findings: {len(findings)}")
for fi, f in enumerate(findings, 1):
    print(f"  {fi}. {f}")


# -- Save results -------------------------------------------------------------

results = {
    'phase': 'AXM_GATEKEEPER_INVESTIGATION',
    'n_axm_runs': len(axm_runs),
    'n_axm_exits': len(axm_exits),
    'gatekeeper_classes': sorted(GATEKEEPER_CLASSES),
    'T1_entry_exit_asymmetry': t1_result,
    'T2_exit_routing': t2_result,
    'T3_positional_confound': t3_result,
    'T4_run_length_prediction': t4_result,
    'T5_regime_invariance': t5_result,
    'T6_hub_subrole': t6_result,
    'T7_transition_entropy': t7_result,
    'T8_boundary_geometry': t8_result,
    'T9_subgraph_profiling': t9_result,
    'findings': findings,
}

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'gatekeeper_analysis.json')
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")
