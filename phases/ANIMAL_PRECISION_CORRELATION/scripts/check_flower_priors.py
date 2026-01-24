#!/usr/bin/env python3
import json
from pathlib import Path

PROJECT_ROOT = Path('C:/git/voynich')

# Load priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)

# Check for cold_moist_flower
flower_tokens = []
for item in priors_data['results']:
    posterior = item.get('material_class_posterior', {})
    flower_prob = posterior.get('cold_moist_flower', 0)
    if flower_prob > 0:
        flower_tokens.append((item['middle'], flower_prob))

print(f"Tokens with P(cold_moist_flower) > 0: {len(flower_tokens)}")
print()

if flower_tokens:
    for token, prob in sorted(flower_tokens, key=lambda x: -x[1])[:20]:
        print(f"  {token}: {prob:.2f}")
else:
    # Check what classes have any tokens
    print("Classes with tokens:")
    class_counts = {}
    for item in priors_data['results']:
        for cls, prob in item.get('material_class_posterior', {}).items():
            if prob > 0:
                class_counts[cls] = class_counts.get(cls, 0) + 1

    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"  {cls}: {count} tokens")
