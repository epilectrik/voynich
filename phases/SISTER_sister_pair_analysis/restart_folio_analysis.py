"""
Restart Folio Analysis: What distinguishes f50v, f57r, f82v?

Questions:
1. What structural properties distinguish restart-capable programs?
2. Why is f57r the ONLY one with explicit reset behavior?
3. Is restart capability a response to brittleness?

Tier 2 investigation - structural comparison.
"""

import json
from collections import defaultdict, Counter
import statistics

def load_currier_b_data():
    """Load Currier B tokens by folio with context."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    folios = defaultdict(list)
    folio_sections = {}
    folio_lines = defaultdict(set)

    with open(filepath, 'r', encoding='latin-1') as f:
        header = None
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            parts = [p.strip('"') for p in parts]

            if header is None:
                header = parts
                continue

            if len(parts) < 14:
                continue

            token = parts[0]
            folio = parts[2]
            section = parts[3]
            currier = parts[6]
            transcriber = parts[12]
            line_num = parts[11]

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                folios[folio].append(token)
                folio_sections[folio] = section
                folio_lines[folio].add(line_num)

    return folios, folio_sections, folio_lines

# Hazard and escape definitions
HAZARD_SOURCES = {'shey', 'chol', 'chedy', 'dy', 'l', 'or', 'chey'}
HAZARD_TARGETS = {'aiin', 'al', 'c', 'r', 'ee', 'dal', 'chol', 'chedy'}
HAZARD_TOKENS = HAZARD_SOURCES | HAZARD_TARGETS

# Kernel primitives
KERNEL_TOKENS = {'s', 'e', 't', 'd', 'l', 'o', 'h', 'c', 'k', 'r'}

def compute_program_profile(tokens):
    """Compute comprehensive profile for a program."""
    if len(tokens) < 10:
        return None

    # Basic counts
    n = len(tokens)
    unique = len(set(tokens))
    ttr = unique / n

    # Hazard metrics
    hazard_count = sum(1 for t in tokens if t in HAZARD_TOKENS)
    hazard_density = hazard_count / n

    # Escape metrics (qo-prefix)
    escape_count = sum(1 for t in tokens if t.startswith('qo'))
    escape_density = escape_count / n

    # Kernel contact
    kernel_contact = sum(1 for t in tokens if any(k in t for k in KERNEL_TOKENS)) / n

    # Sister pair preferences
    ch_count = sum(1 for t in tokens if t.startswith('ch'))
    sh_count = sum(1 for t in tokens if t.startswith('sh'))
    ch_sh_total = ch_count + sh_count
    ch_preference = ch_count / ch_sh_total if ch_sh_total > 0 else 0.5

    ok_count = sum(1 for t in tokens if t.startswith('ok'))
    ot_count = sum(1 for t in tokens if t.startswith('ot'))
    ok_ot_total = ok_count + ot_count
    ok_preference = ok_count / ok_ot_total if ok_ot_total > 0 else 0.5

    # LINK density (daiin, ol)
    link_count = sum(1 for t in tokens if t in {'daiin', 'ol'})
    link_density = link_count / n

    # Max safe run
    max_safe_run = 0
    current_run = 0
    for t in tokens:
        if t in HAZARD_TOKENS:
            max_safe_run = max(max_safe_run, current_run)
            current_run = 0
        else:
            current_run += 1
    max_safe_run = max(max_safe_run, current_run)

    # Forgiveness score
    forgiveness = -hazard_density * 10 + escape_density * 10 + min(max_safe_run, 50) / 50

    # Prefix diversity
    prefixes = Counter()
    for t in tokens:
        for p in ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'al', 'ct']:
            if t.startswith(p):
                prefixes[p] += 1
                break

    prefix_diversity = len([p for p, c in prefixes.items() if c > 0])

    # Token bigram entropy (local predictability)
    bigrams = Counter()
    for i in range(len(tokens) - 1):
        bigrams[(tokens[i], tokens[i+1])] += 1
    bigram_types = len(bigrams)
    bigram_hapax = sum(1 for c in bigrams.values() if c == 1)
    bigram_hapax_rate = bigram_hapax / bigram_types if bigram_types > 0 else 0

    return {
        'token_count': n,
        'unique_tokens': unique,
        'ttr': ttr,
        'hazard_density': hazard_density,
        'escape_density': escape_density,
        'kernel_contact': kernel_contact,
        'ch_preference': ch_preference,
        'ok_preference': ok_preference,
        'link_density': link_density,
        'max_safe_run': max_safe_run,
        'forgiveness': forgiveness,
        'prefix_diversity': prefix_diversity,
        'bigram_hapax_rate': bigram_hapax_rate
    }

def main():
    print("=" * 70)
    print("RESTART FOLIO ANALYSIS")
    print("=" * 70)
    print("\nQuestion: What distinguishes restart-capable programs?")
    print("Restart folios: f50v, f57r, f82v")
    print("f57r is the ONLY one with explicit reset behavior\n")

    # Load data
    folios, sections, lines = load_currier_b_data()
    print(f"Loaded {len(folios)} B folios")

    # Compute profiles for all programs
    profiles = {}
    for folio, tokens in folios.items():
        profile = compute_program_profile(tokens)
        if profile:
            profile['section'] = sections.get(folio, '?')
            profile['line_count'] = len(lines.get(folio, set()))
            profiles[folio] = profile

    print(f"Computed profiles for {len(profiles)} programs\n")

    # Restart folios
    RESTART_FOLIOS = ['f50v', 'f57r', 'f82v']
    restart_profiles = {f: profiles[f] for f in RESTART_FOLIOS if f in profiles}

    # ========================================================================
    # TEST 1: Basic comparison
    # ========================================================================
    print("-" * 70)
    print("TEST 1: Restart Folio Profiles")
    print("-" * 70)

    metrics = ['token_count', 'line_count', 'ttr', 'hazard_density', 'escape_density',
               'link_density', 'ch_preference', 'forgiveness', 'section']

    print(f"\n{'Metric':<20} {'f50v':>12} {'f57r':>12} {'f82v':>12} {'Pop Mean':>12}")
    print("-" * 70)

    for metric in metrics:
        if metric == 'section':
            print(f"{metric:<20} {restart_profiles.get('f50v', {}).get(metric, '?'):>12} "
                  f"{restart_profiles.get('f57r', {}).get(metric, '?'):>12} "
                  f"{restart_profiles.get('f82v', {}).get(metric, '?'):>12} {'(mixed)':>12}")
        else:
            pop_vals = [p[metric] for p in profiles.values() if metric in p]
            pop_mean = statistics.mean(pop_vals) if pop_vals else 0

            vals = []
            for f in RESTART_FOLIOS:
                if f in restart_profiles and metric in restart_profiles[f]:
                    vals.append(f"{restart_profiles[f][metric]:.3f}")
                else:
                    vals.append("N/A")

            print(f"{metric:<20} {vals[0]:>12} {vals[1]:>12} {vals[2]:>12} {pop_mean:>12.3f}")

    # ========================================================================
    # TEST 2: Population comparison
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 2: Restart vs Non-Restart Comparison")
    print("-" * 70)

    non_restart = {f: p for f, p in profiles.items() if f not in RESTART_FOLIOS}

    print(f"\n{'Metric':<20} {'Restart (n=3)':>15} {'Non-Restart':>15} {'Difference':>12}")
    print("-" * 70)

    key_metrics = ['token_count', 'hazard_density', 'escape_density', 'link_density',
                   'ch_preference', 'forgiveness', 'ttr', 'bigram_hapax_rate']

    for metric in key_metrics:
        restart_vals = [restart_profiles[f][metric] for f in RESTART_FOLIOS if f in restart_profiles]
        non_restart_vals = [p[metric] for p in non_restart.values()]

        if restart_vals and non_restart_vals:
            r_mean = statistics.mean(restart_vals)
            nr_mean = statistics.mean(non_restart_vals)
            diff = r_mean - nr_mean
            diff_pct = (diff / nr_mean * 100) if nr_mean != 0 else 0

            print(f"{metric:<20} {r_mean:>15.3f} {nr_mean:>15.3f} {diff_pct:>+11.1f}%")

    # ========================================================================
    # TEST 3: f57r uniqueness (the only reset-present folio)
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 3: f57r Uniqueness Analysis")
    print("-" * 70)

    f57r = restart_profiles.get('f57r', {})
    f50v = restart_profiles.get('f50v', {})
    f82v = restart_profiles.get('f82v', {})

    print("\nf57r is the ONLY folio with explicit reset_present = true")
    print("What makes it different from f50v and f82v?")

    print(f"\n{'Metric':<20} {'f57r':>12} {'f50v':>12} {'f82v':>12} {'f57r vs avg':>12}")
    print("-" * 70)

    for metric in key_metrics:
        if metric in f57r and metric in f50v and metric in f82v:
            avg_other = (f50v[metric] + f82v[metric]) / 2
            diff = f57r[metric] - avg_other
            print(f"{metric:<20} {f57r[metric]:>12.3f} {f50v[metric]:>12.3f} "
                  f"{f82v[metric]:>12.3f} {diff:>+12.3f}")

    # ========================================================================
    # TEST 4: Quartile positions
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 4: Quartile Position Analysis")
    print("-" * 70)

    for metric in ['forgiveness', 'hazard_density', 'escape_density', 'link_density']:
        sorted_folios = sorted(profiles.items(), key=lambda x: x[1][metric])
        n = len(sorted_folios)

        print(f"\n{metric}:")
        for f in RESTART_FOLIOS:
            if f in profiles:
                rank = next(i for i, (fo, _) in enumerate(sorted_folios) if fo == f)
                percentile = rank / n * 100
                quartile = 'Q1' if percentile < 25 else 'Q2' if percentile < 50 else 'Q3' if percentile < 75 else 'Q4'
                print(f"  {f}: rank {rank+1}/{n} ({percentile:.0f}th percentile, {quartile})")

    # ========================================================================
    # TEST 5: Token sequence analysis for f57r
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 5: f57r Token Sequence Around Reset Point")
    print("-" * 70)

    if 'f57r' in folios:
        tokens_57r = folios['f57r']
        print(f"\nf57r has {len(tokens_57r)} tokens")
        print("Known reset point: token 60 (odaiin)")

        # Show tokens around reset
        reset_pos = 60
        print(f"\nTokens 50-70 (reset at position {reset_pos}):")
        for i in range(max(0, 50), min(len(tokens_57r), 71)):
            marker = " <-- RESET" if i == reset_pos else ""
            print(f"  {i:04d}: {tokens_57r[i]}{marker}")

        # Compare pre/post segments
        pre_tokens = tokens_57r[:reset_pos]
        post_tokens = tokens_57r[reset_pos:]

        print(f"\nPre-reset segment: {len(pre_tokens)} tokens")
        print(f"Post-reset segment: {len(post_tokens)} tokens")

        # Prefix distribution comparison
        def get_prefix_dist(tokens):
            prefixes = Counter()
            for t in tokens:
                for p in ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'al']:
                    if t.startswith(p):
                        prefixes[p] += 1
                        break
            total = sum(prefixes.values())
            return {p: c/total if total > 0 else 0 for p, c in prefixes.items()}

        pre_dist = get_prefix_dist(pre_tokens)
        post_dist = get_prefix_dist(post_tokens)

        print(f"\nPrefix distribution comparison:")
        print(f"{'Prefix':<10} {'Pre-reset':>12} {'Post-reset':>12} {'Change':>12}")
        print("-" * 50)
        all_prefixes = set(pre_dist.keys()) | set(post_dist.keys())
        for p in sorted(all_prefixes):
            pre = pre_dist.get(p, 0)
            post = post_dist.get(p, 0)
            change = post - pre
            print(f"{p:<10} {pre*100:>11.1f}% {post*100:>11.1f}% {change*100:>+11.1f}%")

    # ========================================================================
    # TEST 6: Shared properties
    # ========================================================================
    print("\n" + "-" * 70)
    print("TEST 6: What Do All 3 Restart Folios Share?")
    print("-" * 70)

    # Find properties where all 3 are in same direction vs population
    pop_means = {m: statistics.mean([p[m] for p in profiles.values()]) for m in key_metrics}

    print("\nProperties where ALL 3 restart folios differ from population mean:")
    print(f"{'Metric':<20} {'Direction':>15} {'Magnitude':>15}")
    print("-" * 55)

    for metric in key_metrics:
        r_vals = [restart_profiles[f][metric] for f in RESTART_FOLIOS if f in restart_profiles]
        if len(r_vals) == 3:
            pop_mean = pop_means[metric]
            above = sum(1 for v in r_vals if v > pop_mean)
            below = sum(1 for v in r_vals if v < pop_mean)

            if above == 3:
                avg_diff = statistics.mean(r_vals) - pop_mean
                print(f"{metric:<20} {'ALL ABOVE':>15} {avg_diff:>+15.3f}")
            elif below == 3:
                avg_diff = statistics.mean(r_vals) - pop_mean
                print(f"{metric:<20} {'ALL BELOW':>15} {avg_diff:>+15.3f}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    restart_forg = statistics.mean([restart_profiles[f]['forgiveness'] for f in RESTART_FOLIOS])
    pop_forg = statistics.mean([p['forgiveness'] for p in profiles.values()])

    restart_esc = statistics.mean([restart_profiles[f]['escape_density'] for f in RESTART_FOLIOS])
    pop_esc = statistics.mean([p['escape_density'] for p in profiles.values()])

    restart_link = statistics.mean([restart_profiles[f]['link_density'] for f in RESTART_FOLIOS])
    pop_link = statistics.mean([p['link_density'] for p in profiles.values()])

    print(f"""
    Restart programs (n=3) vs Population (n={len(profiles)}):

    Forgiveness:    {restart_forg:.3f} vs {pop_forg:.3f} ({(restart_forg-pop_forg)/pop_forg*100:+.1f}%)
    Escape density: {restart_esc:.3f} vs {pop_esc:.3f} ({(restart_esc-pop_esc)/pop_esc*100:+.1f}%)
    LINK density:   {restart_link:.3f} vs {pop_link:.3f} ({(restart_link-pop_link)/pop_link*100:+.1f}%)

    f57r (reset-present) is in forgiveness Q1 (BRITTLE)
    f82v is in forgiveness Q4 (FORGIVING)
    f50v is in forgiveness Q3 (moderate)

    """)

    # Save results
    results = {
        'restart_folios': RESTART_FOLIOS,
        'restart_profiles': {f: restart_profiles[f] for f in RESTART_FOLIOS if f in restart_profiles},
        'population_means': pop_means,
        'n_programs': len(profiles)
    }

    with open('restart_folio_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results saved to restart_folio_analysis_results.json")

if __name__ == '__main__':
    main()
