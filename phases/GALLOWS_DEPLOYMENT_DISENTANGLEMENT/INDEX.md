# Phase 612: GALLOWS_DEPLOYMENT_DISENTANGLEMENT

**Status:** COMPLETE
**Verdict:** VARIANCE_ABSORBED
**Constraints:** C1778-C1781
**Scripts:** `scripts/gallows_disentangle.py` (~4s)

## Motivation

Phase 611 established that gallows are real and context-sensitive (C1772-C1777): they bias body composition, show asymmetric atom-substrate inheritance, and correlate with ambient operational context. Phase 612 is the closure phase, asking whether gallows contribute unique deployment-posture information beyond block position, paragraph archetype, and ambient context, or whether they are fully reducible to those layers.

Four overlapping explanations remained:

- **A:** Gallows are block-position markers (C865, C1321, C1323)
- **B:** Gallows are context-sensitive deployment headers (C1772-C1777)
- **C:** Gallows echo atom-family behavior (C866, C521, C1773-C1774)
- **D:** Gallows co-vary with paragraph archetype (section-mediated per C1776)

## Method

Consolidated analysis across 572 gallows-initial paragraphs (k=35, t=230, p=287, f=20) spanning 4 sections. Five test blocks:

- **T1.** Incremental variance partition (nested sequential SS, 6-level hierarchy, 200-permutation null, mediation comparison)
- **T2.** Header vs body signal decay (3-zone atom fractions, Cramer's V per zone)
- **T3.** Within-archetype gallows effects (GMM K=5, thermal context control via median split)
- **T4.** Hierarchical model comparison (4-way flat, 2-axis factorized, flat opener/mode)
- **T5.** Section stability under bootstrap (200 resamples, cosine similarity to global)

## Results Summary

### T1: Incremental Variance Partition
- **Forward hierarchy:** section 8.9% → folio|section 27.8% → position|folio 0.0% → archetype|position 21.2% → context|archetype 27.6% → **gallows|context 6.7%** → residual 7.8%
- **Permutation null:** null_mean=7.2%, z=-0.61, **p_perm=0.73 — NULL**
- **Reverse hierarchy:** gallows alone captures 0.8% (gross), vs 6.7% (net after controls)
- **Mediation:** R²_context=0.069, R²_context+gallows=0.075, delta=0.006 — negligible
- **Interpretation:** The 6.7% apparent gallows variance is within permutation null bounds. Gallows do not add unique variance after full controls.

### T2: Header vs Body Signal Decay
- **Z1 (gallows token):** V=0.238, p<10⁻⁶ (n=1,319 atoms)
- **Z2 (first-line residual):** V=0.059, p<10⁻⁷ (n=12,072 atoms; confounded with generic first-line specification effects per C1426/C1729)
- **Z3 (body lines 2+):** V=0.046, p<10⁻⁶ (n=34,843 atoms)
- **Attenuation ratio:** Z3/Z1 = 0.191
- **Interpretation:** Body signal exists and is highly significant, but ~81% of gallows compositional effect is confined to the header zone.

### T3: Within-Archetype Effects
- **A0 (n=22):** V=0.113, p=0.108 (null)
- **A1 (n=362):** V=0.035, p<0.0001; p self-enrichment 1.38; survives thermal control (hi=1.42, lo=1.36)
- **A2 (n=100):** V=0.076, p<0.0001; p self-enrichment 1.46; survives thermal control (hi=2.71, lo=1.43)
- **A3 (n=16):** insufficient data
- **A4 (n=72):** V=0.144, p=0.002; p self-enrichment 3.59; survives thermal control (hi=6.21, lo=2.42)
- **Interpretation:** 3/4 testable archetypes show significant gallows effects surviving simple thermal context control. However, T1 full controls absorb all gallows variance — the within-archetype effects are section/folio-mediated, not archetype-orthogonal.

### T4: Hierarchical Model Comparison
- **M1 (4-way flat):** R²=0.00823, V=0.039, 27 dof
- **M2 (2-axis factored):** R²=0.00823 (identical — trivially same categories, different structure)
- **M3 (opener/mode):** R²=0.00292, V=0.041, 9 dof — **captures 35.5% of M1**
- **Within k vs f:** V=0.102, p<10⁻⁶ (n=55; low power caveat)
- **Within p vs t:** V=0.041, p<10⁻⁶ (n=517)
- **Positional split:** opener mean position=0.355, mode mean=0.527, MW p=0.0003
- **Interpretation:** The opener/mode axis is the dominant but insufficient split — it captures only 35.5% of 4-way variance. Within-family contrasts (k vs f, p vs t) carry the remaining 64.5%. The 4-gallows system is irreducibly 4-way.

### T5: Section Stability Under Bootstrap
- **Cosine to global:** Bio=0.455, Cosmo=0.809, Herbal=0.817, Stars=0.746
- **Bootstrap 90% CIs:** all wide (lower bounds 0.15-0.30, upper bounds 0.90-0.91)
- **Cross-section cosines:** Bio-Herbal=0.233, Bio-Cosmo=0.307, Bio-Stars=0.895, Cosmo-Herbal=0.718, Cosmo-Stars=0.485, Herbal-Stars=0.436
- **Interpretation:** Bio is notably divergent from global and from Herbal (cos=0.233). Stars-Bio alignment is high (0.895). Posture direction changes across sections — not amplitude-only variation.

## Findings

### F1: Gallows carry no unique variance after full controls
All gallows body-ecology effects are absorbed by the control hierarchy (section → folio → block position → archetype → ambient context). The 6.7% apparent gallows SS share falls within the permutation null (mean=7.2%, z=-0.61, p=0.73). Mediation delta R²=0.006. Gallows do not contribute unique body-ecology information beyond the modeled contextual hierarchy.

### F2: Gallows signal attenuates from header to body
The gallows-body association exists (V_Z3=0.046, p<10⁻⁶) but is 81% confined to the header zone (V_Z1=0.238). Gallows are primarily header-specification markers with attenuated body echo. The body signal is real but is mediated by the same upstream context that selects both gallows type and body composition.

### F3: The four-gallows system is irreducibly 4-way
The opener/mode split (k/f vs p/t) captures a genuine positional axis (openers earlier, p=0.0003) but only 35.5% of body-ecology variance. Within-family contrasts (k vs f: V=0.102; p vs t: V=0.041) carry real information. The system cannot be collapsed to a 2-way split.

### F4: Posture directions are section-conditional
Section-to-global cosines range from 0.455 (Bio) to 0.817 (Herbal). Cross-section cosines reach as low as 0.233 (Bio-Herbal). Bootstrap CIs are wide (all lower bounds below 0.30). The posture system is not universal with amplitude tuning — section alters the structure of the gallows-body relationship.

## Constraints

### C1778: Gallows Variance Absorption
**Tier 2 | Scope: B_paragraph, gallows, disentanglement**

Gallows type does not contribute unique variance to paragraph body atom ecology after sequential control for section, folio (within section), block position (within folio), paragraph archetype (within position), and ambient context (within archetype). Forward sequential SS: gallows|context = 6.72% of total, but permutation null (200 shuffles within section) gives mean=7.16%, z=-0.61, p_perm=0.73. Mediation test: adding gallows to a context-only body-prediction model improves R² by 0.006 (from 0.069 to 0.075). Within-archetype effects (significant in 3/4 archetypes under simple thermal control) are absorbed by the full control hierarchy, indicating section/folio mediation. Gallows do not contribute unique body-ecology variance beyond the modeled contextual hierarchy; they function primarily as explicit paragraph-header labels of deployment context.

### C1779: Gallows Header-Body Signal Attenuation
**Tier 2 | Scope: B_paragraph, gallows, header, body**

Gallows-body atom association attenuates across paragraph zones. Zone 1 (gallows-initial token): Cramer's V=0.238 (p<10⁻⁶, n=1,319 body atoms). Zone 2 (first-line residual): V=0.059 (p<10⁻⁷, n=12,072; confounded with generic first-line specification effects per C1426/C1729). Zone 3 (body lines 2+): V=0.046 (p<10⁻⁶, n=34,843). Attenuation ratio Z3/Z1=0.191. Gallows are primarily header-specification markers; ~81% of the compositional effect is confined to the header zone. The body signal is real but is a residual echo of the header declaration, not a separate body-conditioning channel.

### C1780: Gallows Irreducible Four-Type Architecture
**Tier 2 | Scope: B_paragraph, gallows, architecture**

The four-gallows system (k/t/p/f) is not reducible to a simple opener/mode binary split. The opener/mode axis (k/f vs p/t) captures a genuine positional signature (opener mean folio position=0.355, mode=0.527, MW p=0.0003) but only 35.5% of body-ecology variance (R²=0.00292 of 0.00823 total). Within-family contrasts carry the remaining 64.5%: k vs f (V=0.102, p<10⁻⁶, n=55; low-power caveat) and p vs t (V=0.041, p<10⁻⁶, n=517). The positional and compositional axes are partially independent. The system requires all four types to describe its full behavior.

### C1781: Gallows Section-Conditional Posture
**Tier 2 | Scope: B_paragraph, gallows, section, stability**

The gallows posture system (p-gallows body O/E vectors) varies across sections in direction, not just amplitude. Section-to-global cosine similarities: Bio=0.455, Cosmo=0.809, Herbal=0.817, Stars=0.746. Cross-section cosines reach as low as 0.233 (Bio vs Herbal). Bootstrap 90% CIs (200 resamples) are wide: all lower bounds below 0.30. Bio shows the strongest divergence from the global posture pattern. Stars-Bio alignment (0.895) contrasts with Bio-Herbal (0.233) and Herbal-Stars (0.436). The posture system is section-conditional and non-universal: section does not merely scale gallows effects but alters their direction in atom-composition space. Wide bootstrap CIs warrant caution about the precision of section-specific posture geometry.

## Tier 3 Synthesis

Gallows are explicit paragraph-header labels of deployment context. Their strong header-local signal (V=0.238) and weak body echo (V=0.046) show that they primarily mark contextual paragraph posture at entry. They do not add independent body-ecology variance beyond section, folio, block position, paragraph archetype, and ambient context. The labeling system is irreducibly four-way and section-conditional.

Both gallows type and body atom composition are determined by the shared upstream context (section identity, folio position, paragraph archetype, ambient operational state). Gallows declare the label; the body implements the content. Neither controls the other — both are driven by the same contextual state. This means the Phase 611 body-ecology correlations (C1772-C1777) are real patterns but mediated echoes, not independently generated by gallows labels themselves: p labels contexts whose bodies are already p-like; k labels contexts whose handling is e-biased.

Gallows are explanatorily redundant with the contextual state but operationally real — they are the manuscript's actual encoding interface for paragraph posture at entry, analogous to a packet type tag or mode bit. This distinction (explanatory redundancy ≠ structural irrelevance) is the final resolution of the gallows layer.

## Observations Preserved (Not Registered as Tier 2)

- **Within-archetype p self-enrichment:** Survives simple thermal control in archetypes A1 (O/E=1.38), A2 (1.46), A4 (3.59), but absorbed by full control hierarchy. The within-archetype effects are real patterns but section/folio-mediated, not gallows-independent.
- **Archetype A4 anomaly:** p self-enrichment O/E=3.59 (and 6.21 in high-thermal context) is strikingly high. A4 may represent a specialized deployment context where p-gallows is nearly obligatory. Too sparse (n=72) for robust standalone analysis.
- **Bio section divergence:** Cosine to global = 0.455, to Herbal = 0.233. Bio's posture vector is qualitatively different from other sections. May reflect distinct Bio section operational requirements. Absorbed by C1781 section-conditional finding.

## Output Files

| File | Description |
|------|-------------|
| `results/gallows_disentangle_results.json` | Full test statistics, O/E vectors, constraint evidence |
| `scripts/gallows_disentangle.py` | Consolidated analysis (5 test blocks T1-T5) |

## Related Constraints

C865 (gallows front bias), C866 (gallows morphological patterns), C1321 (within-block ordering), C1322 (content-label independence), C1323 (cross-block restart), C1426 (first-line specification), C1729 (first-line enrichment), C1772 (gallows-body composition), C1773 (p direct continuity), C1774 (k complementary e-bias), C1775 (ambient-context deployment), C1776 (gallows-archetype non-reducibility), C1777 (atom-substrate asymmetry).
