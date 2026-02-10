"""
18_paragraph_synchronization.py

Test for paragraph-level synchronization of FL modes.
If lines are parallel control loops, paragraph boundaries should show:
1. Stage convergence at paragraph-final lines
2. Stage reset at paragraph-initial lines
3. FL MIDDLE diversity within paragraphs (different parameters)
4. FL MIDDLE convergence at boundaries
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import mannwhitneyu, kruskal

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': ('INITIAL', 0.299), 'i': ('INITIAL', 0.345),
    'in': ('EARLY', 0.421),
    'r': ('MEDIAL', 0.507), 'ar': ('MEDIAL', 0.545),
    'al': ('LATE', 0.606), 'l': ('LATE', 0.618), 'ol': ('LATE', 0.643),
    'o': ('FINAL', 0.751), 'ly': ('FINAL', 0.785), 'am': ('FINAL', 0.802),
    'm': ('TERMINAL', 0.861), 'dy': ('TERMINAL', 0.908),
    'ry': ('TERMINAL', 0.913), 'y': ('TERMINAL', 0.942),
}
STAGE_ORDER = {'INITIAL': 0, 'EARLY': 1, 'MEDIAL': 2, 'LATE': 3, 'FINAL': 4, 'TERMINAL': 5}

MIN_N = 50
tx = Transcript()
morph = Morphology()

# ============================================================
# Collect tokens by line, assign paragraphs
# ============================================================
line_tokens = defaultdict(list)
line_meta = {}  # (folio, line) -> {par_initial, par_final, ...}

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'par_initial': t.par_initial, 'par_final': t.par_final}
    # Update if any token in line is par_initial/par_final
    if t.par_initial:
        line_meta[key]['par_initial'] = True
    if t.par_final:
        line_meta[key]['par_final'] = True

# Build paragraph structure: group lines into paragraphs
folio_lines = defaultdict(list)
for key in sorted(line_tokens.keys()):
    folio_lines[key[0]].append(key)

paragraphs = []  # list of (folio, [line_keys])
for folio, lines in folio_lines.items():
    current_para = []
    for lk in lines:
        current_para.append(lk)
        if line_meta[lk].get('par_final', False):
            paragraphs.append((folio, list(current_para)))
            current_para = []
    if current_para:
        paragraphs.append((folio, list(current_para)))

print(f"Paragraphs: {len(paragraphs)}")
print(f"Lines: {len(line_tokens)}")

# ============================================================
# Fit GMMs and build FL position model
# ============================================================
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))

gmm_models = {}
for mid, positions in per_middle_positions.items():
    if len(positions) < MIN_N:
        continue
    X = np.array(positions).reshape(-1, 1)
    gmm = GaussianMixture(n_components=2, random_state=42, n_init=10)
    gmm.fit(X)
    if gmm.means_[0] > gmm.means_[1]:
        gmm_models[mid] = {'model': gmm, 'swap': True}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False}

# ============================================================
# Annotate each line's FL tokens
# ============================================================
def get_line_fl_info(tokens):
    """Return FL info for a line: list of (middle, stage, stage_num, mode, pos)"""
    n = len(tokens)
    if n <= 1:
        return []
    fl_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            mid = m.middle
            pos = idx / (n - 1)
            stage_name = FL_STAGE_MAP[mid][0]
            stage_num = STAGE_ORDER[stage_name]

            mode = None
            if mid in gmm_models:
                info = gmm_models[mid]
                pred = info['model'].predict(np.array([[pos]]))[0]
                if info['swap']:
                    pred = 1 - pred
                mode = 'LOW' if pred == 0 else 'HIGH'

            fl_info.append({
                'middle': mid,
                'stage': stage_name,
                'stage_num': stage_num,
                'mode': mode,
                'pos': pos,
            })
    return fl_info

# ============================================================
# Test 1: Stage convergence at paragraph boundaries
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: STAGE DISTRIBUTION BY PARAGRAPH POSITION")
print(f"{'='*60}")

# For each paragraph, classify lines as: FIRST, LAST, MIDDLE
boundary_stages = {'first': [], 'last': [], 'interior': []}
boundary_middles = {'first': [], 'last': [], 'interior': []}

for folio, para_lines in paragraphs:
    if len(para_lines) < 3:
        continue  # Need at least 3 lines to have interior

    for i, lk in enumerate(para_lines):
        fl_info = get_line_fl_info(line_tokens[lk])
        if not fl_info:
            continue

        if i == 0:
            pos_type = 'first'
        elif i == len(para_lines) - 1:
            pos_type = 'last'
        else:
            pos_type = 'interior'

        for fi in fl_info:
            boundary_stages[pos_type].append(fi['stage_num'])
            boundary_middles[pos_type].append(fi['middle'])

for pos_type in ['first', 'last', 'interior']:
    stages = boundary_stages[pos_type]
    if stages:
        mean_stage = np.mean(stages)
        std_stage = np.std(stages)
        n = len(stages)
        print(f"  {pos_type:>8}: n={n:>5}, mean_stage={mean_stage:.2f}, std={std_stage:.2f}")

# Test: is variance lower at boundaries?
if boundary_stages['first'] and boundary_stages['last'] and boundary_stages['interior']:
    first_std = np.std(boundary_stages['first'])
    last_std = np.std(boundary_stages['last'])
    interior_std = np.std(boundary_stages['interior'])

    boundary_all = boundary_stages['first'] + boundary_stages['last']
    stat, p_val = mannwhitneyu(boundary_all, boundary_stages['interior'], alternative='two-sided')
    print(f"\n  Boundary vs Interior stage: U={stat:.0f}, p={p_val:.4f}")
    print(f"  First std={first_std:.3f}, Last std={last_std:.3f}, Interior std={interior_std:.3f}")

# ============================================================
# Test 2: FL MIDDLE diversity within paragraphs
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: FL MIDDLE DIVERSITY WITHIN PARAGRAPHS")
print(f"{'='*60}")

para_middle_diversity = []
para_sizes = []
for folio, para_lines in paragraphs:
    if len(para_lines) < 3:
        continue

    all_middles = []
    middles_per_line = []
    for lk in para_lines:
        fl_info = get_line_fl_info(line_tokens[lk])
        line_middles = set(fi['middle'] for fi in fl_info)
        middles_per_line.append(line_middles)
        all_middles.extend(fi['middle'] for fi in fl_info)

    if not all_middles:
        continue

    unique_middles = len(set(all_middles))
    total_fl = len(all_middles)
    diversity = unique_middles / total_fl if total_fl > 0 else 0

    para_middle_diversity.append({
        'n_lines': len(para_lines),
        'total_fl': total_fl,
        'unique_middles': unique_middles,
        'diversity': diversity,
    })
    para_sizes.append(len(para_lines))

if para_middle_diversity:
    diversities = [p['diversity'] for p in para_middle_diversity]
    print(f"  Paragraphs analyzed: {len(para_middle_diversity)}")
    print(f"  Mean MIDDLE diversity: {np.mean(diversities):.3f}")
    print(f"  Median MIDDLE diversity: {np.median(diversities):.3f}")
    print(f"  Mean unique MIDDLEs per paragraph: {np.mean([p['unique_middles'] for p in para_middle_diversity]):.1f}")

# ============================================================
# Test 3: Consecutive line MIDDLE overlap
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: CONSECUTIVE LINE MIDDLE OVERLAP")
print(f"{'='*60}")

within_para_overlaps = []
cross_para_overlaps = []

for folio, para_lines in paragraphs:
    if len(para_lines) < 2:
        continue

    line_middle_sets = []
    for lk in para_lines:
        fl_info = get_line_fl_info(line_tokens[lk])
        middles = set(fi['middle'] for fi in fl_info)
        line_middle_sets.append(middles)

    # Within-paragraph consecutive overlap
    for i in range(len(line_middle_sets) - 1):
        if line_middle_sets[i] and line_middle_sets[i+1]:
            intersection = line_middle_sets[i] & line_middle_sets[i+1]
            union = line_middle_sets[i] | line_middle_sets[i+1]
            jaccard = len(intersection) / len(union) if union else 0
            within_para_overlaps.append(jaccard)

# Cross-paragraph: last line of para N vs first line of para N+1 (same folio)
folio_paras = defaultdict(list)
for folio, para_lines in paragraphs:
    folio_paras[folio].append(para_lines)

for folio, paras in folio_paras.items():
    for i in range(len(paras) - 1):
        last_line = paras[i][-1]
        first_line = paras[i+1][0]

        fl_last = get_line_fl_info(line_tokens[last_line])
        fl_first = get_line_fl_info(line_tokens[first_line])

        middles_last = set(fi['middle'] for fi in fl_last)
        middles_first = set(fi['middle'] for fi in fl_first)

        if middles_last and middles_first:
            intersection = middles_last & middles_first
            union = middles_last | middles_first
            jaccard = len(intersection) / len(union) if union else 0
            cross_para_overlaps.append(jaccard)

if within_para_overlaps and cross_para_overlaps:
    print(f"  Within-paragraph consecutive Jaccard: {np.mean(within_para_overlaps):.3f} (n={len(within_para_overlaps)})")
    print(f"  Cross-paragraph boundary Jaccard:     {np.mean(cross_para_overlaps):.3f} (n={len(cross_para_overlaps)})")

    if len(within_para_overlaps) >= 10 and len(cross_para_overlaps) >= 10:
        stat, p_val = mannwhitneyu(within_para_overlaps, cross_para_overlaps, alternative='two-sided')
        print(f"  Mann-Whitney U: U={stat:.0f}, p={p_val:.4f}")

# ============================================================
# Test 4: Mode composition at paragraph positions
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: MODE COMPOSITION BY PARAGRAPH POSITION")
print(f"{'='*60}")

# For each paragraph position (normalized 0-1), what % of FL tokens are LOW?
position_mode = defaultdict(list)  # normalized position -> list of (0=LOW, 1=HIGH)

for folio, para_lines in paragraphs:
    n_lines = len(para_lines)
    if n_lines < 3:
        continue

    for i, lk in enumerate(para_lines):
        norm_pos = i / (n_lines - 1)
        fl_info = get_line_fl_info(line_tokens[lk])
        for fi in fl_info:
            if fi['mode'] == 'LOW':
                position_mode[round(norm_pos, 1)].append(0)
            elif fi['mode'] == 'HIGH':
                position_mode[round(norm_pos, 1)].append(1)

print(f"  {'Para pos':>8} {'n':>6} {'%LOW':>7} {'%HIGH':>7}")
print(f"  {'-'*35}")
for pos in sorted(position_mode.keys()):
    modes = position_mode[pos]
    n = len(modes)
    if n < 20:
        continue
    low_pct = (1 - np.mean(modes)) * 100
    high_pct = np.mean(modes) * 100
    print(f"  {pos:>8.1f} {n:>6} {low_pct:>6.1f}% {high_pct:>6.1f}%")

# ============================================================
# Test 5: Stage variance within paragraphs — convergence at end?
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: STAGE VARIANCE BY PARAGRAPH POSITION")
print(f"{'='*60}")

# For each line within a paragraph, compute stage variance of FL tokens
# Then see if it decreases toward paragraph end
position_stage_vars = defaultdict(list)

for folio, para_lines in paragraphs:
    n_lines = len(para_lines)
    if n_lines < 4:
        continue

    for i, lk in enumerate(para_lines):
        fl_info = get_line_fl_info(line_tokens[lk])
        if len(fl_info) < 2:
            continue
        stages = [fi['stage_num'] for fi in fl_info]
        stage_var = np.var(stages)

        # Classify as first-quarter, middle-half, last-quarter
        frac = i / (n_lines - 1)
        if frac <= 0.25:
            bin_name = 'first_quarter'
        elif frac >= 0.75:
            bin_name = 'last_quarter'
        else:
            bin_name = 'middle_half'

        position_stage_vars[bin_name].append(stage_var)

for bin_name in ['first_quarter', 'middle_half', 'last_quarter']:
    vals = position_stage_vars.get(bin_name, [])
    if vals:
        print(f"  {bin_name:>15}: n={len(vals):>4}, mean_var={np.mean(vals):.3f}, median_var={np.median(vals):.3f}")

if position_stage_vars.get('first_quarter') and position_stage_vars.get('last_quarter'):
    stat, p_val = mannwhitneyu(
        position_stage_vars['first_quarter'],
        position_stage_vars['last_quarter'],
        alternative='two-sided'
    )
    print(f"  First vs Last quarter: U={stat:.0f}, p={p_val:.4f}")

# ============================================================
# Test 6: Do paragraph-final lines use TERMINAL stages more?
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: TERMINAL STAGE CONCENTRATION")
print(f"{'='*60}")

terminal_rates = {'first': [], 'last': [], 'interior': []}

for folio, para_lines in paragraphs:
    if len(para_lines) < 3:
        continue

    for i, lk in enumerate(para_lines):
        fl_info = get_line_fl_info(line_tokens[lk])
        if not fl_info:
            continue

        terminal_count = sum(1 for fi in fl_info if fi['stage'] in ('TERMINAL', 'FINAL'))
        rate = terminal_count / len(fl_info)

        if i == 0:
            terminal_rates['first'].append(rate)
        elif i == len(para_lines) - 1:
            terminal_rates['last'].append(rate)
        else:
            terminal_rates['interior'].append(rate)

for pos_type in ['first', 'last', 'interior']:
    rates = terminal_rates[pos_type]
    if rates:
        print(f"  {pos_type:>8}: mean TERMINAL+FINAL rate = {np.mean(rates):.3f} (n={len(rates)})")

if terminal_rates['first'] and terminal_rates['last']:
    stat, p_val = mannwhitneyu(terminal_rates['first'], terminal_rates['last'], alternative='two-sided')
    print(f"  First vs Last: U={stat:.0f}, p={p_val:.4f}")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")

# Gather evidence
sync_evidence = []

# Check MIDDLE overlap difference
if within_para_overlaps and cross_para_overlaps:
    within_mean = np.mean(within_para_overlaps)
    cross_mean = np.mean(cross_para_overlaps)
    if within_mean > cross_mean + 0.05:
        sync_evidence.append("MIDDLE_REUSE_WITHIN_PARA")
    elif cross_mean > within_mean + 0.05:
        sync_evidence.append("MIDDLE_SWITCH_AT_BOUNDARY")

# Check stage convergence at boundaries
if boundary_stages['last'] and boundary_stages['interior']:
    last_std = np.std(boundary_stages['last'])
    interior_std = np.std(boundary_stages['interior'])
    if last_std < interior_std - 0.1:
        sync_evidence.append("STAGE_CONVERGENCE_AT_END")

# Check terminal concentration
if terminal_rates['last'] and terminal_rates['first']:
    last_term = np.mean(terminal_rates['last'])
    first_term = np.mean(terminal_rates['first'])
    if last_term > first_term + 0.05:
        sync_evidence.append("TERMINAL_CONCENTRATION_AT_END")

# Check mode gradient across paragraph
if position_mode:
    sorted_positions = sorted(position_mode.keys())
    if len(sorted_positions) >= 3:
        early_modes = position_mode.get(0.0, []) + position_mode.get(0.1, [])
        late_modes = position_mode.get(0.9, []) + position_mode.get(1.0, [])
        if early_modes and late_modes:
            early_high = np.mean(early_modes)
            late_high = np.mean(late_modes)
            if late_high > early_high + 0.05:
                sync_evidence.append("MODE_GRADIENT_ACROSS_PARAGRAPH")

if len(sync_evidence) >= 3:
    verdict = "PARALLEL_WITH_SYNC"
    explanation = f"Evidence of paragraph-level synchronization: {sync_evidence}"
elif len(sync_evidence) >= 1:
    verdict = "WEAK_SYNC"
    explanation = f"Some synchronization signals: {sync_evidence}"
else:
    verdict = "NO_SYNC"
    explanation = "No evidence of paragraph-level synchronization"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")
print(f"  Sync evidence count: {len(sync_evidence)}/4")

# ============================================================
# Save results
# ============================================================
result = {
    'n_paragraphs': len(paragraphs),
    'n_lines': len(line_tokens),
    'boundary_stages': {
        pos: {'n': len(stages), 'mean': round(float(np.mean(stages)), 3),
              'std': round(float(np.std(stages)), 3)}
        for pos, stages in boundary_stages.items() if stages
    },
    'middle_diversity': {
        'mean': round(float(np.mean(diversities)), 3) if para_middle_diversity else None,
        'median': round(float(np.median(diversities)), 3) if para_middle_diversity else None,
    },
    'consecutive_overlap': {
        'within_para_jaccard': round(float(np.mean(within_para_overlaps)), 3) if within_para_overlaps else None,
        'cross_para_jaccard': round(float(np.mean(cross_para_overlaps)), 3) if cross_para_overlaps else None,
    },
    'terminal_concentration': {
        pos: round(float(np.mean(rates)), 3)
        for pos, rates in terminal_rates.items() if rates
    },
    'sync_evidence': sync_evidence,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "18_paragraph_synchronization.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
