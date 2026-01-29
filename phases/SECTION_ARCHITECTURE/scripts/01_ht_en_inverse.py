"""
01_ht_en_inverse.py - Probe the HT-EN inverse relationship

PHARMA: 40% HT, 27% EN
BIO: 22% HT, 40% EN

Is this:
A) Structural compensation (HT fills EN gaps)
B) Different program types (identification vs execution)
C) Folio-level variation within sections
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

def get_section(folio):
    """Classify folio into section."""
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

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load class map
    class_map_path = Path(__file__).resolve().parents[3] / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(class_map_path) as f:
        raw_map = json.load(f)
    class_map = raw_map.get('token_to_class', raw_map)

    # Load B paragraph tokens
    par_results = Path(__file__).resolve().parents[3] / 'phases' / 'PARAGRAPH_INTERNAL_PROFILING' / 'results'
    with open(par_results / 'b_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Load paragraph inventory
    with open(par_results / 'b_paragraph_inventory.json') as f:
        inventory = json.load(f)

    par_to_info = {p['par_id']: p for p in inventory['paragraphs']}

    # Role mapping
    EN_CLASSES = {8} | set(range(31, 38)) | {39} | set(range(41, 50))

    print("=== HT-EN INVERSE RELATIONSHIP ===\n")

    # === 1. FOLIO-LEVEL HT vs EN ===
    print("--- 1. FOLIO-LEVEL HT vs EN CORRELATION ---\n")

    folio_stats = defaultdict(lambda: {'tokens': 0, 'ht': 0, 'en': 0})

    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue

            folio_stats[folio]['tokens'] += 1

            if word in class_map:
                cls = class_map[word]
                if cls in EN_CLASSES:
                    folio_stats[folio]['en'] += 1
            else:
                folio_stats[folio]['ht'] += 1

    # Calculate rates
    folio_rates = []
    for folio, stats in folio_stats.items():
        if stats['tokens'] >= 50:  # Minimum threshold
            ht_rate = stats['ht'] / stats['tokens']
            en_rate = stats['en'] / stats['tokens']
            section = get_section(folio)
            folio_rates.append((folio, section, ht_rate, en_rate, stats['tokens']))

    # Correlation
    ht_rates = [x[2] for x in folio_rates]
    en_rates = [x[3] for x in folio_rates]

    # Spearman correlation
    from scipy.stats import spearmanr
    try:
        rho, p_value = spearmanr(ht_rates, en_rates)
        print(f"HT-EN Spearman correlation: rho={rho:.3f}, p={p_value:.2e}")
    except:
        # Calculate manually if scipy not available
        n = len(ht_rates)
        rank_ht = [sorted(ht_rates).index(x) + 1 for x in ht_rates]
        rank_en = [sorted(en_rates).index(x) + 1 for x in en_rates]
        d_sq = sum((rh - re)**2 for rh, re in zip(rank_ht, rank_en))
        rho = 1 - (6 * d_sq) / (n * (n**2 - 1))
        print(f"HT-EN Spearman correlation: rho={rho:.3f}")

    # Show extremes
    print("\nHighest HT folios:")
    for folio, section, ht, en, n in sorted(folio_rates, key=lambda x: x[2], reverse=True)[:5]:
        print(f"  {folio} ({section}): HT={ht:.1%}, EN={en:.1%}, n={n}")

    print("\nLowest HT folios:")
    for folio, section, ht, en, n in sorted(folio_rates, key=lambda x: x[2])[:5]:
        print(f"  {folio} ({section}): HT={ht:.1%}, EN={en:.1%}, n={n}")

    # === 2. WITHIN-SECTION VARIATION ===
    print("\n--- 2. WITHIN-SECTION HT-EN VARIATION ---\n")

    section_folios = defaultdict(list)
    for folio, section, ht, en, n in folio_rates:
        section_folios[section].append((folio, ht, en))

    print(f"{'Section':<12} {'N':>4} {'HT mean':>10} {'HT std':>10} {'EN mean':>10} {'EN std':>10}")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        folios = section_folios[section]
        if len(folios) >= 2:
            hts = [x[1] for x in folios]
            ens = [x[2] for x in folios]
            print(f"{section:<12} {len(folios):>4} {statistics.mean(hts):>10.1%} {statistics.stdev(hts):>10.1%} {statistics.mean(ens):>10.1%} {statistics.stdev(ens):>10.1%}")
        else:
            hts = [x[1] for x in folios]
            ens = [x[2] for x in folios]
            print(f"{section:<12} {len(folios):>4} {statistics.mean(hts):>10.1%} {'N/A':>10} {statistics.mean(ens):>10.1%} {'N/A':>10}")

    # === 3. PARAGRAPH-LEVEL ANALYSIS ===
    print("\n--- 3. PARAGRAPH-LEVEL HT vs EN ---\n")

    par_profiles = []
    for par_id, tokens in tokens_by_par.items():
        par_info = par_to_info.get(par_id, {})
        folio = par_info.get('folio', 'unknown')
        section = get_section(folio)

        total = 0
        ht = 0
        en = 0

        for t in tokens:
            word = t['word']
            if not word or '*' in word:
                continue
            total += 1
            if word in class_map:
                cls = class_map[word]
                if cls in EN_CLASSES:
                    en += 1
            else:
                ht += 1

        if total >= 5:
            par_profiles.append({
                'par_id': par_id,
                'section': section,
                'folio': folio,
                'tokens': total,
                'ht_rate': ht / total,
                'en_rate': en / total
            })

    # Paragraph-level correlation
    par_ht = [p['ht_rate'] for p in par_profiles]
    par_en = [p['en_rate'] for p in par_profiles]
    try:
        rho_par, p_par = spearmanr(par_ht, par_en)
        print(f"Paragraph-level HT-EN correlation: rho={rho_par:.3f}, p={p_par:.2e}")
    except:
        pass

    # By section
    print("\nParagraph-level correlation by section:")
    for section in ['BIO', 'HERBAL_B', 'PHARMA', 'RECIPE_B']:
        sec_pars = [p for p in par_profiles if p['section'] == section]
        if len(sec_pars) >= 10:
            sec_ht = [p['ht_rate'] for p in sec_pars]
            sec_en = [p['en_rate'] for p in sec_pars]
            try:
                rho_sec, p_sec = spearmanr(sec_ht, sec_en)
                print(f"  {section}: rho={rho_sec:.3f}, p={p_sec:.2e}, n={len(sec_pars)}")
            except:
                pass

    # === 4. WHAT REPLACES EN IN HIGH-HT PARAGRAPHS? ===
    print("\n--- 4. ROLE COMPOSITION BY HT LEVEL ---\n")

    # Bin paragraphs by HT rate
    low_ht = [p for p in par_profiles if p['ht_rate'] < 0.25]
    med_ht = [p for p in par_profiles if 0.25 <= p['ht_rate'] < 0.40]
    high_ht = [p for p in par_profiles if p['ht_rate'] >= 0.40]

    # Calculate role profiles for each bin
    CC_CLASSES = {10, 11, 12, 17}
    FQ_CLASSES = {9, 13, 14, 23}
    FL_CLASSES = {7, 30, 38, 40}
    AX_CLASSES = {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}

    def get_role_profile(par_ids):
        roles = Counter()
        total = 0
        for par_id in par_ids:
            for t in tokens_by_par.get(par_id, []):
                word = t['word']
                if not word or '*' in word:
                    continue
                total += 1
                if word in class_map:
                    cls = class_map[word]
                    if cls in EN_CLASSES:
                        roles['EN'] += 1
                    elif cls in CC_CLASSES:
                        roles['CC'] += 1
                    elif cls in FQ_CLASSES:
                        roles['FQ'] += 1
                    elif cls in FL_CLASSES:
                        roles['FL'] += 1
                    elif cls in AX_CLASSES:
                        roles['AX'] += 1
                else:
                    roles['HT'] += 1
        return {r: c/total for r, c in roles.items()} if total > 0 else {}

    low_profile = get_role_profile([p['par_id'] for p in low_ht])
    med_profile = get_role_profile([p['par_id'] for p in med_ht])
    high_profile = get_role_profile([p['par_id'] for p in high_ht])

    print(f"{'HT Level':<12} {'n':>6} {'HT':>8} {'EN':>8} {'AX':>8} {'FQ':>8} {'CC':>8} {'FL':>8}")
    print(f"{'Low (<25%)':<12} {len(low_ht):>6} {low_profile.get('HT',0):>8.1%} {low_profile.get('EN',0):>8.1%} {low_profile.get('AX',0):>8.1%} {low_profile.get('FQ',0):>8.1%} {low_profile.get('CC',0):>8.1%} {low_profile.get('FL',0):>8.1%}")
    print(f"{'Med (25-40%)':<12} {len(med_ht):>6} {med_profile.get('HT',0):>8.1%} {med_profile.get('EN',0):>8.1%} {med_profile.get('AX',0):>8.1%} {med_profile.get('FQ',0):>8.1%} {med_profile.get('CC',0):>8.1%} {med_profile.get('FL',0):>8.1%}")
    print(f"{'High (>=40%)':<12} {len(high_ht):>6} {high_profile.get('HT',0):>8.1%} {high_profile.get('EN',0):>8.1%} {high_profile.get('AX',0):>8.1%} {high_profile.get('FQ',0):>8.1%} {high_profile.get('CC',0):>8.1%} {high_profile.get('FL',0):>8.1%}")

    # === 5. PHARMA DETAILED BREAKDOWN ===
    print("\n--- 5. PHARMA DETAILED BREAKDOWN ---\n")

    pharma_folios = [f for f, s, _, _, _ in folio_rates if s == 'PHARMA']
    print(f"PHARMA folios: {pharma_folios}")

    for folio in pharma_folios:
        folio_pars = [p for p in par_profiles if p['folio'] == folio]
        print(f"\n{folio}: {len(folio_pars)} paragraphs")
        for p in folio_pars[:5]:
            print(f"  {p['par_id']}: {p['tokens']} tok, HT={p['ht_rate']:.1%}, EN={p['en_rate']:.1%}")

    # === VERDICT ===
    print("\n=== VERDICT ===\n")

    print(f"Global HT-EN correlation: rho={rho:.3f}")
    if rho < -0.3:
        print("STRONG INVERSE: HT and EN are substitutes")
    elif rho < 0:
        print("WEAK INVERSE: Some trade-off between HT and EN")
    else:
        print("NO INVERSE: HT and EN are independent")

    print(f"\nEN in low-HT paragraphs: {low_profile.get('EN',0):.1%}")
    print(f"EN in high-HT paragraphs: {high_profile.get('EN',0):.1%}")
    print(f"EN drop: {low_profile.get('EN',0) - high_profile.get('EN',0):.1%}")

    # Save
    output = {
        'folio_correlation': rho,
        'paragraph_correlation': rho_par if 'rho_par' in dir() else None,
        'role_by_ht_level': {
            'low': low_profile,
            'med': med_profile,
            'high': high_profile
        },
        'n_paragraphs_by_level': {
            'low': len(low_ht),
            'med': len(med_ht),
            'high': len(high_ht)
        }
    }

    with open(results_dir / 'ht_en_inverse.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to ht_en_inverse.json")

if __name__ == '__main__':
    main()
