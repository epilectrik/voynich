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

Usage:
    python generate_expert_context.py              # Generate agent with all documents
    python generate_expert_context.py --no-contracts  # Exclude structural contracts
    python generate_expert_context.py --legacy     # Also generate EXPERT_CONTEXT.md
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


def generate_content(header, include_contracts=True):
    """Generate expert context content with given header."""
    constraint_count, fit_count = get_counts()
    sections = []

    # Header with instructions (fill in dynamic counts)
    sections.append(header.format(constraint_count=constraint_count, fit_count=fit_count))

    # Metadata (counts parsed dynamically from INDEX.md and FIT_TABLE.txt)
    sections.append(f"""**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Version:** FROZEN STATE ({constraint_count} constraints, {fit_count} fits)

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
            sections.append(f"\n# {title}\n\n**Source:** `context/{filename}`\n\n{content}\n\n---\n")
        else:
            print(f"WARNING: {filename} not found")

    # Contracts
    if include_contracts:
        for filename, title in CONTRACTS:
            filepath = CONTEXT_DIR / filename
            if filepath.exists():
                content = filepath.read_text(encoding='utf-8')
                sections.append(f"\n# {title}\n\n**Source:** `context/{filename}`\n\n```yaml\n{content}\n```\n\n---\n")
            else:
                print(f"WARNING: {filename} not found")

    return "".join(sections)


def generate(include_contracts=True, include_legacy=False):
    """Generate expert-advisor agent with embedded context."""

    doc_count = len(CORE_DOCS) + (len(CONTRACTS) if include_contracts else 0)

    # Generate agent file (with required YAML frontmatter)
    agent_content = AGENT_FRONTMATTER + generate_content(AGENT_HEADER, include_contracts)
    AGENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    AGENT_FILE.write_text(agent_content, encoding='utf-8')
    agent_size_kb = AGENT_FILE.stat().st_size / 1024
    print(f"Generated agent: {AGENT_FILE}")
    print(f"Agent size: {agent_size_kb:.1f} KB")
    print(f"Documents included: {doc_count}")

    # Legacy output (for external expert uploads)
    if include_legacy:
        legacy_content = generate_content(AGENT_HEADER, include_contracts)
        LEGACY_FILE.write_text(legacy_content, encoding='utf-8')
        print(f"Legacy file: {LEGACY_FILE}")

    return AGENT_FILE


if __name__ == "__main__":
    import sys
    include_contracts = "--no-contracts" not in sys.argv
    include_legacy = "--legacy" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    generate(include_contracts, include_legacy)
