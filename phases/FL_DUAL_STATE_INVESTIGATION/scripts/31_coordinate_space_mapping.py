"""
31_coordinate_space_mapping.py

Map what the FL pair coordinate axes actually represent.

The FL pair (LOW_stage, HIGH_stage) tags each line with two independent
state markers. Script 29 showed this grid carves vocabulary (3/4 checks).
But what do the axes MEAN?

For each dimension:
  1. What roles/prefixes/classes dominate at each stage?
  2. How does morphological complexity change?
  3. What specific FL MIDDLEs appear?
  4. What sections specialize where?
  5. What distinctive words characterize each position?

Goal: assign interpretive labels to each axis based on the evidence.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, kruskal

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

class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = class_data['token_to_class']
token_to_role = class_data['token_to_role']

# Build line tokens
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

# ============================================================
# Build per-line FL pair + gap token inventory
# ============================================================
lines_by_pair = defaultdict(list)  # pair -> list of line dicts
lines_by_low = defaultdict(list)   # low_stage -> list of line dicts
lines_by_high = defaultdict(list)  # high_stage -> list of line dicts

for line_key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 6:
        continue

    fl_info = []
    all_info = []
    for idx, t in enumerate(tokens):
        m = morph.extract(t.word)
        pos = idx / (n - 1) if n > 1 else 0.5
        mid = m.middle if m else None
        is_fl = mid is not None and mid in FL_STAGE_MAP

        mode = None
        stage = None
        fl_mid = None
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]
            fl_mid = mid

        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else 'NONE'
        suffix = m.suffix if m and m.suffix else 'NONE'
        word_len = len(t.word)
        n_morphemes = sum([
            1 if (m and m.articulator) else 0,
            1 if (m and m.prefix) else 0,
            1,  # middle always
            1 if (m and m.suffix) else 0,
        ]) if m else 1

        entry = {
            'word': t.word, 'idx': idx, 'is_fl': is_fl,
            'mode': mode, 'stage': stage, 'fl_mid': fl_mid,
            'class': cls, 'role': role, 'prefix': prefix,
            'suffix': suffix, 'word_len': word_len,
            'n_morphemes': n_morphemes,
        }
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]
    pair = (low_stage, high_stage)

    # Gap tokens
    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['idx'] > max_low_idx and t['idx'] < min_high_idx]

    # FL MIDDLEs used
    low_middles = [f['fl_mid'] for f in low_fls]
    high_middles = [f['fl_mid'] for f in high_fls]

    line_dict = {
        'pair': pair,
        'low_stage': low_stage,
        'high_stage': high_stage,
        'gap': gap,
        'low_middles': low_middles,
        'high_middles': high_middles,
        'n_tokens': n,
        'section': line_meta[line_key]['section'],
        'folio': line_meta[line_key]['folio'],
    }

    lines_by_pair[pair].append(line_dict)
    lines_by_low[low_stage].append(line_dict)
    lines_by_high[high_stage].append(line_dict)

# ============================================================
# AXIS 1: LOW dimension profile
# ============================================================
print("=" * 70)
print("AXIS 1: LOW DIMENSION (left bookend stage)")
print("=" * 70)

def profile_lines(lines_list, label):
    """Profile gap tokens from a set of lines."""
    roles = Counter()
    prefixes = Counter()
    suffixes = Counter()
    classes = Counter()
    words = Counter()
    lengths = []
    morphemes = []
    sections = Counter()

    for ld in lines_list:
        sections[ld['section']] += 1
        for t in ld['gap']:
            roles[t['role']] += 1
            prefixes[t['prefix']] += 1
            suffixes[t['suffix']] += 1
            if t['class']:
                classes[t['class']] += 1
            words[t['word']] += 1
            lengths.append(t['word_len'])
            morphemes.append(t['n_morphemes'])

    total = sum(roles.values())
    if total == 0:
        return None

    return {
        'n_lines': len(lines_list),
        'n_gap_tokens': total,
        'mean_word_len': round(float(np.mean(lengths)), 2) if lengths else 0,
        'mean_morphemes': round(float(np.mean(morphemes)), 2) if morphemes else 0,
        'role_pcts': {r: round(roles.get(r, 0) / total * 100, 1)
                      for r in ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR',
                                'CORE_CONTROL', 'AUXILIARY', 'UNKNOWN']},
        'top_prefixes': {p: round(prefixes.get(p, 0) / total * 100, 1)
                         for p in ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot', 'd', 's']},
        'top_suffixes': {s: round(suffixes.get(s, 0) / total * 100, 1)
                         for s in ['y', 'dy', 'NONE', 'n', 'ry', 'ly']},
        'section_pcts': {s: round(sections.get(s, 0) / len(lines_list) * 100, 1)
                         for s in sorted(sections.keys())},
        'top_words': words.most_common(8),
        'words_counter': words,
    }

# Profile each LOW stage
low_profiles = {}
print(f"\n  {'Stage':<10} {'Lines':>6} {'Tokens':>7} {'MeanLen':>8} {'Morph':>6}")
print(f"  {'-'*45}")
for stage in STAGES:
    if stage not in lines_by_low or len(lines_by_low[stage]) < 10:
        continue
    prof = profile_lines(lines_by_low[stage], stage)
    if prof:
        low_profiles[stage] = prof
        print(f"  {stage:<10} {prof['n_lines']:>6} {prof['n_gap_tokens']:>7} "
              f"{prof['mean_word_len']:>8.2f} {prof['mean_morphemes']:>6.2f}")

# Role gradient along LOW
print(f"\n  Role percentages along LOW dimension:")
print(f"  {'Stage':<10}", end='')
for r in ['ENERGY_OP', 'FREQ_OP', 'CORE_CTL', 'AUXIL', 'UNKNOWN']:
    print(f" {r:>9}", end='')
print()
print(f"  {'-'*60}")
role_keys = ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR', 'CORE_CONTROL', 'AUXILIARY', 'UNKNOWN']
role_short_map = {'ENERGY_OPERATOR': 'ENERGY_OP', 'FREQUENT_OPERATOR': 'FREQ_OP',
                  'CORE_CONTROL': 'CORE_CTL', 'AUXILIARY': 'AUXIL', 'UNKNOWN': 'UNKNOWN'}
for stage in STAGES:
    if stage not in low_profiles:
        continue
    prof = low_profiles[stage]
    print(f"  {stage:<10}", end='')
    for r in role_keys:
        print(f" {prof['role_pcts'].get(r, 0):>8.1f}%", end='')
    print()

# Prefix gradient along LOW
print(f"\n  Prefix percentages along LOW dimension:")
pfx_list = ['ch', 'sh', 'qo', 'NONE', 'ok', 'ot', 'd', 's']
print(f"  {'Stage':<10}", end='')
for p in pfx_list:
    print(f" {p:>6}", end='')
print()
print(f"  {'-'*65}")
for stage in STAGES:
    if stage not in low_profiles:
        continue
    prof = low_profiles[stage]
    print(f"  {stage:<10}", end='')
    for p in pfx_list:
        print(f" {prof['top_prefixes'].get(p, 0):>5.1f}%", end='')
    print()

# Section distribution along LOW
print(f"\n  Section distribution along LOW dimension:")
all_sections = sorted(set(s for p in low_profiles.values() for s in p['section_pcts']))
print(f"  {'Stage':<10}", end='')
for s in all_sections:
    print(f" {s:>5}", end='')
print()
print(f"  {'-'*50}")
for stage in STAGES:
    if stage not in low_profiles:
        continue
    prof = low_profiles[stage]
    print(f"  {stage:<10}", end='')
    for s in all_sections:
        print(f" {prof['section_pcts'].get(s, 0):>4.0f}%", end='')
    print()

# ============================================================
# AXIS 2: HIGH dimension profile
# ============================================================
print(f"\n{'='*70}")
print("AXIS 2: HIGH DIMENSION (right bookend stage)")
print(f"{'='*70}")

high_profiles = {}
print(f"\n  {'Stage':<10} {'Lines':>6} {'Tokens':>7} {'MeanLen':>8} {'Morph':>6}")
print(f"  {'-'*45}")
for stage in STAGES:
    if stage not in lines_by_high or len(lines_by_high[stage]) < 10:
        continue
    prof = profile_lines(lines_by_high[stage], stage)
    if prof:
        high_profiles[stage] = prof
        print(f"  {stage:<10} {prof['n_lines']:>6} {prof['n_gap_tokens']:>7} "
              f"{prof['mean_word_len']:>8.2f} {prof['mean_morphemes']:>6.2f}")

# Role gradient along HIGH
print(f"\n  Role percentages along HIGH dimension:")
print(f"  {'Stage':<10}", end='')
for r in ['ENERGY_OP', 'FREQ_OP', 'CORE_CTL', 'AUXIL', 'UNKNOWN']:
    print(f" {r:>9}", end='')
print()
print(f"  {'-'*60}")
for stage in STAGES:
    if stage not in high_profiles:
        continue
    prof = high_profiles[stage]
    print(f"  {stage:<10}", end='')
    for r in role_keys:
        print(f" {prof['role_pcts'].get(r, 0):>8.1f}%", end='')
    print()

# Prefix gradient along HIGH
print(f"\n  Prefix percentages along HIGH dimension:")
print(f"  {'Stage':<10}", end='')
for p in pfx_list:
    print(f" {p:>6}", end='')
print()
print(f"  {'-'*65}")
for stage in STAGES:
    if stage not in high_profiles:
        continue
    prof = high_profiles[stage]
    print(f"  {stage:<10}", end='')
    for p in pfx_list:
        print(f" {prof['top_prefixes'].get(p, 0):>5.1f}%", end='')
    print()

# Section distribution along HIGH
print(f"\n  Section distribution along HIGH dimension:")
all_sections_h = sorted(set(s for p in high_profiles.values() for s in p['section_pcts']))
print(f"  {'Stage':<10}", end='')
for s in all_sections_h:
    print(f" {s:>5}", end='')
print()
print(f"  {'-'*50}")
for stage in STAGES:
    if stage not in high_profiles:
        continue
    prof = high_profiles[stage]
    print(f"  {stage:<10}", end='')
    for s in all_sections_h:
        print(f" {prof['section_pcts'].get(s, 0):>4.0f}%", end='')
    print()

# ============================================================
# Correlation tests: what changes systematically along each axis?
# ============================================================
print(f"\n{'='*70}")
print("GRADIENT TESTS: What changes systematically along each axis?")
print(f"{'='*70}")

# Build per-pair data for correlation
MIN_PAIR_LINES = 15
pair_data = {}
for pair, lines_list in lines_by_pair.items():
    if len(lines_list) < MIN_PAIR_LINES:
        continue
    prof = profile_lines(lines_list, f"{pair[0]}>{pair[1]}")
    if prof:
        pair_data[pair] = prof

common_pairs = sorted(pair_data.keys(), key=lambda p: (STAGE_ORDER[p[0]], STAGE_ORDER[p[1]]))
print(f"\n  Common pairs (n>={MIN_PAIR_LINES}): {len(common_pairs)}")

# Compute gradients
metrics = {}
for pair in common_pairs:
    prof = pair_data[pair]
    metrics[pair] = {
        'low_ord': STAGE_ORDER[pair[0]],
        'high_ord': STAGE_ORDER[pair[1]],
        'mean_word_len': prof['mean_word_len'],
        'mean_morphemes': prof['mean_morphemes'],
        'qo_pct': prof['top_prefixes'].get('qo', 0),
        'ch_pct': prof['top_prefixes'].get('ch', 0),
        'sh_pct': prof['top_prefixes'].get('sh', 0),
        'none_pct': prof['top_prefixes'].get('NONE', 0),
        'ok_pct': prof['top_prefixes'].get('ok', 0),
        'ot_pct': prof['top_prefixes'].get('ot', 0),
        'd_pct': prof['top_prefixes'].get('d', 0),
        's_pct': prof['top_prefixes'].get('s', 0),
        'energy_pct': prof['role_pcts'].get('ENERGY_OPERATOR', 0),
        'freq_pct': prof['role_pcts'].get('FREQUENT_OPERATOR', 0),
        'core_pct': prof['role_pcts'].get('CORE_CONTROL', 0),
        'aux_pct': prof['role_pcts'].get('AUXILIARY', 0),
        'unknown_pct': prof['role_pcts'].get('UNKNOWN', 0),
        'y_sfx': prof['top_suffixes'].get('y', 0),
        'dy_sfx': prof['top_suffixes'].get('dy', 0),
        'none_sfx': prof['top_suffixes'].get('NONE', 0),
        'n_sfx': prof['top_suffixes'].get('n', 0),
    }

metric_names = [
    'mean_word_len', 'mean_morphemes',
    'qo_pct', 'ch_pct', 'sh_pct', 'none_pct', 'ok_pct', 'ot_pct', 'd_pct', 's_pct',
    'energy_pct', 'freq_pct', 'core_pct', 'aux_pct', 'unknown_pct',
    'y_sfx', 'dy_sfx', 'none_sfx', 'n_sfx',
]

print(f"\n  Spearman correlations with LOW and HIGH stage ordinals:")
print(f"  {'Metric':<18} {'LOW rho':>8} {'p':>8} {'HIGH rho':>8} {'p':>8}")
print(f"  {'-'*55}")

low_correlations = {}
high_correlations = {}

for mn in metric_names:
    vals = [metrics[p][mn] for p in common_pairs]
    low_ords = [metrics[p]['low_ord'] for p in common_pairs]
    high_ords = [metrics[p]['high_ord'] for p in common_pairs]

    rho_l, p_l = spearmanr(low_ords, vals)
    rho_h, p_h = spearmanr(high_ords, vals)

    sig_l = '*' if p_l < 0.05 else (' ' if p_l < 0.10 else ' ')
    sig_h = '*' if p_h < 0.05 else (' ' if p_h < 0.10 else ' ')

    low_correlations[mn] = (rho_l, p_l)
    high_correlations[mn] = (rho_h, p_h)

    print(f"  {mn:<18} {rho_l:>+7.3f}{sig_l} {p_l:>7.3f}  {rho_h:>+7.3f}{sig_h} {p_h:>7.3f}")

# ============================================================
# FL MIDDLE inventory per axis position
# ============================================================
print(f"\n{'='*70}")
print("FL MIDDLE INVENTORY PER AXIS POSITION")
print(f"{'='*70}")

# What FL MIDDLEs serve as LOW bookend at each stage?
print(f"\n  LOW bookend FL MIDDLEs by stage:")
low_mid_inventory = defaultdict(Counter)
high_mid_inventory = defaultdict(Counter)
for pair, lines_list in lines_by_pair.items():
    for ld in lines_list:
        for m in ld['low_middles']:
            low_mid_inventory[pair[0]][m] += 1
        for m in ld['high_middles']:
            high_mid_inventory[pair[1]][m] += 1

for stage in STAGES:
    if stage not in low_mid_inventory:
        continue
    total = sum(low_mid_inventory[stage].values())
    top = low_mid_inventory[stage].most_common(5)
    top_str = ', '.join(f"{m}({c/total*100:.0f}%)" for m, c in top)
    print(f"    {stage:<10} (n={total:>4}): {top_str}")

print(f"\n  HIGH bookend FL MIDDLEs by stage:")
for stage in STAGES:
    if stage not in high_mid_inventory:
        continue
    total = sum(high_mid_inventory[stage].values())
    top = high_mid_inventory[stage].most_common(5)
    top_str = ', '.join(f"{m}({c/total*100:.0f}%)" for m, c in top)
    print(f"    {stage:<10} (n={total:>4}): {top_str}")

# ============================================================
# Distinctive words at axis extremes
# ============================================================
print(f"\n{'='*70}")
print("DISTINCTIVE WORDS AT AXIS EXTREMES")
print(f"{'='*70}")

# Total corpus for enrichment
total_words = Counter()
for pair in common_pairs:
    total_words += pair_data[pair]['words_counter']
total_count = sum(total_words.values())

def show_enriched(label, words_counter, n_show=10):
    """Show top enriched words vs corpus baseline."""
    pair_total = sum(words_counter.values())
    if pair_total < 30:
        print(f"  {label}: too few tokens ({pair_total})")
        return []
    enriched = []
    for w, count in words_counter.items():
        if count < 3:
            continue
        pair_pct = count / pair_total
        baseline_pct = total_words[w] / total_count
        if baseline_pct > 0:
            enrichment = pair_pct / baseline_pct
            if enrichment > 1.5:
                enriched.append((w, count, enrichment, pair_pct * 100))
    enriched.sort(key=lambda x: -x[2])
    top = enriched[:n_show]
    if top:
        words_str = ', '.join(f"{w}({e:.1f}x)" for w, c, e, p in top)
        print(f"  {label}: {words_str}")
    else:
        print(f"  {label}: no significantly enriched words")
    return enriched

# LOW extremes
print(f"\n  LOW=INITIAL (earliest stage):")
if 'INITIAL' in low_profiles:
    show_enriched("LOW=INITIAL", low_profiles['INITIAL']['words_counter'])
print(f"\n  LOW=LATE (mid-late stage):")
if 'LATE' in low_profiles:
    show_enriched("LOW=LATE", low_profiles['LATE']['words_counter'])
print(f"\n  LOW=TERMINAL (latest stage):")
if 'TERMINAL' in low_profiles:
    show_enriched("LOW=TERMINAL", low_profiles['TERMINAL']['words_counter'])

# HIGH extremes
print(f"\n  HIGH=LATE:")
if 'LATE' in high_profiles:
    show_enriched("HIGH=LATE", high_profiles['LATE']['words_counter'])
print(f"\n  HIGH=FINAL:")
if 'FINAL' in high_profiles:
    show_enriched("HIGH=FINAL", high_profiles['FINAL']['words_counter'])
print(f"\n  HIGH=TERMINAL:")
if 'TERMINAL' in high_profiles:
    show_enriched("HIGH=TERMINAL", high_profiles['TERMINAL']['words_counter'])

# ============================================================
# Line-level properties along each axis
# ============================================================
print(f"\n{'='*70}")
print("LINE-LEVEL PROPERTIES PER AXIS")
print(f"{'='*70}")

print(f"\n  Mean line length (tokens) along LOW dimension:")
for stage in STAGES:
    if stage not in lines_by_low or len(lines_by_low[stage]) < 10:
        continue
    lens = [ld['n_tokens'] for ld in lines_by_low[stage]]
    print(f"    {stage:<10}: {np.mean(lens):.1f} tokens (n={len(lens)} lines)")

print(f"\n  Mean line length (tokens) along HIGH dimension:")
for stage in STAGES:
    if stage not in lines_by_high or len(lines_by_high[stage]) < 10:
        continue
    lens = [ld['n_tokens'] for ld in lines_by_high[stage]]
    print(f"    {stage:<10}: {np.mean(lens):.1f} tokens (n={len(lens)} lines)")

# Mean gap size (how much content between bookends)
print(f"\n  Mean gap size (non-FL tokens between bookends) along LOW:")
for stage in STAGES:
    if stage not in lines_by_low or len(lines_by_low[stage]) < 10:
        continue
    gaps = [len(ld['gap']) for ld in lines_by_low[stage]]
    print(f"    {stage:<10}: {np.mean(gaps):.1f} gap tokens")

print(f"\n  Mean gap size along HIGH:")
for stage in STAGES:
    if stage not in lines_by_high or len(lines_by_high[stage]) < 10:
        continue
    gaps = [len(ld['gap']) for ld in lines_by_high[stage]]
    print(f"    {stage:<10}: {np.mean(gaps):.1f} gap tokens")

# ============================================================
# CROSS-AXIS: Full grid view
# ============================================================
print(f"\n{'='*70}")
print("FULL GRID VIEW: PAIR (LOW x HIGH)")
print(f"{'='*70}")

print(f"\n  Lines per pair:")
print(f"  {'':>10}", end='')
for h in STAGES:
    print(f" {h[:4]:>6}", end='')
print()
print(f"  {'-'*50}")
for l in STAGES:
    print(f"  {l:<10}", end='')
    for h in STAGES:
        pair = (l, h)
        n = len(lines_by_pair.get(pair, []))
        if n > 0:
            print(f" {n:>6}", end='')
        else:
            print(f" {'--':>6}", end='')
    print()

# Dominant prefix per cell
print(f"\n  Dominant non-NONE prefix per pair:")
print(f"  {'':>10}", end='')
for h in STAGES:
    print(f" {h[:4]:>6}", end='')
print()
print(f"  {'-'*50}")
for l in STAGES:
    print(f"  {l:<10}", end='')
    for h in STAGES:
        pair = (l, h)
        if pair in pair_data:
            pfx = pair_data[pair]['top_prefixes']
            # Find dominant non-NONE prefix
            best = max((v, k) for k, v in pfx.items() if k != 'NONE')
            print(f" {best[1]:>6}", end='')
        else:
            print(f" {'--':>6}", end='')
    print()

# Dominant role per cell
print(f"\n  Dominant role per pair:")
print(f"  {'':>10}", end='')
for h in STAGES:
    print(f" {h[:4]:>6}", end='')
print()
print(f"  {'-'*50}")
role_abbrev = {'ENERGY_OPERATOR': 'EN', 'FREQUENT_OPERATOR': 'FQ',
               'CORE_CONTROL': 'CC', 'AUXILIARY': 'AX', 'UNKNOWN': 'UK'}
for l in STAGES:
    print(f"  {l:<10}", end='')
    for h in STAGES:
        pair = (l, h)
        if pair in pair_data:
            rp = pair_data[pair]['role_pcts']
            best = max((v, k) for k, v in rp.items())
            print(f" {role_abbrev.get(best[1], '??'):>6}", end='')
        else:
            print(f" {'--':>6}", end='')
    print()

# ============================================================
# AXIS INTERPRETATION
# ============================================================
print(f"\n{'='*70}")
print("AXIS INTERPRETATION")
print(f"{'='*70}")

# Summarize significant gradients
print(f"\n  Significant LOW-axis gradients (p<0.05):")
sig_low = [(mn, rho, p) for mn, (rho, p) in low_correlations.items() if p < 0.05]
sig_low.sort(key=lambda x: -abs(x[1]))
for mn, rho, p in sig_low:
    direction = "INCREASES" if rho > 0 else "DECREASES"
    print(f"    {mn:<18}: {direction} (rho={rho:+.3f}, p={p:.4f})")

print(f"\n  Significant HIGH-axis gradients (p<0.05):")
sig_high = [(mn, rho, p) for mn, (rho, p) in high_correlations.items() if p < 0.05]
sig_high.sort(key=lambda x: -abs(x[1]))
for mn, rho, p in sig_high:
    direction = "INCREASES" if rho > 0 else "DECREASES"
    print(f"    {mn:<18}: {direction} (rho={rho:+.3f}, p={p:.4f})")

# Number of significant correlations per axis
n_sig_low = len(sig_low)
n_sig_high = len(sig_high)

# Strongest correlations
best_low_pos = max(sig_low, key=lambda x: x[1]) if [s for s in sig_low if s[1] > 0] else None
best_low_neg = min(sig_low, key=lambda x: x[1]) if [s for s in sig_low if s[1] < 0] else None
best_high_pos = max(sig_high, key=lambda x: x[1]) if [s for s in sig_high if s[1] > 0] else None
best_high_neg = min(sig_high, key=lambda x: x[1]) if [s for s in sig_high if s[1] < 0] else None

low_label = "UNKNOWN"
high_label = "UNKNOWN"

# Interpret LOW axis
if best_low_pos and best_low_neg:
    print(f"\n  LOW axis interpretation:")
    print(f"    Moving LOW INITIAL -> TERMINAL:")
    print(f"      Strongest increase: {best_low_pos[0]} (rho={best_low_pos[1]:+.3f})")
    print(f"      Strongest decrease: {best_low_neg[0]} (rho={best_low_neg[1]:+.3f})")

    # Heuristic labeling
    increases = set(mn for mn, rho, p in sig_low if rho > 0)
    decreases = set(mn for mn, rho, p in sig_low if rho < 0)

    if 'qo_pct' in increases:
        low_label = "ACTION_INTENSITY"
    elif 'energy_pct' in increases:
        low_label = "ENERGY_LEVEL"
    elif 'aux_pct' in decreases and 'unknown_pct' in increases:
        low_label = "AUTONOMY_GRADIENT"

# Interpret HIGH axis
if best_high_pos and best_high_neg:
    print(f"\n  HIGH axis interpretation:")
    print(f"    Moving HIGH INITIAL -> TERMINAL:")
    print(f"      Strongest increase: {best_high_pos[0]} (rho={best_high_pos[1]:+.3f})")
    print(f"      Strongest decrease: {best_high_neg[0]} (rho={best_high_neg[1]:+.3f})")

    increases_h = set(mn for mn, rho, p in sig_high if rho > 0)
    decreases_h = set(mn for mn, rho, p in sig_high if rho < 0)

    if 'core_pct' in decreases_h:
        high_label = "CONTROL_RELEASE"
    elif 'sh_pct' in increases_h:
        high_label = "MONITORING_INTENSITY"
    elif 'none_pct' in increases_h:
        high_label = "SIMPLIFICATION"

print(f"\n  PROPOSED AXIS LABELS:")
print(f"    LOW  axis: {low_label}")
print(f"    HIGH axis: {high_label}")

# ============================================================
# SAVE RESULT
# ============================================================
result = {
    'n_common_pairs': len(common_pairs),
    'n_lines_analyzed': sum(len(lines_by_pair[p]) for p in common_pairs),
    'low_axis': {
        'n_significant_gradients': n_sig_low,
        'significant_metrics': {mn: {'rho': round(float(rho), 3), 'p': round(float(p), 4)}
                                 for mn, rho, p in sig_low},
        'proposed_label': low_label,
    },
    'high_axis': {
        'n_significant_gradients': n_sig_high,
        'significant_metrics': {mn: {'rho': round(float(rho), 3), 'p': round(float(p), 4)}
                                 for mn, rho, p in sig_high},
        'proposed_label': high_label,
    },
    'low_profiles': {
        stage: {
            'n_lines': prof['n_lines'],
            'n_gap_tokens': prof['n_gap_tokens'],
            'mean_word_len': prof['mean_word_len'],
            'mean_morphemes': prof['mean_morphemes'],
            'role_pcts': prof['role_pcts'],
            'top_prefixes': prof['top_prefixes'],
            'section_pcts': prof['section_pcts'],
            'top_words': [(w, c) for w, c in prof['top_words']],
        }
        for stage, prof in low_profiles.items()
    },
    'high_profiles': {
        stage: {
            'n_lines': prof['n_lines'],
            'n_gap_tokens': prof['n_gap_tokens'],
            'mean_word_len': prof['mean_word_len'],
            'mean_morphemes': prof['mean_morphemes'],
            'role_pcts': prof['role_pcts'],
            'top_prefixes': prof['top_prefixes'],
            'section_pcts': prof['section_pcts'],
            'top_words': [(w, c) for w, c in prof['top_words']],
        }
        for stage, prof in high_profiles.items()
    },
    'grid_lines': {
        f"{l}>{h}": len(lines_by_pair.get((l, h), []))
        for l in STAGES for h in STAGES
        if len(lines_by_pair.get((l, h), [])) > 0
    },
}

out_path = Path(__file__).resolve().parent.parent / "results" / "31_coordinate_space_mapping.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
