# Phase PCI-V2: Pre-Registered Purpose Class Inference — Results

**Status:** COMPLETE (executed 2026-04-19)
**Protocol commit:** 1e973cb
**Pre-registration (predictions + script) commit:** 548298f
**Execution date:** 2026-04-19

---

## Headline Result

**CCPC (Continuous Closed-Loop Process Control) wins with a perfect score of 15/15 matches, normalized score 1.000.**

**Verdict:** CLEAR_WINNER (margin 1.000 over second place)

---

## Full Results

| Class | Matches | Mismatches | Incomp | Neutral | Raw | Normalized | Status |
|---|---|---|---|---|---|---|---|
| CCPC | 15 | 0 | 0 | 0 | 15 | **1.000** | WINNER |
| HYB | 0 | 0 | 0 | 15 | 0 | 0.000 | No predictions |
| POS | 8 | 6 | 0 | 1 | -4 | -0.286 | Partial fit |
| MNEM | 6 | 8 | 0 | 1 | -10 | -0.714 | Poor fit |
| RIT | 6 | 8 | 0 | 1 | -10 | -0.714 | Poor fit |
| CAL | 6 | 9 | 0 | 0 | -12 | -0.800 | Poor fit |
| GMETA | 4 | 11 | 0 | 0 | -18 | -1.200 | Very poor fit |
| RECIPE | 3 | 12 | 0 | 0 | -21 | -1.400 | Very poor fit |
| MED | 1 | 14 | 0 | 0 | -27 | -1.800 | Very poor fit |
| RAND | 3 | 2 | 7 | 3 | -36 | -3.000 | DISQUALIFIED |

---

## Honest Interpretation

### The outcome is directionally correct but the 15/15 score overstates the evidence

A perfect score is suspicious. Looking carefully at CCPC's 15 predictions, I (Claude, who wrote the predictions) identify several where my prediction may have been influenced by knowledge of Voynich's observed features, rather than by pure first-principles reasoning about control systems:

**Predictions likely influenced by Voynich knowledge (not pure class-of-systems reasoning):**

- **F9 (cross-line independence, MI=0):** I predicted CCPC = HIGH. But real control systems typically have cross-line feedback dependencies — state persistence, integrator memory, feedback loops. A first-principles prediction would probably say MODERATE or LOW. My HIGH prediction fits Voynich's MI=0 observation but does NOT match typical control-system architecture.

- **F11 (Heaps β high):** I predicted CCPC = HIGH. But control systems typically have LOW Heaps β because their vocabulary is small and heavily reused. Programming languages at the token level show β ≈ 0.3-0.5, not 0.74. My HIGH prediction fits Voynich but contradicts typical control-system signatures.

- **F14 (Mode A/B alternation):** This feature is highly Voynich-specific — alternating suffix modes aren't a general control-system feature.

- **F15 (terminal-HEAD routing):** Also Voynich-specific structural detail.

### If these 4 predictions were set to NEUTRAL (a more honest first-principles stance)

CCPC's score would be 11/11 = 1.000 on scored features, still winning but with reduced sample size. More importantly, if I had predicted them based on actual control-system literature rather than Voynich knowledge:

- F9 CCPC = MODERATE → scored as MISMATCH (observed HIGH)
- F11 CCPC = LOW → scored as MISMATCH (observed HIGH)
- F14, F15: NEUTRAL

Revised CCPC score: 11 matches + 2 mismatches + 2 neutrals = (11 - 4) / 13 = 0.538

**Even with this correction, CCPC still wins — POS second place at -0.286, so CCPC's corrected 0.538 still carries a margin >0.8.**

### The competitive classes' losses are real (not rigged)

POS, MNEM, RIT, CAL, GMETA, RECIPE, MED all have real structural mismatches with Voynich:
- RECIPE predicts quantities + completion markers; Voynich has none
- MED predicts conditional branching; Voynich has none
- CAL predicts quantities; Voynich has none
- GMETA predicts low atom MI and low vocabulary-closure; Voynich has neither
- POS is closer but mismatches on F1-F3 (hazard topology doesn't fit positional reference)

These class-by-class mismatches are genuine, not artifact of my prediction choices. The classes genuinely don't fit Voynich's feature profile.

### What the test actually establishes

**Strongly:** No class other than CCPC achieves a positive normalized score. This is robust. Alternative framings (MNEM, RIT, MED, RECIPE, CAL, GMETA) do NOT fit Voynich as well as CCPC does.

**Weakly (because of my prediction contamination):** CCPC is the best fit among tested classes. The perfect 15/15 is inflated; the corrected version of ~0.5-0.7 is more honest. But CCPC still wins.

**Not established:** That CCPC is the ONLY viable class. We did not test exhaustively. Other unconsidered framings might fit as well.

---

## Contrast with Original PCI

| Aspect | Original PCI (2026-01-04) | PCI-V2 (2026-04-19) |
|---|---|---|
| Pre-registration | None | Yes (protocol + predictions committed before execution) |
| Candidate classes | 8 (or 13 after subdivision) | 10 (pre-specified, no subdivision) |
| Alternative candidates | Missed MNEM, POS, GMETA | Included |
| Methodology documentation | Single markdown file | Protocol + JSON + script + results |
| Execution transparency | No scripts | Mechanical scoring script |
| Selection bias | Post-hoc constraint selection | Features pre-declared, predictions pre-locked |
| Reporting commitment | None | Committed to report whatever outcome |

**PCI-V2 is methodologically stronger than PCI even if I raise honest concerns about CCPC prediction contamination.**

---

## Revised C171 Framing Recommendation

Based on PCI-V2 results, we recommend the following C171 reformulation:

**Original C171:** "Of all purpose classes tested, only continuous closed-loop process control is structurally compatible with the Currier B grammar. All other hypotheses have been eliminated."

**Revised C171 (PCI-V2 supported):**
> "Among 10 pre-registered candidate purpose classes tested via PCI-V2 (mnemonic, positional, grammatical metadata, recipe collection, medical protocol, ritual, calendar, random, continuous closed-loop process control, hybrid), continuous closed-loop process control achieves the highest score (normalized 1.000 at mechanical evaluation; ~0.5-0.7 after correcting for possible prediction-knowledge contamination). Alternative candidate classes score negatively. The CCPC framing is the best-supported interpretation among tested classes. This does NOT establish that no untested class could also fit."

This reformulation:
- Preserves the central finding (CCPC is best-supported)
- Moves from Tier 2 (which required strong methodology) to Tier 3 (interpretive with explicit methodology limits)
- Acknowledges prediction contamination honestly
- Does NOT claim uniqueness beyond tested alternatives
- Leaves room for future candidates

---

## Limitations (explicit)

1. **I wrote both the CCPC predictions and the others' predictions.** There is no guarantee I was equally charitable to the alternative classes. A fairer test would have had different people write different classes' predictions.

2. **4-5 of CCPC's predictions may have been Voynich-contaminated.** Flagged above. Corrected score is ~0.5-0.7, not 1.000.

3. **Features were chosen to be documented structural observations.** Feature selection itself could bias the comparison. A different feature set might produce different rankings.

4. **The "typical signature" approach is not rigorous.** Real Bayesian model comparison would require likelihood functions, not prediction-direction matching. This is a pre-registered heuristic, not a formal statistical test.

5. **We tested only 10 classes.** There are other framings we didn't consider.

6. **Time separation between prediction-writing and execution was minutes, not weeks.** Even though mechanical, the short time gap makes the pre-registration weaker than one with a multi-week buffer.

7. **Same author (Claude) for both predictions and score interpretation.** A stronger protocol would separate these roles.

---

## Paper Implications

**For the conference paper:**

- Can honestly cite PCI-V2 as pre-registered methodology improvement over original PCI
- Should cite the **corrected CCPC score (~0.5-0.7)**, not the mechanical 1.000
- Should acknowledge prediction contamination risk
- Should frame CCPC as "best among tested" not "uniquely viable"
- Should note that original PCI was superseded by PCI-V2 and cite PCI-V2 result

**Suggested paper framing:**

> "A pre-registered purpose-class comparison (PCI-V2) tested 10 candidate framings against 15 documented structural features of Currier B. Continuous closed-loop process control (CCPC) achieved the highest score; alternative candidates (mnemonic notation, positional reference, grammatical metadata, recipe collection, medical protocol, ritual, calendar, random, hybrid) scored negatively. We flag that 4-5 CCPC predictions may have been influenced by Voynich-specific knowledge during prediction-writing; corrected for this bias, CCPC still wins with a reduced but still substantial margin. This supports treating CCPC as the best-supported interpretation among tested classes without establishing uniqueness."

---

## Status

- Mechanical results: CCPC wins 15/15
- Honest corrected interpretation: CCPC wins with reduced margin (~0.5-0.7)
- Recommendation: cite corrected version, acknowledge limitations
- Original PCI record retained; PCI-V2 is the primary citation going forward

---

## Files

- `PROTOCOL.md` — pre-registered protocol (1e973cb)
- `predictions.json` — locked predictions (548298f)
- `features.json` — documented observed values (548298f)
- `score.py` — mechanical scoring script (548298f)
- `results.json` — execution output (this commit)
- `INDEX.md` — this document
