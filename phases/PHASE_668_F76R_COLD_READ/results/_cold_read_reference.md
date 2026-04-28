# Cold Read Reference — Shared Agent Instructions

## Template
Read `phases/PHASE_668_F76R_COLD_READ/results/f75r_cold_read.md` for the EXACT format. Match its structure section by section.

## Required Sections (in order)
1. **Title line**: `# Cold Read: {folio} ↔ {recipe_id} {recipe_title}`
2. **Match tier / Verdict** (at top)
3. **The Recipe** — Full Catalan text with cipher resolved + English translation + cipher note
4. **Token Dictionary** — Preamble explaining how tokens work, prefix domain table, atom reference table, then token table with columns: Token | Prefix | Atoms | Compositional reading | Workshop Reading | Source
5. **Observation MIDDLEs table**
6. **The Folio** — Summary table (Para, Lines, Tokens, dar, e-depth, Obs MIDDLEs, Mapped recipe phase)
7. **Paragraph-by-Paragraph Cold Read** — One subsection per paragraph, each with "Recipe says:" and "What the tokens say:" and "Match assessment:"
8. **Cross-Paragraph Patterns** — e-depth thermal arc table, dar distribution table, observation MIDDLE distribution table
9. **Verdict** — COHERENT / PARTIALLY COHERENT / INCONCLUSIVE with summary

## Token Dictionary Construction
- List the ~20-40 most frequent/significant tokens on this folio
- Look each up in B dictionary first (file: `phases/B_OPERATIONAL_DICTIONARY/results/b_dictionary_top100.md`)
- For tokens not in B dictionary, compose workshop reading from atoms
- Source column: "PT-013 (N/10)" for PT-013 tokens, "B Dict D0/D1/D2" for dictionary tokens, "Compositional" for composed ones
- The token table MUST have the Atoms column showing the atom decomposition

## Atom Reference

| Atom | Role | Gloss | Confidence |
|------|------|-------|------------|
| k | HEAD | heat | LOCKED |
| e | MOD | cool / stabilize | LOCKED |
| h | MOD | watch | LOCKED |
| y | TERM | end / done | LOCKED |
| i | MOD | iterate | LOCKED |
| n | TERM | bind / contain | LOCKED |
| a | MOD | yield | LOCKED |
| m | TERM | final | LOCKED |
| d | MOD | mark / do | SOLID |
| t | HEAD | transfer / apparatus-mediated | SOLID |
| l | MOD/TERM | state / hold | SOLID |
| o | MOD | arrange | SOLID |
| c | MOD | adjust | SOLID |
| r | TERM | respond | PLAUSIBLE |

## Prefix Domains

| Prefix | Domain | Workshop sense |
|--------|--------|---------------|
| qo | Heat source | Managing the fire or furnace |
| ch | Active test | Checking state — finger test, color check, viscosity |
| sh | Passive watch | Observing without intervention — watching distillate, fumes |
| ok | Vessel | Managing the vessel or apparatus temperature |
| ot | Transfer rate | Monitoring output — drip rate, melt flow |
| ol | Continue | Maintaining current state without change |
| da | Material | Adding or handling substances |
| sa | Scaffold | Supporting infrastructure for iterative cycling |

## Observation MIDDLEs

| Code | Atoms | Compositional reading | Workshop sense |
|------|-------|-----------------------|---------------|
| ckh | c.k.h | adjust, heat, watch | Is the fire at the right level? |
| cth | c.t.h | adjust, transfer, watch | Watch what's being transferred or transformed |
| ecth | e.c.t.h | stabilize, adjust, transfer, watch | Handle/observe a cooled intermediate product |

## Key PT-013 Token Glosses (highest confidence)

| Token | Workshop Reading | Cross-folio |
|-------|-----------------|-------------|
| qokedy | Maintain current fire level | 10/10 |
| qokeedy | Gentle fire — balneum / water-bath level | 10/10 |
| qokain | Sustained cyclic heating | 10/10 |
| qokaiin | Heat-source: sustained contained form (apply heat while sealed/bound) | 15/15 |
| qokal | Fire reached target — heat stage done | 10/10 |
| shedy | Watch the distillate (clarity, fumes, color) | 10/10 |
| dal | Carefully collect distillate / careful placement | 9/10 |
| lchedy | Check apparatus (seals, receiver, furnace) | 8/10 |
| otal | Note the output rate (drips or melt-flow) | 8/10 |
| qokchedy | Adjust fire while watching | 3/3 |
| ram | Stage done — note result | 4/4 |

## Cipher Keys

### Part II (Liber Practicus) — applies to II.x chapters
- A = God (Déu)
- B = quicksilver / mercury (argent viu)
- C = salt of stone (sal de pedres)
- D = vitriol azoqueous (vitriol azoquench)
- E = menstrual (menstruall)
- F = fine silver (argent fi)
- G = philosophical mercury (mercuri)
- H = gold (or)

### Part III (Liber Mercuriorum) — applies to III.x chapters
- B = simple water (l'aygua simple)
- C = simple red sulphur (lo sofre roig simple)
- D = simple dissolved gold (l'or dissolt simple)
- E = compound red water (l'aygua roia composta)
- F = compound red sulphur (lo sofre roig compost)
- G = compound dissolved gold (l'or dissolt compost)

### Tavola 2 mirror-script entries (already resolved inline in SISMEL text)
24 inline cipher words mostly in Part II, resolved by SISMEL editors in brackets.

## Writing Style Rules
- Use workshop language throughout the narrative (NOT atom chains like "heat.cool.do.end")
- In the Token Dictionary table, show atoms AND compositional reading AND workshop reading
- For counting shorthand: if identical tokens repeat in sequence, note this (scribe repeats the characteristic operation token once per cycle-pass)
- Be honest about match quality — not every folio will be COHERENT
- Adapt to recipe type: procedural recipes get step-by-step paragraph mapping; theoretical/descriptive recipes get thematic analysis
- Reference specific token sequences from lines in the cold read TXT
- Include the `**e-depth**` explanation paragraph after the folio summary table (same as f75r template)
