#!/usr/bin/env python3
"""
Generate expert-advisor agent with embedded context.

Combines all expert reference materials directly into the agent file
so the expert agent has permanent context without needing to read files.

Includes:
- CLAUDE_INDEX.md (navigation)
- MODEL_CONTEXT.md (architecture)
- CONSTRAINT_TABLE.txt (all constraints)
- FIT_TABLE.txt (all fits)
- INTERPRETATION_SUMMARY.md (Tier 3-4)
- Structural contracts (CASC, BCSC, ACT files)

The generator applies AGENT FILTERS to strip content that is useful in
source files (for humans and file-reading agents) but wastes context
space in the expert-advisor agent which cannot access files.

Usage:
    python generate_expert_context.py              # Generate agent with all documents
    python generate_expert_context.py --compact    # Cognitively compressed (~270KB)
    python generate_expert_context.py --no-contracts  # Exclude structural contracts
    python generate_expert_context.py --legacy     # Also generate EXPERT_CONTEXT.md
    python generate_expert_context.py --no-filter  # Skip agent-specific filtering
"""

import re
from pathlib import Path
from datetime import datetime

CONTEXT_DIR = Path(__file__).parent


def get_counts():
    """Parse constraint count, fit count, and highest constraint ID from index files."""
    constraint_count = 0
    fit_count = 0
    highest_id = "C0000"

    # Parse constraint count from INDEX.md line 3: "**Total:** NNN validated constraints"
    index_file = CONTEXT_DIR / "CLAIMS" / "INDEX.md"
    if index_file.exists():
        first_lines = index_file.read_text(encoding='utf-8').split('\n')[:5]
        for line in first_lines:
            m = re.search(r'\*\*Total:\*\*\s*(\d+)', line)
            if m:
                constraint_count = int(m.group(1))
                break

    # Parse fit count from FIT_TABLE.txt line 4: "# Total: NN fits"
    fit_file = CONTEXT_DIR / "MODEL_FITS" / "FIT_TABLE.txt"
    if fit_file.exists():
        first_lines = fit_file.read_text(encoding='utf-8').split('\n')[:10]
        for line in first_lines:
            m = re.search(r'#\s*Total:\s*(\d+)\s*fits', line)
            if m:
                fit_count = int(m.group(1))
                break

    # Parse highest constraint ID from CONSTRAINT_TABLE.txt
    ct_file = CONTEXT_DIR / "CONSTRAINT_TABLE.txt"
    if ct_file.exists():
        for line in ct_file.read_text(encoding='utf-8').split('\n'):
            m = re.match(r'^(C\d+)\t', line)
            if m:
                highest_id = m.group(1)  # last match wins (file is sorted)

    return constraint_count, fit_count, highest_id


# ============================================================
# AGENT FILTERS
# ============================================================
# These strip content that is useful in source files but wastes
# space in the expert-advisor agent (which cannot read files).

def _strip_file_references(content):
    """Remove **Files:**, **Source:**, and See phases/... lines.

    The expert agent cannot access the filesystem, so file path
    references are pure waste. Handles multi-line Files: blocks.
    """
    lines = content.split('\n')
    filtered = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # Skip **Files:** and continuation lines (indented paths)
        if stripped.startswith('**Files:**') or stripped.startswith('**Source:**'):
            i += 1
            # Skip indented continuation lines (- Phase:, - Results:, etc.)
            while i < len(lines) and lines[i].strip().startswith('- '):
                next_stripped = lines[i].strip()
                # Only skip if it looks like a file path continuation
                if '`' in next_stripped or 'phases/' in next_stripped or 'results/' in next_stripped:
                    i += 1
                else:
                    break
            continue

        # Skip "See phases/..." and "See `phases/..." references
        if re.match(r'^See\s+[`"]?phases/', stripped):
            i += 1
            continue

        # Skip standalone "See [...]" lines pointing to context/ files
        # Also handle lines starting with "> " (blockquotes) before "See"
        clean = re.sub(r'^>\s*', '', stripped)
        if re.match(r'^See\s+\[', clean):
            i += 1
            continue

        # Strip inline "See [...](...)" references mid-sentence
        # e.g. "...frozen. See [SYSTEM/CHANGELOG.md](SYSTEM/CHANGELOG.md) for..."
        if 'See [' in lines[i]:
            lines[i] = re.sub(r'\s*See\s+\[[^\]]*\]\([^)]*\)[^.]*\.?', '', lines[i])

        filtered.append(lines[i])
        i += 1
    return '\n'.join(filtered)


def _strip_claude_index_sections(content, compact=False):
    """Strip sections from CLAUDE_INDEX that are useless to the expert agent.

    Removes:
    - DATA LOADING WARNING (for script-writing agents)
    - Navigation table (for file-reading agents)
    - File Registry (file paths)
    - Automation (tool locations)
    - Context System (progressive disclosure instructions)

    In compact mode, also removes sections duplicated by agent header
    or Architectural Framework:
    - Epistemic Tiers (duplicate tier table — already in agent header)
    - STOP CONDITIONS (covered by MODEL_CONTEXT section III)
    - Default Resolution Policy (references file system agent can't access)
    - Escalation Rule (references file system agent can't access)
    - Structural Analysis vs Interpretive (restates tier discipline)
    - Why Visualization Tools (niche, agent doesn't do visualization)
    """
    sections_to_strip = [
        'DATA LOADING WARNING',
        'Navigation',
        'File Registry',
        'Automation',
        'Context System',
    ]
    if compact:
        sections_to_strip.extend([
            'Epistemic Tiers',
            'STOP CONDITIONS',
            'Default Resolution Policy',
            'Escalation Rule',
            'Structural Analysis vs Interpretive',
            'Why Visualization Tools',
        ])
    lines = content.split('\n')
    filtered = []
    skip_until_next_h2 = False

    for line in lines:
        # Check if this is an ## header
        if line.startswith('## '):
            header_text = line[3:].strip()
            if any(header_text.startswith(s) for s in sections_to_strip):
                skip_until_next_h2 = True
                continue
            else:
                skip_until_next_h2 = False

        if skip_until_next_h2:
            continue

        filtered.append(line)

    return '\n'.join(filtered)


def _strip_yaml_provenance_maps(content):
    """Strip aggregate provenance_map sections from structural contracts.

    The inline provenance: fields on individual entries are sufficient.
    The large provenance_map sections at the end just repeat the same
    constraint numbers in aggregate form.
    """
    lines = content.split('\n')
    filtered = []
    skip_provenance = False

    for line in lines:
        stripped = line.strip()

        # Detect start of provenance, provenance_map, or provenance_summary section
        if stripped in ('provenance:', 'provenance_map:', 'provenance_summary:'):
            skip_provenance = True
            continue

        # Stop skipping when we hit a new top-level key or section divider
        # Check ORIGINAL line for indentation — indented lines are still part of
        # the provenance section; only unindented keys signal a new section
        if skip_provenance:
            is_section_divider = stripped.startswith('# ====')
            is_top_level_key = (stripped and line[0:1] not in (' ', '\t', '')
                                and not stripped.startswith('#')
                                and not stripped.startswith('-')
                                and ':' in stripped)
            if is_section_divider or is_top_level_key:
                skip_provenance = False
            else:
                continue

        filtered.append(line)

    return '\n'.join(filtered)


def _strip_constraint_table_columns(content):
    """Strip LOCATION column from CONSTRAINT_TABLE.txt.

    Keeps NUM, CONSTRAINT, TIER, SCOPE — all needed for reasoning.
    Drops only LOCATION (file paths are useless to the embedded agent).
    Also strips the header lines (count, tier/scope/location legends, column header)
    to avoid count inconsistency — the agent header provides the authoritative count.
    """
    lines = content.split('\n')
    filtered = []
    for line in lines:
        stripped = line.strip()

        # Strip header lines — agent header has authoritative count and legends
        if stripped.startswith('CONSTRAINT_REFERENCE'):
            continue
        if stripped.startswith('TIER:') and '=' in stripped:
            continue
        if stripped.startswith('SCOPE:') and '=' in stripped:
            continue
        if stripped.startswith('LOCATION:') and '=' in stripped:
            continue
        # Strip the column header line (NUM\tCONSTRAINT\tTIER\tSCOPE\tLOCATION)
        if stripped.startswith('NUM\t'):
            continue

        # Skip comment lines and blank lines
        if line.startswith('#') or not stripped:
            filtered.append(line)
            continue

        # TSV lines: NUM | CONSTRAINT | TIER | SCOPE | LOCATION
        # Keep first 4 fields, drop LOCATION
        parts = line.split('\t')
        if len(parts) >= 5:
            filtered.append('\t'.join(parts[:4]))
        elif len(parts) >= 2:
            filtered.append(line)  # Short lines pass through
        else:
            filtered.append(line)

    return '\n'.join(filtered)


def filter_for_agent(content, filename, compact=False):
    """Apply all agent-specific filters to a document before embedding."""
    original_size = len(content)

    # Universal: strip file references from all documents
    content = _strip_file_references(content)

    # Document-specific filters
    if 'CLAUDE_INDEX' in filename:
        content = _strip_claude_index_sections(content, compact=compact)
    elif 'CONSTRAINT_TABLE' in filename:
        content = _strip_constraint_table_columns(content)

    new_size = len(content)
    if original_size != new_size:
        saved = original_size - new_size
        print(f"  Filtered {filename}: {original_size:,} -> {new_size:,} bytes (saved {saved:,})")

    return content


def filter_contract_for_agent(content, filename):
    """Apply agent-specific filters to a structural contract."""
    original_size = len(content)
    content = _strip_yaml_provenance_maps(content)
    new_size = len(content)
    if original_size != new_size:
        saved = original_size - new_size
        print(f"  Filtered {filename}: {original_size:,} -> {new_size:,} bytes (saved {saved:,})")
    return content


# ============================================================
# COMPACT FILTERS
# ============================================================
# Cognitive compression: keep every concept, shrink explanation.
# Preserves interpretive backbone and cross-layer coherence.
# Activated by --compact flag.

# Subsection headers to keep in full when condensing INTERPRETATION_SUMMARY
_INTERP_KEEP_SUBSECTIONS = [
    'Tier ',              # "Tier 2: Core Finding", "Tier 3: ..."
    'Core Finding',
    'What This Does NOT Claim',
    'What This DOES Claim',
    'Cross-References',
    'Constraints Produced',
    'Fits Produced',
    'Evidence Strength Summary',
    'The Three-Text Relationship',
    'Key Structural Findings',
    'Overview',
    'Census',
    'Token Decomposition',
]

# INTERPRETATION_SUMMARY sections to keep in full (already compact)
_INTERP_KEEP_FULL = [
    'Purpose',
    'Frozen Conclusion',
    'Universal Boundaries',
    'II. Process Domain',
    'III. Material Domain',
    'IV. Craft Interpretation',
    'V. Institutional Context',
    'VI. HT Speculative Vocabulary',
    'VII. Program Characteristics',
    'VIII. Limits of Interpretation',
    'IX. Open Questions',
    '0.E.1.',
    '0.H.',
    '0.J.',
    '0.K.',
]

# Sections to heavy-condense (keep headers, blockquotes, constraint refs only)
_INTERP_HEAVY_CONDENSE = [
    'XI.',     # Rosettes Foldout
    'XII.',    # Cross-System Vocabulary Flow
    'XIII.',   # Dark Pipeline
    'XIV.',    # PP Pipeline Atom Decomposition
    'XV.',     # Cross-Lane Content Prediction
    'XVI.',    # 8-Category Operational System
    'XVII.',   # Paragraph Termination
    'XVIII.',  # PREFIX Category Anatomy
    'XIX.',    # Sister Category Mechanism
    'XX.',     # Cross-Mode Category Coupling
    'I.D.',    # MIDDLE Atomic Incompatibility Layer (large tables)
    'I.O.',    # Physical World Reverse Engineering (long detail)
]


def _compact_interpretation_summary(content):
    """Cognitively compress INTERPRETATION_SUMMARY.

    Strategy: Keep every section header + core findings + constraint refs +
    blockquotes + bold definitions + short tables. Remove narrative prose,
    evidence detail, phase attributions, example walkthroughs.

    Section X (Brunschwig, 2096 lines) gets special heavy condensation.
    No section is removed entirely — each keeps its conceptual distillation.
    """
    lines = content.split('\n')
    result = []
    # State: 'full' = keep everything, 'condense' = selective, 'section_x' = heavy condense
    state = 'full'
    in_whitelisted_subsection = False
    table_rows_kept = 0
    consecutive_blank = 0
    x_past_core_finding = False  # For section X: tracks if we've passed the initial blockquotes

    for line in lines:
        stripped = line.strip()

        # Detect ## section headers
        if line.startswith('## '):
            header = line[3:].strip()
            in_whitelisted_subsection = False
            table_rows_kept = 0

            # Always keep the header line
            result.append('')
            result.append(line)

            # Classify section
            if any(header.startswith(k) for k in _INTERP_KEEP_FULL):
                state = 'full'
            elif header.startswith('X. External Alignment') or header.startswith('Navigation'):
                state = 'section_x'
                x_past_core_finding = False
            elif any(header.startswith(k) for k in _INTERP_HEAVY_CONDENSE):
                state = 'heavy_condense'
            else:
                state = 'condense'
            continue

        # FULL: keep everything
        if state == 'full':
            result.append(line)
            continue

        # SECTION X: heavy condensation — keep core finding + summary tables only
        if state == 'section_x':
            # Detect ### subsection headers
            if line.startswith('### '):
                x_past_core_finding = True
                sub_header = line[4:].strip()
                in_whitelisted_subsection = any(
                    sub_header.startswith(k) for k in _INTERP_KEEP_SUBSECTIONS
                )
                if in_whitelisted_subsection:
                    table_rows_kept = 0
                    result.append(line)
                continue

            # Keep whitelisted subsection content (tables + blockquotes)
            if in_whitelisted_subsection:
                if stripped.startswith('|') or stripped == '' or stripped.startswith('>'):
                    result.append(line)
                    continue
                elif stripped and not stripped.startswith('|'):
                    in_whitelisted_subsection = False

            # Before first ### : keep blockquotes (core finding area)
            if not x_past_core_finding and stripped.startswith('>'):
                result.append(line)
                continue

            # Skip everything else in section X
            continue

        # HEAVY CONDENSE: keep headers, blockquotes, and constraint-citing bullets only
        if state == 'heavy_condense':
            # Keep ### subsection headers
            if line.startswith('### '):
                result.append(line)
                consecutive_blank = 0
                continue
            # Keep blockquotes (core findings)
            if stripped.startswith('>'):
                result.append(line)
                consecutive_blank = 0
                continue
            # Keep bullet lines citing constraints
            if stripped.startswith('- ') and re.search(r'C\d{3,4}', stripped):
                result.append(line)
                consecutive_blank = 0
                continue
            # Keep bold standalone definitions
            if stripped.startswith('**') and stripped.endswith('**') and len(stripped) < 120:
                result.append(line)
                consecutive_blank = 0
                continue
            # Keep blank lines (limit to 1 consecutive)
            if stripped == '':
                consecutive_blank += 1
                if consecutive_blank <= 1:
                    result.append('')
                continue
            consecutive_blank = 0
            # Skip everything else (prose, tables, evidence detail)
            continue

        # CONDENSE: selective keep
        if state == 'condense':
            # Detect ### subsection headers
            if line.startswith('### '):
                sub_header = line[4:].strip()
                in_whitelisted_subsection = any(
                    sub_header.startswith(k) for k in _INTERP_KEEP_SUBSECTIONS
                )
                table_rows_kept = 0
                if in_whitelisted_subsection:
                    result.append(line)
                continue

            # Within whitelisted subsection: keep everything
            if in_whitelisted_subsection:
                result.append(line)
                continue

            # Outside whitelisted subsections: keep structural lines only
            # Blockquotes (core findings)
            if stripped.startswith('>'):
                result.append(line)
                continue
            # Bold definitions (only standalone ones, not mid-paragraph)
            if stripped.startswith('**') and stripped.endswith('**') and len(stripped) < 120:
                result.append(line)
                continue
            # Constraint reference lists (bullet points citing constraints)
            if stripped.startswith('- ') and re.search(r'C\d{3,4}', stripped):
                result.append(line)
                continue
            # Table rows (first 4 per table: header + separator + 2 data rows)
            if stripped.startswith('|'):
                table_rows_kept += 1
                if table_rows_kept <= 4:
                    result.append(line)
                continue
            else:
                table_rows_kept = 0
            # Separators
            if stripped == '---':
                result.append(line)
                consecutive_blank = 0
                continue
            # Blank lines (limit to 1 consecutive)
            if stripped == '':
                consecutive_blank += 1
                if consecutive_blank <= 1:
                    result.append('')
                continue
            consecutive_blank = 0

            # Everything else: skip (prose paragraphs, evidence detail, etc.)
            continue

    return '\n'.join(result)


# Patterns that identify etymology/gloss candidate tables (semantic backsliding risk)
_GLOSS_TABLE_PATTERNS = [
    r'\(Ger\.\)',          # German candidate
    r'\(Lat\.\)',          # Latin candidate
    r'German Candidate',   # Table header
    r'Abbreviation.*Meaning.*Confidence',  # Gloss table header
    r'Our Gloss.*German',  # Consonant gloss table
]

_QUARANTINE_WARNING = (
    '> **TIER 4 QUARANTINE:** The following etymology/gloss candidates are speculative '
    'external-language mappings. Do NOT use these for structural answers. Use only when '
    'the user explicitly asks about etymology or external-language alignment. '
    'Structural role is determined by grammar position (C121), not word meaning (C171, C120).'
)


def _quarantine_gloss_tables(content):
    """Insert quarantine warnings before German/Latin etymology tables.

    Detects tables containing gloss/etymology candidates and inserts
    a behavioral guardrail warning. This prevents the model from treating
    Tier 4 speculative language mappings as structural facts.
    """
    lines = content.split('\n')
    result = []
    i = 0
    quarantine_inserted = set()  # Track line indices where we've inserted warnings

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if this line starts a table (pipe character) with gloss patterns
        if stripped.startswith('|') and any(
            re.search(p, stripped) for p in _GLOSS_TABLE_PATTERNS
        ):
            # Check if we already inserted a quarantine for a nearby table
            # (some tables are adjacent — don't duplicate warnings)
            if not any(abs(i - qi) < 5 for qi in quarantine_inserted):
                result.append('')
                result.append(_QUARANTINE_WARNING)
                result.append('')
                quarantine_inserted.add(i)

        result.append(line)
        i += 1

    if quarantine_inserted:
        print(f"  Quarantine: inserted {len(quarantine_inserted)} gloss table warnings")

    return '\n'.join(result)


# MODEL_CONTEXT sections to remove entirely in compact mode
# Sections V-XII: covered by constraint table + contract signatures
# Sections I-III: duplicated by CLAUDE_INDEX (Project Identity, Epistemic Tiers, Stop Conditions)
# Navigation: file-reading artifact
_MC_REMOVE_SECTIONS = [
    'I. PROJECT IDENTITY',
    'II. EPISTEMIC GOVERNANCE',
    'III. MODEL FREEZE',
    'V. GLOBAL MORPHOLOGICAL',
    'VI. CURRIER B',
    'VII. CURRIER A',
    'VIII. AZC',
    'IX. HUMAN TRACK',
    'X. CROSS-SYSTEM',
    'X.B. APPARATUS-CENTRIC',
    'X.C. REPRESENTATION',
    'XI. REJECTED',
    'XII. HISTORICAL',
    'Navigation',
]

# MODEL_CONTEXT ### subsections to remove (file-browsing instructions)
_MC_REMOVE_SUBSECTIONS = [
    'Layered Access',
    'Programmatic Access',
    'Grouped Registries',
]

# MODEL_CONTEXT: within section IV, remove paragraphs that duplicate
# the four-layer table already in CLAUDE_INDEX. Keep Design Freedom subsection.
_MC_IV_KEEP_SUBSECTIONS = [
    'Design Freedom',
    'Critical Distinctions',
]


def _compact_model_context(content):
    """Cognitively compress MODEL_CONTEXT for compact mode.

    Removes:
    - Sections I-III (duplicated by CLAUDE_INDEX Project Identity/Tiers/Stop Conditions)
    - Sections V-XII (covered by constraint table + contract signatures)
    - Navigation (file-reading artifact)
    - File-browsing subsections (Layered Access, Programmatic Access, Grouped Registries)

    Keeps:
    - Section IV Design Freedom subsection + Critical Distinctions
    - Section XIII Methodological Warnings
    - Section XV How to Read Constraints (minus file-browsing subsections)
    - Section XVI Change-Safety Statement
    """
    lines = content.split('\n')
    result = []
    state = 'keep'
    skip_subsection = False

    for line in lines:
        # Detect ## section headers
        if line.startswith('## '):
            header = line[3:].strip()
            skip_subsection = False

            if any(header.startswith(r) for r in _MC_REMOVE_SECTIONS):
                state = 'remove'
                continue
            elif header.startswith('IV. SYSTEM ARCHITECTURE'):
                # Keep section IV header but selectively filter content
                # Skip opening prose/table (duplicated in CLAUDE_INDEX)
                # until we hit a whitelisted ### subsection
                state = 'section_iv'
                skip_subsection = True  # Skip opening content before first ###
                continue
            else:
                state = 'keep'

            result.append(line)
            continue

        # Handle ### subsection headers
        if line.startswith('### '):
            sub_header = line[4:].strip()

            # Always remove file-browsing subsections
            if any(sub_header.startswith(s) for s in _MC_REMOVE_SUBSECTIONS):
                skip_subsection = True
                continue
            else:
                skip_subsection = False

            # In section IV, only keep specific subsections
            if state == 'section_iv':
                if any(sub_header.startswith(k) for k in _MC_IV_KEEP_SUBSECTIONS):
                    result.append(line)
                    skip_subsection = False
                else:
                    skip_subsection = True
                continue

            if state != 'remove':
                result.append(line)
            continue

        if skip_subsection:
            continue

        if state == 'keep':
            result.append(line)
        elif state == 'section_iv':
            # In section IV outside a skip, keep line only if not in skipped subsection
            if not skip_subsection:
                result.append(line)

    return '\n'.join(result)


def _compact_constraint_table(content):
    """Compress constraint table by stripping statistical evidence.

    Removes parenthetical evidence (p-values, rho, chi2, etc.) but
    preserves constraint cross-references like (C384).
    Does NOT truncate descriptions — many encode conceptual nuance.
    """
    # Pattern for statistical evidence parentheticals
    stats_pattern = re.compile(
        r'\s*\([^)]*(?:p[<=]|rho=|chi2|F=\d|eta=|Jaccard|AUC|'
        r'Cohen|KW|z=\d|r=0\.|n=\d|N=\d|OR=|RR=)[^)]*\)'
    )
    lines = content.split('\n')
    result = []
    for line in lines:
        # Skip blank lines and section dividers
        if not line.strip() or line.strip().startswith('# ---'):
            continue
        # Keep header comments
        if line.startswith('#'):
            result.append(line)
            continue
        # Strip statistical parentheticals from descriptions
        result.append(stats_pattern.sub('', line))
    return '\n'.join(result)


def _compact_yaml_contract(content):
    """Compress YAML structural contracts.

    Strips commentary, annotations, deferred, examples, separator blocks.
    Keeps guarantees, invariants, grammar, hazard topology, design freedom.
    """
    lines = content.split('\n')
    result = []
    skip_section = False
    skip_key = None
    example_count = 0
    indent = 0

    # Top-level sections to remove entirely
    remove_sections = ('annotations:', 'deferred:')

    for line in lines:
        stripped = line.strip()

        # Strip YAML comment separator blocks
        if stripped.startswith('# ===='):
            continue

        # Detect top-level keys to skip
        if stripped in remove_sections and line[0:1] not in (' ', '\t'):
            skip_section = True
            skip_key = stripped
            continue

        # Stop skipping at next top-level key
        if skip_section and skip_key != 'indented_block':
            if stripped and line[0:1] not in (' ', '\t', '') and not stripped.startswith('#') and not stripped.startswith('-') and ':' in stripped:
                skip_section = False
            else:
                continue

        # Strip multi-line commentary/notes fields (indented blocks)
        if stripped.startswith('commentary:') or stripped.startswith('notes:'):
            # Keep the key with a shortened value if it's a one-liner
            if '|' in stripped or stripped.endswith(':'):
                # Multi-line block — skip, add condensed note
                result.append(line.split(':')[0] + ': "[condensed]"')
                indent = len(line) - len(line.lstrip())
                skip_section = True
                skip_key = 'indented_block'
                continue
            else:
                result.append(line)
                continue

        # Handle indented block skipping (for commentary/notes)
        if skip_section and skip_key == 'indented_block':
            line_indent = len(line) - len(line.lstrip()) if stripped else 999
            if stripped == '' or line_indent > indent:
                continue
            else:
                skip_section = False
                skip_key = None

        # Limit example/token_reading_pattern blocks (keep first 2)
        if stripped.startswith('token_reading_pattern:') or stripped.startswith('example:'):
            example_count += 1
        if example_count > 2 and (stripped.startswith('- word:') or stripped.startswith('- token:')):
            # Skip additional examples
            continue

        result.append(line)

    return '\n'.join(result)


def compact_filter(content, filename):
    """Apply compact-mode filters to reduce agent size while preserving cognitive richness."""
    original_size = len(content)

    if 'INTERPRETATION_SUMMARY' in filename:
        content = _compact_interpretation_summary(content)
        content = _quarantine_gloss_tables(content)
    elif 'MODEL_CONTEXT' in filename:
        content = _compact_model_context(content)
    elif 'CONSTRAINT_TABLE' in filename:
        content = _compact_constraint_table(content)

    new_size = len(content)
    if original_size != new_size:
        saved = original_size - new_size
        pct = (saved / original_size) * 100
        print(f"  Compact {filename}: {original_size:,} -> {new_size:,} bytes (saved {saved:,}, {pct:.0f}%)")

    return content


def compact_contract_filter(content, filename):
    """Apply compact-mode filters to structural contracts."""
    original_size = len(content)
    content = _compact_yaml_contract(content)
    new_size = len(content)
    if original_size != new_size:
        saved = original_size - new_size
        pct = (saved / original_size) * 100
        print(f"  Compact {filename}: {original_size:,} -> {new_size:,} bytes (saved {saved:,}, {pct:.0f}%)")
    return content


# ============================================================
# CONTRACT SIGNATURE GENERATION
# ============================================================
# Replaces full YAML contracts with compact index in compact mode.
# Extracts guarantees, invariants, section->constraint mappings,
# disallowed interpretations, and key parameters.

def _generate_contract_signature(filepath, title):
    """Generate a compact contract signature from a YAML contract file.

    Extracts structural metadata without embedding the full YAML.
    All constraint references are preserved for citability.
    """
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Extract meta fields
    meta_info = {}
    in_meta = False
    for line in lines:
        if line.strip() == 'meta:':
            in_meta = True
            continue
        if in_meta:
            if line and line[0] not in (' ', '\t'):
                break
            m = re.match(r'\s+(name|acronym|version|status|date|layer_type):\s*"?([^"]*)"?', line)
            if m:
                meta_info[m.group(1)] = m.group(2).strip()

    # Extract scope fields
    scope_info = {}
    in_scope = False
    for line in lines:
        if line.strip() == 'scope:':
            in_scope = True
            continue
        if in_scope:
            if line and line[0] not in (' ', '\t'):
                break
            m = re.match(r'\s+(system|coverage|coverage_under_b_grammar|folio_count|function):\s*"?([^"]*)"?', line)
            if m:
                scope_info[m.group(1)] = m.group(2).strip()

    # Extract guarantees (list of dicts with id, statement, provenance)
    guarantees = []
    in_guarantees = False
    current = {}
    for line in lines:
        stripped = line.strip()
        if stripped == 'guarantees:':
            in_guarantees = True
            continue
        if in_guarantees:
            if line and line[0] not in (' ', '\t', '') and ':' in stripped and not stripped.startswith('#') and not stripped.startswith('-'):
                break
            m = re.match(r'\s+- id:\s*"([^"]*)"', line)
            if m:
                if current:
                    guarantees.append(current)
                current = {'id': m.group(1)}
                continue
            m = re.match(r'\s+statement:\s*"([^"]*)"', line)
            if m and current:
                current['statement'] = m.group(1)[:120]  # Truncate long statements
            m = re.match(r'\s+provenance:\s*"([^"]*)"', line)
            if m and current:
                current['provenance'] = m.group(1)
    if current and current.get('id'):
        guarantees.append(current)

    # Extract invariants (dict of name -> {statement, provenance})
    invariants = []
    in_invariants = False
    inv_name = None
    inv_data = {}
    for line in lines:
        stripped = line.strip()
        if stripped == 'invariants:':
            in_invariants = True
            continue
        if in_invariants:
            if line and line[0] not in (' ', '\t', '') and ':' in stripped and not stripped.startswith('#') and not stripped.startswith('-'):
                break
            # Invariant name (2-space indented key)
            m = re.match(r'  ([a-z_]+):', line)
            if m and not line.startswith('    '):
                if inv_name and inv_data:
                    invariants.append(inv_data)
                inv_name = m.group(1)
                inv_data = {'name': inv_name}
                continue
            m = re.match(r'\s+statement:\s*"([^"]*)"', line)
            if m and inv_name:
                inv_data['statement'] = m.group(1)[:100]
            m = re.match(r'\s+provenance:\s*"([^"]*)"', line)
            if m and inv_name:
                inv_data['provenance'] = m.group(1)
    if inv_name and inv_data:
        invariants.append(inv_data)

    # Extract disallowed interpretations
    disallowed = []
    in_disallowed = False
    current_dis = {}
    for line in lines:
        stripped = line.strip()
        if stripped == 'disallowed:':
            in_disallowed = True
            continue
        if in_disallowed:
            if line and line[0] not in (' ', '\t', '') and ':' in stripped and not stripped.startswith('#') and not stripped.startswith('-'):
                break
            m = re.match(r'\s+- interpretation:\s*"([^"]*)"', line)
            if m:
                if current_dis:
                    disallowed.append(current_dis)
                current_dis = {'text': m.group(1)}
                continue
            m = re.match(r'\s+provenance:\s*"([^"]*)"', line)
            if m and current_dis:
                current_dis['provenance'] = m.group(1)
    if current_dis and current_dis.get('text'):
        disallowed.append(current_dis)

    # Extract top-level sections and their constraint references
    sections_map = {}
    current_section = None
    # Skip meta/scope/guarantees/invariants/disallowed/ownership/provenance/annotations/deferred
    skip_keys = {'meta', 'scope', 'guarantees', 'invariants', 'disallowed',
                 'ownership', 'provenance', 'provenance_map', 'provenance_summary',
                 'annotations', 'deferred', 'negative_guarantees'}
    for line in lines:
        stripped = line.strip()
        # Detect top-level keys
        m = re.match(r'^([a-z_]+):', line)
        if m:
            key = m.group(1)
            if key in skip_keys:
                current_section = None
            else:
                current_section = key
                sections_map[current_section] = set()
            continue
        # Collect constraint refs in current section
        if current_section:
            for ref in re.findall(r'C\d{3,4}', line):
                sections_map[current_section].add(ref)

    # Also extract negative_guarantees constraint refs (important guardrails)
    neg_guarantees = []
    in_neg = False
    for line in lines:
        stripped = line.strip()
        if stripped == 'negative_guarantees:':
            in_neg = True
            continue
        if in_neg:
            if line and line[0] not in (' ', '\t', '') and ':' in stripped and not stripped.startswith('#') and not stripped.startswith('-'):
                break
            m = re.match(r'\s+- "([^"]*)"', line)
            if m:
                refs = re.findall(r'C\d{3,4}', m.group(1))
                neg_guarantees.append({'text': m.group(1), 'refs': refs})

    # Build signature markdown
    out = []
    # Header
    acronym = meta_info.get('acronym', '')
    name = meta_info.get('name', title)
    version = meta_info.get('version', '?')
    status = meta_info.get('status', '?')
    scope_text = scope_info.get('coverage', scope_info.get('system', ''))
    if scope_info.get('folio_count'):
        scope_text += f", {scope_info['folio_count']} folios"

    out.append(f"## {acronym} ({name})")
    out.append(f"**Meta:** v{version}, {status}, {scope_text}")
    out.append("")

    # Guarantees
    if guarantees:
        out.append(f"### Guarantees ({len(guarantees)})")
        for g in guarantees:
            prov = g.get('provenance', '')
            out.append(f"- {g['id']}: {g.get('statement', '')} [{prov}]")
        out.append("")

    # Invariants
    if invariants:
        out.append(f"### Invariants ({len(invariants)})")
        for inv in invariants:
            prov = inv.get('provenance', '')
            out.append(f"- {inv['name']}: {inv.get('statement', '')} [{prov}]")
        out.append("")

    # Sections -> Constraints
    if sections_map:
        out.append("### Sections -> Constraints")
        for section, refs in sections_map.items():
            if refs:
                # Sort constraint refs numerically
                sorted_refs = sorted(refs, key=lambda x: int(re.search(r'\d+', x).group()))
                out.append(f"- {section}: {', '.join(sorted_refs)}")
            else:
                out.append(f"- {section}: (no constraint refs)")
        out.append("")

    # Negative guarantees (if any)
    if neg_guarantees:
        out.append(f"### Negative Guarantees ({len(neg_guarantees)})")
        for ng in neg_guarantees:
            out.append(f"- {ng['text']}")
        out.append("")

    # Disallowed interpretations
    if disallowed:
        out.append(f"### Disallowed Interpretations ({len(disallowed)})")
        for d in disallowed:
            prov = d.get('provenance', '')
            out.append(f'- "{d["text"]}" [{prov}]')
        out.append("")

    return '\n'.join(out)


def _generate_all_contract_signatures():
    """Generate compact signatures for all structural contracts.

    Returns concatenated markdown replacing the full YAML contracts.
    """
    result = []
    for filename, title in CONTRACTS:
        filepath = CONTEXT_DIR / filename
        if filepath.exists():
            sig = _generate_contract_signature(filepath, title)
            result.append(sig)
            print(f"  Signature {filename}: {len(sig):,} bytes")
        else:
            print(f"WARNING: {filename} not found")
    return '\n---\n\n'.join(result)


# Cognitive operating stance for compact agent header
COMPACT_STANCE = """
## Cognitive Operating Stance

This is a structurally closed system with:
- Tier 0-2 binding constraints ({constraint_count} validated, with tier and scope metadata)
- Tier 3-4 explanatory frameworks (non-binding, discardable)
- No substance-level semantic recovery possible (C171, C120)
- High-dimensional discrimination manifold (C973, C982)
- Grammar-level safety enforcement via forbidden transitions (C109)
- Operator judgment gating (13 types structurally required but non-encodable)

When reasoning:
- Honor Tier discipline (Tier 0 frozen, Tier 1 falsified, Tier 2 binding)
- Use constraint table (with tier/scope) as authoritative source
- Use contract signatures to find which constraints cover a topic
- Use interpretive layer for cross-layer integration
- Never infer token meanings beyond structural role
- Dangerous contexts restrict grammar instead of raising alerts (C458)
- Design asymmetry: hazard clamped (CV 0.04-0.11), recovery free (CV 0.72-0.82) (C458)
- Free variation envelope: ~57% of folio-level dynamics are genuine design freedom (C980, C1035)
- Pairwise compositionality: no three-way morphological synergy (C1003)

**Note:** This is a compact agent build. Full structural contracts have been replaced
with contract signatures (topic heading + constraint IDs + key parameters). All
{constraint_count} validated constraints are present as canonical one-line claims with tier
and scope metadata. {fit_count} fits are complete. Tier 3-4 interpretive sections are
condensed but all section headers and constraint references are preserved. Gloss/etymology
tables are quarantined — do not use for structural answers.

---

"""


AGENT_FILE = CONTEXT_DIR.parent / ".claude" / "agents" / "expert-advisor.md"
LEGACY_FILE = CONTEXT_DIR / "EXPERT_CONTEXT.md"

# Session methodology memory directory (per-project Claude Code memory).
# Feedback-type notes are auto-included into expert agents; project-type and
# other types are NOT included (those are individual findings derivable from
# the constraint system, and including all of them would blow the token budget).
MEMORY_DIR = Path.home() / ".claude" / "projects" / "C--git-voynich" / "memory"

# Core documents (always included)
CORE_DOCS = [
    ("CLAUDE_INDEX.md", "Project Overview & Navigation"),
    ("MODEL_CONTEXT.md", "Architectural Framework"),
    ("CONSTRAINT_TABLE.txt", "All Constraints"),
    ("MODEL_FITS/FIT_TABLE.txt", "All Explanatory Fits"),
    ("SPECULATIVE/INTERPRETATION_SUMMARY.md", "Tier 3-4 Interpretations"),
]

# Structural contracts (optional, adds ~60KB)
CONTRACTS = [
    ("STRUCTURAL_CONTRACTS/currierA.casc.yaml", "Currier A Structure Contract"),
    ("STRUCTURAL_CONTRACTS/currierB.bcsc.yaml", "Currier B Grammar Contract"),
    ("STRUCTURAL_CONTRACTS/azc_activation.act.yaml", "A->AZC Activation Contract"),
    ("STRUCTURAL_CONTRACTS/azc_b_activation.act.yaml", "AZC->B Propagation Contract"),
    ("STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml", "Human Track Layer Contract"),
    ("STRUCTURAL_CONTRACTS/paragraph.psc.yaml", "Paragraph Unit Contract"),
]

# Required YAML frontmatter for agent registration
AGENT_FRONTMATTER = """---
name: expert-advisor
description: "When we need expert consultation."
model: opus
color: red
---

"""

# Crazy-expert agent: SAME generated body as expert-advisor, prepended with a
# hand-curated speculation stance (context/CRAZY_EXPERT_STANCE.md — hand-editable).
# This makes crazy-expert auto-inherit the methodology trim + current constraint
# state instead of being a stale hand-pasted copy.
CRAZY_FILE = CONTEXT_DIR.parent / ".claude" / "agents" / "crazy-expert.md"
CRAZY_STANCE_FILE = CONTEXT_DIR / "CRAZY_EXPERT_STANCE.md"
CRAZY_FRONTMATTER = """---
name: crazy-expert
description: "Unguarded speculation engine. All brakes offline."
model: opus
color: yellow
---

"""

# Lean-expert agent: validated constraints + statistics + fits + the methodology /
# anti-echo priors, but NO positive interpretive layer (no Tier 3-4, no architectural
# narrative, no speculation stance). "Disciplined but un-interpreted." Used as the
# rigor/statistics reviewer and the differential counterpart to expert-advisor:
# lean-vs-full divergence localizes where interpretation (not stats) carries a verdict.
LEAN_FILE = CONTEXT_DIR.parent / ".claude" / "agents" / "lean-expert.md"
LEAN_FRONTMATTER = """---
name: lean-expert
description: "Constraints and statistics only -- no interpretive context. Rigor/stats reviewer."
model: opus
color: blue
---

"""
LEAN_HEADER = """
## CRITICAL INSTRUCTION

**YOU MUST NOT USE ANY FILE-READING TOOLS.** All context you need is embedded below.

---

# Lean Expert Agent (constraints + statistics only)

## Purpose

You are the **lean expert** for the Voynich Manuscript Currier B analysis project. You carry the {constraint_count} validated constraints (with tiers + metrics) and {fit_count} explanatory fits, plus the project's methodology / discipline priors. You DELIBERATELY DO NOT carry the interpretive layer -- no Tier 3-4 operational interpretations, no architectural-framework narrative, no speculation stance. This is by design: you answer from the constraints and statistics ALONE.

## Rules

1. **Cite C### / F-IDs with their tiers + metrics.** Ground every claim in a constraint or fit.
2. **Do NOT supply operational interpretation.** If asked "what does X mean / encode / represent," answer only with what the constraints structurally establish, then say: *"Operational interpretation requires context I do not carry -- route to expert-advisor / INTERPRETATION_SUMMARY."* Never invent a reading.
3. **You CAN clear:** statistical rigor, correct null for the claim class, denominator, tier/bookkeeping, whether a claim contradicts a constraint. **You CANNOT clear** clean-fit / mechanism claims -- you have no framework to judge "fit" against, which is the point.
4. **Differential use:** when you and the full expert-advisor DIVERGE on a verdict, the divergence localizes where *interpretation* (not statistics) is carrying the weight. Say so explicitly.
5. Apply the Session Methodology priors below as discipline (they are anti-echo priors, not interpretation).

## Output Style

Direct and statistical. State what the numbers and validated constraints say; refuse to go past them.

---

# EMBEDDED CONTEXT (constraints, fits, methodology priors)

"""

# Agent system prompt
AGENT_HEADER = """
## CRITICAL INSTRUCTION

**YOU MUST NOT USE ANY FILE-READING TOOLS.** Do not use Read, Glob, Grep, or any other tools.
All context you need is ALREADY EMBEDDED in this document below. Answer questions by
searching within THIS document only. If you use file tools, you are doing it wrong.

---

# Expert Advisor Agent

## Purpose

You are the **internal expert** for the Voynich Manuscript Currier B analysis project.
Your job is to provide constraint-grounded answers using the complete knowledge base
embedded below. You have all {constraint_count} validated constraints and {fit_count} explanatory fits loaded
as permanent context. Constraint IDs are chronological and non-contiguous (some invalidated/superseded);
the highest ID present is {highest_id}.

**NEVER read external files** - everything you need is ALREADY IN THIS DOCUMENT.

## When You Are Invoked

You will be asked to:
1. **Validate Proposals** - Check if proposed changes conflict with existing constraints
2. **Answer Questions** - Provide constraint-grounded answers about structure and relationships
3. **Review Findings** - Assess new phase findings against the existing framework
4. **Classify Tiers** - Help determine appropriate tiers for new findings
5. **Find Connections** - Identify relevant constraints for new questions

## Response Format

Always cite constraint numbers (C###) or fit IDs (F-XXX-###) when making claims.

Examples:
- "This conflicts with C384 (no entry-level A-B coupling)"
- "Supported by C121 (49 instruction classes with 100% coverage)"
- "Consistent with Tier 3 interpretation in INTERPRETATION_SUMMARY.md"

## Tier Discipline

- **Tier 0:** Frozen conclusion. Never contradict.
- **Tier 1:** Falsified hypotheses. Never retry.
- **Tier 2:** Validated constraints. Binding - do not contradict.
- **Tier 3:** Structural characterization. Can refine, not contradict.
- **Tier 4:** Speculative. Can disagree with, but note the tier.

## Output Style

Be direct and technical. Cite sources. Avoid hedging when constraints are clear.
When constraints ARE clear, state the conclusion firmly.
When constraints are ambiguous or don't cover the question, say so explicitly.

---

# EMBEDDED EXPERT CONTEXT

"""


def load_methodology_memories():
    """Load feedback-type session memory notes for expert agent embedding.

    Reads MEMORY_DIR for .md files with YAML frontmatter `type: feedback`.
    Returns list of (filename, body_content) tuples. Body has YAML frontmatter
    stripped; the `name` field is preserved as a heading.

    Project-type, user-type, and reference-type memories are NOT included --
    they're either individual findings (project) the expert can re-derive from
    constraints, or non-methodology (user/reference). Token budget restricted to
    methodology-relevant feedback rules only.
    """
    if not MEMORY_DIR.exists():
        return []

    methodology_notes = []
    for path in sorted(MEMORY_DIR.glob("*.md")):
        if path.name == "MEMORY.md":  # skip the index file
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except Exception:
            continue

        # Parse YAML frontmatter
        if not content.startswith("---"):
            continue
        try:
            end_idx = content.index("\n---\n", 4)
        except ValueError:
            continue
        frontmatter_raw = content[4:end_idx]
        body = content[end_idx + 5:].strip()

        # Extract frontmatter fields (simple line-by-line; no PyYAML dependency)
        frontmatter = {}
        for line in frontmatter_raw.split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                frontmatter[k.strip()] = v.strip()

        if frontmatter.get("type", "").lower() != "feedback":
            continue

        name = frontmatter.get("name", path.stem)
        description = frontmatter.get("description", "")
        methodology_notes.append((path.name, name, description, body))

    return methodology_notes


def generate_content(header, include_contracts=True, apply_filters=True, compact=False, lean=False):
    """Generate expert context content with given header."""
    constraint_count, fit_count, highest_id = get_counts()
    sections = []
    component_sizes = {}

    # LEAN mode: validated constraints + stats + discipline priors only. Drops the
    # POSITIVE interpretive layer (Project Overview, Architectural Framework,
    # Tier 3-4 Interpretations, contracts, cognitive stance) but KEEPS the methodology
    # notes (negative-knowledge / anti-echo priors) — "disciplined but un-interpreted".
    docs = [d for d in CORE_DOCS if d[1] in ("All Constraints", "All Explanatory Fits")] if lean else CORE_DOCS

    # Header with instructions (fill in dynamic counts)
    sections.append(header.format(constraint_count=constraint_count, fit_count=fit_count, highest_id=highest_id))

    # Add cognitive stance for compact mode (NOT for lean — the stance is interpretive)
    if compact and not lean:
        sections.append(COMPACT_STANCE.format(
            constraint_count=constraint_count, fit_count=fit_count
        ))

    # Metadata (counts parsed dynamically from INDEX.md and FIT_TABLE.txt)
    mode_label = "COMPACT" if compact else "FULL"
    sections.append(f"""**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Version:** FROZEN STATE ({constraint_count} validated constraints, {fit_count} fits) [{mode_label}]

---

## Table of Contents

""")

    # Load methodology memories (feedback-type only)
    methodology_notes = load_methodology_memories()

    # TOC
    toc_num = 1
    for _, title in docs:
        sections[-1] += f"{toc_num}. {title}\n"
        toc_num += 1
    if methodology_notes:
        sections[-1] += f"{toc_num}. Session Methodology Notes ({len(methodology_notes)} feedback rules)\n"
        toc_num += 1
    if include_contracts:
        if compact:
            sections[-1] += f"{toc_num}. Structural Contract Signatures (6 contracts)\n"
            toc_num += 1
        else:
            for _, title in CONTRACTS:
                sections[-1] += f"{toc_num}. {title}\n"
                toc_num += 1

    sections[-1] += "\n---\n"

    # Core documents
    for filename, title in docs:
        filepath = CONTEXT_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            if apply_filters:
                content = filter_for_agent(content, filename, compact=compact)
            if compact:
                content = compact_filter(content, filename)
            component_sizes[title] = len(content)
            sections.append(f"\n# {title}\n\n{content}\n\n---\n")
        else:
            print(f"WARNING: {filename} not found")

    # Session methodology notes (feedback-type memories from
    # `~/.claude/projects/C--git-voynich/memory/`)
    if methodology_notes:
        memory_section = [
            "\n# Session Methodology Notes\n",
            "\nThese are project-level methodology rules accumulated across sessions.",
            " They document trap patterns we have already caught, controls that are load-bearing,",
            " and discipline rules that govern how new findings should be validated.",
            " **Apply these as priors when assessing new proposals.**\n\n",
        ]
        # COMPACT embedding (2026-05-30): the description carries the rule gist
        # and the body lead carries the core mechanism/why; the long tail (extended
        # examples, evidence dumps, [[related]] links) is dropped to keep the agent
        # within budget. Full notes remain on disk at memory/<filename>.
        MAX_BODY = 900
        for filename, name, description, body in methodology_notes:
            memory_section.append(f"\n## {name}\n\n")
            if description:
                memory_section.append(f"*{description}*\n\n")
            compact_body = body.strip()
            if len(compact_body) > MAX_BODY:
                cut = compact_body.rfind("\n", 0, MAX_BODY)
                if cut < MAX_BODY // 2:
                    cut = MAX_BODY
                compact_body = compact_body[:cut].rstrip() + f"\n\n[…trimmed — full note: memory/{filename}]"
            memory_section.append(f"{compact_body}\n\n---\n")
        full_memory_text = "".join(memory_section)
        component_sizes['Session Methodology Notes'] = len(full_memory_text)
        sections.append(full_memory_text)

    # Contracts
    if include_contracts:
        if compact:
            # Compact mode: generate contract signatures instead of full YAML
            signatures = _generate_all_contract_signatures()
            component_sizes['Contract Signatures (all 6)'] = len(signatures)
            sections.append(f"\n# Structural Contract Signatures\n\n{signatures}\n\n---\n")
        else:
            for filename, title in CONTRACTS:
                filepath = CONTEXT_DIR / filename
                if filepath.exists():
                    content = filepath.read_text(encoding='utf-8')
                    if apply_filters:
                        content = filter_contract_for_agent(content, filename)
                    component_sizes[title] = len(content)
                    sections.append(f"\n# {title}\n\n```yaml\n{content}\n```\n\n---\n")
                else:
                    print(f"WARNING: {filename} not found")

    return "".join(sections), component_sizes


def generate(include_contracts=True, include_legacy=False, apply_filters=True, compact=False):
    """Generate expert-advisor agent with embedded context."""

    doc_count = len(CORE_DOCS) + (len(CONTRACTS) if include_contracts else 0)

    if compact:
        print("Generating COMPACT agent (cognitive compression)...")
    if apply_filters:
        print("Applying agent filters...")

    # Generate agent file (with required YAML frontmatter)
    agent_content, component_sizes = generate_content(
        AGENT_HEADER, include_contracts, apply_filters=apply_filters, compact=compact
    )
    AGENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    AGENT_FILE.write_text(AGENT_FRONTMATTER + agent_content, encoding='utf-8')
    agent_size_kb = AGENT_FILE.stat().st_size / 1024
    print(f"Generated agent: {AGENT_FILE}")
    print(f"Agent size: {agent_size_kb:.1f} KB")

    # Crazy-expert: SAME generated body (agent_content is still the bare body here,
    # frontmatter not yet prepended), with the hand-curated speculation stance in
    # front. Inherits methodology trim + current constraint state automatically.
    if CRAZY_STANCE_FILE.exists():
        crazy_stance = CRAZY_STANCE_FILE.read_text(encoding='utf-8').strip()
        crazy_content = CRAZY_FRONTMATTER + crazy_stance + "\n\n" + agent_content
        CRAZY_FILE.write_text(crazy_content, encoding='utf-8')
        crazy_kb = CRAZY_FILE.stat().st_size / 1024
        print(f"Generated crazy-expert: {CRAZY_FILE} ({crazy_kb:.1f} KB)")
    else:
        print(f"WARN: {CRAZY_STANCE_FILE} missing - crazy-expert NOT regenerated")

    # Lean-expert: validated constraints + stats + fits + methodology priors ONLY
    # (no Tier 3-4, no architectural narrative, no contracts, no cognitive stance).
    # Separate generate_content call with lean=True and contracts off.
    lean_content, _ = generate_content(
        LEAN_HEADER, include_contracts=False, apply_filters=apply_filters,
        compact=compact, lean=True
    )
    LEAN_FILE.write_text(LEAN_FRONTMATTER + lean_content, encoding='utf-8')
    lean_kb = LEAN_FILE.stat().st_size / 1024
    print(f"Generated lean-expert: {LEAN_FILE} ({lean_kb:.1f} KB)")
    print(f"Documents included: {doc_count}")

    # Print component size report
    if component_sizes:
        print(f"\n--- {'Compact' if compact else 'Standard'} Mode Size Report ---")
        for name, size in component_sizes.items():
            print(f"  {name}: {size:,} bytes ({size/1024:.1f} KB)")
        total = sum(component_sizes.values())
        print(f"  ---")
        print(f"  Content total: {total:,} bytes ({total/1024:.1f} KB)")

    # Legacy output (UNFILTERED - for external expert uploads)
    if include_legacy:
        legacy_content, _ = generate_content(AGENT_HEADER, include_contracts, apply_filters=False)
        LEGACY_FILE.write_text(legacy_content, encoding='utf-8')
        legacy_kb = LEGACY_FILE.stat().st_size / 1024
        print(f"Legacy file: {LEGACY_FILE} ({legacy_kb:.1f} KB, unfiltered)")

    return AGENT_FILE


if __name__ == "__main__":
    import sys
    include_contracts = "--no-contracts" not in sys.argv
    include_legacy = "--legacy" in sys.argv
    apply_filters = "--no-filter" not in sys.argv
    compact = "--compact" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    generate(include_contracts, include_legacy, apply_filters, compact)
