# Currier B Fit Registry

> **This document logs explanatory fits.**
> **No entry in this file constrains the model.**

**Version:** 1.4 | **Last Updated:** 2026-02-25 | **Fit Count:** 12

---

## Brunschwig Operational Control Fits

These fits map verified control mechanisms from Brunschwig's *Liber de arte distillandi* (1500) to Currier B structural features. All control mechanisms were verified against the original early modern German text (`sources/brunschwig_1500_text.txt`, Part 1, lines 1-2800). Only controls confirmed in the source text are included.

**WARNING:** These are FITs, not constraints. They show explanatory alignment between B's architecture and historical distillation practice. They do NOT define architectural necessity. The architecture permits these mappings but does not require them.

**Source verification date:** 2026-01-26

---

### F-B-001 - LINK Operator as Sustained Monitoring Interval

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C366, C609, C190

#### Question

Does the LINK operator's structural behavior align with Brunschwig's drop-rate monitoring technique — the primary feedback mechanism in historical distillation?

#### Brunschwig Evidence (verified)

Lines 2039-2042: "wie die glock ſchlecht eyns zwei das ein tropffen felt vnnd aber eyns zwei das ein tropffen felt vñ nit me / wan wo es hehender tropfen iſt / ſo wer das füer zů groß"

("as the clock strikes one-two and a drop falls, and again one-two and a drop falls and no more — because if it drops faster, the fire is too great")

This describes: sustained attention without physical action, occurring between interventions, where deviation from expected rate triggers transition to active control (adjust air holes).

#### Structural Properties of LINK (Tier 2)

| Property | LINK (C366, C609) | Drop-rate monitoring |
|----------|-------------------|---------------------|
| Operational status | Non-operational (no state change) | Non-operational (observe only) |
| Phase role | Boundary between monitoring and intervention | Boundary between "system OK" and "adjust fire" |
| Spatial distribution | Uniform within lines (C365) | Sustained, not positional |
| Control effort correlation | r = -0.7057 with CEI (C190) | More monitoring when system stable, less when intervening |
| Preceding context | AUXILIARY / FLOW tokens | Setup / flow establishment |
| Following context | HIGH_IMPACT / ENERGY tokens | Active intervention (air hole adjustment) |
| Token share | 13.2% of B tokens (C609) | ~1 in 8 operational moments is pure observation |

#### Result Details

All six structural properties of LINK have direct counterparts in the physical practice:

1. **Non-operational status** — LINK tokens produce no state change in the grammar; the operator counting drops produces no change in the apparatus. MATCH.
2. **Phase boundary** — LINK gates the grammar transition from passive to active control (C366); drop-rate deviation gates the physical transition from observation to intervention. MATCH.
3. **Uniformity** — LINK is spatially uniform within lines (not about specific positions); monitoring is temporally sustained (not about specific moments). MATCH.
4. **CEI anticorrelation** — More LINK = less intervention effort (C190, r=-0.7057); a stable drop rate means less fire adjustment needed. MATCH.
5. **Preceding context** — LINK follows setup/flow tokens; monitoring follows apparatus establishment. MATCH.
6. **Following context** — LINK precedes high-impact/energy tokens; deviation triggers active intervention. MATCH.

#### Interpretation

The LINK operator accounts for the structural role of sustained sensory monitoring in a control system. Its grammar-state transition function (gating passive-to-active control) is sufficient to explain why 13.2% of B tokens are non-operational: they represent the monitoring intervals between interventions. The LINK-CEI anticorrelation (r=-0.7057) accounts for why stable processes require more monitoring and less intervention — the physical reality of drop-rate watching.

#### Limitations

- LINK is generic — it does not specify *what* is being monitored. This fit maps LINK to drop-rate monitoring, but LINK could equally account for visual monitoring, olfactory checking, or any sustained attention activity.
- The 13.2% duty cycle is consistent with, but not diagnostic of, drop-rate counting specifically. Other monitoring patterns could produce similar token shares.
- The mapping is to the *structural role of monitoring*, not to the *specific physical sense employed*.

#### Relation to Constraints

- **Supports:** C366 (LINK phase boundary), C609 (LINK density), C190 (LINK-CEI anticorrelation)
- **Refines:** C190 (provides physical mechanism for the anticorrelation)
- **Introduces NEW constraints:** NO

---

### F-B-002 - QO Lane as Safe Energy Pathway

**Tier:** F3 | **Result:** SUCCESS | **Supports:** C601, C574, C600

#### Question

Does the QO execution lane's complete hazard exclusion align with Brunschwig's classification of the pelican as a no-fire distillation method, and more broadly with the distinction between safe and hazardous thermal pathways?

#### Brunschwig Evidence (verified)

Line 1799: "Alſo haſt du den vierdẽ modũ zů diſtillieren on füer" ("Thus you have the fourth method to distill WITHOUT fire")

The pelican uses horse dung warmth (lines 1753-1758), not direct fire. Brunschwig classifies it among the no-fire methods.

Lines 2042-2045 describe fire-based methods where excessive heat is dangerous and requires active air hole management — the hazardous pathway.

#### Structural Properties (Tier 2)

| Property | QO lane | Safe thermal pathway |
|----------|---------|---------------------|
| Hazard participation | 0/19 forbidden transitions (C601) | No direct fire = no fire hazard |
| Upstream trigger | CC_OL_D specifically activates QO (C600) | Dedicated entry point for safe method |
| Recovery association | 63-67% recovery routing | Safe pathway serves as recovery substrate |
| Grammar | Identical to CHSH (C574) | Same operations, different risk profile |
| Ordering | Second position (46.1% first, C579) | Applied after initial processing |

#### Result Details

1. **Hazard exclusion** — QO's 0/19 participation rate (C601) is exactly what a non-fire pathway predicts: remove the primary energy hazard source, and the pathway becomes inherently safe. MATCH.
2. **Dedicated trigger** — CC_OL_D (ol-derived compounds) specifically activates QO at 1.39x enrichment (C600), while CC_DAIIN/CC_OL activate CHSH. A distinct method (pelican vs fire-based) having a distinct entry trigger is architecturally expected. MATCH.
3. **Grammatical identity** — QO and CHSH follow identical grammar (C574): same positions, same REGIME patterns, same transition profiles. The same operational *logic* applies regardless of energy source — only the risk profile changes. MATCH.
4. **Recovery routing** — QO's association with recovery is consistent with safe pathways serving as the substrate for system stabilization. When things go wrong in the CHSH (fire) pathway, you return to QO (gentle/indirect) conditions. MATCH.
5. **Ordering** — CHSH-first (53.9%, C579) is consistent with active fire-based processing preceding gentler equilibration. MATCH.

#### Interpretation

The QO lane accounts for a safe energy pathway — one that achieves the same grammatical operations as the hazardous CHSH pathway but without exposure to forbidden transitions. This is sufficient to explain both the complete hazard exclusion (C601) and the grammatical convergence (C574): the two lanes do the same thing at different risk levels, consistent with fire-based vs non-fire thermal processing.

The broader interpretation is that EN's two-lane architecture accounts for a system where multiple energy sources of different risk profiles are available, routed by upstream control (CC sub-groups), and interleaved within execution (C577) based on operational context (section type).

#### Limitations

- QO is also enriched in REGIME_1 (balneum marie, indirect fire via water bath). The mapping is to "safe thermal pathway" broadly, not exclusively to "pelican = no fire." The physical referent may be indirect/gentle heating rather than absence of heating.
- C626 (Lane-Hazard MIDDLE Discrimination) shows the lanes do NOT predict hazard at the vocabulary level — hazard exclusion is a property of QO's class membership, not its MIDDLE content. This means the safety is grammatical, not lexical, which is consistent with a method-level distinction but complicates material-specific interpretations.
- The pelican in Brunschwig is a specific apparatus; QO is a general grammatical pathway. The mapping is one-to-many: QO could account for any safe energy method, not pelican specifically.

#### Relation to Constraints

- **Supports:** C601 (QO hazard exclusion), C574 (lane convergence), C600 (CC trigger selectivity)
- **Refines:** C601 (provides physical rationale for absolute exclusion)
- **Introduces NEW constraints:** NO

#### Post-Hoc Annotation (LANE_CHANGE_HOLD_ANALYSIS)

LANE_CHANGE_HOLD_ANALYSIS confirms QO tokens contain k-ENERGY_MODULATOR MIDDLEs at 70.7% (C647), validating "safe energy pathway" as controlled energy addition, not absence of energy. QO applies energy without creating hazard conditions (C601: 0/19). CHSH contains e-STABILITY_ANCHOR MIDDLEs at 68.7%, functioning as the stabilization/correction channel that dominates post-hazard recovery at 75.2% (C645). "Safe" = non-hazardous energy application, consistent with controlled heating (balneum marie, indirect fire).

---

### F-B-003 - Pre-Operational Configuration via A→AZC→B Pipeline

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C473, C506, C468

#### Question

Does the A→AZC→B pipeline architecture align with Brunschwig's pre-operational categorical choices (fuel type, vessel material, distillation method) that constrain downstream execution?

#### Brunschwig Evidence (verified)

Lines 2179-2183: Fuel selection hierarchy — coal, bark, sawdust, wood ("das holtz das vnnützeſt" — "wood is the worst")

Lines 1355-1367: Vessel selection — Venetian glass, Bohemian glass, earthenware from Hagenau/Syburg, copper, tin, lead. Different vessels for different methods (balneum marie vs direct fire).

Lines 1344-1348: Luting requirement varies by method — ash/sand distillation requires luting; balneum marie does not ("die in balneũ marie dürffent nit verlottiert ſin").

All are categorical pre-operational choices that constrain what downstream operations are legal and safe.

#### Structural Properties (Tier 2)

| Property | A→AZC→B pipeline | Pre-operational configuration |
|----------|-------------------|-------------------------------|
| Configuration source | A-record constraint bundle (C473) | Fuel, vessel, method choices |
| Downstream effect | Determines B class legality (C468) | Determines which operations are safe |
| Transmission mechanism | AZC mediates, B executes blindly (C468) | Apparatus mediates, operator executes |
| Coverage | 97.2% of A records carry AX (C568) | Nearly all procedures require configuration |
| Survival correlation | PP composition → class survival breadth (C506, r=0.715) | Better fuel → more operational options |

#### Result Details

1. **Categorical, not parametric** — Brunschwig's choices are categorical (coal/wood/bark, glass/earth/copper, lute/no-lute). The A→AZC→B pipeline transmits categorical legality (C469), not continuous parameters. MATCH.
2. **Upstream determines downstream** — Fuel choice constrains what temperatures are achievable; vessel choice constrains what chemicals are safe. A-record composition constrains which B classes survive (C506, r=0.715). The causal direction is the same. MATCH.
3. **Blind execution** — Once the apparatus is set up, the operator executes the procedure without re-choosing fuel or vessel mid-run. B executes blindly against whatever legality field A→AZC produces (C468). MATCH.
4. **Configuration ubiquity** — Nearly all Brunschwig procedures require pre-operational setup. AX vocabulary appears in 97.2% of A records (C568). MATCH.
5. **Quality affects options** — Better fuel (coal > wood) gives more operational freedom. Higher PP composition in A records correlates with broader class survival (C506, r=0.715). MATCH.

#### Interpretation

The A→AZC→B pipeline accounts for the structural role of pre-operational configuration in a production system. Categorical choices made before execution (fuel, vessel, method) create a constraint field that determines which downstream operations are legal. The A-record encodes these choices; AZC mediates the transition; B executes within the resulting legality envelope. This is sufficient to explain why A and B are grammar-disjoint (C383) but vocabulary-integrated (69.8% shared types): the configuration system and the execution system use overlapping vocabulary but different formal logic.

#### Limitations

- The pipeline architecture is established independently of Brunschwig (Tier 2). This fit adds external alignment, not new structural evidence.
- The specific mapping (fuel → specific A-record features, vessel → specific PP vocabulary) is not established. We show the architectural parallel, not the item-level correspondence.
- Other production systems (brewing, dyeing, metallurgy) also have pre-operational configuration → execution architecture. The pipeline is not Brunschwig-specific.

#### Relation to Constraints

- **Supports:** C473 (A-record as constraint bundle), C506 (PP→survival correlation), C468 (B blind execution)
- **Refines:** C468 (provides physical rationale for blind execution)
- **Introduces NEW constraints:** NO

---

## Lane Architecture Fits

### F-B-004 - Lane Hysteresis Control Model

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C643, C549, C577, C608

#### Question

Does the QO/CHSH two-lane architecture exhibit hysteresis-like oscillation patterns consistent with a bang-bang control strategy for maintaining a system within an operational band?

#### Evidence

Alternation rate = 0.563 vs permuted null = 0.494 (p < 0.0001, 10,000 within-line permutations). Median run length = 1.0 for both lanes (most common sequence is a single token before switching). QO exits faster (60.0%) than CHSH (53.3%).

Section variation: BIO = 0.606, STARS = 0.551, COSMO = 0.506, RECIPE = 0.491, HERBAL_B = 0.427. Higher-oscillation sections correspond to content with more interleaved operations.

#### Result Details

1. **Elevated alternation** -- 0.563 vs 0.494 null is highly significant (z > 10). The grammar PREFERS lane switching over lane persistence. MATCH.
2. **Short runs** -- Median 1.0 for both lanes means the grammar does not sustain long same-lane sequences. This is consistent with rapid oscillation to maintain an operational band. MATCH.
3. **Asymmetric exit** -- QO->CHSH = 60.0% vs CHSH->QO = 53.3%. QO pulses are briefer, CHSH sequences are slightly longer. Consistent with brief energy application followed by stabilization. MATCH.
4. **Content-driven oscillation** -- Section variation (BIO highest, HERBAL_B lowest) matches C577's content-driven interleaving. Different content requires different oscillation rates. MATCH.

#### Interpretation

The two-lane architecture accounts for a bang-bang control strategy: rapid alternation between complementary operational modes (energy application and stabilization) to keep a system within a viability regime. The oscillation rate varies by content type, suggesting the "operational band width" differs across production contexts. This is the natural control strategy when no reliable measurement instrument exists and the operator relies on sensory feedback.

#### Limitations

- "Hysteresis control" is a physical interpretation of statistical alternation. The grammar shows elevated switching, but the physical mechanism is inferred from the Brunschwig context.
- The effect, while highly significant statistically, is modest in magnitude (5.6 percentage points above null). The grammar preference for alternation is real but not overwhelming.
- Cannot distinguish true bang-bang control from any other source of elevated alternation.

#### Relation to Constraints

- **Supports:** C643 (hysteresis oscillation), C549 (interleaving significance), C577 (content-driven), C608 (no lane coherence)
- **Refines:** C549 (adds within-line confirmation, run lengths, transition matrix, section stratification)
- **Introduces NEW constraints:** C643

---

### F-B-005 - PP-Lane MIDDLE Discrimination

**Tier:** F2 | **Result:** SUCCESS | **Supports:** C646, C576, C642

#### Question

Can Currier A PP MIDDLE vocabulary predict QO vs CHSH lane preference in Currier B execution?

#### Evidence

20 of 99 testable PP MIDDLEs significantly predict lane preference at FDR < 0.05 (permutation z = 24.26, p < 0.0001). QO-enriched MIDDLEs are k/t-based ENERGY_OPERATOR role (11/15). CHSH-enriched MIDDLEs are o-based AUXILIARY role (3/5). No obligatory lane-exclusive slots. Signal is distributed, not discrete.

#### Result Details

1. **Robust discrimination** -- 20 significant at FDR < 0.05 vs null mean 0.64 (z = 24.26). The A-side vocabulary genuinely predicts B-side lane routing. MATCH.
2. **Systematic character pattern** -- QO-enriched = k/t, CHSH-enriched = o. This is not random; it follows the kernel-character vocabulary structure. MATCH.
3. **Role alignment** -- QO = ENERGY_OPERATOR role dominance; CHSH = AUXILIARY role dominance. The A-side material classification aligns with B-side functional role. MATCH.
4. **AZC mediation** -- 12/15 QO-enriched and 5/5 CHSH-enriched are AZC-Mediated, confirming the A->AZC->B pipeline transmits lane-relevant information. MATCH.

#### Interpretation

PP MIDDLE vocabulary in Currier A encodes sufficient information to predict QO vs CHSH lane routing in Currier B. The prediction is probabilistic (no obligatory slots) but statistically robust (z = 24.26). This accounts for how pre-operational material choices (A) influence downstream execution routing (B): the vocabulary assigned to each material category carries kernel-character signatures (k/t vs o) that align with the two execution lanes.

#### Limitations

- 17 of 20 discriminators are EN-associated. Since EN subfamilies are defined by QO/CHSH prefix, this is partially tautological. Only 3 non-EN discriminators (g, kcho, ko) represent genuinely novel cross-role discrimination.
- The strongest discriminator (k, r = 0.346) explains only 12% of variance. Lane routing is influenced by many factors beyond PP MIDDLE composition.

#### Relation to Constraints

- **Supports:** C646 (PP-lane discrimination), C576 (vocabulary bifurcation), C642 (A-record architecture)
- **Refines:** C576 (provides character-content basis for vocabulary bifurcation)
- **Introduces NEW constraints:** C646

---

### F-B-006 - Energy/Stabilization Lane Assignment

**Tier:** F3 | **Result:** PARTIAL | **Supports:** C647, C645, C601, C521

#### Question

Can the two execution lanes be mapped to specific control functions: QO = controlled energy addition, CHSH = stabilization/correction?

#### Evidence

Five predictions were tested. Under the original "Change/Hold" framing (QO = hold, CHSH = change), 3/5 confirmed. Under the reversed "Energy/Stabilization" framing (QO = energy addition, CHSH = stabilization), all 5 findings are consistent:

| Test | Finding | Energy/Stab Reading |
|------|---------|-------------------|
| Kernel MIDDLE content | QO: 70.7% k, CHSH: 68.7% e | QO carries energy vocabulary, CHSH carries stability vocabulary |
| Transition stability | QO more stable (p=0.0006) | Routine energy addition is predictable |
| Post-hazard dominance | CHSH 75.2% (p=1.0 for QO) | Recovery = stabilization = CHSH function |
| Hazard proximity | CHSH closer (p=0.002) | Stabilization deploys near hazard |
| Hysteresis oscillation | Alternation elevated (p<0.0001) | Interleaved energy-then-stabilize cycles |

#### Result Details

The original "Change/Hold" interpretation (CHSH = state-changing, QO = state-preserving) is **FALSIFIED** in its literal form: QO tokens contain energy modulation characters, not stability characters; CHSH dominates recovery, not QO. The labels are reversed.

The reversed interpretation (QO = controlled energy addition, CHSH = stabilization/correction) resolves all findings:

- **QO = safe energy** -- QO carries k-ENERGY_MODULATOR MIDDLEs (70.7%) because QO IS the energy application pathway. Zero hazard participation (C601) means the energy addition is inherently non-hazardous (controlled/indirect heating). MATCH.
- **CHSH = stabilization** -- CHSH carries e-STABILITY_ANCHOR MIDDLEs (68.7%) because CHSH IS the stabilization pathway. Post-hazard dominance (75.2%) means CHSH is deployed for recovery. MATCH.
- **CHSH-first ordering (C579)** -- Establish stable baseline before adding energy. The physical interpretation: confirm system is safe before applying heat. MATCH.
- **Section variation** -- BIO shows most oscillation (0.606) = most interleaved heat/stabilize cycles. HERBAL_B lowest (0.427) = more sustained operation in one mode. MATCH.

#### Interpretation

The two execution lanes account for two complementary control functions in a physical production system: energy application (QO) and stabilization/correction (CHSH). The operator alternates rapidly between adding controlled energy and stabilizing the system, with the oscillation rate varying by content type (section). This is consistent with bang-bang temperature control in Brunschwig-era distillation where no reliable thermometer existed.

The interpretation is Tier 3: it is consistent with all Tier 0-2 constraints and resolves the data coherently, but alternative functional mappings cannot be excluded.

#### Limitations

- The "Energy/Stabilization" label is interpretive (Tier 3). The structural facts (kernel content, hazard proximity, alternation) are Tier 2 independent of interpretation.
- C522 (construction-execution independence) means MIDDLE content reflects vocabulary assignment, not necessarily execution behavior. The k-characters in QO MIDDLEs indicate construction-layer heritage, not that QO tokens "do energy modulation" at runtime.
- The original "Change/Hold" framing is falsified as stated. This fit documents the corrected interpretation.

#### Relation to Constraints

- **Supports:** C647 (morphological lane signature), C645 (CHSH post-hazard dominance), C601 (QO zero hazard), C521 (kernel directionality)
- **Refines:** C601 (QO's zero hazard reinterpreted as controlled energy application that is inherently non-hazardous)
- **Extends:** F-B-002 (QO = "safe energy pathway" confirmed as energy application, not energy absence)
- **Introduces NEW constraints:** C647

---

### F-B-007 - Extensible Atom Scaling: Intensity and Duration Dimensions

**Tier:** F3 | **Result:** CONSISTENT | **Supports:** C1197, C1204, C1205, C1242, C1244
**Phase:** EN_LANE_CROSS_PREDICTION (Phase 443)

#### Hypothesis

The two extensible atoms (e, i) encode two independent control dimensions: e-extension modulates energy intensity (k=full heat, ke=modulated, kee=gentle), i-extension modulates iteration duration (i=single pass, ii=sustained cycling). The -aiin/-ain "check" gloss (C561 bigram context) should be reread as "settle/intake" (C1195 atom semantics): monitoring is CHSH's job (C929, C1243), not the i-suffix's.

#### Evidence

**E as intensity gradient:**

| REGIME | k (pure) | ke (modulated) | kee (gentle) | k-ratio |
|--------|----------|----------------|--------------|---------|
| REGIME_2 | 112 | 7 | 2 | 92.6% |
| REGIME_3 | 276 | 44 | 8 | 84.1% |
| REGIME_1 | 1,261 | 291 | 12 | 80.6% |
| REGIME_4 | 67 | 14 | 1 | 81.7% |

REGIME_2 (highest k_ratio, most iteration-heavy) runs almost pure k — maximum intensity, no cooling modulation. REGIME_1 (highest thermo_ke) has the most ke mixing — modulated intensity. The physical mechanism (furnace vents, apparatus height, fuel amount) is underdetermined, but the intensity gradient is structurally supported.

**I as duration gradient:**
- ii is the default form (53.7% vs i 45.9%, C1204 inverted gradient)
- aiin precedes ain 64.9% when both co-occur (C1244): sustained → final pass
- i anti-clusters (z=-6.14, C1205): duration tokens spread across the line, not concentrated
- i displaces energy content (C1205): more i = less k and e (duration parameter competes with intensity for token space)

**Independence:**
- i anti-correlates with e (r=-0.513, C1207) and y (r=-0.599) at folio level
- k-e correlation is near-zero (+0.079): energy atoms are independent of each other
- Two orthogonal axes confirmed

#### Interpretation

The control program has two dials. The e-count on a heat MIDDLE sets how intense the energy application is. The i-count on any suffix sets how long the operation runs before halting. These are independent — a token can specify high intensity with short duration (qok + ain) or moderate intensity with sustained cycling (qoke + aiin). The specific physical mapping to Brunschwig apparatus (furnace plugs, balneum height, fuel type) is underdetermined at this resolution and may not matter for the structural model.

#### Limitations

- "Intensity" and "duration" are interpretive labels for extensibility gradients. The structural facts (e/i extension counts vary by REGIME, i anti-clusters, e/i are independent axes) are Tier 2 regardless.
- Cannot distinguish "simmer vs rolling boil" from "close to fire vs far from fire" for e-intensity — both are consistent.
- iii is extremely rare (0.3% for both e and i), making the 3-state encoding effectively 2-state in practice.

#### Relation to Constraints

- **Supports:** C1197 (extensibility partition), C1204 (i-extension inverted), C1205 (i/k/e orthogonality), C1207 (atom correlation clusters)
- **Extends:** C1242 (cross-lane prediction — the heat-measure cycle uses both dimensions)
- **Refines:** C1244 (aiin→ain wind-down = duration decreasing toward line end)
- **Gloss refinement:** -aiin/-ain suffix gloss updated from "check" to "settle/intake" in GLOSSING.md

---

## Distillation Terminology Fits

These fits map Voynich B structural features to distillation physics. All are Tier 3-4 interpretive (extending GLOSSING.md), with Tier 2 structural foundations where noted.

**Source phase:** DISTILLATION_TERMINOLOGY_MAPPING (Phase 461)

---

### F-B-008 - Two-Channel Thermal Architecture

**Tier:** F3 | **Result:** SUCCESS | **Supports:** C647, C601, C1207

#### Hypothesis

qo and ok manage two physically distinct thermal channels: qo = heat source (k-enriched), ok = vessel temperature (e-enriched).

#### Evidence

- qo k-fraction: 0.510, ok k-fraction: 0.001 (Mann-Whitney p < 0.001)
- ok e-fraction: 0.282, qo e-fraction: 0.102 (Mann-Whitney p < 0.001)
- Permutation test (10K shuffles): p < 0.001 for both
- Negative control: sa prefix shows no k-vs-e differentiation (p = 0.999)
- Cross-validates F-B-006: QO = 70.7% k (energy), CHSH = 68.7% e (stabilization)

#### Interpretation (Tier 3-4)

qo selects the heat source domain (fire/furnace management — adding energy), while ok selects the vessel temperature domain (still/apparatus — managing received heat). These are the two independent thermal channels in distillation: the fire you're tending and the vessel you're monitoring. The k/e enrichment is consistent with C1207 (k-o anti-correlation r=-0.585) and Phase 440 (ok = "vessel").

**Brunschwig:** Fire managed via air holes (lines 2038-2055) vs vessel tested by finger (lines 1880-1893).

#### Limitations

- The structural fact (qo is k-enriched, ok is e-enriched) is Tier 2. The physical interpretation (heat source vs vessel temperature) is Tier 3-4.
- qo k-frac = 0.510 (not ~0.707 as F-B-006 lane level) because this measures PREFIX-level, not lane-level.

---

### F-B-009 - Overshoot-Correct Cycling

**Tier:** F3 | **Result:** SUCCESS | **Supports:** C643, C647

#### Hypothesis

Within lines, qo-k tokens followed by ok-e tokens more than chance — consistent with heat overshoot → vessel correction cycle.

#### Evidence

- qo-k → ok-e: 103 transitions (null mean: 72.0, permutation p < 0.001)
- ok-e → qo-k: 112 transitions (null mean: 72.1, permutation p < 0.001)
- Both directions elevated: the cycle completes (overshoot → correct → overshoot)
- Negative control: da→sa transitions = 6 (p = 0.996, at chance)

#### Interpretation (Tier 3-4)

The grammar encodes overshoot-correct cycling at the within-line level. The operator applies heat (qo+k), the vessel overshoots, the operator cools (ok+e), then repeats. This is the fundamental control loop in pre-thermometer distillation: heat always overshoots because there's no precise temperature control, so the operator continually corrects.

**Brunschwig:** "wo es hehender tropfen ist so wer das fuer zu gross" — if it drips faster, the fire is too great.

#### Limitations

- The transition elevation is modest (~40% above null). The grammar prefers but does not require this cycling.
- Cannot distinguish overshoot-correct from any other source of qo/ok alternation within lines.

---

### F-B-010 - REGIME Token Profile Discrimination

**Tier:** F3 | **Result:** SUCCESS | **Supports:** C643, REGIME system

#### Hypothesis

The 4 REGIMEs produce statistically different token profiles across multiple metrics.

#### Evidence

6/7 metrics discriminate by REGIME in B (Kruskal-Wallis p < 0.01):

| Metric | H | p | R1 | R2 | R3 | R4 |
|--------|---|---|----|----|----|----|
| k_frac | 49.2 | <0.001 | 0.168 | 0.113 | 0.086 | 0.080 |
| e_frac | 35.9 | <0.001 | 0.194 | 0.088 | 0.167 | 0.197 |
| h_frac | 27.0 | <0.001 | 0.018 | 0.017 | 0.028 | 0.029 |
| THERMAL_rate | 44.7 | <0.001 | 0.278 | 0.143 | 0.184 | 0.169 |
| MONITORING_rate | 13.9 | 0.003 | 0.019 | 0.007 | 0.014 | 0.019 |
| CONTAINMENT_rate | 11.8 | 0.008 | 0.048 | 0.074 | 0.053 | 0.072 |
| mean_line_length | 3.3 | 0.345 | 9.20 | 9.15 | 9.93 | 11.35 |

**Negative control:** Currier A tokens show 0/7 significant metrics — the discrimination is B-specific (execution, not configuration).

#### Interpretation (Tier 3-4)

The REGIMEs correspond to distinct operational modes. Alignment with Brunschwig fire degrees (Tier 3):
- REGIME_1: highest THERMAL (0.278), highest e-frac (0.194) — consistent with balneum marie (gentle, thermal-intensive with cooling)
- REGIME_2: lowest THERMAL (0.143), lowest e-frac (0.088) — sustained operation, low thermal modulation
- REGIME_3: highest h-frac (0.028) — consistent with direct fire (needs more monitoring)
- REGIME_4: highest h-frac (0.029), longest lines (11.35) — precision operation

#### Limitations

- REGIME-to-Brunschwig mapping is Tier 3. The structural discrimination is Tier 2.
- Mean line length does not discriminate (p = 0.345).

---

### F-B-011 - Luting-CONTAINMENT REGIME Association

**Tier:** F3 | **Result:** SUCCESS (via dy-MIDDLE) | **Supports:** REGIME system

#### Hypothesis

Sealing/luting operations discriminate between REGIMEs.

#### Evidence

Category-level CONTAINMENT rate does NOT discriminate (R1=0.048, R3=0.053, p=0.778). But the specific MIDDLE `dy` (seal/close) does:

- R1 dy-rate: 0.138, R3 dy-rate: 0.100 (Mann-Whitney p = 0.015, Cohen's d = -0.753)
- **Unexpected direction:** R1 (balneum) has MORE sealing than R3 (ash/sand)
- Negative control: OPERATION rate p = 0.215 (not significant)

#### Interpretation (Tier 3-4)

The dy-MIDDLE discriminates REGIMEs with a large effect size (d = -0.75). The direction is reversed from prediction: balneum marie (R1) uses more sealing operations than direct fire (R3). This makes physical sense: balneum marie requires sealed vessels immersed in water baths, while direct fire methods may use open or loosely covered vessels.

**Brunschwig note:** "die in balneum marie durfent nit verlottiert sin" (line 1344-1348) says balneum doesn't need luting of joints — but the vessel itself must be sealed to prevent water ingress. The distinction is between joint-luting (not needed for balneum) and vessel-sealing (more needed for balneum).

#### Limitations

- The category-level test failed; only the specific MIDDLE test passed.
- The direction reversal suggests the hypothesis was partially wrong about which REGIME needs more sealing.

---

### F-B-012 - E-Compound Cooling Taxonomy

**Tier:** F4 | **Result:** SUCCESS | **Supports:** C1197, REGIME system

#### Hypothesis

Different e-compound MIDDLEs correspond to different cooling modes, varying by REGIME.

#### Evidence

Chi-square: 140.67 (p < 0.001, df = 6). REGIME x e-compound contingency is highly significant.

| | e_basic | eo_active | ee_extended |
|---|---|---|---|
| REGIME_1 | 550 | 224 | 526 |
| REGIME_2 | 35 | 22 | 33 |
| REGIME_3 | 220 | 302 | 325 |
| REGIME_4 | 62 | 105 | 91 |

2/3 specific predictions confirmed:
- ee_extended enriched in R1 vs R3: YES (526 > 325 after normalizing)
- eo_active enriched in R3 vs R1: YES (302/847 = 35.7% vs 224/1300 = 17.2%)
- e_basic enriched in R3: NO (220/847 vs 550/1300 — R1 has more after normalizing)

#### Interpretation (Tier 3-4)

The e-compound system encodes multiple cooling strategies:
- **ee_extended** (eey, eeol, ee, eeo): Extended cooling — overnight standing, gradual cooling. Enriched in REGIME_1 (balneum).
- **eo_active** (eo, eol): Active cooling — condenser management, water replenishment. Enriched in REGIME_3 (direct fire).
- **e_basic** (e): Basic cooling — simple heat reduction. Universal.

This aligns with C1197 (extensibility partition) where e-extension modulates cooling duration/intensity.

#### Limitations

- The mapping of specific e-compounds to specific physical cooling methods is Tier 4.
- eeol R1 enrichment is only 0.94x (not enriched as predicted); the ee_extended enrichment comes from eey and eeo.

---

## Grammar Execution Fits

*No fits logged yet.*

---

## Kernel Structure Fits

*No fits logged yet.*

---

## Hazard Topology Fits

*No fits logged yet.*

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
