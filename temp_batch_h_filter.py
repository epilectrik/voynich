#!/usr/bin/env python3
"""
Batch H-Filter Application

Systematically adds PRIMARY transcriber (H) filter to all AZC-related scripts.
Handles two main patterns:
1. csv.DictReader - add row.get('transcriber') != 'H' check
2. Manual header parsing - add transcriber column check

Run this to apply fixes, then manually verify.
"""

import os
import re
from pathlib import Path

# Target directories
AZC_DIRS = [
    'phases/AAZ_a_azc_coordination',
    'phases/AZC_AXIS_axis_connectivity',
    'phases/AZC_COMPATIBILITY',
    'phases/AZC_constraint_hunting',
    'phases/AZC_ZODIAC_INTERNAL_STRATIFICATION',
    'phases/exploration',
    'phases/INTEGRATION_PROBE',
    'phases/EFFICIENCY_REGIME_TEST',
    'phases/BRUNSCHWIG_BACKPROP_VALIDATION',
]

# Filter to only AZC-related scripts in exploration
AZC_PREFIXES = ['azc', 'aaz']

def is_azc_script(filepath):
    """Check if script is AZC-related."""
    name = Path(filepath).stem.lower()
    # Directories dedicated to AZC
    for d in ['AAZ_', 'AZC_']:
        if d in str(filepath):
            return True
    # Or starts with azc/aaz prefix
    for prefix in AZC_PREFIXES:
        if name.startswith(prefix):
            return True
    return False

def check_has_h_filter(content):
    """Check if file already has H filter."""
    patterns = [
        r"transcriber.*==.*['\"]H['\"]",
        r"transcriber.*!=.*['\"]H['\"]",
        r"\['transcriber'\].*==.*['\"]H['\"]",
        r"\.strip\(['\"]H['\"]\)",  # Checking for H string
        r"# PRIMARY.*H",
        r"# Filter to PRIMARY",
    ]
    for p in patterns:
        if re.search(p, content, re.IGNORECASE):
            return True
    return False

def check_loads_transcript(content):
    """Check if file loads the transcript."""
    patterns = [
        r"interlinear_full_words",
        r"interlinear.*\.txt",
    ]
    for p in patterns:
        if re.search(p, content):
            return True
    return False

def add_h_filter_dictreader(content):
    """Add H filter for DictReader pattern."""
    # Pattern: for row in reader:
    # After that line, add transcriber check

    # Find "for row in reader:" pattern
    pattern = r'(for\s+row\s+in\s+reader\s*:)'

    if re.search(pattern, content):
        # Add the filter right after the for loop
        replacement = r'''\1
            # Filter to PRIMARY transcriber (H) only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue'''
        content = re.sub(pattern, replacement, content)

    return content

def add_h_filter_header_parse(content):
    """Add H filter for header-based parsing pattern."""
    # Pattern: row = {header[i]: parts[i]...}
    # Or: all_tokens.append(row)

    # Look for the row creation pattern and add filter after
    patterns_to_patch = [
        # Pattern 1: row = {...} followed by append or add
        (r"(row\s*=\s*\{header\[i\].*?\})\s*\n(\s*)(all_tokens\.append\(row\))",
         r"\1\n\2# Filter to PRIMARY transcriber (H) only\n\2if row.get('transcriber', '').strip('\"') != 'H':\n\2    continue\n\2\3"),

        # Pattern 2: folio_tokens[...].append or similar
        (r"(row\s*=\s*\{header\[i\].*?\})\s*\n(\s*)(folio_tokens\[)",
         r"\1\n\2# Filter to PRIMARY transcriber (H) only\n\2if row.get('transcriber', '').strip('\"') != 'H':\n\2    continue\n\2\3"),
    ]

    for pattern, replacement in patterns_to_patch:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            return content

    return content

def patch_file(filepath):
    """Patch a single file to add H filter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Skip if already has H filter
    if check_has_h_filter(content):
        return 'SKIP_HAS_FILTER', content

    # Skip if doesn't load transcript
    if not check_loads_transcript(content):
        return 'SKIP_NO_TRANSCRIPT', content

    # Try DictReader pattern first
    if 'DictReader' in content:
        content = add_h_filter_dictreader(content)

    # Try header parse pattern
    if 'header[i]' in content and content == original:
        content = add_h_filter_header_parse(content)

    if content == original:
        return 'NO_CHANGE', content

    return 'PATCHED', content

def main():
    print("=" * 70)
    print("BATCH H-FILTER APPLICATION")
    print("=" * 70)

    os.chdir('C:/git/voynich')

    results = {
        'PATCHED': [],
        'SKIP_HAS_FILTER': [],
        'SKIP_NO_TRANSCRIPT': [],
        'NO_CHANGE': [],
        'ERROR': [],
    }

    # Collect all Python files
    all_files = []
    for d in AZC_DIRS:
        if os.path.exists(d):
            for f in Path(d).glob('*.py'):
                if is_azc_script(f) or d.startswith('phases/A'):
                    all_files.append(f)

    print(f"\nFound {len(all_files)} candidate files\n")

    for filepath in sorted(all_files):
        try:
            status, new_content = patch_file(filepath)
            results[status].append(str(filepath))

            if status == 'PATCHED':
                # Write the patched file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"[PATCHED] {filepath}")
            else:
                print(f"[{status}] {filepath}")

        except Exception as e:
            results['ERROR'].append(f"{filepath}: {e}")
            print(f"[ERROR] {filepath}: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for status, files in results.items():
        print(f"{status}: {len(files)}")

    print("\n" + "-" * 70)
    print("Files that need manual review (NO_CHANGE but load transcript):")
    for f in results['NO_CHANGE']:
        print(f"  - {f}")

if __name__ == '__main__':
    main()
