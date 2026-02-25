"""Phase 443: PARAGRAPH_READING - Compose operational narrative from structural analysis.

Usage:
    python phases/PARAGRAPH_READING/scripts/read_paragraph.py --folio f34r --para 1
    python phases/PARAGRAPH_READING/scripts/read_paragraph.py --folio f34r --para 1 --json-only
    python phases/PARAGRAPH_READING/scripts/read_paragraph.py --folio f34r --para 1 --md-only
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter
from datetime import date

# Project root
ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import (
    BFolioDecoder, TokenDictionary, MiddleDictionary, Morphology
)
from scripts.show_b_folio import compile_ir_block, IRBlock, IRToken


# ---------------------------------------------------------------------------
# Decoder maps: prefix actions + suffix flow
# ---------------------------------------------------------------------------

def load_decoder_maps():
    """Load prefix_actions and suffix_flow from decoder_maps.json."""
    with open(ROOT / 'data' / 'decoder_maps.json', 'r', encoding='utf-8') as f:
        raw = json.load(f)
    maps = raw.get('maps', {})
    prefix_actions = {}
    for k, v in maps.get('prefix_actions', {}).get('entries', {}).items():
        prefix_actions[k] = v['value']
    suffix_flow = {}
    for k, v in maps.get('suffix_flow', {}).get('entries', {}).items():
        suffix_flow[k] = v['value']
    suffix_gloss = {}
    for k, v in maps.get('suffix_gloss', {}).get('entries', {}).items():
        suffix_gloss[k] = v['value']
    return prefix_actions, suffix_flow, suffix_gloss


PREFIX_ACTIONS, SUFFIX_FLOW, SUFFIX_GLOSS = load_decoder_maps()


# ---------------------------------------------------------------------------
# Stage 1: Structural Analysis
# ---------------------------------------------------------------------------

def get_paragraph(decoder, folio, para_num):
    """Get a specific paragraph from a folio."""
    paragraphs = decoder.analyze_folio_paragraphs(folio)
    if para_num < 1 or para_num > len(paragraphs):
        print(f"Error: folio {folio} has {len(paragraphs)} paragraphs, requested P{para_num}")
        sys.exit(1)
    return paragraphs[para_num - 1]


def extract_context(decoder, folio, para):
    """Extract folio and paragraph context."""
    fa = decoder.analyze_folio(folio)
    ctx = {
        'folio': folio,
        'section': fa.section if hasattr(fa, 'section') else None,
        'regime': fa.regime if hasattr(fa, 'regime') else None,
        'archetype': fa.archetype if hasattr(fa, 'archetype') else None,
    }

    # Folio kernel (from program card if available)
    if hasattr(fa, 'kernel_dist') and fa.kernel_dist:
        total = sum(fa.kernel_dist.values())
        if total > 0:
            ctx['folio_kernel'] = {k: round(100 * v / total, 1)
                                   for k, v in fa.kernel_dist.items()}

    return ctx


def extract_para_overview(para):
    """Extract paragraph-level overview data."""
    overview = {
        'paragraph_id': para.paragraph_id,
        'line_count': para.line_count,
        'token_count': para.token_count,
        'boundary_token': para.boundary_token,
    }

    # Kernel balance
    if hasattr(para, 'kernel_dist') and para.kernel_dist:
        total = sum(para.kernel_dist.values())
        if total > 0:
            overview['kernel_balance'] = {k: round(100 * v / total, 1)
                                           for k, v in para.kernel_dist.items()}
            overview['kernel_character'] = para.kernel_balance

    # Suffix mode cycling
    if hasattr(para, 'suffix_mode_sequence'):
        overview['suffix_mode_sequence'] = para.suffix_mode_sequence
        overview['mode_interleave_rate'] = para.mode_interleave_rate

    # Zone distribution
    if hasattr(para, 'zone_distribution'):
        overview['zone_distribution'] = para.zone_distribution

    # Gradient
    if hasattr(para, 'gradient_direction'):
        overview['gradient_direction'] = para.gradient_direction

    # Tail product signature
    if hasattr(para, 'tail_product_signature'):
        overview['tail_product_signature'] = para.tail_product_signature

    return overview


# ---------------------------------------------------------------------------
# Stage 2: Token Annotation
# ---------------------------------------------------------------------------

def annotate_line(la, decoder, middle_dict):
    """Produce IR block and per-token annotations for one line."""
    ir = compile_ir_block(la, decoder, middle_dict)
    token_annotations = []
    for tok in la.tokens:
        morph = tok.morph
        ann = {
            'word': tok.word,
            'prefix': morph.prefix if morph else None,
            'middle': morph.middle if morph else None,
            'suffix': morph.suffix if morph else None,
            'interpretive': tok.interpretive(),
            'is_ht': tok.is_ht,
            'is_dark_pipeline': getattr(tok, 'is_dark_pipeline', False),
            'kernels': tok.kernels or [],
        }
        fg = tok.flow_gloss()
        if fg:
            ann['fl_stage'] = fg.get('fl_stage')
            ann['operation'] = fg.get('operation')
            ann['flow'] = fg.get('flow')
            ann['flow_type'] = fg.get('flow_type')
        token_annotations.append(ann)
    return ir, token_annotations


# ---------------------------------------------------------------------------
# Stage 3: Line Narrative Composition
# ---------------------------------------------------------------------------

def describe_token_set(tokens, middle_dict):
    """Describe a set of IR tokens as concurrent operations (C961: unordered)."""
    if not tokens:
        return None
    parts = []
    for t in tokens:
        # Build operation description from prefix + middle gloss
        prefix_verb = PREFIX_ACTIONS.get(t.prefix, '')
        mid_gloss = None
        if t.t3_gloss:
            mid_gloss = t.t3_gloss
        elif t.middle and middle_dict:
            mid_gloss = middle_dict.get_gloss(t.middle)
            if mid_gloss and (mid_gloss == 'None' or ' ' in mid_gloss):
                mid_gloss = None

        sfx_label = ''
        if t.suffix:
            flow = SUFFIX_FLOW.get(t.suffix)
            if flow:
                sfx_label = f"->{flow.lower()}"

        if prefix_verb and mid_gloss:
            desc = f"{prefix_verb} {mid_gloss}{sfx_label}"
        elif mid_gloss:
            desc = f"{mid_gloss}{sfx_label}"
        elif prefix_verb:
            desc = f"{prefix_verb} [{t.middle}]{sfx_label}"
        else:
            desc = f"[{t.middle}]{sfx_label}"

        # Sister annotation
        if t.sister_tag:
            desc += f" ({t.sister_tag})"

        parts.append(desc)

    return ', '.join(parts)


def describe_ht_tokens(tokens, middle_dict):
    """Describe HT/UN tokens as identification context."""
    if not tokens:
        return None
    atoms = []
    for t in tokens:
        if t.is_dark_pipeline:
            atoms.append(f"[ident:{t.middle}]")
        else:
            atoms.append(t.word)
    return f"{len(tokens)} specification token(s): {', '.join(atoms[:5])}" + \
           (f" +{len(atoms)-5} more" if len(atoms) > 5 else "")


def compose_line_narrative(la, ir, token_annotations, middle_dict):
    """Compose a natural-language summary of one line.

    CRITICAL: WORK zone is UNORDERED (C961). Use 'and', never 'then'.
    """
    parts = []
    zone = ir.paragraph_zone or 'BODY'
    mode = ir.suffix_mode or '?'
    n_tokens = len(ir.raw_sequence)

    # Line character from paragraph zone
    if zone == 'HEADER':
        ht_count = len(ir.ht_tokens)
        ht_pct = round(100 * ht_count / n_tokens) if n_tokens > 0 else 0
        parts.append(f"HEADER (Mode {mode}): {n_tokens} tokens, {ht_count} HT/UN ({ht_pct}%).")

        # HT description
        ht_desc = describe_ht_tokens(ir.ht_tokens, middle_dict)
        if ht_desc:
            parts.append(f"Identification: {ht_desc}.")

    elif mode == 'A':
        parts.append(f"SPECIFICATION pass (Mode A): {n_tokens} tokens.")
    else:
        parts.append(f"EXECUTION pass (Mode B): {n_tokens} tokens.")

    # SETUP zone
    if ir.setup_tokens:
        setup_desc = describe_token_set(ir.setup_tokens, middle_dict)
        if setup_desc:
            parts.append(f"Setup: {setup_desc}.")

    # WORK zone — describe as concurrent set (C961)
    work_parts = []
    if ir.work_en_chsh:
        desc = describe_token_set(ir.work_en_chsh, middle_dict)
        if desc:
            work_parts.append(f"monitoring/testing: {desc}")
    if ir.work_en_qo:
        desc = describe_token_set(ir.work_en_qo, middle_dict)
        if desc:
            work_parts.append(f"energy: {desc}")
    if ir.work_ax:
        desc = describe_token_set(ir.work_ax, middle_dict)
        if desc:
            work_parts.append(f"scaffold: {desc}")

    if work_parts:
        # Concurrent: join with ' + '
        parts.append(f"Operations (concurrent): {' + '.join(work_parts)}.")

    # CHECK zone
    if ir.check_tokens:
        check_desc = describe_token_set(ir.check_tokens, middle_dict)
        if check_desc:
            parts.append(f"Checkpoints: {check_desc}.")

    # FL zone
    if ir.fl_tokens:
        fl_desc = describe_token_set(ir.fl_tokens, middle_dict)
        if fl_desc:
            parts.append(f"State index: {fl_desc}.")

    # CLOSE zone
    if ir.close_tokens:
        close_desc = describe_token_set(ir.close_tokens, middle_dict)
        if close_desc:
            parts.append(f"Close: {close_desc}.")

    # Kernel summary
    if ir.kernel_summary and ir.kernel_summary != '-':
        parts.append(f"Kernels: {ir.kernel_summary}.")

    return ' '.join(parts)


# ---------------------------------------------------------------------------
# Stage 4: Paragraph Narrative
# ---------------------------------------------------------------------------

def compose_paragraph_narrative(ctx, overview, line_records):
    """Compose a paragraph-level process description."""
    parts = []

    # Opening
    pid = overview['paragraph_id']
    lc = overview['line_count']
    tc = overview['token_count']
    gallows = overview.get('boundary_token', '?')
    section = ctx.get('section', '?')
    regime = ctx.get('regime', '?')

    parts.append(
        f"{pid} is a {lc}-line, {tc}-token program in section {section} "
        f"({regime}), opened by a {gallows}-gallows."
    )

    # Kernel balance
    kb = overview.get('kernel_balance', {})
    kchar = overview.get('kernel_character', '')
    if kb:
        k_str = ', '.join(f"{k}={v}%" for k, v in sorted(kb.items()))
        parts.append(f"Kernel balance: {k_str} ({kchar}).")

    # Suffix mode cycling
    modes = overview.get('suffix_mode_sequence', [])
    interleave = overview.get('mode_interleave_rate', 0)
    if modes:
        mode_str = ''.join(modes)
        parts.append(
            f"Suffix mode cycling: {mode_str} "
            f"({round(interleave * 100)}% interleave rate)."
        )

    # Zone distribution
    zones = overview.get('zone_distribution', {})
    if zones:
        parts.append(
            f"Zones: {', '.join(f'{k}={v}' for k, v in zones.items())}."
        )

    # Header description
    header_lines = [r for r in line_records if r['paragraph_zone'] == 'HEADER']
    if header_lines:
        ht_count = header_lines[0].get('ht_count', 0)
        parts.append(
            f"The header establishes identification context with "
            f"{ht_count} HT/UN tokens."
        )

    # Body characterization
    body_lines = [r for r in line_records if r['paragraph_zone'] != 'HEADER']
    if body_lines:
        # Count operation families across body
        all_ops = []
        for lr in body_lines:
            for zone_name in ('work_en_chsh_count', 'work_en_qo_count', 'work_ax_count'):
                if lr.get(zone_name, 0) > 0:
                    all_ops.append(zone_name.replace('_count', ''))

        op_counts = Counter(all_ops)
        dominant = op_counts.most_common(1)
        if dominant:
            dom_name = dominant[0][0].replace('work_en_', '').replace('work_', '').upper()
            parts.append(
                f"Body lines are dominated by {dom_name} operations "
                f"across {len(body_lines)} lines."
            )

    # Tail description
    tail_sig = overview.get('tail_product_signature')
    if tail_sig:
        parts.append(f"Tail product signature: {tail_sig}.")

    # Gradient
    gradient = overview.get('gradient_direction')
    if gradient:
        parts.append(f"Gradient: {gradient}.")

    return ' '.join(parts)


# ---------------------------------------------------------------------------
# Stage 5: Coherence Assessment
# ---------------------------------------------------------------------------

def assess_coherence(overview, line_records, token_records_all):
    """Run automated coherence checks."""
    checks = {}

    # 1. Kernel consistency
    kb = overview.get('kernel_balance', {})
    kchar = overview.get('kernel_character', '')
    checks['kernel_consistency'] = {
        'status': 'PASS' if kb else 'WARN',
        'detail': f"Kernel balance {kb}, character: {kchar}"
    }

    # 2. Zone coverage
    zones = set(r.get('paragraph_zone') for r in line_records)
    has_header = 'HEADER' in zones
    checks['zone_coverage'] = {
        'status': 'PASS' if has_header else 'WARN',
        'detail': f"Zones present: {sorted(zones)}. Header: {'yes' if has_header else 'NO'}"
    }

    # 3. Mode cycling
    modes = overview.get('suffix_mode_sequence', [])
    has_both = 'A' in modes and 'B' in modes
    checks['mode_cycling'] = {
        'status': 'PASS' if has_both else 'WARN',
        'detail': f"Modes: {''.join(modes)}. Both present: {has_both}"
    }

    # 4. Narrative coverage: fraction of tokens with meaningful glosses
    total_tokens = 0
    glossed_tokens = 0
    ht_tokens = 0
    for tr_list in token_records_all:
        for tok in tr_list:
            total_tokens += 1
            interp = tok.get('interpretive', '')
            if tok.get('is_ht') or tok.get('is_dark_pipeline'):
                ht_tokens += 1
            elif interp and not interp.startswith('[') and interp != '':
                glossed_tokens += 1

    operational_tokens = total_tokens - ht_tokens
    gloss_rate = glossed_tokens / operational_tokens if operational_tokens > 0 else 0
    checks['narrative_coverage'] = {
        'status': 'PASS' if gloss_rate > 0.6 else 'WARN',
        'detail': f"{glossed_tokens}/{operational_tokens} operational tokens glossed "
                  f"({round(gloss_rate * 100)}%). "
                  f"{ht_tokens} HT/UN tokens (identification, not operational)."
    }

    # 5. Overall
    statuses = [c['status'] for c in checks.values()]
    overall = 'COHERENT' if all(s == 'PASS' for s in statuses) else 'PARTIAL'
    checks['overall'] = overall

    return checks


# ---------------------------------------------------------------------------
# Output: JSON
# ---------------------------------------------------------------------------

def build_json_output(ctx, overview, line_records, token_records_all, narrative, coherence):
    """Build the full JSON output."""
    return {
        'meta': {
            'phase': 'PARAGRAPH_READING',
            'phase_number': 443,
            'version': '1.0',
            'folio': ctx['folio'],
            'paragraph': overview['paragraph_id'],
            'tier': 3,
            'date': str(date.today()),
            'provenance': [
                'C932 (spec->exec gradient)',
                'C961 (WORK unordered)',
                'C855 (parallel programs)',
                'C1229-C1232 (suffix mode cycling)',
                'C1233 (cross-line independence)',
                'C1237 (paragraph termination by -am)',
                'C1240 (-am trigger context)',
            ]
        },
        'context': ctx,
        'paragraph_overview': overview,
        'lines': line_records,
        'paragraph_narrative': narrative,
        'coherence_assessment': coherence,
    }


# ---------------------------------------------------------------------------
# Output: Markdown
# ---------------------------------------------------------------------------

def build_markdown_output(ctx, overview, line_records, token_records_all, narrative, coherence):
    """Build the human-readable markdown output."""
    lines = []
    pid = overview['paragraph_id']
    folio = ctx['folio']

    lines.append(f"# Paragraph Reading: {folio}:{pid}")
    lines.append("")
    lines.append("**Tier:** 3 (Interpretive, grounded in Tier 0-2 structure)")
    lines.append("")

    # Context
    lines.append("## Context")
    lines.append(f"- **Folio:** {folio}")
    lines.append(f"- **Section:** {ctx.get('section', '?')}")
    lines.append(f"- **REGIME:** {ctx.get('regime', '?')}")
    lines.append(f"- **Archetype:** {ctx.get('archetype', '?')}")
    fk = ctx.get('folio_kernel', {})
    if fk:
        lines.append(f"- **Folio kernel:** {', '.join(f'{k}={v}%' for k, v in sorted(fk.items()))}")
    lines.append("")

    # Paragraph overview
    lines.append("## Paragraph Overview")
    lines.append(f"- **{pid}:** {overview['line_count']} lines, {overview['token_count']} tokens")
    lines.append(f"- **Boundary:** {overview.get('boundary_token', '?')}-gallows")
    kb = overview.get('kernel_balance', {})
    if kb:
        lines.append(f"- **Kernel:** {', '.join(f'{k}={v}%' for k, v in sorted(kb.items()))} ({overview.get('kernel_character', '')})")
    modes = overview.get('suffix_mode_sequence', [])
    interleave = overview.get('mode_interleave_rate', 0)
    if modes:
        lines.append(f"- **Suffix modes:** {''.join(modes)} ({round(interleave * 100)}% interleave)")
    zones = overview.get('zone_distribution', {})
    if zones:
        lines.append(f"- **Zones:** {', '.join(f'{k}={v}' for k, v in zones.items())}")
    gradient = overview.get('gradient_direction')
    if gradient:
        lines.append(f"- **Gradient:** {gradient}")
    tail = overview.get('tail_product_signature')
    if tail:
        lines.append(f"- **Tail:** {tail}")
    lines.append("")

    # Line-by-line reading
    lines.append("## Line-by-Line Reading")
    lines.append("")
    for lr in line_records:
        lid = lr['line_id']
        zone = lr.get('paragraph_zone', 'BODY')
        mode = lr.get('suffix_mode', '?')
        lines.append(f"### L{lid} [{zone}] Mode {mode}")
        lines.append("")
        lines.append(lr['narrative'])
        lines.append("")

        # Token table
        lines.append("| # | Token | Morphology | Gloss |")
        lines.append("|---|-------|------------|-------|")
        for i, tok in enumerate(lr['tokens'], 1):
            word = tok['word']
            p = tok.get('prefix') or ''
            m = tok.get('middle') or ''
            s = tok.get('suffix') or ''
            morph_str = f"{p}:{m}.{s}" if s else f"{p}:{m}"
            interp = tok.get('interpretive', '')
            # Escape pipe chars for markdown
            interp = interp.replace('|', '\\|')
            lines.append(f"| {i} | {word} | {morph_str} | {interp} |")
        lines.append("")

    # Process narrative
    lines.append("## Process Narrative")
    lines.append("")
    lines.append(narrative)
    lines.append("")

    # Coherence assessment
    lines.append("## Coherence Assessment")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|-------|--------|--------|")
    for key, val in coherence.items():
        if key == 'overall':
            continue
        status = val['status']
        detail = val['detail'].replace('|', '\\|')
        lines.append(f"| {key} | {status} | {detail} |")
    lines.append("")
    lines.append(f"**Overall:** {coherence.get('overall', '?')}")
    lines.append("")

    # Provenance
    lines.append("## Provenance")
    lines.append("")
    lines.append("- C932: Spec -> exec gradient")
    lines.append("- C961: WORK zone unordered (concurrent operations)")
    lines.append("- C855: Paragraphs are parallel programs")
    lines.append("- C1229-C1232: Suffix mode cycling")
    lines.append("- C1233: Cross-line independence")
    lines.append("- C1237: Paragraph termination by -am")
    lines.append("- C1240: -am trigger context (cooling-verified shutdown)")
    lines.append("")

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Phase 443: Read a paragraph')
    parser.add_argument('--folio', required=True, help='Folio ID (e.g., f34r)')
    parser.add_argument('--para', required=True, type=int, help='Paragraph number (1-based)')
    parser.add_argument('--json-only', action='store_true', help='JSON output only')
    parser.add_argument('--md-only', action='store_true', help='Markdown output only')
    args = parser.parse_args()

    folio = args.folio
    para_num = args.para

    print(f"Reading {folio}:P{para_num}...")

    # Initialize
    decoder = BFolioDecoder()
    td = TokenDictionary()
    md = MiddleDictionary()

    # Stage 1: Structural analysis
    para = get_paragraph(decoder, folio, para_num)
    ctx = extract_context(decoder, folio, para)
    overview = extract_para_overview(para)

    print(f"  {overview['line_count']} lines, {overview['token_count']} tokens")
    print(f"  Section: {ctx.get('section')}, REGIME: {ctx.get('regime')}")

    # Stage 2 + 3: Annotate lines and compose narratives
    line_records = []
    token_records_all = []

    for line_idx, la in enumerate(para.lines):
        ir, token_annotations = annotate_line(la, decoder, md)
        narrative = compose_line_narrative(la, ir, token_annotations, md)

        lr = {
            'line_id': la.line_id,
            'paragraph_zone': la.paragraph_zone,
            'suffix_mode': la.suffix_mode,
            'token_count': len(la.tokens),
            'kernel_summary': ir.kernel_summary,
            'ht_count': len(ir.ht_tokens),
            'work_en_chsh_count': len(ir.work_en_chsh),
            'work_en_qo_count': len(ir.work_en_qo),
            'work_ax_count': len(ir.work_ax),
            'check_count': len(ir.check_tokens),
            'fl_count': len(ir.fl_tokens),
            'setup_count': len(ir.setup_tokens),
            'close_count': len(ir.close_tokens),
            'narrative': narrative,
            'tokens': token_annotations,
        }
        line_records.append(lr)
        token_records_all.append(token_annotations)

        zone_tag = la.paragraph_zone or 'BODY'
        mode_tag = la.suffix_mode or '?'
        print(f"  L{la.line_id} [{zone_tag}] Mode {mode_tag}: {len(la.tokens)} tokens")

    # Stage 4: Paragraph narrative
    narrative = compose_paragraph_narrative(ctx, overview, line_records)
    print(f"\nNarrative:\n  {narrative}\n")

    # Stage 5: Coherence assessment
    coherence = assess_coherence(overview, line_records, token_records_all)
    print(f"Coherence: {coherence['overall']}")
    for key, val in coherence.items():
        if key != 'overall':
            print(f"  {key}: {val['status']} - {val['detail']}")

    # Output
    out_dir = ROOT / 'phases' / 'PARAGRAPH_READING' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)

    pid = overview['paragraph_id']
    base = f"{folio}_{pid}_reading"

    if not args.md_only:
        json_out = build_json_output(ctx, overview, line_records, token_records_all,
                                     narrative, coherence)
        json_path = out_dir / f"{base}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_out, f, indent=2, ensure_ascii=False)
        print(f"\nJSON: {json_path}")

    if not args.json_only:
        md_out = build_markdown_output(ctx, overview, line_records, token_records_all,
                                       narrative, coherence)
        md_path = out_dir / f"{base}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_out)
        print(f"Markdown: {md_path}")


if __name__ == '__main__':
    main()
