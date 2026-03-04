# C1388: o-Atom Arrangement Domain Marker

**Tier:** 2
**Scope:** B
**Phase:** O_ATOM_SEMANTIC_DEEP_DIVE (Phase 498)
**Depends on:** C1195 (atom gloss tiers), C874 (ol=LINK operator), C1207 (k-o anti-correlation), C1381 (o-initial AZC enrichment), C1384 (k-initial AXM dwell), C1386 (ACTOR/RESPONDER timing split), C1190 (MIDDLE additive composition), C1305 (MIDDLE determines category)

## Constraint

Atom o = "arrange" (German: ordnen) is a STAGING domain marker. It tags the arrangement/organizational domain of operations, distinct from thermal (k), cooling (e), or monitoring (h) domains. Evidence from three independent test batteries (23 total tests):

### Core behavioral profile
1. **Category signature**: STAGING 2.49x (#1 enriched), OPERATION 1.78x; THERMAL 0.105x (most extreme single-category depletion of any atom).
2. **Anti-AXM**: #1 anti-AXM atom among all 20 atoms (folio-level rho=-0.614). Higher o-density correlates with lower AXM self-transition (sustained heating dwell). Folio-level rho=-0.431 (rank #2, p=0.000014).
3. **Kernel interleaving**: #1 NEUTRAL kernel interleaver (between-kernel 52.1%), exceeding all RESPONDER atoms. o positions between kernel operations (k/e/h) without being a kernel atom itself.
4. **Macro-state**: AXM depleted (0.719x, p<0.01), FQ enriched (1.209x, p<0.01).

### Convergent evidence (justifies SOLID)
5. **C874 convergence**: ol was independently established as the LINK operator (C874) from pure positional/structural analysis (position 0.489, 96.7% paragraph-interior, monitoring/intervention boundary). Compositional decomposition independently yields o(arrange)+l(state) = "arrange the state" = 100% STAGING at 7.68x enrichment. Two methods, zero shared assumptions, same functional conclusion.
6. **100% compound determinism**: Each o+X compound maps to a DIFFERENT category at 100% purity — ol=STAGING (762 tokens), ok=CONTAINMENT (70 tokens), or=FLOW (446 tokens), ot=MONITORING (46 tokens). The second atom determines which category; o provides the common arrangement frame. Contrast: al=100% FLOW vs ol=100% STAGING — same l, different first atom → completely different category. The first atom carries independent semantic content (C1190).

### Additional evidence
7. **CHSH+o STAGING enrichment**: 4.77x enrichment (#1 enriched category) — checkpoint/monitoring prefix + o-MIDDLE = staging operations.
8. **AZC gradient**: o-initial section gradient tracks TRANSITION (rho=+0.829), not CONTAINMENT (|rho|=0.14). Control: k-initial tracks THERMAL at rho=+0.943.
9. **o-terminal redirect**: TRANSITION 3.08x (o-terminal compounds shift toward state transitions).

### What was falsified
- **CONTAINMENT prediction** (vessel/Ofen): o does not map to CONTAINMENT (enrichment 0.835x). The "vessel" hypothesis in its container-property form is falsified.
- **Temporal ordering** (prepare-then-act): o does NOT precede k within lines (48.6%, chance level). o→k forward bigram shows no enrichment (0.972x). o is a domain marker, not a sequential action verb.
- **Cycling correlation**: o-density does not predict paragraph mode cycling (rho=-0.107, rank #14/20).

## Test Batteries

| Battery | Tests | Pass | Hypothesis |
|---------|-------|------|-----------|
| Phase 498 (vessel) | 12 | 3 | o=Ofen, CONTAINMENT predicted |
| Phase 498b (ordnen) | 8 | 4 | o=ordnen, STAGING predicted |
| Tiebreakers | 3 | 1 | Temporal ordering, ol composition, forward bigram |
| **Total** | **23** | **8** | |

## Gloss

o = "arrange" (ordnen, German: to arrange, to put in order). Domain marker for the staging/arrangement operational domain. Not a temporal action verb — tags WHAT domain an operation belongs to, not WHEN it happens. German etymology consistent with existing pattern: K=Kochen, E=Erkalten, D=Dichten, T=Treiben, O=Ordnen.

Compound readings: ol = arrange+state (STAGING/LINK), ok = arrange+heat (CONTAINMENT via apparatus setup), ot = arrange+transfer (MONITORING), or = arrange+respond (FLOW), od = arrange+mark (MARKING).

## Falsification

Would be falsified if: (1) ol loses its 100% STAGING purity, or (2) the al vs ol category contrast (FLOW vs STAGING) disappears, or (3) o-initial tokens show AXM enrichment rather than depletion.

## Provenance

- `phases/O_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_o01_*.py` through `p_o23_*.py` — 23 prediction scripts
- `phases/O_ATOM_SEMANTIC_DEEP_DIVE/results/o_atom_prediction_results.json` — structured results
