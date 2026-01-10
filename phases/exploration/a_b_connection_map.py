#!/usr/bin/env python
"""
Generate A <-> B Connection Map

Creates a reference file showing which Currier A entries and Currier B
folios/procedures share vocabulary.

FRAMING (post-robustness testing):
- This is VOCABULARY OVERLAP reflecting COMPLEXITY ALIGNMENT
- NOT risk/hazard encoding (falsified by preregistered test)
- A encodes where distinctions become non-obvious
- B encodes executable sequences through that space

Output: A JSON map and human-readable markdown summary.
"""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, 'C:/git/voynich/apps/script_explorer')
from parsing.currier_a import parse_currier_a_token

DATA_FILE = 'C:/git/voynich/data/transcriptions/interlinear_full_words.txt'
B_SIGNATURES_FILE = 'C:/git/voynich/phases/OPS1_folio_control_signatures/ops1_folio_control_signatures.json'
OUTPUT_DIR = Path('C:/git/voynich/phases/exploration')


def load_a_entries():
    """Load Currier A entries with full metadata."""
    entries = []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        current_entry = None
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                section = parts[3].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                line_num = parts[11].strip('"').strip() if len(parts) > 11 else ''
                if language != 'A':
                    continue
                key = f"{folio}_{line_num}"
                if current_entry is None or current_entry['key'] != key:
                    if current_entry is not None:
                        entries.append(current_entry)
                    current_entry = {
                        'key': key,
                        'folio': folio,
                        'section': section,
                        'line': line_num,
                        'tokens': [],
                        'middles': set(),
                        'prefixes': set()
                    }
                current_entry['tokens'].append(word)
                # Parse components
                result = parse_currier_a_token(word)
                if result.prefix:
                    current_entry['prefixes'].add(result.prefix)
                if result.middle:
                    current_entry['middles'].add(result.middle)
        if current_entry is not None:
            entries.append(current_entry)

    # Convert sets to lists for JSON serialization later
    for e in entries:
        e['middles'] = list(e['middles'])
        e['prefixes'] = list(e['prefixes'])

    return entries


def load_b_folios():
    """Load Currier B folios with tokens and parsed components."""
    folios = {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"').strip()
                language = parts[6].strip('"').strip() if len(parts) > 6 else ''
                if language != 'B':
                    continue
                if folio not in folios:
                    folios[folio] = {
                        'folio': folio,
                        'tokens': [],
                        'vocabulary': set(),
                        'middles': set()
                    }
                folios[folio]['tokens'].append(word)
                folios[folio]['vocabulary'].add(word)
                result = parse_currier_a_token(word)
                if result.middle:
                    folios[folio]['middles'].add(result.middle)

    # Convert sets
    for f in folios.values():
        f['vocabulary'] = list(f['vocabulary'])
        f['middles'] = list(f['middles'])

    return folios


def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def classify_a_entries(entries, threshold=0.0):
    """Classify entries as singleton or clustered based on adjacency."""
    n = len(entries)
    adj_j = []
    for i in range(n - 1):
        if entries[i]['section'] == entries[i+1]['section']:
            j = jaccard(set(entries[i]['tokens']), set(entries[i+1]['tokens']))
            adj_j.append(j)
        else:
            adj_j.append(-1)

    runs = []
    current_run = [0]
    for i in range(n - 1):
        j = adj_j[i]
        if j > threshold:
            current_run.append(i + 1)
        else:
            if len(current_run) >= 2:
                runs.append(current_run)
            current_run = [i + 1]
    if len(current_run) >= 2:
        runs.append(current_run)

    classification = {}
    run_indices = set()
    for run in runs:
        run_indices.update(run)

    for i in range(n):
        classification[i] = 'clustered' if i in run_indices else 'singleton'

    return classification, runs


def build_connection_map(a_entries, b_folios, classification):
    """Build bidirectional connection map based on vocabulary overlap."""

    # A -> B connections (which B folios share vocabulary with each A entry)
    a_to_b = {}
    for i, entry in enumerate(a_entries):
        entry_vocab = set(entry['tokens'])
        connections = []
        for folio_id, folio in b_folios.items():
            folio_vocab = set(folio['vocabulary'])
            shared = entry_vocab & folio_vocab
            if shared:
                connections.append({
                    'folio': folio_id,
                    'shared_tokens': list(shared),
                    'shared_count': len(shared),
                    'jaccard': jaccard(entry_vocab, folio_vocab)
                })
        connections.sort(key=lambda x: x['shared_count'], reverse=True)
        a_to_b[entry['key']] = {
            'entry_key': entry['key'],
            'folio': entry['folio'],
            'section': entry['section'],
            'classification': classification[i],
            'token_count': len(entry['tokens']),
            'b_connections': connections[:20]  # Top 20 connections
        }

    # B -> A connections (which A entries share vocabulary with each B folio)
    b_to_a = {}
    for folio_id, folio in b_folios.items():
        folio_vocab = set(folio['vocabulary'])
        connections = []
        for i, entry in enumerate(a_entries):
            entry_vocab = set(entry['tokens'])
            shared = entry_vocab & folio_vocab
            if shared:
                connections.append({
                    'entry_key': entry['key'],
                    'section': entry['section'],
                    'classification': classification[i],
                    'shared_tokens': list(shared),
                    'shared_count': len(shared),
                    'jaccard': jaccard(entry_vocab, folio_vocab)
                })
        connections.sort(key=lambda x: x['shared_count'], reverse=True)
        b_to_a[folio_id] = {
            'folio': folio_id,
            'token_count': len(folio['tokens']),
            'vocabulary_size': len(folio['vocabulary']),
            'a_connections': connections[:50]  # Top 50 A entries
        }

    return a_to_b, b_to_a


def compute_summary_stats(a_to_b, b_to_a, a_entries, b_folios, classification):
    """Compute summary statistics for the connection map."""

    # A entries with B connections
    a_with_connections = sum(1 for v in a_to_b.values() if v['b_connections'])

    # B folios with A connections
    b_with_connections = sum(1 for v in b_to_a.values() if v['a_connections'])

    # Average connections
    avg_b_per_a = sum(len(v['b_connections']) for v in a_to_b.values()) / len(a_to_b)
    avg_a_per_b = sum(len(v['a_connections']) for v in b_to_a.values()) / len(b_to_a)

    # Clustered vs singleton connection density
    clustered_connections = []
    singleton_connections = []
    for i, entry in enumerate(a_entries):
        conn_count = len(a_to_b[entry['key']]['b_connections'])
        if classification[i] == 'clustered':
            clustered_connections.append(conn_count)
        else:
            singleton_connections.append(conn_count)

    # Shared vocabulary
    all_a_vocab = set()
    for e in a_entries:
        all_a_vocab.update(e['tokens'])

    all_b_vocab = set()
    for f in b_folios.values():
        all_b_vocab.update(f['vocabulary'])

    shared_vocab = all_a_vocab & all_b_vocab

    return {
        'total_a_entries': len(a_entries),
        'total_b_folios': len(b_folios),
        'a_with_b_connections': a_with_connections,
        'b_with_a_connections': b_with_connections,
        'avg_b_connections_per_a': round(avg_b_per_a, 2),
        'avg_a_connections_per_b': round(avg_a_per_b, 2),
        'clustered_avg_connections': round(sum(clustered_connections) / len(clustered_connections), 2) if clustered_connections else 0,
        'singleton_avg_connections': round(sum(singleton_connections) / len(singleton_connections), 2) if singleton_connections else 0,
        'a_vocabulary_size': len(all_a_vocab),
        'b_vocabulary_size': len(all_b_vocab),
        'shared_vocabulary_size': len(shared_vocab),
        'shared_vocabulary_pct': round(100 * len(shared_vocab) / len(all_a_vocab | all_b_vocab), 1)
    }


def generate_markdown_summary(stats, a_to_b, b_to_a, b_folios):
    """Generate human-readable markdown summary."""

    lines = [
        "# Currier A <-> B Connection Map",
        "",
        "**Generated:** 2026-01-10",
        "**Interpretation:** Complexity-Frontier Topology",
        "**Status:** Exploratory, non-addressable",
        "",
        "> **WARNING:** This map represents population-level vocabulary overlap, NOT correspondence.",
        "> No A entry refers to, indexes, or explains any B folio.",
        "> Using this map for lookup or causal inference violates Constraint C384.",
        "",
        "---",
        "",
        "## Unified Hypothesis: Complexity-Frontier Registry (CFR)",
        "",
        "Currier A externalizes regions of a shared control-space where operational similarity",
        "breaks down and fine discrimination is required.",
        "",
        "This can be described equivalently as:",
        "- a *variant discrimination registry* (craft view), or",
        "- a *partitioning of continuous control space* (formal view)",
        "",
        "**The relationship between A and B is structural and statistical, not addressable or semantic.**",
        "",
        "---",
        "",
        "## CLOSED TESTS (DO NOT RE-RUN)",
        "",
        "| Test | Status | Result |",
        "|------|--------|--------|",
        "| Hazard density correlation | CLOSED | Initially positive (rho=0.228), fully explained by frequency |",
        "| Permutation control | CLOSED | p=0.111 (failed) |",
        "| Frequency-matched control | CLOSED | p=0.056 (failed) |",
        "| **Pre-registered low-freq MIDDLE** | **CLOSED** | **rho=-0.052, p=0.651 (FAIL)** |",
        "| Forgiveness/brittleness | CLOSED | Inseparable from structural complexity |",
        "",
        "**These tests are closed. Any future correlation must exceed frequency-matched baselines to be considered new evidence.**",
        "",
        "---",
        "",
        "## Summary Statistics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total A entries | {stats['total_a_entries']} |",
        f"| Total B folios | {stats['total_b_folios']} |",
        f"| A entries with B connections | {stats['a_with_b_connections']} |",
        f"| B folios with A connections | {stats['b_with_a_connections']} |",
        f"| Avg B connections per A entry | {stats['avg_b_connections_per_a']} |",
        f"| Avg A connections per B folio | {stats['avg_a_connections_per_b']} |",
        f"| Clustered A avg connections | {stats['clustered_avg_connections']} |",
        f"| Singleton A avg connections | {stats['singleton_avg_connections']} |",
        f"| Shared vocabulary | {stats['shared_vocabulary_size']} types ({stats['shared_vocabulary_pct']}%) |",
        "",
        "---",
        "",
        "## Top Connected B Folios",
        "",
        "B folios with most A entry connections:",
        "",
        "| Folio | A Connections | Avg Shared Tokens |",
        "|-------|---------------|-------------------|",
    ]

    # Sort B folios by number of A connections
    b_sorted = sorted(b_to_a.items(), key=lambda x: len(x[1]['a_connections']), reverse=True)
    for folio_id, data in b_sorted[:15]:
        n_conn = len(data['a_connections'])
        if n_conn > 0:
            avg_shared = sum(c['shared_count'] for c in data['a_connections']) / n_conn
            lines.append(f"| {folio_id} | {n_conn} | {avg_shared:.1f} |")

    lines.extend([
        "",
        "---",
        "",
        "## Connection Density by A Section",
        "",
        "| Section | Entries | Avg B Connections |",
        "|---------|---------|-------------------|",
    ])

    # Group by section
    section_stats = defaultdict(lambda: {'count': 0, 'connections': 0})
    for key, data in a_to_b.items():
        sec = data['section']
        section_stats[sec]['count'] += 1
        section_stats[sec]['connections'] += len(data['b_connections'])

    for sec in sorted(section_stats.keys()):
        s = section_stats[sec]
        avg = s['connections'] / s['count'] if s['count'] > 0 else 0
        lines.append(f"| {sec} | {s['count']} | {avg:.1f} |")

    lines.extend([
        "",
        "---",
        "",
        "## Interpretation: Complexity-Frontier Registry (CFR)",
        "",
        "### Established Facts",
        "",
        "1. **Vocabulary overlap reflects complexity alignment**",
        "   - A and B share ~1,500 token types",
        "   - High-frequency tokens appear in complex structures in BOTH systems",
        "   - This creates apparent correlation that is NOT semantic linkage",
        "",
        "2. **Hazard correlation is spurious (FALSIFIED)**",
        "   - Initial test: rho=0.228, p=0.038",
        "   - Permutation control: p=0.111 (failed)",
        "   - Frequency-matched control: p=0.056 (failed)",
        "   - **Pre-registered low-frequency test: rho=-0.052, p=0.651 (FAIL)**",
        "   - Conclusion: No residual risk-specific signal",
        "",
        "3. **Connection density correlates with complexity**",
        f"   - Clustered A entries: {stats['clustered_avg_connections']} avg B connections",
        f"   - Singleton A entries: {stats['singleton_avg_connections']} avg B connections",
        "   - This reflects WHERE DISTINCTIONS MATTER, not danger",
        "",
        "### The CFR Model",
        "",
        "> **Currier A does not encode danger, procedures, materials, or outcomes.**",
        "> **It encodes where distinctions become non-obvious in a global type system**",
        "> **shared with executable control programs.**",
        "",
        "- **Currier B** provides sequences (how to act)",
        "- **Currier A** provides discrimination (where fine distinctions matter)",
        "- **AZC** constrains availability",
        "- **HT** supports the human operator",
        "",
        "### What This Map Shows",
        "",
        "This connection map reveals which A entries share vocabulary with which B programs.",
        "Higher connectivity indicates regions where:",
        "- Operational similarity breaks down",
        "- Fine-grained distinctions are required",
        "- The same vocabulary appears in complex executable sequences",
        "",
        "This is **complexity topology**, not risk encoding.",
        "",
        "---",
        "",
        "## File References",
        "",
        "| File | Contents |",
        "|------|----------|",
        "| `a_b_connection_map.json` | Full bidirectional map (machine-readable) |",
        "| `a_b_connection_map.py` | Generation script |",
        "| `A_B_CORRELATION_RESULTS.md` | Hazard correlation analysis |",
        "",
    ])

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("Generating Currier A <-> B Connection Map")
    print("=" * 70)

    print("\nLoading data...")
    a_entries = load_a_entries()
    b_folios = load_b_folios()

    print(f"  Loaded {len(a_entries)} A entries")
    print(f"  Loaded {len(b_folios)} B folios")

    print("\nClassifying A entries...")
    classification, runs = classify_a_entries(a_entries)
    n_clustered = sum(1 for v in classification.values() if v == 'clustered')
    print(f"  Clustered: {n_clustered} ({100*n_clustered/len(a_entries):.1f}%)")
    print(f"  Singleton: {len(a_entries) - n_clustered} ({100*(len(a_entries)-n_clustered)/len(a_entries):.1f}%)")

    print("\nBuilding connection map...")
    a_to_b, b_to_a = build_connection_map(a_entries, b_folios, classification)

    print("\nComputing statistics...")
    stats = compute_summary_stats(a_to_b, b_to_a, a_entries, b_folios, classification)

    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Save JSON map with explicit guardrails
    output_json = {
        '_WARNING': [
            'This map represents population-level vocabulary overlap, NOT correspondence.',
            'No A entry refers to, indexes, or explains any B folio.',
            'Counts reflect shared token frequency in complex regions of control space.',
            'Using this map for lookup or causal inference violates Constraint C384.',
            'Hazard correlation is FALSIFIED (preregistered test p=0.651).'
        ],
        'metadata': {
            'generated': '2026-01-10',
            'interpretation': 'Complexity-Frontier Topology',
            'status': 'Exploratory, non-addressable',
            'description': 'Bidirectional vocabulary connection map between Currier A entries and B folios',
            'framing': 'A externalizes complexity frontiers; B executes trajectories through same space'
        },
        'closed_tests': {
            'hazard_correlation': {
                'status': 'CLOSED - NEGATIVE',
                'initial_result': 'rho=0.228, p=0.038',
                'permutation_control': 'p=0.111 (FAILED)',
                'frequency_matched': 'p=0.056 (FAILED)',
                'preregistered_lowfreq': 'rho=-0.052, p=0.651 (FAIL)',
                'conclusion': 'Entirely explained by token frequency; no residual signal'
            },
            'forgiveness_brittleness': {
                'status': 'CLOSED - INSEPARABLE',
                'conclusion': 'Cannot separate from structural complexity'
            }
        },
        'statistics': stats,
        'a_to_b': a_to_b,
        'b_to_a': b_to_a
    }

    json_path = OUTPUT_DIR / 'a_b_connection_map.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, indent=2)
    print(f"\nSaved JSON map to: {json_path}")

    # Save markdown summary
    md_content = generate_markdown_summary(stats, a_to_b, b_to_a, b_folios)
    md_path = OUTPUT_DIR / 'A_B_CONNECTION_MAP.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Saved markdown summary to: {md_path}")

    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == '__main__':
    main()
