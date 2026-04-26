"""
Token-pool control on Phase 655 header-body HT density finding.

Expert-advisor caveat (C1789, 86% header-token exclusivity):
"Header HT density at header position is partly tautological -- header
tokens are different tokens. The gap may reflect token deployment vs
header-exclusive vocabulary being structurally more HT-rich."

Test: restrict to tokens that appear in BOTH header and body positions
across paragraphs. Recompute the HT-rate gap among these "shared" tokens.

If gap survives -> architectural deployment effect (operator places
   compound-rich tokens in header positions). C1968 holds as Tier 2.
If gap collapses -> header-exclusive vocabulary is structurally more
   compound; the architectural claim is artifact. C1968 should not
   be registered.
"""
import sys
import json
import math
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

FIRE = {'ch', 'sh', 'qo'}
VESSEL = {'ok', 'ot', 'ol', 'or'}

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

def block_of(p):
    if p in FIRE: return 'F'
    if p in VESSEL: return 'V'
    return None

def is_ht_token(w):
    """Per HTSC: HT = compound MIDDLE token."""
    m = morph.extract(w)
    if m.middle and len(m.middle) >= 2:
        try:
            return mid_analyzer.is_compound(m.middle)
        except Exception:
            return False
    return False

def split_header_body(toks):
    if not toks: return [], []
    first_line = toks[0].line
    header = [t for t in toks if t.line == first_line]
    body = [t for t in toks if t.line != first_line]
    return header, body

# Filter to block-pure paragraphs (same as Phase 655 test)
qualifying_paragraphs = []
for (folio, par_idx), toks in paragraphs.items():
    if len(toks) < 8: continue
    lines = set(t.line for t in toks)
    if len(lines) < 2: continue

    prefix_counts = Counter()
    block_counts = Counter()
    for t in toks:
        p = prefix_of(t.word)
        if p:
            prefix_counts[p] += 1
            block_counts[block_of(p)] += 1
    target_total = sum(prefix_counts.values())
    if target_total < 4: continue

    fire_frac = block_counts.get('F', 0) / target_total
    vessel_frac = block_counts.get('V', 0) / target_total
    if max(fire_frac, vessel_frac) <= 0.70: continue

    dominant_block = 'F' if fire_frac > vessel_frac else 'V'
    block_prefixes = (FIRE if dominant_block == 'F' else VESSEL)
    dom_channel = max(block_prefixes, key=lambda p: prefix_counts.get(p, 0))

    header, body = split_header_body(toks)
    if len(header) < 2 or len(body) < 2: continue

    qualifying_paragraphs.append({
        'folio': folio, 'par_idx': par_idx,
        'header': header, 'body': body,
        'dominant_channel': dom_channel,
    })

# Build vocabulary: which token types appear in header positions, body positions, both?
header_token_types = set()
body_token_types = set()
for p in qualifying_paragraphs:
    for t in p['header']:
        header_token_types.add(t.word)
    for t in p['body']:
        body_token_types.add(t.word)

shared_types = header_token_types & body_token_types
header_only_types = header_token_types - body_token_types
body_only_types = body_token_types - header_token_types

print("="*78)
print("TOKEN-POOL CONTROL ON PHASE 655 HEADER-BODY HT GAP")
print("="*78)
print()
print(f"Qualifying paragraphs: {len(qualifying_paragraphs)}")
print(f"Header token types (distinct): {len(header_token_types)}")
print(f"Body token types (distinct): {len(body_token_types)}")
print(f"  Shared (appear in both): {len(shared_types)}")
print(f"  Header-only types: {len(header_only_types)}")
print(f"  Body-only types: {len(body_only_types)}")
shared_pct = len(shared_types) / len(header_token_types) * 100
print(f"  Header type-overlap rate: {shared_pct:.1f}% (C1789 implied 14% non-exclusive)")

# Compute HT rates restricting to shared-token occurrences
print()
print("="*78)
print("HT RATE COMPARISON: ALL TOKENS vs SHARED-ONLY")
print("="*78)
print()
print(f"{'Class':>6s}  {'n':>4s}  "
      f"{'H_HT(all)':>10s}  {'B_HT(all)':>10s}  {'gap_all':>9s}  "
      f"{'H_HT(shared)':>13s}  {'B_HT(shared)':>13s}  {'gap_shared':>11s}")
print("-"*100)

import math, random
def paired_t(diffs):
    if len(diffs) < 3: return None
    n = len(diffs)
    mean = sum(diffs)/n
    var = sum((d - mean)**2 for d in diffs) / (n - 1)
    if var <= 0: return None
    se = math.sqrt(var / n)
    t = mean / se
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    return {'mean': mean, 't': t, 'p': p, 'n': n}

class_results = {}
for ch in ('qo', 'ch', 'sh'):
    par_list = [p for p in qualifying_paragraphs if p['dominant_channel'] == ch]
    if len(par_list) < 5: continue

    # All-tokens metric (replicates Phase 655)
    all_h = []
    all_b = []
    # Shared-tokens-only metric (the control)
    sh_h = []
    sh_b = []
    for p in par_list:
        h_toks_all = p['header']
        b_toks_all = p['body']
        h_toks_shared = [t for t in p['header'] if t.word in shared_types]
        b_toks_shared = [t for t in p['body'] if t.word in shared_types]

        if not h_toks_all or not b_toks_all: continue
        all_h.append(sum(1 for t in h_toks_all if is_ht_token(t.word)) / len(h_toks_all))
        all_b.append(sum(1 for t in b_toks_all if is_ht_token(t.word)) / len(b_toks_all))

        if h_toks_shared and b_toks_shared:
            sh_h.append(sum(1 for t in h_toks_shared if is_ht_token(t.word)) / len(h_toks_shared))
            sh_b.append(sum(1 for t in b_toks_shared if is_ht_token(t.word)) / len(b_toks_shared))

    if not all_h or not sh_h: continue
    h_all_mean = sum(all_h) / len(all_h)
    b_all_mean = sum(all_b) / len(all_b)
    gap_all = h_all_mean - b_all_mean
    h_sh_mean = sum(sh_h) / len(sh_h)
    b_sh_mean = sum(sh_b) / len(sh_b)
    gap_sh = h_sh_mean - b_sh_mean

    print(f"  {ch:>4s}  {len(par_list):>4d}  "
          f"{h_all_mean:>10.3f}  {b_all_mean:>10.3f}  {gap_all:>+8.3f}  "
          f"{h_sh_mean:>13.3f}  {b_sh_mean:>13.3f}  {gap_sh:>+10.3f}")
    class_results[ch] = {
        'n': len(par_list),
        'all': {'h_mean': h_all_mean, 'b_mean': b_all_mean, 'gap': gap_all,
                'paired_test': paired_t([h - b for h, b in zip(all_h, all_b)])},
        'shared_only': {'h_mean': h_sh_mean, 'b_mean': b_sh_mean, 'gap': gap_sh,
                        'paired_test': paired_t([h - b for h, b in zip(sh_h, sh_b)]),
                        'n_shared_pars': len(sh_h)}
    }

print()
print("Significance tests on shared-only gap:")
for ch in ('qo', 'ch', 'sh'):
    if ch not in class_results: continue
    r = class_results[ch]['shared_only']
    if r['paired_test']:
        sig = ' *' if r['paired_test']['p'] < 0.05 else (' +' if r['paired_test']['p'] < 0.10 else '')
        print(f"  {ch}-class shared-only: gap={r['gap']:+.3f}, t={r['paired_test']['t']:+.2f}, "
              f"p={r['paired_test']['p']:.4f}, n={r['paired_test']['n']}{sig}")

# Verdict
print()
print("="*78)
print("VERDICT")
print("="*78)
print()
print("If shared-only gaps preserve direction and significance ->")
print("  architectural deployment effect confirmed; C1968 holds as Tier 2.")
print("If shared-only gaps collapse to ~0 ->")
print("  header-exclusive vocabulary drove the original gap;")
print("  C1968 should be reframed or skipped.")

import os
with open('scratch/header_body_ht_token_pool_control.json', 'w') as f:
    json.dump({
        'paragraphs_analyzed': len(qualifying_paragraphs),
        'header_types': len(header_token_types),
        'body_types': len(body_token_types),
        'shared_types': len(shared_types),
        'class_results': class_results,
    }, f, indent=2, default=str)
print()
print("Saved: scratch/header_body_ht_token_pool_control.json")
