# Phase 631: Dark Pipeline PREFIX Domain Locking & Identification Architecture

**Status:** COMPLETE
**Verdict:** DOMAIN_LOCKING_CONFIRMED
**Constraints:** C1901-C1907

---

## Research Question

Do dark pipeline MIDDLEs carry token-level identity that constrains their PREFIX deployment, and how does the A registry treat dark MIDDLEs relative to bridge MIDDLEs?

## Background

Phase 630 (C1897-C1900) discovered during f75r atom-level decoding that dark pipeline tokens appeared at recipe-contextually appropriate positions. This motivated investigation of whether dark MIDDLEs carry structural identity beyond generic identification markers (C1137, C1505). Existing constraints established dark pipeline as 300 unmatched PP MIDDLEs (C1135), 100% HT/UN substrate (C1137), with modified construction grammar (C1138), bridge-disjoint (C1139), and section-hyper-modulated (C1148).

## Novel Contribution

1. Dark MIDDLEs actively SELECT into specific PREFIX channels in B, diverging from host folio baselines (T4a)
2. The same PREFIX domain locking operates in A's registry system (T4/A-side)
3. Dark MIDDLEs are a major derivational substrate for RI instance vocabulary (T1: 78% spawn RI)
4. PREFIX domain locking is HEAD-stratified: k-initial channels thermally, e-initial spreads, headless specifies
5. Dark atom compositions systematically match host section operational profiles

---

## Scripts

All in `phases/DARK_PIPELINE_ID/scripts/`:

| Script | What | Key Result |
|--------|------|------------|
| `t1_prefix_concentration.py` | Aggregate PREFIX entropy: dark vs bridge | FAIL — frequency artifact at aggregate level |
| `t1b_successor_profiles.py` | Dark MIDDLE successor discrimination | Mean JSD=0.483 — dark MIDDLEs route differently |
| `t2_dark_middle_recipe_sharing.py` | Cross-folio dark sharing vs recipe | Balneum sharing p<0.001 vs null but driven by section |
| `t3_dark_atom_section_match.py` | Dark atom profiles vs section grammar | r=0.649-0.924 per section |
| `t4_substance_signature_tests.py` | T4a/T4b/T4c: channel selection, atom similarity, individual concentration | T4a PASS, T4b mixed, T4c bridge wins |
| `t5_a_registry_test.py` | 5-test A-side battery: RI derivation, position, co-occurrence, PREFIX, sharing | 2 MATERIAL, 1 OPERATIONAL, 2 INCONCLUSIVE |
| `_f75r_dark_referents.py` | Exploratory: dark MIDDLEs on f75r vs Ch19 | 11 unique dark MIDDLEs, context analysis |

---

## Constraints

### C1901: Dark MIDDLEs select into PREFIX channels in B (Tier 2, extends C1138)

Individual dark pipeline MIDDLEs show PREFIX selection profiles that diverge from host folio baselines: cosine similarity 0.53-0.59 (tested on eet, ksh, lsh across 14-18 folios each). Categorical exclusions persist cross-folio: eet is 0% qo across 16 folios (vs 19.3% folio baseline), ksh is 0% sh/ch across 18 folios. This is MIDDLE-specific channel selection, not aggregate population bias. Extends C1138 (dark distinct construction grammar) from population-level to per-MIDDLE resolution.

- Scope: B, dark pipeline, PREFIX, C1138, C1356
- Metrics: cos_eet=0.532. cos_ksh=0.593. cos_lsh=0.552. eet_qo=0%. ksh_sh=0%. ksh_ch=0%.

### C1902: Dark MIDDLEs are PREFIX-affiliated in A registry (Tier 2, extends C1138)

Dark pipeline MIDDLEs show strong PREFIX affiliation in Currier A (Cramer's V=0.449, 64 qualifying MIDDLEs with 5+ A tokens). The same PREFIX domain locking observed in B (C1901) operates in A's non-sequential registry system. Dark MIDDLEs are domain-committed identification vocabulary, not freely deployable generic markers.

- Scope: A, dark pipeline, PREFIX, C1138, C1901
- Metrics: V=0.449. qualifying=64. n_tokens=600.

### C1903: 78% of dark MIDDLEs spawn RI instance derivatives (Tier 2, extends C913)

234 of 300 dark pipeline MIDDLEs serve as derivational bases for RI (registry-internal) tokens in Currier A, at 0.83x the bridge MIDDLE derivation rate. The dark pipeline is a major substrate for A's instance identification system (C913: RI = PP + extension). Three-level derivational chain: bridge atoms → dark compound MIDDLEs (C1141) → RI instance extensions.

- Scope: A, dark pipeline, RI, C913, C1141
- Metrics: dark_ri_base=234of300 (78.0%). bridge_ri_base=83of88 (94.3%). ratio=0.83x.

### C1904: Dark and bridge MIDDLEs are positionally identical in A (Tier 2)

Dark and bridge pipeline MIDDLEs occupy the same positional distribution within Currier A lines (cosine similarity 0.977, dark mean position 0.493 vs bridge 0.499). A's line-level organization does not distinguish pipeline membership — the bridge/dark partition is a cross-system property (A→B flow), not an intra-system property. Consistent with C234 (A is POSITION_FREE) and C1145 (dark/shared atoms occupy equivalent slots).

- Scope: A, dark pipeline, bridge, position, C234, C1145
- Metrics: cos=0.977. dark_mean_pos=0.493. bridge_mean_pos=0.499. n_dark=1007. n_bridge=9407.

### C1905: Dark MIDDLEs are LESS PREFIX-concentrated than bridge (Tier 2)

Individual dark pipeline MIDDLEs show lower PREFIX concentration than frequency-matched bridge MIDDLEs at every frequency band tested. Sign test significant (p=0.009, bridge direction: 47/92 bridge wins vs 26/92 dark wins). Dark MIDDLEs spread across MORE PREFIX channels than bridge MIDDLEs — consistent with identification vocabulary deployed across multiple operational contexts, as opposed to bridge MIDDLEs which are channel-specific operational primitives.

- Scope: B, dark pipeline, bridge, PREFIX, concentration
- Metrics: sign_p=0.009. bridge_wins=47of92. dark_wins=26of92. bands=5-10,10-20,20-50,50-100.

### C1906: Dark atom compositions match section grammar profiles (Tier 2, extends C1148)

Dark pipeline MIDDLE atom compositions correlate with the grammar HEAD atom profiles of their host sections: per-section r ranges from 0.378 (section C) to 0.924 (section B). Dark MIDDLEs in thermal-heavy sections contain more thermal atoms; dark MIDDLEs in staging-heavy sections contain more staging atoms. The dark pipeline's section hyper-modulation (C1148) operates through atom-level selection matching the section's operational character.

- Scope: B, GLOBAL, dark pipeline, section, atoms, C1148, C1176
- Metrics: r_B=0.924. r_S=0.719. r_H=0.649. r_T=0.747. r_C=0.378.

### C1907: Dark PREFIX domain locking is HEAD-stratified (Tier 2)

Dark pipeline PREFIX channeling varies systematically by HEAD atom: k-initial dark MIDDLEs channel 65-100% to qo (THERMAL), uniformly across all 7 qualifying k-initial darks. e-initial dark MIDDLEs show moderate spread (mean pairwise cosine 0.629) with extremes both ways (eet vs ees = 0.134, eet vs ekc = 0.991). Headless dark MIDDLEs (l-initial) route through specification PREFIXes (da/so/po) with 0% sh/ch. The HEAD atom determines whether a dark MIDDLE channels operationally (k: locked) or across identification contexts (headless: spread).

- Scope: B, dark pipeline, HEAD, PREFIX, C1475, C1500
- Metrics: k_init_qo=65-100%. e_init_mean_cos=0.629. n_k=7. n_e=21.

---

## Interpretive Summary (Tier 4, not constraints)

The structural findings support the interpretation that dark pipeline MIDDLEs function as **descriptive identification labels**: each dark MIDDLE names something by its operational properties (atom composition), is committed to a specific operational domain (PREFIX locking), and is cataloged by A's registry with instance-level derivatives (RI extensions). The atom composition narrows the property class of the referent (e.g., eet = something with deep-cooling-transfer properties); the PREFIX tells you which operational channel is verifying it; the specific referent is supplied by the operator's domain knowledge, not the notation.

This interpretation respects C171 (semantic ceiling) and C120 (PURE_OPERATIONAL): the manuscript describes HOW things behave operationally, not WHAT they are. The labels are readable as property descriptions but not as substance names without external reference texts.

See `context/SPECULATIVE/INTERPRETATION_SUMMARY.md` for full Tier 4 treatment.
