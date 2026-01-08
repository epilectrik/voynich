# Context System Changelog

**Purpose:** Track changes to the context system structure and content.

---

## Version 1.0 (2026-01-08)

### Initial Release

**Created:** Context expansion system to replace monolithic CLAUDE.md

**Structure:**
- `context/` directory with 9 subdirectories
- `CLAUDE_INDEX.md` as primary entry point (~4k tokens)
- Progressive disclosure architecture
- 57 markdown files total

**Directories:**
- `SYSTEM/` - Meta-rules, tiers, methodology (5 files)
- `CORE/` - Tier 0-1 facts (3 files)
- `ARCHITECTURE/` - Structural analysis by text type (5 files)
- `OPERATIONS/` - OPS doctrine, program taxonomy (3 files)
- `CLAIMS/` - 411 constraints indexed (24 files: 1 index, 16 individual claims, 7 grouped registries)
- `TERMINOLOGY/` - Key definitions (3 files)
- `METRICS/` - Quantitative facts (4 files)
- `SPECULATIVE/` - Tier 3-4 content (4 files)
- `MAPS/` - Cross-references (3 files)

**Design Principles:**
1. Entry point stays slim (<10k tokens)
2. One concept per file
3. ≤15k tokens per file
4. Every claim declares Tier + closure
5. No analysis in context files
6. Archive is append-only
7. Context points to archive

**Migration:**
- Content extracted from CLAUDE.md v1.8 (95KB, ~30k tokens)
- Original preserved as `archive/CLAUDE_v1.8_2026-01-08.md`
- CLAUDE.md converted to redirect

---

## Version 1.1 (2026-01-08)

### Added: Research Automation

**Summary:** Added skills, hooks, and workflow documentation for automated research.

**Files created:**
- `.claude/skills/phase-analysis/SKILL.md` - Automatic phase analysis
- `.claude/skills/constraint-lookup/SKILL.md` - Constraint search and citation
- `.claude/settings.json` - Hook configuration
- `archive/scripts/validate_constraint_reference.py` - Constraint validation
- `archive/scripts/extract_phase_metrics.py` - Metrics extraction

**Files updated:**
- `context/SYSTEM/METHODOLOGY.md` - Added "Research Workflow (Automated)" section
- `context/SYSTEM/HOW_TO_READ.md` - Added multi-branch access patterns
- `context/CLAUDE_INDEX.md` - Added "Automation" section

**New workflows:**
- Phase Analysis Protocol (automatic)
- Constraint Lookup Protocol (automatic)
- Constraint reference validation (hook)

---

## Future Entries

When updating context, add entries in this format:

```markdown
## Version X.Y (YYYY-MM-DD)

### [Type: Added/Changed/Removed/Fixed]

**Summary:** Brief description

**Files affected:**
- `path/to/file.md` - what changed

**Constraint changes:**
- C### added/updated/removed

**Source:** Phase PHASE_NAME (if applicable)
```

---

## Navigation

← [HOW_TO_READ.md](HOW_TO_READ.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
