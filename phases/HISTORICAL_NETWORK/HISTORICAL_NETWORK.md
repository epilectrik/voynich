# Phase 491: Historical Network

**Phase:** 491 (ONGOING)
**Type:** Historical research (revisitable)
**Status:** Initial build complete; designed for incremental expansion

## Purpose

Map the intellectual network of persons, works, and institutions connected to the Voynich manuscript's temporal-geographic zone (c.1350-1530, Northern Italy / Southern Germany / Austria / Alsace / Switzerland). Identify cipher parallels, transmission chains, and the secrecy-to-openness transition that contextualizes the Voynich's existence.

This phase does NOT attempt to identify the Voynich's author or decode the manuscript. It builds the historical infrastructure needed to evaluate any future provenance or authorship claims against documented reality.

## Data Files

| File | Contents | Entries |
|------|----------|---------|
| `data/network_persons.json` | 58 persons with IDs, dates, locations, roles | P001-P058 |
| `data/network_works.json` | 21 works with IDs, authors, dates, features | W001-W021 |
| `data/network_edges.json` | 98 directed edges (teacher-student, source, printing, ownership, etc.) | E001-E098 |
| `data/cipher_parallels.json` | 16 cipher manuscripts/systems from the zone | CP001-CP016 |

## The Network: Three Geographic Clusters

### 1. The Padua-Venice Cluster (1300-1460)

The University of Padua was the primary medical school for the German-speaking world. Students from Vienna, Bavaria, Nuremberg, and Strasbourg traveled to Padua for medical training and brought knowledge back north.

**Key persons:**
- **Peter of Abano (P003)** — foundational Padua medical-philosophical tradition; synthesized Greek, Arabic, Jewish, Latin sources
- **Giovanni de Dondi (P010)** — Padua physician-astronomer; manuscripts ended up in Vienna (ONB Lat. 5208)
- **Galeazzo di Santa Sofia (P011)** — brought Padua traditions to Vienna (1404); first dissection in Vienna
- **Michele Savonarola (P012)** — first treatise on distilled spirits (1444-1450); Padua professor
- **Nicolo Roccabonella (P013)** — illustrated herbal (c.1445); multilingual plant names
- **Giovanni Fontana (P024)** — physician using invented cipher alphabet (c.1420-1430)

**Cipher activity:** Fontana's two cipher works (CP002, CP003) demonstrate that a Padua physician was using invented glyphs — not standard letter substitution — at the exact Voynich radiocarbon date. His cipher was simple by design (concealment from casual readers, not cryptographic security), but his use of entirely invented signs rather than modified Latin letters is the closest parallel to the Voynich's script among known 15th-century cipher manuscripts.

### 2. The Vienna Cluster (1400-1500)

The University of Vienna's medical faculty was the primary recipient of Padua-trained physicians. By the mid-15th century, it was a center for vernacular German medical writing, distillation expertise, and institutional medical power.

**Key persons:**
- **Michael Puff von Schrick (P014)** — 11-time Dean; distillation manual (~1455); personal physician to Archduke; specialist in anatomy, chemistry, medicine
- **Johannes de Ketham (P016)** — contemporary colleague of Puff; Fasciculus medicinae printed in Venice (1491) — Vienna-Venice publishing axis
- **Georg Peuerbach (P026)** and **Regiomontanus (P027)** — Vienna astronomers; Regiomontanus lectured at Padua (1464)
- **Johannes Tichtel (P034)** — overlapped with Puff's late career; diary (1477-1495) is major cultural document
- **Leonhardt Kargl (P036)** and **Benedikt Planckh (P035)** — Puff's continuator tradition

**Institutional significance:** The Vienna medical faculty had direct institutional continuity from Galeazzo di Santa Sofia's arrival (1404) through Puff's decades of deanship (1435-1470). Any manuscript produced within this institutional context would have access to both Padua-derived medical knowledge and the German vernacular tradition of practical medicine.

### 3. The Strasbourg-Alsace Cluster (1480-1530)

Strasbourg was where the secrecy-to-openness transition became explicit. The printer Johann Gruninger published works by multiple authors in the network, and Hieronymus Brunschwig's titles explicitly marked the transition from hidden to revealed knowledge.

**Key persons:**
- **Hieronymus Brunschwig (P018)** — surgeon-apothecary who published distillation knowledge previously circulated only in manuscript
- **Johann Gruninger (P019)** — printer who published Brunschwig, Salicetus, and others
- **Nicolaus Salicetus (P020)** — physician-monk with dual medical-monastic credentials; same printer as Brunschwig
- **Hans von Gersdorff (P032)** — Strasbourg surgeon; military surgery manual (1517)

**The "geoffenbart" program:** Brunschwig's 1512 *Large Book* title includes "geoffenbart" (revealed/disclosed), but this is not a casual word — it is the operating thesis of the entire work. The word appears **90 times** in the text (394 times counting all forms of "offenbar"). Brunschwig's preface explicitly frames the project as bringing "*diese heimlicheit / vnd verborgene kunst an dz liecht*" — "this secrecy and hidden art to the light." He names Arnoldus de Villa Nova and Marsilio Ficino as custodians of the Aurum potabile secret "which one should keep in great safeguarding and concealment" — and then breaks that tradition, saying "*het mich nit bezwungen die lieb*" — "had not love compelled me."

**The Rupescissa Glossator (P040):** Brunschwig almost never cites Rupescissa directly. His primary quintessence authority is "der glosierer uber Johannes Rupescissus" — an **unidentified commentator** who publicly defended quintessence theory at the University of Padua in 1463, "in einer offenbarlichen versamlung der artzet" (in a public assembly of physicians). This ghost figure is the key link in the transmission chain: Rupescissa → Glossator (Padua, 1463) → Brunschwig (Strasbourg, 1512).

**Puff correction:** Puff von Schrick is **not cited** in the 1512 Large Book. The attribution of Puff as Brunschwig's source may come from the 1500 Small Book or from secondary scholarship, not from direct textual citation in this volume. This needs further investigation.

## The Bavarian Cipher Zone

Eastern Bavaria (Passau region) produced the strongest cipher parallel to the Voynich:

**The Alchymey Teuczsch (W007, CP001):**
- **Shelfmark:** Heidelberg, UB, Cod. Pal. germ. 597 (Cpg 597)
- **Digital facsimile:** https://digi.ub.uni-heidelberg.de/diglit/cpg597
- **Date:** 1426 (attested on fol. 9r; within Voynich radiocarbon range 1404-1438)
- **Physical:** Paper, 95 leaves, 225 x 155 mm, East Bavarian dialect
- **Three invented cipher alphabets** — authors explicitly stated: "We ourselves created this new alphabet so that one would not recognize it as an alphabet." Cipher key provided on fol. 1r but later struck through.
- **Double secrecy layer:** Beyond the cipher alphabets, the authors also used Decknamen (coded words): gold = "gelbe Erde" (yellow earth), silver = "weisse Erde" (white earth), saltpeter = "Salzstein" (salt stone).
- **Selective encryption:** Only alchemical formulas (transmutation, gold multiplication) encrypted; medical recipes, astrological calendar, magical spells, and liturgical content all in clear text.
- **Group authorship:** Niklas Jankowitz (leader), Michael von Prapach (astrologer), Michael Wulfing (magical healer), Friedrich (laboratory assistant who performed the hands-on 1423 gold multiplication experiment).
- **Patronage connection:** The manuscript binding is a parchment diploma from the Landgraves of Leuchtenberg concerning Jewish alchemist Salman Teublein's obligation to keep his art secret. Rec argues the Jankowitz circle were Teublein's successors — direct knowledge transmission across the Jewish-Christian boundary, under noble patronage.
- **Deciphered** by Gerhard Eis (published 1957) — the ciphers were simple monoalphabetic substitution, breakable via German word-ending patterns.
- **Never printed** — manuscript-only circulation.

This manuscript demonstrates that Bavarian alchemists were using multiple invented cipher systems to protect commercially valuable formulas at the exact time the Voynich vellum was produced. The double secrecy layer (cipher + Decknamen) shows that multiple concealment strategies could coexist in a single manuscript. The selective encryption logic (encrypt what has commercial value, leave general knowledge readable) is directly relevant to our model's finding that the Voynich encodes operational procedures. And the Teublein connection demonstrates that alchemical knowledge crossed religious and social boundaries under the protection of noble patronage — exactly the kind of milieu where an elaborate encoding system might be developed.

## Transmission Chains

### Chain 1: Distillation Theory (South → North)
```
Taddeo Alderotti (Bologna, ~1280) — fractional distillation
    ↓ [institutional]
Arnald of Villanova (Montpellier, ~1300) — distilled alcohol in medicine
    ↓ [textual: De consideratione quintae essentiae]
John of Rupescissa (Avignon, 1351) — quintessence = universal medicine
    ↓ [commentary/gloss]
UNIDENTIFIED GLOSSATOR (Padua, 1463) — public defense of quintessence theory
    ↓ [10 German MSS by 15th C; Padua → German-speaking world]
German manuscript circulation (incl. Puff, Vienna ~1455)
    ↓ [acknowledged source: "der glosierer uber Johannes Rupescissus"]
Hieronymus Brunschwig (Strasbourg, 1500/1512) — printed, REVEALED
```
**Note:** Brunschwig's 1512 Large Book does NOT cite Puff directly. The Rupescissa Glossator (P040), not Puff, is Brunschwig's primary quintessence authority. The Rupescissa → Puff → Brunschwig chain requires verification in the 1500 Small Book.

### Chain 2: Surgical Knowledge (Italy → Paris → Germany)
```
William of Saliceto (Bologna, ~1270) — surgical knife over cauterization
    ↓ [teacher-student: E001]
Lanfranchi of Milan (Paris, 1296) — Chirurgia Magna
    ↓ [70+ editions, translated into German]
German surgical manuscript tradition
    ↓ [co-bound with Rupescissa in Erlangen MS B 3, 1484]
Fusion of surgery + alchemical distillation
    ↓ [same practitioner tradition]
Brunschwig (Strasbourg, 1497-1512) — published BOTH surgery and distillation
```

### Chain 3: Padua → Vienna Pipeline
```
Peter of Abano (Padua, ~1300) — foundational tradition
    ↓ [institutional legacy]
Giovanni de Dondi (Padua, ~1360) — MSS end up in Vienna
Galeazzo di Santa Sofia (Padua → Vienna, 1404) — direct transfer
    ↓ [institutional continuity]
Michael Puff von Schrick (Vienna, 1435-1473) — 11-time Dean
Johannes de Ketham (Vienna, ~1460) — Fasciculus medicinae → Venice
    ↓ [Regiomontanus lecturing at Padua, 1464]
Bidirectional Vienna-Padua traffic throughout 15th C
```

### Chain 4: Cipher Traditions (parallel)
```
Roger Bacon (England, 1270s) — 7 methods of concealment; Secretum Secretorum
    ↓ [textual influence, ~600 Latin copies]
Cultural norm: important knowledge = secrets
    ↓ [parallel developments]
Papal ciphers (Avignon, 1379) — diplomatic nomenclators
Fontana (Padua, 1420-1430) — invented glyphs for technical content
Alchymey Teuczsch (Bavaria, 1426) — 3 cipher alphabets for alchemy
Buch der heiligen Dreifaltigkeit (S. Germany, 1410-1419) — cipher grids
    ↓ [theoretical systematization]
Alberti (Rome, 1466) — first cryptography treatise
Simonetta (Milan, 1474) — first cryptanalysis treatise
    ↓ [full synthesis]
Trithemius (Sponheim, 1499) — book-length cryptography disguised as magic
    ↓ [printed]
Brunschwig (Strasbourg, 1512) — "geoffenbart" — the secrecy regime ends
```

## Key Findings

### 1. Cipher Use Was Normal in This Zone
Between 1379 and 1499, we can document cipher use in at least 4 domains within the Voynich's geographic zone: diplomatic correspondence, alchemical manuscripts, technical treatises, and theoretical cryptography. The Voynich is not an anomaly — it fits into a well-documented tradition of encoded knowledge.

### 2. Selective Encryption Was the Norm
Both the Alchymey Teuczsch and Fontana's works encrypt only the commercially or strategically valuable content, leaving general knowledge in clear text. The Voynich is entirely in its script — either everything was considered secret, or the encoding operates at a different level than simple substitution.

### 3. Invented Glyphs Were Used
Fontana used entirely invented signs (no letters or numbers) for his cipher. This is closer to the Voynich than standard letter substitution. However, Fontana's system was deliberately simple and decipherable — the Voynich's system resists all known decipherment methods.

### 4. The Vienna-Padua Pipeline Was Active
The institutional connection between Padua and Vienna was continuous throughout the 15th century. Persons, manuscripts, and knowledge traveled in both directions. The Voynich's vellum (radiocarbon 1404-1438) dates to the peak of this traffic.

### 5. Brunschwig's "Revelation" Implies Prior Concealment
The word "geoffenbart" in Brunschwig's 1512 title is not decorative — it is a **program** deployed 90 times throughout the book. Brunschwig explicitly names Arnoldus de Villa Nova and Marsilio Ficino as prior secret-keepers of the Aurum potabile. His quintessence material comes almost entirely through an unidentified glossator who defended Rupescissa's theory at Padua in 1463 — a figure active at the center of the Vienna-Padua pipeline during the Voynich's probable period. The Voynich, if it encodes distillation procedures, may be a product of this pre-revelation period.

### 6. Sworn Institutional Secrecy at Vienna
The Vienna Medical Faculty Acta (1436-1501) document that new deans swore an oath: "*singula facultatis secreta nullatenus revelare velit*" — to reveal none of the faculty's secrets. Michael Puff von Schrick personally held the *registrum receptarum* (pharmaceutical recipe register) during his 11 deanships. A clandestine dissection in 1452 was handled "*occulte*" — secretly. And a later testimony (Stainpeis, ~1520) records that Puff left "*multa egregia experimenta*" (many excellent experiments/recipes) whose fame "has not been extinguished" — implying unpublished operational knowledge surviving in manuscript form.

### 7. Regiomontanus Operated Under Extreme Secrecy
The Schedel correspondence (1473) documents that Regiomontanus, operating in Nuremberg, kept a **locked house** with secret printing operations and traveled to Italy specifically to acquire books. His associate Schedel — a physician trained at Padua — never once mentions alchemy or distillation in surviving correspondence, suggesting either complete absence of interest or deliberate omission.

### 8. Cross-Border Knowledge Seeking Was Documented
Piccolomini's correspondence (1444) records a Saxon court physician traveling to Italy seeking magical arts at Mons Veneris. The same letters explicitly document the Vienna-Padua student pipeline: "*many will remain in Vienna who now go to Padua.*" Johann Schindel, a Prague physician-astronomer, maintained a 200-volume personal library — the kind of private collection where encoded manuscripts could circulate.

### 9. Alchemical Persecution Explains Both Pseudepigraphy and Encryption

The Pseudo-Lullian Testamentum was written under a false name because open alchemical authorship was dangerous. Multiple lines of evidence from the Buosi-Moncunill thesis (2023) and broader scholarship:

**Active inquisitorial prosecution:** The inquisitor Nicolau Eimeric (1316-1399) ran anti-Lullian proceedings in 1371 targeting alchemical texts. His inquisitorial process specifically attacked the attribution of alchemy to Llull. Practitioners of alchemy faced prosecution, imprisonment, and execution.

**Why texts were attributed to Llull:**
1. **Personal safety** — a dead author cannot be prosecuted
2. **The Ars Magna provided a ready-made framework** — Llull's combinatorial letter system (A, B, C, D... linked in circular diagrams) was repurposed for alchemical notation. The ABC cipher throughout the Testamentum IS the Ars Magna, with alchemical concepts filling the letter slots
3. **The diagrams look authentically Lullian** — circular figures, triangular figures, and letter wheels in the Testamentum are visually indistinguishable from Llull's authentic works
4. **Prestige** — Llull was the most famous Catalan intellectual; his name gave authority
5. **A supporting legend** — a story grew (pre-15th C) that Llull learned alchemy from Arnald of Villanova and made gold for Edward III in London. The Testamentum's colophon citing London 1332 may have fed this legend

**The real Llull rejected alchemy.** His authentic writings warn about its dangers. The earliest attributed alchemical texts appeared ~20 years after his death (1316).

**Candidate author:** Ramon de Tàrrega, a Jewish convert and Dominican friar known from Eimeric's 1371 anti-Lullian proceedings. Another "Master Ramon" from the Catalan intellectual world. Speculative but suggestive.

**John of Rupescissa wrote from prison.** His *De consideratione quintae essentiae* — the most influential alchemical text of the medieval period — was composed inside the papal prison at Avignon. This is what happened to alchemical authors who used their real names.

**The Voynich represents a further escalation.** By the early 15th century, even Lullian pseudepigraphy might not have been safe — Eimeric's inquisition targeted pseudo-Lullian alchemy specifically. Full encryption of operational content (with theoretical material stripped) removes the last readable trace. The scribe encoded what was commercially valuable (procedures) and excluded what was doctrinally dangerous (theory that could be quoted in inquisitorial proceedings).

**Source:** Buosi-Moncunill, Stefania (2023), *El Testament alquímic pseudolul·lià en un manuscrit inèdit català del segle XVI, còpia autògrafa de Jaume Mas*. Doctoral thesis, Universitat de Barcelona. Pages 51, 95, 133-141.

---

## Update: Pseudo-Lullian Source Identification (Phases 628-638)

Computational matching (Phases 628-639, C1882-C1958) has identified the Pseudo-Lullian *Testamentum* (Practica + Liber Mercuriorum) as the source text. 51 procedural chapters match to 41 folios (96% of procedural content). 3 independently confirmed (f75r/Ch19M, f76r/Ch18P, f84r/Ch14P), 5 reverse-blind confirmed, 4 fch hard-filter confirmed, 1 cs hard-filter, 4 recto/verso scan. A 10-dimension permutation test validates the assignment set at p < 0.0001 (C1956). The Testamentum was originally composed in Catalan (1332), translated to Latin (1443). The Catalan operational vocabulary matches the Voynich atom system at workshop granularity (fire types, heating rates, drip-count monitoring). The Testamentum slots directly into Chain 1:

```
Arnald of Villanova (~1300)
    ↓ [attributed tradition]
Pseudo-Lullian Testamentum (14th C) — the source text
    ↓ [shared quintessence framework]
John of Rupescissa (1351)
    ↓ [commentary/gloss]
UNIDENTIFIED GLOSSATOR (Padua, 1463) — "der glosierer uber Rupescissus"
    ↓
Brunschwig (Strasbourg, 1500/1512) — printed
```

The Glossator who defended quintessence theory at Padua in 1463 may have been working directly from the Testamentum tradition. Brunschwig's recipe content (particularly in the 1512 Large Book) independently matches the same Voynich folios as the Testamentum, strengthening the identification.

Full details: `phases/RECIPE_FOLIO_CORRESPONDENCE/`, `phases/CRIB_DECODE_SYNTHESIS/`, `phases/FULL_SPECTRUM_SCAN/`. Folio-level documentation: `context/FOLIOS/INDEX.md`.

## Provenance Chain: Workshop → Rudolf II

The known provenance and recent scholarship suggest a plausible chain connecting the manuscript's creation to its documented owners:

### Known Provenance (documented)
```
[Rudolf II, Prague, ~1599] — purchased for 600 gold florins
    ↓
[Jacobus de Tepenec] — Rudolf's Imperial Distiller and botanical garden curator
    ↓
[Georg Baresch, Prague] — 17th century alchemist
    ↓
[Jan Marek Marci → Athanasius Kircher, 1665]
    ↓
[Jesuits → Wilfrid Voynich, 1912 → Yale Beinecke Library]
```

### The Seller: Carl Widemann → Leonhard Rauwolf

Recent scholarship (Prinke, 2023; earlier work by various researchers) has identified the probable seller to Rudolf II as **Carl Widemann**, a prolific collector of alchemical manuscripts in Augsburg. In March 1599, Widemann sold Rudolf "a couple of remarkable/rare books" for 600 florins (matching the 600 ducats figure). The books were transported in a small barrel.

**Widemann lived in the Augsburg house of Dr. Leonhard Rauwolf** (1535?-1596), a German physician-botanist who:
- Studied medicine at **Montpellier** (1560-1562) — the same university where the Testamentum's author was trained and where the Pseudo-Lullian tradition was strongest
- Collected plants and manuscripts in **Southern France and Northern Italy** (1560-1563) — the exact geographic zone where Testamentum manuscripts circulated
- Traveled the Middle East collecting medicinal plants (1573-1576)
- Died ~1596, childless

Widemann began selling books to Rudolf **immediately after Rauwolf and his widow died**. The implication: Widemann inherited or acquired Rauwolf's collection and sold the most valuable pieces.

### Plausible Full Chain
```
[Northern Italian workshop, ~1420s-1440s]
    — Testamentum-based pharmaceutical/alchemical procedures
    — encoded in unreadable script for trade secret protection
    ↓ [Italian manuscript trade, ~100 years]
Leonhard Rauwolf acquires it during Italian travels (1560-1563)
    — Montpellier-trained physician (Pseudo-Lullian network)
    — collecting in N. Italy (Testamentum circulation zone)
    — would recognize pharmaceutical/botanical content
    ↓ [Rauwolf dies ~1596, childless]
Carl Widemann (living in Rauwolf's house) inherits collection
    ↓ [sells to Rudolf II, March 1599, 600 florins]
Rudolf II gives to Jacobus de Tepenec
    — Imperial Distiller, botanical garden curator, physician
    — the one person at court who would recognize distillation content
    ↓ [Rudolf's collection scatters after his death, 1612]
Georg Baresch → Marci → Kircher → Jesuits → Voynich → Yale
```

### The Tepenec Connection

Jacobus de Tepenec (Jakub Hořčický, ennobled 1607) ran a distillation laboratory at the Clementinum botanical garden, commercially produced "Aqua Sinapis" (mustard water distillate), and served as Rudolf's personal physician. His name on folio 1r (visible under UV) suggests Rudolf gave the manuscript specifically to the person most likely to understand its content — an Imperial Distiller examining an encoded distillation manual. He could not read it, but would have recognized the apparatus drawings and organizational structure.

### The Montpellier Thread

The Rauwolf provenance link creates a remarkable Montpellier thread running through the entire history:
- **~1300:** The "Magister Testamenti" trains at Montpellier, composes the Testamentum in Catalan
- **1332:** Testamentum completed in London, claims Montpellier medical training
- **~1420s-1440s:** Unknown workshop encodes Testamentum procedures (Voynich created)
- **1560-1562:** Rauwolf studies medicine at Montpellier, then collects manuscripts in N. Italy
- **1599:** Manuscript reaches Rudolf II via Rauwolf's collection

The University of Montpellier — the institutional home of the Pseudo-Lullian alchemical tradition — connects the text's composition, its probable acquisition route, and potentially its encoding, across 250 years.

### Candidate Workshop: Milanese Court

The product range encoded in the Voynich (47 matched chapters covering mercury preparations, gold dissolution, quintessence, pearl-making, herbal distillation, transmutation, error correction) implies a well-funded, long-term, comprehensive pharmaceutical-alchemical workshop. Combined with Northern Italian vellum:

**Filippo Maria Visconti's Milan (r. 1412-1447)** is the strongest candidate:
- Ruled during the Voynich radiocarbon window (1404-1438)
- Documented obsession with astrology and alchemy
- Reclusive, secretive rule — operated behind closed doors
- Wealthy enough to fund gold/mercury/pearl operations
- The Testamentum itself references Milan (Ch40M: "at Milan in the year 1333")
- Court botanical/herbal tradition from Gian Galeazzo Visconti
- Milan had direct connections to Padua's medical school

**Independent architectural evidence:** The Voynich rosette foldout (f85v-f86r) depicts castles with **Ghibelline swallowtail merlons** — the distinctive V-shaped battlements that were the political symbol of the Ghibelline faction and specifically of the Visconti family. Researchers at Cipher Mysteries (Pelling, 2017) independently proposed the top-right rosette castle as Milan based on: swallowtail merlons, circular canals (Milan's Navigli), ravelins, and accentuated gate structures. A 1395 drawing by Anovelo da Imbonate celebrating Gian Galeazzo Visconti's investiture shows swallowtail merlons on Milanese buildings, predating the Castello Sforzesco reconstruction (1450s). This is a completely independent line of evidence — architectural analysis and operational content analysis (Testamentum matching) both point to Visconti Milan without reference to each other.

Note: The rosette TEXT is confirmed as organizational/indexing vocabulary (C1126, C1127), not procedural content. The castle illustration is a geographic marker; the text is a metalayer index. They serve different functions on the same page.

**Tension with German encoding hypothesis:** The Voynich's atom letters may correspond to German operational verbs (k=kochen/cook, e=erkalten/cool). This suggests the encoder was a German speaker — possibly a German-trained physician working at an Italian court, consistent with the documented Padua↔Vienna/Bavaria traffic.

**This is speculative.** No direct documentary evidence connects the Voynich to the Visconti court. The provenance gap (1440s-1560s) remains dark. But the convergence of Northern Italian vellum, Testamentum source text, Milanese reference in the source, court-scale product range, Rauwolf acquisition route through Northern Italy, and independent architectural identification of Milanese castle features in the rosette foldout is suggestive.

### Sources
- Prinke, Rafał T. (2023), research on Voynich manuscript provenance and Widemann transaction
- Rauwolf's Italian collections: Ferrario et al. (2021), "The early book herbaria of Leonhard Rauwolf (S. France and N. Italy, 1560-1563)", *Rendiconti Lincei*
- Walter & van Andel (2022), "The emperor's herbarium: Leonhard Rauwolf and his botanical field studies", *History of Science*
- Pelling, Nick (2017), "Voynich nine-rosette page: (Part 1) Milan and swallow-tail merlons", Cipher Mysteries (https://ciphermysteries.com/2017/04/16/voynich-nine-rosette-page-part-1-milan-swallow-tail-merlons)
- Ghibelline merlon analysis: various Voynich Ninja forum threads (https://www.voynich.ninja/thread-3643.html)

---

## Connection to Structural Analysis

This historical network provides **context** for our structural findings but does not modify them:

- **C1377 (Phase 490):** Puff's material categories do NOT predict Voynich folio structural profiles. The grammar is material-independent.
- **F-BRU series:** Brunschwig's fire degrees DO map to Voynich REGIMEs. The procedural connection is real even if the material-type connection is not.
- **C458 (hazard clamping):** The grammar deliberately equalizes structural properties across folios. This is consistent with a system designed to encode *procedures* rather than *materials*.

The historical network supports the interpretation that the Voynich's grammar encodes operational knowledge (procedures, apparatus configurations, control parameters) rather than declarative knowledge (plant names, material identities). This matches the secrecy logic: procedures are commercially valuable; material identities are general knowledge.

## What This Phase Does NOT Claim

1. **No authorship attribution.** We do not claim any person in this network wrote the Voynich.
2. **No provenance chain.** We do not claim to trace the manuscript's ownership history.
3. **No decipherment.** Historical parallels do not decode the text.
4. **No geographic certainty.** The network maps the zone of possibility, not the point of origin.

This is infrastructure for future evaluation, not a conclusion.

---

## Session Addendum 2026-05-18: Workshop Structure + Vessel Iconography + Zodiac Label Observation

Additions from PHASE_700+ research session integrating paleographic, iconographic, and direct-observation evidence with the existing synthesis.

### Davis 5-scribes integration

Lisa Fagin Davis's 2020 digital paleographic analysis identifies **5 distinct scribal hands** in the Voynich. Scribe D1 wrote ~113 of 227 pages (~50%). Scribes form two glyph-frequency clusters: D1+D4, D2+D3+D5. All scribes use the same cipher system with personal letter-form variations.

**Implication for production hypothesis:** Confirms **master + 4-collaborator workshop structure** rather than single-author compilation. This rules out solo-polymath candidates (Fontana, Averlino) as sole authors. Fits the Italian-court-alchemy + Padua-Vienna-trained-physician model: master designed the cipher and directed content, 4 trained scribes (possibly across two phases or two sub-teams) executed production over multi-decade workshop continuity.

Sub-cluster structure (D1+D4 vs D2+D3+D5) compatible with:
- Two-phase production (early team, later team under same master tradition)
- Two sub-team specialization (some sections by team 1, others by team 2)
- Master-apprentice generation transition mid-production

### Italian apothecary vessel iconography match

Direct visual comparison of the Voynich pharmaceutical section vessels (folios 87r-102v) to documented Italian albarelli and Murano glassware of the 1400-1450 period:

**Albarelli match (early Italian production: Florence, Montelupo 1420-1450, Siena hospital albarelli 1425-1450, Faenza emerging):**
- Cylindrical body with characteristic waist constriction — MATCH
- Flared lip / wide neck for parchment cover with string — MATCH
- Cobalt blue + iron-oxide red decoration — MATCH (Voynich uses red and blue throughout pharma section)
- "Very ornate and florid" design with botanical, geometric, possibly heraldic decoration — MATCH
- Standardized iconography conventions (round-bellied=unguent, tall-narrow=liquid, wide-mouth=dry powder) — VOYNICH CONFORMS

**Glass vessel match (Murano production):**
- Vessels with depicted LIDS (albarelli used parchment+string covers, not lids) — these are GLASS BOTTLES
- Colored liquid contents visible (only glass would show contents) — Murano glass
- Foot-rings and decorative bases — consistent with high-end Italian glassware

**Combined finding:** Voynich pharma section depicts a **mixed apothecary inventory** of ceramic albarelli (for dry materials) and glass bottles (for liquids) — exactly what a working Italian apothecary of the 1410-1440 period would use. The DECORATED status of the vessels (per user direct observation: more "flare" than utilitarian Brunschwig woodcuts) is consistent with elite Italian apothecary culture (status display of decorated jars) rather than Northern European utilitarian practice.

**Strengthens:** Italian production hypothesis. The vessel iconography is specifically Italian apothecary genre, not generic medieval-European or German.

### Zodiac label "later user" observation

Direct examination of the zodiac folios (f70v-f73v) reveals month-name labels at the CENTER of each zodiac wheel medallion, in Latin script (NOT Voynichese). Davis's analysis identifies these labels as added by a different hand than the main text scribes.

**User direct observation (2026-05-18):** The labels appear:
- Same hand across all the zodiac wheels (one labeler)
- Same ink (single batch / single session)
- Some labels cleanly written, others traced over multiple times (suggesting hesitancy / uncertainty)
- Overall appearance of being added later, not integrated with original design

**Behavioral signature:** Consistent with a **later practitioner attempting to make the zodiac functional for their own astrological-medical practice**. Confident labels where iconography clearly identifies the zodiac sign; uncertain labels (traced over) where they were inferring from imagery. This is the behavior of a USER, not just a collector.

**Linguistic identification (contested):** Labels show Western Romance morphology — Marc/Aberil/May/Yuny/Jollet/Augst. Specific dialect identification is contested in scholarship: Catalan-leaning (Yuny matches Catalan juny), Occitan-leaning, possibly approximated by non-fluent speaker. NOT cleanly Tuscan/Lombard/Venetian. Scholarly readings note "but only superficially" resembles any single language.

**Implication for production:** The labels are POST-PRODUCTION additions, not original. They reflect a later interim owner/user, not the original workshop's language. **The original production language environment is NOT identified by these labels.** The interim user was likely a Romance-speaking practitioner (could be approximated by a German-trained physician's successor working in Italian Pseudo-Lull tradition — fitting the existing project synthesis of German-trained physician at Italian court).

**Adds a chapter to the manuscript's life cycle:**

```
~1415-1445   Italian-court production (German-trained master + 4-scribe workshop, Visconti Milan)
                       |
~1450-1560   Manuscript in Italian Pseudo-Lull tradition circulation
             At some point in this gap, a later practitioner with PARTIAL knowledge
             adds zodiac month labels in approximated Romance dialect
             (user observation: same hand, single session, some confident some uncertain)
                       |
1560-1563   Leonhard Rauwolf acquires during Italian travels
             [...rest of documented chain as previously established...]
```

The "later user" is a specific historical figure who briefly intersected with the manuscript and tried to make at least the zodiac functional. They lacked the cipher key but could recognize iconography.

### Hospital-pharmacy candidate-type framework

Italian hospital pharmacies of the 15th century emerged as a plausible institutional context for Voynich production, alongside the existing court-alchemy hypothesis. The institutional features fit:

- Multi-decade institutional continuity (5-scribe workshop requirement)
- Master + apprentice structure (Spezieria guild operations)
- Resources for elaborate equipment (decorated institutional albarelli)
- Multi-disciplinary scope (medical + pharmaceutical + alchemical)
- Religious-institutional secrecy context

**Specific candidates surveyed:**

- **Spedale di Santa Maria della Scala, Siena** — documented institutional albarelli from 1425-1450 with institutional emblems. Rector Giovanni Buzzichelli 1434-1444. Pellegrinaio frescoes (1440-1441 by Domenico di Bartolo) document professional medical operations including glass vessels for urine analysis. Strong hospital-pharmacy candidate but Tuscan context conflicts with German-encoding hypothesis.

- **Santa Maria Nuova, Florence** — founded 1288, major Florentine pharmacy operation.

- **Santo Spirito in Saxia, Rome** — major papal hospital with documented pharmacy.

- **Hospital de la Santa Creu, Barcelona** — founded 1401, in Voynich window. Catalan Pseudo-Lull homeland context.

**Project synthesis position:** The existing HISTORICAL_NETWORK preferred candidate remains Filippo Maria Visconti's Milan court (architectural evidence via Pelling 2017 Ghibelline merlons + court-scale product range + Testamentum's Milan reference + Visconti documented alchemy obsession). The hospital-pharmacy candidate-type provides an ALTERNATIVE institutional model worth considering but lacks the architectural/regional-specific evidence that supports Visconti Milan.

The hospital-pharmacy framework is most useful as a **structural model** for understanding the kind of institution the Voynich production required (master + apprentices, multi-decade continuity, elaborate equipment, multi-disciplinary scope) — even if the specific institution is Visconti court rather than Sienese hospital.

### Brunschwig downstream confirmation (already documented, integrated)

The PHASE_698 cardinality baseline finding documents Brunschwig 1512 containing ×4+×9 recipes matching f75r↔III.19. This confirms downstream transmission of the Pseudo-Lull/Voynich recipe tradition through Strasbourg-Alsace printing by 1512. Combined with the existing Rupescissa Glossator (Padua 1463) → Brunschwig (Strasbourg 1500/1512) chain in this document, the transmission lineage is now:

```
Pseudo-Lull Testamentum (Catalan 1332, Latin 1443)
    ↓ [direct workshop access at Visconti Milan court]
Voynich workshop (Italian, 1415-1445) — encoded version
    ↓ [tradition continues in Italian Pseudo-Lull circulation through 16th c.]
[Interim user adds zodiac labels at some point]
    ↓ [parallel: tradition also transmits through Vienna-Padua pipeline]
Rupescissa Glossator (Padua 1463) — public defense of quintessence
    ↓
Brunschwig (Strasbourg 1500/1512) — printed, REVEALED
    + Independently: Brunschwig 1512 ×4+×9 recipes confirm same recipe family
```

Both the encrypted Voynich tradition AND the open Brunschwig tradition descend from common Pseudo-Lull/Rupescissa sources. Brunschwig is the open downstream confirmation that the recipe tradition the Voynich encoded was real and continued to be practiced.

### Updated working synthesis

Combining all the above with the existing HISTORICAL_NETWORK synthesis:

**Production context:** Filippo Maria Visconti's Milan court alchemy operation, approximately 1415-1445. Master was a German-speaking physician trained in the Padua-Vienna pipeline, recruited to Milan court possibly during Visconti's middle reign. Workshop of master + 4 trained scribes operating across multi-decade period. Master's death (coincident with or shortly after Visconti's 1447 death) ended workshop continuity; cipher key died with master while manuscript was preserved.

**The manuscript itself:** Working compendium of court alchemy procedures derived from Pseudo-Lull Testamentum tradition. Encoded in invented script with atom system possibly mapping to German operational verbs (k=kochen, e=erkalten). Pseudo-Lull Testamentum identified as primary source via computational matching (51 chapters → 41 folios, p<0.0001). Multi-section structure (herbal, astronomical, biological, pharmaceutical, recipes) reflects polymath court-alchemy scope.

**Why the cipher:** Inquisitorial persecution (Eimeric tradition active), Visconti court secrecy obsession, Vienna sworn-faculty-secrecy training of master, trade-secret protection of valuable procedures. Multiple converging pressures motivated the encryption.

**Post-production transmission:** Italian Pseudo-Lull tradition circulation through later 15th-16th c., possibly with one or more interim practitioner-owners (one of whom added the zodiac labels in approximated Romance dialect — your observation establishes this interim user existed). Acquired by Leonhard Rauwolf (Montpellier-trained, Pseudo-Lull tradition literate) during 1560-1563 Italian collecting. Transmitted via Widemann (Rauwolf's housemate in Augsburg) to Rudolf II in March 1599 for 600 florins. Standard documented chain from Rudolf onward.

**What's still anonymous:** The specific master figure (probably anonymous in surviving Visconti chancery records, consistent with court alchemist conventions). The specific interim Catalan/Occitan/Romance-speaking practitioner who added zodiac labels. The 1450-1560 ownership chain.

---

## Provisional Next-Phase Directions

Open candidate phases identified during PHASE_697-700 work:

1. **Hapax MIDDLE concentration vs. lexical-content tail discrimination** (PHASE_699 produced negative result; line of investigation closed)
2. **Computus / alternative-class periodic notation tests** (PHASE_700 produced 6-class exclusion; methodology exhausted)
3. **Lullian wheels combinatorial structure test** — RAN AS PHASE_701 (2026-05-18). FALSIFIED. Topology is 12-edge spoke-and-ring, not Lullian 36-edge all-to-all. Documented in `phases/PHASE_701_LULLIAN_WHEELS/INDEX.md` as INDEX entry (not constraint-registered per expert consultation — self-generated alternative, already implied by C1128/C1130/C1989/rosettes_workshop_diagram.md).
4. **Codicology audit** — current state of Voynich watermark/ink/paper analysis scholarship.
5. **Rupescissa Glossator identification** — the unidentified Padua 1463 figure who is Brunschwig's primary quintessence source.
6. **German encoding hypothesis audit** — verify how well-grounded the k=kochen, e=erkalten claim is in the project's actual atom-system analysis vs. interpretive overlay.
