# Session Handoff: Atom-Level Cross-System Analysis

**Date:** 2026-04-01
**Last commit:** `11c3740` (Phase 633 complete, C1917-C1924)
**Current branch:** master
**Version:** 6.06 | **Constraints:** 1924 | **Phases:** 633
**Status:** Two formal phases completed, exploratory work preserved

---

## What We Did This Session

### Phase 632: aiin Cross-System Dual-Layer Architecture (C1908-C1916)

Investigated the aiin/daiin token family — the manuscript's most frequent token — across A/B/AZC at atom level. Both expert advisors independently identified this as the highest-leverage target.

**Central finding:** The family has **dual-layer architecture**:
- **Construction-layer** (same across all systems): n-terminal lock (93-95%), ii/ee domain complementarity (a-HEAD uses ii, e-HEAD uses ee)
- **Execution-layer** (system-specific): HEAD selection (A=57% headless, B=36% a-headed), positional grammar (daiin opens lines in B but not A)

**Key constraints:**
| C# | Finding |
|----|---------|
| C1908 | Zodiac i/d MOD swap (chi2=39.3, p=0.0006) — Summer/Winter = aiin, Spring/Autumn = ody |
| C1909 | aiin NEVER line-initial (0/469, all systems) — hardest positional constraint |
| C1910 | n-terminal lock cross-system (A=93.7%, B=94.7%, p=0.197) |
| C1911 | HEAD anatomy diverges (A=19.2% a-HEAD, B=35.9%, p<0.001) |
| C1912 | ii/ee complementary domains confirmed cross-system |
| C1913 | C1908 driven by aiin-family specifically (p=0.0033) |
| C1914 | daiin anti-correlates with thermal complexity (rho=-0.324, p=0.0004) |
| C1915 | AZC daiin-aiin co-occurrence attraction (OR=5.04, p=0.003) |
| C1916 | Section-conditioned family composition (A p=0.003, B p<0.0001) |

**Interpretive meaning:** aiin = "yield through repeated cycling into containment" = the basic distillation operation. The notation enforces that ii-tokens always resolve safely (n-terminal lock). Two safety pathways: ii for a-domain (yield), ee for e-domain (cooling).

Scripts: `phases/AIIN_CROSS_SYSTEM/scripts/s1-s5`

### Phase 633: Folio Design Freedom Decomposition (C1917-C1924)

Decomposed within-section B folio differentiation at atom resolution. Probe found 75% within-section variance; phase reconciled this with C1169's 27% AXM residual.

**Central finding:** 67% genuine atom freedom, orthogonal to AXM. REGIME constrains only head_k + pfx_qo (thermal intensity). Everything else is design freedom — the operational style choices that make each recipe unique.

**Key constraints:**
| C# | Finding |
|----|---------|
| C1917 | 67% genuine atom freedom, AXM captures <2% |
| C1918 | 11 effective dimensions at atom level (PC1=23.8% yield vs cooling) |
| C1919 | 4 FREEDOM features: mod_c, term_h, mod_d, mod_s (monitoring/closure cluster) |
| C1920 | REGIME decomposable but narrow (RF 85.4%, head_k+pfx_qo only) |
| C1921 | Freedom channels consistent cross-section (rho=0.783+) |
| C1922 | PREFIX+MOD drive ~60% of folio differentiation |
| C1923 | Atom-operational correlations (head_e↔e_ratio rho=0.816) |
| C1924 | Freedom in monitoring/closure clusters, not energy/iteration |

Scripts: `phases/FOLIO_DESIGN_FREEDOM/scripts/s1-s5`

### Exploratory Work (Not Formalized)

#### AZC Zodiac Atom Analysis (`phases/AZC_ATOM_SEASONAL/`)
- MOD atoms differ significantly across zodiac seasonal groups (C1908, registered in Phase 632)
- i/d swap = two distinct token families: aiin (yield-iterate-bind) vs ody (arrange-mark-end)
- e_depth gradient: Autumn 0.813 > Winter 0.515
- f57v R2 variant mapping: **negative** (p=0.34)
- 3 scripts, INDEX.md preserved

#### Currier A Atom Deep Dive (`phases/CURRIER_A_ATOMS/`)
- Confirmed A as materials property database at atom level
- e_depth: A=0.304 vs B=0.579 (A has almost no thermal modulation)
- 4 folio clusters by thermal complexity, section-associated (p=1.3e-07)
- Record opacity gradient: open semi-transparent, close opaque
- Cluster 1 (Pharma) entries contain thermal test protocol compounds (`cool.heat.adjust.watch`)
- Bridge MIDDLE A→B specificity: **negative** (p=1.0) — shared grammar, not cross-references
- Bridge HEAD-channel probe: real signal (e-HEAD rho=0.749) but **system-wide**, not folio-specific
- 7 scripts, INDEX.md preserved

#### f108r Crib Decode
- f108r → Ch16 (element separation from putrefied white composite)
- 4/4 aggregate predictions pass (high e_depth, cooling vocabulary, staging, early arrangement)
- BUT trajectory prediction failed (folio gets gentler, recipe says strengthen fire)
- Zero dar tokens (red flag — all confirmed matches have dar)
- Verdict: **inconclusive** — may be wrong match
- Script: `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/_full_decode_f108r.py`

#### Freedom Space + Crib Decode Connection
- Tested whether decoded recipe folios land at predicted positions in freedom space
- 2/4 predictions match (f75r term_h elevated, f84r mod_d elevated)
- f77v (furnace spec) signals through pfx_da (infrastructure prefix), not freedom features
- Small N (4 folios) limits conclusions but validates interpretive content
- Script: `phases/FOLIO_DESIGN_FREEDOM/scripts/s6_crib_decode_freedom_probe.py`

---

## Recipe-Folio Match Candidates (Untested)

From Phase 628 matching, confident matches not yet decoded:

| Folio | PL Chapter | Content | CV% | Priority |
|-------|-----------|---------|-----|----------|
| **f83r** | Ch9 (Practica) | Grinding D+C, distillation | 37% | Medium |
| **f84v** | Ch24 (Mercuriorum) | Sixth water constitution | 57% | High (verso of decoded f84r) |
| **f112r** | Ch11 (Mercuriorum) | Red mercury tincture creation | 71% | High |
| **f81v** | Ch18 (Mercuriorum) | Potable water composition | 67% | Medium |

Plus 3 untested **Codicillus** candidates: f79r, f79v, f80r

---

## Key Interpretive Insights From This Session

1. **aiin = distillation cycle.** The most common word in the manuscript encodes its most common operation: "yield through repeated cycling into containment." The notation enforces safety — you cannot compose an unsafe iteration token.

2. **A is a practitioner's reference.** A entries describe material thermal properties. B recipes are complete programs. The practitioner consults A to know HOW to handle materials (balneum mariae vs direct flame), not to modify B's program.

3. **Recipe individuality = monitoring style.** REGIME constrains thermal intensity. What makes each recipe unique is how much monitoring, adjustment, staging, and sequencing it requires — the FREEDOM features.

4. **Two safety pathways.** ii (in a-domain) locks to n-terminal (containment). ee (in e-domain) routes to y-terminal (closure). Construction-layer — baked into the morphology.

---

## Pending Work

- **dar/dal document type constraint** — still unregistered from earlier session
- **Atom gloss refinements** — r→receive, d→close, n→hold, l→level need cross-folio validation
- **More recipe decodes** — f84v, f112r, f81v are the best untested candidates
- **Codicillus recipe matching** — f79r, f79v, f80r never tested
- **chekar prediction** — f33r, f34r, f94r, f95r1 should describe water-bath procedures (falsifiable)

---

## Critical Files

| File | What |
|------|------|
| `scripts/voynich.py` | Core library with atomize(), Transcript, Morphology |
| `context/CLAIMS/INDEX.md` | 1924 constraints, v6.06 |
| `phases/AIIN_CROSS_SYSTEM/` | Phase 632 (5 scripts, results) |
| `phases/FOLIO_DESIGN_FREEDOM/` | Phase 633 (5+1 scripts, results, CSVs) |
| `phases/AZC_ATOM_SEASONAL/` | Exploratory AZC work (3 scripts) |
| `phases/CURRIER_A_ATOMS/` | Exploratory A work (7 scripts) |
| `sources/pseudo_lull_testamentum/` | PL text (English + Latin) |
| `sources/codicillus/` | Codicillus transcription + translation |

---

## Git Notes

- 18 commits ahead of origin/master
- `sources/codicillus/about.txt` is untracked (minor)
- Expert-advisor agent regenerated but needs Claude Code restart to take effect
- Push pending to both gitea (origin/master) and github (github/main)
