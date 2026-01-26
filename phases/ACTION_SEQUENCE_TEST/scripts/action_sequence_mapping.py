"""
ACTION SEQUENCE TEST: Brunschwig Procedural Flow → B Grammar Transitions

HYPOTHESIS: Brunschwig's procedural action sequence maps to B grammar class
transition patterns.

Brunschwig typical flow:
  GATHER (28%) → CHOP (16%) → [STEEP] → DISTILL (40%) → [REFINE]

B grammar has:
  - 49 instruction classes with transition probabilities
  - Role taxonomy (CORE_CONTROL, ENERGY_OPERATOR, AUXILIARY, etc.)
  - Phase-ordering hazards (41% of forbidden transitions)
  - LINK marks monitoring/intervention boundary

TEST: Do procedural phases map to instruction class phases?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import numpy as np
import json

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("ACTION SEQUENCE TEST: Brunschwig Flow -> B Grammar Transitions")
print("=" * 70)

# =============================================================================
# STEP 1: Load B class mapping
# =============================================================================
print("\n[Step 1] Loading B grammar class data...")

# Load class token map if available
try:
    with open('data/class_token_map.json', 'r') as f:
        class_token_map = json.load(f)
    print(f"  Loaded class_token_map.json: {len(class_token_map)} classes")
except:
    print("  class_token_map.json not found, will compute from scratch")
    class_token_map = None

# Build B token stream with morphology
b_tokens = []
for token in tx.currier_b():
    if token.word:
        m = morph.extract(token.word)
        b_tokens.append({
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix or '',
            'middle': m.middle or '',
            'suffix': m.suffix or '',
        })

print(f"  B tokens: {len(b_tokens)}")

# =============================================================================
# STEP 2: Define Brunschwig action phases
# =============================================================================
print("\n[Step 2] Defining Brunschwig action phases...")

# Brunschwig action taxonomy mapped to procedural phases
BRUNSCHWIG_PHASES = {
    'ACQUISITION': ['GATHER', 'COLLECT', 'PLUCK', 'SELECT', 'OBTAIN'],
    'PREPARATION': ['WASH', 'CLEAN', 'STRIP', 'KILL'],
    'BREAKDOWN': ['CHOP', 'POUND', 'CRUSH', 'BREAK', 'BORE', 'BUTCHER'],
    'PRETREATMENT': ['STEEP', 'MACERATE', 'MIX', 'DRY'],
    'EXTRACTION': ['DISTILL'],
    'REFINEMENT': ['REDISTILL', 'REFINE', 'FILTER'],
}

# Expected procedural flow (from Brunschwig taxonomy)
EXPECTED_FLOW = [
    'ACQUISITION',   # First: get materials
    'PREPARATION',   # Second: clean/prepare
    'BREAKDOWN',     # Third: mechanical processing
    'PRETREATMENT',  # Fourth: optional chemical prep
    'EXTRACTION',    # Fifth: heat extraction (main event)
    'REFINEMENT',    # Sixth: optional purification
]

print("  Brunschwig procedural phases:")
for i, phase in enumerate(EXPECTED_FLOW):
    actions = BRUNSCHWIG_PHASES[phase]
    print(f"    {i+1}. {phase}: {', '.join(actions)}")

# =============================================================================
# STEP 3: Map B PREFIX groups to hypothesized phases
# =============================================================================
print("\n[Step 3] Mapping B PREFIX patterns to hypothesized phases...")

# From BCSC and morphology constraints:
# - PREFIX has positional grammar (C371)
# - Different PREFIX families have different roles
# - qo-prefix = escape route (C397)
# - LINK marks monitoring/intervention boundary

# Let's analyze PREFIX distribution by line position
prefix_by_position = defaultdict(lambda: defaultdict(int))
prefix_total = Counter()

for tok in b_tokens:
    prefix_total[tok['prefix']] += 1

# Get position within line for each token
folio_line_tokens = defaultdict(list)
for tok in b_tokens:
    key = (tok['folio'], tok['line'])
    folio_line_tokens[key].append(tok)

# Compute relative position (0=start, 1=end) for each token
position_prefix = defaultdict(list)  # prefix -> list of relative positions

for key, tokens in folio_line_tokens.items():
    n = len(tokens)
    if n < 2:
        continue
    for i, tok in enumerate(tokens):
        rel_pos = i / (n - 1)  # 0 to 1
        position_prefix[tok['prefix']].append(rel_pos)

print("\n  PREFIX by mean line position:")
prefix_positions = []
for prefix, positions in position_prefix.items():
    if len(positions) >= 100:  # Minimum sample
        mean_pos = np.mean(positions)
        prefix_positions.append((prefix, mean_pos, len(positions)))

prefix_positions.sort(key=lambda x: x[1])
print("  (Sorted early -> late)")
for prefix, pos, count in prefix_positions[:10]:
    phase_guess = "EARLY" if pos < 0.4 else ("LATE" if pos > 0.6 else "MIDDLE")
    print(f"    {prefix or '(none)'}: {pos:.3f} (n={count}) [{phase_guess}]")
print("    ...")
for prefix, pos, count in prefix_positions[-5:]:
    phase_guess = "EARLY" if pos < 0.4 else ("LATE" if pos > 0.6 else "MIDDLE")
    print(f"    {prefix or '(none)'}: {pos:.3f} (n={count}) [{phase_guess}]")

# =============================================================================
# STEP 4: Analyze line-level phase structure
# =============================================================================
print("\n[Step 4] Analyzing line-level phase structure...")

# Hypothesis: Lines follow a phase sequence like Brunschwig recipes
# Test: Do PREFIX transitions within lines follow a consistent pattern?

# Define PREFIX phase mapping based on position analysis
EARLY_PREFIXES = set()
MIDDLE_PREFIXES = set()
LATE_PREFIXES = set()

for prefix, pos, count in prefix_positions:
    if pos < 0.4:
        EARLY_PREFIXES.add(prefix)
    elif pos > 0.6:
        LATE_PREFIXES.add(prefix)
    else:
        MIDDLE_PREFIXES.add(prefix)

print(f"\n  EARLY prefixes (pos < 0.4): {len(EARLY_PREFIXES)}")
print(f"  MIDDLE prefixes (0.4-0.6): {len(MIDDLE_PREFIXES)}")
print(f"  LATE prefixes (pos > 0.6): {len(LATE_PREFIXES)}")

# Count phase transitions within lines
phase_transitions = Counter()
for key, tokens in folio_line_tokens.items():
    if len(tokens) < 3:
        continue
    for i in range(len(tokens) - 1):
        p1 = tokens[i]['prefix']
        p2 = tokens[i+1]['prefix']

        # Map to phase
        phase1 = 'E' if p1 in EARLY_PREFIXES else ('L' if p1 in LATE_PREFIXES else 'M')
        phase2 = 'E' if p2 in EARLY_PREFIXES else ('L' if p2 in LATE_PREFIXES else 'M')

        phase_transitions[(phase1, phase2)] += 1

total_trans = sum(phase_transitions.values())
print("\n  Phase transitions (E=early, M=middle, L=late):")
for (p1, p2), count in sorted(phase_transitions.items(), key=lambda x: -x[1]):
    pct = count / total_trans * 100
    direction = ""
    if p1 == 'E' and p2 == 'M':
        direction = "FORWARD (expected)"
    elif p1 == 'M' and p2 == 'L':
        direction = "FORWARD (expected)"
    elif p1 == 'E' and p2 == 'L':
        direction = "SKIP FORWARD"
    elif p1 == 'L' and p2 == 'E':
        direction = "BACKWARD (reset?)"
    elif p1 == 'L' and p2 == 'M':
        direction = "BACKWARD"
    elif p1 == 'M' and p2 == 'E':
        direction = "BACKWARD"
    print(f"    {p1} -> {p2}: {count:5d} ({pct:5.1f}%) {direction}")

# =============================================================================
# STEP 5: Test Brunschwig-style forward flow
# =============================================================================
print("\n[Step 5] Testing Brunschwig-style forward flow hypothesis...")

# If Voynich follows Brunschwig flow, we expect:
# - E->M and M->L transitions to dominate
# - L->E transitions to mark "recipe boundaries" (start of new procedure)
# - Backward transitions (L->M, M->E) to be rare

forward_count = phase_transitions.get(('E', 'M'), 0) + phase_transitions.get(('M', 'L'), 0)
backward_count = phase_transitions.get(('L', 'M'), 0) + phase_transitions.get(('M', 'E'), 0)
reset_count = phase_transitions.get(('L', 'E'), 0)
stay_count = phase_transitions.get(('E', 'E'), 0) + phase_transitions.get(('M', 'M'), 0) + phase_transitions.get(('L', 'L'), 0)

print(f"\n  Forward (E->M, M->L): {forward_count} ({forward_count/total_trans*100:.1f}%)")
print(f"  Backward (L->M, M->E): {backward_count} ({backward_count/total_trans*100:.1f}%)")
print(f"  Reset (L->E): {reset_count} ({reset_count/total_trans*100:.1f}%)")
print(f"  Stay (E->E, M->M, L->L): {stay_count} ({stay_count/total_trans*100:.1f}%)")

forward_ratio = forward_count / (backward_count + 1)
print(f"\n  Forward/Backward ratio: {forward_ratio:.2f}x")

if forward_ratio > 2:
    print("  [CONSISTENT] Strong forward flow, consistent with Brunschwig procedural model")
elif forward_ratio > 1:
    print("  [WEAK] Slight forward bias, weakly consistent with procedural model")
else:
    print("  [INCONSISTENT] No forward bias, inconsistent with procedural model")

# =============================================================================
# STEP 6: Folio-level phase distribution
# =============================================================================
print("\n[Step 6] Analyzing folio-level phase distribution...")

# Do different folios have different phase profiles?
# This would indicate different recipe types (herb-heavy vs extraction-heavy)

folio_phases = defaultdict(lambda: {'E': 0, 'M': 0, 'L': 0})
for tok in b_tokens:
    prefix = tok['prefix']
    phase = 'E' if prefix in EARLY_PREFIXES else ('L' if prefix in LATE_PREFIXES else 'M')
    folio_phases[tok['folio']][phase] += 1

# Compute phase ratios per folio
folio_ratios = []
for folio, counts in folio_phases.items():
    total = sum(counts.values())
    if total < 50:
        continue
    e_ratio = counts['E'] / total
    m_ratio = counts['M'] / total
    l_ratio = counts['L'] / total
    folio_ratios.append({
        'folio': folio,
        'early': e_ratio,
        'middle': m_ratio,
        'late': l_ratio,
        'total': total,
    })

# Sort by early ratio (acquisition-heavy folios)
folio_ratios.sort(key=lambda x: x['early'], reverse=True)

print("\n  Top 5 EARLY-heavy folios (acquisition/preparation-heavy?):")
for r in folio_ratios[:5]:
    print(f"    {r['folio']}: E={r['early']*100:.1f}% M={r['middle']*100:.1f}% L={r['late']*100:.1f}%")

print("\n  Top 5 LATE-heavy folios (extraction/refinement-heavy?):")
folio_ratios.sort(key=lambda x: x['late'], reverse=True)
for r in folio_ratios[:5]:
    print(f"    {r['folio']}: E={r['early']*100:.1f}% M={r['middle']*100:.1f}% L={r['late']*100:.1f}%")

# =============================================================================
# STEP 7: Correlation with REGIME
# =============================================================================
print("\n[Step 7] Testing correlation with REGIME classification...")

# Load REGIME mapping
try:
    with open('phases/MATERIAL_REGIME_MAPPING/results/regime_folio_mapping.json', 'r') as f:
        regime_mapping = json.load(f)

    folio_to_regime = {}
    for regime, folios in regime_mapping.items():
        for folio in folios:
            folio_to_regime[folio] = regime

    print(f"  Loaded REGIME mapping: {len(folio_to_regime)} folios")

    # Compute mean phase ratios per REGIME
    regime_phases = defaultdict(lambda: {'E': [], 'M': [], 'L': []})
    for r in folio_ratios:
        if r['folio'] in folio_to_regime:
            regime = folio_to_regime[r['folio']]
            regime_phases[regime]['E'].append(r['early'])
            regime_phases[regime]['M'].append(r['middle'])
            regime_phases[regime]['L'].append(r['late'])

    print("\n  Phase distribution by REGIME:")
    for regime in sorted(regime_phases.keys()):
        e_mean = np.mean(regime_phases[regime]['E']) * 100
        m_mean = np.mean(regime_phases[regime]['M']) * 100
        l_mean = np.mean(regime_phases[regime]['L']) * 100
        n = len(regime_phases[regime]['E'])
        print(f"    {regime} (n={n}): E={e_mean:.1f}% M={m_mean:.1f}% L={l_mean:.1f}%")

    # Test if REGIME correlates with phase distribution
    # REGIME_4 should be extraction/refinement heavy (LATE) per C494 precision axis

except Exception as e:
    print(f"  Could not load REGIME mapping: {e}")

# =============================================================================
# STEP 8: Summary
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
TEST RESULTS:

1. PREFIX POSITIONAL GRAMMAR: PREFIX families show clear positional bias
   - Some prefixes cluster EARLY in lines
   - Some prefixes cluster LATE in lines
   - This is consistent with phase-based structure

2. PHASE TRANSITIONS:
   - Forward/Backward ratio indicates directional flow
   - If ratio > 2: Strong procedural flow (like Brunschwig)
   - If ratio ~ 1: No directional preference

3. FOLIO PHASE PROFILES:
   - Different folios have different phase distributions
   - This could correspond to different recipe types:
     * EARLY-heavy = acquisition/preparation focus
     * LATE-heavy = extraction/refinement focus

4. REGIME CORRELATION:
   - If REGIME correlates with phase distribution, it validates
     both the REGIME interpretation and the phase model

INTERPRETATION:
If these tests show consistent forward flow and REGIME correlation,
it supports the hypothesis that B grammar encodes procedural sequences
similar to Brunschwig's recipe structure.
""")
