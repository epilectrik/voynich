#!/usr/bin/env python
"""
Generate a clean ASCII table of all constraints from INDEX.md and grouped registries.
Parses both the main index and all grouped registry files to capture all constraints.
"""
import re
from pathlib import Path

CLAIMS_DIR = Path(__file__).parent / 'CLAIMS'
INDEX_FILE = CLAIMS_DIR / 'INDEX.md'
OUTPUT_FILE = Path(__file__).parent / 'CONSTRAINT_TABLE.txt'

# Registry files that contain additional constraints
REGISTRY_FILES = [
    'tier0_core.md',
    'grammar_system.md',
    'currier_a.md',
    'morphology.md',
    'operations.md',
    'human_track.md',
    'azc_system.md',
    'organization.md',
]

# Scope inference from file names
FILE_SCOPE_MAP = {
    'tier0_core.md': 'B',
    'grammar_system.md': 'B',
    'currier_a.md': 'A',
    'morphology.md': 'GLOBAL',
    'operations.md': 'B',
    'human_track.md': 'HT',
    'azc_system.md': 'AZC',
    'organization.md': 'B',
}


def parse_index_constraints(index_path):
    """Parse constraints from INDEX.md tables"""
    constraints = {}

    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match table rows with constraints
    # Pattern: | NUMBER | Description | Tier | Scope | Location |
    # Handle both bold (**074**) and plain (074) numbers
    pattern = r'\|\s*\*{0,2}(\d+)\*{0,2}\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|'

    for match in re.finditer(pattern, content):
        num = int(match.group(1).strip())
        desc = match.group(2).strip()
        tier = match.group(3).strip()
        scope = match.group(4).strip()
        location = match.group(5).strip()

        # Clean up location - remove markdown links and Unicode
        location = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', location)
        location = location.replace('→', '->').replace('⊂', 'in:')
        location = location.strip()

        # Clean up description - remove markdown links
        desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)

        constraints[num] = {
            'num': num,
            'desc': desc,
            'tier': tier,
            'scope': scope,
            'location': location
        }

    return constraints


def parse_registry_constraints(registry_path, default_scope):
    """Parse constraints from a grouped registry file"""
    constraints = {}

    if not registry_path.exists():
        return constraints

    with open(registry_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: ## or ### C### - Title followed by **Tier:** # | **Status:**
    # Then description on next line(s)
    pattern1 = r'#{2,3}\s*C(\d+)\s*[-–]\s*(.+?)\n\*\*Tier:\*\*\s*(\d+)\s*\|'

    for match in re.finditer(pattern1, content):
        num = int(match.group(1))
        title = match.group(2).strip()
        tier = match.group(3).strip()

        # Get scope from context or default
        scope = default_scope

        # Location is the registry file
        location = f"in: {registry_path.stem}"

        if num not in constraints:
            constraints[num] = {
                'num': num,
                'desc': title,
                'tier': tier,
                'scope': scope,
                'location': location
            }

    # Pattern 2: ## or ### C### - Title followed by → See [link]
    # These reference individual files, should already be in INDEX
    pattern2 = r'#{2,3}\s*C(\d+)\s*[-–]\s*(.+?)\n→\s*See'

    for match in re.finditer(pattern2, content):
        num = int(match.group(1))
        title = match.group(2).strip()

        if num not in constraints:
            constraints[num] = {
                'num': num,
                'desc': title,
                'tier': '2',  # Default if not specified
                'scope': default_scope,
                'location': f"-> C{num:03d}_*.md"
            }

    return constraints


def parse_currier_a_special(currier_a_path):
    """Parse currier_a.md which has a unique format with more detail"""
    constraints = {}

    if not currier_a_path.exists():
        return constraints

    with open(currier_a_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match constraints like: ### C224 - A Coverage = 13.6%
    pattern = r'#{2,3}\s*C(\d+)\s*[-–]\s*(.+?)\n'

    for match in re.finditer(pattern, content):
        num = int(match.group(1))
        title = match.group(2).strip()

        # Look for tier after the title
        tier_match = re.search(
            rf'#{2,3}\s*C{num}\s*[-–][^\n]+\n\*\*Tier:\*\*\s*(\d+)',
            content
        )
        tier = tier_match.group(1) if tier_match else '2'

        # Determine scope based on constraint range
        if num >= 420:
            scope = 'A'
        elif num >= 345 and num <= 346:
            scope = 'A'
        elif num >= 224 and num <= 266:
            scope = 'A'
        else:
            scope = 'A'

        if num not in constraints:
            constraints[num] = {
                'num': num,
                'desc': title,
                'tier': tier,
                'scope': scope,
                'location': 'in: currier_a'
            }

    return constraints


def merge_constraints(*constraint_dicts):
    """Merge multiple constraint dictionaries, preferring earlier sources"""
    merged = {}
    for cd in constraint_dicts:
        for num, c in cd.items():
            if num not in merged:
                merged[num] = c
            else:
                # Keep existing but update if we have better scope info
                if merged[num]['scope'] == 'B' and c['scope'] != 'B':
                    merged[num]['scope'] = c['scope']
    return merged


def format_table(constraints):
    """Format constraints as minimal TSV for AI consumption"""
    lines = []

    # Simple tab-separated format - no decorative characters
    lines.append("NUM\tCONSTRAINT\tTIER\tSCOPE\tLOCATION")

    # Sort by constraint number
    sorted_constraints = sorted(constraints.values(), key=lambda x: x['num'])

    for c in sorted_constraints:
        num_str = f"C{c['num']:03d}"
        lines.append(f"{num_str}\t{c['desc']}\t{c['tier']}\t{c['scope']}\t{c['location']}")

    return '\n'.join(lines)


def main():
    print(f"Parsing constraints from {INDEX_FILE}...")
    index_constraints = parse_index_constraints(INDEX_FILE)
    print(f"Found {len(index_constraints)} constraints in INDEX.md")

    # Parse all registry files
    registry_constraints = {}
    for reg_file in REGISTRY_FILES:
        reg_path = CLAIMS_DIR / reg_file
        default_scope = FILE_SCOPE_MAP.get(reg_file, 'B')

        if reg_file == 'currier_a.md':
            rc = parse_currier_a_special(reg_path)
        else:
            rc = parse_registry_constraints(reg_path, default_scope)

        print(f"Found {len(rc)} constraints in {reg_file}")
        registry_constraints = merge_constraints(registry_constraints, rc)

    # Merge all constraints (INDEX takes priority for scope/location info)
    all_constraints = merge_constraints(index_constraints, registry_constraints)
    print(f"\nTotal unique constraints: {len(all_constraints)}")

    print("Generating table...")
    table = format_table(all_constraints)

    # Minimal header - pure ASCII
    from datetime import date
    today = date.today().isoformat()
    header = f"""CONSTRAINT_REFERENCE v2.6 | {len(all_constraints)} constraints | {today}
TIER: 0=frozen 1=falsified 2=established 3=speculative 4=exploratory
SCOPE: A=CurrierA B=CurrierB AZC=diagrams HT=HumanTrack GLOBAL=cross-system
LOCATION: ->=individual_file in:=grouped_registry

"""

    output = header + table

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Saved to {OUTPUT_FILE}")

    # Show constraint number ranges
    nums = sorted(all_constraints.keys())
    print(f"\nConstraint range: C{min(nums):03d} - C{max(nums):03d}")

    # Find gaps
    expected = set(range(min(nums), max(nums) + 1))
    actual = set(nums)
    gaps = expected - actual
    if gaps:
        print(f"Gaps in numbering: {len(gaps)} missing numbers (normal - numbers assigned chronologically)")


if __name__ == '__main__':
    main()
