# C450: HT Quire Clustering

**Tier:** 2 | **Status:** CLOSED | **Scope:** HT / GLOBAL

---

## Statement

HT density exhibits significant **quire-level clustering** (Kruskal-Wallis H=47.20, p<0.0001, eta-squared=0.150). HT is not uniformly distributed across the manuscript but organized at **codicological boundaries**.

**Interpretation:** HT application was sensitive to quire structure, suggesting quires were treated as production units. Whoever applied HT thought in quire-sized work sessions.

---

## Evidence

### Distribution Test

| Test | Statistic | P-value | Interpretation |
|------|-----------|---------|----------------|
| Wald-Wolfowitz runs test | 84 observed vs 114.5 expected | < 0.0001 | CLUSTERED |
| Kruskal-Wallis (by quire) | H = 47.20 | 0.000063 | Significant quire effect |
| Eta-squared | 0.150 | - | Moderate effect size |

The eta-squared of 0.150 indicates quire membership explains approximately **15% of HT density variance**.

### Quire Rankings

**High HT density quires:**

| Quire | Mean HT Density |
|-------|-----------------|
| G | 0.193 |
| B | 0.189 |
| I | 0.186 |

**Low HT density quires:**

| Quire | Mean HT Density |
|-------|-----------------|
| M | 0.111 |
| K | 0.126 |
| T | 0.138 |

### Position Gradient

| Test | Result |
|------|--------|
| Position-density correlation | r = -0.150 |
| Verdict | No linear gradient |

HT density does not systematically increase or decrease through the manuscript. The pattern is **clustered by quire**, not sequential.

---

## What This Constraint Claims

- HT density is **non-random** (fewer runs than expected)
- Quire membership explains **15% of variance**
- High/low HT quires exist (G, B, I vs M, K, T)
- HT respects **physical production units**

---

## What This Constraint Does NOT Claim

- Specific quires have semantic significance
- Quire = scribe session (possible but not proven)
- HT was applied "after" operational text
- Causal mechanism for quire sensitivity

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C167** | C450 extends: HT is section-exclusive AND quire-clustered |
| **C341** | C450 refines: system stratification now includes codicological axis |
| **C451** | C450 is independent: quire effect persists after controlling for system |

---

## Phase Documentation

Research conducted: 2026-01-10 (HT-THREAD analysis)

Scripts:
- `phases/exploration/ht_folio_features.py` - Per-folio feature extraction
- `phases/exploration/ht_distribution_analysis.py` - Distribution tests

Results:
- `results/ht_folio_features.json`
- `results/ht_distribution_analysis.json`
- `results/ht_threading_synthesis.md`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
