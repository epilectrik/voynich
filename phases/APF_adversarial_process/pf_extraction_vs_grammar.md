# PF-E (Continuous Extraction-Like) vs Voynich Grammar

> **ADVERSARIAL TEST**: Finding where extraction archetype fits POORLY

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| Structural Coherence | 0.470 |
| Total Tensions | 10 |
| Unexplained Features | 7 |
| Strained Assumptions | 2 |

---

## Test A: Program Role Distribution

**Coherence Score**: 0.350

### Tensions
- Only 18.1% AGGRESSIVE programs - extraction typically optimizes throughput
- 26.5% CONSERVATIVE/ULTRA programs unexplained by extraction logic
- Only 12.0% HIGH_INTERVENTION - extraction usually requires close monitoring

### Unexplained Features
- ULTRA_CONSERVATIVE programs (4.8%) have no clear extraction role
- LINK_HEAVY_EXTENDED programs (7.2%) suggest patience beyond extraction needs

---

## Test B: LINK Utilization

**Coherence Score**: 0.700

- Mean LINK density: 0.383
- Mean max consecutive LINK: 8.5

### Tensions
- Mean max consecutive LINK 8.5 suggests patience beyond extraction timescales

### Unexplained Features
- High-LINK programs being SAFER contradicts extraction's speed-safety tradeoff

---

## Test C: Hazard Encoding

**Coherence Score**: 0.400

- Hazard density mean: 0.582
- Near-miss mean: 23.7
- All hazards bidirectional: True

### Tensions
- 100% bidirectional hazards - extraction cannot 'un-extract'
- Mean near-miss 23.7 - extraction operating near hazard limits

### Unexplained Features
- All 5 hazard types equally present - extraction expects COMPOSITION emphasis
- PHASE_ORDERING is 41% of hazards - extraction doesn't inherently phase-order

---

## Test D: Absence of Endpoints

**Coherence Score**: 0.050

- Endpoint markers present: 0
- Archetype predicts endpoints: True
- Fit quality: **POOR**

### Tensions
- CRITICAL: 0 endpoint markers - extraction typically monitors for completion
- 0 yield-progress indicators - extraction needs to know when to stop
- Indefinite operation encoded - extraction is inherently finite

### Unexplained Features
- How does operator know extraction is 'done'?
- What prevents over-extraction or resource waste?

---

## Test E: Recovery & Restart Programs

**Coherence Score**: 0.850

- Restart-capable programs: 3 (f50v, f57r, f82v)
- Mean recovery ops: 16.1

### Tensions
- Only 3 restart-capable - extraction often restarts batches

### Unexplained Features

---

## What PF-E Struggles to Explain

### Critical Mismatches

1. **No endpoint markers** — Extraction is inherently finite; grammar encodes indefinite operation
2. **Bidirectional hazards** — Extraction is irreversible; grammar treats forward/backward violations symmetrically
3. **High LINK density** — Extraction optimizes throughput; grammar emphasizes patience
4. **Conservative program dominance** — Extraction pushes limits; grammar prioritizes safety

### Awkward Fits

1. ULTRA_CONSERVATIVE programs (4.8%) have no extraction purpose
2. High-LINK being SAFER contradicts extraction's speed-safety tradeoff
3. PHASE_ORDERING as dominant hazard (41%) — extraction doesn't inherently phase-order
4. All programs reach STATE-C — extraction expects varied endpoints

### Degree of Contrivance Required

To fit PF-E to this grammar requires assuming:
- The operator provides external endpoint detection (not encoded)
- Speed is externally optimized despite grammar prioritizing safety
- Bidirectional hazards are a "safety margin" abstraction
- Conservative programs handle "delicate" substrates (ad hoc)

**Contrivance level: HIGH**