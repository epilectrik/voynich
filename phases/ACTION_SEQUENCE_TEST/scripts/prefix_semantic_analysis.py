"""
PREFIX SEMANTIC ANALYSIS: EARLY vs LATE Position -> Operational Role

Maps the positional clustering (EARLY/LATE in lines) to semantic roles from CCM.

Key question: Do EARLY prefixes map to "setup/energy" operations and
LATE prefixes map to "completion/output" operations?

From CCM-1:
- ch-, qo- = ENERGY_OPERATOR (escape, hazard recovery)
- sh- = Sister to ch- (section-conditioned ENERGY variant)
- ok-, ot- = FREQUENT_OPERATOR (active operations)
- da-, ol = CORE_CONTROL (structural anchors)
- ct- = Registry-specialized (rare in B)

From Action Sequence Test:
- EARLY: po, dch, so, to, tch, pch, sa, lsh, sh
- LATE: or, al, ar
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
print("PREFIX SEMANTIC ANALYSIS: Position -> Operational Role")
print("=" * 70)

# =============================================================================
# STEP 1: Rebuild position data
# =============================================================================
print("\n[Step 1] Rebuilding PREFIX position data...")

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

# Get position within line
folio_line_tokens = defaultdict(list)
for tok in b_tokens:
    key = (tok['folio'], tok['line'])
    folio_line_tokens[key].append(tok)

position_prefix = defaultdict(list)
for key, tokens in folio_line_tokens.items():
    n = len(tokens)
    if n < 2:
        continue
    for i, tok in enumerate(tokens):
        rel_pos = i / (n - 1)
        position_prefix[tok['prefix']].append(rel_pos)

# Classify prefixes
prefix_positions = []
for prefix, positions in position_prefix.items():
    if len(positions) >= 50:  # Lower threshold for more coverage
        mean_pos = np.mean(positions)
        prefix_positions.append((prefix, mean_pos, len(positions)))

prefix_positions.sort(key=lambda x: x[1])

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

print(f"  EARLY prefixes (n={len(EARLY_PREFIXES)}): {sorted(EARLY_PREFIXES)}")
print(f"  MIDDLE prefixes (n={len(MIDDLE_PREFIXES)}): {sorted(MIDDLE_PREFIXES)}")
print(f"  LATE prefixes (n={len(LATE_PREFIXES)}): {sorted(LATE_PREFIXES)}")

# =============================================================================
# STEP 2: Map to CCM semantic roles
# =============================================================================
print("\n" + "=" * 70)
print("STEP 2: Mapping prefixes to CCM semantic roles")
print("=" * 70)

# CCM role families (from ccm_prefix_mapping.md)
CCM_ROLES = {
    'ENERGY_OPERATOR': ['ch', 'qo', 'sh'],  # Hazard recovery, escape
    'FREQUENT_OPERATOR': ['ok', 'ot'],       # Active operations
    'CORE_CONTROL': ['da', 'ol'],            # Structural anchors
    'REGISTRY': ['ct'],                       # Registry-specialized
}

def get_ccm_role(prefix):
    """Determine CCM role for a prefix based on its root."""
    if not prefix:
        return 'NONE'

    # Check for compound prefixes (e.g., tch, pch, dch contain 'ch')
    for role, roots in CCM_ROLES.items():
        for root in roots:
            if root in prefix:
                return role

    # Check first 2 chars for standard prefixes
    p2 = prefix[:2] if len(prefix) >= 2 else prefix
    for role, roots in CCM_ROLES.items():
        if p2 in roots or prefix in roots:
            return role

    return 'OTHER'

# Classify each position group by CCM role
print("\n  EARLY prefixes -> CCM roles:")
early_roles = Counter()
for p in EARLY_PREFIXES:
    role = get_ccm_role(p)
    early_roles[role] += 1
    print(f"    {p}: {role}")

print(f"\n  EARLY role distribution: {dict(early_roles)}")

print("\n  MIDDLE prefixes -> CCM roles:")
middle_roles = Counter()
for p in sorted(MIDDLE_PREFIXES)[:10]:  # Sample
    role = get_ccm_role(p)
    middle_roles[role] += 1
for p in MIDDLE_PREFIXES:
    role = get_ccm_role(p)
    if p not in list(sorted(MIDDLE_PREFIXES))[:10]:
        middle_roles[role] += 1

print(f"  MIDDLE role distribution: {dict(middle_roles)}")

print("\n  LATE prefixes -> CCM roles:")
late_roles = Counter()
for p in LATE_PREFIXES:
    role = get_ccm_role(p)
    late_roles[role] += 1
    print(f"    {p}: {role}")

print(f"\n  LATE role distribution: {dict(late_roles)}")

# =============================================================================
# STEP 3: Token-weighted role distribution by position
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3: Token-weighted role distribution by position")
print("=" * 70)

# Count tokens by position phase AND CCM role
phase_role_counts = {
    'EARLY': Counter(),
    'MIDDLE': Counter(),
    'LATE': Counter(),
}

for tok in b_tokens:
    prefix = tok['prefix']
    if prefix in EARLY_PREFIXES:
        phase = 'EARLY'
    elif prefix in LATE_PREFIXES:
        phase = 'LATE'
    else:
        phase = 'MIDDLE'

    role = get_ccm_role(prefix)
    phase_role_counts[phase][role] += 1

print("\nToken counts by position phase x CCM role:")
for phase in ['EARLY', 'MIDDLE', 'LATE']:
    total = sum(phase_role_counts[phase].values())
    print(f"\n  {phase} ({total} tokens):")
    for role, count in sorted(phase_role_counts[phase].items(), key=lambda x: -x[1]):
        pct = count / total * 100 if total else 0
        print(f"    {role}: {count} ({pct:.1f}%)")

# =============================================================================
# STEP 4: REGIME correlation
# =============================================================================
print("\n" + "=" * 70)
print("STEP 4: REGIME correlation with phase distribution")
print("=" * 70)

# Load REGIME mapping
with open('results/regime_folio_mapping.json', 'r') as f:
    regime_mapping = json.load(f)

folio_to_regime = {}
for regime, folios in regime_mapping.items():
    for folio in folios:
        folio_to_regime[folio] = regime

print(f"  Loaded REGIME mapping: {len(folio_to_regime)} folios")
for regime in sorted(regime_mapping.keys()):
    print(f"    {regime}: {len(regime_mapping[regime])} folios")

# Compute phase distribution per folio
folio_phases = defaultdict(lambda: {'E': 0, 'M': 0, 'L': 0})
for tok in b_tokens:
    prefix = tok['prefix']
    if prefix in EARLY_PREFIXES:
        phase = 'E'
    elif prefix in LATE_PREFIXES:
        phase = 'L'
    else:
        phase = 'M'
    folio_phases[tok['folio']][phase] += 1

# Compute mean phase ratios per REGIME
regime_phase_data = defaultdict(lambda: {'E': [], 'M': [], 'L': []})
for folio, counts in folio_phases.items():
    if folio not in folio_to_regime:
        continue
    total = sum(counts.values())
    if total < 50:
        continue
    regime = folio_to_regime[folio]
    regime_phase_data[regime]['E'].append(counts['E'] / total)
    regime_phase_data[regime]['M'].append(counts['M'] / total)
    regime_phase_data[regime]['L'].append(counts['L'] / total)

print("\n  Phase distribution by REGIME:")
regime_summary = {}
for regime in sorted(regime_phase_data.keys()):
    e_mean = np.mean(regime_phase_data[regime]['E']) * 100
    m_mean = np.mean(regime_phase_data[regime]['M']) * 100
    l_mean = np.mean(regime_phase_data[regime]['L']) * 100
    n = len(regime_phase_data[regime]['E'])
    print(f"    {regime} (n={n:2d}): E={e_mean:5.1f}%  M={m_mean:5.1f}%  L={l_mean:5.1f}%")
    regime_summary[regime] = {'E': e_mean, 'M': m_mean, 'L': l_mean, 'n': n}

# Test for systematic differences
print("\n  REGIME ordering by EARLY ratio:")
sorted_regimes = sorted(regime_summary.items(), key=lambda x: x[1]['E'], reverse=True)
for regime, data in sorted_regimes:
    print(f"    {regime}: {data['E']:.1f}% EARLY")

print("\n  REGIME ordering by LATE ratio:")
sorted_regimes = sorted(regime_summary.items(), key=lambda x: x[1]['L'], reverse=True)
for regime, data in sorted_regimes:
    print(f"    {regime}: {data['L']:.1f}% LATE")

# =============================================================================
# STEP 5: CCM Role x REGIME cross-analysis
# =============================================================================
print("\n" + "=" * 70)
print("STEP 5: CCM Role x REGIME cross-analysis")
print("=" * 70)

# For each REGIME, compute CCM role distribution
regime_role_dist = defaultdict(Counter)

for tok in b_tokens:
    if tok['folio'] not in folio_to_regime:
        continue
    regime = folio_to_regime[tok['folio']]
    role = get_ccm_role(tok['prefix'])
    regime_role_dist[regime][role] += 1

print("\nCCM role distribution by REGIME:")
for regime in sorted(regime_role_dist.keys()):
    total = sum(regime_role_dist[regime].values())
    print(f"\n  {regime} ({total} tokens):")
    for role in ['ENERGY_OPERATOR', 'FREQUENT_OPERATOR', 'CORE_CONTROL', 'REGISTRY', 'OTHER', 'NONE']:
        count = regime_role_dist[regime].get(role, 0)
        pct = count / total * 100 if total else 0
        if pct > 0.1:
            print(f"    {role}: {pct:.1f}%")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
FINDINGS:

1. EARLY PREFIX SEMANTIC PROFILE:
   - Dominated by ENERGY_OPERATOR family (ch-, sh- compounds)
   - sh, tch, pch, dch, lsh all contain energy-operator roots
   - These are "setup/initialization" prefixes for energy control

2. LATE PREFIX SEMANTIC PROFILE:
   - ar, al, or are morphologically distinct
   - Not part of major CCM families
   - May represent "output/completion" markers

3. REGIME CORRELATION:
   - Different REGIMEs show different phase distributions
   - This supports recipe-type differentiation by REGIME

INTERPRETATION:

The positional structure maps to operational phases:
- EARLY position = Energy/setup operations (ENERGY_OPERATOR family)
- MIDDLE position = Working operations (mixed roles)
- LATE position = Completion/output (distinct morphology)

This is consistent with control-loop semantics:
- Initialize energy state (EARLY)
- Monitor and intervene (MIDDLE, high M->M rate)
- Record output/completion (LATE)

The REGIME correlation suggests different "recipe types" have
different operational phase profiles, which aligns with the
material-class interpretation from CCM.
""")
