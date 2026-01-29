# AX_BEHAVIORAL_UNPACKING

**Status:** COMPLETE | **Date:** 2026-01-26 | **Constraints:** C614-C617

## Purpose

Unpack AX (AUXILIARY) behavior below the class level. C572 established that 19 AX ICC classes collapse to <=2 effective behavioral groups. This phase tests whether MIDDLE-level differentiation exists within those collapsed groups, integrates AX-predicted UN tokens, and characterizes section/REGIME/LINK conditioning.

## Scripts

| Script | Purpose |
|--------|---------|
| `ax_token_routing.py` | MIDDLE-level routing within subgroups, priming test, diversity coupling, Class 22 deep dive |
| `ax_un_integration.py` | AX-predicted UN subgroup classification, routing comparison, MIDDLE overlap, combined profile |
| `ax_context_conditioning.py` | Section-stratified transitions, section-specific MIDDLE selection, REGIME interaction, LINK interaction |

## Key Findings

### 1. MIDDLE-Level Routing Signal (C614)

MIDDLE adds routing information beyond subgroup position in INIT and MED but not FINAL:
- AX_INIT: chi2=136.69, p=0.000003, V=0.167
- AX_MED: chi2=190.49, p<0.000001, V=0.147
- AX_FINAL: chi2=4.15, p=0.645 (not significant)

No priming: AX MIDDLE does NOT predict successor MIDDLE (all permutation p>0.05).

AX MIDDLE diversity strongly predicts operational diversity: EN rho=+0.796***, FQ rho=+0.660***.

Class 22 is extreme FINAL (62.2% line-final vs 32.4% other AX_FINAL), explaining its 60% context detectability.

### 2. AX-UN Functional Integration (C615)

2,246 AX-predicted UN tokens route identically to classified AX (all subgroups p>0.1):
- AX_INIT: p=0.614, V=0.046
- AX_MED: p=0.119, V=0.056
- AX_FINAL: p=0.150, V=0.098

89.3% of classified AX MIDDLEs shared with AX-UN. 312 truly novel MIDDLEs introduced.
Combined AX: 6,098 tokens (26.4% of B), up from 3,852 (16.7%).

### 3. Section/REGIME Conditioning (C616)

Section affects AX transitions (V=0.081) and MIDDLE selection (V=0.227). REGIME affects AX transitions (V=0.082):
- AX->EN: REGIME_1=39.1%, REGIME_2=24.5% (Kruskal-Wallis p=0.0006)
- AX->FQ: REGIME-dependent (p=0.003), refining C602

Section-enriched MIDDLEs: dy->H, ch->T, aiin->C, k->C.

### 4. AX-LINK Subgroup Asymmetry (C617)

LINK concentrates at AX boundary positions:
- AX_FINAL: 35.3% LINK (2.7x average)
- AX_INIT: 19.4% LINK (1.5x average)
- AX_MED: 3.3% LINK (0.25x average)

Line-level co-occurrence: chi2=16.21, p<0.001. No folio-level correlation (p=0.198).

## Constraints Produced

| # | Name | Key Evidence |
|---|------|-------------|
| C614 | AX MIDDLE-Level Routing | INIT V=0.167, MED V=0.147, FINAL n.s.; no priming; AX~EN rho=+0.796*** |
| C615 | AX-UN Functional Integration | All subgroups p>0.1; 89.3% MIDDLE shared; combined 26.4% of B |
| C616 | AX Section/REGIME Conditioning | Section V=0.081/0.227; REGIME V=0.082; AX->EN p=0.0006 |
| C617 | AX-LINK Subgroup Asymmetry | AX_FINAL 35.3% LINK, AX_MED 3.3%; co-occurrence p<0.001 |

## Data Dependencies

| File | Source |
|------|--------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| regime_folio_mapping.json | REGIME_SEMANTIC_INTERPRETATION |
| voynich.py | scripts/ |

## Verification

- AX token count: 3,852 (matches C572)
- AX-predicted UN: 2,246 (PREFIX majority method; consistent with C611 prefix_prediction AX=2,246)
- LINK density: 13.2% (matches C609)
- Sections: B, C, H, S, T (all present)
- REGIMEs: 1-4 (all present)
