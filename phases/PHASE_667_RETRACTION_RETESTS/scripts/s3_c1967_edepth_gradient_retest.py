"""
Phase 667 s3 — C1967 retest: e_depth paragraph-channel gradient

Original claim: qo=0.679 > ch=0.606 > sh=0.538 (monotonic gradient).
Problem 1: No statistical test.
Problem 2: Compositional confound — qo paragraphs have more qo-prefix
  tokens which inherently carry higher e_depth.

Fix 1: Permutation test — shuffle channel labels among block-pure
  paragraphs, check how often random shuffle produces gradient >= observed.
Fix 2: Compute e_depth only on NON-PREFIX tokens (tokens that don't start
  with qo/ch/sh/ok/ot/ol/or) to remove compositional artifact.
"""
import sys
import io
import json
import math
import random
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

FIRE = {'ch', 'sh', 'qo'}
VESSEL = {'ok', 'ot', 'ol', 'or'}
ALL_PREFIXES = FIRE | VESSEL


def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k', 't', 'l', 'r'):
        return 'o' + w[1]
    return None


def has_any_prefix(w):
    return prefix_of(w) is not None


def e_depth_of(w):
    try:
        a = morph.atomize(w)
        return a.e_depth
    except Exception:
        return 0


paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

# Classify block-pure paragraphs by dominant channel
channel_edepths_all = defaultdict(list)     # all tokens
channel_edepths_nonpfx = defaultdict(list)  # non-prefix tokens only
channel_labels = []
channel_edepth_values_all = []
channel_edepth_values_nonpfx = []

for (f, par_idx), toks in paragraphs.items():
    if len(toks) < 8:
        continue

    from collections import Counter
    prefix_counts = Counter()
    block_counts = Counter()
    for t in toks:
        p = prefix_of(t.word)
        if p:
            prefix_counts[p] += 1
            b = 'F' if p in FIRE else 'V'
            block_counts[b] += 1

    target_total = sum(prefix_counts.values())
    if target_total < 4:
        continue

    fire_frac = block_counts.get('F', 0) / target_total
    vessel_frac = block_counts.get('V', 0) / target_total
    if max(fire_frac, vessel_frac) <= 0.70:
        continue

    dominant_block = 'F' if fire_frac > vessel_frac else 'V'
    block_prefixes = FIRE if dominant_block == 'F' else VESSEL
    dom_channel = max(block_prefixes, key=lambda p: prefix_counts.get(p, 0))

    if dom_channel not in ('qo', 'ch', 'sh'):
        continue

    # Compute e_depth on ALL tokens
    all_edepths = [e_depth_of(t.word) for t in toks]
    mean_all = sum(all_edepths) / len(all_edepths) if all_edepths else 0

    # Compute e_depth on NON-PREFIX tokens only (compositional control)
    nonpfx_edepths = [e_depth_of(t.word) for t in toks if not has_any_prefix(t.word)]
    mean_nonpfx = sum(nonpfx_edepths) / len(nonpfx_edepths) if nonpfx_edepths else 0

    channel_edepths_all[dom_channel].append(mean_all)
    channel_edepths_nonpfx[dom_channel].append(mean_nonpfx)
    channel_labels.append(dom_channel)
    channel_edepth_values_all.append(mean_all)
    channel_edepth_values_nonpfx.append(mean_nonpfx)

print('=== C1967 Retest: e_depth Paragraph-Channel Gradient ===')
print()
for ch in ('qo', 'ch', 'sh'):
    vals_all = channel_edepths_all[ch]
    vals_npf = channel_edepths_nonpfx[ch]
    mean_a = sum(vals_all) / len(vals_all) if vals_all else 0
    mean_n = sum(vals_npf) / len(vals_npf) if vals_npf else 0
    print(f'{ch}: n={len(vals_all):>3d}  all_tokens e_depth={mean_a:.4f}  non-prefix e_depth={mean_n:.4f}')

# Observed gradient (all tokens)
qo_a = sum(channel_edepths_all['qo']) / len(channel_edepths_all['qo'])
ch_a = sum(channel_edepths_all['ch']) / len(channel_edepths_all['ch'])
sh_a = sum(channel_edepths_all['sh']) / len(channel_edepths_all['sh'])
gradient_all = qo_a - sh_a

# Observed gradient (non-prefix tokens)
qo_n = sum(channel_edepths_nonpfx['qo']) / len(channel_edepths_nonpfx['qo'])
ch_n = sum(channel_edepths_nonpfx['ch']) / len(channel_edepths_nonpfx['ch'])
sh_n = sum(channel_edepths_nonpfx['sh']) / len(channel_edepths_nonpfx['sh'])
gradient_nonpfx = qo_n - sh_n

print(f'\nAll-token gradient (qo - sh): {gradient_all:+.4f}')
print(f'Non-prefix gradient (qo - sh): {gradient_nonpfx:+.4f}')
monotonic_all = qo_a > ch_a > sh_a
monotonic_nonpfx = qo_n > ch_n > sh_n
print(f'All-token monotonic (qo > ch > sh): {monotonic_all}')
print(f'Non-prefix monotonic (qo > ch > sh): {monotonic_nonpfx}')

# Permutation test: shuffle channel labels, compute gradient
rng = random.Random(20260427)
n_perm = 10000
n_ge_all = 0
n_ge_nonpfx = 0
n_mono_all = 0
n_mono_nonpfx = 0

for _ in range(n_perm):
    shuf_labels = channel_labels[:]
    rng.shuffle(shuf_labels)

    groups_a = defaultdict(list)
    groups_n = defaultdict(list)
    for i, lab in enumerate(shuf_labels):
        groups_a[lab].append(channel_edepth_values_all[i])
        groups_n[lab].append(channel_edepth_values_nonpfx[i])

    if not groups_a['qo'] or not groups_a['sh']:
        continue

    g_a = (sum(groups_a['qo'])/len(groups_a['qo'])) - (sum(groups_a['sh'])/len(groups_a['sh']))
    g_n = (sum(groups_n['qo'])/len(groups_n['qo'])) - (sum(groups_n['sh'])/len(groups_n['sh']))

    if g_a >= gradient_all:
        n_ge_all += 1
    if g_n >= gradient_nonpfx:
        n_ge_nonpfx += 1

    m_qo_a = sum(groups_a['qo'])/len(groups_a['qo'])
    m_ch_a = sum(groups_a['ch'])/len(groups_a['ch']) if groups_a['ch'] else 0
    m_sh_a = sum(groups_a['sh'])/len(groups_a['sh'])
    if m_qo_a > m_ch_a > m_sh_a:
        n_mono_all += 1

    m_qo_n = sum(groups_n['qo'])/len(groups_n['qo'])
    m_ch_n = sum(groups_n['ch'])/len(groups_n['ch']) if groups_n['ch'] else 0
    m_sh_n = sum(groups_n['sh'])/len(groups_n['sh'])
    if m_qo_n > m_ch_n > m_sh_n:
        n_mono_nonpfx += 1

p_all = n_ge_all / n_perm
p_nonpfx = n_ge_nonpfx / n_perm
p_mono_all = n_mono_all / n_perm
p_mono_nonpfx = n_mono_nonpfx / n_perm

print(f'\n=== Permutation tests ({n_perm:,} shuffles) ===')
print(f'Gradient (qo-sh) all tokens:     p = {p_all:.4f}')
print(f'Gradient (qo-sh) non-prefix:     p = {p_nonpfx:.4f}')
print(f'Monotonic (qo>ch>sh) all tokens: p = {p_mono_all:.4f}')
print(f'Monotonic (qo>ch>sh) non-prefix: p = {p_mono_nonpfx:.4f}')

# Verdict
print('\n=== VERDICT ===')
if monotonic_nonpfx and p_nonpfx <= 0.05:
    print('Gradient CONFIRMED after compositional control.')
    verdict = 'CONFIRMED'
elif monotonic_nonpfx and p_nonpfx <= 0.20:
    print('Gradient DIRECTIONAL after compositional control.')
    verdict = 'DIRECTIONAL'
elif not monotonic_nonpfx:
    print('Gradient BREAKS after removing prefix-token composition.')
    verdict = 'FALSIFIED'
else:
    print('Gradient present but not significant.')
    verdict = 'INCONCLUSIVE'
print(f'Verdict: {verdict}')

out = {
    'channel_means_all': {'qo': qo_a, 'ch': ch_a, 'sh': sh_a},
    'channel_means_nonpfx': {'qo': qo_n, 'ch': ch_n, 'sh': sh_n},
    'channel_counts': {ch: len(channel_edepths_all[ch]) for ch in ('qo', 'ch', 'sh')},
    'gradient_all': gradient_all,
    'gradient_nonpfx': gradient_nonpfx,
    'monotonic_all': monotonic_all,
    'monotonic_nonpfx': monotonic_nonpfx,
    'p_gradient_all': p_all,
    'p_gradient_nonpfx': p_nonpfx,
    'p_monotonic_all': p_mono_all,
    'p_monotonic_nonpfx': p_mono_nonpfx,
    'verdict': verdict,
}

out_dir = REPO_ROOT / 'phases' / 'PHASE_667_RETRACTION_RETESTS' / 'results'
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / 'C1967_RETEST.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(f'\nWrote results.')
