"""
Display Currier B folio with configurable output columns.

Usage:
    python scripts/show_b_folio.py f26r              # All columns
    python scripts/show_b_folio.py f26r --no-calc    # Hide calculated gloss
    python scripts/show_b_folio.py f26r --no-manual  # Hide manual gloss
    python scripts/show_b_folio.py f26r --tokens-only # Just tokens
    python scripts/show_b_folio.py f26r --line 3     # Single line
    python scripts/show_b_folio.py f26r --paragraph  # Flowing paragraph view
    python scripts/show_b_folio.py f26r -p --no-color # Paragraph without colors
    python scripts/show_b_folio.py f26r --flow       # Control-flow rendering
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.voynich import BFolioDecoder, TokenDictionary, MiddleDictionary

try:
    from colorama import init, Fore, Style
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

# Rotating colors for token-gloss matching
COLORS = [Fore.CYAN, Fore.YELLOW, Fore.GREEN, Fore.MAGENTA] if HAS_COLOR else []

# FL stage colors for --flow mode
FL_COLORS = {
    'INITIAL': Fore.CYAN,
    'EARLY': Fore.BLUE,
    'MEDIAL': Fore.YELLOW,
    'LATE': Fore.MAGENTA,
    'TERMINAL': Fore.RED,
} if HAS_COLOR else {}


def display_flow(folio_id: str, line_num: int = None, para_num: int = None, use_color: bool = True):
    """Display folio with control-flow rendering: FL stage + operation + suffix semantics."""

    d = BFolioDecoder()

    # Get lines through paragraph analysis (sets paragraph_zone per C932)
    paragraphs = d.analyze_folio_paragraphs(folio_id)
    if para_num:
        paragraphs = [p for p in paragraphs if p.paragraph_id == f"P{para_num}"]
        if not paragraphs:
            print(f"Paragraph {para_num} not found in {folio_id}")
            return
    lines = []
    for p in paragraphs:
        lines.extend(p.lines)

    if not lines:
        print(f"No lines found for {folio_id}")
        return

    if line_num:
        lines = [la for la in lines if la.line_id == str(line_num)]
        if not lines:
            print(f"Line {line_num} not found in {folio_id}")
            return

    color_enabled = use_color and HAS_COLOR and FL_COLORS
    total_count = 0

    # Paragraph structure summary
    all_paras = d.analyze_folio_paragraphs(folio_id)
    para_summary = ", ".join([f"{p.paragraph_id}(L{p.lines[0].line_id}-L{p.lines[-1].line_id})"
                               for p in all_paras if p.lines])

    print(f"\n{'='*100}")
    print(f"FOLIO: {folio_id}  [FLOW VIEW]")
    if para_num:
        print(f"SHOWING: Paragraph {para_num}")
    print(f"STRUCTURE: {para_summary}")
    print(f"{'='*100}")

    # Legend
    if color_enabled:
        print(f"FL markers shown inline as (FL:STAGE) — only on FL-role tokens")
    print()

    for la in lines:
        total_count += len(la.tokens)

        # Build flow rendering with colors
        if color_enabled:
            tok_parts = []
            for tok in la.tokens:
                fg = tok.flow_gloss()
                s = fg['operation']
                # Inline FL marker (colored) — only for FL-role tokens
                if fg['fl_stage']:
                    fl_color = FL_COLORS.get(fg['fl_stage'], '')
                    s += f" {fl_color}{{FL:{fg['fl_stage']}}}{Style.RESET_ALL}"
                # Control-flow label (bright)
                if fg['flow']:
                    s += f" {Style.BRIGHT}[{fg['flow']}]{Style.RESET_ALL}"
                tok_parts.append((s, tok.prefix_phase))

            # Join with zone-aware separators (C961, C964)
            if len(tok_parts) <= 1:
                flow_line = tok_parts[0][0] if tok_parts else ''
            else:
                flow_line = tok_parts[0][0]
                for j in range(1, len(tok_parts)):
                    prev_phase = tok_parts[j-1][1]
                    curr_phase = tok_parts[j][1]
                    sep = ' | ' if prev_phase == 'WORK' and curr_phase == 'WORK' else ' -> '
                    flow_line += sep + tok_parts[j][0]
        else:
            flow_line = la.flow_render()

        # Token row
        token_row = ' '.join(tok.word for tok in la.tokens)

        zone_tag = f" [{la.paragraph_zone}]" if la.paragraph_zone else ""
        print(f"L{la.line_id}{zone_tag}: {flow_line}")
        print(f"    [{token_row}]")
        print()

    print(f"{'='*100}")
    print(f"Total: {total_count} tokens")
    print(f"{'='*100}")


def display_paragraph(folio_id: str, line_num: int = None, para_num: int = None, use_color: bool = True, show_calc: bool = True):
    """Display folio as flowing paragraphs with tokens underneath."""

    d = BFolioDecoder()
    td = TokenDictionary()
    md = MiddleDictionary()

    # Get paragraph structure
    paragraphs = d.analyze_folio_paragraphs(folio_id)

    if para_num:
        # Filter to specific paragraph
        paragraphs = [p for p in paragraphs if p.paragraph_id == f"P{para_num}"]
        if not paragraphs:
            print(f"Paragraph {para_num} not found in {folio_id}")
            print(f"Available paragraphs: {[p.paragraph_id for p in d.analyze_folio_paragraphs(folio_id)]}")
            return
        # Get lines from this paragraph
        lines = []
        for p in paragraphs:
            lines.extend(p.lines)
    else:
        lines = d.analyze_folio_lines(folio_id)

    if not lines:
        print(f"No lines found for {folio_id}")
        return

    if line_num:
        lines = [la for la in lines if la.line_id == str(line_num)]
        if not lines:
            print(f"Line {line_num} not found in {folio_id}")
            return

    glossed_count = 0
    total_count = 0
    color_enabled = use_color and HAS_COLOR and COLORS

    # Show paragraph structure summary
    all_paras = d.analyze_folio_paragraphs(folio_id)
    para_summary = ", ".join([f"{p.paragraph_id}(L{p.lines[0].line_id}-L{p.lines[-1].line_id})"
                               for p in all_paras if p.lines])

    print(f"\n{'='*80}")
    print(f"FOLIO: {folio_id}")
    if para_num:
        print(f"SHOWING: Paragraph {para_num}")
    print(f"STRUCTURE: {para_summary}")
    print(f"{'='*80}\n")

    for la in lines:
        # Build the flowing gloss line with colors
        glosses = []
        structural_glosses = []
        tokens = []

        for i, tok in enumerate(la.tokens):
            total_count += 1

            # Get both glosses
            raw_manual = td.get_gloss(tok.word)

            # Expanded manual gloss (with *middle substitution)
            expanded_manual = tok.interpretive() if raw_manual else None

            # Auto-composed gloss (with MIDDLE dictionary, without whole-token override)
            tok._token_dict = None  # Suppress whole-token gloss (shown on line 1)
            structural = tok.interpretive()
            tok._token_dict = td  # Restore

            if raw_manual:
                glossed_count += 1

            # Build separate lists for manual, structural, and tokens
            manual_display = expanded_manual if expanded_manual else "___"

            # Apply rotating color
            if color_enabled:
                color = COLORS[i % len(COLORS)]
                reset = Style.RESET_ALL
                glosses.append(f"{color}{manual_display}{reset}")
                structural_glosses.append(f"{color}{structural}{reset}")
                tokens.append(f"{color}{tok.word}{reset}")
            else:
                glosses.append(manual_display)
                structural_glosses.append(structural)
                tokens.append(tok.word)

        # Print line: manual gloss, structural (if enabled), tokens
        print(f"L{la.line_id}: {' '.join(glosses)}")
        if show_calc:
            print(f"    {' '.join(structural_glosses)}")
        print(f"    [{' '.join(tokens)}]")
        print()

    print(f"{'='*80}")
    print(f"Total: {total_count} | Glossed: {glossed_count} | Remaining: {total_count - glossed_count}")
    print(f"* = has manual gloss")
    print(f"{'='*80}")


def display_folio(folio_id: str,
                  show_token: bool = True,
                  show_calc: bool = True,
                  show_manual: bool = True,
                  line_num: int = None):
    """Display a B folio with configurable columns."""

    d = BFolioDecoder()
    td = TokenDictionary()

    lines = d.analyze_folio_lines(folio_id)
    if not lines:
        print(f"No lines found for {folio_id}")
        return

    # Filter to specific line if requested
    if line_num:
        lines = [la for la in lines if la.line_id == str(line_num)]
        if not lines:
            print(f"Line {line_num} not found in {folio_id}")
            return

    # Count glossed tokens for summary
    glossed_count = 0
    total_count = 0

    # Header
    print(f"\n{'='*80}")
    print(f"FOLIO: {folio_id}")
    print(f"{'='*80}")

    # Column headers
    headers = []
    if show_token:
        headers.append(f"{'TOKEN':<14}")
    if show_calc:
        headers.append(f"{'CALCULATED':<35}")
    if show_manual:
        headers.append(f"{'MANUAL GLOSS':<30}")
    print(' | '.join(headers))
    print('-' * 80)

    for la in lines:
        print(f"\n[Line {la.line_id}]")

        for tok in la.tokens:
            total_count += 1

            # Get manual gloss
            manual_gloss = td.get_gloss(tok.word)
            if manual_gloss:
                glossed_count += 1

            # Get calculated gloss (temporarily disable dict lookup)
            tok._token_dict = None  # Force fallback
            calc_gloss = tok.interpretive()
            tok._token_dict = td  # Restore

            # Build row
            cols = []
            if show_token:
                cols.append(f"{tok.word:<14}")
            if show_calc:
                cols.append(f"{calc_gloss:<35}")
            if show_manual:
                manual_display = manual_gloss if manual_gloss else "-"
                cols.append(f"{manual_display:<30}")

            print(' | '.join(cols))

    # Summary
    print()
    print(f"{'='*80}")
    print(f"Total tokens: {total_count} | Glossed: {glossed_count} | Remaining: {total_count - glossed_count}")
    print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(description='Display Currier B folio')
    parser.add_argument('folio', help='Folio ID (e.g., f26r)')
    parser.add_argument('--no-token', action='store_true', help='Hide token column')
    parser.add_argument('--no-calc', action='store_true', help='Hide calculated gloss')
    parser.add_argument('--no-manual', action='store_true', help='Hide manual gloss')
    parser.add_argument('--tokens-only', action='store_true', help='Show only tokens')
    parser.add_argument('--line', type=int, help='Show only specific line number')
    parser.add_argument('--paragraph', '-p', action='store_true',
                        help='Flowing paragraph view (gloss + tokens per line)')
    parser.add_argument('--flow', '-f', action='store_true',
                        help='Control-flow view (FL stage + operation + suffix semantics)')
    parser.add_argument('--para', type=int, help='Show only specific paragraph number (1, 2, etc.)')
    parser.add_argument('--no-color', action='store_true', help='Disable color output')

    args = parser.parse_args()

    if args.flow:
        display_flow(args.folio, line_num=args.line, para_num=args.para,
                     use_color=not args.no_color)
        return

    if args.paragraph:
        display_paragraph(args.folio, line_num=args.line, para_num=args.para,
                          use_color=not args.no_color, show_calc=not args.no_calc)
        return

    show_token = not args.no_token
    show_calc = not args.no_calc
    show_manual = not args.no_manual

    if args.tokens_only:
        show_calc = False
        show_manual = False

    display_folio(
        args.folio,
        show_token=show_token,
        show_calc=show_calc,
        show_manual=show_manual,
        line_num=args.line
    )


if __name__ == '__main__':
    main()
