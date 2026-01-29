"""
02_a_ri_profile.py - A Paragraph RI Composition

Metrics per A paragraph:
- ri_count, ri_rate
- ri_initial_count, ri_final_count (first/last 20% positions)
- ri_prefix_families (ct, ch, qo, po, do, etc.)
- has_linker (ct-ho tokens)
- ri_concentration_line1 (RI% in line 1 vs body)

Expected: Three-tier structure (C831), linkers rare (0.6%)

Depends on: 00_build_paragraph_inventory.py
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, RecordAnalyzer, Morphology

# Linker tokens (from C837)
LINKERS = {'cthody', 'ctho', 'ctheody', 'qokoiiin'}

# RI prefixes (from C831)
RI_PREFIXES = ['ct', 'ch', 'qo', 'po', 'do', 'sh', 'da', 'sa']

def main():
    results_dir = Path(__file__).parent.parent / 'results'

    # Load inventory
    with open(results_dir / 'a_paragraph_inventory.json') as f:
        inventory = json.load(f)

    with open(results_dir / 'a_paragraph_tokens.json') as f:
        tokens_by_par = json.load(f)

    # Use RecordAnalyzer to classify tokens
    analyzer = RecordAnalyzer()
    morph = Morphology()

    profiles = []

    for par in inventory['paragraphs']:
        par_id = par['par_id']
        tokens = tokens_by_par[par_id]
        folio = par['folio']
        lines = par['lines']

        # Classify tokens using RecordAnalyzer per-line
        token_classes = []
        for t in tokens:
            word = t['word']
            line = t['line']
            if word and '*' not in word:
                # Classify based on RecordAnalyzer
                try:
                    record = analyzer.analyze_record(folio, line)
                    for rt in record.tokens:
                        if rt.word == word:
                            token_classes.append({
                                'word': word,
                                'line': line,
                                'token_class': rt.token_class
                            })
                            break
                    else:
                        # Token not found in record, classify manually
                        m = morph.extract(word)
                        prefix = m.prefix or ''
                        # Simple RI heuristic: starts with RI prefix
                        is_ri = any(prefix.startswith(p) for p in RI_PREFIXES)
                        token_classes.append({
                            'word': word,
                            'line': line,
                            'token_class': 'RI' if is_ri else 'PP'
                        })
                except:
                    # Fallback classification
                    m = morph.extract(word)
                    prefix = m.prefix or ''
                    is_ri = any(prefix.startswith(p) for p in RI_PREFIXES)
                    token_classes.append({
                        'word': word,
                        'line': line,
                        'token_class': 'RI' if is_ri else 'PP'
                    })

        # Calculate RI metrics
        ri_tokens = [t for t in token_classes if t['token_class'] == 'RI']
        ri_count = len(ri_tokens)
        ri_rate = ri_count / len(token_classes) if token_classes else 0

        # Initial/Final position (first/last 20% of tokens)
        n_tokens = len(token_classes)
        cutoff = max(1, int(n_tokens * 0.2))

        ri_initial_count = sum(1 for i, t in enumerate(token_classes)
                               if i < cutoff and t['token_class'] == 'RI')
        ri_final_count = sum(1 for i, t in enumerate(token_classes)
                             if i >= n_tokens - cutoff and t['token_class'] == 'RI')

        # RI prefix families
        prefix_counts = Counter()
        for t in ri_tokens:
            m = morph.extract(t['word'])
            prefix = m.prefix or ''
            # Match to known families
            for p in RI_PREFIXES:
                if prefix.startswith(p):
                    prefix_counts[p] += 1
                    break
            else:
                prefix_counts['other'] += 1

        # Has linker?
        has_linker = any(t['word'] in LINKERS for t in token_classes)

        # RI concentration in line 1 vs body
        if len(lines) >= 2:
            line1_tokens = [t for t in token_classes if t['line'] == lines[0]]
            body_tokens = [t for t in token_classes if t['line'] != lines[0]]

            line1_ri = sum(1 for t in line1_tokens if t['token_class'] == 'RI')
            body_ri = sum(1 for t in body_tokens if t['token_class'] == 'RI')

            line1_ri_rate = line1_ri / len(line1_tokens) if line1_tokens else 0
            body_ri_rate = body_ri / len(body_tokens) if body_tokens else 0

            ri_concentration_line1 = line1_ri_rate / body_ri_rate if body_ri_rate > 0 else None
        else:
            line1_ri_rate = ri_rate
            body_ri_rate = 0
            ri_concentration_line1 = None

        profiles.append({
            'par_id': par_id,
            'folio': par['folio'],
            'section': par['section'],
            'folio_position': par['folio_position'],
            'ri_profile': {
                'ri_count': ri_count,
                'ri_rate': round(ri_rate, 3),
                'ri_initial_count': ri_initial_count,
                'ri_final_count': ri_final_count,
                'ri_prefix_families': dict(prefix_counts),
                'has_linker': has_linker,
                'line1_ri_rate': round(line1_ri_rate, 3),
                'body_ri_rate': round(body_ri_rate, 3),
                'ri_concentration_line1': round(ri_concentration_line1, 2) if ri_concentration_line1 else None
            }
        })

    # Summary statistics
    ri_rates = [p['ri_profile']['ri_rate'] for p in profiles]
    linker_count = sum(1 for p in profiles if p['ri_profile']['has_linker'])

    # Aggregate prefix distribution
    all_prefixes = Counter()
    for p in profiles:
        all_prefixes.update(p['ri_profile']['ri_prefix_families'])

    # RI concentration stats (for paragraphs with 2+ lines)
    concentrations = [p['ri_profile']['ri_concentration_line1'] for p in profiles
                      if p['ri_profile']['ri_concentration_line1'] is not None]

    summary = {
        'system': 'A',
        'paragraph_count': len(profiles),
        'ri_rate': {
            'mean': round(statistics.mean(ri_rates), 3),
            'median': round(statistics.median(ri_rates), 3),
            'stdev': round(statistics.stdev(ri_rates), 3)
        },
        'linker_rate': round(linker_count / len(profiles), 3),
        'linker_count': linker_count,
        'prefix_distribution': dict(all_prefixes.most_common()),
        'ri_concentration_line1': {
            'mean': round(statistics.mean(concentrations), 2) if concentrations else None,
            'median': round(statistics.median(concentrations), 2) if concentrations else None,
            'expected': 1.85  # From C833
        }
    }

    # Print summary
    print("=== A PARAGRAPH RI PROFILE ===\n")
    print(f"Paragraphs: {summary['paragraph_count']}")
    print(f"\nRI rate: mean={summary['ri_rate']['mean']}, median={summary['ri_rate']['median']}")
    print(f"Linker rate: {summary['linker_rate']} ({linker_count} paragraphs)")

    print("\nRI prefix distribution:")
    for prefix, count in all_prefixes.most_common(10):
        print(f"  {prefix}: {count}")

    if concentrations:
        print(f"\nRI line-1 concentration: mean={summary['ri_concentration_line1']['mean']}, expected={summary['ri_concentration_line1']['expected']}")

    # Save
    with open(results_dir / 'a_ri_profile.json', 'w') as f:
        json.dump({
            'summary': summary,
            'profiles': profiles
        }, f, indent=2)

    print(f"\nSaved to {results_dir}/a_ri_profile.json")

if __name__ == '__main__':
    main()
