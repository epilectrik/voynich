# C866: Gallows Morphological Patterns

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Different gallows types have distinct morphological patterns. k uniquely uses 'e' as POST element, f is often morphologically incomplete, and p/t differ in sh usage.

## Evidence

### POST Element Distribution

```
Gallows     ch       sh        o        e        -
p        38.9%    9.1%    38.1%    0.0%    7.2%
t        31.3%   21.6%    21.6%   13.4%    2.2%
k        24.6%   14.0%    19.3%   29.8%    1.8%
f        16.7%   16.7%    33.3%    0.0%   27.8%
```

### Morphological Completeness

```
Gallows  Has POST  Has SUFFIX
p           93%        95%
t           98%        91%
k           98%        89%
f           72%        61%
```

### Key Patterns

1. **k uses 'e' uniquely** (30% vs 0-13% for others)
2. **t uses more 'sh'** (22% vs 9% for p)
3. **f is often bare** (28% no POST, 39% no SUFFIX)

## Most Common Templates

```
p+ch+M+dy: 16 (pchedy pattern)
p+o+M+y:   18 (poly pattern)
t+ch+M+dy: 12 (tchedy pattern)
t+sh+M+dy:  9 (tshedy pattern)
k+e+M+dy:   6 (keedy pattern)
f+-+-+-:    4 (bare f)
```

## Provenance

- Script: `14_gallows_morphology_probe.py`
- Data: `gallows_morphology.json`

## Related

- C864 (gallows paragraph marker)
- C267 (token morphological structure)
- C540 (kernel primitives bound)
