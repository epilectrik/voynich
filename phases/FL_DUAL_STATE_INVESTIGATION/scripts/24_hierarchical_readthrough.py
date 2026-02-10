"""
24_hierarchical_readthrough.py

Manual readthrough of 20 lines through the hierarchical nesting lens.
Annotate each token with its layer and class to make the structure visible.
Line structure: [FL LOW] [outer-left] ... [center] ... [outer-right] [FL HIGH]
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from sklearn.mixture import GaussianMixture

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
# Build annotated lines
# ============================================================
annotated_lines = []

for line_key, tokens in sorted(line_tokens.items()):
    n = len(tokens)
    if n < 8:  # Need enough tokens for clear nesting
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
        if is_fl and mid in gmm_models:
            info = gmm_models[mid]
            pred = info['model'].predict(np.array([[pos]]))[0]
            if info['swap']:
                pred = 1 - pred
            mode = 'LOW' if pred == 0 else 'HIGH'
            stage = FL_STAGE_MAP[mid][0]

        cls = token_to_class.get(t.word, None)
        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else None
        middle = m.middle if m and m.middle else None
        suffix = m.suffix if m and m.suffix else None

        entry = {'word': t.word, 'idx': idx, 'pos': pos, 'is_fl': is_fl,
                 'mode': mode, 'stage': stage, 'class': cls, 'role': role,
                 'prefix': prefix, 'middle': middle, 'suffix': suffix}
        all_info.append(entry)
        if is_fl and mode:
            fl_info.append(entry)

    low_fls = [f for f in fl_info if f['mode'] == 'LOW']
    high_fls = [f for f in fl_info if f['mode'] == 'HIGH']
    if not low_fls or not high_fls:
        continue

    max_low_idx = max(f['idx'] for f in low_fls)
    min_high_idx = min(f['idx'] for f in high_fls)
    gap = [t for t in all_info if not t['is_fl']
           and t['idx'] > max_low_idx and t['idx'] < min_high_idx]

    if len(gap) < 3:
        continue

    # Assign layer labels using indices
    ol_idx = gap[0]['idx']
    or_idx = gap[-1]['idx']
    gap_indices = set(g['idx'] for g in gap)
    for t in all_info:
        if t['is_fl']:
            if t['mode'] == 'LOW':
                t['layer'] = 'FL-LOW'
            elif t['mode'] == 'HIGH':
                t['layer'] = 'FL-HIGH'
            else:
                t['layer'] = 'FL-?'
        elif t['idx'] <= max_low_idx:
            t['layer'] = 'pre-FL'
        elif t['idx'] >= min_high_idx:
            t['layer'] = 'post-FL'
        elif t['idx'] == ol_idx:
            t['layer'] = 'OUTER-L'
        elif t['idx'] == or_idx:
            t['layer'] = 'OUTER-R'
        elif t['idx'] in gap_indices:
            t['layer'] = 'CENTER'
        else:
            t['layer'] = 'BETWEEN'

    low_stage = Counter(f['stage'] for f in low_fls).most_common(1)[0][0]
    high_stage = Counter(f['stage'] for f in high_fls).most_common(1)[0][0]

    annotated_lines.append({
        'key': line_key,
        'pair': (low_stage, high_stage),
        'tokens': all_info,
        'n_gap': len(gap),
        'n_tokens': n,
    })

print(f"Lines with clear nesting: {len(annotated_lines)}")

# ============================================================
# Select diverse examples
# ============================================================
# Pick lines from different pair types and sections
pair_counts = Counter(al['pair'] for al in annotated_lines)
top_pairs = [p for p, _ in pair_counts.most_common(6)]

selected = []
used_pairs = Counter()
for al in annotated_lines:
    if al['pair'] in top_pairs and used_pairs[al['pair']] < 4:
        if al['n_gap'] >= 4 and al['n_tokens'] >= 9:  # Good examples
            selected.append(al)
            used_pairs[al['pair']] += 1
    if len(selected) >= 20:
        break

# ============================================================
# Print annotated lines
# ============================================================
print(f"\n{'='*80}")
print("HIERARCHICAL LINE READTHROUGH")
print(f"{'='*80}")
print("""
Legend:
  Layer markers: FL-LOW | OUTER-L | CENTER | OUTER-R | FL-HIGH
  Role codes: EN=ENERGY_OPERATOR, FQ=FREQUENT_OPERATOR, AX=AUXILIARY,
              CC=CORE_CONTROL, FL=FLOW_OPERATOR, UK=UNKNOWN
  Class: C## from 49-class system (? = unclassified)
""")

role_codes = {
    'ENERGY_OPERATOR': 'EN', 'FREQUENT_OPERATOR': 'FQ',
    'AUXILIARY': 'AX', 'CORE_CONTROL': 'CC',
    'FLOW_OPERATOR': 'FL', 'UNKNOWN': 'UK'
}

for i, al in enumerate(selected):
    folio, line = al['key']
    low_s, high_s = al['pair']
    pair_label = f"{low_s[:4]}>{high_s[:4]}"

    print(f"\n{'-'*80}")
    print(f"LINE {i+1}: {folio}.{line}  |  Pair: {pair_label}  |  "
          f"Tokens: {al['n_tokens']}  Gap: {al['n_gap']}")
    print(f"{'-'*80}")

    # Print in structured format
    current_layer = None
    for t in al['tokens']:
        layer = t['layer']
        if layer != current_layer:
            if current_layer is not None:
                print(f"  {'':>10}|")
            current_layer = layer

        rc = role_codes.get(t['role'], '??')
        cls_str = f"C{t['class']}" if t['class'] else '?'
        pfx = t['prefix'] if t['prefix'] else '-'
        mid = t['middle'] if t['middle'] else '-'
        sfx = t['suffix'] if t['suffix'] else '-'

        # Highlight FL tokens
        if t['is_fl']:
            stage_str = f"[{t['stage']}]" if t['stage'] else ''
            mode_str = t['mode'] if t['mode'] else '?'
            print(f"  {layer:>10}| {t['word']:<14} "
                  f"FL:{mode_str:<4} {stage_str}")
        else:
            morph_str = f"[{pfx}|{mid}|{sfx}]"
            print(f"  {layer:>10}| {t['word']:<14} "
                  f"{rc:<3} {cls_str:<4} {morph_str}")

# ============================================================
# Pattern summary
# ============================================================
print(f"\n{'='*80}")
print("PATTERN SUMMARY ACROSS ALL LINES")
print(f"{'='*80}")

# What prefix patterns dominate each layer?
layer_prefixes = defaultdict(Counter)
layer_classes = defaultdict(Counter)
for al in annotated_lines:
    for t in al['tokens']:
        if t['layer'] in ['OUTER-L', 'OUTER-R', 'CENTER']:
            if t['prefix']:
                layer_prefixes[t['layer']][t['prefix']] += 1
            if t['class']:
                layer_classes[t['layer']][t['class']] += 1

for layer in ['OUTER-L', 'OUTER-R', 'CENTER']:
    pfx_total = sum(layer_prefixes[layer].values())
    cls_total = sum(layer_classes[layer].values())
    top_pfx = layer_prefixes[layer].most_common(5)
    top_cls = layer_classes[layer].most_common(5)

    pfx_str = ', '.join(f"{p}({c/pfx_total*100:.0f}%)" for p, c in top_pfx)
    cls_str = ', '.join(f"C{c}({n/cls_total*100:.0f}%)" for c, n in top_cls)

    print(f"\n  {layer}:")
    print(f"    Prefixes: {pfx_str}")
    print(f"    Classes:  {cls_str}")

# ============================================================
# Structural pattern: is there a consistent "grammar" of nesting?
# ============================================================
print(f"\n{'='*80}")
print("NESTING GRAMMAR CHECK")
print(f"{'='*80}")

# Check: does OUTER-L prefix predict OUTER-R prefix?
ol_or_pairs = Counter()
for al in annotated_lines:
    ol = None
    oright = None
    for t in al['tokens']:
        if t['layer'] == 'OUTER-L':
            ol = t['prefix'] if t['prefix'] else 'NONE'
        if t['layer'] == 'OUTER-R':
            oright = t['prefix'] if t['prefix'] else 'NONE'
    if ol and oright:
        ol_or_pairs[(ol, oright)] += 1

print("\n  Outer-left prefix -> Outer-right prefix (top 15):")
for (ol, oright), count in ol_or_pairs.most_common(15):
    pct = count / sum(ol_or_pairs.values()) * 100
    print(f"    {ol:>6} -> {oright:<6}: {count:>4} ({pct:.1f}%)")

# Check: are certain OL->OR pairs more common than expected?
ol_totals = Counter()
or_totals = Counter()
for (ol, oright), c in ol_or_pairs.items():
    ol_totals[ol] += c
    or_totals[oright] += c
grand = sum(ol_or_pairs.values())

print("\n  Most enriched OL->OR pairs (obs/exp ratio):")
enriched = []
for (ol, oright), observed in ol_or_pairs.items():
    if observed < 5:
        continue
    expected = ol_totals[ol] * or_totals[oright] / grand
    ratio = observed / expected if expected > 0 else 0
    enriched.append((ol, oright, observed, expected, ratio))

enriched.sort(key=lambda x: -x[4])
for ol, oright, obs, exp, ratio in enriched[:10]:
    print(f"    {ol:>6} -> {oright:<6}: obs={obs:>3}, exp={exp:.1f}, ratio={ratio:.2f}x")

# ============================================================
# Save summary
# ============================================================
result = {
    'n_annotated_lines': len(annotated_lines),
    'n_selected': len(selected),
    'layer_prefix_outer_left_top3': [p for p, _ in layer_prefixes['OUTER-L'].most_common(3)],
    'layer_prefix_outer_right_top3': [p for p, _ in layer_prefixes['OUTER-R'].most_common(3)],
    'layer_prefix_center_top3': [p for p, _ in layer_prefixes['CENTER'].most_common(3)],
    'verdict': 'HIERARCHICAL_READTHROUGH_COMPLETE',
}

out_path = Path(__file__).resolve().parent.parent / "results" / "24_hierarchical_readthrough.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
