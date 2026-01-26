# ANIMAL_RECIPE_TRACE Phase Design

**Date:** 2026-01-25
**Status:** PROPOSED
**Goal:** Trace animal materials through A→AZC→B pipeline to find receiving procedures

---

## Research Question

Do animal-signature A records route to specific B folios/REGIMEs that match Brunschwig's animal procedure categories?

---

## Background

### What We Know

| Constraint | Finding |
|------------|---------|
| C505 | Animal PP signatures: 'te' 16.1×, 'ho' 8.6×, 'ke' 5.1× enriched |
| C527 | Animal suffix pattern: 0% -y/-dy, 78% -ey/-ol |
| C499 | 27 PRECISION-exclusive animal tokens with P(animal)=1.00 |
| C502 | Each A record makes ~80% of B vocabulary illegal |
| C531-535 | Each B folio is distinct procedure with unique vocabulary |

### The New Model

```
A record (material) → AZC (compatibility) → B folio (procedure)
                                           ├── Core vocab (filtered)
                                           └── Unique vocab (always available)
```

### Brunschwig Animal Procedures

From *Liber de Arte Distillandi*, animal-product distillation includes:
- Blood distillation (various animals)
- Milk/whey distillation
- Egg distillation
- Fat/tallow rendering
- Animal part extractions (horns, bones, etc.)

These typically require:
- Lower fire degrees (balneum marie preferred)
- Careful temperature control (proteins denature)
- Specific timing (putrefaction risk)

**Expected REGIME profile:** REGIME_1 or REGIME_2 (low CEI, careful control)

---

## Test Design

### Phase 1: Identify Animal A Records

**Method:**
1. Score each A record for animal signatures using C505 markers
2. Score each A record for animal suffix patterns using C527
3. Combine into animal probability score
4. Identify high-confidence animal records (threshold TBD)

**Markers:**
```python
animal_pp_markers = ['te', 'ho', 'ke']  # C505: 16.1×, 8.6×, 5.1×
animal_suffixes = ['ey', 'ol']  # C527: 78% in animal
herb_suffixes = ['y', 'dy']  # C527: 41% in herb, 0% in animal
```

**Output:** List of A records ranked by P(animal)

### Phase 2: Trace AZC Compatibility

**Method:**
1. For each high-confidence animal A record:
   - Extract its PP vocabulary (MIDDLEs that could pass to B)
   - Apply full morphological filtering (C502.a)
   - Identify which B tokens are legal

2. Aggregate across animal records:
   - Which B MIDDLEs are legal for MOST animal records?
   - Which are legal for FEW animal records?

**Output:** "Animal-compatible" B vocabulary set

### Phase 3: Find Animal-Receiving B Folios

**Method:**
1. For each B folio:
   - Count how many animal-compatible MIDDLEs it contains
   - Compute "animal reception score" = animal-compatible / total MIDDLEs

2. Compare to baseline:
   - Random A records → random B reception
   - Animal A records → specific B reception?

**Hypothesis:** If animal materials route to specific procedures, some B folios will have significantly higher animal reception than others.

**Output:** B folios ranked by animal reception score

### Phase 4: Check REGIME Clustering

**Method:**
1. For high animal-reception B folios:
   - Identify their REGIME (from prior analysis)
   - Check if they cluster in specific REGIMEs

2. Statistical test:
   - Chi-square: Do animal-receiving folios have non-random REGIME distribution?

**Hypothesis:** Animal-receiving folios should cluster in REGIME_1/REGIME_2 (low fire degree, careful control).

**Output:** REGIME distribution of animal-receiving folios

### Phase 5: Brunschwig Comparison

**Method:**
1. From Brunschwig, extract characteristics of animal procedures:
   - Fire degree preferences
   - Timing requirements
   - Hazard warnings

2. Compare to our animal-receiving REGIME profile:
   - CEI match?
   - Escape rate match?
   - Hazard profile match?

**Hypothesis:** Animal-receiving REGIMEs should match Brunschwig's animal procedure characteristics.

**Output:** Structural alignment score

---

## Expected Outcomes

### If Animal Routing Exists

| Phase | Expected Result |
|-------|-----------------|
| Phase 1 | Clear separation: some records strongly animal, others not |
| Phase 2 | Animal-compatible vocabulary is a distinct subset |
| Phase 3 | Specific B folios have high animal reception (>2× baseline) |
| Phase 4 | Animal folios cluster in REGIME_1/REGIME_2 |
| Phase 5 | REGIME profile matches Brunschwig animal characteristics |

### If No Animal Routing

| Phase | Expected Result |
|-------|-----------------|
| Phase 1 | Animal markers work (this is already validated) |
| Phase 2 | Animal-compatible vocabulary is diffuse |
| Phase 3 | All B folios have similar reception (no clustering) |
| Phase 4 | Random REGIME distribution |
| Phase 5 | No specific match |

---

## Success Criteria

**Tier 2 (Structural):** Confirmed if:
- Phase 3 shows >2× reception difference between top/bottom folios
- Phase 4 shows significant REGIME clustering (p<0.05)

**Tier 3 (Characterization):** Animal-receiving folios match Brunschwig profile

**Tier 4 (Speculative):** Specific folio-to-Brunschwig-recipe mapping

---

## Files to Create

| Script | Purpose |
|--------|---------|
| `animal_signature_scoring.py` | Phase 1: Score A records for animal probability |
| `animal_azc_trace.py` | Phase 2: Trace animal compatibility through AZC |
| `animal_folio_reception.py` | Phase 3: Find animal-receiving B folios |
| `animal_regime_clustering.py` | Phase 4: Check REGIME distribution |
| `animal_brunschwig_comparison.py` | Phase 5: Compare to Brunschwig |

---

## Dependencies

- `scripts/voynich.py` for morphology extraction
- Prior REGIME assignments (need to locate/regenerate)
- Brunschwig animal procedure characteristics (from prior phases)

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Animal markers too weak | Use multiple markers, require convergence |
| AZC filtering too aggressive | Compare to baseline (random A records) |
| No REGIME data available | May need to regenerate from CEI/escape metrics |
| Brunschwig comparison subjective | Use quantitative metrics (CEI, escape, hazard class) |

---

## Approval Request

Ready to proceed with Phase 1 (animal signature scoring)?
