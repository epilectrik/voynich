"""
T1: CC Positional Integration

Question: Where does CC sit in the LINK-KERNEL-FL control loop sequence?

Method:
1. Compute mean normalized position for each CC subtype (daiin, ol, ol-derived)
2. Compare to LINK (0.476), KERNEL (0.482), FL (0.576) from C813
3. Test if CC precedes LINK (initiating role) or overlaps with other phases
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
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

# CC classes per C581, C788
# Class 10 = daiin only
# Class 11 = ol only
# Class 12 = k only (ghost - never appears in B)
# Class 17 = ol-prefixed tokens (olkeedy, olkeey, etc.)
CC_CLASSES = {10, 11, 12, 17}

# Collect tokens by line with positions
line_tokens = defaultdict(list)
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    key = (token.folio, token.line)
    tc = token_to_class.get(w)

    # Determine phase membership
    m = morph.extract(w)
    is_link = 'ol' in w  # LINK marker
    has_kernel = any(c in w for c in 'khe')  # Kernel chars
    is_fl = tc in {7, 30, 38, 40} if tc else False  # FL classes

    # CC classification
    cc_subtype = None
    if tc in CC_CLASSES:
        if w == 'daiin':
            cc_subtype = 'daiin'
        elif w == 'ol':
            cc_subtype = 'ol'
        elif tc == 17:
            cc_subtype = 'ol_derived'
        elif w == 'k':
            cc_subtype = 'k'

    line_tokens[key].append({
        'word': w,
        'class': tc,
        'is_link': is_link,
        'has_kernel': has_kernel,
        'is_fl': is_fl,
        'cc_subtype': cc_subtype,
    })

# Compute normalized positions
positions = {
    'daiin': [],
    'ol': [],
    'ol_derived': [],
    'LINK': [],
    'KERNEL': [],
    'FL': [],
}

for key, tokens in line_tokens.items():
    n = len(tokens)
    if n < 2:
        continue
    for i, t in enumerate(tokens):
        pos = i / (n - 1) if n > 1 else 0.5

        if t['cc_subtype']:
            positions[t['cc_subtype']].append(pos)
        if t['is_link']:
            positions['LINK'].append(pos)
        if t['has_kernel']:
            positions['KERNEL'].append(pos)
        if t['is_fl']:
            positions['FL'].append(pos)

# Compute statistics
print("=" * 60)
print("T1: CC POSITIONAL INTEGRATION")
print("=" * 60)

results = {}
for name, pos_list in positions.items():
    if len(pos_list) > 0:
        mean = np.mean(pos_list)
        std = np.std(pos_list)
        n = len(pos_list)
        results[name] = {'mean': mean, 'std': std, 'n': n}
        print(f"\n{name}:")
        print(f"  Mean position: {mean:.4f}")
        print(f"  Std dev: {std:.4f}")
        print(f"  Count: {n}")

# Order by mean position
ordered = sorted([(k, v['mean']) for k, v in results.items()], key=lambda x: x[1])
print("\n" + "-" * 40)
print("CANONICAL ORDERING (by mean position):")
print("-" * 40)
for name, mean in ordered:
    print(f"  {name}: {mean:.4f}")

# Statistical tests: CC subtypes vs control loop phases
print("\n" + "-" * 40)
print("STATISTICAL COMPARISONS:")
print("-" * 40)

# Test if CC subtypes precede LINK
comparisons = [
    ('daiin', 'LINK'),
    ('ol', 'LINK'),
    ('ol_derived', 'LINK'),
    ('daiin', 'KERNEL'),
    ('ol', 'KERNEL'),
    ('daiin', 'FL'),
]

for a, b in comparisons:
    if a in results and b in results:
        stat, p = stats.mannwhitneyu(
            positions[a], positions[b],
            alternative='two-sided'
        )
        delta = results[a]['mean'] - results[b]['mean']
        direction = "earlier" if delta < 0 else "later"
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "NS"
        print(f"  {a} vs {b}: delta={delta:+.4f} ({direction}), p={p:.2e} {sig}")

# Save results
output = {
    'positions': {k: {'mean': float(v['mean']), 'std': float(v['std']), 'n': v['n']}
                  for k, v in results.items()},
    'ordering': [{'phase': k, 'mean': float(v)} for k, v in ordered],
}

out_path = PROJECT_ROOT / 'phases' / 'CC_CONTROL_LOOP_INTEGRATION' / 'results' / 't1_positional_integration.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=True)

print(f"\nResults saved to {out_path.name}")
