"""
Phase CURRIER_A_ATOMS — Script 1: Atom-level baseline statistics for Currier A
Compares A vs B across all atom dimensions.
"""
import sys
import os
import json
from collections import Counter, defaultdict
from statistics import mean, median

# Windows stdout fix
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Run from repo root
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()


def valid_word(w):
    return w and w.strip() and '*' not in w


def atomize_corpus(tokens):
    """Atomize all valid tokens, return list of (word, folio, AtomAnalysis)."""
    results = []
    for tok in tokens:
        w = tok.word
        if not valid_word(w):
            continue
        a = morph.atomize(w)
        results.append((w, tok.folio, a))
    return results


def compute_stats(corpus, label):
    """Compute all stats for a corpus of (word, folio, AtomAnalysis) tuples."""
    head_counts = Counter()
    mod_counts = Counter()
    term_counts = Counter()
    e_depths = []
    atom_lengths = []
    opacity_counts = Counter()
    prefix_counts = Counter()
    articulator_count = 0
    total = len(corpus)

    for word, folio, a in corpus:
        # HEAD
        head = a.head
        if head:
            head_counts[head] += 1
        elif a.is_headless:
            head_counts['HEADLESS'] += 1
        else:
            head_counts['NONE'] += 1

        # MODs
        for ch, role, _ in a.atoms:
            if role == 'MOD':
                mod_counts[ch] += 1

        # TERM
        t = a.term
        if t:
            term_counts[t] += 1
        else:
            term_counts['NONE'] += 1

        # e_depth
        e_depths.append(a.e_depth)

        # atom length
        atom_lengths.append(len(a.atoms))

        # opacity
        opacity_counts[a.terminal_opacity] += 1

        # prefix
        prefix_counts[a.prefix if a.prefix else 'NONE'] += 1

        # articulator
        if a.articulator:
            articulator_count += 1

    stats = {
        'label': label,
        'total_tokens': total,
        'head_dist': dict(head_counts.most_common()),
        'mod_dist': dict(mod_counts.most_common()),
        'term_dist': dict(term_counts.most_common()),
        'e_depth_mean': round(mean(e_depths), 3) if e_depths else 0,
        'e_depth_median': median(e_depths) if e_depths else 0,
        'e_depth_dist': {
            '0': sum(1 for d in e_depths if d == 0),
            '1': sum(1 for d in e_depths if d == 1),
            '2': sum(1 for d in e_depths if d == 2),
            '3+': sum(1 for d in e_depths if d >= 3),
        },
        'atom_len_mean': round(mean(atom_lengths), 3) if atom_lengths else 0,
        'atom_len_median': median(atom_lengths) if atom_lengths else 0,
        'atom_len_dist': dict(Counter(atom_lengths).most_common()),
        'opacity_dist': dict(opacity_counts.most_common()),
        'prefix_dist': dict(prefix_counts.most_common()),
        'articulator_rate': round(articulator_count / total, 4) if total else 0,
        'articulator_count': articulator_count,
    }
    return stats


def print_comparison(a_stats, b_stats, title, key, top_n=None):
    """Print side-by-side comparison table."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

    a_dist = a_stats[key]
    b_dist = b_stats[key]
    all_keys = sorted(set(list(a_dist.keys()) + list(b_dist.keys())),
                      key=lambda k: -(a_dist.get(k, 0) + b_dist.get(k, 0)))
    if top_n:
        all_keys = all_keys[:top_n]

    a_total = a_stats['total_tokens']
    b_total = b_stats['total_tokens']

    print(f"{'Item':<20} {'A count':>8} {'A %':>8} {'B count':>8} {'B %':>8} {'A/B ratio':>10}")
    print(f"{'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")
    for k in all_keys:
        ac = a_dist.get(k, 0)
        bc = b_dist.get(k, 0)
        ap = ac / a_total * 100 if a_total else 0
        bp = bc / b_total * 100 if b_total else 0
        ratio = f"{ap/bp:.2f}" if bp > 0 else "inf"
        print(f"{str(k):<20} {ac:>8} {ap:>7.2f}% {bc:>8} {bp:>7.2f}% {ratio:>10}")


def main():
    print("Loading Currier A tokens...")
    a_tokens = atomize_corpus(tx.currier_a())
    print(f"  Valid A tokens: {len(a_tokens)}")

    print("Loading Currier B tokens...")
    b_tokens = atomize_corpus(tx.currier_b())
    print(f"  Valid B tokens: {len(b_tokens)}")

    a_stats = compute_stats(a_tokens, 'Currier_A')
    b_stats = compute_stats(b_tokens, 'Currier_B')

    # 1. HEAD distribution
    print_comparison(a_stats, b_stats, "1. HEAD DISTRIBUTION", 'head_dist')

    # 2. MOD distribution
    print_comparison(a_stats, b_stats, "2. MOD DISTRIBUTION", 'mod_dist')

    # 3. TERM distribution
    print_comparison(a_stats, b_stats, "3. TERM DISTRIBUTION", 'term_dist')

    # 4. e_depth
    print(f"\n{'='*70}")
    print(f"  4. e_depth COMPARISON")
    print(f"{'='*70}")
    print(f"{'Metric':<25} {'Currier A':>12} {'Currier B':>12}")
    print(f"{'-'*25} {'-'*12} {'-'*12}")
    print(f"{'Mean':<25} {a_stats['e_depth_mean']:>12.3f} {b_stats['e_depth_mean']:>12.3f}")
    print(f"{'Median':<25} {a_stats['e_depth_median']:>12} {b_stats['e_depth_median']:>12}")
    for k in ['0', '1', '2', '3+']:
        ac = a_stats['e_depth_dist'][k]
        bc = b_stats['e_depth_dist'][k]
        ap = ac / a_stats['total_tokens'] * 100
        bp = bc / b_stats['total_tokens'] * 100
        print(f"{'depth=' + k:<25} {ac:>8} ({ap:>5.1f}%) {bc:>8} ({bp:>5.1f}%)")

    # 5. Token length (atom count)
    print(f"\n{'='*70}")
    print(f"  5. TOKEN LENGTH (atom count)")
    print(f"{'='*70}")
    print(f"{'Metric':<25} {'Currier A':>12} {'Currier B':>12}")
    print(f"{'-'*25} {'-'*12} {'-'*12}")
    print(f"{'Mean':<25} {a_stats['atom_len_mean']:>12.3f} {b_stats['atom_len_mean']:>12.3f}")
    print(f"{'Median':<25} {a_stats['atom_len_median']:>12} {b_stats['atom_len_median']:>12}")
    print_comparison(a_stats, b_stats, "  Token length distribution", 'atom_len_dist', top_n=10)

    # 6. Terminal opacity
    print_comparison(a_stats, b_stats, "6. TERMINAL OPACITY", 'opacity_dist')

    # 7. PREFIX distribution
    print_comparison(a_stats, b_stats, "7. PREFIX DISTRIBUTION", 'prefix_dist', top_n=20)

    # 8. Articulator rate
    print(f"\n{'='*70}")
    print(f"  8. ARTICULATOR RATE")
    print(f"{'='*70}")
    print(f"{'Metric':<25} {'Currier A':>12} {'Currier B':>12}")
    print(f"{'-'*25} {'-'*12} {'-'*12}")
    print(f"{'With articulator':<25} {a_stats['articulator_count']:>12} {b_stats['articulator_count']:>12}")
    print(f"{'Rate':<25} {a_stats['articulator_rate']:>11.4f} {b_stats['articulator_rate']:>11.4f}")

    # 9. Per-folio HEAD profiles for A
    print(f"\n{'='*70}")
    print(f"  9. PER-FOLIO HEAD PROFILES (Currier A)")
    print(f"{'='*70}")
    folio_heads = defaultdict(Counter)
    folio_totals = Counter()
    for word, folio, a in a_tokens:
        folio_totals[folio] += 1
        head = a.head
        if head:
            folio_heads[folio][head] += 1
        elif a.is_headless:
            folio_heads[folio]['HEADLESS'] += 1
        else:
            folio_heads[folio]['NONE'] += 1

    head_keys = ['o', 'k', 'a', 'e', 't', 'HEADLESS', 'NONE']
    print(f"{'Folio':<12} {'N':>5}", end='')
    for h in head_keys:
        print(f" {h:>8}", end='')
    print()
    print(f"{'-'*12} {'-'*5}", end='')
    for _ in head_keys:
        print(f" {'-'*8}", end='')
    print()

    for folio in sorted(folio_totals.keys()):
        n = folio_totals[folio]
        print(f"{folio:<12} {n:>5}", end='')
        for h in head_keys:
            c = folio_heads[folio].get(h, 0)
            pct = c / n * 100 if n else 0
            print(f" {pct:>7.1f}%", end='')
        print()

    # 10. Top 20 most common words in A with glosses
    print(f"\n{'='*70}")
    print(f"  10. TOP 20 MOST COMMON WORDS (Currier A)")
    print(f"{'='*70}")
    word_counts = Counter()
    word_gloss = {}
    for word, folio, a in a_tokens:
        word_counts[word] += 1
        if word not in word_gloss:
            word_gloss[word] = a.gloss

    print(f"{'Rank':<5} {'Word':<20} {'Count':>6} {'Gloss'}")
    print(f"{'-'*5} {'-'*20} {'-'*6} {'-'*40}")
    for i, (word, count) in enumerate(word_counts.most_common(20), 1):
        print(f"{i:<5} {word:<20} {count:>6} {word_gloss[word]}")

    # 11. Headless token analysis
    print(f"\n{'='*70}")
    print(f"  11. HEADLESS TOKEN ANALYSIS (Currier A)")
    print(f"{'='*70}")
    headless_words = Counter()
    headless_middles = Counter()
    for word, folio, a in a_tokens:
        if a.is_headless:
            headless_words[word] += 1
            # Get the MIDDLE from extract
            m = morph.extract(word)
            if m.middle:
                headless_middles[m.middle] += 1

    print(f"\nTotal headless tokens: {sum(headless_words.values())}")
    print(f"Unique headless words: {len(headless_words)}")
    print(f"\nTop 20 headless words:")
    print(f"{'Word':<20} {'Count':>6}")
    print(f"{'-'*20} {'-'*6}")
    for word, count in headless_words.most_common(20):
        print(f"{word:<20} {count:>6}")

    print(f"\nTop 15 headless MIDDLEs:")
    print(f"{'MIDDLE':<20} {'Count':>6}")
    print(f"{'-'*20} {'-'*6}")
    for mid, count in headless_middles.most_common(15):
        print(f"{mid:<20} {count:>6}")

    # Save JSON
    output = {
        'currier_a': a_stats,
        'currier_b': b_stats,
        'per_folio_head_profiles_a': {
            folio: {h: folio_heads[folio].get(h, 0) for h in head_keys}
            for folio in sorted(folio_totals.keys())
        },
        'top20_words_a': [
            {'word': w, 'count': c, 'gloss': word_gloss[w]}
            for w, c in word_counts.most_common(20)
        ],
        'headless_top20_a': [
            {'word': w, 'count': c} for w, c in headless_words.most_common(20)
        ],
        'headless_middles_top15_a': [
            {'middle': m, 'count': c} for m, c in headless_middles.most_common(15)
        ],
    }

    out_path = 'phases/CURRIER_A_ATOMS/results/s1_a_baseline.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
