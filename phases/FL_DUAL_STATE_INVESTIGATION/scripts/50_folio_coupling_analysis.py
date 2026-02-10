"""
50_folio_coupling_analysis.py

Investigate how the relationship between the two FL grid axes (lo, ho)
varies across folios and sections.

Globally the axes are weakly correlated (rho=+0.084) with 63.4% diagonal
dominance. Hypothesis: different folios/sections have different COUPLING
between the axes -- e.g. some materials need more heat per unit drip
(steeper slope), others less (shallower slope). The off-diagonal spread
carries folio-specific information.

Parts:
  1. Per-folio coupling characterization
  2. Do folios differ systematically? (section-level KW, slope-vs-center)
  3. Diagonal vs off-diagonal content (vocabulary, section composition)
  4. Coupling slope as "material signature" (R-squared, slope clustering)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, kruskal, chi2_contingency, linregress

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
# Build data pipeline (same as scripts 42-49)
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

# Assign coordinates and extract center words per line
line_coords = {}
line_center_words = defaultdict(list)

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue
    fl_info = []
    center = []
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
            center.append(t.word)
    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue
    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    lo = STAGE_ORDER[low_stage]
    ho = STAGE_ORDER[high_stage]
    line_coords[line_key] = {'lo': lo, 'ho': ho}
    line_center_words[line_key] = center

print("=" * 70)
print("FOLIO COUPLING ANALYSIS")
print("=" * 70)
print(f"\nTotal lines with coordinates: {len(line_coords)}")

# ============================================================
# PART 1: Per-folio coupling characterization
# ============================================================
print(f"\n{'='*70}")
print("PART 1: PER-FOLIO COUPLING CHARACTERIZATION")
print("=" * 70)

# Group lines by folio
folio_lines = defaultdict(list)
for line_key, coords in line_coords.items():
    folio = line_meta[line_key]['folio']
    folio_lines[folio].append({
        'line_key': line_key,
        'lo': coords['lo'],
        'ho': coords['ho'],
        'section': line_meta[line_key]['section'],
    })

# Compute per-folio metrics
folio_metrics = {}
for folio, lines in folio_lines.items():
    n_lines = len(lines)
    if n_lines < 8:
        continue
    lo_arr = np.array([ln['lo'] for ln in lines])
    ho_arr = np.array([ln['ho'] for ln in lines])
    section = lines[0]['section']

    lo_mean = float(np.mean(lo_arr))
    ho_mean = float(np.mean(ho_arr))
    diag_offset = float(np.mean(lo_arr - ho_arr))

    # Per-folio Spearman correlation
    if len(set(lo_arr)) > 1 and len(set(ho_arr)) > 1:
        rho, rho_p = spearmanr(lo_arr, ho_arr)
        rho = float(rho)
        rho_p = float(rho_p)
    else:
        rho = 0.0
        rho_p = 1.0

    lo_range = float(np.ptp(lo_arr))
    ho_range = float(np.ptp(ho_arr))

    metrics = {
        'n_lines': n_lines,
        'section': section,
        'lo_mean': round(lo_mean, 3),
        'ho_mean': round(ho_mean, 3),
        'diag_offset': round(diag_offset, 3),
        'rho': round(rho, 3),
        'rho_p': round(rho_p, 4),
        'lo_range': round(lo_range, 1),
        'ho_range': round(ho_range, 1),
    }

    # OLS slope if >= 10 lines
    if n_lines >= 10 and len(set(lo_arr)) > 1:
        slope, intercept, r_value, p_value, std_err = linregress(lo_arr, ho_arr)
        metrics['slope'] = round(float(slope), 4)
        metrics['intercept'] = round(float(intercept), 4)
        metrics['r_squared'] = round(float(r_value ** 2), 4)
        metrics['slope_p'] = round(float(p_value), 4)
    else:
        metrics['slope'] = None
        metrics['intercept'] = None
        metrics['r_squared'] = None
        metrics['slope_p'] = None

    folio_metrics[folio] = metrics

print(f"\nFolios with >= 8 coordinated lines: {len(folio_metrics)}")
folios_with_slope = [f for f, m in folio_metrics.items() if m['slope'] is not None]
print(f"Folios with slope computed (>= 10 lines): {len(folios_with_slope)}")

# Print table
print(f"\n  {'Folio':<8} {'Sec':>4} {'N':>4} {'lo_m':>6} {'ho_m':>6} "
      f"{'offset':>7} {'rho':>6} {'slope':>7} {'R2':>6} {'lo_r':>5} {'ho_r':>5}")
print(f"  {'-'*8} {'-'*4} {'-'*4} {'-'*6} {'-'*6} "
      f"{'-'*7} {'-'*6} {'-'*7} {'-'*6} {'-'*5} {'-'*5}")

for folio in sorted(folio_metrics.keys()):
    m = folio_metrics[folio]
    slope_str = f"{m['slope']:>7.3f}" if m['slope'] is not None else "   n/a "
    r2_str = f"{m['r_squared']:>6.3f}" if m['r_squared'] is not None else "  n/a "
    print(f"  {folio:<8} {m['section']:>4} {m['n_lines']:>4} {m['lo_mean']:>6.2f} {m['ho_mean']:>6.2f} "
          f"{m['diag_offset']:>+7.2f} {m['rho']:>+6.3f} {slope_str} {r2_str} "
          f"{m['lo_range']:>5.1f} {m['ho_range']:>5.1f}")

# ============================================================
# PART 2: Do folios differ systematically?
# ============================================================
print(f"\n{'='*70}")
print("PART 2: SYSTEMATIC FOLIO DIFFERENCES")
print("=" * 70)

# 2.1 Distribution of diagonal offsets
all_offsets = [m['diag_offset'] for m in folio_metrics.values()]
print(f"\n  2.1 Diagonal offset distribution")
print(f"      Mean offset:   {np.mean(all_offsets):+.3f}")
print(f"      Std offset:    {np.std(all_offsets):.3f}")
print(f"      Min offset:    {np.min(all_offsets):+.3f}")
print(f"      Max offset:    {np.max(all_offsets):+.3f}")
print(f"      Range:         {np.ptp(all_offsets):.3f}")

# Histogram of offsets
offset_bins = {'below_neg1': 0, 'neg1_to_neg05': 0, 'neg05_to_0': 0,
               '0_to_pos05': 0, 'pos05_to_pos1': 0, 'above_pos1': 0}
for off in all_offsets:
    if off < -1.0:
        offset_bins['below_neg1'] += 1
    elif off < -0.5:
        offset_bins['neg1_to_neg05'] += 1
    elif off < 0.0:
        offset_bins['neg05_to_0'] += 1
    elif off < 0.5:
        offset_bins['0_to_pos05'] += 1
    elif off < 1.0:
        offset_bins['pos05_to_pos1'] += 1
    else:
        offset_bins['above_pos1'] += 1

print(f"\n      Offset histogram:")
for bin_name, count in offset_bins.items():
    bar = '#' * count
    print(f"        {bin_name:<18}: {count:>3} {bar}")

n_above = sum(1 for off in all_offsets if off > 0)
n_below = sum(1 for off in all_offsets if off < 0)
n_zero = sum(1 for off in all_offsets if off == 0)
print(f"\n      Above diagonal (offset > 0): {n_above}")
print(f"      Below diagonal (offset < 0): {n_below}")
print(f"      On diagonal (offset = 0):    {n_zero}")

# 2.2 Kruskal-Wallis on diagonal offsets by section
print(f"\n  2.2 Kruskal-Wallis: diagonal offsets by section")
section_offsets = defaultdict(list)
for folio, m in folio_metrics.items():
    section_offsets[m['section']].append(m['diag_offset'])

print(f"      Sections with folios:")
for sec in sorted(section_offsets.keys()):
    offs = section_offsets[sec]
    print(f"        {sec}: n={len(offs)}, mean_offset={np.mean(offs):+.3f}, "
          f"std={np.std(offs):.3f}")

kw_offset_groups = [np.array(v) for v in section_offsets.values() if len(v) >= 2]
kw_offset_sections = [k for k, v in section_offsets.items() if len(v) >= 2]

if len(kw_offset_groups) >= 2:
    kw_offset_stat, kw_offset_p = kruskal(*kw_offset_groups)
    kw_offset_stat = float(kw_offset_stat)
    kw_offset_p = float(kw_offset_p)
else:
    kw_offset_stat, kw_offset_p = 0.0, 1.0

print(f"\n      KW statistic: {kw_offset_stat:.3f}")
print(f"      KW p-value:   {kw_offset_p:.6f}")
print(f"      Groups used:  {len(kw_offset_groups)} ({', '.join(sorted(kw_offset_sections))})")
print(f"      Significant (p<0.05): {'YES' if kw_offset_p < 0.05 else 'NO'}")

# 2.3 Kruskal-Wallis on per-folio slopes by section
print(f"\n  2.3 Kruskal-Wallis: per-folio slopes by section")
section_slopes = defaultdict(list)
for folio, m in folio_metrics.items():
    if m['slope'] is not None:
        section_slopes[m['section']].append(m['slope'])

print(f"      Sections with slope data:")
for sec in sorted(section_slopes.keys()):
    slopes = section_slopes[sec]
    print(f"        {sec}: n={len(slopes)}, mean_slope={np.mean(slopes):+.3f}, "
          f"std={np.std(slopes):.3f}")

kw_slope_groups = [np.array(v) for v in section_slopes.values() if len(v) >= 2]
kw_slope_sections = [k for k, v in section_slopes.items() if len(v) >= 2]

if len(kw_slope_groups) >= 2:
    kw_slope_stat, kw_slope_p = kruskal(*kw_slope_groups)
    kw_slope_stat = float(kw_slope_stat)
    kw_slope_p = float(kw_slope_p)
else:
    kw_slope_stat, kw_slope_p = 0.0, 1.0

print(f"\n      KW statistic: {kw_slope_stat:.3f}")
print(f"      KW p-value:   {kw_slope_p:.6f}")
print(f"      Groups used:  {len(kw_slope_groups)} ({', '.join(sorted(kw_slope_sections))})")
print(f"      Significant (p<0.05): {'YES' if kw_slope_p < 0.05 else 'NO'}")

# 2.4 Spearman: slope vs center position (lo_mean)
print(f"\n  2.4 Spearman: slope vs folio center position (lo_mean)")
if len(folios_with_slope) >= 5:
    slope_arr = np.array([folio_metrics[f]['slope'] for f in folios_with_slope])
    lo_mean_arr = np.array([folio_metrics[f]['lo_mean'] for f in folios_with_slope])
    rho_slope_lo, p_slope_lo = spearmanr(lo_mean_arr, slope_arr)
    rho_slope_lo = float(rho_slope_lo)
    p_slope_lo = float(p_slope_lo)
    print(f"      rho(slope, lo_mean): {rho_slope_lo:+.3f}")
    print(f"      p-value:             {p_slope_lo:.4f}")
    print(f"      Significant (p<0.05): {'YES' if p_slope_lo < 0.05 else 'NO'}")
    print(f"      Interpretation: {'coupling varies with operating point' if p_slope_lo < 0.05 else 'coupling constant across operating points'}")
else:
    rho_slope_lo = 0.0
    p_slope_lo = 1.0
    print(f"      Insufficient folios with slopes for test")

# ============================================================
# PART 3: Diagonal vs off-diagonal content
# ============================================================
print(f"\n{'='*70}")
print("PART 3: DIAGONAL VS OFF-DIAGONAL CONTENT")
print("=" * 70)

# 3.1 Split lines into three groups
above_diag = []  # lo > ho + 1
on_diag = []     # |lo - ho| <= 1
below_diag = []  # ho > lo + 1

for line_key, coords in line_coords.items():
    lo, ho = coords['lo'], coords['ho']
    if lo > ho + 1:
        above_diag.append(line_key)
    elif ho > lo + 1:
        below_diag.append(line_key)
    else:
        on_diag.append(line_key)

print(f"\n  3.1 Line groups by diagonal position")
print(f"      ABOVE_DIAGONAL (lo > ho + 1): {len(above_diag)} lines")
print(f"      ON_DIAGONAL (|lo - ho| <= 1): {len(on_diag)} lines")
print(f"      BELOW_DIAGONAL (ho > lo + 1): {len(below_diag)} lines")

# Average coordinates per group
for name, group_keys in [('ABOVE', above_diag), ('ON', on_diag), ('BELOW', below_diag)]:
    if group_keys:
        avg_lo = np.mean([line_coords[k]['lo'] for k in group_keys])
        avg_ho = np.mean([line_coords[k]['ho'] for k in group_keys])
        print(f"      {name}: avg_lo={avg_lo:.2f}, avg_ho={avg_ho:.2f}")

# 3.2 Section composition by diagonal position
print(f"\n  3.2 Section composition: ABOVE vs BELOW diagonal")
above_sections = Counter(line_meta[k]['section'] for k in above_diag)
below_sections = Counter(line_meta[k]['section'] for k in below_diag)
on_sections = Counter(line_meta[k]['section'] for k in on_diag)

all_sections_in_data = sorted(set(list(above_sections.keys()) +
                                   list(below_sections.keys()) +
                                   list(on_sections.keys())))

print(f"\n      {'Section':<8} {'ABOVE':>7} {'ON':>7} {'BELOW':>7}")
print(f"      {'-'*8} {'-'*7} {'-'*7} {'-'*7}")
for sec in all_sections_in_data:
    print(f"      {sec:<8} {above_sections.get(sec, 0):>7} "
          f"{on_sections.get(sec, 0):>7} {below_sections.get(sec, 0):>7}")
print(f"      {'TOTAL':<8} {len(above_diag):>7} {len(on_diag):>7} {len(below_diag):>7}")

# Chi-squared: ABOVE vs BELOW section composition
print(f"\n  3.3 Chi-squared: ABOVE vs BELOW section compositions")
if len(above_diag) >= 10 and len(below_diag) >= 10:
    # Build contingency table for sections present in both groups
    common_sections = sorted(set(above_sections.keys()) | set(below_sections.keys()))
    if len(common_sections) >= 2:
        contingency = np.array([
            [above_sections.get(sec, 0) for sec in common_sections],
            [below_sections.get(sec, 0) for sec in common_sections],
        ])
        # Remove columns with all zeros
        col_sums = contingency.sum(axis=0)
        contingency = contingency[:, col_sums > 0]
        common_sections_filtered = [s for s, cs in zip(common_sections, col_sums) if cs > 0]

        if contingency.shape[1] >= 2:
            chi2_stat, chi2_p, chi2_dof, chi2_expected = chi2_contingency(contingency)
            chi2_stat = float(chi2_stat)
            chi2_p = float(chi2_p)
            chi2_dof = int(chi2_dof)
            print(f"      Chi2 statistic: {chi2_stat:.3f}")
            print(f"      p-value:        {chi2_p:.6f}")
            print(f"      dof:            {chi2_dof}")
            print(f"      Sections used:  {common_sections_filtered}")
            print(f"      Significant (p<0.05): {'YES' if chi2_p < 0.05 else 'NO'}")
        else:
            chi2_stat, chi2_p, chi2_dof = 0.0, 1.0, 0
            print(f"      Not enough sections for chi-squared test")
    else:
        chi2_stat, chi2_p, chi2_dof = 0.0, 1.0, 0
        print(f"      Not enough sections for chi-squared test")
else:
    chi2_stat, chi2_p, chi2_dof = 0.0, 1.0, 0
    print(f"      Not enough lines in ABOVE or BELOW for chi-squared test")

# 3.4 Vocabulary comparison: ABOVE vs BELOW
print(f"\n  3.4 Vocabulary comparison: ABOVE vs BELOW diagonal")
above_vocab = set()
below_vocab = set()
on_vocab = set()

for k in above_diag:
    above_vocab.update(line_center_words[k])
for k in below_diag:
    below_vocab.update(line_center_words[k])
for k in on_diag:
    on_vocab.update(line_center_words[k])

if above_vocab and below_vocab:
    jaccard_ab = len(above_vocab & below_vocab) / len(above_vocab | below_vocab)
    above_unique = above_vocab - below_vocab - on_vocab
    below_unique = below_vocab - above_vocab - on_vocab
    above_unique_rate = len(above_unique) / len(above_vocab) if above_vocab else 0
    below_unique_rate = len(below_unique) / len(below_vocab) if below_vocab else 0
else:
    jaccard_ab = 1.0
    above_unique_rate = 0.0
    below_unique_rate = 0.0

print(f"      ABOVE vocab size:  {len(above_vocab)}")
print(f"      BELOW vocab size:  {len(below_vocab)}")
print(f"      ON vocab size:     {len(on_vocab)}")
print(f"      Jaccard(ABOVE, BELOW): {jaccard_ab:.3f}")
print(f"      ABOVE unique tokens (not in BELOW or ON): {len(above_vocab - below_vocab - on_vocab)}")
print(f"      BELOW unique tokens (not in ABOVE or ON): {len(below_vocab - above_vocab - on_vocab)}")
print(f"      ABOVE unique rate: {above_unique_rate:.3f}")
print(f"      BELOW unique rate: {below_unique_rate:.3f}")

# ============================================================
# PART 4: Coupling slope as "material signature"
# ============================================================
print(f"\n{'='*70}")
print("PART 4: COUPLING SLOPE AS MATERIAL SIGNATURE")
print("=" * 70)

# 4.1 Distribution of slopes
all_slopes = [folio_metrics[f]['slope'] for f in folios_with_slope]
all_r_squared = [folio_metrics[f]['r_squared'] for f in folios_with_slope]

print(f"\n  4.1 Slope distribution (n={len(all_slopes)} folios)")
if all_slopes:
    print(f"      Mean slope:  {np.mean(all_slopes):+.3f}")
    print(f"      Std slope:   {np.std(all_slopes):.3f}")
    print(f"      Min slope:   {np.min(all_slopes):+.3f}")
    print(f"      Max slope:   {np.max(all_slopes):+.3f}")
    print(f"      Range:       {np.ptp(all_slopes):.3f}")
    print(f"      Median:      {np.median(all_slopes):+.3f}")

    # Histogram of slopes
    slope_hist = {'neg_strong (<-0.3)': 0, 'neg_moderate (-0.3 to -0.1)': 0,
                  'near_zero (-0.1 to 0.1)': 0, 'pos_moderate (0.1 to 0.3)': 0,
                  'pos_strong (>0.3)': 0}
    for s in all_slopes:
        if s < -0.3:
            slope_hist['neg_strong (<-0.3)'] += 1
        elif s < -0.1:
            slope_hist['neg_moderate (-0.3 to -0.1)'] += 1
        elif s < 0.1:
            slope_hist['near_zero (-0.1 to 0.1)'] += 1
        elif s < 0.3:
            slope_hist['pos_moderate (0.1 to 0.3)'] += 1
        else:
            slope_hist['pos_strong (>0.3)'] += 1

    print(f"\n      Slope histogram:")
    for bin_name, count in slope_hist.items():
        bar = '#' * count
        print(f"        {bin_name:<30}: {count:>3} {bar}")

# 4.2 Slope clustering
print(f"\n  4.2 Slope clustering")
slope_variance = float(np.std(all_slopes)) if all_slopes else 0.0
print(f"      Slope std: {slope_variance:.3f}")

if len(all_slopes) >= 10:
    # Try 1-component vs 2-component GMM on slopes
    slope_X = np.array(all_slopes).reshape(-1, 1)
    gmm1 = GaussianMixture(n_components=1, random_state=42, n_init=5)
    gmm2 = GaussianMixture(n_components=2, random_state=42, n_init=5)
    gmm1.fit(slope_X)
    gmm2.fit(slope_X)
    bic1 = gmm1.bic(slope_X)
    bic2 = gmm2.bic(slope_X)
    delta_bic = bic1 - bic2  # positive -> 2-component better

    print(f"      GMM(1) BIC: {bic1:.1f}")
    print(f"      GMM(2) BIC: {bic2:.1f}")
    print(f"      Delta BIC (1-comp minus 2-comp): {delta_bic:+.1f}")
    if delta_bic > 10:
        print(f"      -> Strong evidence for 2 coupling regimes")
        cluster_evidence = "STRONG"
    elif delta_bic > 2:
        print(f"      -> Moderate evidence for 2 coupling regimes")
        cluster_evidence = "MODERATE"
    else:
        print(f"      -> No evidence for distinct coupling regimes")
        cluster_evidence = "NONE"

    # Print 2-component parameters
    means = sorted(gmm2.means_.flatten())
    print(f"      GMM(2) means: {means[0]:+.3f}, {means[1]:+.3f}")
    weights = gmm2.weights_
    print(f"      GMM(2) weights: {weights[0]:.2f}, {weights[1]:.2f}")
else:
    delta_bic = 0.0
    cluster_evidence = "INSUFFICIENT_DATA"
    print(f"      Not enough folios for GMM clustering")

# 4.3 R-squared distribution
print(f"\n  4.3 R-squared distribution")
if all_r_squared:
    print(f"      Mean R2:   {np.mean(all_r_squared):.3f}")
    print(f"      Median R2: {np.median(all_r_squared):.3f}")
    print(f"      Min R2:    {np.min(all_r_squared):.3f}")
    print(f"      Max R2:    {np.max(all_r_squared):.3f}")

    n_r2_gt010 = sum(1 for r2 in all_r_squared if r2 > 0.10)
    n_r2_gt025 = sum(1 for r2 in all_r_squared if r2 > 0.25)
    n_r2_gt050 = sum(1 for r2 in all_r_squared if r2 > 0.50)
    pct_r2_gt010 = n_r2_gt010 / len(all_r_squared) * 100

    print(f"      R2 > 0.10: {n_r2_gt010}/{len(all_r_squared)} ({pct_r2_gt010:.1f}%)")
    print(f"      R2 > 0.25: {n_r2_gt025}/{len(all_r_squared)} ({n_r2_gt025/len(all_r_squared)*100:.1f}%)")
    print(f"      R2 > 0.50: {n_r2_gt050}/{len(all_r_squared)} ({n_r2_gt050/len(all_r_squared)*100:.1f}%)")

    # Per-folio R2 listing (sorted by R2 descending)
    print(f"\n      Top-10 folios by R-squared:")
    sorted_folios = sorted(folios_with_slope, key=lambda f: folio_metrics[f]['r_squared'], reverse=True)
    for i, f in enumerate(sorted_folios[:10]):
        m = folio_metrics[f]
        print(f"        {f:<8} sec={m['section']:>4} slope={m['slope']:+.3f} "
              f"R2={m['r_squared']:.3f} n={m['n_lines']}")
else:
    n_r2_gt010 = 0
    pct_r2_gt010 = 0.0

# ============================================================
# CHECKS AND VERDICT
# ============================================================
print(f"\n{'='*70}")
print("CHECKS AND VERDICT")
print("=" * 70)

# check_1: Per-folio diagonal offsets differ by section (KW p < 0.05)
check_1 = bool(kw_offset_p < 0.05)

# check_2: Per-folio slopes differ by section (KW p < 0.05)
check_2 = bool(kw_slope_p < 0.05)

# check_3: Above-diagonal and below-diagonal lines have different section
#           compositions (chi-squared p < 0.05)
check_3 = bool(chi2_p < 0.05)

# check_4: Per-folio slopes have meaningful variance (std > 0.15)
check_4 = bool(slope_variance > 0.15)

# check_5: At least 30% of folios with slopes have R-squared > 0.10
check_5 = bool(pct_r2_gt010 >= 30.0) if all_r_squared else False

checks_passed = sum([check_1, check_2, check_3, check_4, check_5])

print(f"\n  check_1: Diagonal offsets differ by section (KW p<0.05)")
print(f"    KW p = {kw_offset_p:.6f}")
print(f"    Result: {'PASS' if check_1 else 'FAIL'}")

print(f"\n  check_2: Per-folio slopes differ by section (KW p<0.05)")
print(f"    KW p = {kw_slope_p:.6f}")
print(f"    Result: {'PASS' if check_2 else 'FAIL'}")

print(f"\n  check_3: ABOVE vs BELOW have different section compositions (chi2 p<0.05)")
print(f"    chi2 p = {chi2_p:.6f}")
print(f"    Result: {'PASS' if check_3 else 'FAIL'}")

print(f"\n  check_4: Per-folio slopes have meaningful variance (std > 0.15)")
print(f"    slope std = {slope_variance:.3f}")
print(f"    Result: {'PASS' if check_4 else 'FAIL'}")

print(f"\n  check_5: >= 30% of folios have R2 > 0.10 (meaningful within-folio coupling)")
if all_r_squared:
    print(f"    {n_r2_gt010}/{len(all_r_squared)} = {pct_r2_gt010:.1f}%")
else:
    print(f"    No R-squared data available")
print(f"    Result: {'PASS' if check_5 else 'FAIL'}")

print(f"\n  Checks passed: {checks_passed}/5")

if checks_passed >= 3:
    verdict = "MATERIAL_SIGNATURE"
    explanation = ("The coupling between FL grid axes varies systematically across "
                   "folios and sections. Different folios show different slope "
                   "(coupling strength), diagonal offset, and R-squared values. "
                   "This supports the hypothesis that the off-diagonal spread "
                   "carries folio-specific material information.")
elif checks_passed == 2:
    verdict = "WEAK_SIGNATURE"
    explanation = ("Some evidence for folio-specific coupling variation, but not "
                   "enough for confident material signature identification. "
                   "The coupling may vary but the pattern is not robust across "
                   "all tested dimensions.")
else:
    verdict = "NO_SIGNATURE"
    explanation = ("No evidence that the coupling between FL grid axes varies "
                   "meaningfully across folios or sections. The off-diagonal "
                   "spread does not carry clear folio-specific information.")

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
    'n_lines_coordinated': len(line_coords),
    'n_folios_analyzed': len(folio_metrics),
    'n_folios_with_slope': len(folios_with_slope),
    'part1_per_folio': {
        folio: {
            'n_lines': m['n_lines'],
            'section': m['section'],
            'lo_mean': m['lo_mean'],
            'ho_mean': m['ho_mean'],
            'diag_offset': m['diag_offset'],
            'rho': m['rho'],
            'rho_p': m['rho_p'],
            'lo_range': m['lo_range'],
            'ho_range': m['ho_range'],
            'slope': m['slope'],
            'intercept': m['intercept'],
            'r_squared': m['r_squared'],
            'slope_p': m['slope_p'],
        }
        for folio, m in sorted(folio_metrics.items())
    },
    'part2_systematic': {
        'offset_distribution': {
            'mean': round(float(np.mean(all_offsets)), 4),
            'std': round(float(np.std(all_offsets)), 4),
            'min': round(float(np.min(all_offsets)), 4),
            'max': round(float(np.max(all_offsets)), 4),
            'n_above_diagonal': n_above,
            'n_below_diagonal': n_below,
        },
        'kw_offsets_by_section': {
            'H': round(kw_offset_stat, 3),
            'p': round(kw_offset_p, 6),
            'n_groups': len(kw_offset_groups),
            'significant': bool(kw_offset_p < 0.05),
        },
        'kw_slopes_by_section': {
            'H': round(kw_slope_stat, 3),
            'p': round(kw_slope_p, 6),
            'n_groups': len(kw_slope_groups),
            'significant': bool(kw_slope_p < 0.05),
        },
        'slope_vs_center_position': {
            'rho': round(rho_slope_lo, 4),
            'p': round(p_slope_lo, 4),
            'significant': bool(p_slope_lo < 0.05),
        },
    },
    'part3_diagonal_content': {
        'line_counts': {
            'above_diagonal': len(above_diag),
            'on_diagonal': len(on_diag),
            'below_diagonal': len(below_diag),
        },
        'section_composition': {
            'above': dict(above_sections),
            'on': dict(on_sections),
            'below': dict(below_sections),
        },
        'chi_squared': {
            'chi2': round(chi2_stat, 3),
            'p': round(chi2_p, 6),
            'dof': chi2_dof,
            'significant': bool(chi2_p < 0.05),
        },
        'vocabulary': {
            'above_vocab_size': len(above_vocab),
            'below_vocab_size': len(below_vocab),
            'on_vocab_size': len(on_vocab),
            'jaccard_above_below': round(jaccard_ab, 4),
            'above_unique_rate': round(above_unique_rate, 4),
            'below_unique_rate': round(below_unique_rate, 4),
        },
    },
    'part4_material_signature': {
        'slope_distribution': {
            'mean': round(float(np.mean(all_slopes)), 4) if all_slopes else None,
            'std': round(float(np.std(all_slopes)), 4) if all_slopes else None,
            'min': round(float(np.min(all_slopes)), 4) if all_slopes else None,
            'max': round(float(np.max(all_slopes)), 4) if all_slopes else None,
            'median': round(float(np.median(all_slopes)), 4) if all_slopes else None,
        },
        'slope_clustering': {
            'delta_bic': round(float(delta_bic), 1) if all_slopes else None,
            'cluster_evidence': cluster_evidence,
        },
        'r_squared_distribution': {
            'mean': round(float(np.mean(all_r_squared)), 4) if all_r_squared else None,
            'median': round(float(np.median(all_r_squared)), 4) if all_r_squared else None,
            'n_gt_010': n_r2_gt010,
            'pct_gt_010': round(pct_r2_gt010, 1) if all_r_squared else 0.0,
            'n_gt_025': n_r2_gt025 if all_r_squared else 0,
            'n_gt_050': n_r2_gt050 if all_r_squared else 0,
        },
    },
    'checks': {
        'check_1_kw_offsets_by_section': bool(check_1),
        'check_2_kw_slopes_by_section': bool(check_2),
        'check_3_chi2_above_vs_below': bool(check_3),
        'check_4_slope_variance_gt_015': bool(check_4),
        'check_5_pct_r2_gt_010_ge_30': bool(check_5),
        'n_passed': checks_passed,
    },
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / 'results' / '50_folio_coupling_analysis.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, cls=NpEncoder)
print(f"\nResult written to {out_path}")
