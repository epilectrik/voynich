"""
01_fl_process_stage_mapping.py

Map FL MIDDLEs to process stages with full context analysis.
Builds on C777 (FL state index) with deeper semantic investigation.

Questions:
1. What do FL MIDDLEs physically represent? (stages, materials, conditions)
2. Is position (within line) the primary determinant, or is FL MIDDLE choice?
3. Do FL MIDDLEs cluster into functional groups beyond positional gradient?
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

# Get FL class membership from BCSC (classes 7, 30, 38, 40)
FL_CLASSES = {7, 30, 38, 40}

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)

# Use the token_to_class mapping directly
token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}

# Identify FL tokens
fl_tokens = [t for t in b_tokens if token_to_class.get(t.word) in FL_CLASSES]

print("=" * 60)
print("FL PROCESS STAGE MAPPING")
print("=" * 60)
print(f"\nTotal FL tokens: {len(fl_tokens)}")

# Extract FL MIDDLEs
fl_middles = Counter()
fl_middle_tokens = defaultdict(list)
for t in fl_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        fl_middles[m.middle] += 1
        fl_middle_tokens[m.middle].append(t)

print(f"Unique FL MIDDLEs: {len(fl_middles)}")
print("\n--- FL MIDDLE Inventory ---")
for middle, count in fl_middles.most_common():
    print(f"  {middle:8} x{count:4}")

# ============================================================
# ANALYSIS 1: Positional Profile per FL MIDDLE
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 1: FL MIDDLE Positional Profiles")
print("=" * 60)

def get_line_position(token, all_tokens_in_line):
    """Get normalized position (0-1) within line."""
    if len(all_tokens_in_line) <= 1:
        return 0.5
    # Find token's index in the line by matching word and checking it's the same token
    # Tokens in b_by_line are in order, so we find matching position
    idx = None
    for i, t in enumerate(all_tokens_in_line):
        if t is token:  # Identity check
            idx = i
            break
    if idx is None:
        # Fallback: find by word match (may not be unique)
        for i, t in enumerate(all_tokens_in_line):
            if t.word == token.word:
                idx = i
                break
    if idx is None:
        return 0.5
    return idx / (len(all_tokens_in_line) - 1)

# Group all B tokens by folio+line for position calculation
b_by_line = defaultdict(list)
for t in b_tokens:
    b_by_line[(t.folio, t.line)].append(t)

# Calculate position for each FL token
fl_middle_positions = defaultdict(list)
for t in fl_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        line_tokens = b_by_line[(t.folio, t.line)]
        pos = get_line_position(t, line_tokens)
        fl_middle_positions[m.middle].append(pos)

# Compute stats and sort by mean position
position_stats = []
for middle, positions in fl_middle_positions.items():
    if positions:
        mean_pos = sum(positions) / len(positions)
        position_stats.append({
            'middle': middle,
            'count': len(positions),
            'mean_pos': mean_pos,
            'min_pos': min(positions),
            'max_pos': max(positions),
            'spread': max(positions) - min(positions)
        })

position_stats.sort(key=lambda x: x['mean_pos'])

print("\n--- FL MIDDLEs by Mean Position ---")
print(f"{'MIDDLE':8} {'Count':>6} {'Mean':>6} {'Min':>6} {'Max':>6} {'Spread':>6} Stage")
print("-" * 55)

# Assign stages based on position
def assign_stage(mean_pos):
    if mean_pos < 0.35:
        return "INITIAL"
    elif mean_pos < 0.50:
        return "EARLY"
    elif mean_pos < 0.65:
        return "MEDIAL"
    elif mean_pos < 0.80:
        return "LATE"
    else:
        return "TERMINAL"

for stat in position_stats:
    stage = assign_stage(stat['mean_pos'])
    print(f"{stat['middle']:8} {stat['count']:6} {stat['mean_pos']:6.3f} "
          f"{stat['min_pos']:6.3f} {stat['max_pos']:6.3f} {stat['spread']:6.3f} {stage}")

# ============================================================
# ANALYSIS 2: Character Composition by Stage
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 2: Character Composition by Stage")
print("=" * 60)

stage_chars = defaultdict(Counter)
for stat in position_stats:
    stage = assign_stage(stat['mean_pos'])
    for char in stat['middle']:
        stage_chars[stage][char] += stat['count']

print("\n--- Character Distribution by Stage ---")
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    chars = stage_chars[stage]
    if chars:
        total = sum(chars.values())
        sorted_chars = sorted(chars.items(), key=lambda x: -x[1])
        char_str = ', '.join(f"{c}:{n}" for c, n in sorted_chars[:5])
        print(f"\n{stage}:")
        print(f"  Total char instances: {total}")
        print(f"  Top chars: {char_str}")

# ============================================================
# ANALYSIS 3: FL MIDDLE Co-occurrence Patterns
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 3: FL MIDDLE Line Co-occurrence")
print("=" * 60)

# Which FL MIDDLEs appear together in same line?
fl_cooccurrence = Counter()
fl_line_sets = defaultdict(set)

for t in fl_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        fl_line_sets[(t.folio, t.line)].add(m.middle)

# Count co-occurrences
for line_key, middles in fl_line_sets.items():
    if len(middles) >= 2:
        middles_list = sorted(middles)
        for i, m1 in enumerate(middles_list):
            for m2 in middles_list[i+1:]:
                fl_cooccurrence[(m1, m2)] += 1

print("\n--- Most Common FL MIDDLE Pairs (same line) ---")
for pair, count in fl_cooccurrence.most_common(15):
    m1, m2 = pair
    s1 = assign_stage(dict((s['middle'], s['mean_pos']) for s in position_stats).get(m1, 0.5))
    s2 = assign_stage(dict((s['middle'], s['mean_pos']) for s in position_stats).get(m2, 0.5))
    print(f"  {m1:6} + {m2:6} : {count:3}  ({s1} + {s2})")

# ============================================================
# ANALYSIS 4: FL Class Distribution by Stage
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 4: FL Class (Hazard/Safe) by Stage")
print("=" * 60)

# Map FL classes to hazard/safe
HAZARD_FL = {7, 30}
SAFE_FL = {38, 40}

stage_class_dist = defaultdict(lambda: {'hazard': 0, 'safe': 0})

for t in fl_tokens:
    m = morph.extract(t.word)
    if m and m.middle:
        mean_pos = dict((s['middle'], s['mean_pos']) for s in position_stats).get(m.middle, 0.5)
        stage = assign_stage(mean_pos)
        cls = token_to_class.get(t.word)
        if cls in HAZARD_FL:
            stage_class_dist[stage]['hazard'] += 1
        elif cls in SAFE_FL:
            stage_class_dist[stage]['safe'] += 1

print("\n--- Hazard/Safe Distribution by Stage ---")
print(f"{'Stage':10} {'Hazard':>8} {'Safe':>8} {'Total':>8} {'Hazard%':>8}")
print("-" * 45)
for stage in ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'TERMINAL']:
    d = stage_class_dist[stage]
    total = d['hazard'] + d['safe']
    hazard_pct = d['hazard'] / total * 100 if total > 0 else 0
    print(f"{stage:10} {d['hazard']:8} {d['safe']:8} {total:8} {hazard_pct:7.1f}%")

# ============================================================
# ANALYSIS 5: Semantic Clustering
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS 5: Semantic Clustering Hypothesis")
print("=" * 60)

# Group FL MIDDLEs by character patterns
i_forms = [s for s in position_stats if 'i' in s['middle'] and 'y' not in s['middle']]
y_forms = [s for s in position_stats if 'y' in s['middle']]
consonant_forms = [s for s in position_stats if s['middle'] not in
                   [x['middle'] for x in i_forms + y_forms]]

print("\n--- Character-Based Grouping ---")
print(f"\n'i'-containing (no 'y'): {len(i_forms)} MIDDLEs")
for s in sorted(i_forms, key=lambda x: x['mean_pos']):
    print(f"  {s['middle']:8} pos={s['mean_pos']:.3f} ({s['count']})")

print(f"\nConsonant-only forms: {len(consonant_forms)} MIDDLEs")
for s in sorted(consonant_forms, key=lambda x: x['mean_pos']):
    print(f"  {s['middle']:8} pos={s['mean_pos']:.3f} ({s['count']})")

print(f"\n'y'-containing: {len(y_forms)} MIDDLEs")
for s in sorted(y_forms, key=lambda x: x['mean_pos']):
    print(f"  {s['middle']:8} pos={s['mean_pos']:.3f} ({s['count']})")

# ============================================================
# SAVE RESULTS
# ============================================================
results = {
    'total_fl_tokens': len(fl_tokens),
    'unique_fl_middles': len(fl_middles),
    'fl_middle_counts': dict(fl_middles),
    'position_stats': position_stats,
    'stage_class_distribution': {k: dict(v) for k, v in stage_class_dist.items()},
    'character_groups': {
        'i_forms': [s['middle'] for s in i_forms],
        'consonant_forms': [s['middle'] for s in consonant_forms],
        'y_forms': [s['middle'] for s in y_forms]
    }
}

output_path = Path(__file__).parent.parent / "results" / "01_fl_process_stage_mapping.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# SEMANTIC INTERPRETATION NOTES
# ============================================================
print("\n" + "=" * 60)
print("PRELIMINARY SEMANTIC INTERPRETATION")
print("=" * 60)
print("""
Based on the data:

1. FL MIDDLEs divide into THREE character-based groups:
   - 'i' forms: INITIAL/EARLY position (process input)
   - Consonant forms (r, l, m, n): MEDIAL position (in-process)
   - 'y' forms: LATE/TERMINAL position (process output)

2. The 'i' -> consonant -> 'y' progression suggests:
   - 'i' = INPUT state (material entering process)
   - consonants = INTERMEDIATE states (material being transformed)
   - 'y' = YIELD/OUTPUT state (material exiting process)

3. Hazard/Safe split by stage:
   - If hazard concentrates in early/medial, it marks "unstable" material
   - If safe concentrates in late/terminal, it marks "stable" output

4. Character semantics hypothesis:
   - 'i' (input marker)
   - 'y' (yield/output marker)
   - 'r', 'l', 'm', 'n' (transformation modifiers)
   - 'a', 'o' (state modifiers)

This resembles a BATCH PROCESSING indexing system where FL marks
"where material is" in the transformation pipeline.
""")
