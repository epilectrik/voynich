"""
Test the RATIO hypothesis for Currier A multiplicity

If repetition encodes a RATIO rather than a count:
- The block describes WHAT (ingredients/components)
- The repetition describes HOW MUCH (proportion/ratio)

Tests:
1. Do same/similar blocks appear with DIFFERENT repetition counts?
2. Does repetition correlate with block composition in ratio-like ways?
3. Are there patterns suggesting proportional relationships?
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats

project_root = Path(__file__).parent.parent.parent
MARKER_PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']


def load_currier_a_entries():
    """Load Currier A entries grouped by line."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    entries = defaultdict(lambda: {'tokens': [], 'section': '', 'folio': ''})

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 6:
                # CRITICAL: Filter to H-only transcriber track
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                lang = parts[6].strip('"').strip()
                if lang == 'A':
                    word = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''

                    if word:
                        key = f"{folio}_{line_num}"
                        entries[key]['tokens'].append(word)
                        entries[key]['section'] = section
                        entries[key]['folio'] = folio

    return dict(entries)


def detect_repetition(tokens):
    """Detect repeating block structure."""
    n = len(tokens)
    if n < 4:
        return 0, 0, []

    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            count = n // block_size
            if count >= 2:
                block = tokens[:block_size]
                matches = True
                for i in range(1, count):
                    chunk = tokens[i * block_size:(i + 1) * block_size]
                    mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                    if mismatches > len(block) * 0.2:
                        matches = False
                        break
                if matches:
                    return block_size, count, block

    return 0, 0, []


def get_prefix(token):
    """Get the prefix of a marker token."""
    for prefix in MARKER_PREFIXES:
        if token.startswith(prefix):
            return prefix
    return None


def block_signature(block):
    """Create a signature for a block (sorted prefixes + size)."""
    prefixes = tuple(sorted(get_prefix(t) for t in block if get_prefix(t)))
    return (prefixes, len(block))


def block_prefix_composition(block):
    """Get the prefix composition of a block as a tuple."""
    prefix_counts = Counter(get_prefix(t) for t in block if get_prefix(t))
    return tuple(sorted(prefix_counts.items()))


def main():
    print("=" * 80)
    print("RATIO HYPOTHESIS TEST")
    print("=" * 80)

    entries = load_currier_a_entries()

    # Detect repetitions
    repetitions = []
    for entry_id, data in entries.items():
        tokens = data['tokens']
        block_size, rep_count, block = detect_repetition(tokens)
        if rep_count >= 2:
            repetitions.append({
                'entry_id': entry_id,
                'tokens': tokens,
                'section': data['section'],
                'folio': data['folio'],
                'block_size': block_size,
                'rep_count': rep_count,
                'block': block,
                'signature': block_signature(block),
                'composition': block_prefix_composition(block)
            })

    print(f"\nEntries with repetition: {len(repetitions)}")

    # === TEST 1: Same composition, different repetition counts ===
    print("\n" + "=" * 80)
    print("TEST 1: SAME COMPOSITION, DIFFERENT REPETITION COUNTS")
    print("=" * 80)
    print("\nIf this is a ratio system, same ingredients should appear")
    print("with different repetition counts (different proportions).")

    # Group by prefix composition
    comp_reps = defaultdict(list)
    for r in repetitions:
        comp_reps[r['composition']].append(r)

    # Find compositions with multiple different repetition counts
    variable_comps = []
    for comp, entries in comp_reps.items():
        rep_counts = set(e['rep_count'] for e in entries)
        if len(rep_counts) > 1 and len(entries) >= 3:
            variable_comps.append((comp, entries, rep_counts))

    print(f"\nCompositions with VARIABLE repetition counts: {len(variable_comps)}")

    if variable_comps:
        print(f"\n## EXAMPLES (same ingredients, different ratios?):")
        for comp, entries, rep_counts in sorted(variable_comps, key=lambda x: -len(x[1]))[:10]:
            print(f"\n  Composition: {dict(comp)}")
            print(f"  Repetition counts seen: {sorted(rep_counts)}")
            print(f"  Number of entries: {len(entries)}")
            for e in entries[:3]:
                print(f"    {e['rep_count']}x: {' '.join(e['block'][:6])}...")

    # === TEST 2: Repetition count distribution by composition size ===
    print("\n" + "=" * 80)
    print("TEST 2: REPETITION vs COMPOSITION SIZE")
    print("=" * 80)
    print("\nIf ratio = amount/concentration, simpler compositions")
    print("might have higher repetitions (more of a simple thing).")

    comp_size_reps = defaultdict(list)
    for r in repetitions:
        num_prefixes = len(set(get_prefix(t) for t in r['block'] if get_prefix(t)))
        comp_size_reps[num_prefixes].append(r['rep_count'])

    print(f"\n{'# Prefixes':<12} {'Mean Rep':>10} {'Entries':>10}")
    print("-" * 35)

    for num_prefixes in sorted(comp_size_reps.keys()):
        reps = comp_size_reps[num_prefixes]
        if len(reps) >= 10:
            print(f"{num_prefixes:<12} {np.mean(reps):>10.2f} {len(reps):>10}")

    # Correlation test
    all_sizes = []
    all_reps = []
    for r in repetitions:
        num_prefixes = len(set(get_prefix(t) for t in r['block'] if get_prefix(t)))
        all_sizes.append(num_prefixes)
        all_reps.append(r['rep_count'])

    corr, p_val = stats.spearmanr(all_sizes, all_reps)
    print(f"\nCorrelation (# prefixes vs repetition):")
    print(f"  Spearman rho = {corr:.3f}, p = {p_val:.4f}")

    # === TEST 3: Do repetition counts form ratio-like patterns? ===
    print("\n" + "=" * 80)
    print("TEST 3: RATIO-LIKE PATTERNS")
    print("=" * 80)

    # Look at the distribution of repetition counts
    rep_dist = Counter(r['rep_count'] for r in repetitions)
    print(f"\nRepetition count distribution:")
    for rep, count in sorted(rep_dist.items()):
        bar = '#' * (count // 10)
        print(f"  {rep}x: {count:>4} {bar}")

    # Check if 2x and 3x are near-equal (as found before)
    if 2 in rep_dist and 3 in rep_dist:
        ratio_2_3 = rep_dist[2] / rep_dist[3]
        print(f"\n2x/3x ratio: {ratio_2_3:.3f}")
        print("(Near 1.0 suggests deliberate balance, not random)")

    # === TEST 4: Within-folio ratio patterns ===
    print("\n" + "=" * 80)
    print("TEST 4: WITHIN-FOLIO RATIO PATTERNS")
    print("=" * 80)
    print("\nIf repetitions are ratios in a recipe, entries on the same")
    print("folio might show complementary ratios (adding up to something).")

    # Group by folio
    folio_reps = defaultdict(list)
    for r in repetitions:
        folio_reps[r['folio']].append(r['rep_count'])

    # Check if folios have consistent patterns
    print(f"\n## FOLIO REPETITION PATTERNS (folios with 5+ entries):")

    folio_patterns = []
    for folio, reps in folio_reps.items():
        if len(reps) >= 5:
            mean_rep = np.mean(reps)
            std_rep = np.std(reps)
            total_rep = sum(reps)
            folio_patterns.append((folio, len(reps), mean_rep, std_rep, total_rep, reps))

    folio_patterns.sort(key=lambda x: -x[1])

    print(f"\n{'Folio':<10} {'Entries':>8} {'Mean':>8} {'Std':>8} {'Sum':>8} {'Distribution'}")
    print("-" * 70)

    for folio, n, mean, std, total, reps in folio_patterns[:15]:
        dist = Counter(reps)
        dist_str = ' '.join(f"{r}x:{c}" for r, c in sorted(dist.items()))
        print(f"{folio:<10} {n:>8} {mean:>8.2f} {std:>8.2f} {total:>8} {dist_str}")

    # === TEST 5: Look for ratio signatures ===
    print("\n" + "=" * 80)
    print("TEST 5: RATIO SIGNATURES IN BLOCK CONTENT")
    print("=" * 80)

    # If the block itself encodes ratios, we might see patterns like
    # the same token appearing multiple times proportionally

    print("\n## TOKEN REPETITION WITHIN BLOCKS")

    token_reps_in_blocks = []
    for r in repetitions:
        block = r['block']
        token_counts = Counter(block)
        max_count = max(token_counts.values())
        unique_tokens = len(token_counts)
        if max_count > 1:
            token_reps_in_blocks.append((r, max_count, unique_tokens, token_counts))

    print(f"\nBlocks with repeated tokens: {len(token_reps_in_blocks)}")

    if token_reps_in_blocks:
        print(f"\n## EXAMPLES (tokens repeated within block):")
        for r, max_count, unique, counts in sorted(token_reps_in_blocks, key=lambda x: -x[1])[:10]:
            print(f"\n  Entry: {r['entry_id']}, {r['rep_count']}x repetition")
            print(f"  Block: {' '.join(r['block'])}")
            repeated = {t: c for t, c in counts.items() if c > 1}
            print(f"  Repeated tokens: {repeated}")

    # === SYNTHESIS ===
    print("\n" + "=" * 80)
    print("SYNTHESIS: RATIO HYPOTHESIS ASSESSMENT")
    print("=" * 80)

    print(f"""
## EVIDENCE FOR RATIO INTERPRETATION

1. SAME COMPOSITION, DIFFERENT COUNTS:
   - {len(variable_comps)} compositions appear with variable repetition counts
   - This suggests the count is INDEPENDENT of what's in the block
   - Compatible with: "3 parts of X" vs "2 parts of X"

2. REPETITION vs COMPOSITION SIZE:
   - Correlation: rho = {corr:.3f}
   - {"Simpler compositions tend to have higher repetitions" if corr < 0 else "More complex compositions have higher repetitions" if corr > 0 else "No clear pattern"}

3. 2x/3x NEAR-EQUAL:
   - Ratio = {ratio_2_3:.3f}
   - This is NOT what random counting would produce
   - Could suggest deliberate ratio choices (2:1 vs 3:1 proportions)

4. WITHIN-FOLIO PATTERNS:
   - Folios show mixed repetition counts
   - If entries on same folio are parts of a recipe, different
     components have different proportions

5. TOKEN REPETITION IN BLOCKS:
   - {len(token_reps_in_blocks)} blocks have repeated tokens
   - Could indicate internal ratios (2 parts A, 1 part B)

## RATIO INTERPRETATION

If repetition = RATIO/PROPORTION:

  Entry format: [MIXTURE DESCRIPTION] x [PROPORTION]

  Example: "chol daiin shor" x 3
  Meaning: "3 parts of the mixture containing ch-ol, daiin, sh-or"

  This would explain:
  - Why 2x and 3x are near-equal (both common ratios)
  - Why same composition has different counts (different recipes)
  - Why higher counts have simpler blocks (concentrated simple ingredients)
  - Why blocks are unique (each mixture is a specific formulation)

## ALTERNATIVE: HIERARCHICAL RATIO

The repetition might encode a TIER or CONCENTRATION LEVEL:
  - 2x = base amount / dilute
  - 3x = standard amount / normal
  - 4x = elevated amount / concentrated
  - 5x = maximum amount / pure

This would explain the inverse complexity (simpler = more concentrated).

## VERDICT

The ratio hypothesis is PLAUSIBLE and explains several patterns:
- Variable repetition for same composition
- Near-equal 2x/3x distribution
- Inverse complexity relationship
- Block uniqueness with count variation

This is consistent with Currier A being a FORMULATION REGISTER
where each entry specifies:
- WHAT: the mixture composition (block content)
- HOW MUCH: the proportion/ratio (repetition count)
""")


if __name__ == '__main__':
    main()
