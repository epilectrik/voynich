"""
Phase 610: Extract structured folio data for close reading.

Produces human-readable text dumps of selected Stars folios
with full morphological, atom-level, and categorical annotation.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BASE))

from scripts.voynich import (
    Transcript, Morphology, CategoryClassifier, decompose_middle_hmt, BFolioDecoder
)

DATA_DIR = BASE / 'phases' / 'STARS_FOLIO_CLOSE_READING' / 'data'

TARGETS = ['f104r', 'f108v', 'f107v']

tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()
analyzer = BFolioDecoder()

ATOM_GLOSSES = CategoryClassifier.ATOM_GLOSSES
ATOM_TO_CAT = CategoryClassifier.ATOM_TO_CATEGORY

KERNEL_CHARS = {'k', 'h', 'e'}


def get_kernel(middle):
    """Return kernel character(s) in MIDDLE, or None."""
    if not middle:
        return None
    found = [c for c in middle if c in KERNEL_CHARS]
    return ','.join(found) if found else None


def extract_folio(folio_id):
    """Extract full annotated token dump for a folio."""
    tokens = [t for t in tx.currier_b() if t.folio == folio_id]
    if not tokens:
        return f"No tokens found for {folio_id}"

    # Group by line
    lines = defaultdict(list)
    for t in tokens:
        lines[t.line].append(t)

    # Get paragraph analysis
    paragraphs = analyzer.analyze_folio_paragraphs(folio_id)
    # Map line_id -> paragraph that starts on this line
    para_boundaries = {}
    for p in paragraphs:
        if p.lines:
            first_line_id = p.lines[0].line_id
            para_boundaries[first_line_id] = p

    # Get folio summary
    folio_analysis = analyzer.analyze_folio(folio_id)

    output = []
    output.append(f"{'=' * 80}")
    output.append(f"FOLIO {folio_id} — {len(tokens)} tokens, {len(lines)} lines, {len(paragraphs)} paragraphs")
    output.append(f"Section: Stars")
    if folio_analysis:
        output.append(f"Kernel balance: {folio_analysis.kernel_balance}")
        kt = sum(folio_analysis.kernel_dist.values())
        if kt > 0:
            kp = 100 * folio_analysis.kernel_dist.get('k', 0) / kt
            hp = 100 * folio_analysis.kernel_dist.get('h', 0) / kt
            ep = 100 * folio_analysis.kernel_dist.get('e', 0) / kt
            output.append(f"Kernel distribution: k={kp:.1f}% h={hp:.1f}% e={ep:.1f}%")
        if hasattr(folio_analysis, 'regime') and folio_analysis.regime:
            output.append(f"REGIME: {folio_analysis.regime}")
        output.append(f"Material: {folio_analysis.material_category}")
        output.append(f"Output: {folio_analysis.output_category}")
        output.append(f"QO fraction: {folio_analysis.qo_fraction:.1%}")
        output.append(f"Sister ratio (ch/(ch+sh)): {folio_analysis.sister_ratio:.3f}")
        output.append(f"Bridge rate: {folio_analysis.bridge_rate:.1%}")
        output.append(f"Dark rate: {folio_analysis.dark_pipeline_rate:.1%}")
        if folio_analysis.category_profile:
            output.append(f"Category profile:")
            cat_total = sum(folio_analysis.category_profile.values())
            for cat in ['THERMAL', 'FLOW', 'TRANSITION', 'OPERATION',
                        'STAGING', 'CONTAINMENT', 'MARKING', 'MONITORING']:
                count = folio_analysis.category_profile.get(cat, 0)
                pct = 100 * count / cat_total if cat_total > 0 else 0
                if count > 0:
                    output.append(f"  {cat:14s}: {count:4d} ({pct:5.1f}%)")

    output.append(f"{'=' * 80}")
    output.append("")

    # Paragraph summary table
    output.append("PARAGRAPH SUMMARY")
    output.append("-" * 70)
    para_lines = analyzer.paragraph_summary_lines(folio_id)
    output.append("  ID   | G | kernel k/h/e   | role | size      | FL  | mode         | tail")
    output.append("  " + "-" * 65)
    for pl in para_lines:
        output.append(pl)
    output.append("")

    # Line-by-line token dump
    output.append("LINE-BY-LINE TOKEN DUMP")
    output.append("=" * 80)

    sorted_lines = sorted(lines.keys())
    current_para = None

    for line_id in sorted_lines:
        # Check for paragraph boundary
        if line_id in para_boundaries:
            p = para_boundaries[line_id]
            current_para = p
            output.append("")
            output.append(f"{'─' * 80}")
            first_lid = p.lines[0].line_id if p.lines else '?'
            last_lid = p.lines[-1].line_id if p.lines else '?'
            output.append(f"PARAGRAPH {p.paragraph_id} (lines {first_lid}-{last_lid}, "
                          f"{p.line_count}L/{p.token_count}T)")
            if p.boundary_token:
                output.append(f"  Gallows boundary: {p.boundary_token}")
            kt = sum(p.kernel_dist.values())
            if kt > 0:
                kp = 100 * p.kernel_dist.get('k', 0) / kt
                hp = 100 * p.kernel_dist.get('h', 0) / kt
                ep = 100 * p.kernel_dist.get('e', 0) / kt
                output.append(f"  Kernel: k={kp:.1f}% h={hp:.1f}% e={ep:.1f}%")
            if p.category_profile:
                cat_total = sum(p.category_profile.values())
                if cat_total > 0:
                    top_cat = max(p.category_profile, key=p.category_profile.get)
                    output.append(f"  Dominant category: {top_cat} ({100*p.category_profile[top_cat]/cat_total:.0f}%)")
            output.append(f"{'─' * 80}")

        line_tokens = lines[line_id]
        output.append(f"\n  LINE {line_id} ({len(line_tokens)} tokens)")
        output.append(f"  {'─' * 60}")

        for i, t in enumerate(line_tokens):
            m = morph.extract(t.word)
            middle = m.middle if m else ''
            prefix = m.prefix if m else ''
            suffix = m.suffix if m else ''
            artic = m.articulator if m else ''

            # Atom decomposition
            if middle:
                head, mods, term, frame = decompose_middle_hmt(middle)
                # Atom-by-atom gloss
                atom_gloss = '.'.join(ATOM_GLOSSES.get(c, c) for c in middle)
                # Category
                cat = cc.classify(middle)
                cat_str = cat if cat else '?'
                # Kernel
                kern = get_kernel(middle)
                kern_str = f"[{kern}]" if kern else ""
                # HEAD/MOD/TERM
                head_str = f"H:{head}" if head else "H:-"
                mod_str = f"M:{mods}" if mods else "M:-"
                term_str = f"T:{term}" if term != 'bare' else "T:-"
                pos_str = f"{head_str} {mod_str} {term_str}"
            else:
                atom_gloss = ''
                cat_str = '?'
                kern_str = ''
                pos_str = ''

            # Position markers
            pos_mark = ""
            if i == 0:
                pos_mark = " [LINE-INITIAL]"
            if i == len(line_tokens) - 1:
                pos_mark += " [LINE-FINAL]"

            # Format: word | prefix.middle.suffix | atom glosses | category | kernel | HMT | position
            morph_str = f"{artic+'·' if artic else ''}{prefix+'·' if prefix else ''}{middle}{'·'+suffix if suffix else ''}"

            output.append(
                f"    {t.word:16s} | {morph_str:20s} | {atom_gloss:30s} | "
                f"{cat_str:12s} | {kern_str:5s} | {pos_str:20s}{pos_mark}"
            )

    output.append("")
    output.append("=" * 80)
    output.append("END OF FOLIO DUMP")

    return '\n'.join(output)


# ── Main ──
print("Extracting folio data for close reading...")

for folio_id in TARGETS:
    print(f"\n  Extracting {folio_id}...")
    dump = extract_folio(folio_id)
    outpath = DATA_DIR / f'{folio_id}_dump.txt'
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(dump)
    line_count = dump.count('\n')
    print(f"    -> {outpath.name} ({line_count} lines)")

print("\nDone. Files written to phases/STARS_FOLIO_CLOSE_READING/data/")
