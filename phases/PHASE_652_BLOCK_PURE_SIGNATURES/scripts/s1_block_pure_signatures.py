"""
Block-pure paragraph operational signatures test.

Per C1961 (Phase 648): 46% of Currier B paragraphs are >70% block-pure
(fire-side or vessel-side dominant). Crazy-expert's recommendation:
classify these block-pure paragraphs by their DOMINANT CHANNEL within
the block, then test whether each channel-class shows operationally
distinct signatures.

If the architecture is real:
- qo-dominant paragraphs: high k-HEAD, high e_depth (gentle/sustained heat)
- ok-dominant: containment/vessel-thermal signatures
- ol-dominant: staging/state signatures (per C1388)
- ot-dominant: transfer/iteration signatures (per C1958)
- or-dominant: response/flow signatures
- ch-dominant: active-test signatures
- sh-dominant: passive-monitoring signatures

Tests per channel-class:
1. Mean HEAD atom distribution (k, e, h, etc.)
2. Mean e_depth (continuous-extensible thermal intensity per F-B-007)
3. Dominant section (B, H, S, C, etc.)
4. Dominant REGIME assignment
"""
import sys
import json
import math
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter

tx = Transcript()
morph = Morphology()

with open('data/regime_folio_mapping.json') as f:
    regime_data = json.load(f)
regime_assignments = regime_data['regime_assignments']

# Group tokens into paragraphs
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

# Classify each paragraph
paragraph_class = {}
for (folio, par_idx), toks in paragraphs.items():
    if len(toks) < 8: continue

    # Count target prefixes
    prefix_counts = Counter()
    block_counts = Counter()
    for t in toks:
        p = prefix_of(t.word)
        if p:
            prefix_counts[p] += 1
            block_counts[block_of(p)] += 1
    target_total = sum(prefix_counts.values())
    if target_total < 4: continue

    # Block purity
    fire_frac = block_counts.get('F', 0) / target_total
    vessel_frac = block_counts.get('V', 0) / target_total
    block_pure = max(fire_frac, vessel_frac) > 0.70

    # Dominant channel within block
    dominant_block = 'F' if fire_frac > vessel_frac else 'V'
    block_prefixes = (FIRE if dominant_block == 'F' else VESSEL)
    dom_channel = max(block_prefixes,
                       key=lambda p: prefix_counts.get(p, 0))
    dom_channel_count = prefix_counts.get(dom_channel, 0)
    channel_purity = (dom_channel_count / target_total) if target_total > 0 else 0

    paragraph_class[(folio, par_idx)] = {
        'tokens': toks, 'fire_frac': fire_frac, 'vessel_frac': vessel_frac,
        'block_pure': block_pure, 'dominant_block': dominant_block,
        'dominant_channel': dom_channel, 'channel_purity': channel_purity,
        'target_total': target_total,
        'folio': folio, 'par_idx': par_idx,
    }

n_total = len(paragraph_class)
n_block_pure = sum(1 for d in paragraph_class.values() if d['block_pure'])
print(f"Paragraphs analyzed: {n_total}")
print(f"Block-pure (>70% one block): {n_block_pure} ({n_block_pure/n_total*100:.1f}%)")

# For each channel-class (within block-pure paragraphs), compute signatures
channel_classes = defaultdict(list)
for key, d in paragraph_class.items():
    if d['block_pure']:
        channel_classes[d['dominant_channel']].append(d)

print()
print("="*78)
print("CHANNEL-CLASS PARAGRAPH COUNTS")
print("="*78)
print()
for ch in ('qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'or'):
    n = len(channel_classes.get(ch, []))
    print(f"  {ch}-dominant block-pure paragraphs: {n}")

def compute_signatures(par_list):
    """For a list of paragraphs, compute mean atom distribution,
    e_depth, section, regime."""
    head_counts = Counter()
    e_depths = []
    sections = Counter()
    regimes = Counter()
    n_tokens = 0
    for d in par_list:
        for t in d['tokens']:
            n_tokens += 1
            sections[t.section] += 1
            try:
                a = morph.atomize(t.word)
                # First atom is HEAD
                if a.atoms:
                    head = a.atoms[0]
                    if head[1] == 'HEAD':
                        head_counts[head[0]] += 1
                e_depths.append(a.e_depth)
            except Exception:
                pass
        regime = regime_assignments.get(d['folio'], {}).get('regime', None)
        if regime:
            regimes[regime] += 1
    return {
        'n_paragraphs': len(par_list),
        'n_tokens': n_tokens,
        'head_distribution': {h: c/n_tokens for h, c in head_counts.most_common(10)},
        'mean_e_depth': sum(e_depths)/len(e_depths) if e_depths else 0,
        'top_section': sections.most_common(1)[0] if sections else None,
        'top_regime': regimes.most_common(1)[0] if regimes else None,
        'sections_dist': dict(sections),
        'regimes_dist': dict(regimes),
    }

# Compute baseline (all block-pure paragraphs combined)
all_block_pure = [d for d in paragraph_class.values() if d['block_pure']]
baseline = compute_signatures(all_block_pure)
print()
print(f"Baseline (all block-pure, n={baseline['n_paragraphs']} paragraphs):")
print(f"  Mean e_depth: {baseline['mean_e_depth']:.3f}")
print(f"  HEAD distribution: {baseline['head_distribution']}")
print(f"  Top section: {baseline['top_section']}")
print(f"  Top regime: {baseline['top_regime']}")

# Per-channel signatures
print()
print("="*78)
print("PER-CHANNEL OPERATIONAL SIGNATURES")
print("="*78)

results = {}
for ch in ('qo', 'ch', 'sh', 'ok', 'ot', 'ol', 'or'):
    par_list = channel_classes.get(ch, [])
    if len(par_list) < 5:
        print(f"\n{ch}: n={len(par_list)} -- too few to characterize")
        continue
    sig = compute_signatures(par_list)
    print(f"\n--- {ch}-dominant paragraphs (n={sig['n_paragraphs']} paragraphs, {sig['n_tokens']} tokens) ---")
    print(f"  Mean e_depth: {sig['mean_e_depth']:.3f}  (vs baseline {baseline['mean_e_depth']:.3f}, delta {sig['mean_e_depth']-baseline['mean_e_depth']:+.3f})")
    # Top HEAD atoms
    top_heads = list(sig['head_distribution'].items())[:5]
    print(f"  Top HEAD atoms: {[(h, f'{r*100:.1f}%') for h, r in top_heads]}")
    # Top sections
    top_sections = sorted(sig['sections_dist'].items(), key=lambda x: -x[1])[:3]
    sec_total = sum(sig['sections_dist'].values())
    sec_str = ', '.join(f"{s}={c/sec_total*100:.0f}%" for s, c in top_sections)
    print(f"  Sections: {sec_str}")
    # Top regimes
    top_regimes = sorted(sig['regimes_dist'].items(), key=lambda x: -x[1])[:3]
    reg_total = sum(sig['regimes_dist'].values()) or 1
    reg_str = ', '.join(f"{r}={c/reg_total*100:.0f}%" for r, c in top_regimes)
    print(f"  Regimes: {reg_str}")
    results[ch] = sig

# Save
import os
os.makedirs('scratch', exist_ok=True)
with open('scratch/block_pure_signatures.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print()
print("Saved: scratch/block_pure_signatures.json")
