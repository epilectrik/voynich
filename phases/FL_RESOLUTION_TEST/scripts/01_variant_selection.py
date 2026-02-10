"""
FL RESOLUTION TEST 1: FL Stage -> Token-Variant Selection (PRIMARY)

Hypothesis H1: FL stage biases which token variants are selected within
an already-chosen role, consistent with C506.b.

Method:
- For each FL token, identify neighboring operational tokens within +/-2
- Fix neighbor's ROLE and PREFIX
- Record neighbor's MIDDLE identity
- Compute NMI(FL_STAGE, NEIGHBOR_MIDDLE) per role, per prefix
- Shuffle FL stages within same prefix group for control (1000 iterations)

Decision:
- PASS: NMI > 99.9th percentile of shuffles
- FAIL: NMI indistinguishable from shuffle
"""
import sys, json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from sklearn.metrics import normalized_mutual_info_score

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

# Build lines
line_tokens = defaultdict(list)
for t in tx.currier_b():
    if t.folio in STRONG_FWD:
        line_tokens[(t.folio, t.line)].append(t)

def annotate(word):
    m = morph.extract(word)
    if not m:
        return {'word': word, 'is_fl': False, 'stage': None, 'prefix': None,
                'middle': None, 'role': TOKEN_TO_ROLE.get(word, 'UNK')}
    is_fl = m.middle is not None and m.middle in FL_MIDDLES
    prefix = m.prefix if m.prefix else '_'
    stage = FL_STAGE_MAP.get(m.middle) if is_fl else None
    return {'word': word, 'is_fl': is_fl, 'stage': stage, 'prefix': prefix,
            'middle': m.middle, 'role': TOKEN_TO_ROLE.get(word, 'UNK')}

# Annotate all lines
annotated_lines = {}
for key, tokens in line_tokens.items():
    annotated_lines[key] = [annotate(t.word) for t in tokens]

N_SHUFFLES = 1000
rng = np.random.default_rng(42)
WINDOW = 2  # +/-2 positions

print("=" * 80, flush=True)
print("FL RESOLUTION TEST 1: TOKEN-VARIANT SELECTION", flush=True)
print("=" * 80, flush=True)
print(f"  Window: +/-{WINDOW} positions", flush=True)
print(f"  Shuffles: {N_SHUFFLES}", flush=True)

# =============================================
# Collect (FL_stage, neighbor_middle, neighbor_role, neighbor_prefix) tuples
# Also track FL prefix for shuffle grouping
# =============================================
pairs = []  # (fl_stage, fl_prefix, neighbor_middle, neighbor_role, neighbor_prefix, line_key)

for key, annots in annotated_lines.items():
    for idx, a in enumerate(annots):
        if not a['is_fl']:
            continue
        fl_stage = a['stage']
        fl_prefix = a['prefix']

        for offset in range(-WINDOW, WINDOW + 1):
            if offset == 0:
                continue
            j = idx + offset
            if 0 <= j < len(annots):
                b = annots[j]
                if not b['is_fl'] and b['middle'] and b['role'] != 'UNK':
                    pairs.append({
                        'fl_stage': fl_stage,
                        'fl_prefix': fl_prefix,
                        'nb_middle': b['middle'],
                        'nb_role': b['role'],
                        'nb_prefix': b['prefix'],
                        'line_key': key,
                    })

print(f"  Total FL-neighbor pairs: {len(pairs)}", flush=True)

# =============================================
# A. GLOBAL NMI: FL_STAGE vs NEIGHBOR_MIDDLE (all pairs)
# =============================================
print(f"\n{'='*70}", flush=True)
print("A. GLOBAL NMI: FL_STAGE vs NEIGHBOR_MIDDLE", flush=True)
print(f"{'='*70}", flush=True)

fl_stages_all = [p['fl_stage'] for p in pairs]
nb_middles_all = [p['nb_middle'] for p in pairs]

real_nmi_global = normalized_mutual_info_score(fl_stages_all, nb_middles_all)
print(f"  Real NMI: {real_nmi_global:.6f}", flush=True)

# Shuffle: permute FL stages within same prefix group
fl_prefix_groups = defaultdict(list)
for i, p in enumerate(pairs):
    fl_prefix_groups[p['fl_prefix']].append(i)

shuf_nmis_global = []
for _ in range(N_SHUFFLES):
    shuf_stages = list(fl_stages_all)
    for prefix, indices in fl_prefix_groups.items():
        group_stages = [shuf_stages[i] for i in indices]
        rng.shuffle(group_stages)
        for i, idx in enumerate(indices):
            shuf_stages[idx] = group_stages[i]
    shuf_nmis_global.append(normalized_mutual_info_score(shuf_stages, nb_middles_all))

p_global = sum(1 for s in shuf_nmis_global if s >= real_nmi_global) / N_SHUFFLES
pctile = sum(1 for s in shuf_nmis_global if s < real_nmi_global) / N_SHUFFLES * 100
print(f"  Shuffle mean NMI: {np.mean(shuf_nmis_global):.6f} +/- {np.std(shuf_nmis_global):.6f}", flush=True)
print(f"  Percentile: {pctile:.1f}th", flush=True)
print(f"  p-value: {p_global:.4f}", flush=True)
sig = "PASS (>99.9th)" if pctile > 99.9 else "PASS (>99th)" if pctile > 99 else "PASS (>95th)" if pctile > 95 else "FAIL"
print(f"  Verdict: {sig}", flush=True)

# =============================================
# B. PER-ROLE NMI: FL_STAGE vs NEIGHBOR_MIDDLE
# =============================================
print(f"\n{'='*70}", flush=True)
print("B. PER-ROLE NMI: FL_STAGE vs NEIGHBOR_MIDDLE", flush=True)
print(f"{'='*70}", flush=True)

for role in ['ENERGY_OPERATOR', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL']:
    role_pairs = [p for p in pairs if p['nb_role'] == role]
    if len(role_pairs) < 30:
        print(f"  {role}: insufficient data (n={len(role_pairs)})", flush=True)
        continue

    fl_s = [p['fl_stage'] for p in role_pairs]
    nb_m = [p['nb_middle'] for p in role_pairs]

    if len(set(fl_s)) < 2 or len(set(nb_m)) < 2:
        print(f"  {role}: insufficient variance", flush=True)
        continue

    real_nmi = normalized_mutual_info_score(fl_s, nb_m)

    # Build prefix groups for this role subset
    rp_prefix_groups = defaultdict(list)
    for i, p in enumerate(role_pairs):
        rp_prefix_groups[p['fl_prefix']].append(i)

    shuf_nmis = []
    for _ in range(N_SHUFFLES):
        shuf_s = list(fl_s)
        for prefix, indices in rp_prefix_groups.items():
            group_stages = [shuf_s[i] for i in indices]
            rng.shuffle(group_stages)
            for i, idx in enumerate(indices):
                shuf_s[idx] = group_stages[i]
        shuf_nmis.append(normalized_mutual_info_score(shuf_s, nb_m))

    p_val = sum(1 for s in shuf_nmis if s >= real_nmi) / N_SHUFFLES
    pctile = sum(1 for s in shuf_nmis if s < real_nmi) / N_SHUFFLES * 100
    sig = "PASS" if pctile > 99.9 else "pass" if pctile > 95 else "FAIL"
    print(f"  {role}:", flush=True)
    print(f"    NMI={real_nmi:.6f}  shuffle={np.mean(shuf_nmis):.6f}+/-{np.std(shuf_nmis):.6f}  pctile={pctile:.1f}  p={p_val:.4f}  {sig}", flush=True)

# =============================================
# C. PER-ROLE-PREFIX NMI: FL_STAGE vs NEIGHBOR_MIDDLE
# =============================================
print(f"\n{'='*70}", flush=True)
print("C. PER-ROLE-PREFIX NMI: FL_STAGE vs NEIGHBOR_MIDDLE", flush=True)
print(f"{'='*70}", flush=True)
print(f"  (Fixing both neighbor role AND neighbor prefix)\n", flush=True)

role_prefixes = defaultdict(list)
for p in pairs:
    role_prefixes[(p['nb_role'], p['nb_prefix'])].append(p)

results = []
for (role, nb_prefix), rp_pairs in sorted(role_prefixes.items()):
    if len(rp_pairs) < 30:
        continue

    fl_s = [p['fl_stage'] for p in rp_pairs]
    nb_m = [p['nb_middle'] for p in rp_pairs]

    if len(set(fl_s)) < 2 or len(set(nb_m)) < 2:
        continue

    real_nmi = normalized_mutual_info_score(fl_s, nb_m)

    # Shuffle within FL prefix groups
    rp_pg = defaultdict(list)
    for i, p in enumerate(rp_pairs):
        rp_pg[p['fl_prefix']].append(i)

    shuf_nmis = []
    for _ in range(N_SHUFFLES):
        shuf_s = list(fl_s)
        for prefix, indices in rp_pg.items():
            group_stages = [shuf_s[i] for i in indices]
            rng.shuffle(group_stages)
            for i, idx in enumerate(indices):
                shuf_s[idx] = group_stages[i]
        shuf_nmis.append(normalized_mutual_info_score(shuf_s, nb_m))

    p_val = sum(1 for s in shuf_nmis if s >= real_nmi) / N_SHUFFLES
    pctile = sum(1 for s in shuf_nmis if s < real_nmi) / N_SHUFFLES * 100

    role_short = {'ENERGY_OPERATOR': 'EN', 'AUXILIARY': 'AX',
                  'FREQUENT_OPERATOR': 'FQ', 'CORE_CONTROL': 'CC'}.get(role, role[:3])
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
    print(f"  {role_short}-{nb_prefix:<6}: NMI={real_nmi:.4f} shuf={np.mean(shuf_nmis):.4f} pctile={pctile:.1f} p={p_val:.4f} n={len(rp_pairs)} {sig}", flush=True)
    results.append({'role': role, 'prefix': nb_prefix, 'nmi': real_nmi,
                    'shuf_mean': np.mean(shuf_nmis), 'p': p_val, 'n': len(rp_pairs)})

# =============================================
# D. SUMMARY
# =============================================
print(f"\n{'='*70}", flush=True)
print("SUMMARY", flush=True)
print(f"{'='*70}", flush=True)

n_pass = sum(1 for r in results if r['p'] < 0.001)
n_tested = len(results)
print(f"  Role-prefix combinations tested: {n_tested}", flush=True)
print(f"  PASS (p<0.001): {n_pass}", flush=True)
print(f"  Any PASS (p<0.05): {sum(1 for r in results if r['p'] < 0.05)}", flush=True)

if p_global < 0.001:
    print(f"\n  VERDICT: H1 PASS - FL stage biases token-variant selection", flush=True)
    print(f"  FL is an assessment signal influencing variant choice", flush=True)
elif p_global < 0.05:
    print(f"\n  VERDICT: H1 WEAK PASS - some evidence of variant selection", flush=True)
else:
    print(f"\n  VERDICT: H1 FAIL - FL stage does not bias token variants", flush=True)
    print(f"  FL is purely descriptive with no grammatical uptake", flush=True)

print(flush=True)
