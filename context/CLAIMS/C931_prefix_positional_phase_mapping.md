# C931: Prefix Positional Phase Mapping

## Statement

Voynich B prefixes show strong positional bias within lines that maps to Brunschwig procedural phases. **Line-initial** prefixes (pch 15.9x, tch 18.4x, sa 3.2x) encode preparation operations. **Line-medial** prefixes (ch, ok, qo) encode execution/monitoring. **Line-final** prefixes (ol 0.33x, lch 0.32x, ot 0.29x, lk 0.14x) encode completion/storage operations. This temporal ordering within lines mirrors the temporal ordering of distillation phases.

## Tier

2 — Empirical, multi-signal convergence

## Scope

B (prefix positional distribution, procedural phase mapping)

## Evidence

### Test: Line-Initial vs Line-Final Ratio

| Prefix | LINE_INIT | LINE_MID | LINE_FINAL | init/final ratio | Phase |
|--------|-----------|----------|------------|-----------------|-------|
| **tch** | 4.0% | 0.5% | 0.2% | **18.40x** | PREPARATION |
| **pch** | 5.2% | 0.8% | 0.3% | **15.91x** | PREPARATION |
| **sa** | 6.3% | 1.0% | 2.0% | **3.15x** | PRE-TREATMENT |
| **te** | 2.5% | 1.4% | 0.9% | **2.71x** | PRE-TREATMENT |
| **sh** | 13.4% | 12.8% | 5.3% | **2.54x** | EARLY MONITORING |
| qo | 13.3% | 23.2% | 13.8% | 0.97x | EXECUTION (even) |
| da | 9.4% | 4.5% | 10.1% | 0.93x | BIMODAL (setup+teardown) |
| ch | 7.3% | 20.0% | 16.8% | **0.43x** | MID-EXECUTION |
| ok | 3.2% | 8.3% | 8.1% | **0.40x** | MID-EXECUTION |
| **ol** | 3.2% | 4.1% | 9.7% | **0.33x** | COMPLETION |
| **lch** | 0.9% | 1.6% | 2.9% | **0.32x** | COMPLETION |
| **ot** | 2.3% | 8.3% | 8.0% | **0.29x** | POST-PROCESS |
| **ke** | 0.2% | 1.6% | 0.9% | **0.24x** | MID-EXECUTION |
| **lk** | 0.3% | 2.6% | 2.2% | **0.14x** | LATE MONITORING |

### Test: Paragraph-Initial Distribution

pch and tch are overwhelmingly paragraph-initial:
- **pch**: 19.6% of paragraph-initial prefixed tokens vs 0.8% elsewhere (**25.5x enrichment**)
- **tch**: 7.6% of paragraph-initial vs 0.7% elsewhere (**10.7x enrichment**)
- qo: 2.7% paragraph-initial vs 21.7% elsewhere (0.13x — never starts paragraphs)
- ch: 0.6% paragraph-initial vs 18.6% elsewhere (0.03x — never starts paragraphs)

pch/tch are procedure-openers ("gather X", "chop Y"). qo/ch are mid-execution operations.

### Test: 5-Position Gradient

Using 5-position binning (INITIAL, EARLY, MEDIAL, LATE, FINAL):

- **sh** peaks at EARLY (16.5%), decays monotonically to FINAL (5.0%)
- **ot** peaks at LATE (10.6%), near-zero at INITIAL (2.0%)
- **ol** peaks at FINAL (9.8%), lowest at INITIAL (3.2%)
- **da** is bimodal: peaks at INITIAL (9.3%) AND FINAL (10.4%), trough at EARLY (3.7%)

## Brunschwig Alignment

| Position | Prefix | Brunschwig phase |
|----------|--------|-----------------|
| INITIAL/PAR-INITIAL | pch, tch | PREPARATION (gather, chop, crush) |
| INITIAL | sa, te | PRE-TREATMENT (dry, macerate) |
| EARLY | sh | SEAL / SETUP (seal vessel, begin monitoring) |
| MEDIAL | ch, ok, qo | DISTILLATION / MONITORING (main process) |
| LATE | ot | POST-PROCESS (rectify, filter, strain) |
| FINAL | ol, lch | STORAGE / COMPLETION (store, pour, settle) |
| BIMODAL | da | SETUP + TEARDOWN (bookend operations) |

This ordering matches Brunschwig's seven-phase workflow:
1. **Preparation** (pch, tch) -> 2. **Pre-treatment** (sa, te) -> 3. **Setup/Seal** (sh) -> 4. **Execution** (qo, ch, ok) -> 5. **Post-process** (ot) -> 6. **Storage** (ol, lch)

## Prior Constraints

- C556: prefix phase mapping (SETUP/WORK/RECOVERY)
- C929: ch/sh sensory modality (ch=0.515, sh=0.396 positional)
- C930: lk section-S concentration (fire-method monitoring)
- F-BRU-012: 5 prep actions mapped to 5 prep-tier MIDDLEs (rho=1.0)

## Source

`phases/BRUNSCHWIG_APPARATUS_MAPPING/` (section_prefix_apparatus.py)
Results: `results/section_prefix_apparatus.json`

## Falsification

Would be falsified if:
1. Prefix positional distributions are uniform (all init/final ratios within 0.8-1.2x)
2. The ordering does not correspond to any procedural temporal sequence
3. Paragraph-initial enrichment for pch/tch is an artifact of line length or section composition
