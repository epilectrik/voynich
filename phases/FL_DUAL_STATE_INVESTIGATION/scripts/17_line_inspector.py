"""
17_line_inspector.py

Dump fully annotated lines for manual inspection.
Show every token with: word, prefix, middle, suffix, role, FL mode, position.
Pick lines from a few different folios with clear LOW->HIGH structure.
"""
import sys
import json
from pathlib import Path
from collections import defaultdict

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

MIN_N = 50
tx = Transcript()
morph = Morphology()

# Load role map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data['token_to_role']

# Collect and fit GMMs
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
# Annotate and dump lines
# ============================================================
def annotate_line(tokens):
    n = len(tokens)
    annotated = []
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
        elif is_fl:
            stage = FL_STAGE_MAP[mid][0]

        role = token_to_role.get(t.word, 'UNKNOWN')
        prefix = m.prefix if m and m.prefix else '-'
        suffix = m.suffix if m and m.suffix else '-'
        middle = m.middle if m and m.middle else '?'

        annotated.append({
            'idx': idx,
            'pos': pos,
            'word': t.word,
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
            'role': role,
            'is_fl': is_fl,
            'fl_mode': mode,
            'fl_stage': stage,
        })
    return annotated

def print_line(folio, line_num, annotated):
    print(f"\n{'='*90}")
    print(f"FOLIO {folio} LINE {line_num} ({len(annotated)} tokens)")
    print(f"{'='*90}")
    print(f"{'#':>3} {'pos':>5} {'word':>15} {'pfx':>5} {'MID':>6} {'sfx':>5} "
          f"{'role':>18} {'FL?':>4} {'mode':>5} {'stage':>10}")
    print("-" * 90)

    for a in annotated:
        fl_marker = "FL" if a['is_fl'] else ""
        mode_str = a['fl_mode'] if a['fl_mode'] else ""
        stage_str = a['fl_stage'] if a['fl_stage'] else ""

        # Highlight FL tokens
        prefix = ">>>" if a['is_fl'] else "   "

        print(f"{prefix}{a['idx']:>3} {a['pos']:>5.2f} {a['word']:>15} {a['prefix']:>5} "
              f"{a['middle']:>6} {a['suffix']:>5} {a['role']:>18} {fl_marker:>4} "
              f"{mode_str:>5} {stage_str:>10}")

# Find good example lines: mixed-mode with clear LOW->HIGH
good_lines = []
for line_key, tokens in line_tokens.items():
    if len(tokens) < 6:
        continue
    ann = annotate_line(tokens)
    fl_tokens = [a for a in ann if a['is_fl']]
    if len(fl_tokens) < 3:
        continue

    low_fls = [a for a in fl_tokens if a['fl_mode'] == 'LOW']
    high_fls = [a for a in fl_tokens if a['fl_mode'] == 'HIGH']

    if low_fls and high_fls:
        # Score: prefer lines with clear LOW->HIGH separation
        max_low_pos = max(a['pos'] for a in low_fls)
        min_high_pos = min(a['pos'] for a in high_fls)
        if min_high_pos > max_low_pos:  # Clean separation
            gap_size = min_high_pos - max_low_pos
            good_lines.append((line_key, tokens, ann, gap_size, len(fl_tokens)))

# Sort by gap clarity and pick diverse folios
good_lines.sort(key=lambda x: (-x[3], -x[4]))

# Pick from different folios
seen_folios = set()
selected = []
for line_key, tokens, ann, gap, n_fl in good_lines:
    folio = line_key[0]
    if folio not in seen_folios and len(selected) < 8:
        seen_folios.add(folio)
        selected.append((line_key, tokens, ann, gap, n_fl))

# Also pick a few with many FL tokens regardless of folio
many_fl = sorted(good_lines, key=lambda x: -x[4])
for line_key, tokens, ann, gap, n_fl in many_fl[:4]:
    if line_key not in [s[0] for s in selected]:
        selected.append((line_key, tokens, ann, gap, n_fl))

print(f"Selected {len(selected)} lines for inspection")

for line_key, tokens, ann, gap, n_fl in selected:
    print_line(line_key[0], line_key[1], ann)

    # Summary
    fl_tokens = [a for a in ann if a['is_fl']]
    low = [a for a in fl_tokens if a['fl_mode'] == 'LOW']
    high = [a for a in fl_tokens if a['fl_mode'] == 'HIGH']
    gap_tokens = [a for a in ann if not a['is_fl']
                  and low and high
                  and a['pos'] > max(a2['pos'] for a2 in low)
                  and a['pos'] < min(a2['pos'] for a2 in high)]

    low_str = ', '.join(a['prefix'] + '+' + a['middle'] + '+' + a['suffix'] + '(' + a['fl_stage'] + ')' for a in low)
    high_str = ', '.join(a['prefix'] + '+' + a['middle'] + '+' + a['suffix'] + '(' + a['fl_stage'] + ')' for a in high)
    gap_str = ', '.join(a['word'] + '(' + a['role'] + ')' for a in gap_tokens)
    print(f"\n  LOW cluster:  {low_str}")
    print(f"  HIGH cluster: {high_str}")
    print(f"  Gap tokens:   {gap_str}")
