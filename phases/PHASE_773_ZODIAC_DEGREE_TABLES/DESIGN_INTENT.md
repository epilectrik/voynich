# PHASE_773 — Zodiac figures against medieval degree tables: design intent

**Written and committed before either input has been looked at:**
- the blind figure codes (`data/nymph_attributes.json`, still being produced by a coding agent that has not been told
  the hypothesis);
- the degree tables' contents (`data/degree_tables.json`, collected by a separate agent kept away from all Voynich
  data).

Claude has read neither file's contents. This note fixes the comparisons in advance. The full pre-registration,
lean-expert audit and lock follow before any comparison is computed.

## Question
Do the attributes of the figures on the zodiac pages follow the traditional per-degree tables of medieval astrology,
read one figure per degree? Each sign has 29–30 labelled figures.

If they do, the figures and their labels map onto known degree qualities. That would be an external anchor, the crib
this project has never had.

## Pre-specified pairings
Each pairing is chosen for a plain semantic motivation, fixed now.

| # | Degree table | Figure attribute | Motivation |
|---|---|---|---|
| P1 | **pitted degrees** (*putei*, "wells, pits") | the figure is in, on or beside a barrel or tub | a well or pit, and a vessel of water |
| P2 | **light degrees** (*lucidi*) vs dark, smoky and void | the figure holds a star | stars as light; a void degree as an empty hand |
| P3 | **degrees increasing fortune** | the figure is crowned | a crown as fortune or honour |
| P4 | *(exploratory, lower priority)* **masculine vs feminine degrees** | clothed vs naked | no strong motivation; will be reported as exploratory |

No other pairing will be tested confirmatorily.

## Planned structure (details to be fixed in the pre-registration)
- **Order-free statistic.** Across the 10 signs, the per-sign count of the attribute against the per-sign count of the
  degree category, for P1–P3.
- **Positional statistic.** Agreement between the attribute and the category along the degree order, maximised over a
  small declared family of reading orders:
  - bands outer→inner or inner→outer;
  - clockwise or counter-clockwise;
  - the start at 12:00 or at the ring's written start marker;
  - which page comes first for the two-page signs (Aries, Taurus).
- **Nulls:**
  - degree tables permuted across signs;
  - circular shifts of the degree order within a sign;
  - the same maximisation inside the null.
- **Sources:** the primary is al-Qabisi (the widely used medieval textbook). Bonatti, Leopold of Austria and Lilly are
  sensitivity sources.
- **Multiplicity:** Bonferroni over P1–P3 for the confirmatory calls.
