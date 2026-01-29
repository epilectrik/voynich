"""
15_p_vs_t_comparison.py - What distinguishes p from t?

Both are complete instructions, both distributed throughout folios.
What's the actual difference?
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

def get_role(cls):
    if cls in CC_CLASSES: return 'CC'
    if cls in EN_CLASSES: return 'EN'
    if cls in FL_CLASSES: return 'FL'
    if cls in FQ_CLASSES: return 'FQ'
    return 'AX'

def get_initial_gallows(word):
    if not word:
        return None
    if word[0] in GALLOWS:
        return word[0]
    return None

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load data
    with open(results_dir / 'folio_paragraph_census.json') as f:
        census = json.load(f)

    par_results = Path(__file__).resolve().parents[2] / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    print("=== P vs T COMPARISON ===\n")

    # Collect paragraph data
    p_pars = []
    t_pars = []

    for folio_entry in census['folios']:
        n_pars = len(folio_entry['paragraphs'])
        for i, par_info in enumerate(folio_entry['paragraphs']):
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])

            # Get gallows and first token
            gallows = None
            first_token = None
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    first_token = word
                    gallows = get_initial_gallows(word)
                    break

            if gallows not in ['p', 't']:
                continue

            # Collect paragraph stats
            role_counts = Counter()
            all_words = []
            prefixes = Counter()

            for t in tokens:
                word = t['word']
                if not word or '*' in word:
                    continue
                all_words.append(word)

                if word in class_map:
                    role = get_role(class_map[word])
                    role_counts[role] += 1

                # Count prefixes
                if word.startswith('qo'):
                    prefixes['qo'] += 1
                elif word.startswith('ch'):
                    prefixes['ch'] += 1
                elif word.startswith('sh'):
                    prefixes['sh'] += 1
                elif word.startswith('ok') or word.startswith('ot'):
                    prefixes['ok/ot'] += 1

            total = len(all_words)
            par_data = {
                'par_id': par_id,
                'folio': folio_entry['folio'],
                'ordinal': i + 1,
                'n_pars': n_pars,
                'first_token': first_token,
                'total_tokens': total,
                'roles': dict(role_counts),
                'prefixes': dict(prefixes),
                'unique_words': len(set(all_words)),
                'words': all_words
            }

            if gallows == 'p':
                p_pars.append(par_data)
            else:
                t_pars.append(par_data)

    print(f"p-initial paragraphs: {len(p_pars)}")
    print(f"t-initial paragraphs: {len(t_pars)}\n")

    # === 1. SIZE COMPARISON ===
    print("--- 1. PARAGRAPH SIZE ---\n")

    p_sizes = [p['total_tokens'] for p in p_pars]
    t_sizes = [p['total_tokens'] for p in t_pars]

    print(f"p: mean={statistics.mean(p_sizes):.1f}, median={statistics.median(p_sizes):.0f}, stdev={statistics.stdev(p_sizes):.1f}")
    print(f"t: mean={statistics.mean(t_sizes):.1f}, median={statistics.median(t_sizes):.0f}, stdev={statistics.stdev(t_sizes):.1f}")

    # === 2. ROLE COMPOSITION ===
    print("\n--- 2. ROLE COMPOSITION ---\n")

    def aggregate_roles(pars):
        totals = Counter()
        for p in pars:
            for role, count in p['roles'].items():
                totals[role] += count
        return totals

    p_roles = aggregate_roles(p_pars)
    t_roles = aggregate_roles(t_pars)

    p_total = sum(p_roles.values())
    t_total = sum(t_roles.values())

    print(f"{'Role':<8} {'p':>10} {'t':>10} {'Diff':>10}")
    for role in ['EN', 'FL', 'FQ', 'CC', 'AX']:
        p_pct = p_roles[role] / p_total
        t_pct = t_roles[role] / t_total
        diff = t_pct - p_pct
        print(f"{role:<8} {p_pct:>10.1%} {t_pct:>10.1%} {diff:>+10.1%}")

    # === 3. PREFIX COMPOSITION ===
    print("\n--- 3. PREFIX COMPOSITION (within paragraph) ---\n")

    def aggregate_prefixes(pars):
        totals = Counter()
        token_count = 0
        for p in pars:
            for prefix, count in p['prefixes'].items():
                totals[prefix] += count
            token_count += p['total_tokens']
        return totals, token_count

    p_prefixes, p_tok = aggregate_prefixes(p_pars)
    t_prefixes, t_tok = aggregate_prefixes(t_pars)

    print(f"{'Prefix':<10} {'p':>10} {'t':>10} {'Ratio':>10}")
    for prefix in ['qo', 'ch', 'sh', 'ok/ot']:
        p_rate = p_prefixes[prefix] / p_tok
        t_rate = t_prefixes[prefix] / t_tok
        ratio = t_rate / p_rate if p_rate > 0 else float('inf')
        print(f"{prefix:<10} {p_rate:>10.1%} {t_rate:>10.1%} {ratio:>10.2f}x")

    # === 4. POSITION IN FOLIO ===
    print("\n--- 4. POSITION IN FOLIO ---\n")

    def calc_positions(pars):
        positions = []
        for p in pars:
            if p['n_pars'] > 1:
                rel_pos = (p['ordinal'] - 1) / (p['n_pars'] - 1)
                positions.append(rel_pos)
        return positions

    p_pos = calc_positions(p_pars)
    t_pos = calc_positions(t_pars)

    print(f"p: mean position {statistics.mean(p_pos):.2f}")
    print(f"t: mean position {statistics.mean(t_pos):.2f}")

    # First vs last preference
    p_first = sum(1 for p in p_pars if p['ordinal'] == 1) / len(p_pars)
    t_first = sum(1 for p in t_pars if p['ordinal'] == 1) / len(t_pars)
    p_last = sum(1 for p in p_pars if p['ordinal'] == p['n_pars']) / len(p_pars)
    t_last = sum(1 for p in t_pars if p['ordinal'] == p['n_pars']) / len(t_pars)

    print(f"\np: {p_first:.1%} first, {p_last:.1%} last")
    print(f"t: {t_first:.1%} first, {t_last:.1%} last")

    # === 5. VOCABULARY OVERLAP ===
    print("\n--- 5. VOCABULARY OVERLAP ---\n")

    p_vocab = set()
    t_vocab = set()
    for p in p_pars:
        p_vocab.update(p['words'])
    for p in t_pars:
        t_vocab.update(p['words'])

    overlap = len(p_vocab & t_vocab)
    p_only = len(p_vocab - t_vocab)
    t_only = len(t_vocab - p_vocab)

    print(f"p vocabulary: {len(p_vocab)} unique words")
    print(f"t vocabulary: {len(t_vocab)} unique words")
    print(f"Shared: {overlap} ({overlap/len(p_vocab|t_vocab):.1%})")
    print(f"p-only: {p_only}, t-only: {t_only}")

    # === 6. SECTION DISTRIBUTION ===
    print("\n--- 6. SECTION DISTRIBUTION ---\n")

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

    p_sections = Counter(get_section(p['folio']) for p in p_pars)
    t_sections = Counter(get_section(p['folio']) for p in t_pars)

    print(f"{'Section':<12} {'p':>8} {'t':>8} {'p/t ratio':>10}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        p_count = p_sections[section]
        t_count = t_sections[section]
        ratio = p_count / t_count if t_count > 0 else float('inf')
        print(f"{section:<12} {p_count:>8} {t_count:>8} {ratio:>10.1f}")

    # === 7. FIRST TOKEN MORPHOLOGY ===
    print("\n--- 7. FIRST TOKEN ANALYSIS ---\n")

    p_first_tokens = Counter(p['first_token'] for p in p_pars)
    t_first_tokens = Counter(p['first_token'] for p in t_pars)

    print("Most common p-initial tokens:")
    for tok, count in p_first_tokens.most_common(8):
        print(f"  {tok}: {count}")

    print("\nMost common t-initial tokens:")
    for tok, count in t_first_tokens.most_common(8):
        print(f"  {tok}: {count}")

    # Extract POST element
    def get_post(word):
        if len(word) < 2:
            return '-'
        rest = word[1:]
        for post in ['ch', 'sh', 'o', 'a', 'e']:
            if rest.startswith(post):
                return post
        return '-'

    p_posts = Counter(get_post(p['first_token']) for p in p_pars)
    t_posts = Counter(get_post(p['first_token']) for p in t_pars)

    print(f"\n{'POST':<8} {'p':>10} {'t':>10}")
    for post in ['ch', 'sh', 'o', 'a', 'e', '-']:
        p_pct = p_posts[post] / len(p_pars)
        t_pct = t_posts[post] / len(t_pars)
        print(f"{post:<8} {p_pct:>10.1%} {t_pct:>10.1%}")

    # === 8. WHAT FOLLOWS P vs T? ===
    print("\n--- 8. WHAT FOLLOWS P vs T PARAGRAPHS? ---\n")

    # Build sequence
    folio_sequences = defaultdict(list)
    for folio_entry in census['folios']:
        for par_info in folio_entry['paragraphs']:
            par_id = par_info['par_id']
            tokens = tokens_by_par.get(par_id, [])
            gallows = None
            for t in tokens:
                word = t['word']
                if word and '*' not in word:
                    gallows = get_initial_gallows(word)
                    break
            folio_sequences[folio_entry['folio']].append(gallows)

    # Count what follows p and t
    after_p = Counter()
    after_t = Counter()

    for folio, seq in folio_sequences.items():
        for i in range(len(seq) - 1):
            if seq[i] == 'p':
                after_p[seq[i+1] or 'none'] += 1
            elif seq[i] == 't':
                after_t[seq[i+1] or 'none'] += 1

    print("What follows p-initial paragraph:")
    total_after_p = sum(after_p.values())
    for g, count in after_p.most_common():
        print(f"  {g}: {count} ({count/total_after_p:.1%})")

    print("\nWhat follows t-initial paragraph:")
    total_after_t = sum(after_t.values())
    for g, count in after_t.most_common():
        print(f"  {g}: {count} ({count/total_after_t:.1%})")

    # === VERDICT ===
    print("\n=== VERDICT: P vs T ===\n")

    print("Key differences:")
    print(f"  1. Size: p={statistics.mean(p_sizes):.0f} tokens, t={statistics.mean(t_sizes):.0f} tokens")
    print(f"  2. sh usage: p={p_posts['sh']/len(p_pars):.0%}, t={t_posts['sh']/len(t_pars):.0%}")
    print(f"  3. Self-continuation: p->p={after_p['p']/total_after_p:.0%}, t->t={after_t['t']/total_after_t:.0%}")
    print(f"  4. Cross-transition: p->t={after_p['t']/total_after_p:.0%}, t->p={after_t['p']/total_after_t:.0%}")

if __name__ == '__main__':
    main()
