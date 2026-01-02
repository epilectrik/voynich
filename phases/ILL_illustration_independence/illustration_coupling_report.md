# Illustration Coupling Analysis Report

*Generated: 2026-01-01T08:24:14*

---

## Executive Summary

| Test | Question | Result | Verdict |
|------|----------|--------|---------|
| **Test 1** | Does text-illustration pairing matter? | p = 1.00 (no effect) | **PASS** |
| **Test 2** | Are IF and NIF distinguishable? | 94.0% classifier accuracy | **DISTRIBUTION_SHIFT** |
| **Metrics** | Which execution metrics differ? | 1/5 significant (kernel_contact) | **WEAK EFFECT** |

**OVERALL VERDICT: H1_SUPPORTED**

> Illustrations **correlate** with execution behavior but do **not constrain or gate** it.

**Interpretation:** Illustrated folios (IF) and non-illustrated folios (NIF) have different text characteristics (detectable by classifier), but swapping text between them does not affect execution. The illustration itself has no operational role.

---

## Folio Classification

| Category | Count | Definition |
|----------|-------|------------|
| **IF (Illustrated Folios)** | 40 | Folios with dominant central illustration (herbal A/B, cosmological) |
| **NIF (Non-Illustrated Folios)** | 43 | Folios that are primarily text (recipe, pharmaceutical) |

Classification based on standard paleographic structure:
- **IF**: f1-f66 (herbal A), f67-f73 (cosmological), f85-f86 (diagrams), f87-f102 (herbal B)
- **NIF**: f75-f84 (pharmaceutical), f103-f116 (recipe text)

---

## Test 1: Swap Invariance

**Question:** Does the pairing between illustration and text matter for execution?

**Method:** Compare execution scores when text is:
1. Paired with its original illustration
2. Swapped with text from another illustrated folio
3. Swapped with text from a non-illustrated folio

### Results

| Pairing | Mean Convergence |
|---------|------------------|
| Original | 0.0742 |
| IF-IF swap | 0.0769 |
| IF-NIF swap | 0.0730 |
| NIF-NIF swap | 0.0716 |

| Comparison | p-value |
|------------|---------|
| Original vs IF-IF swap | 1.000 |
| IF original vs NIF swap | 0.613 |

**VERDICT: SWAP_INVARIANT**

**Interpretation:** Swapping text between folios produces statistically indistinguishable execution behavior. The illustration-text pairing has **no operational significance**. Execution is determined by text alone.

---

## Test 2: Distribution Shift

**Question:** Is P(X|IF) different from P(X|NIF)?

**Method:**
1. Compute 10-dimensional feature vectors per folio
2. Apply Maximum Mean Discrepancy (MMD) with permutation test
3. Train cross-validated logistic classifier

### Results

| Metric | Value |
|--------|-------|
| MMD (RBF kernel) | 0.147 |
| Energy distance | 1.90 |
| MMD permutation p-value | **0.000** |
| Classifier accuracy | **94.0% +/- 3.7%** |
| Chance level | 50.0% |

**VERDICT: DISTRIBUTION_SHIFT_DETECTED**

**Interpretation:** A simple classifier can distinguish IF from NIF with 94% accuracy. This indicates that illustrated and non-illustrated folios have systematically different text characteristics. However, this reflects text differences (likely Currier A vs B), not illustration-imposed constraints.

### Features Used

1. legality
2. convergence
3. stability_dwell
4. kernel_contact
5. link_density
6. avg_run_length
7. energy_density
8. token_count
9. hazard_rate
10. type_token_ratio

---

## Per-Metric Comparison

| Metric | IF Mean | NIF Mean | Cohen's d | p-value | Significant? |
|--------|---------|----------|-----------|---------|--------------|
| legality | 1.0000 | 1.0000 | 0.00 | 1.000 | No |
| convergence | 0.0769 | 0.0716 | 0.21 | 0.436 | No |
| stability | 1.1356 | 1.0748 | 0.38 | 0.402 | No |
| **kernel_contact** | **0.6512** | **0.6993** | **-0.68** | **0.004** | **Yes** |
| hazard_rate | 0.0000 | 0.0000 | 0.00 | 1.000 | No |

### Key Finding: Kernel Contact

Non-illustrated folios (NIF) have **higher kernel contact** than illustrated folios (IF):
- NIF: 69.9% of tokens are kernel-adjacent
- IF: 65.1% of tokens are kernel-adjacent
- Effect size: Cohen's d = -0.68 (medium-large)

This likely reflects:
- NIF = recipe pages (Currier B) = more procedural, more kernel operations
- IF = herbal pages (Currier A) = more definitional, fewer kernel operations

---

## Hypothesis Evaluation

| Hypothesis | Signals | Status |
|------------|---------|--------|
| **H0** (No coupling) | 1 | Test 1 supports |
| **H1** (Weak coupling) | 2 | Test 2 and metrics support |
| **H2** (Strong coupling) | 0 | No evidence |

### Signal Breakdown

1. **H0 signal:** Swap invariance (p = 1.0) - text execution is independent of illustration pairing
2. **H1 signal:** Distribution shift (94% classifier) - IF and NIF have different profiles
3. **H1 signal:** 1/5 metrics significant - kernel_contact differs

---

## Conclusions

### 1. Illustrations Do Not Constrain Execution

The swap invariance test definitively shows that **illustration-text pairing has no effect on execution behavior**. You can swap text between illustrated and non-illustrated folios with no measurable impact on:
- Grammar legality
- STATE-C convergence
- Hazard encounters
- Stability dwell time

### 2. IF and NIF Are Textually Distinct

The 94% classifier accuracy indicates a real difference between illustrated and non-illustrated folio text. This is not surprising - it likely reflects the well-known Currier A/B distinction:
- **IF (herbal)**: Predominantly Currier A text (definitional)
- **NIF (recipe)**: Predominantly Currier B text (procedural)

### 3. The Difference Is in the Text, Not the Illustration

The distribution shift is a **text characteristic**, not an illustration constraint. If illustrations constrained text, we would expect:
- Swap dependency (not observed)
- Strong coupling signals (not observed)

Instead, we observe:
- Swap invariance (observed)
- Weak correlation only (observed)

---

## Interpretive Firewall Statement

> All findings describe structural correlations and execution metrics only.
> No semantic interpretation of illustration content has been applied.
> Domain-specific language has been strictly avoided per pre-registration.
>
> If interpretation pressure arises: "Illustration content cannot be characterized without violating semantic constraints."

---

## Kill Condition Evaluation

| Kill Condition | Test | Triggered? |
|----------------|------|------------|
| Swap invariance (H0 vs H2) | E(T,I) = E(T,I') = E(T,null) | **YES - H0 supported** |
| Distribution shift (H0 vs H1) | P(X\|IF) = P(X\|NIF) | **NO - shift detected** |

**Final Status:** Neither full H0 confirmation nor H2 support. The result is **H1 (weak coupling)** - a correlation exists but is non-causal.

---

## Implication for Decipherment

This result **does not falsify** the operational grammar interpretation. The frozen conclusion remains valid:

> The Voynich Manuscript is a PURE_OPERATIONAL system. Execution behavior is determined by text alone. Illustrations are **decorative or organizational** but not **operational**.

The "process the illustrated thing" hypothesis is **structurally falsified** in its strong form. Illustrations do not:
- Gate execution
- Constrain grammar
- Determine execution outcomes

They may serve:
- Visual organization (like section headers)
- Category markers (like chapter illustrations)
- Mnemonic aids (external to operational content)

---

*Report generated by Illustration Coupling Analysis Suite*
