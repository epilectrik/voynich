# Zodiac per-degree tables: sources, readings and variants

Companion to `degree_tables.json` (same folder). It records where each table comes from, how it was read, what is uncertain, and where the sources disagree. It contains external reference material only. No Voynich data was read or compared.

Compiled 2026-09-30.

---

## 1. How the JSON is organised

Structure: `{table_name: {source_label: {sign: [30 values], ..., "raw": {...}, "note": "...", "flagged": {...}}}}`

- **Signs:** `Aries` … `Pisces`.
- **Degrees:** array index 0 = degree 1. All sources count ordinal degrees ("the first eight degrees of Aries…"), so degree *n* covers n−1° to n°.
- **`raw`:** the per-sign reading as printed, before expansion:
  - run lengths such as `te 3|lu 5|…`;
  - Lilly's end-degree notation such as `d.3.l.8.d.16…`;
  - lists of degree numbers such as `6 11 16 23 29`.
- **`note`:** source-specific remarks. **`flagged`:** entries that the source or its editor marks as doubtful. **`uncertain`:** entries I could not read securely. Consumers should read only the 12 sign keys as data.
- **`null`:** the value cannot be determined from the source as printed. A whole sign is `null` when its cell is unreadable. A single degree is `null` when a row's run lengths do not add up to 30. In that case every correction that changes exactly one run by the missing or excess amount is tried. A degree keeps its value only where all these corrections agree; nothing is filled in by guesswork.

| table | codes |
|---|---|
| `masculine_feminine` | `M` masculine, `F` feminine |
| `light_dark_smoky_void` (Latin sources) | `L` lucidus / light, `D` tenebrosus / dark, `S` fumosus / smoky, `V` vacuus / void |
| `light_dark_smoky_void` (al-Biruni only) | `b` brilliant (*nayyir*), `l` luminous (*mudi'*), `d` dusky (*qutmah*), `m` "dark or shadowed" (*muzlim*; typed as a barred s), `v` empty (*khali*). These do **not** map one-to-one onto L/D/S/V. |
| `pitted` | `P` or `""` |
| `azemena` | `A` or `""` |
| `increasing_fortune` | `F` or `""` |
| `monomoiria`, `terms_egyptian`, `faces_decans` | planet: `Sa` `Ju` `Ma` `Su` `Ve` `Me` `Mo` |

**How everything was read.** Each page image was downloaded at full resolution from the Internet Archive's IIIF server (`https://iiif.archive.org/iiif/<identifier>$<index>/full/full/0/default.jpg`, index counted from 0). The tables were cropped and read by eye. The archive.org OCR was used only to find the right pages, because it is unusable for these tables. Every run-length row was then checked to add up to 30 (see §5).

---

## 2. Sources used

| label in JSON | bibliographic source | copy / URL | images used (0-based) |
|---|---|---|---|
| `Alcabitius_Venice_1482_Ratdolt` | Alchabitius (al-Qabisi), *Libellus isagogicus*, Latin tr. John of Seville. Venice: Erhard Ratdolt, 16 Jan. 1482. Differentia I, closing sections. | Florence, BNCF, Magl. M.7.6 (b): https://archive.org/details/ita-bnc-in2-00001325-002 (a handwritten foliation "67" is on the table page). Same printing, lower resolution: Paris, Bibl. Sainte-Geneviève, OEXV 540 RES (P.2), https://archive.org/details/OEXV540_P2 (index 18), checked for masculine/feminine and light/dark. | 19 (masculine/feminine, light/dark); 20 (pits, azemena, fortune) |
| `Alcabitius_Venice_1485_Ratdolt_Saxonia` | Alchabitius, *Libellus isagogicus*, with the commentary of Johannes de Saxonia; corrected by Bartholomaeus de Alten. Venice: Ratdolt, 1485. | BNCF, Magl. K.6.58: https://archive.org/details/ita-bnc-in2-00000985-001 | 18 (terms; text on faces); 19 (faces table); 24 (masculine/feminine, light/dark); 25 (pits, azemena, fortune) |
| `Alcabitius_Paris_1521_Saxonia` | *Alcabitii ad magisterium iudiciorum astrorum Isagoge, commentario Ioannis Saxonii declarata*. Paris, 1521. | BNCF, CFMAGL 1.6.194/a: https://archive.org/details/ita-bnc-mag-00000743-001 | 24 (masculine/feminine); 25 = fol. 7r (light/dark, pits); 26 (azemena, fortune, *gradus compotentes*). Saxonia's commentary on these sections is on images ~110–112. |
| `Bonatti_Augsburg_1491_Ratdolt` | Guido Bonatti, *Decem tractatus astronomiae* (*Liber astronomiae*). Augsburg: Ratdolt, 26 March 1491. Tractatus II, pars 2, capp. 23–28 (masculine/feminine, light/dark, pits, azemena, fortune, *compotentes*). | Smithsonian: https://archive.org/details/guidobonatusdef00bona | 55, 56, 57 (foliated 26–27 at the head) |
| (checked, not a separate label) | Bonatti, *Decem tractatus astronomie*. Venice: Giacomo Penzio, 1506. | Wellcome 963/D: https://archive.org/details/hin-wel-all-00001949-001 | 32, 33. All five tables identical to 1491; cap. 28 ends "Finit pars secunda secundi tractatus". |
| `Leopold_Augsburg_1489_Ratdolt` (plus `…_list1/2/3` for azemena) | Leopold of Austria, *Compilatio de astrorum scientia*. Augsburg: Ratdolt, 9 Jan. 1489. Section on the signs. | Smithsonian: https://archive.org/details/compilatioleupo00leup | 47 (houses, exaltations, terms "Hermetis … per eos iudicat Albumasar", faces rule, masculine/feminine); 48 (light/dark, pits, fortune, three azemena lists) |
| `alBiruni_1029_Wright1934` | al-Biruni, *Kitab al-tafhim* (1029), tr. R. Ramsay Wright, *The Book of Instruction in the Elements of the Art of Astrology* (London: Luzac, 1934), §§457–459 (and §460). | Typescript pages 62–64 as reproduced in the Skyscript digital facsimile (2003) of the astrological section: https://archive.org/details/albirunibookofinstruction (also https://www.skyscript.co.uk/albiruni_elements.html) | 62 (§457 masculine/feminine), 63 (§458 bright/dark), 64 (§459 fortune and pits), 65–67 (§460) |
| `Lilly_London_1647` | William Lilly, *Christian Astrology* (London: T. Brudenell for J. Partridge & H. Blunden, 1647), p. 116: "Two necessary Tables of the Signes" (explained pp. 117–118). Faces from the "Table of the Essentiall Dignities … according to Ptolomy", p. 104. | Wellcome copy: https://archive.org/details/b30338724 | 150 (p.116); 151–152 (pp.117–118); 138 (p.104) |
| `Paulus_Alexandrinus_Wittenberg_1586_*` | Paulus Alexandrinus, *Eisagoge eis ten apotelesmatiken, sive Rudimenta in doctrinam de praedictis natalitiis*, Latin by Andreas Schato. Wittenberg, 1586. Chapter "De distributione signorum in partes singulas, in quibus 7 stellae dominantur". | Copenhagen, Royal Library, LN bis 199: https://archive.org/details/den-kbd-all-130018104572-002 | 47 (rule), 48 (table), 149 (a second, triplicity-based table; not transcribed) |
| `Ptolemy_Tetrabiblos_I.20_Robbins1940` | Ptolemy, *Tetrabiblos* I.20, "Terms according to the Egyptians", tr. F. E. Robbins (Loeb, 1940; public domain in the US). | LacusCurtius: https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Ptolemy/Tetrabiblos/1B*.html | HTML text |

**Consulted but not tabulated.**

- Abu Ma'shar, *Introductorium in astronomiam*, tr. Hermann of Carinthia (Augsburg: Ratdolt, 1489), BNCF Magl. A.5.59, https://archive.org/details/ita-bnc-in1-00001014-001, image 82. Book V, capp. 16–18 (*De gradibus masculinis et femininis*; *De gradibus lucidis et obscuris*; *De puteis stellarum*) describe the categories. I found **no per-degree lists** in the 1489 print. This rests on reading capp. 16–18 and the following page, where Book VI begins, and on a keyword search of the OCR for the rest of the volume. Hermann announces the lists but does not print them.
  - The one list given is the degrees that raise the native "in sublimationem": Taurus 15, 28, 30; Leo 3, 5; Scorpio 4, 7; Aquarius 4, 11 ("praeter quos et alii per singula signa").
  - Saxonia's commentary on Alcabitius (1521, image ~111) also refers to Abu Ma'shar's *Introductorium* for these degrees.
- Skyscript glossary, "Degree Types" (https://www.skyscript.co.uk/glossary/degree-types/). Used for orientation only. It reproduces Lilly p.116 and Johannes Schoener, *Opusculum astrologicum* (1539), canon XXXVII. The Schoener image is only 407×388 px, too small to transcribe reliably, so it was **not** used.

**Not consulted.**

- Burnett, Yamamoto & Yano, *Al-Qabisi (Alcabitius): The Introduction to Astrology* (Warburg Institute, 2004). Not openly available; I did not use a copy that a private user had uploaded to archive.org.
- The Bologna 1473 and Venice 1512 editions of Alcabitius.
- Abu Ma'shar in John of Seville's translation, or the Arabic (Yamamoto & Burnett, Brill 2019).
- Ibn Ezra, *Beginning of Wisdom*, ed. Levy & Cantera 1939, which includes the Old French version of 1273. It is full view on HathiTrust (inu.32000006466553), but automated access was blocked. Leopold attributes one azemena list to "Abraham", probably Ibn Ezra (see §4.4).

---

## 3. Status of each table

| table | sources, with signs covered |
|---|---|
| masculine / feminine | Alcabitius 1482, 1485, 1521 · Bonatti 1491 (=1506) · Leopold 1489 · al-Biruni · Lilly — all 12 signs in every source |
| light / dark / smoky / void | same seven sources, all 12 signs; a few degrees `null` (§1) in Alcabitius 1482 Virgo and Leopold Taurus and Capricorn |
| pitted | same seven sources, all 12 signs |
| azemena | Alcabitius 1485, 1521 · Bonatti · Leopold (three lists) · Lilly. Signs with no entries are all `""`. Alcabitius 1482 is included only as `…_as_printed_UNRELIABLE`. al-Biruni has no such table. |
| increasing fortune | Alcabitius 1485, 1521 · Bonatti · Leopold · al-Biruni · Lilly; 1482 as `…_UNRELIABLE` (Gemini `null`) |
| monomoiria | Paulus 1586: the rule as stated in the text, and the table as printed; all 12 signs |
| Egyptian terms | Tetrabiblos I.20 · Alcabitius 1485 · Leopold 1489; all 12 signs |
| faces / decans | Alcabitius 1485 · Lilly p.104; all 12 signs |

---

## 4. Readings, uncertainties and disagreements by table

The baseline for comparison is **Alcabitius 1485**. The 1521 Paris printing reproduces it exactly except for one azemena misprint, noted below.

### 4.1 Masculine / feminine degrees

**Source wording**

- Alcabitius: *De gradibus signorum masculinis et femininis*. The prose gives Aries in full: masculine from the start to viii, feminine viii–ix, masculine ix–xv, feminine xv–xxii, masculine from xxii to the end. The table gives run lengths.
- Bonatti, cap. 23: *de gradibus masculinis et gradibus femininis in quolibet signo* ("dixerunt Albumasar et Alkabicius…").
- Leopold: *Qui gradus signorum sint masculini vel feminini*.
- Lilly: "Degrees masculine and feminine".

**Agreement.** Alcabitius 1485 and 1521 and Lilly agree exactly.

**Variants**

- **Bonatti, Aries** (1491 and 1506; prose and table agree): mas 8, fem 5, mas 6, fem 7, mas 4. Alcabitius and Lilly have mas 8, fem 1, mas 6, fem 7, mas 8. The two differ at degrees 10–13, 16–19 and 23–26.
- **Cancer:** Alcabitius 1482 and Leopold have … mas 10 | fem 4 | mas 4, giving masculine 13–22, feminine 23–26, masculine 27–30. The others have … mas 11 | fem 4 | mas 3. They differ at degrees 23 and 27.
- **al-Biruni** differs from the Latin tradition at 56 of 360 degrees. Sagittarius and Capricorn are identical. Many of the differences are one-degree boundary shifts.
  - The differences: Aries 8; Taurus 1–5, 8–11, 16–17, 22–24 (Taurus printed as male 7, female 8, male 15); Gemini 6, 17, 23, 27; Cancer 8; Leo 8, 14–15; Virgo 8; Libra 11–15, 21, 28–30; Scorpio 5–6, 14, 23–25; Aquarius 13–15, 19–21, 28–30; Pisces 13–15, 24–28.
  - Libra as printed ends with two consecutive female runs (x7, x2). I kept it as printed.
  - Al-Biruni reports the scheme critically: he says it rests on no proof, and a table must simply be consulted. He also mentions three schematic alternatives, none of them tabulated here:
    - alternating single degrees;
    - alternating twelfths of 2½°;
    - a 12½°/12½°/2½°/2½° split.

**Uncertainty.** The Skyscript glossary summarises al-Biruni's variants for Aries, Aquarius and Pisces only, and its Aquarius statement ("26th, 27th female") does not match the typescript, where 26–30 are male. I followed the typescript. I could not check it against the Arabic or the 1934 printed volume.

### 4.2 Light / dark / smoky / void

**Source wording**

- Alcabitius: *gradus lucidi, tenebrosi, fumosi, vacui*. The table uses te / lu / fu / va.
- Bonatti, cap. 24: the same four terms. The prose gives Aries and Taurus.
- Leopold: "l lucidos, t tenebrosos, v vero vacuos denotat". There is **no smoky category**.
- Lilly: "Degr. light, darke, smoakie, voyd".
- al-Biruni §458: five grades, and his remark that "no two books are to be found which agree on this matter".

**Agreement.** Alcabitius 1485 = 1521 = Lilly in 11 signs.

**Variants**

- **Scorpio:**
  - Alcabitius (1482, 1485, 1521) and Bonatti: dark 1–3, light 4–8, void 9–14, light 15–20, smoky 21–22, void 23–27, dark 28–30. Al-Biruni's run lengths agree.
  - Lilly: light 15–**22**, smoky 23–24, void 25–29, dark **30**.
- **Aries 21–24:**
  - void in Alcabitius 1485 and 1521 (table and text), in the 1482 *text*, and in Lilly;
  - **dark** in the 1482 *table*, in Bonatti (prose and table) and in Leopold.
- **Aries 30:** void (Alcabitius, Leopold, Lilly) vs **dark** (Bonatti).
- **Taurus, Bonatti:** te 3 | lu 4 | va 4 | lu 3 | va 5 | lu 8 | te 3, giving void 8–11, light 12–14, void 15–19, light 20–27, dark 28–30. Alcabitius and Lilly have void 8–12, light 13–15, void 16–20, light 21–28, dark 29–30. They differ at degrees 12, 15, 20 and 28.
- **Capricorn, Alcabitius 1482:** te 2 | va 4 (dark 20–21, void 22–25) vs te 3 | va 3 (dark 20–22, void 23–25) elsewhere. Al-Biruni's run lengths match 1482 here.
- **Virgo, Alcabitius 1482:** lu 5 for lu 6. The row sums to 29, so degrees 6, 9, 11, 16, 22 and 27 are `null`.
- **Leopold:**
  - Only three categories: smoky runs of the other sources appear as t (dark).
  - His run boundaries equal al-Biruni's in Cancer, Virgo, Libra and Sagittarius (Leo partly), and Alcabitius's in Aries, Aquarius and Pisces. Taurus and Gemini differ from both.
  - The **Taurus and Capricorn rows sum to 31**, so some degrees are `null`. Both look like "t3" printed for "t2", but I did not correct them.
- **al-Biruni (five categories):**
  - Run boundaries are identical to Alcabitius in Aries, Scorpio and Sagittarius.
  - They are shifted by one degree in Virgo, Libra, Capricorn and Aquarius, and differ more in Taurus, Gemini, Leo and Pisces.
  - The labels do not correspond one-to-one to the Latin ones. For example, the Aries runs are d/m/d/b/m/b/m where Alcabitius has te/lu/te/lu/va/lu/va.
  - Where the m runs match a Latin run, it is *fumosi* in Cancer 19–20, Scorpio, Sagittarius, Capricorn and Aquarius. But it is *lucidi* or *vacui* in Aries, *vacui* in Cancer 29–30, and mostly *vacui* in Virgo.
  - Wright's legend glosses the typed symbol as *muzlim* "dark or shadowed"; I kept that code (m) without interpreting it further.

**Uncertainties in Lilly (1647 print)**

- Virgo "v.27": the letter is badly inked. Read as v, which matches Alcabitius va 5.
- Capricorn "ſ.15": long s. Read as smoky, which matches Alcabitius fu 5.
- Scorpio "l.22", Aquarius "l.30" and Pisces "d.6" are partly broken type, but the run lengths make the readings secure.

**Uncertainty in al-Biruni.** In Aquarius the last cell (L5) has a handwritten mark beside it.

### 4.3 Pitted degrees (*putei, gradus puteales*; al-Biruni *abar*)

**Agreement.** Alcabitius 1485 = 1521.

**Variants**

- **Lilly = Bonatti**, except that Lilly has Sagittarius 30 (Bonatti does not) and Aquarius 1 (Bonatti prints 11).
- **Lilly and Bonatti vs Alcabitius:** Virgo 8 13 16 21 **22** (Alcabitius 25); Capricorn **7 17 22 24 29** (Alcabitius 2 7 17 22 24 28).
- **al-Biruni sides with Alcabitius** in Virgo (25) and Capricorn (2 … 28). Its own variants:
  - Aries 17 (for 16);
  - Taurus 5 13 18 24 25 26;
  - Gemini 13 (for 12; its first entry, 2, is flagged);
  - Scorpio adds 17;
  - Aquarius 1 12 14* 23 29;
  - Pisces 2* 9 24 27 28.
  - Wright marks the starred entries x = "mistakes in MS". They are listed in `flagged`.
  - In al-Biruni's Virgo the second number is typed over another digit (13/18). I read it as 13, which the Latin sources also have, and listed it under `uncertain`.
- **Alcabitius 1482** shares al-Biruni's Aries 17 and Taurus 13 18. It prints Virgo 12 for 13 and adds Libra 21. Because of its fixed five-column layout, the sixth entries of the other printings are missing: Leo 28, Sagittarius 30, Capricorn 7, Aquarius 24. Scorpio 27 is also missing (the cell is blank).
- **Leopold** (running text) differs in many single degrees: Aries 6 11 17 24 25; Taurus adds 14 and 26; Cancer 12 18 24 26 30; Leo 7 for 6; Scorpio 8 17 22 27; Capricorn 23 for 22; Aquarius 12 17 19 24 28; Pisces 8 for 9.

**Note on transmission.** Saxonia's commentary says some manuscripts list the pits only in the text and others give a table ("quidam libri habent tabulam de eis factam").

### 4.4 Azemena (*gradus azemena, id est debilitatis corporis*; Lilly "lame or deficient")

**Baseline (Alcabitius 1485):** Taurus 6–10; Cancer 9–15; Leo 18 27 28; Scorpio 19 29; Sagittarius 1 7 8 18 19; Capricorn 26–29; Aquarius 18 19. There are none in Aries, Gemini, Virgo, Libra or Pisces.

**Variants**

- **Alcabitius 1521** prints Capricorn **20** 27 28 29. It is kept as printed, but is probably a misprint for 26, which is what 1485, Bonatti and Lilly have.
- **Bonatti (1491 = 1506) and Lilly:** identical to the baseline except Scorpio 19 **28**.
- **Leopold gives three lists:**
  1. `list1_debilitationis`: "gradus qui dicuntur azimene id est debilitationis": Aries 6–10, Taurus 8 9, Gemini 15, Leo 15 27 28, Scorpio 19 29, Sagittarius 17 18 19, Capricorn 27 28 29, Aquarius 18 20. Several entries look displaced by one sign against the baseline.
  2. `list2_corporis_Abraham`: "azimena corporis … cum luna fuerit in eis in nativitate": Taurus 7 9 10 11, Cancer 7 11–16, Leo 19 28 29, Scorpio 10 19 20, Aquarius 10 19 20. It is followed by "Hec est secundum abraham auēseher", read here as Abraham Avenezra (Ibn Ezra). That identification is uncertain.
  3. `list3_alibi` ("alibi"): Taurus 6–10, Cancer "7. 9 usque ad 15 inclusive", Leo 18 27 28, Scorpio 19 29, Sagittarius 17 18 19, Capricorn 26–29, Aquarius 18 19.
- **Alcabitius 1482:** see §4.6.
- **al-Biruni** has no per-degree azemena table. §460, "places injurious to the eyes", names the same kinds of places, in the same signs: the Pleiades, the nebula of Cancer, the tuft of Leo's tail, the sting of Scorpio, the arrow of Sagittarius, the tail of Capricorn and the water of Aquarius. But it gives only star longitudes for his own epoch, so it was not tabulated.

### 4.5 Degrees increasing fortune (*gradus augentes / augmentantes fortunam*)

**Agreement.** Alcabitius 1485 = 1521.

**Variants**

- **Bonatti = Lilly**, which differ from Alcabitius only in Libra 3 **15** 21 (Alcabitius 3 5 21). al-Biruni and Leopold also have 5, which suggests, without proving, that 5 is the older reading.
- **Leopold:** Gemini 11 5; Cancer 1 2 7 15; Virgo 3 13 20; Libra 3 5 13; Scorpio 5 18 20; Sagittarius 12 20; Capricorn 12 13 24; Aquarius 4 16 17 20; Pisces 13 15.
- **al-Biruni** (upper row of the §459 table):
  - Taurus 8 only;
  - Cancer 1 2 3 14 15;
  - Leo 5 7* 17;
  - Virgo [2 12 20] (bracketed = "omission" in the manuscript);
  - Libra 2* 5 12*;
  - Scorpio 12 20;
  - Sagittarius 13 20 23;
  - Capricorn 12 13* 17* 20;
  - Pisces 12 20.
  - Starred and bracketed entries are listed in `flagged`.
- Saxonia (1521) cites Haly on Ptolemy: the fortune degrees include the exaltation degrees of the Sun and the benefics (Aries 19, Taurus 3, Cancer 15, Pisces 27).

### 4.6 Alcabitius Venice 1482: the azemena and fortune tables are scrambled

In this printing the masculine/feminine, light/dark and pits tables are coherent (variants are noted above). The azemena and fortune tables are not:

- The table under the **azemena** heading is essentially a corrupt copy of the fortune list: Gemini 11; Libra 3 5 21; Aquarius 7 16 17 20; Sagittarius 13 20.
- The table under the **fortune** heading mixes fortune rows (Aries 19; Leo 2 5 7 12 19; Virgo 3 3 20; Libra 3 5 21; Pisces 3 13 20) with azemena rows, some moved by one sign:
  - Taurus 6 7 8 9;
  - Cancer 19 27 28, which resembles Leo 18 27 28;
  - Scorpio 19 29;
  - Sagittarius 1 7 8 18;
  - Capricorn "16 26 & usque ad 29";
  - Aquarius 10 18.
- The Gemini cell ("9 | 2 | usq; | ad terciu[m] ?du[m]") is unclear and set to `null`.

Both tables are kept only under labels ending `_as_printed_UNRELIABLE`. Some readings in this print, such as Cancer 14 and Pisces 12, agree with al-Biruni, so the print may preserve an older textual state. I have not resolved this.

### 4.7 Monomoiria

**Source.** Paulus Alexandrinus (1586 Latin, image 47): "prima pars ei stellae attribuatur, cui et signum debetur: secunda vero ei, quae hanc sequitur in ordine orbium, et sic deinceps". In other words, degree 1 goes to the lord of the sign, and each later degree to the next planet in Chaldean order (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon), repeating.

**The two JSON entries**

- `…_rule_in_text` is generated from that rule.
- `…_table_as_printed` follows the printed table on image 48. The table has six columns, one per pair of signs sharing a lord (Aries/Scorpio, Taurus/Libra, Gemini/Virgo, Sagittarius/Pisces, Capricorn/Aquarius, Cancer/Leo).

**The one discrepancy is Cancer.** The printed table puts Cancer with Leo, starting with the **Sun**, which contradicts the rule. The rule gives Cancer degree 1 = **Moon**, and this is what modern accounts based on Schmidt's translation use.

**Checking.** I compared the printed columns cell by cell with the rule; they match apart from Cancer. A few glyphs are poorly printed, for example Gemini/Virgo degree 21, which is star-shaped and should be Venus.

**Scope**

- This scheme is Hellenistic, from Paulus (4th c.). I found no monomoiria table in Alcabitius, Bonatti, Leopold, Abu Ma'shar (Hermann's print) or al-Biruni.
- Ptolemy (*Tetrabiblos* I.22) mentions a different per-degree scheme, "in accordance with the Chaldaean order of terms", and rejects it.
- The 1586 volume also has a triplicity-based "Tabella Monomoerias secundum triangulum" (image 149). It was not transcribed.

### 4.8 Egyptian terms and faces

**Terms.**

- *Tetrabiblos* I.20 ("Terms according to the Egyptians"), Alcabitius 1485 ("Termini egyptiorum et dicuntur esse hermetis") and Leopold 1489 ("sunt Hermetis et per eos iudicat Albumasar") agree exactly in all 12 signs.
- Every sign's term widths add up to 30. The totals per planet are Saturn 57, Jupiter 79, Mars 66, Venus 82 and Mercury 76, together 360.
- Lilly's p.104 table uses **Ptolemy's own terms** (*Tetrabiblos* I.21), a different system. It is not included, so Lilly is not a witness for the Egyptian terms.

**Faces.**

- Alcabitius 1485 (table and rule) and Lilly p.104 agree: Chaldean order starting with Mars at Aries 1–10.
- Leopold states the same rule.
- In the 1485 table the first face of Cancer is a poorly inked glyph. I read it as Venus, as the rule requires.

---

## 5. Internal consistency (row sums)

**Run-length and range tables.** All rows add up to 30 degrees and all of Lilly's end-degree sequences rise steadily to 30, with three exceptions:

- Alcabitius 1482, light/dark, Virgo = 29;
- Leopold, light/dark, Taurus = 31;
- Leopold, light/dark, Capricorn = 31.

These are handled as described in §1 and not corrected.

**Other tables.**

- Masculine/feminine totals over the zodiac: 194 masculine and 166 feminine in Alcabitius, Leopold and Lilly; 190 and 170 in Bonatti; 220 and 140 in al-Biruni.
- Terms and faces add up to 30 in every sign.

---

## 6. What was not verified

- Wright's al-Biruni was read from a typescript facsimile. Neither the Arabic nor the 1934 printed volume was available to check the letters, the x marks or the symbol for *muzlim*.
- For Alcabitius, only three printings were read (1482, 1485, 1521). No manuscript and no critical edition was used.
- Bonatti was read in the 1491 and 1506 prints only, not in a manuscript or modern edition.
- Leopold was read in the 1489 print only. The reading of the "Abraham" attribution is uncertain.
- The monomoiria rule comes from a 1586 Latin translation, not from the Greek critical text (Boer 1958).
