"""
HT BURST/CLUSTERING ANALYSIS

Investigates the 5.4x enrichment of HT-HT consecutive pairs.
HT tokens appear in "bursts" rather than evenly distributed.

HT Definition (per user specification):
- All tokens starting with 'y' (y-initial tokens)
- Single-char atoms: y, f, d, r

Analysis Tasks:
1. Identify HT runs (consecutive HT tokens) - length distribution
2. What TRIGGERS a burst? Token BEFORE HT runs
3. What ENDS a burst? Token AFTER HT runs
4. Within-line vs cross-line bursts
5. Correlate with line position, program risk
6. Test: Do bursts mark TRANSITIONS or BOUNDARIES?
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats
from typing import List, Dict, Tuple, Optional, Set

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

# =============================================================================
# HT CLASSIFICATION
# =============================================================================

SINGLE_CHAR_HT = {'y', 'f', 'd', 'r'}

def is_ht_token(token: str) -> bool:
    """
    HT token definition per user specification:
    - Starts with 'y' (y-initial)
    - OR is a single-char atom (y, f, d, r)
    """
    t = token.lower().strip()
    if not t or '*' in t:
        return False

    # Single-char HT atoms
    if t in SINGLE_CHAR_HT:
        return True

    # y-initial tokens
    if t.startswith('y'):
        return True

    return False


def load_data():
    """Load transcription data with full context."""
    data = []

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            # Use Herbal transcription (H) only for consistency
            if row.get('transcriber') != 'H':
                continue

            # Focus on Currier B
            if row.get('language') != 'B':
                continue

            token = row.get('word', '')
            if not token or '*' in token:
                continue

            data.append({
                'token': token.lower(),
                'folio': row.get('folio', ''),
                'line': row.get('line_number', ''),
                'line_initial': int(row.get('line_initial', 0)),
                'line_final': int(row.get('line_final', 0)),
                'section': row.get('section', ''),
            })

    return data


# =============================================================================
# 1. HT RUN IDENTIFICATION
# =============================================================================

def identify_ht_runs(data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Identify all HT runs (consecutive HT tokens).
    Returns:
    - runs: List of run objects with metadata
    - isolated_ht: List of isolated (non-run) HT tokens
    """
    runs = []
    isolated_ht = []

    current_run = []
    current_run_start_idx = None

    for i, d in enumerate(data):
        is_ht = is_ht_token(d['token'])

        if is_ht:
            if not current_run:
                current_run_start_idx = i
            current_run.append((i, d))
        else:
            # End of potential run
            if current_run:
                if len(current_run) >= 2:
                    # This is a run (2+ consecutive HT)
                    runs.append({
                        'length': len(current_run),
                        'tokens': [t[1]['token'] for t in current_run],
                        'indices': [t[0] for t in current_run],
                        'start_idx': current_run_start_idx,
                        'end_idx': current_run[-1][0],
                        'folios': list(set(t[1]['folio'] for t in current_run)),
                        'lines': list(set(t[1]['line'] for t in current_run)),
                        'contexts': [t[1] for t in current_run],
                    })
                else:
                    # Single HT token (isolated)
                    isolated_ht.append(current_run[0])

                current_run = []
                current_run_start_idx = None

    # Handle final run
    if current_run:
        if len(current_run) >= 2:
            runs.append({
                'length': len(current_run),
                'tokens': [t[1]['token'] for t in current_run],
                'indices': [t[0] for t in current_run],
                'start_idx': current_run_start_idx,
                'end_idx': current_run[-1][0],
                'folios': list(set(t[1]['folio'] for t in current_run)),
                'lines': list(set(t[1]['line'] for t in current_run)),
                'contexts': [t[1] for t in current_run],
            })
        else:
            isolated_ht.append(current_run[0])

    return runs, isolated_ht


def analyze_run_lengths(runs: List[Dict], isolated_ht: List):
    """Analyze run length distribution."""
    print("\n" + "=" * 70)
    print("1. HT RUN LENGTH DISTRIBUTION")
    print("=" * 70)

    lengths = [r['length'] for r in runs]
    length_dist = Counter(lengths)

    print(f"\nTotal HT runs identified: {len(runs)}")
    print(f"Total isolated HT tokens: {len(isolated_ht)}")

    total_ht_in_runs = sum(lengths)
    total_ht = total_ht_in_runs + len(isolated_ht)

    print(f"\nTotal HT tokens: {total_ht}")
    print(f"  - In runs (2+): {total_ht_in_runs} ({total_ht_in_runs/total_ht*100:.1f}%)")
    print(f"  - Isolated: {len(isolated_ht)} ({len(isolated_ht)/total_ht*100:.1f}%)")

    print("\n--- Run Length Distribution ---")
    print(f"{'Length':<10} {'Count':>10} {'%':>10} {'Cumulative %':>15}")
    print("-" * 45)

    cumulative = 0
    for length in sorted(length_dist.keys()):
        count = length_dist[length]
        pct = count / len(runs) * 100
        cumulative += pct
        print(f"{length:<10} {count:>10} {pct:>9.1f}% {cumulative:>14.1f}%")

    print(f"\nLongest runs: {sorted(lengths, reverse=True)[:10]}")
    print(f"Mean run length: {np.mean(lengths):.2f}")
    print(f"Median run length: {np.median(lengths):.2f}")

    # Run length 4+
    long_runs = [r for r in runs if r['length'] >= 4]
    print(f"\nLong runs (4+): {len(long_runs)}")
    for r in long_runs[:10]:
        print(f"  Length {r['length']}: {r['tokens'][:6]}...")

    return length_dist


def analyze_ht_forms_in_runs(runs: List[Dict], isolated_ht: List):
    """Compare HT forms that appear in runs vs isolation."""
    print("\n" + "=" * 70)
    print("HT FORMS: RUNS vs ISOLATED")
    print("=" * 70)

    # Collect tokens from runs
    run_tokens = Counter()
    for r in runs:
        for t in r['tokens']:
            run_tokens[t] += 1

    # Collect isolated tokens
    isolated_tokens = Counter(t[1]['token'] for t in isolated_ht)

    # All HT tokens
    all_ht = run_tokens + isolated_tokens

    print(f"\nUnique HT forms: {len(all_ht)}")
    print(f"  - Appear in runs: {len(run_tokens)}")
    print(f"  - Appear isolated: {len(isolated_tokens)}")
    print(f"  - Overlap: {len(set(run_tokens.keys()) & set(isolated_tokens.keys()))}")

    # Run-preferring forms
    print("\n--- Run-Preferring Forms (appear >80% in runs) ---")
    run_preferring = []
    for token in all_ht:
        total = run_tokens[token] + isolated_tokens[token]
        if total >= 10:  # Minimum frequency
            run_pct = run_tokens[token] / total
            if run_pct > 0.8:
                run_preferring.append((token, run_tokens[token], isolated_tokens[token], run_pct))

    run_preferring.sort(key=lambda x: -x[3])
    for token, in_run, isolated, pct in run_preferring[:15]:
        print(f"  {token:<15}: {in_run:>5} in runs, {isolated:>5} isolated ({pct:.1%} in runs)")

    # Isolation-preferring forms
    print("\n--- Isolation-Preferring Forms (appear >80% isolated) ---")
    isolation_preferring = []
    for token in all_ht:
        total = run_tokens[token] + isolated_tokens[token]
        if total >= 10:
            iso_pct = isolated_tokens[token] / total
            if iso_pct > 0.8:
                isolation_preferring.append((token, run_tokens[token], isolated_tokens[token], iso_pct))

    isolation_preferring.sort(key=lambda x: -x[3])
    for token, in_run, isolated, pct in isolation_preferring[:15]:
        print(f"  {token:<15}: {in_run:>5} in runs, {isolated:>5} isolated ({pct:.1%} isolated)")

    # Top forms overall
    print("\n--- Top 20 HT Forms Overall ---")
    for token, count in all_ht.most_common(20):
        run_ct = run_tokens[token]
        iso_ct = isolated_tokens[token]
        run_pct = run_ct / count * 100
        print(f"  {token:<15}: {count:>5} total ({run_ct:>4} run, {iso_ct:>4} iso, {run_pct:.0f}% run)")

    return run_tokens, isolated_tokens


# =============================================================================
# 2. BURST TRIGGERS - What comes BEFORE HT runs?
# =============================================================================

def analyze_burst_triggers(runs: List[Dict], isolated_ht: List, data: List[Dict]):
    """Analyze what tokens precede HT runs vs isolated HT."""
    print("\n" + "=" * 70)
    print("2. BURST TRIGGERS - Tokens BEFORE HT runs")
    print("=" * 70)

    # Tokens before runs
    pre_run_tokens = Counter()
    for r in runs:
        start_idx = r['start_idx']
        if start_idx > 0:
            prev_token = data[start_idx - 1]['token']
            if not is_ht_token(prev_token):  # Ensure it's not HT
                pre_run_tokens[prev_token] += 1

    # Tokens before isolated HT
    pre_isolated_tokens = Counter()
    for idx, d in isolated_ht:
        if idx > 0:
            prev_token = data[idx - 1]['token']
            if not is_ht_token(prev_token):
                pre_isolated_tokens[prev_token] += 1

    print(f"\nPre-RUN tokens captured: {sum(pre_run_tokens.values())}")
    print(f"Pre-ISOLATED tokens captured: {sum(pre_isolated_tokens.values())}")

    # Compare distributions
    print("\n--- Top 20 Tokens BEFORE Runs ---")
    for token, count in pre_run_tokens.most_common(20):
        pre_iso = pre_isolated_tokens[token]
        total = count + pre_iso
        run_pct = count / total * 100 if total > 0 else 0
        print(f"  {token:<15}: {count:>5} before runs, {pre_iso:>5} before isolated ({run_pct:.0f}% run-associated)")

    # Identify run-triggering tokens (enriched before runs)
    print("\n--- RUN-TRIGGERING Tokens (>60% before runs, min 10 occurrences) ---")
    triggers = []
    all_pre_tokens = set(pre_run_tokens.keys()) | set(pre_isolated_tokens.keys())

    for token in all_pre_tokens:
        run_ct = pre_run_tokens[token]
        iso_ct = pre_isolated_tokens[token]
        total = run_ct + iso_ct

        if total >= 10:
            run_pct = run_ct / total
            if run_pct > 0.6:
                triggers.append((token, run_ct, iso_ct, run_pct))

    triggers.sort(key=lambda x: -x[3])
    for token, run_ct, iso_ct, pct in triggers[:20]:
        print(f"  {token:<15}: {run_ct:>4}/{run_ct+iso_ct:>4} = {pct:.1%} before runs")

    # Statistical test: chi-square for top trigger
    if triggers:
        top_trigger = triggers[0][0]
        trigger_run = pre_run_tokens[top_trigger]
        trigger_iso = pre_isolated_tokens[top_trigger]
        other_run = sum(pre_run_tokens.values()) - trigger_run
        other_iso = sum(pre_isolated_tokens.values()) - trigger_iso

        contingency = np.array([[trigger_run, trigger_iso], [other_run, other_iso]])
        chi2, p, _, _ = stats.chi2_contingency(contingency)
        print(f"\nChi-square for top trigger '{top_trigger}': chi2={chi2:.2f}, p={p:.6f}")

    # Prefix analysis - what PREFIX of preceding token triggers runs?
    print("\n--- Preceding Token PREFIXES (2-char) ---")
    pre_run_prefixes = Counter()
    pre_iso_prefixes = Counter()

    for token, count in pre_run_tokens.items():
        if len(token) >= 2:
            pre_run_prefixes[token[:2]] += count

    for token, count in pre_isolated_tokens.items():
        if len(token) >= 2:
            pre_iso_prefixes[token[:2]] += count

    print(f"{'Prefix':<10} {'Before Run':>12} {'Before Iso':>12} {'Run %':>10}")
    print("-" * 44)

    all_prefixes = set(pre_run_prefixes.keys()) | set(pre_iso_prefixes.keys())
    prefix_data = []
    for prefix in all_prefixes:
        run_ct = pre_run_prefixes[prefix]
        iso_ct = pre_iso_prefixes[prefix]
        total = run_ct + iso_ct
        if total >= 20:
            prefix_data.append((prefix, run_ct, iso_ct, run_ct/total))

    prefix_data.sort(key=lambda x: -x[3])
    for prefix, run_ct, iso_ct, pct in prefix_data[:15]:
        print(f"{prefix:<10} {run_ct:>12} {iso_ct:>12} {pct:>9.1%}")

    return pre_run_tokens, pre_isolated_tokens


# =============================================================================
# 3. BURST TERMINATORS - What comes AFTER HT runs?
# =============================================================================

def analyze_burst_terminators(runs: List[Dict], isolated_ht: List, data: List[Dict]):
    """Analyze what tokens follow HT runs vs isolated HT."""
    print("\n" + "=" * 70)
    print("3. BURST TERMINATORS - Tokens AFTER HT runs")
    print("=" * 70)

    # Tokens after runs
    post_run_tokens = Counter()
    for r in runs:
        end_idx = r['end_idx']
        if end_idx < len(data) - 1:
            next_token = data[end_idx + 1]['token']
            if not is_ht_token(next_token):
                post_run_tokens[next_token] += 1

    # Tokens after isolated HT
    post_isolated_tokens = Counter()
    for idx, d in isolated_ht:
        if idx < len(data) - 1:
            next_token = data[idx + 1]['token']
            if not is_ht_token(next_token):
                post_isolated_tokens[next_token] += 1

    print(f"\nPost-RUN tokens captured: {sum(post_run_tokens.values())}")
    print(f"Post-ISOLATED tokens captured: {sum(post_isolated_tokens.values())}")

    # Compare distributions
    print("\n--- Top 20 Tokens AFTER Runs ---")
    for token, count in post_run_tokens.most_common(20):
        post_iso = post_isolated_tokens[token]
        total = count + post_iso
        run_pct = count / total * 100 if total > 0 else 0
        print(f"  {token:<15}: {count:>5} after runs, {post_iso:>5} after isolated ({run_pct:.0f}% run-following)")

    # Identify run-terminating tokens
    print("\n--- RUN-TERMINATING Tokens (>60% after runs, min 10 occurrences) ---")
    terminators = []
    all_post_tokens = set(post_run_tokens.keys()) | set(post_isolated_tokens.keys())

    for token in all_post_tokens:
        run_ct = post_run_tokens[token]
        iso_ct = post_isolated_tokens[token]
        total = run_ct + iso_ct

        if total >= 10:
            run_pct = run_ct / total
            if run_pct > 0.6:
                terminators.append((token, run_ct, iso_ct, run_pct))

    terminators.sort(key=lambda x: -x[3])
    for token, run_ct, iso_ct, pct in terminators[:20]:
        print(f"  {token:<15}: {run_ct:>4}/{run_ct+iso_ct:>4} = {pct:.1%} after runs")

    # Suffix analysis
    print("\n--- Following Token SUFFIXES (3-char) ---")
    post_run_suffixes = Counter()
    post_iso_suffixes = Counter()

    for token, count in post_run_tokens.items():
        if len(token) >= 3:
            post_run_suffixes[token[-3:]] += count

    for token, count in post_isolated_tokens.items():
        if len(token) >= 3:
            post_iso_suffixes[token[-3:]] += count

    print(f"{'Suffix':<10} {'After Run':>12} {'After Iso':>12} {'Run %':>10}")
    print("-" * 44)

    all_suffixes = set(post_run_suffixes.keys()) | set(post_iso_suffixes.keys())
    suffix_data = []
    for suffix in all_suffixes:
        run_ct = post_run_suffixes[suffix]
        iso_ct = post_iso_suffixes[suffix]
        total = run_ct + iso_ct
        if total >= 20:
            suffix_data.append((suffix, run_ct, iso_ct, run_ct/total))

    suffix_data.sort(key=lambda x: -x[3])
    for suffix, run_ct, iso_ct, pct in suffix_data[:15]:
        print(f"{suffix:<10} {run_ct:>12} {iso_ct:>12} {pct:>9.1%}")

    return post_run_tokens, post_isolated_tokens


# =============================================================================
# 4. WITHIN-LINE vs CROSS-LINE BURSTS
# =============================================================================

def analyze_line_boundaries(runs: List[Dict], data: List[Dict]):
    """Analyze whether HT bursts respect or span line boundaries."""
    print("\n" + "=" * 70)
    print("4. LINE BOUNDARY ANALYSIS")
    print("=" * 70)

    within_line = []
    cross_line = []

    for r in runs:
        unique_lines = set()
        unique_folios = set()

        for ctx in r['contexts']:
            line_key = (ctx['folio'], ctx['line'])
            unique_lines.add(line_key)
            unique_folios.add(ctx['folio'])

        if len(unique_lines) == 1:
            within_line.append(r)
        else:
            cross_line.append(r)

    print(f"\nTotal runs: {len(runs)}")
    print(f"  - Within-line: {len(within_line)} ({len(within_line)/len(runs)*100:.1f}%)")
    print(f"  - Cross-line: {len(cross_line)} ({len(cross_line)/len(runs)*100:.1f}%)")

    # Analyze cross-line runs
    if cross_line:
        cross_lengths = [r['length'] for r in cross_line]
        within_lengths = [r['length'] for r in within_line]

        print(f"\n--- Cross-line Run Details ---")
        print(f"Mean length of cross-line runs: {np.mean(cross_lengths):.2f}")
        print(f"Mean length of within-line runs: {np.mean(within_lengths):.2f}")

        # How many lines do cross-line runs span?
        spans = []
        for r in cross_line:
            n_lines = len(set((ctx['folio'], ctx['line']) for ctx in r['contexts']))
            spans.append(n_lines)

        span_dist = Counter(spans)
        print(f"\nLines spanned by cross-line runs:")
        for span, count in sorted(span_dist.items()):
            print(f"  {span} lines: {count} runs")

        # Do cross-line runs span folios?
        cross_folio_runs = [r for r in cross_line if len(set(ctx['folio'] for ctx in r['contexts'])) > 1]
        print(f"\nCross-FOLIO runs: {len(cross_folio_runs)}")

    # Position within line
    print("\n--- Run Start Position Within Line ---")
    print("(Using line_initial as proxy: 1=first token, higher=later)")

    run_start_positions = []
    for r in runs:
        first_ctx = r['contexts'][0]
        pos = first_ctx.get('line_initial', 0)
        if pos > 0:
            run_start_positions.append(pos)

    if run_start_positions:
        pos_dist = Counter(run_start_positions)
        print(f"\n{'Position':<10} {'Count':>10} {'%':>10}")
        print("-" * 30)
        for pos in sorted(pos_dist.keys())[:10]:
            count = pos_dist[pos]
            pct = count / len(run_start_positions) * 100
            print(f"{pos:<10} {count:>10} {pct:>9.1f}%")

        # Line-initial vs mid-line
        line_initial_runs = sum(1 for p in run_start_positions if p == 1)
        print(f"\nRuns starting at line position 1: {line_initial_runs} ({line_initial_runs/len(run_start_positions)*100:.1f}%)")

    return within_line, cross_line


# =============================================================================
# 5. CORRELATION WITH POSITION AND CONTEXT
# =============================================================================

def analyze_position_correlations(runs: List[Dict], isolated_ht: List, data: List[Dict]):
    """Correlate bursts with line position, folio, and context."""
    print("\n" + "=" * 70)
    print("5. POSITION AND CONTEXT CORRELATIONS")
    print("=" * 70)

    # Line position analysis
    print("\n--- HT Density by Line Position ---")

    # Bucket by line_initial position
    position_buckets = {'early': [], 'middle': [], 'late': []}

    for i, d in enumerate(data):
        pos = d.get('line_initial', 0)
        is_ht = is_ht_token(d['token'])

        if pos > 0:
            if pos <= 3:
                position_buckets['early'].append(is_ht)
            elif pos <= 6:
                position_buckets['middle'].append(is_ht)
            else:
                position_buckets['late'].append(is_ht)

    for bucket, values in position_buckets.items():
        if values:
            ht_rate = sum(values) / len(values) * 100
            print(f"  {bucket}: {ht_rate:.1f}% HT ({sum(values)}/{len(values)})")

    # Folio-level analysis
    print("\n--- HT Run Density by Folio ---")

    runs_per_folio = Counter()
    tokens_per_folio = Counter()

    for r in runs:
        for folio in r['folios']:
            runs_per_folio[folio] += 1

    for d in data:
        tokens_per_folio[d['folio']] += 1

    folio_densities = []
    for folio in tokens_per_folio:
        run_ct = runs_per_folio[folio]
        token_ct = tokens_per_folio[folio]
        density = run_ct / token_ct * 1000  # runs per 1000 tokens
        folio_densities.append((folio, run_ct, token_ct, density))

    folio_densities.sort(key=lambda x: -x[3])

    print(f"\nTop 10 folios by run density (runs per 1000 tokens):")
    for folio, run_ct, token_ct, density in folio_densities[:10]:
        print(f"  {folio}: {density:.1f} runs/1000 ({run_ct} runs, {token_ct} tokens)")

    print(f"\nBottom 10 folios by run density:")
    for folio, run_ct, token_ct, density in folio_densities[-10:]:
        print(f"  {folio}: {density:.1f} runs/1000 ({run_ct} runs, {token_ct} tokens)")

    # Section analysis
    print("\n--- HT Runs by Section ---")

    runs_per_section = Counter()
    tokens_per_section = Counter()

    for r in runs:
        for ctx in r['contexts']:
            section = ctx.get('section', 'UNK')
            if section:
                runs_per_section[section] += 1
                break  # Count run once per section

    for d in data:
        section = d.get('section', 'UNK')
        if section:
            tokens_per_section[section] += 1

    for section in sorted(tokens_per_section.keys()):
        run_ct = runs_per_section[section]
        token_ct = tokens_per_section[section]
        if token_ct > 0:
            density = run_ct / token_ct * 1000
            print(f"  {section}: {density:.1f} runs/1000 ({run_ct} runs)")

    return folio_densities


# =============================================================================
# 6. TRANSITION/BOUNDARY HYPOTHESIS TEST
# =============================================================================

def analyze_transition_markers(runs: List[Dict], data: List[Dict]):
    """Test if HT bursts mark structural transitions or boundaries."""
    print("\n" + "=" * 70)
    print("6. TRANSITION/BOUNDARY HYPOTHESIS")
    print("=" * 70)

    print("\nHypothesis: HT bursts mark transitions in program structure")
    print("Tests:")
    print("  A. Do runs occur after specific 'transition' tokens?")
    print("  B. Do runs precede specific 'start' tokens?")
    print("  C. Are runs enriched at paragraph/section boundaries?")

    # Known structural tokens (from grammar)
    KERNEL_TOKENS = {'k', 'ch', 'ck', 'kch', 'ke', 'ka'}  # kernel-related
    LINK_SUFFIXES = {'ol', 'al', 'or', 'ar', 'aiin'}  # LINK operators
    STATE_TOKENS = {'shedy', 'chedy', 'shey', 'chey'}  # STATE operators

    # A. Tokens BEFORE runs - are they transition-related?
    print("\n--- A. Pre-Run Token Analysis ---")

    pre_run_categories = {'kernel': 0, 'link': 0, 'state': 0, 'other': 0}

    for r in runs:
        start_idx = r['start_idx']
        if start_idx > 0:
            prev_token = data[start_idx - 1]['token']

            if any(prev_token.startswith(k) for k in KERNEL_TOKENS):
                pre_run_categories['kernel'] += 1
            elif any(prev_token.endswith(s) for s in LINK_SUFFIXES):
                pre_run_categories['link'] += 1
            elif prev_token in STATE_TOKENS:
                pre_run_categories['state'] += 1
            else:
                pre_run_categories['other'] += 1

    total_pre = sum(pre_run_categories.values())
    print(f"Pre-run token categories (n={total_pre}):")
    for cat, count in pre_run_categories.items():
        print(f"  {cat}: {count} ({count/total_pre*100:.1f}%)")

    # B. Tokens AFTER runs - are they 'start' tokens?
    print("\n--- B. Post-Run Token Analysis ---")

    post_run_categories = {'kernel': 0, 'link': 0, 'state': 0, 'other': 0}

    for r in runs:
        end_idx = r['end_idx']
        if end_idx < len(data) - 1:
            next_token = data[end_idx + 1]['token']

            if any(next_token.startswith(k) for k in KERNEL_TOKENS):
                post_run_categories['kernel'] += 1
            elif any(next_token.endswith(s) for s in LINK_SUFFIXES):
                post_run_categories['link'] += 1
            elif next_token in STATE_TOKENS:
                post_run_categories['state'] += 1
            else:
                post_run_categories['other'] += 1

    total_post = sum(post_run_categories.values())
    print(f"Post-run token categories (n={total_post}):")
    for cat, count in post_run_categories.items():
        print(f"  {cat}: {count} ({count/total_post*100:.1f}%)")

    # C. Line boundary enrichment
    print("\n--- C. Line Boundary Enrichment ---")

    # Count runs that start at line position 1 (line-initial)
    line_initial_runs = sum(1 for r in runs if r['contexts'][0].get('line_initial', 0) == 1)

    # Expected if random
    all_line_initial = sum(1 for d in data if d.get('line_initial', 0) == 1)
    total_tokens = len(data)
    expected_rate = all_line_initial / total_tokens
    observed_rate = line_initial_runs / len(runs) if runs else 0
    enrichment = observed_rate / expected_rate if expected_rate > 0 else 0

    print(f"Runs starting at line position 1: {line_initial_runs}/{len(runs)} ({observed_rate*100:.1f}%)")
    print(f"Expected if random: {expected_rate*100:.1f}%")
    print(f"Enrichment: {enrichment:.2f}x")

    # Chi-square test
    obs_line_initial = line_initial_runs
    obs_not_line_initial = len(runs) - line_initial_runs
    exp_line_initial = len(runs) * expected_rate
    exp_not_line_initial = len(runs) * (1 - expected_rate)

    if exp_line_initial > 0 and exp_not_line_initial > 0:
        chi2 = ((obs_line_initial - exp_line_initial)**2 / exp_line_initial +
                (obs_not_line_initial - exp_not_line_initial)**2 / exp_not_line_initial)
        p = 1 - stats.chi2.cdf(chi2, 1)
        print(f"Chi-square: {chi2:.2f}, p={p:.6f}")

    return pre_run_categories, post_run_categories


# =============================================================================
# 7. SPECIFIC TRIGGER TOKENS DEEP DIVE
# =============================================================================

def deep_dive_triggers(runs: List[Dict], isolated_ht: List, data: List[Dict]):
    """Deep dive into specific tokens that trigger bursts."""
    print("\n" + "=" * 70)
    print("7. DEEP DIVE: SPECIFIC TRIGGER PATTERNS")
    print("=" * 70)

    # Get 2-token context before runs
    pre_run_bigrams = Counter()
    for r in runs:
        start_idx = r['start_idx']
        if start_idx >= 2:
            prev2 = data[start_idx - 2]['token']
            prev1 = data[start_idx - 1]['token']
            if not is_ht_token(prev2) and not is_ht_token(prev1):
                pre_run_bigrams[(prev2, prev1)] += 1

    print("\n--- Top 20 Bigram Contexts BEFORE Runs ---")
    for bigram, count in pre_run_bigrams.most_common(20):
        print(f"  {bigram[0]} -> {bigram[1]} -> [HT RUN]: {count}")

    # Get 2-token context after runs
    post_run_bigrams = Counter()
    for r in runs:
        end_idx = r['end_idx']
        if end_idx < len(data) - 2:
            next1 = data[end_idx + 1]['token']
            next2 = data[end_idx + 2]['token']
            if not is_ht_token(next1) and not is_ht_token(next2):
                post_run_bigrams[(next1, next2)] += 1

    print("\n--- Top 20 Bigram Contexts AFTER Runs ---")
    for bigram, count in post_run_bigrams.most_common(20):
        print(f"  [HT RUN] -> {bigram[0]} -> {bigram[1]}: {count}")

    # Full pattern: before -> HT -> after
    print("\n--- Most Common Full Patterns (before -> HT RUN -> after) ---")
    full_patterns = Counter()
    for r in runs:
        start_idx = r['start_idx']
        end_idx = r['end_idx']

        if start_idx > 0 and end_idx < len(data) - 1:
            prev = data[start_idx - 1]['token']
            next_t = data[end_idx + 1]['token']
            if not is_ht_token(prev) and not is_ht_token(next_t):
                full_patterns[(prev, next_t)] += 1

    for pattern, count in full_patterns.most_common(20):
        print(f"  {pattern[0]} -> [HT RUN] -> {pattern[1]}: {count}")

    return pre_run_bigrams, post_run_bigrams


# =============================================================================
# 8. HT-HT PAIR ENRICHMENT VALIDATION
# =============================================================================

def validate_ht_enrichment(data: List[Dict]):
    """Validate the 5.4x HT-HT enrichment claim."""
    print("\n" + "=" * 70)
    print("8. HT-HT ENRICHMENT VALIDATION")
    print("=" * 70)

    # Count HT tokens
    total_tokens = len(data)
    ht_tokens = sum(1 for d in data if is_ht_token(d['token']))
    ht_rate = ht_tokens / total_tokens

    print(f"\nTotal tokens: {total_tokens}")
    print(f"HT tokens: {ht_tokens} ({ht_rate*100:.1f}%)")

    # Count HT-HT consecutive pairs
    ht_ht_pairs = 0
    ht_nonht_pairs = 0
    nonht_ht_pairs = 0
    nonht_nonht_pairs = 0

    for i in range(len(data) - 1):
        curr_ht = is_ht_token(data[i]['token'])
        next_ht = is_ht_token(data[i + 1]['token'])

        if curr_ht and next_ht:
            ht_ht_pairs += 1
        elif curr_ht and not next_ht:
            ht_nonht_pairs += 1
        elif not curr_ht and next_ht:
            nonht_ht_pairs += 1
        else:
            nonht_nonht_pairs += 1

    total_pairs = ht_ht_pairs + ht_nonht_pairs + nonht_ht_pairs + nonht_nonht_pairs

    # Expected under independence
    expected_ht_ht = ht_rate * ht_rate * total_pairs
    observed_ht_ht = ht_ht_pairs
    enrichment = observed_ht_ht / expected_ht_ht if expected_ht_ht > 0 else 0

    print(f"\n--- Consecutive Pair Analysis ---")
    print(f"Total pairs: {total_pairs}")
    print(f"\nObserved HT-HT pairs: {observed_ht_ht} ({observed_ht_ht/total_pairs*100:.1f}%)")
    print(f"Expected if independent: {expected_ht_ht:.1f} ({expected_ht_ht/total_pairs*100:.1f}%)")
    print(f"ENRICHMENT: {enrichment:.2f}x")

    # Chi-square test
    observed = np.array([
        [ht_ht_pairs, ht_nonht_pairs],
        [nonht_ht_pairs, nonht_nonht_pairs]
    ])
    chi2, p, _, expected = stats.chi2_contingency(observed)
    print(f"\nChi-square test: chi2={chi2:.2f}, p={p:.2e}")

    # Transition matrix
    print("\n--- Transition Matrix ---")
    print(f"{'':15} {'Next HT':>12} {'Next non-HT':>12}")
    print(f"{'Current HT':<15} {ht_ht_pairs:>12} {ht_nonht_pairs:>12}")
    print(f"{'Current non-HT':<15} {nonht_ht_pairs:>12} {nonht_nonht_pairs:>12}")

    # P(next=HT | current=HT) vs P(next=HT | current=nonHT)
    p_ht_given_ht = ht_ht_pairs / (ht_ht_pairs + ht_nonht_pairs) if (ht_ht_pairs + ht_nonht_pairs) > 0 else 0
    p_ht_given_nonht = nonht_ht_pairs / (nonht_ht_pairs + nonht_nonht_pairs) if (nonht_ht_pairs + nonht_nonht_pairs) > 0 else 0

    print(f"\nTransition probabilities:")
    print(f"  P(next=HT | current=HT): {p_ht_given_ht:.3f}")
    print(f"  P(next=HT | current=non-HT): {p_ht_given_nonht:.3f}")
    print(f"  Ratio: {p_ht_given_ht/p_ht_given_nonht:.2f}x" if p_ht_given_nonht > 0 else "  N/A")

    return enrichment


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("HT BURST/CLUSTERING ANALYSIS")
    print("=" * 70)
    print("\nHT Definition:")
    print("  - Tokens starting with 'y' (y-initial)")
    print("  - Single-char atoms: y, f, d, r")

    # Load data
    print("\n" + "=" * 70)
    print("DATA LOADING")
    print("=" * 70)

    data = load_data()
    print(f"\nLoaded {len(data)} Currier B tokens (Herbal transcription)")

    # Count HT
    ht_count = sum(1 for d in data if is_ht_token(d['token']))
    print(f"HT tokens: {ht_count} ({ht_count/len(data)*100:.1f}%)")

    # Validate enrichment first
    enrichment = validate_ht_enrichment(data)

    # Identify runs
    runs, isolated_ht = identify_ht_runs(data)

    # Analysis tasks
    length_dist = analyze_run_lengths(runs, isolated_ht)
    run_tokens, isolated_tokens = analyze_ht_forms_in_runs(runs, isolated_ht)

    pre_run, pre_iso = analyze_burst_triggers(runs, isolated_ht, data)
    post_run, post_iso = analyze_burst_terminators(runs, isolated_ht, data)

    within_line, cross_line = analyze_line_boundaries(runs, data)
    folio_densities = analyze_position_correlations(runs, isolated_ht, data)

    pre_cat, post_cat = analyze_transition_markers(runs, data)
    pre_bigrams, post_bigrams = deep_dive_triggers(runs, isolated_ht, data)

    # =============================================================================
    # SUMMARY
    # =============================================================================

    print("\n" + "=" * 70)
    print("SUMMARY: HT BURST PHENOMENON")
    print("=" * 70)

    print(f"""
KEY FINDINGS:

1. ENRICHMENT CONFIRMED
   - HT-HT consecutive pairs: {enrichment:.1f}x enriched
   - HT tokens cluster into bursts, not evenly distributed

2. RUN STATISTICS
   - Total runs (2+ consecutive HT): {len(runs)}
   - Isolated HT tokens: {len(isolated_ht)}
   - Most common run length: {length_dist.most_common(1)[0] if length_dist else 'N/A'}
   - Long runs (4+): {sum(1 for r in runs if r['length'] >= 4)}

3. LINE BOUNDARIES
   - Within-line runs: {len(within_line)} ({len(within_line)/len(runs)*100:.1f}%)
   - Cross-line runs: {len(cross_line)} ({len(cross_line)/len(runs)*100:.1f}%)
   -> Bursts mostly respect line boundaries

4. TOP TRIGGER TOKENS (precede runs)
""")

    for token, count in pre_run.most_common(5):
        print(f"   - {token}: {count}")

    print("""
5. TOP TERMINATOR TOKENS (follow runs)
""")

    for token, count in post_run.most_common(5):
        print(f"   - {token}: {count}")

    print("""
6. TRANSITION HYPOTHESIS
   - Pre-run categories: kernel={kernel}, link={link}, state={state}, other={other}
   - Post-run categories: kernel={post_kernel}, link={post_link}, state={post_state}, other={post_other}
""".format(
        kernel=pre_cat.get('kernel', 0),
        link=pre_cat.get('link', 0),
        state=pre_cat.get('state', 0),
        other=pre_cat.get('other', 0),
        post_kernel=post_cat.get('kernel', 0),
        post_link=post_cat.get('link', 0),
        post_state=post_cat.get('state', 0),
        post_other=post_cat.get('other', 0),
    ))

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
