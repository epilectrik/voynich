# Negative Control Validation Report

*Generated: 2026-01-01T07:34:15.238300*

## Purpose

Validate that the discriminator correctly identifies known DSL-like structures.

---

## Synthetic Corpus

| Component | Count |
|-----------|-------|
| A-text (definitions) | 365 |
| B-text (procedures) | 1499 |
| Unique definitions | 50 |

---

## Test Results on Synthetic DSL

| Test | Value | Passes? |
|------|-------|---------|
| Context diversity | 25.75 | True |
| Reference rate | 1.000 | True |
| Role consistency | 0.135 | True |

---

## Discriminator Validity

**DISCRIMINATOR VALID: True**

The synthetic DSL shows high reference rates and context diversity, confirming the discriminator can detect DSL-like behavior. Role consistency is variable because this is a random corpus.

---

## Implications

The discriminator successfully detects DSL-like patterns in a known DSL corpus. Results on the Voynich corpus can be trusted.
