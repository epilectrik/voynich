"""
14_cross_line_mode_dynamics.py

Test whether FL LOW->HIGH mode dynamics operate beyond the line level.

Questions:
1. Line-to-line: does last FL mode in line N predict first FL mode in line N+1?
2. Paragraph-level: does LOW/HIGH ratio shift across lines within a paragraph?
3. Folio-level: does LOW/HIGH ratio shift across paragraphs within a folio?
4. Does it reset at paragraph or folio boundaries?
"""
import sys
import json
import statistics
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr

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
# Step 1: Build FL records and assign modes (same as script 13)
# ============================================================
line_tokens = defaultdict(list)
token_list = []
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)
    token_list.append(t)

# Collect positions per MIDDLE for GMM fitting
per_middle_positions = defaultdict(list)
fl_records = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            per_middle_positions[m.middle].append(idx / (n - 1))
            fl_records.append({
                'word': t.word,
                'middle': m.middle,
                'stage': FL_STAGE_MAP[m.middle][0],
                'actual_pos': idx / (n - 1),
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
                'par_initial': t.par_initial,
                'line_key': line_key,
                'idx': idx,
            })

# Fit GMMs
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

# Assign modes
for r in fl_records:
    mid = r['middle']
    if mid in gmm_models:
        info = gmm_models[mid]
        pred = info['model'].predict(np.array([[r['actual_pos']]]))[0]
        if info['swap']:
            pred = 1 - pred
        r['mode'] = 'LOW' if pred == 0 else 'HIGH'
    else:
        r['mode'] = 'UNKNOWN'

assigned = [r for r in fl_records if r['mode'] != 'UNKNOWN']
print(f"Mode-assigned FL tokens: {len(assigned)}")

# ============================================================
# Step 2: Organize by folio -> paragraph -> line
# ============================================================
# Group FL tokens by line, preserving order
fl_by_line = defaultdict(list)
for r in assigned:
    fl_by_line[r['line_key']].append(r)

# Sort tokens within each line by position
for key in fl_by_line:
    fl_by_line[key].sort(key=lambda x: x['idx'])

# Build ordered line sequences per folio, inferring paragraph from par_initial
# First, collect all lines per folio with their par_initial flag from original tokens
line_par_initial = {}
for line_key, tokens in line_tokens.items():
    if tokens:
        line_par_initial[line_key] = tokens[0].par_initial

folio_lines = defaultdict(list)  # folio -> [(line_num, para_id, [fl_tokens])]
for line_key, tokens in fl_by_line.items():
    if not tokens:
        continue
    folio = tokens[0]['folio']
    line_num = tokens[0]['line']
    is_par_start = line_par_initial.get(line_key, False)
    folio_lines[folio].append((line_num, is_par_start, tokens))

# Sort by line number and assign paragraph IDs
for folio in folio_lines:
    folio_lines[folio].sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)
    para_id = 0
    for i, (line_num, is_par_start, tokens) in enumerate(folio_lines[folio]):
        if is_par_start and i > 0:
            para_id += 1
        folio_lines[folio][i] = (line_num, para_id, tokens)

# ============================================================
# Step 3: Line-to-line transitions
# ============================================================
print(f"\n{'='*60}")
print("LINE-TO-LINE MODE TRANSITIONS")

# Last mode of line N -> First mode of line N+1
line_to_line = Counter()
line_to_line_same_para = Counter()
line_to_line_cross_para = Counter()

for folio, lines in folio_lines.items():
    for i in range(len(lines) - 1):
        _, para_a, tokens_a = lines[i]
        _, para_b, tokens_b = lines[i + 1]

        if not tokens_a or not tokens_b:
            continue

        last_mode = tokens_a[-1]['mode']
        first_mode = tokens_b[0]['mode']
        transition = f"{last_mode}->{first_mode}"

        line_to_line[transition] += 1
        if para_a == para_b:
            line_to_line_same_para[transition] += 1
        else:
            line_to_line_cross_para[transition] += 1

print("\nAll line-to-line transitions (last FL of line N -> first FL of line N+1):")
total_l2l = sum(line_to_line.values())
for trans, count in sorted(line_to_line.items()):
    print(f"  {trans}: {count:>4} ({count/total_l2l*100:.1f}%)")

# Reset rate: how often does HIGH at end of line -> LOW at start of next?
high_to_low = line_to_line.get('HIGH->LOW', 0)
high_to_high = line_to_line.get('HIGH->HIGH', 0)
high_ends = high_to_low + high_to_high
reset_rate = high_to_low / high_ends if high_ends > 0 else 0

low_to_low = line_to_line.get('LOW->LOW', 0)
low_to_high = line_to_line.get('LOW->HIGH', 0)
low_ends = low_to_low + low_to_high
persist_rate = low_to_low / low_ends if low_ends > 0 else 0

print(f"\n  When line ends HIGH: reset to LOW = {high_to_low}/{high_ends} ({reset_rate:.1%})")
print(f"  When line ends LOW:  stay LOW     = {low_to_low}/{low_ends} ({persist_rate:.1%})")

# Same paragraph vs cross paragraph
print(f"\nSame-paragraph transitions:")
for trans, count in sorted(line_to_line_same_para.items()):
    total = sum(line_to_line_same_para.values())
    print(f"  {trans}: {count:>4} ({count/total*100:.1f}%)")

print(f"\nCross-paragraph transitions:")
for trans, count in sorted(line_to_line_cross_para.items()):
    total = sum(line_to_line_cross_para.values())
    if total > 0:
        print(f"  {trans}: {count:>4} ({count/total*100:.1f}%)")

# Cross-paragraph reset rate
cp_h2l = line_to_line_cross_para.get('HIGH->LOW', 0)
cp_h2h = line_to_line_cross_para.get('HIGH->HIGH', 0)
cp_high_ends = cp_h2l + cp_h2h
cp_reset = cp_h2l / cp_high_ends if cp_high_ends > 0 else 0

sp_h2l = line_to_line_same_para.get('HIGH->LOW', 0)
sp_h2h = line_to_line_same_para.get('HIGH->HIGH', 0)
sp_high_ends = sp_h2l + sp_h2h
sp_reset = sp_h2l / sp_high_ends if sp_high_ends > 0 else 0

print(f"\n  Same-para reset (HIGH->LOW): {sp_h2l}/{sp_high_ends} ({sp_reset:.1%})")
print(f"  Cross-para reset (HIGH->LOW): {cp_h2l}/{cp_high_ends} ({cp_reset:.1%})")

# ============================================================
# Step 4: Paragraph-level mode gradient
# ============================================================
print(f"\n{'='*60}")
print("PARAGRAPH-LEVEL MODE GRADIENT")

# For each paragraph, compute HIGH% per line (normalized line position)
para_gradients = []
for folio, lines in folio_lines.items():
    # Group lines by paragraph
    para_lines = defaultdict(list)
    for line_num, para, tokens in lines:
        para_lines[(folio, para)].append((line_num, tokens))

    for (f, p), p_lines in para_lines.items():
        if len(p_lines) < 3:
            continue
        p_lines.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)

        line_positions = []
        high_pcts = []
        for line_idx, (line_num, tokens) in enumerate(p_lines):
            norm_line_pos = line_idx / (len(p_lines) - 1) if len(p_lines) > 1 else 0.5
            high_n = sum(1 for t in tokens if t['mode'] == 'HIGH')
            total_n = len(tokens)
            high_pct = high_n / total_n if total_n > 0 else 0.5
            line_positions.append(norm_line_pos)
            high_pcts.append(high_pct)

        if len(line_positions) >= 3:
            rho, pval = spearmanr(line_positions, high_pcts)
            if not np.isnan(rho):
                para_gradients.append({
                    'folio': f, 'paragraph': p,
                    'n_lines': len(p_lines),
                    'rho': float(rho), 'p': float(pval),
                    'first_line_high_pct': high_pcts[0],
                    'last_line_high_pct': high_pcts[-1],
                })

if para_gradients:
    rhos = [pg['rho'] for pg in para_gradients]
    sig_positive = sum(1 for pg in para_gradients if pg['rho'] > 0.3 and pg['p'] < 0.05)
    sig_negative = sum(1 for pg in para_gradients if pg['rho'] < -0.3 and pg['p'] < 0.05)

    print(f"  Paragraphs tested: {len(para_gradients)}")
    print(f"  Mean rho (HIGH% vs line position): {statistics.mean(rhos):.3f}")
    print(f"  Median rho: {statistics.median(rhos):.3f}")
    print(f"  Significant positive gradient (rho>0.3, p<0.05): {sig_positive}")
    print(f"  Significant negative gradient (rho<-0.3, p<0.05): {sig_negative}")
    print(f"  Neutral: {len(para_gradients) - sig_positive - sig_negative}")

    # First vs last line HIGH%
    first_line_avg = statistics.mean(pg['first_line_high_pct'] for pg in para_gradients)
    last_line_avg = statistics.mean(pg['last_line_high_pct'] for pg in para_gradients)
    print(f"\n  Avg HIGH% in first line of paragraph: {first_line_avg:.3f}")
    print(f"  Avg HIGH% in last line of paragraph:  {last_line_avg:.3f}")
    print(f"  Shift: {last_line_avg - first_line_avg:+.3f}")

# ============================================================
# Step 5: Folio-level mode gradient
# ============================================================
print(f"\n{'='*60}")
print("FOLIO-LEVEL MODE GRADIENT")

folio_gradients = []
for folio, lines in folio_lines.items():
    if len(lines) < 5:
        continue

    line_positions = []
    high_pcts = []
    for line_idx, (line_num, para, tokens) in enumerate(lines):
        norm_pos = line_idx / (len(lines) - 1) if len(lines) > 1 else 0.5
        high_n = sum(1 for t in tokens if t['mode'] == 'HIGH')
        total_n = len(tokens)
        high_pct = high_n / total_n if total_n > 0 else 0.5
        line_positions.append(norm_pos)
        high_pcts.append(high_pct)

    rho, pval = spearmanr(line_positions, high_pcts)
    folio_gradients.append({
        'folio': folio,
        'n_lines': len(lines),
        'rho': float(rho), 'p': float(pval),
        'first_quarter_high': statistics.mean(high_pcts[:len(high_pcts)//4+1]),
        'last_quarter_high': statistics.mean(high_pcts[-(len(high_pcts)//4+1):]),
    })

if folio_gradients:
    rhos = [fg['rho'] for fg in folio_gradients]
    sig_positive = sum(1 for fg in folio_gradients if fg['rho'] > 0.3 and fg['p'] < 0.05)
    sig_negative = sum(1 for fg in folio_gradients if fg['rho'] < -0.3 and fg['p'] < 0.05)

    print(f"  Folios tested: {len(folio_gradients)}")
    print(f"  Mean rho (HIGH% vs line position): {statistics.mean(rhos):.3f}")
    print(f"  Median rho: {statistics.median(rhos):.3f}")
    print(f"  Significant positive gradient: {sig_positive}")
    print(f"  Significant negative gradient: {sig_negative}")

    first_q_avg = statistics.mean(fg['first_quarter_high'] for fg in folio_gradients)
    last_q_avg = statistics.mean(fg['last_quarter_high'] for fg in folio_gradients)
    print(f"\n  Avg HIGH% in first quarter of folio: {first_q_avg:.3f}")
    print(f"  Avg HIGH% in last quarter of folio:  {last_q_avg:.3f}")
    print(f"  Shift: {last_q_avg - first_q_avg:+.3f}")

    # Top 5 most positive and most negative folios
    sorted_fg = sorted(folio_gradients, key=lambda x: x['rho'])
    print(f"\n  Most negative gradient folios (HIGH% decreases):")
    for fg in sorted_fg[:5]:
        print(f"    {fg['folio']}: rho={fg['rho']:.3f}, p={fg['p']:.3f}, n={fg['n_lines']}")
    print(f"\n  Most positive gradient folios (HIGH% increases):")
    for fg in sorted_fg[-5:]:
        print(f"    {fg['folio']}: rho={fg['rho']:.3f}, p={fg['p']:.3f}, n={fg['n_lines']}")

# ============================================================
# Step 6: Mode at paragraph boundaries
# ============================================================
print(f"\n{'='*60}")
print("PARAGRAPH BOUNDARY ANALYSIS")

# First FL token mode in first line of each paragraph
para_first_modes = Counter()
para_last_modes = Counter()

for folio, lines in folio_lines.items():
    para_groups = defaultdict(list)
    for line_num, para, tokens in lines:
        para_groups[(folio, para)].append((line_num, tokens))

    for (f, p), p_lines in para_groups.items():
        p_lines.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0)
        if p_lines:
            first_tokens = p_lines[0][1]
            last_tokens = p_lines[-1][1]
            if first_tokens:
                para_first_modes[first_tokens[0]['mode']] += 1
            if last_tokens:
                para_last_modes[last_tokens[-1]['mode']] += 1

print(f"  First FL token of paragraph:")
for mode, count in para_first_modes.most_common():
    total = sum(para_first_modes.values())
    print(f"    {mode}: {count} ({count/total*100:.1f}%)")

print(f"  Last FL token of paragraph:")
for mode, count in para_last_modes.most_common():
    total = sum(para_last_modes.values())
    print(f"    {mode}: {count} ({count/total*100:.1f}%)")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")

# Determine reset behavior
reset_at_line = reset_rate > 0.60
reset_at_para = cp_reset > sp_reset + 0.10 if cp_high_ends > 10 else False

# Determine gradient behavior
para_gradient_exists = (statistics.mean([pg['rho'] for pg in para_gradients]) > 0.1
                        if para_gradients else False)
folio_gradient_exists = (statistics.mean([fg['rho'] for fg in folio_gradients]) > 0.1
                         if folio_gradients else False)

if reset_at_line and not para_gradient_exists:
    verdict = "LINE_LEVEL_RESET"
    explanation = (f"HIGH->LOW reset rate = {reset_rate:.0%} at line boundaries. "
                   f"No paragraph-level accumulation. "
                   f"LOW->HIGH is a per-line process that resets each line.")
elif para_gradient_exists and not folio_gradient_exists:
    verdict = "PARAGRAPH_LEVEL_ACCUMULATION"
    explanation = (f"HIGH% increases across paragraph (mean rho={statistics.mean([pg['rho'] for pg in para_gradients]):.3f}). "
                   f"No folio-level gradient. Process accumulates within paragraphs, "
                   f"resets at paragraph boundaries.")
elif folio_gradient_exists:
    verdict = "FOLIO_LEVEL_ACCUMULATION"
    explanation = (f"HIGH% increases across folio (mean rho={statistics.mean([fg['rho'] for fg in folio_gradients]):.3f}). "
                   f"LOW->HIGH accumulates across the entire program.")
elif not reset_at_line and not para_gradient_exists:
    verdict = "NO_CLEAR_DYNAMICS"
    explanation = (f"Reset rate = {reset_rate:.0%}, no paragraph/folio gradient. "
                   f"Mode transitions don't follow a hierarchical pattern.")
else:
    verdict = "MIXED_DYNAMICS"
    explanation = (f"Reset rate = {reset_rate:.0%}, "
                   f"para gradient mean rho = {statistics.mean([pg['rho'] for pg in para_gradients]):.3f}, "
                   f"folio gradient mean rho = {statistics.mean([fg['rho'] for fg in folio_gradients]):.3f}")

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_assigned': len(assigned),
    'line_to_line_transitions': dict(line_to_line),
    'same_para_transitions': dict(line_to_line_same_para),
    'cross_para_transitions': dict(line_to_line_cross_para),
    'reset_rate_overall': round(reset_rate, 4),
    'reset_rate_same_para': round(sp_reset, 4),
    'reset_rate_cross_para': round(cp_reset, 4),
    'paragraph_gradients': {
        'n_tested': len(para_gradients),
        'mean_rho': round(statistics.mean([pg['rho'] for pg in para_gradients]), 4) if para_gradients else None,
        'median_rho': round(statistics.median([pg['rho'] for pg in para_gradients]), 4) if para_gradients else None,
        'first_line_avg_high_pct': round(first_line_avg, 4) if para_gradients else None,
        'last_line_avg_high_pct': round(last_line_avg, 4) if para_gradients else None,
    },
    'folio_gradients': {
        'n_tested': len(folio_gradients),
        'mean_rho': round(statistics.mean([fg['rho'] for fg in folio_gradients]), 4) if folio_gradients else None,
        'median_rho': round(statistics.median([fg['rho'] for fg in folio_gradients]), 4) if folio_gradients else None,
        'first_q_avg_high_pct': round(first_q_avg, 4) if folio_gradients else None,
        'last_q_avg_high_pct': round(last_q_avg, 4) if folio_gradients else None,
        'per_folio': folio_gradients,
    },
    'paragraph_boundaries': {
        'first_token_modes': dict(para_first_modes),
        'last_token_modes': dict(para_last_modes),
    },
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "14_cross_line_mode_dynamics.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
