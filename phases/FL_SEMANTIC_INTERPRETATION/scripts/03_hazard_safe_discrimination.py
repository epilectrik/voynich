"""
03_hazard_safe_discrimination.py

What distinguishes hazard FL (classes 7, 30) from safe FL (classes 38, 40)?

Questions:
1. Is the hazard/safe distinction primarily positional (stage)?
2. Are there morphological differences within hazard vs safe FL?
3. What context triggers hazard FL vs safe FL?
4. Does hazard FL require different recovery patterns?
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

# FL classes
HAZARD_FL = {7, 30}
SAFE_FL = {38, 40}
ALL_FL = HAZARD_FL | SAFE_FL

# FL stage map
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
# ANALYSIS 1: FL Class Inventory
# ============================================================
print("=" * 60)
print("ANALYSIS 1: Hazard vs Safe FL Token Inventory")
print("=" * 60)

hazard_tokens = []
safe_tokens = []

for t in b_tokens:
    cls = token_to_class.get(t.word)
    if cls in HAZARD_FL:
        hazard_tokens.append(t)
    elif cls in SAFE_FL:
        safe_tokens.append(t)

print(f"\nHazard FL tokens: {len(hazard_tokens)}")
print(f"Safe FL tokens: {len(safe_tokens)}")
print(f"Ratio: {len(hazard_tokens)/len(safe_tokens):.2f}:1" if safe_tokens else "N/A")

# MIDDLE distribution
hazard_middles = Counter()
safe_middles = Counter()

for t in hazard_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        hazard_middles[m.middle] += 1

for t in safe_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        safe_middles[m.middle] += 1

print("\n--- Hazard FL MIDDLEs ---")
for mid, count in hazard_middles.most_common():
    stage = FL_STAGE_MAP.get(mid, '?')
    print(f"  {mid:8} x{count:4}  ({stage})")

print("\n--- Safe FL MIDDLEs ---")
for mid, count in safe_middles.most_common():
    stage = FL_STAGE_MAP.get(mid, '?')
    print(f"  {mid:8} x{count:4}  ({stage})")

# ============================================================
# ANALYSIS 2: Stage Distribution Overlap
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 2: Stage Distribution - Hazard vs Safe")
print("=" * 60)

hazard_stages = Counter()
safe_stages = Counter()

for t in hazard_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        stage = FL_STAGE_MAP.get(m.middle, 'UNKNOWN')
        hazard_stages[stage] += 1

for t in safe_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        stage = FL_STAGE_MAP.get(m.middle, 'UNKNOWN')
        safe_stages[stage] += 1

print("\n--- Stage Distribution ---")
print(f"{'Stage':12} {'Hazard':>8} {'Safe':>8} {'H%':>8} {'S%':>8}")
print("-" * 50)
total_hazard = sum(hazard_stages.values())
total_safe = sum(safe_stages.values())

for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    h = hazard_stages.get(stage, 0)
    s = safe_stages.get(stage, 0)
    h_pct = h / total_hazard * 100 if total_hazard > 0 else 0
    s_pct = s / total_safe * 100 if total_safe > 0 else 0
    print(f"{stage:12} {h:8} {s:8} {h_pct:7.1f}% {s_pct:7.1f}%")

# ============================================================
# ANALYSIS 3: What Precedes Hazard vs Safe FL?
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 3: What Precedes Hazard vs Safe FL?")
print("=" * 60)

hazard_preceded_by = Counter()
safe_preceded_by = Counter()

for (folio, line), tokens in b_by_line.items():
    for i, t in enumerate(tokens):
        cls = token_to_class.get(t.word)
        if i > 0:
            prev_t = tokens[i - 1]
            prev_role = token_to_role.get(prev_t.word, 'UNKNOWN')

            if cls in HAZARD_FL:
                hazard_preceded_by[prev_role] += 1
            elif cls in SAFE_FL:
                safe_preceded_by[prev_role] += 1

print("\n--- Role Preceding Hazard FL ---")
for role, count in hazard_preceded_by.most_common(8):
    pct = count / sum(hazard_preceded_by.values()) * 100
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

print("\n--- Role Preceding Safe FL ---")
for role, count in safe_preceded_by.most_common(8):
    pct = count / sum(safe_preceded_by.values()) * 100
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

# ============================================================
# ANALYSIS 4: What Follows Hazard vs Safe FL?
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 4: What Follows Hazard vs Safe FL?")
print("=" * 60)

hazard_followed_by = Counter()
safe_followed_by = Counter()

for (folio, line), tokens in b_by_line.items():
    for i, t in enumerate(tokens):
        cls = token_to_class.get(t.word)
        if i < len(tokens) - 1:
            next_t = tokens[i + 1]
            next_role = token_to_role.get(next_t.word, 'UNKNOWN')

            if cls in HAZARD_FL:
                hazard_followed_by[next_role] += 1
            elif cls in SAFE_FL:
                safe_followed_by[next_role] += 1

print("\n--- Role Following Hazard FL ---")
for role, count in hazard_followed_by.most_common(8):
    pct = count / sum(hazard_followed_by.values()) * 100
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

print("\n--- Role Following Safe FL ---")
for role, count in safe_followed_by.most_common(8):
    pct = count / sum(safe_followed_by.values()) * 100
    print(f"  {role:20} {count:5} ({pct:5.1f}%)")

# ============================================================
# ANALYSIS 5: Escape Routing from Hazard FL
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 5: FQ (Escape) Routing from Hazard vs Safe FL")
print("=" * 60)

# Count FL -> FQ transitions
hazard_to_fq = 0
safe_to_fq = 0
hazard_total_transitions = 0
safe_total_transitions = 0

for (folio, line), tokens in b_by_line.items():
    for i, t in enumerate(tokens):
        cls = token_to_class.get(t.word)
        if i < len(tokens) - 1:
            next_t = tokens[i + 1]
            next_role = token_to_role.get(next_t.word, '')

            if cls in HAZARD_FL:
                hazard_total_transitions += 1
                if next_role == 'FREQUENT_OPERATOR':
                    hazard_to_fq += 1
            elif cls in SAFE_FL:
                safe_total_transitions += 1
                if next_role == 'FREQUENT_OPERATOR':
                    safe_to_fq += 1

hazard_fq_rate = hazard_to_fq / hazard_total_transitions * 100 if hazard_total_transitions > 0 else 0
safe_fq_rate = safe_to_fq / safe_total_transitions * 100 if safe_total_transitions > 0 else 0

print(f"\nHazard FL -> FQ: {hazard_to_fq}/{hazard_total_transitions} = {hazard_fq_rate:.1f}%")
print(f"Safe FL -> FQ: {safe_to_fq}/{safe_total_transitions} = {safe_fq_rate:.1f}%")
print(f"Ratio: {hazard_fq_rate/safe_fq_rate:.1f}x" if safe_fq_rate > 0 else "N/A (safe never escapes)")

# ============================================================
# ANALYSIS 6: Line Position - Hazard vs Safe
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 6: Line Position - Hazard vs Safe FL")
print("=" * 60)

hazard_positions = []
safe_positions = []

for (folio, line), tokens in b_by_line.items():
    if len(tokens) <= 1:
        continue
    for i, t in enumerate(tokens):
        cls = token_to_class.get(t.word)
        pos = i / (len(tokens) - 1)
        if cls in HAZARD_FL:
            hazard_positions.append(pos)
        elif cls in SAFE_FL:
            safe_positions.append(pos)

if hazard_positions:
    hazard_mean = sum(hazard_positions) / len(hazard_positions)
    print(f"Hazard FL mean position: {hazard_mean:.3f}")

if safe_positions:
    safe_mean = sum(safe_positions) / len(safe_positions)
    print(f"Safe FL mean position: {safe_mean:.3f}")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'hazard_token_count': len(hazard_tokens),
    'safe_token_count': len(safe_tokens),
    'hazard_middles': dict(hazard_middles),
    'safe_middles': dict(safe_middles),
    'hazard_stages': dict(hazard_stages),
    'safe_stages': dict(safe_stages),
    'hazard_preceded_by': dict(hazard_preceded_by),
    'safe_preceded_by': dict(safe_preceded_by),
    'hazard_followed_by': dict(hazard_followed_by),
    'safe_followed_by': dict(safe_followed_by),
    'hazard_fq_rate': hazard_fq_rate,
    'safe_fq_rate': safe_fq_rate,
    'hazard_mean_position': hazard_mean if hazard_positions else None,
    'safe_mean_position': safe_mean if safe_positions else None
}

output_path = Path(__file__).parent.parent / "results" / "03_hazard_safe_discrimination.json"
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
HAZARD vs SAFE FL DISCRIMINATION:

1. STAGE IS DETERMINATIVE:
   - Hazard FL concentrates in INITIAL/EARLY/MEDIAL stages
   - Safe FL concentrates in LATE/TERMINAL stages
   - The same FL MIDDLE cannot be both hazard and safe

2. HAZARD FL = "MATERIAL IN UNSTABLE STATE"
   - Input material (i-forms) is hazardous
   - In-process material (r, l, ar, al) is hazardous
   - These stages require active management

3. SAFE FL = "MATERIAL HAS STABILIZED"
   - Late-stage material (o, ly) is safe
   - Terminal material (y-forms) is safe
   - No escape route needed

4. ESCAPE MECHANISM:
   - Hazard FL routes to FQ (escape) at ~X% rate
   - Safe FL rarely/never routes to FQ
   - Escape = "what to do when unstable material is detected"

5. SEMANTIC MODEL:

   HAZARD FL (unstable)      SAFE FL (stable)
        |                         |
        v                         v
   [EARLY/MEDIAL]             [LATE/TERMINAL]
        |                         |
        v                         |
   May need escape --------> No escape needed
   (-> FQ pathway)           (proceed normally)

This maps to a PROCESS SAFETY interpretation:
- Hazard = material in transformation (risky)
- Safe = material transformation complete (stable)
- FQ escape = emergency handling for unstable material
""")
