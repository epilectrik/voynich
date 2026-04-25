# SISMEL Matched Recipe Reference

Source: `phases/SISMEL_RECIPE_CORPUS/results/sismel_corpus.json`

Paragraph-aligned Latin + Catalan text for the 16 folio-chapter matches used in
PCI-V2, RECIPE_FOLIO_CORRESPONDENCE, and ATOM_GLOSS_RECIPE_VALIDATION.

> **Current verification status (2026-04-25):** the 16 folio-recipe pairs below
> were established via Phase 628's 8D residual feature matching. Subsequent
> phases applied additional verification layers:
>
> - **Phase 641 atom-decode-vs-Catalan:** 2 STRONG (f75r, f84r), 7 MODERATE,
>   3 WEAK, 4 INCONCLUSIVE. f76r's INCONCLUSIVE atom-decode flagged.
> - **Phase 643 (C1959) paragraph layout-order vs recipe-phase order Test B:**
>   verified on 5 of the 16 originals (f75r, f84r, f78r-via-blind-test, f86v3-
>   via-blind-test, f82r). Mean rho across these 5 originally was +0.81.
> - **Phases 644 / 646 / 647 added 5 NEW confirmed matches** not in Phase 628's
>   original set: f78r↔III.36.0 (mercury congelation), f86v3↔II.10.0 (3-day
>   coniuncció), f108v↔III.29.0 (mercury sublimation), f79v↔II.8.0 (first
>   liquefaction), f77r↔III.28.0 (4-element temperament). All passed atom-decode
>   STRONG SUPPORT and Test B at strict significance.
> - **Phase 647 (C1960) heat-mode encoding** confirmed on heat-phase-distinct
>   subset (f84r, f82r, f78r, f86v3, f77r): mean rho +0.71.
>
> **C1959's evidence base now spans 8 confirmed matches** (3 originals retained
> + 5 new) across 7 distinct recipe classes, mean rho +0.89, 6/8 at strict
> permutation significance, 3/8 at n≥10 individually-significant.
>
> The 16 below remain the original Phase 628 candidate set. Their tier labels
> reflect Phase 628's 8D-matching tier, NOT the subsequent atom-decode +
> Test B verification status. See `## Verification Status Per Folio` near the
> end of this document for the current cross-phase status table.

---

## f75r -> Part III, Ch. 19
**Tier:** CONFIRMED  
**Recipe:** Aqua vitae (4x/9x reflux, honey+wax)  
**Title (Latin):** *Administracio dicte aque in corpore humano; et primo de aquis temperantibus illam*  
**Title (Catalan):** *La administració de la dita aygua en cors humanall; e primer de les aygues temperans aquella*  
**Folio refs in MS:** f. 63va, f. 64vb, f. 64ra, f. 64va  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['286_L', '287_L', '288_L']`, Catalan `['286_R', '287_R', '288_R']`

### ¶ 1

**Latin**

[Tu] accipe aquam vite et tempera suam humiditatem per distillacionem; et substanciam aque, que est purum aurum, pone ad partem; et infra humiditatem vegetabilem pones tertiam partem de bresis, alias brescis, cum tota sua substancia, scilicet cum melle et cera. Et illam ponas ad fermentandum in levi calore per tres dies; et quanto magis ibi moratur, prevalet. Post pone ad distillandum in balneo; et hanc distillacionem reitera, renovando brescas qualibet secunda distillacione per quatuor vices. Confeccio secunde aque: Accipe unum caponem antiquum sive unam gallinam et depluma et abice intestina et omnia interiora ventris; et separa ossa et pedes. Et tota caro pistetur; et post pone in alembico et distilla totius aquam et eam pone ad partem. Confeccio tercie aque: Recipe totam carnem galline sive caponis et super cineres distilla totam suam humiditatem cum igne mediocri bene continuato; et caveas bene a combustione carnis; et pone ad partem humiditatem distillantem. Confeccio aque quarte: Recipe humiditatem simplicem dicte lunarie et de illa pones tres partes supra substanciam carnis. Post claude cucurbitam cum suo coopertorio vitreo clauso cum cera communi et pone super cineres per tres dies naturales cum igne ex serraturis composito. Postea pone alembicum et distilla totam per balneum; et illam custodies ad partem. Confeccio aque quinte: Recipe dictam substanciam galline sive caponis et super cineres separa totam humiditatem per distillacionem. Confeccio aque sexte: Recipe omnia ossa dicti caponis sive galline et f. 64rb  bene minute pistata pone in cucurbita cum alembico super cineres; / recipe totum liquorem cum distillacione […].

**Catalan**

Tu pendràs l'aygua de vida e separa'n sa humiditat tota per distillació; e la substancia de l'aygua, qui és pur or, tu metràs a part; e dedins la humiditat vejetal metràs la terça part de ****** [24] ab tota sa substancia, ço és assaber ab la mel e ab la cera. E aquella metràs a fermentar en laugera calor per .iii. dies; e quant més hi està, més val. Puys mit-ho a distillar en bany; e aquesta distillació e fermentació reitera en renovellant la bresca a cascuna segona distillació per quatre vegades aliter broicé e triblé; e aprés ix vegades. La confectio de¹ la segona aygua: Pren una² capó veel³ o una gallina e plomen-lo, / e gita'n los budells e tot ço que és dedins son ventre; e separa los        f. 63vb pes e pus separa'n los ossos. E tota la carn sia picada aliter broicé e triblé; e aprés met-la dedins lo alembich e en bany; distilla tota l'aygua, e aquella mit a part. La confectió de la tercera aygua: Pren la carn de la gallina o del capó e sobre cenres distilla sa humiditat ab foch mijà bé continuat; e guarda't de la combustibilitat de la carn; e mit a part la humiditat. La confectió de la 4ª aygua: Pren de la humiditat simpla de la dita lunaria, e de aquella mit .iii. parts sobre la substancia de la dit carn. Puys tapa la carabasa ab son cubertor de vidre ab cera communa, e posa-u tot sobre cendres per .iii. dies naturalls ab foch de serradura composta. Puis mit-li dessús e distilla tota l'aygua per lo bany, e aquella guarda a part. La confectió de la quinta aygua: Pren de la substancia de la dita gallina o del capó, e sobre cendres separa tota la humiditat per distillació. La confectió de la sisena aygua: Pren los ossos del dit capó o de la gallina, e ben menudament picats mit-los en lo alembich e sobre cendres; pren tota lur liquor ab distillació, e mettes a part.

### ¶ 2

**Latin**

De rectificacione aquarum predictarum distillatarum per cineres: Recipe terciam aquam, primam et sextam; misce insimul; post distilla per balneum, pone ad partem et custodi.

**Catalan**

La rectificació de les .iii. aygues distillades per cenres: Pren la terça aygua e la .v. e la .vi., e mescla-la ensemps. Puys distilla per lo bany e guarda a part.

### ¶ 3

**Latin**

De modo administrandi sanis: Recipe aurum, quod est aqua terminata et humidum radicale congelatum in modum coloris citrini simile auripigmento. Et pone medietatem in prima aqua et cito dissolvetur in aquam gloriosam. De ista accipe ad quantitatem unius coclearis argenti et misce cum

**Catalan**

La manera de la administració […]: Pren l'aur qui és l'aygua termenada en humit radicall congelat en manera de color citrina semblant a or peinent⁴. E mit-ne la meytat en la primera aygua⁵, e tantost se dissolrà en aygua gloriosa. De aquesta aygua pren la quantitat de una cullereta

### ¶ 4

**Latin**

magna quantitate vini albi: et in hieme da sano fleumatico. Si sit colericus, da ei cum aqua simplici. Et melancolico da cum brodio caullium alborum, in quo sit coctum de mutone. Et si sit sanguineus, non des ei de ista aqua, sed illa que sequitur, in vino albo simplici. Accipe de aqua auri ad quantitatem medii coclearis; et manebunt securi ab omni infirmitate et rectificati contra qualitates temporum. Et si sit in estate, fleumatico da cum brodio galline tenere, ubi¹ sit coctum petrosillum. Et si sit colericus, da ei aqua[m], que sequitur, cum brodio galline. Et similiter si sit melencolicus. Et debes dare istam aquam, quando tempus excitatur in sua magna actione aut frigiditatis aut caliditatis.

**Catalan**

d'argent, e mescla ab gran quantitat de vin blanch: e dona-lo al sa fleumatich en ivern. E si és colerich, da lui ab aygua simpla. E al malencolich, dona lui ab brou de cols blanques on sia cuyt moltó. E si és sanguini, no li dons de aquesta aygua, mas de aquella que's segueix ab vin blanch simplex. Pren de l'aygua de l'or a la quantitat de una cullereta; e estaran segurs de tota malaltia e rectificats contra la qualitat de temps. E si és estiu, al fleumatich da lui ab brou de galina tendra en lo qual sia cuyt iulivert¹. E si és colerich, da lui de l'aygua qui's segueix ab brou de galina. E així matex si és melancolich. E deus donar aquesta aygua quant lo temps se excita en sa gran actió, o en fret o en calt.

### ¶ 5

**Latin**

Et cum velis dare infirmantibus, amministra ut sequitur: Recipe aliam medietatem auri et dissolve in aqua secunda caponis. Et si infirmus sit fleumaticus, da ei medium coclear argenti aque auri cum duabus partibus aque quarte. Et similiter facies, si infirmus sit sanguineus. Et si sit colericus, adiunge ei duo coclearia trium aquarum rectificatarum. Similem viam facies melancolico. Non oportet te dare aliud aut facere, quoniam infra tres dies sanabitur aut multum meliorabitur. Et non cures cognoscere infirmitatem, quoniam discreta natura suo instinctu dedit virtutem lapidi dissoluto sanandi omnes infirmitates et rectificandi seipsam, sicut magis large diximus in »Tractatu aquarum medicinalium«. Et in simili forma potes amministrare summam medicinam corpori humano. Verumtamen, quoniam illa sit multum digesta et depurata, tam per industriam artis quam per industriam nature ad summum temperamentum ducta, non oportet amministrare cum dictis aquis, sed solum petere ab infirmo, in quo cibo habet appetitum eorum recipiendi. Et sic de illo, quamquam sit contrarius, amministra ei ad quantitatem unius grani millii semel sive pluries aut in vino vel in scutella aut in salsamentis sive in brodio aut in liquore spisso sive tenui aut claro, secundum ingenium quod scies apponere, vel habet appetitum […]. Fili, ista medicina habet respectum contra omnes infirmitates calidas et frigidas, naturales et accidentales, quia omnia reducit ad equalitatem. Quando volueris mutare ab una terra in aliam et velis portare dictam medicinam tecum, simplicem seu compositam, congela eam et post pone in vitro et porta illam tecum et utere ea, sicut diximus tibi, per disso-

**Catalan**

E si la vols donar als malats, administra-los en aquesta manera: Pren l'altra meytat de l'aur e dissol-lo en l'aygua segona del capó. E si lo malalt és fleumatich, da lui meja² cullereta d'argent […] ab .ii. parts de la quarta aygua. E semblant faràs que sia sanguini. E si és colerich, ajusta més .ii. culleretes de les .iii. aygues rectificats. Semblant via faràs al malencolich. No't cal far ni fer altra cosa³, si dins .iii. dies le pacient és sanat o fort millorat. No haies cura de conexer la malaltia, *car cest indici ne garrist e purge l'om de tout mal*; car saviesa⁴ de natura per son instinch ha dat virtuts a la pedra dissolta de bé e tost sanar totes malalties e de rectificar si matexa, així com més largament havem dit en lo »Tractat de⁵ les aygues medicinals«. En semblant manera pots administrar la sobirana medicina al corsos⁶ humanals. Totes vegades, com aquella sia molt digesta e depurada, tant per la industria de la art, quant per / la industria de natura, al sobiran tempe-    f. 64ra rament reduyta, ne la't cal amministrar ab les dites aygues, mas solament demanar al malalt de qual vianda ha més appetit de reebre, *e lui fetes appa-* *reler e mengna[r] de celle, e non obstant qu'elle soit contraire a sa maladie, e luy* *amministres de la dit sovereigne medicine a la quantité du gres du gran de* *miller*. E ab aquella, per contraria que sia, amministra-li a la quantitat de un gra de mil una vegada sens plus, o en salsa o en la escutella on sia sa vianda o en vi o en brou o ab liquor espesa o ab clara, segons l'engeny que tu hi sabràs metre o el haurà appetit, e il garirà⁷ certament. Ffill, aquesta medicina ha reguart contra totes malalties caldes o fredes, e naturals e accidentals. […] Quant tu volràs mudar de terra en terra e volràs portar la medicina damunt dita simpla e composta, conjela-la e puis mit-la en vidre e porta aquella a tu, e usa-la així com te havem dit per dis-

### ¶ 6

**Latin**

lutionem ipsius in liquore potabili aut alio viatico, in quo volueris; unf. 64va    de virtutes habet tantas, que sunt incredibiles ignorantibus, / iam sicut plene diximus in »Tractatu lapidarii«. Et quando de ipsa volueris amministrare leproso, da ei cum aqua frigida communi; et intoxicato cum vino albo.

**Catalan**

solució de aquella en liquor potable o en vianda là on tu serràs; car virtuts ha tantes les quals són incredibles als no conexents ella, axí com plenarament havem dit en lo »Tractat lapidari«. E quant aquella volràs amministrar al lebrós, dona lui ab aygua freda comuna; e als entuxegats, ab vin blanch; e similiter homini sano etiam alla [sic].

#### Apparatus (Latin side)
- 1. Coperto da macchia e riscritto sul margine.

#### Apparatus (Catalan side)
- 1. In interlinea.
- 2. Scil. un (cfr. infra).
- 3. Scil. vell (cfr. supra).
- 4. Cfr. cat. orpiment.
- 5. Ms. laygua.
- 1. Ms. *inhivert* (in interlinea *dieta persilli*); cfr. lat. *petrosillum*.
- 2. Scil. *mitja*.
- 3. In interlinea.
- 4. Ms. *savisa*.
- 5. Ms. *me de*.
- 6. Ms. *coros*.
- 7. Ms. *gaura*.

---

## f76r -> Part II, Ch. 18
**Tier:** CONFIRMED (Phase 628 8D-matching) — **but INCONCLUSIVE under Phase 641 Catalan atom-decode and excluded from C1959 Test B verification.** The 8D residual feature alignment holds; the operational atom-decode against the matched Catalan recipe doesn't show clean structural-anchor support. Tier label retained for traceability of Phase 628 work; current evidence position is weaker.  
**Recipe:** Element separation (silver-plate test)  
**Title (Latin):** *Tercia operacio, que est creare lapidem de dicta substancia elementorum preparata²*  
**Title (Catalan):** *La terça operació, que és crear la pedra de la dita substancia preparada dels 4 elements*  
**Folio refs in MS:** f. 51ra, f. 50vb, f. 50va  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['249_L', '250_L']`, Catalan `['249_R', '250_R']`

### ¶ 1

**Latin**

Fili, tercia operacio nostri lapidis est ut reducas aerem, qui significatur per M post suam rectificationem cum O, qui reducitur cum L, quoniam ipsa duo sunt elementa sicca nature fixe. Coniunge ergo O compositi rubei cum L, quod est compositi albi, ut mixtio, que fit per confortacionem, sit 5 profectibilior. Preparacio de O et L fit, ut ipsa recuperent maiorem humiditatem per attraccionem […]³. Quoniam tu potes scire quod omne corpus

**Catalan**

Fill, la terça operació de la nostra pedra és que tu retornes l'ayre, que és significada per M aprés sa rectificatió ab O qui es reduix ab L, per ço car los dos són elements sechs de natura fixa. Ajusta adonchs O del compost roig ab L qui est del compost blanch, a fi que la mixtió que's fa per confortació sia més profitable. La preparació de O e de L se fa a fi que ells recobren maior humiditat per attracció que no han perdut en lur calcinació. Car tu pots saber que tot corps discontinuat no pot esser sans calcinació, per la qual és

### ¶ 2

**Latin**

discontinuatum esse non potest sine calcinacione, per quam privatur ab omni humiditate. Et ideo, cum sit siccum et evacuatum a tota sua humiditate spirituali, libenter bibit suum humidum aquaticum. Et si nos hic intelligas, intelliges id, quod dicimus in nostra »Theorica«, in capitulo quod incipit: «Fili, intencio nature», super illo verbo, quod dicimus de perfecta preparacione, alias operacione, que succedit perfectam purificationem elementorum supradictorum. Fili, ista preparacio prevalet omni auro, quoniam per eam fiunt lapides preciosi et omnes margarite. Igitur, pro consequendo effectum talis operacionis, accipe M et ipsum dividas in duodecim partes, alias duas, ad pondus de O et de L. Quoniam necessarium est ut custodias medietatem de M et plus, et quod alia pars sit equalis ad pondus de O et de L divisa in duodecim partes; quamlibet partem pones cum O et cum L, omnibus insimul mixtis infra vas simile aliis. Sed nos clamamus ipsum 'ymen' pro isto regimine. Et post claudas tuum vas cum suo coopertorio vitri et cum fina cera et pone in ignem fimi, ut ibi nutrias eum cum parva aqua primo et post cum maiori, sicut tibi monstrat natura in educacione infancium. Et non sis negligens imbibere terram de quindecim diebus in quindecim, secundum quod comedet et convertet; et non tedeat te reiterare hoc multociens. Et dumf. 51ra  modo¹ invenies quod eam converterit / et fuerit sicca, pone in igne sicco per diem naturalem. Postea da ei plus de M et fac totum sicut diximus. Quoniam non potes in isto opere errare, dum tamen habeas pacienciam in sua longa nutricione. Fili, ibi videbis multos colores, de quibus non cures, quousque materia terminetur in finis pulveribus albis sive in forma terre foliate albe in colore margaritarum talquearum. Et si eam videbis in forma pulveris multum subtilis, scias quod est maioris fortitudinis et maioris virtutis mineralis sulphuree, pro congelando mercurium et transmutando omnia corpora metallica post elixacionem. Fili, nolimus hic tibi longum sermonem facere, ne intellectus sit impeditus propter verba. Quoniam satis potest tibi sufficere nostra »Theorica«, quam potes convertere in veram practicam per istam, quam tibi damus. Hec est res quesita et terra foliata congelans et congelata et nostrum arsenicum et nostrum sulphur completum ad album pro faciendo elixir ad argentum. Operare ergo, fili, et fac exinde medicinam ad rubeum, sicut tibi dicemus, cum istud sit completum album sulphur non urens, cum quo habet fieri.

**Catalan**

privat de tota humiditat. Per ço, cum sia sech e buyt de tota sa humor spirituall, molt volente[r]s beu son humit aquatich. E si tu nos entenes acy, entendràs ço que havem dit en nostra »Theorica«, ço és assaber en lo capitol que començà: «Ffill, la entenció de natura», sobre aquella paraula [que] nós havem¹ dita de la perfeta operació aliter preparació succehex la pu/rificació    f. 50vb dels element subradits. Ffill, aquesta preparació val² tot or, car per ella se fan pedres preciosos e tots margarits. Donques, per aconseguir lo effects de tal preparació, pendràs M e aquell diviseràs en³ .xii. aliter dieux parties al pes de O e de L. Car la meytat de M, e més, és mester que tu guardes, e que l'altra⁴ part sia equall al pes de O e de L [...]⁵ tot ensemps mesclat dedins [...] als altres. Mas nós lo appella[m] 'ymen' per aquest regiment. E aprés taparàs ton vexell ab ton cubertor de vidre e ab fina cera, e mit-lo al foch de fems, e aquí lexa-la nodrir ab petita aygua primerament, e aprés ab maior, axí com natura monstra en la educació dels enfants. E no sies pereròs de imbibir la terra de 15 dies en 15 dies, segons que veuràs que menjarà e convertirà; e no t'enuies⁶ de reiterar açò moltes vegades. E quant troveràs que ella haurà convertit e serrà sech, mit-lo en foch sech per una dia naturall. E aprés dali més de M, e fes tot axí com te havem dit. Car tu en aquesta obra no pots gens errar, sol que haies paciencia en sa longa nutrició. Ffill, aquí veuràs molts colors, dels quals no haies cura en tro a tant materia se termine en fines polveres blanques⁷ o en forma de terra fullada blancha en color de margarita talquearua. E si la veies en forma de polvera mult subtill, sapies que ella és més de gran força e de maior virtut mineral sulferenca, per congelar mercuri e transmudar tots los corsos metallins aprés sa elixació aliter translació | ha contra lixationem aliter abnixacionem. Ffil, no't volen⁸ ací fer lonch sermó, a fi que⁹ l'entenimet no sia empachat per parauls. Car assats te pot bastar la nostra »Theorica«, la qual pots convertir en vera practica per aquesta que't donam. Açò és la cosa demanada, e la terra fullada congelant e congelada e lo nostre arsenich e lo nostre sofre, qui és complit a blanch per fer elexir a argent. Obra donchs, fill, e fe medicina al roig, axí com te direm, com ja complit lo sofre blanc no cremant ab lo qual se ha a fer.

#### Apparatus (Latin side)
- 1. Ms. solis solis.
- 2. Cfr. figure 8-11.
- 3. Lacuna per 'saut du même au même' (cfr. testo catalano).
- 1. Corretto in: quando.

#### Apparatus (Catalan side)
- Ms. e per.
- 1. Ms. haverem.
- 2. Ms. va.
- 3. Ms. ex.
- 4. Ms. atra.
- 5. Lacuna per 'saut du même au même' (da "de L" a "cum L").
- 6. Scil. enujes (lat. non tedeat te).
- 7. Ms. blan blanques.
- 8. Scil. volem.
- 9. Ms. qui.

---

## f84r -> Part II, Ch. 14
**Tier:** CONFIRMED  
**Recipe:** Gold dissolution (balneum + putrefaction)  
**Title (Latin):** *De secunda parte solutiva*  
**Title (Catalan):** *De segona partida solutiva*  
**Folio refs in MS:** f. 48vb  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['244_L']`, Catalan `['244_R']`

### ¶ 1

**Latin**

Fili, postquam tuum compositum album putruerit per mensem et f. 49ra         medium, tunc animabitur et magna virtute multum / preciabitur. Et ab isto separabis elementa, in modum quod sequitur. Tu recipies vas, ubi est materia; et pones alembicum superius, inserendo coopertorium; et illud bene lutatum collocabitur in balneo marie, secundum quod scies cum tua discrecione et tibi demonstrabitur per nostram doctrinam. Primo recipies aquam per distillacionem cum levi igne, equaliter continuando, quousque non possit aliquid distillari. Tunc cessa ignem et permitte refrigidari. Et post accipe vas et pone super cinerem, parum et parum vigorando ignem. Distilla aerem totum mixtum cum suo igne, et illum pone ad partem cum suo proprio receptorio; et illud quod remanet in fundo combustum, est terra sicca et nigra. Questio: Quare distillatio aque fit in calido et humido, cum aeris fiat cum igne sicco? Et ideo operatio nobis demonstrat nature subtilis quod convenit extrahi aquam per substanciam humidam cum calore multum subtili, cum artificialiter non possit esse subtilior separacio in eo, quod videtur quod aqua non sustineat ignem stans in sua natura. Ideo est necesse quod cum igne corrupto habeat separari. Sed aer et ignis, qui sustinent ignicionem, distillantur per cineres, quando partes grosse et colores terrestres ascendunt superius in aere. Sic divides tria elementa, que significantur per L M N. Quoniam ad album non est ignis nostri lapidis necessarius; sed ad rubeum sunt quatuor elementa, significata per O P Q R.

**Catalan**

Fill, quant ton compost blank haurà podrit per un mes e mig, adonchs serà ell animat e de gran virtut molt preat. E de aquest separaràs los elemens en la manera que·s segueix. Tu pendràs lo vexel on és la materia e metràs hi lo alembich dessús, levantne lo cubertori; e aquest bé lutat asetaràs¹ en lo bany de maria segons que tu sabràs a ta discrecció, e serrà demonstrat per la nostra doctrina. E primerament reebràs l'aygua per distillació ab lauger foch egualment continuat en tro aytant que res no pusca més distillar. Adonchs cessa lo foch e lexa l'aygua refredar. Després pren lo vexell e met-lo sobre cendres, e poch a poch vigorant lo foch. Distilla l'ayre tot mesclat ab son foch, e aquell met a part ab son receptor; e ço que remandrà al fons cremat, és terra secca e negra. Questió: Per que la distillació de l'aygua se fa en calt humit, com de l'aire se sia fet ab foch sech? És per ço, car rahó nos demostra de natura subtil que·ns cové traur[e] l'aygua per substancia humida ab calor molt subtil, cum artificialment no pusca esser més subtill separació en ço qu'est vist que l'aygua no sosté ignició estant en sa natura. E per ço est mester que ab foch corrumput se haien a separar. Mais l'air e lo foch que sostenen ignició se distellen per cenres quant les partides grosses e les colors terrestres se'n munten sus en l'aire. Axí departiràs los tres elemens qui sunt significats per L M N **. *** ******.****.***.***** [23]² són les quatre elemens significats per O P Q R.

---

## f79r -> Part III, Ch. 12
**Tier:** strong-supported  
**Recipe:** Mercury sublimation -> elixir  
**Title (Latin):** *Rubificacio mercurii sublimati cum suomet igne ad faciendum elixir rubeum*  
**Title (Catalan):** *La rubificació del mercuri sublimat ab son mateix foch per fer elixir roig*  
**Folio refs in MS:** f. 61rb, f. 61vb, f. 61va, f. 62ra  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['280_L', '281_L']`, Catalan `['280_R', '281_R']`

### ¶ 1

**Latin**

Recipe mercurium sublimatum ad album, sicut diximus tibi, et dissolve in aqua mercurii, a qua extraxisti ignem lapidis mercuriosi, in qua dissolvatur ignis duri lapidis tam substancialiter quam essencialiter. Et quando dicimus 'substancialiter', hoc dicimus pro substancia ignis; et quando dici5 mus 'essencialiter', dicimus ad differenciam qualitatum, quas aqua accipit a substancia ignis. Postea recipe aquam per distillacionem, quousque totum congeletur. Et alia vice reduc aquam super mercurium, ut sua unctuositas superetur cum aqua per distillacionem. Postea alia vice reitera; et tercia vice distilla. Et 10 post paulatim fortifica tuum ignem, quousque videas maximam rubifica-

**Catalan**

Pren mercuri sublimat e blanch axí com te havem dit, e dissol-lo en aygua del mercuri, de la qual és tret lo foch de la pedra mercuriosa, en la qual sia dissolt lo foch de la pedra axí substancialment com essencialment. Quant diem 'sub/stancialment', diem per la substancia del foch; e quant      f. 61va diem 'essencialment', diem a la differencia des qualitats que l'aygua ha preses de la substancia del foch. Aprés separes l'aygua per distillació en tro sia tot congelat. E altra vegada retorna l'aygua sobre lo mercuri que si hi ha unctuositat aliter a fi que soit la unctuositat se supere⁴ ab l'aygua per distillació⁵. Puis altra vegada retorna sur le dit mercuri; e terça vegada distilla. E aprés paulatinament fortifica ton

### ¶ 2

**Latin**

cionem. Et si est aliquid, quod non ligetur cum igne lapidis, hoc ascendet [...] virtute ignis totum album. Continua ergo tuum ignem, donec videas quod sublimativum sublimetur, et fixum, quod est in fundo, rubificetur. Et super istam terram fixa tua elementa, sicut diximus tibi, si bene nos 15 intellexisti; et habebis a mercurio elixir completum.

**Catalan**

foch, en trou veies vostre dit feu molt fort rubificar. E si res hi ha que no sia ligat ab lo foch de la pedra, allò se'n muntarà e sublimarà per la virtut del foch tot blanch. Continua donchs ton foch en tro veies que'l sublimatiu se sia sublimat, e el fix que és baix ou fons du vayssel se sia rubificat. E sobre aquest fixe sos elements axí com te havem dit; si tu nos has entès o oït, hauràs del mercuri elixir complit.

#### Apparatus (Latin side)
- 1. de aggiunto sopra.

#### Apparatus (Catalan side)
- 1. Ms. derrarera.
- 2. Cfr. se dissolle, p. 407 (ma il testo lat. ha 'expoliatur'; corr. dispolle?).
- 3. In interlinea la prima -i-.
- 4. Ms. sepere.
- 5. Segue en tro sia tot congelat (espunto).

---

## f82r -> Part III, Ch. 22
**Tier:** strong-supported  
**Recipe:** Lunaria maceration (3-day sealed)  
**Title (Latin):** *Quomodo debeas intelligere elementa*  
**Title (Catalan):** *Com tu deus entendre los elements                                             f. 65ra*  
**Folio refs in MS:** f. 65va, f. 66ra, f.65va, f. 66rb  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['290_L', '291_L', '292_L']`, Catalan `['290_R', '291_R', '292_R']`

### ¶ 1

**Latin**

Fili, tu debes intelligere quod omnia elementa sunt composita, quia natura non habet se sustentare nisi in materia simplicis compositi cum aliis elementis compositis ex materia fina et clara elementaliter per virtutem elementativam, in qua sustentatur virtus vegetalis. Igitur, fili, nostra ele5 menta sunt in quolibet eorum; et quodlibet eorum est in forma circuli; et circulus cuiuslibet vocatur simplex mixtum. Fili, nomen cuiuslibet elementi accipimus racione sue proprietatis determinate, sicut aquam per suam frigiditatem et ignem per suam caliditatem; et sic de aliis. Adhuc respectu talis determinacionis dicimus nos 10 corpora animalium, vegetabilium et mineralium 'elementa', quodlibet secundum denominacionem elementi dominantis in quolibet illorum. Et ideo, quia successive naturaliter sunt generata ex elementis elementatis secundum gradualitatem sue diverse simplicitatis et grossiciei aut mediocritatis, accipiunt diversas formas in diversis elementatis, de quibus aliqua 15 vocamus elementa; et maxime corpora mineralia et omne illud, cuius pars est similis suo toto. Et ideo nostra medicina vocatur 'ignis', quia determinate ipsa habet complexionem ignis, non obstante quod fuit composita ex elementis compositis et contemperata ex qualitatibus contrariis. Et quia unum composi20 tum intravit in aliud, accipit formam homogeneam per veram mixtionem, que dicitur unio rerum [alteratarum], que appetunt miscibilitatem pro veniendo ad composicionem cum potencia instrumentorum dictarum rerum alteratarum, scilicet elementativitatis et vegetativitatis. Tunc perfectus est spericus circulus ex quatuor circulis spericis, qui faciunt quadran25 gulum, postquam fuerunt divisi, veluti iste figure tibi ostendunt¹. Quapropter, fili, intellige quod nostra elementa sunt composita et elementata; quia in terra nostra est ignis illuminatus, et ideo ipsa est calida per f. 65vb      complexionem ei appropriatam / ex parte ignis; et similiter aqua et aer in ipsa contenti<s>. Et ab illis participat secundum magis et minus proprie30 tates suarum extremitatum; et sic est de aliis elementis. Quia in nostra aqua habentur ignis et aer et terra, sed ignis in profundiori omnium suarum regionum quiescit magis remote quam terra et aer. Et ideo istum ignem multiplicamus cum calore aliorum; et istum contemperamus cum frigiditate

**Catalan**

Fill, tu deus entendre que los elements són tots compost¹, car natura no ha a sustentar sinó és en la materia del simple compost ab los altres elements compost de materia fina e clara elementadament per la virtut elementativa, en la qual és sustentada la virtut vegetal. Per ço, fill, los nostres elements són en cascú de aquells; e cascú de elles és en forma de cercle; e lo cercle de cascú és appellat simple mesclat. Fill, lo nom de tot element nós prenem per rahó de sa determinada proprietat, axí com aygua per sa frigiditat e lo foch per sa calididat; e axí dels altres. Encara a l'esguart² de tal determinació, diem nós los corsos animals, vejetals e minerals 'elements', cascú segons la denominació de l'element que domina en cascú d'els. E per ço, car successivament són naturalment enjenrats dels elements elementats segons la gradualitat de lur diversa simplicitat e grossitat o mediocritat, prenent diverses formes corps elementats, dels quals alguns nós appellam elements; e maiorment los corsos mineralls, e tota cosa d'ells aliter altres, per que aliter de laquella la una part és semblant a son tot. E / per ço nostra medicina és appellada 'foch', car determenadament ella ha complexió del foch no contrastant que ella sia estada composta de com-   f. 65rb posts elements e contemperada ab qualitats contraries. E car la un compost és entrat en l'altre, ha pres forma homogenea per vera mixtió, qui és dita unió de las coses alterades, les quals appetien miscibilitat per venir a composició ab lo poder a els instruments de les dites coses alterades, ço és assaber elementativitat e vejetativitat aliter elementatiu e vejetatiu. Adonchs és perfet lo cercle espherich de .iiii. cercles espherichs que fien quadrangle quant eren divisius axí com aquestes figures te demonstren. Per que, fill, entén que los nostres elements són compost e elementats; car en la nostra terra és lo foch alumat, e per ço és ella calda per la complexió a ella appropiada de part del foch; e semblantment l'aygua e l'ayre en ella continguts. E ab aquelles participa segons lo més e lo meyns de la proprietat de lurs extremitats, e axí és dels altres elements. Car en la nostra aygua ha foch e ayre e terra, mas lo foch a³ pus pregon de totes ses regions se reposa més remotament que no fe l'ayre e la terra. E per ço aquest foch nós multiplicam ab la calor dels altres; e aquest contemperam ab la fredor de l'aygua

### ¶ 2

**Latin**

aque et fixamus cum humiditate aeris, que est materia sulphuris. Quia humidum est materia nostri ignis, sicut oleum est luminis, quod ardet in lampade. Et in tali materia, fili, applicatur et augmentatur noster ignis, donec fiat substancia; quia ignis terre, qui comburit et cremat massam, mutatur in subiectum, alias se mutat in subiectum; et aqua mercurialis fit sulphur non urens per temperamentum frigiditatis aque incombustibilis; et postea redit in substanciam aeris, quando mittitur in fusione, alias mittit se in fusione. Iste est noster ignis, quem debes figere per certa regimina reduccionis in materia humida, que est terminanda in materia secreti sulphuris per humidum radicale. Quoniam, quanto magis ipsum occultas in subtili materia, tanto magis multiplicatur suum humidum radicale. Et quanto plus multiplicatur, tanto potencius operatur suum humidum radicale. Et quanto magis sua materia est subtilis, tanto subtilius et occulcius penetrat cum firma et radiosa alteracione. Ideo, fili, sit amonestatum advisamentum huius naturalis operacionis, que fit cum igne, quem multum sapienter debes gubernare cum longa mora. Quia cum pluralitate temporis adiunguntur pluralitates parcium in una substancia, in qua est unita una virtus potencialis, que est tota essencialiter composita ex igne in humido radicali. Et ideo, cum sit ignis compositus ex pluribus partibus ignitivis, habet potenciam ignibilem ad igniendum alias partes. Et cum ille partes sint ignificative, sunt colorative, que habent potenciam colorabilem, ad colorandum et tingendum alias partes; et sic devallatur colorativum ab ignificativo; et ab ignificabili [venit colorificabilis]; et ab ignificare venit colorificare. Et de hoc est ideo, quia nostra tinctura non est nisi purus ignis, compositus ex multis partibus coessencialibus, adiunctis in unum per artem claram et scitam. Unde dicimus quod ignis noster facit in una hora illud, quod sol et stelle faciunt in eorum mineris in mille annis. Considera ergo, fili, ad hoc; et intellige quomodo et qualiter ignis noster nutritur et crescit, quousque veniat ad illam potenciam, per quam monstrat virtutem sulphuream per suam proprietatem, qua congelat omne argentum vivum. Fili, accipe exemplum experimentale a racione nostre philosophie, que monstrat tibi potencialiter in nostro magisterio quod, sicut calor naturalis simplex terminat suum humidum naturale simplex, digerendo et congelando illud secundum subtiliacionem cibi limitati ad proporcionem virtutis caloris naturalis digerentis, sicut manifestat primum regimen reductionum in substanciam sulfuris, consimiliter calor compositus et multiplicatus in humido maturato digerit, maturat et congelat materiam primam crudam argenti vivi volgaris, compositam in terminacione forme metalli.

**Catalan**

e fixam ab lo humit aquatich, qui és materia del sofre. Car lo humit és materia del nostre foch, axí com lo oli és de la lum que crema en lampa. E en tal materia, fill, és applicat e augmentat lo nostre foch, en tro és fet sofre; car lo foch de la terra, que crema la mas[s]a, se muda en lo subiech; e l'aygua mercuriall és feta sofre no cremant per lo temperament de la fredor de l'aygua incombustible; e aprés se'n torna en la substancia de l'ayre quant se met en fusió. Aquest és lo nostre foch, lo qual tu deus figir per certs regiments de reductió en la materia humida, qui és terminadora en materia del secret sofre per lo humit radicall. Car com tu més les occultes en sa subtill materia, més se multiplica son humit radicall. E de quant pluis se multiplica e més poderosament obra son humit radicall. E quant més sa materia és subtil, més subtilment e occultament penetra ab ferma e radiosa alteració. Per ço sia amonestat e divisament de aquesta naturall operació que's fa ab foch, lo qual molt saviament e soferans deus governa[r] ab longa triga. Car ab pluralitat de temps se ajusten pluralitats de partides en una substancia en la qual és unida una poderosa virtut que és tota essencialment composta de foch en lo humit radicall. E per ço, com sia foch compost de moltes partides ignitives, ha poder ignibilench de ignir altres parts. E com aquells parts sien ignificatives, són colorificatives, que han poder colorabilench de colorar e tiner altres parts; e axí devalla colorificatiu de ignificatiu; e de ignificable [...]; e de ignificar ve colorificar. E açò és car nostra tinctura no és sinó pur foch compost de moltes partides coessencials ajustades en un per art clara e sabuda. Donchs diem que nostre foch fa en una¹ hora [ço] que'l sol e les estreles fan en les mineres en mil anys. Considera, fill, açò, e entén com e en qual manera lo nostre foch se nodrex e crex en tro ell ve a quell poder per lo qual mostra / virtut sulfurenca per sa pro-   60  f.65va prietat, qui congela<t> tot argent viu. Ffill, pren exemple² experimental de la rahó de philosophia nostra, qui't mostra poderosament en nostre magisterii que, sicut la calor naturall simple termena son humit naturall simple, e digerent e congelant aquell segons la asubtiliació de la vianda a la proporció de virtut de la³ calor naturall digerent, axí com manifesta lo primer regiment de les reductions en substancias e sofre, tot axí la calor composta e multiplicada en lo humit madurat digerex, madura e congela la materia crua de l'argent viu volgar composta en la terminació de forma de metall.

### ¶ 3

**Latin**

Igitur, fili, multiplica ignem in substancia subtili nostri argenti vivi; et congelabit illud totum corpus compositum. Quia natura tibi ostendit quod 75 infans natus a papilla mamillarum non potest sumere cibum fortem, nisi per calorem matris primo digeratur, coquatur et subtilietur et in succum lactis convertatur, quod est cibus et proprium nutrimentum infantis. Et hoc requiritur, fili, generaliter in suis primis actionibus, ad nutriendum suos fetus, ad finem quod hoc, quod non poterat capere in suo cibo grosso, 80 quod trahat et sugat in substancia lactis, quousque sit nutritus et possit f. 66ra    sumere / cibum grossum. Fili, tuum speculum sit generacio et nutritio infantis modici humanalis, ad creandum nostrum lapidem. Et hic iacet totum regimen sanitatis, ad quod omnis bonus phisicus debet multum suum intellectum 85 applicare.

**Catalan**

Donchs, fil, multiplica lo foch en lo substancia subtill de nostre argent viu; e congelarà aquell tot compostament. Car natura te mostra que l'infant nat de lo mocet¹ mamillar no pot pendre vianda fort, si per la calor naturall de la mare no és primer digesta, cuyta o asubtiliada e en such de let convertida, qui és vianda e propri nodriment all enfant. E açò requer, ffill, generalment natura en ses primeres actions per nodrir son fetus, a fi que ço que no ha pogut pendre en vianda grossa, que tire e suque en substancia de let, en tro sia nodrit e pusca pendre vianda grossa. Ffill, ton mirail sia la generació e nudrició de l'enfant poch humanal per crear nostra pedra. E aquí jau² lo regiment de sanitat, al qual tot bon fisich deu molt son entenimentt adherer.

#### Apparatus (Latin side)
- 1. Le figure cui il testo si riferisce mancano. Cfr. tuttavia la figura 34.

#### Apparatus (Catalan side)
- 1. Segue <del simple compost> (cassato: errore di anticipo).
- 2. -t in interlinea.
- 3. Ms. ha.
- 1. Ms. o-.
- 2. Ms. -pel.
- 3. Ms. a.

---

## f103r -> Part III, Ch. 16
**Tier:** strong-supported  
**Recipe:** Ferment multiplication (multi-chamber)  
**Title (Latin):** *Multiplicacio fermentorum per viam mixtionis¹*  
**Title (Catalan):** *La multiplicació dels ferments per vía de mixtió*  
**Folio refs in MS:** f. 63ra, f. 62rb, f. 62va, f. 62vb  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['283_L', '284_L']`, Catalan `['283_R', '284_R']`

### ¶ 1

**Latin**

Fili, si B ponas coqui cum C, que sunt due camere, misce totum insimul per resolucionem liquefactionis cum calore solummodo. Sed, si cum aqua lapidis facis tuam mixtionem, illa erit melior, quoniam est² unionis rerum miscibilium, que iam alterantur per opera supradicta. Recipe ergo, fili, fermentum de B et illud de C; et quodlibet ipsorum proiciatur in aqua rubea. Ex post coniunge aquas et evapora eas in balneo marie; et post pone super cineres et fac modo, quo dixi tibi in precedenti capitulo. Et si videas quod non fluat, adiunge ei de aere, quantum pertinebit, quia quanto comminuitur in liquefactione, tanto trahitur aqua per distillacionem. Et ideo reveletur tibi separacio quintarum essenciarum. Restitue ei totum illud quod perdidit, et plus; et fecisti multiplicacionem compositi³ super aliud compositum. Et sic matrimonificabis gummam cum gumma et fermentum cum fermento. Illud postea potes multiplicare usque ad finem, de qua multiplicacione numquam potest videri finis, cum sit infinita. Quando nos dicimus 'plus', dicimus hoc propter equipollenciam ad racionem sensus, cum sit certum pondus limitatum a natura. Iccirco tibi habet operari racio intentiva et sensus artiste, inclinando ad optatum, quod natura desiderat; et hoc potes scire cito, si parum et parum imbibas, quousque videas eam fluere, quoniam aliud non oportet facere; pondus ibi non est. Et ideo dicimus, et plus cum cautela scita quam sensus cognoscere debet in rebus invisibilibus, nisi esset per assentimentum sui intellectus, quo utitur cum cautela, donec videat signum, quod ei monstrat mensuram, per quam sua natura ponitur in fusione, que est tocius sui operis perfecta directio. Et quando dicimus 'infinita', dicimus hoc ad differenciam vite hominis. Et si velis multiplicare dictum fermentum compositum et illud ducere ad maiorem composicionem multiplicacionis, adiunge ei cameras B F D H I. Et si maxime multiplicacionis eam volueris esse, misce cum aliis cameris per viam practice. Ego et quidam sociorum meorum evacuavimus omnes quatuor cameras prime partis tabule infra tres annos cum magna sollicitudine; et credebamus quod totam evacuavissemus infra tres menses, nisi divisio superascendisset, alias supervenisset, ad voluntatem omnium.

**Catalan**

Fill, si B metràs aliter mets tu ab C, que són les dues cambres, mesclar s'[h]a¹ tot en un per resolució de liquefactió ab calor solament. Mas si tu ab l'aygua de la pedra vols fer ton mesclament, aquell serrà millor, car és pres de unió de les coses miscibles que ja són alterades per les obres sobredites. Pren donques, fill, lo ferment de B e aquell de C; e cascú de aquels sia gitat en l'aygua roia. Puis ajusta les aygues e evapora aquells en lo bany de maria; e aprés mit-ho sobre cenres e feu² en la manera que t'havem dit en lo precedent capitol. E si veus que no flua, ajusta-li de l'ayre tant quant se pertendrà, car de tant quant se minua en liquefació, de tant se'n tira l'aygua per distillació. E per açò te sia revelada la separació de les quintes essencies. Restituit-li³ tot ço qui ha perdut e més, e hauràs fet multiplicació de composició sobre altre compost. E axí matrimonificaràs gomma ab gomma e ferment ab ferment. Aquell pots tu multiplicar, puys la fi de la qual multiplicació jammés no's pot hom veure, cum sia infinida. Quant nós diem⁴ 'més', diem-ho a la equipollencia a la rahó dell seny, com sia cert pes limitat a natura. Per ço y [h]a obrar la rahó ententiva e lo seny de l'artist' enclinat a l' optat que natura desira; e açò pot post saber, si poch a poch la abeura en tro la veia fluir, car altre […] pes no y ha. E per ço diem, e més ab cautela sabuda, que lo seny deu entendre en coses no visibles, sinó és per lo sentiment de son entaniment que usa ab cautela en tro veu lo senyal que li mostra mesura, per la qual sa natura se met en fusió, que és de tot cors dreta perfecció. E quant diem 'infinida', diem-ho a la differentia de la vida de l' hom. E si vols multiplicar lo dit ferment compost e aquell portar en pus gran composició de multiplicació, ajusta-li la cambra B F D H I. E si de més gran multiplicació la vols esser, mesclalo ab les altres cambres per vía practical. Yo e algú de mes companyons evacuams totes les .iiii. cambres de la primera partida de la taula dins .iii. anys⁵ ab gran sollicitud; e creem que tota haguessem evacuada dedins .iii. meses, si divisió no y fos sobrepujada ab le volentat de tots.

### ¶ 2

**Latin**

Fili, si intres in artem per viam practice, cito videbis omnes suas fortitudines. Fili, in introitu magisterii est mora, quoniam primo separaciones elementorum sunt longe et rectificaciones eorum et creacio summi medii mineralis, quod tenet omnes virtutes minerales ligatas in suo ventre per ingenium magisterii, per quas totum, quod dictum est, fit. Et si omnia ferf. 62vb      menta de D misceas cum illis de G, sicut tibi diximus in prac/tica primarum camerarum, fiet sine alia multiplicacione elixir et fermentum potestatis infinite.

**Catalan**

Ffill, si tu és entrat en l'art per via de practica, tantost veuràs totes ses forces. Ffill, a l'entrar del magisterii és la estada, car al commençament¹ les separacions des elements són lon/gues e les ratificacions² de aquels e la creació del sobiran mijà mineral qui té totes les virtuts minerals ligades en       35  f. 62va son ventre per engeny de magisterii, per les quals tot ço qu'és dit és feyt. E si tots los ferments de D mescles ab los ferments de G, axí com te havem dit en la practica de les primeres cambres, serrà feyt sens altra multiplicació elixir o ferment de poder infinit.

#### Apparatus (Latin side)
- 1. Cfr. figura
- 33.
- 2. Segue uno spazio bianco.
- 3. Ms. compositum.

#### Apparatus (Catalan side)
- 1. Ms. sa.
- 2. Scil. fac.
- 3. Probabile latinismo (restituite).
- 4. Ms. -i.
- 5. In interlinea iii tours.

---

## f76v -> Part III, Ch. 15
**Tier:** strong-supported  
**Recipe:** Ferment conversion (join H + bind)  
**Title (Latin):** *Fermentum liquefactionis et eius multiplicacio*  
**Title (Catalan):** *Lo ferment de liquefacció e multiplicació de aquella*  
**Folio refs in MS:** f. 62ra  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['282_L']`, Catalan `['282_R']`

### ¶ 1

**Latin**

f. 62rb     Quando feceris fermentum tincture illud […] in liquefaccione, coniungendo ei H secundum pondus quod scis et sensus demonstrat per opus nature, donec totus fixetur infra condensorium. Et postea pones illi quintam litteram; illam fixabis, quousque videas quod fundatur sicut cera sine fumo; et cum tanto fiet fermentum liquefactum prime camere. Istud in infinitum potest multiplicari per opera secreta mixtionis facte diversimode.

**Catalan**

Quant tu hauràs fet lo ferment de tinctura, aquell convertiràs en liquefacció, ajustant-li H segon lo pes que saps, e lo seny te demonstrarà per la obra de natura, en tro sia tot fix dedins lo condensori. E après tu metràs y la cuinqua⁴ littera; aquella fixaràs tro veies que's fona com a cera, sens fer fum; e a tant serrà fet lo ferment liquefet de la primera cambra. E aquest in infinit se pot multiplicar per les obres secrets fetes de mixtió en diversa manera.

#### Apparatus (Catalan side)
- ¹ Lacuna per 'saut du même au même' (da "aque rubee" a "aque rubee").
- 2. Scil. fac.
- 3. Ms. marien.
- 4. Scil. quinta (latinismo grafico?).

---

## f77v -> Part III, Ch. 27
**Tier:** supported  
**Recipe:** Furnace specification  
**Title (Latin):** *Modo dicemus quomodo debes considerare subiecta cum quatuor condicionibus et quomodo accipiuntur in arte*  
**Title (Catalan):** *Ara direm com deus considerar los subiechs ab .iiii. condicions, e com      f. 67vb són preses en l'art*  
**Folio refs in MS:** f. 68ra  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['298_L', '299_L']`, Catalan `['298_R', '299_R']`

### ¶ 1

**Latin**

Fili, subiecta accipiuntur hic in nostra arte dupliciter, videlicet propter instrumenta, sicut superius nominavimus, per que nostrum magisterium completur. Alia subiecta instrumentalia non pertinent nisi rebus vivis, que ars non potest retinere propter raritatem materie illarum. Et propterea non potest illas vivaciter generare, nisi intellectus suppleat cum manu lenta aliquorum experimentorum divinalium suppletorum per scienciam nature stellate, organizantis armonias cum instrumento sensualitatis, que per artem experiencie se aperuit et revelavit, natura alta coadiuvante per aliqua multociens, in tantum quod loqui certas res et movere faciebamus cum alif. 68rb 10 quibus vir/tutibus infixis et monstris alte influencie, sicut faciunt lapides, verba et herbe, in quibus multe virtutes sunt¹ influxe et innate per [quintam] essenciam alte nature et matris accidencium et nature basse per bonos suos motus et subtiles mixtiones; unde virtutes causantur in materiis simplicibus ligatis cum grossis secundum intellectum sensualem nature alte, 15 que postea facit mirabilia, sicut tibi dicemus cum bono intellectu in volumine »De rebus sensibilibus«. Habes intelligere illo modo subiecta in loco materie, in qua stant supradicta instrumenta, que faciunt transmutamentum illius secundum specialem differenciam proprie et naturalis concordancie et terminacionis dicte 20 materie. Iccirco, fili, tibi dicimus quod habes considerare modum istorum subiectorum tam materialiter quam instrumentaliter cum quatuor condicionibus, ut per illa remaneat² intellectus habituatus et condicionatus ad discurrendum dicta subiecta materialiter et instrumentaliter per sua elementa, ad simpliciandum grossa materialia et sublimare instrumentalia 25 insimul, cum instrumentalia semper sint cum materialibus; et secundum hoc, quod quodlibet subiectum tam materiale quam instrumentale extat condicionatum per suam essenciam et naturam. Quia subiectum materiale et instrumentale, quod est in leone viridi, habet unam condicionem per se et aliam condicionem in fumo congelato.

**Catalan**

Fill, los subiechs se prenen en aquesta art ab dobla manera, ço és assaber per instruments, axí com dessús los havem nomenat, per los quals nostre magisterii se complex¹. Los altres subiechs instrumentals no's pertanyen sinó a coses vives, los quals art no'ls pot retenir per la raritat de lur matèria. Per ço no'ls pot vivament generar, si l'entenement no y supplex ab ma lenta de alguns experiments divinals supplits per la scientia de natur' estelada, organizant les armonies de l'estrument de sensualitat qui per art de experiencia s'és tot dessecretat e revelat, natura coadiuvant la alta per algunes moltes veus, en tant que parlar² certes coses [e] moure les fem ab algunes virtuts infigides e les monstres de la alta influencia, axí com les pedres e paraules e erbes, en qui molta virtut és influïda e nada per la quinta essència de la alta natura e mare dels accidents e de natura baxa per sons bons moviments e subtils mesclaments; d'on les virtuts se causen en les matèries simples ligades ab les grosses segons l'entenyment sensuall de natura la alta, qui despues³ fa maravelles, axí com direm ab tot bon entenyment en lo volum »De les coses sensibles«. Ha⁴ a entendre per altra manera los subiechs en loch de matèria en la qual [estan] los sobredites instruments, qui són transmudament de aquell segons⁵ la especial differencia de lur propria e natural concordança e determinació de la dita matèria. Per ço, fill, te diem que tu has a conside/rar la     20   f. 68ra manera de aquestes subiech axí materialment com instrumentalment ab .iiii. condicions, a fi que per aquelles remanga lo enteniment abituat e condicionat a discorrer los dits subiechs materialment e instrumentalment per lurs elemens, a simpliciar los grossos materials e sublevar los instrumentals tot ensemps, com los instrumentals sien tots temps ab los materials; e açò segons que cascun subiech axí materiall com instrumentall està condicionat per sa essencia e per sa natura. Car lo subiech instrumental e material, que és en leó vert, ha una condició entre ell e l'altre condició en lo fum gelat.

### ¶ 2

**Latin**

In leone viridi dominatur subiectum materiale racione sue grosse substancie, que impedit instrumentale, quod non oportet separare ab illo per ignem extraneum, quousque sit fixum in substancia subtili cum operacione. Et in fumo gelato dominatur instrumentale racione raritatis sue materie; et specialiter postquam acceperit ex aqua vel ex aere, in quibus sunt anime vivificative, que vivificant ipsum. Et postea sunt res vivificate¹ cum re viva. Et huius damus exemplum de argento vivo sublimato, quod, dum est vivificatum, facit impressionem; sed postea totum hoc perdit per sublimacionem, nisi post reciperet eam cum sublimacione, que portat ei vitam, per operacionem scitam et cognitam per intentivum operatorem. Prima condicio, fili, quam debes habere cum sciencia habituata, est quod a quolibet subiecto trahas suam proprietatem virtuosam sub conservacione sue essencie cum propria diffinicione; et per viam practice formate, trahas de potencia ad actum, ut sit differens ab alio subiecto. Secunda condicio est quod in practica sit conservata differencia subiectorum tam materialium quam instrumentalium, sicut vegetativa leonis viridis differt a vegetativa sulphuris et virtute et in substancia, que est fumus de aqua congelata per grossiciem corporalem fixam et perfectam. Tercia condicio est quod concordancia, que est inter unum subiectum et aliud tam materialiter quam instrumentaliter, non destruatur; sicut concordancia que est inter terram et aquam aut aerem et aquam aut aerem et ignem. Eciam inter corpus et spiritum, quoniam spiritus concordat cum corpore in corporalitate et instrumentalitate cum differencia concordancie, et corpus cum spiritu in spiritualitate similiter cum differencia concordancie per concordanciam unitatis, quam dissolucio fecit ex ambobus. Quarta condicio est quod nobiliori subiecto attribuantur nobiliora elementa participancia in essencia cum nobilioribus principiis, sicut lapis, cum creatus est, est nobilior in virtute et in substancia, quam sit in sua minera, ex qua exivit; et aer magis quam aqua; et ignis magis quam aer; et mixtum magis quam simplex. Et per tales condiciones potest habituari intellectus illius, qui voluerit esse practicus in operacionibus nature, mediante secreto perfectivo contento in tractatu compendioso, qui dicitur »Vademecum de numero philosophorum«.

**Catalan**

En leó vert domina lo subiech materiall per rahó de sa grossa substancia que empacha lo instrumentall, lo qual no has pas ops que·s partesca de aquí per foch estrany, a tant en tro sia fix en substancia subtill ab operació. E en lo fum gelat domina lo instrumentall per rahó de la raritat de sa materia; e per especial, aprés que ella ha pres de aygua o de ayre en qui són ses ànimes vivificatives que vivifiquen. Aprés, així com cosa vivificada obrarem la cosa viva, e de tot donam exemple de l'argent viu sublimat quant és vivificat, que fa empressió; mas aprés ho pert per sublimació, si aprés no la cobra ab sublimació que li porta la vida per operació sabuda e coneguda per lo prudent e autentic obrer. La primera condició, fill, que tu deus haver ab sciencia abituada, si és que de cascun subiech tragues sa proprietat virtuosa sots la conservació de essencia ab propria diffinició; e per via de pratica formada la tragues de potencia en acte, a fi que sia¹ different de l'altre subiech. La segona condició és que en la pratica sia conservada la differencia dels subiechs axí materials cum instrumentals, axí com lo vegetatiu del leó vert differrí ab lo vegetatiu del sofre en virtut e en substancia, que és fum de aygua gelada per grossitat corporall fixa e de perfectió. La tercera condició si és que la concordança que és entre la un subiech e l'altre, axí materialment com instrumentalment, no·s destrouesca; axí com la concordança que és entre la terra e l'aygua e lo ayre, e l'ayre e lo foch, e entre lo cors e l'espirit. Car lo espirit se concorda ab lo cors en corporalitat e instrumentalitat ab differencia de concordança, e lo corps ab lo espirit en espiritualitat semblantment ab differencia de concordança per la concordia de la unitat que ha nostra dissolució feyta de abdosos. La 4ª condició és que al pus noble subiech sien attributs los pus nobles elements participancia en essencia ab més nobles principiis, axí com la pedra quant és creada és pus nobla en virtut e en substancia que no és sa minera de la qual és exida; e lo ayre més que l'aygua; e lo foch més que l'ayre; e lo mesclat més que·l simple. E per tals condicions pot esser abituat l'entendiment de aquell que vol esser pratic en les ovres de natura, mijançant lo secret perfectiu contengut en lo tractat compendiós qui és dit »Vademecum de numero philosophorum«.

#### Apparatus (Latin side)
- 1. Segue infixe cassato.
- 2. remaneant corretto in -at.
- 1. Ms. virificata.

#### Apparatus (Catalan side)
- bien que experience en a eu sans cause. Pour ce que comme le feu naturel soit instrument direct a la forme il convient doncques qu'il soit droit mené par ung autre tendant a la forme et cestuy n'est pas feu commun comme l'effect d'icelluy ne soit <mes> mais aultre chose que eschauffer mais amcois [sic] vertu celeste estante en challeur et espirit et ceste vertu enformé en mouvement par la chaleur comme non excedente. Icelle dicte vertu soy mouvant et ceste vertu de propre mouvement devient en propre matiere elle informe et maine droite la chaleur naturelle departant son humide il quel est matere et nature du metal terminant a propre forme ainsi que en nulle magniere il ne oeuvre fors que soulx la vertu celeste.
- 1. Precede com.
- 2. Ms. parles (errore di anticipo: -es).
- 3. Scil. després (forse per incrocio con despuis).
- 4. Scil. has (cfr. lat. habeas).
- 5. Precede e.
- 1. Ms. sa.

---

## f81v -> Part III, Ch. 18
**Tier:** supported  
**Recipe:** Potable gold / water of life  
**Title (Latin):** *De aquis et medicinis pro humano corpore*  
**Title (Catalan):** *Del aygues e medicines per le cors humanal*  
**Folio refs in MS:** f. 63va  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['285_L']`, Catalan `['285_R']`

### ¶ 1

**Latin**

Nunc dicemus composicionem aque potabilis simplicis, que fit de sanguine fixato per naturam, ad confortandum humorem radicalem humanum. Recipe aquam, quam tibi supradiximus, que habet potestatem dissolvendi aurum sub conservacione sue speciei vel forme; et subtilia ipsum per viam continuacionis cum inhumacione in balneo et in levi decoccione. Et post pone aurum dissolutum in cucurbita vitri et distilla aquam et separa totum humorem. Et remanebit substancia auri sicca in fundo vasis. Post accipe de lunaria et distilla humorem per alembicum, donec videas quod per diminucionem sue sulphureitatis non poterit plus cremari. Continua tuam distillacionem in alio receptorio et illam aquam recipe, quousque super caput alembici nulle appareant vene. In istam aquam proicies substanciam auri, et cito dissolvetur in aqua vegetali racione mercurii. Rectifica suum mercurium a fleumate, donec videas quod cremet, et post misce eam cum aqua prima cum substancia auri. Et est aqua vite.

**Catalan**

Ara direm la composició de l'aygua potable simpla, que·s fa de sanch fixat per natura per confortar lo humit radicall humanal. Pren l'aygua que dessús te havem dit, que ha poder de sobre aliter dissolre or sots la conservació de sa specie o forme; e subtilia-lo en aquella per via de continuació ab inhumació en bany e laugera decocció. E aprés posa l'or dissolt en una carabaça de fin vidre, e distilla l'aygua e separa'n tota la humor. E estarà la substancia de l'or al fons del vexell tota secca. Puis pren de la lunaria e distilla la humor per alembich, en tro veuràs que par la diminució de sa sulphureitat no porà pus cremar. Continua ta distillació en altre receptori e aquella aygua pren en tro sobre'l cap de l'alembich no apparrà res de venes. En aquesta aygua gitaràs la substancia de l'or, e tantost se dissolrà en l'aygua vejetall per rahó del mercuri. Rectifica son mercuri de la fleuma, en tro veies que creme, e puis mescla-la ab primera eau ab la substancia de l'or. E és aygua de vida.

#### Apparatus (Latin side)
- 1. Seguono quindici righe bianche. L'intera colonna 63rb è occupata dalla figura 33.

#### Apparatus (Catalan side)
- 1. Ms. fui͛ʳ (spazio bianco dopo l'iniziale, sufficiente a una lettera).
- 2. Ms. demost.
- 3. Scil. és (anglonorm.).
- 4. Ms. fre.
- 5. Ms. jam.
- 6. Ms. e.
- 7. Cfr. testo latino, cap. I.63.

---

## f82v -> Part III, Ch. 28
**Tier:** supported  
**Recipe:** Vessel specification  
**Title (Latin):** *Modo dicemus de temperamento lapidis; et quomodo fit ex quatuor elementis cum distemperamento*  
**Title (Catalan):** *Ara direm del temperament de la pedra; e com està en los .iiii. elements ab distemperament                                                               f. 68rb*  
**Folio refs in MS:** f. 68vb  
**Paragraph alignment:** ⚠ Latin=3, Catalan=2  
**Source pages:** Latin `['300_L', '301_L']`, Catalan `['300_R', '301_R']`

### ¶ 1

**Latin**

Noster lapis, fili, manet in omnibus suis elementis et totus est in quolibet illorum per separacionem eorum, que vocatur mixtio rerum mixtarum, quia ipse est totus in terra, scilicet mortuus sicut arena de sabulo stat in illo sine vita propter magnam siccitatem. Adhuc magis tibi dicimus quod ipse 5 est totus in aqua sua, scilicet ibi iacet mortificatus: propter frigus multum magnum stat sine vita. Adhuc dicimus quod ipse est totus in suo aere, scilicet quia ibi stat submersus in magno mari suffocatus cum calore suo naturali per humiditatem excellentem. Adhuc dicimus magis quod lapis noster est totus in igne, scilicet cum iacet ibi imbibitus nimio calore, manet illic 10 combustus sine condimento cuiusquam actus vite […]¹ nisi in mixtis. Si ergo qualitates excellentes omnes insimul debite copulentur in uno mixto, videlicet quod lapis calidus et lapis frigidus et lapis siccus et lapis humidus equaliter omnes insimul se temperent, erit complexio peculiosa, que portat nascenciam veri temperamenti per actionem actualem qualita15 tum primarum excellencium, que sunt in elementis. Et iccirco tibi manifestatur quod nulla complexionalis qualitas est excellens, nisi elementa

**Catalan**

La nostra pedra, fill, està en tots sos elements, e tota és en cascú de aquells aprés lur separació, qui és appellada mixtió de les coses mesclades, car ella és  f. 68va tota en la terra, mas morta axí com arena de sabble està en ella sens vida per gran siccitat. Encara més te direm que ella és tot en aygua sua, mas car aquí està tan mortificada: per fredor fort gran, està sens vida. Encara't direm que ella és tota en son ayre, mas car aquí està negada en la gran mare, e sufogada és sa calor naturall per la humiditat excellent. Encara diem més que la nostra pedra és tot en lo foch, mas con iau¹ allí embeguda de molt gran calor, està allí cremada sens condiment de tot acte de vida. Per la qual cosa te sia revelat que en nengun dels extrems estants de qualitats excellents està condició temperada per la qual resulte tots los actes de vida, sinó és als mesclats. Si donchs les qualitats excellents tots ensemps degudament se copulen en un mesclat, ço és assaber que la pedra calda e la pedra freda e la pedra secca e la pedra humida degudament tots ensemps se tempren, serrà complexió peculiosa que porta naxença de ver temperament per la actió actual dels qualitats primeres excellents qui són als elements. E per ço te sia manifestat, com nenguna complexional qualitat és excellent, los elements ab ella mesclats se rompen ab actió ajustada per mutació en tro pervenen a aquell mijà en lo qual la especie del perfet mesclat pot esser constituïda. Per ço, donques, fill, com ja conste que nengun acte de vida estiga sens mijà, ajusta l'aygua ab terra, axí com natura requer, en partides minudes, en tro resulte la nostra pedra que no és ne la un ne l'altre, e serrà dit un monstre qui no és de natura no complida. Quant l'aygua serrà gelada per la vapor de sa terra, és mijà approximat de natura de ayre. Mas car encara té molt de la natura secca del primer extreme, no's poria encara contemperar ab lo ayre sinó greument no's feça per aver engressió aliter empressió; car encara no participa tant ab ell quant fa ab la terra. Retorna, donchs, per diverses vegades de l'aygua sobre la terra blancha, a fi que's fixe ab ella; e sia mijà més approximat a l'ayre que a la terra, e que'l fret compreme lo humit ab la part pregon. Adonchs serrà la mijà proporcional en seccor a la colorabilitat de la natura de l'ayre per la virtut del fret aquatich. Ajusta, donchs, l'ayre humit ab lo sech proporcionalment temperat per l'aygua, a fi que la virtut de la un extrem sia exaltada sobre l'altre

### ¶ 2

**Latin**

cum eis mixta rumpantur cum actione / aggregata per mutacionem, donec perveniat in aliud medium, in quo species mixti perfecti potest constitui. Ob hoc igitur, cum ita sit quod nullus actus vite sit sine medio, adiunge 20 aquam cum terra, sicut natura requirit, in minimis partibus, quousque resultet noster lapis, qui non est unum nec aliud, et dicetur unum monstrum, quod est in natura incompletum. Quando aqua erit gelata per vaporem sue terre, est medium approximatum nature aeris. Sed quia adhuc tenet multum de natura sicca primi extremi, non poterit adhuc contempe25 rari per aerem, nisi graviter fiat ad habendum ingressionem; quia adhuc non participat tantum illo, quantum facit cum terra. Reduc igitur per diversas vices de aqua super terram albam, ut fixetur cum illa; et sit medium magis approximatum aeri quam terre et quod frigidum comprimit humidum in profundiori. Tunc erit medium proporcio30 natum ei siccitate ad colorabilitatem naturalem aeris per virtutem frigidi aquatici. Adiunge ergo aerem humidum cum sicco et proporcionabiliter temperato per aquam, ut virtus unius extremi exaltetur super aliud; et

**Catalan**

[...] axí com lo sech per lo humit e lo humit per lo sech tot ensemps s'espesexca per la continuació de ses partides, a fi que la empressió, quant serràs en ta proiectió, adquisica humiditat del sech. Car nulla empressió és feta sinó és per humit ligat en lo ventre del sech e el sech en lo ventre de l'humit. E lo ligament és fet per la passió de la un e de l'altre per decocció en foch de temperança. E aprés tal ligament, quant lo humit sent lo fret, lavors se amaga ell all ventre del sech. Mas quant lo sech troba calor excellent, de aquells el se defen en lo ventre de l'humit. E lo humit és retengu[t] per lo sech a fi que ell pusca soferir tot foch. / E per humit és dada empressió en    f. 68vb lo sech, qui és aygua [...] de morts. Ffill, si tal sech per si retornat en cors novell ha una vegada pres empressió per la virtut de la unió de l'humit ab lo sech, en tal manera que en la batalla del foch é[s] lo sech deffès¹ per lo humit de la separació de ses partides, en semblantment que l'humit sia prohib<u>it per lo sech a exalabilitat², a cert e greument³ porà tal cors perdre d'aquí⁴ en avant la dita empressió ja feta. Per ço, fill, estudia't que quant lo vapor del sech serrà estada en fum exaltada e constreta⁵ e expressat per lo humit fret constrictiu en novell cors luent e resplendent així com a cristall, que aquell ab lo humit calt ayrench laxatiu, a fi que les partides del sech constret se continuen en la lamina cristallina blancha fluent, ingredient, trairent [sic]⁶ e penitrant sens vaporabilitat e mortalitat nulla, mas ab solidat, qui és propria virtut de l'humit radical e d'argent viu, e vida de tots los corsos liquables e des altres semblantment, que ne són pas liquables. E així és terminat en la fi demanada lo foch dels philosofs, per sos proprias mijans apportat a lur fi perfectiu per levitat de açò que demanes. Donchs los vers⁷ principis reguarden a lur fi e les fins aquells refluen per los mijans⁸, així com és ja vist en la proiecció venguda de metall en metall [se] termena per lo conservaments dels naturals mijans en qui són los extrems de fins e de principis. E per ço te diem que la pedra no és feta en tro per .iiii. vegades sia molt bes dissolta e aprés congelada. Car adonchs la malaltia mijana dels extrems ja gitada a l'extrem temprat se'n torna de grat per la nobla natura de sa mijanitat; car així com és dit, jamés natura va a sa perfecció sinó per lo passament de ses propriis mijans. Car adonchs se confranjen e de tot se distemperen les qualitats primeres de tots los elements en tro venen del grat al propri temperament dels⁹ individuals que són pura natura dels sobirans metalls.

### ¶ 3

**Latin**

unum contemperabit reliquum, sicut siccum propter humidum et humidum propter siccum insimul inspissantur per continuacionem suarum partium, ut impressio, quam queris in tua proiectione, acquirat humiditatem sicci. Quia nulla impressio fit, nisi propter humidum ligatum in ventre sicci et siccum in ventre humidi. Et ligatura fit per mutuam passionem unius et alterius per decoccionem in igne temperato. Et post talem ligaturam, quando humidum sentit frigidum, illico absconditur in ventre sicci. Sed, quando siccum reperit calorem excellentem, ab illo se defendit in ventre humidi. Et humidum retinetur per siccum, ut possit sustinere quemlibet ignem. Et per humidum datur impressio in siccum, quod est aqua et vita mortuorum. Fili, si tale siccum per se reversum in corpus novum semel acceperit impressionem virtute unionis humidi cum sicco, taliter quod in pugna ignis siccus defendatur per humidum a separacione suarum partium, similiter quod humido prohibeatur exalabilitas propter siccum, tarde et graviter poterit illud corpus perdere impressionem iam ante factam ab illis. Iccirco, fili, studeas quod, quando vapor sicci in fumo est exaltatus et constrictus et expressus per humidum frigidum constrictum in novum corpus, lucens et resplendens sicut cristallus, quod illud inspissetur cum humido calido aereo laxativo, ut partes sicci constricte continuentur in laminas cristallinas albas fluentes, ingredientes, tergentes et penetrantes absque vaporabilitate et mortalitate aliqua, sed cum soliditate, que est propria virtus [humidi] radicalis et argenti vivi et vita omnium corporum liquabilium et aliorum similiter non liquabilium. Et sic terminatur finis optatus ignis philosophorum, per sua propria media apportatus ad suum perfectivum per entitatem huius, quod petis. Tunc vera principia respiciunt ad suum finem et fines in illa refluunt per media, sicut iam visum est in proiectione, que venit ex metallo et in metallum terminatur per conservacionem naturalium mediorum, in quibus sunt extrema finium et principiorum. Et ideo tibi dicimus quod lapis non est factus, donec per quatuor vices sit bene dissolutus et postea congelatus. Quia tunc egritudo media extremorum, iam proiecta ad extremum temperatum, reducitur gratis per naturam sui medii; quia, sicut dictum est, natura numquam vadit ad suam perfectionem, nisi sit per transitum de suis propriis mediis. Quia tunc infringuntur et totaliter distemperantur qualitates primarie omnium elementorum, quousque sponte veniant ad proprium temperamentum individualium, qui sunt pura natura supremorum metallorum.

**Catalan**

*(missing)*

#### Apparatus (Latin side)
- 1. Lacuna per 'saut du même au même' (cfr. testo catalano).

#### Apparatus (Catalan side)
- 1. Scil. jau.
- 1. Ms. e doffes.
- 2. Ms. exabilitat.
- 3. Ms. engreument.
- 4. Ms. de aqui.
- 5. Ms. confreta (cfr. lat. constrictus).
- 6. Possibile adattamento, attraverso trejent, di un latinismo terjent (cfr. lat. tergen- tes).
- 7. Ms. los vers los vers.
- 8. Ms. -atis.
- 9. Ms. als (cfr. lat. individualium).

---

## f112r -> Part III, Ch. 11
**Tier:** supported  
**Recipe:** Red mercury tincture (cohobation)  
**Title (Latin):** *Modo dicam de creacione mercuriorum rubeorum, ad faciendum tincturam rubeam a¹ sua propria substancia, ad consequendum operaciones pre-*  
**Title (Catalan):** *Ara direm de la creació dels mercuris roigs per fer tinctura roia de sa propria substancia, per aconseguir les operacions sobredites*  
**Folio refs in MS:** f. 61rb  
**Paragraph alignment:** ⚠ Latin=2, Catalan=1  
**Source pages:** Latin `['280_L']`, Catalan `['280_R']`

### ¶ 1

**Latin**

dictas

**Catalan**

Fill, tu prendràs la liquor derrera¹ que pus greu és separada per distillació sobre cendres; e aquella distillaràs en bany per .iii. vegades. E aprés cascuna distillació, metràs l'aygua sobre la terra viscosa, e aquella terra tost se dissolrà en la dita aygua. Separa alt<e>ra vegada aquella aygua per cendres; açò's fa per entenció que l'aygua traga lo foch qui és en la terra e sia guardat per tinctura. Distilla aquella liquor altra vegada per bany, a fi que's dissoulle² del foch, e mit lo foch tot temps a part tout ensemble; et soit come dit est par tant de fois distillat que le plus de l'ame de la terre soit extraite en feu sech. Distillada que sia, tira més de la ànima de la terra ab foch sech. Et guarda emperò que la terra no's rubifich, car tantost cremaria la tinctura del sofre blanch en lo qual se deu fixar lo foch de la nostra pedra mercuriall. E açò reitera en tro que veies la terra comminuida³, defallent de tota humiditat. Puis pren lo foch e lavalo ab la distillació et calcinació en tro que sia bé roig així com a foch ardent. Ffill, aquest feu se trau ab calor e humor, e l'altre ab seccor e fredor se cree e engenre.

### ¶ 2

**Latin**

Fili, tu accipies liquorem ultimum, qui gravius separatur per distillacionem in cineribus; et illum distilla in balneo ter. Et post quamlibet distillacionem pone aquam super terram viscosam, et illa terra cito dissolvetur in dicta aqua. Separa alia vice dictam aquam per cineres; et hoc fit inten5 cione, ut aqua extrahat ignem, qui est in terra, et custodiatur pro tinctura. Distilla illum liquorem alia vice per balneum, ut expolietur ab igne, et pone semper ad partem. Distillata aqua, trahe plus de anima a terra cum igne sicco. Cave tamen quod terra non rubificetur, quoniam tam cito cremaretur tinctura sulphuris albi, in quo debet fixari ignis nostri lapidis mer10 curialis. Et hoc reitera, quousque videas terram comminutam deficientem ab omni humiditate. Postea recipe ignem et lava eum cum distillacione et calcinacione, donec sit bene rubeus, sicut ignis. Fili, iste ignis extrahetur cum calore et humore; et alter cum siccitate et frigiditate […].

**Catalan**

*(missing)*

---

## f112v -> Part III, Ch. 1
**Tier:** supported  
**Recipe:** Lunaria -> quicksilver  
**Title (Latin):** *Liber faciendi mercuria et elixiria illorum*  
**Title (Catalan):** *[Senza rubrica]*  
**Folio refs in MS:** f. 59rb, f. 59ra, f. 59va  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['273_L', '274_L']`, Catalan `['273_R', '274_R']`

### ¶ 1

**Latin**

Fili, necesse est ut intelligas operaciones per quas creantur nostra argenta viva. Et de post, si scias hoc et habeas scientiam cognoscendi nostrum argentum vivum, habebis artem integratam, quoniam non est nisi una operacio sola, quae fit per modum, quem nos tibi dicemus. Tu accipies de liquore mercuriali vel lunarie quantum volueris et de ipsa per distillacionem separabis elementa. Sed primo separabis aquam f. 59rb      fleumaticam, in qua moratur spiritus mortificatus. Et continua distilla/ cionem tuam in balneo, donec videas distillare aquam animatam, que incipit cremari. Et eam distilla ad partem, quousque totum receperis, quod per illum calorem poterit distillari, et fleuma extrahatur, sicut manifestat signum sue cremacionis. Istam divides in duas partes: et unam custodias pro creando mercurios, et de alia extrahes elementa sine ulla combustione sub conservacione proprietatis sulphuris et argenti vivi. Isto modo pone istam partem predicte aque animate supra feces, que erunt in similitudine picis fuse sive liquefacte in fundo vasis. Et tam cito pone superius alembicum cum receptorio et accende ignem de serraturis compositis, sicut diximus in principio nostre practice. Et iste ignis continuetur, quousque totum illud, quod distillari poterit, distilletur per equalitatem dicti ignis. Et fiat ista distillacio in balneo marie. Et postea pone vas in igne cinerum facto de serraturis, et distilla oleum, et in fine distillacionis permitte infrigidari materiam cum toto vase. Post reduc primum liquorem, qui est inter aquam primam et oleum, super feces et reitera tuam distillacionem, ut iam dictum est, donec feces remaneant sicce et arse; et quod humidum unctuosum sit omnino sublevatum sicut anima in substancia spiritus. Fili, natura nostri spiritus operatur cum omnibus rebus et omnia superat. Et per eum fit nigredo, albedo et rubedo, dum tamen ipsum scias bene miscere. Et mixtio illorum fit sicut tibi diximus, quoniam unum ingreditur per alterum et fugit in ipsum, et rarifactum impletur a condenso, et

**Catalan**

Fill, t'és ops que entenes les operacions per les quals se creen los nostres argents vius. Aprés, si saps ho, has scientia de conexer lo nostre argent viu; hauràs l'art integrament, car les operacions de tots no és sinó una cosa qui's fa per la manera que ara't direm. Tu pendràs de la liquor mercuriall aliter | o lunaria quant en volràs, e de aquella per distillació departiràs les elements. Mas primerament separaràs l'aygua fleumatica en la qual està mortificat lo esperit. E continua en bany ta distillació en tro que veies distillar per l'aygua animada que comença a cremar. E aquella distilla a part; e quant tot ço qui's porà distillar per aquella calor hauràs reebut, la fleuma ne serrà fora, axí com manifesta lo senyall de son cremament. E aquella partiràs en dues parts: e la una part guardaràs per crear los mercuries; e de la segona trauràs los elements sens tota combustió desús la conservació de la proprietat del sofre e de l'argent viu. En aquesta manera tu mettràs la dita part de l'aygua animada sobre les feces, que serràn en semblança de pega fusa o liquefeita al fons de vexell. E tantost mit¹ lo alembich dessús ab ton receptor, e encén lo foch de serradura composta, com dit havem dessuis al començament de la nostra pratica. E aquell se continue en tro tot ço que porà distillar sia distillat per equalitat del dit foch. E soit fet ceste distillacion en bany marie. Aprés mit-ho en foch sech cinerench ab aquell continuitat de serradura; distilla lo oli, e a la fi de la distillació lexa refradar² la materia ab tot lo vexell. Puys retorna la primera liquor que és entre l'aygua primera e l'oli sobre les feces e reitera ta distillació axí com ja és dit, en tro que les feces esteguen totes seques e arses; e que l'humit unctuós sia tot sublevat axí com a ànima en la substancia de l'esperit. Ffill, natura del nostre esperit obra en totes coses e tota cosa sobremunta. E per aquella se fa negror, blanchor e rojor, mas que ben ho sapies mesclar. E'l mesclament de aquells és fet axí com te havem dit, car la un se'n entra en l'aultre e se'n fug en aquell, e lo clar se complex de l'espès, e

### ¶ 2

**Latin**

condensum subtiliatur a rarifacto. Et totum hoc fit per solucionem et calcinacionem in levi igne. Et iste ignis debet continuari, quousque elementa amplexentur cum terminacione humiditatis eorum. Que terminacio alias et eorum terminacio est, et paulatim ardeantur, donec in illo lento igne desiccentur. Et scias, fili, quod unum ardet alterum et commiscet; et unum coniungit alterum et conservat et docet pugnare contra ignem. Et sic, fili, decoquendo elementa in lento igne, multum gaudent et reducuntur in extraneas naturas, quoniam liquidum omnino comminuitur et convertitur in non liquidum et humidum fit spissum; et isto modo fit corpus spiritus et spiritus fit tingens et fortis et pugnans cum igne.

**Catalan**

l'espex¹ se subtilia per lo clar. E tot açò és fet per solució e calcinació en lauger foch. E aquest foch se deu continuar en tro que les elements se sien abrachats et ensamble liés e conjonts ab terminació de lur humiditat. E la lur terminació és que a poch a poch se sien cremats en tro que en aquell lent foch se sien desiccats. E sapies, fill, que la un crema l'altre e mescla; e la un ajusta l'altre e'l conforta e l'ensenya a combatre contra lo foch. E així, fill, cohent los elements a lent foch, molt se alegren e tornen en estraynyes natures, car lo liquit² de tot se diminuex e's torna en no líquit, [e lo humit] se fa espès; e en aquesta manera se fa lo cors espirit e l'[e]spirit se fa tinent e fort combatiu³ contra lo foch.

#### Apparatus (Catalan side)
- 1. Ms. misc.
- 2. Scil. refredar.

---

## f116r -> Part III, Ch. 4
**Tier:** supported  
**Recipe:** Fixation / fusibility test  
**Title (Latin):** *Fixacio et perfectio illius*  
**Title (Catalan):** *La fixació e la perfectió de aquell*  
**Folio refs in MS:** f. 59vb, f. 59va, f. 60ra  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['275_L', '276_L']`, Catalan `['275_R', '276_R']`

### ¶ 1

**Latin**

Quando sublimaveris et acceperis dictam substanciam puram mercurii, tunc fixabis unam partem ipsius; et nos dedimus tibi modum fixacionis in lapide maiori. Et quando illa pars erit fixa, fixabis postea aliam partem. Tunc reitera sublimacionem partis non fixe supra rem fixam, quousque ipsa similiter fixetur. Quam rem temptabis, si bonam fusionem prestabit super ignem. Et si hoc facit, factum est; sin autem, adiunge de argento vivo exuberato, reiterando suam sublimacionem, donec sit fusile. Et modum exuberacionis cuiuslibet argenti vivi tibi dabimus, si bene nos intellexeris, in practica lapidis maioris, ut est in ista »Practica«, in capitulo illo, quod incipit: «Fili, tu accipies». Sed illa fit de suomet argento vivo, et ideo est illa simplex. Sed, si vis plus compositam et eam volueris de mercurio, dissolve alium mercurium in aqua prima, que exuberata est ab anima dicti mercurii, de qua fit tinctura; et post separa aquam post distillacionem, et sic reitera, distillando et redistillando super suas feces, quousque aquam biberit et traxerit ad ipsam totam humiditatem suarum fecum mercurialium. Fili, ista est humiditas inceratiua, que super omnes alias moratur contra pugnam ignis. Et sic per solam substanciam mercurii facimus nos medicinam excellentem albedinis. Et sicut tibi videtur quod nos dicimus de uno, sic intellige quod nos dicimus de omnibus. Et quando dicimus 'de omnibus', non excipimus ullum, neque volgare neque commune. Et quando dicimus 'commune' dicimus hoc, pro aliquo ipsorum, quod phi-

**Catalan**

Quant hauràs sublimat e presa la dita pura substancia del mercuri, adonchs fixaràs la una part de aquell; e nós te havem dat la manera de la fixació en la pedra maior. E quant aquella part serrà fixada, fixarà aprés l'altra. Donchs, reitera la sublimació de la partida no fixa sobra la cosa fixa, en tro que aquella semblantment² sia fixa. La qual / cosa temptaràs assaiant si   5  f. 59vb bona fusió prestarà sobre lo foch. E si ho [fa], fet és; e si non fa, ajusta-li de l'argent viu exuberat en³ reiterant sa sublimació en tro que sia fusible. E la manera de la exuberació de tot argent viu te havem dat, si nos has entès, en la pratica de la pedra maior, com en aquesta »Pratica«, en lo capitol segon que comença «Tu pendràs». Mas aquell se fa de son matex argent viu, e per ço és ella simpla. Mas si la vols més composta e la vols de mercuri, dissol altre mercuri en l'aygua primera que és exuberada de la ànima del dit mercuri del qual és feta la tinctura; e puys separa l'aygua per distilació, e así reitera en distillant e redistillant sobre ses feces en tro haya beguda l'aygua e tirada a ella tota la humiditat de les feces mercurials. Ffill, aquesta és la humiditat encerativa que sobre totes les altres està contra la batalla del foch. Per que ací, per la sola substancia del mercuri, fem excellent medicina de blanchor. E así com te sembla que nós diem de un, així entén⁴ que nós diem de tots. Quant nós diem 'de tots', nós non gitam nengú ni volgar ni comú. E quant diem 'comú', diem-ho per alguns de aquells que

### ¶ 2

**Latin**

losophi propinquius habent in suo intellectu. Et quando dicimus 'volgare', dicimus hoc pro illo, quod rusticus intendit, quod venditur in ten25 toriis. Sed bene credas quod, ubi est illud commune, ponitur sicut scimus. Et nos, qui illud cognoscimus, scimus cum propria veritate.

**Catalan**

los philosofs han puis propinquament en lur entenement. E quant diem 'volgar', diem-ho per aquell que·l rustech ho entén que·s ven en les tendes. Mas ben cregues que on és lo comú, és posat axí com sabem. E nós, que·l conexem, [conexem] a pròpria veritat.

#### Apparatus (Catalan side)
- 1. Ms. se.
- 2. Ms. semblat-.
- 3. Ms. e.
- 4. Ms. en.

---

## f107r -> Part III, Ch. 44
**Tier:** supported  
**Recipe:** Quicksilver coagulation  
**Title (Latin):** *Modo dicemus quomodo debent corrigi errata; et de possibilitate errandi*  
**Title (Catalan):** *Ara direm com se devem corrigir les coses errades; e de la possibilitat de errar*  
**Folio refs in MS:** f. 80rb, f. 79vb, f. 79va, f. 80ra  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['333_L', '334_L']`, Catalan `['333_R', '334_R']`

### ¶ 1

**Latin**

Fili, impossibilitas regnat in ista sciencia, quod tu possis habere spiritus quintos absque aliqua mutacione materiali de colore in colorem. Ad quos rogo te, ut habeas sollicitacionem taliter, quod omnes colores tibi sint grati, excepta rubedine, que in materia venit post separacionem quintarum substanciarum per ignem stimulativum contra materiam siccam. Fili, tunc quinte essencie, que remanent in sicco, cremantur et consumuntur sua tinctura, quia nolunt esse nisi ut aeres simplices, nec possunt extrahi, nisi sunt cum eis artificialiter; et sua virtute attractiva colligantur cum aeribus aquarum suarum et revivificantur, sicut apparet in ultimo puncto separacionis aquarum intra balneum. Si tu nescis extrahere aerem ex aquis, precare naturam, ut per suam virtutem attractivam tibi velit ostendere. Quia illa tibi monstrabit, quomodo per appetitum illius, quod ipsa perdidit in sua calcinacione, ipsa separat aerem ab aqua cum restauracione, quousque materia virtutis attractive es[t] fere totaliter separata. Et caveas a nimio igne in distillacione aerum, quia corpus rubificaretur et suffocaretur sua virtus attractiva, que tibi dat aeres. Aut, si non esset in gradu suffocacionis, poss<i>et trahere magis, quam indigeres, cum non indigeas nisi aere multum subtili. Trahe igitur ipsum per inhumaciones, quia ille custodiunt tincturas ab omni adustione et restaurant humiditatem perditam et revivificant attractivam virtutem. Et si videas quod corpus esset rubificatum aut sua folia talquea, que in similitudine bresis mutantur multociens, proice cito in suam aquam et in illa coque, donec acceperit vitam albedinis vel nigref. 80ra dinis; et trahes omnes aeres per inhumaciones absque / calcinacionibus factis cum igne extraneo. Fili, tres colores principales sunt tria instrumenta, qui dant cognoscere illud, quod natura volt, et sunt nigredo, albedo et rubedo, sicut tibi diximus in capitulo: «Verumptamen fili». Sed hoc tibi dicimus pro intencione trahendi aeres et corrigendi errata; et caveas ab illis. Verumptamen, quomodocumque sit de omnibus albedinibus et omnibus nigredinibus, cave quod non habeas nisi unicam rubedinem, que debet venire in fine primi

**Catalan**

Fill, impossibilitat regna en esta sciencia que tu pusques haver los espirits quintes sens alguna mutació materiall de color en color aliter de calor en calor. A les quals prech-te que haies sollicitació en tal manera que tots colors te sien agradables, exceptat roior, qui en la materia ve aprés les separacions de les quintes substancies per foch estimulatiu contra la materia secca. Ffill, adonchs les quintes substancies qui estan en sech e's cremen e's consumen lur tinctura, car no volen esser sinó com ayres humits simples, no's poden tirar fora sinó són ab aquells ajustats artificialment; [e] per lur virtut attractiva se sien colligats ab los ayres de lurs aygues e revivificat, axí com pareix al derrer punt de la separació de lurs aygues en lo blanch aliter per lo bany de marie. Si tu no saps traure de les aygues l'ayre, prega a natura que per sa virtut attractiva t'[h]a¹ vulla mostrar. Car aquella te mostrarà com, per lo appetit de açò que ell' a perdut en sa calcinació, ella separa l'ayre de l'aygua ab restauració en tro la materia de la virtut attractiva és prés de tot² separada. / E guarda't de fer molt foch en la distillació dels ayres, car lo cors se rubificaria e soffocaria sa virtut attractiva qui't dona les ayres. O, sinó era al grau de suffocació, poria tirar més que no has mester, con³ no y has ops sinó de   f. 79vb ayre molt subtil. Trau-lo donchs per inhumacions, car aquells guarden les tinctures de tota adustió e restauran la humiditat perduda e revivifiquen la virtut attractiva. E si veies qu'el cors fos rubificat, o ses fulles talqueans, qui en semblant de bresa se muda moltes vegades, gita'l tantost en sa aygua, e en aquella cou-lo en tro haia pres vida de blanchor o de negror; e trau-ne tots los ayres per inhumacions sens calcinacions fetes ab foch estrany. Ffil, les .iii. colors principals són les .iii. instruments qui donen a conexer ço que natura vol, e son negror, blanchor e roior, axí com te havem dit en lo capitol: «Totes vegades, fill». Mas ací te dehim per intenció de traure los ayres e de corrigir les coses errades e gardar-se de aquells. Totes vegades, qu'ell sia de totes blanchors e de totes negrors, guarda't que no y haia sinó

### ¶ 2

**Latin**

gradus. Et si ante venerit, significat combustionem colorum, qui volunt rubificare propter festinanciam aut decoccionem, quam sentiunt ex punctura ignis stimulativi, qui sibi amministratur¹ […] antequam suus pro35 prius motus eis integretur. Et ideo, quantum rubent ante tempus, tantum perdunt de sua tinctura in sua ultima et propria rubificacione, in quanto sua essencia rubificativa colligatur cum extranea materia, que non potest sustinere ignem; et hoc cum ei non datur vera preparacio. Et si hoc intelligas, scies quare sophiste deficiunt a faciendo verum aurum.

**Catalan**

una roior que deu venir a la fi de primer grau. E si enans ve, significa combustibilitat de les colors qui·s volen rubificar per […] lo cuytament que elles senten de la puncuitat del foch estimulatiu, lo qual li és amministrat per malvada enformació enans que·ll proprii moviment los sia entegrat. E per ço, tant com se rubifiquen¹ enans de temps, a tant perden de lur tinctura en lur derrera e propria rubificació, en tant quant lur especie aliter essence rubificativa és colligada ab estranya materia que no pot soferrir foch; e açò com no li sia donada vera preparació. E si açò entens, sabràs per que los sophistes defallen en fer verdader or.

#### Apparatus (Catalan side)
- 1. Lettura incerta (to a te).
- 2. Cfr. lat. fere totaliter.
- 3. Scil. com.

---

## f80r -> Part III, Ch. 21
**Tier:** supported  
**Recipe:** Animal ash chain Ch21 (multi-chapter 21-25)  
**Title (Latin):** *De vasis*  
**Title (Catalan):** *De les vexells*  
**Folio refs in MS:** f. 64vb, f. 65ra  
**Paragraph alignment:** ⚠ Latin=1, Catalan=2  
**Source pages:** Latin `['289_L']`, Catalan `['289_R']`

### ¶ 1

**Latin**

Fili, in omnibus medicinis componendis non indiges nisi solum nostra forma unius vasis, quod est ex tribus peciis, scilicet de uno coopertorio, de uno alembico et de una cucurbita. Sed accipit differentiam nominum secundum differentiam sue operacionis. Nam, quando ipsum est pro intencione distillandi, [dici]tur 'distillatorium' cum suo alembico; et pro intencione dissolvendi, dicitur 'dissolutorium'; et putrefaciendi, 'putrefactorium'; et calcinandi, dicitur 'calcinatorium' et 'mortificatorium'; et pro intencione congelandi, dicitur 'congelatorium' et 'condensatorium' et 'sublimatorium' et 'animatorium' et 'vivificatorium', 'creatorium' et 'inhumatorium', 'attenuatorium' et 'condensorium' et 'ymen'; et semper non est in forma nisi unum solummodo. Sed quelibet medicina requirit suum vas formatum, sicut dictum est, de vitro cum suo coopertorio cumque suo alembico. Fili, quando dicimus in hoc capitulo 'medicina', nos dicimus pro intellectu simplicis per se vel de compositis per se. Simplex est sicut solummodo terra prima aut aqua tantummodo per se sine adiunctione aliorum elementorum; et sic de quolibet ex suis compositis, sicut lapis, qui est compositus vel creatus ex duobus simplicibus elementis, scilicet ex terra et aqua, aut elixir, quod fit de compositis et simplicibus ex compositis, sicut de sulphure et de fermentis, et ex simplicibus, sicut ex aqua et aere. Et ideo, fili, quando aqua preparatur, indiget suo proprio vase facto, ut supra dictum est, sicut medicina simplex, et aer similiter, et sic de aliis elementis et medicinis simplicibus. Quapropter sit manifestum quod, quando due res possunt fieri in uno tempore, nolite successionem temporis, propter defectum vasorum [...]¹ que omnia sunt unius forme et illa forma potest tibi sufficere ad componendum et ad finem ducendum realem medicinam.

**Catalan**

Fill, en totes medicines compondre tu no has ops sinó tant solament la forma de un vexell, lo qual és de .iii. peches¹, ço és assaber de un cubertor e de un alembich e de una carabaça². Mas ell pren differencia de nom segons la differença de sa operació. Car quant ell hi és per entenció de distillar, és dit³ 'distillatori' ab son alembich; e quant és per intenció de dissolre, és dit 'dissolutori'; e de podrir, és dit 'putrefactori'; e de calcinar, és dit 'calcinatori' e 'mortificatori'; e de congelar, és dit 'congelatori' e 'reductori' e 'sublimatori' e 'animatori' e 'vivificatori', 'creatori' e 'inhumatori', 'putrefactori', 'attenuatori', 'condensatori' e 'ymen' e 'fin de l'œuvre'; e totes vegades no és in forma sinó una tant solament. Ma[s] cascuna medicina requir son propre vexell format axí com és dit de vidre ab son cubertor e son alembich. Ffill, quant nós diem en aquest capitol 'medicina', açò ho entenem niment de lo simple per aquell o del compost per aquell. C'est assavoir du simple axí com tant solament és la terra primera o l'aygua tant solament per ella sens lo ajustament dels altres elements; e de cascú de aquells compost, axí com la pedra qui és creada de dos simples elements, ço és assaber de terra e de aygua, o lo elixir qui és fet de compost e de simples de compost, axí com de sofre e de ferments e de simples, axí com de aygua e de ayre. E per ço, ffill, quant aygua's preparata, ella ha mester son proprii vexell, fet axí com damunt és dit, axí com medicina simpla, e l'ayre semblantment, e axí des altres elements e medicines simples. Per qu'e] sia manifest

### ¶ 2

**Latin**

*(missing)*

**Catalan**

que com dues coses se pusquen tot en un / temps, no vulles successió o prolungació de temps per falta de vexell; car algunes vegades dues coses ensemps pots fer e algunes vegades .iii., e algunes vegades .iiii., la qual cosa tu no poràs fer si eres posat en defalliment dels vexells que són tos⁵ de una forma, e aquella forma te po[t] abastar per compondre e [a] fi menar la real medicina.

#### Apparatus (Latin side)
- 1. Lacuna per 'saut du même au même' (cfr. testo catalano).

#### Apparatus (Catalan side)
- 1. Scil. peces.
- 2. Ms. -ca.
- 3. Segue <'putrefactori, e de calcinar, és dit calcinatori> (cassato: errore di anticipo).
- 4. Ms. di.
- 5. Scil. tots.

---

## f83r -> Part II, Ch. 9
**Tier:** supported  
**Recipe:** Drip-counted mercurial solvent  
**Title (Latin):** *[senza rubrica]*  
**Title (Catalan):** *De la liquefacció de G                                 f. 48rb*  
**Folio refs in MS:** f. 48rb  
**Paragraph alignment:** ✓  
**Source pages:** Latin `['242_L']`, Catalan `['242_R']`

### ¶ 1

**Latin**

Fili, tu accipies unam unciam de G et […] infra unam amphoram cum longo collo, in qua posueris tres uncias de E. Et tam cito claude amphoram cum suo coopertorio et cum cera communi et pone in balneo calido per duos dies naturales. Et post duos dies in finam aquam invenies dissolutum.

**Catalan**

Fill, tu pendràs una once de G e dedins una ampolla ab lonch coll lo meteràs, en lo qual haies mes .iiii. onces de E. E tantost tapa la dita ampolla ab son cubertor e ab cera comuna e met-lo dedins lo bany calt per .ii. jorns naturalls. E aprés les .ii. dies en fin[a ai]gua¹ trobaràs-lo dissolt.

---

## Verification Status Per Folio (2026-04-25)

Cross-phase verification status. Phase 628 = 8D residual feature matching tier (the original Tier label above). Phase 641 atom-decode = Catalan operational scoring per [catalan_atom_decode_findings.md](../../PHASE_641_SISMEL_RERUN/results/catalan_atom_decode_findings.md). Phase 643 Test B = paragraph layout-order vs recipe-phase order Spearman rho per [C1959](../../../context/CLAIMS/C1959_paragraph_layout_recipe_phase_coherence.md).

### Original Phase 628 matches (16)

| Folio | 1566 Ch | SISMEL | P628 tier | P641 atom-decode | C1959 Test B |
|-------|---------|--------|----------:|------------------|--------------|
| f75r  | III.19  | III.19.0 | CONFIRMED | STRONG (rho +0.81 to +0.86 on counts) | ✓ rho=+0.866 (n=3, underpowered but high) |
| f76r  | II.18   | II.16.0  | CONFIRMED | **INCONCLUSIVE** | excluded (atom-decode failed) |
| f84r  | II.14   | II.12.0  | CONFIRMED | STRONG (12-headers anchor) | ✓★ rho=+0.827, p=0.0005 (n=18) |
| f79r  | III.12  | III.12.0 | strong-supported | INCONCLUSIVE | not tested |
| f82r  | III.22  | III.19.3 | strong-supported | MODERATE | ✓ rho=+0.894 (n=4, underpowered) |
| f76v  | III.15  | III.16.0 | strong-supported | MODERATE | not tested |
| f103r | III.16  | III.16.0 | strong-supported | MODERATE | not tested |
| f77v  | III.27  | III.20.0 | supported | MODERATE | not tested |
| f81v  | III.18  | III.18.0 | supported | INCONCLUSIVE | not tested |
| f82v  | III.28  | III.21.0 | supported | MODERATE | not tested |
| f112r | III.11  | III.11.0 | supported | MODERATE | not tested |
| f112v | III.1   | III.1.0  | supported | WEAK (DOES NOT SUPPORT) | not tested |
| f116r | III.4   | III.4.0  | supported | INCONCLUSIVE | not tested |
| f107r | III.44  | II.1.0 (sim 0) | supported | WEAK | not tested |
| f80r  | III.21  | II.1.0 (sim 0) | supported | MODERATE | not tested |
| f83r  | II.9    | II.7.0   | supported | MODERATE | not tested |

### New matches added Phases 644 / 646 (5)

These were not in Phase 628's original 16. Identified via reverse-prediction (anchor → recipe) or reverse-folio-search (recipe-template → folio), then verified at STRONG SUPPORT under atom-decode + Test B.

| Folio | Recipe | Origin | Atom-decode | Test B |
|-------|--------|--------|-------------|--------|
| f78r  | III.36.0 (mercury congelation) | Phase 641 blind test → P644 verified | STRONG (7M/1W/0X) | ✓★ rho=+0.926, p=0.0055 (n=8, refined) |
| f86v3 | II.10.0 (3-day coniuncció) | Phase 641 blind test → P644 verified | STRONG (8M/1W/0X) | ✓★ rho=+0.896, p=0.025 (n=7) |
| f108v | III.29.0 (mercury sublimation) | Phase 641 reverse-pred → P644 verified | STRONG (7M/1W/0X) | ✓★ rho=+0.924, p=0.002 (n=10) |
| f79v  | II.8.0 (first liquefaction) | Phase 641 reverse-pred → P644 verified | STRONG (6M/2W/0X) | ✓★ rho=+0.954, p=0.005 (n=7) |
| f77r  | III.28.0 (4-element temperament) | Phase 646 reverse-folio-search | STRONG (7M/1W/0X) | ✓★ rho=+0.861, p=0.0005 (n=13) |

### C1959 aggregate (8 matches passing Test B)

The 5 originals (f75r, f84r, f82r — plus f78r and f86v3 from blind test verified) + 3 new (f108v, f79v, f77r) form the C1959 evidence base:

- Mean Spearman rho across 8 matches: **+0.89**
- 8/8 positive direction
- 6/8 at strict permutation significance (p<0.05)
- 3/8 at n≥10 individually-significant
- Random-phase noise floor: rho +0.245 (effect size ~3.6× noise)

Phase 647 (C1960) further establishes that **paragraph-level heat metrics correlate with recipe fire-degree** on the heat-phase-distinct subset (f84r, f82r, f78r, f86v3, f77r): mean qokeedy_frac rho +0.71 vs heat-uniform control +0.07.

### Status of the 11 Phase 628 originals not in C1959 evidence

Not contradicted, but not at the same verification tier. They retain their Phase 628 8D-match status as candidates. Each could potentially be promoted via a focused atom-decode + Test B verification phase, similar to what was done for f78r (phase reassignment improved it from underpowered to strict-significant).

f76r is the most prominent demotion candidate — its atom-decode INCONCLUSIVE status puts the CONFIRMED tier label in tension with current evidence.

