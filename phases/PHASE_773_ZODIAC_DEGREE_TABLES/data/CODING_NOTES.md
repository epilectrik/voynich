# Zodiac figure iconography: coding notes

Output: `nymph_attributes.json`, one record for each of the 298 `slot_id`s in `nymph_slots.json`. The `page`, `sign`, `ring` and `clock` fields are copied from the slot list; `clothed`, `container`, `star`, `headwear`, `other` and `confidence` were coded by eye from the Beinecke scans. Every crop used is in `crops/` (see the index at the end).

Only the scans, the slot list and my own crops were consulted.

## 1. Panel identification

Each panel was identified by its central emblem. None of the identifications is in doubt.

| Page | Scan | Emblem seen | Sign |
|---|---|---|---|
| f70v2 | `images/canvas_126_70v-part.jpg` | two fish | Pisces |
| f70v1 | `images/canvas_127_70v-part.jpg` | dark (brown-grey) ram | Aries |
| f71r | `images/canvas_128_71r.jpg` | light ram | Aries |
| f71v | `foldouts/canvas_129_71v-and-72r.jpg`, panel 1 (left) | pale bull with green collar | Taurus |
| f72r1 | same foldout, panel 2 | solid red-brown bull | Taurus |
| f72r2 | same foldout, panel 3 | couple (man in green tunic and hat, woman in blue gown) | Gemini |
| f72r3 | same foldout, panel 4 (right) | two crayfish (one green, one red) | Cancer |
| f72v3 | `foldouts/canvas_130_72v-part.jpg`, left panel | lion | Leo |
| f72v2 | same foldout, right panel | woman in blue gown holding a sprig | Virgo |
| f72v1 | `images/canvas_131_72v-part.jpg` | balance on a stand | Libra |
| f73r | `images/canvas_132_73r.jpg` | green quadruped with curled tail | Scorpius |
| f73v | `images/canvas_133_73v.jpg` | figure in blue tunic with crossbow | Sagittarius |

## 2. How the slots were matched

1. For each panel I estimated the centre of the ring system in full-resolution scan pixels and checked it with a clock overlay: radial lines every 15 minutes plus circles at the text-band radii (`*_ov_q*` crops). Two first estimates were wrong and were redone: Gemini (final centre 5090,1415) and Virgo (final 4560,1840).
2. Figures were counted and located in upright sector crops (`*_r1_*`, `*_r2_*`) and, for crowded rings, in polar "unwraps". An unwrap is a strip with clock time along x and radius along y, so every figure in the ring stands upright side by side (`*_unwrap_*`, `*_wide_*`, `*_r2u_*`, `*_r1u_*`). Each figure's clock position is its head position, read from the tick marks on the strips.
3. Figures were then paired with slots in ring order: the k-th slot of a ring, clockwise from 12:00, goes to the k-th figure. Where the ring start is ambiguous, I kept the cyclic alignment with the smallest total clock deviation. Each record's `other` field gives the measured clock position of the figure used (for example "figure ~7:05"). When that position is far from the slot clock, `other` also says "matched by order".
4. Attributes were then coded from close upright crops of each figure (`*_s*`, `*_spots*`, `*_z*`, `*_h*`, `*_t*`).

Geometry:
- **Cancer (f72r3).** The left half of the panel is horizontally foreshortened in the foldout scan. Unwraps and spot crops for the left half used an x-scale of 0.9.
- **Leo (f72v3).** The ring-1 area from about 7:30 to 10:30 lies across a vertical page fold, which compresses the figures there.

## 3. Mismatches between slot counts and visible figures

Figure counts per ring agree with the slot list everywhere except Gemini ring 1.

| Page / ring | Slots | Figures seen | Note |
|---|---|---|---|
| f72r2 Gemini ring 1 | 15 | **16** | Counted in the unwrap strips `gem_unwrap_r1_s1of6` … `s6of6`. The minimum-deviation order match leaves the figure at **~8:25** without a slot. It is a clothed figure in a belted tunic, with collar and sleeves; its head is cut by a vertical crease (headwear not readable), it touches a star at ~8:45 and holds a small object in the other hand. No record was made for it. Slots 103 (8:00 → figure ~7:50) and 104 (9:00 → figure ~8:55) carry a note. Dropping any other figure gives a worse clock fit over the 6:30–9:30 section (40 min total deviation for this choice, against 55–70 min for the alternatives). |
| All other rings | = | = | Counts match. The ring-0 arcs (Gemini 5, Scorpius 4, Sagittarius 4) also match. |

Alignment choices worth checking:
- **f72v1 Libra ring 1.** The slot list starts this ring at 1:00, and there is no slot between 11:30 and 1:00, but there is a figure at ~12:05. The best cyclic fit, 318 min total deviation against 698 min for the naive fit, gives slot 1:00 to the crowned figure at ~12:35, each following slot to the next figure, and slot 11:30 (id 227) to the figure at ~12:05. If this is wrong, every Libra ring-1 record is off by one figure. All Libra ring-1 rows are therefore capped at medium confidence and flagged in `other`.
- **f72r3 Cancer ring 1.** Two slots are listed at 07:00 (ids 125 and 126). By order they go to the figures at ~7:05 (no star) and ~8:00.
- **Other large clock offsets taken by order** (30–55 min): Gemini ring 2, slot 114 (8:00) → figure ~7:05; Virgo ring 1, slots 5:30–8:30 → figures 20–30 min earlier; Scorpius ring 2, slots 10:30 and 11:30 → figures ~9:57 and ~10:57; Sagittarius ring 0, slot 12:30 → figure ~12:00. The order of figures in these rings is unambiguous, so these are position offsets only.
- **Figures too damaged to read for match or content:** Gemini ring 0, figure ~10:47 (under a dark stain); Cancer ring 1, figure ~1:40 (under a fold stain); Leo ring 1, figure ~10:28 (in the page fold); Leo ring 2, figures ~8:20 and ~9:15 (very faint); Virgo ring 1, figures ~3:02 and ~3:47 (fold shadow). Each is still the only figure at its position in the ring, so the match is probable, but its attributes are mostly `unclear`.

## 4. Coding rules used

- **clothed.** `naked`: no garment on torso or arms; a head covering or a veil hanging down the back does not count. `partly`: some garment on torso or arms (mantle over the shoulders, sleeve, cape, cloth over the hip or thigh) with breasts or belly still bare. `clothed`: torso covered. A coloured wash over the torso is coded as a garment only when it has garment edges (neckline, sleeve end, hem); otherwise it is noted in `other`.
- **container.** `in_or_on_barrel_or_tub`: the figure emerges from, stands in, sits or lies on, or stands on a tub or barrel. This includes the Gemini figures standing on barrels lying on their sides. `beside_barrel_or_tub`: the figure stands or sits next to one. `none`: no container associated with the figure.
- **star.**
  - `held`: the hand or fingers touch the star or its rays, or a line or stalk runs from the star to the figure's hand or arm.
  - `near`: a star is beside the figure without contact. This includes stars whose stalk ends on the **tub rim** rather than on the hand, and hands raised close under a star with a visible gap.
  - `none`: no star next to the figure.
  - `unclear`: the relevant area is damaged, or a pigment smudge covers where a star would be.
- **headwear.** `crown`: a spiked or arched crown. `hat_or_cap`: a distinct brimmed hat, cap, padded roll or turban shape. `veil_or_cloth`: a hood or veil with a contour enclosing the head and falling to the shoulders or back. `unclear`: see the systematic difficulties below.
- **confidence.** This is for the whole row, including the figure-to-slot match. It is roughly the lowest confidence of the attributes coded.

## 5. Attributes that were hard to judge

1. **Star held vs near.** This was the main difficulty.
   - *Pisces ring 1.* Many stars sit on long curling stalks that run down to the rim of the figure's tub, next to the arm. Where the line visibly ends on the rim (ids 0, 2, 3, 5, 6, 10, 13, 14, 17) the code is `near`. Where it ends on the hand, arm or shoulder the code is `held`; the shoulder or elbow cases are low confidence.
   - *Rings of standing figures on the unpainted pages (Cancer, Leo, Virgo, Libra, Scorpius, Sagittarius).* A hand raised just under the lower rays is often a matter of a pixel or two. Contact that is only probable was coded `held` at low or medium confidence.
2. **Dark scalloped outline over the crown.** On Virgo, Libra, Scorpius and Sagittarius (and one light-Aries figure, id 46), several figures have a heavy dark-ink scalloped or crimped line over the top of the head. It could be curly hair, a wreath, a frilled veil edge or a cap. It is coded `headwear: unclear` throughout, with the feature described in `other`. The one exception is Sagittarius id 276, where the scalloped band continues down the side of the face to the shoulder like a hood edge; it is coded `veil_or_cloth` at low confidence.
3. **Coloured masses on the head.** On Pisces, blue-painted masses over the crown can be read as a cap or as blue-painted hair. Where there is a distinct shape with hair visible beneath it (ids 1, 4, 5) I coded `hat_or_cap`. Crescents, bands or side-falls of blue (ids 3, 6, 7) and the ochre crescent (id 18) are `unclear`. The same judgement applies to the ochre or red bands on dark Aries (ids 32, 33), the green blob on Sagittarius id 294 (probably a smudge) and several rolled or round outlines elsewhere.
4. **Pisces ring-2 containers.** These figures sit at the ends of horizontal tubes lying on the inner band. Whether the lower body is inside the tube's open end or in front of it is often not decidable. `in_or_on` was used only where the tube rim visibly wraps round the body (id 26) or the figure lies over the tube (id 27).
5. **clothed on the painted pages** (f71r, f71v). Coloured washes over the torso with breasts outlined underneath (ids 46, 70) were judged as garments. Partial garments, such as a sleeve or belt on an otherwise bare figure, were coded `partly`.

## 6. Systematic difficulties

- **Foldout damage.** Folds, creases and offset stains cross the foldout panels. The worst areas are Leo (vertical fold through the left of the panel, a faint lower-left quadrant, stains around 9:30–10:30), Virgo (fold shadow from 1:45 to 3:30 and from 8:00 to 9:30), Cancer (a diagonal stain at about 1:30–2:00) and Gemini (a dark stain at ring-0 ~10:47). About two thirds of the low-confidence rows are on Leo, Virgo, Scorpius and Sagittarius.
- **Faint inner rings.** On Scorpius and Sagittarius the ring-2 figures recline and overlap in faint ink. On Sagittarius, two apparent heads turned out to be hands (a hand at ~7:55 belongs to the ~8:23 figure; a shape under the ~10:05 star is the ~9:37 figure's hand gripping it), and a brown blob at ~5:40 is a stain. These were resolved with enlarged sector crops (`sag_r2z_*`, `sag_r2_1005`).
- **Holes in the vellum.** There are holes at Libra ~2:25 (between rings 1 and 2; a figure on the leaf beneath shows through) and dark Taurus ~9:00 in ring 2.
- **Unmodelled ink.** A small lattice box or barrel sits in the outer text band of f71r at ~9:40 and is attached to no figure. Large C-shaped ink marks and a black blot lie near Sagittarius ring-0 ~11:11. None of these was coded as a figure.
- **Clock-position scatter.** The slot clocks and my measured head positions differ by up to about 55 min in places (see section 3). Matching was always done by ring order, not by nearest clock value.

## 7. Crop index (`crops/`, 439 JPEGs, about 150 MB)

Crops are named by prefix and view type; `ariD` is the dark ram (f70v1) and `ariL` the light ram (f71r).

| Prefix | Page |
|---|---|
| `pis`, `pisZ`, `pisZZ` | Pisces f70v2 |
| `ariD` | Aries f70v1 (dark ram) |
| `ariL` | Aries f71r (light ram) |
| `tauL` | Taurus f71v (light bull) |
| `tauD` | Taurus f72r1 (dark bull) |
| `gem`, `gem2`, `gemZ` | Gemini f72r2 |
| `can` | Cancer f72r3 |
| `leo` | Leo f72v3 |
| `vir` | Virgo f72v2 |
| `lib` | Libra f72v1 |
| `sco` | Scorpius f73r |
| `sag` | Sagittarius f73v |
| `overview_*`, `fold129_*`, `check_*` | whole scans and single foldout panels |

| Suffix pattern | View |
|---|---|
| `*_ov_q*` | clock overlays by quadrant |
| `*_r0_*`, `*_r1_*`, `*_r2_*` with clock range | upright sector crops |
| `*unwrap*`, `*_wide_*`, `*_r2u_*`, `*_r1u_*` | polar unwrap strips |
| other suffixes (`*_s*`, `*_spots*`, `*_z*`, `*_h*`, `*_t*`, `*_lines*`, `*_chk*`) | upright close-ups of individual figures, labelled `clock:radius` in scan pixels |

In the unwrap strips the clock labels are the page clock positions; in the sector crops the two corner labels give the sector's start and end clock times.
