"""
44_heat_drip_physics.py

If ACTION=heat and OVERSIGHT=drip rate, physics predicts:
  1. POSITIVE CORRELATION: more heat -> more drip (not perfect)
  2. FORBIDDEN STATES: high drip + zero heat should be rare/impossible
  3. LAG STATES: heat up but drip hasn't caught up (or vice versa) should exist
  4. THE ATTRACTOR ON THE CURVE: (LATE,LATE) should sit on the natural heat-drip line
  5. ASYMMETRIC OFF-DIAGONAL: raising heat is fast, drip responds with lag;
     lowering heat causes drip to persist briefly (thermal inertia)

Tests:
  1. Correlation between LOW and HIGH coordinates
  2. Joint frequency distribution -- which cells are populated?
  3. Physics-forbidden states (high drip, no heat) vs physics-expected states
  4. Lag/hysteresis: are off-diagonal states asymmetric?
  5. Transition physics: does changing heat predict drip change on next line?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, chi2_contingency

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

# Build data (same as previous scripts)
line_tokens = defaultdict(list)
line_meta = {}
folio_lines_ordered = defaultdict(list)

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'section': t.section, 'folio': t.folio}
        folio_lines_ordered[t.folio].append(key)

for f in folio_lines_ordered:
    seen = set()
    deduped = []
    for k in folio_lines_ordered[f]:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    folio_lines_ordered[f] = deduped

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
    line_coords[line_key] = {
        'lo': STAGE_ORDER[low_stage], 'ho': STAGE_ORDER[high_stage],
    }

# ============================================================
# 1. GLOBAL CORRELATION
# ============================================================
print("=" * 70)
print("1. HEAT (ACTION) vs DRIP (OVERSIGHT) CORRELATION")
print("=" * 70)

all_lo = [c['lo'] for c in line_coords.values()]
all_ho = [c['ho'] for c in line_coords.values()]

rho, p = spearmanr(all_lo, all_ho)
print(f"\n  Lines with both coordinates: {len(all_lo)}")
print(f"  Spearman rho: {rho:+.3f}")
print(f"  p-value: {p:.6f}")
print(f"\n  Physics prediction: rho should be POSITIVE (more heat -> more drip)")
print(f"  Result: {'CONSISTENT' if rho > 0.05 and p < 0.05 else 'NOT SIGNIFICANT' if p > 0.05 else 'INCONSISTENT'}")

# Per-folio correlation
folio_rhos = []
for folio, keys in folio_lines_ordered.items():
    coords = [(line_coords[k]['lo'], line_coords[k]['ho']) for k in keys if k in line_coords]
    if len(coords) < 8:
        continue
    lo_vals = [c[0] for c in coords]
    ho_vals = [c[1] for c in coords]
    if len(set(lo_vals)) > 1 and len(set(ho_vals)) > 1:
        r, _ = spearmanr(lo_vals, ho_vals)
        folio_rhos.append(r)

print(f"\n  Per-folio correlations (folios with 8+ lines):")
print(f"    N folios: {len(folio_rhos)}")
print(f"    Mean rho: {np.mean(folio_rhos):+.3f}")
print(f"    Positive: {sum(1 for r in folio_rhos if r > 0)} ({sum(1 for r in folio_rhos if r > 0)/len(folio_rhos)*100:.0f}%)")
print(f"    Negative: {sum(1 for r in folio_rhos if r < 0)} ({sum(1 for r in folio_rhos if r < 0)/len(folio_rhos)*100:.0f}%)")

# ============================================================
# 2. JOINT FREQUENCY DISTRIBUTION
# ============================================================
print(f"\n{'='*70}")
print("2. JOINT FREQUENCY GRID (heat x drip)")
print("=" * 70)

grid = np.zeros((6, 6), dtype=int)
for c in line_coords.values():
    grid[c['lo'], c['ho']] += 1

total = grid.sum()

print(f"\n  Raw counts:")
print(f"  {'HEAT':>10}", end='')
for ho in range(6):
    print(f"  {STAGES[ho][:4]:>6}", end='')
print("  <- DRIP RATE")
for lo in range(6):
    print(f"  {STAGES[lo][:4]:>6}  ", end='')
    for ho in range(6):
        print(f"  {grid[lo, ho]:>6}", end='')
    print(f"  | {grid[lo,:].sum():>4}")
print(f"  {'':>10}", end='')
for ho in range(6):
    print(f"  {'-----':>6}", end='')
print()
print(f"  {'':>10}", end='')
for ho in range(6):
    print(f"  {grid[:,ho].sum():>6}", end='')
print(f"  | {total}")

# Percentages
print(f"\n  Percentages:")
print(f"  {'HEAT':>10}", end='')
for ho in range(6):
    print(f"  {STAGES[ho][:4]:>6}", end='')
print("  <- DRIP RATE")
for lo in range(6):
    print(f"  {STAGES[lo][:4]:>6}  ", end='')
    for ho in range(6):
        pct = grid[lo, ho] / total * 100
        if pct == 0:
            print(f"  {'--':>6}", end='')
        else:
            print(f"  {pct:>5.1f}%", end='')
    print()

# ============================================================
# 3. PHYSICS-FORBIDDEN vs PHYSICS-EXPECTED STATES
# ============================================================
print(f"\n{'='*70}")
print("3. PHYSICS-FORBIDDEN vs PHYSICS-EXPECTED STATES")
print("=" * 70)

# In distillation physics:
# - Diagonal states (heat ~ drip) are natural: more heat = more drip
# - Below diagonal (heat >> drip): physically possible (heating up, drip lag)
# - Above diagonal (drip >> heat): physically suspect (drip without heat?)
# Define regions
diagonal = []      # |lo - ho| <= 1
below_diag = []    # lo > ho + 1 (heat exceeds drip by 2+ stages)
above_diag = []    # ho > lo + 1 (drip exceeds heat by 2+ stages)

for lo in range(6):
    for ho in range(6):
        count = grid[lo, ho]
        if count == 0:
            continue
        diff = lo - ho  # positive = heat > drip
        if abs(diff) <= 1:
            diagonal.append((lo, ho, count))
        elif diff >= 2:
            below_diag.append((lo, ho, count, diff))
        else:
            above_diag.append((lo, ho, count, -diff))

diag_total = sum(c for _, _, c in diagonal)
below_total = sum(c for _, _, c, _ in below_diag)
above_total = sum(c for _, _, c, _ in above_diag)

print(f"\n  DIAGONAL (heat ~ drip, |diff| <= 1): {diag_total} ({diag_total/total*100:.1f}%)")
print(f"  BELOW DIAGONAL (heat >> drip):        {below_total} ({below_total/total*100:.1f}%)")
print(f"  ABOVE DIAGONAL (drip >> heat):         {above_total} ({above_total/total*100:.1f}%)")

print(f"\n  Physics prediction: diagonal > below > above")
print(f"  Result: {'CONSISTENT' if diag_total > below_total > above_total else 'PARTIALLY CONSISTENT' if diag_total > max(below_total, above_total) else 'INCONSISTENT'}")

# Expected vs observed under independence
print(f"\n  Chi-squared test (are heat and drip independent?):")
chi2, p_chi, dof, expected = chi2_contingency(grid + 0.5)  # add 0.5 to avoid zero cells
cramers_v = np.sqrt(chi2 / (total * 4))  # min(6,6)-1 = 5, but use 4 for safer estimate
print(f"    chi2={chi2:.1f}, p={p_chi:.6f}, Cramer's V={cramers_v:.3f}")

# ============================================================
# 4. LAG/HYSTERESIS ANALYSIS
# ============================================================
print(f"\n{'='*70}")
print("4. LAG/HYSTERESIS: OFF-DIAGONAL ASYMMETRY")
print("=" * 70)

# In distillation:
# - When you INCREASE heat, drip lags behind (thermal inertia)
#   -> expect more (high heat, low drip) than (low heat, high drip)
# - When you DECREASE heat, drip persists briefly (residual heat)
#   -> some (low heat, high drip) from cooling, but less than heating lag

# Compare symmetric off-diagonal pairs
print(f"\n  Symmetric pair comparison (heat,drip) vs (drip,heat):")
print(f"  {'State A':>20} {'Count A':>8} {'State B':>20} {'Count B':>8} {'Ratio':>8}")
asymmetry_pairs = []
for lo in range(6):
    for ho in range(6):
        if lo > ho + 1:  # heat >> drip
            mirror = grid[ho, lo]  # drip >> heat
            actual = grid[lo, ho]
            if actual > 0 or mirror > 0:
                ratio = actual / mirror if mirror > 0 else float('inf')
                state_a = f"({STAGES[lo][:4]},{STAGES[ho][:4]})"
                state_b = f"({STAGES[ho][:4]},{STAGES[lo][:4]})"
                print(f"  {state_a:>20} {actual:>8} {state_b:>20} {mirror:>8} {ratio:>7.2f}x")
                asymmetry_pairs.append((actual, mirror))

# Overall: heat>>drip vs drip>>heat
if asymmetry_pairs:
    total_heat_leads = sum(a for a, m in asymmetry_pairs)
    total_drip_leads = sum(m for a, m in asymmetry_pairs)
    overall_ratio = total_heat_leads / total_drip_leads if total_drip_leads > 0 else float('inf')
    print(f"\n  Total heat-leads-drip: {total_heat_leads}")
    print(f"  Total drip-leads-heat: {total_drip_leads}")
    print(f"  Ratio: {overall_ratio:.2f}x")
    print(f"\n  Physics prediction: heat-leads > drip-leads (thermal inertia)")
    print(f"  Result: {'CONSISTENT' if overall_ratio > 1.2 else 'NOT SIGNIFICANT' if 0.8 < overall_ratio < 1.2 else 'INCONSISTENT'}")
else:
    overall_ratio = 1.0

# ============================================================
# 5. TRANSITION PHYSICS: does heat change predict drip change?
# ============================================================
print(f"\n{'='*70}")
print("5. TRANSITION PHYSICS: heat change -> drip follows?")
print("=" * 70)

# For consecutive coordinated lines in a folio:
# When heat increases, does drip increase on the NEXT line?
heat_up_drip = []    # drip change when heat went UP
heat_down_drip = []  # drip change when heat went DOWN
heat_same_drip = []  # drip change when heat stayed same

for folio, keys in folio_lines_ordered.items():
    coordinated = [(k, line_coords[k]) for k in keys if k in line_coords]
    for i in range(len(coordinated) - 1):
        curr = coordinated[i][1]
        next_c = coordinated[i + 1][1]
        heat_change = next_c['lo'] - curr['lo']
        drip_change = next_c['ho'] - curr['ho']

        if heat_change > 0:
            heat_up_drip.append(drip_change)
        elif heat_change < 0:
            heat_down_drip.append(drip_change)
        else:
            heat_same_drip.append(drip_change)

print(f"\n  When HEAT INCREASES (n={len(heat_up_drip)}):")
if heat_up_drip:
    print(f"    Mean drip change: {np.mean(heat_up_drip):+.3f}")
    print(f"    Drip up: {sum(1 for d in heat_up_drip if d > 0)} ({sum(1 for d in heat_up_drip if d > 0)/len(heat_up_drip)*100:.0f}%)")
    print(f"    Drip same: {sum(1 for d in heat_up_drip if d == 0)} ({sum(1 for d in heat_up_drip if d == 0)/len(heat_up_drip)*100:.0f}%)")
    print(f"    Drip down: {sum(1 for d in heat_up_drip if d < 0)} ({sum(1 for d in heat_up_drip if d < 0)/len(heat_up_drip)*100:.0f}%)")

print(f"\n  When HEAT DECREASES (n={len(heat_down_drip)}):")
if heat_down_drip:
    print(f"    Mean drip change: {np.mean(heat_down_drip):+.3f}")
    print(f"    Drip up: {sum(1 for d in heat_down_drip if d > 0)} ({sum(1 for d in heat_down_drip if d > 0)/len(heat_down_drip)*100:.0f}%)")
    print(f"    Drip same: {sum(1 for d in heat_down_drip if d == 0)} ({sum(1 for d in heat_down_drip if d == 0)/len(heat_down_drip)*100:.0f}%)")
    print(f"    Drip down: {sum(1 for d in heat_down_drip if d < 0)} ({sum(1 for d in heat_down_drip if d < 0)/len(heat_down_drip)*100:.0f}%)")

print(f"\n  When HEAT UNCHANGED (n={len(heat_same_drip)}):")
if heat_same_drip:
    print(f"    Mean drip change: {np.mean(heat_same_drip):+.3f}")

# Physics: heat up should make drip go up (or at least not down)
# heat down should make drip go down (or lag)
if heat_up_drip and heat_down_drip:
    mean_up = np.mean(heat_up_drip)
    mean_down = np.mean(heat_down_drip)
    print(f"\n  Physics prediction: heat-up -> drip-up, heat-down -> drip-down")
    print(f"  Heat up -> drip change:   {mean_up:+.3f} ({'UP = CONSISTENT' if mean_up > 0 else 'NO EFFECT' if abs(mean_up) < 0.1 else 'DOWN = INCONSISTENT'})")
    print(f"  Heat down -> drip change: {mean_down:+.3f} ({'DOWN = CONSISTENT' if mean_down < 0 else 'NO EFFECT' if abs(mean_down) < 0.1 else 'UP = LAG EFFECT'})")

# ============================================================
# 6. DIAGONAL CONCENTRATION
# ============================================================
print(f"\n{'='*70}")
print("6. DISTANCE FROM DIAGONAL (heat=drip line)")
print("=" * 70)

diffs = [c['lo'] - c['ho'] for c in line_coords.values()]
abs_diffs = [abs(d) for d in diffs]

print(f"\n  Distance from heat=drip diagonal:")
for d in range(6):
    count = sum(1 for ad in abs_diffs if ad == d)
    pct = count / len(abs_diffs) * 100
    bar = '#' * int(pct)
    print(f"    |heat-drip|={d}: {count:>4} ({pct:>5.1f}%) {bar}")

mean_abs_diff = np.mean(abs_diffs)
print(f"\n  Mean |heat-drip|: {mean_abs_diff:.2f}")
print(f"  Physics: should be small (concentrated near diagonal)")
print(f"  Result: {'CONSISTENT' if mean_abs_diff < 1.5 else 'WEAK' if mean_abs_diff < 2.0 else 'INCONSISTENT'}")

# ============================================================
# 7. VERDICT
# ============================================================
print(f"\n{'='*70}")
print("7. VERDICT: DOES THE GRID BEHAVE LIKE HEAT x DRIP?")
print("=" * 70)

check1 = rho > 0.05 and p < 0.05  # positive correlation
check2 = diag_total > max(below_total, above_total)  # diagonal dominates
check3 = overall_ratio > 1.1 if asymmetry_pairs else False  # heat leads drip
check4 = (np.mean(heat_up_drip) > 0 if heat_up_drip else False)  # heat up -> drip up
check5 = mean_abs_diff < 1.8  # concentrated near diagonal

checks = [check1, check2, check3, check4, check5]
n_pass = sum(checks)

print(f"\n  Checks passed: {n_pass}/5")
print(f"  1. Positive heat-drip correlation: {'PASS' if check1 else 'FAIL'} (rho={rho:+.3f}, p={p:.4f})")
print(f"  2. Diagonal dominates:             {'PASS' if check2 else 'FAIL'}")
print(f"  3. Heat leads drip (asymmetry):    {'PASS' if check3 else 'FAIL'} (ratio={overall_ratio:.2f})")
print(f"  4. Heat up -> drip follows:        {'PASS' if check4 else 'FAIL'}")
print(f"  5. Concentrated near diagonal:     {'PASS' if check5 else 'FAIL'} (mean |diff|={mean_abs_diff:.2f})")

if n_pass >= 4:
    verdict = "PHYSICS_CONSISTENT"
    expl = "Grid behavior matches heat x drip rate physics: correlated, diagonal-heavy, asymmetric lag"
elif n_pass >= 2:
    verdict = "PARTIALLY_CONSISTENT"
    expl = "Some physics-consistent features but not all predictions met"
else:
    verdict = "PHYSICS_INCONSISTENT"
    expl = "Grid does not behave like two physically coupled observables"

print(f"\n  VERDICT: {verdict}")
print(f"  {expl}")

# ============================================================
# Write results
# ============================================================
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

results = {
    'correlation': {'rho': round(float(rho), 3), 'p': round(float(p), 6)},
    'diagonal_dominance': {
        'diagonal_pct': round(diag_total / total * 100, 1),
        'below_pct': round(below_total / total * 100, 1),
        'above_pct': round(above_total / total * 100, 1),
    },
    'asymmetry_ratio': round(float(overall_ratio), 2),
    'transition_physics': {
        'heat_up_drip_change': round(float(np.mean(heat_up_drip)), 3) if heat_up_drip else None,
        'heat_down_drip_change': round(float(np.mean(heat_down_drip)), 3) if heat_down_drip else None,
    },
    'mean_diagonal_distance': round(float(mean_abs_diff), 2),
    'checks': [bool(c) for c in checks],
    'verdict': verdict,
    'explanation': expl,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '44_heat_drip_physics.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
