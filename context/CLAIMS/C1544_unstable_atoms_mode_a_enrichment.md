# C1544: Unstable atoms increase Mode A suffix rate A->B

**Tier:** 2
**Scope:** B, MIDDLE, atom, suffix, mode, UNSTABLE, Mode A, THERMAL, specification, C1509, C1515, C1229

## Claim

All three unstable atoms {p,f,c} increase their Mode A suffix rate when moving from A to B: c +25.3pp (58.2% -> 83.4%), f +22.3pp (32.2% -> 54.4%), p +15.5pp (41.4% -> 56.9%). Stable MOD atoms {i,d} show near-zero or negative shifts (i +0.7pp, d -3.4pp). In B's execution grammar, unstable atoms become MORE specification-oriented (Mode A = THERMAL/MONITORING per C1515), while stable MODs remain in their base register.

## Evidence

Mode A suffix rates by system:

| Atom | Tier | A Mode A% | B Mode A% | Shift | B bare% |
|------|------|-----------|-----------|-------|---------|
| c | UNSTABLE | 58.2% | 83.4% | +25.3pp | 4.9% |
| f | UNSTABLE | 32.2% | 54.4% | +22.3pp | 9.8% |
| p | UNSTABLE | 41.4% | 56.9% | +15.5pp | 6.7% |
| d | STABLE | 6.8% | 3.5% | -3.4pp | 68.6% |
| i | STABLE | 3.2% | 3.9% | +0.7pp | 74.3% |
| s | STABLE | 29.2% | 52.9% | +23.7pp | 28.4% |

Note: s shows similar Mode A enrichment to unstable atoms (+23.7pp), suggesting s may share some register-sensitivity. But s also appears in suffix (986 times), placing it in the OUTCOME-accessible tier (C1541).

c has the highest Mode A rate of any MOD atom in B at 83.4% -- overwhelmingly specification-oriented.

## Methodology

Phase 545 analysis. Mode A suffixes = {d, e, ee, h, y, ey, edy, eey, dy, hy}. Mode B suffixes = {a, i, ii, l, m, n, o, r, s, al, ar, or, am, ol, aiin, ain, iin}. Classified per C1410/C1515 definitions.

## Constraints

- Extends C1382 (k/a atom-initial suffix mode polarization): unstable atoms also show mode polarization
- Consistent with C1515 (Mode A = THERMAL/MONITORING): unstable atoms preferentially receive specification suffixes
- Extends C1509 (instability tiers): instability correlates with Mode A enrichment direction

## Phase

Phase 545: Executive Atom Instability
