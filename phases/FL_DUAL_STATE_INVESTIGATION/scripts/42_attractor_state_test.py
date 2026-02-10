"""
42_attractor_state_test.py

Is there an "ideal" attractor state on the FL grid, with other lines
serving as error correction toward it?

Control theory model: the apparatus has a target operating point. The FL
coordinate tells you WHERE you are relative to that target. Lines at the
target state = maintenance. Lines away from target = corrective action.

Tests:
  1. ATTRACTOR IDENTIFICATION: which state is the "center of mass" of
     all transitions? Do transition flows converge on a specific region?
  2. TRANSITION ASYMMETRY: from peripheral states, do transitions point
     inward (toward attractor)? From the attractor, do they stay?
  3. CONTENT GRADIENT: does the qo/sh/ok mix shift as you move away
     from the attractor? (more qo at periphery = corrective, more
     sh/ok at center = monitoring/maintenance)
  4. PER-FOLIO ATTRACTOR: does each folio have its own attractor, or
     is there one universal target?
  5. HAZARD CONNECTION: are peripheral states (far from attractor)
     associated with hazard prefixes/classes?
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

PREFIXES = {
    'qo': 'ACTION', 'sh': 'SENSE', 'ch': 'INTERACT', 'ok': 'CHECK',
    'ol': 'LINK', 'ot': 'TEST', 'd': 'YIELD', 'or': 'ORIENT',
}

tx = Transcript()
morph = Morphology()
MIN_N = 50

# ============================================================
# Build data
# ============================================================
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

# Assign coordinates + extract per-line prefix/role profiles
line_coords = {}
line_profiles = {}

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    prefix_counts = Counter()
    role_counts = Counter()

    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        # Prefix profile (non-FL tokens only = center content)
        if not is_fl and m and m.prefix:
            prefix_counts[m.prefix] += 1

        # Role profile
        role = token_to_role.get(t.word, 'UNKNOWN')
        role_counts[role] += 1

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

    line_coords[line_key] = {'lo': lo, 'ho': ho, 'low': low_stage, 'high': high_stage}

    # Normalize prefix/role counts
    total_pfx = sum(prefix_counts.values())
    line_profiles[line_key] = {
        'prefix_counts': dict(prefix_counts),
        'role_counts': dict(role_counts),
        'total_center': total_pfx,
        'qo_rate': prefix_counts.get('qo', 0) / max(total_pfx, 1),
        'sh_rate': prefix_counts.get('sh', 0) / max(total_pfx, 1),
        'ch_rate': prefix_counts.get('ch', 0) / max(total_pfx, 1),
        'ok_rate': prefix_counts.get('ok', 0) / max(total_pfx, 1),
        'ol_rate': prefix_counts.get('ol', 0) / max(total_pfx, 1),
    }

print(f"Lines with coordinates + profiles: {len(line_coords)}")

# ============================================================
# 1. ATTRACTOR IDENTIFICATION
# ============================================================
print(f"\n{'='*70}")
print("1. ATTRACTOR IDENTIFICATION")
print("=" * 70)

# State frequency
state_freq = Counter()
for key, c in line_coords.items():
    state_freq[(c['lo'], c['ho'])] += 1

total_lines = sum(state_freq.values())
print(f"\n  State frequency (top 10):")
for (lo, ho), count in state_freq.most_common(10):
    pct = count / total_lines * 100
    print(f"    ({STAGES[lo][:4]},{STAGES[ho][:4]}): {count:>4} ({pct:.1f}%)")

# Center of mass
all_lo = [c['lo'] for c in line_coords.values()]
all_ho = [c['ho'] for c in line_coords.values()]
com_lo = np.mean(all_lo)
com_ho = np.mean(all_ho)
print(f"\n  Center of mass: ACTION={com_lo:.2f} ({STAGES[int(round(com_lo))][:4]}), "
      f"OVERSIGHT={com_ho:.2f} ({STAGES[int(round(com_ho))][:4]})")

# The most frequent state
top_state = state_freq.most_common(1)[0][0]
top_count = state_freq.most_common(1)[0][1]
print(f"  Most frequent state: ({STAGES[top_state[0]][:4]},{STAGES[top_state[1]][:4]}) "
      f"with {top_count} lines ({top_count/total_lines*100:.1f}%)")

# ============================================================
# 2. TRANSITION FLOW ANALYSIS
# ============================================================
print(f"\n{'='*70}")
print("2. TRANSITION FLOW (within folio line sequences)")
print("=" * 70)

# Build transition counts between consecutive coordinated lines
transitions = Counter()  # (from_state, to_state) -> count
for folio, keys in folio_lines_ordered.items():
    coordinated = [(k, line_coords[k]) for k in keys if k in line_coords]
    for i in range(len(coordinated) - 1):
        from_state = (coordinated[i][1]['lo'], coordinated[i][1]['ho'])
        to_state = (coordinated[i+1][1]['lo'], coordinated[i+1][1]['ho'])
        transitions[(from_state, to_state)] += 1

# For each state: compute mean transition direction
state_flow = {}
for state in state_freq:
    outgoing = [(to, count) for (fr, to), count in transitions.items() if fr == state]
    if not outgoing:
        continue
    total_out = sum(c for _, c in outgoing)
    mean_lo_shift = sum((to[0] - state[0]) * c for to, c in outgoing) / total_out
    mean_ho_shift = sum((to[1] - state[1]) * c for to, c in outgoing) / total_out
    state_flow[state] = {
        'mean_lo_shift': mean_lo_shift,
        'mean_ho_shift': mean_ho_shift,
        'n_transitions': total_out,
    }

# Do flows converge toward the center of mass?
print(f"\n  State flow vectors (mean transition direction from each state):")
print(f"  {'State':<16} {'N':>5} {'dACTION':>10} {'dOVERSIGHT':>12} {'Toward COM?':>12}")

toward_com = 0
away_com = 0
for state in sorted(state_flow.keys()):
    flow = state_flow[state]
    if flow['n_transitions'] < 3:
        continue
    # Is the flow toward the center of mass?
    dist_before = abs(state[0] - com_lo) + abs(state[1] - com_ho)
    next_lo = state[0] + flow['mean_lo_shift']
    next_ho = state[1] + flow['mean_ho_shift']
    dist_after = abs(next_lo - com_lo) + abs(next_ho - com_ho)
    converging = dist_after < dist_before
    if converging:
        toward_com += 1
    else:
        away_com += 1
    label = "TOWARD" if converging else "AWAY"
    print(f"  ({STAGES[state[0]][:4]},{STAGES[state[1]][:4]})"
          f"  {flow['n_transitions']:>5}"
          f"  {flow['mean_lo_shift']:>+9.2f}"
          f"  {flow['mean_ho_shift']:>+11.2f}"
          f"  {label:>12}")

convergence_rate = toward_com / (toward_com + away_com) if (toward_com + away_com) > 0 else 0
print(f"\n  Converging toward COM: {toward_com}/{toward_com + away_com} ({convergence_rate*100:.1f}%)")

# Distance from COM vs transition magnitude (toward COM)
# States far from COM should have larger inward shifts
dists_from_com = []
shifts_toward_com = []
for state, flow in state_flow.items():
    if flow['n_transitions'] < 3:
        continue
    dist = abs(state[0] - com_lo) + abs(state[1] - com_ho)
    # Component of shift toward COM
    dir_lo = com_lo - state[0]
    dir_ho = com_ho - state[1]
    norm = np.sqrt(dir_lo**2 + dir_ho**2) if dir_lo != 0 or dir_ho != 0 else 1
    shift_toward = (flow['mean_lo_shift'] * dir_lo + flow['mean_ho_shift'] * dir_ho) / norm
    dists_from_com.append(dist)
    shifts_toward_com.append(shift_toward)

if len(dists_from_com) > 5:
    rho_conv, p_conv = spearmanr(dists_from_com, shifts_toward_com)
    print(f"\n  Distance from COM vs shift toward COM:")
    print(f"    rho={rho_conv:+.3f}, p={p_conv:.4f}")
    print(f"    (Positive = farther states shift more toward center)")
else:
    rho_conv = 0
    p_conv = 1

pass_2 = convergence_rate > 0.55 and rho_conv > 0.2
print(f"\n  CHECK 2 (convergent flow): {'PASS' if pass_2 else 'FAIL'}")

# ============================================================
# 3. CONTENT GRADIENT FROM ATTRACTOR
# ============================================================
print(f"\n{'='*70}")
print("3. CONTENT GRADIENT (prefix rates vs distance from attractor)")
print("=" * 70)

# For each line: compute Manhattan distance from COM
line_dists = []
line_qo = []
line_sh = []
line_ok = []
line_ch = []

for key, c in line_coords.items():
    if key not in line_profiles:
        continue
    prof = line_profiles[key]
    if prof['total_center'] < 2:
        continue
    dist = abs(c['lo'] - com_lo) + abs(c['ho'] - com_ho)
    line_dists.append(dist)
    line_qo.append(prof['qo_rate'])
    line_sh.append(prof['sh_rate'])
    line_ok.append(prof['ok_rate'])
    line_ch.append(prof['ch_rate'])

if line_dists:
    rho_qo, p_qo = spearmanr(line_dists, line_qo)
    rho_sh, p_sh = spearmanr(line_dists, line_sh)
    rho_ok, p_ok = spearmanr(line_dists, line_ok)
    rho_ch, p_ch = spearmanr(line_dists, line_ch)

    print(f"\n  Correlation: distance from center vs prefix rate")
    print(f"    qo (ACTION):    rho={rho_qo:+.3f}, p={p_qo:.4f}")
    print(f"    sh (SENSE):     rho={rho_sh:+.3f}, p={p_sh:.4f}")
    print(f"    ok (CHECK):     rho={rho_ok:+.3f}, p={p_ok:.4f}")
    print(f"    ch (INTERACT):  rho={rho_ch:+.3f}, p={p_ch:.4f}")

    # Bin by distance and show prefix profiles
    bins = [(0, 1, 'NEAR'), (1, 2, 'MID'), (2, 3, 'FAR'), (3, 10, 'EXTREME')]
    print(f"\n  Prefix rates by distance from attractor:")
    print(f"  {'Bin':<10} {'N':>5} {'qo%':>8} {'sh%':>8} {'ok%':>8} {'ch%':>8}")
    for lo, hi, label in bins:
        mask = [(i, d) for i, d in enumerate(line_dists) if lo <= d < hi]
        if not mask:
            continue
        idxs = [i for i, d in mask]
        n = len(idxs)
        qo_m = np.mean([line_qo[i] for i in idxs]) * 100
        sh_m = np.mean([line_sh[i] for i in idxs]) * 100
        ok_m = np.mean([line_ok[i] for i in idxs]) * 100
        ch_m = np.mean([line_ch[i] for i in idxs]) * 100
        print(f"  {label:<10} {n:>5} {qo_m:>7.1f}% {sh_m:>7.1f}% {ok_m:>7.1f}% {ch_m:>7.1f}%")

# ============================================================
# 4. PER-FOLIO ATTRACTOR
# ============================================================
print(f"\n{'='*70}")
print("4. PER-FOLIO ATTRACTOR")
print("=" * 70)

folio_attractors = []
for folio, keys in folio_lines_ordered.items():
    coords = [line_coords[k] for k in keys if k in line_coords]
    if len(coords) < 5:
        continue
    folio_com_lo = np.mean([c['lo'] for c in coords])
    folio_com_ho = np.mean([c['ho'] for c in coords])
    # Most frequent state in this folio
    folio_states = Counter((c['lo'], c['ho']) for c in coords)
    folio_top = folio_states.most_common(1)[0]
    folio_attractors.append({
        'folio': folio,
        'section': line_meta[keys[0]]['section'],
        'com': (round(folio_com_lo, 2), round(folio_com_ho, 2)),
        'top_state': folio_top[0],
        'top_count': folio_top[1],
        'top_pct': folio_top[1] / len(coords) * 100,
        'n_lines': len(coords),
    })

# How concentrated is the top state?
top_pcts = [a['top_pct'] for a in folio_attractors]
print(f"\n  Folios with 5+ coordinated lines: {len(folio_attractors)}")
print(f"  Mean top-state concentration: {np.mean(top_pcts):.1f}%")
print(f"  Folios with >30% at one state: {sum(1 for p in top_pcts if p > 30)}")
print(f"  Folios with >50% at one state: {sum(1 for p in top_pcts if p > 50)}")

# Do per-folio COMs cluster?
coms = [(a['com'][0], a['com'][1]) for a in folio_attractors]
com_spread_lo = np.std([c[0] for c in coms])
com_spread_ho = np.std([c[1] for c in coms])
print(f"\n  Per-folio COM spread: ACTION std={com_spread_lo:.2f}, OVERSIGHT std={com_spread_ho:.2f}")

# Is there a universal attractor or folio-specific?
# If universal: low COM spread. If folio-specific: high COM spread
print(f"\n  Per-folio COMs by section:")
section_coms = defaultdict(list)
for a in folio_attractors:
    section_coms[a['section']].append(a['com'])
for sec in sorted(section_coms.keys()):
    coms_sec = section_coms[sec]
    mean_lo = np.mean([c[0] for c in coms_sec])
    mean_ho = np.mean([c[1] for c in coms_sec])
    print(f"    {sec}: mean COM=({mean_lo:.2f}, {mean_ho:.2f}), n={len(coms_sec)}")

# ============================================================
# 5. STATE STABILITY: do lines at the attractor stay there?
# ============================================================
print(f"\n{'='*70}")
print("5. STATE STABILITY (self-transition rate)")
print("=" * 70)

# For each state: what fraction of transitions stay at the same state?
self_trans = {}
for state in state_freq:
    if state_freq[state] < 5:
        continue
    total_from = sum(c for (fr, to), c in transitions.items() if fr == state)
    self_count = transitions.get((state, state), 0)
    if total_from > 0:
        self_trans[state] = {
            'self_rate': self_count / total_from,
            'self_count': self_count,
            'total': total_from,
        }

print(f"\n  {'State':<16} {'Self-trans':>10} {'Total':>8} {'Rate':>8}")
for state in sorted(self_trans.keys()):
    st = self_trans[state]
    dist = abs(state[0] - com_lo) + abs(state[1] - com_ho)
    print(f"  ({STAGES[state[0]][:4]},{STAGES[state[1]][:4]})"
          f"  {st['self_count']:>10}"
          f"  {st['total']:>8}"
          f"  {st['self_rate']*100:>7.1f}%")

# Does self-transition rate correlate with proximity to COM?
st_dists = []
st_rates = []
for state, st in self_trans.items():
    dist = abs(state[0] - com_lo) + abs(state[1] - com_ho)
    st_dists.append(dist)
    st_rates.append(st['self_rate'])

if len(st_dists) > 5:
    rho_self, p_self = spearmanr(st_dists, st_rates)
    print(f"\n  Distance from COM vs self-transition rate:")
    print(f"    rho={rho_self:+.3f}, p={p_self:.4f}")
    print(f"    (Negative = central states stay put more)")
else:
    rho_self = 0
    p_self = 1

# ============================================================
# 6. VERDICT
# ============================================================
print(f"\n{'='*70}")
print("6. VERDICT")
print("=" * 70)

check1 = state_freq.most_common(1)[0][1] / total_lines > 0.12  # top state > 12%
check2 = pass_2
check3 = (p_qo < 0.05 or p_sh < 0.05) if line_dists else False
check4 = np.mean(top_pcts) > 25 if top_pcts else False
check5 = rho_self < -0.2 and p_self < 0.1

checks = [check1, check2, check3, check4, check5]
n_pass = sum(checks)

print(f"\n  Checks passed: {n_pass}/5")
print(f"  1. Dominant attractor state (>12%):  {'PASS' if check1 else 'FAIL'}")
print(f"  2. Convergent transition flow:       {'PASS' if check2 else 'FAIL'}")
print(f"  3. Content shifts with distance:     {'PASS' if check3 else 'FAIL'}")
print(f"  4. Per-folio concentration (>25%):   {'PASS' if check4 else 'FAIL'}")
print(f"  5. Central states more stable:       {'PASS' if check5 else 'FAIL'}")

if n_pass >= 4:
    verdict = "ATTRACTOR_MODEL"
    expl = ("Clear attractor state with convergent flow, content gradient, "
            "and stability gradient. Lines away from attractor are corrective.")
elif n_pass >= 2:
    verdict = "WEAK_ATTRACTOR"
    expl = ("Some attractor behavior (convergence or content gradient) "
            "but not all properties of a clean attractor model.")
else:
    verdict = "NO_ATTRACTOR"
    expl = ("No evidence for single attractor state. The grid may operate "
            "as a traversal space without a preferred target.")

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
    'center_of_mass': {'action': round(float(com_lo), 2), 'oversight': round(float(com_ho), 2)},
    'top_state': {
        'state': [int(top_state[0]), int(top_state[1])],
        'count': int(top_count),
        'pct': round(top_count / total_lines * 100, 1),
    },
    'convergence': {
        'toward_rate': round(float(convergence_rate), 3),
        'rho_dist_vs_shift': round(float(rho_conv), 3),
        'p': round(float(p_conv), 4),
    },
    'content_gradient': {
        'rho_qo': round(float(rho_qo), 3) if line_dists else None,
        'rho_sh': round(float(rho_sh), 3) if line_dists else None,
        'rho_ok': round(float(rho_ok), 3) if line_dists else None,
        'p_qo': round(float(p_qo), 4) if line_dists else None,
    },
    'per_folio': {
        'mean_top_pct': round(float(np.mean(top_pcts)), 1) if top_pcts else None,
        'com_spread': {
            'action': round(float(com_spread_lo), 2),
            'oversight': round(float(com_spread_ho), 2),
        },
    },
    'stability': {
        'rho_dist_vs_self_rate': round(float(rho_self), 3),
        'p': round(float(p_self), 4),
    },
    'checks': [bool(c) for c in checks],
    'verdict': verdict,
    'explanation': expl,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '42_attractor_state_test.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
