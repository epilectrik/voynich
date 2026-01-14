# Test 1: Historical Operator Writing Analysis

**Question:** What do historical sources say "ruins runs"?

**Verdict:** QUALITATIVE_MATCH — Historical sources show phase/location failures as dominant concern.

---

## Methodology

Surveyed early modern distillation texts and secondary scholarship to identify documented failure modes. Categorized findings into the 5-class Voynich hazard taxonomy.

**Sources Analyzed:**
1. Brunschwig's *Liber de arte distillandi* (1500) and secondary literature
2. Medieval/early modern luting and sealing practices
3. General alchemical distillation warnings from period sources

---

## Historical Failure Modes Identified

### 1. Luting Failures (Sealing Problems)

**Source:** [Distillatio blog](https://distillatio.wordpress.com/2013/09/24/the-lute-of-wisdom/) and secondary literature

**Description:**
- Lute (sealing compound) was critical for preventing vapor escape
- Materials included clay, dung, egg whites, flour mixtures
- Low-temperature lutes (like propolis) would melt or burn if heated too much
- Egg white + flour lutes would "bake like a biscuit" but burn at high temperatures

**Hazard Class:** CONTAINMENT_TIMING (seal failures → vapor escape/pressure events)

### 2. Pressure Buildup and Explosions

**Source:** Historical records including "The Alchemist's Experiment Takes Fire" (1687)

**Description:**
- Alembics could explode from pressure buildup
- Operators bored pressure-release holes covered with soft lute
- Manual intervention required to release pressure safely
- Excessive vapor buildup → catastrophic failure

**Hazard Class:** CONTAINMENT_TIMING (pressure events)

### 3. Phase/Location Errors

**Source:** Brunschwig's emphasis on "body and senses" for true craftsmanship

**Description:**
- Knowing when material is in correct phase (vapor vs liquid)
- Timing of collection critical
- Wrong phase at wrong location = failed batch
- "Signs of change" must be watched carefully

**Hazard Class:** PHASE_ORDERING (wrong phase/location)

### 4. Vessel Material Incompatibility

**Source:** [Medieval distillation practices](https://aprilmunday.wordpress.com/tag/medieval-distillation/)

**Description:**
- Alchemists used glass (unreactive) vs pottery (for medical distillation)
- Pottery vessels "can't cope with high temperature distillation"
- Wrong vessel material → contamination or breakage
- Cracked vessels required lute repair

**Hazard Class:** COMPOSITION_JUMP (contamination) and CONTAINMENT_TIMING (breakage)

### 5. Temperature Control

**Source:** [Alchemist workshop practices](https://daily.jstor.org/alchemists-workshop/)

**Description:**
- "Fire was the most significant tool in the alchemist's workshop"
- Fires "carefully curated and meticulously maintained"
- Different fuels (wood, coal, charcoal) for different heat requirements
- Degrees of fire concept (Brunschwig's 4 degrees)

**Hazard Class:** ENERGY_OVERSHOOT (thermal damage) — but notably this is discussed as a CONTROL variable, not primary failure mode

---

## Mapping to Voynich Hazard Classes

| Historical Failure | Voynich Class | Dominance in Sources |
|--------------------|---------------|---------------------|
| Phase/location timing | PHASE_ORDERING | HIGH (constant emphasis) |
| Impure fractions | COMPOSITION_JUMP | MEDIUM (vessel/seal related) |
| Luting/pressure | CONTAINMENT_TIMING | MEDIUM (major practical concern) |
| Flow imbalance | RATE_MISMATCH | LOW (not emphasized) |
| Scorching/thermal | ENERGY_OVERSHOOT | LOW (controlled, not primary risk) |

---

## Qualitative Distribution Comparison

| Hazard Class | Voynich % | Historical Emphasis |
|--------------|-----------|---------------------|
| PHASE_ORDERING | 41% | **DOMINANT** — "signs of change," timing critical |
| COMPOSITION_JUMP | 24% | **SIGNIFICANT** — purity concerns, vessel material |
| CONTAINMENT_TIMING | 24% | **SIGNIFICANT** — luting, pressure release |
| RATE_MISMATCH | 6% | **MINOR** — not emphasized in sources |
| ENERGY_OVERSHOOT | 6% | **MINOR** — control variable, not primary risk |

**Match Quality:** QUALITATIVE ALIGNMENT

The dominance ordering matches:
1. Phase ordering DOMINANT (both)
2. Composition and containment SIGNIFICANT (both)
3. Rate and energy MINOR (both)

---

## Key Insight: Why Energy Is Minor

Historical sources treat temperature/fire as a **control variable**, not a primary hazard:
- Operators control fire carefully (it's their primary tool)
- Failures come from OTHER things going wrong (seals, phases, timing)
- "Degrees of fire" is a STRATEGY choice, not a risk

This matches PWRE-1 finding: ENERGY_OVERSHOOT is only 6% because thermal management is what the operator controls — failures arise elsewhere.

---

## Brunschwig's "Body and Senses" Emphasis

From [PMC article on Brunschwig](https://pmc.ncbi.nlm.nih.gov/articles/PMC5268093/):

> "To realise his concept in the workshop, Brunschwig emphasises the central importance of the body and its senses to ensure true craftsmanship."

This aligns with:
- OJLM-1 hypothesis (judgment-critical processes)
- HT density patterns (attention markers)
- Irrecoverability architecture (operator supplies identity)

---

## Limitations

1. **Indirect Evidence:** Sources describe practices, not failure statistics
2. **Selection Bias:** Surviving texts may emphasize certain concerns
3. **Language Barriers:** Original Latin/German texts not directly accessed
4. **No Quantitative Data:** Proportions inferred from emphasis, not counted

---

## Conclusion

**Test 1 Result: QUALITATIVE_MATCH**

Historical distillation sources show the same dominance pattern as Voynich hazard distribution:
- Phase/timing concerns DOMINANT
- Contamination and containment SIGNIFICANT
- Rate and thermal damage MINOR

The match is qualitative but structurally aligned. Energy is minor because it's a control variable, not a primary failure mode.

---

## Sources

- [Brunschwig PMC Article](https://pmc.ncbi.nlm.nih.gov/articles/PMC5268093/)
- [Distillatio Blog - Lute of Wisdom](https://distillatio.wordpress.com/2013/09/24/the-lute-of-wisdom/)
- [Medieval Distillation - Writer's Perspective](https://aprilmunday.wordpress.com/tag/medieval-distillation/)
- [JSTOR - Inside the Alchemist's Workshop](https://daily.jstor.org/alchemists-workshop/)
- [Wikipedia - Hieronymus Brunschwig](https://en.wikipedia.org/wiki/Hieronymus_Brunschwig)

---

> *This phase does not decode the Voynich Manuscript. It uses physics and historical operator knowledge to test whether the controller's structure is natural for certain process classes. All findings are Tier 3 unless they establish logical necessity.*
