# C1487: Six-Terminal Functional Taxonomy

**Tier:** 2
**Scope:** B, MIDDLE, atom, TERMINAL, taxonomy, specificity, opacity
**Phase:** TERM_FUNCTIONAL_TAXONOMY (Phase 535)
**Date:** 2026-03-06

## Statement

The 6 TERMINAL atoms decompose into three functional tiers along category specificity:

**LOCKED (1-2 categories):** r=FLOW (98.9%), m=TRANSITION (87.9%). Category-imposing — the terminal overrides HEAD to determine operational domain.

**CHANNELED (3-4 categories):** l=STAGING (64.5%), y=OPERATION (40.6%), n=TRANSITION+STAGING (39.3%+27.7%). Category-guiding — the terminal narrows but does not fully determine domain.

**DIFFUSE (5-6 categories):** h=transparent across 6 categories (V=0.988 passthrough), bare=THERMAL-leaning across 6 categories. Category-transparent — HEAD+MODS determine domain.

This taxonomy cross-cuts the opacity gradient (C1440): OPAQUE terminals (m,n,y) span LOCKED and CHANNELED. SEMI-TRANSPARENT (l,r) span LOCKED and CHANNELED. TRANSPARENT (h,bare) are exclusively DIFFUSE. Opacity controls suffix gating; specificity controls operational domain. These are orthogonal design axes.

## Evidence

- **LOCKED:** r norm entropy 0.036, m norm entropy 0.211
- **CHANNELED:** l norm entropy 0.456, y norm entropy 0.631, n norm entropy 0.652
- **DIFFUSE:** h norm entropy 0.844, bare norm entropy 0.818
- **Opacity-specificity independence:** r is SEMI-TRANSPARENT but LOCKED; h is TRANSPARENT but DIFFUSE
- **Overall V:** 0.463 (TERMINAL × CATEGORY)
- **Pairwise JSD:** LOCKED terminals most distant from each other (m vs r: 0.977) and from all others

## Cross-references

- C1483: Terminal category specificity gradient (raw gradient this taxonomy organizes)
- C1484: Terminal modifier exclusivity (modifier channels align with tiers)
- C1485: HEAD×TERMINAL affinity partition (frame structure within tiers)
- C1486: m-terminal line-final closure (LOCKED tier member characterization)
- C1440-C1441: Terminal opacity gradient (orthogonal axis)
- C1475: HEAD domain taxonomy (symmetric counterpart for HEAD atoms)
