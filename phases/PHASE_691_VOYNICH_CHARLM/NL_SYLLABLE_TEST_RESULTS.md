# Results: the decisive test of the syllable-segmentation NL theory

**OFF-BOOKS / FUN / EXPLORATORY. No constraint registered.** 2026-06-16.
Pre-reg + design: experts' convergent proposal (syllabify NL, test static stats + C2032).

## Verdict: my own theory FAILS — on the cleanest, most robust statistics, exactly as predicted.

I assumed the manuscript is natural language and proposed that **Voynich spaces mark syllables,
not words**, so the famous low entropy is a "unit-mismatch artifact." Built the adversarial test
with external grounding (real Latin/Italian/German corpora). Three robust static results kill it:

| metric | Voynich-B | NL **words** | NL **syllables** | reading |
|---|---|---|---|---|
| mean token length | **5.15** | 4.90–6.47 | 2.55–3.13 | Voynich tokens are **word-sized** |
| type/token (TTR) | 0.21 | 0.15–0.42 | 0.024–0.055 | Voynich is **word-range**, 4–8× above syllable-range |
| char h2 (bits) | **2.20** | 3.41–3.87 | 3.41–3.87 (identical) | low-entropy gap is **segmentation-INVARIANT** |
| adjacent repetition | **0.009** | 0.000–0.005 | 0.001–0.004 | Voynich repetition is **intrinsic** |

1. **Tokens are word-sized, not syllable-sized.** If spaces marked syllables, Voynich tokens would
   be ~2.6 chars like NL syllables. They're 5.15 — squarely in the NL *word* range. The theory's
   central premise is simply false at the descriptive level.
2. **The low-entropy anomaly is character-level and segmentation-invariant.** NL char-h2 is identical
   whether you segment into words or syllables (the glyph stream is unchanged), and it stays ~1.2–1.7
   bits *above* Voynich regardless. Re-imagining where the word boundaries fall **cannot** touch it.
   My "unit-mismatch" reframe — the heart of the theory — collapses. (lean-expert called this exactly:
   the strong entropy results live in the glyph stream, where segmentation is irrelevant; cf. C2015.)
3. **Repetition is intrinsic**, higher in Voynich than in NL under *either* segmentation — not a
   by-product of any segmentation choice.

So: whatever Voynich is, the **space is a meaningful word-level boundary**, and the low entropy must
come from *within-token redundancy* (verbose-cipher-like), not from sub-lexical segmentation.

## What survives, and the real open question
The syllable theory dies, but the experts' deeper point stands: the **verbose/expansion cipher** is
the strongest NL-encoding consistent with these stats (low entropy from redundant multi-glyph groups;
rigid slots = group framing; repetition = repeated plaintext letter). Its one failure — and the field's
genuine unsolved hole — is reconciling the **low character entropy** with the **~8,000 open productive
types**: cipher buys the entropy but not the type count; open morphology buys the type count but not the
entropy. No single NL-encoding squares the two. That, not segmentation, is what we're missing.

## A flag for a separate audit (NOT a verdict)
While replicating the C2032 −0.66 "period-2" discriminator I could **not** reproduce −0.66 on *full*
Currier B with the canonical heat-cycle-MIDDLE-class metric — I got **r21 = +0.70 (persistence)**.
The registered −0.66 is specific to the matched-folio subsets (`MATCHED_B`/`MATCHED_S`) under length
stratification, and the r21 ratio is brittle (it divides by a near-zero lag1). Also: the e-depth channel
itself *persists* (+0.27), so the −0.66 is a MIDDLE-stem-class phenomenon, not an e-depth one. This is a
**lead for a proper, verdict-gated audit of C2032's robustness**, not a claim that C2032 is wrong — an
exploratory non-replication is not an adversarial verdict on a Tier-2 constraint.

## Files
- `scripts/syllable_nl_test.py` (static stats — the decisive ones), `syllable_nl_test2.py` (e-depth),
  `syllable_nl_test3.py` (canonical heat-cycle metric)
- `results/predictions/syllable_nl_test.json`
