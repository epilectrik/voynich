"""
47_shuffle_attractor_control.py

SHUFFLE CONTROL for the attractor state at (LATE,LATE) = (3,3).

Script 42 found an attractor with 100% convergent flow (rho=+0.881).
Question: is this convergence genuine, or does it arise trivially from
FL's positional gradient (C777) which makes LATE tokens more common?

Strategy:
  - Within each folio, randomly redistribute FL tokens across lines
    (preserving per-folio FL token counts, breaking line-level associations)
  - Recompute line coordinates and attractor statistics
  - 1000 iterations to build a null distribution
  - Compare observed convergence fraction and distance-correction rho
    against null

Checks:
  1. Observed convergence fraction exceeds 95th percentile of null (p<0.05)
  2. Observed distance-correction rho exceeds 95th percentile of null
  3. Attractor location stability: same cell in >80% of shuffles = trivial;
     different cell in >50% = observed is special
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

# ============================================================
# Build data (identical pipeline to script 42)
# ============================================================
line_tokens = defaultdict(list)
folio_lines_ordered = defaultdict(list)

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in [k for k in folio_lines_ordered[t.folio]]:
        folio_lines_ordered[t.folio].append(key)

for f in folio_lines_ordered:
    seen = set()
    deduped = []
    for k in folio_lines_ordered[f]:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    folio_lines_ordered[f] = deduped

# Fit GMMs (ONCE, reuse for all shuffles)
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
# Extract FL token info per line (for shuffling)
# ============================================================
# For each line, store:
#   - list of (token_index_in_line, fl_middle) for FL tokens
#   - line length n
# For shuffling: collect all FL entries within a folio, redistribute across lines

line_fl_entries = {}  # line_key -> list of (position_in_line, fl_middle)
line_lengths = {}     # line_key -> n

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    line_lengths[line_key] = n
    if n <= 1:
        continue
    fl_entries = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP and m.middle in gmm_models:
            fl_entries.append((idx, m.middle))
    line_fl_entries[line_key] = fl_entries


def compute_line_coords_from_fl_entries(fl_entries_by_line, line_lengths_dict):
    """
    Given per-line FL entries (list of (position, middle)),
    compute (lo, ho) coordinates for each line.

    Returns dict: line_key -> {'lo': int, 'ho': int}
    """
    coords = {}
    for line_key, fl_entries in fl_entries_by_line.items():
        n = line_lengths_dict.get(line_key, 0)
        if n < 6 or not fl_entries:
            continue

        fl_info = []
        for pos_idx, mid in fl_entries:
            pos = pos_idx / (n - 1) if n > 1 else 0.5
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
        coords[line_key] = {'lo': lo, 'ho': ho}

    return coords


def compute_attractor_stats(coords, folio_lines):
    """
    Given line coordinates and folio ordering, compute:
      - attractor cell (most common (lo, ho))
      - convergence fraction (fraction of non-attractor states whose
        mean transition vector points toward the attractor)
      - distance-correction rho (Spearman: distance-to-attractor vs
        magnitude of step toward attractor)

    Returns dict with attractor, convergence_frac, rho, n_states_tested.
    """
    if not coords:
        return {'attractor': None, 'convergence_frac': 0.0, 'rho': 0.0,
                'n_states_tested': 0}

    # State frequency
    state_freq = Counter()
    for c in coords.values():
        state_freq[(c['lo'], c['ho'])] += 1

    attractor = state_freq.most_common(1)[0][0]

    # Build transitions
    transitions = Counter()
    for folio, keys in folio_lines.items():
        coordinated = [(k, coords[k]) for k in keys if k in coords]
        for i in range(len(coordinated) - 1):
            from_state = (coordinated[i][1]['lo'], coordinated[i][1]['ho'])
            to_state = (coordinated[i+1][1]['lo'], coordinated[i+1][1]['ho'])
            transitions[(from_state, to_state)] += 1

    # For each non-attractor state with enough transitions, compute mean flow
    state_flow = {}
    for state in state_freq:
        if state == attractor:
            continue
        outgoing = [(to, count) for (fr, to), count in transitions.items()
                     if fr == state]
        if not outgoing:
            continue
        total_out = sum(c for _, c in outgoing)
        if total_out < 3:
            continue
        mean_lo_shift = sum((to[0] - state[0]) * c for to, c in outgoing) / total_out
        mean_ho_shift = sum((to[1] - state[1]) * c for to, c in outgoing) / total_out
        state_flow[state] = {
            'mean_lo_shift': mean_lo_shift,
            'mean_ho_shift': mean_ho_shift,
            'n_transitions': total_out,
        }

    if not state_flow:
        return {'attractor': attractor, 'convergence_frac': 0.0, 'rho': 0.0,
                'n_states_tested': 0}

    # Convergence: does mean vector point toward attractor?
    toward = 0
    away = 0
    dists_from_att = []
    shifts_toward_att = []

    for state, flow in state_flow.items():
        # Distance before and after the mean step
        dist_before = abs(state[0] - attractor[0]) + abs(state[1] - attractor[1])
        next_lo = state[0] + flow['mean_lo_shift']
        next_ho = state[1] + flow['mean_ho_shift']
        dist_after = abs(next_lo - attractor[0]) + abs(next_ho - attractor[1])

        if dist_after < dist_before:
            toward += 1
        else:
            away += 1

        # For rho: component of shift toward attractor
        dir_lo = attractor[0] - state[0]
        dir_ho = attractor[1] - state[1]
        norm = np.sqrt(dir_lo**2 + dir_ho**2)
        if norm > 0:
            shift_toward = (flow['mean_lo_shift'] * dir_lo +
                            flow['mean_ho_shift'] * dir_ho) / norm
        else:
            shift_toward = 0.0
        dists_from_att.append(dist_before)
        shifts_toward_att.append(shift_toward)

    convergence_frac = toward / (toward + away) if (toward + away) > 0 else 0.0

    if len(dists_from_att) > 4:
        rho, _ = spearmanr(dists_from_att, shifts_toward_att)
        if np.isnan(rho):
            rho = 0.0
    else:
        rho = 0.0

    return {
        'attractor': attractor,
        'convergence_frac': convergence_frac,
        'rho': rho,
        'n_states_tested': toward + away,
    }


# ============================================================
# Compute OBSERVED statistics
# ============================================================
print("=" * 70)
print("47. SHUFFLE ATTRACTOR CONTROL")
print("=" * 70)

obs_coords = compute_line_coords_from_fl_entries(line_fl_entries, line_lengths)
obs_stats = compute_attractor_stats(obs_coords, folio_lines_ordered)

print(f"\nLines with coordinates: {len(obs_coords)}")
print(f"\nObserved attractor statistics:")
print(f"  Attractor cell: ({obs_stats['attractor'][0]}, {obs_stats['attractor'][1]})"
      f" = ({STAGES[obs_stats['attractor'][0]]}, {STAGES[obs_stats['attractor'][1]]})")
print(f"  Convergence fraction: {obs_stats['convergence_frac']:.3f}"
      f" ({obs_stats['n_states_tested']} non-attractor states tested)")
print(f"  Distance-correction rho: {obs_stats['rho']:+.3f}")


# ============================================================
# SHUFFLE TEST (1000 iterations)
# ============================================================
print(f"\n{'='*70}")
print("SHUFFLE TEST (1000 iterations)")
print("=" * 70)
print("\n  Within each folio, randomly redistribute FL tokens across lines.")
print("  Preserves: per-folio FL count, FL MIDDLE distribution, line lengths.")
print("  Breaks: which FL appears in which line (the line-level association).\n")

rng = np.random.RandomState(42)
N_SHUFFLES = 1000

null_convergence = []
null_rho = []
null_attractor = []

for iteration in range(N_SHUFFLES):
    # Build shuffled FL entries
    shuffled_fl_entries = {}

    for folio, keys in folio_lines_ordered.items():
        # Collect all FL entries from this folio (as (middle, original_position_index) pairs)
        # We need the position within line to recompute GMM mode, so we keep track
        # of which slot each FL occupies
        folio_fl_middles = []  # just the middles
        folio_line_fl_slots = {}  # line_key -> list of position indices that were FL

        for line_key in keys:
            entries = line_fl_entries.get(line_key, [])
            slots = [pos_idx for pos_idx, mid in entries]
            middles = [mid for pos_idx, mid in entries]
            folio_line_fl_slots[line_key] = slots
            folio_fl_middles.extend(middles)

        if not folio_fl_middles:
            # No FL tokens in this folio, copy as-is (empty)
            for line_key in keys:
                shuffled_fl_entries[line_key] = []
            continue

        # Shuffle the middles
        rng.shuffle(folio_fl_middles)

        # Redistribute shuffled middles into the same slots
        mid_idx = 0
        for line_key in keys:
            slots = folio_line_fl_slots[line_key]
            new_entries = []
            for slot_pos in slots:
                new_entries.append((slot_pos, folio_fl_middles[mid_idx]))
                mid_idx += 1
            shuffled_fl_entries[line_key] = new_entries

    # Compute coordinates from shuffled entries
    shuf_coords = compute_line_coords_from_fl_entries(shuffled_fl_entries, line_lengths)
    shuf_stats = compute_attractor_stats(shuf_coords, folio_lines_ordered)

    null_convergence.append(shuf_stats['convergence_frac'])
    null_rho.append(shuf_stats['rho'])
    if shuf_stats['attractor'] is not None:
        null_attractor.append(shuf_stats['attractor'])

    if (iteration + 1) % 200 == 0:
        print(f"  Completed {iteration + 1}/{N_SHUFFLES} shuffles...")

null_convergence = np.array(null_convergence)
null_rho = np.array(null_rho)

print(f"\n  Shuffle complete. {len(null_convergence)} valid iterations.")

# ============================================================
# Compute p-values and null distribution statistics
# ============================================================
print(f"\n{'='*70}")
print("NULL DISTRIBUTION RESULTS")
print("=" * 70)

# Convergence fraction
p_conv = float(np.mean(null_convergence >= obs_stats['convergence_frac']))
null_conv_mean = float(np.mean(null_convergence))
null_conv_95 = float(np.percentile(null_convergence, 95))

print(f"\n  Convergence fraction:")
print(f"    Observed:     {obs_stats['convergence_frac']:.3f}")
print(f"    Null mean:    {null_conv_mean:.3f}")
print(f"    Null 95th:    {null_conv_95:.3f}")
print(f"    Null min/max: {float(np.min(null_convergence)):.3f} / {float(np.max(null_convergence)):.3f}")
print(f"    p-value:      {p_conv:.4f}")

# Distance-correction rho
p_rho = float(np.mean(null_rho >= obs_stats['rho']))
null_rho_mean = float(np.mean(null_rho))
null_rho_95 = float(np.percentile(null_rho, 95))

print(f"\n  Distance-correction rho:")
print(f"    Observed:     {obs_stats['rho']:+.3f}")
print(f"    Null mean:    {null_rho_mean:+.3f}")
print(f"    Null 95th:    {null_rho_95:+.3f}")
print(f"    Null min/max: {float(np.min(null_rho)):+.3f} / {float(np.max(null_rho)):+.3f}")
print(f"    p-value:      {p_rho:.4f}")

# Attractor location stability
attractor_counts = Counter(null_attractor)
total_with_attractor = len(null_attractor)
obs_att = obs_stats['attractor']
obs_att_in_null = attractor_counts.get(obs_att, 0)
obs_att_null_frac = obs_att_in_null / total_with_attractor if total_with_attractor > 0 else 0.0

most_common_null_att = attractor_counts.most_common(1)[0] if attractor_counts else (None, 0)
most_common_null_frac = most_common_null_att[1] / total_with_attractor if total_with_attractor > 0 else 0.0

print(f"\n  Attractor location stability:")
print(f"    Observed attractor: ({obs_att[0]}, {obs_att[1]}) = "
      f"({STAGES[obs_att[0]]}, {STAGES[obs_att[1]]})")
print(f"    Same cell in null:  {obs_att_in_null}/{total_with_attractor}"
      f" ({obs_att_null_frac*100:.1f}%)")
if most_common_null_att[0] is not None:
    mc = most_common_null_att[0]
    print(f"    Most common null attractor: ({mc[0]}, {mc[1]}) = "
          f"({STAGES[mc[0]]}, {STAGES[mc[1]]})"
          f" in {most_common_null_att[1]} shuffles ({most_common_null_frac*100:.1f}%)")

print(f"\n  Top 5 null attractor locations:")
for (lo, ho), count in attractor_counts.most_common(5):
    pct = count / total_with_attractor * 100
    print(f"    ({lo}, {ho}) = ({STAGES[lo]}, {STAGES[ho]}): "
          f"{count} ({pct:.1f}%)")


# ============================================================
# CHECKS
# ============================================================
print(f"\n{'='*70}")
print("CHECKS")
print("=" * 70)

check_1 = bool(p_conv < 0.05)
check_2 = bool(p_rho < 0.05)
# Check 3: same cell in >80% = trivial, different cell in >50% = special
# If the observed attractor appears in >80% of shuffles, the location is
# a trivial consequence of the marginals, not a dynamical property
attractor_trivial = obs_att_null_frac > 0.80
attractor_special = obs_att_null_frac < 0.50
check_3 = bool(attractor_special)

print(f"\n  check_1 (convergence fraction p < 0.05): {'PASS' if check_1 else 'FAIL'}")
print(f"    Observed = {obs_stats['convergence_frac']:.3f}, "
      f"null 95th = {null_conv_95:.3f}, p = {p_conv:.4f}")

print(f"\n  check_2 (distance-correction rho p < 0.05): {'PASS' if check_2 else 'FAIL'}")
print(f"    Observed = {obs_stats['rho']:+.3f}, "
      f"null 95th = {null_rho_95:+.3f}, p = {p_rho:.4f}")

print(f"\n  check_3 (attractor location is special): {'PASS' if check_3 else 'FAIL'}")
print(f"    Observed attractor in {obs_att_null_frac*100:.1f}% of shuffles")
if attractor_trivial:
    print(f"    >80% -- location is TRIVIAL (arises from marginal distribution)")
elif attractor_special:
    print(f"    <50% -- location is SPECIAL (not determined by marginals alone)")
else:
    print(f"    Between 50-80% -- location is PARTIALLY determined by marginals")


# ============================================================
# VERDICT
# ============================================================
print(f"\n{'='*70}")
print("VERDICT")
print("=" * 70)

n_pass = sum([check_1, check_2, check_3])
print(f"\n  Checks passed: {n_pass}/3")
print(f"    check_1 (convergence exceeds null): {'PASS' if check_1 else 'FAIL'}")
print(f"    check_2 (rho exceeds null):         {'PASS' if check_2 else 'FAIL'}")
print(f"    check_3 (location is special):      {'PASS' if check_3 else 'FAIL'}")

if check_1 and check_2:
    verdict = "GENUINE_ATTRACTOR"
    expl = ("Both convergence fraction and distance-correction rho exceed "
            "the 95th percentile of the null distribution. The attractor "
            "dynamics are NOT an artifact of FL's positional gradient.")
elif not check_1 and not check_2:
    verdict = "ARTIFACT"
    expl = ("Neither convergence fraction nor distance-correction rho "
            "exceeds the null distribution. The apparent attractor at "
            "(LATE,LATE) is an artifact of FL's positional gradient "
            "making LATE tokens more common.")
else:
    verdict = "PARTIAL"
    passing = []
    failing = []
    if check_1:
        passing.append("convergence fraction")
    else:
        failing.append("convergence fraction")
    if check_2:
        passing.append("distance-correction rho")
    else:
        failing.append("distance-correction rho")
    expl = (f"Mixed result: {', '.join(passing)} exceeds null, "
            f"but {', '.join(failing)} does not. The attractor signal "
            f"is partially genuine but may be amplified by the "
            f"positional gradient.")

print(f"\n  VERDICT: {verdict}")
print(f"  {expl}")

if check_3:
    print(f"\n  Note: The attractor LOCATION ({STAGES[obs_att[0]]}, "
          f"{STAGES[obs_att[1]]}) is special -- shuffles do not "
          f"consistently produce an attractor at the same cell.")
elif attractor_trivial:
    print(f"\n  Note: The attractor LOCATION ({STAGES[obs_att[0]]}, "
          f"{STAGES[obs_att[1]]}) is trivial -- shuffles produce "
          f"the same attractor cell >80% of the time. The location "
          f"is determined by marginal FL stage frequencies, not "
          f"by dynamical convergence.")
else:
    print(f"\n  Note: The attractor location appears in "
          f"{obs_att_null_frac*100:.1f}% of shuffles (neither "
          f"clearly trivial nor clearly special).")


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

results = {
    'n_lines': len(obs_coords),
    'observed': {
        'attractor': list(obs_stats['attractor']),
        'attractor_label': [STAGES[obs_stats['attractor'][0]],
                            STAGES[obs_stats['attractor'][1]]],
        'convergence_frac': round(float(obs_stats['convergence_frac']), 3),
        'distance_correction_rho': round(float(obs_stats['rho']), 3),
        'n_states_tested': obs_stats['n_states_tested'],
    },
    'null_distribution': {
        'n_shuffles': N_SHUFFLES,
        'convergence': {
            'mean': round(null_conv_mean, 3),
            'percentile_95': round(null_conv_95, 3),
            'min': round(float(np.min(null_convergence)), 3),
            'max': round(float(np.max(null_convergence)), 3),
            'p_value': round(p_conv, 4),
        },
        'rho': {
            'mean': round(null_rho_mean, 3),
            'percentile_95': round(null_rho_95, 3),
            'min': round(float(np.min(null_rho)), 3),
            'max': round(float(np.max(null_rho)), 3),
            'p_value': round(p_rho, 4),
        },
        'attractor_location': {
            'observed_in_null_frac': round(obs_att_null_frac, 3),
            'most_common_null': list(most_common_null_att[0]) if most_common_null_att[0] else None,
            'most_common_null_frac': round(most_common_null_frac, 3),
            'top_5': [
                {'cell': [lo, ho], 'label': [STAGES[lo], STAGES[ho]],
                 'count': count, 'frac': round(count / total_with_attractor, 3)}
                for (lo, ho), count in attractor_counts.most_common(5)
            ],
        },
    },
    'checks': {
        'check_1_convergence_exceeds_null': bool(check_1),
        'check_2_rho_exceeds_null': bool(check_2),
        'check_3_location_is_special': bool(check_3),
    },
    'verdict': verdict,
    'explanation': expl,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '47_shuffle_attractor_control.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
