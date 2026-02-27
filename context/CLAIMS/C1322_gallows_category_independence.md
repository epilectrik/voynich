# C1322: Gallows-Category Independence

**Tier:** 2
**Scope:** B
**Phase:** BLOCK_GALLOWS_ORDERING (463)
**Date:** 2026-02-26

## Finding

The paragraph-initial gallows letter (k/t/p/f) does NOT predict the paragraph body's operational category profile or kernel distribution. Gallows encode positional phase (C1321), not operational type.

**Category profiles (T1):**
- 0/8 categories show KW p<0.01 across gallows types
- Closest: CONTAINMENT p=0.015, MONITORING p=0.024, MARKING p=0.042
- Category fractions are nearly identical across gallows types (e.g., THERMAL: f=0.209, k=0.212, p=0.233, t=0.226 — a 0.024 range)
- No categories confirmed in >=2 sections

**Kernel profiles (T2):**
- 1/3 kernel fractions shows KW p<0.01: kernel-h (p=0.006) with t lowest (0.138) and k highest (0.197)
- But this holds in only 1 section (B), failing the >=2 section requirement
- kernel-k (p=0.162) and kernel-e (p=0.877) show no significant gallows dependence

Combined with C868 (gallows-QO/CHSH independence, 0.3% variance explained), this establishes gallows as a positional/structural axis orthogonal to operational content.

## Interpretation

Gallows are "phase markers" not "job titles." A k-initial paragraph does the same kinds of operations as a t-initial paragraph — the gallows letter tells you WHERE in the block it appears (C1321), not WHAT it does. The operational specialization comes from PREFIX choice (C1318), not gallows choice.

## Negative Control

Section-stratified analysis: no category or kernel fraction reaches significance in >=2 sections independently. The global-level marginal effects (CONTAINMENT, kernel-h) do not replicate across sections, confirming they are noise or section-specific artifacts.

## Extends

- C868 (gallows-QO/CHSH independence) — extends independence from lane choice to full operational category profile
- C1318 (block PREFIX complementarity) — operational specialization comes from PREFIX, confirming gallows and PREFIX encode orthogonal information
- C1321 (gallows within-block ordering) — gallows encode position (when), this constraint confirms they do not encode type (what)

## Falsifiability

Would be falsified if any category shows KW p<0.001 across gallows types AND replicates in >=3 sections independently, establishing a genuine gallows-category association.

## Evidence Files

- `phases/BLOCK_GALLOWS_ORDERING/results/block_gallows_ordering.json` (T1, T2)
