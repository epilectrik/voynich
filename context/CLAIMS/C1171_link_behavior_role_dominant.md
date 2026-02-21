# C1171: LINK Behavior Is Role-Dominant

**Tier:** 2
**Scope:** B, LINK, cross-role, position
**Phase:** LINK_FUNCTIONAL_ARCHITECTURE (Phase 418)
**Depends on:** C609, C805, C1170

## Statement

LINK tokens behave differently across all four major ICC roles (AX, EN, CC, UN), with all showing significant positional divergence from their non-LINK counterparts (Mann-Whitney p<0.05). EN-LINK is early (pos=0.422 vs 0.489), CC-LINK is late (0.511 vs 0.413), AX-LINK is neutral (0.514 vs 0.485), UN-LINK is slightly early (0.461 vs 0.496). Cross-role positional JSD for LINK (0.0138) is comparable to non-LINK (0.0128), indicating that the `ol` substring does not impose a unified behavioral signature across roles. Predecessor macro-state distributions diverge most for CC (JSD=0.014) and least for AX (JSD=0.001). LINK behavior is dominated by the role it inhabits, not by any intrinsic LINK property.

## Evidence

### Per-Role Position Comparison (LINK vs non-LINK)
| Role | n_LINK | n_non | LINK pos | non pos | MW p |
|------|--------|-------|----------|---------|------|
| AX | 799 | 3,341 | 0.514 | 0.485 | 0.037 |
| EN | 578 | 6,633 | 0.422 | 0.489 | <0.001 |
| CC | 421 | 314 | 0.511 | 0.413 | <0.001 |
| UN | 1,168 | 5,870 | 0.461 | 0.496 | 0.001 |

### Boundary Rates
| Role | LINK first | non first | LINK last | non last |
|------|-----------|-----------|----------|----------|
| AX | 14.9% | 15.5% | 15.8% | 10.5% |
| EN | 7.4% | 4.4% | 3.3% | 5.3% |
| CC | 5.0% | 27.1% | 9.5% | 7.6% |
| UN | 19.9% | 15.4% | 15.2% | 14.7% |

### Cross-Role Consistency
| Metric | Value |
|--------|-------|
| Mean LINK pairwise JSD | 0.0138 |
| Mean non-LINK pairwise JSD | 0.0128 |
| Consistent roles (MW p>0.05) | 0/4 |

### Predecessor JSD (LINK vs non-LINK within role)
| Role | JSD |
|------|-----|
| AX | 0.001 |
| EN | 0.004 |
| CC | 0.014 |
| UN | 0.003 |

## Interpretation

If `ol` were a functional substrate imposing consistent behavior regardless of role, we would expect LINK tokens to be more similar to each other across roles than non-LINK tokens. Instead, cross-role JSD is comparable (0.0138 vs 0.0128), and within each role LINK tokens diverge significantly from their non-LINK counterparts in role-specific ways. The `ol` substring does not override or modulate role behavior — it is subordinate to it.

## Provenance

- Phase 418 Test 2: LINK_CROSS_ROLE_CONSISTENCY
- Script: `phases/LINK_FUNCTIONAL_ARCHITECTURE/scripts/link_functional_architecture.py`
- Results: `phases/LINK_FUNCTIONAL_ARCHITECTURE/results/link_functional_architecture.json` → test2_cross_role_consistency
