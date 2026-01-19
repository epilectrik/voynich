"""
EXT-HF-03 Supplemental: Rare Bigram Section Distribution

Test whether rare bigrams show section-exclusive patterns suggesting
structured "lessons" vs random distribution.

Hypothesis: If practice is structured, different sections would focus
on different difficult character combinations (low overlap).
If practice is random, rare bigrams would be distributed evenly.
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from itertools import combinations

project_root = Path(__file__).parent.parent.parent

# Token filtering (same as main analysis)
HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}

OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol', 's', 'o', 'd', 'y',
    'a', 'e', 'l', 'r', 'k', 'h', 'c', 't', 'n', 'p', 'm', 'g', 'f',
    'dain', 'chain', 'shain', 'ain', 'in', 'an', 'dan',
}

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}
KERNEL_TOKENS = {'k', 'h', 'e', 's', 't', 'd', 'l', 'o', 'c', 'r'}


def is_grammar_token(token):
    t = token.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def is_human_track_strict(token):
    t = token.lower().strip()
    if len(t) < 2:
        return False
    if not t.isalpha():
        return False
    if t in HAZARD_TOKENS:
        return False
    if t in OPERATIONAL_TOKENS:
        return False
    if t in KERNEL_TOKENS:
        return False
    if is_grammar_token(t):
        return False
    return True


def is_executable_token(token):
    t = token.lower().strip()
    if len(t) < 2:
        return False
    if not t.isalpha():
        return False
    if is_grammar_token(t):
        return True
    if t in OPERATIONAL_TOKENS:
        return True
    return False


def get_bigrams(token):
    """Extract all bigrams from a token."""
    t = token.lower()
    return [t[i:i+2] for i in range(len(t)-1)]


def load_data():
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # CRITICAL: Filter to H (PRIMARY) transcriber only
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"').strip()
                section = parts[3].strip('"') if len(parts) > 3 else ''
                if word and section:
                    data.append({'token': word.lower(), 'section': section})
    return data


def main():
    print("=" * 70)
    print("EXT-HF-03 SUPPLEMENTAL: Rare Bigram Section Distribution")
    print("=" * 70)

    data = load_data()
    print(f"\nLoaded {len(data)} tokens")

    # Separate HT and Exec tokens by section
    ht_by_section = defaultdict(list)
    exec_tokens = []

    for d in data:
        token = d['token']
        section = d['section']

        if is_human_track_strict(token):
            ht_by_section[section].append(token)
        elif is_executable_token(token):
            exec_tokens.append(token)

    print(f"\nExecutable tokens: {len(exec_tokens)}")
    print(f"HT tokens by section:")
    for s in sorted(ht_by_section.keys()):
        print(f"  {s}: {len(ht_by_section[s])}")

    # Build global bigram frequency from exec corpus
    exec_bigram_counts = Counter()
    for token in exec_tokens:
        for bg in get_bigrams(token):
            exec_bigram_counts[bg] += 1

    # Identify bottom decile (rare) bigrams
    all_bigrams = list(exec_bigram_counts.keys())
    counts = [exec_bigram_counts[bg] for bg in all_bigrams]
    threshold = np.percentile(counts, 25)  # Bottom 25% for larger sample

    rare_bigrams = {bg for bg in all_bigrams if exec_bigram_counts[bg] <= threshold}
    print(f"\nRare bigrams (bottom quartile, count <= {threshold}): {len(rare_bigrams)}")
    print(f"Examples: {sorted(rare_bigrams)[:15]}")

    # For each section, find which rare bigrams appear in HT tokens
    section_rare_bigrams = {}

    for section, tokens in ht_by_section.items():
        section_bgs = set()
        for token in tokens:
            for bg in get_bigrams(token):
                if bg in rare_bigrams:
                    section_bgs.add(bg)
        section_rare_bigrams[section] = section_bgs

    print("\n" + "=" * 70)
    print("RARE BIGRAM DISTRIBUTION BY SECTION")
    print("=" * 70)

    for section in sorted(section_rare_bigrams.keys()):
        bgs = section_rare_bigrams[section]
        print(f"\n{section}: {len(bgs)} rare bigrams")
        if bgs:
            print(f"  {sorted(bgs)}")

    # Calculate section exclusivity for rare bigrams
    print("\n" + "=" * 70)
    print("RARE BIGRAM EXCLUSIVITY ANALYSIS")
    print("=" * 70)

    # For each rare bigram that appears in HT, count how many sections use it
    all_ht_rare_bigrams = set()
    for bgs in section_rare_bigrams.values():
        all_ht_rare_bigrams.update(bgs)

    bigram_section_count = {}
    for bg in all_ht_rare_bigrams:
        count = sum(1 for s, bgs in section_rare_bigrams.items() if bg in bgs)
        bigram_section_count[bg] = count

    # Exclusivity breakdown
    exclusive = [bg for bg, c in bigram_section_count.items() if c == 1]
    shared_2 = [bg for bg, c in bigram_section_count.items() if c == 2]
    shared_3plus = [bg for bg, c in bigram_section_count.items() if c >= 3]

    total_rare_in_ht = len(all_ht_rare_bigrams)

    print(f"\nTotal rare bigrams appearing in HT: {total_rare_in_ht}")
    print(f"\nExclusivity breakdown:")
    print(f"  Section-exclusive (1 section only): {len(exclusive)} ({100*len(exclusive)/total_rare_in_ht:.1f}%)")
    print(f"  Shared by 2 sections: {len(shared_2)} ({100*len(shared_2)/total_rare_in_ht:.1f}%)")
    print(f"  Shared by 3+ sections: {len(shared_3plus)} ({100*len(shared_3plus)/total_rare_in_ht:.1f}%)")

    print(f"\nSection-exclusive rare bigrams:")
    for bg in sorted(exclusive):
        for s, bgs in section_rare_bigrams.items():
            if bg in bgs:
                print(f"  '{bg}' -> Section {s}")
                break

    # Calculate pairwise Jaccard similarity between sections
    print("\n" + "=" * 70)
    print("SECTION PAIRWISE OVERLAP (Jaccard Similarity)")
    print("=" * 70)

    sections = sorted(section_rare_bigrams.keys())

    print("\n       ", end="")
    for s in sections:
        print(f"  {s:>5}", end="")
    print()

    jaccard_values = []
    for s1 in sections:
        print(f"  {s1}   ", end="")
        for s2 in sections:
            set1 = section_rare_bigrams[s1]
            set2 = section_rare_bigrams[s2]
            if len(set1) == 0 and len(set2) == 0:
                jaccard = 1.0
            elif len(set1 | set2) == 0:
                jaccard = 0.0
            else:
                jaccard = len(set1 & set2) / len(set1 | set2)
            print(f"  {jaccard:>5.2f}", end="")
            if s1 < s2:  # Only count each pair once
                jaccard_values.append(jaccard)
        print()

    mean_jaccard = np.mean(jaccard_values) if jaccard_values else 0
    print(f"\nMean pairwise Jaccard (off-diagonal): {mean_jaccard:.3f}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    exclusivity_rate = len(exclusive) / total_rare_in_ht if total_rare_in_ht > 0 else 0

    print(f"""
Rare Bigram Exclusivity Rate: {exclusivity_rate:.1%}
Mean Pairwise Jaccard: {mean_jaccard:.3f}

For reference:
- Token-level section exclusivity (from MCS): 80.7%
- If rare bigrams show similar exclusivity: SUPPORTS "lesson structure"
- If rare bigrams are shared across sections: WEAKENS lesson interpretation
""")

    if exclusivity_rate > 0.5 and mean_jaccard < 0.3:
        print("VERDICT: **LESSON STRUCTURE SUPPORTED**")
        print("Different sections focus on different rare bigrams with low overlap.")
        print("This strengthens the practice hypothesis.")
    elif exclusivity_rate < 0.3 or mean_jaccard > 0.5:
        print("VERDICT: **LESSON STRUCTURE NOT SUPPORTED**")
        print("Rare bigrams are shared across sections.")
        print("Practice appears opportunistic, not structured by curriculum.")
    else:
        print("VERDICT: **INDETERMINATE**")
        print("Partial exclusivity; structured practice possible but not clear.")

    # Additional: which sections have the MOST rare bigram engagement?
    print("\n" + "=" * 70)
    print("RARE BIGRAM DENSITY BY SECTION")
    print("=" * 70)

    for section in sorted(ht_by_section.keys()):
        tokens = ht_by_section[section]
        total_bigrams = sum(len(get_bigrams(t)) for t in tokens)
        rare_count = sum(1 for t in tokens for bg in get_bigrams(t) if bg in rare_bigrams)
        density = rare_count / total_bigrams if total_bigrams > 0 else 0
        print(f"  {section}: {rare_count}/{total_bigrams} = {density:.4f} rare bigram density")


if __name__ == '__main__':
    main()
