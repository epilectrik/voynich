"""Check fire degree values in detail."""
import json

with open('data/brunschwig_curated_v2.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("First 30 recipes fire degree check:")
print("-" * 80)
for r in d['recipes'][:30]:
    fd = r.get('fire_degree', 'N/A')
    method = r.get('method', '') or ''
    name = r.get('name_english', '')[:35]
    print(f"{r['id']:3d}. {name:35s} fire={fd} method={method}")

print("\n" + "=" * 80)
print("\nFire degree distribution across ALL recipes:")
from collections import Counter
fds = Counter(r.get('fire_degree', 'N/A') for r in d['recipes'])
for fd, count in sorted(fds.items()):
    print(f"  fire_degree={fd}: {count} recipes")

# Check if method field has fire info
print("\n" + "=" * 80)
print("\nMethod field distribution:")
methods = Counter(r.get('method', '') or 'NONE' for r in d['recipes'])
for m, count in methods.most_common(10):
    print(f"  '{m}': {count}")
