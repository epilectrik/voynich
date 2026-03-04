"""Quick check: Does l appear in CHSH-lane MIDDLEs? And in QO-lane MIDDLEs?
What are the actual token combinations?"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Collect: prefix -> middle combinations for l-terminal compounds
# Track ch/sh (CHSH lane) vs qo (QO lane) vs other prefixes
l_term_by_prefix = defaultdict(Counter)  # prefix -> {middle: count}
all_by_prefix = defaultdict(Counter)

chsh_prefixes = {'ch', 'sh'}
qo_prefixes = {'qo'}

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle or len(m.middle) < 2:
        continue

    pfx = m.prefix or 'NONE'
    mid = m.middle
    terminal = mid[-1]

    all_by_prefix[pfx][mid] += 1

    if terminal == 'l':
        l_term_by_prefix[pfx][mid] += 1

# ============================================================
# Summary: l-terminal by prefix lane
# ============================================================
print(f"{'='*70}")
print("l-TERMINAL MIDDLES BY PREFIX (LANE)")
print(f"{'='*70}\n")

# Group by lane
chsh_l = Counter()
qo_l = Counter()
other_l = Counter()
none_l = Counter()

for pfx, mids in l_term_by_prefix.items():
    for mid, count in mids.items():
        if pfx in chsh_prefixes:
            chsh_l[f"{pfx}+{mid}"] += count
        elif pfx in qo_prefixes:
            qo_l[f"{pfx}+{mid}"] += count
        elif pfx == 'NONE':
            none_l[mid] += count
        else:
            other_l[f"{pfx}+{mid}"] += count

print(f"CHSH lane (ch/sh prefix) with l-terminal MIDDLE:")
print(f"  Total: {sum(chsh_l.values())}")
for combo, count in chsh_l.most_common(20):
    print(f"    {combo}: {count}")

print(f"\nQO lane (qo prefix) with l-terminal MIDDLE:")
print(f"  Total: {sum(qo_l.values())}")
for combo, count in qo_l.most_common(20):
    print(f"    {combo}: {count}")

print(f"\nNo prefix with l-terminal MIDDLE:")
print(f"  Total: {sum(none_l.values())}")
for mid, count in none_l.most_common(20):
    print(f"    {mid}: {count}")

print(f"\nOther prefixes with l-terminal MIDDLE:")
print(f"  Total: {sum(other_l.values())}")
for combo, count in other_l.most_common(20):
    print(f"    {combo}: {count}")

# ============================================================
# Full token examples: ch/sh + l-terminal
# ============================================================
print(f"\n{'='*70}")
print("ACTUAL TOKENS: ch/sh PREFIX + l-TERMINAL MIDDLE")
print(f"{'='*70}\n")

chsh_l_tokens = Counter()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle or len(m.middle) < 2:
        continue
    if m.prefix in chsh_prefixes and m.middle[-1] == 'l':
        full = f"{m.prefix}+{m.middle}+{m.suffix or 'BARE'}"
        chsh_l_tokens[full] += 1

print(f"  {'Token breakdown':<30s} {'count':>8s}")
print(f"  {'-'*30} {'-'*8}")
for tok, count in chsh_l_tokens.most_common(30):
    print(f"  {tok:<30s} {count:>8d}")

# ============================================================
# Comparison: what MIDDLEs does CHSH lane normally use?
# ============================================================
print(f"\n{'='*70}")
print("CHSH LANE: TOP MIDDLES (all, not just l-terminal)")
print(f"{'='*70}\n")

chsh_all = Counter()
for pfx in chsh_prefixes:
    for mid, count in all_by_prefix[pfx].items():
        chsh_all[mid] += count

total_chsh = sum(chsh_all.values())
print(f"Total CHSH-lane compound tokens: {total_chsh}\n")
print(f"  {'MIDDLE':<14s} {'count':>8s} {'%':>8s} {'l-term?':>8s}")
print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*8}")
for mid, count in chsh_all.most_common(25):
    pct = count / total_chsh * 100
    is_l = 'YES' if mid[-1] == 'l' else ''
    print(f"  {mid:<14s} {count:>8d} {pct:>7.1f}% {is_l:>8s}")

# l-terminal fraction of CHSH
chsh_l_total = sum(c for m, c in chsh_all.items() if len(m) >= 2 and m[-1] == 'l')
print(f"\n  l-terminal fraction of CHSH: {chsh_l_total}/{total_chsh} = {chsh_l_total/total_chsh*100:.1f}%")

# Same for QO
qo_all = Counter()
for mid, count in all_by_prefix['qo'].items():
    qo_all[mid] += count
total_qo = sum(qo_all.values())
qo_l_total = sum(c for m, c in qo_all.items() if len(m) >= 2 and m[-1] == 'l')
print(f"  l-terminal fraction of QO:   {qo_l_total}/{total_qo} = {qo_l_total/total_qo*100:.1f}%")

# No prefix
none_all = Counter()
for mid, count in all_by_prefix['NONE'].items():
    none_all[mid] += count
total_none = sum(none_all.values())
none_l_total = sum(c for m, c in none_all.items() if len(m) >= 2 and m[-1] == 'l')
print(f"  l-terminal fraction of BARE: {none_l_total}/{total_none} = {none_l_total/total_none*100:.1f}%")

# ============================================================
# Reading: what does "ch + el" mean in our interpretation?
# ============================================================
print(f"\n{'='*70}")
print("INTERPRETATION: ch/sh + l-terminal compound readings")
print(f"{'='*70}")
print("""
If ch = "active test/checkpoint" and sh = "passive monitor"
And l-terminal converts operation to state reading:

  ch + ol  = "checkpoint the vessel-state"  (test what's in the vessel)
  ch + eol = "checkpoint the cooling-state"  (test thermal stability)
  sh + ol  = "monitor the vessel-state"     (watch vessel conditions)
  sh + eol = "monitor the cooling-state"    (watch thermal stability)
  ch + al  = "checkpoint the flow-state"    (test what's flowing)

These read as: "check/monitor [the condition of X]"
The prefix says HOW (test vs watch), the l-terminal says WHAT (state of X).
""")
