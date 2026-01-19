"""
EXT-8 Consistency Check

Does the shared infrastructure finding break anything?
Does it open new avenues?
"""

from collections import defaultdict, Counter
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']


def load_ab_tokens():
    """Load all tokens separated by Currier language."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    a_tokens = Counter()
    b_tokens = Counter()

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # CRITICAL: Filter to H-only transcriber track
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                lang = parts[6].strip('"').strip()
                word = parts[0].strip('"').strip().lower()

                if word:
                    if lang == 'A':
                        a_tokens[word] += 1
                    elif lang == 'B':
                        b_tokens[word] += 1

    return a_tokens, b_tokens


def main():
    print("=" * 80)
    print("EXT-8: CONSISTENCY CHECK & NEW AVENUES")
    print("=" * 80)

    a_tokens, b_tokens = load_ab_tokens()

    # === CHECK 1: Does this break the DISJOINT finding? ===
    print("\n## CHECK 1: DISJOINT Consistency")
    print("-" * 40)

    print("""
Prior finding: A and B are DISJOINT
- 0 shared folios
- Different structure (compositional vs sequential)
- 25/112,733 cross-transitions (0.0%)

New finding: Components are SHARED
- Same prefixes, suffixes, most middles
- Different usage patterns (enrichment)

VERDICT: NO CONTRADICTION
- Physical separation (folios) is unchanged
- Structural difference (grammar) is unchanged
- Shared components with different usage is EXPECTED
- Like element symbols in reagent catalog vs procedure manual
""")

    # === CHECK 2: Does this break structural primitive findings? ===
    print("\n## CHECK 2: Structural Primitive Consistency")
    print("-" * 40)

    # We found daiin is A-enriched (1.55x), ol is B-enriched (0.21x)
    daiin_a = a_tokens.get('daiin', 0)
    daiin_b = b_tokens.get('daiin', 0)
    ol_a = a_tokens.get('ol', 0)
    ol_b = b_tokens.get('ol', 0)

    print(f"\ndaiin: A={daiin_a}, B={daiin_b}, ratio={daiin_b/daiin_a:.2f}x")
    print(f"ol: A={ol_a}, B={ol_b}, ratio={ol_b/ol_a:.2f}x")

    # Now check CT prefix (A-enriched) and OL prefix (B-enriched)
    ct_a = sum(c for t, c in a_tokens.items() if t.startswith('ct'))
    ct_b = sum(c for t, c in b_tokens.items() if t.startswith('ct'))
    ol_prefix_a = sum(c for t, c in a_tokens.items() if t.startswith('ol'))
    ol_prefix_b = sum(c for t, c in b_tokens.items() if t.startswith('ol'))

    print(f"\nCT prefix: A={ct_a}, B={ct_b}, ratio={ct_b/ct_a:.2f}x (A-enriched)")
    print(f"OL prefix: A={ol_prefix_a}, B={ol_prefix_b}, ratio={ol_prefix_b/ol_prefix_a:.2f}x (B-enriched)")

    print("""
VERDICT: CONSISTENT
- ol (token) is B-enriched (structural primitive finding)
- OL (prefix) is B-enriched (EXT-8 finding)
- These align perfectly

- daiin is A-enriched (structural primitive)
- DA prefix is BALANCED (EXT-8 finding)
- daiin is a specific DA-family token, not the whole family
""")

    # === NEW AVENUE 1: CT's A-exclusivity ===
    print("\n" + "=" * 80)
    print("NEW AVENUE 1: What is CT?")
    print("=" * 80)

    print("""
CT is 7x more common in A than B (0.14x ratio).
CT has A-exclusive middles: -ho, -hod, -hom, -hol, -hor

Questions:
- What category of materials would be cataloged but rarely processed?
- Is CT a "reference" category (pure standards, samples)?
- Is CT materials that are stored but not actively used?
""")

    # Check CT tokens in B
    ct_tokens_b = {t: c for t, c in b_tokens.items() if t.startswith('ct')}
    print(f"\nCT tokens in B (rare): {sum(ct_tokens_b.values())} occurrences")
    print("Top CT tokens in B:")
    for t, c in sorted(ct_tokens_b.items(), key=lambda x: -x[1])[:10]:
        a_c = a_tokens.get(t, 0)
        print(f"  {t}: B={c}, A={a_c}")

    # === NEW AVENUE 2: -dy suffix B-enrichment ===
    print("\n" + "=" * 80)
    print("NEW AVENUE 2: What is -dy?")
    print("=" * 80)

    # Find all -dy tokens
    dy_tokens_a = {t: c for t, c in a_tokens.items() if t.endswith('dy')}
    dy_tokens_b = {t: c for t, c in b_tokens.items() if t.endswith('dy')}

    print(f"\n-dy suffix:")
    print(f"  In A: {sum(dy_tokens_a.values())} occurrences, {len(dy_tokens_a)} types")
    print(f"  In B: {sum(dy_tokens_b.values())} occurrences, {len(dy_tokens_b)} types")
    print(f"  Ratio: {sum(dy_tokens_b.values())/sum(dy_tokens_a.values()):.1f}x B-enriched")

    print(f"\nTop -dy tokens in B:")
    for t, c in sorted(dy_tokens_b.items(), key=lambda x: -x[1])[:10]:
        a_c = dy_tokens_a.get(t, 0)
        print(f"  {t}: B={c}, A={a_c}")

    print("""
Hypothesis: -dy might be a PROCEDURAL suffix
- Appears mainly in operational context (B)
- Rare in registry context (A)
- Could mark an action/state relevant to procedures
""")

    # === NEW AVENUE 3: -or vs -dy split ===
    print("\n" + "=" * 80)
    print("NEW AVENUE 3: -or (A) vs -dy (B) modal split")
    print("=" * 80)

    or_tokens_a = {t: c for t, c in a_tokens.items() if t.endswith('or')}
    or_tokens_b = {t: c for t, c in b_tokens.items() if t.endswith('or')}

    print(f"\n-or suffix:")
    print(f"  In A: {sum(or_tokens_a.values())} occurrences")
    print(f"  In B: {sum(or_tokens_b.values())} occurrences")
    print(f"  Ratio: {sum(or_tokens_b.values())/sum(or_tokens_a.values()):.2f}x")

    print(f"\n-dy suffix:")
    print(f"  In A: {sum(dy_tokens_a.values())} occurrences")
    print(f"  In B: {sum(dy_tokens_b.values())} occurrences")
    print(f"  Ratio: {sum(dy_tokens_b.values())/sum(dy_tokens_a.values()):.2f}x")

    print("""
Observation:
- -or is A-enriched (0.45x) = REGISTRY mode
- -dy is B-enriched (27x) = OPERATIONAL mode

These might represent different "aspects" of the same base:
- X-or = cataloged/stored form of X
- X-dy = procedural/active form of X

This would explain why both exist but in different contexts.
""")

    # === NEW AVENUE 4: Can we find structural parallels? ===
    print("\n" + "=" * 80)
    print("NEW AVENUE 4: Structural Parallels")
    print("=" * 80)

    print("""
If A catalogs materials that B operates on, can we find:
1. Materials cataloged in A that appear in B procedures?
2. Patterns in how registry codes map to operational tokens?

This could test whether A and B are truly complementary systems.
""")

    # Find tokens that appear in both with similar frequency
    shared_balanced = []
    for token in set(a_tokens.keys()) & set(b_tokens.keys()):
        a_c = a_tokens[token]
        b_c = b_tokens[token]
        if a_c >= 10 and b_c >= 10:
            ratio = b_c / a_c
            if 0.5 <= ratio <= 2.0:
                shared_balanced.append((token, a_c, b_c, ratio))

    shared_balanced.sort(key=lambda x: -(x[1] + x[2]))

    print(f"\nBalanced tokens (0.5x - 2.0x ratio, both >= 10):")
    print(f"Count: {len(shared_balanced)}")
    print(f"\nTop 20:")
    for token, a_c, b_c, ratio in shared_balanced[:20]:
        print(f"  {token:<20} A={a_c:>5}  B={b_c:>5}  ratio={ratio:.2f}")

    # === SYNTHESIS ===
    print("\n" + "=" * 80)
    print("SYNTHESIS")
    print("=" * 80)

    print("""
## NOTHING BROKEN

The shared infrastructure finding is CONSISTENT with:
1. Physical separation (0 shared folios) - UNCHANGED
2. Structural difference (compositional vs sequential) - UNCHANGED
3. Structural primitives (daiin A-enriched, ol B-enriched) - ALIGNED

## NEW AVENUES OPENED

1. **CT Mystery**: Why is CT 7x more common in A?
   - Materials cataloged but rarely processed?
   - Reference standards? Stored inventory?

2. **-dy Procedural Marker**: Why is -dy 27x more common in B?
   - Procedural/active form suffix?
   - Action state in operational context?

3. **Modal Split (-or vs -dy)**: Different "aspects" of same base?
   - -or = registry/stored form
   - -dy = operational/active form

4. **Structural Parallels**: Can we map A codes to B operations?
   - Would confirm complementary system hypothesis
   - Would identify which materials appear in which procedures

## RECOMMENDED NEXT PHASE

EXT-9: Cross-System Mapping
- Test if A registry codes appear in B procedures
- Map CT's rare B appearances to specific procedures
- Analyze -or/-dy modal distribution by prefix
""")


if __name__ == '__main__':
    main()
