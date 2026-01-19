#!/usr/bin/env python
"""
Generate FIT_TABLE.txt from fit registry files.

Parses the standard format:
    ### F-X-### - Title
    **Tier:** F# | **Result:** SUCCESS/PARTIAL/NULL | **Supports:** C###, C###
"""
import re
from pathlib import Path
from datetime import date

FITS_DIR = Path(__file__).parent
OUTPUT_FILE = FITS_DIR / 'FIT_TABLE.txt'

# Fit registry files and their scopes
FIT_FILES = [
    ('fits_currier_a.md', 'A'),
    ('fits_currier_b.md', 'B'),
    ('fits_azc.md', 'AZC'),
    ('fits_ht.md', 'HT'),
    ('fits_global.md', 'GLOBAL'),
    ('fits_brunschwig.md', 'A'),  # Brunschwig backprop fits
]


def parse_fit_file(filepath, default_scope):
    """Parse fits from a registry file using standard format."""
    fits = []

    if not filepath.exists():
        return fits

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Standard format:
    # ### F-X-### - Title
    # **Tier:** F# | **Result:** WORD | **Supports:** C###
    pattern = r'### (F-[A-Z]+-\d+) - (.+?)\n+\*\*Tier:\*\* (F\d) \| \*\*Result:\*\* (\w+) \| \*\*Supports:\*\* ([^\n]+)'

    for match in re.finditer(pattern, content):
        fit_id = match.group(1).strip()
        title = match.group(2).strip()
        tier = match.group(3).strip()
        result = match.group(4).strip().upper()
        supports = match.group(5).strip()

        fits.append({
            'id': fit_id,
            'title': title,
            'tier': tier,
            'scope': default_scope,
            'result': result,
            'supports': supports,
            'file': f"in: {filepath.stem}"
        })

    # Brunschwig format (multi-line):
    # ## F-BRU-###: Title
    # **Tier:** F# (description)
    # **Scope:** X
    # **Result:** WORD (notes)
    # **Supports:** C###
    bru_pattern = r'## (F-BRU-\d+): (.+?)\n+\*\*Tier:\*\* (F\d)[^\n]*\n\*\*Scope:\*\* ([A-Z]+)\n\*\*Result:\*\* (\w+)[^\n]*\n\*\*Supports:\*\* ([^\n]+)'

    for match in re.finditer(bru_pattern, content):
        fit_id = match.group(1).strip()
        title = match.group(2).strip()
        tier = match.group(3).strip()
        scope = match.group(4).strip()
        result = match.group(5).strip().upper()
        supports = match.group(6).strip()

        fits.append({
            'id': fit_id,
            'title': title,
            'tier': tier,
            'scope': scope,
            'result': result,
            'supports': supports,
            'file': f"in: {filepath.stem}"
        })

    return fits


def format_table(fits):
    """Format fits as TSV."""
    lines = []
    lines.append("ID\tFIT\tTIER\tSCOPE\tRESULT\tSUPPORTS\tFILE")

    for f in fits:
        lines.append(f"{f['id']}\t{f['title']}\t{f['tier']}\t{f['scope']}\t{f['result']}\t{f['supports']}\t{f['file']}")

    return '\n'.join(lines)


def count_by_tier(fits):
    """Count fits by tier."""
    counts = {'F0': 0, 'F1': 0, 'F2': 0, 'F3': 0, 'F4': 0}
    for f in fits:
        tier = f['tier']
        if tier in counts:
            counts[tier] += 1
    return counts


def main():
    all_fits = []

    print("Parsing fit files...")
    for filename, scope in FIT_FILES:
        filepath = FITS_DIR / filename
        fits = parse_fit_file(filepath, scope)
        print(f"  {filename}: {len(fits)} fits")
        all_fits.extend(fits)

    print(f"\nTotal fits: {len(all_fits)}")

    # Count by tier
    tier_counts = count_by_tier(all_fits)
    for tier, count in tier_counts.items():
        if count > 0:
            print(f"  {tier}: {count}")

    # Generate table
    table = format_table(all_fits)

    # Header
    today = date.today().isoformat()
    header = f"""# FIT_TABLE.txt - Programmatic Fit Index
# WARNING: No entry in this file constrains the model.
# Generated: {today}
# Total: {len(all_fits)} fits
# Format: ID	FIT	TIER	SCOPE	RESULT	SUPPORTS	FILE

"""

    output = header + table

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
