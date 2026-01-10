# Context System

This directory implements a **progressive disclosure context system** for the Voynich Manuscript analysis project.

## Purpose

The project's knowledge has grown beyond what fits in a single file (~30k tokens). This system:

1. **Controls AI cognition** - prevents reading everything at once
2. **Enforces tier discipline** - Tier 0-2 facts separated from Tier 3-4 speculation
3. **Enables addressability** - every claim can be cited by number
4. **Supports growth** - new findings extend without destabilizing core

## How to Use

### Entry Point

**Always start here:** `CLAUDE_INDEX.md`

This is the only file that should be read automatically. All other files are loaded on demand.

### Navigation Pattern

1. Read `CLAUDE_INDEX.md` for orientation
2. Follow links to specific topic files as needed
3. Stop when you have enough context
4. Never read the entire directory

### Directory Structure

| Directory | Contents | When to Read |
|-----------|----------|--------------|
| `SYSTEM/` | Meta-rules, tiers, methodology | When unsure how project works |
| `CORE/` | Tier 0 frozen facts, Tier 1 falsifications | When checking what's proven/rejected |
| `ARCHITECTURE/` | Currier A, B, AZC structural analysis | When working on specific text type |
| `OPERATIONS/` | OPS doctrine, program taxonomy | When analyzing program behavior |
| `CLAIMS/` | All 299 constraints, indexed and grouped | When citing or checking constraints |
| `TERMINOLOGY/` | Definitions of key terms | When confused about vocabulary |
| `METRICS/` | Quantitative facts and thresholds | When checking numbers |
| `SPECULATIVE/` | Tier 3-4 interpretive content | Only when explicitly relevant |
| `MAPS/` | Cross-references, phase index | When tracing provenance |

## Rules

1. **One concept per file** - files are focused, not comprehensive
2. **≤15k tokens per file** - headroom for 25k READ limit
3. **Every claim declares Tier + closure** - no ambiguous status
4. **No analysis in context files** - summarize, don't derive
5. **Archive is memory, context is interface** - raw work in archive/, curated knowledge here

## Relationship to Other Directories

| Directory | Role | Relationship to context/ |
|-----------|------|--------------------------|
| `archive/` | Memory (append-only) | Context points to archive for provenance |
| `phases/` | Research projects | Context extracts findings from phases |
| `results/` | Frozen outputs | Context summarizes results |
| `data/` | Raw data | Context does not reference directly |

## Adding New Content

When a new phase produces findings:

1. Phase documentation goes to `phases/PHASE_NAME/`
2. Scripts go to `archive/scripts/`
3. If a new constraint is established:
   - Add to `CLAIMS/INDEX.md`
   - Create individual file OR add to grouped registry
4. Update `SYSTEM/CHANGELOG.md`
5. Update `MAPS/claim_to_phase.md`

**Rule:** Context files summarize and point. They do not introduce new analysis.

## Version

- **System Version:** 1.0
- **Project Version:** 1.8 FROZEN STATE
- **Created:** 2026-01-08
