"""
33_coordinate_determinants.py

What determines a line's FL coordinate (action_level, oversight_level)?

Candidates:
  1. FOLIO identity - does each folio use a restricted set of coordinates?
  2. SECTION - do sections predict coordinates?
  3. LINE POSITION within folio - do early lines differ from late lines?
  4. PARAGRAPH POSITION - first/middle/last line of paragraph?
  5. LINE CONTENT - does the gap vocabulary predict the coordinate?
  6. FOLIO POSITION within section - does folio ordering matter?

For each factor, measure how much of coordinate variance it explains.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, chi2_contingency, kruskal

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
STAGES = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

tx = Transcript()
morph = Morphology()
MIN_N = 50

# Build line tokens and metadata
line_tokens = defaultdict(list)
line_meta = {}
folio_lines = defaultdict(list)  # folio -> list of line keys in order

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {
            'section': t.section, 'folio': t.folio, 'line': t.line,
            'par_initial': False, 'par_final': False,
        }
        folio_lines[t.folio].append(key)
    if t.par_initial:
        line_meta[key]['par_initial'] = True
    if t.par_final:
        line_meta[key]['par_final'] = True

# Deduplicate folio_lines (same key may be appended multiple times)
for f in folio_lines:
    seen = set()
    deduped = []
    for k in folio_lines[f]:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    folio_lines[f] = deduped

# Fit GMMs
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
# Assign coordinates to every line
# ============================================================
line_coords = {}  # line_key -> (low_stage, high_stage, low_ord, high_ord)

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]
            fl_info.append({'mode': mode, 'stage': stage})

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    line_coords[line_key] = (low_stage, high_stage,
                              STAGE_ORDER[low_stage], STAGE_ORDER[high_stage])

print(f"Lines with FL coordinates: {len(line_coords)}")

# ============================================================
# 1. FOLIO as determinant
# ============================================================
print(f"\n{'='*70}")
print("1. FOLIO AS COORDINATE DETERMINANT")
print(f"{'='*70}")

# Per-folio: how many distinct pairs, and how concentrated?
folio_pair_counts = defaultdict(Counter)
for line_key, (ls, hs, lo, ho) in line_coords.items():
    folio = line_meta[line_key]['folio']
    folio_pair_counts[folio][(ls, hs)] += 1

folio_diversities = []
folio_top_pair_pcts = []
folio_n_pairs = []

for folio, pair_counts in folio_pair_counts.items():
    total = sum(pair_counts.values())
    if total < 5:
        continue
    n_unique = len(pair_counts)
    top_pct = pair_counts.most_common(1)[0][1] / total * 100
    folio_diversities.append(n_unique / total)  # normalized diversity
    folio_top_pair_pcts.append(top_pct)
    folio_n_pairs.append(n_unique)

print(f"\n  Mean unique pairs per folio: {np.mean(folio_n_pairs):.1f}")
print(f"  Mean top-pair coverage:      {np.mean(folio_top_pair_pcts):.1f}%")
print(f"  Mean diversity (unique/total):{np.mean(folio_diversities):.3f}")

# Chi-squared: does folio predict LOW stage?
folio_low_table = defaultdict(Counter)
folio_high_table = defaultdict(Counter)
for line_key, (ls, hs, lo, ho) in line_coords.items():
    folio = line_meta[line_key]['folio']
    folio_low_table[folio][ls] += 1
    folio_high_table[folio][hs] += 1

# Build contingency tables (folio x stage) - only folios with enough data
min_folio_lines = 8
good_folios = [f for f in folio_low_table if sum(folio_low_table[f].values()) >= min_folio_lines]

# LOW
low_matrix = []
for f in good_folios:
    row = [folio_low_table[f].get(s, 0) for s in STAGES]
    low_matrix.append(row)
low_matrix = np.array(low_matrix)
# Remove all-zero columns
col_sums = low_matrix.sum(axis=0)
keep_cols = col_sums > 0
low_matrix_clean = low_matrix[:, keep_cols]
if low_matrix_clean.shape[1] >= 2:
    chi2_low, p_low, dof_low, _ = chi2_contingency(low_matrix_clean)
    v_low = np.sqrt(chi2_low / (low_matrix_clean.sum() * (min(low_matrix_clean.shape) - 1)))
    print(f"\n  Folio -> LOW stage: chi2={chi2_low:.1f}, p={p_low:.2e}, V={v_low:.3f}")
else:
    v_low = 0
    p_low = 1
    print(f"\n  Folio -> LOW stage: insufficient variation")

# HIGH
high_matrix = []
for f in good_folios:
    row = [folio_high_table[f].get(s, 0) for s in STAGES]
    high_matrix.append(row)
high_matrix = np.array(high_matrix)
col_sums_h = high_matrix.sum(axis=0)
keep_cols_h = col_sums_h > 0
high_matrix_clean = high_matrix[:, keep_cols_h]
if high_matrix_clean.shape[1] >= 2:
    chi2_high, p_high, dof_high, _ = chi2_contingency(high_matrix_clean)
    v_high = np.sqrt(chi2_high / (high_matrix_clean.sum() * (min(high_matrix_clean.shape) - 1)))
    print(f"  Folio -> HIGH stage: chi2={chi2_high:.1f}, p={p_high:.2e}, V={v_high:.3f}")
else:
    v_high = 0
    p_high = 1
    print(f"  Folio -> HIGH stage: insufficient variation")

# Show 5 most concentrated folios
print(f"\n  Most coordinate-concentrated folios:")
folio_concentration = []
for folio, pair_counts in folio_pair_counts.items():
    total = sum(pair_counts.values())
    if total < 8:
        continue
    top_pair, top_count = pair_counts.most_common(1)[0]
    pct = top_count / total * 100
    folio_concentration.append((folio, top_pair, top_count, total, pct))
folio_concentration.sort(key=lambda x: -x[4])

print(f"  {'Folio':<8} {'TopPair':<14} {'Count':>5}/{' Total':<6} {'%':>5}")
for folio, pair, count, total, pct in folio_concentration[:10]:
    pair_str = f"{pair[0][:4]}>{pair[1][:4]}"
    print(f"  {folio:<8} {pair_str:<14} {count:>5}/{total:<6} {pct:>4.0f}%")

# Show 5 most diverse folios
print(f"\n  Most coordinate-diverse folios:")
folio_concentration.sort(key=lambda x: x[4])
for folio, pair, count, total, pct in folio_concentration[:10]:
    pair_str = f"{pair[0][:4]}>{pair[1][:4]}"
    n_unique = len(folio_pair_counts[folio])
    print(f"  {folio:<8} {n_unique:>2} unique pairs, top={pair_str} at {pct:.0f}%")

# ============================================================
# 2. SECTION as determinant
# ============================================================
print(f"\n{'='*70}")
print("2. SECTION AS COORDINATE DETERMINANT")
print(f"{'='*70}")

section_low = defaultdict(Counter)
section_high = defaultdict(Counter)
section_pair = defaultdict(Counter)

for line_key, (ls, hs, lo, ho) in line_coords.items():
    sec = line_meta[line_key]['section']
    section_low[sec][ls] += 1
    section_high[sec][hs] += 1
    section_pair[sec][(ls, hs)] += 1

print(f"\n  LOW stage distribution by section:")
print(f"  {'Sect':<6}", end='')
for s in STAGES:
    print(f" {s[:4]:>6}", end='')
print(f" {'n':>6}")
print(f"  {'-'*48}")
for sec in sorted(section_low.keys()):
    total = sum(section_low[sec].values())
    print(f"  {sec:<6}", end='')
    for s in STAGES:
        pct = section_low[sec].get(s, 0) / total * 100
        print(f" {pct:>5.1f}%", end='')
    print(f" {total:>6}")

print(f"\n  HIGH stage distribution by section:")
print(f"  {'Sect':<6}", end='')
for s in STAGES:
    print(f" {s[:4]:>6}", end='')
print(f" {'n':>6}")
print(f"  {'-'*48}")
for sec in sorted(section_high.keys()):
    total = sum(section_high[sec].values())
    print(f"  {sec:<6}", end='')
    for s in STAGES:
        pct = section_high[sec].get(s, 0) / total * 100
        print(f" {pct:>5.1f}%", end='')
    print(f" {total:>6}")

# Section chi-squared
sec_low_matrix = []
sec_labels = sorted(section_low.keys())
for sec in sec_labels:
    row = [section_low[sec].get(s, 0) for s in STAGES]
    sec_low_matrix.append(row)
sec_low_matrix = np.array(sec_low_matrix)
col_keep = sec_low_matrix.sum(axis=0) > 0
sec_low_clean = sec_low_matrix[:, col_keep]
if sec_low_clean.shape[0] >= 2 and sec_low_clean.shape[1] >= 2:
    chi2_sl, p_sl, _, _ = chi2_contingency(sec_low_clean)
    v_sl = np.sqrt(chi2_sl / (sec_low_clean.sum() * (min(sec_low_clean.shape) - 1)))
    print(f"\n  Section -> LOW stage: V={v_sl:.3f} (p={p_sl:.2e})")

sec_high_matrix = []
for sec in sec_labels:
    row = [section_high[sec].get(s, 0) for s in STAGES]
    sec_high_matrix.append(row)
sec_high_matrix = np.array(sec_high_matrix)
col_keep_h = sec_high_matrix.sum(axis=0) > 0
sec_high_clean = sec_high_matrix[:, col_keep_h]
if sec_high_clean.shape[0] >= 2 and sec_high_clean.shape[1] >= 2:
    chi2_sh, p_sh, _, _ = chi2_contingency(sec_high_clean)
    v_sh = np.sqrt(chi2_sh / (sec_high_clean.sum() * (min(sec_high_clean.shape) - 1)))
    print(f"  Section -> HIGH stage: V={v_sh:.3f} (p={p_sh:.2e})")

# ============================================================
# 3. LINE POSITION within folio
# ============================================================
print(f"\n{'='*70}")
print("3. LINE POSITION WITHIN FOLIO")
print(f"{'='*70}")

# For each line, compute its relative position within the folio (0=first, 1=last)
line_rel_positions = {}
for folio, keys in folio_lines.items():
    n_lines = len(keys)
    if n_lines <= 1:
        continue
    for idx, key in enumerate(keys):
        if key in line_coords:
            line_rel_positions[key] = idx / (n_lines - 1)

# Correlate line position with LOW and HIGH ordinals
positions = []
low_ords = []
high_ords = []
for key, pos in line_rel_positions.items():
    lo = line_coords[key][2]
    ho = line_coords[key][3]
    positions.append(pos)
    low_ords.append(lo)
    high_ords.append(ho)

rho_pos_low, p_pos_low = spearmanr(positions, low_ords)
rho_pos_high, p_pos_high = spearmanr(positions, high_ords)

print(f"\n  Line position vs LOW stage:  rho={rho_pos_low:+.3f} (p={p_pos_low:.4f})")
print(f"  Line position vs HIGH stage: rho={rho_pos_high:+.3f} (p={p_pos_high:.4f})")

# Bin into thirds
early_lines = [(lo, ho) for key, pos in line_rel_positions.items()
               if pos < 0.33 for lo, ho in [(line_coords[key][2], line_coords[key][3])]]
mid_lines = [(lo, ho) for key, pos in line_rel_positions.items()
             if 0.33 <= pos <= 0.66 for lo, ho in [(line_coords[key][2], line_coords[key][3])]]
late_lines = [(lo, ho) for key, pos in line_rel_positions.items()
              if pos > 0.66 for lo, ho in [(line_coords[key][2], line_coords[key][3])]]

print(f"\n  Folio position thirds:")
print(f"  {'Third':<10} {'n':>5} {'MeanLOW':>8} {'MeanHIGH':>9}")
print(f"  {'-'*35}")
for label, data in [('Early', early_lines), ('Middle', mid_lines), ('Late', late_lines)]:
    if data:
        print(f"  {label:<10} {len(data):>5} {np.mean([d[0] for d in data]):>8.2f} "
              f"{np.mean([d[1] for d in data]):>9.2f}")

# ============================================================
# 4. PARAGRAPH POSITION
# ============================================================
print(f"\n{'='*70}")
print("4. PARAGRAPH POSITION")
print(f"{'='*70}")

# Build paragraphs
paragraphs = []
current_para = []
current_folio = None

# Walk through lines in order
all_line_keys = []
for folio in sorted(folio_lines.keys()):
    all_line_keys.extend(folio_lines[folio])

for key in all_line_keys:
    meta = line_meta[key]
    if meta['par_initial'] and current_para:
        paragraphs.append(current_para)
        current_para = []
    current_para.append(key)
    if meta['par_final']:
        paragraphs.append(current_para)
        current_para = []
if current_para:
    paragraphs.append(current_para)

# For each line, record its paragraph position
line_para_pos = {}  # key -> ('FIRST', 'MIDDLE', 'LAST', 'SOLO')
for para in paragraphs:
    if len(para) == 1:
        line_para_pos[para[0]] = 'SOLO'
    else:
        line_para_pos[para[0]] = 'FIRST'
        line_para_pos[para[-1]] = 'LAST'
        for key in para[1:-1]:
            line_para_pos[key] = 'MIDDLE'

# Compare coordinates by paragraph position
para_pos_coords = defaultdict(list)
for key, (ls, hs, lo, ho) in line_coords.items():
    pp = line_para_pos.get(key, 'UNKNOWN')
    para_pos_coords[pp].append((lo, ho))

print(f"\n  Coordinate means by paragraph position:")
print(f"  {'ParaPos':<10} {'n':>5} {'MeanLOW':>8} {'MeanHIGH':>9}")
print(f"  {'-'*35}")
for pp in ['FIRST', 'MIDDLE', 'LAST', 'SOLO']:
    data = para_pos_coords.get(pp, [])
    if data:
        print(f"  {pp:<10} {len(data):>5} {np.mean([d[0] for d in data]):>8.2f} "
              f"{np.mean([d[1] for d in data]):>9.2f}")

# Kruskal-Wallis: does paragraph position predict LOW?
groups_low = [
    [lo for lo, ho in para_pos_coords.get('FIRST', [])],
    [lo for lo, ho in para_pos_coords.get('MIDDLE', [])],
    [lo for lo, ho in para_pos_coords.get('LAST', [])],
]
groups_low = [g for g in groups_low if len(g) >= 5]
if len(groups_low) >= 2:
    h_low, p_kw_low = kruskal(*groups_low)
    print(f"\n  Kruskal-Wallis para_pos -> LOW:  H={h_low:.2f}, p={p_kw_low:.4f}")

groups_high = [
    [ho for lo, ho in para_pos_coords.get('FIRST', [])],
    [ho for lo, ho in para_pos_coords.get('MIDDLE', [])],
    [ho for lo, ho in para_pos_coords.get('LAST', [])],
]
groups_high = [g for g in groups_high if len(g) >= 5]
if len(groups_high) >= 2:
    h_high, p_kw_high = kruskal(*groups_high)
    print(f"  Kruskal-Wallis para_pos -> HIGH: H={h_high:.2f}, p={p_kw_high:.4f}")

# ============================================================
# 5. ADJACENT LINE CONTINUITY
# ============================================================
print(f"\n{'='*70}")
print("5. ADJACENT LINE CONTINUITY")
print(f"{'='*70}")

# Do adjacent lines tend to share coordinates?
same_pair = 0
same_low = 0
same_high = 0
adj_total = 0
low_diffs = []
high_diffs = []

for folio, keys in folio_lines.items():
    for i in range(len(keys) - 1):
        k1, k2 = keys[i], keys[i + 1]
        if k1 in line_coords and k2 in line_coords:
            lo1, ho1 = line_coords[k1][2], line_coords[k1][3]
            lo2, ho2 = line_coords[k2][2], line_coords[k2][3]
            adj_total += 1
            if lo1 == lo2 and ho1 == ho2:
                same_pair += 1
            if lo1 == lo2:
                same_low += 1
            if ho1 == ho2:
                same_high += 1
            low_diffs.append(abs(lo1 - lo2))
            high_diffs.append(abs(ho1 - ho2))

# Expected same rates under independence
low_stage_counts = Counter(line_coords[k][2] for k in line_coords)
high_stage_counts = Counter(line_coords[k][3] for k in line_coords)
total_lines = len(line_coords)
expected_same_low = sum((c / total_lines) ** 2 for c in low_stage_counts.values())
expected_same_high = sum((c / total_lines) ** 2 for c in high_stage_counts.values())
expected_same_pair = expected_same_low * expected_same_high

actual_same_pair = same_pair / adj_total if adj_total > 0 else 0
actual_same_low = same_low / adj_total if adj_total > 0 else 0
actual_same_high = same_high / adj_total if adj_total > 0 else 0

print(f"\n  Adjacent line agreement rates:")
print(f"  {'Metric':<20} {'Actual':>8} {'Expected':>9} {'Lift':>6}")
print(f"  {'-'*48}")
print(f"  {'Same pair':<20} {actual_same_pair:>7.1%} {expected_same_pair:>8.1%} "
      f"{actual_same_pair/expected_same_pair:.2f}x" if expected_same_pair > 0 else "")
print(f"  {'Same LOW':<20} {actual_same_low:>7.1%} {expected_same_low:>8.1%} "
      f"{actual_same_low/expected_same_low:.2f}x" if expected_same_low > 0 else "")
print(f"  {'Same HIGH':<20} {actual_same_high:>7.1%} {expected_same_high:>8.1%} "
      f"{actual_same_high/expected_same_high:.2f}x" if expected_same_high > 0 else "")

print(f"\n  Mean adjacent step sizes:")
print(f"    LOW:  {np.mean(low_diffs):.2f} stages (0=same, 5=max)")
print(f"    HIGH: {np.mean(high_diffs):.2f} stages")

# ============================================================
# 6. WITHIN-PARAGRAPH CONTINUITY
# ============================================================
print(f"\n{'='*70}")
print("6. WITHIN-PARAGRAPH vs BETWEEN-PARAGRAPH CONTINUITY")
print(f"{'='*70}")

within_same_pair = 0
within_same_low = 0
within_same_high = 0
within_total = 0
within_low_diffs = []
within_high_diffs = []

between_same_pair = 0
between_same_low = 0
between_same_high = 0
between_total = 0

# Build paragraph membership
line_to_para = {}
for pi, para in enumerate(paragraphs):
    for key in para:
        line_to_para[key] = pi

for folio, keys in folio_lines.items():
    for i in range(len(keys) - 1):
        k1, k2 = keys[i], keys[i + 1]
        if k1 not in line_coords or k2 not in line_coords:
            continue
        lo1, ho1 = line_coords[k1][2], line_coords[k1][3]
        lo2, ho2 = line_coords[k2][2], line_coords[k2][3]

        p1 = line_to_para.get(k1, -1)
        p2 = line_to_para.get(k2, -2)

        if p1 == p2 and p1 >= 0:
            within_total += 1
            if lo1 == lo2 and ho1 == ho2:
                within_same_pair += 1
            if lo1 == lo2:
                within_same_low += 1
            if ho1 == ho2:
                within_same_high += 1
            within_low_diffs.append(abs(lo1 - lo2))
            within_high_diffs.append(abs(ho1 - ho2))
        else:
            between_total += 1
            if lo1 == lo2 and ho1 == ho2:
                between_same_pair += 1
            if lo1 == lo2:
                between_same_low += 1
            if ho1 == ho2:
                between_same_high += 1

print(f"\n  {'Context':<20} {'SamePair':>9} {'SameLOW':>8} {'SameHIGH':>9} {'n':>6}")
print(f"  {'-'*58}")
if within_total > 0:
    print(f"  {'Within paragraph':<20} "
          f"{within_same_pair/within_total:>8.1%} "
          f"{within_same_low/within_total:>7.1%} "
          f"{within_same_high/within_total:>8.1%} "
          f"{within_total:>6}")
if between_total > 0:
    print(f"  {'Between paragraphs':<20} "
          f"{between_same_pair/between_total:>8.1%} "
          f"{between_same_low/between_total:>7.1%} "
          f"{between_same_high/between_total:>8.1%} "
          f"{between_total:>6}")

if within_total > 0 and within_low_diffs:
    print(f"\n  Within-paragraph mean step: LOW={np.mean(within_low_diffs):.2f}, HIGH={np.mean(within_high_diffs):.2f}")

# ============================================================
# 7. COORDINATE SEQUENCES within paragraphs
# ============================================================
print(f"\n{'='*70}")
print("7. COORDINATE SEQUENCES WITHIN PARAGRAPHS")
print(f"{'='*70}")

# Within paragraphs: do coordinates progress, oscillate, or stay flat?
para_patterns = Counter()
para_low_trends = []
para_high_trends = []

for para in paragraphs:
    coords_in_para = []
    for key in para:
        if key in line_coords:
            coords_in_para.append(line_coords[key])

    if len(coords_in_para) < 3:
        continue

    low_seq = [c[2] for c in coords_in_para]
    high_seq = [c[3] for c in coords_in_para]

    # Classify LOW sequence
    low_changes = [low_seq[i+1] - low_seq[i] for i in range(len(low_seq)-1)]
    if all(d >= 0 for d in low_changes) and any(d > 0 for d in low_changes):
        low_pattern = 'ASCENDING'
    elif all(d <= 0 for d in low_changes) and any(d < 0 for d in low_changes):
        low_pattern = 'DESCENDING'
    elif all(d == 0 for d in low_changes):
        low_pattern = 'FLAT'
    else:
        low_pattern = 'MIXED'

    high_changes = [high_seq[i+1] - high_seq[i] for i in range(len(high_seq)-1)]
    if all(d >= 0 for d in high_changes) and any(d > 0 for d in high_changes):
        high_pattern = 'ASCENDING'
    elif all(d <= 0 for d in high_changes) and any(d < 0 for d in high_changes):
        high_pattern = 'DESCENDING'
    elif all(d == 0 for d in high_changes):
        high_pattern = 'FLAT'
    else:
        high_pattern = 'MIXED'

    para_patterns[(low_pattern, high_pattern)] += 1
    para_low_trends.append(low_pattern)
    para_high_trends.append(high_pattern)

print(f"\n  Paragraphs with 3+ coordinated lines: {len(para_low_trends)}")

print(f"\n  LOW trend distribution:")
low_trend_counts = Counter(para_low_trends)
for pattern in ['FLAT', 'ASCENDING', 'DESCENDING', 'MIXED']:
    n = low_trend_counts.get(pattern, 0)
    pct = n / len(para_low_trends) * 100 if para_low_trends else 0
    print(f"    {pattern:<12}: {n:>4} ({pct:.1f}%)")

print(f"\n  HIGH trend distribution:")
high_trend_counts = Counter(para_high_trends)
for pattern in ['FLAT', 'ASCENDING', 'DESCENDING', 'MIXED']:
    n = high_trend_counts.get(pattern, 0)
    pct = n / len(para_high_trends) * 100 if para_high_trends else 0
    print(f"    {pattern:<12}: {n:>4} ({pct:.1f}%)")

print(f"\n  Combined (LOW, HIGH) patterns:")
for (lp, hp), count in para_patterns.most_common(8):
    pct = count / len(para_low_trends) * 100 if para_low_trends else 0
    print(f"    ({lp:<10}, {hp:<10}): {count:>4} ({pct:.1f}%)")

# ============================================================
# 8. SUMMARY: VARIANCE ATTRIBUTION
# ============================================================
print(f"\n{'='*70}")
print("8. SUMMARY: WHAT DETERMINES COORDINATES?")
print(f"{'='*70}")

print(f"\n  Factor                    LOW effect       HIGH effect")
print(f"  {'-'*60}")
print(f"  Folio identity            V={v_low:.3f}          V={v_high:.3f}")
print(f"  Section                   V={v_sl:.3f}          V={v_sh:.3f}")
print(f"  Line position in folio    rho={rho_pos_low:+.3f}       rho={rho_pos_high:+.3f}")
if len(groups_low) >= 2:
    print(f"  Paragraph position        p={p_kw_low:.4f}         p={p_kw_high:.4f}")
adj_low_lift = actual_same_low / expected_same_low if expected_same_low > 0 else 0
adj_high_lift = actual_same_high / expected_same_high if expected_same_high > 0 else 0
print(f"  Adjacent line continuity  {adj_low_lift:.2f}x lift       {adj_high_lift:.2f}x lift")
if within_total > 0 and between_total > 0:
    within_pair_rate = within_same_pair / within_total
    between_pair_rate = between_same_pair / between_total
    para_lift = within_pair_rate / between_pair_rate if between_pair_rate > 0 else 0
    print(f"  Within-para coherence     {para_lift:.2f}x vs between")

# Determine primary driver
drivers = []
if v_low > 0.15 or v_high > 0.15:
    drivers.append("FOLIO")
if v_sl > 0.15 or v_sh > 0.15:
    drivers.append("SECTION")
if abs(rho_pos_low) > 0.1 or abs(rho_pos_high) > 0.1:
    drivers.append("LINE_POSITION")
if adj_low_lift > 1.3 or adj_high_lift > 1.3:
    drivers.append("LOCAL_CONTINUITY")

if 'FLAT' in low_trend_counts and low_trend_counts['FLAT'] > len(para_low_trends) * 0.3:
    drivers.append("PARAGRAPH_ANCHORED")

verdict = "MIXED" if len(drivers) > 2 else "+".join(drivers) if drivers else "INDEPENDENT"

print(f"\n  Primary determinants: {', '.join(drivers)}")
print(f"  Verdict: {verdict}")

# ============================================================
# SAVE
# ============================================================
result = {
    'n_lines': len(line_coords),
    'folio_effect': {
        'low_cramers_v': round(float(v_low), 3),
        'high_cramers_v': round(float(v_high), 3),
        'mean_unique_pairs_per_folio': round(float(np.mean(folio_n_pairs)), 1),
        'mean_top_pair_coverage': round(float(np.mean(folio_top_pair_pcts)), 1),
    },
    'section_effect': {
        'low_cramers_v': round(float(v_sl), 3),
        'high_cramers_v': round(float(v_sh), 3),
    },
    'line_position_effect': {
        'low_rho': round(float(rho_pos_low), 3),
        'low_p': round(float(p_pos_low), 4),
        'high_rho': round(float(rho_pos_high), 3),
        'high_p': round(float(p_pos_high), 4),
    },
    'paragraph_position_effect': {
        'low_kw_p': round(float(p_kw_low), 4) if len(groups_low) >= 2 else None,
        'high_kw_p': round(float(p_kw_high), 4) if len(groups_high) >= 2 else None,
    },
    'adjacent_continuity': {
        'same_pair_rate': round(float(actual_same_pair), 3),
        'same_pair_expected': round(float(expected_same_pair), 3),
        'same_low_lift': round(float(adj_low_lift), 2),
        'same_high_lift': round(float(adj_high_lift), 2),
        'mean_low_step': round(float(np.mean(low_diffs)), 2),
        'mean_high_step': round(float(np.mean(high_diffs)), 2),
    },
    'within_para_continuity': {
        'same_pair_rate': round(float(within_same_pair / within_total), 3) if within_total > 0 else None,
        'between_same_pair_rate': round(float(between_same_pair / between_total), 3) if between_total > 0 else None,
    },
    'paragraph_sequences': {
        'low_flat_pct': round(float(low_trend_counts.get('FLAT', 0) / len(para_low_trends) * 100), 1) if para_low_trends else 0,
        'low_mixed_pct': round(float(low_trend_counts.get('MIXED', 0) / len(para_low_trends) * 100), 1) if para_low_trends else 0,
        'high_flat_pct': round(float(high_trend_counts.get('FLAT', 0) / len(para_high_trends) * 100), 1) if para_high_trends else 0,
        'high_mixed_pct': round(float(high_trend_counts.get('MIXED', 0) / len(para_high_trends) * 100), 1) if para_high_trends else 0,
    },
    'primary_determinants': drivers,
    'verdict': verdict,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "33_coordinate_determinants.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
