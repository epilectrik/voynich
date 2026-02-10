"""
FL RESOLUTION TEST 4: Negative Control (Role Independence Reconfirmation)

Confirm: Chi2(FL stage x role) = NS, V < 0.05
If unexpectedly significant: STOP - model violation.
"""
import sys, json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import chi2_contingency

sys.path.insert(0, str(Path('C:/git/voynich').resolve()))
from scripts.voynich import Transcript, Morphology

FL_STAGE_MAP = {
    'ii': 0, 'i': 0, 'in': 1, 'r': 2, 'ar': 2,
    'al': 3, 'l': 3, 'ol': 3, 'o': 4, 'ly': 4, 'am': 4,
    'm': 5, 'dy': 5, 'ry': 5, 'y': 5,
}
FL_MIDDLES = set(FL_STAGE_MAP.keys())

CLASS_MAP_PATH = Path('C:/git/voynich/phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json')
with open(CLASS_MAP_PATH, 'r', encoding='utf-8') as f:
    class_data = json.load(f)
TOKEN_TO_ROLE = class_data.get('token_to_role', {})

STRONG_FWD = {'f26v','f76v','f112r','f82r','f115v','f85r2','f105r','f108v','f94r','f95v2','f106r'}

tx = Transcript()
morph = Morphology()

line_tokens = defaultdict(list)
for t in tx.currier_b():
    if t.folio in STRONG_FWD:
        line_tokens[(t.folio, t.line)].append(t)

def annotate(word):
    m = morph.extract(word)
    if not m:
        return {'word': word, 'is_fl': False, 'stage': None,
                'role': TOKEN_TO_ROLE.get(word, 'UNK')}
    is_fl = m.middle is not None and m.middle in FL_MIDDLES
    stage = FL_STAGE_MAP.get(m.middle) if is_fl else None
    return {'word': word, 'is_fl': is_fl, 'stage': stage,
            'role': TOKEN_TO_ROLE.get(word, 'UNK')}

WINDOW = 2
ROLES = ['ENERGY_OPERATOR', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL']
ROLE_SHORT = {'ENERGY_OPERATOR': 'EN', 'AUXILIARY': 'AX',
              'FREQUENT_OPERATOR': 'FQ', 'CORE_CONTROL': 'CC'}
STAGE_NAMES = ['INIT', 'EARL', 'MEDI', 'LATE', 'FINL', 'TERM']

print("=" * 80, flush=True)
print("FL RESOLUTION TEST 4: NEGATIVE CONTROL (ROLE INDEPENDENCE)", flush=True)
print("=" * 80, flush=True)

# Collect (FL_stage, neighbor_role) pairs
stage_role = defaultdict(Counter)
total_pairs = 0

for key, tokens in line_tokens.items():
    annots = [annotate(t.word) for t in tokens]

    for idx, a in enumerate(annots):
        if not a['is_fl']:
            continue
        fl_stage = a['stage']

        for offset in range(-WINDOW, WINDOW + 1):
            if offset == 0:
                continue
            j = idx + offset
            if 0 <= j < len(annots):
                b = annots[j]
                if not b['is_fl'] and b['role'] in ROLES:
                    stage_role[fl_stage][b['role']] += 1
                    total_pairs += 1

print(f"\n  Total FL-neighbor pairs (known roles): {total_pairs}", flush=True)

# Cross-tab
print(f"\n  {'Stage':<6}", end="")
for r in ROLES:
    print(f" {ROLE_SHORT[r]:>5}", end="")
print(f" {'Total':>6}")

table = []
for stage in range(6):
    total = sum(stage_role[stage].values())
    if total < 5:
        continue
    row = [stage_role[stage].get(r, 0) for r in ROLES]
    table.append(row)
    print(f"  {STAGE_NAMES[stage]:<6}", end="")
    for r in ROLES:
        c = stage_role[stage].get(r, 0)
        pct = c / total * 100
        print(f" {pct:>4.0f}%", end="")
    print(f" {total:>6}")

# Chi-squared
if len(table) >= 2:
    table_np = np.array(table)
    col_sums = table_np.sum(axis=0)
    table_np = table_np[:, col_sums > 0]

    if table_np.shape[1] >= 2:
        chi2, p_val, dof, _ = chi2_contingency(table_np)
        n = table_np.sum()
        min_dim = min(table_np.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

        print(f"\n  Chi-squared: {chi2:.1f}, dof={dof}", flush=True)
        print(f"  p-value: {p_val:.4e}", flush=True)
        print(f"  Cramer's V: {cramers_v:.4f}", flush=True)

        print(f"\n{'='*70}", flush=True)
        print("VERDICT", flush=True)
        print(f"{'='*70}", flush=True)

        if p_val >= 0.05 and cramers_v < 0.05:
            print(f"  CONFIRMED: Chi2 NS (p={p_val:.4f}), V={cramers_v:.4f} < 0.05", flush=True)
            print(f"  -> FL stage does NOT predict role choice", flush=True)
            print(f"  -> Negative control PASSES", flush=True)
        elif p_val >= 0.05:
            print(f"  CONFIRMED: Chi2 NS (p={p_val:.4f}), V={cramers_v:.4f}", flush=True)
            print(f"  -> FL stage does NOT predict role choice", flush=True)
            print(f"  -> Negative control PASSES (V slightly above 0.05 threshold)", flush=True)
        else:
            print(f"  *** WARNING: Chi2 SIGNIFICANT (p={p_val:.4f}), V={cramers_v:.4f} ***", flush=True)
            print(f"  -> MODEL VIOLATION: FL stage predicts role choice", flush=True)
            print(f"  -> STOP: re-evaluate all conclusions", flush=True)

print(flush=True)
