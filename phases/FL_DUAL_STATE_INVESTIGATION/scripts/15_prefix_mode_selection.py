"""
15_prefix_mode_selection.py

Does PREFIX select LOW vs HIGH mode? Specifically:
- Does qo correlate with one mode?
- Do ch/sh correlate with the other?
- Is there a clean PREFIX -> mode mapping?
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency

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

MIN_N = 50
tx = Transcript()
morph = Morphology()

# Collect tokens by line
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

# Build FL records with prefix
fl_records = []
per_middle_positions = defaultdict(list)
for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n <= 1:
        continue
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        if m and m.middle and m.middle in FL_STAGE_MAP:
            pos = idx / (n - 1)
            per_middle_positions[m.middle].append(pos)
            fl_records.append({
                'word': t.word,
                'middle': m.middle,
                'prefix': m.prefix if m.prefix else 'NONE',
                'suffix': m.suffix if m.suffix else 'NONE',
                'actual_pos': pos,
            })

# Fit GMMs and assign modes
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

for r in fl_records:
    if r['middle'] in gmm_models:
        info = gmm_models[r['middle']]
        pred = info['model'].predict(np.array([[r['actual_pos']]]))[0]
        if info['swap']:
            pred = 1 - pred
        r['mode'] = 'LOW' if pred == 0 else 'HIGH'
    else:
        r['mode'] = 'UNKNOWN'

assigned = [r for r in fl_records if r['mode'] != 'UNKNOWN']
print(f"Mode-assigned FL tokens: {len(assigned)}")

# ============================================================
# PREFIX -> mode distribution
# ============================================================
print(f"\n{'='*60}")
print("PREFIX -> MODE DISTRIBUTION")
print(f"{'PREFIX':>8} {'LOW':>6} {'HIGH':>6} {'Total':>6} {'LOW%':>7} {'HIGH%':>7}  {'Bias':>10}")
print("-" * 65)

prefix_mode = defaultdict(Counter)
for r in assigned:
    prefix_mode[r['prefix']][r['mode']] += 1

# Sort by total count
sorted_prefixes = sorted(prefix_mode.keys(), key=lambda p: -sum(prefix_mode[p].values()))

prefix_results = {}
for pfx in sorted_prefixes:
    counts = prefix_mode[pfx]
    low = counts.get('LOW', 0)
    high = counts.get('HIGH', 0)
    total = low + high
    if total < 10:
        continue
    low_pct = low / total * 100
    high_pct = high / total * 100

    if low_pct > 65:
        bias = "STRONG-LOW"
    elif low_pct > 55:
        bias = "lean-LOW"
    elif high_pct > 65:
        bias = "STRONG-HIGH"
    elif high_pct > 55:
        bias = "lean-HIGH"
    else:
        bias = "balanced"

    prefix_results[pfx] = {
        'low': low, 'high': high, 'total': total,
        'low_pct': round(low_pct, 1), 'high_pct': round(high_pct, 1),
        'bias': bias,
    }
    print(f"{pfx:>8} {low:>6} {high:>6} {total:>6} {low_pct:>6.1f}% {high_pct:>6.1f}%  [{bias}]")

# ============================================================
# Group prefixes by family
# ============================================================
print(f"\n{'='*60}")
print("PREFIX FAMILIES")

families = {
    'qo': ['qo'],
    'ch': ['ch'],
    'sh': ['sh'],
    'da': ['da'],
    'ok/ot/ol': ['ok', 'ot', 'ol'],
    'Xo (ko,so,to,do,po)': ['ko', 'so', 'to', 'do', 'po'],
    'Xa (ka,sa,ta)': ['ka', 'sa', 'ta'],
    'Xch (pch,tch,kch,lch,dch,fch,rch,sch)': ['pch', 'tch', 'kch', 'lch', 'dch', 'fch', 'rch', 'sch'],
    'Xe (ke,te)': ['ke', 'te'],
    'Xk (lk,yk)': ['lk', 'yk'],
    'NONE': ['NONE'],
    'Xr/Xl (ar,al,or)': ['ar', 'al', 'or'],
}

family_results = {}
for family_name, members in families.items():
    low_total = sum(prefix_mode[p].get('LOW', 0) for p in members)
    high_total = sum(prefix_mode[p].get('HIGH', 0) for p in members)
    total = low_total + high_total
    if total < 10:
        continue
    low_pct = low_total / total * 100

    if low_pct > 65:
        bias = "STRONG-LOW"
    elif low_pct > 55:
        bias = "lean-LOW"
    elif low_pct < 35:
        bias = "STRONG-HIGH"
    elif low_pct < 45:
        bias = "lean-HIGH"
    else:
        bias = "balanced"

    family_results[family_name] = {
        'low': low_total, 'high': high_total, 'total': total,
        'low_pct': round(low_pct, 1), 'bias': bias,
    }
    print(f"  {family_name:>35}: LOW={low_total:>4} HIGH={high_total:>4} "
          f"({low_pct:.1f}% LOW) [{bias}]")

# ============================================================
# Chi-squared: PREFIX x MODE contingency
# ============================================================
print(f"\n{'='*60}")
print("CHI-SQUARED: PREFIX x MODE")

# Build contingency table for prefixes with n >= 30
valid_prefixes = [p for p in sorted_prefixes if sum(prefix_mode[p].values()) >= 30]
if len(valid_prefixes) >= 2:
    table = np.array([[prefix_mode[p].get('LOW', 0), prefix_mode[p].get('HIGH', 0)]
                       for p in valid_prefixes])
    chi2, p_val, dof, expected = chi2_contingency(table)
    cramers_v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
    print(f"  chi2={chi2:.1f}, p={p_val:.2e}, dof={dof}, Cramer's V={cramers_v:.3f}")
    print(f"  Prefixes in test: {len(valid_prefixes)}")

# ============================================================
# Per-MIDDLE: does prefix -> mode hold within each MIDDLE?
# ============================================================
print(f"\n{'='*60}")
print("PER-MIDDLE PREFIX -> MODE (key prefixes: qo, ch, sh, da, NONE)")

key_prefixes = ['qo', 'ch', 'sh', 'da', 'NONE', 'ok', 'ot']
per_middle_prefix_mode = {}

for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    if mid not in gmm_models:
        continue
    mid_records = [r for r in assigned if r['middle'] == mid]
    if len(mid_records) < 50:
        continue

    pfx_modes = {}
    for pfx in key_prefixes:
        low = sum(1 for r in mid_records if r['prefix'] == pfx and r['mode'] == 'LOW')
        high = sum(1 for r in mid_records if r['prefix'] == pfx and r['mode'] == 'HIGH')
        total = low + high
        if total >= 5:
            pfx_modes[pfx] = {
                'low': low, 'high': high, 'total': total,
                'low_pct': round(low / total * 100, 1),
            }

    per_middle_prefix_mode[mid] = pfx_modes

    # Print compact summary
    parts = []
    for pfx in key_prefixes:
        if pfx in pfx_modes:
            d = pfx_modes[pfx]
            parts.append(f"{pfx}:{d['low_pct']:.0f}%L")
    if parts:
        stage = FL_STAGE_MAP[mid][0]
        print(f"  {mid:>4} ({stage:>10}): {', '.join(parts)}")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")

# Check specific hypotheses
qo_data = prefix_results.get('qo', {})
ch_data = prefix_results.get('ch', {})
sh_data = prefix_results.get('sh', {})
da_data = prefix_results.get('da', {})
none_data = prefix_results.get('NONE', {})

qo_low_pct = qo_data.get('low_pct', 50)
ch_low_pct = ch_data.get('low_pct', 50)
sh_low_pct = sh_data.get('low_pct', 50)

print(f"KEY FINDINGS:")
print(f"  qo:   {qo_low_pct:.1f}% LOW — {'LOW-biased' if qo_low_pct > 55 else 'HIGH-biased' if qo_low_pct < 45 else 'balanced'}")
print(f"  ch:   {ch_low_pct:.1f}% LOW — {'LOW-biased' if ch_low_pct > 55 else 'HIGH-biased' if ch_low_pct < 45 else 'balanced'}")
print(f"  sh:   {sh_low_pct:.1f}% LOW — {'LOW-biased' if sh_low_pct > 55 else 'HIGH-biased' if sh_low_pct < 45 else 'balanced'}")

# Overall assessment
strong_low = [p for p, d in prefix_results.items() if d['bias'] == 'STRONG-LOW']
strong_high = [p for p, d in prefix_results.items() if d['bias'] == 'STRONG-HIGH']

if len(strong_low) >= 3 and len(strong_high) >= 3:
    verdict = "PREFIX_DETERMINES_MODE"
    explanation = (f"Clear PREFIX->mode mapping. "
                   f"LOW-biased: {strong_low}. HIGH-biased: {strong_high}.")
elif len(strong_low) >= 2 or len(strong_high) >= 2:
    verdict = "PARTIAL_PREFIX_MODE_SELECTION"
    explanation = (f"Some prefixes strongly select mode. "
                   f"LOW-biased: {strong_low}. HIGH-biased: {strong_high}.")
else:
    verdict = "WEAK_PREFIX_MODE_LINK"
    explanation = "No strong PREFIX->mode mapping"

print(f"\nVERDICT: {verdict}")
print(f"  {explanation}")

result = {
    'total_assigned': len(assigned),
    'prefix_mode_distribution': prefix_results,
    'prefix_family_results': family_results,
    'chi_squared': {
        'chi2': round(float(chi2), 1),
        'p': float(p_val),
        'dof': int(dof),
        'cramers_v': round(float(cramers_v), 3),
    },
    'per_middle_prefix_mode': per_middle_prefix_mode,
    'strong_low_prefixes': strong_low,
    'strong_high_prefixes': strong_high,
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "15_prefix_mode_selection.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
