# f66r as Character-Key / Glossary Page — FALSIFIED

**Status:** FALSIFIED (2026-05-15)
**Previously:** Tier 4 interpretive synthesis (2026-05-04)
**Phase:** 684 (proposed), Phase 685+ (falsified via diagnostic tests)

---

## Retraction notice

The "f66r is a character-key / glossary page" interpretation **does not survive diagnostic testing**. The structural anomaly that motivated the interpretation (C1992) is real and confirmed; the interpretation of that anomaly as a glossary is falsified.

This file is preserved for traceability. The synthesis below remains historically interesting but should NOT be treated as supported. **Do not cite this interpretation.**

---

## What was claimed (now falsified)

The original synthesis claimed:
- f66r contains M-column atom-markers that classify L-column labels by operational role
- The atom-gloss header→content prefix correspondence (C1993) showed this systematically
- 11/15 corpus-singular L-labels = "definitions" of rare terms; 4/15 heavily cross-referenced = "terms used elsewhere"
- f66r served as the manuscript's "internal Rosetta Stone"

## What killed it (2026-05-15 diagnostic tests)

After expert push-back (both expert-advisor and crazy-expert independently flagging the claim as over-fit), three pre-registered diagnostic tests were run:

### Test 1: Frequency-matched null on 11/15 singleton split — **PASS**
- 10,000 random samples of 15 line-initial tokens from comparable B folios
- Null distribution: mean 3.78 singletons, sd 1.67
- f66r observed: 11/15, z=4.32, p=0.0001
- **f66r IS singleton-heavy** — not a hapax baseline artifact.

### Test 2: L1-L15 vs L16-L32 R-body structural equivalence — **FAIL**
- JSD between zones: 0.1043; random-split null mean 0.0706
- Observed at 95.5th percentile, p=0.045
- L1-L15 is ch/qo/ok-heavy; L16-L32 shifts to sh/ot/ol-heavy
- **f66r is at minimum TWO structurally distinct zones**, not a single glossary

### Test 3: M-marker dominance on 4 cross-referenced labels — **FAIL hard**
- Predicted: f66r-assigned M-marker should be top-1 dominant neighborhood class
- rary [M=y]: top is o, k. y not in top-3.
- qor [M=s]: top is ch, l, o, r. s not in top-4.
- raiin [M=d]: top is o, ch, l, sh. d not in top-4.
- qokal [M=sh]: top is o, ch, sh (3rd), d.
- **0/4 top-1 matches. 1/4 top-3.**
- The M-column does NOT classify L-labels by operational neighborhood.

## What survives

- **C1992 stays.** The structural singleton fact (88% short-start, z=11.11) is reinforced by Test 1.
- **f66r is structurally anomalous.** This was never in dispute.
- **L1-L15 and L16-L32 are structurally distinct zones.** New finding from Test 2. Plausibly absorbed by C1287 paragraph-header enrichment over a folio with unusually many short paragraphs — testable separately.

## What does NOT survive

- **C1993 retracted as Tier 1 falsification** (2026-05-15). Strict pre-reg failed in Phase 684 (2/4 with sh-inverted); Test 3 failed worse (0/4 top-1). The cross-folio specificity (1/46) that justified Tier 3 is now reinterpreted as a multiple-comparison artifact — f66r is structurally unique on many axes, so uniquely passing any pattern test is unsurprising.
- **"f66r is a character-key / glossary / Rosetta Stone"** — falsified.
- **"qokal is a named procedure cataloged by f66r"** — falsified.

## Most probable alternative readings (updated posterior, crazy-expert)

- 50% Annotation overlay (two co-occurring patterns we conflated)
- 20% Structurally unique reference card / condensed procedure
- 15% Practice page / scribal exercise
- 10% Index page with broken/unmatched pointers
- 5% Other glossary-like, not C1993-shape
- ~0.5% C1993-as-registered

## Methodological lesson

This is the fourth instance of the operational-story-first trap (per `memory/feedback_operational_story_first_trap.md`). The trap signature here:
1. Real structural anomaly (C1992, z=11)
2. Cleanly-structured story that fits the anomaly (3-column glossary)
3. Cherry-picked corroborating test (qokal anchor at 1.44× sh enrichment)
4. Pre-registration failure rationalized via post-hoc cross-folio specificity
5. Discriminating test (run weeks later) kills the story

The fix proposed by both experts: when a finding fits existing tier-2 operational glosses (C1195, C1394, etc.) and uses their interpretive language, treat the existing fit as a *prior toward null* — the operational vocabulary itself can produce the appearance of signal in the data. At this stage of the project, framework-fit is evidence of confirmation bias, not confirmation.

## Files

- Original Phase 684 INDEX: `phases/PHASE_684_F66R_KEYPAGE/INDEX.md` (update to reflect retraction)
- Diagnostic tests: `phases/PHASE_684_F66R_KEYPAGE/scripts/_three_diagnostic_tests.py`
- Results: `phases/PHASE_684_F66R_KEYPAGE/results/three_diagnostic_tests.log`
- Memory note: `memory/feedback_operational_story_first_trap.md` (extend with f66r case)
