"""
FL RESOLUTION TEST 3: FL Stage -> Suffix Profile (TERTIARY)

Hypothesis H3: Later FL stages correspond to more complete/closed
token morphology, reflected in suffix choice.

Method:
- For operational tokens on FL-bearing lines, collect suffix by FL stage
- Analyze within role and within prefix family
- Chi-squared or KL divergence across stages
- Exclude CC (suffix-free by design)

Decision:
- PASS: Suffix distributions shift monotonically with FL stage
- FAIL: Flat distributions
"""
import sys, json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy.stats import chi2_contingency, spearmanr

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
        return {'word': word, 'is_fl': False, 'stage': None, 'prefix': None,
                'middle': None, 'suffix': None,
                'role': TOKEN_TO_ROLE.get(word, 'UNK')}
    is_fl = m.middle is not None and m.middle in FL_MIDDLES
    prefix = m.prefix if m.prefix else '_'
    stage = FL_STAGE_MAP.get(m.middle) if is_fl else None
    suffix = m.suffix if m.suffix else '_none'
    return {'word': word, 'is_fl': is_fl, 'stage': stage, 'prefix': prefix,
            'middle': m.middle, 'suffix': suffix,
            'role': TOKEN_TO_ROLE.get(word, 'UNK')}

annotated_lines = {}
for key, tokens in line_tokens.items():
    annotated_lines[key] = [annotate(t.word) for t in tokens]

WINDOW = 2
N_SHUFFLES = 1000
rng = np.random.default_rng(42)
STAGE_NAMES = ['INIT', 'EARL', 'MEDI', 'LATE', 'FINL', 'TERM']

print("=" * 80, flush=True)
print("FL RESOLUTION TEST 3: SUFFIX PROFILE BY FL STAGE", flush=True)
print("=" * 80, flush=True)

# =============================================
# Collect (FL_stage, neighbor_suffix, neighbor_role) tuples
# =============================================
pairs = []
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
                if not b['is_fl'] and b['suffix'] and b['role'] not in ('UNK', 'CORE_CONTROL'):
                    pairs.append({
                        'fl_stage': fl_stage,
                        'fl_prefix': fl_prefix,
                        'nb_suffix': b['suffix'],
                        'nb_role': b['role'],
                        'nb_prefix': b['prefix'],
                    })

print(f"  Total FL-neighbor pairs (excl CC, UNK): {len(pairs)}", flush=True)

# =============================================
# A. GLOBAL: Suffix distribution by FL stage
# =============================================
print(f"\n{'='*70}", flush=True)
print("A. GLOBAL SUFFIX DISTRIBUTION BY FL STAGE", flush=True)
print(f"{'='*70}", flush=True)

stage_suffix = defaultdict(Counter)
for p in pairs:
    stage_suffix[p['fl_stage']][p['nb_suffix']] += 1

# Get top suffixes
all_suffixes = Counter()
for p in pairs:
    all_suffixes[p['nb_suffix']] += 1
top_suffixes = [s for s, _ in all_suffixes.most_common(10)]

print(f"\n  {'Stage':<6}", end="", flush=True)
for s in top_suffixes:
    print(f" {s:>6}", end="")
print(f" {'Total':>6}")

for stage in range(6):
    total = sum(stage_suffix[stage].values())
    if total < 5:
        continue
    print(f"  {STAGE_NAMES[stage]:<6}", end="")
    for s in top_suffixes:
        c = stage_suffix[stage].get(s, 0)
        pct = c / total * 100
        if pct > 0:
            print(f" {pct:>5.0f}%", end="")
        else:
            print(f"      .", end="")
    print(f" {total:>6}")

# Chi-squared
table = []
for stage in range(6):
    row = [stage_suffix[stage].get(s, 0) for s in top_suffixes]
    if sum(row) >= 5:
        table.append(row)

if len(table) >= 2:
    table_np = np.array(table)
    # Remove zero columns
    col_sums = table_np.sum(axis=0)
    table_np = table_np[:, col_sums > 0]

    if table_np.shape[1] >= 2:
        chi2, p_val, dof, expected = chi2_contingency(table_np)
        n = table_np.sum()
        min_dim = min(table_np.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        print(f"\n  Chi-squared: {chi2:.1f}, dof={dof}, p={p_val:.4e}", flush=True)
        print(f"  Cramer's V: {cramers_v:.3f}", flush=True)

# =============================================
# B. PER-ROLE: Suffix by FL stage
# =============================================
print(f"\n{'='*70}", flush=True)
print("B. PER-ROLE SUFFIX BY FL STAGE", flush=True)
print(f"{'='*70}", flush=True)

for role in ['ENERGY_OPERATOR', 'AUXILIARY', 'FREQUENT_OPERATOR']:
    role_pairs = [p for p in pairs if p['nb_role'] == role]
    if len(role_pairs) < 30:
        continue

    role_short = {'ENERGY_OPERATOR': 'EN', 'AUXILIARY': 'AX', 'FREQUENT_OPERATOR': 'FQ'}[role]
    print(f"\n  --- {role_short} ---", flush=True)

    r_stage_suffix = defaultdict(Counter)
    for p in role_pairs:
        r_stage_suffix[p['fl_stage']][p['nb_suffix']] += 1

    r_all_suffixes = Counter()
    for p in role_pairs:
        r_all_suffixes[p['nb_suffix']] += 1
    r_top = [s for s, _ in r_all_suffixes.most_common(8)]

    print(f"  {'Stage':<6}", end="")
    for s in r_top:
        print(f" {s:>6}", end="")
    print(f" {'N':>5}")

    r_table = []
    for stage in range(6):
        total = sum(r_stage_suffix[stage].values())
        if total < 3:
            continue
        row = [r_stage_suffix[stage].get(s, 0) for s in r_top]
        r_table.append(row)
        print(f"  {STAGE_NAMES[stage]:<6}", end="")
        for s in r_top:
            c = r_stage_suffix[stage].get(s, 0)
            pct = c / total * 100 if total > 0 else 0
            if pct > 0:
                print(f" {pct:>5.0f}%", end="")
            else:
                print(f"      .", end="")
        print(f" {total:>5}")

    if len(r_table) >= 2:
        r_table_np = np.array(r_table)
        col_sums = r_table_np.sum(axis=0)
        r_table_np = r_table_np[:, col_sums > 0]
        if r_table_np.shape[1] >= 2:
            chi2, p_val, dof, _ = chi2_contingency(r_table_np)
            n = r_table_np.sum()
            min_dim = min(r_table_np.shape) - 1
            v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
            print(f"  Chi2={chi2:.1f}, p={p_val:.4e}, V={v:.3f}", flush=True)

# =============================================
# C. MONOTONICITY TEST: Does suffix complexity increase with stage?
# =============================================
print(f"\n{'='*70}", flush=True)
print("C. MONOTONICITY: SUFFIX LENGTH vs FL STAGE", flush=True)
print(f"{'='*70}", flush=True)
print(f"  Does suffix 'complexity' (length) increase with FL stage?\n", flush=True)

# Simple proxy: suffix length (longer = more complex?)
stage_suffix_lengths = defaultdict(list)
for p in pairs:
    suf = p['nb_suffix']
    suf_len = 0 if suf == '_none' else len(suf)
    stage_suffix_lengths[p['fl_stage']].append(suf_len)

for stage in range(6):
    lengths = stage_suffix_lengths[stage]
    if len(lengths) < 5:
        continue
    no_suffix_pct = sum(1 for l in lengths if l == 0) / len(lengths) * 100
    print(f"  {STAGE_NAMES[stage]}: mean_len={np.mean(lengths):.2f} no_suffix={no_suffix_pct:.1f}% n={len(lengths)}", flush=True)

all_stages_flat = [p['fl_stage'] for p in pairs]
all_suf_lens = [0 if p['nb_suffix'] == '_none' else len(p['nb_suffix']) for p in pairs]
rho, p_rho = spearmanr(all_stages_flat, all_suf_lens)
print(f"\n  Spearman (stage vs suffix_length): rho={rho:.4f}, p={p_rho:.4e}", flush=True)

# =============================================
# D. SHUFFLE CONTROL: NMI(FL_stage, suffix) vs shuffled
# =============================================
print(f"\n{'='*70}", flush=True)
print("D. SHUFFLE CONTROL: NMI(FL_STAGE, SUFFIX)", flush=True)
print(f"{'='*70}", flush=True)

from sklearn.metrics import normalized_mutual_info_score

fl_s = [p['fl_stage'] for p in pairs]
nb_suf = [p['nb_suffix'] for p in pairs]

real_nmi = normalized_mutual_info_score(fl_s, nb_suf)

fl_prefix_groups = defaultdict(list)
for i, p in enumerate(pairs):
    fl_prefix_groups[p['fl_prefix']].append(i)

shuf_nmis = []
for _ in range(N_SHUFFLES):
    shuf_s = list(fl_s)
    for prefix, indices in fl_prefix_groups.items():
        group_stages = [shuf_s[i] for i in indices]
        rng.shuffle(group_stages)
        for i, idx in enumerate(indices):
            shuf_s[idx] = group_stages[i]
    shuf_nmis.append(normalized_mutual_info_score(shuf_s, nb_suf))

p_nmi = sum(1 for s in shuf_nmis if s >= real_nmi) / N_SHUFFLES
pctile = sum(1 for s in shuf_nmis if s < real_nmi) / N_SHUFFLES * 100

print(f"  Real NMI: {real_nmi:.6f}", flush=True)
print(f"  Shuffle mean: {np.mean(shuf_nmis):.6f} +/- {np.std(shuf_nmis):.6f}", flush=True)
print(f"  Percentile: {pctile:.1f}th", flush=True)
print(f"  p-value: {p_nmi:.4f}", flush=True)

# =============================================
# VERDICT
# =============================================
print(f"\n{'='*70}", flush=True)
print("VERDICT", flush=True)
print(f"{'='*70}", flush=True)

if p_nmi < 0.001:
    print(f"  H3 PASS: FL stage significantly predicts suffix profile", flush=True)
    print(f"  -> FL reflects processing completeness", flush=True)
elif p_nmi < 0.05:
    print(f"  H3 WEAK PASS: Some suffix-stage association", flush=True)
else:
    print(f"  H3 FAIL: Flat suffix distributions across FL stages", flush=True)
    print(f"  -> FL stage does not affect execution morphology", flush=True)

print(flush=True)
