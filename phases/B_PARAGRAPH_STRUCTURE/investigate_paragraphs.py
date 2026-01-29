#!/usr/bin/env python3
"""
Investigate paragraph structure in Currier B.

Key questions:
1. Do B paragraphs function as "mini-programs" within folios?
2. Is there HT enrichment at paragraph boundaries (like folio line 1)?
3. What initiates B paragraphs? (gallows-initial like A? or something else?)
4. Is there within-paragraph line-position structure?
"""

import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
from statistics import mean, stdev

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

# Load class token map for HT identification
CLASS_MAP_PATH = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'

def load_class_map():
    """Load the token-to-class mapping."""
    with open(CLASS_MAP_PATH) as f:
        data = json.load(f)
    return data['token_to_class']

def is_ht(word, class_map):
    """Check if a token is HT (unclassified - not in the 49 classes)."""
    return word not in class_map

def analyze_b_paragraphs():
    """Main analysis function."""
    tx = Transcript()
    morph = Morphology()
    class_map = load_class_map()

    # Collect all B tokens with paragraph info
    # Group by folio -> paragraph -> line
    folios = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Track paragraph starts
    par_starts = []  # (folio, line, token_idx)

    current_par_id = 0
    current_folio = None

    for token in tx.currier_b():
        # Track paragraph boundaries
        if token.par_initial:
            current_par_id += 1

        if token.folio != current_folio:
            current_folio = token.folio
            current_par_id += 1  # Reset par ID on new folio

        folios[token.folio][current_par_id][token.line].append(token)

        if token.par_initial:
            par_starts.append((token.folio, token.line, token.word))

    # Re-process to get proper paragraph structure
    # A paragraph is a sequence of lines until the next par_initial
    print("=" * 70)
    print("CURRIER B PARAGRAPH STRUCTURE ANALYSIS")
    print("=" * 70)

    # Build proper paragraph data structure
    paragraphs = []  # List of (folio, par_idx, lines_data)

    current_par = None
    current_folio = None

    for token in tx.currier_b():
        if token.folio != current_folio:
            # New folio - save current par and start fresh
            if current_par is not None:
                paragraphs.append(current_par)
            current_folio = token.folio
            current_par = {
                'folio': token.folio,
                'lines': defaultdict(list),
                'is_folio_line1_start': token.line == '1'
            }

        if token.par_initial and current_par is not None and len(current_par['lines']) > 0:
            # Save previous paragraph and start new one
            paragraphs.append(current_par)
            current_par = {
                'folio': token.folio,
                'lines': defaultdict(list),
                'is_folio_line1_start': token.line == '1'
            }

        current_par['lines'][token.line].append(token)

    # Don't forget last paragraph
    if current_par is not None and len(current_par['lines']) > 0:
        paragraphs.append(current_par)

    print(f"\n1. PARAGRAPH BOUNDARY STATISTICS")
    print("-" * 50)

    # Count paragraphs per folio
    pars_per_folio = Counter()
    for par in paragraphs:
        pars_per_folio[par['folio']] += 1

    print(f"Total B paragraphs: {len(paragraphs)}")
    print(f"B folios with paragraphs: {len(pars_per_folio)}")
    print(f"Mean paragraphs/folio: {mean(pars_per_folio.values()):.2f}")
    print(f"Max paragraphs in folio: {max(pars_per_folio.values())} ({pars_per_folio.most_common(1)[0][0]})")

    # Lines per paragraph
    lines_per_par = [len(par['lines']) for par in paragraphs]
    print(f"\nLines per paragraph:")
    print(f"  Mean: {mean(lines_per_par):.2f}")
    print(f"  Stdev: {stdev(lines_per_par):.2f}")
    print(f"  Min: {min(lines_per_par)}, Max: {max(lines_per_par)}")

    # Distribution of lines per paragraph
    lines_dist = Counter(lines_per_par)
    print(f"\n  Distribution (lines -> count):")
    for n_lines in sorted(lines_dist.keys())[:15]:
        print(f"    {n_lines} lines: {lines_dist[n_lines]} paragraphs")

    print(f"\n2. HT ENRICHMENT AT PARAGRAPH BOUNDARIES")
    print("-" * 50)

    # For each paragraph, compute HT fraction in line 1 vs lines 2+
    par_line1_ht = []
    par_lines2plus_ht = []
    par_deltas = []

    for par in paragraphs:
        sorted_lines = sorted(par['lines'].keys(), key=lambda x: int(x) if x.isdigit() else 0)
        if len(sorted_lines) < 2:
            continue  # Need at least 2 lines for comparison

        first_line = sorted_lines[0]
        first_line_tokens = par['lines'][first_line]

        # HT in first line of paragraph
        ht_in_first = sum(1 for t in first_line_tokens if is_ht(t.word, class_map))
        total_first = len(first_line_tokens)

        # HT in lines 2+
        ht_in_rest = 0
        total_rest = 0
        for line in sorted_lines[1:]:
            line_tokens = par['lines'][line]
            ht_in_rest += sum(1 for t in line_tokens if is_ht(t.word, class_map))
            total_rest += len(line_tokens)

        if total_first > 0 and total_rest > 0:
            ht_frac_first = ht_in_first / total_first
            ht_frac_rest = ht_in_rest / total_rest
            delta = ht_frac_first - ht_frac_rest

            par_line1_ht.append(ht_frac_first)
            par_lines2plus_ht.append(ht_frac_rest)
            par_deltas.append(delta)

    print(f"Paragraphs with 2+ lines analyzed: {len(par_line1_ht)}")
    print(f"\nHT fraction in paragraph line 1: {100*mean(par_line1_ht):.1f}%")
    print(f"HT fraction in paragraph lines 2+: {100*mean(par_lines2plus_ht):.1f}%")
    print(f"Delta (line1 - rest): +{100*mean(par_deltas):.1f}pp")

    # Compare to folio-level pattern (C747: 50.2% line 1 vs 29.8% elsewhere)
    print(f"\nComparison to C747 (folio level):")
    print(f"  C747 folio line 1 HT: 50.2%")
    print(f"  C747 folio lines 2+ HT: 29.8%")
    print(f"  C747 delta: +20.3pp")

    # Direction count
    positive = sum(1 for d in par_deltas if d > 0)
    negative = sum(1 for d in par_deltas if d < 0)
    zero = sum(1 for d in par_deltas if d == 0)
    print(f"\nDirection: {positive} positive / {zero} zero / {negative} negative")

    print(f"\n3. WHAT INITIATES B PARAGRAPHS?")
    print("-" * 50)

    # For each paragraph, get the FIRST token
    first_tokens = []
    first_token_prefixes = []
    first_token_is_gallows = []

    GALLOWS = {'k', 't', 'p', 'f'}  # Gallows letters

    for par in paragraphs:
        sorted_lines = sorted(par['lines'].keys(), key=lambda x: int(x) if x.isdigit() else 0)
        if not sorted_lines:
            continue
        first_line = sorted_lines[0]
        tokens = par['lines'][first_line]
        if not tokens:
            continue

        first_token = tokens[0]
        first_tokens.append(first_token.word)

        # Extract morphology
        m = morph.extract(first_token.word)

        # Is it gallows-initial?
        word = first_token.word
        is_gallows = word[0] in GALLOWS if word else False
        first_token_is_gallows.append(is_gallows)

        # Prefix
        first_token_prefixes.append(m.prefix)

    print(f"Total paragraphs analyzed: {len(first_tokens)}")

    # Top first tokens
    first_token_counts = Counter(first_tokens)
    print(f"\nTop 20 first tokens in paragraphs:")
    for token, count in first_token_counts.most_common(20):
        pct = 100 * count / len(first_tokens)
        print(f"  {token}: {count} ({pct:.1f}%)")

    # Gallows-initial rate
    gallows_rate = sum(first_token_is_gallows) / len(first_token_is_gallows)
    print(f"\nGallows-initial rate: {100*gallows_rate:.1f}%")

    # Prefix distribution
    prefix_counts = Counter(first_token_prefixes)
    print(f"\nPREFIX distribution of paragraph-initial tokens:")
    for prefix, count in prefix_counts.most_common(15):
        pct = 100 * count / len(first_token_prefixes)
        prefix_display = prefix if prefix else '(none)'
        print(f"  {prefix_display}: {count} ({pct:.1f}%)")

    print(f"\n4. PARAGRAPH-INTERNAL LINE STRUCTURE")
    print("-" * 50)

    # For paragraphs with 5+ lines, track HT by position
    long_pars = [p for p in paragraphs if len(p['lines']) >= 5]
    print(f"Paragraphs with 5+ lines: {len(long_pars)}")

    # HT fraction by relative position (1, 2, 3, 4, 5+)
    ht_by_position = defaultdict(list)

    for par in long_pars:
        sorted_lines = sorted(par['lines'].keys(), key=lambda x: int(x) if x.isdigit() else 0)

        for i, line in enumerate(sorted_lines):
            tokens = par['lines'][line]
            if not tokens:
                continue

            ht_count = sum(1 for t in tokens if is_ht(t.word, class_map))
            ht_frac = ht_count / len(tokens)

            # Position: 1, 2, 3, 4, or '5+'
            pos = i + 1 if i < 5 else '5+'
            ht_by_position[pos].append(ht_frac)

    print(f"\nHT fraction by paragraph line position (5+ line pars only):")
    for pos in [1, 2, 3, 4, '5+']:
        fracs = ht_by_position[pos]
        if fracs:
            print(f"  Position {pos}: {100*mean(fracs):.1f}% HT (n={len(fracs)})")

    print(f"\n5. FOLIO LINE 1 vs PARAGRAPH LINE 1 OVERLAP")
    print("-" * 50)

    # Count paragraphs that start at folio line 1 vs elsewhere
    folio_line1_pars = [p for p in paragraphs if p['is_folio_line1_start']]
    other_pars = [p for p in paragraphs if not p['is_folio_line1_start']]

    print(f"Paragraphs starting at folio line 1: {len(folio_line1_pars)}")
    print(f"Paragraphs starting elsewhere: {len(other_pars)}")

    # HT enrichment for non-folio-line1 paragraphs
    if other_pars:
        other_par_line1_ht = []
        other_par_rest_ht = []
        other_par_deltas = []

        for par in other_pars:
            sorted_lines = sorted(par['lines'].keys(), key=lambda x: int(x) if x.isdigit() else 0)
            if len(sorted_lines) < 2:
                continue

            first_line = sorted_lines[0]
            first_line_tokens = par['lines'][first_line]

            ht_in_first = sum(1 for t in first_line_tokens if is_ht(t.word, class_map))
            total_first = len(first_line_tokens)

            ht_in_rest = 0
            total_rest = 0
            for line in sorted_lines[1:]:
                line_tokens = par['lines'][line]
                ht_in_rest += sum(1 for t in line_tokens if is_ht(t.word, class_map))
                total_rest += len(line_tokens)

            if total_first > 0 and total_rest > 0:
                ht_frac_first = ht_in_first / total_first
                ht_frac_rest = ht_in_rest / total_rest
                delta = ht_frac_first - ht_frac_rest

                other_par_line1_ht.append(ht_frac_first)
                other_par_rest_ht.append(ht_frac_rest)
                other_par_deltas.append(delta)

        if other_par_line1_ht:
            print(f"\nFor paragraphs NOT at folio line 1:")
            print(f"  Paragraphs analyzed: {len(other_par_line1_ht)}")
            print(f"  HT in paragraph line 1: {100*mean(other_par_line1_ht):.1f}%")
            print(f"  HT in paragraph lines 2+: {100*mean(other_par_rest_ht):.1f}%")
            print(f"  Delta: {100*mean(other_par_deltas):+.1f}pp")

            # Direction
            pos = sum(1 for d in other_par_deltas if d > 0)
            neg = sum(1 for d in other_par_deltas if d < 0)
            zero = sum(1 for d in other_par_deltas if d == 0)
            print(f"  Direction: {pos} positive / {zero} zero / {neg} negative")

    print(f"\n6. FIRST TOKEN BY PARAGRAPH START POSITION")
    print("-" * 50)

    # Compare first tokens at folio line 1 vs elsewhere
    folio_line1_first_tokens = []
    other_first_tokens = []

    for par in paragraphs:
        sorted_lines = sorted(par['lines'].keys(), key=lambda x: int(x) if x.isdigit() else 0)
        if not sorted_lines:
            continue
        first_line = sorted_lines[0]
        tokens = par['lines'][first_line]
        if not tokens:
            continue

        first_token = tokens[0].word
        if par['is_folio_line1_start']:
            folio_line1_first_tokens.append(first_token)
        else:
            other_first_tokens.append(first_token)

    print(f"\nFirst tokens at FOLIO LINE 1 (n={len(folio_line1_first_tokens)}):")
    for token, count in Counter(folio_line1_first_tokens).most_common(15):
        print(f"  {token}: {count}")

    print(f"\nFirst tokens at OTHER positions (n={len(other_first_tokens)}):")
    for token, count in Counter(other_first_tokens).most_common(15):
        print(f"  {token}: {count}")

    # HT rate comparison
    folio_line1_ht_rate = sum(1 for t in folio_line1_first_tokens if is_ht(t, class_map)) / len(folio_line1_first_tokens) if folio_line1_first_tokens else 0
    other_ht_rate = sum(1 for t in other_first_tokens if is_ht(t, class_map)) / len(other_first_tokens) if other_first_tokens else 0

    print(f"\nHT rate in first token:")
    print(f"  Folio line 1 paragraphs: {100*folio_line1_ht_rate:.1f}%")
    print(f"  Other paragraphs: {100*other_ht_rate:.1f}%")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"""
Key Findings:

1. B PARAGRAPHS AS STRUCTURAL UNITS:
   - {len(paragraphs)} paragraphs across {len(pars_per_folio)} B folios
   - Mean {mean(pars_per_folio.values()):.1f} paragraphs per folio
   - Mean {mean(lines_per_par):.1f} lines per paragraph

2. HT ENRICHMENT PATTERN:
   - Paragraph line 1: {100*mean(par_line1_ht):.1f}% HT
   - Paragraph lines 2+: {100*mean(par_lines2plus_ht):.1f}% HT
   - Delta: +{100*mean(par_deltas):.1f}pp
   - Compare to C747 folio pattern: +20.3pp

3. PARAGRAPH INITIATION:
   - Gallows-initial rate: {100*gallows_rate:.1f}%
   - Most common prefix: {prefix_counts.most_common(1)[0][0] or '(none)'} ({100*prefix_counts.most_common(1)[0][1]/len(first_token_prefixes):.1f}%)

4. VERDICT: Do paragraphs show "mini-program" header pattern?
   [Analysis above provides the evidence]
""")

if __name__ == '__main__':
    analyze_b_paragraphs()
