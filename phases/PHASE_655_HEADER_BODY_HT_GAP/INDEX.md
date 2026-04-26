# Phase 655: Header-Body HT Density Gap

**Status:** COMPLETE
**Date:** 2026-04-26
**Constraint registered:** C1968 (Tier 2)

---

## Question

C1967 supplement (Phase 652) found bodies > headers in e_depth across block-pure paragraphs. The architectural reading: bodies carry thermal execution; headers carry compound specification. The symmetric prediction: **headers > bodies in HT density** (since HT = compound MIDDLE per HTSC).

Phase 655 tests this symmetric prediction across the three primary fire-side channel classes (qo, ch, sh), with token-pool control to address the C1789 caveat (header-exclusive vocabulary may inflate apparent gaps).

---

## Method

### Test 1 (s1): Header-body HT gap, all tokens

For each block-pure Currier B paragraph (n=222 from Phase 652):
- Split tokens into header (first line) and body (remaining lines)
- Compute HT rate (compound MIDDLE per HTSC) for each
- Stratify by dominant channel class (qo, ch, sh, ok, ot, ol, or)
- Paired t-test on header-body gap per class

### Test 2 (s2): Token-pool control

Restrict to tokens that appear in BOTH header and body positions across the qualifying paragraph set. Recompute HT-rate gap among shared tokens only. If gap survives, the architectural deployment effect is genuine. If gap collapses, the original gap was driven by header-exclusive vocabulary (per C1789 ~86% header-token exclusivity).

---

## Findings

### Test 1 result (all tokens)

| Class | n | Header HT | Body HT | Gap (H-B) | p |
|---|---|---|---|---|---|
| qo | 102 | 0.320 | 0.282 | +0.038 | 0.032 ✓ |
| ch | 82 | 0.359 | 0.272 | **+0.088** | **<0.0001** ✓✓✓ |
| sh | 25 | 0.319 | 0.269 | +0.050 | 0.35 (NS) |

Direction unanimous across all three classes. ch reaches strong significance.

### Test 2 result (shared-token control)

| Class | n | Header HT (shared) | Body HT (shared) | Gap (shared) | p |
|---|---|---|---|---|---|
| qo | 102 | 0.242 | 0.230 | **+0.012** (collapsed) | 0.59 (NS) |
| ch | 82 | 0.266 | 0.200 | **+0.066** (survives) | **0.007** ✓ |
| sh | 25 | 0.167 | 0.208 | **-0.041 (reversed)** | 0.29 (NS) |

**Critical:** the qo and sh gaps from Test 1 were token-pool artifacts. Only ch survives the shared-token control with significant deployment effect. sh actually reverses direction.

### Architectural interpretation

After token-pool control, the channel-class header-body specialization pattern is:

| Class | HT (header-spec) gap | e_depth (body-thermal) gap |
|---|---|---|
| qo | none (artifact-only) | small (-0.034) |
| ch | **+0.066 (real)** | medium (-0.062) |
| sh | none / reversed | LARGE (-0.123) |

Each channel class has a distinct architectural pattern:
- **ch (active testing):** front-loads compound specification at paragraph header. Operator declares what to test for, then tests in body.
- **sh (passive monitoring):** thermal context concentrates in body. Operator just observes ambient state.
- **qo (heat-driving):** consistent throughout — neither dimension shows strong header-body division. Driving heat is sustained.

The architecture is NOT "headers carry spec, bodies carry execution" universally. It's **channel-class-specific**: different operational modes concentrate different content at different positions.

---

## Constraint registered

### C1968 (Tier 2): ch-class paragraph-header compound-specification concentration

[Full text in `context/CLAIMS/C1968_ch_class_header_compound_specification.md`]

**Statement:** Block-pure Currier B paragraphs with ch-dominant channel show concentration of compound MIDDLE tokens (HT) at the paragraph header relative to body. Shared-token-controlled gap +0.066 (p=0.007, n=82). Other channel classes (qo, sh) do not show genuine concentration after token-pool control. Refines C929 (ch=active test) with the operational claim: active-testing operations require explicit compound-specification at the paragraph header before test execution in the body. Pairs with C1967 supplement (sh-class largest e_depth gap) to establish channel-class-distinctive header-body specialization patterns.

---

## Methodology lesson

The C1789 token-pool caveat was real and consequential. Without the control:
- qo apparent gap (+0.038, p=0.032) → would have been registered as confirming the symmetric prediction
- ch apparent gap (+0.088, p<0.0001) → registered as Tier 2
- sh apparent gap (+0.050) → directional support
- Total: "headers > bodies in HT across all three classes" — broadly registered Tier 2

With the control:
- qo gap collapses (artifact) → not registerable
- ch gap survives at lower magnitude (+0.066) but stronger interpretation (genuine architectural effect, not vocabulary artifact)
- sh gap reverses (artifact) → opposite direction from prediction

The control narrowed the claim from "universal across fire-side channels" to "ch-class-specific architectural deployment." The narrower finding is the truer one.

**Pre-registration was implicit but critical:** the token-pool control was specified by expert-advisor BEFORE running it, based on C1789. The sequence (test → flag caveat → run control → revise claim) was the right discipline.

---

## What this means in conjunction with prior findings

- **C1966** (HT density tracks compound specification load per folio): general claim, holds at folio resolution
- **C1967 + supplement** (e_depth gradient + body > header): channel-class differs in thermal-commitment distribution
- **C1968** (this phase): channel-class differs in compound-spec deployment, with ch uniquely concentrating spec at header

Together: **the architecture's header-body division isn't universal — it's channel-class-specific and dimension-specific.** ch concentrates compound-spec; sh concentrates thermal-commitment; qo is consistent throughout.

---

## Files

- `scripts/`
  - `s1_header_body_ht_gap.py` — initial all-tokens test
  - `s2_token_pool_control.py` — shared-token control (decisive)
- `results/`
  - `header_body_ht_density.json`
  - `header_body_ht_token_pool_control.json`
