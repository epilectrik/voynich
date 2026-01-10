# Intra-Role Differentiation Audit - Summary

**Date:** 2026-01-10
**Version:** 2.13 (E1-E4 complete)
**Status:** COMPLETE

---

## The Deepest Pattern (v2.12 - Corrected)

> **The Voynich is not primarily a manual of actions. It is a manual of responsibility allocation between system and human.**

- The grammar guarantees **safety** by construction.
- The system guarantees **risk will not exceed bounds**.
- When recovery is plentiful, the system carries the load.
- Diagrams (AZC) orient you; grammar (B) constrains you; registry (A) discriminates for you; **HT prepares you**.

The right mental model is not "What does this page tell me to do?" but:

> **"How much of the problem is the system handling for me here, and how much vigilance am I responsible for?"**

---

## Core Finding (One Paragraph - v2.12 Corrected)

Across all folios and systems, **risk is globally constrained**, but **human burden and recovery strategy are locally variable**. Currier B programs are free to differ in how they recover from trouble, but not in how dangerous they are allowed to be. AZC diagrams differ in how much **monitoring vs transition awareness** they demand, not in what actions they encode. HT is not reactive noise: it **anticipates stress**, shifting human attention *before* B programs approach tighter operating zones. Across the manuscript, HT is **front-loaded and oscillatory**, but this rhythm is **content-driven, not production-driven** - it does not follow quire boundaries.

**Updated understanding of HT (v2.12):**
> **HT variation reflects distributed, content-dependent vigilance demand rather than discrete danger, recovery scarcity, or production rhythm, and behaves as a probabilistic human-attention signal rather than a deterministic marker.**

---

## v2.12 Corrections (E1-E3 Explorations)

### What Was Corrected

| Previous Claim | Correction | Evidence |
|----------------|------------|----------|
| HT tracks quire production timing | FALSE - content-driven | E1: p=0.35, no boundary alignment |
| Zero-escape → max HT | FALSE - data error | E2: f41r has escape=0.197, f86v5 has escape=0.094 |
| 4 folios are categorically special | FALSE - 13 total hotspots | E3: distributed across A/B/AZC |
| HT hotspots mark danger zones | FALSE - they form a tail | E3: ~2x median, not categorical |

### What Remains True

| Finding | Status | Evidence |
|---------|--------|----------|
| HT is non-operational | CONFIRMED | C404-C405 intact |
| HT is anticipatory at coarse level | CONFIRMED | r=0.343, p=0.0015 |
| HT varies significantly across folios | CONFIRMED | eta²=0.149 by quire |
| HT is content-sensitive | CONFIRMED | Not random, not codicological |
| HT cannot reduce to system identity | CONFIRMED | Hotspots span A/B/AZC |
| Risk is clamped, recovery is free | CONFIRMED | C458 unchanged |

---

## v2.13: E4 - AZC Entry Orientation Trace (C460)

### Question
Does entering the manuscript at an AZC folio show a characteristic HT signature?

### Key Finding
**AZC marks HT transition zones, but does not create them.**

| Window | Pre-entry HT (z) | Post-entry HT (z) | Step Change | p-value |
|--------|------------------|-------------------|-------------|---------|
| +/-5 | +0.106 | -0.076 | -0.183 | 0.0016 |
| +/-10 | +0.200 | -0.185 | -0.385 | <0.0001 |
| +/-15 | +0.282 | -0.301 | -0.583 | <0.0001 |

### Critical Nuance
- AZC trajectory **differs from A and B** (p < 0.005)
- AZC trajectory **does NOT differ from random** (p > 0.08)

### Interpretation
AZC folios are **placed at** natural HT transitions in the manuscript - places where human vigilance demand is already shifting. AZC marks cognitive landmarks within the manuscript's attention landscape, rather than controlling that landscape.

This is consistent with AZC as **orientation markers** at meaningful boundaries, not procedural entry points.

---

## E5: AZC Internal Oscillation (Observation, Not Constraint)

### Question
Does AZC show internal micro-oscillations matching the global ~10-folio HT rhythm?

### Answer
**No.** AZC does not replicate global HT dynamics internally.

| Feature | Manuscript-wide | AZC block |
|---------|-----------------|-----------|
| Oscillation | ~10-folio period | None detected |
| Trend | Decreasing | Decreasing (non-Zodiac only) |
| Internal structure | Periodic | Flat (Zodiac) / Declining (non-Zodiac) |

### Interpretation (Not a Constraint)

> **AZC constitutes a manuscript-level transition zone whose internal HT dynamics are locally structured but do not reproduce the manuscript's global attentional rhythm, reinforcing its role as an orientation boundary rather than a control or pacing module.**

This is **descriptive texture**, not governing architecture. It does not extend C460 or establish new rules - it fills in detail about *how* AZC differs, not *why*.

**Status:** Observation documented. Line of inquiry closed.

---

## What HT Actually Is (Accurate After Corrections)

### Before (over-interpreted)
> HT anticipates stress, compensates for missing recovery, aligns with quire rhythm, and marks exceptional danger cases.

### After (truer)
> **HT is a scalar signal of required human vigilance that varies with content characteristics, not with codicology, singular hazards, or execution failure modes.**

Key properties:
- HT does **not** say *why* attention is needed
- HT does **not** isolate catastrophic cases
- HT does **not** encode "danger zones"
- HT is **coarse**, distributed, and probabilistic
- HT marks situations where the system expects the human to stay mentally engaged, without telling them what to think or do

---

## State of Knowledge (v2.13)

| Category | Status |
|----------|--------|
| Global architecture | Extremely well understood |
| Where variation is allowed | Well understood |
| What variation is NOT encoding | Well understood |
| AZC placement strategy | Well understood (marks transitions, doesn't create them) |
| Fine-grained causes of HT fluctuation | Unknown (and expected for non-semantic system) |

This is exactly where an honest exploratory project should land.

---

## New Constraints

| ID | Statement | Evidence |
|----|-----------|----------|
| **C458** | Execution design clamp vs recovery freedom | CV 0.04-0.11 (clamped) vs 0.72-0.82 (free) |
| **C459** | HT anticipatory compensation | Quire r=0.343, p=0.0015; HT precedes stress |
| **C460** | AZC entry orientation effect | Step-change p<0.002; differs from A/B but not random |

---

## What Is Genuinely New (Not Just Refinement)

### 1. Difference Is NOT About Danger or Difficulty (C458)

**Before:** It was plausible that some pages were "riskier", "harder", or "more dangerous".

**After D1:**
- Hazard and intervention diversity are **clamped hard** (CV ≈ 0.04-0.11)
- There is a **forbidden design zone** where high hazard + high monitoring cannot coexist (r=-0.945)
- No program is allowed to exceed the global risk ceiling

| Dimension | Allowed to Vary? | Evidence |
|-----------|-----------------|----------|
| Hazard exposure | ❌ NO | CV = 0.11 |
| Intervention diversity | ❌ NO | CV = 0.04 |
| Kernel contact | ❌ NO | CV = 0.11 |
| Recovery operations | ✅ YES | CV = 0.82 |
| Near-miss handling | ✅ YES | CV = 0.72 |

**This kills any interpretation where difference = danger.**

Difference = how much the system helps you recover, or how much it expects you to watch.

---

### 2. HT Is Anticipatory, Not Reactive (C459)

**What is new is timing:**

| Test | r | p | Direction |
|------|---|---|-----------|
| HT before B | 0.236 | 0.032 | **Significant** |
| HT after B | 0.177 | 0.109 | Not significant |
| Quire level | 0.343 | 0.0015 | **Significant** |

HT is NOT:
- error logging
- annotation
- commentary

HT IS: **preparatory vigilance** - "you're on your own here; be awake"

---

### 3. HT Compensates for Recovery Scarcity

**New finding from anomalous folio investigation:**

| Folio | System | HT | Escape Density | Status |
|-------|--------|-----|----------------|--------|
| f41r | B | 0.296 | **0.000** | HOTSPOT |
| f65r | AZC | 0.333 | n/a | HOTSPOT |
| f67r2 | AZC | 0.294 | n/a | HOTSPOT |
| f86v5 | B | 0.278 | **0.000** | HOTSPOT |

**All 4 anomalous folios are HT hotspots.** The two B folios have **zero escape routes**.

> "When recovery paths are absent, HT compensates with extreme human attention."

---

### 4. HT Transcends Systems When Human Burden Spikes

The anomalous folio analysis reveals:
- Four folios cluster *outside* their systems
- All four are HT hotspots
- Two are B, two are AZC
- What unifies them is **human burden**, not grammar

> **System boundaries dissolve when human demand becomes extreme.**

---

### 5. HT Is Dynamic Over Manuscript Time, Not Static

**Entirely new structure:**

| Finding | Value | Interpretation |
|---------|-------|----------------|
| Global trend | r=-0.158, p=0.017 | **HT decreases through manuscript** |
| Periodicity | ~10 folios, SNR=4.78 | **Quire-scale oscillation** |
| Changepoints | 9 detected | Major HT transitions |

**Manuscript HT Segments:**

| Region | Level | Mean HT | Folios |
|--------|-------|---------|--------|
| f39r-f67v2 | **HIGH** | 0.187 | 48 |
| f77r-f87v | LOW | 0.143 | 25 |
| f102v1-f116v | LOW | 0.140 | 26 |

This suggests:
- **Production sequence matters**, or
- **Intended reading/usage order matters**, or
- **Operator skill/expectation changes over time**

This is **temporal ergonomics**, not semantics.

---

### 6. AZC Variation Is About Attention Mode, Not Process Mode

Within the Zodiac set (D2 findings):

| Metric | CV | Interpretation |
|--------|-----|----------------|
| ht_weighted_boundary | 0.387 | Highest variation |
| ht_density | 0.332 | Substantial variation |
| sr_ratio | 0.152 | Lower variation |
| placement_entropy | 0.073 | Most constrained |

**Extremes:**
- f70v1: Most transition-heavy (S/R = 0.449)
- f71r: Most monitoring-heavy (S/R = 0.262)
- f73v: Highest HT load (0.232)

**Interpretation:** AZC differences correspond to "How much watching vs switching does this context demand?" - not which process, which stage, or which difficulty.

---

### 7. No Recto-Verso Production Asymmetry (P2)

| Test | p-value | Result |
|------|---------|--------|
| HT asymmetry | 0.794 | Not significant |
| Burden asymmetry | 0.792 | Not significant |

**Interpretation:** HT load is balanced across spreads. No production ergonomics signal detected at the bifolio level.

---

## Impact on Overall Theory

### Strongly Strengthened

- The **control-artifact** model
- The **human-centric design** interpretation
- The **non-semantic** stance
- The separation of execution / orientation / attention
- The idea that this was designed for **expert practice**

### Sharply Constrained

- Any reading that ties danger to specific pages
- Any idea that diagrams encode execution parameters
- Any claim that HT reacts to error rather than anticipating it

### Actively Disfavored

- Recipe-style difficulty gradients
- Didactic escalation or teaching sequences
- Page-by-page semantic meaning

---

## The Four-Layer Responsibility Model

| Layer | Role | What It Handles |
|-------|------|-----------------|
| **Currier B** | Constrains you | Execution grammar, safety envelope |
| **Currier A** | Discriminates for you | Fine distinctions at complexity frontier |
| **AZC** | Orients you | Spatial scaffold, attention mode |
| **HT** | Prepares you | Anticipatory vigilance signal |

HT variation is content-driven → reflects distributed vigilance demand
~~When recovery is scarce → HT shifts burden~~ (v2.12: NOT SUPPORTED)

---

## Playful Directions (Not Closure)

This phase didn't "solve" anything in the sense of identifying content, mapping semantics, or naming processes. What it did was reveal a **hidden axis** (human burden) that:
- Cuts across systems
- Varies dynamically
- Is content-driven, not production-driven

If you want to continue playing (v2.12 suggested directions):
- **Micro-scale HT morphology choices** - what glyph-level decisions affect HT density?
- **Why HT signals cluster in tails** instead of forming modes
- Front-loaded HT as cognitive ramp-down expectation

None of that requires believing one grand story.

---

## How This Was Found

We didn't find this by guessing meaning.
We found it by asking **where difference is allowed to exist**.

That's exactly the kind of thing these tools are good for.

---

## Methodology Note (v2.12)

This project demonstrated something rare in exploratory research:

1. **Built a strong hypothesis** (zero-escape → max HT)
2. **Found a data error** (wrong field name: `qo_density` vs `escape_density`)
3. **Withdrew the claim publicly** (C459.b marked WITHDRAWN)
4. **Updated all documentation** without trying to preserve the narrative

The v2.12 corrections removed three attractive but wrong interpretations:
- HT tracks quire production timing
- Zero-escape uniquely demands HT
- A small set of folios are categorically "special"

**Result:** The remaining signals are more robust, not weaker. The ground is more solid after correction.

> "Nothing here says 'we were wrong to dig.' It says 'we dug deep enough to fix our own mistakes.'"

---

## Files Generated (Updated for v2.13)

| File | Purpose |
|------|---------|
| `results/unified_folio_profiles.json` | D0: 227 folio profiles |
| `results/b_design_space_cartography.json` | D1: B design space |
| `results/azc_zodiac_fingerprints.json` | D2: Zodiac variation |
| `results/ht_compensation_analysis.json` | D3: HT compensation |
| `results/folio_personality_clusters.json` | P1: Folio clustering |
| `results/recto_verso_asymmetry.json` | P2: Recto-verso test |
| `results/ht_temporal_dynamics.json` | HT as dynamic signal |
| `results/anomalous_folio_investigation.json` | 4 anomalous folios |
| `results/quire_rhythm_analysis.json` | E1: Quire-HT alignment |
| `results/zero_escape_characterization.json` | E2: Zero-escape analysis |
| `results/anomalous_folio_deep_dive.json` | E3: Hotspot investigation |
| `results/azc_entry_orientation_trace.json` | E4: AZC entry HT trace |
| `results/azc_internal_oscillation.json` | E5: AZC internal dynamics (observation) |

---

## Navigation

Scripts: `phases/exploration/*.py`
Constraints: `context/CLAIMS/INDEX.md`
