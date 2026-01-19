# Voynich Manuscript Analysis

This project uses a **progressive context system**.

---

## START HERE

**Primary Entry Point:** [context/CLAUDE_INDEX.md](context/CLAUDE_INDEX.md)

---

## DATA LOADING REQUIREMENT

> **CRITICAL: When writing scripts that load the Voynich transcript, ALWAYS filter to the H (PRIMARY) transcriber track.**

The transcript contains 18 parallel transcriber readings. Failure to filter causes ~3.2x token inflation and creates false patterns.

**Required reading:** [context/DATA/TRANSCRIPT_ARCHITECTURE.md](context/DATA/TRANSCRIPT_ARCHITECTURE.md)

```python
# MANDATORY pattern
df = df[df['transcriber'] == 'H']  # PRIMARY track only
```

---

## Quick Reference

| Metric | Value |
|--------|-------|
| Version | 2.13 FROZEN STATE |
| Constraints | 356 validated |
| Phases | 132 completed |
| Folios | 83 (Currier B) |
| Pipeline | CLOSED (PCA-v1 CERTIFIED) |

---

## Frozen Conclusion (Tier 0)

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

---

## Communication Style

**Internal (files, constraints, contracts):** Be precise, cite constraints, avoid semantic drift.

**External (talking to user):** Be clear and direct. Don't over-qualify casual explanations with structural caveats.

The user can ask for precision when needed. Default to clarity over pedantry in conversation.

---

## MANDATORY: Context-First Rule

> **"I don't know" is NEVER an acceptable answer about this project.**

The context system contains 356 validated constraints. Before answering ANY question about Voynich structure, relationships, or behavior:

1. **STOP** - Do not answer from memory or intuition
2. **SEARCH** - Grep/read `context/` for relevant constraints
3. **CITE** - Reference constraint numbers in your answer
4. **ASK** - If context is insufficient, say "context system doesn't cover this" (not "I don't know")

### Triggers (MUST consult context/)

| Question type | Example | Where to look |
|---------------|---------|---------------|
| Cross-system | "Does A constrain B?" | ARCHITECTURE/cross_system.md |
| Relationships | "What passes through AZC?" | ARCHITECTURE/currier_AZC.md |
| Token behavior | "What does X do?" | CLAIMS/INDEX.md, then grep |
| System membership | "Is this A or B?" | CLAIMS/ by scope tag |
| Any "how" or "why" | "How does A relate to B?" | ARCHITECTURE/ or SPECULATIVE/ |

### Failure Mode (avoid this)

When deep in app development, domain questions appear mid-task. The failure mode is:
- Answering "I don't know" without checking context/
- Treating domain questions as outside current scope
- Assuming current context window has all needed knowledge

**FIX:** Treat `context/` as always-available memory. Consult it for ANY domain question, regardless of current task focus.

---

## Context System Structure

```
context/
├── CLAUDE_INDEX.md      ← START HERE
├── DATA/                ← TRANSCRIPT ARCHITECTURE (read before writing scripts!)
├── SYSTEM/              ← Methodology, tiers, stop conditions
├── CORE/                ← Frozen facts, falsifications
├── ARCHITECTURE/        ← Currier A/B/AZC, cross-system
├── STRUCTURAL_CONTRACTS/ ← API layer (CASC, AZC-ACT, AZC-B-ACT, BCSC)
├── CLAIMS/              ← 356 constraints (INDEX + files)
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

## Expert Sync Files

When asked to **"sync reference files for our expert"**, update these 5 files:

| File | Purpose | Generator |
|------|---------|-----------|
| `context/CONSTRAINT_TABLE.txt` | All constraints (Tier 0-2) | `python context/generate_constraint_table.py` |
| `context/MODEL_FITS/FIT_TABLE.txt` | All fits (F0-F4) | `python context/MODEL_FITS/generate_fit_table.py` |
| `context/EXPERT_CONTEXT.md` | Combined expert context | `python context/generate_expert_context.py` |
| `context/MODEL_CONTEXT.md` | Architectural guide | Manual edit |
| `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` | Tier 3-4 interpretations | Manual edit |

**Workflow:**
1. Run all three generator scripts
2. Update MODEL_CONTEXT.md if structural understanding changed
3. Update INTERPRETATION_SUMMARY.md if speculative interpretations changed
4. Verify counts match (constraints, fits)

**Internal Expert:** The expert-advisor agent (`.claude/agents/expert-advisor/`) has the full constraint system embedded. It is invoked via automatic delegation - mention "ask the expert-advisor" or "have the expert validate" in your request.

---

## Agent Workflow: Expert Validation

When planning changes that affect the constraint system, structural contracts, or architectural documentation, request expert-advisor validation before finalizing.

**Triggers for expert validation:**
- Adding or modifying constraints (CLAIMS/)
- Updating structural contracts (CASC, BCSC, ACT files)
- Proposing new interpretations (SPECULATIVE/)
- Any change that might conflict with Tier 0-2 constraints

**How to invoke:** Simply request validation naturally:
- "Ask the expert-advisor to validate this proposal"
- "Have the expert check if this conflicts with existing constraints"
- "Get expert validation on whether this should be Tier 2 or 3"

Claude will automatically delegate to the expert-advisor agent based on the request.

**Why this matters:** The expert-advisor has all 356 constraints embedded in its system prompt. Delegation runs in isolated context, avoiding context bloat.
---

## App Development

Individual applications have their own structure files:

| App | Structure File |
|-----|----------------|
| Script Explorer | `apps/script_explorer/APP_STRUCTURE.md` |

App structure files define *where* code belongs.
This file defines *how to think* about the code.

### MANDATORY: Context Engagement During App Work

When working on apps, visualizations, or any tangent project in this repository:

1. **Domain questions don't pause** - Structural questions arise mid-implementation
2. **Context system is always available** - Treat it as external memory
3. **Check before guessing** - Never assume you know Voynich structure from memory

**Triggers that MUST engage context system:**
- "How should I represent..." → Check structural contracts first
- "Is this valid..." → Check constraints
- "What are the rules for..." → Check CASC or architecture docs
- "Can A do X..." → Check participation rules
- Any uncertainty about Voynich structure → STOP and check

**Failure modes to avoid:**
- Implementing based on vague recollection
- Hardcoding structural assumptions without verification
- Treating domain questions as "out of scope" for current task
- Saying "I think..." instead of "constraint C### says..."

---

## Structural Contracts (API Layer)

For quick structural validation without reading dozens of constraints, use **Structural Contracts**:

| System | Contract File | Use When |
|--------|---------------|----------|
| Currier A | `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` | Any A structure question |
| A->AZC | `context/STRUCTURAL_CONTRACTS/azc_activation.act.yaml` | How AZC affects A entries |
| AZC->B | `context/STRUCTURAL_CONTRACTS/azc_b_activation.act.yaml` | How AZC legality propagates to B |
| Currier B | `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` | B internal grammar, kernel, hazards |

### CASC Priority Rule

For Currier A questions about:
- Record types (1-token vs 2+ token)
- Morphology (PREFIX/MIDDLE/SUFFIX)
- Line structure (batch semantics, repetition)
- Participation rules (AZC, HT, B interaction)
- Positional properties
- What interpretations are DISALLOWED

**Check `currierA.casc.yaml` FIRST.** This is the shallow API. Only drill into constraints if CASC is insufficient.

```
Question about Currier A structure?
  ↓
Read currierA.casc.yaml (single file, ~350 lines)
  ↓
Answer found? → Done
  ↓
Need more detail? → Follow provenance to specific constraints
```

### AZC-ACT Priority Rule

For questions about A->AZC transformation:
- What happens when A entries enter AZC positions
- Positional legality (C, P, R-series, S-series zones)
- Compatibility filtering (MIDDLE incompatibility)
- Escape permission by position
- Constraint inheritance into B

**Check `azc_activation.act.yaml` FIRST.** This is the A-facing interface, not standalone AZC structure.

```
Question about A->AZC transformation?
  ↓
Read azc_activation.act.yaml
  ↓
Answer found? → Done
  ↓
Need AZC->B propagation? → Use AZC-B-ACT
```

### AZC-B-ACT Priority Rule

For questions about AZC->B propagation:
- How AZC legality affects B execution
- What B receives from AZC (legality, intervention permission)
- What B does NOT receive (A entries, AZC structure, reasons)
- Escape rate transfer and restriction inheritance
- Why B is "blind" to upstream mechanics

**Check `azc_b_activation.act.yaml` FIRST.** This is the AZC-output-facing interface, not B internal structure.

```
Question about AZC->B propagation?
  ↓
Read azc_b_activation.act.yaml
  ↓
Answer found? → Done
  ↓
Need B internal grammar? → Use BCSC
```

### BCSC Priority Rule

For questions about Currier B internal grammar:
- 49 instruction classes and role taxonomy
- Kernel structure (k, h, e operators)
- Hazard topology (17 forbidden transitions, 5 classes)
- Program structure (folio = program, line = control block)
- Convergence behavior (STATE-C, MONOSTATE)
- LINK operator (monitoring/intervention boundary)
- Recovery architecture (escape routes, stability anchor)
- Design freedom (hazard clamped, recovery free)

**Check `currierB.bcsc.yaml` FIRST.** This is the pure internal grammar, independent of A and AZC.

```
Question about B internal grammar?
  ↓
Read currierB.bcsc.yaml
  ↓
Answer found? → Done
  ↓
Need A/AZC context? → Use CASC, AZC-ACT, or AZC-B-ACT
```

---

*This file exists to redirect readers. Full documentation is in `context/`.*
