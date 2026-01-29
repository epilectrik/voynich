# C622: Hazard Exposure Anatomy

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** HAZARD_CLASS_VULNERABILITY

## Statement

The 43 safe instruction classes (those not participating in forbidden transitions) achieve hazard immunity through exactly two mechanisms: **role exclusion** (23 classes: 20 AX + 3 CC contain zero hazard members) and **sub-group exclusion** (20 classes: 16 EN + 2 FL + 2 FQ belong to safe sub-groups within hazard-bearing roles). No class achieves safety incidentally. Despite immunity from forbidden transitions, safe classes route to hazard classes at 24.6% rate -- they are embedded in the same transition network and do not avoid hazard neighbors.

## Evidence

### Immunity Mechanism Counts

| Mechanism | Classes | Roles |
|-----------|---------|-------|
| Role exclusion | 23 | 20 AX + 3 CC |
| Sub-group exclusion | 20 | 16 EN + 2 FL + 2 FQ |
| Incidental | 0 | -- |
| **Total safe** | **43** | 49 - 6 hazard |

### Safe-Class Hazard Routing Rates

| Role | N safe | Mean ->haz% | Std | Range |
|------|--------|-------------|-----|-------|
| AX | 20 | 0.267 | 0.101 | [0.125, 0.455] |
| CC | 3 | 0.229 | 0.162 | [0.000, 0.351] |
| EN | 16 | 0.213 | 0.087 | [0.042, 0.367] |
| FL | 2 | 0.151 | 0.026 | [0.125, 0.176] |
| FQ | 2 | 0.269 | 0.071 | [0.198, 0.340] |

Global safe-class rate: 24.6%. Class membership predicts hazard-neighbor rate beyond role alone (chi2=239.0, df=37 vs chi2=33.3, df=4 for role-only).

### Within-Role Contrasts

**EN:** Hazard {8,31} vs 16 safe classes show no positional difference (Mann-Whitney p=0.49). MIDDLE overlap is minimal: Jaccard=0.089 (5 shared MIDDLEs from 56 total). Hazard EN has only 6 MIDDLEs; safe EN has 55.

**FL:** Hazard {7,30} vs safe {38,40} show massive positional separation (Mann-Whitney p<0.001). Safe FL clusters at line-final (mean=0.811); hazard FL is mid-line (mean=0.546). MIDDLE Jaccard=0.300.

**FQ:** Hazard {9,23} vs safe {13,14} show no positional difference (p=0.53). MIDDLE Jaccard=0.333. Safe FQ (ok/ot-prefixed) routes heavily to EN classes; hazard FQ (short atomic tokens) routes to self and hazard FL.

## Interpretation

Hazard immunity is cleanly stratified. The first layer is role-level: CC and AX roles have zero hazard classes by definition. The second layer is sub-group-level: within EN, FL, and FQ, specific sub-groups (EN_QO, FL_SAFE, FQ_PAIR) are excluded from forbidden transitions. There is no third layer -- no class achieves safety by accident. This confirms that hazard topology is structurally determined, not emergent.

## Extends

- **C541**: Confirms 6 hazard classes and adds the immunity mechanism for the other 43
- **C586**: FL_SAFE={38,40} confirmed as positionally distinct (line-final vs mid-line)
- **C601**: FQ_PAIR={13,14} confirmed as routing-distinct from FQ_CONN={9,23}

## Related

C109, C541, C542, C554, C586, C601
