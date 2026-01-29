# C692: Filtering Failure Mode Distribution

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

MIDDLE mismatch accounts for **94.7% of all filtering failures**. PREFIX contributes 3.6%, SUFFIX 1.7%. This dominance is consistent across all roles (91-97% MIDDLE failures). The filtering hierarchy is unambiguous: **MIDDLE is the gatekeeper; PREFIX and SUFFIX are edge refinements.**

## Overall Failure Decomposition

| Failure Mode | Count | % |
|-------------|-------|---|
| MIDDLE miss | 8,311 | 94.7% |
| PREFIX miss | 315 | 3.6% |
| SUFFIX miss | 149 | 1.7% |
| Total | 8,775 | 100% |

## Failure by Role

| Role | Total Failures | MIDDLE % | PREFIX % | SUFFIX % |
|------|---------------|----------|----------|----------|
| CC | 250 | 97.2% | 1.6% | 1.2% |
| EN | 3,416 | 96.4% | 1.2% | 2.4% |
| FL | 298 | 95.6% | 4.4% | 0.0% |
| FQ | 937 | 91.7% | 8.0% | 0.3% |
| AX | 1,263 | 91.1% | 7.2% | 1.7% |

## Interpretation

FQ and AX show the highest PREFIX failure rates (8.0% and 7.2%), suggesting these roles use prefixes that are less commonly shared between A and B. EN shows the highest SUFFIX failure rate (2.4%). FL has zero SUFFIX failures — all FL tokens that pass the MIDDLE gate also pass the SUFFIX gate, indicating FL suffixes are universally compatible.

This confirms C502.a's filtering architecture: MIDDLE provides ~95% of the selectivity; PREFIX and SUFFIX provide targeted additional restriction at the morphological edges.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/instance_trace_analysis.py` (Test 11)
- Extends: C502.a (filtering algorithm), C509.d (independent dimensions)
