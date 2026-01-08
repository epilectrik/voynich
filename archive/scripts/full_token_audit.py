"""
Full Token Audit

Comprehensive check of every token in the manuscript against our
classification systems to ensure nothing snuck past.

Classification hierarchy:
1. Currier B grammar (49 classes, 479 canonical types)
2. Currier A compositional (PREFIX + MIDDLE + SUFFIX)
3. HT layer (disjoint HT prefixes)
4. AZC vocabulary
5. LINK tokens
6. Structural primitives (daiin, ol)
7. Single-character tokens
8. Damaged tokens (contain *)
9. TRUE ORPHAN (nothing fits)
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR_FILE = BASE / "results" / "canonical_grammar.json"

# Known classification components
A_PREFIXES = {'ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol'}
HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc', 'do', 'ta', 'ke', 'al', 'po', 'ko', 'yd', 'ysh', 'ych', 'kch', 'ks'}
LINK_TOKENS = {'ol', 'al', 'or', 'ar', 'aiin', 'daiin', 'chol', 'chor', 'shol', 'shor'}
STRUCTURAL_PRIMITIVES = {'daiin', 'ol'}

# Extended cluster prefixes from MORPH-CLOSE
EXTENDED_CLUSTERS = {'ck', 'ckh', 'ds', 'dsh', 'cp', 'cph', 'ks', 'ksh', 'ts', 'tsh', 'ps', 'psh',
                     'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch'}

# L-compound prefixes (B-specific operators from Constraint 298)
L_COMPOUNDS = {'lch', 'lk', 'lsh', 'lkch', 'lo', 'lr', 'ls'}

# Common suffixes
COMMON_SUFFIXES = {'aiin', 'ain', 'ar', 'or', 'al', 'ol', 'dy', 'ey', 'y', 'r', 'l', 's', 'd',
                   'chy', 'shy', 'eey', 'ody', 'edy', 'oly', 'am'}

# Standalone valid tokens (suffixes/markers that appear alone)
STANDALONE_TOKENS = {'ain', 'am', 'aiin', 'aiiin', 'an', 'ar', 'or', 'al', 'ol', 'dy', 'ey',
                     'oiin', 'oiiin', 'om', 'aim', 'aiim', 'lo', 'ro', 'in', 'iin', 'iiin'}

def load_data():
    """Load transcription and grammar."""
    data = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            data.append(row)

    with open(GRAMMAR_FILE, 'r') as f:
        grammar = json.load(f)

    # Build canonical vocabulary from grammar
    canonical_vocab = set()
    for term in grammar.get('terminals', {}).get('list', []):
        canonical_vocab.add(term['symbol'])

    return data, canonical_vocab

def classify_token(token, canonical_vocab, language):
    """
    Classify a single token. Returns (category, details).
    """
    if not token:
        return ('EMPTY', None)

    # Damaged tokens
    if '*' in token:
        return ('DAMAGED', token)

    # Single character
    if len(token) == 1:
        return ('SINGLE_CHAR', token)

    # Standalone valid tokens (suffixes appearing alone)
    if token in STANDALONE_TOKENS:
        return ('STANDALONE_SUFFIX', token)

    # Canonical B grammar
    if token in canonical_vocab:
        return ('B_GRAMMAR', token)

    # LINK tokens
    if token in LINK_TOKENS:
        return ('LINK', token)

    # Structural primitives
    if token in STRUCTURAL_PRIMITIVES:
        return ('STRUCTURAL_PRIMITIVE', token)

    # Check for A-prefix compositional
    for prefix in sorted(A_PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            remainder = token[len(prefix):]
            # Check if remainder has valid suffix
            for suffix in sorted(COMMON_SUFFIXES, key=len, reverse=True):
                if remainder.endswith(suffix):
                    middle = remainder[:-len(suffix)]
                    return ('A_COMPOSITIONAL', {'prefix': prefix, 'middle': middle, 'suffix': suffix})
            # Has prefix but no recognized suffix
            return ('A_PREFIX_ONLY', {'prefix': prefix, 'remainder': remainder})

    # Check for HT-prefix compositional
    for prefix in sorted(HT_PREFIXES, key=len, reverse=True):
        if token.startswith(prefix):
            remainder = token[len(prefix):]
            # Check for B-suffix (HT+B hybrid)
            for suffix in sorted(COMMON_SUFFIXES, key=len, reverse=True):
                if remainder.endswith(suffix):
                    middle = remainder[:-len(suffix)]
                    return ('HT_COMPOSITIONAL', {'prefix': prefix, 'middle': middle, 'suffix': suffix})
            return ('HT_PREFIX_ONLY', {'prefix': prefix, 'remainder': remainder})

    # Check for extended cluster patterns
    for cluster in sorted(EXTENDED_CLUSTERS, key=len, reverse=True):
        if token.startswith(cluster):
            return ('EXTENDED_CLUSTER', {'cluster': cluster, 'remainder': token[len(cluster):]})

    # Check for L-compound patterns (B-specific)
    for lc in sorted(L_COMPOUNDS, key=len, reverse=True):
        if token.startswith(lc):
            return ('L_COMPOUND', {'prefix': lc, 'remainder': token[len(lc):]})

    # Check if it has ANY recognized suffix (suffix-only)
    for suffix in sorted(COMMON_SUFFIXES, key=len, reverse=True):
        if token.endswith(suffix) and len(token) > len(suffix):
            return ('SUFFIX_ONLY', {'base': token[:-len(suffix)], 'suffix': suffix})

    # EVA-valid check (only EVA characters)
    eva_chars = set('abcdefghiklmnopqrstxy')
    if all(c in eva_chars for c in token):
        return ('EVA_UNCLASSIFIED', token)

    # Contains non-EVA characters
    return ('NON_EVA', token)

def main():
    print("="*70)
    print("FULL TOKEN AUDIT")
    print("="*70)
    print("\nClassifying every token in the manuscript...")

    data, canonical_vocab = load_data()

    print(f"\nCanonical B grammar vocabulary: {len(canonical_vocab)} types")

    # Classify all tokens
    classifications = defaultdict(list)
    token_classifications = {}  # token -> category
    language_breakdown = defaultdict(lambda: defaultdict(int))

    total_tokens = 0
    unique_tokens = set()

    for row in data:
        if row.get('transcriber') != 'H':
            continue

        token = row.get('word', '')
        language = row.get('language', 'NA')

        if not token:
            continue

        total_tokens += 1
        unique_tokens.add(token)

        category, details = classify_token(token, canonical_vocab, language)
        classifications[category].append((token, details, row))
        language_breakdown[language][category] += 1

        if token not in token_classifications:
            token_classifications[token] = category

    # Summary
    print(f"\nTotal tokens (H transcriber): {total_tokens:,}")
    print(f"Unique token types: {len(unique_tokens):,}")

    print("\n" + "="*70)
    print("CLASSIFICATION SUMMARY")
    print("="*70)

    category_order = [
        'B_GRAMMAR', 'A_COMPOSITIONAL', 'HT_COMPOSITIONAL', 'LINK',
        'STANDALONE_SUFFIX', 'STRUCTURAL_PRIMITIVE', 'A_PREFIX_ONLY', 'HT_PREFIX_ONLY',
        'EXTENDED_CLUSTER', 'L_COMPOUND', 'SUFFIX_ONLY', 'SINGLE_CHAR', 'DAMAGED',
        'EVA_UNCLASSIFIED', 'NON_EVA', 'EMPTY'
    ]

    print(f"\n{'Category':<25} {'Tokens':>10} {'Types':>10} {'%':>8}")
    print("-" * 55)

    explained = 0
    for cat in category_order:
        tokens = classifications[cat]
        n_tokens = len(tokens)
        n_types = len(set(t[0] for t in tokens))
        pct = n_tokens / total_tokens * 100 if total_tokens > 0 else 0

        if cat not in ['EVA_UNCLASSIFIED', 'NON_EVA']:
            explained += n_tokens

        print(f"{cat:<25} {n_tokens:>10,} {n_types:>10,} {pct:>7.2f}%")

    # Any remaining categories
    for cat in classifications:
        if cat not in category_order:
            tokens = classifications[cat]
            n_tokens = len(tokens)
            n_types = len(set(t[0] for t in tokens))
            pct = n_tokens / total_tokens * 100
            print(f"{cat:<25} {n_tokens:>10,} {n_types:>10,} {pct:>7.2f}%")

    explained_pct = explained / total_tokens * 100 if total_tokens > 0 else 0
    print("-" * 55)
    print(f"{'EXPLAINED':<25} {explained:>10,} {'-':>10} {explained_pct:>7.2f}%")

    # Language breakdown
    print("\n" + "="*70)
    print("BREAKDOWN BY CURRIER LANGUAGE")
    print("="*70)

    for lang in sorted(language_breakdown.keys()):
        print(f"\n{lang}:")
        lang_total = sum(language_breakdown[lang].values())
        for cat in category_order:
            count = language_breakdown[lang][cat]
            if count > 0:
                pct = count / lang_total * 100
                print(f"  {cat:<23} {count:>8,} ({pct:>5.1f}%)")

    # Examine unexplained tokens
    print("\n" + "="*70)
    print("UNEXPLAINED TOKENS (EVA_UNCLASSIFIED + NON_EVA)")
    print("="*70)

    unexplained = classifications['EVA_UNCLASSIFIED'] + classifications['NON_EVA']
    unexplained_tokens = Counter(t[0] for t in unexplained)

    print(f"\nTotal unexplained: {len(unexplained):,} tokens, {len(unexplained_tokens):,} types")

    print("\nMost common unexplained tokens:")
    for token, count in unexplained_tokens.most_common(30):
        # Try to understand why it's unexplained
        cat, details = classify_token(token, canonical_vocab, 'NA')
        print(f"  '{token}': {count} occurrences")

    # Sample unexplained by length
    print("\nUnexplained tokens by length:")
    by_length = defaultdict(list)
    for token in unexplained_tokens:
        by_length[len(token)].append(token)

    for length in sorted(by_length.keys()):
        tokens = by_length[length]
        sample = tokens[:5]
        print(f"  Length {length}: {len(tokens)} types (e.g., {', '.join(sample)})")

    # Check if unexplained tokens have any patterns
    print("\n" + "="*70)
    print("PATTERN ANALYSIS OF UNEXPLAINED")
    print("="*70)

    # What do unexplained tokens start with?
    start_chars = Counter(t[0][0] for t in unexplained if t[0])
    print("\nStarting characters of unexplained:")
    for char, count in start_chars.most_common(15):
        print(f"  '{char}': {count}")

    # What do they end with?
    end_chars = Counter(t[0][-1] for t in unexplained if t[0])
    print("\nEnding characters of unexplained:")
    for char, count in end_chars.most_common(15):
        print(f"  '{char}': {count}")

    # Final verdict
    print("\n" + "="*70)
    print("AUDIT VERDICT")
    print("="*70)

    unexplained_pct = len(unexplained) / total_tokens * 100 if total_tokens > 0 else 0

    print(f"""
Total tokens: {total_tokens:,}
Explained: {explained:,} ({explained_pct:.2f}%)
Unexplained: {len(unexplained):,} ({unexplained_pct:.2f}%)

Classification breakdown:
- B_GRAMMAR: {len(classifications['B_GRAMMAR']):,} tokens (canonical 49-class grammar)
- A_COMPOSITIONAL: {len(classifications['A_COMPOSITIONAL']):,} tokens (prefix+middle+suffix)
- HT_COMPOSITIONAL: {len(classifications['HT_COMPOSITIONAL']):,} tokens (HT prefix + suffix)
- Other explained: {explained - len(classifications['B_GRAMMAR']) - len(classifications['A_COMPOSITIONAL']) - len(classifications['HT_COMPOSITIONAL']):,}
""")

    if unexplained_pct < 1:
        print("VERDICT: EXCELLENT - Less than 1% unexplained")
    elif unexplained_pct < 5:
        print("VERDICT: GOOD - Less than 5% unexplained")
    elif unexplained_pct < 10:
        print("VERDICT: ACCEPTABLE - Less than 10% unexplained")
    else:
        print("VERDICT: NEEDS INVESTIGATION - More than 10% unexplained")

    # Save detailed results
    output = {
        'total_tokens': total_tokens,
        'unique_types': len(unique_tokens),
        'explained': explained,
        'explained_pct': explained_pct,
        'unexplained': len(unexplained),
        'unexplained_pct': unexplained_pct,
        'category_counts': {cat: len(classifications[cat]) for cat in classifications},
        'top_unexplained': unexplained_tokens.most_common(100)
    }

    output_file = BASE / "archive" / "reports" / "full_token_audit.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nDetailed results saved to {output_file}")

if __name__ == '__main__':
    main()
