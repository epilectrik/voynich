# C1173: LINK Boundary Enrichment Is Passive

**Tier:** 2
**Scope:** B, LINK, boundary, dynamics
**Phase:** LINK_FUNCTIONAL_ARCHITECTURE (Phase 418)
**Depends on:** C805, C609, C1168, C1170

## Statement

LINK is significantly boundary-enriched (entry 17.2%, interior 12.4%, exit 15.3%; chi2=54.5, p<1e-12), replicating C805. However, this enrichment is structurally passive — it does NOT correlate with boundary divergence measures from the dual boundary model (C1168). Per-folio LINK entry enrichment vs jsd_entry: rho=-0.059, p=0.074 (n=43). Per-folio LINK exit enrichment vs jsd_exit: rho=-0.151, p=0.108. LINK macro-state boundary enrichment is only 1.09× (49.8% vs 45.7% baseline). LINK occupies AXM (69.3%) and CC (22.4%) states, consistent with its vocabulary (standalone `ol` = CC, rest = mostly AXM). Boundary vs interior LINK role composition JSD: 0.061 (moderate). Section B drives most boundary enrichment (entry 25.4%, exit 27.5%).

## Evidence

### Zone LINK Rates
| Zone | LINK | Total | Rate |
|------|------|-------|------|
| ENTRY | 416 | 2,414 | 17.2% |
| INTERIOR | 2,261 | 18,262 | 12.4% |
| EXIT | 370 | 2,414 | 15.3% |

| Metric | Value |
|--------|-------|
| Zone chi-square | 54.5 |
| Zone p-value | 1.46e-12 |

### Divergence Correlation (n=43 common folios)
| Correlation | rho | p |
|-------------|-----|---|
| Entry enrichment vs jsd_entry | -0.059 | 0.074 |
| Exit enrichment vs jsd_exit | -0.151 | 0.108 |

### Macro-Automaton Dynamics
| State | LINK | Baseline |
|-------|------|----------|
| AXM | 69.3% | 67.5% |
| AXm | 3.9% | 2.9% |
| FQ | 3.8% | 19.9% |
| CC | 22.4% | 2.2% |
| FL_HAZ | 0.0% | 6.7% |
| FL_SAFE | 0.5% | 0.8% |

| Metric | Value |
|--------|-------|
| Occupancy JSD | 0.147 |
| State boundary enrichment | 1.09× |
| Boundary vs interior role JSD | 0.061 |

### Per-Section Boundary Rates
| Section | ENTRY | INTERIOR | EXIT |
|---------|-------|----------|------|
| B | 25.4% | 18.4% | 27.5% |
| C | 8.7% | 11.9% | 11.9% |
| H | 10.1% | 9.7% | 8.7% |
| S | 16.1% | 9.7% | 9.6% |
| T | 3.0% | 11.8% | 13.4% |

## Interpretation

LINK's boundary enrichment (C805) is a positional frequency effect, not functional choreography. Folios with high boundary divergence (programs that differ most at entry/exit from interior) do NOT use more LINK tokens at boundaries. The enrichment is a static structural property (LINK types happen to be placed more at boundaries) rather than a dynamic modulation (more LINK when programs are diverging). The CC-dominated occupancy (standalone `ol` at 22.4% vs 2.2% baseline CC) further suggests the boundary enrichment reflects `ol`'s specific grammatical function as a CC operator, not a LINK-wide monitoring role.

## Provenance

- Phase 418 Tests 4-5: LINK_MACRO_AUTOMATON_DYNAMICS + LINK_BOUNDARY_ARCHITECTURE
- Script: `phases/LINK_FUNCTIONAL_ARCHITECTURE/scripts/link_functional_architecture.py`
- Results: `phases/LINK_FUNCTIONAL_ARCHITECTURE/results/link_functional_architecture.json` → test4_macro_automaton_dynamics, test5_boundary_architecture
