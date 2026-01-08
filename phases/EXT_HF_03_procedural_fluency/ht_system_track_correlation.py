"""
HT-System Track Correlation Analysis

Question: Can human-track patterns help differentiate system-track processes?

If HT represents attention-occupation during waiting, HT characteristics
might serve as a "human sensor" revealing operational differences.

Tests:
1. HT density vs LINK density (waiting correlation)
2. HT vocabulary diversity vs section operational complexity
3. HT rare bigram profile vs operational bigram profile
4. Section-level correlation matrix
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats as sp_stats

project_root = Path(__file__).parent.parent.parent

# Token classification (same as other analyses)
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

# LINK tokens (waiting operators)
LINK_TOKENS = {'ol', 'or', 'ar', 'al', 'ain', 'aiin'}


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


def is_link_token(token):
    return token.lower().strip() in LINK_TOKENS


def is_executable(token):
    t = token.lower().strip()
    if len(t) < 2:
        return False
    if not t.isalpha():
        return False
    return is_grammar_token(t) or t in OPERATIONAL_TOKENS


def get_bigrams(token):
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
                word = parts[0].strip('"').strip()
                folio = parts[1].strip('"') if len(parts) > 1 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                if word and section:
                    data.append({
                        'token': word.lower(),
                        'folio': folio,
                        'section': section
                    })
    return data


def main():
    print("=" * 70)
    print("HT-SYSTEM TRACK CORRELATION ANALYSIS")
    print("=" * 70)
    print("\nQuestion: Can HT patterns help differentiate system-track processes?")

    data = load_data()
    print(f"\nLoaded {len(data)} tokens")

    # Aggregate by section
    section_stats = defaultdict(lambda: {
        'total': 0,
        'ht_count': 0,
        'link_count': 0,
        'exec_count': 0,
        'ht_tokens': [],
        'exec_tokens': [],
        'ht_unique': set(),
        'exec_unique': set(),
    })

    for d in data:
        token = d['token']
        section = d['section']

        section_stats[section]['total'] += 1

        if is_human_track_strict(token):
            section_stats[section]['ht_count'] += 1
            section_stats[section]['ht_tokens'].append(token)
            section_stats[section]['ht_unique'].add(token)

        if is_link_token(token):
            section_stats[section]['link_count'] += 1

        if is_executable(token):
            section_stats[section]['exec_count'] += 1
            section_stats[section]['exec_tokens'].append(token)
            section_stats[section]['exec_unique'].add(token)

    # Calculate derived metrics
    sections = sorted(section_stats.keys())

    print("\n" + "=" * 70)
    print("SECTION-LEVEL METRICS")
    print("=" * 70)

    print(f"\n{'Section':<8} {'Total':<8} {'HT%':<8} {'LINK%':<8} {'HT_div':<8} {'Exec_div':<8}")
    print("-" * 48)

    metrics = {}
    for s in sections:
        stats = section_stats[s]
        ht_pct = 100 * stats['ht_count'] / stats['total'] if stats['total'] > 0 else 0
        link_pct = 100 * stats['link_count'] / stats['total'] if stats['total'] > 0 else 0
        ht_diversity = len(stats['ht_unique']) / stats['ht_count'] if stats['ht_count'] > 0 else 0
        exec_diversity = len(stats['exec_unique']) / stats['exec_count'] if stats['exec_count'] > 0 else 0

        metrics[s] = {
            'ht_pct': ht_pct,
            'link_pct': link_pct,
            'ht_diversity': ht_diversity,
            'exec_diversity': exec_diversity,
            'ht_count': stats['ht_count'],
            'exec_count': stats['exec_count'],
        }

        print(f"{s:<8} {stats['total']:<8} {ht_pct:<8.1f} {link_pct:<8.1f} {ht_diversity:<8.3f} {exec_diversity:<8.3f}")

    # Test 1: HT density vs LINK density
    print("\n" + "=" * 70)
    print("TEST 1: HT Density vs LINK Density Correlation")
    print("=" * 70)

    ht_pcts = [metrics[s]['ht_pct'] for s in sections]
    link_pcts = [metrics[s]['link_pct'] for s in sections]

    r_ht_link, p_ht_link = sp_stats.pearsonr(ht_pcts, link_pcts)
    rho_ht_link, p_rho = sp_stats.spearmanr(ht_pcts, link_pcts)

    print(f"\nPearson r: {r_ht_link:.3f} (p={p_ht_link:.4f})")
    print(f"Spearman rho: {rho_ht_link:.3f} (p={p_rho:.4f})")

    if abs(r_ht_link) > 0.5:
        print("\n** STRONG CORRELATION ** HT density tracks LINK density")
        print("   Implication: HT practice occurs during operational waiting")
    elif abs(r_ht_link) > 0.3:
        print("\n** MODERATE CORRELATION ** HT partially tracks LINK")
    else:
        print("\n** WEAK/NO CORRELATION ** HT independent of LINK density")

    # Test 2: HT diversity vs Exec diversity
    print("\n" + "=" * 70)
    print("TEST 2: HT Vocabulary Diversity vs Exec Diversity")
    print("=" * 70)

    ht_divs = [metrics[s]['ht_diversity'] for s in sections]
    exec_divs = [metrics[s]['exec_diversity'] for s in sections]

    r_div, p_div = sp_stats.pearsonr(ht_divs, exec_divs)

    print(f"\nPearson r: {r_div:.3f} (p={p_div:.4f})")

    if abs(r_div) > 0.5:
        print("\n** CORRELATED ** More diverse exec sections have more diverse HT")
        print("   Implication: HT complexity mirrors operational complexity")
    else:
        print("\n** NOT CORRELATED ** HT diversity independent of exec diversity")

    # Test 3: Bigram profile similarity per section
    print("\n" + "=" * 70)
    print("TEST 3: HT vs Exec Bigram Profile Similarity by Section")
    print("=" * 70)

    print(f"\n{'Section':<8} {'Jaccard':<10} {'Shared%':<10} {'HT_only':<10} {'Exec_only':<10}")
    print("-" * 48)

    jaccard_values = []
    for s in sections:
        ht_bigrams = set()
        exec_bigrams = set()

        for token in section_stats[s]['ht_tokens']:
            ht_bigrams.update(get_bigrams(token))
        for token in section_stats[s]['exec_tokens']:
            exec_bigrams.update(get_bigrams(token))

        if len(ht_bigrams) > 0 and len(exec_bigrams) > 0:
            intersection = len(ht_bigrams & exec_bigrams)
            union = len(ht_bigrams | exec_bigrams)
            jaccard = intersection / union
            shared_pct = 100 * intersection / len(ht_bigrams)
            ht_only = len(ht_bigrams - exec_bigrams)
            exec_only = len(exec_bigrams - ht_bigrams)

            jaccard_values.append(jaccard)
            print(f"{s:<8} {jaccard:<10.3f} {shared_pct:<10.1f} {ht_only:<10} {exec_only:<10}")

    mean_jaccard = np.mean(jaccard_values)
    print(f"\nMean Jaccard (HT vs Exec bigrams): {mean_jaccard:.3f}")

    if mean_jaccard > 0.6:
        print("** HIGH OVERLAP ** HT bigram usage similar to Exec")
    elif mean_jaccard > 0.3:
        print("** MODERATE OVERLAP ** HT explores beyond Exec but within system")
    else:
        print("** LOW OVERLAP ** HT bigrams quite distinct from Exec")

    # Test 4: Can HT profile predict section identity?
    print("\n" + "=" * 70)
    print("TEST 4: Section Discrimination via HT Patterns")
    print("=" * 70)

    # Calculate section pairwise distances based on HT bigram profiles
    section_ht_bigram_freqs = {}
    all_bigrams = set()

    for s in sections:
        bg_counts = Counter()
        for token in section_stats[s]['ht_tokens']:
            for bg in get_bigrams(token):
                bg_counts[bg] += 1
        section_ht_bigram_freqs[s] = bg_counts
        all_bigrams.update(bg_counts.keys())

    # Normalize to frequency vectors
    all_bigrams = sorted(all_bigrams)

    print(f"\nUnique HT bigrams across sections: {len(all_bigrams)}")

    # Calculate cosine similarity between sections (HT profiles)
    def cosine_sim(v1, v2):
        dot = sum(a*b for a,b in zip(v1, v2))
        norm1 = sum(a*a for a in v1) ** 0.5
        norm2 = sum(b*b for b in v2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)

    section_vectors = {}
    for s in sections:
        total = sum(section_ht_bigram_freqs[s].values())
        if total > 0:
            vec = [section_ht_bigram_freqs[s].get(bg, 0) / total for bg in all_bigrams]
        else:
            vec = [0] * len(all_bigrams)
        section_vectors[s] = vec

    print(f"\nCosine similarity matrix (HT bigram profiles):")
    print(f"\n{'':8}", end="")
    for s in sections:
        print(f"{s:>8}", end="")
    print()

    similarities = []
    for s1 in sections:
        print(f"{s1:8}", end="")
        for s2 in sections:
            sim = cosine_sim(section_vectors[s1], section_vectors[s2])
            print(f"{sim:8.3f}", end="")
            if s1 < s2:
                similarities.append(sim)
        print()

    mean_sim = np.mean(similarities)
    print(f"\nMean off-diagonal similarity: {mean_sim:.3f}")

    if mean_sim < 0.5:
        print("** SECTIONS DISTINGUISHABLE ** HT profiles differentiate sections")
        print("   Implication: HT patterns can serve as section signatures")
    else:
        print("** SECTIONS SIMILAR ** HT profiles don't strongly differentiate")

    # Summary
    print("\n" + "=" * 70)
    print("SYNTHESIS: CAN HT DIFFERENTIATE SYSTEM-TRACK PROCESSES?")
    print("=" * 70)

    print(f"""
Test Results:
1. HT-LINK correlation: r={r_ht_link:.3f}
2. HT-Exec diversity correlation: r={r_div:.3f}
3. HT-Exec bigram overlap: Jaccard={mean_jaccard:.3f}
4. Section distinguishability via HT: mean_sim={mean_sim:.3f}

Key Question: Does HT provide signal about system-track processes?
""")

    signals = 0
    if abs(r_ht_link) > 0.3:
        signals += 1
        print("+ HT density tracks operational waiting (LINK)")
    if abs(r_div) > 0.3:
        signals += 1
        print("+ HT complexity mirrors operational complexity")
    if mean_jaccard < 0.5:
        signals += 1
        print("+ HT explores beyond operational patterns")
    if mean_sim < 0.5:
        signals += 1
        print("+ HT profiles can differentiate sections")

    print(f"\nSignals detected: {signals}/4")

    if signals >= 3:
        print("\n** VERDICT: YES ** HT layer provides useful signal about system track")
        print("   HT serves as 'human sensor' revealing operational differences")
    elif signals >= 2:
        print("\n** VERDICT: PARTIAL ** HT provides some differentiation signal")
    else:
        print("\n** VERDICT: LIMITED ** HT does not strongly differentiate processes")


if __name__ == '__main__':
    main()
