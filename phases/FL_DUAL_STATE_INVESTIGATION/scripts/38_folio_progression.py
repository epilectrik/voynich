"""
38_folio_progression.py

Can we stitch together a state progression from a folio's coordinates?

Each folio covers multiple (action, oversight) states. If these form
a connected path through the grid, we can reconstruct the procedure
as a logical progression regardless of physical line order.

Questions:
  1. Do folio coordinate sets form connected paths or scattered points?
  2. Is there a dominant progression direction?
  3. What does the stitched procedure look like for typical folios?
  4. Do different sections trace different path shapes?
  5. Is there a common "process arc" (e.g., low->high action, tight->loose oversight)?
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

line_tokens = defaultdict(list)
line_meta = {}
folio_lines_ordered = defaultdict(list)

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'section': t.section, 'folio': t.folio}
        folio_lines_ordered[t.folio].append(key)

# Deduplicate
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

# Assign coordinates
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
        'low': low_stage, 'high': high_stage,
        'lo': STAGE_ORDER[low_stage], 'ho': STAGE_ORDER[high_stage],
    }

# ============================================================
# 1. FOLIO FOOTPRINTS on the grid
# ============================================================
print("=" * 70)
print("1. FOLIO FOOTPRINTS ON THE STATE GRID")
print("=" * 70)

folio_footprints = defaultdict(list)  # folio -> list of (lo, ho) in line order
folio_sections = {}

for folio, keys in folio_lines_ordered.items():
    section = line_meta[keys[0]]['section'] if keys else '?'
    folio_sections[folio] = section
    for key in keys:
        if key in line_coords:
            c = line_coords[key]
            folio_footprints[folio].append((c['lo'], c['ho']))

# Filter to folios with enough data
good_folios = {f: fp for f, fp in folio_footprints.items() if len(fp) >= 8}
print(f"\nFolios with 8+ coordinated lines: {len(good_folios)}")

# ============================================================
# 2. PATH CONNECTIVITY: are states adjacent on the grid?
# ============================================================
print(f"\n{'='*70}")
print("2. PATH CONNECTIVITY")
print("=" * 70)

# For each folio, get unique states and check connectivity
# A state (lo, ho) is "connected" to another if Manhattan distance <= 2

folio_stats = []
for folio, footprint in good_folios.items():
    unique_states = list(set(footprint))
    n_unique = len(unique_states)
    n_lines = len(footprint)
    section = folio_sections[folio]

    # Compute grid span
    lo_vals = [s[0] for s in unique_states]
    ho_vals = [s[1] for s in unique_states]
    lo_span = max(lo_vals) - min(lo_vals)
    ho_span = max(ho_vals) - min(ho_vals)
    lo_center = np.mean(lo_vals)
    ho_center = np.mean(ho_vals)

    # Check connectivity: can we reach all states from any state
    # via steps of Manhattan distance <= 2?
    def is_connected(states):
        if len(states) <= 1:
            return True
        visited = {states[0]}
        queue = [states[0]]
        while queue:
            current = queue.pop(0)
            for s in states:
                if s not in visited:
                    dist = abs(s[0] - current[0]) + abs(s[1] - current[1])
                    if dist <= 2:
                        visited.add(s)
                        queue.append(s)
        return len(visited) == len(states)

    connected = is_connected(unique_states)

    # Mean pairwise distance
    if n_unique > 1:
        dists = []
        for i in range(n_unique):
            for j in range(i+1, n_unique):
                d = abs(unique_states[i][0] - unique_states[j][0]) + \
                    abs(unique_states[i][1] - unique_states[j][1])
                dists.append(d)
        mean_dist = np.mean(dists)
    else:
        mean_dist = 0

    # Dominant direction: is the folio moving along LOW, HIGH, or diagonal?
    if n_unique >= 3:
        lo_range = max(lo_vals) - min(lo_vals)
        ho_range = max(ho_vals) - min(ho_vals)
        if lo_range > ho_range * 1.5:
            direction = "LOW_DOMINANT"
        elif ho_range > lo_range * 1.5:
            direction = "HIGH_DOMINANT"
        elif lo_range > 0 and ho_range > 0:
            direction = "DIAGONAL"
        else:
            direction = "POINT"
    else:
        direction = "NARROW"

    folio_stats.append({
        'folio': folio, 'section': section,
        'n_lines': n_lines, 'n_unique': n_unique,
        'lo_span': lo_span, 'ho_span': ho_span,
        'lo_center': lo_center, 'ho_center': ho_center,
        'connected': connected, 'mean_dist': mean_dist,
        'direction': direction,
        'unique_states': unique_states,
        'footprint': footprint,
    })

# Summary stats
connected_rate = sum(1 for f in folio_stats if f['connected']) / len(folio_stats)
print(f"\n  Connected footprints: {sum(1 for f in folio_stats if f['connected'])}/{len(folio_stats)} ({connected_rate:.0%})")
print(f"  Mean unique states per folio: {np.mean([f['n_unique'] for f in folio_stats]):.1f}")
print(f"  Mean LOW span: {np.mean([f['lo_span'] for f in folio_stats]):.1f}")
print(f"  Mean HIGH span: {np.mean([f['ho_span'] for f in folio_stats]):.1f}")
print(f"  Mean pairwise distance: {np.mean([f['mean_dist'] for f in folio_stats]):.2f}")

direction_counts = Counter(f['direction'] for f in folio_stats)
print(f"\n  Direction distribution:")
for d, c in direction_counts.most_common():
    print(f"    {d:<15}: {c}")

# ============================================================
# 3. PROGRESSION SHAPE: what path through the grid?
# ============================================================
print(f"\n{'='*70}")
print("3. PROGRESSION SHAPE")
print("=" * 70)

# For each folio, sort unique states and see if there's a natural ordering
# Try ordering by: (a) LOW first, (b) HIGH first, (c) diagonal (sum)

print(f"\n  Can states be ordered as a progression?")
print(f"  Testing: sort by LOW, sort by HIGH, sort by sum(LOW+HIGH)")

progression_types = Counter()
for fs in folio_stats:
    states = fs['unique_states']
    if len(states) < 4:
        fs['prog_type'] = 'TOO_FEW'
        progression_types['TOO_FEW'] += 1
        continue

    # Sort by LOW
    by_low = sorted(states, key=lambda s: (s[0], s[1]))
    # Sort by sum (diagonal)
    by_sum = sorted(states, key=lambda s: (s[0] + s[1], s[0]))
    # Sort by HIGH
    by_high = sorted(states, key=lambda s: (s[1], s[0]))

    # Check if HIGH increases along LOW ordering (positive diagonal)
    lo_seq = [s[0] for s in by_low]
    ho_seq = [s[1] for s in by_low]
    if len(set(lo_seq)) >= 3:
        rho, p = spearmanr(lo_seq, ho_seq)
    else:
        rho, p = 0, 1

    if rho > 0.3 and p < 0.1:
        prog = "POSITIVE_DIAGONAL"  # both increase together
    elif rho < -0.3 and p < 0.1:
        prog = "NEGATIVE_DIAGONAL"  # one increases, other decreases
    elif fs['lo_span'] >= 3 and fs['ho_span'] <= 1:
        prog = "LOW_SWEEP"  # sweeps along action axis
    elif fs['ho_span'] >= 3 and fs['lo_span'] <= 1:
        prog = "HIGH_SWEEP"  # sweeps along oversight axis
    elif fs['lo_span'] >= 2 and fs['ho_span'] >= 2:
        prog = "GRID_PATCH"  # covers a 2D area
    else:
        prog = "CLUSTER"

    fs['prog_type'] = prog
    fs['lo_ho_rho'] = rho
    progression_types[prog] += 1

print(f"\n  Progression type distribution:")
for pt, c in progression_types.most_common():
    print(f"    {pt:<22}: {c}")

# ============================================================
# 4. EXAMPLE FOLIO PROGRESSIONS
# ============================================================
print(f"\n{'='*70}")
print("4. EXAMPLE FOLIO PROGRESSIONS")
print("=" * 70)

# Show 8 representative folios with their state paths
# Pick one from each progression type
shown_types = set()
examples = []
for fs in sorted(folio_stats, key=lambda x: -x['n_lines']):
    if fs['prog_type'] not in shown_types and fs['n_unique'] >= 5:
        examples.append(fs)
        shown_types.add(fs['prog_type'])
    if len(examples) >= 8:
        break

# Also add the most concentrated and most diverse
folio_stats_sorted = sorted(folio_stats, key=lambda x: x['n_unique'])
if folio_stats_sorted[0] not in examples:
    examples.append(folio_stats_sorted[0])
if folio_stats_sorted[-1] not in examples:
    examples.append(folio_stats_sorted[-1])

for fs in examples:
    folio = fs['folio']
    section = fs['section']
    n_lines = fs['n_lines']
    n_unique = fs['n_unique']
    prog = fs['prog_type']

    print(f"\n  {folio} (Section {section}, {n_lines} lines, {n_unique} unique states, {prog})")

    # Print grid
    states_set = set(fs['unique_states'])
    state_counts = Counter(fs['footprint'])

    print(f"  {'':>10}", end='')
    for h in range(6):
        print(f" {STAGES[h][:4]:>5}", end='')
    print(f"   <- OVERSIGHT")
    print(f"  {'-'*45}")
    for l in range(6):
        print(f"  {STAGES[l][:4]:<6}   ", end='')
        for h in range(6):
            c = state_counts.get((l, h), 0)
            if c > 0:
                print(f" {c:>5}", end='')
            else:
                print(f"   {'.'}", end='')
        print()
    print(f"  ^")
    print(f"  ACTION")

    # Show logical progression (sorted by sum)
    by_sum = sorted(states_set, key=lambda s: (s[0] + s[1], s[0]))
    path_str = ' -> '.join(f"({STAGES[s[0]][:4]},{STAGES[s[1]][:4]})" for s in by_sum)
    print(f"  Path: {path_str}")

# ============================================================
# 5. SECTION-LEVEL PATTERNS
# ============================================================
print(f"\n{'='*70}")
print("5. SECTION-LEVEL PROGRESSION PATTERNS")
print("=" * 70)

section_stats = defaultdict(list)
for fs in folio_stats:
    section_stats[fs['section']].append(fs)

for sec in sorted(section_stats.keys()):
    stats = section_stats[sec]
    n_folios = len(stats)
    mean_unique = np.mean([f['n_unique'] for f in stats])
    mean_lo_center = np.mean([f['lo_center'] for f in stats])
    mean_ho_center = np.mean([f['ho_center'] for f in stats])
    mean_lo_span = np.mean([f['lo_span'] for f in stats])
    mean_ho_span = np.mean([f['ho_span'] for f in stats])

    prog_dist = Counter(f['prog_type'] for f in stats)
    dominant_prog = prog_dist.most_common(1)[0][0] if prog_dist else '?'

    print(f"\n  Section {sec} ({n_folios} folios):")
    print(f"    Center: ACTION={mean_lo_center:.1f}, OVERSIGHT={mean_ho_center:.1f}")
    print(f"    Span:   ACTION={mean_lo_span:.1f}, OVERSIGHT={mean_ho_span:.1f}")
    print(f"    States: {mean_unique:.1f} unique per folio")
    print(f"    Dominant: {dominant_prog}")
    progs = ', '.join(f"{p}({c})" for p, c in prog_dist.most_common(3))
    print(f"    Types: {progs}")

# ============================================================
# 6. COMMON PROCESS ARCS
# ============================================================
print(f"\n{'='*70}")
print("6. COMMON PROCESS ARCS ACROSS FOLIOS")
print("=" * 70)

# What fraction of folios include each stage pair?
pair_folio_rate = Counter()
for fs in folio_stats:
    for state in set(fs['unique_states']):
        pair_folio_rate[state] += 1

total_folios = len(folio_stats)
print(f"\n  State presence rate across {total_folios} folios:")
print(f"  {'':>10}", end='')
for h in range(6):
    print(f" {STAGES[h][:4]:>5}", end='')
print()
print(f"  {'-'*45}")
for l in range(6):
    print(f"  {STAGES[l][:4]:<6}   ", end='')
    for h in range(6):
        rate = pair_folio_rate.get((l, h), 0) / total_folios * 100
        if rate >= 1:
            print(f" {rate:>4.0f}%", end='')
        else:
            print(f"   {'.'}", end='')
    print()

# What's the "universal" arc? States present in >40% of folios
universal_states = sorted(
    [s for s, c in pair_folio_rate.items() if c / total_folios > 0.40],
    key=lambda s: (s[0] + s[1], s[0])
)
if universal_states:
    print(f"\n  Universal states (>40% of folios):")
    for s in universal_states:
        rate = pair_folio_rate[s] / total_folios * 100
        print(f"    ({STAGES[s[0]][:4]}, {STAGES[s[1]][:4]}): {rate:.0f}%")

    arc_str = ' -> '.join(f"({STAGES[s[0]][:4]},{STAGES[s[1]][:4]})" for s in universal_states)
    print(f"\n  Universal arc: {arc_str}")

# ============================================================
# 7. TRANSITION ANALYSIS
# ============================================================
print(f"\n{'='*70}")
print("7. STATE TRANSITIONS (between unique states within folios)")
print("=" * 70)

# For each folio's unique states sorted by sum, what transitions occur?
lo_transitions = Counter()  # (delta_lo) counts
ho_transitions = Counter()
joint_transitions = Counter()

for fs in folio_stats:
    by_sum = sorted(set(fs['unique_states']), key=lambda s: (s[0] + s[1], s[0]))
    for i in range(len(by_sum) - 1):
        dlo = by_sum[i+1][0] - by_sum[i][0]
        dho = by_sum[i+1][1] - by_sum[i][1]
        lo_transitions[dlo] += 1
        ho_transitions[dho] += 1
        joint_transitions[(dlo, dho)] += 1

print(f"\n  LOW (action) transitions along progression:")
for delta in sorted(lo_transitions.keys()):
    c = lo_transitions[delta]
    pct = c / sum(lo_transitions.values()) * 100
    direction = "UP" if delta > 0 else "DOWN" if delta < 0 else "SAME"
    print(f"    {delta:>+2}: {c:>4} ({pct:>4.1f}%) {direction}")

print(f"\n  HIGH (oversight) transitions along progression:")
for delta in sorted(ho_transitions.keys()):
    c = ho_transitions[delta]
    pct = c / sum(ho_transitions.values()) * 100
    direction = "UP" if delta > 0 else "DOWN" if delta < 0 else "SAME"
    print(f"    {delta:>+2}: {c:>4} ({pct:>4.1f}%) {direction}")

# Net direction
lo_up = sum(c for d, c in lo_transitions.items() if d > 0)
lo_down = sum(c for d, c in lo_transitions.items() if d < 0)
lo_same = lo_transitions.get(0, 0)
ho_up = sum(c for d, c in ho_transitions.items() if d > 0)
ho_down = sum(c for d, c in ho_transitions.items() if d < 0)
ho_same = ho_transitions.get(0, 0)

print(f"\n  Net direction:")
print(f"    ACTION:    {lo_up} up, {lo_same} same, {lo_down} down -> {'INCREASING' if lo_up > lo_down else 'DECREASING' if lo_down > lo_up else 'BALANCED'}")
print(f"    OVERSIGHT: {ho_up} up, {ho_same} same, {ho_down} down -> {'INCREASING' if ho_up > ho_down else 'DECREASING' if ho_down > ho_up else 'BALANCED'}")

# ============================================================
# SAVE
# ============================================================
result = {
    'n_folios': len(good_folios),
    'n_with_progression': len(folio_stats),
    'connectivity': {
        'connected_rate': round(float(connected_rate), 3),
        'mean_unique_states': round(float(np.mean([f['n_unique'] for f in folio_stats])), 1),
        'mean_lo_span': round(float(np.mean([f['lo_span'] for f in folio_stats])), 1),
        'mean_ho_span': round(float(np.mean([f['ho_span'] for f in folio_stats])), 1),
    },
    'progression_types': dict(progression_types),
    'section_profiles': {
        sec: {
            'n_folios': len(stats),
            'mean_lo_center': round(float(np.mean([f['lo_center'] for f in stats])), 2),
            'mean_ho_center': round(float(np.mean([f['ho_center'] for f in stats])), 2),
            'dominant_type': Counter(f['prog_type'] for f in stats).most_common(1)[0][0],
        }
        for sec, stats in section_stats.items()
    },
    'universal_states': [
        {'low': STAGES[s[0]], 'high': STAGES[s[1]],
         'rate': round(float(pair_folio_rate[s] / total_folios * 100), 1)}
        for s in universal_states
    ] if universal_states else [],
    'transitions': {
        'action_up_pct': round(float(lo_up / (lo_up + lo_down + lo_same) * 100), 1) if (lo_up + lo_down + lo_same) > 0 else 0,
        'oversight_up_pct': round(float(ho_up / (ho_up + ho_down + ho_same) * 100), 1) if (ho_up + ho_down + ho_same) > 0 else 0,
    },
}

out_path = Path(__file__).resolve().parent.parent / "results" / "38_folio_progression.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
