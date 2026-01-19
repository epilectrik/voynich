"""
PHARMA-LABEL-VALIDATION: Confirm f99r Label Token Roles

Tests whether the jar/root labels identified on f99r have properties
that confirm their role as specialized labels vs regular text vocabulary.
"""
import json
import re
import csv
from collections import Counter
from pathlib import Path


def load_f99r_labels():
    """Load the manually mapped f99r labels."""
    with open('phases/PHARMA_LABEL_DECODING/f99r_jar_root_mapping.json', 'r') as f:
        data = json.load(f)

    jars = []
    roots = []
    for group in data['groups']:
        jars.append(group['jar'])
        for root in group['roots']:
            if isinstance(root, dict):
                roots.append(root['token'])
            else:
                roots.append(root)

    return jars, roots


def load_zl_transcription():
    """Parse ZL transcription to separate labels from text."""
    labels = []  # @L entries
    text_tokens = []  # @P0 entries

    with open('data/transcriptions/reference/ZL_official.txt', 'r', encoding='utf-8') as f:
        for line in f:
            # Match label lines: <f99r.1,@Lc> or <f99r.1,+Lf>
            label_match = re.match(r'<(f\d+[rv]\d*)\.\d+,[@+]L[cf]>\s+(.+)', line)
            if label_match:
                content = label_match.group(2)
                # Clean up
                content = re.sub(r'<![^>]*>', '', content)  # Remove comments
                content = re.sub(r'\[[^\]]*\]', '', content)  # Remove brackets
                content = content.replace(',', '').strip()
                if content and not content.startswith('#'):
                    labels.append(content.lower())
                continue

            # Match text lines: <f99r.15,@P0> or <f99r.16,+P0>
            text_match = re.match(r'<(f\d+[rv]\d*)\.\d+,[@+]P0>\s+(.+)', line)
            if text_match:
                content = text_match.group(2)
                # Clean up
                content = re.sub(r'<![^>]*>', '', content)
                content = re.sub(r'<%>', '', content)
                content = re.sub(r'<\$>', '', content)
                content = re.sub(r'<->', ' ', content)
                content = re.sub(r'\{[^}]*\}', '', content)
                content = re.sub(r'\[[^\]]*\]', '', content)
                # Split into tokens
                for token in content.replace('.', ' ').replace(',', ' ').split():
                    token = token.strip().lower()
                    if token and not token.startswith('#'):
                        text_tokens.append(token)

    return labels, text_tokens


def load_full_vocab():
    """Load full vocabulary from interlinear transcript (H-only)."""
    a_vocab = Counter()
    b_vocab = Counter()

    with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # skip header
        for row in reader:
            if len(row) < 13:
                continue
            transcriber = row[12].strip('"').strip()
            lang = row[6].strip('"').strip()
            word = row[0].strip('"').strip().lower()

            if transcriber == 'H':
                if lang == 'A':
                    a_vocab[word] += 1
                elif lang == 'B':
                    b_vocab[word] += 1

    return a_vocab, b_vocab


def load_pharma_labels_by_folio():
    """Load all @L entries from pharma folios."""
    pharma_folios = {}  # folio -> list of labels

    with open('data/transcriptions/reference/ZL_official.txt', 'r', encoding='utf-8') as f:
        for line in f:
            label_match = re.match(r'<(f\d+[rv]\d*)\.\d+,[@+]L[cf]>\s+(.+)', line)
            if label_match:
                folio = label_match.group(1)
                content = label_match.group(2)
                content = re.sub(r'<![^>]*>', '', content)
                content = re.sub(r'\[[^\]]*\]', '', content)
                content = content.replace(',', '').strip().lower()
                if content and not content.startswith('#'):
                    if folio not in pharma_folios:
                        pharma_folios[folio] = []
                    pharma_folios[folio].append(content)

    return pharma_folios


def test1_label_vs_text_isolation(f99r_labels, zl_labels, zl_text):
    """TEST 1: Do label tokens appear in regular text?"""
    print("=" * 60)
    print("TEST 1: Label vs Text Isolation")
    print("=" * 60)

    # All labels from f99r
    f99r_all = set([l.lower() for l in f99r_labels])

    # All text tokens
    text_set = set(zl_text)

    # All labels from ZL
    label_set = set(zl_labels)

    # Check overlap
    overlap = f99r_all & text_set
    isolation_rate = 1 - len(overlap) / len(f99r_all) if f99r_all else 0

    print(f"f99r labels: {len(f99r_all)}")
    print(f"ZL text tokens (unique): {len(text_set)}")
    print(f"Overlap (f99r labels in text): {len(overlap)}")
    print(f"Isolation rate: {isolation_rate:.1%}")
    print()

    if overlap:
        print("Labels that ALSO appear in text:")
        for token in sorted(overlap):
            text_count = zl_text.count(token)
            print(f"  {token}: {text_count} occurrences in text")

    isolated = f99r_all - text_set
    print(f"\nLabels that are ISOLATED (not in text): {len(isolated)}")

    result = {
        'f99r_label_count': len(f99r_all),
        'text_vocab_size': len(text_set),
        'overlap_count': len(overlap),
        'overlap_tokens': list(overlap),
        'isolation_rate': isolation_rate,
        'isolated_tokens': list(isolated),
        'pass': isolation_rate > 0.80
    }

    print(f"\nPASS: {result['pass']} (threshold: >80% isolation)")
    return result


def test2_a_vs_b_distribution(f99r_labels, a_vocab, b_vocab):
    """TEST 2: Are these label tokens A-exclusive?"""
    print("\n" + "=" * 60)
    print("TEST 2: A vs B Distribution")
    print("=" * 60)

    a_only = []
    b_only = []
    shared = []
    neither = []

    for label in f99r_labels:
        label = label.lower()
        in_a = label in a_vocab
        in_b = label in b_vocab

        if in_a and in_b:
            shared.append(label)
        elif in_a:
            a_only.append(label)
        elif in_b:
            b_only.append(label)
        else:
            neither.append(label)

    total = len(f99r_labels)
    print(f"Total f99r labels: {total}")
    print(f"A-only: {len(a_only)} ({100*len(a_only)/total:.1f}%)")
    print(f"B-only: {len(b_only)} ({100*len(b_only)/total:.1f}%)")
    print(f"Shared A+B: {len(shared)} ({100*len(shared)/total:.1f}%)")
    print(f"Neither (hapax in labels): {len(neither)} ({100*len(neither)/total:.1f}%)")

    if shared:
        print("\nShared tokens (appear in both A and B):")
        for token in shared:
            print(f"  {token}: A={a_vocab[token]}, B={b_vocab[token]}")

    if b_only:
        print("\nB-only tokens (RED FLAG):")
        for token in b_only:
            print(f"  {token}: B={b_vocab[token]}")

    # A-biased means mostly A-only or A+neither
    a_biased_rate = (len(a_only) + len(neither)) / total if total else 0

    result = {
        'a_only': a_only,
        'b_only': b_only,
        'shared': shared,
        'neither': neither,
        'a_only_count': len(a_only),
        'b_only_count': len(b_only),
        'shared_count': len(shared),
        'neither_count': len(neither),
        'a_biased_rate': a_biased_rate,
        'pass': len(b_only) == 0 and a_biased_rate > 0.70
    }

    print(f"\nA-biased rate: {a_biased_rate:.1%}")
    print(f"PASS: {result['pass']} (no B-only, >70% A-biased)")
    return result


def test3_frequency_profile(f99r_labels, a_vocab, b_vocab):
    """TEST 3: Are label tokens rare?"""
    print("\n" + "=" * 60)
    print("TEST 3: Frequency Profile")
    print("=" * 60)

    full_vocab = Counter()
    full_vocab.update(a_vocab)
    full_vocab.update(b_vocab)

    # Sort by frequency for ranking
    sorted_vocab = sorted(full_vocab.items(), key=lambda x: -x[1])
    rank_map = {word: i+1 for i, (word, _) in enumerate(sorted_vocab)}

    freq_data = []
    for label in f99r_labels:
        label = label.lower()
        freq = full_vocab.get(label, 0)
        rank = rank_map.get(label, len(sorted_vocab) + 1)
        freq_data.append({
            'token': label,
            'frequency': freq,
            'rank': rank
        })

    # Count hapax/rare
    hapax = sum(1 for d in freq_data if d['frequency'] <= 1)
    rare = sum(1 for d in freq_data if d['frequency'] <= 5)
    common = sum(1 for d in freq_data if d['frequency'] > 20)

    total = len(freq_data)
    print(f"Frequency distribution of f99r labels:")
    print(f"  Hapax (<=1): {hapax} ({100*hapax/total:.1f}%)")
    print(f"  Rare (<=5): {rare} ({100*rare/total:.1f}%)")
    print(f"  Common (>20): {common} ({100*common/total:.1f}%)")

    print("\nTop 10 most frequent labels:")
    for d in sorted(freq_data, key=lambda x: -x['frequency'])[:10]:
        print(f"  {d['token']}: freq={d['frequency']}, rank={d['rank']}")

    print("\nLabels NOT found in corpus (label-only):")
    not_found = [d for d in freq_data if d['frequency'] == 0]
    for d in not_found[:10]:
        print(f"  {d['token']}")
    if len(not_found) > 10:
        print(f"  ... and {len(not_found) - 10} more")

    rare_rate = rare / total if total else 0

    result = {
        'hapax_count': hapax,
        'rare_count': rare,
        'common_count': common,
        'rare_rate': rare_rate,
        'freq_data': freq_data,
        'pass': rare_rate > 0.50
    }

    print(f"\nRare rate: {rare_rate:.1%}")
    print(f"PASS: {result['pass']} (threshold: >50% rare)")
    return result


def test4_jar_vs_root_differentiation(jars, roots):
    """TEST 4: Do jars differ from roots?"""
    print("\n" + "=" * 60)
    print("TEST 4: Jar vs Root Differentiation")
    print("=" * 60)

    jar_lengths = [len(j) for j in jars]
    root_lengths = [len(r) for r in roots]

    jar_avg = sum(jar_lengths) / len(jar_lengths) if jar_lengths else 0
    root_avg = sum(root_lengths) / len(root_lengths) if root_lengths else 0

    print(f"Jar labels ({len(jars)}): {jars}")
    print(f"Jar avg length: {jar_avg:.1f}")
    print()
    print(f"Root labels ({len(roots)}): {len(roots)} tokens")
    print(f"Root avg length: {root_avg:.1f}")
    print()
    print(f"Length difference: jars are {jar_avg - root_avg:.1f} chars longer on average")

    # Check for common prefixes
    def get_prefix(token, length=2):
        return token[:length] if len(token) >= length else token

    jar_prefixes = Counter([get_prefix(j) for j in jars])
    root_prefixes = Counter([get_prefix(r) for r in roots])

    print(f"\nJar prefixes (2-char): {dict(jar_prefixes)}")
    print(f"Root prefixes (2-char): {dict(root_prefixes.most_common(10))}")

    result = {
        'jar_count': len(jars),
        'root_count': len(roots),
        'jar_avg_length': jar_avg,
        'root_avg_length': root_avg,
        'length_diff': jar_avg - root_avg,
        'jar_prefixes': dict(jar_prefixes),
        'root_prefixes': dict(root_prefixes),
        'pass': jar_avg > root_avg  # Jars should be longer/more complex
    }

    print(f"\nPASS: {result['pass']} (jars longer than roots)")
    return result


def test5_cross_folio_reuse(f99r_labels, pharma_labels_by_folio):
    """TEST 5: Do labels repeat across folios?"""
    print("\n" + "=" * 60)
    print("TEST 5: Cross-Folio Reuse")
    print("=" * 60)

    f99r_set = set([l.lower() for l in f99r_labels])

    reuse_count = Counter()
    for label in f99r_set:
        for folio, labels in pharma_labels_by_folio.items():
            if folio != 'f99r' and label in [l.lower() for l in labels]:
                reuse_count[label] += 1

    reused = len([l for l in f99r_set if reuse_count[l] > 0])
    unique = len(f99r_set) - reused

    print(f"f99r labels: {len(f99r_set)}")
    print(f"Unique to f99r: {unique} ({100*unique/len(f99r_set):.1f}%)")
    print(f"Reused on other folios: {reused} ({100*reused/len(f99r_set):.1f}%)")

    if reuse_count:
        print("\nLabels reused on other folios:")
        for label, count in reuse_count.most_common(10):
            folios = [f for f, labels in pharma_labels_by_folio.items()
                     if f != 'f99r' and label in [l.lower() for l in labels]]
            print(f"  {label}: {count} other folios ({', '.join(folios[:3])})")

    unique_rate = unique / len(f99r_set) if f99r_set else 0

    result = {
        'unique_count': unique,
        'reused_count': reused,
        'unique_rate': unique_rate,
        'reuse_details': dict(reuse_count),
        'pass': unique_rate > 0.70
    }

    print(f"\nUnique rate: {unique_rate:.1%}")
    print(f"PASS: {result['pass']} (threshold: >70% unique)")
    return result


def main():
    print("PHARMA-LABEL-VALIDATION: Testing f99r Label Token Properties")
    print("=" * 60)
    print()

    # Load data
    print("Loading data...")
    jars, roots = load_f99r_labels()
    f99r_labels = jars + roots
    print(f"  f99r: {len(jars)} jars, {len(roots)} roots = {len(f99r_labels)} total")

    zl_labels, zl_text = load_zl_transcription()
    print(f"  ZL: {len(zl_labels)} labels, {len(zl_text)} text tokens")

    a_vocab, b_vocab = load_full_vocab()
    print(f"  Vocab: {len(a_vocab)} A types, {len(b_vocab)} B types")

    pharma_labels = load_pharma_labels_by_folio()
    print(f"  Pharma folios with labels: {len(pharma_labels)}")
    print()

    # Run tests
    results = {}
    results['test1'] = test1_label_vs_text_isolation(f99r_labels, zl_labels, zl_text)
    results['test2'] = test2_a_vs_b_distribution(f99r_labels, a_vocab, b_vocab)
    results['test3'] = test3_frequency_profile(f99r_labels, a_vocab, b_vocab)
    results['test4'] = test4_jar_vs_root_differentiation(jars, roots)
    results['test5'] = test5_cross_folio_reuse(f99r_labels, pharma_labels)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    tests_passed = sum(1 for r in results.values() if r['pass'])
    print(f"\nTests passed: {tests_passed}/5")
    print()
    for name, r in results.items():
        status = "PASS" if r['pass'] else "FAIL"
        print(f"  {name}: {status}")

    if tests_passed >= 4:
        print("\nVERDICT: CONFIRMED - These tokens behave like specialized labels")
    elif tests_passed >= 2:
        print("\nVERDICT: MIXED - Some label-like properties, needs investigation")
    else:
        print("\nVERDICT: REJECTED - These tokens behave like regular vocabulary")

    # Save results
    results['summary'] = {
        'tests_passed': tests_passed,
        'verdict': 'CONFIRMED' if tests_passed >= 4 else 'MIXED' if tests_passed >= 2 else 'REJECTED'
    }

    with open('results/pharma_label_validation.json', 'w') as f:
        # Clean up non-serializable data
        clean_results = {}
        for k, v in results.items():
            clean_results[k] = {kk: vv for kk, vv in v.items()
                              if not isinstance(vv, list) or len(vv) < 100}
        json.dump(clean_results, f, indent=2)

    print("\nResults saved to results/pharma_label_validation.json")


if __name__ == '__main__':
    main()
