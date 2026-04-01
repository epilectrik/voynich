#!/usr/bin/env python3
"""
s2_id_swap_analysis.py — Analyze i/d MOD atom swap between zodiac seasons.

Summer/Winter zodiac folios are i-dominant (iterate) while Spring/Autumn
are d-dominant (mark/close). This script investigates HOW the swap manifests.

Analyses:
  1. Token-level i/d classification rates per season and folio
  2. HEAD+i vs HEAD+d compound frequencies per season
  3. Most common words containing i vs d per season
  4. i/d co-occurrence within tokens
  5. Positional ordering (i before d, or d before i)
  6. i_depth and d_depth (consecutive runs)
  7. Token length comparison (i-tokens vs d-tokens)
  8. Currier B baseline comparison
"""

import sys
import os
import io
import json
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../..')

from scripts.voynich import Transcript, Morphology

# ── Season definitions ──
SEASONS = {
    'Spring': ['f70v1', 'f70v2', 'f71r'],
    'Summer': ['f72r2', 'f72r3', 'f72v1'],
    'Autumn': ['f72v2', 'f72v3', 'f73r'],
    'Winter': ['f71v', 'f72r1', 'f73v'],
}

SEASON_ORDER = ['Spring', 'Summer', 'Autumn', 'Winter']
ALL_ZODIAC_FOLIOS = [f for s in SEASON_ORDER for f in SEASONS[s]]

# Reverse lookup: folio -> season
FOLIO_SEASON = {}
for season, folios in SEASONS.items():
    for f in folios:
        FOLIO_SEASON[f] = season


def get_zodiac_tokens(tx):
    """Get H-track, non-label, non-empty, non-uncertain tokens from zodiac folios."""
    tokens = []
    for token in tx.all(h_only=True):
        if token.folio not in FOLIO_SEASON:
            continue
        if token.placement and token.placement.startswith('L'):
            continue
        if not token.word or token.word.strip() == '':
            continue
        if '*' in token.word:
            continue
        tokens.append(token)
    return tokens


def classify_token_atoms(morph, word):
    """Atomize a word and extract i/d info."""
    a = morph.atomize(word)
    atom_chars = [ch for ch, role, gloss in a.atoms]
    has_i = 'i' in atom_chars
    has_d = 'd' in atom_chars

    # HEAD atom (first HEAD-role atom)
    head = a.head

    # Positions of i and d
    i_positions = [idx for idx, ch in enumerate(atom_chars) if ch == 'i']
    d_positions = [idx for idx, ch in enumerate(atom_chars) if ch == 'd']

    # Consecutive i_depth and d_depth (max consecutive run)
    def max_consecutive(chars, target):
        max_run = 0
        run = 0
        for c in chars:
            if c == target:
                run += 1
                max_run = max(max_run, run)
            else:
                run = 0
        return max_run

    i_depth = max_consecutive(atom_chars, 'i')
    d_depth = max_consecutive(atom_chars, 'd')

    return {
        'has_i': has_i,
        'has_d': has_d,
        'has_both': has_i and has_d,
        'has_neither': not has_i and not has_d,
        'head': head,
        'atom_chars': atom_chars,
        'atom_count': len(atom_chars),
        'i_positions': i_positions,
        'd_positions': d_positions,
        'i_depth': i_depth,
        'd_depth': d_depth,
    }


def main():
    tx = Transcript()
    morph = Morphology()

    # ── Collect zodiac token data ──
    zodiac_tokens = get_zodiac_tokens(tx)
    print(f"Total zodiac tokens (H-track, no labels, no uncertain): {len(zodiac_tokens)}")
    print()

    # Pre-compute atom info for each token
    token_data = []
    for tok in zodiac_tokens:
        info = classify_token_atoms(morph, tok.word)
        info['word'] = tok.word
        info['folio'] = tok.folio
        info['season'] = FOLIO_SEASON[tok.folio]
        token_data.append(info)

    # ══════════════════════════════════════════════════════════════
    # 1. TOKEN-LEVEL i/d CLASSIFICATION
    # ══════════════════════════════════════════════════════════════
    print("=" * 70)
    print("1. TOKEN-LEVEL i/d CLASSIFICATION")
    print("=" * 70)

    # Per season
    season_counts = defaultdict(lambda: {'total': 0, 'i_only': 0, 'd_only': 0, 'both': 0, 'neither': 0})
    folio_counts = defaultdict(lambda: {'total': 0, 'i_only': 0, 'd_only': 0, 'both': 0, 'neither': 0})

    for td in token_data:
        s = td['season']
        f = td['folio']
        for bucket in [season_counts[s], folio_counts[f]]:
            bucket['total'] += 1
            if td['has_both']:
                bucket['both'] += 1
            elif td['has_i']:
                bucket['i_only'] += 1
            elif td['has_d']:
                bucket['d_only'] += 1
            else:
                bucket['neither'] += 1

    print(f"\n{'Season':<10} {'Total':>6} {'i-only':>8} {'d-only':>8} {'both':>8} {'neither':>8} {'i-rate':>8} {'d-rate':>8}")
    print("-" * 70)
    season_results = {}
    for s in SEASON_ORDER:
        c = season_counts[s]
        i_rate = (c['i_only'] + c['both']) / c['total'] if c['total'] else 0
        d_rate = (c['d_only'] + c['both']) / c['total'] if c['total'] else 0
        print(f"{s:<10} {c['total']:>6} {c['i_only']:>8} {c['d_only']:>8} {c['both']:>8} {c['neither']:>8} {i_rate:>8.3f} {d_rate:>8.3f}")
        season_results[s] = {
            'total': c['total'],
            'i_only': c['i_only'],
            'd_only': c['d_only'],
            'both': c['both'],
            'neither': c['neither'],
            'i_rate': round(i_rate, 4),
            'd_rate': round(d_rate, 4),
        }

    print(f"\n{'Folio':<10} {'Season':<10} {'Total':>6} {'i-only':>8} {'d-only':>8} {'both':>8} {'neither':>8} {'i-rate':>8} {'d-rate':>8}")
    print("-" * 78)
    folio_results = {}
    for f in ALL_ZODIAC_FOLIOS:
        c = folio_counts[f]
        s = FOLIO_SEASON[f]
        i_rate = (c['i_only'] + c['both']) / c['total'] if c['total'] else 0
        d_rate = (c['d_only'] + c['both']) / c['total'] if c['total'] else 0
        print(f"{f:<10} {s:<10} {c['total']:>6} {c['i_only']:>8} {c['d_only']:>8} {c['both']:>8} {c['neither']:>8} {i_rate:>8.3f} {d_rate:>8.3f}")
        folio_results[f] = {
            'season': s,
            'total': c['total'],
            'i_only': c['i_only'],
            'd_only': c['d_only'],
            'both': c['both'],
            'neither': c['neither'],
            'i_rate': round(i_rate, 4),
            'd_rate': round(d_rate, 4),
        }

    # ══════════════════════════════════════════════════════════════
    # 2. HEAD+i vs HEAD+d COMPOUNDS
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("2. HEAD+i vs HEAD+d COMPOUND FREQUENCIES BY SEASON")
    print("=" * 70)

    # Count (HEAD, has_i, has_d) per season
    head_id_season = defaultdict(Counter)
    for td in token_data:
        if td['head'] is not None:
            key = td['head']
            if td['has_i']:
                head_id_season[td['season']][(key, 'i')] += 1
            if td['has_d']:
                head_id_season[td['season']][(key, 'd')] += 1

    heads_seen = sorted(set(td['head'] for td in token_data if td['head'] is not None))
    head_id_results = {}
    for s in SEASON_ORDER:
        print(f"\n  {s}:")
        print(f"    {'HEAD':>6} {'with_i':>8} {'with_d':>8} {'i/d ratio':>10}")
        print(f"    {'-'*36}")
        head_id_results[s] = {}
        for h in heads_seen:
            wi = head_id_season[s].get((h, 'i'), 0)
            wd = head_id_season[s].get((h, 'd'), 0)
            ratio = f"{wi/wd:.2f}" if wd > 0 else ("inf" if wi > 0 else "n/a")
            print(f"    {h:>6} {wi:>8} {wd:>8} {ratio:>10}")
            head_id_results[s][h] = {'with_i': wi, 'with_d': wd}

    # ══════════════════════════════════════════════════════════════
    # 3. MOST COMMON WORDS WITH i vs d PER SEASON
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("3. MOST COMMON WORDS CONTAINING i vs d BY SEASON")
    print("=" * 70)

    TOP_N = 15
    word_i_season = defaultdict(Counter)
    word_d_season = defaultdict(Counter)
    for td in token_data:
        if td['has_i']:
            word_i_season[td['season']][td['word']] += 1
        if td['has_d']:
            word_d_season[td['season']][td['word']] += 1

    top_words_results = {}
    for s in SEASON_ORDER:
        print(f"\n  {s} — Top {TOP_N} i-words:")
        top_i = word_i_season[s].most_common(TOP_N)
        for w, cnt in top_i:
            print(f"    {w:<20} {cnt:>4}")

        print(f"  {s} — Top {TOP_N} d-words:")
        top_d = word_d_season[s].most_common(TOP_N)
        for w, cnt in top_d:
            print(f"    {w:<20} {cnt:>4}")

        top_words_results[s] = {
            'top_i_words': [(w, c) for w, c in top_i],
            'top_d_words': [(w, c) for w, c in top_d],
        }

    # ══════════════════════════════════════════════════════════════
    # 4. i/d CO-OCCURRENCE
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("4. i/d CO-OCCURRENCE WITHIN TOKENS")
    print("=" * 70)

    print(f"\n{'Season':<10} {'i-or-d':>8} {'both':>8} {'co-occ%':>10}")
    print("-" * 40)
    cooccurrence_results = {}
    for s in SEASON_ORDER:
        c = season_counts[s]
        i_or_d = c['i_only'] + c['d_only'] + c['both']
        co_rate = c['both'] / i_or_d if i_or_d > 0 else 0
        print(f"{s:<10} {i_or_d:>8} {c['both']:>8} {co_rate:>10.3f}")
        cooccurrence_results[s] = {
            'tokens_with_i_or_d': i_or_d,
            'tokens_with_both': c['both'],
            'co_occurrence_rate': round(co_rate, 4),
        }

    # ══════════════════════════════════════════════════════════════
    # 5. POSITIONAL ORDERING (i before d or d before i)
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("5. POSITIONAL ORDERING IN TOKENS WITH BOTH i AND d")
    print("=" * 70)

    ordering_season = defaultdict(lambda: {'i_before_d': 0, 'd_before_i': 0, 'interleaved': 0})
    for td in token_data:
        if td['has_both']:
            first_i = td['i_positions'][0]
            first_d = td['d_positions'][0]
            if first_i < first_d:
                ordering_season[td['season']]['i_before_d'] += 1
            elif first_d < first_i:
                ordering_season[td['season']]['d_before_i'] += 1
            else:
                ordering_season[td['season']]['interleaved'] += 1

    print(f"\n{'Season':<10} {'i->d':>8} {'d->i':>8} {'same-pos':>8}")
    print("-" * 38)
    ordering_results = {}
    for s in SEASON_ORDER:
        o = ordering_season[s]
        print(f"{s:<10} {o['i_before_d']:>8} {o['d_before_i']:>8} {o['interleaved']:>8}")
        ordering_results[s] = dict(o)

    # Example tokens with both
    print("\n  Example tokens with both i and d:")
    shown = set()
    for td in token_data:
        if td['has_both'] and td['word'] not in shown:
            print(f"    {td['word']:<20} atoms: {''.join(td['atom_chars']):<12} season: {td['season']}")
            shown.add(td['word'])
            if len(shown) >= 20:
                break

    # ══════════════════════════════════════════════════════════════
    # 6. i_depth AND d_depth
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("6. i_depth AND d_depth (MAX CONSECUTIVE RUNS)")
    print("=" * 70)

    depth_season = defaultdict(lambda: {'i_depths': [], 'd_depths': []})
    for td in token_data:
        s = td['season']
        if td['has_i']:
            depth_season[s]['i_depths'].append(td['i_depth'])
        if td['has_d']:
            depth_season[s]['d_depths'].append(td['d_depth'])

    print(f"\n{'Season':<10} {'mean_i_dep':>11} {'max_i_dep':>10} {'mean_d_dep':>11} {'max_d_dep':>10} {'n_i':>6} {'n_d':>6}")
    print("-" * 68)
    depth_results = {}
    for s in SEASON_ORDER:
        dd = depth_season[s]
        mean_i = sum(dd['i_depths']) / len(dd['i_depths']) if dd['i_depths'] else 0
        max_i = max(dd['i_depths']) if dd['i_depths'] else 0
        mean_d = sum(dd['d_depths']) / len(dd['d_depths']) if dd['d_depths'] else 0
        max_d = max(dd['d_depths']) if dd['d_depths'] else 0
        print(f"{s:<10} {mean_i:>11.3f} {max_i:>10} {mean_d:>11.3f} {max_d:>10} {len(dd['i_depths']):>6} {len(dd['d_depths']):>6}")
        depth_results[s] = {
            'mean_i_depth': round(mean_i, 4),
            'max_i_depth': max_i,
            'mean_d_depth': round(mean_d, 4),
            'max_d_depth': max_d,
            'n_i_tokens': len(dd['i_depths']),
            'n_d_tokens': len(dd['d_depths']),
        }

    # Distribution of i_depth values
    print("\n  i_depth distribution:")
    for s in SEASON_ORDER:
        dist = Counter(depth_season[s]['i_depths'])
        print(f"    {s}: {dict(sorted(dist.items()))}")
    print("\n  d_depth distribution:")
    for s in SEASON_ORDER:
        dist = Counter(depth_season[s]['d_depths'])
        print(f"    {s}: {dict(sorted(dist.items()))}")

    # ══════════════════════════════════════════════════════════════
    # 7. TOKEN LENGTH COMPARISON
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("7. TOKEN LENGTH (ATOM COUNT) FOR i-TOKENS vs d-TOKENS")
    print("=" * 70)

    length_season = defaultdict(lambda: {'i_lengths': [], 'd_lengths': [], 'neither_lengths': []})
    for td in token_data:
        s = td['season']
        if td['has_i']:
            length_season[s]['i_lengths'].append(td['atom_count'])
        if td['has_d']:
            length_season[s]['d_lengths'].append(td['atom_count'])
        if td['has_neither']:
            length_season[s]['neither_lengths'].append(td['atom_count'])

    print(f"\n{'Season':<10} {'mean_i_len':>11} {'mean_d_len':>11} {'mean_neith':>11}")
    print("-" * 48)
    length_results = {}
    for s in SEASON_ORDER:
        ll = length_season[s]
        mean_i = sum(ll['i_lengths']) / len(ll['i_lengths']) if ll['i_lengths'] else 0
        mean_d = sum(ll['d_lengths']) / len(ll['d_lengths']) if ll['d_lengths'] else 0
        mean_n = sum(ll['neither_lengths']) / len(ll['neither_lengths']) if ll['neither_lengths'] else 0
        print(f"{s:<10} {mean_i:>11.3f} {mean_d:>11.3f} {mean_n:>11.3f}")
        length_results[s] = {
            'mean_i_token_atoms': round(mean_i, 4),
            'mean_d_token_atoms': round(mean_d, 4),
            'mean_neither_token_atoms': round(mean_n, 4),
        }

    # ══════════════════════════════════════════════════════════════
    # 8. CURRIER B BASELINE
    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("8. CURRIER B BASELINE COMPARISON")
    print("=" * 70)

    b_total = 0
    b_i = 0
    b_d = 0
    b_both = 0
    b_neither = 0
    for tok in tx.currier_b():
        info = classify_token_atoms(morph, tok.word)
        b_total += 1
        if info['has_both']:
            b_both += 1
        elif info['has_i']:
            b_i += 1
        elif info['has_d']:
            b_d += 1
        else:
            b_neither += 1

    b_i_rate = (b_i + b_both) / b_total if b_total else 0
    b_d_rate = (b_d + b_both) / b_total if b_total else 0
    print(f"\n  Currier B tokens: {b_total}")
    print(f"  i-only: {b_i}, d-only: {b_d}, both: {b_both}, neither: {b_neither}")
    print(f"  i-rate: {b_i_rate:.4f}, d-rate: {b_d_rate:.4f}")

    b_baseline = {
        'total': b_total,
        'i_only': b_i,
        'd_only': b_d,
        'both': b_both,
        'neither': b_neither,
        'i_rate': round(b_i_rate, 4),
        'd_rate': round(b_d_rate, 4),
    }

    print(f"\n  Season comparison to B baseline:")
    print(f"  {'Season':<10} {'i-rate':>8} {'d-rate':>8} {'i-vs-B':>10} {'d-vs-B':>10}")
    print(f"  {'-'*50}")
    for s in SEASON_ORDER:
        sr = season_results[s]
        i_diff = sr['i_rate'] - b_i_rate
        d_diff = sr['d_rate'] - b_d_rate
        print(f"  {s:<10} {sr['i_rate']:>8.4f} {sr['d_rate']:>8.4f} {i_diff:>+10.4f} {d_diff:>+10.4f}")

    # ══════════════════════════════════════════════════════════════
    # SAVE JSON
    # ══════════════════════════════════════════════════════════════
    output = {
        'description': 'i/d MOD atom swap analysis across zodiac seasons',
        'season_definitions': SEASONS,
        'token_level_classification': {
            'by_season': season_results,
            'by_folio': folio_results,
        },
        'head_id_compounds': head_id_results,
        'top_words': top_words_results,
        'co_occurrence': cooccurrence_results,
        'positional_ordering': ordering_results,
        'depth_analysis': depth_results,
        'token_length': length_results,
        'currier_b_baseline': b_baseline,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 's2_id_swap_analysis.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {os.path.abspath(out_path)}")


if __name__ == '__main__':
    main()
