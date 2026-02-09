# QO_CHSH_DIFFERENTIATION Phase

## Research Question

What do the QO-family (qo, ok, ot, o-prefixed) and CHSH-family (ch, sh-prefixed) EN tokens specifically monitor or operate on?

## Background

From existing constraints:
- **C576**: QO uses 25 MIDDLEs, CHSH uses 43 MIDDLEs, only 8 shared (Jaccard=0.133)
- **C577**: Identical line positions, interleaving varies by section (BIO 58.5%, PHARMA 27.5%)
- **C598**: FQ_CONN feeds CHSH (1.41x) but avoids QO (0.16x)
- **C574**: Grammatically equivalent but lexically partitioned

Current decoder glosses both as "monitor" - we need differentiation.

## Proposed Tests

### Test 1: Section QO:CHSH Ratio
**Question**: Does QO or CHSH dominate in specific sections?
- Compute QO:CHSH token ratio per section (BIO, HERBAL_B, PHARMA, RECIPE_B, STARS)
- If BIO is QO-heavy and PHARMA is CHSH-heavy (or vice versa), suggests material specialization

### Test 2: Material Marker Correlation
**Question**: Do QO and CHSH tokens co-occur with different material markers?
- Count ANIMAL markers (-ol, -or, -eol) by prefix family
- Count OIL markers (kch-, -kch) by prefix family
- Count WATER markers (-al, -ly) by prefix family
- Chi-square test for independence

### Test 3: Kernel Profile by Prefix Family
**Question**: Do QO and CHSH have different k/h/e distributions?
- Extract kernel characters from QO tokens vs CHSH tokens
- Compare k:h:e ratios
- If QO is k-heavy (energy) and CHSH is h-heavy (hazard), suggests functional split

### Test 4: MIDDLE Vocabulary Brunschwig Mapping
**Question**: Do QO-exclusive and CHSH-exclusive MIDDLEs map to different Brunschwig operations?
- Identify the 25 QO MIDDLEs and 43 CHSH MIDDLEs
- Map to F-BRU-011 tiers (PREP, THERMO, EXTENDED)
- Look for tier concentration differences

### Test 5: ESCAPE Line Behavior
**Question**: Do QO and CHSH behave differently during exception handling?
- Filter to ESCAPE-type lines only
- Compare QO:CHSH ratio in ESCAPE vs non-ESCAPE lines
- If one family concentrates in ESCAPE, suggests recovery/intervention role

### Test 6: Upstream Trigger Analysis
**Question**: What triggers QO vs CHSH activation?
- Analyze bigrams: what tokens precede QO tokens vs CHSH tokens?
- Look for systematic differences in upstream context
- May reveal what conditions activate each channel

### Test 7: Suffix Distribution
**Question**: Do QO and CHSH have different suffix profiles?
- Extract suffix distributions for each family
- Different suffixes may indicate different output types or continuation patterns

## Success Criteria

Phase succeeds if we can:
1. Identify at least one statistically significant discriminator (p < 0.01)
2. Propose differentiated glosses grounded in evidence
3. Map findings to interpretable Brunschwig/process domain concepts

## Null Hypothesis

QO and CHSH are functionally identical channels that happen to use different vocabularies for historical/scribal reasons, with no semantic differentiation.
