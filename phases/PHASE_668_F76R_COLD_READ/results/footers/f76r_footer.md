## Cross-Paragraph Patterns

### e-depth Thermal Arc

| Para | Lines | Tokens | e-depth | Recipe phase |
|------|-------|--------|---------|-------------|
| P1 | 1-29 | 357 | 0.599 | Sevenfold distillation (aquatic, balneum-level) |
| P2 | 30-34 | 58 | 0.500 | Rectification / air processing |
| P3 | 35-40 | 65 | 0.462 | Calcination (direct fire, hot, dry) |
| P4 | 41-47 | 66 | 0.576 | Product recovery / final operations |

The two-regime thermal structure is clear: P1-P2 (distillation, e-depth 0.50-0.60) vs P3 (calcination, e-depth 0.46). The recipe explicitly describes two heat modes — "foch calcinant" (calcining fire) for earth+fire, and aquatic distillation for water+air. The folio's e-depth tracks this: P3 has the lowest e-depth (least cooling stabilization, most direct fire), while P1 has the highest (most cooling stabilization, balneum-level gentle heat).

### dar Distribution

| Para | dar | % | Recipe phase |
|------|-----|---|-------------|
| P1 | 19 | 70% | 7-pass distillation with dregs removal at each pass |
| P2 | 4 | 15% | Rectification material handling |
| P3 | 1 | 4% | Calcination (minimal material — direct fire on earth) |
| P4 | 3 | 11% | Product collection and recovery |

The dar concentration in P1 (70%) directly tracks the recipe's most material-intensive operation: sevenfold distillation where "les feces de l'aygua posaràs ab la terra" (put water's dregs with the earth) at each pass. 19 dar across 29 lines = roughly one material-handling event every 1.5 lines, consistent with iterative distill-then-remove-dregs cycling. P3 (calcination) has only 1 dar — calcining is a fire-only operation with minimal material handling, exactly as the recipe describes.

### Observation MIDDLE Distribution

| Para | ckh | cth | ecth | cfh | Total | Density |
|------|-----|-----|------|-----|-------|---------|
| P1 | 10 | 4 | 2 | 1 | 17 | 4.8% |
| P2 | 2 | — | 1 | — | 3 | 5.2% |
| P3 | 4 | — | — | — | 4 | 6.2% |
| P4 | — | — | 1 | — | 1 | 1.5% |

P3 (calcination) has the highest observation density (6.2%) with 4 ckh (temperature checks) and zero transfer-watches. This is physically correct: calcination requires careful temperature monitoring (too hot burns the tincture, too cold doesn't calcine) but involves no material transfer. P1's observations are more diverse (ckh + cth + ecth + cfh) — the seven-pass distillation requires monitoring temperature, transfer rate, and cooled intermediates.

### Prefix Shift: P1 → P3

| Prefix | P1 (distillation) | P3 (calcination) | Shift |
|--------|-------------------|-------------------|-------|
| qo (fire) | 21% | 9% | Fire management drops |
| ok (vessel) | 6% | 17% | Vessel management triples |
| ot (output) | 3% | 8% | Output monitoring rises |

The P1→P3 prefix shift encodes the operational difference between distillation and calcination. Distillation is fire-focused (manage the heat source continuously). Calcination is vessel-focused (manage what's happening inside the vessel under direct fire). This shift was identified by the expert positive control as one of the strongest discriminative features.

---

## Verdict: COHERENT

f76r produces a coherent structural reading against II.16.0 (element separation via sevenfold distillation). The folio's 4 paragraphs map to the recipe's operational phases:

1. **Sevenfold distillation** (P1, 357 tokens, 65% of folio) — the massive main paragraph encoding all 7 distillation passes with dregs removal. 19 dar tokens (~1 per 1.5 lines), e-depth 0.599 (balneum-level), ckh×10 for continuous temperature monitoring.
2. **Rectification** (P2, 58 tokens) — secondary processing of the distilled product. e-depth drops to 0.500.
3. **Calcination** (P3, 65 tokens) — direct fire on earth+fire elements. Lowest e-depth (0.462), ok-prefix triples to 17%, only 1 dar (fire-only operation).
4. **Product recovery** (P4, 66 tokens) — collecting the water of life. e-depth rebounds to 0.576.

**Honest gaps:** No ×7 counting anchor — the scribe did not encode "septena" as a counted token run (C1965 counting shorthand doesn't generalize). Only 4 paragraphs for a recipe with 7+ distinct steps — the scribe compressed the entire distillation cycle into one paragraph rather than encoding each pass separately.

**Negative control:** f82r ↔ II.16.0 (wrong folio) scored 0/6 INCOHERENT — the expert found no counting anchor, no silver-plate test, no calcination phase, and P5's double-okain is a III.19.3 diagnostic, not an II.16.0 feature.
