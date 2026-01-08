"""
Sister Pair Conditioning Test: What determines ch vs sh choice?

For CONDITIONED pairs (low Jaccard like cheky/sheky), test if the
choice correlates with known higher-level structures:
- Section (H/P/T/B/C/S)
- Quire
- Control regime (REGIME_1-4)
- Line position (initial/final/mid)

If alignment found -> Tier 2 (contextual constraint)
If no alignment -> stylistic/scribal variation

Tier 4 - Exploratory
"""

from collections import defaultdict, Counter
import json
import math

PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Known conditioned pairs (Jaccard < 0.3)
CONDITIONED_PAIRS = [
    ('cheky', 'sheky'),      # J=0.11
    ('chy', 'shy'),          # J=0.15
    ('chody', 'shody'),      # J=0.24
    ('chcthy', 'shcthy'),    # J=0.25
    ('checkhy', 'sheckhy'),  # J=0.28
    ('char', 'shar'),        # J=0.31
    ('chckhy', 'shckhy'),    # J=0.33
]

# Free variation pairs for comparison (Jaccard > 0.5)
FREE_PAIRS = [
    ('chedy', 'shedy'),      # J=0.80
    ('cheol', 'sheol'),      # J=0.59
    ('chey', 'shey'),        # J=0.58
    ('cheey', 'sheey'),      # J=0.53
]

def load_currier_b_with_context():
    """Load Currier B tokens with full context."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    data = []
    seen = set()

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
            quire = parts[4] if len(parts) > 4 else ''
            currier = parts[6]
            transcriber = parts[12]
            line_num = parts[11]
            line_init = parts[13]
            line_final = parts[14] if len(parts) > 14 else '0'

            if currier == 'B' and transcriber == 'H' and token and '*' not in token:
                key = (folio, line_num, token)
                if key not in seen:
                    seen.add(key)
                    data.append({
                        'token': token,
                        'folio': folio,
                        'section': section,
                        'quire': quire,
                        'line': line_num,
                        'line_init': line_init == '1',
                        'line_final': line_final == '1'
                    })

    return data

def get_folio_regimes():
    """Load regime classifications from OPS results if available."""
    # Hardcoded from OPS-2 findings
    regime_map = {
        # REGIME_1 (conservative)
        'f75r': 1, 'f75v': 1, 'f76r': 1, 'f76v': 1, 'f77r': 1, 'f77v': 1,
        'f78r': 1, 'f78v': 1, 'f79r': 1, 'f79v': 1, 'f80r': 1, 'f80v': 1,
        # REGIME_2 (low intensity)
        'f81r': 2, 'f81v': 2, 'f82r': 2, 'f82v': 2, 'f83r': 2, 'f83v': 2,
        'f84r': 2, 'f84v': 2,
        # REGIME_3 (aggressive/throughput)
        'f88r': 3, 'f88v': 3, 'f89r1': 3, 'f89r2': 3,
        # REGIME_4 (balanced)
        'f85r1': 4, 'f85r2': 4, 'f86r3': 4, 'f86r4': 4,
    }
    return regime_map

def chi_square_test(observed, expected):
    """Simple chi-square statistic."""
    if expected == 0:
        return 0
    return (observed - expected) ** 2 / expected

def analyze_pair_conditioning(data, ch_token, sh_token):
    """Analyze what conditions the choice between ch and sh forms."""

    # Find all occurrences
    ch_contexts = []
    sh_contexts = []

    for d in data:
        if d['token'] == ch_token:
            ch_contexts.append(d)
        elif d['token'] == sh_token:
            sh_contexts.append(d)

    if len(ch_contexts) < 5 or len(sh_contexts) < 5:
        return None  # Not enough data

    results = {
        'pair': f"{ch_token}/{sh_token}",
        'ch_count': len(ch_contexts),
        'sh_count': len(sh_contexts),
        'tests': {}
    }

    total = len(ch_contexts) + len(sh_contexts)
    ch_rate = len(ch_contexts) / total

    # Test 1: Section conditioning
    section_counts = defaultdict(lambda: {'ch': 0, 'sh': 0})
    for d in ch_contexts:
        section_counts[d['section']]['ch'] += 1
    for d in sh_contexts:
        section_counts[d['section']]['sh'] += 1

    # Calculate chi-square for section
    chi2_section = 0
    section_details = {}
    for section, counts in section_counts.items():
        sect_total = counts['ch'] + counts['sh']
        expected_ch = sect_total * ch_rate
        expected_sh = sect_total * (1 - ch_rate)
        chi2_section += chi_square_test(counts['ch'], expected_ch)
        chi2_section += chi_square_test(counts['sh'], expected_sh)
        if sect_total >= 5:
            section_details[section] = {
                'ch': counts['ch'],
                'sh': counts['sh'],
                'ch_pct': 100 * counts['ch'] / sect_total
            }

    results['tests']['section'] = {
        'chi2': chi2_section,
        'df': max(1, len(section_counts) - 1),
        'details': section_details
    }

    # Test 2: Quire conditioning
    quire_counts = defaultdict(lambda: {'ch': 0, 'sh': 0})
    for d in ch_contexts:
        quire_counts[d['quire']]['ch'] += 1
    for d in sh_contexts:
        quire_counts[d['quire']]['sh'] += 1

    chi2_quire = 0
    quire_details = {}
    for quire, counts in quire_counts.items():
        q_total = counts['ch'] + counts['sh']
        expected_ch = q_total * ch_rate
        expected_sh = q_total * (1 - ch_rate)
        chi2_quire += chi_square_test(counts['ch'], expected_ch)
        chi2_quire += chi_square_test(counts['sh'], expected_sh)
        if q_total >= 5:
            quire_details[quire] = {
                'ch': counts['ch'],
                'sh': counts['sh'],
                'ch_pct': 100 * counts['ch'] / q_total
            }

    results['tests']['quire'] = {
        'chi2': chi2_quire,
        'df': max(1, len(quire_counts) - 1),
        'details': quire_details
    }

    # Test 3: Line position conditioning
    pos_counts = {'init': {'ch': 0, 'sh': 0}, 'final': {'ch': 0, 'sh': 0}, 'mid': {'ch': 0, 'sh': 0}}
    for d in ch_contexts:
        if d['line_init']:
            pos_counts['init']['ch'] += 1
        elif d['line_final']:
            pos_counts['final']['ch'] += 1
        else:
            pos_counts['mid']['ch'] += 1
    for d in sh_contexts:
        if d['line_init']:
            pos_counts['init']['sh'] += 1
        elif d['line_final']:
            pos_counts['final']['sh'] += 1
        else:
            pos_counts['mid']['sh'] += 1

    chi2_pos = 0
    pos_details = {}
    for pos, counts in pos_counts.items():
        p_total = counts['ch'] + counts['sh']
        if p_total > 0:
            expected_ch = p_total * ch_rate
            expected_sh = p_total * (1 - ch_rate)
            chi2_pos += chi_square_test(counts['ch'], expected_ch)
            chi2_pos += chi_square_test(counts['sh'], expected_sh)
            pos_details[pos] = {
                'ch': counts['ch'],
                'sh': counts['sh'],
                'ch_pct': 100 * counts['ch'] / p_total if p_total > 0 else 0
            }

    results['tests']['position'] = {
        'chi2': chi2_pos,
        'df': 2,
        'details': pos_details
    }

    # Test 4: Folio-level (are there folio preferences?)
    folio_counts = defaultdict(lambda: {'ch': 0, 'sh': 0})
    for d in ch_contexts:
        folio_counts[d['folio']]['ch'] += 1
    for d in sh_contexts:
        folio_counts[d['folio']]['sh'] += 1

    # Count folios that strongly prefer one form
    ch_dominant = 0  # >70% ch
    sh_dominant = 0  # >70% sh
    mixed = 0        # 30-70% ch

    for folio, counts in folio_counts.items():
        f_total = counts['ch'] + counts['sh']
        if f_total >= 3:
            ch_pct = counts['ch'] / f_total
            if ch_pct > 0.7:
                ch_dominant += 1
            elif ch_pct < 0.3:
                sh_dominant += 1
            else:
                mixed += 1

    results['tests']['folio_preference'] = {
        'ch_dominant': ch_dominant,
        'sh_dominant': sh_dominant,
        'mixed': mixed,
        'total_folios': ch_dominant + sh_dominant + mixed
    }

    return results

def main():
    print("=" * 70)
    print("SISTER PAIR CONDITIONING TEST")
    print("=" * 70)
    print("\nQuestion: What determines ch vs sh choice for conditioned pairs?")

    data = load_currier_b_with_context()
    print(f"\nLoaded {len(data)} Currier B tokens")

    # Analyze conditioned pairs
    print("\n" + "-" * 70)
    print("CONDITIONED PAIRS (Jaccard < 0.3)")
    print("-" * 70)
    print("These pairs show folio segregation - what drives it?")

    conditioned_results = []
    for ch_tok, sh_tok in CONDITIONED_PAIRS:
        result = analyze_pair_conditioning(data, ch_tok, sh_tok)
        if result:
            conditioned_results.append(result)

    # Print conditioned pair results
    for r in conditioned_results:
        print(f"\n### {r['pair']} (n={r['ch_count']}+{r['sh_count']}={r['ch_count']+r['sh_count']})")

        # Section
        sect = r['tests']['section']
        print(f"\n  SECTION (chi2={sect['chi2']:.1f}, df={sect['df']}):")
        for s, d in sorted(sect['details'].items(), key=lambda x: -x[1]['ch']-x[1]['sh']):
            print(f"    {s}: ch={d['ch']}, sh={d['sh']} ({d['ch_pct']:.0f}% ch)")

        # Quire
        quire = r['tests']['quire']
        if quire['details']:
            print(f"\n  QUIRE (chi2={quire['chi2']:.1f}, df={quire['df']}):")
            for q, d in sorted(quire['details'].items(), key=lambda x: -x[1]['ch']-x[1]['sh'])[:5]:
                print(f"    {q}: ch={d['ch']}, sh={d['sh']} ({d['ch_pct']:.0f}% ch)")

        # Position
        pos = r['tests']['position']
        print(f"\n  LINE POSITION (chi2={pos['chi2']:.1f}):")
        for p, d in pos['details'].items():
            if d['ch'] + d['sh'] > 0:
                print(f"    {p}: ch={d['ch']}, sh={d['sh']} ({d['ch_pct']:.0f}% ch)")

        # Folio preference
        fp = r['tests']['folio_preference']
        print(f"\n  FOLIO PREFERENCE:")
        print(f"    ch-dominant (>70%): {fp['ch_dominant']} folios")
        print(f"    sh-dominant (<30%): {fp['sh_dominant']} folios")
        print(f"    mixed (30-70%): {fp['mixed']} folios")

    # Analyze free variation pairs for comparison
    print("\n" + "-" * 70)
    print("FREE VARIATION PAIRS (Jaccard > 0.5) - for comparison")
    print("-" * 70)

    free_results = []
    for ch_tok, sh_tok in FREE_PAIRS:
        result = analyze_pair_conditioning(data, ch_tok, sh_tok)
        if result:
            free_results.append(result)

    for r in free_results:
        print(f"\n### {r['pair']} (n={r['ch_count']}+{r['sh_count']}={r['ch_count']+r['sh_count']})")

        # Section
        sect = r['tests']['section']
        print(f"\n  SECTION (chi2={sect['chi2']:.1f}):")
        for s, d in sorted(sect['details'].items(), key=lambda x: -x[1]['ch']-x[1]['sh']):
            print(f"    {s}: ch={d['ch']}, sh={d['sh']} ({d['ch_pct']:.0f}% ch)")

        # Folio preference
        fp = r['tests']['folio_preference']
        print(f"\n  FOLIO PREFERENCE:")
        print(f"    ch-dominant: {fp['ch_dominant']}, sh-dominant: {fp['sh_dominant']}, mixed: {fp['mixed']}")

    # Summary comparison
    print("\n" + "=" * 70)
    print("SUMMARY: Conditioning Evidence")
    print("=" * 70)

    # Calculate average chi2 for conditioned vs free
    if conditioned_results:
        avg_chi2_cond_sect = sum(r['tests']['section']['chi2'] for r in conditioned_results) / len(conditioned_results)
        avg_chi2_cond_pos = sum(r['tests']['position']['chi2'] for r in conditioned_results) / len(conditioned_results)
    else:
        avg_chi2_cond_sect = 0
        avg_chi2_cond_pos = 0

    if free_results:
        avg_chi2_free_sect = sum(r['tests']['section']['chi2'] for r in free_results) / len(free_results)
        avg_chi2_free_pos = sum(r['tests']['position']['chi2'] for r in free_results) / len(free_results)
    else:
        avg_chi2_free_sect = 0
        avg_chi2_free_pos = 0

    print(f"\nAverage chi2 for SECTION conditioning:")
    print(f"  Conditioned pairs: {avg_chi2_cond_sect:.1f}")
    print(f"  Free variation pairs: {avg_chi2_free_sect:.1f}")
    print(f"  Ratio: {avg_chi2_cond_sect/avg_chi2_free_sect:.2f}x" if avg_chi2_free_sect > 0 else "  Ratio: N/A")

    print(f"\nAverage chi2 for POSITION conditioning:")
    print(f"  Conditioned pairs: {avg_chi2_cond_pos:.1f}")
    print(f"  Free variation pairs: {avg_chi2_free_pos:.1f}")

    # Folio dominance comparison
    if conditioned_results:
        cond_ch_dom = sum(r['tests']['folio_preference']['ch_dominant'] for r in conditioned_results)
        cond_sh_dom = sum(r['tests']['folio_preference']['sh_dominant'] for r in conditioned_results)
        cond_mixed = sum(r['tests']['folio_preference']['mixed'] for r in conditioned_results)
        cond_total = cond_ch_dom + cond_sh_dom + cond_mixed

        print(f"\nFolio dominance pattern (CONDITIONED pairs):")
        print(f"  ch-dominant: {cond_ch_dom} ({100*cond_ch_dom/cond_total:.0f}%)" if cond_total > 0 else "  N/A")
        print(f"  sh-dominant: {cond_sh_dom} ({100*cond_sh_dom/cond_total:.0f}%)" if cond_total > 0 else "  N/A")
        print(f"  mixed: {cond_mixed} ({100*cond_mixed/cond_total:.0f}%)" if cond_total > 0 else "  N/A")

    if free_results:
        free_ch_dom = sum(r['tests']['folio_preference']['ch_dominant'] for r in free_results)
        free_sh_dom = sum(r['tests']['folio_preference']['sh_dominant'] for r in free_results)
        free_mixed = sum(r['tests']['folio_preference']['mixed'] for r in free_results)
        free_total = free_ch_dom + free_sh_dom + free_mixed

        print(f"\nFolio dominance pattern (FREE VARIATION pairs):")
        print(f"  ch-dominant: {free_ch_dom} ({100*free_ch_dom/free_total:.0f}%)" if free_total > 0 else "  N/A")
        print(f"  sh-dominant: {free_sh_dom} ({100*free_sh_dom/free_total:.0f}%)" if free_total > 0 else "  N/A")
        print(f"  mixed: {free_mixed} ({100*free_mixed/free_total:.0f}%)" if free_total > 0 else "  N/A")

    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)
    print("""
If conditioned pairs show:
  - HIGH section chi2 -> SECTION determines choice (Tier 2)
  - HIGH position chi2 -> LINE POSITION determines choice (Tier 2)
  - HIGH folio dominance -> FOLIO/PROGRAM determines choice (Tier 2)
  - NONE of above -> stylistic/scribal variation (Tier 4)
""")

if __name__ == '__main__':
    main()
