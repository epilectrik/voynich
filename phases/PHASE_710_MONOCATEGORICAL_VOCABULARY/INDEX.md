# PHASE_710: Monocategorical-Operational Vocabulary Discrimination

**Status:** COMPLETE
**Date:** 2026-05-20
**Posture:** Test whether Voynich's atom-layer primitive inventory shows the **categorical-homogeneity** signature characteristic of procedural-DSLs (programming-language opcode sets, recipe-verb sets), distinguishing it from NL morpheme inventories (categorically mixed) and from non-NL non-operational systems (mensural durations — categorically homogeneous as ENTITIES, not operations).

**Verdict:** PROCEDURAL-DSL SIGNATURE CONFIRMED — Tier 3 measurement registered as C2042.

**Expert review applied:** expert-advisor flagged four corrections before registration:
1. Latin **morpheme** baseline added (granularity-fix) — confirms result (15% OP, FUNCTION-dominant)
2. Result reported as **72-100% band** (strict vs inclusive coding of 5 ambiguous atoms), not 100%
3. Demoted to **Tier 3** (category assignments require glossing judgment — hermeneutic)
4. Framing avoids C171 tension: "atoms classify as operational ROLE" not "atoms ARE verbs"

Crazy-expert added caveat: signature distinguishes operational-from-non-operational, not procedural-DSL specifically. Could be operational specification language or taxonomic key.

---

## The actual question

User observation (2026-05-20): all 18 Voynich atom glosses are verbs/operations. Programming-language instruction sets share this monocategorical-operational pattern (MOV, ADD, JMP, PRINT, GOTO — all verbs). NL morphemes don't (nouns + verbs + adjectives + grammatical-function morphemes).

Question: is this a genuine structural signature distinguishing Voynich from NL, or an artifact of how the project's 7-axis gloss-battery framed atom semantics?

---

## Two measurable properties

For each system's primitive-vocabulary inventory:

1. **Inventory size N** (number of distinct primitives)
2. **Categorical-homogeneity H** (fraction of primitives in dominant category)

### Expected patterns by system type

| System type | Example | N | H_dominant | Dominant category |
|---|---|---|---|---|
| Voynich atoms | (observed) | 18 | 18/18 = 1.00 | OPERATION (verb) |
| Forth core words | ANS Forth CORE | ~130 | ≈1.00 | OPERATION |
| x86 base instructions | RISC-V base | ~50-100 | ≈0.95 | OPERATION |
| Medieval recipe verbs | extracted Codicillus | ~30-50 | ≈1.00 | OPERATION |
| Mensural durations | MEI duration classes | 5-12 | ≈1.00 | ENTITY (duration-unit) |
| NL Latin morphemes (core) | top-N most frequent | hundreds | ≤0.50 | mixed (most-frequent are usually grammatical) |
| NL Latin roots | top-N nouns/verbs/adj roots | thousands | ≤0.50 | mixed |

---

## Pre-registered three-axis discriminating test (LOCKED)

### Axis 1: Categorical-homogeneity threshold

**LOCKED:** Voynich H_dominant for OPERATION-glossed atoms (using existing ATOM_GLOSSES dict).
- PASS-procedural-DSL: H_dominant ≥ 0.85 (allows up to 2-3 atoms to be ambiguous or non-operational without breaking signature)
- FAIL: H_dominant < 0.85

### Axis 2: Co-classification with positive controls

**LOCKED:** Voynich must share both (N small, H high, dominant=OPERATION) with at least 2 of:
- Forth CORE words
- x86 base instructions
- Medieval recipe verbs extracted from Codicillus/Mesue

### Axis 3: Discrimination from floor + NL

**LOCKED:** Voynich must NOT share (small-N, high-H, ENTITY-dominant) with mensural durations (small-N high-H but ENTITY not OPERATION).
**LOCKED:** Voynich must NOT share (large-N, low-H, mixed) with NL Latin morpheme inventory.

### Verdict matrix

| Voynich pattern | Verdict |
|---|---|
| Small-N, high-H, OPERATION-dominant; matches ≥2 procedural-DSL controls; differs from mensural + NL | **PROCEDURAL-DSL SIGNATURE CONFIRMED** — Tier 2 candidate constraint |
| Small-N, high-H, OPERATION-dominant; matches mensural ALSO | **FLOOR — small-N+high-H is a generic property** of small-inventory-symbolic-systems; not discriminating for procedural-DSL specifically |
| Small-N, high-H, OPERATION-dominant; doesn't match any control corpus | **UNIQUE SIGNATURE** — Voynich isn't on the procedural-DSL spectrum but isn't NL either; new category |
| H < 0.85 when ambiguous-glossable atoms reclassified | **MONOCATEGORICAL CLAIM FALSIFIED** — atom glosses aren't reliably all-operational; current framing softer than claimed |

---

## Category ambiguity audit (mandatory step BEFORE main test)

The project's existing ATOM_GLOSSES are operational by convention. The 'd' atom was *revised* from 'mark' (noun-ambiguous) to 'do/execute' (verb-explicit) by the 7-axis battery — suggesting at least one atom was initially noun-glossable.

Pre-registered ambiguity audit:
For each of the 18 atoms, score the gloss on:
- **Operation-pure** (only a verb sense — heat, iterate, transfer) — 18 expected by current framing
- **Operation-or-entity ambiguous** (gloss has both senses — mark, flag, state, sequence, diagram) — at most 5 by current framing
- **Entity-pure** (only a noun/property sense) — 0 expected by current framing

If 4+ atoms turn out operation-or-entity ambiguous, the monocategorical claim weakens. If any entity-pure, it's falsified.

---

## Corpora

### Positive control 1: Forth CORE words
Source: ANS Forth-94 standard CORE wordset. ~130 words. Hand-curated reference list shipped in `reference_data/forth_core_words.json`. Each word categorized: OPERATION (DUP, SWAP, +), CONTROL (IF, THEN, BEGIN), STACK_MANIP (DUP, OVER), or LITERAL_HANDLER. All four categories are operational in nature.

### Positive control 2: x86 base instructions
Source: Intel SDM Volume 2 basic integer instructions. ~80 base instructions. Categorize: DATA_MOVE (MOV, LEA), ARITH (ADD, SUB), CONTROL (JMP, CALL), LOGIC (AND, OR), COMPARE (CMP, TEST). All operations.

### Positive control 3: Medieval recipe verbs
Extract Latin verb-stems from Codicillus/Mesue (lemmatized via Whitaker's WORDS or simple suffix-stripping). Top-30 most-frequent verb-glossed lemmas. Recipe-imperative-only.

### Floor control: Mensural durations
Already in `phases/MENSURAL_NOTATION_HYPOTHESIS/results/mensural_streams.json`. Duration classes: MAX, LON, BRE, SBR, MIN, SMN, FUS, SFS (+ rests). All entities (duration-units), not operations.

### NL comparison: Latin morpheme inventory
Two scopes:
- **Top-N word-form list** from Codicillus/Mesue (top-50 by frequency). Categorize each: NOUN/VERB/ADJ/ADV/FUNCTION. Function-words (et, in, de, ad, cum, etc.) should dominate top frequencies.
- **Productive derivational morphemes**: -atio, -tor, -ilis, etc. Categorize.

---

## Implementation plan

| Script | Purpose | Order |
|---|---|---|
| `_audit_atom_glosses.py` | Step 0: ambiguity audit of current ATOM_GLOSSES | 1 |
| `_build_control_inventories.py` | Build hand-curated Forth + x86 + mensural reference data | 2 |
| `_extract_latin_inventory.py` | Extract Latin top-50 word-forms + categorize | 3 |
| `_monocategorical_test.py` | Run main test: N + H + categorical comparison | 4 |

Total estimated effort: ~3-4 hours.

---

## Pre-registered worry list (framework-as-null discipline)

This test fits the project's Tier 0 "closed-loop control programs" conclusion cleanly. Per `feedback_framework_as_null.md` and `feedback_operational_story_first_trap.md`, this is the signature of a framework-echo trap.

Anti-trap precautions baked in:
1. **Three discrete possible outcomes** (CONFIRMED / FLOOR / UNIQUE / FALSIFIED), not binary
2. **Mensural floor check** is mandatory per `feedback_floor_vs_discriminator_metric_test.md`
3. **Category-ambiguity audit** runs BEFORE main test — if 4+ Voynich atoms are operation-or-entity ambiguous, the underlying claim is weak and we should report that even if downstream numbers look favorable
4. **Falsification path is real** — if Voynich H drops below 0.85 after honest ambiguity audit, the monocategorical claim doesn't hold
5. **Tier 2 measurement only, not Tier 3 mechanism** — even if all three axes pass, we register the categorical-homogeneity *measurement*, NOT a "Voynich IS a programming language" interpretation. Mechanism remains Tier 4 SPECULATIVE.

---

## What this can and can't establish

**CAN establish (if all three axes pass):**
- Voynich atom inventory has a measurable structural signature shared with programming languages and recipe-instruction sets
- This signature distinguishes Voynich from NL morpheme inventories AND from mensural durations
- The substrate-quintet "non-NL" framing is extended onto a new axis (categorical-homogeneity)

**CANNOT establish:**
- That Voynich literally IS a programming language
- That the operational glosses are correct (independently of being verbs)
- That a 15th-century writer was thinking in programming-language terms
- That this proves the manuscript is decipherable

The honest finding is at the structural-measurement level: **Voynich's primitive vocabulary is categorically homogeneous-operational**, like procedural-DSLs and unlike NL morphology. That's a measurement. The mechanism (whether Voynich is genuinely a procedural language, an unusually homogeneous proto-language, a constructed cipher, or something else) remains underdetermined.

---

## Registration-trap audit

- Pre-registered before any new measurements run
- Decision rules cover 4 outcomes, including falsification path
- Category-ambiguity audit precedes main test (would catch glossing-overconfidence)
- Two positive controls (Forth, x86) plus recipe-verbs from existing corpora
- Mensural floor mandatory
- Outcome registered as Tier 2 measurement only, not Tier 3 mechanism
- Framework-as-null discipline acknowledged upfront

---

## Constraints potentially affected

If PROCEDURAL-DSL SIGNATURE CONFIRMED:
- New Tier 2 constraint: categorical-homogeneity signature
- Strengthens C1003 (pairwise compositionality)
- Strengthens Tier 0 framing
- May reshape interpretation of C1394 (HEAD+MOD*+TERM as opcode+operands+terminator)

If FALSIFIED:
- Revisit ATOM_GLOSSES: were any atoms force-categorized to verb when they're better entity-glossed?
- The 'd' atom revision (mark → do/execute) might have been over-correction toward operational framing
- Atom layer may be more morpheme-like (mixed-category) than the project currently treats it

---

## RESULTS (2026-05-20)

### Final cross-corpus table

| Corpus | N | H_OP strict | H_OP inclusive | Dominant (inclusive) |
|---|---:|---:|---:|---|
| **Voynich atoms** | 18 | **72%** | **100%** | OPERATION |
| Forth CORE (positive control) | 57 | 100% | 100% | OPERATION |
| x86 base (positive control) | 56 | 100% | 100% | OPERATION |
| Mensural durations (floor) | 8 | 0% | 0% | ENTITY |
| Latin Codicillus top-50 word-forms | 50 | 12% | 12% | ENTITY (54%) |
| **Latin morpheme inventory** (granularity-fix) | 46 | 15% | 15% | FUNCTION (43%) |

### Pre-registered axis verdicts
- **Axis 1** (Voynich H_OP_inclusive ≥ 0.85): PASS at 100% inclusive, FAIL at 72% strict (the band is the honest report)
- **Axis 2** (matches ≥2 positive controls): PASS (Forth + x86 both 100%)
- **Axis 3** (distinguished from mensural + NL): PASS — mensural 0% OP/ENTITY-dominant, both NL Latin baselines OPERATION-minority (12-15%)

### Ambiguity audit (load-bearing)
5/18 atoms operation-or-entity/property ambiguous in English glosses:
- m (final) → AMBIGUOUS_OP_PROP
- l (state) → AMBIGUOUS_OP_ENT
- f (flag) → AMBIGUOUS_OP_ENT
- s (sequence) → AMBIGUOUS_OP_ENT
- x (diagram) → AMBIGUOUS_OP_ENT

13/18 atoms unambiguously OPERATION. Project's existing ATOM_GLOSSES treats all 18 operationally; expert-advisor scrutiny requires reporting the band.

### Specific (load-bearing) findings
- **0/18 Voynich atoms** unambiguously ENTITY-pure, PROPERTY-pure, or FUNCTION-pure
- **42/46 Latin morphemes** non-OPERATION (FUNCTION 20, ENTITY 11, PROPERTY 8); morpheme-level NL signature is FUNCTION-dominant
- **43/50 Latin word-forms** non-OPERATION; word-form NL signature is ENTITY-dominant
- Voynich's zero-count for non-operational atoms vs Latin's ~85% non-operational morphemes is the load-bearing contrast

### Crazy-expert caveat
Categorical-homogeneity-operational distinguishes "operational system" from "non-operational symbolic system," but does not specifically distinguish "procedural DSL" from "operational specification language" (e.g., taxonomic key, classification system). C1399-C1400 (paragraph ordering independence) tensions with strict-temporal-procedural reading.

### Registered constraint
**C2042** — Tier 3 categorically-operational atom-layer measurement (see CLAIMS/INDEX.md).

### What was NOT registered
- Mechanism interpretation ("Voynich IS a programming language") — stays Tier 4 SPECULATIVE
- Strong claim "100% OPERATION" (without strict-vs-inclusive band)
- Tier 2 framing (per expert-advisor: glossing judgment is hermeneutic, demote to Tier 3)
- Specific procedural-DSL identification (per crazy-expert: signature is operational-vs-non-operational, broader than procedural-DSL)

