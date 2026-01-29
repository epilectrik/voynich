"""
LINE_LEVEL_LANE_VALIDATION: Line-Level Two-Lane Model Validation

Tests whether the two-lane model (CHSH lane vs QO lane) operates at the
LINE level, not just as an emergent folio-level pattern.

Folio-level benchmarks:
  C603: CC composition predicts EN subfamily (rho=0.345-0.355)
  C605: Lane balance predicts escape density (rho=-0.506)

Six sections:
  1. CC->EN Immediate Routing (contingency table)
  2. Line-Level Composition (Spearman)
  3. Lane Coherence (permutation test)
  4. Line-Level Escape Prediction
  5. Position Interaction (directionality)
  6. Summary

Data dependencies:
  - class_token_map.json (CLASS_COSURVIVAL_TEST)
  - voynich.py (scripts/)
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
RESULTS = BASE / 'phases/LINE_LEVEL_LANE_VALIDATION/results'

# Sub-group definitions (from SUB_ROLE_INTERACTION)
EN_QO = {32, 33, 36, 44, 45, 46, 49}
EN_CHSH = {8, 31, 34, 35, 37, 39, 42, 43, 47, 48}
EN_MINOR = {41}
EN_CLASSES = EN_QO | EN_CHSH | EN_MINOR

CC_DAIIN = {10}
CC_OL = {11}
CC_OL_D = {17}
CC_CLASSES = CC_DAIIN | CC_OL | CC_OL_D

# Morphology for PREFIX extraction
morph = Morphology()
CORE_PREFIXES_QO = {'qo'}

def get_en_subfamily(cls):
    if cls in EN_QO: return 'QO'
    if cls in EN_CHSH: return 'CHSH'
    if cls in EN_MINOR: return 'MINOR'
    return None

def get_cc_subgroup(cls):
    if cls in CC_DAIIN: return 'CC_DAIIN'
    if cls in CC_OL: return 'CC_OL'
    if cls in CC_OL_D: return 'CC_OL_D'
    return None

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("LINE_LEVEL_LANE_VALIDATION")
print("=" * 70)

tx = Transcript()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}

# Build per-line token structures (ordered by position)
lines = defaultdict(list)
for token in tokens:
    word = token.word.strip()
    if not word:
        continue
    cls = token_to_class.get(word)
    m = morph.extract(word)
    lines[(token.folio, token.line)].append({
        'word': word,
        'class': cls,
        'en_subfamily': get_en_subfamily(cls),
        'cc_subgroup': get_cc_subgroup(cls),
        'prefix': m.prefix,
        'folio': token.folio,
        'section': token.section,
    })

# Verification
total_lines = len(lines)
total_tokens = sum(len(toks) for toks in lines.values())
en_total = sum(1 for toks in lines.values() for t in toks if t['en_subfamily'] is not None)
cc_total = sum(1 for toks in lines.values() for t in toks if t['cc_subgroup'] is not None)

lines_with_cc = sum(1 for toks in lines.values()
                    if any(t['cc_subgroup'] is not None for t in toks))
lines_with_en = sum(1 for toks in lines.values()
                    if any(t['en_subfamily'] in ('QO', 'CHSH') for t in toks))
lines_with_both = sum(1 for toks in lines.values()
                      if any(t['cc_subgroup'] is not None for t in toks)
                      and any(t['en_subfamily'] in ('QO', 'CHSH') for t in toks))

print(f"\nVerification:")
print(f"  Total B lines: {total_lines} (expected ~2420)")
print(f"  Total B tokens: {total_tokens}")
print(f"  EN tokens: {en_total} (expected ~7211)")
print(f"  CC tokens: {cc_total}")
print(f"  Lines with CC: {lines_with_cc} ({lines_with_cc/total_lines*100:.1f}%)")
print(f"  Lines with EN: {lines_with_en} ({lines_with_en/total_lines*100:.1f}%)")
print(f"  Lines with BOTH: {lines_with_both} (~743 expected)")
print(f"  Mean tokens/line: {total_tokens/total_lines:.2f}")

results = {
    'verification': {
        'total_lines': total_lines,
        'total_tokens': total_tokens,
        'en_total': en_total,
        'cc_total': cc_total,
        'lines_with_cc': lines_with_cc,
        'lines_with_en': lines_with_en,
        'lines_with_both': lines_with_both,
    }
}

# ============================================================
# SECTION 1: CC->EN IMMEDIATE ROUTING
# ============================================================
print("\n" + "=" * 70)
print("SECTION 1: CC->EN IMMEDIATE ROUTING")
print("=" * 70)

# For each CC token, find the FIRST EN token (QO or CHSH) appearing after it
# in the same line. Build contingency table: CC_type x next_EN_type.
contingency = Counter()  # (cc_subgroup, en_subfamily) -> count
distances = defaultdict(list)  # (cc_subgroup, en_subfamily) -> [distances]

for line_key, toks in lines.items():
    for i, t in enumerate(toks):
        if t['cc_subgroup'] is None:
            continue
        cc_type = t['cc_subgroup']
        # Find first EN after this CC
        for j in range(i + 1, len(toks)):
            en_sf = toks[j]['en_subfamily']
            if en_sf in ('QO', 'CHSH'):
                contingency[(cc_type, en_sf)] += 1
                distances[(cc_type, en_sf)].append(j - i)
                break

# Build 3x2 contingency table: CC_DAIIN, CC_OL, CC_OL_D x QO, CHSH
cc_types = ['CC_DAIIN', 'CC_OL', 'CC_OL_D']
en_types = ['QO', 'CHSH']
table = np.zeros((3, 2), dtype=int)

print(f"\nContingency: CC type -> FIRST subsequent EN subfamily")
print(f"{'CC type':>12} {'QO':>6} {'CHSH':>6} {'Total':>6} {'QO%':>7} {'CHSH%':>7}")
for i, cc in enumerate(cc_types):
    for j, en in enumerate(en_types):
        table[i, j] = contingency.get((cc, en), 0)
    total = table[i].sum()
    qo_pct = table[i, 0] / total * 100 if total > 0 else 0
    chsh_pct = table[i, 1] / total * 100 if total > 0 else 0
    print(f"{cc:>12} {table[i,0]:>6} {table[i,1]:>6} {total:>6} {qo_pct:>6.1f}% {chsh_pct:>6.1f}%")

total_all = table.sum()
print(f"{'Total':>12} {table[:,0].sum():>6} {table[:,1].sum():>6} {total_all:>6}")

# Chi-squared test
if table.min() >= 0 and table.sum() > 0:
    chi2, p_chi2, dof, expected = stats.chi2_contingency(table)
    min_dim = min(3, 2) - 1
    cramers_v = np.sqrt(chi2 / (total_all * min_dim))
    print(f"\nChi-squared: chi2={chi2:.2f}, df={dof}, p={p_chi2:.6f}")
    print(f"Cramer's V: {cramers_v:.3f}")
    print(f"CC type -> next EN subfamily: {'DEPENDENT (p<0.05)' if p_chi2 < 0.05 else 'INDEPENDENT'}")

    # Report expected vs observed for key cells
    print(f"\nExpected counts:")
    for i, cc in enumerate(cc_types):
        for j, en in enumerate(en_types):
            obs = table[i, j]
            exp = expected[i, j]
            ratio = obs / exp if exp > 0 else 0
            if abs(ratio - 1.0) > 0.1:
                print(f"  {cc}->{en}: observed={obs}, expected={exp:.1f}, ratio={ratio:.2f}")
else:
    chi2, p_chi2, cramers_v = None, None, None
    print("\nInsufficient data for chi-squared test")

# Mean distance analysis
print(f"\nMean token distance CC->first EN:")
for cc in cc_types:
    for en in en_types:
        d = distances.get((cc, en), [])
        if d:
            print(f"  {cc}->{en}: mean={np.mean(d):.2f}, median={np.median(d):.1f}, n={len(d)}")

results['section1_routing'] = {
    'contingency': {cc: {en: int(table[i, j]) for j, en in enumerate(en_types)}
                    for i, cc in enumerate(cc_types)},
    'total_pairs': int(total_all),
    'chi2': round(float(chi2), 4) if chi2 is not None else None,
    'p_value': float(p_chi2) if p_chi2 is not None else None,
    'dof': int(dof) if chi2 is not None else None,
    'cramers_v': round(float(cramers_v), 4) if cramers_v is not None else None,
    'significant': bool(p_chi2 < 0.05) if p_chi2 is not None else False,
    'mean_distances': {
        f"{cc}->{en}": round(float(np.mean(distances[(cc, en)])), 2)
        for cc in cc_types for en in en_types
        if distances.get((cc, en))
    },
}

# ============================================================
# SECTION 2: LINE-LEVEL COMPOSITION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: LINE-LEVEL COMPOSITION")
print("=" * 70)

# For lines with BOTH CC and EN: within-line CC_DAIIN_fraction vs EN_CHSH_proportion
line_cc_fractions = []
line_en_chsh_proportions = []

for line_key, toks in lines.items():
    # Count CC subtypes in this line
    cc_daiin = sum(1 for t in toks if t['cc_subgroup'] == 'CC_DAIIN')
    cc_ol = sum(1 for t in toks if t['cc_subgroup'] == 'CC_OL')
    cc_old = sum(1 for t in toks if t['cc_subgroup'] == 'CC_OL_D')
    cc_total_line = cc_daiin + cc_ol + cc_old
    if cc_total_line == 0:
        continue

    # Count EN subtypes in this line
    en_qo = sum(1 for t in toks if t['en_subfamily'] == 'QO')
    en_chsh = sum(1 for t in toks if t['en_subfamily'] == 'CHSH')
    en_total_line = en_qo + en_chsh
    if en_total_line == 0:
        continue

    cc_daiin_frac = cc_daiin / cc_total_line
    en_chsh_prop = en_chsh / en_total_line

    line_cc_fractions.append(cc_daiin_frac)
    line_en_chsh_proportions.append(en_chsh_prop)

print(f"\nLines with both CC and EN (QO/CHSH): {len(line_cc_fractions)}")

if len(line_cc_fractions) >= 20:
    rho_line_comp, p_line_comp = stats.spearmanr(line_cc_fractions, line_en_chsh_proportions)
    print(f"Spearman: CC_DAIIN_fraction ~ EN_CHSH_proportion")
    print(f"  rho={rho_line_comp:.4f}, p={p_line_comp:.6f}, n={len(line_cc_fractions)}")
    print(f"  Folio-level benchmark (C603): rho=0.345")
    if abs(rho_line_comp) > 0.345:
        print(f"  --> LINE-LEVEL EXCEEDS folio-level (delta={abs(rho_line_comp)-0.345:.3f})")
    elif abs(rho_line_comp) > 0.2:
        print(f"  --> LINE-LEVEL COMPARABLE to folio-level")
    elif abs(rho_line_comp) > 0.1:
        print(f"  --> LINE-LEVEL WEAKER than folio-level")
    else:
        print(f"  --> LINE-LEVEL NOT SIGNIFICANT or very weak")

    results['section2_composition'] = {
        'n_lines': len(line_cc_fractions),
        'rho': round(float(rho_line_comp), 4),
        'p_value': float(p_line_comp),
        'folio_benchmark': 0.345,
        'exceeds_folio': bool(abs(rho_line_comp) > 0.345),
    }
else:
    print("Insufficient lines for line-level composition test")
    results['section2_composition'] = {'n_lines': len(line_cc_fractions), 'verdict': 'insufficient'}

# Also test CC_OL_D fraction vs EN_QO proportion
line_cc_old_fracs = []
line_en_qo_props = []

for line_key, toks in lines.items():
    cc_daiin = sum(1 for t in toks if t['cc_subgroup'] == 'CC_DAIIN')
    cc_ol = sum(1 for t in toks if t['cc_subgroup'] == 'CC_OL')
    cc_old = sum(1 for t in toks if t['cc_subgroup'] == 'CC_OL_D')
    cc_total_line = cc_daiin + cc_ol + cc_old
    if cc_total_line == 0:
        continue

    en_qo = sum(1 for t in toks if t['en_subfamily'] == 'QO')
    en_chsh = sum(1 for t in toks if t['en_subfamily'] == 'CHSH')
    en_total_line = en_qo + en_chsh
    if en_total_line == 0:
        continue

    line_cc_old_fracs.append(cc_old / cc_total_line)
    line_en_qo_props.append(en_qo / en_total_line)

if len(line_cc_old_fracs) >= 20:
    rho_old_qo, p_old_qo = stats.spearmanr(line_cc_old_fracs, line_en_qo_props)
    print(f"\nSpearman: CC_OL_D_fraction ~ EN_QO_proportion")
    print(f"  rho={rho_old_qo:.4f}, p={p_old_qo:.6f}, n={len(line_cc_old_fracs)}")
    print(f"  Folio-level benchmark (C603): rho=0.355")

    results['section2_old_qo'] = {
        'rho': round(float(rho_old_qo), 4),
        'p_value': float(p_old_qo),
        'n': len(line_cc_old_fracs),
    }

# ============================================================
# SECTION 3: LANE COHERENCE
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: LANE COHERENCE")
print("=" * 70)

# For lines with >=5 EN tokens (QO or CHSH), compute dominant subfamily proportion
# Permutation test: shuffle subfamily labels within each line, 10,000 times
MIN_EN_FOR_COHERENCE = 5

coherence_lines = []  # list of (qo_count, chsh_count) per qualifying line
for line_key, toks in lines.items():
    en_qo = sum(1 for t in toks if t['en_subfamily'] == 'QO')
    en_chsh = sum(1 for t in toks if t['en_subfamily'] == 'CHSH')
    en_total_line = en_qo + en_chsh
    if en_total_line >= MIN_EN_FOR_COHERENCE:
        coherence_lines.append((en_qo, en_chsh))

print(f"\nLines with >={MIN_EN_FOR_COHERENCE} EN (QO/CHSH) tokens: {len(coherence_lines)}")

if len(coherence_lines) >= 50:
    # Observed dominant proportion per line
    observed_dominant = []
    for qo, chsh in coherence_lines:
        total = qo + chsh
        dominant = max(qo, chsh) / total
        observed_dominant.append(dominant)
    observed_mean = np.mean(observed_dominant)

    # Global base rates
    total_qo = sum(qo for qo, chsh in coherence_lines)
    total_chsh = sum(chsh for qo, chsh in coherence_lines)
    total_en_coh = total_qo + total_chsh
    base_chsh = total_chsh / total_en_coh

    print(f"  Global CHSH base rate (in qualifying lines): {base_chsh:.3f}")
    print(f"  Observed mean dominant proportion: {observed_mean:.4f}")

    # Permutation test
    N_PERMS = 10000
    rng = np.random.RandomState(42)
    perm_means = []

    for _ in range(N_PERMS):
        perm_dominant = []
        for qo, chsh in coherence_lines:
            total = qo + chsh
            # Random draw from binomial with global CHSH rate
            perm_chsh = rng.binomial(total, base_chsh)
            perm_qo = total - perm_chsh
            dominant = max(perm_qo, perm_chsh) / total
            perm_dominant.append(dominant)
        perm_means.append(np.mean(perm_dominant))

    perm_means = np.array(perm_means)
    p_coherence = np.mean(perm_means >= observed_mean)
    null_mean = np.mean(perm_means)
    null_std = np.std(perm_means)
    cohens_d = (observed_mean - null_mean) / null_std if null_std > 0 else 0

    print(f"  Null distribution: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"  p-value (one-sided): {p_coherence:.4f}")
    print(f"  Cohen's d: {cohens_d:.3f}")

    if p_coherence < 0.05:
        print(f"  --> LANE COHERENCE EXISTS: lines specialize above chance (p={p_coherence:.4f})")
    elif p_coherence < 0.10:
        print(f"  --> MARGINAL coherence (p={p_coherence:.4f})")
    else:
        print(f"  --> NO coherence: line specialization is chance-level (p={p_coherence:.4f})")

    # Distribution of observed dominant proportions
    print(f"\n  Dominant proportion distribution:")
    print(f"    Mean: {np.mean(observed_dominant):.4f}")
    print(f"    Std:  {np.std(observed_dominant):.4f}")
    print(f"    Min:  {np.min(observed_dominant):.4f}")
    print(f"    Max:  {np.max(observed_dominant):.4f}")

    # How many lines are "pure" (>= 80% one subfamily)?
    pure_count = sum(1 for d in observed_dominant if d >= 0.8)
    print(f"    Lines >= 80% dominant: {pure_count}/{len(coherence_lines)} ({pure_count/len(coherence_lines)*100:.1f}%)")

    results['section3_coherence'] = {
        'n_lines': len(coherence_lines),
        'min_en_threshold': MIN_EN_FOR_COHERENCE,
        'base_chsh_rate': round(float(base_chsh), 4),
        'observed_mean_dominant': round(float(observed_mean), 4),
        'null_mean': round(float(null_mean), 4),
        'null_std': round(float(null_std), 4),
        'p_value': round(float(p_coherence), 4),
        'cohens_d': round(float(cohens_d), 3),
        'significant': bool(p_coherence < 0.05),
        'pure_lines_80pct': pure_count,
    }
else:
    print("Insufficient qualifying lines for coherence test")
    results['section3_coherence'] = {'n_lines': len(coherence_lines), 'verdict': 'insufficient'}

# ============================================================
# SECTION 4: LINE-LEVEL ESCAPE PREDICTION
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: LINE-LEVEL ESCAPE PREDICTION")
print("=" * 70)

MIN_TOKENS_ESCAPE = 3

# For lines with EN tokens and >= MIN_TOKENS total
escape_en_chsh_props = []
escape_densities = []

for line_key, toks in lines.items():
    if len(toks) < MIN_TOKENS_ESCAPE:
        continue
    en_qo = sum(1 for t in toks if t['en_subfamily'] == 'QO')
    en_chsh = sum(1 for t in toks if t['en_subfamily'] == 'CHSH')
    en_total_line = en_qo + en_chsh
    if en_total_line == 0:
        continue

    # Escape density: qo-prefixed tokens / total
    qo_prefix_count = sum(1 for t in toks if t['prefix'] in CORE_PREFIXES_QO)
    escape_dens = qo_prefix_count / len(toks)

    escape_en_chsh_props.append(en_chsh / en_total_line)
    escape_densities.append(escape_dens)

print(f"\nLines with EN and >={MIN_TOKENS_ESCAPE} tokens: {len(escape_en_chsh_props)}")

if len(escape_en_chsh_props) >= 50:
    rho_esc_en, p_esc_en = stats.spearmanr(escape_en_chsh_props, escape_densities)
    print(f"\nSpearman: EN_CHSH_proportion ~ escape_density (line-level)")
    print(f"  rho={rho_esc_en:.4f}, p={p_esc_en:.6f}, n={len(escape_en_chsh_props)}")
    print(f"  Folio-level benchmark (C412): rho=-0.304")
    if rho_esc_en < -0.1 and p_esc_en < 0.05:
        print(f"  --> LINE-LEVEL CONFIRMS: higher CHSH = lower escape")
    else:
        print(f"  --> Line-level does not confirm folio-level pattern")

    results['section4_escape_en'] = {
        'n_lines': len(escape_en_chsh_props),
        'rho': round(float(rho_esc_en), 4),
        'p_value': float(p_esc_en),
        'folio_benchmark': -0.304,
    }

# Lane balance at line level (lines with both CC and EN)
lane_balances_line = []
escape_densities_lane = []

for line_key, toks in lines.items():
    if len(toks) < MIN_TOKENS_ESCAPE:
        continue

    cc_daiin = sum(1 for t in toks if t['cc_subgroup'] == 'CC_DAIIN')
    cc_ol = sum(1 for t in toks if t['cc_subgroup'] == 'CC_OL')
    cc_old = sum(1 for t in toks if t['cc_subgroup'] == 'CC_OL_D')
    cc_total_line = cc_daiin + cc_ol + cc_old
    if cc_total_line == 0:
        continue

    en_qo = sum(1 for t in toks if t['en_subfamily'] == 'QO')
    en_chsh = sum(1 for t in toks if t['en_subfamily'] == 'CHSH')
    en_total_line = en_qo + en_chsh
    if en_total_line == 0:
        continue

    cc_daiin_frac = cc_daiin / cc_total_line
    cc_old_frac = cc_old / cc_total_line
    en_chsh_prop = en_chsh / en_total_line
    en_qo_prop = en_qo / en_total_line

    chsh_lane_int = en_chsh_prop * cc_daiin_frac
    qo_lane_int = en_qo_prop * cc_old_frac
    total_lane = chsh_lane_int + qo_lane_int

    if total_lane == 0:
        continue

    lb = chsh_lane_int / total_lane

    qo_prefix_count = sum(1 for t in toks if t['prefix'] in CORE_PREFIXES_QO)
    escape_dens = qo_prefix_count / len(toks)

    lane_balances_line.append(lb)
    escape_densities_lane.append(escape_dens)

print(f"\nLines with lane balance computable: {len(lane_balances_line)}")

if len(lane_balances_line) >= 50:
    rho_lane_esc, p_lane_esc = stats.spearmanr(lane_balances_line, escape_densities_lane)
    print(f"\nSpearman: lane_balance ~ escape_density (line-level)")
    print(f"  rho={rho_lane_esc:.4f}, p={p_lane_esc:.6f}, n={len(lane_balances_line)}")
    print(f"  Folio-level benchmark (C605): rho=-0.506")
    if rho_lane_esc < -0.1 and p_lane_esc < 0.05:
        print(f"  --> LANE BALANCE PREDICTS ESCAPE at line level")
    else:
        print(f"  --> Lane balance does NOT predict escape at line level")

    results['section4_lane_escape'] = {
        'n_lines': len(lane_balances_line),
        'rho': round(float(rho_lane_esc), 4),
        'p_value': float(p_lane_esc),
        'folio_benchmark': -0.506,
    }
else:
    print("Insufficient lines for lane balance escape test")
    results['section4_lane_escape'] = {'n_lines': len(lane_balances_line), 'verdict': 'insufficient'}

# ============================================================
# SECTION 5: POSITION INTERACTION (DIRECTIONALITY)
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: POSITION INTERACTION (DIRECTIONALITY)")
print("=" * 70)

# Split each qualifying line at midpoint
# Forward: first-half CC composition -> second-half EN composition
# Reverse: second-half CC composition -> first-half EN composition

forward_cc = []  # first-half CC_DAIIN fraction
forward_en = []  # second-half EN_CHSH proportion
reverse_cc = []  # second-half CC_DAIIN fraction
reverse_en = []  # first-half EN_CHSH proportion

for line_key, toks in lines.items():
    n = len(toks)
    if n < 4:  # need at least 4 tokens to split meaningfully
        continue

    mid = n // 2
    first_half = toks[:mid]
    second_half = toks[mid:]

    # First-half CC
    fh_cc_daiin = sum(1 for t in first_half if t['cc_subgroup'] == 'CC_DAIIN')
    fh_cc_ol = sum(1 for t in first_half if t['cc_subgroup'] == 'CC_OL')
    fh_cc_old = sum(1 for t in first_half if t['cc_subgroup'] == 'CC_OL_D')
    fh_cc_total = fh_cc_daiin + fh_cc_ol + fh_cc_old

    # Second-half CC
    sh_cc_daiin = sum(1 for t in second_half if t['cc_subgroup'] == 'CC_DAIIN')
    sh_cc_ol = sum(1 for t in second_half if t['cc_subgroup'] == 'CC_OL')
    sh_cc_old = sum(1 for t in second_half if t['cc_subgroup'] == 'CC_OL_D')
    sh_cc_total = sh_cc_daiin + sh_cc_ol + sh_cc_old

    # First-half EN
    fh_en_qo = sum(1 for t in first_half if t['en_subfamily'] == 'QO')
    fh_en_chsh = sum(1 for t in first_half if t['en_subfamily'] == 'CHSH')
    fh_en_total = fh_en_qo + fh_en_chsh

    # Second-half EN
    sh_en_qo = sum(1 for t in second_half if t['en_subfamily'] == 'QO')
    sh_en_chsh = sum(1 for t in second_half if t['en_subfamily'] == 'CHSH')
    sh_en_total = sh_en_qo + sh_en_chsh

    # Forward: first-half CC -> second-half EN
    if fh_cc_total > 0 and sh_en_total > 0:
        forward_cc.append(fh_cc_daiin / fh_cc_total)
        forward_en.append(sh_en_chsh / sh_en_total)

    # Reverse: second-half CC -> first-half EN
    if sh_cc_total > 0 and fh_en_total > 0:
        reverse_cc.append(sh_cc_daiin / sh_cc_total)
        reverse_en.append(fh_en_chsh / fh_en_total)

print(f"\nForward pairs (first-half CC -> second-half EN): {len(forward_cc)}")
print(f"Reverse pairs (second-half CC -> first-half EN): {len(reverse_cc)}")

forward_rho, forward_p = None, None
reverse_rho, reverse_p = None, None

if len(forward_cc) >= 30:
    forward_rho, forward_p = stats.spearmanr(forward_cc, forward_en)
    print(f"\nForward: first_half_CC_DAIIN_frac ~ second_half_EN_CHSH_prop")
    print(f"  rho={forward_rho:.4f}, p={forward_p:.6f}")

if len(reverse_cc) >= 30:
    reverse_rho, reverse_p = stats.spearmanr(reverse_cc, reverse_en)
    print(f"\nReverse: second_half_CC_DAIIN_frac ~ first_half_EN_CHSH_prop")
    print(f"  rho={reverse_rho:.4f}, p={reverse_p:.6f}")

if forward_rho is not None and reverse_rho is not None:
    diff = forward_rho - reverse_rho
    print(f"\nDirectionality: forward - reverse = {diff:.4f}")

    # Bootstrap CI for the difference
    N_BOOT = 5000
    rng = np.random.RandomState(42)
    boot_diffs = []

    # We need paired data for bootstrap, use the overlap of lines
    # For simplicity, bootstrap both independently
    for _ in range(N_BOOT):
        # Resample forward
        idx_f = rng.choice(len(forward_cc), size=len(forward_cc), replace=True)
        fcc = [forward_cc[i] for i in idx_f]
        fen = [forward_en[i] for i in idx_f]
        r_f, _ = stats.spearmanr(fcc, fen)

        # Resample reverse
        idx_r = rng.choice(len(reverse_cc), size=len(reverse_cc), replace=True)
        rcc = [reverse_cc[i] for i in idx_r]
        ren = [reverse_en[i] for i in idx_r]
        r_r, _ = stats.spearmanr(rcc, ren)

        boot_diffs.append(r_f - r_r)

    boot_diffs = np.array(boot_diffs)
    ci_lo = np.percentile(boot_diffs, 2.5)
    ci_hi = np.percentile(boot_diffs, 97.5)

    print(f"  Bootstrap 95% CI for difference: [{ci_lo:.4f}, {ci_hi:.4f}]")

    if ci_lo > 0:
        print(f"  --> FORWARD EXCEEDS REVERSE: evidence for left-to-right causal routing")
    elif ci_hi < 0:
        print(f"  --> REVERSE EXCEEDS FORWARD: unexpected reverse causation")
    else:
        print(f"  --> CI INCLUDES ZERO: no directional asymmetry (shared line identity)")

    results['section5_directionality'] = {
        'forward': {
            'n': len(forward_cc),
            'rho': round(float(forward_rho), 4),
            'p': float(forward_p),
        },
        'reverse': {
            'n': len(reverse_cc),
            'rho': round(float(reverse_rho), 4),
            'p': float(reverse_p),
        },
        'difference': round(float(diff), 4),
        'bootstrap_ci_95': [round(float(ci_lo), 4), round(float(ci_hi), 4)],
        'forward_exceeds': bool(ci_lo > 0),
    }
else:
    print("Insufficient data for directionality test")
    results['section5_directionality'] = {'verdict': 'insufficient'}

# ============================================================
# SECTION 6: SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: SUMMARY")
print("=" * 70)

print(f"\n{'Test':>40} {'Line-level':>12} {'Folio-level':>12} {'Verdict':>15}")
print("-" * 82)

# 1. CC->EN routing
s1 = results.get('section1_routing', {})
if s1.get('chi2') is not None:
    print(f"{'CC->EN routing (Cramers V)':>40} {s1['cramers_v']:>12.3f} {'C603 rho=0.35':>12} {'CONFIRMED' if s1['significant'] else 'NOT SIG':>15}")
else:
    print(f"{'CC->EN routing':>40} {'N/A':>12} {'C603 rho=0.35':>12}")

# 2. CC composition -> EN composition
s2 = results.get('section2_composition', {})
if 'rho' in s2:
    sig = 'CONFIRMED' if s2['p_value'] < 0.05 else 'NOT SIG'
    print(f"{'CC comp -> EN comp (rho)':>40} {s2['rho']:>12.3f} {'C603 rho=0.35':>12} {sig:>15}")

# 3. Lane coherence
s3 = results.get('section3_coherence', {})
if 'p_value' in s3:
    sig = 'CONFIRMED' if s3['significant'] else 'NOT SIG'
    print(f"{'Lane coherence (Cohens d)':>40} {s3['cohens_d']:>12.3f} {'New test':>12} {sig:>15}")

# 4. EN -> escape (line level)
s4a = results.get('section4_escape_en', {})
if 'rho' in s4a:
    sig = 'CONFIRMED' if s4a['p_value'] < 0.05 and s4a['rho'] < -0.1 else 'NOT SIG'
    print(f"{'EN_CHSH -> escape (rho)':>40} {s4a['rho']:>12.3f} {'C412 rho=-0.30':>12} {sig:>15}")

# 4b. Lane balance -> escape (line level)
s4b = results.get('section4_lane_escape', {})
if 'rho' in s4b:
    sig = 'CONFIRMED' if s4b['p_value'] < 0.05 and s4b['rho'] < -0.1 else 'NOT SIG'
    print(f"{'Lane balance -> escape (rho)':>40} {s4b['rho']:>12.3f} {'C605 rho=-0.51':>12} {sig:>15}")

# 5. Directionality
s5 = results.get('section5_directionality', {})
if 'difference' in s5:
    dir_verdict = 'CAUSAL' if s5.get('forward_exceeds') else 'SHARED ID'
    print(f"{'Directionality (fwd-rev)':>40} {s5['difference']:>12.3f} {'New test':>12} {dir_verdict:>15}")

# Overall verdict
print(f"\n--- OVERALL VERDICT ---")
confirmed = 0
total_tests = 0

if s1.get('significant'):
    confirmed += 1
total_tests += 1 if s1.get('chi2') is not None else 0

if s2.get('p_value') is not None and s2['p_value'] < 0.05:
    confirmed += 1
total_tests += 1 if s2.get('rho') is not None else 0

if s3.get('significant'):
    confirmed += 1
total_tests += 1 if s3.get('p_value') is not None else 0

if s4a.get('p_value') is not None and s4a['p_value'] < 0.05 and s4a.get('rho', 0) < -0.1:
    confirmed += 1
total_tests += 1 if s4a.get('rho') is not None else 0

if s4b.get('p_value') is not None and s4b['p_value'] < 0.05 and s4b.get('rho', 0) < -0.1:
    confirmed += 1
total_tests += 1 if s4b.get('rho') is not None else 0

print(f"\nTests confirmed: {confirmed}/{total_tests}")

if confirmed >= 4:
    verdict = "GRAMMAR-LEVEL: Two-lane model operates at line level"
elif confirmed >= 2:
    verdict = "PARTIAL: Some line-level signal, weaker than folio-level"
elif confirmed >= 1:
    verdict = "WEAK: Minimal line-level evidence"
else:
    verdict = "FOLIO-ONLY: Two-lane model is emergent, not grammar-level"

print(f"Verdict: {verdict}")

results['summary'] = {
    'confirmed': confirmed,
    'total_tests': total_tests,
    'verdict': verdict,
}

# ============================================================
# SAVE
# ============================================================
RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'line_lane_validation.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to {RESULTS / 'line_lane_validation.json'}")
