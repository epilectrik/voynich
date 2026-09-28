# Model Boundary (Tier 0)

**Status:** LOCKED | **Tier:** 0

> **Status note (v7.25, 2026-09-28).** Tier 0 was restated on 2026-09-28 (human sign-off) to its measured core. The
> generated `CONSTRAINT_TABLE.txt` and `SYSTEM/STATUS_BRIEF.md` outrank this page. The Tier-0 conclusion now reads:
>
> > Currier B is written in a single, compact token grammar: 49 classes covering 69.5% of its tokens, organised by line
> > with positional zones and word-boundary glyph coupling, and applied in folio units that share the grammar while
> > carrying their own vocabulary. This structure is not reproduced by copy-and-modify generation or by the Naibbe cipher
> > as published.
>
> Basis: C121, C124 (as corrected); C956, C357; C1212, C1563 (with PHASE_761); C531, C1790; C2077, C2080. The earlier
> Tier-0 reading ("closed-loop, kernel-centric control programs ... narrow viability regime") is now a Tier-3 working
> interpretation (procedural notation) with its supports withdrawn. In the table below, the kernel, hazard, convergence
> and LINK rows are historical (STATUS_BRIEF §3). For the list of measurements that stand, see STATUS_BRIEF §2.

---

## What the Manuscript DOES Encode (Proven)

### Currier B (61.9% of tokens, 83 folios)

| Layer | Content | Evidence |
|-------|---------|----------|
| **Executable Grammar** | 49 instruction classes, 100% coverage of the grammar's own vocabulary = 69.5% of B tokens (C121, C124 as corrected; "executable" is the Tier-3 reading) | Phase 20: 9.8x compression |
| ~~**Kernel Control**~~ | ~~3 operators (k, h, e) with mandatory STATE-C~~ **Withdrawn:** C089 superseded by C2082 (glyph-level re-test MIXED — k shows nothing; the e/bench signal is word-ending routing); C079 Tier 3 | ~~Phase 15: 0/100 surrogates reproduced~~ (per the C089 row, the only documented evidence — an adversarial-audit surrogate test — is uninformative) |
| ~~**Hazard Topology**~~ | ~~17 forbidden transitions in 5 failure classes~~ **Withdrawn:** zero bigrams reduce to composition, zones and boundary coupling (C2081, supersedes C957); class level demoted (C783); taxonomy imposed (C2060) | Phase 18 (historical) |
| **Convergence** → occupancy | ~~Dominant convergence to STATE-C~~ 57.8% of folios end in their dominant macro-state — measurement only (C074, Tier 2); no sequential convergence (C1401–C1403) | Phase 13-14, SEL-F |
| ~~**LINK Operator**~~ | ~~Deliberate non-intervention (38% of text)~~ **Withdrawn:** true density 13.2%, 38% not reproducible (C609); LINK is a morphological artifact of "ol" (C1174) | Phase 16 (historical) |
| **Folio units** | Folios share one grammar while carrying their own vocabulary (C531); no duplicate lines or paragraphs (C1790). "Folio = program" is the Tier-3 reading | Phase 22: 83 folios enumerated |
| **Line organisation** | Lines 3.3x more regular than random (C357); positional zones (C956); boundary glyph coupling (C1212, C1563). "Control block / micro-stage" is the Tier-3 reading | Phase LINE; PHASE_761 |

### Currier A (30.5% of tokens, 114 folios)

| Layer | Content | Evidence |
|-------|---------|----------|
| **Non-sequential registry** | Categorical entries, not executable programs | Phase CAS |
| **Marker system** | 8+ mutually exclusive prefix families | Phase CAS |
| **Compositional morphology** | PREFIX + MIDDLE + SUFFIX structure | Phase CAS-MORPH |
| **Section isolation** | 100% section-exclusive vocabulary | Phase CAS-DEEP [unverified: the matching CAS-DEEP row appears to be C255 "Blocks 100% section-exclusive", invalidated (Tier 1) with C250 — check before citing] |

### AZC (8.7% of tokens, 30 folios)

| Layer | Content | Evidence |
|-------|---------|----------|
| **Hybrid mode** | Bridges A and B vocabulary (60.5% shared) | Phase AZC |
| **Placement coding** | Finite placement classes (C, P, R1-R3, S-S2, Y) | Phase AZC-PLACEMENT |
| **Diagram anchoring** | Tokens are position-locked to diagram features | Phase AZC-AXIS |

---

## What the Manuscript DOES NOT Encode (Proven)

> **Scope note (v7.25):** exclusions are scoped to what was tested (STATUS_BRIEF §4; `falsifications.md`).
> Excluded: natural language written one token per word (C132, C2015, C2022); token ≈ word codes, atom-level
> polyalphabetic ciphers and three published decipherments (C1976, C2017); the Naibbe verbose homophonic cipher as
> published (C2080); Timm & Schinner copy-and-modify (C2077); a table walk over a coordinate lookup (C2079).
> **Untested:** syllable- or word-level codebooks, modified verbose ciphers, the Rugg grille. Excluding a rival is not
> evidence for the working interpretation.

| Claim | Status | Evidence |
|-------|--------|----------|
| **Language** | FALSIFIED (scoped: natural language written one token per word) | ~~Phase X.5: 0.19% reference rate~~ (tainted statistic, not relied on — C130/C131); now C132, C2015, C2022 |
| **Cipher** | FALSIFIED (scoped to the tested classes — see note above) | Phase G: transforms DECREASE MI; C1976, C2017, C2080 |
| **Glyph Semantics** | FALSIFIED | Phase 19: 0 identifier tokens [where the same "no identifier tokens" evidence is used against herbarium/taxonomy, SYSTEM/NEGATIVE_AUDIT.md Disposition 1 rates it SUSPECT (unstated threshold)] |
| **Illustration-Dependent Logic** | FALSIFIED | Phase ILL: swap invariance p=1.0 |
| **Step-by-Step Recipe** | FALSIFIED (format only — scope-restricted 2026-06-05, see falsifications.md) | Phase FSS: families are emergent |
| **Material Encoding** | FALSIFIED | Pure operational, 0 referent tokens ["pure operational" is interpretive — C120 demoted to Tier 3; the negative part is carried by C119] |
| **Ingredient Lists** | FALSIFIED | No quantities, no materials |

---

## What the Operator Provides (Not Encoded)

*[Tier-3 working interpretation: this section and the next assume the control-program reading, whose supports are withdrawn (STATUS_BRIEF §1, §3).]*

The text assumes an expert operator who brings:

| Knowledge | Why Not Encoded |
|-----------|-----------------|
| **Sensory completion judgment** | "When to stop" requires physical observation |
| **Material selection** | "What to process" is external to the control system |
| **Hazard recognition** | Physical signs (smoke, overflow) can't be encoded |
| **Process initiation** | Text assumes operator is already at the apparatus |
| **Equipment setup** | Physical configuration is tacit knowledge |

This is **consistent with a reference manual**, not a teaching text.

---

## What the Text Provides

| Information | How Encoded |
|-------------|-------------|
| **WHERE in the sequence** | Position in token stream |
| **WHAT to do at each step** | Instruction class (49 types) |
| ~~**What NOT to do**~~ | ~~Forbidden transitions (17 specific)~~ withdrawn — no prohibition layer remains (C2081) |
| ~~**When to wait**~~ | ~~LINK tokens (38% of text)~~ withdrawn — LINK is 13.2% and a morphological artifact (C609, C1174) |
| **Program organization** | Folio = complete program, Line = control block (Tier-3 reading of folio units and line organisation) |

---

## Scope Boundaries

### Inside Scope (Recoverable Internally)
- Grammar structure and rules
- Transition patterns and constraints
- Token classification and roles
- Program organization and flow
- ~~Hazard topology~~ (withdrawn — C2081; STATUS_BRIEF §3)

### Outside Scope (Requires External Evidence)
- Specific substances or products
- Natural language equivalents
- Author identity or school
- Dating or geographic origin
- Illustration meanings
- Apparatus construction details

**Rule:** Claims about outside-scope topics belong to Tier 3-4.

---

## The Three Systems

| System | Function | Relationship |
|--------|----------|--------------|
| **Currier B** | Sequential executable programs (Tier-3 reading; Tier 0 is the measured grammar) | Primary control content |
| **Currier A** | Non-sequential categorical registry | Parts catalog / index |
| **AZC** | Hybrid diagram annotation | Labeling / position marking |

- A and B are **folio-disjoint** (0 shared folios)
- A and B are **grammar-disjoint** (different formal systems)
- A, B, and AZC are **vocabulary-integrated** (shared type system)

See [../ARCHITECTURE/cross_system.md](../ARCHITECTURE/cross_system.md) for details.

---

## Navigation

← [frozen_conclusion.md](frozen_conclusion.md) | [falsifications.md](falsifications.md) →
