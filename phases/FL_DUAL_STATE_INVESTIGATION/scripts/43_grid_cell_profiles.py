"""
43_grid_cell_profiles.py

What does each cell of the FL grid "look like"?

If FL is a state index, the center content at each grid cell should tell us
what operations are prescribed for that state. By profiling the content
systematically, we can infer what physical condition each state represents.

Approach:
  1. For each grid cell: profile prefix distribution, suffix patterns,
     kernel types, and dominant instruction classes
  2. Map how content shifts along each axis (what changes as ACTION increases?
     as OVERSIGHT increases?)
  3. Identify cell-specific vocabulary (words that ONLY appear at specific states)
  4. Look at FL MIDDLEs themselves: do specific MIDDLEs correlate with
     specific center content? (The MIDDLE might BE the observable label)
  5. Cross-reference with hazard classes: do hazard types cluster at specific
     grid positions?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load class data
class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data.get('token_to_class', {})
token_to_role = class_data.get('token_to_role', {})

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

KNOWN_PREFIXES = ['qo', 'sh', 'ch', 'ok', 'ol', 'ot', 'd', 'or', 'so', 'op']
KNOWN_SUFFIXES = ['y', 'dy', 'am', 'al', 'ar', 'ol', 'in', 'aiin', 'ain',
                  'edy', 'eedy', 'chy']

tx = Transcript()
morph = Morphology()
MIN_N = 50

# ============================================================
# Build data
# ============================================================
line_tokens = defaultdict(list)
line_meta = {}

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'section': t.section, 'folio': t.folio}

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

# Assign coordinates and collect center tokens per grid cell
line_coords = {}
cell_center_tokens = defaultdict(list)  # (lo, ho) -> list of center token words
cell_center_morphs = defaultdict(list)  # (lo, ho) -> list of Morphology results
cell_fl_middles = defaultdict(lambda: {'low': [], 'high': []})  # FL MIDDLEs by mode
cell_lines = defaultdict(int)
cell_sections = defaultdict(lambda: Counter())

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    center_tokens = []
    center_morphs = []

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
            fl_info.append({'mode': mode, 'stage': stage, 'middle': mid})
        elif not is_fl:
            center_tokens.append(t.word)
            if m:
                center_morphs.append(m)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    lo = STAGE_ORDER[low_stage]
    ho = STAGE_ORDER[high_stage]
    cell = (lo, ho)

    line_coords[line_key] = {'lo': lo, 'ho': ho}
    cell_center_tokens[cell].extend(center_tokens)
    cell_center_morphs[cell].extend(center_morphs)
    cell_lines[cell] += 1
    cell_sections[cell][line_meta[line_key]['section']] += 1

    for f in low_fls:
        cell_fl_middles[cell]['low'].append(f['middle'])
    for f in high_fls:
        cell_fl_middles[cell]['high'].append(f['middle'])

print(f"Lines with coordinates: {len(line_coords)}")
print(f"Grid cells populated: {len(cell_lines)}")

# ============================================================
# 1. PREFIX PROFILES ACROSS THE GRID
# ============================================================
print(f"\n{'='*70}")
print("1. PREFIX PROFILES ACROSS THE GRID")
print("=" * 70)

# For each cell: compute prefix distribution of center tokens
cell_prefix_rates = {}
for cell, morphs in cell_center_morphs.items():
    if cell_lines[cell] < 5:
        continue
    pfx_counts = Counter()
    total = 0
    for m in morphs:
        if m.prefix:
            pfx_counts[m.prefix] += 1
            total += 1
    if total > 0:
        cell_prefix_rates[cell] = {p: c / total for p, c in pfx_counts.items()}
        cell_prefix_rates[cell]['_total'] = total

# Show the grid for key prefixes
for pfx in ['qo', 'sh', 'ch', 'ok', 'ol', 'd']:
    print(f"\n  {pfx} rate across grid:")
    print(f"  {'':>10}", end='')
    for ho in range(6):
        print(f"  {STAGES[ho][:4]:>6}", end='')
    print("  <- OVERSIGHT")
    for lo in range(6):
        print(f"  {STAGES[lo][:4]:>6}  ", end='')
        for ho in range(6):
            cell = (lo, ho)
            if cell in cell_prefix_rates:
                rate = cell_prefix_rates[cell].get(pfx, 0) * 100
                print(f"  {rate:>5.1f}%", end='')
            else:
                print(f"  {'--':>6}", end='')
        print()
    print(f"  ^ ACTION")

# ============================================================
# 2. SUFFIX PROFILES ACROSS THE GRID
# ============================================================
print(f"\n{'='*70}")
print("2. SUFFIX PROFILES ACROSS THE GRID")
print("=" * 70)

cell_suffix_rates = {}
for cell, morphs in cell_center_morphs.items():
    if cell_lines[cell] < 5:
        continue
    sfx_counts = Counter()
    total = 0
    for m in morphs:
        sfx = m.suffix if m.suffix else 'NONE'
        sfx_counts[sfx] += 1
        total += 1
    if total > 0:
        cell_suffix_rates[cell] = {s: c / total for s, c in sfx_counts.items()}

# Key suffixes: y (iterate), dy (terminal), NONE (bare), aiin/ain (complex)
for sfx in ['y', 'dy', 'NONE', 'aiin', 'ain']:
    print(f"\n  '{sfx}' suffix rate across grid:")
    print(f"  {'':>10}", end='')
    for ho in range(6):
        print(f"  {STAGES[ho][:4]:>6}", end='')
    print("  <- OVERSIGHT")
    for lo in range(6):
        print(f"  {STAGES[lo][:4]:>6}  ", end='')
        for ho in range(6):
            cell = (lo, ho)
            if cell in cell_suffix_rates:
                rate = cell_suffix_rates[cell].get(sfx, 0) * 100
                print(f"  {rate:>5.1f}%", end='')
            else:
                print(f"  {'--':>6}", end='')
        print()
    print(f"  ^ ACTION")

# ============================================================
# 3. GRADIENT ALONG EACH AXIS
# ============================================================
print(f"\n{'='*70}")
print("3. GRADIENT ANALYSIS ALONG EACH AXIS")
print("=" * 70)

# Collapse to rows (ACTION levels) and columns (OVERSIGHT levels)
# For each prefix: correlate rate with axis level

print("\n  Prefix rate vs ACTION level (collapsed across OVERSIGHT):")
for pfx in ['qo', 'sh', 'ch', 'ok', 'ol', 'd']:
    action_rates = []
    action_levels = []
    for lo in range(6):
        rates = []
        for ho in range(6):
            cell = (lo, ho)
            if cell in cell_prefix_rates:
                rates.append(cell_prefix_rates[cell].get(pfx, 0))
        if rates:
            action_rates.append(np.mean(rates))
            action_levels.append(lo)
    if len(action_levels) > 3:
        rho, p = spearmanr(action_levels, action_rates)
        trend = [f"{r*100:.1f}%" for r in action_rates]
        print(f"    {pfx:<4}: rho={rho:+.3f} p={p:.3f}  [{' -> '.join(trend)}]")

print("\n  Prefix rate vs OVERSIGHT level (collapsed across ACTION):")
for pfx in ['qo', 'sh', 'ch', 'ok', 'ol', 'd']:
    oversight_rates = []
    oversight_levels = []
    for ho in range(6):
        rates = []
        for lo in range(6):
            cell = (lo, ho)
            if cell in cell_prefix_rates:
                rates.append(cell_prefix_rates[cell].get(pfx, 0))
        if rates:
            oversight_rates.append(np.mean(rates))
            oversight_levels.append(ho)
    if len(oversight_levels) > 3:
        rho, p = spearmanr(oversight_levels, oversight_rates)
        trend = [f"{r*100:.1f}%" for r in oversight_rates]
        print(f"    {pfx:<4}: rho={rho:+.3f} p={p:.3f}  [{' -> '.join(trend)}]")

# ============================================================
# 4. CELL-SPECIFIC VOCABULARY
# ============================================================
print(f"\n{'='*70}")
print("4. CELL-SPECIFIC VOCABULARY (MIDDLEs enriched at specific states)")
print("=" * 70)

# For each center MIDDLE: compute which cell it's most enriched in
global_middle_counts = Counter()
cell_middle_counts = defaultdict(Counter)
for cell, morphs in cell_center_morphs.items():
    if cell_lines[cell] < 5:
        continue
    for m in morphs:
        if m.middle:
            global_middle_counts[m.middle] += 1
            cell_middle_counts[cell][m.middle] += 1

global_total = sum(global_middle_counts.values())

# Find MIDDLEs with highest lift at specific cells
print("\n  MIDDLEs with >2x enrichment at specific grid cells:")
enrichments = []
for cell in cell_middle_counts:
    cell_total = sum(cell_middle_counts[cell].values())
    if cell_total < 20:
        continue
    for mid, count in cell_middle_counts[cell].items():
        if count < 5:
            continue
        global_rate = global_middle_counts[mid] / global_total
        cell_rate = count / cell_total
        lift = cell_rate / global_rate if global_rate > 0 else 0
        if lift > 2.0:
            enrichments.append({
                'middle': mid, 'cell': cell, 'lift': lift,
                'cell_rate': cell_rate, 'global_rate': global_rate,
                'count': count,
            })

enrichments.sort(key=lambda x: -x['lift'])
for e in enrichments[:20]:
    lo, ho = e['cell']
    print(f"    '{e['middle']}' at ({STAGES[lo][:4]},{STAGES[ho][:4]}): "
          f"{e['lift']:.1f}x enriched ({e['cell_rate']*100:.1f}% vs {e['global_rate']*100:.1f}% global, n={e['count']})")

# ============================================================
# 5. FL MIDDLE LABELS AT EACH CELL
# ============================================================
print(f"\n{'='*70}")
print("5. WHICH FL MIDDLEs LABEL EACH CELL?")
print("=" * 70)

# The FL MIDDLEs that appear at each cell (as LOW or HIGH coordinate)
print("\n  LOW FL MIDDLEs by ACTION level:")
for lo in range(6):
    low_mids = []
    for ho in range(6):
        cell = (lo, ho)
        low_mids.extend(cell_fl_middles[cell]['low'])
    if low_mids:
        counts = Counter(low_mids)
        total = len(low_mids)
        top = ', '.join(f"{m}({c/total*100:.0f}%)" for m, c in counts.most_common(4))
        print(f"    {STAGES[lo][:8]:<10}: n={total:>4}, {top}")

print("\n  HIGH FL MIDDLEs by OVERSIGHT level:")
for ho in range(6):
    high_mids = []
    for lo in range(6):
        cell = (lo, ho)
        high_mids.extend(cell_fl_middles[cell]['high'])
    if high_mids:
        counts = Counter(high_mids)
        total = len(high_mids)
        top = ', '.join(f"{m}({c/total*100:.0f}%)" for m, c in counts.most_common(4))
        print(f"    {STAGES[ho][:8]:<10}: n={total:>4}, {top}")

# ============================================================
# 6. ATTRACTOR vs PERIPHERY CONTENT COMPARISON
# ============================================================
print(f"\n{'='*70}")
print("6. ATTRACTOR (LATE,LATE) vs PERIPHERY CONTENT")
print("=" * 70)

attractor = (3, 3)  # LATE, LATE
near_cells = [(lo, ho) for lo in range(2, 5) for ho in range(2, 5)
              if (lo, ho) != attractor and (lo, ho) in cell_prefix_rates]
far_cells = [(lo, ho) for lo in range(6) for ho in range(6)
             if abs(lo - 3) + abs(ho - 3) >= 3 and (lo, ho) in cell_prefix_rates]

def cell_profile(cells):
    total_pfx = Counter()
    total_sfx = Counter()
    total_mid = Counter()
    n_tokens = 0
    for cell in cells:
        for m in cell_center_morphs.get(cell, []):
            if m.prefix:
                total_pfx[m.prefix] += 1
            sfx = m.suffix if m.suffix else 'NONE'
            total_sfx[sfx] += 1
            if m.middle:
                total_mid[m.middle] += 1
            n_tokens += 1
    return total_pfx, total_sfx, total_mid, n_tokens

att_pfx, att_sfx, att_mid, att_n = cell_profile([attractor])
near_pfx, near_sfx, near_mid, near_n = cell_profile(near_cells)
far_pfx, far_sfx, far_mid, far_n = cell_profile(far_cells)

print(f"\n  Token counts: Attractor={att_n}, Near={near_n}, Far={far_n}")

print(f"\n  PREFIX comparison:")
print(f"  {'Prefix':<8} {'Attractor':>12} {'Near':>12} {'Far':>12}")
for pfx in ['qo', 'sh', 'ch', 'ok', 'ol', 'd', 'ot', 'or']:
    a_rate = att_pfx.get(pfx, 0) / att_n * 100 if att_n else 0
    n_rate = near_pfx.get(pfx, 0) / near_n * 100 if near_n else 0
    f_rate = far_pfx.get(pfx, 0) / far_n * 100 if far_n else 0
    print(f"  {pfx:<8} {a_rate:>11.1f}% {n_rate:>11.1f}% {f_rate:>11.1f}%")

print(f"\n  SUFFIX comparison:")
print(f"  {'Suffix':<8} {'Attractor':>12} {'Near':>12} {'Far':>12}")
for sfx in ['y', 'dy', 'NONE', 'aiin', 'ain', 'edy']:
    a_rate = att_sfx.get(sfx, 0) / att_n * 100 if att_n else 0
    n_rate = near_sfx.get(sfx, 0) / near_n * 100 if near_n else 0
    f_rate = far_sfx.get(sfx, 0) / far_n * 100 if far_n else 0
    print(f"  {sfx:<8} {a_rate:>11.1f}% {n_rate:>11.1f}% {f_rate:>11.1f}%")

# Top MIDDLEs unique to attractor vs periphery
att_set = set(m for m, c in att_mid.items() if c >= 3)
far_set = set(m for m, c in far_mid.items() if c >= 3)
att_only = att_set - far_set
far_only = far_set - att_set

print(f"\n  MIDDLEs enriched at attractor (not common at periphery):")
att_enriched = []
for mid in att_set:
    a_rate = att_mid[mid] / att_n
    f_rate = far_mid.get(mid, 0) / far_n if far_n else 0
    if f_rate > 0:
        lift = a_rate / f_rate
        if lift > 1.5:
            att_enriched.append((mid, lift, att_mid[mid]))
att_enriched.sort(key=lambda x: -x[1])
for mid, lift, count in att_enriched[:10]:
    print(f"    '{mid}': {lift:.1f}x enriched at attractor (n={count})")

print(f"\n  MIDDLEs enriched at periphery (not common at attractor):")
far_enriched = []
for mid in far_set:
    f_rate = far_mid[mid] / far_n
    a_rate = att_mid.get(mid, 0) / att_n if att_n else 0
    if a_rate > 0:
        lift = f_rate / a_rate
        if lift > 1.5:
            far_enriched.append((mid, lift, far_mid[mid]))
    elif f_rate > 0:
        far_enriched.append((mid, 99, far_mid[mid]))
far_enriched.sort(key=lambda x: -x[1])
for mid, lift, count in far_enriched[:10]:
    lift_str = f"{lift:.1f}x" if lift < 50 else "UNIQUE"
    print(f"    '{mid}': {lift_str} enriched at periphery (n={count})")

# ============================================================
# 7. INSTRUCTION CLASS DISTRIBUTION
# ============================================================
print(f"\n{'='*70}")
print("7. INSTRUCTION CLASS AT EACH STATE (from 49-class system)")
print("=" * 70)

cell_classes = defaultdict(Counter)
for line_key, tokens in line_tokens.items():
    if line_key not in line_coords:
        continue
    c = line_coords[line_key]
    cell = (c['lo'], c['ho'])
    for t in tokens:
        cls = token_to_class.get(t.word)
        if cls:
            cell_classes[cell][cls] += 1

# Show top class at each cell
print(f"\n  Dominant instruction class at each cell:")
print(f"  {'':>10}", end='')
for ho in range(6):
    print(f"  {STAGES[ho][:4]:>8}", end='')
print("  <- OVERSIGHT")
for lo in range(6):
    print(f"  {STAGES[lo][:4]:>6}  ", end='')
    for ho in range(6):
        cell = (lo, ho)
        if cell in cell_classes and sum(cell_classes[cell].values()) > 10:
            top_cls, top_n = cell_classes[cell].most_common(1)[0]
            total = sum(cell_classes[cell].values())
            pct = top_n / total * 100
            print(f"  {top_cls:>5}({pct:.0f}%)", end='')
        else:
            print(f"  {'--':>8}", end='')
    print()
print(f"  ^ ACTION")

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

# Compact results
results = {
    'n_lines': len(line_coords),
    'n_cells': len(cell_lines),
    'attractor_profile': {
        'qo_rate': round(att_pfx.get('qo', 0) / max(att_n, 1) * 100, 1),
        'sh_rate': round(att_pfx.get('sh', 0) / max(att_n, 1) * 100, 1),
        'ch_rate': round(att_pfx.get('ch', 0) / max(att_n, 1) * 100, 1),
        'ok_rate': round(att_pfx.get('ok', 0) / max(att_n, 1) * 100, 1),
    },
    'periphery_profile': {
        'qo_rate': round(far_pfx.get('qo', 0) / max(far_n, 1) * 100, 1),
        'sh_rate': round(far_pfx.get('sh', 0) / max(far_n, 1) * 100, 1),
        'ch_rate': round(far_pfx.get('ch', 0) / max(far_n, 1) * 100, 1),
        'ok_rate': round(far_pfx.get('ok', 0) / max(far_n, 1) * 100, 1),
    },
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '43_grid_cell_profiles.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
