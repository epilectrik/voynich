#!/usr/bin/env python3
"""
Test 10: FL Sensory Modality Mapping

Hypothesis: FL states correspond to different sensory modalities used to
determine the material state.

From SENSORY_VALIDATION_2026-01-12:
- PHASE_ORDERING → VISION
- COMPOSITION_JUMP → SMELL
- ENERGY_OVERSHOOT → SMELL + VISION
- RATE_MISMATCH → SIGHT + SOUND
- CONTAINMENT_TIMING → SOUND + TOUCH

From C777: FL stages are INITIAL → MEDIAL → LATE → TERMINAL

Test approach:
1. Map FL MIDDLEs to stages
2. Find what contexts (predecessors/hazards) correlate with each FL stage
3. Check if hazard classes cluster differently by FL stage
4. Test if sensory-associated patterns differ by FL stage
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("TEST 10: FL SENSORY MODALITY MAPPING")
print("="*70)

# =========================================================================
# FL MIDDLE to Stage mapping (from C777)
# =========================================================================
FL_STAGES = {
    # INITIAL (pos ~0.30)
    'ii': 'INITIAL', 'i': 'INITIAL',
    # EARLY (pos ~0.42)
    'in': 'EARLY',
    # MEDIAL (pos ~0.51-0.55)
    'r': 'MEDIAL', 'ar': 'MEDIAL',
    # LATE (pos ~0.60-0.64)
    'al': 'LATE', 'l': 'LATE', 'ol': 'LATE',
    # FINAL (pos ~0.75-0.80)
    'o': 'FINAL', 'ly': 'FINAL', 'am': 'FINAL',
    # TERMINAL (pos ~0.86-0.94)
    'm': 'TERMINAL', 'dy': 'TERMINAL', 'ry': 'TERMINAL', 'y': 'TERMINAL',
}

FL_MIDDLES = set(FL_STAGES.keys())

# Stage ordering for analysis
STAGE_ORDER = ['INITIAL', 'EARLY', 'MEDIAL', 'LATE', 'FINAL', 'TERMINAL']

# =========================================================================
# Hazard class sensory associations (from SENSORY_VALIDATION)
# =========================================================================
# These are the hazard types and their primary sensory resolution
HAZARD_SENSORY = {
    'PHASE_ORDERING': 'VISION',
    'COMPOSITION_JUMP': 'SMELL',
    'ENERGY_OVERSHOOT': 'SMELL_VISION',
    'RATE_MISMATCH': 'SIGHT_SOUND',
    'CONTAINMENT_TIMING': 'SOUND_TOUCH',
}

# Kernel operators and their associations
# h = phase check (VISION - seeing phase state)
# k = energy (SMELL_VISION - detecting energy excess)
# e = equilibration (TOUCH - thermal equilibrium)
KERNEL_SENSORY = {
    'h': 'VISION',      # Phase monitoring
    'k': 'SMELL_VISION', # Energy detection
    'e': 'TOUCH',        # Thermal/equilibrium
}

print("\nFL Stage mapping loaded:")
for stage in STAGE_ORDER:
    middles = [m for m, s in FL_STAGES.items() if s == stage]
    print(f"  {stage}: {', '.join(middles)}")

# =========================================================================
# Collect FL contexts from Currier B
# =========================================================================
print("\n" + "="*70)
print("COLLECTING FL CONTEXTS")
print("="*70)

# Group tokens by line
b_lines = defaultdict(list)
for token in tx.currier_b():
    if '*' not in token.word:
        b_lines[(token.folio, token.line)].append(token.word)

# Collect FL token contexts
fl_contexts = defaultdict(lambda: {
    'predecessors': [],
    'successors': [],
    'kernel_before': Counter(),
    'kernel_after': Counter(),
    'positions': [],
    'count': 0,
})

for (folio, line), tokens in b_lines.items():
    for i, word in enumerate(tokens):
        try:
            m = morph.extract(word)
            if m.middle in FL_MIDDLES:
                stage = FL_STAGES[m.middle]
                fl_contexts[stage]['count'] += 1
                fl_contexts[stage]['positions'].append(i / max(len(tokens)-1, 1))

                # Get predecessor
                if i > 0:
                    prev_word = tokens[i-1]
                    try:
                        prev_m = morph.extract(prev_word)
                        fl_contexts[stage]['predecessors'].append(prev_m.middle)
                        # Check for kernel characters in predecessor
                        for char in prev_word:
                            if char in 'hke':
                                fl_contexts[stage]['kernel_before'][char] += 1
                    except:
                        pass

                # Get successor
                if i < len(tokens) - 1:
                    next_word = tokens[i+1]
                    try:
                        next_m = morph.extract(next_word)
                        fl_contexts[stage]['successors'].append(next_m.middle)
                        # Check for kernel characters in successor
                        for char in next_word:
                            if char in 'hke':
                                fl_contexts[stage]['kernel_after'][char] += 1
                    except:
                        pass
        except:
            pass

print("\nFL stage counts:")
for stage in STAGE_ORDER:
    print(f"  {stage}: {fl_contexts[stage]['count']}")

# =========================================================================
# Test 1: Kernel profile by FL stage
# =========================================================================
print("\n" + "="*70)
print("TEST 1: KERNEL PROFILE BY FL STAGE")
print("="*70)

print("\nKernel operators AFTER each FL stage:")
print(f"{'Stage':<12} {'h (phase)':<12} {'k (energy)':<12} {'e (equilib)':<12} {'Dominant':<12}")
print("-"*60)

stage_kernel_profiles = {}
for stage in STAGE_ORDER:
    ctx = fl_contexts[stage]
    total = sum(ctx['kernel_after'].values())
    if total > 0:
        h_pct = 100 * ctx['kernel_after'].get('h', 0) / total
        k_pct = 100 * ctx['kernel_after'].get('k', 0) / total
        e_pct = 100 * ctx['kernel_after'].get('e', 0) / total

        # Determine dominant
        if h_pct > k_pct and h_pct > e_pct:
            dominant = 'h (VISION)'
        elif k_pct > h_pct and k_pct > e_pct:
            dominant = 'k (SMELL)'
        else:
            dominant = 'e (TOUCH)'

        stage_kernel_profiles[stage] = {'h': h_pct, 'k': k_pct, 'e': e_pct}
        print(f"{stage:<12} {h_pct:<12.1f} {k_pct:<12.1f} {e_pct:<12.1f} {dominant:<12}")
    else:
        print(f"{stage:<12} {'(no data)':<12}")

# =========================================================================
# Test 2: Kernel profile BEFORE each FL stage
# =========================================================================
print("\n" + "-"*50)
print("Kernel operators BEFORE each FL stage (what triggers FL?):")
print(f"{'Stage':<12} {'h (phase)':<12} {'k (energy)':<12} {'e (equilib)':<12} {'Dominant':<12}")
print("-"*60)

stage_kernel_before = {}
for stage in STAGE_ORDER:
    ctx = fl_contexts[stage]
    total = sum(ctx['kernel_before'].values())
    if total > 0:
        h_pct = 100 * ctx['kernel_before'].get('h', 0) / total
        k_pct = 100 * ctx['kernel_before'].get('k', 0) / total
        e_pct = 100 * ctx['kernel_before'].get('e', 0) / total

        if h_pct > k_pct and h_pct > e_pct:
            dominant = 'h (VISION)'
        elif k_pct > h_pct and k_pct > e_pct:
            dominant = 'k (SMELL)'
        else:
            dominant = 'e (TOUCH)'

        stage_kernel_before[stage] = {'h': h_pct, 'k': k_pct, 'e': e_pct}
        print(f"{stage:<12} {h_pct:<12.1f} {k_pct:<12.1f} {e_pct:<12.1f} {dominant:<12}")
    else:
        print(f"{stage:<12} {'(no data)':<12}")

# =========================================================================
# Test 3: Do early vs late FL stages have different kernel signatures?
# =========================================================================
print("\n" + "="*70)
print("TEST 3: EARLY vs LATE FL KERNEL DIVERGENCE")
print("="*70)

# Aggregate early stages (INITIAL, EARLY, MEDIAL) vs late stages (LATE, FINAL, TERMINAL)
early_stages = ['INITIAL', 'EARLY', 'MEDIAL']
late_stages = ['LATE', 'FINAL', 'TERMINAL']

early_kernel = Counter()
late_kernel = Counter()

for stage in early_stages:
    for k, v in fl_contexts[stage]['kernel_before'].items():
        early_kernel[k] += v

for stage in late_stages:
    for k, v in fl_contexts[stage]['kernel_before'].items():
        late_kernel[k] += v

early_total = sum(early_kernel.values())
late_total = sum(late_kernel.values())

print("\nKernel profile BEFORE FL stages:")
print(f"{'Kernel':<12} {'Early FL %':<15} {'Late FL %':<15} {'Ratio (L/E)':<15}")
print("-"*55)

kernel_ratios = {}
for k in ['h', 'k', 'e']:
    early_pct = 100 * early_kernel.get(k, 0) / early_total if early_total > 0 else 0
    late_pct = 100 * late_kernel.get(k, 0) / late_total if late_total > 0 else 0
    ratio = late_pct / early_pct if early_pct > 0 else float('inf')
    kernel_ratios[k] = ratio
    print(f"{k:<12} {early_pct:<15.1f} {late_pct:<15.1f} {ratio:<15.2f}")

# Chi-square test
if early_total > 10 and late_total > 10:
    contingency = [
        [early_kernel.get('h', 0), early_kernel.get('k', 0), early_kernel.get('e', 0)],
        [late_kernel.get('h', 0), late_kernel.get('k', 0), late_kernel.get('e', 0)],
    ]
    chi2, chi_p, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nChi-square (early vs late kernel): chi2={chi2:.2f}, p={chi_p:.4f}")

    if chi_p < 0.05:
        print("** Kernel profile DIFFERS between early and late FL stages **")
    else:
        print("Kernel profile does not differ significantly")

# =========================================================================
# Test 4: FL character composition and sensory inference
# =========================================================================
print("\n" + "="*70)
print("TEST 4: FL CHARACTER COMPOSITION")
print("="*70)

print("""
FL MIDDLE character patterns (from C777):
  - 'i' character = INITIAL state marker
  - 'y' character = TERMINAL state marker
  - Consonants (r, l, m, n) = intermediate markers

Hypothesis: Character might encode sensory modality:
  - 'i' = visual (you SEE material is present/starting)
  - 'y' = olfactory (you SMELL completion/terminal state)
  - Consonants = mixed/transitional
""")

# Check if 'i'-containing FL MIDDLEs have different kernel contexts than 'y'-containing
i_kernel = Counter()
y_kernel = Counter()
other_kernel = Counter()

for stage, ctx in fl_contexts.items():
    middles_in_stage = [m for m, s in FL_STAGES.items() if s == stage]

    for middle in middles_in_stage:
        if 'i' in middle and 'y' not in middle:
            for k, v in ctx['kernel_before'].items():
                i_kernel[k] += v
        elif 'y' in middle and 'i' not in middle:
            for k, v in ctx['kernel_before'].items():
                y_kernel[k] += v
        else:
            for k, v in ctx['kernel_before'].items():
                other_kernel[k] += v

i_total = sum(i_kernel.values())
y_total = sum(y_kernel.values())

print("\nKernel profile BEFORE FL MIDDLEs by character type:")
print(f"{'Type':<15} {'h %':<10} {'k %':<10} {'e %':<10} {'Implied Sense':<15}")
print("-"*55)

if i_total > 0:
    i_h = 100 * i_kernel.get('h', 0) / i_total
    i_k = 100 * i_kernel.get('k', 0) / i_total
    i_e = 100 * i_kernel.get('e', 0) / i_total
    i_sense = 'h=VISION' if i_h > i_k and i_h > i_e else ('k=SMELL' if i_k > i_e else 'e=TOUCH')
    print(f"{'i-forms':<15} {i_h:<10.1f} {i_k:<10.1f} {i_e:<10.1f} {i_sense:<15}")

if y_total > 0:
    y_h = 100 * y_kernel.get('h', 0) / y_total
    y_k = 100 * y_kernel.get('k', 0) / y_total
    y_e = 100 * y_kernel.get('e', 0) / y_total
    y_sense = 'h=VISION' if y_h > y_k and y_h > y_e else ('k=SMELL' if y_k > y_e else 'e=TOUCH')
    print(f"{'y-forms':<15} {y_h:<10.1f} {y_k:<10.1f} {y_e:<10.1f} {y_sense:<15}")

# =========================================================================
# Test 5: Predecessor MIDDLE patterns by FL stage
# =========================================================================
print("\n" + "="*70)
print("TEST 5: PREDECESSOR MIDDLES BY FL STAGE")
print("="*70)

print("\nTop 5 predecessors for each FL stage:")
for stage in STAGE_ORDER:
    preds = Counter(fl_contexts[stage]['predecessors'])
    top5 = preds.most_common(5)
    if top5:
        pred_str = ', '.join([f"{m}({c})" for m, c in top5])
        print(f"  {stage}: {pred_str}")

# Check if certain MIDDLEs preferentially precede certain FL stages
print("\nDo certain operations preferentially produce certain FL stages?")

# Build predecessor->FL_stage mapping
pred_to_stage = defaultdict(Counter)
for stage in STAGE_ORDER:
    for pred in fl_contexts[stage]['predecessors']:
        pred_to_stage[pred][stage] += 1

# Find predecessors with strong stage preferences
print("\nPredecessors with strong FL stage preferences (>50% to one stage):")
for pred, stage_counts in pred_to_stage.items():
    total = sum(stage_counts.values())
    if total >= 20:  # Minimum count
        for stage, count in stage_counts.items():
            pct = 100 * count / total
            if pct > 50:
                print(f"  {pred} → {stage} ({pct:.0f}% of {total})")

# =========================================================================
# Summary
# =========================================================================
print("\n" + "="*70)
print("SUMMARY: FL SENSORY MODALITY MAPPING")
print("="*70)

findings = []

# Check if kernel profile differs by FL stage
if 'chi_p' in dir() and chi_p < 0.05:
    findings.append(f"Kernel profile differs between early/late FL stages (chi2 p={chi_p:.4f})")

    # Interpret the difference
    if kernel_ratios.get('h', 1) < 0.8:
        findings.append("Late FL stages have LESS 'h' (phase/VISION) - visual monitoring decreases")
    if kernel_ratios.get('k', 1) > 1.2:
        findings.append("Late FL stages have MORE 'k' (energy/SMELL) - olfactory criteria increase")
    if kernel_ratios.get('e', 1) > 1.2:
        findings.append("Late FL stages have MORE 'e' (equilib/TOUCH) - thermal sensing increases")

# Check i vs y forms
if i_total > 10 and y_total > 10:
    if abs(i_h - y_h) > 10 or abs(i_k - y_k) > 10:
        findings.append(f"i-forms vs y-forms have different kernel profiles")
        if i_h > y_h:
            findings.append("  i-forms (INITIAL) are preceded by more 'h' (VISION)")
        if y_k > i_k:
            findings.append("  y-forms (TERMINAL) are preceded by more 'k' (SMELL)")

if not findings:
    findings.append("No clear sensory modality differentiation by FL stage")

print("\nKey findings:")
for i, f in enumerate(findings, 1):
    print(f"  {i}. {f}")

# Determine verdict
if any('differ' in f.lower() for f in findings):
    verdict = "SUPPORT"
    explanation = "FL stages show different sensory-associated kernel profiles"
else:
    verdict = "NOT SUPPORTED"
    explanation = "FL stages do not show clear sensory modality mapping"

print(f"\nVERDICT: {verdict}")
print(f"  {explanation}")

# Save results
output = {
    'stage_counts': {s: fl_contexts[s]['count'] for s in STAGE_ORDER},
    'kernel_profiles_after': stage_kernel_profiles,
    'kernel_profiles_before': stage_kernel_before,
    'early_vs_late_chi_p': chi_p if 'chi_p' in dir() else None,
    'kernel_ratios_late_early': kernel_ratios,
    'findings': findings,
    'verdict': verdict,
}

output_path = Path(__file__).parent.parent / 'results' / 'fl_sensory_modality.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2, default=float)

print(f"\n\nResults saved to {output_path}")
