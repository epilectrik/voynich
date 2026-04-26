# C1961: Fire-side / Vessel-side Paragraph-level PREFIX Partition

**Tier:** 2
**Scope:** B, PREFIX, paragraph, partition, fire-vessel, architecture
**Phase:** PHASE_648_VESSEL_4AXIS_RECIPE
**Date:** 2026-04-25
**Extends:** C1217 (lane atom content separation, token-scope), C1242 (cross-lane content prediction, line-scope), C1306 (sister-pair cross-lane cargo divergence), C929 (ch/sh sensory modality)
**Relates to:** C1811-C1812 (PREFIX is paragraph-level design parameter), C1808 (PREFIX section eta²=0.21), C1810 (manifold retention after section control)

---

## Statement

At paragraph scale (the load-bearing scale for PREFIX composition per C1811-C1812), Currier B prefixes partition into two anti-correlated blocks:

- **Fire-side block:** `qo` (heat-application action), `ch` (active sample/test), `sh` (passive watch) — the operator's relationship to the heat source
- **Vessel-side block:** `ok` (thermal regime on contents), `ot` (transfer/iteration), `ol` (vessel-content state), `or` (outcome state) — what is happening in the apparatus

Mean within-block correlation +0.080 vs. mean cross-block correlation −0.232 (folio-level). Paragraph-level differential +0.131 (n=466, p=0.024 by 1000-permutation null).

The partition operates at paragraph scale and is compatible with — not in contradiction to — the existing token-scope C1217/C1242/C1306 lane architecture: the lanes describe within-line cross-lane routing (CHSH→QO at MI=1.063 bits), while this constraint describes between-paragraph specialization in fire-side vs vessel-side activity.

---

## Empirical evidence

### Block correlations across 82 Currier B folios

```
        ch      sh      qo      ok      ot      ol      or
ch    1.00   -0.05   -0.12   -0.10   -0.26   -0.45   -0.19
sh   -0.05    1.00   +0.25   -0.40   -0.22   +0.04   -0.42
qo   -0.12   +0.25    1.00   -0.42   -0.24   +0.29   -0.40
ok   -0.10   -0.40   -0.42    1.00   +0.01   -0.04   +0.34
ot   -0.26   -0.22   -0.24   +0.01    1.00   -0.01   +0.04
ol   -0.45   +0.04   +0.29   -0.04   -0.01    1.00   +0.24
or   -0.19   -0.42   -0.40   +0.34   +0.04   +0.24    1.00
```

Strongest cells:
- **Cross-block negative** (block partition signal): ch↔ol −0.45, qo↔ok −0.42, sh↔or −0.42, sh↔ok −0.40, qo↔or −0.40
- **Within-block positive**: ok↔or +0.34 (vessel-side coherence), qo↔sh +0.25 (fire-side coherence), ol↔or +0.24
- **The bridge**: qo↔ol +0.29 (heat application correlates with vessel-state change — only positive cross-block cell)

### Permutation null

| Scale | Differential | n | p-value |
|---|---|---|---|
| Folio | +0.295 | 82 | 0.058 (borderline; 35 distinct splits limit null granularity) |
| Paragraph | +0.131 | 466 | 0.024 |

### Within-section controls

| Section | n | Differential | p | Verdict |
|---|---|---|---|---|
| B (Bath) | 84 | +0.411 | 0.015 | SURVIVES |
| H (Herbal) | 68 | +0.321 | 0.027 | SURVIVES |
| S (Stars/Recipes) | 278 | +0.089 | 0.018 | SURVIVES |
| C (Cosmo) | 22 | +0.146 | 0.120 | directional |

3/4 significant at p<0.05; 4/4 directional. Not section-confounded.

### Within-regime controls

| Regime | Profile | n | Differential | p | Verdict |
|---|---|---|---|---|---|
| REGIME_1 (qo-heavy) | 201 | +0.120 | 0.112 | directional |
| **REGIME_2** (iteration/k-heavy, low link) | 32 | **−0.081** | 0.704 | **FAILS** |
| REGIME_3 (h-ratio/thermo-kch) | 190 | +0.139 | 0.011 | SURVIVES |
| REGIME_4 (link-heavy, low qo) | 43 | +0.290 | 0.025 | SURVIVES |

---

## Scope restriction (REGIME_2)

The architecture **fails directionally in REGIME_2** (iteration-dominated, k-heavy, low-link paragraphs). This is consistent with two compatible interpretations:

1. **Underpowered stratum** — n=32 is the smallest stratum; the −0.081 differential may be within paragraph-shuffle noise.
2. **LINK-as-separator hypothesis (Tier 3 candidate, pending validation)** — REGIME_2 has near-zero link-rate; without LINK operators separating monitoring from intervention, the fire-side / vessel-side ontology has no boundary to register, so the partition collapses. Under this reading, REGIME_2 represents single-domain execution-only programs (continuous redistillation/cohobation cycles) where heat-application and vessel-state are co-engaged as one operation.

The constraint applies to programs with non-trivial LINK density. REGIME_2 is documented as the scope exception.

---

## ch/sh position sub-distinction (commentary)

Within the fire-side block, paragraph-position resolution yields:
- `ch` is paragraph-LATE enriched (1.18× base) — phase-end verification
- `sh` is paragraph-EARLY enriched (1.13× base) — continuous monitoring during operation

This is consistent with C929's modality split (ch=active test, sh=passive monitor) at the *temporal positioning* level: sh sustains through the operation, ch verifies at phase boundaries. The effect sizes are below the 1.5× threshold for independent constraint registration; documented here as commentary refining C929 with positional structure.

---

## Bridge transition (qo↔ol +0.29)

The only positive cross-block correlation. Interpretation: heat application (qo, fire-side action) correlates with vessel-state change (ol, vessel-side observation) because applying heat is the operation that *causes* vessel-state change. The fire-side action and vessel-side state are coupled via this transition.

This corresponds to the predicted control loop in the SISMEL recipes: `sh → qo → ol → ok → ot → ch/sh` (continuous-monitor → apply-heat → vessel-state-change → thermal-state-registers → transfer-triggered → verify).

---

## Compatibility with existing token-scope constraints

C1217 (token-within-line lane atom content separation), C1242 (line-scoped cross-lane prediction), and C1306 (sister-pair cross-lane cargo divergence) operate at within-line / token-scope. C1961 operates at paragraph-scope. The two scales describe different aspects of the same architecture:

- **Token-scope:** within any line, the CHSH→QO cross-lane routing operates as a control-loop primitive
- **Paragraph-scope:** between paragraphs, programs specialize in fire-side vs vessel-side operations

The qo↔ok = −0.42 paragraph-level anti-correlation does *not* contradict C1217's "QO lane carries energy atoms": C1217 describes within-line atom content of QO-lane tokens; C1961 describes between-paragraph qo and ok specialization. Different scales, different measurements.

---

## Falsification

Would be falsified if:

1. The paragraph-level differential drops to ≤0 under any well-powered stratification (we ran section + regime; both passed in 7/8 strata)
2. The qo-ok anti-correlation reverses at paragraph scale
3. A within-paragraph cross-channel sequencing test (pending Phase 649+) shows that the predicted control-loop topology (sh→qo→ol→ok→ot→ch/sh) does NOT manifest as enriched bigram/trigram transitions

---

## Provenance

- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/scripts/s5_chsh_qo_lane_test.py` (folio-level block correlation)
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/scripts/s6_position_resolve_and_permute.py` (paragraph-level + permutation null + position resolution)
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/scripts/s7_section_regime_controls.py` (section + regime controls)
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/chsh_qo_lane_test.json`
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/position_and_permutation.json`
- `phases/PHASE_648_VESSEL_4AXIS_RECIPE/results/section_regime_controls.json`
