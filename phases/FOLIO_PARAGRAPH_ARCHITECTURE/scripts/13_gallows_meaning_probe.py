"""
13_gallows_meaning_probe.py - What does gallows actually mark?

If not QO/CHSH, then what? Check:
1. Role composition (EN/FL/FQ/CC rates)
2. Paragraph size/complexity
3. MIDDLE vocabulary
4. Position patterns
5. Folio-level patterns
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

GALLOWS = {'t', 'k', 'p', 'f'}

# Role classes
CC_CLASSES = {10, 11, 12, 17}
EN_CLASSES = {8, 31, 32, 33, 34, 35, 36, 37, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49}
FL_CLASSES = {7, 30, 38, 40}
FQ_CLASSES = {9, 13, 14, 23}
LINK_CLASS = 29

def get_role(cls):
    if cls in CC_CLASSES: return 'CC'
    if cls in EN_CLASSES: return 'EN'
    if cls in FL_CLASSES: return 'FL'
    if cls in FQ_CLASSES: return 'FQ'
    if cls == LINK_CLASS: return 'LINK'
    return 'AX'

def get_initial_gallows(word):
    if not word:
        return None
    if word[0] in GALLOWS:
        return word[0]
    return None

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

    print("=== WHAT DOES GALLOWS MARK? ===\n")

    # Collect paragraph data
    par_data = []

    for folio_entry in census['folios']:
        n_pars = len(folio_entry['paragraphs'])
        for i, par_info in enumerate(folio_entry['paragraphs']):
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            # Get gallows
            gallows = None
            first_token = None
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    first_token = word
                    gallows = get_initial_gallows(word)
                    break

            # Count roles
            role_counts = Counter()
            total_tokens = 0
            middles = set()

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue
                total_tokens += 1

                if word in class_map:
                    role = get_role(class_map[word])
                    role_counts[role] += 1
                else:
                    role_counts['HT'] += 1

                # Extract middle (simple: remove first 2 chars if gallows+post)
                if len(word) > 2:
                    middles.add(word[2:])

            par_data.append({
                'par_id': par_id,
                'folio': folio_entry['folio'],
                'gallows': gallows,
                'first_token': first_token,
                'total_tokens': total_tokens,
                'roles': dict(role_counts),
                'n_pars_in_folio': n_pars,
                'ordinal': i + 1,
                'middles': middles
            })

    # === 1. ROLE COMPOSITION BY GALLOWS ===
    print("--- 1. ROLE COMPOSITION BY GALLOWS ---\n")

    role_by_gallows = defaultdict(lambda: defaultdict(int))
    total_by_gallows = defaultdict(int)

    for p in par_data:
        if p['gallows']:
            g = p['gallows']
            for role, count in p['roles'].items():
                role_by_gallows[g][role] += count
                total_by_gallows[g] += count

    print(f"{'Gallows':<8} {'EN':>8} {'FL':>8} {'FQ':>8} {'CC':>8} {'LINK':>8} {'HT':>8}")
    for g in ['p', 't', 'k', 'f']:
        total = total_by_gallows[g]
        if total > 0:
            row = f"{g:<8}"
            for role in ['EN', 'FL', 'FQ', 'CC', 'LINK', 'HT']:
                pct = role_by_gallows[g][role] / total
                row += f" {pct:>7.1%}"
            print(row)

    # === 2. PARAGRAPH SIZE BY GALLOWS ===
    print("\n--- 2. PARAGRAPH SIZE BY GALLOWS ---\n")

    sizes_by_gallows = defaultdict(list)
    for p in par_data:
        if p['gallows']:
            sizes_by_gallows[p['gallows']].append(p['total_tokens'])

    print(f"{'Gallows':<8} {'Mean':>8} {'Median':>8} {'StdDev':>8} {'N':>8}")
    for g in ['p', 't', 'k', 'f']:
        sizes = sizes_by_gallows[g]
        if len(sizes) > 1:
            mean = statistics.mean(sizes)
            median = statistics.median(sizes)
            stdev = statistics.stdev(sizes)
            print(f"{g:<8} {mean:>8.1f} {median:>8.1f} {stdev:>8.1f} {len(sizes):>8}")

    # === 3. FOLIO POSITION BY GALLOWS ===
    print("\n--- 3. WHERE IN FOLIO DOES EACH GALLOWS APPEAR? ---\n")

    # Relative position (0=first, 1=last)
    rel_positions = defaultdict(list)
    for p in par_data:
        if p['gallows'] and p['n_pars_in_folio'] > 1:
            rel_pos = (p['ordinal'] - 1) / (p['n_pars_in_folio'] - 1)
            rel_positions[p['gallows']].append(rel_pos)

    print(f"{'Gallows':<8} {'Mean Pos':>10} {'Front(<0.3)':>12} {'Back(>0.7)':>12}")
    for g in ['p', 't', 'k', 'f']:
        positions = rel_positions[g]
        if positions:
            mean_pos = statistics.mean(positions)
            front = sum(1 for p in positions if p < 0.3) / len(positions)
            back = sum(1 for p in positions if p > 0.7) / len(positions)
            print(f"{g:<8} {mean_pos:>10.2f} {front:>12.1%} {back:>12.1%}")

    # === 4. FOLIO GALLOWS PROFILES ===
    print("\n--- 4. FOLIO GALLOWS PROFILES ---\n")

    # What's the dominant gallows per folio?
    folio_gallows = defaultdict(Counter)
    for p in par_data:
        if p['gallows']:
            folio_gallows[p['folio']][p['gallows']] += 1

    # Count folio profiles
    profile_counts = Counter()
    for folio, counts in folio_gallows.items():
        if counts:
            dominant = counts.most_common(1)[0][0]
            total = sum(counts.values())
            dominant_pct = counts[dominant] / total
            if dominant_pct >= 0.8:
                profile = f"{dominant}-mono"
            elif dominant_pct >= 0.5:
                profile = f"{dominant}-dominant"
            else:
                profile = "mixed"
            profile_counts[profile] += 1

    print("Folio gallows profiles:")
    for profile, count in profile_counts.most_common():
        print(f"  {profile}: {count} folios")

    # === 5. GALLOWS-SPECIFIC VOCABULARY ===
    print("\n--- 5. FIRST TOKEN VOCABULARY OVERLAP ---\n")

    # Get unique first tokens by gallows
    first_tokens_by_g = defaultdict(set)
    for p in par_data:
        if p['gallows'] and p['first_token']:
            first_tokens_by_g[p['gallows']].add(p['first_token'])

    # Calculate overlap (should be 0 since gallows is first char)
    print("First token sets by gallows:")
    for g in ['p', 't', 'k', 'f']:
        tokens = first_tokens_by_g[g]
        print(f"  {g}: {len(tokens)} unique tokens")

    # Check if MIDDLE portions overlap
    print("\nMIDDLE overlap (stripping gallows+post):")
    middle_by_g = defaultdict(set)
    for p in par_data:
        if p['gallows']:
            for m in p['middles']:
                middle_by_g[p['gallows']].add(m)

    # Pairwise overlap
    pairs = [('p', 't'), ('p', 'k'), ('p', 'f'), ('t', 'k'), ('t', 'f'), ('k', 'f')]
    for g1, g2 in pairs:
        m1, m2 = middle_by_g[g1], middle_by_g[g2]
        if m1 and m2:
            overlap = len(m1 & m2)
            jaccard = overlap / len(m1 | m2)
            print(f"  {g1}-{g2}: Jaccard={jaccard:.2f} ({overlap} shared)")

    # === 6. GALLOWS AND HT DENSITY ===
    print("\n--- 6. HT (HUMAN TRACK) DENSITY BY GALLOWS ---\n")

    ht_rates = defaultdict(list)
    for p in par_data:
        if p['gallows'] and p['total_tokens'] > 0:
            ht_rate = p['roles'].get('HT', 0) / p['total_tokens']
            ht_rates[p['gallows']].append(ht_rate)

    print(f"{'Gallows':<8} {'Mean HT':>10} {'StdDev':>10}")
    for g in ['p', 't', 'k', 'f']:
        rates = ht_rates[g]
        if len(rates) > 1:
            print(f"{g:<8} {statistics.mean(rates):>10.1%} {statistics.stdev(rates):>10.1%}")

    # === 7. LINK OPERATOR DENSITY ===
    print("\n--- 7. LINK OPERATOR DENSITY BY GALLOWS ---\n")

    link_rates = defaultdict(list)
    for p in par_data:
        if p['gallows'] and p['total_tokens'] > 0:
            link_rate = p['roles'].get('LINK', 0) / p['total_tokens']
            link_rates[p['gallows']].append(link_rate)

    print(f"{'Gallows':<8} {'Mean LINK':>10} {'Has LINK':>10}")
    for g in ['p', 't', 'k', 'f']:
        rates = link_rates[g]
        if rates:
            mean_rate = statistics.mean(rates)
            has_link = sum(1 for r in rates if r > 0) / len(rates)
            print(f"{g:<8} {mean_rate:>10.1%} {has_link:>10.1%}")

    # === 8. SECTION BREAKDOWN (detailed) ===
    print("\n--- 8. GALLOWS BY SECTION (detailed) ---\n")

    def get_section(folio):
        num = int(''.join(c for c in folio if c.isdigit()))
        if 74 <= num <= 84:
            return 'BIO'
        elif 26 <= num <= 56:
            return 'HERBAL_B'
        elif 57 <= num <= 67:
            return 'PHARMA'
        elif num >= 103:
            return 'RECIPE_B'
        else:
            return 'OTHER'

    section_gallows = defaultdict(Counter)
    for p in par_data:
        if p['gallows']:
            section = get_section(p['folio'])
            section_gallows[section][p['gallows']] += 1

    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        counts = section_gallows[section]
        total = sum(counts.values())
        print(f"{section}:")
        for g in ['p', 't', 'k', 'f']:
            if counts[g] > 0:
                print(f"  {g}: {counts[g]:3} ({counts[g]/total:.1%})")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    # Check what differs most by gallows
    print("What differs by gallows type:")

    # Role composition - calculate variance
    role_variances = {}
    for role in ['EN', 'FL', 'FQ', 'CC', 'LINK', 'HT']:
        rates = []
        for g in ['p', 't', 'k', 'f']:
            total = total_by_gallows[g]
            if total > 0:
                rates.append(role_by_gallows[g][role] / total)
        if len(rates) > 1:
            role_variances[role] = statistics.variance(rates)

    print("\nRole composition variance across gallows types:")
    for role, var in sorted(role_variances.items(), key=lambda x: x[1], reverse=True):
        print(f"  {role}: {var:.6f}")

    # Size variance
    size_means = [statistics.mean(sizes_by_gallows[g]) for g in ['p', 't', 'k', 'f'] if sizes_by_gallows[g]]
    print(f"\nParagraph size means: {[f'{m:.1f}' for m in size_means]}")
    print(f"Size variance: {statistics.variance(size_means):.2f}")

    # Position variance
    pos_means = [statistics.mean(rel_positions[g]) for g in ['p', 't', 'k', 'f'] if rel_positions[g]]
    print(f"Position means: {[f'{m:.2f}' for m in pos_means]}")
    print(f"Position variance: {statistics.variance(pos_means):.4f}")

    print("\n" + "="*50)
    print("GALLOWS appears to mark: ???")
    print("="*50)

if __name__ == '__main__':
    main()
