#!/usr/bin/env python
"""
Batch fix exploration phase scripts to add H transcriber filter.

This script:
1. Identifies scripts that load interlinear_full_words.txt
2. Adds H filter to data loading functions
3. Reports what was changed
"""
import os
import re
from pathlib import Path

EXPLORATION_DIR = Path('C:/git/voynich/phases/exploration')

# Scripts that already have the H filter - don't modify
ALREADY_FIXED = {
    'azc_topology_test.py',
    'c412_verification.py',
    'ht_training_final.py',
    'ht_d_deep_dive.py',
}

# Pattern to find transcript loading
TRANSCRIPT_PATTERN = re.compile(r'interlinear_full_words')

# Pattern to find language filtering (where we add H filter after)
LANGUAGE_FILTER_PATTERNS = [
    # Pattern: if language != 'A': continue  or  if language == 'A':
    (r"(if\s+language\s*[!=]=\s*['\"](?:A|B|NA)['\"])",
     r"\1\n                # Filter to PRIMARY transcriber (H) only\n                transcriber = parts[12].strip('\"').strip() if len(parts) > 12 else ''\n                if transcriber != 'H':\n                    continue"),

    # Pattern: language = parts[6] followed by continue check
    (r"(language\s*=\s*parts\[6\][^\n]+\n)(\s*)(if\s+language)",
     r"\1\2transcriber = parts[12].strip('\"').strip() if len(parts) > 12 else ''\n\2if transcriber != 'H':\n\2    continue\n\2\3"),
]

# For pandas-style loading
PANDAS_PATTERN = re.compile(r"(df\s*=\s*pd\.read_csv[^\n]+)")
PANDAS_FIX = r"\1\n    df = df[df['transcriber'] == 'H']  # PRIMARY track only"


def needs_fixing(filepath):
    """Check if file needs H filter added."""
    if filepath.name in ALREADY_FIXED:
        return False

    content = filepath.read_text(encoding='utf-8')

    # Must load transcript
    if not TRANSCRIPT_PATTERN.search(content):
        return False

    # Must NOT already have H filter
    if "transcriber" in content and ("== 'H'" in content or '== "H"' in content):
        return False

    return True


def fix_file(filepath):
    """Add H filter to a file. Returns (was_modified, description)."""
    content = filepath.read_text(encoding='utf-8')
    original = content

    # Try pandas pattern first
    if 'pd.read_csv' in content and "df['transcriber']" not in content:
        content = PANDAS_PATTERN.sub(PANDAS_FIX, content)

    # Try manual reading patterns
    # Look for the common pattern: after reading parts, filter by language
    # Add transcriber filter right after language filter

    # Pattern 1: Look for "if language" checks and add transcriber check
    if "if language" in content and "transcriber" not in content:
        # Find where language is extracted and add transcriber extraction nearby
        # This is a heuristic - add after language extraction
        lines = content.split('\n')
        new_lines = []
        added = False

        for i, line in enumerate(lines):
            new_lines.append(line)

            # After language assignment, add transcriber assignment
            if not added and 'language = parts[6]' in line:
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                new_lines.append(f"{spaces}transcriber = parts[12].strip('\"').strip() if len(parts) > 12 else ''")
                added = True

            # After language filter, add transcriber filter
            elif not added and re.search(r"if language\s*[!=]=\s*['\"]", line):
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                # Check if this is a continue-style filter
                if 'continue' in line or (i + 1 < len(lines) and 'continue' in lines[i+1]):
                    # Add after the continue
                    pass
                else:
                    # Add transcriber filter
                    new_lines.append(f"{spaces}# Filter to PRIMARY transcriber (H) only")
                    new_lines.append(f"{spaces}transcriber = parts[12].strip('\"').strip() if len(parts) > 12 else ''")
                    new_lines.append(f"{spaces}if transcriber != 'H':")
                    new_lines.append(f"{spaces}    continue")
                    added = True

        if added:
            content = '\n'.join(new_lines)

    if content != original:
        filepath.write_text(content, encoding='utf-8')
        return True, "Added H filter"

    return False, "No changes needed or pattern not recognized"


def main():
    print("Scanning exploration phase scripts...\n")

    py_files = list(EXPLORATION_DIR.glob('*.py'))
    print(f"Found {len(py_files)} Python files\n")

    needs_fix = []
    already_ok = []

    for f in py_files:
        if f.name in ALREADY_FIXED:
            already_ok.append(f.name)
        elif needs_fixing(f):
            needs_fix.append(f)
        else:
            # Check if it loads transcript at all
            content = f.read_text(encoding='utf-8')
            if TRANSCRIPT_PATTERN.search(content):
                if 'transcriber' in content:
                    already_ok.append(f.name)
                else:
                    needs_fix.append(f)

    print(f"Already have H filter: {len(already_ok)}")
    print(f"Need fixing: {len(needs_fix)}\n")

    if needs_fix:
        print("Files needing H filter:")
        for f in sorted(needs_fix, key=lambda x: x.name):
            print(f"  - {f.name}")

    return needs_fix


if __name__ == '__main__':
    files_to_fix = main()
    print(f"\n{len(files_to_fix)} files identified for fixing")
