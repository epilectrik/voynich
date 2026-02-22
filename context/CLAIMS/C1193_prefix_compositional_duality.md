# C1193: PREFIX Compositional Duality

**Tier:** 2
**Phase:** 423 (POSITIONAL_ATOMICITY)
**Scope:** Currier B PREFIX position

## Statement

PREFIX compounds split into two distinct classes based on compositional behavior:

1. **Compositional prefixes** — behavior predictable from position-specific atom profiles (ke r=0.922, te r=0.815, po r=0.784, ka r=0.747, ar r=0.915, or r=0.867, pch r=0.761, lk r=0.751, kch r=0.600). These are predominantly EXTENDED_PREFIXES.

2. **Emergent prefixes** — behavior NOT predictable from atom profiles; the compound acquires properties beyond its atoms (ch r=0.252, sh r=0.262, da r=0.161, ot r=0.260, ok r=0.324, ol r=0.354). These are exactly the CORE_PREFIXES.

The compositional/emergent split maps directly to the existing EXTENDED/CORE prefix classification in the morphological system.

## Cluster Analysis (T5)

PREFIX-vs-MIDDLE shift vectors cluster into 2 discrete groups (not a continuum):

- **Cluster 1 (emergent-associated):** {a, d, o, q} — atoms that participate in core/emergent prefixes
- **Cluster 2 (compositional):** {c, e, f, h, k, l, p, r, s, t, y} — atoms that compose transparently

At k=4 refinement: {e,f,l,p,r,y} | {c,h,s} | {k,t} | {a,d,o,q}

This is evidence for discrete positional role categories, not a smooth behavioral gradient.

## Interpretation

Core prefixes (ch, sh, da, qo, ok, ot, ol) are frozen functional units — morphological fossils that have acquired specialized operational identity beyond their atomic components. Extended prefixes (ke, te, ka, po, etc.) are productive compositions where atoms retain their individual behavioral contribution.

## Provenance

- Script: `phases/POSITIONAL_ATOMICITY/scripts/positional_atomicity_test.py` (T1, T5)
- Strengthens: C929 (ch/sh emergence), C1191 (position-dependent composition)
- Cross-references: C235 (core prefix set), C1190 (MIDDLE additivity)
