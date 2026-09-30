# PHASE_775 — Is Currier B's word-boundary rule the key of a context-keyed cipher? (rank decoding)

**Status: LOCKING.** The pre-registration is v3, after these steps:
1. **Design calibration** (all keyed ciphers had a positive key gain; all no-key controls a negative one).
2. **Certification on disjoint segments.** It FAILED R1: 4 of 12 in-scope keyed ciphers were missed. v2 therefore made
   both arms one-sided (PRESENT only), with no re-tuning.
3. **A lean-expert lock audit:** LOCKABLE WITH EDITS. It added 37 no-key plants and none reached PRESENT; the edits are
   applied.

**Nothing has been computed on B's token order.**

## Question (from the human's challenge: a new, text-only test)
B's strongest rule couples each word's beginning to the previous word's ending. If that rule is the key of a cipher
whose alphabet switches with the previous ending, replacing each word by its frequency rank among the words that
follow the same ending ("rank decoding") would realign the hidden units.

## Locked design (summary)
- **Statistic:** the key gain G_K. It is the mutual information of consecutive rank-decoded symbols (key K1, the last
  glyph; or K2, the last two glyphs), minus the same with global ranks, net of a header-aware exact edge-frame null.
- **Calls:** PRESENT at G_K1 ≥ 0.0033 or G_K2 ≥ 0.0041, with p ≤ 0.005. Otherwise not PRESENT, which is descriptive
  only.
- **Specificity:** no PRESENT in 98 no-key controls.
- **Sensitivity:** partial. 8 of 12 held-out keyed ciphers were detected, and no keyed B-like habit stream was.
