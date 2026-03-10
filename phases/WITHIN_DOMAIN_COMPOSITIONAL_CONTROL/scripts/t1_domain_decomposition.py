"""Phase 560 T1: Domain-Partitioned Corpus Decomposition

Iterates ALL Currier B tokens, decomposes via BFolioDecoder.analyze_token(),
assigns domain from HEAD atom, computes positional context (line_zone,
paragraph_zone), builds headless subtypes, and records adjacency context.

Input: All H-track Currier B tokens via Transcript().currier_b()
Output: t1_domain_decomposition.json
"""
import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import (
    Transcript, Morphology, BFolioDecoder, decompose_middle_hmt
)

# Domain mapping: plan labels (Phase 560), not voynich.py internal labels
HEAD_TO_DOMAIN = {
    'k': 'THERMAL',
    't': 'FLOW',
    'a': 'ACTIVE',
    'e': 'STABILITY',
    'o': 'ARRANGEMENT',
}
HEADED_ATOMS = {'k', 't', 'a', 'e', 'o'}

# Headless subtype classification (expert review #3)
PSEUDO_HEAD_CORE = {'d', 'i', 'l'}   # C1489: real pseudo-HEAD selectors
PARAMETRIC = {'c', 'p', 'f'}          # C1492: suffixed parametric mode
DISPLACED_HEAD_ATOMS = {'k', 't', 'e', 'a', 'o'}


def classify_headless_subtype(pseudo_head_atom):
    """Classify headless token into subtype per expert spec."""
    if pseudo_head_atom in PSEUDO_HEAD_CORE:
        return 'PSEUDO_HEAD_CORE'
    elif pseudo_head_atom in PARAMETRIC:
        return 'PARAMETRIC'
    return 'OTHER'


def has_displaced_head_terminal(middle):
    """Check if MIDDLE contains interior k/t/e/a/o atom (not at position 0).
    Tracks displaced HEAD atoms functioning as terminals under c-context (C1494-C1497).
    """
    if not middle or len(middle) < 2:
        return False
    for ch in middle[1:]:
        if ch in DISPLACED_HEAD_ATOMS:
            return True
    return False


def compute_quintile(pos_idx, n_tokens):
    """Assign quintile Q0-Q4 from 0-based position index."""
    if n_tokens <= 1:
        return 0
    frac = pos_idx / (n_tokens - 1)
    return min(int(frac * 5), 4)


def zone_from_quintile(q):
    if q == 0:
        return 'SPEC'
    elif q == 4:
        return 'CLOSE'
    return 'WORK'


def main():
    t0 = time.time()
    print("=== Phase 560 T1: Domain-Partitioned Corpus Decomposition ===")

    # Initialize
    print("  Initializing BFolioDecoder...")
    decoder = BFolioDecoder()
    tx = Transcript()

    # ═══════════════════════════════════════════════════════════
    # Step 1: Load ALL Currier B tokens
    # ═══════════════════════════════════════════════════════════
    print("  Loading Currier B tokens...")
    raw_tokens = [t for t in tx.currier_b()
                  if '*' not in t.word and t.word.strip()]
    print(f"  Raw B tokens: {len(raw_tokens)}")

    # ═══════════════════════════════════════════════════════════
    # Step 2: Organize by folio → paragraph → line
    # ═══════════════════════════════════════════════════════════
    print("  Organizing tokens by folio/paragraph/line...")

    # Group tokens by (folio, line) preserving order
    folio_para_line = defaultdict(lambda: defaultdict(list))
    # Track paragraph boundaries per folio
    folio_paragraphs = defaultdict(list)  # folio -> list of lists of (line_id, [tokens])

    current_folio = None
    current_para = []
    current_line_id = None
    current_line_tokens = []

    for t in raw_tokens:
        line_id = (t.folio, t.line)

        # Detect folio change
        if t.folio != current_folio:
            # Flush previous line and paragraph
            if current_line_tokens:
                current_para.append((current_line_id, current_line_tokens))
            if current_para and current_folio is not None:
                folio_paragraphs[current_folio].append(current_para)
            current_folio = t.folio
            current_para = []
            current_line_tokens = [t]
            current_line_id = line_id

        elif line_id != current_line_id:
            # Flush previous line
            if current_line_tokens:
                current_para.append((current_line_id, current_line_tokens))
            # Check paragraph boundary
            if t.par_initial and current_para:
                folio_paragraphs[current_folio].append(current_para)
                current_para = []
            current_line_tokens = [t]
            current_line_id = line_id
        else:
            current_line_tokens.append(t)

    # Flush final
    if current_line_tokens:
        current_para.append((current_line_id, current_line_tokens))
    if current_para and current_folio is not None:
        folio_paragraphs[current_folio].append(current_para)

    n_folios = len(folio_paragraphs)
    n_paras = sum(len(ps) for ps in folio_paragraphs.values())
    n_lines = sum(len(line) for ps in folio_paragraphs.values()
                  for p in ps for line in [p])
    print(f"  Folios: {n_folios}, Paragraphs: {n_paras}")

    # ═══════════════════════════════════════════════════════════
    # Step 3: Analyze every token
    # ═══════════════════════════════════════════════════════════
    print("  Analyzing tokens via BFolioDecoder...")

    corpus_tokens = []
    token_idx_global = 0

    for folio, paragraphs in folio_paragraphs.items():
        n_para_lines = [len(para) for para in paragraphs]

        for pi, para in enumerate(paragraphs):
            n_lines_in_para = len(para)

            for li, (line_id, line_tokens) in enumerate(para):
                n_toks = len(line_tokens)

                # Determine paragraph zone
                if li == 0:
                    para_zone = 'HEADER'
                elif li == n_lines_in_para - 1:
                    para_zone = 'TAIL'
                else:
                    para_zone = 'BODY'

                # First pass: analyze all tokens in line
                line_analyses = []
                for ti, tok in enumerate(line_tokens):
                    is_first = (ti == 0)
                    is_last = (ti == n_toks - 1)
                    analysis = decoder.analyze_token(tok.word,
                                                     line_initial=is_first,
                                                     line_final=is_last)

                    # Determine domain
                    head = analysis.middle_head
                    if head is not None:
                        domain = HEAD_TO_DOMAIN.get(head, 'HEADLESS')
                    else:
                        domain = 'HEADLESS'

                    # Headless subtype
                    hl_subtype = None
                    hl_displaced = False
                    if domain == 'HEADLESS':
                        pa = analysis.pseudo_head_atom
                        hl_subtype = classify_headless_subtype(pa) if pa else 'OTHER'
                        hl_displaced = has_displaced_head_terminal(
                            analysis.morph.middle)

                    # Line position
                    if n_toks <= 1:
                        line_pos = 0.0
                    else:
                        line_pos = ti / (n_toks - 1)
                    quintile = compute_quintile(ti, n_toks)
                    line_zone = zone_from_quintile(quintile)

                    # Suffix head
                    sfx = analysis.morph.suffix
                    sfx_head = sfx[0] if sfx and len(sfx) > 0 else None

                    rec = {
                        'word': tok.word,
                        'folio': tok.folio,
                        'section': tok.section,
                        'line': tok.line,
                        'line_pos': round(line_pos, 4),
                        'quintile': quintile,
                        'line_zone': line_zone,
                        'paragraph_idx': pi,
                        'paragraph_zone': para_zone,
                        'domain': domain,
                        'headless_subtype': hl_subtype,
                        'has_displaced_head_terminal': hl_displaced,
                        'head': head,
                        'mods': analysis.middle_mods,
                        'term': analysis.middle_term,
                        'frame': analysis.head_term_frame,
                        'middle': analysis.morph.middle,
                        'prefix': analysis.morph.prefix,
                        'prefix_base': analysis.prefix_base,
                        'prefix_modifier': analysis.prefix_modifier,
                        'suffix': analysis.morph.suffix,
                        'suffix_head': sfx_head,
                        'operational_category': analysis.operational_category,
                        'frame_hazard': analysis.frame_hazard,
                        'has_i_mod': analysis.has_i_mod,
                        'i_count': analysis.i_count,
                        'has_quenching_mod': analysis.has_quenching_mod,
                        'is_safe_pathway': analysis.is_safe_pathway,
                        'source_immune': analysis.source_immune,
                        'terminal_opacity': analysis.terminal_opacity,
                        'terminal_tier': analysis.terminal_tier,
                        'is_dark_pipeline': analysis.is_dark_pipeline,
                        'pseudo_head_atom': analysis.pseudo_head_atom,
                        'pseudo_head_domain': analysis.pseudo_head_domain,
                        'compound_depth': analysis.compound_depth,
                        # Placeholders for adjacency — filled in second pass
                        'prev_term_same_line': None,
                        'next_domain_same_line': None,
                    }
                    line_analyses.append(rec)

                # Second pass: fill adjacency context
                for ti, rec in enumerate(line_analyses):
                    if ti > 0:
                        rec['prev_term_same_line'] = line_analyses[ti - 1]['term']
                    if ti < len(line_analyses) - 1:
                        rec['next_domain_same_line'] = line_analyses[ti + 1]['domain']

                corpus_tokens.extend(line_analyses)

    print(f"  Total tokens analyzed: {len(corpus_tokens)}")

    # ═══════════════════════════════════════════════════════════
    # Step 4: Build index structures
    # ═══════════════════════════════════════════════════════════
    print("  Building index structures...")

    by_domain = defaultdict(list)
    by_folio = defaultdict(list)
    by_folio_domain = defaultdict(lambda: defaultdict(list))
    by_folio_para = defaultdict(lambda: defaultdict(list))

    for i, tok in enumerate(corpus_tokens):
        by_domain[tok['domain']].append(i)
        by_folio[tok['folio']].append(i)
        by_folio_domain[tok['folio']][tok['domain']].append(i)
        by_folio_para[tok['folio']][tok['paragraph_idx']].append(i)

    # Census
    census = {
        'total': len(corpus_tokens),
        'by_domain': {d: len(idxs) for d, idxs in by_domain.items()},
        'by_section': dict(Counter(t['section'] for t in corpus_tokens)),
        'by_folio_count': {f: len(idxs) for f, idxs in by_folio.items()},
        'headless_subtypes': dict(Counter(
            t['headless_subtype'] for t in corpus_tokens
            if t['domain'] == 'HEADLESS'
        )),
        'n_folios': len(by_folio),
    }

    print(f"\n  === Census ===")
    print(f"  Total tokens: {census['total']}")
    for d in ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']:
        print(f"  {d}: {census['by_domain'].get(d, 0)}")
    print(f"  Headless subtypes: {census['headless_subtypes']}")
    print(f"  Folios: {census['n_folios']}")
    print(f"  Sections: {census['by_section']}")

    # ═══════════════════════════════════════════════════════════
    # Step 5: Validation checks
    # ═══════════════════════════════════════════════════════════
    print("\n  === Validation ===")
    validations = {}
    all_pass = True

    # Total tokens in range
    total = census['total']
    v = 22500 <= total <= 24000
    validations['total_in_range'] = {'value': total, 'range': [22500, 24000], 'pass': v}
    if not v:
        all_pass = False
    print(f"  Total in [22500, 24000]: {total} -> {'PASS' if v else 'FAIL'}")

    # All 6 domains populated
    for d in ['THERMAL', 'FLOW', 'ACTIVE', 'STABILITY', 'ARRANGEMENT', 'HEADLESS']:
        ct = census['by_domain'].get(d, 0)
        v = ct > 0
        validations[f'{d}_populated'] = {'value': ct, 'pass': v}
        if not v:
            all_pass = False
        print(f"  {d} > 0: {ct} -> {'PASS' if v else 'FAIL'}")

    # Domain count ranges
    domain_ranges = {
        'THERMAL': (2800, 3400),
        'FLOW': (800, 1050),
        'ACTIVE': (2800, 3400),
        'STABILITY': (6500, 7500),
        'ARRANGEMENT': (2400, 3000),
        'HEADLESS': (5800, 6800),
    }
    for d, (lo, hi) in domain_ranges.items():
        ct = census['by_domain'].get(d, 0)
        v = lo <= ct <= hi
        validations[f'{d}_range'] = {'value': ct, 'range': [lo, hi], 'pass': v}
        if not v:
            all_pass = False
        print(f"  {d} in [{lo}, {hi}]: {ct} -> {'PASS' if v else 'FAIL'}")

    # Folios represented
    nf = census['n_folios']
    v = nf >= 80
    validations['folios_ge_80'] = {'value': nf, 'pass': v}
    if not v:
        all_pass = False
    print(f"  Folios >= 80: {nf} -> {'PASS' if v else 'FAIL'}")

    # All 3 headless subtypes populated
    for st in ['PSEUDO_HEAD_CORE', 'PARAMETRIC', 'OTHER']:
        ct = census['headless_subtypes'].get(st, 0)
        v = ct > 0
        validations[f'headless_{st}_populated'] = {'value': ct, 'pass': v}
        if not v:
            all_pass = False
        print(f"  Headless {st} > 0: {ct} -> {'PASS' if v else 'FAIL'}")

    print(f"\n  Validation: {'ALL PASS' if all_pass else 'SOME FAILURES'}")

    # ═══════════════════════════════════════════════════════════
    # Step 6: Save output
    # ═══════════════════════════════════════════════════════════
    # Save indices as lists of ints (not full token dicts — those are in corpus_tokens)
    output = {
        'metadata': {
            'phase': '560',
            'task': 'T1_domain_decomposition',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'n_tokens': len(corpus_tokens),
        },
        'corpus_tokens': corpus_tokens,
        'indices': {
            'by_domain': dict(by_domain),
            'by_folio': dict(by_folio),
            'by_folio_domain': {f: dict(dd) for f, dd in by_folio_domain.items()},
            'by_folio_para': {f: dict(pp) for f, pp in by_folio_para.items()},
        },
        'census': census,
        'validations': validations,
        'validation_pass': all_pass,
    }

    out_path = (Path(__file__).parent.parent / 'results'
                / 't1_domain_decomposition.json')
    print(f"\n  Writing output to {out_path}...")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)

    import os
    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    elapsed = time.time() - t0
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n=== T1 Complete (validation: {'PASS' if all_pass else 'FAIL'}) ===")


if __name__ == '__main__':
    main()
