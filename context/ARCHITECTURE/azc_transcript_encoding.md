# AZC Transcript Encoding: Physical Diagram Structure

**Parent:** [currier_AZC.md](currier_AZC.md)
**Last Updated:** 2026-01-19 (AZC_INTERFACE_VALIDATION phase)

---

The transcript encodes AZC diagram geometry through **placement codes** and **line numbers**.

## Placement Code Meanings

| Code | Physical Meaning | Typical Tokens |
|------|------------------|----------------|
| **R, R1-R4** | Ring text (concentric circles) | Varies by ring count |
| **S, S0-S3** | Star/spoke OR nymph-interrupted ring | Context-dependent |
| **C, C1-C2** | Circle text (continuous ring) | 10-140 |
| **P** | Paragraph (separate from diagram) | 28-100 |
| **L** | Labels | 2-34 |
| **X, Y, Z** | Other positioned text | Varies |
| **I, O, B, W, U, F, T** | Miscellaneous positions | Rare |

### S-Placement Context Dependency

**CRITICAL:** S-placement meaning varies by folio type:

| Folio Type | S Meaning | Example |
|------------|-----------|---------|
| Non-nymph (f67-f70r) | Radial spokes from center | 8 spokes = 8 S lines |
| Nymph pages (f70v-f73v) | Nymph-interrupted rings | S1, S2 = rings divided by nymphs |

On nymph pages, tokens are placed in ring segments BETWEEN nymph illustrations. The ring is physically interrupted by the nymphs, so it's encoded as S (sectored) rather than R (continuous).

---

## Diagram Type Classification

**Validated by AZC_INTERFACE_VALIDATION (2026-01-19)**

| Type | Folios | Tokens | Description |
|------|--------|--------|-------------|
| **STANDARD_RING** | 12 | 1,109 | Standard concentric ring diagrams |
| **SCATTER** | 2 | 81 | No ring structure (f68r1, f68r2) |
| **SEGMENTED** | 3 | 381 | Divided/segmented rings (f67r1, f67r2, f68v3) |
| **NYMPH** | 12 | 1,330 | Rings interrupted by nymph illustrations |

### Uniformity Finding

All diagram types show **same functional signature** (PREFIX cosine >0.88 to pooled profile):
- STANDARD_RING: 0.9670
- SCATTER: 0.8795 (marginal)
- SEGMENTED: 0.9179
- NYMPH: 0.9710

**Conclusion:** Visual diagram variation is INTERFACE only - same underlying linguistic content.

---

## Line Number Encoding

**Critical insight:** Line numbers encode spatial arrangement, not just sequence:

| Pattern | Line Numbers | Physical Meaning |
|---------|--------------|------------------|
| **Ring/circle** | All same line # | Continuous circular text |
| **Spokes** | N different lines | N radial spoke-lines |
| **Scattered** | 1 token per line | Non-sequential positions |
| **Nymph-divided** | 1 token per line | Tokens between nymphs, each treated as separate position |

### Example: f68r1 (Scatter Pattern)

```
S placement: 29 tokens, 29 different line numbers
→ Each token gets its own "line" because they're scattered in a circular area
→ NOT a ring - tokens spread like "buckshot"
```

### Example: f68r3 (Ring-Spoke Hybrid)

```
C1 placement: 38 tokens, all "line 1" → continuous outer ring
C2 placement: 10 tokens, all "line 1" → continuous inner ring
R placement:  38 tokens, 8 lines     → 8 radial spokes (~5 tokens each)
X placement:  16 tokens              → scattered between spokes
```

### Example: f73r (Nymph with Top Tokens)

```
S0 placement: 4 tokens, 4 lines → 4 tokens at top (ambiguous: tiny ring or line?)
R1 placement: 34 tokens, 1 line → outer continuous ring
R2 placement: 24 tokens, 1 line → middle continuous ring
R3 placement: 8 tokens, 1 line  → inner continuous ring
S1 placement: 16 tokens, 16 lines → nymph-divided ring (1 token per nymph segment)
S2 placement: 10 tokens, 10 lines → innermost nymph-divided ring
```

---

## P-Placement Text: RECLASSIFIED AS CURRIER A

**Validated by TEST 1 (AZC_INTERFACE_VALIDATION, 2026-01-19)**

P (paragraph) text on AZC folios is linguistically **Currier A**, not AZC:

| Metric | P-text vs Currier A | P-text vs AZC Diagram |
|--------|--------------------|-----------------------|
| PREFIX cosine | **0.946** | 0.777 |
| Exclusive vocab types | **57** | 10 |
| Classification | **A-like** | - |

### P-Text Statistics

- **Total tokens:** 398 (12.1% of AZC)
- **Folios with P-text:** f65v, f67r1, f67r2, f68r1, f68r2, f68v2, f68v3, f69r, f70r2

### Recommendation

**Reclassify P-text as Currier A** for analysis purposes:
- Exclude from AZC legality calculations
- Include in Currier A token counts when appropriate
- P-text represents A-like material that happens to appear above AZC diagrams

```python
# Filter AZC to diagram-only (exclude P-text)
azc_diagram = azc_tokens[azc_tokens['placement'] != 'P']
```

---

## Center Token Behavior

**Validated by TEST 3 (AZC_INTERFACE_VALIDATION, 2026-01-19)**

Center tokens (C, C1, C2, L, I, W placements) are **LEGALITY-PARTICIPATING**, not labels:

| Metric | Value | Label Threshold |
|--------|-------|-----------------|
| Single-char tokens | 3.2% | >5% |
| PREFIX sim to ring | 0.9395 | <0.85 |
| Vocab overlap | 30.0% | <30% |

**Conclusion:** Center tokens behave like normal ring text. Include in standard analysis.

**Caveat:** Many center tokens may be MISSING from transcript (not transcribed). Those present are linguistically standard.

---

## Nymph-Interrupted Ring Enrichment

**Validated by TEST 4 (AZC_INTERFACE_VALIDATION, 2026-01-19)**

S-placement tokens on nymph pages show distinct PREFIX profile:

| Position | ok | ot | o | Total o-prefix |
|----------|----|----|---|----------------|
| S-interrupted | 25.4% | 25.1% | 24.5% | **75%** |
| R-continuous | 14.6% | 27.9% | - | ~43% |

**Finding:** Nymph-adjacent positions show o-prefix enrichment. This may encode:
- Proximity to illustration
- Positional semantics (near-nymph = different lexical selection)
- Artist/scribe preference on nymph pages

**Constraint status:** New constraint may be needed for S-position PREFIX enrichment.

---

## Placement Code Statistics (H-track only, diagram text)

After P-text exclusion (2,901 tokens):

| Code | Tokens | % | Notes |
|------|--------|---|-------|
| C | 587 | 20.2% | Generic circle |
| R1 | 483 | 16.7% | Outermost ring (Zodiac) |
| R2 | 413 | 14.2% | Second ring |
| R | 235 | 8.1% | Generic ring (A/C family) |
| R3 | 208 | 7.2% | Third ring |
| S1 | 199 | 6.9% | First nymph-divided |
| S2 | 146 | 5.0% | Second nymph-divided |
| S | 139 | 4.8% | Generic star/spoke |
| Y | 111 | 3.8% | Other position |
| X | 77 | 2.7% | Other position |
| L | 68 | 2.3% | Labels |
| R4 | 43 | 1.5% | Fourth ring (rare) |

### Subscript Usage by Family

| Family | Uses Subscripts | Example Codes |
|--------|-----------------|---------------|
| **Zodiac (Family 0)** | Yes | R1, R2, R3, S1, S2 |
| **A/C (Family 1)** | No | R, S, C, P |

---

## Special Folio Features

### Apparatus at Center (Non-Living Objects)

Only 2 folios have apparatus (not creatures) at center:

| Folio | Apparatus | Symbolism |
|-------|-----------|-----------|
| f72v1 | Balancing scale | Measurement, judgment, equilibrium |
| f73v | Crossbow | Hunting, precision, aggression |

Both are on verso pages - may indicate a pattern.

### Unusual Center Images

| Folio | Center Type | Notes |
|-------|-------------|-------|
| f72r2 | Man + woman | Only human couple in nymph series |
| f73r | Reptile | Unusual animal type (most are mammals) |
| f72v3 | Tiger/feline | Exotic animal |

### S0 Top Tokens

f73r and f73v both have S0 placement (4 tokens at top of diagram):
- Ambiguous: could be tiny ring or separate line
- Both folios are paired (recto/verso, end of quire 9)

---

## Folio Annotations

Per-folio documentation of visual oddities: `data/folio_annotations/azc/`

| Annotation File | Folios | Key Features |
|-----------------|--------|--------------|
| `f67r1_f67r2_foldout` | f67r1, f67r2 | Segmented rings, 1a/1b encoding, red ink |
| `f67v2_f67v1_foldout` | f67v2, f67v1 | X/Y only codes, artistic oddball |
| `f68r1_f68r2_f68r3_foldout` | f68r1, f68r2, f68r3 | Scatter diagrams, ring-spoke hybrid |
| `f68v3_f68v2_f68v1_foldout` | f68v3, f68v2, f68v1 | Segmented center, f68v1 missing P-text |
| `f69r` | f69r | W placement with single characters (d,o,l,s,em,y) |
| `f69v_f70r1_f70r2_foldout` | f69v, f70r1, f70r2 | Triple foldout with separate text block |
| `f70v2_f70v1_foldout` | f70v2, f70v1 | First nymph pages, fish/goat centers |
| `f71r` | f71r | Nymph page with CLOTHED ladies (vs naked) |
| `f71v_f72r1_f72r2_f72r3_foldout` | f71v, f72r1, f72r2, f72r3 | Quadruple foldout, man+woman center on f72r2 |
| `f72v1` | f72v1 | Balancing scale apparatus at center |
| `f72v3_f72v2_foldout` | f72v3, f72v2 | Tiger center, lady of status center |
| `f73r` | f73r | 4 top tokens (S0), reptile center |
| `f73v` | f73v | Crossbow apparatus, fancy lady, end of nymph series |

---

## Summary: Key Encoding Rules

1. **H-track only:** Always filter to transcriber='H'
2. **P-text = Currier A:** Exclude P-placement from AZC analysis
3. **S-placement is context-dependent:** Spokes on standard diagrams, interrupted rings on nymph pages
4. **Line numbers encode geometry:** Same line = continuous, different lines = separate positions
5. **Diagram types are interface-only:** All types show same linguistic signature
6. **Center tokens participate in legality:** Not labels, include in analysis
7. **Nymph S-positions show o-enrichment:** 75% o-prefixes vs ~43% elsewhere

---

*Last updated: 2026-01-19*
*Major update from AZC_INTERFACE_VALIDATION phase*
