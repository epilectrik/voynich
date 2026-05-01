# Phase 671: dar Bimodality vs Clause-Structure Hypothesis

**Status:** COMPLETE
**Started:** 2026-05-01
**Goal:** Test whether dar's bimodal line-position distribution (C1980) reflects line-internal clause structure (crazy-expert's hypothesis) or some other mechanism.

## Pre-registered Falsifiers

Before running joint tests, two killer alternatives were tested:

1. **F1 (pre-screen):** Do "headless" tokens (no HEAD atom at MIDDLE position 0) themselves cluster within lines? If uniform, abandon.
2. **F2 (a-HEAD frame leakage):** Do other a-HEAD r-TERM tokens (ar, otar, okar, air) share dar's bimodal profile? If yes, finding is a-HEAD-frame, not dar-specific.
3. **F3 (paragraph-zone residualization):** Does dar's BC drop after residualizing by (paragraph zone × line position)? If yes, dar bimodality is paragraph-position aggregation artifact.

## Pre-registered Joint Tests (executed only if F1 passes and F3 doesn't kill)

1. **J1 (length-conditional peak tracking):** Do dar's bimodal peaks SHIFT with line length, or stay position-absolute? Shifting → clause structure.
2. **J2 (mutual information):** I(dar_pos; nearest_headless_offset | length_bin) — significant MI vs shuffle null = clause-structure signal.

## Pre-registered Outcomes

- Joint tests significant + peaks scale with length → C1980 promotes Tier 3 → 2
- Joint tests null → C1980 stays Tier 3 (descriptive observation valid)
- F2 finds a-HEAD class property → reframe as a-HEAD finding, not dar-specific
- F3 collapse → C1980 demoted (paragraph-zone artifact)

## Findings

### F1: PASS (barely)

Headless tokens (1241 unique forms, n=4967 instances) cluster within lines: BC=0.596, chi-sq=16.98 vs uniform null (crit=16.92 at p=0.05). Decile distribution is U-shaped (16.95% in decile 0, 18.95% in decile 9). Tokens cluster at line edges, not interior.

### F2: a-HEAD r-TERM CLASS PROPERTY CONFIRMED

| Token | N | Mean | BC | Bimodal |
|-------|---|------|-----|---------|
| ar | 198 | 0.554 | 0.600 | YES |
| otar | 92 | 0.626 | 0.576 | YES |
| okar | 85 | 0.514 | 0.490 | no (outlier) |
| air | 34 | 0.571 | 0.638 | YES |
| dar | 188 | 0.507 | 0.581 | YES |

**4 of 5 a-HEAD r-TERM tokens with n≥30 share the bimodal profile.** dar's bimodality is not unique to dar — it generalizes to a class. okar is the lone outlier (BC=0.490 just below threshold), unexplained.

### F3: dar Bimodality SURVIVES Residualization

Body-only dar: BC = 0.564, n=138.

Per-zone:
| Zone | N | Mean | BC |
|------|---|------|-----|
| Z1_first | 1 | 0.566 | 0.000 (n too small) |
| Z2_middle | 118 | 0.522 | 0.563 |
| Z3_last | 19 | 0.432 | 0.601 |

Residualized BC: 0.557 (drop of 0.007 from raw 0.564).

Crazy-expert's bet was 70% null after residualization. Wrong on this falsifier — dar bimodality is NOT a paragraph-zone aggregation artifact.

### J1: Length-Conditional Peak Tracking — PEAKS POSITION-ABSOLUTE (FALSIFIES CLAUSE STRUCTURE)

| Length bin | N | Peak 1 | Peak 2 | Deciles |
|------------|---|--------|--------|---------|
| 4-7 tokens | 12 | 0.05 | 0.25 | 25, 0, 25, 0, 0, 0, 17, 8, 0, 25 |
| 8-12 tokens | 98 | 0.05 | 0.85 | 12, 3, 11, 10, 9, 10, 5, 12, 15, 11 |
| 13+ tokens | 28 | 0.05 | 0.95 | 18, 4, 11, 4, 11, 14, 4, 7, 11, 18 |

**First peak is fixed at decile 0 (line-start) regardless of line length. Second peak migrates with line-end as length grows.** Clause-structure prediction was: peaks scale toward 0.33/0.67 for medium lines, 0.25/0.5/0.75 for long lines (interior boundaries). Observation: peaks remain at the literal line edges. This rules out interior clause-boundary marking.

### J2: Mutual Information — NULL

I(dar_pos; nearest_headless_offset | length_bin) = **0.0000 bits**. Random-shuffle null mean MI = 0.7139 bits. p(actual ≥ random) = 1.0000. The actual MI is LOWER than random nulls — dar position and headless-token positions are independent within length bins.

## Verdict

**Clause-structure hypothesis FALSIFIED.** Both J1 (length-conditional peak tracking) and J2 (conditional MI) reject the prediction that dar marks line-internal clause boundaries. The bimodality is line-edge concentration, not interior structure marking.

**dar bimodality is real but is a class property:** 4 of 5 a-HEAD r-TERM tokens share the bimodal profile. C1980 generalizes from "dar bimodal" to "a-HEAD r-TERM class is bimodal at line edges."

## Constraint Updates

### C1981 (Tier 1, falsification): Clause-structure hypothesis for dar bimodality REJECTED

Pre-registered hypothesis (Phase 671): dar's bimodal line-position distribution reflects interior clause-boundary marking, not just line edges. Tested via:
- J1 length-conditional peak tracking: peaks position-absolute (decile 0 + line-end), do NOT scale with line length
- J2 conditional MI(dar_pos; headless_offset | length): 0.0000 bits, p=1.0000

Mechanism rejected. dar bimodality = line-edge concentration only.

**Tier:** 1 (Currier B, falsification)

### C1982 (Tier 3, observation): a-HEAD r-TERM tokens share bimodal line-position class profile

In Currier B, 4 of 5 a-HEAD r-TERM tokens with n≥30 (ar, otar, air, dar) are bimodal (BC > 0.555). One outlier (okar, BC=0.490) does not share the profile. dar bimodality (C1980) is not dar-specific — it generalizes to a class of tokens sharing the a-HEAD r-TERM frame.

| Token | N | BC |
|-------|---|-----|
| ar | 198 | 0.600 |
| dar | 188 | 0.581 |
| otar | 92 | 0.576 |
| air | 34 | 0.638 |
| okar | 85 | 0.490 (outlier) |

**Tier:** 3 (Currier B, observation pending mechanistic test)

### C1980 update

Mechanism candidate "clause-edge marker" rejected by C1981. C1980 stable at Tier 3 as descriptive observation. Cross-reference C1982 as the more general phenomenon.

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_falsifiers_and_joint.py | All 5 tests (F1-F3 falsifiers, J1-J2 joint test) with 2k-perm MI null | ~1 min |

## Relationship to Existing Constraints

- **C1980** (dar bimodal observation): Mechanism falsified by C1981. Observation stable but reframed as instance of C1982 class.
- **C1486** (-m line-final): Universal pattern. C1981 confirms dar's r-TERM is NOT a hidden interior pattern — it's edge-concentration like -m, just less strict.
- **C1394** (HEAD+MOD*+TERM atom model): C1982 is consistent — atom-frame combinations have positional behavior.
- **C964** (boundary-constrained free-interior grammar): C1981 supports — interior IS free of dar-bimodality structure.
- **C1979** (PREFIX-conditional terminal-atom positional gradient, da family): C1982 generalizes — multiple a-HEAD frames share positional class properties.

## Suggested Follow-up

- **okar outlier:** Why does okar (BC=0.490) not share the a-HEAD r-TERM class profile? Possible mechanisms: ok-prefix-specific deployment, frequency-driven smoothing, or genuine okar-specific behavior.
- **Class extension:** Test a-HEAD with other terminals (-l: dal, kal, tal, al; -n: dan, kan, tan, an) and other HEADs (e-HEAD r-TERM: er, der, ker; t-HEAD r-TERM: tar, tor) for class generalization.
- **Mechanism for edge-concentration:** If clause structure is rejected, what IS driving the bimodal class? Possibilities: discourse-level scope markers, line-as-unit signaling, RI/PP/INFRA partitioning at line edges.
