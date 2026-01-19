#!/usr/bin/env python3
"""
FOLIO CHAINING HYPOTHESIS TEST

Expert hypothesis: The 42.2% of folios that don't end in STATE-C are
MODULAR PROCEDURES that chain together.

Folios are not 83 independent programs, but a LIBRARY OF COMPOSABLE OPERATIONS.

Tests:
1. Sequential State Matching - Do consecutive folios have matching end/start states?
2. Token Overlap at Boundaries - Do chained folios share vocabulary at boundaries?
3. State Trajectory Continuity - Do folio sequences form continuous trajectories?
4. Quire Structure Correlation - Are physically adjacent folios operationally adjacent?
5. Completion Analysis - Are STATE-C folios workflow terminals?
6. Initial-State Entry Points - Are "initial" folios reset/entry points?
"""

import os
import json
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
import re

os.chdir('C:/git/voynich')

print("=" * 70)
print("FOLIO CHAINING HYPOTHESIS TEST")
print("Are folios modular procedures that chain together?")
print("=" * 70)

# Load control signatures
with open('results/control_signatures.json', 'r') as f:
    signatures = json.load(f)

sigs = signatures.get('signatures', {})

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

# Build per-folio token sequences
folio_tokens = defaultdict(list)
for t in all_tokens:
    if t.get('language', '') == 'B':
        folio = t.get('folio', '')
        folio_tokens[folio].append(t.get('word', ''))

# Get ordered list of Currier B folios
def folio_sort_key(f):
    """Sort folios by their numeric value."""
    match = re.match(r'f(\d+)([rv]?)(\d*)', f)
    if match:
        num = int(match.group(1))
        side = 0 if match.group(2) == 'r' else 1
        sub = int(match.group(3)) if match.group(3) else 0
        return (num, side, sub)
    return (999, 0, 0)

b_folios = sorted([f for f in sigs.keys()], key=folio_sort_key)
print(f"\nCurrier B folios: {len(b_folios)}")

# =========================================================================
# TEST 1: SEQUENTIAL STATE MATCHING
# =========================================================================

print("\n" + "=" * 70)
print("TEST 1: SEQUENTIAL STATE MATCHING")
print("Do consecutive folios have matching end/start states?")
print("=" * 70)

def get_terminal_state(folio):
    """Get terminal state from signatures."""
    return sigs.get(folio, {}).get('terminal_state', 'unknown')

def get_initial_state(folio):
    """Infer initial state from first few tokens."""
    tokens = folio_tokens.get(folio, [])
    if not tokens:
        return 'unknown'

    # Check first few tokens for kernel contact
    first_5 = tokens[:5]

    # Simple heuristic: check for LINK vs kernel tokens
    link_count = sum(1 for t in first_5 if 'ol' in t)
    kernel_count = sum(1 for t in first_5 if any(k in t for k in ['ok', 'yk', 'ak', 'oh', 'yh', 'ah']))

    if link_count > kernel_count:
        return 'STATE-C'  # Starting from stable/waiting state
    elif kernel_count > 0:
        return 'transitional'  # Starting with kernel activity
    else:
        return 'other'

def get_kernel_dominance(folio):
    """Get kernel dominance from signatures."""
    return sigs.get(folio, {}).get('kernel_dominance', 'unknown')

# Test consecutive folio pairs
chain_matches = []
for i in range(len(b_folios) - 1):
    f1, f2 = b_folios[i], b_folios[i+1]

    end_state = get_terminal_state(f1)
    start_state = get_initial_state(f2)
    kernel_dom_1 = get_kernel_dominance(f1)
    kernel_dom_2 = get_kernel_dominance(f2)

    # Check for state matching
    match = False
    if end_state == 'other' and start_state in ['transitional', 'other']:
        match = True
    elif end_state == 'initial' and start_state in ['STATE-C', 'other']:
        match = True
    elif end_state == 'STATE-C' and start_state == 'STATE-C':
        match = True

    # Also check kernel continuity
    kernel_match = kernel_dom_1 == kernel_dom_2

    chain_matches.append({
        'folio_1': f1,
        'folio_2': f2,
        'end_state': end_state,
        'start_state': start_state,
        'state_match': match,
        'kernel_match': kernel_match,
        'kernel_1': kernel_dom_1,
        'kernel_2': kernel_dom_2
    })

# Count matches
state_match_count = sum(1 for m in chain_matches if m['state_match'])
kernel_match_count = sum(1 for m in chain_matches if m['kernel_match'])
total_pairs = len(chain_matches)

print(f"\nConsecutive folio pairs: {total_pairs}")
print(f"State matches: {state_match_count} ({state_match_count/total_pairs*100:.1f}%)")
print(f"Kernel continuity: {kernel_match_count} ({kernel_match_count/total_pairs*100:.1f}%)")

# Expected by chance
# Terminal states: 57.8% STATE-C, 38.6% other, 3.6% initial
# If random: P(match) ~ 0.578^2 + 0.386^2 + 0.036^2 ~ 0.48
expected_random = 0.578**2 + 0.386**2 + 0.036**2
print(f"\nExpected by chance (state): {expected_random*100:.1f}%")
print(f"Actual rate: {state_match_count/total_pairs*100:.1f}%")

if state_match_count/total_pairs > expected_random * 1.2:
    test1_verdict = "SUPPORTS CHAINING"
else:
    test1_verdict = "NO EVIDENCE"

print(f"\nTEST 1 VERDICT: {test1_verdict}")

# Show potential chains
print(f"\nPotential chain connections (non-STATE-C endings):")
print(f"{'Folio 1':<10} {'End':<12} {'Folio 2':<10} {'Start':<12} {'Match':<8}")
print("-" * 55)

for m in chain_matches:
    if m['end_state'] != 'STATE-C':
        match_str = "YES" if m['state_match'] else "no"
        print(f"{m['folio_1']:<10} {m['end_state']:<12} {m['folio_2']:<10} {m['start_state']:<12} {match_str:<8}")

# =========================================================================
# TEST 2: TOKEN OVERLAP AT BOUNDARIES
# =========================================================================

print("\n" + "=" * 70)
print("TEST 2: TOKEN OVERLAP AT BOUNDARIES")
print("Do potentially chained folios share vocabulary at boundaries?")
print("=" * 70)

def get_boundary_tokens(folio, n=10, start=True):
    """Get first or last n tokens of a folio."""
    tokens = folio_tokens.get(folio, [])
    if start:
        return set(tokens[:n])
    else:
        return set(tokens[-n:])

# Calculate boundary overlap for all consecutive pairs
boundary_overlaps = []
for i in range(len(b_folios) - 1):
    f1, f2 = b_folios[i], b_folios[i+1]

    end_tokens = get_boundary_tokens(f1, n=10, start=False)
    start_tokens = get_boundary_tokens(f2, n=10, start=True)

    if end_tokens and start_tokens:
        overlap = len(end_tokens & start_tokens)
        jaccard = len(end_tokens & start_tokens) / len(end_tokens | start_tokens)
        boundary_overlaps.append({
            'folio_1': f1,
            'folio_2': f2,
            'overlap_count': overlap,
            'jaccard': jaccard,
            'end_state': get_terminal_state(f1)
        })

# Compare chain candidates vs non-chains
chain_candidates = [b for b in boundary_overlaps if b['end_state'] != 'STATE-C']
non_chains = [b for b in boundary_overlaps if b['end_state'] == 'STATE-C']

if chain_candidates and non_chains:
    chain_mean = np.mean([b['jaccard'] for b in chain_candidates])
    nonchain_mean = np.mean([b['jaccard'] for b in non_chains])

    print(f"\nBoundary Jaccard similarity:")
    print(f"  Potential chains (non-STATE-C end): {chain_mean:.4f} (n={len(chain_candidates)})")
    print(f"  Non-chains (STATE-C end): {nonchain_mean:.4f} (n={len(non_chains)})")

    # Statistical test
    chain_jaccards = [b['jaccard'] for b in chain_candidates]
    nonchain_jaccards = [b['jaccard'] for b in non_chains]

    stat, p_value = stats.mannwhitneyu(chain_jaccards, nonchain_jaccards, alternative='greater')
    print(f"  Mann-Whitney U p-value (chain > nonchain): {p_value:.4f}")

    if p_value < 0.05 and chain_mean > nonchain_mean:
        test2_verdict = "SUPPORTS CHAINING"
    else:
        test2_verdict = "NO EVIDENCE"

    print(f"\nTEST 2 VERDICT: {test2_verdict}")

# =========================================================================
# TEST 3: STATE TRAJECTORY CONTINUITY
# =========================================================================

print("\n" + "=" * 70)
print("TEST 3: STATE TRAJECTORY CONTINUITY")
print("Do folio sequences form continuous state trajectories?")
print("=" * 70)

def get_kernel_trajectory(folio):
    """Get sequence of kernel states in a folio."""
    tokens = folio_tokens.get(folio, [])
    trajectory = []

    for t in tokens:
        if 'ok' in t or 'yk' in t or 'ak' in t:
            trajectory.append('K')
        elif 'oh' in t or 'yh' in t or 'ah' in t:
            trajectory.append('H')
        elif 'ol' in t:
            trajectory.append('L')  # LINK

    return trajectory

# Check if trajectories are continuous across folios
continuity_scores = []
for i in range(len(b_folios) - 1):
    f1, f2 = b_folios[i], b_folios[i+1]

    traj1 = get_kernel_trajectory(f1)
    traj2 = get_kernel_trajectory(f2)

    if traj1 and traj2:
        # Check if last state of f1 matches first state of f2
        last_state = traj1[-1] if traj1 else None
        first_state = traj2[0] if traj2 else None

        # Also check last 3 states vs first 3 states
        last_3 = traj1[-3:] if len(traj1) >= 3 else traj1
        first_3 = traj2[:3] if len(traj2) >= 3 else traj2

        point_match = last_state == first_state
        pattern_similarity = len(set(last_3) & set(first_3)) / max(len(set(last_3) | set(first_3)), 1)

        continuity_scores.append({
            'folio_1': f1,
            'folio_2': f2,
            'point_match': point_match,
            'pattern_similarity': pattern_similarity,
            'end_state': get_terminal_state(f1)
        })

# Compare chain candidates vs non-chains
chain_cont = [c for c in continuity_scores if c['end_state'] != 'STATE-C']
nonchain_cont = [c for c in continuity_scores if c['end_state'] == 'STATE-C']

if chain_cont and nonchain_cont:
    chain_point = sum(1 for c in chain_cont if c['point_match']) / len(chain_cont)
    nonchain_point = sum(1 for c in nonchain_cont if c['point_match']) / len(nonchain_cont)

    print(f"\nPoint continuity (last state = first state):")
    print(f"  Potential chains: {chain_point*100:.1f}%")
    print(f"  Non-chains: {nonchain_point*100:.1f}%")

    chain_pattern = np.mean([c['pattern_similarity'] for c in chain_cont])
    nonchain_pattern = np.mean([c['pattern_similarity'] for c in nonchain_cont])

    print(f"\nPattern similarity (last 3 vs first 3):")
    print(f"  Potential chains: {chain_pattern:.3f}")
    print(f"  Non-chains: {nonchain_pattern:.3f}")

    if chain_point > nonchain_point + 0.1:
        test3_verdict = "SUPPORTS CHAINING"
    else:
        test3_verdict = "NO EVIDENCE"

    print(f"\nTEST 3 VERDICT: {test3_verdict}")

# =========================================================================
# TEST 4: QUIRE STRUCTURE CORRELATION
# =========================================================================

print("\n" + "=" * 70)
print("TEST 4: QUIRE STRUCTURE CORRELATION")
print("Are physically adjacent folios operationally adjacent?")
print("=" * 70)

# Estimate quire membership from folio numbers
# Typical quire = 4 bifolios = 8 leaves = 16 pages
# Folios are numbered by leaf, so ~8 folios per quire

def estimate_quire(folio):
    """Estimate quire number from folio number."""
    match = re.match(r'f(\d+)', folio)
    if match:
        num = int(match.group(1))
        return num // 8  # Approximate quire
    return -1

# Group folios by estimated quire
quire_folios = defaultdict(list)
for f in b_folios:
    q = estimate_quire(f)
    quire_folios[q].append(f)

print(f"\nEstimated quires: {len(quire_folios)}")
for q in sorted(quire_folios.keys())[:5]:
    print(f"  Quire {q}: {quire_folios[q][:5]}...")

# Count chains within vs across quires
within_quire_chains = 0
across_quire_chains = 0
within_quire_total = 0
across_quire_total = 0

for i in range(len(b_folios) - 1):
    f1, f2 = b_folios[i], b_folios[i+1]
    q1, q2 = estimate_quire(f1), estimate_quire(f2)

    is_chain = get_terminal_state(f1) != 'STATE-C'

    if q1 == q2:
        within_quire_total += 1
        if is_chain:
            within_quire_chains += 1
    else:
        across_quire_total += 1
        if is_chain:
            across_quire_chains += 1

print(f"\nChain candidates (non-STATE-C endings):")
print(f"  Within quire: {within_quire_chains}/{within_quire_total} ({within_quire_chains/max(1,within_quire_total)*100:.1f}%)")
print(f"  Across quires: {across_quire_chains}/{max(1,across_quire_total)} ({across_quire_chains/max(1,across_quire_total)*100:.1f}%)")

if within_quire_total > 0 and across_quire_total > 0:
    within_rate = within_quire_chains / within_quire_total
    across_rate = across_quire_chains / across_quire_total

    if within_rate > across_rate + 0.1:
        test4_verdict = "SUPPORTS CHAINING (quire-local)"
    elif across_rate > within_rate + 0.1:
        test4_verdict = "CHAINS CROSS QUIRES"
    else:
        test4_verdict = "NO QUIRE PATTERN"

    print(f"\nTEST 4 VERDICT: {test4_verdict}")

# =========================================================================
# TEST 5: COMPLETION ANALYSIS
# =========================================================================

print("\n" + "=" * 70)
print("TEST 5: COMPLETION ANALYSIS")
print("Are STATE-C folios workflow terminals (never followed by continuations)?")
print("=" * 70)

state_c_followed_by_chain = 0
state_c_followed_by_terminal = 0
state_c_total = 0

for i in range(len(b_folios) - 1):
    f1, f2 = b_folios[i], b_folios[i+1]

    if get_terminal_state(f1) == 'STATE-C':
        state_c_total += 1

        # Check if f2 looks like a continuation
        f2_start = get_initial_state(f2)

        if f2_start in ['transitional', 'other']:
            state_c_followed_by_chain += 1
        else:
            state_c_followed_by_terminal += 1

print(f"\nSTATE-C folios followed by:")
print(f"  New workflow (STATE-C start): {state_c_followed_by_terminal} ({state_c_followed_by_terminal/max(1,state_c_total)*100:.1f}%)")
print(f"  Continuation (transitional start): {state_c_followed_by_chain} ({state_c_followed_by_chain/max(1,state_c_total)*100:.1f}%)")

if state_c_followed_by_terminal > state_c_followed_by_chain:
    test5_verdict = "STATE-C = TERMINAL (supports modular structure)"
else:
    test5_verdict = "STATE-C NOT TERMINAL"

print(f"\nTEST 5 VERDICT: {test5_verdict}")

# =========================================================================
# TEST 6: INITIAL-STATE ENTRY POINTS
# =========================================================================

print("\n" + "=" * 70)
print("TEST 6: INITIAL-STATE ENTRY POINTS")
print("Are 'initial' folios reset/entry points?")
print("=" * 70)

initial_folios = [f for f in b_folios if get_terminal_state(f) == 'initial']
print(f"\nFolios with terminal_state = 'initial': {initial_folios}")

for f in initial_folios:
    sig = sigs.get(f, {})
    print(f"\n  {f}:")
    print(f"    reset_present: {sig.get('reset_present')}")
    print(f"    kernel_dominance: {sig.get('kernel_dominance')}")
    print(f"    total_length: {sig.get('total_length')}")
    print(f"    hazard_density: {sig.get('hazard_density', 0):.3f}")

    # Check position in manuscript
    idx = b_folios.index(f)
    if idx > 0:
        prev_f = b_folios[idx-1]
        prev_state = get_terminal_state(prev_f)
        print(f"    preceded_by: {prev_f} (terminal: {prev_state})")
    if idx < len(b_folios) - 1:
        next_f = b_folios[idx+1]
        next_state = get_terminal_state(next_f)
        print(f"    followed_by: {next_f} (terminal: {next_state})")

# Check if initial folios are at quire boundaries
initial_at_boundary = 0
for f in initial_folios:
    q = estimate_quire(f)
    idx = b_folios.index(f)

    if idx > 0:
        prev_q = estimate_quire(b_folios[idx-1])
        if prev_q != q:
            initial_at_boundary += 1

if initial_folios:
    print(f"\nInitial folios at quire boundaries: {initial_at_boundary}/{len(initial_folios)}")

    if initial_at_boundary > len(initial_folios) * 0.5:
        test6_verdict = "INITIAL = SECTION ENTRY POINTS"
    else:
        test6_verdict = "INITIAL = RESTART INSTRUCTIONS"

    print(f"\nTEST 6 VERDICT: {test6_verdict}")

# =========================================================================
# OVERALL VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("FOLIO CHAINING HYPOTHESIS - OVERALL VERDICT")
print("=" * 70)

verdicts = []
if 'test1_verdict' in dir():
    verdicts.append(('TEST 1 (State Matching)', test1_verdict))
if 'test2_verdict' in dir():
    verdicts.append(('TEST 2 (Boundary Overlap)', test2_verdict))
if 'test3_verdict' in dir():
    verdicts.append(('TEST 3 (Trajectory Continuity)', test3_verdict))
if 'test4_verdict' in dir():
    verdicts.append(('TEST 4 (Quire Structure)', test4_verdict))
if 'test5_verdict' in dir():
    verdicts.append(('TEST 5 (Completion)', test5_verdict))
if 'test6_verdict' in dir():
    verdicts.append(('TEST 6 (Entry Points)', test6_verdict))

print("\nTest Results:")
supports = 0
for test, verdict in verdicts:
    print(f"  {test}: {verdict}")
    if "SUPPORTS" in verdict:
        supports += 1

print(f"\nTests supporting chaining: {supports}/{len(verdicts)}")

if supports >= 4:
    overall = "STRONG SUPPORT for modular chaining"
elif supports >= 2:
    overall = "PARTIAL SUPPORT for modular chaining"
else:
    overall = "WEAK/NO SUPPORT for modular chaining"

print(f"\nOVERALL: {overall}")

# =========================================================================
# CHAIN RECONSTRUCTION
# =========================================================================

if supports >= 2:
    print("\n" + "=" * 70)
    print("POTENTIAL CHAIN RECONSTRUCTION")
    print("=" * 70)

    # Identify chain starts (STATE-C endings or after STATE-C)
    # and chain ends (STATE-C or end of sequence)

    chains = []
    current_chain = []

    for f in b_folios:
        terminal = get_terminal_state(f)

        if terminal == 'STATE-C':
            # This folio ends a chain
            current_chain.append(f)
            if len(current_chain) > 1:
                chains.append(current_chain)
            current_chain = []
        else:
            # This folio continues a chain
            current_chain.append(f)

    # Don't forget the last chain if it doesn't end in STATE-C
    if current_chain:
        chains.append(current_chain)

    print(f"\nIdentified {len(chains)} potential chains/workflows:")

    for i, chain in enumerate(chains[:10]):  # Show first 10
        if len(chain) > 1:
            states = [get_terminal_state(f) for f in chain]
            print(f"\n  Chain {i+1} ({len(chain)} folios): {' -> '.join(chain)}")
            print(f"    Terminal states: {states}")

print("\n" + "=" * 70)
print("FOLIO CHAINING HYPOTHESIS TEST COMPLETE")
print("=" * 70)
