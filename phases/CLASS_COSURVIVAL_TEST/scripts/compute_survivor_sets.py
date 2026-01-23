"""Compute survivor sets for each A record.

For each A record (folio, line):
1. Extract MIDDLEs from A record tokens
2. Find AZC folios containing those MIDDLEs
3. Aggregate legal MIDDLEs from matched AZC folios
4. Filter B vocabulary to tokens with legal MIDDLEs
5. Map surviving tokens to their classes
"""
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Morphology extraction (same as build_class_token_map.py)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['daiin', 'aiin', 'ain', 'iin', 'in', 'an', 'y', 'l', 'r', 'm', 'n', 'dy', 'ey', 'ol', 'or', 'ar', 'al']
ALL_SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)


def extract_middle(token):
    """Extract MIDDLE component from token."""
    if pd.isna(token):
        return None
    token = str(token)
    if not token.strip():
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
    print("COMPUTE SURVIVOR SETS PER A RECORD")
    print("=" * 70)

    # Load class-token map
    map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(map_path, 'r') as f:
        class_map = json.load(f)

    token_to_class = class_map['token_to_class']
    token_to_middle = class_map['token_to_middle']
    atomic_classes = set(class_map['atomic_classes'])
    infrastructure_classes = set(class_map['infrastructure_classes'])

    print(f"Loaded class map: {len(token_to_class)} tokens -> {len(class_map['class_to_tokens'])} classes")
    print(f"Atomic classes (always survive): {sorted(atomic_classes)}")
    print(f"Infrastructure classes: {sorted(infrastructure_classes)}")

    # Load transcript (H track only)
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    print(f"\nLoaded transcript: {len(df)} H-track tokens")

    # Split by system
    df_a = df[df['language'] == 'A'].copy()
    df_b = df[df['language'] == 'B'].copy()
    df_azc = df[df['language'].isna()].copy()

    print(f"Currier A: {len(df_a)} tokens")
    print(f"Currier B: {len(df_b)} tokens")
    print(f"AZC: {len(df_azc)} tokens")

    # Pre-compute MIDDLEs
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_azc['middle'] = df_azc['word'].apply(extract_middle)

    # Pre-compute AZC MIDDLEs by folio (O(1) lookups)
    azc_middles_by_folio = {}
    for folio, group in df_azc.groupby('folio'):
        azc_middles_by_folio[folio] = set(group['middle'].dropna())
    print(f"\nAZC folios with MIDDLEs: {len(azc_middles_by_folio)}")

    # Build A records (group by folio+line)
    a_records = []
    for (folio, line), group in df_a.groupby(['folio', 'line_number']):
        middles = set(group['middle'].dropna())
        if middles:  # Skip empty records
            a_records.append({
                'folio': folio,
                'line': str(line),
                'middles': middles
            })
    print(f"A records with MIDDLEs: {len(a_records)}")

    # Get all B tokens that belong to instruction classes
    b_instruction_tokens = set(token_to_class.keys())
    print(f"B instruction tokens: {len(b_instruction_tokens)}")

    # Compute survivor sets
    print("\n" + "-" * 70)
    print("Computing survivor sets...")
    print("-" * 70)

    results = []
    collision_check = {}  # To verify C481 (unique survivor sets)

    for i, a_rec in enumerate(a_records):
        a_middles = a_rec['middles']

        # Find AZC folios containing any of these MIDDLEs
        matching_azc_folios = []
        for azc_folio, azc_mids in azc_middles_by_folio.items():
            if a_middles & azc_mids:  # Any overlap
                matching_azc_folios.append(azc_folio)

        # Aggregate legal MIDDLEs from all matching AZC folios
        legal_middles = set()
        for azc_folio in matching_azc_folios:
            legal_middles |= azc_middles_by_folio[azc_folio]

        # Filter B instruction tokens by legal MIDDLEs
        surviving_tokens = set()
        for token in b_instruction_tokens:
            token_middle = token_to_middle.get(token)
            if token_middle is None:
                # Atomic token (no MIDDLE) - always survives
                surviving_tokens.add(token)
            elif token_middle in legal_middles:
                surviving_tokens.add(token)

        # Map surviving tokens to classes
        surviving_classes = set()
        for token in surviving_tokens:
            cls = token_to_class.get(token)
            if cls is not None:
                surviving_classes.add(cls)

        # Add atomic classes (always survive)
        surviving_classes |= atomic_classes

        # Store result
        result = {
            'a_record': f"{a_rec['folio']}:{a_rec['line']}",
            'a_middles': list(a_middles),
            'matching_azc_folios': matching_azc_folios,
            'legal_middle_count': len(legal_middles),
            'surviving_token_count': len(surviving_tokens),
            'surviving_classes': sorted(surviving_classes),
            'surviving_class_count': len(surviving_classes)
        }
        results.append(result)

        # Check for collisions (C481 verification)
        survivor_key = frozenset(surviving_classes)
        if survivor_key in collision_check:
            print(f"  COLLISION: {a_rec['folio']}:{a_rec['line']} matches {collision_check[survivor_key]}")
        else:
            collision_check[survivor_key] = f"{a_rec['folio']}:{a_rec['line']}"

        if (i + 1) % 200 == 0:
            print(f"  Processed {i + 1}/{len(a_records)} A records...")

    print(f"\nProcessed {len(results)} A records")
    print(f"Unique survivor sets: {len(collision_check)}")
    if len(collision_check) < len(results):
        print(f"WARNING: {len(results) - len(collision_check)} collisions detected!")
    else:
        print("No collisions - each A record produces unique survivor set (C481 verified)")

    # Summary statistics
    class_counts = defaultdict(int)
    for r in results:
        for cls in r['surviving_classes']:
            class_counts[cls] += 1

    print("\n" + "-" * 70)
    print("CLASS SURVIVAL RATES")
    print("-" * 70)
    print(f"{'Class':>6} {'Survives':>10} {'Rate':>10} {'Note':>20}")
    print("-" * 50)
    for cls in sorted(class_counts.keys()):
        count = class_counts[cls]
        rate = count / len(results) * 100
        note = ""
        if cls in atomic_classes:
            note = "ATOMIC"
        elif cls in infrastructure_classes:
            note = "INFRASTRUCTURE"
        print(f"{cls:>6} {count:>10} {rate:>9.1f}% {note:>20}")

    # Find classes that never survive
    all_classes = set(class_map['class_to_tokens'].keys())
    never_survive = all_classes - set(class_counts.keys())
    if never_survive:
        print(f"\nClasses that NEVER survive: {sorted(never_survive)}")

    # Save results
    output = {
        'a_record_count': len(results),
        'unique_survivor_sets': len(collision_check),
        'c481_verified': len(collision_check) == len(results),
        'class_survival_rates': {str(k): v / len(results) for k, v in class_counts.items()},
        'atomic_classes': list(atomic_classes),
        'infrastructure_classes': list(infrastructure_classes),
        'records': results
    }

    output_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'a_record_survivors.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
