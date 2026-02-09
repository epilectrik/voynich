#!/usr/bin/env python3
"""
Systematic analysis of what distinguishes paragraphs within a folio.
"""

import sys
from pathlib import Path
from collections import defaultdict
import json

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

# Load class map for role analysis
class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_class = {t: int(c) for t, c in class_data['token_to_class'].items()}
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()

GALLOWS = {'k', 't', 'p', 'f'}

# Build line-grouped tokens per folio
folio_line_tokens = defaultdict(lambda: defaultdict(list))
for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_line_tokens[token.folio][token.line].append(token)

def get_paragraphs(folio):
    lines = folio_line_tokens[folio]
    paragraphs = []
    current_para = []

    for line_num in sorted(lines.keys()):
        tokens = lines[line_num]
        if not tokens:
            continue
        first_word = tokens[0].word
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, tokens)]
        else:
            current_para.append((line_num, tokens))

    if current_para:
        paragraphs.append(current_para)

    return paragraphs

def analyze_paragraph(para):
    """Return detailed stats for a paragraph"""
    all_tokens = []
    for line_num, tokens in para:
        all_tokens.extend(tokens)

    words = [t.word for t in all_tokens]

    # Gallows marker
    first_word = words[0] if words else ""
    gallows = first_word[0] if first_word else "?"

    # Kernel counts
    k_count = sum(w.count('k') for w in words)
    h_count = sum(w.count('h') for w in words)
    e_count = sum(w.count('e') for w in words)
    total_kernel = k_count + h_count + e_count

    # Role distribution
    roles = defaultdict(int)
    for w in words:
        role = token_to_role.get(w, 'UNKNOWN')
        roles[role] += 1

    # PREFIX analysis (qo vs ch/sh)
    qo_count = sum(1 for w in words if w.startswith('qo'))
    ch_sh_count = sum(1 for w in words if w.startswith('ch') or w.startswith('sh'))

    # Unique vocabulary
    unique_words = set(words)

    return {
        'gallows': gallows,
        'first_token': first_word,
        'lines': len(para),
        'tokens': len(all_tokens),
        'unique': len(unique_words),
        'k': k_count,
        'h': h_count,
        'e': e_count,
        'k_pct': 100*k_count/total_kernel if total_kernel > 0 else 0,
        'h_pct': 100*h_count/total_kernel if total_kernel > 0 else 0,
        'e_pct': 100*e_count/total_kernel if total_kernel > 0 else 0,
        'qo_count': qo_count,
        'ch_sh_count': ch_sh_count,
        'qo_pct': 100*qo_count/len(words) if words else 0,
        'ch_sh_pct': 100*ch_sh_count/len(words) if words else 0,
        'roles': dict(roles),
        'words': words[:20]  # First 20 for inspection
    }

def compare_paragraphs(folio):
    """Compare all paragraphs in a folio"""
    paragraphs = get_paragraphs(folio)

    print(f"\n{'='*80}")
    print(f"FOLIO {folio}: {len(paragraphs)} PARAGRAPHS")
    print("="*80)

    stats = [analyze_paragraph(p) for p in paragraphs]

    # Summary table
    print(f"\n{'Par':<4} {'Gal':<4} {'Lines':<6} {'Tok':<5} {'k%':<6} {'h%':<6} {'e%':<6} {'qo%':<6} {'ch/sh%':<7} {'First Token':<15}")
    print("-"*80)

    for i, s in enumerate(stats):
        print(f"{i+1:<4} {s['gallows']:<4} {s['lines']:<6} {s['tokens']:<5} "
              f"{s['k_pct']:<6.0f} {s['h_pct']:<6.0f} {s['e_pct']:<6.0f} "
              f"{s['qo_pct']:<6.1f} {s['ch_sh_pct']:<7.1f} {s['first_token'][:15]:<15}")

    # Find the most distinct paragraphs
    print(f"\n{'='*80}")
    print("PARAGRAPH DISTINCTIVENESS")
    print("="*80)

    # Vocabulary overlap between consecutive paragraphs
    print("\nVocabulary overlap (consecutive pairs):")
    for i in range(len(stats)-1):
        vocab1 = set(stats[i]['words'])
        vocab2 = set(stats[i+1]['words'])
        overlap = len(vocab1 & vocab2)
        union = len(vocab1 | vocab2)
        jaccard = overlap/union if union > 0 else 0
        print(f"  Par {i+1} <-> Par {i+2}: {overlap} shared, Jaccard={jaccard:.3f}")

    # All-pairs vocabulary overlap
    print("\nAll-pairs vocabulary overlap matrix (Jaccard):")
    print("     ", end="")
    for i in range(len(stats)):
        print(f"P{i+1:<4}", end="")
    print()
    for i in range(len(stats)):
        print(f"P{i+1}   ", end="")
        for j in range(len(stats)):
            if i == j:
                print("-    ", end="")
            else:
                vocab1 = set(stats[i]['words'])
                vocab2 = set(stats[j]['words'])
                overlap = len(vocab1 & vocab2)
                union = len(vocab1 | vocab2)
                jaccard = overlap/union if union > 0 else 0
                print(f"{jaccard:.2f} ", end="")
        print()

    # Kernel signature comparison
    print("\nKernel signature clustering:")
    for i, s in enumerate(stats):
        signature = f"k={s['k_pct']:.0f}% h={s['h_pct']:.0f}% e={s['e_pct']:.0f}%"
        # Classify
        if s['k_pct'] > 25:
            cluster = "HIGH-K (energy input?)"
        elif s['h_pct'] > 35:
            cluster = "HIGH-H (monitoring?)"
        elif s['e_pct'] > 60:
            cluster = "HIGH-E (equilibration?)"
        else:
            cluster = "BALANCED"
        print(f"  Par {i+1}: {signature} -> {cluster}")

    # Prefix lane comparison (qo vs ch/sh)
    print("\nPrefix lane (qo vs ch/sh):")
    for i, s in enumerate(stats):
        total_lane = s['qo_count'] + s['ch_sh_count']
        if total_lane > 0:
            qo_ratio = s['qo_count'] / total_lane
            if qo_ratio > 0.6:
                lane = "QO-DOMINANT (energy/venting)"
            elif qo_ratio < 0.4:
                lane = "CHSH-DOMINANT (stabilization)"
            else:
                lane = "BALANCED"
        else:
            lane = "NO LANE TOKENS"
        print(f"  Par {i+1}: qo={s['qo_count']} ch/sh={s['ch_sh_count']} -> {lane}")

    return stats

# Analyze several folios
folios_to_analyze = ['f105r', 'f111r', 'f79v']

for folio in folios_to_analyze:
    if folio in folio_line_tokens:
        compare_paragraphs(folio)

# Look for folios with maximum intra-folio kernel variance
print("\n" + "="*80)
print("FOLIOS WITH HIGHEST INTRA-PARAGRAPH KERNEL VARIANCE")
print("="*80)

folio_kernel_variance = []
for folio in folio_line_tokens:
    paras = get_paragraphs(folio)
    if len(paras) < 3:
        continue

    stats = [analyze_paragraph(p) for p in paras]
    k_pcts = [s['k_pct'] for s in stats if s['tokens'] > 10]
    h_pcts = [s['h_pct'] for s in stats if s['tokens'] > 10]

    if len(k_pcts) >= 3:
        k_var = max(k_pcts) - min(k_pcts)
        h_var = max(h_pcts) - min(h_pcts)
        total_var = k_var + h_var
        folio_kernel_variance.append((folio, total_var, k_var, h_var, len(paras)))

folio_kernel_variance.sort(key=lambda x: -x[1])

print(f"\n{'Folio':<10} {'Paras':<6} {'k-range':<10} {'h-range':<10} {'Total':<10}")
print("-"*50)
for folio, total, k_var, h_var, n_paras in folio_kernel_variance[:10]:
    print(f"{folio:<10} {n_paras:<6} {k_var:<10.1f} {h_var:<10.1f} {total:<10.1f}")
