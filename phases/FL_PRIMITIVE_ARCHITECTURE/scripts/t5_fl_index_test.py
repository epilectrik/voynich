"""
T5: FL as State Index Test

Hypothesis: FL MIDDLEs index material states through a process.
If true:
1. Different FL MIDDLEs should appear at different line positions
2. FL MIDDLEs should correlate with what precedes/follows them
3. FL vocabulary (17) is small enough to be state labels
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load classified token set
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

# Role definitions
ROLE_MAP = {}
for cls in [10, 11, 12, 17]:
    ROLE_MAP[cls] = 'CC'
for cls in [8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49]:
    ROLE_MAP[cls] = 'EN'
for cls in [7, 30, 38, 40]:
    ROLE_MAP[cls] = 'FL'
for cls in [9, 13, 14, 23]:
    ROLE_MAP[cls] = 'FQ'
for cls in [1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29]:
    ROLE_MAP[cls] = 'AX'

FL_CLASSES = {7, 30, 38, 40}

print("="*70)
print("FL AS STATE INDEX TEST")
print("="*70)

# Build per-line token sequences with FL MIDDLE info
lines_data = defaultdict(list)

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    key = (token.folio, token.line)
    m = morph.extract(w)

    if w in token_to_class:
        cls = int(token_to_class[w])
        role = ROLE_MAP.get(cls, 'UNK')
    else:
        cls = None
        role = 'UN'

    lines_data[key].append({
        'word': w,
        'class': cls,
        'role': role,
        'middle': m.middle,
        'folio': token.folio,
        'line': token.line
    })

# ============================================================
# FL MIDDLE POSITIONAL PROFILES
# ============================================================
print("\n" + "="*70)
print("FL MIDDLE POSITIONAL PROFILES")
print("="*70)

# For each FL MIDDLE, compute mean normalized position
fl_middle_positions = defaultdict(list)

for key, tokens in lines_data.items():
    line_len = len(tokens)
    for i, t in enumerate(tokens):
        if t['role'] == 'FL' and t['middle']:
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            fl_middle_positions[t['middle']].append(norm_pos)

print("\nFL MIDDLE mean positions (sorted by position):")
fl_middle_stats = []
for mid, positions in fl_middle_positions.items():
    if len(positions) >= 5:  # Minimum sample
        mean_pos = np.mean(positions)
        std_pos = np.std(positions)
        fl_middle_stats.append({
            'middle': mid,
            'mean_pos': mean_pos,
            'std_pos': std_pos,
            'count': len(positions)
        })

fl_middle_stats.sort(key=lambda x: x['mean_pos'])

for s in fl_middle_stats:
    print(f"  '{s['middle']}': pos={s['mean_pos']:.3f} +/- {s['std_pos']:.3f} (n={s['count']})")

# Check if positions are differentiated
if len(fl_middle_stats) >= 2:
    positions = [s['mean_pos'] for s in fl_middle_stats]
    pos_range = max(positions) - min(positions)
    pos_std = np.std(positions)
    print(f"\nPosition range across FL MIDDLEs: {pos_range:.3f}")
    print(f"Position std across FL MIDDLEs: {pos_std:.3f}")

# ============================================================
# FL MIDDLE CONTEXT CORRELATION
# ============================================================
print("\n" + "="*70)
print("FL MIDDLE CONTEXT CORRELATION")
print("="*70)

# For each FL MIDDLE, what roles precede/follow it?
fl_middle_before = defaultdict(Counter)
fl_middle_after = defaultdict(Counter)

for key, tokens in lines_data.items():
    for i, t in enumerate(tokens):
        if t['role'] == 'FL' and t['middle']:
            mid = t['middle']
            if i > 0:
                fl_middle_before[mid][tokens[i-1]['role']] += 1
            if i < len(tokens) - 1:
                fl_middle_after[mid][tokens[i+1]['role']] += 1

# Check if different FL MIDDLEs have different context profiles
print("\nTop FL MIDDLEs and their context profiles:")
for s in fl_middle_stats[:10]:
    mid = s['middle']
    before = fl_middle_before[mid]
    after = fl_middle_after[mid]

    before_top = before.most_common(2)
    after_top = after.most_common(2)

    before_str = ', '.join(f"{r}:{c}" for r, c in before_top)
    after_str = ', '.join(f"{r}:{c}" for r, c in after_top)

    print(f"\n  '{mid}' (pos={s['mean_pos']:.3f}, n={s['count']}):")
    print(f"    BEFORE: {before_str}")
    print(f"    AFTER:  {after_str}")

# ============================================================
# FL MIDDLE AS STATE MARKER
# ============================================================
print("\n" + "="*70)
print("FL MIDDLE STATE MARKER ANALYSIS")
print("="*70)

# If FL indexes states, early FL MIDDLEs should differ from late FL MIDDLEs
early_fl = [s for s in fl_middle_stats if s['mean_pos'] < 0.4]
late_fl = [s for s in fl_middle_stats if s['mean_pos'] > 0.6]

print(f"\nEarly FL MIDDLEs (pos < 0.4): {len(early_fl)}")
for s in early_fl:
    print(f"  '{s['middle']}': {s['mean_pos']:.3f}")

print(f"\nLate FL MIDDLEs (pos > 0.6): {len(late_fl)}")
for s in late_fl:
    print(f"  '{s['middle']}': {s['mean_pos']:.3f}")

# Check character composition difference
early_chars = set()
late_chars = set()
for s in early_fl:
    early_chars.update(s['middle'])
for s in late_fl:
    late_chars.update(s['middle'])

print(f"\nEarly FL chars: {sorted(early_chars)}")
print(f"Late FL chars: {sorted(late_chars)}")
print(f"Early-only chars: {sorted(early_chars - late_chars)}")
print(f"Late-only chars: {sorted(late_chars - early_chars)}")

# ============================================================
# FL MIDDLE TRANSITION PATTERNS
# ============================================================
print("\n" + "="*70)
print("FL MIDDLE TRANSITION PATTERNS")
print("="*70)

# When FL[i] appears, what FL[j] comes next (in same line)?
fl_fl_transitions = Counter()
fl_sequence_lengths = []

for key, tokens in lines_data.items():
    fl_sequence = []
    for t in tokens:
        if t['role'] == 'FL' and t['middle']:
            fl_sequence.append(t['middle'])

    if len(fl_sequence) >= 2:
        fl_sequence_lengths.append(len(fl_sequence))
        for i in range(len(fl_sequence) - 1):
            fl_fl_transitions[(fl_sequence[i], fl_sequence[i+1])] += 1

print(f"\nLines with 2+ FL tokens: {len(fl_sequence_lengths)}")
if fl_sequence_lengths:
    print(f"Mean FL sequence length: {np.mean(fl_sequence_lengths):.2f}")

print("\nMost common FL -> FL MIDDLE transitions:")
for (m1, m2), count in fl_fl_transitions.most_common(15):
    same = "SAME" if m1 == m2 else "DIFF"
    print(f"  '{m1}' -> '{m2}': {count} [{same}]")

# Self-transition rate
total_fl_trans = sum(fl_fl_transitions.values())
self_trans = sum(c for (m1, m2), c in fl_fl_transitions.items() if m1 == m2)
self_rate = 100 * self_trans / total_fl_trans if total_fl_trans else 0
print(f"\nFL self-transition rate: {self_rate:.1f}%")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Position differentiation
if pos_range > 0.3:
    findings.append(f"POSITION_DIFFERENTIATED: FL MIDDLEs span {pos_range:.2f} position range")
elif pos_range > 0.15:
    findings.append(f"POSITION_PARTIAL: FL MIDDLEs span {pos_range:.2f} position range (moderate)")
else:
    findings.append(f"POSITION_UNIFORM: FL MIDDLEs span only {pos_range:.2f} position range")

# Early/late split
if len(early_fl) >= 2 and len(late_fl) >= 2:
    findings.append(f"EARLY_LATE_SPLIT: {len(early_fl)} early MIDDLEs, {len(late_fl)} late MIDDLEs")

# Self-transition
if self_rate > 30:
    findings.append(f"HIGH_SELF_TRANSITION: {self_rate:.1f}% same-MIDDLE sequences")
elif self_rate < 10:
    findings.append(f"LOW_SELF_TRANSITION: {self_rate:.1f}% (state changes, not repetition)")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

# Index hypothesis assessment
print(f"""

FL-AS-INDEX ASSESSMENT:

Position differentiation: {'YES' if pos_range > 0.2 else 'PARTIAL' if pos_range > 0.1 else 'NO'}
  - Range: {pos_range:.3f} (0=same position, 1=full spread)

Early/Late vocabulary split: {'YES' if len(early_fl) >= 2 and len(late_fl) >= 2 else 'NO'}
  - Early MIDDLEs: {[s['middle'] for s in early_fl]}
  - Late MIDDLEs: {[s['middle'] for s in late_fl]}

Self-transition rate: {self_rate:.1f}%
  - Low = state progression (index changes)
  - High = state persistence (index stable)

INTERPRETATION:
FL's 17 MIDDLEs {'DO' if pos_range > 0.2 else 'PARTIALLY' if pos_range > 0.1 else 'DO NOT'} show positional differentiation.
{'This supports FL-as-state-index.' if pos_range > 0.2 else 'Evidence is mixed.' if pos_range > 0.1 else 'FL MIDDLEs appear position-independent.'}
""")

# Save results
results = {
    'fl_middle_stats': fl_middle_stats,
    'position_range': float(pos_range),
    'position_std': float(pos_std),
    'early_fl_middles': [s['middle'] for s in early_fl],
    'late_fl_middles': [s['middle'] for s in late_fl],
    'self_transition_rate': self_rate,
    'fl_fl_transitions_top': [{'from': m1, 'to': m2, 'count': c}
                              for (m1, m2), c in fl_fl_transitions.most_common(20)],
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'FL_PRIMITIVE_ARCHITECTURE' / 'results' / 't5_fl_index_test.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True, default=float)

print(f"\nResults saved to {out_path}")
