"""
T2: CC Trigger Mechanics

Question: Does CC initiate the control loop? What follows CC tokens?

Method:
1. For each CC subtype, compute successor distribution (what phase follows?)
2. Test CC -> LINK -> KERNEL -> FL hypothesis
3. Compare CC successors to baseline phase rates
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Load class map
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
token_to_class = ctm['token_to_class']

CC_CLASSES = {10, 11, 12, 17}
FL_CLASSES = {7, 30, 38, 40}

def classify_token(word, tc):
    """Classify token into control loop phase"""
    phases = []

    # CC check
    if tc in CC_CLASSES:
        if word == 'daiin':
            phases.append('CC_DAIIN')
        elif word == 'ol':
            phases.append('CC_OL')
        elif tc == 17:
            phases.append('CC_OL_DERIVED')
        phases.append('CC')

    # LINK check (contains 'ol')
    if 'ol' in word:
        phases.append('LINK')

    # KERNEL check (contains k, h, or e)
    if any(c in word for c in 'khe'):
        phases.append('KERNEL')

    # FL check
    if tc in FL_CLASSES:
        phases.append('FL')

    return phases if phases else ['OTHER']

# Collect tokens by line
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    key = (token.folio, token.line)
    tc = token_to_class.get(w)
    phases = classify_token(w, tc)
    line_tokens[key].append({
        'word': w,
        'class': tc,
        'phases': phases,
    })

# Compute successor distributions for CC subtypes
successors = defaultdict(Counter)
baseline_phases = Counter()

total_transitions = 0
for key, tokens in line_tokens.items():
    for i in range(len(tokens) - 1):
        curr = tokens[i]
        next_t = tokens[i + 1]

        # Count baseline
        for p in next_t['phases']:
            baseline_phases[p] += 1
        total_transitions += 1

        # CC successor analysis
        for cc_type in ['CC_DAIIN', 'CC_OL', 'CC_OL_DERIVED', 'CC']:
            if cc_type in curr['phases']:
                for p in next_t['phases']:
                    successors[cc_type][p] += 1

# Compute enrichments
print("=" * 60)
print("T2: CC TRIGGER MECHANICS")
print("=" * 60)

baseline_rates = {p: c / total_transitions for p, c in baseline_phases.items()}

print("\nBASELINE PHASE RATES:")
for p in ['LINK', 'KERNEL', 'FL', 'CC', 'OTHER']:
    if p in baseline_rates:
        print(f"  {p}: {baseline_rates[p]*100:.1f}%")

results = {}
for cc_type in ['CC_DAIIN', 'CC_OL', 'CC_OL_DERIVED', 'CC']:
    total = sum(successors[cc_type].values())
    if total == 0:
        continue

    print(f"\n{'-'*40}")
    print(f"{cc_type} SUCCESSORS (n={total}):")
    print(f"{'-'*40}")

    results[cc_type] = {'total': total, 'successors': {}}

    for phase in ['LINK', 'KERNEL', 'FL', 'CC', 'OTHER']:
        count = successors[cc_type].get(phase, 0)
        rate = count / total if total > 0 else 0
        baseline = baseline_rates.get(phase, 0)
        enrichment = rate / baseline if baseline > 0 else 0

        results[cc_type]['successors'][phase] = {
            'count': count,
            'rate': float(rate),
            'baseline': float(baseline),
            'enrichment': float(enrichment),
        }

        if count > 0:
            print(f"  {phase}: {count} ({rate*100:.1f}%), baseline {baseline*100:.1f}%, enrichment {enrichment:.2f}x")

# Test CC -> LINK hypothesis specifically
print("\n" + "=" * 60)
print("CC -> LINK HYPOTHESIS TEST:")
print("=" * 60)

# Does CC preferentially route to LINK?
cc_link_rate = successors['CC'].get('LINK', 0) / sum(successors['CC'].values()) if successors['CC'] else 0
link_baseline = baseline_rates.get('LINK', 0)

# Chi-squared test
observed = successors['CC'].get('LINK', 0)
expected = sum(successors['CC'].values()) * link_baseline
if expected > 0:
    chi2 = (observed - expected) ** 2 / expected
    p_val = 1 - stats.chi2.cdf(chi2, df=1)
    print(f"\nCC -> LINK:")
    print(f"  Observed: {observed} ({cc_link_rate*100:.1f}%)")
    print(f"  Expected: {expected:.1f} ({link_baseline*100:.1f}%)")
    print(f"  Enrichment: {observed/expected:.2f}x")
    print(f"  Chi2={chi2:.2f}, p={p_val:.4f}")

# CC -> KERNEL
cc_kernel_rate = successors['CC'].get('KERNEL', 0) / sum(successors['CC'].values()) if successors['CC'] else 0
kernel_baseline = baseline_rates.get('KERNEL', 0)
observed_k = successors['CC'].get('KERNEL', 0)
expected_k = sum(successors['CC'].values()) * kernel_baseline
if expected_k > 0:
    chi2_k = (observed_k - expected_k) ** 2 / expected_k
    p_val_k = 1 - stats.chi2.cdf(chi2_k, df=1)
    print(f"\nCC -> KERNEL:")
    print(f"  Observed: {observed_k} ({cc_kernel_rate*100:.1f}%)")
    print(f"  Expected: {expected_k:.1f} ({kernel_baseline*100:.1f}%)")
    print(f"  Enrichment: {observed_k/expected_k:.2f}x")
    print(f"  Chi2={chi2_k:.2f}, p={p_val_k:.4f}")

# Save results
output = {
    'baseline_rates': {k: float(v) for k, v in baseline_rates.items()},
    'cc_successors': results,
    'total_transitions': total_transitions,
}

out_path = PROJECT_ROOT / 'phases' / 'CC_CONTROL_LOOP_INTEGRATION' / 'results' / 't2_trigger_mechanics.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
