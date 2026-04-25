# Match Remap: 1566 chapter numbers -> SISMEL sub-recipe IDs

For each of the 16 matched folios (Phase 628 originals), the best-matching
SISMEL sub-recipe by Latin-content cosine similarity.

> **Update 2026-04-25:** Phases 644 / 646 / 647 added 5 NEW matches not in
> Phase 628's original 16. These were not 1566→SISMEL remapped — they were
> identified directly against SISMEL via reverse-prediction or
> reverse-folio-search:
>
> | Folio | SISMEL ID | Recipe |
> |-------|-----------|--------|
> | f78r  | III.36.0  | mercury congelation (4 dry elements + 6-hour fire) |
> | f86v3 | II.10.0   | 3-day coniuncció (11-hour heat → balneum → putrefaction) |
> | f108v | III.29.0  | mercury sublimation (3 principal operations) |
> | f79v  | II.8.0    | first liquefaction (3-day balneum) |
> | f77r  | III.28.0  | 4-element temperament (theoretical exposition) |
>
> All 5 verified at STRONG SUPPORT under Phase 641 atom-decode + Phase 643
> Test B at strict significance. See `matched_recipes.md` Verification Status
> Per Folio section for full evidence.

Columns: folio · orig 1566 ch · best SISMEL id · label · similarity · same-number similarity · numbering matches?

| Folio | 1566 Ch | Best SISMEL | Label | Sim | Same-# Sim | Match? |
|-------|---------|-------------|-------|-----|------------|--------|
| f107r | III.44 | `II.1.0` | primary | 0.0 | 0.0 | NO |
| f76r | II.18 | `II.16.0` | primary | 0.751 | 0.271 | NO |
| f76v | III.15 | `III.16.0` | primary | 0.171 | 0.155 | NO |
| f77v | III.27 | `III.20.0` | primary | 0.431 | 0.077 | NO |
| f80r | III.21 | `II.1.0` | primary | 0.0 | 0.0 | NO |
| f82r | III.22 | `III.19.3` | confeccio_quarte | 0.468 | 0.033 | NO |
| f82v | III.28 | `III.21.0` | primary | 0.491 | 0.193 | NO |
| f83r | II.9 | `II.7.0` | primary | 0.609 | 0.049 | NO |
| f84r | II.14 | `II.12.0` | primary | 0.517 | 0.142 | NO |
| f103r | III.16 | `III.16.0` | primary | 0.445 | 0.445 | YES |
| f112r | III.11 | `III.11.0` | primary | 0.391 | 0.391 | YES |
| f112v | III.1 | `III.1.0` | primary | 0.494 | 0.494 | YES |
| f116r | III.4 | `III.4.0` | primary | 0.585 | 0.585 | YES |
| f75r | III.19 | `III.19.1` | confeccio_secunde | 0.408 | 0.408 | YES |
| f79r | III.12 | `III.12.0` | primary | 0.461 | 0.461 | YES |
| f81v | III.18 | `III.18.0` | primary | 0.47 | 0.47 | YES |

## Top-5 candidates per folio

### f107r (1566 III.44 — Quicksilver coagulation)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `II.1.0` | 0.0 | primary | Incipit secunda pars huius voluminis, que est practica; et p |
| 2 | `II.2.0` | 0.0 | primary | Sequitur prima distinctio alphabetalis¹ |
| 3 | `II.3.0` | 0.0 | primary | De distinctione secunda, que est de figuris prime partis sol |
| 4 | `II.4.0` | 0.0 | primary | De distinctione tercia, que est de figuris secunde partis so |
| 5 | `II.5.0` | 0.0 | primary | [senza rubrica] |

### f76r (1566 II.18 — Element separation (silver-plate test))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `II.16.0` | 0.751 | primary | Operacio secundi regiminis, quod est abluere; et primo de aq |
| 2 | `III.11.0` | 0.433 | primary | Modo dicam de creacione mercuriorum rubeorum, ad faciendum t |
| 3 | `III.22.0` | 0.399 | primary | Quomodo debeas intelligere elementa |
| 4 | `III.12.0` | 0.397 | primary | Rubificacio mercurii sublimati cum suomet igne ad faciendum  |
| 5 | `III.3.0` | 0.388 | primary | LA STRUTTURA DEL TESTO NELLE TRE FAMIGLIE DEI MANOSCRITTI LA |

### f76v (1566 III.15 — Ferment conversion (join H + bind))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.16.0` | 0.171 | primary | Multiplicacio fermentorum per viam mixtionis¹ |
| 2 | `III.15.0` | 0.155 | primary | Fermentum liquefactionis et eius multiplicacio |
| 3 | `II.10.0` | 0.128 | primary | De coniunctione duarum liquefactionum |
| 4 | `III.14.0` | 0.122 | primary | De modo fermentorum compositorum liquefactionis, que nos app |
| 5 | `III.40.0` | 0.117 | primary | Modo dicemus modum separandi elementa in octo diebus, ad con |

### f77v (1566 III.27 — Furnace specification)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.20.0` | 0.431 | primary | De furnis et vasis; et prima de furnis |
| 2 | `III.46.0` | 0.249 | primary | Modo dicemus de omnibus proiectionibus omnium medicinarum, t |
| 3 | `III.33.0` | 0.18 | primary | Nunc dicemus per viam practice aliquas brancas tincture, in  |
| 4 | `III.29.0` | 0.157 | primary | Nunc dicemus quomodo debes intelligere sublimacionem mercuri |
| 5 | `II.7.0` | 0.152 | primary | De dispositione prima ad incipiendum nostrum opus in forma p |

### f80r (1566 III.21 — Animal ash chain Ch21 (multi-chapter 21-25))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `II.1.0` | 0.0 | primary | Incipit secunda pars huius voluminis, que est practica; et p |
| 2 | `II.2.0` | 0.0 | primary | Sequitur prima distinctio alphabetalis¹ |
| 3 | `II.3.0` | 0.0 | primary | De distinctione secunda, que est de figuris prime partis sol |
| 4 | `II.4.0` | 0.0 | primary | De distinctione tercia, que est de figuris secunde partis so |
| 5 | `II.5.0` | 0.0 | primary | [senza rubrica] |

### f82r (1566 III.22 — Lunaria maceration (3-day sealed))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.19.3` | 0.468 | confeccio_quarte | Administracio dicte aque in corpore humano; et primo de aqui |
| 2 | `II.10.0` | 0.301 | primary | De coniunctione duarum liquefactionum |
| 3 | `III.19.2` | 0.298 | confeccio_tertie | Administracio dicte aque in corpore humano; et primo de aqui |
| 4 | `III.19.5` | 0.286 | confeccio_sexte | Administracio dicte aque in corpore humano; et primo de aqui |
| 5 | `III.19.1` | 0.282 | confeccio_secunde | Administracio dicte aque in corpore humano; et primo de aqui |

### f82v (1566 III.28 — Vessel specification)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.21.0` | 0.491 | primary | De vasis |
| 2 | `III.3.0` | 0.288 | primary | LA STRUTTURA DEL TESTO NELLE TRE FAMIGLIE DEI MANOSCRITTI LA |
| 3 | `II.16.0` | 0.264 | primary | Operacio secundi regiminis, quod est abluere; et primo de aq |
| 4 | `III.26.0` | 0.246 | primary | Modo dicemus quod colligacio elementorum fit in diversis pro |
| 5 | `III.22.0` | 0.22 | primary | Quomodo debeas intelligere elementa |

### f83r (1566 II.9 — Drip-counted mercurial solvent)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `II.7.0` | 0.609 | primary | De dispositione prima ad incipiendum nostrum opus in forma p |
| 2 | `II.16.0` | 0.318 | primary | Operacio secundi regiminis, quod est abluere; et primo de aq |
| 3 | `III.3.0` | 0.304 | primary | LA STRUTTURA DEL TESTO NELLE TRE FAMIGLIE DEI MANOSCRITTI LA |
| 4 | `III.33.0` | 0.299 | primary | Nunc dicemus per viam practice aliquas brancas tincture, in  |
| 5 | `II.21.0` | 0.289 | primary | De composicione medicine realis, alias regalis² |

### f84r (1566 II.14 — Gold dissolution (balneum + putrefaction))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `II.12.0` | 0.517 | primary | De aqua corruptibili |
| 2 | `II.13.0` | 0.431 | primary | De alia aqua corruptibili |
| 3 | `II.10.0` | 0.264 | primary | De coniunctione duarum liquefactionum |
| 4 | `III.18.0` | 0.247 | primary | De aquis et medicinis pro humano corpore |
| 5 | `III.7.0` | 0.21 | primary | Rectificacio margaritarum seu perlarum |

### f103r (1566 III.16 — Ferment multiplication (multi-chamber))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.16.0` | 0.445 | primary | Multiplicacio fermentorum per viam mixtionis¹ |
| 2 | `III.4.0` | 0.216 | primary | Fixacio et perfectio illius |
| 3 | `III.33.0` | 0.203 | primary | Nunc dicemus per viam practice aliquas brancas tincture, in  |
| 4 | `III.43.0` | 0.198 | primary | [Senza rubrica] |
| 5 | `III.42.0` | 0.195 | primary | Modo dicemus per alias revelaciones de propriis naturis et e |

### f112r (1566 III.11 — Red mercury tincture (cohobation))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.11.0` | 0.391 | primary | Modo dicam de creacione mercuriorum rubeorum, ad faciendum t |
| 2 | `II.16.0` | 0.32 | primary | Operacio secundi regiminis, quod est abluere; et primo de aq |
| 3 | `III.17.0` | 0.265 | primary | Nunc dicemus opus quod vidimus in inquisitione perfectionis  |
| 4 | `III.12.0` | 0.251 | primary | Rubificacio mercurii sublimati cum suomet igne ad faciendum  |
| 5 | `III.19.7` | 0.229 | administracio | Administracio dicte aque in corpore humano; et primo de aqui |

### f112v (1566 III.1 — Lunaria -> quicksilver)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.1.0` | 0.494 | primary | Liber faciendi mercuria et elixiria illorum |
| 2 | `II.14.0` | 0.295 | primary | De secunda parte solutiva |
| 3 | `III.33.0` | 0.284 | primary | Nunc dicemus per viam practice aliquas brancas tincture, in  |
| 4 | `III.17.0` | 0.282 | primary | Nunc dicemus opus quod vidimus in inquisitione perfectionis  |
| 5 | `II.16.0` | 0.265 | primary | Operacio secundi regiminis, quod est abluere; et primo de aq |

### f116r (1566 III.4 — Fixation / fusibility test)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.4.0` | 0.585 | primary | Fixacio et perfectio illius |
| 2 | `III.12.0` | 0.263 | primary | Rubificacio mercurii sublimati cum suomet igne ad faciendum  |
| 3 | `II.16.0` | 0.241 | primary | Operacio secundi regiminis, quod est abluere; et primo de aq |
| 4 | `II.20.0` | 0.236 | primary | De quarta operacione, que est figere, per quam fit composici |
| 5 | `III.17.0` | 0.197 | primary | Nunc dicemus opus quod vidimus in inquisitione perfectionis  |

### f75r (1566 III.19 — Aqua vitae (4x/9x reflux, honey+wax))

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.19.1` | 0.408 | confeccio_secunde | Administracio dicte aque in corpore humano; et primo de aqui |
| 2 | `III.19.0` | 0.318 | primary | Administracio dicte aque in corpore humano; et primo de aqui |
| 3 | `III.19.2` | 0.286 | confeccio_tertie | Administracio dicte aque in corpore humano; et primo de aqui |
| 4 | `II.12.0` | 0.27 | primary | De aqua corruptibili |
| 5 | `III.19.3` | 0.262 | confeccio_quarte | Administracio dicte aque in corpore humano; et primo de aqui |

### f79r (1566 III.12 — Mercury sublimation -> elixir)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.12.0` | 0.461 | primary | Rubificacio mercurii sublimati cum suomet igne ad faciendum  |
| 2 | `III.4.0` | 0.334 | primary | Fixacio et perfectio illius |
| 3 | `II.16.0` | 0.297 | primary | Operacio secundi regiminis, quod est abluere; et primo de aq |
| 4 | `III.11.0` | 0.243 | primary | Modo dicam de creacione mercuriorum rubeorum, ad faciendum t |
| 5 | `III.17.0` | 0.216 | primary | Nunc dicemus opus quod vidimus in inquisitione perfectionis  |

### f81v (1566 III.18 — Potable gold / water of life)

| Rank | SISMEL ID | Sim | Label | Title |
|------|-----------|-----|-------|-------|
| 1 | `III.18.0` | 0.47 | primary | De aquis et medicinis pro humano corpore |
| 2 | `III.17.0` | 0.302 | primary | Nunc dicemus opus quod vidimus in inquisitione perfectionis  |
| 3 | `III.19.7` | 0.27 | administracio | Administracio dicte aque in corpore humano; et primo de aqui |
| 4 | `III.19.0` | 0.24 | primary | Administracio dicte aque in corpore humano; et primo de aqui |
| 5 | `III.11.0` | 0.227 | primary | Modo dicam de creacione mercuriorum rubeorum, ad faciendum t |
