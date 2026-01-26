#!/usr/bin/env python3
"""
MIDDLE CLASS PREPARATION v2 - CORRECTED METHODOLOGY

Previous version (v1) had a critical flaw: it REQUIRED PREFIX to extract MIDDLE.
This excluded ~40% of RI tokens (C509.a shows only 58.5% of RI has PREFIX).

v2 FIXES:
1. PREFIX is OPTIONAL - tokens without prefix are still processed
2. SUFFIX is STRIPPED - to get true MIDDLE cores, not MIDDLE+SUFFIX variants
3. RI = A-exclusive MIDDLEs (definition unchanged)
4. PP = Shared A&B MIDDLEs (definition unchanged)

METHODOLOGY DOCUMENTATION:
- For each token, try to strip PREFIX (longest match, optional)
- Then strip SUFFIX (longest match, if present and leaves residue)
- What remains is the MIDDLE core
- RI = MIDDLE cores that appear in Currier A but NEVER in Currier B
- PP = MIDDLE cores that appear in BOTH Currier A and Currier B
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
OUTPUT_PATH = Path(__file__).parent.parent / 'results' / 'middle_classes.json'
BACKUP_PATH = Path(__file__).parent.parent / 'results' / 'middle_classes_v1_backup.json'

# ============================================================
# MORPHOLOGICAL INVENTORY
# ============================================================

# Core prefixes from C235
CORE_PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']

# Extended prefixes (compound forms observed in corpus)
EXTENDED_PREFIXES = [
    # Compound ch-forms
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch', 'lch',
    # Compound k-forms
    'lk', 'yk',
    # Compound sh-forms
    'lsh',
    # Gallows + vowel patterns
    'ke', 'te', 'se', 'de', 'pe',
    'ko', 'to', 'so', 'do', 'po',
    'ka', 'ta', 'sa',
    # Bench forms
    'al', 'ar', 'or',
]

ALL_PREFIXES = sorted(set(CORE_PREFIXES + EXTENDED_PREFIXES), key=len, reverse=True)

# Suffixes (grammatical endings)
SUFFIXES = [
    # Long compound suffixes
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'tedy', 'kedy',
    'cheey', 'sheey', 'chey', 'shey',
    'chol', 'shol', 'chor', 'shor',
    'eedy', 'edy', 'eey',
    # Medium suffixes
    'iin', 'ain', 'oin', 'ein',
    'dy', 'ey', 'chy', 'shy', 'ky', 'ty', 'hy', 'ly', 'ry',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'in', 'an', 'on', 'en',
    # Short suffixes
    'y', 'l', 'r', 'm', 'n', 's',
]
SUFFIXES = sorted(set(SUFFIXES), key=len, reverse=True)


def extract_components(token):
    """
    Extract (prefix, middle, suffix) from a token.

    KEY DIFFERENCE FROM v1: PREFIX is OPTIONAL.
    Tokens without recognized prefix still get their MIDDLE extracted.

    Returns dict with all components, or None if no valid MIDDLE.
    """
    if not token or len(token) == 0:
        return None

    original = token
    working = token
    prefix = None
    suffix = None

    # Try to strip PREFIX (OPTIONAL - longest match first)
    for p in ALL_PREFIXES:
        if working.startswith(p) and len(working) > len(p):
            prefix = p
            working = working[len(p):]
            break

    # Strip SUFFIX if present (must leave something)
    for s in SUFFIXES:
        if working.endswith(s) and len(working) > len(s):
            suffix = s
            working = working[:-len(s)]
            break

    # What remains is the MIDDLE core
    middle = working if len(working) > 0 else None

    if middle is None:
        return None

    return {
        'original': original,
        'prefix': prefix,
        'middle': middle,
        'suffix': suffix,
        'had_prefix': prefix is not None,
        'had_suffix': suffix is not None,
    }


def get_section(folio):
    """Determine section (H, P, T) from folio name."""
    if not folio:
        return 'UNKNOWN'
    f = folio.lower()
    # Pharma section
    if any(f.startswith(x) for x in ['f88', 'f89', 'f90', 'f99', 'f100', 'f101', 'f102', 'f103']):
        return 'P'
    # Text section
    if any(f.startswith(x) for x in ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f111', 'f112', 'f113', 'f114', 'f115', 'f116']):
        return 'T'
    # Default to H for Currier A folios
    return 'H'


def main():
    print("=" * 70)
    print("MIDDLE CLASS PREPARATION v2 - CORRECTED METHODOLOGY")
    print("=" * 70)
    print()
    print("KEY FIXES from v1:")
    print("  1. PREFIX is OPTIONAL (v1 required PREFIX, excluding ~40% of RI)")
    print("  2. SUFFIX is STRIPPED (v1 kept suffix, inflating type count)")
    print()

    # Backup old file if it exists
    if OUTPUT_PATH.exists():
        print(f"Backing up v1 file to {BACKUP_PATH}")
        import shutil
        shutil.copy(OUTPUT_PATH, BACKUP_PATH)

    # ================================================================
    # LOAD ALL DATA
    # ================================================================

    print("Loading transcript data...")

    a_tokens = []  # All parsed Currier A tokens
    b_middles = set()  # Unique MIDDLE cores from Currier B

    skipped = {'empty': 0, 'asterisk': 0, 'no_middle': 0}

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            # H-track only
            if row.get('transcriber', '').strip().strip('"') != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            line_num = row.get('line_number', '').strip()
            lang = row.get('language', '').strip()

            if not word:
                skipped['empty'] += 1
                continue
            if '*' in word:
                skipped['asterisk'] += 1
                continue

            parsed = extract_components(word)

            if parsed is None:
                skipped['no_middle'] += 1
                continue

            if lang == 'A':
                parsed['folio'] = folio
                parsed['line'] = line_num
                parsed['section'] = get_section(folio)
                a_tokens.append(parsed)
            elif lang == 'B':
                b_middles.add(parsed['middle'])

    print(f"  Currier A tokens: {len(a_tokens):,}")
    print(f"  Currier B unique MIDDLEs: {len(b_middles):,}")
    print(f"  Skipped: {skipped}")
    print()

    # ================================================================
    # CLASSIFY MIDDLES
    # ================================================================

    # Get unique A MIDDLEs
    a_middles = set(t['middle'] for t in a_tokens)

    # Classify: RI = A-exclusive, PP = shared
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

    # Token counts by class
    ri_token_count = sum(1 for t in a_tokens if t['middle'] in ri_middles)
    pp_token_count = sum(1 for t in a_tokens if t['middle'] in pp_middles)

    print(f"  RI token instances: {ri_token_count:,} ({100*ri_token_count/len(a_tokens):.1f}%)")
    print(f"  PP token instances: {pp_token_count:,} ({100*pp_token_count/len(a_tokens):.1f}%)")
    print()

    # PREFIX presence rates (for validation against C509.a)
    ri_tokens = [t for t in a_tokens if t['middle'] in ri_middles]
    pp_tokens = [t for t in a_tokens if t['middle'] in pp_middles]

    ri_with_prefix = sum(1 for t in ri_tokens if t['had_prefix'])
    pp_with_prefix = sum(1 for t in pp_tokens if t['had_prefix'])

    ri_prefix_rate = 100 * ri_with_prefix / len(ri_tokens) if ri_tokens else 0
    pp_prefix_rate = 100 * pp_with_prefix / len(pp_tokens) if pp_tokens else 0

    print("  PREFIX presence (token-level):")
    print(f"    RI: {ri_prefix_rate:.1f}% (C509.a expected: 58.5%)")
    print(f"    PP: {pp_prefix_rate:.1f}% (C509.a expected: 85.4%)")
    print()

    # MIDDLE length statistics
    ri_lengths = [len(m) for m in ri_middles]
    pp_lengths = [len(m) for m in pp_middles]

    ri_mean_len = sum(ri_lengths) / len(ri_lengths) if ri_lengths else 0
    pp_mean_len = sum(pp_lengths) / len(pp_lengths) if pp_lengths else 0

    print("  MIDDLE length (type-level):")
    print(f"    RI mean: {ri_mean_len:.2f} chars (C509.a expected: 3.96)")
    print(f"    PP mean: {pp_mean_len:.2f} chars (C509.a expected: 1.46)")
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
    print(f"    RI avg folios: {ri_avg_folios:.2f} (C498 expected: 1.34)")
    print(f"    PP avg folios: {pp_avg_folios:.2f} (C498 expected: 7.96)")
    print()

    # MIDDLE frequencies
    middle_freq = Counter(t['middle'] for t in a_tokens)

    # ================================================================
    # BUILD ENTRY-LEVEL DATA
    # ================================================================

    entries = defaultdict(list)
    for t in a_tokens:
        key = (t['folio'], t['line'])
        entries[key].append(t)

    entry_stats = []
    for (folio, line), tokens in entries.items():
        middles = [t['middle'] for t in tokens]
        ri_count = sum(1 for m in middles if m in ri_middles)
        pp_count = sum(1 for m in middles if m in pp_middles)

        if ri_count > 0 and pp_count == 0:
            composition = 'PURE_RI'
        elif pp_count > 0 and ri_count == 0:
            composition = 'PURE_PP'
        else:
            composition = 'MIXED'

        entry_stats.append({
            'folio': folio,
            'line': line,
            'section': tokens[0]['section'],
            'n_tokens': len(tokens),
            'n_ri': ri_count,
            'n_pp': pp_count,
            'composition': composition,
        })

    comp_counts = Counter(e['composition'] for e in entry_stats)

    print(f"  Entry composition (n={len(entry_stats)}):")
    for comp, count in comp_counts.most_common():
        print(f"    {comp}: {count} ({100*count/len(entry_stats):.1f}%)")
    print()

    # ================================================================
    # PREPARE OUTPUT
    # ================================================================

    output = {
        'version': '2.0',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'methodology': {
            'description': 'MIDDLE extraction with optional PREFIX, stripped SUFFIX',
            'prefix_handling': 'OPTIONAL - tokens without prefix are included',
            'suffix_handling': 'STRIPPED - to get true MIDDLE cores',
            'ri_definition': 'A-exclusive: MIDDLE appears in Currier A but not Currier B',
            'pp_definition': 'Shared: MIDDLE appears in both Currier A and Currier B',
            'prefix_inventory_size': len(ALL_PREFIXES),
            'suffix_inventory_size': len(SUFFIXES),
            'changes_from_v1': [
                'PREFIX no longer required (was excluding ~40% of RI)',
                'SUFFIX now stripped (was inflating type count with variants)',
            ],
        },
        'summary': {
            'a_total_middles': len(a_middles),
            'ri_count': len(ri_middles),
            'pp_count': len(pp_middles),
            'ri_pct': round(100 * len(ri_middles) / len(a_middles), 1),
            'ri_token_instances': ri_token_count,
            'pp_token_instances': pp_token_count,
            'total_entries': len(entry_stats),
            'entry_composition': dict(comp_counts),
        },
        'validation': {
            'ri_prefix_rate': round(ri_prefix_rate, 1),
            'ri_prefix_rate_expected': 58.5,
            'pp_prefix_rate': round(pp_prefix_rate, 1),
            'pp_prefix_rate_expected': 85.4,
            'ri_mean_length': round(ri_mean_len, 2),
            'ri_mean_length_expected': 3.96,
            'pp_mean_length': round(pp_mean_len, 2),
            'pp_mean_length_expected': 1.46,
            'ri_avg_folios': round(ri_avg_folios, 2),
            'ri_avg_folios_expected': 1.34,
            'pp_avg_folios': round(pp_avg_folios, 2),
            'pp_avg_folios_expected': 7.96,
        },
        'a_exclusive_middles': sorted(ri_middles),
        'a_shared_middles': sorted(pp_middles),
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
    print(f"  v1 backup: {BACKUP_PATH}")
    print()

    print("=" * 70)
    print("COMPARISON WITH v1")
    print("=" * 70)
    print(f"  v1 RI count: 349 (PREFIX required, SUFFIX kept)")
    print(f"  v2 RI count: {len(ri_middles)} (PREFIX optional, SUFFIX stripped)")
    print(f"  Change: {len(ri_middles) - 349:+d} ({100*(len(ri_middles)-349)/349:+.1f}%)")
    print()
    print(f"  v1 PP count: 268")
    print(f"  v2 PP count: {len(pp_middles)}")
    print(f"  Change: {len(pp_middles) - 268:+d} ({100*(len(pp_middles)-268)/268:+.1f}%)")


if __name__ == '__main__':
    main()
