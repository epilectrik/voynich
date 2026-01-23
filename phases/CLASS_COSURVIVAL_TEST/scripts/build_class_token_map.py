"""Build bidirectional mappings between tokens, classes, and MIDDLEs."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Morphology extraction
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)

def extract_middle(token):
    """Extract MIDDLE component from token."""
    if not token:
        return None
    remainder = token
    for p in ALL_PREFIXES:
        if remainder.startswith(p):
            remainder = remainder[len(p):]
            break
    for s in ALL_SUFFIXES:
        if remainder.endswith(s) and len(remainder) > len(s):
            remainder = remainder[:-len(s)]
            break
    return remainder if remainder else None


def main():
    print("=" * 70)
    print("BUILD CLASS-TOKEN MAP")
    print("=" * 70)

    # Load phase20a data
    with open(PROJECT_ROOT / 'results' / 'phase20a_operator_equivalence.json', 'r') as f:
        data = json.load(f)

    classes = data['classes']
    print(f"Loaded {len(classes)} instruction classes")

    # Build mappings
    token_to_class = {}
    token_to_role = {}
    token_to_middle = {}
    class_to_tokens = {}
    class_to_role = {}
    class_to_middles = {}

    atomic_classes = []  # Classes with no MIDDLE component
    decomposable_classes = []  # Classes with MIDDLE components

    for cls in classes:
        class_id = cls['class_id']
        role = cls['functional_role']
        members = cls['members']

        class_to_tokens[class_id] = members
        class_to_role[class_id] = role
        class_to_middles[class_id] = set()

        has_middle = False
        for token in members:
            token_to_class[token] = class_id
            token_to_role[token] = role
            middle = extract_middle(token)
            token_to_middle[token] = middle
            if middle:
                class_to_middles[class_id].add(middle)
                has_middle = True

        if has_middle:
            decomposable_classes.append(class_id)
        else:
            atomic_classes.append(class_id)

        # Convert set to list for JSON
        class_to_middles[class_id] = list(class_to_middles[class_id])

    print(f"\nTotal tokens mapped: {len(token_to_class)}")
    print(f"Atomic classes (no MIDDLE): {len(atomic_classes)} -> {atomic_classes}")
    print(f"Decomposable classes (with MIDDLE): {len(decomposable_classes)}")

    # Infrastructure classes (from BCI)
    infrastructure_classes = [36, 42, 44, 46]
    print(f"\nInfrastructure classes (BCI): {infrastructure_classes}")

    # Check overlap
    infra_in_atomic = [c for c in infrastructure_classes if c in atomic_classes]
    infra_in_decomp = [c for c in infrastructure_classes if c in decomposable_classes]
    print(f"  - Atomic: {infra_in_atomic}")
    print(f"  - Decomposable: {infra_in_decomp}")

    # Summary by role
    print("\n--- Classes by Role ---")
    role_counts = {}
    for class_id, role in class_to_role.items():
        role_counts[role] = role_counts.get(role, 0) + 1
    for role, count in sorted(role_counts.items(), key=lambda x: -x[1]):
        print(f"  {role}: {count} classes")

    # Save output
    output = {
        'token_to_class': token_to_class,
        'token_to_role': token_to_role,
        'token_to_middle': token_to_middle,
        'class_to_tokens': class_to_tokens,
        'class_to_role': class_to_role,
        'class_to_middles': class_to_middles,
        'atomic_classes': atomic_classes,
        'decomposable_classes': decomposable_classes,
        'infrastructure_classes': infrastructure_classes,
        'metadata': {
            'total_classes': len(classes),
            'total_tokens': len(token_to_class),
            'atomic_count': len(atomic_classes),
            'decomposable_count': len(decomposable_classes),
        }
    }

    output_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
