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
    python generate_expert_context.py --compact    # Cognitively compressed (~310KB)
    python generate_expert_context.py --no-contracts  # Exclude structural contracts
    python generate_expert_context.py --legacy     # Also generate EXPERT_CONTEXT.md
    python generate_expert_context.py --no-filter  # Skip agent-specific filtering
"""

import re
from pathlib import Path
from datetime import datetime

CONTEXT_DIR = Path(__file__).parent


def get_counts():
    """Parse constraint and fit counts from their respective index files."""
    constraint_count = 0
    fit_count = 0

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

    return constraint_count, fit_count


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

        filtered.append(lines[i])
        i += 1
    return '\n'.join(filtered)


def _strip_claude_index_sections(content):
    """Strip sections from CLAUDE_INDEX that are useless to the expert agent.

    Removes:
    - DATA LOADING WARNING (for script-writing agents)
    - Navigation table (for file-reading agents)
    - File Registry (file paths)
    - Automation (tool locations)
    - Context System (progressive disclosure instructions)
    """
    sections_to_strip = [
        'DATA LOADING WARNING',
        'Navigation',
        'File Registry',
        'Automation',
        'Context System',
    ]
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
    """Compress CONSTRAINT_TABLE.txt by removing TIER/SCOPE/LOCATION columns.

    The agent rarely uses these for lookup - it searches by constraint
    number and description. Removing these columns saves ~15-20% of
    the table size.
    """
    lines = content.split('\n')
    filtered = []
    for line in lines:
        # Skip comment/header lines
        if line.startswith('#') or not line.strip():
            filtered.append(line)
            continue

        # TSV lines: ID | TITLE | TIER | SCOPE | LOCATION
        # Keep only ID and TITLE (first two fields)
        parts = line.split('\t')
        if len(parts) >= 2:
            filtered.append(f"{parts[0]}\t{parts[1]}")
        else:
            filtered.append(line)

    return '\n'.join(filtered)


def filter_for_agent(content, filename):
    """Apply all agent-specific filters to a document before embedding."""
    original_size = len(content)

    # Universal: strip file references from all documents
    content = _strip_file_references(content)

    # Document-specific filters
    if 'CLAUDE_INDEX' in filename:
        content = _strip_claude_index_sections(content)
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


# MODEL_CONTEXT sections to remove entirely (fully redundant)
_MC_REMOVE_SECTIONS = [
    'X.B. APPARATUS-CENTRIC',
    'XII. HISTORICAL',
]

# MODEL_CONTEXT sections to compress (keep first N lines)
_MC_COMPRESS_SECTIONS = {
    'V. GLOBAL MORPHOLOGICAL': 65,
    'VI. CURRIER B': 55,
    'VII. CURRIER A': 35,
    'VIII. AZC': 30,
}


def _compact_model_context(content):
    """Cognitively compress MODEL_CONTEXT.

    Compress V (morphology), VI (B), VII (A), VIII (AZC) to core concepts.
    Remove X.B and XII (redundant with INTERPRETATION_SUMMARY).
    Keep governance sections I-IV, IX, XI, XIII-XVI in full.
    """
    lines = content.split('\n')
    result = []
    state = 'keep'  # 'keep', 'remove', 'compress'
    compress_limit = 0
    lines_in_section = 0

    for line in lines:
        # Detect ## section headers
        if line.startswith('## '):
            header = line[3:].strip()

            # Check if this section should be removed
            if any(header.startswith(r) for r in _MC_REMOVE_SECTIONS):
                state = 'remove'
                result.append(line)
                result.append('')
                result.append('*[Section condensed — content available in INTERPRETATION_SUMMARY or structural contracts.]*')
                result.append('')
                continue

            # Check if this section should be compressed
            matched = False
            for prefix, limit in _MC_COMPRESS_SECTIONS.items():
                if header.startswith(prefix):
                    state = 'compress'
                    compress_limit = limit
                    lines_in_section = 0
                    matched = True
                    break

            if not matched:
                state = 'keep'

            result.append(line)
            continue

        if state == 'keep':
            result.append(line)
        elif state == 'remove':
            continue
        elif state == 'compress':
            lines_in_section += 1
            if lines_in_section <= compress_limit:
                result.append(line)
            elif lines_in_section == compress_limit + 1:
                result.append('')
                result.append('*[Remaining detail available in structural contracts.]*')
                result.append('')

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


# Cognitive operating stance for compact agent header
COMPACT_STANCE = """
## Cognitive Operating Stance

This is a structurally closed system with:
- Tier 0-2 binding constraints ({constraint_count} validated)
- Tier 3-4 explanatory frameworks (non-binding, discardable)
- No substance-level semantic recovery possible (C171, C120)
- High-dimensional discrimination manifold (C973, C982)
- Grammar-level safety enforcement via forbidden transitions (C109)
- Operator judgment gating (13 types structurally required but non-encodable)

When reasoning:
- Honor Tier discipline (Tier 0 frozen, Tier 1 falsified, Tier 2 binding)
- Use contracts for structural questions
- Use interpretive layer for cross-layer integration
- Never infer token meanings beyond structural role
- Dangerous contexts restrict grammar instead of raising alerts (C458)
- Design asymmetry: hazard clamped (CV 0.04-0.11), recovery free (CV 0.72-0.82) (C458)
- Free variation envelope: ~57% of folio-level dynamics are genuine design freedom (C980, C1035)
- Pairwise compositionality: no three-way morphological synergy (C1003)

**Note:** This is a compact agent build. Sections marked *[condensed]* have
full content in their source documents. All {constraint_count} constraints, {fit_count} fits,
and 4 structural contracts are complete.

---

"""


AGENT_FILE = CONTEXT_DIR.parent / ".claude" / "agents" / "expert-advisor.md"
LEGACY_FILE = CONTEXT_DIR / "EXPERT_CONTEXT.md"

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
]

# Required YAML frontmatter for agent registration
AGENT_FRONTMATTER = """---
name: expert-advisor
description: "When we need expert consultation."
model: opus
color: red
---

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
embedded below. You have ALL {constraint_count} validated constraints and {fit_count} explanatory fits loaded
as permanent context.

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


def generate_content(header, include_contracts=True, apply_filters=True, compact=False):
    """Generate expert context content with given header."""
    constraint_count, fit_count = get_counts()
    sections = []
    component_sizes = {}

    # Header with instructions (fill in dynamic counts)
    sections.append(header.format(constraint_count=constraint_count, fit_count=fit_count))

    # Add cognitive stance for compact mode
    if compact:
        sections.append(COMPACT_STANCE.format(
            constraint_count=constraint_count, fit_count=fit_count
        ))

    # Metadata (counts parsed dynamically from INDEX.md and FIT_TABLE.txt)
    mode_label = "COMPACT" if compact else "FULL"
    sections.append(f"""**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Version:** FROZEN STATE ({constraint_count} constraints, {fit_count} fits) [{mode_label}]

---

## Table of Contents

""")

    # TOC
    toc_num = 1
    for _, title in CORE_DOCS:
        sections[-1] += f"{toc_num}. {title}\n"
        toc_num += 1
    if include_contracts:
        for _, title in CONTRACTS:
            sections[-1] += f"{toc_num}. {title}\n"
            toc_num += 1

    sections[-1] += "\n---\n"

    # Core documents
    for filename, title in CORE_DOCS:
        filepath = CONTEXT_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            if apply_filters:
                content = filter_for_agent(content, filename)
            if compact:
                content = compact_filter(content, filename)
            component_sizes[title] = len(content)
            sections.append(f"\n# {title}\n\n{content}\n\n---\n")
        else:
            print(f"WARNING: {filename} not found")

    # Contracts
    if include_contracts:
        for filename, title in CONTRACTS:
            filepath = CONTEXT_DIR / filename
            if filepath.exists():
                content = filepath.read_text(encoding='utf-8')
                if apply_filters:
                    content = filter_contract_for_agent(content, filename)
                if compact:
                    content = compact_contract_filter(content, filename)
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
    agent_content = AGENT_FRONTMATTER + agent_content
    AGENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    AGENT_FILE.write_text(agent_content, encoding='utf-8')
    agent_size_kb = AGENT_FILE.stat().st_size / 1024
    print(f"Generated agent: {AGENT_FILE}")
    print(f"Agent size: {agent_size_kb:.1f} KB")
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
