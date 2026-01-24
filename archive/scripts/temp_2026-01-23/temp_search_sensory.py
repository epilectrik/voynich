#!/usr/bin/env python3
"""Search German source text for sensory monitoring patterns."""

import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read source text
with open('sources/brunschwig_1500_text.txt', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Sensory monitoring patterns to search for
patterns = [
    # "Until" patterns (indicates monitoring for state change)
    (r'bis es.*(?:klar|trüb|dick|dünn|farb|siede|wall)', 'UNTIL-STATE'),
    (r'bis.*(?:erkenn|sieh|riech|fühl|schmeck)', 'UNTIL-SENSE'),

    # Color observation
    (r'(?:so|wenn|wan).*farb.*(?:wird|werd|geworden)', 'COLOR-CHANGE'),
    (r'(?:erkenn|sieh|merk).*(?:farb|klar|trüb)', 'COLOR-OBSERVE'),

    # Smell observation
    (r'(?:riech|geruch).*(?:erkenn|merk|zeich)', 'SMELL-OBSERVE'),
    (r'(?:so|wenn).*(?:riech|geruch|dunst|dampf)', 'SMELL-CHANGE'),

    # Sound observation (boiling)
    (r'(?:so|wenn|wan).*(?:sied|wall|brodel)', 'SOUND-BOIL'),

    # Temperature/touch
    (r'(?:warm|kalt|heiß).*(?:werd|wird|geworden)', 'TEMP-CHANGE'),
    (r'(?:fühl|temperatur|grad)', 'TOUCH-SENSE'),

    # Consistency
    (r'(?:dick|dünn|weich|hart).*(?:werd|wird)', 'CONSISTENCY-CHANGE'),

    # General "watch for" patterns
    (r'(?:acht hab|acht geb|merck|erkenn).*(?:zeich|farb|geruch)', 'WATCH-FOR'),
]

print("\n=== Searching for sensory monitoring patterns ===\n")

for pattern, name in patterns:
    print(f"\n--- Pattern: {name} ({pattern}) ---")
    found = 0
    for i, line in enumerate(lines, 1):
        if re.search(pattern, line.lower()):
            # Show context
            context_start = max(0, i-2)
            context_end = min(len(lines), i+2)
            print(f"\nLine {i}:")
            for j in range(context_start, context_end):
                marker = ">>>" if j == i-1 else "   "
                print(f"  {marker} {j+1}: {lines[j].strip()[:100]}")
            found += 1
            if found >= 5:  # Limit results
                print(f"  ... (showing first 5 of potentially more matches)")
                break
    if found == 0:
        print("  No matches found")

# Also search for specific terms
print("\n\n=== Simple term frequency ===")
terms = ['bis es', 'erkenn', 'zeich', 'merk', 'farb', 'riech', 'geruch',
         'sied', 'wall', 'warm', 'kalt', 'heiß', 'dick', 'dünn', 'klar', 'trüb']

full_text = ''.join(lines).lower()
for term in terms:
    count = len(re.findall(term, full_text))
    print(f"  '{term}': {count} occurrences")
