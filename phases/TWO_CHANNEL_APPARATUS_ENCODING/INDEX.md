# Phase 616: Two-Channel Apparatus Encoding Test

**Status:** COMPLETE
**Verdict:** DEPLOYMENT_DOMINANT
**Constraints:** C1799-C1805
**Date:** 2026-03-20

---

## Research Question

C1709 showed PP MIDDLE composition predicts apparatus manifold (Mantel r=0.423). C1796 showed paragraph shape vectors predict apparatus manifold (Mantel r=0.314). These use completely different feature spaces — vocabulary identity (WHAT MIDDLEs) vs deployment architecture (HOW arranged into paragraphs). Are they redundant or complementary?

## Blocking Tests

| Test | Description | Metric | Result | Verdict |
|------|-------------|--------|--------|---------|
| T1 | Vocab → Manifold | r=0.257, partial\|section r=0.204 | Significant, weaker than C1709 A-side | PASS |
| T2 | Shape → Manifold | r=0.317, partial\|section r=0.287 | Replicates C1796 | PASS |
| T3 | Vocab ↔ Shape independence | r=0.289 | PARTIAL_OVERLAP (0.20-0.40) | PARTIAL |
| T3b | PREFIX confound | vocab r=0.581, shape r=0.395 | Vocab heavily PREFIX-influenced | FLAG |
| T4 | Combined (alpha=0.5) | r=0.358, improvement +0.040 | Below +0.05 threshold | FAIL |
| T4-null | Permutation null | frac=0.002 | Improvement real, not random | PASS |
| T5 | Shape \| vocab | partial r=0.263 | Shape adds beyond vocab | PASS |
| T6 | Vocab \| shape | partial r=0.182 | Vocab adds beyond shape | PASS |
| T7 | Bridge-only vocab | r=0.257 | Bridge ≈ dark in B-space | INFO |
| T8 | Dark-only vocab | r=0.267 | Dark ≥ bridge (opposite of A-side) | INFO |
| T9 | Reduced shape \| vocab | partial r=0.157 | Structural deployment adds | PASS |
| T10a | Vocab \| section | partial r=0.204 (79.4% retention) | Not section-driven | PASS |
| T10b | Shape \| section | partial r=0.287 (90.4% retention) | Not section-driven | PASS |
| T10c | Combined \| section | partial r=0.312 (87.2% retention) | Not section-driven | PASS |
| T10d | Within-Herbal | vocab r=0.146 ns, shape r=0.347** | Shape dominates within-section | PASS |
| T11a | Vocab \| PREFIX | partial r=-0.028 | **Vocab completely absorbed** | CRITICAL |
| T11b | Shape \| PREFIX | partial r=0.160 | Shape retains half its signal | PASS |
| T11c | Vocab \| (PREFIX+shape) | partial r=-0.041 | Vocab has zero independent info | CRITICAL |
| T11d | Shape \| (PREFIX+vocab) | partial r=0.163 | **Shape survives everything** | CRITICAL |
| T11e | PREFIX → Manifold | r=0.476, partial\|section r=0.437 | Strongest single predictor | CRITICAL |
| T11f | Within-Herbal PREFIX mediation | shape\|PREFIX r=0.337, vocab\|PREFIX r=0.098 | Pattern replicates | PASS |

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `scripts/two_channel_encoding_test.py` | ~45s | `results/two_channel_encoding_results.json` |

## Key Findings

- **Vocabulary absorbed by PREFIX (C1799):** B-folio MIDDLE vocabulary distance is entirely mediated by PREFIX composition. Controlling for PREFIX drops vocab→manifold from r=0.257 to r=-0.028 (complete absorption). The MIDDLEs a folio uses are determined by its PREFIX distribution.
- **Shape carries independent deployment signal (C1800):** Paragraph shape vector survives control for both PREFIX and vocabulary (partial r=0.163, z=8.43). Half the raw signal (0.317→0.163) persists after removing everything vocabulary and PREFIX can explain. How paragraphs deploy MIDDLEs is informationally distinct from which MIDDLEs they use.
- **PREFIX is the powerhouse predictor (C1801):** PREFIX composition→manifold r=0.476, the strongest single predictor in the manifold family. Stronger than vocabulary (r=0.257), shape (r=0.317), or their combination (r=0.358). Survives section control (partial r=0.437).
- **Combined improvement real but modest (C1802):** Combining vocab+shape yields r=0.358 at alpha=0.5, a +0.040 improvement over shape alone. This is statistically real (T4-null p=0.002) but below the pre-registered +0.05 complementary threshold.
- **Asymmetric partial Mantels (C1803):** Shape adds substantially beyond vocabulary (partial r=0.263) but vocabulary's addition beyond shape (r=0.182) is entirely PREFIX-mediated — it vanishes to r=-0.041 when PREFIX is controlled.
- **Within-Herbal deployment dominance (C1804):** Within Herbal section (n=27), shape|PREFIX r=0.337 (highly significant), vocab|PREFIX r=0.098 (barely significant). The deployment signal operates within-section; vocabulary does not.
- **Section retention strong (C1805):** All channels retain 79-90% of signal after section control. This is not a section proxy.

## Verdict Rationale

DEPLOYMENT_DOMINANT, not COMPLEMENTARY or REDUNDANT:
- The "two channels" (vocabulary vs shape) appeared partially overlapping (T3 r=0.289) with both contributing (T5, T6 pass).
- But PREFIX mediation analysis reveals the overlap is PREFIX-driven: vocabulary is a downstream readout of PREFIX composition, not an independent channel.
- The true encoding hierarchy is: PREFIX composition (r=0.476) → vocabulary selection (absorbed) + deployment architecture (r=0.163 independent).
- The manuscript encodes apparatus identity through PREFIX gating plus an independent paragraph deployment channel.

## Dependencies

- Phase 580 (apparatus manifold, 5 PCs)
- Phase 589 (C1709, PP→manifold A-side)
- Phase 615 (C1796, paragraph shape→manifold)
- C121 (49 grammar classes, classified MIDDLEs filter)
- C1405-C1431 (PREFIX composition constraints)
