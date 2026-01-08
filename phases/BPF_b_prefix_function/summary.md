# Phase BPF: B-Prefix Functional Grammar

## Question
How do prefixes function in Currier B? Do they have structural roles beyond compositional morphology?

## Methodology
5 tests on 23,195 Currier B tokens (84.8% have identifiable prefix):

1. **Positional Preferences** - Line-initial/final enrichment
2. **Kernel Correlation** - k/h/e character presence
3. **LINK Proximity** - Within 2 tokens of LINK
4. **Section Association** - Chi-square across B sections
5. **Type Classification** - Aggregate by prefix class

## Key Findings

### TEST 1: POSITIONAL GRAMMAR (SIGNAL)
Prefixes have strong positional specialization (range 0.07x - 7.0x):

| Role | Prefixes | Enrichment |
|------|----------|------------|
| LINE-INITIAL | so, ych, pch, sa, yk, yt | 4-7x |
| LINE-FINAL | lo, al, da, ol, lch | 1.7-3.7x |
| MID-LINE | ch, ke, lk, op | <0.2x initial |

### TEST 2: KERNEL DICHOTOMY (SIGNAL)
Sharp split between kernel-heavy and kernel-light prefixes:

| Type | Kernel Contact | Examples |
|------|----------------|----------|
| KERNEL-HEAVY | 100% | ch, sh, ok, lk, lch, yk, ke |
| KERNEL-LIGHT | <5% | da (4.9%), sa (3.4%) |

This indicates two distinct operational modes within B grammar.

### TEST 3: LINK AFFINITY (SIGNAL)
Prefixes split by LINK proximity:

| Type | Enrichment | Examples |
|------|------------|----------|
| LINK-ATTRACTED | 1.6-2.5x | al, ol, da |
| LINK-AVOIDING | 0.6-0.7x | qo, lch, op |

Prefixes that avoid kernel also attract LINK (da, al) - correlation with waiting phases.

### TEST 4: SECTION PREFERENCES (SIGNAL)
Chi-square = 2368.9, p = 0.0 (highly significant)

Notable specializations:
- `lk`: 81% Section S
- `yk`: 36% Section H (highest diversity)
- `ol`: 49% Section B

### TEST 5: PREFIX TYPE SIGNATURES
| Type | Init% | Final% | Kernel% | LINK-adj% |
|------|-------|--------|---------|-----------|
| EXT_CLUSTER | 53.6% | 4.5% | 99.9% | 9.5% |
| HT_PREFIX | 28.0% | 11.0% | 58.5% | 19.0% |
| L_COMPOUND | 5.3% | 16.0% | 83.3% | 10.9% |
| A_PREFIX | 6.2% | 9.6% | 78.7% | 14.3% |
| KERNEL | 6.9% | 5.6% | 100% | 34.7% |

EXT_CLUSTER = line openers with kernel contact
L_COMPOUND = line closers
HT_PREFIX = early-line orientation markers

## Interpretation

Prefixes in Currier B are not neutral - they carry:
1. **Positional information** (where in line)
2. **Operational mode** (kernel-contact vs kernel-free)
3. **Waiting/intervention phase** (LINK affinity)
4. **Section constraints** (which program families)

This is consistent with prefixes encoding **instruction type** within the 49-class grammar:
- KERNEL-HEAVY prefixes = active intervention instructions
- KERNEL-LIGHT prefixes = monitoring/waiting instructions
- LINE-INITIAL prefixes = stage entry points
- LINE-FINAL prefixes = stage completion markers

## Constraints Added

| # | Constraint |
|---|------------|
| 371 | Prefixes have POSITIONAL GRAMMAR (0.07x-7.0x enrichment range) |
| 372 | Prefixes split by KERNEL CONTACT (100% vs <5% dichotomy) |
| 373 | Prefixes have LINK AFFINITY patterns (attracted vs avoiding) |
| 374 | Prefixes have SECTION PREFERENCES (chi2=2369, p=0) |

## Status
**CLOSED** - PREFIX FUNCTION CHARACTERIZED

Phase BPF establishes that B-prefixes are functional markers within the control grammar, not mere compositional building blocks.
