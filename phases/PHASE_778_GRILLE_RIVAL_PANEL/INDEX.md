# PHASE_778 — Rival-generator panel II: the table-and-grille method

**Status: DESIGN (v2 after the lean-expert design audit); fit stage running; not locked.**
- **Question:** can the table-and-grille method (Rugg 2004; Hyde & Rugg 2014; Rugg & Taylor 2016; Zandbergen 2021),
  with its composition fitted to Currier B, produce an ensemble containing B on the PHASE_757 discriminators D2–D6?
- **Why now:** the strategic review's rival panel (Naibbe done, C2080 EXCLUDED; Timm earlier, C2077 EXCLUDED); the
  grille is the next named rival. Improvisation in a practised script at book scale stays untested.
- **Generator:** `scripts/grille778.py`, implemented from the published mechanics (quotations verified against the
  Hyde & Rugg page): a prefix | root | suffix table of R rows and G column sets, a three-hole grille, the next word
  three cells across plus an arbitrary vertical move, back to the first column set at each new line, repeats kept or
  avoided, several tables and grilles. Three tiers: PUBLISHED (as described), EXTENDED (published sources beyond the
  description, plus the public implementations' per-word random placement), STEELMAN-EXPOSED (chain rows and junction
  redraw built from B's edge-glyph bigram table; D2 built in and not counted).
- **Gates PASSED:** page reproduction from a page-built table (Zandbergen's equivalence), exact binomial word lengths
  from 24-fragment wheels.
- **Fit stage:** composition only (nine statistics; bands FITTED ≤ 1.0 / PARTIAL ≤ 2.0 / UNFITTED); one fit per walk
  group shared across row arrangements; a declared grid extension toward richer tables.
- **Panel:** PHASE_757's skeleton, noise, controls and discriminators unchanged; 65 families × 2 noise = 130 variants,
  N = 1,000, pooled rerun of non-excluding variants; per-tier verdicts; pre-lock controls C1–C5.
- Pre-registration: `PRE_REGISTRATION.md`.

## Result on Currier B
Pending the lock and the run.
