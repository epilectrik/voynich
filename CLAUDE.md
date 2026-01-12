# Voynich Manuscript Analysis

This project uses a **progressive context system**.

---

## START HERE

**Primary Entry Point:** [context/CLAUDE_INDEX.md](context/CLAUDE_INDEX.md)

---

## Quick Reference

| Metric | Value |
|--------|-------|
| Version | 2.6 FROZEN STATE |
| Constraints | 317 validated |
| Phases | 118 completed |
| Folios | 83 (Currier B) |

---

## Frozen Conclusion (Tier 0)

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

---

## Context System Structure

```
context/
├── CLAUDE_INDEX.md      ← START HERE
├── SYSTEM/              ← Methodology, tiers, stop conditions
├── CORE/                ← Frozen facts, falsifications
├── ARCHITECTURE/        ← Currier A/B/AZC, cross-system
├── CLAIMS/              ← 317 constraints (INDEX + files)
├── OPERATIONS/          ← OPS doctrine, program taxonomy
├── TERMINOLOGY/         ← Definitions
├── METRICS/             ← Quantitative facts
├── SPECULATIVE/         ← Tier 3-4 interpretations
└── MAPS/                ← Cross-references
```

---

## Navigation Rules

1. Read the **smallest file** that answers your question
2. Follow links for depth
3. Check tier before extending any claim
4. Never re-derive proven facts (Tier 0)
5. Never retry falsified hypotheses (Tier 1)

---

## Legacy Documentation

| File | Purpose |
|------|---------|
| `archive/CLAUDE_full_2026-01-06.md` | Full verbose version |
| `REVISION_LOG.md` | Change history |
| `MODEL_SCOPE.md` | Scope boundaries |

---

## Autonomous Escalation Rules

The assistant must **automatically consult the context system** when performing:

1. Token classification or reclassification
2. Parsing rules or morphological decomposition
3. System membership (A / B / AZC / HT / INVALID)
4. Validation or legality logic
5. Heuristics affecting structure

**Behavior:**
- Frozen constraints must be checked before proceeding
- Ambiguity must be surfaced, not smoothed over
- Pause and ask if implementation requires assuming unstated semantics

**Does NOT apply to:**
- UI layout or styling
- Pure refactors without semantic effect
- Performance or tooling changes

---

## Expert Sync Files

When asked to **"sync reference files for our expert"**, update these 4 files:

| File | Purpose | Generator |
|------|---------|-----------|
| `context/CONSTRAINT_TABLE.txt` | All constraints (Tier 0-2) | `python context/generate_constraint_table.py` |
| `context/MODEL_FITS/FIT_TABLE.txt` | All fits (F0-F4) | `python context/MODEL_FITS/generate_fit_table.py` |
| `context/MODEL_CONTEXT.md` | Architectural guide | Manual edit |
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | Tier 3-4 interpretations | Manual edit |

**Workflow:**
1. Run both generator scripts
2. Update MODEL_CONTEXT.md if structural understanding changed
3. Update INTERPRETATION_SUMMARY.md if speculative interpretations changed
4. Verify counts match (constraints, fits)

---

## App Development

Individual applications have their own structure files:

| App | Structure File |
|-----|----------------|
| Script Explorer | `apps/script_explorer/APP_STRUCTURE.md` |

App structure files define *where* code belongs.
This file defines *how to think* about the code.

---

*This file exists to redirect readers. Full documentation is in `context/`.*
