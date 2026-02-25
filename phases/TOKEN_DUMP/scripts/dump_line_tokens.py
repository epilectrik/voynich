#!/usr/bin/env python3
"""
Dump all computed per-token fields for a specific line from f79r.

Produces a structured dump of every BTokenAnalysis field for sharing
with an external expert.
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import BFolioDecoder


# 5-role reduction mapping (from prefix_role to reduced role)
ROLE_REDUCTION = {
    'EN_KERNEL': 'EN',
    'EN_QO': 'EN',
    'PREP_TIER': 'EN',
    'AX_SCAFFOLD': 'AX',
    'AX_LATE': 'AX',
    'CC_INIT': 'CC',
    'FL_FINAL': 'FL',
}


def lane_for_token(t):
    """Compute lane (QO vs CHSH) for EN tokens, N/A otherwise."""
    reduced = ROLE_REDUCTION.get(t.prefix_role)
    if reduced != 'EN':
        return 'N/A'
    prefix = t.morph.prefix if t.morph else None
    if prefix == 'qo':
        return 'QO'
    elif prefix in ('ch', 'sh'):
        return 'CHSH'
    else:
        return 'OTHER'


def pick_best_line(decoder, folio, preferred_lines):
    """Pick the line with best variety from the candidates."""
    paragraphs = decoder.analyze_folio_paragraphs(folio)
    # Build a map: line_id -> (BLineAnalysis, paragraph_zone)
    all_lines = {}
    for para in paragraphs:
        for la in para.lines:
            all_lines[la.line_id] = la

    best = None
    best_score = -1

    for lid in preferred_lines:
        la = all_lines.get(str(lid))
        if la is None:
            continue

        # Score: count unique roles, presence of FL tokens, lane diversity
        roles = set(t.prefix_role for t in la.tokens if t.prefix_role)
        reduced = set(ROLE_REDUCTION.get(t.prefix_role, 'UNK') for t in la.tokens if t.prefix_role)
        lanes = set(lane_for_token(t) for t in la.tokens)
        has_fl = any(t.fl_stage for t in la.tokens)
        n_tokens = la.token_count

        score = len(roles) * 3 + len(reduced) * 2 + len(lanes) + (5 if has_fl else 0) + n_tokens
        print(f"  Candidate L{lid}: {n_tokens} tokens, {len(roles)} roles, "
              f"{len(reduced)} reduced, FL={has_fl}, zone={la.paragraph_zone}, score={score}")

        if score > best_score:
            best_score = score
            best = la

    return best


def dump_token(i, t):
    """Dump all fields for a single token."""
    m = t.morph
    reduced = ROLE_REDUCTION.get(t.prefix_role, 'FQ' if t.prefix_role is None and t.is_fl_role else 'UNK')
    lane = lane_for_token(t)

    lines = []
    lines.append(f"  TOKEN {i+1}: '{t.word}'")
    lines.append(f"  {'-' * 50}")

    # Morphological parse
    lines.append(f"    Morphology:")
    lines.append(f"      articulator   : {m.articulator or '(none)'}")
    lines.append(f"      prefix        : {m.prefix or '(none)'}")
    if m.prefix2:
        lines.append(f"      prefix2       : {m.prefix2}")
    lines.append(f"      middle        : {m.middle or '(none)'}")
    lines.append(f"      suffix        : {m.suffix or '(none)'}")

    # Role classification
    lines.append(f"    Role Classification:")
    lines.append(f"      prefix_role   : {t.prefix_role or '(none)'}")
    lines.append(f"      5-role reduced: {reduced}")
    lines.append(f"      lane          : {lane}")
    lines.append(f"      suffix_role   : {t.suffix_role or '(none)'}")

    # Phase / zone / macro
    lines.append(f"    Positional / Phase:")
    lines.append(f"      prefix_phase  : {t.prefix_phase or '(none)'}")
    lines.append(f"      prefix_zone   : {t.prefix_zone or '(none)'}")
    lines.append(f"      macro_state   : {t.macro_state or '(none)'}")
    lines.append(f"      is_line_initial: {t.is_line_initial}")
    lines.append(f"      is_line_final : {t.is_line_final}")

    # Kernel
    lines.append(f"    Kernel:")
    lines.append(f"      kernels       : {t.kernels if t.kernels else '(none)'}")
    lines.append(f"      middle_kernel : {t.middle_kernel or '(none)'}")
    lines.append(f"      middle_regime : {t.middle_regime or '(none)'}")
    lines.append(f"      middle_section: {t.middle_section or '(none)'}")

    # MIDDLE analysis
    lines.append(f"    MIDDLE Analysis:")
    lines.append(f"      middle_tier   : {t.middle_tier or '(none)'}")
    lines.append(f"      middle_meaning: {t.middle_meaning or '(none)'}")
    lines.append(f"      middle_affordance_bin   : {t.middle_affordance_bin or '(none)'}")
    lines.append(f"      middle_affordance_family: {t.middle_affordance_family or '(none)'}")

    # FL state
    fl_stage_display = t.fl_stage if t.fl_stage else 'N/A'
    lines.append(f"    FL State:")
    lines.append(f"      fl_stage      : {fl_stage_display}")
    lines.append(f"      fl_meaning    : {t.fl_meaning or 'N/A'}")
    lines.append(f"      is_fl_role    : {t.is_fl_role}")

    # HT
    lines.append(f"    HT (Human Track):")
    lines.append(f"      is_ht         : {t.is_ht}")

    # Hub / terminal / compound / dark
    lines.append(f"    Hub / Terminal / Compound:")
    lines.append(f"      hub_sub_role  : {t.hub_sub_role or '(none)'}")
    lines.append(f"      terminal_char : {t.terminal_char or '(none)'}")
    lines.append(f"      terminal_group: {t.terminal_group or '(none)'}")
    lines.append(f"      compound_depth: {t.compound_depth}")
    lines.append(f"      compound_atoms: {t.compound_atoms if t.compound_atoms else '(none)'}")
    lines.append(f"      is_dark_pipeline: {t.is_dark_pipeline}")

    # Material / output markers
    lines.append(f"    Material / Output:")
    lines.append(f"      material_markers: {t.material_markers if t.material_markers else '(none)'}")
    lines.append(f"      output_markers  : {t.output_markers if t.output_markers else '(none)'}")

    # Suffix details
    lines.append(f"    Suffix Details:")
    lines.append(f"      suffix_terminal   : {t.suffix_terminal or '(none)'}")
    lines.append(f"      suffix_continuation: {t.suffix_continuation}")

    # Structural / interpretive strings
    lines.append(f"    Computed Strings:")
    lines.append(f"      structural()  : {t.structural()}")
    lines.append(f"      struct_gloss(): {t.structural_gloss()}")
    try:
        lines.append(f"      interpretive(): {t.interpretive()}")
    except Exception as e:
        lines.append(f"      interpretive(): ERROR: {e}")

    return '\n'.join(lines)


def main():
    folio = 'f79r'
    print(f"Initializing BFolioDecoder (this loads all maps)...")
    decoder = BFolioDecoder()

    print(f"\nAnalyzing folio {folio}...")
    print(f"Evaluating candidate lines [5, 14, 13]:")
    line_analysis = pick_best_line(decoder, folio, [5, 14, 13])

    if line_analysis is None:
        print("ERROR: None of the candidate lines found in f79r!")
        # Fall back: show what lines exist
        all_lines = decoder.analyze_folio_lines(folio)
        print(f"Available lines: {[la.line_id for la in all_lines]}")
        return

    lid = line_analysis.line_id
    print(f"\n{'=' * 60}")
    print(f"SELECTED: Line {lid} of {folio}")
    print(f"{'=' * 60}")

    # Line-level info
    print(f"\n  LINE-LEVEL INFO:")
    print(f"  {'-' * 50}")
    print(f"    line_id         : {line_analysis.line_id}")
    print(f"    token_count     : {line_analysis.token_count}")
    print(f"    line_type       : {line_analysis.line_type}")
    print(f"    paragraph_zone  : {line_analysis.paragraph_zone or '(not set - line not in paragraph analysis)'}")
    print(f"    is_header       : {line_analysis.is_header}")
    print(f"    has_init_marker : {line_analysis.has_init_marker}")
    print(f"    has_final_marker: {line_analysis.has_final_marker}")
    print(f"    init_token      : {line_analysis.init_token or '(none)'}")
    print(f"    final_token     : {line_analysis.final_token or '(none)'}")
    print(f"    fl_stages       : {line_analysis.fl_stages}")
    print(f"    fl_progression  : {line_analysis.fl_progression}")
    print(f"    kernel_sequence : {line_analysis.kernel_sequence}")
    print(f"    role_sequence   : {line_analysis.role_sequence}")
    print(f"    opener_role     : {line_analysis.opener_role or '(none)'}")
    print(f"    structural()    : {line_analysis.structural()}")
    print(f"    interpretive()  : {line_analysis.interpretive()}")
    print(f"    flow_render()   : {line_analysis.flow_render()}")

    # Per-token dump
    print(f"\n  {'=' * 60}")
    print(f"  PER-TOKEN ANALYSIS ({line_analysis.token_count} tokens)")
    print(f"  {'=' * 60}")

    for i, t in enumerate(line_analysis.tokens):
        print()
        print(dump_token(i, t))

    # Summary table (compact)
    print(f"\n  {'=' * 60}")
    print(f"  COMPACT SUMMARY TABLE")
    print(f"  {'=' * 60}")
    hdr = f"  {'#':>2} {'word':<14} {'prefix_role':<14} {'5R':<4} {'lane':<6} {'phase':<6} {'zone':<16} {'macro':<8} {'kern':<6} {'fl_stage':<10} {'morph'}"
    print(hdr)
    print(f"  {'-' * len(hdr)}")
    for i, t in enumerate(line_analysis.tokens):
        m = t.morph
        reduced = ROLE_REDUCTION.get(t.prefix_role, 'FQ' if t.is_fl_role else 'UNK')
        lane = lane_for_token(t)
        phase = t.prefix_phase or '-'
        zone = t.prefix_zone or '-'
        macro = t.macro_state or '-'
        kern = ','.join(t.kernels) if t.kernels else '-'
        fl = t.fl_stage or '-'
        morph_str = f"[{m.articulator or ''}/{m.prefix or ''}/{m.middle or ''}/{m.suffix or ''}]"
        print(f"  {i+1:>2} {t.word:<14} {(t.prefix_role or '-'):<14} {reduced:<4} {lane:<6} {phase:<6} {zone:<16} {macro:<8} {kern:<6} {fl:<10} {morph_str}")


if __name__ == '__main__':
    main()
