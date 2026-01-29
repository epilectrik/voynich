# C871: HT Role Cooccurrence Pattern

**Tier:** 2
**Scope:** Currier-B
**Phase:** HT_TOKEN_INVESTIGATION

## Statement

HT tokens show systematic cooccurrence preferences at line level:
- **ENRICHED** with FL (Flow Operators): 2.17x
- **DEPLETED** with CC (Core Control): 0.79x, 0.66x
- **DEPLETED** with FQ (Frequent Operators): 0.61x

HT appears in "setup/flow" zones, not "execution/control" zones.

## Evidence

### Line Composition

| Type | Lines | % |
|------|-------|---|
| HT-only | 65 | 2.6% |
| Mixed (HT + PP) | 2,274 | 89.4% |
| No-HT | 206 | 8.1% |

### Class Cooccurrence on HT Lines

| Role | Representative Class | Ratio |
|------|---------------------|-------|
| FL (Flow) | Class 7 | 2.17x enriched |
| EN (Energy) | Class 39 | 2.09x enriched |
| EN (Energy) | Class 46 | 1.98x enriched |
| FQ (Frequent) | Class 23 | 0.61x depleted |
| CC (Core) | Class 17 | 0.66x depleted |
| CC (Core) | Class 11 | 0.79x depleted |

### Line-1 Specific Pattern

| Class | Enriched in L1 | Context |
|-------|----------------|---------|
| AX_INIT (4,5,6) | 2.1-3.5x | Initialization scaffold |
| EN (44,45,46) | 2.8-3.5x | Energy setup |
| CC (10,11) | 0.56-0.65x | Control depleted |

## Interpretation

HT tokens appear where the system is being set up or flow is being directed, but avoid the dense execution zones where core control (daiin, ol) and frequent operators operate. This suggests:

1. **HT in setup/header zones**: Line-1 uses HT + AX_INIT + certain EN
2. **HT sparse in execution zones**: Body uses CC + FQ with less HT
3. **HT mixed with flow control**: FL operations cooccur with HT

## Implications

HT is not isolated from the instruction grammar—it interleaves with it. But the interleaving is systematic: HT appears in transitional/flow contexts, not in tight control loops.

## Provenance

- Phase: HT_TOKEN_INVESTIGATION
- Script: 03_ht_c475_compliance.py
- Data: ht_c475_compliance.json
