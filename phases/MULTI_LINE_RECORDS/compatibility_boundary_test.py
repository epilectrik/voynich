"""
Test whether Currier A records span multiple lines.
Boundary = compatibility collapse (no AZC folio can host all accumulated tokens).

Key principle (C442, C473): Record continues as long as there EXISTS
at least one AZC folio where ALL accumulated tokens can coexist.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.azc_folio_animator.core.folio_loader import FolioLoader
from apps.azc_folio_animator.core.azc_folio_model import AZCFolioRegistry

# Infrastructure tokens that don't constrain (per C407, C422)
DA_TOKENS = {'daiin', 'dar', 'dal', 'dain', 'aiin'}


def count_compatible_folios(tokens, registry):
    """
    Count AZC folios where ALL tokens can coexist.
    Returns (count, compatible_folio_ids).
    """
    if not tokens:
        all_ids = registry.get_all_folio_ids()
        return len(all_ids), set(all_ids)

    # Get folio sets for each token (only AZC-visible tokens)
    token_folios = []
    for token_text in tokens:
        folios = {f.folio_id for f in registry.get_activated_folios(token_text)}
        if folios:  # Only include tokens with AZC presence
            token_folios.append(folios)

    if not token_folios:
        # No AZC-visible tokens yet - all folios still compatible
        all_ids = registry.get_all_folio_ids()
        return len(all_ids), set(all_ids)

    # Compatibility = intersection of all folio sets
    compatible = set.intersection(*token_folios)
    return len(compatible), compatible


def analyze_folio(folio_data, registry):
    """
    Analyze compatibility persistence across lines.
    Track when compatibility collapses (count -> 0).
    """
    records = []
    current_record = {
        'start_line': 0,
        'tokens': [],
        'lines': [],
        'compat_history': []
    }

    for line_num, line_tokens in enumerate(folio_data.lines):
        line_token_texts = [t.text for t in line_tokens]

        # Add this line's tokens to accumulator
        new_tokens = current_record['tokens'] + line_token_texts
        compat_count, compat_folios = count_compatible_folios(new_tokens, registry)

        # Check for compatibility collapse
        if compat_count == 0 and current_record['tokens']:
            # BOUNDARY: Save current record, start new one
            records.append({
                'start_line': current_record['start_line'],
                'end_line': line_num - 1,
                'length': line_num - current_record['start_line'],
                'token_count': len(current_record['tokens']),
                'final_compat': current_record['compat_history'][-1] if current_record['compat_history'] else 0,
                'lines': current_record['lines']
            })

            # Start new record with THIS line
            current_record = {
                'start_line': line_num,
                'tokens': line_token_texts,
                'lines': [line_num],
                'compat_history': []
            }
            compat_count, compat_folios = count_compatible_folios(line_token_texts, registry)
        else:
            # Continue current record
            current_record['tokens'] = new_tokens
            current_record['lines'].append(line_num)

        current_record['compat_history'].append(compat_count)

    # Don't forget last record
    if current_record['tokens']:
        records.append({
            'start_line': current_record['start_line'],
            'end_line': len(folio_data.lines) - 1,
            'length': len(folio_data.lines) - current_record['start_line'],
            'token_count': len(current_record['tokens']),
            'final_compat': current_record['compat_history'][-1] if current_record['compat_history'] else 0,
            'lines': current_record['lines']
        })

    return records


def count_structural_compatible_folios(tokens, registry, min_folio_count=5):
    """
    Count AZC folios where all STRUCTURAL tokens can coexist.
    Structural = appears in min_folio_count+ AZC folios.
    """
    if not tokens:
        all_ids = registry.get_all_folio_ids()
        return len(all_ids), set(all_ids), 0

    # Get folio sets for each STRUCTURAL token
    token_folios = []
    structural_count = 0
    for token_text in tokens:
        folios = {f.folio_id for f in registry.get_activated_folios(token_text)}
        if len(folios) >= min_folio_count:  # Only structural tokens
            token_folios.append(folios)
            structural_count += 1

    if not token_folios:
        # No structural tokens - all folios compatible
        all_ids = registry.get_all_folio_ids()
        return len(all_ids), set(all_ids), structural_count

    compatible = set.intersection(*token_folios)
    return len(compatible), compatible, structural_count


def analyze_folio_structural(folio_data, registry):
    """
    Analyze compatibility using ONLY structural tokens (5+ AZC folios).
    """
    records = []
    current_record = {
        'start_line': 0,
        'tokens': [],
        'lines': [],
        'compat_history': []
    }

    for line_num, line_tokens in enumerate(folio_data.lines):
        line_token_texts = [t.text for t in line_tokens]

        new_tokens = current_record['tokens'] + line_token_texts
        compat_count, compat_folios, structural_count = count_structural_compatible_folios(
            new_tokens, registry
        )

        if compat_count == 0 and current_record['tokens']:
            # BOUNDARY
            records.append({
                'start_line': current_record['start_line'],
                'end_line': line_num - 1,
                'length': line_num - current_record['start_line'],
                'token_count': len(current_record['tokens']),
                'final_compat': current_record['compat_history'][-1] if current_record['compat_history'] else 0,
                'lines': current_record['lines']
            })

            current_record = {
                'start_line': line_num,
                'tokens': line_token_texts,
                'lines': [line_num],
                'compat_history': []
            }
            compat_count, _, _ = count_structural_compatible_folios(line_token_texts, registry)
        else:
            current_record['tokens'] = new_tokens
            current_record['lines'].append(line_num)

        current_record['compat_history'].append(compat_count)

    if current_record['tokens']:
        records.append({
            'start_line': current_record['start_line'],
            'end_line': len(folio_data.lines) - 1,
            'length': len(folio_data.lines) - current_record['start_line'],
            'token_count': len(current_record['tokens']),
            'final_compat': current_record['compat_history'][-1] if current_record['compat_history'] else 0,
            'lines': current_record['lines']
        })

    return records


def main():
    test_folios = ['1r', '2r', '3r', '4r', '5r']

    loader = FolioLoader()
    loader.load()
    registry = AZCFolioRegistry(loader)

    print("=" * 60)
    print("TEST 1: ALL AZC-visible tokens")
    print("=" * 60)

    all_record_lengths = []

    for folio_id in test_folios:
        folio = loader.get_folio(folio_id)
        if not folio:
            continue

        print(f"\n=== Folio f{folio_id} ===")
        records = analyze_folio(folio, registry)

        lengths = [r['length'] for r in records]
        all_record_lengths.extend(lengths)

        print(f"  Total lines: {len(folio.lines)}")
        print(f"  Records found: {len(records)}")
        print(f"  Record lengths: {lengths}")
        print(f"  Mean length: {sum(lengths)/len(lengths) if lengths else 0:.2f}")

    print(f"\n=== SUMMARY (All tokens) ===")
    print(f"Total records: {len(all_record_lengths)}")
    print(f"Mean record length: {sum(all_record_lengths)/len(all_record_lengths):.2f} lines")

    print("\n" + "=" * 60)
    print("TEST 2: STRUCTURAL tokens only (5+ AZC folios)")
    print("=" * 60)

    structural_record_lengths = []

    for folio_id in test_folios:
        folio = loader.get_folio(folio_id)
        if not folio:
            continue

        print(f"\n=== Folio f{folio_id} ===")
        records = analyze_folio_structural(folio, registry)

        lengths = [r['length'] for r in records]
        structural_record_lengths.extend(lengths)

        print(f"  Total lines: {len(folio.lines)}")
        print(f"  Records found: {len(records)}")
        print(f"  Record lengths: {lengths}")
        print(f"  Mean length: {sum(lengths)/len(lengths) if lengths else 0:.2f}")

        for i, r in enumerate(records[:5]):
            print(f"  Record {i+1}: lines {r['start_line']}-{r['end_line']} "
                  f"({r['length']} lines, {r['token_count']} tokens, "
                  f"final compat={r['final_compat']})")

    print(f"\n=== SUMMARY (Structural only) ===")
    print(f"Total records: {len(structural_record_lengths)}")
    mean_struct = sum(structural_record_lengths)/len(structural_record_lengths) if structural_record_lengths else 0
    print(f"Mean record length: {mean_struct:.2f} lines")
    print(f"Length distribution: {sorted(set(structural_record_lengths))}")

    # Final interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    mean_all = sum(all_record_lengths)/len(all_record_lengths)
    print(f"All tokens mean: {mean_all:.2f} -> {'single-line' if mean_all < 1.5 else 'multi-line'}")
    print(f"Structural mean: {mean_struct:.2f} -> {'single-line' if mean_struct < 1.5 else 'multi-line'}")

    if mean_struct > mean_all * 1.5:
        print("\nKEY FINDING: Structural tokens allow longer records!")
        print("Specialized tokens are causing premature compatibility collapse.")


if __name__ == '__main__':
    main()
