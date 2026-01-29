# Currier B Fit Registry

> **This document logs explanatory fits.**
> **No entry in this file constrains the model.**

**Version:** 1.2 | **Last Updated:** 2026-01-26 | **Fit Count:** 6

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
