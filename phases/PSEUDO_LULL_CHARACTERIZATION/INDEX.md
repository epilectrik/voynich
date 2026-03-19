# Phase 602: PSEUDO_LULL_CHARACTERIZATION

**Status:** COMPLETE
**Verdict:** STRUCTURAL_PROFILE_EXTRACTED (characterization-only, no alignment)
**Constraints:** None (characterization phase — no Voynich claims)
**Script:** `scripts/pseudo_lull_characterization.py` (4.5s)
**Results:** `results/pseudo_lull_structural_profile.json` (235 KB)
**Extraction Protocol:** `EXTRACTION_PROTOCOL.md` (frozen before execution)

## Motivation

The Brunschwig alignment (Phases 598-601) confirmed safety substitution within Stars but failed to reach the Voynich's midprocess control layer (C1056). Brunschwig describes *what* to collect but not *how to monitor, adjust, and terminate* a process in progress. Pseudo-Lull's Testamentum contains explicit midprocess monitoring, iterative termination conditions, coded letter-based operational notation, correction/recovery logic, and operator judgment cues — exactly the structural features Brunschwig lacks.

**Design principle (from Brunschwig lesson):** Characterize first, align second. This phase extracts and formalizes 8 structural features of pseudo-Lull on its own terms. No Voynich data is loaded or compared. Phase 603 will use this output for alignment testing.

## Source Material

| Source | Edition | Content | Size |
|--------|---------|---------|------|
| Testamentum (1566 Cologne/Byrckmann) | Theorica (96 ch), Practica (32 ch), Compendium, Index | 513 pages |
| Liber Mercuriorum (1567 Cologne/Byrckmann) | 52 chapters on mercury preparations | 179 pages |
| Practica de Furnis (1600 Basel) | 27 chapters + Elucidatio (6 ch) | 79 pages |

English translation: `testamentum_complete_english.txt` (6,738 lines, 953 KB)
Latin transcription: `testamentum_complete_latin.txt` (12,957 lines, 863 KB)

## Extraction Targets and Results

### E1: Chapter Structure Inventory
- **209 chapters** detected: 96 Theorica + 32 Practica + 51 Mercuriorum + 30 Furnis
- Mercuriorum: 2 chapters (34, 41) genuinely missing from source edition
- Furnis: includes 27 core + 3 Elucidatio chapters detected
- Theory/practice split: 60 theoretical, 78 mixed, 71 practical

### E2: Symbolic-Letter Operational System
- **667 cipher-letter occurrences** across operational text
- **355 with operational context** (co-occurring with operational verbs)
- **23 active letters**: A B C D E F G H I K L M N O P Q R S T V X Y Z
- **50 multi-letter sequences** (bundles like H.I.K.)
- Top frequency: H (83), E (57), D (51), C (49), L (49)
- H (pure gold) is the most-referenced cipher letter — gold is the target product

### E3: Monitoring Passages
- **316 monitoring passages** (color: 88, consistency: 175, volatility: 133)
- **247 action-triggering** observations (78% — most monitoring directly drives decisions)
- 65 descriptive, 4 purely diagnostic
- **247 monitor->action chains** extracted

### E4: Termination Conditions
- **196 termination conditions**
- **Dominant type: threshold-based (139, 71%)** — "until it turns white", "until it flows like wax"
- Externally judged: 35, count-based: 10, time-dependent: 8
- **101 require operator sensory judgment** (51.5%)
- Only 18 bounded (predetermined endpoint) — 91% are open-ended or state-dependent

### E5: Heat Regime Inventory
- **585 heat passages** across the corpus
- **12 functionally distinct heat modes**: balneum mariae (33), ash fire (16), solar heat (16), gentle fire (12), open fire (5), strong fire (4), cupellation (4), dung fire (3), crucible (2), sand bath (2), athanor (2), tripod of secrets (1)
- **38 heat transitions**: 19 increase, 9 decrease, 10 unspecified direction
- Heat management is rich and varied — 12 modes exceeds what Brunschwig describes

### E6: Correction/Recovery Procedures
- **181 correction passages**
- Failure sources: process drift (85), unspecified (39), combustion (26), irrecoverable (25), apparatus failure (5), false practitioners (1)
- **156 recoverable, 25 irrecoverable** (86% recovery rate)
- Correction ratio: 0.4 (many failure types but relatively few distinct correction strategies)
- "Start over" is surprisingly rare — most failures have in-process recovery paths

### E7: Operation-Family Taxonomy
- **13 distinct operation families** represented (of 14 checked)
- Primary families: theoretical (127), distillation (16), dissolution (15), separation (13), fixation (10), sublimation (7), fermentation (6), coagulation (6), furnace/apparatus (5), calcination (1), imbibition (1), circulation (1)
- Mercuriorum has the highest operational diversity: distillation (12), separation (5), fixation (4), sublimation (4)
- **Pseudo-Lull covers the full alchemical operational envelope** — not just distillation

### E8: Operator Judgment Cues
- **96 judgment cues** extracted
- Types: "you will find" (36), "know that" (19), "note that" (9), "you will see" (9), "if you see" (9), "sign of" (8), "you shall know" (3), "take care" (2), "judge by" (1)
- **61 formalized (63.5%)** — explicit threshold or observable specified
- **35 discretionary** — left to operator judgment
- Consequences: continue (42), proceed (23), stop (18), correct (7), adjust (5), abort (1)

## Derived Summaries

| Metric | Value |
|--------|-------|
| Operational chapters | 149 (71%) |
| Theoretical chapters | 60 (29%) |
| Heat granularity | 12 distinct modes |
| Correction-to-failure ratio | 0.4 |
| Termination: state-dependent | 71% (threshold-based) |
| Termination: needs judgment | 51.5% |
| Judgment cues: formalized | 63.5% |
| Cipher alphabet size | 23 letters |
| Active cipher letters in operations | 23 |

## Key Structural Observations

1. **Rich midprocess control layer.** 316 monitoring passages with 247 action chains — this text verbalizes the observation->decision->action loop that the Voynich may structurally constrain (C1056).

2. **State-dependent termination dominates.** 71% of termination conditions are threshold-based ("until white"), not count-based ("seven times"). This is a feedback-loop architecture, not a fixed recipe.

3. **Half of all decisions require operator judgment.** 51.5% of termination conditions and 36.5% of judgment cues are discretionary. The system depends on the operator's ability to read process state.

4. **12 heat modes, not just "fire."** The heat management vocabulary distinguishes balneum mariae, ash fire, dung fire, solar heat, athanor, and others. This exceeds Brunschwig's heat vocabulary.

5. **Recovery architecture is forgiving.** 86% of failures are recoverable. The text assumes operators WILL make errors and provides correction paths rather than demanding perfection.

6. **Full operational envelope.** 13 operation families including distillation, sublimation, calcination, fixation, dissolution, coagulation, circulation, imbibition, fermentation, and projection. Not just "boil and collect."

## What This Phase Does NOT Do

- No Voynich data loading or comparison
- No statistical testing or hypothesis testing
- No alignment claims or constraint registration
- No symbol-to-symbol mapping
- Pure structural description — alignment is Phase 603
