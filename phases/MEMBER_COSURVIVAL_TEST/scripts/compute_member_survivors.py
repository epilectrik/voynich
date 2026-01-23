"""Compute member-level survivor sets for each A record.

STRICT INTERPRETATION (validated against C481):
For each A record:
1. Extract MIDDLEs from A record tokens
2. ONLY those MIDDLEs are legal (no AZC expansion)
3. Filter B tokens: atomic always survive, decomposable survive iff MIDDLE is in A record
4. Output surviving tokens with their class and MIDDLE

NOTE: The union-based model (AZC expands vocabulary) was WRONG.
C481 specifies ~128-dimensional discrimination space.
Strict: 95.9 dimensions (matches). Union: 463 dimensions (way off).
"""
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

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
    print("COMPUTE MEMBER-LEVEL SURVIVOR SETS")
    print("=" * 70)

    # Load class-token map from CLASS_COSURVIVAL_TEST
    map_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(map_path, 'r') as f:
        class_map = json.load(f)

    token_to_class = class_map['token_to_class']
    token_to_middle = class_map['token_to_middle']
    class_to_tokens = class_map['class_to_tokens']

    print(f"Loaded class map: {len(token_to_class)} tokens -> {len(class_to_tokens)} classes")

    # Load transcript (H track only)
    df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                     sep='\t', low_memory=False)
    df = df[df['transcriber'] == 'H']
    print(f"\nLoaded transcript: {len(df)} H-track tokens")

    # Split by system
    df_a = df[df['language'] == 'A'].copy()
    df_azc = df[df['language'].isna()].copy()

    print(f"Currier A: {len(df_a)} tokens")
    print(f"AZC: {len(df_azc)} tokens")

    # Pre-compute MIDDLEs
    df_a['middle'] = df_a['word'].apply(extract_middle)
    df_azc['middle'] = df_azc['word'].apply(extract_middle)

    # Pre-compute AZC MIDDLEs by folio (O(1) lookups)
    azc_middles_by_folio = {}
    for folio, group in df_azc.groupby('folio'):
        azc_middles_by_folio[folio] = set(group['middle'].dropna())
    print(f"AZC folios with MIDDLEs: {len(azc_middles_by_folio)}")

    # Build A records (group by folio+line)
    a_records = []
    for (folio, line), group in df_a.groupby(['folio', 'line_number']):
        middles = set(group['middle'].dropna())
        if middles:
            a_records.append({
                'folio': folio,
                'line': str(line),
                'middles': middles
            })
    print(f"A records with MIDDLEs: {len(a_records)}")

    # Get all B tokens that belong to instruction classes
    b_instruction_tokens = set(token_to_class.keys())
    print(f"B instruction tokens: {len(b_instruction_tokens)}")

    # Compute member survivor sets
    print("\n" + "-" * 70)
    print("Computing member survivor sets...")
    print("-" * 70)

    results = []

    for i, a_rec in enumerate(a_records):
        a_middles = a_rec['middles']

        # STRICT INTERPRETATION: Only A-record MIDDLEs are legal
        # (AZC provides compatibility grouping but NOT vocabulary expansion)
        legal_middles = a_middles

        # Filter B instruction tokens by legal MIDDLEs
        surviving_tokens = []
        for token in sorted(b_instruction_tokens):
            token_middle = token_to_middle.get(token)
            if token_middle is None:
                # Atomic token (no MIDDLE) - always survives
                surviving_tokens.append(token)
            elif token_middle in legal_middles:
                surviving_tokens.append(token)

        # Group surviving tokens by class
        surviving_members_by_class = defaultdict(list)
        for token in surviving_tokens:
            cls = token_to_class.get(token)
            if cls is not None:
                surviving_members_by_class[str(cls)].append(token)

        # Compute class cardinalities
        class_cardinalities = {cls: len(members) for cls, members in surviving_members_by_class.items()}

        # Store result
        result = {
            'a_record': f"{a_rec['folio']}:{a_rec['line']}",
            'a_middles': sorted(a_middles),
            'legal_middles': sorted(legal_middles),  # STRICT: same as a_middles
            'legal_middle_count': len(legal_middles),
            'surviving_tokens': surviving_tokens,
            'surviving_token_count': len(surviving_tokens),
            'surviving_members_by_class': dict(surviving_members_by_class),
            'class_cardinalities': class_cardinalities,
            'surviving_class_count': len(class_cardinalities)
        }
        results.append(result)

        if (i + 1) % 200 == 0:
            print(f"  Processed {i + 1}/{len(a_records)} A records...")

    print(f"\nProcessed {len(results)} A records")

    # Summary statistics
    print("\n" + "-" * 70)
    print("SUMMARY STATISTICS")
    print("-" * 70)

    # Token survival statistics
    token_counts = [r['surviving_token_count'] for r in results]
    print(f"Surviving tokens per A record:")
    print(f"  Min: {min(token_counts)}")
    print(f"  Max: {max(token_counts)}")
    print(f"  Mean: {sum(token_counts)/len(token_counts):.1f}")

    # Legal MIDDLE statistics
    middle_counts = [r['legal_middle_count'] for r in results]
    print(f"\nLegal MIDDLEs per A record:")
    print(f"  Min: {min(middle_counts)}")
    print(f"  Max: {max(middle_counts)}")
    print(f"  Mean: {sum(middle_counts)/len(middle_counts):.1f}")

    # Class cardinality summary
    print(f"\n--- Per-Class Survival Summary ---")
    all_class_ids = sorted(class_to_tokens.keys(), key=int)

    for cls_id in all_class_ids:
        total_members = len(class_to_tokens[cls_id])
        cardinalities = [r['class_cardinalities'].get(str(cls_id), 0) for r in results]
        mean_survivors = sum(cardinalities) / len(cardinalities)
        min_survivors = min(cardinalities)
        max_survivors = max(cardinalities)
        zero_contexts = sum(1 for c in cardinalities if c == 0)
        single_contexts = sum(1 for c in cardinalities if c == 1)

        if total_members <= 3 or mean_survivors < 2:
            print(f"Class {cls_id:>2}: {total_members} members, "
                  f"avg={mean_survivors:.1f}, min={min_survivors}, max={max_survivors}, "
                  f"zero={zero_contexts}, single={single_contexts}")

    # Save results
    output = {
        'metadata': {
            'a_record_count': len(results),
            'total_tokens': len(b_instruction_tokens),
            'total_classes': len(class_to_tokens),
            'token_survival_stats': {
                'min': min(token_counts),
                'max': max(token_counts),
                'mean': sum(token_counts)/len(token_counts)
            },
            'legal_middle_stats': {
                'min': min(middle_counts),
                'max': max(middle_counts),
                'mean': sum(middle_counts)/len(middle_counts)
            }
        },
        'records': results
    }

    output_path = PROJECT_ROOT / 'phases' / 'MEMBER_COSURVIVAL_TEST' / 'results' / 'member_survivors.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == '__main__':
    main()
