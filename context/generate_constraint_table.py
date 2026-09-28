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


# Row patterns are confined to ONE line ([ \t] not \s, [^|\n] not [^|]). With \s a match could run across a
# line break, so a struck row could swallow the row after it (fixed 2026-09-28: C132 was silently dropped).
STRUCK_ROW = re.compile(
    r'^\|[ \t]*~~[ \t]*\*{0,2}(\d+(?:\.[a-z])?)\*{0,2}[ \t]*~~[ \t]*\|[ \t]*(.+?)[ \t]*\|[ \t]*([^|\n]*?)[ \t]*\|'
    r'[ \t]*([^|\n]+?)[ \t]*\|[ \t]*(.+?)[ \t]*\|',
    re.MULTILINE)
DEAD_STATUS = re.compile(r'STATUS:\s*(RETRACTED|SUPERSEDED)', re.IGNORECASE)


def registry_entry_is_dead(title, tier_line_tail):
    """A grouped-registry entry is dead only if its own Status field says so
    (RETRACTED / SUPERSEDED / REFUTED), it carries a 'Superseded by' pointer, or its
    title *is* the status (e.g. '### C172 - SUPERSEDED'). A title that merely mentions an
    earlier retraction (e.g. C287 '(EXT-9B RETRACTION)') is NOT dead. INVALIDATED Tier-1
    entries stay (negative knowledge)."""
    m = re.search(r'\*\*Status:\*\*\s*([A-Za-z_:]+)', tier_line_tail)
    status = m.group(1).upper() if m else ''
    if status.startswith(('RETRACTED', 'SUPERSEDED', 'REFUTED')):
        return True
    if re.search(r'Superseded by', tier_line_tail, re.IGNORECASE):
        return True
    if re.match(r'\s*(SUPERSEDED|RETRACTED)\b', title, re.IGNORECASE):
        return True
    return False


def _num_key(num_str):
    return num_str if '.' in num_str else int(num_str)


def parse_struck_index_rows(content):
    """Struck rows (~~N~~). Convention (2026-09-27 reconciliation):
    - a struck row whose tier cell still carries a live tier digit (e.g. '~~2~~ 3', or '1' for a
      claim retracted into a Tier-1 falsification) is ALIVE at that tier (demotion / re-tiering);
    - a struck row with no live tier digit, or any row tagged STATUS:RETRACTED|SUPERSEDED, is DEAD.
    Returns (alive_dict, dead_set)."""
    alive, dead = {}, set()
    for m in STRUCK_ROW.finditer(content):
        num_str = m.group(1).strip()
        desc = m.group(2).strip()
        tier_cell = m.group(3).strip()
        live_tier = re.sub(r'~~.*?~~', '', tier_cell).strip()
        key = _num_key(num_str)
        if DEAD_STATUS.search(desc) or live_tier not in ('0', '1', '2', '3', '4'):
            dead.add(key)
            continue
        desc = desc.replace('~~', '')
        desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)
        location = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', m.group(5).strip())
        location = location.replace('→', '->').replace('⊂', 'in:').strip()
        alive[key] = {'num': num_str, 'desc': desc, 'tier': live_tier,
                      'scope': m.group(4).strip(), 'location': location}
    return alive, dead


def parse_index_constraints(index_path):
    """Parse constraints from INDEX.md tables. Returns (constraints, dead_set)."""
    constraints = {}
    dead = set()

    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match table rows with constraints
    # Pattern: | NUMBER | Description | Tier | Scope | Location |
    # Handle both bold (**074**) and plain (074) numbers
    # Also handle sub-numbered constraints like 384.a
    # The number field must be ONLY digits (optionally .a/.b suffix) — reject ranges like 251-262
    # Tier cell forms: '2' | '~~2~~ 3' (demoted, alive at 3) | '~~2~~' (dead) | '2/3' (borderline -> 3)
    pattern = (r'^\|[ \t]*\*{0,2}(\d+(?:\.[a-z])?)\*{0,2}[ \t]*\|[ \t]*(.+?)[ \t]*\|[ \t]*'
               r'(\d+|~~[ \t]*\d[ \t]*~~[ \t]*\d?|\d[ \t]*/[ \t]*\d)[ \t]*\|[ \t]*([^|\n]+?)[ \t]*\|[ \t]*(.+?)[ \t]*\|')

    for match in re.finditer(pattern, content, re.MULTILINE):
        num_str = match.group(1).strip()
        desc = match.group(2).strip()
        raw_tier = match.group(3).strip()
        scope = match.group(4).strip()
        location = match.group(5).strip()
        if '~~' in raw_tier:
            tier = re.sub(r'~~.*?~~', '', raw_tier).strip()
            if tier not in ('0', '1', '2', '3', '4'):
                dead.add(_num_key(num_str))
                continue
        elif '/' in raw_tier:
            tier = raw_tier.split('/')[-1].strip()   # borderline: take the lower-confidence tier
            desc = f"[tier cell {raw_tier}] " + desc
        else:
            tier = raw_tier

        # Skip if tier is not a valid number 0-4 (catches garbled range-row mis-parses)
        if tier not in ('0', '1', '2', '3', '4'):
            continue

        # Skip retracted/superseded rows via parseable status tag.
        # Belt-and-suspenders: strikethrough (~~N~~) already drops struck rows at
        # the number-field regex; this also drops a status-tagged retraction whose
        # row wasn't struck — preventing the notice-vs-stale-row drift (the
        # C1959/C1960/C1970 failure: retraction recorded in prose but row left live).
        if DEAD_STATUS.search(desc):
            dead.add(_num_key(num_str))
            continue

        # Clean up location - remove markdown links and Unicode
        location = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', location)
        location = location.replace('→', '->').replace('⊂', 'in:')
        location = location.strip()

        # Clean up description - remove markdown links
        desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)

        # Normalize key to int for proper deduplication (handle sub-numbers like '384.a')
        key = num_str if '.' in num_str else int(num_str)
        constraints[key] = {
            'num': num_str,
            'desc': desc,
            'tier': tier,
            'scope': scope,
            'location': location
        }

    struck_alive, struck_dead = parse_struck_index_rows(content)
    for key, c in struck_alive.items():
        constraints.setdefault(key, c)
    dead |= struck_dead
    for key in dead:
        constraints.pop(key, None)
    return constraints, dead


def parse_registry_constraints(registry_path, default_scope):
    """Parse constraints from a grouped registry file"""
    constraints = {}

    if not registry_path.exists():
        return constraints

    with open(registry_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: ## or ### C### - Title followed by **Tier:** # | **Status:**
    # Then description on next line(s)
    pattern1 = r'#{2,3}\s*C(\d+)\s*[-–]\s*(.+?)\n(?:[ \t]*\n)?\*\*Tier:\*\*\s*(\d+)([^\n]*)'

    for match in re.finditer(pattern1, content):
        num = int(match.group(1))
        title = match.group(2).strip()
        tier = match.group(3).strip()
        status_tail = match.group(4)
        if registry_entry_is_dead(title, status_tail):
            continue

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
            rf'#{{2,3}}\s*C{num}\s*[-–][^\n]+\n(?:[ \t]*\n)?\*\*Tier:\*\*\s*(\d+)([^\n]*)',
            content
        )
        tier = tier_match.group(1) if tier_match else '2'
        tail = tier_match.group(2) if tier_match else ''
        if registry_entry_is_dead(title, tail):
            continue

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


def constraint_sort_key(num):
    """Sort key for constraint numbers (handles both '384' and '384.a')"""
    if isinstance(num, int):
        return (num, '')
    num_str = str(num)
    if '.' in num_str:
        base, suffix = num_str.split('.', 1)
        return (int(base), suffix)
    return (int(num_str), '')


def format_table(constraints):
    """Format constraints as minimal TSV for AI consumption"""
    lines = []

    # Simple tab-separated format - no decorative characters
    lines.append("NUM\tCONSTRAINT\tTIER\tSCOPE\tLOCATION")

    # Sort by constraint number (handles both integers and strings like '384.a')
    sorted_constraints = sorted(constraints.values(), key=lambda x: constraint_sort_key(x['num']))

    for c in sorted_constraints:
        num = c['num']
        if isinstance(num, int):
            num_str = f"C{num:03d}"
        else:
            # Handle sub-numbered like '384.a' -> 'C384.a'
            parts = str(num).split('.')
            if len(parts) == 2:
                num_str = f"C{int(parts[0]):03d}.{parts[1]}"
            else:
                num_str = f"C{int(num):03d}"
        lines.append(f"{num_str}\t{c['desc']}\t{c['tier']}\t{c['scope']}\t{c['location']}")

    return '\n'.join(lines)


def main():
    print(f"Parsing constraints from {INDEX_FILE}...")
    index_constraints, dead = parse_index_constraints(INDEX_FILE)
    print(f"Found {len(index_constraints)} live constraints in INDEX.md "
          f"({len(dead)} dead: struck or STATUS-retracted/superseded)")

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
    # A number that INDEX marks dead must never be re-imported from a grouped registry
    for key in dead:
        all_constraints.pop(key, None)
    print(f"\nTotal unique constraints: {len(all_constraints)}")
    from collections import Counter
    tier_counts = Counter(str(c['tier']) for c in all_constraints.values())
    tier_summary = ' '.join(f"T{t}={tier_counts.get(t, 0)}" for t in ('0', '1', '2', '3', '4'))
    print(f"By tier: {tier_summary}")

    print("Generating table...")
    table = format_table(all_constraints)

    # Minimal header - pure ASCII
    from datetime import date
    today = date.today().isoformat()
    header = f"""CONSTRAINT_REFERENCE v2.7 | {len(all_constraints)} live constraints ({tier_summary}) | {today}
TIER: 0=frozen 1=falsified 2=established 3=speculative 4=exploratory
SCOPE: A=CurrierA B=CurrierB AZC=diagrams HT=HumanTrack GLOBAL=cross-system
LOCATION: ->=individual_file in:=grouped_registry

"""

    output = header + table

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Saved to {OUTPUT_FILE}")

    # Show constraint number ranges
    # Extract base numbers (ignoring sub-numbers like .a, .b)
    base_nums = []
    for num in all_constraints.keys():
        if isinstance(num, int):
            base_nums.append(num)
        else:
            base = str(num).split('.')[0]
            base_nums.append(int(base))

    base_nums = sorted(set(base_nums))
    print(f"\nConstraint range: C{min(base_nums):03d} - C{max(base_nums):03d}")

    # Find gaps (only for base numbers)
    expected = set(range(min(base_nums), max(base_nums) + 1))
    actual = set(base_nums)
    gaps = expected - actual
    if gaps:
        print(f"Gaps in numbering: {len(gaps)} missing numbers (normal - numbers assigned chronologically)")


if __name__ == '__main__':
    main()
