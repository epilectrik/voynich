"""Full breakdown of 49 instruction classes by role."""
import json

with open('results/phase20a_operator_equivalence.json', 'r') as f:
    data = json.load(f)

# Group by role
by_role = {}
for cls in data['classes']:
    role = cls['functional_role']
    if role not in by_role:
        by_role[role] = []
    by_role[role].append(cls)

print("=" * 70)
print("FULL 49-CLASS BREAKDOWN BY ROLE")
print("=" * 70)

total_classes = 0
total_tokens = 0
for role, classes in sorted(by_role.items(), key=lambda x: -len(x[1])):
    print(f"\n{role}: {len(classes)} classes")
    for cls in classes:
        sig = cls['behavioral_signature']
        print(f"  Class {cls['class_id']:2d}: {cls['member_count']:2d} tokens, "
              f"kernel_prox={sig['mean_kernel_proximity']:.2f}, "
              f"freq_rank={sig['mean_frequency_rank']:.2f}")
        total_classes += 1
        total_tokens += cls['member_count']

print(f"\n" + "=" * 70)
print(f"TOTALS: {total_classes} classes, {total_tokens} tokens")
print("=" * 70)

# Now show what distinguishes AUXILIARY classes from each other
print("\n" + "=" * 70)
print("WHAT DISTINGUISHES AUXILIARY CLASSES?")
print("=" * 70)

aux_classes = by_role.get('AUXILIARY', [])
print(f"\nComparing {len(aux_classes)} AUXILIARY classes:\n")
print(f"{'Class':>6} {'Tokens':>6} {'KernelProx':>10} {'FreqRank':>10} {'OpType':>10} {'Length':>10}")
print("-" * 60)
for cls in aux_classes:
    sig = cls['behavioral_signature']
    print(f"{cls['class_id']:>6} {cls['member_count']:>6} "
          f"{sig['mean_kernel_proximity']:>10.3f} "
          f"{sig['mean_frequency_rank']:>10.3f} "
          f"{sig['mean_operator_type']:>10.3f} "
          f"{sig['mean_length']:>10.3f}")

# Show tokens in each AUXILIARY class
print("\n" + "=" * 70)
print("AUXILIARY CLASS MEMBERS")
print("=" * 70)
for cls in aux_classes[:3]:  # First 3 for brevity
    print(f"\nClass {cls['class_id']} ({cls['member_count']} tokens):")
    print(f"  {cls['members']}")
