# C1374: Within-PREFIX MIDDLE Positional Selection

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** 487 (WITHIN_PREFIX_MIDDLE_POSITION)
**Depends on:** C1373, C1371, C1305, C1012, C1001, C911, C576, C649, C1300, C1302

## Statement

MIDDLE selection changes by line position within every major PREFIX (7/7 permutation tests p<0.001). The within-ch THERMAL decline (Q1=27.1% → Q5=18.1%) is driven by **extreme concentration**: just 2 MIDDLEs (eey, eol — both THERMAL) explain 100% of the gradient. Position specialists are PREFIX-generalists (mean breadth 15.3 vs 8.3 PREFIXes, p=0.0004), not restricted vocabulary. BARE tokens show EQUAL positional MIDDLE selection to prefixed tokens (JSD rank 14/27 = median), demonstrating that **position drives MIDDLE selection independently of PREFIX routing**. The ch/sh parallel gradient exists but is moderate (shared MIDDLE COM rho=0.468, p=0.007). QO-lane vs CHSH-lane vocabulary partition does not predict positional behavior (p=0.120).

## Key Findings

### T1: Universal MIDDLE Positional Entropy (7/7 PASS)

| PREFIX | JSD(Q1,Q5) | Perm p | N tokens |
|--------|-----------|--------|----------|
| BARE | 0.192 | <0.001 | 3,634 |
| ot | 0.164 | <0.001 | 1,437 |
| da | 0.161 | <0.001 | 1,083 |
| ch | 0.134 | <0.001 | 3,457 |
| ok | 0.120 | <0.001 | 1,474 |
| qo | 0.106 | <0.001 | 4,066 |
| sh | 0.103 | <0.001 | 2,306 |

Every PREFIX changes its MIDDLE distribution between line start and line end.

### T2: Specialist Census (Asymmetric)

| PREFIX | Specialists | Direction | Notes |
|--------|------------|-----------|-------|
| ch | 5/40 (12.5%) | 1 early | Low rate — gradient is distributed |
| sh | 10/34 (29.4%) | **9 early** | sh has many early-biased MIDDLEs |
| qo | 2/34 (5.9%) | mixed | Only k and t are specialists |
| ok | 5/24 (20.8%) | **4 late** | Final-position specialists |
| ot | 8/22 (36.4%) | **7 late** | Strong late specialization |
| da | 8/10 (80%) | 4 late | Most MIDDLEs are specialists |
| BARE | 13/35 (37.1%) | 5 late | Strong late specialization |

**Key asymmetry:** sh has early-biased specialists, ot/ok/BARE have late-biased ones. This matches the thermal arc direction (THERMAL/early categories front-loaded, FLOW/TRANSITION back-loaded).

### T3: Extreme Gradient Concentration (STRONG PASS)

Within ch, the THERMAL decline (Q1=27.1%, Q5=18.1%, decline=9.0pp) is explained by:

| MIDDLE | Contribution | Cumulative | Category | N |
|--------|-------------|-----------|----------|---|
| eey | +4.87pp | 54.3% | THERMAL | 147 |
| eol | +4.15pp | **100.4%** | THERMAL | 102 |

**Just 2 MIDDLEs explain the entire gradient.** Both are THERMAL-classified. eey and eol are heavily Q1-biased within ch — they appear disproportionately at line start. The remaining MIDDLEs partially counteract each other, netting near zero.

### T4: ch/sh Parallel Gradient (Moderate)

32 shared MIDDLEs have sufficient data. Position COM correlation: **rho=0.468, p=0.007**. The parallel exists (significant) but is moderate (below 0.60 threshold). Notable divergences: 'or' (ch_COM=1.76, sh_COM=1.03), 'eeo' (ch_COM=1.10, sh_COM=0.46).

ch-only MIDDLEs have later mean COM (2.57) than sh-only (2.00) — ch's exclusive vocabulary is more centrally/late positioned.

### T5: QO vs CHSH Lane Distinction (NOT Predictive)

QO-only MIDDLEs are slightly earlier (COM=2.03) than CHSH-only (2.28), but the difference is not significant (Mann-Whitney p=0.120). Within qo, k-atom MIDDLEs (COM=1.86) and non-k (1.89) are nearly identical. **The lane vocabulary partition (C649) is orthogonal to positional grammar.**

### T6: BARE = Equal Positional Selection

BARE JSD(Q1,Q5) = 0.192, rank 14/27 = exactly at median. BARE shows NO less positional MIDDLE selection than prefixed tokens, despite lacking PREFIX routing (C1012). **Position drives MIDDLE selection independently of PREFIX identity.**

### T7: Specialists Are Generalists (INVERTED)

Position-specialist MIDDLEs appear under significantly MORE PREFIXes (mean 15.3) than flat MIDDLEs (8.3). Mann-Whitney p=0.0004. This is the opposite of the prediction — positional specialists are the **common, versatile MIDDLEs** (like eey, ey, edy, am, r) that appear across many PREFIX contexts, not restricted vocabulary.

## Interpretation

The thermal arc mechanism is now fully resolved:

1. **A small number of high-frequency, PREFIX-generalist MIDDLEs** (eey, eol, ey, eo, am, r, etc.) have intrinsic positional preferences.
2. These MIDDLEs appear under MANY PREFIXes — they are the "common vocabulary" of the grammar.
3. Their positional specialization creates the within-PREFIX category gradient because they are categorically typed (C1305).
4. PREFIX identity modulates WHICH of these generalist MIDDLEs appear (C1012), but NOT their positional behavior.
5. The gradient is a **MIDDLE-level property**, not PREFIX-level — confirmed by BARE showing equal positional selection.

This means the thermal arc is a genuine feature of MIDDLE positional grammar, not an artifact of PREFIX mixing or PREFIX positional grammar.

## Evidence

- Script: `phases/WITHIN_PREFIX_MIDDLE_POSITION/scripts/within_prefix_middle_position.py`
- Results: `phases/WITHIN_PREFIX_MIDDLE_POSITION/results/within_prefix_middle_position.json`
- 22,753 tokens, 2,413 lines, 1,231 unique MIDDLEs, 7 major PREFIXes

## Falsification Conditions

This constraint would be revised if:
1. eey and eol are shown to be artifacts of the category classification system (C1250)
2. A within-folio analysis reveals the positional preferences are folio-specific rather than universal
3. The category classification changes, altering which MIDDLEs are THERMAL
