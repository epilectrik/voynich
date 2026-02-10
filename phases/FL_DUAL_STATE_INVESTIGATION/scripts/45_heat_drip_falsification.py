"""
45_heat_drip_falsification.py

STRESS TEST for the heat/drip model of the FL coordinate system.

Script 44 found 5/5 physics-consistent checks. This script attempts to
KILL the model by asking:

  1. NULL DISTRIBUTION: Can random shuffles produce the same "physics-like"
     statistics? If so, the result is meaningless.
  2. AXIS SWAP: If we swap heat<->drip, do physics predictions still hold?
     Thermal lag should be DIRECTIONAL. Symmetric = not thermal.
  3. SECTION OPERATING WINDOWS: Different plant materials should occupy
     different heat/drip regions. Test via Kruskal-Wallis on section COMs.
  4. EXTREME STATE CONTENT: Physically dangerous states should show
     different vocabulary (hazard tokens, etc). Test content divergence.
  5. FOLIO OPERATING RANGE: Each folio's heat-center and drip-center
     should be positively correlated (materials needing more heat produce
     more drip). Test this correlation.

Each test is designed to FAIL the model, not confirm it.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, kruskal, mannwhitneyu

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load class data for Test 4
class_map_path = (Path(__file__).resolve().parents[3] / 'phases' /
                  'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json')
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

tx = Transcript()
morph = Morphology()
MIN_N = 50

# ============================================================
# Build data (identical pipeline to script 44)
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

# Assign line coordinates
line_coords = {}
line_fl_info_all = {}  # store raw fl_info for permutation tests
line_center_tokens = defaultdict(list)

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue
    fl_info = []
    center_words = []
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
        elif not is_fl:
            center_words.append(t.word)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue
    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    lo = STAGE_ORDER[low_stage]
    ho = STAGE_ORDER[high_stage]
    line_coords[line_key] = {'lo': lo, 'ho': ho}
    line_fl_info_all[line_key] = fl_info
    line_center_tokens[line_key] = center_words

# Pre-compute observed statistics for comparison
all_lo = np.array([c['lo'] for c in line_coords.values()])
all_ho = np.array([c['ho'] for c in line_coords.values()])

obs_rho, obs_rho_p = spearmanr(all_lo, all_ho)
obs_diag_frac = np.mean(np.abs(all_lo - all_ho) <= 1)

# Below diagonal: lo > ho + 1 (heat >> drip)
below = np.sum(all_lo > all_ho + 1)
above = np.sum(all_ho > all_lo + 1)
obs_asymmetry = below / above if above > 0 else float('inf')

# Transition following
ordered_keys = []
for folio, keys in folio_lines_ordered.items():
    coordinated = [k for k in keys if k in line_coords]
    ordered_keys.append(coordinated)

heat_up_drip_obs = []
for folio_keys in ordered_keys:
    for i in range(len(folio_keys) - 1):
        curr = line_coords[folio_keys[i]]
        nxt = line_coords[folio_keys[i + 1]]
        dh = nxt['lo'] - curr['lo']
        dd = nxt['ho'] - curr['ho']
        if dh > 0:
            heat_up_drip_obs.append(dd)
obs_heat_up_drip_mean = np.mean(heat_up_drip_obs) if heat_up_drip_obs else 0.0

print("=" * 70)
print("HEAT/DRIP MODEL FALSIFICATION TEST SUITE")
print("=" * 70)
print(f"\nLines with coordinates: {len(line_coords)}")
print(f"Observed statistics from script 44:")
print(f"  Spearman rho:       {obs_rho:+.3f}")
print(f"  Diagonal fraction:  {obs_diag_frac:.3f}")
print(f"  Asymmetry ratio:    {obs_asymmetry:.2f}")
print(f"  Heat-up -> drip:    {obs_heat_up_drip_mean:+.3f}")

# ============================================================
# TEST 1: NULL DISTRIBUTION (1000 random shuffles)
# ============================================================
print(f"\n{'='*70}")
print("TEST 1: NULL DISTRIBUTION (1000 random shuffles)")
print("=" * 70)
print("\n  Independently shuffling LOW and HIGH assignments across lines.")
print("  If random data produces similar statistics, our result is noise.\n")

rng = np.random.RandomState(42)
N_SHUFFLES = 1000

null_rhos = []
null_diag_fracs = []
null_asymmetries = []
null_heat_up_drip = []

for iteration in range(N_SHUFFLES):
    # Shuffle LOW and HIGH coordinates independently
    shuf_lo = rng.permutation(all_lo)
    shuf_ho = rng.permutation(all_ho)

    # 1. Correlation
    r, _ = spearmanr(shuf_lo, shuf_ho)
    null_rhos.append(r)

    # 2. Diagonal fraction
    diag_f = np.mean(np.abs(shuf_lo - shuf_ho) <= 1)
    null_diag_fracs.append(diag_f)

    # 3. Asymmetry
    b = np.sum(shuf_lo > shuf_ho + 1)
    a = np.sum(shuf_ho > shuf_lo + 1)
    null_asymmetries.append(b / a if a > 0 else float('inf'))

    # 4. Transition following -- pair shuffled coords with line order
    # Reassign shuffled coords to the same line keys
    keys_list = list(line_coords.keys())
    shuf_coords = {keys_list[j]: {'lo': int(shuf_lo[j]), 'ho': int(shuf_ho[j])}
                   for j in range(len(keys_list))}
    hud = []
    for folio_keys in ordered_keys:
        for i in range(len(folio_keys) - 1):
            k1, k2 = folio_keys[i], folio_keys[i + 1]
            if k1 in shuf_coords and k2 in shuf_coords:
                dh = shuf_coords[k2]['lo'] - shuf_coords[k1]['lo']
                dd = shuf_coords[k2]['ho'] - shuf_coords[k1]['ho']
                if dh > 0:
                    hud.append(dd)
    null_heat_up_drip.append(np.mean(hud) if hud else 0.0)

null_rhos = np.array(null_rhos)
null_diag_fracs = np.array(null_diag_fracs)
null_asymmetries = np.array([x for x in null_asymmetries if x < 100])  # filter inf
null_heat_up_drip = np.array(null_heat_up_drip)

# Compute p-values: fraction of null >= observed
p_rho = np.mean(null_rhos >= obs_rho)
p_diag = np.mean(null_diag_fracs >= obs_diag_frac)
p_asym = np.mean(null_asymmetries >= obs_asymmetry)
p_trans = np.mean(null_heat_up_drip >= obs_heat_up_drip_mean)

print(f"  Statistic            Observed    Null mean    Null 95th    p-value  Result")
print(f"  -------------------  ----------  -----------  -----------  -------  ------")

t1_rho_pass = p_rho < 0.05
print(f"  Spearman rho         {obs_rho:>+.3f}       {np.mean(null_rhos):>+.4f}       "
      f"{np.percentile(null_rhos, 95):>+.4f}       {p_rho:.4f}   "
      f"{'PASS' if t1_rho_pass else 'FAIL'}")

t1_diag_pass = p_diag < 0.05
print(f"  Diagonal fraction    {obs_diag_frac:>.3f}       {np.mean(null_diag_fracs):>.4f}       "
      f"{np.percentile(null_diag_fracs, 95):>.4f}       {p_diag:.4f}   "
      f"{'PASS' if t1_diag_pass else 'FAIL'}")

t1_asym_pass = p_asym < 0.05
print(f"  Asymmetry ratio      {obs_asymmetry:>.2f}        {np.mean(null_asymmetries):>.4f}       "
      f"{np.percentile(null_asymmetries, 95):>.4f}       {p_asym:.4f}   "
      f"{'PASS' if t1_asym_pass else 'FAIL'}")

t1_trans_pass = p_trans < 0.05
print(f"  Heat-up->drip mean   {obs_heat_up_drip_mean:>+.3f}       {np.mean(null_heat_up_drip):>+.4f}       "
      f"{np.percentile(null_heat_up_drip, 95):>+.4f}       {p_trans:.4f}   "
      f"{'PASS' if t1_trans_pass else 'FAIL'}")

t1_n_pass = sum([t1_rho_pass, t1_diag_pass, t1_asym_pass, t1_trans_pass])
print(f"\n  PASS criterion: observed must be in top 5% (p < 0.05)")
print(f"  Sub-tests passed: {t1_n_pass}/4")

# Overall test 1 verdict: model survives if at least 3/4 are significant
t1_survives = t1_n_pass >= 3
print(f"\n  TEST 1 VERDICT: {'MODEL SURVIVES' if t1_survives else 'MODEL KILLED'}")
if not t1_survives:
    print("  ** Random shuffles can reproduce the observed statistics. **")
    print("  ** The 'physics-like' properties may be artifacts of marginal distributions. **")
else:
    print("  Random shuffles cannot reproduce the observed statistics.")
    print("  The joint structure is real, not an artifact of marginals.")

# ============================================================
# TEST 2: AXIS SWAP
# ============================================================
print(f"\n{'='*70}")
print("TEST 2: AXIS SWAP (is thermal lag directional?)")
print("=" * 70)
print("\n  If we call LOW='drip' and HIGH='heat' (swap), the asymmetry and")
print("  transition following should REVERSE. If they don't, there's no")
print("  directional thermal lag -- the signal is symmetric.\n")

# Original: LOW=heat, HIGH=drip
# lo > ho + 1 means heat>>drip (heating up, drip lag) -> "below diagonal"
# Swapped: LOW=drip, HIGH=heat
# Now lo = drip, ho = heat
# "heat leads drip" in swapped frame: ho > lo + 1 (heat>>drip)

# With swap: asymmetry = (cases where ho > lo + 1) / (cases where lo > ho + 1)
swap_below = np.sum(all_ho > all_lo + 1)  # now "heat >> drip" in swapped frame
swap_above = np.sum(all_lo > all_ho + 1)  # now "drip >> heat" in swapped frame
swap_asymmetry = swap_below / swap_above if swap_above > 0 else float('inf')

# Transition following with swap: "heat" is now HIGH
# When HIGH increases, does LOW (drip) follow?
swap_heat_up_drip = []
for folio_keys in ordered_keys:
    for i in range(len(folio_keys) - 1):
        curr = line_coords[folio_keys[i]]
        nxt = line_coords[folio_keys[i + 1]]
        dh = nxt['ho'] - curr['ho']  # "heat" change in swapped frame
        dd = nxt['lo'] - curr['lo']  # "drip" change in swapped frame
        if dh > 0:
            swap_heat_up_drip.append(dd)

swap_heat_up_drip_mean = np.mean(swap_heat_up_drip) if swap_heat_up_drip else 0.0

print(f"  {'Metric':<30} {'Original':>12} {'Swapped':>12} {'Directional?':>14}")
print(f"  {'------------------------------'} {'------------':>12} {'------------':>12} {'--------------':>14}")

# Asymmetry: original has heat-leads > drip-leads
# If directional, swapped should have drip-leads > heat-leads (ratio < 1)
asym_directional = (obs_asymmetry > 1.0 and swap_asymmetry < 1.0) or \
                   (obs_asymmetry < 1.0 and swap_asymmetry > 1.0)
print(f"  {'Asymmetry ratio':<30} {obs_asymmetry:>12.2f} {swap_asymmetry:>12.2f} "
      f"{'YES' if asym_directional else 'NO':>14}")

# Transition: original has heat-up -> drip follows (positive)
# If directional, swapped should be different
trans_directional = abs(obs_heat_up_drip_mean - swap_heat_up_drip_mean) > 0.05
print(f"  {'Heat-up -> drip-follows':<30} {obs_heat_up_drip_mean:>+12.3f} {swap_heat_up_drip_mean:>+12.3f} "
      f"{'YES' if trans_directional else 'NO':>14}")

# Key check: is the asymmetry truly reversed?
# Original: heat leads (ratio > 1), Swapped: drip leads (ratio < 1) is the reciprocal
# By construction, swap_asymmetry = 1/obs_asymmetry (they're the exact same counts flipped)
# So the REAL test is: is the ratio significantly different from 1.0?
print(f"\n  NOTE: By construction, swap ratio = 1/original ratio.")
print(f"  The real question: is the asymmetry significantly different from 1.0?")
print(f"  Null p-value from Test 1: {p_asym:.4f}")

# More nuanced: test if LOW and HIGH have DIFFERENT relationship with transitions
# When LOW increases, what happens to HIGH? vs When HIGH increases, what happens to LOW?
lo_up_ho_change = []
ho_up_lo_change = []
for folio_keys in ordered_keys:
    for i in range(len(folio_keys) - 1):
        curr = line_coords[folio_keys[i]]
        nxt = line_coords[folio_keys[i + 1]]
        d_lo = nxt['lo'] - curr['lo']
        d_ho = nxt['ho'] - curr['ho']
        if d_lo > 0:
            lo_up_ho_change.append(d_ho)
        if d_ho > 0:
            ho_up_lo_change.append(d_lo)

mean_lo_up_ho = np.mean(lo_up_ho_change) if lo_up_ho_change else 0.0
mean_ho_up_lo = np.mean(ho_up_lo_change) if ho_up_lo_change else 0.0

print(f"\n  Cross-axis following (the key directional test):")
print(f"    When LOW increases  -> HIGH changes by: {mean_lo_up_ho:+.3f} (n={len(lo_up_ho_change)})")
print(f"    When HIGH increases -> LOW changes by:  {mean_ho_up_lo:+.3f} (n={len(ho_up_lo_change)})")

# Directional: one axis leads, the other follows. Symmetric: both respond the same.
asymmetry_diff = abs(mean_lo_up_ho - mean_ho_up_lo)
t2_directional = asymmetry_diff > 0.05
print(f"    Difference: {asymmetry_diff:.3f}")
print(f"    Directional threshold: > 0.05")

t2_survives = t2_directional
print(f"\n  TEST 2 VERDICT: {'MODEL SURVIVES' if t2_survives else 'MODEL KILLED'}")
if not t2_survives:
    print("  ** The axes are symmetric -- no directional thermal lag. **")
    print("  ** Either axis could be 'heat' or 'drip', which undermines physical identity. **")
else:
    leader = "LOW" if mean_lo_up_ho > mean_ho_up_lo else "HIGH"
    print(f"  {leader} leads the other axis (asymmetric cross-axis following).")
    print(f"  This is consistent with one axis being a 'cause' and the other a 'response'.")

# ============================================================
# TEST 3: SECTION OPERATING WINDOWS
# ============================================================
print(f"\n{'='*70}")
print("TEST 3: SECTION OPERATING WINDOWS")
print("=" * 70)
print("\n  If folios describe different plant materials, different sections should")
print("  have different operating windows (different centers of mass).\n")

section_los = defaultdict(list)
section_hos = defaultdict(list)

for line_key, coords in line_coords.items():
    sec = line_meta[line_key]['section']
    section_los[sec].append(coords['lo'])
    section_hos[sec].append(coords['ho'])

sections_with_data = sorted([s for s in section_los if len(section_los[s]) >= 10])
print(f"  Sections with 10+ lines: {sections_with_data}")

for sec in sections_with_data:
    lo_arr = np.array(section_los[sec])
    ho_arr = np.array(section_hos[sec])
    print(f"\n  Section {sec} (n={len(lo_arr)}):")
    print(f"    LOW center:  mean={np.mean(lo_arr):.2f}, median={np.median(lo_arr):.1f}")
    print(f"    HIGH center: mean={np.mean(ho_arr):.2f}, median={np.median(ho_arr):.1f}")

# Kruskal-Wallis test: are the distributions different across sections?
if len(sections_with_data) >= 2:
    lo_groups = [np.array(section_los[s]) for s in sections_with_data]
    ho_groups = [np.array(section_hos[s]) for s in sections_with_data]

    kw_lo_stat, kw_lo_p = kruskal(*lo_groups)
    kw_ho_stat, kw_ho_p = kruskal(*ho_groups)

    print(f"\n  Kruskal-Wallis (do sections differ in operating window?):")
    print(f"    LOW axis:  H={kw_lo_stat:.2f}, p={kw_lo_p:.6f}")
    print(f"    HIGH axis: H={kw_ho_stat:.2f}, p={kw_ho_p:.6f}")

    # Also test the center-of-mass (mean lo, mean ho) per folio by section
    folio_coms = defaultdict(lambda: {'lo': [], 'ho': [], 'section': None})
    for line_key, coords in line_coords.items():
        folio = line_meta[line_key]['folio']
        folio_coms[folio]['lo'].append(coords['lo'])
        folio_coms[folio]['ho'].append(coords['ho'])
        folio_coms[folio]['section'] = line_meta[line_key]['section']

    section_folio_coms = defaultdict(lambda: {'lo': [], 'ho': []})
    for folio, data in folio_coms.items():
        if len(data['lo']) < 5:
            continue
        sec = data['section']
        section_folio_coms[sec]['lo'].append(np.mean(data['lo']))
        section_folio_coms[sec]['ho'].append(np.mean(data['ho']))

    print(f"\n  Per-folio COM distributions by section:")
    for sec in sorted(section_folio_coms.keys()):
        lo_vals = section_folio_coms[sec]['lo']
        ho_vals = section_folio_coms[sec]['ho']
        print(f"    Section {sec}: {len(lo_vals)} folios, "
              f"LOW COM = {np.mean(lo_vals):.2f}+/-{np.std(lo_vals):.2f}, "
              f"HIGH COM = {np.mean(ho_vals):.2f}+/-{np.std(ho_vals):.2f}")

    # Folio-level Kruskal-Wallis
    folio_lo_groups = [np.array(section_folio_coms[s]['lo'])
                       for s in sorted(section_folio_coms.keys())
                       if len(section_folio_coms[s]['lo']) >= 3]
    folio_ho_groups = [np.array(section_folio_coms[s]['ho'])
                       for s in sorted(section_folio_coms.keys())
                       if len(section_folio_coms[s]['ho']) >= 3]

    if len(folio_lo_groups) >= 2:
        kw_flo_stat, kw_flo_p = kruskal(*folio_lo_groups)
        kw_fho_stat, kw_fho_p = kruskal(*folio_ho_groups)
        print(f"\n  Folio-level Kruskal-Wallis:")
        print(f"    LOW axis:  H={kw_flo_stat:.2f}, p={kw_flo_p:.6f}")
        print(f"    HIGH axis: H={kw_fho_stat:.2f}, p={kw_fho_p:.6f}")
    else:
        kw_flo_p = 1.0
        kw_fho_p = 1.0

    t3_survives = (kw_lo_p < 0.05 or kw_ho_p < 0.05)
else:
    t3_survives = False
    kw_lo_p = 1.0
    kw_ho_p = 1.0
    kw_flo_p = 1.0
    kw_fho_p = 1.0

print(f"\n  TEST 3 VERDICT: {'MODEL SURVIVES' if t3_survives else 'MODEL KILLED'}")
if t3_survives:
    print("  Sections have significantly different operating windows.")
    print("  This is consistent with different materials requiring different conditions.")
else:
    print("  ** Sections do NOT differ in operating window. **")
    print("  ** All sections use the same heat/drip range, which contradicts **")
    print("  ** the prediction that different materials need different conditions. **")

# ============================================================
# TEST 4: EXTREME STATE CONTENT
# ============================================================
print(f"\n{'='*70}")
print("TEST 4: EXTREME STATE CONTENT (dangerous states)")
print("=" * 70)
print("\n  Physically dangerous states:")
print("    DANGER: high heat + low drip  = dry still (fire hazard)")
print("    IMPOSSIBLE: low heat + high drip = drip without heat source")
print("  These extreme off-diagonal states should have different vocabulary.\n")

# Define regions
# Danger zone: lo >= 4 and ho <= 1 (high heat, low drip)
# Impossible zone: ho >= 4 and lo <= 1 (high drip, no heat)
# Normal zone: |lo - ho| <= 1 and 1 <= lo <= 4 (on diagonal, moderate)

danger_tokens = []
impossible_tokens = []
normal_tokens = []
danger_roles = Counter()
impossible_roles = Counter()
normal_roles = Counter()
danger_classes = Counter()
impossible_classes = Counter()
normal_classes = Counter()

for line_key, coords in line_coords.items():
    lo, ho = coords['lo'], coords['ho']
    center = line_center_tokens[line_key]

    if lo >= 4 and ho <= 1:
        zone = 'danger'
        danger_tokens.extend(center)
        for w in center:
            r = token_to_role.get(w)
            c = token_to_class.get(w)
            if r:
                danger_roles[r] += 1
            if c is not None:
                danger_classes[c] += 1
    elif ho >= 4 and lo <= 1:
        zone = 'impossible'
        impossible_tokens.extend(center)
        for w in center:
            r = token_to_role.get(w)
            c = token_to_class.get(w)
            if r:
                impossible_roles[r] += 1
            if c is not None:
                impossible_classes[c] += 1
    elif abs(lo - ho) <= 1 and 1 <= lo <= 4:
        zone = 'normal'
        normal_tokens.extend(center)
        for w in center:
            r = token_to_role.get(w)
            c = token_to_class.get(w)
            if r:
                normal_roles[r] += 1
            if c is not None:
                normal_classes[c] += 1

print(f"  Zone sizes:")
print(f"    DANGER (high heat, low drip):  {len(danger_tokens)} tokens")
print(f"    IMPOSSIBLE (low heat, high drip): {len(impossible_tokens)} tokens")
print(f"    NORMAL (on diagonal, moderate): {len(normal_tokens)} tokens")

# Compare role distributions
print(f"\n  Role distributions:")
print(f"  {'Role':<20} {'DANGER':>10} {'IMPOSSIBLE':>12} {'NORMAL':>10}")
all_roles = sorted(set(list(danger_roles.keys()) + list(impossible_roles.keys()) +
                       list(normal_roles.keys())))
d_total = sum(danger_roles.values()) or 1
i_total = sum(impossible_roles.values()) or 1
n_total = sum(normal_roles.values()) or 1
for role in all_roles:
    d_pct = danger_roles.get(role, 0) / d_total * 100
    i_pct = impossible_roles.get(role, 0) / i_total * 100
    n_pct = normal_roles.get(role, 0) / n_total * 100
    print(f"  {role:<20} {d_pct:>9.1f}% {i_pct:>11.1f}% {n_pct:>9.1f}%")

# Vocabulary uniqueness: how many word types are unique to each zone?
danger_types = set(danger_tokens)
impossible_types = set(impossible_tokens)
normal_types = set(normal_tokens)

danger_unique = danger_types - normal_types - impossible_types
impossible_unique = impossible_types - normal_types - danger_types
normal_unique = normal_types - danger_types - impossible_types

print(f"\n  Vocabulary overlap:")
print(f"    DANGER types:     {len(danger_types):>4} ({len(danger_unique)} unique to zone)")
print(f"    IMPOSSIBLE types: {len(impossible_types):>4} ({len(impossible_unique)} unique to zone)")
print(f"    NORMAL types:     {len(normal_types):>4} ({len(normal_unique)} unique to zone)")

# Jaccard similarity: danger vs normal, impossible vs normal
if danger_types and normal_types:
    j_danger_normal = len(danger_types & normal_types) / len(danger_types | normal_types)
else:
    j_danger_normal = 0.0
if impossible_types and normal_types:
    j_impossible_normal = len(impossible_types & normal_types) / len(impossible_types | normal_types)
else:
    j_impossible_normal = 0.0

print(f"\n  Jaccard similarity with NORMAL zone:")
print(f"    DANGER vs NORMAL:     {j_danger_normal:.3f}")
print(f"    IMPOSSIBLE vs NORMAL: {j_impossible_normal:.3f}")

# Test: extreme zones should have LOWER Jaccard (more distinct vocabulary)
# Compare with baseline: random split of normal tokens
if len(normal_tokens) >= 20:
    rng2 = np.random.RandomState(123)
    half = len(normal_tokens) // 2
    idx = rng2.permutation(len(normal_tokens))
    split_a = set(np.array(normal_tokens)[idx[:half]])
    split_b = set(np.array(normal_tokens)[idx[half:]])
    j_baseline = len(split_a & split_b) / len(split_a | split_b)
    print(f"    Random split of NORMAL: {j_baseline:.3f} (baseline)")
else:
    j_baseline = 1.0

# The extreme zones should be more distinct from normal than a random split of normal
t4_danger_distinct = j_danger_normal < j_baseline if danger_types else False
t4_impossible_distinct = j_impossible_normal < j_baseline if impossible_types else False

# Also check: do extreme states have enough data to test?
t4_has_data = len(danger_tokens) >= 20 or len(impossible_tokens) >= 20
t4_survives = t4_has_data and (t4_danger_distinct or t4_impossible_distinct)

print(f"\n  TEST 4 VERDICT: {'MODEL SURVIVES' if t4_survives else 'MODEL KILLED' if t4_has_data else 'INCONCLUSIVE (insufficient data)'}")
if t4_survives:
    print("  Extreme off-diagonal states have distinct vocabulary from normal states.")
    print("  Consistent with different operational regimes at dangerous conditions.")
elif not t4_has_data:
    print("  ** Too few tokens at extreme states to test vocabulary divergence. **")
    print("  ** This is actually CONSISTENT with physics (extreme states are rare). **")
else:
    print("  ** Extreme states have the SAME vocabulary as normal states. **")
    print("  ** No evidence for content-aware state indexing. **")

# ============================================================
# TEST 5: FOLIO OPERATING RANGE CORRELATION
# ============================================================
print(f"\n{'='*70}")
print("TEST 5: FOLIO OPERATING RANGE (heat-center vs drip-center)")
print("=" * 70)
print("\n  If each folio is a procedure for a specific material, the folio's")
print("  heat range and drip range should correlate: materials needing")
print("  more heat also produce more drip.\n")

folio_lo_centers = []
folio_ho_centers = []
folio_lo_ranges = []
folio_ho_ranges = []
folio_labels = []

for folio, keys in folio_lines_ordered.items():
    coords = [(line_coords[k]['lo'], line_coords[k]['ho']) for k in keys if k in line_coords]
    if len(coords) < 5:
        continue
    los = [c[0] for c in coords]
    hos = [c[1] for c in coords]
    folio_lo_centers.append(np.mean(los))
    folio_ho_centers.append(np.mean(hos))
    folio_lo_ranges.append(np.max(los) - np.min(los))
    folio_ho_ranges.append(np.max(hos) - np.min(hos))
    folio_labels.append(folio)

folio_lo_centers = np.array(folio_lo_centers)
folio_ho_centers = np.array(folio_ho_centers)
folio_lo_ranges = np.array(folio_lo_ranges)
folio_ho_ranges = np.array(folio_ho_ranges)

# Center correlation
if len(folio_lo_centers) > 5:
    r_center, p_center = spearmanr(folio_lo_centers, folio_ho_centers)
    print(f"  Folio center-of-mass correlation:")
    print(f"    N folios: {len(folio_lo_centers)}")
    print(f"    Spearman rho (LOW center vs HIGH center): {r_center:+.3f}")
    print(f"    p-value: {p_center:.6f}")

    # Range correlation: do folios that span more heat also span more drip?
    r_range, p_range = spearmanr(folio_lo_ranges, folio_ho_ranges)
    print(f"\n  Folio operating RANGE correlation:")
    print(f"    Spearman rho (LOW range vs HIGH range): {r_range:+.3f}")
    print(f"    p-value: {p_range:.6f}")

    # Null distribution for center correlation
    null_center_rhos = []
    for _ in range(1000):
        shuf_ho = rng.permutation(folio_ho_centers)
        r, _ = spearmanr(folio_lo_centers, shuf_ho)
        null_center_rhos.append(r)
    null_center_rhos = np.array(null_center_rhos)
    p_center_perm = np.mean(null_center_rhos >= r_center)

    print(f"\n  Permutation test for center correlation:")
    print(f"    Observed rho: {r_center:+.3f}")
    print(f"    Null mean: {np.mean(null_center_rhos):+.4f}")
    print(f"    Null 95th percentile: {np.percentile(null_center_rhos, 95):+.4f}")
    print(f"    Permutation p-value: {p_center_perm:.4f}")

    t5_survives = r_center > 0 and p_center < 0.05
else:
    r_center = 0.0
    p_center = 1.0
    r_range = 0.0
    p_range = 1.0
    p_center_perm = 1.0
    t5_survives = False

print(f"\n  TEST 5 VERDICT: {'MODEL SURVIVES' if t5_survives else 'MODEL KILLED'}")
if t5_survives:
    print("  Folio heat-centers and drip-centers are positively correlated.")
    print("  Materials that need more heat also produce more drip.")
else:
    if r_center <= 0:
        print("  ** Folio heat-centers and drip-centers are NOT positively correlated. **")
        print("  ** Materials' heat needs don't predict their drip output. **")
    else:
        print("  ** Correlation is not statistically significant. **")
        print("  ** Insufficient evidence for material-specific operating windows. **")

# ============================================================
# OVERALL VERDICT
# ============================================================
print(f"\n{'='*70}")
print("OVERALL FALSIFICATION VERDICT")
print("=" * 70)

tests = {
    'T1_null_distribution': bool(t1_survives),
    'T2_axis_swap': bool(t2_survives),
    'T3_section_windows': bool(t3_survives),
    'T4_extreme_content': bool(t4_survives) if t4_has_data else None,  # None = inconclusive
    'T5_folio_range': bool(t5_survives),
}

n_survived = sum(1 for v in tests.values() if v is True)
n_killed = sum(1 for v in tests.values() if v is False)
n_inconclusive = sum(1 for v in tests.values() if v is None)
n_total = len(tests) - n_inconclusive

print(f"\n  Test results:")
for name, result in tests.items():
    if result is None:
        status = "INCONCLUSIVE"
    elif result:
        status = "MODEL SURVIVES"
    else:
        status = "MODEL KILLED"
    print(f"    {name:<25} {status}")

print(f"\n  Survived: {n_survived}/{n_total} (excl. {n_inconclusive} inconclusive)")

if n_killed == 0 and n_inconclusive == 0:
    verdict = "SURVIVES_ALL"
    expl = ("Heat/drip model passes all 5 falsification tests. "
            "The physics-consistent properties are NOT artifacts of marginal "
            "distributions, the axes are directional, sections differ, and "
            "folio operating ranges correlate.")
elif n_killed == 0:
    verdict = "SURVIVES_TESTABLE"
    expl = (f"Heat/drip model survives all testable falsification attempts "
            f"({n_inconclusive} tests inconclusive due to data limitations).")
elif n_survived >= n_killed:
    verdict = "PARTIALLY_SURVIVES"
    killed = [k for k, v in tests.items() if v is False]
    expl = (f"Heat/drip model survives {n_survived}/{n_total} tests but fails: "
            f"{', '.join(killed)}. Model needs refinement.")
else:
    verdict = "KILLED"
    killed = [k for k, v in tests.items() if v is False]
    expl = (f"Heat/drip model FAILS {n_killed}/{n_total} tests: "
            f"{', '.join(killed)}. The model is not supported by rigorous testing.")

print(f"\n  VERDICT: {verdict}")
print(f"  {expl}")

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
    'n_lines': len(line_coords),
    'test_1_null_distribution': {
        'n_shuffles': N_SHUFFLES,
        'observed': {
            'rho': round(float(obs_rho), 3),
            'diagonal_fraction': round(float(obs_diag_frac), 3),
            'asymmetry_ratio': round(float(obs_asymmetry), 2),
            'heat_up_drip_mean': round(float(obs_heat_up_drip_mean), 3),
        },
        'null_95th': {
            'rho': round(float(np.percentile(null_rhos, 95)), 4),
            'diagonal_fraction': round(float(np.percentile(null_diag_fracs, 95)), 4),
            'asymmetry_ratio': round(float(np.percentile(null_asymmetries, 95)), 4),
            'heat_up_drip_mean': round(float(np.percentile(null_heat_up_drip, 95)), 4),
        },
        'p_values': {
            'rho': round(float(p_rho), 4),
            'diagonal_fraction': round(float(p_diag), 4),
            'asymmetry_ratio': round(float(p_asym), 4),
            'heat_up_drip_mean': round(float(p_trans), 4),
        },
        'sub_tests_passed': t1_n_pass,
        'survives': t1_survives,
    },
    'test_2_axis_swap': {
        'original_asymmetry': round(float(obs_asymmetry), 2),
        'swapped_asymmetry': round(float(swap_asymmetry), 2),
        'lo_up_ho_change': round(float(mean_lo_up_ho), 3),
        'ho_up_lo_change': round(float(mean_ho_up_lo), 3),
        'asymmetry_diff': round(float(asymmetry_diff), 3),
        'directional': t2_directional,
        'survives': t2_survives,
    },
    'test_3_section_windows': {
        'kw_lo_p': round(float(kw_lo_p), 6),
        'kw_ho_p': round(float(kw_ho_p), 6),
        'sections': {sec: {
            'n_lines': len(section_los[sec]),
            'lo_mean': round(float(np.mean(section_los[sec])), 2),
            'ho_mean': round(float(np.mean(section_hos[sec])), 2),
        } for sec in sections_with_data},
        'survives': t3_survives,
    },
    'test_4_extreme_content': {
        'danger_tokens': len(danger_tokens),
        'impossible_tokens': len(impossible_tokens),
        'normal_tokens': len(normal_tokens),
        'jaccard_danger_normal': round(float(j_danger_normal), 3),
        'jaccard_impossible_normal': round(float(j_impossible_normal), 3),
        'jaccard_baseline': round(float(j_baseline), 3),
        'has_sufficient_data': t4_has_data,
        'survives': t4_survives if t4_has_data else None,
    },
    'test_5_folio_range': {
        'n_folios': len(folio_lo_centers),
        'center_rho': round(float(r_center), 3),
        'center_p': round(float(p_center), 6),
        'range_rho': round(float(r_range), 3),
        'range_p': round(float(p_range), 6),
        'permutation_p': round(float(p_center_perm), 4),
        'survives': t5_survives,
    },
    'overall': {
        'survived': n_survived,
        'killed': n_killed,
        'inconclusive': n_inconclusive,
        'total_testable': n_total,
        'verdict': verdict,
        'explanation': expl,
    },
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '45_heat_drip_falsification.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
