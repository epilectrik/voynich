# C1968: ch-Class Paragraph-Header Compound-Specification Concentration

**Tier:** 2
**Scope:** B, paragraph, header-body, ch, compound-specification, channel-class
**Phase:** PHASE_655_HEADER_BODY_HT_GAP
**Date:** 2026-04-26
**Refines:** C929 (ch=active test, sh=passive monitor) with paragraph-architectural claim
**Pairs with:** C1967 supplement (body>header in e_depth) to establish channel-class header-body specialization
**Extends:** C1966 (HT density tracks compound specification, per-folio) to sub-paragraph (header-body) resolution
**Token-pool control:** C1789 (header-body vocabulary exclusivity 86%) caveat addressed via shared-token restriction

---

## Statement

Block-pure Currier B paragraphs with ch-dominant channel concentrate compound MIDDLE tokens (HT, per HTSC = compound-MIDDLE-bearing) at the paragraph header relative to the body.

**Shared-token-controlled gap: +0.066 (header HT rate − body HT rate), p = 0.007, n = 82 paragraphs.**

The effect survives token-pool control: even when restricting to tokens that appear in BOTH header and body positions across the paragraph set, ch-class paragraphs show significant header HT enrichment. The gap is not driven by header-exclusive vocabulary.

**Other channel classes do not show this genuine concentration after the same control:**
- qo-class shared-token gap: +0.012 (p=0.59, NS) — apparent gap was vocabulary artifact
- sh-class shared-token gap: -0.041 (p=0.29, REVERSED) — apparent gap was vocabulary artifact

The header-body HT division is therefore **ch-class-specific**, not a universal architectural feature.

---

## Empirical evidence

### Sample

- 220 block-pure paragraphs (per C1961, n>=8 tokens, >=2 lines, >70% block-pure)
- ch-dominant: 82 paragraphs
- qo-dominant: 102 paragraphs
- sh-dominant: 25 paragraphs

### Test 1: all-tokens header-body HT gap (paired t-test)

| Class | n | Header HT | Body HT | Gap | p |
|---|:---:|:---:|:---:|:---:|:---:|
| qo | 102 | 0.320 | 0.282 | +0.038 | 0.032 |
| ch | 82 | 0.359 | 0.272 | +0.088 | <0.0001 |
| sh | 25 | 0.319 | 0.269 | +0.050 | 0.35 |

### Test 2: shared-token control (the decisive test)

Restricted to token types appearing in BOTH header and body positions across the qualifying paragraph set (468 of 1212 header types are shared with body, ~38%).

| Class | n | Header HT (shared) | Body HT (shared) | Gap (shared) | p |
|---|:---:|:---:|:---:|:---:|:---:|
| qo | 102 | 0.242 | 0.230 | +0.012 | 0.59 |
| **ch** | **82** | **0.266** | **0.200** | **+0.066** | **0.007** |
| sh | 25 | 0.167 | 0.208 | -0.041 | 0.29 |

The qo gap collapses; the sh gap reverses; only the ch gap survives.

---

## Operational interpretation

ch-class paragraphs are dominated by ch-prefix tokens. Per C929, ch encodes active testing / discrete sampling. Active testing operations require explicit declaration of WHAT to test for before executing the test. The architecture concentrates this declarative content (compound MIDDLE tokens, encoding compound specifications per C935/C1966) at the paragraph header. The body then executes the test against the specified target.

This pattern is **specific to active testing**:
- qo (heat-driving): heat application is sustained throughout the paragraph; no need for front-loaded specification
- sh (passive monitoring): observation is continuous; no test-target to declare
- **ch (active testing): each test event requires specific target declaration**

The C1968 finding therefore identifies a **functional architectural feature**: the manuscript's grammar provides a paragraph-level header-spec convention specifically for active-test operations.

---

## Pairing with C1967 supplement

C1967 supplement found the inverse direction in e_depth: bodies > headers in thermal commitment, with cross-class gap-magnitude qo (-0.034) < ch (-0.062) < sh (-0.123). sh-class shows the largest e_depth body-concentration.

Combined channel-class architectural patterns:

| Class | HT header concentration | e_depth body concentration |
|---|:---:|:---:|
| qo | none (artifact-only) | small (-0.034) |
| **ch** | **+0.066 real** | medium (-0.062) |
| sh | reversed (-0.041) | **LARGE (-0.123)** |

**Each channel class has a distinct header-body specialization pattern, in different dimensions:**
- **ch concentrates compound-specification at header**
- **sh concentrates thermal-commitment at body**
- **qo is consistent throughout** in both dimensions

The header-body architectural division is NOT universal "headers=spec, bodies=execution." It's channel-class-specific, with each class concentrating different content according to its operational character.

---

## Why ch and not the others

- **ch (active test, per C929):** discrete events requiring explicit target specification. Header front-loads "what to test for"; body executes test. The operator must commit to specific target before testing — hence concentrated compound-spec at header.
- **qo (heat-driving):** continuous action; no discrete target events. No need for header-concentrated specification.
- **sh (passive monitoring):** continuous observation; no operator-driven events to set up. No need for header-concentrated specification. Thermal context emerges in body as it appears.

The asymmetry is operationally coherent: active testing is the only one of the three that has discrete event-execution, and event-execution is what creates the header-spec / body-execute division.

---

## Falsification

Would be falsified if:

1. The shared-token-controlled gap on ch-class drops below +0.03 with n>50, p>0.10
2. Another channel class (e.g., ot or ol) also shows a ≥+0.05 shared-token gap with significant p, breaking the "ch-only" specificity
3. A direct test of compound-MIDDLE position-deployment (rather than header-body aggregate) within ch paragraphs shows uniform distribution rather than head-loading

---

## Provenance

- `phases/PHASE_655_HEADER_BODY_HT_GAP/scripts/s1_header_body_ht_gap.py` (all-tokens test)
- `phases/PHASE_655_HEADER_BODY_HT_GAP/scripts/s2_token_pool_control.py` (shared-token control)
- `phases/PHASE_655_HEADER_BODY_HT_GAP/results/header_body_ht_density.json`
- `phases/PHASE_655_HEADER_BODY_HT_GAP/results/header_body_ht_token_pool_control.json`
- C929 (ch=active test) — refined by this constraint at paragraph-architecture resolution
- C935 (compound specification at line-1) — extended to channel-class-specific concentration
- C1966 (HT density tracks compound specification, per-folio) — extended to sub-paragraph resolution
- C1789 (header-body vocabulary exclusivity) — caveat addressed by token-pool control
- C1967 supplement (body>header in e_depth) — pairs to establish channel-class architectural patterns
