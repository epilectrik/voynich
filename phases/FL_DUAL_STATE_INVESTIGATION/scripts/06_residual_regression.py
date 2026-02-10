"""
06_residual_regression.py

Residual regression: after removing known confounds, how much FL position
variance remains — and is it bimodal?

Q: After removing confounds (line length, section, preceding role),
how much FL position variance remains?
- Linear regression: actual_pos ~ expected_pos + line_length + section + preceding_role
- Compute R-squared and residual distribution
- Test if residuals are bimodal (kurtosis)
- Pass (confounds): R-squared > 0.30, residuals unimodal
- Fail (unexplained): R-squared < 0.15, residuals bimodal
"""
import sys
import json
import statistics
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import kurtosis
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

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

tx = Transcript()
morph = Morphology()

# Load role map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build regression dataset
rows = []
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            stage, expected = FL_STAGE_MAP[m.middle]
            prev_role = token_to_role.get(tokens[idx - 1].word, 'UNKNOWN') if idx > 0 else 'LINE_START'

            rows.append({
                'actual_pos': idx / (n - 1),
                'expected_pos': expected,
                'line_length': n,
                'section': t.section,
                'prev_role': prev_role,
                'middle': m.middle,
            })

print(f"Regression dataset: {len(rows)} FL tokens")

# ============================================================
# Build feature matrix
# ============================================================
# Encode categoricals
sections = sorted(set(r['section'] for r in rows))
roles = sorted(set(r['prev_role'] for r in rows))

section_enc = {s: i for i, s in enumerate(sections)}
role_enc = {r: i for i, r in enumerate(roles)}

y = np.array([r['actual_pos'] for r in rows])
n_samples = len(rows)

# Features: expected_pos, line_length, section (one-hot), prev_role (one-hot)
n_section = len(sections)
n_role = len(roles)

X = np.zeros((n_samples, 2 + n_section + n_role))
for i, r in enumerate(rows):
    X[i, 0] = r['expected_pos']
    X[i, 1] = r['line_length']
    X[i, 2 + section_enc[r['section']]] = 1.0
    X[i, 2 + n_section + role_enc[r['prev_role']]] = 1.0

# ============================================================
# Model 1: expected_pos only
# ============================================================
X_exp = X[:, 0:1]
reg1 = LinearRegression().fit(X_exp, y)
r2_expected_only = reg1.score(X_exp, y)
resid1 = y - reg1.predict(X_exp)

print(f"\nModel 1 (expected_pos only):")
print(f"  R-squared: {r2_expected_only:.4f}")
print(f"  Residual std: {np.std(resid1):.4f}")
print(f"  Residual kurtosis: {kurtosis(resid1):.4f}")

# ============================================================
# Model 2: expected_pos + line_length
# ============================================================
X_exp_len = X[:, 0:2]
reg2 = LinearRegression().fit(X_exp_len, y)
r2_exp_len = reg2.score(X_exp_len, y)
resid2 = y - reg2.predict(X_exp_len)

print(f"\nModel 2 (expected_pos + line_length):")
print(f"  R-squared: {r2_exp_len:.4f}")
print(f"  Residual std: {np.std(resid2):.4f}")
print(f"  Residual kurtosis: {kurtosis(resid2):.4f}")

# ============================================================
# Model 3: full model
# ============================================================
reg3 = LinearRegression().fit(X, y)
r2_full = reg3.score(X, y)
resid3 = y - reg3.predict(X)

print(f"\nModel 3 (full: expected_pos + line_length + section + prev_role):")
print(f"  R-squared: {r2_full:.4f}")
print(f"  Residual std: {np.std(resid3):.4f}")
print(f"  Residual kurtosis: {kurtosis(resid3):.4f}")

# Feature importance (coefficients)
feature_names = ['expected_pos', 'line_length'] + \
                [f'section_{s}' for s in sections] + \
                [f'role_{r}' for r in roles]
coefs = reg3.coef_

print(f"\n  Top features by |coefficient|:")
sorted_feats = sorted(zip(feature_names, coefs), key=lambda x: abs(x[1]), reverse=True)
for name, coef in sorted_feats[:10]:
    print(f"    {name:>30}: {coef:>+8.4f}")

# ============================================================
# Residual distribution analysis
# ============================================================
print(f"\n{'='*60}")
print("RESIDUAL DISTRIBUTION (full model)")

residuals = resid3
resid_mean = float(np.mean(residuals))
resid_std = float(np.std(residuals))
resid_kurt = float(kurtosis(residuals))

# Split above/below median to check for bimodality
median_resid = float(np.median(residuals))
below = residuals[residuals < median_resid]
above = residuals[residuals >= median_resid]

# Per-MIDDLE residuals
print(f"\nPer-MIDDLE residual analysis:")
mid_resid_kurt = {}
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    mid_idx = [i for i, r in enumerate(rows) if r['middle'] == mid]
    if len(mid_idx) < 20:
        continue
    mid_resid = residuals[mid_idx]
    mk = float(kurtosis(mid_resid))
    mid_resid_kurt[mid] = {
        'n': len(mid_idx),
        'resid_mean': round(float(np.mean(mid_resid)), 4),
        'resid_std': round(float(np.std(mid_resid)), 4),
        'resid_kurtosis': round(mk, 3),
    }
    label = "BIMODAL" if mk < -0.5 else "FLAT" if mk < 0 else "PEAKED"
    print(f"  {mid:>4}: n={len(mid_idx):>4} resid_std={np.std(mid_resid):.3f} "
          f"resid_kurt={mk:>7.3f} [{label}]")

bimodal_after_regression = sum(1 for v in mid_resid_kurt.values() if v['resid_kurtosis'] < -0.5)
total_tested = len(mid_resid_kurt)

# ============================================================
# Verdict
# ============================================================
if r2_full > 0.30 and resid_kurt > -0.5:
    verdict = "CONFOUNDS_EXPLAIN"
    explanation = (f"Full model R²={r2_full:.3f} > 0.30 and residual kurtosis={resid_kurt:.3f} "
                   f"is not bimodal. Confounds explain FL position spread.")
elif r2_full < 0.15 and resid_kurt < -0.5:
    verdict = "UNEXPLAINED_BIMODAL"
    explanation = (f"Full model R²={r2_full:.3f} < 0.15 and residual kurtosis={resid_kurt:.3f} "
                   f"is bimodal. Genuine dual-state signal.")
else:
    verdict = "PARTIAL"
    explanation = (f"Full model R²={r2_full:.3f}, residual kurtosis={resid_kurt:.3f}. "
                   f"{bimodal_after_regression}/{total_tested} MIDDLEs remain bimodal after regression.")

print(f"\n{'='*60}")
print(f"VERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'n_samples': len(rows),
    'model_1_expected_only': {
        'r_squared': round(r2_expected_only, 4),
        'resid_std': round(float(np.std(resid1)), 4),
        'resid_kurtosis': round(float(kurtosis(resid1)), 3),
    },
    'model_2_expected_length': {
        'r_squared': round(r2_exp_len, 4),
        'resid_std': round(float(np.std(resid2)), 4),
        'resid_kurtosis': round(float(kurtosis(resid2)), 3),
    },
    'model_3_full': {
        'r_squared': round(r2_full, 4),
        'resid_std': round(float(np.std(resid3)), 4),
        'resid_kurtosis': round(float(kurtosis(resid3)), 3),
        'top_features': [(name, round(float(coef), 4)) for name, coef in sorted_feats[:10]],
    },
    'per_middle_residuals': mid_resid_kurt,
    'bimodal_after_regression': bimodal_after_regression,
    'total_middles_tested': total_tested,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "06_residual_regression.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
