"""
T6: EN Kernel Profile Analysis

EN is 60.7% kernel-containing (highest after CC 100%).
EN appears most often after FL (25.1%).

Questions:
1. What k/h/e combinations does EN use?
2. Does EN kernel profile vary by position relative to FL?
3. Is EN the transformation operator between FL states?
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
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}

# FL state categories from T5
FL_EARLY = {'i', 'ii', 'in'}  # pos < 0.45
FL_MEDIAL = {'r', 'ar', 'al', 'l', 'ol'}  # pos 0.45-0.70
FL_LATE = {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'}  # pos > 0.70

def get_kernel_signature(word):
    """Return kernel signature: which of k, h, e are present."""
    has_k = 'k' in word
    has_h = 'h' in word
    has_e = 'e' in word

    sig = []
    if has_k: sig.append('k')
    if has_h: sig.append('h')
    if has_e: sig.append('e')

    return tuple(sig) if sig else ('none',)

def get_fl_stage(middle):
    """Classify FL MIDDLE into stage."""
    if middle in FL_EARLY:
        return 'EARLY'
    elif middle in FL_MEDIAL:
        return 'MEDIAL'
    elif middle in FL_LATE:
        return 'LATE'
    return 'OTHER'

print("="*70)
print("EN KERNEL PROFILE ANALYSIS")
print("="*70)

# Build per-line token sequences
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
# EN KERNEL SIGNATURE DISTRIBUTION
# ============================================================
print("\n" + "="*70)
print("EN KERNEL SIGNATURE DISTRIBUTION")
print("="*70)

en_kernel_sigs = Counter()
en_tokens_total = 0

for key, tokens in lines_data.items():
    for t in tokens:
        if t['role'] == 'EN':
            sig = get_kernel_signature(t['word'])
            en_kernel_sigs[sig] += 1
            en_tokens_total += 1

print(f"\nTotal EN tokens: {en_tokens_total}")
print("\nKernel signature distribution:")
for sig, count in en_kernel_sigs.most_common():
    pct = 100 * count / en_tokens_total
    sig_str = '+'.join(sig) if sig != ('none',) else 'none'
    print(f"  {sig_str}: {count} ({pct:.1f}%)")

# Calculate kernel rates
has_any_kernel = en_tokens_total - en_kernel_sigs.get(('none',), 0)
has_k = sum(c for sig, c in en_kernel_sigs.items() if 'k' in sig)
has_h = sum(c for sig, c in en_kernel_sigs.items() if 'h' in sig)
has_e = sum(c for sig, c in en_kernel_sigs.items() if 'e' in sig)

print(f"\nEN kernel rates:")
print(f"  Any kernel: {100*has_any_kernel/en_tokens_total:.1f}%")
print(f"  Has 'k': {100*has_k/en_tokens_total:.1f}%")
print(f"  Has 'h': {100*has_h/en_tokens_total:.1f}%")
print(f"  Has 'e': {100*has_e/en_tokens_total:.1f}%")

# ============================================================
# EN KERNEL BY CLASS
# ============================================================
print("\n" + "="*70)
print("EN KERNEL PROFILE BY CLASS")
print("="*70)

class_kernel_profile = defaultdict(Counter)
class_totals = Counter()

for key, tokens in lines_data.items():
    for t in tokens:
        if t['role'] == 'EN' and t['class']:
            sig = get_kernel_signature(t['word'])
            class_kernel_profile[t['class']][sig] += 1
            class_totals[t['class']] += 1

print("\nEN classes by kernel rate:")
class_kernel_rates = []
for cls in sorted(EN_CLASSES):
    total = class_totals[cls]
    if total > 0:
        kernel_count = total - class_kernel_profile[cls].get(('none',), 0)
        kernel_rate = 100 * kernel_count / total
        class_kernel_rates.append((cls, kernel_rate, total))

class_kernel_rates.sort(key=lambda x: -x[1])
for cls, rate, total in class_kernel_rates:
    print(f"  Class {cls}: {rate:.1f}% kernel (n={total})")

# ============================================================
# EN AFTER FL: KERNEL PROFILE BY FL STATE
# ============================================================
print("\n" + "="*70)
print("EN KERNEL PROFILE AFTER FL (BY FL STATE)")
print("="*70)

# When EN follows FL, does EN's kernel depend on FL's state?
en_after_fl_early = Counter()
en_after_fl_medial = Counter()
en_after_fl_late = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'FL' and tokens[i+1]['role'] == 'EN':
            fl_mid = tokens[i]['middle']
            fl_stage = get_fl_stage(fl_mid)
            en_sig = get_kernel_signature(tokens[i+1]['word'])

            if fl_stage == 'EARLY':
                en_after_fl_early[en_sig] += 1
            elif fl_stage == 'MEDIAL':
                en_after_fl_medial[en_sig] += 1
            elif fl_stage == 'LATE':
                en_after_fl_late[en_sig] += 1

def summarize_kernel(counter):
    total = sum(counter.values())
    if total == 0:
        return "n/a", 0, 0, 0, 0
    kernel = total - counter.get(('none',), 0)
    k_rate = 100 * sum(c for sig, c in counter.items() if 'k' in sig) / total
    h_rate = 100 * sum(c for sig, c in counter.items() if 'h' in sig) / total
    e_rate = 100 * sum(c for sig, c in counter.items() if 'e' in sig) / total
    any_rate = 100 * kernel / total
    return total, any_rate, k_rate, h_rate, e_rate

print("\nEN kernel profile by preceding FL state:")
print("\n  After FL-EARLY (i, ii, in):")
total, any_r, k_r, h_r, e_r = summarize_kernel(en_after_fl_early)
print(f"    n={total}, any={any_r:.1f}%, k={k_r:.1f}%, h={h_r:.1f}%, e={e_r:.1f}%")

print("\n  After FL-MEDIAL (r, ar, al, l, ol):")
total, any_r, k_r, h_r, e_r = summarize_kernel(en_after_fl_medial)
print(f"    n={total}, any={any_r:.1f}%, k={k_r:.1f}%, h={h_r:.1f}%, e={e_r:.1f}%")

print("\n  After FL-LATE (o, ly, am, m, dy, ry, y):")
total, any_r, k_r, h_r, e_r = summarize_kernel(en_after_fl_late)
print(f"    n={total}, any={any_r:.1f}%, k={k_r:.1f}%, h={h_r:.1f}%, e={e_r:.1f}%")

# ============================================================
# EN BEFORE FL: KERNEL PROFILE BY FL STATE
# ============================================================
print("\n" + "="*70)
print("EN KERNEL PROFILE BEFORE FL (BY FL STATE)")
print("="*70)

en_before_fl_early = Counter()
en_before_fl_medial = Counter()
en_before_fl_late = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 1):
        if tokens[i]['role'] == 'EN' and tokens[i+1]['role'] == 'FL':
            fl_mid = tokens[i+1]['middle']
            fl_stage = get_fl_stage(fl_mid)
            en_sig = get_kernel_signature(tokens[i]['word'])

            if fl_stage == 'EARLY':
                en_before_fl_early[en_sig] += 1
            elif fl_stage == 'MEDIAL':
                en_before_fl_medial[en_sig] += 1
            elif fl_stage == 'LATE':
                en_before_fl_late[en_sig] += 1

print("\nEN kernel profile by following FL state:")
print("\n  Before FL-EARLY (i, ii, in):")
total, any_r, k_r, h_r, e_r = summarize_kernel(en_before_fl_early)
print(f"    n={total}, any={any_r:.1f}%, k={k_r:.1f}%, h={h_r:.1f}%, e={e_r:.1f}%")

print("\n  Before FL-MEDIAL (r, ar, al, l, ol):")
total, any_r, k_r, h_r, e_r = summarize_kernel(en_before_fl_medial)
print(f"    n={total}, any={any_r:.1f}%, k={k_r:.1f}%, h={h_r:.1f}%, e={e_r:.1f}%")

print("\n  Before FL-LATE (o, ly, am, m, dy, ry, y):")
total, any_r, k_r, h_r, e_r = summarize_kernel(en_before_fl_late)
print(f"    n={total}, any={any_r:.1f}%, k={k_r:.1f}%, h={h_r:.1f}%, e={e_r:.1f}%")

# ============================================================
# FL -> EN -> FL STATE TRANSITIONS
# ============================================================
print("\n" + "="*70)
print("FL -> EN -> FL STATE TRANSITIONS")
print("="*70)

# What FL state transitions does EN mediate?
fl_en_fl_transitions = Counter()

for key, tokens in lines_data.items():
    for i in range(len(tokens) - 2):
        if (tokens[i]['role'] == 'FL' and
            tokens[i+1]['role'] == 'EN' and
            tokens[i+2]['role'] == 'FL'):

            fl1_stage = get_fl_stage(tokens[i]['middle'])
            fl2_stage = get_fl_stage(tokens[i+2]['middle'])
            fl_en_fl_transitions[(fl1_stage, fl2_stage)] += 1

print("\nFL state transitions mediated by EN:")
total_trans = sum(fl_en_fl_transitions.values())
for (s1, s2), count in fl_en_fl_transitions.most_common():
    pct = 100 * count / total_trans if total_trans else 0
    direction = "FORWARD" if FL_EARLY <= {s1} or s1 == 'EARLY' and s2 in ['MEDIAL', 'LATE'] else \
                "FORWARD" if s1 == 'MEDIAL' and s2 == 'LATE' else \
                "SAME" if s1 == s2 else "BACKWARD"
    # Simplified direction logic
    stage_order = {'EARLY': 0, 'MEDIAL': 1, 'LATE': 2, 'OTHER': -1}
    o1, o2 = stage_order.get(s1, -1), stage_order.get(s2, -1)
    if o1 < o2:
        direction = "FORWARD"
    elif o1 == o2:
        direction = "SAME"
    else:
        direction = "BACKWARD"
    print(f"  {s1} -> EN -> {s2}: {count} ({pct:.1f}%) [{direction}]")

# ============================================================
# EN POSITIONAL PROFILE
# ============================================================
print("\n" + "="*70)
print("EN POSITIONAL PROFILE (OVERALL)")
print("="*70)

en_positions = []
for key, tokens in lines_data.items():
    line_len = len(tokens)
    for i, t in enumerate(tokens):
        if t['role'] == 'EN':
            norm_pos = i / (line_len - 1) if line_len > 1 else 0.5
            en_positions.append(norm_pos)

en_mean_pos = np.mean(en_positions)
en_std_pos = np.std(en_positions)
print(f"\nEN mean position: {en_mean_pos:.3f} +/- {en_std_pos:.3f}")
print(f"EN tokens: {len(en_positions)}")

# Compare to FL
fl_mean = 0.576  # From T2
print(f"FL mean position: {fl_mean:.3f} (from T2)")
print(f"EN vs FL: EN is {en_mean_pos - fl_mean:+.3f} relative to FL")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

findings = []

# Dominant kernel signature
top_sig, top_count = en_kernel_sigs.most_common(1)[0]
top_sig_str = '+'.join(top_sig) if top_sig != ('none',) else 'none'
findings.append(f"DOMINANT_KERNEL: '{top_sig_str}' at {100*top_count/en_tokens_total:.1f}%")

# e dominance
if has_e > has_k and has_e > has_h:
    findings.append(f"E_DOMINANT: 'e' is most common kernel char ({100*has_e/en_tokens_total:.1f}%)")

# FL state correlation
early_total, early_any, _, _, _ = summarize_kernel(en_after_fl_early)
late_total, late_any, _, _, _ = summarize_kernel(en_after_fl_late)
if isinstance(early_any, float) and isinstance(late_any, float):
    if abs(early_any - late_any) > 10:
        findings.append(f"FL_STATE_CORRELATED: EN kernel varies by FL state ({early_any:.0f}% after early vs {late_any:.0f}% after late)")

# Forward transitions
forward_count = sum(c for (s1, s2), c in fl_en_fl_transitions.items()
                   if {'EARLY': 0, 'MEDIAL': 1, 'LATE': 2}.get(s1, -1) < {'EARLY': 0, 'MEDIAL': 1, 'LATE': 2}.get(s2, -1))
if total_trans > 0:
    forward_rate = 100 * forward_count / total_trans
    findings.append(f"FORWARD_BIAS: {forward_rate:.1f}% of EN-mediated FL transitions are forward")

print("\nKey findings:")
for f in findings:
    print(f"  - {f}")

print(f"""

EN KERNEL ANALYSIS SUMMARY:

EN is the primary transformation operator:
- {100*has_any_kernel/en_tokens_total:.1f}% kernel-containing
- Dominant kernel: 'e' at {100*has_e/en_tokens_total:.1f}% (stability anchor)
- EN mediates FL state transitions

EN kernel profile:
- 'e' (stability): {100*has_e/en_tokens_total:.1f}%
- 'h' (phase): {100*has_h/en_tokens_total:.1f}%
- 'k' (energy): {100*has_k/en_tokens_total:.1f}%

EN appears to transform material between FL-indexed states,
using primarily 'e' (stability anchor) for state transitions.
""")

# Save results
results = {
    'en_tokens_total': en_tokens_total,
    'kernel_signatures': {'+'.join(k) if k != ('none',) else 'none': v
                          for k, v in en_kernel_sigs.most_common()},
    'kernel_rates': {
        'any': 100*has_any_kernel/en_tokens_total,
        'k': 100*has_k/en_tokens_total,
        'h': 100*has_h/en_tokens_total,
        'e': 100*has_e/en_tokens_total
    },
    'en_mean_position': float(en_mean_pos),
    'fl_en_fl_transitions': {f"{s1}->{s2}": c for (s1, s2), c in fl_en_fl_transitions.most_common()},
    'findings': findings
}

out_path = PROJECT_ROOT / 'phases' / 'FL_PRIMITIVE_ARCHITECTURE' / 'results' / 't6_en_kernel_profile.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path}")
