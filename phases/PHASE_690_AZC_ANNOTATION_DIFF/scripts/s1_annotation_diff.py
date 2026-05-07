#!/usr/bin/env python3
"""
Phase 690 — AZC annotation-transcript systematic diff.

For each user annotation file (13 total in data/folio_annotations/azc/),
compute per-folio diff between user-observed counts and H-track transcript
encoding. Methodology locked per Phase 690 INDEX.md.
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ANNOT_DIR = PROJECT_ROOT / 'data' / 'folio_annotations' / 'azc'


def load_h_track_azc():
    """All H-track AZC tokens (language=NA) with metadata. NO label exclusion."""
    tx = Transcript()
    by_folio = defaultdict(list)
    for tok in tx.all(h_only=True):
        if tok.language != 'NA':
            continue
        if not tok.word:
            continue
        if tok.is_uncertain:  # exclude * tokens to match standard methodology
            continue
        by_folio[tok.folio].append(tok)
    return dict(by_folio)


def transcript_summary(tokens):
    """Summary statistics for a folio's transcript tokens."""
    if not tokens:
        return {
            'total': 0, 'placement_counts': {},
            'distinct_lines_per_placement': {},
            'placement_codes': [],
        }
    placement_counts = Counter(t.placement for t in tokens)
    placement_lines = defaultdict(set)
    for t in tokens:
        placement_lines[t.placement].add(t.line)
    return {
        'total': len(tokens),
        'placement_counts': dict(placement_counts),
        'distinct_lines_per_placement': {p: len(ls) for p, ls in placement_lines.items()},
        'placement_codes': sorted(placement_counts.keys()),
    }


def is_ring_or_circle_code(code):
    """True if placement code refers to a ring/circle (continuous)."""
    return code.startswith('R') or code.startswith('C')


def is_spoke_or_sectored_code(code):
    """True if placement code refers to spokes or nymph-divided rings."""
    return code.startswith('S')


def extract_user_layout(annotation, folio):
    """
    Extract user-stated counts from an annotation file for a given folio.
    Returns dict with total, center, ring_layers, etc.
    """
    folio_data = annotation.get('structure', {}).get(folio)
    if folio_data is None:
        # Single-folio annotation file (e.g., f69r.json) — annotation may be at top level
        folio_data = annotation

    layout = folio_data.get('layout', {})

    user_total = folio_data.get('tokens', None)

    # Center tokens — look for user_observed in center section
    center = layout.get('center', {})
    user_center_observed = None
    if isinstance(center, dict):
        # User's observation may be in 'user_observed' field as int or string
        uo = center.get('user_observed')
        if isinstance(uo, int):
            user_center_observed = uo
        elif isinstance(uo, str):
            # Try to extract integer from "2 tokens" etc.
            import re
            m = re.search(r'\d+', uo)
            if m:
                user_center_observed = int(m.group())
        # Fallback: count from explicit token list
        if user_center_observed is None and 'tokens' in center:
            t = center['tokens']
            if isinstance(t, int):
                user_center_observed = t

    # Ring layers — count R/S placements mentioned
    user_ring_layers = 0
    user_outer_ring_count = 0
    user_inner_segmented_count = 0
    for section_name in ['outer_rings_continuous', 'rings_continuous', 'rings']:
        sec = layout.get(section_name)
        if isinstance(sec, dict):
            user_outer_ring_count = len(sec.get('placements', []))
            user_ring_layers += user_outer_ring_count
    for section_name in ['inner_rings_nymph_divided', 'rings_nymph_divided', 'spokes']:
        sec = layout.get(section_name)
        if isinstance(sec, dict):
            user_inner_segmented_count = len(sec.get('placements', []))
            user_ring_layers += user_inner_segmented_count

    # Diagram type
    diagram_type = folio_data.get('diagram_type', folio_data.get('type', 'UNKNOWN'))

    # Oddities mentioning this folio
    oddities = []
    for od in annotation.get('oddities', []):
        if isinstance(od, dict):
            ods_folios = od.get('folios', [folio])
            if folio in ods_folios:
                oddities.append({'type': od.get('type', '?'), 'desc': od.get('description', '')})

    return {
        'user_total': user_total,
        'user_center_observed': user_center_observed,
        'user_ring_layers': user_ring_layers,
        'user_outer_ring_count': user_outer_ring_count,
        'user_inner_segmented_count': user_inner_segmented_count,
        'diagram_type': diagram_type,
        'oddities': oddities,
        'description': folio_data.get('description', ''),
        'illustration_notes': folio_data.get('illustration_notes', []),
    }


def transcript_layout(summary):
    """Extract ring/center counts from transcript summary."""
    placement_counts = summary['placement_counts']
    placement_lines = summary['distinct_lines_per_placement']

    # Center tokens: any C, C1, C2 placement, or W, I, B (per architecture doc)
    center_codes = {'C', 'C1', 'C2', 'W', 'I', 'B'}
    transcript_center = sum(c for p, c in placement_counts.items() if p in center_codes)

    # Distinct ring/circle layers: R, R1, R2, R3, R4, C, C1, C2 (continuous)
    ring_circle_layers = set()
    for p in placement_counts:
        if p == 'R' or (p.startswith('R') and len(p) <= 3):
            ring_circle_layers.add(p)
        elif p == 'C' or (p.startswith('C') and len(p) <= 3 and p not in {'C', 'C1', 'C2'}):
            ring_circle_layers.add(p)

    # Distinct S layers (spokes or nymph-divided)
    s_layers = set()
    for p in placement_counts:
        if p.startswith('S'):
            s_layers.add(p)

    return {
        'transcript_total': summary['total'],
        'transcript_center': transcript_center,
        'transcript_ring_layers': len(ring_circle_layers) + len(s_layers),
        'transcript_continuous_rings': len(ring_circle_layers),
        'transcript_s_layers': len(s_layers),
        'placement_codes': summary['placement_codes'],
    }


def diff_folio(folio, user, transcript_summ):
    """Build diff record for one folio."""
    transcript = transcript_layout(transcript_summ)

    user_total = user.get('user_total')
    transcript_total = transcript['transcript_total']
    total_diff = (user_total - transcript_total) if (user_total is not None and transcript_total is not None) else None

    user_center = user.get('user_center_observed')
    transcript_center = transcript['transcript_center']
    center_diff = (user_center - transcript_center) if (user_center is not None and transcript_center is not None) else None

    user_rings = user.get('user_ring_layers')
    transcript_rings = transcript['transcript_ring_layers']
    ring_diff = (user_rings - transcript_rings) if (user_rings and transcript_rings) else None

    has_any_discrepancy = (
        (total_diff is not None and total_diff != 0) or
        (center_diff is not None and center_diff != 0) or
        (ring_diff is not None and ring_diff != 0)
    )

    return {
        'folio': folio,
        'diagram_type': user['diagram_type'],
        'description': user['description'],
        'user_total': user_total,
        'transcript_total': transcript_total,
        'total_diff': total_diff,
        'user_center': user_center,
        'transcript_center': transcript_center,
        'center_diff': center_diff,
        'user_ring_layers': user_rings,
        'transcript_ring_layers': transcript_rings,
        'transcript_continuous_rings': transcript['transcript_continuous_rings'],
        'transcript_s_layers': transcript['transcript_s_layers'],
        'ring_diff': ring_diff,
        'placement_codes': transcript['placement_codes'],
        'oddities_count': len(user.get('oddities', [])),
        'oddities': user.get('oddities', []),
        'flag_for_review': has_any_discrepancy,
    }


def main():
    print("Loading H-track AZC tokens...")
    by_folio = load_h_track_azc()
    print(f"  Folios with AZC tokens: {len(by_folio)}")
    print(f"  Total AZC tokens: {sum(len(toks) for toks in by_folio.values())}")

    # Build transcript summaries per folio
    summaries = {f: transcript_summary(toks) for f, toks in by_folio.items()}

    # Process annotations
    annot_files = sorted(ANNOT_DIR.glob('*.json'))
    print(f"\nLoading {len(annot_files)} annotation files...")

    results = []
    for af in annot_files:
        with open(af) as f:
            annotation = json.load(f)
        folios_in_file = annotation.get('folios', [annotation.get('folio')])
        if isinstance(folios_in_file, str):
            folios_in_file = [folios_in_file]
        if not folios_in_file or folios_in_file == [None]:
            # try inferring from structure keys
            folios_in_file = list(annotation.get('structure', {}).keys())
            if not folios_in_file:
                # try filename
                folios_in_file = [af.stem]
        for folio in folios_in_file:
            user = extract_user_layout(annotation, folio)
            transcript_summ = summaries.get(folio, {
                'total': 0, 'placement_counts': {},
                'distinct_lines_per_placement': {},
                'placement_codes': [],
            })
            diff = diff_folio(folio, user, transcript_summ)
            diff['annotation_file'] = af.name
            results.append(diff)

    print(f"  Per-folio records: {len(results)}")

    # Aggregate statistics
    n_total = len(results)
    n_with_total_diff = sum(1 for r in results if r['total_diff'] not in (None, 0))
    n_with_center_diff = sum(1 for r in results if r['center_diff'] not in (None, 0))
    n_with_ring_diff = sum(1 for r in results if r['ring_diff'] not in (None, 0))
    n_flagged = sum(1 for r in results if r['flag_for_review'])

    # Diagram type breakdown
    by_type = defaultdict(list)
    for r in results:
        by_type[r['diagram_type']].append(r)

    print("\n" + "=" * 72)
    print("AGGREGATE")
    print("=" * 72)
    print(f"  Total folios audited:                  {n_total}")
    print(f"  Folios with any discrepancy (flagged): {n_flagged}")
    print(f"  Folios with total-token diff != 0:     {n_with_total_diff}")
    print(f"  Folios with center diff != 0:          {n_with_center_diff}")
    print(f"  Folios with ring-layer diff != 0:      {n_with_ring_diff}")

    print("\n  Per-diagram-type breakdown:")
    for dtype, recs in sorted(by_type.items()):
        flagged = sum(1 for r in recs if r['flag_for_review'])
        print(f"    {dtype}: {len(recs)} folios, {flagged} flagged")

    print("\n" + "=" * 72)
    print("PER-FOLIO TABLE (truncated for terminal)")
    print("=" * 72)
    header = f"{'folio':<10s} {'type':<25s} {'usr_tot':>7s} {'tx_tot':>7s} {'usr_c':>5s} {'tx_c':>4s} {'flag':>5s}"
    print(header)
    print("-" * len(header))
    for r in results:
        flag = 'YES' if r['flag_for_review'] else '.'
        usr_tot = str(r['user_total']) if r['user_total'] is not None else '?'
        tx_tot = str(r['transcript_total'])
        usr_c = str(r['user_center']) if r['user_center'] is not None else '?'
        tx_c = str(r['transcript_center'])
        print(f"{r['folio']:<10s} {r['diagram_type'][:25]:<25s} {usr_tot:>7s} {tx_tot:>7s} {usr_c:>5s} {tx_c:>4s} {flag:>5s}")

    # Center-token discrepancy detail
    print("\n" + "=" * 72)
    print("CENTER-TOKEN DISCREPANCIES")
    print("=" * 72)
    for r in results:
        if r['center_diff'] not in (None, 0):
            sign = '+' if r['center_diff'] > 0 else ''
            print(f"  {r['folio']:<8s}: user={r['user_center']} transcript={r['transcript_center']} diff={sign}{r['center_diff']} ({r['description'][:50]})")

    # Save results
    out = {
        'phase': 690,
        'aggregate': {
            'n_total_folios': n_total,
            'n_flagged': n_flagged,
            'n_with_total_diff': n_with_total_diff,
            'n_with_center_diff': n_with_center_diff,
            'n_with_ring_diff': n_with_ring_diff,
        },
        'by_diagram_type': {
            dtype: {
                'n_folios': len(recs),
                'n_flagged': sum(1 for r in recs if r['flag_for_review']),
                'folios': [r['folio'] for r in recs],
            }
            for dtype, recs in by_type.items()
        },
        'per_folio': results,
    }

    out_path = Path(__file__).resolve().parent.parent / 'results' / 'annotation_transcript_diff.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
