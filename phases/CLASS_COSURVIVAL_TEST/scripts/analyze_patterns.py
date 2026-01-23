"""Analyze the unique survivor patterns."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

with open(PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'a_record_survivors.json', 'r') as f:
    data = json.load(f)

# Find the unique patterns
patterns = {}
for rec in data['records']:
    key = tuple(sorted(rec['surviving_classes']))
    if key not in patterns:
        patterns[key] = {'count': 0, 'example': rec['a_record'], 'classes': list(key)}
    patterns[key]['count'] += 1

print(f"Found {len(patterns)} unique survivor patterns:")
print()
for i, (key, info) in enumerate(sorted(patterns.items(), key=lambda x: -x[1]['count'])):
    print(f"Pattern {i+1}: {info['count']} A records ({info['count']/len(data['records'])*100:.1f}%)")
    print(f"  Example: {info['example']}")
    print(f"  Classes surviving ({len(info['classes'])}): {info['classes'][:20]}{'...' if len(info['classes']) > 20 else ''}")

    # Find which classes are MISSING compared to all 49
    all_classes = set(range(1, 50))
    missing = all_classes - set(info['classes'])
    if missing:
        print(f"  Classes MISSING ({len(missing)}): {sorted(missing)}")
    else:
        print(f"  All 49 classes survive")
    print()

# Show which classes are always together vs sometimes excluded
always_survive = set(range(1, 50))
for key in patterns.keys():
    always_survive &= set(key)

print(f"Classes that survive in ALL patterns ({len(always_survive)}): {sorted(always_survive)}")

sometimes_excluded = set(range(1, 50)) - always_survive
print(f"Classes sometimes excluded ({len(sometimes_excluded)}): {sorted(sometimes_excluded)}")
