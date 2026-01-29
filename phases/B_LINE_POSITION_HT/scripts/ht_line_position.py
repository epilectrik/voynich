"""
B_LINE_POSITION_HT: Test whether opening lines of B folios have
elevated HT (unclassified token) density compared to working lines.

Tests:
  T1: Line-1 vs Lines-2+ HT density (paired across folios)
  T2: Positional gradient (HT density by line position 1-10)
  T3: First-line HT morphological profile vs working-line HT
  T4: Section breakdown (H, B, S, C, T)
"""

import json, sys
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# Collect all B tokens organized by folio and line
folio_line_tokens = defaultdict(lambda: defaultdict(list))
folio_section = {}
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    folio_line_tokens[token.folio][token.line].append(w)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

# ============================================================
# T1: Line-1 vs Lines-2+ HT density
# ============================================================
print("=== T1: LINE-1 vs LINES-2+ HT DENSITY ===")

folio_line1_ht = {}  # folio -> HT fraction on line 1
folio_rest_ht = {}   # folio -> HT fraction on lines 2+
folio_stats = []

for folio in sorted(folio_line_tokens.keys()):
    lines = folio_line_tokens[folio]
    sorted_line_nums = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)

    if len(sorted_line_nums) < 2:
        continue  # Need at least 2 lines

    first_line = sorted_line_nums[0]
    rest_lines = sorted_line_nums[1:]

    # Line 1
    l1_tokens = lines[first_line]
    l1_total = len(l1_tokens)
    l1_ht = sum(1 for w in l1_tokens if w not in classified_tokens)
    l1_frac = l1_ht / l1_total if l1_total > 0 else 0

    # Lines 2+
    rest_tokens = [w for ln in rest_lines for w in lines[ln]]
    rest_total = len(rest_tokens)
    rest_ht = sum(1 for w in rest_tokens if w not in classified_tokens)
    rest_frac = rest_ht / rest_total if rest_total > 0 else 0

    folio_line1_ht[folio] = l1_frac
    folio_rest_ht[folio] = rest_frac

    folio_stats.append({
        'folio': folio,
        'section': folio_section.get(folio, '?'),
        'line1_ht': l1_ht,
        'line1_total': l1_total,
        'line1_frac': round(l1_frac, 4),
        'rest_ht': rest_ht,
        'rest_total': rest_total,
        'rest_frac': round(rest_frac, 4),
        'delta': round(l1_frac - rest_frac, 4),
        'n_lines': len(sorted_line_nums),
    })

# Paired comparison
folios_both = sorted(set(folio_line1_ht.keys()) & set(folio_rest_ht.keys()))
line1_fracs = np.array([folio_line1_ht[f] for f in folios_both])
rest_fracs = np.array([folio_rest_ht[f] for f in folios_both])
deltas = line1_fracs - rest_fracs

mean_line1 = np.mean(line1_fracs)
mean_rest = np.mean(rest_fracs)
mean_delta = np.mean(deltas)

# Wilcoxon signed-rank (non-parametric paired test)
wilcoxon_stat, wilcoxon_p = stats.wilcoxon(line1_fracs, rest_fracs, alternative='greater')

# Also paired t-test for reference
t_stat, t_p_two = stats.ttest_rel(line1_fracs, rest_fracs)
t_p_one = t_p_two / 2 if t_stat > 0 else 1 - t_p_two / 2

# Effect size (Cohen's d for paired)
d_cohen = mean_delta / np.std(deltas, ddof=1) if np.std(deltas, ddof=1) > 0 else 0

# How many folios show positive delta
n_positive = np.sum(deltas > 0)
n_zero = np.sum(deltas == 0)
n_negative = np.sum(deltas < 0)

print(f"  Folios analyzed: {len(folios_both)}")
print(f"  Mean line-1 HT fraction: {mean_line1:.4f} ({mean_line1*100:.1f}%)")
print(f"  Mean lines-2+ HT fraction: {mean_rest:.4f} ({mean_rest*100:.1f}%)")
print(f"  Mean delta (line1 - rest): {mean_delta:.4f} ({mean_delta*100:.1f}pp)")
print(f"  Direction: {n_positive} positive / {n_zero} zero / {n_negative} negative")
print(f"  Wilcoxon signed-rank: W={wilcoxon_stat:.1f}, p={wilcoxon_p:.6f}")
print(f"  Paired t-test (one-sided): t={t_stat:.3f}, p={t_p_one:.6f}")
print(f"  Cohen's d: {d_cohen:.3f}")
print()

t1_verdict = "ENRICHED" if wilcoxon_p < 0.01 and mean_delta > 0.02 else \
             "MARGINAL" if wilcoxon_p < 0.05 else "NO_EFFECT"
print(f"  T1 VERDICT: {t1_verdict}")
print()

# ============================================================
# T2: Positional gradient (line positions 1-10)
# ============================================================
print("=== T2: HT DENSITY BY LINE POSITION (1-10) ===")

position_ht = defaultdict(list)  # position -> list of HT fractions per folio

for folio in sorted(folio_line_tokens.keys()):
    lines = folio_line_tokens[folio]
    sorted_line_nums = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)

    for pos_idx, line_num in enumerate(sorted_line_nums[:10]):
        tokens = lines[line_num]
        total = len(tokens)
        ht = sum(1 for w in tokens if w not in classified_tokens)
        frac = ht / total if total > 0 else 0
        position_ht[pos_idx + 1].append(frac)

gradient_data = []
for pos in range(1, 11):
    fracs = position_ht.get(pos, [])
    if not fracs:
        continue
    mn = np.mean(fracs)
    se = np.std(fracs, ddof=1) / np.sqrt(len(fracs)) if len(fracs) > 1 else 0
    gradient_data.append({
        'position': pos,
        'n_folios': len(fracs),
        'mean_ht_frac': round(mn, 4),
        'se': round(se, 4),
    })
    print(f"  Pos {pos:2d}: n={len(fracs):3d}, mean HT={mn*100:.1f}% (+/-{se*100:.1f}%)")

# Spearman correlation of position vs HT density (using all folio-level data)
all_positions = []
all_fracs_for_corr = []
for pos in range(1, 11):
    for frac in position_ht.get(pos, []):
        all_positions.append(pos)
        all_fracs_for_corr.append(frac)

spearman_r, spearman_p = stats.spearmanr(all_positions, all_fracs_for_corr)
print(f"\n  Spearman (position vs HT frac): r={spearman_r:.4f}, p={spearman_p:.6f}")

# Also test: is position 1 different from positions 2-5?
pos1 = position_ht.get(1, [])
pos2_5 = [f for p in range(2, 6) for f in position_ht.get(p, [])]
if pos1 and pos2_5:
    mw_stat, mw_p = stats.mannwhitneyu(pos1, pos2_5, alternative='greater')
    print(f"  Mann-Whitney pos1 vs pos2-5: U={mw_stat:.1f}, p={mw_p:.6f}")

t2_verdict = "GRADIENT" if spearman_p < 0.01 and spearman_r < 0 else \
             "STEP" if (wilcoxon_p < 0.01 and mean_delta > 0.02 and spearman_p > 0.05) else "FLAT"
print(f"\n  T2 VERDICT: {t2_verdict}")
print()

# ============================================================
# T3: First-line HT morphological profile vs working-line HT
# ============================================================
print("=== T3: FIRST-LINE HT vs WORKING-LINE HT MORPHOLOGY ===")

first_line_ht_tokens = []
working_line_ht_tokens = []

for folio in sorted(folio_line_tokens.keys()):
    lines = folio_line_tokens[folio]
    sorted_line_nums = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)

    if not sorted_line_nums:
        continue

    first_line = sorted_line_nums[0]
    rest_lines = sorted_line_nums[1:]

    for w in lines[first_line]:
        if w not in classified_tokens:
            first_line_ht_tokens.append(w)

    for ln in rest_lines:
        for w in lines[ln]:
            if w not in classified_tokens:
                working_line_ht_tokens.append(w)

print(f"  First-line HT tokens: {len(first_line_ht_tokens)}")
print(f"  Working-line HT tokens: {len(working_line_ht_tokens)}")

# PREFIX distribution
def get_prefix_dist(token_list):
    pfx_counts = Counter()
    for w in token_list:
        m = morph.extract(w)
        if m.prefix:
            lane = 'qo' if m.prefix == 'qo' else ('chsh' if m.prefix in ('ch', 'sh') else m.prefix)
            pfx_counts[lane] += 1
        else:
            pfx_counts['NONE'] += 1
    return pfx_counts

first_pfx = get_prefix_dist(first_line_ht_tokens)
work_pfx = get_prefix_dist(working_line_ht_tokens)

print("\n  PREFIX distribution:")
all_pfx = sorted(set(first_pfx.keys()) | set(work_pfx.keys()),
                 key=lambda x: -(first_pfx.get(x, 0) + work_pfx.get(x, 0)))
for pfx in all_pfx[:10]:
    f_n = first_pfx.get(pfx, 0)
    w_n = work_pfx.get(pfx, 0)
    f_pct = f_n / len(first_line_ht_tokens) * 100 if first_line_ht_tokens else 0
    w_pct = w_n / len(working_line_ht_tokens) * 100 if working_line_ht_tokens else 0
    print(f"    {pfx:8s}: first={f_n:4d} ({f_pct:5.1f}%)  work={w_n:5d} ({w_pct:5.1f}%)")

# SUFFIX distribution
def get_suffix_dist(token_list):
    sfx_counts = Counter()
    for w in token_list:
        m = morph.extract(w)
        if m.suffix:
            sfx_counts[m.suffix] += 1
        else:
            sfx_counts['BARE'] += 1
    return sfx_counts

first_sfx = get_suffix_dist(first_line_ht_tokens)
work_sfx = get_suffix_dist(working_line_ht_tokens)

print("\n  SUFFIX distribution:")
all_sfx = sorted(set(first_sfx.keys()) | set(work_sfx.keys()),
                 key=lambda x: -(first_sfx.get(x, 0) + work_sfx.get(x, 0)))
for sfx in all_sfx[:10]:
    f_n = first_sfx.get(sfx, 0)
    w_n = work_sfx.get(sfx, 0)
    f_pct = f_n / len(first_line_ht_tokens) * 100 if first_line_ht_tokens else 0
    w_pct = w_n / len(working_line_ht_tokens) * 100 if working_line_ht_tokens else 0
    print(f"    {sfx:8s}: first={f_n:4d} ({f_pct:5.1f}%)  work={w_n:5d} ({w_pct:5.1f}%)")

# Has articulator?
first_art = sum(1 for w in first_line_ht_tokens if morph.extract(w).has_articulator)
work_art = sum(1 for w in working_line_ht_tokens if morph.extract(w).has_articulator)
f_art_pct = first_art / len(first_line_ht_tokens) * 100 if first_line_ht_tokens else 0
w_art_pct = work_art / len(working_line_ht_tokens) * 100 if working_line_ht_tokens else 0
print(f"\n  Articulator rate: first={first_art}/{len(first_line_ht_tokens)} ({f_art_pct:.1f}%) "
      f"work={work_art}/{len(working_line_ht_tokens)} ({w_art_pct:.1f}%)")

# Type diversity
first_types = len(set(first_line_ht_tokens))
work_types = len(set(working_line_ht_tokens))
print(f"  Type diversity: first={first_types} types/{len(first_line_ht_tokens)} occ "
      f"({first_types/len(first_line_ht_tokens)*100:.1f}% unique)  "
      f"work={work_types} types/{len(working_line_ht_tokens)} occ "
      f"({work_types/len(working_line_ht_tokens)*100:.1f}% unique)")

# Chi-squared on prefix distributions (pooling small categories)
# Use top-3 prefixes + OTHER
def pool_for_chi2(dist, total, top_n=4):
    top = dist.most_common(top_n)
    pooled = {k: v for k, v in top}
    other = total - sum(pooled.values())
    if other > 0:
        pooled['_OTHER'] = other
    return pooled

first_pooled = pool_for_chi2(first_pfx, len(first_line_ht_tokens))
work_pooled = pool_for_chi2(work_pfx, len(working_line_ht_tokens))
all_cats = sorted(set(first_pooled.keys()) | set(work_pooled.keys()))
obs_first = [first_pooled.get(c, 0) for c in all_cats]
obs_work = [work_pooled.get(c, 0) for c in all_cats]

chi2_stat, chi2_p = stats.chi2_contingency([obs_first, obs_work])[:2]
print(f"\n  Chi-squared (PREFIX first vs work): chi2={chi2_stat:.2f}, p={chi2_p:.6f}")

t3_verdict = "DISTINCT" if chi2_p < 0.01 else "SIMILAR"
print(f"\n  T3 VERDICT: {t3_verdict}")
print()

# ============================================================
# T4: Section breakdown
# ============================================================
print("=== T4: SECTION BREAKDOWN ===")

section_deltas = defaultdict(list)
for fs in folio_stats:
    section_deltas[fs['section']].append(fs['delta'])

section_results = []
for sec in sorted(section_deltas.keys()):
    ds = np.array(section_deltas[sec])
    n = len(ds)
    mn = np.mean(ds)
    if n >= 5:
        # Wilcoxon within section
        sec_l1 = np.array([folio_line1_ht[fs['folio']] for fs in folio_stats if fs['section'] == sec])
        sec_rest = np.array([folio_rest_ht[fs['folio']] for fs in folio_stats if fs['section'] == sec])
        try:
            w_stat, w_p = stats.wilcoxon(sec_l1, sec_rest, alternative='greater')
        except ValueError:
            w_stat, w_p = 0, 1.0
    else:
        w_stat, w_p = 0, 1.0

    pos = np.sum(ds > 0)
    neg = np.sum(ds < 0)

    section_results.append({
        'section': sec,
        'n_folios': n,
        'mean_delta': round(float(mn), 4),
        'n_positive': int(pos),
        'n_negative': int(neg),
        'wilcoxon_p': round(float(w_p), 6),
    })

    sig = "***" if w_p < 0.001 else "**" if w_p < 0.01 else "*" if w_p < 0.05 else "ns"
    print(f"  {sec}: n={n:2d}, mean delta={mn*100:+5.1f}pp, "
          f"+:{pos:.0f} -:{neg:.0f}, Wilcoxon p={w_p:.4f} {sig}")

print()

# ============================================================
# T5: Permutation test (folio-level shuffle)
# ============================================================
print("=== T5: PERMUTATION TEST ===")

rng = np.random.RandomState(42)
n_perm = 10000

# Observed: mean delta across folios
observed_delta = mean_delta

# Null: for each folio, randomly assign tokens to "line 1" vs "rest"
# preserving the same line-1 size
perm_deltas = []
for _ in range(n_perm):
    perm_delta_sum = 0
    n_folios_used = 0
    for folio in folios_both:
        lines = folio_line_tokens[folio]
        sorted_line_nums = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)
        if len(sorted_line_nums) < 2:
            continue

        first_line = sorted_line_nums[0]
        l1_size = len(lines[first_line])

        # Pool all tokens
        all_tokens = [w for ln in sorted_line_nums for w in lines[ln]]
        # Shuffle
        rng.shuffle(all_tokens)

        # Split
        fake_l1 = all_tokens[:l1_size]
        fake_rest = all_tokens[l1_size:]

        fake_l1_ht = sum(1 for w in fake_l1 if w not in classified_tokens) / len(fake_l1) if fake_l1 else 0
        fake_rest_ht = sum(1 for w in fake_rest if w not in classified_tokens) / len(fake_rest) if fake_rest else 0

        perm_delta_sum += (fake_l1_ht - fake_rest_ht)
        n_folios_used += 1

    perm_deltas.append(perm_delta_sum / n_folios_used if n_folios_used > 0 else 0)

perm_deltas = np.array(perm_deltas)
perm_p = np.mean(perm_deltas >= observed_delta)
perm_mean = np.mean(perm_deltas)
perm_std = np.std(perm_deltas)
perm_z = (observed_delta - perm_mean) / perm_std if perm_std > 0 else 0

print(f"  Observed mean delta: {observed_delta*100:.2f}pp")
print(f"  Permutation null mean: {perm_mean*100:.4f}pp")
print(f"  Permutation null std: {perm_std*100:.4f}pp")
print(f"  z-score: {perm_z:.2f}")
print(f"  Permutation p-value (n={n_perm}): {perm_p:.6f}")

t5_verdict = "SIGNIFICANT" if perm_p < 0.001 else "MARGINAL" if perm_p < 0.05 else "NO_EFFECT"
print(f"\n  T5 VERDICT: {t5_verdict}")
print()

# ============================================================
# T6: Last-line comparison
# ============================================================
print("=== T6: LAST-LINE HT DENSITY ===")

folio_last_ht = {}
for folio in sorted(folio_line_tokens.keys()):
    lines = folio_line_tokens[folio]
    sorted_line_nums = sorted(lines.keys(), key=lambda x: int(x) if x.isdigit() else 0)
    if len(sorted_line_nums) < 3:
        continue
    last_line = sorted_line_nums[-1]
    last_tokens = lines[last_line]
    lt_total = len(last_tokens)
    lt_ht = sum(1 for w in last_tokens if w not in classified_tokens)
    folio_last_ht[folio] = lt_ht / lt_total if lt_total > 0 else 0

folios_all3 = sorted(set(folio_line1_ht.keys()) & set(folio_rest_ht.keys()) & set(folio_last_ht.keys()))
last_fracs = np.array([folio_last_ht[f] for f in folios_all3])
rest_fracs_3 = np.array([folio_rest_ht[f] for f in folios_all3])
line1_fracs_3 = np.array([folio_line1_ht[f] for f in folios_all3])

mean_last = np.mean(last_fracs)
mean_rest_3 = np.mean(rest_fracs_3)
mean_line1_3 = np.mean(line1_fracs_3)

print(f"  Mean line-1 HT: {mean_line1_3*100:.1f}%")
print(f"  Mean interior HT: {mean_rest_3*100:.1f}%")
print(f"  Mean last-line HT: {mean_last*100:.1f}%")

# Is last line also elevated?
try:
    w_last, p_last = stats.wilcoxon(last_fracs, rest_fracs_3, alternative='greater')
    print(f"  Last vs interior Wilcoxon: W={w_last:.1f}, p={p_last:.6f}")
except ValueError:
    p_last = 1.0
    print(f"  Last vs interior Wilcoxon: insufficient variation")

t6_verdict = "LAST_ENRICHED" if p_last < 0.01 else "LAST_NORMAL"
print(f"\n  T6 VERDICT: {t6_verdict}")
print()

# ============================================================
# Save results
# ============================================================
results = {
    'phase': 'B_LINE_POSITION_HT',
    'description': 'Test whether opening lines of B folios have elevated HT density',
    'T1_line1_vs_rest': {
        'verdict': t1_verdict,
        'n_folios': len(folios_both),
        'mean_line1_ht_frac': round(float(mean_line1), 4),
        'mean_rest_ht_frac': round(float(mean_rest), 4),
        'mean_delta': round(float(mean_delta), 4),
        'n_positive': int(n_positive),
        'n_negative': int(n_negative),
        'wilcoxon_stat': round(float(wilcoxon_stat), 2),
        'wilcoxon_p': round(float(wilcoxon_p), 8),
        'paired_t': round(float(t_stat), 4),
        'paired_t_p': round(float(t_p_one), 8),
        'cohens_d': round(float(d_cohen), 4),
    },
    'T2_gradient': {
        'verdict': t2_verdict,
        'positions': gradient_data,
        'spearman_r': round(float(spearman_r), 4),
        'spearman_p': round(float(spearman_p), 8),
    },
    'T3_morphology': {
        'verdict': t3_verdict,
        'first_line_ht_count': len(first_line_ht_tokens),
        'working_line_ht_count': len(working_line_ht_tokens),
        'first_line_ht_types': first_types,
        'working_line_ht_types': work_types,
        'prefix_chi2': round(float(chi2_stat), 2),
        'prefix_chi2_p': round(float(chi2_p), 8),
        'first_articulator_rate': round(float(f_art_pct), 2),
        'working_articulator_rate': round(float(w_art_pct), 2),
    },
    'T4_sections': section_results,
    'T5_permutation': {
        'verdict': t5_verdict,
        'n_permutations': n_perm,
        'observed_delta': round(float(observed_delta), 6),
        'null_mean': round(float(perm_mean), 6),
        'null_std': round(float(perm_std), 6),
        'z_score': round(float(perm_z), 2),
        'p_value': round(float(perm_p), 6),
    },
    'T6_last_line': {
        'verdict': t6_verdict,
        'mean_line1_ht': round(float(mean_line1_3), 4),
        'mean_interior_ht': round(float(mean_rest_3), 4),
        'mean_last_ht': round(float(mean_last), 4),
        'last_vs_interior_p': round(float(p_last), 6),
    },
    'folio_details': folio_stats,
}

out_path = PROJECT_ROOT / 'phases' / 'B_LINE_POSITION_HT' / 'results' / 'ht_line_position.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=str)

print(f"Results saved to {out_path}")
print()
print("=== SUMMARY ===")
print(f"  T1 (Line-1 vs Rest):     {t1_verdict}")
print(f"  T2 (Positional gradient): {t2_verdict}")
print(f"  T3 (Morphology):          {t3_verdict}")
print(f"  T4 (Section breakdown):   see above")
print(f"  T5 (Permutation):         {t5_verdict}")
print(f"  T6 (Last line):           {t6_verdict}")
