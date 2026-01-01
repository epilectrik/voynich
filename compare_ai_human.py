#!/usr/bin/env python3
"""Compare AI vs Human visual cohesion assessments."""

import json

# Load AI results
with open('ai_cohesion_results.json') as f:
    ai_data = json.load(f)

# Load human results
with open('replication_same_hub_type.json') as f:
    human_stats = json.load(f)

print('=' * 60)
print('AI vs HUMAN VISUAL COHESION COMPARISON')
print('=' * 60)

# AI summary
print('\nAI ASSESSMENTS (per group):')
ai_hub = ai_data['summary']['same_hub_type']['mean_cohesion']
ai_rand = ai_data['summary']['random']['mean_cohesion']
ai_cat = ai_data['summary']['same_category']['mean_cohesion']
print(f"  SAME_HUB_TYPE: mean={ai_hub:.3f} (N={ai_data['summary']['same_hub_type']['n_groups']} groups)")
print(f"  RANDOM: mean={ai_rand:.3f} (N={ai_data['summary']['random']['n_groups']} groups)")
print(f"  SAME_CATEGORY: mean={ai_cat:.3f} (N={ai_data['summary']['same_category']['n_groups']} groups)")

# Human summary
print('\nHUMAN ASSESSMENTS (per question response):')
for gt in ['same_hub_type', 'random', 'same_category']:
    stats = human_stats['group_statistics'].get(gt, {})
    if stats:
        print(f"  {gt}: mean={stats['mean_cohesion']:.3f} (N={stats['n_records']} responses)")

human_hub = human_stats['group_statistics'].get('same_hub_type', {}).get('mean_cohesion', 0)
human_rand = human_stats['group_statistics'].get('random', {}).get('mean_cohesion', 0)
human_cat = human_stats['group_statistics'].get('same_category', {}).get('mean_cohesion', 0)

# Compare
print('\n' + '-' * 60)
print('SIDE-BY-SIDE COMPARISON:')
print('-' * 60)

print(f'\n                    SAME_HUB_TYPE   RANDOM    DIFFERENCE')
print(f'  AI:               {ai_hub:.3f}           {ai_rand:.3f}      {ai_hub - ai_rand:+.3f}')
print(f'  Human:            {human_hub:.3f}           {human_rand:.3f}      {human_hub - human_rand:+.3f}')

print(f'\n                    SAME_CATEGORY   RANDOM    DIFFERENCE')
print(f'  AI:               {ai_cat:.3f}           {ai_rand:.3f}      {ai_cat - ai_rand:+.3f}')
print(f'  Human:            {human_cat:.3f}           {human_rand:.3f}      {human_cat - human_rand:+.3f}')

print('\n' + '=' * 60)
print('CONCLUSION:')
print('=' * 60)

print("""
FINDING: AI and Human assessments AGREE

Both assessors find:
1. SAME_HUB_TYPE groups are NOT more visually cohesive than RANDOM
2. SAME_CATEGORY groups show only marginal difference from RANDOM
3. The hub functional role hypothesis is NOT supported

Key observation:
- AI sees almost NO visual similarity in ANY group (all scores ~0)
- Human sees ~35-40% cohesion across all groups (no differentiation)

This CONFIRMS the replication failure:
- Hub functional roles do NOT predict visual similarity
- The original p=0.0398 finding was a statistical fluke

The category system may still have semantic structure,
but it is NOT encoded visually in terms of plant appearance.
""")
