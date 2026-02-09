# Revision Log

Document version history tracking superseded claims and constraint revisions.

---

## v1.0 - Initial Frozen Model (Pre-AZC)

- 49-class grammar established
- 17 forbidden transitions identified
- 5 hazard classes defined
- Corpus split: A (31.8%) + B (64.7%) = 96.5%
- Initial claim: "100% convergence to STATE-C"

## v1.1 - SEL-D Hazard Audit

**Revisions:**
- Hazard bidirectionality: ~~100%~~ → 65% asymmetric (Constraint 111)
- Kernel adjacency: ~~"KERNEL_ADJACENT clustering"~~ → 59% distant from kernel (Constraint 112)
- CONTAINMENT_TIMING class: functional → theoretical-only (0 corpus impact)

## v1.2 - SEL-F Convergence Audit

**Revisions:**
- STATE-C convergence: ~~100%~~ → 57.8% terminal (Constraint 74, 323)
- OPS-R contradiction: RESOLVED (definitional ambiguity, not formal contradiction)
- Added Constraints 323-327 (terminal state distribution, completion gradient)

## v1.3 - AZC Discovery

**Revisions:**
- Corpus rebalanced: A(30.5%) + B(61.9%) + AZC(7.7%) = 100%
- Prior binary A/B model → Ternary A/B/AZC model
- Added Constraints 300-322 (AZC hybrid classification, placement-coding axis)

## v1.4 - HTD Phase

**Revisions:**
- Constraint 172 (HT 99.6% LINK-proximal): **SUPERSEDED** by Constraint 342
- HT-LINK decoupling confirmed (ρ=0.010, p=0.93)
- Added Constraints 341-344 (HT-program stratification, HT-A inverse coupling)

## v1.5 - Hygiene Cleanup (2026-01-07)

**Changes:**
- Updated Frozen Conclusion corpus percentage: 64.7% → 61.9%
- Marked Constraint 172 as SUPERSEDED
- Updated Key Structural Findings section: removed outdated "100% convergence" claim
- Added REVISION_LOG.md (this file)
- Added MODEL_SCOPE.md (scope boundaries)
- Added version header to CLAUDE.md

## v1.6 - CAS-FOLIO Phase (2026-01-07)

**Additions:**
- Added Constraints 345-346 (Currier A folio coherence)
- Constraint 345: No folio-level thematic coherence (within=between, p=0.997)
- Constraint 346: Sequential coherence confirmed (adjacent 1.31x more similar, p<0.000001)
- Total constraints: 344 → 346

## v1.7 - HT-MORPH + HT-STATE Phases (2026-01-07)

**Additions:**
- Added Constraints 347-348 (Human Track structural closure)
- Constraint 347: HT is a third compositional notation system with DISJOINT prefix vocabulary from A/B; 71.3% decomposable into HT_PREFIX + MIDDLE + SUFFIX
- Constraint 348: HT prefixes are phase- and context-synchronized (position effect -0.25, grammar V=0.136 p<0.0001, regime V=0.123)
- Total constraints: 346 → 348

**Key Finding:**
- Human Track is NOT residue/noise but a formal, learned, non-executing annotation system
- Three notation systems confirmed: Currier A (registry), Currier B (grammar), Human Track (annotation)
- HT prefix vocabulary (yk-, op-, yt-, sa-, etc.) is COMPLETELY DISJOINT from A/B prefixes (ch-, qo-, sh-, etc.)
- HT structural exhaustion achieved: morphology formalized, synchrony demonstrated, role bounded

## v1.8 - Damaged Token Recovery (2026-01-07)

**Additions:**
- Created `data/transcriptions/recovery_patches.tsv` (1,215 recoverable damaged tokens)
- Created `lib/transcription.py` (loader with optional recovery)
- Recovery validation: 5 tests passed (frequency stability, grammar stability, HT stability, sensitivity)
- See `RECOVERY_VALIDATION.md` for full validation report

**Key Statistics:**
- 1,392 damaged tokens total (with `*` characters)
- 148 CERTAIN (10.6%), 265 HIGH (19.0%), 802 AMBIGUOUS (57.6%), 177 unrecoverable (12.7%)
- Recovery does NOT change structural conclusions (validated)

## v1.9 - MORPH-CLOSE Phase (2026-01-07)

**Additions:**
- Added Constraints 349-352 (Final Morphology Closure)
- Extended cluster prefix inventory: pch, tch, kch, dch, fch, rch, sch (7 new)
- HT+B hybrids recognized: HT prefix + B suffix = 12.47% of corpus (explained, not orphan)
- Total constraints: 348 → 352

**Final Classification:**
- 92.66% EXPLAINED (B grammar + clusters + HT + hybrids)
- 3.90% AMBIGUOUS (known components in unclear position)
- 2.82% NOISE (single chars + unrecoverable damaged)
- 0.62% TRUE ORPHAN (consonant ligatures, scribal fragments)

**Key Finding:**
- Morphology is CLOSED
- No unaccounted formal system remains
- TRUE ORPHAN residue (0.62%) = consonant ligatures (dl, lr, ld), vowel-initial fragments, scribal artifacts

---

## Superseded Claims Registry

| Original Claim | Location | Superseded By | New Value |
|----------------|----------|---------------|-----------|
| 64.7% Currier B | Line 19 | AZC discovery | 61.9% |
| 100% convergence to STATE-C | Line 292 | SEL-F (Constraint 323) | 57.8% terminal |
| 100% bidirectional hazards | implicit | SEL-D (Constraint 111) | 65% asymmetric |
| KERNEL_ADJACENT clustering | implicit | SEL-D (Constraint 112) | 59% distant |
| HT 99.6% LINK-proximal | Constraint 172 | HTD (Constraint 342) | ρ=0.010 (decoupled) |

---

## Version Control Notes

- v1.5: Document hygiene; model structure unchanged
- v1.6: CAS-FOLIO phase adds 2 Tier 2 constraints (folio organization falsification)
- v1.7: HT-MORPH + HT-STATE phases add 2 Tier 2 constraints (Human Track structural closure)
- v1.8: Damaged token recovery infrastructure (no constraint changes; hygiene)
- v1.9: MORPH-CLOSE phase adds 4 Tier 2 constraints (morphology closure)
- **Total constraints: 352**
- Tier 0/1 constraint logic unchanged
- No tier promotions applied
- **Morphology structurally exhausted** — 0.62% irreducible residue
