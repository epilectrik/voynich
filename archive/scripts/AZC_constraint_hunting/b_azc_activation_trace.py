"""
F-AZC-015: Windowed AZC Activation Trace

Traces how AZC constraint constellations evolve during B procedure execution.
Reveals whether parallelism is structured, uniform, or phased.
"""

import json
import csv
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import statistics


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)


# Selected B folios for analysis
SAMPLE_FOLIOS = {
    'brittle': ['f83v', 'f77r', 'f76r'],
    'forgiving': ['f48r', 'f85v2', 'f105v'],
    'mixed': ['f113r', 'f41r']
}

# Morphological components
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']

# Zodiac folios (from C430-C431)
ZODIAC_FOLIOS = {'f70v1', 'f70v2', 'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3',
                 'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v'}


def decompose_token(token: str) -> Dict[str, str]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    original = token
    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return {'prefix': prefix, 'middle': token, 'suffix': suffix}


def build_token_to_azc_mapping_from_source(filepath: Path) -> Dict[str, Set[str]]:
    """Build token -> AZC folio mapping directly from source data."""
    token_to_folios = defaultdict(set)
    azc_sections = {'Z', 'A', 'C'}

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # AZC folios: section in Z, A, C or language not A/B
            is_azc = section in azc_sections or language not in ('A', 'B')
            if is_azc:
                token_to_folios[word].add(folio)

    return dict(token_to_folios)


def load_azc_escape_rates(ht_data: Dict) -> Dict[str, float]:
    """Load escape rates by AZC folio."""
    # The F-AZC-013 data has aggregate stats but not per-folio
    # We'll use a uniform estimate from aggregate mean
    mean_escape = ht_data.get('aggregate', {}).get('escape_rate', {}).get('mean', 3.86)

    # For now, return the mean for all folios
    # TODO: Load actual per-folio rates if available
    return {'mean': mean_escape}


def load_b_folio_tokens(filepath: Path, target_folio: str) -> List[Dict]:
    """Load all tokens from a B folio in sequence order."""
    tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            folio = row.get('folio', '').strip()
            if folio != target_folio:
                continue

            word = row.get('word', '').strip()
            language = row.get('language', '').strip()
            line = row.get('line', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            if language != 'B':
                continue

            decomp = decompose_token(word)
            tokens.append({
                'token': word,
                'line': line,
                'prefix': decomp['prefix'],
                'middle': decomp['middle'],
                'suffix': decomp['suffix']
            })

    return tokens


def compute_window_metrics(tokens: List[Dict], start: int, size: int,
                           token_to_azc: Dict[str, Set[str]],
                           escape_rates: Dict) -> Dict:
    """Compute all metrics for a single window."""
    window_tokens = tokens[start:start+size]

    if not window_tokens:
        return None

    # Collect AZC folios activated by tokens in window
    azc_folios_activated = set()
    suffix_counts = Counter()
    prefix_counts = Counter()
    tokens_with_azc = 0

    for t in window_tokens:
        # Get AZC folio membership for this token
        azc_folios = token_to_azc.get(t['token'], set())
        azc_folios_activated.update(azc_folios)
        if azc_folios:
            tokens_with_azc += 1

        # Track suffixes and prefixes
        if t['suffix']:
            suffix_counts[t['suffix']] += 1
        if t['prefix']:
            prefix_counts[t['prefix']] += 1

    # Compute metrics
    n_folios_active = len(azc_folios_activated)

    # Zodiac fraction
    zodiac_count = len(azc_folios_activated & ZODIAC_FOLIOS)
    zodiac_fraction = zodiac_count / n_folios_active if n_folios_active > 0 else 0

    # Escape rate (using mean for now)
    escape_rate_mean = escape_rates.get('mean', 3.86)

    # Top suffixes (phase indicators)
    phase_suffixes = ['aiin', 'ain', 'iin', 'in']
    phase_suffix_count = sum(suffix_counts.get(s, 0) for s in phase_suffixes)
    phase_suffix_rate = phase_suffix_count / len(window_tokens) if window_tokens else 0

    return {
        'start': start,
        'size': len(window_tokens),
        'n_folios_active': n_folios_active,
        'azc_folios': list(azc_folios_activated),
        'zodiac_fraction': round(zodiac_fraction, 3),
        'escape_rate_mean': round(escape_rate_mean, 2),
        'tokens_with_azc_mapping': tokens_with_azc,
        'azc_coverage': round(tokens_with_azc / len(window_tokens), 3) if window_tokens else 0,
        'phase_suffix_rate': round(phase_suffix_rate, 3),
        'suffix_dist': dict(suffix_counts.most_common(5)),
        'prefix_dist': dict(prefix_counts.most_common(5))
    }


def trace_folio_activation(folio: str, tokens: List[Dict],
                           token_to_azc: Dict[str, Set[str]],
                           escape_rates: Dict,
                           window_size: int = 11, stride: int = 3) -> Dict:
    """Generate full windowed trace for a B folio."""
    windows = []

    for start in range(0, len(tokens) - window_size + 1, stride):
        metrics = compute_window_metrics(tokens, start, window_size,
                                         token_to_azc, escape_rates)
        if metrics:
            windows.append(metrics)

    if not windows:
        return {'folio': folio, 'status': 'insufficient_tokens', 'n_tokens': len(tokens)}

    # Compute summary statistics
    n_folios_series = [w['n_folios_active'] for w in windows]
    zodiac_series = [w['zodiac_fraction'] for w in windows]
    phase_suffix_series = [w['phase_suffix_rate'] for w in windows]

    # Temporal pattern analysis
    # Compute trend (is n_folios_active increasing, decreasing, or flat?)
    n = len(n_folios_series)
    if n >= 3:
        early = statistics.mean(n_folios_series[:n//3])
        mid = statistics.mean(n_folios_series[n//3:2*n//3])
        late = statistics.mean(n_folios_series[2*n//3:])

        if early > mid > late:
            pattern = 'PHASED_NARROWING'
        elif late > mid > early:
            pattern = 'PHASED_BROADENING'
        elif max(n_folios_series) - min(n_folios_series) < 3:
            pattern = 'UNIFORM'
        else:
            pattern = 'OSCILLATING'
    else:
        pattern = 'INSUFFICIENT_DATA'

    # Autocorrelation of folio activation (do same folios persist?)
    # Simplified: measure overlap between consecutive windows
    overlaps = []
    for i in range(1, len(windows)):
        prev_folios = set(windows[i-1]['azc_folios'])
        curr_folios = set(windows[i]['azc_folios'])
        if prev_folios or curr_folios:
            intersection = len(prev_folios & curr_folios)
            union = len(prev_folios | curr_folios)
            overlaps.append(intersection / union if union > 0 else 0)

    persistence = statistics.mean(overlaps) if overlaps else 0

    return {
        'folio': folio,
        'n_tokens': len(tokens),
        'n_windows': len(windows),
        'windows': windows,
        'summary': {
            'n_folios_mean': round(statistics.mean(n_folios_series), 2),
            'n_folios_min': min(n_folios_series),
            'n_folios_max': max(n_folios_series),
            'n_folios_std': round(statistics.stdev(n_folios_series), 2) if len(n_folios_series) > 1 else 0,
            'zodiac_fraction_mean': round(statistics.mean(zodiac_series), 3),
            'phase_suffix_mean': round(statistics.mean(phase_suffix_series), 3),
            'pattern': pattern,
            'persistence': round(persistence, 3)
        }
    }


def analyze_by_folio_type(results: Dict) -> Dict:
    """Compare patterns across folio types."""
    type_summaries = {}

    for folio_type in ['brittle', 'forgiving', 'mixed']:
        folios = [r for r in results['traces'] if r['folio'] in SAMPLE_FOLIOS.get(folio_type, [])]

        if not folios:
            continue

        # Aggregate metrics
        n_folios_means = [f['summary']['n_folios_mean'] for f in folios if 'summary' in f]
        patterns = [f['summary']['pattern'] for f in folios if 'summary' in f]
        persistence = [f['summary']['persistence'] for f in folios if 'summary' in f]

        type_summaries[folio_type] = {
            'n_folios': len(folios),
            'n_folios_active_mean': round(statistics.mean(n_folios_means), 2) if n_folios_means else 0,
            'pattern_distribution': dict(Counter(patterns)),
            'persistence_mean': round(statistics.mean(persistence), 3) if persistence else 0
        }

    return type_summaries


def determine_overall_pattern(type_summaries: Dict) -> Dict:
    """Determine which Case (A/B/C) the results support."""
    all_means = []
    all_patterns = []

    for folio_type, summary in type_summaries.items():
        all_means.append(summary['n_folios_active_mean'])
        all_patterns.extend(summary['pattern_distribution'].keys())

    overall_mean = statistics.mean(all_means) if all_means else 0
    pattern_counts = Counter(all_patterns)

    # Determine case
    if overall_mean >= 15:
        case = 'B'
        description = 'High-order uniform parallelism'
        implication = 'AZC is primarily a global legality baseline'
    elif 'PHASED_NARROWING' in pattern_counts or 'PHASED_BROADENING' in pattern_counts:
        case = 'C'
        description = 'Phased parallelism'
        implication = 'Constraint space narrows/broadens over execution'
    elif overall_mean < 10:
        case = 'A'
        description = 'Low-order structured parallelism'
        implication = 'Bounded composable compatibility classes'
    else:
        case = 'MIXED'
        description = 'Mixed patterns'
        implication = 'Further analysis needed'

    return {
        'case': case,
        'description': description,
        'implication': implication,
        'evidence': {
            'mean_folios_active': round(overall_mean, 2),
            'dominant_patterns': pattern_counts.most_common(3)
        }
    }


def main():
    base_path = Path(__file__).parent.parent.parent
    data_path = base_path / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
    threading_path = base_path / 'results' / 'azc_folio_threading.json'
    ht_path = base_path / 'results' / 'azc_ht_modulation.json'

    print("F-AZC-015: Windowed AZC Activation Trace")
    print("="*60)

    # Load dependencies
    print("\nLoading dependencies...")

    with open(threading_path, 'r', encoding='utf-8') as f:
        threading_data = json.load(f)

    with open(ht_path, 'r', encoding='utf-8') as f:
        ht_data = json.load(f)

    # Build token -> AZC folio mapping from source data
    print("Building token-to-AZC mapping from source...")
    token_to_azc = build_token_to_azc_mapping_from_source(data_path)
    print(f"  Mapped {len(token_to_azc)} token types to AZC folios")

    # Load escape rates
    escape_rates = load_azc_escape_rates(ht_data)

    # Process each sample folio
    results = {
        'fit_id': 'F-AZC-015',
        'question': 'What does the parallel constraint landscape look like during B execution?',
        'parameters': {
            'window_size': 11,
            'stride': 3,
            'sample_folios': SAMPLE_FOLIOS
        },
        'traces': []
    }

    all_folios = SAMPLE_FOLIOS['brittle'] + SAMPLE_FOLIOS['forgiving'] + SAMPLE_FOLIOS['mixed']

    for folio in all_folios:
        print(f"\nProcessing {folio}...")

        # Load tokens
        tokens = load_b_folio_tokens(data_path, folio)
        print(f"  Loaded {len(tokens)} tokens")

        if len(tokens) < 15:
            print(f"  Skipping - insufficient tokens")
            results['traces'].append({'folio': folio, 'status': 'insufficient_tokens', 'n_tokens': len(tokens)})
            continue

        # Generate trace
        trace = trace_folio_activation(folio, tokens, token_to_azc, escape_rates)
        results['traces'].append(trace)

        if 'summary' in trace:
            print(f"  Pattern: {trace['summary']['pattern']}")
            print(f"  N folios active: {trace['summary']['n_folios_mean']:.1f} (range: {trace['summary']['n_folios_min']}-{trace['summary']['n_folios_max']})")
            print(f"  Persistence: {trace['summary']['persistence']:.3f}")

    # Analyze by folio type
    print("\n" + "="*60)
    print("ANALYSIS BY FOLIO TYPE")
    print("="*60)

    type_summaries = analyze_by_folio_type(results)
    results['type_analysis'] = type_summaries

    for folio_type, summary in type_summaries.items():
        print(f"\n{folio_type.upper()}:")
        print(f"  Mean AZC folios active: {summary['n_folios_active_mean']}")
        print(f"  Patterns: {summary['pattern_distribution']}")
        print(f"  Persistence: {summary['persistence_mean']}")

    # Determine overall pattern
    print("\n" + "="*60)
    print("OVERALL INTERPRETATION")
    print("="*60)

    interpretation = determine_overall_pattern(type_summaries)
    results['interpretation'] = interpretation

    print(f"\nCase: {interpretation['case']}")
    print(f"Description: {interpretation['description']}")
    print(f"Implication: {interpretation['implication']}")
    print(f"Evidence: {interpretation['evidence']}")

    # Save results
    output_path = base_path / 'results' / 'b_azc_activation_trace.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {output_path}")


if __name__ == '__main__':
    main()
