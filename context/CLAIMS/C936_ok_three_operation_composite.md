# C936: ok Prefix as Vessel Domain Selector

## Statement

The prefix **ok** functions as a **domain selector** targeting the vessel/apparatus, not as a verb. The MIDDLE provides the actual action performed on the vessel: ok+aiin = "check vessel," ok+ar = "close vessel," ok+e = "cool vessel," ok+ai = "open vessel." This is consistent with the general PREFIX-as-role-selector principle (C570, C571) and explains ok's restriction to e-family + infrastructure MIDDLEs (C911): vessel operations are cooling/stability and infrastructure actions, not direct energy operations.

**Revision note:** This constraint was originally titled "ok Prefix Three-Operation Composite" and claimed ok encoded three distinct Brunschwig sealing verbs (LUTE_JOINTS/PLUG/COVER) distinguished by MIDDLE. That interpretation was falsified at the line level — composite verb glosses produced incoherent procedural readings ("seal check, plug close, cover cool" = word salad). The distributional evidence (regime distributions, repetition rates) remains valid but is reinterpreted as reflecting different vessel operations (cooling, checking, opening) rather than different sealing types.

## Tier

- **Tier 2** — ok distributional properties: late position (mean 0.538), same-MIDDLE pairing with other prefixes (378 pairs), e-family + infrastructure restriction (C911)
- **Tier 3** — The semantic label "VESSEL" is speculative interpretation consistent with structural evidence and Brunschwig alignment

## Scope

B (morphology, prefix semantics)

## Evidence

### Test 1: Domain Selector Coherence (15 hypotheses, 10 lines)
Tested 15 alternative glossing hypotheses (seal, close, cap, cover, vessel, shut, stopper, secure, while-sealed, lid, contain, apparatus, seal-v2, lute, tend) against 10 high-ok lines across all four regimes.

**Result:** "vessel" (ok = apparatus target, MIDDLE = action) produced the only coherent procedural readings across ALL test lines. All verb-based hypotheses (ok = "seal/close/cap/cover") produced either word salad or circular constructions.

**Key discriminating line (f40r L4):**
- Verb model: `seal check -> seal close -> seal end` (redundant, incoherent)
- Domain model: `check vessel -> close vessel -> vessel ready -> maintain vessel` (distinct actions, coherent sequence)

### Test 2: Same-MIDDLE Pairing (378 pairs)
Found 378 instances where ok and another prefix share the same MIDDLE on the same line:
- `okeey` (vessel: deep cool) vs `cheey` (test: deep cool) — same action, different target
- `okaiin` (vessel: check) vs `qoaiin` (heat: check) — same check, different domain
- `okedy` (vessel: batch) vs `ychedy` (test: batch) — same batch, different context

This demonstrates PREFIX differentiates the TARGET DOMAIN, not the action.

### Test 3: Positional Behavior
ok tokens appear LATE in lines (mean position 0.538 vs 0.484 for non-ok), consistent with managing the vessel AFTER process operations begin. Position distribution: Q1=17.2%, Q2=25.6%, Q3=28.4%, Q4=28.8%.

### Test 4: C911 Physical Explanation
ok is restricted to e-family (cooling) + infrastructure, forbidden from k-family (heating). Under the vessel interpretation: you cool/check/maintain the vessel, but you don't "heat the vessel" (you heat the contents via qo-channel). The C911 forbidden combinations now have a physical explanation.

### Test 5: Full Paragraph Recipe Coherence
Rendered complete paragraphs from f40r (R4), f108v (R1), f33r (R3) as step-by-step recipes under the vessel hypothesis. Sequences like:
- `HEAT:apply -> VESSEL:check -> VESSEL:close -> VESSEL:ready -> VESSEL:maintain -> continue` (f40r L4)
- `VESSEL:cool -> VESSEL:cool -> VESSEL:cool -> TEST:discharge -> VESSEL:open` (f108v L8)
- `VESSEL:check -> VESSEL:check -> SETUP:iterate -> VESSEL:collect` (f33r L6)

All read as coherent procedural steps that could produce a product.

### Preserved Evidence from Original Analysis
The original distributional tests remain valid, reinterpreted:

| Original Category | MIDDLE Group | New Interpretation | Regime Pattern |
|---|---|---|---|
| LUTE_JOINTS | am, y, a, c, om | Terminal vessel operations (finalize, ready) | NWB enriched 2.85x (more finalization in direct-fire) |
| PLUG | aiin, ain, ol, or, edy, al | Active vessel management (check, maintain, collect) | Regime-shared |
| COVER | e, ee, eey, eeo, eed, etc. | Vessel cooling operations | WB enriched 1.45x (more cooling cycles in water bath) |
| UNCOVER | ai, aii, airo | Vessel opening | — |
| CHECK | ch, chd, sh | Vessel inspection | — |

The regime distributions reflect that different operational environments require different vessel management patterns (more cooling in WB, more finalization in NWB), not different sealing types.

## Domain Selector Model

```
PREFIX determines WHAT you're acting on:
  ch/sh  = the PROCESS (testing, monitoring)
  qo     = the HEAT SOURCE (energy management)
  ok     = the VESSEL (apparatus management)
  da/sa  = the SETUP (infrastructure configuration)
  ot/ol  = the ADJUSTMENT (correction, continuation)

MIDDLE determines the ACTION:
  aiin   = check    ->  ch+aiin = test check (verify process)
                        ok+aiin = check vessel (inspect apparatus)
  ar     = close    ->  ch+ar   = test close (verify completion)
                        ok+ar   = close vessel (shut apparatus)
  e      = cool     ->  ch+e    = test cool (monitor cooling)
                        ok+e    = cool vessel (cool apparatus)
  ai     = open     ->  ok+ai   = open vessel (unseal apparatus)
  am     = finalize ->  ok+am   = finalize vessel (seal permanently)
```

## Sister Pair Resolution (C408)

ok and ot are sister pairs (equivalent grammatical slots). Under domain selection:
- ok = proactive vessel management (check, close, cool, maintain)
- ot = corrective adjustment (rectify, correct)

Both target the physical apparatus but from different stances: ok is routine management, ot is corrective intervention. This preserves C408 mutual exclusivity while giving distinct semantic roles.

## Prior Constraints

- C570: PREFIX predicts AX membership (89.6% accuracy) — PREFIX is role selector
- C571: AX = PREFIX-determined scaffold mode — PREFIX selects role, MIDDLE carries material
- C661: PREFIX behavioral transformation (effect ratio 0.975)
- C662: PREFIX narrows class membership by 75-82%
- C911: PREFIX-MIDDLE selectivity (ok selects e-family + infrastructure, forbidden k-family)
- C466: PREFIX encodes control-flow participation
- C382: Morphology encodes control phase
- C267: Tokens are compositional

## Falsification

Would be falsified if:
1. ok tokens do NOT preferentially co-occur with same-MIDDLE other-PREFIX tokens on the same line (pairing rate < random baseline)
2. ok tokens show no positional bias (mean position within 0.02 of overall prefix mean)
3. An alternative verb-based interpretation produces equally or more coherent procedural readings across all regimes
4. C911 forbidden combinations for ok are shown to be arbitrary (no physical explanation under any domain interpretation)
