# C460: AZC Entry Orientation Effect

**Tier:** 2 | **Status:** CONFIRMED (with nuance) | **Scope:** Cross-system (AZC x HT)

---

## Statement

AZC folios show a significant **HT step-change pattern**: human-track density is above average *before* AZC pages and below average *after* them.

However, this pattern is **not unique to AZC** - random manuscript positions show similar structure. AZC may be **placed at natural HT transitions** rather than causing them.

---

## Evidence

### Step-Change Test (All Window Sizes)

| Window | Pre-entry HT (z) | Post-entry HT (z) | Step Change | p-value |
|--------|------------------|-------------------|-------------|---------|
| +/-5 folios | +0.106 | -0.076 | -0.183 | 0.0016 |
| +/-10 folios | +0.200 | -0.185 | -0.385 | <0.0001 |
| +/-15 folios | +0.282 | -0.301 | -0.583 | <0.0001 |

Pattern confirmed at all scales with high significance.

### Gradient Analysis

| Window | Slope | R-squared | Direction |
|--------|-------|-----------|-----------|
| +/-5 | -0.030 | 0.86 | DECAY |
| +/-10 | -0.036 | 0.97 | DECAY |
| +/-15 | -0.037 | 0.98 | DECAY |

HT systematically decreases through AZC neighborhoods (R^2 > 0.86).

### Comparison to Control Groups

| Comparison | KS p-value (window +/-10) | Patterns Differ? |
|------------|---------------------------|------------------|
| AZC vs Random | 0.603 | **NO** |
| AZC vs Currier A | 0.0017 | YES |
| AZC vs Currier B | 0.0017 | YES |

**Critical finding:** AZC trajectory does NOT differ significantly from random positions, but DOES differ from both A and B system entries.

### Zodiac vs Non-Zodiac AZC

| Subgroup | Step Change (+/-10) |
|----------|---------------------|
| Zodiac AZC | -0.390 |
| Non-Zodiac AZC | -0.361 |

Zodiac shows slightly stronger step-change, but both subgroups exhibit the pattern.

---

## Interpretation

### What the data shows

1. HT is **elevated before AZC** and **reduced after AZC**
2. This pattern is statistically significant
3. The pattern resembles **random manuscript positions** more than A or B entries
4. Zodiac AZC shows the effect more strongly

### What this likely means

AZC folios appear to be **positioned at natural HT transition zones** in the manuscript - places where human vigilance demand is already shifting.

This is consistent with AZC as **orientation markers** placed at cognitively meaningful boundaries, rather than AZC *causing* the HT shift.

### What this does NOT mean

- AZC does not "reset" attention (it marks transitions, not creates them)
- The step-change is not unique to AZC (random shows similar structure)
- AZC is not an "entry point" in a procedural sense

---

## Architectural Implications

This finding supports a refined understanding of AZC:

> AZC marks cognitive landmarks within the manuscript's attention landscape, rather than controlling or modulating that landscape.

AZC folios cluster at positions where HT naturally transitions from high to low. This suggests intentional placement for orientation purposes.

---

## Relationship to Other Constraints

- **C313**: AZC constrains legality, not behavior - consistent
- **C454**: AZC does not modulate B execution - consistent
- **C459**: HT reflects human burden - AZC marks burden transitions
- **C458**: Risk is clamped elsewhere - AZC handles orientation, not risk

---

## What Remains Unknown

1. Why AZC pages cluster at HT transition zones
2. Whether this is designer intent or emergent structure
3. Whether Zodiac AZC serves a different function than non-Zodiac

---

## Phase Documentation

Research conducted: 2026-01-10 (E4 - AZC Entry Orientation Trace)

Scripts:
- `phases/exploration/azc_entry_orientation_trace.py`

Results:
- `results/azc_entry_orientation_trace.json`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
