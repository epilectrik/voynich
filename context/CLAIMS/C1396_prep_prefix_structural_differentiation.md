# C1396: Prep PREFIX Structural Differentiation

**Tier:** 2 (ESTABLISHED)
**Scope:** B, PREFIX, prep, position, REGIME, suffix, atom
**Phase:** PREP_PREFIX_PROFILING (Phase 508)
**Extends:** C1221 (prep PREFIX similarity is base-driven), C1394 (instruction encoding architecture)
**Challenges:** F-BRU-012 collapse to generic "process" — specific verb glosses are challenged but functional differentiation is real
**Relates to:** C931 (PREFIX positional phase mapping), C1218-C1220 (PREFIX internal grammar)

---

## Statement

Prep PREFIXes (pch, tch, dch, lch, te) share identical MIDDLE category content (C1221 confirmed: cosine 0.963, shuffle p=0.998), but are **structurally differentiated on 7 of 8 non-content dimensions**. The modifier characters (p, t, d, l) are not interchangeable — they select different line positions, paragraph positions, suffix attachment rates, REGIME concentrations, section distributions, and sequential contexts for the shared h-base processing.

### Token Counts

| PREFIX | N |
|--------|---|
| pch | 245 |
| tch | 172 |
| dch | 104 |
| lch | 315 |
| te | 289 |
| ch (bare) | 3,492 |

---

## Key Findings

### T1: Positional Differentiation — DIFFERENTIATED

9/10 prep pairs significant at p<0.05 for line position (KS tests).

| PREFIX | Mean pos | Line-initial % | Line-final % |
|--------|----------|---------------|-------------|
| dch | 0.168 | 71.2% | 2.9% |
| tch | 0.283 | 52.9% | 2.3% |
| pch | 0.299 | 48.2% | 2.4% |
| te | 0.441 | 19.7% | 5.9% |
| lch | 0.530 | 6.7% | 16.8% |
| ch | 0.515 | 4.8% | 8.9% |

dch is extremely line-initial (71.2%). lch is line-interior/final. pch/tch are initial-biased.

### T2: Sequential Context — DIFFERENTIATED

Predecessor class distributions differ (chi2=212.3, p=0.007, V=0.308). pch/dch preceded by different classes than lch/te.

### T3: Suffix Pattern Divergence — DIFFERENTIATED

Bare suffix rates diverge dramatically (chi2=183.4, p<0.001, V=0.202):

| PREFIX | Bare rate |
|--------|----------|
| pch | 50.6% |
| dch | 65.4% |
| te | 71.3% |
| tch | 73.3% |
| lch | 81.3% |
| ch | 47.0% |

pch takes suffixes at nearly the rate of bare ch (50.6% vs 47.0%), meaning it carries more parametric specification. lch is 81.3% bare — typically a standalone instruction.

### T4: REGIME Distribution — DIFFERENTIATED

chi2=138.7, p<0.001, V=0.203.

| PREFIX | R1 | R2 | R3 | R4 |
|--------|-----|-----|-----|-----|
| pch | 35.5% | 7.3% | 40.0% | 17.1% |
| tch | 29.1% | 14.0% | 43.6% | 13.4% |
| dch | 41.3% | 6.7% | 39.4% | 12.5% |
| lch | 70.5% | 2.9% | 23.8% | 2.9% |
| te | 47.8% | 8.0% | 24.6% | 19.7% |

lch is 70.5% REGIME_1 (sustained gentle-heating). pch/tch concentrate in REGIME_3 (40-44%, batch-cycling).

### T5: Specific MIDDLE Vocabulary — PARTIAL

Mean Jaccard 0.306 among prep pairs. Each has 8-28 unique MIDDLEs. Top MIDDLEs heavily overlap (edy, dy, ey dominant). Content similarity confirmed per C1221, but vocabulary sets only ~31% shared — vocabulary divergence exists at the specific-MIDDLE level despite category-axis convergence.

### T6: Paragraph Position Profile — DIFFERENTIATED

8/10 pairs significant (KS tests).

| PREFIX | Mean par-pos | Par-initial % |
|--------|-------------|--------------|
| pch | 0.134 | 41.2% |
| tch | 0.366 | 22.7% |
| te | 0.427 | 4.2% |
| dch | 0.549 | 3.8% |
| lch | 0.538 | 0.0% |
| ch | 0.535 | 0.1% |

pch is overwhelmingly paragraph-initial (41.2% — vs bare ch 0.1%). lch never appears paragraph-initial.

### T7: Section Distribution — DIFFERENTIATED

chi2=127.3, p<0.001, V=0.168. lch is 40.0% Section B (balneological). tch has highest Section C at 14.0%.

### T8: Bare ch Comparison — DIFFERENTIATED

27/35 dimension-prefix pairs significant. pch/tch diverge from bare ch on ALL 7 dimensions. dch on 2 (position + predecessor). lch on 5. te on 6.

---

## Three Positional Tiers

| Tier | PREFIXes | Line Position | Paragraph Position | Interpretation |
|------|----------|--------------|-------------------|----------------|
| OPENER | pch, dch, tch | Line-initial (mean 0.17-0.30) | pch: paragraph-early (0.134); tch: early-mid (0.366); dch: body (0.549) | Open sequences |
| BODY | te | Mid-line (mean 0.44) | Mid-paragraph (mean 0.43) | Body processing |
| SUSTAINER | lch | Mid-late line (mean 0.53) | Late paragraph (mean 0.54), 0% initial | Interior operations |

---

## Atom Gloss Alignment

The differentiation pattern aligns with C1394 modifier atom functions:

| Modifier | Atom Gloss | Observed Behavior | Alignment |
|----------|-----------|-------------------|-----------|
| **p** (pch) | pause/marking | Paragraph-opener (41.2%), suffix-heavy (50.6% bare), REGIME_3 | STRONG — marks batch cycle starts |
| **d** (dch) | mark/operation | Most line-initial (71.2%), smallest sample | STRONG — marks operation beginnings |
| **t** (tch) | transfer/flow | Initial-biased (52.9%), REGIME_3 (43.6%), highest Section C | MODERATE — initiates flow/transfer |
| **l** (lch) | state/staging | Interior (0% par-initial), REGIME_1 (70.5%), bare (81.3%), Section B | STRONG — maintains state in place |

---

## Revision of C1221 Status

C1221 correctly identified that prep PREFIXes share MIDDLE category-axis content (cosine 0.963). This finding HOLDS. However, C1221's conclusion that the specific verb glosses should collapse to a generic "process" was **premature on non-content dimensions**. The modifiers differentiate on 7 non-content dimensions:

1. Line position (strongly)
2. Paragraph position (strongly)
3. Suffix attachment rate (strongly)
4. REGIME concentration (strongly)
5. Section distribution (strongly)
6. Sequential context (moderately)
7. MIDDLE vocabulary overlap (partially — Jaccard 0.31)

The Brunschwig-derived specific verbs (CHOP, POUND, STRIP, GATHER) remain challenged as *action type* labels, but the modifiers are NOT interchangeable. They specify HOW and WHEN the shared h-base processing occurs, consistent with C1394's atom-level functional inventory.

### Revised Glosses

| PREFIX | Old Gloss | Revised Gloss | Basis |
|--------|----------|---------------|-------|
| pch | process (was: CHOP) | stage-test | p=pause/marking + ch=test; 41.2% par-initial, suffix-heavy |
| tch | process (was: POUND) | transfer-test | t=transfer + ch=test; initial-biased, REGIME_3, Section C |
| dch | process | mark-test | d=mark + ch=test; 71.2% line-initial |
| lch | process (was: STRIP) | hold-test | l=state + ch=test; 81.3% bare, REGIME_1, 0% par-initial |
| te | process (was: GATHER) | transfer-cool | t=transfer + e=cool; body position, distributed |

---

## Falsification Criteria

1. If suffix patterns converge to identical bare rates (>70% for all prep PREFIXes), suffix differentiation fails
2. If positional profiles converge under section control, positional differentiation is section-driven
3. If REGIME distribution flattens under section control, REGIME effect is section-driven

---

## Method

- 23,243 Currier B tokens, H-track, labels excluded
- 8 tests across position, context, suffix, REGIME, vocabulary, paragraph, section, and bare ch comparison
- KS tests for continuous distributions, chi-squared + Cramer's V for categorical
- Random seed 42

**Script:** `phases/PREP_PREFIX_PROFILING/scripts/prep_prefix_profiling.py`
**Results:** `phases/PREP_PREFIX_PROFILING/results/prep_prefix_profiling.json`
