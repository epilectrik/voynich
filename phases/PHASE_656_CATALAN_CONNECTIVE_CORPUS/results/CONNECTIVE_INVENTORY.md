# Phase 656 — Connective Inventory

Per pre-registration, this is data prep — no claim of significance.

**Procedural corpus** (Practica II + Mercuriorum III):
- Total subrecipes scanned: 89
  - Subrecipes with >=1 instance: 83
- Total connective instances: 1012

**Theorica negative control** (part I):
- Total subrecipes scanned: 100
- Total connective instances: 926

## Frequency by category x part

| Category | Practica (II) | Mercuriorum (III) | Theorica (I, control) |
|---|---:|---:|---:|
| BOUNDED_DURATION | 17 | 17 | 29 |
| CAUSAL | 54 | 87 | 260 |
| CONDITIONAL_HYPOTHETICAL | 89 | 159 | 231 |
| CONDITIONAL_TEMPORAL | 75 | 157 | 160 |
| CONSEQUENT | 29 | 51 | 70 |
| MANNER | 6 | 7 | 17 |
| REPETITION | 10 | 49 | 23 |
| TEMPORAL_AFTER | 85 | 120 | 136 |

## Spot-check examples (3 random per category, procedural corpus)

Use these to verify the regex categorization is correct.

### BOUNDED_DURATION  (N=34)
- `III.1.0` ord=23: ...t. E la lur terminació és que a poch a poch se sien cremats 【en tro que】 en aquell lent foch se sien desiccats. E sapies, fill, que...
- `II.24.0` ord=11: ...ecessitat de / la fi, que és nodrir l'infant aprés lo⁴ part 【en tro que】 ell pot menjar del pa. Car tota cosa vital ha mester d...
- `II.23.0` ord=2: ...ent, e feu molre tot ensemps dedens un mortar[i]³ de vidre, 【en tro que】 tot sia fet un cors. Aprés enbeu⁴ ton elixir ab una part de...

### CAUSAL  (N=141)
- `III.95.0` ord=125: ...osee et affin quelle puisse plus forte matiere digerer. Et 【per ço】 pren potencia de Et pour ce elle prant puissance...
- `III.29.0` ord=90: ...da en lur ley moyesach¹⁴ contra nosaltres tots cristians. E 【per ço】, car de tot açò havem largament parlat e de tots lurs delin...
- `III.31.0` ord=15: ...E l'obra del cors a⁴ laxar e dissolure e sus en alt estar. 【Per ço】't | te⁵ sia monstrat que si tots dos ensemps són molt be pr...

### CONDITIONAL_HYPOTHETICAL  (N=248)
- `II.17.0` ord=10: ..., met-ne un poch sobre una lamina de covre ignida, e guarda 【si】 res de aquella evapora. E si ho fa, torna-la al regiment de...
- `III.43.0` ord=3: ...la potestat, de la qual coman lo nostre pur »Testament«. E 【si】 açò entens², entendràs per natura molt radicalment partida...
- `III.43.0` ord=6: ...er consequent tots los altres continguts en la roda de T. E 【si】 bé ab realitat entens⁴ tu la dita roda, entendràs promptame...

### CONDITIONAL_TEMPORAL  (N=232)
- `II.26.0` ord=22: ...e metall, quant de pura sanch és tota abeurada, e no abans. 【Quant】 donchs volràs haver tal⁷ / sanch per enbebir la pedra ab...
- `II.22.0` ord=39: ...e molt gran ignició seria e cremaria⁷ los simples elements. 【Quant】 diem 'simples', diem-ho a la differencia de la substancia f...
- `III.95.0` ord=127: ...ativa es quant la vertu formative est Car 【quant】 la vertu formative est infusa en la materia mineral,...

### CONSEQUENT  (N=80)
- `III.30.0` ord=36: ...a, car ses decoccions no li són estades entegrades. De tant 【donchs】 com a la materia segons sa exigencia se trau lo deute de na...
- `II.26.0` ord=10: ...mentall, que és axí com let, que es convertex en sanch. Car 【donchs】 segons la temperança de l'humit exuberat ell per rahó de fi...
- `III.33.0` ord=61: ...oltes van per lo món, qui saben coses molt bones e plasens. 【Donchs】, si tu los encontres, veies si'n peus traure alguna cosa de...

### MANNER  (N=13)
- `II.10.0` ord=5: ...à tota distillada, fortifica ton foch de carbó poch a poch, 【segons que】't serrà vist, per calcinar la terra. Mas garda't de massa a...
- `II.23.0` ord=8: ...na-ho de sobre ses feces molent e enbuent e cohent e assant 【segons que】 vol natura; e cohu-ho e sublima. E axí continua lo dessús d...
- `III.46.0` ord=24: ...a medicina per cendrada, e trobaràs en aquella aur e argent 【segons que】 les medicines serran a blanch o a vermell. Ffill, quant vol...

### REPETITION  (N=59)
- `III.21.0` ord=18: ...s coses ensemps pots fer e algunes vegades .iii., e algunes 【vegades】 .iiii., la qual cosa tu no poràs fer si eres posat en defal...
- `III.19.0` ord=8: ...novellant la bresca a cascuna segona distillació per quatre 【vegades】 aliter broicé e triblé; e aprés ix vegades....
- `III.29.0` ord=40: ...atsia açò que ells poguessen entendre per lo foch naturall, 【totes vegades】 no pot esser excitat sens la contra natura, que ell pusca r...

### TEMPORAL_AFTER  (N=205)
- `II.2.0` ord=9: ...corromp e confon tot ceo que […] és de l'argent viu comú. E 【puys】 lo [5] és significa[t] per E, que conté les natures dels d...
- `III.17.0` ord=20: ...rahó e entenció de animació, e sublima-u en tro sia gelada. 【Puys】 fortifica ton foch en tro sia sublimat tot ço que's porà su...
- `III.95.0` ord=40: ...ee catholica gran, in fide catholica magna, 【puys】 aprés entenen lo dictat, exinde intelligent dic...

## Coverage (procedural)

- Avg instances per subrecipe: 11.4
- Avg connective density (instances per 1000 chars, subrecipes >= 100 chars): 4.7

### Categories present in >=50% of subrecipes

- CAUSAL: 48/89 (53.9%)
- CONDITIONAL_HYPOTHETICAL: 59/89 (66.3%)
- CONDITIONAL_TEMPORAL: 63/89 (70.8%)
- TEMPORAL_AFTER: 66/89 (74.2%)

## Pre-registered corpus-quality bar (PRE_REGISTRATION section 8)

- Total instances >= 800: 1012 -> PASS
- >=3 categories present in >=50% of subrecipes: 4 -> PASS
- Theorica control >= 100: 926 -> PASS
- Manual 20-record spot-check: see "Spot-check examples" above; humans verify >=18/20 correct categorization.
