"""
19_azc_causal_vs_epiphenomenal.py

DECISIVE TEST: Is AZC causal or epiphenomenal?

If AZC is CAUSAL:
  - AZC overlap should predict B behavior BEYOND vocabulary composition
  - Model: B_escape ~ vocabulary + AZC_overlap should beat B_escape ~ vocabulary

If AZC is EPIPHENOMENAL:
  - Vocabulary composition fully explains B behavior
  - AZC overlap adds no predictive power once vocabulary is controlled

Method:
1. For each B folio, compute vocabulary features (PREFIX dist, kernel rates)
2. For each B folio, compute AZC overlap features
3. Build regression models:
   - Model 1: Vocabulary only
   - Model 2: Vocabulary + AZC overlap
4. Compare R² - does AZC add anything?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

print("="*70)
print("AZC CAUSAL VS EPIPHENOMENAL TEST")
print("="*70)

tx = Transcript()
morph = Morphology()

# =============================================================
# STEP 1: Build AZC vocabulary by position
# =============================================================
print("\nSTEP 1: Cataloging AZC vocabulary by position...")

def classify_position(placement):
    if not placement:
        return None
    p = placement.upper()
    if p.startswith('P'):
        return 'P'
    elif 'R3' in p or p.startswith('R3'):
        return 'R3'
    elif p.startswith('S'):
        return 'S'
    elif 'R1' in p or p.startswith('R1'):
        return 'R1'
    elif 'R2' in p or p.startswith('R2'):
        return 'R2'
    elif p.startswith('C'):
        return 'C'
    return 'OTHER'

# Collect AZC vocabulary
azc_vocab_by_pos = defaultdict(set)  # position -> set of MIDDLEs
azc_all_middles = set()

for t in tx.azc():
    try:
        m = morph.extract(t.word)
        if m.middle:
            pos = classify_position(t.placement)
            if pos and pos != 'OTHER':
                azc_vocab_by_pos[pos].add(m.middle)
                azc_all_middles.add(m.middle)
    except:
        pass

print(f"AZC MIDDLEs by position:")
for pos in ['P', 'C', 'R1', 'R2', 'R3', 'S']:
    print(f"  {pos}: {len(azc_vocab_by_pos[pos])}")

high_escape_azc = azc_vocab_by_pos['P']
low_escape_azc = azc_vocab_by_pos['R3'] | azc_vocab_by_pos['S']

print(f"\nHigh-escape AZC vocab (P): {len(high_escape_azc)}")
print(f"Low-escape AZC vocab (R3+S): {len(low_escape_azc)}")

# =============================================================
# STEP 2: Compute per-B-folio features
# =============================================================
print("\n" + "="*70)
print("STEP 2: Computing per-B-folio features...")

b_tokens = list(tx.currier_b())
b_folios = sorted(set(t.folio for t in b_tokens))
print(f"B folios: {len(b_folios)}")

# Group B tokens by folio
folio_tokens = defaultdict(list)
for t in b_tokens:
    folio_tokens[t.folio].append(t)

# Compute features for each folio
folio_features = {}

for folio in b_folios:
    tokens = folio_tokens[folio]

    # Extract morphology
    prefixes = []
    middles = []
    escape_count = 0
    kernel_k = 0
    kernel_h = 0
    kernel_e = 0

    for t in tokens:
        try:
            m = morph.extract(t.word)
            if m.prefix:
                prefixes.append(m.prefix)
            if m.middle:
                middles.append(m.middle)
                if 'k' in m.middle:
                    kernel_k += 1
                if 'h' in m.middle:
                    kernel_h += 1
                if 'e' in m.middle:
                    kernel_e += 1
            if m.prefix == 'qo':
                escape_count += 1
        except:
            pass

    n = len(tokens)
    n_mid = len(middles)

    # Vocabulary features
    prefix_counts = Counter(prefixes)
    qo_rate = prefix_counts.get('qo', 0) / n if n > 0 else 0
    ch_rate = prefix_counts.get('ch', 0) / n if n > 0 else 0
    ok_rate = prefix_counts.get('ok', 0) / n if n > 0 else 0

    k_rate = kernel_k / n_mid if n_mid > 0 else 0
    h_rate = kernel_h / n_mid if n_mid > 0 else 0
    e_rate = kernel_e / n_mid if n_mid > 0 else 0

    escape_rate = escape_count / n if n > 0 else 0

    # AZC overlap features
    middle_set = set(middles)
    azc_overlap = len(middle_set & azc_all_middles) / len(middle_set) if middle_set else 0
    high_escape_overlap = len(middle_set & high_escape_azc) / len(middle_set) if middle_set else 0
    low_escape_overlap = len(middle_set & low_escape_azc) / len(middle_set) if middle_set else 0

    folio_features[folio] = {
        'n_tokens': n,
        # Vocabulary features
        'qo_rate': qo_rate,
        'ch_rate': ch_rate,
        'ok_rate': ok_rate,
        'k_rate': k_rate,
        'h_rate': h_rate,
        'e_rate': e_rate,
        # Target variable
        'escape_rate': escape_rate,
        # AZC overlap features
        'azc_overlap': azc_overlap,
        'high_escape_azc_overlap': high_escape_overlap,
        'low_escape_azc_overlap': low_escape_overlap,
    }

# =============================================================
# STEP 3: Regression analysis
# =============================================================
print("\n" + "="*70)
print("STEP 3: Regression analysis...")

# Simple linear regression implementation
def mean(x):
    return sum(x) / len(x)

def variance(x):
    m = mean(x)
    return sum((xi - m)**2 for xi in x) / len(x)

def covariance(x, y):
    mx, my = mean(x), mean(y)
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / len(x)

def correlation(x, y):
    vx, vy = variance(x), variance(y)
    if vx == 0 or vy == 0:
        return 0
    return covariance(x, y) / (vx**0.5 * vy**0.5)

def r_squared(y_true, y_pred):
    ss_res = sum((yt - yp)**2 for yt, yp in zip(y_true, y_pred))
    ss_tot = sum((yt - mean(y_true))**2 for yt in y_true)
    return 1 - ss_res/ss_tot if ss_tot > 0 else 0

def simple_regression(x, y):
    """Returns slope, intercept, r_squared"""
    mx, my = mean(x), mean(y)
    cov = covariance(x, y)
    var_x = variance(x)
    if var_x == 0:
        return 0, my, 0
    slope = cov / var_x
    intercept = my - slope * mx
    y_pred = [slope * xi + intercept for xi in x]
    return slope, intercept, r_squared(y, y_pred)

# Prepare data
folios = list(folio_features.keys())
escape_rates = [folio_features[f]['escape_rate'] for f in folios]

# Model 1: Vocabulary features only (qo_rate as proxy for escape tendency)
qo_rates = [folio_features[f]['qo_rate'] for f in folios]
k_rates = [folio_features[f]['k_rate'] for f in folios]
h_rates = [folio_features[f]['h_rate'] for f in folios]

# Model 2: AZC overlap features
azc_overlaps = [folio_features[f]['azc_overlap'] for f in folios]
high_azc = [folio_features[f]['high_escape_azc_overlap'] for f in folios]
low_azc = [folio_features[f]['low_escape_azc_overlap'] for f in folios]

print("\n--- INDIVIDUAL PREDICTORS OF ESCAPE RATE ---")

# Vocabulary predictors
slope, intercept, r2 = simple_regression(qo_rates, escape_rates)
print(f"\nqo_rate (PREFIX):      R² = {r2:.4f}")

slope, intercept, r2 = simple_regression(k_rates, escape_rates)
print(f"k_rate (kernel k):     R² = {r2:.4f}")

slope, intercept, r2 = simple_regression(h_rates, escape_rates)
print(f"h_rate (kernel h):     R² = {r2:.4f}")

# AZC predictors
slope, intercept, r2 = simple_regression(azc_overlaps, escape_rates)
print(f"\nazc_overlap (all):     R² = {r2:.4f}")

slope, intercept, r2 = simple_regression(high_azc, escape_rates)
print(f"high_escape_azc (P):   R² = {r2:.4f}")

slope, intercept, r2 = simple_regression(low_azc, escape_rates)
print(f"low_escape_azc (R3+S): R² = {r2:.4f}")

# =============================================================
# STEP 4: The critical test - residual AZC effect
# =============================================================
print("\n" + "="*70)
print("STEP 4: CRITICAL TEST - Residual AZC effect")
print("="*70)

# If AZC is causal: after controlling for qo_rate, AZC should still predict escape
# If AZC is epiphenomenal: qo_rate fully explains, AZC adds nothing

# Compute residuals from qo_rate prediction
slope_qo, intercept_qo, r2_qo = simple_regression(qo_rates, escape_rates)
escape_predicted_by_qo = [slope_qo * qo + intercept_qo for qo in qo_rates]
escape_residuals = [actual - pred for actual, pred in zip(escape_rates, escape_predicted_by_qo)]

print(f"\nBaseline: qo_rate predicts escape_rate with R² = {r2_qo:.4f}")
print(f"Residual variance to explain: {1 - r2_qo:.4f}")

# Does AZC overlap predict the RESIDUALS?
slope_resid, intercept_resid, r2_resid_high = simple_regression(high_azc, escape_residuals)
print(f"\nHigh-escape AZC overlap predicts residuals: R² = {r2_resid_high:.4f}")

slope_resid, intercept_resid, r2_resid_low = simple_regression(low_azc, escape_residuals)
print(f"Low-escape AZC overlap predicts residuals:  R² = {r2_resid_low:.4f}")

# Combined: high - low as "AZC escape gradient"
azc_gradient = [h - l for h, l in zip(high_azc, low_azc)]
slope_grad, intercept_grad, r2_grad = simple_regression(azc_gradient, escape_residuals)
print(f"AZC gradient (high-low) predicts residuals: R² = {r2_grad:.4f}")

# =============================================================
# STEP 5: Correlation matrix
# =============================================================
print("\n" + "="*70)
print("STEP 5: Correlation matrix")
print("="*70)

print("\n         escape  qo_rate  k_rate  azc_all  azc_hi  azc_lo")
print(f"escape    1.000   {correlation(escape_rates, qo_rates):.3f}   {correlation(escape_rates, k_rates):.3f}    {correlation(escape_rates, azc_overlaps):.3f}   {correlation(escape_rates, high_azc):.3f}   {correlation(escape_rates, low_azc):.3f}")
print(f"qo_rate           1.000   {correlation(qo_rates, k_rates):.3f}    {correlation(qo_rates, azc_overlaps):.3f}   {correlation(qo_rates, high_azc):.3f}   {correlation(qo_rates, low_azc):.3f}")
print(f"azc_hi                            {correlation(high_azc, azc_overlaps):.3f}   1.000   {correlation(high_azc, low_azc):.3f}")

# =============================================================
# STEP 6: The killer test - same vocabulary, AZC position difference
# =============================================================
print("\n" + "="*70)
print("STEP 6: KILLER TEST - Same vocabulary different contexts")
print("="*70)

# Find MIDDLEs that appear in BOTH high and low escape AZC positions
shared_middles = high_escape_azc & low_escape_azc
only_high = high_escape_azc - low_escape_azc
only_low = low_escape_azc - high_escape_azc

print(f"\nMIDDLEs only in high-escape AZC (P): {len(only_high)}")
print(f"MIDDLEs only in low-escape AZC (R3/S): {len(only_low)}")
print(f"MIDDLEs in BOTH positions: {len(shared_middles)}")

# For B tokens with shared MIDDLEs, is there ANY signal from AZC position?
# Since the MIDDLE is the same, if AZC position matters, we'd need to see
# something ELSE differ (like PREFIX distribution)

print("\n--- Analyzing PREFIX distribution by MIDDLE source ---")

# Get B tokens and classify their MIDDLEs
only_high_tokens = []
only_low_tokens = []
shared_tokens = []

for t in b_tokens:
    try:
        m = morph.extract(t.word)
        if m.middle:
            if m.middle in only_high:
                only_high_tokens.append(t)
            elif m.middle in only_low:
                only_low_tokens.append(t)
            elif m.middle in shared_middles:
                shared_tokens.append(t)
    except:
        pass

def get_escape_rate(tokens):
    if not tokens:
        return 0, 0
    escape = sum(1 for t in tokens if t.word.startswith('qo'))
    return escape / len(tokens), len(tokens)

rate_high, n_high = get_escape_rate(only_high_tokens)
rate_low, n_low = get_escape_rate(only_low_tokens)
rate_shared, n_shared = get_escape_rate(shared_tokens)

print(f"\nB tokens with MIDDLEs from:")
print(f"  Only HIGH-escape AZC: {n_high:,} tokens, escape={rate_high:.4f}")
print(f"  Only LOW-escape AZC:  {n_low:,} tokens, escape={rate_low:.4f}")
print(f"  SHARED (both):        {n_shared:,} tokens, escape={rate_shared:.4f}")

# =============================================================
# STEP 7: VERDICT
# =============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

print(f"""
QUESTION: Does AZC add predictive power beyond vocabulary?

EVIDENCE:

1. Vocabulary (qo_rate) explains escape with R² = {r2_qo:.4f}
   This is the baseline - vocabulary composition predicts behavior.

2. AZC overlap predicts escape with R² = {r2_resid_high:.4f} for high-escape AZC
   (After controlling for vocabulary)

3. AZC gradient (high-low) predicts residuals with R² = {r2_grad:.4f}
   (Additional variance explained by AZC beyond vocabulary)

4. Same-MIDDLE different-AZC-source escape rates:
   - Only HIGH AZC: {rate_high:.4f}
   - Only LOW AZC:  {rate_low:.4f}
   - Difference: {abs(rate_high - rate_low):.4f}
""")

if r2_grad > 0.05:
    print("VERDICT: AZC appears to add predictive power beyond vocabulary.")
    print("         This suggests a CAUSAL role (or unmeasured vocabulary confound).")
elif r2_grad > 0.01:
    print("VERDICT: AZC adds marginal predictive power.")
    print("         Effect is small - could be causal or residual confounding.")
else:
    print("VERDICT: AZC adds NO predictive power beyond vocabulary.")
    print("         This suggests AZC is EPIPHENOMENAL - just vocabulary appearing")
    print("         in different places with consistent properties.")

# Additional check
if abs(rate_high - rate_low) > 0.10:
    print(f"\nCRITICAL: Tokens with only-HIGH vs only-LOW AZC MIDDLEs differ by {abs(rate_high-rate_low):.2%}")
    print("         This could be vocabulary effect OR AZC effect.")
    print("         Need to check if these MIDDLEs have different inherent properties.")
