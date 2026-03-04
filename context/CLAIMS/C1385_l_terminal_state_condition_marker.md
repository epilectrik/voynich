# C1385: l-Terminal State/Condition Marker

**Tier:** 2
**Scope:** B
**Phase:** L_ATOM_SEMANTIC_DEEP_DIVE (Phase 496)
**Date:** 2026-03-03
**Depends on:** C1195 (atom gloss tiers), C1209 (positional grammar), C1207 (atom clusters)

## Statement

The atom l functions as a **state/condition marker** in Currier B MIDDLEs. When l occupies the TERMINAL slot of a compound MIDDLE, it converts the base operation into a status reading: "the state of X" rather than "perform X." This interpretation is supported by 15 rounds of hypothesis testing with 10 alternative hypotheses falsified.

Key behavioral signatures:
1. **Post-state-change enrichment (68.9%):** l-terminal tokens appear after macro-state transitions 68.9% of the time vs 47.2% baseline across all terminal atoms. l ranks 3rd highest (after m=78.2%, r=72.6%) in post-change affinity.
2. **Kernel-before-l ordering (77.0%):** On lines containing both kernel tokens and l-terminal tokens, kernel appears first 77% of the time. Operations execute, then status is checked.
3. **Kernel contact avoidance (rho=-0.197):** l-terminal fraction anticorrelates with kernel atom density at line level (p<0.000001). State readings displace active operators.
4. **Mode B locking (72%):** l-terminal MIDDLEs appear overwhelmingly on Mode B (continuation/bare) lines. Status readings are observed, not specified.
5. **Category redirection:** l-terminal compounds redirect from their base atom's default category in 5/5 tested groups, always shifting to state-of-X rather than performing-X.

German candidate: **Lage** (situation, condition, state of affairs).

Compound readings: ol=vessel-state, el=cool-state, al=flow-state, kl=heat-state, dl=seal-state.

Upgrades l from WEAK ("frame") to SOLID ("state") in C1195.

## Evidence

### E1: Post-state-change timing (P-L15 Test 3)

Post-state-change rate by terminal atom (fraction of tokens that follow a macro-state transition):

| Atom | Post-change % | Class |
|------|--------------|-------|
| m | 78.2% | RESPONDER |
| r | 72.6% | RESPONDER |
| **l** | **68.9%** | **RESPONDER** |
| n | 63.6% | RESPONDER |
| i | 48.7% | NEUTRAL |
| y | 43.9% | NEUTRAL |
| o | 42.4% | NEUTRAL |
| d | 38.3% | NEUTRAL |
| k | 31.8% | ACTOR |
| t | 30.4% | ACTOR |
| h | 29.1% | ACTOR |
| e | 18.4% | ACTOR |

Baseline: 47.2%. l exceeds baseline by +21.7 percentage points.

### E2: Kernel-before-l ordering (P-L15 Test 4)

On lines containing both l-terminal and kernel (k/h/e) tokens:
- Kernel appears before l: **77.0%** (374 lines)
- l appears before kernel: 23.0% (112 lines)
- Mean normalized position: kernel=0.450, l=0.498

### E3: Kernel contact avoidance (P-L11)

| Metric | Value |
|--------|-------|
| l-terminal kernel contact ratio | 0.870x |
| Spearman rho (l-frac vs kernel-frac) | -0.197 |
| p-value | < 0.000001 |
| Per kernel: k | 0.836x |
| Per kernel: h | 0.744x (most avoided) |
| Per kernel: e | 0.885x |

Holds in all 4 testable sections: B(-0.286), C(-0.272), H(-0.185), S(-0.215).

### E4: Mode B locking (P-L10)

l-terminal suffix mode distribution: 28.1% Mode A, 71.9% Mode B. Flexibility rank: 16/17 (Mode B locked). l is the only pro-AXM terminal atom that is also Mode B.

### E5: Short dwell / state boundary behavior (P-L12)

l-terminal tokens appear in SHORTER same-state runs (0.739x), with lower next-token same-state probability (0.642x). l is at state boundaries, not in stable dwell states. Line-level: rho=-0.148 (more l = shorter runs).

### E6: Category redirection (P-L6)

l-terminal compounds redirect from base atom's default operational category in 5/5 tested groups. Massive STAGING enrichment (9.7x baseline).

### E7: CHSH + l compositional confirmation

450 tokens of ch/sh prefix + l-terminal MIDDLE (9.2% of CHSH lane). Compositional reading: ch (checkpoint) + ol (vessel-state) = "checkpoint the vessel condition." Overwhelmingly BARE suffix.

### E8: Falsified alternatives

| Hypothesis | Round | Result | Why falsified |
|-----------|-------|--------|---------------|
| Let flow | P-L1/2 | WRONG_DIRECTION | l enriched in AXM, not FL_SAFE |
| Release/discharge | P-L3 | WRONG_DIRECTION | STAGING 9.7x, not TRANSITION |
| Arrange/lay | P-L4 | NULL | No paragraph-positional gradient |
| Level (thermal) | P-L5 | WRONG_DIRECTION | Anticorrelates with THERMAL |
| Specifier | P-L7 | INVERTED | Low categorical purity (rank 11/13) |
| Redirect | P-L8 | INVERTED | Pro-AXM, not anti-AXM |
| Continue/sustain | P-L9 | NUANCED | ol increases transitions |
| Nominalizer | P-L10 | FAILED | Mode B locked, not flexible |
| Hold/standby | P-L12 | INVERTED | Short dwell, at boundaries |
| Free/available | P-L13 | FAILED | Low successor diversity |
| Product/deposit | P-L14 | CONTROL_FAILS | l not special for ordering |

## Relationship to Existing Constraints

- **C1195** (Tier 2): Updates l from WEAK ("frame") to SOLID ("state")
- **C1207** (Tier 2): {k,l} energy cluster at folio level (r=+0.54); at line level they anticorrelate (-0.184, Simpson's paradox) — k operates, l reads state, both needed per folio
- **C1208** (Tier 2): l is NEUTRAL carryover class; consistent with state-reading (no directional persistence)
- **C1209** (Tier 2): l is TERMINAL slot (71%+); state marker is inherently terminal (modifies what precedes it)
- **C1250** (Tier 2): l maps to STAGING (9.7x); staging = readiness/condition assessment
- **C1386** (Tier 2): l is a RESPONDER atom (68.9% post-change); state readings follow operations

## Falsification

Would be falsified if:
1. l-terminal tokens were shown to PRECEDE state changes at above-baseline rates
2. l-terminal compounds were found to have operational (not observational) semantics in a validated compound set
3. The post-state-change signal (68.9%) were shown to be an artifact of MIDDLE length or frequency confounding

## Provenance

- `phases/L_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_l15_state_condition_marker.py` — primary evidence (P-L15)
- `phases/L_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_l11_kernel_contact.py` — kernel avoidance (P-L11)
- `phases/L_ATOM_SEMANTIC_DEEP_DIVE/scripts/chsh_l_lane_check.py` — CHSH compositional confirmation
- `phases/L_ATOM_SEMANTIC_DEEP_DIVE/results/l_atom_prediction_results.json` — all 15 rounds structured
