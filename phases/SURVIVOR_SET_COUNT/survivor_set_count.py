#!/usr/bin/env python3
"""
Survivor-Set Count Test

Question: How many distinct survivor-sets does Currier A produce when quotiented by AZC compatibility?

Expert claim: "~80ish distinct survivor-set bundles once phase legality and hub rationing are enforced"

Method:
1. Extract all A lines with their MIDDLE sets
2. For each A line, identify which AZC folios it's compatible with (via shared MIDDLEs)
3. Group A lines by their AZC compatibility profile
4. Count the resulting equivalence classes

This tests whether |A/AZC| ≈ 83
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "survivor_set_count.json"

# PREFIX and SUFFIX for parsing
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]


def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return None, None, None
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    prefix = None
    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    if not middle:
        middle = None

    return prefix, middle, suffix


def load_data():
    """Load and organize data by system (A, B, AZC) and by line."""
    a_lines = defaultdict(lambda: defaultdict(list))  # folio -> line -> tokens
    b_lines = defaultdict(lambda: defaultdict(list))
    azc_lines = defaultdict(lambda: defaultdict(list))

    # AZC folios (from C430)
    azc_folios = {
        'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
        'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
        'f73r', 'f73v', 'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2',
        'f67v1', 'f67v2', 'f68r1', 'f68r2', 'f68r3', 'f68v1',
        'f68v2', 'f68v3', 'f69r', 'f69v', 'f70r1', 'f70r2'
    }

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            folio = row['folio']
            lang = row['language']
            line = row['line_number']
            word = row['word'].strip('"')

            if lang == 'A':
                a_lines[folio][line].append(word)
            elif lang == 'B':
                b_lines[folio][line].append(word)
            elif folio in azc_folios:
                azc_lines[folio][line].append(word)

    return a_lines, b_lines, azc_lines, azc_folios


def extract_middles(tokens: List[str]) -> Set[str]:
    """Extract set of MIDDLEs from a list of tokens."""
    middles = set()
    for token in tokens:
        _, middle, _ = decompose_token(token)
        if middle:
            middles.add(middle)
    return middles


def main():
    print("Loading data...")
    a_lines, b_lines, azc_lines, azc_folios = load_data()

    # Step 1: Build MIDDLE inventory for each AZC folio
    print("\nBuilding AZC MIDDLE inventories...")
    azc_middle_inventory = {}
    for folio in azc_folios:
        all_middles = set()
        for line, tokens in azc_lines[folio].items():
            all_middles.update(extract_middles(tokens))
        azc_middle_inventory[folio] = all_middles
        print(f"  {folio}: {len(all_middles)} MIDDLEs")

    # Step 2: For each A line, compute its MIDDLE set and AZC compatibility profile
    print("\nAnalyzing A lines...")
    a_line_profiles = []

    for folio in sorted(a_lines.keys()):
        for line, tokens in a_lines[folio].items():
            middles = extract_middles(tokens)
            if not middles:
                continue

            # Compute AZC compatibility: which AZC folios share at least one MIDDLE?
            compatible_azc = set()
            for azc_folio, azc_middles in azc_middle_inventory.items():
                if middles & azc_middles:  # intersection
                    compatible_azc.add(azc_folio)

            # Create compatibility signature (frozenset for hashing)
            profile = frozenset(compatible_azc)

            a_line_profiles.append({
                'folio': folio,
                'line': line,
                'n_middles': len(middles),
                'middles': middles,
                'compatible_azc': compatible_azc,
                'profile': profile
            })

    print(f"Total A lines with MIDDLEs: {len(a_line_profiles)}")

    # Step 3: Group A lines by their AZC compatibility profile
    print("\nGrouping by AZC compatibility profile...")
    profile_groups = defaultdict(list)
    for entry in a_line_profiles:
        profile_groups[entry['profile']].append(entry)

    n_profiles = len(profile_groups)
    print(f"\nDistinct AZC compatibility profiles: {n_profiles}")

    # Step 4: Analyze profile distribution
    profile_sizes = [len(v) for v in profile_groups.values()]

    print(f"\nProfile size distribution:")
    print(f"  Min: {min(profile_sizes)}")
    print(f"  Max: {max(profile_sizes)}")
    print(f"  Mean: {sum(profile_sizes)/len(profile_sizes):.1f}")

    # Count how many AZC folios each profile covers
    coverage_dist = Counter()
    for profile in profile_groups.keys():
        coverage_dist[len(profile)] += 1

    print(f"\nAZC coverage distribution (how many AZC folios per profile):")
    for n_azc in sorted(coverage_dist.keys()):
        print(f"  {n_azc} AZC folios: {coverage_dist[n_azc]} profiles")

    # Step 5: Also count B folio survivor-sets
    print("\n" + "="*60)
    print("Now analyzing B folios...")

    b_folio_profiles = []
    for folio in sorted(b_lines.keys()):
        all_middles = set()
        for line, tokens in b_lines[folio].items():
            all_middles.update(extract_middles(tokens))

        if not all_middles:
            continue

        # Compute AZC compatibility
        compatible_azc = set()
        for azc_folio, azc_middles in azc_middle_inventory.items():
            if all_middles & azc_middles:
                compatible_azc.add(azc_folio)

        profile = frozenset(compatible_azc)
        b_folio_profiles.append({
            'folio': folio,
            'n_middles': len(all_middles),
            'compatible_azc': compatible_azc,
            'profile': profile
        })

    # Group B folios by profile
    b_profile_groups = defaultdict(list)
    for entry in b_folio_profiles:
        b_profile_groups[entry['profile']].append(entry['folio'])

    n_b_profiles = len(b_profile_groups)
    print(f"Total B folios: {len(b_folio_profiles)}")
    print(f"Distinct AZC compatibility profiles for B: {n_b_profiles}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY: Survivor-Set Count Test")
    print("="*60)
    print(f"A lines analyzed: {len(a_line_profiles)}")
    print(f"A-line AZC compatibility profiles: {n_profiles}")
    print(f"B folios analyzed: {len(b_folio_profiles)}")
    print(f"B-folio AZC compatibility profiles: {n_b_profiles}")
    print(f"\nExpected if expert is correct: ~83")
    print(f"Actual A-line profiles: {n_profiles}")
    print(f"Actual B-folio profiles: {n_b_profiles}")

    if n_profiles > 100:
        verdict = "A profiles >> 83: Expert claim CHALLENGED"
    elif 70 <= n_profiles <= 100:
        verdict = "A profiles ≈ 83: Expert claim SUPPORTED"
    else:
        verdict = "A profiles << 83: Expert claim CHALLENGED"

    print(f"\nVERDICT: {verdict}")

    # Save results
    results = {
        'test': 'SURVIVOR_SET_COUNT',
        'question': 'How many distinct survivor-sets does A/AZC produce?',
        'expected': '~83 if expert claim is correct',
        'a_analysis': {
            'n_lines': len(a_line_profiles),
            'n_profiles': n_profiles,
            'profile_sizes': {
                'min': min(profile_sizes),
                'max': max(profile_sizes),
                'mean': sum(profile_sizes)/len(profile_sizes)
            },
            'azc_coverage_dist': dict(coverage_dist)
        },
        'b_analysis': {
            'n_folios': len(b_folio_profiles),
            'n_profiles': n_b_profiles
        },
        'verdict': verdict,
        'profiles_detail': [
            {
                'profile_id': i,
                'n_azc_folios': len(profile),
                'n_a_lines': len(entries),
                'sample_folios': list(set(e['folio'] for e in entries[:10]))
            }
            for i, (profile, entries) in enumerate(sorted(
                profile_groups.items(),
                key=lambda x: -len(x[1])
            )[:20])
        ]
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
