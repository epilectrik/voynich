"""
06_non_fl_kernel_free.py

Analyze the 142 kernel-free PP MIDDLEs that are NOT classified as FL in B.
What roles do they play? Can we extend FL-like semantics to them?
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

# Load class map
class_map_path = Path(__file__).resolve().parents[3] / "phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json"
with open(class_map_path) as f:
    class_data = json.load(f)

token_to_class = {k: int(v) for k, v in class_data['token_to_class'].items()}
token_to_role = class_data['token_to_role']
FL_CLASSES = {7, 30, 38, 40}

tx = Transcript()
morph = Morphology()

# Get all MIDDLEs
a_middles = set()
b_middles = set()
for t in tx.currier_a():
    m = morph.extract(t.word)
    if m and m.middle:
        a_middles.add(m.middle)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

pp_middles = a_middles & b_middles

# Get FL MIDDLEs
fl_middles = set()
for t in tx.currier_b():
    cls = token_to_class.get(t.word)
    if cls in FL_CLASSES:
        m = morph.extract(t.word)
        if m and m.middle:
            fl_middles.add(m.middle)

# Kernel-free PP
kernel_chars = set('khe')
kernel_free_pp = {m for m in pp_middles if not any(c in m for c in kernel_chars)}
non_fl_kernel_free = kernel_free_pp - fl_middles

print("=" * 60)
print("Non-FL Kernel-Free PP MIDDLEs: What Are They?")
print("=" * 60)
print(f"\nKernel-free PP: {len(kernel_free_pp)}")
print(f"FL MIDDLEs: {len(fl_middles)}")
print(f"Non-FL kernel-free: {len(non_fl_kernel_free)}")

# For each non-FL kernel-free MIDDLE, find what roles they belong to in B
middle_to_roles = defaultdict(Counter)
middle_to_classes = defaultdict(Counter)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle and m.middle in non_fl_kernel_free:
        role = token_to_role.get(t.word, 'UNKNOWN')
        cls = token_to_class.get(t.word, -1)
        middle_to_roles[m.middle][role] += 1
        middle_to_classes[m.middle][cls] += 1

print("\n" + "=" * 60)
print("Role Distribution of Non-FL Kernel-Free PP")
print("=" * 60)

# Aggregate role counts
total_role_counts = Counter()
for mid, roles in middle_to_roles.items():
    for role, count in roles.items():
        total_role_counts[role] += count

print("\n--- Aggregate Role Distribution ---")
total = sum(total_role_counts.values())
for role, count in total_role_counts.most_common():
    print(f"  {role:25} {count:6} ({count/total*100:5.1f}%)")

# Show which MIDDLEs map to which roles
print("\n" + "=" * 60)
print("MIDDLE -> Role Mapping (Non-FL Kernel-Free)")
print("=" * 60)

# Group MIDDLEs by their dominant role
role_to_middles = defaultdict(list)
for mid in non_fl_kernel_free:
    if mid in middle_to_roles:
        dominant_role = middle_to_roles[mid].most_common(1)[0][0]
        total_count = sum(middle_to_roles[mid].values())
        role_to_middles[dominant_role].append((mid, total_count))

for role in ['ENERGY_OPERATOR', 'AUXILIARY', 'FREQUENT_OPERATOR', 'CORE_CONTROL', 'HT', 'UNKNOWN']:
    middles = role_to_middles.get(role, [])
    if middles:
        middles.sort(key=lambda x: -x[1])
        print(f"\n{role}:")
        for mid, count in middles[:10]:
            print(f"  {mid:12} x{count}")

# Check character composition of non-FL kernel-free
print("\n" + "=" * 60)
print("Character Analysis: Non-FL Kernel-Free PP")
print("=" * 60)

char_counts = Counter()
for mid in non_fl_kernel_free:
    for c in mid:
        char_counts[c] += 1

print("\nCharacter frequency:")
for c, count in char_counts.most_common():
    print(f"  '{c}': {count}")

# Compare to FL characters
fl_chars = set()
for mid in fl_middles:
    fl_chars.update(mid)

non_fl_chars = set()
for mid in non_fl_kernel_free:
    non_fl_chars.update(mid)

print(f"\nFL uses characters: {sorted(fl_chars)}")
print(f"Non-FL kernel-free uses: {sorted(non_fl_chars)}")
print(f"Shared: {sorted(fl_chars & non_fl_chars)}")
print(f"Non-FL only: {sorted(non_fl_chars - fl_chars)}")

# The key difference
extra_chars = non_fl_chars - fl_chars
print(f"\n" + "=" * 60)
print("KEY FINDING: Extra Characters in Non-FL Kernel-Free")
print("=" * 60)
print(f"""
FL MIDDLEs use ONLY: {sorted(fl_chars)}
  (a, d, i, l, m, n, o, r, y - 9 characters)

Non-FL kernel-free ALSO uses: {sorted(extra_chars)}

The extra characters are: {sorted(extra_chars)}

These extra characters ({', '.join(sorted(extra_chars))}) may encode:
  - Different role semantics (AX, FQ, CC patterns)
  - Helper modifiers (c, s, t)
  - Domain-specific markers
""")

# Check which non-FL kernel-free MIDDLEs use ONLY FL characters
fl_char_only = [m for m in non_fl_kernel_free if all(c in fl_chars for c in m)]
print(f"\nNon-FL kernel-free using ONLY FL characters: {len(fl_char_only)}")
if fl_char_only:
    print("These MIDDLEs:")
    for mid in sorted(fl_char_only)[:20]:
        roles = middle_to_roles.get(mid, {})
        role_str = ', '.join(f"{r}:{c}" for r, c in roles.most_common(2))
        print(f"  {mid:12} -> {role_str}")

# Write JSON result
result = {
    "kernel_free_pp_count": len(kernel_free_pp),
    "fl_middles_count": len(fl_middles),
    "non_fl_kernel_free_count": len(non_fl_kernel_free),
    "aggregate_role_distribution": {role: count for role, count in total_role_counts.most_common()},
    "role_to_middles": {
        role: [{"middle": mid, "count": count} for mid, count in sorted(mids, key=lambda x: -x[1])[:10]]
        for role, mids in role_to_middles.items()
    },
    "fl_characters": sorted(fl_chars),
    "non_fl_characters": sorted(non_fl_chars),
    "extra_characters": sorted(non_fl_chars - fl_chars),
    "fl_char_only_non_fl_middles": sorted(fl_char_only),
    "fl_char_only_count": len(fl_char_only),
    "fl_char_only_roles": {
        mid: {r: c for r, c in middle_to_roles.get(mid, {}).most_common(3)}
        for mid in sorted(fl_char_only)
    },
    "verdict": f"{len(fl_char_only)} non-FL kernel-free MIDDLEs use only FL characters"
}

out_path = Path(__file__).resolve().parents[1] / "results" / "06_non_fl_kernel_free.json"
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)
print(f"\nResult written to {out_path}")
