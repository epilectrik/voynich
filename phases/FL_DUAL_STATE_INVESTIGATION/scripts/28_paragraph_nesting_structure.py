"""
28_paragraph_nesting_structure.py

Revisit paragraph structure through the 7-layer nesting lens.
Do paragraphs have internal structure visible through the layers?
  - Do first/last lines differ from middle lines?
  - Is preamble more common at paragraph start, coda at paragraph end?
  - Do FL pairs show any paragraph-level pattern?
  - Is there a "paragraph envelope"?
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import chi2_contingency, spearmanr

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

tx = Transcript()
morph = Morphology()
MIN_N = 50

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

line_tokens = defaultdict(list)
for t in tx.currier_b():
    line_tokens[(t.folio, t.line)].append(t)

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

# ============================================================
# Build line profiles with full 7-layer annotation
# ============================================================
def analyze_line(tokens):
    """Return full line profile or None if insufficient FL structure."""
    n = len(tokens)
    if n < 4:
        return None

    fl_info = []
    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        stage = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]

        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else 'NONE'
        entry = {'word': t.word, 'idx': idx, 'pos': pos, 'is_fl': is_fl,
                 'mode': mode, 'stage': stage, 'class': cls, 'role': role,
                 'prefix': prefix}
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']

    # Lines without both modes
    has_nesting = bool(low_fls) and bool(high_fls)

    pair = None
    has_preamble = False
    has_coda = False
    n_gap = 0

    if has_nesting:
        max_low_idx = max(f['idx'] for f in low_fls)
        min_high_idx = min(f['idx'] for f in high_fls)
        gap = [t for t in all_info if not t['is_fl']
               and t['idx'] > max_low_idx and t['idx'] < min_high_idx]
        n_gap = len(gap)

        low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
        high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
        pair = (low_stage, high_stage)

        min_fl_idx = min(f['idx'] for f in low_fls)
        max_fl_idx = max(f['idx'] for f in high_fls)
        pre = [t for t in all_info if not t['is_fl'] and t['idx'] < min_fl_idx]
        post = [t for t in all_info if not t['is_fl'] and t['idx'] > max_fl_idx]
        has_preamble = len(pre) > 0
        has_coda = len(post) > 0

    # Role summary of non-FL tokens
    non_fl = [t for t in all_info if not t['is_fl']]
    role_summary = Counter(t['role'] for t in non_fl)

    return {
        'n_tokens': n,
        'n_fl': len(fl_info),
        'has_nesting': has_nesting,
        'pair': pair,
        'has_preamble': has_preamble,
        'has_coda': has_coda,
        'n_gap': n_gap,
        'role_summary': role_summary,
        'non_fl_words': [t['word'] for t in non_fl],
        'non_fl_prefixes': [t['prefix'] for t in non_fl],
    }

# Build paragraph structure using par_initial/par_final markers
# Group consecutive lines into paragraphs
paragraph_map = {}  # (folio, para_idx) -> [line_keys]
current_para_lines = []
current_folio = None
para_idx = 0

# Get unique line keys in order, with par boundary info
line_par_info = {}  # line_key -> {'par_initial': bool, 'par_final': bool}
for t in tx.currier_b():
    key = (t.folio, t.line)
    if key not in line_par_info:
        line_par_info[key] = {'par_initial': False, 'par_final': False}
    if t.par_initial:
        line_par_info[key]['par_initial'] = True
    if t.par_final:
        line_par_info[key]['par_final'] = True

# Walk through lines in order, split on par_initial
ordered_keys = sorted(line_tokens.keys())
current_para = []
current_folio = None
para_idx = 0

for key in ordered_keys:
    folio = key[0]
    if folio != current_folio:
        # New folio, save current para
        if current_para:
            paragraph_map[(current_folio, para_idx)] = current_para
        current_para = [key]
        current_folio = folio
        para_idx = 0
    elif key in line_par_info and line_par_info[key]['par_initial'] and current_para:
        # Paragraph boundary
        paragraph_map[(current_folio, para_idx)] = current_para
        para_idx += 1
        current_para = [key]
    else:
        current_para.append(key)

# Don't forget last paragraph
if current_para and current_folio:
    paragraph_map[(current_folio, para_idx)] = current_para

# Build paragraph profiles
paragraphs = []
for para_key in sorted(paragraph_map.keys()):
    line_keys = paragraph_map[para_key]
    if len(line_keys) < 3:
        continue

    line_profiles = []
    for lk in line_keys:
        if lk in line_tokens:
            profile = analyze_line(line_tokens[lk])
            if profile:
                profile['line_key'] = lk
                line_profiles.append(profile)

    if len(line_profiles) < 3:
        continue

    paragraphs.append({
        'key': para_key,
        'n_lines': len(line_profiles),
        'lines': line_profiles,
    })

print(f"Paragraphs with 3+ profiled lines: {len(paragraphs)}")
print(f"Total profiled lines: {sum(p['n_lines'] for p in paragraphs)}")

# ============================================================
# TEST 1: Preamble/Coda by paragraph position
# ============================================================
print(f"\n{'='*60}")
print("TEST 1: PREAMBLE/CODA BY PARAGRAPH POSITION")
print(f"{'='*60}")

# For each line, classify its paragraph position: FIRST, MIDDLE, LAST
pos_preamble = {'FIRST': [0, 0], 'MIDDLE': [0, 0], 'LAST': [0, 0]}
pos_coda = {'FIRST': [0, 0], 'MIDDLE': [0, 0], 'LAST': [0, 0]}
pos_nesting = {'FIRST': [0, 0], 'MIDDLE': [0, 0], 'LAST': [0, 0]}

for para in paragraphs:
    for i, lp in enumerate(para['lines']):
        if i == 0:
            pos = 'FIRST'
        elif i == len(para['lines']) - 1:
            pos = 'LAST'
        else:
            pos = 'MIDDLE'

        if lp['has_nesting']:
            pos_nesting[pos][0] += 1
            if lp['has_preamble']:
                pos_preamble[pos][0] += 1
            if lp['has_coda']:
                pos_coda[pos][0] += 1
        pos_nesting[pos][1] += 1
        pos_preamble[pos][1] += 1
        pos_coda[pos][1] += 1

print(f"\n  {'Position':>10} {'Has nesting':>12} {'Has preamble':>13} {'Has coda':>10}")
print(f"  {'-'*48}")
for pos in ['FIRST', 'MIDDLE', 'LAST']:
    nest_pct = pos_nesting[pos][0] / pos_nesting[pos][1] * 100 if pos_nesting[pos][1] > 0 else 0
    pre_pct = pos_preamble[pos][0] / pos_preamble[pos][1] * 100 if pos_preamble[pos][1] > 0 else 0
    coda_pct = pos_coda[pos][0] / pos_coda[pos][1] * 100 if pos_coda[pos][1] > 0 else 0
    print(f"  {pos:>10} {nest_pct:>11.1f}% {pre_pct:>12.1f}% {coda_pct:>9.1f}%")

# ============================================================
# TEST 2: Line length by paragraph position
# ============================================================
print(f"\n{'='*60}")
print("TEST 2: LINE CHARACTERISTICS BY PARAGRAPH POSITION")
print(f"{'='*60}")

pos_lengths = {'FIRST': [], 'MIDDLE': [], 'LAST': []}
pos_n_fl = {'FIRST': [], 'MIDDLE': [], 'LAST': []}
pos_n_gap = {'FIRST': [], 'MIDDLE': [], 'LAST': []}

for para in paragraphs:
    for i, lp in enumerate(para['lines']):
        if i == 0:
            pos = 'FIRST'
        elif i == len(para['lines']) - 1:
            pos = 'LAST'
        else:
            pos = 'MIDDLE'
        pos_lengths[pos].append(lp['n_tokens'])
        pos_n_fl[pos].append(lp['n_fl'])
        pos_n_gap[pos].append(lp['n_gap'])

print(f"\n  {'Position':>10} {'mean_len':>9} {'mean_FL':>8} {'mean_gap':>9}")
print(f"  {'-'*40}")
for pos in ['FIRST', 'MIDDLE', 'LAST']:
    print(f"  {pos:>10} {np.mean(pos_lengths[pos]):>9.1f} "
          f"{np.mean(pos_n_fl[pos]):>8.1f} {np.mean(pos_n_gap[pos]):>9.1f}")

# ============================================================
# TEST 3: Role distribution by paragraph position
# ============================================================
print(f"\n{'='*60}")
print("TEST 3: ROLE DISTRIBUTION BY PARAGRAPH POSITION")
print(f"{'='*60}")

roles = ['ENERGY_OPERATOR', 'UNKNOWN', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL']

for pos_label in ['FIRST', 'MIDDLE', 'LAST']:
    role_total = Counter()
    for para in paragraphs:
        for i, lp in enumerate(para['lines']):
            if i == 0:
                pos = 'FIRST'
            elif i == len(para['lines']) - 1:
                pos = 'LAST'
            else:
                pos = 'MIDDLE'
            if pos == pos_label:
                role_total += lp['role_summary']

    total = sum(role_total.values())
    if total == 0:
        continue
    role_str = '  '.join(f"{r[:4]}={role_total.get(r,0)/total*100:.0f}%"
                         for r in roles)
    print(f"  {pos_label:>8}: {role_str}  (n={total})")

# ============================================================
# TEST 4: FL pair by paragraph position
# ============================================================
print(f"\n{'='*60}")
print("TEST 4: FL PAIR BY PARAGRAPH POSITION")
print(f"{'='*60}")

pos_pairs = {'FIRST': [], 'MIDDLE': [], 'LAST': []}
for para in paragraphs:
    for i, lp in enumerate(para['lines']):
        if i == 0:
            pos = 'FIRST'
        elif i == len(para['lines']) - 1:
            pos = 'LAST'
        else:
            pos = 'MIDDLE'
        if lp['pair']:
            pos_pairs[pos].append(lp['pair'])

for pos_label in ['FIRST', 'MIDDLE', 'LAST']:
    pairs = pos_pairs[pos_label]
    if not pairs:
        continue
    pair_counts = Counter(pairs)
    total = len(pairs)
    top5 = pair_counts.most_common(5)
    top5_str = ', '.join(f"{p[0][:4]}>{p[1][:4]}({c/total*100:.0f}%)"
                         for p, c in top5)
    print(f"  {pos_label:>8} (n={total}): {top5_str}")

# Chi-squared: position x pair
all_pairs_set = set()
for pairs in pos_pairs.values():
    all_pairs_set.update(pairs)
common_pairs = [p for p, c in Counter(
    pos_pairs['FIRST'] + pos_pairs['MIDDLE'] + pos_pairs['LAST']
).most_common() if c >= 10]

if len(common_pairs) >= 2:
    table_rows = []
    for pos_label in ['FIRST', 'MIDDLE', 'LAST']:
        pair_counts = Counter(pos_pairs[pos_label])
        table_rows.append([pair_counts.get(p, 0) for p in common_pairs])

    table = np.array(table_rows)
    col_mask = table.sum(axis=0) > 0
    table = table[:, col_mask]
    if table.shape[0] >= 2 and table.shape[1] >= 2:
        chi2, p_val, dof, _ = chi2_contingency(table)
        v = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))
        print(f"\n  Position x Pair: chi2={chi2:.1f}, p={p_val:.2e}, Cramer's V={v:.3f}")
        pair_position_v = v
    else:
        pair_position_v = 0
else:
    pair_position_v = 0

# ============================================================
# TEST 5: Do first and last lines in a paragraph share FL pair?
# ============================================================
print(f"\n{'='*60}")
print("TEST 5: FIRST-LAST PAIR CONSISTENCY")
print(f"{'='*60}")

same_pair = 0
diff_pair = 0
same_low = 0
same_high = 0
total_tested = 0

for para in paragraphs:
    first = para['lines'][0]
    last = para['lines'][-1]
    if first['pair'] and last['pair']:
        total_tested += 1
        if first['pair'] == last['pair']:
            same_pair += 1
        else:
            diff_pair += 1
        if first['pair'][0] == last['pair'][0]:
            same_low += 1
        if first['pair'][1] == last['pair'][1]:
            same_high += 1

if total_tested > 0:
    print(f"  Same pair (first=last): {same_pair}/{total_tested} ({same_pair/total_tested*100:.1f}%)")
    print(f"  Same LOW stage: {same_low}/{total_tested} ({same_low/total_tested*100:.1f}%)")
    print(f"  Same HIGH stage: {same_high}/{total_tested} ({same_high/total_tested*100:.1f}%)")

    # Expected by chance?
    all_pairs = [lp['pair'] for para in paragraphs for lp in para['lines'] if lp['pair']]
    pair_freq = Counter(all_pairs)
    total_all = len(all_pairs)
    expected_same = sum((c/total_all)**2 for c in pair_freq.values())
    print(f"  Expected same-pair by chance: {expected_same*100:.1f}%")
    print(f"  Observed/Expected: {(same_pair/total_tested)/expected_same:.2f}x")

# ============================================================
# TEST 6: Within-paragraph pair diversity
# ============================================================
print(f"\n{'='*60}")
print("TEST 6: WITHIN-PARAGRAPH PAIR DIVERSITY")
print(f"{'='*60}")

para_diversities = []
para_sizes = []
for para in paragraphs:
    pairs = [lp['pair'] for lp in para['lines'] if lp['pair']]
    if len(pairs) >= 3:
        unique = len(set(pairs))
        total = len(pairs)
        diversity = unique / total
        para_diversities.append(diversity)
        para_sizes.append(total)

print(f"  Mean pair diversity (unique/total): {np.mean(para_diversities):.3f}")
print(f"  Median pair diversity: {np.median(para_diversities):.3f}")
print(f"  Mean paragraph size: {np.mean(para_sizes):.1f} paired lines")

# How many paragraphs are dominated by a single pair?
single_pair_paras = sum(1 for d in para_diversities if d <= 0.4)
print(f"  Paragraphs with dominant pair (diversity<=0.4): "
      f"{single_pair_paras}/{len(para_diversities)} ({single_pair_paras/len(para_diversities)*100:.1f}%)")

# ============================================================
# TEST 7: Vocabulary overlap within paragraphs
# ============================================================
print(f"\n{'='*60}")
print("TEST 7: VOCABULARY OVERLAP WITHIN PARAGRAPHS")
print(f"{'='*60}")

# Within-paragraph Jaccard vs between-paragraph Jaccard
within_jaccards = []
for para in paragraphs:
    word_sets = [set(lp['non_fl_words']) for lp in para['lines']]
    for i in range(len(word_sets)):
        for j in range(i + 1, len(word_sets)):
            inter = len(word_sets[i] & word_sets[j])
            union = len(word_sets[i] | word_sets[j])
            if union > 0:
                within_jaccards.append(inter / union)

# Between: compare lines from different paragraphs
import random
random.seed(42)
between_jaccards = []
all_word_sets = [(para['key'], set(lp['non_fl_words']))
                 for para in paragraphs for lp in para['lines']]

for _ in range(min(5000, len(within_jaccards))):
    i, j = random.sample(range(len(all_word_sets)), 2)
    if all_word_sets[i][0] != all_word_sets[j][0]:
        s1, s2 = all_word_sets[i][1], all_word_sets[j][1]
        union = len(s1 | s2)
        if union > 0:
            between_jaccards.append(len(s1 & s2) / union)

within_mean = np.mean(within_jaccards)
between_mean = np.mean(between_jaccards)
lift = within_mean / between_mean if between_mean > 0 else 0

print(f"  Within-paragraph Jaccard: {within_mean:.4f}")
print(f"  Between-paragraph Jaccard: {between_mean:.4f}")
print(f"  Lift: {lift:.2f}x")

# ============================================================
# TEST 8: Prefix pattern by paragraph position
# ============================================================
print(f"\n{'='*60}")
print("TEST 8: PREFIX PROFILE BY PARAGRAPH POSITION")
print(f"{'='*60}")

top_pfx = ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot']

for pos_label in ['FIRST', 'MIDDLE', 'LAST']:
    pfx_total = Counter()
    for para in paragraphs:
        for i, lp in enumerate(para['lines']):
            if i == 0:
                pos = 'FIRST'
            elif i == len(para['lines']) - 1:
                pos = 'LAST'
            else:
                pos = 'MIDDLE'
            if pos == pos_label:
                pfx_total.update(lp['non_fl_prefixes'])

    total = sum(pfx_total.values())
    if total == 0:
        continue
    pfx_str = '  '.join(f"{p}={pfx_total.get(p,0)/total*100:.0f}%"
                        for p in top_pfx)
    print(f"  {pos_label:>8}: {pfx_str}")

# ============================================================
# Verdict
# ============================================================
print(f"\n{'='*60}")
print("VERDICT")
print(f"{'='*60}")

# Check structural signals
preamble_first_enriched = (pos_preamble['FIRST'][0] / max(pos_preamble['FIRST'][1], 1) >
                           pos_preamble['MIDDLE'][0] / max(pos_preamble['MIDDLE'][1], 1) * 1.1)
coda_last_enriched = (pos_coda['LAST'][0] / max(pos_coda['LAST'][1], 1) >
                      pos_coda['MIDDLE'][0] / max(pos_coda['MIDDLE'][1], 1) * 1.1)
pair_varies_by_position = pair_position_v > 0.08
vocab_coherence = lift > 1.2
first_last_match = (same_pair / total_tested > expected_same * 1.5) if total_tested > 0 else False
low_diversity = np.mean(para_diversities) < 0.7

signals = {
    'preamble_first_enriched': preamble_first_enriched,
    'coda_last_enriched': coda_last_enriched,
    'pair_varies_by_position': pair_varies_by_position,
    'vocab_coherence': vocab_coherence,
    'first_last_pair_match': first_last_match,
    'low_pair_diversity': low_diversity,
}

n_signals = sum(signals.values())
print(f"  Structural signals ({n_signals}/6):")
for name, val in signals.items():
    print(f"    {name:>30}: {'YES' if val else 'NO'}")

if n_signals >= 4:
    verdict = "STRUCTURED_PARAGRAPH"
    explanation = "Paragraphs show internal structure: position-dependent layers and pair coherence"
elif n_signals >= 2:
    verdict = "WEAKLY_STRUCTURED"
    explanation = "Some paragraph-level organization but no strong internal grammar"
else:
    verdict = "FLAT_PARAGRAPH"
    explanation = "Paragraphs are loose collections of lines with no internal structure"

print(f"\n  VERDICT: {verdict}")
print(f"  {explanation}")

# Save
result = {
    'n_paragraphs': len(paragraphs),
    'preamble_rates': {pos: pos_preamble[pos][0] / max(pos_preamble[pos][1], 1)
                       for pos in ['FIRST', 'MIDDLE', 'LAST']},
    'coda_rates': {pos: pos_coda[pos][0] / max(pos_coda[pos][1], 1)
                   for pos in ['FIRST', 'MIDDLE', 'LAST']},
    'pair_position_cramers_v': round(float(pair_position_v), 3),
    'first_last_same_pair': round(same_pair / total_tested, 3) if total_tested > 0 else None,
    'expected_same_pair': round(float(expected_same), 3),
    'within_para_jaccard': round(float(within_mean), 4),
    'between_para_jaccard': round(float(between_mean), 4),
    'jaccard_lift': round(float(lift), 2),
    'mean_pair_diversity': round(float(np.mean(para_diversities)), 3),
    'signals': {k: bool(v) for k, v in signals.items()},
    'n_signals': int(n_signals),
    'verdict': verdict,
    'explanation': explanation,
}

out_path = Path(__file__).resolve().parent.parent / "results" / "28_paragraph_nesting_structure.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
