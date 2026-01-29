"""
00_build_paragraph_inventory.py - GATE SCRIPT

Builds paragraph inventories for both Currier A and B using par_initial field.
Must complete before any other scripts in this phase.

Output:
- a_paragraph_inventory.json: Skeleton A paragraphs
- b_paragraph_inventory.json: Skeleton B paragraphs

Verification:
- A: ~306 paragraphs, 11,415 tokens total
- B: ~585 paragraphs, 23,243 tokens total
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript

def build_inventory(system: str):
    """Build paragraph inventory for A or B."""
    tx = Transcript()

    if system == 'A':
        tokens = list(tx.currier_a())
    else:
        tokens = list(tx.currier_b())

    paragraphs = []
    current_par = None
    current_folio = None
    par_ordinal = 0  # Within-folio ordinal

    for token in tokens:
        # New paragraph on par_initial=True or folio change
        if token.par_initial or token.folio != current_folio:
            # Save previous paragraph
            if current_par is not None:
                paragraphs.append(current_par)

            # Reset ordinal on folio change
            if token.folio != current_folio:
                par_ordinal = 1
                current_folio = token.folio
            else:
                par_ordinal += 1

            # Start new paragraph
            par_id = f"{system}_{len(paragraphs) + 1:03d}"
            current_par = {
                'par_id': par_id,
                'folio': token.folio,
                'section': token.section,
                'paragraph_ordinal': par_ordinal,
                'lines': [],
                'tokens': [],
                'token_count': 0
            }

        # Add token to current paragraph
        current_par['tokens'].append({
            'word': token.word,
            'line': token.line,
            'folio': token.folio,
            'section': token.section,
            'par_initial': token.par_initial
        })
        current_par['token_count'] += 1

        # Track unique lines
        if token.line not in current_par['lines']:
            current_par['lines'].append(token.line)

    # Save last paragraph
    if current_par is not None:
        paragraphs.append(current_par)

    # Add folio_position (first/middle/last)
    folio_pars = defaultdict(list)
    for i, par in enumerate(paragraphs):
        folio_pars[par['folio']].append(i)

    for folio, indices in folio_pars.items():
        for i, idx in enumerate(indices):
            if len(indices) == 1:
                paragraphs[idx]['folio_position'] = 'only'
            elif i == 0:
                paragraphs[idx]['folio_position'] = 'first'
            elif i == len(indices) - 1:
                paragraphs[idx]['folio_position'] = 'last'
            else:
                paragraphs[idx]['folio_position'] = 'middle'

    return paragraphs

def main():
    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)

    # Build A inventory
    print("Building Currier A paragraph inventory...")
    a_paragraphs = build_inventory('A')

    # Build B inventory
    print("Building Currier B paragraph inventory...")
    b_paragraphs = build_inventory('B')

    # Calculate summary statistics
    a_token_total = sum(p['token_count'] for p in a_paragraphs)
    b_token_total = sum(p['token_count'] for p in b_paragraphs)

    a_folios = len(set(p['folio'] for p in a_paragraphs))
    b_folios = len(set(p['folio'] for p in b_paragraphs))

    # Verification
    print(f"\n=== VERIFICATION ===")
    print(f"Currier A:")
    print(f"  Paragraphs: {len(a_paragraphs)} (expected ~306)")
    print(f"  Tokens: {a_token_total} (expected 11,415)")
    print(f"  Folios: {a_folios}")
    print(f"  Mean lines/paragraph: {sum(len(p['lines']) for p in a_paragraphs) / len(a_paragraphs):.1f}")

    print(f"\nCurrier B:")
    print(f"  Paragraphs: {len(b_paragraphs)} (expected ~585)")
    print(f"  Tokens: {b_token_total} (expected 23,243)")
    print(f"  Folios: {b_folios}")
    print(f"  Mean lines/paragraph: {sum(len(p['lines']) for p in b_paragraphs) / len(b_paragraphs):.1f}")

    # Token verification
    if a_token_total != 11415:
        print(f"\nWARNING: A token count mismatch: {a_token_total} vs expected 11,415")
    if b_token_total != 23243:
        print(f"\nWARNING: B token count mismatch: {b_token_total} vs expected 23,243")

    # Save inventories (without full token lists for summary)
    a_summary = []
    for p in a_paragraphs:
        a_summary.append({
            'par_id': p['par_id'],
            'folio': p['folio'],
            'section': p['section'],
            'paragraph_ordinal': p['paragraph_ordinal'],
            'folio_position': p['folio_position'],
            'lines': p['lines'],
            'line_count': len(p['lines']),
            'token_count': p['token_count']
        })

    b_summary = []
    for p in b_paragraphs:
        b_summary.append({
            'par_id': p['par_id'],
            'folio': p['folio'],
            'section': p['section'],
            'paragraph_ordinal': p['paragraph_ordinal'],
            'folio_position': p['folio_position'],
            'lines': p['lines'],
            'line_count': len(p['lines']),
            'token_count': p['token_count']
        })

    # Save summaries
    with open(results_dir / 'a_paragraph_inventory.json', 'w') as f:
        json.dump({
            'system': 'A',
            'paragraph_count': len(a_paragraphs),
            'token_total': a_token_total,
            'folio_count': a_folios,
            'paragraphs': a_summary
        }, f, indent=2)

    with open(results_dir / 'b_paragraph_inventory.json', 'w') as f:
        json.dump({
            'system': 'B',
            'paragraph_count': len(b_paragraphs),
            'token_total': b_token_total,
            'folio_count': b_folios,
            'paragraphs': b_summary
        }, f, indent=2)

    # Save full token lists separately (for later scripts)
    with open(results_dir / 'a_paragraph_tokens.json', 'w') as f:
        json.dump({p['par_id']: p['tokens'] for p in a_paragraphs}, f)

    with open(results_dir / 'b_paragraph_tokens.json', 'w') as f:
        json.dump({p['par_id']: p['tokens'] for p in b_paragraphs}, f)

    print(f"\nSaved to {results_dir}/")
    print("  - a_paragraph_inventory.json")
    print("  - b_paragraph_inventory.json")
    print("  - a_paragraph_tokens.json")
    print("  - b_paragraph_tokens.json")

    return len(a_paragraphs), len(b_paragraphs)

if __name__ == '__main__':
    main()
