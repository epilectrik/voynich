"""
12_gallows_qo_ch_correlation.py - Does gallows correlate with qo/ch pattern?

Questions:
1. Do p-initial paragraphs favor qo or ch?
2. Does gallows type predict EN subfamily?
3. Is the early-late pattern gallows-dependent?
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

GALLOWS = {'t', 'k', 'p', 'f'}

# EN classes
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}

def get_initial_gallows(word):
    """Get gallows if word starts with one."""
    if not word:
        return None
    if word[0] in GALLOWS:
        return word[0]
    return None

def get_en_subfamily(word):
    """Classify EN token as QO or CHSH based on prefix."""
    if not word:
        return None
    if word.startswith('qo'):
        return 'QO'
    elif word.startswith('ch') or word.startswith('sh'):
        return 'CHSH'
    return 'OTHER'

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load census
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    # Load paragraph tokens
    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    print("=== GALLOWS vs QO/CH CORRELATION ===\n")

    # Collect data per paragraph
    par_data = []

    for folio_entry in census['folios']:
        for i, par_info in enumerate(folio_entry['paragraphs']):
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            # Get gallows from first token
            gallows = None
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    gallows = get_initial_gallows(word)
                    break

            # Count EN subfamilies in paragraph
            qo_count = 0
            chsh_count = 0
            other_en = 0

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue
                if word in class_map and class_map[word] in EN_CLASSES:
                    subfamily = get_en_subfamily(word)
                    if subfamily == 'QO':
                        qo_count += 1
                    elif subfamily == 'CHSH':
                        chsh_count += 1
                    else:
                        other_en += 1

            total_en = qo_count + chsh_count + other_en
            ordinal = min(i + 1, 6)

            par_data.append({
                'par_id': par_id,
                'folio': folio_entry['folio'],
                'ordinal': ordinal,
                'gallows': gallows,
                'qo_count': qo_count,
                'chsh_count': chsh_count,
                'total_en': total_en,
                'qo_rate': qo_count / total_en if total_en > 0 else 0,
                'chsh_rate': chsh_count / total_en if total_en > 0 else 0
            })

    # === 1. QO/CH RATES BY GALLOWS ===
    print("--- 1. QO/CHSH RATES BY GALLOWS TYPE ---\n")

    gallows_stats = defaultdict(lambda: {'qo': 0, 'chsh': 0, 'total': 0, 'pars': 0})

    for p in par_data:
        if p['gallows']:
            g = p['gallows']
            gallows_stats[g]['qo'] += p['qo_count']
            gallows_stats[g]['chsh'] += p['chsh_count']
            gallows_stats[g]['total'] += p['total_en']
            gallows_stats[g]['pars'] += 1

    print(f"{'Gallows':<10} {'QO Rate':>10} {'CHSH Rate':>10} {'QO/CHSH':>10} {'Paragraphs':>12}")
    for g in ['p', 't', 'k', 'f']:
        stats = gallows_stats[g]
        if stats['total'] > 0:
            qo_rate = stats['qo'] / stats['total']
            chsh_rate = stats['chsh'] / stats['total']
            ratio = stats['qo'] / stats['chsh'] if stats['chsh'] > 0 else float('inf')
            print(f"{g:<10} {qo_rate:>10.1%} {chsh_rate:>10.1%} {ratio:>10.2f} {stats['pars']:>12}")

    # === 2. GALLOWS × ORDINAL INTERACTION ===
    print("\n--- 2. QO RATE BY GALLOWS × ORDINAL ---\n")

    gallows_ordinal = defaultdict(lambda: defaultdict(lambda: {'qo': 0, 'total': 0}))

    for p in par_data:
        if p['gallows'] and p['total_en'] > 0:
            gallows_ordinal[p['gallows']][p['ordinal']]['qo'] += p['qo_count']
            gallows_ordinal[p['gallows']][p['ordinal']]['total'] += p['total_en']

    print(f"{'Gallows':<8}", end='')
    for ord in range(1, 7):
        print(f" {'Ord '+str(ord):>8}", end='')
    print()

    for g in ['p', 't', 'k', 'f']:
        print(f"{g:<8}", end='')
        for ord in range(1, 7):
            stats = gallows_ordinal[g][ord]
            if stats['total'] > 5:
                qo_rate = stats['qo'] / stats['total']
                print(f" {qo_rate:>8.1%}", end='')
            else:
                print(f" {'--':>8}", end='')
        print()

    # === 3. EARLY vs LATE BY GALLOWS ===
    print("\n--- 3. EARLY vs LATE QO RATE BY GALLOWS ---\n")

    early_late = defaultdict(lambda: {'early_qo': 0, 'early_total': 0, 'late_qo': 0, 'late_total': 0})

    for p in par_data:
        if p['gallows'] and p['total_en'] > 0:
            g = p['gallows']
            if p['ordinal'] <= 2:
                early_late[g]['early_qo'] += p['qo_count']
                early_late[g]['early_total'] += p['total_en']
            elif p['ordinal'] >= 5:
                early_late[g]['late_qo'] += p['qo_count']
                early_late[g]['late_total'] += p['total_en']

    print(f"{'Gallows':<10} {'Early QO':>10} {'Late QO':>10} {'Shift':>10}")
    for g in ['p', 't', 'k', 'f']:
        stats = early_late[g]
        if stats['early_total'] > 10 and stats['late_total'] > 10:
            early_rate = stats['early_qo'] / stats['early_total']
            late_rate = stats['late_qo'] / stats['late_total']
            shift = early_rate - late_rate
            print(f"{g:<10} {early_rate:>10.1%} {late_rate:>10.1%} {shift:>+10.1%}")
        else:
            print(f"{g:<10} {'insufficient data':>30}")

    # === 4. DOES GALLOWS PREDICT QO/CHSH BETTER THAN ORDINAL? ===
    print("\n--- 4. VARIANCE DECOMPOSITION ---\n")

    # Calculate variance explained by gallows vs ordinal
    import statistics

    # Get QO rates for paragraphs with enough EN tokens
    valid_pars = [p for p in par_data if p['total_en'] >= 5 and p['gallows']]

    if len(valid_pars) > 10:
        qo_rates = [p['qo_rate'] for p in valid_pars]
        overall_mean = statistics.mean(qo_rates)
        total_var = statistics.variance(qo_rates)

        # Variance by gallows
        gallows_means = {}
        for g in GALLOWS:
            g_rates = [p['qo_rate'] for p in valid_pars if p['gallows'] == g]
            if len(g_rates) >= 3:
                gallows_means[g] = statistics.mean(g_rates)

        # Between-group variance (gallows)
        if gallows_means:
            gallows_var = sum(
                len([p for p in valid_pars if p['gallows'] == g]) * (gallows_means[g] - overall_mean)**2
                for g in gallows_means
            ) / len(valid_pars)

        # Variance by ordinal
        ordinal_means = {}
        for o in range(1, 7):
            o_rates = [p['qo_rate'] for p in valid_pars if p['ordinal'] == o]
            if len(o_rates) >= 3:
                ordinal_means[o] = statistics.mean(o_rates)

        # Between-group variance (ordinal)
        if ordinal_means:
            ordinal_var = sum(
                len([p for p in valid_pars if p['ordinal'] == o]) * (ordinal_means[o] - overall_mean)**2
                for o in ordinal_means
            ) / len(valid_pars)

        print(f"Total QO rate variance: {total_var:.4f}")
        print(f"Variance explained by GALLOWS: {gallows_var:.4f} ({gallows_var/total_var:.1%})")
        print(f"Variance explained by ORDINAL: {ordinal_var:.4f} ({ordinal_var/total_var:.1%})")

        if gallows_var > ordinal_var:
            print("\n→ GALLOWS explains more variance than ORDINAL")
        else:
            print("\n→ ORDINAL explains more variance than GALLOWS")

    # === 5. GALLOWS-SPECIFIC EN TOKENS ===
    print("\n--- 5. CHARACTERISTIC EN TOKENS BY GALLOWS ---\n")

    en_by_gallows = defaultdict(Counter)

    for p in par_data:
        if not p['gallows']:
            continue
        g = p['gallows']
        tokens = tokens_by_par.get(p['par_id'], [])
        for t in tokens:
            word = t['word']
            if word and '*' not in word and word in class_map:
                if class_map[word] in EN_CLASSES:
                    en_by_gallows[g][word] += 1

    for g in ['p', 't', 'k', 'f']:
        print(f"Most common EN in '{g}'-initial paragraphs:")
        for token, count in en_by_gallows[g].most_common(8):
            subfamily = get_en_subfamily(token)
            print(f"  {token:15} ({subfamily}): {count}")
        print()

    # === VERDICT ===
    print("=== VERDICT ===\n")

    # Check if different gallows have different QO/CHSH profiles
    p_ratio = gallows_stats['p']['qo'] / gallows_stats['p']['chsh'] if gallows_stats['p']['chsh'] > 0 else 0
    t_ratio = gallows_stats['t']['qo'] / gallows_stats['t']['chsh'] if gallows_stats['t']['chsh'] > 0 else 0
    k_ratio = gallows_stats['k']['qo'] / gallows_stats['k']['chsh'] if gallows_stats['k']['chsh'] > 0 else 0

    print(f"QO/CHSH ratios: p={p_ratio:.2f}, t={t_ratio:.2f}, k={k_ratio:.2f}")

    if abs(p_ratio - t_ratio) > 0.2 or abs(p_ratio - k_ratio) > 0.2:
        print("→ GALLOWS DOES correlate with QO/CHSH preference")
    else:
        print("→ GALLOWS does NOT strongly correlate with QO/CHSH")

    # Save results
    output = {
        'gallows_stats': {g: dict(v) for g, v in gallows_stats.items()},
        'early_late': {g: dict(v) for g, v in early_late.items()},
        'en_by_gallows': {g: dict(v.most_common(20)) for g, v in en_by_gallows.items()}
    }

    with open(results_dir / 'gallows_qo_ch_correlation.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to gallows_qo_ch_correlation.json")

if __name__ == '__main__':
    main()
