# C1195: Atom Gloss Confidence Tiers

**Tier:** 2
**Scope:** B
**Phase:** ATOM_GLOSS_AUDIT (Phase 424)
**Depends on:** C1190 (MIDDLE additive composition), C777 (FL state index)

## Constraint

The 18 MIDDLE atom glosses fall into four confidence tiers based on compound evidence validation:

| Tier | Atoms | Count | Criterion |
|------|-------|-------|-----------|
| **LOCKED** | k(heat), e(cool), h(watch), y(end), i(iterate), n(halt), a(yield), m(final) | 8 | Strong compound evidence, internally consistent across multiple glossed compounds |
| **SOLID** | d(mark), t(transfer) | 2 | Good evidence from compounds, correct but label might be refined |
| **PLAUSIBLE** | c(adjust), p(pause), f(flag), s(sequence), g(complete), x(diagram) | 6 | Thin evidence, nothing contradicts; too few compounds to fully validate |
| **WEAK** | o(work), l(frame), r(input) | 3 | Correct direction but very generic/abstract; FL positional data (C777) is stronger signal than operational gloss |

## Evidence

Spot-check analysis of all 18 atoms against 91 manually glossed compounds (GLOSSING.md + dictionary):

- **LOCKED atoms**: Each validated against 4+ glossed compounds where atom decomposition explains the compound gloss. Example: k=heat validated through ke=sustained heat, ck=direct heat, ek=precision, kc=intense heat-seal (order-sensitive). The i+n family (in=link, iin=iterate, ain=intake, aiin=settle) is the most internally consistent family in the system.
- **SOLID atoms**: d=mark validated through ed=discharge, od=collect, ked=release, keed=vent, eod=stand — all output/product operations. Could be refined to "product". t=transfer fits ct=control, te=rapid gather, et=path, ot=route.
- **WEAK atoms**: o=work (FL pos 0.751) is too generic — "work" doesn't constrain. l=frame (FL pos 0.618) has tenuous connections. r=input (FL pos 0.507) has only 3 glossed compounds.

Dictionary synchronized: 5 atom glosses corrected from FL-stage markers (C777) to GLOSSING.md expert-validated values: i(early→iterate), l(late→frame), o(near→work), r(mid→input), s(break→sequence). Both readings coexist — FL positional data is structural observation, operational gloss is interpretive.

## Falsification

Would be falsified if new compound glosses systematically contradict LOCKED atom glosses (e.g., if k-compounds consistently mean something unrelated to heat).

## Provenance

- `phases/ATOM_GLOSS_AUDIT/scripts/spotcheck_report.py` — atom-by-atom compound analysis
- `phases/ATOM_GLOSS_AUDIT/scripts/generate_autogloss.py` — confidence tier assignments
- `phases/ATOM_GLOSS_AUDIT/results/spotcheck_report.txt` — full spot-check report
- `phases/ATOM_GLOSS_AUDIT/results/autogloss_summary.json` — tier distribution
