# Phase 521: The m-Terminal Anomaly

**Date:** 2026-03-05
**Status:** COMPLETE
**Phase type:** Characterization
**Extends:** C1427 (line-final transition profile), C1393-1394 (instruction encoding), C1237 (-am paragraph termination)
**Script:** `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py`
**Results:** `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json`

---

## Research Question

C1427 found that the MIDDLE terminal atom `m` shows a 196x enrichment from line-initial to line-final position -- the largest positional effect ever observed. What is m doing? Is it a dedicated closure signal? How does it interact with the instruction encoding grammar and line-level architecture?

## Key Findings Summary

| Finding | Result | Constraint |
|---------|--------|-----------|
| m-terminal is an extreme low-diversity closure terminal | 10 types, 289 tokens, 95.9% bare | C1434 |
| m is line-body-exclusive, anti-paragraph, anti-header | 10.5% body-line-final, 0% header, 3.3% par-final | C1435 |
| m-terminal is near-pure TRANSITION (87.9%) | Most category-concentrated terminal atom | C1436 |
| m is completely hazard-excluded | 0% FLOW, 0% CONTAINMENT, 0% hazard categories | C1437 |
| m-terminal categorically suppresses suffixation | 4.2% suffix rate vs 48.3% overall | C1438 |
| -am suffix and m-terminal MIDDLE are distinct systems | 1 token overlap; -am is multi-category, m-terminal is near-pure TRANSITION | C1439 |

---

## T1: m-Terminal Inventory

**289 tokens, 10 unique MIDDLE types, 1.25% of all B tokens.**

| MIDDLE | Count | Category | HEAD |
|--------|-------|----------|------|
| am | 174 | TRANSITION | a |
| m | 76 | TRANSITION | (none) |
| om | 25 | OPERATION | o |
| im | 8 | STAGING | (none) |
| faim | 1 | TRANSITION | (none) |
| lm | 1 | STAGING | (none) |
| kam | 1 | TRANSITION | k |
| eam | 1 | TRANSITION | e |
| opom | 1 | OPERATION | o |
| fam | 1 | TRANSITION | (none) |

**Key observations:**
- **Extreme concentration:** `am` alone accounts for 60.2% of all m-terminal tokens, and `am` + `m` account for 86.5%.
- **HEAD distribution:** a-HEAD dominates (60.2%), followed by headless (30.1%), o-HEAD (9.0%).
- **Vocabulary diversity is the lowest of any terminal:** Only 10 types for 289 tokens, vs y: 33 types for 4,780 tokens, l: 48 types for 2,568 tokens.
- **MOD stack is nearly empty:** Only 3 tokens have a modifier between HEAD and m (faim, opom, fam). m operates as a near-bare terminal.
- The `am` MIDDLE reads compositionally as a(yield) + m(close) = "yield-close" or "batch-close" under the Tier 3 atom glosses.

---

## T2: Positional Gradient

The m-terminal rate follows a **steep exponential ramp**, not a step function:

| Position | m-rate | Notes |
|----------|--------|-------|
| Pos 1 | 0.04% | Near-zero |
| Q0 (0-20%) | 0.16% | Near-zero |
| Q1 (20-40%) | 0.15% | Near-zero |
| Q2 (40-60%) | 0.39% | Beginning to rise |
| Q3 (60-80%) | 0.64% | Gradual increase |
| Q4 (80-100%) | 6.03% | Steep jump |
| FINAL token | 8.80% | Peak |

The pattern is a smooth exponential ramp, not a binary switch. m begins appearing around position 7 in typical 10-token lines and accelerates sharply at the penultimate and final positions.

**Concentration indices** (final rate / overall rate):

| Terminal | Concentration Index |
|----------|-------------------|
| **m** | **7.0x** |
| l | 1.1x |
| y | 1.0x |
| r | 1.0x |
| t | 0.9x |
| k | 0.7x |
| n | 0.7x |
| h | 0.7x |

m is uniquely concentrated at line-final position. No other terminal comes close. The next-highest (l) is essentially flat at 1.1x.

---

## T3: Scope -- Line-Final, Not Paragraph-Final

This is a critical finding: **m is a LINE-body closure signal, not a paragraph closure signal.**

| Context | m-rate | N |
|---------|--------|---|
| Non-final position | 0.31% | 20,542 |
| **Body-line-final** (not par-final) | **10.45%** | 1,971 |
| Non-header line-final | 9.12% | 2,052 |
| **Header line-final** | **0.00%** | 502 |
| **Paragraph-final** | **3.26%** | 583 |
| Folio-final | 3.61% | 83 |

**Critical contrasts:**
1. **m is ANTI-HEADER:** Zero m-terminal tokens appear at header line-final position. m is categorically excluded from paragraph opening lines.
2. **m is ANTI-PARAGRAPH-FINAL:** m-rate at paragraph-final (3.26%) is significantly LOWER than at body-line-final (10.45%). Fisher exact test p < 0.000001. This is the opposite of what C1237 found for the -am suffix (which IS paragraph-final concentrated at 5.19x).
3. **m is a BODY-LINE signal:** It marks the end of interior body lines within paragraphs, not the end of paragraphs themselves.

This directly contradicts the naive hypothesis that m is "the paragraph terminator." The -am SUFFIX (C1237) is the paragraph terminator; the m-terminal MIDDLE is the body-line closer.

---

## T4: PREFIX Distribution

m-terminal tokens show a distinctive PREFIX profile:

| PREFIX | m-terminal % | Overall % | Enrichment |
|--------|-------------|-----------|------------|
| ar | 3.8% | 0.6% | 6.46x |
| ta | 5.5% | 1.0% | 5.40x |
| al | 3.8% | 0.7% | 5.08x |
| or | 3.5% | 0.7% | 4.62x |
| da | 17.3% | 4.7% | 3.69x |
| ka | 2.4% | 1.0% | 2.35x |
| ot | 13.5% | 6.3% | 2.15x |
| BARE | 26.6% | 16.7% | 1.59x |
| ok | 8.0% | 6.4% | 1.25x |
| **ch** | **2.4%** | **15.2%** | **0.16x** |
| **sh** | **1.7%** | **10.2%** | **0.17x** |
| **qo** | **0.4%** | **16.5%** | **0.02x** |

**Key patterns:**
- **ch/sh massively depleted** (0.16-0.17x): The two monitoring/testing PREFIXes almost never combine with m-terminal. Only 12 tokens total across ch+sh.
- **qo nearly absent** (0.02x): Only 1 qo+m-terminal token in the entire corpus. The thermal channel avoids m.
- **LATE PREFIXes enriched:** ar (6.46x), al (5.08x), or (4.62x) -- exactly the C539 LATE prefix class (line-final output markers).
- **da strongly enriched** (3.69x): Infrastructure anchor prefix combined with m-terminal.
- Chi-squared test: chi2=281.6, p=8.0e-52, V=0.116 -- highly significant PREFIX selectivity.

This means m-terminal lives in the LATE/BARE/ot/ok prefix space -- the output, routing, and containment channels. It avoids the thermal (qo) and monitoring (ch/sh) channels entirely.

---

## T5: Suffix Suppression

**m-terminal categorically suppresses suffix attachment:**

| Measure | m-terminal | Overall |
|---------|-----------|---------|
| Suffix rate | **4.2%** | 48.3% |
| Bare rate | **95.9%** | 51.7% |

Only 12 m-terminal tokens have any suffix at all (3 -dy, 3 -om, 2 -y, and singletons). This is a 11.5x suppression ratio -- the strongest suffix suppression of any terminal atom.

This connects to C1420 (ARTICULATOR suffix suppression at 38.1% vs 64.3%) but is far more extreme. m acts as a **self-contained operator** that doesn't need suffix parameterization.

Suffix mode distribution for the 12 suffixed tokens: 5 Mode A, 7 Mode B (too small for statistical inference).

---

## T6: Category Concentration

**m-terminal is 87.9% TRANSITION -- the most category-concentrated terminal atom.**

| Category | m-terminal % | Overall % | Enrichment |
|----------|-------------|-----------|------------|
| TRANSITION | 87.9% | 15.0% | 5.86x |
| OPERATION | 9.0% | 14.2% | 0.63x |
| STAGING | 3.1% | 12.8% | 0.24x |
| All others | 0.0% | 58.0% | 0.00x |

Five categories are completely absent from m-terminal MIDDLEs: THERMAL, MONITORING, FLOW, CONTAINMENT, MARKING. m is exclusively in the TRANSITION + OPERATION + STAGING space. This confirms the GUIDE.md characterization (m -> 87% TRANSITION) exactly.

Per-MIDDLE breakdown:
- `am` (174 tokens): TRANSITION
- `m` (76 tokens): TRANSITION
- `om` (25 tokens): OPERATION
- `im` (8 tokens): STAGING
- All singleton MIDDLEs: TRANSITION (faim, kam, eam, fam) or OPERATION (opom) or STAGING (lm)

m-terminal accounts for 7.4% of all TRANSITION tokens, making it a significant contributor to the TRANSITION category despite being only 1.25% of all tokens.

---

## T7: Successor Analysis

**Within-line successors** (76 tokens where m is NOT line-final):

| Category | Rate |
|----------|------|
| TRANSITION | 22.4% |
| FLOW | 18.4% |
| OPERATION | 17.1% |
| CONTAINMENT | 10.5% |
| MARKING | 9.2% |
| STAGING | 9.2% |
| THERMAL | 7.9% |

When m-terminal is NOT the last token, it is followed by a broadly distributed successor profile. The modest THERMAL depletion (7.9% vs 23.9% baseline) is notable -- the line is already past its thermal phase.

**Cross-line successors** (210 transitions from m-terminal line-final to next line's first token):

The cross-line successor profile after m-closed lines is nearly identical to the overall cross-line profile after non-m-closed lines. THERMAL at 23.3% matches the non-m rate of 21.9%. m does not preferentially route to any specific category on the next line.

**Verdict:** m terminates the current line's operational sequence without biasing what comes next. It is a pure closure signal, not a routing signal.

---

## T8: Hazard Topology

**m-terminal is completely excluded from hazard categories:**

| Measure | m-terminal | Overall |
|---------|-----------|---------|
| Hazard categories (FLOW + CONTAINMENT) | 0.0% | 23.9% |
| Preceded by hazard category | 31.8% | -- |
| Followed by hazard category | 7.6% | -- |

m never appears in FLOW or CONTAINMENT -- the two hazard-carrying categories (C1280). However, 31.8% of m-terminal tokens are preceded by tokens in hazard categories, especially FLOW (27.4% of predecessor categories). This suggests m often closes sequences that include FLOW operations.

---

## T9: m vs Other Terminals

| Terminal | Overall % | Final % | Concentration | Initial % |
|----------|-----------|---------|---------------|-----------|
| **m** | **1.25%** | **8.81%** | **7.0x** | **0.04%** |
| y | 20.70% | 21.38% | 1.0x | 17.06% |
| l | 11.12% | 12.45% | 1.1x | 10.81% |
| n | 9.30% | 6.46% | 0.7x | 12.58% |
| r | 8.50% | 8.65% | 1.0x | 9.67% |
| h | 5.56% | 3.76% | 0.7x | 5.46% |
| k | 12.95% | 8.85% | 0.7x | 8.92% |
| t | 4.16% | 3.64% | 0.9x | 1.57% |

m is:
- The **rarest** terminal (1.25% vs n at 9.30%, the next-rarest standard terminal)
- The **most positionally concentrated** (7.0x vs next-highest l at 1.1x)
- **Near-zero at line-initial** (0.04%, only 1 token out of 2,554 initial positions)
- The only terminal with both extreme line-final enrichment AND extreme line-initial depletion

The line-initial rate of 0.04% (1 token) means m is effectively **forbidden** at line-initial position. Combined with the 8.81% line-final rate, m has the most extreme positional polarity of any atom in the system.

---

## T10: Functional Closure Test

### Line Length
m-closed lines are significantly **longer** than non-m lines:
- m-closed: mean 10.9 tokens
- Non-m: mean 9.4 tokens
- Mann-Whitney U-test: p < 0.000001

Lines that end with m have ~1.5 more tokens on average. This suggests m closes lines that have gone through more operational steps.

### Category Composition
m-closed lines show elevated TRANSITION (20.4% vs 14.1%, ratio 1.44x) and slightly depressed MONITORING (0.68x) and STAGING (0.81x). THERMAL is near-normal (0.93x). Lines ending in m are doing more state-change work.

### Paragraph Position
m-closed lines strongly concentrate in **body** position:

| Position | m-closed | Non-m | m-frac |
|----------|----------|-------|--------|
| Header | 36 | 466 | 7.2% |
| Body | 158 | 1,251 | 11.2% |
| Last (par-final) | 17 | 459 | 3.6% |
| Single-line para | 2 | 31 | 6.1% |

m is enriched in body lines (11.2%) and depleted at paragraph-final (3.6%). This confirms T3: m is a BODY-LINE closer.

### Section Distribution
Per-section m-terminal rate at line-final:

| Section | m-rate at line-final |
|---------|---------------------|
| C (Cosmo) | 18.3% |
| H (Herbal) | 14.3% |
| S (Stars/Recipe) | 10.0% |
| T (Zodiac) | 8.1% |
| B (Bio/Bathing) | 3.2% |

Bio section has the lowest m-final rate (3.2%), while Cosmo has the highest (18.3%). This anti-correlates with THERMAL intensity -- Bio is the most THERMAL-intensive section (C553). Sections with less thermal work use more m-terminal closure markers.

### -am Suffix vs m-Terminal MIDDLE

These are **two completely distinct systems:**

| Feature | -am Suffix | m-Terminal MIDDLE |
|---------|-----------|-------------------|
| N tokens | 234 | 289 |
| Overlap | 1 token | 1 token |
| Category profile | Multi-category (FLOW 34.6%, THERMAL 26.5%, MARKING 19.2%) | Near-pure TRANSITION (87.9%) |
| Line-final rate | 82.1% | 77.9% |
| Paragraph-final | 5.19x enriched (C1237) | 0.31x DEPLETED |
| Function | Paragraph terminator | Body-line closer |

The -am suffix (C1237) terminates paragraphs. The m-terminal MIDDLE closes body lines. Both are line-final concentrated but serve different structural levels. Their near-zero overlap (1 token: `amam`) confirms these are orthogonal systems.

---

## Predecessor Analysis

What comes before m-terminal tokens?

| Category | Rate (of predecessors) |
|----------|----------------------|
| FLOW | 27.4% |
| TRANSITION | 19.4% |
| THERMAL | 14.2% |
| STAGING | 13.9% |
| OPERATION | 10.1% |

FLOW is the most common predecessor (27.4%), well above its overall rate (~19%). This means m frequently closes sequences that have been doing FLOW operations. The pattern is: operations → FLOW → m-close.

---

## Synthesis: What m-Terminal IS

The m-terminal atom is a **dedicated body-line closure operator** with the following characteristics:

1. **Extreme positional polarity:** Near-zero at line-initial (0.04%), exponentially ramping to 8.8% at line-final. The 7.0x concentration index is unmatched by any other terminal.

2. **Body-line scope:** Closes interior paragraph lines, NOT headers (0%), NOT paragraph-final lines (depleted). The -am suffix handles paragraph termination; m-terminal handles line closure.

3. **Near-pure TRANSITION:** 87.9% TRANSITION category. m is the most category-specific terminal atom -- it does one thing (state change/closure) and nothing else.

4. **Channel-restricted:** Depleted in thermal (qo 0.02x), monitoring (ch/sh 0.16-0.17x) channels. Enriched in output (ar/al/or 4.6-6.5x) and infrastructure (da 3.7x) channels.

5. **Self-contained:** 95.9% bare (no suffix). m doesn't need suffix parameterization -- it IS the closure operation.

6. **Hazard-excluded:** 0% in FLOW/CONTAINMENT categories. Never a hazard source or target.

7. **Low diversity:** Only 10 MIDDLE types, dominated by `am` (60%) and bare `m` (26%). Unlike other terminals which appear in dozens of different MIDDLEs, m is essentially a 2-3 word vocabulary.

8. **Section-modulated:** Strongest in Cosmo/Herbal (14-18%), weakest in Bio (3.2%). Anti-correlates with THERMAL intensity.

### The Two-System Closure Architecture

The line/paragraph closure architecture in Currier B uses two orthogonal systems:

| System | Scope | Mechanism | Category | Suffix | Rate |
|--------|-------|-----------|----------|--------|------|
| m-terminal MIDDLE | Body-line closure | MIDDLE atom `m` as terminal | TRANSITION (87.9%) | Suppressed (4.2%) | 8.8% of line-final |
| -am suffix (C1237) | Paragraph termination | Suffix `-am` | Multi-category | IS the suffix | 5.19x par-final |

These two systems share an "m" character but operate at completely different levels of the grammar. The MIDDLE m closes individual operational lines; the suffix -am closes entire paragraphs.

---

## New Constraints

### C1434: m-Terminal Low-Diversity Closure Specialization
m-terminal MIDDLE atom has only 10 types (289 tokens, 1.25% of B). Two MIDDLEs (`am` 60%, `m` 26%) account for 86.5%. Vocabulary diversity is the lowest of any terminal atom (10 types vs y: 33, l: 48, r: 49, h: 188). 95.9% bare (no suffix). m is a structurally specialized closure terminal with minimal internal diversification.

### C1435: m-Terminal Body-Line Exclusivity
m-terminal is a body-line-final signal: 10.45% rate at body-line-final (not paragraph-final), 0.00% at header-line-final, 3.26% at paragraph-final (Fisher p < 0.000001 vs body). m is categorically excluded from paragraph headers and depleted at paragraph boundaries. Scope is LINE BODY, not paragraph or folio.

### C1436: m-Terminal Near-Pure TRANSITION Category
m-terminal MIDDLEs are 87.9% TRANSITION (5.86x enrichment), the most category-concentrated terminal atom. Five categories are completely absent (THERMAL, MONITORING, FLOW, CONTAINMENT, MARKING). m accounts for 7.4% of all TRANSITION tokens despite being only 1.25% of corpus.

### C1437: m-Terminal Complete Hazard Exclusion
m-terminal has 0% tokens in hazard categories (FLOW, CONTAINMENT). 31.8% of m-terminal tokens are preceded by FLOW-category tokens, suggesting m closes sequences that include flow operations. m is never a hazard source, target, or buffer.

### C1438: m-Terminal Categorical Suffix Suppression
m-terminal tokens have 4.2% suffix rate vs 48.3% overall (11.5x suppression ratio). This is the most extreme suffix suppression of any MIDDLE terminal atom. m-terminal MIDDLEs are self-contained operators that do not accept suffix parameterization.

### C1439: m-Terminal MIDDLE and -am Suffix Are Orthogonal Systems
m-terminal MIDDLE (289 tokens, 87.9% TRANSITION, body-line-final) and -am suffix (234 tokens, multi-category, paragraph-final) overlap at exactly 1 token. They share an `m` character but operate at different grammar levels: m-terminal closes body lines, -am suffix closes paragraphs. Two-level closure architecture.

---

## Falsification Criteria

- C1434: If m-terminal vocabulary exceeds 20 distinct types or suffix rate exceeds 15%
- C1435: If m-terminal rate at header-line-final exceeds 3% or par-final exceeds body-line-final
- C1436: If TRANSITION fraction of m-terminal drops below 70%
- C1437: If m-terminal tokens appear in FLOW or CONTAINMENT at >2%
- C1438: If m-terminal suffix rate exceeds 15%
- C1439: If overlap between m-terminal MIDDLE and -am suffix exceeds 10 tokens
