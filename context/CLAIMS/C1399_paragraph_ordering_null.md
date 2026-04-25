# C1399: Paragraph Ordering Within Folios (NULL)

**Tier:** 2 (ESTABLISHED)
**Scope:** B, paragraph, ordering, folio, sequence
**Phase:** PARAGRAPH_ORDERING_WITHIN_FOLIOS (Phase 511)
**Extends:** C1398 (paragraph operational gradient), C845 (paragraph self-containment), C862 (parallel programs verdict)
**Relates to:** C1288 (within-folio paragraph coherence), C855 (folio role template), C1378 (material differentiation NULL)

---

## Statement

Paragraphs within folios show **no preferred execution ordering at the corpus-aggregate level when measured against operational-zone composition**. The 4 operational gradient zones (C1398: THERMAL-QO, CONTAINMENT-Sealing, OPERATION-Iteration, MONITORING-Phase) do not follow a procedural sequence by zone composition. There is no thermal-first/monitoring-last ramp. All 8 tests for sequential structure fail except the transition matrix (T4), which reveals **zone inertia** (self-transition O/E=2.02) rather than sequential ordering. Folios run consecutive paragraphs of the same operational type, not a progression through different phases.

> **SCOPE NOTE (added 2026-04-25, Phase 643):** This finding applies to corpus-aggregate composition-vs-position measurements. It does **NOT** test:
> - Paragraph layout-order vs external recipe-phase order on matched folios (see C-NEW Phase 643: layout-order tracks recipe-phase on matched folios at rho=+0.81)
> - Operational interchangeability (whether shuffling paragraph order preserves operational outcome)
> - Within-individual-folio sequence relative to external referents
>
> The "parallel subroutines, not sequential steps" interpretation in the original Phase 511 framing was an interpretive overreach beyond the actual measurements. The statistical core (zone-composition does not predict folio-position at corpus scale) remains valid.

---

## Key Findings

### T1: Zone Ordinal Position — FAIL (KW p=0.289)

Zones do not have distinct positional preferences within folios.

| Zone | Mean Ordinal | n |
|------|-------------|---|
| Z3 MONITORING | 0.412 | 33 |
| Z1 CONTAINMENT | 0.467 | 52 |
| Z0 THERMAL | 0.509 | 87 |
| Z2 OPERATION | 0.555 | 69 |

KW H=3.760, p=0.289, epsilon-squared=0.016 (negligible). All zones cluster at ~0.5.

### T2: First-Paragraph Zone — FAIL (p=0.452)

THERMAL-QO shows mild opener tendency (35%, O/E=1.40) but not significant against proportional baselines (chi2=2.63, p=0.452).

### T3: Last-Paragraph Zone — FAIL (p=0.470)

No zone significantly enriched as closer. OPERATION-Iteration has highest last-paragraph rate (37.5%) but reflects zone size, not positional preference.

### T4: Transition Matrix — PASS (chi2=99.1, V=0.424)

The transition matrix IS structured — but the structure is **zone inertia**, not sequential ordering. Self-transitions dominate.

### T5: Bigram Enrichment — INERTIA, NOT SEQUENCE

| Transition | O/E | Interpretation |
|-----------|-----|----------------|
| Z3→Z3 MONITORING→MONITORING | **3.01** | Strongest self-repeat |
| Z1→Z1 CONTAINMENT→CONTAINMENT | **2.75** | Strong self-repeat |
| Z0→Z0 THERMAL→THERMAL | **1.96** | Strong self-repeat |
| Z2→Z2 OPERATION→OPERATION | **1.56** | Moderate self-repeat |
| Z0→Z3 THERMAL→MONITORING | **0.12** | Most depleted |
| Z3→Z0 MONITORING→THERMAL | **0.20** | Second most depleted |

Overall self-transition O/E = **2.02** (103 observed vs 50.9 expected). Paragraphs are twice as likely to repeat the same zone as expected under independence.

THERMAL↔MONITORING mutual avoidance (O/E 0.12/0.20) reflects different program types (different sections/REGIMEs), not sequential incompatibility.

### T6: Monotonicity — FAIL (rho=-0.052, p=0.611)

Mean within-folio Spearman correlation between paragraph ordinal and zone number: -0.052. 15 positive, 20 negative, 5 zero. No ramp.

### T7: First-Half vs Second-Half — FAIL (p=0.374)

Zone distributions in first and second half are statistically identical (chi2=3.12, V=0.114). MONITORING is 1.70x enriched in the first half — opposite of any "monitoring comes last" sequence.

### T8: Section-Controlled — ALL FAIL

Within every section (B, C, H, S), zone ordinal tests non-significant (all p>0.17). Within-section monotonicity non-significant (all p>0.57). The absence of ordering is genuine, not a section confound.

---

## Interpretation (revised 2026-04-25)

At the corpus-aggregate composition level, folios do not show a thermal-first/monitoring-last ramp. The zone inertia (self-transition 2.02x) means folios tend to cluster consecutive paragraphs doing the same kind of work — a thermal folio runs mostly thermal paragraphs, a containment folio runs mostly containment paragraphs.

Combined with C1398 (continuous operational gradient) and C1378 (same material across paragraphs):
- Same material (C1378)
- Different operational emphases (C1398)
- No corpus-aggregate composition-vs-position ordering (C1399, scoped)
- Same-type clustering within folios (zone inertia)

**The folio-program specifies WHAT operational concerns to address and HOW MUCH of each at the composition level. This does not address whether paragraph layout-order on the page reflects external operational sequence (e.g., recipe phases) on individual folios — that is outside this measurement's scope.**

Phase 643 (PARAGRAPH_ORDERING_DISAMBIGUATION) demonstrated empirically that on confirmed-match folios, paragraph layout-order DOES track recipe-phase order (rho=+0.81 across 5 matches). C1399's measurement is preserved; its earlier framing as "parallel subroutines, not sequential steps" was an interpretive overreach now scoped accordingly.

---

## Falsification Criteria

1. If a larger paragraph set (relaxing 3+ body line filter) reveals significant ordering, the body-length filter biases this result
2. If within-REGIME ordering emerges at finer granularity (sub-zone), the 4-zone resolution is too coarse
3. If zone inertia disappears under folio-length control, it's a folio-size artifact

---

## Method

- 264 paragraphs from Phase 510 labels (3+ body lines, 80 folios)
- 57 folios with 2+ paragraphs, 40 with 2+ distinct zones
- 8 tests: ordinal position, first/last paragraph, transition matrix, bigram enrichment, monotonicity, half-split, section control
- Kruskal-Wallis, chi-squared, Spearman, permutation tests
- Random seed 42

**Script:** `phases/PARAGRAPH_ORDERING_WITHIN_FOLIOS/scripts/paragraph_ordering.py`
**Results:** `phases/PARAGRAPH_ORDERING_WITHIN_FOLIOS/results/paragraph_ordering.json`
