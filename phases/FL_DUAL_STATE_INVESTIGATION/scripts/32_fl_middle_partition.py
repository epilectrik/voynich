"""
32_fl_middle_partition.py

How do specific FL MIDDLEs partition across the (ACTION, OVERSIGHT) grid?

Questions:
  1. Which MIDDLEs serve as LOW bookend vs HIGH bookend vs both?
  2. For each MIDDLE, what region of the grid does it occupy?
  3. Do specific LOW-HIGH MIDDLE pairs co-occur (e.g., does 'r' LOW always
     pair with 'y' HIGH)?
  4. Does MIDDLE character composition predict axis role?
  5. Are some MIDDLEs "anchors" (tight grid position) vs "floaters" (spread)?
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

# Build line tokens
line_tokens = defaultdict(list)
line_meta = {}
for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {'section': t.section}

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
        gmm_models[mid] = {'model': gmm, 'swap': True,
                           'low_mean': float(gmm.means_[1][0]),
                           'high_mean': float(gmm.means_[0][0])}
    else:
        gmm_models[mid] = {'model': gmm, 'swap': False,
                           'low_mean': float(gmm.means_[0][0]),
                           'high_mean': float(gmm.means_[1][0])}

# ============================================================
# Classify each FL token as LOW or HIGH, record co-occurrences
# ============================================================
# Per-MIDDLE: how often LOW vs HIGH
middle_mode_counts = defaultdict(Counter)  # mid -> {'LOW': n, 'HIGH': n}

# Per-line: (low_middle, high_middle) co-occurrence pairs
line_middle_pairs = []  # list of (low_mid, high_mid, low_stage, high_stage, section)

# Per-MIDDLE: what partner stages it pairs with
middle_as_low_partner_stages = defaultdict(Counter)   # mid -> Counter of HIGH stages
middle_as_high_partner_stages = defaultdict(Counter)  # mid -> Counter of LOW stages

# Per-MIDDLE: what sections it appears in by mode
middle_low_sections = defaultdict(Counter)
middle_high_sections = defaultdict(Counter)

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
            fl_info.append({'mid': mid, 'mode': mode, 'stage': stage, 'idx': idx})
            middle_mode_counts[mid][mode] += 1

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    section = line_meta[line_key]['section']

    # Record all LOW-HIGH MIDDLE pairs in this line
    low_mids = set(f['mid'] for f in low_fls)
    high_mids = set(f['mid'] for f in high_fls)

    for lm in low_mids:
        for hm in high_mids:
            line_middle_pairs.append((lm, hm, low_stage, high_stage, section))

    for f in low_fls:
        middle_as_low_partner_stages[f['mid']][high_stage] += 1
        middle_low_sections[f['mid']][section] += 1
    for f in high_fls:
        middle_as_high_partner_stages[f['mid']][low_stage] += 1
        middle_high_sections[f['mid']][section] += 1

# ============================================================
# 1. MODE SPECIALIZATION: LOW vs HIGH preference per MIDDLE
# ============================================================
print("=" * 70)
print("1. FL MIDDLE MODE SPECIALIZATION")
print("=" * 70)

all_middles = sorted(FL_STAGE_MAP.keys(),
                     key=lambda m: FL_STAGE_MAP[m][1])

print(f"\n  {'MIDDLE':<6} {'Stage':<10} {'GlobPos':>7} "
      f"{'Total':>6} {'LOW':>5} {'HIGH':>5} {'LOW%':>6} "
      f"{'Bias':>8} {'LowMu':>6} {'HiMu':>6}")
print(f"  {'-'*78}")

middle_profiles = {}
for mid in all_middles:
    stage, gpos = FL_STAGE_MAP[mid]
    total_occ = sum(middle_mode_counts[mid].values())
    n_low = middle_mode_counts[mid].get('LOW', 0)
    n_high = middle_mode_counts[mid].get('HIGH', 0)
    low_pct = n_low / total_occ * 100 if total_occ > 0 else 0

    if low_pct > 65:
        bias = "LOW-dom"
    elif low_pct < 35:
        bias = "HIGH-dom"
    else:
        bias = "DUAL"

    low_mu = gmm_models[mid]['low_mean'] if mid in gmm_models else float('nan')
    high_mu = gmm_models[mid]['high_mean'] if mid in gmm_models else float('nan')

    middle_profiles[mid] = {
        'stage': stage, 'gpos': gpos, 'total': total_occ,
        'n_low': n_low, 'n_high': n_high, 'low_pct': low_pct,
        'bias': bias, 'low_mu': low_mu, 'high_mu': high_mu,
    }

    if total_occ >= 10:
        print(f"  {mid:<6} {stage:<10} {gpos:>7.3f} "
              f"{total_occ:>6} {n_low:>5} {n_high:>5} {low_pct:>5.1f}% "
              f"{bias:>8} {low_mu:>6.3f} {high_mu:>6.3f}")

# Classify
low_dominant = [m for m, p in middle_profiles.items() if p['bias'] == 'LOW-dom' and p['total'] >= 10]
high_dominant = [m for m, p in middle_profiles.items() if p['bias'] == 'HIGH-dom' and p['total'] >= 10]
dual_role = [m for m, p in middle_profiles.items() if p['bias'] == 'DUAL' and p['total'] >= 10]

print(f"\n  LOW-dominant MIDDLEs:  {', '.join(low_dominant)}")
print(f"  HIGH-dominant MIDDLEs: {', '.join(high_dominant)}")
print(f"  DUAL-role MIDDLEs:    {', '.join(dual_role)}")

# ============================================================
# 2. PARTNER STAGE PROFILES: Who pairs with whom?
# ============================================================
print(f"\n{'='*70}")
print("2. PARTNER STAGE PROFILES")
print(f"{'='*70}")

print(f"\n  When serving as LOW bookend, what HIGH stages appear?")
print(f"  {'MIDDLE':<6} {'n':>5}  ", end='')
for s in STAGES:
    print(f" {s[:4]:>5}", end='')
print(f"  {'Dominant':>10} {'Spread':>7}")
print(f"  {'-'*72}")

for mid in all_middles:
    counts = middle_as_low_partner_stages[mid]
    total = sum(counts.values())
    if total < 10:
        continue
    print(f"  {mid:<6} {total:>5}  ", end='')
    pcts = []
    for s in STAGES:
        pct = counts.get(s, 0) / total * 100
        pcts.append(pct)
        print(f" {pct:>4.0f}%", end='')
    dominant = STAGES[np.argmax(pcts)]
    spread = sum(1 for p in pcts if p > 10)
    print(f"  {dominant[:6]:>10} {spread:>7}")

print(f"\n  When serving as HIGH bookend, what LOW stages appear?")
print(f"  {'MIDDLE':<6} {'n':>5}  ", end='')
for s in STAGES:
    print(f" {s[:4]:>5}", end='')
print(f"  {'Dominant':>10} {'Spread':>7}")
print(f"  {'-'*72}")

for mid in all_middles:
    counts = middle_as_high_partner_stages[mid]
    total = sum(counts.values())
    if total < 10:
        continue
    print(f"  {mid:<6} {total:>5}  ", end='')
    pcts = []
    for s in STAGES:
        pct = counts.get(s, 0) / total * 100
        pcts.append(pct)
        print(f" {pct:>4.0f}%", end='')
    dominant = STAGES[np.argmax(pcts)]
    spread = sum(1 for p in pcts if p > 10)
    print(f"  {dominant[:6]:>10} {spread:>7}")

# ============================================================
# 3. CO-OCCURRENCE: Specific LOW-HIGH MIDDLE pairs
# ============================================================
print(f"\n{'='*70}")
print("3. LOW-HIGH MIDDLE CO-OCCURRENCE PAIRS")
print(f"{'='*70}")

pair_counter = Counter((lm, hm) for lm, hm, ls, hs, sec in line_middle_pairs)
total_pairs = sum(pair_counter.values())

# Show top 25 co-occurring pairs
print(f"\n  Top 25 FL MIDDLE co-occurrences (LOW x HIGH):")
print(f"  {'LOW':<6} {'HIGH':<6} {'Count':>6} {'%':>6} {'Expected%':>9} {'Lift':>6}")
print(f"  {'-'*45}")

# Marginals for expected frequency
low_marginal = Counter()
high_marginal = Counter()
for (lm, hm), c in pair_counter.items():
    low_marginal[lm] += c
    high_marginal[hm] += c

for (lm, hm), count in pair_counter.most_common(25):
    pct = count / total_pairs * 100
    expected = (low_marginal[lm] / total_pairs) * (high_marginal[hm] / total_pairs) * 100
    lift = pct / expected if expected > 0 else 0
    print(f"  {lm:<6} {hm:<6} {count:>6} {pct:>5.1f}% {expected:>8.2f}% {lift:>5.1f}x")

# ============================================================
# 4. SECTION SPECIALIZATION PER MIDDLE+MODE
# ============================================================
print(f"\n{'='*70}")
print("4. SECTION SPECIALIZATION BY MIDDLE + MODE")
print(f"{'='*70}")

all_sections = ['B', 'C', 'H', 'S', 'T']

print(f"\n  As LOW bookend:")
print(f"  {'MIDDLE':<6} {'n':>5}", end='')
for s in all_sections:
    print(f"  {s:>4}", end='')
print()
print(f"  {'-'*35}")

for mid in all_middles:
    counts = middle_low_sections[mid]
    total = sum(counts.values())
    if total < 10:
        continue
    print(f"  {mid:<6} {total:>5}", end='')
    for s in all_sections:
        pct = counts.get(s, 0) / total * 100
        print(f" {pct:>4.0f}%", end='')
    print()

print(f"\n  As HIGH bookend:")
print(f"  {'MIDDLE':<6} {'n':>5}", end='')
for s in all_sections:
    print(f"  {s:>4}", end='')
print()
print(f"  {'-'*35}")

for mid in all_middles:
    counts = middle_high_sections[mid]
    total = sum(counts.values())
    if total < 10:
        continue
    print(f"  {mid:<6} {total:>5}", end='')
    for s in all_sections:
        pct = counts.get(s, 0) / total * 100
        print(f" {pct:>4.0f}%", end='')
    print()

# ============================================================
# 5. CHARACTER COMPOSITION vs AXIS ROLE
# ============================================================
print(f"\n{'='*70}")
print("5. CHARACTER COMPOSITION vs AXIS ROLE")
print(f"{'='*70}")

# Do character features predict LOW vs HIGH preference?
print(f"\n  Character features of mode-specialized MIDDLEs:")
print(f"  {'MIDDLE':<6} {'Bias':<10} {'Len':>4} {'HasVowel':>9} {'EndsY':>6} {'HasR':>5} {'HasL':>5} {'HasN':>5}")
print(f"  {'-'*55}")

vowels = set('aeiou')
for mid in all_middles:
    if middle_profiles[mid]['total'] < 10:
        continue
    bias = middle_profiles[mid]['bias']
    length = len(mid)
    has_vowel = any(c in vowels for c in mid)
    ends_y = mid.endswith('y')
    has_r = 'r' in mid
    has_l = 'l' in mid
    has_n = 'n' in mid
    print(f"  {mid:<6} {bias:<10} {length:>4} "
          f"{'Y' if has_vowel else 'N':>9} "
          f"{'Y' if ends_y else 'N':>6} "
          f"{'Y' if has_r else 'N':>5} "
          f"{'Y' if has_l else 'N':>5} "
          f"{'Y' if has_n else 'N':>5}")

# Test: does ending in 'y' predict HIGH-dominant?
ends_y_bias = []
not_ends_y_bias = []
for mid in all_middles:
    if middle_profiles[mid]['total'] < 10:
        continue
    low_pct = middle_profiles[mid]['low_pct']
    if mid.endswith('y'):
        ends_y_bias.append(low_pct)
    else:
        not_ends_y_bias.append(low_pct)

if ends_y_bias and not_ends_y_bias:
    print(f"\n  Ends-in-y MIDDLEs: mean LOW% = {np.mean(ends_y_bias):.1f}% (n={len(ends_y_bias)})")
    print(f"  No-y MIDDLEs:      mean LOW% = {np.mean(not_ends_y_bias):.1f}% (n={len(not_ends_y_bias)})")

# Test: does containing 'l' predict LOW-dominant?
has_l_bias = []
no_l_bias = []
for mid in all_middles:
    if middle_profiles[mid]['total'] < 10:
        continue
    low_pct = middle_profiles[mid]['low_pct']
    if 'l' in mid:
        has_l_bias.append(low_pct)
    else:
        no_l_bias.append(low_pct)

if has_l_bias and no_l_bias:
    print(f"\n  Contains-l MIDDLEs: mean LOW% = {np.mean(has_l_bias):.1f}% (n={len(has_l_bias)})")
    print(f"  No-l MIDDLEs:       mean LOW% = {np.mean(no_l_bias):.1f}% (n={len(no_l_bias)})")

# Global position vs LOW preference
gpos_list = []
low_pct_list = []
for mid in all_middles:
    if middle_profiles[mid]['total'] < 20:
        continue
    gpos_list.append(middle_profiles[mid]['gpos'])
    low_pct_list.append(middle_profiles[mid]['low_pct'])

if len(gpos_list) >= 5:
    rho, p = spearmanr(gpos_list, low_pct_list)
    print(f"\n  Global position vs LOW%: rho={rho:+.3f} (p={p:.4f})")
    print(f"  {'-> Higher-position MIDDLEs prefer LOW role' if rho > 0 else '-> Lower-position MIDDLEs prefer LOW role'}")

# ============================================================
# 6. ANCHOR vs FLOATER classification
# ============================================================
print(f"\n{'='*70}")
print("6. GRID POSITION: ANCHOR vs FLOATER")
print(f"{'='*70}")

# For each MIDDLE, compute its grid "footprint":
# how many distinct (low_stage, high_stage) pairs does it appear in?
middle_grid_footprint = defaultdict(set)
for lm, hm, ls, hs, sec in line_middle_pairs:
    middle_grid_footprint[lm].add((ls, hs))
    middle_grid_footprint[hm].add((ls, hs))

# Also compute spread of partner stages
print(f"\n  {'MIDDLE':<6} {'Bias':<10} {'GridCells':>9} {'LowPartners':>12} {'HighPartners':>13} {'Type':>8}")
print(f"  {'-'*65}")

middle_types = {}
for mid in all_middles:
    if middle_profiles[mid]['total'] < 20:
        continue

    n_cells = len(middle_grid_footprint.get(mid, set()))
    n_low_partners = len([s for s, c in middle_as_low_partner_stages[mid].items() if c >= 3])
    n_high_partners = len([s for s, c in middle_as_high_partner_stages[mid].items() if c >= 3])

    bias = middle_profiles[mid]['bias']

    # Classify
    if n_cells <= 5:
        mtype = "ANCHOR"
    elif n_cells <= 10:
        mtype = "MODERATE"
    else:
        mtype = "FLOATER"

    middle_types[mid] = mtype

    print(f"  {mid:<6} {bias:<10} {n_cells:>9} {n_low_partners:>12} {n_high_partners:>13} {mtype:>8}")

anchors = [m for m, t in middle_types.items() if t == 'ANCHOR']
floaters = [m for m, t in middle_types.items() if t == 'FLOATER']
moderates = [m for m, t in middle_types.items() if t == 'MODERATE']

print(f"\n  ANCHORS ({len(anchors)}):   {', '.join(anchors)}")
print(f"  MODERATE ({len(moderates)}): {', '.join(moderates)}")
print(f"  FLOATERS ({len(floaters)}):  {', '.join(floaters)}")

# ============================================================
# 7. SUMMARY: MIDDLE ROLE MAP
# ============================================================
print(f"\n{'='*70}")
print("7. FL MIDDLE ROLE MAP")
print(f"{'='*70}")

print(f"\n  Mapping each FL MIDDLE to its function in the coordinate system:\n")
print(f"  {'MIDDLE':<6} {'Stage':<10} {'AxisRole':<10} {'GridType':<10} {'Interpretation'}")
print(f"  {'-'*75}")

for mid in all_middles:
    if middle_profiles[mid]['total'] < 10:
        continue
    stage = middle_profiles[mid]['stage']
    bias = middle_profiles[mid]['bias']
    gtype = middle_types.get(mid, '?')

    # Build interpretation
    interp_parts = []
    if bias == 'LOW-dom':
        interp_parts.append(f"marks ACTION level={stage}")
    elif bias == 'HIGH-dom':
        interp_parts.append(f"marks OVERSIGHT level={stage}")
    else:
        interp_parts.append(f"dual: ACTION or OVERSIGHT at {stage}")

    if gtype == 'ANCHOR':
        interp_parts.append("tight grid position")
    elif gtype == 'FLOATER':
        interp_parts.append("broad grid coverage")

    print(f"  {mid:<6} {stage:<10} {bias:<10} {gtype:<10} {'; '.join(interp_parts)}")

# ============================================================
# SAVE
# ============================================================
result = {
    'n_fl_middles_analyzed': sum(1 for m in all_middles if middle_profiles[m]['total'] >= 10),
    'mode_specialization': {
        'low_dominant': low_dominant,
        'high_dominant': high_dominant,
        'dual_role': dual_role,
    },
    'grid_types': {
        'anchors': anchors,
        'moderates': moderates,
        'floaters': floaters,
    },
    'middle_profiles': {
        mid: {
            'stage': p['stage'],
            'global_position': p['gpos'],
            'total_occurrences': p['total'],
            'low_count': p['n_low'],
            'high_count': p['n_high'],
            'low_pct': round(p['low_pct'], 1),
            'bias': p['bias'],
            'grid_type': middle_types.get(mid, 'unknown'),
            'low_gmm_mean': round(p['low_mu'], 3) if not np.isnan(p['low_mu']) else None,
            'high_gmm_mean': round(p['high_mu'], 3) if not np.isnan(p['high_mu']) else None,
        }
        for mid, p in middle_profiles.items()
        if p['total'] >= 10
    },
    'top_co_occurrences': [
        {'low_mid': lm, 'high_mid': hm, 'count': c,
         'pct': round(c / total_pairs * 100, 2),
         'lift': round((c / total_pairs) / ((low_marginal[lm] / total_pairs) *
                 (high_marginal[hm] / total_pairs)), 2)
                 if (low_marginal[lm] > 0 and high_marginal[hm] > 0) else 0}
        for (lm, hm), c in pair_counter.most_common(20)
    ],
    'global_position_vs_low_pct': {
        'rho': round(float(rho), 3) if len(gpos_list) >= 5 else None,
        'p': round(float(p), 4) if len(gpos_list) >= 5 else None,
    },
}

out_path = Path(__file__).resolve().parent.parent / "results" / "32_fl_middle_partition.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
