"""
41_tail_reset_test.py

Do paragraph tail lines reset the state toward INITIAL/EARLY?

Script 40 showed tails are enriched at INITIAL (6%) and EARLY (8.4%) on the
ACTION axis, vs headers at 0.5% and 1.4%. Is this a deliberate state reset?

Tests:
  1. BODY->TAIL transition: does the tail consistently drop on ACTION/OVERSIGHT?
  2. DROP magnitude: how far does the tail fall from the body mean?
  3. HIGH->LOW reset: do paragraphs with high body states show bigger tail drops?
  4. TAIL->NEXT HEADER continuity: does the next paragraph's header pick up near
     the previous tail's state?
  5. Section consistency: is the reset pattern uniform across sections?
  6. Tail vs FIRST body line: compare tail state to first body line (spec zone)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, mannwhitneyu, wilcoxon

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
# Build data (same as script 39/40)
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

for f in folio_lines_ordered:
    seen = set()
    deduped = []
    for k in folio_lines_ordered[f]:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
    folio_lines_ordered[f] = deduped

# Build paragraphs per folio (ordered list of paragraphs)
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
        'lo': STAGE_ORDER[low_stage], 'ho': STAGE_ORDER[high_stage],
        'low': low_stage, 'high': high_stage,
    }

# ============================================================
# 1. BODY->TAIL TRANSITION
# ============================================================
print("=" * 70)
print("1. BODY -> TAIL STATE TRANSITION")
print("=" * 70)

# For each paragraph with 3+ lines (header + body + tail),
# compare last body line's state to tail line's state
body_to_tail_lo = []  # (last_body_lo, tail_lo)
body_to_tail_ho = []
body_mean_to_tail_lo = []
body_mean_to_tail_ho = []

for folio, paras in folio_paragraphs.items():
    for para in paras:
        if len(para) < 3:
            continue
        tail_key = para[-1]
        body_keys = para[1:-1]

        if tail_key not in line_coords:
            continue

        # Body lines with coordinates
        body_coords = [line_coords[k] for k in body_keys if k in line_coords]
        if not body_coords:
            continue

        tail = line_coords[tail_key]

        # Last body line
        last_body = body_coords[-1]
        body_to_tail_lo.append((last_body['lo'], tail['lo']))
        body_to_tail_ho.append((last_body['ho'], tail['ho']))

        # Body mean
        mean_body_lo = np.mean([c['lo'] for c in body_coords])
        mean_body_ho = np.mean([c['ho'] for c in body_coords])
        body_mean_to_tail_lo.append((mean_body_lo, tail['lo']))
        body_mean_to_tail_ho.append((mean_body_ho, tail['ho']))

if body_to_tail_lo:
    # Direction of last-body -> tail
    lo_drops = [b - t for b, t in body_to_tail_lo]
    ho_drops = [b - t for b, t in body_to_tail_ho]

    lo_down = sum(1 for d in lo_drops if d > 0)
    lo_same = sum(1 for d in lo_drops if d == 0)
    lo_up = sum(1 for d in lo_drops if d < 0)
    ho_down = sum(1 for d in ho_drops if d > 0)
    ho_same = sum(1 for d in ho_drops if d == 0)
    ho_up = sum(1 for d in ho_drops if d < 0)
    n = len(lo_drops)

    print(f"\n  Paragraphs with body+tail coordinates: {n}")
    print(f"\n  Last body -> tail (ACTION):")
    print(f"    DROP (body > tail): {lo_down} ({lo_down/n*100:.1f}%)")
    print(f"    SAME:               {lo_same} ({lo_same/n*100:.1f}%)")
    print(f"    RISE (body < tail): {lo_up} ({lo_up/n*100:.1f}%)")
    print(f"    Mean drop: {np.mean(lo_drops):+.2f}")

    print(f"\n  Last body -> tail (OVERSIGHT):")
    print(f"    DROP (body > tail): {ho_down} ({ho_down/n*100:.1f}%)")
    print(f"    SAME:               {ho_same} ({ho_same/n*100:.1f}%)")
    print(f"    RISE (body < tail): {ho_up} ({ho_up/n*100:.1f}%)")
    print(f"    Mean drop: {np.mean(ho_drops):+.2f}")

    # Wilcoxon signed-rank: are drops significant?
    if len(set(lo_drops)) > 1:
        w_lo, p_wlo = wilcoxon(lo_drops, alternative='greater')
        print(f"\n  Wilcoxon (ACTION drop > 0): W={w_lo:.0f}, p={p_wlo:.4f}")
    else:
        p_wlo = 1.0
    if len(set(ho_drops)) > 1:
        w_ho, p_who = wilcoxon(ho_drops, alternative='greater')
        print(f"  Wilcoxon (OVERSIGHT drop > 0): W={w_ho:.0f}, p={p_who:.4f}")
    else:
        p_who = 1.0

    # Body mean -> tail
    lo_mean_drops = [b - t for b, t in body_mean_to_tail_lo]
    ho_mean_drops = [b - t for b, t in body_mean_to_tail_ho]
    print(f"\n  Body mean -> tail mean drop:")
    print(f"    ACTION:    {np.mean(lo_mean_drops):+.3f}")
    print(f"    OVERSIGHT: {np.mean(ho_mean_drops):+.3f}")
else:
    p_wlo = 1.0
    p_who = 1.0

pass_1 = p_wlo < 0.05
print(f"\n  CHECK 1 (tail drops on ACTION): {'PASS' if pass_1 else 'FAIL'}")

# ============================================================
# 2. DROP MAGNITUDE
# ============================================================
print(f"\n{'='*70}")
print("2. DROP MAGNITUDE DISTRIBUTION")
print("=" * 70)

if body_to_tail_lo:
    print(f"\n  ACTION drop distribution (last body - tail):")
    for d in range(-5, 6):
        count = sum(1 for x in lo_drops if x == d)
        if count > 0:
            pct = count / len(lo_drops) * 100
            bar = '#' * int(pct)
            print(f"    {d:+2d}: {count:>4} ({pct:>5.1f}%) {bar}")

    print(f"\n  OVERSIGHT drop distribution (last body - tail):")
    for d in range(-5, 6):
        count = sum(1 for x in ho_drops if x == d)
        if count > 0:
            pct = count / len(ho_drops) * 100
            bar = '#' * int(pct)
            print(f"    {d:+2d}: {count:>4} ({pct:>5.1f}%) {bar}")

# ============================================================
# 3. HIGH->LOW RESET: bigger drops from higher body states?
# ============================================================
print(f"\n{'='*70}")
print("3. HIGH BODY -> LOW TAIL: PROPORTIONAL RESET?")
print("=" * 70)

if body_mean_to_tail_lo:
    body_means_lo = [b for b, t in body_mean_to_tail_lo]
    tail_vals_lo = [t for b, t in body_mean_to_tail_lo]
    drops_lo = [b - t for b, t in body_mean_to_tail_lo]

    rho_lo, p_rho_lo = spearmanr(body_means_lo, drops_lo)
    print(f"\n  Correlation: body mean ACTION vs drop size")
    print(f"    rho={rho_lo:+.3f}, p={p_rho_lo:.4f}")
    print(f"    (Positive = higher body -> bigger drop)")

    # Stratify by body level
    print(f"\n  Drop by body ACTION level:")
    for lo_level in range(6):
        mask = [(b, d) for b, d in zip(body_means_lo, drops_lo) if int(round(b)) == lo_level]
        if mask:
            mean_drop = np.mean([d for _, d in mask])
            print(f"    Body ~{STAGES[lo_level][:4]}: n={len(mask)}, mean drop={mean_drop:+.2f}")

    body_means_ho = [b for b, t in body_mean_to_tail_ho]
    drops_ho = [b - t for b, t in body_mean_to_tail_ho]
    rho_ho, p_rho_ho = spearmanr(body_means_ho, drops_ho)
    print(f"\n  Correlation: body mean OVERSIGHT vs drop size")
    print(f"    rho={rho_ho:+.3f}, p={p_rho_ho:.4f}")
else:
    rho_lo = 0
    p_rho_lo = 1

pass_3 = rho_lo > 0.3 and p_rho_lo < 0.01
print(f"\n  CHECK 3 (proportional reset): {'PASS' if pass_3 else 'FAIL'}")

# ============================================================
# 4. TAIL -> NEXT HEADER CONTINUITY
# ============================================================
print(f"\n{'='*70}")
print("4. TAIL -> NEXT HEADER CONTINUITY")
print("=" * 70)

tail_to_header_lo = []
tail_to_header_ho = []

for folio, paras in folio_paragraphs.items():
    for pi in range(len(paras) - 1):
        this_para = paras[pi]
        next_para = paras[pi + 1]

        if len(this_para) < 2 or len(next_para) < 1:
            continue

        tail_key = this_para[-1]
        next_header_key = next_para[0]

        if tail_key in line_coords and next_header_key in line_coords:
            tail = line_coords[tail_key]
            header = line_coords[next_header_key]
            tail_to_header_lo.append((tail['lo'], header['lo']))
            tail_to_header_ho.append((tail['ho'], header['ho']))

if tail_to_header_lo:
    n = len(tail_to_header_lo)

    # Distance between tail and next header
    th_dists = [abs(t - h) + abs(to - ho)
                for (t, to), (h, ho) in zip(tail_to_header_lo, tail_to_header_ho)]
    mean_th_dist = np.mean(th_dists)

    # Compare to random pairing baseline
    rng = np.random.default_rng(42)
    random_dists = []
    all_tails = [(t, to) for t, to in zip([x[0] for x in tail_to_header_lo],
                                           [x[0] for x in tail_to_header_ho])]
    all_headers = [(h, ho) for h, ho in zip([x[1] for x in tail_to_header_lo],
                                             [x[1] for x in tail_to_header_ho])]
    for _ in range(1000):
        shuffled = list(range(len(all_headers)))
        rng.shuffle(shuffled)
        rd = [abs(all_tails[i][0] - all_headers[shuffled[i]][0]) +
              abs(all_tails[i][1] - all_headers[shuffled[i]][1]) for i in range(n)]
        random_dists.append(np.mean(rd))

    random_mean = np.mean(random_dists)
    perm_p = np.mean([r <= mean_th_dist for r in random_dists])

    print(f"\n  Tail -> Next header pairs: {n}")
    print(f"  Mean Manhattan distance: {mean_th_dist:.3f}")
    print(f"  Random baseline:         {random_mean:.3f}")
    print(f"  Ratio (actual/random):   {mean_th_dist/random_mean:.3f}")
    print(f"  Permutation p (closer than random): {perm_p:.4f}")

    # Direction: does next header match tail or go higher?
    th_lo_diff = [h - t for t, h in tail_to_header_lo]
    th_ho_diff = [h - t for t, h in tail_to_header_ho]
    print(f"\n  Tail -> Next header direction:")
    print(f"    ACTION:    mean diff = {np.mean(th_lo_diff):+.3f} "
          f"(+ = header higher than tail)")
    print(f"    OVERSIGHT: mean diff = {np.mean(th_ho_diff):+.3f}")

    # If tail resets to low and header starts mid/high, that's the pattern
    lo_up = sum(1 for d in th_lo_diff if d > 0)
    lo_same = sum(1 for d in th_lo_diff if d == 0)
    lo_down = sum(1 for d in th_lo_diff if d < 0)
    print(f"    ACTION: {lo_up} rise, {lo_same} same, {lo_down} drop")
else:
    mean_th_dist = 0
    random_mean = 1
    perm_p = 1

pass_4 = perm_p < 0.05 or (tail_to_header_lo and np.mean([h - t for t, h in tail_to_header_lo]) > 0.3)
print(f"\n  CHECK 4 (tail->header continuity or reset->rise): {'PASS' if pass_4 else 'FAIL'}")

# ============================================================
# 5. SECTION CONSISTENCY
# ============================================================
print(f"\n{'='*70}")
print("5. SECTION CONSISTENCY OF TAIL RESET")
print("=" * 70)

section_drops = defaultdict(lambda: {'lo': [], 'ho': []})
for folio, paras in folio_paragraphs.items():
    section = line_meta[paras[0][0]]['section'] if paras and paras[0] else '?'
    for para in paras:
        if len(para) < 3:
            continue
        tail_key = para[-1]
        body_keys = para[1:-1]
        if tail_key not in line_coords:
            continue
        body_coords = [line_coords[k] for k in body_keys if k in line_coords]
        if not body_coords:
            continue
        tail = line_coords[tail_key]
        mean_body_lo = np.mean([c['lo'] for c in body_coords])
        mean_body_ho = np.mean([c['ho'] for c in body_coords])
        section_drops[section]['lo'].append(mean_body_lo - tail['lo'])
        section_drops[section]['ho'].append(mean_body_ho - tail['ho'])

print(f"\n  {'Section':<10} {'N':>5} {'ACTION drop':>15} {'OVERSIGHT drop':>18} {'% dropping':>12}")
for sec in sorted(section_drops.keys()):
    data = section_drops[sec]
    n = len(data['lo'])
    mean_lo = np.mean(data['lo'])
    mean_ho = np.mean(data['ho'])
    pct_drop = sum(1 for d in data['lo'] if d > 0) / n * 100 if n > 0 else 0
    print(f"  {sec:<10} {n:>5} {mean_lo:>+14.3f} {mean_ho:>+17.3f} {pct_drop:>11.1f}%")

# ============================================================
# 6. TAIL STATE vs HEADER STATE (within same paragraph)
# ============================================================
print(f"\n{'='*70}")
print("6. HEADER vs TAIL STATE (same paragraph)")
print("=" * 70)

header_tail_lo = []
header_tail_ho = []
for folio, paras in folio_paragraphs.items():
    for para in paras:
        if len(para) < 3:
            continue
        header_key = para[0]
        tail_key = para[-1]
        if header_key in line_coords and tail_key in line_coords:
            h = line_coords[header_key]
            t = line_coords[tail_key]
            header_tail_lo.append((h['lo'], t['lo']))
            header_tail_ho.append((h['ho'], t['ho']))

if header_tail_lo:
    ht_lo_diff = [t - h for h, t in header_tail_lo]
    ht_ho_diff = [t - h for h, t in header_tail_ho]
    print(f"\n  Paragraphs with coordinated header+tail: {len(header_tail_lo)}")
    print(f"  Mean header->tail shift:")
    print(f"    ACTION:    {np.mean(ht_lo_diff):+.3f} (- = tail lower)")
    print(f"    OVERSIGHT: {np.mean(ht_ho_diff):+.3f}")

    lo_lower = sum(1 for d in ht_lo_diff if d < 0)
    lo_same = sum(1 for d in ht_lo_diff if d == 0)
    lo_higher = sum(1 for d in ht_lo_diff if d > 0)
    n = len(ht_lo_diff)
    print(f"    ACTION: tail lower={lo_lower} ({lo_lower/n*100:.1f}%), "
          f"same={lo_same} ({lo_same/n*100:.1f}%), "
          f"higher={lo_higher} ({lo_higher/n*100:.1f}%)")

# ============================================================
# 7. VERDICT
# ============================================================
print(f"\n{'='*70}")
print("7. VERDICT")
print("=" * 70)

checks = [pass_1, pass_3, pass_4]
# Additional: is the tail consistently lower than body mean?
if body_mean_to_tail_lo:
    mean_drop = np.mean([b - t for b, t in body_mean_to_tail_lo])
    pass_drop = mean_drop > 0.2
else:
    pass_drop = False

# Section consistency: do most sections show drops?
sections_dropping = sum(1 for sec in section_drops.values()
                        if np.mean(sec['lo']) > 0)
pass_section = sections_dropping >= len(section_drops) * 0.6

all_checks = [pass_1, pass_drop, pass_3, pass_4, pass_section]
n_pass = sum(all_checks)

print(f"\n  Checks passed: {n_pass}/5")
print(f"  1. Wilcoxon tail drop (ACTION):     {'PASS' if pass_1 else 'FAIL'}")
print(f"  2. Mean body->tail drop > 0.2:       {'PASS' if pass_drop else 'FAIL'}")
print(f"  3. Proportional reset (rho):         {'PASS' if pass_3 else 'FAIL'}")
print(f"  4. Tail->header continuity/rise:      {'PASS' if pass_4 else 'FAIL'}")
print(f"  5. Section consistency:              {'PASS' if pass_section else 'FAIL'}")

if n_pass >= 4:
    verdict = "STATE_RESET"
    expl = "Tail lines systematically reset the state toward lower/earlier stages"
elif n_pass >= 2:
    verdict = "PARTIAL_RESET"
    expl = "Some reset behavior but not consistent across all measures"
else:
    verdict = "NO_RESET"
    expl = "Tail lines do not show systematic state reset behavior"

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
    'body_to_tail_drop': {
        'n': len(body_to_tail_lo),
        'action_mean_drop': round(float(np.mean(lo_drops)), 3) if body_to_tail_lo else None,
        'oversight_mean_drop': round(float(np.mean(ho_drops)), 3) if body_to_tail_ho else None,
        'action_drop_pct': round(lo_down / len(lo_drops) * 100, 1) if body_to_tail_lo else None,
        'p_wilcoxon_action': round(float(p_wlo), 4),
    },
    'proportional_reset': {
        'rho_action': round(float(rho_lo), 3),
        'p_action': round(float(p_rho_lo), 4),
    },
    'tail_to_header': {
        'n': len(tail_to_header_lo),
        'mean_distance': round(float(mean_th_dist), 3) if tail_to_header_lo else None,
        'random_baseline': round(float(random_mean), 3) if tail_to_header_lo else None,
        'action_rise': round(float(np.mean([h - t for t, h in tail_to_header_lo])), 3) if tail_to_header_lo else None,
    },
    'checks': [bool(c) for c in all_checks],
    'verdict': verdict,
    'explanation': expl,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '41_tail_reset_test.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
