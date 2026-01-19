#!/usr/bin/env python3
"""
SEL-F: MONOSTATE vs 2-CYCLE CONTRADICTION RESOLUTION

The Contradiction (from SEL-B):
- MONOSTATE (Tier 0): "System is fundamentally MONOSTATE" - 100% convergence to STATE-C
- 2-cycle (OPS-R): "dominant_cycle_order = 2" - execution oscillates between 2 states

Resolution Strategy:
1. Clarify what "2-cycle" actually measures (periodicity vs state oscillation)
2. Verify terminal state distribution across all 83 folios
3. Track kernel state trajectories for true oscillation detection
4. Determine: contradiction, definitional ambiguity, or reconcilable

Key Questions:
- Does "2-cycle" mean periodic token patterns OR state oscillation?
- What % of folios terminate in STATE-C vs "other"?
- Are there stable oscillations that NEVER converge?
- If oscillations exist, are they transient (converge) or persistent?
"""

import os
import json
from collections import Counter, defaultdict
import numpy as np

os.chdir('C:/git/voynich')

print("=" * 70)
print("SEL-F: MONOSTATE vs 2-CYCLE CONTRADICTION RESOLUTION")
print("=" * 70)

# =========================================================================
# PART 1: CLARIFY THE 2-CYCLE DEFINITION
# =========================================================================

print("\n" + "=" * 70)
print("PART 1: WHAT DOES '2-CYCLE' ACTUALLY MEAN?")
print("=" * 70)

# Load control signatures
with open('results/control_signatures.json', 'r') as f:
    signatures = json.load(f)

metadata = signatures.get('metadata', {})
print(f"\nCycle detection algorithm: {metadata.get('cycle_detection_algorithm', 'unknown')}")
print(f"  -> 'Sliding window period detection' detects PERIODICITY in token sequences")
print(f"  -> This is NOT the same as state oscillation between two execution states")

sigs = signatures.get('signatures', {})
print(f"\nTotal folios with signatures: {len(sigs)}")

# Count dominant cycle orders
cycle_orders = Counter(sig.get('dominant_cycle_order', 0) for sig in sigs.values())
print(f"\nDominant cycle order distribution:")
for order, count in sorted(cycle_orders.items()):
    pct = count / len(sigs) * 100
    print(f"  Order {order}: {count} folios ({pct:.1f}%)")

# =========================================================================
# PART 2: TERMINAL STATE DISTRIBUTION
# =========================================================================

print("\n" + "=" * 70)
print("PART 2: TERMINAL STATE DISTRIBUTION")
print("Does MONOSTATE (100% STATE-C convergence) hold?")
print("=" * 70)

terminal_states = Counter(sig.get('terminal_state', 'unknown') for sig in sigs.values())
print(f"\nTerminal state distribution:")
for state, count in terminal_states.most_common():
    pct = count / len(sigs) * 100
    print(f"  {state}: {count} folios ({pct:.1f}%)")

state_c_count = terminal_states.get('STATE-C', 0)
other_count = terminal_states.get('other', 0)
total = len(sigs)

if state_c_count == total:
    monostate_verdict = "CONFIRMED"
    monostate_detail = "100% of folios terminate in STATE-C"
elif state_c_count > 0.9 * total:
    monostate_verdict = "WEAKLY_SUPPORTED"
    monostate_detail = f"{state_c_count/total*100:.1f}% terminate in STATE-C (not 100%)"
else:
    monostate_verdict = "CHALLENGED"
    monostate_detail = f"Only {state_c_count/total*100:.1f}% terminate in STATE-C"

print(f"\nMONOSTATE claim status: {monostate_verdict}")
print(f"  {monostate_detail}")

# List folios NOT in STATE-C
non_statec = [f for f, sig in sigs.items() if sig.get('terminal_state') != 'STATE-C']
if non_statec:
    print(f"\nFolios NOT terminating in STATE-C ({len(non_statec)}):")
    for f in non_statec[:10]:
        print(f"  {f}: terminal_state = {sigs[f].get('terminal_state')}")
    if len(non_statec) > 10:
        print(f"  ... and {len(non_statec) - 10} more")

# =========================================================================
# PART 3: KERNEL STATE TRAJECTORY ANALYSIS
# =========================================================================

print("\n" + "=" * 70)
print("PART 3: KERNEL STATE TRAJECTORY ANALYSIS")
print("Track k->h->e sequences for oscillation vs convergence")
print("=" * 70)

# Load grammar for kernel identification
with open('results/canonical_grammar.json', 'r') as f:
    grammar = json.load(f)

# Load transcription data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        # Filter to H (PRIMARY) transcriber only
        transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
        if transcriber != 'H':
            continue
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Get Currier B folios only
b_folios = set()
for t in all_tokens:
    if t.get('language', '') == 'B':
        b_folios.add(t.get('folio', ''))

print(f"\nCurrier B folios: {len(b_folios)}")

# Define kernel tokens
kernel_tokens = {'ok', 'yk', 'ak', 'ek', 'otk',  # k variants
                 'oh', 'yh', 'ah', 'eh', 'oth',  # h variants
                 'oe', 'ye', 'ae', 'ee', 'ote'}  # e variants (hypothetical)

# Actually, let's be more inclusive - look for tokens containing k, h, e
def get_kernel_class(word):
    """Classify token by kernel contact."""
    # Check for explicit kernel markers
    if any(word == k or word.endswith(k) for k in ['ok', 'yk', 'ak', 'ek']):
        return 'K'
    if any(word == h or word.endswith(h) for h in ['oh', 'yh', 'ah', 'eh']):
        return 'H'
    if word.endswith('e') and len(word) <= 3:
        return 'E'
    # Check for 'ol' as LINK
    if 'ol' in word or word == 'ol':
        return 'LINK'
    return 'OTHER'

# Build per-folio kernel trajectories
folio_trajectories = defaultdict(list)
for t in all_tokens:
    if t.get('language', '') == 'B':
        folio = t.get('folio', '')
        word = t.get('word', '')
        kernel = get_kernel_class(word)
        folio_trajectories[folio].append(kernel)

print(f"\nFolios with trajectories: {len(folio_trajectories)}")

# Analyze trajectories for oscillation patterns
def detect_oscillation(trajectory, window_size=20):
    """
    Detect oscillation in kernel trajectory.
    Returns:
    - oscillation_score: proportion of transitions that are alternating
    - convergence_score: proportion of trajectory at end in single state
    """
    if len(trajectory) < window_size * 2:
        return None, None

    # Count alternating transitions (A→B→A pattern)
    alternations = 0
    total_transitions = 0
    for i in range(len(trajectory) - 2):
        if trajectory[i] != trajectory[i+1] and trajectory[i+1] != trajectory[i+2]:
            if trajectory[i] == trajectory[i+2]:  # A→B→A
                alternations += 1
            total_transitions += 1

    oscillation_score = alternations / max(1, total_transitions)

    # Check final segment for convergence
    final_segment = trajectory[-window_size:]
    state_counts = Counter(final_segment)
    dominant_state, dominant_count = state_counts.most_common(1)[0]
    convergence_score = dominant_count / len(final_segment)

    return oscillation_score, convergence_score

print("\nOscillation vs Convergence Analysis:")
print(f"{'Folio':<12} {'Length':<8} {'Oscillation':<12} {'Convergence':<12} {'Pattern':<15}")
print("-" * 65)

oscillation_scores = []
convergence_scores = []
patterns = []

for folio in sorted(folio_trajectories.keys())[:20]:  # Sample first 20
    traj = folio_trajectories[folio]
    osc, conv = detect_oscillation(traj)

    if osc is not None:
        oscillation_scores.append(osc)
        convergence_scores.append(conv)

        if osc > 0.4 and conv < 0.6:
            pattern = "OSCILLATING"
        elif conv > 0.8:
            pattern = "CONVERGED"
        else:
            pattern = "MIXED"
        patterns.append(pattern)

        print(f"{folio:<12} {len(traj):<8} {osc:<12.3f} {conv:<12.3f} {pattern:<15}")

# =========================================================================
# PART 4: STATE SEQUENCE ANALYSIS
# =========================================================================

print("\n" + "=" * 70)
print("PART 4: STATE SEQUENCE DEEP ANALYSIS")
print("Looking for persistent 2-state oscillation")
print("=" * 70)

def analyze_state_sequence(trajectory):
    """
    Analyze state sequence for:
    - Dominant states
    - Transition patterns
    - Oscillation persistence
    """
    if len(trajectory) < 10:
        return None

    # State frequency
    state_freq = Counter(trajectory)

    # Transition matrix
    transitions = defaultdict(Counter)
    for i in range(len(trajectory) - 1):
        transitions[trajectory[i]][trajectory[i+1]] += 1

    # Check for 2-state dominance
    top_2_states = [s for s, _ in state_freq.most_common(2)]
    top_2_coverage = sum(state_freq[s] for s in top_2_states) / len(trajectory)

    # Check for alternation pattern between top 2
    if len(top_2_states) >= 2:
        s1, s2 = top_2_states
        alt_score = (transitions[s1][s2] + transitions[s2][s1]) / max(1, sum(sum(t.values()) for t in transitions.values()))
    else:
        alt_score = 0

    return {
        'state_freq': state_freq,
        'top_2_states': top_2_states,
        'top_2_coverage': top_2_coverage,
        'alternation_score': alt_score,
        'total_transitions': sum(sum(t.values()) for t in transitions.values())
    }

# Analyze all B folios
two_state_folios = []
converged_folios = []

for folio, traj in folio_trajectories.items():
    analysis = analyze_state_sequence(traj)
    if analysis is None:
        continue

    # Check if this looks like 2-state oscillation
    if analysis['top_2_coverage'] > 0.8 and analysis['alternation_score'] > 0.3:
        two_state_folios.append((folio, analysis))

    # Check if this looks like convergence
    if max(analysis['state_freq'].values()) / len(traj) > 0.6:
        converged_folios.append((folio, analysis))

print(f"\nFolios with strong 2-state pattern: {len(two_state_folios)}")
print(f"Folios with strong convergence: {len(converged_folios)}")
print(f"Overlap: {len(set(f for f, _ in two_state_folios) & set(f for f, _ in converged_folios))}")

# =========================================================================
# PART 5: RECONCILIATION ANALYSIS
# =========================================================================

print("\n" + "=" * 70)
print("PART 5: CONTRADICTION RESOLUTION")
print("=" * 70)

print("""
DEFINITIONAL CLARIFICATION:

1. "2-cycle" in OPS-R refers to:
   - PERIODICITY in token sequences (sliding window detection)
   - Pattern: tokens tend to repeat every ~2 positions
   - This is about LOCAL structure, not global state

2. "MONOSTATE" refers to:
   - TERMINAL convergence to STATE-C
   - All execution paths eventually reach same state
   - This is about GLOBAL behavior

3. These are NOT contradictory IF:
   - Local periodicity (2-cycle) can coexist with global convergence
   - The system oscillates WHILE running but CONVERGES when complete
   - "2-cycle" is transient pattern, "STATE-C" is attractor

HOWEVER, the terminal_state data shows:
""")

print(f"  STATE-C: {state_c_count}/{total} ({state_c_count/total*100:.1f}%)")
print(f"  Other: {other_count}/{total} ({other_count/total*100:.1f}%)")

if other_count > 0:
    print(f"""
FINDING: {other_count} folios do NOT terminate in STATE-C!

This challenges the "100% convergence" aspect of MONOSTATE.

Options:
1. MONOSTATE is too strong - should say "dominant convergence" not "100%"
2. "terminal_state" field is measuring something different
3. Some folios are incomplete/anomalous
""")

# =========================================================================
# PART 6: VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("SEL-F VERDICT: MONOSTATE vs 2-CYCLE")
print("=" * 70)

# Calculate final metrics
pct_statec = state_c_count / total * 100
pct_cycle2 = cycle_orders.get(2, 0) / total * 100

print(f"""
METRICS:
  - % folios with dominant_cycle_order = 2: {pct_cycle2:.1f}%
  - % folios with terminal_state = STATE-C: {pct_statec:.1f}%
  - % folios with terminal_state = other: {other_count/total*100:.1f}%

ANALYSIS:
""")

if pct_statec >= 99.0:
    convergence_status = "CONFIRMED (>99% STATE-C)"
    monostate_revision = "NONE NEEDED"
elif pct_statec >= 90.0:
    convergence_status = "MOSTLY CONFIRMED (90-99% STATE-C)"
    monostate_revision = "Weaken to 'dominant convergence'"
else:
    convergence_status = "CHALLENGED (<90% STATE-C)"
    monostate_revision = "Revise MONOSTATE claim"

print(f"  Convergence status: {convergence_status}")
print(f"  MONOSTATE revision: {monostate_revision}")

# Final verdict
print(f"""
RESOLUTION:

The "contradiction" is primarily DEFINITIONAL:

1. "2-cycle" = LOCAL periodicity in token sequences
   - Detected by sliding window algorithm
   - Measures pattern repetition period
   - Does NOT mean two distinct execution states

2. "MONOSTATE" = GLOBAL terminal convergence
   - Measures where execution ends up
   - STATE-C is the attractor
   - Does NOT mean no oscillation during operation

THESE ARE COMPATIBLE because:
- A system can oscillate locally while converging globally
- Think of a damped oscillator: swings back and forth but settles
- The 2-cycle is the oscillation; STATE-C is the equilibrium

REMAINING ISSUE:
- {other_count}/{total} folios have terminal_state != STATE-C
- This requires investigation: are these incomplete, anomalous, or genuine exceptions?
""")

# Check which folios have "other" terminal state
print("\nFolios with terminal_state = 'other':")
for f in non_statec:
    sig = sigs[f]
    print(f"  {f}: kernel_dominance={sig.get('kernel_dominance')}, "
          f"kernel_contact_ratio={sig.get('kernel_contact_ratio', 0):.3f}, "
          f"reset_present={sig.get('reset_present')}")

print("\n" + "=" * 70)
print("SEL-F COMPLETE")
print("=" * 70)
