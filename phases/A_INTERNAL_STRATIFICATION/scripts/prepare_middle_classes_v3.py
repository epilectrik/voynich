#!/usr/bin/env python3
"""
MIDDLE CLASS PREPARATION v3 - USING CANONICAL LIBRARY

v2 had a critical flaw: it didn't strip articulators before extracting MIDDLE.
This caused y-initial tokens to have 'y' absorbed into the MIDDLE field.

v3 FIXES:
1. Uses voynich.py Morphology which properly handles articulators
2. TOKEN = [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX] is correctly parsed
3. MIDDLE no longer contains articulator pollution

METHODOLOGY:
- Use Morphology.extract() to get (articulator, prefix, middle, suffix)
- RI = MIDDLE cores that appear in Currier A but NEVER in Currier B
- PP = MIDDLE cores that appear in BOTH Currier A and Currier B
"""

import sys
import json
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

# Add scripts directory to path for voynich import
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from voynich import Transcript, Morphology

OUTPUT_PATH = Path(__file__).parent.parent / 'results' / 'middle_classes.json'
BACKUP_PATH = Path(__file__).parent.parent / 'results' / 'middle_classes_v2_backup.json'


def main():
    print("=" * 70)
    print("MIDDLE CLASS PREPARATION v3 - USING CANONICAL LIBRARY")
    print("=" * 70)
    print()
    print("KEY FIX from v2:")
    print("  - Uses voynich.py Morphology which properly strips articulators")
    print("  - TOKEN = [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]")
    print("  - MIDDLE no longer contains articulator pollution")
    print()

    # Backup old file if it exists
    if OUTPUT_PATH.exists():
        print(f"Backing up v2 file to {BACKUP_PATH}")
        import shutil
        shutil.copy(OUTPUT_PATH, BACKUP_PATH)

    # ================================================================
    # LOAD DATA USING CANONICAL LIBRARY
    # ================================================================

    print("Loading transcript using voynich.Transcript...")
    tx = Transcript()
    morph = Morphology(require_prefix=False)  # PREFIX is optional

    a_tokens = []  # All parsed Currier A tokens
    b_middles = set()  # Unique MIDDLE cores from Currier B

    skipped = {'empty': 0, 'asterisk': 0, 'no_middle': 0}

    # Process Currier A
    for token in tx.currier_a():
        word = token.word
        if not word:
            skipped['empty'] += 1
            continue
        if '*' in word:
            skipped['asterisk'] += 1
            continue

        parsed = morph.extract(word)
        if parsed.middle is None or parsed.middle == '':
            skipped['no_middle'] += 1
            continue

        a_tokens.append({
            'original': word,
            'articulator': parsed.articulator,
            'prefix': parsed.prefix,
            'middle': parsed.middle,
            'suffix': parsed.suffix,
            'has_articulator': parsed.has_articulator,
            'has_prefix': parsed.prefix is not None,
            'folio': token.folio,
            'line': token.line,
        })

    # Process Currier B
    for token in tx.currier_b():
        word = token.word
        if not word or '*' in word:
            continue

        parsed = morph.extract(word)
        if parsed.middle:
            b_middles.add(parsed.middle)

    print(f"  Currier A tokens: {len(a_tokens):,}")
    print(f"  Currier B unique MIDDLEs: {len(b_middles):,}")
    print(f"  Skipped: {skipped}")
    print()

    # ================================================================
    # CLASSIFY MIDDLES
    # ================================================================

    a_middles = set(t['middle'] for t in a_tokens)

    ri_middles = a_middles - b_middles
    pp_middles = a_middles & b_middles

    print("=" * 70)
    print("MIDDLE CLASSIFICATION")
    print("=" * 70)
    print(f"  Total A MIDDLEs: {len(a_middles)}")
    print(f"  RI (A-exclusive): {len(ri_middles)} ({100*len(ri_middles)/len(a_middles):.1f}%)")
    print(f"  PP (shared A&B): {len(pp_middles)} ({100*len(pp_middles)/len(a_middles):.1f}%)")
    print()

    # ================================================================
    # COMPUTE STATISTICS
    # ================================================================

    ri_token_count = sum(1 for t in a_tokens if t['middle'] in ri_middles)
    pp_token_count = sum(1 for t in a_tokens if t['middle'] in pp_middles)

    print(f"  RI token instances: {ri_token_count:,} ({100*ri_token_count/len(a_tokens):.1f}%)")
    print(f"  PP token instances: {pp_token_count:,} ({100*pp_token_count/len(a_tokens):.1f}%)")
    print()

    # Articulator rates
    ri_tokens = [t for t in a_tokens if t['middle'] in ri_middles]
    pp_tokens = [t for t in a_tokens if t['middle'] in pp_middles]

    ri_with_art = sum(1 for t in ri_tokens if t['has_articulator'])
    pp_with_art = sum(1 for t in pp_tokens if t['has_articulator'])

    ri_art_rate = 100 * ri_with_art / len(ri_tokens) if ri_tokens else 0
    pp_art_rate = 100 * pp_with_art / len(pp_tokens) if pp_tokens else 0

    print("  ARTICULATOR presence (token-level):")
    print(f"    RI: {ri_art_rate:.1f}%")
    print(f"    PP: {pp_art_rate:.1f}%")
    print()

    # PREFIX rates
    ri_with_prefix = sum(1 for t in ri_tokens if t['has_prefix'])
    pp_with_prefix = sum(1 for t in pp_tokens if t['has_prefix'])

    ri_prefix_rate = 100 * ri_with_prefix / len(ri_tokens) if ri_tokens else 0
    pp_prefix_rate = 100 * pp_with_prefix / len(pp_tokens) if pp_tokens else 0

    print("  PREFIX presence (token-level):")
    print(f"    RI: {ri_prefix_rate:.1f}%")
    print(f"    PP: {pp_prefix_rate:.1f}%")
    print()

    # MIDDLE length
    ri_lengths = [len(m) for m in ri_middles]
    pp_lengths = [len(m) for m in pp_middles]

    ri_mean_len = sum(ri_lengths) / len(ri_lengths) if ri_lengths else 0
    pp_mean_len = sum(pp_lengths) / len(pp_lengths) if pp_lengths else 0

    print("  MIDDLE length (type-level):")
    print(f"    RI mean: {ri_mean_len:.2f} chars")
    print(f"    PP mean: {pp_mean_len:.2f} chars")
    print()

    # Folio localization
    ri_folio_counts = defaultdict(set)
    pp_folio_counts = defaultdict(set)

    for t in a_tokens:
        if t['middle'] in ri_middles:
            ri_folio_counts[t['middle']].add(t['folio'])
        else:
            pp_folio_counts[t['middle']].add(t['folio'])

    ri_avg_folios = sum(len(f) for f in ri_folio_counts.values()) / len(ri_folio_counts) if ri_folio_counts else 0
    pp_avg_folios = sum(len(f) for f in pp_folio_counts.values()) / len(pp_folio_counts) if pp_folio_counts else 0

    print("  Folio localization:")
    print(f"    RI avg folios: {ri_avg_folios:.2f}")
    print(f"    PP avg folios: {pp_avg_folios:.2f}")
    print()

    # ================================================================
    # CHECK FOR Y-INITIAL CLEANUP
    # ================================================================

    print("=" * 70)
    print("ARTICULATOR CLEANUP CHECK")
    print("=" * 70)

    # Count y-initial in v2 vs v3
    v2_y_initial_ri = [m for m in ri_middles if m.startswith('y')]

    print(f"  Y-initial MIDDLEs in RI: {len(v2_y_initial_ri)}")
    if v2_y_initial_ri:
        print(f"  Examples: {v2_y_initial_ri[:10]}")
    print()

    # Show articulator distribution
    art_counter = Counter(t['articulator'] for t in a_tokens if t['has_articulator'])
    print("  Articulator distribution (when present):")
    for art, count in art_counter.most_common():
        print(f"    {art}: {count}")
    print()

    # ================================================================
    # MIDDLE FREQUENCIES
    # ================================================================

    middle_freq = Counter(t['middle'] for t in a_tokens)

    # ================================================================
    # AZC TRACKING (for C498.a)
    # ================================================================

    print("Computing AZC presence for shared MIDDLEs...")

    azc_middles = set()
    for token in tx.azc():
        word = token.word
        if not word or '*' in word:
            continue
        parsed = morph.extract(word)
        if parsed.middle:
            azc_middles.add(parsed.middle)

    shared_in_azc = pp_middles & azc_middles
    ri_in_azc = ri_middles & azc_middles

    print(f"  Shared MIDDLEs in AZC: {len(shared_in_azc)} / {len(pp_middles)} ({100*len(shared_in_azc)/len(pp_middles):.1f}%)")
    print(f"  RI MIDDLEs in AZC: {len(ri_in_azc)} / {len(ri_middles)} ({100*len(ri_in_azc)/len(ri_middles):.1f}%)")
    print()

    # ================================================================
    # PREPARE OUTPUT
    # ================================================================

    output = {
        'version': '3.0',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'methodology': {
            'description': 'MIDDLE extraction using voynich.py Morphology',
            'articulator_handling': 'STRIPPED - articulators parsed separately from MIDDLE',
            'prefix_handling': 'OPTIONAL - tokens without prefix are included',
            'suffix_handling': 'STRIPPED - to get true MIDDLE cores',
            'ri_definition': 'A-exclusive: MIDDLE appears in Currier A but not Currier B',
            'pp_definition': 'Shared: MIDDLE appears in both Currier A and Currier B',
            'changes_from_v2': [
                'Uses voynich.py Morphology instead of custom extraction',
                'Articulators now properly stripped (v2 absorbed them into MIDDLE)',
                'Y-initial MIDDLEs cleaned up',
            ],
        },
        'summary': {
            'a_exclusive_count': len(ri_middles),
            'a_shared_count': len(pp_middles),
            'b_exclusive_count': len(b_middles - a_middles),
            'a_exclusive_pct': round(100 * len(ri_middles) / len(a_middles), 1),
            'a_exclusive_token_instances': ri_token_count,
            'a_shared_token_instances': pp_token_count,
        },
        'articulator_stats': {
            'ri_articulator_rate': round(ri_art_rate, 1),
            'pp_articulator_rate': round(pp_art_rate, 1),
            'articulator_distribution': dict(art_counter),
        },
        'validation': {
            'ri_prefix_rate': round(ri_prefix_rate, 1),
            'pp_prefix_rate': round(pp_prefix_rate, 1),
            'ri_mean_length': round(ri_mean_len, 2),
            'pp_mean_length': round(pp_mean_len, 2),
            'ri_avg_folios': round(ri_avg_folios, 2),
            'pp_avg_folios': round(pp_avg_folios, 2),
        },
        'a_exclusive_middles': sorted(ri_middles),
        'a_shared_middles': sorted(pp_middles),
        'a_exclusive_in_azc': sorted(ri_in_azc),
        'a_shared_in_azc': sorted(shared_in_azc),
        'middle_frequencies': {m: middle_freq[m] for m in a_middles},
    }

    # ================================================================
    # SAVE OUTPUT
    # ================================================================

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)

    print("=" * 70)
    print("OUTPUT SAVED")
    print("=" * 70)
    print(f"  Main file: {OUTPUT_PATH}")
    print(f"  v2 backup: {BACKUP_PATH}")
    print()

    print("=" * 70)
    print("COMPARISON WITH v2")
    print("=" * 70)
    print(f"  v2 RI count: 609 (articulators absorbed into MIDDLE)")
    print(f"  v3 RI count: {len(ri_middles)} (articulators properly stripped)")
    print(f"  Change: {len(ri_middles) - 609:+d}")
    print()
    print(f"  v2 PP count: 404")
    print(f"  v3 PP count: {len(pp_middles)}")
    print(f"  Change: {len(pp_middles) - 404:+d}")


if __name__ == '__main__':
    main()
