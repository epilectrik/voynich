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
