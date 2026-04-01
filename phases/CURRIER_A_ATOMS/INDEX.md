# CURRIER_A_ATOMS — Exploratory

**Status:** EXPLORATORY (not formalized)
**Date:** 2026-03-31

## Purpose
Atom-level deep dive into Currier A to test the "materials property database" hypothesis.

## Key Findings
- **Confirms existing constraints** at atom level: A is headless+o dominant (C1507), shared grammar with B (C1395), no specific A→B addressing (C384).
- **e_depth**: A=0.304 vs B=0.579. A has almost no thermal modulation — describes properties at ambient conditions.
- **4 folio clusters** by atom profile, strongly associated with sections (chi2=42.8, p=1.3e-07). Cluster 1 (Thermal/Pharma) has e_depth 0.507; Cluster 3 (Stripped-down Herbal) has 0.133.
- **Record opacity gradient**: First tokens are 40.7% semi-transparent (l/r), last tokens are 67.8% opaque (y/n/m). Records open with state descriptions, close with sealed identity.
- **Bridge MIDDLEs (393 shared)**: No specific A→B folio links (permutation p=1.0). Shared grammar, not cross-references.
- **Record decode**: Cluster 1 entries contain `cool.heat.adjust.watch` compounds — thermal test protocols. Cluster 4 entries have zero thermal content.

## No New Constraints
Findings are confirmatory of existing Tier 2 constraints. No formalization needed.

## Scripts
| Script | Purpose |
|--------|---------|
| s1_a_baseline.py | A vs B atom-level comparison (HEAD, MOD, TERM, e_depth, PREFIX) |
| s2_a_folio_clustering.py | Hierarchical clustering of A folios by atom profile |
| s3_a_record_structure.py | Internal record structure: positional grammar, opacity trajectory |
| s4_a_record_decode.py | Full atom decode of 20 sample records (5 per cluster) |
| s5_bridge_ab_connection.py | Bridge MIDDLE A→B specificity test (negative) |

## Results
All in `results/` — JSON outputs from each script.
