"""Find recipes missing fire_degree and prepare batches for parallel extraction."""
import json

with open('data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

# Get recipes with missing fire_degree (0 means not set)
missing = [r for r in d['recipes'] if r.get('fire_degree', 0) == 0]
print(f'Total recipes missing fire_degree: {len(missing)}')

# Show first few to understand structure
print('\nSample recipes with source_lines:')
for r in missing[:5]:
    sl = r.get('source_lines', {})
    print(f"\nRecipe {r['id']}: {r['name_english'][:40]}")
    print(f"  source_lines: start={sl.get('start')}, end={sl.get('end')}")
    print(f"  procedure_lines: {sl.get('procedure_lines')}")

# Split into batches of ~40 for parallel processing
batch_size = 40
batches = []
for i in range(0, len(missing), batch_size):
    batch = missing[i:i+batch_size]
    batches.append({
        'batch_num': len(batches) + 1,
        'start_id': batch[0]['id'],
        'end_id': batch[-1]['id'],
        'count': len(batch),
        'recipes': [(r['id'], r['name_english'][:30], r.get('source_lines', {})) for r in batch]
    })

print(f'\n\nSplit into {len(batches)} batches:')
for b in batches:
    print(f"  Batch {b['batch_num']}: recipes {b['start_id']}-{b['end_id']} ({b['count']} recipes)")

# Save batch info for agents
with open('phases/PREP_POSTURE_DIVERGENCE/results/fire_degree_batches.json', 'w') as f:
    json.dump({'total_missing': len(missing), 'batches': batches}, f, indent=2)

print('\nBatch info saved to: phases/PREP_POSTURE_DIVERGENCE/results/fire_degree_batches.json')
