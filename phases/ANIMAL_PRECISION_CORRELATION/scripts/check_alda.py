#!/usr/bin/env python3
"""Check what 'alda' actually represents - specific herb or class marker?"""

import json
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

# Find alda
for item in priors_data['results']:
    if item['middle'] == 'alda':
        print("ALDA PRIORS:")
        print(json.dumps(item, indent=2))
        break

print()
print("=" * 70)
print("COMPARISON: Specific vs Generic tokens")
print("=" * 70)
print()

# Compare alda to known specific tokens (like eoschso=chicken)
# and known generic class markers
tokens_to_check = ['alda', 'eoschso', 'chald', 'okaro', 'ockho']

for token in tokens_to_check:
    for item in priors_data['results']:
        if item['middle'] == token:
            print(f"{token}:")
            posterior = item.get('material_class_posterior', {})
            # Sort by probability
            sorted_priors = sorted(posterior.items(), key=lambda x: -x[1])
            for cls, prob in sorted_priors[:3]:
                print(f"  {cls}: {prob:.2f}")
            print()
            break

# Check how many tokens have high herb prior
print("=" * 70)
print("HERB CLASS DISTRIBUTION")
print("=" * 70)
print()

herb_tokens = []
for item in priors_data['results']:
    middle = item['middle']
    posterior = item.get('material_class_posterior', {})
    herb_prob = posterior.get('herb', 0)
    if herb_prob > 0.5:
        herb_tokens.append((middle, herb_prob))

herb_tokens.sort(key=lambda x: -x[1])
print(f"Tokens with P(herb) > 0.5: {len(herb_tokens)}")
print()
print("Top herb tokens:")
for token, prob in herb_tokens[:20]:
    print(f"  {token}: {prob:.2f}")

print()
print("=" * 70)
print("KEY QUESTION: Is 'herb' a CLASS or SPECIFIC material?")
print("=" * 70)
print()
print("In Brunschwig:")
print("  - 'herb' is a CLASS containing 360 materials")
print("  - Individual herbs have names like 'dorn', 'muntz', 'quuendel'")
print()
print("If P(herb)=0.86 for 'alda', this could mean:")
print("  1. 'alda' is a CLASS MARKER (generic herb designation)")
print("  2. 'alda' is one of many herbs with similar priors (no specific ID)")
print()
print("Checking: How many tokens share alda's prior distribution...")

# Find tokens with similar priors to alda
alda_priors = None
for item in priors_data['results']:
    if item['middle'] == 'alda':
        alda_priors = item.get('material_class_posterior', {})
        break

if alda_priors:
    similar_count = 0
    for item in priors_data['results']:
        posterior = item.get('material_class_posterior', {})
        if abs(posterior.get('herb', 0) - alda_priors.get('herb', 0)) < 0.01:
            similar_count += 1

    print(f"Tokens with identical P(herb) to alda: {similar_count}")
    print()
    if similar_count > 10:
        print("CONCLUSION: 'alda' is likely NOT a specific herb identifier.")
        print("            Many tokens share this prior - it's a CLASS probability,")
        print("            not evidence of specific material identity.")
