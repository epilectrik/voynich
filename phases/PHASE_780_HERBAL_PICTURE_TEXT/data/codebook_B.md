# Coding guide for plant pictures (coder set B)

Each image shows a drawn or printed plant. Flat grey regions are masks: disregard them, and disregard any lettering.
Record only what the picture actually shows. Do not infer missing parts from what kind of plant it may be. Where a
feature cannot be decided (damage, ambiguity, part hidden), answer `unclear`.

Answer every field below for every image, using exactly the codes given.

**Underground part**
- `root_form`: how the root is drawn — `none_visible` (no root shown) / `single_taproot` (one principal root, small
  side roots allowed) / `few_branched` (two to four principal roots) / `many_branched_or_fibrous` (five or more roots,
  or a mass of fine rootlets) / `swollen` (bulb, tuber or a fat rounded base) / `unclear`.
- `root_size`: the root's share of the plant's total height — `none` (no root shown) / `small` (less than one quarter) /
  `medium` / `large` (more than one half) / `unclear`.

**Stems**
- `stem_count`: how many principal stems leave the base — `1` / `2-3` / `4+` / `unclear`.

**Foliage**
- `leaf_type`: the most common leaf form — `simple_entire` (one undivided blade, plain margin) /
  `simple_toothed_or_lobed` (one undivided blade with teeth, waves or lobes) / `compound` (a leaf made of several
  leaflets on a common stalk) / `grass_or_needle` (long thin blades or needles) / `none` (no leaves) / `mixed` (two or
  more forms in roughly equal amounts) / `unclear`.
- `leaf_size`: usual leaf size compared with the plant — `small` / `medium` / `large` / `unclear`.
- `leaf_count`: how many leaves are shown — `0` / `1-5` / `6-15` / `16+` / `unclear`.

**Blossoms and fruits**
- `flowers`: `none` / `flowers` / `fruits_or_seed_heads` (berries, pods, seed heads, cones) / `both` / `unclear`.
- `flower_count`: blossoms plus fruits — `0` / `1` / `2-5` / `6+` / `unclear`.
- `flower_colour` (only for painted pictures; for black-and-white prints answer `na`): dominant colour of blossoms or
  fruits — `none` (there are none) / `blue` / `red_or_pink` / `yellow` / `white_or_unpainted` / `mixed` / `unclear`.

**Growth form**
- `habit`: `upright_herb` / `sprawling_or_climbing` / `shrub_or_tree_like` / `unclear`.

**Manner of drawing**
- `fill` (painted pictures only, otherwise `na`): `outline_only` / `partly_painted` / `fully_painted` / `unclear`.
- `line_weight`: the contour lines — `thin` / `heavy` / `unclear`.
- `shading` (prints only, otherwise `na`): `none` / `hatching` (shading by parallel or crossing lines) / `unclear`.
- `pigments` (painted pictures only, otherwise `[]`): list every paint colour used on the plant, chosen from `green`,
  `blue`, `red_brown`, `yellow`, `other`.

**Checks on the image itself**
- `text_visible`: `yes` if lettering or writing can be seen anywhere outside the grey masks, otherwise `no`.
- `main_plant`: `yes` if a plant is the main subject of the image, otherwise `no`.
- `n_plants`: `1` or `2+` (separate plants of similar size).
