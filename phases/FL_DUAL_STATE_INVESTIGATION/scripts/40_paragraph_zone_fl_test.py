"""
40_paragraph_zone_fl_test.py

Is the FL coordinate system specific to paragraph body lines?

Hypothesis: Paragraph structure = HEADER (setup) + BODY (state-indexed) + TAIL (collect)
- HEADER lines: specification, NOT state-indexed
- BODY lines: state-indexed via FL coordinates, executed in state-dictated order
- TAIL lines: collection/termination, NOT state-indexed

Tests:
  1. FL token rate by paragraph zone (HEADER / BODY / TAIL)
  2. FL coordinate coverage by zone (do body lines use more of the grid?)
  3. FL predictive power by zone (do FL coordinates predict center content better in body?)
  4. FL MIDDLE diversity by zone
  5. Within-zone vs between-zone state coherence
  6. Specific FL stage preferences by zone (do headers cluster at specific stages?)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, kruskal, mannwhitneyu

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
# Build line data with paragraph zones
# ============================================================
line_tokens = defaultdict(list)
line_meta = {}
folio_lines_ordered = defaultdict(list)

for t in tx.currier_b():
    key = (t.folio, t.line)
    line_tokens[key].append(t)
    if key not in line_meta:
        line_meta[key] = {
            'section': t.section, 'folio': t.folio,
            'par_initial': False, 'par_final': False,
        }
        folio_lines_ordered[t.folio].append(key)
    if t.par_initial:
        line_meta[key]['par_initial'] = True
    if t.par_final:
        line_meta[key]['par_final'] = True

# Deduplicate
for f in folio_lines_ordered:
    seen = set()
    deduped = []
    for k in folio_lines_ordered[f]:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    folio_lines_ordered[f] = deduped

# Build paragraphs
folio_paragraphs = defaultdict(list)
for folio, keys in folio_lines_ordered.items():
    current_para = []
    for key in keys:
        meta = line_meta[key]
        if meta['par_initial'] and current_para:
            folio_paragraphs[folio].append(current_para)
            current_para = []
        current_para.append(key)
        if meta['par_final']:
            folio_paragraphs[folio].append(current_para)
            current_para = []
    if current_para:
        folio_paragraphs[folio].append(current_para)

# Assign paragraph zones to each line
line_zone = {}  # key -> 'HEADER' | 'BODY' | 'TAIL' | 'SOLO'
for folio, paras in folio_paragraphs.items():
    for para in paras:
        if len(para) == 1:
            line_zone[para[0]] = 'SOLO'
        elif len(para) == 2:
            line_zone[para[0]] = 'HEADER'
            line_zone[para[1]] = 'TAIL'
        else:
            line_zone[para[0]] = 'HEADER'
            line_zone[para[-1]] = 'TAIL'
            for key in para[1:-1]:
                line_zone[key] = 'BODY'

print(f"Zone distribution:")
zone_counts = Counter(line_zone.values())
for z in ['HEADER', 'BODY', 'TAIL', 'SOLO']:
    print(f"  {z}: {zone_counts.get(z, 0)}")

# ============================================================
# Fit GMMs and assign FL coordinates
# ============================================================
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

# Per-line: count FL tokens, assign coordinates, extract FL details
line_fl_data = {}
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 3:
        continue

    fl_tokens = []
    fl_middles = []
    non_fl_tokens = []

    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        if is_fl:
            fl_tokens.append({'pos': pos, 'middle': mid, 'word': t.word})
            fl_middles.append(mid)
            if mid in gmm_models:
                info = gmm_models[mid]
                pred = info['model'].predict(np.array([[pos]]))[0]
                if info['swap']:
                    pred = 1 - pred
                fl_tokens[-1]['mode'] = 'LOW' if pred == 0 else 'HIGH'
                fl_tokens[-1]['stage'] = FL_STAGE_MAP[mid][0]
        else:
            non_fl_tokens.append({'pos': pos, 'middle': mid, 'word': t.word})

    # Compute coordinates
    low_fls = [f for f in fl_tokens if f.get('mode') == 'LOW']
    high_fls = [f for f in fl_tokens if f.get('mode') == 'HIGH']

    has_coord = bool(low_fls and high_fls)
    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0] if low_fls else None
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0] if high_fls else None

    line_fl_data[line_key] = {
        'n_tokens': n,
        'n_fl': len(fl_tokens),
        'fl_rate': len(fl_tokens) / n,
        'fl_middles': fl_middles,
        'n_unique_fl_middles': len(set(fl_middles)),
        'has_coord': has_coord,
        'low_stage': low_stage,
        'high_stage': high_stage,
        'lo': STAGE_ORDER[low_stage] if low_stage else None,
        'ho': STAGE_ORDER[high_stage] if high_stage else None,
        'n_low': len(low_fls),
        'n_high': len(high_fls),
        'center_middles': [t['middle'] for t in non_fl_tokens if t['middle']],
    }

# ============================================================
# 1. FL TOKEN RATE BY ZONE
# ============================================================
print(f"\n{'='*70}")
print("1. FL TOKEN RATE BY PARAGRAPH ZONE")
print("=" * 70)

zone_fl_rates = defaultdict(list)
zone_fl_counts = defaultdict(lambda: [0, 0])  # [fl_count, total_count]

for key, data in line_fl_data.items():
    zone = line_zone.get(key)
    if zone and zone != 'SOLO':
        zone_fl_rates[zone].append(data['fl_rate'])
        zone_fl_counts[zone][0] += data['n_fl']
        zone_fl_counts[zone][1] += data['n_tokens']

print(f"\n  {'Zone':<10} {'Mean FL%':>10} {'Median':>10} {'FL/total':>15} {'N lines':>10}")
for z in ['HEADER', 'BODY', 'TAIL']:
    rates = zone_fl_rates.get(z, [])
    if rates:
        fc, tc = zone_fl_counts[z]
        print(f"  {z:<10} {np.mean(rates)*100:>9.1f}% {np.median(rates)*100:>9.1f}% "
              f"{fc:>6}/{tc:<6}  {len(rates):>10}")

# Kruskal-Wallis: FL rate ~ zone
h_rates = zone_fl_rates.get('HEADER', [])
b_rates = zone_fl_rates.get('BODY', [])
t_rates = zone_fl_rates.get('TAIL', [])
if h_rates and b_rates and t_rates:
    h_stat, p_kw = kruskal(h_rates, b_rates, t_rates)
    print(f"\n  Kruskal-Wallis (FL rate ~ zone): H={h_stat:.2f}, p={p_kw:.6f}")
else:
    p_kw = 1.0

# ============================================================
# 2. COORDINATE COVERAGE BY ZONE
# ============================================================
print(f"\n{'='*70}")
print("2. FL COORDINATE COVERAGE BY ZONE")
print("=" * 70)

zone_coord_rate = {}
zone_states = defaultdict(list)

for key, data in line_fl_data.items():
    zone = line_zone.get(key)
    if zone and zone != 'SOLO':
        if zone not in zone_coord_rate:
            zone_coord_rate[zone] = [0, 0]
        zone_coord_rate[zone][1] += 1
        if data['has_coord']:
            zone_coord_rate[zone][0] += 1
            zone_states[zone].append((data['lo'], data['ho']))

print(f"\n  {'Zone':<10} {'Coord rate':>12} {'Unique states':>15} {'Grid coverage':>15}")
for z in ['HEADER', 'BODY', 'TAIL']:
    if z in zone_coord_rate:
        has, total = zone_coord_rate[z]
        rate = has / total if total > 0 else 0
        states = zone_states.get(z, [])
        unique = len(set(states))
        coverage = unique / 36 * 100  # 6x6 grid
        print(f"  {z:<10} {has:>4}/{total:<4} ({rate*100:.1f}%) {unique:>15} {coverage:>13.1f}%")

# Stage distribution by zone
print(f"\n  LOW stage distribution by zone:")
for z in ['HEADER', 'BODY', 'TAIL']:
    states = zone_states.get(z, [])
    if states:
        lo_counts = Counter(STAGES[s[0]] for s in states)
        total = len(states)
        dist_str = ', '.join(f"{s[:4]}={lo_counts.get(s, 0)/total*100:.0f}%" for s in STAGES)
        print(f"    {z}: {dist_str}")

print(f"\n  HIGH stage distribution by zone:")
for z in ['HEADER', 'BODY', 'TAIL']:
    states = zone_states.get(z, [])
    if states:
        ho_counts = Counter(STAGES[s[1]] for s in states)
        total = len(states)
        dist_str = ', '.join(f"{s[:4]}={ho_counts.get(s, 0)/total*100:.0f}%" for s in STAGES)
        print(f"    {z}: {dist_str}")

# ============================================================
# 3. STATE DISTRIBUTION DIFFERENCE
# ============================================================
print(f"\n{'='*70}")
print("3. STATE DISTRIBUTION DIFFERENCE BETWEEN ZONES")
print("=" * 70)

# Are header/tail states drawn from a different distribution than body?
# Chi-squared: zone x LOW_stage
if zone_states.get('HEADER') and zone_states.get('BODY') and zone_states.get('TAIL'):
    # LOW axis
    contingency_lo = np.zeros((3, 6), dtype=int)
    for zi, z in enumerate(['HEADER', 'BODY', 'TAIL']):
        for lo, ho in zone_states[z]:
            contingency_lo[zi, lo] += 1

    chi2_lo, p_lo, dof_lo, _ = chi2_contingency(contingency_lo)
    n_total_lo = contingency_lo.sum()
    v_lo = np.sqrt(chi2_lo / (n_total_lo * (min(3, 6) - 1))) if n_total_lo > 0 else 0
    print(f"\n  LOW stage x Zone: chi2={chi2_lo:.2f}, p={p_lo:.4f}, Cramer's V={v_lo:.3f}")

    # HIGH axis
    contingency_ho = np.zeros((3, 6), dtype=int)
    for zi, z in enumerate(['HEADER', 'BODY', 'TAIL']):
        for lo, ho in zone_states[z]:
            contingency_ho[zi, ho] += 1

    chi2_ho, p_ho, dof_ho, _ = chi2_contingency(contingency_ho)
    n_total_ho = contingency_ho.sum()
    v_ho = np.sqrt(chi2_ho / (n_total_ho * (min(3, 6) - 1))) if n_total_ho > 0 else 0
    print(f"  HIGH stage x Zone: chi2={chi2_ho:.2f}, p={p_ho:.4f}, Cramer's V={v_ho:.3f}")

    # Show the distributions
    print(f"\n  LOW stage proportions:")
    print(f"  {'Zone':<10}", end='')
    for s in STAGES:
        print(f"  {s[:4]:>6}", end='')
    print()
    for zi, z in enumerate(['HEADER', 'BODY', 'TAIL']):
        row_sum = contingency_lo[zi].sum()
        print(f"  {z:<10}", end='')
        for si in range(6):
            pct = contingency_lo[zi, si] / row_sum * 100 if row_sum > 0 else 0
            print(f"  {pct:>5.1f}%", end='')
        print()

    print(f"\n  HIGH stage proportions:")
    print(f"  {'Zone':<10}", end='')
    for s in STAGES:
        print(f"  {s[:4]:>6}", end='')
    print()
    for zi, z in enumerate(['HEADER', 'BODY', 'TAIL']):
        row_sum = contingency_ho[zi].sum()
        print(f"  {z:<10}", end='')
        for si in range(6):
            pct = contingency_ho[zi, si] / row_sum * 100 if row_sum > 0 else 0
            print(f"  {pct:>5.1f}%", end='')
        print()
else:
    v_lo = 0
    v_ho = 0
    p_lo = 1
    p_ho = 1

# ============================================================
# 4. FL MIDDLE DIVERSITY BY ZONE
# ============================================================
print(f"\n{'='*70}")
print("4. FL MIDDLE DIVERSITY BY ZONE")
print("=" * 70)

zone_middles = defaultdict(list)
for key, data in line_fl_data.items():
    zone = line_zone.get(key)
    if zone and zone != 'SOLO':
        zone_middles[zone].extend(data['fl_middles'])

print(f"\n  {'Zone':<10} {'Total FL':>10} {'Unique':>8} {'Entropy':>10} {'Top 3':>30}")
for z in ['HEADER', 'BODY', 'TAIL']:
    mids = zone_middles.get(z, [])
    if mids:
        counts = Counter(mids)
        total = len(mids)
        unique = len(counts)
        # Shannon entropy
        probs = np.array([c / total for c in counts.values()])
        entropy = -np.sum(probs * np.log2(probs))
        top3 = ', '.join(f"{m}({c/total*100:.0f}%)" for m, c in counts.most_common(3))
        print(f"  {z:<10} {total:>10} {unique:>8} {entropy:>10.2f} {top3:>30}")

# ============================================================
# 5. CENTER CONTENT PREDICTABILITY BY ZONE
# ============================================================
print(f"\n{'='*70}")
print("5. CENTER CONTENT SIMILARITY BY ZONE")
print("=" * 70)

# For lines with coordinates: group center MIDDLEs by state and zone
# Compare: do same-state lines have more similar centers within BODY than HEADER/TAIL?

state_center_by_zone = defaultdict(lambda: defaultdict(list))
for key, data in line_fl_data.items():
    zone = line_zone.get(key)
    if zone and zone != 'SOLO' and data['has_coord']:
        state = (data['lo'], data['ho'])
        state_center_by_zone[zone][state].append(set(data['center_middles']))

# Jaccard similarity within same state, by zone
zone_jaccard = defaultdict(list)
for z in ['HEADER', 'BODY', 'TAIL']:
    for state, center_sets in state_center_by_zone[z].items():
        if len(center_sets) < 2:
            continue
        for i in range(len(center_sets)):
            for j in range(i + 1, len(center_sets)):
                if center_sets[i] or center_sets[j]:
                    inter = len(center_sets[i] & center_sets[j])
                    union = len(center_sets[i] | center_sets[j])
                    if union > 0:
                        zone_jaccard[z].append(inter / union)

print(f"\n  Same-state center Jaccard similarity:")
for z in ['HEADER', 'BODY', 'TAIL']:
    jaccards = zone_jaccard.get(z, [])
    if jaccards:
        print(f"    {z}: mean={np.mean(jaccards):.3f}, n={len(jaccards)}")
    else:
        print(f"    {z}: insufficient data")

# ============================================================
# 6. HEADER-SPECIFIC STAGE PREFERENCES
# ============================================================
print(f"\n{'='*70}")
print("6. HEADER vs TAIL STAGE PREFERENCES")
print("=" * 70)

header_states = zone_states.get('HEADER', [])
body_states = zone_states.get('BODY', [])
tail_states = zone_states.get('TAIL', [])

if header_states and body_states and tail_states:
    # Mean ordinals
    for z_name, states in [('HEADER', header_states), ('BODY', body_states), ('TAIL', tail_states)]:
        mean_lo = np.mean([s[0] for s in states])
        mean_ho = np.mean([s[1] for s in states])
        print(f"  {z_name}: mean ACTION={mean_lo:.2f} ({STAGES[int(round(mean_lo))][:4]}), "
              f"mean OVERSIGHT={mean_ho:.2f} ({STAGES[int(round(mean_ho))][:4]})")

    # Is header biased toward specific stages?
    print(f"\n  Header vs Body stage comparison:")
    h_lo = [s[0] for s in header_states]
    b_lo = [s[0] for s in body_states]
    t_lo = [s[0] for s in tail_states]
    h_ho = [s[1] for s in header_states]
    b_ho = [s[1] for s in body_states]
    t_ho = [s[1] for s in tail_states]

    u_hb_lo, p_hb_lo = mannwhitneyu(h_lo, b_lo, alternative='two-sided')
    u_hb_ho, p_hb_ho = mannwhitneyu(h_ho, b_ho, alternative='two-sided')
    u_tb_lo, p_tb_lo = mannwhitneyu(t_lo, b_lo, alternative='two-sided')
    u_tb_ho, p_tb_ho = mannwhitneyu(t_ho, b_ho, alternative='two-sided')

    print(f"    Header vs Body ACTION:    U={u_hb_lo:.0f}, p={p_hb_lo:.4f}")
    print(f"    Header vs Body OVERSIGHT: U={u_hb_ho:.0f}, p={p_hb_ho:.4f}")
    print(f"    Tail vs Body ACTION:      U={u_tb_lo:.0f}, p={p_tb_lo:.4f}")
    print(f"    Tail vs Body OVERSIGHT:   U={u_tb_ho:.0f}, p={p_tb_ho:.4f}")

# ============================================================
# 7. VERDICT
# ============================================================
print(f"\n{'='*70}")
print("7. VERDICT")
print("=" * 70)

# Check 1: FL rate differs by zone
check1 = p_kw < 0.01
# Check 2: Header has lower coord rate than body
h_rate = zone_coord_rate.get('HEADER', [0, 1])
b_rate_val = zone_coord_rate.get('BODY', [0, 1])
header_coord_pct = h_rate[0] / h_rate[1] * 100 if h_rate[1] > 0 else 0
body_coord_pct = b_rate_val[0] / b_rate_val[1] * 100 if b_rate_val[1] > 0 else 0
check2 = header_coord_pct < body_coord_pct - 5  # header 5pp lower
# Check 3: State distributions differ between zones
check3 = v_lo > 0.10 or v_ho > 0.10
# Check 4: Body has higher same-state Jaccard
body_jacc = np.mean(zone_jaccard.get('BODY', [0])) if zone_jaccard.get('BODY') else 0
header_jacc = np.mean(zone_jaccard.get('HEADER', [0])) if zone_jaccard.get('HEADER') else 0
check4 = body_jacc > header_jacc + 0.02
# Check 5: Header/tail stage preferences differ from body
check5 = (p_hb_lo < 0.05 or p_hb_ho < 0.05 or p_tb_lo < 0.05 or p_tb_ho < 0.05) if header_states and body_states and tail_states else False

checks = [check1, check2, check3, check4, check5]
n_pass = sum(checks)

print(f"\n  Checks passed: {n_pass}/5")
print(f"  1. FL rate differs by zone:        {'PASS' if check1 else 'FAIL'}")
print(f"  2. Header lower coord rate:        {'PASS' if check2 else 'FAIL'} "
      f"(H={header_coord_pct:.1f}%, B={body_coord_pct:.1f}%)")
print(f"  3. State distributions differ:     {'PASS' if check3 else 'FAIL'} "
      f"(V_lo={v_lo:.3f}, V_ho={v_ho:.3f})")
print(f"  4. Body higher same-state Jaccard: {'PASS' if check4 else 'FAIL'} "
      f"(B={body_jacc:.3f}, H={header_jacc:.3f})")
print(f"  5. Header/tail stage preference:   {'PASS' if check5 else 'FAIL'}")

if n_pass >= 4:
    verdict = "ZONE_SPECIFIC_FL"
    explanation = ("FL coordinate system is specific to paragraph body lines. "
                   "Headers and tails operate differently.")
elif n_pass >= 2:
    verdict = "WEAK_ZONE_EFFECT"
    explanation = ("Some differences between zones, but FL coordinates operate "
                   "across all paragraph positions.")
else:
    verdict = "ZONE_INDEPENDENT"
    explanation = ("FL coordinate system operates uniformly across all paragraph zones. "
                   "No evidence that body lines are specially state-indexed.")

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

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
    'fl_rate_by_zone': {
        z: {
            'mean': round(float(np.mean(zone_fl_rates.get(z, [0]))), 3),
            'n_lines': len(zone_fl_rates.get(z, [])),
        } for z in ['HEADER', 'BODY', 'TAIL']
    },
    'coord_rate_by_zone': {
        z: {
            'rate': round(zone_coord_rate.get(z, [0, 1])[0] / max(zone_coord_rate.get(z, [0, 1])[1], 1) * 100, 1),
            'n': zone_coord_rate.get(z, [0, 1])[1],
        } for z in ['HEADER', 'BODY', 'TAIL']
    },
    'state_distribution_test': {
        'v_low': round(float(v_lo), 3),
        'v_high': round(float(v_ho), 3),
        'p_low': round(float(p_lo), 4),
        'p_high': round(float(p_ho), 4),
    },
    'checks': {
        'fl_rate_differs': bool(check1),
        'header_lower_coord': bool(check2),
        'state_dist_differs': bool(check3),
        'body_higher_jaccard': bool(check4),
        'stage_preference': bool(check5),
    },
    'verdict': verdict,
    'explanation': explanation,
    'checks_passed': n_pass,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '40_paragraph_zone_fl_test.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
