"""
HTCS Hygiene Check

Test whether HTCS coordinate semantics findings are affected by token filtering.

Key HTCS claims:
- 1163 frequent human-track tokens analyzed
- 124 tokens concentrated at section start (CF-1)
- 126 tokens concentrated at section end (CF-2)
- 1158 tokens show >50% LINK proximity (CF-3)
- 41 tokens show run-forming behavior (CF-5)

Hygiene question: Are these counts inflated by noise tokens?
"""

from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

project_root = Path(__file__).parent.parent.parent

# Grammar patterns (from SID-04)
GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

# Hazard tokens (should NOT be counted as human-track)
HAZARD_TOKENS = {
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    'dar', 'qokaiin', 'qokedy'
}

# High-frequency operational tokens
OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol', 's', 'o', 'd', 'y',
    'a', 'e', 'l', 'r', 'k', 'h', 'c', 't', 'n', 'p', 'm', 'g', 'f',
    'dain', 'chain', 'shain', 'ain', 'in', 'an', 'dan',
}


def is_grammar_token(token):
    """Original classification."""
    t = token.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def is_human_track_original(token, freq):
    """Original HTCS filter: not grammar, low frequency."""
    if is_grammar_token(token):
        return False
    if freq > 0.001:  # High frequency = operational
        return False
    return True


def is_human_track_strict(token, freq):
    """Strict filter: additional hygiene checks."""
    t = token.lower().strip()

    # Filter: empty or very short
    if len(t) < 2:
        return False

    # Filter: non-alpha
    if not t.isalpha():
        return False

    # Filter: hazard tokens
    if t in HAZARD_TOKENS:
        return False

    # Filter: operational tokens
    if t in OPERATIONAL_TOKENS:
        return False

    # Filter: grammar tokens
    if is_grammar_token(t):
        return False

    # Filter: high frequency
    if freq > 0.001:
        return False

    return True


def load_data():
    """Load transcription with section info."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []
    section_tokens = defaultdict(list)

    with open(filepath, 'r', encoding='utf-8') as f:
        f.readline()  # skip header
        for line_num, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                # H-only transcriber filter (CRITICAL: avoids 3.2x token inflation)
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                word = parts[0].strip('"').strip()
                section = parts[3].strip('"') if len(parts) > 3 else ''

                if word and word.isalpha():
                    data.append({
                        'token': word,
                        'section': section,
                        'line_num': line_num
                    })
                    section_tokens[section].append({
                        'token': word,
                        'position': len(section_tokens[section])
                    })

    return data, section_tokens


def compute_htcs_stats(data, section_tokens, is_ht_func):
    """Compute key HTCS statistics."""

    # Count tokens
    token_counts = Counter(d['token'] for d in data)
    total_tokens = len(data)

    # Identify human-track tokens
    ht_tokens = set()
    for token, count in token_counts.items():
        freq = count / total_tokens
        if is_ht_func(token, freq):
            ht_tokens.add(token)

    # Compute section position statistics
    early_tokens = []  # >40% in first 20%
    late_tokens = []   # >40% in last 20%

    for token in ht_tokens:
        early_count = 0
        late_count = 0
        total_count = 0

        for section, tokens in section_tokens.items():
            section_len = len(tokens)
            if section_len < 10:
                continue

            for i, t in enumerate(tokens):
                if t['token'] == token:
                    total_count += 1
                    rel_pos = i / section_len
                    if rel_pos < 0.2:
                        early_count += 1
                    elif rel_pos > 0.8:
                        late_count += 1

        if total_count >= 3:  # Minimum occurrences
            early_rate = early_count / total_count
            late_rate = late_count / total_count

            if early_rate > 0.4:
                early_tokens.append(token)
            if late_rate > 0.4:
                late_tokens.append(token)

    # Compute run statistics
    run_forming = []
    for section, tokens in section_tokens.items():
        i = 0
        while i < len(tokens):
            token = tokens[i]['token']
            if token in ht_tokens:
                run_len = 1
                while i + run_len < len(tokens) and tokens[i + run_len]['token'] == token:
                    run_len += 1
                if run_len >= 3:
                    run_forming.append(token)
                i += run_len
            else:
                i += 1

    run_forming = set(run_forming)

    return {
        'total_ht_tokens': len(ht_tokens),
        'section_early': len(early_tokens),
        'section_late': len(late_tokens),
        'run_forming': len(run_forming),
        'sample_ht': list(ht_tokens)[:10],
        'sample_early': early_tokens[:5],
        'sample_late': late_tokens[:5],
    }


def main():
    print("HTCS Hygiene Check")
    print("=" * 60)

    data, section_tokens = load_data()
    print(f"Loaded {len(data)} tokens across {len(section_tokens)} sections\n")

    # Token frequency distribution
    token_counts = Counter(d['token'] for d in data)
    total = len(data)

    # Original classification
    print("ORIGINAL CLASSIFICATION:")
    stats_orig = compute_htcs_stats(
        data, section_tokens,
        lambda t, f: is_human_track_original(t, f)
    )
    print(f"  Human-track tokens: {stats_orig['total_ht_tokens']}")
    print(f"  Section-early (CF-1): {stats_orig['section_early']}")
    print(f"  Section-late (CF-2): {stats_orig['section_late']}")
    print(f"  Run-forming (CF-5): {stats_orig['run_forming']}")
    print(f"  Sample HT: {stats_orig['sample_ht'][:5]}")

    # Strict classification
    print("\nSTRICT CLASSIFICATION:")
    stats_strict = compute_htcs_stats(
        data, section_tokens,
        lambda t, f: is_human_track_strict(t, f)
    )
    print(f"  Human-track tokens: {stats_strict['total_ht_tokens']}")
    print(f"  Section-early (CF-1): {stats_strict['section_early']}")
    print(f"  Section-late (CF-2): {stats_strict['section_late']}")
    print(f"  Run-forming (CF-5): {stats_strict['run_forming']}")
    print(f"  Sample HT: {stats_strict['sample_ht'][:5]}")

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)

    def pct_change(old, new):
        if old == 0:
            return "N/A"
        return f"{(new - old) / old * 100:+.1f}%"

    print(f"""
| Metric          | Original | Strict | Change    |
|-----------------|----------|--------|-----------|
| HT tokens       | {stats_orig['total_ht_tokens']}     | {stats_strict['total_ht_tokens']}    | {pct_change(stats_orig['total_ht_tokens'], stats_strict['total_ht_tokens'])} |
| Section-early   | {stats_orig['section_early']}      | {stats_strict['section_early']}     | {pct_change(stats_orig['section_early'], stats_strict['section_early'])} |
| Section-late    | {stats_orig['section_late']}      | {stats_strict['section_late']}     | {pct_change(stats_orig['section_late'], stats_strict['section_late'])} |
| Run-forming     | {stats_orig['run_forming']}        | {stats_strict['run_forming']}       | {pct_change(stats_orig['run_forming'], stats_strict['run_forming'])} |
""")

    # Check what was filtered
    print("=" * 60)
    print("FILTERED TOKENS ANALYSIS")
    print("=" * 60)

    # What passes original but not strict?
    filtered_out = []
    for token in stats_orig['sample_ht']:
        freq = token_counts[token] / total
        if is_human_track_original(token, freq) and not is_human_track_strict(token, freq):
            reason = []
            if len(token) < 2:
                reason.append("too_short")
            if not token.isalpha():
                reason.append("non_alpha")
            if token in HAZARD_TOKENS:
                reason.append("hazard_token")
            if token in OPERATIONAL_TOKENS:
                reason.append("operational")
            filtered_out.append((token, reason))

    if filtered_out:
        print("\nTokens filtered by strict rules:")
        for token, reasons in filtered_out:
            print(f"  '{token}': {', '.join(reasons)}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    changes = [
        abs((stats_strict['total_ht_tokens'] - stats_orig['total_ht_tokens']) / stats_orig['total_ht_tokens'] * 100) if stats_orig['total_ht_tokens'] else 0,
        abs((stats_strict['section_early'] - stats_orig['section_early']) / stats_orig['section_early'] * 100) if stats_orig['section_early'] else 0,
        abs((stats_strict['section_late'] - stats_orig['section_late']) / stats_orig['section_late'] * 100) if stats_orig['section_late'] else 0,
    ]
    max_change = max(changes)

    if max_change < 20:
        print(f"\n** RESULTS STABLE ** (max change: {max_change:.1f}%)")
        print("HTCS findings are ROBUST to hygiene filtering.")
    elif max_change < 50:
        print(f"\n** MODERATE CHANGES ** (max change: {max_change:.1f}%)")
        print("HTCS findings show moderate sensitivity to token filtering.")
    else:
        print(f"\n** SIGNIFICANT CHANGES ** (max change: {max_change:.1f}%)")
        print("HTCS findings AFFECTED by token filtering. Review recommended.")


if __name__ == '__main__':
    main()
