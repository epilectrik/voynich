"""
T1b: Dark MIDDLE successor profiles.

C1351 says dark MIDDLEs have narrow successor entropy (2.59 bits vs bridge 4.18).
Each dark MIDDLE constrains what grammar token follows it DIFFERENTLY.

Questions:
  1. Do different dark MIDDLEs route to different successor PREFIXes?
  2. Is the successor discrimination STRONGER than PREFIX discrimination?
  3. On f75r, do dark MIDDLE successors match recipe-appropriate operations?
  4. Are there dark MIDDLE "families" that share successor profiles?
"""

import sys, os, io, json, math
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

PREFIX_LABEL = {
    'qo': 'THERMAL', 'ch': 'TEST', 'sh': 'MONITOR', 'ok': 'VESSEL',
    'ot': 'OPS-CHK', 'da': 'SETUP', 'sa': 'SCAFFOLD', 'ol': 'CONTINUE',
    'po': 'PRE-WORK', 'so': 'SCAFF-ARR', 'ke': 'HEAT-BURST',
    'ko': 'HEAT-WORK', 'ka': 'HEAT-YIELD', 'ta': 'XFER-YIELD',
    'pch': 'STAGE-TEST', 'tch': 'XFER-TEST', 'dch': 'MARK-TEST',
    'lch': 'HOLD-TEST',
}

# ═══ BUILD SUCCESSOR INDEX ═══
# For each token, record what PREFIX follows it on the same line
folio_line_tokens = defaultdict(list)
for t in all_b:
    folio_line_tokens[(t.folio, t.line)].append(t)

# Dark MIDDLE -> successor PREFIX counter
dark_succ_prefix = defaultdict(Counter)
dark_succ_middle = defaultdict(Counter)
dark_succ_word = defaultdict(Counter)
# Bridge MIDDLE -> successor PREFIX counter (for comparison)
bridge_succ_prefix = defaultdict(Counter)

from scripts.voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()
bridge_set = pp_middles - dp_set

for (folio, line), line_toks in folio_line_tokens.items():
    for i, t in enumerate(line_toks):
        if i + 1 >= len(line_toks):
            continue
        m = morph.extract(t.word)
        mid = m.middle
        if not mid:
            continue

        succ = line_toks[i + 1]
        sm = morph.extract(succ.word)
        succ_pre = sm.prefix or 'BARE'
        succ_mid = sm.middle or '?'

        if mid in dp_set:
            dark_succ_prefix[mid][succ_pre] += 1
            dark_succ_middle[mid][succ_mid] += 1
            dark_succ_word[mid][succ.word] += 1
        elif mid in bridge_set:
            bridge_succ_prefix[mid][succ_pre] += 1

# ═══ SUCCESSOR ENTROPY COMPARISON ═══
def entropy(counter):
    total = sum(counter.values())
    if total <= 1:
        return 0.0
    h = 0.0
    for ct in counter.values():
        if ct > 0:
            p = ct / total
            h -= p * math.log2(p)
    return h

def concentration(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return max(counter.values()) / total

MIN_SUCCESSORS = 5

print("=" * 100)
print("DARK vs BRIDGE: SUCCESSOR PREFIX ENTROPY")
print("=" * 100)

dark_ent = []
dark_conc = []
for mid in dp_set:
    n = sum(dark_succ_prefix[mid].values())
    if n >= MIN_SUCCESSORS:
        dark_ent.append((mid, entropy(dark_succ_prefix[mid]), n))
        dark_conc.append((mid, concentration(dark_succ_prefix[mid]), n))

bridge_ent = []
bridge_conc_list = []
for mid in bridge_set:
    n = sum(bridge_succ_prefix[mid].values())
    if n >= MIN_SUCCESSORS:
        bridge_ent.append((mid, entropy(bridge_succ_prefix[mid]), n))
        bridge_conc_list.append((mid, concentration(bridge_succ_prefix[mid]), n))

dark_e_vals = [e for _, e, _ in dark_ent]
bridge_e_vals = [e for _, e, _ in bridge_ent]
dark_c_vals = [c for _, c, _ in dark_conc]
bridge_c_vals = [c for _, c, _ in bridge_conc_list]

print(f"\n  Dark MIDDLEs with {MIN_SUCCESSORS}+ successors: {len(dark_ent)}")
print(f"  Bridge MIDDLEs with {MIN_SUCCESSORS}+ successors: {len(bridge_ent)}")

if dark_e_vals and bridge_e_vals:
    print(f"\n  Successor PREFIX entropy:")
    print(f"    Dark:   mean={sum(dark_e_vals)/len(dark_e_vals):.3f}, median={sorted(dark_e_vals)[len(dark_e_vals)//2]:.3f}")
    print(f"    Bridge: mean={sum(bridge_e_vals)/len(bridge_e_vals):.3f}, median={sorted(bridge_e_vals)[len(bridge_e_vals)//2]:.3f}")

    print(f"\n  Successor PREFIX concentration (top-1):")
    print(f"    Dark:   mean={sum(dark_c_vals)/len(dark_c_vals):.3f}")
    print(f"    Bridge: mean={sum(bridge_c_vals)/len(bridge_c_vals):.3f}")

# ═══ TOP DARK MIDDLEs BY SUCCESSOR CONCENTRATION ═══
print("\n" + "=" * 100)
print("TOP 20 DARK MIDDLEs: WHAT FOLLOWS THEM?")
print("=" * 100)

dark_conc.sort(key=lambda x: -x[1])

print(f"\n  {'MIDDLE':>8s} {'N':>4s} {'Conc':>5s} {'Top successor PREFIX':>20s} {'2nd':>12s}  Atom reading")
print(f"  {'-'*80}")

for mid, c, n in dark_conc[:20]:
    top = dark_succ_prefix[mid].most_common(2)
    t1_pre, t1_ct = top[0]
    t1_pct = 100 * t1_ct / n
    t1_label = PREFIX_LABEL.get(t1_pre, t1_pre)
    t2_pre, t2_ct = top[1] if len(top) > 1 else ('', 0)
    t2_pct = 100 * t2_ct / n
    atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in mid)
    print(f"  {mid:>8s} {n:4d} {c:5.2f} {t1_pre:>8s}({t1_label:>10s}) {t1_pct:4.0f}%  {t2_pre:>5s} {t2_pct:3.0f}%  {atoms}")

# ═══ SUCCESSOR DISCRIMINATION: DO DIFFERENT DARK MIDDLEs ROUTE DIFFERENTLY? ═══
print("\n" + "=" * 100)
print("SUCCESSOR DISCRIMINATION: Do dark MIDDLEs route to DIFFERENT successors?")
print("=" * 100)

# Compute pairwise JSD between dark MIDDLE successor profiles
qualifying_dark = [(mid, dark_succ_prefix[mid]) for mid in dp_set
                   if sum(dark_succ_prefix[mid].values()) >= MIN_SUCCESSORS]

def jsd(c1, c2):
    """Jensen-Shannon divergence between two Counters."""
    all_keys = set(c1.keys()) | set(c2.keys())
    t1 = sum(c1.values())
    t2 = sum(c2.values())
    if t1 == 0 or t2 == 0:
        return 1.0
    h_avg = 0.0
    h1 = 0.0
    h2 = 0.0
    for k in all_keys:
        p1 = c1.get(k, 0) / t1
        p2 = c2.get(k, 0) / t2
        m = (p1 + p2) / 2
        if m > 0:
            h_avg -= m * math.log2(m)
        if p1 > 0:
            h1 -= p1 * math.log2(p1)
        if p2 > 0:
            h2 -= p2 * math.log2(p2)
    return h_avg - (h1 + h2) / 2

# Sample pairwise JSD
import random
random.seed(42)
if len(qualifying_dark) > 2:
    pairs = []
    for i in range(min(500, len(qualifying_dark) * (len(qualifying_dark)-1) // 2)):
        a, b = random.sample(range(len(qualifying_dark)), 2)
        mid_a, prof_a = qualifying_dark[a]
        mid_b, prof_b = qualifying_dark[b]
        pairs.append(jsd(prof_a, prof_b))

    mean_jsd = sum(pairs) / len(pairs)
    print(f"\n  Pairwise JSD between dark MIDDLE successor profiles:")
    print(f"    Mean JSD = {mean_jsd:.3f} (over {len(pairs)} pairs)")
    print(f"    If JSD > 0.2: dark MIDDLEs route to DIFFERENT successors")
    print(f"    If JSD < 0.1: dark MIDDLEs route to SIMILAR successors")

    if mean_jsd > 0.2:
        print(f"    >>> DARK MIDDLEs DISCRIMINATE — different dark tokens route differently")
    else:
        print(f"    >>> Dark MIDDLEs share similar successor profiles")

# ═══ f75r: WHAT FOLLOWS EACH DARK TOKEN? ═══
print("\n" + "=" * 100)
print("f75r: SUCCESSOR OF EACH DARK PIPELINE TOKEN")
print("=" * 100)

f75r = [t for t in all_b if t.folio == 'f75r']
f75r_lines = sorted(set(t.line for t in f75r), key=lambda x: int(x))

def get_phase(line):
    lnum = int(line)
    if lnum <= 5: return 'ASSESS'
    elif lnum <= 6: return 'HEAT'
    elif lnum <= 12: return 'DISTILL'
    elif lnum <= 16: return 'REPEAT'
    elif lnum <= 22: return 'FERMENT'
    elif lnum <= 26: return 'RESTART'
    elif lnum <= 27: return 'QUALITY'
    elif lnum <= 31: return 'RE-DISTILL'
    else: return 'MAIN-LOOP'

for li in f75r_lines:
    line_toks = [t for t in f75r if t.line == li]
    for i, t in enumerate(line_toks):
        m = morph.extract(t.word)
        if not (m.middle and m.middle in dp_set):
            continue
        if i + 1 >= len(line_toks):
            succ_word = '(LINE END)'
            succ_pre = ''
            succ_label = ''
        else:
            succ = line_toks[i + 1]
            succ_word = succ.word
            sm = morph.extract(succ.word)
            succ_pre = sm.prefix or 'BARE'
            succ_label = PREFIX_LABEL.get(succ_pre, succ_pre)

        phase = get_phase(t.line)

        # What does this dark MIDDLE USUALLY route to (corpus-wide)?
        usual_succ = dark_succ_prefix[m.middle].most_common(1)
        usual_pre = usual_succ[0][0] if usual_succ else '?'
        usual_label = PREFIX_LABEL.get(usual_pre, usual_pre)
        usual_pct = 100 * usual_succ[0][1] / sum(dark_succ_prefix[m.middle].values()) if usual_succ else 0

        match = "MATCH" if succ_pre == usual_pre else "DIFFERENT"

        print(f"  L{t.line:>2s} [{phase:10s}] {t.word:16s} -> {succ_word:16s} ({succ_label})")
        print(f"      Corpus usual: {usual_pre}({usual_label}) {usual_pct:.0f}% of time.  {match}")
        print()

# ═══ KEY QUESTION: SUCCESSOR CONCENTRATION vs OWN-PREFIX CONCENTRATION ═══
print("=" * 100)
print("COMPARISON: Dark MIDDLE own-PREFIX vs successor-PREFIX concentration")
print("Is the successor signal STRONGER than the self-PREFIX signal?")
print("=" * 100)

own_concs = []
succ_concs = []
for mid in dp_set:
    # Own PREFIX
    own_counter = Counter()
    for t in all_b:
        m = morph.extract(t.word)
        if m.middle == mid:
            own_counter[m.prefix or 'BARE'] += 1
    own_n = sum(own_counter.values())

    # Successor PREFIX
    succ_n = sum(dark_succ_prefix[mid].values())

    if own_n >= MIN_SUCCESSORS and succ_n >= MIN_SUCCESSORS:
        own_concs.append(concentration(own_counter))
        succ_concs.append(concentration(dark_succ_prefix[mid]))

if own_concs and succ_concs:
    print(f"\n  Dark MIDDLEs with {MIN_SUCCESSORS}+ tokens AND successors: {len(own_concs)}")
    print(f"  Own-PREFIX concentration:      mean={sum(own_concs)/len(own_concs):.3f}")
    print(f"  Successor-PREFIX concentration: mean={sum(succ_concs)/len(succ_concs):.3f}")

    # Are they correlated?
    n = len(own_concs)
    mean_o = sum(own_concs) / n
    mean_s = sum(succ_concs) / n
    cov = sum((own_concs[i] - mean_o) * (succ_concs[i] - mean_s) for i in range(n)) / n
    std_o = (sum((x - mean_o)**2 for x in own_concs) / n) ** 0.5
    std_s = (sum((x - mean_s)**2 for x in succ_concs) / n) ** 0.5
    r = cov / (std_o * std_s) if std_o > 0 and std_s > 0 else 0
    print(f"  Correlation (own vs successor concentration): r={r:.3f}")

    if sum(succ_concs)/len(succ_concs) > sum(own_concs)/len(own_concs):
        print(f"\n  >>> SUCCESSOR concentration is HIGHER than own-PREFIX concentration")
        print(f"  >>> Dark MIDDLEs are more deterministic about what FOLLOWS than about their OWN prefix")
    else:
        print(f"\n  >>> Own-PREFIX concentration is higher — dark tokens are self-determined, not routing")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
