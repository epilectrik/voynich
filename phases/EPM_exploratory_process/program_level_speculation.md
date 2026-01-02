# Program-Level Speculation

> **PURPOSE**: Speculate on what kinds of operations different program role types might perform, grounded in locked grammar constraints.

> **STATUS**: EXPLICITLY SPECULATIVE AND NON-BINDING

---

## Framework

The locked grammar identifies 83 programs classified across stability, waiting, convergence, and recovery dimensions. This document speculates on what *kinds of physical transformations* each role type might correspond to—without claiming specific products or materials.

---

## ULTRA_CONSERVATIVE Programs (4.8%)

**Representatives**: f26v, f41v, f48v

**STRUCTURAL SUPPORT**:
- link_density: 0.504 (highest)
- hazard_density: 0.496 (lowest)
- Max consecutive LINK: 7
- Near-miss count: 9 (lowest)

**Speculative Operations** (MEDIUM confidence):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Gentle conditioning** | Slow equilibration of material | Maximizes wait time, minimizes intervention |
| **Holding / storage** | Maintaining material in stable state | High LINK = "do almost nothing" |
| **Delicate substrate handling** | Processing fragile or easily damaged material | Avoids stress, stays far from hazards |
| **Post-processing stabilization** | Allowing product to settle after active phase | 100% convergence with minimal action |

**Physical Actions** (PURE SPECULATION):
- Material sits in circulation loop with minimal flow adjustment
- Temperature/concentration held steady
- Time passes; material equilibrates slowly
- Operator observes but rarely intervenes

**Workshop Intuition** (LOW confidence):
> *"Run this program when you've just loaded something delicate, or when you need to keep the batch stable overnight. It won't push the material—just let it settle."*

---

## CONSERVATIVE Programs (21.7%)

**Representatives**: f31v, f40v, f48r

**STRUCTURAL SUPPORT**:
- link_density: 0.469
- hazard_density: 0.515
- Near-miss count: 11
- Recovery ops present but low

**Speculative Operations** (MEDIUM confidence):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Gradual extraction** | Slow removal of mobile fractions | Moderate waiting + some active circulation |
| **Light conditioning** | Gentle shifting of material state | Conservative but not passive |
| **Initial treatment** | First-stage processing before more aggressive steps | Safe starting point in progression |
| **Training programs** | Operations for new apprentices | Low risk, forgiving of operator error |

**Physical Actions** (PURE SPECULATION):
- Flow adjusted periodically but not aggressively
- Material circulates at moderate rate
- Operator has time to observe between interventions
- Recovery available if something starts to drift

**Workshop Intuition** (LOW confidence):
> *"Standard working programs. Use these for everyday substrates that don't need pushing. Good for learning the apparatus."*

---

## MODERATE Programs (55.4%)

**Representatives**: f26r, f31r, f33r

**STRUCTURAL SUPPORT**:
- link_density: 0.396 (near mean)
- hazard_density: 0.554 (near mean)
- Intervention frequency: ~5.9 (mean)
- 47% REGULAR_STABLE convergence

**Speculative Operations** (MEDIUM confidence):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Standard extraction** | Typical operating regime for most substrates | Dominates the library (55%) |
| **Routine conditioning** | Normal maintenance circulation | Balanced wait/action ratio |
| **Workhorse programs** | General-purpose operations | Neither cautious nor aggressive |
| **Adapted processing** | Flexible enough for substrate variation | Moderate in all dimensions |

**Physical Actions** (PURE SPECULATION):
- Regular alternation between waiting and adjustment
- Flow and temperature modified at predictable intervals
- Material experiences moderate stress
- Most common operating mode

**Workshop Intuition** (LOW confidence):
> *"These are your everyday programs. Most of what you'll run. Nothing special, just solid work."*

---

## AGGRESSIVE Programs (18.1%)

**Representatives**: f75r, f76r, f76v

**STRUCTURAL SUPPORT**:
- link_density: 0.303 (lowest)
- hazard_density: 0.668 (highest)
- Near-miss count: 34 (very high)
- Often EXTENDED scale (>800 instructions)

**Speculative Operations** (MEDIUM confidence):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Intensive extraction** | Pushing material hard to maximize transfer | High hazard, low waiting |
| **Boundary-pushing processing** | Operating near limits for maximum effect | Many near-misses |
| **Recalcitrant substrate handling** | Difficult materials needing strong treatment | Aggressive action required |
| **Final-stage concentration** | Late-cycle intensification | Often long (EXTENDED scale) |

**Physical Actions** (PURE SPECULATION):
- Rapid adjustments, little waiting
- Material stressed toward its limits
- Operator must be vigilant—many near-misses
- Risk of runaway if attention lapses

**Workshop Intuition** (LOW confidence):
> *"Master-level programs. Don't run these until you know the apparatus well. They'll push the material—and you—hard. Watch for phase instability."*

---

## LINK_HEAVY_EXTENDED Programs (7.2%)

**Representatives**: f26v, f48r, f48v

**STRUCTURAL SUPPORT**:
- link_density: 0.504+
- max_consecutive_link: 7
- EXTENDED scale
- Overlaps with ULTRA_CONSERVATIVE

**Speculative Operations** (MEDIUM confidence):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Very long equilibration** | Multi-hour or overnight settling | Maximum waiting, extended duration |
| **Slow diffusion processes** | Waiting for mobility-limited transport | Long LINK chains = physical delay |
| **Patient conditioning** | Gradual state shift over extended time | Time is the primary variable |
| **Maturation holding** | Keeping material in stable cycling indefinitely | No rush, no stress |

**Physical Actions** (PURE SPECULATION):
- Apparatus runs for extended periods with minimal adjustment
- Material slowly equilibrates through repeated circulation
- Long sequences of LINK = "wait, wait, wait, check, wait..."
- Operator can leave and return

**Workshop Intuition** (LOW confidence):
> *"Set this up in the evening. Let it run overnight. Come back tomorrow and see where it is. Don't rush it."*

---

## LINK_SPARSE Programs (16.9%)

**Representatives**: f31r, f33r, f46r

**STRUCTURAL SUPPORT**:
- link_density: ~0.295
- Still may have max_consecutive_link: 7
- Often MODERATE stability

**Speculative Operations** (MEDIUM confidence):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Active processing** | More intervention than waiting | Low LINK = frequent adjustment |
| **Rapid-cycle extraction** | Fast circulation with quick adjustments | Speed priority |
| **Responsive operation** | Handling changing conditions | Must keep acting, not waiting |
| **Throughput-oriented** | Moving material through faster | Less patience built in |

**Physical Actions** (PURE SPECULATION):
- Operator stays engaged—less idle time
- Flow or temperature adjusted frequently
- Material moves through faster
- More work per unit time

**Workshop Intuition** (LOW confidence):
> *"These programs keep you busy. Less waiting around. Good when you need to process quickly, but watch for overshoot."*

---

## HIGH_INTERVENTION Programs (12.0%)

**Representatives**: f33r, f33v, f39r, f55r, f66v, f86v4, f94v, f95r2, f95v2, f116r

**STRUCTURAL SUPPORT**:
- intervention_frequency: >8 operations per cycle
- Often complex programs
- Mixed stability profiles

**Speculative Operations** (MEDIUM confidence):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Sensitive substrate handling** | Materials that need constant monitoring | High intervention = active attention |
| **Critical processing** | Delicate operations requiring precision | Frequent adjustment |
| **Unstable regime management** | Operating near boundaries intentionally | Must keep correcting |
| **Multi-variable control** | Managing several parameters simultaneously | Many adjustments needed |

**Physical Actions** (PURE SPECULATION):
- Operator constantly adjusting
- Small corrections prevent drift
- Material in sensitive regime
- Cannot step away

**Workshop Intuition** (LOW confidence):
> *"Hands-on programs. Stay with the apparatus the whole time. Small adjustments, frequently. Don't let it drift."*

---

## RESTART_CAPABLE Programs (3.6%)

**Representatives**: f50v, f57r, f82v

**STRUCTURAL SUPPORT**:
- Contain reset_present marker
- Can return to initial state
- Only 3 in entire corpus

**Speculative Operations** (HIGH confidence for role, LOW for meaning):

| Operation Type | Description | Why It Fits |
|----------------|-------------|-------------|
| **Error recovery** | Starting over after something went wrong | Reset capability |
| **Fresh batch initiation** | Beginning processing on new material | Return to initial state |
| **Cleaning/purging cycle** | Clearing apparatus before new operation | Full reset |
| **Calibration programs** | Returning to known baseline | Restart from reference |

**Physical Actions** (PURE SPECULATION):
- f57r especially significant (only folio with pure restart behavior)
- Clear circulation loop
- Dump or remove current charge
- Return apparatus to baseline
- Prepare for fresh start

**Workshop Intuition** (MEDIUM confidence):
> *"Something went wrong? Run f57r. It'll clear the apparatus and get you back to a known state. Then start over with the right program."*

---

## Transformation Type Summary

| Role | Primary Transformation | Time Character | Operator Demand |
|------|------------------------|----------------|-----------------|
| ULTRA_CONSERVATIVE | Equilibration / holding | Very long | Minimal |
| CONSERVATIVE | Gentle extraction / conditioning | Long | Low |
| MODERATE | Standard processing | Moderate | Moderate |
| AGGRESSIVE | Intensive extraction / concentration | Variable | High |
| LINK_HEAVY_EXTENDED | Slow diffusion / maturation | Very long | Minimal |
| LINK_SPARSE | Active processing / rapid cycle | Short | High |
| HIGH_INTERVENTION | Sensitive / critical processing | Variable | Very high |
| RESTART_CAPABLE | Recovery / fresh start | N/A | Depends |

---

## Cross-Role Interpretation

**HISTORICAL ALIGNMENT** (MEDIUM confidence):

The program role distribution suggests a library optimized for:

1. **Majority everyday use** (55% MODERATE) — Most substrates, most days
2. **Conservative fallback** (22% CONSERVATIVE) — When unsure, use these
3. **Expert-only aggressive** (18% AGGRESSIVE) — Experienced operators, difficult substrates
4. **Specialty functions** (RESTART, HIGH_INTERVENTION) — Unusual situations

This matches the structure of **pre-modern craft training**:
- Apprentices learn CONSERVATIVE/MODERATE programs first
- Masters handle AGGRESSIVE programs
- Everyone knows the RESTART protocol

**PURE SPECULATION** (LOW confidence):

> *"The book is organized like a workshop manual. Start with the safe ones. Work up to the hard ones. Always know how to reset if things go wrong."*

---

## What This Does NOT Claim

- ❌ Specific materials processed
- ❌ Specific products made
- ❌ Historical identity of user
- ❌ Exact apparatus configuration
- ❌ Token-by-token meanings

---

*Speculation complete. See `material_candidates.md` for material-level hypotheses.*
