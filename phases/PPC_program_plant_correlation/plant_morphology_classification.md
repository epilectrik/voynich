# Plant Morphology Classification (BLIND)

> **PURPOSE**: Classify Voynich botanical illustrations by observable morphology ONLY.
> **METHOD**: Visual examination without reference to program metrics, product hypotheses, or uses.

---

## Classification Tags

| Tag | Definition |
|-----|------------|
| **ROOT_HEAVY** | Roots prominently drawn, complex, or emphasized |
| **FLOWER_DOMINANT** | Large or emphasized inflorescences/flowers |
| **LEAFY_HERB** | Dense leaf mass relative to stem |
| **WOODY_SHRUB** | Thick stems, branch-like structure |
| **COMPOSITE** | Multiple distinct plants shown |
| **AMBIGUOUS** | Unusual or unclear morphology |

---

## Folio-by-Folio Classification

| Folio | Primary Tag | Secondary Tags | Confidence | Key Visual Features |
|-------|-------------|----------------|------------|---------------------|
| **f26r** | ROOT_HEAVY | LEAFY_HERB | HIGH | Branching stem, rounded scalloped leaves, small blue flower clusters, prominent taproot |
| **f26v** | ROOT_HEAVY | LEAFY_HERB | HIGH | Dense small rounded leaves on branches, blue fruits/flowers, elaborate spreading root system |
| **f31r** | ROOT_HEAVY | FLOWER_DOMINANT, LEAFY_HERB | HIGH | Upright stem, large serrated leaves, cream/white flower clusters, thick spreading roots |
| **f31v** | COMPOSITE | ROOT_HEAVY, LEAFY_HERB | MEDIUM | TWO PLANTS: thin-stemmed with blue flowers + dense pointed leaves with root mass |
| **f33r** | FLOWER_DOMINANT | ROOT_HEAVY, LEAFY_HERB | HIGH | Large pointed leaves in rosette, two globular spiky flower heads, bulbous calyxes |
| **f33v** | LEAFY_HERB | AMBIGUOUS | MEDIUM | Multiple stems, caterpillar-like structures at top, deeply divided star-shaped leaves |
| **f34r** | ROOT_HEAVY | LEAFY_HERB, FLOWER_DOMINANT | HIGH | Central stem, deeply lobed palmate leaves, large fruit/pod, spreading roots |
| **f34v** | WOODY_SHRUB | ROOT_HEAVY | HIGH | Tree-like branching, many oval leaves (green/brown), woody trunk, root system |
| **f39r** | ROOT_HEAVY | LEAFY_HERB | HIGH | Row of upright stems with pointed leaves, horizontal connected rhizome-like root system |
| **f39v** | FLOWER_DOMINANT | ROOT_HEAVY, LEAFY_HERB | HIGH | Central stem, elongated oval leaves, cluster of blue/white star flowers, spreading roots |
| **f40r** | FLOWER_DOMINANT | ROOT_HEAVY, LEAFY_HERB | HIGH | Single tall stem, large blue daisy-like flower, feathery/spiky palmate leaves |
| **f40v** | FLOWER_DOMINANT | ROOT_HEAVY | HIGH | Large compound ring-flower head (blue petals), feathery basal leaves, connected bulbous roots |
| **f41r** | LEAFY_HERB | ROOT_HEAVY | HIGH | Single stem with alternating fan-shaped/lobed leaves, no prominent flowers, taproot |
| **f41v** | ROOT_HEAVY | LEAFY_HERB, FLOWER_DOMINANT | HIGH | Dense feathery/divided leaves, large umbrella flower cluster (blue), prominent tuberous roots |
| **f43r** | ROOT_HEAVY | LEAFY_HERB, FLOWER_DOMINANT | HIGH | Multiple connected plants in row, small flower heads, dense scalloped leaves, EXTREME root emphasis |
| **f43v** | COMPOSITE | LEAFY_HERB, ROOT_HEAVY | MEDIUM | Multiple plant types: narrow leaves + curly leaves + feathery stems, spiral root element |
| **f46r** | LEAFY_HERB | ROOT_HEAVY | HIGH | Multiple stems with wavy/curled leaves, small flower buds, connected horizontal root mass |
| **f46v** | FLOWER_DOMINANT | LEAFY_HERB, ROOT_HEAVY | HIGH | Central stems with spiky/serrated thistle-like leaves, multiple blue/cream flower heads |
| **f48r** | LEAFY_HERB | ROOT_HEAVY, AMBIGUOUS | MEDIUM | Branching stem with bulbous leaf clusters (unusual shape), small flowers, prominent roots |
| **f48v** | LEAFY_HERB | FLOWER_DOMINANT, ROOT_HEAVY | HIGH | Bushy with many lobed/oak-like leaves, small blue/cream flowers, spreading root system |
| **f50r** | FLOWER_DOMINANT | LEAFY_HERB, ROOT_HEAVY | HIGH | Large dramatic flower head (eye-like, blue/white petals), lobed leaves with blue veining |
| **f50v** | FLOWER_DOMINANT | ROOT_HEAVY, LEAFY_HERB | HIGH | Single stem with rounded lobed leaves, dramatic blue feathery structure at top |
| **f55r** | LEAFY_HERB | FLOWER_DOMINANT, ROOT_HEAVY | HIGH | Bushy with lobed/palmate leaves, three dark red seed pods, small white flower clusters |
| **f55v** | ROOT_HEAVY | LEAFY_HERB, FLOWER_DOMINANT | HIGH | Tall stem with very large broad leaves, small blue cluster flower, elaborate root system |

---

## Morphology Distribution Summary

### Primary Tag Distribution

| Primary Tag | Count | Percentage |
|-------------|-------|------------|
| ROOT_HEAVY | 10 | 41.7% |
| FLOWER_DOMINANT | 7 | 29.2% |
| LEAFY_HERB | 5 | 20.8% |
| COMPOSITE | 2 | 8.3% |
| WOODY_SHRUB | 1 | 4.2% |
| AMBIGUOUS | 0 | 0% |

**Total: 24 folios (note: one folio can have one primary tag)**

### Secondary Tag Frequency (any position)

| Tag | Frequency | Percentage |
|-----|-----------|------------|
| ROOT_HEAVY | 22/24 | 91.7% |
| LEAFY_HERB | 20/24 | 83.3% |
| FLOWER_DOMINANT | 12/24 | 50.0% |
| AMBIGUOUS | 2/24 | 8.3% |
| WOODY_SHRUB | 1/24 | 4.2% |
| COMPOSITE | 2/24 | 8.3% |

### Confidence Distribution

| Confidence | Count | Percentage |
|------------|-------|------------|
| HIGH | 20 | 83.3% |
| MEDIUM | 4 | 16.7% |
| LOW | 0 | 0% |

---

## Key Observations (Morphology Only)

1. **ROOT_HEAVY dominance**: 91.7% of folios show prominent root systems (primary or secondary)
2. **LEAFY_HERB universal**: 83.3% show dense leaf structures
3. **FLOWER_DOMINANT common**: 50.0% emphasize flowers
4. **WOODY_SHRUB rare**: Only 1/24 (4.2%) shows tree-like structure
5. **No GRASSLIKE/GRAINLIKE**: 0% show grass or grain morphology
6. **Composite illustrations**: 8.3% show multiple distinct plant forms

---

## Morphology Type Summary

For correlation analysis, simplified to dominant morphology:

| Category | Folios | Count |
|----------|--------|-------|
| **ROOT_DOMINATED** | f26r, f26v, f31r, f34r, f39r, f41v, f43r, f55v | 8 |
| **FLOWER_DOMINATED** | f33r, f39v, f40r, f40v, f46v, f50r, f50v | 7 |
| **LEAF_DOMINATED** | f33v, f41r, f46r, f48r, f48v, f55r | 6 |
| **WOODY_STRUCTURE** | f34v | 1 |
| **COMPOSITE/AMBIGUOUS** | f31v, f43v | 2 |

---

*Classification performed BLIND without reference to program metrics.*
