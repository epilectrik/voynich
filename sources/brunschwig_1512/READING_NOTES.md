# Brunschwig 1512 Reading Notes

Notes on Voynich-relevant observations encountered while reading through the NLM scans.

---

## 1. Luting/Sealing Techniques (page 52, folio XII)

Brunschwig gives specific instructions for creating airtight seals using paper, cloth ("durchlage"), and lutum (sealing paste). Seal quality is presented as a prerequisite for successful distillation, not an afterthought.

**Voynich connection:** A2 family depends on seal quality (F5 axis = gasket quality / seal completeness / containment responsiveness). The grammar's containment-timing hazard class (24% of all hazard frames) exists because seal manipulation at the wrong moment is dangerous. Brunschwig's emphasis on luting confirms that seal quality was a primary operational concern, not a trivial setup step.

**Constraints:** C1642 (strength-dependent closure), F5 knob mapping, CONTAINMENT_TIMING hazard class (C109)

---

## 2. Circulation Process Description (page 54, folio XIIII)

"Die mass zu Circulieren" -- explicit instructions for circulatory distillation with pelican-style apparatus. Material circulates through the vessel and returns, rather than being collected and removed.

**Voynich connection:** A2 (SEALED_RECIRC) family is defined by recirculatory behavior with close-recovery channels (R1_C/R4_C). Brunschwig describes exactly the physical process that produces A2-like forgivingness: sealed recirculation allows the apparatus to self-correct because material returns rather than being lost.

**Constraints:** C1639 (A2 excess forgivingness = 159.5% from close-recovery), C1640 (family partition)

---

## 3. Six Distinct Heat Application Methods (pages 50-56, folios XIII-XV)

Brunschwig describes six methods of applying heat, each requiring different apparatus:

| Method | Apparatus | Intensity |
|--------|-----------|-----------|
| Direct fire | Brick furnace | Highest |
| Water bath (balneum mariae) | Kettle over furnace | Moderate-high |
| Sand bath | Flask in sand over heat | Moderate |
| Solar direct | Flask in sun | Low-moderate |
| Solar focused (mirror) | Mirror + flask | Low-moderate (concentrated) |
| Ambient summer heat (dog days) | Flask in warm environment | Lowest |

This is NOT a single knob turned up or down. Each method requires a fundamentally different apparatus configuration. Changing heat regime = changing apparatus setup.

**Voynich connection:** Our REGIME system (R1-R4) maps to distinct fire degrees with different CEI values. Brunschwig confirms that period practitioners did not think of heat as a continuous variable -- they thought of it as distinct operational modes, each with its own equipment. This matches the grammar's treatment of REGIME as a discrete classifier, not a continuous parameter.

**Constraints:** REGIME system (C494), F3 axis (thermal accent), CEI ordering (R2=0.367, R1=0.510, R4=0.584, R3=0.717)

---

## 4. Multiple Simultaneous Distillations (page 50, folio XIII)

The woodcut shows three alembics running simultaneously on a single brick furnace. This is not sequential processing -- it's parallel operation on a shared heat source.

**Voynich connection:** Paragraph independence (C1399-C1400) -- paragraphs as self-contained operational subroutines that can run in parallel. A shared furnace with multiple vessels matches the model of independent subroutines sharing infrastructure (heat source) but operating independently on their own material.

**Constraints:** C1399 (paragraph independence), C1398 (paragraph operational gradient)

---

## 5. Graduated Fire Control Within a Single Distillation (page 50)

Text describes stepping through fire grades during a single distillation run: "bis vff das end des dritten grado / also das das Balneum marie gar nahe anfasse zu süd. Aber in der andern distillation sol man absteen vnd müssen das füer ein beytenteil eine grado..."

Start at one degree, hold until a state condition is met (bath nearly boiling), then reduce fire by a specific amount for the next phase.

**Voynich connection:** This is state-based, not time-based control -- exactly what the user identified. You don't distill for X minutes; you distill until the bath nearly boils, then change your fire. The grammar's macro-state model (AXM/AXm/CC/FL) describes state transitions, not timed sequences.

**Constraints:** C976 (6 macro-states), operator judgment boundaries (C1056)

---

## 6. Pelican Vessel Variants (page 58, folio XVI)

Chapter 7 shows multiple pelican/circulatory vessel forms: "Etliche machen ein ander form und gestalt" (some make another form and shape). Different configurations of the same apparatus type (sealed circulator), each illustrated separately.

**Voynich connection:** A2 family folios share the SEALED_RECIRC classification but have different CCS1 values (forgivingness scores). Different pelican configurations would produce different degrees of self-correction -- a wider return arm allows more material to recirculate, a narrower one restricts flow. Within-family variation in the grammar may reflect physical variation in apparatus configuration within the same apparatus *type*.

**Constraints:** C1639-C1645 (forgivingness mechanism), C1668 (family gradient -- families are gradients, not discrete bins)

---

## 7. Vapor Visible in Woodcuts (page 57)

The furnace illustration explicitly shows vapor/steam rising from the vessel necks. Brunschwig's illustrator chose to depict the vapor as visible rising wisps. This means the operator was expected to observe vapor behavior as part of process monitoring.

**Voynich connection:** Operator judgment boundaries include "visual condensate quality" and "sound assessment (boiling character, hissing, bumping)" as non-encodable judgments. Brunschwig's illustrations confirm that vapor observation was a real-time monitoring activity, not just endpoint assessment.

**Constraints:** C1056 (13 non-encodable judgment types)

---

## 8. Iterative Labor for Quinta Essentia (page 60, folio XVII)

Brunschwig describes the production of quinta essentia as requiring "grosse arbeit vnd lange zit vil mühe vnd werckh" -- great work and long time, much toil and labor. Not a single pass but repeated cycling of material through the apparatus.

**Voynich connection:** F-BRU-033 (Iterative Extraction Cycling Within Paragraphs) found cross-line reset clustering (C1227), PREFIX channel switching (C1228), and alternating suffix modes (C1229) -- the grammar encodes cycling/iteration within paragraphs. Brunschwig confirms the physical basis: producing refined distillates requires repeated passes through the same apparatus, each pass refining further.

**Constraints:** C1227-C1229, F-BRU-033 (ITERATIVE_CYCLING_SUPPORTED)

---

## 9. Three Distinct Operations: Distill, Sublimate, Circulate (page 64, folio XIX)

Brunschwig explicitly lists three distinct operations: "distillieren sub limmiren vnd circuliren" -- distill, sublimate, and circulate. These are not synonyms; they are different processes requiring different apparatus configurations and producing different results. Distillation collects vapor; sublimation collects solid deposits; circulation returns material to the body.

**Voynich connection:** The PREFIX system discriminates between different operational domains (C911, C936). If the grammar's PREFIX families map to these three fundamental operation types, that would be a direct structural anchor. The grammar distinguishes operations not just by intensity (REGIME) but by *type* (PREFIX domain) -- and Brunschwig shows us exactly the operational type vocabulary that was in use.

**Constraints:** C911 (PREFIX-MIDDLE selectivity), C936 (PREFIX domain model), C570-571

**STATUS: NEEDS FOLLOW-UP** -- Check whether the 5 PREFIX domains can be mapped to Brunschwig's operation types (distill/sublimate/circulate plus potentially digest and rectify).

---

## 10. Parallel Pelican Operation (page 64, folio XIX)

Woodcut shows two pelican vessels running side by side on a shared furnace setup. Not a single vessel -- two independent circulatory operations sharing infrastructure.

**Voynich connection:** Reinforces paragraph independence (C1399-C1400) and the operational subroutine model. Two pelicans on one furnace = two parallel subroutines sharing a heat source but operating independently on their own material.

**Constraints:** C1399-C1400 (paragraph independence), C1398 (operational gradient)

---

## 11. Zodiac Signs as Apparatus-Configuration Legality Gates (pages 318-395)

Throughout the Second Book, Brunschwig's woodcut illustrations systematically pair zodiac vignettes with distillation apparatus. The same base woodcut template is reused, but two elements vary: the zodiac sign in the upper right corner, and the apparatus type shown.

**Observed pairings (our page numbering):**

| Page | Zodiac | Apparatus Type |
|------|--------|----------------|
| 318 | Capricorn (goat) | Pelican alembic on brick furnace |
| 323 | Gemini (small human figures) | Pelican alembic on brick furnace |
| 329 | Leo (cat-like lion) | Circular water bath, multiple flasks |
| 339 | Cancer (red lobster/crab) | Circular water bath, multiple flasks |
| 341 | Sagittarius? | Pelican alembic on brick furnace |
| 348 | Different apparatus | Multiple flask arrangement on stand |
| 351 | Scorpio (black scorpion) | Pelican alembic on brick furnace |
| 354 | Libra (scales) | Circular radial water bath |
| 395 | Capricorn (goat, repeated) | Pelican alembic on brick furnace |

The zodiac sign is NOT decorative. The accompanying text uses explicit conditional syntax: **"So der mon ist im [SIGN]..."** ("When the moon is in [sign]...") followed by aspect conditions and then operational instructions. This appears dozens of times throughout the text (grep finds 30+ instances of "mon ist im/in").

The full conditional structure is a three-part gate:
1. **Lunar zodiac position** -- which sign the moon is in
2. **Aspect quality** -- whether planetary aspects are favorable ("guten aspect," "fruntlich")
3. **Operation permitted** -- what to distill, digest, or administer

**Key example (page 351, line 43935):** "So der mon ist im scorpion / so er ist in seinem lesten mittel mit guttem aspect vnd fruntlichen..." -- when the moon is in Scorpio, in its last middle with good aspect and friendly [planets], THEN the kidney/bladder operations described here are legal.

**Key example (page 354, line 44291):** "So der mon ist im ersten angesicht der zwilling..." -- when the moon is in the first face of Gemini, THEN the joint/shoulder operations are appropriate.

**Key example (line 39891):** "liert in balneo Marie / so der mon ist im wid" -- distilled in balneum mariae when the moon is in Aries. Here the zodiac sign directly gates an apparatus type.

**Voynich connection:** This is a direct historical mechanism for C322 (SEASON-GATED WORKFLOW). The constraint system established that only 5/25 AZC placements have full zodiac coverage -- most workflow states are seasonally restricted. Brunschwig provides the physical reason: seasonal/environmental conditions constrain which apparatus configurations are viable.

The critical refinement: since materials are NOT encoded in the Voynich grammar, the zodiac gating cannot be about ingredients. But apparatus configuration IS encoded (families A1-A4, REGIME R1-R4, F5 seal quality). Brunschwig's six heat methods are physically season-dependent:
- Solar direct/focused distillation: only viable in summer months
- "Dog days" ambient heat: only in high summer (Cancer/Leo)
- Freezing-based separation: only in winter
- Water bath behavior: varies dramatically with ambient temperature
- Fire intensity requirements: higher in winter to compensate for cold

The 12 Zodiac pages as seasonal apparatus-configuration legality tables: each page encodes which apparatus configurations and operational regimes are positionally legal given the environmental conditions of that period. The scaffold is identical across all 12 (C431, similarity 0.945) because it's always the same KIND of classification. The vocabulary varies per page (C472, MIDDLE carries folio specificity) because different operations are legal in different seasons.

This does NOT conflict with the "rules out calendars" note in currier_AZC.md. That note rules out narrative calendars (sequential month-by-month prose instructions). What Brunschwig shows is 12 PARALLEL legality tables indexed by temporal position -- each is an independent, standalone gate, not a sequential narrative. This is exactly what 12 structural clones with local vocabulary variation would produce.

**Constraints:** C322 (SEASON-GATED WORKFLOW), C431 (Zodiac template reuse), C472 (MIDDLE folio specificity), C313 (position constrains LEGALITY not PREDICTION), C430 (AZC bifurcation)

**STATUS: ACTIVE INTERPRETIVE LEAD** -- The Brunschwig zodiac-apparatus pairings provide the first period-documented physical mechanism for C322. Consider whether Tier 3 interpretation should be updated.

---

## 12. Shared Iconographic Vocabulary Between Brunschwig and Voynich AZC (pages 316-395)

The zodiac figures in Brunschwig's woodcuts share specific stylistic features with Voynich AZC imagery:

1. **Leo depicted as a housecat-like creature** (page 329) -- the same "weird cat" appearance as Leo in the Voynich zodiac pages. Period German artists had no firsthand reference for lions; they drew from description or copied through chains of artists. Both manuscripts show the same result.

2. **Cancer as a lobster/crayfish** (page 339) -- depicted from above with spread claws, consistent with the crustacean figures in Voynich AZC pages.

3. **Gemini as small human figures** (page 323) -- the "pixies" or nymphs that populate the Voynich AZC rings have a parallel in Brunschwig's zodiac vignettes showing paired small human figures.

4. **Libra as hanging scales** (page 354) -- standard period iconography, matching Voynich depictions.

5. **Wispy vapor/steam** rising from apparatus (all illustrated pages) -- the curling, tapering wisps of steam from alembic necks share a visual aesthetic with certain flowing Voynich glyph forms. This is speculative but worth noting: an author immersed in the visual tradition of illustrated distillation manuals would carry this aesthetic vocabulary into their writing.

6. **Circular radial apparatus layout** (page 354) -- the water bath with flasks arranged radially around a central basin, seen from slightly above, bears a structural resemblance to the center of the Voynich rosettes foldout. If the rosettes page depicts an apparatus layout from above, Brunschwig provides a period illustration of exactly this kind of setup.

7. **Woodcut block reuse with variable elements** -- Brunschwig's printer reuses the same base apparatus woodcut but swaps the zodiac vignette and sometimes the figure pair. The Voynich AZC pages similarly reuse the same circular diagram scaffold but populate it with different figures and labels (C431, 0.945 cross-folio consistency). Both are modular template systems.

**Voynich connection:** These parallels place the Voynich AZC imagery firmly within the Central European pharmaceutical/distillation illustration tradition of c.1480-1520. The iconographic vocabulary is shared. This does not prove common authorship or direct copying, but it narrows the genre and cultural context significantly.

**STATUS: OBSERVATIONAL** -- Visual parallels documented. No constraint implications beyond supporting the established distillation-manual interpretation.
