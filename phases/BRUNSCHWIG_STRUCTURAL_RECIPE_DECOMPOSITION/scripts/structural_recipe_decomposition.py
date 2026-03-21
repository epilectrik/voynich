"""
Phase 617: Brunschwig Structural Recipe Decomposition

Tests whether Brunschwig recipe INTERNAL STRUCTURE predicts Voynich
PARAGRAPH-LEVEL features within the Stars section.

Hypotheses (all within Stars, R1 n=10 vs R3 n=12):
  H1: Elevated recipe complexity -> R3 > R1 mean paragraph body length
  H2: Elevated method diversity -> R3 > R1 OPERATION-Iteration zone fraction
  H3a: Gentle > elevated monitoring density (Brunschwig-internal)
  H3b: R1 > R3 h_ratio (monitoring anti-correlates with thermal intensity)
  PC1: Positive control -- R1 > R3 e-to-y rate (C1735 replication)
  N1: R1 vs R3 token count non-significant (negative control)
  N2: R1 vs R3 headless rate non-significant (negative control)

Produces: structural_recipe_decomposition_results.json
"""

import sys
sys.path.insert(0, '.')

import json
import time
import re
import numpy as np
from pathlib import Path
from scipy.stats import mannwhitneyu
from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology

t0 = time.time()

# --- Paths ---
RECIPE_PATH = Path('phases/BRUNSCHWIG_1512_BLIND_PREDICTION/results/brunschwig_1512_recipes.json')
ENGLISH_PATH = Path('sources/brunschwig_1512/brunschwig_1512_english.txt')
ZONE_PATH = Path('phases/PARAGRAPH_PROGRAM_TYPING/results/paragraph_program_typing.json')
PROFILE_PATH = Path('results/folio_operational_profiles.json')
REGIME_PATH = Path('data/regime_folio_mapping.json')
OUT_DIR = Path('phases/BRUNSCHWIG_STRUCTURAL_RECIPE_DECOMPOSITION/results')
OUT_PATH = OUT_DIR / 'structural_recipe_decomposition_results.json'

GALLOWS = set('ktpf')
OPERATION_ITERATION_CLUSTER = 2  # Zone 2 = OPERATION-Iteration per C1398


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


# ============================================================
# BLOCK A: Recipe Structure Extraction
# ============================================================
print('=' * 60)
print('BLOCK A: Recipe Structure Extraction')

# Load recipes
with open(RECIPE_PATH) as f:
    recipe_data = json.load(f)

all_recipes = recipe_data['recipes']

# Filter: classification='recipe', first_book or third_book
recipes = [r for r in all_recipes
           if r['classification'] == 'recipe'
           and r['book'] in ('first_book', 'third_book')]
print(f'  Filtered recipes: {len(recipes)} (first_book + third_book, classification=recipe)')

# Load English translation
with open(ENGLISH_PATH, encoding='utf-8') as f:
    eng_lines = f.readlines()
print(f'  English translation: {len(eng_lines)} lines')

# Extract full text per recipe using start_line boundaries
# Sort all segments by start_line for boundary detection
all_segments_sorted = sorted(all_recipes, key=lambda r: r['start_line'])
seg_starts = {r['id']: r['start_line'] for r in all_segments_sorted}
seg_order = [r['id'] for r in all_segments_sorted]

recipe_texts = {}
for i, seg in enumerate(all_segments_sorted):
    if seg['id'] not in {r['id'] for r in recipes}:
        continue
    start = seg['start_line']
    if i + 1 < len(all_segments_sorted):
        end = all_segments_sorted[i + 1]['start_line']
    else:
        end = len(eng_lines)
    recipe_texts[seg['id']] = ' '.join(line.strip() for line in eng_lines[start:end])

print(f'  Extracted text for {len(recipe_texts)} recipes')

# Monitoring keyword extraction with conditional co-occurrence
TEMPORAL_MARKERS = re.compile(
    r'\b(until|when|if|while|as\s+soon\s+as|once|then|after|before)\b', re.I
)

PASSIVE_MONITOR = re.compile(
    r'\b(look|appear(?:s|ed|ance)?|colou?r|clear|smell|odou?r|taste|tast(?:ed|ing)|'
    r'observe|sign|notice|see|watch|scent|fragran[ct]|aroma)\b', re.I
)

ACTIVE_TEST = re.compile(
    r'\b(test|try|tried|drop(?:s|ped)?|finger|feel|touch|prove|proven|proof|assay|'
    r'examine|inspect)\b', re.I
)


def count_monitoring_conditional(text, window=15):
    """Count monitoring keywords that co-occur with temporal markers within window."""
    words = text.split()
    n = len(words)

    # Find positions of temporal markers
    temporal_positions = set()
    for i, w in enumerate(words):
        if TEMPORAL_MARKERS.search(w):
            temporal_positions.add(i)

    # Count monitoring keywords near temporal markers
    passive_cond = 0
    active_cond = 0
    passive_raw = 0
    active_raw = 0

    for i, w in enumerate(words):
        is_passive = bool(PASSIVE_MONITOR.search(w))
        is_active = bool(ACTIVE_TEST.search(w))

        if is_passive:
            passive_raw += 1
        if is_active:
            active_raw += 1

        # Check if any temporal marker is within window
        near_temporal = any(abs(i - tp) <= window for tp in temporal_positions)

        if near_temporal:
            if is_passive:
                passive_cond += 1
            if is_active:
                active_cond += 1

    return {
        'passive_conditional': passive_cond,
        'active_conditional': active_cond,
        'total_conditional': passive_cond + active_cond,
        'passive_raw': passive_raw,
        'active_raw': active_raw,
        'total_raw': passive_raw + active_raw,
    }


# Compute per-recipe metrics
recipe_metrics = []
for r in recipes:
    rid = r['id']
    text = recipe_texts.get(rid, '')
    wc = r['word_count'] if r['word_count'] > 0 else 1

    mon = count_monitoring_conditional(text)
    distill_refs = r['distillation_steps']['distill_references']

    fire_class = r['fire_degree'].get('inferred_class')

    metrics = {
        'id': rid,
        'book': r['book'],
        'fire_class': fire_class,
        'word_count': r['word_count'],
        'complexity_score': distill_refs + len(r['methods']) + len(r['vessels']) + len(r['durations']),
        'n_methods': len(r['methods']),
        'n_vessels': len(r['vessels']),
        'n_durations': len(r['durations']),
        'distill_references': distill_refs,
        'monitoring_density': mon['total_conditional'] / wc,
        'monitoring_raw_density': mon['total_raw'] / wc,
        'monitoring_counts': mon,
    }
    recipe_metrics.append(metrics)

# Aggregate by fire class
gentle = [m for m in recipe_metrics if m['fire_class'] == 1]
elevated = [m for m in recipe_metrics if m['fire_class'] is not None and m['fire_class'] >= 2]
unclassed = [m for m in recipe_metrics if m['fire_class'] is None]

print(f'  Gentle (degree 1): {len(gentle)} recipes')
print(f'  Elevated (degree 2+): {len(elevated)} recipes')
print(f'  Unclassed: {len(unclassed)} recipes')


def agg_stats(metrics_list, field):
    vals = [m[field] for m in metrics_list]
    if not vals:
        return {'n': 0, 'mean': None, 'median': None, 'std': None}
    return {
        'n': len(vals),
        'mean': float(np.mean(vals)),
        'median': float(np.median(vals)),
        'std': float(np.std(vals)),
    }


fire_class_summary = {
    'gentle': {
        'n': len(gentle),
        'complexity': agg_stats(gentle, 'complexity_score'),
        'monitoring_density': agg_stats(gentle, 'monitoring_density'),
        'monitoring_raw_density': agg_stats(gentle, 'monitoring_raw_density'),
        'n_methods': agg_stats(gentle, 'n_methods'),
        'word_count': agg_stats(gentle, 'word_count'),
    },
    'elevated': {
        'n': len(elevated),
        'complexity': agg_stats(elevated, 'complexity_score'),
        'monitoring_density': agg_stats(elevated, 'monitoring_density'),
        'monitoring_raw_density': agg_stats(elevated, 'monitoring_raw_density'),
        'n_methods': agg_stats(elevated, 'n_methods'),
        'word_count': agg_stats(elevated, 'word_count'),
    },
}

print(f'\n  Gentle: complexity={fire_class_summary["gentle"]["complexity"]["mean"]:.2f}, '
      f'monitoring_density={fire_class_summary["gentle"]["monitoring_density"]["mean"]:.5f}, '
      f'n_methods={fire_class_summary["gentle"]["n_methods"]["mean"]:.2f}')
print(f'  Elevated: complexity={fire_class_summary["elevated"]["complexity"]["mean"]:.2f}, '
      f'monitoring_density={fire_class_summary["elevated"]["monitoring_density"]["mean"]:.5f}, '
      f'n_methods={fire_class_summary["elevated"]["n_methods"]["mean"]:.2f}')

block_a_time = time.time() - t0
print(f'\n  Block A complete ({block_a_time:.1f}s)')


# ============================================================
# BLOCK B: Voynich Paragraph Feature Aggregation
# ============================================================
print('\n' + '=' * 60)
print('BLOCK B: Voynich Paragraph Feature Aggregation')

# Load REGIME mapping
with open(REGIME_PATH) as f:
    regime_data = json.load(f)
regime_map = {f: info['regime'] for f, info in regime_data['regime_assignments'].items()}

# Load operational profiles (h_ratio, token_count)
with open(PROFILE_PATH) as f:
    profile_data = json.load(f)
profiles = {p['folio']: p for p in profile_data['profiles']}

# Load zone labels
with open(ZONE_PATH) as f:
    zone_data = json.load(f)
zone_labels = zone_data['paragraph_labels']

# Identify Stars folios by REGIME
tx = Transcript()
morph = Morphology()

# Get section per folio
folio_sections = {}
for tok in tx.currier_b():
    if tok.folio not in folio_sections:
        folio_sections[tok.folio] = tok.section

stars_folios = [f for f, s in folio_sections.items() if s == 'S']
stars_r1 = [f for f in stars_folios if regime_map.get(f) == 'REGIME_1']
stars_r3 = [f for f in stars_folios if regime_map.get(f) == 'REGIME_3']

print(f'  Stars folios: {len(stars_folios)}')
print(f'  Stars R1: {len(stars_r1)} folios')
print(f'  Stars R3: {len(stars_r3)} folios')

# Compute per-folio paragraph features using BFolioDecoder pattern
# (inline from Phase 616 approach, not using BFolioDecoder directly since
#  we need the same quality filter)

# Build per-folio token lists for e-to-y and headless computation
folio_tokens = defaultdict(list)
for tok in tx.currier_b():
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle:
        continue

    folio_tokens[tok.folio].append({
        'word': w,
        'folio': tok.folio,
        'line': tok.line,
        'prefix': m.prefix,
        'middle': m.middle,
        'suffix': m.suffix,
        'head': m.middle[0] if m.middle else None,
        'term': m.middle[-1] if m.middle else None,
        'is_ey': (m.middle[0] == 'e' and m.middle[-1] == 'y') if len(m.middle) >= 2 else False,
        'is_headless': m.prefix is None and len(m.middle) > 2,
    })

# Compute per-folio features
folio_features = {}
for fid in stars_folios:
    toks = folio_tokens.get(fid, [])
    n = len(toks)

    # h_ratio from profiles
    h_ratio = profiles[fid]['h_ratio'] if fid in profiles else None

    # Token count
    token_count = profiles[fid]['token_count'] if fid in profiles else n

    # e-to-y rate
    n_ey = sum(1 for t in toks if t['is_ey'])
    ey_rate = n_ey / n if n > 0 else 0

    # Headless rate
    n_headless = sum(1 for t in toks if t['is_headless'])
    headless_rate = n_headless / n if n > 0 else 0

    folio_features[fid] = {
        'folio': fid,
        'regime': regime_map.get(fid),
        'h_ratio': h_ratio,
        'token_count': token_count,
        'ey_rate': ey_rate,
        'headless_rate': headless_rate,
    }

# Compute paragraph-level features per folio
# Parse lines from transcript to identify paragraphs (gallows-boundary method)
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for tok in tx.currier_b():
    w = tok.word.strip()
    if not w or '*' in w:
        continue
    ln_int = int(tok.line) if tok.line.isdigit() else 0
    folio_line_tokens[tok.folio][ln_int].append(w)

for fid in stars_folios:
    lines = folio_line_tokens[fid]
    sorted_lines = sorted(lines.keys())

    # Identify paragraph boundaries (gallows-starting lines)
    para_starts = []
    for ln in sorted_lines:
        first_word = lines[ln][0] if lines[ln] else ''
        m = morph.extract(first_word)
        if m.middle and m.middle[0] in GALLOWS:
            para_starts.append(ln)

    # Build paragraphs
    body_lengths = []  # tokens per paragraph body
    for i, start_ln in enumerate(para_starts):
        if i + 1 < len(para_starts):
            end_ln = para_starts[i + 1]
        else:
            end_ln = max(sorted_lines) + 1 if sorted_lines else start_ln + 1

        para_lines = [ln for ln in sorted_lines if start_ln <= ln < end_ln]
        if len(para_lines) < 2:
            continue

        # Header = first line, body = rest
        body_lines = para_lines[1:]
        if len(body_lines) < 1:
            continue

        # Count body tokens
        body_token_count = sum(len(lines[ln]) for ln in body_lines)
        body_lengths.append(body_token_count)

    mean_body_length = float(np.mean(body_lengths)) if body_lengths else 0
    n_quality_paras = len(body_lengths)

    folio_features[fid]['mean_body_length'] = mean_body_length
    folio_features[fid]['n_quality_paras'] = n_quality_paras

# Compute zone features per folio
folio_zone_counts = defaultdict(lambda: Counter())
folio_zone_total = defaultdict(int)
for entry in zone_labels:
    fid = entry['folio']
    if fid in folio_features:
        folio_zone_counts[fid][entry['cluster']] += 1
        folio_zone_total[fid] += 1

for fid in stars_folios:
    total = folio_zone_total.get(fid, 0)
    op_iter_count = folio_zone_counts[fid].get(OPERATION_ITERATION_CLUSTER, 0)
    op_iter_frac = op_iter_count / total if total > 0 else 0
    zone_diversity = len(folio_zone_counts[fid])

    folio_features[fid]['op_iter_frac'] = op_iter_frac
    folio_features[fid]['zone_diversity'] = zone_diversity
    folio_features[fid]['zone_total'] = total

# Print Stars folio table
print(f'\n  Stars Folio Features:')
print(f'  {"Folio":<10} {"REGIME":<10} {"BodyLen":>8} {"OpIter%":>8} {"h_ratio":>8} '
      f'{"ey_rate":>8} {"Tokens":>7} {"Headless":>9} {"ZoneDiv":>8} {"QPara":>6}')
for fid in sorted(stars_r1 + stars_r3):
    ff = folio_features[fid]
    print(f'  {fid:<10} {ff["regime"]:<10} {ff["mean_body_length"]:>8.1f} '
          f'{ff["op_iter_frac"]:>8.3f} {ff["h_ratio"]:>8.4f} '
          f'{ff["ey_rate"]:>8.4f} {ff["token_count"]:>7} '
          f'{ff["headless_rate"]:>9.4f} {ff["zone_diversity"]:>8} {ff["n_quality_paras"]:>6}')

block_b_time = time.time() - t0
print(f'\n  Block B complete ({block_b_time:.1f}s)')


# ============================================================
# BLOCK C: Hypothesis Tests
# ============================================================
print('\n' + '=' * 60)
print('BLOCK C: Hypothesis Tests')


def mann_whitney_directional(group1_vals, group2_vals, alternative='greater'):
    """Mann-Whitney U with effect size (rank-biserial r)."""
    g1 = np.array(group1_vals, dtype=float)
    g2 = np.array(group2_vals, dtype=float)
    U, p = mannwhitneyu(g1, g2, alternative=alternative)
    n1, n2 = len(g1), len(g2)
    r = 1 - 2 * U / (n1 * n2)  # rank-biserial correlation
    return {
        'U': float(U),
        'p': float(p),
        'effect_r': float(r),
        'mean1': float(np.mean(g1)),
        'mean2': float(np.mean(g2)),
        'median1': float(np.median(g1)),
        'median2': float(np.median(g2)),
        'n1': n1,
        'n2': n2,
    }


# Get R1 and R3 feature arrays
r1_feats = [folio_features[f] for f in stars_r1]
r3_feats = [folio_features[f] for f in stars_r3]

# --- H1: Mean paragraph body length, R3 > R1 ---
print('\nH1: Mean paragraph body length (R3 > R1)')
r1_body = [f['mean_body_length'] for f in r1_feats]
r3_body = [f['mean_body_length'] for f in r3_feats]
h1_mw = mann_whitney_directional(r3_body, r1_body, alternative='greater')
h1_direction = h1_mw['mean1'] > h1_mw['mean2']  # R3 mean > R1 mean
h1_pass = h1_mw['p'] < 0.05 and h1_direction
print(f'  R3 mean={h1_mw["mean1"]:.1f}, R1 mean={h1_mw["mean2"]:.1f}, '
      f'U={h1_mw["U"]:.0f}, p={h1_mw["p"]:.4f}, r={h1_mw["effect_r"]:.3f}')
print(f'  Direction correct: {h1_direction}, PASS: {h1_pass}')

# --- H2: OPERATION-Iteration zone fraction, R3 > R1 ---
print('\nH2: OPERATION-Iteration zone fraction (R3 > R1)')
r1_opiter = [f['op_iter_frac'] for f in r1_feats]
r3_opiter = [f['op_iter_frac'] for f in r3_feats]
h2_mw = mann_whitney_directional(r3_opiter, r1_opiter, alternative='greater')
h2_direction = h2_mw['mean1'] > h2_mw['mean2']
h2_pass = h2_mw['p'] < 0.05 and h2_direction
print(f'  R3 mean={h2_mw["mean1"]:.4f}, R1 mean={h2_mw["mean2"]:.4f}, '
      f'U={h2_mw["U"]:.0f}, p={h2_mw["p"]:.4f}, r={h2_mw["effect_r"]:.3f}')
print(f'  Direction correct: {h2_direction}, PASS: {h2_pass}')

# --- H3a: Brunschwig monitoring density, gentle > elevated ---
print('\nH3a: Monitoring density, gentle > elevated (Brunschwig-internal)')
gentle_mon = [m['monitoring_density'] for m in gentle]
elevated_mon = [m['monitoring_density'] for m in elevated]
h3a_mw = mann_whitney_directional(gentle_mon, elevated_mon, alternative='greater')
h3a_direction = h3a_mw['mean1'] > h3a_mw['mean2']
h3a_pass = h3a_mw['p'] < 0.05 and h3a_direction
print(f'  Gentle mean={h3a_mw["mean1"]:.6f}, Elevated mean={h3a_mw["mean2"]:.6f}, '
      f'U={h3a_mw["U"]:.0f}, p={h3a_mw["p"]:.4f}, r={h3a_mw["effect_r"]:.3f}')
print(f'  Direction correct: {h3a_direction}, PASS: {h3a_pass}')

# Also report raw (unconditional) monitoring density
gentle_raw = [m['monitoring_raw_density'] for m in gentle]
elevated_raw = [m['monitoring_raw_density'] for m in elevated]
h3a_raw_mw = mann_whitney_directional(gentle_raw, elevated_raw, alternative='greater')
print(f'  [Raw] Gentle mean={h3a_raw_mw["mean1"]:.6f}, Elevated mean={h3a_raw_mw["mean2"]:.6f}, '
      f'p={h3a_raw_mw["p"]:.4f}')

# --- H3b: h_ratio, R1 > R3 ---
print('\nH3b: h_ratio (R1 > R3)')
r1_hratio = [f['h_ratio'] for f in r1_feats]
r3_hratio = [f['h_ratio'] for f in r3_feats]
h3b_mw = mann_whitney_directional(r1_hratio, r3_hratio, alternative='greater')
h3b_direction = h3b_mw['mean1'] > h3b_mw['mean2']
h3b_pass = h3b_mw['p'] < 0.05 and h3b_direction
print(f'  R1 mean={h3b_mw["mean1"]:.4f}, R3 mean={h3b_mw["mean2"]:.4f}, '
      f'U={h3b_mw["U"]:.0f}, p={h3b_mw["p"]:.4f}, r={h3b_mw["effect_r"]:.3f}')
print(f'  Direction correct: {h3b_direction}, PASS: {h3b_pass}')

h3_pass = h3a_pass and h3b_pass
print(f'  H3 combined PASS: {h3_pass}')

# --- PC1: Positive control -- e-to-y rate, R1 > R3 (C1735 replication) ---
print('\nPC1: e-to-y rate (R1 > R3) -- C1735 replication')
r1_ey = [f['ey_rate'] for f in r1_feats]
r3_ey = [f['ey_rate'] for f in r3_feats]
pc1_mw = mann_whitney_directional(r1_ey, r3_ey, alternative='greater')
pc1_direction = pc1_mw['mean1'] > pc1_mw['mean2']
pc1_pass = pc1_mw['p'] < 0.05 and pc1_direction
print(f'  R1 mean={pc1_mw["mean1"]:.4f}, R3 mean={pc1_mw["mean2"]:.4f}, '
      f'U={pc1_mw["U"]:.0f}, p={pc1_mw["p"]:.4f}, r={pc1_mw["effect_r"]:.3f}')
print(f'  Direction correct: {pc1_direction}, PASS: {pc1_pass}')

# --- N1: Token count, R1 vs R3 (two-sided, should be non-significant) ---
print('\nN1: Token count (R1 vs R3, two-sided, expect p > 0.10)')
r1_tokens = [f['token_count'] for f in r1_feats]
r3_tokens = [f['token_count'] for f in r3_feats]
n1_mw = mann_whitney_directional(r1_tokens, r3_tokens, alternative='two-sided')
n1_pass = n1_mw['p'] > 0.10
print(f'  R1 mean={n1_mw["mean1"]:.0f}, R3 mean={n1_mw["mean2"]:.0f}, '
      f'U={n1_mw["U"]:.0f}, p={n1_mw["p"]:.4f}, r={n1_mw["effect_r"]:.3f}')
print(f'  PASS (p > 0.10): {n1_pass}')

# --- N2: Headless rate, R1 vs R3 (two-sided, should be non-significant) ---
print('\nN2: Headless rate (R1 vs R3, two-sided, expect p > 0.10)')
r1_headless = [f['headless_rate'] for f in r1_feats]
r3_headless = [f['headless_rate'] for f in r3_feats]
n2_mw = mann_whitney_directional(r1_headless, r3_headless, alternative='two-sided')
n2_pass = n2_mw['p'] > 0.10
print(f'  R1 mean={n2_mw["mean1"]:.4f}, R3 mean={n2_mw["mean2"]:.4f}, '
      f'U={n2_mw["U"]:.0f}, p={n2_mw["p"]:.4f}, r={n2_mw["effect_r"]:.3f}')
print(f'  PASS (p > 0.10): {n2_pass}')

block_c_time = time.time() - t0
print(f'\n  Block C complete ({block_c_time:.1f}s)')


# ============================================================
# BLOCK D: Diagnostics and Controls
# ============================================================
print('\n' + '=' * 60)
print('BLOCK D: Diagnostics and Controls')

# Directional consistency
h1_dir_correct = h1_mw['mean1'] > h1_mw['mean2']  # R3 body > R1
h2_dir_correct = h2_mw['mean1'] > h2_mw['mean2']  # R3 opiter > R1
h3_dir_correct = h3a_direction and h3b_direction    # gentle > elevated mon AND R1 > R3 h_ratio
n_directions_correct = sum([h1_dir_correct, h2_dir_correct, h3_dir_correct])
print(f'\n  Directional consistency: {n_directions_correct}/3 H-tests with correct direction')
print(f'    H1 direction (R3 body > R1): {h1_dir_correct}')
print(f'    H2 direction (R3 opiter > R1): {h2_dir_correct}')
print(f'    H3 direction (gentle>elev mon AND R1>R3 h): {h3_dir_correct}')

# Within-R1 control: variance in paragraph features among R1 folios
print(f'\n  Within-R1 control (n={len(stars_r1)}):')
r1_body_std = float(np.std(r1_body))
r1_opiter_std = float(np.std(r1_opiter))
r1_hratio_std = float(np.std(r1_hratio))
print(f'    body_length std: {r1_body_std:.2f}')
print(f'    op_iter_frac std: {r1_opiter_std:.4f}')
print(f'    h_ratio std: {r1_hratio_std:.4f}')

# Exploratory: Herbal R2 vs R3+R4 (if enough folios)
herbal_folios = [f for f, s in folio_sections.items() if s == 'H']
herbal_r1 = [f for f in herbal_folios if regime_map.get(f) == 'REGIME_1']
herbal_r2 = [f for f in herbal_folios if regime_map.get(f) == 'REGIME_2']
herbal_r3 = [f for f in herbal_folios if regime_map.get(f) == 'REGIME_3']
herbal_r4 = [f for f in herbal_folios if regime_map.get(f) == 'REGIME_4']
print(f'\n  Herbal REGIME distribution: R1={len(herbal_r1)}, R2={len(herbal_r2)}, '
      f'R3={len(herbal_r3)}, R4={len(herbal_r4)}')

# Brunschwig recipe descriptive statistics
print(f'\n  Recipe structure summary:')
print(f'  {"Fire class":<12} {"N":>5} {"Complexity":>12} {"Mon.dens":>12} '
      f'{"N_methods":>10} {"Word_ct":>10}')
for label, group in [('Gentle', gentle), ('Elevated', elevated), ('Unclassed', unclassed)]:
    if not group:
        continue
    print(f'  {label:<12} {len(group):>5} '
          f'{np.mean([m["complexity_score"] for m in group]):>12.2f} '
          f'{np.mean([m["monitoring_density"] for m in group]):>12.6f} '
          f'{np.mean([m["n_methods"] for m in group]):>10.2f} '
          f'{np.mean([m["word_count"] for m in group]):>10.0f}')

block_d_time = time.time() - t0
print(f'\n  Block D complete ({block_d_time:.1f}s)')


# ============================================================
# VERDICT
# ============================================================
print('\n' + '=' * 60)
print('VERDICT')

h_passes = [h1_pass, h2_pass, h3_pass]
n_h_pass = sum(h_passes)
n_passes = [n1_pass, n2_pass]
n_n_pass = sum(n_passes)
all_directions_correct = (n_directions_correct == 3)

if not pc1_pass:
    verdict = 'MACHINERY_FAILURE'
    reason = f'Positive control (e-to-y) failed: p={pc1_mw["p"]:.4f}'
elif n_h_pass >= 3 and n_n_pass >= 2:
    verdict = 'STRUCTURAL_PREDICTION_CONFIRMED'
    reason = f'{n_h_pass}/3 H-tests + {n_n_pass}/2 N-controls pass'
elif n_h_pass >= 2 and n_n_pass >= 2:
    verdict = 'PARTIAL_STRUCTURAL_PREDICTION'
    reason = f'{n_h_pass}/3 H-tests + {n_n_pass}/2 N-controls pass'
elif n_h_pass >= 2 and n_n_pass < 2:
    verdict = 'STRUCTURAL_SIGNAL_CONTROLS_COMPROMISED'
    reason = f'{n_h_pass}/3 H-tests pass but only {n_n_pass}/2 N-controls'
elif all_directions_correct and n_h_pass >= 1:
    verdict = 'DIRECTIONAL_CONSISTENCY'
    reason = f'All 3 directions correct but only {n_h_pass}/3 significant'
elif n_h_pass == 1:
    verdict = 'WEAK_SIGNAL'
    reason = f'Only {n_h_pass}/3 H-tests pass, {n_directions_correct}/3 correct direction'
else:
    verdict = 'NO_STRUCTURAL_PREDICTION'
    reason = f'{n_h_pass}/3 H-tests, {n_directions_correct}/3 correct direction'

print(f'\n  VERDICT: {verdict}')
print(f'  Reason: {reason}')
print(f'\n  H1 (body length):    {"PASS" if h1_pass else "FAIL"} (p={h1_mw["p"]:.4f}, dir={h1_dir_correct})')
print(f'  H2 (op-iter frac):   {"PASS" if h2_pass else "FAIL"} (p={h2_mw["p"]:.4f}, dir={h2_dir_correct})')
print(f'  H3a (monitoring):    {"PASS" if h3a_pass else "FAIL"} (p={h3a_mw["p"]:.4f}, dir={h3a_direction})')
print(f'  H3b (h_ratio):       {"PASS" if h3b_pass else "FAIL"} (p={h3b_mw["p"]:.4f}, dir={h3b_direction})')
print(f'  PC1 (e-to-y):        {"PASS" if pc1_pass else "FAIL"} (p={pc1_mw["p"]:.4f})')
print(f'  N1 (token count):    {"PASS" if n1_pass else "FAIL"} (p={n1_mw["p"]:.4f})')
print(f'  N2 (headless rate):  {"PASS" if n2_pass else "FAIL"} (p={n2_mw["p"]:.4f})')


# ============================================================
# Save results
# ============================================================
results = {
    'metadata': {
        'phase': '617',
        'phase_name': 'BRUNSCHWIG_STRUCTURAL_RECIPE_DECOMPOSITION',
        'n_recipes_analyzed': len(recipes),
        'n_gentle': len(gentle),
        'n_elevated': len(elevated),
        'n_unclassed': len(unclassed),
        'n_stars_r1': len(stars_r1),
        'n_stars_r3': len(stars_r3),
        'stars_r1_folios': sorted(stars_r1),
        'stars_r3_folios': sorted(stars_r3),
    },
    'block_A_recipe_metrics': fire_class_summary,
    'block_B_voynich_features': {
        'stars_folios': [folio_features[f] for f in sorted(stars_r1 + stars_r3)]
    },
    'H1': {
        'test': 'mean_paragraph_body_length_R3_gt_R1',
        **h1_mw,
        'direction_correct': bool(h1_dir_correct),
        'pass': bool(h1_pass),
    },
    'H2': {
        'test': 'operation_iteration_zone_fraction_R3_gt_R1',
        **h2_mw,
        'direction_correct': bool(h2_dir_correct),
        'pass': bool(h2_pass),
    },
    'H3a': {
        'test': 'monitoring_density_gentle_gt_elevated',
        **h3a_mw,
        'direction_correct': bool(h3a_direction),
        'pass': bool(h3a_pass),
        'raw_monitoring': {
            'gentle_mean': float(np.mean(gentle_raw)),
            'elevated_mean': float(np.mean(elevated_raw)),
            'p': float(h3a_raw_mw['p']),
        },
    },
    'H3b': {
        'test': 'h_ratio_R1_gt_R3',
        **h3b_mw,
        'direction_correct': bool(h3b_direction),
        'pass': bool(h3b_pass),
    },
    'PC1': {
        'test': 'ey_rate_R1_gt_R3_positive_control',
        **pc1_mw,
        'direction_correct': bool(pc1_direction),
        'pass': bool(pc1_pass),
    },
    'N1': {
        'test': 'token_count_R1_vs_R3_null',
        **n1_mw,
        'pass': bool(n1_pass),
    },
    'N2': {
        'test': 'headless_rate_R1_vs_R3_null',
        **n2_mw,
        'pass': bool(n2_pass),
    },
    'diagnostics': {
        'directional_consistency': n_directions_correct,
        'within_R1_std': {
            'body_length': r1_body_std,
            'op_iter_frac': r1_opiter_std,
            'h_ratio': r1_hratio_std,
        },
        'herbal_regime_distribution': {
            'R1': len(herbal_r1),
            'R2': len(herbal_r2),
            'R3': len(herbal_r3),
            'R4': len(herbal_r4),
        },
    },
    'verdict': {
        'verdict': verdict,
        'reason': reason,
        'h_passed': n_h_pass,
        'h_total': 3,
        'n_passed': n_n_pass,
        'n_total': 2,
        'pc1_passed': bool(pc1_pass),
        'directions_correct': n_directions_correct,
    },
    'runtime_s': round(time.time() - t0, 1),
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, 'w') as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)

print(f'\nResults saved to {OUT_PATH}')
print(f'Total runtime: {time.time() - t0:.1f}s')
