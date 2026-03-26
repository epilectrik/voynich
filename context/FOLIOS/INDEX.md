# Folio Notes Index

Per-folio findings from individual analysis. Each file captures structural properties, recipe correspondences, unique features, and exploratory results that would otherwise be lost across sessions.

**Scope:** Only folios that have been individually investigated get a file here. This is not a catalog of all 83 B folios — it's a working notebook for folios with non-trivial findings.

**Rule:** Findings recorded here should cite their source (phase number, script name, constraint number). No uncited claims.

---

## Documented Folios

| Folio | REGIME | Section | Key Finding | File |
|-------|--------|---------|-------------|------|
| f75r | R1 | Herbal B | Ch19 match (aqua vitae, 9x reflux); only 4+ token run in corpus; double-dar unique | [f75r.md](f75r.md) |
| f76r | R1 | Herbal B | Ch18 match (element separation, silver-plate test); strongest monitoring gradient in corpus (rho=0.710, rank 1/13); ch-dominant (active test) | [f76r.md](f76r.md) |

---

## Template

When adding a new folio, copy this structure:

```markdown
# f__r/v — [one-line summary]

## Identity
- **REGIME:** R_
- **Section:** [Herbal A/B, Pharma, Astro, etc.]
- **Lines:** N
- **Paragraphs:** N (gallows-delimited)
- **Tokens:** N

## Recipe Correspondence (Phase 628)
- **Matched PL chapter:** Ch__ (idx=__, family=__)
- **Distance:** __.___
- **Ratio:** __.___
- **Confident:** yes/no
- **CV consensus:** ___%
- **Recipe summary:** [one-line]

## Structural Properties
[Anything notable about this folio's grammar, token distribution, etc.]

## Unique Features
[Hapax legomena, unusual runs, PREFIX anomalies, etc.]

## Exploratory Findings
[Crib decode results, paragraph-level analysis, etc.]

## Open Questions
[What remains to be tested]

## Sources
[Phase numbers, script paths, constraint citations]
```
