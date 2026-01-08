# Phase BSF: B-Suffix Functional Grammar

## Question
How do suffixes function in Currier B? Do they mirror prefix patterns or show independent structure?

## Methodology
5 tests on 23,195 Currier B tokens (95.7% have identifiable suffix):

1. **Positional Preferences** - Line-initial/final enrichment
2. **Kernel Correlation** - k/h/e presence in token base
3. **LINK Proximity** - Within 2 tokens of LINK
4. **Section Association** - Chi-square across B sections
5. **Prefix-Suffix Interaction** - Independence test

## Key Findings

### TEST 1: POSITIONAL GRAMMAR (SIGNAL)
Suffixes show extreme positional specialization:

| Role | Suffixes | Enrichment |
|------|----------|------------|
| LINE-FINAL (extreme) | -am (7.7x), -om (8.7x), -oly (4.6x) | 80-90% line-final |
| LINE-FINAL (moderate) | -y (2.3x), -dy (1.7x), -an (2.4x) | 20-25% line-final |
| LINE-INITIAL | -or (1.8x), -shy (1.7x), -ol (1.6x) | 17-20% line-initial |

**Note:** -am and -om are essentially line-termination markers (80-90% line-final).

### TEST 2: KERNEL DICHOTOMY (SIGNAL)
Mirrors prefix pattern exactly:

| Type | Kernel% | Suffixes |
|------|---------|----------|
| KERNEL-HEAVY | 84-95% | -edy, -ey, -dy, -d, -eey, -ody |
| KERNEL-LIGHT | 6-17% | -in (5.8%), -l (12.4%), -r (16.7%) |

### TEST 3: LINK AFFINITY (SIGNAL)
**Critical finding:** KERNEL-LIGHT suffixes are LINK-attracted

| Type | Suffixes | LINK Enrichment |
|------|----------|-----------------|
| LINK-ATTRACTED | -l (2.78x), -in (2.30x), -r (2.16x) | Waiting markers |
| LINK-AVOIDING | -edy (0.59x), -y (0.68x), -shy (0.52x) | Intervention markers |

This confirms: **kernel-light = waiting phase**

### TEST 4: SECTION PREFERENCES (SIGNAL)
Chi-square = 2233.0, p = 0.0

Notable specializations:
- -ody: 52% Section S, only 1% Section B
- -eey: 63% Section S
- -ain: 54% Section S

### TEST 5: PREFIX-SUFFIX DEPENDENCY (SIGNAL)
Chi-square = 7052.5, p = 0.0 — highly constrained

| Combination | Frequency | Interpretation |
|-------------|-----------|----------------|
| da + -aiin | 30% | High affinity |
| da + -edy | 1% | Strong avoidance |
| sh + -edy | 28% | High affinity |

Prefixes select compatible suffixes — not free combination.

## Interpretation

Suffixes in Currier B encode:
1. **Line position** (-am/-om = termination markers)
2. **Operational mode** (kernel-heavy vs kernel-light)
3. **Phase identity** (LINK-attracted = waiting; LINK-avoiding = intervention)
4. **Section constraints** (chi2=2233)
5. **Prefix compatibility** (chi2=7053)

The kernel-light suffix pattern (-r, -l, -in) is particularly significant:
- These suffixes have LOW kernel contact (6-17%)
- These suffixes are HIGH LINK-proximity (2.2-2.8x)
- This confirms waiting-phase vs intervention-phase grammar split

Combined with prefix findings:
- WAITING tokens: kernel-light prefix (da, sa) + kernel-light suffix (-r, -l, -in) + LINK-adjacent
- INTERVENTION tokens: kernel-heavy prefix (ch, sh, ok) + kernel-heavy suffix (-edy, -ey, -dy) + LINK-distant

## Constraints Added

| # | Constraint |
|---|------------|
| 375 | Suffixes have POSITIONAL GRAMMAR (-am/-om 80-90% line-final) |
| 376 | Suffixes split by KERNEL CONTACT (mirrors prefix dichotomy) |
| 377 | KERNEL-LIGHT suffixes are LINK-ATTRACTED (waiting-phase markers) |
| 378 | Prefix-suffix combinations are CONSTRAINED (chi2=7053) |

## Status
**CLOSED** - SUFFIX FUNCTION CHARACTERIZED

Phase BSF confirms suffix functional structure mirrors and complements prefix structure, establishing a coherent waiting/intervention grammar axis.
