# C903: Prefix Rarity Gradient

**Tier:** 2
**Scope:** A
**Phase:** TOKEN_ANNOTATION_BATCH_11

## Constraint

The Currier A prefix inventory exhibits a rarity gradient. Common prefixes (ch, sh, qo, ok) appear throughout the corpus, while rare prefixes (qk, qy) concentrate in late Currier A and mark exceptional entries.

## Evidence

From systematic annotation of 114 Currier A folios:

### Prefix Rarity Distribution

| Rarity Level | Prefixes | Folio Count | Notes |
|--------------|----------|-------------|-------|
| Common | ch, sh, qo, ok, ot, da, ol | 100+ | Distributed throughout |
| Moderate | ct | 37 | Reserved per C889 |
| Rare | qk | 9 | Late Currier A concentration |
| Extremely Rare | qy | 3 | Highly specialized |

### QK-Prefix Distribution

The 9 folios with qk-prefix tokens show late Currier A concentration:
- Multiple occurrences in f99-f102 range
- Often co-occurs with other rare markers

### QY-Prefix Distribution

Only 3 folios contain qy-prefix tokens, making it the rarest productive prefix in Currier A.

### Contrast with C889 (ct-reserved)

Per C889, ct-prefix combines almost exclusively with MIDDLEs h, hy, ho. The qk and qy prefixes show no such MIDDLE restriction but are rarity-constrained at the prefix level itself.

## Interpretation

The prefix rarity gradient suggests:

1. **Common prefixes** handle routine discrimination tasks
2. **Rare prefixes** mark exceptional or specialized entries
3. **Rarity correlates with specialization** - the rarer the prefix, the more unusual the entry

This parallels the gallows domain rarity gradient (k/t common, p/f rare per C530).

## Implication for Triangulation

When triangulating material classes:
- Entries with qk/qy prefixes likely represent rare or specialized materials
- Prefix rarity may serve as a filter for "unusual cases" category

## Provenance

- **Phase:** TOKEN_ANNOTATION_BATCH_11
- **Method:** Systematic token-by-token annotation
- **Data:** data/folio_notes.json, data/token_dictionary.json
- **Date:** 2026-02-01

## Related

- C889: ct-reserved vocabulary
- C530: Gallows domain coherence
- C902: Late Currier A register characteristics
