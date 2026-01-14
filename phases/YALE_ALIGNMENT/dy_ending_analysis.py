"""
Test 5: dy Ending Anomaly Analysis
Phase: YALE_ALIGNMENT

Yale finding: "The 'dy' (looks like '89') ending is extremely common in
Language B but rare in Language A."

Test: Verify this maps to our Currier A/B classification.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_interlinear():
    """Load the interlinear word data with Currier language tags."""
    data_dir = Path(__file__).parent.parent.parent / "data" / "transcriptions"
    interlinear_path = data_dir / "interlinear_full_words.txt"

    words = []
    with open(interlinear_path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')
        # Find column indices
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


def analyze_dy_endings(words):
    """Analyze distribution of 'dy' endings across languages."""

    # Count endings
    ending_by_lang = defaultdict(Counter)
    dy_words_by_lang = defaultdict(list)

    for entry in words:
        word = entry['word']
        lang = entry['language']

        # Get last 2 characters as ending
        if len(word) >= 2:
            ending = word[-2:]
            ending_by_lang[lang][ending] += 1

            if ending == 'dy':
                dy_words_by_lang[lang].append(word)

    return ending_by_lang, dy_words_by_lang


def main():
    print("=" * 60)
    print("TEST 5: 'dy' ENDING ANOMALY ANALYSIS")
    print("Yale Expert Alignment Phase")
    print("=" * 60)

    # Load data
    words = load_interlinear()
    print(f"\nLoaded {len(words)} words with Currier language tags")

    # Split by language
    a_words = [w for w in words if w['language'] == 'A']
    b_words = [w for w in words if w['language'] == 'B']
    print(f"  Language A: {len(a_words)} words")
    print(f"  Language B: {len(b_words)} words")

    # Analyze endings
    ending_by_lang, dy_words_by_lang = analyze_dy_endings(words)

    # Calculate dy frequency
    a_dy_count = ending_by_lang['A']['dy']
    b_dy_count = ending_by_lang['B']['dy']

    a_total_2char = sum(ending_by_lang['A'].values())
    b_total_2char = sum(ending_by_lang['B'].values())

    a_dy_rate = 100 * a_dy_count / a_total_2char if a_total_2char > 0 else 0
    b_dy_rate = 100 * b_dy_count / b_total_2char if b_total_2char > 0 else 0

    print("\n" + "-" * 60)
    print("'dy' ENDING FREQUENCY")
    print("-" * 60)
    print(f"\nLanguage A: {a_dy_count}/{a_total_2char} = {a_dy_rate:.2f}%")
    print(f"Language B: {b_dy_count}/{b_total_2char} = {b_dy_rate:.2f}%")
    print(f"\nRatio (B/A): {b_dy_rate/a_dy_rate:.1f}x" if a_dy_rate > 0 else "")

    # Yale prediction: dy common in B, rare in A
    if b_dy_rate > a_dy_rate * 2:
        prediction_status = "CONFIRMED"
        print(f"\n>>> YALE PREDICTION CONFIRMED: 'dy' is {b_dy_rate/a_dy_rate:.1f}x more common in B")
    else:
        prediction_status = "NOT CONFIRMED"
        print(f"\n>>> YALE PREDICTION NOT CONFIRMED")

    # Top endings comparison
    print("\n" + "-" * 60)
    print("TOP 10 ENDINGS BY LANGUAGE")
    print("-" * 60)

    print("\nLanguage A:")
    for ending, count in ending_by_lang['A'].most_common(10):
        pct = 100 * count / a_total_2char
        print(f"  '{ending}': {count} ({pct:.2f}%)")

    print("\nLanguage B:")
    for ending, count in ending_by_lang['B'].most_common(10):
        pct = 100 * count / b_total_2char
        print(f"  '{ending}': {count} ({pct:.2f}%)")

    # Look for other diagnostic endings
    print("\n" + "-" * 60)
    print("A/B DISCRIMINATING ENDINGS (>3x ratio)")
    print("-" * 60)

    all_endings = set(ending_by_lang['A'].keys()) | set(ending_by_lang['B'].keys())
    discriminating = []

    for ending in all_endings:
        a_rate = ending_by_lang['A'][ending] / a_total_2char if a_total_2char > 0 else 0
        b_rate = ending_by_lang['B'][ending] / b_total_2char if b_total_2char > 0 else 0

        if a_rate > 0 and b_rate > 0:
            ratio = max(b_rate / a_rate, a_rate / b_rate)
            if ratio > 3:
                discriminating.append({
                    'ending': ending,
                    'a_rate': a_rate,
                    'b_rate': b_rate,
                    'ratio': ratio,
                    'favors': 'B' if b_rate > a_rate else 'A'
                })

    discriminating.sort(key=lambda x: x['ratio'], reverse=True)

    print("\nEndings that strongly discriminate A from B:")
    for d in discriminating[:15]:
        print(f"  '{d['ending']}': favors {d['favors']} ({d['ratio']:.1f}x)")

    # Sample dy words
    print("\n" + "-" * 60)
    print("SAMPLE 'dy' WORDS BY LANGUAGE")
    print("-" * 60)

    print(f"\nLanguage A ({len(dy_words_by_lang['A'])} total):")
    unique_a_dy = list(set(dy_words_by_lang['A']))[:10]
    print(f"  {', '.join(unique_a_dy)}")

    print(f"\nLanguage B ({len(dy_words_by_lang['B'])} total):")
    unique_b_dy = list(set(dy_words_by_lang['B']))[:10]
    print(f"  {', '.join(unique_b_dy)}")

    # Build results
    results = {
        "test": "DY_ENDING_ANALYSIS",
        "date": "2026-01-14",
        "yale_finding": "'dy' ending common in Language B, rare in Language A",
        "prediction_status": prediction_status,
        "language_a": {
            "total_words": len(a_words),
            "dy_count": a_dy_count,
            "dy_rate_percent": round(a_dy_rate, 3)
        },
        "language_b": {
            "total_words": len(b_words),
            "dy_count": b_dy_count,
            "dy_rate_percent": round(b_dy_rate, 3)
        },
        "b_to_a_ratio": round(b_dy_rate / a_dy_rate, 2) if a_dy_rate > 0 else None,
        "top_discriminating_endings": [
            {"ending": d['ending'], "favors": d['favors'], "ratio": round(d['ratio'], 1)}
            for d in discriminating[:10]
        ],
        "interpretation": ""
    }

    if prediction_status == "CONFIRMED":
        results["interpretation"] = (
            f"Yale finding CONFIRMED. 'dy' endings are {results['b_to_a_ratio']}x "
            f"more common in Language B ({b_dy_rate:.2f}%) than Language A ({a_dy_rate:.2f}%). "
            "This validates that our Currier A/B classification captures real linguistic differences."
        )
    else:
        results["interpretation"] = (
            f"Yale finding NOT CONFIRMED. 'dy' ending rates: A={a_dy_rate:.2f}%, B={b_dy_rate:.2f}%."
        )

    # Save results
    output_path = Path(__file__).parent.parent.parent / "results" / "dy_ending_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")
    print(f"\n{results['interpretation']}")

    return results


if __name__ == "__main__":
    main()
