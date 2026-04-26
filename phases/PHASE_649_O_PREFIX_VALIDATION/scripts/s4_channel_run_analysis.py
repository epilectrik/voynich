"""
Phase 649 Step 4: Channel-run analysis — where do channel transitions happen?

Now that we know channels persist within lines (mode-invariantly), the
remaining shape question is: do channel transitions happen at line breaks,
within lines, or only at paragraph breaks?

Shapes to discriminate:
- A: Line-as-statement       (transitions at line breaks; runs ~3-5 tokens)
- B: Multi-line channel runs (transitions mid-paragraph; runs 8-15 tokens)
- C: Paragraph-pure          (transitions at paragraph breaks; runs 20+ tokens)

Method:
1. For each paragraph, walk the sequence; tag each token with channel
2. Group consecutive same-channel tokens into runs
3. For each transition, classify location: within-line / line-break / par-break
4. Compute run-length distribution
5. Compute paragraph channel-purity (single dominant channel?)
6. Bonus: within-paragraph channel ordering — is it structured?
"""
import sys
import json
from collections import defaultdict, Counter
sys.path.insert(0, '.')
from scripts.voynich import Transcript

tx = Transcript()

def prefix_of(w):
    if w.startswith('ch'): return 'ch'
    if w.startswith('sh'): return 'sh'
    if w.startswith('qo'): return 'qo'
    if len(w) >= 2 and w[0] == 'o' and w[1] in ('k','t','l','r'):
        return 'o' + w[1]
    return None

# Block assignments
FIRE = {'ch', 'sh', 'qo'}
VESSEL = {'ok', 'ot', 'ol', 'or'}
def block_of(p):
    if p in FIRE: return 'F'
    if p in VESSEL: return 'V'
    return None

# Walk Currier B tokens with paragraph + line context
paragraphs = defaultdict(list)
current_par = {}
for t in tx.currier_b():
    f = t.folio
    if t.par_initial:
        current_par[f] = current_par.get(f, -1) + 1
    par_idx = current_par.get(f, 0)
    paragraphs[(f, par_idx)].append(t)

# For each paragraph, build sequence of (channel, line, in-line-idx)
# Then identify runs and transitions
prefix_runs = []   # list of run-length lists (per paragraph)
block_runs = []    # at fire/vessel level

# Transition location counts
prefix_trans_loc = Counter()  # 'within-line' / 'line-break'
block_trans_loc = Counter()

# Channel-purity
par_pref_purity = []  # fraction of dominant channel in each paragraph
par_block_purity = []

# Channel ordering within paragraphs (for paragraphs with >=3 distinct channels)
par_channel_orders = []
par_block_orders = []

for (f, par_idx), toks in paragraphs.items():
    if len(toks) < 6: continue  # need enough tokens to see runs

    # Filter to tokens with target prefix
    tagged = [(prefix_of(t.word), block_of(prefix_of(t.word)), t.line) for t in toks]
    tagged_pref = [(p, l) for p, _, l in tagged if p is not None]
    tagged_block = [(b, l) for _, b, l in tagged if b is not None]

    if len(tagged_pref) < 3: continue

    # ---- Prefix-level runs ----
    runs = []
    cur_pref = tagged_pref[0][0]
    cur_len = 1
    for i in range(1, len(tagged_pref)):
        p, line = tagged_pref[i]
        prev_p, prev_line = tagged_pref[i-1]
        if p == prev_p:
            cur_len += 1
        else:
            runs.append(cur_len)
            # classify transition location
            if line == prev_line:
                prefix_trans_loc['within-line'] += 1
            else:
                prefix_trans_loc['line-break'] += 1
            cur_pref = p
            cur_len = 1
    runs.append(cur_len)
    prefix_runs.append(runs)

    # Channel purity at prefix level
    counts = Counter(p for p, _ in tagged_pref)
    dominant = max(counts.values())
    par_pref_purity.append(dominant / len(tagged_pref))

    # Channel ordering: collapse to run-of-channels sequence (deduplicated consecutive)
    order = []
    for p, _ in tagged_pref:
        if not order or order[-1] != p:
            order.append(p)
    if len(set(order)) >= 3:
        par_channel_orders.append(order)

    # ---- Block-level runs (fire/vessel) ----
    if len(tagged_block) < 3: continue
    runs_b = []
    cur_b = tagged_block[0][0]
    cur_len_b = 1
    for i in range(1, len(tagged_block)):
        b, line = tagged_block[i]
        prev_b, prev_line = tagged_block[i-1]
        if b == prev_b:
            cur_len_b += 1
        else:
            runs_b.append(cur_len_b)
            if line == prev_line:
                block_trans_loc['within-line'] += 1
            else:
                block_trans_loc['line-break'] += 1
            cur_b = b
            cur_len_b = 1
    runs_b.append(cur_len_b)
    block_runs.append(runs_b)
    counts_b = Counter(b for b, _ in tagged_block)
    dominant_b = max(counts_b.values())
    par_block_purity.append(dominant_b / len(tagged_block))

    # Block ordering
    order_b = []
    for b, _ in tagged_block:
        if not order_b or order_b[-1] != b:
            order_b.append(b)
    par_block_orders.append(order_b)

# Run-length stats
def run_stats(runs_lists):
    flat = [r for runs in runs_lists for r in runs]
    if not flat: return None
    flat.sort()
    return {
        'mean': sum(flat) / len(flat),
        'median': flat[len(flat)//2],
        'p25': flat[len(flat)//4],
        'p75': flat[3*len(flat)//4],
        'max': max(flat),
        'n_runs': len(flat),
        'frac_singletons': sum(1 for r in flat if r == 1) / len(flat),
        'frac_long_5plus': sum(1 for r in flat if r >= 5) / len(flat),
        'frac_long_10plus': sum(1 for r in flat if r >= 10) / len(flat),
    }

print("="*72)
print("PREFIX-LEVEL CHANNEL RUNS")
print("="*72)
ps = run_stats(prefix_runs)
print(f"Paragraphs analyzed: {len(prefix_runs)}")
print(f"Total runs: {ps['n_runs']:,}")
print(f"Run length: mean={ps['mean']:.2f}  median={ps['median']}  "
      f"p25={ps['p25']}  p75={ps['p75']}  max={ps['max']}")
print(f"Singletons (length 1):     {ps['frac_singletons']*100:5.1f}%")
print(f"Long runs (5+):            {ps['frac_long_5plus']*100:5.1f}%")
print(f"Long runs (10+):           {ps['frac_long_10plus']*100:5.1f}%")
print()
print("Prefix transition location:")
total_pt = sum(prefix_trans_loc.values())
for loc, c in prefix_trans_loc.most_common():
    print(f"  {loc}: {c:5d} ({c/total_pt*100:5.1f}%)")

print()
print("Channel purity per paragraph (fraction of dominant channel):")
par_pref_purity.sort()
mp = sum(par_pref_purity) / len(par_pref_purity)
print(f"  Mean: {mp*100:.1f}%")
print(f"  Median: {par_pref_purity[len(par_pref_purity)//2]*100:.1f}%")
print(f"  Paragraphs >70% channel-pure: {sum(1 for p in par_pref_purity if p > 0.7)}/{len(par_pref_purity)}"
      f" ({sum(1 for p in par_pref_purity if p > 0.7)/len(par_pref_purity)*100:.1f}%)")
print(f"  Paragraphs >50%: {sum(1 for p in par_pref_purity if p > 0.5)/len(par_pref_purity)*100:.1f}%")

print()
print("="*72)
print("BLOCK-LEVEL CHANNEL RUNS (fire vs vessel)")
print("="*72)
bs = run_stats(block_runs)
print(f"Total block runs: {bs['n_runs']:,}")
print(f"Run length: mean={bs['mean']:.2f}  median={bs['median']}  "
      f"p25={bs['p25']}  p75={bs['p75']}  max={bs['max']}")
print(f"Singletons (length 1): {bs['frac_singletons']*100:5.1f}%")
print(f"Long runs (5+):        {bs['frac_long_5plus']*100:5.1f}%")
print(f"Long runs (10+):       {bs['frac_long_10plus']*100:5.1f}%")
print()
print("Block transition location:")
total_bt = sum(block_trans_loc.values())
for loc, c in block_trans_loc.most_common():
    print(f"  {loc}: {c:5d} ({c/total_bt*100:5.1f}%)")

print()
print("Block purity per paragraph (fraction of dominant block):")
par_block_purity.sort()
mbp = sum(par_block_purity) / len(par_block_purity)
print(f"  Mean: {mbp*100:.1f}%")
print(f"  Paragraphs >70% block-pure: {sum(1 for p in par_block_purity if p > 0.7)/len(par_block_purity)*100:.1f}%")
print(f"  Paragraphs >85% block-pure: {sum(1 for p in par_block_purity if p > 0.85)/len(par_block_purity)*100:.1f}%")
print(f"  Paragraphs 100% block-pure: {sum(1 for p in par_block_purity if p == 1.0)/len(par_block_purity)*100:.1f}%")

# Shape verdict
print()
print("="*72)
print("SHAPE VERDICT")
print("="*72)
print()
print("Reference shapes:")
print("  A (line-as-statement):    runs 3-5, transitions concentrated at line-break")
print("  B (multi-line runs):      runs 8-15, transitions within paragraphs")
print("  C (paragraph-pure):       runs 20+, transitions at paragraph-break only")
print()
print(f"Observed prefix runs: mean={ps['mean']:.2f}, median={ps['median']}")
print(f"Observed block runs: mean={bs['mean']:.2f}, median={bs['median']}")
print(f"Prefix transitions at line-break: {prefix_trans_loc['line-break']/total_pt*100:.1f}%")
print(f"Block transitions at line-break:  {block_trans_loc['line-break']/total_bt*100:.1f}%")

# Channel ordering analysis: does specification (ol) come before action (ot)?
print()
print("="*72)
print("WITHIN-PARAGRAPH CHANNEL ORDERING (mixed-channel paragraphs)")
print("="*72)
print()
print(f"Paragraphs with 3+ distinct prefixes: {len(par_channel_orders)}")
# Test: does ol appear before ot in these orderings?
ol_before_ot = 0
ot_before_ol = 0
both_seen = 0
for order in par_channel_orders:
    if 'ol' in order and 'ot' in order:
        both_seen += 1
        if order.index('ol') < order.index('ot'):
            ol_before_ot += 1
        else:
            ot_before_ol += 1
print(f"\nol vs ot first appearance:")
if both_seen > 0:
    print(f"  ol before ot: {ol_before_ot} ({ol_before_ot/both_seen*100:.1f}%)")
    print(f"  ot before ol: {ot_before_ol} ({ot_before_ol/both_seen*100:.1f}%)")
    print(f"  (n={both_seen}, expected 50/50 if random)")

# Same for qo before ok (driver before observer?)
qo_before_ok = 0; ok_before_qo = 0; both_qo_ok = 0
for order in par_channel_orders:
    if 'qo' in order and 'ok' in order:
        both_qo_ok += 1
        if order.index('qo') < order.index('ok'):
            qo_before_ok += 1
        else:
            ok_before_qo += 1
print(f"\nqo vs ok first appearance:")
if both_qo_ok > 0:
    print(f"  qo before ok: {qo_before_ok} ({qo_before_ok/both_qo_ok*100:.1f}%)")
    print(f"  ok before qo: {ok_before_qo} ({ok_before_qo/both_qo_ok*100:.1f}%)")

# Save
out = {
    'prefix_run_stats': ps,
    'block_run_stats': bs,
    'prefix_transition_location': dict(prefix_trans_loc),
    'block_transition_location': dict(block_trans_loc),
    'mean_prefix_purity': mp,
    'mean_block_purity': mbp,
    'paragraphs_70pct_block_pure': sum(1 for p in par_block_purity if p > 0.7)/len(par_block_purity),
    'paragraphs_85pct_block_pure': sum(1 for p in par_block_purity if p > 0.85)/len(par_block_purity),
    'ol_before_ot': {'count': ol_before_ot, 'total': both_seen,
                     'pct': ol_before_ot/both_seen if both_seen else 0},
    'qo_before_ok': {'count': qo_before_ok, 'total': both_qo_ok,
                     'pct': qo_before_ok/both_qo_ok if both_qo_ok else 0},
}
with open('phases/PHASE_649_O_PREFIX_VALIDATION/results/channel_runs.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)
