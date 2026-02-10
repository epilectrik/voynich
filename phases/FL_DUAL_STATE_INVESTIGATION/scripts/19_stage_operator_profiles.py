"""
19_stage_operator_profiles.py

If FL is a scope label ("at stage X, do these operations"), then
gap operators should differ by FL stage. INITIAL lines should have
different operations than TERMINAL lines.

Group lines by their LOW FL stage, profile the gap tokens, and
test whether operator vocabulary changes significantly.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, kruskal

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

MIN_N = 50
tx = Transcript()
morph = Morphology()

# Load role map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

# ============================================================
# Collect tokens by line, fit GMMs
# ============================================================
line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

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

# ============================================================
# Annotate lines: identify LOW/HIGH FL clusters and gap tokens
# ============================================================
def annotate_line(tokens):
    n = len(tokens)
    if n <= 1:
        return None

    fl_tokens = []
    all_tokens = []

    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1)
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        stage = None
        stage_num = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]
            stage_num = STAGE_ORDER[stage]

        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else 'NONE'
        middle = m.middle if m and m.middle else None

        entry = {
            'idx': idx, 'pos': pos, 'word': t.word,
            'prefix': prefix, 'middle': middle,
            'role': role, 'is_fl': is_fl,
            'mode': mode, 'stage': stage, 'stage_num': stage_num,
        }
        all_tokens.append(entry)
        if is_fl and mode:
            fl_tokens.append(entry)

    return {'all': all_tokens, 'fl': fl_tokens}

# ============================================================
# For each line: get dominant LOW stage, dominant HIGH stage, gap tokens
# ============================================================
line_profiles = []

for line_key, tokens in line_tokens.items():
    ann = annotate_line(tokens)
    if not ann:
        continue

    low_fls = [f for f in ann['fl'] if f['mode'] == 'LOW']
    high_fls = [f for f in ann['fl'] if f['mode'] == 'HIGH']

    if not low_fls:
        continue

    # Dominant LOW stage (most common, or earliest)
    low_stages = Counter(f['stage'] for f in low_fls)
    dominant_low = low_stages.most_common(1)[0][0]
    dominant_low_num = STAGE_ORDER[dominant_low]

    # Dominant HIGH stage
    dominant_high = None
    dominant_high_num = None
    if high_fls:
        high_stages = Counter(f['stage'] for f in high_fls)
        dominant_high = high_stages.most_common(1)[0][0]
        dominant_high_num = STAGE_ORDER[dominant_high]

    # Gap tokens: non-FL tokens between LOW and HIGH clusters
    max_low_pos = max(f['pos'] for f in low_fls)
    min_high_pos = min(f['pos'] for f in high_fls) if high_fls else 1.0

    gap_tokens = [t for t in ann['all'] if not t['is_fl']
                  and t['pos'] > max_low_pos and t['pos'] < min_high_pos]

    # All non-FL tokens in the line
    non_fl = [t for t in ann['all'] if not t['is_fl']]

    line_profiles.append({
        'line_key': line_key,
        'low_stage': dominant_low,
        'low_stage_num': dominant_low_num,
        'high_stage': dominant_high,
        'high_stage_num': dominant_high_num,
        'gap_tokens': gap_tokens,
        'non_fl_tokens': non_fl,
        'n_tokens': len(tokens),
    })

print(f"Lines with FL profiles: {len(line_profiles)}")

# ============================================================
# TEST 1: Role distribution by LOW FL stage
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: GAP ROLE DISTRIBUTION BY LOW FL STAGE")
print(f"{'='*60}")

stage_gap_roles = defaultdict(Counter)
stage_gap_counts = Counter()

for lp in line_profiles:
    stage = lp['low_stage']
    for gt in lp['gap_tokens']:
        stage_gap_roles[stage][gt['role']] += 1
        stage_gap_counts[stage] += 1

all_roles = sorted(set(r for c in stage_gap_roles.values() for r in c.keys()))

# Print role distribution per stage
header = f"{'Stage':>10}"
for role in all_roles:
    short = role[:8]
    header += f" {short:>8}"
print(header)
print("-" * (10 + 9 * len(all_roles)))

stage_role_pcts = {}
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
    if stage not in stage_gap_roles:
        continue
    total = stage_gap_counts[stage]
    if total < 20:
        continue
    row = f"{stage:>10}"
    pcts = {}
    for role in all_roles:
        count = stage_gap_roles[stage].get(role, 0)
        pct = count / total * 100
        pcts[role] = round(pct, 1)
        row += f" {pct:>7.1f}%"
    stage_role_pcts[stage] = pcts
    print(f"{row}  (n={total})")

# ============================================================
# TEST 2: Chi-squared — stage x role contingency
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: CHI-SQUARED — LOW FL STAGE x GAP ROLE")
print(f"{'='*60}")

valid_stages = [s for s in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']
                if stage_gap_counts.get(s, 0) >= 30]

if len(valid_stages) >= 2 and len(all_roles) >= 2:
    table = np.array([[stage_gap_roles[s].get(r, 0) for r in all_roles]
                       for s in valid_stages])
    # Remove zero columns
    nonzero = table.sum(axis=0) > 0
    table = table[:, nonzero]
    roles_used = [r for r, nz in zip(all_roles, nonzero) if nz]

    chi2, p_val, dof, expected = chi2_contingency(table)
    cramers_v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
    print(f"  chi2={chi2:.1f}, p={p_val:.2e}, dof={dof}, Cramer's V={cramers_v:.3f}")
    print(f"  Stages: {valid_stages}")
    print(f"  Roles: {roles_used}")

# ============================================================
# TEST 3: Top gap WORDS by LOW FL stage
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: TOP GAP WORDS BY LOW FL STAGE")
print(f"{'='*60}")

stage_gap_words = defaultdict(Counter)
for lp in line_profiles:
    stage = lp['low_stage']
    for gt in lp['gap_tokens']:
        stage_gap_words[stage][gt['word']] += 1

for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
    if stage not in stage_gap_words or sum(stage_gap_words[stage].values()) < 30:
        continue
    top = stage_gap_words[stage].most_common(10)
    words_str = ', '.join(f"{w}({c})" for w, c in top)
    print(f"  {stage:>10}: {words_str}")

# ============================================================
# TEST 4: Gap PREFIX distribution by LOW FL stage
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: GAP PREFIX DISTRIBUTION BY LOW FL STAGE")
print(f"{'='*60}")

stage_gap_prefixes = defaultdict(Counter)
for lp in line_profiles:
    stage = lp['low_stage']
    for gt in lp['gap_tokens']:
        stage_gap_prefixes[stage][gt['prefix']] += 1

# Top prefixes overall
all_gap_prefixes = Counter()
for c in stage_gap_prefixes.values():
    all_gap_prefixes += c
top_prefixes = [p for p, _ in all_gap_prefixes.most_common(10)]

header = f"{'Stage':>10}"
for pfx in top_prefixes:
    header += f" {pfx:>7}"
print(header)
print("-" * (10 + 8 * len(top_prefixes)))

for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
    if stage not in stage_gap_prefixes:
        continue
    total = sum(stage_gap_prefixes[stage].values())
    if total < 30:
        continue
    row = f"{stage:>10}"
    for pfx in top_prefixes:
        count = stage_gap_prefixes[stage].get(pfx, 0)
        pct = count / total * 100
        row += f" {pct:>6.1f}%"
    print(f"{row}  (n={total})")

# Chi-squared on prefix distribution
if len(valid_stages) >= 2:
    table_pfx = np.array([[stage_gap_prefixes[s].get(p, 0) for p in top_prefixes]
                           for s in valid_stages])
    nonzero_pfx = table_pfx.sum(axis=0) > 0
    table_pfx = table_pfx[:, nonzero_pfx]
    if table_pfx.shape[1] >= 2:
        chi2_pfx, p_pfx, dof_pfx, _ = chi2_contingency(table_pfx)
        v_pfx = np.sqrt(chi2_pfx / (table_pfx.sum() * (min(table_pfx.shape) - 1)))
        print(f"\n  Chi-squared: chi2={chi2_pfx:.1f}, p={p_pfx:.2e}, Cramer's V={v_pfx:.3f}")

# ============================================================
# TEST 5: Gap MIDDLE distribution by LOW FL stage
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: GAP MIDDLE (non-FL) DISTRIBUTION BY LOW FL STAGE")
print(f"{'='*60}")

stage_gap_middles = defaultdict(Counter)
for lp in line_profiles:
    stage = lp['low_stage']
    for gt in lp['gap_tokens']:
        if gt['middle']:
            stage_gap_middles[stage][gt['middle']] += 1

# Top non-FL middles overall
all_gap_middles = Counter()
for c in stage_gap_middles.values():
    all_gap_middles += c
top_middles = [m for m, _ in all_gap_middles.most_common(15)]

for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
    if stage not in stage_gap_middles:
        continue
    total = sum(stage_gap_middles[stage].values())
    if total < 30:
        continue
    top = stage_gap_middles[stage].most_common(8)
    mids_str = ', '.join(f"{m}({c})" for m, c in top)
    print(f"  {stage:>10}: {mids_str}")

# ============================================================
# TEST 6: Do specific FL MIDDLEs predict specific gap words?
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: SPECIFIC FL MIDDLE -> GAP WORD ASSOCIATIONS")
print(f"{'='*60}")

# For each FL MIDDLE that appears in LOW position, what gap words follow?
fl_middle_gap_words = defaultdict(Counter)
for lp in line_profiles:
    # Use the actual LOW FL middles, not just stage
    for fl in [f for f in lp.get('_low_fls', [])]:
        pass  # Need to re-extract

# Re-extract with more detail
fl_mid_gap = defaultdict(Counter)
for line_key, tokens in line_tokens.items():
    ann = annotate_line(tokens)
    if not ann:
        continue

    low_fls = [f for f in ann['fl'] if f['mode'] == 'LOW']
    high_fls = [f for f in ann['fl'] if f['mode'] == 'HIGH']
    if not low_fls:
        continue

    max_low_pos = max(f['pos'] for f in low_fls)
    min_high_pos = min(f['pos'] for f in high_fls) if high_fls else 1.0

    gap = [t for t in ann['all'] if not t['is_fl']
           and t['pos'] > max_low_pos and t['pos'] < min_high_pos]

    # Associate each LOW FL middle with gap words
    for fl in low_fls:
        for gt in gap:
            fl_mid_gap[fl['middle']][gt['word']] += 1

# Show top gap words per FL MIDDLE
for mid in sorted(FL_STAGE_MAP.keys(), key=lambda x: FL_STAGE_MAP[x][1]):
    if mid not in fl_mid_gap or sum(fl_mid_gap[mid].values()) < 30:
        continue
    total = sum(fl_mid_gap[mid].values())
    top = fl_mid_gap[mid].most_common(8)
    words_str = ', '.join(f"{w}({c})" for w, c in top)
    stage = FL_STAGE_MAP[mid][0]
    print(f"  {mid:>4} ({stage:>10}): {words_str}  [n={total}]")

# ============================================================
# TEST 7: Vocabulary overlap between stages
# ============================================================
print(f"\n{'='*60}")
print("TEST 7: GAP VOCABULARY OVERLAP (JACCARD) BETWEEN STAGES")
print(f"{'='*60}")

stage_vocab = {}
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']:
    if stage in stage_gap_words and sum(stage_gap_words[stage].values()) >= 30:
        # Use top-50 words to avoid noise
        stage_vocab[stage] = set(w for w, _ in stage_gap_words[stage].most_common(50))

stages_with_vocab = sorted(stage_vocab.keys(), key=lambda s: STAGE_ORDER[s])
if len(stages_with_vocab) >= 2:
    header = f"{'':>10}"
    for s in stages_with_vocab:
        header += f" {s[:6]:>7}"
    print(header)

    jaccard_matrix = {}
    for s1 in stages_with_vocab:
        row = f"{s1:>10}"
        for s2 in stages_with_vocab:
            intersection = stage_vocab[s1] & stage_vocab[s2]
            union = stage_vocab[s1] | stage_vocab[s2]
            j = len(intersection) / len(union) if union else 0
            jaccard_matrix[(s1, s2)] = round(j, 2)
            row += f" {j:>7.2f}"
        print(row)

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")

# Check if stage predicts gap composition
stage_predicts = False
if 'chi2' in dir() or True:
    try:
        if p_val < 0.01 and cramers_v > 0.05:
            stage_predicts = True
    except:
        pass

# Check vocabulary differentiation
vocab_differentiated = False
if jaccard_matrix:
    # Average off-diagonal Jaccard
    off_diag = [v for (s1, s2), v in jaccard_matrix.items() if s1 != s2]
    avg_jaccard = np.mean(off_diag) if off_diag else 1.0
    if avg_jaccard < 0.50:
        vocab_differentiated = True
    print(f"  Average inter-stage Jaccard: {avg_jaccard:.3f}")

if stage_predicts and vocab_differentiated:
    verdict = "STAGE_SPECIFIC_OPERATIONS"
    explanation = "Different FL stages have significantly different gap operator profiles"
elif stage_predicts:
    verdict = "WEAK_STAGE_SPECIFICITY"
    explanation = "Stage predicts gap composition statistically but vocabularies heavily overlap"
elif vocab_differentiated:
    verdict = "VOCABULARY_DIVERGENCE"
    explanation = "Stage vocabularies differ but role distribution is uniform"
else:
    verdict = "NO_STAGE_SPECIFICITY"
    explanation = "Gap operators do not vary meaningfully by FL stage"

print(f"VERDICT: {verdict}")
print(f"  {explanation}")

# ============================================================
# Save results
# ============================================================
result = {
    'n_profiled_lines': len(line_profiles),
    'stage_gap_role_pcts': stage_role_pcts,
    'chi_squared_role': {
        'chi2': round(float(chi2), 1) if 'chi2' in dir() else None,
        'p': float(p_val) if 'p_val' in dir() else None,
        'cramers_v': round(float(cramers_v), 3) if 'cramers_v' in dir() else None,
    },
    'top_gap_words_by_stage': {
        stage: dict(stage_gap_words[stage].most_common(10))
        for stage in stage_gap_words if sum(stage_gap_words[stage].values()) >= 30
    },
    'jaccard_matrix': {f"{s1}_vs_{s2}": v for (s1, s2), v in jaccard_matrix.items() if s1 != s2}
        if 'jaccard_matrix' in dir() and jaccard_matrix else {},
    'vocab_differentiated': bool(vocab_differentiated),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "19_stage_operator_profiles.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Result written to {out_path}")
