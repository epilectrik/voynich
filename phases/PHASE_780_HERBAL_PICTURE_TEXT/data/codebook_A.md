# Plant-drawing codebook (coder set A)

You will see images of plant drawings. Parts of some images are filled with flat grey; ignore the grey areas and any
writing. Code ONLY what is visible in the drawing. Do not use any knowledge of what species the plant might be, and do
not add parts that are not drawn. If a feature cannot be judged (damaged, ambiguous, hidden), use `unclear`.

For each image, give exactly these fields (use the value spellings shown):

**Root**
- `root_form`: `none_visible` (no root drawn) / `single_taproot` (one main root, possibly with small side roots) /
  `few_branched` (2–4 main roots) / `many_branched_or_fibrous` (5 or more roots, or a tuft of fine roots) / `swollen`
  (a bulb, tuber or thick rounded rootstock) / `unclear`.
- `root_size`: size of the root relative to the whole plant's height: `none` (no root drawn) / `small` (under a
  quarter) / `medium` / `large` (over half) / `unclear`.

**Stem**
- `stem_count`: number of main stems rising from the base: `1` / `2-3` / `4+` / `unclear`.

**Leaves**
- `leaf_type`: the predominant leaf shape: `simple_entire` (undivided leaf with a smooth edge) /
  `simple_toothed_or_lobed` (undivided leaf with a toothed, wavy or lobed edge) / `compound` (several separate leaflets
  on one shared stalk) / `grass_or_needle` (long narrow blades or needles) / `none` (no leaves drawn) / `mixed` (two or
  more of these types in about equal measure) / `unclear`.
- `leaf_size`: typical leaf size relative to the plant: `small` / `medium` / `large` / `unclear`.
- `leaf_count`: number of leaves drawn: `0` / `1-5` / `6-15` / `16+` / `unclear`.

**Flowers and fruit**
- `flowers`: `none` / `flowers` / `fruits_or_seed_heads` (berries, pods, seed heads, cones) / `both` / `unclear`.
- `flower_count`: number of flowers and fruits together: `0` / `1` / `2-5` / `6+` / `unclear`.
- `flower_colour` (coloured drawings only; for uncoloured prints write `na`): the main colour of the flowers or fruits:
  `none` (no flowers or fruits) / `blue` / `red_or_pink` / `yellow` / `white_or_unpainted` / `mixed` / `unclear`.

**Overall habit**
- `habit`: `upright_herb` / `sprawling_or_climbing` / `shrub_or_tree_like` / `unclear`.

**How it is drawn**
- `fill` (coloured drawings only, else `na`): `outline_only` / `partly_painted` / `fully_painted` / `unclear`.
- `line_weight`: the outline strokes: `thin` / `heavy` / `unclear`.
- `shading` (printed woodcuts only, else `na`): `none` / `hatching` (parallel-line or cross-hatched shading) /
  `unclear`.
- `pigments` (coloured drawings only, else `[]`): a list of the colours of paint used anywhere on the plant, from
  `green`, `blue`, `red_brown`, `yellow`, `other`.

**Image checks**
- `text_visible`: `yes` if any letters or writing are visible in the image (outside the grey areas), else `no`.
- `main_plant`: `yes` if the image shows a plant as its main subject, else `no`.
- `n_plants`: `1` or `2+` (separate, comparably sized plants).
