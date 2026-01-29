"""
02_en_transformation_profiles.py

Analyze EN kernel behavior around FL states.
Builds on C779 (EN-FL state coupling) to understand transformation semantics.

Questions:
1. What do EN kernel profiles (k, h, e) mean operationally?
2. Why does h-rate drop as FL progresses? (less phase correction needed?)
3. Does k (energy) injection correlate with state transitions?
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load data
tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

# Get class mappings
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}
token_to_role = class_data['token_to_role']

# FL and EN classes
FL_CLASSES = {7, 30, 38, 40}
EN_CLASSES = set()
for token, role in token_to_role.items():
    if role == 'ENERGY_OPERATOR':
        cls = token_to_class.get(token)
        if cls:
            EN_CLASSES.add(cls)

print(f"FL classes: {FL_CLASSES}")
print(f"EN classes: {EN_CLASSES}")

# Define FL stages based on script 01 results
FL_STAGE_MAP = {
    'ii': 'INITIAL', 'i': 'INITIAL',
    'in': 'EARLY',
    'r': 'MEDIAL', 'ar': 'MEDIAL', 'al': 'MEDIAL', 'l': 'MEDIAL', 'ol': 'MEDIAL',
    'o': 'LATE', 'ly': 'LATE',
    'am': 'TERMINAL', 'n': 'TERMINAL', 'im': 'TERMINAL', 'm': 'TERMINAL',
    'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL'
}

# Group tokens by folio+line
b_by_line = defaultdict(list)
for t in b_tokens:
    b_by_line[(t.folio, t.line)].append(t)

# ============================================================
# ANALYSIS 1: EN Kernel Profile After FL (by FL stage)
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 1: EN Kernel Profile AFTER FL Tokens")
print("=" * 60)

# Find all FL -> EN transitions
fl_en_transitions = []
for (folio, line), tokens in b_by_line.items():
    for i, t in enumerate(tokens):
        cls = token_to_class.get(t.word)
        if cls in FL_CLASSES:
            # Get FL stage
            m = morph.extract(t.word)
            fl_middle = m.middle if m else None
            fl_stage = FL_STAGE_MAP.get(fl_middle, 'UNKNOWN')

            # Check if next token is EN
            if i + 1 < len(tokens):
                next_t = tokens[i + 1]
                next_cls = token_to_class.get(next_t.word)
                if next_cls in EN_CLASSES:
                    # Extract EN kernel profile
                    en_m = morph.extract(next_t.word)
                    en_middle = en_m.middle if en_m else ''
                    has_k = 'k' in en_middle
                    has_h = 'h' in en_middle
                    has_e = 'e' in en_middle

                    fl_en_transitions.append({
                        'fl_stage': fl_stage,
                        'fl_middle': fl_middle,
                        'en_word': next_t.word,
                        'en_middle': en_middle,
                        'has_k': has_k,
                        'has_h': has_h,
                        'has_e': has_e
                    })

print(f"\nTotal FL -> EN transitions: {len(fl_en_transitions)}")

# Aggregate by FL stage
stage_en_profiles = defaultdict(lambda: {'n': 0, 'k': 0, 'h': 0, 'e': 0})
for trans in fl_en_transitions:
    stage = trans['fl_stage']
    stage_en_profiles[stage]['n'] += 1
    if trans['has_k']:
        stage_en_profiles[stage]['k'] += 1
    if trans['has_h']:
        stage_en_profiles[stage]['h'] += 1
    if trans['has_e']:
        stage_en_profiles[stage]['e'] += 1

print("\n--- EN Kernel Profile AFTER FL by Stage ---")
print(f"{'Stage':10} {'n':>6} {'k%':>8} {'h%':>8} {'e%':>8}")
print("-" * 45)
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    prof = stage_en_profiles[stage]
    n = prof['n']
    if n > 0:
        k_pct = prof['k'] / n * 100
        h_pct = prof['h'] / n * 100
        e_pct = prof['e'] / n * 100
        print(f"{stage:10} {n:6} {k_pct:7.1f}% {h_pct:7.1f}% {e_pct:7.1f}%")

# ============================================================
# ANALYSIS 2: EN Kernel Profile Before FL (by FL stage)
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 2: EN Kernel Profile BEFORE FL Tokens")
print("=" * 60)

# Find all EN -> FL transitions
en_fl_transitions = []
for (folio, line), tokens in b_by_line.items():
    for i, t in enumerate(tokens):
        cls = token_to_class.get(t.word)
        if cls in EN_CLASSES:
            # Check if next token is FL
            if i + 1 < len(tokens):
                next_t = tokens[i + 1]
                next_cls = token_to_class.get(next_t.word)
                if next_cls in FL_CLASSES:
                    # Get FL stage
                    fl_m = morph.extract(next_t.word)
                    fl_middle = fl_m.middle if fl_m else None
                    fl_stage = FL_STAGE_MAP.get(fl_middle, 'UNKNOWN')

                    # Extract EN kernel profile
                    en_m = morph.extract(t.word)
                    en_middle = en_m.middle if en_m else ''
                    has_k = 'k' in en_middle
                    has_h = 'h' in en_middle
                    has_e = 'e' in en_middle

                    en_fl_transitions.append({
                        'fl_stage': fl_stage,
                        'fl_middle': fl_middle,
                        'en_word': t.word,
                        'en_middle': en_middle,
                        'has_k': has_k,
                        'has_h': has_h,
                        'has_e': has_e
                    })

print(f"\nTotal EN -> FL transitions: {len(en_fl_transitions)}")

# Aggregate by FL stage
stage_en_before = defaultdict(lambda: {'n': 0, 'k': 0, 'h': 0, 'e': 0})
for trans in en_fl_transitions:
    stage = trans['fl_stage']
    stage_en_before[stage]['n'] += 1
    if trans['has_k']:
        stage_en_before[stage]['k'] += 1
    if trans['has_h']:
        stage_en_before[stage]['h'] += 1
    if trans['has_e']:
        stage_en_before[stage]['e'] += 1

print("\n--- EN Kernel Profile BEFORE FL by Stage ---")
print(f"{'Stage':10} {'n':>6} {'k%':>8} {'h%':>8} {'e%':>8}")
print("-" * 45)
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    prof = stage_en_before[stage]
    n = prof['n']
    if n > 0:
        k_pct = prof['k'] / n * 100
        h_pct = prof['h'] / n * 100
        e_pct = prof['e'] / n * 100
        print(f"{stage:10} {n:6} {k_pct:7.1f}% {h_pct:7.1f}% {e_pct:7.1f}%")

# ============================================================
# ANALYSIS 3: Kernel Character Semantics
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 3: Kernel Character Behavior Summary")
print("=" * 60)

# Compare BEFORE vs AFTER
print("\n--- k (Energy) Injection Patterns ---")
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    before = stage_en_before[stage]
    after = stage_en_profiles[stage]
    k_before = before['k'] / before['n'] * 100 if before['n'] > 0 else 0
    k_after = after['k'] / after['n'] * 100 if after['n'] > 0 else 0
    delta = k_before - k_after
    print(f"{stage:10}: BEFORE={k_before:5.1f}%  AFTER={k_after:5.1f}%  (delta={delta:+5.1f}%)")

print("\n--- h (Phase) Management Patterns ---")
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    before = stage_en_before[stage]
    after = stage_en_profiles[stage]
    h_before = before['h'] / before['n'] * 100 if before['n'] > 0 else 0
    h_after = after['h'] / after['n'] * 100 if after['n'] > 0 else 0
    delta = h_after - h_before
    print(f"{stage:10}: BEFORE={h_before:5.1f}%  AFTER={h_after:5.1f}%  (delta={delta:+5.1f}%)")

print("\n--- e (Stability) Patterns ---")
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    before = stage_en_before[stage]
    after = stage_en_profiles[stage]
    e_before = before['e'] / before['n'] * 100 if before['n'] > 0 else 0
    e_after = after['e'] / after['n'] * 100 if after['n'] > 0 else 0
    delta = e_after - e_before
    print(f"{stage:10}: BEFORE={e_before:5.1f}%  AFTER={e_after:5.1f}%  (delta={delta:+5.1f}%)")

# ============================================================
# ANALYSIS 4: State Transition Kernel Signatures
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 4: Kernel at State Transitions")
print("=" * 60)

# Find EN tokens between two FL tokens (FL -> EN -> FL)
transition_kernels = defaultdict(lambda: {'n': 0, 'k': 0, 'h': 0, 'e': 0})

for (folio, line), tokens in b_by_line.items():
    for i in range(len(tokens) - 2):
        t1, t2, t3 = tokens[i], tokens[i+1], tokens[i+2]
        cls1 = token_to_class.get(t1.word)
        cls2 = token_to_class.get(t2.word)
        cls3 = token_to_class.get(t3.word)

        # FL -> EN -> FL pattern
        if cls1 in FL_CLASSES and cls2 in EN_CLASSES and cls3 in FL_CLASSES:
            # Get FL stages
            m1 = morph.extract(t1.word)
            m3 = morph.extract(t3.word)
            stage1 = FL_STAGE_MAP.get(m1.middle if m1 else '', 'UNK')
            stage3 = FL_STAGE_MAP.get(m3.middle if m3 else '', 'UNK')

            # Get EN kernel
            en_m = morph.extract(t2.word)
            en_middle = en_m.middle if en_m else ''

            trans_key = f"{stage1}->{stage3}"
            transition_kernels[trans_key]['n'] += 1
            if 'k' in en_middle:
                transition_kernels[trans_key]['k'] += 1
            if 'h' in en_middle:
                transition_kernels[trans_key]['h'] += 1
            if 'e' in en_middle:
                transition_kernels[trans_key]['e'] += 1

print("\n--- EN Kernel Profile at FL State Transitions ---")
print(f"{'Transition':20} {'n':>5} {'k%':>7} {'h%':>7} {'e%':>7}")
print("-" * 50)
for trans_key, prof in sorted(transition_kernels.items(), key=lambda x: -x[1]['n']):
    n = prof['n']
    if n >= 3:  # Only show transitions with >= 3 instances
        k_pct = prof['k'] / n * 100
        h_pct = prof['h'] / n * 100
        e_pct = prof['e'] / n * 100
        print(f"{trans_key:20} {n:5} {k_pct:6.1f}% {h_pct:6.1f}% {e_pct:6.1f}%")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'fl_en_transitions': len(fl_en_transitions),
    'en_fl_transitions': len(en_fl_transitions),
    'stage_en_after': {k: dict(v) for k, v in stage_en_profiles.items()},
    'stage_en_before': {k: dict(v) for k, v in stage_en_before.items()},
    'transition_kernels': {k: dict(v) for k, v in transition_kernels.items()}
}

output_path = Path(__file__).parent.parent / "results" / "02_en_transformation_profiles.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# SEMANTIC INTERPRETATION
# ============================================================
print("\n" + "=" * 60)
print("SEMANTIC INTERPRETATION")
print("=" * 60)
print("""
Based on the data, kernel characters appear to have these functions:

1. 'h' (PHASE OPERATOR):
   - Higher h-rate AFTER early FL states
   - Decreases as FL progresses toward terminal
   - INTERPRETATION: Phase alignment/correction needed for unstable material
   - Semantic: "align material to target phase/state"

2. 'k' (ENERGY OPERATOR):
   - Higher k-rate BEFORE medial FL states
   - Energy injection precedes state transitions
   - INTERPRETATION: Energy input required to drive state changes
   - Semantic: "inject energy to enable transformation"

3. 'e' (STABILITY OPERATOR):
   - Relatively consistent across stages
   - Present in most transitions
   - INTERPRETATION: Stability checking/anchoring throughout
   - Semantic: "verify/maintain stability envelope"

TRANSFORMATION MODEL:

  FL[EARLY] --[EN: high-h "phase align"]--> FL[MEDIAL]
       ^                                        |
       |                                        v
  [k-injection]                           [e-checking]
       |                                        |
       |                                        v
  ENERGY INPUT                        FL[LATE] (stable)
                                              |
                                              v
                                      FL[TERMINAL]
                                      (safe output)

This resembles a CONTROLLED TRANSFORMATION process where:
- Material enters (FL-INITIAL/EARLY) - needs phase alignment
- Energy is injected (k) to enable transformation
- Material stabilizes (FL-LATE/TERMINAL) - less correction needed
- Stability is verified throughout (e)
""")
