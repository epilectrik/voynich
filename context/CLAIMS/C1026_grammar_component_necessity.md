# C1026: Grammar Component Necessity — Class Ordering and Forbidden Avoidance Are Load-Bearing; Token Identity Is Partial

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** GRAMMAR_COMPONENT_NECESSITY (Phase 349)
**Depends on:** C1025 (generative sufficiency at M2), C109 (forbidden transitions), C121 (49 classes), C1010 (6-state macro), C789 (forbidden permeability), C1023 (PREFIX load-bearing)

---

## Finding

Five ablation conditions on the real Currier B corpus (100 shuffles each, 100 bootstrap resamples for sigma, >2sigma break threshold) reveal that **class ordering within macro-states** and **forbidden pair avoidance** are both load-bearing for topology-sensitive metrics, while **token identity within class** carries partial signal through MIDDLE-level forbidden pair constraints. Four of 10 topology-sensitive metrics are distributional (survive all ablations), confirming Phase 348's finding that frequency dominates many structural properties. The 49-class ordering carries real sequential structure beyond the 6-state partition — the macro-automaton is NOT the operative grammar layer.

---

## Results

### Necessity Verdicts

| Ablation | Verdict | Breaks | Key Finding |
|----------|---------|--------|-------------|
| (a) All forbidden injection | LOAD_BEARING | 4/10 | Forbidden avoidance shapes bigram diversity and directionality |
| (b) Subset forbidden injection | LOAD_BEARING | 3/10 | Even top-half subset is load-bearing |
| (c) Class shuffle within state | LOAD_BEARING | 5/10 | Class ordering beyond macro-state is essential (spectral gap z=8.85) |
| (d) Class shuffle within role | LOAD_BEARING | 5/10 | Nearly identical to (c) — state and role partitions are equivalent |
| (e) Token shuffle within class | PARTIAL | 2/10 | Within-class entropy breaks; forbidden MIDDLE pairs leak through class boundaries |

### Metric Sensitivity Classification

| Category | Count | Metrics |
|----------|-------|---------|
| DISTRIBUTIONAL | 4 | Depletion asymmetry, FL forward bias, cross-line MI, role self-enrichment |
| SEQUENTIAL | 2 | Spectral gap (49-class), within-class token entropy |
| TOPOLOGICAL | 1 | Forbidden class pair count |
| COMPOUND | 3 | Forbidden MIDDLE count, bigram diversity, forward-reverse JSD |

### Break Matrix (19/50 cells)

| Metric | (a) Forbid all | (b) Forbid subset | (c) State shuffle | (d) Role shuffle | (e) Token shuffle |
|--------|---------------|-------------------|-------------------|------------------|-------------------|
| Spectral gap 49 | - | - | z=8.85 | z=7.58 | - |
| Forbidden MIDDLE | z=4.91 | z=3.90 | z=2.92 | z=3.08 | z=3.51 |
| Forbidden class | z=18.88 | z=15.23 | - | - | - |
| Bigram diversity | z=2.13 | - | z=2.61 | z=2.84 | - |
| Depletion asym. | - | - | - | - | - |
| Fwd-rev JSD | z=2.47 | z=2.40 | z=7.59 | z=7.82 | - |
| FL forward bias | - | - | - | - | - |
| Cross-line MI | - | - | - | - | - |
| Role self-enrich. | - | - | - | - | - |
| Within-class H | - | - | z=4.45 | z=4.48 | z=4.55 |

---

## Key Findings

### 1. Class ordering is the primary load-bearing layer

Shuffling class assignments within macro-states (preserving the 6-state sequence) breaks 5/10 metrics with massive z-scores (spectral gap z=8.85, fwd-rev JSD z=7.59). This proves the 49-class ordering carries real sequential structure that the 6-state macro-automaton does not capture. Combined with C1025 (sufficiency at M2 = 49-class Markov), this brackets the grammar: the 49-class transition matrix is both sufficient AND necessary.

### 2. Forbidden pair avoidance shapes directionality

Injecting forbidden transitions breaks not just the forbidden pair counts (trivially) but also forward-reverse JSD (z=2.47). The safety topology is load-bearing for the grammar's directional asymmetry (C1024). Forbidden avoidance creates measurable time-asymmetry in the transition structure.

### 3. Ablations c and d are structurally equivalent

Class shuffle within macro-state (c) and within role (d) produce nearly identical break patterns (5/10 each, same metrics, similar z-scores). This confirms that the macro-state partition (C1010) and role partition provide equivalent coarse-graining of the 49-class structure.

### 4. Token identity leaks through class boundaries via MIDDLE

Token shuffle within class (e) only breaks 2/10 metrics, but one break is important: forbidden MIDDLE count increases from 13 to 24.8 (z=3.51). This happens because forbidden pairs are defined at the MIDDLE level, and different tokens within the same class can have different MIDDLEs. Swapping tokens within a class can create MIDDLE pairs that violate forbidden rules even though the class pair is unchanged. This proves token-level MIDDLE identity carries structural signal beyond class assignment.

### 5. Four metrics are distributional

Depletion asymmetry, FL forward bias, cross-line MI, and role self-enrichment survive all five ablations. These properties are determined by frequency distributions, not sequential grammar. This directly extends C1025's finding that M0 (i.i.d.) passes 73% of tests — even topology-sensitive metrics can be frequency-dominated.

---

## Structural Implications

1. **The grammar's operative layer is the 49-class transition matrix** — both sufficient (C1025: M2 at 80%) and necessary (this phase: class shuffle breaks 5/10 metrics). The macro-automaton is a lossy projection.

2. **The grammar has exactly two necessary components**: class-level transition ordering AND forbidden pair avoidance. Neither alone is sufficient; both are load-bearing.

3. **Token identity contributes partially** through MIDDLE-level forbidden constraints that cross class boundaries. This is a refinement below the class level that Phase 348's test battery couldn't detect.

4. **40% of topology-sensitive metrics are actually distributional**, confirming that frequency dominates more structural properties than previously recognized.

---

## Evidence

- Script: `phases/GRAMMAR_COMPONENT_NECESSITY/scripts/grammar_component_necessity.py`
- Results: `phases/GRAMMAR_COMPONENT_NECESSITY/results/grammar_component_necessity.json`
- 5 ablations x 100 shuffles x 10 metrics = 5,000 metric evaluations + 100 bootstrap resamples
