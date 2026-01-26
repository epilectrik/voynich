# Currier A: What We Know Now

**Status:** CHARACTERIZATION COMPLETE
**Last Updated:** 2026-01-16
**Tier:** Consolidated from Tier 2-3 findings

---

## Executive Summary

Currier A is a **human-facing complexity-frontier registry** - a structured collection of material discriminators organized for expert navigation without semantic content.

The system is:
- **LINE_ATOMIC**: Each line is an independent record unit
- **Non-semantic**: No meaning encoded in individual entries
- **Cognitively optimized**: Structure supports human working memory and navigation
- **AZC-interfacing**: Vocabulary composition predicts downstream compatibility breadth

---

## 1. Record Structure (Tier 2 - Binding)

### 1.1 Atomic Units
| Constraint | Description |
|------------|-------------|
| C233 | LINE_ATOMIC - each line is a complete, independent record |
| C236 | No inter-line dependencies (MI=0 across lines) |
| C240 | Line boundaries are hard record boundaries |

### 1.2 Entry Grammar
```
[non-prefix opener] + [prefixed content] + [DA-family closer]
```

| Component | Description | Evidence |
|-----------|-------------|----------|
| Opener | 57.5% have no standard PREFIX | CAR-6.4 |
| Content | Prefixed tokens (ch, sh, qo, da, ok, ot, ol, ct) | C235 |
| Closer | DA-family tokens 1.92x enriched at final position | CAR-6.4 |

### 1.3 Closure Mechanism
Boundary tokens are **closure states**, not delimiters:
- Return vocabulary space to neutral, maximally compatible state
- Signal that entry has emitted all discriminating vocabulary
- Enable cognitive bracketing without punctuation
- **Uniform** - not adjusted to complexity (PCC AXIS 1)

Morphological signatures:
- -y ending: 36.5% at final position
- -n ending: 15.2% at final position
- -m ending: 12.2% at final position

---

## 2. Internal Punctuation (Tier 2 - Binding)

### 2.1 DA Articulation
| Constraint | Description |
|------------|-------------|
| C422 | DA marks internal sub-record boundaries (75.1% separation) |
| C475 | DA-boundary suppression at entry boundaries |

DA has **dual role**:
1. Internal punctuation (within-entry segmentation)
2. Entry closure (at final position)

### 2.2 DA Distribution
- 38.2% of entries have no DA (single-block)
- 37.1% have 1 DA (two-block)
- 17.4% have 2 DA (three-block)
- 7.3% have 3+ DA

---

## 3. Adjacency Structure (Tier 2 - Binding)

### 3.1 Core Constraints
| Constraint | Description |
|------------|-------------|
| C389 | Adjacency structure exists (9.1% bigram reuse) |
| C346 | Sequential coherence (1.20x MIDDLE overlap) |
| C424 | Clustered adjacency (41.5% in runs) |

### 3.2 Working Memory Chunks (Tier 3 - PCC AXIS 2)
Adjacent entries form **working-memory-sized clusters**:
- Within-cluster coherence: 2.14x vs cross-cluster
- Median cluster size: 2
- Max cluster size: 7 (working memory limit)
- Cohen's d: 1.44 (large effect)

### 3.3 Cluster Properties
Adjacency maximizes **SIMILARITY**, not contrast:
- Adjacent entries share vocabulary (local coherence)
- Clusters function as discrimination regions
- Order optimizes coverage traversal (p=0.002)

### 3.4 Singleton Isolation
Singleton entries (not clustered) show distinct properties:
- Lower hub overlap (0.731 vs 0.850)
- Higher incompatibility density (0.986 vs 0.979)
- These are **deliberate isolation points**, not noise

---

## 4. Vocabulary Structure (Tier 2-3)

### 4.1 MIDDLE Distribution
| Category | Definition | Count | Entry Dominance |
|----------|------------|-------|-----------------|
| Hub | Top 10% frequency | 182 | 92.8% of entries |
| Universal | 10-50% frequency | 729 | 3.3% of entries |
| Tail | Bottom 50% frequency | 911 | 1.9% of entries |

### 4.1.1 A-B MIDDLE Overlap (MIDDLE-AB Phase)

| Metric | Count |
|--------|-------|
| Currier A unique MIDDLEs | 1,013 |
| Currier B unique MIDDLEs | 1,339 |
| Shared (A & B) | 404 (39.9% of A) |
| A-exclusive | 609 (60.1% of A) |
| B-exclusive | 935 |
| Jaccard similarity | 0.262 |

**METHODOLOGY NOTE (2026-01-24):** Regenerated with atomic-suffix parser (voynich.py). Previous counts used compound suffixes and different extraction logic.

**Interpretation:** Currier A enumerates a *potential discrimination space*; Currier B traverses only a *submanifold* of that space. Most of A's MIDDLEs (61.8%) never appear in B, supporting the registry model where A catalogues entities beyond B's operational scope.

### 4.2 Marker Classes (C235)
Eight mutually exclusive PREFIX families:
- ch, sh (sister pair)
- qo, da
- ok, ot (sister pair)
- ol, ct

### 4.3 Folio Specialization
- Entropy: 1.35 vs 1.46 baseline
- Some folios specialize (f100v: 89% ch, f16v: 83% ch)
- Clustering at folio level (C424)

---

## 5. A-AZC Interface (Tier 3)

### 5.1 Compatibility Breadth Rule
Entry vocabulary composition predicts AZC activation breadth:

| Factor | Effect on Breadth | p-value |
|--------|-------------------|---------|
| Hub-dominant | Broader | - |
| Tail-dominant | Narrower | <0.0001 |
| Closure present | Slightly broader | 0.003 |
| Non-prefix opener | Narrower | <0.0001 |

### 5.2 Universal vs Tail Asymmetry
Strong asymmetry in estimated breadth:
- Universal-dominant: 0.58
- Tail-dominant: 0.31
- Difference: 0.27 (p<0.0001)

### 5.3 Section Differences
Herbal A vs Herbal C show measurable differences:
- Hub ratio: 0.79 vs 0.71 (p<0.0001)
- Closure rate: 77.6% vs 71.9% (p=0.028)

Treat as **content regimes**, not temporal phases (rebinding uncertainty).

---

## 6. What Currier A is NOT

### 6.1 Not Semantic
- No meaning encoded in entries
- No material identification possible
- No recipe decoding
- Closure is structural, not meaningful

### 6.2 Not A-B Coupled (at Entry Level)
- C384: No entry-level A-B correspondence
- A-B frequency correlation is infrastructure effect (shared vocabulary)
- Population-level correlation does NOT imply entry mapping

**Vocabulary overlap exists but is partial:**
- 404 shared MIDDLEs (PP, Pipeline-Participating)
- 60.1% of A's MIDDLEs are A-exclusive (609 RI, Registry-Internal)
- Shared vocabulary is cross-reference infrastructure, not entry coupling

### 6.3 Not Order-Dependent (mostly)
- Most properties are INVARIANT under folio reordering
- Folio-local order (within-folio line sequence) is assumed original
- Cross-folio order is NOT authoritative (rebinding likely)

### 6.4 Not Temporally Structured
- No systematic novelty trend in current order
- C476/C478 (coverage/scheduling) interpretation requires latent order recovery
- Any "early/late" claims are LATENT_ORDER_DEPENDENT

---

## 7. Human-Factors Model

Currier A is designed for **expert navigation without meaning**:

### 7.1 Cognitive Affordances
| Feature | Function |
|---------|----------|
| Closure markers | Visual record bracketing |
| Working-memory clusters | Attention stabilization |
| Singleton isolation | Deliberate separation points |
| DA articulation | Within-record segmentation |

### 7.2 Navigation Model
An expert using Currier A would:
1. Recognize entry boundaries via closure morphology
2. Process clusters as working-memory chunks
3. Use adjacency similarity for local orientation
4. Treat singletons as special/isolated items
5. Navigate via marker class organization

### 7.3 AZC Interface
Entry vocabulary composition shapes downstream options:
- Hub-heavy entries: broad compatibility
- Tail-heavy entries: narrow compatibility
- This is interface characterization, not semantic mapping

### 7.4 Visual Anchoring Posture (Labels)

Currier A entries can operate in **two postures** while following identical rules:

| Posture | Placement | Token % | Tail Pressure | AZC Breadth |
|---------|-----------|---------|---------------|-------------|
| **Registry** | P* (text) | 98.5% | 0.031 | 0.70 zones |
| **Visual Anchoring** | L* (label) | 1.5% | 0.190 | 2.25 zones |

**Key findings:**
- Labels are 6.14x more tail-heavy (select high-discrimination MIDDLEs)
- Labels reach 3.2x more AZC zones (remain valid across operational contexts)
- Chi-square test (p=0.282): Same MIDDLE behaves identically in both postures

**Interpretation:** Labels anchor human perception to registry without pre-committing to operational context. The interface role is purely contextual — no semantics introduced.

**See:** [tier3_interface_postures.md](../SPECULATIVE/tier3_interface_postures.md) for full analysis.

---

## 8. Constraints Summary

### Tier 2 (Binding)
| ID | Description |
|----|-------------|
| C233 | LINE_ATOMIC |
| C235 | 8 marker classes |
| C236/C240 | Line independence |
| C346 | Sequential coherence 1.20x |
| C384 | No A-B entry coupling |
| C389 | Adjacency structure exists |
| C422 | DA articulation |
| C424 | Clustered adjacency |
| C475 | DA-boundary suppression |

### Tier 3 (Characterized)
| Finding | Source |
|---------|--------|
| Closure state mechanism | CAR Phase |
| Working-memory chunks | PCC AXIS 2 |
| Singleton isolation | PCC AXIS 2 |
| A-AZC breadth interface | PCC AXIS 4 |
| Section differences | PCC AXIS 1-4 |
| **Visual Anchoring Posture** | **A_LABEL_INTERFACE_ROLE** |

---

## 9. Open Questions (Narrow)

### 9.1 Legitimately Open
1. Adjacency x learning/reinforcement patterns
2. Latent order reconstruction (curriculum recovery)
3. Further A-AZC breadth formalization

### 9.2 Closed (Stop Here)
- Boundary tokens as adaptive signals
- Closure-HT hypotheses
- Closure-adjacency delimiter theories
- Semantic interpretations of any kind
- New grammar proposals

---

## 10. Source Phases

| Phase | Contribution |
|-------|--------------|
| CAR (Currier A Re-examination) | Clean data, closure mechanism, boundary analysis |
| PCC (Post-Closure Characterization) | Cognitive interface, adjacency function, AZC interface |

**Files:**
- `phases/CAR_currier_a_reexamination/CAR_REPORT.md`
- `phases/POST_CLOSURE_CHARACTERIZATION/PCC_SUMMARY_REPORT.md`
- `context/SPECULATIVE/car_observations.md`

---

*Currier A characterization is COMPLETE.*
*Further work should focus on presentation, not discovery.*
