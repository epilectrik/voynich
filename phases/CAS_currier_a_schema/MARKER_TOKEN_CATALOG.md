# Currier A Marker Token Catalog

**Phase:** CAS-DEEP
**Tier:** 2 (STRUCTURAL INFERENCE)
**Date:** 2026-01-06

---

## Summary

| Statistic | Value |
|-----------|-------|
| **Total unique marker tokens** | 1,123 |
| **Total marker occurrences** | 4,640 |
| **Core tokens (freq >= 10)** | 85 |
| **Marker classes** | 8 |

---

## The 8 Marker Classes

| Prefix | Unique Tokens | Occurrences | % of Total | Dominant Token |
|--------|---------------|-------------|------------|----------------|
| **CH** | 343 | 1,410 | 30.4% | chol (194) |
| **DA** | 73 | 717 | 15.5% | daiin (371 = **51.7%**) |
| **QO** | 239 | 714 | 15.4% | qotchy (42) |
| **SH** | 149 | 674 | 14.5% | shol (91) |
| **OK** | 97 | 346 | 7.5% | oky (35) |
| **CT** | 61 | 318 | 6.9% | cthy (74) |
| **OT** | 93 | 306 | 6.6% | otol (27) |
| **OL** | 68 | 155 | 3.3% | ol (50 = **32.3%**) |

---

## Core Marker Tokens (frequency >= 10)

### CH Class (25 core tokens)
```
chol      194    chor      130    chy        64    chey       55
cheol      34    cheor      34    chody      34    chaiin     33
cho        26    char       22    cheey      22    chodaiin   20
choky      18    cheody     17    chckhy     17    chal       12
chcthy     12    cheky      11    chocthy    11    chokchy    11
chom       11    choty      11    cham       10    cheo       10
chos       10
```

### DA Class (7 core tokens)
```
daiin     371    dain       64    dar        62    dal        47
dam        32    dair       29    dan        13
```

### QO Class (16 core tokens)
```
qotchy     42    qokol      33    qokchy     30    qoky       27
qoty       24    qokeey     23    qotol      19    qotor      17
qokaiin    13    qokchol    12    qotchol    12    qotchor    12
qokeol     12    qokey      11    qokor      11    qotaiin    11
```

### SH Class (13 core tokens)
```
shol       91    sho        79    shor       51    shy        46
shey       38    sheey      23    shody      21    sheol      20
shaiin     16    sheor      16    sheo       14    shodaiin   11
sheody     10
```

### OK Class (9 core tokens)
```
oky        35    okaiin     28    okol       26    okal       16
okeey      16    okchy      15    okeol      14    okor       11
okchor     10
```

### CT Class (7 core tokens)
```
cthy       74    cthol      44    cthor      33    cthey      24
cthaiin    13    cthar      11    ctho       10
```

### OT Class (7 core tokens)
```
otol       27    oty        27    otaiin     23    otchy      22
otchol     21    otchor     14    otal       12
```

### OL Class (1 core token)
```
ol         50
```

---

## Positional Patterns

| Class | First | Middle | Last | Typical Position |
|-------|-------|--------|------|------------------|
| CH | 3.4% | **84.7%** | 11.9% | Middle |
| DA | 9.1% | 65.7% | **25.2%** | Middle/Last |
| QO | **20.2%** | 72.7% | 7.1% | First/Middle |
| SH | 10.8% | **83.1%** | 6.1% | Middle |
| OK | 13.0% | **74.0%** | 13.0% | Middle |
| OT | 16.0% | **69.0%** | 15.0% | Middle |
| CT | 1.9% | **81.4%** | 16.7% | Middle (rarely first) |
| OL | 10.3% | **72.9%** | 16.8% | Middle |

**Key observations:**
- QO most likely to appear FIRST (20.2%)
- DA most likely to appear LAST (25.2%)
- CT almost never appears first (1.9%)
- All classes predominantly MIDDLE position

---

## Section Distribution

| Class | Section H | Section P | Section T |
|-------|-----------|-----------|-----------|
| CH | 1,180 (83.7%) | 153 (10.9%) | 77 (5.5%) |
| DA | 598 (83.4%) | 76 (10.6%) | 43 (6.0%) |
| QO | 579 (81.1%) | 93 (13.0%) | 42 (5.9%) |
| SH | 559 (82.9%) | 69 (10.2%) | 46 (6.8%) |
| OK | 238 (68.8%) | 76 (22.0%) | 32 (9.2%) |
| OT | 246 (80.4%) | 32 (10.5%) | 28 (9.2%) |
| CT | 301 (94.7%) | 5 (1.6%) | 12 (3.8%) |
| OL | 99 (63.9%) | 36 (23.2%) | 20 (12.9%) |

**Key observations:**
- CT is almost exclusively Section H (94.7%)
- OK and OL have relatively high Section P presence (22-23%)
- All markers present in all sections, but varying proportions

---

## Structural Primitive Connection

Two marker tokens are also **structural primitives** (Phase SP):

| Token | As Marker | As Structural Primitive |
|-------|-----------|------------------------|
| **daiin** | DA class: 371 occurrences (51.7% of class) | Record articulator in A, execution boundary in B |
| **ol** | OL class: 50 occurrences (32.3% of class) | Marginal in A, execution anchor in B |

These tokens serve dual roles:
1. Classification markers within Currier A's categorical registry
2. Structural primitives shared with Currier B's grammar

---

## Morphological Patterns

Common suffixes across marker classes:

| Suffix | Examples | Interpretation |
|--------|----------|----------------|
| -ol | chol, shol, qokol, okol, otol, cthol | Most common ending |
| -or | chor, shor, qotor, okor, cthor | Second most common |
| -y | chy, shy, qoky, oky, oty, cthy | Short form |
| -ey | chey, shey, qokey, okey, cthey | Variant of -y |
| -aiin | chaiin, shaiin, daiin, okaiin, cthaiin | Control-related? |
| -daiin | chodaiin, shodaiin, qodaiin | Compound with daiin |

The consistent morphological patterns suggest a **systematic construction** of marker tokens from prefix + base + suffix.

---

## Key Findings

1. **DA class is highly concentrated** - `daiin` alone accounts for 51.7% of all DA markers
2. **OL class is minimal** - `ol` alone accounts for 32.3%, total class only 3.3% of markers
3. **CH class is largest and most diverse** - 343 unique tokens, 30.4% of all markers
4. **Positional preferences exist** - QO tends first, DA tends last, CT avoids first
5. **Section conditioning** - CT heavily favors H; OK/OL favor P more than others

---

## Files Generated

- `cas_marker_catalog.py` - Extraction script
- `marker_token_catalog.json` - Full catalog (JSON)
- `core_marker_tokens.txt` - Core tokens list (plain text)
- `MARKER_TOKEN_CATALOG.md` - This reference document

---

## New Constraint

| # | Constraint |
|---|------------|
| 265 | Currier A uses 1,123 unique marker tokens across 8 classes; 85 core tokens (freq>=10) account for majority of classification (CAS-CAT) |
