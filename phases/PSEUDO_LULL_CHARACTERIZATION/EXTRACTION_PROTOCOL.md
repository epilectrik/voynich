# Phase 602: Extraction Protocol

**Status:** FROZEN — do not modify after script execution begins.

## 1. Chapter Parser Regexes

### English file patterns:

```
Theorica/Practica (Parts I-II):
  r'CAP\.\s+([IVXLC]+)\.'

Mercuriorum (Part III) — Latin ordinals:
  r'CAPVT\s+(PRIMVM|SECVNDVM|TERTIVM|QVARTVM|QVINTVM|SEXTVM|SEPTIMVM|OCTAVVM|NONVM|DECIMVM|VIGESIM\w+|TRIGESIM\w+|QVADRAGESIM\w+|QVINQVAGESIM\w+)'

Furnis (Part IV):
  r'(?:Cap|Caput)\.\s+([IVXLC]+)\.'
```

### Part boundaries (English file):

| Part | Start marker | Approximate line |
|------|-------------|-----------------|
| Theorica | First `CAP. I.` after page 22 | ~244 |
| Practica | `--- Page 353` or second `CAP. I.` restart | ~2478 |
| Mercuriorum | `# LIBER MERCURIORUM` divider | ~3111 |
| Furnis | `# PRACTICA DE FURNIS` divider | ~4320 |
| Compendium | `--- Page 440 (page 211 verso, Compendium` | ~5986 |
| Index | `--- Page 500` or `Index Materiarum` | ~6400 |

## 2. Symbolic-Letter Detection Rules

### What counts as a cipher-letter reference:
- Single uppercase letter followed by period: `\b([A-Z])\.\s` (e.g., "H. I. K.")
- Single uppercase letter preceded by "of" or "per" or "cum": contextual cipher ref
- Multi-letter sequences: 2+ single-letter refs within 50 characters of each other

### What does NOT count:
- `c.` or `f.` in the Index section (chapter/folio references)
- `A.` when it means "Amen" at sentence end
- Roman numerals in chapter headings (CAP. XXVI)
- Abbreviations: `sc.` (scilicet), `ar.` (argentum), `vi.` / `viu.` (vivum)
- Letters in quoted verse passages (poetic, not operational)
- `A.` when clearly referring to God in theological passages (Theorica cosmological chapters)

### Disambiguation rule:
A single letter is a cipher reference if:
1. It appears in a chapter tagged as "practical" or "mixed" (not pure "theoretical")
2. It is NOT in the excluded abbreviation list
3. It appears within 2 sentences of an operational verb (distill, sublime, calcine, dissolve, congeal, fix, etc.)

## 3. Monitoring Lexicon

### English — Color terms:
```
black, blackness, blackened, nigredo, dark, charcoal-colored
white, whiteness, whitened, albedo, snow-white, pale
red, redness, reddened, rubedo, scarlet, citrine, citrinitas, yellow, golden
```

### English — Consistency terms:
```
powder, powdery, pulverized, paste, wax, wax-like, waxy, fusible, fuse,
fusion, flow, flowing, liquid, liquefied, crystalline, crystallized,
solid, hardened, calcined, calx, earth, earthy, oil, oily, unctuous,
slime, slimy, gum, gummy, foliated
```

### English — Volatility terms:
```
vapor, vaporous, fume, fumes, smoke, smoking, volatile, volatilized,
sublimate, sublimated, flight, fleeing, ascending, rising, evaporate
```

### Latin — Color terms:
```
niger, nigra, nigrum, nigredo, nigrescit
albus, alba, album, albedo, albescit, albissim
rubeus, rubea, rubeum, rubedo, rubescit, citrinus, citrinitas
```

### Latin — Consistency terms:
```
puluis, pulueris, pasta, cera, cereus, fusibil, fusio, fluxi, fluxu,
liquefact, crystal, solidif, calcin, calx, terra, oleum, oleosa,
limus, gumma, foliat
```

### Latin — Volatility terms:
```
vapor, fumus, sublim, volatil, fugit, ascend, euaporat
```

## 4. Termination Lexicon

### English triggers:
```
until, repeat, reiterate, reiteration, as many times as, so often,
continue...until, do not stop until, keep...until, iterate
```

### Latin triggers:
```
donec, quousque, toties...quoties, reiter, repet, continua
```

### Classification rules:
- **Count-based**: contains a specific number ("seven times", "thirty distillations", "septies")
- **Threshold-based**: contains a color or state term ("until white", "donec nigra")
- **Time-dependent**: contains a duration ("for eight days", "per octo dies", "for one year")
- **Quality-gated**: contains a quality test ("until it resists fire", "until it flows like wax")
- **Externally judged**: contains judgment language ("when you judge", "as seems sufficient")
- **Asymptotic/open-ended**: contains open language ("as long as you wish", "to infinity")

## 5. Heat Lexicon

### English terms:
```
fire, heat, heated, degree, gentle, strong, moderate, fierce, slow,
balneum, bath, water bath, bain-marie, ashes, ash fire, ash bed,
sand, sand bath, athanor, furnace, dung, horse dung, quicklime,
cinericium, cupel, crucible, tripod, oven, open fire, charcoal
```

### Latin terms:
```
ignis, ignem, calor, calore, gradus, lenis, lento, fortis, forte,
moderatus, balneum, balneo, ciner, cinerit, arena, athanor,
furnus, furno, stercor, fimus, calx viua, copella, crucibul
```

### Heat mode classification:
A heat reference is a distinct "mode" if it specifies a qualitatively different heat source or intensity level. Two references to "gentle fire" are the same mode; "gentle fire" and "ash fire" are different modes.

## 6. Correction Lexicon

### English terms:
```
error, errors, erring, correct, correcting, correction, defect, defective,
trouble, fail, failing, failure, if you see that, beware lest,
wrong, mistaken, sophisticators, deceived, ruin, ruined, burned, burnt,
combustion, combustible, start over, begin again, lost
```

### Latin terms:
```
error, errore, errorem, errare, corrig, defect, defectu,
cave, caueas, sophistae, decepti, combust, combustibil,
perdit, destructio, ruinat
```

### Failure source classification:
- **Process drift**: co-occurs with color-sequence or premature-state language
- **Material failure**: co-occurs with contamination or wrong-substance language
- **Operator error**: co-occurs with "too much fire", "opened too early", timing language
- **Irrecoverable**: co-occurs with "start over", "lost", "cannot be saved"

## 7. Judgment Cue Patterns

### English patterns:
```
"if you see"       → visual judgment
"if you find"      → discovery/assessment
"you will see"     → expected observation
"you will find"    → expected discovery
"you shall know"   → diagnostic knowledge
"this is the sign" → explicit signal
"beware lest"      → warning/caution
"take care that"   → precaution
"when it becomes"  → state-change trigger
"when it no longer"→ cessation trigger
"test whether"     → explicit assay
"judge by"         → operator assessment
"as seems"         → subjective assessment
```

### Latin patterns:
```
"si videas" / "si videris" / "si videbis"  → visual
"inuenies"                                  → discovery
"signum erit" / "signum est"               → diagnostic signal
"cave ne" / "caueas"                        → warning
"nota quod" / "nota si"                    → attention marker
"cum videris" / "quando videris"           → state observation
"proba" / "probatur"                       → test/assay
"iudicio" / "arbitrio"                     → judgment
```

## 8. Operation-Family Keywords

| Family | English keywords | Latin keywords |
|--------|-----------------|----------------|
| Distillation | distill, distillation, alembic, cucurbit | distill, distillat, alembic, cucurbit |
| Sublimation | sublimate, sublimation, sublime, ascending | sublim, sublimat, ascend |
| Calcination | calcine, calcination, calx, ash, powder | calcin, calx, ciner |
| Fixation | fix, fixation, fixed, immobile | fix, fixat, fixio, immobil |
| Dissolution | dissolve, dissolution, resolved, solution | dissolv, solut, resolut |
| Coagulation | congeal, coagulate, coagulation, congelation | congel, coagul |
| Circulation | circulate, circulation, circulatory | circul, circulat |
| Imbibition | imbibe, imbibition, moisten, nourish | imbib, humect, nutri |
| Fermentation | ferment, fermentation | ferment |
| Projection | project, projection, cast upon | proiect, proijc |
| Separation | separate, separation, rectify, purify, wash | separ, rectific, purific, laua |
| Furnace/apparatus | furnace, vessel, athanor, instrument | furnus, vas, athanor, instrument |
| Theoretical | nature, element, principle, philosophy | natura, elementum, principium, philosophi |

Classification rule: a chapter's primary family is the operation whose keywords appear most frequently in that chapter's text. Secondary family assigned if a second operation has >50% of the primary's keyword count.

## 9. Ambiguous Passage Handling

- If a passage matches multiple extraction categories (e.g., a color-monitoring passage that also contains a termination condition), record it in ALL matching categories with cross-references.
- If a passage is borderline between "descriptive" and "action-triggering" observation, classify as "diagnostic" (the middle category).
- If a cipher-letter reference could be either operational or theological (especially "A." = God), check whether the sentence contains any operational verbs. If yes → cipher reference. If no → exclude.

## 10. Duplicate/Restatement Handling

- The Compendium Animae restates material from the Theorica/Practica. If a passage in the Compendium closely paraphrases an earlier passage, tag the Compendium version as `restated` and exclude from counts (but retain in the data for reference).
- The Elucidatio explicitly summarizes the Testament. All Elucidatio passages tagged as `summary` and excluded from primary counts.
- Cross-part repetitions (same instruction in Mercuriorum and Furnis): count both, since they represent independent textualization of the same operation in different editions.
