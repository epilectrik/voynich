# Fit Registry Index

**Version:** 2.0 | **Last Updated:** 2026-01-11

---

> **WARNING:** No entry in this registry constrains the model.
> Fits demonstrate explanatory sufficiency. They do NOT restrict behavior.
> Fits are NEVER constraints. See [FIT_METHODOLOGY.md](../SYSTEM/FIT_METHODOLOGY.md) for governance.

---

## Quick Reference

| Metric | Value |
|--------|-------|
| Total Fits | 11 |
| F0 (Trivial) | 0 |
| F1 (Failed) | 4 |
| F2 (Adequate) | 4 |
| F3 (Compelling) | 3 |
| F4 (Exploratory) | 0 |

---

## Navigation by System

| System | File | Fit Count |
|--------|------|-----------|
| Currier A | [fits_currier_a.md](fits_currier_a.md) | 8 |
| Currier B | [fits_currier_b.md](fits_currier_b.md) | 0 |
| AZC | [fits_azc.md](fits_azc.md) | 0 |
| Human Track | [fits_ht.md](fits_ht.md) | 0 |
| Global | [fits_global.md](fits_global.md) | 3 |

### Documentation Standard

Fits use a **two-layer format** (like constraints):
- **Header:** Standardized for programmatic parsing
- **Body:** Full methodology for human reference

See [FIT_METHODOLOGY.md](../SYSTEM/FIT_METHODOLOGY.md) for the complete standard.

### Supporting Documents

| Document | Purpose |
|----------|---------|
| [ecr_stress_tests.md](ecr_stress_tests.md) | ECR-1 stress test results |

---

## Fit Tier Definitions

| Tier | Label | Meaning | Constraint Effect |
|------|-------|---------|-------------------|
| **F0** | TRIVIAL | Definitional or tautological fit | None |
| **F1** | FAILED | Negative knowledge - model did not explain | None |
| **F2** | ADEQUATE | Simple model sufficient for observed pattern | None |
| **F3** | COMPELLING | Strong but non-necessary explanation | None |
| **F4** | EXPLORATORY | Provisional modeling attempt | None |

**Critical:** No fit at any tier constrains the model.

---

## All Fits by System

### Currier A (F-A-###)

| ID | Fit | Tier | Result | Supports |
|----|-----|------|--------|----------|
| F-A-001 | Compositional Token Generator | F2 | PARTIAL | C267-C282 |
| F-A-002 | Sister-Pair Classifier | F1 | NULL | C407-C410 |
| F-A-003 | Repetition Distribution | F2 | PARTIAL | C250-C258 |
| F-A-004 | Entry Clustering HMM | F2 | SUCCESS | C424 |
| F-A-005 | Scarcity-Weighted Registry Effort | F1 | NULL | C293 |
| F-A-007 | Forbidden-Zone Attraction | F1 | NULL | C281 |
| F-A-008 | Repetition as Relational Stabilizer | F1 | NULL | C287-C290 |
| F-A-009 | Comparability Window | F2 | SUCCESS | C424 |

### Currier B (F-B-###)

*No fits logged yet.*

### AZC (F-AZC-###)

*No fits logged yet.*

### Human Track (F-HT-###)

*No fits logged yet.*

### Global (F-ECR-###)

| ID | Fit | Tier | Result | Supports |
|----|-----|------|--------|----------|
| F-ECR-001 | Material-Class Identification | F3 | SUCCESS | C109-C114, C232 |
| F-ECR-002 | Apparatus-Role Identification | F3 | SUCCESS | C085-C108, C171, C216 |
| F-ECR-003 | Decision-State Semantics | F3 | SUCCESS | C384, C404-C405, C459-C460 |

See also: [ecr_stress_tests.md](ecr_stress_tests.md) for validation of F-ECR-001.

---

## Numbering Convention

| Scope | Prefix | Example |
|-------|--------|---------|
| Currier A | F-A-### | F-A-001 |
| Currier B | F-B-### | F-B-001 |
| AZC | F-AZC-### | F-AZC-001 |
| Human Track | F-HT-### | F-HT-001 |
| Global | F-G-### | F-G-001 |

---

## Language Rules

### Allowed (Fit-Safe)
- "explains", "accounts for", "is sufficient to generate"
- "collapses the need for", "supports existing constraints"
- "fails exactly where expected"

### Forbidden
- "governs", "determines", "rules", "encodes"
- "necessitates", "defines legality", "is required for"

---

## Navigation

← [../CLAIMS/INDEX.md](../CLAIMS/INDEX.md) (Constraints) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
