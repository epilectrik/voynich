#!/usr/bin/env python3
"""
Pacemaker script for systematic token annotation.
Supports Currier A (line-by-line), Currier B (line-by-line/paragraph), and AZC (position-by-position) modes.

Usage:
    python annotate_next_line.py              # Show current line/position
    python annotate_next_line.py --next       # Advance and show next
    python annotate_next_line.py --reset      # Reset to beginning
    python annotate_next_line.py --mode azc   # Switch to AZC mode
    python annotate_next_line.py --mode a     # Switch to Currier A mode
    python annotate_next_line.py --mode b     # Switch to Currier B mode

Paragraph Mode (Currier B only):
    python annotate_next_line.py --paragraph-out   # Display paragraph, save expected tokens
    python annotate_next_line.py --paragraph-in    # Validate and save annotations
    python annotate_next_line.py --paragraph-next  # Advance to next paragraph
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import sys
sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript, Morphology, TokenDictionary, FolioNotes

PROJECT_ROOT = Path(__file__).parent.parent
PROGRESS_PATH = PROJECT_ROOT / 'data' / 'annotation_progress.json'
CONTEXT_PATH = PROJECT_ROOT / 'data' / 'annotation_context.txt'
PARAGRAPH_PENDING_PATH = PROJECT_ROOT / 'data' / 'paragraph_pending.json'

# AZC position zones in logical order (interior -> boundary)
AZC_POSITION_ORDER = ['C', 'C1', 'C2', 'R', 'R1', 'R2', 'R3', 'R4', 'S', 'S0', 'S1', 'S2', 'S3', 'P', 'I', 'O', 'X', 'Y']

# Gallows prefixes for paragraph boundary detection (C841: 71.5% of paragraphs start with gallows-initial)
GALLOWS_PREFIXES = {'k', 't', 'p', 'f', 'ck', 'ct', 'cp', 'cf'}


# ============================================================
# PARAGRAPH VALIDATOR CLASS
# ============================================================

class ParagraphValidator:
    """
    Validates that paragraph annotations include all expected tokens.

    Workflow:
    1. --paragraph-out: Extracts paragraph, displays, saves expected tokens
    2. User annotates tokens (adds notes via TokenDictionary)
    3. --paragraph-in: Validates all tokens have notes, then saves progress
    """

    def __init__(self):
        self.pending_path = PARAGRAPH_PENDING_PATH
        self.td = TokenDictionary()

    def save_expected(self, folio, paragraph_num, lines, tokens):
        """Save expected token list for validation."""
        data = {
            'folio': folio,
            'paragraph_num': paragraph_num,
            'lines': lines,  # list of line numbers
            'tokens': [{'word': t.word, 'line': t.line} for t in tokens],
            'token_count': len(tokens),
            'unique_tokens': list(set(t.word for t in tokens)),
            'created': datetime.now().isoformat()
        }
        with open(self.pending_path, 'w') as f:
            json.dump(data, f, indent=2)
        return data

    def load_expected(self):
        """Load expected token list."""
        if not self.pending_path.exists():
            return None
        with open(self.pending_path) as f:
            return json.load(f)

    def clear_expected(self):
        """Clear pending paragraph after successful validation."""
        if self.pending_path.exists():
            self.pending_path.unlink()

    def validate(self, require_notes=True):
        """
        Validate that all expected tokens have been annotated.

        Returns: (success: bool, report: dict)
        """
        expected = self.load_expected()
        if not expected:
            return False, {'error': 'No pending paragraph. Run --paragraph-out first.'}

        # Reload token dictionary to get fresh data
        self.td = TokenDictionary()

        tokens = expected['tokens']
        unique_tokens = expected['unique_tokens']

        # Check each unique token for notes specific to THIS folio
        missing_notes = []
        has_notes = []
        current_folio = expected['folio']

        for word in unique_tokens:
            entry = self.td.get(word)
            has_folio_note = False
            if entry and entry.get('notes'):
                # Check if any note mentions this folio
                for note in entry['notes']:
                    if current_folio in note.get('text', ''):
                        has_folio_note = True
                        break

            if has_folio_note:
                has_notes.append(word)
            else:
                missing_notes.append(word)

        report = {
            'folio': expected['folio'],
            'paragraph_num': expected['paragraph_num'],
            'lines': expected['lines'],
            'total_tokens': expected['token_count'],
            'unique_tokens': len(unique_tokens),
            'tokens_with_notes': len(has_notes),
            'tokens_missing_notes': len(missing_notes),
            'missing_list': missing_notes[:20],  # First 20 for display
            'success': len(missing_notes) == 0 if require_notes else True
        }

        return report['success'], report

    def display_validation_report(self, report):
        """Display validation results."""
        print("=" * 80)
        print("PARAGRAPH VALIDATION REPORT")
        print("=" * 80)
        print()
        print(f"Folio: {report['folio']}, Paragraph: {report['paragraph_num']}")
        print(f"Lines: {report['lines']}")
        print(f"Total tokens: {report['total_tokens']}, Unique: {report['unique_tokens']}")
        print()

        if report['success']:
            print("[SUCCESS] All tokens have been annotated!")
            print()
            print("Run: python scripts/annotate_next_line.py --paragraph-next")
            print("to advance to the next paragraph.")
        else:
            print(f"[INCOMPLETE] {report['tokens_missing_notes']} tokens still need notes.")
            print()
            print("Missing notes for:")
            for word in report['missing_list']:
                print(f"  - {word}")
            if report['tokens_missing_notes'] > 20:
                print(f"  ... and {report['tokens_missing_notes'] - 20} more")
            print()
            print("Add notes with:")
            print("  td = TokenDictionary()")
            print("  td.add_note('TOKEN', 'Your annotation')")
            print("  td.save()")
            print()
            print("Then run: python scripts/annotate_next_line.py --paragraph-in")


def detect_b_paragraphs(folio):
    """
    Detect paragraph boundaries in a B folio using gallows-initial heuristic.

    Returns list of paragraphs, each as dict with:
    - 'lines': list of line numbers
    - 'tokens': list of token objects
    """
    tx = Transcript()
    morph = Morphology()

    # Get all tokens grouped by line
    lines = defaultdict(list)
    for t in tx.currier_b():
        if t.folio == folio and t.line.isdigit():
            lines[int(t.line)].append(t)

    if not lines:
        return []

    sorted_line_nums = sorted(lines.keys())
    paragraphs = []
    current_para = {'lines': [], 'tokens': []}

    for ln in sorted_line_nums:
        line_tokens = lines[ln]
        if not line_tokens:
            continue

        # Check if line starts a new paragraph (gallows-initial)
        first_word = line_tokens[0].word
        m = morph.extract(first_word)
        is_gallows_initial = m.prefix in GALLOWS_PREFIXES if m.prefix else False

        # Also check for explicit paragraph marker in transcript (rare)
        # Start new paragraph if gallows-initial AND not first line of folio
        if is_gallows_initial and current_para['lines']:
            # Save current paragraph
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'lines': [], 'tokens': []}

        current_para['lines'].append(ln)
        current_para['tokens'].extend(line_tokens)

    # Don't forget the last paragraph
    if current_para['tokens']:
        paragraphs.append(current_para)

    return paragraphs


def get_b_paragraph_tokens(folio, paragraph_num):
    """Get tokens for a specific paragraph in a B folio."""
    paragraphs = detect_b_paragraphs(folio)
    if paragraph_num < 1 or paragraph_num > len(paragraphs):
        return None
    return paragraphs[paragraph_num - 1]


def display_b_paragraph(folio, paragraph_num, paragraph_data, total_paragraphs):
    """Display formatted output for paragraph-level B annotation."""
    morph = Morphology()
    td = TokenDictionary()

    print("=" * 80)
    print(f"CURRIER B PARAGRAPH ANNOTATION - {folio} - Paragraph {paragraph_num}/{total_paragraphs}")
    print("=" * 80)
    print()

    lines = paragraph_data['lines']
    tokens = paragraph_data['tokens']

    print(f"Lines: {lines[0]}-{lines[-1]} ({len(lines)} lines, {len(tokens)} tokens)")
    print()

    # Show tokens grouped by line
    print("-" * 80)
    line_tokens = defaultdict(list)
    for t in tokens:
        line_tokens[int(t.line)].append(t)

    for ln in sorted(line_tokens.keys()):
        token_words = " ".join(t.word for t in line_tokens[ln])
        print(f"Line {ln:2d}: {token_words}")
    print("-" * 80)
    print()

    # Helper to check for folio-specific note
    def has_folio_note(entry, folio):
        if not entry or not entry.get('notes'):
            return False
        for note in entry['notes']:
            if folio in note.get('text', ''):
                return True
        return False

    # Token summary
    unique_tokens = list(set(t.word for t in tokens))
    annotated = sum(1 for w in unique_tokens if has_folio_note(td.get(w), folio))

    print(f"Unique tokens: {len(unique_tokens)}, Annotated for {folio}: {annotated}")
    print()

    # List all unique tokens with status
    print("TOKEN LIST:")
    for i, word in enumerate(sorted(unique_tokens), 1):
        m = morph.extract(word)
        entry = td.get(word)
        status = "[DONE]" if has_folio_note(entry, folio) else "[TODO]"
        role = entry.get('role', {}).get('primary', '?') if entry else '?'
        print(f"  {i:3d}. {status} {word:20s} PREFIX={m.prefix or '-':6s} MIDDLE={m.middle or '-':10s} SUFFIX={m.suffix or '-':4s} ROLE={role}")

    print()
    print("-" * 80)
    print("PARAGRAPH ANNOTATION WORKFLOW:")
    print("1. Analyze tokens in context of the paragraph")
    print("2. Add notes: td.add_note('token', 'analysis'); td.save()")
    print("3. Validate: python scripts/annotate_next_line.py --paragraph-in")
    print("4. If valid, advance: python scripts/annotate_next_line.py --paragraph-next")
    print("-" * 80)
    print()

    # Paragraph-level structural notes
    print("PARAGRAPH CONTEXT:")
    print("- Check for hazard adjacencies across line boundaries")
    print("- Note kernel access patterns (k/h/e operators)")
    print("- Identify LINK boundaries (monitoring vs intervention)")
    print("- Look for FL clustering (escape routes)")
    print("- Consider paragraph's role: identification? processing? terminal?")
    print("=" * 80)

    # Last paragraph warning
    if paragraph_num == total_paragraphs:
        print()
        print("!" * 80)
        print("!!! LAST PARAGRAPH OF FOLIO !!!")
        print("!")
        print("! After annotating this paragraph:")
        print("!   1. Validate: python scripts/annotate_next_line.py --paragraph-in")
        print("!   2. Add folio notes to folio_notes.json:")
        print(f"!      fn = FolioNotes(); fn.add_note('{folio}', 'observation'); fn.save()")
        print("!   3. Add cross-folio patterns to annotation_context.txt Section 43")
        print("!   4. Advance: python scripts/annotate_next_line.py --paragraph-next")
        print("!")
        print("! The next --paragraph-next will complete this folio and move to the next.")
        print("!" * 80)


def get_currier_a_folios():
    """Get all Currier A folios in manuscript order."""
    import re
    tx = Transcript()
    folios = sorted(set(t.folio for t in tx.currier_a()),
                    key=lambda f: (int(re.search(r'\d+', f).group()), f))
    return folios


def get_azc_folios():
    """Get all AZC folios in manuscript order."""
    import re
    tx = Transcript()
    folios = sorted(set(t.folio for t in tx.azc()),
                    key=lambda f: (int(re.search(r'\d+', f).group()), f))
    return folios


def get_currier_b_folios():
    """Get all Currier B folios in manuscript order."""
    import re
    tx = Transcript()
    folios = sorted(set(t.folio for t in tx.currier_b()),
                    key=lambda f: (int(re.search(r'\d+', f).group()), f))
    return folios


def get_azc_folio_positions(folio):
    """Get all positions present in a folio, ordered."""
    tx = Transcript()
    positions = set()
    for t in tx.azc():
        if t.folio == folio:
            positions.add(t.placement)
    # Sort by AZC_POSITION_ORDER, then alphabetically for unknowns
    def pos_key(p):
        if p in AZC_POSITION_ORDER:
            return (AZC_POSITION_ORDER.index(p), p)
        return (999, p)
    return sorted(positions, key=pos_key)


def load_progress():
    if PROGRESS_PATH.exists():
        with open(PROGRESS_PATH) as f:
            return json.load(f)
    # Default to Currier A
    folios = get_currier_a_folios()
    return {
        'current_folio': folios[0],
        'current_line': 1,
        'current_position': None,  # For AZC mode
        'mode': 'currier_a',
        'lines_completed': 0,
        'positions_completed': 0,  # For AZC mode
        'tokens_annotated': 0,
        'folios_completed': [],
        'azc_folios_completed': [],  # Separate tracking for AZC
        'last_updated': None
    }


def init_azc_progress():
    """Initialize progress for AZC mode."""
    folios = get_azc_folios()
    first_folio = folios[0] if folios else None
    first_positions = get_azc_folio_positions(first_folio) if first_folio else []
    return {
        'current_folio': first_folio,
        'current_line': None,
        'current_position': first_positions[0] if first_positions else None,
        'mode': 'azc',
        'lines_completed': 0,
        'positions_completed': 0,
        'tokens_annotated': 0,
        'folios_completed': [],
        'azc_folios_completed': [],
        'last_updated': None
    }


def save_progress(progress):
    progress['last_updated'] = datetime.now().isoformat()
    with open(PROGRESS_PATH, 'w') as f:
        json.dump(progress, f, indent=2)


def get_line_tokens(folio, line_num):
    """Get all tokens for a specific folio/line."""
    tx = Transcript()
    return [t for t in tx.currier_a()
            if t.folio == folio and t.line == str(line_num)]


def get_max_line(folio):
    """Get highest line number in folio."""
    tx = Transcript()
    lines = [int(t.line) for t in tx.currier_a()
             if t.folio == folio and t.line.isdigit()]
    return max(lines) if lines else 0


def get_all_folio_lines(folio):
    """Get all lines in a folio as a dict of line_num -> [words]."""
    tx = Transcript()
    lines = defaultdict(list)
    for t in tx.currier_a():
        if t.folio == folio and t.line.isdigit():
            lines[int(t.line)].append(t.word)
    return lines


# ============================================================
# CURRIER B-SPECIFIC FUNCTIONS
# ============================================================

def get_b_line_tokens(folio, line_num):
    """Get all tokens for a specific Currier B folio/line."""
    tx = Transcript()
    return [t for t in tx.currier_b()
            if t.folio == folio and t.line == str(line_num)]


def get_b_max_line(folio):
    """Get highest line number in Currier B folio."""
    tx = Transcript()
    lines = [int(t.line) for t in tx.currier_b()
             if t.folio == folio and t.line.isdigit()]
    return max(lines) if lines else 0


def get_b_all_folio_lines(folio):
    """Get all lines in a Currier B folio as a dict of line_num -> [words]."""
    tx = Transcript()
    lines = defaultdict(list)
    for t in tx.currier_b():
        if t.folio == folio and t.line.isdigit():
            lines[int(t.line)].append(t.word)
    return lines


def init_currier_b_progress():
    """Initialize progress for Currier B mode."""
    folios = get_currier_b_folios()
    return {
        'current_folio': folios[0] if folios else None,
        'current_line': 1,
        'current_position': None,
        'mode': 'currier_b',
        'lines_completed': 0,
        'positions_completed': 0,
        'tokens_annotated': 0,
        'folios_completed': [],
        'azc_folios_completed': [],
        'b_folios_completed': [],
        'last_updated': None
    }


def display_b_folio_context(folio, current_line):
    """Display full Currier B folio content for context."""
    lines = get_b_all_folio_lines(folio)
    td = TokenDictionary()

    print("=" * 80)
    print(f"CURRIER B FOLIO CONTEXT: {folio} ({len(lines)} lines)")
    print("=" * 80)
    print()

    # Count tokens by annotation status
    all_tokens = set()
    annotated = set()
    for line_tokens in lines.values():
        for word in line_tokens:
            all_tokens.add(word)
            entry = td.get(word)
            if entry and entry.get('notes'):
                annotated.add(word)

    print(f"Unique tokens: {len(all_tokens)}, Already annotated: {len(annotated)}")
    print()

    # Display all lines with marker for current line
    for ln in sorted(lines.keys()):
        marker = ">>>" if ln == current_line else "   "
        line_text = " ".join(lines[ln])
        print(f"{marker} Line {ln:2d}: {line_text}")

    print()
    print("-" * 80)
    print("CURRIER B STRUCTURAL CONTEXT:")
    print("- B is the EXECUTION GRAMMAR (49 instruction classes)")
    print("- Kernel primitives: k (ENERGY), h (PHASE), e (STABILITY)")
    print("- 17 forbidden transitions (hazards) - check adjacency")
    print("- LINK operator marks monitoring/intervention boundary")
    print("- Line = control block, Folio = program")
    print("- See context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml")
    print("-" * 80)
    print()


def display_b_line(tokens, folio, line_num, max_line):
    """Display formatted output for Currier B annotation."""
    morph = Morphology()
    td = TokenDictionary()

    print("=" * 80)
    print(f"CURRIER B ANNOTATION - LINE {line_num} of {max_line} ({folio})")
    print("=" * 80)
    print()

    # Token list
    token_words = [t.word for t in tokens]
    print(f"TOKENS: {' | '.join(token_words)}")
    print()
    print("-" * 80)

    # Each token detail
    for i, token in enumerate(tokens, 1):
        m = morph.extract(token.word)
        entry = td.get(token.word)

        print(f"TOKEN {i}: {token.word}")
        print(f"  Morphology: PREFIX={m.prefix}, MIDDLE={m.middle}, SUFFIX={m.suffix}")

        if entry:
            systems = '/'.join(entry['systems'])
            total = entry['distribution']['total']
            print(f"  Systems: {systems} ({total} occurrences)")

            # Show role classification
            role = entry.get('role', {})
            primary = role.get('primary', 'UNKNOWN')
            subrole = role.get('subrole')
            role_str = f"{primary}" + (f"/{subrole}" if subrole else "")
            print(f"  Role: {role_str}")

            # Show B-specific data
            b_data = entry.get('currier_b', {})
            if b_data:
                regime = b_data.get('regime', 'unknown')
                instruction_class = b_data.get('instruction_class', 'unknown')
                print(f"  B Regime: {regime}, Instruction class: {instruction_class}")

            notes = entry.get('notes', [])
            if notes:
                print(f"  Notes:")
                for n in notes:
                    print(f"    - [{n['date']}] {n['text']}")
            else:
                print(f"  Notes: (none)")
        print()

    print("-" * 80)
    print("CURRIER B ANNOTATION GUIDANCE:")
    print("- Check instruction class (49 classes, 9.8x compression)")
    print("- Check for hazard adjacency (17 forbidden transitions)")
    print("- Note kernel access (k/h/e operators)")
    print("- Note LINK presence (monitoring/intervention boundary)")
    print("- Consider escape paths (FL tokens = recovery routes)")
    print()
    print("KEY CONSTRAINTS:")
    print("- C121: 49 instruction classes")
    print("- C109: 5 hazard classes (PHASE_ORDERING dominant)")
    print("- C105: e = STABILITY_ANCHOR (54.7% recovery)")
    print("- BCSC: currierB.bcsc.yaml for full grammar")
    print()
    print("INSTRUCTIONS:")
    print("1. Analyze token role in execution grammar")
    print("2. Add notes: td.add_note('token', 'analysis'); td.save()")
    print("3. When done: python scripts/annotate_next_line.py --next")
    print("=" * 80)

    # Last line warning
    if line_num == max_line:
        print()
        print("!" * 80)
        print("!!! LAST LINE OF FOLIO !!!")
        print("!")
        print("! After annotating this line:")
        print("!   1. Add folio notes (HT count, patterns, observations)")
        print("!   2. Run --next to advance to the NEXT FOLIO")
        print("!")
        print("! DO NOT batch multiple folios together.")
        print("! DO NOT skip the pacemaker workflow.")
        print("! Process ONE LINE at a time, ONE FOLIO at a time.")
        print("!" * 80)


def display_b_folio_complete(folio):
    """Display Currier B folio completion prompt."""
    fn = FolioNotes()
    lines = get_b_all_folio_lines(folio)
    td = TokenDictionary()

    print()
    print("=" * 80)
    print(f"CURRIER B FOLIO COMPLETE: {folio}")
    print("=" * 80)
    print()

    # Cross-folio context reminder
    print("!" * 80)
    print("! CROSS-FOLIO CONTEXT: Did you notice any structural patterns?")
    print("! If so, add a brief note to: data/annotation_context.txt")
    print("! Section 43: DISCOVERED PATTERNS")
    print("!")
    print("! Good notes: 'f105r: Heavy QO-lane, FL clusters lines 8-12'")
    print("! Bad notes: Long verbose descriptions (causes bloat)")
    print("!" * 80)
    print()

    # Show folio summary
    all_tokens = set()
    for line_tokens in lines.values():
        all_tokens.update(line_tokens)

    print(f"Lines: {len(lines)}, Unique tokens: {len(all_tokens)}")
    print()

    # Show existing folio notes if any
    existing = fn.get(folio)
    if existing and existing.get('notes'):
        print("Existing folio notes:")
        for n in existing['notes']:
            print(f"  - [{n['date']}] {n['text']}")
        print()

    # Re-display full folio for final review
    print("FULL FOLIO CONTENT:")
    for ln in sorted(lines.keys()):
        line_text = " ".join(lines[ln])
        print(f"  Line {ln:2d}: {line_text}")

    print()
    print("-" * 80)
    print("CURRIER B FOLIO OBSERVATIONS:")
    print("- Program structure (what does this folio's 'program' do?)")
    print("- Hazard density (many forbidden adjacencies or clean?)")
    print("- Kernel access patterns (k/h/e distribution)")
    print("- LINK boundaries (where is monitoring vs intervention?)")
    print("- Escape clustering (FL tokens = recovery routes)")
    print("- State convergence (trending toward STATE-C?)")
    print()
    print("Add folio notes via:")
    print(f"  fn = FolioNotes()")
    print(f"  fn.add_note('{folio}', 'Your observation here')")
    print(f"  fn.save()")
    print()
    print("Then run: python scripts/annotate_next_line.py --next")
    print("=" * 80)


def advance_b_progress(progress):
    """Move to next line or next folio in Currier B mode."""
    folio = progress['current_folio']
    line = progress['current_line']
    max_line = get_b_max_line(folio)

    if line < max_line:
        progress['current_line'] = line + 1
    else:
        # Folio complete - show observation prompt
        display_b_folio_complete(folio)

        # Mark folio as completed
        if 'b_folios_completed' not in progress:
            progress['b_folios_completed'] = []
        progress['b_folios_completed'].append(folio)

        # Find next folio
        folios = get_currier_b_folios()
        try:
            idx = folios.index(folio)
            if idx + 1 < len(folios):
                progress['current_folio'] = folios[idx + 1]
                progress['current_line'] = 1
            else:
                print("\n*** ALL CURRIER B FOLIOS COMPLETE ***")
                return False
        except ValueError:
            print("\n*** FOLIO NOT IN CURRIER B ***")
            return False

    progress['lines_completed'] += 1
    return True


# ============================================================
# AZC-SPECIFIC FUNCTIONS
# ============================================================

def get_azc_position_tokens(folio, position):
    """Get all tokens for a specific folio/position."""
    tx = Transcript()
    return [t for t in tx.azc()
            if t.folio == folio and t.placement == position]


def get_azc_folio_structure(folio):
    """Get full structure of an AZC folio: position -> [tokens]."""
    tx = Transcript()
    structure = defaultdict(list)
    for t in tx.azc():
        if t.folio == folio:
            structure[t.placement].append(t)
    return structure


def display_azc_folio_context(folio, current_position):
    """Display full AZC folio content for context."""
    structure = get_azc_folio_structure(folio)
    td = TokenDictionary()
    positions = get_azc_folio_positions(folio)

    print("=" * 80)
    print(f"AZC FOLIO CONTEXT: {folio} ({len(positions)} positions)")
    print("=" * 80)
    print()

    # Count tokens by annotation status
    all_tokens = set()
    annotated = set()
    for pos_tokens in structure.values():
        for t in pos_tokens:
            all_tokens.add(t.word)
            entry = td.get(t.word)
            if entry and entry.get('notes'):
                annotated.add(t.word)

    total_tokens = sum(len(toks) for toks in structure.values())
    print(f"Total tokens: {total_tokens}, Unique: {len(all_tokens)}, Already annotated: {len(annotated)}")
    print()

    # Categorize positions by zone type
    center_pos = [p for p in positions if p.startswith('C')]
    ring_pos = [p for p in positions if p.startswith('R')]
    spoke_pos = [p for p in positions if p.startswith('S')]
    para_pos = [p for p in positions if p == 'P']
    other_pos = [p for p in positions if p not in center_pos + ring_pos + spoke_pos + para_pos]

    # Display by zone
    for zone_name, zone_positions in [('CENTER (C)', center_pos),
                                       ('RINGS (R)', ring_pos),
                                       ('SPOKES/BOUNDARY (S)', spoke_pos),
                                       ('PARAGRAPH', para_pos),
                                       ('OTHER', other_pos)]:
        if zone_positions:
            print(f"--- {zone_name} ---")
            for pos in zone_positions:
                tokens = structure.get(pos, [])
                marker = ">>>" if pos == current_position else "   "
                token_words = " ".join(t.word for t in tokens)
                print(f"{marker} {pos:3s} ({len(tokens):2d}): {token_words[:70]}{'...' if len(token_words) > 70 else ''}")
            print()

    print("-" * 80)
    print("AZC STRUCTURAL NOTES:")
    print("- C/C1/C2: Interior center positions (rotation-tolerant)")
    print("- R/R1-R4: Ring positions (progressive restriction, R1->R2->R3 ordering)")
    print("- S/S0-S3: Spoke/boundary positions (no intervention permitted)")
    print("- P: Paragraph text on AZC folio (not diagram)")
    print("- See context/STRUCTURAL_CONTRACTS/azc_activation.act.yaml")
    print("-" * 80)
    print()


def display_azc_position(tokens, folio, position, all_positions):
    """Display formatted output for AZC position annotation."""
    morph = Morphology()
    td = TokenDictionary()

    pos_idx = all_positions.index(position) + 1 if position in all_positions else '?'

    print("=" * 80)
    print(f"AZC ANNOTATION - {folio} - Position {position} ({pos_idx}/{len(all_positions)})")
    print("=" * 80)
    print()

    # Position zone context
    if position.startswith('C'):
        zone_desc = "CENTER - Interior, rotation-tolerant, moderate escape permission"
    elif position.startswith('R'):
        zone_desc = f"RING {position} - Interior, progressive escape restriction"
        if position == 'R3':
            zone_desc += " (ZERO escape at R3)"
    elif position.startswith('S'):
        zone_desc = f"SPOKE/BOUNDARY {position} - No intervention permitted"
    elif position == 'P':
        zone_desc = "PARAGRAPH - Currier A text on AZC folio (not diagram position)"
    else:
        zone_desc = f"Other position type"

    print(f"Zone: {zone_desc}")
    print()

    # Token list
    token_words = [t.word for t in tokens]
    print(f"TOKENS ({len(tokens)}): {' | '.join(token_words)}")
    print()
    print("-" * 80)

    # Each token detail
    for i, token in enumerate(tokens, 1):
        m = morph.extract(token.word)
        entry = td.get(token.word)

        print(f"TOKEN {i}: {token.word}")
        print(f"  Morphology: PREFIX={m.prefix}, MIDDLE={m.middle}, SUFFIX={m.suffix}")

        if entry:
            systems = '/'.join(entry['systems'])
            total = entry['distribution']['total']
            print(f"  Systems: {systems} ({total} occurrences)")

            # Show role classification
            role = entry.get('role', {})
            primary = role.get('primary', 'UNKNOWN')
            subrole = role.get('subrole')
            role_str = f"{primary}" + (f"/{subrole}" if subrole else "")
            print(f"  Role: {role_str}")

            # Show AZC positions from dictionary
            azc_data = entry.get('azc', {})
            all_azc_pos = azc_data.get('positions', [])
            if all_azc_pos:
                print(f"  AZC positions (all folios): {', '.join(all_azc_pos)}")
            by_folio = azc_data.get('by_folio', {})
            if folio in by_folio:
                print(f"  AZC positions (this folio): {', '.join(by_folio[folio])}")

            notes = entry.get('notes', [])
            if notes:
                print(f"  Notes:")
                for n in notes:
                    print(f"    - [{n['date']}] {n['text']}")
            else:
                print(f"  Notes: (none)")
        print()

    print("-" * 80)
    print("AZC ANNOTATION GUIDANCE:")
    print("- Does this token's position match its role (PP should flow to B)?")
    print("- Note positional exclusivity patterns (same MIDDLE, different positions?)")
    print("- Check escape permission gradient (C > R1 > R2 > R3=0, S=0)")
    print("- Record compatibility observations (what appears together?)")
    print()
    print("INSTRUCTIONS:")
    print("1. Analyze each token's positional behavior")
    print("2. Add notes: td.add_note('token', 'analysis'); td.save()")
    print("3. Optionally update AZC position: td.add_azc_position('token', 'folio', 'pos')")
    print("4. When done: python scripts/annotate_next_line.py --next")
    print("=" * 80)

    # Last position warning
    if position == all_positions[-1] if all_positions else False:
        print()
        print("!" * 80)
        print("!!! LAST POSITION OF FOLIO !!!")
        print("!")
        print("! After annotating this position:")
        print("!   1. Add folio notes (patterns, observations)")
        print("!   2. Run --next to advance to the NEXT FOLIO")
        print("!")
        print("! DO NOT batch multiple folios together.")
        print("! DO NOT skip the pacemaker workflow.")
        print("! Process ONE POSITION at a time, ONE FOLIO at a time.")
        print("!" * 80)


def display_azc_folio_complete(folio):
    """Display AZC folio completion prompt."""
    fn = FolioNotes()
    structure = get_azc_folio_structure(folio)

    print()
    print("=" * 80)
    print(f"AZC FOLIO COMPLETE: {folio}")
    print("=" * 80)
    print()

    # Cross-folio context reminder
    print("!" * 80)
    print("! CROSS-FOLIO CONTEXT: Did you notice any structural patterns?")
    print("! If so, add a brief note to: data/annotation_context.txt")
    print("! Section 43: DISCOVERED PATTERNS")
    print("!")
    print("! Keep notes brief: 'f57v: R-positions dominant, S-zone empty'")
    print("!" * 80)
    print()

    # Show folio summary
    positions = get_azc_folio_positions(folio)
    total_tokens = sum(len(toks) for toks in structure.values())
    unique_tokens = len(set(t.word for toks in structure.values() for t in toks))

    print(f"Positions: {len(positions)}, Total tokens: {total_tokens}, Unique: {unique_tokens}")
    print()

    # Show existing folio notes if any
    existing = fn.get(folio)
    if existing and existing.get('notes'):
        print("Existing folio notes:")
        for n in existing['notes']:
            print(f"  - [{n['date']}] {n['text']}")
        print()

    # Re-display structure summary
    print("POSITION SUMMARY:")
    for pos in positions:
        tokens = structure.get(pos, [])
        token_words = " ".join(t.word for t in tokens[:10])
        more = f"... (+{len(tokens)-10})" if len(tokens) > 10 else ""
        print(f"  {pos:3s}: {token_words}{more}")

    print()
    print("-" * 80)
    print("AZC FOLIO OBSERVATIONS:")
    print("- Position distribution (what dominates - C, R, S?)")
    print("- Escape potential (interior-heavy vs boundary-heavy?)")
    print("- Family affinity (Zodiac ordered subscripts vs A/C unordered?)")
    print("- Vocabulary patterns (any position-exclusive MIDDLEs?)")
    print()
    print("Add folio notes via:")
    print(f"  fn = FolioNotes()")
    print(f"  fn.add_note('{folio}', 'Your observation here')")
    print(f"  fn.save()")
    print()
    print("Then run: python scripts/annotate_next_line.py --next")
    print("=" * 80)


def advance_azc_progress(progress):
    """Move to next position or next folio in AZC mode."""
    folio = progress['current_folio']
    position = progress['current_position']
    positions = get_azc_folio_positions(folio)

    if position in positions:
        pos_idx = positions.index(position)
        if pos_idx + 1 < len(positions):
            # Move to next position in same folio
            progress['current_position'] = positions[pos_idx + 1]
            progress['positions_completed'] += 1
            return True

    # Folio complete - show observation prompt
    display_azc_folio_complete(folio)

    # Mark folio as completed
    if folio not in progress['azc_folios_completed']:
        progress['azc_folios_completed'].append(folio)

    # Find next folio
    folios = get_azc_folios()
    try:
        idx = folios.index(folio)
        if idx + 1 < len(folios):
            next_folio = folios[idx + 1]
            next_positions = get_azc_folio_positions(next_folio)
            progress['current_folio'] = next_folio
            progress['current_position'] = next_positions[0] if next_positions else None
            progress['positions_completed'] += 1
            return True
        else:
            print("\n*** ALL AZC FOLIOS COMPLETE ***")
            return False
    except ValueError:
        print("\n*** FOLIO NOT IN AZC ***")
        return False


def display_annotation_context():
    """Display the persistent annotation context file."""
    if CONTEXT_PATH.exists():
        print()
        print("=" * 80)
        print("LOADING ANNOTATION CONTEXT (edit data/annotation_context.txt to update)")
        print("=" * 80)
        with open(CONTEXT_PATH) as f:
            print(f.read())
    else:
        print("(No annotation_context.txt found)")


def display_folio_context(folio, current_line):
    """Display full folio content for context."""
    lines = get_all_folio_lines(folio)
    td = TokenDictionary()

    print("=" * 80)
    print(f"FOLIO CONTEXT: {folio} ({len(lines)} lines)")
    print("=" * 80)
    print()

    # Count tokens by annotation status
    all_tokens = set()
    annotated = set()
    for line_tokens in lines.values():
        for word in line_tokens:
            all_tokens.add(word)
            entry = td.get(word)
            if entry and entry.get('notes'):
                annotated.add(word)

    print(f"Unique tokens: {len(all_tokens)}, Already annotated: {len(annotated)}")
    print()

    # Display all lines with marker for current line
    for ln in sorted(lines.keys()):
        marker = ">>>" if ln == current_line else "   "
        line_text = " ".join(lines[ln])
        print(f"{marker} Line {ln:2d}: {line_text}")

    print()
    print("-" * 80)
    print("STRUCTURAL OBSERVATIONS:")
    print("(Analyze: line-initial patterns, INFRA distribution, escape clustering,")
    print(" record boundaries, unusual tokens, repeated sequences)")
    print("-" * 80)
    print()


def display_line(tokens, folio, line_num, max_line):
    """Display formatted output for AI consumption."""
    morph = Morphology()
    td = TokenDictionary()

    print("=" * 80)
    print(f"CURRIER A ANNOTATION - LINE {line_num} of {max_line} ({folio})")
    print("=" * 80)
    print()

    # Token list
    token_words = [t.word for t in tokens]
    print(f"TOKENS: {' | '.join(token_words)}")
    print()
    print("-" * 80)

    # Each token detail
    for i, token in enumerate(tokens, 1):
        m = morph.extract(token.word)
        entry = td.get(token.word)

        print(f"TOKEN {i}: {token.word}")
        print(f"  Morphology: PREFIX={m.prefix}, MIDDLE={m.middle}, SUFFIX={m.suffix}")

        if entry:
            systems = '/'.join(entry['systems'])
            total = entry['distribution']['total']
            print(f"  Systems: {systems} ({total} occurrences)")

            # Show role classification
            role = entry.get('role', {})
            primary = role.get('primary', 'UNKNOWN')
            subrole = role.get('subrole')
            role_str = f"{primary}" + (f"/{subrole}" if subrole else "")
            print(f"  Role: {role_str}")

            # Show locations summary
            locations = entry.get('locations', [])
            if locations:
                # Show first few locations as preview
                preview = locations[:5]
                more = f" (+{len(locations)-5} more)" if len(locations) > 5 else ""
                print(f"  Locations: {', '.join(preview)}{more}")

            notes = entry.get('notes', [])
            if notes:
                print(f"  Notes:")
                for n in notes:
                    print(f"    - [{n['date']}] {n['text']}")
            else:
                print(f"  Notes: (none)")
        print()

    print("-" * 80)
    print("CONTEXT REMINDERS:")
    print("- Check context/STRUCTURAL_CONTRACTS/currierA.casc.yaml for A structure")
    print("- Check context/CLAIMS/ for constraints (grep by token or MIDDLE)")
    print("- Use RecordAnalyzer for RI/PP/INFRA classification")
    print("- Consider: position in line, morphology patterns, cross-system behavior")
    print()
    print("INSTRUCTIONS:")
    print("1. Analyze each token using context system")
    print("2. Add notes via: td.add_note('token', 'analysis'); td.save()")
    print("3. When done with ALL tokens, run: python scripts/annotate_next_line.py --next")
    print("=" * 80)

    # Last line warning
    if line_num == max_line:
        print()
        print("!" * 80)
        print("!!! LAST LINE OF FOLIO !!!")
        print("!")
        print("! After annotating this line:")
        print("!   1. Add folio notes (patterns, observations)")
        print("!   2. Run --next to advance to the NEXT FOLIO")
        print("!")
        print("! DO NOT batch multiple folios together.")
        print("! DO NOT skip the pacemaker workflow.")
        print("! Process ONE LINE at a time, ONE FOLIO at a time.")
        print("!" * 80)


def display_folio_complete(folio):
    """Display folio completion prompt for observations."""
    fn = FolioNotes()
    lines = get_all_folio_lines(folio)
    td = TokenDictionary()

    print()
    print("=" * 80)
    print(f"FOLIO COMPLETE: {folio}")
    print("=" * 80)
    print()

    # Cross-folio context reminder
    print("!" * 80)
    print("! CROSS-FOLIO CONTEXT: Did you notice any structural patterns?")
    print("! If so, add a brief note to: data/annotation_context.txt")
    print("! Section 43: DISCOVERED PATTERNS")
    print("!")
    print("! Keep notes brief: 'f1r: RI-heavy L1, unusual sa- clustering'")
    print("!" * 80)
    print()

    # Show folio summary
    all_tokens = set()
    for line_tokens in lines.values():
        all_tokens.update(line_tokens)

    print(f"Lines: {len(lines)}, Unique tokens: {len(all_tokens)}")
    print()

    # Show existing folio notes if any
    existing = fn.get(folio)
    if existing and existing.get('notes'):
        print("Existing folio notes:")
        for n in existing['notes']:
            print(f"  - [{n['date']}] {n['text']}")
        print()

    # Re-display full folio for final review
    print("FULL FOLIO CONTENT:")
    for ln in sorted(lines.keys()):
        line_text = " ".join(lines[ln])
        print(f"  Line {ln:2d}: {line_text}")

    print()
    print("-" * 80)
    print("FOLIO OBSERVATIONS PROMPT:")
    print("Before advancing, note any folio-level patterns:")
    print("  - Line-initial token patterns (what starts lines?)")
    print("  - INFRA/escape clustering (where do da-/qo- tokens concentrate?)")
    print("  - Unusual structures (singletons, repetitions, short lines)")
    print("  - Record boundaries (where might paragraphs divide?)")
    print("  - Questions to investigate later")
    print()
    print("Add folio notes via:")
    print(f"  fn = FolioNotes()")
    print(f"  fn.add_note('{folio}', 'Your observation here')")
    print(f"  fn.save()")
    print()
    print("Then run: python scripts/annotate_next_line.py --next")
    print("=" * 80)


def advance_progress(progress):
    """Move to next line or next folio."""
    folio = progress['current_folio']
    line = progress['current_line']
    max_line = get_max_line(folio)

    if line < max_line:
        progress['current_line'] = line + 1
    else:
        # Folio complete - show observation prompt
        display_folio_complete(folio)

        # Mark folio as completed
        progress['folios_completed'].append(folio)

        # Find next folio
        folios = get_currier_a_folios()
        try:
            idx = folios.index(folio)
            if idx + 1 < len(folios):
                progress['current_folio'] = folios[idx + 1]
                progress['current_line'] = 1
            else:
                print("\n*** ALL 114 CURRIER A FOLIOS COMPLETE ***")
                return False
        except ValueError:
            print("\n*** FOLIO NOT IN CURRIER A ***")
            return False

    progress['lines_completed'] += 1
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Pacemaker for systematic token annotation (Currier A, B, AZC)'
    )
    parser.add_argument('--next', action='store_true',
                        help='Advance to next line/position before displaying')
    parser.add_argument('--reset', action='store_true',
                        help='Reset progress to beginning')
    parser.add_argument('--status', action='store_true',
                        help='Show progress status only')
    parser.add_argument('--mode', choices=['a', 'b', 'azc'],
                        help='Switch annotation mode: a=Currier A, b=Currier B, azc=AZC diagrams')
    # Paragraph mode arguments (Currier B only)
    parser.add_argument('--paragraph-out', action='store_true',
                        help='[B mode] Display paragraph and save expected token list')
    parser.add_argument('--paragraph-in', action='store_true',
                        help='[B mode] Validate annotations have all tokens')
    parser.add_argument('--paragraph-next', action='store_true',
                        help='[B mode] Advance to next paragraph after validation')
    parser.add_argument('--paragraph-skip', action='store_true',
                        help='[B mode] Skip validation and advance (use sparingly)')
    args = parser.parse_args()

    if args.reset:
        if PROGRESS_PATH.exists():
            PROGRESS_PATH.unlink()
        print("Progress reset. Run again to start from beginning.")
        return

    progress = load_progress()

    # Handle mode switch
    if args.mode:
        if args.mode == 'azc' and progress['mode'] != 'azc':
            print("Switching to AZC mode...")
            progress = init_azc_progress()
            save_progress(progress)
            print(f"Now annotating AZC folios. Starting at {progress['current_folio']}")
        elif args.mode == 'a' and progress['mode'] != 'currier_a':
            print("Switching to Currier A mode...")
            folios = get_currier_a_folios()
            progress['mode'] = 'currier_a'
            progress['current_folio'] = folios[0]
            progress['current_line'] = 1
            progress['current_position'] = None
            save_progress(progress)
            print(f"Now annotating Currier A folios. Starting at {progress['current_folio']}")
        elif args.mode == 'b' and progress['mode'] != 'currier_b':
            print("Switching to Currier B mode...")
            progress = init_currier_b_progress()
            save_progress(progress)
            print(f"Now annotating Currier B folios. Starting at {progress['current_folio']}")

    if args.status:
        print(f"Mode: {progress['mode']}")
        print(f"Folio: {progress['current_folio']}")
        if progress['mode'] == 'azc':
            print(f"Position: {progress.get('current_position')}")
            print(f"Positions completed: {progress.get('positions_completed', 0)}")
            print(f"AZC folios completed: {len(progress.get('azc_folios_completed', []))}")
        elif progress['mode'] == 'currier_b':
            print(f"Line: {progress['current_line']}")
            print(f"Lines completed: {progress['lines_completed']}")
            print(f"B folios completed: {len(progress.get('b_folios_completed', []))}")
            # Show paragraph info
            folio = progress['current_folio']
            paragraphs = detect_b_paragraphs(folio)
            current_para = progress.get('current_paragraph', 1)
            print(f"Current paragraph: {current_para}/{len(paragraphs)} (use --paragraph-out for paragraph mode)")
        else:
            print(f"Line: {progress['current_line']}")
            print(f"Lines completed: {progress['lines_completed']}")
            print(f"Folios completed: {len(progress.get('folios_completed', []))}")
        return

    # Handle paragraph mode operations (Currier B only)
    if args.paragraph_out or args.paragraph_in or args.paragraph_next or args.paragraph_skip:
        if progress['mode'] != 'currier_b':
            print("ERROR: Paragraph mode is only available in Currier B mode.")
            print("Switch with: python scripts/annotate_next_line.py --mode b")
            return
        main_paragraph_mode(progress, args)
        return

    # Branch based on mode
    if progress['mode'] == 'azc':
        main_azc(progress, args)
    elif progress['mode'] == 'currier_b':
        main_currier_b(progress, args)
    else:
        main_currier_a(progress, args)


def main_currier_a(progress, args):
    """Main flow for Currier A annotation."""
    # Advance first if --next flag
    if args.next:
        if not advance_progress(progress):
            return  # All complete
        save_progress(progress)

    folio = progress['current_folio']
    line = progress['current_line']

    tokens = get_line_tokens(folio, line)
    max_line = get_max_line(folio)

    if not tokens:
        print(f"No tokens found for {folio} line {line}")
        print("Try: python scripts/annotate_next_line.py --next")
        return

    # Show full folio context when starting a new folio
    if line == 1:
        display_annotation_context()
        print()
        print("*** REMINDER: After annotating, remember to make folio notes. ***")
        print("*** Note anything interesting or that needs further investigation. ***")
        print()
        display_folio_context(folio, line)

    display_line(tokens, folio, line, max_line)


def main_currier_b(progress, args):
    """Main flow for Currier B annotation."""
    # Advance first if --next flag
    if args.next:
        if not advance_b_progress(progress):
            return  # All complete
        save_progress(progress)

    folio = progress['current_folio']
    line = progress['current_line']

    tokens = get_b_line_tokens(folio, line)
    max_line = get_b_max_line(folio)

    if not tokens:
        print(f"No tokens found for {folio} line {line}")
        print("Try: python scripts/annotate_next_line.py --next")
        return

    # Show full folio context when starting a new folio
    if line == 1:
        display_annotation_context()
        print()
        print("*** CURRIER B MODE: Annotating execution grammar ***")
        print("*** Remember folio notes after completing each folio. ***")
        print()
        display_b_folio_context(folio, line)

    display_b_line(tokens, folio, line, max_line)


def main_paragraph_mode(progress, args):
    """Handle paragraph-at-a-time annotation for Currier B."""
    validator = ParagraphValidator()
    folio = progress['current_folio']

    # Detect paragraphs for this folio
    paragraphs = detect_b_paragraphs(folio)
    total_paragraphs = len(paragraphs)

    # Get current paragraph number (default to 1 if not set)
    current_para = progress.get('current_paragraph', 1)

    if args.paragraph_out:
        # OUT mode: Display paragraph and save expected tokens
        if current_para > total_paragraphs:
            print(f"No more paragraphs in {folio}. Run --paragraph-next to advance folio.")
            return

        para_data = paragraphs[current_para - 1]

        # Save expected tokens for validation
        validator.save_expected(folio, current_para, para_data['lines'], para_data['tokens'])

        # Display full folio context on first paragraph
        if current_para == 1:
            display_annotation_context()
            print()
            print("*** PARAGRAPH MODE: Annotating Currier B paragraph-by-paragraph ***")
            print()
            display_b_folio_context(folio, para_data['lines'][0])

        # Display paragraph
        display_b_paragraph(folio, current_para, para_data, total_paragraphs)

        print()
        print(f"Expected tokens saved to: {PARAGRAPH_PENDING_PATH}")
        print("After annotating, run: python scripts/annotate_next_line.py --paragraph-in")

    elif args.paragraph_in:
        # IN mode: Validate annotations
        success, report = validator.validate(require_notes=True)
        validator.display_validation_report(report)

        if not success:
            print()
            print("NOTE: If you want to skip validation and move on anyway,")
            print("use: python scripts/annotate_next_line.py --paragraph-skip")

    elif args.paragraph_next or args.paragraph_skip:
        # NEXT mode: Advance after validation (or skip validation)
        if args.paragraph_next:
            success, report = validator.validate(require_notes=True)
            if not success:
                validator.display_validation_report(report)
                print()
                print("Cannot advance until all tokens are annotated.")
                print("To skip validation: python scripts/annotate_next_line.py --paragraph-skip")
                return

        # Clear pending and advance
        validator.clear_expected()

        if current_para < total_paragraphs:
            # Move to next paragraph in same folio
            progress['current_paragraph'] = current_para + 1
            save_progress(progress)
            print(f"Advanced to paragraph {current_para + 1}/{total_paragraphs} in {folio}")
            print("Run: python scripts/annotate_next_line.py --paragraph-out")
        else:
            # Folio complete - show observation prompt
            display_b_folio_complete(folio)

            # Mark folio as completed
            if 'b_folios_completed' not in progress:
                progress['b_folios_completed'] = []
            if folio not in progress['b_folios_completed']:
                progress['b_folios_completed'].append(folio)

            # Find next folio
            folios = get_currier_b_folios()
            try:
                idx = folios.index(folio)
                if idx + 1 < len(folios):
                    progress['current_folio'] = folios[idx + 1]
                    progress['current_paragraph'] = 1
                    progress['current_line'] = 1  # Keep line sync for regular mode
                    save_progress(progress)
                    print(f"\nAdvanced to next folio: {folios[idx + 1]}")
                    print("Run: python scripts/annotate_next_line.py --paragraph-out")
                else:
                    print("\n*** ALL CURRIER B FOLIOS COMPLETE ***")
            except ValueError:
                print("\n*** FOLIO NOT IN CURRIER B ***")


def main_azc(progress, args):
    """Main flow for AZC annotation."""
    # Advance first if --next flag
    if args.next:
        if not advance_azc_progress(progress):
            return  # All complete
        save_progress(progress)

    folio = progress['current_folio']
    position = progress.get('current_position')

    if not folio:
        print("No AZC folio set. Try: python scripts/annotate_next_line.py --mode azc")
        return

    positions = get_azc_folio_positions(folio)

    if not position and positions:
        position = positions[0]
        progress['current_position'] = position
        save_progress(progress)

    tokens = get_azc_position_tokens(folio, position)

    if not tokens:
        print(f"No tokens found for {folio} position {position}")
        print("Try: python scripts/annotate_next_line.py --next")
        return

    # Show full folio context when starting a new folio (first position)
    if position == positions[0] if positions else False:
        display_annotation_context()
        print()
        print("*** AZC MODE: Annotating diagram positions ***")
        print("*** Remember folio notes after completing each folio. ***")
        print()
        display_azc_folio_context(folio, position)

    display_azc_position(tokens, folio, position, positions)


if __name__ == '__main__':
    main()
