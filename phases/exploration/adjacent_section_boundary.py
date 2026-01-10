#!/usr/bin/env python
"""
Test if adjacent similarity changes at section boundaries.

Question: Does the 1.31x adjacent similarity drop when crossing sections?
"""
import sys
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import MARKER_FAMILIES, A_UNIVERSAL_SUFFIXES, EXTENDED_PREFIX_MAP

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'


def load_entries_with_section():
    """Load entries with section information."""

    entries = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        current_entry = None

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                if language != 'A':
                    continue

                key = f"{folio}_{line_num}"

                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None and current_entry['tokens']:
                        entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': []
                    }

                current_entry['tokens'].append(word)

        if current_entry is not None and current_entry['tokens']:
            entries.append(current_entry)

    return entries


def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def main():
    print("=" * 70)
    print("SECTION BOUNDARY EFFECT ON ADJACENT SIMILARITY")
    print("=" * 70)

    entries = load_entries_with_section()
    print(f"\nLoaded {len(entries)} entries")

    # Sort entries by folio then line
    def sort_key(e):
        # Extract folio number and side
        folio = e['folio']
        line = int(e['line']) if e['line'].isdigit() else 0
        # Simple sort: try to extract number
        import re
        match = re.match(r'(\d+)', folio)
        num = int(match.group(1)) if match else 0
        side = 1 if 'v' in folio else 0
        return (num, side, line)

    entries.sort(key=sort_key)

    # Compare adjacent pairs within same section vs across sections
    same_section_sims = []
    cross_section_sims = []
    same_folio_sims = []
    cross_folio_sims = []

    for i in range(len(entries) - 1):
        e1 = entries[i]
        e2 = entries[i + 1]

        if len(e1['tokens']) < 2 or len(e2['tokens']) < 2:
            continue

        sim = jaccard(set(e1['tokens']), set(e2['tokens']))

        same_section = e1['section'] == e2['section']
        same_folio = e1['folio'] == e2['folio']

        if same_section:
            same_section_sims.append(sim)
        else:
            cross_section_sims.append(sim)

        if same_folio:
            same_folio_sims.append(sim)
        else:
            cross_folio_sims.append(sim)

    print(f"\n{'Category':<25} {'Count':<10} {'Mean J':<12} {'Std':<10}")
    print("-" * 60)

    for name, sims in [
        ('Same section', same_section_sims),
        ('Cross section', cross_section_sims),
        ('Same folio', same_folio_sims),
        ('Cross folio (adjacent)', cross_folio_sims),
    ]:
        if sims:
            print(f"{name:<25} {len(sims):<10} {np.mean(sims):<12.4f} {np.std(sims):<10.4f}")

    # Statistical tests
    print("\n" + "-" * 60)
    print("STATISTICAL TESTS")
    print("-" * 60)

    if same_section_sims and cross_section_sims:
        stat, p = stats.mannwhitneyu(same_section_sims, cross_section_sims, alternative='greater')
        ratio = np.mean(same_section_sims) / np.mean(cross_section_sims) if np.mean(cross_section_sims) > 0 else float('inf')
        print(f"\nSame section > Cross section:")
        print(f"  Ratio: {ratio:.2f}x")
        print(f"  p-value: {p:.6f}")

    if same_folio_sims and cross_folio_sims:
        stat, p = stats.mannwhitneyu(same_folio_sims, cross_folio_sims, alternative='greater')
        ratio = np.mean(same_folio_sims) / np.mean(cross_folio_sims) if np.mean(cross_folio_sims) > 0 else float('inf')
        print(f"\nSame folio > Cross folio:")
        print(f"  Ratio: {ratio:.2f}x")
        print(f"  p-value: {p:.6f}")

    # Marker distribution by section
    print("\n" + "-" * 60)
    print("MARKER DISTRIBUTION BY SECTION")
    print("-" * 60)

    section_markers = defaultdict(Counter)
    for e in entries:
        for token in e['tokens']:
            for prefix in sorted(MARKER_FAMILIES, key=len, reverse=True):
                if token.lower().startswith(prefix):
                    section_markers[e['section']][prefix] += 1
                    break

    for section in sorted(section_markers.keys()):
        markers = section_markers[section]
        total = sum(markers.values())
        print(f"\n{section}:")
        for m, c in markers.most_common(5):
            print(f"  {m}: {c} ({100*c/total:.1f}%)")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if same_section_sims and cross_section_sims:
        same_mean = np.mean(same_section_sims)
        cross_mean = np.mean(cross_section_sims)

        if same_mean > cross_mean * 1.3:
            print("\nSTRONG section boundary effect - similarity drops at section boundaries.")
        elif same_mean > cross_mean * 1.1:
            print("\nMODERATE section boundary effect.")
        else:
            print("\nWEAK or NO section boundary effect - similarity is consistent across sections.")


if __name__ == '__main__':
    main()
