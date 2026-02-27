# C1373: PREFIX Category-Position Decomposition

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** 486 (PREFIX_CATEGORY_POSITION_DECOMPOSITION)
**Depends on:** C1372, C1371, C1001, C1012, C1305, C1250, C1299, C1300, C1302
**Amends:** C1372 (PREFIX confound conclusion was too strong)

## Statement

The "thermal arc" (C1371) is NOT a PREFIX compositional artifact. It exists **within** individual PREFIX families: ch shows THERMAL decline rho=-0.900 (chi² p=0.000003), sh shows rho=-0.800 (chi² p=0.000286), and 11/27 qualifying PREFIXes show |rho|>0.50 (weighted average rho=-0.720). Removing positional specialist PREFIXes (5.7% of tokens) actually **strengthens** the gradient (rho -0.400 → -0.900). The full-corpus Q2 THERMAL bump is caused by qo (59% THERMAL, peaks at Q2); removing qo makes the gradient monotonic. BARE tokens (no PREFIX) anchor the line-final THERMAL depletion: they concentrate at Q5 (rho=1.000 for position) with near-zero THERMAL (1.6%-4.9%).

**C1372 amendment:** The PREFIX confound control in Phase 485 was too aggressive. It residualized category position against PREFIX mean position, which removed both between-PREFIX composition AND within-PREFIX gradients. The gradient is genuinely within-PREFIX, meaning MIDDLE selection by line position is not fully mediated by PREFIX identity.

## Key Findings

### T1: Within-PREFIX Gradient (ch, sh)

| PREFIX | N | Chi² | p | V | THERMAL rho | FLOW rho |
|--------|---|------|---|---|-------------|----------|
| ch | 3,457 | 75.9 | 0.000003 | 0.074 | -0.900 | +0.900 |
| sh | 2,306 | 61.2 | 0.000286 | 0.081 | -0.800 | -0.600 |

Both show significant category-position coupling. **H3 (compositional artifact) FALSIFIED.**

ch THERMAL profile: Q1=0.271, Q2=0.229, Q3=0.187, Q4=0.202, Q5=0.181 (declining)
sh THERMAL profile: Q1=0.262, Q2=0.263, Q3=0.240, Q4=0.202, Q5=0.218 (declining)

### T2: Specialist Contribution (INVERTED)

| Corpus Subset | N | THERMAL rho | Interpretation |
|---------------|---|-------------|----------------|
| Full corpus | 22,753 | -0.400 | Weakened by qo Q2 bump |
| Specialists removed | 21,445 | -0.900 | Gradient strengthens |
| ch+sh only | 5,763 | -1.000 | Perfect monotonic decline |

Specialist PREFIXes (po, pch, tch, dch, ar, al, or) are only 5.7% of tokens. They DILUTE the gradient, not create it. Attenuation ratio > 1.0 (inverted: removing them helps).

### T3: ch/sh Divergence by Position

ch/sh category divergence is significant at only 1/5 quintiles (Q3, V=0.204). JSD range/mean = 1.807 (unstable). The sister pair divergence (C1299) is real but varies by line position — strongest at Q3 where OPERATION diverges most (ch=0.242 vs sh=0.342).

### T4: ok/ot at Q5

ok/ot contribute +3.3pp FLOW+TRANSITION at Q5. Their profiles at Q5: ok=30% TRANSITION + 29% FLOW; ot=32% TRANSITION + 31% FLOW. They are line-final resolution specialists, enriching the FLOW/TRANSITION spike at Q5.

### T5: qo THERMAL Effect

qo is 59.1% THERMAL and peaks at Q2 (23.3% of Q2 tokens). Removing qo STRENGTHENS the gradient (rho -0.400 → -0.900). **qo creates the non-monotonic Q2 THERMAL bump** in the full corpus. Without qo, THERMAL decline is monotonic.

### T6: BARE Line-Final Anchor

BARE tokens (n=3,634) concentrate at Q5 (rho=1.000 for position gradient). They carry near-zero THERMAL (1.6%-4.9%) and high FLOW (30.5%). BARE at Q5 creates a compositional THERMAL-depleting AND FLOW-enriching effect. But BARE also has its own internal gradient (chi²=94.2, p<0.000001).

### T7: Full PREFIX Stratification

| Metric | Value |
|--------|-------|
| Qualifying PREFIXes (N≥100) | 27 |
| With |rho| > 0.50 | 11 (41%) |
| Weighted average THERMAL rho | -0.720 |
| Token coverage of strong PREFIXes | >85% |

**Verdict: H1+H2 HYBRID.** The gradient is concentrated in the major PREFIXes (qo, BARE, ch, sh, ok, ot, ol, lk, lch, yk, pch) but these cover the vast majority of tokens. Smaller PREFIXes (da, sa, te, ke, ka, ta, etc.) show flat or inconsistent patterns.

## Three Mechanisms Creating the Thermal Arc

1. **Within-PREFIX MIDDLE selection shifts** (dominant): At different line positions, each PREFIX selects different category MIDDLEs. THERMAL MIDDLEs are preferentially selected at line-initial positions even within a single PREFIX like ch.

2. **BARE compositional effect**: BARE tokens concentrate at Q5 with near-zero THERMAL, amplifying line-final THERMAL depletion.

3. **qo medial injection**: qo peaks at Q2 with 59% THERMAL, creating the non-monotonic Q2 bump. This partially masks the underlying monotonic decline.

## Implications

1. **C1372 is partially reversed:** The "PREFIX confound COLLAPSES signal" finding was an artifact of the residualization method, not a genuine confound. The gradient exists WITHIN PREFIXes.

2. **MIDDLE selection is position-dependent even within PREFIX.** This extends C1012 (PREFIX selects MIDDLEs) — the selection depends on line position, not just PREFIX identity.

3. **The thermal arc is structural, not artifactual.** C1371 stands, and the arc is genuinely distributed across the grammar.

4. **The thermodynamic ORDERING model (C1372) still fails.** The specific rank ordering (STAGING < MARKING < CONTAINMENT < ...) is wrong regardless of PREFIX control. What's rehabilitated is the arc itself, not the thermodynamic prediction.

## Evidence

- Script: `phases/PREFIX_CATEGORY_POSITION_DECOMPOSITION/scripts/prefix_category_position_decomposition.py`
- Results: `phases/PREFIX_CATEGORY_POSITION_DECOMPOSITION/results/prefix_category_position_decomposition.json`
- 22,753 tokens, 2,413 lines, 27 qualifying PREFIXes
