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
| f31r | R1 | Herbal H | Rosewater candidate; highest e_ratio in R1 (0.654); P2 48% monitoring spike; illustration plausibly rose | [f31r.md](f31r.md) |
| f46v | R4 | Herbal H | Precision sublimation candidate (thistle salt); highest h_ratio in R4 (0.262); max dam density (2.70%); illustration = thistle | [f46v.md](f46v.md) |
| f55r | R2 | Herbal H | Aggressive iterative oil extraction (poppy?); only ENERGY_DOMINANT folio in Section H; k=0.545; illustration = poppy plant | [f55r.md](f55r.md) |
| f50r | R2 | Herbal H | Highest iteration in Section H (4.35%); OIL output; BALANCED kernel; large ray-floret flower (sunflower-like?) | [f50r.md](f50r.md) |
| f41v | R4 | Herbal H | Most distinctive folio in Section H (z=13.75); extreme terminal_rate (48.4%); very high e_ratio (69.2%); tiny (68 tokens); feathery leaves + tuberous roots | [f41v.md](f41v.md) |
| f40v | R2 | Herbal H | Highest paragraph density in Section H (19 para/106 tokens); iterative; borderline R2; ornate flower with thick striped calyx | [f40v.md](f40v.md) |
| f77v | R1 | Herbal B | Ch27 match (furnace specification, three fire regimes); strongest ratio in Phase 628 (2.805); qo-dominant (29%); all paragraph gallows are t; thermal gradient P3→P7 maps bath→ashes→flame | [f77v.md](f77v.md) |
| f84r | R1 | Herbal B | Ch14 match (gold dissolution, balneum mariae + putrefaction); dual-layer 12-header architecture; lowest distance in dataset (0.723); 84% CV consensus | [f84r.md](f84r.md) |
| f108r | R1 | S (Pharma) | Ch16 match (two-phase element separation); blind prediction test FAILED (1/8); ok+ot correction rate 22.4%; zero iteration | [f108r.md](f108r.md) |
| f112r | R1 | S (Pharma) | Ch11 match (red mercury tincture); ok escalation 5%→27% matches recipe monitoring shift; zero dar (cohobation only); 10 paragraphs / 10 recipe steps | [f112r.md](f112r.md) |
| f84v | R1 | Herbal B | Ch24 match **REJECTED** — single-sentence recipe vs 347-token folio; statistical false positive | [f84v.md](f84v.md) |
| f81v | R1 | Herbal B | Ch18 Mercuriorum match (potable gold); dar+dal on L1 (gold+water); daiin x9 all in P1 (cohobation); weak stats but operationally coherent | [f81v.md](f81v.md) |
| f82r | R1 | Herbal B | Ch22 Mercuriorum match (lunaria maceration); dar=1 for lunaria; **5-token sealing micro-para (P3)**; 12 consecutive qo lines = 3-day maceration; cleanest non-confirmed match | [f82r.md](f82r.md) |
| f75v | — | — | Codicillus mercury preparation candidate | [f75v.md](f75v.md) |

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
