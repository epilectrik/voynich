"""
Test 6: Gallows Character Distribution by Regime
Phase: YALE_ALIGNMENT

Yale finding: Gallows characters (tall letters) have particular distributions.
The four main gallows (k, t, f, p in EVA) may correlate with operational states.

Test: Analyze gallows distribution across regimes and languages.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import re

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# EVA gallows characters (tall letters in the manuscript)
# k = plain gallows
# t = looped gallows
# f = forked gallows
# p = double-looped gallows
GALLOWS = ['k', 't', 'f', 'p']

# Bench gallows (gallows with 'ch' bench)
BENCH_GALLOWS = ['ckh', 'cth', 'cfh', 'cph']


def load_interlinear():
    """Load the interlinear word data with Currier language tags."""
    data_dir = Path(__file__).parent.parent.parent / "data" / "transcriptions"
    interlinear_path = data_dir / "interlinear_full_words.txt"

    words = []
    with open(interlinear_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        word_idx = header.index('"word"')
        lang_idx = header.index('"language"')
        folio_idx = header.index('"folio"')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > max(word_idx, lang_idx, folio_idx):
                word = parts[word_idx].strip('"')
                lang = parts[lang_idx].strip('"')
                folio = parts[folio_idx].strip('"')
                if lang in ('A', 'B') and word and not word.startswith('*'):
                    words.append({
                        'word': word,
                        'language': lang,
                        'folio': folio
                    })

    return words


def load_regime_assignments():
    """Load regime assignments for B folios."""
    results_dir = Path(__file__).parent.parent.parent / "results"
    cart_path = results_dir / "b_design_space_cartography.json"

    if not cart_path.exists():
        return {}

    with open(cart_path) as f:
        cart_data = json.load(f)

    regimes = {}
    for folio, data in cart_data.get("folio_positions", {}).items():
        regimes[folio.lower()] = data.get("regime", "UNKNOWN")

    return regimes


def count_gallows(word):
    """Count gallows characters in a word."""
    counts = Counter()

    # Count bench gallows first (so we don't double-count)
    word_lower = word.lower()
    for bg in BENCH_GALLOWS:
        count = word_lower.count(bg)
        if count > 0:
            counts[bg] = count
            # Remove to avoid recounting the gallows
            word_lower = word_lower.replace(bg, '')

    # Now count simple gallows
    for g in GALLOWS:
        counts[g] = word_lower.count(g)

    return counts


def main():
    print("=" * 60)
    print("TEST 6: GALLOWS CHARACTER DISTRIBUTION")
    print("Yale Expert Alignment Phase")
    print("=" * 60)

    # Load data
    words = load_interlinear()
    regimes = load_regime_assignments()

    print(f"\nLoaded {len(words)} words")
    print(f"Regime assignments available for {len(regimes)} folios")

    # Analyze by language
    gallows_by_lang = defaultdict(Counter)
    total_by_lang = Counter()

    for entry in words:
        word = entry['word']
        lang = entry['language']
        total_by_lang[lang] += len(word)  # Total characters

        counts = count_gallows(word)
        for g, c in counts.items():
            gallows_by_lang[lang][g] += c

    print("\n" + "-" * 60)
    print("GALLOWS FREQUENCY BY LANGUAGE")
    print("-" * 60)

    print("\n           Language A    Language B    Ratio (A/B)")
    print("-" * 55)

    for g in GALLOWS:
        a_count = gallows_by_lang['A'][g]
        b_count = gallows_by_lang['B'][g]
        a_rate = 1000 * a_count / total_by_lang['A'] if total_by_lang['A'] > 0 else 0
        b_rate = 1000 * b_count / total_by_lang['B'] if total_by_lang['B'] > 0 else 0
        ratio = a_rate / b_rate if b_rate > 0 else float('inf')
        print(f"  {g}:        {a_count:>6} ({a_rate:>5.2f})   {b_count:>6} ({b_rate:>5.2f})    {ratio:.2f}x")

    print("\nBench gallows:")
    for bg in BENCH_GALLOWS:
        a_count = gallows_by_lang['A'][bg]
        b_count = gallows_by_lang['B'][bg]
        a_rate = 1000 * a_count / total_by_lang['A'] if total_by_lang['A'] > 0 else 0
        b_rate = 1000 * b_count / total_by_lang['B'] if total_by_lang['B'] > 0 else 0
        ratio = a_rate / b_rate if b_rate > 0 else float('inf')
        if a_count > 10 or b_count > 10:  # Only show if meaningful
            print(f"  {bg}:      {a_count:>6} ({a_rate:>5.2f})   {b_count:>6} ({b_rate:>5.2f})    {ratio:.2f}x")

    # Analyze by regime (B folios only)
    print("\n" + "-" * 60)
    print("GALLOWS FREQUENCY BY REGIME (B folios only)")
    print("-" * 60)

    gallows_by_regime = defaultdict(Counter)
    total_by_regime = Counter()

    b_words = [w for w in words if w['language'] == 'B']
    for entry in b_words:
        word = entry['word']
        folio = entry['folio'].lower()
        regime = regimes.get(folio, 'UNKNOWN')

        total_by_regime[regime] += len(word)
        counts = count_gallows(word)
        for g, c in counts.items():
            gallows_by_regime[regime][g] += c

    print("\n           ", end="")
    regime_order = ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']
    for r in regime_order:
        print(f"{r[-1]:>10}", end="")
    print()
    print("-" * 55)

    for g in GALLOWS:
        print(f"  {g}:      ", end="")
        rates = []
        for r in regime_order:
            count = gallows_by_regime[r][g]
            total = total_by_regime[r]
            rate = 1000 * count / total if total > 0 else 0
            rates.append(rate)
            print(f"{rate:>10.2f}", end="")
        print()

    # Look for regime-specific gallows patterns
    print("\n" + "-" * 60)
    print("GALLOWS PROFILE BY REGIME")
    print("-" * 60)

    regime_profiles = {}
    for r in regime_order:
        total_gallows = sum(gallows_by_regime[r][g] for g in GALLOWS)
        if total_gallows > 0:
            profile = {g: round(100 * gallows_by_regime[r][g] / total_gallows, 1) for g in GALLOWS}
            dominant = max(profile, key=profile.get)
            regime_profiles[r] = {
                'total_gallows': total_gallows,
                'profile': profile,
                'dominant': dominant
            }
            print(f"\n{r}:")
            print(f"  Total gallows: {total_gallows}")
            print(f"  Distribution: {profile}")
            print(f"  Dominant: {dominant} ({profile[dominant]}%)")

    # Positional analysis
    print("\n" + "-" * 60)
    print("GALLOWS POSITION IN WORD")
    print("-" * 60)

    position_by_lang = defaultdict(lambda: defaultdict(Counter))

    for entry in words:
        word = entry['word']
        lang = entry['language']
        word_lower = word.lower()

        for g in GALLOWS:
            for i, char in enumerate(word_lower):
                if char == g:
                    if i == 0:
                        pos = 'initial'
                    elif i == len(word) - 1:
                        pos = 'final'
                    else:
                        pos = 'medial'
                    position_by_lang[lang][g][pos] += 1

    print("\nLanguage A gallows positions:")
    for g in GALLOWS:
        total = sum(position_by_lang['A'][g].values())
        if total > 0:
            dist = {k: round(100 * v / total) for k, v in position_by_lang['A'][g].items()}
            print(f"  {g}: {dist}")

    print("\nLanguage B gallows positions:")
    for g in GALLOWS:
        total = sum(position_by_lang['B'][g].values())
        if total > 0:
            dist = {k: round(100 * v / total) for k, v in position_by_lang['B'][g].items()}
            print(f"  {g}: {dist}")

    # Build results
    results = {
        "test": "GALLOWS_DISTRIBUTION",
        "date": "2026-01-14",
        "gallows_chars": GALLOWS,
        "by_language": {
            "A": {
                "total_chars": total_by_lang['A'],
                "gallows_counts": dict(gallows_by_lang['A']),
                "gallows_per_1000": {
                    g: round(1000 * gallows_by_lang['A'][g] / total_by_lang['A'], 3)
                    for g in GALLOWS
                }
            },
            "B": {
                "total_chars": total_by_lang['B'],
                "gallows_counts": dict(gallows_by_lang['B']),
                "gallows_per_1000": {
                    g: round(1000 * gallows_by_lang['B'][g] / total_by_lang['B'], 3)
                    for g in GALLOWS
                }
            }
        },
        "by_regime": {
            r: {
                "total_chars": total_by_regime[r],
                "gallows_counts": dict(gallows_by_regime[r]),
                "profile": regime_profiles.get(r, {}).get('profile', {}),
                "dominant": regime_profiles.get(r, {}).get('dominant', None)
            }
            for r in regime_order
        },
        "findings": []
    }

    # Generate findings
    # Check for A vs B differences
    for g in GALLOWS:
        a_rate = results['by_language']['A']['gallows_per_1000'][g]
        b_rate = results['by_language']['B']['gallows_per_1000'][g]
        if a_rate > 0 and b_rate > 0:
            ratio = a_rate / b_rate
            if ratio > 1.5:
                results['findings'].append(f"Gallows '{g}' is {ratio:.1f}x more common in A than B")
            elif ratio < 0.67:
                results['findings'].append(f"Gallows '{g}' is {1/ratio:.1f}x more common in B than A")

    # Check for regime differences
    for r, data in regime_profiles.items():
        dom = data['dominant']
        pct = data['profile'][dom]
        if pct > 35:  # Significant dominance
            results['findings'].append(f"{r} shows {dom}-dominant gallows profile ({pct}%)")

    # Save results
    output_path = Path(__file__).parent.parent.parent / "results" / "gallows_distribution.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    for finding in results['findings']:
        print(f"  - {finding}")

    return results


if __name__ == "__main__":
    main()
