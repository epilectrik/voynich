"""
48_grid_cell_sparsity.py

Audit how many of the 36 grid cells (6x6) actually have data, and whether
the grid topology claims are supported by adequate sample sizes.

The FL_DUAL_STATE_INVESTIGATION phase uses a 6x6 grid where each axis has
stages INITIAL(0), EARLY(1), MEDIAL(2), LATE(3), FINAL(4), TERMINAL(5).

This script answers:
  1. How many cells are populated, and with what counts?
  2. Is the grid truly 2D or pseudo-1D (concentrated along diagonal)?
  3. Are the extreme corners populated?
  4. Is the effective dimensionality sufficient to support 2D topology claims?
"""
import sys
import json
import math
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture

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

# ============================================================
# Build data pipeline (same as scripts 42-45)
# ============================================================
line_tokens = defaultdict(list)
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)

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

line_coords = {}
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
    lo = STAGE_ORDER[low_stage]
    ho = STAGE_ORDER[high_stage]
    line_coords[line_key] = {'lo': lo, 'ho': ho}

print("=" * 70)
print("GRID CELL SPARSITY AUDIT")
print("=" * 70)
print(f"\nTotal lines with grid coordinates: {len(line_coords)}")

# ============================================================
# 1. Build 6x6 count matrix
# ============================================================
grid = np.zeros((6, 6), dtype=int)
for coords in line_coords.values():
    grid[coords['lo'], coords['ho']] += 1

total_lines = int(grid.sum())

print(f"\n{'='*70}")
print("1. GRID COUNT MATRIX (rows=LOW/ACTION, cols=HIGH/OVERSIGHT)")
print("=" * 70)
print()

# Header row
header = "          "
for ho in range(6):
    header += f" {STAGES[ho][:5]:>7}"
header += "   <-- HIGH"
print(header)

# Separator
print("          " + "-" * 49)

for lo in range(6):
    row_str = f" {STAGES[lo][:5]:>7} |"
    for ho in range(6):
        count = grid[lo, ho]
        if count == 0:
            row_str += f"     {'.':>2}"
        else:
            row_str += f"  {count:>5}"
    row_total = int(grid[lo, :].sum())
    row_str += f"  | {row_total:>4}"
    print(row_str)

print("          " + "-" * 49)

# Column totals
col_str = "   totals:"
for ho in range(6):
    col_str += f"  {int(grid[:, ho].sum()):>5}"
print(col_str)
print("  ^ LOW")

# ============================================================
# 2. Sparsity metrics
# ============================================================
print(f"\n{'='*70}")
print("2. SPARSITY METRICS")
print("=" * 70)

populated_counts = grid[grid > 0]
n_populated = int(len(populated_counts))
n_ge_5 = int(np.sum(grid >= 5))
n_ge_10 = int(np.sum(grid >= 10))
n_ge_20 = int(np.sum(grid >= 20))
max_count = int(grid.max())
median_populated = float(np.median(populated_counts)) if n_populated > 0 else 0.0

print(f"\n  Total cells:               36 (6x6)")
print(f"  Populated (count > 0):     {n_populated} ({n_populated/36*100:.1f}%)")
print(f"  Cells with n >= 5:         {n_ge_5} ({n_ge_5/36*100:.1f}%)")
print(f"  Cells with n >= 10:        {n_ge_10} ({n_ge_10/36*100:.1f}%)")
print(f"  Cells with n >= 20:        {n_ge_20} ({n_ge_20/36*100:.1f}%)")
print(f"  Maximum count (any cell):  {max_count}")
print(f"  Median count (populated):  {median_populated:.1f}")
print(f"  Empty cells:               {36 - n_populated}")

# ============================================================
# 3. Diagonal analysis
# ============================================================
print(f"\n{'='*70}")
print("3. DIAGONAL ANALYSIS")
print("=" * 70)

diag_count = 0
near_diag_count = 0
off_diag_count = 0

diag_cells = []
near_diag_cells = []

for lo in range(6):
    for ho in range(6):
        c = int(grid[lo, ho])
        diff = abs(lo - ho)
        if diff == 0:
            diag_count += c
            diag_cells.append((lo, ho, c))
        elif diff <= 1:
            near_diag_count += c
            near_diag_cells.append((lo, ho, c))
        else:
            off_diag_count += c

band_count = diag_count + near_diag_count  # |lo - ho| <= 1

print(f"\n  Main diagonal (lo == ho):")
for lo, ho, c in diag_cells:
    print(f"    ({lo},{ho}) [{STAGES[lo][:4]},{STAGES[ho][:4]}]: {c} lines")
print(f"    Total on diagonal: {diag_count} ({diag_count/total_lines*100:.1f}%)")

print(f"\n  Near-diagonal band (|lo - ho| == 1):")
for lo, ho, c in near_diag_cells:
    if c > 0:
        print(f"    ({lo},{ho}) [{STAGES[lo][:4]},{STAGES[ho][:4]}]: {c} lines")
print(f"    Total in band (|lo-ho|<=1): {band_count} ({band_count/total_lines*100:.1f}%)")

print(f"\n  Off-diagonal (|lo - ho| > 1): {off_diag_count} ({off_diag_count/total_lines*100:.1f}%)")

diag_fraction = diag_count / total_lines if total_lines > 0 else 0.0
band_fraction = band_count / total_lines if total_lines > 0 else 0.0

# ============================================================
# 4. Effective dimensionality test
# ============================================================
print(f"\n{'='*70}")
print("4. EFFECTIVE DIMENSIONALITY")
print("=" * 70)

# Compute entropy of the cell distribution
flat_counts = grid.flatten()
probs = flat_counts / flat_counts.sum()
# Filter out zero probabilities for entropy calculation
nonzero_probs = probs[probs > 0]
entropy = -np.sum(nonzero_probs * np.log(nonzero_probs))
max_entropy = np.log(36)  # uniform over 36 cells
effective_cells = float(np.exp(entropy))
entropy_ratio = entropy / max_entropy

print(f"\n  Shannon entropy of cell distribution: {entropy:.3f} nats")
print(f"  Maximum entropy (uniform over 36):    {max_entropy:.3f} nats")
print(f"  Entropy ratio (H / H_max):            {entropy_ratio:.3f}")
print(f"  Effective cells = exp(H):             {effective_cells:.1f}")
print(f"\n  Interpretation:")
if effective_cells < 10:
    print(f"    Effective cells < 10: grid is concentrated in a few cells (pseudo-1D)")
elif effective_cells < 20:
    print(f"    Effective cells 10-20: moderate spread, partially 2D")
else:
    print(f"    Effective cells >= 20: well-spread across grid (truly 2D)")

# ============================================================
# 5. Corner analysis
# ============================================================
print(f"\n{'='*70}")
print("5. CORNER ANALYSIS")
print("=" * 70)

extreme_corners = {
    '(0,0) INITIAL/INITIAL': (0, 0),
    '(0,5) INITIAL/TERMINAL': (0, 5),
    '(5,0) TERMINAL/INITIAL': (5, 0),
    '(5,5) TERMINAL/TERMINAL': (5, 5),
}

off_diag_corners = {
    '(0,5) INITIAL/TERMINAL': (0, 5),
    '(5,0) TERMINAL/INITIAL': (5, 0),
}

print(f"\n  Extreme corners:")
n_extreme_populated = 0
n_offdiag_extreme_populated = 0
for label, (lo, ho) in extreme_corners.items():
    c = int(grid[lo, ho])
    status = f"n={c}" if c > 0 else "EMPTY"
    print(f"    {label}: {status}")
    if c > 0:
        n_extreme_populated += 1

# Count corners with distance > 3 from diagonal
far_corners_populated = 0
far_corner_cells = []
for lo in range(6):
    for ho in range(6):
        if abs(lo - ho) > 3 and grid[lo, ho] > 0:
            far_corners_populated += 1
            far_corner_cells.append((lo, ho, int(grid[lo, ho])))

print(f"\n  Cells with |lo - ho| > 3 (far from diagonal):")
if far_corner_cells:
    for lo, ho, c in far_corner_cells:
        print(f"    ({lo},{ho}) [{STAGES[lo][:4]},{STAGES[ho][:4]}]: {c} lines")
    print(f"    Total far-corner cells populated: {far_corners_populated}")
else:
    print(f"    None populated")
    print(f"    Total far-corner cells populated: 0")

# ============================================================
# 6. CHECKS
# ============================================================
print(f"\n{'='*70}")
print("6. CHECKS")
print("=" * 70)

check_1 = bool(n_populated >= 20)
check_2 = bool(n_ge_5 >= 15)
check_3 = bool(effective_cells > 12)
check_4 = bool(far_corners_populated >= 2)

n_pass = sum([check_1, check_2, check_3, check_4])

print(f"\n  check_1: >= 20 cells populated (>55% of grid used)")
print(f"    Populated cells: {n_populated}")
print(f"    Result: {'PASS' if check_1 else 'FAIL'}")

print(f"\n  check_2: >= 15 cells with n >= 5 (adequate sample in most populated cells)")
print(f"    Cells with n>=5: {n_ge_5}")
print(f"    Result: {'PASS' if check_2 else 'FAIL'}")

print(f"\n  check_3: Effective dimensionality > 12 (truly 2D, not pseudo-1D)")
print(f"    Effective cells: {effective_cells:.1f}")
print(f"    Result: {'PASS' if check_3 else 'FAIL'}")

print(f"\n  check_4: At least 2 cells with |lo-ho| > 3 populated (extreme corners)")
print(f"    Far-corner cells populated: {far_corners_populated}")
print(f"    Result: {'PASS' if check_4 else 'FAIL'}")

print(f"\n  Checks passed: {n_pass}/4")

# ============================================================
# 7. VERDICT
# ============================================================
if n_pass >= 3:
    verdict = "WELL_POPULATED"
elif n_pass == 2:
    verdict = "SPARSE_BUT_USABLE"
else:
    verdict = "TOO_SPARSE"

print(f"\n{'='*70}")
print(f"VERDICT: {verdict}")
print("=" * 70)

if verdict == "WELL_POPULATED":
    print("  The 6x6 grid is well-populated with adequate sample sizes.")
    print("  Grid topology claims are supported by sufficient data coverage.")
elif verdict == "SPARSE_BUT_USABLE":
    print("  The grid has partial coverage. Topology claims should be qualified")
    print("  with caveats about sparse regions.")
else:
    print("  The grid is too sparse to support 2D topology claims.")
    print("  Most data is concentrated in a few cells; the grid may be pseudo-1D.")

# ============================================================
# Write results
# ============================================================
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.bool_): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)

# Build grid as serializable nested list
grid_list = grid.tolist()

results = {
    'n_lines': total_lines,
    'sparsity': {
        'total_cells': 36,
        'populated': n_populated,
        'cells_ge_5': n_ge_5,
        'cells_ge_10': n_ge_10,
        'cells_ge_20': n_ge_20,
        'max_count': max_count,
        'median_populated': round(median_populated, 1),
        'empty_cells': 36 - n_populated,
    },
    'diagonal': {
        'diagonal_count': diag_count,
        'diagonal_fraction': round(diag_fraction, 3),
        'band_count': band_count,
        'band_fraction': round(band_fraction, 3),
        'off_diagonal_count': off_diag_count,
    },
    'effective_dimensionality': {
        'entropy_nats': round(float(entropy), 3),
        'max_entropy_nats': round(float(max_entropy), 3),
        'entropy_ratio': round(float(entropy_ratio), 3),
        'effective_cells': round(effective_cells, 1),
    },
    'corners': {
        'extreme_corners_populated': n_extreme_populated,
        'far_corners_populated': far_corners_populated,
        'far_corner_cells': [{'lo': lo, 'ho': ho, 'count': c}
                             for lo, ho, c in far_corner_cells],
    },
    'grid_matrix': grid_list,
    'checks': {
        'check_1_populated_ge_20': bool(check_1),
        'check_2_adequate_ge_15': bool(check_2),
        'check_3_effective_dim_gt_12': bool(check_3),
        'check_4_far_corners_ge_2': bool(check_4),
        'n_passed': n_pass,
    },
    'verdict': verdict,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '48_grid_cell_sparsity.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
