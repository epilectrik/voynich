# Tier 0 Core Constraints

**Scope:** Frozen facts proven by internal structural analysis
**Status:** FROZEN - Do not reopen

---

## C074 - Dominant Convergence
→ See [C074_dominant_convergence.md](C074_dominant_convergence.md)

---

## C079 - Only STATE-C Essential
**Tier:** 0 | **Status:** FROZEN
System can reach completion only through STATE-C pathway.
**Source:** Phase 13-14

---

## C084 - System Targets MONOSTATE
**Tier:** 0 | **Status:** FROZEN
Grammar architecture targets single stable state (STATE-C). 42.2% non-STATE-C endings are incomplete runs, not alternative endpoints.
**Source:** Phase 13-14, SEL-F revision

---

## C109 - 5 Hazard Failure Classes
→ See [C109_hazard_classes.md](C109_hazard_classes.md)

---

## C115 - 0 Non-Executable Tokens
**Tier:** 0 | **Status:** FROZEN
Every token in Currier B corpus maps to exactly one instruction class. Zero tokens require special handling or fall outside grammar.
**Source:** Phase 19

---

## C119 - 0 Translation-Eligible Zones
**Tier:** 0 | **Status:** FROZEN
No region of the manuscript contains natural language or cipher text eligible for translation. PURE_OPERATIONAL throughout.
**Source:** Phase 19

---

## C120 - PURE_OPERATIONAL Verdict
**Tier:** 0 | **Status:** FROZEN
Final classification: The Currier B text is an operational control notation, not language, cipher, or symbolic text.
**Source:** Phase 19

---

## C121 - 49 Instruction Classes
→ See [C121_49_instruction_classes.md](C121_49_instruction_classes.md)

---

## C124 - 100% Grammar Coverage
→ See [C124_grammar_coverage.md](C124_grammar_coverage.md)

---

## ~~C131~~ - [RETRACTED 2026-05-19]
**Tier:** 1 (RETRACTED) | **Status:** FALSIFIED via discriminating control
Originally claimed: "Token role consistency is 23.8%, inconsistent with linguistic encoding."
**Audit:** Value does not reproduce on H-only-filtered current data (re-run = 12.2%, pre-v2.42 transcriber filter bug). Observed value sits at within-line shuffle null mean (z=+0.69, effect size +0.3pp). Threshold ">80% = DSL signal" was theoretical, never calibrated. Note: C131 was inconsistently listed here as Tier 0 but was Tier 2 in INDEX.md; the inconsistency is itself an audit finding. Language-hypothesis falsification is independently supported by C130 (reference rate 0.19% vs 5% threshold), C132 (pre-registered closure), C173, substrate quintet (C2015/C2022/C2032), and kernel architecture (C089/C503.c/C521).
**See:** [INDEX.md C131 entry](INDEX.md), `phases/C131_AUDIT/`, memory `feedback_made_up_threshold_audit.md`.

---

## C171 - Closed-Loop Control Only
→ See [C171_closed_loop_only.md](C171_closed_loop_only.md)

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
